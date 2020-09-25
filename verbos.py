import sys

VERBOSITY = 1
LIMIT = 100

def vprint0(*args, **kw):
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

def vprint(*args, **kw):
    if VERBOSITY == 0:
        vprint0(*args, **kw)
    elif VERBOSITY >= 1:
        print (*args, **kw)

def vvprint(*args, **kw):
    if VERBOSITY >= 2:
        print (*args, **kw)
