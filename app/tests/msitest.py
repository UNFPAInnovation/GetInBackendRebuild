import json
import random

from rest_framework import status
from rest_framework.renderers import JSONRenderer

from app.models import *
from app.serializers import *
from app.tests.parenttest import ParentTest
from django.utils.crypto import get_random_string

from app.webhook import send_data_to_msi_webhook


class TestMSI(ParentTest):
    def test_msi_webhook_json(self):
        """
        Test structure of json sent to msi webhook
        """
        last_name = "MukuluGirlTest" + get_random_string(length=3)
        girl = Girl.objects.create(user=self.chew2, first_name="Ttest", marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3).date(), village=self.village3,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3).date(),
                                   phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL, next_of_kin_phone_number="0756789542")
        request_data = {
            "id": str(girl.id),
            "first_name": "Ttest",
            "last_name": last_name,
            "village": {
                "id": self.village3.id,
                "parish": {
                    "id": self.parish3.id,
                    "sub_county": {
                        "id": self.sub_county3.id,
                        "county": {
                            "id": self.county3.id,
                            "district": {
                                "id": self.district3.id,
                                "name": self.district3.name,
                                "region": self.region2.id,
                            },
                            "name": self.county3.name,
                        },
                        "name": self.sub_county3.name,
                    },
                    "name": self.parish3.name,
                },
                "name": self.village3.name
            },
            "location": {
                "village": {
                    "id": self.village3.id,
                    "name": self.village3.name
                },
                "parish": {
                    "id": self.parish3.id,
                    "name": self.parish3.name
                },
                "sub_county": {
                    "id": self.sub_county3.id,
                    "name": self.sub_county3.name
                },
                "county": {
                    "id": self.county3.id,
                    "name": self.county3.name
                },
                "district": {
                    "id": self.district3.id,
                    "name": self.district3.name
                },
                "region": {
                    "id": self.region2.id,
                    "name": self.region2.name
                }
            },
            "phone_number": "0756789543",
            "trimester": girl.trimester,
            "next_of_kin_phone_number": "0756789542",
            "education_level": PRIMARY_LEVEL,
            "marital_status": "Single",
            "last_menstruation_date": "2020-03-03",
            "dob": "2000-03-03",
            "user": {
                "id": str(self.chew2.id),
                "first_name": self.chew2.first_name,
                "last_name": self.chew2.last_name,
                "username": self.chew2.username,
                "email": self.chew2.email,
                "gender": self.chew2.gender,
                "village": self.chew2.village.id,
                "number_plate": None,
                "role": "chew",
                "phone": self.chew2.phone
            },
            "odk_instance_id": None,
            "age": girl.age,
            "completed_all_visits": False,
            "pending_visits": 30,
            "missed_visits": 0,
            "nationality": "Ugandan",
            "disabled": False,
            "created_at": str(girl.created_at.astimezone().isoformat())
        }

        serializer = GirlMSISerializer(girl)
        expected_data = json.dumps(request_data).strip().replace(': ', ':').replace(', ', ',')
        print(serializer.data)
        actual_data = JSONRenderer().render(serializer.data).decode("utf-8")
        self.assertEqual(actual_data, expected_data)

    def test_msi_webhook_response(self):
        last_name = "MukuluGirlTest2" + get_random_string(length=3)
        girl = Girl.objects.create(user=self.chew, first_name="Ttest2", marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3).date(), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3).date(),
                                   phone_number="0756789" + str(random.randint(100, 999)),
                                   education_level=PRIMARY_LEVEL, next_of_kin_phone_number="0756789" + str(random.randint(100, 999)))
        response = send_data_to_msi_webhook(girl)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['successful'])
