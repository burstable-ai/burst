import sys

VERBOSITY = 0
LIMIT = 100

def set_verbosity(v):
    global VERBOSITY
    VERBOSITY = v

def get_verbosity():
    return VERBOSITY

def _vprint_nolf(*args, **kw):
    # return
    if 'file' not in kw:
        file = sys.stdout
    sarg = ""
    for arg in args:
        sarg += (str(arg) + " ").rstrip()
    s =sarg[:LIMIT]
    s += " " * (LIMIT - len(s))
    s = s.replace("\n", "\r")
    s += "\r"
    file.write("burst: %s" % s)

def v0print(*args, **kw):
    if VERBOSITY >=0:
        print(*args, **kw)

def vprint(*args, **kw):
    if VERBOSITY == 0:
        _vprint_nolf(*args, **kw)
    elif VERBOSITY >= 1:
        print (*args, **kw)

def vvprint(*args, **kw):
    if VERBOSITY >= 2:
        print (*args, **kw)

#docker verbosity
def get_piper():
    if VERBOSITY < 3:
        return ">/dev/null 2>/dev/null"
    elif VERBOSITY & 8:
        return ""
    elif VERBOSITY & 4:
        return ">/dev/null"
    return ""

def get_dockrunflags():
    if VERBOSITY & 128:
        return "-ti"            #run in foreground
    return "-d"

#rsync verbosity
def get_rsync_v():
    if VERBOSITY & 16:
        return "v --progress"
    if VERBOSITY & 32:
        return "vv --progress"
    if VERBOSITY & 64:
        return "vvv --progress"
    if VERBOSITY >= 1:
        return " --progress"
    return ""