import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
CAM="""(()=>{const g=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);navigator.mediaDevices.getUserMedia=c=>{if(c&&c.video&&typeof c.video==='object'){const v=Object.assign({},c.video);delete v.facingMode;delete v.deviceId;c=Object.assign({},c,{video:v});}return g(c);};})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
        for (w,h) in [(360,640),(412,860)]:
            ctx = await b.new_context(viewport={'width':w,'height':h}, device_scale_factor=2, has_touch=True, is_mobile=True, permissions=['camera'])
            await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED)); await ctx.add_init_script(CAM)
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto('http://localhost:8765/fieldcam.html'); await pg.wait_for_timeout(3500)
            await pg.locator('#shutter').click(); await pg.wait_for_timeout(3000)
            job1 = await pg.evaluate("current && current.id")
            await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(1200)
            print(w,h,'tile:', (await pg.locator('.tiles li').nth(5).inner_text()).replace('\n',' | '), '| overlap:', await pg.evaluate("(()=>{const t=document.querySelector('.tnew').getBoundingClientRect(),b=[...document.querySelectorAll('.tiles b')].pop().getBoundingClientRect();return !(t.right<b.left||t.left>b.right||t.bottom<b.top||t.top>b.bottom)})()"), document_class:=await pg.evaluate("document.getElementById('menu').className"))
            await pg.screenshot(path=f'/tmp/fk-shots/camnew_{w}.png')
            w0 = await pg.evaluate("document.querySelector('.tnew').getBoundingClientRect().width")
            await pg.locator('.tnew').click(); await pg.wait_for_timeout(300)
            w1 = await pg.evaluate("document.querySelector('.tnew').getBoundingClientRect().width")
            print('  New width before/after first tap:', round(w0), round(w1), await pg.locator('.tnew').inner_text())
            await pg.locator('.tnew').click(); await pg.wait_for_timeout(3500)
            job2 = await pg.evaluate("current && current.id")
            print('  ->', pg.url, 'new job:', job1 != job2, 'photos in new job:', await pg.evaluate("curPhotos().length"), [e for e in errs if 'ViewTransition' not in e])
            await ctx.close()
        await b.close()
asyncio.run(main())
