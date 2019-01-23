from collections import OrderedDict, defaultdict
import yamlordereddictloader
import oyaml as yaml
from src.defaults import *
import pprint
import re

class Router(object):
    net_name = 'Lab-Net'
    public_net = 'ntnu-internal'

    def __init__(self, data, router_name, template):
        self.data = data
        self.router_name = router_name
        self.template = template
        self.public_net = 'ntnu-internal'
        self.net_name = 'CyberRange-Net'
        self.subnet_count = len(self.data['properties']['networks'])
        self.update_heat_template()

    def print_yaml(self):
        a = yaml.dump(self.template, Dumper=yamlordereddictloader.SafeDumper)
        print(a)

    def update_heat_template(self):
        self.add_router()
        self.add_router_interfaces()
        self.add_subnets()
        self.write_template()

        pp = pprint.PrettyPrinter(indent=2)
       # pp.pprint(self.template)

    def write_template(self):
        with open('heat-network.yaml', 'a+') as file:
            a = yaml.dump(self.template, Dumper=yamlordereddictloader.SafeDumper)
            file.write(str(a).strip("'"))

    def add_subnets(self):
        for subnet in self.data['properties']['networks'].keys():
            subnet_resource = OrderedDict({
                subnet: {
                    'type': 'OS:Neutron::Subnet',
                    'properties': {
                        'name': '{ get_param: ' + subnet + ' }',
                        'network_id': '{ get_resource: Lab_net }',
                        'cidr': '{ get_param: ' + subnet + '_net_cidr }',
                        'gateway_ip': '{ get_param: ' + subnet + '_net_gateway }',
                        'allocation_pools': {
                            '[ - start': ' get_param: ' + subnet + '_net_pool_start }',
                            'end': '{ get_param: ' + subnet + '_net_pool_end] }'
                        }
                    }
                }
            })
            self.template['resources'].update(subnet_resource)
            self.template['parameters'].update(OrderedDict({
                subnet: {
                    'type': 'string'
                }}))
            self.template['parameters'].update(OrderedDict({
                subnet + '_net_cidr': {
                    'type': 'string',
                    'default': '192.168.1.0/24'
                }}))
            self.template['parameters'].update(OrderedDict({
                subnet + '_net_gateway': {
                    'type': 'string',
                    'default': '192.168.1.1'
                }}))
            self.template['parameters'].update(OrderedDict({
                subnet + '_net_pool_start': {
                    'type': 'string',
                    'default': '192.168.1.100'
                }}))
            self.template['parameters'].update(OrderedDict({
                subnet + '_net_pool_end': {
                    'type': 'string',
                    'default': '192.168.1.200'
                }}))
            

    def add_router(self):
        router = OrderedDict({self.router_name: {
            'type': 'OS::Neutron::Router',
            'properties': {
                'external_gateway_info': {
                    'network': '{ get_param: public_net }'
                }
            }
        }})
        self.template['resources'].update(router)

    def add_router_interfaces(self):
        for subnet_name in self.data['properties']['networks'].keys():
            interface = OrderedDict({
                str(self.router_name + '_interface_' + subnet_name): {
                    'type': 'OS::Neutron::RouterInterface',
                    'properties': {
                        'router_id': '{ get_resource: ' + self.router_name + ' }',
                        'subnet_id': '{ get_resource: ' + subnet_name + ' }'
                    }   
                }
            })
            self.template['resources'].update(interface)


        
    def foo(self):
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(self.template)
                          


class Dictlist(dict):
    def __setitem__(self, key, value):
        try:
            self[key]
        except KeyError:
            super(Dictlist, self).__setitem__(key, [])
        self[key].append(value)
 


class Node(object):
    def __init__(self, data, node_name, template):
        self.data = data
        self.node_name = node_name
        self.template = template
        self.subnet_count = len(data['properties']['networks'])
        self.platform = self.check_platform()
        self.update_heat_template()

    def update_heat_template(self):
        self.add_node()
        self.write_template()

    def write_template(self):
        with open('heat-network.yaml', 'a+') as file:
            a = yaml.dump(self.template, Dumper=yamlordereddictloader.SafeDumper)
            file.write(str(a).strip("'"))
        
    def flavor(self):
        if self.platform == 'linux':
            return 'm1.small'
        elif self.platform == 'windows':
            return 'm1.medium'
        
    def print_yaml(self, f):
        a = yaml.dump(f, Dumper=yamlordereddictloader.SafeDumper)
        print(a)

    @staticmethod
    def prettyprint(f):
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(f)

    def check_platform(self):
        platform = str(self.data['properties']['os']).lower()
        for image in windows_image_list:
            if platform in str(image).lower():
                return 'windows'
        for i in linux_image_list:
            if platform in str(i).lower():
                return 'linux'
        #raise Exception
        return 'undefined'

    def add_node_ports():
        subnet = data['properties']['networks']
        for port_number in range(0, self.subnet_count):
            port_name = str(self.node_name + '_port' + port_number)
            port_name = OrderedDict({
                'type': 'OS::Neutron::Port',
                'properties': {
                    'network_id': '{ get_param: group_net_name }',
                    'security_groups': '{ get_param: sec_group_' + self.node_name + ' }',
                    'fixed_ips': {
                        '- subnet_id': '{ get_param: '
                    }
                }
            })
            self.template['resources'].update(port_name)

    def add_node(self):
        node = OrderedDict({
            self.node_name: {
                'type': 'OS::Nova::Server',
                'properties': {
                    'name': '{ get_param: server_name',
                    'image': '{ get_param: ' + self.node_name + '_image }',
                    'flavor': '{ get_param: flavor_' + self.platform + '_server }',
                    'key_name': '{ get_param: key_name }',
                    'networks': [
                        OrderedDict({
                            'port': 'foo'
                        }),
                        OrderedDict({
                            'port': 'bar'
                        })
                    ]
                }
            }
        })
       # self.prettyprint(node)
        self.print_yaml(node)
        self.template['resources'].update(node)

"""
        OrderedDict([ 
            ( 'networks',
            [ 
                OrderedDict([('port', 'abcd')]),
                OrderedDict([('port', 'defg')])]
            )
        ])

        
"""