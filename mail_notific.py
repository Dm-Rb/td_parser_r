import smtplib
from email.mime.text import MIMEText
from config import ConfigParsing, ConfigMail


messages = {1: "Stopping parser of tecalliance.net => incorrect answer from API",
            2: 'Stopping parser of tecalliance.net => ConnectionError',
            3: f'Parser of tecalliance.net: "{ConfigParsing.brand}" parsing completed',
            4: 'Stopping parser of tecalliance.net => unknown exception'
            }


def send_email(message_key):
    sender = ConfigMail.sender
    password = ConfigMail.password

    server = smtplib.SMTP("smtp.yandex.ru", 587)
    server.starttls()

    try:
        server.login(sender, password)
        msg = MIMEText(messages[message_key])

        server.sendmail(sender, sender, msg.as_string())

        # server.sendmail(sender, sender, f"Subject: CLICK ME PLEASE!\n{message}")

    except Exception as _ex:
        return f"{_ex}\nCheck your login or password please!"
