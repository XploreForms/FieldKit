import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':800}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        if not await pg.get_by_text('Start New SA').count(): await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2000)
        await pg.locator('#jobBtn').click(); await pg.wait_for_timeout(800)
        slots = pg.locator('#fkSlots')
        print('cam slots:', await slots.locator('.fkj-sh b').all_inner_texts())
        await slots.locator('[data-slot-in="router"]').fill('RTR11223344'); await slots.locator('[data-slot-add="router"]').click(); await pg.wait_for_timeout(1000)
        if await pg.locator('.fkj-opt:visible').count(): await pg.locator('.fkj-opt:visible').first.click(); await pg.wait_for_timeout(800)
        print('router added:', 'RTR11223344' in await slots.inner_text())
        await slots.locator('[data-slot-in="radio"]').scroll_into_view_if_needed(); await pg.screenshot(path='/tmp/fk-shots/cam_slots.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
