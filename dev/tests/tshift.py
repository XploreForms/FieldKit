import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
R='''()=>Object.fromEntries(['shutter','dlBtn','thumbBtn','snBtn','frame','labels','zoombar','jobBtn'].map(id=>{const e=document.getElementById(id)||document.querySelector('.'+id); if(!e) return [id,null]; const r=e.getBoundingClientRect(); return [id,[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)]];}))'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.BarcodeDetector = class { static async getSupportedFormats(){ return ['code_128']; } async detect(){ return []; } };")
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page()
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Conversion').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2500)
        await pg.evaluate("document.querySelectorAll('.toast').forEach(t=>t.remove())")
        a = await pg.evaluate(R); await pg.screenshot(path='/tmp/s_off.png')
        await pg.locator('#snBtn').click(); await pg.wait_for_timeout(700)
        bb = await pg.evaluate(R); await pg.screenshot(path='/tmp/s_on.png')
        for k in a: print(k.ljust(9), a[k], '->', bb[k], '' if a[k]==bb[k] else '  MOVED')
        await b.close()
    x,y=Image.open('/tmp/s_off.png'),Image.open('/tmp/s_on.png'); o=Image.new('RGB',(x.width*2+20,x.height),'white'); o.paste(x,(0,0)); o.paste(y,(x.width+20,0)); o.resize((o.width//2,o.height//2)).save('/tmp/fk-shots/shift.png')
asyncio.run(main())
