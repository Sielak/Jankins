import json
import xml.etree.ElementTree as ET
from smtplib import SMTP  # sending email
from email.mime.text import MIMEText  # constructing messages
from jinja2 import Environment  # Jinja2 templating


def notification(status, log):
    print("Transus test result:", status)
    print(log)
    # HTML
    TEMPLATE = """
    <p>There is some errors on transus web portal</p>
    <p>LOG:</p>
    <br>
    {{log}}
    """  # Our HTML Template

    # Create a text/html message from a rendered template
    msg = MIMEText(
        Environment().from_string(TEMPLATE).render(
            title='Hello World!', log=log
        ), "html"
    )
    # e-mail
    COMMASPACE = ', '
    subject = "Transus Errors"
    sender = "transus.helthcheck@hl-display.com"
    recipient = ["mariusz.lekstutis@hl-display.com"]
    # recipient = ["gliwiceitall@hl-display.com"]

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = COMMASPACE.join(recipient)

    # Send the message via our own local SMTP server.
    s = SMTP('smtp.hl-display.com')
    s.send_message(msg)
    s.quit()
    print("Email was sent to", recipient)


# import xml files
with open('test-reports/test_results.xml', 'r', encoding="UTF-8") as f2:
    file2check = f2.read()
root = ET.fromstring(file2check)  # import file as XML
result_errors = root.attrib['errors']  # search for number of errors in test report
result_failures = root.attrib['failures']  # search for number of failures in test report
console_log = root.find('system-out').text
if int(result_errors) != 0 or int(result_failures) != 0:
    notification('NOK', console_log)
else:
    pass




