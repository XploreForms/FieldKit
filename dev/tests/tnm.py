import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':375,'height':812}, device_scale_factor=2, has_touch=True, is_mobile=True)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8766/stock-item-names.html'); await pg.wait_for_timeout(1200)
        print(await pg.locator('#progTxt').inner_text(), '| groups:', await pg.locator('.ghead h2').all_inner_texts())
        await pg.screenshot(path='/tmp/fk-shots/nm1.png')
        # rename + done
        inp = pg.locator('input.nm').first; await inp.fill('5G radio – O5 Next Gen (white)'); await pg.locator('.ok').first.click(); await pg.wait_for_timeout(300)
        print(await pg.locator('#progTxt').inner_text())
        await pg.locator('[data-alldone]').first.click(); await pg.wait_for_timeout(300); print('after mark group:', await pg.locator('#progTxt').inner_text())
        # move a category
        await pg.locator('select.cat').first.select_option('TV'); await pg.wait_for_timeout(300)
        # categories edit
        await pg.locator('#cats summary').click(); await pg.locator('#newCat').fill('Tools'); await pg.locator('#addCat').click(); await pg.wait_for_timeout(200)
        await pg.locator('.catrow input').first.fill('Wireless radios'); await pg.locator('.catrow input').first.press('Enter'); await pg.wait_for_timeout(300)
        print('cats:', await pg.evaluate("[...document.querySelectorAll('.catrow input')].map(i=>i.value)"))
        await pg.reload(); await pg.wait_for_timeout(800)
        print('after reload:', await pg.locator('#progTxt').inner_text(), await pg.evaluate("JSON.parse(localStorage.getItem('fk-stock-names-v1')).cats.slice(0,2)"))
        await pg.locator('[data-f=all]').click(); await pg.locator('#cats summary').click(); await pg.wait_for_timeout(300)
        await pg.screenshot(path='/tmp/fk-shots/nm2.png')
        print('errors', errs); await b.close()
asyncio.run(main())
