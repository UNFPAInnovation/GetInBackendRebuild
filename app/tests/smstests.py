import random

from django.utils.crypto import get_random_string

from app.tests.parenttest import ParentTest
from app.models import *
from app.notifier import NotifierView

"""
TESTS GUIDE
assertEqual(actual, expected)
"""


class TestSMS(ParentTest):
    def setUp(self) -> None:
        super(TestSMS, self).setUp()
        last_name = get_random_string(length=7)
        self.girl = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                        last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                        village=self.village,
                                        last_menstruation_date=timezone.now() - timezone.timedelta(weeks=12),
                                        phone_number="0756677" + str(random.randint(100, 999)),
                                        education_level=PRIMARY_LEVEL)

        self.girl2 = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4500),
                                         village=self.village,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=8),
                                         phone_number="0756677" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)

        self.girl3 = Girl.objects.create(user=self.midwife2, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=4),
                                         phone_number="0756677" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)
        self.girl4 = Girl.objects.create(user=self.midwife3, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village2,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=20),
                                         phone_number="0756677" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)
        self.girl5 = Girl.objects.create(user=self.midwife3, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village2,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=20),
                                         phone_number="0756789" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)
        self.girl6 = Girl.objects.create(user=self.midwife2, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=30),
                                         phone_number="0756789" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)
        self.girl7 = Girl.objects.create(user=self.midwife, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=20),
                                         phone_number="0756789" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)

        self.girl8 = Girl.objects.create(user=self.midwife4, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=42),
                                         phone_number="0756789" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)
        self.girl9 = Girl.objects.create(user=self.midwife4, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=42),
                                         phone_number="0756789" + str(random.randint(100, 999)),
                                         education_level=O_LEVEL)

        Appointment.objects.create(girl=self.girl, user=self.midwife, date=timezone.now() - timezone.timedelta(hours=7))
        Appointment.objects.create(girl=self.girl2, user=self.chew, date=timezone.now() + timezone.timedelta(days=1))
        Appointment.objects.create(girl=self.girl3, user=self.midwife2, date=timezone.now() + timezone.timedelta(days=2))
        Appointment.objects.create(girl=self.girl4, user=self.midwife3, date=timezone.now() + timezone.timedelta(days=3))
        Appointment.objects.create(girl=self.girl5, user=self.midwife3, date=timezone.now() - timezone.timedelta(days=1))
        Appointment.objects.create(girl=self.girl6, user=self.midwife2, date=timezone.now() - timezone.timedelta(days=1))
        Appointment.objects.create(girl=self.girl7, user=self.midwife, date=timezone.now() - timezone.timedelta(days=2))
        Appointment.objects.create(girl=self.girl8, user=self.midwife4, date=timezone.now() + timezone.timedelta(days=1))
        Appointment.objects.create(girl=self.girl9, user=self.midwife4, date=timezone.now() - timezone.timedelta(days=1))

        for text in range(200):
            HealthMessage.objects.create(text=get_random_string(length=20))
        self.notifier = NotifierView()
        self.client.force_authenticate(user=self.manager)

    def test_random_message_query(self):
        first_message = NotifierView.get_random_health_messages()
        second_message = NotifierView.get_random_health_messages()
        self.assertNotEqual(first_message, second_message)

    def test_sending_health_sms_messages(self):
        """
        Test sending of random sms health messages.
        Acceptance criterion:
        - Girl should not receive two message in the same day
        - Only girls who are pregnant should receive the sms messages
        """
        self.notifier.send_health_messages()
        self.assertEqual(SentSmsLog.objects.count(), 7)

        # simulate sms sent 24 hours prior. to ensure no user
        sms_log = SentSmsLog.objects.last()
        sms_log.created_at = timezone.now() - timezone.timedelta(hours=24)
        sms_log.save(update_fields=['created_at'])
        self.notifier.send_health_messages()
        self.assertEqual(SentSmsLog.objects.count(), 8)

    # def test_appointment_notification_before_appointment(self):
    #     """
    #     Test sending of sms notification to health workers and girl 3 days to appointment day
    #     Acceptance criterion:
    #     - Users must never get spam messages
    #     - Users must get notified 3 days to appointment day
    #     - If health worker has multiple upcoming appointments for several girls, only one must be sent
    #     - Sent sms should not exceed the daily limit
    #     - Only girls who are still pregnant should receive messages
    #     """
    #     self.notifier.send_appointment_sms_to_eligible_girls()
    #     self.assertEqual(SentSmsLog.objects.count(), 3)
    #     self.assertEqual(SentSmsLog.objects.filter(message__icontains='today').count(), 1)
    #     self.assertEqual(SentSmsLog.objects.filter(message__icontains='tomorrow').count(), 1)
    #     self.assertEqual(SentSmsLog.objects.filter(message__icontains='3 days').count(), 1)

    # def test_missed_appointment(self):
    #     """
    #     Test sending of missed appointment sms to health worker
    #     Acceptance criterion:
    #     - Only health workers attached to the girl should receive sms
    #     - Only missed or expected appointments should trigger sms to health worker
    #     - Only one message should reach a health worker every 20 hr period
    #     - Only health workers who have pregnant girls should receive sms
    #     """
    #     self.notifier.send_missed_appointment_reminder_one_day_after()
    #     self.assertEqual(SentSmsLog.objects.count(), 2)
    #     self.assertEqual(SentSmsLog.objects.filter(message__icontains='missed').count(), 2)

    def test_send_weekly_sms_reminders(self):
        """
        Test sending of weekly app usage reminder sms to health worker
        Acceptance criterion:
        - Only one message should reach a health worker every 20 hr period
        - Only health workers who are not test users must get sms
        """
        self.notifier.send_weekly_usage_reminder()
        self.assertEqual(SentSmsLog.objects.count(), 8)

        # test users have mid or vht in user name. create test user then send weekly reminder again
        self.chew2 = User.objects.create(username="vhtuservt2", first_name="vht2", last_name="uservht2",
                                         phone="075687" + str(random.randint(1000, 9999)),
                                         password=self.chew_phone_number,
                                         gender=GENDER_FEMALE,
                                         village=self.village, district=self.district, role=USER_TYPE_CHEW,
                                         midwife=self.midwife, email="chewtest2@test.com")

        self.notifier.send_weekly_usage_reminder()
        self.assertEqual(SentSmsLog.objects.count(), 8)