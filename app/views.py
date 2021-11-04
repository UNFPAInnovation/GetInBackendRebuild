import datetime
import calendar

import pytz
from django.db.models import Q, Sum, Case, When, IntegerField
from django.utils import timezone
from django_filters.rest_framework import DjangoFilterBackend, OrderingFilter
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView, CreateAPIView
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.views import APIView

from GetInBackendRebuild.settings import SHEET_FILES_FOLDER
from app.airtime_dispatcher import AirtimeModule
from app.extractor import extract_excel_org_unit_data, extract_excel_user_data
from app.filters import GirlFilter, FollowUpFilter, MappingEncounterFilter, DeliveryFilter, AppointmentFilter, \
    UserFilter
from app.models import Girl, District, County, SubCounty, Parish, Village, \
    HealthFacility, FollowUp, Delivery, MappingEncounter, Appointment, SmsModel
from app.permissions import IsPostOrIsAuthenticated
from app.serializers import UserSerializer, User, GirlSerializer, DistrictGetSerializer, \
    CountyGetSerializer, SubCountyGetSerializer, ParishGetSerializer, VillageGetSerializer, HealthFacilityGetSerializer, \
    FollowUpGetSerializer, FollowUpPostSerializer, DeliveryPostSerializer, DeliveryGetSerializer, \
    MappingEncounterSerializer, AppointmentSerializer, SmsModelSerializer
from app.sms_handler import send_sms_message

from app.utils.constants import USER_TYPE_MIDWIFE, USER_TYPE_CHEW, USER_TYPE_DHO, GENERAL_MESSAGE
from app.utils.utilities import add_months

# disabled the markdown manually
# https://www.reddit.com/r/django/comments/d5ob15/help_drf_markdown_is_optional_but_my_project/
from rest_framework import compat

compat.md_filter_add_syntax_highlight = lambda md: False


class UserCreateView(ListCreateAPIView):
    """
    Allows creation of user.
    """

    def get_queryset(self):
        user = self.request.user
        if user.role in [USER_TYPE_DHO]:
            return User.objects.filter(district=user.district).order_by('-created_at')
        else:
            return User.objects.all()

    permission_classes = (IsPostOrIsAuthenticated,)
    serializer_class = UserSerializer
    filter_class = UserFilter


class GirlView(ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.role in [USER_TYPE_DHO, USER_TYPE_CHEW, USER_TYPE_MIDWIFE]:
            return Girl.objects.filter(user__district=user.district).order_by('-created_at')
        else:
            return Girl.objects.all()

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
            model = HealthFacility.objects.filter(sub_county__county__district=user.district)
        else:
            model = HealthFacility.objects.all()
        return model

    serializer_class = HealthFacilityGetSerializer
    permission_classes = (IsAuthenticated,)


class FollowUpView(ListCreateAPIView):
    def get_queryset(self):
        user = self.request.user
        if user.role == USER_TYPE_MIDWIFE:
            users = User.objects.filter(midwife=user)
            model = FollowUp.objects.filter(Q(user__in=users) | Q(user=user)).order_by('-created_at')
        elif user.role == USER_TYPE_CHEW:
            model = FollowUp.objects.filter(Q(user=user)).order_by('-created_at')
        elif user.role == USER_TYPE_DHO:
            model = FollowUp.objects.filter(user__district=user.district).order_by('-created_at')
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
        elif user.role == USER_TYPE_CHEW:
            model = Delivery.objects.filter(user=user).order_by('-created_at')
        elif user.role == USER_TYPE_DHO:
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
        return appointments

    permission_classes = (IsAuthenticated, DRYPermissions)
    filter_class = AppointmentFilter
    serializer_class = AppointmentSerializer


class DashboardStatsView(APIView):
    def get(self, request, format=None, **kwargs):
        get_params = dict(zip(request.GET.keys(), request.GET.values()))
        date_format = '%Y-%m-%d'

        created_at_from = datetime.datetime.strptime(get_params['from'], date_format).replace(tzinfo=pytz.utc)
        created_at_to_limit = datetime.datetime.strptime(get_params['to'], date_format).replace(tzinfo=pytz.utc) \
                              + timezone.timedelta(days=1)

        all_months_range_data = []
        first_date_range = True
        subcounty = request.user.village.parish.sub_county
        district = subcounty.county.district
        sub_counties = SubCounty.objects.filter(county__district=district)

        while created_at_from <= created_at_to_limit:
            '''We loop through all months for the data querried.
            we do some mutation on the dates so as to group the data in months '''
            created_at_to = self.generate_date_range(created_at_from, created_at_to_limit, first_date_range)

            all_subcounties = []

            if request.path == '/api/v1/mapping_encounters_stats':
                total_girls_in_all_subcounties = 0
                response = dict()
                response["district"] = district.name
                response["year"] = created_at_from.year
                response["month"] = created_at_from.strftime("%B")

                subvalues = SubCounty.objects.annotate(girls_count=Sum(
                    Case(
                        When(Q(parish__village__girl__created_at__gte=created_at_from) & Q(
                            parish__village__girl__created_at__lte=created_at_to), then=1),
                        output_field=IntegerField())), ).exclude(girls_count=None) \
                    .values('name', 'girls_count').filter(county__district=district)

                for subcounty in subvalues:
                    response["totalNumberOfGirlsMappedFrom" + subcounty['name']] = subcounty['girls_count']
                    total_girls_in_all_subcounties += subcounty['girls_count']

                girls = Girl.objects.aggregate(
                    girls_count_12_15=Sum(
                        Case(When(Q(age__lte=15) & Q(age__lte=15) & Q(user__district=district) &
                                  Q(created_at__gte=created_at_from) & Q(created_at__lte=created_at_to), then=1),
                             output_field=IntegerField())),
                    girls_count_16_19=Sum(
                        Case(When(Q(age__gte=16) & Q(age__lte=19) & Q(user__district=district) &
                                  Q(created_at__gte=created_at_from) & Q(created_at__lte=created_at_to), then=1),
                             output_field=IntegerField())),
                    girls_count_20_24=Sum(
                        Case(When(Q(age__gte=20) & Q(age__lte=24) & Q(user__district=district) &
                                  Q(created_at__gte=created_at_from) & Q(created_at__lte=created_at_to), then=1),
                             output_field=IntegerField()))
                )

                response["mappedGirlsInAgeGroup12_15"] = girls['girls_count_12_15']
                response["mappedGirlsInAgeGroup16_19"] = girls['girls_count_16_19']
                response["mappedGirlsInAgeGroup20_24"] = girls['girls_count_20_24']
                response["count"] = total_girls_in_all_subcounties
                response["subcounties"] = [subcounty.name for subcounty in sub_counties]

                all_months_range_data.append(response)
            elif request.path == '/api/v1/deliveries_stats':
                response = dict()
                deliveries = Delivery.objects.filter(
                    Q(girl__created_at__gte=created_at_from) & Q(girl__created_at__lte=created_at_to))

                all_subcounties += [delivery.girl.village.parish.sub_county for delivery in deliveries
                                    if delivery.user.district == district]

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
            created_at_from = created_at_to + timezone.timedelta(days=1)
            first_date_range = False

        return Response(all_months_range_data, 200)

    def generate_date_range(self, created_at_from, created_at_to_limit, first_date_range):
        if first_date_range:
            return created_at_from.replace(day=calendar.monthrange(created_at_from.year,
                                                                   created_at_from.month)[1]) \
                .replace(tzinfo=pytz.utc)
        else:
            return add_months(created_at_from, 1).replace(tzinfo=pytz.utc)


class SmsView(ListCreateAPIView):
    permission_classes = (IsAdminUser, IsAuthenticated)
    serializer_class = SmsModelSerializer

    def get_queryset(self):
        user = self.request.user
        if user.role == USER_TYPE_DHO:
            model = SmsModel.objects.filter(sender_id=user.id).order_by('-created_at')
        else:
            model = SmsModel.objects.all().order_by('-created_at')
        return model

    def post(self, request, *args, **kwargs):
        try:
            receiver_ids = request.data.get('receiver_ids')
            phone_numbers = ["+256" + User.objects.get(id=receiver_id).phone[1:] for receiver_id in receiver_ids]
            send_sms_message(request.data.get('message'), phone_numbers, GENERAL_MESSAGE)
            return Response({'result': 'success'})
        except Exception as e:
            return Response({'result': 'failure'})


class ExtractView(APIView):
    def get(self, request, format=None, **kwargs):
        location = (SHEET_FILES_FOLDER + "bundibugyo_org_units.xlsx")
        # extract_excel_data(location_arua)

        # location = (SHEET_FILES_FOLDER + "Kampala Org Units DB.xlsx")
        # extract_excel_org_unit_data(location)
        #
        # arua_users = (SHEET_FILES_FOLDER + "GetInAruaUsers.xlsx")
        # extract_excel_user_data(arua_users)

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
