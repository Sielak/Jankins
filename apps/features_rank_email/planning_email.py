from lib.Axosoft_lib import Axosoft
from smtplib import SMTP  # sending email
from email.mime.text import MIMEText  # constructing messages
from jinja2 import Environment  # Jinja2 templating
import json
from operator import itemgetter
from datetime import datetime
from datetime import timedelta
import sqlite3 as sql
import sys


with open('config.json') as data_file:
    config = json.load(data_file)


def send_email(results_data, choosed_recipant='gliwice_all'):
    # HTML
    TEMPLATE = """
    <style type="text/css">
    .tg  {border-collapse:collapse;border-spacing:0;border-color:#ccc;}
    .tg td{font-family:Arial, sans-serif;font-size:14px;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:#ccc;color:#333;background-color:#fff;}
    .tg th{font-family:Arial, sans-serif;font-size:14px;font-weight:normal;padding:10px 5px;border-style:solid;border-width:1px;overflow:hidden;word-break:normal;border-color:#ccc;color:#333;background-color:#f0f0f0;}
    .tg .tg-s6z2{text-align:center}
    .tg .tg-yw4l{vertical-align:top}
    </style>
    <h1>Planning list:</h1>
    <table class="tg">
      <tr>
        <th class="tg-yw4l">Rank</th>
        <th class="tg-yw4l">Trend</th>
        <th class="tg-yw4l">Number</th>
        <th class="tg-yw4l">Project</th>
        <th class="tg-yw4l">Step</th>
        <th class="tg-yw4l">Sprint</th>
        <th class="tg-yw4l">Name</th>
        <th class="tg-yw4l">Env</th>
      </tr>
    {% for row in results %}
      <tr>
        <td class="tg-yw4l">{{row.item_rank}}</td>
        {% if 'sign' in row %}
            {% if "UP" in row.sign %}
                <td class="tg-yw4l"> ▲ </td>
            {% elif "DOWN" in row.sign %}
                <td class="tg-yw4l"> ▼ </td>
            {% elif "=" in row.sign %}
                <td class="tg-yw4l"> ➤ </td>
            {% else %}
                <td class="tg-yw4l"> {{row.sign}} </td>
            {% endif %}
        {% else %}
            <td class="tg-yw4l"> ➤ </td>
        {% endif %}
        <td class="tg-yw4l">{{row.item_number}}</td>
        <td class="tg-yw4l">{{row.item_project}}</td>
        <td class="tg-yw4l">{{row.item_step}}</td>
        <td class="tg-yw4l">{{row.item_sprint}}</td>
        <td class="tg-yw4l">{{row.item_name}}</td>
        <td class="tg-yw4l">{{row.item_env}}</td>
      </tr>
    {% endfor %}
    </table>
    """  # Our HTML Template

    # Create a text/html message from a rendered template
    msg = MIMEText(
        Environment().from_string(TEMPLATE).render(
            title='Planning list', results=results_data), "html"
    )
    # e-mail
    COMMASPACE = ', '
    subject = "Planning Lista"
    sender = "Sprint_statistics@hl-display.com"
    tester = ["dawid.wybierek@hl-display.com"]
    gliwice_all = ["gliwiceitall@hl-display.com"]
    devs_and_supp = ["devs@hl-display.com",
                     "julia.homik@hl-display.com", "GliwiceSupp@hl-display.com"]

    if choosed_recipant == 'gliwice_all':
        recipient = gliwice_all
    elif choosed_recipant == 'tester':
        recipient = tester
    elif choosed_recipant == 'devs_and_supp':
        recipient = devs_and_supp
    else:
        recipient = gliwice_all

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = COMMASPACE.join(recipient)

    # Send the message via our own local SMTP server.
    s = SMTP('smtp.hl-display.com')
    s.send_message(msg)
    s.quit()
    print("Email was sent to", recipient)

def fetch_sprint_id():
    db_path = config['path2db']
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
    sprint_id = cur.fetchone()[0]
    
    return sprint_id


def fetch_data():
    client_id = config['client_id']
    client_secret = config['client_secret']
    password = config['Axosoft_password']
    login = config['Axosoft_username']

    axosoft_client = Axosoft(client_id, client_secret, 'hl-display')
    axosoft_client.authenticate_by_password(login, password, scope='read')
    sprint_id = fetch_sprint_id()
    # features args for API request
    f_arg1 = "release_id={0}".format(sprint_id)
    f_arg2 = "columns=number,is_ranked,rank,workflow_step,release,name,project,custom_301"
    f_arg3 = "sort_fields=rank"
    # API call
    features_result = axosoft_client.get(
        "features", arguments="{0}&{1}&{2}".format(f_arg1, f_arg2, f_arg3))
    # Data for HTML table
    results = []
    for item in features_result['data']:
        if item['is_ranked'] is True and item['release']['name'] is not None:
            an_item = dict(item_rank=item['rank'],
                           item_number=item['number'],
                           item_project=item['project']['name'],
                           item_step=item['workflow_step']['name'],
                           item_sprint=item['release']['name'],
                           item_name=item['name'],
                           item_env=item['custom_fields']['custom_301'])
            results.append(an_item)
        else:
            pass

    results_sorted = sorted(results, key=itemgetter('item_rank'))
    results2 = add_rank_int(results_sorted)

    return results2


def add_rank_int(list_of_dict):
    for item in list_of_dict:
        item_rank_int = list_of_dict.index(item)
        item['item_rank_int'] = item_rank_int

    return list_of_dict


def save_result_to_file(results_data):
    with open('data.json', 'w', encoding='utf-8') as f:
        json.dump(results_data, f, ensure_ascii=False, indent=4)


def search_in_dict_old(list_name, id2search):
    test1 = [d['item_rank']
             for d in list_name if d['item_number'] == id2search]

    return test1[0]


def search_in_dict(list_name, id2search):
    test1 = [d['item_rank_int']
             for d in list_name if d['item_number'] == id2search]

    return test1[0]


def compare_results_old(old_list, new_list):
    res = []
    for item in new_list:
        item_rank = int(item['item_rank'])
        item_id = item['item_number']
        try:
            item_rank_old = search_in_dict(old_list, item_id)
            if item_rank > int(item_rank_old):
                item['sign'] = 'DOWN'
            elif item_rank < int(item_rank_old):
                item['sign'] = 'UP'
            else:
                item['sign'] = '='
        except IndexError:
            item['sign'] = 'new'
        res.append(item)

    results_sorted = sorted(res, key=itemgetter('item_rank'))

    return results_sorted


def compare_results(old_list, new_list):
    res = []
    for item in new_list:
        item_rank = int(item['item_rank_int'])
        item_id = item['item_number']
        try:
            item_rank_old = search_in_dict(old_list, item_id)
            if item_rank > int(item_rank_old):
                item['sign'] = 'DOWN'
            elif item_rank < int(item_rank_old):
                item['sign'] = 'UP'
            else:
                item['sign'] = '='
        except IndexError:
            item['sign'] = 'new'
        res.append(item)
    results_sorted = sorted(res, key=itemgetter('item_rank'))

    return results_sorted


def search_for_deleted_items(old_list, new_list):
    deleted_items_list = []
    for item in old_list:
        item_id = item['item_number']
        try:
            search_in_dict(new_list, item_id)
        except IndexError:
            item['sign'] = 'Removed'
            deleted_items_list.append(item)

    return deleted_items_list


def check_date(start_date):
    result_dates = []
    start_date_object = datetime.strptime(start_date, '%d/%m/%Y')
    for i in range(0, 100):
        end_date = start_date_object + timedelta(days=14)
        result_dates.append(end_date.date())
        start_date_object = end_date
        i += 1

    return result_dates


dates_sprint_starts = check_date(config['date_for_calculating_Sprint_start'])
dates_sprint_ends = check_date(config['date_for_calculating_Sprint_end'])
today = datetime.today().date()
try:
    force = sys.argv[1]
except IndexError:
    force = "None"
if force == '-force_end':
    print('Forced end of sprint')
    results_new = fetch_data()
    with open('data.json') as data_file:
        results_old = json.load(data_file)
    results_final = compare_results(results_old, results_new)
    deleted = search_for_deleted_items(results_old, results_new)
    for item in deleted:
        results_final.append(item)
    send_email(results_final, choosed_recipant='tester')
elif force == '-force_start':
    print('Forced start of sprint')
    results = fetch_data()
    save_result_to_file(results)
    send_email(results, choosed_recipant='tester')
else:
    if today in dates_sprint_starts:
        print('Today is first day of sprint, fetching data')
        results = fetch_data()
        save_result_to_file(results)
        send_email(results)
    elif today in dates_sprint_ends:
        print('Today is last day of sprint, sending email')
        results_new = fetch_data()
        with open('data.json') as data_file:
            results_old = json.load(data_file)
        results_final = compare_results(results_old, results_new)
        deleted = search_for_deleted_items(results_old, results_new)
        for item in deleted:
            results_final.append(item)
        print('DEBUG', len(results_final))
        for item in results_final:
            print(item)
        send_email(results_final)
    else:
        print('Normal sprint day')

