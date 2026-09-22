# Monumentos de la Ringstraße y alrededores. Cada función construye uno.
# Convención: la fachada principal mira a -Y local; face_to() la orienta en el plano.
import math
exec(open(r"C:\Users\Baldo\Desktop\portfolio\vienna-3d\blender\vlib.py", encoding="utf-8").read())
mat("Paper", "F4F2EE"); mat("Roof", "C9C6C0"); mat("Ink", "111111")
MATS = ["Paper", "Roof", "Ink"]
P, ROOF, INK = 0, 1, 2


def pediment(part, x0, x1, y0, y1, z, h, mi=P):
    """Frontón triangular sobre una fachada (entre x0 y x1, de y0 a y1)."""
    xm = (x0 + x1) / 2
    part.faces_from([(x0, y0, z), (x1, y0, z), (xm, y0, z + h), (x0, y1, z), (x1, y1, z), (xm, y1, z + h)],
                    [(0, 1, 2), (5, 4, 3), (0, 3, 4, 1), (1, 4, 5, 2), (2, 5, 3, 0)], mi)


# ------------------------------------------------------------------ Staatsoper
def build_oper():
    root = landmark_root("Staatsoper", to_map(-304, -612))
    face_to(root, -420, -740)                 # la logia mira al Opernring
    clear_children(root)
    p = Part("Oper_Body", root, MATS)
    p.box((0, 0, 11), (66, 96, 22), P)                            # cuerpo principal
    p.box((0, -52, 13), (40, 12, 26), P)                          # bloque de la logia
    p.box((0, -52, 27.5), (34, 10, 3), P)                         # ático
    for s in (-1, 1):
        p.box((s * 27.5, -48, 10), (15, 16, 20), P)               # alas delanteras
        p.windows(s * 20 - 7 if s > 0 else -35, s * 35 if s > 0 else -20, -56.1, [5, 13], 2, 1.8, 3.6, INK)
        p.box((s * 19, -57, 32), (3, 3, 5), INK)                  # grupos escultóricos (Pegasos)
    # logia: 5 arcos abajo (pórtico) y 5 arriba (galería)
    for i in range(5):
        x = -14 + 7 * i
        p.arch(x, -58.1, 9, 4.6, 7, INK)
        p.arch(x, -58.1, 21.5, 4.6, 8, INK)
    p.colonnade(-17.5, 17.5, -58.6, 13, 9, 6, 0.55, P)
    p.windows(-31, 31, 48.1, [5, 12, 18], 12, 1.6, 3.2, INK)      # fachada trasera
    p.windows_x(-40, 44, 33.1, [5, 12, 18], 14, 1.6, 3.2, INK)
    p.windows_x(-40, 44, -33.1, [5, 12, 18], 14, 1.6, 3.2, INK)
    p.commit()
    r = Part("Oper_Roofs", root, MATS)
    r.dome((0, -24, 0), 24, 22, 13, rings=6, sides=28, mi=ROOF)   # cubierta curva de la sala
    r.box((0, 14, 33), (42, 30, 22), P)                           # caja escénica
    r.gable_roof((0, 14, 0), 42, 30, 44, 50, ROOF, rot_z=0)
    r.gable_roof((0, 0, 0), 64, 94, 22, 26, ROOF, hip=20)
    r.commit()


# ------------------------------------------------------------------ Karlskirche
def build_karlskirche():
    root = landmark_root("Karlskirche", to_map(-89, -1134))
    face_to(root, -89, -800)                  # mira al norte, hacia la ciudad
    clear_children(root)
    p = Part("Karl_Body", root, MATS)
    # pórtico hexástilo con frontón
    p.box((0, -27, 1.25), (24, 10, 2.5), P)
    p.colonnade(-9.5, 9.5, -30, 2.5, 15, 6, 0.8, P)
    p.box((0, -28.5, 19), (23, 7, 3), P)
    pediment(p, -11.5, 11.5, -32, -25, 20.5, 6)
    p.box((0, -20, 12), (26, 12, 24), P)                          # vestíbulo
    p.box((0, -17, 11), (82, 12, 22), P)                          # fachada ancha
    # cuerpo oval con tambor y cúpula
    p.frustum((0, 6, 0), 16, 16, 0, 30, 24, P)
    p.frustum((0, 6, 0), 12, 12, 30, 44, 24, P)
    for k in range(8):
        a = 2 * math.pi * k / 8
        p.box((12.05 * math.cos(a), 6 + 12.05 * math.sin(a), 37), (0.3, 2.2, 6), INK, rot_z=a)
    p.dome((0, 6, 0), 12.5, 44, 17, rings=8, sides=28, mi=ROOF, lantern=(2.4, 5))
    p.box((0, 30, 13), (22, 26, 26), P)                           # coro
    p.gable_roof((0, 30, 0), 22, 26, 26, 32, ROOF, rot_z=math.pi / 2)
    # columnas triunfales (47 m) y pabellones laterales
    for s in (-1, 1):
        x = s * 22
        p.box((x, -24, 4), (8, 8, 8), P)
        p.frustum((x, -24, 0), 3.4, 3.1, 8, 41, 16, P)
        for z in range(11, 40, 4):                               # relieve en espiral sugerido con anillos
            p.frustum((x, -24, 0), 3.55, 3.5, z, z + 0.6, 16, P)
        p.box((x, -24, 42), (7.5, 7.5, 2), P)
        p.frustum((x, -24, 0), 2.2, 2.2, 43, 45.5, 8, P)
        p.dome((x, -24, 0), 2.4, 45.5, 2, rings=4, sides=12, mi=ROOF, lantern=(0.6, 1.2))
        px = s * 35
        p.box((px, -17, 13.5), (14, 14, 27), P)
        p.arch(px, -24.1, 9, 5, 8, INK)                          # arco de paso
        p.frustum((px, -17, 27), 8.5, 4.0, 0, 4, 4, ROOF, rot=math.pi / 4)
        p.dome((px, -17, 0), 3.2, 31, 2.5, rings=4, sides=12, mi=ROOF, lantern=(0.8, 1.5))
    p.commit()
    # estanque delante (Karlsplatz)
    w = Part("Karl_Pond", root, ["Water"])
    w.box((0, -62, 0.08), (36, 22, 0.1), 0)
    w.commit()


# ------------------------------------------------------------------ Secession
def build_secession():
    root = landmark_root("Secession", to_map(-549, -912))
    face_to(root, -380, -760)                 # entrada hacia la Friedrichstraße / Oper
    clear_children(root)
    p = Part("Secession_Body", root, MATS)
    p.box((0, 12, 5.5), (32, 34, 11), P)                          # nave de exposiciones
    p.box((0, -12, 5), (44, 12, 10), P)                           # frente bajo
    p.box((0, -12, 7.5), (24, 16, 15), P)                         # bloque de entrada
    for sx in (-1, 1):
        for sy in (-1, 1):
            p.box((sx * 8.8, -12 + sy * 5.2, 17), (5.2, 4.2, 4), P)   # pilonos que abrazan la cúpula
    p.box((0, -20.2, 3.2), (3.4, 0.3, 5), INK)                    # puerta
    p.box((0, -20.2, 11.5), (13, 0.2, 1.2), INK)                  # inscripción
    p.commit()
    d = Part("Secession_Laurel", root, ["Ink"])
    d.dome((0, -12, 0), 5.6, 15.5, 5.6, rings=6, sides=20, mi=0)  # cúpula de laurel (en tinta)
    d.commit()


# ------------------------------------------------------------------ Parlamento
def build_parlament():
    root = landmark_root("Parlament", to_map(-1083, -33))
    face_to(root, -900, -33)                  # mira al este, al Ring
    clear_children(root)
    p = Part("Parl_Body", root, MATS)
    p.box((0, 0, 4), (140, 100, 8), P)                            # basamento rústico
    p.box((0, 0, 15), (136, 96, 14), P)
    p.windows(-66, -24, -48.1, [5.5], 9, 1.6, 2.6, INK)
    p.windows(24, 66, -48.1, [5.5], 9, 1.6, 2.6, INK)
    p.windows(-66, -26, -48.1, [13.5, 18.5], 9, 1.6, 3, INK)
    p.windows(26, 66, -48.1, [13.5, 18.5], 9, 1.6, 3, INK)
    # pórtico central sobre podio, con frontón
    p.box((0, -56, 4), (40, 16, 8), P)
    p.colonnade(-16, 16, -62, 8, 13, 8, 0.8, P)
    p.box((0, -59, 22.5), (38, 10, 3), P)
    pediment(p, -19, 19, -64, -54, 24, 7)
    p.box((0, -26, 18), (44, 44, 36), P)                          # sala central
    p.gable_roof((0, -26, 0), 44, 44, 36, 42, ROOF, rot_z=math.pi / 2)
    # pabellones de esquina con pórtico
    for s in (-1, 1):
        x = s * 60
        p.box((x, -46, 13), (22, 14, 26), P)
        p.colonnade(x - 7, x + 7, -53.5, 8, 12, 4, 0.6, P)
        pediment(p, x - 10, x + 10, -54, -44, 26, 5)
        p.box((x, -46, 30), (3, 3, 5), INK)                       # cuadrigas
    # rampas curvas y la fuente de Palas Atenea
    for s in (-1, 1):
        p.faces_from([(s * 22, -64, 8), (s * 34, -64, 8), (s * 44, -100, 0), (s * 30, -100, 0),
                      (s * 22, -64, 0), (s * 34, -64, 0)],
                     [(0, 1, 2, 3), (4, 0, 3), (5, 2, 1), (4, 5, 1, 0)] if s > 0 else [(3, 2, 1, 0), (3, 0, 4), (1, 2, 5), (0, 1, 5, 4)], P)
    p.frustum((0, -84, 0), 5, 5, 0, 1.2, 16, P)
    p.box((0, -84, 4), (2.4, 2.4, 6), P)
    p.frustum((0, -84, 0), 0.7, 0.4, 7, 12, 8, INK)
    p.commit()
    r = Part("Parl_Roofs", root, MATS)
    r.gable_roof((0, 0, 0), 136, 96, 22, 27, ROOF, hip=30)
    r.commit()


# ------------------------------------------------------------------ Rathaus
def build_rathaus():
    root = landmark_root("Rathaus", to_map(-1172, 256))
    face_to(root, -950, 256)                  # mira al este, al Rathauspark
    clear_children(root)
    p = Part("Rathaus_Body", root, MATS)
    # bloque perimetral con patio
    p.box((0, -56, 13), (150, 16, 26), P)
    p.box((0, 56, 13), (150, 16, 26), P)
    p.box((-67, 0, 13), (16, 96, 26), P)
    p.box((67, 0, 13), (16, 96, 26), P)
    p.box((0, 0, 13), (16, 96, 26), P)                            # ala central (patios)
    for i in range(15):                                           # arcada en planta baja
        x = -63 + 9 * i
        if abs(x) > 7:
            p.arch(x, -64.2, 6, 5, 4.5, INK)
    p.windows(-72, -8, -64.1, [11, 17, 22], 8, 1.8, 3.6, INK)
    p.windows(8, 72, -64.1, [11, 17, 22], 8, 1.8, 3.6, INK)
    # torre central (98 m + Rathausmann)
    p.box((0, -60, 35), (14, 14, 70), P)
    p.arch(0, -67.2, 28, 6, 10, INK)
    p.frustum((0, -67.4, 0), 2.2, 2.2, 52, 52.3, 16, INK)          # reloj (disco)
    p.frustum((0, -60, 0), 8, 6.5, 70, 80, 8, P)
    p.frustum((0, -60, 0), 6.5, 0.0, 80, 98, 8, P)
    for k in range(8):
        a = math.pi / 8 + 2 * math.pi * k / 8
        p.frustum((7.6 * math.cos(a), -60 + 7.6 * math.sin(a), 0), 0.7, 0.0, 70, 78, 4, P)
    p.frustum((0, -60, 0), 0.5, 0.3, 98, 103.5, 6, INK)             # Rathausmann
    # cuatro torres menores (61 m)
    for x in (-40, -20, 20, 40):
        p.box((x, -60, 20), (6, 6, 40), P)
        p.frustum((x, -60, 0), 3.6, 3.0, 40, 48, 8, P)
        p.frustum((x, -60, 0), 3.0, 0.0, 48, 61, 8, P)
    p.commit()
    r = Part("Rathaus_Roofs", root, MATS)
    for y in (-56, 56):
        r.gable_roof((0, y, 0), 150, 16, 26, 33, ROOF)
    for x in (-67, 0, 67):
        r.gable_roof((x, 0, 0), 96, 16, 26, 33, ROOF, rot_z=math.pi / 2)
    for sx in (-1, 1):                                             # pabellones de esquina, tejados empinados
        r.box((sx * 68, -56, 15), (18, 18, 30), P)
        r.frustum((sx * 68, -56, 30), 13, 3, 0, 12, 4, ROOF, rot=math.pi / 4)
    r.commit()


# ------------------------------------------------------------------ Burgtheater
def build_burgtheater():
    root = landmark_root("Burgtheater", to_map(-868, 211))
    face_to(root, -1000, 211)                 # mira al oeste, al Ring y al Rathaus
    clear_children(root)
    p = Part("Burg_Body", root, MATS)
    p.frustum((0, -4, 0), 30, 30, 0, 22, 32, P)                   # frente curvo de la sala
    p.box((0, 8, 11), (60, 26, 22), P)
    p.box((0, -32, 14), (26, 10, 28), P)                          # cuerpo central con ático
    p.colonnade(-10, 10, -37.5, 10, 10, 6, 0.6, P)
    for i in range(3):
        p.arch(-7 + 7 * i, -37.2, 5.5, 3.6, 4.5, INK)
    for k in range(13):                                           # ventanas del frente curvo
        a = math.pi + math.pi * (k + 0.5) / 13
        if abs(math.cos(a)) > 0.45:
            p.box((30.05 * math.cos(a), -4 + 30.05 * math.sin(a), 13), (2.2, 0.3, 4), INK, rot_z=a + math.pi / 2)
    for s in (-1, 1):                                             # alas de las escaleras
        p.box((s * 50, 0, 10), (40, 34, 20), P)
        p.windows(s * 50 - 17, s * 50 + 17, -17.1, [6, 13], 6, 1.8, 3.4, INK)
        p.box((s * 66, 0, 12), (12, 36, 24), P)
        p.frustum((s * 66, 0, 24), 9, 4, 0, 5, 4, ROOF, rot=math.pi / 4)
    p.box((0, -32, 30), (3, 3, 4), INK)                           # grupo escultórico
    p.commit()
    r = Part("Burg_Roofs", root, MATS)
    r.dome((0, -4, 0), 28, 22, 7, rings=5, sides=32, mi=ROOF)
    r.gable_roof((0, 22, 0), 56, 20, 22, 30, ROOF)
    r.commit()


# ------------------------------------------------------------------ Votivkirche
def build_votivkirche():
    root = landmark_root("Votivkirche", to_map(-1054, 778))
    face_to(root, -900, 600)                  # fachada hacia el Sigmund-Freud-Park
    clear_children(root)
    p = Part("Votiv_Body", root, MATS)
    p.box((0, 8, 12), (28, 84, 24), P)                            # nave
    p.box((0, 24, 12), (56, 18, 24), P)                           # crucero
    p.box((0, -34.5, 16), (22, 3, 32), P)                         # fachada entre torres
    pediment(p, -10, 10, -36, -33, 32, 9)
    p.frustum((0, -36.1, 0), 4, 4, 22, 22.3, 20, INK)             # rosetón
    p.arch(0, -36.2, 9, 5, 6, INK)
    for s in (-1, 1):                                             # torres de 99 m
        x = s * 11
        p.box((x, -34, 23), (10, 10, 46), P)
        p.arch(x, -39.2, 30, 3, 8, INK)
        p.frustum((x, -34, 0), 5.6, 4.8, 46, 64, 8, P)
        for k in range(8):
            a = math.pi / 8 + 2 * math.pi * k / 8
            p.box((x + 5.1 * math.cos(a), -34 + 5.1 * math.sin(a), 56), (0.3, 1.6, 12), INK, rot_z=a)
        p.frustum((x, -34, 0), 4.6, 0.0, 64, 99, 8, P)
        for k in range(4):
            a = math.pi / 4 + math.pi / 2 * k
            p.frustum((x + 6 * math.cos(a), -34 + 6 * math.sin(a), 0), 0.8, 0.0, 46, 56, 4, P)
    for y in range(-26, 50, 9):                                   # ventanales laterales
        for s in (-1, 1):
            p.box((s * 14.1, y, 13), (0.3, 3, 12), INK)
    p.frustum((0, 24, 0), 1.6, 0.0, 38, 55, 8, P)                 # aguja del crucero
    p.commit()
    r = Part("Votiv_Roofs", root, MATS)
    r.gable_roof((0, 10, 0), 80, 28, 24, 40, ROOF, rot_z=math.pi / 2)
    r.gable_roof((0, 24, 0), 56, 18, 24, 37, ROOF)
    r.commit()


# ------------------------------------------------------------------ Donauturm
def build_donauturm():
    root = landmark_root("Donauturm", to_map(2760, 3525))
    clear_children(root)
    p = Part("Donauturm", root, MATS)
    p.frustum((0, 0, 0), 6.5, 4.2, 0, 150, 16, P)                 # fuste
    p.frustum((0, 0, 0), 8, 15, 150, 156, 24, P)                  # cesta
    p.frustum((0, 0, 0), 15, 15, 156, 163, 24, P)
    p.windows_band = None
    for k in range(24):
        a = 2 * math.pi * k / 24
        p.box((15.05 * math.cos(a), 15.05 * math.sin(a), 159.5), (0.3, 3.2, 4.5), INK, rot_z=a)
    p.frustum((0, 0, 0), 15, 12, 163, 168, 24, P)
    p.frustum((0, 0, 0), 12, 5, 168, 172, 24, P)
    p.frustum((0, 0, 0), 2.2, 1.2, 172, 230, 8, P)                # mástil
    p.frustum((0, 0, 0), 0.8, 0.2, 230, 252, 6, INK)
    p.box((0, 0, 3), (22, 22, 6), P)                              # pabellón de la base
    p.commit()
