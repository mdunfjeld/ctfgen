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

from collections import OrderedDict
import oyaml as yaml
from src.data import *
from src.helpers import debug_yaml  # For debugging only
from src.helpers import prettyprint # For debugging only
import ipaddress
import sys

class Router(object):
    def __init__(self, data, template, team_name, device_name, subnet_list):
        self.router_data = data
        self.router_name = '{}_{}'.format(team_name, device_name)
        self.team_name = team_name
        self.device_name = device_name
        self.router_data = data[self.device_name]
        self.template = template
        self.subnet_list = subnet_list
        self.subnet_count = self.count_subnets()

        self.netname = self.add_net()
        self.add_router()
        self.add_router_interfaces()
        self.add_subnets(self.router_name, self.netname)

    def count_subnets(self): 
        if not 'networks' in self.router_data['properties'].keys():
            return 0
        elif self.router_data['properties']['networks'] == None:
            return 0
        else:
            return len(self.router_data['properties']['networks'])

    def add_net(self):
        netname = str(self.router_name + '-net')
        self.template['resources'].update(OrderedDict({
            str(self.router_name + '-net'): {
                'type': 'OS::Neutron::Net',
                'properties': {
                    'name': netname
                }
            }
        }))
        return netname

    def get_allocated_subnets(self):
        return self.subnet_list

    def allocate_subnet(self):
        """Allocate an IP address range in CIDR format to a subnet"""
        if len(self.subnet_list) == 0:
            subnet = '192.168.1.0/24'
            self.subnet_list.append(subnet)
            return subnet
        else:
            subnet = self.subnet_list[::-1][0]
            ip = ipaddress.IPv4Network(subnet)[0]
            s = ipaddress.IPv4Address(ip) + 256
            return '{}{}'.format(s, '/24')

    def set_cidr(self, subnet):
        if self.router_data['properties']['networks'][subnet] is not None and \
            'cidr' in self.router_data['properties']['networks'][subnet].keys():
            try:
                cidr = str(self.router_data['properties']['networks'][subnet]['cidr'])
                cidr = ipaddress.IPv4Network(cidr)
                return str(cidr)
            except ValueError:
                print('Invalid CIDR range selected for subnet: ' + subnet)
                sys.exit(1)
        elif self.router_data['properties']['networks'][subnet] is None:
            return str(self.allocate_subnet())
    
    def set_gatewayIP(self, subnet, cidr):
        if self.router_data['properties']['networks'][subnet] is not None and \
        'gatewayIP' in self.router_data['properties']['networks'][subnet].keys():
            ip = str(self.router_data['properties']['networks'][subnet]['gatewayIP'])
            if ipaddress.IPv4Address(ip) in ipaddress.IPv4Network(cidr):
                return ip
            else:
                print('The selected GatewayIP is not invalid')
                sys.exit(1)
        elif self.router_data['properties']['networks'][subnet] is None:
            ip = ipaddress.IPv4Network(cidr)[1]
            return str(ip)

    def set_dhcp_pools(self, cidr):
        """Sets the DHCP pool boundary"""
        start = str(ipaddress.IPv4Network(cidr)[50])
        end   = str(ipaddress.IPv4Network(cidr)[200])
        return start, end

    def add_subnets(self, router_name, netname):
        """Add subnet heat resources and parameters to the template"""
        for subnet in self.router_data['properties']['networks'].keys():
            resource = str(router_name + '_' + subnet)
            subnet_resource = OrderedDict({   
                resource: {
                    'type': 'OS::Neutron::Subnet',
                    'properties': {
                        'name': resource,
                        'network_id': { 
                            'get_resource': netname, 
                        },
                        'cidr': { 
                            'get_param': resource + '_net_cidr'
                        },
                        'gateway_ip': { 
                            'get_param': resource + '_net_gateway'
                        },
                        'allocation_pools': [{
                            'start': { 'get_param': resource + '_net_pool_start' },
                            'end': { 'get_param': resource + '_net_pool_end' }
                        }],
                    }
                }
            })
            self.template['resources'].update(subnet_resource)
            cidr = self.set_cidr(subnet)
            gw = self.set_gatewayIP(subnet, cidr)
            self.template['parameters'].update(OrderedDict({
                resource + '_net_cidr': {
                    'type': 'string',
                    'default': cidr
                }}))
            self.template['parameters'].update(OrderedDict({
                resource + '_net_gateway': {
                    'type': 'string',
                    'default': gw
                }}))
            self.template['parameters'].update(OrderedDict({
                resource + '_net_pool_start': {
                    'type': 'string',
                    'default': self.set_dhcp_pools(cidr)[0]
                }}))
            self.template['parameters'].update(OrderedDict({
                resource + '_net_pool_end': {
                    'type': 'string',
                    'default': self.set_dhcp_pools(cidr)[1]
                }}))

    def add_router(self):
        """Add a router heat template resource to the template"""
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
        """Adds the router's interfaces to the heat template"""
        for subnet_name in self.router_data['properties']['networks'].keys():
            #print(subnet_name)
            interface = OrderedDict({
                str(self.router_name + '_interface_' + subnet_name): {
                    'type': 'OS::Neutron::RouterInterface',
                    'properties': {
                        'router_id': { 'get_resource': self.router_name },
                        'subnet_id': { 'get_resource': str(self.router_name + '_' + subnet_name)  }
                    }   
                }
            })
            self.template['resources'].update(interface)