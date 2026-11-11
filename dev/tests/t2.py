import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(f'PAGEERR: {e}'))
        pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type=='error' and 'ERR_NAME' not in m.text else None)
        await pg.goto('http://localhost:8765/fieldkit-preview.html'); await pg.wait_for_timeout(1500)
        fr = lambda: pg.frame_locator('#fk')
        ins = fr().locator('input:visible')
        for i,v in enumerate(['Curtis Gibbons','curtis.gibbons@xplore.ca','5195551234','approver@xplore.ca']):
            await ins.nth(i).fill(v)
        await fr().get_by_role('button', name='Continue').click(); await pg.wait_for_timeout(600)
        ins = fr().locator('input:visible, select:visible, textarea:visible')
        n = await ins.count()
        for i in range(n):
            el = ins.nth(i); tag = await el.evaluate('e=>e.tagName+"|"+(e.type||"")+"|"+(e.id||e.name)')
            print('step2', tag)
        await pg.screenshot(path='s2.png', full_page=True)
        print(errs)
        await b.close()
asyncio.run(main())
