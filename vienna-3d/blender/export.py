# Exporta la ciudad a web/city.glb (Draco + EXT_mesh_gpu_instancing).
# - Los tubos del Riesenrad (curvas) se convierten a malla en copias "RRM_*".
# - Las piezas que giran cuelgan de RR_WheelPivot; los vagones quedan bajo RR_Root
#   con su ángulo en la propiedad "angle" (la web los recoloca cada fotograma).
import bpy, math
exec(open(r"C:\Users\Baldo\Desktop\portfolio\vienna-3d\blender\vlib.py", encoding="utf-8").read())
OUT = r"C:\Users\Baldo\Desktop\portfolio\vienna-3d\web\city.glb"

RR = bpy.data.collections["Riesenrad"]
root = bpy.data.objects["RR_Root"]
pivot = bpy.data.objects["RR_WheelPivot"]
# el pivote vive en el marco local del Riesenrad, en el buje
pivot.parent = root
pivot.matrix_parent_inverse.identity()
pivot.location = (0, 0, 34.0)
pivot.rotation_euler = (0, 0, 0)

ROTATING = ["RR_Rings", "RR_Truss", "RR_Arms", "RR_Ties", "RR_Spokes", "RR_Axle", "RR_FlangeA", "RR_FlangeB"]
dg = bpy.context.evaluated_depsgraph_get()
for name in ROTATING + ["RR_TowerChords", "RR_TowerBrace"]:
    src = bpy.data.objects[name]
    mname = "RRM_" + name[3:]
    old = bpy.data.objects.get(mname)
    if old:
        bpy.data.objects.remove(old, do_unlink=True)
    if src.type == 'CURVE':
        me = bpy.data.meshes.new_from_object(src.evaluated_get(dg))
        ob = bpy.data.objects.new(mname, me)
        RR.objects.link(ob)
        ob.matrix_world = src.matrix_world.copy()
        src.hide_viewport = True
        src.hide_render = True
        target = ob
    else:
        target = src
    mw = target.matrix_world.copy()
    target.parent = pivot if name in ROTATING else root
    target.matrix_world = mw

# selección para exportar: todo lo visible de VIENNA salvo guías, cámaras y prototipos
bpy.ops.object.select_all(action='DESELECT')
protos = bpy.data.objects.get("BLOCK_PROTOS")
skip_types = {'CAMERA', 'LIGHT'}
n = 0
for o in bpy.data.collections["VIENNA"].all_objects:
    if o.type in skip_types or o.name in ("CAM_PATH", "CamScrollTarget"):
        continue
    if o.hide_viewport or o.hide_get():
        continue
    if protos and (o == protos or o.parent == protos):
        continue
    if o.type == 'CURVE':
        continue
    o.select_set(True)
    n += 1

import io, contextlib, logging
logging.getLogger("glTFExporter").setLevel(logging.WARNING)
_sink = io.StringIO()
with contextlib.redirect_stdout(_sink), contextlib.redirect_stderr(_sink):
  bpy.ops.export_scene.gltf(
      filepath=OUT,
      export_format='GLB',
      use_selection=True,
      export_apply=True,
      export_yup=True,
      export_extras=True,
      export_gpu_instances=True,
      export_draco_mesh_compression_enable=True,
      export_draco_mesh_compression_level=7,
      export_draco_position_quantization=14,
      export_draco_normal_quantization=8,
      export_normals=True,
      export_texcoords=False,
      export_materials='EXPORT',
      export_cameras=False,
      export_lights=False,
      export_animations=False,
  )
import os
result = {"objects": n, "glb_kb": round(os.path.getsize(OUT) / 1024)}
