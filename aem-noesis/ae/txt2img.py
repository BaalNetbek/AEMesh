# based on https://github.com/K0lb3/tex2img/tree/master/src
# and https://github.com/GPUOpen-Tools/compressonator/blob/master/cmp_compressonatorlib/atc/
# pythonized by gemini 3 pro

import struct

def decompress_atc(data: bytes, width: int, height: int) -> bytearray:
    MASK_03 = 0x03
    MASK_0F = 0x0F
    MASK_1F = 0x1F
    MASK_3F = 0x3F

    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    stride = width * 4
    output_buffer = bytearray(stride * height)
    offset = 0
    data_len = len(data)

    
    for by in range(blocks_y):
        for bx in range(blocks_x):
            if offset + 16 > data_len:
                break

            w0, w1, color_word, indices_word = struct.unpack_from('<4I', data, offset)
            offset += 16
            
            alphas = [0] * 16

            alphas[0] = ((w0) & MASK_0F); alphas[0] |= alphas[0] << 4
            alphas[1] = ((w0 >> 4) & MASK_0F); alphas[1] |= alphas[1] << 4
            alphas[2] = ((w0 >> 8) & MASK_0F); alphas[2] |= alphas[2] << 4
            alphas[3] = ((w0 >> 12) & MASK_0F); alphas[3] |= alphas[3] << 4
            alphas[4] = ((w0 >> 16) & MASK_0F); alphas[4] |= alphas[4] << 4
            alphas[5] = ((w0 >> 20) & MASK_0F); alphas[5] |= alphas[5] << 4
            alphas[6] = ((w0 >> 24) & MASK_0F); alphas[6] |= alphas[6] << 4
            alphas[7] = ((w0 >> 28) & MASK_0F); alphas[7] |= alphas[7] << 4
            
            alphas[8] = ((w1) & MASK_0F); alphas[8] |= alphas[8] << 4
            alphas[9] = ((w1 >> 4) & MASK_0F); alphas[9] |= alphas[9] << 4
            alphas[10] = ((w1 >> 8) & MASK_0F); alphas[10] |= alphas[10] << 4
            alphas[11] = ((w1 >> 12) & MASK_0F); alphas[11] |= alphas[11] << 4
            alphas[12] = ((w1 >> 16) & MASK_0F); alphas[12] |= alphas[12] << 4
            alphas[13] = ((w1 >> 20) & MASK_0F); alphas[13] |= alphas[13] << 4
            alphas[14] = ((w1 >> 24) & MASK_0F); alphas[14] |= alphas[14] << 4
            alphas[15] = ((w1 >> 28) & MASK_0F); alphas[15] |= alphas[15] << 4

            color0_raw = color_word & 0xFFFF
            color1_raw = (color_word >> 16) & 0xFFFF
            mode = (color0_raw & 0x8000) != 0
                        
            r0_5b = (color0_raw >> 10) & MASK_1F; r0 = (r0_5b << 3) | (r0_5b >> 2)
            g0_5b = (color0_raw >> 5) & MASK_1F;  g0 = (g0_5b << 3) | (g0_5b >> 2)
            b0_5b = color0_raw & MASK_1F;         b0 = (b0_5b << 3) | (b0_5b >> 2)
            p0 = (r0, g0, b0)

            r1_5b = (color1_raw >> 11) & MASK_1F; r1 = (r1_5b << 3) | (r1_5b >> 2)
            g1_6b = (color1_raw >> 5) & MASK_3F;  g1 = (g1_6b << 2) | (g1_6b >> 4)
            b1_5b = color1_raw & MASK_1F;         b1 = (b1_5b << 3) | (b1_5b >> 2)
            p3 = (r1, g1, b1)

            if mode:
                p1 = (max(0, r0 - (r1 >> 2)), max(0, g0 - (g1 >> 2)), max(0, b0 - (b1 >> 2)))
                palette = [(0, 0, 0), p1, p0, p3]
            else:
                p1 = ((r0 * 5 + r1 * 3) >> 3, (g0 * 5 + g1 * 3) >> 3, (b0 * 5 + b1 * 3) >> 3)
                p2 = ((r0 * 3 + r1 * 5) >> 3, (g0 * 3 + g1 * 5) >> 3, (b0 * 3 + b1 * 5) >> 3)
                palette = [p0, p1, p2, p3]

            base_x = bx * 4
            base_y = by * 4
            
            for i in range(16):
                x = i % 4
                y = i // 4
                
                px = base_x + x
                py = base_y + y
                
                if px < width and py < height:
                    idx = (indices_word >> (2 * i)) & MASK_03
                    
                    r, g, b = palette[idx]
                    a = alphas[i]
                    pixel_offset = (py * stride) + (px * 4)
                    output_buffer[pixel_offset]     = r
                    output_buffer[pixel_offset + 1] = g
                    output_buffer[pixel_offset + 2] = b
                    output_buffer[pixel_offset + 3] = a

    return output_buffer