#pip3 install json2xml
import os
import requests
import json
import time
import sys
from json2xml import json2xml
from datetime import datetime
import shutil

filename = 'accounts'
date = datetime.now().strftime("%Y%m%d")
timtestmap = datetime.now().strftime("%Y%m%d%H%M%S")
fileNameTmp = filename + '_' + timtestmap + '.xml'
fileName = filename + '_' + date + '.xml'
tmpFileWithPath = '//ew1-fil-101/Public/_LinuxShareFolder/CRM/SIS/tmp/' + fileNameTmp
FileWithPath = '//ew1-fil-101/Public/_LinuxShareFolder/CRM/SIS/' + fileName                                                                           

                                                                                      
x = 0
while x < 100:        
    x = x + 1
    try:
        answer = requests.post("https://login.microsoftonline.com/common/oauth2/token", data={'client_id': 'e5f7e1d5-232d-4368-994c-9c23e2457c20', 
                                                                                              'username': 'S-CRMBG@hl-display.com',
                                                                                              'password': 'Sv4rt.0nyx!0451',
                                                                                              'resource': 'https://hldisplaysandbox.crm4.dynamics.com',
                                                                                              'grant_type': 'password'})
    except:
        print('NOK while POST. Wait 2 seconds before repeat... Try: ' + str(x) +' /100')   
        time.sleep(2)
        continue
        
    if answer.status_code != 200:
        print('NOK while fetching token. HTTP STATUS <> 200. Wait 2 seconds before repear... Try: ' + str(x) +' /100')   
        time.sleep(2)
        continue
    try:
        token = json.loads(answer.content)["access_token"]
        x = 0
        break
    except:
        print('NOK Response token is not JSON. Wait 2 seconds before repeat... Try: ' + str(x) +' /100')   
        time.sleep(2)
        continue

if x > 0:
    print('Mission failed. Token couldn''t be fetched.')
    sys.exit(1)
    
    
url = 'https://hldisplay.api.crm4.dynamics.com/api/data/v9.1/accounts()?$select=name,address1_country,accountnumber,emailaddress1,_ownerid_value&$expand=new_Area($select=new_name),new_SalesMarket($select=new_name)'
headers = {"authorization": token,}
x = 0
while x < 1000:
    x = x + 1
    
    try:
        answer = requests.get(url, headers=headers)
    except:
        print('NOK while GET accounts. Wait 2 seconds before repeat... Try: ' + str(x) +' /100')   
        time.sleep(2)
        continue    
    
    if answer.status_code != 200:
        print('NOK while fetching accounts. HTTP STATUS <> 200. Wait 2 seconds before repeat... Try: ' + str(x) +' /100')    
        time.sleep(2)
        continue
    
    try:
        jsonBody = json.loads(answer.content)
    except:
        print('NOK Response account list is not JSON. Wait 2 seconds before repeat... Try: ' + str(x) +' /100')   
        time.sleep(2)
        continue
    
    if 'value' in jsonBody:
        print('GOOD JSON :)')      
    else:
        print('NOK value missing in JSON but should be. Wait 2 seconds before repeat... Try: ' + str(x) +' /100')    
        time.sleep(2)        
        continue     
    
    try:
        xml = json2xml.Json2xml(jsonBody["value"]).to_xml()
        with open(tmpFileWithPath, "a+", encoding='utf-8') as myfile:
            myfile.write(xml)
        print('ADD TO FILE')
    except:
        print('NOK while converting JSON to XML.')
        time.sleep(2)        
        continue            
        
    if '@odata.nextLink' in jsonBody:
        x = 0
        url = jsonBody['@odata.nextLink']
        print(url)
    else:    
        x = 0
        break
if x > 0:
    print('Mission failed. Accounts couldn''t be fetched.')
    sys.exit(1)

print('COPY FILE')
shutil.copy(tmpFileWithPath, FileWithPath)
os.remove(tmpFileWithPath)

sys.exit(0)
