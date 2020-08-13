import json
from django.utils.crypto import get_random_string
from rest_framework.renderers import JSONRenderer
from app.models import *
from app.serializers import GirlSerializer
from app.tests.parenttest import ParentTest


class TestSerializer(ParentTest):
    def test_girl_serializer(self):
        last_name = "MukuluGirlTest" + get_random_string(length=3)
        girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                   last_name=last_name, dob=datetime.date(2000, 3, 3), village=self.village,
                                   last_menstruation_date=datetime.date(2020, 3, 3), phone_number="0756789543",
                                   education_level=PRIMARY_LEVEL, voucher_number="123-XYZ")
        MSIService.objects.create(girl=girl, option="ANC1")
        MSIService.objects.create(girl=girl, option="ANC2")

        request_data = {
            "id": str(girl.id),
            "first_name": girl.first_name,
            "last_name": girl.last_name,
            "village": {
                "id": 1,
                "parish": {
                    "id": 1,
                    "sub_county": {
                        "id": 1,
                        "county": {
                            "id": 1,
                            "district": {
                                "id": 1,
                                "name": "BUNDIBUGYO",
                                "region": 1
                            },
                            "name": "BWAMBA_COUNTY"
                        },
                        "name": "BUBANDI"
                    },
                    "name": "NJUULE"
                },
                "name": "BUNDISELYA"
            },
            "phone_number": girl.phone_number,
            "trimester": girl.trimester,
            "next_of_kin_phone_number": girl.next_of_kin_phone_number,
            "education_level": "Primary level",
            "marital_status": "Single",
            "last_menstruation_date": str(girl.last_menstruation_date),
            "dob": str(girl.dob),
            "user": str(self.chew.id),
            "odk_instance_id": None,
            "age": girl.age,
            "completed_all_visits": False,
            "voucher_number": "123-XYZ",
            "pending_visits": girl.pending_visits,
            "missed_visits": 0,
            "services_received": "ANC1,ANC2",
            "created_at": str(girl.created_at.astimezone().isoformat())
        }

        self.assertEqual(Girl.objects.count(), 1)

        services = MSIService.objects.all()
        self.assertEqual(services.count(), 2)
        self.assertEqual(services.first().option, "ANC1")

        serializer = GirlSerializer(girl)
        expected_data = json.dumps(request_data).strip().replace(': ', ':').replace(', ', ',')
        actual_data = JSONRenderer().render(serializer.data).decode("utf-8")
        self.assertEqual(actual_data, expected_data)
