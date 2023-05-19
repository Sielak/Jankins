from xmldiff import main
from xmldiff import formatting
import os
import sys
import requests
import json
import re


def post2monitoring(integration_name, status):
    url = 'http://bma-iwa-101:8085/logExternalService/ext_edi_reg_{0}/{1}/test'.format(
        integration_name, status)
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


# integration = 'tesco'  # TEST
# invoiceNO = '2168798'  # TEST
integration = sys.argv[1]  # PROD
invoiceNO = sys.argv[2]  # PROD
file1 = 'models/{0}.xml'.format(integration)
file2 = 'to_compare/{0}.xml'.format(integration)
# import xml files
with open(file1, 'r', encoding="UTF-8") as f1:
    model_file = f1.read()
with open(file2, 'r', encoding="UTF-8") as f2:
    file2check = f2.read()
formatter = formatting.DiffFormatter()
diff2 = main.diff_texts(model_file, file2check, diff_options={
                        'fast_match': True}, formatter=formatter)
diff_locations = []
rows = diff2.split('\n')
exclude = ['FullMsgID', 'DocDateShort', 'DocTime', 'DocTimeStd', 'InterchangeCtrlReff', 'jsbDataSource',
           'DummyUniqueId', 'EDIfileNo', 'DueDate']
comparision_result = []
if len(diff2) != 0:
    for row in rows:
        item = row.split(',')
        action = item[0][1:]
        where = item[1][1:]
        field = item[2][1:]
        value_temp = re.findall(r'"(.*?)"', item[3])
        if len(value_temp) == 0:
            value = 'None'
        else:
            value = value_temp[0]
        if field not in exclude:
            if field == 'InvoiceNo':
                if value[:-1] == invoiceNO:
                    print('Invoice number match')
                else:
                    print('Invoice number do not match')
            else:
                comparision_result.append(row)
                print(row)
else:
    print('ERROR --> files have this same date. Problem with fetching xml')
    comparision_result.append('ERROR')
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
