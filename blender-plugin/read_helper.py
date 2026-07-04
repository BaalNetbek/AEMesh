from struct import unpack

def read_float(file):
    return unpack('f', file.read(4))[0]
    
def read_short(file):
    return unpack('h', file.read(2))[0]

def read_ushort(file):
    return unpack('H', file.read(2))[0]

def read_short_array(file, len): 
    return list(unpack(f'{len}h', file.read(len*2)))
    
def read_float_array(file, len):
    return list(unpack(f'{len}f', file.read(len*4)))

def read_short_twins_array(file, len, endian='<'):
    """Reads a flat array of shorts from a file and converts it into a list of 2-tuples."""
    if (len % 2 != 0):
        raise ValueError("Twins array length must be a multiple of 2")
    flat_array = unpack(f'{endian}{len}h', file.read(len * 2))
    return list(zip(flat_array[0::2], flat_array[1::2]))

def read_short_triplets_array(file, len, endian='<'):
    """Reads a flat array of shorts from a file and converts it into a list of 3-tuples."""
    if (len % 3 != 0):
        raise ValueError("Triplets array length must be a multiple of 3")
    flat_array = unpack(f'{endian}{len}h', file.read(len * 2))
    return list(zip(flat_array[0::3], flat_array[1::3], flat_array[2::3]))

def read_ushort_triplets_array(file, len, endian='<'):
    """Reads a flat array of shorts from a file and converts it into a list of 3-tuples."""
    if (len % 3 != 0):
        raise ValueError("Triplets array length must be a multiple of 3")
    flat_array = unpack(f'{endian}{len}H', file.read(len * 2))
    return list(zip(flat_array[0::3], flat_array[1::3], flat_array[2::3]))

def read_short_quadruplets_array(file, len, endian='<'):
    """Reads a flat array of shorts from a file and converts it into a list of 4-tuples."""
    if (len % 4 != 0):
        raise ValueError("Quadruplets array length must be a multiple of 4")
    flat_array = unpack(f'{endian}{len}h', file.read(len * 2))
    return list(zip(flat_array[0::4], flat_array[1::4], flat_array[2::4], flat_array[3::4]))

def read_short_hexlets_array(file, len, endian='<'):
    """Reads a flat array of shorts from a file and converts it into a list of 4-tuples."""
    if (len % 6 != 0):
        raise ValueError("Hexlets array length must be a multiple of 4")
    flat_array = unpack(f'{endian}{len}h', file.read(len * 2))
    return list(zip(flat_array[0::6], flat_array[1::6], flat_array[2::6], flat_array[3::6], flat_array[4::6], flat_array[5::6]))    

def read_float_quadruplets_array(file, len, endian='<'):
    """Reads a flat array of floats from a file and converts it into a list of 4-tuples."""
    if (len % 4 != 0):
        raise ValueError("Quadruplets array length must be a multiple of 4")
    flat_array = unpack(f'{endian}{len}f', file.read(len * 4))
    return list(zip(flat_array[0::4], flat_array[1::4], flat_array[2::4], flat_array[3::4]))
  
def read_float_triplets_array(file, len, endian='<'):
    """Reads a flat array of floats from a file and converts it into a list of 3-tuples."""
    if (len % 3 != 0):
        raise ValueError("Triplets array length must be a multiple of 3")
    flat_array = unpack(f'{endian}{len}f', file.read(len * 4))
    return list(zip(flat_array[0::3], flat_array[1::3], flat_array[2::3]))

def read_float_twins_array(file, len, endian='<'):
    """Reads a flat array of floats from a file and converts it into a list of 2-tuples."""
    if (len % 2 != 0):
        raise ValueError("Twins array length must be a multiple of 2")
    flat_array = unpack(f'{endian}{len}f', file.read(len * 4))
    return list(zip(flat_array[0::2], flat_array[1::2]))