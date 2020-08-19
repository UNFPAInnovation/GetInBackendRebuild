import random

from rest_framework.test import APITestCase
from app.models import *
from django.utils.crypto import get_random_string

"""
TESTS GUIDE
assertEqual(actual, expected)
"""


class ParentTest(APITestCase):
    def setUp(self) -> None:
        self.maxDiff = None
        self.region = Region.objects.create(name="Western")
        self.district = District.objects.create(name="BUNDIBUGYO", region=self.region)
        self.county = County.objects.create(name="BWAMBA_COUNTY", district=self.district)
        self.sub_county = SubCounty.objects.create(name="BUBANDI", county=self.county)
        self.parish = Parish.objects.create(name="NJUULE", sub_county=self.sub_county)
        self.village = Village.objects.create(name="BUNDISELYA", parish=self.parish)

        self.region2 = Region.objects.create(name="Northern")
        self.district2 = District.objects.create(name="Arua", region=self.region2)
        self.county2 = County.objects.create(name="Arua", district=self.district2)
        self.sub_county2 = SubCounty.objects.create(name="Dadamu", county=self.county2)
        self.parish2 = Parish.objects.create(name="Yapi", sub_county=self.sub_county2)
        self.village2 = Village.objects.create(name="Abira", parish=self.parish2)

        self.midwife_phone_number = "075687" + str(random.randint(1000, 9999))
        self.midwife = User.objects.create(username="midwife40", first_name="mid", last_name="wife40" + get_random_string(length=4),
                                           phone=self.midwife_phone_number, password=self.midwife_phone_number, gender=GENDER_FEMALE, village=self.village,
                                           district=self.district, role=USER_TYPE_MIDWIFE, email="midwifetest@test.com")
        self.midwife2 = User.objects.create(username="midwife41", first_name="mid",
                                           last_name="wife41" + get_random_string(length=4),
                                           phone="0756677888", password="0756677888",
                                           gender=GENDER_FEMALE, village=self.village,
                                           district=self.district, role=USER_TYPE_MIDWIFE, email="midwifetest2@test.com")
        self.chew_phone_number = "075687" + str(random.randint(1000, 9999))
        self.chew = User.objects.create(username="vhtuservht", first_name="vht", last_name="uservht",
                                        phone=self.chew_phone_number, password=self.chew_phone_number, gender=GENDER_FEMALE,
                                        village=self.village, district=self.district, role=USER_TYPE_CHEW,
                                        midwife=self.midwife, email="chewtest@test.com")
        self.dho = User.objects.create(username="dhodho", first_name="dho", last_name="dho",
                                       phone="0756879444", password="0756879444",
                                       gender=GENDER_FEMALE, is_staff=True,
                                       village=self.village, district=self.district, role=USER_TYPE_DHO,
                                       midwife=self.midwife, email="dhodho@test.com")
        self.user = User.objects.create(is_staff=True, is_superuser=True, role=USER_TYPE_DEVELOPER)
        self.client.force_authenticate(user=self.chew)
        self.current_date = timezone.now()