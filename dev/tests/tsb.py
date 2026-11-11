import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':390,'height':844}); logs=[]
        pg.on('console', lambda m: logs.append(m.text) if m.type=='error' else None)
        pg.on('pageerror', lambda e: logs.append('PAGEERR '+str(e)))
        await pg.goto('http://localhost:8765/outer_test.html'); await pg.wait_for_timeout(2500)
        fr = [f for f in pg.frames if 'srcdoc' in f.url]
        print('frames', [f.url[:40] for f in pg.frames])
        inner = fr[0] if fr else None
        if inner: print((await inner.evaluate('document.body.innerText'))[:200])
        print('\n'.join(l for l in logs if 'ERR_NAME' not in l)[:1500])
        await b.close()
asyncio.run(main())
