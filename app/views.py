import json
from datetime import datetime

from django.utils import timezone
from dry_rest_permissions.generics import DRYPermissions
from rest_framework.generics import ListCreateAPIView, ListAPIView, RetrieveUpdateDestroyAPIView, \
    RetrieveDestroyAPIView, \
    CreateAPIView, UpdateAPIView
from rest_framework.permissions import *

from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Girl, District, County, SubCounty, Parish, Village, \
    HealthFacility, FollowUp, Delivery, MappingEncounter
from app.serializers import UserSerializer, User, UserGetSerializer, GirlSerializer, DistrictGetSerializer, \
    CountyGetSerializer, \
    SubCountyGetSerializer, ParishGetSerializer, VillageGetSerializer, HealthFacilityGetSerializer, \
    FollowUpGetSerializer, FollowUpPostSerializer, DeliveryPostSerializer, DeliveryGetSerializer

import logging

logger = logging.getLogger('testlogger')


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
        print("post request called")
        try:
            json_result = request.data
            print(json_result)
            mapped_girl_object = json_result["GetInTest18"]

        except Exception as e:
            print(e)
            json_result = json.loads(request.data)
            print(json_result)
            mapped_girl_object = json_result["GetInTest18"]

        if mapped_girl_object:
            try:
                print(mapped_girl_object)
                demographic1 = mapped_girl_object["GIRLSDEMOGRAPHIC"][0]
                first_name = demographic1["FirstName"][0]
                last_name = demographic1["LastName"][0]

                year, month, day = [int(x) for x in demographic1["DOB"][0].split("-")]
                dob = datetime(year, month, day)

                demographic2 = mapped_girl_object["GIRLSDEMOGRAPHIC2"][0]
                girls_phone_number = demographic2["GirlsPhoneNumber"][0]
                next_of_kin_number = demographic2["NextOfKinNumber"][0]
                next_of_kin_first_name = demographic2["NextOfKinFirstName"][0]
                next_of_kin_last_name = demographic2["NextOfKinLastName"][0]

                girl_location = mapped_girl_object["GIRLLOCATION"][0]
                district = District.objects.filter(name__icontains=girl_location["district"][0])
                county = County.objects.filter(name__icontains=girl_location["county"][0])
                subcounty = SubCounty.objects.filter(name__icontains=girl_location["subcounty"][0])
                parish = Parish.objects.filter(name__icontains=girl_location["parish"][0])

                village = Village.objects.get(name__icontains=girl_location["village"][0])

                observations3 = mapped_girl_object["observations3"][0]
                marital_status = observations3["marital_status"][0]
                education_level = observations3["education_level"][0]

                year, month, day = [int(x) for x in observations3["MenstruationDate"][0].split("-")]
                last_menstruation_date = timezone.datetime(year, month, day)

                observations1 = mapped_girl_object["observations1"][0]
                # attended_anc_visit = observations1["AttendedANCVisit"][0] == "yes"
                bleeding = observations1["bleeding"][0] == "yes"
                fever = observations1["fever"][0] == "yes"

                observations2 = mapped_girl_object["observations2"][0]
                swollenfeet = observations2["swollenfeet"][0] == "yes"
                blurred_vision = observations2["blurred_vision"][0] == "yes"

                used_contraceptives = mapped_girl_object["UsedContraceptives"][0] == "yes"
                contraceptive_method = mapped_girl_object["ContraceptiveMethod"][0]
                voucher_card = mapped_girl_object["VoucherCard"][0]

                girl = Girl(first_name=first_name, last_name=last_name, village=village,
                            phone_number=girls_phone_number,
                            next_of_kin_first_name=next_of_kin_first_name, next_of_kin_last_name=next_of_kin_last_name,
                            next_of_kin_phone_number=next_of_kin_number, education_level=education_level, dob=dob,
                            marital_status=marital_status, last_menstruation_date=last_menstruation_date)
                girl.save()

                # todo get vht or midwife user object
                user = User.objects.first()

                # todo get next_appointment
                next_appointment = timezone.now() + timezone.timedelta(days=30)

                mapping_encounter = MappingEncounter(girl=girl, user=user, next_appointment=next_appointment,
                                                     no_family_planning_reason="",
                                                     using_family_planning=used_contraceptives, bleeding_heavily=bleeding,
                                                     swollen_feet=swollenfeet, family_planning_type=contraceptive_method,
                                                     fever=fever, blurred_vision=blurred_vision)
                mapping_encounter.save()

                return Response({'result': 'success'}, 200)
            except Exception as e:
                print(e)
                return Response({'result': 'failure'}, 200)
        return Response({'result': 'failure'}, 400)
