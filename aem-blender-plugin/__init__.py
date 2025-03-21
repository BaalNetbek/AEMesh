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

