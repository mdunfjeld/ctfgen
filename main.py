#!/usr/bin/env python

import sys
import os
import oyaml as yaml
import argparse
from collections import OrderedDict
from src.heat import Node
from src.heat import Router
import ipaddress
import pprint
import shutil
from time import strftime
import subprocess

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
    return platform
   

def heat_instantiate(data):
    for device in data['resources']:
        if data['resources'][device]['type'] == 'router':
            r = Router(data['resources'][device], device, network_template)
            router_list.append(r)
        if data['resources'][device]['type'] == 'node':
            n = Node(data['resources'][device], device, network_template)
            node_list.append(n)
                

def get_empty_heat_template():
    with open('data/empty_heat_template.yaml') as file:
        f = yaml.load(file)
        return f

def write_template_to_file(template, platform):
    timestamp = strftime("%Y_%m_%d-%H_%M")
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
    filename = write_template_to_file(network_template, platform)

    debug_yaml(network_template)

if __name__ == '__main__':
    main()
    sys.exit(0)
    