import os, sys, time
from pprint import pprint
from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver
import config

g_driver = None

def init():
    global g_driver
    cls = get_driver(Provider.EC2)
    g_driver = cls(config.access, config.secret, region=config.region)

def get_server(url):
    if g_driver == None:
        init()
    nodes = g_driver.list_nodes()
    node = [x for x in nodes if url in x.public_ips]
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
    n = get_server(sys.argv[1])
    pprint (n)
