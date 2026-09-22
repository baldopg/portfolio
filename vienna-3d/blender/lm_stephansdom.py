# Stephansdom: nave + coro con ábside, tejado empinado, fachada oeste con Heidentürme,
# torre sur (136,4 m) y torre norte con cúpula. Eje largo = X local (oeste -> este).
import math
exec(open(r"C:\Users\Baldo\Desktop\portfolio\vienna-3d\blender\vlib.py", encoding="utf-8").read())

root = landmark_root("Stephansdom", to_map(0, 0), rot_deg=0)
clear_children(root)
MATS = ["Paper", "Roof", "Ink"]
P, ROOF, INK = 0, 1, 2

# ---------------------------------------------------------------- cuerpo
body = Part("Steffl_Body", root, MATS)
W = 18.0                       # media anchura de la nave
X0, X1, XA = -38.0, 46.0, 57.0 # fachada oeste, arranque del ábside, punta del ábside
EAVE, RIDGE = 26.0, 60.0
# orden antihorario: sur (y-) de oeste a este, ábside, norte de este a oeste
foot = [(X0, -W), (X1, -W), (X1 + (XA - X1) * 0.7071, -W * 0.7071), (XA, 0.0),
        (X1 + (XA - X1) * 0.7071, W * 0.7071), (X1, W), (X0, W)]
body.extrude_poly(foot, 0, EAVE, P)

# tejado: dos aguas con remate a cuatro aguas sobre el ábside
rp = [(X0, -W - 0.8, EAVE), (X1, -W - 0.8, EAVE), (X1 + (XA - X1) * 0.7071 + 0.6, -W * 0.7071 - 0.6, EAVE),
      (XA + 0.8, 0, EAVE), (X1 + (XA - X1) * 0.7071 + 0.6, W * 0.7071 + 0.6, EAVE), (X1, W + 0.8, EAVE),
      (X0, W + 0.8, EAVE), (X0, 0, RIDGE), (X1, 0, RIDGE)]
body.faces_from(rp, [(0, 1, 8, 7), (5, 6, 7, 8), (1, 2, 8), (2, 3, 8), (3, 4, 8), (4, 5, 8), (6, 0, 7)], ROOF)

# contrafuertes y ventanales en los muros largos
for x in [X0 + 6 + 9 * i for i in range(10)]:
    for s in (-1, 1):
        body.box((x, s * (W + 1.2), EAVE / 2 - 1), (2.4, 2.4, EAVE - 2), P)
        body.frustum((x, s * (W + 1.2), 0), 1.2, 0.0, EAVE - 2, EAVE + 5, 4, P, rot=math.pi / 4)
        if x + 4.5 < X1:
            body.box((x + 4.5, s * (W + 0.08), 13.5), (3.2, 0.2, 15), INK)       # ventanal
# gabletes (Wimperge) sobre los aleros del muro sur
for x in [X0 + 10.5 + 9 * i for i in range(8)]:
    body.faces_from([(x - 3.6, -W - 0.4, EAVE), (x + 3.6, -W - 0.4, EAVE), (x, -W - 0.4, EAVE + 9),
                     (x - 3.6, -W + 0.6, EAVE), (x + 3.6, -W + 0.6, EAVE), (x, -W + 0.6, EAVE + 9)],
                    [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], P)
body.commit()

# ---------------------------------------------------------------- fachada oeste
west = Part("Steffl_West", root, MATS)
west.box((X0 - 3, 0, 16), (6, 2 * W - 6, 32), P)
west.faces_from([(X0 - 6, -8, 32), (X0 - 6, 8, 32), (X0 - 6, 0, 44), (X0, -8, 32), (X0, 8, 32), (X0, 0, 44)],
                [(0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)], P)
west.box((X0 - 6.2, 0, 7), (0.4, 7, 13), INK)                                  # Riesentor
for s in (-1, 1):                                                               # Heidentürme
    c = (X0 - 3, s * 11.5, 0)
    west.frustum(c, 5.4, 4.8, 0, 44, 8, P)
    west.frustum(c, 5.8, 5.8, 44, 45.2, 8, P)                                   # galería
    west.frustum(c, 4.6, 0.0, 45.2, 65, 8, P)
    for k in range(8):                                                          # ventanas por planta
        a = math.pi / 8 + 2 * math.pi * k / 8
        for z in (18, 30):
            west.box((c[0] + 5.0 * math.cos(a), c[1] + 5.0 * math.sin(a), z), (0.4, 1.2, 4.5), INK, rot_z=a)
    # capillas de las esquinas oeste con tejado piramidal
    west.box((X0 + 6, s * (W + 5), 11), (13, 10, 22), P)
    west.frustum((X0 + 6, s * (W + 5), 22), 8.8, 0.0, 0, 13, 4, ROOF, rot=math.pi / 4)
west.commit()

# ---------------------------------------------------------------- torre sur (Steffl)
def tower_pinnacles(part, c, r, z, h, n=4, rot=math.pi / 4):
    for k in range(n):
        a = rot + 2 * math.pi * k / n
        part.frustum((c[0] + r * math.cos(a), c[1] + r * math.sin(a), 0), 0.9, 0.0, z, z + h, 4, P)

south = Part("Steffl_SouthTower", root, MATS)
c = (6.0, -W - 9.0, 0)
south.frustum(c, 10.5, 9.6, 0, 40, 4, P, rot=math.pi / 4)       # base cuadrada (~14 m de lado)
tower_pinnacles(south, c, 9.4, 40, 9)
for s in (-1, 1):                                                  # gabletes de la base
    south.faces_from([(c[0] - 4, c[1] + s * 6.9, 36), (c[0] + 4, c[1] + s * 6.9, 36), (c[0], c[1] + s * 6.9, 47),
                      (c[0] - 4, c[1] + s * 6.2, 36), (c[0] + 4, c[1] + s * 6.2, 36), (c[0], c[1] + s * 6.2, 47)],
                     [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], P)
south.frustum(c, 8.6, 7.4, 40, 72, 8, P)
tower_pinnacles(south, c, 7.6, 72, 10, 8, rot=math.pi / 8)
south.frustum(c, 7.2, 5.2, 72, 100, 8, P)
tower_pinnacles(south, c, 5.4, 100, 8, 8, rot=math.pi / 8)
south.frustum(c, 5.0, 0.0, 100, 136.4, 8, P)
south.box((c[0], c[1] - 6.95, 22), (2.6, 0.3, 16), INK)            # gran ventanal sur
south.box((c[0], c[1] - 5.6, 56), (1.8, 0.3, 12), INK)
south.commit()

# ---------------------------------------------------------------- torre norte (Adlerturm)
north = Part("Steffl_NorthTower", root, MATS)
c = (6.0, W + 8.0, 0)
north.frustum(c, 9.6, 8.8, 0, 56, 4, P, rot=math.pi / 4)
north.frustum(c, 5.6, 5.2, 56, 61, 8, P)
north.dome(c, 5.2, 61, 5.0, rings=6, sides=16, mi=ROOF, lantern=(1.4, 2.4))
north.commit()
result = [o.name for o in root.children]
