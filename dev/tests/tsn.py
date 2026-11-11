import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.BarcodeDetector = class { static async getSupportedFormats(){ return ['code_128']; } async detect(){ return []; } };")
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1300)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300); N=pg.locator('#newjob')
        await pg.locator('#njRef').fill('1234567'); await N.locator('button').filter(has_text=X('Install')).click(); await N.locator('button').filter(has_text=X('Fibre')).click(); await N.locator('button').filter(has_text=X('Existing Drop')).click(); await N.locator('[data-nj=tech]').first.click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(800)
        await pg.goto(B+'fieldcam.html#job'); await pg.wait_for_timeout(2200)   # 1.20.27: Start SA opens the SA summary
        print('tiles:', await pg.locator('#lGrid button').all_inner_texts())
        tile = lambda t: pg.locator('#lGrid button').filter(has_text=X(t))
        st = lambda: pg.evaluate("[S.sel.join(' + '), SC.on]")
        await tile('ONT SN').click(); await pg.wait_for_timeout(500); print('tap ONT SN        ->', await st())
        await tile('XWR SN').click(); await pg.wait_for_timeout(300); print('tap XWR SN        ->', await st())
        await tile('Router Placement').click(); await pg.wait_for_timeout(300); print('tap Router Placem.->', await st())
        await tile('ONT Placement').click(); await pg.wait_for_timeout(300); print('tap ONT Placement ->', await st())
        await tile('XTV SN').click(); await pg.wait_for_timeout(500); print('tap XTV SN        ->', await st())
        await pg.evaluate("window.__sel=[]; capture = async () => { window.__sel.push(S.sel.join(' + ')); return null; }; readAim = async () => 'E66AV5974844233'; scanOnce()"); await pg.wait_for_timeout(1300)
        print('scan an XTV box   -> photo label', await pg.evaluate("window.__sel"))
        await tile('XTV SN').click(); await pg.wait_for_timeout(300); print('tap XTV SN again  ->', await st())
        await pg.screenshot(path='/tmp/fk-shots/sn_tiles.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
