import os, sys, time, argparse, json
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeAuthSSHKey
from easydict import EasyDict as dictobj

config = dictobj()

#
# for now providers are EC2 or GCE
#
def init(conf = None):
    #init is a one-time thang
    if 'driver' in config:
        return

    if conf == None:
        conf = {}

    f = open(os.environ['HOME'] + "/.rexec/config.json")
    jconf = json.load(f)
    f.close()

    if 'provider' in conf:
        config.provider = conf['provider']
    else:
        config.provider = jconf['preferred']

    for param in ['access', 'secret', 'region', 'project']:
        if param in conf:
            config[param] = conf[param]
        else:
            config[param] = jconf[config.provider].get(param, None)

    cls = get_driver(Provider[config.provider])

    if config.provider == 'EC2':
        config.driver = cls(config.access, config.secret, region=config.region)

    elif config.provider == 'GCE':
        config.driver = cls(config.access, config.secret, datacenter=config.region, project=config.project)

    else:
        print ("ERROR: unknown cloud provider", config.provider)

def get_config():
    return config

def get_server(url=None, uuid=None, name=None, conf = None):
    init(conf)
    nodes = config.driver.list_nodes()
    if url:
        node = [x for x in nodes if url in x.public_ips and x.state != 'terminated']
    elif uuid:
        node = [x for x in nodes if x.uuid.find(uuid)==0 and x.state != 'terminated']
    elif name:
        node = [x for x in nodes if x.name==name and x.state != 'terminated']
    else:
        return "error: specify url, uuid, or name"
    return node[0] if node else None

def get_server_state(srv):
    srv = get_server(uuid = srv.uuid)
    if srv:
        return srv.state

def start_server(srv):
    result = srv.start()
    if not result:
        return "error starting server"
    state = None
    while state != 'running':
        state = get_server_state(srv)
        time.sleep(2)
        print ("server state:", state)
    print ("Waiting for public IP address to be assigned")
    config.driver.wait_until_running([srv])
    while len(srv.public_ips)==0:
        # srv = config.driver.list_nodes(ex_node_ids=[srv.id])[0]
        srv = get_server(uuid=srv.uuid)       #seems necessary to refresh to update state
        print("Public IP's:", srv.public_ips)
        time.sleep(5)
    return srv

def launch_server(name, size=None, image=None, pubkey=None, conf = None):
    init(conf)

    images = [x for x in config.driver.list_images() if x.name == size]
    if not images:
        raise Exception("Image %s not found" % image)

    sizes = [x for x in config.driver.list_sizes() if x.name == size]
    if not sizes:
        raise Exception("Instance size %s not found" % size)
    size = sizes[0]

    print ("Launching instance node, image=%s, name=%s, size=%s" % (image.id, name, size.id))
    if pubkey:
        auth = NodeAuthSSHKey(pubkey)
        node = config.driver.create_node(name, size, image, auth=auth)
    else:
        node = config.driver.create_node(name, size, image)
    print ("Waiting for public IP address to be active")
    config.driver.wait_until_running([node])
    while len(node.public_ips)==0:
        # node = config.driver.list_nodes(ex_node_ids=[node.id])[0] #refresh node -- is this really necessary
        node = get_server(uuid=node.uuid)       #seems necessary to refresh to update state
        print("Public IP's:", node.public_ips)
        time.sleep(5)
    return node

def stop_server(srv):
    result = srv.stop_node()
    if not result:
        return "error stopping server"
    state = None
    while state != 'stopped':
        state = get_server_state(srv)
        time.sleep(2)
        print ("server state:", state)
    return "success"

def terminate_server(srv):
    result = config.driver.destroy_node(srv)
    if not result:
        return "error terminating server"
    state = None
    while state != 'terminated':
        state = get_server_state(srv)
        time.sleep(2)
        print ("server state:", state)
    return "success"

def list_servers(name, conf = None):
    init(conf)
    nodes = config.driver.list_nodes()
    nodes = [x for x in nodes if x.name==name]
    return nodes


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    parser.add_argument("--uuid")
    parser.add_argument("--name")
    args, unknown = parser.parse_known_args()

    n = get_server(args.url, args.uuid, args.name)
    pprint (n)