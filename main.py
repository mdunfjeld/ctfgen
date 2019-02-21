#!/usr/bin/env python

import oyaml as yaml
import sys
import os
import argparse
from collections import OrderedDict
from src.scenario import Scenario
from time import strftime
import subprocess
from src.helpers import debug_yaml  # For debugging only
from src.helpers import prettyprint # For debugging only

def load_config_file(filepath):
    try:
        with open(filepath, 'r') as file:
            f1 = yaml.load(file)
            return f1
    except FileNotFoundError:
        print("File not found")
        sys.exit(1)

def write_template_to_file(template, platform, debug=False):
    timestamp = strftime("%Y_%m_%d-%H_%M")
    if debug is True:
        filename = 'debug.yaml'
    else:
        if not os.path.exists('templates'):
            os.mkdir('templates')
        filename = os.path.join('templates', platform + '-stack-' + timestamp + '.yaml')
    with open(filename, 'w') as file:
        yaml_template = yaml.dump(template)
        file.write(str(yaml_template))
    return filename

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
    #global allocated_subnets = ['a', 'b', 'c']

    #network_template = get_empty_heat_template()
    router_list = []
    node_list = []
    scenario = Scenario(data)
    network_template = scenario.get_template()

    filename = write_template_to_file(network_template, scenario.platform, debug=args.debug)

if __name__ == '__main__':
    main()
    sys.exit(0)
    