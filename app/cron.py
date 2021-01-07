from django.utils import timezone

from app.models import Appointment, Girl
from app.notifier import NotifierView
from app.utils.constants import EXPECTED, ATTENDED, MISSED


def notifier_appointment_reminder_cron_job():
    """
    Appointment reminder. Notifies the VHT, midwife and girl about expected and missed appointments
    """
    notifier = NotifierView()
    notifier.send_appointment_sms_to_eligible_girls()
    # notifier.send_appointment_one_day_after_date()
    # notifier.send_appointment_on_actual_day()


def notifier_daily_usage_reminder_cron_job():
    """
    Sends out daily FCM notification reminder to use the GetIn mobile app
    """
    notifier = NotifierView()
    notifier.send_daily_usage_reminder()


def transition_expected_appointments():
    """
    Updates missed appointments that have EXPECTED status to MISSED status.
    This transition is made if a new appointment is not generated 24 hrs after the appointment date
    """
    try:
        print('update previous appointment status')

        girls = Girl.objects.all()

        for girl in girls:
            girl_previous_appointments = Appointment.objects.filter(girl__id=girl.id).order_by("id")
            if girl_previous_appointments.count() <= 1:
                print('Girl has less than 1 appointment')
                continue

            for girl_previous_appointment in girl_previous_appointments:
                # previous appointment must have been attended atleast within 24 hours margin on its deadline
                current_time_24_hours_ahead = timezone.now() + timezone.timedelta(hours=24)

                if girl_previous_appointment.status == EXPECTED \
                        and girl_previous_appointment.date < current_time_24_hours_ahead:
                    girl_previous_appointment.status = MISSED
                    girl_previous_appointment.save(update_fields=['status'])
    except Exception as e:
        print(e)
