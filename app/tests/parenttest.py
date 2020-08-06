from rest_framework.test import APITestCase
from app.models import *
from django.utils.crypto import get_random_string

"""
TESTS GUIDE
assertEqual(actual, expected)
"""


class ParentTest(APITestCase):
    def setUp(self) -> None:
        self.region = Region.objects.create(name="Western")
        self.district = District.objects.create(name="BUNDIBUGYO", region=self.region)
        self.county = County.objects.create(name="BWAMBA_COUNTY", district=self.district)
        self.sub_county = SubCounty.objects.create(name="BUBANDI", county=self.county)
        self.parish = Parish.objects.create(name="NJUULE", sub_county=self.sub_county)
        self.village = Village.objects.create(name="BUNDISELYA", parish=self.parish)
        self.midwife = User.objects.create(username="midwife40", first_name="mid", last_name="wife40" + get_random_string(length=4),
                                           phone="0756878333", password="075687834", gender=GENDER_FEMALE, village=self.village,
                                           district=self.district, role=USER_TYPE_MIDWIFE, email="midwifetest@test.com")
        self.chew = User.objects.create(username="vhtuser", first_name="vht", last_name="user" + get_random_string(length=4),
                                        phone="075687834", password="075687834", gender=GENDER_FEMALE,
                                        village=self.village, district=self.district, role=USER_TYPE_MIDWIFE,
                                        midwife=self.midwife, email="midwifetest@test.com")