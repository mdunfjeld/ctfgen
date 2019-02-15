#!/usr/bin/env python

import sys
import os
import oyaml as yaml
import argparse
from collections import OrderedDict
from src.node import Node
from src.router import Router
import ipaddress
import pprint
import shutil
from time import strftime
import subprocess
from heatclient.client import Client

def load_config_file(filepath):
    try:
        with open(filepath, 'r') as file:
            f1 = yaml.load(file)
            return f1
    except FileNotFoundError:
        print("File not found")
        sys.exit(1)

def check_platform(data):   
    if str(data['options']['cloud-platform'].lower()) == 'heat':
        heat_instantiate(data)
        platform = 'heat'
    elif data['options']['cloud-platform'].lower() == "terraform":
        platform = 'terraform'
        raise NotImplementedError
    elif data['options']['cloud-platform'].lower() == "azure":
        platform = 'azure'
        raise NotImplementedError
    return platform
   

def heat_instantiate(data):
    global allocated_subnets
    allocated_subnets = []
    for device_name in data['resources']:
        if data['resources'][device_name]['type'] == 'router':
            r = Router(
                data['resources'][device_name],
                device_name,
                network_template,
                allocated_subnets
            )
            allocated_subnets = r.get_subnet_list()
            router_list.append(r)               # This list might not be necessary
        if data['resources'][device_name]['type'] == 'node':
            n = Node(
                data['resources'][device_name], 
                device_name, 
                network_template
            )
            node_list.append(n)                 # This list might not be necessary
                
def get_empty_heat_template():
    with open('data/empty_heat_template.yaml') as file:
        f = yaml.load(file)
        return f

def write_template_to_file(template, platform, debug=False):
    timestamp = strftime("%Y_%m_%d-%H_%M")
    if debug is True:
        filename = 'debug.yaml'
    else:
        filename = os.path.join('history', platform + '-stack-' + timestamp + '.yaml')
    with open(filename, 'w') as file:
        yaml_template = yaml.dump(template)
        file.write(str(yaml_template))
    return filename

def debug_yaml(template):
    a = yaml.dump(template)
    print(a)

def prettyprint(template):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(template)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs=1, help="Input yaml file")
    parser.add_argument('-d', '--deploy', help="Deploy the created scenario", action='store_true')
    parser.add_argument('--debug', action='store_true', help="Changes filename if set")
    args = parser.parse_args()
    data = OrderedDict()
    data = load_config_file(args.file[0])

    global network_template
    global router_list
    global node_list

    network_template = get_empty_heat_template()
    router_list = []
    node_list = []
    platform = check_platform(data)
    if args.debug:
        filename = write_template_to_file(network_template, platform, debug=True)
    else:
        filename = write_template_to_file(network_template, platform, debug=False)

    prettyprint(network_template['resources']['kali01_security_group_ctf-lan'])
    prettyprint(network_template['resources']['kali01'])


    debug_yaml(network_template['resources']['kali01_security_group_ctf-lan'])
    debug_yaml(network_template['resources']['kali01'])
    if args.deploy:
        print("yay")
    #print(args)

if __name__ == '__main__':
    main()
    sys.exit(0)
    