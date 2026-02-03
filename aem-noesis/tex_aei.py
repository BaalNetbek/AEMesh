# based on https://github.com/Trimatix/AEPi/
# and https://web.archive.org/web/20230429101833fw_/https://zenhax.com/viewtopic.php?t=3349

from inc_noesis import *
import sys, os
scriptDir = os.path.dirname(__file__) + '/ae/'
sys.path.append(scriptDir) if scriptDir not in sys.path else sys.path
import txt2img

MAGIC = "AEimage\x00"

# Unknown =                   0b00000000
# Uncompressed =              0b00000011
# Uncompressed_CubeMap =      0b11000010
RGBA =                 0b00000001 # 0x01
PVRTC12A =             0b00001101 # 0x0d
PVRTC14A =             0b00010000 # 0x10
RGBA_CubeMap =         0b10000001 # 0x81
ATC =                  0b00010001 # 0x11
ETC1_ =                0b00010100 # 0x14
ETC1__ =               0b00010111 # 0x17
DXT1 =                 0b00100000 # 0x20
DXT3 =                 0b00100001 # 0x21
DXT5 =                 0b00100100 # 0x24
ETC1 =                 0b01000000 # 0x40

MIPMAP =               0b00000010 # 0x02

def isCompressed(fmt):
    return fmt not in (
    #    Unknown,
    #    Uncompressed_CubeMap,
        RGBA,
        RGBA_CubeMap
    )

def registerNoesisTypes():
    handle = noesis.register("AEimage", ".aei")
    noesis.setHandlerTypeCheck(handle, aeiCheckType)
    noesis.setHandlerLoadRGBA(handle, aeiLoadRGBA)
	#noesis.logPopup()
    return 1

def aeiCheckType(data):
    bs = NoeBitStream(data)
    Magic = bs.readBytes(8).decode("ASCII")
    if Magic != MAGIC:
        return 0
    return 1
	
def aeiLoadRGBA(data, texList):
     
    file = NoeBitStream(data)
    magic = file.read(len(MAGIC))

    format = file.readUByte()
    mipmapped = (format & MIPMAP) != 0
    #format &= ~2
    
    width = file.readUShort()
    height = file.readUShort()
    numTextures = file.readUShort()

    textures = []
    for _ in range(numTextures):
        texX = file.readUShort()
        texY = file.readUShort()
        texWidth = file.readUShort()
        texHeight = file.readUShort()
        textures.append((texX, texY, texWidth, texHeight))

    if isCompressed(format):
        imageLength = file.readUInt()
    else:
        imageLength = 4 * width * height      
 
    texBytes = file.readBytes(imageLength)      
    texFmt = noesis.NOESISTEX_RGBA32
    if format in (RGBA, RGBA | MIPMAP):
        print("Uncompressed_UI RGBA32")  
    elif format in (PVRTC12A, PVRTC12A | MIPMAP):
        print("PVRTC12A 2BPP")
        texBytes = rapi.imageDecodePVRTC(texBytes, width, height, 2)
    elif format in (PVRTC14A, PVRTC14A | MIPMAP):
        print("PVRTC14A 4BPP")
        texBytes = rapi.imageDecodePVRTC(texBytes, width, height, 4)
    elif format in (ATC, ATC | MIPMAP):
        print("ATC interpolated alpha")
        texBytes = txt2img.decompress_atc(texBytes, width, height) # imports slow and artifacts around (asquare) semitransparent pixels
    elif format in (DXT1, DXT1 | MIPMAP):
        print("DXT1")
        texFmt = noesis.NOESISTEX_DXT1
    elif format in (DXT3, DXT3 | MIPMAP):
        print("DXT3")
        texFmt = noesis.NOESISTEX_DXT3
    elif format in (DXT5, DXT5 | MIPMAP):
        print("DXT5")
        texFmt = noesis.NOESISTEX_DXT5
    elif format in (ETC1, ETC1 | MIPMAP):
        print("ETC1")
        texBytes = rapi.imageDecodeETC(texBytes, width, height, "RGB")
    elif format in (ETC1_, ETC1_ | MIPMAP):
        print("ETC1")
        texBytes = rapi.imageDecodeETC(texBytes, width, height, "RGB")
    elif format == ETC1__:
        print("ETC1")
        texBytes = rapi.imageDecodeETC(texBytes, width, height, "RGB")
    else:
        print("WTF BOOM")

    texList.append(NoeTexture(rapi.getInputName(), width, height, texBytes, texFmt))
    return 1

