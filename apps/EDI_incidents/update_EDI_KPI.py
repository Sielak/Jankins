from lib.Axosoft_lib import Axosoft
import json
import sqlite3 as sql
import requests
from datetime import date, timedelta


# BASIC DATA
with open('config.json') as data_file:
    config = json.load(data_file)

db_path = config['path2db']  # PROD
# db_path = config['path2db_test']  # TEST


def save2db(connection, arg1, arg2, arg3, arg4, arg5):
    c = connection.cursor()
    # Insert a row of data
    c.execute("INSERT INTO EDI_KPI VALUES (?, ?, ?, ?, ?);", (arg1, arg2, arg3, arg4, arg5))
    connection.commit()


def initial_upload(filter):
    r = requests.get(URL + "tickets/view/{0}?format=json&page={1}".format(filter, counter), auth=(api_key, password))
    if r.status_code == 200:
        # response = json.loads(r.content)
        response = r.json()
        page = len(response)
        conn = sql.connect(db_path)
        for item in response:
            inc_id = item['display_id']
            inc_type = item['sub_category']
            inc_prio = item['priority'] + 1
            if inc_prio == 5:
                inc_prio = '5 - high'
            inc_created = item['created_at'][:10]
            inc_completion = item['updated_at'][:10]
            print(inc_id, inc_type, inc_prio, inc_created, inc_completion, type(inc_prio))
            # save2db(conn, inc_id, inc_type, inc_prio, inc_created, inc_completion)
        conn.close()
    else:
        print("Failed to read tickets, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))
    return page


def daily_upload(filter):
    r = requests.get(URL + "tickets/view/{0}?format=json&page={1}".format(filter, counter), auth=(api_key, password))
    if r.status_code == 200:
        # response = json.loads(r.content)
        response = r.json()
        page = len(response)
        conn = sql.connect(db_path)
        for item in response:
            inc_id = item['display_id']
            inc_type = item['sub_category']
            inc_prio = item['priority'] + 1
            if inc_prio == 5:
                inc_prio = '5 - high'
            inc_created = item['created_at'][:10]
            inc_completion = item['updated_at'][:10]
            yesterday = date.today() - timedelta(days=1)
            yesterday.strftime('%Y-%m-%d')
            if inc_completion == str(yesterday):
                print(inc_id, inc_type, inc_prio, inc_created, inc_completion)
                save2db(conn, inc_id, inc_type, inc_prio, inc_created, inc_completion)
            else:
                pass
        conn.close()
    else:
        print("Failed to read tickets, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))
    return page


api_key = config['FS_API_key']
URL = config['FS_URL']
password = config['FS_pass']
filter_no_ext = config['FS_filter_id_external']
filter_no_inte = config['FS_filter_id_internal']
# Initial upload
#counter = 1
#while True:
#    checker = initial_upload(filter_no_ext)
#    if checker == 0:
#        break
#    counter += 1
#counter = 1
#while True:
#    checker = initial_upload(filter_no_inte)
#    if checker == 0:
#        break
#    counter += 1

# Daily upload
counter = 1
while True:
    checker = daily_upload(filter_no_ext)
    if checker == 0:
        break
    counter += 1
counter = 1
while True:
    checker = daily_upload(filter_no_inte)
    if checker == 0:
        break
    counter += 1

