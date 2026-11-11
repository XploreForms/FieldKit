import asyncio, zxingcpp
from PIL import Image
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':375,'height':812}, device_scale_factor=2)
        await pg.goto('http://localhost:8766/test-serials.html'); await pg.wait_for_timeout(800)
        await pg.screenshot(path='/tmp/fk-shots/ts1.png')
        print('overflow:', await pg.evaluate("document.documentElement.scrollWidth - innerWidth"))
        codes = pg.locator('.code'); n = await codes.count(); bad=[]
        for i in range(n):
            await codes.nth(i).screenshot(path='/tmp/c.png')
            r = zxingcpp.read_barcodes(Image.open('/tmp/c.png'))
            want = await codes.nth(i).evaluate("e=>e.closest('.card').querySelector('[data-copy]').getAttribute('data-copy')")
            if not r or r[0].text != want: bad.append(want)
        print(n, 'barcodes on screen, unreadable:', bad)
        await b.close()
asyncio.run(main())
