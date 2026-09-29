"""Genera el visor con los datos embebidos.

- viewer/index.html: documento completo para abrir local en el navegador.
- viewer/artifact.html: el mismo contenido sin <html>/<head>/<body>, para publicarlo como Artifact.

Las dos llevan el texto completo de cada nota.

Junta taxonomía, notas (posts/), etiquetas (data/tags/*.jsonl) y vecinos (data/similar.json)
dentro de viewer/template.html.
"""
import glob
import json
import os

from corpus import DATA_DIR, ROOT, load_posts

BASE_URL = "https://andyfrisella.com/blogs/andygram/"
VIEWER = os.path.join(ROOT, "viewer")
SHELL = """<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
</head>
<body>
{page}
</body>
</html>
"""


def load_tags():
    """Etiquetas por id de nota. La prueba (pilot) va primero y la corrida completa la sobreescribe."""
    paths = sorted(glob.glob(os.path.join(DATA_DIR, "tags", "*.jsonl")),
                   key=lambda p: (not p.endswith("pilot.jsonl"), p))
    tags = {}
    for path in paths:
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            tags[r["id"]] = r
    return tags


def build_data(full_text=True):
    tax = json.load(open(os.path.join(DATA_DIR, "taxonomy.json"), encoding="utf-8"))
    sub_index = {s["id"]: i for i, s in enumerate(s for e in tax["emociones"] for s in e["subs"])}
    tags = load_tags()
    similar = json.load(open(os.path.join(DATA_DIR, "similar.json"), encoding="utf-8"))
    posts = load_posts()
    index = {p["id"]: i for i, p in enumerate(posts)}
    rows = []
    for p in posts:
        t = tags.get(p["id"], {"tags": [], "consejo": ""})
        rows.append([
            p["url"].removeprefix(BASE_URL),
            p["title"],
            p["date"],
            t["consejo"],
            [[sub_index[s], w] for s, w in t["tags"]],
            [index[s] for s, _ in similar.get(p["id"], [])[:4]],
            "\n".join(p["paragraphs"]) if full_text else "",
        ])
    emotions = [{
        "id": e["id"], "name": e["nombre"], "desc": e["descripcion"],
        "subs": [{"id": s["id"], "name": s["nombre"], "desc": s["descripcion"]} for s in e["subs"]],
    } for e in tax["emociones"]]
    return {"emotions": emotions, "baseUrl": BASE_URL, "fullText": full_text, "posts": rows}, len(tags), len(posts)


def render(full_text):
    data, n_tagged, n_posts = build_data(full_text)
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    template = open(os.path.join(VIEWER, "template.html"), encoding="utf-8").read()
    return template.replace("__DATA__", blob), n_tagged, n_posts


if __name__ == "__main__":
    page, n_tagged, n_posts = render(full_text=True)
    with open(os.path.join(VIEWER, "index.html"), "w", encoding="utf-8") as f:
        f.write(SHELL.format(page=page))
    with open(os.path.join(VIEWER, "artifact.html"), "w", encoding="utf-8") as f:
        f.write(page)
    sizes = [os.path.getsize(os.path.join(VIEWER, n)) / 1e6 for n in ("index.html", "artifact.html")]
    print(f"{n_tagged}/{n_posts} notas etiquetadas -> viewer/index.html ({sizes[0]:.1f} MB) "
          f"y viewer/artifact.html ({sizes[1]:.1f} MB)")
