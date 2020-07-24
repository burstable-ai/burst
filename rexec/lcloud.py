import os, sys, time, argparse
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
sys.path.insert(0, os.environ['HOME']+"/.rexec")
try:
    import config
except:
    config = None

g_driver = None

def init(access=None, secret=None, region=None):
    global g_driver
    cls = get_driver(Provider.EC2)
    if access==None:
        if config==None:
            raise Exception("no config file or parameters")
        g_driver = cls(config.access, config.secret, region=config.region)
    else:
        g_driver = cls(access, secret, region=region)

def get_server(url=None, uuid=None, name=None, access=None, secret=None, region=None):
    if g_driver == None:
        init(access, secret, region)
    nodes = g_driver.list_nodes()
    if url:
        node = [x for x in nodes if url in x.public_ips]
    elif uuid:
        node = [x for x in nodes if x.uuid.find(uuid)==0]
    elif name:
        node = [x for x in nodes if x.name==name]
    else:
        return "error: specify url, uuid, or name"
    return node[0] if node else None

def get_server_state(srv):
    return g_driver.list_nodes(ex_node_ids=[srv.id])[0].state

def start_server(srv):
    result = srv.start()
    if not result:
        return "error starting server"
    state = None
    while state != 'running':
        state = get_server_state(srv)
        time.sleep(2)
        print ("server state:", state)
    print ("Waiting for IP address to be active")
    g_driver.wait_until_running([srv])
    return "success"

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

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url")
    parser.add_argument("--uuid")
    parser.add_argument("--name")
    args, unknown = parser.parse_known_args()

    n = get_server(args.url, args.uuid, args.name)
    pprint (n)