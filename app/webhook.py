import datetime
import json
import random
import traceback

import pytz
import requests
from django.db.models import Q
from django.utils import timezone
from rest_framework import status
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.response import Response
from rest_framework.views import APIView

from app.models import Girl, Parish, Village, FollowUp, Delivery, MappingEncounter, \
    Appointment, AppointmentEncounter, Referral, FamilyPlanning, Observation, MSIService
from app.serializers import User, GirlMSISerializer, GirlMSIDateFormattedSerializer

import logging

from app.utils.constants import FOLLOW_UP_FORM_CHEW_NAME, APPOINTMENT_FORM_CHEW_NAME, \
    MAP_GIRL_BUNDIBUGYO_MIDWIFE_FORM_NAME, APPOINTMENT_FORM_MIDWIFE_NAME, FOLLOW_UP_FORM_MIDWIFE_NAME, USER_TYPE_CHEW, \
    MAP_GIRL_BUNDIBUGYO_CHEW_FORM_NAME, POSTNATAL_FORM_CHEW_NAME, POSTNATAL_FORM_MIDWIFE_NAME, ATTENDED, \
    PRE, POST, EXPECTED, MAP_GIRL_ARUA_CHEW_FORM_NAME, MAP_GIRL_ARUA_MIDWIFE_FORM_NAME, MAP_GIRL_KAMPALA_CHEW_FORM_NAME, \
    MAP_GIRL_KAMPALA_MIDWIFE_FORM_NAME, DEFAULT_TAG, MSI_BASE_URL, MSI_TOKEN

logger = logging.getLogger('testlogger')


def send_data_to_msi_webhook(girl):
    try:
        serializer = GirlMSISerializer(girl)
        actual_data = JSONRenderer().render(serializer.data)
    except Exception as e:
        print(e)
        serializer = GirlMSIDateFormattedSerializer(girl)
        actual_data = JSONRenderer().render(serializer.data)
    headers = {'Authorization': 'Basic ' + MSI_TOKEN}
    return requests.post(url=MSI_BASE_URL + "/msi/api/generateMaternityVoucher", data=actual_data, headers=headers)


class ODKWebhook(APIView):
    """
    Receives the mapping encounter data and then creates the Girl model and MappingEncounter model
    Receives followup, delivery and appointments from the getin app and odk server
    """

    parser_classes = [JSONParser]

    def post(self, request, *args, **kwargs):
        print("post request called")
        json_result = request.data
        json_result_string = str(request.data)

        try:
            webhooklog = open('webhook_log.txt', 'a')
            webhooklog.write("\n\n" + str(timezone.now()) + "\n" + str(json_result))
            webhooklog.close()
        except Exception as e:
            print(e)

        if type(json_result) != dict:
            json_result = str(json_result).replace('\'', "\"")
            json_result = json.loads(json_result)

        form_meta_data = json_result["form_meta_data"]

        try:
            form_meta_data = json.loads(form_meta_data)
        except Exception as e:
            print(e)
        try:
            girl_id = form_meta_data["GIRL_ID"]
        except KeyError:
            print(traceback.print_exc())

        try:
            user_id = form_meta_data["USER_ID"]
        except KeyError:
            print(traceback.print_exc())

        if MAP_GIRL_BUNDIBUGYO_CHEW_FORM_NAME in json_result_string or MAP_GIRL_BUNDIBUGYO_MIDWIFE_FORM_NAME in json_result_string \
                or MAP_GIRL_ARUA_CHEW_FORM_NAME in json_result_string or MAP_GIRL_ARUA_MIDWIFE_FORM_NAME in json_result_string \
                or MAP_GIRL_KAMPALA_CHEW_FORM_NAME in json_result_string or MAP_GIRL_KAMPALA_MIDWIFE_FORM_NAME in json_result_string:
            print("mapping forms matched")
            return self.process_mapping_encounter(json_result, user_id)
        elif FOLLOW_UP_FORM_CHEW_NAME in json_result_string or FOLLOW_UP_FORM_MIDWIFE_NAME in json_result_string:
            return self.process_follow_up_and_delivery_encounter(girl_id, json_result, user_id)
        elif APPOINTMENT_FORM_MIDWIFE_NAME in json_result_string:
            return self.process_appointment_encounter(girl_id, json_result, user_id)
        elif POSTNATAL_FORM_CHEW_NAME in json_result_string or POSTNATAL_FORM_MIDWIFE_NAME in json_result_string:
            return self.postnatal_encounter(girl_id, json_result, user_id)
        return Response({'result': 'failure'}, 400)

    def process_mapping_encounter(self, json_result, user_id):
        print("process mapping encounter")

        try:
            try:
                mapped_girl_object = json_result[MAP_GIRL_BUNDIBUGYO_MIDWIFE_FORM_NAME]
            except KeyError:
                print(traceback.print_exc())
            try:
                mapped_girl_object = json_result[MAP_GIRL_BUNDIBUGYO_CHEW_FORM_NAME]
            except KeyError:
                print(traceback.print_exc())
            try:
                mapped_girl_object = json_result[MAP_GIRL_ARUA_CHEW_FORM_NAME]
            except KeyError:
                print(traceback.print_exc())
            try:
                mapped_girl_object = json_result[MAP_GIRL_ARUA_MIDWIFE_FORM_NAME]
            except KeyError:
                print(traceback.print_exc())
            try:
                mapped_girl_object = json_result[MAP_GIRL_KAMPALA_CHEW_FORM_NAME]
            except KeyError:
                print(traceback.print_exc())
            try:
                mapped_girl_object = json_result[MAP_GIRL_KAMPALA_MIDWIFE_FORM_NAME]
            except KeyError:
                print(traceback.print_exc())
            try:
                mapped_girl_object = json_result[DEFAULT_TAG]
            except KeyError:
                print(traceback.print_exc())

            next_of_kin_number = None
            voucher_number = ""
            attended_anc_visit = False
            bleeding = False
            fever = False
            swollenfeet = False
            blurred_vision = False
            voucher_number_creation = False
            nationality = "Ugandan"
            disabled = False
            mapping_encounter = MappingEncounter()

            try:
                odk_instance_id = mapped_girl_object["meta"][0]["instanceID"][0]
            except Exception as e:
                print(e)
                odk_instance_id = "abc123"

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

            try:
                nationality_group = mapped_girl_object["NationalityGroup"][0]
                nationality = nationality_group['Nationality'][0]
            except KeyError or IndexError as e:
                print(e)

            girl_location = mapped_girl_object["GirlLocation"][0]

            # use filter and get first because there are so some duplicate locations
            parish = Parish.objects.filter(name__icontains=replace_underscore(girl_location["parish"][0])).first()
            village = Village.objects.filter(
                Q(name__icontains=replace_underscore(girl_location["village"][0])) & Q(parish=parish)).first()

            try:
                disability_group = mapped_girl_object["DisabilityGroup"][0]
                disabled = disability_group['Disability'][0] == "yes"
            except KeyError or IndexError as e:
                print(e)

            observations3 = mapped_girl_object["Observations3"][0]
            marital_status = observations3["marital_status"][0]
            education_level = replace_underscore(observations3["education_level"][0])
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
                    voucher_number = voucher_card_group["VoucherNumber"][0]
                else:
                    voucher_number_creation = voucher_card_group["VoucherNumberCreation"][0] == "yes"
            except KeyError or IndexError:
                print(traceback.print_exc())

            user = User.objects.get(id=user_id)
            print(user)

            # incase the village does not exist use the health worker's village
            if not village:
                village = user.village

            # incase the girl already exists with the same name,
            # create a new girl and swap the new girl for the old one with updated data
            old_girl = Girl.objects.filter(Q(first_name__icontains=first_name) & Q(last_name__icontains=last_name))
            if old_girl:
                if len(voucher_number) == 0:
                    voucher_number = old_girl.first().voucher_number
                edited_girl = Girl(first_name=first_name, last_name=last_name, village=village,
                                   phone_number=girls_phone_number, user=user, disabled=disabled, voucher_number=voucher_number,
                                   next_of_kin_phone_number=next_of_kin_number, nationality=nationality,
                                   education_level=education_level, dob=dob, marital_status=marital_status,
                                   last_menstruation_date=last_menstruation_date, odk_instance_id=odk_instance_id)
                edited_girl.save()
                girl = edited_girl

                # swap the old girl for the edited girl
                old_girl = old_girl.first()
                old_appointments = old_girl.appointment_set.all()
                for appointment in old_appointments:
                    appointment.girl = edited_girl
                    appointment.save(update_fields=['girl'])

                old_referrals = old_girl.referral_set.all()
                for referral in old_referrals:
                    referral.girl = edited_girl
                    referral.save(update_fields=['girl'])

                # lastly delete the old girl
                old_girl.delete()
            else:
                new_girl = Girl.objects.create(first_name=first_name, last_name=last_name, village=village,
                            phone_number=girls_phone_number, user=user, nationality=nationality, disabled=disabled,
                            next_of_kin_phone_number=next_of_kin_number, education_level=education_level, dob=dob,
                            marital_status=marital_status, last_menstruation_date=last_menstruation_date,
                            voucher_number=voucher_number, odk_instance_id=odk_instance_id)
                girl = new_girl

                try:
                    # incase girl who has already had ANC visit is mapped by midwife
                    # save that date and create an anc visit
                    anc_previous_group = mapped_girl_object["ANCAppointmentPreviousGroup"][0]
                    attended_anc_visit = anc_previous_group["AttendedANCVisit"][0] == "yes"

                    if attended_anc_visit:
                        previous_appointment_date = anc_previous_group["ANCDatePrevious"][0]
                        self.auto_generate_appointment(new_girl, user, previous_appointment_date)
                    else:
                        self.auto_generate_appointment(new_girl, user)
                except Exception:
                    print(traceback.print_exc())

                try:
                    anc_group = mapped_girl_object["ANCAppointmentGroup"][0]
                    next_appointment_date = anc_group["ANCDate"][0]
                    appointment = Appointment(girl=new_girl, user=user, date=next_appointment_date)
                    appointment.save()
                except Exception:
                    print(traceback.print_exc())

            observation = Observation(blurred_vision=blurred_vision, bleeding_heavily=bleeding, fever=fever,
                                      swollen_feet=swollenfeet)
            observation.save()

            mapping_encounter.observation = observation
            mapping_encounter.attended_anc_visit = attended_anc_visit
            mapping_encounter.voucher_card = voucher_number
            mapping_encounter.odk_instance_id = odk_instance_id
            mapping_encounter.user = user
            mapping_encounter.girl = girl
            mapping_encounter.save()
            self.save_family_planning_methods_in_mapping_encounter(mapped_girl_object, mapping_encounter)

            if voucher_number_creation:
                self.get_and_save_msi_voucher_to_girl(girl)
            return Response({'result': 'success'}, status.HTTP_200_OK)
        except Exception:
            print(traceback.print_exc())
        return Response({'result': 'failure'}, status.HTTP_400_BAD_REQUEST)

    def get_and_save_msi_voucher_to_girl(self, girl):
        try:
            webhook_response = send_data_to_msi_webhook(girl)
            webhook_response = webhook_response.json()
            if webhook_response['successful']:
                voucher_number = webhook_response['eVoucher']['code']
                girl.voucher_number = voucher_number
                girl.save(update_fields=['voucher_number'])
        except Exception as e:
            print(e)

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
        # if girl.age < 25:
        if True:
            # Priority is given to girls who are less than 25 years
            current_date = datetime.datetime.now()

            if previous_appointment_date:
                # if girl has ever attended ANC
                # Pick ANC date from card
                # assume that a previous ANC appointment was attended
                year, month, day = [int(x) for x in previous_appointment_date.split("-")]
                previous_appointment_date = timezone.datetime(year, month, day)

                status = EXPECTED if current_date.replace(tzinfo=pytz.utc) \
                                     > previous_appointment_date.replace(tzinfo=pytz.utc) else ATTENDED
                appointment = Appointment(girl=girl, user=user, date=previous_appointment_date, status=status)
                appointment.save()

            if user.role == USER_TYPE_CHEW:
                # create auto appointment is the user is a chew
                last_menstruation_date = girl.last_menstruation_date

                lmd_days = (current_date - last_menstruation_date).days
                print("lmd_days " + str(lmd_days))

                if lmd_days > 84:
                    # If girls is greater than 12 weeks pregnant and has never attended ANC*
                    # Get the day of week when she is mapped
                    # Add the number of days to either Tuesday or Thursday
                    appointment_date = current_date + timezone.timedelta(days=8 - current_date.weekday())
                else:
                    # If girl is less than 12 weeks pregnant and has never attended ANC
                    # Get a random number , add it to the day she was mapped
                    # Then work out the logic of her appointment being between Tuesday and Thursday
                    rand_diff = 84 - lmd_days

                    incremented_days = random.randint(0, rand_diff)
                    current_date = current_date + timezone.timedelta(days=incremented_days)

                    if current_date.weekday() == 0:
                        appointment_date = current_date + timezone.timedelta(days=3)
                    elif current_date.weekday() == 1:
                        appointment_date = current_date + timezone.timedelta(days=2)
                    elif current_date.weekday() == 2:
                        appointment_date = current_date + timezone.timedelta(days=6)
                    elif current_date.weekday() == 3:
                        appointment_date = current_date + timezone.timedelta(days=5)
                    elif current_date.weekday() == 4:
                        appointment_date = current_date + timezone.timedelta(days=4)
                    elif current_date.weekday() == 5:
                        appointment_date = current_date + timezone.timedelta(days=5)
                    else:
                        appointment_date = current_date + timezone.timedelta(days=4)

                appointment = Appointment(girl=girl, user=user, date=appointment_date, status=EXPECTED)
                appointment.save()

    def process_follow_up_and_delivery_encounter(self, girl_id, json_result, user_id):
        try:

            try:
                follow_up_object = json_result[FOLLOW_UP_FORM_CHEW_NAME]
            except Exception:
                print(traceback.print_exc())
            try:
                follow_up_object = json_result[FOLLOW_UP_FORM_MIDWIFE_NAME]
            except Exception:
                print(traceback.print_exc())
            try:
                follow_up_object = json_result[DEFAULT_TAG]
            except KeyError:
                print(traceback.print_exc())
            print(follow_up_object)

            fever = False
            swollenfeet = False
            bleeding = False
            blurred_vision = False
            missed_anc_before = False
            missed_anc_reason = ""
            action_taken_by_health_person = "appointment"

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

            try:
                missed_anc_before_group = follow_up_object["missed_anc_before_group"][0]
                missed_anc_before = missed_anc_before_group["missed_anc_before"][0] == "yes"

                if missed_anc_before:
                    missed_anc_before_group2 = follow_up_object["missed_anc_before_group2"][0]
                    missed_anc_reason = replace_underscore(missed_anc_before_group2["missed_anc_reason"][0])
                    if missed_anc_reason == "Other":
                        missed_anc_reason = replace_underscore(missed_anc_before_group2["missed_anc_reason_other"][0])
            except Exception:
                print(traceback.print_exc())

            try:
                action_taken_group = follow_up_object["action_taken_by_health_person_group"][0]
                action_taken_by_health_person = action_taken_group["action_taken_by_health_person"][0]
            except Exception:
                print(traceback.print_exc())

            girl = Girl.objects.get(id=girl_id)
            user = User.objects.get(id=user_id)

            if action_taken_by_health_person == "appointment":
                next_appointment = follow_up_object["schedule_appointment_group"][0]["schedule_appointment"][0]
                appointment = Appointment(girl=girl, user=user, date=next_appointment)
                appointment.save()
            elif action_taken_by_health_person == "delivery":
                self.save_delivery(follow_up_object, girl, user)
            elif action_taken_by_health_person in ["referral", "referred"]:
                Referral.objects.create(girl=girl, user=user, reason="critical")

            observation = Observation(blurred_vision=blurred_vision, bleeding_heavily=bleeding, fever=fever,
                                      swollen_feet=swollenfeet)
            observation.save()

            follow_up = FollowUp(girl=girl, user=user, follow_up_action_taken=action_taken_by_health_person,
                                 missed_anc_reason=missed_anc_reason, missed_anc_before=missed_anc_before,
                                 observation=observation)
            follow_up.save()
            return Response({'result': 'success'}, 200)
        except Exception:
            print(traceback.print_exc())
        return Response({'result': 'failure'}, 400)

    def save_delivery(self, follow_up_object, girl, user):
        """
        The follow up and postnatal form have the same structure.
        Postnatal form will use this function directly while follow up will depend on
        whether the health worker selected 'delivery' as the action taken
        """
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
        delivery_action_taken = replace_underscore(delivery_follow_up_group["action_taken"][0])
        used_contraceptives = "family" in delivery_action_taken
        try:
            contraceptive_group = follow_up_object["family_planning_group"][0]
            postnatal_care = contraceptive_group["postnatal_received"][0] == "yes"
        except Exception as e:
            print(e)
            postnatal_care = False
            contraceptive_group = []

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

        if used_contraceptives:
            self.save_family_planning_methods_in_delivery(contraceptive_group, delivery)

    def save_family_planning_methods_in_delivery(self, contraceptive_group, delivery):
        try:
            contraceptive_method = str(contraceptive_group["ContraceptiveMethod"][0])

            # separate the contraceptive methods which are in a string 'IUD condoms pills'
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
        except KeyError or IndexError as e:
            print(e)

    def process_appointment_encounter(self, girl_id, json_result, user_id):
        try:
            try:
                appointment_object = json_result[APPOINTMENT_FORM_MIDWIFE_NAME]
            except Exception:
                print(traceback.print_exc())
            try:
                appointment_object = json_result[DEFAULT_TAG]
            except KeyError:
                print(traceback.print_exc())

            needed_ambulance = False
            used_ambulance = False
            missed_anc_reason = ""
            appointment_method = ""
            fever = False
            swollenfeet = False
            bleeding = False
            blurred_vision = False

            try:
                ambulance_group = appointment_object["ambulance_group"][0]
                needed_ambulance = ambulance_group["needed_ambulance"][0] == "yes"
                used_ambulance = ambulance_group["used_ambulance"][0] == "yes"
            except Exception:
                print(traceback.print_exc())

            try:
                appointment_soon_group = appointment_object["appointment_soon_group"][0]
                appointment_method = replace_underscore(appointment_soon_group["appointment_method"][0])
            except Exception:
                print(traceback.print_exc())

            missed_anc_before_group = appointment_object["missed_anc_before_group"][0]
            missed_anc_before = missed_anc_before_group["missed_anc_before"][0] == "yes"

            if missed_anc_before:
                missed_anc_before_group2 = appointment_object["missed_anc_before_group2"][0]
                missed_anc_reason = missed_anc_before_group2["missed_anc_reason"][0]
                if missed_anc_reason == "Other":
                    missed_anc_reason = missed_anc_before_group2["missed_anc_reason_other"][0]

            action_taken_group = appointment_object["action_taken_group"][0]
            action_taken = replace_underscore(action_taken_group["action_taken_meeting_girl"][0])
            if action_taken == 'other':
                action_taken = replace_underscore(action_taken_group["action_taken_other"][0])

            schedule_appointment_group = appointment_object["schedule_appointment_group"][0]
            next_appointment_date = schedule_appointment_group["schedule_appointment"][0]

            girl = Girl.objects.get(id=girl_id)
            user = User.objects.get(id=user_id)

            try:
                has_voucher = appointment_object["voucher_received_group"][0]["has_voucher"][0] == "yes"
                if has_voucher:
                    msi_service = appointment_object["voucher_redeem_group"][0]["voucher_services"][0]
                    MSIService.objects.create(girl=girl, option=msi_service)
            except Exception as e:
                print(e)

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
        try:
            postnatal_object = json_result[POSTNATAL_FORM_MIDWIFE_NAME]
        except Exception:
            print(traceback.print_exc())
        try:
            postnatal_object = json_result[DEFAULT_TAG]
        except Exception:
            print(traceback.print_exc())

        girl = Girl.objects.get(id=girl_id)
        user = User.objects.get(id=user_id)

        self.save_delivery(postnatal_object, girl, user)
        return Response()


def replace_underscore(text):
    return str(text).replace("_", " ")
