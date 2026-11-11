import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':375,'height':812})
        await pg.goto('http://localhost:8766/stock-item-names.html'); await pg.wait_for_timeout(800)
        await pg.locator('#cats summary').click(); await pg.wait_for_timeout(300)
        print(await pg.evaluate("""()=>{const W=document.documentElement.clientWidth; return [document.documentElement.scrollWidth, W, [...document.querySelectorAll('*')].filter(e=>e.getBoundingClientRect().right>W+1).slice(0,8).map(e=>e.tagName+'.'+e.className+' '+Math.round(e.getBoundingClientRect().right))]}"""))
        await b.close()
asyncio.run(main())
