# Mide ancho y alto de cada vídeo del sitio con ffprobe y los guarda en video_sizes.json,
# para que cada reproductor tenga la proporción real (vertical, 16:9, panorámico).
# Uso: python probe_videos.py   (después: python build_content.py)
import json, pathlib, subprocess

HERE = pathlib.Path(__file__).parent
ROOT = HERE.parent.parent
OUT = HERE / "video_sizes.json"
sizes = json.loads(OUT.read_text(encoding="utf-8")) if OUT.exists() else {}

src = (HERE / "content.js").read_text(encoding="utf-8")
data = json.loads(src[src.index("{"): src.rstrip().rstrip(";").rindex("}") + 1])
urls = [e["src"] for e in data["works"]["experiments"] if e["type"] == "video"]
urls += [p["video"] for p in data["works"]["projects"] if p["video"]]
urls += [f["src"] for f in data["world"]["films"]]
urls += [m["src"] for m in data["motion"]["pieces"]]

for u in urls:
    if u in sizes:
        continue
    target = str(ROOT / u.lstrip("/")) if u.startswith("/") else u
    r = subprocess.run(["ffprobe", "-v", "error", "-select_streams", "v:0", "-show_entries", "stream=width,height",
                        "-of", "csv=p=0", target], capture_output=True, text=True, timeout=90)
    w, h = map(int, r.stdout.strip().split("\n")[0].split(","))
    sizes[u] = [w, h]
    print(f"{w}x{h}  {u}")
OUT.write_text(json.dumps(sizes, indent=1), encoding="utf-8")
print(len(sizes), "vídeos medidos")
