import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.grant_permissions(['clipboard-read','clipboard-write'], origin=B[:-1])
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        shots=[]
        async def shot(sel, name, pad=30):
            el = pg.locator(sel).first; await el.scroll_into_view_if_needed(); bb = await el.bounding_box()
            await pg.screenshot(path=f'/tmp/{name}.png', clip={'x':0,'y':max(0,bb['y']-pad),'width':360,'height':bb['height']+2*pad}); shots.append(name)
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(400)
        await pg.evaluate("navigator.clipboard.writeText('Service Appointment SA-7654321 for customer')")
        await pg.locator('#njPaste').click(); await pg.wait_for_timeout(400); print('New SA paste ->', await pg.locator('#njRef').input_value())
        await shot('.njref','newsa')
        # one-time Field Cam start screen
        await pg.goto(B+'fieldcam.html'); await pg.wait_for_timeout(1800)
        if await pg.locator('#inRef').is_visible():
            await pg.locator('[data-paste=inRef]').click(); await pg.wait_for_timeout(400); print('Cam paste ->', await pg.locator('#inRef').input_value())
            await shot('#inRef','cam', 40)
        # Field Stock deploy SA box
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1500)
        await pg.get_by_role('button', name='Deploy').first.click(); await pg.wait_for_timeout(500)
        if await pg.locator('#accountIn').is_visible():
            await pg.locator('[data-sapaste=accountIn]').click(); await pg.wait_for_timeout(400); print('Stock paste ->', await pg.locator('#accountIn').input_value())
            await shot('.sa-in','stock')
        ims=[Image.open(f'/tmp/{n}.png') for n in shots]; H=sum(i.height for i in ims)+10*len(ims)
        o=Image.new('RGB',(720,H),'white'); y=0
        for im in ims: o.paste(im,(0,y)); y+=im.height+10
        o.save('/tmp/fk-shots/paste_all.png'); print(shots, [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
