import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        async def where(tag):
            await pg.wait_for_timeout(1300)
            u = pg.url.replace(B,'')
            v = await pg.evaluate("()=>['menu','lobby','newjob','settings','setup'].filter(id=>{const e=document.getElementById(id);return e&&!e.hidden}).join(',')") if 'index' in u or u=='' else ''
            t = await pg.evaluate("()=>{const t=document.getElementById('toast'); return t && !t.hidden ? t.textContent : ''}") if 'index' in u else ''
            n = await pg.evaluate("window.navigation ? navigation.currentEntry.index+'/'+navigation.entries().length : '-'")
            print(f'{tag:34} {u:22} [{v}] {t!r} nav {n}')
        async def tap(): await pg.mouse.click(180, 760); await pg.wait_for_timeout(150)
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        if not await pg.get_by_text('Start New SA').count(): await pg.reload(); await pg.wait_for_timeout(1500)
        await where('launch')
        # 1) New SA screen, Back -> home
        await pg.get_by_text('Start New SA').first.click(); await where('New SA')
        await pg.go_back(); await where('Back from New SA')
        # 2) start an SA, go through Field Cam, back on the SA page
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        N=pg.locator('#newjob'); await pg.locator('#njRef').fill('1234567'); await N.locator('button').filter(has_text=X('Install')).click(); await N.locator('button').filter(has_text=X('Fixed Wireless')).click(); await N.locator('[data-nj=tech]').first.click()
        await pg.get_by_role('button', name='Start SA').click(); await where('Field Cam')
        await tap(); await pg.go_back(); await where('Back from Field Cam')
        await tap(); await pg.go_back(); await where('Back on SA page')
        # 3) settings
        await pg.locator('#openSettings').click(); await where('Settings')
        await pg.go_back(); await where('Back from Settings')
        # 4) home: warn, then close
        await tap(); await pg.go_back(); await where('Back on home (1st)')
        r = await pg.go_back(); await pg.wait_for_timeout(800); print('Back on home (2nd) ->', pg.url or '(left the app)')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
