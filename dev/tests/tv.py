import asyncio, json, base64
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=1, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page()
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500); await pg.screenshot(path='/tmp/v1.png')
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(500)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.screenshot(path='/tmp/v2.png')
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(1500)
        d = await pg.evaluate('''async()=>{ const id=Object.keys(jobs).pop(); S.photos.push({id:'p1',sessionId:id,created:Date.now()+600000,job:jobs[id]});
            const f=await makeDivider(id,'start'); const u8=new Uint8Array(await f.arrayBuffer()); let s=''; for(const c of u8) s+=String.fromCharCode(c); return btoa(s); }''')
        open('/tmp/card.jpg','wb').write(base64.b64decode(d))
        await pg.goto(B+'index.html#job'); await pg.wait_for_timeout(1200); await pg.evaluate('scrollTo(0,1e5)'); await pg.wait_for_timeout(300); await pg.screenshot(path='/tmp/v3.png')
        ims=[Image.open('/tmp/v1.png'),Image.open('/tmp/v2.png'),Image.open('/tmp/v3.png'),Image.open('/tmp/card.jpg').resize((390,390))]
        o=Image.new('RGB',(390*4+30,844),'white')
        for i,im in enumerate(ims): o.paste(im,(i*400,0))
        o.save('/tmp/fk-shots/sa_check.png'); await b.close()
asyncio.run(main())
