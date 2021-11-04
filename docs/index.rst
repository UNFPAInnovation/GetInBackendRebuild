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

https://simpleisbetterthancomplex.com/tutorial/2016/10/14/how-to-deploy-to-digital-ocean.html

* ODK certificate 

https://www.digitalocean.com/community/tutorials/how-to-secure-nginx-with-let-s-encrypt-on-ubuntu-18-04

* ODK central
https://docs.getodk.org/central-install-digital-ocean/


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


Setup Compute Engine instance
-------------------------------

#. Log into the GetIn GCP account
#. Go to Services > Compute engine.
#. Click create instance Launch Instance.
#. Install gcloud on local machine(optional) or gshell
#. Login into gcloud acount
#. Open ports 80 and 443(Note you can do this in the console)

.. code-block:: console

    gcloud compute firewall-rules create allow-443 --allow tcp:443
    gcloud compute firewall-rules create allow-80 --allow tcp:80
#. SSH into machine. Enter paraphrase(make sure you remember it)
#. Switch active user. ``su - <username>``
#. Change user password. ``sudo passwd <username>``

#. Finally Click on save.


SSH  into the Server, Install dependencies & setup postgreSql
----------------------------------------------------------------
#. cd Desktop/
#. sudo chmod 400 GetInWebServer.pem
#. ssh -i GetInWebServer.pem ubuntu@public_ip_address 
#. OR (GCP password is the one ssh key phrase you entered earlier) ``gcloud compute ssh <instance-id>`` if this fails then use ``gcloud beta compute ssh --zone "europe-west3-c" "test-backend-django" --project "getin-293809"``
#. Set user password ``sudo passwd <username>``
#. sudo apt-get update && sudo apt-get upgrade -y (this may require root ``sudo bash``)
#. sudo apt-get install libpq-dev postgresql postgresql-contrib nginx git
#. sudo apt-get install python3-venv
#. create `log` folder for logs files in location `/home/username/logs`
#. source venv/bin/activate(or install without env)
#. git clone https://github.com/UNFPAInnovation/GetInServerRebuild.git
#. pip install -r requirements.txt


Setup environment variables
----------------------------
#. Move into the ~/GetInBackendRebuild/GetInBackendRebuild folder ``cd GetInBackendRebuild/GetInBackendRebuild``
#. cat `.env.example` to see the variables required
#. Acquire variables from the person incharge of project
#. Create a file name `.env` and add those variables


Create postgres db credentials
-------------------------------
#. Login into db. ``sudo -u postgres psql``
#. Change password. ``ALTER USER postgres PASSWORD 'mysecretpassword';``
 

.. note:: All servers in the GetIn Project use the GetInWebServer.pem.

.. warning:: Activate allowed hosts in /home/ubuntu/GetInServerRebuild/GetInBackendRebuild/settings.py ALLOWED_HOSTS = ['*']
    Requests may not work if not activated or add the actual IP address of the server


Add static files and collect static
-------------------------------------
``Add these lines to the /home/ubuntu/GetInServerRebuild/GetInBackendRebuild/settings.py``

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

Create file rename GetInBackendRebuild in sites-available
``sudo vim /etc/nginx/sites-available/GetInBackendRebuild``

Insert the following commands

.. code-block:: python

    upstream app_server {
        server unix:/home/codephillip/GetInBackendRebuild/GetInBackendRebuild.sock fail_timeout=0;
    }

    server {
        listen 80;

        # add here the ip address of your server
        # or a domain pointing to that ip (like example.com or www.example.com)
        server_name 34.221.109.93 testbackend.getinmobile.org;

        keepalive_timeout 5;
        client_max_body_size 4G;

        # MAKE SURE YOU CREATE A FOLDER CALLED logs in the user root directory
        access_log /home/codephillip/logs/nginx-access.log;
        error_log /home/codephillip/logs/nginx-error.log;

        # collect static using command ./manage.py collectstatic
        location /static/ {
            alias /home/codephillip/GetInBackendRebuild/static/;
        }

        # checks for static file, if not found proxy to app
        location / {
            try_files $uri @proxy_to_app;
        }

        location @proxy_to_app {
          proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
          proxy_set_header Host $http_host;
          proxy_redirect off;
          proxy_pass http://app_server;
        }
    }



Enable the file by linking it to the sites-enabled directory

.. code-block:: console

    sudo ln -s /etc/nginx/sites-available/GetInBackendRebuild /etc/nginx/sites-enabled

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
    sudo apt  install certbot
    sudo apt-get install python3-certbot-nginx
    sudo certbot --nginx -d testbackend.getinmobile.org
    IF IT FAILS RUN sudo apt install --only-upgrade certbot
    sudo nginx -t
    sudo service nginx restart


Adding monthly stats email recipients
--------------------------------------

- Open the .env file
- Add emails without quotes or spaces
- Finally update the cron job. ``python manage.py crontab add``


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
    OR Run the ``update_certificate.sh`` file


.. note:: You may need to kill nginx manually. The system may also run out of space.


.. code-block:: console

    ps -ef |grep nginx
    kill -9 pid


.. warning:: The system may run out of space. FIRST MAKE SURE THE IMAGES ARE RUNNING using docker ps. Then run ``sudo docker system prune``


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



Database backup
===================

#. Log into postgres on server from local machine to view database name. Then log out(optional) 
#. Export database into `.sql` file ``pg_dump -h <host> -p 5432 -U postgres -f <exampledump.sql> <dbname>``
#. Go to new server and create database. ``sudo -u postgres psql postgres`` then ``CREATE DATABASE <dbname>;``
#. Logout of postgres. Import database into new sql db ``sudo -u postgres psql <dbname> < <exampledump.sql>``
#. Connect to the database in the app.


ODK central setup
======================

Installation guide
-------------------
Use the installation guide on odk central website
https://docs.getodk.org/central-install-digital-ocean/

Install docker(supplement to odk installation guide)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#. Install docker using. ``sudo apt install docker.io`` then ``sudo apt install docker-compose``
#. Create the docker group. ``$ sudo groupadd docker``
#. Add your user to the docker group. ``$ sudo usermod -aG docker $USER``
#. Log out and log back in so that your group membership is re-evaluated.

ODK database backup
--------------------

Export old db
~~~~~~~~~~~~~~~
#. Export odk central db ``docker exec central_postgres_1 pg_dump odk -U odk -f <filename>.sql``
#. Extract the sql file from docker container `central_postgres_1` to the vm ``docker cp central_postgres_1:/<filename>.sql <filename>.sql``
#. Export sql file to local machine from EC2 instance(Google compute will require Google storage). Use your local machine for this operation ``scp -i "GetInWebServer.pem" ubuntu@18.237.225.123:/home/ubuntu/'<filename>.sql' /home/codephillip/Downloads/'<filename>.sql'``

Import new db
~~~~~~~~~~~~~~~
#. Import sql file into GCE instance ``gcloud compute scp <local-file-path> <instance-name>`` or Use the gcloud browser shell
#. Delete all tables in database(MAKE SURE THIS IS A MIGRATION FROM ONE SERVER TO ANOTHER).

.. code-block:: console

    docker exec -it central_postgres_1 /bin/bash
    psql -U odk
    \c odk
    DROP SCHEMA public CASCADE;
    CREATE SCHEMA public;
    CTRL + d

#. Copy sql file into docker image ``docker cp '<filename>.sql' central_postgres_1:/'<filename>.sql'``
#. Update odk database. ``docker exec central_postgres_1 psql -d odk -U odk -f <filename>.sql``

ODK Form update
================

Updating ODK forms
-------------------
#. SSH into server ``gcloud beta compute ssh --zone "europe-west3-a" "production-odk-central" --project "getin-293809"``
#. Access postgres db in docker ``docker exec -it central_postgres_1 psql -U odk``
#. Delete form in sql by formId ``delete from forms where "xmlFormId" = 'GetINFoobar';``
#. Visit odk central _dashboard
#. Upload updated form

.. _dashboard: https://odkcentral.getinmobile.org/#/projects/2


GetIN django backend
=======================

Local dev environment setup
-----------------------------

remember to also create a virtualenv




#. Clone the project ``git clone https://github.com/UNFPAInnovation/GetInBackendRebuild.git``
#. Create .env file inside the project folder GetInBackendRebuild. Hint; Use the `.env.example` file as a reference
using python3 -m venv venv
then source venv/bin/activate
then pip install -r requirements.txt
then python3 ./manage.py runserver