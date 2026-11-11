import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':375,'height':812}, device_scale_factor=2)
        await pg.goto('http://localhost:8766/stock-item-names.html'); await pg.wait_for_timeout(800)
        await pg.locator('#cats summary').click(); await pg.wait_for_timeout(300)
        await pg.locator('#newCat').scroll_into_view_if_needed()
        print(await pg.evaluate("[JSON.stringify(document.getElementById('newCat').getBoundingClientRect()), JSON.stringify(document.getElementById('addCat').getBoundingClientRect())]"))
        await pg.screenshot(path='/tmp/fk-shots/nm_cats.png'); await b.close()
asyncio.run(main())
