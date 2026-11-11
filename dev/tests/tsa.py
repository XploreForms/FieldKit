import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(800)
        await pg.get_by_text('Start New Job').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start Job').click(); await pg.wait_for_timeout(1500)
        await pg.screenshot(path='/tmp/a.png', clip={'x':0,'y':0,'width':360,'height':60})
        print('cam back:', await pg.locator('a.fk-back:visible').first.inner_text(), '| pill:', await pg.locator('#jobBtn').inner_text())
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1200)
        await pg.screenshot(path='/tmp/b.png', clip={'x':0,'y':0,'width':360,'height':110})
        print('notes back:', await pg.locator('a.fk-back:visible').first.inner_text())
        await pg.locator('a.fk-back:visible').first.click(); await pg.wait_for_timeout(1000); print('->', pg.url.replace(B,''))
        a,c=Image.open('/tmp/a.png'),Image.open('/tmp/b.png'); o=Image.new('RGB',(a.width,a.height+c.height+10),'white'); o.paste(a,(0,0)); o.paste(c,(0,a.height+10)); o.save('/tmp/fk-shots/sa_back.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
