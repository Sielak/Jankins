# Script to retrive list of all jobs and windows commands from Jenkins
import jenkins
import json
import time
import argparse

# import of configuration file
with open('config.json') as data_file:
    config = json.load(data_file)

jenkins_server = config["Jenkins_server"]
jenkins_user = config["Jenkins_username"]
jenkins_password = config["Jenkins_password"]
server = jenkins.Jenkins(jenkins_server, username=jenkins_user, password=jenkins_password)

def check_node(node_name):
    for item in server.get_nodes():
        if item['name'] == node_name:
            print(item)
            return item

def activate_node(node_info):
    if node_info['offline'] is True:
        print("Node {0} is offile, activating...".format(node_info['name']))
        choosed_node_config = [node for node in config['nodes'] if node['name'] == node_info['name']]
        if len(choosed_node_config) == 0:
            print("Node not supported. Add it to config.json")
            exit(0)
        server.build_job(choosed_node_config[0])
        print("Job for activating node was runned.")
        time.sleep(120)
    else:
        print('Node already runned')


parser = argparse.ArgumentParser()
parser.add_argument('-node_name', help='Pass node name for checking')
args = parser.parse_args()
if args.node_name is None:
    print('Node name was not provided!')
    exit(0)
else:
    print("Checking for node: {0}".format(args.node_name))
    node_data = check_node(args.node_name)
    if node_data is None:
        print('Node with name {0} dont exists'.format(args.node_name))
        exit(0)
    activate_node(node_data)    
    
