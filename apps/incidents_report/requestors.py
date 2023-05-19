import requests
import json
from functions import connect_to_sql_server

api_key = "Zpll1RafGc3UY8CoSRV"
URL = "https://hldisplayab.freshservice.com/api/v2/"
password = "x"
counter = 1
cursor = connect_to_sql_server('Reports').cursor()
cursor.execute("DELETE FROM freshservice_requesters")  # Truncate table
while True:
    r = requests.get(
        URL + "requesters?per_page=100&page={0}".format(counter),
        auth=(api_key, password))
    if r.status_code == 200:
        # print("Request processed successfully, the response is given below")
        # print(r.content)
        response_raw = json.loads(r.content)
        response = response_raw['requesters']
        if len(response) == 0:
            break
        print('Page:', counter, 'Items:', len(response))
        for item in response:
            requester_id = item['id']
            requester_company = item['custom_fields']['company']
            location_id = item['location_id']
            name = str(item['first_name']) + ' ' + str(item['last_name'])
            cursor.execute("INSERT INTO freshservice_requesters VALUES (?,?,?,?)", (
                requester_id,
                requester_company,
                location_id,
                name
                ))  # insert row
    else:
        print("Failed to read tickets, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))
    counter += 1
cursor.commit()  # save changes
