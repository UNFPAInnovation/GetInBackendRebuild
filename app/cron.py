from app.notifier import NotifierView


def notifier_appointment_reminder_cron_job():
    notifier = NotifierView()
    notifier.send_appointment_three_days_before_date()
    notifier.send_appointment_one_day_after_date()
    notifier.send_appointment_on_actual_day()


def notifier_daily_usage_reminder_cron_job():
    notifier = NotifierView()
    notifier.send_daily_usage_reminder()
