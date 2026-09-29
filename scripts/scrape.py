import re, json, os, sys, time, requests
from concurrent.futures import ThreadPoolExecutor
from bs4 import BeautifulSoup
from markdownify import markdownify as md

BASE = "https://andyfrisella.com"
OUT = os.path.join(os.path.dirname(__file__), "..", "posts")
os.makedirs(OUT, exist_ok=True)
S = requests.Session(); S.headers["User-Agent"] = "Mozilla/5.0"

DELAY = 1.0  # segundos entre requests por hilo

def get(url):
    wait = 30
    for i in range(12):
        try:
            r = S.get(url, timeout=30)
            if r.status_code == 200:
                time.sleep(DELAY); return r.text
            if r.status_code == 404: return None
            if r.status_code == 429:
                w = int(r.headers.get("Retry-After") or wait)
                print(f"429, esperando {w}s", flush=True); time.sleep(w); wait = min(wait * 2, 300); continue
        except Exception: pass
        time.sleep(5)
    return None

def list_page(p):
    html = get(f"{BASE}/blogs/andygram?page={p}") or ""
    return re.findall(r'href="(/blogs/andygram/[^"#?/]+)"', html)

def fetch(path):
    slug = path.rsplit("/", 1)[1]
    done = [f for f in os.listdir(OUT) if f.endswith(f"_{slug}.md") or f == f"{slug}.md"]
    if done: return slug, done[0]
    html = get(BASE + path)
    if not html: return slug, None
    s = BeautifulSoup(html, "html.parser")
    title = s.select_one("h1.article_title").get_text(strip=True)
    date = ""
    for sc in s.select('script[type="application/ld+json"]'):
        try:
            d = json.loads(sc.string, strict=False)
            if d.get("@type") == "Article": date = d.get("datePublished", "")[:10]
        except Exception: pass
    content = s.select_one("div.article_content")
    for fr in content.select("iframe[src]"):
        src = fr["src"].split("?")[0]
        if src.startswith("//"): src = "https:" + src
        fr.replace_with(BeautifulSoup(f'<p><a href="{src}">Video: {src}</a></p>', "html.parser"))
    for st in content.select("style"): st.decompose()
    body = md(str(content), heading_style="ATX").strip()
    body = re.sub(r"\n{3,}", "\n\n", body)
    fn = f"{date}_{slug}.md" if date else f"{slug}.md"
    with open(os.path.join(OUT, fn), "w") as f:
        f.write(f"---\ntitle: \"{title.replace(chr(34), chr(39))}\"\ndate: {date}\nurl: {BASE}{path}\n---\n\n# {title}\n\n{body}\n")
    return slug, fn

def discover_new(known):
    """Recorre el listado desde la página 1 hasta encontrar una página sin URLs nuevas."""
    new = []
    for page in range(1, 1000):
        found = [x for x in list_page(page) if x not in known and x not in new]
        if not found:
            break
        new.extend(found)
    return new

if __name__ == "__main__":
    # Uso: python3 scripts/scrape.py [páginas]   o   python3 scripts/scrape.py --nuevos
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    last = int(args[0]) if args else 202
    cache = os.path.join(os.path.dirname(__file__), "urls.json")
    if os.path.exists(cache):
        paths = json.load(open(cache))
        if "--nuevos" in sys.argv:
            new = discover_new(set(paths))
            print("urls nuevas:", len(new), flush=True)
            paths = new + paths
            json.dump(paths, open(cache, "w"))
    else:
        with ThreadPoolExecutor(2) as ex:
            pages = list(ex.map(list_page, range(1, last + 1)))
        paths = list(dict.fromkeys(p for lst in pages for p in lst))
        empty = [i + 1 for i, l in enumerate(pages) if not l]
        if empty: print("páginas vacías (no se cachea):", empty, flush=True)
        else: json.dump(paths, open(cache, "w"))
    print("urls:", len(paths), flush=True)
    fails = []
    with ThreadPoolExecutor(2) as ex:
        for i, (slug, fn) in enumerate(ex.map(fetch, paths), 1):
            if not fn: fails.append(slug)
            if i % 100 == 0: print(i, flush=True)
    print("done", len(paths) - len(fails), "failed:", fails)
