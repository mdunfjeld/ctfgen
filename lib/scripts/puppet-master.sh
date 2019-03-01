#!/bin/bash -v

apt update
apt install -y puppet puppet-master

echo "$(ip a | grep -Eo 'inet ([0-9]*\.){3}[0-9]*' | tr -d 'inet ' | grep -v '^127') $(hostname -s).ctf.lan $(hostname -s)" >> /etc/hosts
cat <<EOF >> /etc/cloud/cloud.cfg.d/99_hostname.cfg
#cloud-config
hostname: $(hostname -s)
fqdn: $(hostname -s).ctf.lan
EOF

cat <<EOF >> /etc/puppet/puppet.conf
[main]
    server = puppet-master.ctf.lan
    environment = production
EOF