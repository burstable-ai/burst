import  subprocess, time, os, sys, re, socket
from blessings import Terminal
bless_term = Terminal()

MAXLINES=100

def print_red(s, **kw):
    print (bless_term.red(s), **kw)

def run(*args, **kw):
    # print ("DBG", args, kw)
    if 'showoutput' in kw:
        showoutput = kw['showoutput']
        # print("showoutput:", showoutput)
        del kw['showoutput']
    else:
        showoutput = False
    if 'timeout' in kw:
        timeout = float(kw['timeout'])
        if showoutput:
            print("running", args[0], "with timeout:", timeout, end=' ')
        del kw['timeout']
    else:
        timeout = 0
    try:
        if not timeout:
            timeout = 10**10
        # print ("args:", args)
        proc = subprocess.Popen(*args, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
        t0 = time.time()
        out = ""
        complete = False
        while time.time() < t0 + timeout:
            line = proc.stdout.readline().decode('utf8')
            # print ("DBG", type(out), type(line))
            out += line
            i = 0
            while line != "":
                if showoutput:
                    sys.stdout.write(line)
                i += 1
                if i >= MAXLINES:
                    break
                line = proc.stdout.readline().decode('utf8')
                out += line
            if proc.poll() != None:
                complete = True
                #get all output
                line = proc.stdout.readline().decode('utf8')
                out += line
                while line != "":
                    if showoutput:
                        sys.stdout.write(line)
                    sys.stdout.write(line)
                    line = proc.stdout.readline().decode('utf8')
                    out += line
                sys.stdout.flush()
                break
##                sys.stdout.write(".")
##                sys.stdout.flush()
            time.sleep(0.2)
        if not complete:
            proc.kill()

    except subprocess.CalledProcessError as e:
        out = e.output
    return out, complete

#
# run a git command, capture the output
#
def git(cmd, show=False, debug=False):
    if debug:
        print_red ("git %s" % cmd)
    if hasattr(cmd, "lower"):
        cmd = cmd.split()
    out, good = run(["git"] + cmd, showoutput=show)
    if not good:
        err = "ERROR -- git command did not complete"
        print (err, file=sys.stderr)
        out += "\n\n" + err
    return out, not good


def get_branch():
    out, err = git("rev-parse --abbrev-ref HEAD")
    return out.strip()

def get_repo():
    out, err = git("remote -v")
    return out.split()[1]

def get_author():
    return git("log -1 --pretty=format:'%an'")[0].strip().replace("'", "")

def get_username():
    return git("config --get user.name")[0].strip()

def git_status(show=False, debug=False):
    out, err = git("status --porcelain", show=show, debug=debug)
    changes=0
    for row in out.split("\n"):
        row = row.strip()
        if not row:
            continue
        if row[:2] != "??":
            changes += 1
    return changes

import subprocess as sp
from threading import Thread
from queue import Queue, Empty
import time


def test_func(s):
    if not s:
        return ""
    # print ("----------PARSE------------")
    # print (s)
    # print ("~~~~~~~~~~~~~~~~~")
    N = 7
    for L in s.split():
        try:
            N = int(L.strip())
        except:
            pass
    # print ("RESULT:", N)
    # print ("----------/PARSE------------")
    return "BOOM " * N


def stdout_thread(o, q):
    def getchar():
        return o.read(1)

    for c in iter(getchar, b''):
        q.put(c)
    o.close()


def get_sub_stdout(q):
    r = b''
    while True:
        try:
            c = q.get(False)
        except Empty:
            # print ("   EMPTY")
            break
        else:
            # print ("   DATA")
            r += c
    return r

def escape_ansi(line):
    ansi_escape = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    # ansi_escape = re.compile(r'(\x9B|\x1B\[)[0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', line)


SLEEPYTIME = .1
SSH_FORCE_TIMEOUT = 30
class runner:
    def __init__(self, cmd):
        self.pobj = sp.Popen(cmd.split(), stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.STDOUT)
        self.q = Queue()
        self.t = Thread(target=stdout_thread, args=(self.pobj.stdout, self.q))
        self.t.daemon = True
        self.t.start()
        self.in_dat = ''
        self.t0 = time.time()

    # Use advanced machine learning algorithms to ascertain if we have a prompt:
    def has_prompt(self, s):  # A proud moment in hell
        # print ("SSS:", s)
        if "\n" in s:
            s = s.split("\n")[-1]
        s = escape_ansi(s.strip())
        i = s.find(self.prompt)
        if i<0  or i>12:
            # print ("FAIL")
            return False
        # print("PROMPT FOUND")
        return True

    #
    # call interact with user input, returns next process text+prompt
    #
    def interact(self, cmd=None, expect=None):
        if cmd != None:                                   #typically None for first interaction to get prompt
                                                          #if '', still need to write to stdin to keep rolling ball
            # print ("===%s==="%cmd)
            self.pobj.stdin.write(bytes(cmd, 'utf-8'))
            self.pobj.stdin.write(b'\n')
            try:
                self.pobj.stdin.flush()
            except:
                return ''
            self.in_dat = cmd

        if expect==None:
            expect=[]
        elif hasattr(expect, "lower"):
            expect = [expect]
        # print ("EXPECT:", expect)
        o_new = get_sub_stdout(self.q).decode('utf8')
        o_dat = o_new
        while not o_new:
            br = False
            for ex in expect:
                # print ("TEST:", ex, o_new, "||", ex in o_new, "|||")
                if ex in o_new:                           #additional triggers to return such as Y/n prompts
                    br = True
                    break
            if br:
                break
            o_new = get_sub_stdout(self.q).decode('utf8')
            o_dat += o_new
            time.sleep(SLEEPYTIME)
        # print ("DBG A")
        # remove echo:
        # if o_dat.find(self.in_dat+"\r\n")==0:
        #     o_dat=o_dat[len(self.in_dat)+2:]
        return o_dat, self.has_prompt(o_dat)

    def first(self):
        o_dat = ""
        t0 = time.time()
        while True:
            # print ("  FIRST:",o_dat)
            if time.time()-t0 > SSH_FORCE_TIMEOUT:
                return o_dat, True
            o_dat += get_sub_stdout(self.q).decode('utf8')
            spl = o_dat.rstrip().split("\n")
            if len(spl) >= 2 and "last login" in spl[-2].lower():
                break
            if "timed out" in spl[-1]:
                return o_dat, True
            time.sleep(SLEEPYTIME)
        # print (o_dat)
        prompt = escape_ansi(spl[-1])
        prompt.replace("\r", ']').strip()
        i = prompt.find(':')
        if i > 0:
            # print ("III:", i)
            prompt = prompt[0:i+1]
        self.prompt = prompt
        print ("PROMPT: >>>%s<<<" % prompt)
        sys.stdout.flush()
        return o_dat, False

    def exit(self):
        self.pobj.stdin.write(bytes('exit', 'utf-8'))
        self.pobj.stdin.write(b'\n')
        time.sleep(2)
        o_new = get_sub_stdout(self.q).decode('utf8')
        print (o_new)
        sys.stdout.flush()

if __name__=="__main__":
    cmd = "ssh -tt -4 localhost"
    # cmd = "echoz foo"
    print (cmd, end="\n\n")
    run = runner(cmd)
    o = run.first()                                  #get initial startup spam + prompt
    print (o)
    run.interact("pwd")
    run.exit()
    print ("DONE")

# if __name__ == "__main__":
#     print("test run.py")
#     cmd = sys.argv[1:]
#     s, err = run(cmd, timeout=10, showoutput=False)
#     print("output----------\n", s)
#     print("end output------")
#     print("completed:", err)
