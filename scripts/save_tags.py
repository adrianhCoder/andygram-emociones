"""Valida y guarda las etiquetas de un chunk (JSONL por stdin).

Uso: python3 scripts/save_tags.py chunk_05 < etiquetas.jsonl
Escribe data/tags/chunk_05.jsonl solo si todo es válido.
"""
import json
import os
import re
import sys

from corpus import DATA_DIR

name = sys.argv[1]
ids = re.findall(r"^=== POST (\S+)$", open(os.path.join(DATA_DIR, "chunks", name + ".txt")).read(), re.M)
tax = json.load(open(os.path.join(DATA_DIR, "taxonomy.json")))
valid_subs = {s["id"] for e in tax["emociones"] for s in e["subs"]}

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
    if not isinstance(tags, list) or len(tags) > 3:
        errors.append(f"{pid}: 'tags' debe ser una lista de 0 a 3 elementos")
        tags = []
    for t in tags:
        if not (isinstance(t, list) and len(t) == 2 and t[0] in valid_subs and t[1] in (2, 3)):
            errors.append(f"{pid}: tag inválido {t!r} (usa [\"<id de sub-sentimiento>\", 2|3])")
    if len({t[0] for t in tags if isinstance(t, list) and t}) != len(tags):
        errors.append(f"{pid}: sub-sentimiento repetido")
    consejo = r.get("consejo")
    if not isinstance(consejo, str) or not consejo.strip():
        errors.append(f"{pid}: falta 'consejo'")
    elif len(consejo.split()) > 35:
        errors.append(f"{pid}: 'consejo' demasiado largo ({len(consejo.split())} palabras, máx. 25)")
    rows[pid] = {"id": pid, "tags": tags, "consejo": consejo}

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
print(f"OK {name}: {len(ids)} notas guardadas")
