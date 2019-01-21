from collections import OrderedDict
import yamlordereddictloader
import oyaml as yaml
import src.defaults
import pprint

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

    def print_yaml(self):
        a = yaml.dump(self.template, Dumper=yamlordereddictloader.SafeDumper)
        print(a)

    def update_heat_template(self):
        self.add_router()
        self.add_router_interfaces()
        self.add_subnets()
        pp = pprint.PrettyPrinter(indent=2)
       # pp.pprint(self.template)

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

    def write_template(self):
        with open('heat-network', 'a') as file:
            file.write(self.template)
        
    def foo(self):
        pass
        pp = pprint.PrettyPrinter(indent=2)
        pp.pprint(self.template)
                          



 


class Node(object):
    #flavor_= 
    def __init__(self, data, node_name):
        self.data = data
        self.node_name = node_name
        self.structure = OrderedDict()
        #self.flavor = 
        #self.os = 
        #self.floating_ip = True
    def foo(self):
        print(self.data)