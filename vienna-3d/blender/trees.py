# Árboles: alineaciones de la Ringstraße y relleno de parques (copias enlazadas de un prototipo).
import math, random
exec(open(r"C:\Users\Baldo\Desktop\portfolio\vienna-3d\blender\vlib.py", encoding="utf-8").read())
rng = random.Random(1857)
NAT = bpy.data.collections["Nature"]
for o in list(NAT.objects):
    if o.name.startswith("T_") or o.name in ("TREE_PROTO", "CITY_TREES"):
        bpy.data.objects.remove(o, do_unlink=True)
TREES = bpy.data.objects.new("CITY_TREES", None)   # padre común -> instancias GPU al exportar
NAT.objects.link(TREES)

# prototipo: copa en papel + tronco en tinta
proto_root = bpy.data.objects.get("BLOCK_PROTOS")
t = Part("Tree", proto_root, ["Paper", "Ink"])
t.frustum((0, 0, 0), 0.28, 0.2, 0, 4.2, 6, 1)
bm = t.bm
r = bmesh.ops.create_icosphere(bm, subdivisions=1, radius=3.6)
bmesh.ops.transform(bm, matrix=Matrix.Translation((0, 0, 7.2)) @ Matrix.Diagonal((1, 1, 1.15, 1)), verts=r["verts"])
tree_me = t.commit(coll="Nature").data
bpy.data.objects["Tree"].name = "TREE_PROTO"


def plant(x, y, s=1.0):
    ob = bpy.data.objects.new(f"T_{len(NAT.objects):05d}", tree_me)
    NAT.objects.link(ob)
    ob.parent = TREES
    ob.location = (x, y, 0)
    ob.rotation_euler = (0, 0, rng.uniform(0, 6.28))
    ob.scale = (s, s, s * rng.uniform(0.9, 1.1))


def resample(line, step):
    out = []
    for i in range(len(line) - 1):
        a, b = line[i], line[i + 1]
        n = max(1, int((b - a).length / step))
        for k in range(n):
            out.append((a.lerp(b, k / n), (b - a).normalized()))
    return out


def catmull2(pts, n=10):
    P = [Vector(p) for p in pts]; out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for k in range(n):
            tt = k / n; t2, t3 = tt * tt, tt * tt * tt
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * tt + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-1]); return out


RING = [(-133, 1034), (-500, 860), (-808, 690), (-897, 500), (-945, 167), (-960, -33), (-900, -300),
        (-822, -500), (-600, -640), (-378, -700), (-67, -801), (215, -834), (438, -500), (511, -222),
        (697, 167), (808, 356)]
ring = [v.to_2d() for v in catmull2([to_map(e, n) for e, n in RING])]
for p, d in resample(ring, 13):
    nrm = Vector((-d.y, d.x))
    for off in (-19, -8.5, 8.5, 19):                                 # cuatro filas: aceras y paseo central
        q = p + nrm * off
        plant(q.x, q.y, 0.85 if abs(off) < 10 else 1.0)

# parques: relleno aleatorio dentro de cada polígono
def inside(p, poly):
    c = False; j = len(poly) - 1
    for i in range(len(poly)):
        if ((poly[i].y > p.y) != (poly[j].y > p.y)) and \
                (p.x < (poly[j].x - poly[i].x) * (p.y - poly[i].y) / (poly[j].y - poly[i].y + 1e-12) + poly[i].x):
            c = not c
        j = i
    return c


for o in NAT.objects:
    if o.type == 'MESH' and o.name.startswith("Park_") and o.name != "Park_Prater":
        poly = [(o.matrix_world @ v.co).to_2d() for v in o.data.vertices]
        xs = [v.x for v in poly]; ys = [v.y for v in poly]
        area = (max(xs) - min(xs)) * (max(ys) - min(ys))
        for _ in range(int(area / 260)):
            q = Vector((rng.uniform(min(xs), max(xs)), rng.uniform(min(ys), max(ys))))
            if inside(q, poly):
                plant(q.x, q.y, rng.uniform(0.9, 1.4))
# Prater: arboleda alrededor del Riesenrad y la Hauptallee
rr = bpy.data.objects["RR_Root"].location.to_2d()
for _ in range(900):
    q = rr + Vector((rng.uniform(-60, 900), rng.uniform(-500, 420)))
    if (q - rr).length > 110:
        plant(q.x, q.y, rng.uniform(1.0, 1.6))
result = sum(1 for o in NAT.objects if o.name.startswith("T_"))
