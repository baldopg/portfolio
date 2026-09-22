"""Helpers para construir la Viena del portfolio en Blender.

Uso dentro de Blender:  exec(open(VLIB).read())
Convenciones: X = este, Y = norte, Z = arriba, metros reales.
Cada monumento es un Empty "LM_<Nombre>" con sus piezas como hijos,
así se puede mover o girar entero sin tocar la geometría.
"""
import bpy, bmesh, math
from mathutils import Vector, Matrix

S = 0.6  # compresión del plano: distancias reales * S; los edificios van 1:1


def srgb(h):
    h = h.lstrip('#')
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    return tuple((x / 12.92) if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c)


def mat(name, hexc=None):
    m = bpy.data.materials.get(name)
    if m is None:
        m = bpy.data.materials.new(name)
        m.use_nodes = True
    if hexc:
        rgb = srgb(hexc)
        m.node_tree.nodes["Principled BSDF"].inputs["Base Color"].default_value = (*rgb, 1)
        m.diffuse_color = (*rgb, 1)
    return m


def set_material_indices(me, idx):
    attr = me.attributes.get("material_index")
    if attr is None:
        attr = me.attributes.new("material_index", 'INT', 'FACE')
    attr.data.foreach_set("value", idx)
    me.update()


def to_map(e, n):
    """Coordenadas reales en metros (este, norte) desde el Stephansdom -> escena."""
    return Vector((e * S, n * S, 0))


def landmark_root(name, loc, rot_deg=0.0, coll="Landmarks"):
    root = bpy.data.objects.get("LM_" + name)
    if root is None:
        root = bpy.data.objects.new("LM_" + name, None)
        bpy.data.collections[coll].objects.link(root)
    root.location = loc
    root.rotation_euler = (0, 0, math.radians(rot_deg))
    root.empty_display_size = 10
    return root


def face_to(root, e, n):
    """Gira el monumento para que su fachada principal (-Y local) mire al punto real (e, n)."""
    t = to_map(e, n)
    d = Vector((t.x - root.location.x, t.y - root.location.y))
    root.rotation_euler = (0, 0, math.atan2(d.x, -d.y))


def clear_children(root):
    for ch in list(root.children):
        bpy.data.objects.remove(ch, do_unlink=True)


class Part:
    """Acumula geometría en un bmesh con varios materiales y la vuelca a un objeto."""

    def __init__(self, name, root, mats):
        self.name, self.root, self.mats = name, root, mats
        self.bm = bmesh.new()

    # --- primitivas -------------------------------------------------
    def box(self, c, size, mi=0, rot_z=0.0):
        r = bmesh.ops.create_cube(self.bm, size=1.0)
        M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(rot_z, 4, 'Z') @ Matrix.Diagonal((*size, 1))
        bmesh.ops.transform(self.bm, matrix=M, verts=r["verts"])
        self._mi(r["verts"], mi)
        return r

    def frustum(self, c, r0, r1, z0, z1, sides=8, mi=0, rot=None, cap_top=True):
        """Tronco de pirámide/cono. r = radio del círculo circunscrito."""
        rot = (math.pi / sides) if rot is None else rot
        c = Vector(c)
        bot = [self.bm.verts.new(c + Vector((r0 * math.cos(rot + 2 * math.pi * i / sides),
                                              r0 * math.sin(rot + 2 * math.pi * i / sides), z0)))
               for i in range(sides)]
        if r1 <= 1e-4:
            tip = self.bm.verts.new(c + Vector((0, 0, z1)))
            faces = [self.bm.faces.new((bot[i], bot[(i + 1) % sides], tip)) for i in range(sides)]
        else:
            top = [self.bm.verts.new(c + Vector((r1 * math.cos(rot + 2 * math.pi * i / sides),
                                                  r1 * math.sin(rot + 2 * math.pi * i / sides), z1)))
                   for i in range(sides)]
            faces = [self.bm.faces.new((bot[i], bot[(i + 1) % sides], top[(i + 1) % sides], top[i]))
                     for i in range(sides)]
            if cap_top:
                faces.append(self.bm.faces.new(top))
        faces.append(self.bm.faces.new(list(reversed(bot))))
        for f in faces:
            f.material_index = mi
        return faces

    def gable_roof(self, c, length, width, h_eave, h_ridge, mi=0, rot_z=0.0, hip=0.0):
        """Tejado a dos aguas sobre un rectángulo centrado en c (eje largo = X local).
        hip > 0 recorta los hastiales (tejado a cuatro aguas)."""
        L, W = length / 2, width / 2
        pts = [(-L, -W, h_eave), (L, -W, h_eave), (L, W, h_eave), (-L, W, h_eave),
               (-L + hip, 0, h_ridge), (L - hip, 0, h_ridge)]
        M = Matrix.Translation(Vector(c)) @ Matrix.Rotation(rot_z, 4, 'Z')
        v = [self.bm.verts.new(M @ Vector(p)) for p in pts]
        fs = [self.bm.faces.new((v[0], v[1], v[5], v[4])), self.bm.faces.new((v[2], v[3], v[4], v[5])),
              self.bm.faces.new((v[1], v[2], v[5])), self.bm.faces.new((v[3], v[0], v[4])),
              self.bm.faces.new((v[3], v[2], v[1], v[0]))]
        for f in fs:
            f.material_index = mi
        return fs

    def dome(self, c, r, z0, h, rings=8, sides=24, mi=0, lantern=None):
        """Cúpula (media elipse de revolución) con linterna opcional (radio, alto)."""
        c = Vector(c)
        prev = None
        for k in range(rings + 1):
            a = (math.pi / 2) * k / rings
            rr, zz = r * math.cos(a), z0 + h * math.sin(a)
            if k == rings:
                rr = max(rr, 1e-3)
            ring = [self.bm.verts.new(c + Vector((rr * math.cos(2 * math.pi * i / sides),
                                                   rr * math.sin(2 * math.pi * i / sides), zz)))
                    for i in range(sides)]
            if prev:
                for i in range(sides):
                    f = self.bm.faces.new((prev[i], prev[(i + 1) % sides], ring[(i + 1) % sides], ring[i]))
                    f.material_index = mi
            prev = ring
        f = self.bm.faces.new(prev)
        f.material_index = mi
        if lantern:
            lr, lh = lantern
            top = z0 + h
            self.frustum(c, lr, lr * 0.9, top - 0.2, top + lh, 8, mi)
            self.frustum(c, lr * 0.9, 0, top + lh, top + lh * 1.8, 8, mi)

    def extrude_poly(self, pts, z0, z1, mi=0, mi_top=None):
        """Prisma vertical a partir de un polígono 2D (lista de (x, y) en sentido antihorario)."""
        bot = [self.bm.verts.new((x, y, z0)) for x, y in pts]
        top = [self.bm.verts.new((x, y, z1)) for x, y in pts]
        n = len(pts)
        fs = [self.bm.faces.new((bot[i], bot[(i + 1) % n], top[(i + 1) % n], top[i])) for i in range(n)]
        for f in fs:
            f.material_index = mi
        ft = self.bm.faces.new(top)
        ft.material_index = mi if mi_top is None else mi_top
        fb = self.bm.faces.new(list(reversed(bot)))
        fb.material_index = mi
        return fs

    def faces_from(self, pts3, quads, mi=0):
        """Malla libre: lista de puntos 3D e índices de caras."""
        v = [self.bm.verts.new(p) for p in pts3]
        out = []
        for q in quads:
            f = self.bm.faces.new([v[i] for i in q])
            f.material_index = mi
            out.append(f)
        return out

    def colonnade(self, x0, x1, y, z0, h, n, r=0.6, mi=0, cap=True):
        """n columnas repartidas entre x0 y x1 sobre el plano y."""
        for i in range(n):
            x = x0 + (x1 - x0) * (i / (n - 1) if n > 1 else 0.5)
            self.frustum((x, y, 0), r, r * 0.88, z0, z0 + h, 8, mi)
            if cap:
                self.box((x, y, z0 + h + 0.25), (r * 2.6, r * 2.6, 0.5), mi)

    def _quad(self, pts, mi):
        f = self.bm.faces.new([self.bm.verts.new(p) for p in pts])
        f.material_index = mi

    def windows(self, x0, x1, y, zs, n, w=1.4, h=2.4, mi=2, depth=0.15, arched=False, quad=False):
        """Filas de ventanas sobre el plano de fachada y. quad=True: un solo cuadrado mirando
        hacia fuera (signo de y), 2 triángulos en vez de 12; para las manzanas genéricas."""
        for z in zs:
            for i in range(n):
                x = x0 + (x1 - x0) * ((i + 0.5) / n)
                if quad:
                    a, b, c, d = (x - w / 2, y, z - h / 2), (x + w / 2, y, z - h / 2), (x + w / 2, y, z + h / 2), (x - w / 2, y, z + h / 2)
                    self._quad((a, b, c, d) if y < 0 else (d, c, b, a), mi)
                    continue
                self.box((x, y, z), (w, depth, h), mi)
                if arched:
                    self.frustum((x, y, 0), w / 2, 0.0, z + h / 2, z + h / 2 + w / 2, 6, mi, rot=0)

    def windows_x(self, y0, y1, x, zs, n, w=1.4, h=2.4, mi=2, depth=0.15, quad=False):
        """Igual que windows pero sobre un plano de fachada x (fachadas laterales)."""
        for z in zs:
            for i in range(n):
                y = y0 + (y1 - y0) * ((i + 0.5) / n)
                if quad:
                    a, b, c, d = (x, y + w / 2, z - h / 2), (x, y - w / 2, z - h / 2), (x, y - w / 2, z + h / 2), (x, y + w / 2, z + h / 2)
                    self._quad((a, b, c, d) if x < 0 else (d, c, b, a), mi)
                    continue
                self.box((x, y, z), (depth, w, h), mi)

    def arch(self, x, y, z_spring, w, h_rect, mi=2, depth=0.3, axis='X', segs=10):
        """Hueco de arco de medio punto: rectángulo + semicírculo (plano de fachada y o x)."""
        r = w / 2
        z0 = z_spring - h_rect
        pts = [(-r, z0), (r, z0)] + [(r * math.cos(math.pi * k / segs), z_spring + r * math.sin(math.pi * k / segs))
                                     for k in range(segs + 1)]
        def P3(u, zz, d):
            return (x + u, y + d, zz) if axis == 'X' else (x + d, y + u, zz)
        front = [self.bm.verts.new(P3(u, zz, -depth / 2)) for u, zz in pts]
        back = [self.bm.verts.new(P3(u, zz, depth / 2)) for u, zz in pts]
        n = len(pts)
        fs = [self.bm.faces.new(front), self.bm.faces.new(list(reversed(back)))]
        for i in range(n):
            fs.append(self.bm.faces.new((front[i], front[(i + 1) % n], back[(i + 1) % n], back[i])))
        for f in fs:
            f.material_index = mi

    def _mi(self, verts, mi):
        for f in {f for v in verts for f in v.link_faces}:
            f.material_index = mi

    # --- salida -----------------------------------------------------
    def commit(self, coll="Landmarks"):
        me = bpy.data.meshes.get(self.name) or bpy.data.meshes.new(self.name)
        bmesh.ops.remove_doubles(self.bm, verts=self.bm.verts, dist=1e-4)
        self.bm.normal_update()
        idx = [f.material_index for f in self.bm.faces]
        self.bm.to_mesh(me)
        self.bm.free()
        me.materials.clear()
        for m in self.mats:
            me.materials.append(mat(m))
        # Blender 5.1 beta no conserva material_index al pasar de bmesh a malla: se reescribe
        set_material_indices(me, idx)
        ob = bpy.data.objects.get(self.name) or bpy.data.objects.new(self.name, me)
        c = bpy.data.collections[coll]
        if ob.name not in c.objects:
            c.objects.link(ob)
        ob.parent = self.root
        ob.matrix_parent_inverse.identity()
        return ob
