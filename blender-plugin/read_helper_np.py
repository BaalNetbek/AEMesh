import numpy as np

def read_float(file):
    return np.frombuffer(file.read(4), dtype=np.float32)[0]

def read_short(file):
    return np.frombuffer(file.read(2), dtype=np.int16)[0]

def read_short_array(file, length):
    return np.frombuffer(file.read(length * 2), dtype=np.int16).tolist()

def read_float_array(file, length):
    return np.frombuffer(file.read(length * 4), dtype=np.float32).tolist()

def read_tuples_array(file, length, tuple_size, dtype, endian='<'):
    """Reads a flat array from a file and converts it into a list of tuples."""
    dtype_map = {'short': np.int16, 'float': np.float32}
    
    if length % tuple_size != 0:
        raise ValueError(f"Array length must be a multiple of {tuple_size}")
    
    data_type = dtype_map[dtype]
    data = np.frombuffer(file.read(length * data_type().nbytes), dtype=endian + data_type().name)
    
    return [tuple(data[i:i+tuple_size]) for i in range(0, length, tuple_size)]

def read_short_twins_array(file, length, endian='<'):
    return read_tuples_array(file, length, 2, 'short', endian)

def read_short_triplets_array(file, length, endian='<'):
    return read_tuples_array(file, length, 3, 'short', endian)

def read_short_quadruplets_array(file, length, endian='<'):
    return read_tuples_array(file, length, 4, 'short', endian)

def read_float_twins_array(file, length, endian='<'):
    return read_tuples_array(file, length, 2, 'float', endian)

def read_float_triplets_array(file, length, endian='<'):
    return read_tuples_array(file, length, 3, 'float', endian)

def read_float_quadruplets_array(file, length, endian='<'):
    return read_tuples_array(file, length, 4, 'float', endian)
