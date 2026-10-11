import sys; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
out={}
# Derivadas: todas las opciones con valores por defecto
acts=[tile(2)]
for k in range(1,7):
    acts += [row(k), SAME, ESC]
acts += [row(1), form("X^2*SIN(X)","X","X=2"), ESC, ESC]
out['deriv']=run('deriv',acts)
# Integrales
acts=[tile(3), row(1), SAME, ESC, row(2), SAME, ESC, row(3), SAME, ESC, row(4), SAME, SAME, ESC, row(5), SAME, ESC, ESC]
out['integ']=run('integ',acts)
# Limites
acts=[tile(4), row(1), SAME, ESC, row(1), form("(1+1/x)^x","x","inf"), ESC, row(2), SAME, key(12), ESC, ESC]
out['limit']=run('limit',acts)
# Ecuaciones
acts=[tile(5), row(1), SAME, ESC, row(3), SAME, ESC, row(4), SAME, ESC, row(5), SAME, ESC, row(2), SAME, ESC, ESC]
out['ecuac']=run('ecuac',acts)
# Polinomios
out['poli']=run('poli',[tile(6), SAME, ESC, tile(6), form("1,-6,11,-6"), ESC])
# EDO
acts=[tile(7), row(1), SAME, ESC, row(2), SAME, ESC, row(1), form("d2y+4*dy+3*y=0","y","x"), ESC, row(3), SAME, soft(1), ESC, ESC, ESC]
out['edo']=run('edo',acts)
# Laplace
out['lapl']=run('lapl',[tile(8), row(1), SAME, ESC, row(2), SAME, ESC, row(3), SAME, ESC, ESC])
# Campos
acts=[tile(12)]
for k in (1,4,5): acts += [row(k), SAME, ESC]
for k in (2,3): acts += [row(k), SAME, ESC]
acts += [row(6), SAME, ESC, ESC]
out['campos']=run('campos',acts)
# Algebra (pagina 2)
acts=[PAGE2, tile(9)]
for k in range(1,5): acts += [row(k), SAME, ESC]
out['algebra']=run('algebra',acts+[ESC])
print()
for name,r in out.items():
    print("----",name)
    for c in r['cas']:
        print("   ", c)
