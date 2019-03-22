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
from tqdm import tqdm

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

def wait(seconds=90):
    wait_time = int(seconds * 10)
    with tqdm(total=wait_time, dynamic_ncols=True, bar_format='{desc} {elapsed} {bar}') as pbar:
        pbar.set_description("Waiting {} seconds for VMs to spawn...".format(seconds))
        for i in range(wait_time):
            sleep(0.1)
            pbar.update(1)

def write(filepath, some_list):
    with open(filepath, 'w') as file:
        for line in some_list:
            file.write(line + '\n')

def main():
    parser = argparse.ArgumentParser()
    group1 = parser.add_mutually_exclusive_group()
    parser.add_argument('-f', '--file', nargs=1, help="Input yaml file")
    parser.add_argument('--debug', action='store_true', help="Changes filename if set")
    group1.add_argument('-r', '--run', action='store_true', help="Launch in openstack")
    group1.add_argument('-i', '--inventory', action='store_true', help='Create inventory file')

    parser.add_argument('-t', '--test', action='store_true')
    
    args = parser.parse_args()
    config = get_config()

    data = OrderedDict()
    create_deploy_key()
    if args.file:
        data = load_config_file(args.file[0])

    platform = config.get('DEFAULT', 'platform')

    global network_template
    global management_nodes 
    management_nodes = get_config_items(config, str(data['scenario']['type'].upper()), 'management_nodes')

    if args.inventory:
        path = os.path.join('output', 'node_list.txt')
        with open(path, 'r') as file:
            node_list = [node.strip() for node in file]
            print('Populating inventory file...' )
        inventory = create_inventory(node_list, management_nodes)
        print(inventory)
        sys.exit(0)

    scenario = Scenario(data, platform)
    node_list = scenario.node_list

    if not os.path.exists('output'):
        os.mkdir('output')
    write(os.path.join('output', 'node_list.txt'), node_list)

    network_template = scenario.get_template()
    
    filename = write_template_to_file(network_template, scenario.platform, debug=args.debug)

    if args.test:
        sys.exit(0)

    if args.run:
        stackname='test123'
        command = 'openstack stack create -t {} --parameter key_name=testkey {}'.format(filename, stackname)
        subprocess.run(command, shell=True)
        spawn_wait_time = int(config.get('DEFAULT', 'spawn_wait_time'))
        wait(spawn_wait_time)

        print('Populating inventory file...')
        inventory = create_inventory(node_list, management_nodes)
        write2(inventory)

if __name__ == '__main__':
    main()
    sys.exit(0)
    