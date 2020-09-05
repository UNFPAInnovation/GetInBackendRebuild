import json

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
        girl = Girl.objects.create(user=self.chew, first_name="Ttest", marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3).date(), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3).date(),
                                   phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL, next_of_kin_phone_number="0756789542")
        request_data = {
            "id": str(girl.id),
            "first_name": "Ttest",
            "last_name": last_name,
            "village": {
                "id": 1,
                "parish": {
                    "id": 1,
                    "sub_county": {
                        "id": 1,
                        "county": {
                            "id": 1,
                            "district": {
                                "id": 1,
                                "name": "BUNDIBUGYO",
                                "region": 1
                            },
                            "name": "BWAMBA_COUNTY"
                        },
                        "name": "BUBANDI"
                    },
                    "name": "NJUULE"
                },
                "name": "BUNDISELYA"
            },
            "location": {
                "village": {
                    "id": 1,
                    "name": "BUNDISELYA"
                },
                "parish": {
                    "id": 1,
                    "name": "NJUULE"
                },
                "sub_county": {
                    "id": 1,
                    "name": "BUBANDI"
                },
                "county": {
                    "id": 1,
                    "name": "BWAMBA_COUNTY"
                },
                "district": {
                    "id": 1,
                    "name": "BUNDIBUGYO"
                },
                "region": {
                    "id": 1,
                    "name": "Western"
                }
            },
            "phone_number": "0756789543",
            "trimester": 2,
            "next_of_kin_phone_number": "0756789542",
            "education_level": PRIMARY_LEVEL,
            "marital_status": "Single",
            "last_menstruation_date": "2020-03-03",
            "dob": "2000-03-03",
            "user": {
                "id": str(self.chew.id),
                "first_name": "vht",
                "last_name": "uservht",
                "username": "vhtuservht",
                "email": "chewtest@test.com",
                "gender": "female",
                "village": 1,
                "number_plate": None,
                "role": "chew",
                "phone": self.chew_phone_number
            },
            "odk_instance_id": None,
            "age": 20,
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
                                   phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL, next_of_kin_phone_number="0756789542")
        response = send_data_to_msi_webhook(girl)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.json()['successful'])
