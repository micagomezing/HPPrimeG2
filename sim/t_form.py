import sys, math, random; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import pplrt as R
P=program(); P.IngIni()
random.seed(7)
LET=["A","B","C","D","F","G","H","J","K","L","M","N"]
def solve(ecu, var, vals, unk, seed=1.0):
    dst=[]; k=0
    for v in var:
        if v==unk: dst.append("X")
        else:
            P.FmPon(k+1, vals[v]); dst.append(LET[k]); k+=1
    R.LOG.clear()
    assert P.ExPrep(ecu,var,dst)==1, (ecu, R.LOG)
    xs=P.ExRaices(seed)
    return (xs[0] if xs else None)
cats=P.FmCats(); tot=0; bad=[]; nform=0
names=set()
for c in range(2,len(cats)+1):
    regs=P.FmDatos(c)
    for reg in regs:
        nform+=1
        parts=reg.split("|"); assert len(parts)==3, reg
        nom,ecu,des=parts
        assert len(nom)<=52, ("nombre largo", nom, len(nom))
        assert (c,nom) not in names; names.add((c,nom))
        var=P.ExVars(ecu)
        dnames=[]
        for d in des.split(";"):
            dd=d.split(":"); assert len(dd)==2, ("descripcion",nom,d)
            dnames.append(dd[0]); assert len(dd[1])>0
        assert sorted(dnames)==sorted(var), ("variables", nom, var, dnames)
        assert len(var)<=13 and ecu.count("=")==1
        # ida y vuelta
        for unk in var:
            ok=False; tries=0
            for attempt in range(12):
                vals={}
                for v in var:
                    lo,hi=0.5,5.0
                    if v in ("x","eta","eps","z","xd","xb","xf","xw","y","zf","ye","xe","x1","beta","pe","pf","pt","f","os","dr","rr","cd","xw"): lo,hi=0.05,0.95
                    vals[v]=random.uniform(lo,hi)
                first=var[0] if var[0]!=unk else var[-1]
                # hace consistente el juego de valores resolviendo una variable
                s0=solve(ecu,var,vals,first)
                if s0 is None or abs(s0)<1e-9 or abs(s0)>1e9: continue
                vals[first]=s0
                tries+=1
                true=vals[unk]
                got=solve(ecu,var,vals,unk,1.0)
                if got is not None and abs(got-true)<=1e-6*max(1,abs(true)):
                    ok=True; break
                # con una estimacion cercana (boton "Otra")
                got2=solve(ecu,var,vals,unk,true*1.2)
                if got2 is not None and abs(got2-true)<=1e-6*max(1,abs(true)):
                    ok="seed"; break
            tot+=1
            if ok is not True:
                bad.append((cats[c-1],nom,unk,ok,tries, got))
print("fórmulas:",nform," combinaciones probadas:",tot," sin resolver directo:",len(bad))
for b in bad: print("  ",b)
