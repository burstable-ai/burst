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

from burst.lcloud import *
from burst.runrun import run
from burst.version import version
from burst.verbos import set_verbosity, get_verbosity, vprint, vvprint, v0print, get_piper, get_rsync_v, get_dockrunflags

os.chdir(opath)

DEFAULT_IMAGE = "burst_image" #FIXME: should be unique to folder structure
SHUTDOWN_IMAGE = "burstableai/burst_shutdown:latest"
# DOCKER_REMPORT = "2376"
# DOCKER_REMOTE = "localhost:"+DOCKER_REMPORT

def burst(args, sshuser=None, url=None, uuid=None, rxuser=None, gpus = "", ports=None, stop=False,
          image=None, size=None, pubkey=None, dockerfile="Dockerfile",
          cloudmap="", dockerdport=2376, conf=None):
    tunnel = None
    try:
        if not os.path.exists(dockerfile):
            raise Exception("Dockerfile not found")
        if not os.path.exists(".dockerignore"):
            raise Exception("""

.dockerignore file not found. Burst requires a .dockerignore to avoid sending excess data to docker build.
Because the working directory is rsync'd to the remote host, you typically only need to send the Dockerfile
and files that are referred to (such as requirements.txt) to the build daemon.

#Template .dockerignore
#Default to ignoring everything:
**
#exceptions (These will be sent to the docker daemon for building):
!/Dockerfile*
!requirements.txt
""")
        #
        # Chunnel container to local via host:
        # on host, docker map remote_port:remote_port
        # on local, ssh tunnel local_port:localhost:remote_port
        #
        host_port_args = []
        docker_port_args = ""
        if ports:
            for pa in ports:
                if ':' in pa:
                    local_port, remote_port = pa.split(':')
                else:
                    remote_port = local_port = pa
                docker_port_args += " -p {0}:{0}".format(remote_port)
                host_port_args.append("-L {0}:localhost:{1}".format(local_port, remote_port))
        # print ("PORTS: |%s|%s|" % (docker_port_args, host_port_args)); exit()
        if url:
            if not sshuser:
                sshuser, url = url.split('@')
        node = None
        if url or uuid or rxuser:
            fresh = False
            node = get_server(url=url, uuid=uuid, name=rxuser, conf=conf)
            if rxuser and not node:
                node = launch_server(rxuser, pubkey=pubkey, size=size, image=image, conf=conf, user=sshuser, gpus=gpus)
                fresh = True
            if node:
                if node.state.lower() != "running":
                    vprint ("Starting server")
                    node = start_server(node)
                url = node.public_ips[0]
                vprint ("Waiting for sshd")
                cmd = ["ssh", "-o StrictHostKeyChecking=no", "-o UserKnownHostsFile=/dev/null", "-o LogLevel=error", "{0}@{1}".format(sshuser, url), "echo", "'sshd responding'"]
                vvprint(cmd)
                good = False
                for z in range(10, -1, -1):
                    ret = run(cmd, timeout=15)
                    if ret[0].strip()[-15:]=='sshd responding':
                        good = True
                        break
                    vprint ("sshd not responding; %d attempts left" % z)
                    if z:
                        time.sleep(5)
                if not good:
                    raise Exception("error in ssh call: %s" % ret[0].strip())
                vvprint ("SSH returns -->%s|%s<--" % ret)
            else:
                raise Exception("Error: node not found")

        if url:
            if fresh:
                print("Configuring Docker")
                # 'sudo apt-get -y update; sudo apt-get -y install docker.io; ' \ #images have docker installed
                cmd = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=error {0}@{1} ' \
                      '"sudo usermod -a -G docker ubuntu; ' \
                      'sudo systemctl unmask docker; sudo service docker start"'.format(sshuser, url)
                vvprint(cmd)
                os.system(cmd)

            vprint ("Connecting through ssh")
            remote = "-H localhost:%s" % dockerdport
            ssh_args = ["ssh", "-o StrictHostKeyChecking=no", "-o UserKnownHostsFile=/dev/null",
                        "-o LogLevel=error", "-NL", "{0}:/var/run/docker.sock".format(dockerdport), "{0}@{1}".format(sshuser, url)]
            for arg in host_port_args:
                ssh_args.insert(3, arg)
            vvprint (ssh_args)
            tunnel = subprocess.Popen(ssh_args)
            time.sleep(2)
            relpath = os.path.abspath('.')[len(os.path.expanduser('~')):]
            relpath = "/_BURST" +  relpath.replace('/', '_') #I can exlain
            locpath = os.path.abspath('.')
            path = "/home/{0}{1}".format(sshuser, relpath)

            cmd = ["docker", "{0}".format(remote), "ps", "--format", '{{json .}}']
            vvprint (cmd)
            out = run(cmd)
            vvprint("PS returns -->%s|%s<--" % out)
            if out[0].strip():
                kills = []
                for x in out[0].split("\n"):
                    if x:
                        try:
                            j = json.loads(x)
                        except:
                            raise Exception("ERROR in Docker check (is Docker installed?): %s" % x)
                        Command = j['Command']
                        if Command.find("burst --stop") < 2:
                            kills.append(j['ID'])
                if kills:
                    vprint ("Killing shutdown processes:", kills)
                    cmd = "docker {0} stop {1} {2} &".format(remote, " ".join(kills), get_piper())
                    vvprint (cmd)
                    os.system(cmd)

            vprint ("Removing topmost layer")        #to avoid running stale image
            cmd = ["docker", "{0}".format(remote), "rmi", "--no-prune", DEFAULT_IMAGE]
            vvprint (cmd)
            out, err = run(cmd)
            vvprint (out)
            # print ("DEEBG ex:", node.extra)
            size, image = fix_size_and_image(size, image)
            if size and size != get_server_size(node):
                raise Exception("FIXME: cannot change size (instance type) -- need to re-launch")

            # get_server_image is broken, need to prompt better here
            # if image and image != get_server_image(node):
            #     raise Exception("FIXME: cannot change host image -- need to terminate & re-launch server")

            vprint ("burst: name %s size %s image %s url %s" % (node.name, size, image, url))

            if cloudmap:
                if remote:
                    stor = get_config()['storage']
                    if stor['provider'] == 'GCS':
                        #create a keyfile & point to it
                        srvacctf = ".rclone_key_%s.json" % stor['settings']['private_key']['private_key_id']
                        f = open(srvacctf, 'w')
                        json.dump(stor['settings']['private_key'], f)
                        f.close()
                        stor['settings']['service_account_file'] = srvacctf

                    # build  & save rclone.conf
                    s = f"[{stor['config']}]\n"
                    for k, v in stor.items():
                        if k != 'settings':
                            s += f"{k} = {v}\n"
                    for k, v in stor['settings'].items():
                        s += f"{k} = {v}\n"
                    f = open(".rclone.conf", 'w')
                    f.write(s)
                    f.close()

            #sync project directory
            cmd = 'rsync -rltzu{4} -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=error" {0}/. {3}@{1}:{2}/'.format(locpath,
                                        url, path, sshuser, get_rsync_v())
            vprint ("Synchronizing project folders")
            vvprint (cmd)
            os.system(cmd)
            if get_config().provider == 'GCE':
                # sync service acct creds (for shutdown)
                cmd = 'rsync -rltzu{4} --relative -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=error" {0}/./.burst/{5} {3}@{1}:{2}/'.format(os.path.expanduser('~'),
                                        url, path, sshuser, get_rsync_v(), get_config().raw_secret)
                vprint("Synchronizing credentials for shutdown")
                vvprint (cmd)
                os.system(cmd)
        else:
            vprint ("burst: running locally")
            remote = ""
            path = os.path.abspath('.')

        vprint ("Building docker container")
        cmd = "docker {1} build . --file {2} -t {0} {3}".format(DEFAULT_IMAGE, remote, dockerfile, get_piper())
        vvprint (cmd)
        os.system(cmd)

        args = " ".join(args)
        gpu_args = "--gpus "+gpus if gpus else ""

        cloud_args = ""
        if cloudmap:
            cloud, host = cloudmap.split(":")
            args = f"bash -c 'mkdir -p {host}; rclone mount --vfs-cache-mode writes --vfs-write-back 0 --config .rclone.conf {cloud}: {host} & sleep 3; {args}; umount {host}'"
            cloud_args = " --privileged"

        vprint ("Running docker container")
        cmd = "docker {3} run {4} {5} --rm -ti -v {2}:/home/burst/work {6} {0} {1}".format(DEFAULT_IMAGE,
                                                                                  args, path, remote, gpu_args, docker_port_args, cloud_args)
        vvprint (cmd)
        vprint ("")
        v0print ("---------------------OUTPUT-----------------------")
        os.system(cmd)
        v0print ("----------------------END-------------------------")
        if url:
            vprint ("Synchronizing folders")
            cmd = "rsync -rltzu{4}  -e 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=error' '{3}@{1}:{2}/.' {0}/".format(locpath,
                                            url, path, sshuser, get_rsync_v())
            vvprint (cmd)
            os.system(cmd)
    except:
        traceback.print_exc()
        v0print ("--------------------------------")

    if url and node:
        if stop == 0:
            vprint ("Stopping VM at %s immediately as instructed" % url)
            stop_server(node)
        else:
            vprint ("Scheduling shutdown of VM at %s for %d seconds from now" % (url, stop))
            conf = get_config()
            if conf.provider == "GCE":
                secret = ".burst/" + conf.raw_secret
            else:
                secret = conf.secret
            # print("SECRET 1:", secret)
            cmd = "docker {7} run --rm {11} -v {9}:/home/burst/work {8} burst --verbosity {12} --stop_instance_by_url {0} --delay={1} --access={2} --secret={3} --region={4} {5} --provider={6} {10}".format(url,
                                                                    stop, conf.access, secret, conf.region,
                                                                    ("--project=" + conf.project) if conf.project else "",
                                                                    conf.provider,
                                                                    remote, SHUTDOWN_IMAGE, path, get_piper(), get_dockrunflags(), get_verbosity())
            # cmd = "docker {0} run --rm -ti {1} burst --version".format(remote, DEFAULT_IMAGE)
            vvprint (cmd)
            vvprint ("Shutdown process container ID:")
            os.system(cmd)

    if tunnel:
        tunnel.kill()

#
# Note this function is typically called by the shutdown process so it does
# not share scope with most of what burst does
#
def stop_instance_by_url(url, conf):
    vprint ("STOP instance with public IP", url)
    # print ("DEBUG", os.path.abspath('.'), conf.secret)
    node = get_server(url=url, conf=conf)
    if not node:
        vprint ("No active instance found for IP", url)
    else:
        vprint ("shutting down node %s" % node)
        stop_server(node)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    parser.add_argument("command", nargs='?',                   help="Command to run on remote server")
    parser.add_argument("--configure", action="store_true",     help="Interactive configuration")
    parser.add_argument("--configfile",                         help="override default config.yml")
    parser.add_argument("--build", action="store_true",         help="Download and build environment")
    parser.add_argument("--sshuser", default="ubuntu",          help="remote server username")
    parser.add_argument("--local", action="store_true",         help="run on local device")
    parser.add_argument("--list-servers", action="store_true",  help="List all associated remote servers")
    parser.add_argument("--terminate-servers", action="store_true",     help="Terminate associated remote servers")
    parser.add_argument("--version", action="store_true",       help="Print version # & exit")
    parser.add_argument("--storage-config",                     help="override default storage configuration")
    parser.add_argument("--compute-config",                     help="override default compute configuration")
    parser.add_argument("--url",                                help="run on remote server specified by url")
    parser.add_argument("--uuid",                               help="run on remote server specified by libcloud uuid")
    parser.add_argument("--burst_user",                         help="Burst user name; defaults to local username")
    parser.add_argument("--gpus", default='all',                help="defaults to 'all'; can be set to specific gpu or 'none'")
    parser.add_argument("-p", action="append", metavar="PORTMAP", help="port mapping; example: -p 8080:8080")
    parser.add_argument("--access",                             help="libcloud username (aws: ACCESS_KEY)")
    parser.add_argument("--secret",                             help="libcloud password (aws: SECRET)")
    parser.add_argument("--region",                             help="libcloud location (aws: region)")
    parser.add_argument("--project",                            help="GCE project ID")
    parser.add_argument("--provider", default='EC2',            help="GCE, EC2 etc.")
    parser.add_argument("--image",                              help="libcloud image (aws: ami image_id")
    parser.add_argument("--size",                               help="libcloud size (aws: instance_type")
    parser.add_argument("--pubkey",                             help="public key to access server (defaults to ~/.ssh/id_rsa.pub)")
    parser.add_argument("--delay", type=int, default=0,         help="delay command by N seconds")
    parser.add_argument("--verbosity", type=int, default=0,     help="-1: just task output 0: status 1-4: more verbose")
    parser.add_argument("--shutdown", type=int, default=900, nargs='?',   help="seconds before server is stopped (default 15 minutes)")
    parser.add_argument("--stop_instance_by_url",               help="internal use")
    parser.add_argument("--cloudmap", type=str, default="",     help="map cloud storage to local mount point")
    parser.add_argument("--dockerfile", type=str, default="Dockerfile",    help="Docker file to build the container with if not ./Dockerfile")
    parser.add_argument("--dockerdport", type=int, default=2376, help="local port to map to remote host docker daemon")
    parser.add_argument("--help", action="store_true",          help="Print usage info")

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    #
    # this got a bit tricky.
    # we want to parse args BEFORE the main command as burst options
    # and pass all args AFTER the main command to the command when it runs remotely
    #
    argv = sys.argv[1:]
    args, unknown = parser.parse_known_args(argv)

    if args.build and args.verbosity < 1:
        set_verbosity(1)
    else:
        set_verbosity(args.verbosity)

    vvprint ("ARGV:", argv)

    if args.command != None:
        i = argv.index(args.command)
    else:
        i = len(argv)

    rexargs = argv[:i]
    vvprint ("REXARGS:", rexargs)
    cmdargs = argv[i:]
    vvprint ("CMDARGS:", cmdargs)
    args = parser.parse_args(rexargs)
    vvprint ("ARGS:", args)

    if args.help:
        parser.print_help()
        sys.exit(1)

    if args.gpus.lower() == 'none':
        args.gpus = None

    if args.access:
        args_compute = dictobj()
        args_compute.access = args.access
        args_compute.secret = args.secret
        args_compute.region = args.region
        args_compute.project = args.project
        args_compute.provider = args.provider
    else:
        burst_conf = {}

        if args.compute_config:
            burst_conf['compute_config'] = args.compute_config

        if args.storage_config:
            burst_conf['storage_config'] = args.storage_config

        if args.configfile:
            burst_conf['configfile'] = args.configfile

    if args.local and (args.uuid or args.url):
        vprint (args)
        parser.error("when specifying --local, do not set --sshuser, --burst_user, --uuid, or --url")
        exit()
    t0 = time.time()
    while time.time()-t0 < args.delay:
        vprint ("%d seconds till action" % (args.delay+.5+t0-time.time()))
        time.sleep(5)

    if not (args.burst_user or args.uuid or args.url or args.local or args.version):
        rxuser = getpass.getuser()
        args.burst_user = "burst-" + rxuser
        vprint ("Session: %s" % args.burst_user)

    if args.stop_instance_by_url:
        stop_instance_by_url(args.stop_instance_by_url, burst_conf)

    elif args.list_servers:
        init(burst_conf)
        # pprint(get_config())
        cconf = get_config()['compute_config']
        v0print ("-------------------------------------------------------------\nSessions with config %s & user %s:" % (cconf, args.burst_user))
        for _, s in list_servers(args.burst_user, burst_conf):
            print (s)
        v0print ("-------------------------------------------------------------")

    elif args.shutdown == None:
        v0print ("-------------------------------------------------------------")
        count = 0
        for node, s in list_servers(args.burst_user, burst_conf):
            if node.state == "stopped":
                continue
            count += 1
            yes = input("Stopping (warm shutdown) %s, are you sure? (y/n)" % s)
            if yes=='y':
                stop_server(node)
            else:
                print ("Aborted")
        if not count:
            print ("no servers to shut down")
        v0print ("-------------------------------------------------------------")

    elif args.terminate_servers:
        v0print ("-------------------------------------------------------------")
        count = 0
        for node, s in list_servers(args.burst_user, burst_conf, terminated=False):
            count += 1
            yes = input("Terminating %s, are you sure? (y/n)" % s)
            if yes=='y':
                terminate_server(node)
            else:
                print ("Aborted")
        if not count:
            print ("no servers to terminate")
        v0print ("-------------------------------------------------------------")

    elif args.version:
        print ("VERSION:", version)

    elif args.configure:
        if args.configfile:
            yam = args.configfile
        else:
            yam = os.environ['HOME'] + "/.burst/config.yml"
        os.system("burst-config --config_path %s" % yam)

    else:
        if args.local:
            pubkey = None
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
                size = 'DEFAULT_GPU_SIZE'
            else:
                size = args.size
            if args.image == None:
                image = 'DEFAULT_GPU_IMAGE'
            else:
                image = args.image
        else:
            if args.size == None:
                size = 'DEFAULT_SIZE'
            else:
                size = args.size
            if args.image == None:
                image = 'DEFAULT_IMAGE'
            else:
                image = args.image

        if args.build:
            cmdargs = ['echo', 'Build phase 1 success']

        burst(cmdargs, sshuser=args.sshuser, url=args.url, uuid=args.uuid,
              rxuser=args.burst_user, gpus=args.gpus, ports=args.p, stop=args.shutdown,
              image=image, size=size, pubkey=pubkey, dockerfile=args.dockerfile, cloudmap=args.cloudmap,
              dockerdport=args.dockerdport, conf = burst_conf)

        if args.build:
            v0print()
            print ("Build phase 2 success")

        vprint ("DONE")
        v0print()
