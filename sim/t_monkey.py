import sys, random, traceback; import os; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from harness import *
import pplrt as R
P=program(); P.gDepura=1
import time, signal
class Hang(Exception): pass
def _alarm(*a): raise Hang()
signal.signal(signal.SIGALRM,_alarm)
t0=time.time(); runs=int(sys.argv[1]) if len(sys.argv)>1 else 300
errs={}; ok=0; msgs={}
for seed in (list(range(30000,30000+runs)) if len(sys.argv)<3 else [int(v) for v in sys.argv[2].split(',')]):
    R.reset([], angle=("deg" if seed%5==0 else "rad"), shot_dir=None)
    R.MONKEY=random.Random(seed); R.MONKEY_STEPS=0; R.MONKEY_LIMIT=350; R.TRACE.clear()
    for c in "ABCDEFGHIJKLMNOPQRSTUVWXYZ": R.HOME[c]=0
    R.HOME['M1']=[[2,1],[1,3]] if seed%2 else [[1,2,3],[4,5,6]]
    R.HOME['M2']=[[1],[2]]
    signal.alarm(20)
    try:
        P.ING(); ok+=1
    except R.EndOfScript:
        ok+=1
    except Exception as e:
        tb=traceback.extract_tb(e.__traceback__)
        fr=[f for f in tb if 'ing_py' in f.filename]
        key=(type(e).__name__, str(e)[:110], fr[-1].name if fr else '?')
        errs.setdefault(key,[]).append((seed, list(R.TRACE[-6:])))
    signal.alarm(0)
    for it in R.LOG:
        if it[0]=="MSGBOX": msgs[it[1][:60]]=msgs.get(it[1][:60],0)+1
R.MONKEY=None
print(f"corridas: {runs}  sin error: {ok}  tipos de error: {len(errs)}  ({time.time()-t0:.0f}s)")
for k,v in errs.items():
    print("ERROR",k,"x",len(v)); print("    seed",v[0][0],"ultimos:",v[0][1])
print("mensajes al usuario vistos:",len(msgs))
for m,c in sorted(msgs.items(), key=lambda x:-x[1])[:60]: print(f"  {c:4d}  {m}")
