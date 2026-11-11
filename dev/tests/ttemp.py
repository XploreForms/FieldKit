import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for work,sub in [('Install','Drop Required'),('Install','Existing Drop'),('Conversion','Existing Drop'),('Install','Drop Only')]:
            for _ in range(2):
                await pg.goto(B+'index.html'); await pg.wait_for_timeout(1100)
                await pg.evaluate("FieldKit.job.setActive(null)"); await pg.reload(); await pg.wait_for_timeout(800)
                if await pg.get_by_text('Start New SA').count(): break
            await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300); N=pg.locator('#newjob')
            await pg.locator('#njRef').fill('1111111'); await N.locator('button').filter(has_text=X(work)).click(); await N.locator('button').filter(has_text=X('Fibre')).click()
            if await N.locator('button').filter(has_text=X(sub)).count(): await N.locator('button').filter(has_text=X(sub)).click()
            else: print(f'{work} {sub}: not offered on New SA'); continue
            await N.locator('[data-nj=tech]').first.click(); await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2000)
            await pg.locator('#outBtn, .outchip, button:has-text("Complete")').first.click(); await pg.wait_for_timeout(500)
            reasons = await pg.locator('#outPicker button').all_inner_texts()
            has = any('Temp Drop Required' in r for r in reasons)
            if has:
                await pg.locator('#outPicker button', has_text='Temp Drop Required').first.click(); await pg.wait_for_timeout(900)
            tiles = [t.replace('\n',' ') for t in await pg.locator('#lGrid button').all_inner_texts()]
            req = await pg.evaluate("[...document.querySelectorAll('#lGrid button')].map(b=>b.className.includes('need')||getComputedStyle(b).borderLeftColor).slice(0,3)") if False else ''
            prog = await pg.locator('#jobProg').inner_text() if await pg.locator('#jobProg').count() else ''
            print(f'{work:10} {sub:14} reason offered: {has} | counter {prog.strip()} | tiles: {tiles[:4]}')
            if work=='Install' and sub=='Drop Required': await pg.screenshot(path='/tmp/fk-shots/tempdrop.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
