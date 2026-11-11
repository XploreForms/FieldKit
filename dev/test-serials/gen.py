import random, re, json, subprocess, io
import barcode
from barcode.writer import SVGWriter, ImageWriter
import zxingcpp
from PIL import Image
random.seed(20261108)
D=lambda n:''.join(random.choice('0123456789') for _ in range(n))
H=lambda n:''.join(random.choice('0123456789ABCDEF') for _ in range(n))
A=lambda n:''.join(random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ') for _ in range(n))
AN=lambda n:''.join(random.choice('ABCDEFGHJKLMNPQRSTUVWXYZ0123456789') for _ in range(n))
# one generator per serial pattern in fieldkit-catalog.js (same order)
GEN=[lambda:'854V6'+AN(11), lambda:'834V6'+AN(11), lambda:'O5SGS'+D(9), lambda:'O5MGS'+D(9), lambda:'O5PGS'+D(9), lambda:'B5SGS'+D(9),
     lambda:'OAK'+A(2)+D(9), lambda:'GMK'+D(12), lambda:'GMB'+D(9), lambda:'BY'+D(10)+AN(2), lambda:'E'+D(11)+AN(2), lambda:'902'+D(9),
     lambda:'501'+D(9), lambda:'601'+D(9), lambda:'2837'+D(8), lambda:'10'+D(8), lambda:'ALCLFF'+H(6), lambda:'ALCLFE'+H(6), None,
     lambda:'ADTN21'+H(6), lambda:'ADTN25'+H(6), None, lambda:'S2'+D(2)+'Z'+D(8), lambda:'E66AV'+D(10), lambda:'101-'+D(8)]
cat=json.loads(subprocess.check_output(['node','-e','''global.window={}; eval(require("fs").readFileSync("/home/claude/xploreforms/fieldkit/fieldkit-catalog.js","utf8")); const C=window.FK_CATALOG;
console.log(JSON.stringify({rules:C.SERIAL_RULES.map(r=>[r[0].source,r[1]]), skus:C.SKUS}))''']))
SK={s['id']:s for s in cat['skus']}
rules=[(re.compile(src),ids) for src,ids in cat['rules']]
def models(code):
    for rx,ids in rules:
        if rx.search(code): return ids
    return []
out=[]; seen=set()
for i,(rx,ids) in enumerate(rules):
    g=GEN[i]
    if not g: continue
    for k in range(2):
        while True:
            c=g()
            if c not in seen and models(c)==ids: break
        seen.add(c)
        out.append({'code':c,'skus':ids,'names':[SK[x]['name'] for x in ids],'group':SK[ids[0]]['group']})
# check every code is a valid Code 128 that a reader decodes back exactly
for o in out:
    buf=io.BytesIO(); barcode.get('code128',o['code'],writer=ImageWriter()).write(buf,{'module_width':0.3,'module_height':12,'quiet_zone':6,'write_text':False})
    buf.seek(0); r=zxingcpp.read_barcodes(Image.open(buf))
    assert r and r[0].text==o['code'], (o['code'], r and r[0].text)
    s=io.BytesIO(); barcode.get('code128',o['code'],writer=SVGWriter()).write(s,{'module_width':0.3,'module_height':14,'quiet_zone':4,'write_text':False,'background':'#FFFFFF','foreground':'#000000'})
    svg=s.getvalue().decode()
    svg=svg[svg.index('<svg'):]
    o['svg']=svg
mac={'code':'5C:0F:FB:'+':'.join(H(2) for _ in range(3)),'skus':[],'names':[],'group':'test'}
s=io.BytesIO(); barcode.get('code128',mac['code'],writer=SVGWriter()).write(s,{'module_width':0.3,'module_height':14,'quiet_zone':4,'write_text':False}); mac['svg']=s.getvalue().decode()[s.getvalue().decode().index('<svg'):]
json.dump({'items':out,'mac':mac},open('codes.json','w'))
print(len(out),'codes, all decode back exactly')
for o in out: print(o['code'].ljust(20), ' / '.join(o['skus']))
print('MAC test', mac['code'])
