from django.shortcuts import redirect
from django.urls import reverse
from rest_framework import status
from app.models import *
from app.tests.parenttest import ParentTest


class TestManagerUserQueries(ParentTest):
    def setUp(self) -> None:
        super(TestManagerUserQueries, self).setUp()

        Girl.objects.create(first_name="first_name", last_name="last_name", village=self.village,
                            phone_number='0756878442', user=self.chew, nationality="Ugandan",
                            disabled=False, next_of_kin_phone_number='0756878442',
                            education_level='primary',
                            dob=(timezone.now() + timezone.timedelta(days=7300)).date(),
                            marital_status="Single",
                            last_menstruation_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                            odk_instance_id="odk_instance_id")

        Girl.objects.create(first_name="first_name2", last_name="last_name2", village=self.village2,
                            phone_number='0756878443', user=self.chew2, nationality="Ugandan",
                            disabled=False, next_of_kin_phone_number='0756878443',
                            education_level='primary',
                            dob=(timezone.now() + timezone.timedelta(days=7300)).date(),
                            marital_status="Single",
                            last_menstruation_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                            odk_instance_id="odk_instance_id")

        Girl.objects.create(first_name="first_name3", last_name="last_name3", village=self.village3,
                            phone_number='0756878441', user=self.chew2, nationality="Ugandan",
                            disabled=False, next_of_kin_phone_number='0756878441',
                            education_level='primary',
                            dob=(timezone.now() + timezone.timedelta(days=7300)).date(),
                            marital_status="Single",
                            last_menstruation_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                            odk_instance_id="odk_instance_id")
        self.client.force_authenticate(user=self.manager)

    def test_all_girl_from_single_district(self):
        url = "%s?district=%s" % (reverse('girls'), self.district.id)
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 1)

    def test_all_girl_from_all_districts(self):
        url = reverse("girls")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 3)

    def test_chew_all_girl_from_all_districts(self):
        """
        Chew and midwife should only view girls in their district
        """
        self.client.force_authenticate(user=self.chew)
        url = reverse("girls")
        request = self.client.get(url)
        self.assertEqual(request.status_code, status.HTTP_200_OK)
        self.assertEqual(request.json()['count'], 1)
