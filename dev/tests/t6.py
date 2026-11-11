import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, is_mobile=True, has_touch=True)
        pg = await ctx.new_page(); errs=[]
        pg.on('pageerror', lambda e: errs.append(f'PAGEERR: {e}'))
        pg.on('console', lambda m: errs.append(f'{m.type}: {m.text}') if m.type=='error' and 'ERR_NAME' not in m.text else None)
        await pg.goto('http://localhost:8765/fieldkit-preview.html'); await pg.wait_for_timeout(1500)
        F = pg.frame_locator('#fk')
        txt = lambda: F.locator('body').inner_text()
        ins = F.locator('input:visible')
        for i,v in enumerate(['Curtis Gibbons','curtis.gibbons@xplore.ca','5195551234','Approver@Xplore.ca']): await ins.nth(i).fill(v)
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

        await F.locator('a.fk-back:visible, a:has-text("Field Stock")').filter(has_text='Field Stock').first.click(); await pg.wait_for_timeout(1500)
        fr = [f for f in pg.frames if f != pg.main_frame][0]
        r = await fr.evaluate('''() => { Store.events.push({jobId:"t1", type:"transfer", voided:false, ts:Date.now(), toTech:"Guelph XCI Tech", fromEmail:"curtis.gibbons@xplore.ca", toEmail:"other.tech@xplore.ca", sku:"X", serial:"ABC123"});
          const m = transferMail("t1"); openTransferMail("t1"); return m.cc; }''')
        print('CC:', r)
        await pg.wait_for_timeout(600); await pg.screenshot(path='transfer.png')
        await b.close(); print(errs)
asyncio.run(main())
