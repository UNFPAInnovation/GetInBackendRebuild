import random

from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest
from django.utils.crypto import get_random_string

from app.utils.utilities import add_months


class TestDashboardStats(ParentTest):
    def test_mapping_encounter_stats(self):
        """
        Test mapping encounter stats for the dashboard
        """
        years = [
            random.randint(self.current_date.year - 22, self.current_date.year - 20),
            random.randint(self.current_date.year - 22, self.current_date.year - 20),
            random.randint(self.current_date.year - 18, self.current_date.year - 16),
            random.randint(self.current_date.year - 18, self.current_date.year - 16),
            random.randint(self.current_date.year - 15, self.current_date.year - 12),
            random.randint(self.current_date.year - 15, self.current_date.year - 12)
        ]
        for year in years:
            last_name = "MukuluGirlTest" + get_random_string(length=3)
            request_data = {
                "GetInMapGirlBundibugyo17_chew": {
                    "GirlDemographic": [
                        {
                            "FirstName": [
                                "MukuluGirlTest"
                            ],
                            "LastName": [
                                last_name
                            ],
                            "GirlsPhoneNumber": [
                                "0779281444"
                            ],
                            "DOB": [
                                "{year}-02-26".format(year=year)
                            ]
                        }
                    ],
                    "GirlDemographic2": [
                        {
                            "NextOfKinNumber": [
                                "0779281822"
                            ]
                        }
                    ],
                    "GirlLocation": [
                        {
                            "county": [
                                "BUGHENDERA_COUNTY"
                            ],
                            "subcounty": [
                                "SINDILA"
                            ],
                            "parish": [
                                "NYANKONDA"
                            ],
                            "village": [
                                "BULYATA_II"
                            ]
                        }
                    ],
                    "Observations3": [
                        {
                            "marital_status": [
                                "married"
                            ],
                            "education_level": [
                                "primary_level"
                            ],
                            "MenstruationDate": [
                                "2020-02-28"
                            ]
                        }
                    ],
                    "Observations1": [
                        {
                            "bleeding": [
                                "no"
                            ],
                            "fever": [
                                "yes"
                            ]
                        }
                    ],
                    "Observations2": [
                        {
                            "swollenfeet": [
                                "no"
                            ],
                            "blurred_vision": [
                                "no"
                            ]
                        }
                    ],
                    "EmergencyCall": [
                        ""
                    ],
                    "ANCAppointmentPreviousGroup": [
                        {
                            "AttendedANCVisit": [
                                "no"
                            ]
                        }
                    ],
                    "ContraceptiveGroup": [
                        {
                            "UsedContraceptives": [
                                "no"
                            ],
                            "ReasonNoContraceptives": [
                                "None"
                            ]
                        }
                    ],
                    "VouncherCardGroup": [
                        {
                            "VoucherCard": [
                                "no"
                            ]
                        }
                    ],
                    "meta": [
                        {
                            "instanceID": [
                                "uuid:21a505a9-2d17-4fed-a3ad-183343227eb3"
                            ]
                        }
                    ]
                },
                "form_meta_data": {
                    "GIRL_ID": "0",
                    "USER_ID": self.chew.id
                }
            }

            url = reverse("mapping_encounter_webhook")
            self.client.post(url, request_data, format='json')
        girl = Girl.objects.last()
        girl.created_at = self.current_date - timezone.timedelta(days=30)
        girl.save(update_fields=['created_at'])
        self.assertEqual(Girl.objects.count(), 6)

        from_date = timezone.now() - timezone.timedelta(weeks=8)
        to_date = timezone.now() + timezone.timedelta(weeks=4)
        to_date = timezone.datetime(to_date.year, to_date.month, from_date.day)

        kwargs = {"from": "{0}-{1}-{2}".format(from_date.year, from_date.month, from_date.day),
                  "to": "{0}-{1}-{2}".format(to_date.year, to_date.month, to_date.day)}
        url = reverse("mapping-encounters-stats")
        response = self.client.get(url, kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_delivery_stats(self):
        months = [
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
        ]
        for month in months:
            last_name = get_random_string(length=7)
            girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                       last_name=last_name, dob=timezone.datetime(2000, 3, 3), village=self.village,
                                       last_menstruation_date=timezone.datetime(2020, 3, 3),
                                       phone_number="0756789" + str(random.randint(100, 999)),
                                       education_level=PRIMARY_LEVEL)

            Delivery.objects.create(girl=girl, user=self.chew, action_taken="Referred",
                                    baby_birth_date=timezone.datetime(self.current_date.year, month, 1))

        self.assertEqual(Girl.objects.count(), 2)
        self.assertEqual(Delivery.objects.count(), 2)

        from_date = timezone.now() - timezone.timedelta(weeks=8)
        to_date = timezone.now() + timezone.timedelta(weeks=4)
        to_date = timezone.datetime(to_date.year, to_date.month, from_date.day)

        response_data = [{'subcounties': [], 'count': 0}, {'subcounties': [], 'count': 0},
                         {'subcounties': ['BUBANDI'], 'deliveriesFromSubcountyBUBANDI': 2, 'count': 2}]
        kwargs = {"from": "{0}-{1}-{2}".format(from_date.year, from_date.month, from_date.day),
                  "to": "{0}-{1}-{2}".format(to_date.year, to_date.month, to_date.day)}
        url = reverse("deliveries-stats")
        response = self.client.get(url, kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.json(), response_data)
