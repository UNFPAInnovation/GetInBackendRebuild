import datetime
import calendar

import pytz
from django.db.models import Q
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.views import APIView

from app import sms_handler
from app.airtime_dispatcher import AirtimeModule
from app.extractor import extract_excel_data, extract_excel_user_data_from_sheet
from app.filters import GirlFilter, FollowUpFilter, MappingEncounterFilter, DeliveryFilter, AppointmentFilter, \
    UserFilter
from app.models import Girl, District, County, SubCounty, Parish, Village, \
    HealthFacility, FollowUp, Delivery, MappingEncounter, AppointmentEncounter, Appointment, SmsModel
from app.permissions import IsPostOrIsAuthenticated
from app.serializers import UserSerializer, User, GirlSerializer, DistrictGetSerializer, \
    CountyGetSerializer, SubCountyGetSerializer, ParishGetSerializer, VillageGetSerializer, HealthFacilityGetSerializer, \
    FollowUpGetSerializer, FollowUpPostSerializer, DeliveryPostSerializer, DeliveryGetSerializer, \
    MappingEncounterSerializer, AppointmentEncounterSerializer, AppointmentSerializer, SmsModelSerializer

from app.utils.constants import USER_TYPE_MIDWIFE, USER_TYPE_CHEW, USER_TYPE_DHO
from app.utils.utilities import add_months

# disabled the markdown manually
# https://www.reddit.com/r/django/comments/d5ob15/help_drf_markdown_is_optional_but_my_project/
from rest_framework import compat
compat.md_filter_add_syntax_highlight = lambda md: False

class UserCreateView(ListCreateAPIView):
    """
    Allows creation of user.
    """
    permission_classes = (IsPostOrIsAuthenticated,)
    serializer_class = UserSerializer
    queryset = User.objects.all()
    filter_class = UserFilter


class GirlCreateView(CreateAPIView):
    """
    Allows creation of user.
    """
    permission_classes = [IsAuthenticated, DRYPermissions]
    serializer_class = GirlSerializer
    queryset = Girl.objects.all()


class GirlView(ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.role == USER_TYPE_MIDWIFE:
            users = User.objects.filter(midwife=user)
            model = Girl.objects.filter(Q(user__in=users) | Q(user=user)).order_by('-created_at')
        elif user.role in [USER_TYPE_CHEW]:
            model = Girl.objects.filter(user=user).order_by('-created_at')
        elif user.role in [USER_TYPE_DHO]:
            model = Girl.objects.filter(user__district=user.district).order_by('-created_at')
        else:
            model = Girl.objects.all()
        return model

    serializer_class = GirlSerializer
    permission_classes = (DRYPermissions, IsAuthenticated)
    filter_class = GirlFilter


class MappingEncounterView(ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.role == USER_TYPE_MIDWIFE:
            users = User.objects.filter(midwife=user)
            model = MappingEncounter.objects.filter(Q(user__in=users) | Q(user=user)).order_by('-created_at')
        elif user.role in [USER_TYPE_CHEW]:
            model = MappingEncounter.objects.filter(user=user).order_by('-created_at')
        elif user.role in [USER_TYPE_DHO]:
            model = MappingEncounter.objects.filter(user__district=user.district).order_by('-created_at')
        else:
            model = MappingEncounter.objects.all().order_by('-created_at')
        return model

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
    def get_queryset(self):
        user = self.request.user
        if user.role in [USER_TYPE_DHO, USER_TYPE_CHEW, USER_TYPE_MIDWIFE]:
            model = HealthFacility.objects.filter(user__district=user.district)
        else:
            model = HealthFacility.objects.all()
        return model

    queryset = HealthFacility.objects.all()
    serializer_class = HealthFacilityGetSerializer
    permission_classes = (IsAdminUser, IsAuthenticated)


class FollowUpView(ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.role == USER_TYPE_MIDWIFE:
            users = User.objects.filter(midwife=user)
            model = FollowUp.objects.filter(Q(user__in=users) | Q(user=user)).order_by('-created_at')
        elif user.role in [USER_TYPE_CHEW, USER_TYPE_DHO]:
            model = FollowUp.objects.filter(
                girl__village__parish_id=user.village.parish_id).order_by('-created_at')
        else:
            model = FollowUp.objects.all().order_by('-created_at')
        return model

    permission_classes = (IsAuthenticated, DRYPermissions)
    filter_class = FollowUpFilter

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FollowUpPostSerializer
        else:
            return FollowUpGetSerializer


class DeliveriesView(ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.role == USER_TYPE_MIDWIFE:
            users = User.objects.filter(midwife=user)
            model = Delivery.objects.filter(Q(user_id__in=[user.id for user in users]) | Q(user__id=user.id)).order_by(
                '-created_at')
        elif user.role in [USER_TYPE_CHEW]:
            model = Delivery.objects.filter(user=user).order_by('-created_at')
        elif user.role in [USER_TYPE_DHO]:
            model = Delivery.objects.filter(user__district=user.district).order_by('-created_at')
        else:
            model = Delivery.objects.all().order_by('-created_at')
        return model

    permission_classes = (IsAuthenticated, DRYPermissions)
    filter_class = DeliveryFilter

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return DeliveryPostSerializer
        else:
            return DeliveryGetSerializer


class AppointmentEncounterView(ListCreateAPIView):
    def get_queryset(self):
        # todo reactivate after matching midwife and vht
        # user = self.request.user
        # if user.role == USER_TYPE_MIDWIFE:
        #     users = User.objects.filter(midwife=user)
        #     model = AppointmentEncounter.objects.filter(
        #         Q(user_id__in=[user.id for user in users]) | Q(user__id=user.id)).order_by('-created_at')
        # elif user.role in [USER_TYPE_CHEW]:
        #     model = AppointmentEncounter.objects.filter(user=user).order_by('-created_at')
        # elif user.role in [USER_TYPE_DHO]:
        #     model = AppointmentEncounter.objects.filter(user__district=user.district).order_by('-created_at')
        # else:
        #     model = AppointmentEncounter.objects.all().order_by('-created_at')
        model = AppointmentEncounter.objects.all().order_by('-created_at')
        return model

    queryset = AppointmentEncounter.objects.all()
    permission_classes = (IsAuthenticated, DRYPermissions)
    filter_class = DeliveryFilter
    serializer_class = AppointmentEncounterSerializer


class AppointmentView(ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.role == USER_TYPE_MIDWIFE:
            # return all appointment from CHEWS attached to the midwife or
            # any appointment created by the midwife herself
            users = User.objects.filter(midwife=user)
            appointments = Appointment.objects.filter(
                Q(user_id__in=[user.id for user in users]) | Q(user__id=user.id)).order_by('-created_at')
        elif user.role in [USER_TYPE_CHEW]:
            # return appointments created by CHEW
            appointments = Appointment.objects.filter(Q(user=user) | Q(girl__user=user)).order_by('-created_at')
        elif user.role in [USER_TYPE_DHO]:
            # return all appointments in the DHO district
            appointments = Appointment.objects.filter(user__district=user.district).order_by('-created_at')
        else:
            # return everything for super users and developers
            appointments = Appointment.objects.all().order_by('-created_at')
        # appointments = Appointment.objects.all().order_by('-created_at')
        return appointments

    queryset = Appointment.objects.all()
    permission_classes = (IsAuthenticated, DRYPermissions)
    filter_class = AppointmentFilter
    serializer_class = AppointmentSerializer


class DashboardStatsView(APIView):
    ''' View that handles dashboard data'''

    def get(self, request, format=None, **kwargs):
        ''' Get date params from request '''
        get_params = dict(zip(request.GET.keys(), request.GET.values()))
        created_at_from_param = get_params['from']
        created_at_to_param = get_params['to']

        ''' Extract year, month and day from requests '''
        year_from, month_from, day_from = [int(x) for x in created_at_from_param.split("-")]
        year_to, month_to, day_to = [int(x) for x in created_at_to_param.split("-")]

        ''' So we can manipulate the date object, we convert it here '''
        created_at_from = timezone.datetime(year_from, month_from, day_from).replace(tzinfo=pytz.utc)
        created_at_to_limit = timezone.datetime(year_to, month_to, day_to).replace(tzinfo=pytz.utc)

        # Set number of months we are going to poll data for. We add + 1 to include the current month
        number_of_months = (month_to - month_from) + 1

        all_months_range_data = []

        subcounty = request.user.village.parish.sub_county
        district = subcounty.county.district
        sub_counties = SubCounty.objects.filter(county__district=district)

        while created_at_from <= created_at_to_limit:
            '''We loop through all months for the data querried.
            we do some ugly mutation on the dates so as to group the data in months '''
            created_at_to = add_months(created_at_from, 1).replace(tzinfo=pytz.utc)

            print("--------------------------------------------------------------------------------------------")
            print("Month is " + created_at_from.strftime("%B"))
            print("created_at_from is: " + str(created_at_from) + " and created_at_to is: " + str(created_at_to))
            all_subcounties = []

            if request.path == '/api/v1/mapping_encounters_stats':
                total_girls_in_all_subcounties = 0
                response = dict()
                response["district"] = district.name
                response["year"] = created_at_from.year
                response["month"] = created_at_from.strftime("%B")

                for subcounty in sub_counties:
                    total_girls_in_subcounty = Girl.objects.filter(Q(village__parish__sub_county=subcounty) &
                                                Q(created_at__gte=created_at_from) & Q(created_at__lte=created_at_to)).count()
                    response["totalNumberOfGirlsMappedFrom" + subcounty.name] = total_girls_in_subcounty
                    print('total girls in subcounty ' + str(total_girls_in_subcounty))
                    total_girls_in_all_subcounties += total_girls_in_subcounty

                print('total girls in all subcounties ' + str(total_girls_in_all_subcounties))

                girls = Girl.objects.filter(Q(age__gte=12) & Q(age__lte=15) & Q(user__district=district) &
                                            Q(created_at__gte=created_at_from) & Q(created_at__lte=created_at_to))

                response["mappedGirlsInAgeGroup12_15"] = girls.count()

                girls = Girl.objects.filter(Q(age__gte=16) & Q(age__lte=19) & Q(user__district=district) &
                                            Q(created_at__gte=created_at_from) & Q(created_at__lte=created_at_to))
                response["mappedGirlsInAgeGroup16_19"] = girls.count()

                girls = Girl.objects.filter(Q(age__gte=20) & Q(age__lte=24) & Q(user__district=district) &
                                            Q(created_at__gte=created_at_from) & Q(created_at__lte=created_at_to))
                response["mappedGirlsInAgeGroup20_24"] = girls.count()

                response["count"] = total_girls_in_all_subcounties
                response["subcounties"] = [subcounty.name for subcounty in sub_counties]

                all_months_range_data.append(response)
            elif request.path == '/api/v1/deliveries_stats':
                """
                Provides statistical data for deliveries statistics
                Client query params
                dashboard_stats?from=2019-10-01&to=2019-11-05

                Server response
                {
                count: 0,
                district: "Arua",
                month: "November",
                year: "2019",
                subcounties: ["Subcounty1", "Subcounty2", "etc"],
                deliveriesFromSubcounty1: 3,
                deliveriesFromSubcounty2: 4,
                etc: 10
                }
                """

                deliveries = Delivery.objects.filter(
                    Q(girl__created_at__gte=created_at_from) & Q(girl__created_at__lte=created_at_to))

                all_subcounties += [delivery.girl.village.parish.sub_county for delivery in deliveries
                                    if delivery.girl.village.parish.sub_county.county.district == district]

                # remove duplicate subcounties
                all_subcounties = list(set(all_subcounties))

                response["subcounties"] = [subcounty.name for subcounty in all_subcounties]

                all_deliveries_total = 0

                for subcounty in all_subcounties:
                    delivery_total = Delivery.objects.filter(
                        girl__village__parish_id__in=[parish.id for parish in subcounty.parish_set.all()]).count()
                    response["deliveriesFromSubcounty" + subcounty.name] = delivery_total
                    all_deliveries_total += delivery_total

                response["count"] = all_deliveries_total

                all_months_range_data.append(response)
            else:
                print('-----Followups stats instead ----------')

            created_at_from = add_months(created_at_from, 1).replace(tzinfo=pytz.utc)
            print('end looping ... ' + str(created_at_from))

        return Response(all_months_range_data, 200)


class DeliveriesStatsView(APIView):
    """
    Provides statistical data for deliveries statistics
    Client query params
    dashboard_stats?from=2019-10-01&to=2019-11-05

    Server response
    {
      count: 0,
      district: "Arua",
      month: "November",
      year: "2019",
      subcounties: ["Subcounty1", "Subcounty2", "etc"],
      deliveriesFromSubcounty1: 3,
      deliveriesFromSubcounty2: 4,
      etc: 10
    }
    """

    def get(self, request, format=None, **kwargs):
        print("get request")

        get_params = dict(zip(request.GET.keys(), request.GET.values()))

        created_at_from_param = get_params['from']
        created_at_to_param = get_params['to']

        year, month, day = [int(x) for x in created_at_from_param.split("-")]
        created_at_from = timezone.datetime(year, month, day)

        year, month, day = [int(x) for x in created_at_to_param.split("-")]
        created_at_to = timezone.datetime(year, month, day)
        print(created_at_from)

        response = dict()
        subcounty = request.user.village.parish.sub_county
        district = subcounty.county.district

        response["district"] = district.name
        response["year"] = created_at_from.year
        response["month"] = created_at_from.strftime("%B")

        all_subcounties = []

        deliveries = Delivery.objects.filter(
            Q(girl__created_at__gte=created_at_from) & Q(girl__created_at__lte=created_at_to))

        all_subcounties += [delivery.girl.village.parish.sub_county for delivery in deliveries
                            if delivery.girl.village.parish.sub_county.county.district == district]

        # remove duplicate subcounties
        all_subcounties = list(set(all_subcounties))

        response["subcounties"] = [subcounty.name for subcounty in all_subcounties]

        all_deliveries_total = 0

        for subcounty in all_subcounties:
            delivery_total = Delivery.objects.filter(
                girl__village__parish_id__in=[parish.id for parish in subcounty.parish_set.all()]).count()
            response["deliveriesFromSubcounty" + subcounty.name] = delivery_total
            all_deliveries_total += delivery_total

        response["count"] = all_deliveries_total
        return Response({"results": response}, 200)


class SmsView(ListCreateAPIView):
    permission_classes = (DRYPermissions, IsAuthenticated)
    serializer_class = SmsModelSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == USER_TYPE_DHO:
            model = SmsModel.objects.filter(sender_id=user.id).order_by('-created_at')
        else:
            model = SmsModel.objects.all().order_by('-created_at')
        return model

    def post(self, request, *args, **kwargs):
        message = request.data.get('message')
        print(message)

        try:
            sender = request.user
        except Exception as e:
            print(e)
            # use the developer account as the sender incase the user is None
            sender = User.objects.get(username__icontains="admin")

        receiver_ids = request.data.get('receiver_ids')
        return sms_handler.send_sms(message, sender, receiver_ids)


class ExtractView(APIView):
    def get(self, request, format=None, **kwargs):
        # location = ("/home/codephillip/PycharmProjects/GetInBackendRebuild/bundibugyo_org_units.xlsx")
        location = ("bundibugyo_org_units.xlsx")
        # extract_excel_data(location_arua)

        location = ("/home/codephillip/PycharmProjects/GetInBackendRebuild/Kampala Org Units DB.xlsx")
        extract_excel_data(location)

        # arua_users = ("/home/codephillip/PycharmProjects/GetInBackendRebuild/GetInAruaUsers.xlsx")
        # extract_excel_user_data_from_sheet(arua_users)

        return Response({"result": "success"})


class AirtimeDispatchView(APIView):
    """
    Sends airtime to provided phone numbers
    Json body(example)
    {numbers": ["+25675XXXXXXX", "+25678XXXXXXX"], "amount": 500}
    """
    def post(self, request, format=None):
        airtime_module = AirtimeModule()
        airtime_module.send_airtime(request.data["numbers"], request.data["amount"])
        return Response({"result": "success"})