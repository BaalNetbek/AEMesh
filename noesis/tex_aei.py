# based on https://github.com/Trimatix/AEPi/
# and https://web.archive.org/web/20230429101833fw_/https://zenhax.com/viewtopic.php?t=3349

# Baal Netbek 2025-2026

from inc_noesis import *
import sys, os
scriptDir = os.path.dirname(__file__) + '/ae/'
sys.path.append(scriptDir) if scriptDir not in sys.path else sys.path
import txt2img

MAGIC = "AEimage\x00"

UNKNOWN =              0b00000000
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

def isSupported(fmt):
    return fmt|MIPMAP in (
        f|MIPMAP for f in (
            RGBA, PVRTC12A, PVRTC14A, 
            RGBA_CubeMap,    
            ATC, ETC1_, ETC1__,          
            DXT1, DXT3,  DXT5, ETC1,
        )
    )  


def isCompressed(fmt):
    return fmt|MIPMAP not in (
        RGBA|MIPMAP,
        RGBA_CubeMap|MIPMAP
    )

def registerNoesisTypes():
    hETC1 = noesis.register("AEimage: ETC1 no alpha", ".aei")
    noesis.setHandlerTypeCheck(hETC1, aeiCheckETC)
    noesis.setHandlerLoadRGBA(hETC1, aeiLoadRGBA)
    # Saves with randomly picked by me encoder setting.
    noesis.setHandlerWriteRGBA(hETC1, aeiWriteETC)

    hETC1_ = noesis.register("AEimage: ETC1 0x14", ".aei")
    noesis.setHandlerTypeCheck(hETC1_, aeiCheckETC_)
    noesis.setHandlerLoadRGBA(hETC1_, aeiLoadRGBA)

    hETC1__ = noesis.register("AEimage: ETC1 0x17", ".aei")
    noesis.setHandlerTypeCheck(hETC1__, aeiCheckETC__) 
    noesis.setHandlerLoadRGBA(hETC1__, aeiLoadRGBA)

    hD1 = noesis.register("AEimage: DXT1", ".aei")
    noesis.setHandlerTypeCheck(hD1, aeiCheckD1)
    noesis.setHandlerLoadRGBA(hD1, aeiLoadRGBA)
    noesis.setHandlerWriteRGBA(hD1, aeiWriteD1)

    hD3 = noesis.register("AEimage: DXT3", ".aei")
    noesis.setHandlerTypeCheck(hD3, aeiCheckD3)
    noesis.setHandlerLoadRGBA(hD3, aeiLoadRGBA)
    noesis.setHandlerWriteRGBA(hD3, aeiWriteD3)

    hD5 = noesis.register("AEimage: DXT5", ".aei")
    noesis.setHandlerTypeCheck(hD5, aeiCheckD5)
    noesis.setHandlerLoadRGBA(hD5, aeiLoadRGBA)
    noesis.setHandlerWriteRGBA(hD5, aeiWriteD5)

    hATC = noesis.register("AEimage: ATC explicit alpha", ".aei")
    noesis.setHandlerTypeCheck(hATC, aeiCheckATC)
    noesis.setHandlerLoadRGBA(hATC, aeiLoadRGBA)

    hRaw = noesis.register("AEimage: RGBA", ".aei")
    noesis.setHandlerTypeCheck(hRaw, aeiCheckRaw)
    noesis.setHandlerLoadRGBA(hRaw, aeiLoadRGBA)
    noesis.setHandlerWriteRGBA(hRaw, aeiWriteRGBA)

    hCMap = noesis.register("AEimage: RGBA CubeMap", ".aei")
    noesis.setHandlerTypeCheck(hCMap, aeiCheckCMap)
    noesis.setHandlerLoadRGBA(hCMap, aeiLoadRGBA)

    hP12 = noesis.register("AEimage: PVRTC12A", ".aei")
    noesis.setHandlerTypeCheck(hP12, aeiCheckP12)
    noesis.setHandlerLoadRGBA(hP12, aeiLoadRGBA)

    hP14 = noesis.register("AEimage: PVRTC14A", ".aei")
    noesis.setHandlerTypeCheck(hP14, aeiCheckP14)
    noesis.setHandlerLoadRGBA(hP14, aeiLoadRGBA)

    hUnk = noesis.register("AEimage: unrecognised compression", ".aei")
    noesis.setHandlerTypeCheck(hUnk, aeiCheckUnk)
    noesis.setHandlerLoadRGBA(hUnk, aeiLoadRGBA)

	#noesis.logPopup()
    return 1

def aeiCheckETC(data):
    return aeiCheckType(data, ETC1)
def aeiCheckETC_(data):
    return aeiCheckType(data, ETC1_)
def aeiCheckETC__(data):
    return aeiCheckType(data, ETC1__)
def aeiCheckD1(data):
    return aeiCheckType(data, DXT1)
def aeiCheckD3(data):
    return aeiCheckType(data, DXT3)
def aeiCheckD5(data):
    return aeiCheckType(data, DXT5)
def aeiCheckATC(data):
    return aeiCheckType(data, ATC)
def aeiCheckRaw(data):
    return aeiCheckType(data, RGBA)
def aeiCheckCMap(data):
    return aeiCheckType(data, RGBA_CubeMap)    
def aeiCheckP12(data):
    return aeiCheckType(data, PVRTC12A)    
def aeiCheckP14(data):
    return aeiCheckType(data, PVRTC14A)    
def aeiCheckUnk(data):
    return aeiCheckType(data, UNKNOWN)

def aeiCheckType(data, format: int):
    bs = NoeBitStream(data)
    Magic = bs.readBytes(8).decode("ASCII")
    if Magic != MAGIC:
        return 0
    fformat = bs.readUByte()
    if format == UNKNOWN and not isSupported(fformat):
        print("AEimage: unrecognized compression flags: " + hex(fformat))
        noesis.logPopup()
        return 0 
    if fformat|MIPMAP == format|MIPMAP :

        return 1
    return 0
	
def aeiLoadRGBA(data, texList):
     
    file = NoeBitStream(data)
    magic = file.read(len(MAGIC))

    format = file.readUByte()
    mipmapped = (format & MIPMAP) != 0
    if mipmapped:
        print("mipmapping flag high")
    
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
        pass
        #print("Uncompressed_UI RGBA32")  
    elif format in (PVRTC12A, PVRTC12A | MIPMAP):
        #print("PVRTC12A 2BPP")
        texBytes = rapi.imageDecodePVRTC(texBytes, width, height, 2)
    elif format in (PVRTC14A, PVRTC14A | MIPMAP):
        #print("PVRTC14A 4BPP")
        texBytes = rapi.imageDecodePVRTC(texBytes, width, height, 4)
    elif format in (ATC, ATC | MIPMAP):
        #print("ATC interpolated alpha")
        texBytes = txt2img.decompress_atc(texBytes, width, height)
    elif format in (DXT1, DXT1 | MIPMAP):
        #print("DXT1")
        texFmt = noesis.NOESISTEX_DXT1
    elif format in (DXT3, DXT3 | MIPMAP):
        #print("DXT3")
        texFmt = noesis.NOESISTEX_DXT3
    elif format in (DXT5, DXT5 | MIPMAP):
        #print("DXT5")
        texFmt = noesis.NOESISTEX_DXT5
    elif format in (ETC1, ETC1 | MIPMAP):
        #print("ETC1")
        texBytes = rapi.imageDecodeETC(texBytes, width, height, "RGB")
    elif format in (ETC1_, ETC1_ | MIPMAP):
        #print("ETC1")
        texBytes = rapi.imageDecodeETC(texBytes, width, height, "RGB")
    elif format == ETC1__:
        #print("ETC1")
        texBytes = rapi.imageDecodeETC(texBytes, width, height, "RGB")
    else:
        print("WTF BOOM")

    texList.append(NoeTexture(rapi.getInputName(), width, height, texBytes, texFmt))

    numFonts = file.readUShort()
    print("{} texture(s) + {} font(s)".format(numTextures, numFonts))
    # parsing symbols at https://github.com/Trimatix/AEPi/blob/7acecbf2d495bb1781fac5a8da18e9ddaf3d416c/src/AEPi/image/AEI.py#L338
    
    return 1

def aeiWriteRGBA(data, width, height, bs):
    return aeiWrite(data, width, height, bs, RGBA)

def aeiWriteD5(data, width, height, bs):
    return aeiWrite(data, width, height, bs, DXT5)

def aeiWriteD3(data, width, height, bs):
    return aeiWrite(data, width, height, bs, DXT3)

def aeiWriteD1(data, width, height, bs):
    return aeiWrite(data, width, height, bs, DXT1)

def aeiWriteETC(data, width, height, bs):
    return aeiWrite(data, width, height, bs, ETC1)

def aeiWrite(data, width, height, file, format, textures = None):
    if textures == None: 
        textures = ((0, 0, width, height),)
    
    file.writeBytes(MAGIC.encode("ASCII"))
    file.writeUByte(format)
    mipmapped = (format & MIPMAP) != 0
    if mipmapped:
        print("mipmapping flag high")
    
    file.writeUShort(width)
    file.writeUShort(height)
    file.writeUShort(len(textures)) #numTextures

    for tex in textures:
        file.writeUShort(tex[0]) #texX      
        file.writeUShort(tex[1]) #texY      
        file.writeUShort(tex[2]) #texWidth  
        file.writeUShort(tex[3]) #texHeight 

    if format == DXT5:
        data = rapi.imageEncodeDXT(data, 4, width, height, noesis.FOURCC_BC3)
    elif format == DXT3:
        data = rapi.imageEncodeDXT(data, 4, width, height, noesis.FOURCC_BC2)
    elif format == DXT1:
        data = rapi.imageEncodeDXT(data, 4, width, height, noesis.FOURCC_BC1)

    # I have no idea what is format (0..11), if you care you can test it. Tell me then.   
    # {"imageEncodeETC", Noesis_ImageEncodeETC, METH_VARARGS, "returns encoded etc from rgba image. (Oiiii|i)"}, //args=source image array, width, height, format (0..11), quality, (optional) flags
    elif format in (ETC1, ETC1 | MIPMAP, ETC1_, ETC1_ | MIPMAP):
        data = rapi.imageEncodeETC(data, width, height, 11, 0)
    elif format == ETC1__:
        data = rapi.imageEncodeETC(data, width, height, 11, 10)
        
    # elif format in (PVRTC12A, PVRTC12A | MIPMAP):
    #     data = encodePVRTC(data, width, height, 2)
    # elif format in (PVRTC14A, PVRTC14A | MIPMAP):
    #     #print("PVRTC14A 4BPP")
    #     data = encodePVRTC(data, width, height, 4)
    # elif format in (ATC, ATC | MIPMAP):
    #     data = encodeATC(data, width, height)

    

    #texList.append(NoeTexture(rapi.getInputName(), width, height, texBytes, texFmt))
    if isCompressed(format):
        file.writeUInt(len(data))
    
    file.writeBytes(data)
    file.writeUShort(0)
    #print("{} texture(s) + {} font(s)".format(numTextures, numFonts))
    return 1
