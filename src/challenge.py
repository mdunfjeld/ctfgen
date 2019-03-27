from collections import OrderedDict
from src.data import *
from src.helpers import debug_yaml


class Challenge(object):
    def __init__(self, name, data, challenge_template, requirements, used_ports=None):
        self.name = name
        self.data = data
        self.challenge_template = challenge_template
        self.requirements = requirements       



        if name in challenges:
            challenge_data = challenges.get(name)
            
            if 'properties' not in self.data.keys() or 'port' not in self.data['properties'].keys():
                port = challenge_data['port']
            else:
                port = self.data['properties']['port']    

            role = OrderedDict({
                'name': 'Installing challenge {}'.format(name), 
                'include_role': {
                    'name': 'docker-container',

                },
                'vars': {
                    'image': str(challenge_data['image']),
                    'name': str(challenge_data['name']),
                    'public_ports': str(port)
                }
            })
            challenge_template[0]['tasks'].append(role)            

    def get_file(self):
        return self.challenge_template

    def get_requirements(self):
        return self.requirements