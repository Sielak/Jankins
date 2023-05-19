"""Axosoft <> Freshservice Integration

This script is used to close freshservice RFC everytime all features assigned
to RFC are closed in Axosoft.

Script is runned daily by jenkins job

Credentials configuration is holded in config.json file.
"""
from Axo import Axosoft
import json
import requests


# basic data
with open('config.json') as data_file:
    config = json.load(data_file)
api_key = config['Freshservice_api_key']
root_url = config['Freshservice_api_url']
root_url_v1 = config['Freshservice_api_url_v1']
password = config['Freshservice_api_password']

# Connect to axosoft
axosoft_client = Axosoft(
    config['Axosoft_client_id'],
    config['Axosoft_client_secret'],
    'hl-display'
)
# Authenticate in axosoft
axosoft_client.authenticate_by_password(
    config['Axosoft_username'],
    config['Axosoft_password'],
    "read"
)

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
                change_status = item['status']
                if change_status != 6:
                    an_item = fetch_one_change(change_id)            
                    results.append(an_item)
        else:
            print("Failed to read tickets, errors are displayed below,")
            print(r)
            print("x-request-id : " + r.headers['x-request-id'])
            print("Status Code : " + str(r.status_code))
        counter += 1

    return results

def fetch_one_change(change_id, debug=False):
    """Fetch

    Args:
        change_id (int): change id to fetch data
        debug (bool, optional): If debug true then return all change data. Defaults to False.

    Returns:
        dict: dict with change id, change status, feature number or json is debug is True
    """    
    r = requests.get(root_url + "changes/{0}".format(change_id), auth=(api_key, password))
    if r.status_code == 200:
        response_raw = json.loads(r.content)
        response = response_raw['change']
        change_id = response['id']
        change_status = look4name(response['status'])
        change_feature_number = response['custom_fields']['feature_id']
        if debug is True:
            return response_raw
        change = {
            "id": change_id,
            "status_id": response['status'],
            "status": change_status,
            "feature_number": change_feature_number
        }
        return change
    else:
        print("Failed to read tickets, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))

def update_change_status(change_id, release_info):
    """Update FreshService change status to completed  
        ## Parameters:   
        `change_id` : int    
        """
    data = {
        "status": 6,
        "custom_fields": {
            "release_2": release_info,
            "step": "Implemented"
        }
    }
    headers = {
            'content-type': 'application/json'
        }
    r = requests.put(root_url + "changes/{0}".format(change_id), auth=(api_key, password), data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        response_raw = json.loads(r.content)
        if 'errors' in response_raw:
            print("Cannot change status of RFC {0}. Reason: {1}".format(change_id, response_raw['errors']))
            return False
        response = response_raw['change']
        change_id = response['id']
        change_status = look4name(response['status'])
        change_feature_number = response['custom_fields']['feature_id']
        change = {
            "id": change_id,
            "status": change_status,
            "feature_number": change_feature_number
        }
        return change
    else:
        print("*** Failed to update change, errors are displayed below ***")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))
        print(r.headers)
        print(r.content)
        print("*** END ***")
        return False

def update_change_status_apiv1(change_id, release_info):
    """Update FreshService change status to completed  
        ## Parameters:   
        `change_id` : int  
        `release_info` : string    
        """
    data = { 
        "itil_change": { 
            "status": 6, 
            "custom_field_attributes": { 
                "release_222059": release_info 
            }
        }
    }
    headers = {
            'content-type': 'application/json'
        }
    r = requests.put(root_url_v1 + "changes/{0}.json".format(change_id), auth=(api_key, password), data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        response_raw = json.loads(r.content)
        if 'errors' in response_raw:
            print("Cannot change status of RFC {0}. Reason: {1}".format(change_id, response_raw['errors']))
            return False
        response = response_raw['item']['itil_change']
        change_id = response['display_id']
        change_status = look4name(response['status'])
        change_feature_number = response['custom_field_values']['feature_id_222059']
        change = {
            "id": change_id,
            "status": change_status,
            "feature_number": change_feature_number
        }
        return change
    else:
        print("Failed to update change, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))
        print(r.headers)
        return False

def axosoft_workflow_id2name(workflow_id):
    """Fetch Axosoft workflow step name by its id  
        ## Parameters:   
        `workflow_id` : int    
        ## Returns:  
        `string` [Workflow step name]  
        """
    axosoft_result = axosoft_client.get('workflow_steps', resourse_id=workflow_id)
    return axosoft_result['data']['name']

def check_feature_in_axosoft(feature_numbers):
    """Fetch data from Axosoft about specific feature  
        ## Parameters:   
        `feature_numbers` : string    
        ## Returns:  
        `tuple` (
            `list` [list values are boolen, True if feature is completed else False],  
            `string` [highest release number from all features that was checked]  
        )
        """
    
    feature_list = feature_numbers.split(',')
    results = []
    release_list = []
    for feature_number in feature_list:
        if len(feature_number) > 0:
            try:
                axosoft_result = axosoft_client.get('features', resourse_id=feature_number, arguments="columns=number,workflow_step,custom_309")
                workflow_step_id = axosoft_result['data']['workflow_step']['id']
                workflow_step_name = axosoft_workflow_id2name(workflow_step_id)
                release_id = axosoft_result['data']['custom_fields']['custom_309']
                if workflow_step_name == "Completed":
                    results.append(True)
                    release_list.append(release_id)
                else:
                    results.append(False)
            except ValueError:
                results.append(False)
                release_list.append("Feature not found in Axosoft")
    if len(release_list) == 0:
        final_release_number = ''
    else:
        final_release_number = sorted(release_list)[-1]
        
            
    return results, final_release_number


if __name__ == "__main__":
    print("### Fetching data about changes ###")
    results = fetch_changes()
    print("### Checking changes START ###")
    errors = []
    for item in results:
        if item['feature_number'] is not None:
            check_results = check_feature_in_axosoft(item['feature_number'])
            axosoft_results = check_results[0]
            release_number = check_results[1]
            if False in axosoft_results:
                if "Feature not found in Axosoft" in release_number:
                    print("Feature: {0} from change {1} not found in Axosoft".format(item['feature_number'], item['id']))  
                else:
                    print("Not all features completed yet for change", item['id'])
            else:
                print("Needs to update Freshservice change with id:", item['id'])
                update_results = update_change_status(item['id'], release_number)
                # update_change_status_apiv1(item['id'], release_number)
                if update_results is False:
                    errors.append(1)
                print("done")
    print("### Checking changes END ###")
    if len(errors) > 0:
        exit(1)
