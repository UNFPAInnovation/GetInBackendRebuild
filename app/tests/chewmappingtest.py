from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest
from django.utils.crypto import get_random_string


class TestChewMapping(ParentTest):
    def test_mapping_encounter_by_chew_no_previous_appointments(self):
        """
        Test mapping girl who has no previous appointments is recorded.
        The system autogenerates an appointment within a 2 weeks period
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
        self.assertEqual(MappingEncounter.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(appointments.count(), 1)

        # test that the appointment is within 2 weeks period
        self.assertLess(appointments.first().date.replace(tzinfo=None),
                        timezone.now().replace(tzinfo=None) + timezone.timedelta(weeks=2))

        self.assertEqual(Girl.objects.first().voucher_number, '')
        self.assertEqual(MSIService.objects.count(), 0)

    def test_mapping_encounter_by_chew_girl_below_84(self):
        """
        Test mapping girl who has last_menstration day less than 84 days.
        The system autogenerates an appointment within a 12 weeks period
        """
        last_name = "MukuluGirlTest" + get_random_string(length=3)
        current_date = timezone.now()
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
                            "2020-" + str((current_date - timezone.timedelta(days=30)).month) + "-28"
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
        self.assertEqual(MappingEncounter.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(appointments.count(), 1)

        # test that the appointment is within 12 weeks period for girls who have lmd less than 84
        self.assertLess(appointments.first().date.replace(tzinfo=None),
                        timezone.now().replace(tzinfo=None) + timezone.timedelta(weeks=12))

        self.assertEqual(Girl.objects.first().voucher_number, '')

        url = reverse("mapping-encounters")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 1)
        self.assertEqual(MSIService.objects.count(), 0)

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
                        ],
                        "VoucherNumberCreation": [
                            "yes"
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
        self.assertEqual(MappingEncounter.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__last_name__icontains=last_name)
        # appointments should be 2 since the previous appointment is recorded and a new autogenerated appointment
        self.assertEqual(appointments.count(), 2)

        # test that the appointment is within 2 weeks period
        self.assertLess(appointments.first().date.replace(tzinfo=None),
                        timezone.now().replace(tzinfo=None) + timezone.timedelta(weeks=2))

        self.assertEqual(Girl.objects.first().voucher_number, '')

        url = reverse("mapping-encounters")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 1)

        self.client.force_authenticate(user=self.midwife)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)

        self.client.force_authenticate(user=self.dho)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(MSIService.objects.count(), 0)

    def test_mapping_encounter_by_chew_in_MSI_regions(self):
        """
        Test mapping girl who is in a region where MSI operates
        Result:
        - VHT should always create vouchers. Regardless of the options they choose
        """
        last_name = "MukuluGirlTest" + get_random_string(length=3)
        current_date = timezone.now()

        request_data = {
            "data": {
                "$": {
                    "id": "GetInMapGirlYumbe1_chew",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms"
                },
                "GirlDemographic": [
                    {
                        "FirstName": [
                            "Samusa"
                        ],
                        "LastName": [
                            last_name
                        ],
                        "GirlsPhoneNumber": [
                            "0783563675"
                        ],
                        "DOB": [
                            "1998-04-01"
                        ]
                    }
                ],
                "GirlDemographic2": [
                    {
                        "NextOfKinNumber": [
                            "0783563675"
                        ]
                    }
                ],
                "NationalityGroup": [
                    {
                        "Nationality": [
                            "Ugandan"
                        ]
                    }
                ],
                "GirlLocation": [
                    {
                        "county": [
                            "Yumbe"
                        ],
                        "subcounty": [
                            "Kululu"
                        ],
                        "parish": [
                            "Aliapi"
                        ],
                        "village": [
                            "Onjiri"
                        ]
                    }
                ],
                "DisabilityGroup": [
                    {
                        "Disability": [
                            "no"
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
                            str(current_date.year) + "-" + str((current_date - timezone.timedelta(days=30)).month) + "-28"
                        ]
                    }
                ],
                "Observations1": [
                    {
                        "bleeding": [
                            "no"
                        ],
                        "fever": [
                            "no"
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
                "ContraceptiveGroup": [
                    {
                        "UsedContraceptives": [
                            "yes"
                        ],
                        "ContraceptiveMethod": [
                            "Pills"
                        ]
                    }
                ],
                "ANCAppointmentPreviousGroup": [
                    {
                        "AttendedANCVisit": [
                            "yes"
                        ],
                        "ANCDatePrevious": [
                            "2021-01-29"
                        ]
                    }
                ],
                "VouncherCardGroup": [
                    {
                        "VoucherCard": [
                            "no"
                        ],
                        "VoucherNumberCreation": [
                            "no"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:c7d07eda-3fc2-4cce-a4ac-5acc1b8f5d35"
                        ]
                    }
                ]
            },
            "form_meta_data": {
                "GIRL_ID": "0",
                "USER_ID": self.chew2.id
            }
        }

        url = reverse("mapping_encounter_webhook")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)
        self.assertEqual(Girl.objects.first().last_name, last_name)
        self.assertNotEqual(Girl.objects.first().voucher_number, '')

    def test_mapping_encounter_by_chew_with_age_field(self):
        """
        Test mapping girl with a form that has an age field instead of DOB
        """
        last_name = "MukuluGirlTest" + get_random_string(length=3)
        age = 45

        request_data = {
            "data": {
                "$": {
                    "id": "GetInMapGirlYumbe1_chew",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms"
                },
                "GirlDemographic": [
                    {
                        "FirstName": [
                            "Tttrrr"
                        ],
                        "LastName": [
                            last_name
                        ],
                        "GirlsPhoneNumber": [
                            "0757888777"
                        ],
                        "Age": [
                            str(age)
                        ]
                    }
                ],
                "GirlDemographic2": [
                    {
                        "NextOfKinNumber": [
                            "0755555777"
                        ]
                    }
                ],
                "NationalityGroup": [
                    {
                        "Nationality": [
                            "Refugee"
                        ]
                    }
                ],
                "GirlLocation": [
                    {
                        "county": [
                            "YUMBE"
                        ],
                        "subcounty": [
                            "KURU"
                        ],
                        "parish": [
                            "LIBUA"
                        ],
                        "village": [
                            "A'UNGA"
                        ]
                    }
                ],
                "DisabilityGroup": [
                    {
                        "Disability": [
                            "I have challenges walking/climbing some places"
                        ]
                    }
                ],
                "Observations3": [
                    {
                        "marital_status": [
                            "divorced"
                        ],
                        "education_level": [
                            "O Level"
                        ],
                        "MenstruationDate": [
                            "2021-10-18"
                        ]
                    }
                ],
                "Observations1": [
                    {
                        "bleeding": [
                            "no"
                        ],
                        "fever": [
                            "no"
                        ]
                    }
                ],
                "Observations2": [
                    {
                        "swollenfeet": [
                            "yes"
                        ],
                        "blurred_vision": [
                            "yes"
                        ]
                    }
                ],
                "EmergencyCall": [
                    ""
                ],
                "ContraceptiveGroup": [
                    {
                        "UsedContraceptives": [
                            "yes"
                        ],
                        "ContraceptiveMethod": [
                            "Condoms Injectables Implant"
                        ]
                    }
                ],
                "ANCAppointmentPreviousGroup": [
                    {
                        "AttendedANCVisit": [
                            "no"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:dc45b955-5819-4077-820c-ba9e69cf9b66"
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
        self.assertEqual(MappingEncounter.objects.count(), 1)
        self.assertEqual(Girl.objects.first().age, 45)
