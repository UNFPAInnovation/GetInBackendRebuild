# user's gender
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
FOLLOW_UP_FORM_CHEW_NAME = "GetInFollowup20_chew"
FOLLOW_UP_FORM_MIDWIFE_NAME = "GetInFollowup19_midwife"
POSTNATAL_FORM_CHEW_NAME = "GetINPostnatalForm6_chew"
POSTNATAL_FORM_MIDWIFE_NAME = "GetINPostnatalForm6_midwife"

FIREBASE_TOKEN = "AAAAI8T7WsI:APA91bEfmZYjDWdaiI24hqCP3LGzg0s9c-hviHs4gC4RV_qW3J2xlshhK5coizTf4FmQaMOY10fkjyd49howXFkGPpB3VSLq_MXdnsgKKDzBTWh6ZSc69Gis6FnZEJsf8Yl7gBeqtG4d"