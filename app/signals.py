from django.db.models.signals import post_save
from django.dispatch import receiver

from app.models import Appointment
from app.utils.constants import ATTENDED


@receiver(post_save, sender=Appointment)
def update_last_appointment_status(sender, **kwargs):
    """
    Updates the last appointment status to Attended
    The midwife creates a new appointment(ANC) which then changes the state of the previous visit to attended
    """
    try:
        last_appointment = Appointment.objects.all()[Appointment.objects.count()-2]
        last_appointment.status = ATTENDED
        last_appointment.save(update_fields=['status'])
    except Exception as e:
        print(e)
