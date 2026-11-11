import asyncio, sys
from playwright.async_api import async_playwright
SB = sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        pg = await b.new_page(viewport={'width':390,'height':844}); logs=[]
        pg.on('console', lambda m: logs.append(m.text) if m.type=='error' else None)
        pg.on('pageerror', lambda e: logs.append('PAGEERR '+str(e)))
        open('/tmp/fk-shots/outer_test.html','w').write(f'<!doctype html><style>html,body,iframe{{margin:0;height:100%;width:100%;border:0;display:block}}</style><iframe id="o" sandbox="{SB}" src="fieldkit-preview.html"></iframe>')
        await pg.goto('http://localhost:8765/outer_test.html'); await pg.wait_for_timeout(2000)
        F = pg.frame_locator('#o').frame_locator('#fk')
        ins = F.locator('input:visible')
        for i,v in enumerate(['Curtis Gibbons','curtis.gibbons@xplore.ca','5195551234','approver@xplore.ca']): await ins.nth(i).fill(v)
        await F.get_by_role('button', name='Continue').click(); await pg.wait_for_timeout(500)
        for k,v in dict(w_dealer='Cambridge XCI Tech',w_sap='123456',w_sf='1700123',w_street='1 Main St',w_city='Cambridge',w_postal='N1R 1A1').items(): await F.locator('#'+k).fill(v)
        await F.locator('#w_prov').select_option('ON')
        await F.get_by_role('button', name='Continue').click(); await pg.wait_for_timeout(500)
        await F.get_by_role('button', name='Finish').click(); await pg.wait_for_timeout(1500)
        await F.get_by_text('Start New Job').first.click(); await pg.wait_for_timeout(1000)
        print(SB, '->', (await F.locator('body').inner_text())[:80].replace('\n',' | '))
        print('\n'.join(l for l in logs if 'ERR_NAME' not in l)[:800])
        await b.close()
asyncio.run(main())
