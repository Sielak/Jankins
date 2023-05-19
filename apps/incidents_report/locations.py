import requests
import json
from functions import connect_to_sql_server

api_key = "Zpll1RafGc3UY8CoSRV"
URL = "https://hldisplayab.freshservice.com/api/v2/"
password = "x"
counter = 1
cursor = connect_to_sql_server('Reports').cursor()
cursor.execute("DELETE FROM freshservice_locations")  # Truncate table
cursor.execute("INSERT INTO freshservice_locations VALUES (?,?)", (0, 'Blank'))  # start values
while True:
    r = requests.get(
        URL + "locations?per_page=100&page={0}".format(counter),
        auth=(api_key, password))
    if r.status_code == 200:
        # print("Request processed successfully, the response is given below")
        # print(r.content)
        response_raw = json.loads(r.content)
        response = response_raw['locations']
        if len(response) == 0:
            break
        print('Page:', counter, 'Items:', len(response))
        for item in response:
            location_id = item['id']
            location_name = item['name']
            cursor.execute("INSERT INTO freshservice_locations VALUES (?,?)", (
                location_id,
                location_name
                ))  # insert row
    else:
        print("Failed to read tickets, errors are displayed below,")
        print(r)
        # print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))
    counter += 1
cursor.commit()  # save changes
