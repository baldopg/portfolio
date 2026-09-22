# Manzanas genéricas: pocas variantes de bloque vienés (Gründerzeit, patio cerrado)
# repartidas como copias enlazadas. Evitan monumentos, plazas, parques, calles y el canal.
import math, random
exec(open(r"C:\Users\Baldo\Desktop\portfolio\vienna-3d\blender\vlib.py", encoding="utf-8").read())
mat("Paper", "F4F2EE"); mat("Roof", "C9C6C0"); mat("Ink", "111111")
MATS = ["Paper", "Roof", "Ink"]
P, ROOF, INK = 0, 1, 2
rng = random.Random(1897)

BLK = bpy.data.collections["Blocks"]
# --------------------------------------------------------------- limpiar lo anterior
for o in list(BLK.objects):
    bpy.data.objects.remove(o, do_unlink=True)
proto_root = bpy.data.objects.get("BLOCK_PROTOS") or bpy.data.objects.new("BLOCK_PROTOS", None)
if proto_root.name not in BLK.objects:
    BLK.objects.link(proto_root)
proto_root.location = (0, 0, -500)          # los prototipos quedan bajo el suelo


def wing(p, cx, cy, length, depth, h, along_x):
    """Ala de un bloque: cuerpo + tejado a dos aguas + ventanas en la cara exterior."""
    if along_x:
        p.box((cx, cy, h / 2), (length, depth, h), P)
        p.gable_roof((cx, cy, 0), length, depth, h, h + 5.5, ROOF, rot_z=0)
    else:
        p.box((cx, cy, h / 2), (depth, length, h), P)
        p.gable_roof((cx, cy, 0), length, depth, h, h + 5.5, ROOF, rot_z=math.pi / 2)


def block_variant(name, W, D, h, ring=13.0):
    p = Part(name, proto_root, MATS)
    wing(p, 0, -D / 2 + ring / 2, W, ring, h, True)
    wing(p, 0, D / 2 - ring / 2, W, ring, h, True)
    wing(p, -W / 2 + ring / 2, 0, D - 2 * ring, ring, h, False)
    wing(p, W / 2 - ring / 2, 0, D - 2 * ring, ring, h, False)
    floors = [4.2 + 3.5 * k for k in range(int((h - 5) / 3.5))]
    nx, ny = max(2, int(W / 3.6)), max(2, int(D / 3.6))
    p.windows(-W / 2 + 1.5, W / 2 - 1.5, -D / 2 - 0.06, floors, nx, 1.25, 2.1, INK, quad=True)
    p.windows(-W / 2 + 1.5, W / 2 - 1.5, D / 2 + 0.06, floors, nx, 1.25, 2.1, INK, quad=True)
    p.windows_x(-D / 2 + 1.5, D / 2 - 1.5, -W / 2 - 0.06, floors, ny, 1.25, 2.1, INK, quad=True)
    p.windows_x(-D / 2 + 1.5, D / 2 - 1.5, W / 2 + 0.06, floors, ny, 1.25, 2.1, INK, quad=True)
    p.box((0, 0, 0.6), (W, D, 1.2), P)                              # zócalo continuo
    ob = p.commit(coll="Blocks")
    ob.parent = proto_root
    return ob.data


VARIANTS = [block_variant(f"Block_{i}", W, D, h) for i, (W, D, h) in enumerate([
    (48, 40, 21), (56, 44, 24.5), (40, 36, 21), (64, 50, 24.5), (44, 52, 28), (36, 30, 17.5)])]

# --------------------------------------------------------------- zonas prohibidas
def seg_dist(p, a, b):
    ab = b - a; t = max(0.0, min(1.0, (p - a).dot(ab) / max(ab.length_squared, 1e-9)))
    return (p - (a + ab * t)).length


def polyline(real):
    return [to_map(e, n).to_2d() for e, n in real]


def dist_to_line(p, line):
    return min(seg_dist(p, line[i], line[i + 1]) for i in range(len(line) - 1))


def inside(p, poly):
    c = False; j = len(poly) - 1
    for i in range(len(poly)):
        if ((poly[i].y > p.y) != (poly[j].y > p.y)) and \
                (p.x < (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y + 1e-12) + poly[i].x):
            c = not c
        j = i
    return c


RING = polyline([(-133, 1034), (-500, 860), (-808, 690), (-897, 500), (-945, 167), (-960, -33), (-900, -300),
                 (-822, -500), (-600, -640), (-378, -700), (-67, -801), (215, -834), (438, -500), (511, -222),
                 (697, 167), (808, 356)])
CANAL = polyline([(-1500, 2400), (-700, 1500), (-133, 1034), (348, 367), (808, 356), (1300, 50), (1900, -500)])
STREETS = [(polyline([(348, 367), (1000, 640), (1500, 830)]), 26),
           (polyline([(0, -40), (-120, -350), (-230, -660)]), 18),
           (polyline([(-60, 40), (-260, 110), (-330, 160)]), 20),
           (polyline([(-120, -840), (-160, -1400)]), 22)]
INNER = RING + list(reversed(polyline([(-133, 1034), (348, 367), (808, 356)])))  # Innere Stadt
AREAS = []
for o in bpy.data.collections["Nature"].objects:
    if o.type == 'MESH' and (o.name.startswith("Park_") or o.name.startswith("Square_")):
        AREAS.append([(o.matrix_world @ v.co).to_2d() for v in o.data.vertices])
for o in bpy.data.collections["Streets"].objects:
    if o.name.startswith("Square_"):
        AREAS.append([(o.matrix_world @ v.co).to_2d() for v in o.data.vertices])
LANDMARK_R = {"LM_Stephansdom": 95, "LM_Staatsoper": 88, "LM_Karlskirche": 105, "LM_Secession": 45,
              "LM_Parlament": 112, "LM_Rathaus": 118, "LM_Burgtheater": 82, "LM_Votivkirche": 70}
LMS = [(bpy.data.objects[n].location.to_2d(), r) for n, r in LANDMARK_R.items() if n in bpy.data.objects]
RR = bpy.data.objects["RR_Root"].location.to_2d()


# tramos bajos del recorrido de cámara: ahí no puede haber manzanas
import json
_keys = json.load(open(r"C:\Users\Baldo\Desktop\portfolio\vienna-3d\web\camera_path.json", encoding="utf-8"))["keys"]
_cp = [Vector(k["cam"]) for k in _keys]
CAM_LOW = []
for i in range(len(_cp) - 1):
    p0 = _cp[max(i - 1, 0)]; p1 = _cp[i]; p2 = _cp[i + 1]; p3 = _cp[min(i + 2, len(_cp) - 1)]
    for k in range(24):
        t = k / 24; t2, t3 = t * t, t * t * t
        q = 0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2 + (-p0 + 3 * p1 - 3 * p2 + p3) * t3)
        if q.z < 55:
            CAM_LOW.append(q.to_2d())


def free(p, radius):
    for q in CAM_LOW:
        if (p - q).length < radius + 22: return False
    if dist_to_line(p, RING) < 23 + radius + 4: return False
    if dist_to_line(p, CANAL) < 40 + radius: return False
    for line, w in STREETS:
        if dist_to_line(p, line) < w / 2 + radius: return False
    for c, r in LMS:
        if (p - c).length < r + radius * 0.6: return False
    if (p - RR).length < 150: return False
    for poly in AREAS:
        if inside(p, poly): return False
    return True


# --------------------------------------------------------------- reparto
placed = []
def place(p, rot, var, h_scale):
    me = VARIANTS[var]
    ob = bpy.data.objects.new(f"B_{len(placed):04d}", me)
    BLK.objects.link(ob)
    ob.location = (p.x, p.y, 0)
    ob.rotation_euler = (0, 0, rot)
    ob.scale = (1, 1, h_scale)
    placed.append(ob)


R_MAX = 1350
# 1) Innere Stadt: trama medieval, densa e irregular
for gx in range(-700, 700, 50):
    for gy in range(-600, 700, 46):
        p = Vector((gx + rng.uniform(-6, 6), gy + rng.uniform(-6, 6)))
        if not inside(p, INNER):
            continue
        var = rng.choice([0, 2, 5, 5, 2])
        if not free(p, 20):
            continue
        rot = math.radians(rng.choice([-14, -6, 0, 8, 16]) + rng.uniform(-4, 4))
        place(p, rot, var, 1.08 + rng.uniform(-0.1, 0.1))

# 2) Vorstädte: cada sector de 30° tiene su cuadrícula girada (calles radiales y concéntricas)
CELL_X, CELL_Y = 66, 58
for k in range(12):
    a0 = -math.pi + k * math.pi / 6
    th = a0 + math.pi / 12                                          # eje del sector
    ux, uy = Vector((math.cos(th), math.sin(th))), Vector((-math.sin(th), math.cos(th)))
    for i in range(-2, int(R_MAX / CELL_X) + 2):
        for j in range(-int(R_MAX / CELL_Y) - 2, int(R_MAX / CELL_Y) + 2):
            p = ux * (i * CELL_X) + uy * (j * CELL_Y)
            ang = math.atan2(p.y, p.x)
            if not (a0 <= ang < a0 + math.pi / 6) or p.length > R_MAX or inside(p, INNER):
                continue
            var = rng.choice([1, 3, 4, 0, 1])
            if not free(p, 26):
                continue
            place(p, th + math.radians(rng.uniform(-1.5, 1.5)), var, 1.0 + rng.uniform(-0.06, 0.08))

# un padre común: el exportador glTF solo instancia (EXT_mesh_gpu_instancing) hermanos
grp = bpy.data.objects.new("CITY_BLOCKS", None)
BLK.objects.link(grp)
for ob in placed:
    ob.parent = grp
result = len(placed)
