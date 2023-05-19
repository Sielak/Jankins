from lib.Axosoft_lib import Axosoft
from smtplib import SMTP  # sending email
from email.mime.text import MIMEText  # constructing messages
from jinja2 import Environment  # Jinja2 templating
import pyodbc
import sqlite3 as sql
import json
from datetime import datetime, timedelta, date
import pandas as pd

# RELEASE_ID
with open('config.json') as data_file:
    config = json.load(data_file)

db_path = config['path2db']  # PROD

sql_select = """
SELECT 
    Param_Value_string   
FROM 
    dashboard_systemparameter
WHERE 
    Param_Name = 'Actual sprint id';
"""
con = sql.connect(db_path)
cur = con.cursor()
cur.execute(sql_select)
release_id = cur.fetchone()[0]

print(release_id)
# UT
server = config['DB_server']
database = 'HLTools'
username = config['DB_username']
password = config['DB_password']
driver = '{ODBC Driver 13 for SQL Server}'
cnxn = pyodbc.connect(
    'DRIVER={0};PORT=1433;SERVER={1};PORT=1443;DATABASE={2};UID={3};PWD={4}'.format(driver, server, database, username,
                                                                                    password))
cursor = cnxn.cursor()
cursor.execute("""
SELECT  
    TestCase,
    DatabaseName,
    SolutionId,
    SolutionName,
    UnitTestCreatedBy,
    Result,
    TestExecutionTime 
FROM 
    [HLTools].[dbo].[DashboardUT] 
WHERE 
    DatabaseName in('ErpTst005', 'ErpTst001')
    and CAST(TestExecutionTime AS DATE) = CAST(GETDATE() AS DATE) 
    and Result = 'FAILURE'
""")
UT = cursor.fetchall()
# Axosoft Basic Data
client_id = config['client_id']
client_secret = config['client_secret']
password = config['Axosoft_password']
login = config['Axosoft_username']
axosoft_client = Axosoft(client_id, client_secret, 'hl-display')
axosoft_client.authenticate_by_password(login, password, scope='read')


# Ficzery
def count_days(date_string):
    # convert first 10 chars to date object
    date_object = datetime.strptime(date_string[:10], "%Y-%m-%d").date()
    # count number of days between today and step date
    # days_counter = (date.today() - date_object).days
    # exclude weekends
    excluded=(6, 7)
    d = date_object
    end = date.today()
    days = []
    while d <= end:
        if d.isoweekday() not in excluded:
            days.append(d)
        d += timedelta(days=1)
    return len(days) -1


arg1 = 'filter_id=379&release_id={0}&sort_fields=assigned_to'.format(
    release_id)
arg2 = 'columns=item_type,id,name,custom_296,remaining_duration,assigned_to'
f = axosoft_client.get('features', arguments='{0}&{1}'.format(arg1, arg2))

# remainig time == 0
ficzery2 = []
for item in f['data']:
    number = item['number']
    name = item['name']
    dev = item['assigned_to']['name']
    dev_ready_date_temp = item['custom_fields']['custom_296']
    remaining = item['remaining_duration']['value']
    if remaining == 0.0:
        # print(number, '  ', item_type, '  ', remaining, '  ', dev_ready_date)
        an_item = dict(ID=number, name=name, dev=dev, rem=remaining)
        ficzery2.append(an_item)

# Defekty
arg1 = 'filter_id=393&release_id={0}&sort_fields=assigned_to'.format(
    release_id)
arg2 = 'columns=item_type,id,name,custom_302,remaining_duration,assigned_to'
d = axosoft_client.get('defects', arguments='{0}&{1}'.format(arg1, arg2))

# remainig time == 0
defekty2 = []
for item in d['data']:
    if item['remaining_duration']['value'] == 0.0:
        number = item['number']
        name = item['name']
        dev = item['assigned_to']['name']
        remaining = item['remaining_duration']['value']
        an_item = dict(ID=number, name=name, dev=dev, rem=remaining)
        defekty2.append(an_item)

#  BTP
BTP = []
# BTP for defects
arg1 = 'filter_id=397&sort_fields=assigned_to'
arg2 = 'columns=item_type,id,name,custom_320,remaining_duration,assigned_to,name'
d_btp = axosoft_client.get('defects', arguments='{0}&{1}'.format(arg1, arg2))
for item in d_btp['data']:
    number = item['number']
    name = item['name']
    item_type = item['item_type']
    dev = item['assigned_to']['name']
    BTP_date = item['custom_fields']['custom_320']
    BTP_days = count_days(BTP_date)
    an_item = dict(ID=number, typ=item_type, dev=dev,
                   BTP_days=BTP_days, name=name)
    BTP.append(an_item)
    # print(number, '  ', item_type, '  ', dev, '  ', BTP_date)

# BTP for features
arg1 = 'filter_id=668&sort_fields=assigned_to'
arg2 = 'columns=item_type,id,name,custom_311,remaining_duration,assigned_to'
f_btp = axosoft_client.get('features', arguments='{0}&{1}'.format(arg1, arg2))
for item in f_btp['data']:
    number = item['number']
    name = item['name']
    item_type = item['item_type']
    dev = item['assigned_to']['name']
    BTP_date = item['custom_fields']['custom_311']
    BTP_days = count_days(BTP_date)
    an_item = dict(ID=number, typ=item_type, dev=dev,
                   BTP_days=BTP_days, name=name)
    BTP.append(an_item)
    # print(number, '  ', item_type, '  ', dev, '  ', BTP_date)

# Work Logs
start_date = datetime.strftime(datetime.now() - timedelta(1), '%Y-%m-%d')
end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
arg_hl = 'assigned_to_id=5&assigned_to_type=team&include_archived=true&start_date={0}&end_date={1}'.format(
    start_date, end_date)
arg_euvic = 'assigned_to_id=4&assigned_to_type=team&include_archived=true&start_date={0}&end_date={1}'.format(
    start_date, end_date)
arg_gung = 'assigned_to_id=8&assigned_to_type=team&include_archived=true&start_date={0}&end_date={1}'.format(
    start_date, end_date)
work_logs_hl = axosoft_client.get('work_logs', arguments=arg_hl)
work_logs_euvic = axosoft_client.get('work_logs', arguments=arg_euvic)
work_logs_gung = axosoft_client.get('work_logs', arguments=arg_gung)


def combine_results(work_log_data):
    if len(work_log_data) > 0:
        results = []
        for item in work_log_data:
            an_item = dict(
                user_name=item['user']['name'], duration=item['work_done']['duration'])
            results.append(an_item)
            global_results.append(an_item)
    else:
        pass


global_results = []
combine_results(work_logs_hl['data'])
combine_results(work_logs_euvic['data'])
combine_results(work_logs_gung['data'])
if len(global_results) > 0:
    result_data_frame = pd.DataFrame(global_results)
    result_data_frame_grouped = result_data_frame.groupby(['user_name']).sum()
    result_dictionary = result_data_frame_grouped.to_dict()
else:
    result_dictionary = {'duration': {}}

# Code review & internal test & BT
code_review = []
internal_test = []
bt_step = []
arg1 = 'release_id={0}'.format(release_id)
arg2 = 'columns=id,name,workflow_step,custom_257,custom_317,custom_314,custom_316'
arg2_defects = 'columns=id,name,workflow_step,custom_279,custom_319,custom_321,custom_324'
# cr "custom_321"
# it "custom_324"
# bt "custom_319"
step_data = axosoft_client.get(
    'features', arguments='{0}&{1}'.format(arg1, arg2))
step_data_defects = axosoft_client.get(
    'defects', arguments='{0}&{1}'.format(arg1, arg2_defects))
for item in step_data['data']:
    number = item['number']
    name = item['name']
    workflow_step = item['workflow_step']['name']
    system_tester = item['custom_fields']['custom_257']
    if workflow_step == 'Code Review':
        step_date_cr = item['custom_fields']['custom_314']
        step_days = count_days(step_date_cr)
        an_item = dict(item_id=number, item_name=name,
                       system_tester=system_tester, days=step_days)
        code_review.append(an_item)
    elif workflow_step == 'Business Tests':
        step_date_bt = item['custom_fields']['custom_317']
        step_days = count_days(step_date_bt)
        an_item = dict(item_id=number, item_name=name,
                       system_tester=system_tester, days=step_days)
        bt_step.append(an_item)
    elif workflow_step == 'Internal Tests':
        step_date_it = item['custom_fields']['custom_316']
        step_days = count_days(step_date_it)
        an_item = dict(item_id=number, item_name=name,
                       system_tester=system_tester, days=step_days)
        internal_test.append(an_item)
for item in step_data_defects['data']:
    number = item['number']
    name = item['name']
    workflow_step = item['workflow_step']['name']
    system_tester = item['custom_fields']['custom_279']
    if workflow_step == 'Code Review':
        step_date_cr = item['custom_fields']['custom_321']
        step_days = count_days(step_date_cr)
        an_item = dict(item_id=number, item_name=name,
                       system_tester=system_tester, days=step_days)
        code_review.append(an_item)
    elif workflow_step == 'Business Tests':
        step_date_bt = item['custom_fields']['custom_319']
        step_days = count_days(step_date_bt)
        an_item = dict(item_id=number, item_name=name,
                       system_tester=system_tester, days=step_days)
        bt_step.append(an_item)
    elif workflow_step == 'Internal Tests':
        step_date_it = item['custom_fields']['custom_324']
        step_days = count_days(step_date_it)
        an_item = dict(item_id=number, item_name=name,
                       system_tester=system_tester, days=step_days)
        internal_test.append(an_item)

# HTML
TEMPLATE = """
<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;border-color:#ccc;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:#ccc;color:#333;background-color:#fff;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:#ccc;color:#333;background-color:#f0f0f0;}
.tg .tg-s6z2{text-align:center}
.tg .tg-yw4l{vertical-align:top}
</style>
<h1>UT:</h1>
<table class="tg">
  <tr>
    <th class="tg-yw4l">Name</th>
    <th class="tg-yw4l">Database</th>
    <th class="tg-yw4l">ID</th>
    <th class="tg-yw4l">Name</th>
    <th class="tg-yw4l">Dev</th>
    <th class="tg-yw4l">Result</th>
    <th class="tg-yw4l">Date</th>
  </tr>
{% for row in UT %}
  <tr>
    <td class="tg-yw4l">{{row["TestCase"]}}</td>
    <td class="tg-yw4l">{{row["DatabaseName"]}}</td>
    <td class="tg-yw4l">{{row["SolutionId"]}}</td>
    <td class="tg-yw4l">{{row["SolutionName"]}}</td>
    <td class="tg-yw4l">{{row["UnitTestCreatedBy"]}}</td>
    <td class="tg-yw4l">{{row["Result"]}}</td>
    <td class="tg-yw4l">{{row["TestExecutionTime"]}}</td>
  </tr>
{% endfor %}
</table>
<h1>Code Review</h1>
<table class="tg">
  <tr>
    <th class="tg-yw4l">ID</th>
    <th class="tg-yw4l">Name</th>
    <th class="tg-yw4l">System Tester</th>
    <th class="tg-yw4l">Days</th>
  </tr>
{% for row in code_review %}
  <tr>
    <td class="tg-yw4l">{{row.item_id}}</td>
    <td class="tg-yw4l">{{row.item_name}}</td>
    <td class="tg-yw4l">{{row.system_tester}}</td>
    <td class="tg-yw4l">{{row.days}}</td>
  </tr>
{% endfor %}
</table>
<h1>Internal Tests</h1>
<table class="tg">
  <tr>
    <th class="tg-yw4l">ID</th>
    <th class="tg-yw4l">Name</th>
    <th class="tg-yw4l">System Tester</th>
    <th class="tg-yw4l">Days</th>
  </tr>
{% for row in internal_tests %}
  <tr>
    <td class="tg-yw4l">{{row.item_id}}</td>
    <td class="tg-yw4l">{{row.item_name}}</td>
    <td class="tg-yw4l">{{row.system_tester}}</td>
    <td class="tg-yw4l">{{row.days}}</td>
  </tr>
{% endfor %}
</table>
<h1>Business Tests</h1>
<table class="tg">
  <tr>
    <th class="tg-yw4l">ID</th>
    <th class="tg-yw4l">Name</th>
    <th class="tg-yw4l">System Tester</th>
    <th class="tg-yw4l">Days</th>
  </tr>
{% for row in bt_step %}
  <tr>
    <td class="tg-yw4l">{{row.item_id}}</td>
    <td class="tg-yw4l">{{row.item_name}}</td>
    <td class="tg-yw4l">{{row.system_tester}}</td>
    <td class="tg-yw4l">{{row.days}}</td>
  </tr>
{% endfor %}
</table>
<h1>Features - No hours</h1>
<table class="tg">
  <tr>
    <th class="tg-yw4l">Developer</th>
    <th class="tg-yw4l">ID</th>
    <th class="tg-yw4l">Name</th>
    <th class="tg-yw4l">Time Remaining</th>
  </tr>
{% for row in ficzery2 %}
  <tr>
    <td class="tg-yw4l">{{row.dev}}</td>
    <td class="tg-yw4l">{{row.ID}}</td>
    <td class="tg-yw4l">{{row.name}}</td>
    <td class="tg-yw4l">{{row.rem}}</td>
  </tr>
{% endfor %}
</table>
<h1>Defects - No hours</h1>
<table class="tg">
  <tr>
    <th class="tg-yw4l">Developer</th>
    <th class="tg-yw4l">ID</th>
    <th class="tg-yw4l">Name</th>
    <th class="tg-yw4l">Time Remaining</th>
  </tr>
{% for row in defekty2 %}
  <tr>
    <td class="tg-yw4l">{{row.dev}}</td>
    <td class="tg-yw4l">{{row.ID}}</td>
    <td class="tg-yw4l">{{row.name}}</td>
    <td class="tg-yw4l">{{row.rem}}</td>
  </tr>
{% endfor %}
</table>
<h1>BTP:</h1>
<table class="tg">
  <tr>
    <th class="tg-yw4l">Developer</th>
    <th class="tg-yw4l">Type</th>
    <th class="tg-yw4l">ID</th>
    <th class="tg-yw4l">Name</th>
    <th class="tg-yw4l">Days</th>
  </tr>
{% for row in BTP %}
  <tr>
    <td class="tg-yw4l">{{row["dev"]}}</td>
    <td class="tg-yw4l">{{row["typ"]}}</td>
    <td class="tg-yw4l">{{row["ID"]}}</td>
    <td class="tg-yw4l">{{row["name"]}}</td>
    <td class="tg-yw4l">{{row["BTP_days"]}}</td>
  </tr>
{% endfor %}
</table>
<h1>Work Logs:</h1>
<table class="tg">
  <tr>
    <th class="tg-yw4l">Developer</th>
    <th class="tg-yw4l">Work Log</th>
  </tr>
{% for key, value in result_dictionary.items() %}
  <tr>
    <td class="tg-yw4l">{{key}}</td>
    <td class="tg-yw4l">{{value}}</td>
  </tr>
{% endfor %}
</table>
"""  # Our HTML Template

# Create a text/html message from a rendered template
msg = MIMEText(
    Environment().from_string(TEMPLATE).render(
        title='Hello World!', ficzery2=ficzery2, defekty2=defekty2, UT=UT, BTP=BTP,
        result_dictionary=result_dictionary['duration'], code_review=code_review, bt_step=bt_step, 
        internal_tests=internal_test
    ), "html"
)
# e-mail
COMMASPACE = ', '
subject = "UT, BTP, No hours"
sender = "Dev_statistics@hl-display.com"
# recipient = ["dawid.wybierek@hl-display.com"]
recipient = ["gliwiceitall@hl-display.com"]
# recipient = ["devs@hl-display.com", "julia.homik@hl-display.com", "GliwiceSupp@hl-display.com"]

msg['Subject'] = subject
msg['From'] = sender
msg['To'] = COMMASPACE.join(recipient)

# Send the message via our own local SMTP server.
s = SMTP('smtp.hl-display.com')
s.send_message(msg)
s.quit()
print("Email was sent to", recipient)
