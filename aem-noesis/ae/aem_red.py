import struct
import math


V3 = 0x04
V4 = 0x08
V5 = 0x10

# keframe types
# since V3 
TRAN_X = 1
TRAN_Y = 2 
TRAN_Z = 4
TRAN_XYZ = TRAN_X|TRAN_Y|TRAN_Z
ROT_X = 0x40
ROT_Y = 0x80 
ROT_Z = 0x100
ROT_XYZ = ROT_X|ROT_Y|ROT_Z
SCALE_X = 8
SCALE_Y = 0x10
SCALE_Z = 0x20
SCALE_XYZ = SCALE_X|SCALE_Y|SCALE_Z

#since V4
_UNKNOWN = 0x200 # need verify, internaly divided by 100

#since V5, 
UV_POS_X = 0x400
UV_POS_Y = 0x800
UV_POS_Z = 0x1000 # unused
UV_POS_XYZ = UV_POS_X|UV_POS_Y|UV_POS_Z # unused

UV_SCA_X = 0x2000
UV_SCA_Y = 0x4000
UV_SCA_Z = 0x8000 # unused
UV_SCA_XYZ = UV_SCA_X|UV_SCA_Y|UV_SCA_Z # unused

UV_ROT_X = 0x10000 # unused
UV_ROT_Y = 0x20000 # unused
UV_ROT_Z = 0x40000
UV_ROT_XYZ = UV_ROT_X|UV_ROT_Y|UV_ROT_Z # unused

# 'unused' flags are handled by the engine interally 
# but aren't used in the official AEMesh formats. 


_type2str = {
    TRAN_X:     "TRAN_X",
    TRAN_Y:     "TRAN_Y",
    TRAN_Z:     "TRAN_Z",
    TRAN_XYZ:   "TRAN_XYZ",
    ROT_X:      "ROT_X",
    ROT_Y:      "ROT_Y",
    ROT_Z:      "ROT_Z",
    ROT_XYZ:    "ROT_XYZ",
    SCALE_X:    "SCALE_X",
    SCALE_Y:    "SCALE_Y",
    SCALE_Z:    "SCALE_Z",
    SCALE_XYZ:  "SCALE_XYZ",
    _UNKNOWN:    "OPACITY?",
    UV_SCA_X:   "UV_SCA_X",
    UV_SCA_Y:   "UV_SCA_Y",
    UV_POS_X:   "UV_POS_X",
    UV_POS_Y:   "UV_POS_Y",
    UV_ROT_Z:   "UV_ROT_Z",
}
    

class Transform:
    def __init__(self):
        self.keyframes = []
        self.timeBetweenFrames = 0
        self.max_time = 0
        self.min_time = 0

    def insert_keyframe(self, values, key_type, time):
        self.keyframes.append({
            'values': values if isinstance(values, list) else [values], # list of 3 values x, y, z
            'type': key_type, 
            'time': time
        })

    def get_keyframe_count(self):
        return len(self.keyframes)

    def set_animation_range_in_time(self, time_between_frames, max_time, min_time):
        self.timeBetweenFrames = time_between_frames
        self.max_time = max_time
        self.min_time = min_time

    def __str__(self):
        """
        User-friendly string representation of the Transform object
        """
        keyframes_str = "\n".join(
            "  Keyframe "+str(i)+": time="+str(kf['time'])+", "
            ""+_type2str.get(kf['type'], "type=0x{:x}".format(kf['type']))+", "
            "values="+str(kf['values'])
            for i, kf in enumerate(self.keyframes)
        ) if self.keyframes else "  No keyframes"

        return ("Transform:\n"
                "  Number of keyframes: "+str(len(self.keyframes))+"\n"
                "  Time between frames: "+str(self.timeBetweenFrames)+"\n"
                "  Animation range: ["+str(self.min_time)+", "+str(self.max_time)+"\n"
                "  Time between frames: "+ str(self.timeBetweenFrames) + " ms"+"\n"
                "  Keyframes:\n"+str(keyframes_str))

    def __repr__(self):
        """
        Detailed string representation for debugging
        """
        return ("Transform(keyframes="+str(self.keyframes)+", "
                "timeBetweenFrames="+str(self.timeBetweenFrames)+", "
                "max_time="+str(self.max_time)+", "
                "min_time="+str(self.min_time))


class Mesh:
    def __init__(self):
        self.bsphereX = 0
        self.bsphereY = 0
        self.bsphereZ = 0
        self.bsphereR = 0
        self.transform = None
        self.uv_animated = False

    def read_enhanced_data_from_file(self, file_obj, version):
        time_between_frames = float('inf')
        transform = Transform()
        try:
            """
            # Read bounding sphere data (4 floats = 16 bytes)
            sphere_data = file_obj.read(16)
            if len(sphere_data) != 16:
                return -1
                
            self.bsphereX, self.bsphereY, self.bsphereZ, self.bsphereR = struct.unpack('4f', sphere_data)
            
            # Rotate BSphere center
            self.bsphereY, self.bsphereZ = self.bsphereZ, -self.bsphereY
            """
            #transform = Transform()

            
            type_data = file_obj.read(2)
            if len(type_data) != 2:
                return -1
            type_val = struct.unpack('h', type_data)[0]

            # Translation
            if type_val == 1:
                key_frame_cnt = struct.unpack('h', file_obj.read(2))[0]
                for _ in range(key_frame_cnt):
                    time = struct.unpack('f', file_obj.read(4))[0]
                    if 0.0 < time < time_between_frames:
                        time_between_frames = time
                    values = struct.unpack('3f', file_obj.read(12))
                    transform.insert_keyframe(list(values), TRAN_XYZ, int(time))
            elif type_val == 0:
                for i in range(3):
                    key_frame_cnt = struct.unpack('h', file_obj.read(2))[0]
                    for _ in range(key_frame_cnt):
                        time = struct.unpack('f', file_obj.read(4))[0]
                        if 0.0 < time < time_between_frames:
                            time_between_frames = time
                        value = struct.unpack('f', file_obj.read(4))[0]
                        if i == 2:
                            transform.insert_keyframe(value, TRAN_Y, int(time))
                        elif i == 1:
                            transform.insert_keyframe(-value, TRAN_Z, int(time))
                        else:
                            transform.insert_keyframe(value, TRAN_X, int(time))

            
            type_data = file_obj.read(2)
            if len(type_data) != 2:
                return -1
            type_val = struct.unpack('h', type_data)[0]

            # Rotation
            if type_val == 1:
                key_frame_cnt = struct.unpack('h', file_obj.read(2))[0]
                for _ in range(key_frame_cnt):
                    time = struct.unpack('f', file_obj.read(4))[0]
                    if 0.0 < time < time_between_frames:
                        time_between_frames = time
                    values = struct.unpack('3f', file_obj.read(12))
                    transform.insert_keyframe(list(values), ROT_XYZ, int(time))
            elif type_val == 0:
                for i in range(3):
                    key_frame_cnt = struct.unpack('h', file_obj.read(2))[0]
                    for _ in range(key_frame_cnt):
                        time = struct.unpack('f', file_obj.read(4))[0]
                        if 0.0 < time < time_between_frames:
                            time_between_frames = time
                        value = struct.unpack('f', file_obj.read(4))[0]
                        key_types = [ROT_X, ROT_Y, ROT_Z]
                        # if i == 1:
                        #     print(file_obj.tell())
                        transform.insert_keyframe(value, key_types[i], int(time))

            
            type_data = file_obj.read(2)
            if len(type_data) != 2:
                return -1
            type_val = struct.unpack('h', type_data)[0]

            # Scale
            if type_val == 1:
                key_frame_cnt = struct.unpack('h', file_obj.read(2))[0]
                for _ in range(key_frame_cnt):
                    time = struct.unpack('f', file_obj.read(4))[0]
                    if 0.0 < time < time_between_frames:
                        time_between_frames = time
                    values = struct.unpack('3f', file_obj.read(12))
                    transform.insert_keyframe(list(values), SCALE_XYZ, int(time))
            elif type_val == 0:
                for i in range(3):
                    key_frame_cnt = struct.unpack('h', file_obj.read(2))[0]
                    for _ in range(key_frame_cnt):
                        time = struct.unpack('f', file_obj.read(4))[0]
                        if 0.0 < time < time_between_frames:
                            time_between_frames = time
                        value = struct.unpack('f', file_obj.read(4))[0]
                        key_types = [SCALE_X, SCALE_Y, SCALE_Z]
                        transform.insert_keyframe(value, key_types[i], int(time))

            if version in (V4, V5):
                type_val = struct.unpack('h', file_obj.read(2))[0]
                if type_val == 2:
                    key_frame_cnt = struct.unpack('h', file_obj.read(2))[0]
                    for _ in range(key_frame_cnt):
                        time = struct.unpack('f', file_obj.read(4))[0]
                        if 0.0 < time < time_between_frames:
                            time_between_frames = time
                        value = struct.unpack('f', file_obj.read(4))[0]
                        transform.insert_keyframe(value, _UNKNOWN, int(time))

            # UV
            if version == V5:
                uv_keyframes = struct.unpack('h', file_obj.read(2))[0]
                if uv_keyframes != 0:
                    key_types = [UV_POS_X, UV_POS_Y, UV_SCA_X, UV_SCA_Y, 0, 0, UV_ROT_Z]
                    for i in range(7):
                        key_frame_cnt = struct.unpack('h', file_obj.read(2))[0]
                        for _ in range(key_frame_cnt):
                            time = struct.unpack('f', file_obj.read(4))[0]
                            if 0.0 < time < time_between_frames:
                                time_between_frames = time
                            value = struct.unpack('f', file_obj.read(4))[0]
                            value /= 100.0
                            if i == 6:
                                value = (value * math.pi) / 180.0
                            transform.insert_keyframe(value, key_types[i], int(time))
                            self.uv_animated = True
            padding = file_obj.read(2)
            if padding != b'\x00\x00':
                print("UNEXPECTED BYTES %s @ %d" % (padding.hex() ,file_obj.tell()-2))

            if transform.get_keyframe_count() < 1:
                return -1
            else:
                self.transform = transform
                try:
                    transform.timeBetweenFrames = int(time_between_frames)
                except Exception:
                    print("Invalid time between frames.")
                    transform.timeBetweenFrames = 1000
                transform.set_animation_range_in_time(
                    transform.timeBetweenFrames, 10000000, 0
                )
                return 1

        except (struct.error, IOError):
            return -1