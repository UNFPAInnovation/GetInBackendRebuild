import africastalking
from app.utils.constants import username, api_key

africastalking.initialize(username, api_key)


class AirtimeModule:
    def send_airtime(self, phone_numbers: list):
        airtime = africastalking.Airtime
        recipients = []
        for phone_number in phone_numbers:
            recipients.append({
                'phoneNumber': phone_number,
                'amount': '50',
                'currency_code': 'UGX'
            })
        x = airtime.send(recipients=recipients, amount='50', currency_code='UGX')
        print(x)

