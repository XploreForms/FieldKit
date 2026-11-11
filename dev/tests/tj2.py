import asyncio, sys, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1","shipHold":"","shipNotes":""}),
        "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
NOVT = len(sys.argv) > 1 and sys.argv[1] == 'novt'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED) + (";document.startViewTransition=undefined;" if NOVT else ""))
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        for page in ['fieldstock.html','fieldnotes.html']:
            await pg.goto('http://localhost:8765/'+page); await pg.wait_for_timeout(1200)
            r = await pg.evaluate('''async()=>{
              const m=document.querySelector('main')||document.body.children[3]; 
              const res=[['docH',document.documentElement.scrollHeight]];
              for (const y of [40,59,62,64,70,90,300,3]) { scrollTo(0,y); await new Promise(r=>setTimeout(r,400)); res.push([y, scrollY, document.documentElement.classList.contains('fk-slim'), Math.round(m.getBoundingClientRect().top+scrollY)]); }
              return res;}''')
            print(page, 'noVT' if NOVT else 'VT'); [print('  ', x) for x in r]
        print('errors', errs); await b.close()
asyncio.run(main())
