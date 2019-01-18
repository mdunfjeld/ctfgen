#!/usr/bin/env python

import sys
import os
import yaml
import argparse
from collections import OrderedDict
import yamlordereddictloader
from src.heat import Node
from src.heat import Router




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
            router_list.append(Router(data['resources'][device]))
        elif data['resources'][device]['type'] == 'node':
            node_list.append(Node(data['resources'][device]))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs=1, help="Input yaml file")
    args = parser.parse_args()
    data = OrderedDict()
    data = load_config_file(args.file[0])
    global router_list
    global node_list
    router_list = []
    node_list = []
    check_platform(data)
    router_list[0].new_subnets()
       
    
    #data = yaml.dump(data, Dumper=yamlordereddictloader.SafeDumper)
    #print(data)
if __name__ == '__main__':
    main()
    sys.exit(0)
    