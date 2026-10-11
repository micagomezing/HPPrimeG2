#!/usr/bin/env python3
"""Strict PPL-subset parser + linter + PPL->Python transpiler.

Only the subset used by ING is accepted; anything else is an error, so this
doubles as a syntax checker for the conventions the program relies on.
"""
import re, sys

KEYWORDS = {"BEGIN","END","IF","THEN","ELSE","FOR","FROM","TO","STEP","DO","WHILE",
            "REPEAT","UNTIL","IFERR","RETURN","LOCAL","EXPORT","AND","OR","NOT","MOD",
            "CASE","DEFAULT","BREAK","CONTINUE","DOWNTO","XOR","KILL","VIEW","KEY"}

# builtin -> (min args, max args)
BUILTINS = {
 "DIM":(1,1),"MID":(2,3),"LEFT":(2,2),"RIGHT":(2,2),"INSTRING":(2,2),"ASC":(1,1),
 "CHAR":(1,1),"STRING":(1,1),"EXPR":(1,1),"CONCAT":(2,2),"SIZE":(1,1),"POS":(2,2),
 "SORT":(1,1),"TYPE":(1,1),"ABS":(1,1),"FLOOR":(1,1),"CEILING":(1,1),"IP":(1,1),
 "ROUND":(2,2),"LOG":(1,1),"LN":(1,1),"EXP":(1,1),"MAX":(2,2),"MIN":(2,2),
 "SIN":(1,1),"COS":(1,1),"ACOS":(1,1),"COMB":(2,2),"RGB":(3,3),
 "RECT_P":(6,6),"LINE_P":(5,5),"TEXTOUT_P":(5,7),"DRAWMENU":(6,6),
 "WAIT":(1,1),"MSGBOX":(1,1),"STARTAPP":(1,1),"STARTVIEW":(2,2),
 "EDITMAT":(1,1),"EVAL":(1,1),
}
HOME_VARS = set("ABCDEFGHIJKLMNOPQRSTUVWXYZ") | {"M0","M1","M2","M3","M4","M5","M6","M7","M8","M9"}

# Names that must never be used as identifiers (case-insensitive): PPL/CAS
# commands, Home/app variables, constants.
RESERVED = set(x.upper() for x in """
ABS ACOS ACOSH ACOT ACSC ADDCOL ADDROW ALOG AND ANS APPROX ARC ARC_P ARG ASC ASEC ASIN ASINH
ATAN ATANH AVARS AFILES ANOTE APROGRAM AXES B BEGIN BINOMIAL BITAND BITOR BLIT BLIT_P BREAK
C CAS CASE CEILING CHAR CHECK CHISQUARE CHOOSE COMB CONCAT CONJ CONTINUE COS COSH COT CROSS CSC
CURSOR D DATE DEFAULT DEGREE DELCOL DELROW DET DIFF DIM DIMGROB DIMGROB_P DISP DO DOT DRAWMENU
E EDITLIST EDITMAT EIGENVAL EIGENVV ELSE END ENTRY EVAL EXACT EXP EXPAND EXPORT EXPR F FACTOR
FILLPOLY FILLPOLY_P FISHER FLOOR FNROOT FOR FP FREEZE FROM FSOLVE G GETKEY GETPIX GETPIX_P GROBH
GROBW H HANGLE HCOMPLEX HDIGITS HFORMAT HVARS I IDENMAT IF IFERR IFTE IM INPUT INSTRING INT INTEGER
INV INVERSE INVERT IP ISKEYDOWN ITERATE J K KEY KILL L LANGUAGE LAPLACE LEFT LIMIT LINE LINE_P
LN LNP1 LOCAL LOG LOWER LSQ LU M MAKELIST MAKEMAT MANT MAX MEAN MEDIAN MID MIN MOD MOUSE MSGBOX
N NORM NORMALD NOT NTHROOT O OR P PERM PI PIECEWISE PIXOFF PIXON PIXON_P POISSON POLYCOEF POLYEVAL
POLYROOT POS PRINT PROOT PURGE Q QR QUO QUOTE R RANDINT RANDMAT RANDOM RANDSEED RANK RE RECT
RECT_P REM REPEAT REPLACE RETURN REVERSE RGB RIGHT ROUND ROWNORM RREF S SCALE SEC SIGN SIMPLIFY
SIN SINH SIZE SOLVE SORT SQ SQRT STARTAPP STARTVIEW STEP STRING STUDENT SUB SUBGROB SUBST SUM
SVD SWAPCOL SWAPROW T TAN TANH TAYLOR TEXTOUT TEXTOUT_P THEN TICKS TIME TO TRACE TRIANGLE TRN
TRUNCATE TYPE U UNTIL UPPER UTPC UTPF UTPN UTPT V VIEW W WAIT WHILE X XMAX XMIN XOR XPON XTICK
XZOOM Y YMAX YMIN YTICK YZOOM Z TMIN TMAX TSTEP NMIN NMAX HMIN HMAX HWIDTH LABELS RECENTER METHOD
NUMSTART NUMSTEP NUMTYPE NUMZOOM NUMINDEP NBITEM MINVAL MAXVAL MEDVAL MEANX MEANY SX SY SCOV CORR
COEFDET SERRX SERRY BASE BITS SIGNED NBPMT IPYR PV PMT FV PPYR CPYR BEG CONF ALPHA POOLED ALTHYP
RESULT RESID FIT GRIDDOTS GRIDLINES TRUE FALSE NIL INF INFINITY UNDEF RAD DEG ROW COL LIST MAT
MATRIX VECTOR STR NUM EXPRS LEN LENGTH COUNT ID APPS APP TEVAL DOLIST DOSUBS NSUB ENDSUB STREAM
MAP ZIP APPLY SEQ RANGE DELTA PIECE WHEN ERRORNO NAN POW FLOAT REAL COMPLEX EQ NE LT GT LE GE
""".split())


class PPLSyntaxError(Exception):
    pass


TOKEN_RE = re.compile(r"""
   (?P<ws>[ \t\r]+)
 | (?P<nl>\n)
 | (?P<comment>//[^\n]*)
 | (?P<pragma>\#pragma[^\n]*)
 | (?P<string>"[^"\n]*")
 | (?P<number>\d+\.\d+|\d+|\.\d+)
 | (?P<ident>[A-Za-z_Ͱ-Ͽ][A-Za-z0-9_Ͱ-Ͽ]*)
 | (?P<op>:=|==|<>|<=|>=|[-+*/^(){}\[\],;<>.=])
""", re.X)


def lex(src):
    toks = []
    line = 1
    pos = 0
    while pos < len(src):
        m = TOKEN_RE.match(src, pos)
        if not m:
            raise PPLSyntaxError(f"line {line}: unexpected character {src[pos]!r}")
        kind = m.lastgroup
        text = m.group(kind)
        pos = m.end()
        if kind == "nl":
            line += 1
            continue
        if kind in ("ws", "comment", "pragma"):
            continue
        if kind == "number" and pos < len(src) and src[pos] in "eE" and re.match(r"[eE][-+]?\d", src[pos:]):
            raise PPLSyntaxError(f"line {line}: E-notation number literal is not allowed")
        if kind == "ident" and text.upper() in KEYWORDS:
            if text != text.upper():
                raise PPLSyntaxError(f"line {line}: keyword {text} must be upper case")
            kind = "kw"
        toks.append((kind, text, line))
    toks.append(("eof", "", line))
    return toks


class Parser:
    def __init__(self, toks):
        self.t = toks
        self.i = 0
        self.funcs = {}          # name -> nparams
        self.func_order = []
        self.globals = []
        self.warnings = []
        self.out = []
        self.ind = 0
        self.scope = None        # set of locals for current function
        self.used = None
        self.tmp = 0
        self.all_idents = {}     # ident -> first line
        self.iferr_depth = 0
        self.params = set()
        self.findings = []       # strict-format findings
        self.inv_builtins = {}   # name -> set of arg counts
        self.inv_stmt = {}       # statement kind -> count
        self.inv_ops = {}
        self.max_depth = 0
        self.depth = 0

    # --- token helpers
    def peek(self, k=0):
        return self.t[self.i + k]

    def nxt(self):
        tok = self.t[self.i]
        self.i += 1
        return tok

    def err(self, msg, tok=None):
        tok = tok or self.peek()
        raise PPLSyntaxError(f"line {tok[2]}: {msg} (near {tok[1]!r})")

    def expect(self, kind, text=None):
        tok = self.nxt()
        if tok[0] != kind or (text is not None and tok[1] != text):
            self.err(f"expected {text or kind}", tok)
        return tok

    def accept(self, kind, text=None):
        tok = self.peek()
        if tok[0] == kind and (text is None or tok[1] == text):
            self.i += 1
            return tok
        return None

    def emit(self, s):
        self.out.append("    " * self.ind + s)

    def note_ident(self, name, line):
        self.all_idents.setdefault(name, line)

    # --- program
    def parse_program(self):
        while self.peek()[0] != "eof":
            tok = self.peek()
            if tok[0] == "kw" and tok[1] == "LOCAL":
                self.nxt()
                names = self.ident_list()
                self.expect("op", ";")
                self.globals.extend(names)
            else:
                self.parse_function()
        return "\n".join(self.out)

    def ident_list(self):
        names = [self.expect("ident")]
        while self.accept("op", ","):
            names.append(self.expect("ident"))
        if len(names) > 8:
            self.err(f"more than 8 variables in one LOCAL ({len(names)})", names[0])
        for n in names:
            self.note_ident(n[1], n[2])
        return [n[1] for n in names]

    def parse_function(self):
        self.accept("kw", "EXPORT")
        name = self.expect("ident")
        self.note_ident(name[1], name[2])
        if name[1] in self.funcs:
            self.err("function defined twice", name)
        self.expect("op", "(")
        params = []
        if not self.accept("op", ")"):
            params.append(self.expect("ident")[1])
            while self.accept("op", ","):
                params.append(self.expect("ident")[1])
            self.expect("op", ")")
        for p in params:
            self.note_ident(p, name[2])
        self.expect("kw", "BEGIN")
        self.funcs[name[1]] = len(params)
        self.func_order.append(name[1])
        self.scope = set(params)
        self.params = set(params)
        self.used = set()
        self.assigned = set(params)
        self.emit(f"def {name[1]}({', '.join(params)}):")
        self.ind += 1
        if self.globals:
            self.emit("global " + ", ".join(self.globals))
        self.parse_block(("END",))
        self.expect("kw", "END")
        self.expect("op", ";")
        self.emit("return 0")
        self.ind -= 1
        self.emit("")
        unused = [v for v in self.scope if v not in self.used and v not in params]
        if unused:
            self.warnings.append(f"{name[1]}: unused locals {sorted(unused)}")
        self.scope = None

    def parse_block(self, enders):
        n = 0
        while True:
            tok = self.peek()
            if tok[0] == "kw" and tok[1] in enders:
                break
            if tok[0] == "eof":
                self.err("unexpected end of file")
            self.parse_stmt()
            n += 1
        if n == 0:
            self.emit("pass")

    def parse_stmt(self):
        tok = self.peek()
        kind = tok[1] if tok[0] == "kw" else "asignacion/llamada"
        self.inv_stmt[kind] = self.inv_stmt.get(kind, 0) + 1
        if tok[0] == "kw":
            k = tok[1]
            if k == "LOCAL":
                self.nxt()
                names = self.ident_list()
                self.expect("op", ";")
                for nme in names:
                    if nme in self.scope:
                        self.err(f"local {nme} declared twice", tok)
                    if nme in self.globals:
                        self.err(f"local {nme} hides a program global", tok)
                    self.scope.add(nme)
                    self.emit(f"{nme} = 0")
                return
            if k == "IF":
                self.nxt()
                c = self.parse_expr()
                self.expect("kw", "THEN")
                self.emit(f"if {c}:")
                self.ind += 1
                self.parse_block(("ELSE", "END"))
                self.ind -= 1
                if self.accept("kw", "ELSE"):
                    self.emit("else:")
                    self.ind += 1
                    self.parse_block(("END",))
                    self.ind -= 1
                self.expect("kw", "END")
                self.expect("op", ";")
                return
            if k == "FOR":
                self.nxt()
                v = self.expect("ident")
                self.use_var(v, assign=True)
                self.expect("kw", "FROM")
                a = self.parse_expr()
                self.expect("kw", "TO")
                b = self.parse_expr()
                st = "1"
                if self.accept("kw", "STEP"):
                    st = self.parse_expr()
                self.expect("kw", "DO")
                self.emit(f"for {v[1]} in R.frange({a}, {b}, {st}):")
                self.ind += 1
                self.parse_block(("END",))
                self.ind -= 1
                self.expect("kw", "END")
                self.expect("op", ";")
                return
            if k == "WHILE":
                self.nxt()
                c = self.parse_expr()
                self.expect("kw", "DO")
                self.emit(f"while {c}:")
                self.ind += 1
                self.parse_block(("END",))
                self.ind -= 1
                self.expect("kw", "END")
                self.expect("op", ";")
                return
            if k == "REPEAT":
                self.nxt()
                self.emit("while True:")
                self.ind += 1
                self.parse_block(("UNTIL",))
                self.expect("kw", "UNTIL")
                c = self.parse_expr()
                self.expect("op", ";")
                self.emit(f"if {c}: break")
                self.ind -= 1
                return
            if k == "IFERR":
                self.nxt()
                self.emit("try:")
                self.ind += 1
                self.iferr_depth += 1
                self.parse_block(("THEN",))
                self.ind -= 1
                self.expect("kw", "THEN")
                self.emit("except R.PPLError:")
                self.ind += 1
                self.parse_block(("ELSE", "END"))
                self.iferr_depth -= 1
                self.ind -= 1
                if self.peek()[1] == "ELSE":
                    self.err("IFERR ... ELSE is not used in this code base")
                self.expect("kw", "END")
                self.expect("op", ";")
                return
            if k == "RETURN":
                if self.iferr_depth > 0:
                    self.findings.append(f"line {tok[2]}: RETURN inside an IFERR block")
                self.nxt()
                if self.accept("op", ";"):
                    self.emit("return 0")
                else:
                    e = self.parse_expr()
                    self.expect("op", ";")
                    self.emit(f"return {e}")
                return
            self.err(f"keyword {k} is not allowed here")
        # assignment or call
        if tok[0] != "ident":
            self.err("statement expected")
        name = tok[1]
        nx = self.peek(1)
        # HVars("X"):=expr
        if name == "HVars" and nx[1] == "(":
            self.nxt(); self.nxt()
            key = self.parse_expr()
            self.expect("op", ")")
            self.expect("op", ":=")
            e = self.parse_expr()
            self.expect("op", ";")
            self.emit(f"R.hvars_set({key}, {e})")
            return
        if nx[1] == ":=":
            self.nxt(); self.nxt()
            self.assign_to(tok, None)
            return
        if nx[1] == "(" and self.is_var(name):
            # element assignment  v(idx):=expr
            self.nxt(); self.nxt()
            idx = self.parse_expr()
            self.expect("op", ")")
            self.expect("op", ":=")
            self.assign_to(tok, idx)
            return
        # plain call statement
        e = self.parse_expr()
        self.expect("op", ";")
        self.emit(e)

    def assign_to(self, tok, idx):
        name = tok[1]
        if name in self.params and not (name in HOME_VARS):
            self.findings.append(f"line {tok[2]}: assignment to parameter {name}")
        # INPUT needs its variables written back
        if self.peek()[1] == "INPUT" and self.peek(1)[1] == "(":
            if idx is not None:
                self.err("INPUT into a list element")
            self.nxt(); self.nxt()
            vars_, types = self.parse_input_spec()
            args = []
            while self.accept("op", ","):
                args.append(self.parse_expr())
            self.expect("op", ")")
            self.expect("op", ";")
            if len(args) != 5:
                self.err("INPUT must be called with title, labels, help, reset, initial", tok)
            self.use_var(tok, assign=True)
            self.emit(f"_t = R.b_input({types!r}, [{', '.join(vars_)}], {', '.join(args)})")
            self.emit(f"{self.ref(name)} = _t[0]")
            self.emit(f"if _t[0]: {', '.join(vars_)}{',' if len(vars_) == 1 else ''} = _t[1]")
            return
        e = self.parse_expr()
        self.expect("op", ";")
        self.use_var(tok, assign=True)
        if idx is None:
            self.emit(f"{self.ref(name)} = {e}")
        else:
            self.emit(f"{self.ref(name)} = R.setitem({self.ref(name)}, {idx}, {e})")

    def parse_input_spec(self):
        self.expect("op", "{")
        vars_, types = [], []
        while True:
            self.expect("op", "{")
            v = self.expect("ident")
            self.use_var(v, assign=True)
            self.expect("op", ",")
            self.expect("op", "[")
            ty = self.expect("number")
            self.expect("op", "]")
            self.expect("op", "}")
            vars_.append(v[1])
            types.append(int(ty[1]))
            if not self.accept("op", ","):
                break
        self.expect("op", "}")
        return vars_, types

    # --- variables
    def is_var(self, name):
        return (self.scope is not None and name in self.scope) or name in self.globals or name in HOME_VARS

    def ref(self, name):
        if name in HOME_VARS and not (self.scope and name in self.scope):
            return f"R.HOME[{name!r}]"
        return name

    def use_var(self, tok, assign=False):
        name = tok[1]
        if not self.is_var(name):
            self.err(f"undeclared variable {name}", tok)
        self.used.add(name)

    # --- expressions
    def parse_expr(self):
        return self.p_or()

    def p_or(self):
        left = self.p_and()
        had_and = self.last_and
        while self.peek()[0] == "kw" and self.peek()[1] == "OR":
            if had_and:
                self.err("mixing AND and OR without parentheses")
            self.nxt()
            right = self.p_and()
            if self.last_and:
                self.err("mixing AND and OR without parentheses")
            left = f"R.lor({left}, {right})"
        return left

    def p_and(self):
        self.last_and = False
        left = self.p_not()
        flag = False
        while self.peek()[0] == "kw" and self.peek()[1] == "AND":
            self.nxt()
            right = self.p_not()
            left = f"R.land({left}, {right})"
            flag = True
        self.last_and = flag
        return left

    def p_not(self):
        if self.peek()[0] == "kw" and self.peek()[1] == "NOT":
            self.nxt()
            return f"R.lnot({self.p_not()})"
        return self.p_cmp()

    def p_cmp(self):
        left = self.p_add()
        tok = self.peek()
        if tok[0] == "op" and tok[1] in ("==", "<>", "<", ">", "<=", ">="):
            self.nxt()
            right = self.p_add()
            fn = {"==": "eq", "<>": "ne", "<": "lt", ">": "gt", "<=": "le", ">=": "ge"}[tok[1]]
            left = f"R.{fn}({left}, {right})"
            nx = self.peek()
            if nx[0] == "op" and nx[1] in ("==", "<>", "<", ">", "<=", ">="):
                self.err("chained comparison")
        elif tok[0] == "op" and tok[1] == "=":
            self.err("single = used as comparison; use ==")
        return left

    def p_add(self):
        left = self.p_mul()
        while self.peek()[0] == "op" and self.peek()[1] in "+-":
            op = self.nxt()[1]
            right = self.p_mul()
            left = f"R.add({left}, {right})" if op == "+" else f"R.sub({left}, {right})"
        return left

    def p_mul(self):
        left = self.p_unary()
        while True:
            tok = self.peek()
            if tok[0] == "op" and tok[1] in "*/":
                self.nxt()
                right = self.p_unary()
                left = f"R.mul({left}, {right})" if tok[1] == "*" else f"R.div({left}, {right})"
            elif tok[0] == "kw" and tok[1] == "MOD":
                self.nxt()
                right = self.p_unary()
                left = f"R.mod({left}, {right})"
                nx = self.peek()
                if nx[0] == "op" and nx[1] in ("==", "<>", "<", ">", "<=", ">="):
                    self.err("MOD followed by a comparison: add parentheses")
            else:
                return left

    def p_unary(self):
        if self.peek()[0] == "op" and self.peek()[1] == "-":
            self.nxt()
            return f"R.neg({self.p_unary()})"
        return self.p_pow()

    def p_pow(self):
        base = self.p_postfix()
        if self.peek()[0] == "op" and self.peek()[1] == "^":
            self.nxt()
            if self.peek()[1] == "-":
                self.err("negative exponent needs parentheses")
            ex = self.p_postfix()
            if self.peek()[1] == "^":
                self.err("chained ^ needs parentheses")
            return f"R.pow({base}, {ex})"
        return base

    def p_postfix(self):
        tok = self.nxt()
        if tok[0] == "number":
            return tok[1]
        if tok[0] == "string":
            return repr(tok[1][1:-1])
        if tok[0] == "op" and tok[1] == "(":
            e = self.parse_expr()
            self.expect("op", ")")
            return f"({e})"
        if tok[0] == "op" and tok[1] == "{":
            items = []
            if not self.accept("op", "}"):
                items.append(self.parse_expr())
                while self.accept("op", ","):
                    items.append(self.parse_expr())
                self.expect("op", "}")
            return "[" + ", ".join(items) + "]"
        if tok[0] != "ident":
            self.err("expression expected", tok)
        name = tok[1]
        # special forms
        if name == "CAS":
            if self.accept("op", "."):
                meth = self.expect("ident")[1]
                self.expect("op", "(")
                a = self.parse_expr()
                self.expect("op", ")")
                if meth != "expr":
                    self.err("only CAS.expr is used", tok)
                return f"R.b_cas({a})"
            self.expect("op", "(")
            inner = self.expect("ident")
            if inner[1] != "EVAL":
                self.err("CAS(...) must wrap EVAL(text)", inner)
            self.expect("op", "(")
            a = self.parse_expr()
            self.expect("op", ")")
            self.expect("op", ")")
            return f"R.b_cas({a})"
        if name == "HVars":
            if self.accept("op", "("):
                a = self.parse_expr()
                self.expect("op", ")")
                return f"R.hvars_get({a})"
            return "R.hvars_names()"
        if self.peek()[1] == "(":
            if self.is_var(name):
                self.nxt()
                idx = self.parse_expr()
                self.expect("op", ")")
                self.use_var(tok)
                return f"R.ix({self.ref(name)}, {idx})"
            self.nxt()
            args = []
            if not self.accept("op", ")"):
                args.append(self.parse_expr())
                while self.accept("op", ","):
                    args.append(self.parse_expr())
                self.expect("op", ")")
            if name in self.funcs:
                if len(args) != self.funcs[name]:
                    self.err(f"{name} takes {self.funcs[name]} arguments, got {len(args)}", tok)
                return f"{name}({', '.join(args)})"
            if name in BUILTINS:
                self.inv_builtins.setdefault(name, set()).add(len(args))
                lo, hi = BUILTINS[name]
                if not (lo <= len(args) <= hi):
                    self.err(f"builtin {name} called with {len(args)} arguments", tok)
                if name == "EDITMAT":
                    return f"R.b_EDITMAT({args[0]!r})"
                return f"R.b_{name}({', '.join(args)})"
            self.err(f"unknown function {name} (not defined before use)", tok)
        self.use_var(tok)
        return self.ref(name)


def transpile(src):
    p = Parser(lex(src))
    py = p.parse_program()
    problems = []
    seen = {}
    for name, line in p.all_idents.items():
        if not re.fullmatch(r"[A-Za-z][A-Za-z0-9]*", name):
            problems.append(f"line {line}: identifier {name} has characters other than letters and digits")
        if name.upper() in RESERVED or name.upper() in KEYWORDS or name.upper() in BUILTINS:
            problems.append(f"line {line}: identifier {name} clashes with a reserved name")
        key = name.upper()
        if key in seen and seen[key] != name:
            problems.append(f"line {line}: identifiers {name} and {seen[key]} differ only by case")
        seen[key] = name
        if len(name) < 3 and name not in HOME_VARS:
            problems.append(f"line {line}: identifier {name} is shorter than 3 characters")
    header = "import pplrt as R\n" + "".join(f"{g} = 0\n" for g in p.globals) + "\n"
    problems.extend(p.findings)
    return header + py + "\n", p, problems


if __name__ == "__main__":
    src = open(sys.argv[1], encoding="utf-8").read()
    try:
        py, p, problems = transpile(src)
    except PPLSyntaxError as e:
        print("SYNTAX ERROR:", e)
        sys.exit(1)
    open(sys.argv[2], "w", encoding="utf-8").write(py)
    print(f"functions: {len(p.funcs)}  globals: {len(p.globals)}  lines: {src.count(chr(10))}  bytes: {len(src.encode('utf-8'))}")
    for w in p.warnings:
        print("warning:", w)
    for pr in problems:
        print("PROBLEM:", pr)
    sys.exit(1 if problems else 0)
