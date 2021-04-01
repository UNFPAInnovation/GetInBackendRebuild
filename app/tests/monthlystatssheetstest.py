import xlrd
from django.utils import timezone

from GetInBackendRebuild.settings import SHEET_FILES_FOLDER
from app.extractor import generate_monthly_system_stats
from app.models import District, User
from app.tests import ParentTest
from app.utils.constants import USER_TYPE_CHEW, USER_TYPE_MIDWIFE


class TestMonthlyStats(ParentTest):
    def test_generate_monthly_system_stats(self):
        """
        Test creation of user performance excel sheet
        Acceptance criterion:
        - The user in the last row should be the the first created user
        - The month in the last row should be the month of the end_date
        """
        filename = SHEET_FILES_FOLDER + 'GetIN Traceability Form ' + \
                   str(timezone.now().strftime("%m-%d-%Y-%H:%M")) + '.xls'
        generate_monthly_system_stats(location=filename)
        wb = xlrd.open_workbook(filename + 'x')
        sheet = wb.sheet_by_index(0)
        name = ""
        month = ""

        for row_number in range(0, 1000):
            try:
                row_data = sheet.row_values(row_number)
            except Exception as e:
                print(e)
                break
            name = row_data[0]
            month = row_data[4]

        first_user = User.objects.filter(district=District.objects.last(),
                                         role__in=[USER_TYPE_MIDWIFE, USER_TYPE_CHEW]).last()
        self.assertEqual(name, first_user.first_name + " " + first_user.last_name)
        self.assertEqual(month, timezone.now().strftime("%B"))
