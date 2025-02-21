# importer.py
import bpy, os
from bpy_extras.io_utils import ImportHelper
from bpy.props import StringProperty, FloatProperty, BoolProperty, CollectionProperty
from bpy.types import Operator
from math import pi
from struct import unpack


from . import common
from .common import FLAGS, VERSION
from .read_helper import * 
from .BoundingSphere import build_bounding_sphere


def sign_check(c, cs):
    if (cs == -1 and c < 0) or (cs == 0x0 and c >= 0):
        return 1
    return -1       
    
def triangle_strips_unpack(indices, tstrip_array):
    i = 0
    unpacked = []
    for strip in tstrip_array:
        for j in range(strip - 2):
            if j % 2 == 0:
                unpacked.append([indices[i+j], indices[i+j+1], indices[i+j+2]])
            else:
                unpacked.append([indices[i+j], indices[i+j+2], indices[i+j+1]])
        i += strip  
    return unpacked
    
def import_aem(file_path, import_normals=True):
    print(f"\nLoading: {os.path.basename(file_path)}")
    importer_state = "READ_HEADER"  
    with open(file_path, 'rb') as file_aem:
        while (importer_state != "END"):
            if importer_state == "READ_HEADER":
                print(importer_state)
                magic = ""
                while not magic.endswith("AEMesh\x00"):
                    magic += file_aem.read(1).decode("utf-8")
                    if len(magic) > 9:
                        file_aem.close()
                        print("Unsuppored .aem file. Invalid signature") #self.report ...
                        return -1
                flags = int.from_bytes(file_aem.read(1))
                mesh_present = bool(flags & FLAGS["basemesh"])
                if mesh_present:
                    uvs_present = bool(flags & FLAGS["uvs"])
                    normals_present = bool(flags & FLAGS["normals"])
                    unk_present = bool(flags & FLAGS["unk"])
                    version = VERSION[magic]
                    
                    submesh_num = 1
                    first_mesh = True
                    if version in (3, 4, 5):
                        submesh_num = unpack('h',file_aem.read(2))[0]
                        print(f'Number of submeshes: {submesh_num}')
                    submeshes_left = submesh_num
                    
                    importer_state = "READ_MESH"
                else:
                    print("Basemesh flag is false!")
                    importer_state = "END"
                    
            if importer_state == "READ_MESH":
                print(importer_state)
                submeshes_left -= 1            
                if version in (4, 5):   
                    #print(hex(file_aem.tell()))
                    pivot_point = unpack('fff',file_aem.read(12))
                    print(f'Pivot point: x: {pivot_point[0]}, y: {pivot_point[1]}, z: {pivot_point[2]}')
                    indices_num = read_short(file_aem)
                    faces = read_short_triplets_array(file_aem, indices_num)
                    v_num = read_short(file_aem)
                    vertices = read_float_triplets_array(file_aem, v_num * 3)
                    if uvs_present:
                        uvs = read_float_twins_array(file_aem, v_num * 2)
                    if import_normals and normals_present:
                        normals = read_float_triplets_array(file_aem, v_num*3)
                    if unk_present:
                        try:
                            #some_quaternions = read_float_quadruplets_array(file_aem, 4* v_num)
                            some_quaternions = read_float_array(file_aem, 4* v_num)
                            if any(i != 1 for i in some_quaternions):
                                print("Abnormality in the unknown values!")
                        except Exception as e:
                            print(f"quaternions loading failed: {e}")                            
                elif version in (1, 2, 3):  
                    if version in (2,3):
                        if version == 3:
                            pivot_point = unpack('fff',file_aem.read(12))
                            print(f'Pivot point: x: {pivot_point[0]}, y: {pivot_point[1]}, z: {pivot_point[2]}')    
                        vertex_cord_size = 6
                        UV_UNIT_POINT = 1/4096 #(2^12)
                        NORMALS_UNIT_POINT = 1/32768 #(2^15)
                        indices_num = read_short(file_aem)
                        faces = read_short_triplets_array(file_aem, indices_num)
                        v_num = read_short(file_aem)
                        '''if cord is negative sign bits are FFFF else they are 0000'''
                        v_block = read_short_hexlets_array(file_aem, v_num*6)
                        vertices = [(x*sign_check(x, xs), y*sign_check(y, ys), z*sign_check(z, zs)) for x, xs, y, ys, z, zs in v_block]
                    if version == 1:
                        vertex_cord_size = 3
                        UV_UNIT_POINT = NORMALS_UNIT_POINT = 1/256 #(2^8)
                        indices_num = read_short(file_aem)
                        pre_strip_pos = file_aem.tell()
                        try: #handling sepcial case of AEM version 1 and a half
                            UV_UNIT_POINT = 1/4096
                            NORMALS_UNIT_POINT = 1/32768
                            indices = read_short_array(file_aem, indices_num)
                            t_strips_len = read_short(file_aem)
                            t_strips = read_short_array(file_aem, t_strips_len)
                            faces = triangle_strips_unpack(indices, t_strips)
                        except IndexError:
                            file_aem.seek(pre_strip_pos)
                            faces = read_short_triplets_array(file_aem, indices_num)
                        v_num = read_short(file_aem)
                        vertices = read_short_triplets_array(file_aem, v_num*3)
                    
                    if uvs_present:
                        uv_block = read_short_twins_array(file_aem, v_num*2) 
                        #print(f"UVS maximum raw value {max(uv_block)}")
                        uvs = [(u*UV_UNIT_POINT, v*UV_UNIT_POINT) for u, v in uv_block]
                    if import_normals and normals_present:
                        normals_block = read_short_triplets_array(file_aem, v_num*3)
                        normals = [(x*NORMALS_UNIT_POINT, y*NORMALS_UNIT_POINT, z*NORMALS_UNIT_POINT) for x, y, z in normals_block]
                    if unk_present:
                        try:
                            #print("some keys")
                            #print(f"vnum: {v_num}, {hex(v_num)}")
                            # file size - pos - 4*vnum*4 < 0 -> throw
                            some_twins = read_short_twins_array(file_aem, 2*v_num)
                            for i in range(0, len(some_quaternions), 5):
                                print(' '.join(f'{q}' for q in some_quaternions[i:i+5]))
                        except Exception as e:
                            print(f"quaternions loading failed: {e}")
                    
                    if version == 1:
                        is_transparent = int.from_bytes(file_aem.read(1))

                else:
                    print(f"Unsupported file AEM version: {version}")
                    return -1

                # Read BoundingSphere
                if version in (3, 4, 5):
                    bounding_sphere = unpack('<4f',file_aem.read(16))#read_float_quadruplets_array(file_aem, 4)
                    #unpack('<4f',file_aem.read(16))
                    print(f'BoundingBox: x: {bounding_sphere[0]}, y: {bounding_sphere[1]}, z: {bounding_sphere[2]}, r: {bounding_sphere[3]}')
                    
                importer_state = "BUILD_MESH"
                    
            if importer_state == "BUILD_MESH":

                obj_name = os.path.basename(file_path).split('.')[0]
                mesh = bpy.data.meshes.new(name=obj_name + "_Mesh")
                obj = bpy.data.objects.new(obj_name, mesh)
                bpy.context.collection.objects.link(obj)
                bpy.context.view_layer.objects.active = obj
                obj.select_set(True)
                if first_mesh:
                    root_mesh = obj
                    first_mesh = False
                else:
                    obj.parent = root_mesh
                
                mesh.from_pydata(vertices, [], faces)
                mesh.update()
                
                if uvs_present:
                    uv_layer = mesh.uv_layers.new(name="UVMap")
                    for poly in mesh.polygons:
                        for loop_index in poly.loop_indices:
                            loop_vert_index = mesh.loops[loop_index].vertex_index
                            uv_layer.data[loop_index].uv = uvs[loop_vert_index]
                
                if import_normals and normals_present:
                    mesh.normals_split_custom_set_from_vertices(normals)
                    obj.data.shade_smooth()
                
                if version in (3, 4, 5):
                    build_bounding_sphere(bounding_sphere, obj_name)
                    
                    importer_state = "READ_ANIM"
                else:
                    importer_state = "END"
                
                    
            if importer_state == "READ_ANIM": 
                print(importer_state)
                importer_state = "END"
                if version in (3, 4, 5):
                    from . import red
                    mesh = red.Mesh()
                    mesh.read_enhanced_data_from_file(file_aem, flags)
                    print((mesh.transform))
                    if submeshes_left > 0:
                        importer_state = "READ_MESH"

            if importer_state == "END":    
                if mesh_present == False:
                    return -1
                if version == 1:
                    return (root_mesh, version, is_transparent)
                return (root_mesh, version, normals_present, submesh_num)      

class ImportAEM(Operator, ImportHelper):
    """Import from AEM file format (.aem)"""
    bl_idname = "import_scene.aem"
    bl_label = "Import AEM"
    bl_options = {'PRESET', 'UNDO'}

    filename_ext = ".aem"

    filter_glob: StringProperty(
        default="*.aem",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    files: CollectionProperty(
        type=bpy.types.PropertyGroup
    )
    
    scale: FloatProperty(
        name="Scale Factor",
        description="Scale factor for imported objects",
        default=common.SCALE,
        min=0.001, max=1.0
    )
    
    import_normals: BoolProperty(
        name="Import Normals",
        description="Choose whether to import normals or not",
        default=True,
    )
    


    def execute(self, context):
        common.SCALE = self.scale

        if len(self.filepath) < 1:
            print('No valid AEM provided.')
            return {'FINISHED'}
            
        if bpy.context.mode != 'OBJECT':
            bpy.ops.object.mode_set(mode='OBJECT', toggle=False)
        
        if len(self.files) > 1:
            directory = os.path.dirname(self.filepath)
            for file in self.files:
                file_path = os.path.join(directory, file.name)
                bpy.ops.object.select_all(action='DESELECT')
                root_mesh = import_aem(file_path)[0]
                bpy.ops.object.select_all(action='DESELECT')
                bpy.context.view_layer.objects.active = root_mesh
                #bpy.ops.transform.rotate(value=-pi / 2, orient_axis='X')
                #bpy.ops.transform.resize(value=(SCALE,SCALE,SCALE))
                root_mesh.rotation_euler = (pi/2, 0, 0)
                root_mesh.scale = (self.scale,self.scale,self.scale)
                #bpy.ops.object.transform_apply(rotation=True, scale=True)
                #bpy.ops.object.shade_smooth()
                aem_collection = bpy.data.collections.new(os.path.basename(file_path).split('.')[0])
                bpy.context.scene.collection.children.link(aem_collection)
                for obj in bpy.context.selected_objects:
                    for coll in obj.users_collection:
                        coll.objects.unlink(obj)
                    aem_collection.objects.link(obj)

        else:
            bpy.ops.object.select_all(action='DESELECT')
            root_mesh = import_aem(self.filepath)[0]
            bpy.ops.object.select_all(action='DESELECT')
            bpy.context.view_layer.objects.active = root_mesh
            print(root_mesh)
            print(bpy.context.view_layer.objects.active)
            bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
            root_mesh.rotation_euler = (pi/2, 0, 0)
            root_mesh.scale = (self.scale,self.scale,self.scale)
            #bpy.ops.transform.rotate(value=-pi/2, orient_axis='X')
            #bpy.ops.transform.resize(value=(SCALE,SCALE,SCALE))
            #bpy.ops.object.transform_apply(rotation=True, scale=True)
            #bpy.ops.object.shade_smooth()
            
        return {'FINISHED'}

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "scale")
        
def menu_func_import(self, context):
    self.layout.operator(ImportAEM.bl_idname, text="Abyss Engine Mesh(.aem)")
                
