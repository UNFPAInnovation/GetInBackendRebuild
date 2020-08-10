from django.utils.crypto import get_random_string
from app.models import *
from app.tests import ParentTest


class TestModel(ParentTest):
    def test_create_girl_msi_service(self):
        """
        Test creation of girl's msi services when redeeming one of the services
        """
        girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=get_random_string(length=7), dob=timezone.datetime(2000, 3, 3), village=self.village,
                                   last_menstruation_date=timezone.datetime(2020, 3, 3), phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL)
        MSIService.objects.create(girl=girl, option="ANC1")
        msi_service = MSIService.objects.all()
        self.assertEqual(msi_service.count(), 1)
