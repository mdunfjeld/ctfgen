#!/usr/bin/env python

# Licensed to the Apache Software Foundation (ASF) under one
# or more contributor license agreements.  See the NOTICE file
# distributed with this work for additional information
# regarding copyright ownership.  The ASF licenses this file
# to you under the Apache License, Version 2.0 (the
# "License"); you may not use this file except in compliance
# with the License.  You may obtain a copy of the License at

# http://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing,
# software distributed under the License is distributed on an
# "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
# KIND, either express or implied.  See the License for the
# specific language governing permissions and limitations
# under the License.

import oyaml as yaml
import sys
import os
import argparse
import subprocess
import shutil
import random
import string
from collections import OrderedDict
from time import strftime, sleep
from src.config import get_config, get_config_items
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


def write_template_to_file(stack_id, template, platform, debug=False):
    timestamp = strftime("%Y_%m_%d")
    if not os.path.exists('history'):
        os.mkdir('history')
    if debug is True:
        filename = os.path.join('output', 'debug.yaml')
    else:
        filename = os.path.join('output', 'heat_stack_' + timestamp + '_' + stack_id + '.yaml')
    with open(filename, 'w') as file:
        yaml_template = yaml.dump(template)
        file.write(str(yaml_template))
    return filename

def write_yaml(data, filename):
    with open(os.path.join('output', filename), 'w') as file:
        yaml_template = yaml.dump(data)
        file.write(str(yaml_template))        

def create_deploy_key():
    """This is a shortcut that should be replaced with a python version to avoid being limited to linux"""
    privkey = 'output/ansible_deploy_key'
    pubkey  = 'output/ansible_deploy_key.pub'       
    if os.path.exists(privkey) or os.path.exists(pubkey):
        os.remove(privkey)
        os.remove(pubkey)
    subprocess.run('ssh-keygen -t ed25519 -f output/ansible_deploy_key -q -P ""', shell=True)
    hostname = os.uname()[1]
    username = os.environ['USER']
    subprocess.run('sed -i "s/{}@{}/AnsibleDeployKey/g" output/ansible_deploy_key.pub'.format(
        username, hostname), shell=True)

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
            file.write(str(line) + '\n')

def file_transfer(dir, ip):
    command = 'scp -r -i output/ansible_deploy_key -o "UserKnownHostsFile=/dev/null" \
        -o "StrictHostKeyChecking=no" {} ubuntu@{}:'.format(dir, ip)
    subprocess.run(command, shell=True)

def random_string(stringLength=6):
    """Generate a random string of fixed length """
    letters = string.ascii_uppercase
    return ''.join(random.choice(letters) for i in range(stringLength))

def add_to_history(stackname, content_dir):
    if not os.path.exists(os.path.join('history', stackname)):
        newdir = os.path.join('history', stackname)
    shutil.copytree(content_dir, newdir)

def create_stack_id():
    stack_id = random_string(6)
    stack_name = 'heat_stack_' + str(stack_id)
    return stack_name, stack_id

def deploy_from_history(path):
    if not os.path.exists(path):
        print('Invalid path provided...')
        sys.exit(1)
    tmpdir = os.path.join(maindir, 'output')
    if os.path.exists(tmpdir):
        shutil.rmtree(tmpdir)
    shutil.copytree(path, tmpdir)
    files = os.listdir(tmpdir)
    for file in files:
        if str(file).startswith('heat_stack'):
            heat_file = str(file)
    
    stack_id = str(heat_file).split('_')[::-1][0].split('.')[0]
    stack_name = 'heat_stack_' + stack_id
    data = load_config_file(os.path.join(tmpdir, 'metadata.yaml'))
    deploy(os.path.join(tmpdir, heat_file), stack_name, data['nodes'], data['management_nodes'])

def inventory(node_list, management_nodes):
    print('Populating inventory file...')
    inventory, manager_public_ip = create_inventory(node_list, management_nodes)
    write_yaml(inventory, 'hosts.yaml')
    return manager_public_ip

def deploy(filename, stack_name, node_list, management_nodes):
    command = 'openstack stack create -t {} --parameter key_name={} {}'.format(
        filename, 
        openstack_key, 
        stack_name
    )
    subprocess.run(command, shell=True)
    wait(spawn_wait_time)

    manager_ip = inventory(node_list, management_nodes)

    print('Transferring files to manager...')
    file_transfer('output/', manager_ip)

def create_args():
    parser = argparse.ArgumentParser()
    group1 = parser.add_mutually_exclusive_group()
    group2 = parser.add_mutually_exclusive_group()
    group1.add_argument('-i', '--inventory', action='store_true', help='Invoke inventory plugin')
    parser.add_argument('--debug', action='store_true', help="Changes filename if set")
    parser.add_argument('-t', '--transfer', action='store_true', help='Transfer files. May be used together with -i')
    group1.add_argument('-f', '--file', nargs=1, help="Input yaml file")
    parser.add_argument('-r', '--run', action='store_true', help="Launch in openstack")
    group1.add_argument('-d', '--deploy-existing', nargs=1, 
    help='Deploy stack from historic build. Provide path e.g history/heat_stack_XXXXXX')
    args = parser.parse_args()
    return args

def main():
    args = create_args()
    config = get_config()
    global management_nodes 
    global spawn_wait_time
    global openstack_key
    global maindir
    maindir = os.path.abspath(os.path.dirname(sys.argv[0]))

    if args.inventory:
        c = load_config_file('output/metadata.yaml')
        management_nodes = c['management_nodes']
        node_list = c['nodes']
        ip = inventory(node_list, management_nodes)
        if args.transfer:
            file_transfer('output/', ip)
        sys.exit(0)
 
    data = OrderedDict()
    if args.file:
        if os.path.exists('output'):
            shutil.rmtree('output')
        os.mkdir('output')
        data = load_config_file(args.file[0])
        create_deploy_key()
        management_nodes = get_config_items(config, str(data['scenario']['type'].upper()), 'management_nodes')
        stack_name, stack_id = create_stack_id()
        metadata = OrderedDict({
            'stack_name': stack_name,
            'type': str(data['scenario']['type']),
            'management_nodes': management_nodes,
            'nodes': [],
        })    
    
    platform = config.get('DEFAULT', 'platform')
    openstack_key = config.get('DEFAULT', 'openstack_key')
    spawn_wait_time = int(config.get('DEFAULT', 'spawn_wait_time'))

    if args.deploy_existing:
        deploy_from_history(args.deploy_existing[0])
        sys.exit(0)

    scenario = Scenario(data, platform, metadata)   
    network_template = scenario.get_template()
    filename = write_template_to_file(stack_id, network_template, scenario.platform, debug=args.debug)
    write_yaml(metadata, 'metadata.yaml')
    if args.run:
        add_to_history(stack_name, 'output/')
        deploy(filename, stack_name, metadata['nodes'], management_nodes)

if __name__ == '__main__':
    main()
    sys.exit(0)