"""Drive the transpiled ING program with scripted taps, keys and form answers."""
import os, sys, shutil, importlib
sys.path.insert(0, os.path.dirname(__file__))
import pplrt as R
from PIL import Image, ImageDraw, ImageFont

BASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "build", "shots")


def tile(k):
    col, row = (k - 1) % 4, (k - 1) // 4
    return ("tap", 4 + col * 79 + 37, 29 + row * 63 + 29)


def row(k):
    return ("tap", 160, 28 + (k - 1) * 27 + 12)


def soft(k):
    return ("tap", int((k - 0.5) * 53.3), 230)


def key(c):
    return ("key", c)


def form(*vals):
    return ("in", list(vals))


SAME = ("in", ["="])       # accept the form's initial values
CANCEL = ("cancel",)
ESC = key(4)
PAGE2 = soft(2)

_mod = None


def program():
    global _mod
    if _mod is None:
        import ing_py
        _mod = ing_py
    return _mod


def run(name, actions, angle="rad", keep_home=False, quiet=False):
    P = program()
    d = os.path.join(BASE, name)
    if os.path.isdir(d):
        shutil.rmtree(d)
    R.reset(actions, angle=angle, shot_dir=d, prefix=name)
    R.EXPR_LOG.clear()
    if not keep_home:
        for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ":
            R.HOME[c] = 0
    ended = "returned"
    try:
        P.ING()
    except R.EndOfScript as e:
        ended = f"script ended at {e}"
    R.snapshot()
    left = len(R.ACTIONS)
    if not quiet:
        print(f"== {name}: {ended}; shots {len(R.SHOTS)}; unused actions {left}")
        for it in R.LOG:
            if it[0] == "MSGBOX":
                print("   MSGBOX:", it[1])
            if it[0] in ("STARTAPP", "STARTVIEW", "EDITMAT"):
                print("  ", it)
        fr = [it for it in R.LOG if it[0] in ("fractional-coordinate", "rect-inverted")]
        if fr:
            print(f"   COORDENADAS: {len(fr)} avisos, p.ej. {fr[0]}")
        if R.OVERFLOW:
            seen = set()
            for o in R.OVERFLOW:
                if o[0] not in seen:
                    seen.add(o[0])
                    print(f"   OVERFLOW font{o[3]}: {o[1]}px > {o[2]}px  {o[0][:70]!r}")
    return {"ended": ended, "shots": list(R.SHOTS), "log": list(R.LOG), "cas": list(R.CAS_LOG),
            "overflow": list(R.OVERFLOW), "left": left}


def sheet(paths, out, cols=3, scale=2):
    """Contact sheet of screenshots, each scaled up."""
    if not paths:
        return None
    w, h = 320 * scale, 240 * scale
    rows = (len(paths) + cols - 1) // cols
    img = Image.new("RGB", (cols * (w + 8) + 8, rows * (h + 26) + 8), (40, 42, 50))
    d = ImageDraw.Draw(img)
    f = ImageFont.truetype(R.FALLBACK, 14)
    for k, p in enumerate(paths):
        im = Image.open(p).resize((w, h), Image.LANCZOS)
        x = 8 + (k % cols) * (w + 8)
        y = 8 + (k // cols) * (h + 26)
        img.paste(im, (x, y + 18))
        d.text((x, y), os.path.basename(p), font=f, fill=(220, 220, 230))
    os.makedirs(os.path.dirname(out), exist_ok=True)
    img.save(out)
    return out
