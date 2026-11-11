import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{ const j=FieldKit.job.start(); j.sa='SA-1233559'; j.base='Install · Fibre (Drop Required) · FTX'; j.title=j.base+' · Complete'; FieldKit.job.save(j); }")
        await pg.reload(); await pg.wait_for_timeout(1000)
        await pg.locator('#jobNew').click(); await pg.wait_for_timeout(300)
        print('after 1 tap, still on menu:', await pg.evaluate("!document.getElementById('menu').hidden"))
        await pg.wait_for_timeout(4300); print('resets after 4s:', (await pg.locator('#jobNew').inner_text()).strip())
        await pg.locator('#jobNew').click(); await pg.locator('#jobNew').click(); await pg.wait_for_timeout(500)
        print('after 2 taps: New SA screen:', await pg.evaluate("!document.getElementById('newjob').hidden"), '| old SA kept in history:', await pg.evaluate("FieldKit.job.list().length"))
        print('errors', errs); await b.close()
asyncio.run(main())
