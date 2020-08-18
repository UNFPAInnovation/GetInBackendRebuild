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
        self.midwife_phone_number = "075687" + str(random.randint(1000, 9999))
        self.midwife = User.objects.create(username="midwife40", first_name="mid", last_name="wife40" + get_random_string(length=4),
                                           phone=self.midwife_phone_number, password=self.midwife_phone_number, gender=GENDER_FEMALE, village=self.village,
                                           district=self.district, role=USER_TYPE_MIDWIFE, email="midwifetest@test.com")
        self.chew_phone_number = "075687" + str(random.randint(1000, 9999))
        self.chew = User.objects.create(username="vhtuservht", first_name="vht", last_name="uservht",
                                        phone=self.chew_phone_number, password=self.chew_phone_number, gender=GENDER_FEMALE,
                                        village=self.village, district=self.district, role=USER_TYPE_CHEW,
                                        midwife=self.midwife, email="chewtest@test.com")
        self.user = User.objects.create(is_staff=True, is_superuser=True)
        self.client.force_authenticate(user=self.chew)
        self.current_date = timezone.now()