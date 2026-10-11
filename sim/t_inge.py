import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import pplrt as R
out={}
P=program()
# Formulas: gas ideal (v), luego otra incognita; Colebrook; mis formulas
acts=[PAGE2, tile(1),
      row(2), row(1), row(2), form(101325,1,8.314462618,273.15), ESC, row(5), SAME, ESC, ESC, ESC,
      row(4), row(7), row(1), form(0.0001,100000), ESC, ESC, ESC,
      row(3), soft(5), row(4), row(2), form(10,0.5,1), soft(1), form(1.5), ESC, ESC, ESC,
      row(1), row(1), form("Energia cinetica","ec=m*v^2/2","ec:Energía [J];m:Masa [kg];v:Velocidad [m/s]"), row(3), row(1), form(2,3), ESC, row(3), form(9,2), ESC, ESC,
      row(1), form("Lente","1/f=1/a+1/b",""), row(4), row(1), form(10,15), ESC, ESC, row(2), row(1), ESC, ESC]
out['form']=run('form',acts)
print("gMias:",P.gMias, "HVARS:",R.HVARS)
# Iteracion
acts=[PAGE2, tile(2), row(1), SAME, key(12), ESC, row(1), form("x^2","2","0.000001","50"), ESC, row(1), form("ln(x-5)","1","0.000001","50"), ESC,
      row(2), SAME, ESC, row(2), form("x*exp(x)=5","1","0.0000001"), ESC, row(3), SAME, key(12), key(12), ESC, row(3), form("x^2+1","0","1","0.001"), ESC]
out['iter']=run('iter',acts)
# Unidades
acts=[PAGE2, tile(3), row(7), row(5), form(1), key(12), ESC, row(7), form(14.7), ESC, ESC, row(6), row(2), form(25), ESC, row(3), form(212), ESC, ESC,
      soft(5), row(1), row(7), form(1), ESC, ESC, soft(5), row(7), row(5), form(1), ESC, ESC, soft(5), ESC]
out['unid']=run('unid',acts)
# Constantes, interpolacion, masa molar
out['const']=run('const',[PAGE2, tile(4), key(12), key(12), key(12), key(12), ESC])
out['interp']=run('interp',[PAGE2, tile(5), row(1), form(100,419.04,120,503.71,110), ESC, row(1), form(1,2,1,5,3), row(1), form(0,0,1,1,2), ESC,
                            row(2), form(100,150,1,2,120,1.4), form(2676.2,2675.5,2776.4,2768.8), ESC, ESC])
out['masa']=run('masa',[PAGE2, tile(6), SAME, soft(1), form(10,0), ESC, soft(1), form(0,2), ESC, ESC, form("CuSO4*5H2O"), ESC, form("h2o"), form("UO2(NO3)2*6H2O"), ESC, CANCEL])
# Adimensionales, nuclear, estadistica, planilla
out['adim']=run('adim',[PAGE2, tile(7), row(1), row(1), form(1000,2,0.05,0.001), ESC, ESC, soft(5), soft(5), row(1), ESC, ESC])
out['nucl']=run('nucl',[PAGE2, tile(8), row(1), row(4), form(3.6788e19,1e20,0.001), ESC, ESC, soft(5), row(1), row(1), form(1.41e17,1,238.029), ESC, ESC, soft(5), soft(5), soft(5), ESC])
out['estad']=run('estad',[PAGE2, tile(10), row(2)])
out['plan']=run('plan',[PAGE2, tile(11)])
out['estad4']=run('estad4',[PAGE2, tile(10), row(4), row(1), row(1), SAME, ESC, ESC, ESC, ESC])
for n in out:
    ps=out[n]['shots']
    for k in range(0,len(ps),16):
        sheet(ps[k:k+16],f'build/shots/sheets/{n}{"" if k==0 else "_"+str(k//16)}.png',cols=4)
