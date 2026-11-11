import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
        ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True, permissions=['camera'])
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        await ctx.add_init_script("window.BarcodeDetector = class { static async getSupportedFormats(){ return ['code_128','code_39','qr_code','data_matrix','ean_13']; } constructor(){} async detect(){ return []; } };")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(1500)
        await pg.locator('a.fk-back:visible').first.click(); await pg.wait_for_timeout(1200)   # back to the SA home
        print('at', pg.url.replace(B,''))
        # 1) slot Scan: one serial, then back
        await pg.locator('#lbGear [data-scanret=one]').first.click(); await pg.wait_for_timeout(2500)
        print('cam', pg.url.replace(B,''), await pg.evaluate("[fkScanBack, SC.on]"))
        await pg.evaluate("()=>{ const j=curJob(); j.serials=[...(j.serials||[]),{code:'RTR55554444',item:''}]; jobChanged(); fkIdentify('RTR55554444'); }")
        await pg.wait_for_timeout(800)
        if await pg.locator('.fkj-opt:visible').count(): await pg.locator('.fkj-opt:visible').first.click()
        await pg.wait_for_timeout(2500)
        print('after scan ->', pg.url.replace(B,''), '| router on SA:', 'RTR55554444' in await pg.locator('#lbGear').inner_text())
        # 2) Scan More: stays for more, back on Done
        await pg.locator('#lbGear [data-scanret=many]').first.click(); await pg.wait_for_timeout(2500)
        print('cam', pg.url.replace(B,''), await pg.evaluate("fkScanBack"))
        await pg.evaluate("()=>{ const j=curJob(); j.serials=[...(j.serials||[]),{code:'XWH77776666',item:''}]; jobChanged(); fkIdentify('XWH77776666'); }")
        await pg.wait_for_timeout(800)
        if await pg.locator('.fkj-opt:visible').count(): await pg.locator('.fkj-opt:visible').first.click()
        await pg.wait_for_timeout(2000); print('still in cam after a Scan More scan:', pg.url.replace(B,''))
        await pg.evaluate("stopScan()"); await pg.wait_for_timeout(1500); print('Done ->', pg.url.replace(B,''))
        # 3) Field Cam opened normally from the SA home: no scanner, stays
        await pg.locator('a[href="fieldcam.html#job"]:not([data-scanret])').first.click(); await pg.wait_for_timeout(2000)
        print('normal open:', pg.url.replace(B,''), await pg.evaluate("[fkScanBack, SC.on]"))
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
