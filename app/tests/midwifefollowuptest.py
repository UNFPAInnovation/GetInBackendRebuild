from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest
from django.utils.crypto import get_random_string


class TestMidwifeFollowUp(ParentTest):
    def test_midwife_follow_up(self):
        """
        Test midwife follow up of girl. Midwife then creates an appointment
        """
        last_name = get_random_string(length=7)
        girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=last_name, dob=timezone.datetime(2000, 3, 3), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3), phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL)
        current_date = timezone.now()
        request_data = {
            "GetInFollowup19_midwife": {
                "$": {
                    "id": "GetInFollowup19_midwife",
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
                "schedule_appointment_group": [
                    {
                        "schedule_appointment": [
                            "{year}-{month}-{day}".format(year=current_date.year, month=current_date.month + 1,
                                                          day=current_date.day)
                        ]
                    }
                ],
                "meta": [
                    {
                        "instanceID": [
                            "uuid:66ac369f-6a72-44ad-929c-37890ad116dd"
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

        followUps = FollowUp.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(followUps.count(), 1)

        appointments = Appointment.objects.filter(girl__last_name__icontains=last_name)
        self.assertEqual(appointments.count(), 1)
