import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.214: Field Stock item pick lists open Field Kit's own sheet (search, two-line rows, Serial/Qty); picking sets the select
async def tapSel(pg):
    bb = await pg.locator('#dItemSel').bounding_box(); await pg.touchscreen.tap(bb['x']+bb['width']/2, bb['y']+bb['height']/2)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1500)
        await pg.locator('[data-type=receive]').first.tap(); await pg.wait_for_timeout(400)
        await pg.evaluate("document.getElementById('dItemSel').addEventListener('change',e=>window.__picked=e.target.value,true)")
        bb = await pg.locator('#dItemSel').bounding_box(); x=bb['x']+bb['width']/2; y=bb['y']+bb['height']/2
        cdp = await ctx.new_cdp_session(pg)
        await cdp.send('Input.dispatchTouchEvent', {'type':'touchStart','touchPoints':[{'x':x,'y':y}]})
        for i in range(1,8): await cdp.send('Input.dispatchTouchEvent', {'type':'touchMove','touchPoints':[{'x':x,'y':y-i*25}]})
        await cdp.send('Input.dispatchTouchEvent', {'type':'touchEnd','touchPoints':[]}); await pg.wait_for_timeout(500)
        print('swipe on the field opens it (should be 0):', await pg.locator('.isheet').count())
        await tapSel(pg); await pg.wait_for_timeout(400)
        print('sheet:', await pg.locator('.isheet').count(), '| cats:', await pg.locator('.isheet-cat').all_inner_texts())
        print('rows sample:', [t.replace('\n',' / ') for t in (await pg.locator('.isheet-row').all_inner_texts())[12:16]])
        await pg.screenshot(path='/tmp/isheet.png')
        await pg.locator('.isheet-q').fill('green'); await pg.wait_for_timeout(200)
        print('search green:', [t.replace('\n',' / ') for t in await pg.locator('.isheet-row').all_inner_texts()])
        await pg.locator('.isheet-row').first.tap(); await pg.wait_for_timeout(400)
        print('picked:', await pg.evaluate("(window.__picked||'')"), '| sheet gone:', await pg.locator('.isheet').count()==0)
        await tapSel(pg); await pg.wait_for_timeout(300)
        print('lines after pick:', await pg.evaluate("document.querySelectorAll('#lines .line, [data-lsel], .dline').length"))
        await pg.go_back(); await pg.wait_for_timeout(400)
        print('back closes:', await pg.locator('.isheet').count()==0, '| still on:', pg.url.split('/')[-1])
        await pg.evaluate("FieldKit.setPrefs({theme:'black'})"); await pg.reload(); await pg.wait_for_timeout(1200); await pg.locator('[data-type=receive]').first.tap(); await pg.wait_for_timeout(300)
        await tapSel(pg); await pg.wait_for_timeout(300); await pg.locator('.isheet-q').fill('drop'); await pg.wait_for_timeout(200)
        await pg.screenshot(path='/tmp/isheet-black.png')
        print('errors', errs); await b.close()
asyncio.run(main())
