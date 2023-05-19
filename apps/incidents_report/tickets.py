import requests
import json
import time
from functions import connect_to_sql_server

api_key = "Zpll1RafGc3UY8CoSRV"
URL = "https://hldisplayab.freshservice.com/api/v2/"
password = "x"
counter = 1
cursor = connect_to_sql_server('Reports').cursor()
cursor.execute("DELETE FROM freshservice_tickets")  # Truncate table
while True:
    r = requests.get(
        URL + "tickets?include=stats&updated_since=2019-04-01&per_page=100&page={0}".format(counter),
        auth=(api_key, password))
    if r.status_code == 200:
        # print("Request processed successfully, the response is given below")
        # print(r.content)
        response_raw = json.loads(r.content)
        response = response_raw['tickets']
        if len(response) == 0:
            break
        print('Page:', counter, 'Items:', len(response))
        for item in response:
            item_category = item['category']
            item_closed_at = item['stats']['closed_at']
            item_created_at = item['created_at']
            item_id = item['id']
            item_first_responded_at = item['stats']['first_responded_at']
            item_category2 = item['item_category']  # ??
            item_reason_code_for_closing = item['custom_fields']['reason_code_for_closing']
            item_requester_id = item['requester_id']
            item_resolution_time_in_secs = item['stats']['resolution_time_in_secs']
            item_resolved_at = item['stats']['resolved_at']
            item_status = item['status']
            item_sub_category = item['sub_category']
            item_type = item['type']
            item_subject = item['subject']
            cursor.execute("INSERT INTO freshservice_tickets VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (
                item_category,
                item_closed_at,
                item_created_at,
                item_id,
                item_first_responded_at,
                item_category2,
                item_reason_code_for_closing,
                item_requester_id,
                item_resolution_time_in_secs,
                item_resolved_at,
                item_status,
                item_sub_category,
                item_type,
                item_subject
                ))  # insert row
    elif r.status_code == 429:
        print("Rate limit exceeded, Sleeping for 60 sek")
        time.sleep(60)
    else:
        print("Failed to read tickets, errors are displayed below,")
        print(r.text)
        # print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))
    counter += 1
cursor.commit()  # save changes
