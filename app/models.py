import uuid

from django.contrib.auth.models import AbstractUser
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models

from app.utils.constants import *

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


MARITAL_STATUS_CHOICES = (
    (SINGLE, 'Single'),
    (MARRIED, 'Married'),
    (DIVORCED, 'Divorced'),
)

DELIVERY_LOCATION = (
    (HOME, 'Home'),
    (HEALTH_FACILITY, 'Health Facility'),
)


class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    phone = models.CharField(max_length=12, validators=[
        RegexValidator(
            regex='^(07)[0-9]{8}$',
            message='Wrong phone number format',
        )
    ])
    gender = models.IntegerField(choices=GENDER_CHOICES, default=GENDER_NOT_SPECIFIED,
                                 help_text='0 - Male, 1 - Female, 2 - Not Specified')
    createdAt = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class District(models.Model):
    name = models.CharField(max_length=250)


class County(models.Model):
    name = models.CharField(max_length=250)
    district = models.ForeignKey(District, on_delete=models.CASCADE)


class SubCounty(models.Model):
    name = models.CharField(max_length=250)
    county = models.ForeignKey(County, on_delete=models.CASCADE)


class Parish(models.Model):
    name = models.CharField(max_length=250)
    sub_county = models.ForeignKey(SubCounty, on_delete=models.CASCADE)


class Village(models.Model):
    name = models.CharField(max_length=250)
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE)


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
    trimester = models.IntegerField(default=1, validators=[MaxValueValidator(4), MinValueValidator(1)])
    next_of_kin_name = models.CharField(max_length=250)
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
    createdAt = models.DateTimeField(auto_now_add=True)


class HealthFacility(models.Model):
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE)
    name = models.CharField(max_length=50)


class DHO(User):
    user_type = models.CharField(default='dho', max_length=50)
    district = models.ForeignKey(District, on_delete=models.CASCADE)

    def __str__(self):
        return self.username + self.user_type


class Midwife(User):
    user_type = models.CharField(default='midwife', max_length=50)
    health_facility = models.ForeignKey(HealthFacility, on_delete=models.CASCADE)

    def __str__(self):
        return self.username + self.user_type


class CHEW(User):
    user_type = models.CharField(default='chew', max_length=50)
    sub_county = models.ForeignKey(SubCounty, on_delete=models.CASCADE)
    midwife_relation = models.ForeignKey(Midwife, on_delete=models.CASCADE)

    def __str__(self):
        return self.username + self.user_type


class Ambulance(User):
    user_type = models.CharField(default='ambulance', max_length=50)
    parish = models.ForeignKey(Parish, on_delete=models.CASCADE)
    midwife_relation = models.ForeignKey(Midwife, on_delete=models.CASCADE)
    number_place = models.CharField(max_length=50)

    def __str__(self):
        return self.username + self.user_type


class FollowUp(models.Model):
    girl = models.ForeignKey(Girl, on_delete=models.CASCADE)
    midwife = models.ForeignKey(Midwife, on_delete=models.CASCADE)
    chew = models.ForeignKey(CHEW, on_delete=models.CASCADE)
    followup_reason = models.TextField()
    actionTaken = models.CharField(max_length=200)
    blurred_vision = models.BooleanField(default=False)
    bleeding_heavily = models.BooleanField(default=False)
    fever = models.BooleanField(default=False)
    swollen_feet = models.BooleanField(default=False)
    next_appointment = models.DateTimeField(auto_now_add=True)
    follow_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Delivery(models.Model):
    girl = models.ForeignKey(Girl, on_delete=models.CASCADE)
    midwife = models.ForeignKey(Midwife, on_delete=models.CASCADE)
    chew = models.ForeignKey(CHEW, on_delete=models.CASCADE)
    followup_reason = models.TextField()
    actionTaken = models.CharField(max_length=200)
    received_postnatal_care = models.BooleanField(default=True)
    is_mother_alive = models.BooleanField(default=True)
    is_baby_alive = models.BooleanField(default=True)
    is_baby_alive = models.BooleanField(default=True)
    baby_death_date = models.DateTimeField(blank=True, null=True)
    baby_birth_date = models.DateTimeField(blank=True, null=True)
    mother_death_date = models.DateTimeField(blank=True, null=True)
    using_family_planning = models.BooleanField(default=True)
    no_family_planning_reason = models.CharField(max_length=250)
    family_planning_type = models.CharField(max_length=250)
    health_facility = models.CharField(max_length=200)
    delivery_date = models.DateTimeField(auto_now_add=True)
    created_at = models.DateTimeField(auto_now_add=True)
