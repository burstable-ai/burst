#!/usr/bin/env python3
import os, sys, argparse, subprocess, time, traceback, json, getpass
#
# the BDFL does not admire scripts which are also importable modules
# well, frack him -- this is how we roll
#
#so absolute imports work in script mode, we need to import from the parent folder
opath = os.path.abspath(".")
abspath = os.path.abspath(__file__)
# print ("BURST PATHS:", opath, abspath)
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

install_burst_sh = "sudo bash -c 'rm -fr /var/lib/dpkg/lock*" \
                   " /var/cache/apt/archives/lock /var/lib/apt/lists/lock;" \
                   "sudo systemctl stop apt-daily* ; " \
                   "apt-get -y update; " \
                   "apt-get -y install python3-pip; " \
                   "python3 -m pip install --upgrade pip; " \
                   "python3 -m pip install easydict apache-libcloud; " \
                   "rm -fr burst; " \
                   "git clone -b monitor https://github.com/burstable-ai/burst'"      #for reals

                # "git clone -b shutdown_39 https://github.com/danx0r/burst'"  # for testing


def do_ssh(url, cmd):
    ssh_cmd = f'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=error {url} ' \
          f'{cmd}'
    vvprint (ssh_cmd)
    os.system(ssh_cmd)


def ssh_tunnel(url, sshuser, ports, dockerdport):
    # set up ssh tunnel mapping docker socket, ports
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
    ssh_args = ["ssh", "-o StrictHostKeyChecking=no", "-o UserKnownHostsFile=/dev/null",
                "-o ExitOnForwardFailure=yes",
                "-o LogLevel=error", "-NL", "{0}:/var/run/docker.sock".format(dockerdport),
                "{0}@{1}".format(sshuser, url)]
    for arg in host_port_args:
        ssh_args.insert(3, arg)
    vvprint(ssh_args)
    tunnel = subprocess.Popen(ssh_args)
    vvprint("TUNNEL:", tunnel)
    time.sleep(2)
    return tunnel, docker_port_args


def burst(args, sshuser=None, url=None, uuid=None, burst_user=None, gpu=False, ports=None, stop=False,
          image=None, size=None, pubkey=None, dockerfile="Dockerfile",
          cloudmap="", dockerdport=2376, bgd=False, sync_only=False, conf=None):
    error = None
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

        #if url specified, split into user & IP
        if url:
            if not sshuser:
                sshuser, url = url.split('@')

        #launch, restart, or reconnect to node
        node = None

        #unless running --local:
        if url or uuid or burst_user:

            #if server does not exist, launch a fresh one
            fresh = False
            restart = False
            node = get_server(url=url, uuid=uuid, name=burst_user, conf=conf)
            if burst_user and not node:
                node = launch_server(burst_user, pubkey=pubkey, size=size, image=image, conf=conf, user=sshuser, gpu=gpu)
                fresh = True
                restart = True
            if node:

                #if stopped, restart
                if node.state.lower() != "running":
                    restart = True
                    vprint ("Starting server")
                    node = start_server(node)

                #by now we must have a public IP address
                url = node.public_ips[0]

                #wait for ssh daemon to be ready
                vprint ("Waiting for sshd")
                cmd = ["ssh", "-o StrictHostKeyChecking=no", "-o UserKnownHostsFile=/dev/null", "-o LogLevel=error", "{0}@{1}".format(sshuser, url), "echo", "'sshd responding'"]
                vvprint(cmd)
                good = False
                for z in range(10, -1, -1):
                    ret = run(cmd, timeout=15)
                    if ret[0].strip()[-15:]=='sshd responding':
                        good = True
                        break
                    vprint ("still waiting on sshd (this can take a while) -- will try %d more times" % z)
                    if z:
                        time.sleep(5)
                if not good:
                    raise Exception("error in ssh call: %s" % ret[0].strip())
                vvprint ("SSH returns -->%s|%s<--" % ret)
            else:
                raise Exception("Error: node not found")

        docker_port_args = ""

        #we have a url unless running --local:
        if url:

            #if just launched, install docker
            if fresh:
                vprint("Configuring Docker")
                # 'sudo apt-get -y update; sudo apt-get -y install docker.io; ' \ #images have docker installed
                cmd = 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=error {0}@{1} ' \
                      '"sudo usermod -a -G docker ubuntu; ' \
                      'sudo systemctl unmask docker; sudo service docker start"'.format(sshuser, url)
                vvprint(cmd)
                os.system(cmd)

            vprint ("Connecting through ssh")
            tunnel, docker_port_args = ssh_tunnel(url, sshuser, ports, dockerdport)

            #path = absolute working directory on host
            relpath = os.path.abspath('.')[len(os.path.expanduser('~')):]
            relpath = "/_BURST" +  relpath.replace('/', '_') #I can exlain
            locpath = os.path.abspath('.')
            path = "/home/{0}{1}".format(sshuser, relpath)

            if not sync_only:
                # part of check to see if docker is installed and running
                remote = "-H localhost:%s" % dockerdport
                cmd = ["docker", "{0}".format(remote), "ps", "--format", '{{json .}}']
                vvprint(cmd)
                out, err = run(cmd)
                vvprint("PS returns:", out)
                running = len([x for x in out.strip().split("\n") if x])
                if running:
                    raise Exception("docker process already running -- burst does not support multiple processes")

                #prepare to build docker container
                vprint ("Removing topmost layer")        #to avoid running stale image
                cmd = ["docker", "{0}".format(remote), "rmi", "--no-prune", DEFAULT_IMAGE]
                vvprint (cmd)
                out, err = run(cmd)
                if "no such image" in out.lower():
                    out = "Creating new burst_image"
                vvprint (out)

            size, image = fix_size_and_image(size, image)
            if size and size != get_server_size(node):                      #FIXME
                raise Exception("Cannot change size (instance type) or gpu status -- need to re-launch")

            # get_server_image is broken, need to prompt better here
            # if image and image != get_server_image(node):
            # if image and image != get_server_image(node):
            #     raise Exception("FIXME: cannot change host image -- need to terminate & re-launch server")

            vprint ("burst: name %s size %s image %s url %s" % (node.name, size, image, url))

            #if using cloud storage (s3 etc), set up config & auth for rclone
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

            rsync_ignore_path = os.path.abspath("./.burstignore")
            if not sync_only:       #sync_only means from remote to local
                #sync local working data to host
                if not os.path.exists(rsync_ignore_path):
                    vprint("creating empty .burstignore")
                    os.system("touch .burstignore")
                cmd = 'rsync -rltzu{4} --exclude-from {5} -e "ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=error" {0}/. {3}@{1}:{2}/'.format(locpath,
                                            url, path, sshuser, get_rsync_v(), rsync_ignore_path)
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

            #if fresh launch, clone burst locally for monitor
            if fresh:
                vprint ("Installing burst on server")
                vvprint("Delay for apt-get to settle")
                time.sleep(30)      #trust me this helps
                vvprint("Delay done")
                do_ssh(f"{sshuser}@{url}", '"%s"' % install_burst_sh)       #notable quoteables

            if restart:
                vprint ("Starting monitor process for shutdown++")
                #run monitor (in detached screen) to check if user's burst OR rsync is still running
                conf = get_config()
                if conf.provider == "GCE":
                    secret = ".burst/" + conf.raw_secret
                else:
                    secret = conf.secret
                proj = ('--project ' + conf.project) if conf.project else ''
                cmd = f"screen -md bash -c 'cd {path}; /usr/bin/python3 ~/burst/burst/monitor/monitor.py" \
                      f" --ip {url} --access {conf.access} --provider {conf.provider}" \
                      f" --secret={secret} --region {conf.region} {proj}'"
                vvprint (cmd)
                do_ssh(f"{sshuser}@{url}", '"%s"' % cmd)

        else:
            vprint ("burst: running locally")
            remote = ""
            path = os.path.abspath('.')

        if not sync_only:
            #actually build container -- for reals
            vprint ("Building docker container")
            cmd = "docker {1} build . --file {2} -t {0} {3}".format(DEFAULT_IMAGE, remote, dockerfile, get_piper())
            vvprint (cmd)
            os.system(cmd)

            #build argument list
            args = " ".join(args)

            if gpu:
                gpu_args = "--gpus all"
            else:
                gpu_args = ""

            #if mounting storage, add arguments & insert commands before (to mount) and after (to unmount) user-specified args
            cloud_args = ""
            if cloudmap:
                cloud, host = cloudmap.split(":")
                args = f"bash -c 'mkdir -p {host}; rclone mount --vfs-cache-mode writes --vfs-write-back 0 --config .rclone.conf {cloud}: {host} & sleep 3; {args}; umount {host}'"
                cloud_args = " --privileged"

            vprint ("Running docker container")
            background_args = "-td" if bgd else "-ti"
            cmd = f"docker {remote} run {gpu_args} {docker_port_args} --rm {background_args} --label ai.burstable.shutdown={stop} " \
                  f"-v {path}:/home/burst/work {cloud_args} {DEFAULT_IMAGE} {args}"

            #run main task
            vvprint (cmd)
            vprint ("")
            v0print ("---------------------OUTPUT-----------------------")
            sys.stdout.flush()
            if bgd:
                cmd = cmd.split()
                docker_container, err = run(cmd)
                print ("Running in background mode. Container =", docker_container[:11])
            else:
                os.system(cmd)
            sys.stdout.flush()
            v0print ("----------------------END-------------------------")
            sys.stdout.flush()

        #sync data on host back to local
        if url and not bgd:
            vprint ("Synchronizing folders")
            cmd = "rsync -rltzu{4} --exclude-from {5} -e 'ssh -o StrictHostKeyChecking=no -o UserKnownHostsFile=/dev/null -o LogLevel=error' '{3}@{1}:{2}/.' {0}/".format(locpath,
                                        url, path, sshuser, get_rsync_v(), rsync_ignore_path)
            vvprint (cmd)
            os.system(cmd)

    except Exception as ex:
        if get_verbosity() & 64:
            v0print ("--------------------------------")
            traceback.print_exc()
            v0print ("--------------------------------")
        else:
            print ()
        print (ex)
        error = "Exception"
    if tunnel:
        tunnel.kill()
    return error
