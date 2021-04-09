#!/usr/bin/env python3
import os, sys, argparse, time, json, getpass
#
# the BDFL does not admire scripts which are also importable modules
# well, frack him -- this is how we roll
#
#so absolute imports work in script mode, we need to import from the parent folder
opath = os.path.abspath(".")
abspath = os.path.abspath(__file__)
# print ("CLI PATHS:", opath, abspath)
abspath = abspath[:abspath.rfind('/') + 1]
os.chdir(abspath)
abspath = os.path.abspath("..")
sys.path.insert(0, abspath)

os.chdir(opath)

from burst.burst import *

#
# typing reduction act
#
def complete(x, a):
    num = 0
    match = []
    for k in a:
        if k[:len(x)] == x:
            num += 1
            match.append(k)
    return match, num

verbs = {
    # None,
    'build',
    'run',
    'help',
    'list-servers',
    'status',
    'stop-server',
    'terminate-server',
    'attach',
    'sync',
    'kill'
}

#
# This hack ensures we do not collect new, undocumented 'verbs' (subcommands)
#
def switch(verb, *args):
    # print ("SWITCH:", verb, args, verbs, verb in verbs)
    if verb == None:
        return False
    if verb not in verbs:
        raise Exception("Unknown subcommand: %s  try: 'burst help'" % verb)
    for a in args:
        if a == verb:
            return True
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__, add_help=False)
    add = parser.add_argument
    add("command", nargs='?',                                                               help="Command to run on remote server: %s" % ", ".join(verbs))
    add("--compute-access",     metavar="KEY", dest='access',                               help="libcloud username (aws: ACCESS_KEY)")
    add("--background", "-b",   action="store_true",                                        help="Run task in background mode")
    add("--session-name",       metavar="NAME", dest='burst_user',                          help="Burst session name (defaults to burst-username; "
                                                                                                 "different sessions launch new machine instances)")
    add("--cloudmap",           type=str, default="",  metavar="STORAGE:MOUNT",             help="map (mount) burst storage service to local folder")
    add("--compute-service",    dest='compute_config',metavar="COMPUTE_SERVICE",            help="override default compute configuration service")
    add("--config-file",        metavar="FILE", dest='configfile',                          help="override default config.yml")
    add("--docker-port",        dest='dockerdport', type=int, default=2377, metavar="PORT", help="local port to map to remote host docker daemon"
                                                                                                 "(default: 2377)")
    add("--docker-file",        dest='dockerfile', type=str, default="Dockerfile", metavar="FILE",
                                                                                            help="Docker file (defaults to ./Dockerfile)")
    add("--gpus",                                                                           help="'all', 'none', list of gpus, or prompt if not specified")
    add("--help",               action="store_true",                                        help="Print usage info")
    add("--vm-image",           dest='image',                                               help="libcloud image (aws: ami image_id)")
    add("--local",              action="store_true",                                        help="run on local device")
    add("--tunnel-port", "-p",  dest='portmap', action="append", metavar="LOCAL[:REMOTE]",  help="port mapping; example: -p 8080 or -p 8081:8080")
    add("--gcs-project",        dest='project',                                             help="Google Cloud project ID")
    add("--compute-provider",   dest='provider',default='EC2',                              help="GCE, EC2 etc.")
    add("--pubkey-file",        dest='pubkey',                                              help="public key to access server (defaults to ~/.ssh/id_rsa.pub)")
    add("--compute-region",     dest='region',                                              help="libcloud location (aws: region)")
    add("--compute-secret",     dest='secret',                                              help="libcloud password (aws: SECRET)")
    add("--vm-type",            dest='size',                                                help="aws: instance_type; gce: size)")
    add("--stop",               type=int, default=900, metavar="SECONDS",                   help="seconds before server is stopped (default 900) "
                                                                                                 "0 means never. Use subcommad 'stop' to force stop")
    add("--vm-username",        default="ubuntu",                                           help="remote server username for login")
    add("--storage-config",     metavar="STORAGE_SERVICE",                                  help="override default storage configuration")
    add("--verbose", "-v",      dest='verbosity', type=int, default=0,                      help="-1: just task output 0: status 1-127: more verbose"
                                                                                                 "(default: -1)")
    add("--version",            action="store_true",                                        help="Print version # & exit")

    if len(sys.argv) < 2:
        parser.print_help()
        sys.exit(1)
    #
    # this got a bit tricky.
    # we want to parse args BEFORE the main command as burst options
    # and pass all args AFTER the main command to the command when it runs remotely
    #
    argv = sys.argv[1:]
    args, task_args = parser.parse_known_args(argv)
    set_verbosity(args.verbosity)

    verb, matches = complete(args.command, verbs)
    if matches > 1:
        raise Exception(f"Ambiguous subcommand: {args.command} could be one of: {', '.join(verb)}")
    elif matches == 0:
        verb = args.command
    else:
        verb = verb[0]
        vvprint (f"Expanding subcommand: {args.command} --> {verb}")

    vvprint ("ARGV:", argv)
    vvprint ("BURST:")
    for k, v in args.__dict__.items():
        if v:
            vvprint (f"  {k}=={v}")
    vvprint ("TASK:")
    for k in task_args:
        vvprint (" ", k)

    if verb == 'build' and args.verbosity < 1:
        set_verbosity(9)

    if args.help or switch(verb, 'help'):
        parser.print_help()
        sys.exit(1)

    #override config credentials on command line: --access implies all must be provided
    if args.access:
        args_compute = dictobj()
        args_compute.access = args.access
        args_compute.secret = args.secret
        args_compute.region = args.region
        args_compute.project = args.project
        args_compute.provider = args.provider
    else:
        burst_conf = {}

        #command line overrides:
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
    # t0 = time.time()
    # while time.time()-t0 < args.delay:
    #     vprint ("%d seconds till action" % (args.delay+.5+t0-time.time()))
    #     time.sleep(5)

    #set default burst_user if necessary:
    if not (args.burst_user or args.uuid or args.url or args.local or args.version):
        burst_user = getpass.getuser()
        args.burst_user = "burst-" + burst_user
        vprint ("Session: %s" % args.burst_user)

    # #master switch clause. First, stand-alone options
    if switch(verb, 'list-servers'):
        init(burst_conf)
        # pprint(get_config())
        cconf = get_config()['compute_config']
        v0print ("-------------------------------------------------------------\nSessions with config %s & user %s:" % (cconf, args.burst_user))
        for n, s in list_servers(args.burst_user, burst_conf):
            # print ("DBG:", n.public_ips[0])
            print (s)
            if n.state.lower()=='running':
                cmd = f"ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=error ubuntu@{n.public_ips[0]} 'screen -r -md -X hardcopy .burst_monitor.log; tail -n 2 .burst_monitor.log'"
                os.system(cmd)
        v0print ("-------------------------------------------------------------")

    elif switch(verb, 'stop-server'):
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

    elif switch(verb, 'terminate-server'):
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

    elif switch(verb, 'attach'):
        tunnel = None
        init(burst_conf)
        cconf = get_config()['compute_config']
        url = None
        for node, s in list_servers(args.burst_user, burst_conf):
            vvprint (node, s)
            if node.state.upper() == 'RUNNING':
                if url:
                    raise Exception("multiple docker processes running, this is not supported")
                url = node.public_ips[0]
                break
        if not url:
            print ("No process running")
        else:
            vvprint (f"Attaching to docker process on {url}")
            tunnel, _ = ssh_tunnel(url, args.sshuser, args.portmap, args.dockerdport)
            vvprint ("Tunnel:", tunnel)
            cmd = ["docker", "-H localhost:%s" % args.dockerdport, "ps", "--format", '{{json .}}']
            vvprint (cmd)
            out, err = run(cmd)
            vvprint("PS returns:", out)
            if not out:
                print ("\nNo Docker process found")
            else:
                try:
                    did = json.loads(out)
                    v0print ("Attaching to docker process", did['ID'])
                    cmd = f"docker -H localhost:{args.dockerdport} attach --sig-proxy=false {did['ID']}"
                    vvprint (cmd)
                    vprint("ctrl-C only detaches; --kill to stop")
                    v0print ("---------------------OUTPUT-----------------------")
                    os.system(cmd)
                    v0print ("----------------------END-------------------------")
                except:
                    print ("\nFailed to attach:", out)
                    sys.stdout.flush()
        if tunnel:
            tunnel.kill()

    elif switch(verb, 'kill'):
        tunnel = None
        init(burst_conf)
        cconf = get_config()['compute_config']
        url = None
        for node, s in list_servers(args.burst_user, burst_conf):
            vvprint (node, s)
            if node.state.upper() == 'RUNNING':
                if url:
                    raise Exception("multiple docker processes running, this is not supported")
                url = node.public_ips[0]
                break
        if not url:
            print ("No process running")
        else:
            vvprint (f"Terminating Docker process on {url}")
            tunnel, _ = ssh_tunnel(url, args.sshuser, args.portmap, args.dockerdport)
            vvprint ("Tunnel:", tunnel)
            cmd = ["docker", "-H localhost:%s" % args.dockerdport, "ps", "--format", '{{json .}}']
            vvprint (cmd)
            out, err = run(cmd)
            vvprint("PS returns:", out)
            if not out:
                print ("\nNo Docker process found")
            else:
                try:
                    did = json.loads(out)
                    yes = input(f"Terminating Docker process {did['ID']}, are you sure? (y/n)")
                    if yes == 'y':
                        cmd = f"docker -H localhost:{args.dockerdport} stop {did['ID']}"
                        vvprint (cmd)
                        os.system(cmd)
                        print ("Process terminated")
                    else:
                        print("Aborted")
                except:
                    print ("\nError:", out)
                    sys.stdout.flush()
        if tunnel:
            tunnel.kill()

    elif switch(verb, 'status'):
        tunnel = None
        init(burst_conf)
        cconf = get_config()['compute_config']
        url = None
        for node, s in list_servers(args.burst_user, burst_conf):
            vvprint (node, s)
            if node.state.upper() == 'RUNNING':
                if url:
                    raise Exception("multiple docker processes running, this is not supported")
                url = node.public_ips[0]
                break
        if not url:
            v0print("-------------------------------------------------------------")
            print ("No remote host running")
            v0print("-------------------------------------------------------------")
        else:
            vvprint (f"Looking for docker process on {url}")
            tunnel, _ = ssh_tunnel(url, args.sshuser, args.portmap, args.dockerdport)
            vvprint ("Tunnel:", tunnel)
            cmd = ["docker", "-H localhost:%s" % args.dockerdport, "ps", "--no-trunc", "--format", '{{json .}}']
            vvprint (cmd)
            out, err = run(cmd)
            vvprint("PS returns:", out)
            if not out:
                print ("\nNo Docker process found")
            else:
                try:
                    did = json.loads(out)
                    v0print("-------------------------------------------------------------")
                    print (f"Docker process ID: {did['ID'][:12]}\n"
                           f"Status: {did['Status']}\n"
                           f"Command: {did['Command']}")
                           # f"Mounts: {did['Mounts']}")
                    v0print("-------------------------------------------------------------")
                except:
                    print ("\nError:", out)
                    sys.stdout.flush()
        if tunnel:
            tunnel.kill()

    elif args.version:
        print ("VERSION:", version)

    elif switch(verb, 'configure'):
        if args.configfile:
            yam = args.configfile
        else:
            yam = os.environ['HOME'] + "/.burst/config.yml"
        os.system("burst-config --config_path %s" % yam)

    elif switch(verb, 'build', 'run', 'sync'):
        #no stand-alone options; do burst for reals
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

        args_gpus = args.gpus
        if args.gpus == None:
            if os.path.exists(".burst_gpus"):
                args_gpus = open(".burst_gpus").read().strip()
            else:
                raise Exception("no .burst_gpus; specify --gpus")
        if args_gpus.lower() != 'none':
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

        if verb == 'build':
            task_args = ['echo', 'Build phase 1 success']

        #let's do this thing
        error = burst(task_args, sshuser=args.sshuser, url=args.url, uuid=args.uuid,
              burst_user=args.burst_user, gpus=args.gpus, ports=args.portmap, stop=args.stop,
              image=image, size=size, pubkey=pubkey, dockerfile=args.dockerfile, cloudmap=args.cloudmap,
              dockerdport=args.dockerdport, bgd = args.background, sync_only = verb=='sync', conf = burst_conf)

        if error:
            v0print ("Build failed")
        else:
            if verb == 'build':
                v0print()
                print ("Build phase 2 success")

            vprint ("DONE")
            v0print()
    else:
        vprint()
        print (" subcommand:", verb)