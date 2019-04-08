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
import crypt
from src.data import *
from src.config import get_config
import sys
from src.helpers import debug_yaml

class Component(object):
    """
    See: https://galaxy.ansible.com/docs/using/installing.html
    """

    def __init__(self, component, ansible_group, component_template, requirements, attr, component_resource=None):
        self.component = component
        self.ansible_group = ansible_group
        self.requirements = requirements
        self.component_template = component_template
        self.component_type = attr
        self.component_resource = component_resource
       
        if self.component_type == 'user_accounts':
            self.requirements, self.component_template = self.add_user_account(
                component, requirements, component_template)

        elif self.component_type in ['services', 'vulnerabilities']:
            self.requirements, self.component_template = self.add_from_db(
                self.component, self.component_type, self.requirements, 
                self.component_template, self.component_resource)

    def validate_user_account(self, user):
        for required_setting in ['username', 'password']:
            if required_setting not in user.keys():
                print('Error! Missing required setting {} for user account... '.format(required_setting))
                sys.exit(1)


    def add_user_account(self, settings, req, template):
        self.validate_user_account(settings)
        config = get_config()
        rolename = config.get('ANSIBLE', 'user_role')
        role = OrderedDict({
            'name': 'Configuring user {}'.format(settings['username']),
            'include_role': { 
                'name': rolename
            }
        })
        rolevars = OrderedDict({'vars': {}})
        for key, value in zip(settings.keys(), settings.values()):
            rolevars['vars'].update({
                        key: value
                    })
            role.update(rolevars)
        n = len(template[0]['tasks'])
        template[0]['tasks'].insert(n, role)
        return req, template

    def add_from_db(self, name, component_type, req, template, resource):
        """This should be integrated into PLED"""

        if component_type == 'vulnerabilities':
            db = ansible_vulnerability_roles
        elif component_type == 'services':
            db = ansible_service_roles
        tmp = 'vulnerability' if db == ansible_vulnerability_roles else 'service'

        if name in db.keys():
            component_data  = db.get(name)
            component_name_dsl = component_data['name']

            if not self.is_already_added(name, req):
                req.insert(len(req), component_data)

            role = OrderedDict({
                'name': 'Installing {} {}'.format(tmp, component_name_dsl), 
                'include_role': {
                    'name': str(component_name_dsl)
                }
            })
            if resource is not None:
                rolevars = OrderedDict({'vars': {}})
                for key, value in zip(
                    resource['properties'].keys(), self.component_resource['properties'].values()):
                    rolevars['vars'].update({
                        key: value
                    })
                role.update(rolevars)
            n = len(template[0]['tasks'])
            template[0]['tasks'].insert(n, role)
           
        else:
            print('Error! {} {} is unsupported...'.format(component_type, name))
            sys.exit(1) 
        return req, template


    def is_already_added(self, component, req):
        for s in self.requirements:
            if component in s['name']:
                return True
        return False        

    def get_file(self):
        return self.component_template

    def get_requirements(self):
        return self.requirements
    


