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
        self.region2 = Region.objects.create(name="Northern")
        self.district = District.objects.create(name="BUNDIBUGYO", region=self.region)
        self.district2 = District.objects.create(name="Arua", region=self.region2)
        self.county = County.objects.create(name="BWAMBA_COUNTY", district=self.district)
        self.county2 = County.objects.create(name="Arua", district=self.district2)
        self.sub_county = SubCounty.objects.create(name="BUBANDI", county=self.county)
        self.sub_county2 = SubCounty.objects.create(name="Arivu", county=self.county2)
        self.parish = Parish.objects.create(name="NJUULE", sub_county=self.sub_county)
        self.parish2 = Parish.objects.create(name="Awika", sub_county=self.sub_county2)
        self.village = Village.objects.create(name="BUNDISELYA", parish=self.parish)
        self.village2 = Village.objects.create(name="Etori", parish=self.parish2)

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
        self.midwife = User.objects.create(username="midwife40", first_name="mid", last_name="wife40",
                                           phone="0756878333", gender=GENDER_FEMALE, village=self.village,
                                           district=self.district, role=USER_TYPE_MIDWIFE, email="midwifetest@test.com")
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

    def test_dashboard_users_per_district(self):
        User.objects.create(username="midwife40", first_name="mid", last_name="wife40",
                            phone="0756878333", gender=GENDER_FEMALE, village=self.village,
                            district=self.district, role=USER_TYPE_MIDWIFE, email="midwifetest@test.com")
        User.objects.create(username="chew10", first_name="chew10", last_name="chew10",
                            phone="0756878311", gender=GENDER_FEMALE, village=self.village,
                            district=self.district, role=USER_TYPE_CHEW, email="chew10@test.com")
        User.objects.create(username="chew11", first_name="chew11", last_name="chew11",
                            phone="0756878312", gender=GENDER_FEMALE, village=self.village2,
                            district=self.district2, role=USER_TYPE_CHEW, email="chew11@test.com")
        dho = User.objects.create(username="dho1", first_name="dho1", last_name="dho1",
                            phone="0756878315", gender=GENDER_FEMALE, village=self.village,
                            district=self.district, role=USER_TYPE_DHO, email="dho1@test.com")
        dho2 = User.objects.create(username="dho2", first_name="dho2", last_name="dho2",
                                  phone="0756878316", gender=GENDER_MALE, village=self.village2,
                                  district=self.district2, role=USER_TYPE_DHO, email="dho2@test.com")
        superadmin = User.objects.create(username="manager1", first_name="manager1", last_name="manager1",
                                  phone="0756878317", gender=GENDER_FEMALE, village=self.village,
                                  district=self.district, role=USER_TYPE_MANAGER, email="manager1@test.com")

        url = reverse("users")
        kwargs = {"role": USER_TYPE_CHEW}
        self.client.force_authenticate(user=dho)
        request = self.client.get(url, kwargs)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 1)

        self.client.force_authenticate(user=superadmin)
        request = self.client.get(url, kwargs)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 2)

        kwargs = {"role": USER_TYPE_MIDWIFE}
        self.client.force_authenticate(user=dho2)
        request = self.client.get(url, kwargs)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 0)
