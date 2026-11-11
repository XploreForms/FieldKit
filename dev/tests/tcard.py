import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); shots=[]
        for w in (360, 320):
            ctx = await b.new_context(viewport={'width':w,'height':520}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
            await pg.evaluate("""()=>{ const j=FieldKit.job.start(); j.sa='SA-1233559'; j.work='INS'; j.plat='Fibre (Drop Required)'; j.tech='FTX'; j.base='Install · Fibre (Drop Required) · FTX'; j.title=j.base+' · Complete'; FieldKit.job.save(j); }""")
            await pg.reload(); await pg.wait_for_timeout(1200)
            card = pg.locator('#jobArea .jobwrap')
            await pg.screenshot(path=f'/tmp/c{w}a.png', clip=dict(await card.bounding_box(), x=0, width=w) if False else None)
            bb = await card.bounding_box(); clip={'x':0,'y':max(0,bb['y']-12),'width':w,'height':bb['height']+24}
            await pg.screenshot(path=f'/tmp/c{w}a.png', clip=clip)
            ov = await pg.evaluate("""()=>{const r=document.querySelector('#jobArea .job span'), n=document.getElementById('jobNew'); const a=r.getBoundingClientRect(), c=n.getBoundingClientRect(); return {textCut: r.scrollWidth>r.clientWidth+1, textBottom:Math.round(a.bottom), btnTop:Math.round(c.top), overlap:a.bottom>c.top, btnH:Math.round(c.height), pageOverflow:document.documentElement.scrollWidth-innerWidth}}""")
            print(w, 'normal:', ov, '| button:', (await pg.locator('#jobNew').inner_text()).strip())
            await pg.locator('#jobNew').click(); await pg.wait_for_timeout(250)
            bb = await card.bounding_box(); clip={'x':0,'y':max(0,bb['y']-12),'width':w,'height':bb['height']+24}
            await pg.screenshot(path=f'/tmp/c{w}b.png', clip=clip)
            ov2 = await pg.evaluate("""()=>{const n=document.getElementById('jobNew'); return {cut:n.scrollWidth>n.clientWidth+1, h:Math.round(n.getBoundingClientRect().height)}}""")
            print(w, 'tap once:', ov2, '|', (await pg.locator('#jobNew').inner_text()).strip(), '| url', pg.url.replace(B,''))
            shots += [f'/tmp/c{w}a.png', f'/tmp/c{w}b.png']
            print('errors', errs); await ctx.close()
        await b.close()
    ims=[Image.open(s) for s in shots]; W=max(i.width for i in ims); H=sum(i.height for i in ims)+10*len(ims)
    o=Image.new('RGB',(W*2+20,max(ims[0].height+ims[1].height, ims[2].height+ims[3].height)+10),'white')
    o.paste(ims[0],(0,0)); o.paste(ims[1],(0,ims[0].height+10)); o.paste(ims[2],(W+20,0)); o.paste(ims[3],(W+20,ims[2].height+10)); o.save('/tmp/fk-shots/card.png')
asyncio.run(main())
