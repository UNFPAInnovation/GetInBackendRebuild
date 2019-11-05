from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.views import APIView

from app.filters import GirlFilter, FollowUpFilter, MappingEncounterFilter, DeliveryFilter, AppointmentFilter
from app.models import Girl, District, County, SubCounty, Parish, Village, \
    HealthFacility, FollowUp, Delivery, MappingEncounter, AppointmentEncounter, Appointment
from app.permissions import IsPostOrIsAuthenticated
from app.serializers import UserSerializer, User, GirlSerializer, DistrictGetSerializer, \
    CountyGetSerializer, SubCountyGetSerializer, ParishGetSerializer, VillageGetSerializer, HealthFacilityGetSerializer, \
    FollowUpGetSerializer, FollowUpPostSerializer, DeliveryPostSerializer, DeliveryGetSerializer, \
    MappingEncounterSerializer, AppointmentEncounterSerializer, AppointmentSerializer

import logging

logger = logging.getLogger('testlogger')


class UserCreateView(ListCreateAPIView):
    """
    Allows creation of user.
    """
    permission_classes = (IsPostOrIsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()


class GirlCreateView(CreateAPIView):
    """
    Allows creation of user.
    """
    permission_classes = [IsAuthenticated, DRYPermissions]
    serializer_class = GirlSerializer
    queryset = Girl.objects.all()


class GirlView(ListCreateAPIView):
    queryset = Girl.objects.all()
    serializer_class = GirlSerializer
    permission_classes = (DRYPermissions, IsAuthenticated)
    filter_class = GirlFilter


class MappingEncounterView(ListCreateAPIView):
    queryset = MappingEncounter.objects.all()
    serializer_class = MappingEncounterSerializer
    permission_classes = (DRYPermissions, IsAuthenticated)
    filter_class = MappingEncounterFilter


class GirlDetailsView(RetrieveUpdateDestroyAPIView):
    queryset = Girl.objects.all()
    serializer_class = GirlSerializer
    permission_classes = (DRYPermissions, IsAuthenticated)


class DistrictView(ListCreateAPIView):
    queryset = District.objects.all()
    serializer_class = DistrictGetSerializer
    permission_classes = (IsAdminUser, IsAuthenticated)
    filter_backends = (DjangoFilterBackend,)


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
    filter_class = FollowUpFilter

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FollowUpPostSerializer
        else:
            return FollowUpGetSerializer


class DeliveriesView(ListCreateAPIView):
    queryset = Delivery.objects.all()
    permission_classes = (IsAuthenticated, DRYPermissions)
    filter_class = DeliveryFilter

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DeliveryPostSerializer
        else:
            return DeliveryGetSerializer


class AppointmentEncounterView(ListCreateAPIView):
    queryset = AppointmentEncounter.objects.all()
    permission_classes = (IsAuthenticated, DRYPermissions)
    filter_class = DeliveryFilter
    serializer_class = AppointmentEncounterSerializer


class AppointmentView(ListCreateAPIView):
    queryset = Appointment.objects.all()
    permission_classes = (IsAuthenticated, DRYPermissions)
    filter_class = AppointmentFilter
    serializer_class = AppointmentSerializer


class DashboardStatsView(APIView):
    """
    {
  count: 0,
  district: "Arua",
  month: "November",
  year: "2019",
  mappedGirlsInAgeGroup12_15: 0,
  mappedGirlsInAgeGroup16_19: 10,
  mappedGirlsInAgeGroup19_24: 3,
  subcounties: ["Subcounty1", "Subcounty2", "etc"],
  totalNumberOfGirlsMappedFromSubcounty1: 3,
  totalNumberOfGirlsMappedFromSubcounty2: 4,
  etc: 10
}
    """

    def get(self, request, format=None, **kwargs):
        print("get request")

        get_params = dict(zip(request.GET.keys(), request.GET.values()))

        created_at_param = get_params['created_at']
        print(created_at_param)
        print(type(created_at_param))
        year, month, day = created_at_param.split("-")
        created_at = timezone.datetime(int(year), int(month), int(day))
        print(created_at)

        response = dict()
        district = request.user.village.parish.sub_county.county.district
        response["district"] = district.name
        response["year"] = created_at.year
        response["month"] = created_at.month

        current_date = timezone.now()

        date_12_years_ago = timezone.datetime(current_date.year - 12, current_date.month, current_date.day)
        date_15_years_ago = timezone.datetime(current_date.year - 15, current_date.month, current_date.day)
        girls_count = Girl.objects.filter(Q(dob__lte=date_12_years_ago) & Q(dob__gte=date_15_years_ago) &
                                          Q(created_at__gte=created_at)).count()
        response["mappedGirlsInAgeGroup12_15"] = girls_count

        date_16_years_ago = timezone.datetime(current_date.year - 16, current_date.month, current_date.day)
        date_19_years_ago = timezone.datetime(current_date.year - 19, current_date.month, current_date.day)
        girls_count = Girl.objects.filter(Q(dob__lte=date_16_years_ago) & Q(dob__gte=date_19_years_ago) &
                                          Q(created_at__gte=created_at)).count()
        response["mappedGirlsInAgeGroup16_19"] = girls_count

        date_17_years_ago = timezone.datetime(current_date.year - 17, current_date.month, current_date.day)
        date_24_years_ago = timezone.datetime(current_date.year - 24, current_date.month, current_date.day)
        girls_count = Girl.objects.filter(Q(dob__lte=date_17_years_ago) & Q(dob__gte=date_24_years_ago) &
                                          Q(created_at__gte=created_at)).count()
        response["mappedGirlsInAgeGroup17_24"] = girls_count


        counties = district.county_set.all()

        all_subcounties = []
        for county in counties:
            all_subcounties += county.subcounty_set.all()

        response["subcounties"] = [subcounty.name for subcounty in all_subcounties]

        for subcounty in all_subcounties:
            total_girls_in_subcounty = Girl.objects.filter(village__parish__sub_county=subcounty).count()
            response["totalNumberOfGirlsMappedFrom" + subcounty.name] = total_girls_in_subcounty

        return Response({"results": response}, 200)
