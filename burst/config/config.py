#!/usr/bin/env python3
import os, sys, argparse

#for absolute imports to work in script mode, we need to import from the root folder
opath = os.path.abspath(".")
abspath = os.path.abspath(__file__)
abspath = abspath[:abspath.rfind('/') + 1]
os.chdir(abspath)
abspath = os.path.abspath("../..")
sys.path.insert(0, abspath)

from burst.config import menus, summary, configurers
from burst.config.config_file_utils import get_config, write_config

os.chdir(opath)

# CONFIG_FILE = '~/.burst/config.yml'

def main():

    args = parse_arguments()

    config = get_config(args.config_path)
    print('Welcome to the burst tool configuration!')
    if args.main_choice in [None, 'summary']:
        summary.all(config)

    main_selection = args.main_choice if args.main_choice else menus.main_menu()
    if main_selection == 'compute':
        second_selection = args.second_choice if args.second_choice else menus.main_service_menu('compute')
        if second_selection == 'add':
            alias, creds = configurers.new_compute(aws_path=args.aws_path)
            configurers.check_existance(config, 'compute', alias)
            config['compute']['configurations'][alias] = creds
            print(f'{alias} has been added to compute')
        elif second_selection == 'remove':
            remove_alias = configurers.remove_service(config, 'compute', remove_alias=args.third_choice)
            del config['compute']['configurations'][remove_alias]
            print(f'{remove_alias} has been removed from compute')

    elif main_selection == 'storage':
        second_selection = args.second_choice if args.second_choice else menus.main_service_menu('storage')
        if second_selection == 'add':
            alias, creds = configurers.new_storage(aws_path=args.aws_path)
            config['storage']['configurations'][alias] = creds
            print(f'{alias} has been added to storage')
        elif second_selection == 'remove':
            remove_alias = configurers.remove_service(config, 'storage', remove_alias=args.third_choice)
            del config['storage']['configurations'][remove_alias]
            print(f'{remove_alias} has been removed from storage')

    elif main_selection == 'default':
        second_selection = args.second_choice if args.second_choice else menus.default_service_menu()
        if second_selection == 'compute':
            settings = configurers.set_default(config, 'compute')
            config['compute']['settings'] = settings
        elif second_selection == 'storage':
            settings = configurers.set_default(config, 'storage')
            config['storage']['settings'] = settings

    else:
        return 0

    if len(config.get('compute', {}).get('configurations', {})) == 1 and not config['compute']['settings']:
        settings = configurers.set_default(config, 'compute', list(config['compute']['configurations'])[0])
        config['compute']['settings'] = settings

    if len(config.get('storage', {}).get('configurations', {})) == 1 and not config['storage']['settings']:
        settings = configurers.set_default(config, 'storage', list(config['storage']['configurations'])[0])
        config['storage']['settings'] = settings

    write_config(config, args.config_path)


def parse_arguments():

    parser = argparse.ArgumentParser(description=__doc__)

    parser.add_argument('main_choice', choices=['compute', 'storage', 'default', 'summary'], nargs='?')
    parser.add_argument('second_choice', nargs='?')
    parser.add_argument('third_choice', nargs='?')

    parser.add_argument('--aws_path', '-a', default='~/.aws', help='Specify location of AWS credentials (default "~/.aws")')
    parser.add_argument('--config_path', default="~/.burst.config.yml", help='Specify location of config file (default "~/.burst.config.yml")')

    args = parser.parse_args()

    if args.main_choice in ['compute', 'storage'] and args.second_choice not in ['add', 'remove', None]:
        raise Exception("Can only specify 'add' or 'remove' when configuring compute")
    elif args.main_choice == 'default' and args.second_choice not in ['compute', 'storage', None]:
        raise Exception("Can only specify 'compute' or 'storage' when configuring defaults")

    return args


if __name__ == '__main__':
    main()
