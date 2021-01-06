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
                                        phone_number="0756789543",
                                        education_level=PRIMARY_LEVEL)

        self.girl2 = Girl.objects.create(user=self.chew, first_name=get_random_string(length=7), marital_status=SINGLE,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4500),
                                         village=self.village,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=8),
                                         phone_number="0756783333",
                                         education_level=O_LEVEL)

        self.girl3 = Girl.objects.create(user=self.midwife2, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=4),
                                         phone_number="0756783334",
                                         education_level=O_LEVEL)
        self.girl4 = Girl.objects.create(user=self.midwife3, first_name=get_random_string(length=7),
                                         marital_status=MARRIED,
                                         last_name=last_name, dob=timezone.now() - timezone.timedelta(days=4000),
                                         village=self.village2,
                                         last_menstruation_date=timezone.now() - timezone.timedelta(weeks=50),
                                         phone_number="0756783339",
                                         education_level=O_LEVEL)

        Appointment.objects.create(girl=self.girl, user=self.midwife, date=timezone.now() + timezone.timedelta(days=2))
        Appointment.objects.create(girl=self.girl2, user=self.chew, date=timezone.now() + timezone.timedelta(days=2))
        Appointment.objects.create(girl=self.girl3, user=self.midwife2, date=timezone.now() + timezone.timedelta(days=2))
        Appointment.objects.create(girl=self.girl4, user=self.midwife3, date=timezone.now() + timezone.timedelta(days=2))
        Appointment.objects.create(girl=self.girl, user=self.midwife, date=timezone.now() + timezone.timedelta(days=4))
        Appointment.objects.create(girl=self.girl2, user=self.midwife, date=timezone.now() + timezone.timedelta(days=10))

        for text in range(200):
            HealthMessage.objects.create(text=get_random_string(length=20))
        self.notifier = NotifierView()

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
        self.assertEqual(SentSmsLog.objects.count(), 3)

        # simulate sms sent 24 hours prior. to ensure no user
        sms_log = SentSmsLog.objects.last()
        sms_log.created_at = timezone.now() - timezone.timedelta(hours=24)
        sms_log.save(update_fields=['created_at'])
        self.notifier.send_health_messages()
        self.assertEqual(SentSmsLog.objects.count(), 4)

    def test_appointment_notification_before_appointment(self):
        """
        Test sending of sms notification to health workers and girl 3 days to appointment day
        Acceptance criterion:
        - Users must never get spam messages
        - Users must get notified 3 days to appointment day
        - If health worker has multiple upcoming appointments for several girls, only one must be sent
        - Sent sms dont exceed the daily limit
        """
        self.notifier.send_appointment_three_days_before_date()
        self.assertEqual(SentSmsLog.objects.count(), 8)
