import json
import requests
import csv


# basic data
with open('config.json') as data_file:
    config = json.load(data_file)
api_key = config['Freshservice_api_key']
root_url = config['Freshservice_api_url']
root_url_v1 = config['Freshservice_api_url_v1']
password = config['Freshservice_api_password']
# sheet_names = ['Production', 'Supply Chain', 'Sales and Quotation', 'Marketing', 'Finance', 'HR', 'IT']
sheet_names = ['Production', 'Supply Chain', 'Sales and Quotation', 'Finance', 'IT']



def create_change_in_FreshServicev1(subject, description):
    """Create new FreshService change.
        ## Parameters:   
        `subject` : string    
        """
    change_data = {
        "itil_change": {
            "subject": subject,
            "description": description,
            "email": "cape.polar@hl-display.com",
            "priority": 1, 
            "status": 1, 
            "change_type": 2,
            "risk": 1, 
            "impact": 1
        }
    }
    headers = {
            'content-type': 'application/json'
        }
    r = requests.post(root_url_v1 + "changes.json", auth=(api_key, password), data=json.dumps(change_data), headers=headers)
    if r.status_code == 200:
        response_raw = json.loads(r.content)
        # print(response_raw)
        return response_raw['item']['itil_change']['display_id']
    else:
        print("Failed to update change, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))
        print(r.headers)
        return 0

def update_change_data_apiv1(change_id, data):
    """Update FreshService change status to completed  
        ## Parameters:   
        `change_id` : int    
        """
    headers = {
            'content-type': 'application/json'
        }
    r = requests.put(root_url_v1 + "changes/{0}.json".format(change_id), auth=(api_key, password), data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        response_raw = json.loads(r.content)
        # print(response_raw)
        return response_raw['status']
    else:
        print("Failed to update change, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))
        print(r.headers)

def update_change_status_apiv1(change_id):
    """Update FreshService change status to Pending Release  
        ## Parameters:   
        `change_id` : int    
        """
    data = {
        "itil_change": { 
            "status": 4
        }
    }
    headers = {
            'content-type': 'application/json'
        }
    r = requests.put(root_url_v1 + "changes/{0}.json".format(change_id), auth=(api_key, password), data=json.dumps(data), headers=headers)
    if r.status_code == 200:
        response_raw = json.loads(r.content)
        # print(response_raw)
        return response_raw['status']
    else:
        print("Failed to update change, errors are displayed below,")
        print(r)
        print("x-request-id : " + r.headers['x-request-id'])
        print("Status Code : " + str(r.status_code))
        print(r.headers)

def convert_priority(prio_in_string):
    try:
        prio_int = int(float(prio_in_string))
    except ValueError:
        prio_int = 1
    if prio_int == 5:
        prio_final = 3  # High in FS
    elif prio_int == 4:
        prio_final = 2  # Medium in FS
    else:
        prio_final = 1  # Low in FS

    return prio_final

def convert_status(status):
    mapping = {
        "OPEN": "Open",
        "INVESTIGATION": "Investigation",
        "SPECIFIED": "Specified",
        "IN PROGRESS": "In Progress",
        "IMPLEMENTED": "Implemented",
        "DUPLICATED": "Duplicated",
        "ON HOLD": "On Hold",
        "REJECTED": "Rejected"
    }

    try:
        bc_status = mapping[status]
    except KeyError:
        bc_status = ''

    return bc_status


# filename = f"results/test.csv"
for item in sheet_names:
    filename = f"results/{item}.csv"  # PROD
    # filename = f"results/test_files/{item}.csv"  # TEST

    with open(filename, encoding='utf-8') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter=',', )
        for row in csv_reader:
            status = row[0]
            if status != 'Status':
                Date = row[1]
                Requested_by = row[2]
                Approved_by = row[3]
                HL_unit = row[4]
                Product = row[5]
                prio = convert_priority(row[6])
                est_dev_hrs = row[7]
                try:
                    est_Cost = float(row[8]) * 10.26  # convert EUR to SEK
                except ValueError:
                    est_Cost = 0
                decision = row[9]
                decision_date = row[10]
                est_deliv_date = row[11]
                feature_ID = row[12]
                subject = row[13][:50]
                description = f"Created Date = {Date} \n Description: \n {row[13]} \n Justification: \n {row[14]} \n RFC Link: \n {row[15]}"
                change_id = create_change_in_FreshServicev1(subject, description)
                # data for modify change
                data = { 
                    "itil_change": { 
                        "status": 2, 
                        "priority": prio,
                        "custom_field_attributes": { 
                            "product_222059": Product,
                            "est_dev_hrs_222059": est_dev_hrs,
                            "est_cost_sek_222059": est_Cost,
                            "est_deliv_date_222059": est_deliv_date,
                            "feature_id_222059": feature_ID,
                            "hl_unit_payer_222059": HL_unit,
                            "decision_222059": decision,
                            "decision_date_222059": decision_date,
                            "approved_by_222059": Approved_by,
                            "stream_222059": item,
                            "step_222059": convert_status(row[0])
                        }
                    }
                }
                update_change_data_apiv1(change_id, data)
                if status in ['IN PROGRESS', 'SPECIFIED']:
                    update_change_status_apiv1(change_id)
                print(f"New change with id {change_id} was created and updated")


# result_creation = create_change_in_FreshServicev1("Change from script 3")
# result_update = update_change_status_apiv1(result_creation)
# if result_update is True:
#     print(f"Chnage with id {result_creation} created and updated")


# CUSTOM FIELDS
# 'custom_field_values': {
#     'approved_by_222059': None, 
#     'hl_unit_payer_222059': None, 
#     'release_222059': None, 
#     'product_222059': None, 
#     'est_dev_hrs_222059': None, 
#     'est_cost_sek_222059': None, 
#     'decision_222059': None, 
#     'decision_date_222059': None, 
#     'est_deliv_date_222059': None, 
#     'feature_id_222059': None, 
#     'comment_222059': None, 
#     'stream_222059': None,
#     'step_222059: None
# }



# {
#     'status': True, 
#     'item': {
#         'itil_change': {
#             'id': 50000107668, 
#             'display_id': 67, 
#             'requester_id': 50000499702, 
#             'owner_id': None, 
#             'group_id': None, 
#             'priority': 1, 
#             'impact': 1, 
#             'status': 1, 
#             'risk': 1, 
#             'change_type': 2, 
#             'approval_status': 4, 
#             'deleted': False, 
#             'subject': 'Change from script 2', 
#             'created_at': '2020-12-03T15:40:12+01:00', 
#             'updated_at': '2020-12-03T15:40:12+01:00', 
#             'cc_email': {}, 
#             'planned_start_date': None, 
#             'planned_end_date': None, 
#             'import_id': None, 
#             'department_id': None, 
#             'email_config_id': None, 
#             'category': None, 
#             'sub_category': None,
#             'item_category': None, 
#             'project_id': None, 
#             'approval_type': None, 
#             'wf_event_id': None, 
#             'state_flow_id': 50000023899, 
#             'state_traversal': [1], 
#             'change_window_id': None, 
#             'status_name': 'Open', 
#             'impact_name': 'Low', 
#             'priority_name': 'Low', 
#             'requester_name': 'Cape Polar', 
#             'owner_name': None, 
#             'group_name': None, 
#             'risk_type': 'Low', 
#             'change_type_name': 'Standard', 
#             'approval_status_name': 'Not Requested', 
#             'description': 'Not given.', 
#             'assoc_release_id': None, 
#             'associated_assets': [], 
#             'attachments': [], 
#             'notes': [], 
#             'custom_field_values': {
#                 'approved_by_222059': None, 
#                 'hl_unit_payer_222059': None, 
#                 'release_222059': None, 
#                 'product_222059': None, 
#                 'est_dev_hrs_222059': None, 
#                 'est_cost_sek_222059': None, 
#                 'decision_222059': None, 
#                 'decision_date_222059': None, 
#                 'est_deliv_date_222059': None, 
#                 'feature_id_222059': None, 
#                 'comment_222059': None, 
#                 'stream_222059': None
#             }
#       }
# }, 
# 'redirect': None}
