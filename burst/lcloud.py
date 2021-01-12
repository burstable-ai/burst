import os, sys, time, argparse, json
import yaml
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
from libcloud.compute.base import NodeAuthSSHKey
from libcloud.common.google import ResourceNotFoundError
from easydict import EasyDict as dictobj

from burst.verbos import vprint

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

    yam = conf.get('configfile', os.environ['HOME'] + "/.burst/config.yml")

    if os.path.exists(yam):
        #FIXME: check for local overriding .burst
        f = open(yam)
        yconf = yaml.load(f, Loader=yaml.FullLoader)
        f.close()
        if 'compute_config' in conf:
            compute_config = conf['compute_config']
        else:
            compute_config = yconf['compute']['settings']['default_compute']
                                                                                    #this got a bit strained. sorry
        storage_config = None
        if 'storage_config' in conf:                                                #if storage_config passed in, use
            storage_config = conf['storage_config']
        else:
            if 'storage' in yconf:                                                  #otherwise check in config.yml
                storage_config = yconf['storage']['settings']['default_storage']
        if storage_config:                                                          #if it exists,
            storage = yconf['storage']['configurations'][storage_config]            #use it
            storage['config'] = storage_config                                      #and store the config name too
        yconf = yconf['compute']['configurations'][compute_config]
        yconf.update(yconf['settings'])   #easier to deal with all attributes at top level
        yconf['compute_config']=compute_config
        if storage_config:                                                          #if specified,
            yconf['storage'] = storage                                              #pull storage to top level for ease

    else:
        vprint ("config.yml not found")
        yconf = {}          #dummy yconf

    if 'provider' in conf:
        config.provider = conf['provider']
    else:
        if 'provider' in yconf:
            config.provider = yconf['provider']
        else:
            raise Exception("Configuration file %s not available. Try running:\nburst --configure" % yam)

    for param in ['access', 'secret', 'region', 'project', 'default_image', 'default_size', 'default_gpu_image',
                  'default_gpu_size', 'default_gpu', 'storage', 'compute_config']:
        if param in conf:
            config[param] = conf[param]
        else:
            config[param] = yconf.get(param, None)

    cls = get_driver(Provider[config.provider])

    if config.provider == 'EC2':
        config.driver = cls(config.access, config.secret, region=config.region)

    elif config.provider == 'GCE':
        if hasattr(config.secret, 'lower'):         #string points to key file
            privkeypath = config.secret
            config.raw_secret = config.secret
        else:                                       #if dict, create key file
            config.raw_secret = "%s.json" % config.secret['private_key_id']
            privkeypath = "%s/.burst/%s.json" % (os.path.expanduser("~"), config.secret['private_key_id'])
        if not os.path.exists(privkeypath):
            fp =  open(privkeypath, 'w')
            json.dump(config.secret, fp)
            fp.close()
        config.driver = cls(config.access, privkeypath, datacenter=config.region, project=config.project)
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

# not working now that EC2 image == AMI full name
# def get_server_image(srv):
#     if config.provider=='EC2':
#         pprint(srv.extra)
#         return srv.extra['name']
#     elif config.provider=='GCE':
#         return srv.extra['image']

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
    image_full_path = image
    if config.provider=='EC2':
        images = config.driver.list_images(ex_filters={'name': image})
    elif config.provider=='GCE':
        #note: GCE libcloud driver list_images is hella borke, list is incomplete so...
        images = []
        for proj in ["deeplearning-platform-release", "ubuntu-os-cloud"]:
            try:
                im = config.driver.ex_get_image(image, ex_project_list=proj)
                images = [im]
                break
            except ResourceNotFoundError:
                pass
    else:
        ims = config.driver.list_images()
        images = [x for x in ims if x.name == image]
    if not images:
        raise Exception("Image %s not found" % image)
    image = images[0]

    sizes = [x for x in config.driver.list_sizes() if x.name == size]
    if not sizes:
        raise Exception("Instance size %s not found" % size)
    size = sizes[0]
    vprint ("Launching instance image=%s, id=%s, session=%s, type=%s ram=%s disk=%s" % (image_full_path, image.id, name, size.id, size.ram, size.disk))

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

def list_servers(name, conf = None, terminated=True):
    init(conf)
    ret = []
    nodes = config.driver.list_nodes()
    for x in nodes:
        x = get_server(uuid=x.uuid)       #seems necessary to refresh to update state
        if not x:
            continue
        # print ("DBG", terminated, x.state)
        if (not terminated) and (x.state=='terminated'): #don't include terminated
            continue
        if x.name==name:
            ret.append([x])
            img = x.extra['image_id'] if config.provider == 'EC2' else x.image
            if img == config.default_image:
                img += " (default_image, no gpu)"
            elif img == config.default_gpu_image:
                img += " (default_gpu_image)"
            s = "IMAGE: %s STATE: %s IP's: %s ID: %s/%s" %(img, x.state, x.public_ips, config.provider, x.id)
            ret[-1].append(s)
    return ret


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    parser.add_argument("--uuid")
    parser.add_argument("--name")
    args, unknown = parser.parse_known_args()

    n = get_server(args.url, args.uuid, args.name)
    pprint (n)