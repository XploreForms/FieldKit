import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        dl=[]; 
        async def dlg(d): print('DIALOG:', d.message[:70].replace('\n',' ')); await d.accept()
        pg.on('dialog', lambda d: asyncio.ensure_future(dlg(d)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(600)
        await pg.goto(B+'fieldstock.html#testload'); await pg.wait_for_timeout(3500)
        print('page errors so far:', errs)
        print('stock after testload:', await pg.locator('#st-ser').inner_text(), 'serialized')
        await pg.locator('.tabs [role=tab]', has_text='Log').click(); await pg.locator('#typeSeg button', has_text='Deploy').click(); await pg.wait_for_timeout(400)
        opts = await pg.evaluate("[...document.querySelectorAll('#dItemSel option')].map(o=>o.textContent)")
        print('deploy picker:', len(opts), 'options | first:', opts[0], '| has serialized:', 'Adtran 854-V6' in opts, '| has NID:', 'NID' in opts)
        # pick a serialized item by hand
        await pg.locator('#dItemSel').select_option(label='Adtran 854-V6'); await pg.wait_for_timeout(400)
        print('line:', (await pg.locator('#lineList').inner_text()).replace('\n',' | ')[:200])
        chips = await pg.locator('#lineList [data-lser]').all_inner_texts(); print('in-stock serial chips:', len(chips), chips[:3])
        await pg.locator('#accountIn').fill('1111111')
        # save without a serial
        await pg.locator('#saveBtn').click(); await pg.wait_for_timeout(300); print('save w/o serial ->', (await pg.locator('#formErr').inner_text()).strip(), '| btn:', await pg.locator('#saveBtn').inner_text(), await pg.locator('#saveBtn').is_visible())
        # wrong-item serial typed
        await pg.locator('#lineList [data-lin]').fill('ALCLFFDBFA43'); await pg.locator('#lineList [data-ladd]').click(); await pg.wait_for_timeout(300)
        print('typed an ONT serial for a router ->', await pg.evaluate("document.getElementById('toast').textContent"), '| line still needs serial:', await pg.locator('#lineList [data-lin]').count()==1)
        # tap a stock chip
        await pg.locator('#lineList [data-lser]').first.click(); await pg.wait_for_timeout(300)
        print('after tapping a chip:', (await pg.locator('#lineList').inner_text()).replace('\n',' | ')[:120])
        before = await pg.locator('#st-ser').inner_text() if False else None
        await pg.locator('#saveBtn').click(); await pg.wait_for_timeout(900)
        print('saved ->', await pg.evaluate("document.getElementById('toast').textContent"), '| last event:', await pg.evaluate("(({type,skuName,serial,sa})=>[type,skuName,serial,sa].join(' · '))(JSON.parse(localStorage.getItem('techstock.events')).filter(e=>!e.voided && e.type==='deploy').sort((a,b)=>b.ts-a.ts)[0])"))
        # typed serial path, plus a no-serial item still works
        await pg.locator('#dItemSel').select_option(label='Nokia XS-010X'); await pg.wait_for_timeout(300)
        await pg.locator('#lineList [data-lin]').fill('ALCLFFDBFA43'); await pg.locator('#saveBtn').click(); await pg.wait_for_timeout(900)
        print('typed serial, saved with Save only ->', await pg.evaluate("(({type,skuName,serial})=>[type,skuName,serial].join(' · '))(JSON.parse(localStorage.getItem('techstock.events')).filter(e=>!e.voided && e.type==='deploy').sort((a,b)=>b.ts-a.ts)[0])"))
        await pg.locator('#dItemSel').select_option(label='NID'); await pg.wait_for_timeout(300); await pg.locator('#saveBtn').click(); await pg.wait_for_timeout(900)
        print('NID (no serial) ->', await pg.evaluate("(({type,skuName,serial,qty})=>[type,skuName,serial||'-',qty].join(' · '))(JSON.parse(localStorage.getItem('techstock.events')).filter(e=>!e.voided && e.type==='deploy').sort((a,b)=>b.ts-a.ts)[0])"))
        # other functions keep the old picker
        await pg.locator('#typeSeg button', has_text='Receive').click(); await pg.wait_for_timeout(300)
        o2 = await pg.evaluate("[...document.querySelectorAll('#dItemSel option')].map(o=>o.textContent)"); print('receive picker:', o2[0], '| serialized item offered:', 'Adtran 854-V6' in o2)
        print('history check:', end=' ')
        await pg.locator('.tabs [role=tab]', has_text='History').click(); await pg.wait_for_timeout(400); t=await pg.locator('#p-history').inner_text(); i=t.find('VERIFIED'); print('VERIFIED' if i>=0 else t[t.find('History Check'):][:80])
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(500); await pg.goto(B+'fieldstock.html#testremove'); await pg.wait_for_timeout(2500)
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
