import bpy
from mathutils import Vector

def get_bounding_sphere(objects, mode='BBOX'):
    """Return the bounding sphere center and radius for objects (in global coordinates)."""
    """Nikita from  B3D - Interplanety
       https://b3d.interplanety.org/en/how-to-calculate-the-bounding-sphere-for-selected-objects/"""
    
    # return the bounding sphere center and radius for objects (in global coordinates)
    if not isinstance(objects, list):
        objects = [objects]
    points_co_global = []
    if mode == 'GEOMETRY':
        # GEOMETRY - by all vertices/points - more precis, more slow
        for obj in objects:
            points_co_global.extend([obj.matrix_world @ vertex.co for vertex in obj.data.vertices])
    elif mode == 'BBOX':
        # BBOX - by object bounding boxes - less precis, quick
        for obj in objects:
            points_co_global.extend([obj.matrix_world @ Vector(bbox) for bbox in obj.bound_box])
 
    def get_center(l):
        return (max(l) + min(l)) / 2 if l else 0.0
 
    x, y, z = [[point_co[i] for point_co in points_co_global] for i in range(3)]
    b_sphere_center = Vector([get_center(axis) for axis in [x, y, z]]) if (x and y and z) else None
    b_sphere_radius = max(((point - b_sphere_center) for point in points_co_global)) if b_sphere_center else None
    return b_sphere_center, b_sphere_radius.length
 



def build_bounding_sphere(xyzr, name: str):
    """Creates wireframe sphere. Gets it adopted by active object. Keep selection in state like before calling."""
    r = xyzr[3]
    x,y,z = xyzr[:3]
    selection = bpy.context.selected_objects
    active = bpy.context.view_layer.objects.active
    bpy.ops.object.select_all(action='DESELECT')
    
    bpy.ops.mesh.primitive_ico_sphere_add() #radius = r, location = (x,z,-y)
    sphere = bpy.context.view_layer.objects.active
    sphere.name = name + "_bsphere"
    sphere.data.name = name + "_bsphere"
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.delete(type='ONLY_FACE')    
    
    
    bpy.ops.object.mode_set(mode='OBJECT')
    bpy.context.scene.tool_settings.transform_pivot_point = 'INDIVIDUAL_ORIGINS'
    bpy.ops.transform.resize(value=(r,r,r))
    #bpy.ops.transform.translate(value=(x,y,z))
    #bpy.ops.object.transform_apply()
    
    #bpy.ops.object.parent_set(type='OBJECT', keep_transform=False)
    sphere.parent = active
    #bpy.context.scene.tool_settings.transform_pivot_point = 'CURSOR'
    #bpy.ops.transform.rotate(value=pi / 2, orient_axis='X')
    sphere.location = (x,z,-y)
    for obj in selection:
      obj.select_set(True)
    sphere.select_set(False)

if __name__ == "__main__":
    b_sphere_co, b_sphere_radius = get_bounding_sphere(
        objects=bpy.context.selected_objects,
        mode='GEOMETRY'
        )
    radius = 50.0
    position = (0.0, 0.0, 0.0)

    # Create a new UV sphere
    bpy.ops.mesh.primitive_ico_sphere_add()

    # Get the active object
    obj = bpy.context.active_object

    # Convert the UV sphere to a wireframe mesh
    bpy.ops.object.mode_set(mode='EDIT')
    bpy.ops.mesh.select_all(action='SELECT')
    bpy.ops.mesh.delete(type='ONLY_FACE')
    bpy.ops.object.mode_set(mode='OBJECT')
    

    
    # <Vector (0.0000, 0.0000, 1.5710)> 2.0898222449791612