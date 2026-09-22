# Recorrido de cámara del portfolio: puntos clave (posición + objetivo) y paradas por sección.
# Crea la cámara animada "CamScroll" (1 clave cada 30 fotogramas) para revisar encuadres
# y escribe camera_path.json para la web.
import json, math
exec(open(r"C:\Users\Baldo\Desktop\portfolio\vienna-3d\blender\vlib.py", encoding="utf-8").read())

KEYS = [
    # cam (x, y, z)            objetivo (x, y, z)        parada / etiqueta
    ((850, 590, 26),           (1015, 590, 34),          "hero"),
    ((860, 470, 90),           (500, 250, 40),           None),
    ((380, 330, 110),          (40, 20, 60),             None),
    ((230, -210, 80),          (0, -10, 62),             "motion"),
    ((-60, -230, 70),          (-182, -367, 20),         None),
    ((-290, -486, 30),         (-182, -367, 22),         "works"),
    ((-277, -500, 26),         (-329, -547, 14),         None),
    ((-10, -540, 34),          (-53, -680, 30),          "built"),
    ((-420, -400, 120),        (-600, -100, 20),         None),
    ((-480, -20, 70),          (-650, -20, 16),          "architect"),
    ((-480, 140, 60),          (-703, 154, 54),          "vienna"),
    ((-625, 125, 45),          (-521, 127, 14),          "world"),
    ((-560, 380, 90),          (-632, 467, 50),          None),
    ((-700, -560, 480),        (250, 300, 0),            "about"),
]
STEP = 30

cam = bpy.data.objects.get("CamScroll")
if cam is None:
    cam = bpy.data.objects.new("CamScroll", bpy.data.cameras.new("CamScroll"))
    bpy.data.collections["CameraRig"].objects.link(cam)
tgt = bpy.data.objects.get("CamScrollTarget")
if tgt is None:
    tgt = bpy.data.objects.new("CamScrollTarget", None)
    bpy.data.collections["CameraRig"].objects.link(tgt)
cam.data.lens = 35
cam.data.clip_end = 8000
cam.animation_data_clear(); tgt.animation_data_clear()
for c in list(cam.constraints):
    cam.constraints.remove(c)
tc = cam.constraints.new('TRACK_TO'); tc.target = tgt
tc.track_axis = 'TRACK_NEGATIVE_Z'; tc.up_axis = 'UP_Y'

for i, (cp, tp, label) in enumerate(KEYS):
    f = 1 + i * STEP
    cam.location = cp; cam.keyframe_insert("location", frame=f)
    tgt.location = tp; tgt.keyframe_insert("location", frame=f)
for ob in (cam, tgt):
    for fc in ob.animation_data.action.fcurves if hasattr(ob.animation_data.action, "fcurves") else []:
        for kp in fc.keyframe_points:
            kp.interpolation = 'BEZIER'
            kp.handle_left_type = kp.handle_right_type = 'AUTO_CLAMPED'
sc = bpy.context.scene
sc.frame_start, sc.frame_end = 1, 1 + (len(KEYS) - 1) * STEP
sc.camera = cam

# curva visible del recorrido (solo guía)
cu = bpy.data.curves.get("CAM_PATH") or bpy.data.curves.new("CAM_PATH", 'CURVE')
cu.splines.clear(); cu.dimensions = '3D'; cu.bevel_depth = 0.8
sp = cu.splines.new('BEZIER'); sp.bezier_points.add(len(KEYS) - 1)
for bp, (cp, _, _) in zip(sp.bezier_points, KEYS):
    bp.co = cp; bp.handle_left_type = bp.handle_right_type = 'AUTO'
path = bpy.data.objects.get("CAM_PATH") or bpy.data.objects.new("CAM_PATH", cu)
if path.name not in bpy.data.collections["CameraRig"].objects:
    bpy.data.collections["CameraRig"].objects.link(path)
path.hide_render = True
path.hide_viewport = True

out = {
    "units": "metres, Blender Z-up (x east, y north, z up)",
    "lens_mm": 35,
    "keys": [{"cam": list(cp), "tgt": list(tp), "stop": label} for cp, tp, label in KEYS],
}
with open(r"C:\Users\Baldo\Desktop\portfolio\vienna-3d\web\camera_path.json", "w", encoding="utf-8") as fh:
    json.dump(out, fh, indent=1)
result = {"frames": sc.frame_end, "stops": {k[2]: 1 + i * STEP for i, k in enumerate(KEYS) if k[2]}}
