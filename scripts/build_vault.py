"""Genera un vault de Obsidian (vault/) con las notas enlazadas a sus emociones.

- Emociones/<emoción>.md y Sentimientos/<sub-sentimiento>.md son los nodos principales.
- Notas/<fecha> <título>.md trae el consejo, los enlaces [[...]] a sus sentimientos,
  el texto completo y las notas parecidas.
Cada nota queda con su fecha de publicación como fecha de modificación del archivo.
"""
import calendar
import json
import os
import re
import shutil
import time

from build_viewer import BASE_URL, load_tags
from corpus import DATA_DIR, ROOT, load_posts

VAULT = os.path.join(ROOT, "vault")


def safe(name):
    return re.sub(r'[\\/:*?"<>|#^\[\]]+', "-", name.replace(" / ", " - ")).strip(" .-")


def write(path, text, date=None):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    if date:
        ts = calendar.timegm(time.strptime(date, "%Y-%m-%d")) + 12 * 3600
        os.utime(path, (ts, ts))


if __name__ == "__main__":
    tax = json.load(open(os.path.join(DATA_DIR, "taxonomy.json"), encoding="utf-8"))
    subs = {s["id"]: (s, e) for e in tax["emociones"] for s in e["subs"]}
    tags = load_tags()
    similar = json.load(open(os.path.join(DATA_DIR, "similar.json"), encoding="utf-8"))
    posts = load_posts()

    shutil.rmtree(VAULT, ignore_errors=True)
    for d in ("Emociones", "Sentimientos", "Notas"):
        os.makedirs(os.path.join(VAULT, d))

    names, used = {}, set()
    for p in posts:
        name = safe(f"{p['date']} {p['title']}")
        if name in used:
            name = safe(f"{p['date']} {p['title']} ({p['id'].split('_', 1)[1]})")
        used.add(name)
        names[p["id"]] = name

    by_sub = {sid: [] for sid in subs}
    for p in posts:
        t = tags.get(p["id"], {"tags": [], "consejo": ""})
        for sid, w in t["tags"]:
            by_sub[sid].append((w, p))
        links = [f"[[{safe(subs[sid][0]['nombre'])}]]{' (tema central)' if w == 3 else ''}" for sid, w in t["tags"]]
        sims = [f"- [[{names[s]}]]" for s, _ in similar.get(p["id"], [])[:4]]
        text = "\n".join([
            "---",
            f"fecha: {p['date']}",
            f"url: {p['url']}",
            "tags: [" + ", ".join(f"{subs[s][1]['id']}/{s}" for s, _ in t["tags"]) + "]",
            "---",
            "",
            f"# {p['title']}",
            "",
            f"> {t['consejo']}" if t["consejo"] else "",
            "",
            ("Sentimientos: " + " · ".join(links)) if links else "Sin emoción asignada.",
            "",
            *p["paragraphs"],
            "",
            f"[Leer en andyfrisella.com]({p['url']})",
            "",
            "## Notas parecidas",
            *sims,
            "",
        ])
        write(os.path.join(VAULT, "Notas", names[p["id"]] + ".md"), text, p["date"])

    for e in tax["emociones"]:
        lines = [f"# {e['nombre']}", "", e["descripcion"], ""]
        lines += [f"- [[{safe(s['nombre'])}]]: {s['descripcion']} ({len(by_sub[s['id']])} notas)" for s in e["subs"]]
        write(os.path.join(VAULT, "Emociones", safe(e["nombre"]) + ".md"), "\n".join(lines) + "\n")
        for s in e["subs"]:
            items = sorted(by_sub[s["id"]], key=lambda wp: wp[1]["date"], reverse=True)
            items.sort(key=lambda wp: -wp[0])  # tema central primero, luego de la más reciente a la más antigua
            lines = [f"# {s['nombre']}", "", f"Emoción: [[{safe(e['nombre'])}]]", "", s["descripcion"], "",
                     f"## Notas ({len(items)})", ""]
            lines += [f"- [[{names[p['id']]}]]{' · tema central' if w == 3 else ''}" for w, p in items]
            write(os.path.join(VAULT, "Sentimientos", safe(s["nombre"]) + ".md"), "\n".join(lines) + "\n")
    print(f"vault/: {len(posts)} notas, {len(subs)} sentimientos, {len(tax['emociones'])} emociones")
