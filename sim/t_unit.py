import sys, math, random; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import pplrt as R
from scipy import stats
P=program(); P.IngIni()
fails=0
def check(name, got, exp, tol=1e-6):
    global fails
    ok = abs(got-exp) <= tol*max(1,abs(exp))
    if not ok:
        fails+=1; print("FAIL",name,got,exp)
# ---- 1. distribuciones
cases=[(1,[2,3],[ -1,2,5.5], stats.norm(2,3)),(2,[7],[-2,0,1.3],stats.t(7)),(3,[5],[0.5,4,11],stats.chi2(5)),
       (4,[5,10],[0.3,1,3.2],stats.f(5,10)),(5,[0.7],[0.2,1,4],stats.expon(scale=1/0.7)),(6,[2,5],[2.5,4,6],stats.uniform(2,3)),
       (7,[12,0.3],[0,3,7,12],stats.binom(12,0.3)),(8,[4.2],[0,3,9],stats.poisson(4.2)),(9,[0.3],[1,2,6],stats.geom(0.3)),
       (10,[50,10,5],[0,1,3],stats.hypergeom(50,10,5))]
for d,par,xs,ref in cases:
    for x in xs:
        R.__dict__  # noqa
        P.gBad=0
        pdf = ref.pmf(x) if d>=7 else ref.pdf(x)
        check(f"pdf d{d} x{x}", P.PrPdf(d,par,x), pdf)
        check(f"cdf d{d} x{x}", P.PrCdf(d,par,x), ref.cdf(x))
    for p in (0.05,0.5,0.975):
        check(f"icdf d{d} p{p}", P.PrIcdf(d,par,p), ref.ppf(p), 1e-6)
    m=P.PrMom(d,par)
    check(f"mean d{d}", m[0], ref.mean()); check(f"var d{d}", m[1], ref.var())
    assert P.gBad==0
print("distribuciones: ok" if fails==0 else f"distribuciones: {fails} fallas")
# ---- 2. motor de expresiones
tests=[("x^2*SIN(X)",{"x":1.3},lambda x:x**2*math.sin(x)),("sqrt(x+1)/sqrt(x)",{"x":3},lambda x:math.sqrt(x+1)/math.sqrt(x)),
       ("2x+3(x+1)",{"x":2},lambda x:2*x+3*(x+1)),("1.5e-3*x",{"x":2},lambda x:0.003),("6.02E23/x",{"x":2},lambda x:3.01e23),
       ("LOG(x)+ln(x)+log10(x)",{"x":100},lambda x:2+math.log(100)+2),("e^x+pi",{"x":1},lambda x:math.e+math.pi),
       ("EXP(-x)*ABS(-3)",{"x":0},lambda x:3),("sqrt(sqrt(x)+sqrt(x))",{"x":4},lambda x:2),("x(x+1)",{"x":3},lambda x:12),
       ("−x+π",{"x":1},lambda x:math.pi-1)]
for s,vals,fn in tests:
    c=P.ExComp(s,["x"],["X"],0)
    assert P.gBad==0,(s,P.gErr)
    R.HOME['X']=vals['x']
    v=R.b_EXPR(c)
    check("expr "+s, v, fn(vals['x']))
c=P.ExComp("a*x",["x"],["X"],0); assert P.gBad==1 and P.gErr=="a"
print("ExVars:",P.ExVars("p1/(rho*g)+V1^2/(2*g)+z1=sqrt(hf)*pi*e*exp(k)"))
print("CAS  :",P.ExCasT("X^2*SIN(2X)+LOG(X)+LN(X)-1.5e-3"), "|", P.ExCasT("y''+3*y'=e^(-x)"))
print("Valor:",P.ExValor("2*pi"),P.ExValor("1.5e-3"),P.ExValor("-3"),P.ExValor(""),P.gBad)
# ---- 3. formato de numeros y cortes
for v in (0,5,-2.5,1234567.891,0.000123456789,1.66053906892e-27,6.02214076e23,-9.99999e-5,123456789012,1/3,99999.99999,0.1+0.2):
    print("  UiNum",repr(v),"->",P.UiNum(v,8),"|",P.UiNum(v,4))
print(P.UiCortar("simplify(diff(x^2*sin(x),x))+cos(x)*x^2+2*x*sin(x)-1234567*exp(x)",30))
print(P.UiPartir("a|b||c","|"), P.UiPartir("abc","|"), P.UiPartir("abc|","|"), P.UiComas("x*y, atan2(y,x), [1,2]"))
# ---- 4. masa molar
ref={"H2O":18.015,"Ca(OH)2":74.092,"H2SO4":98.072,"CuSO4*5H2O":249.677,"C6H12O6":180.156,"Al2(SO4)3":342.132,"D2O":20.027,"UO2":270.027,"K4[Fe(CN)6]":368.346,"Co":58.933,"CO":28.010,"NaCl":58.44,"UF6":352.017}
for f,m in ref.items():
    res=P.QmParse(f); assert P.gBad==0,(f,P.gErr)
    tot=sum(c*P.QmMasas()[e-1] for e,c in zip(res[0],res[1]))
    check("masa "+f, tot, m, 2e-4)
for bad in ("h2o","Xx2","Ca(OH","CaOH)2",""):
    P.QmParse(bad); print("  fórmula inválida",repr(bad),"->",P.gBad,P.gErr)
assert len(P.QmSimbolos())==len(P.QmMasas())
print("total fallas:",fails)
