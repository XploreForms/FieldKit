import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1","shipHold":"","shipNotes":""}),
        "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        shots=[]
        async def snap(n):
            await pg.wait_for_timeout(1000); await pg.screenshot(path=f'/tmp/{n}.png', clip={'x':0,'y':0,'width':390,'height':330}); shots.append(n)
        await pg.goto(B+'index.html'); await snap('menu')
        await pg.get_by_text('Start New Job').first.click(); await snap('newjob')
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start Job').click(); await pg.wait_for_timeout(800)
        await pg.goto(B+'index.html#job'); await snap('lobby')
        await pg.goto(B+'fieldnotes.html'); await snap('notes')
        await pg.goto(B+'fieldstock.html'); await snap('stock')
        await pg.evaluate('scrollTo(0,400)'); await snap('stock_scrolled')
        ims=[Image.open(f'/tmp/{n}.png') for n in shots]; w,h=ims[0].size
        o=Image.new('RGB',(w*3+20,h*2+10),'white')
        for i,im in enumerate(ims): o.paste(im,((i%3)*(w+10),(i//3)*(h+10)))
        o.resize((o.width//2,o.height//2)).save('/tmp/fk-shots/slim_all.png'); print(shots, errs); await b.close()
asyncio.run(main())
