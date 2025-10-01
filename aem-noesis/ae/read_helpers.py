from inc_noesis import NoeVec3

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
