// v4, v5 only
struct header {
    char magic[9];
    u8 flags;
    u16 meshCnt;
};

struct key4{
    float time;
    float val;
};
struct key12{
    float time;
    float vals[3];
};
struct anim0{
    u16 keyCntX;
    key4 keysX[keyCntX];
    u16 keyCntY;
    key4 keysY[keyCntY];
    u16 keyCntZ;
    key4 keysZ[keyCntZ];
};
struct anim1{
    u16 keyCnt;
    key12 keysXYZ[keyCnt];
};
struct anim2{
    u16 keyCnt;
    key4 keys[keyCnt];
};
struct anim{
    u16 transType;
    if (transType == false)
        anim0 translation;
    if (transType == true)
        anim1 translation;

    u16 rotType;
    if (rotType == false)
        anim0 rotation;
    if (rotType == true)
        anim1 rotation;
    
    u16 scaleType;
    if (scaleType == false)
        anim0 scale;
    if (scaleType == true)
        anim1 scale;
    
    // V4 and V5 special keys 
    u16 typ4;
    if (typ4 == 2 && (h.flags & (8 | 16)))
        anim2 keys4;
    
    // V5 special keys 
    u16 uv_keys; // if V4 this acts as just padding
    if (uv_keys != 0 && (h.flags & 16)) {
        anim2 uv_pos_x;
        anim2 uv_pos_y;
        anim2 uv_sca_x;
        anim2 uv_sca_y;
        anim2 specialKey5;
        anim2 specialKey6;
        anim2 uv_rot_z;
        s16 pad;
    }
    
};

struct mesh {
    float pivot[3];
    u16 fnum;
    u16 faces[fnum];
    u16 vnum;
    float verts[vnum*3];
    float uvs[vnum*2];
    float normals[vnum*3];
    if (h.flags & 8)
    float cols[vnum*4];
    float bbox[4];
    anim a;
}[[hex::visualize("3d", verts, faces)]];

header h @ 0;
mesh m[h.meshCnt] @ sizeof(h);