#Noesis AEMesh import (not export) module
from inc_noesis import *
from struct import pack
from collections import defaultdict
import os

def registerNoesisTypes():
	handle = noesis.register("Abyss Engine Mesh", ".aem")
	noesis.setHandlerTypeCheck(handle, aemCheckType)
	noesis.setHandlerLoadModel(handle, aemLoadModel)
	noesis.setHandlerWriteModel(handle, noepyWriteModel)
	noesis.setHandlerWriteAnim(handle, noepyWriteAnim)
	#any noesis.NMSHAREDFL_* flags can be applied here, to affect the model which is handed off to the exporter.
	#adding noesis.NMSHAREDFL_FLATWEIGHTS_FORCE4 would force us to 4 weights per vert.
	noesis.setTypeSharedModelFlags(handle, noesis.NMSHAREDFL_FLATWEIGHTS)

	#noesis.logPopup()
	#print("The log can be useful for catching debug prints from preview loads.\nBut don't leave it on when you release your script, or it will probably annoy people.")
	return 1

FLAGS = {
    "basemesh": 1 | 16,  # every mesh should have it
    "uvs": 2,           # texture coordinates
    "normals": 4,
    "unk": 8,           # per vertex attributes of some kind
}

VERSION = {
    "AEMesh\x00": 1,
    "V2AEMesh\x00": 2,
    "V3AEMesh\x00": 3,
    "V4AEMesh\x00": 4,
    "V5AEMesh\x00": 5
}

def aemCheckType(data):
    if len(data) < 9:
        return 0
    file_aem = NoeBitStream(data)

    magic = ""
    while not magic.endswith("AEMesh\x00"):
        magic += chr(file_aem.readUByte())#.decode("utf-8")
        if len(magic) > 9:
            file_aem.close()
            print("Unsuppored .aem file. Invalid signature") #self.report ...
            return 0
    
    return 1

def read_float_array(file, len):
	return file.read('{0}f'.format(len))

def read_short_array(file, len, endian='<'):
    return file.read('{0}h'.format(len))

def read_short_twins_array(file, len, endian='<'):
    if (len % 2 != 0): raise ValueError("Twins array length must be a multiple of 2")
    flat_array = file.read('{0}h'.format(len))
    return list(zip(flat_array[0::2], flat_array[1::2]))

def read_short_triplets_array(file, len, endian='<'):
    if (len % 3 != 0): raise ValueError("Triplets array length must be a multiple of 3")
    flat_array = file.read('{0}h'.format(len))
    return list(zip(flat_array[0::3], flat_array[1::3], flat_array[2::3]))

def read_short_NoeVec3_array(file, length, endian='<'):
    if (length % 3 != 0): raise ValueError("Triplets array length must be a multiple of 3")
    flat_array = file.read('{0}h'.format(length))
    return [NoeVec3([flat_array[i], flat_array[i+1], flat_array[i+2]])
            for i in range(0, length, 3)]

def read_ushort_triplets_array(file, len, endian='<'):
    if (len % 3 != 0): raise ValueError("Triplets array length must be a multiple of 3")
    flat_array = file.read('{0}H'.format(len))
    return list(zip(flat_array[0::3], flat_array[1::3], flat_array[2::3]))

def read_short_quadruplets_array(file, len, endian='<'):
    if (len % 4 != 0): raise ValueError("Quadruplets array length must be a multiple of 4")
    flat_array = file.read('{0}h'.format(len))
    return list(zip(flat_array[0::4], flat_array[1::4], flat_array[2::4], flat_array[3::4]))

def read_short_hexlets_array(file, len, endian='<'):
    if (len % 6 != 0): raise ValueError("Hexlets array length must be a multiple of 4")
    flat_array = file.read('{0}h'.format(len))
    print(max(flat_array))
    print(min(flat_array))
    return list(zip(flat_array[0::6], flat_array[1::6], flat_array[2::6], flat_array[3::6], flat_array[4::6], flat_array[5::6]))    

def read_float_quadruplets_array(file, len, endian='<'):
    if (len % 4 != 0): raise ValueError("Quadruplets array length must be a multiple of 4")
    flat_array = file.read('{0}f'.format(len))
    return list(zip(flat_array[0::4], flat_array[1::4], flat_array[2::4], flat_array[3::4]))
  
def read_float_triplets_array(file, len, endian='<'):
    if (len % 3 != 0): raise ValueError("Triplets array length must be a multiple of 3")
    flat_array = file.read('{0}f'.format(len))
    return list(zip(flat_array[0::3], flat_array[1::3], flat_array[2::3]))

def read_float_triplets_array(file, len, endian='<'):
    if (len % 3 != 0): raise ValueError("Triplets array length must be a multiple of 3")
    flat_array = file.read('{0}f'.format(len))
    return list(zip(flat_array[0::3], flat_array[1::3], flat_array[2::3]))

def read_float_NoeVec3_array(file, length, endian='<'):
    if length % 3 != 0:
        raise ValueError("Triplets array length must be a multiple of 3")
    flat_array = file.read('{0}f'.format(length))
    return [NoeVec3([flat_array[i], flat_array[i+1], flat_array[i+2]])
            for i in range(0, length, 3)]

def read_float_twins_array(file, len, endian='<'):
    if (len % 2 != 0): raise ValueError("Twins array length must be a multiple of 2")
    flat_array = file.read('{0}f'.format(len))
    return list(zip(flat_array[0::2], flat_array[1::2]))

def read_float_NoeVec3_UV_array(file, len, endian='<'):
    if (len % 2 != 0): raise ValueError("Twins array length must be a multiple of 2")
    flat_array = file.read('{0}f'.format(len))
    return [NoeVec3([flat_array[i], -flat_array[i+1], 0])
        for i in range(0, len, 2)]

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
    
def aemLoadModel(data, mdlList):
    #print(f"\nLoading: {os.path.basename(file_path)}")
    importer_state = "READ_HEADER"  
    ctx = rapi.rpgCreateContext()
    bones = []
    root_bone = NoeBone(0, "root", NoeMat43())
    texture = NoeTexture("dummyTexture", 2,2,b'\xff\xff\xff\xff\x00\x00\x00\x00\x00\x00\x00\x00\xff\xff\xff\xff',  noesis.NOESISTEX_RGBA32) 
    print(os.path.dirname(os.path.realpath(__file__)))
    material = NoeMaterial("defMaterial", os.path.dirname(os.path.realpath(__file__))+r"\test.bmp")
    bones.append(root_bone)

    meshes = []
    kf_bones = []
    anims = []

    bon_idx = -1
    mdl = None
    file_aem = NoeBitStream(data)
    if True:
        while (importer_state != "END"):
            if importer_state == "READ_HEADER":
                print(importer_state)
                magic = ""
                while not magic.endswith("AEMesh\x00"):
                    magic += chr(file_aem.readUByte())
                    if len(magic) > 9:
                        file_aem.close()
                        print("Unsuppored .aem file. Invalid signature") #self.report ...
                        return -1
                flags = file_aem.readUByte()
                print(magic[:-1])
                mesh_present = bool(flags & FLAGS["basemesh"])
                if mesh_present:
                    uvs_present = bool(flags & FLAGS["uvs"])
                    normals_present = bool(flags & FLAGS["normals"])
                    unk_present = bool(flags & FLAGS["unk"])
                    version = VERSION[magic]
                    
                    submesh_num = 1
                    first_mesh = True
                    if version in (3, 4, 5):
                        submesh_num = file_aem.readUShort()
                        print('Number of submeshes: {0}'.format(submesh_num))
                    submeshes_left = submesh_num
                    
                    importer_state = "READ_MESH"
                else:
                    print("Basemesh flag is false!")
                    importer_state = "END"
                    
            if importer_state == "READ_MESH":
                print(importer_state)
                submeshes_left -= 1            
                if version in (4, 5):   
                    pivot_point = file_aem.read('fff')
                    print("Pivot point: x: {0}, y: {1}, z: {2}".format(pivot_point[0], pivot_point[1], pivot_point[2]))
                    indices_num = file_aem.readUShort()
                    faces = read_ushort_triplets_array(file_aem, indices_num)
                    v_num = file_aem.readUShort()
                    vertices = read_float_NoeVec3_array(file_aem, v_num * 3)
                    if uvs_present:
                        uvs = read_float_NoeVec3_UV_array(file_aem, v_num * 2)
                    if normals_present:
                        normals = read_float_NoeVec3_array(file_aem, v_num*3)
                    if unk_present:
                        try:
                            #some_quaternions = read_float_quadruplets_array(file_aem, 4* v_num)
                            some_quaternions = read_float_array(file_aem, 4* v_num)
                            if any(i != 1 for i in some_quaternions):
                                print("Abnormality in the unknown values!")
                        except Exception as e:
                            print("quaternions loading failed: "+e)                            
                elif version in (1, 2, 3):  
                    if version in (2,3):
                        if version == 3:
                            pivot_point = file_aem.read('fff')
                            print('Pivot point: x: {0}, y: {1}, z: {2}'.format(pivot_point[0],pivot_point[1], pivot_point[2]))    
                        vertex_cord_size = 6
                        UV_UNIT_POINT = 1/4096 #(2^12)
                        NORMALS_UNIT_POINT = 1/32768 #(2^15)
                        indices_num = file_aem.readUShort()
                        faces = read_short_triplets_array(file_aem, indices_num)
                        v_num = file_aem.readUShort()
                        '''if cord is negative sign bits are FFFF else they are 0000'''
                        v_block = read_short_hexlets_array(file_aem, v_num*6)
                        vertices = [NoeVec3([x*sign_check(x, xs), y*sign_check(y, ys), z*sign_check(z, zs)]) for x, xs, y, ys, z, zs in v_block]
                    if version == 1:
                        vertex_cord_size = 3
                        UV_UNIT_POINT = NORMALS_UNIT_POINT = 1/256 #(2^8)
                        indices_num = file_aem.readUShort()
                        pre_strip_pos = file_aem.tell()
                        try: #handling sepcial case of AEM version 1 and a half
                            UV_UNIT_POINT = 1/4096
                            NORMALS_UNIT_POINT = 1/32768
                            indices = read_short_array(file_aem, indices_num)
                            t_strips_len = file_aem.readUShort()
                            t_strips = read_short_array(file_aem, t_strips_len)
                            faces = triangle_strips_unpack(indices, t_strips)
                        except IndexError:
                            file_aem.seek(pre_strip_pos)
                            faces = read_short_triplets_array(file_aem, indices_num)
                        v_num = file_aem.readUShort()
                        vertices = read_short_NoeVec3_array(file_aem, v_num*3)
                    
                    if uvs_present:
                        uv_block = read_short_twins_array(file_aem, v_num*2) 
                        #print(f"UVS maximum raw value {max(uv_block)}")
                        uvs = [NoeVec3([u*UV_UNIT_POINT, -v*UV_UNIT_POINT, 0]) for u, v in uv_block]
                    if normals_present:
                        normals_block = read_short_triplets_array(file_aem, v_num*3)
                        normals = [NoeVec3((x*NORMALS_UNIT_POINT, y*NORMALS_UNIT_POINT, z*NORMALS_UNIT_POINT)) for x, y, z in normals_block]
                    if unk_present:
                        try:
                            #print("some keys")
                            #print(f"vnum: {v_num}, {hex(v_num)}")
                            # file size - pos - 4*vnum*4 < 0 -> throw
                            some_twins = read_short_twins_array(file_aem, 2*v_num)
                            for i in range(0, len(some_quaternions), 5):
                                print(' '.join('{0}'.format(q) for q in some_quaternions[i:i+5]))
                        except Exception as e:
                            print("quaternions loading failed: {0}".format(e))
                    
                    if version == 1:
                        is_transparent = int.from_bytes(file_aem.read(1), 'little')

                else:
                    print("Unsupported file AEM version: {0}".format(version))
                    return -1

                # Read BoundingSphere
                if version in (3, 4, 5):
                    bounding_sphere = file_aem.read('<4f')
                    print('BoundingBox: x: {0}, y: {1}, z: {2}, r: {3}'.format(bounding_sphere[0], bounding_sphere[1], bounding_sphere[2], bounding_sphere[3]))
                    
                    #TODO
                importer_state = "BUILD_MESH"
                    
            if importer_state == "BUILD_MESH":

                bon_idx = submesh_num - submeshes_left
                
                bone_name = "submesh_" + str(bon_idx)
                
                # The bone's initial matrix is its position in the scene.
                # For this example, we'll just use an identity matrix because the vertex positions are already in world space.
                # If your vertices are in local space, this matrix should transform them to world space.
                bone_matrix = NoeMat43() 
                indices = [x for tup in faces for x in tup]
                # Parent each submesh bone to the root
                bone = NoeBone(bon_idx, bone_name, bone_matrix, "root")
                bones.append(bone)

                mesh = NoeMesh(indices, vertices, bone_name, bone_name)
                if normals_present:
                    mesh.setNormals(normals)
                if uvs_present:
                    mesh.setUVs(uvs)
                mesh.setMaterial("defMaterial")
                #bone_index_for_this_mesh = bon_idx + 1
                kf_bone = NoeKeyFramedBone(bon_idx)
                # Create vertex weights
                vert_weights = []
                for v in range(len(vertices)):
                    weight = NoeVertWeight([bon_idx], [1.0])
                    vert_weights.append(weight)
                
                mesh.setWeights(vert_weights)
                meshes.append(mesh)
                                                
                if version in (3, 4, 5):
                    #build_bounding_sphere(bounding_sphere, obj_name)
                    importer_state = "READ_ANIM"
                else:
                     
                    importer_state = "END"
                
                    
            if importer_state == "READ_ANIM": 
                print(importer_state)
                importer_state = "END"
                TRAN_X = 1
                TRAN_Y = 2 
                TRAN_Z = 4
                TRAN_XYZ = 7
                ROT_X = 0x40
                ROT_Y = 0x80 
                ROT_Z = 0x100
                ROT_XYZ = 0x1c0
                SCALE_X = 8
                SCALE_Y = 0x10
                SCALE_Z = 0x20
                SCALE_XYZ = 0x38
                ROT_Z, ROT_Y = ROT_Y, ROT_Z 

                # pivot_point
                if version in (3, 4, 5):
                    v0 = NoeVec3( (1.0, 0.0, 0.0) )
                    v1 = NoeVec3( (0.0, 1.0, 0.0) )
                    v2 = NoeVec3( (0.0, 0.0, 1.0) )
                    v3 = NoeVec3( (pivot_point[0], pivot_point[1], pivot_point[2]) )
                
                    boneMat = NoeMat43( (v0, v1, v2, v3) )
                else:
                    boneMat = NoeMat43()
                    bone = NoeBone(bon_idx, "mesh_{0}".format(bon_idx), boneMat, "mesh_0", 0)
                    bones.append(bone)
                if version in (4, 5):
                    import aem_red
                    mesh = aem_red.Mesh()
                    red_success = mesh.read_enhanced_data_from_file(file_aem, flags)
                    print((mesh.transform))
                    if red_success != -1 and len(mesh.transform.keyframes) > 0:
                        # group keyframes by type of tranformation                  
                        trans = defaultdict(lambda: [None, None, None])
                        rots = defaultdict(lambda: [None, None, None])
                        scals = defaultdict(lambda: [None, None, None])
                        
                        for kf in mesh.transform.keyframes:
                            type = kf["type"]
                            t = kf["time"]
                            
                            if type in (TRAN_X, TRAN_Y, TRAN_Z, TRAN_XYZ):
                                if type == TRAN_X:
                                    trans[t][0] = kf["values"][0]
                                elif type == TRAN_Y:
                                    trans[t][1] = kf["values"][0]
                                elif type == TRAN_Z:
                                    trans[t][2] = kf["values"][0]
                                elif type == TRAN_XYZ:
                                    trans[t] = list(kf["values"])

                            if type in (ROT_X, ROT_Y, ROT_Z, ROT_XYZ):
                                from math import pi

                                if type == ROT_X:
                                    rots[t][0] = kf["values"][0]/pi*180
                                elif type == ROT_Y:
                                    rots[t][1] = kf["values"][0]/pi*180
                                elif type == ROT_Z:
                                    rots[t][2] = kf["values"][0]/pi*180
                                elif type == ROT_XYZ:
                                    print("WARNING: ROT_XYZ detected. case for analysis.")
                                    rots[t] = list(r/pi*180 for r in kf["values"])

                            if type in (SCALE_X, SCALE_Y, SCALE_Z, SCALE_XYZ):
                                if type == SCALE_X:
                                    scals[t][0] = kf["values"][0]
                                elif type == SCALE_Y:
                                    scals[t][1] = kf["values"][0]
                                elif type == SCALE_Z:
                                    scals[t][2] = kf["values"][0]
                                elif type == SCALE_XYZ:
                                    scals[t] = list(kf["values"])
                        

                        all_times = sorted(list(set(trans.keys()) | set(rots.keys()) | set(scals.keys())))

                        trans_keys = []
                        scale_keys = []
                        rot_keys = []

                        for i, t in enumerate(all_times):
                            if None in trans[t]:
                                for j, tran in enumerate(trans[t]):
                                    if tran == None:
                                        for last_t in all_times[i:0:-1]:
                                            if trans[last_t][j] != None:
                                                trans[t][j] = trans[last_t][j]
                                                break
                                        if trans[t][j] == None and trans[0][j] != None:
                                            trans[t][j] = trans[0][j]
                                        if trans[t][j] is None:
                                            for next_t in all_times[i+1:]:
                                                if trans[next_t][j] != None:
                                                    trans[t][j] = trans[next_t][j]
                                                    break
                                        if trans[t][j] == None :
                                            trans[t][j] = 0
                            trans_keys.append(NoeKeyFramedValue(t, NoeVec3(trans[t])))
                            
                            if None in rots[t]:
                                for j, rot in enumerate(rots[t]):
                                    if rot == None:
                                        for last_t in all_times[i:0:-1]:
                                            if rots[last_t][j] != None:
                                                rots[t][j] = rots[last_t][j]
                                                break
                                        if rots[t][j] == None and rots[0][j] != None:
                                            rots[t][j] = rots[0][j]
                                        if rots[t][j] is None:
                                            for next_t in all_times[i+1:]:
                                                if rots[next_t][j] != None:
                                                    rots[t][j] = rots[next_t][j]
                                                    break
                                        if rots[t][j] == None :
                                            rots[t][j] = 0
                            rot_keys.append(NoeKeyFramedValue(t, NoeAngles(rots[t])))
                            
                            
                            if None in scals[t]:
                                for j, scale in enumerate(scals[t]):
                                    if scale == None:
                                        for last_t in all_times[i:0:-1]:
                                            if scals[last_t][j] != None:
                                                scals[t][j] = scals[last_t][j]
                                                break
                                        if scals[t][j] == None and scals[0][j] != None:
                                            scals[t][j] = scals[0][j]
                                        if scals[t][j] is None:
                                            for next_t in all_times[i+1:]:
                                                if scals[next_t][j] != None:
                                                    scals[t][j] = scals[next_t][j]
                                                    break
                                        if scals[t][j] == None:
                                            scals[t][j] = 1
                            scale_keys.append(NoeKeyFramedValue(t, NoeVec3(scals[t])))
                            #if i > 0:
                            #    last_t = all_times[i:0:-1][0]

                        kf_bone.setTranslation(trans_keys, noesis.NOEKF_TRANSLATION_VECTOR_3)

                        kf_bone.setRotation(rot_keys, noesis.NOEKF_ROTATION_EULER_XYZ_3)
                        print (scale_keys)
                        kf_bone.setScale(scale_keys, noesis.NOEKF_SCALE_VECTOR_3)
                        
                        # Add the animated bone to our list
                        if kf_bone.hasAnyKeys():
                            kf_bones.append(kf_bone)
                        if len(kf_bones) > 0:
                            # The bone list here should be the same as the main model's bone list
                            noe_anim = NoeKeyFramedAnim("lAnimation", bones, kf_bones, mesh.transform.timeBetweenFrames/1000) # 30.0 = frameRate
                            anims.append(noe_anim)
                      
                    if submeshes_left > 0:
                        importer_state = "READ_MESH"

            if importer_state == "END": 
                mdl = NoeModel(meshes, bones, anims)
                nmm = NoeModelMaterials([texture],[material])
                mdl.setModelMaterials(nmm)
                # Add the completed model to the list for Noesis to display
                mdlList.append(mdl)  
                return 1 

#write it
def noepyWriteModel(mdl, bs):
	anims = rapi.getDeferredAnims()

	bs.writeInt(len(mdl.meshes))
	for mesh in mdl.meshes:
		bs.writeString(mesh.name)
		bs.writeString(mesh.matName)
		bs.writeInt(len(mesh.indices))
		bs.writeInt(len(mesh.positions))
		bs.writeInt(len(mesh.normals))
		bs.writeInt(len(mesh.uvs))
		bs.writeInt(len(mesh.tangents))
		bs.writeInt(len(mesh.colors))
		bs.writeInt(mesh.flatWeightsPerVert)
		for idx in mesh.indices:
			bs.writeInt(idx)
		for vcmp in mesh.positions:
			bs.writeBytes(vcmp.toBytes())
		for vcmp in mesh.normals:
			bs.writeBytes(vcmp.toBytes())
		for vcmp in mesh.uvs:
			bs.writeBytes(vcmp.toBytes())
		for vcmp in mesh.tangents:
			bs.writeBytes(vcmp.toBytes())
		for vcmp in mesh.colors:
			bs.writeBytes(vcmp.toBytes())
		if mesh.flatWeightsPerVert > 0:
			bs.writeBytes(noePack("i" * len(mesh.positions) * mesh.flatWeightsPerVert, *mesh.flatWeightIdx))
			bs.writeBytes(noePack("f" * len(mesh.positions) * mesh.flatWeightsPerVert, *mesh.flatWeightVal))
		bs.writeInt(len(mesh.morphList))
		for mf in mesh.morphList:
			bs.writeInt(len(mf.positions))
			bs.writeInt(len(mf.normals))
			for vec in mf.positions:
				bs.writeBytes(vec.toBytes())
			for vec in mf.normals:
				bs.writeBytes(vec.toBytes())

	bs.writeInt(len(mdl.bones))
	for bone in mdl.bones:
		noepyWriteBone(bs, bone)

	bs.writeInt(len(anims))
	for anim in anims:
		bs.writeString(anim.name)
		bs.writeInt(len(anim.bones))
		for bone in anim.bones:
			noepyWriteBone(bs, bone)
		bs.writeInt(anim.numFrames)
		bs.writeFloat(anim.frameRate)
		bs.writeInt(len(anim.frameMats))
		for mat in anim.frameMats:
			bs.writeBytes(mat.toBytes())

	return 1

#when you want animation data to be written out with a model format, you should make a handler like this that catches it and defers it
def noepyWriteAnim(anims, bs):
	#it's good practice for an animation-deferring handler to inform the user that the format only supports joint model-anim export
	if rapi.isGeometryTarget() == 0:
		print("WARNING: Stand-alone animations cannot be written to the .noepy format.")
		return 0

	rapi.setDeferredAnims(anims)
	return 0

#write bone
def noepyWriteBone(bs, bone):
	bs.writeInt(bone.index)
	bs.writeString(bone.name)
	bs.writeString(bone.parentName)
	bs.writeInt(bone.parentIndex)
	bs.writeBytes(bone.getMatrix().toBytes())

#read bone
def noepyReadBone(bs):
	boneIndex = bs.readInt()
	boneName = bs.readString()
	bonePName = bs.readString()
	bonePIndex = bs.readInt()
	boneMat = NoeMat43.fromBytes(bs.readBytes(48))
	return NoeBone(boneIndex, boneName, boneMat, bonePName, bonePIndex)
