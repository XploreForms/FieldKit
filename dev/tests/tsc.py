import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True, permissions=['camera'])
        await ctx.add_init_script("window.__det=[]; window.BarcodeDetector = class { static async getSupportedFormats(){ return ['code_128']; } async detect(){ const v=window.__det.shift(); return v?[{rawValue:v}]:[]; } };")
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2500)
        await pg.locator('#snBtn').click(); await pg.wait_for_timeout(800)
        print('scanning:', await pg.evaluate("SC.on"), '| panel hidden:', await pg.evaluate("document.getElementById('scanTop').hidden"))
        await pg.screenshot(path='/tmp/fk-shots/scan1.png')
        await pg.evaluate("scanOnce()"); await pg.wait_for_timeout(2600)
        print('fail toast:', await pg.locator('#toast').inner_text())
        await pg.evaluate("readAim = async () => '854V6W4QV0A3F3GA'; scanOnce()"); await pg.wait_for_timeout(2500)
        if await pg.locator('.fkj-opt:visible').count(): await pg.locator('.fkj-opt:visible').first.click(); await pg.wait_for_timeout(600)
        print('serials:', await pg.evaluate("(curJob().serials||[]).map(x=>x.code)"), 'bd:', await pg.evaluate("String(!!SC.bd)"), 'vw:', await pg.evaluate("document.getElementById('video').videoWidth"))
        print('added toast:', await pg.locator('#toast').inner_text())
        await pg.screenshot(path='/tmp/fk-shots/scan2.png')
        await pg.locator('#snBtn').click(); await pg.wait_for_timeout(400); print('stopped with scan button:', not await pg.evaluate("SC.on"))
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
