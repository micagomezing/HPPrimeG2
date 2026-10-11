#!/usr/bin/env python3
"""Corta los renglones largos del programa despues de una coma que este
fuera de un texto entre comillas. No cambia el significado."""
import sys
LIMIT, MIN_CHUNK = 110, 70
out = []
for line in open(sys.argv[1], encoding="utf-8").read().split("\n"):
    if len(line) <= LIMIT or line.lstrip().startswith("//"):
        out.append(line)
        continue
    indent = line[:len(line) - len(line.lstrip())] + "    "
    cur, in_str, first = "", False, True
    for ch in line:
        cur += ch
        if ch == '"':
            in_str = not in_str
        elif ch == "," and not in_str and len(cur) >= MIN_CHUNK:
            out.append(cur if first else indent + cur.lstrip())
            cur, first = "", False
    if cur.strip():
        out.append(cur if first else indent + cur.lstrip())
open(sys.argv[2], "w", encoding="utf-8").write("\n".join(out))
