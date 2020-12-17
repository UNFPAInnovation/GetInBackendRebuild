import africastalking
from rest_framework.response import Response

from app.models import SmsModel, User, SentSmsLog
from app.serializers import SmsModelSerializer
from app.utils.constants import username, api_key, HEALTH_MESSAGES
from django.utils import timezone
africastalking.initialize(username, api_key)
sms = africastalking.SMS
print(username)
print(api_key)


def send_hw_sms(message, sender, receiver_ids):
    server_response = []
    phone_numbers = ["+256" + User.objects.get(id=receiver_id).phone[1:] for receiver_id in receiver_ids]
    response = sms.send(message, phone_numbers)
    sms_logger(str(response), message)
    recipients_results = response['SMSMessageData']['Recipients']

    for recipient in recipients_results:
        try:
            sms_model = SmsModel(recipient=User.objects.get(phone__contains=recipient['number'][5:]),
                                 sender_id=sender.id,
                                 message=message, status=recipient['status'],
                                 message_id=recipient['messageId'])
            sms_model.save()
            server_response.append(SmsModelSerializer(sms_model).data)
        except Exception as e:
            print(e)
    server_response = "success"
    return server_response


def send_sms_message(message, phone_numbers):
    """
    No user should get the same message twice in the same day
    """
    valid_phone_numbers = []
    response = ""
    for phone_number in phone_numbers:
        sms_log = SentSmsLog.objects.filter(phone_number=phone_number, message_type=HEALTH_MESSAGES)
        if sms_log.exists():
            if sms_log.first().created_at < timezone.now() - timezone.timedelta(hours=20):
                valid_phone_numbers.append(phone_number)
                SentSmsLog.objects.create(phone_number=phone_number, message=message)
        else:
            valid_phone_numbers.append(phone_number)
            SentSmsLog.objects.create(phone_number=phone_number, message=message)

    if valid_phone_numbers:
        response = sms.send(message, valid_phone_numbers)
        sms_logger(str(response), message)
    return response


def sms_logger(logs, message):
    try:
        webhooklog = open('sms_sender_log.txt', 'a')
        webhooklog.write("\n\n" + str(timezone.now()) + "\n" + logs + " message:" + message)
        webhooklog.close()
    except Exception as e:
        print(e)
