import asyncio, json, re
from playwright.async_api import async_playwright
from PIL import Image
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        async def newsa():
            for _ in range(2):
                await pg.goto(B+'index.html'); await pg.wait_for_timeout(1300)
                await pg.evaluate("FieldKit.job.setActive(null)"); await pg.reload(); await pg.wait_for_timeout(900)
                if await pg.get_by_text('Start New SA').count(): break
            await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        N = pg.locator('#newjob')
        for fam in ['Fibre','Fixed Wireless','Satellite','Value Added Services']:
            await newsa(); await N.locator('button').filter(has_text=X('Install')).click(); await N.locator('button').filter(has_text=X(fam)).click(); await pg.wait_for_timeout(200)
            print(fam.ljust(22), 'labels:', await N.locator('.lbl').all_inner_texts(), '| tech:', await N.locator('[data-nj=tech]').all_inner_texts())
            if fam=='Satellite': await pg.screenshot(path='/tmp/sat.png')
        # missing technology
        await newsa(); await pg.locator('#njRef').fill('1234567'); await N.locator('button').filter(has_text=X('Install')).click(); await N.locator('button').filter(has_text=X('Fixed Wireless')).click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(300); print('error:', await pg.locator('#njErr').inner_text())
        await N.locator('[data-nj=tech]').filter(has_text=X('LTE')).click(); await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2500)
        print('cam header:', (await pg.locator('#jobBtn').inner_text()).replace('\n',' '))
        await pg.goto(B+'index.html#job'); await pg.wait_for_timeout(1200); print('SA page:', await pg.locator('#lbSub').inner_text())
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1500); print('Field Notes platform:', await pg.evaluate("STATE.fw_plat"))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200); print('home card:', (await pg.locator('#jobGo').inner_text()).replace('\n',' | '))
        await pg.screenshot(path='/tmp/home.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
    a=Image.open('/tmp/sat.png'); c=Image.open('/tmp/home.png'); o=Image.new('RGB',(a.width*2+20,a.height),'white'); o.paste(a,(0,0)); o.paste(c,(a.width+20,0)); o.resize((o.width//2,o.height//2)).save('/tmp/fk-shots/tech.png')
asyncio.run(main())
