import asyncio, sys, json
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1","shipHold":"","shipNotes":""}),
        "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
async def main(page, y1, out):
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page()
        await pg.goto('http://localhost:8765/'+page); await pg.wait_for_timeout(1200)
        cdp = await ctx.new_cdp_session(pg); await cdp.send('Animation.enable'); await cdp.send('Animation.setPlaybackRate', {'playbackRate': 0.1})
        frames=[]
        await pg.evaluate(f'scrollTo(0,{y1})')
        for i in range(7):
            await pg.screenshot(path=f'/tmp/f{i}.png', clip={'x':0,'y':0,'width':390,'height':260}); frames.append(f'/tmp/f{i}.png')
            await pg.wait_for_timeout(400)
        await pg.evaluate('scrollTo(0,0)')
        for i in range(7,14):
            await pg.screenshot(path=f'/tmp/f{i}.png', clip={'x':0,'y':0,'width':390,'height':260}); frames.append(f'/tmp/f{i}.png')
            await pg.wait_for_timeout(400)
        ims=[Image.open(f) for f in frames]; w,h=ims[0].size
        o=Image.new('RGB',(w*7+60,h*2+10),'white')
        for i,im in enumerate(ims): o.paste(im,((i%7)*(w+10),(i//7)*(h+10)))
        o.resize((o.width//2,o.height//2)).save(out); await b.close()
asyncio.run(main(sys.argv[1], int(sys.argv[2]), sys.argv[3]))
