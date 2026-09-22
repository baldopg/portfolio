# Genera content.js (datos de las vistas de detalle) a partir de lo extraído del portfolio
# actual (content_extract.json) más los textos de cada sección.
# Uso: python build_content.py
import json, pathlib

HERE = pathlib.Path(__file__).parent
d = json.loads((HERE / "content_extract.json").read_text(encoding="utf-8"))
P = "/"   # la web es la portada del sitio; rutas desde la raíz


def thumb(rel):
    """Miniatura de 640 px generada por make_thumbs.py (ruta relativa a la web)."""
    return "/vienna-3d/web/thumbs/" + rel.rsplit(".", 1)[0] + ".webp"


def cld(url, tr):
    """Transformación de Cloudinary insertada tras /upload/."""
    return url.replace("/upload/", f"/upload/{tr}/", 1)


def cld_poster(url, t=2):
    return cld(url, f"so_{t},w_720,f_jpg,q_auto").rsplit(".", 1)[0] + ".jpg"


experiments = []
for e in d["experiments"]:
    if e["type"] == "video":
        experiments.append({"type": "video", "title": e["title"], "cat": "3D & Experiments",
                            "src": cld(e["src"], "q_auto:good,f_auto,w_1600"),
                            "preview": cld(e["src"], "q_auto:eco,f_auto,w_640"),
                            "poster": cld_poster(e["src"])})
    else:
        experiments.append({"type": "image", "title": e["title"], "cat": "3D & Experiments", "src": P + e["src"], "thumb": thumb(e["src"])})

projects = []
for card in d["campCards"]:
    c = d["campaigns"][card["id"]]
    projects.append({
        "id": card["id"], "cat": "Branding" if card["cat"] == "branding" else "Campaigns",
        "title": c["name"].title() if c["name"].isupper() else c["name"], "tag": c["tag"],
        "cover": P + card["cover"], "coverThumb": thumb(card["cover"]),
        "video": cld(c["video"], "q_auto:good,f_auto,w_1600") if c.get("video") else None,
        "videoPoster": cld_poster(c["video"], 1) if c.get("video") else None,
        "photos": [{"src": P + ph["src"], "thumb": thumb(ph["src"]), "label": ph["label"]} for ph in c["photos"]],
    })
# nombres con mayúsculas propias
FIX = {"Ros Retail Outlet": "ROS Retail Outlet", "A.N.D. Beauty": "A.N.D. Beauty", "Omv": "OMV",
       "Österreichische Lotterien": "Österreichische Lotterien", "Freyville": "FREYVILLE"}
for p in projects:
    p["title"] = FIX.get(p["title"], p["title"])

w = d["world"]["videos"]
world_films = [
    {"title": "9.9.26, the countdown film", "meta": "Reposted by @world_xyz", "src": w[0]["src"], "poster": w[0]["poster"]},
    {"title": "Trade Everything, the launch film", "meta": "Reposted by @world_xyz", "src": w[1]["src"], "poster": w[1]["poster"]},
    {"title": "Happiness", "meta": "0:31 · A trading-floor life traded in for something else.", "src": w[3]["src"], "poster": w[3]["poster"]},
    {"title": "Prophecy", "meta": "0:40 · Every civilisation kept the same record. All of them named one date.", "src": w[4]["src"], "poster": w[4]["poster"]},
    {"title": "Back to World", "meta": "0:57 · The long way round, and the return.", "src": w[5]["src"], "poster": w[5]["poster"]},
]
world_visuals = [{"src": u, "label": l} for u, l in zip(d["world"]["images"], [
    "01 · Key visual · Call it and find out", "02 · Key visual · Predict", "03 · 3D render · What is World",
    "04 · Key visual · Open to resolve"])]

content = {
    "motion": {
        "num": "01", "title": "Motion.", "sub": "Independent experiments",
        "intro": "Personal motion studies, built frame by frame in After Effects with the sound designed to the same timeline. "
                 "Press the speaker on any piece to hear it from the start.",
        "disclaimer": "Independent experiments. Not commissioned by, affiliated with or endorsed by vorauerfriends or fonio. "
                      "Names and logos belong to their owners.",
        "pieces": [
            {"title": "vorauerfriends · Hello!", "meta": "Independent study · After Effects · 11 s · sound design",
             "text": "The letters of a hello turn into a waving hand, then into the VF logo, a wink and a signature. Every stroke is rounded.",
             "src": P + "work/motion/vf-hello.mp4", "poster": P + "work/motion/vf-hello-poster.jpg"},
            {"title": "vorauerfriends · Hello! in 3D", "meta": "Independent study · After Effects Cinema 4D renderer · 11 s",
             "text": "The same choreography rebuilt in 3D: flat colour without lights, real extrusion and a real 3D camera.",
             "src": P + "work/motion/vf-hello-3d.mp4", "poster": P + "work/motion/vf-hello-3d-poster.jpg"},
            {"title": "fonio · Anruf angenommen", "meta": "Independent study · After Effects · 4.5 s · alpha video",
             "text": "A logo animation for an AI phone assistant: the call is picked up by a classic handset with slots.",
             "src": P + "work/motion/fonio-logo.mp4", "srcWebm": P + "work/motion/fonio-logo.webm",
             "poster": P + "work/motion/fonio-logo-poster.webp", "light": True},
        ],
    },
    "works": {
        "num": "02", "title": "Selected works.", "sub": "3D & Experiments · Branding · Campaigns",
        "intro": "Experiments in 3D and motion, brand identities and campaigns for Austrian brands.",
        "experiments": experiments, "projects": projects,
    },
    "built": {
        "num": "03", "title": "Built on my own.", "sub": "Self-taught · shipped · no mockups",
        "intro": "Since 2021 I have been on parental leave, caring for my son. I used the time to stop handing designs over and to "
                 "build them myself. Kotlin, Jetpack Compose and the modern web stack, all self-taught. One app is live on the Play "
                 "Store, an AI product went from idea to live in four days. Every one of these is finished and running. Nothing here is a mockup.",
        "items": [
            {"n": "01", "status": "Live on Play Store", "title": "SplitEasy", "kind": "Android · solo",
             "text": "Bill splitting with on-device receipt scanning: point the camera at a receipt, OCR reads the items, the app splits them. "
                     "Product, interface, code, store listing, monetisation and consent flow, all of it alone.",
             "stack": ["Kotlin", "Jetpack Compose", "Material 3", "Room", "CameraX", "ML Kit OCR", "AdMob + UMP", "R8"]},
            {"n": "02", "status": "Live", "title": "Module 01", "kind": "Interactive learning · ~8 min",
             "text": "A working e-learning module built as a job application, because describing instructional design in a PDF proves nothing. "
                     "Five chapters, branching scenarios, an xAPI statement fired on every interaction, and a live tracking panel.",
             "stack": ["JavaScript", "xAPI", "WCAG 2.2 AA", "EN/DE/ES", "Blender", "Netlify"], "link": P + "for-boehringer/index.html"},
            {"n": "03", "status": "Live", "title": "Mast", "kind": "AI product · 4 days",
             "text": "You tie a note to an emotional state instead of a date; months later it recognises you are back in that state and "
                     "returns your own words. Ships with a forced response schema, a fail-closed parser and a browser-side fallback.",
             "stack": ["Vanilla JS", "Netlify Functions", "Structured output", "Serverless", "Deploy guard"]},
            {"n": "04", "status": "In development", "title": "Faro", "kind": "Android",
             "text": "Personal finance for people who are not accountants. Privacy is the architecture rather than a policy: no accounts, "
                     "no sync, no telemetry, encrypted local storage, ads forced to non-personalised with no advertising ID.",
             "stack": ["Kotlin", "Compose", "Room + SQLCipher", "Hilt", "Coroutines", "Biometrics", "Glance", "Vico"]},
            {"n": "05", "status": "Built", "title": "HabitCheck", "kind": "Android",
             "text": "Habit tracker with reminders that survive a reboot, and a custom Compose calendar heatmap.",
             "stack": ["Kotlin", "Compose", "Room", "DataStore", "Hilt", "AlarmManager"]},
            {"n": "06", "status": "Built", "title": "Prism Dodge", "kind": "Game · signed APK",
             "text": "One-tap Android arcade game, rendered entirely procedurally so it ships with zero binary assets.",
             "stack": ["Godot 4", "GDScript", "Android signing"]},
        ],
    },
    "architect": {
        "num": "·", "title": "The architect of form.", "sub": "3D · Motion · Brand identity",
        "intro": "Precision-driven design at the intersection of 3D, motion and brand identity. Precision from concept to final render.",
        "facts": [
            {"k": "Recognition", "v": "SuperRare Open Call Winner. Work exhibited in Times Square, New York and in Rome, Italy."},
            {"k": "Industry experience", "v": "Campaigns for Österreichische Lotterien, Puntigamer, Gösser and OMV through GGK MullenLowe Vienna."},
            {"k": "Specialisation", "v": "3D product visualization · Motion design · Brand identity."},
        ],
    },
    "vienna": {
        "num": "04", "title": "Vienna, on foot.", "sub": "Street photography",
        "intro": "Street photography from the city this model is made of.",
        "photos": [{"src": P + p, "thumb": thumb(p), "label": p.rsplit("/", 1)[-1].rsplit(".", 1)[0]} for p in d["photos"]],
    },
    "world": {
        "num": "05", "title": "World · AI films.", "sub": "ComfyUI · MiniMax H3 · independent series",
        "intro": "Short films and key visuals generated locally in ComfyUI with MiniMax H3. Independent creative work exploring World, "
                 "the on-chain prediction market. The identity, product and positioning are theirs; my work builds on that foundation "
                 "through key visuals, films and social concepts created for X. Selected work was reposted by @world_xyz.",
        "films": world_films, "visuals": world_visuals,
    },
    "about": {
        "num": "06", "title": "About me.", "sub": "Vienna · from Spain · available for projects",
        "intro": "Graphic designer, 3D artist and motion specialist based in Vienna, originally from Spain. I believe in systems over "
                 "isolated pieces: visual languages that scale, breathe and last. After building campaigns for major Austrian brands and "
                 "earning international recognition for my digital art, I bring both strategic thinking and technical precision to every project.",
        "experience": [
            {"k": "SuperRare", "v": "Open Call Winner. Work exhibited in Rome and Times Square, New York."},
            {"k": "GGK MullenLowe", "v": "Campaigns for Österreichische Lotterien, Puntigamer, Gösser, OMV. Brand consistency across all channels."},
            {"k": "Securikett", "v": "Graphic and label designer in a technically driven environment. Precision workflows, packaging."},
            {"k": "Bosch", "v": "Industrial production in Bavaria. Structured, disciplined, high-precision workflow."},
        ],
        "tools": [["Blender", "Advanced"], ["Adobe Photoshop", "Expert"], ["Adobe Illustrator", "Expert"], ["Adobe InDesign", "Expert"],
                  ["Premiere Pro", "Proficient"], ["Houdini", "Growing"], ["Unreal Engine", "Proficient"],
                  ["3D Product Visualization", "Advanced"], ["Motion Design", "Advanced"], ["Brand Identity", "Expert"]],
        "languages": ["ES · Native", "EN · Fluent", "DE · Growing"],
        "email": "baldopgarcia@gmail.com", "cv": P + "CV-Baldomero-Perdomo-Garcia.pdf",
    },
}

js = "// Generado por build_content.py a partir del portfolio actual. No editar a mano.\nexport const CONTENT = " + \
     json.dumps(content, ensure_ascii=False, indent=1) + ";\n"
(HERE / "content.js").write_text(js, encoding="utf-8")
print("content.js", len(js) // 1024, "KB ·", len(experiments), "experiments ·", len(projects), "projects ·",
      len(content["vienna"]["photos"]), "photos ·", len(world_films), "films")
