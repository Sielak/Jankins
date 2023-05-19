import requests
import json
from mails import Mail
import csv
import shutil


# basic data
with open('config.json') as data_file:
    config = json.load(data_file)
api_key = config['Freshservice_api_key']
root_url = config['Freshservice_api_url']
root_url_v1 = config['Freshservice_api_url_v1']
password = config['Freshservice_api_password']

change_statuses = [
    {
        "name": "Open",
        "id": 1
    },
    {
        "name": "Planning",
        "id": 2
    },
    {
        "name": "Awaiting Approval",
        "id": 3
    },
    {
        "name": "Pending Release",
        "id": 4
    },
    {
        "name": "Pending Review",
        "id": 5
    },
    {
        "name": "closed",
        "id": 6
    }
]

def look4name(status_id):
    """Look for change status name by its id  
        ## Parameters:   
        `status_id` : int    
        ## Returns:  
        `string` [change status name]  
        """
    for item in change_statuses:
        if item['id'] == status_id:
            return item['name']

def fetch_changes():
    """Fetch all changes from FreshService    
        ## Returns:  
        `list` [List of dicts with change information]  
        """
    results = []
    counter = 1
    while True:
        r = requests.get(root_url + "changes?include=custom_fields&updated_since=2019-04-01&per_page=100&page={0}".format(counter), auth=(api_key, password))
        if r.status_code == 200:
            response_raw = json.loads(r.content)
            response = response_raw['changes']
            print('Page:', counter, 'Items:', len(response))
            if len(response) == 0:
                break
            for item in response:
                change_id = item['id']        
                results.append(fetch_one_change(change_id))
        else:
            print("Failed to read tickets, errors are displayed below,")
            print(r.text)
            print("x-request-id : " + r.headers['x-request-id'])
            print("Status Code : " + str(r.status_code))
            break
        counter += 1

    return results

def fetch_one_change(change_id):
    """Fetch info about specific change in FreshService  
        ## Parameters:   
        `change_id` : int    
        ## Returns:  
        `dict` [change id, change status, feature number]  
        """
    r = requests.get(root_url + "changes/{0}".format(change_id), auth=(api_key, password))
    if r.status_code == 200:
        response_raw = json.loads(r.content)
        response = response_raw['change']
        change_id = response['id']
        change_status = look4name(response['status'])
        change_feature_number = response['custom_fields']['feature_id']
        change_stream = response['custom_fields']['stream']
        change_step = response['custom_fields']['step']
        hl_payer = response['custom_fields']['msf_hl_unit_payer_2']
        est_dev_hrs = response['custom_fields']['est_dev_hrs']
        est_cost_sek = response['custom_fields']['est_cost_sek']
        comment = response['custom_fields']['comment']
        subject = response['subject']
        change = {
            "id": change_id,
            "status_id": response['status'],
            "status": change_status,
            "feature_number": change_feature_number,
            "stream": change_stream,
            "step": change_step,
            "subject": subject,
            "hl_payer": hl_payer,
            "est_dev_hrs": est_dev_hrs,
            "est_cost_sek": est_cost_sek,
            "comment": comment
        }
        return change
    else:
        print("Failed to read tickets, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))


res = fetch_changes()

# Send csv by email
# mail_object = Mail('dawid.wybierek@hl-display.com')
# print(mail_object.rfc_report(res))
# Genarte CSV to file
if len(res) > 0:
    # save list as csv
    keys = res[0].keys()
    with open('cache/rfc_data.csv', 'w', newline='')  as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(res)
    shutil.move('cache/rfc_data.csv', "C:/reports/rfc_data.csv")