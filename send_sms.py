import os
from twilio.rest import Client

account_sid = os.environ['TWILIO_ACCOUNT_SID']
auth_token = os.environ['TWILIO_AUTH_TOKEN']
personal_number = os.environ['PERSONAL_NUMBER']
twilio_number = os.environ['TWILIO_NUMBER']

client = Client(account_sid, auth_token)

client.messages.create(
    to=personal_number,
    from_=twilio_number,
    body="here is ya message 2"
)
