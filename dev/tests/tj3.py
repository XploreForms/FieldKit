import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1","shipHold":"","shipNotes":""}),
        "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':480}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/index.html#new-job'); await pg.wait_for_timeout(1000)
        await pg.get_by_role('button', name='Fibre').click(); await pg.wait_for_timeout(300)
        r = await pg.evaluate('''async()=>{
          const h=[...document.querySelectorAll('.lhead')].find(e=>e.getClientRects().length), m=h.nextElementSibling;
          const res=[['docH',document.documentElement.scrollHeight, m&&m.className]];
          for (const y of [40,62,70,150,3]) { scrollTo(0,y); await new Promise(r=>setTimeout(r,400)); res.push([y, scrollY, document.documentElement.classList.contains('fk-slim'), Math.round(m.getBoundingClientRect().top+scrollY)]); }
          return res;}''')
        [print(x) for x in r]
        await pg.evaluate('scrollTo(0,150)'); await pg.wait_for_timeout(500); await pg.screenshot(path='nj_slim.png')
        # job summary
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click()
        print('errors', errs); await b.close()
asyncio.run(main())
