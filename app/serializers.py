import jwt
from djoser.serializers import TokenSerializer
from rest_framework import serializers
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.utils import jwt_payload_handler

from GetInBackendRebuild.settings import SECRET_KEY
from app.models import User, District, County, SubCounty, Parish, Village, Girl, HealthFacility, FollowUp, Delivery, \
    MappingEncounter, AppointmentEncounter, Appointment, SmsModel, Observation, FamilyPlanning, Region, MSIService, \
    Disability

from app.utils.constants import USER_TYPE_MIDWIFE, USER_TYPE_CHEW, USER_TYPE_AMBULANCE


def create_token(user=None):
    payload = jwt_payload_handler(user)
    token = jwt.encode(payload, SECRET_KEY)
    return token.decode('unicode_escape')


class LocationMSISerializer(serializers.Field):
    def to_representation(self, village):
        parish = village.parish
        sub_county = parish.sub_county
        county = sub_county.county
        district = county.district
        region = district.region

        data = {
            "village": {
                "id": village.id,
                "name": village.name
            },
            "parish": {
                "id": parish.id,
                "name": parish.name
            },
            "sub_county": {
                "id": sub_county.id,
                "name": sub_county.name
            },
            "county": {
                "id": county.id,
                "name": county.name
            },
            "district": {
                "id": district.id,
                "name": district.name
            },
            "region": {
                "id": region.id,
                "name": region.name
            }
        }
        return data


class MidwifeSerializer(serializers.Field):
    def to_representation(self, health_facility):
        return User.objects.filter(health_facility__name=health_facility.name, role=USER_TYPE_MIDWIFE).count()


class ChewSerializer(serializers.Field):
    def to_representation(self, health_facility):
        return User.objects.filter(health_facility__name=health_facility.name, role=USER_TYPE_CHEW).count()


class AmbulanceSerializer(serializers.Field):
    def to_representation(self, health_facility):
        return User.objects.filter(health_facility__name=health_facility.name, role=USER_TYPE_AMBULANCE).count()


class AverageDeliveriesSerializer(serializers.Field):
    def to_representation(self, health_facility):
        return Delivery.objects.filter(user__health_facility__name=health_facility.name).count()


class MSIServicesSerializer(serializers.Field):
    def to_representation(self, girl):
        msi_services = MSIService.objects.filter(girl=girl)
        return ",".join([service.option for service in msi_services])


class GirlHealthFacilitySerializer(serializers.Field):
    def to_representation(self, girl):
        try:
            user = girl.user.midwife if girl.user.role == USER_TYPE_CHEW else girl.user
            return HealthFacility.objects.filter(user__health_facility__id=user.health_facility.id).first().name
        except Exception as e:
            return ""


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'email', 'phone', 'password', 'gender', 'village', 'number_plate',
            'role', 'midwife')

    def create(self, validated_data):
        """
        Sets user password.
        NOTE: Without this, User will never sign_in and password will not be encrypted
        """
        user = User.objects.create_user(**validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user


class UserGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'gender', 'village', 'number_plate', 'role', 'phone')


class DistrictGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = '__all__'


class CountyGetSerializer(serializers.ModelSerializer):
    district = DistrictGetSerializer(many=False, read_only=True)

    class Meta:
        model = County
        fields = '__all__'


class SubCountyGetSerializer(serializers.ModelSerializer):
    county = CountyGetSerializer(many=False, read_only=True)

    class Meta:
        model = SubCounty
        fields = '__all__'


class ParishGetSerializer(serializers.ModelSerializer):
    sub_county = SubCountyGetSerializer(many=False, read_only=True)

    class Meta:
        model = Parish
        fields = '__all__'


class VillageGetSerializer(serializers.ModelSerializer):
    parish = ParishGetSerializer(many=False, read_only=True)
    parish_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Village
        fields = '__all__'


class HealthFacilityGetSerializer(serializers.ModelSerializer):
    sub_county_id = serializers.IntegerField(write_only=True)
    sub_county = SubCountyGetSerializer(many=False, read_only=True)
    midwife = MidwifeSerializer(source='*', read_only=True)
    chew = ChewSerializer(source='*', read_only=True)
    ambulance = AmbulanceSerializer(source='*', read_only=True)
    average_deliveries = AverageDeliveriesSerializer(source='*', read_only=True)

    class Meta:
        model = HealthFacility
        fields = (
            'id', 'sub_county', 'name', 'sub_county_id', 'facility_level', 'midwife', 'chew', 'ambulance',
            'average_deliveries')


class UserSerializer(serializers.ModelSerializer):
    village = VillageGetSerializer(many=False, read_only=True)
    midwife = UserGetSerializer(read_only=True)
    health_facility = HealthFacilityGetSerializer(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'phone', 'password', 'gender', 'village',
            'number_plate',
            'role', 'midwife', 'user_permissions', 'created_at', 'health_facility')
        # extra_kwargs = {"password": {"write_only": True}}

    def validate_phone(self, value):
        # user can only register one phone number
        user = User.objects.filter(phone=value)
        if user.exists():
            raise ValidationError("This user has already registered with the phone number")
        return value

    def create(self, validated_data):
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            username=validated_data['username'],
            email=validated_data['email'],
            phone=validated_data['phone'],
        )
        user.set_password(validated_data['phone'])
        user.save()
        return user


class DisabilitySerializer(serializers.ModelSerializer):

    class Meta:
        model = Disability
        fields = '__all__'


class GirlSerializer(serializers.ModelSerializer):
    village = VillageGetSerializer(many=False, read_only=True)
    village_id = serializers.IntegerField(write_only=True)
    services_received = MSIServicesSerializer(source='*', read_only=True)
    health_facility = GirlHealthFacilitySerializer(source='*', read_only=True)
    disabilities = DisabilitySerializer(many=True, read_only=True)

    class Meta:
        model = Girl
        # list all the fields since the age property is not picked up by __all__
        fields = (
            'id', 'first_name', 'last_name', 'village', 'village_id', 'phone_number', 'trimester', 'health_facility',
            'next_of_kin_phone_number', 'education_level', 'marital_status', 'voucher_expiry_date', 'disabilities',
            'last_menstruation_date', 'dob', 'user', 'odk_instance_id', 'age', 'completed_all_visits', 'voucher_number',
            'pending_visits', 'missed_visits', 'services_received', 'nationality', 'disabled', 'created_at')


class GirlMSIDateFormattedSerializer(serializers.ModelSerializer):
    village = VillageGetSerializer(many=False, read_only=True)
    village_id = serializers.IntegerField(write_only=True)
    location = LocationMSISerializer(source='village', read_only=True)
    user = UserGetSerializer(read_only=True)
    dob = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)
    last_menstruation_date = serializers.DateTimeField(format="%Y-%m-%d", read_only=True)

    class Meta:
        model = Girl
        # list all the fields since the age property is not picked up by __all__
        fields = (
            'id', 'first_name', 'last_name', 'village', 'village_id', 'location', 'phone_number', 'trimester',
            'next_of_kin_phone_number', 'education_level', 'marital_status',
            'last_menstruation_date', 'dob', 'user', 'odk_instance_id', 'age', 'completed_all_visits',
            'pending_visits', 'missed_visits', 'nationality', 'disabled', 'created_at')


# This is a preventive measure to make tests work. Some depend on Date and others on DateTime
class GirlMSISerializer(serializers.ModelSerializer):
    village = VillageGetSerializer(many=False, read_only=True)
    village_id = serializers.IntegerField(write_only=True)
    location = LocationMSISerializer(source='village', read_only=True)
    user = UserGetSerializer(read_only=True)

    class Meta:
        model = Girl
        # list all the fields since the age property is not picked up by __all__
        fields = (
            'id', 'first_name', 'last_name', 'village', 'village_id', 'location', 'phone_number', 'trimester',
            'next_of_kin_phone_number', 'education_level', 'marital_status',
            'last_menstruation_date', 'dob', 'user', 'odk_instance_id', 'age', 'completed_all_visits',
            'pending_visits', 'missed_visits', 'nationality', 'disabled', 'created_at')


class ObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Observation
        fields = '__all__'


class FamilyPlanningSerializer(serializers.ModelSerializer):
    class Meta:
        model = FamilyPlanning
        fields = '__all__'


class FollowUpGetSerializer(serializers.ModelSerializer):
    girl = GirlSerializer(read_only=True)
    observation = ObservationSerializer(read_only=True)

    class Meta:
        model = FollowUp
        fields = '__all__'


class FollowUpPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUp
        fields = '__all__'


class DeliveryGetSerializer(serializers.ModelSerializer):
    girl = GirlSerializer(read_only=True)
    health_facility = HealthFacilityGetSerializer()
    family_planning = FamilyPlanningSerializer(read_only=True, many=True)

    class Meta:
        model = Delivery
        fields = '__all__'


class DeliveryPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'


class MappingEncounterSerializer(serializers.ModelSerializer):
    girl = GirlSerializer(read_only=True)
    family_planning = FamilyPlanningSerializer(read_only=True, many=True)
    observation = ObservationSerializer(read_only=True)
    user = UserGetSerializer(read_only=True)

    class Meta:
        model = MappingEncounter
        fields = '__all__'


class AppointmentSerializer(serializers.ModelSerializer):
    girl = GirlSerializer(read_only=True)
    user = UserGetSerializer(read_only=True)

    class Meta:
        model = Appointment
        fields = '__all__'


class AppointmentEncounterSerializer(serializers.ModelSerializer):
    observation = ObservationSerializer(read_only=True)
    appointment = AppointmentSerializer(read_only=True)

    class Meta:
        model = AppointmentEncounter
        fields = '__all__'


class CustomTokenSerializer(TokenSerializer):
    """
    Override the djoser(https://djoser.readthedocs.io/en/latest/) token serializer
    Allows us to return user details along side the djoser token
    """
    auth_token = serializers.CharField(source='key')
    user = UserSerializer()

    class Meta:
        model = Token
        fields = (
            'auth_token', 'user'
        )


class SmsModelSerializer(serializers.ModelSerializer):
    recipient = UserGetSerializer(read_only=True)

    class Meta:
        model = SmsModel
        fields = (
            'id', 'recipient', 'sender_id', 'message', 'status', 'created_at')
