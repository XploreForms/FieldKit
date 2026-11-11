import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page()
        errs=[]
        pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type in ('error','warning') else None)
        pg.on('pageerror', lambda e: errs.append(f'PAGEERR: {e}'))
        await pg.goto('http://localhost:8765/fieldkit-preview.html')
        await pg.wait_for_timeout(2500)
        await pg.screenshot(path='s1.png')
        fr = pg.frame_locator('#fk')
        print(await fr.locator('body').inner_text())
        print('\n'.join(errs[:20]))
        await b.close()
asyncio.run(main())
