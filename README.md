# CTFgen
CTFgen is a platform for creating cyber security testbeds or CTF's based on input from a domain specific language that is designed and created as part of a Master thesis at NTNU Gjøvik.

### Requirements
* oyaml
* python-heatclient
* python-openstackclient
* tqdm

### Setup

```
git clone https://github.com/mdunfjeld/ctfgen.git
cd ctfgen
virtualenv3 py3-env
source py3-env/bin/activate
pip3 install -r requirements.txt
```
### Usage
```
# Define scenario. See examples
# Remember to source OpenStack RC file first
python3 ctfgen.py -f examples/example-jeopardy-verbose.yaml --debug --run
```

### Notes
* Deploy key creation and file transfer is done using `ssh-keygen` and `scp` which breaks cross platform compatibility. Consider implementing this functionality using a python library (e.g python-paramiko).
* Openstack VM images must have cloud-init
* Each node creates its own security group(s). In scenarios with many nodes we might exceed the quota limit for security groups.  
* Ansible inventory is populated with IP addresses after the heat stack is created. Sufficient time must be allocated to ensure that all nodes have aquired an IP address before attempting to populate the inventory. Perhaps DNS can be used to circumvent this.
* Management infrastructure is currently statically defined. Future work should include giving the instructor the option to choose which management nodes is needed depending on the scenario.
