import os, sys

from burst.config import summary
from burst.config.cred_loaders import get_aws_creds
from burst.config.config_file_utils import get_config

abspath = os.path.abspath(__file__)
abspath = abspath[:abspath.rfind('/') + 1]

# The alias used in the template file to set default images/sizes
TEMPLATE_AWS_ALIAS = 'burst_ec2'

def new_compute(aws_path='~/.aws'):

    print('\nSetting up EC2 on AWS')

    config = get_config(file_name='%sconfig_template.yml' % abspath)['compute']['configurations'][TEMPLATE_AWS_ALIAS]
    config['access'], config['settings']['secret'], config['region'] = get_aws_creds(aws_path)
    alias = input('\nPlease enter an alias (name) to reference these credentials: ')
    # ask if this should be default?

    return alias, config


def new_storage(aws_path='~/.aws'):
    print('\nSetting up S3 on AWS')

    config = {'settings': {}}
    config['provider'] = 'AWS'
    config['type'] = 's3'
    config['settings']['access_key_id'], config['settings']['secret_access_key'], config['settings']['region'] = get_aws_creds(aws_path)
    config['settings']['env_auth'] = False
    config['settings']['acl'] = 'private'
    # config['default_mount_folder'] = input("\nSet the default mount folder: ")

    alias = input('\nPlease enter an alias (name) to reference these credentials: ')
    return alias, config


def remove_service(config, service, remove_alias=None):

    if remove_alias is None:
        getattr(summary, service)(config)
        remove_alias = input('Enter name to remove: ')

    if remove_alias not in config[service].get('configurations', []):
        raise Exception("Name entered is not configured")

    return remove_alias


def set_default(config, service, default_service=None):

    settings = {}

    if default_service is None:
        getattr(summary, service)(config)
        default_service = input('\nEnter the name to set for default compute service: ')
        if default_service not in config[service].get('configurations', []):
            raise Exception("Name entered is not configured")
    else:
        print(f'\nSince {default_service} is the only {service} configuration, it will be set to default.')

    if service == 'compute':
        # default_to_gpu = input("Default to GPU (y/n): ")
        # settings['default_to_gpu'] = True if default_to_gpu.lower() in ['y', 'yes'] else False
        settings['default_compute'] = default_service
    elif service == 'storage':
        # sync_policy = input('Enter default sync policy (hit enter to select recommended "lazy"): ')
        # settings['sync_policy'] = sync_policy if sync_policy else 'lazy'
        settings['default_storage'] = default_service

    return settings

def check_existance(config, service, alias):

    if alias in config[service]['configurations']:
        proceed = input(f"Warning - {alias} is already in use. Overwrite? (y/n)> ")

        if proceed.lower() != 'y':
            sys.exit()
