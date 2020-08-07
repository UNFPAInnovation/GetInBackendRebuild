from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest
from django.utils.crypto import get_random_string


class TestDelivery(ParentTest):
    def test_chew_captures_delivery(self):
        """
        Test chew capture delivery
        """
        last_name = get_random_string(length=7)
        girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3), phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL)
        request_data = {
            "GetINPostnatalForm6_chew": {
                "$": {
                    "id": "GetINPostnatalForm6_chew",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
                },
                "delivery_followup_group": [
                    {
                        "mother_delivery_outcomes": [
                            "mother_alive"
                        ],
                        "baby_delivery_outcomes": [
                            "baby_alive"
                        ],
                        "baby_birth_date": [
                            "2020-08-06"
                        ],
                        "birth_place": [
                            "Home"
                        ],
                        "action_taken": [
                            "Others"
                        ],
                        "other_action_taken": [
                            "I dont know"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:9a3f09ee-e80f-4d5c-b94e-85ee0f51a96b"
                        ]
                    }
                ]
            },
            "form_meta_data": {"GIRL_ID": girl.id, "USER_ID": self.chew.id}
        }

        url = reverse("mapping_encounter_webhook")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        delivery = Delivery.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(delivery.count(), 1)

    def test_midwife_captures_delivery(self):
        """
        Test midwife capture delivery and offers family planning
        """
        last_name = get_random_string(length=7)
        girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3), phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL)
        request_data = {
            "GetINPostnatalForm6_midwife": {
                "$": {
                    "id": "GetINPostnatalForm6_midwife",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms"
                },
                "delivery_followup_group": [
                    {
                        "mother_delivery_outcomes": [
                            "mother_alive"
                        ],
                        "baby_delivery_outcomes": [
                            "baby_alive"
                        ],
                        "baby_birth_date": [
                            "2020-08-07"
                        ],
                        "birth_place": [
                            "HealthFacility"
                        ],
                        "action_taken": [
                            "offered_family_planning"
                        ]
                    }
                ],
                "family_planning_group": [
                    {
                        "ContraceptiveMethod": [
                            "Implant Injectables"
                        ],
                        "postnatal_received": [
                            "yes"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:0c195453-4cfe-441c-8464-06ea2c2ded38"
                        ]
                    }
                ]
            },
            "form_meta_data": {"GIRL_ID": girl.id, "USER_ID": self.midwife.id}
        }

        url = reverse("mapping_encounter_webhook")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        delivery = Delivery.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(delivery.count(), 1)

        self.assertEqual(FamilyPlanning.objects.count(), 2)