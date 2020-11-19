def main_menu():

    input_map = {'1': 'compute', '2': 'storage', '3': 'default', '4': 'exit'}

    print('\nSelect from the options below:')
    print('  1. Set up or remove a compute service')
    print('  2. Set up or remove a storage service')
    print('  3. Change settings for compute or storage service (i.e. defaults)')
    print('  4. Exit configuration')
    selection = input(f"{'/'.join(input_map)}> ")

    if selection not in input_map:
        raise Exception("Invalid selection")

    return input_map[selection]


def main_service_menu(service):

    input_map = {'1': 'add', '2': 'remove'}

    print('\nDo you want to:')
    print(f'  1. Set up a new {service} service')
    print(f'  2. Remove a {service} service')

    selection = input(f"{'/'.join(input_map)}> ")

    if selection not in input_map:
        raise Exception("Invalid selection")

    return input_map[selection]


def default_service_menu():

    input_map = {'1': 'compute', '2': 'storage'}

    print('\nDo you want to:')
    print(f'  1. Change default compute service')
    print(f'  2. Change default storage service')
    selection = input(f"{'/'.join(input_map)}> ")

    if selection not in input_map:
        raise Exception("Invalid selection")

    return input_map[selection]
