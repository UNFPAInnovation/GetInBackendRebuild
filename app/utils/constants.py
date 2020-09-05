# user's gender
from os import environ

GENDER_MALE = "male"
GENDER_FEMALE = "female"

PRIMARY_LEVEL = "Primary level"
O_LEVEL = "O level"
A_LEVEL = "A level"
TERTIARY_LEVEL = "Tertiary"


SINGLE = "Single"
MARRIED = "Married"
DIVORCED = "Divorced"


HOME = "Home"
HEALTH_FACILITY = "Health facility"

USER_TYPE_DEVELOPER = "developer"
USER_TYPE_DHO = "dho"
# Also known as VHT
USER_TYPE_CHEW = "chew"
USER_TYPE_MIDWIFE = "midwife"
USER_TYPE_AMBULANCE = "ambulance"
USER_TYPE_MANAGER = "manager"

MISSED = "Missed"
ATTENDED = "Attended"
EXPECTED = "Expected"


PRE = "Pre"
POST = "Post"


BEFORE = "Before"
AFTER = "After"
CURRENT = "Current"

ANC1 = "AN1"
ANC2 = "AN2"
ANC3 = "AN3"
ANC4 = "AN4"
DELIVERY = "Delivery"
FAMILY_PLANNING = "Family Planning"
#####################################
# NOTE: The form ids must be the same in odk central, android app, xslm forms and django backend
# When you change a form and generate the xml, odk central will require you to upload one with a different id
# from those that are already there
#####################################
APPOINTMENT_FORM_CHEW_NAME = "GetINAppointment6_chew"
APPOINTMENT_FORM_MIDWIFE_NAME = "GetINAppointment10_midwife"
# each district has its own form.
MAP_GIRL_BUNDIBUGYO_CHEW_FORM_NAME = "GetInMapGirlBundibugyo17_chew"
MAP_GIRL_BUNDIBUGYO_MIDWIFE_FORM_NAME = "GetInMapGirlBundibugyo16_midwife"
MAP_GIRL_ARUA_CHEW_FORM_NAME = "GetInMapGirlArua3_chew"
MAP_GIRL_ARUA_MIDWIFE_FORM_NAME = "GetInMapGirlArua3_midwife"
MAP_GIRL_KAMPALA_CHEW_FORM_NAME = "GetInMapGirlKampala1_chew"
MAP_GIRL_KAMPALA_MIDWIFE_FORM_NAME = "GetInMapGirlKampala1_midwife"
FOLLOW_UP_FORM_CHEW_NAME = "GetInFollowup20_chew"
FOLLOW_UP_FORM_MIDWIFE_NAME = "GetInFollowup19_midwife"
POSTNATAL_FORM_CHEW_NAME = "GetINPostnatalForm6_chew"
POSTNATAL_FORM_MIDWIFE_NAME = "GetINPostnatalForm6_midwife"
# NOTE: Some times the json object starts with data object param
DEFAULT_TAG = "data"
MSI_BASE_URL = environ.get('MSI_BASE_URL', 'http://35.203.191.127/')

FIREBASE_TOKEN = "AAAAI8T7WsI:APA91bEfmZYjDWdaiI24hqCP3LGzg0s9c-hviHs4gC4RV_qW3J2xlshhK5coizTf4FmQaMOY10fkjyd49howXFkGPpB3VSLq_MXdnsgKKDzBTWh6ZSc69Gis6FnZEJsf8Yl7gBeqtG4d"

africa_env = environ.get('AFRICAS_TALKING_ENV', 'test')
if africa_env == 'production':
    username = "getinapp"
    api_key = "9e8c2ca8d8a1897248036f1a9bf25fb1f9ba5898635044a96558e1323fd1c16b"
else:
    username = "sandbox"
    api_key = "969fb96582f9639b086879f64a8d4b7411af1523c0b0ee1f16a0eac6f4882a22"