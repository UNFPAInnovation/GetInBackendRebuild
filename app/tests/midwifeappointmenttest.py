from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest
from django.utils.crypto import get_random_string


class TestAppointment(ParentTest):
    def test_midwife_appointment_referred_girl(self):
        """
        Test midwife receives girl from her previous appointment and creates a new appointment and referred girl
        """
        last_name = get_random_string(length=7)
        girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3), phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL)
        request_data = {
            "GetINAppointment10_midwife": {
                "$": {
                    "id": "GetINAppointment10_midwife",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms"
                },
                "voucher_received_group": [
                    {
                        "has_voucher": [
                            "yes"
                        ]
                    }
                ],
                "voucher_validate_group": [
                    {
                        "ex_printer_widget": [
                            ""
                        ]
                    }
                ],
                "voucher_redeem_group": [
                    {
                        "voucher_services": [
                            "ANC1"
                        ],
                        "ex_printer_widget": [
                            ""
                        ]
                    }
                ],
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
                "ambulance_group": [
                    {
                        "needed_ambulance": [
                            "yes"
                        ],
                        "used_ambulance": [
                            "yes"
                        ]
                    }
                ],
                "appointment_soon_group": [
                    ""
                ],
                "action_taken_group": [
                    {
                        "action_taken_meeting_girl": [
                            "referred"
                        ]
                    }
                ],
                "schedule_appointment_group": [
                    {
                        "schedule_appointment": [
                            "2020-10-12"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:babbf9e7-784a-4be8-987d-19b7910dfd4b"
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

        appointments = Appointment.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(appointments.count(), 1)

    def test_midwife_appointment_referred_girl_different_structure(self):
        """
        Test midwife receives girl from her previous appointment and creates a new appointment and referred girl
        NOTE: The json object can either start with the form name or object called data
        """
        last_name = get_random_string(length=7)
        girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3), phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL)
        request_data = {
            "data": {
                "$": {
                    "id": "GetINAppointment10_midwife",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms"
                },
                "voucher_received_group": [
                    {
                        "has_voucher": [
                            "yes"
                        ]
                    }
                ],
                "voucher_validate_group": [
                    {
                        "ex_printer_widget": [
                            ""
                        ]
                    }
                ],
                "voucher_redeem_group": [
                    {
                        "voucher_services": [
                            "ANC1"
                        ],
                        "ex_printer_widget": [
                            ""
                        ]
                    }
                ],
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
                "ambulance_group": [
                    {
                        "needed_ambulance": [
                            "yes"
                        ],
                        "used_ambulance": [
                            "yes"
                        ]
                    }
                ],
                "appointment_soon_group": [
                    ""
                ],
                "action_taken_group": [
                    {
                        "action_taken_meeting_girl": [
                            "referred"
                        ]
                    }
                ],
                "schedule_appointment_group": [
                    {
                        "schedule_appointment": [
                            "2020-10-12"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:babbf9e7-784a-4be8-987d-19b7910dfd4b"
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

        appointments = Appointment.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(appointments.count(), 1)

    def test_midwife_appointment_other_action_taken_different_structure(self):
        """
        Test midwife receives girl from her previous appointment and creates a new appointment and performs an action
        NOTE: The json object can either start with the form name or object called data
        """
        last_name = get_random_string(length=7)
        girl = Girl.objects.create(user=self.chew2, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3), village=self.village3,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3), phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL)
        request_data = {
            "data": {
                "$": {
                    "id": "GetINAppointment10_midwife",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms"
                },
                "voucher_received_group": [
                    {
                        "has_voucher": [
                            "yes"
                        ]
                    }
                ],
                "voucher_validate_group": [
                    {
                        "voucher_validate": [
                            ""
                        ]
                    }
                ],
                "voucher_redeem_group": [
                    {
                        "voucher_services": [
                            "AN3"
                        ],
                        "voucher_redeem": [
                            ""
                        ]
                    }
                ],
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
                "ambulance_group": [
                    {
                        "needed_ambulance": [
                            "yes"
                        ],
                        "used_ambulance": [
                            "yes"
                        ]
                    }
                ],
                "appointment_soon_group": [
                    ""
                ],
                "action_taken_group": [
                    {
                        "action_taken_meeting_girl": [
                            "other"
                        ],
                        "action_taken_other": [
                            "Offered family planning"
                        ]
                    }
                ],
                "schedule_appointment_group": [
                    {
                        "schedule_appointment": [
                            "2020-10-12"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:ae773245-8150-4aab-9ca0-eea03544974e"
                        ]
                    }
                ]
            },
            "form_meta_data": {"GIRL_ID": girl.id, "USER_ID": self.midwife5.id}
        }

        url = reverse("mapping_encounter_webhook")
        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__last_name__icontains=last_name)
        appointment_encounters = AppointmentEncounter.objects.all()

        self.assertEqual(appointments.count(), 1)
        self.assertEqual(appointment_encounters.count(), 1)
        self.assertEqual(appointment_encounters.first().action_taken, 'Offered family planning')

        services = MSIService.objects.all()
        self.assertEqual(services.count(), 1)
        self.assertEqual(services.first().option, "AN3")

        request_data = {
            "data": {
                "$": {
                    "id": "GetINAppointment10_midwife",
                    "xmlns:ev": "http://www.w3.org/2001/xml-events",
                    "xmlns:orx": "http://openrosa.org/xforms",
                    "xmlns:odk": "http://www.opendatakit.org/xforms",
                    "xmlns:h": "http://www.w3.org/1999/xhtml",
                    "xmlns:jr": "http://openrosa.org/javarosa",
                    "xmlns:xsd": "http://www.w3.org/2001/XMLSchema"
                },
                "voucher_received_group": [
                    {
                        "has_voucher": [
                            "no"
                        ]
                    }
                ],
                "missed_anc_before_group": [
                    {
                        "missed_anc_before": [
                            "no"
                        ]
                    }
                ],
                "missed_anc_before_group2": [
                    ""
                ],
                "ambulance_group": [
                    {
                        "needed_ambulance": [
                            "no"
                        ]
                    }
                ],
                "appointment_soon_group": [
                    {
                        "appointment_method": [
                            "physical_visit"
                        ]
                    }
                ],
                "action_taken_group": [
                    {
                        "action_taken_meeting_girl": [
                            "set_an_appointment"
                        ]
                    }
                ],
                "schedule_appointment_group": [
                    {
                        "schedule_appointment": [
                            "2020-12-07"
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:dcb3467f-754f-4494-a21e-90b3234d69f8"
                        ]
                    }
                ]
            },
            "form_meta_data": {"GIRL_ID": girl.id, "USER_ID": self.midwife5.id}
        }

        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 1)

        appointments = Appointment.objects.filter(girl__last_name__icontains=last_name)
        appointment_encounters = AppointmentEncounter.objects.all()

        self.assertEqual(appointments.count(), 2)
        self.assertEqual(appointment_encounters.count(), 2)

        appointment_encounter = AppointmentEncounter.objects.first()
        self.assertEqual(appointment_encounter.appointment_method, "physical visit")
