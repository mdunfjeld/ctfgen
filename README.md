# CTF Scenario-DSL
This app generates a CTF scenario based on the input specified declaratively using a domain specific language that is designed and created as part of a Master thesis at NTNU Gjøvik.

### Requirements
* oyaml
* python-heatclient
* python-openstackclient


### Setup

```
git clone https://github.com/dunf/master-thesis.git
cd master-thesis
virtualenv3 py3-env
source py3-env/bin/activate
pip3 install oyaml
pip3 install python-heatclient
pip3 install python-openstackclient
```
### Usage
```
# Remember to source OpenStack RC file first
python3 main.py -f examples/example-attack-defense-minimal.yaml --debug --run
```

### Notes
* Until deploy key creation can be implemented properly the program is dependent on linux.
* Openstack VM images must have cloud-init