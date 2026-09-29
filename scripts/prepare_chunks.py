"""Parte el corpus en chunks de texto para los subagentes que etiquetan.

Genera data/chunks/chunk_NN.txt (hasta ~45 KB c/u, en orden cronológico),
data/chunks/pilot.txt (50 notas al azar, semilla fija),
data/chunks/pendientes_AAAAMMDD.txt (notas nuevas que aún no tienen etiquetas) y
data/chunks/INSTRUCCIONES.md (reglas + taxonomía).
"""
import glob
import json
import os
import random
from datetime import date

from corpus import DATA_DIR, load_posts

MAX_CHARS = 45_000  # ~11k tokens: cabe en una sola lectura del subagente
OUT = os.path.join(DATA_DIR, "chunks")


def render(p):
    return f"=== POST {p['id']}\nTITLE: {p['title']}\nDATE: {p['date']}\n" + "\n".join(p["paragraphs"]) + "\n\n"


def render_taxonomy(tax):
    out = []
    for e in tax["emociones"]:
        out.append(f"### {e['nombre'].upper()}: {e['descripcion']}")
        for s in e["subs"]:
            out.append(f"- `{s['id']}` ({s['nombre']}): {s['descripcion']} Pistas: {s['pistas']}.")
        out.append("")
    return "\n".join(out)


if __name__ == "__main__":
    posts = load_posts()
    os.makedirs(OUT, exist_ok=True)
    for old in os.listdir(OUT):
        if old.startswith("chunk_"):
            os.remove(os.path.join(OUT, old))
    chunks, cur = [], ""
    for p in posts:
        text = render(p)
        if cur and len(cur) + len(text) > MAX_CHARS:
            chunks.append(cur)
            cur = ""
        cur += text
    chunks.append(cur)
    for n, text in enumerate(chunks, 1):
        with open(os.path.join(OUT, f"chunk_{n:02d}.txt"), "w") as f:
            f.write(text)
    pilot = sorted(random.Random(7).sample(posts, 50), key=lambda p: p["id"])
    with open(os.path.join(OUT, "pilot.txt"), "w") as f:
        f.write("".join(map(render, pilot)))
    tagged = set()
    for path in glob.glob(os.path.join(DATA_DIR, "tags", "chunk_*.jsonl")) + glob.glob(os.path.join(DATA_DIR, "tags", "pendientes_*.jsonl")):
        tagged.update(json.loads(line)["id"] for line in open(path))
    pending = [p for p in posts if p["id"] not in tagged]
    if tagged and pending:
        name = f"pendientes_{date.today():%Y%m%d}"
        with open(os.path.join(OUT, name + ".txt"), "w") as f:
            f.write("".join(map(render, pending)))
        print(f"{len(pending)} notas sin etiquetar -> data/chunks/{name}.txt")
    tax = json.load(open(os.path.join(DATA_DIR, "taxonomy.json")))
    template = open(os.path.join(DATA_DIR, "instrucciones_etiquetado.md")).read()
    with open(os.path.join(OUT, "INSTRUCCIONES.md"), "w") as f:
        f.write(template.replace("{{TAXONOMIA}}", render_taxonomy(tax)))
    print(f"{len(posts)} notas -> {len(chunks)} chunks + pilot")
