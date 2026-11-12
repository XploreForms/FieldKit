import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
CAM="""(()=>{const g=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);navigator.mediaDevices.getUserMedia=c=>{if(c&&c.video&&typeof c.video==='object'){const v=Object.assign({},c.video);delete v.facingMode;delete v.deviceId;c=Object.assign({},c,{video:v});}return g(c);};})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True, permissions=['camera'])
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED)); await ctx.add_init_script(CAM); await ctx.add_init_script("Element.prototype.requestFullscreen=async function(){};")
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto('http://localhost:8765/fieldcam.html'); await pg.wait_for_timeout(4000)
        geo = "(()=>{const v=document.getElementById('vf').getBoundingClientRect(),f=document.getElementById('frame').getBoundingClientRect();return {fs:document.documentElement.classList.contains('fc-fs'),vf:[Math.round(v.width),Math.round(v.height)],pic:[Math.round(f.width),Math.round(f.height)],top:getComputedStyle(document.querySelector('.top')).display,photos:S.photos.length}})()"
        print('normal   ', await pg.evaluate(geo))
        await pg.locator('#fsBtn').click(); await pg.wait_for_timeout(800)
        print('fs portr.', await pg.evaluate(geo)); await pg.screenshot(path='/tmp/fk-shots/fs_p.png')
        await pg.set_viewport_size({'width':780,'height':360}); await pg.evaluate("S.rollQ = (screen.orientation && screen.orientation.angle) || 90; measureVf()"); await pg.wait_for_timeout(900)
        print('fs land. ', await pg.evaluate(geo)); await pg.screenshot(path='/tmp/fk-shots/fs_l.png')
        await pg.locator('#fsShut').click(); await pg.wait_for_timeout(3500)
        await pg.set_viewport_size({'width':360,'height':780}); await pg.evaluate("S.rollQ = 0; measureVf()"); await pg.wait_for_timeout(900)
        print('after    ', await pg.evaluate(geo)); await pg.screenshot(path='/tmp/fk-shots/fs_after.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
