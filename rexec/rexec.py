#!/usr/bin/env python3
import os, sys, argparse, subprocess, time, traceback, json, getpass

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

def rexec(args, sshuser=None, url=None, uuid=None, rxuser=None, gpus = "", ports=None, stop=False,
          access=None, secret=None, region=None, image=None, size=None, pubkey=None, dockerfile="Dockerfile"):
    tunnel = None
    try:
        if url:
            if not sshuser:
                sshuser, url = url.split('@')
        node = None
        if url or uuid or rxuser:
            node = get_server(url=url, uuid=uuid, name=rxuser, access=access, secret=secret, region=region)
            if rxuser and not node:
                node = launch_server(rxuser, access=access, secret=secret, region=region, pubkey=pubkey, size=size, image=image)
            if node:
                if node.state.lower() != "running":
                    print ("Starting server")
                    node = start_server(node)
                url = node.public_ips[0]
                print ("Waiting for sshd")
                cmd = ["ssh", "-o StrictHostKeyChecking=no", "{0}@{1}".format(sshuser, url), "echo", "'sshd responding'"]
                print(cmd)
                good = False
                for z in range(6, -1, -1):
                    ret = run(cmd, timeout=15)
                    if ret[0].strip()=='sshd responding':
                        good = True
                        break
                    print ("sshd not responding; %d attempts left" % z)
                    if z:
                        time.sleep(5)
                if not good:
                    raise Exception("error in ssh call: %s" % ret[0].strip())
                print ("SSH returns -->%s|%s<--" % ret)
            else:
                raise Exception("Error: node not found")

        if url:
            remote = "-H " + DOCKER_REMOTE
            ssh_args = ["ssh", "-o StrictHostKeyChecking=no", "-NL", "{0}:/var/run/docker.sock".format(DOCKER_REMPORT), "{0}@{1}".format(sshuser, url)]
            print (ssh_args)
            tunnel = subprocess.Popen(ssh_args)
            time.sleep(5)
            relpath = os.path.abspath('.')[len(os.path.expanduser('~')):]
            relpath = "/_REXEC" +  relpath.replace('/', '_') #I can exlain
            locpath = os.path.abspath('.')
            path = "/home/{0}{1}".format(sshuser, relpath)

            cmd = ["docker", "{0}".format(remote), "ps", "--format", '{{json .}}']
            print (cmd)
            out = run(cmd)
            # print("PS returns -->%s|%s<--" % out)
            if out[0].strip():
                kills = []
                for x in out[0].split("\n"):
                    if x:
                        j = json.loads(x)
                        Command = j['Command']
                        if Command.find("rexec --stop") <2:
                            kills.append(j['ID'])
                if kills:
                    print ("Killing shutdown processes:", kills)
                    cmd = "docker {0} stop {1}".format(remote, " ".join(kills))
                    print (cmd)
                    os.system(cmd)
            print ("Removing topmost layer")        #to avoid running stale image
            cmd = ["docker", "{0}".format(remote), "rmi", "--no-prune", DEFAULT_IMAGE]
            print (cmd)
            out, err = run(cmd)
            print (out)

            if size and size != node.extra['instance_type']:
                raise Exception("FIXME: cannot change size (EC2 instance type) -- need to re-launch")
            if image and image != node.extra['image_id']:
                raise Exception("FIXME: cannot change image (EC2 ami) -- need to terminate & re-launch server")
            print ("rexec: name %s size %s image %s url %s" % (node.name, node.extra['instance_type'], node.extra['image_id'], url))
            cmd = "rsync -vrltzu {0}/* {3}@{1}:{2}/".format(locpath, url, path, sshuser)
            print (cmd)
            os.system(cmd)
        else:
            print ("rexec: running locally")
            remote = ""
            path = os.path.abspath('.')


        cmd = "docker {1} build . --file {2} -t {0}".format(DEFAULT_IMAGE, remote, dockerfile)
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
        print ("\n\n---------------------OUTPUT-----------------------")
        os.system(cmd)
        print ("----------------------END-------------------------\n\n")
        if url:
            cmd = "rsync -vrltzu '{3}@{1}:{2}/*' {0}/".format(locpath, url, path, sshuser)
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
            print (cmd[:80] + "...")
            print ("Shutdown process container ID:")
            os.system(cmd)

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
    parser.add_argument("--sshuser", default="ubuntu",          help="remote server username")
    parser.add_argument("--local", action="store_true",         help="run on local device")
    parser.add_argument("--list-servers", action="store_true",  help="List all associated remote servers")
    parser.add_argument("--terminate", action="store_true",     help="Terminate associated remote servers")
    parser.add_argument("--url",                                help="run on remote server specified by url")
    parser.add_argument("--uuid",                               help="run on remote server specified by libcloud uuid")
    parser.add_argument("--rexecuser",                          help="Rexec user name; defaults to local username")
    parser.add_argument("--gpus",                               help="docker run gpu option (usually 'all')")
    parser.add_argument("-p", action="append",                  help="docker port mapping")
    parser.add_argument("--access",                             help="libcloud username (aws: ACCESS_KEY)")
    parser.add_argument("--secret",                             help="libcloud password (aws: SECRET)")
    parser.add_argument("--region",                             help="libcloud location (aws: region)")
    parser.add_argument("--image",                              help="libcloud image (aws: ami image_id")
    parser.add_argument("--size",                               help="libcloud size (aws: instance_type")
    parser.add_argument("--pubkey",                             help="public key to access server (defaults to ~/.ssh/id_rsa.pub)")
    parser.add_argument("--delay", type=int, default=0,         help="delay command by N seconds")
    parser.add_argument("--shutdown", type=int, default=900,    help="seconds before server is stopped (default 15 minutes)")
    parser.add_argument("--stop_instance_by_url",               help="internal use")
    parser.add_argument("--dockerfile", type=str, default="Dockerfile",    help="Docker file to build the container with if not ./Dockerfile")
    args, unknown = parser.parse_known_args()
    if args.local and (args.uuid or args.url):
        print (args)
        parser.error("when specifying --local, do not set --sshuser, --rexecuser, --uuid, or --url")
        exit()
    t0 = time.time()
    while time.time()-t0 < args.delay:
        print ("%d seconds till action" % (args.delay+.5+t0-time.time()))
        time.sleep(5)

    if not (args.rexecuser or args.uuid or args.url or args.local):
        rxuser = getpass.getuser()
        print ("Rexec username:", rxuser)
        args.rexecuser = "rexec_" + rxuser

    if args.stop_instance_by_url:
        stop_instance_by_url(args.stop_instance_by_url, access=args.access, secret=args.secret, region=args.region)

    elif args.list_servers:
        for s in list_servers(args.rexecuser, access=args.access, secret=args.secret, region=args.region):
            print (s)

    else:

        if args.pubkey==None:
            try:
                f=open(os.path.expanduser("~") + "/.ssh/id_rsa.pub")             #FIXME: a bit cheeky
                pubkey=f.read()
                f.close()
            except:
                print ("Public key not found in usual place; please specify --pubkey")
        if args.gpus:
            if args.size == None:
                size = 'g4dn.xlarge'
            else:
                size = args.size
            if args.image == None:
                image = 'ami-008d8ed4bd7dc2485'
            else:
                image = args.image
        else:
            if args.size == None:
                size = 't2.small'
            else:
                size = args.size
            if args.image == None:
                image = 'ami-0ba3ac9cd67195659'
            else:
                image = args.image

        rexec(unknown, sshuser=args.sshuser, url=args.url, uuid=args.uuid,
              rxuser=args.rexecuser, gpus=args.gpus, ports=args.p, stop=args.shutdown,
              access=args.access, secret=args.secret, region=args.region,
              image=image, size=size, pubkey=pubkey, dockerfile=args.dockerfile)
        print ("DONE")
