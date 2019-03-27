
# See https://galaxy.ansible.com/docs/using/installing.html for instructions on 
# how to define install instructions 
# NB! All roles MUST have a name. 
# For overriding default role variables please check the roles documentation.

"""
********** EXAMPLE*********************************************************
'id': {
    'src': '',
    'name': 'role-name'

***************************************************************************
id: Used from the DSL to designate which software is to be installed. 
    Id must be unique
src: Location where role is downloaded from. 
name: The name the role will be installed as. Needed because the role will
        be referred to from other files. All roles MUST have a name.
***************************************************************************
"""
ansible_service_roles = {
    'apache2': {
        'src': 'https://github.com/dunf/ansible-role-apache',
        'name': 'apache2-role'
    },
    'docker': {
        'src': 'geerlingguy.docker',
        'name': 'geerlingguy.docker'
    },
    'nginx': {
        'src': 'geerlingguy.nginx',
        'name': 'geerlingguy.nginx'
    }

}

#ansible_vulnerability_roles = {
    
#}


challenges = {
    'shellshock': {
        'image': 'hmlio/vaas-cve-2014-6271:latest',
        'name': 'vaas-cve-2014-6271',
        'port': "8080",
    },
    'heartbleed': {
        'image': 'hmlio/vaas-cve-2014-0160',
        'name': 'vaas-cve-2014-0160',
        'port': '1337'
    }
}

linux_image_list = [
    'CentOS 6 (1809) x86_64',                      
    'CentOS 7.3 x86_64',                             
    'CentOS 7.5 x86_64',                             
    'CirrOS 0.3.4 x86_64',                           
    'Debian 8.6.0 (Jessie) stable amd64',
    'Debian 8.7.0 (Jessie) stable amd64',            
    'Debian 9.0.0 (Stretch) stable amd64',           
    'Debian 9.4.2 (Stretch) stable amd64',           
    'Kali Linux 2016.1 xfce amd64',                  
    'Kali Linux 2017.3 xfce amd64',                  
    'Kali Linux 2018.2 xfce amd64',                  
    'Kali Linux 2018.3a xfce amd64',                              
    'Ubuntu Server 14.04 LTS (Trusty Tahr) i386',
    'Ubuntu Server 16.04 LTS (Xenial Xerus) amd64',  
    'Ubuntu Server 16.04 LTS (Xenial Xerus) i386',   
    'Ubuntu Server 16.10 (Yakkety Yak) amd64',       
    'Ubuntu Server 16.10 (Yakkety Yak) i386',      
    'Ubuntu Server 17.04 (Zesty Zapus) amd64',     
    'Ubuntu Server 18.04 LTS (Bionic Beaver) amd64',    # Currently the only supported image
    'Ubuntu Server 18.04 LTS (Bionic Beaver) i386', 
    'Ubuntu Server 18.10 (Cosmic Cuttlefish) amd64',
    'openSUSE Leap 42.3 x86_64'
]

windows_image_list = [
    'Windows 10 1803 Enterprise Eval',            
    'Windows 10 1803 Professional N',              
    'Windows Server 2012 R2 Standard',               
    'Windows Server 2012 R2 Std Eval',               
    'Windows Server 2016 Standard',                  
    'Windows Server 2016 Std Eval',                  
    'Windows Server 2019 Standard',                  
    'Windows Server 2019 Standard Evaluation'
]

flavor_list = [
    'c1.xlarge',
    't1.small',
    'c1.tiny',
    'm1.medium',
    'r1.medium',
    't1.medium',
    't1.large',
    'm1.tiny',
    'r1.small',
    'r1.xlarge',
    'c1.large',
    'm1.large',
    't1.tiny',
    'm1.xlarge',
    'c1.medium',
    'c1.small',
    't1.xlarge',
    'r1.large',
    'r1.tiny',
    'm1.small'
]