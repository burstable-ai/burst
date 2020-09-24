import sys

LIMIT = 111

def vprint(*args, **kw):
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

