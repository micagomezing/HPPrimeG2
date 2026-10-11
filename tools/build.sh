#!/bin/bash
# Une src/p*.ppl en un solo programa, corta renglones largos, lo verifica con
# el analizador estricto y genera la copia de entrega (UTF-8 sin BOM, CRLF).
#
#   tools/build.sh          -> build/ING.txt (LF, para las pruebas)
#                              sim/ing_py.py (traduccion a Python, generada)
#                              dist/ING_v<VERSION>.txt (para la calculadora)
set -e
cd "$(dirname "$0")/.."
VER=$(cat VERSION)
mkdir -p build dist
cat src/p1_base.ppl src/p2_graf.ppl src/p3_mate.ppl src/p4_mat_prob.ppl \
    src/p5_inge.ppl src/p6_datos.ppl src/p7_formulas.ppl src/p8_main.ppl > build/ing_raw.txt
python3 tools/wrap.py build/ing_raw.txt build/ING.txt
python3 sim/ppl2py.py build/ING.txt sim/ing_py.py
python3 - "$VER" <<'PY'
import sys
src = open("build/ING.txt", encoding="utf-8").read().rstrip("\n") + "\n"
out = f"dist/ING_v{sys.argv[1]}.txt"
open(out, "w", encoding="utf-8", newline="").write(src.replace("\n", "\r\n"))
print("entrega:", out, len(src.splitlines()), "renglones")
PY
