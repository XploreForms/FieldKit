import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1",
        "techstock.gs": json.dumps({"connected":True,"email":"curtis.gibbons@xplore.ca","sheetId":"abc","token":"","exp":0,"rev":3,"synced":1})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(700)
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1500)
        pill = pg.locator('#mode'); bb = await pill.bounding_box()
        print('pill:', (await pill.inner_text()).strip(), '| tap size', round(bb['width']), 'x', round(bb['height']), '| is button:', await pill.evaluate('e=>e.tagName'))
        await pg.screenshot(path='/tmp/fk-shots/pill.png', clip={'x':0,'y':0,'width':360,'height':110})
        await pill.click(); await pg.wait_for_timeout(1500)
        print('went to:', pg.url.replace(B,''), '| settings open:', await pg.evaluate("!document.getElementById('settings').hidden"),
              '| Google card visible:', await pg.locator('#backup').is_visible(), '| Sync Now there:', await pg.locator('[data-gs=sync]').count()>0)
        vis = await pg.evaluate("(()=>{const r=document.getElementById('backup').getBoundingClientRect(); return [Math.round(r.top), innerHeight]})()"); print('Google card top at', vis[0], 'of', vis[1], 'px screen')
        await pg.screenshot(path='/tmp/fk-shots/pill_settings.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
