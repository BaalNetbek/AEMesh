# based on https://github.com/Trimatix/AEPi/
# and https://web.archive.org/web/20230429101833fw_/https://zenhax.com/viewtopic.php?t=3349

from inc_noesis import *
import sys, os
scriptDir = os.path.dirname(__file__) + '/ae/'
sys.path.append(scriptDir) if scriptDir not in sys.path else sys.path
import txt2img

MAGIC = "AEimage\x00"

Unknown =                   0b00000000
Uncompressed =              0b00000011
Uncompressed_UI =           0b00000001
Uncompressed_CubeMap_PC =   0b10000001
Uncompressed_CubeMap =      0b11000010
PVRTC12A =                  0b00001101
PVRTC14A =                  0b00010000
ATC =                       0b00010001
DXT1 =                      0b00100000
DXT3 =                      0b00100001
DXT5 =                      0b00100100
ETC1 =                      0b01000000
ETC2 =                      0b00010101 #!

def isCompressed(fmt):
    return fmt not in (
        Unknown,
        Uncompressed_UI,
        Uncompressed_CubeMap,
        Uncompressed_CubeMap_PC
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
    mipmapped = (format & 2) != 0
    format &= ~2
    
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
    if format == Uncompressed_UI:
        print("Uncompressed_UI RGBA32")
    elif format == PVRTC12A:
        print("PVRTC12A 2BPP")
        texBytes = rapi.imageDecodePVRTC(texBytes, width, height, 2)
    elif format == PVRTC14A:
        print("PVRTC14A 4BPP")
        texBytes = rapi.imageDecodePVRTC(texBytes, width, height, 4)
    elif format == ATC:
        print("ATC interpolated alpha")
        texBytes = txt2img.decompress_atc(texBytes, width, height, True) # imports slow and artifacts around (asquare) semitransparent pixels
    elif format == DXT1:
        print("DXT1")
        texFmt = noesis.NOESISTEX_DXT1
    elif format == DXT3:
        print("DXT3")
        texFmt = noesis.NOESISTEX_DXT3
    elif format == DXT5:
        print("DXT5")
        texFmt = noesis.NOESISTEX_DXT5
    elif format == ETC1:
        print("ETC1")
        texBytes = rapi.imageDecodeETC(texBytes, width, height, "RGB")
    elif format == ETC2:
        print("ETC2")
        texBytes = rapi.imageDecodeETC(texBytes, width, height, "RGB")
    else:
        print("WTF BOOM")

    texList.append(NoeTexture(rapi.getInputName(), width, height, texBytes, texFmt))
    return 1

