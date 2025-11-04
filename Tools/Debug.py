import sys, datetime, traceback, os

def dprint(*args):
    msg = " ".join(str(a) for a in args)
    ts = datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
    line = f"[{ts}] {msg}"
    print(line, flush=True)
    try:
        with open("debug.log", "a", encoding="utf-8") as f:
            f.write(line + os.linesep)
    except Exception:
        pass

def log_exc(prefix="EXC"):
    dprint(prefix, traceback.format_exc())