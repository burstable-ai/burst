
def compute(config):
    print('\nThe following compute services are configured:')
    if 'compute' in config and len(config['compute'].get('configurations', [])) > 0:
        for service in config['compute']['configurations']:
            print(f'  * {service}')
    else:
        print('(none)')

def storage(config):

    print('\nThe following storage services are configured:')
    if 'storage' in config and len(config['storage'].get('configurations', [])) > 0:
        for service in config['storage']['configurations']:
            print(f'  * {service}')
    else:
        print('(none)')

def all(config):

    compute(config)
    storage(config)
