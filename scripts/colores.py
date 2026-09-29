"""Colores de las emociones al estilo Intensamente.

Cada emoción toma el color de su personaje (Furia rojo, Alegría amarillo...) o, si no hay
personaje, la mezcla de dos. La mezcla se hace en OKLab (perceptual) y luego se ajusta la
luminosidad para cada modo: más clara sobre fondo oscuro y más oscura sobre fondo claro,
para que los nodos tengan contraste de al menos 3:1 con el fondo.
"""


def _lin(c):
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def _srgb(c):
    return 12.92 * c if c <= 0.0031308 else 1.055 * c ** (1 / 2.4) - 0.055


def hex_to_oklab(h):
    r, g, b = (_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))
    l = (0.4122214708 * r + 0.5363325363 * g + 0.0514459929 * b) ** (1 / 3)
    m = (0.2119034982 * r + 0.6806995451 * g + 0.1073969566 * b) ** (1 / 3)
    s = (0.0883024619 * r + 0.2817188376 * g + 0.6299787005 * b) ** (1 / 3)
    return (0.2104542553 * l + 0.7936177850 * m - 0.0040720468 * s,
            1.9779984951 * l - 2.4285922050 * m + 0.4505937099 * s,
            0.0259040371 * l + 0.7827717662 * m - 0.8086757660 * s)


def _oklab_to_lin(L, a, b):
    l = (L + 0.3963377774 * a + 0.2158037573 * b) ** 3
    m = (L - 0.1055613458 * a - 0.0638541728 * b) ** 3
    s = (L - 0.0894841775 * a - 1.2914855480 * b) ** 3
    return (4.0767416621 * l - 3.3077115913 * m + 0.2309699292 * s,
            -1.2684380046 * l + 2.6097574011 * m - 0.3413193965 * s,
            -0.0041960863 * l - 0.7034186147 * m + 1.7076147010 * s)


def oklab_to_hex(L, a, b):
    """Si el color no cabe en sRGB, reduce el croma (manteniendo tono y luminosidad) hasta que quepa."""
    for k in range(40):
        f = 1 - k * 0.025
        rgb = _oklab_to_lin(L, a * f, b * f)
        if all(-1e-4 <= c <= 1 + 1e-4 for c in rgb):
            break
    return "#" + "".join(f"{round(max(0, min(1, _srgb(max(0, min(1, c))))) * 255):02x}" for c in rgb)


def luminancia(h):
    r, g, b = (_lin(int(h[i:i + 2], 16) / 255) for i in (1, 3, 5))
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    la, lb = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def mezcla(hexes):
    labs = [hex_to_oklab(h) for h in hexes]
    L, a, b = (sum(v) / len(labs) for v in zip(*labs))
    c = (a * a + b * b) ** 0.5
    if len(hexes) > 1 and c < 0.07:  # dos colores casi opuestos se vuelven gris: se le devuelve algo de color
        f = 0.07 / max(c, 1e-6)
        a, b = a * f, b * f
    return L, a, b


def para_modo(lab, fondo, oscuro):
    """Ajusta la luminosidad hasta tener contraste >= 3:1 con el fondo, sin salirse de la banda del modo."""
    L, a, b = lab
    L = min(max(L, 0.66), 0.84) if oscuro else min(max(L, 0.45), 0.62)
    paso = 0.01 if oscuro else -0.01
    color = oklab_to_hex(L, a, b)
    while contraste(color, fondo) < 3.0 and 0.3 < L < 0.95:
        L += paso
        color = oklab_to_hex(L, a, b)
    return color


def colores_emociones(tax, fondo_oscuro="#0f1218", fondo_claro="#f6f7f9"):
    paleta = {k: v["color"] for k, v in tax["intensamente"].items()}
    res = {}
    for e in tax["emociones"]:
        L, a, b = mezcla([paleta[k] for k in e["intensamente"]])
        f = e.get("croma", 1.0)  # algunas emociones van apagadas a propósito (desesperanza: "sin luz")
        lab = (L, a * f, b * f)
        res[e["id"]] = {"dark": para_modo(lab, fondo_oscuro, True), "light": para_modo(lab, fondo_claro, False)}
    return res


if __name__ == "__main__":
    import json
    import os
    from corpus import DATA_DIR
    tax = json.load(open(os.path.join(DATA_DIR, "taxonomy.json"), encoding="utf-8"))
    for e in tax["emociones"]:
        c = colores_emociones(tax)[e["id"]]
        mezcla_txt = " + ".join(tax["intensamente"][k]["nombre"] for k in e["intensamente"])
        print(f"{e['nombre']:<24} {mezcla_txt:<22} noche {c['dark']} ({contraste(c['dark'], '#0f1218'):.1f}:1)  "
              f"claro {c['light']} ({contraste(c['light'], '#f6f7f9'):.1f}:1)")
