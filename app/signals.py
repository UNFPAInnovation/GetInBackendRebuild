from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import Appointment
from app.utils.constants import ATTENDED, EXPECTED


@receiver(post_save, sender=Appointment)
def update_last_appointment_status(sender, **kwargs):
    """
    Updates the last appointment status to ATTENDED only if it has not been MISSED
    The midwife creates a new appointment(ANC) which then changes the state of the previous visit to attended
    """
    try:
        print('update previous appointment status')
        last_appointment = Appointment.objects.last()
        girl_previous_appointments = Appointment.objects.filter(girl__id=last_appointment.girl.id)
        second_last_appointment = girl_previous_appointments[girl_previous_appointments.count() -2]

        print(second_last_appointment.status)
        if second_last_appointment.status == EXPECTED:
            second_last_appointment.status = ATTENDED
            second_last_appointment.save(update_fields=['status'])
            print(second_last_appointment)
            print("changed second last appointment status")
    except Exception as e:
        print(e)
