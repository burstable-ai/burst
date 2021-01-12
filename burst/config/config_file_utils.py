import os
import yaml

#
# Set literal style to block (more readable for long strings)
#
def selective_representer(dumper, data):
    return dumper.represent_scalar(u"tag:yaml.org,2002:str", data,
                                   style="|" if "\n" in data else None)

yaml.add_representer(str, selective_representer)


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
    # print ("PATH", path)
    if not os.path.exists(path):
        if path.count('/') >= 2:
            os.mkdir(path[:path.rfind('/')])
    with open(path, 'w') as fp:
        yaml.dump(config, fp)
