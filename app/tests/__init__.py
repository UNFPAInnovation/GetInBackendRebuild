# Add these environment variables
# PYTHONUNBUFFERED=1;DJANGO_SETTINGS_MODULE=GetInBackendRebuild.settings;PASSWORD=Doppler25;DJANGO_DATABASE=unittest;AFRICAS_TALKING_ENV=test
from app.tests.usertests import *
from app.tests.midwifemappingtest import *
from app.tests.chewmappingtest import *
from app.tests.chewfollowuptest import *
from app.tests.midwifefollowuptest import *
from app.tests.deliverytest import *