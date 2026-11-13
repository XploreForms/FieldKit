import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
CAM="""(()=>{const g=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);navigator.mediaDevices.getUserMedia=c=>{if(c&&c.video&&typeof c.video==='object'){const v=Object.assign({},c.video);delete v.facingMode;delete v.deviceId;v.width={ideal:1080};v.height={ideal:1440};c=Object.assign({},c,{video:v});}return g(c);};})()"""
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True, permissions=['camera'])
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED)); await ctx.add_init_script(CAM)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(500); await pg.locator('#jobStart').click(); await pg.wait_for_timeout(200)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await pg.locator('[data-nj=tech][data-v=FWN]').click()
        await pg.locator('[data-nj=tech]').first.click(); await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(500)
        await pg.goto(B+'fieldcam.html#job'); await pg.wait_for_timeout(3500)
        await pg.locator('#shutter').click(); await pg.wait_for_timeout(3000)
        await pg.evaluate("hideSnack()")
        print('first tile:', await pg.locator('#lGrid .lt').first.inner_text(), '| To label row visible:', await pg.locator('.deck .lhead').is_visible())
        await pg.screenshot(path='/tmp/fk-shots/tolabel.png')
        await pg.locator('#lGrid .lt.tolabel').click(); await pg.wait_for_timeout(600)
        print('sorter opened:', await pg.evaluate("[...document.querySelectorAll('.open')].map(e=>e.id).filter(Boolean)"))
        await pg.goto(B+'index.html#job'); await pg.wait_for_timeout(1200)
        print('SA summary pictures button:', await pg.locator('#lbPhotos a.btn').inner_text())
        await pg.goto(B+'fieldcam.html#job'); await pg.wait_for_timeout(3500)
        await pg.evaluate("document.getElementById('hud').classList.add('scan'); document.getElementById('aim').hidden=false"); await pg.wait_for_timeout(500)
        await pg.screenshot(path='/tmp/fk-shots/scanner.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
