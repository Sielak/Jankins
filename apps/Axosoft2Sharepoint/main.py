from typing import Dict, List
from lib.Axo import Axosoft
from lib.api import GraphApi
import json
from datetime import datetime
import sys

# basic data
with open('config.json') as data_file:
    config = json.load(data_file)

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


def fetch_release_content_from_axosoft(release_number: str) -> List[Dict[str, str]]:
    """Fetch data from Axosoft about features assigned to a specific release
        ## Parameters:   
        `release_number` : string
        ## Returns:  
        `list of dicts`
        """
    args = "filters=custom_fields.custom_309%3Din%5B%22{0}%22%5D&columns=project,custom_400,custom_408,custom_198,id,name,custom_309".format(release_number)
    results = []
    axosoft_result = axosoft_client.get('features', arguments=args)
    for item in axosoft_result['data']:
        an_item = {
            "Project": item['project']['name'],
            "ProductType": item['custom_fields']['custom_400'],
            "Product": item['custom_fields']['custom_408'],
            "CbmStream": item['custom_fields']['custom_198'],
            "ItemID": str(item['id']),
            "Name": item['name'],
            "Release": item['custom_fields']['custom_309']
        }
        results.append(an_item)    
    args = "filters=custom_fields.custom_310%3Din%5B%22{0}%22%5D&columns=project,custom_401,custom_409,custom_215,id,name,custom_310".format(release_number)
    axosoft_result = axosoft_client.get('defects', arguments=args)
    for item in axosoft_result['data']:
        an_item = {
            "Project": item['project']['name'],
            "ProductType": item['custom_fields']['custom_401'],
            "Product": item['custom_fields']['custom_409'],
            "CbmStream": item['custom_fields']['custom_215'],
            "ItemID": str(item['id']),
            "Name": item['name'],
            "Release": item['custom_fields']['custom_310']
        }
        results.append(an_item)    
    return results


release = datetime.now().strftime("R%y.%m")
release_erp2 = datetime.now().strftime("R%y.%m_ERP2")
try:
    release = str(sys.argv[1])
    release_erp2 = release + "_ERP2"
except IndexError:
    pass

res = fetch_release_content_from_axosoft(release)
print("Fetching data for release", release)
for item in res:
    result = GraphApi().ms_post_data_to_list(item)
    print(item['ItemID'], result)

print("Normal release counter:", len(res))


res2 = fetch_release_content_from_axosoft(release_erp2)
print("Fetching data for release", release_erp2)
for item in res2:
    result = GraphApi().ms_post_data_to_list(item)
    print(item['ItemID'], result)

print("ERP2 release counter:", len(res2))
