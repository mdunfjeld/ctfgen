import oyaml as yaml
import sys
import os
from collections import OrderedDict, defaultdict
from src.node import Node
from src.router import Router
from src.challenge import Challenge
from src.helpers import debug_yaml  # For debugging only
from src.helpers import prettyprint # For debugging only


class Scenario(object):

    def __init__(self, data, platform, config=None):
        self.data = data
        self.template = self.get_scenario_template()
        self.type = self.data['scenario']['type']
        self.config = config 
        self.platform = platform
        self.docker_hosts = self.get_docker_hosts()
        self.ansible_requirements = self.get_requirements_template()
        self.allocated_subnets = []
        self.node_list = []
        self.router_list = []
        self.initialize_scenario(self.type, self.data)


    def initialize_scenario(self, stype, data):
        if self.scenario_resources_are_valid(data) is False:
            print('Invalid resource(s) specified for scenario type', stype)
            print('Valid resource(s) for', stype, 'are', self.get_valid_types(stype))
            sys.exit(1)

        if self.type == 'jeopardy':
            challenge_file = self.initialize_software_template('docker', self.type)
            self.jeopardy_create(data, self.ansible_requirements, challenge_file)
        elif self.type == 'wargame':
            self.wargame_create(data)
        elif self.type == 'attack-defense':
            self.attack_defense_create(data, self.ansible_requirements)
        else:
            self.redteam_blueteam_create(data)

    def get_requirements_template(self):
        filename = str(self.type + '_requirements.yaml')
        with open(os.path.join('lib', 'ansible', filename), 'r') as file:
            return yaml.load(file)

    def get_docker_hosts(self):
        if 'docker_hosts' in self.data['scenario']['properties'].keys():
            return int(self.data['scenario']['properties']['docker_hosts'])
        else:
            return 2    # Default number of docker hosts
            
    def get_template(self):
        return self.template

    def get_valid_types(self, stype):
        """Get a list of valid resource objects for the specified scenario type"""
        foo = {
            'jeopardy': ['challenge'],
            'attack-defense': ['node', 'vulnerability', 'team', 'agent', 'objective', 'service'],
            'redteam-vs-blueteam': ['node', 'router', 'service', 'team', 'agent', 'vulnerability', 'user', 'objective', 'rules'],
            'wargame': ['service', 'vulnerability', 'node']
        }
        return foo[stype]

    def scenario_resources_are_valid(self, data):
        """Verify that valid objects are specfied for the desired scenario type"""
        for resource in data['resources']:
            if data['resources'][resource]['type'] not in self.get_valid_types(self.type):
                return False
        return True

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
        """ Verify correct scenario type"""
        return True if self.data['scenario']['type'].lower() in \
        ['attack-defense', 'generic', 'redteam-vs-blueteam', 'jeopardy', 'wargame'] \
        else False

    def get_scenario_template(self):
        """Opens the appropriate heat template based on scenario type"""
        if self.scenario_type_is_valid():
            stype = str(self.data['scenario']['type']).lower()
            path = os.path.join('lib', 'templates', stype + '-template.yaml')
        else:
            print('Invalid scenario type')
            sys.exit(1)
        with open(path) as file:
            return yaml.load(file)

    def initialize_software_template(self, ansible_group, stype):
        """Identical to the function in node. Refactoring is needed"""
        with open(os.path.join('lib', 'templates', str(stype) + '-software-template.yaml'), 'r') as file:
            data = yaml.load(file)
            data[0]['hosts'] = ansible_group
            return data

    def jeopardy_create(self, data, requirements, challenge_file):
        self.template['parameters']['docker_hosts']['default'] = str(self.docker_hosts)
        self.node_list = ['Docker{}'.format(x) for x in range(0, self.docker_hosts)]
    
        for challenge in data['resources'].keys():
            c = Challenge(
                challenge,
                data['resources'][challenge],
                challenge_file,
                requirements
            )
            challenge_file = c.get_file()        
            requirements = c.get_requirements()
            
        self.write_output(challenge_file, 'docker.yaml')   
        self.write_output(requirements, 'requirements.yaml')


    def wargame_create(self, data):
        pass
    
    def get_teams(self, data):
        for team in data['resources']:
            if data['resources'][team]['type'] == 'team':
                yield team, data['resources'][team]
       
    def write_output(self, template, filename):
        """There are a few write functions now. Should probably refactor"""
        with open(os.path.join('output', filename), 'w') as file:
            f = yaml.dump(template)
            file.write(f)

    def attack_defense_create(self, data, requirements):
        for device_name in data['resources']:
            if data['resources'][device_name]['type'] == 'node':
                service_file_created = False
                for team_name, team_data in self.get_teams(data): # Is team_data needed?                
                    full_node_name = '{}_{}'.format(team_name, device_name)
                    node = Node(
                        data['resources'], 
                        full_node_name, 
                        self.template,
                        device_name,
                        service_file_created,
                        requirements
                    )
        
                    self.node_list.append(full_node_name)
                    service_file_created = True
                    requirements = node.get_requirements()
                    self.write_output(requirements, 'requirements.yaml')

    def redteam_blueteam_create(self, data):
        """Create the heat infrastructure"""
        for device_name in data['resources']:
            if data['resources'][device_name]['type'] == 'router':
                router = Router(
                    data['resources'][device_name],
                    device_name,
                    self.template,
                    self.allocated_subnets
                )
                self.router_list.append(router)
                self.allocated_subnets = router.get_allocated_subnets()
        for device_name in data['resources']:
            if data['resources'][device_name]['type'] == 'node':
                node = Node(
                    data['resources'][device_name], 
                    # 
                    device_name, 
                    self.template
                )
                self.node_list.append(node)
            #elif data['resources'][device_name]['type'] == 'vulnerability':
            #    v = Vulnerability()
