#!/usr/bin/env python

import oyaml as yaml
import sys
import os
import argparse
import configparser
import subprocess
from collections import OrderedDict
from time import strftime, sleep

from src.scenario import Scenario
from src.helpers import debug_yaml  # For debugging only
from src.helpers import prettyprint # For debugging only
from src.openstack_inventory_plugin import create_inventory

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
    if not os.path.exists('templates'):
        os.mkdir('templates')
    if debug is True:
        filename = os.path.join('templates', 'debug.yaml')
    else:
        filename = os.path.join('templates', platform + '-stack-' + timestamp + '.yaml')
    with open(filename, 'w') as file:
        yaml_template = yaml.dump(template)
        file.write(str(yaml_template))
    return filename

def write2(data):
    with open(os.path.join('data', 'hosts.yaml'), 'w') as file:
        yaml_template = yaml.dump(data)
        file.write(str(yaml_template))        

def create_deploy_key():
    """This is a shortcut that should be replaced with a python version to avoid being limited to linux"""
    privkey = 'ansible_deploy_key'
    pubkey  = 'ansible_deploy_key.pub'       
    if os.path.exists(privkey) or os.path.exists(pubkey):
        os.remove(privkey)
        os.remove(pubkey)
    subprocess.run('ssh-keygen -t ed25519 -f ansible_deploy_key -q -P ""', shell=True)
    hostname = os.uname()[1]
    username = os.environ['USER']
    subprocess.run('sed -i "s/{}@{}/Ansible-Deploy-Key/g" ansible_deploy_key.pub'.format(username, hostname), shell=True)

def get_config():
    config = configparser.ConfigParser()
    config.read('ctfgen.conf')
    return config

def get_config_items(config, section, item):
    item = str(config.get(section, item)).rsplit(' ')
    return [str(x).strip(',') for x in item ]

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-f', '--file', nargs=1, help="Input yaml file")
    parser.add_argument('-t', '--test', action='store_true', help='temp argument for testing purposes')
    parser.add_argument('--debug', action='store_true', help="Changes filename if set")
    parser.add_argument('-r', '--run', action='store_true', help="Launch in openstack")
    args = parser.parse_args()
    config = get_config()

    data = OrderedDict()
    create_deploy_key()
    data = load_config_file(args.file[0])
    platform = config.get('DEFAULT', 'platform')

    global network_template
    global management_nodes 
    management_nodes = get_config_items(config, str(data['scenario']['type'].upper()), 'management_nodes')

    scenario = Scenario(data, platform)
    node_list = scenario.node_list
    network_template = scenario.get_template()
    
    filename = write_template_to_file(network_template, scenario.platform, debug=args.debug)
    if args.run:
        stackname='test123'
        command = 'openstack stack create -t {} --parameter key_name=testkey {}'.format(filename, stackname)
        subprocess.run(command, shell=True)
        spawn_wait_time = int(config.get('DEFAULT', 'spawn_wait_time'))
        sleep(spawn_wait_time)

        inventory = create_inventory(node_list, management_nodes)
        write2(inventory)

if __name__ == '__main__':
    main()
    sys.exit(0)
    