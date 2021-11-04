from app.models import *
from app.serializers import GirlSerializer
from app.tests import ParentTest

"""
TESTS GUIDE
assertEqual(actual, expected)
"""


class TestUser(ParentTest):
    def test_health_facility_field_of_chew_mapped_girl(self):
        girl = Girl.objects.create(first_name="first_name", last_name="last_name", village=self.village,
                                   phone_number='0756878442', user=self.chew, nationality="Ugandan",
                                   disabled=False, next_of_kin_phone_number='0756878441',
                                   education_level='primary', dob=(timezone.now() + timezone.timedelta(days=7300)).date(),
                                   marital_status="Single",
                                   last_menstruation_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                                   odk_instance_id="odk_instance_id")

        serializer_data = GirlSerializer(girl)
        self.assertEqual(serializer_data.data['health_facility'], self.healthfacility.name)

    def test_health_facility_field_of_midwife_mapped_girl(self):
        girl = Girl.objects.create(first_name="first_name", last_name="last_name", village=self.village,
                                   phone_number='0756878442', user=self.midwife, nationality="Ugandan",
                                   disabled=False, next_of_kin_phone_number='0756878441',
                                   education_level='primary', dob=(timezone.now() + timezone.timedelta(days=7300)).date(),
                                   marital_status="Single",
                                   last_menstruation_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                                   odk_instance_id="odk_instance_id")

        serializer_data = GirlSerializer(girl)
        self.assertEqual(serializer_data.data['health_facility'], self.healthfacility.name)

    def test_empty_health_facility_field_of_chew_mapped_girl(self):
        girl = Girl.objects.create(first_name="first_name", last_name="last_name", village=self.village,
                                   phone_number='0756878442', user=self.chew2, nationality="Ugandan",
                                   disabled=False, next_of_kin_phone_number='0756878441',
                                   education_level='primary', dob=(timezone.now() + timezone.timedelta(days=7300)).date(),
                                   marital_status="Single",
                                   last_menstruation_date=(timezone.now() + timezone.timedelta(days=30)).date(),
                                   odk_instance_id="odk_instance_id")

        serializer_data = GirlSerializer(girl)
        self.assertEqual(serializer_data.data['health_facility'], '')