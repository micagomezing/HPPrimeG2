import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import pplrt as R
out={}
# Graficos: cartesiano con zoom, lectura y rango; polar; superficie; apps
acts=[tile(1), row(1), SAME, ("tap",200,100), soft(1), soft(2), soft(2), soft(3), form(-2,2,-1,3), ("tap",100,90), ESC,
      row(1), form("TAN(X)","-5","5"), ESC, row(1), form("1/x","-5","5"), ESC, row(1), form("sqrt(x)*ln(x)","-2","6"), ESC,
      row(2), SAME, ("tap",200,80), soft(1), soft(3), form(0,3.14159), ESC,
      row(2), form("2*sin(3*t)","0","2*pi"), ESC,
      row(3), SAME, soft(2), soft(2), ESC, row(3), form("x^2-y^2","-2","2","-2","2"), ESC,
      row(1), form("a*x","0","1"), row(1), form("sin(x)","5","1"), row(4)]
out['graf']=run('graf',acts)
# EDO numerica
out['rk4']=run('rk4',[tile(7), row(3), SAME, soft(1), ESC, ESC, row(3), form("y","0","1","1","50"), ESC, row(3), form("1/(x-1)","0","1","2","20"), ESC])
# Ecuacion numerica
out['ecnum']=run('ecnum',[tile(5), row(2), SAME, ESC, row(2), form("x^3-2*x-5","x","2"), ESC, row(2), form("T*LN(T)=100","T","10"), ESC, row(2), form("x^2+1=0","x","1"), ESC])
# Probabilidad
acts=[tile(10)]
for d in range(1,8):
    acts += [row(d), row(1), SAME, ESC, row(2), SAME, ESC, row(3), SAME, ESC, row(4), SAME, ESC]
    if d==7: acts += [row(5), SAME, ESC]
    acts += [ESC]
acts += [soft(5)]
for d in range(1,4):
    acts += [row(d), row(1), SAME, ESC, row(2), SAME, ESC, row(3), SAME, ESC, row(4), SAME, ESC, row(5), SAME, ESC, ESC, soft(5)]
out['proba']=run('proba',acts)
# Coordenadas
acts=[tile(11), row(1), SAME, ESC, row(1), form(-3,-4), ESC, row(2), SAME, ESC, row(2), form(2,3.14159265358979,2), ESC, row(3), SAME, ESC, row(4), SAME, ESC, row(5), SAME, ESC, row(6), SAME, ESC, row(7), SAME, ESC, ESC]
out['coord']=run('coord',acts)
out['coord_deg']=run('coord_deg',[tile(11), row(1), form(1,1), ESC, row(2), SAME, ESC, row(5), SAME, ESC, row(6), SAME, ESC, ESC], angle='deg')
# Matrices
R.HOME['M1']=[[2,1],[1,3]]; R.HOME['M2']=[[1],[2]]
acts=[tile(9), row(1), row(2), row(3), ESC, row(4), row(5), row(6), ESC, row(7), soft(5), row(1), row(2), row(3), SAME, row(4), SAME, row(5), row(6), row(7), soft(4), row(3), ESC, ESC]
out['matr']=run('matr',acts,keep_home=True)
print("M3 =",R.HOME['M3'])
for n in out:
    import glob
    ps=out[n]['shots']
    sheet(ps[:16],f'build/shots/sheets/{n}.png',cols=4)
    if len(ps)>16: sheet(ps[16:32],f'build/shots/sheets/{n}_b.png',cols=4)
    if len(ps)>32: sheet(ps[32:48],f'build/shots/sheets/{n}_c.png',cols=4)
    if len(ps)>48: sheet(ps[48:64],f'build/shots/sheets/{n}_d.png',cols=4)
