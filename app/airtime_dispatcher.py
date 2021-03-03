import africastalking
from app.utils.constants import username, api_key

africastalking.initialize(username, api_key)


class AirtimeModule:
    def send_airtime(self, phone_numbers, amount):
        airtime = africastalking.Airtime
        recipients = []
        for phone_number in phone_numbers:
            recipients.append({
                'phoneNumber': phone_number,
                'amount': amount,
                'currency_code': 'UGX'
            })
        return airtime.send(recipients=recipients, amount='50', currency_code='UGX')

