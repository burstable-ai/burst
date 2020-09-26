import sys

VERBOSITY = 0
LIMIT = 100

def set_verbosity(v):
    global VERBOSITY
    VERBOSITY = v

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
    file.write("rexec: %s" % s)

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

def get_piper():
    if VERBOSITY < 3:
        return ">/dev/null 2>/dev/null"
    elif VERBOSITY == 3:
        return ">/dev/null"
    elif VERBOSITY >= 4:
        return ""