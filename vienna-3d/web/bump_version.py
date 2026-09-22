# Pone un parámetro de versión (?v=...) a los CSS y módulos JS locales para romper la caché
# del navegador tras cada cambio. Uso: python bump_version.py
import re, time, pathlib

HERE = pathlib.Path(__file__).parent
V = time.strftime("%Y%m%d%H%M%S")
LOCAL = r"(style\.css|detail\.css|main\.js|video\.js|detail\.js|content\.js)"

for p in [HERE.parent.parent / "index.html", HERE / "main.js", HERE / "detail.js"]:
    name = p.name
    s = p.read_text(encoding="utf-8")
    s2 = re.sub(r"""(["'](?:\./|/vienna-3d/web/)?)""" + LOCAL + r"""(?:\?v=\d+)?(["'])""", lambda m: f"{m.group(1)}{m.group(2)}?v={V}{m.group(3)}", s)
    p.write_text(s2, encoding="utf-8")
    print(name, len(re.findall(r"\?v=" + V, s2)), "refs")
print("version", V)
