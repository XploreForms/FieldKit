import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
CAM="""(()=>{const g=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);navigator.mediaDevices.getUserMedia=c=>{if(c&&c.video&&typeof c.video==='object'){const v=Object.assign({},c.video);delete v.facingMode;delete v.deviceId;v.width={ideal:1080};v.height={ideal:1440};c=Object.assign({},c,{video:v});}return g(c);};})()"""
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
        for (w,h) in [(360,640),(412,860)]:
            for mode in ('quick','sa'):
                ctx = await b.new_context(viewport={'width':w,'height':h}, device_scale_factor=2, has_touch=True, is_mobile=True, permissions=['camera'])
                await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED)); await ctx.add_init_script(CAM)
                pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
                if mode=='sa':
                    await pg.goto(B+'index.html'); await pg.wait_for_timeout(500); await pg.locator('#jobStart').click(); await pg.wait_for_timeout(200)
                    await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless', exact=True).click()
                    await pg.locator('[data-nj=tech]').first.click(); await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(400)
                    await pg.goto(B+'fieldcam.html#job')
                else: await pg.goto(B+'fieldcam.html')
                await pg.wait_for_timeout(4500)
                r = await pg.evaluate("""(()=>{const vf=document.getElementById('vf').getBoundingClientRect(),f=document.getElementById('frame').getBoundingClientRect(),d=document.querySelector('.deck').getBoundingClientRect(),t=document.querySelector('.top').getBoundingClientRect(),bk=document.getElementById('fkHome').getBoundingClientRect();return {top:Math.round(t.height),back:[Math.round(bk.left),Math.round(bk.width)],vfH:Math.round(vf.height),picH:Math.round(f.height),deck:[Math.round(d.top),Math.round(d.bottom)],scroll:document.documentElement.scrollHeight-innerHeight}})()""")
                print(w,h,mode,r,[e for e in errs if 'ViewTransition' not in e])
                await pg.screenshot(path=f'/tmp/fk-shots/cam5_{w}_{mode}.png'); await ctx.close()
        await b.close()
asyncio.run(main())
