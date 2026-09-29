"""Valida y guarda las etiquetas de un chunk (JSONL por stdin).

Uso: python3 scripts/save_tags.py chunk_05 [--lote] < etiquetas.jsonl
Escribe data/tags/chunk_05.jsonl solo si todo es válido. Si una línea no trae consejo,
se conserva el que la nota ya tenía. Cada fila guarda la versión de la taxonomía ("v").

Con --lote se pueden mandar las notas por partes: cada lote se valida y se acumula en
data/tags/.lotes/; cuando ya están todas las notas del chunk, se escribe el archivo final.
"""
import glob
import json
import os
import re
import sys

from corpus import DATA_DIR

MAX_TAGS = 4

name = sys.argv[1]
lote = "--lote" in sys.argv[2:]
staging = os.path.join(DATA_DIR, "tags", ".lotes", name + ".jsonl")
ids = re.findall(r"^=== POST (\S+)$", open(os.path.join(DATA_DIR, "chunks", name + ".txt")).read(), re.M)
tax = json.load(open(os.path.join(DATA_DIR, "taxonomy.json")))
valid_subs = {s["id"] for e in tax["emociones"] for s in e["subs"]}
previos = {}
for path in glob.glob(os.path.join(DATA_DIR, "tags", "*.jsonl")):
    for line in open(path):
        r = json.loads(line)
        if r.get("consejo"):
            previos[r["id"]] = r["consejo"]

errors, rows = [], {}
for n, line in enumerate(sys.stdin, 1):
    line = line.strip()
    if not line:
        continue
    try:
        r = json.loads(line)
    except json.JSONDecodeError as e:
        errors.append(f"línea {n}: JSON inválido ({e})")
        continue
    pid = r.get("id")
    if pid not in ids:
        errors.append(f"línea {n}: id desconocido en este chunk: {pid!r}")
        continue
    if pid in rows:
        errors.append(f"línea {n}: id repetido: {pid}")
    tags = r.get("tags")
    if not isinstance(tags, list) or len(tags) > MAX_TAGS:
        errors.append(f"{pid}: 'tags' debe ser una lista de 0 a {MAX_TAGS} elementos")
        tags = []
    for t in tags:
        if not (isinstance(t, list) and len(t) == 2 and t[0] in valid_subs and t[1] in (2, 3)):
            errors.append(f"{pid}: tag inválido {t!r} (usa [\"<id de sub-sentimiento>\", 2|3])")
    if len({t[0] for t in tags if isinstance(t, list) and t}) != len(tags):
        errors.append(f"{pid}: sub-sentimiento repetido")
    consejo = r.get("consejo") or previos.get(pid)
    if not isinstance(consejo, str) or not consejo.strip():
        errors.append(f"{pid}: falta 'consejo' (la nota no tenía uno)")
    elif len(consejo.split()) > 35:
        errors.append(f"{pid}: 'consejo' demasiado largo ({len(consejo.split())} palabras, máx. 25)")
    rows[pid] = {"id": pid, "tags": tags, "consejo": consejo, "v": tax["version"]}

if lote and errors:
    print(f"ERROR {name}: este lote no se guardó.\n" + "\n".join(errors))
    sys.exit(1)
if lote:
    acumulado = {}
    if os.path.exists(staging):
        acumulado = {r["id"]: r for r in map(json.loads, open(staging))}
    acumulado.update(rows)
    faltan = [i for i in ids if i not in acumulado]
    if faltan:
        os.makedirs(os.path.dirname(staging), exist_ok=True)
        with open(staging, "w") as f:
            for pid in ids:
                if pid in acumulado:
                    f.write(json.dumps(acumulado[pid], ensure_ascii=False) + "\n")
        print(f"Lote OK {name}: {len(rows)} notas en este lote, {len(acumulado)}/{len(ids)} en total. "
              f"Faltan {len(faltan)}, empezando por: " + ", ".join(faltan[:5]))
        sys.exit(0)
    rows = acumulado

missing = [i for i in ids if i not in rows]
if missing:
    errors.append(f"faltan {len(missing)} notas: " + ", ".join(missing[:10]) + (" ..." if len(missing) > 10 else ""))
if errors:
    print(f"ERROR {name}: no se guardó nada.\n" + "\n".join(errors))
    sys.exit(1)

os.makedirs(os.path.join(DATA_DIR, "tags"), exist_ok=True)
with open(os.path.join(DATA_DIR, "tags", name + ".jsonl"), "w") as f:
    for pid in ids:
        f.write(json.dumps(rows[pid], ensure_ascii=False) + "\n")
if os.path.exists(staging):
    os.remove(staging)
print(f"OK {name}: {len(ids)} notas guardadas")
