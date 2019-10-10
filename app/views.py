from datetime import datetime

from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveDestroyAPIView, \
    CreateAPIView, UpdateAPIView
from rest_framework.permissions import *

from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Girl, DHO, Midwife, CHEW, Ambulance
from app.serializers import UserSerializer, User, UserGetSerializer, GirlSerializer, DHOGetSerializer, \
    CHEWGetSerializer, MidwifeGetSerializer, AmbulanceGetSerializer


class UserCreateView(CreateAPIView):
    """
    Allows creation of user.
    """
    permission_classes = [AllowAny]
    serializer_class = UserSerializer
    queryset = User


class GirlCreateView(CreateAPIView):
    """
    Allows creation of user.
    """
    permission_classes = [AllowAny]
    serializer_class = GirlSerializer
    queryset = Girl


class GirlView(ListCreateAPIView):
    queryset = Girl.objects.all()
    serializer_class = GirlSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class GirlDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = Girl.objects.all()
    serializer_class = GirlSerializer
    # permission_classes = (IsAdminUser,)


class UserView(APIView):
    """
    Returns the system users
    """

    def get(self, request, format=None, **kwargs):
        print("get request")
        dhos = DHO.objects.all()
        chews = CHEW.objects.all()
        midwives = Midwife.objects.all()
        ambulances = Ambulance.objects.all()

        dho_serializer = DHOGetSerializer(dhos, many=True)
        chew_serializer = CHEWGetSerializer(chews, many=True)
        midwives_serializer = MidwifeGetSerializer(midwives, many=True)
        ambulance_serializer = AmbulanceGetSerializer(ambulances, many=True)

        return Response({
            'dhos': dho_serializer.data,
            'chews': chew_serializer.data,
            'midwives': midwives_serializer.data,
            'ambulances': ambulance_serializer.data,
        })
