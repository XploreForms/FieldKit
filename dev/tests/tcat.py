import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1500)
        # receive: three different Nokia SKUs + a known B5 serial + a TRIA
        inp = pg.locator('#p-log input[placeholder*="serial" i]').first
        for v in ['ALCLFDD595C4','ALCLFE49FE1D','ALCLF93C0910','B5SGS252400016']:
            await inp.fill(v); await inp.press('Enter'); await pg.wait_for_timeout(250)
        pass #, (await pg.locator('#p-log').inner_text()).replace('\n',' | ')[:700])
        print('buttons:', await pg.locator('#p-log button:visible').all_inner_texts())
        await pg.locator('#p-log button', has_text='Warehouse').click()
        save = pg.locator('#p-log button', has_text='Log Received Items')
        print('save button:', await save.inner_text()); await save.click(); await pg.wait_for_timeout(800)
        await pg.locator('.tabs [role=tab]', has_text='Stock').click(); await pg.wait_for_timeout(400)
        print('stock rows:', [t.replace('\n',' | ') for t in await pg.locator('#stockList summary').all_inner_texts()])
        await pg.screenshot(path='/tmp/fk-shots/stock_rows.png')
        # pickers: one entry per name
        print('picker has Nokia x', await pg.evaluate("[...document.querySelectorAll('#skuSel option')].filter(o=>o.textContent==='Nokia XS-010X').length"), '| TRIA 1W x', await pg.evaluate("[...document.querySelectorAll('#skuSel option')].filter(o=>o.textContent==='TRIA - 1 Watt').length"))
        print('errors', errs); await b.close()
asyncio.run(main())
