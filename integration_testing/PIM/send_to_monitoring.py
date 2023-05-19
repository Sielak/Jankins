import requests
import json
import xml.etree.ElementTree as ET


def post2monitoring(status):
    url = 'http://bma-iwa-101:8085/logExternalService/pim_reg_tests/{0}/nothing'.format(status)
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


# import xml files
with open('test-reports/test_results.xml', 'r') as f2:
    file2check = f2.read()
root = ET.fromstring(file2check)  # import file as XML
result_errors = root.attrib['errors']  # search for number of errors in test report
result_failures = root.attrib['failures']  # search for number of failures in test report
if int(result_errors) != 0 or int(result_failures) != 0:
    post2monitoring('NOK')
else:
    post2monitoring('OK')
