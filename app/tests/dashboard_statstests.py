import random

from django.core import mail
from django.urls import reverse
from rest_framework import status

from app.cron import generate_stats_message, send_monthly_stats_email
from app.extractor import generate_overall_stats
from app.models import *
from app.tests.parenttest import ParentTest
from django.utils.crypto import get_random_string


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

        kwargs = {"from": "{0}-{1}-{2}".format(from_date.year, from_date.month, from_date.day),
                  "to": "{0}-{1}-{2}".format(to_date.year, to_date.month, to_date.day)}
        url = reverse("deliveries-stats")
        response = self.client.get(url, kwargs)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_overall_stats(self):
        months = [
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month),
            random.randint(1, self.current_date.month)
        ]

        for index, month in enumerate(months):
            last_name = get_random_string(length=7)
            if index > 3:
                village = self.village2
                user = self.midwife3
            else:
                village = self.village
                user = self.midwife4
            girl = Girl.objects.create(user=user, first_name=get_random_string(length=7), marital_status=SINGLE,
                                       last_name=last_name, dob=timezone.datetime(2000, 3, 3),
                                       village=village, last_menstruation_date=timezone.datetime(2020, 3, 3),
                                       phone_number="0756789" + str(random.randint(100, 999)),
                                       education_level=PRIMARY_LEVEL)

            Delivery.objects.create(girl=girl, user=user, action_taken="Referred",
                                    baby_birth_date=timezone.datetime(self.current_date.year, month, 1))
            FollowUp.objects.create(girl=girl, user=user)
            Appointment.objects.create(girl=girl, user=user,
                                       date=timezone.now() - timezone.timedelta(days=random.randint(1, 20)))
            Appointment.objects.create(girl=girl, user=user,
                                       date=timezone.now() - timezone.timedelta(days=random.randint(21, 28)))
        self.assertEqual(Girl.objects.count(), 12)
        self.assertEqual(Appointment.objects.count(), 24)
        self.assertEqual(generate_overall_stats('bundibugyo'), {"Mapped girls": 4, "ANC visits": 8, "Follow ups": 4,
                                                                "Deliveries": 4})
        self.assertEqual(generate_overall_stats('arua'), {"Mapped girls": 8, "ANC visits": 16, "Follow ups": 8,
                                                          "Deliveries": 8})

    def test_generate_stats_message(self):
        response = """Hello

Monthly statistics

<strong>BUNDIBUGYO</strong>
Mapped girls: 0
ANC visits: 0
Follow ups: 0
Deliveries: 0


<strong>Arua</strong>
Mapped girls: 0
ANC visits: 0
Follow ups: 0
Deliveries: 0


<strong>Yumbe</strong>
Mapped girls: 0
ANC visits: 0
Follow ups: 0
Deliveries: 0

Regards.
GetIn Team"""
        print(generate_stats_message())

        self.assertEqual(generate_stats_message(), response)

    def test_send_monthly_stats_email(self):
        send_monthly_stats_email()
        self.assertEqual(len(mail.outbox), 1)
        self.assertEqual(mail.outbox[0].subject[:16], 'GetIn statistics')
