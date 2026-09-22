# Plano base: Ringstraße, Donaukanal, Danubio, calles principales, parques y plazas.
# Coordenadas reales en metros (este, norte) desde el Stephansdom, comprimidas con S.
import math
exec(open(r"C:\Users\Baldo\Desktop\portfolio\vienna-3d\blender\vlib.py", encoding="utf-8").read())

mat("Ground", "FBFBFA"); mat("Road", "ECEAE6"); mat("Water", "D4D2CD"); mat("Park", "F3F2EE")


def catmull(pts, n=10):
    P = [Vector(p) for p in pts]
    out = []
    for i in range(len(P) - 1):
        p0 = P[max(i - 1, 0)]; p1 = P[i]; p2 = P[i + 1]; p3 = P[min(i + 2, len(P) - 1)]
        for k in range(n):
            t = k / n; t2, t3 = t * t, t * t * t
            out.append(0.5 * ((2 * p1) + (-p0 + p2) * t + (2 * p0 - 5 * p1 + 4 * p2 - p3) * t2
                              + (-p0 + 3 * p1 - 3 * p2 + p3) * t3))
    out.append(P[-1])
    return out


def ribbon(name, real_pts, width, z, material, coll="Streets", n=10):
    pts = catmull([to_map(e, nn) for e, nn in real_pts], n)
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    bm = bmesh.new(); L, R = [], []
    for i, p in enumerate(pts):
        a = pts[max(i - 1, 0)]; b = pts[min(i + 1, len(pts) - 1)]
        d = b - a; d.z = 0; d.normalize(); nv = Vector((-d.y, d.x, 0))
        L.append(bm.verts.new(p + nv * width / 2 + Vector((0, 0, z))))
        R.append(bm.verts.new(p - nv * width / 2 + Vector((0, 0, z))))
    for i in range(len(pts) - 1):
        bm.faces.new((L[i], R[i], R[i + 1], L[i + 1]))
    bm.to_mesh(me); bm.free()
    me.materials.clear(); me.materials.append(mat(material))
    ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, me)
    c = bpy.data.collections[coll]
    if ob.name not in c.objects:
        c.objects.link(ob)
    ob["path_real"] = str(real_pts)
    return ob


def area(name, real_pts, z, material, coll="Nature"):
    me = bpy.data.meshes.get(name) or bpy.data.meshes.new(name)
    bm = bmesh.new()
    bm.faces.new([bm.verts.new(to_map(e, n) + Vector((0, 0, z))) for e, n in real_pts])
    bm.to_mesh(me); bm.free()
    me.materials.clear(); me.materials.append(mat(material))
    ob = bpy.data.objects.get(name) or bpy.data.objects.new(name, me)
    c = bpy.data.collections[coll]
    if ob.name not in c.objects:
        c.objects.link(ob)
    return ob


# limpiar lo que hubiera del plano anterior (compresión 0,45)
for n in ["Ringstrasse", "Donaukanal", "Kanal_Kai", "Donau", "Praterstrasse", "Park_Stadtpark", "Park_Volksgarten",
          "Park_Burggarten", "Park_Rathauspark", "Square_Heldenplatz", "Park_Karlsplatz", "Park_Prater"]:
    if n in bpy.data.objects:
        bpy.data.objects.remove(bpy.data.objects[n], do_unlink=True)

RING = [(-133, 1034), (-500, 860), (-808, 690), (-897, 500), (-945, 167), (-960, -33), (-900, -300),
        (-822, -500), (-600, -640), (-378, -700), (-67, -801), (215, -834), (438, -500), (511, -222),
        (697, 167), (808, 356)]
CANAL = [(-1500, 2400), (-700, 1500), (-133, 1034), (348, 367), (808, 356), (1300, 50), (1900, -500)]
ribbon("Ringstrasse", RING, 46, 0.05, "Road")
ribbon("Kanal_Kai", CANAL, 80, 0.02, "Road")
ribbon("Donaukanal", CANAL, 42, 0.04, "Water")
ribbon("Donau", [(-1500, 5400), (700, 3500), (2300, 2400), (4200, 900)], 280, 0.04, "Water", "Nature")
ribbon("Praterstrasse", [(348, 367), (1000, 640), (1500, 830)], 30, 0.05, "Road", n=6)
ribbon("Kaerntner_Strasse", [(0, -40), (-120, -350), (-230, -660)], 18, 0.05, "Road", n=4)
ribbon("Graben", [(-60, 40), (-260, 110), (-330, 160)], 22, 0.05, "Road", n=4)
ribbon("Wiedner_Hauptstr", [(-120, -840), (-160, -1400)], 24, 0.05, "Road", n=3)

area("Park_Stadtpark", [(420, -560), (560, -420), (700, -120), (620, 60), (470, -200), (330, -520)], 0.03, "Park")
area("Park_Volksgarten", [(-880, 180), (-800, 220), (-700, -60), (-790, -130)], 0.03, "Park")
area("Park_Burggarten", [(-660, -520), (-560, -600), (-470, -500), (-570, -420)], 0.03, "Park")
area("Park_Rathauspark", [(-1100, 330), (-975, 330), (-985, 20), (-1100, 20)], 0.03, "Park")
area("Square_Heldenplatz", [(-840, -200), (-680, -90), (-560, -280), (-720, -400)], 0.03, "Road")
area("Park_Karlsplatz", [(-330, -870), (140, -870), (160, -1080), (-310, -1080)], 0.03, "Park")
area("Park_SigmundFreud", [(-1000, 640), (-880, 700), (-850, 560), (-960, 520)], 0.03, "Park")
area("Park_Prater", [(1150, 1400), (2800, 1400), (3400, 200), (2400, -600), (1200, 300)], 0.02, "Park")

# el Riesenrad en el Prater, eje este-oeste (se ve de frente desde el oeste)
rr = bpy.data.objects["RR_Root"]
rr.location = to_map(1692, 901)
rr.rotation_euler = (0, 0, math.radians(90))
result = "layout ok"
