from app.notifier import NotifierView


def notifier_cron_job():
    notifier = NotifierView()
    notifier.send_appointment_three_days_before_date()
    notifier.send_appointment_one_day_after_date()
    notifier.send_appointment_on_actual_day()
