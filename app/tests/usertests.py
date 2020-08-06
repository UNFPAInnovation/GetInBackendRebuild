from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from app.models import *

"""
TESTS GUIDE
assertEqual(actual, expected)
"""


class TestUser(APITestCase):
    def setUp(self) -> None:
        self.region = Region.objects.create(name="Western")
        self.district = District.objects.create(name="BUNDIBUGYO", region=self.region)
        self.county = County.objects.create(name="BWAMBA_COUNTY", district=self.district)
        self.sub_county = SubCounty.objects.create(name="BUBANDI", county=self.county)
        self.parish = Parish.objects.create(name="NJUULE", sub_county=self.sub_county)
        self.village = Village.objects.create(name="BUNDISELYA", parish=self.parish)

    def test_create_midwife_user(self):
        """
        Creates midwife user
        """
        request_data = {
            "first_name": "mid91",
            "last_name": "mid91",
            "username": "mid91",
            "email": "testmid1@mail.com",
            "phone": "0756878441",
            "password": "0756878441",
            "village": self.village.id,
            "district": self.district.id,
            "gender": "female",
            "number_plate": "",
            "role": USER_TYPE_MIDWIFE
        }
        url = reverse("register")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_create_chew_user(self):
        """
        Creates chew user
        """
        self.midwife = User.objects.create(username="midwife40", first_name="mid", last_name="wife40", phone="0756878333", gender=GENDER_FEMALE, village=self.village, district=self.district, role=USER_TYPE_MIDWIFE, email="midwifetest@test.com")
        self.assertEqual(User.objects.filter(username="midwife40").count(), 1)

        request_data = {
            "first_name": "mid91",
            "last_name": "mid91",
            "username": "mid91",
            "email": "testmid1@mail.com",
            "phone": "0756878441",
            "password": "0756878441",
            "village": self.village.id,
            "district": self.district.id,
            "gender": "female",
            "number_plate": "",
            "midwife": self.midwife.id,
            "role": USER_TYPE_CHEW
        }
        url = reverse("register")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)

    def test_create_ambulance_user(self):
        """
        Creates ambulance user
        """
        request_data = {
            "first_name": "amb",
            "last_name": "ulance22",
            "username": "ambulance22",
            "email": "testmid1@mail.com",
            "phone": "0756878445",
            "password": "0756878445",
            "village": self.village.id,
            "district": self.district.id,
            "gender": "female",
            "number_plate": "",
            "role": USER_TYPE_AMBULANCE
        }
        url = reverse("register")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)