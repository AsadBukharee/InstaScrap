"""prefork worker doesn't work in windows , so we have to use (-P solo) or (-P eventlet)\
as following:
celery -A celery_worker worker --loglevel=INFO -P eventlet
"""
import os
import time
from celery import Celery
import smtplib
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import  load_env
from jinja2 import Environment, FileSystemLoader



def populate_html_file(url,user_name):
    base_url = f"{os.environ.get('SSO_BACKEND_URL')}api/v1/image/"
    if not "http" in base_url:
        base_url = "http://"+base_url
    environment = Environment(loader=FileSystemLoader("templates/"))
    template = environment.get_template("email.html")
    html_ = template.render(user_activation_url=url,base_url=base_url,user_name=user_name)
    # print(base_url)
    with open('email.html', 'wb') as f:
        f.write(html_.encode())
        # f.truncate()


def wait_until_found_file(file_path):
    while not os.path.exists(file_path):
        print(f"\t{file_path} not found")
        time.sleep(.5)

    if os.path.isfile(file_path):
        print(f"\tSuccess {file_path} found")
        file_= open(file_path)
        return file_
    else:
        raise ValueError("%s isn't a file!" % file_path)


def send_email(url, recipient, user_name, attachment=None):
    try:
        print("===================================================")
        print("                Email Task Started                 ")
        print("===================================================")

        populate_html_file(url,user_name)
        file_ = wait_until_found_file("email.html")

        mail_content = MIMEText(file_.read(), "html")
        # The mail addresses and password
        # The mail addresses and password
        sender_address = os.environ.get("EMAIL_SENDER")
        sender_pass = os.environ.get("EMAIL_SENDER_PASSWORD")
        # Setup the MIME
        message = MIMEMultipart()
        message['From'] = sender_address
        message['To'] = recipient
        message['Subject'] = os.environ.get("EMAIL_SUBJECT")
        # The body and the attachments for the mail
        message.attach(mail_content)
        # attach files if given
        if attachment:
            attach_file = open(attachment, 'rb')  # Open the file as binary mode
            payload = MIMEBase('application', 'octate-stream')
            payload.set_payload((attach_file).read())
            encoders.encode_base64(payload)  # encode the attachment
            # add payload header with filename
            payload.add_header('Content-Decomposition', 'attachment', filename=attachment.split("\"")[-1])
            message.attach(payload)
        # Create SMTP session for sending the mail
        session = smtplib.SMTP('smtp.gmail.com', 587)  # use gmail with port
        session.starttls()  # enable security
        session.login(sender_address, sender_pass)  # login with mail_id and password
        text = message.as_string()
        session.sendmail(sender_address, recipient, text)
        session.quit()
        print("===================================================")
        print(f"      Success: {recipient}")
        print("===================================================")
        return True
    except Exception as e:
        print(str(e))
        return False


celery = Celery(__name__)
celery.conf.broker_url = os.environ.get("CELERY_BROKER_URL", "redis://redis:6379/0")
celery.conf.result_backend = os.environ.get("CELERY_RESULT_BACKEND", "redis://redis:6379/0")


@celery.task(name="email_sender")
def email_sender(user_verification_url, user_email,user_name):
    return send_email(url=user_verification_url,recipient=user_email,user_name=user_name)
