import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True}), "techstock.order": json.dumps({"qty":{"3":2},"reason":"","notes":""})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(800); await pg.goto(B+'fieldstock.html#order'); await pg.wait_for_timeout(1500)
        L=pg.locator('#ordList')
        print('old order cleared:', await pg.locator('#ordCount').inner_text())
        rows = await L.evaluate("e=>[...e.children].map(c=>c.className.includes('ord-group')?'## '+c.textContent:c.className.includes('ord-more')?'   ['+c.textContent+']':c.querySelector('.ord-txt')?.innerText.replace(/\\n/g,' — ')).filter(Boolean)")
        print('\n'.join(rows))
        # family qty, then a specific model
        row = lambda t: L.locator('.ord-row').filter(has=pg.locator('b', has_text=re.compile('^'+re.escape(t)+'$')))
        await row('5G CPE').locator('[data-d="1"]').click(); await row('5G CPE').locator('[data-d="1"]').click()
        await L.locator('[data-ofam="fam:DROP CABLE"]').click(); await pg.wait_for_timeout(200)
        await row('Drop - 300m - Evolv Dielectric Drop PushLok Tech').locator('[data-d="1"]').click()
        await L.locator('[data-ofam="fam:ONT"]').click(); await row('Nokia XS-010X').locator('[data-d="1"]').click()
        await row('Aerial kit').locator('[data-d="1"]').click() if await row('Aerial kit').count() else None
        await pg.screenshot(path='/tmp/fk-shots/order.png', full_page=False)
        await pg.locator('#ordReason').fill('Warehouse short'); await pg.locator('#ordSend').click(); await pg.wait_for_timeout(600)
        body = await pg.evaluate("decodeURIComponent((document.querySelector('#detailSheet a[href^=\"mailto:\"]')||{}).href.split('body=')[1]||'')")
        print('--- email items:'); print(body[body.index('Items'):body.index('Thank')] if 'Items' in body else body[:400])
        print('errors', errs); await b.close()
asyncio.run(main())
