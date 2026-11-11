import asyncio, json
from playwright.async_api import async_playwright
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, storage_state='/tmp/fk-shots/with_test.json')
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        before = await pg.evaluate("1") 
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1200)
        seen = await pg.evaluate("document.getElementById('toast').textContent")
        print('toast:', seen)
        print('stock now:', await pg.locator('#st-ser').inner_text(), 'serialized,', await pg.locator('#st-non').inner_text(), 'counted')
        ev = await pg.evaluate("JSON.parse(localStorage.getItem('techstock.events')).filter(e=>e.note==='Test inventory load (remove before rollout)')")
        print('test entries left live:', sum(1 for e in ev if not e.get('deleted')), 'of', len(ev), '| sample deleted:', ev[0].get('deleted'), '|', ev[0].get('voidReason'))
        await pg.locator('.tabs [role=tab]', has_text='History').click(); await pg.wait_for_timeout(500)
        t = await pg.locator('#p-history').inner_text(); i=t.find('History Check'); print('check:', t[i:i+110].replace('\n',' | '))
        # nothing happens twice
        await pg.reload(); await pg.wait_for_timeout(1200); print('second open toast:', repr(await pg.evaluate("document.getElementById('toast').textContent")))
        await pg.goto(B+'fieldstock.html#testload'); await pg.wait_for_timeout(1500); print('#testload now does nothing; stock:', await pg.locator('#st-ser').inner_text(), '| file served:', (await pg.request.get(B+'testdata-inventory.js')).status)
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
