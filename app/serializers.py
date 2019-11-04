import jwt
from django.contrib.auth.models import Permission
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework_jwt.utils import jwt_payload_handler

from GetInBackendRebuild.settings import SECRET_KEY
from app.models import User, District, County, SubCounty, Parish, Village, Girl, HealthFacility, FollowUp, Delivery, \
    MappingEncounter


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'email', 'phone', 'password', 'gender', 'village', 'number_plate',
            'role', 'created_at', 'user_permissions')
        # extra_kwargs = {"password": {"write_only": True}}

    def validate_phone(self, value):
        # user can only register one phone number
        user = User.objects.filter(phone=value)
        if user.exists():
            raise ValidationError("This user has already registered with the phone number")
        return value

    def validate(self, data):
        return data

    def create(self, validated_data):
        user = User(
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name'],
            # username is a combination of first and last name
            username=validated_data['first_name'] + validated_data['last_name'],
            email=validated_data['email'],
            phone=validated_data['phone'],
        )
        user.set_password(validated_data['phone'])
        user.save()
        return user


def create_token(user=None):
    payload = jwt_payload_handler(user)
    token = jwt.encode(payload, SECRET_KEY)
    return token.decode('unicode_escape')


class UserPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'first_name', 'last_name', 'username', 'email', 'phone', 'password', 'gender', 'village', 'number_plate',
            'role')

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
            'id', 'first_name', 'last_name', 'email', 'gender', 'village', 'number_plate', 'role', 'phone')


class DistrictGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = District
        fields = (
            'id', 'name')


class CountyGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = County
        fields = (
            'id', 'district', 'name')


class SubCountyGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = SubCounty
        fields = (
            'id', 'county', 'name')


class ParishGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Parish
        fields = (
            'id', 'sub_county', 'name')


class VillageGetSerializer(serializers.ModelSerializer):
    parish = ParishGetSerializer(many=False, read_only=True)
    parish_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Village
        fields = '__all__'


class HealthFacilityGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = HealthFacility
        fields = (
            'id', 'parish', 'name')


class GirlSerializer(serializers.ModelSerializer):
    village = VillageGetSerializer(many=False, read_only=True)
    village_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Girl
        # list all the fields since the age property is not picked up by __all__
        fields = ('id', 'first_name', 'last_name', 'village', 'village_id','phone_number', 'trimester', 'next_of_kin_last_name',
                  'next_of_kin_first_name', 'next_of_kin_phone_number', 'education_level', 'marital_status',
                  'last_menstruation_date', 'dob', 'user', 'odk_instance_id','age', 'created_at')


class FollowUpGetSerializer(serializers.ModelSerializer):
    girl = GirlSerializer()
    user = UserGetSerializer()

    class Meta:
        model = FollowUp
        fields = '__all__'


class FollowUpPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = FollowUp
        fields = '__all__'


class DeliveryGetSerializer(serializers.ModelSerializer):
    girl = GirlSerializer()
    user = UserGetSerializer()
    health_facility = HealthFacilityGetSerializer()

    class Meta:
        model = Delivery
        fields = '__all__'


class DeliveryPostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Delivery
        fields = '__all__'


class MappingEncounterSerializer(serializers.ModelSerializer):
    girl = GirlSerializer()
    user = UserGetSerializer()

    class Meta:
        model = MappingEncounter
        fields = '__all__'
