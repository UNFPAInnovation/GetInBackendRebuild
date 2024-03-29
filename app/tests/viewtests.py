import random

from django.urls import reverse
from django.utils.crypto import get_random_string
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest


class TestViews(ParentTest):
    def setUp(self) -> None:
        super(TestViews, self).setUp()
        last_name = get_random_string(length=7)
        self.girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                        last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                        village=self.village,
                                        last_menstruation_date=timezone.now() - timezone.timedelta(weeks=12),
                                        phone_number="0756677" + str(random.randint(100, 999)),
                                        education_level=PRIMARY_LEVEL)

        self.girl2 = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4500),
                                         village=self.village,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=8),
                                         phone_number="0756677" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)

        self.girl3 = Girl.objects.create(user=self.midwife2, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=7),
                                         phone_number="0756677" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)
        self.girl4 = Girl.objects.create(user=self.midwife3, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village2,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=7),
                                         phone_number="0756677" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)

    def test_appointment_view(self):
        """
        Test how different users access appointments.
        Midwife should see all appointments from her VHTs as well as hers
        DHO should see all appointments generated by Midwives and VHTs
        Admin user should see all appointments from every district
        """
        Appointment.objects.create(girl=self.girl, user=self.midwife, date=timezone.now() + timezone.timedelta(weeks=2))
        Appointment.objects.create(girl=self.girl, user=self.chew, date=timezone.now() + timezone.timedelta(weeks=2))
        Appointment.objects.create(girl=self.girl2, user=self.chew, date=timezone.now() + timezone.timedelta(weeks=1))
        Appointment.objects.create(girl=self.girl3, user=self.midwife2,
                                   date=timezone.now() + timezone.timedelta(weeks=1))

        url = reverse("appointments")

        self.client.force_authenticate(user=self.chew)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 3)

        self.client.force_authenticate(user=self.midwife)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 3)

        self.client.force_authenticate(user=self.midwife2)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 1)

        self.client.force_authenticate(user=self.dho)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 4)

    def test_girls_view(self):
        """
        Test how different users access girls.
        Midwife should see all girls from her VHTs as well as hers
        DHO should see all girls generated by Midwives and VHTs
        Admin user should see all girls from every district
        """
        url = reverse("girls")

        self.client.force_authenticate(user=self.chew)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 3)

        self.client.force_authenticate(user=self.midwife)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 3)

        self.client.force_authenticate(user=self.midwife2)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 3)

        self.client.force_authenticate(user=self.dho)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 3)

        self.client.force_authenticate(user=self.user)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 4)

        self.client.force_authenticate(user=self.manager)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 4)

    def test_health_facility_view(self):
        request_data = {
            "name": "healthfacility1",
            "sub_county_id": self.sub_county.id
        }

        url = reverse("health_facilities")
        self.client.force_authenticate(user=self.dho)

        request = self.client.post(url, request_data, format='json')
        self.assertEqual(request.status_code, status.HTTP_201_CREATED)
        self.assertEqual(HealthFacility.objects.count(), 2)

        HealthFacility.objects.create(sub_county=self.sub_county, name="healthfacility2")
        HealthFacility.objects.create(sub_county=self.sub_county2, name="healthfacility3")

        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 3)

        self.client.force_authenticate(user=self.user)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 4)

        self.client.force_authenticate(user=self.manager)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 4)

    def test_followup_view(self):
        """
        Test how different users access followups.
        Midwife should see all followups from her VHTs as well as hers
        DHO should see all followups generated by Midwives and VHTs
        Admin user should see all followups from every district
        """
        FollowUp.objects.create(girl=self.girl, user=self.midwife)
        FollowUp.objects.create(girl=self.girl, user=self.chew)
        FollowUp.objects.create(girl=self.girl2, user=self.chew)
        FollowUp.objects.create(girl=self.girl3, user=self.midwife2)
        FollowUp.objects.create(girl=self.girl4, user=self.midwife3)

        url = reverse("followups")

        self.client.force_authenticate(user=self.chew)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 2)

        self.client.force_authenticate(user=self.midwife)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 3)

        self.client.force_authenticate(user=self.midwife2)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 1)

        self.client.force_authenticate(user=self.dho)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 4)

        self.client.force_authenticate(user=self.user)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 5)

    def test_delivery_view(self):
        """
        Test how different users access delivery.
        Midwife should see all delivery from her VHTs as well as hers
        DHO should see all delivery generated by Midwives and VHTs
        Admin user should see all delivery from every district
        """
        Delivery.objects.create(girl=self.girl, user=self.midwife)
        Delivery.objects.create(girl=self.girl, user=self.chew)
        Delivery.objects.create(girl=self.girl2, user=self.chew)
        Delivery.objects.create(girl=self.girl3, user=self.midwife2)
        Delivery.objects.create(girl=self.girl3, user=self.midwife3)

        url = reverse("deliveries")

        self.client.force_authenticate(user=self.chew)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 2)

        self.client.force_authenticate(user=self.midwife)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 3)

        self.client.force_authenticate(user=self.midwife2)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 1)

        self.client.force_authenticate(user=self.dho)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 4)

        self.client.force_authenticate(user=self.user)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 5)

    def test_sms_view(self):
        """
        Test sending and viewing of sent sms.
        Midwife and CHEW are restricted from using this feature
        DHO, Admin and Developer are the only users allowed
        """
        SmsModel.objects.create(recipient=self.chew, message="test", message_id="abc234", status="received", sender_id=self.dho.id)
        SmsModel.objects.create(recipient=self.midwife, message="test", message_id="abc235", status="received", sender_id=self.dho.id)

        url = reverse("sms")
        self.client.force_authenticate(user=self.dho)

        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 2)

        self.client.force_authenticate(user=self.chew)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.midwife)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_403_FORBIDDEN)

        self.client.force_authenticate(user=self.user)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 2)