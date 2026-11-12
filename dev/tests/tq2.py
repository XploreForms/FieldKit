import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
CAM="""(()=>{const g=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);navigator.mediaDevices.getUserMedia=c=>{if(c&&c.video&&typeof c.video==='object'){const v=Object.assign({},c.video);delete v.facingMode;delete v.deviceId;c=Object.assign({},c,{video:v});}return g(c);};})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True, permissions=['camera'], accept_downloads=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED)); await ctx.add_init_script(CAM)
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/fieldcam.html'); await pg.wait_for_timeout(3500)
        for i in range(2):
            await pg.locator('#shutter').click(); await pg.wait_for_timeout(2500)
            print('snack shown after photo', i+1, ':', await pg.evaluate("document.getElementById('snack').classList.contains('show')"), '| qflag:', await pg.evaluate("S.photos[S.photos.length-1].qflag||null"))
        await pg.locator('#galBtn').click(); await pg.wait_for_timeout(700)
        print('gallery prev block hidden:', await pg.evaluate("document.getElementById('prevBlock').hidden"))
        print('divider cards queued:', await pg.evaluate("divCache.size"))
        await pg.evaluate("closeSheets()"); await pg.wait_for_timeout(300)
        await pg.locator('#dlBtn').click(); await pg.wait_for_timeout(3000)
        print('dbg', await pg.evaluate("[S.photos.map(p=>p.downloaded), !!current, curJob() && curJob().quick, [...document.querySelectorAll('.sheet.open,.sorter.open')].map(e=>e.id)]"))
        print('done sheet:', await pg.evaluate("document.getElementById('doneSheet').classList.contains('open')"), '|', (await pg.locator('#doneSheet').inner_text()).replace('\n',' | '))
        await pg.locator('#doneNext').click(); await pg.wait_for_timeout(1500)
        print('after Finish:', pg.url, '| cam tile:', (await pg.locator('.tiles li').nth(5).inner_text()).replace('\n',' | '))
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
