import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, is_mobile=True, has_touch=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/fieldnotes.html'); await pg.wait_for_timeout(1500)
        J=pg.locator('[data-field-id=job]')
        for t in ['Install','Fibre','Drop Required']: await J.locator('button').filter(has_text=re.compile('^'+re.escape(t)+'$')).first.click(); await pg.wait_for_timeout(200)
        R=pg.locator('[data-field-id=route]'); await R.scroll_into_view_if_needed()
        print([ (await x.inner_text()).strip()[:20] for x in await R.locator('button').all()])
        await R.locator('button', has_text='MPT Vault').click(); await pg.wait_for_timeout(300)
        print('after MPT:', [(await x.get_attribute('aria-label')) or (await x.inner_text()).strip()[:24] for x in await R.locator('button').all()])
        await R.locator('button[aria-label*="Buried" i], button:has-text("Buried")').first.click(); await pg.wait_for_timeout(300)
        print('after Buried:', [(await x.get_attribute('aria-label')) or (await x.inner_text()).strip()[:24] for x in await R.locator('button').all()])
        print('inputs:', await R.locator('input[type=checkbox]').count(), '| text:', (await R.inner_text()).replace('\n',' | ')[:200])
        await b.close()
asyncio.run(main())
