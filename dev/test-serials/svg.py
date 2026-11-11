import json, barcode, io
from PIL import Image, ImageDraw
import zxingcpp
def bars(code):
    m=barcode.get('code128',code).build()[0]   # '1101...' one char per module
    q=10; w=len(m)+2*q; h=48
    rects=[]; i=0
    while i<len(m):
        if m[i]=='1':
            j=i
            while j<len(m) and m[j]=='1': j+=1
            rects.append(f'<rect x="{q+i}" y="0" width="{j-i}" height="{h}"/>'); i=j
        else: i+=1
    svg=f'<svg viewBox="0 0 {w} {h}" preserveAspectRatio="none" role="img" aria-label="Barcode {code}"><rect width="{w}" height="{h}" fill="#FFFFFF"/><g fill="#000000">{"".join(rects)}</g></svg>'
    # check: draw the same modules as a picture and read it back
    s=4; im=Image.new('L',(w*s,h*s),255); dr=ImageDraw.Draw(im)
    for k,ch in enumerate(m):
        if ch=='1': dr.rectangle([(q+k)*s,0,(q+k+1)*s-1,h*s],fill=0)
    r=zxingcpp.read_barcodes(im); assert r and r[0].text==code,(code,r and r[0].text)
    return svg
d=json.load(open('codes.json'))
for o in d['items']+[d['mac']]: o['svg']=bars(o['code'])
json.dump(d,open('codes.json','w')); print('ok', len(d['items'][0]['svg']))
