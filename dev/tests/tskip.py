import asyncio
from playwright.async_api import async_playwright
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); pg = await b.new_page(viewport={'width':360,'height':780}, device_scale_factor=2); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        ins = pg.locator('#stepForm input:visible')
        for i,v in enumerate(['Curtis Gibbons','curtis.gibbons@xplore.ca','5195551234','approver@xplore.ca']): await ins.nth(i).fill(v)
        await pg.locator('#stepNext').click(); await pg.wait_for_timeout(400)
        for k,v in dict(w_dealer='Cambridge XCI Tech',w_sap='123456',w_sf='1234567',w_street='1 Main St',w_city='Cambridge',w_postal='N1R 1A1').items(): await pg.locator('#'+k).fill(v)
        await pg.locator('#w_prov').select_option('ON'); await pg.locator('#stepNext').click(); await pg.wait_for_timeout(500)
        print('step 3:', (await pg.locator('#setup').inner_text()).replace('\n',' | ')[-260:])
        await pg.screenshot(path='/tmp/fk-shots/skip.png')
        await pg.locator('#gsSkip').click(); await pg.wait_for_timeout(800)
        print('after skip view:', await pg.evaluate("['menu','setup'].filter(id=>!document.getElementById(id).hidden)"), '| banner:', await pg.locator('#gsWarn:visible').count())
        await pg.reload(); await pg.wait_for_timeout(1200); print('after reload:', await pg.evaluate("['menu','setup'].filter(id=>!document.getElementById(id).hidden)"))
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1300); print('Field Stock opens:', pg.url.replace(B,''))
        print('errors', errs); await b.close()
asyncio.run(main())
