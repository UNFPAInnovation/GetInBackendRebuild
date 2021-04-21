from django.core.mail import send_mail
from GetInBackendRebuild.settings import EMAIL_HOST_USER


def send_email(subject, message, recipients):
    send_mail(subject, message, EMAIL_HOST_USER, recipients, fail_silently=False)
