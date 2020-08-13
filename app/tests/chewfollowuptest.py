import random

from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest
from django.utils.crypto import get_random_string


class TestChewFollowUp(ParentTest):
    def test_chew_follow_up(self):
        """
        Test chew follow up of girl
        """
        last_name = get_random_string(length=7)
        girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3), phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL)
        request_data = {
            "GetInFollowup20_chew": {
                "$": {
                    "id": "GetInFollowup20_chew",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
                },
                "missed_anc_before_group": [
                    {
                        "missed_anc_before": [
                            "yes"
                        ]
                    }
                ],
                "missed_anc_before_group2": [
                    {
                        "missed_anc_reason": [
                            "too_busy"
                        ]
                    }
                ],
                "observations1": [
                    {
                        "bleeding": [
                            "yes"
                        ],
                        "fever": [
                            "yes"
                        ]
                    }
                ],
                "observations2": [
                    {
                        "swollenfeet": [
                            "yes"
                        ],
                        "blurred_vision": [
                            "no"
                        ]
                    }
                ],
                "emergency_call": [
                    ""
                ],
                "action_taken_by_health_person_group": [
                    {
                        "action_taken_by_health_person": [
                            "referral"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:16b8056f-d4a2-4029-8507-b7428acd2c6c"
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

        followUps = FollowUp.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(followUps.count(), 1)

    def test_chew_followup_with_referral(self):
        """
        Test chew follows up a girl who has all observations as yes. A referral to midwife must be created
        """
        last_name = get_random_string(length=7)
        girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3),
                                   phone_number="0756789" + str(random.randint(100,999)), education_level=PRIMARY_LEVEL)
        request_data = {
            "GetInFollowup20_chew": {
                "$": {
                    "id": "GetInFollowup20_chew",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
                },
                "missed_anc_before_group": [
                    {
                        "missed_anc_before": [
                            "yes"
                        ]
                    }
                ],
                "missed_anc_before_group2": [
                    {
                        "missed_anc_reason": [
                            "too_busy"
                        ]
                    }
                ],
                "observations1": [
                    {
                        "bleeding": [
                            "yes"
                        ],
                        "fever": [
                            "yes"
                        ]
                    }
                ],
                "observations2": [
                    {
                        "swollenfeet": [
                            "yes"
                        ],
                        "blurred_vision": [
                            "yes"
                        ]
                    }
                ],
                "emergency_call": [
                    ""
                ],
                "action_taken_by_health_person_group": [
                    {
                        "action_taken_by_health_person": [
                            "referral"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:16b8056f-d4a2-4029-8507-b7428acd2c6c"
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

        followUps = FollowUp.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(followUps.count(), 1)

        self.assertEqual(Observation.objects.count(), 1)

        referral = Referral.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(referral.count(), 1)

    def test_chew_followup_and_delivery(self):
        """
        Test chew follows up a girl who has delivered. A follow up and delivery must be captured
        """
        last_name = get_random_string(length=7)
        girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3), phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL)
        request_data = {
            "GetInFollowup20_chew": {
                "$": {
                    "id": "GetInFollowup20_chew",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms"
                },
                "missed_anc_before_group": [
                    {
                        "missed_anc_before": [
                            "yes"
                        ]
                    }
                ],
                "missed_anc_before_group2": [
                    {
                        "missed_anc_reason": [
                            "lack_of_money"
                        ]
                    }
                ],
                "observations1": [
                    {
                        "bleeding": [
                            "yes"
                        ],
                        "fever": [
                            "no"
                        ]
                    }
                ],
                "observations2": [
                    {
                        "swollenfeet": [
                            "yes"
                        ],
                        "blurred_vision": [
                            "no"
                        ]
                    }
                ],
                "emergency_call": [
                    ""
                ],
                "action_taken_by_health_person_group": [
                    {
                        "action_taken_by_health_person": [
                            "delivery"
                        ]
                    }
                ],
                "delivery_followup_group": [
                    {
                        "mother_delivery_outcomes": [
                            "mother_alive"
                        ],
                        "baby_delivery_outcomes": [
                            "baby_dead"
                        ],
                        "baby_death_date": [
                            "2020-08-05"
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
                            "Condoms"
                        ],
                        "postnatal_received": [
                            "yes"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:9382bc50-1ca0-4fb1-bf58-79d3a6319c8a"
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

        followUps = FollowUp.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(followUps.count(), 1)

        self.assertEqual(Observation.objects.count(), 1)
        self.assertEqual(FamilyPlanning.objects.count(), 1)

        delivery = Delivery.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(delivery.count(), 1)
