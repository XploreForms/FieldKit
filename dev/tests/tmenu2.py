import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':760}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
            if await pg.get_by_text('Start New SA').count(): break
        print('tools:', [t.split('\n')[0] for t in await pg.locator('#links li').all_inner_texts()])
        print('without an SA:', await pg.locator('#tools b').all_inner_texts())
        await pg.locator('#links a', has_text='Field Stock').click(); await pg.wait_for_timeout(1300); print('opened', pg.url.replace(B,''))
        # unsaved item in Field Stock -> in progress on the menu
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
        await pg.evaluate("FieldKit.setSession('stock', {title:'1 item not saved'})"); await pg.reload(); await pg.wait_for_timeout(1200)
        print('stock row:', (await pg.locator('#links li').first.inner_text()).replace('\n',' | '))
        await pg.screenshot(path='/tmp/fk-shots/menu3.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
