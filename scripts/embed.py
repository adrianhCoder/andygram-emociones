"""Embeddings locales (bge-small-en-v1.5) para enlazar cada nota con sus más parecidas.

Escribe data/similar.json: {id: [[id_vecino, similitud], ...]} con las K más cercanas.
"""
import json
import os

import numpy as np
from fastembed import TextEmbedding

from corpus import DATA_DIR, load_posts

K = 5

if __name__ == "__main__":
    posts = load_posts()
    texts = [p["title"] + ". " + " ".join(p["paragraphs"]) for p in posts]
    model = TextEmbedding("BAAI/bge-small-en-v1.5")
    vecs = np.array(list(model.embed(texts, batch_size=64)))
    vecs /= np.linalg.norm(vecs, axis=1, keepdims=True)
    sims = vecs @ vecs.T
    np.fill_diagonal(sims, -1)
    similar = {}
    for i, p in enumerate(posts):
        top = np.argsort(-sims[i])[:K]
        similar[p["id"]] = [[posts[j]["id"], round(float(sims[i, j]), 3)] for j in top]
    with open(os.path.join(DATA_DIR, "similar.json"), "w") as f:
        json.dump(similar, f, ensure_ascii=False)
    best = sims.max(axis=1)
    print(f"{len(posts)} notas. Similitud con su vecina más cercana: "
          f"mediana {np.median(best):.3f}, p90 {np.percentile(best, 90):.3f}, "
          f"casi duplicadas (>0.97): {int((best > 0.97).sum())}")
