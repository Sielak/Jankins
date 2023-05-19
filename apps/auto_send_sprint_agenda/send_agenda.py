import json
import sqlite3 as sql
from smtplib import SMTP  # sending email
from email.mime.text import MIMEText  # constructing messages
from jinja2 import Environment  # Jinja2 templating
from Axo import Axosoft
import datetime
import sys


def send_sprint_agenda(release_id, sprint_name):
    # Connect to axosoft
    axosoft_client = Axosoft(
        config['client_id'],
        config['client_secret'],
        'hl-display'
    )
    # Authenticate in axosoft
    axosoft_client.authenticate_by_password(
        config['Axosoft_username'],
        config['Axosoft_password'],
        "read"
    )

    #  Features
    arg1 = 'release_id={0}'.format(release_id)
    arg2 = 'sort_fields=custom_198&columns=id,name,custom_198,custom_346,custom_347,assigned_to'
    f = axosoft_client.get('features', arguments='{0}&{1}'.format(arg1, arg2))
    all3 = f['data']
    ficzery = []

    for item in all3:
        number = item['number']
        name = item['name']
        stream = item['custom_fields']['custom_198']
        demo = item['custom_fields']['custom_346']
        demo_comment = item['custom_fields']['custom_347']
        if demo == 'No - demo on demand / nothing to show':
            if demo_comment == '':
                demo_comment = 'NEED COMMENT FROM DEV'
        else:
            demo_comment = ''
        dev = item['assigned_to']['name']
        # print(number, '  ', stream, '  ', name)
        an_item = dict(ID=number, name=name, stream=stream,
                       demo=demo, dev=dev, comment=demo_comment)
        ficzery.append(an_item)

    ficzery_sorted = sorted(ficzery, key=lambda elem: "%s %s" %
                            (elem['stream'], elem['dev']))

    # Defects
    d_arg1 = 'sort_fields=custom_215'
    d_arg2 = 'columns=id,name,assigned_to,custom_215,custom_402,custom_403'
    d = axosoft_client.get(
        'defects', arguments='{0}&{1}&{2}'.format(arg1, d_arg1, d_arg2))
    d_all_data = d['data']
    defects = []

    for item in d_all_data:
        number = item['number']
        name = item['name']
        dev = item['assigned_to']['name']
        stream = item['custom_fields']['custom_215']
        demo = item['custom_fields']['custom_402']
        demo_comment = item['custom_fields']['custom_403']
        if demo == 'No - demo on demand / nothing to show':
            if demo_comment == '':
                demo_comment = 'NEED COMMENT FROM DEV'
        else:
            demo_comment = ''
        # print(number, '  ', stream, '  ', name)
        an_item = dict(ID=number, name=name, dev=dev,
                       stream=stream, demo=demo, demo_comment=demo_comment)
        defects.append(an_item)

    defects_sorted = sorted(defects, key=lambda elem: "%s %s" %
                            (elem['stream'], elem['dev']))

    # HTML

    # Create a text/html message from a rendered template
    with open('sprint_agenda.html') as file:
        template = file.read()  # Our HTML Template
    msg = MIMEText(
        Environment().from_string(template).render(
            title='Hello World!', ficzery_sorted=ficzery_sorted, defects_sorted=defects_sorted
        ), "html"
    )

    # e-mail

    commaspace = ', '

    subject = sprint_name + " agenda"
    sender = "Agenda@hl-display.com"
    recipient = ["gliwiceitall@hl-display.com"]
    # recipient = ["dawid.wybierek@hl-display.com"]

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = commaspace.join(recipient)

    # Send the message via our own local SMTP server.
    s = SMTP('smtp.hl-display.com')
    s.send_message(msg)
    s.quit()
    text2log = "Email was sent. Relese ID = {0} Sprint ID = {1}".format(
        release_id, sprint_name)
    print(text2log)


# send_sprint_agenda()
with open('config.json') as data_file:
    config = json.load(data_file)

# RELEASE_ID
select_sprint_id = """
SELECT
    Param_Value_string
FROM 
    dashboard_systemparameter
WHERE
    Param_Name = 'Actual sprint id';
"""
select_sprint_name = """
SELECT
    Param_Value_string
FROM 
    dashboard_systemparameter
WHERE
    Param_Name = 'Actual sprint name';
"""
db_path = config['db_path']
con = sql.connect(db_path)
# con.row_factory = sql.Row
cur = con.cursor()
cur.execute(select_sprint_id)
temp2 = cur.fetchone()
release_id = temp2[0]
cur.execute(select_sprint_name)
temp2_name = cur.fetchone()
sprint_name = temp2_name[0].split('-', 1)[0].strip()

# check if is the end of the sprint
today = datetime.date.today()
tomorrow = today + datetime.timedelta(days=1)

client_id = config['client_id']
client_secret = config['client_secret']
password = config['Axosoft_password']
login = config['Axosoft_username']

axosoft_client = Axosoft(client_id, client_secret, 'hl-display')
axosoft_client.authenticate_by_password(login, password, scope='read')

sprint_due_date_get = axosoft_client.get(
    'releases', resourse_id=release_id.strip())
sprint_due_date_tmp = sprint_due_date_get['data']['due_date'][:10]
sprint_due_date_tmp2 = datetime.datetime.strptime(
    sprint_due_date_tmp, "%Y-%m-%d").date()
# Convert from UTC time zone
sprint_due_date = sprint_due_date_tmp2 + datetime.timedelta(days=1)
print('[DEBUG] -->', tomorrow, sprint_due_date)
force = sys.argv[1]
if force == '-force':
    send_sprint_agenda(release_id, sprint_name)
else:
    # check date
    if tomorrow != sprint_due_date:
        print('not end of the sprint')
        print('TimeStamp =', today)
    else:
        print('end of sprint')
        print('Retrieving data')
        send_sprint_agenda(release_id, sprint_name)
