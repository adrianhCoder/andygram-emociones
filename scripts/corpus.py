"""Carga los posts descargados (posts/*.md) como texto limpio."""
import glob
import os
import re

ROOT = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
POSTS_DIR = os.path.join(ROOT, "posts")
DATA_DIR = os.path.join(ROOT, "data")


def _clean(line):
    line = re.sub(r"!\[[^\]]*\]\([^)]*\)", "", line)  # imágenes
    line = re.sub(r"\[([^\]]*)\]\(([^)]*)\)", lambda m: m.group(1) or m.group(2), line)  # links -> texto
    line = re.sub(r"\\([\\`*_{}\[\]()#+\-.!>|~])", r"\1", line)  # escapes de markdownify
    line = re.sub(r"^(#+|>)\s*", "", line.strip())  # encabezados y citas
    return line.replace("**", "").replace("__", "").strip()


def load_posts():
    """Lista de posts en orden cronológico: id, title, date, url, paragraphs."""
    posts = []
    for path in sorted(glob.glob(os.path.join(POSTS_DIR, "*.md"))):
        _, fm, body = open(path, encoding="utf-8").read().split("---\n", 2)
        meta = dict(re.findall(r"^(\w+): (.*)$", fm, re.M))
        lines = body.strip().split("\n")
        if lines and lines[0].startswith("# "):
            lines = lines[1:]
        posts.append({
            "id": os.path.basename(path)[:-3],
            "title": meta["title"].strip().strip('"'),
            "date": meta["date"].strip(),
            "url": meta["url"].strip(),
            "paragraphs": [c for c in map(_clean, lines) if c],
        })
    return posts
