from collections import OrderedDict
from src.data import *
from src.helpers import debug_yaml


class Challenge(object):
    def __init__(self, name, data, challenge_template, requirements, used_ports=None):
        self.name = name
        self.data = data
        self.challenge_template = challenge_template
        self.requirements = requirements       
        self.used_ports = used_ports

        if name in challenges:
            challenge_data = challenges.get(name)
            exposed_port = challenge_data['port']

            if 'properties' not in self.data.keys() or 'port' not in self.data['properties'].keys():
                port = self.assign_port_to_container(self.used_ports)
                self.used_ports.append(port)
            else:
                port = self.data['properties']['port']
                while port in self.used_ports:
                    port += 1
                self.used_ports.append(port)


            port_mapping = str(port) + ':' + str(exposed_port)
            role = OrderedDict({
                'name': 'Installing challenge {}'.format(name), 
                'include_role': {
                    'name': 'docker-container',

                },
                'vars': {
                    'image': str(challenge_data['image']),
                    'container_name': str(challenge_data['name']),
                    'public_port': str(port_mapping)
                }
            })
            challenge_template[0]['tasks'].append(role)            

    def get_file(self):
        return self.challenge_template

    def get_requirements(self):
        return self.requirements

    def get_port_list(self):
        return self.used_ports

    def assign_port_to_container(self, ports):
        if len(ports) == 0:
            return 1337
        else:
            return ports[::-1][0] + 1
