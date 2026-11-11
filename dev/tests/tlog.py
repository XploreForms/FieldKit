import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        sel = lambda: pg.evaluate("document.querySelector('.tabs [aria-selected=true]').textContent.trim()")
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1300)
        print('tabs:', await pg.locator('.tabs [role=tab]').all_inner_texts(), '| opens on:', await sel())
        for t in ['History','Stock','Count']:
            await pg.locator('.tabs [role=tab]', has_text=t).click(); await pg.wait_for_timeout(300)
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(900)
            await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1200)
            print(f'left on {t:8} -> reopens on:', await sel())
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(700); await pg.goto(B+'fieldstock.html#order'); await pg.wait_for_timeout(1200); print('#order opens:', await pg.evaluate("document.getElementById('p-order').hidden ? 'not order' : 'order'"))
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1200); await pg.screenshot(path='/tmp/fk-shots/log.png')
        print('errors', errs); await b.close()
asyncio.run(main())
