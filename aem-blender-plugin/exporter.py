# exporter.py
import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from struct import pack
import bmesh

from . import common

VERSION = {
    1: b"AEMesh\x00",
    2: b"V2AEMesh\x00",
    3: b"V3AEMesh\x00",
    4: b"V4AEMesh\x00",
    5: b"V5AEMesh\x00"
}

               
def export_aem(mesh, file_path, aem_version, triangulate_method, SCALE):
   
    with open(file_path, 'wb') as file_aem:
        magic = VERSION[4]
        pivot = pack("<bH3f", 0x17, 1,*(0,0,0))
        header = magic + pivot
        file_aem.write(header)
               
        obj = bpy.context.active_object
        if obj is None or obj.type != 'MESH':
            print("Please select a mesh object")
            return
        mesh = obj.data
        bm = bmesh.new()
        bm.from_mesh(mesh)
        bmesh.ops.triangulate(bm, faces=bm.faces)
        me = mesh.copy()
        bm.to_mesh(me)
        bm.free()
        del bm
        
        """
        uv_layer = None
        if bm.loops.layers.uv:
            uv_layer = bm.loops.layers.uv.active
       
        for face in bm.faces:
            next_face = []
            
            for loop in face.loops:
                x, y, z = loop.vert.co
                
                u, v = (0, 0)
                if uv_layer:
                    u, v = loop[uv_layer].uv

                nx, ny, nz = loop.vert.normal
        """
    
        vertices = me.vertices
        uv_layer = None        
        if len(me.uv_layers) > 0:
            uv_layer = me.uv_layers.active.data[:]        
        loops = me.loops
        polygons = me.polygons
        v_buffer = {} # Maps unique vertex data to index
        f_buffer = []
        vi = 0

        for polygon in polygons:
            next_face = [] # 3 v, 3 vn, 2 vt
            for li in polygon.loop_indices:
                # append vertex
                vid = loops[li].vertex_index
                x, y, z  = vertices[vid].co
                loops[li].vertex_index

                # append uv
                u, v = (0, 0)
                if uv_layer:
                    u, v = uv_layer[li].uv

                # append normal
                nx, ny, nz = loops[li].normal
                
                unique_v = (
                    round(x, 6), round(z, 6), round(-y, 6),
                    round(u, 6), round(v, 6),
                    round(nx, 6), round(nz, 6), round(-ny, 6)
                )
                
                if unique_v not in v_buffer:
                    v_buffer[unique_v] = vi
                    fv = vi
                    vi += 1
                else:
                    fv = v_buffer[unique_v]
                    
                next_face.append(fv)
            
            f_buffer.append(next_face)
        bpy.data.meshes.remove(me)

        fi_num = len(f_buffer)*3   
        file_aem.write(pack("H", fi_num))         
        file_aem.write(pack(f"{fi_num}H", *(i for sub in f_buffer for i in sub)))
        v_num = len(v_buffer)
        file_aem.write(pack("H", v_num))
        file_aem.write(pack(f"{v_num*3}f", *(v for ver in v_buffer for v in ver[:3])))
        file_aem.write(pack(f"{v_num*2}f", *(t for ver in v_buffer for t in ver[3:5])))
        file_aem.write(pack(f"{v_num*3}f", *(n for ver in v_buffer for n in ver[5:])))


        bsphere = pack("4f", *(0,0,0,1000))
        animation = pack("7H", *(1,0,1,0,1,0,0))
        file_aem.write(bsphere + animation)




class ExportAEM(Operator, ExportHelper):
    """Export to AEM file format (.aem)"""
    bl_idname = "export_scene.aem"
    bl_label = "Export AEM"
    bl_options = {'UNDO'}

    filename_ext = ".aem"

    filter_glob: StringProperty(
        default="*.aem",
        options={'HIDDEN'},
        maxlen=255,
    )
    
    aem_version: EnumProperty(
        name="AEM version",
        description="Choose exported AEM's version.",
        items=[
            ("V2AEMesh", "V2AEMesh", "Export V2AEMesh"),
            ("V5AEMesh", "V5AEMesh", "Export V5AEMesh")
        ],
        default='V5AEMesh'
    )
    
    scale: FloatProperty(
        name="Scale Factor (inverted)",
        description="Scale factor for exported objects - set the same as in import",
        default=common.SCALE,
        min=0.001, max=1.0
    )

    triangulate_method: EnumProperty(
        name="Triangulation Method",
        description="Method used for triangulating mesh",
        items=[
            ('BEAUTY', "Beauty", "Use Beauty method"),
            ('FIXED', "Fixed", "Use Fixed method"),
            ('ALTERNATE', "Fixed Alternate", "Use Fixed Alternate method"),
            ('SHORT_EDGE', "Shortest Diagonal", "Use Shortest Diagonal method"),
            ('LONG_EDGE', "Longest Diagonal", "Use Longest Diagonal method")
        ],
        default='BEAUTY'
    )
    
    
    add_prefix: StringProperty(
        name="Prefix",
        description="Prefix to add to exported files",
        default=""
    )

    add_suffix: StringProperty(
        name="Suffix",
        description="Suffix to add to exported files",
        default=""
    )
    

    overwrite: BoolProperty(
        name="Overwrite",
        description="Overwrite existing files",
        default=False
    )
    
    #def prepare_mesh(self, me, triangulate_method):



    def execute(self, context):

        common.SCALE = self.scale
        directory = os.path.dirname(self.filepath)
        
        if not context.selected_objects:
            self.report({'ERROR'}, "No objects selected")
            return {'CANCELLED'}
            
        for obj in bpy.context.selected_objects:
            if not obj.data or not isinstance(obj.data, bpy.types.Mesh) or obj.type != 'MESH':
                self.report({'ERROR'}, f"Object {obj.name} does not have a mesh")
                continue

            if len(context.selected_objects) == 1:
                file_out = os.path.join(directory, self.add_prefix + os.path.splitext(os.path.basename(self.filepath))[0] + self.add_suffix + '.aem')
            else:
                file_out = os.path.join(directory, self.add_prefix + obj.name + self.add_suffix + '.aem')
            
            if ( (self.overwrite and os.path.exists(file_out) ) or (not os.path.exists(file_out)) ):
            
                mesh = obj.data.copy()
                
                #bpy.context.collection.objects.link(bpy.data.objects.new("aem_temp", mesh))
                #bpy.context.view_layer.objects.active = bpy.context.collection.objects['aem_temp']
            
                #AEM does't support quads nor higher n-gons
                '''bpy.ops.object.modifier_add(type='TRIANGULATE')
                bpy.context.object.modifiers["Triangulate"].quad_method = self.triangulate_method
                bpy.context.object.modifiers["Triangulate"].min_vertices = 4
                if self.triangulate_method == 'BEAUTY':
                    bpy.context.object.modifiers["Triangulate"].ngon_method = 'BEAUTY'
                else:
                    bpy.context.object.modifiers["Triangulate"].ngon_method = 'CLIP'       
                bpy.ops.object.modifier_apply(modifier="Triangulate")
                
                '''
                #self.prepare_mesh(mesh, self.triangulate_method)
                
                export_aem(mesh, self.filepath.replace(".aem", f"_{obj.name}.aem"), VERSION[self.aem_version+"\x00"], self.triangulate_method, self.scale)
                bpy.data.meshes.remove(mesh)
            else:
                self.report({'WARNING'}, f"File {file_out} already exists and overwrite is disabled.")
    
        return {'FINISHED'}


    def write(self, context, filepath):
        export_aem(filepath)
        return {'FINISHED'}
        

def menu_func_export(self, context):
    self.layout.operator(ExportAEM.bl_idname, text="Abyss Engine Mesh(.aem)")

