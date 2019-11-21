import traceback

from django.db.models import Q
from django.utils import timezone
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from app.firebase_notification import send_firebase_notification
from app.models import Appointment, MappingEncounter, User, NotificationLog
from app.sms_handler import send_sms, send_single_sms
from app.utils.constants import BEFORE, AFTER, CURRENT, EXPECTED, MISSED


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
        self.send_appointment_three_days_before_date()
        self.send_appointment_three_days_after_date()
        self.send_appointment_on_actual_day()
        return Response({"result": "success"}, 200)

    def send_appointment_three_days_before_date(self):
        girl_phone_numbers = []

        appointments = Appointment.objects.filter(
            Q(date__lt=self.current_date + timezone.timedelta(days=3)) & Q(date__gte=self.current_date))

        for appointment in appointments:
            print(appointment.date)

            # extract midwife and vht firebase device ids
            firebase_device_ids = list({appointment.user.firebase_device_id, appointment.girl.user.firebase_device_id})
            girl_phone_numbers.append(appointment.girl.phone_number)
            print('girl_phone_numbers')
            print(girl_phone_numbers)

            # midwife and vhts phone numbers
            health_worker_ids = list({appointment.user.id, appointment.girl.user.id})
            print('health_worker_ids')
            print(health_worker_ids)

            # TODO REMOVE ON RELEASE
            health_worker_ids = ['0756878460']
            girl_phone_numbers = ['0756878460']

            message_title = "GetIn ANC reminder"
            message_body = "GetIN. " + appointment.girl.first_name + " " + appointment.girl.last_name \
                           + "'s ANC visits is in three days"
            girls_message_body = "GetIN. Please visit hospital for ANC visits in three days"

            # only send notification and sms if the user has never received. this prevents spamming
            if not NotificationLog.objects.filter(Q(appointment=appointment) & Q(stage=BEFORE)):
                send_firebase_notification(firebase_device_ids, message_title, message_body)

                sender = User.objects.get(username__icontains="admin")
                send_sms(girls_message_body, sender, receiver_ids=health_worker_ids)
                send_single_sms(message_body, phone_number=girl_phone_numbers)

                NotificationLog(appointment=appointment, stage=BEFORE).save()

    def send_appointment_three_days_after_date(self):
        girl_phone_numbers = []

        appointments = Appointment.objects.filter(Q(date__lte=self.current_date)
                                                  & Q(date__gte=self.current_date - timezone.timedelta(days=3)))

        for appointment in appointments:
            print(appointment.date)

            # extract midwife and vht firebase device ids
            firebase_device_ids = list({appointment.user.firebase_device_id, appointment.girl.user.firebase_device_id})
            girl_phone_numbers.append(appointment.girl.phone_number)
            print('girl_phone_numbers')
            print(girl_phone_numbers)

            # midwife and vhts phone numbers
            health_workers_ids = list({appointment.user.id, appointment.girl.user.id})
            print('health_workers_ids')
            print(health_workers_ids)

            # TODO REMOVE ON RELEASE
            health_workers_ids = ['0756878460']
            girl_phone_numbers = ['0756878460']

            message_title = "GetIn ANC reminder"
            message_body = "GetIN. " + appointment.girl.first_name + " " + appointment.girl.last_name \
                           + "'s has missed ANC visit"
            girls_message_body = "GetIN. You have missed your ANC visit. Please visit health facility immediately"

            # only send notification and sms if the user has never received. this prevents spamming
            if not NotificationLog.objects.filter(Q(appointment=appointment) & Q(stage=AFTER)):
                send_firebase_notification(firebase_device_ids, message_title, message_body)

                sender = User.objects.get(username__icontains="admin")
                send_sms(girls_message_body, sender, receiver_ids=health_workers_ids)
                send_single_sms(message_body, phone_number=girl_phone_numbers)

                NotificationLog(appointment=appointment, stage=AFTER).save()

    def send_appointment_on_actual_day(self):
        girl_phone_numbers = []

        appointments = Appointment.objects.filter(Q(date__lte=timezone.now().replace(hour=23, minute=59, second=59))
                                                  & Q(date__gte=self.current_date))

        for appointment in appointments:
            print(appointment.date)

            # extract midwife and vht firebase device ids
            firebase_device_ids = list({appointment.user.firebase_device_id, appointment.girl.user.firebase_device_id})
            girl_phone_numbers.append(appointment.girl.phone_number)
            print('girl_phone_numbers')
            print(girl_phone_numbers)

            # midwife and vhts phone numbers
            health_workers_ids = list({appointment.user.id, appointment.girl.user.id})
            print('health_workers_ids')
            print(health_workers_ids)

            # TODO REMOVE ON RELEASE
            health_workers_ids = ['0756878460']
            girl_phone_numbers = ['0756878460']

            message_title = "GetIn ANC reminder"
            message_body = "GetIN. " + appointment.girl.first_name + " " + appointment.girl.last_name \
                           + "'s ANC visits is today"
            girls_message_body = "GetIN. Please visit hospital today for your ANC visits"

            # only send notification and sms if the user has never received. this prevents spamming
            if not NotificationLog.objects.filter(Q(appointment=appointment) & Q(stage__in=[CURRENT, AFTER])):
                send_firebase_notification(firebase_device_ids, message_title, message_body)

                sender = User.objects.get(username__icontains="admin")
                send_sms(girls_message_body, sender, receiver_ids=health_workers_ids)
                send_single_sms(message_body, phone_number=girl_phone_numbers)

                NotificationLog(appointment=appointment, stage=CURRENT).save()
