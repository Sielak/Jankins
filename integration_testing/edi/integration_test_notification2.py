import json
import jenkins
import sys
from smtplib import SMTP
from email.mime.text import MIMEText
from jinja2 import Environment
import urllib
import base64

with open('config.json') as data_file:
    config = json.load(data_file)

# integration = 'Tungsten_portal'  # TEST
integration = sys.argv[1]  # PROD

JENKINS_LOGIN = config["Jenkins_username"]
JENKINS_PASSWD = config["Jenkins_password"]


def urlopen(url, data=None):
    request = urllib.request.Request(url, data)
    base64string = base64.encodestring(('%s:%s' % (JENKINS_LOGIN, JENKINS_PASSWD)).encode()).decode().replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)
    response = urllib.request.urlopen(request)
    return response


base_url = 'http://bma-mte-101:8080'
a = urlopen(
    '{0}/view/Flows/job/EDI_integration_tests/lastBuild/wfapi/'.format(base_url))  # Need change if job name will change in jenkins
content = a.read().decode(a.headers.get_content_charset())
d = json.loads(content)
stage_status = 'None'
stage_console_url = 'None'
stage_log = 'None'
for item in d['stages']:
    if item['name'] == integration:
        node_desc_link = item['_links']['self']['href']
        node_desc = urlopen(base_url + node_desc_link)
        node_content = node_desc.read().decode(node_desc.headers.get_content_charset())
        node_content_json = json.loads(node_content)
        for node_item in node_content_json['stageFlowNodes']:
            if 'compare_xml' in node_item['parameterDescription'] or 'portal_check' in node_item['parameterDescription']:
                stage_log_link = node_item['_links']['log']['href']
                stage_log_desc = urlopen(base_url + stage_log_link)
                stage_log_content = stage_log_desc.read().decode(stage_log_desc.headers.get_content_charset())
                stage_log_content_json = json.loads(stage_log_content)
                stage_status = stage_log_content_json['nodeStatus']
                stage_log = stage_log_content_json['text']
                stage_console_url = stage_log_content_json['consoleUrl']

if stage_status != 'SUCCESS':
    TEMPLATE = """
    <h2>Integration: {{integration}}</h2>
    <h2>Result: {{result}}</h2>
    <h2>URL: {{url}}</h2>
    <h2>Console log</h2>
    <pre>{{console}}</pre>
    """  # Our HTML Template

    # Create a text/html message from a rendered template
    msg = MIMEText(Environment().from_string(TEMPLATE).render(integration=integration, result=stage_status,
                                                              url=base_url + stage_console_url, console=stage_log),
                   "html")

    COMMASPACE = ', '

    subject = "[monitoring] {0} EDI XML generated with errors".format(integration)
    sender = "EDI.monitoring@hl-display.com"
    recipient = ["dawid.wybierek@hl-display.com"]
    # recipient = ["devs@hl-display.com", "julia.homik@hl-display.com", "GliwiceSupp@hl-display.com"]

    msg['Subject'] = subject
    msg['From'] = sender
    msg['To'] = COMMASPACE.join(recipient)

    # Send the message via our own local SMTP server.
    s = SMTP('smtp.hl-display.com')
    s.send_message(msg)
    s.quit()
    print("Email was sent to", recipient)
else:
    print('Nothing to send')
