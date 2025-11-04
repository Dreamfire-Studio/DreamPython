from DreamPython.Tools.Debug import dprint, log_exc

def traced(name):
    def deco(fn):
        def wrap(*a, **k):
            dprint(f"[ENTER] {name}")
            try:
                r = fn(*a, **k)
                dprint(f"[EXIT]  {name} -> {str(r)[:200]}")
                return r
            except Exception:
                log_exc(f"[ERROR] {name}")
                raise
        return wrap
    return deco