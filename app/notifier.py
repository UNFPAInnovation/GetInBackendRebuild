import traceback

from django.db.models import Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from app.firebase_notification import send_firebase_notification
from app.models import Appointment, User, NotificationLog, Girl, HealthMessage
from app.sms_handler import send_hw_sms, send_sms_message, sms_logger
from app.utils.constants import BEFORE, AFTER, CURRENT, USER_TYPE_CHEW, USER_TYPE_MIDWIFE
from random import shuffle


class NotifierView(APIView):
    """
    Send sms and firebase notification to vhts and midwife.
    Receives the new firebase_device_id from the android phone and updates the use model
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current_date = timezone.now().date()

    def post(self, request, *args, **kwargs):
        try:
            firebase_device_id = request.data.get('firebase_device_id')
            user_id = request.data.get('user_id')
            user = User.objects.get(id=user_id)

            print(firebase_device_id)
            user.firebase_device_id = firebase_device_id
            user.save(update_fields=['firebase_device_id'])
            return Response({"result": "success"}, 200)
        except Exception:
            print(traceback.print_exc())
        return Response({"result": "failure"}, 400)

    def get(self, request, format=None, **kwargs):
        # self.send_appointment_three_days_before_date()
        # self.send_appointment_one_day_after_date()
        # self.send_appointment_on_actual_day()
        return Response({"result": "success"}, 200)

    def send_appointment_three_days_before_date(self):
        girl_phone_numbers = []
        sms_logger("#started# ", " three days before date notifier")

        appointments = Appointment.objects.filter(
            Q(date__lt=self.current_date + timezone.timedelta(days=3)) & Q(date__gte=self.current_date))

        for appointment in appointments:
            print(appointment.date)

            # extract midwife and vht firebase device ids
            firebase_device_ids = list(
                filter(None, {appointment.user.firebase_device_id, appointment.girl.user.firebase_device_id}))
            print(firebase_device_ids)
            girl_phone_numbers.append("+256" + appointment.girl.phone_number[1:])
            print('girl_phone_numbers')
            print(girl_phone_numbers)

            # midwife and vhts phone numbers
            hw_phone_numbers = list(filter(None, {appointment.user.phone, appointment.girl.user.phone}))
            print('hw_phone_numbers')
            print(hw_phone_numbers)

            message_title = "GetIn ANC reminder"
            hw_message_body = "GetIN. " + appointment.girl.first_name + " " + appointment.girl.last_name \
                              + "'s ANC visits is in three days"

            # only send notification and sms if the user has never received. this prevents spamming
            if not NotificationLog.objects.filter(Q(appointment=appointment) & Q(stage=BEFORE)):
                send_firebase_notification(firebase_device_ids, message_title, hw_message_body)
                send_sms_message(hw_message_body, hw_phone_numbers)
                NotificationLog(appointment=appointment, stage=BEFORE).save()
        girls_message_body = "GetIN. Please visit hospital for ANC visits in three days"
        girl_phone_numbers = list(filter(None, set(girl_phone_numbers)))
        send_sms_message(girls_message_body, girl_phone_numbers)

    def send_appointment_one_day_after_date(self):
        girl_phone_numbers = []

        appointments = Appointment.objects.filter(Q(date__lte=self.current_date)
                                                  & Q(date__gte=self.current_date - timezone.timedelta(days=1)))

        for appointment in appointments:
            print(appointment.date)

            # extract midwife and vht firebase device ids
            firebase_device_ids = list({appointment.user.firebase_device_id, appointment.girl.user.firebase_device_id})
            girl_phone_numbers.append("+256" + appointment.girl.phone_number[1:])
            print('girl_phone_numbers')
            print(girl_phone_numbers)

            # midwife and vhts phone numbers
            health_workers_ids = list({appointment.user.id, appointment.girl.user.id})
            print('health_workers_ids')
            print(health_workers_ids)

            message_title = "GetIn ANC reminder"
            message_body = "GetIN. " + appointment.girl.first_name + " " + appointment.girl.last_name \
                           + "'s has missed ANC visit"

            # only send notification and sms if the user has never received. this prevents spamming
            if not NotificationLog.objects.filter(Q(appointment=appointment) & Q(stage=AFTER)):
                send_firebase_notification(firebase_device_ids, message_title, message_body)

                sender = User.objects.filter(username__icontains="admin").first()
                # send_hw_sms(message_body, sender, receiver_ids=health_workers_ids)

                NotificationLog(appointment=appointment, stage=AFTER).save()
        girls_message_body = "GetIN. You have missed your ANC visit. Please visit health facility immediately"
        # send_sms_message(girls_message_body, phone_number=girl_phone_numbers)

    def send_appointment_on_actual_day(self):
        girl_phone_numbers = []

        appointments = Appointment.objects.filter(Q(date__lte=timezone.now().replace(hour=23, minute=59, second=59))
                                                  & Q(date__gte=self.current_date))

        for appointment in appointments:
            print(appointment.date)

            # extract midwife and vht firebase device ids
            firebase_device_ids = list({appointment.user.firebase_device_id, appointment.girl.user.firebase_device_id})
            girl_phone_numbers.append("+256" + appointment.girl.phone_number[1:])
            print('girl_phone_numbers')
            print(girl_phone_numbers)

            # midwife and vhts phone numbers
            health_workers_ids = list({appointment.user.id, appointment.girl.user.id})
            print('health_workers_ids')
            print(health_workers_ids)

            message_title = "GetIn ANC reminder"
            message_body = "GetIN. " + appointment.girl.first_name + " " + appointment.girl.last_name \
                           + "'s ANC visits is today"

            # only send notification and sms if the user has never received. this prevents spamming
            if not NotificationLog.objects.filter(Q(appointment=appointment) & Q(stage__in=[CURRENT, AFTER])):
                send_firebase_notification(firebase_device_ids, message_title, message_body)

                sender = User.objects.filter(username__icontains="admin").first()
                # send_hw_sms(message_body, sender, receiver_ids=health_workers_ids)
                NotificationLog(appointment=appointment, stage=CURRENT).save()

        girls_message_body = "GetIN. Please visit hospital today for your ANC visits"
        # send_sms_message(girls_message_body, phone_number=girl_phone_numbers)

    def send_daily_usage_reminder(self):
        print('start sending daily usage reminders')
        users = User.objects.filter(Q(role__icontains=USER_TYPE_CHEW) | Q(role__icontains=USER_TYPE_MIDWIFE))
        firebase_device_ids = [user.firebase_device_id for user in users]
        message_title = 'GetIn Reminder'
        message_body = 'Please remember to use the GetIn app to map girls, follow up on appointments and call the girls'
        send_firebase_notification(firebase_device_ids, message_title, message_body)

    @staticmethod
    def get_random_health_messages():
        messages = list(HealthMessage.objects.all())
        shuffle(messages)
        return messages[0].text

    def send_health_messages(self):
        """
        Sends health messages to pregnant girls every Wednesday at 12pm
        """
        nine_months_date = timezone.timedelta(days=274)
        pregnant_girls = Girl.objects.filter(last_menstruation_date__gte=self.current_date - nine_months_date)
        phone_numbers = ["+256" + girl.phone_number[1:] for girl in pregnant_girls]
        send_sms_message(self.get_random_health_messages(), phone_numbers)
