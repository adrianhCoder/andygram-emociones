"""Muestra en vivo el avance del etiquetado por emociones (Ctrl+C para salir).

Uso: python3 scripts/progreso_etiquetado.py [--una-vez]
"""
import glob
import json
import os
import re
import sys
import time
from collections import Counter
from datetime import datetime

from corpus import DATA_DIR

REFRESH = 5
WINDOW_MIN = 10


def bar(frac, width):
    full = round(frac * width)
    return "█" * full + "░" * (width - full)


def snapshot():
    chunks = sorted(glob.glob(os.path.join(DATA_DIR, "chunks", "chunk_*.txt")))
    sizes = {os.path.basename(c)[:-4]: len(re.findall(r"^=== POST ", open(c).read(), re.M)) for c in chunks}
    total = sum(sizes.values())
    done, rows, recent = {}, [], []
    now = time.time()
    for name in sizes:
        path = os.path.join(DATA_DIR, "tags", name + ".jsonl")
        if os.path.exists(path):
            lines = [json.loads(line) for line in open(path)]
            done[name] = os.path.getmtime(path)
            rows += lines
    tagged = len(rows)
    empty = sum(1 for r in rows if not r["tags"])
    subs = Counter(s for r in rows for s, _ in r["tags"])
    in_window = sum(sizes[n] for n, t in done.items() if now - t <= WINDOW_MIN * 60)
    rate = in_window / WINDOW_MIN

    out = [f"Etiquetado AndyGram  ({datetime.now():%H:%M:%S})", ""]
    out.append(f"Bloques: {len(done):>3}/{len(sizes)}  {bar(len(done) / len(sizes), 30)} {len(done) * 100 // len(sizes)}%")
    out.append(f"Notas:   {tagged:,}/{total:,}" + (f" · {empty} sin emoción ({empty * 100 // max(tagged, 1)}%)" if tagged else ""))
    if len(done) == len(sizes):
        out.append("Ritmo:   terminado")
    elif rate:
        out.append(f"Ritmo:   ~{rate:.0f} notas/min (últimos {WINDOW_MIN} min) · faltan ~{(total - tagged) / rate:.0f} min")
    else:
        out.append(f"Ritmo:   sin bloques nuevos en los últimos {WINDOW_MIN} min")
    out += ["", "Últimos bloques guardados:"]
    for name, t in sorted(done.items(), key=lambda x: -x[1])[:6]:
        out.append(f"  {datetime.fromtimestamp(t):%H:%M:%S}  {name}  {sizes[name]} notas")
    if subs:
        top = subs.most_common(10)
        out += ["", "Sub-sentimientos más usados:"]
        for s, c in top:
            out.append(f"  {s:<20} {bar(c / top[0][1], 24)} {c}")
    missing = [n.removeprefix("chunk_") for n in sizes if n not in done]
    if missing:
        out += ["", "Faltan: " + " ".join(missing)]
    return "\n".join(out)


if __name__ == "__main__":
    if "--una-vez" in sys.argv:
        print(snapshot())
        sys.exit()
    try:
        while True:
            text = snapshot()
            print("\033[2J\033[H" + text, flush=True)
            time.sleep(REFRESH)
    except KeyboardInterrupt:
        pass
