from datetime import datetime

from dry_rest_permissions.generics import DRYPermissions
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveDestroyAPIView, \
    CreateAPIView, UpdateAPIView
from rest_framework.permissions import *

from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Girl, District, County, SubCounty, Parish, Village, \
    HealthFacility, FollowUp, Delivery
from app.serializers import UserSerializer, User, UserGetSerializer, GirlSerializer, DistrictGetSerializer, CountyGetSerializer, \
    SubCountyGetSerializer, ParishGetSerializer, VillageGetSerializer, HealthFacilityGetSerializer, \
    FollowUpGetSerializer, FollowUpPostSerializer, DeliveryPostSerializer, DeliveryGetSerializer


class UserCreateView(ListCreateAPIView):
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
    permission_classes = [IsAuthenticated, DRYPermissions]
    serializer_class = GirlSerializer
    queryset = Girl


class GirlView(ListCreateAPIView):
    queryset = Girl.objects.all()
    serializer_class = GirlSerializer
    permission_classes = (DRYPermissions, IsAuthenticated)


class GirlDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = Girl.objects.all()
    serializer_class = GirlSerializer
    permission_classes = (DRYPermissions, IsAuthenticated)


# class UserView(APIView):
#     """
#     Returns the system users
#     """
#
#     def get(self, request, format=None, **kwargs):
#         print("get request")
#         dhos = DHO.objects.all()
#         chews = CHEW.objects.all()
#         midwives = Midwife.objects.all()
#         ambulances = Ambulance.objects.all()
#
#         dho_serializer = DHOGetSerializer(dhos, many=True)
#         chew_serializer = CHEWGetSerializer(chews, many=True)
#         midwives_serializer = MidwifeGetSerializer(midwives, many=True)
#         ambulance_serializer = AmbulanceGetSerializer(ambulances, many=True)
#
#         return Response({
#             'dhos': dho_serializer.data,
#             'chews': chew_serializer.data,
#             'midwives': midwives_serializer.data,
#             'ambulances': ambulance_serializer.data,
#         })


class DistrictView(ListCreateAPIView):
    queryset = District.objects.all()
    serializer_class = DistrictGetSerializer
    permission_classes = (IsAdminUser, IsAuthenticated)


class CountyView(ListCreateAPIView):
    queryset = County.objects.all()
    serializer_class = CountyGetSerializer
    permission_classes = (IsAdminUser, IsAuthenticated)


class SubCountyView(ListCreateAPIView):
    queryset = SubCounty.objects.all()
    serializer_class = SubCountyGetSerializer
    permission_classes = (IsAdminUser, IsAuthenticated)


class ParishView(ListCreateAPIView):
    queryset = Parish.objects.all()
    serializer_class = ParishGetSerializer
    permission_classes = (IsAdminUser, IsAuthenticated)


class VillageView(ListCreateAPIView):
    queryset = Village.objects.all()
    serializer_class = VillageGetSerializer
    permission_classes = (IsAdminUser, IsAuthenticated)


class HealthFacilityView(ListCreateAPIView):
    queryset = HealthFacility.objects.all()
    serializer_class = HealthFacilityGetSerializer
    permission_classes = (IsAdminUser, IsAuthenticated)


class FollowUpView(ListCreateAPIView):
    queryset = FollowUp.objects.all()
    permission_classes = (IsAuthenticated, DRYPermissions)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FollowUpPostSerializer
        else:
            return FollowUpGetSerializer


class DeliveriesView(ListCreateAPIView):
    queryset = Delivery.objects.all()
    permission_classes = (IsAuthenticated, DRYPermissions)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DeliveryPostSerializer
        else:
            return DeliveryGetSerializer


class MappingEncounterWebhook(APIView):
    """
    Receives the mapping encounter data and then creates the Girl model and MappingEncounter model

    """

    def post(self, request, *args, **kwargs):
        data = request.data
        print(data)
        return Response({
            'result': 'success'
        })
