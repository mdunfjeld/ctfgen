from collections import OrderedDict
from src.data import *
import sys
from src.helpers import debug_yaml

class Service(object):
    """
    See: https://galaxy.ansible.com/docs/using/installing.html
    """

    def __init__(self, name, ansible_group, service_template, requirements, service_resource=None):
        self.name = name
        self.ansible_group = ansible_group
        self.requirements = requirements
        self.service_template = service_template
        self.service_resource = service_resource
       

        if name in ansible_service_roles.keys():
            service_data  = ansible_service_roles.get(name)
            service_name_dsl = service_data['name']

            if not self.is_already_added(name, self.requirements):
                self.requirements.insert(len(self.requirements), service_data)

            role = OrderedDict({
                    'name': 'Installing service {}'.format(service_name_dsl), 
                    'include_role': {
                        'name': str(service_name_dsl)
                    }})
            if self.service_resource is not None:
                #role.update('vars': {
                # TODO! Implement variable overriding here
                #})  
                pass
            n = len(self.service_template[0]['tasks'])
            self.service_template[0]['tasks'].insert(n, role)
           
        else:
            print('Error! Service {} is unsupported...'.format(name))
            sys.exit(1) 
    
    def is_already_added(self, service, req):
        for s in self.requirements:
            if service in s['name']:
                return True
        return False        
    

    def get_file(self):
        return self.service_template

    def get_requirements(self):
        return self.requirements
    


