import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for tz in ['America/Toronto','America/Vancouver','UTC','America/Halifax']:
            ctx = await b.new_context(timezone_id=tz); await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
            pg = await ctx.new_page(); await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(1200)
            print(f'{tz:18}', await pg.locator('#foot').inner_text()); await ctx.close()
        await b.close()
asyncio.run(main())
