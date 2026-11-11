import asyncio
from playwright.async_api import async_playwright
PFX=__import__('sys').argv[2]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/'+__import__('sys').argv[1]); await pg.wait_for_timeout(1500)
        F = pg.frame_locator('#fk')
        ins = F.locator('input:visible')
        for i,v in enumerate(['Curtis Gibbons','curtis.gibbons@xplore.ca','5195551234','approver@xplore.ca']): await ins.nth(i).fill(v)
        await F.get_by_role('button', name='Continue').click(); await pg.wait_for_timeout(500)
        await F.locator('#w_dealer').fill('Cambridge XCI Tech')
        await F.locator('#w_sap').press_sequentially('1234567890')
        await F.locator('#w_sf').press_sequentially('SF 1700-123-99')
        print('typed  sap=%r sf=%r' % (await F.locator('#w_sap').input_value(), await F.locator('#w_sf').input_value()))
        await pg.screenshot(path=PFX+'typed.png'); await F.locator('#w_sap').fill('')
        await F.locator('#w_sap').press_sequentially('12345'); await F.locator('#w_sf').fill(''); await F.locator('#w_sf').press_sequentially('170012')
        await F.get_by_role('button', name='Continue').click(); await pg.wait_for_timeout(500)
        await F.locator('#w_sap').scroll_into_view_if_needed(); await pg.wait_for_timeout(300)
        await pg.screenshot(path=PFX+'err.png')
        print('errors shown:', await F.locator('.ferr:visible').all_inner_texts())
        await F.locator('#w_sap').press_sequentially('6'); await F.locator('#w_sf').press_sequentially('3')
        await pg.wait_for_timeout(300); await pg.screenshot(path=PFX+'ok.png')
        print('page errors', errs); await b.close()
asyncio.run(main())
