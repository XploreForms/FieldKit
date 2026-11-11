import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Brantford Central 3 XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Brantford","prov":"ON","postal":"N3T 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780})
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page()
        async def dlg(d): await d.accept()
        pg.on('dialog', lambda d: asyncio.ensure_future(dlg(d)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(600)
        await pg.goto(B+'fieldstock.html#testload'); await pg.wait_for_timeout(3500)
        # also a real (non-test) entry that must survive
        print('loaded:', await pg.locator('#st-ser').inner_text(), 'serialized,', await pg.locator('#st-non').inner_text(), 'counted')
        await ctx.storage_state(path='/tmp/fk-shots/with_test.json'); await b.close()
asyncio.run(main())
