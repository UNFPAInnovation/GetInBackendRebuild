import random
from tempfile import TemporaryFile

from rest_framework.test import APITestCase
from xlwt import Workbook

from GetInBackendRebuild.settings import SHEET_FILES_FOLDER
from app.extractor import extract_excel_org_unit_data, extract_excel_user_data
from app.models import District, County, SubCounty, Parish, Village, User, Region, HealthFacility
from app.utils.constants import USER_TYPE_CHEW, USER_TYPE_MIDWIFE, GENDER_MALE


class TestImport(APITestCase):
    def setUp(self) -> None:
        self.region2 = Region.objects.create(name="Northern")
        self.district2 = District.objects.create(name="Arua", region=self.region2)
        self.county2 = County.objects.create(name="Arua", district=self.district2)
        self.sub_county2 = SubCounty.objects.create(name="Dadamu", county=self.county2)
        self.parish2 = Parish.objects.create(name="Yapi", sub_county=self.sub_county2)
        self.village2 = Village.objects.create(name="Abira", parish=self.parish2)

    def test_import_org_units(self):
        """
        Test importation of org units
        """
        book = Workbook()
        sheet1 = book.add_sheet('Sheet 1')
        excel_sheet = SHEET_FILES_FOLDER + 'simple' + str(random.randint(1000, 9999)) + '.xls'

        data = [
            ["Arua", "Arua", "Arua", "Arua", "Arua"],
            ["Arua", "Arua", "Arua", "Arua", "Arua"],
            ["Adumi", "Manibe", "Offaka", "Oli River", "Pajulu"],
            ["Anyara", "Eleku", "Adroa", "Kenya", "Adalafu"],
            ["Adroce", "Adravu", "Adroa", "Adriko", "Ajiriva"]
        ]

        for c_index, columns in enumerate(data):
            for r_index, row_item in enumerate(columns):
                sheet1.write(r_index, c_index, row_item)

        book.save(excel_sheet)
        book.save(TemporaryFile())

        extract_excel_org_unit_data(excel_sheet)
        self.assertEqual(District.objects.count(), 1)
        self.assertEqual(County.objects.count(), 1)
        self.assertEqual(SubCounty.objects.count(), 6)
        self.assertEqual(Parish.objects.count(), 6)
        self.assertEqual(Village.objects.count(), 6)
        self.assertEqual(Village.objects.last().name, "Ajiriva")

    def test_import_users(self):
        """
        Test importation of users
        Acceptance criterion:
        - User should be created only once
        - Hospital HC should have facility level of 0
        - Users with multiple last names must be concatenated while creating a username
        - Only girls who are pregnant should receive the sms messages
        """
        book = Workbook()
        sheet1 = book.add_sheet('Sheet 1')
        excel_sheet = SHEET_FILES_FOLDER + 'simple' + str(random.randint(1000, 9999)) + '.xls'

        data = [
            ["Rita", "Joshua", "Noah", "Peter", "Abraham"],
            ["Namakula", "Mukasa", "Okoth", "Opio", "Ibanda Mugada"],
            ["0756878450", "0756878451", "0756878452", "0756878453", "0756878454"],
            ["0756878440", "0756878441", "0756878442", "0756878443", "0756878444"],
            ["chew", "chew", "midwife", "chew", "midwife"],
            ["female", "female", "female", "female", "male"],
            ["Bondo HCIII", "Bondo HCII", "Arua Hospital", "Orivu HCIII", "Pajulu HCIII"],
            ["Dadamu", "Dadamu", "Dadamu", "Dadamu", "Dadamu"],
        ]

        for c_index, columns in enumerate(data):
            for r_index, row_item in enumerate(columns):
                sheet1.write(r_index, c_index, row_item)

        book.save(excel_sheet)
        book.save(TemporaryFile())

        extract_excel_user_data(excel_sheet, "Arua")
        self.assertEqual(User.objects.filter(role=USER_TYPE_CHEW).count(), 3)
        self.assertEqual(User.objects.filter(role=USER_TYPE_MIDWIFE).count(), 2)
        self.assertEqual(User.objects.last().last_name, "Namakula")
        self.assertEqual(User.objects.first().username, "aibandamugada")
        self.assertEqual(User.objects.first().gender, GENDER_MALE)
        self.assertEqual(User.objects.first().health_facility.name, "Pajulu HCIII")
        self.assertEqual(User.objects.first().health_facility.facility_level, '3')
        self.assertEqual(HealthFacility.objects.count(), 5)
        self.assertEqual(HealthFacility.objects.filter(facility_level='0').count(), 1)
