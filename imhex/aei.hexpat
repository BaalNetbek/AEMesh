// uncompressed textures only
struct tex{
    u16 x,y,w,h;
};

struct aei{
    char aei [8];
    u8 type;
    u16 w,h;
    u16 ntex;
    tex texs [ntex];
    u8 color[w*h*4];
}[[hex::visualize("bitmap", this.color, w, h)]];


aei h @0;