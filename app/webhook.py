import json
import traceback
from datetime import datetime

from django.utils import timezone
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Girl, District, County, SubCounty, Parish, Village, FollowUp, Delivery, MappingEncounter, \
    Appointment, AppointmentEncounter
from app.serializers import User

import logging

from app.utils.constants import MAP_GIRL_FORM_NAME, FOLLOW_UP_FORM_NAME, APPOINTMENT_FORM_NAME, \
    MAP_GIRL_BUNDIBUGYO_FORM_NAME

logger = logging.getLogger('testlogger')


class MappingEncounterWebhook(APIView):
    """
    Receives the mapping encounter data and then creates the Girl model and MappingEncounter model
    """

    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        print("post request called")
        # todo replace with proper form ids
        json_result = request.data
        print(json_result)

        if type(json_result) != dict:
            print('not dict')
            json_result = str(json_result).replace('\'', "\"")
            json_result = json.loads(json_result)

        form_meta_data = json_result["form_meta_data"]
        print(form_meta_data)
        form_meta_data = json.loads(form_meta_data)
        try:
            girl_id = form_meta_data["GIRL_ID"]
        except KeyError:
            print(traceback.print_exc())

        try:
            user_id = form_meta_data["USER_ID"]
            print('user id')
            print(user_id)
        except KeyError:
            print(traceback.print_exc())

        if MAP_GIRL_FORM_NAME in json_result or MAP_GIRL_BUNDIBUGYO_FORM_NAME in json_result:
            return self.process_mapping_encounter(json_result, user_id)
        elif FOLLOW_UP_FORM_NAME in json_result:
            return self.process_follow_up_and_delivery_encounter(girl_id, json_result, user_id)
        elif APPOINTMENT_FORM_NAME in json_result:
            return self.process_appointment_encounter(girl_id, json_result, user_id)
        return Response({'result': 'failure'}, 400)

    def process_mapping_encounter(self, json_result, user_id):
        print("process mapping encounter")
        try:
            try:
                mapped_girl_object = json_result.get(MAP_GIRL_FORM_NAME)
                print(mapped_girl_object)
                print(type(mapped_girl_object))

                if mapped_girl_object is None:
                    mapped_girl_object = json_result.get(MAP_GIRL_BUNDIBUGYO_FORM_NAME)
                print(mapped_girl_object)
            except KeyError:
                print(traceback.print_exc())

            contraceptive_method = ""
            voucher_number = 0
            used_contraceptives = False
            no_family_planning_reason = ""

            demographic1 = mapped_girl_object["GirlDemographic"][0]
            first_name = demographic1["FirstName"][0]
            last_name = demographic1["LastName"][0]
            girls_phone_number = demographic1["GirlsPhoneNumber"][0]
            dob = demographic1["DOB"][0]

            demographic2 = mapped_girl_object["GirlDemographic2"][0]
            next_of_kin_number = demographic2["NextOfKinNumber"][0]
            next_of_kin_first_name = demographic2["NextOfKinFirstName"][0]
            next_of_kin_last_name = demographic2["NextOfKinLastName"][0]

            girl_location = mapped_girl_object["GirlLocation"][0]
            county = County.objects.filter(name__icontains=girl_location["county"][0])
            subcounty = SubCounty.objects.filter(name__icontains=girl_location["subcounty"][0])
            parish = Parish.objects.filter(name__icontains=girl_location["parish"][0])

            village = Village.objects.get(name__icontains=girl_location["village"][0])

            observations3 = mapped_girl_object["Observations3"][0]
            marital_status = observations3["marital_status"][0]
            education_level = observations3["education_level"][0]
            last_menstruation_date = observations3["MenstruationDate"][0]

            observations1 = mapped_girl_object["Observations1"][0]
            attended_anc_visit = observations1["AttendedANCVisit"][0] == "yes"
            bleeding = observations1["bleeding"][0] == "yes"
            fever = observations1["fever"][0] == "yes"

            observations2 = mapped_girl_object["Observations2"][0]
            swollenfeet = observations2["swollenfeet"][0] == "yes"
            blurred_vision = observations2["blurred_vision"][0] == "yes"

            try:
                contraceptive_group = mapped_girl_object["ContraceptiveGroup"][0]
                used_contraceptives = contraceptive_group["UsedContraceptives"][0] == "yes"
                if used_contraceptives:
                    contraceptive_group = mapped_girl_object["ContraceptiveGroup"][0]
                    contraceptive_method = contraceptive_group["ContraceptiveMethod"][0]
                else:
                    no_family_planning_reason = mapped_girl_object["ReasonNoContraceptives"][0]
            except KeyError or IndexError as e:
                print(e)

            try:
                voucher_card_group = mapped_girl_object["VouncherCardGroup"][0]
                has_voucher_card = voucher_card_group["VoucherCard"][0] == "yes"
                if has_voucher_card:
                    voucher_number = int(voucher_card_group["VoucherNumber"][0])
            except KeyError or IndexError:
                print(traceback.print_exc())

            anc_group = mapped_girl_object["ANCAppointmentGroup"][0]
            next_appointment = anc_group["ANCDate"][0]

            print("save form data")

            user = User.objects.get(id=user_id)
            print(user)

            girl = Girl(first_name=first_name, last_name=last_name, village=village,
                        phone_number=girls_phone_number, user=user,
                        next_of_kin_first_name=next_of_kin_first_name, next_of_kin_last_name=next_of_kin_last_name,
                        next_of_kin_phone_number=next_of_kin_number, education_level=education_level, dob=dob,
                        marital_status=marital_status, last_menstruation_date=last_menstruation_date)
            girl.save()

            mapping_encounter = MappingEncounter(girl=girl, user=user,
                                                 no_family_planning_reason=no_family_planning_reason,
                                                 using_family_planning=used_contraceptives,
                                                 bleeding_heavily=bleeding,
                                                 swollen_feet=swollenfeet,
                                                 family_planning_type=contraceptive_method,
                                                 attended_anc_visit=attended_anc_visit,
                                                 voucher_number=voucher_number,
                                                 fever=fever, blurred_vision=blurred_vision)
            mapping_encounter.save()

            appointment = Appointment(girl=girl, user=user, next_appointment=next_appointment)
            appointment.save()
            return Response({'result': 'success'}, 200)
        except Exception:
            print(traceback.print_exc())
        return Response({'result': 'failure'}, 400)

    def process_follow_up_and_delivery_encounter(self, girl_id, json_result, user_id):
        try:
            follow_up_object = json_result[FOLLOW_UP_FORM_NAME]
            print(follow_up_object)

            missed_anc_reason = ""
            anc_card = ""
            follow_up_reason = ""

            anc_group = follow_up_object["anc_group"][0]
            missed_anc = anc_group["missed_anc"][0] == "yes"
            try:
                if missed_anc:
                    missed_anc_reason = anc_group["missed_anc_reason"][0]
                    if missed_anc_reason == 'other':
                        missed_anc_reason = anc_group["missed_anc_reason_other"][0]
                else:
                    anc_card = anc_group["anc_card"][0]
            except TypeError or IndexError:
                print(traceback.print_exc())

            follow_up_reason = anc_group["follow_up_reason"][0]
            observations1 = follow_up_object["observations1"][0]
            bleeding = observations1["bleeding"][0] == "yes"
            fever = observations1["fever"][0] == "yes"

            observations2 = follow_up_object["observations2"][0]
            swollenfeet = observations2["swollenfeet"][0] == "yes"
            blurred_vision = observations2["blurred_vision"][0] == "yes"

            action_taken_group = follow_up_object["action_taken_group"][0]
            follow_up_action_taken = action_taken_group["action_taken_by_health_person"][0]

            next_appointment = ""
            baby_birth_date = ""
            baby_death_date = ""
            mother_death_date = ""
            no_family_planning_reason = ""

            girl = Girl.objects.get(id=girl_id)
            user = User.objects.get(id=user_id)
            follow_up_reason = "Reminder"

            if follow_up_action_taken == "appointment":
                follow_up_reason = "Set appointment"
                next_appointment = follow_up_object["schedule_appointment_group"][0]["schedule_appointment"][0]
                appointment = Appointment(girl=girl, user=user, next_appointment=next_appointment)
                appointment.save()
            elif follow_up_action_taken == "delivery":
                follow_up_reason = "Delivery"
                delivery_follow_up_group = follow_up_object["delivery_followup_group"][0]
                mother_alive = delivery_follow_up_group["mother_delivery_outcomes"][0] == "mother_alive"
                baby_alive = delivery_follow_up_group["baby_delivery_outcomes"][0] == "baby_alive"

                if baby_alive:
                    baby_birth_date = delivery_follow_up_group["baby_birth_date"][0]
                else:
                    baby_death_date = delivery_follow_up_group["baby_death_date"][0]

                if not mother_alive:
                    mother_death_date = delivery_follow_up_group["mother_death_date"][0]

                birth_place = delivery_follow_up_group["birth_place"][0]
                postnatal_care = delivery_follow_up_group["postnatal_received"][0] == "yes"
                used_contraceptives = delivery_follow_up_group["family_planning"][0] == "yes"
                contraceptive_method = delivery_follow_up_group["ContraceptiveMethod"][0]

                try:
                    if used_contraceptives:
                        contraceptive_method = delivery_follow_up_group["ContraceptiveMethod"][0]
                    else:
                        no_family_planning_reason = delivery_follow_up_group["ReasonNoContraceptives"][0]
                except TypeError or IndexError:
                    print(traceback.print_exc())

                action_taken = delivery_follow_up_group["action_taken"][0]

                delivery = Delivery(girl=girl, user=user, followup_reason=follow_up_reason,
                                    action_taken=action_taken, using_family_planning=used_contraceptives,
                                    postnatal_care=postnatal_care, mother_alive=mother_alive, baby_alive=baby_alive,
                                    delivery_location=birth_place, no_family_planning_reason=no_family_planning_reason)

                if next_appointment:
                    delivery.action_taken = next_appointment

                if baby_birth_date:
                    delivery.baby_birth_date = baby_birth_date
                else:
                    delivery.baby_death_date = baby_death_date

                if mother_death_date:
                    delivery.mother_death_date = mother_death_date

                if contraceptive_method:
                    delivery.family_planning_type = contraceptive_method

                delivery.save()

            follow_up = FollowUp(girl=girl, user=user, blurred_vision=blurred_vision, fever=fever,
                                 swollen_feet=swollenfeet, followup_reason=follow_up_reason,
                                 bleeding_heavily=bleeding)
            follow_up.save()
            return Response({'result': 'success'}, 200)
        except Exception:
            print(traceback.print_exc())
        return Response({'result': 'failure'}, 400)

    def process_appointment_encounter(self, girl_id, json_result, user_id):
        try:
            appointment_object = json_result[APPOINTMENT_FORM_NAME]
            risk_assessment_group = appointment_object["risk_assessment_group"][0]
            risks_identified = risk_assessment_group["risks_identified"][0]
            needed_ambulance = risk_assessment_group["needed_ambulance"][0] == "yes"

            missed_anc_before_group = appointment_object["missed_anc_before_group"][0]
            missed_anc_before = missed_anc_before_group["missed_anc_before"][0] == "yes"

            missed_anc_reason = ""
            if missed_anc_before:
                missed_anc_group = appointment_object["missed_anc_group"][0]
                missed_anc_reason = missed_anc_group["missed_anc_reason"][0]
                if not missed_anc_reason:
                    missed_anc_reason = missed_anc_group["missed_anc_other_reason"][0]

            action_taken_group = appointment_object["action_taken_group"][0]
            action_taken = action_taken_group["action_taken_meeting_girl"][0]
            next_appointment = action_taken_group["anc_date"][0]

            girl = Girl.objects.get(id=girl_id)
            user = User.objects.get(id=user_id)

            appointment = Appointment(girl=girl, user=user, next_appointment=next_appointment)
            appointment.save()

            appointment_encounter = AppointmentEncounter(girl=girl, user=user, risks_identified=risks_identified,
                                                         needed_ambulance=needed_ambulance,
                                                         missed_anc_reason=missed_anc_reason,
                                                         action_taken=action_taken,
                                                         missed_anc_before=missed_anc_before)
            appointment_encounter.save()
            return Response({'result': 'success'}, 200)
        except Exception:
            print(traceback.print_exc())
        return Response({'result': 'failure'}, 400)
