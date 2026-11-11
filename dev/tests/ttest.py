import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Brantford Central 3 XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Brantford","prov":"ON","postal":"N3T 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        msgs=[]
        async def dlg(d):
            msgs.append(d.message.replace('\n',' / ')); await d.accept()
        pg.on('dialog', lambda d: asyncio.ensure_future(dlg(d)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(700)
        await pg.goto(B+'fieldstock.html#testload'); await pg.wait_for_timeout(4000)
        print('\n'.join(msgs)); msgs.clear()
        print('url:', pg.url.replace(B,''), '| totals:', await pg.locator('#st-ser').inner_text(), 'serialized,', await pg.locator('#st-non').inner_text(), 'counted')
        print('rows:', len(await pg.locator('#stockList summary').all_inner_texts()))
        await pg.locator('.tabs [role=tab]', has_text='History').click(); await pg.wait_for_timeout(500)
        t=await pg.locator('#p-history').inner_text(); i=t.find('History Check'); print('check text:', t[i:i+120].replace('\n',' | ')); print('history check:', [l for l in t.split('\n') if 'erif' in l or 'heck' in l][:3], '| first entry:', t.split('\n')[6:10])
        await pg.locator('.tabs [role=tab]', has_text='Stock').click(); await pg.wait_for_timeout(300)
        print('check:', (await pg.locator('#checkPill, .check-pill, [id*=heck]').first.inner_text()) if await pg.locator('#checkPill, .check-pill, [id*=heck]').count() else '?')
        await pg.screenshot(path='/tmp/fk-shots/testload.png')
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(500); await pg.goto(B+'fieldstock.html#testload'); await pg.wait_for_timeout(2500); print('again:', msgs); msgs.clear()
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(500); await pg.goto(B+'fieldstock.html#testremove'); await pg.wait_for_timeout(2500); print('remove:', msgs); msgs.clear()
        print('after remove totals:', await pg.locator('#st-ser').inner_text(), await pg.locator('#st-non').inner_text())
        print('errors', errs); await b.close()
asyncio.run(main())
