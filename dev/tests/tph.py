import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def start(pg, work, fam, sub=None):
    for _ in range(2):
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1300)
        await pg.evaluate("FieldKit.job.setActive(null)"); await pg.reload(); await pg.wait_for_timeout(1000)
        if await pg.get_by_text('Start New SA').count(): break
    await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
    await pg.locator('#njRef').fill('1234567'); await pg.locator('#newjob button', has_text=work).first.click(); await pg.locator('#newjob button').filter(has_text=__import__('re').compile('^'+fam+'$')).first.click()
    if sub: await pg.locator('#newjob button').filter(has_text=__import__('re').compile('^'+sub+'$')).first.click()
    await pg.wait_for_timeout(200)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for work,fam,sub in [('Install','Fibre','Existing Drop'),('Conversion','Fixed Wireless',None),('Install','Satellite',None),('Install','Value Added Services','XWR')]:
            await start(pg, work, fam, sub)
            if fam=='Value Added Services': print('New SA VAS order:', await pg.evaluate("[...document.querySelectorAll('#newjob button')].map(b=>b.textContent.trim()).filter(t=>/^X(W|T)/.test(t))"))
            if fam=='Value Added Services': await pg.screenshot(path='/tmp/vas.png')
            await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2200)
            labels = await pg.evaluate("[...document.querySelectorAll('#lGrid button')].map(b=>b.textContent.trim()).filter(Boolean)")
            prog = await pg.locator('#jobProg').inner_text()
            print(f'{work} {fam} {sub or ""} [{prog}]:', labels)
            if fam=='Fixed Wireless': await pg.screenshot(path='/tmp/fw.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
    a=Image.open('/tmp/fw.png'); c=Image.open('/tmp/vas.png'); o=Image.new('RGB',(a.width*2+20,a.height),'white'); o.paste(a,(0,0)); o.paste(c,(a.width+20,0)); o.resize((o.width//2,o.height//2)).save('/tmp/fk-shots/photos.png')
asyncio.run(main())
