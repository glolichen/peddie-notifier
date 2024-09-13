import base64
import requests
import datetime
import json
from email.message import EmailMessage
from email.utils import formataddr

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://mail.google.com/"]

DEBUG_MODE = True

# Monday = 0, Tuesday = 1, ...
CURRENT_DATE = 3


def send_reminder(name: str, email: str, block: str, time: str, location: str):
    creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    try:
        service = build("gmail", "v1", credentials=creds)
        message = EmailMessage()

#         message.set_content(f"""Dear {name},
#
# This is an automated reminder that you are scheduled for CS Fellows \
# today during {block}. Please appear at {location} at {time} today.
#
# Thank you,
# The CS Club""")

        message.set_content(f"""Dear {name},

This is an automated reminder that you are scheduled for CS Fellows today.

        Block: {block}
        Time: {time}
        Location: {location}

Thank you,
The CS Club""")

        message["To"] = formataddr((name, email))
        message["From"] = formataddr(
            ("CompSci Club", "compsciclub@peddie.org"))
        message["Subject"] = f"Reminder: CS Fellows at {block}"

        # encoded message
        encoded_message = base64.urlsafe_b64encode(message.as_bytes()).decode()

        create_message = {"raw": encoded_message}

        if not DEBUG_MODE:
            send_message = (
                service.users()
                .messages()
                .send(userId="me", body=create_message)
                .execute()
            )
            print(f"Message Id: {send_message['id']}")
        else:
            send_message = None

        print(f"Email to {name} ({email}) sent",
              "(debug)" if DEBUG_MODE else "")

    except HttpError as error:
        print(f"An error occurred: {error}")
        send_message = None

    return send_message


def is_gold_week():
    r = requests.get("https://peddie.org/families/peddie-am/")
    return "gold week" in r.text.lower()


def main():
    mail_time = datetime.time(8, 30)

    with open("gold.jsonc", "r") as file:
        gold = json.loads(file.read())
    with open("blue.jsonc", "r") as file:
        blue = json.loads(file.read())

    prev_email_day = CURRENT_DATE
    while True:
        now = datetime.datetime.today()
        weekday = now.weekday()
        if weekday != prev_email_day and now.time() > mail_time:
            is_gold = is_gold_week()
            print("Gold" if is_gold else "Blue", "week")
            info = gold if is_gold else blue
            for session in info[weekday]:
                block = session["block"]
                time = session["time"]
                location = session["location"]
                for person in session["people"]:
                    name = person["name"]
                    email = person["email"]
                    send_reminder(name, email, block, time, location)
            prev_email_day = weekday

    # print(gold)


if __name__ == "__main__":
    main()
    # send_reminder("Jayden Li", "cli-26@peddie.org",
    #               "DMX", "10:20 AM", "CS Lab")
