"""Runtime that imitates the HP Prime pieces ING uses, for off-device testing.

Screen drawing goes to a 320x240 PIL image. WAIT/INPUT take scripted actions.
The CAS is NOT available here: b_cas only records the command.
"""
import math, os, re
from PIL import Image, ImageDraw, ImageFont


class PPLError(Exception):
    pass


class EndOfScript(Exception):
    pass


# ---------------- state ----------------
HOME = {c: 0 for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"}
for _k in range(10):
    HOME[f"M{_k}"] = [[0]]
HVARS = {}
ANGLE = "rad"            # "rad" or "deg"
ACTIONS = []             # scripted actions
LOG = []                 # everything notable that happened
CAS_LOG = []
SHOTS = []               # saved screenshots
SHOT_DIR = None
SHOT_PREFIX = "s"
OVERFLOW = []
STRICT_SHORT_CIRCUIT = True

IMG = Image.new("RGB", (320, 240), (255, 255, 255))
DRAW = ImageDraw.Draw(IMG)
_FONTS = {}
FONT_PX = {0: 14, 1: 10, 2: 12, 3: 14, 4: 16, 5: 18, 6: 20, 7: 22}
FONT_FILE = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FALLBACK = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(idx):
    px = FONT_PX.get(int(idx), 14)
    if px not in _FONTS:
        _FONTS[px] = ImageFont.truetype(FONT_FILE, px)
    return _FONTS[px]


def reset(actions=None, angle="rad", shot_dir=None, prefix="s"):
    global ACTIONS, ANGLE, SHOT_DIR, SHOT_PREFIX
    ACTIONS = list(actions or [])
    ANGLE = angle
    LOG.clear(); CAS_LOG.clear(); SHOTS.clear(); OVERFLOW.clear()
    SHOT_DIR = shot_dir
    SHOT_PREFIX = prefix
    DRAW.rectangle([0, 0, 319, 239], fill=(255, 255, 255))


def snapshot(tag=""):
    if SHOT_DIR:
        os.makedirs(SHOT_DIR, exist_ok=True)
        path = os.path.join(SHOT_DIR, f"{SHOT_PREFIX}_{len(SHOTS):03d}.png")
        IMG.save(path)
        SHOTS.append(path)


# ---------------- operators ----------------
def _num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _sat(fn):
    try:
        return fn()
    except OverflowError:
        return float("inf")


def _f(v):
    if isinstance(v, int) and abs(v) > 10**300:
        return float("inf") if v > 0 else float("-inf")
    return v


def add(a, b):
    if isinstance(a, str) and isinstance(b, str):
        return a + b
    if isinstance(a, str) or isinstance(b, str):
        raise TypeError(f"string + non-string: {a!r} + {b!r}")
    if isinstance(a, list) or isinstance(b, list):
        raise TypeError("list arithmetic is not used")
    return _f(a) + _f(b)


def sub(a, b):
    _chk(a, b); return _f(a) - _f(b)


def mul(a, b):
    _chk(a, b); return _sat(lambda: _f(_f(a) * _f(b)))


def div(a, b):
    _chk(a, b)
    if b == 0:
        raise PPLError("division by zero")
    return _f(a) / _f(b)


def mod(a, b):
    _chk(a, b)
    return a - b * math.floor(a / b) if b else a


def neg(a):
    _chk(a, 0); return -a


def pow(a, b):
    _chk(a, b)
    try:
        if a == 0 and b < 0:
            raise PPLError("0 to a negative power")
        if isinstance(a, int) and isinstance(b, int) and 0 <= b <= 40 and abs(a) <= 1000:
            r = a ** b
        else:
            r = float(_f(a)) ** float(_f(b))
    except OverflowError:
        r = float("inf")
    if isinstance(r, complex):
        raise PPLError("complex result")
    return r


def _chk(a, b):
    for v in (a, b):
        if isinstance(v, complex):
            raise PPLError("complex value")
        if not _num(v):
            raise TypeError(f"arithmetic on non-number {v!r}")


def _cmp_ok(a, b):
    if isinstance(a, list) or isinstance(b, list):
        raise TypeError("comparison with a list")
    if isinstance(a, str) != isinstance(b, str):
        raise TypeError(f"comparing string with number: {a!r} vs {b!r}")


def eq(a, b):
    _cmp_ok(a, b); return 1 if a == b else 0


def ne(a, b):
    _cmp_ok(a, b); return 1 if a != b else 0


def lt(a, b):
    _chk(a, b); return 1 if a < b else 0


def gt(a, b):
    _chk(a, b); return 1 if a > b else 0


def le(a, b):
    _chk(a, b); return 1 if a <= b else 0


def ge(a, b):
    _chk(a, b); return 1 if a >= b else 0


def land(a, b):          # both sides are always evaluated, as on the calculator
    return 1 if (a and b) else 0


def lor(a, b):
    return 1 if (a or b) else 0


def lnot(a):
    return 0 if a else 1


def frange(a, b, st=1):
    v = a
    out = []
    n = 0
    while (st > 0 and v <= b + 1e-12) or (st < 0 and v >= b - 1e-12):
        out.append(v)
        v = v + st
        n += 1
        if n > 2_000_000:
            raise RuntimeError("runaway FOR loop")
    return out


def ix(obj, i):
    if isinstance(obj, (list, str)):
        k = int(i)
        if k != i or k < 1 or k > len(obj):
            raise PPLError(f"index {i} out of range (size {len(obj)})")
        return obj[k - 1]
    raise TypeError(f"indexing a non-list {obj!r}")


def setitem(obj, i, v):
    if not isinstance(obj, list):
        raise TypeError("element assignment on non-list")
    k = int(i)
    if k < 1 or k > len(obj):
        raise PPLError(f"index {i} out of range in assignment")
    new = list(obj)
    new[k - 1] = v
    return new


# ---------------- builtins: strings and lists ----------------
def b_DIM(s):
    if not isinstance(s, str):
        raise TypeError("DIM on non-string (use SIZE for lists)")
    return len(s)


def b_SIZE(x):
    if isinstance(x, str):
        raise TypeError("SIZE on a string (use DIM)")
    if not isinstance(x, list):
        raise TypeError("SIZE on non-list")
    return len(x)


def b_MID(s, p, n=None):
    if not isinstance(s, str):
        raise TypeError("MID on non-string")
    if p < 1 or p > len(s):
        raise RuntimeError(f"MID position {p} outside string of length {len(s)}: unsafe on the calculator")
    if n is None:
        return s[int(p) - 1:]
    if n <= 0:
        raise RuntimeError("MID with length <= 0: unsafe on the calculator")
    return s[int(p) - 1:int(p) - 1 + int(n)]


def b_LEFT(s, n):
    if not isinstance(s, str):
        raise TypeError("LEFT on non-string")
    if n < 1 or s == "":
        raise RuntimeError("LEFT with count < 1 or empty string: unsafe on the calculator")
    return s[:int(n)]


def b_RIGHT(s, n):
    if n < 1:
        raise PPLError("RIGHT with count < 1")
    return s[-int(n):]


def b_INSTRING(s, sub_):
    if not (isinstance(s, str) and isinstance(sub_, str)):
        raise TypeError("INSTRING on non-strings")
    if s == "" or sub_ == "":
        raise RuntimeError("INSTRING with an empty string: avoided on the calculator")
    return s.find(sub_) + 1


def b_ASC(s):
    if not isinstance(s, str):
        raise TypeError("ASC on non-string")
    if s == "":
        raise RuntimeError("ASC of an empty string: the calculator raises an error here")
    return [ord(c) for c in s]


def b_CHAR(x):
    if isinstance(x, list):
        if not x:
            raise PPLError("CHAR of empty list")
        return "".join(chr(int(c)) for c in x)
    return chr(int(x))


def fmt_num(x):
    """Rough imitation of Standard number format (12 significant digits)."""
    if isinstance(x, bool):
        x = int(x)
    if isinstance(x, int) and abs(x) > 10**15:
        x = float(_f(x))
    if isinstance(x, int):
        return str(x)
    if x != x or x in (float("inf"), float("-inf")):
        return "NaN"
    if x == int(x) and abs(x) < 1e12:
        return str(int(x))
    ax = abs(x)
    if 1e-4 <= ax < 1e12:
        s = f"{x:.12g}"
        if "e" in s:
            s = f"{x:.11f}".rstrip("0")
        return s
    m, e = f"{x:.11e}".split("e")
    m = m.rstrip("0").rstrip(".")
    return f"{m}E{int(e)}"


def b_STRING(x):
    if isinstance(x, str):
        return x
    if isinstance(x, list):
        return "{" + ",".join(b_STRING(v) for v in x) + "}"
    return fmt_num(x)


def b_CONCAT(a, b):
    if not (isinstance(a, list) and isinstance(b, list)):
        raise TypeError("CONCAT needs two lists")
    return a + b


def b_POS(lst, v):
    if not isinstance(lst, list):
        raise TypeError("POS on non-list")
    if not lst:
        raise RuntimeError("POS on an empty list: avoided on the calculator")
    for k, it in enumerate(lst):
        if type(it) == type(v) or (_num(it) and _num(v)):
            if it == v:
                return k + 1
    return 0


def b_SORT(lst):
    return sorted(lst)


def b_TYPE(x):
    if isinstance(x, str):
        return 2
    if isinstance(x, list):
        return 6
    if isinstance(x, complex):
        return 3
    if _num(x):
        return 0
    return 8


# ---------------- builtins: math ----------------
def _ang_in(v):
    return v if ANGLE == "rad" else math.radians(v)


def _ang_out(v):
    return v if ANGLE == "rad" else math.degrees(v)


def b_ABS(x): _chk(x, 0); return abs(x)
def _whole(fn, x):
    _chk(x, 0)
    if isinstance(x, float) and (x != x or x in (float("inf"), float("-inf"))):
        raise PPLError("not a finite number")
    return fn(x)


def b_FLOOR(x): return _whole(math.floor, x)
def b_CEILING(x): return _whole(math.ceil, x)
def b_IP(x): return _whole(math.trunc, x)


def b_ROUND(x, n):
    _chk(x, n)
    if n < 0:
        raise TypeError("ROUND with negative places is not used")
    f = 10 ** int(n)
    if isinstance(x, float) and (x != x or x in (float("inf"), float("-inf"))):
        raise PPLError("not a finite number")
    try:
        return math.floor(x * f + 0.5) / f if x >= 0 else -math.floor(-x * f + 0.5) / f
    except OverflowError:
        return float(x)


def b_LOG(x):
    _chk(x, 0)
    if x <= 0:
        raise PPLError("LOG of non-positive")
    return math.log10(x)


def b_LN(x):
    _chk(x, 0)
    if x <= 0:
        raise PPLError("LN of non-positive")
    return math.log(x)


def b_EXP(x):
    _chk(x, 0)
    try:
        return math.exp(x)
    except OverflowError:
        raise PPLError("overflow")


def b_MAX(a, b): _chk(a, b); return max(a, b)
def b_MIN(a, b): _chk(a, b); return min(a, b)
def b_SIN(x): _chk(x, 0); return math.sin(_ang_in(x))
def b_COS(x): _chk(x, 0); return math.cos(_ang_in(x))


def b_ACOS(x):
    _chk(x, 0)
    if abs(x) > 1:
        raise PPLError("ACOS out of range")
    return _ang_out(math.acos(x))


def b_COMB(n, k):
    _chk(n, k)
    if k < 0 or k > n:
        return 0
    if n > 100000:
        raise PPLError("COMB too large")
    try:
        return float(math.comb(int(n), int(k)))
    except OverflowError:
        return float("inf")


def b_EVAL(x):
    return x


# ---------------- Home expression evaluator (EXPR) ----------------
def _tan(x): return math.tan(_ang_in(x))
def _asin(x):
    if abs(x) > 1: raise PPLError("ASIN range")
    return _ang_out(math.asin(x))
def _atan(x): return _ang_out(math.atan(x))


def _mat(v):
    import numpy as np
    return np.array(v, dtype=float)


def _from_np(a):
    import numpy as np
    a = np.array(a)
    if a.ndim == 0:
        return float(a)
    return a.tolist()


class _Mat:
    """Tiny matrix wrapper so M1^(-1)*M2 style expressions work."""
    def __init__(self, v):
        import numpy as np
        self.a = np.array(v, dtype=float)
        if self.a.ndim == 1:
            self.a = self.a.reshape(1, -1)
    def __add__(self, o): return self._bin(o, "+")
    def __sub__(self, o): return self._bin(o, "-")
    def _bin(self, o, op):
        if not isinstance(o, _Mat) or o.a.shape != self.a.shape:
            raise PPLError("matrix size mismatch")
        return _Mat(self.a + o.a if op == "+" else self.a - o.a)
    def __mul__(self, o):
        if isinstance(o, _Mat):
            if self.a.shape[1] != o.a.shape[0]:
                raise PPLError("matrix size mismatch")
            return _Mat(self.a @ o.a)
        return _Mat(self.a * o)
    def __rmul__(self, o): return _Mat(self.a * o)
    def __pow__(self, n):
        import numpy as np
        if self.a.shape[0] != self.a.shape[1]:
            raise PPLError("not square")
        try:
            return _Mat(np.linalg.matrix_power(self.a, int(n)))
        except np.linalg.LinAlgError:
            raise PPLError("singular matrix")


def _home_env():
    import numpy as np
    from scipy import stats
    def DET(m):
        if m.a.shape[0] != m.a.shape[1]: raise PPLError("not square")
        return float(np.linalg.det(m.a))
    env = {
        "SIN": b_SIN, "COS": b_COS, "TAN": _tan, "ASIN": _asin, "ACOS": b_ACOS, "ATAN": _atan,
        "SINH": math.sinh, "COSH": math.cosh, "TANH": math.tanh, "TICKS": CLOCK[0],
        "EXP": b_EXP, "LN": b_LN, "LOG": b_LOG, "ABS": abs, "PI_": math.pi,
        "DET": DET,
        "TRN": lambda m: _Mat(m.a.T),
        "RANK": lambda m: float(np.linalg.matrix_rank(m.a)),
        "TRACE": lambda m: float(np.trace(m.a)),
        "EIGENVAL": lambda m: _Mat(np.real(np.linalg.eigvals(m.a))),
        "RREF": lambda m: _Mat(_rref(m.a)),
        "NORMALD_CDF": lambda mu, s, x: float(stats.norm.cdf(x, mu, s)),
        "NORMALD_ICDF": lambda mu, s, p: float(stats.norm.ppf(p, mu, s)),
        "STUDENT": lambda n, x: float(stats.t.pdf(x, n)),
        "STUDENT_CDF": lambda n, x: float(stats.t.cdf(x, n)),
        "STUDENT_ICDF": lambda n, p: float(stats.t.ppf(p, n)),
        "CHISQUARE": lambda n, x: float(stats.chi2.pdf(x, n)),
        "CHISQUARE_CDF": lambda n, x: float(stats.chi2.cdf(x, n)),
        "CHISQUARE_ICDF": lambda n, p: float(stats.chi2.ppf(p, n)),
        "FISHER": lambda n, d, x: float(stats.f.pdf(x, n, d)),
        "FISHER_CDF": lambda n, d, x: float(stats.f.cdf(x, n, d)),
        "FISHER_ICDF": lambda n, d, p: float(stats.f.ppf(p, n, d)),
    }
    return env


def _rref(a):
    import numpy as np
    a = a.astype(float).copy()
    r = 0
    rows, cols = a.shape
    for c in range(cols):
        if r >= rows:
            break
        p = max(range(r, rows), key=lambda i: abs(a[i, c]))
        if abs(a[p, c]) < 1e-12:
            continue
        a[[r, p]] = a[[p, r]]
        a[r] = a[r] / a[r, c]
        for i in range(rows):
            if i != r:
                a[i] = a[i] - a[i, c] * a[r]
        r += 1
    return a


_IDENT = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
EXPR_LOG = []


def b_EXPR(s):
    if not isinstance(s, str):
        raise TypeError("EXPR on non-string")
    EXPR_LOG.append(s)
    if not s.strip():
        raise PPLError("empty expression")
    env = _home_env()
    src = s.replace("π", " PI_ ").replace("^", "**")
    src = re.sub(r"\[\[[-0-9.,\[\] ]*\]\]", lambda m: "MAT_(" + m.group(0) + ")", src)
    env["MAT_"] = _Mat
    names = set(_IDENT.findall(src))
    loc = {}
    for nme in names:
        if nme in env:
            continue
        if nme in HOME:
            v = HOME[nme]
            if nme.startswith("M") and len(nme) == 2 and nme[1].isdigit():
                loc[nme] = _Mat(v)
            else:
                loc[nme] = float(_f(v)) if _num(v) else v
        else:
            raise PPLError(f"unknown name {nme} in EXPR({s!r})")
    try:
        val = eval(src, {"__builtins__": {}}, {**env, **loc})
    except PPLError:
        raise
    except (ZeroDivisionError, OverflowError, ValueError, MemoryError) as ex:
        raise PPLError(f"math error in {s!r}: {ex}")
    except TypeError as ex:
        if "complex" in str(ex):
            raise PPLError("complex value")
        raise
    except SyntaxError as ex:
        raise PPLError(f"syntax error in EXPR({s!r})")
    if isinstance(val, tuple):
        raise PPLError("syntax error (empty parentheses)")
    if isinstance(val, _Mat):
        return val.a.tolist()
    if isinstance(val, complex):
        raise PPLError("complex result")
    if isinstance(val, int) and abs(val) > 10**15:
        val = float(_f(val))
    if isinstance(val, float) and (val != val or val in (float("inf"), float("-inf"))):
        raise PPLError("not a number")
    return val


# ---------------- CAS (not available: record only) ----------------
def b_cas(cmd):
    CAS_LOG.append(cmd)
    inner = cmd
    if inner.startswith("string(") and inner.endswith(")"):
        inner = inner[7:-1]
    return "<<" + inner + ">>"


# ---------------- HVars ----------------
def hvars_names():
    return list(HVARS.keys())


def hvars_get(k):
    if k not in HVARS:
        raise PPLError("no such HVar")
    return HVARS[k]


def hvars_set(k, v):
    HVARS[k] = v


# ---------------- graphics ----------------
def b_RGB(r, g, b):
    return (int(r), int(g), int(b))


def _pix(v, what):
    if not _num(v):
        raise TypeError(f"{what}: coordinate {v!r} is not a number")
    if v != int(v):
        LOG.append(("fractional-coordinate", what, v))
    return int(v)


def b_RECT_P(x1, y1, x2, y2, edge, fill):
    x1, y1, x2, y2 = (_pix(v, "RECT_P") for v in (x1, y1, x2, y2))
    if x2 < x1 or y2 < y1:
        LOG.append(("rect-inverted", x1, y1, x2, y2))
        x1, x2 = min(x1, x2), max(x1, x2)
        y1, y2 = min(y1, y2), max(y1, y2)
    DRAW.rectangle([x1, y1, x2, y2], fill=fill, outline=edge)
    return 0


def b_LINE_P(x1, y1, x2, y2, col):
    x1, y1, x2, y2 = (_pix(v, "LINE_P") for v in (x1, y1, x2, y2))
    DRAW.line([x1, y1, x2, y2], fill=col)
    return 0


def b_TEXTOUT_P(text, x, y, fnt, col, width=None, bg=None):
    if not isinstance(text, str):
        raise TypeError(f"TEXTOUT_P with non-string {text!r}")
    x, y = _pix(x, "TEXTOUT_P"), _pix(y, "TEXTOUT_P")
    f = font(fnt)
    w = DRAW.textlength(text, font=f)
    limit = width if width is not None else 320 - x
    if w > limit + 0.5:
        OVERFLOW.append((text, int(w), int(limit), int(fnt)))
    if width is not None:
        tmp = Image.new("RGBA", (int(width), FONT_PX[int(fnt)] + 6), (0, 0, 0, 0))
        ImageDraw.Draw(tmp).text((0, 0), text, font=f, fill=col)
        IMG.paste(tmp, (x, y), tmp)
    else:
        DRAW.text((x, y), text, font=f, fill=col)
    return x + w


def b_DRAWMENU(*labels):
    f = font(2)
    for k, lab in enumerate(labels):
        if not isinstance(lab, str):
            raise TypeError("DRAWMENU label is not a string")
        x1 = int(k * 320 / 6)
        x2 = int((k + 1) * 320 / 6) - 2
        DRAW.rectangle([x1, 220, x2, 239], fill=(50, 54, 66) if lab else (243, 244, 248))
        if lab:
            w = DRAW.textlength(lab, font=f)
            if w > (x2 - x1) - 2:
                OVERFLOW.append(("menu:" + lab, int(w), x2 - x1 - 2, 2))
            DRAW.text((x1 + (x2 - x1 - w) / 2, 223), lab, font=f, fill=(255, 255, 255))
    return 0


# ---------------- interaction ----------------
MONKEY = None            # random.Random instance for random-walk testing
MONKEY_STEPS = 0
MONKEY_LIMIT = 400
TRACE = []


def _monkey(kind):
    global MONKEY_STEPS
    MONKEY_STEPS += 1
    if MONKEY_STEPS > MONKEY_LIMIT:
        raise EndOfScript("monkey limit")
    r = MONKEY
    if kind == "INPUT":
        act = ("cancel",) if r.random() < 0.12 else ("in", ["~"])
    else:
        u = r.random()
        if u < 0.40:
            act = ("tap", 160, 28 + r.randrange(7) * 27 + 12)
        elif u < 0.60:
            k = r.randrange(12)
            act = ("tap", 4 + (k % 4) * 79 + 37, 29 + (k // 4) * 63 + 29)
        elif u < 0.78:
            act = ("tap", int((r.randrange(6) + 0.5) * 53.3), 230)
        elif u < 0.84:
            act = ("tap", r.randrange(320), r.randrange(240))
        else:
            act = ("key", r.choice([4, 4, 4, 30, 19, 2, 12, 7, 8, 42, 43, 44, 37, 38, 39, 32, 50, 45, 3, 47, 0]))
    TRACE.append(act)
    return act


def _next_action(kind):
    if MONKEY is not None:
        return _monkey(kind)
    if not ACTIONS:
        raise EndOfScript(kind)
    return ACTIONS.pop(0)


CLOCK = [100000]


def b_WAIT(n):
    snapshot()
    act = _next_action("WAIT")
    if act[0] == "stale":          # an event that arrives right after a dialog closed
        return [3, act[1], act[2]]
    CLOCK[0] += 400
    if act[0] == "tap":
        return [3, act[1], act[2]]
    if act[0] == "key":
        return act[1]
    if act[0] == "timeout":
        return -1
    raise RuntimeError(f"script gave {act!r} but the program is waiting for a tap or key")


def b_input(types, current, title, labels, help_, reset_, initial):
    for nm, obj in (("labels", labels), ("help", help_), ("reset", reset_), ("initial", initial)):
        if not isinstance(obj, list) or len(obj) != len(types):
            raise TypeError(f"INPUT {title!r}: {nm} has {len(obj) if isinstance(obj, list) else '?'} items for {len(types)} fields")
    if len(types) > 6:
        raise TypeError("INPUT with more than 6 fields")
    for ty, ini in zip(types, initial):
        if ty == 2 and not isinstance(ini, str):
            raise TypeError(f"INPUT {title!r}: text field with non-text initial value {ini!r}")
        if ty == 0 and not _num(ini):
            raise TypeError(f"INPUT {title!r}: numeric field with non-numeric initial value {ini!r}")
    for lb in labels + help_:
        if not isinstance(lb, str):
            raise TypeError("INPUT label/help is not text")
    LOG.append(("INPUT", title, list(labels), list(help_), list(initial)))
    act = _next_action("INPUT")
    if act[0] == "cancel":
        return [0, None]
    if act[0] != "in":
        raise RuntimeError(f"script gave {act!r} but the program opened the form {title!r} {labels}")
    vals = list(act[1])
    if vals == ["="]:
        vals = list(initial)
    if vals == ["~"]:          # monkey: initial values, sometimes mutated
        vals = list(initial)
        for k, ty in enumerate(types):
            if MONKEY.random() < 0.25:
                if ty == 0:
                    vals[k] = MONKEY.choice([0, -1, 1, 0.5, 1e6, 1e-9, 3, -2.5, 100, 1e30])
                else:
                    vals[k] = MONKEY.choice(["", "x", "1/0", "sin(x", "abc", "0", "-1", "x,y", "2*pi", "ln(-x)", "1e400", "t", "x^x", "y=", "=", "1,2,3", "H2O", "((", "x y"])
        TRACE.append(("vals", title, vals))
    if len(vals) != len(types):
        raise RuntimeError(f"form {title!r} has {len(types)} fields {labels}, script gave {len(vals)}")
    for ty, v in zip(types, vals):
        if ty == 2 and not isinstance(v, str):
            raise RuntimeError("script must give text for a text field")
        if ty == 0 and not _num(v):
            raise RuntimeError("script must give a number for a numeric field")
    return [1, vals]


def b_MSGBOX(s):
    if not isinstance(s, str):
        raise TypeError("MSGBOX with non-string")
    LOG.append(("MSGBOX", s))
    return 0


def b_STARTAPP(name):
    LOG.append(("STARTAPP", name))
    if name not in ("Function", "Graph 3D", "Polar", "Parametric", "Spreadsheet",
                    "Statistics 1Var", "Statistics 2Var", "Inference"):
        raise PPLError("no such app")
    return 0


def b_STARTVIEW(n, r):
    LOG.append(("STARTVIEW", n))
    return 0


def b_EDITMAT(which):
    LOG.append(("EDITMAT", which))
    return 0
