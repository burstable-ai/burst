#!/usr/bin/env python3
import os, sys, argparse, subprocess, time
from lcloud import *
DEFAULT_IMAGE = "rexec_image"
DOCKER_REMPORT = "2376"
DOCKER_REMOTE = "localhost:"+DOCKER_REMPORT

def rexec(args, user=None, url=None, uuid=None, name=None, gpus = "", ports=None):
    if url:
        if not user:
            user, url = url.split('@')
            return
    else:
        if uuid or name:
            node = get_server(uuid=uuid, name=name)
            if node:
                url = node.public_ips[0]
                if node.state.lower() != "running":
                    print ("RUN RUN RUN")
                    return
            else:
                print ("Error: node not found")
                return
    if url:
        print ("rexec: running on", url)
        ssh_args = ["ssh", "-NL", "{0}:/var/run/docker.sock".format(DOCKER_REMPORT), "{0}@{1}".format(user, url)]
        print (ssh_args)
        # return
        tunnel = subprocess.Popen(ssh_args)
        time.sleep(5)                                    #FIXME get smarter -- wait for output confirming tunnel is live
        remote = "-H " + DOCKER_REMOTE
        relpath = os.path.abspath('.')[len(os.path.expanduser('~')):]
        relpath = "/_REXEC" +  relpath.replace('/', '_') #I can exlain
        locpath = os.path.abspath('.')
        path = "/home/{0}{1}".format(user, relpath)
        cmd = "rsync -vrltzu {0}/* {3}@{1}:{2}/".format(locpath, url, path, user)
        print (cmd)
        os.system(cmd)
    else:
        print ("rexec: running locally")
        remote = ""
        path = os.path.abspath('.')

    cmd = "docker {1} build . -t {0}".format(DEFAULT_IMAGE, remote)
    print (cmd)
    os.system(cmd)

    args = " ".join(args)
    gpu_args = "--gpus "+gpus if gpus else ""
    port_args = ""
    if ports:
        for pa in ports:
            if ':' not in pa:
                pa = "{0}:{0}".format(pa)
            port_args += " -p " + pa
    cmd = "docker {3} run {4} {5} --rm -it -v {2}:/home/rexec {0} {1}".format(DEFAULT_IMAGE,
                                                                              args, path, remote, gpu_args, port_args)
    print (cmd)
    os.system(cmd)
    if url:
        cmd = "rsync -vrltzu '{3}@{1}:{2}/*' {0}/".format(locpath, url, path, user)
        print (cmd)
        os.system(cmd)
        tunnel.kill()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user")
    parser.add_argument("--url")
    parser.add_argument("--uuid")
    parser.add_argument("--name")
    parser.add_argument("--gpus")
    parser.add_argument("-p", action="append")
    args, unknown = parser.parse_known_args()

    rexec(unknown, user=args.user, url=args.url, uuid=args.uuid, name=args.name, gpus=args.gpus, ports=args.p)
    print ("DONE")
