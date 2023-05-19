from os import error
import subprocess
import json


def checker(server, login, password, service_name, multi=False):
    # basic data 
    command = ["PsService.exe", server, "-u", login, "-p", password, "query", service_name]
    # print(command)
    # run command in CMD
    p = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    # parsing cmd output
    out, err = p.communicate()
    line_list = str(out).replace('\\t', '').split("\\r\\n")
    services_names = []
    services_states = []
    errors = []
    for item in line_list:
        if "SERVICE_NAME" in item:
            services_names.append(item)
        elif "STATE" in item:
            services_states.append(item)
        elif "Unable to connect" in item:
            errors.append(item)
    # Printing
    if len(errors) != 0:
        print(errors)
        return 
    if multi is True:
        for name, state in zip(services_names, services_states):
            print(name, state)
    else:
        print(services_names[0], services_states[0])
    

with open('config.json') as data_file:
    services = json.load(data_file)

for item in services['services2check']:
    checker(item['server'], item['login'], item['password'], item['service_name'], multi=item['list'])

# PsService.exe \\10.192.194.24 -u administrator -p "butte-RQRT3N" query "Gung.io - SB2 - 1600 - FR"