from GetInBackendRebuild.settings import env
import os

MSI_DISTRICTS = ['yumbe', 'moyo', 'adjumani']

GENDER_MALE = "male"
GENDER_FEMALE = "female"

PRIMARY_LEVEL = "Primary level"
O_LEVEL = "O level"
A_LEVEL = "A level"
TERTIARY_LEVEL = "Tertiary"
NONE = "None"

SINGLE = "Single"
MARRIED = "Married"
DIVORCED = "Divorced"
WIDOWED = "Widowed"

HOME = "Home"
HEALTH_FACILITY = "Health facility"

USER_TYPE_DEVELOPER = "developer"
USER_TYPE_DHO = "dho"
# Also known as VHT
USER_TYPE_CHEW = "chew"
USER_TYPE_ADMIN = "admin"
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

HEALTH_MESSAGES = "HEALTH_MESSAGES"
APPOINTMENT_REMINDER_MESSAGES = "APPOINTMENT_REMINDER_MESSAGES"
APP_USAGE_REMINDER_MESSAGES = "APP_USAGE_REMINDER_MESSAGES"
GENERAL_MESSAGE = "GENERAL_MESSAGE"
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
MAP_GIRL_MOYO_CHEW_FORM_NAME = "GetInMapGirlMoyo1_chew"
MAP_GIRL_MOYO_MIDWIFE_FORM_NAME = "GetInMapGirlMoyo1_midwife"
MAP_GIRL_ADJUMANI_CHEW_FORM_NAME = "GetInMapGirlAdjumani1_chew"
MAP_GIRL_ADJUMANI_MIDWIFE_FORM_NAME = "GetInMapGirlAdjumani1_midwife"
MAP_GIRL_YUMBE_CHEW_FORM_NAME = "GetInMapGirlYumbe1_chew"
MAP_GIRL_YUMBE_MIDWIFE_FORM_NAME = "GetInMapGirlYumbe1_midwife"
FOLLOW_UP_FORM_CHEW_NAME = "GetInFollowup20_chew"
FOLLOW_UP_FORM_MIDWIFE_NAME = "GetInFollowup19_midwife"
POSTNATAL_FORM_CHEW_NAME = "GetINPostnatalForm6_chew"
POSTNATAL_FORM_MIDWIFE_NAME = "GetINPostnatalForm6_midwife"
# NOTE: Some times the json object starts with data object param
DEFAULT_TAG = "data"
FORM_MAP_TEMPLATE = "forms.put(\"{0}\", \"GetInMapGirl{1}1_chew\");"

MAPPING_FORMS = [MAP_GIRL_BUNDIBUGYO_CHEW_FORM_NAME, MAP_GIRL_BUNDIBUGYO_MIDWIFE_FORM_NAME,
                 MAP_GIRL_ARUA_CHEW_FORM_NAME, MAP_GIRL_ARUA_MIDWIFE_FORM_NAME, MAP_GIRL_KAMPALA_CHEW_FORM_NAME,
                 MAP_GIRL_KAMPALA_MIDWIFE_FORM_NAME, MAP_GIRL_MOYO_CHEW_FORM_NAME, MAP_GIRL_MOYO_MIDWIFE_FORM_NAME,
                 MAP_GIRL_ADJUMANI_CHEW_FORM_NAME, MAP_GIRL_ADJUMANI_MIDWIFE_FORM_NAME, MAP_GIRL_YUMBE_CHEW_FORM_NAME,
                 MAP_GIRL_YUMBE_MIDWIFE_FORM_NAME]

MSI_BASE_URL = env('MSI_BASE_URL')
MSI_TOKEN = env('MSI_TOKEN')

FIREBASE_TOKEN = env('FIREBASE_TOKEN')
username = env('AFRICAS_TALKING_USERNAME')
api_key = env('AFRICAS_TALKING_PASSWORD')
