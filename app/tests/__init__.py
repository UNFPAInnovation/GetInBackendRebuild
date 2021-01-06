# Add these environment variables
# PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=GetInBackendRebuild.settings;PASSWORD=Doppler25;DJANGO_DATABASE=unittest;AFRICAS_TALKING_ENV=test
# for test coverage run this after running the tests
# coverage run --source='.' manage.py test && coverage report --omit 'venv/*','app/migrations/*','app/tests/*','GetInBackendRebuild/wsgi.py','app/__init__.py','app/utils/__init__.py'

# from app.tests.usertests import *
# from app.tests.midwifemappingtest import *
# from app.tests.chewmappingtest import *
# from app.tests.chewfollowuptest import *
# from app.tests.midwifefollowuptest import *
# from app.tests.deliverytest import *
# from app.tests.modeltests import *
# from app.tests.msitest import *
# from app.tests.locationtest import *
# from app.tests.midwifeappointmenttest import *
# from app.tests.serializertests import *
# from app.tests.dashboard_statstests import *
# from app.tests.viewtests import *
from app.tests.smstests import *
