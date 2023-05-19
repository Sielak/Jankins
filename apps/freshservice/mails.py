import csv
from smtplib import SMTP              # sending email
from email.mime.text import MIMEText  # constructing messages
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from jinja2 import Environment        # Jinja2 templating



class Mail:

    def __init__(self, email_address):
        """
        Class used to communicate with Users by email  
        :params:  
        email_address: string
        """
        self.email_address = email_address

    def _send_email(self, msg, subject):
        """
        Method used to send email to user
        """
        COMMASPACE = ', '

        sender = "no.replay@hl-display.com"
        recipient = [item for item in self.email_address.split('#')]

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = COMMASPACE.join(recipient)

        # Send the message via our own local SMTP server.
        s = SMTP('smtp.hl-display.com')
        s.send_message(msg)
        s.quit()

        return "Email was sent to {0}".format(recipient)

    def rfc_report(self, rfc_data):
        """
        Method used to compose HTML email template for change report  
        """
        # HTML
        TEMPLATE = "<h2>RFC Status report</h2>"

        msg = MIMEMultipart()
        # Create a text/html message from a rendered template
        msgText = MIMEText(
            Environment().from_string(TEMPLATE).render(
                title='Hello World!'
            ), "html"
        )
        msg.attach(msgText)
        subject = 'FreshService RFC status'
        if len(rfc_data) > 0:
            # save list as csv
            keys = rfc_data[0].keys()
            with open('cache/rfc_data.csv', 'w', newline='')  as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(rfc_data)

            csv_file = MIMEApplication(open('cache/rfc_data.csv', 'rb').read())
            csv_file.add_header('Content-Disposition', 'attachment', filename= "rfc_data.csv")
            msg.attach(csv_file)

        return self._send_email(msg, subject)

    