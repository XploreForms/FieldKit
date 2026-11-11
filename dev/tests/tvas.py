import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page()
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1300)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300); N=pg.locator('#newjob')
        await pg.locator('#njRef').fill('1234567'); await N.locator('button').filter(has_text=X('Install')).click(); await N.locator('button').filter(has_text=X('VAS Only')).click()
        print('labels:', await N.locator('.lbl').all_inner_texts())
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(300); print('error:', await pg.locator('#njErr').inner_text())
        await b.close()
asyncio.run(main())
