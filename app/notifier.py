import traceback

from django.db.models import Q
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from app.firebase_notification import send_firebase_notification
from app.models import Appointment, User, NotificationLog, Girl, HealthMessage
from app.sms_handler import send_sms_message, sms_logger
from app.utils.constants import BEFORE, AFTER, CURRENT, USER_TYPE_CHEW, USER_TYPE_MIDWIFE, EXPECTED, MISSED
from random import shuffle

from app.utils.utilities import de_emojify


class NotifierView(APIView):
    """
    Send sms and firebase notification to vhts and midwife.
    Receives the new firebase_device_id from the android phone and updates the use model
    """

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # .date() ensures that the time is midnight
        self.current_date = timezone.now().date()
        self.nine_months_date = timezone.timedelta(days=274)

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
        self.send_appointment_sms_to_eligible_girls()
        self.send_missed_appointment_reminder_one_day_after()
        return Response({"result": "success"}, 200)

    def send_appointment_sms_to_eligible_girls(self):
        girl_today_phone_numbers = []
        girl_tomorrow_phone_numbers = []
        girl_three_days_phone_numbers = []
        sms_logger("#started# ", " today, tomorrow, three days before date notifier")
        appointments = Appointment.objects.filter(
            Q(date__lte=self.current_date + timezone.timedelta(days=4))
            & Q(date__gte=self.current_date) & Q(status=EXPECTED)
            & Q(girl__last_menstruation_date__gte=self.current_date - self.nine_months_date))

        for appointment in appointments:
            days_to_appointment = (appointment.date - timezone.now()).days
            if appointment.date.day == self.current_date.day:
                girl_today_phone_numbers.append("+256" + appointment.girl.phone_number[1:])
            elif days_to_appointment == 0:
                girl_tomorrow_phone_numbers.append("+256" + appointment.girl.phone_number[1:])
            elif days_to_appointment == 2:
                girl_three_days_phone_numbers.append("+256" + appointment.girl.phone_number[1:])

        girl_today_message = "Today is the due day for your ANC visit, your midwife is waiting to receive you at the health facility. From GETIN TEAM"
        girl_tomorrow_message = "Your next ANC visit is due tomorrow, please don't forget to attend your appointment for the safety of your unborn baby. From GETIN TEAM"
        girl_three_days_message = "Your next ANC visit is due in 3 days, please don't forget to attend your appointment for the safety of your unborn baby. From GETIN TEAM"
        send_sms_message(girl_today_message, list(filter(None, set(girl_today_phone_numbers))))
        send_sms_message(girl_tomorrow_message, list(filter(None, set(girl_tomorrow_phone_numbers))))
        send_sms_message(girl_three_days_message, list(filter(None, set(girl_three_days_phone_numbers))))

    def send_missed_appointment_reminder_one_day_after(self):
        appointments = Appointment.objects.filter(
            Q(date__lt=self.current_date)
            & Q(date__gte=self.current_date - timezone.timedelta(days=1))
            & Q(status__in=[EXPECTED, MISSED])
            & Q(girl__last_menstruation_date__gte=self.current_date - self.nine_months_date))

        for appointment in appointments:
            yesterday = self.current_date - timezone.timedelta(days=1)
            # skip days that are not yesterday
            if appointment.date.day != yesterday.day:
                continue

            firebase_device_ids = list({appointment.user.firebase_device_id, appointment.girl.user.firebase_device_id})
            health_workers_ids = list({appointment.user.id, appointment.girl.user.id})

            message_title = "GetIn ANC reminder"
            message_body = de_emojify(appointment.girl.first_name) + " " + de_emojify(
                appointment.girl.last_name) + " has missed ANC visit yesterday. Please call or visit her to find out the reason why she missed. From GETIN TEAM"

            # only send notification and sms if the user has never received. this prevents spamming
            if not NotificationLog.objects.filter(Q(appointment=appointment) & Q(stage=AFTER)):
                send_firebase_notification(firebase_device_ids, message_title, message_body)
                phone_numbers = ["+256" + User.objects.get(id=receiver_id).phone[1:] for receiver_id in
                                 health_workers_ids]
                send_sms_message(message_body, phone_numbers)
                NotificationLog(appointment=appointment, stage=AFTER).save()

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
        pregnant_girls = Girl.objects.filter(last_menstruation_date__gte=self.current_date - self.nine_months_date)
        phone_numbers = ["+256" + girl.phone_number[1:] for girl in pregnant_girls]
        send_sms_message(self.get_random_health_messages(), phone_numbers)
