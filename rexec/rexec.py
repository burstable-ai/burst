#!/usr/bin/env python3
import os, sys, argparse, subprocess, time, traceback

#
# the BDFL does not admire scripts which are also importable modules
# well, frack him -- this is how we roll
#
#so absolute imports work in script mode, we need to import from the parent folder
opath = os.path.abspath(".")
abspath = os.path.abspath(__file__)
abspath = abspath[:abspath.rfind('/') + 1]
os.chdir(abspath)
abspath = os.path.abspath("..")
sys.path.insert(0, abspath)

from rexec.lcloud import *
from rexec.runrun import run

os.chdir(opath)

DEFAULT_IMAGE = "rexec_image" #FIXME: should be unique to folder structure
DOCKER_REMPORT = "2376"
DOCKER_REMOTE = "localhost:"+DOCKER_REMPORT

def rexec(args, user=None, url=None, uuid=None, name=None, gpus = "", ports=None, stop=False,
          access=None, secret=None, region=None):
    tunnel = None
    try:
        if url:
            if not user:
                user, url = url.split('@')
        node = None
        if url or uuid or name:
            node = get_server(url=url, uuid=uuid, name=name, access=access, secret=secret, region=region)
            if node:
                url = node.public_ips[0]
                if node.state.lower() != "running":
                    print ("Starting", url)
                    start_server(node)
                    print ("Waiting for sshd")
                    cmd = ["ssh", "{0}@{1}".format(user, url), "echo", "'sshd responding'"]
                    print(cmd)
                    good = False
                    for z in range(3, -1, -1):
                        ret = run(cmd)
                        if ret[0].strip()=='sshd responding':
                            good = True
                            break
                        print ("sshd not responding; %d attempts left" % z)
                        if z:
                            time.sleep(10)
                    if not good:
                        raise Exception("error in ssh call: %s" % ret[0].strip())
                    print ("SSH returns -->%s|%s<--" % ret)
            else:
                raise Exception("Error: node not found")

        if url:
            print ("rexec: running on", url)
            ssh_args = ["ssh", "-NL", "{0}:/var/run/docker.sock".format(DOCKER_REMPORT), "{0}@{1}".format(user, url)]
            print (ssh_args)
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
    except:
        traceback.print_exc()
        print ("--------------------------------")

    if url and node:
        if stop == 0:
            print ("Stopping VM at %s immediately as instructed" % url)
            stop_server(node)
        else:
            print ("Scheduling shutdown of VM at %s for %d seconds from now" % (url, stop))
            acc, sec, reg = get_credentials()       # may be  in config or as parameters
            cmd = "docker {5} run --rm -d {6} rexec --stop_instance_by_url {0} --delay={1} --access={2} --secret={3} --region={4}".format(url,
                                                                                                    stop, acc, sec, reg, remote, DEFAULT_IMAGE)
            print (cmd)
            print ("~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            sys.stdout.flush()
            os.system(cmd)
            print ("~~~-----------------------------------~~")
            sys.stdout.flush()

    if tunnel:
        tunnel.kill()

def stop_instance_by_url(url, access=None, secret=None, region=None):
    print ("STOP", url, access, region)
    node = get_server(url=url, access=access, secret=secret, region=region)
    if not node:
        print ("No active instance found for URL", url)
    else:
        print ("shutting down node %s" % node)
        stop_server(node)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--user")
    parser.add_argument("--url")
    parser.add_argument("--uuid")
    parser.add_argument("--name")
    parser.add_argument("--gpus")
    parser.add_argument("--access")
    parser.add_argument("--secret")
    parser.add_argument("--region")
    parser.add_argument("--delay", type=int, default=0)
    parser.add_argument("--shutdown", type=int, default=0)
    parser.add_argument("--stop_instance_by_url")
    parser.add_argument("-p", action="append")
    args, unknown = parser.parse_known_args()

    t0 = time.time()
    while time.time()-t0 < args.delay:
        print ("%d seconds till action" % (args.delay+.5+t0-time.time()))
        time.sleep(5)

    if args.stop_instance_by_url:
        stop_instance_by_url(args.stop_instance_by_url, access=args.access, secret=args.secret, region=args.region)

    else:
        rexec(unknown, user=args.user, url=args.url, uuid=args.uuid,
              name=args.name, gpus=args.gpus, ports=args.p, stop=args.shutdown,
              access=args.access, secret=args.secret, region=args.region)
        print ("DONE")
