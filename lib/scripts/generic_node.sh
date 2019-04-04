#!/bin/bash -v

cat <<EOF >> /etc/cloud/cloud.cfg.d/99_hostname.cfg
#cloud-config
hostname: $(hostname -s)
fqdn: $(hostname -s).ctf.lan
EOF

apt update
mkdir -p /mnt/config
mount /dev/disk/by-label/config-2 /mnt/config

cat /mnt/config/openstack/content/0000 >> /home/ubuntu/.ssh/authorized_keys
