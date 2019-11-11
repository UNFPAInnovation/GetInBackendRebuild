import africastalking
from rest_framework.response import Response

from app.models import SmsModel, User
from app.serializers import SmsModelSerializer

username = "getinapp"
api_key = "9e8c2ca8d8a1897248036f1a9bf25fb1f9ba5898635044a96558e1323fd1c16b"
africastalking.initialize(username, api_key)
sms = africastalking.SMS


def send_sms(message, sender, receiver_ids):
    server_response = []
    phone_numbers = ["+256" + User.objects.get(id=receiver_id).phone[1:] for receiver_id in receiver_ids]
    response = sms.send(message, phone_numbers)
    print(response)

    recipients_results = response['SMSMessageData']['Recipients']

    for recipient in recipients_results:
        try:
            sms_model = SmsModel(recipient=User.objects.get(phone__contains=recipient['number'][5:]), sender_id=sender.id,
                                 message=message, status=recipient['status'],
                                 message_id=recipient['messageId'])
            sms_model.save()
            server_response.append(SmsModelSerializer(sms_model).data)
        except Exception as e:
            print(e)
    return Response({'result': server_response})
