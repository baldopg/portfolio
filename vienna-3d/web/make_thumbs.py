# Miniaturas para paneles y rejillas (WebP, 640 px de ancho). Los originales solo se cargan
# en el visor. Refleja la ruta: ../../work/x/y.webp -> thumbs/work/x/y.webp
# Uso: python make_thumbs.py   (después: python build_content.py)
import json, pathlib, re
from PIL import Image

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent            # portfolio/
MAX_W = 640

d = json.loads((HERE / "content_extract.json").read_text(encoding="utf-8"))
paths = set(d["photos"])
paths |= {e["src"] for e in d["experiments"] if e["type"] == "image"}
for c in d["campaigns"].values():
    paths |= {ph["src"] for ph in c["photos"]}
paths |= {c["cover"] for c in d["campCards"]}
# imágenes de los paneles de index.html
html = (ROOT / "index.html").read_text(encoding="utf-8")
paths |= {re.sub(r"%([0-9A-F]{2})", lambda m: bytes.fromhex(m.group(1)).decode("latin-1"), p).encode("latin-1").decode("utf-8")
          for p in re.findall(r'src="/(work/[^"]+\.(?:webp|jpg|png))"', html)}

made = skipped = 0
total_in = total_out = 0
for rel in sorted(paths):
    src = ROOT / rel
    dst = HERE / "thumbs" / rel
    dst = dst.with_suffix(".webp")
    if not src.exists():
        print("FALTA", rel)
        continue
    if dst.exists() and dst.stat().st_mtime >= src.stat().st_mtime:
        skipped += 1
        continue
    dst.parent.mkdir(parents=True, exist_ok=True)
    im = Image.open(src)
    im = im.convert("RGBA" if im.mode in ("RGBA", "LA", "P") else "RGB")
    if im.width > MAX_W:
        im = im.resize((MAX_W, round(im.height * MAX_W / im.width)), Image.LANCZOS)
    im.save(dst, "WEBP", quality=78, method=6)
    made += 1
    total_in += src.stat().st_size
    total_out += dst.stat().st_size
print(f"{made} miniaturas nuevas, {skipped} al día · {total_in / 1e6:.1f} MB -> {total_out / 1e6:.2f} MB")
