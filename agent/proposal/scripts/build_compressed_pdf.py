# -*- coding: utf-8 -*-
"""usage: python3 build_compressed.py <srcdir with 01..20.pdf> <output pdf path>"""
import sys, os
from pypdf import PdfWriter, PdfReader
from pypdf.generic import RectangleObject, NameObject, NumberObject, DecodedStreamObject
from PIL import Image
src, path = sys.argv[1], sys.argv[2]
w=PdfWriter()
for i in range(1,21):
    r=PdfReader(os.path.join(src,f"{i:02d}.pdf"))
    for p in r.pages:
        W=float(p.mediabox.width); H=float(p.mediabox.height)
        if (W,H)!=(1600.0,900.0):
            # frame drop-shadow padding: symmetric left/right, top pad = 26 (1700) / 27 (1705)
            l=round((W-1600)/2); t=26 if W<1702 else 27
            box=RectangleObject([l,H-t-900,l+1600,H-t]); p.mediabox=box; p.cropbox=box; p.trimbox=box
        w.add_page(p)
def tiny(gray):
    s=DecodedStreamObject()
    s[NameObject("/Type")]=NameObject("/XObject"); s[NameObject("/Subtype")]=NameObject("/Image")
    s[NameObject("/Width")]=NumberObject(1); s[NameObject("/Height")]=NumberObject(1)
    s[NameObject("/BitsPerComponent")]=NumberObject(8)
    s[NameObject("/ColorSpace")]=NameObject("/DeviceGray" if gray else "/DeviceRGB")
    s.set_data(b"\x00" if gray else b"\xff\xff\xff"); return s
for p in w.pages:
    xo=p["/Resources"].get("/XObject")
    if not xo: continue
    xo=xo.get_object()
    for name,ref in list(xo.items()):
        obj=ref.get_object()
        if obj.get("/Subtype")!="/Image": continue
        if int(obj["/Width"])>=3000 and int(obj["/Height"])>=1800 and "/SMask" in obj:
            img=tiny(False); img[NameObject("/SMask")]=w._add_object(tiny(True)); xo[NameObject(name)]=w._add_object(img)
    for im in p.images:
        img=im.image; wpx,hpx=img.size
        if wpx*hpx < 300000 or wpx>=3000: continue
        if img.mode=="RGBA" and img.getchannel("A").getextrema()[0] < 255: continue
        rgb=img.convert("RGB"); scale=min(1.0, 2000/max(wpx,hpx))
        if scale<1: rgb=rgb.resize((int(wpx*scale),int(hpx*scale)), Image.LANCZOS)
        im.replace(rgb, quality=82)
for p in w.pages: p.compress_content_streams()
w.compress_identical_objects(remove_duplicates=True, remove_unreferenced=True)
w.add_metadata({"/Title":os.path.splitext(os.path.basename(path))[0]})
with open(path,"wb") as f: w.write(f)
r=PdfReader(path); print(len(r.pages),"pages", round(os.path.getsize(path)/1024/1024,1),"MB", set((float(p.cropbox.width),float(p.cropbox.height)) for p in r.pages))
