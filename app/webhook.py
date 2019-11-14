import json
import traceback
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Girl, County, SubCounty, Parish, Village, FollowUp, Delivery, MappingEncounter, \
    Appointment, AppointmentEncounter, Referral, FamilyPlanning, Observation
from app.serializers import User

import logging

from app.utils.constants import FOLLOW_UP_FORM_CHEW_NAME, APPOINTMENT_FORM_CHEW_NAME, \
    MAP_GIRL_BUNDIBUGYO_MIDWIFE_FORM_NAME, APPOINTMENT_FORM_MIDWIFE_NAME, FOLLOW_UP_FORM_MIDWIFE_NAME, USER_TYPE_CHEW, \
    MAP_GIRL_BUNDIBUGYO_CHEW_FORM_NAME, POSTNATAL_FORM_CHEW_NAME, POSTNATAL_FORM_MIDWIFE_NAME, ATTENDED, \
    HEALTH_FACILITY, PRE, POST

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

        if MAP_GIRL_BUNDIBUGYO_CHEW_FORM_NAME in json_result or MAP_GIRL_BUNDIBUGYO_MIDWIFE_FORM_NAME in json_result:
            print("mapping forms matched")
            return self.process_mapping_encounter(json_result, user_id)
        elif FOLLOW_UP_FORM_CHEW_NAME in json_result or FOLLOW_UP_FORM_MIDWIFE_NAME in json_result:
            return self.process_follow_up_and_delivery_encounter(girl_id, json_result, user_id)
        elif APPOINTMENT_FORM_CHEW_NAME in json_result or APPOINTMENT_FORM_MIDWIFE_NAME in json_result:
            return self.process_appointment_encounter(girl_id, json_result, user_id)
        elif POSTNATAL_FORM_CHEW_NAME in json_result or POSTNATAL_FORM_MIDWIFE_NAME in json_result:
            return self.postnatal_encounter(girl_id, json_result, user_id)
        return Response({'result': 'failure'}, 400)

    def process_mapping_encounter(self, json_result, user_id):
        print("process mapping encounter")

        try:
            try:
                mapped_girl_object = json_result[MAP_GIRL_BUNDIBUGYO_MIDWIFE_FORM_NAME]
            except KeyError:
                print(traceback.print_exc())
                mapped_girl_object = json_result[MAP_GIRL_BUNDIBUGYO_CHEW_FORM_NAME]

            next_of_kin_number = None
            voucher_number = 0
            attended_anc_visit = False
            bleeding = False
            fever = False
            swollenfeet = False
            blurred_vision = False
            mapping_encounter = MappingEncounter()

            demographic1 = mapped_girl_object["GirlDemographic"][0]
            first_name = demographic1["FirstName"][0]
            last_name = demographic1["LastName"][0]
            girls_phone_number = demographic1["GirlsPhoneNumber"][0]
            dob = demographic1["DOB"][0]

            try:
                demographic2 = mapped_girl_object["GirlDemographic2"][0]
                next_of_kin_number = demographic2["NextOfKinNumber"][0]
            except Exception as e:
                print(e)

            girl_location = mapped_girl_object["GirlLocation"][0]
            county = County.objects.filter(name__icontains=girl_location["county"][0])
            subcounty = SubCounty.objects.filter(name__icontains=girl_location["subcounty"][0])
            parish = Parish.objects.filter(name__icontains=girl_location["parish"][0])

            village = Village.objects.get(name__icontains=girl_location["village"][0])

            observations3 = mapped_girl_object["Observations3"][0]
            marital_status = observations3["marital_status"][0]
            education_level = observations3["education_level"][0]
            last_menstruation_date = observations3["MenstruationDate"][0]

            try:
                observations1 = mapped_girl_object["Observations1"][0]
                bleeding = observations1["bleeding"][0] == "yes"
                fever = observations1["fever"][0] == "yes"

                observations2 = mapped_girl_object["Observations2"][0]
                swollenfeet = observations2["swollenfeet"][0] == "yes"
                blurred_vision = observations2["blurred_vision"][0] == "yes"
            except Exception:
                print(traceback.print_exc())

            try:
                voucher_card_group = mapped_girl_object["VouncherCardGroup"][0]
                has_voucher_card = voucher_card_group["VoucherCard"][0] == "yes"
                if has_voucher_card:
                    voucher_number = int(voucher_card_group["VoucherNumber"][0])
            except KeyError or IndexError:
                print(traceback.print_exc())

            print("save form data")

            user = User.objects.get(id=user_id)
            print(user)

            girl = Girl(first_name=first_name, last_name=last_name, village=village,
                        phone_number=girls_phone_number, user=user,
                        next_of_kin_phone_number=next_of_kin_number, education_level=education_level, dob=dob,
                        marital_status=marital_status, last_menstruation_date=last_menstruation_date)
            girl.save()

            try:
                # incase girl who has already had ANC visit is mapped by midwife
                # save that date and create an anc visit
                anc_previous_group = mapped_girl_object["ANCAppointmentPreviousGroup"][0]
                attended_anc_visit = anc_previous_group["AttendedANCVisit"][0] == "yes"
                print("attended anc visit " + str(attended_anc_visit))

                if attended_anc_visit:
                    previous_appointment_date = anc_previous_group["ANCDatePrevious"][0]
                    # assume that a previous ANC appointment was attended
                    appointment = Appointment(girl=girl, user=user, date=previous_appointment_date, status=ATTENDED)
                    appointment.save()
                    self.auto_generate_appointment(girl, user, previous_appointment_date)
                else:
                    self.auto_generate_appointment(girl, user)
            except Exception:
                print(traceback.print_exc())

            try:
                anc_group = mapped_girl_object["ANCAppointmentGroup"][0]
                next_appointment_date = anc_group["ANCDate"][0]
                appointment = Appointment(girl=girl, user=user, date=next_appointment_date)
                appointment.save()
            except Exception:
                print(traceback.print_exc())

            observation = Observation(blurred_vision=blurred_vision, bleeding_heavily=bleeding, fever=fever,
                                      swollen_feet=swollenfeet)
            observation.save()

            mapping_encounter.observation = observation
            mapping_encounter.attended_anc_visit = attended_anc_visit
            mapping_encounter.voucher_card = voucher_number
            mapping_encounter.odk_instance_id = attended_anc_visit
            mapping_encounter.attended_anc_visit = attended_anc_visit
            mapping_encounter.user = user
            mapping_encounter.girl = girl
            mapping_encounter.save()
            self.save_family_planning_methods_in_mapping_encounter(mapped_girl_object, mapping_encounter)
            return Response({'result': 'success'}, 200)
        except Exception:
            print(traceback.print_exc())
        return Response({'result': 'failure'}, 400)

    def save_family_planning_methods_in_mapping_encounter(self, mapped_girl_object, mapping_encounter):
        try:
            contraceptive_group = mapped_girl_object["ContraceptiveGroup"][0]
            used_contraceptives = contraceptive_group["UsedContraceptives"][0] == "yes"
            if used_contraceptives:
                contraceptive_method = str(contraceptive_group["ContraceptiveMethod"][0])
                print("contraceptive method " + contraceptive_method)
                if " " in contraceptive_method:
                    contraceptive_method_names = contraceptive_method.split(" ")
                    for contraceptive_method_name in contraceptive_method_names:
                        if "Others" == contraceptive_method_name:
                            print("others present")
                            other_contraceptive_method = contraceptive_group["other_contraceptive_method"][0]
                            family_planning = FamilyPlanning(method=other_contraceptive_method, status=PRE)
                            family_planning.save()
                            mapping_encounter.family_planning.add(family_planning)
                        else:
                            family_planning = FamilyPlanning(method=contraceptive_method_name, status=PRE)
                            family_planning.save()
                            mapping_encounter.family_planning.add(family_planning)
                else:
                    family_planning = FamilyPlanning(method=contraceptive_method, status=PRE)
                    family_planning.save()
                    mapping_encounter.family_planning.add(family_planning)
            else:
                print("no contraceptive")
                no_family_planning_reason = contraceptive_group["ReasonNoContraceptives"][0]
                family_planning = FamilyPlanning(no_family_planning_reason=no_family_planning_reason,
                                                 using_family_planning=False)
                family_planning.save()
                mapping_encounter.family_planning.add(family_planning)
        except KeyError or IndexError as e:
            print(e)

    def auto_generate_appointment(self, girl, user, previous_appointment_date=None):
        pass

    def process_follow_up_and_delivery_encounter(self, girl_id, json_result, user_id):
        try:

            try:
                follow_up_object = json_result[FOLLOW_UP_FORM_CHEW_NAME]
            except Exception:
                print(traceback.print_exc())
                follow_up_object = json_result[FOLLOW_UP_FORM_MIDWIFE_NAME]
            print(follow_up_object)

            fever = False
            swollenfeet = False
            bleeding = False
            blurred_vision = False

            try:
                # captured in chew follow up
                observations1 = follow_up_object["observations1"][0]
                bleeding = observations1["bleeding"][0] == "yes"
                fever = observations1["fever"][0] == "yes"

                observations2 = follow_up_object["observations2"][0]
                swollenfeet = observations2["swollenfeet"][0] == "yes"
                blurred_vision = observations2["blurred_vision"][0] == "yes"
            except Exception:
                print(traceback.print_exc())

            action_taken_group = follow_up_object["action_taken_by_health_person_group"][0]
            action_taken_by_health_person = action_taken_group["action_taken_by_health_person"][0]

            girl = Girl.objects.get(id=girl_id)
            user = User.objects.get(id=user_id)

            if action_taken_by_health_person == "appointment":
                print("action taken appointment")
                next_appointment = follow_up_object["schedule_appointment_group"][0]["schedule_appointment"][0]
                appointment = Appointment(girl=girl, user=user, date=next_appointment)
                appointment.save()
            elif action_taken_by_health_person == "delivery":
                print("action taken delivery")
                self.save_delivery(follow_up_object, girl, user)
            else:
                referral = Referral(girl=girl, user=user, reason="critical")
                referral.save()

            print('save results')

            observation = Observation(blurred_vision=blurred_vision, bleeding_heavily=bleeding, fever=fever,
                                      swollen_feet=swollenfeet)
            observation.save()

            follow_up = FollowUp(girl=girl, user=user, follow_up_action_taken=action_taken_by_health_person)
            follow_up.observation = observation
            follow_up.save()
            return Response({'result': 'success'}, 200)
        except Exception:
            print(traceback.print_exc())
        return Response({'result': 'failure'}, 400)

    def save_delivery(self, follow_up_object, girl, user):
        print("action taken delivery")
        baby_birth_date = ""
        baby_death_date = ""
        mother_death_date = ""
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
        if birth_place == "HealthFacility":
            birth_place = "Health facility"
        delivery_action_taken = delivery_follow_up_group["action_taken"][0]
        contraceptive_group = follow_up_object["family_planning_group"][0]
        postnatal_care = contraceptive_group["postnatal_received"][0] == "yes"
        used_contraceptives = contraceptive_group["family_planning"][0] == "yes"

        print('save delivery')
        delivery = Delivery(girl=girl, user=user, action_taken=delivery_action_taken,
                            postnatal_care=postnatal_care, mother_alive=mother_alive, baby_alive=baby_alive,
                            delivery_location=birth_place)

        if baby_birth_date:
            delivery.baby_birth_date = baby_birth_date
        else:
            delivery.baby_death_date = baby_death_date
        if mother_death_date:
            delivery.mother_death_date = mother_death_date
        delivery.save()

        self.save_family_planning_methods_in_delivery(contraceptive_group, delivery, used_contraceptives)

    def save_family_planning_methods_in_delivery(self, contraceptive_group, delivery, used_contraceptives):
        try:
            if used_contraceptives:
                contraceptive_method = str(contraceptive_group["ContraceptiveMethod"][0])
                print("contraceptive method " + contraceptive_method)
                if " " in contraceptive_method:
                    contraceptive_method_names = contraceptive_method.split(" ")
                    for contraceptive_method_name in contraceptive_method_names:
                        if "Others" == contraceptive_method_name:
                            print("others present")
                            other_contraceptive_method = contraceptive_group["other_contraceptive_method"][0]
                            family_planning = FamilyPlanning(method=other_contraceptive_method, status=POST)
                            family_planning.save()
                            delivery.family_planning.add(family_planning)
                        else:
                            family_planning = FamilyPlanning(method=contraceptive_method_name, status=POST)
                            family_planning.save()
                            delivery.family_planning.add(family_planning)
                else:
                    family_planning = FamilyPlanning(method=contraceptive_method, status=POST)
                    family_planning.save()
                    delivery.family_planning.add(family_planning)
            else:
                print("no contraceptive")
                no_family_planning_reason = contraceptive_group["ReasonNoContraceptives"][0]
                family_planning = FamilyPlanning(no_family_planning_reason=no_family_planning_reason,
                                                 using_family_planning=False)
                family_planning.save()
                delivery.family_planning.add(family_planning)
        except KeyError or IndexError as e:
            print(e)

    def process_appointment_encounter(self, girl_id, json_result, user_id):
        try:
            try:
                appointment_object = json_result[APPOINTMENT_FORM_CHEW_NAME]
            except Exception:
                print(traceback.print_exc())
                appointment_object = json_result[APPOINTMENT_FORM_MIDWIFE_NAME]

            needed_ambulance = False
            used_ambulance = False
            missed_anc_reason = ""
            appointment_method = ""
            fever = False
            swollenfeet = False
            bleeding = False
            blurred_vision = False

            try:
                # captured in midwife appointment
                ambulance_group = appointment_object["ambulance_group"][0]
                needed_ambulance = ambulance_group["needed_ambulance"][0] == "yes"
                used_ambulance = ambulance_group["used_ambulance"][0] == "yes"
            except Exception:
                print(traceback.print_exc())

            missed_anc_before_group = appointment_object["missed_anc_before_group"][0]
            missed_anc_before = missed_anc_before_group["missed_anc_before"][0] == "yes"

            if missed_anc_before:
                missed_anc_before_group2 = appointment_object["missed_anc_before_group2"][0]
                missed_anc_reason = missed_anc_before_group2["missed_anc_reason"][0]
                if missed_anc_reason == "Other":
                    missed_anc_reason = missed_anc_before_group2["missed_anc_reason_other"][0]
            else:
                missed_anc_reason = appointment_object["appointment_soon_group"][0]
                appointment_method = missed_anc_reason["appointment_method"][0]

                try:
                    # captured in chew appointment
                    observations1 = appointment_object["observations1"][0]
                    bleeding = observations1["bleeding"][0] == "yes"
                    fever = observations1["fever"][0] == "yes"

                    observations2 = appointment_object["observations2"][0]
                    swollenfeet = observations2["swollenfeet"][0] == "yes"
                    blurred_vision = observations2["blurred_vision"][0] == "yes"
                except Exception:
                    print(traceback.print_exc())

            action_taken_group = appointment_object["action_taken_group"][0]
            action_taken = action_taken_group["action_taken_meeting_girl"][0]

            schedule_appointment_group = appointment_object["schedule_appointment_group"][0]
            next_appointment_date = schedule_appointment_group["schedule_appointment"][0]

            girl = Girl.objects.get(id=girl_id)
            user = User.objects.get(id=user_id)

            observation = Observation(blurred_vision=blurred_vision, bleeding_heavily=bleeding, fever=fever,
                                      swollen_feet=swollenfeet)
            observation.save()

            appointment = Appointment(girl=girl, user=user, date=next_appointment_date)
            appointment.save()

            appointment_encounter = AppointmentEncounter(used_ambulance=used_ambulance,
                                                         needed_ambulance=needed_ambulance,
                                                         missed_anc_reason=missed_anc_reason,
                                                         action_taken=action_taken,
                                                         appointment_method=appointment_method,
                                                         missed_anc_before=missed_anc_before, appointment=appointment)
            appointment_encounter.observation = observation
            appointment_encounter.save()
            return Response({'result': 'success'}, 200)
        except Exception:
            print(traceback.print_exc())
        return Response({'result': 'failure'}, 400)

    def postnatal_encounter(self, girl_id, json_result, user_id):
        print("postnatal counter")

        try:
            postnatal_object = json_result[POSTNATAL_FORM_CHEW_NAME]
        except Exception:
            print(traceback.print_exc())
            postnatal_object = json_result[POSTNATAL_FORM_MIDWIFE_NAME]
        print(postnatal_object)

        girl = Girl.objects.get(id=girl_id)
        user = User.objects.get(id=user_id)

        self.save_delivery(postnatal_object, girl, user)
        return Response()
