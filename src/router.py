from collections import OrderedDict, defaultdict
import oyaml as yaml
from src.defaults import *
import pprint
import ipaddress

class Router(object):
    net_name = 'Lab-Net'
    public_net = 'ntnu-internal'

    def __init__(self, data, router_name, template, subnet_list):
        self.data = data
        self.router_name = router_name
        self.template = template
        self.subnet_list = subnet_list
        self.subnet_count = len(self.data['properties']['networks'])
        self.initialize_object()

    def debug_yaml(self):
        a = yaml.dump(self.template)
        print(a)

    def initialize_object(self):
        self.add_router()
        self.add_router_interfaces()
        self.add_subnets()

    def get_subnet_list(self):
        return self.subnet_list

        """
    # Need to figure out IP allocation. Dont use this


    def allocate_ip_networks(self):
        number_allocated = len(self.subnet_list)
        address_range = '192.168.{}.0/24'.format(number_allocated)
        self.subnet_list.append(address_range)
        return address_range



    def setup_ip_settings(self, subnet_data):
        if ('cidr' and 'gatewayIP') not in subnet.keys():
            cidr, gw, dhcp_start, dhcp_end = self.allocate_IP_settings()

        elif 'cidr' in subnet.keys() and 'gatewayIP' not in subnet.keys():
            cidr = subnet['cidr']
            tmp1 = str(cidr).split('/')[0]
            tmp2 = tmp1.split('.')
            gw   = str(tmp2[0] + '.' + tmp2[1] + '.' + tmp[2] + '.1')

        elif 'gatewayIP' in subnet.keys() and 'cidr' not in subnet.keys():
            pass
        else:
            pass

    def allocate_IP_settings(self):
        pass
    """  

    def add_subnets(self):
        for subnet in self.data['properties']['networks'].keys():
            subnet_resource = OrderedDict({
                subnet: {
                    'type': 'OS::Neutron::Subnet',
                    'properties': {
                        'name': subnet,
                        'network_id': { 
                            'get_resource': 'neutron-net', 
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
                    'default': '192.168.100.0/24'    # Fix this
                }}))
            self.template['parameters'].update(OrderedDict({
                subnet + '_net_gateway': {
                    'type': 'string',
                    'default': '192.168.100.1'
                }}))
            self.template['parameters'].update(OrderedDict({
                subnet + '_net_pool_start': {
                    'type': 'string',
                    'default': '192.168.100.50'
                }}))
            self.template['parameters'].update(OrderedDict({
                subnet + '_net_pool_end': {
                    'type': 'string',
                    'default': '192.168.100.200'
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