import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
UA={'android':'Mozilla/5.0 (Linux; Android 14; SM-S921U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/130.0.0.0 Mobile Safari/537.36','iphone':'Mozilla/5.0 (iPhone; CPU iPhone OS 17_5 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Mobile/15E148 Safari/604.1'}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for name,ua in UA.items():
            ctx = await b.new_context(viewport={'width':360,'height':780}, user_agent=ua)
            await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
            pg = await ctx.new_page(); await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
            for nm in ['Compass','Inventory','RMA Request']:
                a = pg.locator('#links a', has_text=nm).first
                print(f'{name:8} {nm:12} target={await a.get_attribute("target")!s:7} href={(await a.get_attribute("href"))[:150]}')
            await ctx.close()
        await b.close()
asyncio.run(main())
