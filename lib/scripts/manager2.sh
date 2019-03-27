#!/bin/bash -v

mkdir -p /mnt/config
mount /dev/disk/by-label/config-2 /mnt/config
cat /mnt/config/openstack/content/0000 >> /home/ubuntu/.ssh/ansible_deploy_key
chmod 600 /home/ubuntu/.ssh/ansible_deploy_key

apt update
apt install -y ansible

export HOME=/root
ansible-pull -U https://github.com/dunf/ansible-role-ctf-manager local.yml
