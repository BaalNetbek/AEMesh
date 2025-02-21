# exporter.py
import bpy, os
from bpy_extras.io_utils import ExportHelper
from bpy.props import StringProperty, FloatProperty, BoolProperty, EnumProperty
from bpy.types import Operator
from math import pi
from mathutils import Matrix, Vector
from struct import pack
import bmesh

from . import common
from .common import VERSION

               
def export_aem(mesh, file_path, aem_version, triangulate_method, SCALE):

    '''Arguments: mesh, triangulation method.
    Triangulates and splits faces of the mesh for compatibility with AEM format,
    and rotates the mesh 90 degrees clockwise around the X-axis.'''
    
    bm = bmesh.new()
    bm.from_mesh(mesh)
    rotation_matrix = Matrix.Rotation(-pi / 2, 4, 'X')
    bmesh.ops.transform(bm, matrix=rotation_matrix, verts=bm.verts)
    bmesh.ops.triangulate(bm, faces=bm.faces, quad_method = triangulate_method)
    bmesh.ops.split_edges(bm, edges=bm.edges)
    bm.edges.ensure_lookup_table()

    def uv_from_vert_first(uv_layer, v):
        for l in v.link_loops:
            uv_data = l[uv_layer]
            return uv_data.uv
        return None

    def uv_from_vert_average(uv_layer, v):
        uv_average = Vector((0.0, 0.0))
        total = 0.0
        for loop in v.link_loops:
            uv_average += loop[uv_layer].uv
            total += 1.0

        if total != 0.0:
            return uv_average * (1.0 / total)
        else:
            return None

    # Example using the functions above
    uv_layer = bm.loops.layers.uv.active
    uv_per_vertex = []
    for v in bm.verts:
        uv_first = uv_from_vert_first(uv_layer, v)
        uv_per_vertex.append(uv_first)
        uv_average = uv_from_vert_average(uv_layer, v)
        print("Vertex: %r, uv_first=%r, uv_average=%r" % (v, uv_first, uv_average))
    bmnormals = []
    for v in bm.verts:
        # Custom normals are stored in the `normal` attribute of each vertex
        # But note, this is not directly "split normals" but rather the custom normal for this vertex
        bmnormals.append([*v.normal])

 
    bm.to_mesh(mesh)
    bm.free()

    
    #faces = [face.vertices for face in mesh.polygons]
    #vertices = [v.co for v in mesh.vertices]
    uv_layer = mesh.uv_layers.active.data if mesh.uv_layers.active else None
    uvs = [uv.uv for uv in uv_layer] if uv_layer else []
    uvs = [uv.uv for uv in mesh.uv_layers.active.data]
    normals = [v.normal for v in mesh.vertices]

    # Extract vertices and faces
    #vertices = [(v.co.x, v.co.y, v.co.z) for v in mesh.vertices]
    #faces = [(t.vertices[0], t.vertices[1], t.vertices[2]) for t in mesh.loop_triangles]
    #faces = [[*t.vertices] for t in mesh.loop_triangles]
    

    
    def write_short(file, value, endian='<'):
        """Writes a short integer to a binary file."""
        file.write(pack(f'{endian}h', value))

    def write_short_triplets_array(file, array, endian='<'):
        """Writes an array of 3-tuple shorts to a binary file."""
        for triplet in array:
            file.write(pack(f'{endian}hhh', *triplet))
    

    def write_float_triplets_array(file, array, endian='<'):
        """Writes an array of 3-tuple floats to a binary file."""
        for triplet in array:
            file.write(pack(f'{endian}fff', *triplet))
    

    addon_directory = os.path.dirname(os.path.abspath(__file__))
    header_file_path = os.path.join(addon_directory, 'header.bin')
    
    with open(header_file_path, 'rb') as file_header, open(file_path, 'wb') as file_aem:
        header = file_header.read(24)
        file_aem.write(header)
        

        indices = []
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                indices.append(mesh.loops[loop_index].vertex_index)
        indices_num = len(indices)
        write_short(file_aem, indices_num)
        #print(faces)
        #write_short_triplets_array(file_aem, faces)
        #print(*indices)
        file_aem.write(pack(f"{indices_num}H", *indices))
        
        vertices = [(v.co.x, v.co.y, v.co.z) for v in mesh.vertices]#[*(v.co for v in mesh.vertices)]
        v_num = len(vertices)
        write_short(file_aem, v_num)
        write_float_triplets_array(file_aem, vertices)
    
        #uv_layer = mesh.uv_layers.active.data if mesh.uv_layers.active else None
        #uvs = [uv.uv for uv in uv_layer] if uv_layer else []
        #print(*uvs)
        #for uv in uvs:
        #    file_aem.write(pack("ff", uv[0], uv[1]))
        for uv in uv_per_vertex:
            print(uv)
            if uv is not None:
                file_aem.write(pack(f"2f", uv[0],uv[1]))

        #normals = [v.normal for v in mesh.vertices]
        write_float_triplets_array(file_aem, bmnormals)   
        #file_aem.write(pack(f"{len(bmnormals)}f", *bmnormals))
        """
        processed_vertices = [False] * len(mesh.vertices)
        for poly in mesh.polygons:
            for loop_index in poly.loop_indices:
                loop = mesh.loops[loop_index]
                vertex_index = loop.vertex_index
                if not processed_vertices[vertex_index]:
                    normal = normals[mesh.loops[loop_index].vertex_index]
                    print(normal.x, normal.y, normal.z, "\n")
                    file_aem.write(pack("fff", normal.x, normal.y, normal.z))"""
        # mesh.use_auto_smooth = True

           
        header = file_header.read(56)
        file_aem.write(header)




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
                
                export_aem(mesh, self.filepath.replace(".aem", f"_{obj.name}.aem"), VERSION[self.aem_version+"\x00"], self.scale, self.triangulate_method)
                bpy.data.meshes.remove(mesh)
            else:
                self.report({'WARNING'}, f"File {file_out} already exists and overwrite is disabled.")
    
        return {'FINISHED'}


    def write(self, context, filepath):
        export_aem(filepath)
        return {'FINISHED'}
        

def menu_func_export(self, context):
    self.layout.operator(ExportAEM.bl_idname, text="Abyss Engine Mesh(.aem)")

