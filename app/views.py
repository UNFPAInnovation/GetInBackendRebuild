from datetime import datetime

from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveDestroyAPIView, \
    CreateAPIView, UpdateAPIView
from rest_framework.permissions import *

from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Girl, DHO, Midwife, CHEW, Ambulance, District, County, SubCounty, Parish, Village, HealthFacility
from app.serializers import UserSerializer, User, UserGetSerializer, GirlSerializer, DHOGetSerializer, \
    CHEWGetSerializer, MidwifeGetSerializer, AmbulanceGetSerializer, DistrictGetSerializer, CountyGetSerializer, \
    SubCountyGetSerializer, ParishGetSerializer, VillageGetSerializer, HealthFacilityGetSerializer


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


class DHOView(ListCreateAPIView):
    queryset = DHO.objects.all()
    serializer_class = DHOGetSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class MidwifeView(ListCreateAPIView):
    queryset = Midwife.objects.all()
    serializer_class = MidwifeGetSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class ChewView(ListCreateAPIView):
    queryset = CHEW.objects.all()
    serializer_class = CHEWGetSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class AmbulanceView(ListCreateAPIView):
    queryset = Ambulance.objects.all()
    serializer_class = AmbulanceGetSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class DistrictView(ListCreateAPIView):
    queryset = District.objects.all()
    serializer_class = DistrictGetSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class CountyView(ListCreateAPIView):
    queryset = County.objects.all()
    serializer_class = CountyGetSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class SubCountyView(ListCreateAPIView):
    queryset = SubCounty.objects.all()
    serializer_class = SubCountyGetSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class ParishView(ListCreateAPIView):
    queryset = Parish.objects.all()
    serializer_class = ParishGetSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class VillageView(ListCreateAPIView):
    queryset = Village.objects.all()
    serializer_class = VillageGetSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)


class HealthFacilityView(ListCreateAPIView):
    queryset = HealthFacility.objects.all()
    serializer_class = HealthFacilityGetSerializer
    # permission_classes = (IsAdminUser, IsAuthenticated)
