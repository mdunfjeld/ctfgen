import oyaml as yaml
import sys
import os
from collections import OrderedDict
from src.node import Node
from src.router import Router

class Scenario(object):

    def __init__(self, data):
        self.data = data
        self.template = self.get_scenario_template()
        self.platform = self.check_platform(self.data)
        self.initialize_scenario()

    def initialize_scenario(self):
        self.heat_instantiate(self.data)

    def get_template(self):
        return self.template

    def check_platform(self, data):   
        """Check which backend platform is to be used. Added for future needs"""
        if str(data['options']['cloud-platform'].lower()) == 'heat':
            platform = 'heat'
        elif data['options']['cloud-platform'].lower() == "terraform":
            platform = 'terraform'
            raise NotImplementedError
        elif data['options']['cloud-platform'].lower() == "azure":
            platform = 'azure'
            raise NotImplementedError
        return platform
    
    def scenario_type_is_valid(self):
        """ Make sure scenario type is valid"""
        return True if self.data['scenario']['type'].lower() in \
        ['ad', 'generic', 'redteam-vs-blueteam', 'jeopardy', 'wargame'] \
        else False

    def get_scenario_template(self):
        """Opens the appropriate heat template based on scenario type"""
        if self.scenario_type_is_valid():
            type = str(self.data['scenario']['type']).lower()
            path = os.path.join('data', type + '-template.yaml')
        else:
            print('Invalid scenario type')
            sys.exit(1)
        with open(path) as file:
            f = yaml.load(file)
            return f
    
    def heat_instantiate(self, data):
        """Create the heat infrastructure"""
        global allocated_subnets
        allocated_subnets = []
        for device_name in data['resources']:
            if data['resources'][device_name]['type'] == 'router':
                r = Router(
                    data['resources'][device_name],
                    device_name,
                    self.template,
                    allocated_subnets
                )
                allocated_subnets = r.get_subnet_list()
            if data['resources'][device_name]['type'] == 'node':
                n = Node(
                    data['resources'][device_name], 
                    device_name, 
                    self.template
                )

    