
# using SendGrid's Python Library
# https://github.com/sendgrid/sendgrid-python
import os
import json
import argparse
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

with open('config.json') as data_file:
    config = json.load(data_file)

def send_mail_by_sendgrid(to_emails, subject, html_content):
    message = Mail(
        from_email='oberos@gmail.com',
        to_emails=to_emails,
        subject=subject,
        html_content=html_content)
    try:
        # sg = SendGridAPIClient(os.environ.get('SENDGRID_API_KEY'))
        sg = SendGridAPIClient(config['api_key'])
        response = sg.send(message)
        print("Email sent --> ", response.status_code)
    except Exception as e:
        print("Error when sending email")
        print(e)
        print(e.body)

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter)
parser.add_argument('-to_emails', help='List of recipients')
parser.add_argument('-subject', help='Email Subject')
parser.add_argument('-html_content', help='Email body in html')

args = parser.parse_args()

if args.to_emails is None:
    print('You must provide recipients')
    exit(0)
if args.subject is None:
    print('You must provide subject')
    exit(0)
if args.html_content is None:
    print('You must provide email body')
    exit(0)

send_mail_by_sendgrid(args.to_emails, args.subject, args.html_content)