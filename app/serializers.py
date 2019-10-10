import jwt
from django.db.models import Q
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.fields import EmailField, CharField
from rest_framework.settings import api_settings
from rest_framework_jwt.utils import jwt_payload_handler

from GetInBackendRebuild.settings import SECRET_KEY
from app.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name', 'phone', 'createdAt',)
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
            'first_name', 'last_name', 'username', 'email', 'phone', 'password', 'gender')

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
            'id', 'first_name', 'last_name', 'email', 'gender')


class DHOGetSerializer(UserGetSerializer):
    class Meta:
        model = DHO
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'gender', 'district', 'user_type')


class CHEWGetSerializer(UserGetSerializer):
    class Meta:
        model = CHEW
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'gender', 'sub_county')


class MidwifeGetSerializer(UserGetSerializer):
    class Meta:
        model = Midwife
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'gender', 'health_facility')


class AmbulanceGetSerializer(UserGetSerializer):
    class Meta:
        model = Ambulance
        fields = (
            'id', 'first_name', 'last_name', 'username', 'email', 'gender', 'parish', 'number_place')


class GirlSerializer(serializers.ModelSerializer):
    class Meta:
        model = Girl
        fields = ('id', 'first_name', 'last_name', 'village', 'phone_number', 'trimester',
                  'next_of_kin_name', 'next_of_kin_phone_number', 'education_level', 'marital_status',
                  'last_menstruation_date', 'dob')
