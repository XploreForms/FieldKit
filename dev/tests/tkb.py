import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def check(pg, sel, label):
    el = pg.locator(sel); await el.click(); await el.press_sequentially('123456', delay=30)
    six = await pg.evaluate(f"document.activeElement===document.querySelector('{sel}')")
    await el.press_sequentially('7', delay=30); await pg.wait_for_timeout(100)
    seven = await pg.evaluate(f"document.activeElement===document.querySelector('{sel}')")
    print(f'{label:24} value={await el.input_value()!r:14} focused after 6: {six}  after 7: {seven}')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await check(pg, '#njRef', 'New SA')
        await pg.goto(B+'fieldcam.html#new'); await pg.wait_for_timeout(1500)
        if await pg.locator('#inRef').is_visible(): await check(pg, '#inRef', 'Field Cam start')
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1200)
        await pg.get_by_role('button', name='Deploy').first.click(); await pg.wait_for_timeout(400)
        await check(pg, '#accountIn', 'Field Stock deploy')
        print('errors', errs); await b.close()
asyncio.run(main())
