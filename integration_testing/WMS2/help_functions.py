import pyodbc
import csv
import time
from smtplib import SMTP              # sending email
from email.mime.text import MIMEText  # constructing messages
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from jinja2 import Environment        # Jinja2 templating



class SqlQueries:
    def __init__(self, database_name, db_server):
        # Connects to SQL server DB
        self.server = db_server
        self.database = database_name
        cnxn = pyodbc.connect(driver='{SQL Server}', server=self.server, database=self.database, trusted_connection='yes')
        self.cursor = cnxn.cursor()

    def _run_query(self, query):
        for _ in range(0, 10):
            try:
                self.cursor.execute(query)
                return self.cursor.fetchall()
            except pyodbc.Error as ex:
                sqlstate = ex.args[0]
                if sqlstate == '40001':
                    print("Transaction was a deadlock victim. Sleep 30 sek and run again")
                    time.sleep(30)
                else:
                    raise Exception(ex.args[1])

    def fetch_dp_data(self, foretagkod): 
        query = """
        SELECT
            ProcesId
            ,ProcesType
            ,Text1
            ,Text2
            ,Message
            ,RowCreationDate
        FROM
            q_hl_dp_data
        WHERE
            ProcesName = 'WMS2.0'
            AND EI = 'E'
            AND RowCreationDate > dateadd(day,datediff(day,1,GETDATE()),0)
            AND Text1 = '{foretagkod}'
        """.format(foretagkod=foretagkod)
        sql_results = self._run_query(query)
        results = []
        for row in sql_results:
            if row[4] is None:
                message = row[4]
            else:
                message = ''
                for item in row[4].split("\n"):
                    if "<%OrderNr>" in item and "<%OrderNr>" not in message:
                        message += item.strip() + ', '
                    if "<%BestNr>" in item and "<%BestNr>" not in message:
                        message += item.strip() + ', '
                message += row[4].split("*=*=*=*=*")[0]
            jeeves_data = {
                "ProcesId": row[0],
                "ProcesType": row[1],
                "Text1": row[2],
                "Text2": row[3],
                "Message": message,
                "RowCreationDate": row[5]
            }
            results.append(jeeves_data)
        return results


class Mail:

    def __init__(self, email_addresses):
        """
        Class used to communicate with Users by email  
        :params:  
        email_address: list
        """
        self.email_addresses = email_addresses

    def _send_email(self, msg, subject):
        """
        Method used to send email to user
        """
        COMMASPACE = ', '

        sender = "wms.integration@hl-display.com"

        msg['Subject'] = subject
        msg['From'] = sender
        msg['To'] = COMMASPACE.join(self.email_addresses)

        # Send the message via our own local SMTP server.
        s = SMTP('smtp.hl-display.com')
        s.send_message(msg)
        s.quit()

        return "Email was sent to {0}".format(self.email_addresses)

    def integration_errors(self, data, foretagkod):
        """
        Method used to compose HTML email template for integration errors  
        """
        # HTML
        if len(data) == 0:
            TEMPLATE = "<h2>There is no recent errors</h2>"
        else:
            TEMPLATE = "<h2>Errors from last 24h</h2>"
        # Our HTML Template

        msg = MIMEMultipart()
        # Create a text/html message from a rendered template
        msgText = MIMEText(
            Environment().from_string(TEMPLATE).render(
                title='wms2 errors', balance_data=data
            ), "html"
        )
        msg.attach(msgText)
        subject = 'WMS2.0 Integration Errors = {0}'.format(foretagkod)
        if len(data) > 0:
            # save list as csv
            keys = data[0].keys()
            with open('cache/integration_errors.csv', 'w', newline='')  as output_file:
                dict_writer = csv.DictWriter(output_file, keys)
                dict_writer.writeheader()
                dict_writer.writerows(data)

            csv_file = MIMEApplication(open('cache/integration_errors.csv', 'rb').read())
            csv_file.add_header('Content-Disposition', 'attachment', filename= "integration_errors.csv")
            msg.attach(csv_file)

        return self._send_email(msg, subject)
