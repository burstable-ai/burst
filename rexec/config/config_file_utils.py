import os
import yaml

def get_config(file_name):

    config = {}

    path = os.path.expanduser(file_name)
    if os.path.exists(path):
        with open(path) as fp:
            config = yaml.load(fp, Loader=yaml.FullLoader)

    # defines sections in dict for writing
    if 'compute' not in config:
        config['compute'] = {'configurations': {}, 'settings': {}}
    if 'storage' not in config:
        config['storage'] = {'configurations': {}, 'settings': {}}

    return config

def write_config(config, file_name):

    # Removes empty sections
    if len(config.get('storage', {}).get('configurations', {})) == 0:
        del config['storage']
    if len(config.get('compute', {}).get('configurations', {})) == 0:
        del config['compute']

    path = os.path.expanduser(file_name)

    with open(path, 'w') as fp:
        yaml.dump(config, fp)
