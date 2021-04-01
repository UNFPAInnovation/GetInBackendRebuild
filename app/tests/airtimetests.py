import random

from django.urls import reverse
from rest_framework import status
from xlwt import Workbook

from GetInBackendRebuild.settings import SHEET_FILES_FOLDER
from app.airtime_dispatcher import AirtimeModule
from app.extractor import extract_excel_user_data_for_airtime_dispatchment
from app.models import *
from app.tests.parenttest import ParentTest


class TestAirtime(ParentTest):
    def test_phone_number_extraction_and_send_AT(self):
        """
        Acceptance criterion:
        - The phone numbers must start with international number +256
        - Invalid phone numbers must not receive airtime
        :return: list of phone numbers
        """
        book = Workbook()
        sheet1 = book.add_sheet('Sheet 1')
        location = SHEET_FILES_FOLDER + 'GetIN users airtime list' + str(random.randint(1000, 9999)) + '.xls'

        data = [
            ["0756878459", "0756878455", "0756878453", "0756878452", "0756878452"]
        ]

        for c_index, columns in enumerate(data):
            for r_index, row_item in enumerate(columns):
                print('row_item')
                print(row_item)
                sheet1.write(r_index, c_index, row_item)

        book.save(location)

        phone_numbers = extract_excel_user_data_for_airtime_dispatchment(location)
        # count is 4 because repeated numbers are merged
        self.assertEqual(len(phone_numbers), 4)

        airtime = AirtimeModule()
        response = airtime.send_airtime(phone_numbers, 500)
        self.assertEqual(response['numSent'], 4)

