from collections import OrderedDict
import yamlordereddictloader
import oyaml as yaml


class Router(object):
    subnets = []
    subnetA_cidr = '192.168.1.0/24'
    subnetA_gateway_ip = '192.168.1.1'
    subnetA_dhcp_pool_start = '192.168.1.100'
    subnetA_dhcp_pool_end = '192.168.1.199'
    subnetB_cidr = '10.0.1.0/24'
    subnetB_gateway_ip = '10.0.1.1'
    subnetB_dhcp_pool_start = '10.0.1.100'
    subnetB_dhcp_pool_end   = '10.0.1.199'
    net_name = 'Lab-Net'
    public_net = 'ntnu-internal'


    def __init__(self, data, router_name):
        self.data = data
        self.router_name = router_name
        self.public_net = 'ntnu-internal'
        self.net_name = 'CyberRange-Net'
        self.structure = OrderedDict({
            'heat_template_version': '2015-10-15',
            'parameters': {
                'public_net': {
                    'type': 'string',
                    'default': self.public_net
                },
                'Lab_net_name': {
                    'type': 'string',
                    'default': self.net_name
                },
                'subnetA': {
                    'type': 'string'
                },
                'subnetB': {
                    'type': 'string'
                },
                'subnetA_net_cidr': {
                    'type': 'string',
                    'default': self.subnetA_cidr
                },
                'subnetA_net_gateway': {
                    'type': 'string',
                    'default': self.subnetA_gateway_ip
                },
                'subnetA_net_pool_start': {
                    'type': 'string',
                    'default': self.subnetA_dhcp_pool_start
                },
                'subnetA_net_pool_end': {
                    'type': 'string',
                    'default': self.subnetA_dhcp_pool_end
                },
                'subnetB_net_cidr': {
                    'type': 'string',
                    'default': self.subnetB_cidr
                },
                'subnetB_net_gateway': {
                    'type': 'string',
                    'default': self.subnetB_gateway_ip
                },
                'subnetB_net_pool_start': {
                    'type': 'string',
                    'default': self.subnetB_dhcp_pool_start
                },
                'subnetB_net_pool_end': {
                    'type': 'string',
                    'default': self.subnetB_dhcp_pool_end
                },

            },
            'resources': {
                'Lab_net': {
                    'type': 'OS::Neutron::Net',
                    'properties': {
                        'name': '{ get_param: Lab_net_name }'
                    }
                },
                
            },
            'outputs': {
                'Lab_name': {
                    'value': '{ get_attr: [Lab_net, name] }'
                },
                'subnetA': {
                    'value': '{ get_attr: [subnetA, name] }'
                },
                'subnetB': {
                    'value': '{ get_attr: [subnetB, name] }'
                }
            }})
        self.subnet_count = len(self.data['properties']['networks'])
       # self.router_count = num_of_routers()
       # self.node_count = num_of_nodes()
      
        
        self.subnet_count = len(data['properties']['networks'])
    
    def create_router(self):
        rtr = OrderedDict({self.router_name: {
            'type': 'OS::Neutron::Router',
            'properties': {
                'external_gateway_info': {
                    'network': '{ get_param: public_net }'
                }
            }
        }})
        return rtr

    def create_router_interfaces(self):
   #     for i, subnet in zip(range(0, self.subnet_count), self.data['properties']['networks'].keys()):
        print(self.structure)
                          

    def create_subnets(self):
        for subnet in self.data['properties']['networks'].keys():
            subnet = {subnet: {
                'type': 'OS::Neutron::Subnet',
                'properties': {
                    'name': '{ get_param: subnetA }',
                    'network_id': '{ get_param: Lab_net }'
                }
            }}
            self.subnets.append(subnet)
        print(self.subnets)

    def num_of_routers(self):
        pass

    def foo(self):
        print(self.data)

    def change_subnet_address(self):
        pass


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