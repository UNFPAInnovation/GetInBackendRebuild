import datetime
import uuid

import pytz
from django.contrib.auth.models import AbstractUser, Permission
from django.core.validators import RegexValidator, MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from rest_framework.exceptions import ValidationError

from app.utils.constants import GENDER_FEMALE, GENDER_MALE, PRIMARY_LEVEL, O_LEVEL, A_LEVEL, \
    TERTIARY_LEVEL, SINGLE, MARRIED, DIVORCED, HOME, HEALTH_FACILITY, USER_TYPE_DEVELOPER, USER_TYPE_DHO, \
    USER_TYPE_CHEW, USER_TYPE_MIDWIFE, USER_TYPE_AMBULANCE, USER_TYPE_MANAGER, MISSED, ATTENDED, EXPECTED

GENDER_CHOICES = (
    (GENDER_MALE, 'male'),
    (GENDER_FEMALE, 'female'),
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
    (USER_TYPE_DEVELOPER, 'developer'),
    (USER_TYPE_DHO, 'dho'),
    (USER_TYPE_CHEW, 'chew'),
    (USER_TYPE_MIDWIFE, 'midwife'),
    (USER_TYPE_AMBULANCE, 'ambulance'),
)

APPOINTMENT = (
    (MISSED, 'Missed'),
    (ATTENDED, 'Attended'),
    (EXPECTED, 'Expected'),
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
    role = models.CharField(choices=USER_TYPE_CHOICES, default=USER_TYPE_DEVELOPER, max_length=50,
                            help_text='developer - Developer, dho - DHO, chew - CHEW, midwife - Midwife, '
                                      'ambulance - Ambulance, manager - Manager')
    phone = models.CharField(max_length=12, validators=[
        RegexValidator(
            regex='^(07)[0-9]{8}$',
            message='Wrong phone number format',
        )
    ], unique=True)
    gender = models.CharField(choices=GENDER_CHOICES, default=GENDER_FEMALE, max_length=50,
                              help_text='male - Male, female - Female')
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    number_plate = models.CharField(max_length=50, blank=True, null=True)
    village = models.ForeignKey(Village, on_delete=models.CASCADE, blank=True, null=True)
    district = models.ForeignKey(District, on_delete=models.CASCADE, blank=True, null=True)
    # midwife attached to vht. Midwife can have two VHTs at a time while VHT has one midwife
    midwife = models.ForeignKey('User', on_delete=models.DO_NOTHING, blank=True, null=True)
    # allows use to access these fields in /auth/me
    REQUIRED_FIELDS = ["phone", "role"]

    def save(self, *args, **kwargs):
        if self.role in [USER_TYPE_DEVELOPER, USER_TYPE_DHO]:
            self.is_staff = True
        if self.role in [USER_TYPE_DEVELOPER, USER_TYPE_MANAGER]:
            self.is_superuser = True

        # the user attached to the CHEW should only be midwife
        if self.midwife:
            if self.midwife.role is not USER_TYPE_MIDWIFE:
                raise ValidationError("Attached person is not a midwife")

        if self.village:
            # only get the village and extract the rest of the fields from there
            self.district = self.village.parish.sub_county.county.district
        super(User, self).save(*args, **kwargs)

    def __str__(self):
        return self.username

    @staticmethod
    def has_write_permission(request):
        # return request.user.role in [USER_TYPE_CHEW,
        #                              USER_TYPE_MIDWIFE] or request.user.is_staff or request.user.is_superuser
        return True

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True


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
    ], blank=True, null=True)
    trimester = models.IntegerField(default=1, validators=[MaxValueValidator(3), MinValueValidator(1)])
    next_of_kin_last_name = models.CharField(max_length=250, blank=True, null=True)
    next_of_kin_first_name = models.CharField(max_length=250, blank=True, null=True)
    next_of_kin_phone_number = models.CharField(max_length=12, validators=[
        RegexValidator(
            regex='^(07)[0-9]{8}$',
            message='Wrong phone number format',
        )
    ], blank=True, null=True)
    education_level = models.CharField(choices=EDUCATION_CHOICES, default=PRIMARY_LEVEL, max_length=250)
    marital_status = models.CharField(choices=MARITAL_STATUS_CHOICES, default=SINGLE, max_length=250)
    # todo add constraint
    last_menstruation_date = models.DateField()
    # calculate expected_delivery from last menstruation date
    # expected_delivery_date = models.DateTimeField()
    dob = models.DateField()
    age = models.IntegerField(blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    pending_visits = models.IntegerField(default=3, validators=[MaxValueValidator(3), MinValueValidator(0)])
    missed_visits = models.IntegerField(default=0, validators=[MaxValueValidator(3), MinValueValidator(0)])
    completed_all_visits = models.BooleanField(default=False, blank=True, null=True)
    odk_instance_id = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.last_name + " " + self.first_name

    @staticmethod
    def has_write_permission(request):
        return True

    @staticmethod
    def has_read_permission(request):
        # return request.user.role in [USER_TYPE_CHEW,
        #                              USER_TYPE_MIDWIFE] or request.user.is_staff
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):

        self.set_trimester()
        self.set_age_field()

        super(Girl, self).save(force_insert, force_update, using, update_fields)

    def set_trimester(self):
        # calculate trimester of the girl based on the last menstruation date
        # trimester 1 = 1-12 weeks, trimester 2 = 13-26 weeks, trimester 3 = 27-40
        try:
            # error is thrown when updating from django admin
            year, month, day = [int(x) for x in self.last_menstruation_date.split("-")]
            self.last_menstruation_date = timezone.datetime(year, month, day)
        except Exception as e:
            print(e)
        try:
            days_diff = (timezone.now().replace(tzinfo=pytz.utc) - self.last_menstruation_date
                         .replace(tzinfo=pytz.utc)).days
        except TypeError as e:
            print(e)
            days_diff = (timezone.now().date() - self.last_menstruation_date).days
        if days_diff >= 189:
            self.trimester = 3
        elif days_diff >= 91:
            self.trimester = 2
        else:
            self.trimester = 1

    def set_age_field(self):
        try:
            # error is thrown when updating from django admin
            year, month, day = [int(x) for x in self.dob.split("-")]
            self.dob = timezone.datetime(year, month, day)
        except Exception as e:
            print(e)
        try:
            days_diff = (timezone.now().replace(tzinfo=pytz.utc) - self.dob
                         .replace(tzinfo=pytz.utc)).days
        except TypeError as e:
            print(e)
            days_diff = (timezone.now().date() - self.dob).days
        self.age = int(days_diff / 365)


class FollowUp(models.Model):
    girl = models.ForeignKey(Girl, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    followup_reason = models.TextField(blank=True, null=True)
    blurred_vision = models.BooleanField(default=False)
    bleeding_heavily = models.BooleanField(default=False)
    fever = models.BooleanField(default=False)
    swollen_feet = models.BooleanField(default=False)
    follow_up_action_taken = models.CharField(max_length=400, blank=True, null=True)
    odk_instance_id = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.girl.first_name + " " + self.girl.last_name

    @staticmethod
    def has_write_permission(request):
        return request.user.role in [USER_TYPE_CHEW, USER_TYPE_MIDWIFE] or request.user.is_staff \
               or request.user.is_superuser

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True


class MappingEncounter(models.Model):
    girl = models.ForeignKey(Girl, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    using_family_planning = models.BooleanField(default=True)
    no_family_planning_reason = models.CharField(max_length=250, blank=True, null=True)
    family_planning_type = models.CharField(max_length=250, blank=True, null=True)
    blurred_vision = models.BooleanField(default=False)
    bleeding_heavily = models.BooleanField(default=False)
    fever = models.BooleanField(default=False)
    swollen_feet = models.BooleanField(default=False)
    voucher_card = models.CharField(max_length=250, blank=True, null=True)
    attended_anc_visit = models.BooleanField(default=False)
    voucher_number = models.IntegerField(default=0, blank=True, null=True)
    odk_instance_id = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.girl.last_name + " " + self.girl.first_name

    @staticmethod
    def has_write_permission(request):
        return request.user.role in [USER_TYPE_CHEW, USER_TYPE_MIDWIFE] or request.user.is_staff \
               or request.user.is_superuser

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True


class AppointmentEncounter(models.Model):
    girl = models.ForeignKey(Girl, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    needed_ambulance = models.BooleanField(default=False)
    missed_anc_before = models.BooleanField(default=False)
    used_ambulance = models.BooleanField(default=False)
    missed_anc_reason = models.CharField(max_length=250, blank=True, null=True)
    action_taken = models.CharField(max_length=250, blank=True, null=True)
    appointment_method = models.CharField(max_length=250, blank=True, null=True)
    blurred_vision = models.BooleanField(default=False)
    bleeding_heavily = models.BooleanField(default=False)
    fever = models.BooleanField(default=False)
    swollen_feet = models.BooleanField(default=False)
    odk_instance_id = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.girl.last_name + " " + self.girl.first_name

    @staticmethod
    def has_write_permission(request):
        return request.user.role in [USER_TYPE_CHEW, USER_TYPE_MIDWIFE] or request.user.is_staff \
               or request.user.is_superuser

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
    postnatal_care = models.BooleanField(default=True)
    mother_alive = models.BooleanField(default=True)
    baby_alive = models.BooleanField(default=True)
    baby_death_date = models.DateTimeField(blank=True, null=True)
    baby_birth_date = models.DateTimeField(blank=True, null=True)
    mother_death_date = models.DateTimeField(blank=True, null=True)
    using_family_planning = models.BooleanField(default=True)
    no_family_planning_reason = models.CharField(max_length=250, blank=True, null=True)
    family_planning_type = models.CharField(max_length=250, blank=True, null=True)
    health_facility = models.ForeignKey(HealthFacility, on_delete=models.CASCADE, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)
    delivery_location = models.CharField(choices=DELIVERY_LOCATION, default=HOME, max_length=250)
    odk_instance_id = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.girl.first_name + " " + self.girl.last_name

    @staticmethod
    def has_write_permission(request):
        # return request.user.role in [USER_TYPE_CHEW,
        #                              USER_TYPE_MIDWIFE] or request.user.is_staff or request.user.is_superuser
        return True

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True


class Appointment(models.Model):
    # Also known as ANC visit
    girl = models.ForeignKey(Girl, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateTimeField(blank=True, null=True)
    health_facility = models.ForeignKey(HealthFacility, on_delete=models.CASCADE, blank=True, null=True)
    status = models.CharField(choices=APPOINTMENT, default=EXPECTED, max_length=250)
    odk_instance_id = models.CharField(max_length=250, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.girl.first_name + " " + self.girl.last_name

    def save(self, force_insert=False, force_update=False, using=None,
             update_fields=None):
        self.update_pending_and_completed_visits(force_insert, force_update, update_fields, using)

    def update_pending_and_completed_visits(self, force_insert, force_update, update_fields, using):
        """
        Mapped girls must attend only three pending visits
        When midwife creates an appointment(ANC visit) date,
        the previous appointment is marked off as attended since the girl will have visited the health facility
        This is done in signals.py - update_last_appointment_status.
        signals.py is called after an appointment is saved
        """
        try:
            print("save appointment")
            last_appointment = Appointment.objects.filter(girl=self.girl).last()
            print(last_appointment)

            # save first time appointment
            if not last_appointment:
                super(Appointment, self).save(force_insert, force_update, using, update_fields)
            else:
                girl = self.girl
                if girl.pending_visits > 0:
                    super(Appointment, self).save(force_insert, force_update, using, update_fields)
                    # reduce the pending visits once the girl has attend a health facility
                    girl.pending_visits = girl.pending_visits - 1
                    girl.save(update_fields=['pending_visits'])
                else:
                    raise ValidationError("Girl cannot have any more appointments")
        except Exception as e:
            print(e)

    @staticmethod
    def has_write_permission(request):
        # return request.user.role in [USER_TYPE_CHEW,
        #                              USER_TYPE_MIDWIFE] or request.user.is_staff or request.user.is_superuser
        return True

    @staticmethod
    def has_read_permission(request):
        return True

    @staticmethod
    def has_object_write_permission(self, request):
        return True


class SmsModel(models.Model):
    recipient = models.ForeignKey('User', on_delete=models.CASCADE)
    message = models.CharField(max_length=400, blank=True, null=True)
    message_id = models.CharField(max_length=200, blank=True, null=True)
    status = models.CharField(max_length=200, blank=True, null=True)
    sender_id = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)


    @staticmethod
    def has_write_permission(request):
        return request.user.role in [USER_TYPE_DHO] or request.user.is_superuser

    @staticmethod
    def has_read_permission(request):
        return request.user.role in [USER_TYPE_DHO] or request.user.is_superuser

    @staticmethod
    def has_object_write_permission(self, request):
        return True
