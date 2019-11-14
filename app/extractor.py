import xlrd

from app.models import District, County, SubCounty, Parish, Village


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
        print(district_value+county_value+sub_county_value+parish_value+village_value)
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
