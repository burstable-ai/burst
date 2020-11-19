import menus
import summary
import configurers
from config_file_utils import get_config, write_config

CONFIG_FILE = '~/.rexec/config.yml'

def main():

    config = get_config(CONFIG_FILE)
    print('Welcome to rexec!')
    summary.all(config)

    main_selection = menus.main_menu()
    if main_selection == '1':  # Compute Config
        compute_selection = menus.main_service_menu('compute')
        if compute_selection == '1':
            alias, creds = configurers.new_compute()
            config['compute']['configurations'][alias] = creds
        elif compute_selection == '2':
            remove_alias = configurers.remove_service(config, 'compute')
            del config['compute']['configurations'][remove_alias]

    elif main_selection == '2':  # Cloud Config
        storage_selection = menus.main_service_menu('storage')
        if storage_selection == '1':
            alias, creds = configurers.new_storage()
            config['storage']['configurations'][alias] = creds
        elif storage_selection == '2':
            remove_alias = configurers.remove_service(config, 'storage')
            del config['storage']['configurations'][remove_alias]

    elif main_selection == '3':  # Set Defaults
        default_type = menus.default_type_menu()
        if default_type == '1':
            settings = configurers.set_default(config, 'compute')
            config['compute']['settings'] = settings
        elif default_type == '2':
            settings = configurers.set_default(config, 'storage')
            config['storage']['settings'] = settings

    if len(config.get('compute', {}).get('configurations', {})) == 1 and not config['compute']['settings']:
        settings = configurers.set_default(config, 'compute', list(config['compute']['configurations'])[0])
        config['compute']['settings'] = settings

    if len(config.get('storage', {}).get('configurations', {})) == 1 and not config['storage']['settings']:
        settings = configurers.set_default(config, 'storage', list(config['storage']['configurations'])[0])
        config['storage']['settings'] = settings

    write_config(config, CONFIG_FILE)


if __name__ == '__main__':
    main()
