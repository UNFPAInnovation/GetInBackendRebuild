import random

from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest
from django.utils.crypto import get_random_string


class TestMidwifeMapping(ParentTest):
    def test_mapping_encounter_by_midwife_no_previous_appointments(self):
        """
        Test mapping girl who has no previous appointments. the midwife creates one appointment at the end of the process
        """
        request_data = {
            "GetInMapGirlBundibugyo16_midwife": {
                "GirlDemographic": [
                    {
                        "FirstName": [
                            "MukuluGirlTest"
                        ],
                        "LastName": [
                            "Muwalatest"
                        ],
                        "GirlsPhoneNumber": [
                            "0779281" + str(random.randint(100, 999))
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
                "ANCAppointmentGroup": [
                    {
                        "ANCDate": [
                            "2020-05-30"
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
                "USER_ID": self.midwife.id
            }
        }

        url = reverse("mapping_encounter_webhook")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__first_name__icontains="MukuluGirlTest")
        self.assertEqual(appointments.count(), 1)

        self.assertEqual(Girl.objects.first().voucher_number, '')

    def test_mapping_encounter_by_midwife_with_previous_appointments(self):
        """
        Test mapping girl's previous appointment recorded. the midwife creates one appointment at the end of the process
        """
        request_data = {
            "GetInMapGirlBundibugyo16_midwife": {
                "GirlDemographic": [
                    {
                        "FirstName": [
                            "MukuluGirlTest"
                        ],
                        "LastName": [
                            "Muwalatest" + get_random_string(length=3)
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
                "ANCAppointmentGroup": [
                    {
                        "ANCDate": [
                            "2020-05-30"
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
                "USER_ID": self.midwife.id
            }
        }

        url = reverse("mapping_encounter_webhook")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__first_name__icontains="MukuluGirlTest")
        self.assertEqual(appointments.count(), 2)

        self.assertEqual(Girl.objects.first().voucher_number, '')

    def test_mapping_encounter_by_midwife_with_previous_appointments_and_fp(self):
        """
        Test mapping girl's previous appointment recorded and has FP.
        The midwife creates one appointment at the end of the process
        """
        request_data = {
            "GetInMapGirlBundibugyo16_midwife": {
                "$": {
                    "id": "GetInMapGirlBundibugyo16_midwife",
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
                            "Firsttestgirl"
                        ],
                        "LastName": [
                            "Lasttestgirl"
                        ],
                        "GirlsPhoneNumber": [
                            "0756979485"
                        ],
                        "DOB": [
                            "2006-03-09"
                        ]
                    }
                ],
                "GirlDemographic2": [
                    {
                        "NextOfKinNumber": [
                            "0756745688"
                        ]
                    }
                ],
                "GirlLocation": [
                    {
                        "county": [
                            "BWAMBA_COUNTY"
                        ],
                        "subcounty": [
                            "BUSARU"
                        ],
                        "parish": [
                            "KIRINDI"
                        ],
                        "village": [
                            "MUKUNDUNGU"
                        ]
                    }
                ],
                "Observations3": [
                    {
                        "marital_status": [
                            "married"
                        ],
                        "education_level": [
                            "ALevel"
                        ],
                        "MenstruationDate": [
                            "2020-06-13"
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
                            "yes"
                        ]
                    }
                ],
                "ANCAppointmentPreviousGroup": [
                    {
                        "AttendedANCVisit": [
                            "yes"
                        ],
                        "ANCDatePrevious": [
                            "2020-07-13"
                        ]
                    }
                ],
                "ContraceptiveGroup": [
                    {
                        "UsedContraceptives": [
                            "yes"
                        ],
                        "ContraceptiveMethod": [
                            "Pills Injectables Implant"
                        ]
                    }
                ],
                "ANCAppointmentGroup": [
                    {
                        "ANCDate": [
                            "2020-09-13"
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
                            "uuid:f35877e8-439c-475c-922f-2893411bbacb"
                        ]
                    }
                ]
            },
            "form_meta_data": {
                "GIRL_ID": "0",
                "USER_ID": self.midwife.id
            }
        }

        url = reverse("mapping_encounter_webhook")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__first_name__icontains="Firsttestgirl")
        self.assertEqual(appointments.count(), 2)

        self.assertEqual(Observation.objects.count(), 1)
        self.assertEqual(FamilyPlanning.objects.count(), 3)
        self.assertEqual(FamilyPlanning.objects.last().method, "Pills")
        self.assertEqual(Girl.objects.first().voucher_number, '')

    def test_mapping_girl_without_voucher_and_nationality_field(self):
        """
        Test mapping girl's without voucher and nationality fields
        The midwife chooses  yes option to create voucher, girl should have voucher
        The midwife creates one appointment
        """
        request_data = {
            "data": {
                "$": {
                    "id": "GetInMapGirlBundibugyo16_midwife",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
                },
                "GirlDemographic": [
                    {
                        "FirstName": [
                            "Jennifer"
                        ],
                        "LastName": [
                            "Lususu"
                        ],
                        "GirlsPhoneNumber": [
                            "0779281" + str(random.randint(100, 999))
                        ],
                        "DOB": [
                            "2009-09-04"
                        ]
                    }
                ],
                "GirlDemographic2": [
                    {
                        "NextOfKinNumber": [
                            "0779281" + str(random.randint(100, 999))
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
                            "BWAMBA_COUNTY"
                        ],
                        "subcounty": [
                            "BUBUKWANGA"
                        ],
                        "parish": [
                            "HUMYA"
                        ],
                        "village": [
                            "MAMPONGURO"
                        ]
                    }
                ],
                "DisabilityGroup": [
                    {
                        "Disability": [
                            "yes"
                        ]
                    }
                ],
                "Observations3": [
                    {
                        "marital_status": [
                            "married"
                        ],
                        "education_level": [
                            "OLevel"
                        ],
                        "MenstruationDate": [
                            "2020-07-04"
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
                            "yes"
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
                "ContraceptiveGroup": [
                    {
                        "UsedContraceptives": [
                            "yes"
                        ],
                        "ContraceptiveMethod": [
                            "Implant Injectables"
                        ]
                    }
                ],
                "ANCAppointmentGroup": [
                    {
                        "ANCDate": [
                            "2020-11-04"
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
                            "uuid:f176b2ac-f02d-45cf-b76d-917ed81db80d"
                        ]
                    }
                ]
            },
            "form_meta_data": {
                "GIRL_ID": "0",
                "USER_ID": self.midwife.id
            }
        }

        url = reverse("mapping_encounter_webhook")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__first_name__icontains="Jennifer")
        self.assertEqual(appointments.count(), 1)

        self.assertEqual(Observation.objects.count(), 1)
        self.assertEqual(FamilyPlanning.objects.count(), 2)
        self.assertEqual(FamilyPlanning.objects.first().method, "Injectables")

        girl = Girl.objects.first()
        self.assertIsNotNone(girl.voucher_number)
        self.assertEqual(girl.nationality, "Refugee")
        self.assertEqual(girl.disabled, True)

    def test_mapping_girl_with_voucher_and_nationality_field(self):
        """
        Test mapping girl's with voucher and nationality fields
        The User inserts the voucher number in the mapping form.
        In this case a voucher is not created from MSI
        The midwife creates one appointment at the end of the process
        """
        request_data = {
            "data": {
                "$": {
                    "id": "GetInMapGirlBundibugyo16_midwife",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
                },
                "GirlDemographic": [
                    {
                        "FirstName": [
                            "Dhdjdjdd"
                        ],
                        "LastName": [
                            "Dudhd"
                        ],
                        "GirlsPhoneNumber": [
                            "0779281" + str(random.randint(100, 999))
                        ],
                        "DOB": [
                            "2007-08-27"
                        ]
                    }
                ],
                "GirlDemographic2": [
                    {
                        "NextOfKinNumber": [
                            "0779281" + str(random.randint(100, 999))
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
                            "BWAMBA_COUNTY"
                        ],
                        "subcounty": [
                            "BUSARU"
                        ],
                        "parish": [
                            "KIRINDI"
                        ],
                        "village": [
                            "BUNDIKAHUKA_I"
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
                            "ALevel"
                        ],
                        "MenstruationDate": [
                            "2020-06-05"
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
                            "yes"
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
                "ContraceptiveGroup": [
                    {
                        "UsedContraceptives": [
                            "yes"
                        ],
                        "ContraceptiveMethod": [
                            "Implant Condoms Others"
                        ],
                        "other_contraceptive_method": [
                            "Withdrawal"
                        ]
                    }
                ],
                "ANCAppointmentGroup": [
                    {
                        "ANCDate": [
                            "2020-11-05"
                        ]
                    }
                ],
                "VouncherCardGroup": [
                    {
                        "VoucherCard": [
                            "yes"
                        ],
                        "VoucherNumber": [
                            "223-acd"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:b1e2609a-7eaa-489d-9743-c318658c607b"
                        ]
                    }
                ]
            },
            "form_meta_data": {
                "GIRL_ID": "0",
                "USER_ID": self.midwife.id
            }
        }
        url = reverse("mapping_encounter_webhook")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__first_name__icontains="Dhdjdjdd")
        self.assertEqual(appointments.count(), 1)

        self.assertEqual(Observation.objects.count(), 1)
        self.assertEqual(FamilyPlanning.objects.count(), 3)
        self.assertEqual(FamilyPlanning.objects.first().method, "Withdrawal")

        girl = Girl.objects.first()
        self.assertIsNotNone(girl.voucher_number)
        self.assertEqual(girl.voucher_number, "223-acd")
        self.assertEqual(girl.nationality, "Ugandan")
        self.assertEqual(girl.disabled, False)
