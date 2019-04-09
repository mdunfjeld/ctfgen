#!/bin/bash -v

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

mkdir -p /mnt/config
mount /dev/disk/by-label/config-2 /mnt/config
cat /mnt/config/openstack/content/0000 >> /home/ubuntu/.ssh/ansible_deploy_key
cat /mnt/config/openstack/content/0001 >> /home/ubuntu/.ssh/authorized_keys
chmod 600 /home/ubuntu/.ssh/ansible_deploy_key

apt update
apt install -y ansible

export HOME=/root
ansible-pull -U https://github.com/dunf/ansible-role-ctf-manager local.yml


while [[ ! -d "/home/ubuntu/output" ]]; do
    sleep 10
    echo $(date) >> /home/ubuntu/bootstrap.log
done

if [[ -d "/home/ubuntu/output" ]]; then
    cp /home/ubuntu/output/*.yaml /etc/ansible/
    cd /etc/ansible/
    ansible-galaxy install -r /etc/ansible/requirements.yaml
    
    # Playbooks MUST have .yml extension. All other files MUST have .yaml
    for playbook in $(ls /home/ubuntu/output/*.yml); do      
        ansible-playbook -i /etc/ansible/hosts.yaml $playbook
    done
fi
