from pyfcm import FCMNotification

from app.utils.constants import FIREBASE_TOKEN

push_service = FCMNotification(api_key=FIREBASE_TOKEN)


def send_firebase_notification(firebase_device_ids, message_title, message_body):
    result = push_service.notify_multiple_devices(registration_ids=firebase_device_ids, message_title=message_title,
                                                  message_body=message_body)
    print(result)
