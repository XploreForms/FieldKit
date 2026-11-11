import asyncio, json
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True)
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/index.html')
        await pg.evaluate("""()=>{localStorage.setItem('fieldkit.profile',JSON.stringify({name:'Curtis Gibbons',email:'c@xplore.ca',phone:'5195551234',manager:'m@xplore.ca',dealer:'Cambridge XCI Tech',sap:'123456',sf:'1234567',addr:'1 Main St',city:'Cambridge',prov:'ON',postal:'N1R1A1'}));localStorage.setItem('fieldkit.setupDone','1');localStorage.setItem('techstock.gs',JSON.stringify({connected:true}));}""")
        for f in ['index.html','fieldcam.html','fieldnotes.html','fieldstock.html']:
            await pg.goto('http://localhost:8765/'+f); await pg.wait_for_timeout(1200)
            print(f, pg.url.split('/')[-1], errs); errs.clear()
        await b.close()
asyncio.run(main())
# usage: dev/run.sh dev/check.py  -> prints each page and any page errors (empty [] = good)
