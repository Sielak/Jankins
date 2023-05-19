from xmldiff import main
# from xmldiff import formatting
import xml.etree.ElementTree as ET
import sys
import os
import requests
import json


def post2monitoring(integration_name, status):
    url = 'http://bma-iwa-101:8085/logExternalService/ext_edi_reg_{0}/{1}/test'.format(integration_name, status)
    r = requests.get(url)
    print('Posting result to:', url)
    if r.status_code == 200:
        data = json.loads(r.text)
        if data['messageNo'] != '0':
            print('ERROR', data['messageStr'])
            exit(1)
        else:
            print('Status:', data['messageStr'])
    else:
        print('returned status not OK')
        exit(1)


# integration = 'asda'  # TEST
integration = sys.argv[1]  # PROD
file1 = 'models/{0}.xml'.format(integration)
file2 = 'to_compare/{0}.xml'.format(integration)
# import xml files
with open(file1, 'r', encoding="UTF-8") as f1:
    model_file = f1.read()
with open(file2, 'r', encoding="UTF-8") as f2:
    file2check = f2.read()
print('## All rows with differences ##')
# choose diff style, default without formatter
diff2 = main.diff_texts(model_file, file2check)
diff_locations = set()  # use set to get only unique values
debug_list = []  # For debug only
for item in diff2:
    debug_list.append(item)  # For debug only
    # extract row number from diff
    check_action_end = str(item).find('(')
    check_action = str(item)[:check_action_end]
    if check_action == 'InsertNode':
        location = str(item).split('position=', 1)[1]
        diff_locations.add(location[:-1])
    else:
        start = str(item).find('[') + 1
        end = str(item).find(']', start)
        # save row numbers
        diff_locations.add(str(item)[start:end])
if len(debug_list) > 30:
    print('too much to show')
else:
    for item in debug_list:
        print(item)
print('## Rows with error ##')


def show_xml_rows(et_root, row_id):
    pattern = "./EDIMsgRow[@Rad='{0}']".format(row_id)
    try:
        row = et_root.find(pattern).attrib
    except AttributeError:
        row = {'Field': '{0} not found'.format(row_id)}
    return row


exclude = ['FullMsgID', 'DocDateShort', 'DocTime', 'DocTimeStd', 'InterchangeCtrlReff', 'jsbDataSource',
           'DummyUniqueId']
comparision_result = []
root = ET.fromstring(file2check)
for item in diff_locations:
    whole_xml_row = show_xml_rows(root, item)
    xml_field = whole_xml_row['Field']
    if xml_field in exclude:
        pass
    else:
        comparision_result.append(whole_xml_row)

if len(comparision_result) > 30:
    print('too much to show')
else:
    for item in comparision_result:
        print(item)
print('########################')
print('Deleting files from test')
os.remove(file1)
os.remove(file2)
print('Done')
print('########################')
if len(comparision_result) != 0:
    print('[RESULT] Files are different')
    print('there is {0} problems'.format(len(comparision_result)))
    post2monitoring(integration, 'NOK')
    exit(1)
else:
    print('[RESULT] Files are equal')
    post2monitoring(integration, 'OK')
