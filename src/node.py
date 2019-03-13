from collections import OrderedDict
import oyaml as yaml
from src.data import *
import sys

from src.helpers import debug_yaml  # For debugging only
from src.helpers import prettyprint # For debugging only

class Node(object):
    # Remember to test if port_list, net and subnet works properly.
    def __init__(self, data, node_name, template, ansible_group=None, port_list=None, net=None, subnet=None):
        self.data = data
        self.node_name = node_name
        self.port_list = port_list
        self.net = net
        self.ansible_group = ansible_group
        self.subnet = subnet
        self.template = template
        self.subnet_count = self.count_subnets()
        self.initialize_node()

    def initialize_node(self):
        """Heat resources are initialized from this function"""
        self.add_node(self.port_list)

        if 'networks' in self.data['properties'].keys() and self.subnet_count is not 0:
            for idx in range(0, self.subnet_count):
                router = self.data['properties']['networks'][idx]['router']
                subnet = self.data['properties']['networks'][idx]['subnet']
                self.add_node_ports(idx, router, subnet)
        else:
            self.add_node_ports('0', 'management', 'attack_defense_subnet') # TODO: fix other types as well

        if 'public_ip' in self.data['properties'].keys() and self.data['properties']['public_ip'] is True:
            self.add_floating_ip()

    def add_outputs(self):
        self.template['outputs'].update(OrderedDict({
            str(self.node_name + '_ip'): {
                'value': ""
            }
        }))

    def count_subnets(self): 
        """Get the number of subnets the node is connected to"""
        if 'properties' not in self.data.keys() or self.data['properties'] is None:
            return 0
        elif 'networks' not in self.data['properties'].keys():
            return 0
        elif self.data['properties']['networks'] == None:
            return 0
        else:
            return len(self.data['properties']['networks'])

    def get_node_ports(self, net, subnet ):
        subnet_list = []
        for router in self.data['properties']['networks'].keys():
            subnet = str(self.data['properties']['networks'][router]['subnet'])
            subnet_list.append((router, subnet))
        for port_number, subnet_name in zip(range(0, len(subnet_list)), subnet_list):
            yield (port_number, subnet_name[0], subnet_name[1])

    def set_flavor(self):
        """Set the Node's flavor"""
        if 'flavor' not in self.data['properties'].keys():
            return 'm1.small'
        elif self.data['properties']['flavor'].lower() not in flavor_list:
            print('Invalid flavor selected')
            sys.exit(1)
        else:
            return str(self.data['properties']['flavor'])
    
    def set_operating_system(self):
        """Set the Node's operating system"""
        if 'os' not in self.data['properties'].keys():
            return 'Ubuntu Server 18.04 LTS (Bionic Beaver) amd64'      # Default OS unless specified
        elif self.check_os_family() is None:
            print('Invalid operating system selected')
            sys.exit(1)
        else:
            return str(self.data['properties']['os'])

    def check_os_family(self):
        """Check whether the specified OS is linux or windows based"""
        os = str(self.data['properties']['os']).lower()
        for image in windows_image_list:
            if os in str(image).lower():
                return 'windows'
        for i in linux_image_list:
            if os in str(i).lower():
                return 'linux'
        return None

    def add_node_ports(self, idx, router, subnet):
        """Create and add OS::Neutron::Port resource(s) to the heat template"""
        if router == 'management' and subnet == 'attack_defense_subnet':
            subnet_id  = { 'get_attr': ['management', subnet ]}
            network_id = { 'get_attr': ['management', 'attack_defense_net']} # Should change naming of predefined static network
        else:
            subnet_id  = { 'get_resource': subnet }
            network_id = { 'get_resource': str(router + 'net')}
        port_name = str(self.node_name + '_port' + str(idx))
        port = OrderedDict({
        port_name: {
            'type': 'OS::Neutron::Port',
            'properties': {
                'network': network_id,
                'security_groups': [{ 'get_resource': self.add_security_group(idx, subnet)}],
                'fixed_ips': [{
                    'subnet_id': subnet_id
                }]
            }}
        })
        self.template['resources'].update(port)

    def add_node(self, ports):
        """Create the OS::Nova::Server resource and the relevant parameters"""
        port_list = []
        if ports is None:
            for portnumber in range(0, self.subnet_count):
                port_list.append(OrderedDict({
                    'port': { 'get_resource': self.node_name + '_port' + str(portnumber) }
                }))
        else:
            for port in ports:
                port_list.append(OrderedDict({
                    'port': { 'get_resource': port }
                }))
        node = OrderedDict({
            self.node_name: {
                'type': 'OS::Nova::Server',
               # 'depends on': 'management',
                'properties': {
                    'config_drive': 'true',
                    'personality': {
                        'pubkey': { 'get_file': '../ansible_deploy_key.pub'},
                    },
                    'metadata': { 'group': self.ansible_group },
                    'name': { 'get_param': self.node_name + '_server_name' },
                    'image': { 'get_param': self.node_name + '_image' },
                    'flavor': { 'get_param': self.node_name + '_flavor' },
                    'key_name': { 'get_param': 'key_name' },                # This should be made dynamic at some point
                    'networks': port_list,
                    'user_data_format': 'RAW',
                    'user_data': 
                        self.add_software_config() # Fix this function
                }
            }
        })
        self.template['resources'].update(node)

        # Heat parameters related to Node
        self.template['parameters'].update(OrderedDict({
            str(self.node_name + '_server_name'): {
                'type': 'string',
                'default': str(self.node_name)
            }
        }))
        self.template['parameters'].update(OrderedDict({
            str(self.node_name + '_image'): {
                'type': 'string',
                'default': str(self.set_operating_system())
            }
        }))
        self.template['parameters'].update(OrderedDict({
            str(self.node_name + '_flavor'): {
                'type': 'string',
                'default': str(self.set_flavor())
            }
        }))
        self.template['parameters'].update(OrderedDict({
            'key_name': {
                'type': 'string'
            }
        }))

    def add_floating_ip(self):
        """Associates a node with the node in the template"""
        self.template['resources'].update(OrderedDict({
            self.node_name + '_floating_ip': {
                'type': 'OS::Neutron::FloatingIP',
                'properties': {
                    'floating_network_id': { 'get_param': 'public_net' },
                    'port_id': { 'get_resource': self.node_name + '_port0' } 
                }
            }
        }))
                
    def create_portsecurity_rule(self, port, protocol):
        """Creates a security rule"""
        return OrderedDict({
            'remote_ip_prefix': '0.0.0.0/0',
            'protocol': protocol,
            'port_range_min': port,
            'port_range_max': port
        })

    def add_security_group(self, idx, subnet):
        """Adds a security group resource to the template"""
        # ICMP is always allowed.
        rule_list = [ OrderedDict({'remote_ip_prefix': '0.0.0.0/0', 'protocol': 'icmp'}) ]

        subnet = self.data['properties']['networks'][idx]['subnet']
        resource_name = str(self.node_name + '_security_group_' + subnet)

        # Port security is not specified
        if 'port_security' not in self.data['properties']['networks'][idx].keys():
            rule_list.append(self.create_portsecurity_rule(22, 'tcp'))

        # Port security is specified
        else:
            # Port security and TCP is specified
            if 'tcp' in self.data['properties']['networks'][idx]['port_security'].keys():
                # Add SSH if it's not specified
                if 22 not in self.data['properties']['networks'][idx]['port_security']['tcp']:
                    rule_list.append(self.create_portsecurity_rule(22, 'tcp'))

                for tcp_port in self.data['properties']['networks'][idx]['port_security']['tcp']:
                    rule_list.append(self.create_portsecurity_rule(tcp_port, 'tcp'))

            # Add SSH if Port security is specified but TCP is not. 
            else:
                rule_list.append(self.create_portsecurity_rule(22, 'tcp'))

            if 'udp' in self.data['properties']['networks'][idx]['port_security'].keys(): 
                for udp_port in self.data['properties']['networks'][idx]['port_security']['udp']:
                    rule_list.append(self.create_portsecurity_rule(udp_port, 'udp'))

        # Security group Heat resource
        secgrp = OrderedDict({
            resource_name: {
            'type': 'OS::Neutron::SecurityGroup',
            'properties': {
                'rules': rule_list
            }
        }})
        self.template['resources'].update(secgrp)
        return resource_name

    def add_software_config(self): # It should be possible to select which files are used. Need to fix this.
        """This one probably needs more work"""
        config = OrderedDict({
                'str_replace': {
                    'template': { 'get_file': '../lib/scripts/ubuntu_boot.sh' },
                    'params': {
                        '__manager_ip__': { 'get_attr': ['management', 'manager_ip']}
                    }
                }
        })
        return config

