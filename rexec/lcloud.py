import os, sys, time, argparse, json
import yaml
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeAuthSSHKey
from easydict import EasyDict as dictobj

from verbos import vprint

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

    try:
        f = open(os.environ['HOME'] + "/.rexec/config.yml")
        yconf = yaml.load(f, Loader=yaml.FullLoader)
        f.close()
    except:
        vprint ("config.yml not found")
        yconf = {'EC2': {}, 'GCE': {}}          #dummy yconf

    if 'provider' in conf:
        config.provider = conf['provider']
    else:
        config.provider = yconf['preferred']

    for param in ['access', 'secret', 'region', 'project', 'default_image', 'default_size', 'default_gpu_image',
                  'default_gpu_size', 'default_gpu']:
        if param in conf:
            config[param] = conf[param]
        else:
            config[param] = yconf[config.provider].get(param, None)

    cls = get_driver(Provider[config.provider])

    if config.provider == 'EC2':
        config.driver = cls(config.access, config.secret, region=config.region)

    elif config.provider == 'GCE':
        config.driver = cls(config.access, config.secret, datacenter=config.region, project=config.project)

    else:
        vprint ("ERROR: unknown cloud provider", config.provider)

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
    nodes = config.driver.list_nodes()                      #need to refresh node to get state
    node = [x for x in nodes if x.uuid.find(srv.uuid)==0]
    if node:
        return node[0].state
    vprint ("Cannot find server to determine state; assuming terminated")
    return 'terminated'

def get_server_size(srv):
    if config.provider=='EC2':
        return srv.extra['instance_type']
    elif config.provider=='GCE':
        typ = srv.extra['machineType']
        i = typ.rfind('/')
        return typ[i+1:]

def get_server_image(srv):
    if config.provider=='EC2':
        return srv.extra['image_id']
    elif config.provider=='GCE':
        return srv.extra['image']

def start_server(srv):
    result = srv.start()
    if not result:
        return "error starting server"
    state = None
    while state != 'running':
        state = get_server_state(srv)
        time.sleep(2)
        vprint ("server state:", state)
    vprint ("Waiting for public IP address to be assigned")
    config.driver.wait_until_running([srv])
    vprint("Public IP's:", srv.public_ips)
    while len(srv.public_ips)==0 or srv.public_ips.count(None) == len(srv.public_ips): #Really? Google? [None]????
        # srv = config.driver.list_nodes(ex_node_ids=[srv.id])[0]
        srv = get_server(uuid=srv.uuid)       #seems necessary to refresh to update state
        vprint("Public IP's:", srv.public_ips)
        time.sleep(5)
    return srv

#
# fill in default values for size & image
#
def fix_size_and_image(size, image):
    if image=="DEFAULT_IMAGE":
        image = config.default_image

    if size=="DEFAULT_SIZE":
        size = config.default_size

    if image=="DEFAULT_GPU_IMAGE":
        image = config.default_gpu_image

    if size=="DEFAULT_GPU_SIZE":
        size = config.default_gpu_size
    return size, image

def launch_server(name, size=None, image=None, pubkey=None, conf = None, user=None, gpus=None):
    init(conf)
    size, image = fix_size_and_image(size, image)
    if config.provider=='EC2':
        images = config.driver.list_images(ex_image_ids=[image])
    else:
        images = [x for x in config.driver.list_images() if x.name == image]
    if not images:
        raise Exception("Image %s not found" % image)
    image = images[0]

    sizes = [x for x in config.driver.list_sizes() if x.name == size]
    if not sizes:
        raise Exception("Instance size %s not found" % size)
    size = sizes[0]

    vprint ("Launching instance node, image=%s, name=%s, size=%s" % (image.id, name, size.id))
    if pubkey:
        if config.provider == 'EC2':                #Everybody makes it up
            auth = NodeAuthSSHKey(pubkey)
            node = config.driver.create_node(name, size, image, auth=auth)
        elif config.provider == 'GCE':
            meta = {
                'items': [
                    {
                        'key': 'sshKeys',
                        'value': '%s: %s' % (user, pubkey)
                    }
                ]
            }
            if gpus:
                vprint ("Launching with GPU")
                node = config.driver.create_node(name, size, image, ex_metadata=meta, ex_accelerator_type=config.default_gpu,
                                             ex_accelerator_count=1, ex_on_host_maintenance="TERMINATE")
            else:
                vprint ("Launching without GPU")
                node = config.driver.create_node(name, size, image, ex_metadata=meta)
        else:
            raise Exception("Unsupported clown provider: %s" % config.provider)
    else:
        node = config.driver.create_node(name, size, image)
    vprint ("Waiting for public IP address to be active")
    config.driver.wait_until_running([node])
    while len(node.public_ips)==0:
        # node = config.driver.list_nodes(ex_node_ids=[node.id])[0] #refresh node -- is this really necessary
        node = get_server(uuid=node.uuid)       #seems necessary to refresh to update state
        vprint("Public IP's:", node.public_ips)
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
        vprint ("server state:", state)
    return "success"

def terminate_server(srv):
    result = config.driver.destroy_node(srv)
    if not result:
        return "error terminating server"
    state = None
    while state != 'terminated':
        state = get_server_state(srv)
        time.sleep(2)
        vprint ("server state:", state)
    return "success"

def list_servers(name, conf = None, pretty=False):
    init(conf)
    ret = []
    nodes = config.driver.list_nodes()
    for x in nodes:
        if x.name==name:
            if pretty:
                img = x.extra['image_id'] if config.provider == 'EC2' else x.image
                if img == config.default_image:
                    img += " (default_image, no gpu)"
                elif img == config.default_gpu_image:
                    img += " (default_gpu_image)"
                s = "IMAGE: %s STATE: %s IP's: %s ID: %s/%s" %(img, x.state, x.public_ips, config.provider, x.id)
                ret.append(s)
            else:
                ret.append(x)
    return ret


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    parser.add_argument("--uuid")
    parser.add_argument("--name")
    args, unknown = parser.parse_known_args()

    n = get_server(args.url, args.uuid, args.name)
    pprint (n)