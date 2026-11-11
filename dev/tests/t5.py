import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(f'PAGEERR: {e}'))
        pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type=='error' and 'ERR_NAME' not in m.text else None)
        await pg.goto('http://localhost:8766/fieldkit-preview.html'); await pg.wait_for_timeout(1500)
        F = pg.frame_locator('#fk')
        txt = lambda: F.locator('body').inner_text()
        ins = F.locator('input:visible')
        for i,v in enumerate(['Curtis Gibbons','curtis.gibbons@xplore.ca','5195551234','approver@xplore.ca']): await ins.nth(i).fill(v)
        await F.get_by_role('button', name='Continue').click(); await pg.wait_for_timeout(500)
        for k,v in dict(w_dealer='Cambridge XCI Tech',w_sap='123456',w_sf='1234567',w_street='1 Main St',w_city='Cambridge',w_postal='N1R 1A1').items():
            await F.locator('#'+k).fill(v)
        await F.locator('#w_prov').select_option('ON')
        await F.get_by_role('button', name='Continue').click(); await pg.wait_for_timeout(500)
        await pg.screenshot(path='s3.png'); print('== step3\n', (await txt())[:500])
        btns = await F.locator('button:visible').all_inner_texts(); print('buttons', btns)
        if btns and 'Continue' in btns or True:
            for name in ['Finish','Done','Skip','Continue','Open Field Kit','Start using Field Kit']:
                b2 = F.get_by_role('button', name=name)
                if await b2.count() and await b2.first.is_visible():
                    print('click', name); await b2.first.click(); await pg.wait_for_timeout(700); break
        await pg.screenshot(path='s4.png'); print('== after\n', (await txt())[:900])

        async def shot(name):
            await pg.wait_for_timeout(1200); await pg.screenshot(path=name+'.png')
            t=(await txt()).replace('\n',' | '); print('==',name, t[:260]); 
        # New job
        await F.get_by_text('Start New SA').first.click(); await shot('n1')
        print('inputs', await F.locator('input:visible,select:visible').evaluate_all('a=>a.map(e=>e.id+":"+e.type)'))
        print('buttons', await F.locator('button:visible').all_inner_texts())

        await F.locator('#njRef').fill('1234567')
        await F.get_by_role('button', name='Install').click()
        await F.get_by_role('button', name='Fixed Wireless').click()
        await F.locator('[data-nj=tech]').first.click()
        await F.get_by_role('button', name='Start SA').click(); await shot('c1')
        await F.locator('a.fk-back:visible').first.click(); await shot('lobby')
        await F.locator('a.fk-back:visible').first.click(); await shot('m2')
        await F.get_by_text('Field Notes').first.click(); await shot('fn1')
        await F.locator('a.fk-back:visible').first.click(); await shot('m3')
        await F.get_by_text('Field Stock').first.click(); await shot('fs1')
        await F.locator('a.fk-back:visible').first.click(); await shot('m4')
        await F.get_by_text('Manual Order Request').first.click(); await shot('fs2')
        await b.close(); print(errs)
asyncio.run(main())
