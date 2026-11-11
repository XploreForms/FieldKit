import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.BarcodeDetector = class { static async getSupportedFormats(){ return ['code_128']; } async detect(){ return []; } };")
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300); N=pg.locator('#newjob')
        await pg.locator('#njRef').fill('1111111'); await N.locator('button').filter(has_text=X('Install')).click(); await N.locator('button').filter(has_text=X('Fibre')).click(); await N.locator('button').filter(has_text=X('Existing Drop')).click(); await N.locator('[data-nj=tech]').first.click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2200)
        t = lambda n: pg.locator('#lGrid button').filter(has_text=X(n))
        await t('Indoor Cable Run').click(); await t('Install Overview').click(); await pg.wait_for_timeout(300)
        info = await pg.evaluate("""()=>{const h=document.getElementById('vfHint'), r=h.getBoundingClientRect(), v=document.getElementById('vf').getBoundingClientRect(), t=document.getElementById('toast').classList.contains('show');
          return {text:h.textContent, shown:h.classList.contains('show'), topInVf: Math.round(r.top - v.top), vfTop: Math.round(v.top), left:Math.round(r.left), right:Math.round(r.right), vfW:Math.round(v.width), toastShown:t}}""")
        print('hint:', info); await pg.screenshot(path='/tmp/fk-shots/vfhint.png', clip={'x':0,'y':0,'width':360,'height':300})
        await pg.wait_for_timeout(3000); print('hint gone after 3s:', not await pg.evaluate("document.getElementById('vfHint').classList.contains('show')"))
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
