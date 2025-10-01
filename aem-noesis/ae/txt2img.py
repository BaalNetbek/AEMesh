# based on https://github.com/K0lb3/tex2img/tree/master/src
# and https://github.com/GPUOpen-Tools/compressonator/blob/master/cmp_compressonatorlib/atc/

import struct

def _unpack_bc4(compressedBlock):
    dwords = struct.unpack('<II', compressedBlock)
    alpha = [0] * 8
    alpha[0] = dwords[0] & 0xff
    alpha[1] = (dwords[0] >> 8) & 0xff

    if alpha[0] > alpha[1]:  # 8-alpha mode
        alpha[2] = (6 * alpha[0] + 1 * alpha[1] + 3) // 7
        alpha[3] = (5 * alpha[0] + 2 * alpha[1] + 3) // 7
        alpha[4] = (4 * alpha[0] + 3 * alpha[1] + 3) // 7
        alpha[5] = (3 * alpha[0] + 4 * alpha[1] + 3) // 7
        alpha[6] = (2 * alpha[0] + 5 * alpha[1] + 3) // 7
        alpha[7] = (1 * alpha[0] + 6 * alpha[1] + 3) // 7
    else:  # 6-alpha mode
        alpha[2] = (4 * alpha[0] + 1 * alpha[1] + 2) // 5
        alpha[3] = (3 * alpha[0] + 2 * alpha[1] + 2) // 5
        alpha[4] = (2 * alpha[0] + 3 * alpha[1] + 2) // 5
        alpha[5] = (1 * alpha[0] + 4 * alpha[1] + 2) // 5
        alpha[6], alpha[7] = 0, 255

    alphaBlock = [0] * 16
    
    for i in range(16):        
        if (i < 5):
            index = (dwords[0] & (0x7 << (16 + (i * 3)))) >> (16 + (i * 3))
        elif (i > 5):
            index = (dwords[1] & (0x7 << (2 + (i - 6) * 3))) >> (2 + (i - 6) * 3)
        else: # i == 5
            index = (dwords[0] & 0x80000000) >> 31
            index |= (dwords[1] & 0x3) << 1
            
        alphaBlock[i] = alpha[index]

    return alphaBlock

def _unpack_atc(block):
    c0_16, c1_16, sels = struct.unpack('<HHI', block)
    mode = (c0_16 & 0x8000) != 0

    r0_5b = (c0_16 >> 10) & 31; r0 = (r0_5b << 3) | (r0_5b >> 2)
    g0_5b = (c0_16 >> 5) & 31;  g0 = (g0_5b << 3) | (g0_5b >> 2)
    b0_5b = c0_16 & 31;         b0 = (b0_5b << 3) | (b0_5b >> 2)
    p0 = (r0, g0, b0)

    r1_5b = (c1_16 >> 11) & 31; r1 = (r1_5b << 3) | (r1_5b >> 2)
    g1_6b = (c1_16 >> 5) & 63;  g1 = (g1_6b << 2) | (g1_6b >> 4)
    b1_5b = c1_16 & 31;         b1 = (b1_5b << 3) | (b1_5b >> 2)
    p3 = (r1, g1, b1)

    if mode:
        p1 = (max(0, r0 - (r1 >> 2)), max(0, g0 - (g1 >> 2)), max(0, b0 - (b1 >> 2)))
        palette = [(0, 0, 0), p1, p0, p3]
    else:
        p1 = ((r0 * 5 + r1 * 3) >> 3, (g0 * 5 + g1 * 3) >> 3, (b0 * 5 + b1 * 3) >> 3)
        p2 = ((r0 * 3 + r1 * 5) >> 3, (g0 * 3 + g1 * 5) >> 3, (b0 * 3 + b1 * 5) >> 3)
        palette = [p0, p1, p2, p3]

    pixels = [None] * 16
    for i in range(16):
        pixels[i] = palette[(sels >> (i * 2)) & 3]
    return pixels

def decompress_atc(data, width, height, has_alpha):
    if width == 0 or height == 0:
        return b''

    block_size = 16 if has_alpha else 8
    pixel_size = 4 if has_alpha else 3
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    
    dst = bytearray(width * height * pixel_size)
    offset = 0

    for by in range(blocks_y):
        for bx in range(blocks_x):
            block = data[offset : offset + block_size]
            offset += block_size

            if has_alpha:
                alphas = _unpack_bc4(block[:8])
                rgbs = _unpack_atc(block[8:])
                pixels = [(r, g, b, a) for (r, g, b), a in zip(rgbs, alphas)]
            else:
                pixels = _unpack_atc(block)

            for y in range(4):
                py = by * 4 + y
                if py >= height:
                    break
                for x in range(4):
                    px = bx * 4 + x
                    if px >= width:
                        break
                    
                    p_idx = y * 4 + x
                    d_idx = (py * width + px) * pixel_size
                    dst[d_idx:d_idx + pixel_size] = pixels[p_idx]
    
    return bytes(dst)