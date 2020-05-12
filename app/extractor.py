import traceback

import pytz
#import xlrd
from django.db.models import Q
from django.utils import timezone

from app.models import District, County, SubCounty, Parish, Village, User, Girl
from app.utils.utilities import add_months
from openpyxl import Workbook, load_workbook
from openpyxl.utils.dataframe import dataframe_to_rows


def extract_excel_data(location):
    wb = xlrd.open_workbook(location)
    sheet = wb.sheet_by_index(0)

    sheet.cell_value(0, 0)

    print(sheet.row_values(10))
    print(sheet.row_values(10)[0])
    print(sheet.utter_max_rows)

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
        print(district_value + county_value + sub_county_value + parish_value + village_value)
        print(row_number)

        if not district_value:
            break

        try:
            district = District.objects.get(name=district_value)
        except Exception as e:
            print(e)
            district = District(name=district_value)
            district.save()

        try:
            county = County.objects.get(name=county_value)
        except Exception as e:
            print(e)
            county = County(name=county_value, district=district)
            county.save()

        try:
            sub_county = SubCounty.objects.get(name=sub_county_value)
        except Exception as e:
            print(e)
            sub_county = SubCounty(name=sub_county_value, county=county)
            sub_county.save()

        try:
            parish = Parish.objects.get(name=parish_value)
        except Exception as e:
            print(e)
            parish = Parish(name=parish_value, sub_county=sub_county)
            parish.save()

        try:
            village = Village.objects.get(name=village_value)
        except Exception as e:
            print(e)
            village = Village(name=village_value, parish=parish)
            village.save()


def extract_excel_user_data(location):
    wb = xlrd.open_workbook(location)
    sheet = wb.sheet_by_index(1)

    sheet.cell_value(0, 0)

    print(sheet.utter_max_rows)

    village = Village.objects.get(id=303)

    for row_number in range(0, 1000):
        try:
            row_data = sheet.row_values(row_number)
        except Exception as e:
            print(e)
            break

        print(row_data)
        first_name_value = row_data[0]
        last_name_value = row_data[1]
        personal_number = int(row_data[2])
        getin_number_value = int(row_data[3])
        role = row_data[4]
        print(first_name_value + last_name_value + str(personal_number) + str(getin_number_value) + role)

        print(row_number)

        if not first_name_value:
            break

        try:
            role = str(role).lower()
            getin_number_value = "0" + str(int(getin_number_value))
            print(getin_number_value)
            print(first_name_value)
            print(last_name_value)
            user = User(first_name=first_name_value, village=village, last_name=last_name_value,
                        username=str(first_name_value).lower()[0] + str(last_name_value).lower(),
                        email=first_name_value + last_name_value + "@getinmobile.org", phone=getin_number_value,
                        role=str(role).lower())
            user.set_password(getin_number_value)
            user.save()
        except Exception:
            print(traceback.print_exc())


def extract_excel_user_data_from_sheet(location):
    wb = xlrd.open_workbook(location)
    sheet = wb.sheet_by_index(0)

    sheet.cell_value(0, 0)

    print(sheet.utter_max_rows)

    for row_number in range(0, 1000):
        try:
            row_data = sheet.row_values(row_number)
        except Exception as e:
            print(e)
            break

        if row_number == 0:
            continue

        print(row_data)
        first_name_value = row_data[0]
        last_name_value = row_data[1]
        personal_number = int(row_data[2])
        getin_number_value = int(row_data[3])
        role = row_data[4]
        sub_county = row_data[5]
        username = row_data[6]
        print(first_name_value + last_name_value + str(personal_number) + str(getin_number_value) + role)

        print(row_number)

        if not first_name_value:
            break

        try:
            subcounty = SubCounty.objects.get(name=sub_county)
            village = subcounty.parish_set.first().village_set.first()
        except Exception as e:
            print(e)
            village = Village.objects.get(id=144)

        try:
            role = str(role).lower()
            getin_number_value = "0" + str(int(getin_number_value))
            print(getin_number_value)
            print(first_name_value)
            print(last_name_value)
            user = User(first_name=first_name_value, village=village, last_name=last_name_value,
                        username=str(username).lower(),
                        email=username + "@getinmobile.org", phone=getin_number_value, role=str(role).lower())
            user.set_password(getin_number_value)
            user.save()
        except Exception:
            print(traceback.print_exc())


def generate_system_user_stats():
    for district in District.objects.all():
        created_at = timezone.datetime(2019, 11, 1).replace(tzinfo=pytz.utc)
        while created_at < timezone.datetime(2020, 4, 1).replace(tzinfo=pytz.utc):
            for user in User.objects.filter(district=district):
                girls = Girl.objects.filter(Q(created_at__gte=created_at) &
                                            Q(created_at__lte=add_months(created_at, 1)
                                              .replace(tzinfo=pytz.utc)) & Q(user=user)).count()
                filename = "/home/codephillip/PycharmProjects/GetInBackendRebuild/GetIN Traceability Form.xlsx"
                wb = load_workbook(filename)
                sheet = wb['Sheet1']
                sheet.append([user.first_name + " " + user.last_name, user.phone, user.role, district.name,
                              created_at.strftime("%B"), girls])
                wb.save(filename)
            created_at = add_months(created_at, 1).replace(tzinfo=pytz.utc)
