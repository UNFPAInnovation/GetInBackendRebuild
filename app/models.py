import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator
from django.db import models

from app.utils.constants import *

GENDER_CHOICES = (
    (GENDER_MALE, 'male'),
    (GENDER_FEMALE, 'female'),
    (GENDER_NOT_SPECIFIED, 'not specified'),
)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=12, validators=[
        RegexValidator(
            regex='^(256|254|255)[0-9]{9}$',
            message='Wrong phone number format',
        ),
    ])
    gender = models.IntegerField(choices=GENDER_CHOICES, default=GENDER_NOT_SPECIFIED,
                                 help_text='0 - Male, 1 - Female, 2 - Not Specified')
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class DHO(User):
    district = models.CharField(max_length=50)
