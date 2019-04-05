import configparser

def get_config():
    config = configparser.ConfigParser()
    config.read('ctfgen.conf')
    return config

def get_config_items(config, section, item):
    item = str(config.get(section, item)).rsplit(' ')
    return [str(x).strip(',') for x in item ]