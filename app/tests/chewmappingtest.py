from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest
from django.utils.crypto import get_random_string


class TestChewMapping(ParentTest):
    def test_mapping_encounter_by_chew_no_previous_appointments(self):
        """
        Test mapping girl who has no previous appointments is recorded and the system autogenerates an appointment within a 2 weeks period
        """
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
                            "2004-02-26"
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
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(appointments.count(), 1)

        # test that the appointment is within 2 weeks period
        self.assertLess(appointments.first().date.replace(tzinfo=None),
                        timezone.now().replace(tzinfo=None) + timezone.timedelta(weeks=2))

        self.assertIsNotNone(Girl.objects.first().voucher_number)

    def test_mapping_encounter_by_chew_with_previous_appointments(self):
        """
        Test mapping girl who has a previous appointments is recorded and the system autogenerates an appointment within a 2 weeks period
        """
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
                            "2004-02-26"
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
                            "yes"
                        ],
                        "ANCDatePrevious": [
                            "2020-04-14"
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
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__last_name__icontains=last_name)
        # appointments should be 2 since the previous appointment is recorded and a new autogenerated appointment
        self.assertEqual(appointments.count(), 2)

        # test that the appointment is within 2 weeks period
        self.assertLess(appointments.first().date.replace(tzinfo=None),
                        timezone.now().replace(tzinfo=None) + timezone.timedelta(weeks=2))

        self.assertIsNotNone(Girl.objects.first().voucher_number)