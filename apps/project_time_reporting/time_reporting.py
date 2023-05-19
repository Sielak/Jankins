from Axo import Axosoft
import json
from datetime import datetime, timedelta
import pandas as pd
from smtplib import SMTP
from email.mime.text import MIMEText
from jinja2 import Environment


with open('config.json') as data_file:
    config = json.load(data_file)

# Connect to axosoft
axosoft_client = Axosoft(
    config['client_id'],
    config['client_secret'],
    'hl-display'
)
# Authenticate in axosoft
axosoft_client.authenticate_by_password(
    config['Axosoft_username'],
    config['Axosoft_password'],
    "read"
)

def extract_data2(raw_data):
    results_init = 0
    for item in raw_data['data']:
        results_init += item['work_done']['duration_minutes']
    results = results_init / 60
    return results

def work_logs_last_week_by_project(proj_id):
    start_date = datetime.strftime(datetime.now() - timedelta(7), '%Y-%m-%d')
    end_date = datetime.strftime(datetime.now(), '%Y-%m-%d')
    arg_hl = 'project_id={0}&assigned_to_id=5&assigned_to_type=team&include_archived=true&start_date={1}&end_date={2}'.format(
        proj_id, start_date, end_date)
    arg_bc = 'project_id={0}&assigned_to_id=3&assigned_to_type=team&include_archived=true&start_date={1}&end_date={2}'.format(
        proj_id, start_date, end_date)
    arg_euvic = 'project_id={0}&assigned_to_id=4&assigned_to_type=team&include_archived=true&start_date={1}&end_date={2}'.format(
        proj_id, start_date, end_date)
    arg_gung = 'project_id={0}&assigned_to_id=8&assigned_to_type=team&include_archived=true&start_date={1}&end_date={2}'.format(
        proj_id, start_date, end_date)
    work_logs_hl_raw = axosoft_client.get('work_logs', arguments=arg_hl)
    work_logs_bc_raw = axosoft_client.get('work_logs', arguments=arg_bc)
    work_logs_euvic_raw = axosoft_client.get('work_logs', arguments=arg_euvic)
    work_logs_gung_raw = axosoft_client.get('work_logs', arguments=arg_gung)
    work_logs_hl = extract_data2(work_logs_hl_raw)
    work_logs_bc = extract_data2(work_logs_bc_raw)
    work_logs_euvic = extract_data2(work_logs_euvic_raw)
    work_logs_gung = extract_data2(work_logs_gung_raw)
    work_logs_external = work_logs_euvic + work_logs_gung
    
    return work_logs_hl, work_logs_external, work_logs_bc

def total_used_axosoft(proj_id):
    args_hl = 'project_id={0}&include_sub_projects_items=True&include_inactive_projects=True&include_archived=True&assigned_to_id=5&assigned_to_type=team'.format(proj_id)
    args_bc = 'project_id={0}&include_sub_projects_items=True&include_inactive_projects=True&include_archived=True&assigned_to_id=3&assigned_to_type=team'.format(proj_id)
    args_euvic = 'project_id={0}&include_sub_projects_items=True&include_inactive_projects=True&include_archived=True&assigned_to_id=4&assigned_to_type=team'.format(proj_id)
    args_gung = 'project_id={0}&include_sub_projects_items=True&include_inactive_projects=True&include_archived=True&assigned_to_id=8&assigned_to_type=team'.format(proj_id)
    work_logs_hl = axosoft_client.get('work_logs', arguments=args_hl)
    work_logs_bc = axosoft_client.get('work_logs', arguments=args_bc)
    work_logs_euvic = axosoft_client.get('work_logs', arguments=args_euvic)
    work_logs_gung = axosoft_client.get('work_logs', arguments=args_gung)
    ext = (work_logs_euvic['metadata']['minutes_worked'] + work_logs_gung['metadata']['minutes_worked']) / 60
    return {'internal': work_logs_hl['metadata']['minutes_worked'] / 60, 'external': ext, 'bc': round(work_logs_bc['metadata']['minutes_worked'] / 60, 2)}

def remaining_axosoft(proj_id):
    args = 'project_id={0}&include_sub_projects_items=True&include_inactive_projects=True&include_archived=True'.format(proj_id)
    features_remaining = axosoft_client.get('features', arguments=args)
    return {'remaining': features_remaining['metadata']['minutes_remaining'] / 60}


all_projects = axosoft_client.get('projects')
projects2skip = ['OneJeeves Cleanup', 'Maintenance', 'Other', 'Support', 'HL IT POC']
project_info = []
for item in all_projects['data']:
    project_id = item['id']
    project_name = item['name']
    if project_name not in projects2skip:        
        total_used = total_used_axosoft(project_id)
        rem = remaining_axosoft(project_id)
        last_week = work_logs_last_week_by_project(project_id)
        result = {'project': project_name,
                'last_week_internal': last_week[0],
                'last_week_external': last_week[1],
                'last_week_bc': last_week[2],
                'duration_total_internal': total_used['internal'], 
                'duration_total_bc': total_used['bc'],
                'duration_total_external': total_used['external'], 
                'remaining': rem['remaining'],
                'total_forecast': total_used['internal'] + total_used['external'] + total_used['bc'] + rem['remaining']}
        project_info.append(result)
    # exception for Maintanance
    if project_name == 'Maintenance':
        rem = remaining_axosoft(project_id)
        last_week = work_logs_last_week_by_project(project_id)
        result = {'project': project_name,
                'last_week_internal': last_week[0],
                'last_week_external': last_week[1],
                'last_week_bc': last_week[2],
                'duration_total_internal': 'NA',
                'duration_total_bc': 'NA', 
                'duration_total_external': 'NA', 
                'remaining': rem['remaining'],
                'total_forecast': rem['remaining']}
        project_info.append(result)
    else:
        pass

# Create a text/html message from a rendered template
with open('C:/jenkins/apps/project_time_reporting/template.html') as file:
    template = file.read()  # Our HTML Template
msg = MIMEText(
    Environment().from_string(template).render(
        results=project_info
    ), "html"
)

recipient = config['emails']  # PROD
# recipient = config['emails_test']  # TEST

COMMASPACE = ', '

subject = "[Reports] Weekly project time report"
sender = "auto.reports@hl-display.com"

msg['Subject'] = subject
msg['From'] = sender
msg['To'] = COMMASPACE.join(recipient)

# Send the message via our own local SMTP server.
s = SMTP('smtp.hl-display.com')
s.send_message(msg)
s.quit()
print("Email was sent to", recipient)
