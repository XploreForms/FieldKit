# usage: python3 shotset.py <html> <out.png>  — setup step 1, phone size
import asyncio, sys
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/'+sys.argv[1]); await pg.wait_for_timeout(1500)
        await pg.screenshot(path=sys.argv[2]); print('errors', errs); await b.close()
asyncio.run(main())
