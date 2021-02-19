import traceback

import pytz
import xlrd
from django.db.models import Q
from django.utils import timezone

from GetInBackendRebuild.settings import SHEET_FILES_FOLDER
from app.airtime_dispatcher import AirtimeModule
from app.models import District, County, SubCounty, Parish, Village, User, Girl, Appointment, FollowUp, HealthFacility
from app.utils.utilities import add_months
from openpyxl import Workbook, load_workbook
from app.utils.constants import *
from django.db.models.expressions import F, Q, ExpressionWrapper
from django.db.models import Sum, Case, Value, When, Avg, FloatField, IntegerField, Count


def extract_excel_org_unit_data(location):
    """
    :param location: uri of the excel file to extract from. Usually excel files are placed in the sheets folder
    Creates org units from an excel sheet provided
    Sheet Fields: District, County, SubCounty, Parish, Village
    Note: Some districts don't have county. In that case the district name is used as a county
    """
    wb = xlrd.open_workbook(location)
    sheet = wb.sheet_by_index(0)

    sheet.cell_value(0, 0)

    for row_number in range(0, 1000):
        try:
            row_data = sheet.row_values(row_number)
        except Exception as e:
            print(e)
            break

        print(row_data)
        district_value = row_data[0]
        county_value = row_data[1]
        sub_county_value = row_data[2]
        parish_value = row_data[3]
        village_value = row_data[4]

        if not district_value:
            break

        if str(district_value).lower() == 'district':
            continue
        district = District.objects.get_or_create(name=district_value)
        county = County.objects.get_or_create(name=county_value, district=district[0])
        sub_county = SubCounty.objects.get_or_create(name=sub_county_value, county=county[0])
        parish = Parish.objects.get_or_create(name=parish_value, sub_county=sub_county[0])
        village = Village.objects.get_or_create(name=village_value, parish=parish[0])


def extract_excel_user_data(location, district_name):
    """
    :param location: uri of the excel file of users to extract from. Usually excel files are placed in the sheets folder
    :param district_name: district where these users will be created
    Creates user accounts from an excel sheet provided
    Sheet Fields: FirstName, LastName, Personal PhoneNumber, GetIn PhoneNumber, Role, Gender, HealthCenter, SubCounty
    """
    wb = xlrd.open_workbook(location)
    sheet = wb.sheet_by_index(0)
    sheet.cell_value(0, 0)

    for row_number in range(0, 1000):
        try:
            row_data = sheet.row_values(row_number)
        except Exception as e:
            print(e)
            break

        first_name_value = row_data[0]
        last_name_value = row_data[1]
        getin_number_value = int(row_data[3])
        role = row_data[4]
        gender = row_data[5]
        health_facility = row_data[6]
        sub_county = row_data[7]

        if not first_name_value:
            break

        try:
            sub_county = SubCounty.objects.get(name__contains=sub_county)
            village = sub_county.parish_set.first().village_set.first()
        except Exception as e:
            print(e)
            sub_county = District.objects.get(name__icontains=district_name).county_set.last() \
                .subcounty_set.last()
            village = sub_county.parish_set.last().village_set.last()

        try:
            health_facility, _ = HealthFacility.objects.get_or_create(name=health_facility, sub_county=sub_county,
                                                                      facility_level=len(
                                                                          health_facility.split("HC")[1]))
        except Exception as e:
            print(e)
            health_facility, _ = HealthFacility.objects.get_or_create(name=health_facility, sub_county=sub_county,
                                                                      facility_level='0')

        try:
            getin_number_value = "0" + str(int(getin_number_value))
            user = User(first_name=first_name_value.strip(), village=village, last_name=last_name_value.strip(),
                        username=str(first_name_value.strip()).lower()[0] + str(last_name_value.strip()).lower().replace(" ", ""),
                        email=first_name_value + last_name_value + "@getinmobile.org", phone=getin_number_value.strip(),
                        health_facility=health_facility,
                        gender=GENDER_FEMALE if gender.lower().find("f") > -1 else GENDER_MALE,
                        role=USER_TYPE_CHEW if str(role).lower().find("vht") > -1 else str(role).lower())
            user.set_password(getin_number_value)
            user.save()
        except Exception:
            print(traceback.print_exc())


def generate_monthly_system_stats():
    for district in District.objects.all():
        created_at = timezone.datetime(2019, 10, 1).replace(tzinfo=pytz.utc)
        while created_at < timezone.datetime(2020, 12, 1).replace(tzinfo=pytz.utc):
            for user in User.objects.filter(district=district):
                if user.role in [USER_TYPE_DHO, USER_TYPE_AMBULANCE, USER_TYPE_DEVELOPER]:
                    continue
                girls = Girl.objects.filter(Q(created_at__gte=created_at) &
                                            Q(created_at__lte=add_months(created_at, 1)
                                              .replace(tzinfo=pytz.utc)) & Q(user=user)).count()
                filename = SHEET_FILES_FOLDER + "GetIN Traceability Form.xlsx"
                wb = load_workbook(filename)
                sheet = wb['Sheet1']

                appointment_data = {
                    "attended": 0,
                    "expected": 0,
                    "missed": 0
                }

                if user.role == USER_TYPE_MIDWIFE:
                    appointment_data = Appointment.objects.filter(Q(user=user) & Q(created_at__gte=created_at) &
                                                                  Q(created_at__lte=add_months(created_at, 1)
                                                                    .replace(tzinfo=pytz.utc))).aggregate(
                        attended=Count(Case(
                            When(Q(status=ATTENDED), then=1),
                            output_field=IntegerField(),
                        )),
                        expected=Count(Case(
                            When(Q(status=EXPECTED), then=1),
                            output_field=IntegerField(),
                        )),
                        missed=Count(Case(
                            When(Q(status=MISSED), then=1),
                            output_field=IntegerField(),
                        ))
                    )

                followups = FollowUp.objects.filter(Q(user=user) & Q(created_at__gte=created_at) &
                                                    Q(created_at__lte=add_months(created_at, 1).replace(
                                                        tzinfo=pytz.utc))).count()

                sheet.append([user.first_name + " " + user.last_name, user.phone, user.role, district.name,
                              created_at.strftime("%B"), created_at.strftime("%Y"), girls, appointment_data['attended'],
                              appointment_data['expected'],
                              appointment_data['missed'], followups])
                wb.save(filename)
            created_at = add_months(created_at, 1).replace(tzinfo=pytz.utc)


def extract_excel_user_data_for_airtime_dispatchment(location, amount):
    """
    Sends airtime to users GetIN phone numbers
    """
    wb = xlrd.open_workbook(location)
    sheet = wb.sheet_by_index(0)

    sheet.cell_value(0, 0)
    phone_numbers = []

    for row_number in range(0, sheet.utter_max_rows):
        try:
            row_data = sheet.row_values(row_number)
            phone_numbers.append("+256" + str(int(row_data[0])))
        except Exception as e:
            print(e)

    print(phone_numbers)
    print(len(phone_numbers))
    airtime = AirtimeModule()
    airtime.send_airtime(phone_numbers, amount)


def generate_user_credential_sheet(district_name):
    for user in User.objects.filter(district__name=district_name):
        girls = Girl.objects.filter(user=user).count()
        filename = SHEET_FILES_FOLDER + "GetIN User Credentials.xlsx"
        wb = load_workbook(filename)
        sheet = wb['Sheet1']
        sheet.append([user.first_name + " " + user.last_name, user.username, user.phone, user.role, girls])
        wb.save(filename)
