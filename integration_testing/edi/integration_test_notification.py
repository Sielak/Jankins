import json
import jenkins
import sys
from smtplib import SMTP
from email.mime.text import MIMEText
from jinja2 import Environment


with open('config.json') as data_file:
    config = json.load(data_file)

job_name = 'EDI regression tests/{0}'.format(sys.argv[1])  # PROD
# job_name = 'EDI regression tests/{0}'.format('Fetch new xml TESCO')  # TEST


jenkins_server = config["Jenkins_server"]
jenkins_user = config["Jenkins_username"]
jenkins_password = config["Jenkins_password"]
server = jenkins.Jenkins(jenkins_server, username=jenkins_user, password=jenkins_password)
last_build_number = server.get_job_info(job_name)['lastCompletedBuild']['number']
build_info = server.get_build_info(job_name, last_build_number, 0)
console = server.get_build_console_output(job_name, last_build_number)
result = build_info['result']
result_url = build_info['url']
integration = ''
for item in build_info['actions']:
    try:
        params = item['parameters']
        for param in params:
            if param['name'] == 'integration':
                integration = param['value']
    except KeyError:
        pass

print(integration, '--->', result, '--->', result_url)
if result != 'SUCCESS':
    TEMPLATE = """
    <h2>Integration: {{integration}}</h2>
    <h2>Result: {{result}}</h2>
    <h2>URL: {{url}}</h2>
    <h2>Console log</h2>
    <pre>{{console}}</pre>
    """  # Our HTML Template

    # Create a text/html message from a rendered template
    msg = MIMEText(Environment().from_string(TEMPLATE).render(integration=integration, result=result, url=result_url, console=console), "html")

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

