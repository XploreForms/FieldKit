import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':760}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
            if await pg.get_by_text('Start New SA').count(): break
        print('headings:', await pg.locator('#menu .eyebrow').all_inner_texts())
        await pg.screenshot(path='/tmp/m1.png')
        # Field Notes in progress: start a one-time comment, then come back
        await pg.locator('#tools a', has_text='Field Notes').click(); await pg.wait_for_timeout(1500)
        print('opened:', pg.url.replace(B,''))
        await pg.locator('#form-mount button', has_text='Install').first.click(); await pg.wait_for_timeout(300)
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
        print('busy tiles:', await pg.locator('.mini.busy b').all_inner_texts())
        await pg.screenshot(path='/tmp/m2.png')
        await pg.locator('.mini [data-new]').click(); await pg.wait_for_timeout(200); await pg.screenshot(path='/tmp/m3.png')
        await pg.locator('.mini [data-new]').click(); await pg.wait_for_timeout(500)
        print('busy after clear:', await pg.locator('.mini.busy').count())
        print('overflow:', await pg.evaluate("document.documentElement.scrollWidth-innerWidth"), 'errors', [e for e in errs if 'ViewTransition' not in e])
        await b.close()
    ims=[Image.open(f'/tmp/m{i}.png') for i in (1,2,3)]; w,h=ims[0].size
    o=Image.new('RGB',(w*3+40,h),'white')
    for i,im in enumerate(ims): o.paste(im,(i*(w+20),0))
    o.resize((o.width//2,o.height//2)).save('/tmp/fk-shots/menu_new.png')
asyncio.run(main())
