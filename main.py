#!/usr/bin/env python

import sys
import os
import oyaml as yaml
import argparse
from collections import OrderedDict
import yamlordereddictloader
from src.heat import Node
from src.heat import Router
import ipaddress
import pprint
from shutil import copy
from time import strftime


def load_config_file(filepath):
    try:
        with open(filepath, 'r') as file:
            f1 = yaml.load(file, Loader=yamlordereddictloader.Loader)
            return f1
    except FileNotFoundError:
        print("File not found")
        sys.exit(1)

def check_platform(data):   
    if str(data['options']['cloud-platform'].lower()) == 'heat':
        heat_instantiate(data)
    elif data['options']['cloud-platform'].lower() == "terraform":
        raise NotImplementedError
        #sys.exit(1)
   

def heat_instantiate(data):
    for device in data['resources']:
        if data['resources'][device]['type'] == 'router':
            r = Router(data['resources'][device], device, network_template)
            router_list.append(r)
        if data['resources'][device]['type'] == 'node':
            n = Node(data['resources'][device], device, network_template)
            node_list.append(n)
                

def read_network_template():
    with open('data/empty_net_template.yaml') as file:
        f = yaml.load(file, Loader=yamlordereddictloader.Loader)
        return f

def overwrite_temp_file():
    timestamp = strftime("%Y_%m_%d-%H_%M-")
    dst = os.path.join('history', timestamp, 'heat-network.yaml')
    copy('heat-network-yaml', dst)

def print_yaml(template):
    a = yaml.dump(template, Dumper=yamlordereddictloader.SafeDumper)
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
    if os.path.exists('heat-network.yaml'):
        os.remove('heat-network.yaml')
    network_template = read_network_template()
    router_list = []
    node_list = []
    check_platform(data)
    #overwrite_temp_file()
    router_list[0].data
    #node_list[1].print_yaml()  
    pp = pprint.PrettyPrinter(indent=2)
  #  pp.pprint(network_template)


    #prettyprint(node_list[0].data)
    #print_yaml(node_list[0].data)



if __name__ == '__main__':
    main()
    sys.exit(0)
    