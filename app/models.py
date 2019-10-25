import datetime
import uuid

import pytz
from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from app.utils.constants import GENDER_FEMALE, GENDER_MALE, GENDER_NOT_SPECIFIED, PRIMARY_LEVEL, O_LEVEL, A_LEVEL, \
    TERTIARY_LEVEL, SINGLE, MARRIED, DIVORCED, HOME, HEALTH_FACILITY, USER_TYPE_DEVELOPER, USER_TYPE_DHO, \
    USER_TYPE_CHEW, USER_TYPE_MIDWIFE, USER_TYPE_AMBULANCE, USER_TYPE_MANAGER

GENDER_CHOICES = (
    (GENDER_MALE, 'male'),
    (GENDER_FEMALE, 'female'),
    (GENDER_NOT_SPECIFIED, 'not specified'),
)

EDUCATION_CHOICES = (
    (PRIMARY_LEVEL, 'Primary Level'),
    (O_LEVEL, 'O Level'),
    (A_LEVEL, 'A Level'),
    (TERTIARY_LEVEL, 'Tertiary Level'),
)


MARITAL_STATUS_CHOICES = {
    (SINGLE, 'Single'),
    (MARRIED, 'Married'),
    (DIVORCED, 'Divorced'),
}

DELIVERY_LOCATION = (
    (HOME, 'Home'),
    (HEALTH_FACILITY, 'Health Facility'),
)

USER_TYPE_CHOICES = (
    (USER_TYPE_DEVELOPER, 'Developer'),
    (USER_TYPE_DHO, 'DHO'),
    (USER_TYPE_CHEW, 'CHEW'),
    (USER_TYPE_MIDWIFE, 'Midwife'),
    (USER_TYPE_AMBULANCE, 'Ambulance'),
)


class District(models.Model):
    name = models.CharField(max_length=250)

    def __str__(self):
        return self.name


class County(models.Model):
    name = models.CharField(max_length=250)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class SubCounty(models.Model):
    name = models.CharField(max_length=250)
    county = models.ForeignKey(County, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Parish(models.Model):
    name = models.CharField(max_length=250)
    sub_county = models.ForeignKey(SubCounty, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class Village(models.Model):
    name = models.CharField(max_length=250)
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class Girl(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=250)
    last_name = models.CharField(max_length=250)
    village = models.ForeignKey(Village, on_delete=models.CASCADE)
    phone_number = models.CharField(max_length=12, validators=[
        RegexValidator(
            regex='^(07)[0-9]{8}$',
            message='Wrong phone number format',
        )
    ])
    trimester = models.IntegerField(default=1, validators=[MaxValueValidator(3), MinValueValidator(1)])
    next_of_kin_last_name = models.CharField(max_length=250)
    next_of_kin_first_name = models.CharField(max_length=250)
    next_of_kin_phone_number = models.CharField(max_length=12, validators=[
        RegexValidator(
            regex='^(07)[0-9]{8}$',
            message='Wrong phone number format',
        )
    ])
    education_level = models.CharField(choices=EDUCATION_CHOICES, default=PRIMARY_LEVEL, max_length=250)
    marital_status = models.CharField(choices=MARITAL_STATUS_CHOICES, default=SINGLE, max_length=250)
    # todo add constraint
    last_menstruation_date = models.DateField()
    # calculate expected_delivery from last menstruation date
    # expected_delivery_date = models.DateTimeField()
    dob = models.DateField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.last_name + " " + self.first_name

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_read_permission(request):
        # return request.user.type in [USER_TYPE_CHEW,
        #                              USER_TYPE_MIDWIFE] or request.user.is_staff
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        # calculate trimester of the girl based on the last menstruation date
        # trimester 1 = 1-12 weeks, trimester 2 = 13-26 weeks, trimester 3 = 27-40

        days_diff = (timezone.now().date() - self.last_menstruation_date).days
        if days_diff >= 189:
            self.trimester = 3
        elif days_diff >= 91:
            self.trimester = 2
        else:
            self.trimester = 1

        super(Girl, self).save(force_insert, force_update, using, update_fields)


class HealthFacility(models.Model):
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    type = models.IntegerField(choices=USER_TYPE_CHOICES, default=USER_TYPE_DEVELOPER)
    phone = models.CharField(max_length=12, validators=[
        RegexValidator(
            regex='^(07)[0-9]{8}$',
            message='Wrong phone number format',
        )
    ])
    gender = models.IntegerField(choices=GENDER_CHOICES, default=GENDER_NOT_SPECIFIED,
                                 help_text='0 - Male, 1 - Female, 2 - Not Specified')
    created_at = models.DateTimeField(auto_now_add=True)
    number_place = models.CharField(max_length=50)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, blank=True, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null=True)
    number_plate = models.CharField(max_length=50, blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.type in [USER_TYPE_DEVELOPER, USER_TYPE_DHO]:
            self.is_staff = True
        if self.type in [USER_TYPE_DEVELOPER, USER_TYPE_MANAGER]:
            self.is_superuser = True
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    @staticmethod
    def has_write_permission(request):
        # return request.user.type in [USER_TYPE_CHEW,
        #                              USER_TYPE_MIDWIFE] or request.user.is_staff or request.user.is_superuser
        return True

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True


class FollowUp(models.Model):
    girl = models.ForeignKey(Girl, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followup_reason = models.TextField()
    action_taken = models.CharField(max_length=200)
    blurred_vision = models.BooleanField(default=False)
    bleeding_heavily = models.BooleanField(default=False)
    fever = models.BooleanField(default=False)
    swollen_feet = models.BooleanField(default=False)
    next_appointment = models.DateTimeField(auto_now_add=True)
    follow_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @staticmethod
    def has_write_permission(request):
        return request.user.type in [USER_TYPE_CHEW, USER_TYPE_MIDWIFE] or request.user.is_staff or request.user.is_superuser

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True


class Delivery(models.Model):
    girl = models.ForeignKey(Girl, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followup_reason = models.CharField(max_length=200)
    action_taken = models.CharField(max_length=200)
    received_postnatal_care = models.BooleanField(default=True)
    is_mother_alive = models.BooleanField(default=True)
    is_baby_alive = models.BooleanField(default=True)
    baby_death_date = models.DateTimeField(blank=True, null=True)
    baby_birth_date = models.DateTimeField(blank=True, null=True)
    mother_death_date = models.DateTimeField(blank=True, null=True)
    using_family_planning = models.BooleanField(default=True)
    no_family_planning_reason = models.CharField(max_length=250)
    family_planning_type = models.CharField(max_length=250)
    health_facility = models.ForeignKey(HealthFacility, on_delete=models.CASCADE, blank=True, null=True)
    delivery_date = models.DateTimeField(auto_now_add=True)
    delivery_location = models.CharField(choices=DELIVERY_LOCATION, default=HOME, max_length=250)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    @staticmethod
    def has_write_permission(request):
        # return request.user.type in [USER_TYPE_CHEW,
        #                              USER_TYPE_MIDWIFE] or request.user.is_staff or request.user.is_superuser
        return True
    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True
