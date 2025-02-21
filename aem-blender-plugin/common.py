SCALE = 0.01

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