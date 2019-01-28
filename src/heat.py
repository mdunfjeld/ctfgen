from collections import OrderedDict, defaultdict
import oyaml as yaml
from src.defaults import *
import pprint

class Router(object):
    net_name = 'Lab-Net'
    public_net = 'ntnu-internal'

    def __init__(self, data, router_name, template):
        self.data = data
        self.router_name = router_name
        self.template = template
        self.public_net = 'ntnu-internal'
        self.subnet_count = len(self.data['properties']['networks'])
        self.initialize_object()

    def debug_yaml(self):
        a = yaml.dump(self.template)
        print(a)

    def initialize_object(self):
        self.add_router()
        self.add_router_interfaces()
        self.add_subnets()

    def add_subnets(self):
        for subnet in self.data['properties']['networks'].keys():
            subnet_resource = OrderedDict({
                subnet: {
                    'type': 'OS::Neutron::Subnet',
                    'properties': {
                        'name': subnet,
                        'network_id': { 
                            'get_resource': 'Lab_net', 
                        },
                        'cidr': { 
                            'get_param': subnet + '_net_cidr'
                        },
                        'gateway_ip': { 
                            'get_param': subnet + '_net_gateway'
                        },
                        'allocation_pools': [{
                            'start': { 'get_param': subnet + '_net_pool_start' },
                            'end': { 'get_param': subnet + '_net_pool_end' }
                        }],
                    }
                }
            })
            self.template['resources'].update(subnet_resource)
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
                'name': self.router_name,
                'external_gateway_info': {
                    'network': { 'get_param': 'public_net' }
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
                        'router_id': { 'get_resource': self.router_name },
                        'subnet_id': { 'get_resource': subnet_name  }
                    }   
                }
            })
            self.template['resources'].update(interface)


class Node(object):
    def __init__(self, data, node_name, template):
        self.data = data
        self.node_name = node_name
        self.template = template
        self.subnet_count = self.count_subnets()
        self.platform = self.check_platform()
        self.initialize_object()

    def count_subnets(self):
        if not 'networks' in self.data['properties'].keys():
            return 0
        elif self.data['properties']['networks'] == None:
            return 0
        else:
            return len(self.data['properties']['networks'])

    def get_node_ports(self):
        subnet_list = []
        for router in self.data['properties']['networks'].keys():
            for k in self.data['properties']['networks'][router]['subnet'].split(','):
                subnet = str(k).strip(' ')
                subnet_list.append(subnet)
        for port_number, subnet_name in zip(range(0, len(subnet_list)), subnet_list):
            yield (port_number, subnet_name)

    def initialize_object(self):
        self.add_node()
        if 'networks' in self.data['properties'].keys() and self.data['properties']['networks'] is not None:
            self.add_node_ports()
 
    def set_flavor(self):
        if 'flavor' not in self.data['properties'].keys():
            platform = self.check_platform()
            if platform == 'linux':
                return 'm1.small'
            elif platform == 'windows':
                return 'm1.medium'
        else:
            platform = str(self.data['properties']['flavor']).lower()
            return platform
        
    def debug_yaml(self, f):
        print(yaml.dump(f))

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
        return 'undefined'

    def add_node_ports(self):
        for port_number, subnet in self.get_node_ports():
            port_name = str(self.node_name + '_port' + str(port_number))
            port = OrderedDict({
            port_name: {
                'type': 'OS::Neutron::Port',
                'properties': {
                    'network': { 'get_resource': 'Lab_net' },
                #    'security_groups': { 'get_param': 'sec_group_' + self.node_name  },
                    'fixed_ips': [{
                        'subnet_id': { 'get_resource': subnet }
                    }]
                }}
            })
            self.template['resources'].update(port)

    def add_node(self):
        port_list = []
        for portnumber in range(0, self.subnet_count):
            port_list.append(OrderedDict({
                'port': { 'get_resource': self.node_name + '_port' + str(portnumber) }
            }))
        node = OrderedDict({
            self.node_name: {
                'type': 'OS::Nova::Server',
                'properties': {
                    'name': { 'get_param': self.node_name + '_server_name' },
                    'image': { 'get_param': self.node_name + '_image' },
                    'flavor': { 'get_param': self.node_name + '_flavor' },
                    'key_name': { 'get_param': 'key_name' },
                    'networks': port_list
                }
            }
        })
        self.template['resources'].update(node)
        self.template['parameters'].update(OrderedDict({
            str(self.node_name + '_server_name'): {
                'type': 'string',
                'default': str(self.node_name)
            }
        }))
        self.template['parameters'].update(OrderedDict({
            str(self.node_name + '_image'): {
                'type': 'string',
                'default': str(self.data['properties']['os'])
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
        for router in self.data['properties']['networks'][router].keys():
            if 'public_ip' in self.data['properties']['networks'][router].keys() or self.data['properties']['networks'][router]['public_ip'] == 'yes':
                self.template['resources'].update(OrderedDict({
                    self.node_name + '_floating_ip': {
                        'type': 'OS::Neutron::FloatingIP',
                        'properties': {
                            'floating_network_id': { 'get_param': 'public_net' },
                            'port_id': { 'get_resource': self.node_name + '_port0' }  # Cba to fix this now. Make sure to set port ID at some point
                        }
                    }
                }))



    def add_node_security(self):
        pass