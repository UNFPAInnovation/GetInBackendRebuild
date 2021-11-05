from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest


class TestManagerUserQueries(ParentTest):
    def setUp(self) -> None:
        super(TestManagerUserQueries, self).setUp()

        girl = Girl.objects.create(first_name="first_name", last_name="last_name", village=self.village,
                                   phone_number='0756878442', user=self.chew, nationality="Ugandan",
                                   disabled=False, next_of_kin_phone_number='0756878442',
                                   education_level='primary',
                                   dob=(timezone.now() + timezone.timedelta(days=7300)).date(),
                                   marital_status="Single",
                                   last_menstruation_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                                   odk_instance_id="odk_instance_id")

        observation = Observation(blurred_vision=True, bleeding_heavily=False, fever=False, swollen_feet=True)
        observation.save()

        FollowUp.objects.create(girl=girl, user=self.chew, follow_up_action_taken="action_taken_by_health_person",
                                missed_anc_reason="missed_anc_reason", missed_anc_before=True,
                                observation=observation)

        Delivery.objects.create(girl=girl, user=self.chew, action_taken="delivery_action_taken",
                                postnatal_care=True, mother_alive=True, baby_alive=True,
                                delivery_location="Home")

        Appointment.objects.create(girl=girl, user=self.midwife,
                                   date=(timezone.now() + timezone.timedelta(days=30)).date())
        Appointment.objects.create(girl=girl, user=self.midwife,
                                   date=(timezone.now() + timezone.timedelta(days=40)).date())

        girl2 = Girl.objects.create(first_name="first_name2", last_name="last_name2", village=self.village2,
                                    phone_number='0756878443', user=self.chew2, nationality="Ugandan",
                                    disabled=False, next_of_kin_phone_number='0756878443',
                                    education_level='primary',
                                    dob=(timezone.now() + timezone.timedelta(days=7300)).date(),
                                    marital_status="Single",
                                    last_menstruation_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                                    odk_instance_id="odk_instance_id")

        FollowUp.objects.create(girl=girl2, user=self.chew2, follow_up_action_taken="action_taken_by_health_person",
                                missed_anc_reason="missed_anc_reason", missed_anc_before=True,
                                observation=observation)

        Delivery.objects.create(girl=girl2, user=self.chew2, action_taken="delivery_action_taken",
                                postnatal_care=True, mother_alive=True, baby_alive=True,
                                delivery_location="Home")

        Appointment.objects.create(girl=girl2, user=self.midwife5,
                                   date=(timezone.now() + timezone.timedelta(days=30)).date())

        girl3 = Girl.objects.create(first_name="first_name3", last_name="last_name3", village=self.village3,
                                    phone_number='0756878441', user=self.chew3, nationality="Ugandan",
                                    disabled=False, next_of_kin_phone_number='0756878441',
                                    education_level='primary',
                                    dob=(timezone.now() + timezone.timedelta(days=7300)).date(),
                                    marital_status="Single",
                                    last_menstruation_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                                    odk_instance_id="odk_instance_id")

        FollowUp.objects.create(girl=girl3, user=self.chew3, follow_up_action_taken="action_taken_by_health_person",
                                missed_anc_reason="missed_anc_reason", missed_anc_before=True,
                                observation=observation)

        Delivery.objects.create(girl=girl3, user=self.chew3, action_taken="delivery_action_taken",
                                postnatal_care=True, mother_alive=True, baby_alive=True,
                                delivery_location="Home")

        Appointment.objects.create(girl=girl3, user=self.midwife3,
                                   date=(timezone.now() + timezone.timedelta(days=30)).date())

        HealthFacility.objects.create(sub_county=self.sub_county, name="HF1 II", facility_level="2")
        HealthFacility.objects.create(sub_county=self.sub_county2, name="HF2 II", facility_level="2")
        HealthFacility.objects.create(sub_county=self.sub_county3, name="HF3 II", facility_level="2")

        self.assertEqual(Girl.objects.count(), 3)
        self.client.force_authenticate(user=self.manager)

    def test_all_girl_from_single_district(self):
        url = "%s?district=%s" % (reverse('girls'), self.district.id)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 3)
        self.assertEqual(request.json()['count'], 1)

    def test_all_girl_from_all_districts(self):
        url = reverse("girls")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 3)
        self.assertEqual(request.json()['count'], 3)

    def test_chew_all_girl_from_all_districts(self):
        """
        Chew and midwife should only view girls in their district
        """
        self.client.force_authenticate(user=self.chew)
        url = reverse("girls")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Girl.objects.count(), 3)
        self.assertEqual(request.json()['count'], 1)

    def test_all_followup_from_single_district(self):
        url = "%s?district=%s" % (reverse('followups'), self.district.id)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(FollowUp.objects.count(), 3)
        self.assertEqual(request.json()['count'], 1)

    def test_all_followup_from_all_districts(self):
        url = reverse("followups")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(FollowUp.objects.count(), 3)
        self.assertEqual(request.json()['count'], 3)

    def test_chew_all_followup_from_all_districts(self):
        """
        Chew and midwife should only view followups in their district
        """
        self.client.force_authenticate(user=self.chew)
        url = reverse("followups")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(FollowUp.objects.count(), 3)
        self.assertEqual(request.json()['count'], 1)

    def test_all_deliveries_from_single_district(self):
        url = "%s?district=%s" % (reverse('deliveries'), self.district.id)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Delivery.objects.count(), 3)
        self.assertEqual(request.json()['count'], 1)

    def test_all_deliveries_from_all_districts(self):
        url = reverse("deliveries")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Delivery.objects.count(), 3)
        self.assertEqual(request.json()['count'], 3)

    def test_chew_all_deliveries_from_all_districts(self):
        """
        Chew and midwife should only view deliveries in their district
        """
        self.client.force_authenticate(user=self.chew)
        url = reverse("deliveries")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Delivery.objects.count(), 3)
        self.assertEqual(request.json()['count'], 1)

    def test_all_health_facilities_from_single_district(self):
        url = "%s?district=%s" % (reverse('health_facilities'), self.district.id)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(HealthFacility.objects.count(), 4)
        self.assertEqual(request.json()['count'], 2)

    def test_all_health_facilities_from_all_districts(self):
        url = reverse("health_facilities")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(HealthFacility.objects.count(), 4)
        self.assertEqual(request.json()['count'], 4)

    def test_chew_all_health_facilities_from_all_districts(self):
        """
        Chew and midwife should only view health facilities in their district
        """
        self.client.force_authenticate(user=self.chew)
        url = reverse("health_facilities")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(HealthFacility.objects.count(), 4)
        self.assertEqual(request.json()['count'], 2)

    def test_all_appointments_from_single_district(self):
        url = "%s?district=%s" % (reverse('appointments'), self.district.id)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.count(), 4)
        self.assertEqual(request.json()['count'], 2)

    def test_all_appointments_from_all_districts(self):
        url = reverse("appointments")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.count(), 4)
        self.assertEqual(request.json()['count'], 4)

    def test_chew_all_appointments_from_all_districts(self):
        """
        Chew and midwife should only view appointments in their district
        """
        self.client.force_authenticate(user=self.chew)
        url = reverse("appointments")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(Appointment.objects.count(), 4)
        self.assertEqual(request.json()['count'], 2)
