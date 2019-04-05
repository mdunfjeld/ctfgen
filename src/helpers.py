import pprint
import oyaml as yaml

def debug_yaml(template):
    a = yaml.dump(template)
    print(a)

def prettyprint(template):
    pp = pprint.PrettyPrinter(indent=2)
    pp.pprint(template)