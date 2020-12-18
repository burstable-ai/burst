import os
import configparser

def get_aws_creds(aws_path='~/.aws'):

    config_parser = configparser.ConfigParser()

    aws_abspath = os.path.expanduser(aws_path)
    config_parser.read(f'{aws_abspath}/credentials')
    config_parser.read(f'{aws_abspath}/config')

    index_map = {}
    print('Select AWS credentials to use:')
    index = -1
    for index, section in enumerate(config_parser.sections()):
        print(f'{index+1}: use "{section}" profile from {aws_abspath}')
        index_map[str(index+1)] = section

    env_access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    env_secret = os.environ.get('AWS_SECRET_ACCESS_KEY')
    env_region = os.environ.get('AWS_DEFAULT_REGION')
    env_available = env_access_key is not None and env_secret is not None and env_region is not None

    if env_available:
        index += 1
        print(f'{index+1}: credentials in enviornment variables')

    print(f'{index+2}: Manually enter credentials')

    selected_index = input('\n1/2> ')

    if selected_index and selected_index in index_map:
        section = config_parser[index_map[selected_index]]
        access_key = section['aws_access_key_id']
        secret = section['aws_secret_access_key']
        region = section.get('region')
    elif env_available and selected_index == str(index+1):
        access_key = env_access_key
        secret = env_secret
        region = env_region
    elif selected_index == str(index+2):
        access_key = input('Access Key> ')
        secret = input('Secret Access Key> ')
        region = input('Region> ')
    else:
        raise Exception('Inavlid Selection')

    if region is None:
        print('This profile has no region')
        if 'region' in dict(config_parser).get('default'):
            default_region = config_parser['default']['region']
            choice = input(f'The "default" has region of {default_region}.  Should we use this? (y/n)> ')
            if choice.lower() == 'y':
                region = default_region
        if region is None:
            region = input('Please enter the region> ')

    return access_key, secret, region


if __name__ == '__main__':
    print(get_aws_creds())  # used for testing
