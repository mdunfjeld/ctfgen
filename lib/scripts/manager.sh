#!/bin/bash -v

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
    
    for playbook in $(ls /home/ubuntu/output/*.yaml | grep -v requirements.yaml | grep -v hosts.yaml | grep -v heat_stack*); do
        ansible-playbook -i /etc/ansible/hosts.yaml $playbook
    done
fi
