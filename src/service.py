from collections import OrderedDict
from src.data import *
import sys
from src.helpers import debug_yaml

class Service(object):
    """
    See: https://galaxy.ansible.com/docs/using/installing.html
    """

    def __init__(self, name, ansible_group, service_template, requirements, attr, service_resource=None):
        self.name = name
        self.ansible_group = ansible_group
        self.requirements = requirements
        self.service_template = service_template
        self.service_type = attr
        self.service_resource = service_resource
       
        if self.service_type == 'vulnerabilities':
            db = ansible_vulnerability_roles
        elif self.service_type == 'services':
            db = ansible_service_roles
        tmp = 'vulnerability' if db == ansible_vulnerability_roles else 'service'

        if name in db.keys():
            service_data  = db.get(name)
            service_name_dsl = service_data['name']

            if not self.is_already_added(name, self.requirements):
                self.requirements.insert(len(self.requirements), service_data)

            role = OrderedDict({
                'name': 'Installing {} {}'.format(tmp, service_name_dsl), 
                'include_role': {
                    'name': str(service_name_dsl)
                }
            })

            if self.service_resource is not None:
                rolevars = OrderedDict({'vars': {}})
                for key, value in zip(
                    self.service_resource['properties'].keys(), self.service_resource['properties'].values()):
                    rolevars['vars'].update({
                        key: value
                    })
                role.update(rolevars)
            n = len(self.service_template[0]['tasks'])
            self.service_template[0]['tasks'].insert(n, role)
           
        else:
            print('Error! {} {} is unsupported...'.format(self.service_type, name))
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
    


