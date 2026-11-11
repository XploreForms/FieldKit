import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':1250}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/'+sys.argv[1]); await pg.wait_for_timeout(1500)
        F = pg.frame_locator('#fk'); ins = F.locator('input:visible')
        for i,v in enumerate(['Curtis Gibbons','curtis.gibbons@xplore.ca','5195551234','approver@xplore.ca']): await ins.nth(i).fill(v)
        await F.get_by_role('button', name='Continue').click(); await pg.wait_for_timeout(500)
        await F.locator('#w_shipHold').check(); print('hints:', await F.locator('.field:has(#w_shipNotes) .hint').count()); await pg.wait_for_timeout(300)
        await pg.screenshot(path=sys.argv[2]); print(sys.argv[2], 'errors', errs); await b.close()
asyncio.run(main())
