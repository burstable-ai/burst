def main_menu():

    print('\nSelect from the options below:')
    print('  1. Set up or remove a compute service')
    print('  2. Set up or remove a cloud service')
    print('  3. Change settings for compute or storage service (i.e. defaults)')
    selection = input('1/2/3> ')

    if selection not in ['1', '2', '3']:
        raise Exception("Invalid selection")

    return selection


def default_type_menu():
    print('\nSelect from the options below:')
    print(f'  1. Change default compute service')
    print(f'  2. Change default storage service')

    selection = input('1/2> ')

    if selection not in ['1', '2']:
        raise Exception("Invalid selection")

    return selection


def main_service_menu(service):

    print('\nSelect from the options below:')
    print(f'  1. Set up a new {service} service')
    print(f'  2. Remove a {service} service')

    selection = input('1/2> ')

    if selection not in ['1', '2']:
        raise Exception("Invalid selection")

    return selection
