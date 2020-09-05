======================
GetIn Documentation
======================

Introduction
============
GetIn Server that provides data to the dashboard and mobile app

Tools
============
#. Django
#. Django Rest Framework
#. Python3
#. Swagger



Resources
============

* Deployment

https://medium.com/techkylabs/django-deployment-on-linux-ubuntu-16-04-with-postgresql-nginx-ssl-e6504a02f224
https://www.humankode.com/ssl/how-to-set-up-free-ssl-certificates-from-lets-encrypt-using-docker-and-nginx

* ODK certificate 

https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04


Links
============

* Django admin - http://backend.getinmobile.org/admin/
* Swagger - http://backend.getinmobile.org


Server Deployment
===================

Setup EC2 instance
-------------------

#. Log into the GetIn AWS account
#. Go to Services > compute > EC2.
#. Click on Launch Instance.
#. Select Ubuntu Server 18.04 TLS(or higher)
#. Click Review and Launch > Launch .
#. Use existing pair(please check the documentation folder for the pem file GetInWebServer.pem
#. Finally Click on Launch Instances.



SSH  into the Server, Install dependencies & setup postgreSql
----------------------------------------------------------------
#. cd Desktop/
#. sudo chmod 400 GetInWebServer.pem
#. ssh -i GetInWebServer.pem ubuntu@public_ip_address
#. sudo apt-get update && apt-get upgrade -y
#. sudo apt-get install python-pip python-dev libpq-dev postgresql postgresql-contrib nginx git
#. sudo apt-get install python3-venv
#. source venv/bin/activate(or install without env)
#. pip install django
#. pip install -r requirements.txt
#. git clone https://github.com/UNFPAInnovation/GetInServerRebuild.git

.. note:: All servers in the GetIn Project use the GetInWebServer.pem.

.. warning:: Activate allowed hosts in /home/ubuntu/GetInServerRebuild/GetInBackendRebuild/settings.py ALLOWED_HOSTS = ['*']
    Requests may not work if not activated or add the actual IP address of the server


Add static files and collect static
-------------------------------------
`Add these lines to the /home/ubuntu/GetInServerRebuild/GetInBackendRebuild/settings.py`

.. code-block:: python

    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'static/')

Then collect static files

.. code-block:: console

    source venv/bin/activate
    (venv)$ python manage.py collectstatic

**Explanation:** This allows the static files like css and images to get rendered in django admin dashboard and swagger




Setup gunicorn to run the django server
----------------------------------------

Create gunicorn file

.. code-block:: console

    (venv)$ deactivate
    $sudo vim /etc/systemd/system/gunicorn.service


Insert the following commands

.. code-block:: python

    [Unit]
    Description=gunicorn
    daemon After=network.target
    [Service]
    User=ubuntu
    Group=www-data
    WorkingDirectory=/home/ubuntu/GetInServerRebuild
    ExecStart=/home/ubuntu/GetInServerRebuild/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/sample_project/sample_project.sock sample_project.wsgi:application
    [Install]
    WantedBy=multi-user.target

**Explanation:**
Start with the [Unit] section, which is used to specify metadata and dependencies. We'll put a description of our service here and tell the init system to only start this after the networking target has been reached
[Unit]
Description=gunicorn
daemon After=network.target
Next, we’ll open up the [Service] section. We'll specify the user and group that we want to process to run under. We will give ubuntu as our user ownership of the process. We'll then give group ownership to the www-data group so that Nginx can communicate easily with Gunicorn.
We’ll then map out the working directory and specify the command to use to start the service. In this case, we’ll have to specify the full path to the Gunicorn executable, which is installed within our virtual environment. We will bind it to a Unix socket within the project directory since Nginx is installed on the same machine. We can also specify any optional Gunicorn tweaks here. For example, we specified 3 worker processes in this case
[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/home/ubuntu/GetInServerRebuild
ExecStart=/home/ubuntu/GetInServerRebuild/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/home/ubuntu/GetInServerRebuild/GetInBackendRebuild.sock GetInBackendRebuild.wsgi:application


Finally, we’ll add an [Install] section. This will tell systemd what to link this service to if we enable it to start at boot. We want this service to start when the regular multi-user system is up and running.

.. code-block:: console

    sudo systemctl start gunicorn
    sudo systemctl enable gunicorn


Configure Nginx to Proxy Pass to Gunicorn
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Create file named GetInServerRebuild
sudo vim /etc/nginx/sites-available/GetInServerRebuild

Insert the following commands

.. code-block:: python

    server {
        listen 80;
        server_name 34.221.109.93 backend.getinmobile.org;
    location = /favicon.ico { access_log off; log_not_found off; }

        location /static/ {
            root /home/ubuntu/GetInServerRebuild;
        }
        return 301 https://backend.getinmobile.org$request_uri;
    }

    server {
       listen 443 ssl;
       listen [::]:443 ssl;
       server_name backend.getinmobile.org;
    ssl on;
        ssl_certificate /etc/letsencrypt/live/backend.getinmobile.org/fullchain.pem; # managed by Certbot
        ssl_certificate_key /etc/letsencrypt/live/backend.getinmobile.org/privkey.pem; # managed by Certbot
    location /static/ {
            root /home/ubuntu/GetInServerRebuild;
       }
    location / {
         include proxy_params;
         proxy_pass http://unix:/home/ubuntu/GetInServerRebuild/GetInBackendRebuild.sock;
       }
    }

Enable the file by linking it to the sites-enabled directory

.. code-block:: console

    sudo ln -s /etc/nginx/sites-available/sample_project /etc/nginx/sites-enabled

Generate ssl certificate
~~~~~~~~~~~~~~~~~~~~~~~~~

Create directories and request for certificate from lets encrypt

.. code-block:: console

    sudo mkdir /etc/nginx/ssl
    sudo openssl req -x509 -nodes -days 365 -newkey rsa:2048 -keyout /etc/nginx/ssl/nginx.key -out /etc/nginx/ssl/nginx.crt



**Activate the certificate and start nginx**

.. code-block:: console

    sudo service nginx restart
    sudo apt-get update
    sudo apt-get install software-properties-common
    sudo add-apt-repository ppa:certbot/certbot
    sudo apt-get update
    sudo apt-get install python-certbot-nginx
    sudo certbot --nginx
    IF IT FAILS RUN sudo apt install --only-upgrade certbot
    sudo nginx -t
    sudo service nginx restart


Update of code and server
--------------------------

Incase the code has changed in the repository

.. code-block:: console

    git add .
    git stash save
    git pull
    sudo systemctl restart gunicorn
    sudo service nginx restart


ODK Central
============

Generate ssl certificate
-------------------------

Stop docker images

.. code-block:: console

    cd central
    docker-compose stop nginx


Update the certificates


.. code-block:: console

    sudo systemctl start nginx
    sudo certbot --nginx -d odkcentral.getinmobile.org
    sudo cp /etc/letsencrypt/live/odkcentral.getinmobile.org/fullchain.pem /home/ubuntu/central/files/local/customssl/fullchain.pem
    sudo cp /etc/letsencrypt/live/odkcentral.getinmobile.org/privkey.pem /home/ubuntu/central/files/local/customssl/privkey.pem
    cd central
    sudo systemctl stop nginx
    docker-compose build nginx
    docker-compose up -d
    OR Run the `update_certificate.sh` file


.. note:: You may need to kill nginx manually. The system may also run out of space.


.. code-block:: console

    ps -ef |grep nginx
    kill -9 pid


.. warning:: The system may run out of space. FIRST MAKE SURE THE IMAGES ARE RUNNING using docker ps. Then run `sudo docker system prune`


Adding org units
==================

https://infoinspired.com/google-docs/spreadsheet/filter-unique-values-using-the-filter-menu/
- Clean up data
- Rearrage columns if needed
- Use this formula in google sheets to filter unique parishes, subcounties and counties. 
=COUNTIF(D2:D,D2:D)=1
- insert the values into the odk sheet(xlsx)
- upload the file to https://getodk.org/xlsform/
- download the xml file
- upload the xml file to https://testcentral.getinmobile.org/
