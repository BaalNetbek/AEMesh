import bpy
from . import importer, exporter
bl_info = {
    "name": "AEM Blender Plugin",
    "author": "Baal Netbek",
    "version": (1, 8),
    "blender": (4, 1, 0),
    "location": "File > Import-Export",
    "description": "AByss Engine Mesh Import / ? Export",
    "warning": "",
    "category": "Import-Export",
}

SCALE = 0.01

FLAGS = {
    "basemesh":1|16, #10001 every mesh should have it
    "uvs":2,        #00010 texture coordinates
    "normals":4,    #00100
    "unk":8,        #01000 per vertex attributes of some kind
}
VERSION = {
    "AEMesh\x00":1,
    "V2AEMesh\x00":2,
    "V3AEMesh\x00":3,
    "V4AEMesh\x00":4,
    "V5AEMesh\x00":5
}  
   


'''    
def parse_animation(f):
    #read, test, go back
    unpack("3h", f.read(6))
    #type = f.read(2)
    if type == 0:
    if type == 1:
    if type == 2:
        #4 floats?
    if type == 3:
        read_float_twins_array(3, f)
    if type == 4:
        read read_float_quadruplets_array(2, f)
    if type == 5:
        read read_float_quadruplets_array(5, f) 
        # (t, x, y, z)
    if type == 6:
    if type == 10:
'''    

def register():
    bpy.utils.register_class(importer.ImportAEM)
    bpy.utils.register_class(exporter.ExportAEM)
    bpy.types.TOPBAR_MT_file_import.append(importer.menu_func_import)
    bpy.types.TOPBAR_MT_file_export.append(exporter.menu_func_export)

def unregister():
    bpy.utils.unregister_class(importer.ImportAEM)
    bpy.utils.unregister_class(exporter.ExportAEM)
    bpy.types.TOPBAR_MT_file_import.remove(importer.menu_func_import)
    bpy.types.TOPBAR_MT_file_export.remove(exporter.menu_func_export)

if __name__ == "__main__":
    register()
if __name__ == "__main__":
    register()
