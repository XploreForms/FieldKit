import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':900}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(600); await pg.goto('http://localhost:8765/fieldstock.html#order'); await pg.wait_for_timeout(1500)
        await pg.locator('#ordList').scroll_into_view_if_needed(); await pg.evaluate("window.scrollBy(0,-90)"); await pg.wait_for_timeout(300)
        await pg.screenshot(path='/tmp/fk-shots/ordlist.png'); await b.close()
asyncio.run(main())
