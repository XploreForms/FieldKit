import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True,"email":"c@xplore.ca","sheetId":"x","rev":3,"synced":1})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
        await pg.locator('#links a', has_text='Manual Order Request').click(); await pg.wait_for_timeout(1500)
        vis = lambda sel: pg.evaluate(f"(()=>{{const e=document.querySelector('{sel}'); return !!e && e.getClientRects().length>0}})()")
        print('url:', pg.url.replace(B,''))
        print('title:', await pg.locator('.top h1').inner_text(), '| name line:', await pg.locator('#who').inner_text(), '| back link:', (await pg.locator('a.fk-back:visible').first.inner_text()).strip())
        print('tab bar visible:', await vis('.tabs'), '| status pill:', await vis('#mode'), '| sync banner:', await vis('#gsBanner'), '| duplicate heading:', await vis('#p-order h2'), '| form visible:', await vis('#ordList'))
        await pg.screenshot(path='/tmp/fk-shots/order_alone.png')
        print('bottom of page reachable (send button visible after scroll):', end=' ')
        await pg.locator('#ordSend').scroll_into_view_if_needed(); print(await pg.locator('#ordSend').is_visible())
        # Field Stock itself is unchanged
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(700); await pg.locator('#links a', has_text='Field Stock').click(); await pg.wait_for_timeout(1300)
        print('Field Stock: title', await pg.locator('.top h1').inner_text(), '| tab bar', await vis('.tabs'), '| pill', await vis('#mode'), '| tab', await pg.evaluate("document.querySelector('.tabs [aria-selected=true]').textContent.trim()"))
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
