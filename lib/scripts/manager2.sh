#!/bin/bash -v

echo "$(ip a | grep -Eo 'inet ([0-9]*\.){3}[0-9]*' | tr -d 'inet ' | grep -v '^127') $(hostname -s).ctf.lan $(hostname -s)" >> /etc/hosts
cat <<EOF >> /etc/cloud/cloud.cfg.d/99_hostname.cfg
#cloud-config
hostname: $(hostname -s)
fqdn: $(hostname -s).ctf.lan
EOF


mkdir -p /mnt/config
mount /dev/disk/by-label/config-2 /mnt/config
cat /mnt/config/openstack/content/0000 >> /home/ubuntu/.ssh/ansible_deploy_key

apt update
apt install -y ansible

# Set ansible_deploy_key to be default SSH key
sed -i 's:#private_key_file = /path/to/file:private_key_file = /home/ubuntu/.ssh/ansible_deploy_key:g' /etc/ansible/ansible.cfg

# Disable "The authenticity of host ... can't be established" message which require user interaction
sed -i 's:#host_key_checking = False:host_key_checking = False:g' /etc/ansible/ansible.cfg