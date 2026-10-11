#!/usr/bin/env python3
"""Auditoria de formato del archivo final, renglon por renglon."""
import os, re, sys, unicodedata
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "sim"))
import ppl2py as T
path = sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "build", "ING.txt")
raw = open(path, "rb").read()
src = raw.decode("utf-8")
lines = src.replace("\r\n", "\n").split("\n")
print(f"archivo: {path}  bytes={len(raw)}  renglones={len(lines)}")
print("BOM:", raw.startswith(b"\xef\xbb\xbf"), "| CRLF:", raw.count(b"\r\n"), "| LF sueltos:", raw.count(b"\n") - raw.count(b"\r\n"), "| CR sueltos:", raw.count(b"\r") - raw.count(b"\r\n"))
bad = []
allowed_ws = {" "}
nonascii_code, nonascii_comment, chars_in_strings = [], [], {}
for n, ln in enumerate(lines, 1):
    if "\t" in ln: bad.append((n, "tabulador"))
    if ln != ln.rstrip(): bad.append((n, "espacios al final"))
    # recorrer el renglon separando codigo, texto y comentario
    in_str = False; i = 0; code = ""; comment = ""
    while i < len(ln):
        ch = ln[i]
        if not in_str and ln.startswith("//", i):
            comment = ln[i:]; break
        if ch == '"':
            in_str = not in_str
        elif in_str:
            if ord(ch) > 126 or ord(ch) < 32:
                chars_in_strings[ch] = chars_in_strings.get(ch, 0) + 1
        else:
            code += ch
        i += 1
    if in_str: bad.append((n, "comillas sin cerrar en el renglon"))
    for ch in code:
        if ord(ch) > 126 or (ord(ch) < 32):
            nonascii_code.append((n, ch))
    for ch in comment:
        if ord(ch) > 126: nonascii_comment.append((n, ch))
    if "'" in code: bad.append((n, "apostrofo fuera de un texto"))
    if "_" in re.sub(r"\b(RECT_P|LINE_P|TEXTOUT_P)\b", "", code): bad.append((n, "guion bajo fuera de un comando"))
    if re.search(r"[“”‘’«»]", ln): bad.append((n, "comillas tipograficas"))
    if len(ln) > 400: bad.append((n, f"renglon de {len(ln)} caracteres"))
print("problemas de texto:", bad if bad else "ninguno")
print("caracteres no ASCII en codigo:", nonascii_code if nonascii_code else "ninguno")
print("caracteres no ASCII en comentarios:", len(nonascii_comment))
print("caracteres especiales dentro de textos:", " ".join(f"{c}(U+{ord(c):04X} {unicodedata.name(c,'?').split()[0].lower()})x{k}" for c, k in sorted(chars_in_strings.items())))
# analisis sintactico estricto
py, p, problems = T.transpile(src.replace("\r\n", "\n"))
print("\nfunciones:", len(p.funcs), "| variables globales del programa:", len(p.globals), "| identificadores propios:", len(p.all_idents))
print("problemas de sintaxis/nombres:", problems if problems else "ninguno")
print("instrucciones por tipo:", dict(sorted(p.inv_stmt.items(), key=lambda x: -x[1])), "total", sum(p.inv_stmt.values()))
print("comandos de la calculadora usados (nombre: cantidad de argumentos):")
for k in sorted(p.inv_builtins): print(f"   {k}: {sorted(p.inv_builtins[k])}")
ids = sorted(p.all_idents)
print("largo de nombres: min", min(map(len, ids)), "max", max(map(len, ids)), "| todo mayusculas:", [i for i in ids if i.isupper()], "| todo minusculas:", [i for i in ids if i.islower()])
# nombres reservados de la calculadora (lista de holyjoe.net/hp/PrimeVars.htm)
RES = """Θ A B C D E F G H I J K L M N O P Q R S T U V W X Y Z Base Bits Entry HAngle HComplex HDigits HFormat HSeparator Signed Date DelHVars HVars Language Notes Programs Theme Time TOff Digits epsilon AAngle AComplex ADigits AFiles AFilesB AFormat ANote AProgram AVars DelAFiles DelAVars Θmax Θmin Θstep Axes BoxAxes BoxDots BoxFrame BoxLines BoxScale BoxSides Connect Cursor Fit GridDots GridLines GridX GridY Hmax Hmin Hwidth ImageDisplay ImageName ImageOpacity ImageXmax ImageXmin ImageYmax ImageYmin KeyAxes Labels Method Nmax Nmin PixSize PoseTurn PoseXaxis PoseYaxis PoseZaxis Recenter ScrollText Surface Tmax Tmin Tstep Xmax Xmin Xtick Xzoom Ymax Ymin Ytick Yzoom Zmax Zmin Ztick Zzoom μ0 π0 σ1 σ2 Alpha AngleA AngleB AngleC Cell CellName Col ColWidth Conf ExpList LSolution LSystem Mean1 Mean2 n1 n2 NumIndep NumStart NumStep NumType NumXStart NumXStep NumXZoom NumYStart NumYStep NumYZoom NumZoom ObsList ObsMat Pooled ProbList Row RowHeight s1 s2 SideA SideB SideC TriType x1 x2 Xlist Xval Ylist AltHyp DataType FinType InfType σCov ΣX σX ΣX2 ΣXY ΣY σY ΣY2 CoefDet coefDet Corr corr ContribList ContribMat CritScore CritVal1 CritVal2 DF DFerr ExpMat Extremum Fval Inter Isect MaxVal MeanX MeanY MedVal MinVal MS MSerr NbItem Prob Q1 Q3 Result Root serrInter serrLine serrSlope serrX serrY SignedArea Slope SS SSerr ssX ssY sCov sX sY TestScore TestValue Yval Accrued Bond360 CallPrice CpnPer MatDate PriceBond SemiAnnual SetDate YieldBond BEG CPYR FV GSize IPYR NbPmt PMT PPYR PV BSCall BSPut Dividend RiskFree StockPrice StrikePrice TimeMarket Volatility CFData CFPYR FMRR InvestInt IRR MIRR NFV NPV NUS Payback SafeInt TotalCF CostAsset FactorDepr FirstAsset LifeAsset SalvageAsset Date360 DateDiff DateOne DateTwo EffInt IntCPYR NomInt FixedCost Profit Quantity SalePrice VariableCost Change Cost Margin Markup NewValue OldValue Price Total""".split()
for pre in "GLMZCDEFRSUVXY":
    RES += [f"{pre}{k}" for k in range(10)]
RES += [f"FZ{k}" for k in range(10)] + [f"z{k}" for k in range(10)] + [f"H{k}" for k in range(1, 6)] + [f"I{k}" for k in range(1, 5)]
exact = sorted(set(ids) & set(RES))
ci = sorted(i for i in ids if i.upper() in {r.upper() for r in RES} and i not in RES)
print("nombres propios iguales a una variable del sistema:", exact if exact else "ninguno")
print("nombres propios que solo difieren en mayusculas/minusculas de una variable del sistema:", ci if ci else "ninguno")
os.makedirs(os.path.join(ROOT, "build"), exist_ok=True)
open(os.path.join(ROOT, "build", "idents.txt"), "w").write("\n".join(ids))
