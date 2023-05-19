import pandas as pd
from Axo import Axosoft
import json
import csv
import os
from smtplib import SMTP              # sending email
from email.mime.text import MIMEText  # constructing messages
from jinja2 import Environment        # Jinja2 templating
from shutil import copyfile

# Copy new file from sharepoint to local folder
cab_sharepoint_path = 'C:\\Users\\poca\\HL Display AB\\IT Documentation Repository - CAB\\CAB REQUESTS.xlsx'  # PROD
cab_local_path = 'C:\\jenkins\\apps\\cab_time_counter\\CAB REQUESTS.xlsx'  # PROD
# cab_sharepoint_path = 'C:\\Users\\dawy\\HL Display AB\\IT Documentation Repository - CAB\\CAB REQUESTS.xlsx'  # TEST
# cab_local_path = 'C:\\Users\\dawy\\Desktop\\my_stuff\\skrypty\\Test-tools\\CAB_time_counter\\CAB REQUESTS.xlsx'  # TEST
try:
    os.remove(cab_local_path)
    info_text = "Old CAB file removed from {0}".format(cab_local_path)
except OSError:
    info_text = "Nothing to remove"
print(info_text)
copyfile(cab_sharepoint_path, cab_local_path)
# open config file
with open('config.json') as data_file:
    config = json.load(data_file)
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
    "read%20write"
)
# prepare dictionaries
prio_list = axosoft_client.get('picklists', element='priority')['data']

# List of tabs
tab_list = ['Sales and Quotation', 'Logistics and Purchasing', 'Marketing', 'Production', 'Finance', 'HR', 'IT']

master_results = []
headers = ['Row_ID', 'Prio', 'Decission', 'Decission Date', 'Feature Number', 'Axosoft item Number', 'Status',
           'Completion Date', 'CBM Stream', 'Axo_Prio']
master_results.append(headers)
for tab_name in tab_list:
    # print('##################### {0} #####################'.format(tab_name))
    # Prepare data frame
    df = pd.read_excel('CAB REQUESTS.xlsx', sheet_name=tab_name, header=2)
    # remove blank lines
    df1 = df.dropna(how='all')
    df_tmp = df1[df1['Decision'].str.contains('YES', na=False) & df1['Decision date'].notnull() & df1[
        'Feature ID'].notnull()]  # filter dataFrame
    df_final_tmp = df_tmp[['Prio', 'Decision', 'Decision date', 'Feature ID']]
    df_final = df_final_tmp.replace(to_replace=r'\n', value='$', regex=True)
    df_final['Feature ID'] = df_final['Feature ID'].replace(to_replace=r',', value='$', regex=True)
    try:
        df_final['Prio'] = df_final['Prio'].astype(int)
    except ValueError:
        pass
    df_final.to_csv('{0}.csv'.format(tab_name))
    # print(df_final)

    # prepare data
    data = []
    with open('{0}.csv'.format(tab_name), 'r') as csvFile:
        reader = csv.reader(csvFile)
        for row in reader:
            f_num = row[4]
            x = f_num.split('$')
            if len(x) == 1:
                data.append(row)
            else:
                for item in x:
                    if item == '':
                        pass
                    else:
                        temp = [row[0], row[1], row[2], row[3], item]
                        data.append(temp)

    # Remove file
    os.remove('{0}.csv'.format(tab_name))

    results = []
    for item in data:
        if item[2] == 'Decision':  # need to change headers !!
            pass
        else:
            # make call
            item4 = int(float(item[4]))  # need to convert like this because of excel
            try:
                test = axosoft_client.get('features', resourse_id=item4)
                f_number = test['data']['number']
                f_step_tmp = test['data']['workflow_step']['id']
                test2 = axosoft_client.get('workflow_steps', resourse_id=f_step_tmp)
                f_step = test2['data']['name']
                f_completion_date = test['data']['completion_date']
                f_prio_id = test['data']['priority']['id']
                f_prio = ''
                for d in prio_list:
                    if d['id'] == f_prio_id:
                        f_prio = d['name']
                item.append(f_number)
                item.append(f_step)
                try:
                    item.append(f_completion_date[0:10])
                except TypeError:
                    item.append(f_completion_date)
                item.append(tab_name)
                item.append(f_prio)
                results.append(item)
            except ValueError:
                pass

    for row in results:
        master_results.append(row)


final_data = pd.DataFrame(master_results[1:])
final_data.columns = master_results[0]
final_data['Completion Date'] = pd.to_datetime(final_data['Completion Date'], format='%Y/%m/%d')
final_data['Decission Date'] = pd.to_datetime(final_data['Decission Date'], format='%d/%m/%Y')
final_data['Time spent'] = final_data['Completion Date'] - final_data['Decission Date']
test_df = final_data.dropna()
test_df.to_csv('debug.csv')
cbm_streams = test_df['CBM Stream'].unique()
print(cbm_streams)
cbm_results = []
for stream in cbm_streams:
    stream_df = test_df[test_df['CBM Stream'].str.contains(stream)]
    stream_prios = stream_df['Prio'].unique()
    an_item = dict(cbm_stream=stream)
    for prio in stream_prios:
        prio_df = stream_df[stream_df['Prio'].str.contains(prio)]
        average = prio_df['Time spent'].mean()
        an_item[prio] = int(average.days)
    cbm_results.append(an_item)

prio_list_tmp = ['1', '2', '3', '4', '5']
for item in cbm_results:
    for priority in prio_list_tmp:
        if priority in item:
            pass
        else:
            item[priority] = '-'

# HTML

TEMPLATE = """
<style type="text/css">
.tg  {border-collapse:collapse;border-spacing:0;border-color:#ccc;}
.tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:#ccc;color:#333;background-color:#fff;}
.tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:#ccc;color:#333;background-color:#f0f0f0;}
.tg .tg-s6z2{text-align:center}
.tg .tg-yw4l{vertical-align:top}
</style>
<h2>Days to implementation</h2>
<table class="tg">
  <tr>
    <th class="tg-yw4l">Stream</th>
    <th class="tg-yw4l">Prio 5</th>
    <th class="tg-yw4l">Prio 4</th>
    <th class="tg-yw4l">Prio 3</th>
    <th class="tg-yw4l">Prio 2</th>
    <th class="tg-yw4l">Prio 1</th>
  </tr>
{% for row in cbm_results %}
  <tr>
    <td class="tg-yw4l">{{row.cbm_stream}}</td>
    <td class="tg-yw4l">{{row["5"]}}</td>
    <td class="tg-yw4l">{{row["4"]}}</td>
    <td class="tg-yw4l">{{row["3"]}}</td>
    <td class="tg-yw4l">{{row["2"]}}</td>
    <td class="tg-yw4l">{{row["1"]}}</td>
  </tr>
{% endfor %}
</table>
"""  # Our HTML Template

# Create a text/html message from a rendered template
msg = MIMEText(
    Environment().from_string(TEMPLATE).render(
        title='Hello World!', cbm_results=cbm_results
    ), "html"
)

# e-mail

COMMASPACE = ', '

subject = "CAB - days to implement RFC"
sender = "Jenkins@hl-display.com"
# recipient = ["dawid.wybierek@hl-display.com"]
recipient = ["Dawid.Wybierek@hl-display.com", "Kamil.Saczka@hl-display.com", "Marcin.Pianka@hl-display.com", "Pawel.Nowak@hl-display.com", "Kinga.Lesniewska@hl-display.com"]

msg['Subject'] = subject
msg['From'] = sender
msg['To'] = COMMASPACE.join(recipient)

# Send the message via our own local SMTP server.
s = SMTP('smtp.hl-display.com')
s.send_message(msg)
s.quit()
print("Emal was sent")

