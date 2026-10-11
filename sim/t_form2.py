import sys, math; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import pplrt as R
P=program(); P.IngIni()
LET=["A","B","C","D","F","G","H","J","K","L","M","N"]
def find(nom):
    for c in range(2,11):
        for reg in P.FmDatos(c):
            if reg.split("|")[0]==nom: return reg
    raise KeyError(nom)
def calc(nom, unk, seed=None, **vals):
    reg=find(nom); _,ecu,des=reg.split("|")
    var=P.ExVars(ecu); desc=dict(d.split(":") for d in des.split(";"))
    dst=[]; k=0
    for v in var:
        if v==unk: dst.append("X")
        else: P.FmPon(k+1, vals[v]); dst.append(LET[k]); k+=1
    assert P.ExPrep(ecu,var,dst)==1
    if seed is None:
        seed=1
        d=desc[unk]
        if "de 0 a 1" in d or "menor que 1" in d or "Fracción" in d: seed=0.5
        if "[K]" in d: seed=300
        if "Reynolds" in d: seed=10000
    n0=len(R.EXPR_LOG)
    xs=P.ExRaices(seed)
    return (xs[0] if xs else None), len(R.EXPR_LOG)-n0, xs[1:]
CASES=[("Gas ideal","v",0.0224140,dict(p=101325,n=1,r=8.314462618,t=273.15)),
   ("Gas ideal","t",273.15,dict(p=101325,n=1,r=8.314462618,v=0.022413969545)),
   ("Van der Waals","v",0.0023873,dict(p=1e6,a=0.3640,n=1,b=4.267e-5,r=8.314462618,t=300)),
   ("Van der Waals","p",None,dict(v=0.0024,a=0.3640,n=1,b=4.267e-5,r=8.314462618,t=300)),
   ("Van der Waals","n",None,dict(v=0.0024,a=0.3640,p=1e6,b=4.267e-5,r=8.314462618,t=300)),
   ("Colebrook","f",0.0185138661,dict(rr=0.0001,re=1e5)),
   ("Swamee-Jain","f",0.0184524453,dict(rr=0.0001,re=1e5)),
   ("Swamee-Jain","re",1e5,dict(rr=0.0001,f=0.01845244530756638)),
   ("Arrhenius","t",369.7618,dict(k=0.05,a=1e10,ea=80000,r=8.314462618)),
   ("Arrhenius","ea",None,dict(k=0.05,a=1e10,t=350,r=8.314462618)),
   ("Clausius-Clapeyron","t2",None,dict(p2=2,p1=1,dh=40660,r=8.314462618,t1=373.15)),
   ("Antoine (logaritmo en base 10)","p",760.086,dict(a=8.07131,b=1730.63,c=233.426,t=100)),
   ("Antoine (logaritmo en base 10)","t",100.0,dict(a=8.07131,b=1730.63,c=233.426,p=760.0863691649307)),
   ("CSTR, orden 2","x",0.6417424,dict(tau=10,k=0.5,c0=1)),
   ("CSTR, orden 1","x",5/6,dict(tau=10,k=0.5)),
   ("PFR, orden 1","x",1-math.exp(-5),dict(tau=10,k=0.5)),
   ("Radiación de una superficie a su entorno","q",0.8*5.670374e-8*2*(400**4-300**4),dict(eps=0.8,a=2,t1=400,t2=300)),
   ("Radiación de una superficie a su entorno","t1",400.0,dict(eps=0.8,a=2,q=0.8*5.670374e-8*2*(400**4-300**4),t2=300)),
   ("Diferencia media logarítmica","dtml",(60-20)/math.log(3),dict(dt1=60,dt2=20)),
   ("Diferencia media logarítmica","dt1",60.0,dict(dtml=(60-20)/math.log(3),dt2=20)),
   ("Decaimiento radiactivo","n",1e20*math.exp(-1),dict(n0=1e20,lam=1e-3,t=1000)),
   ("Decaimiento radiactivo","t",1000.0,dict(n0=1e20,lam=1e-3,n=1e20*math.exp(-1))),
   ("Decaimiento radiactivo","lam",1e-3,dict(n0=1e20,t=1000,n=1e20*math.exp(-1))),
   ("Actividad en el tiempo","t",math.log(1.245)/1.5e-10,dict(a=100,a0=124.5,lam=1.5e-10)),
   ("Actividad en el tiempo","t",math.log(1.245)/1.5e-17,dict(a=100,a0=124.5,lam=1.5e-17)),
   ("Núcleos en una masa","n",6.02214076e23/238.029,dict(m=1,mm=238.029)),
   ("Núcleos en una masa","m",1.0,dict(n=6.02214076e23/238.029,mm=238.029)),
   ("Actividad de una masa","a",math.log(2)/1.41e17*6.02214076e23/238.029,dict(th=1.41e17,m=1,mm=238.029)),
   ("Actividad de una masa","th",1.41e17,dict(a=math.log(2)/1.41e17*6.02214076e23/238.029,m=1,mm=238.029)),
   ("Densidad atómica","nd",19.05*6.02214076e23/238.029,dict(rho=19.05,mm=238.029)),
   ("Atenuación en un blindaje","x",math.log(10)/0.5,dict(phi=10,phi0=100,mu=0.5)),
   ("Actividad con la vida media","t",10.54,dict(a=25,a0=100,th=5.27)),
   ("Energía de enlace","be",(26*1.007825+30*1.008665-55.934936)*931.494,dict(z=26,a=56,m=55.934936)),
   ("Período estable del reactor","rho",0.0065/(1+60*0.08),dict(tp=60,beta=0.0065,lam=0.08)),
   ("k efectivo con un grupo de energía","bg2",0.2/3.5,dict(keff=1,kinf=1.2,l2=3.5)),
   ("Buckling de un cilindro","r",2.405/math.sqrt(0.01-(math.pi/100)**2),dict(bg2=0.01,h=100)),
   ("Bernoulli con pérdidas","v2",None,dict(p1=200000,rho=1000,g=9.80665,v1=1,z1=0,p2=150000,z2=2,hf=1)),
   ("Fenske (etapas mínimas)","nmin",None,dict(xd=0.95,xb=0.05,alfa=2.5)),
   ("Fenske (etapas mínimas)","xd",0.95,dict(nmin=math.log((0.95/0.05)*(0.95/0.05))/math.log(2.5),xb=0.05,alfa=2.5)),
   ("Destilación diferencial (Rayleigh)","xw",None,dict(f=100,w=40,alfa=2.5,xf=0.5)),
   ("Ácido débil","h",(-1.8e-5+math.sqrt(1.8e-5**2+4*1.8e-5*0.1))/2,dict(ka=1.8e-5,c=0.1)),
   ("Ecuación de Nernst","pot",None,dict(pot0=1.10,r=8.314462618,t=298.15,n=2,f=96485.33212,q=10)),
   ("Sobrepaso (segundo orden)","z",0.4559498,dict(os=0.2)),
   ("Tiempo de pico","z",math.sqrt(1-(math.pi/4)**2),dict(tp=2,wn=2)),
   ("Dittus-Boelter","re",None,dict(nu=200,pr=5,n=0.4)),
   ("Placa orificio","dp",None,dict(q=0.01,cd=0.61,a=0.002,rho=1000,beta=0.5)),
   ("Enfriamiento de un cuerpo (sistema concentrado)","tt",None,dict(t=50,tinf=20,t0=100,h=25,a=0.05,rho=7800,v=0.0005,cp=470)),
   ("Grashof","gr",None,dict(g=9.80665,beta=0.0033,ts=60,tf=20,l=0.5,vis=1.6e-5)),
   ("Reactividad","k",None,dict(rho=0.005)),
   ("Eficiencia de Carnot","tc",None,dict(eta=0.4,tf=300)),
  ]
bad=0; mx=0
for nom,unk,exp,vals in CASES:
    x,ne,otras=calc(nom,unk,**vals)
    mx=max(mx,ne)
    flag=""
    if x is None: flag="  <-- SIN SOLUCION"; bad+=1
    elif exp is not None and abs(x-exp)>2e-5*abs(exp): flag=f"  <-- esperado {exp}"; bad+=1
    print(f"{nom[:34]:34s} {unk:5s}= {x!s:22s} ev={ne:4d} otras={[float('%.5g'%o) for o in otras]}{flag}")
print("problemas:",bad," máx. evaluaciones:",mx)
