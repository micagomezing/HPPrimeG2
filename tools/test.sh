#!/bin/bash
# Reconstruye y corre todas las pruebas en el simulador.
#   tools/test.sh [cantidad de corridas al azar, por defecto 60]
set -e
cd "$(dirname "$0")/.."
tools/build.sh
python3 tools/audit.py dist/ING_v$(cat VERSION).txt > build/audit.txt
grep -E "problemas|no ASCII en codigo|iguales a una variable" build/audit.txt
for t in t_math t_num t_unit t_form t_form2 t_inge; do
  echo "### $t"
  python3 sim/$t.py > build/$t.log 2>&1 || { echo "FALLO $t (ver build/$t.log)"; tail -20 build/$t.log; exit 1; }
  grep -ciE "traceback|FALLO|FAIL" build/$t.log || true
done
echo "### t_monkey"
python3 sim/t_monkey.py ${1:-60} | head -3
