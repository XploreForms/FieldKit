import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
CASES=[('Install','Fixed Wireless',None,['O5SGS048614630','854V6W4QV0A3F3GA','834V6N317MA17G45','E66AV5974844233']),
       ('Install','Fibre','Existing Drop',['ALCLFFDBFA43','854V6ZV15FSZ3A3X']),
       ('Install','Satellite',None,['283705057839','1082600394','854V6ZZZZZZZZZZZ'])]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("window.BarcodeDetector = class { static async getSupportedFormats(){ return ['code_128']; } async detect(){ return []; } };")
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for work,fam,sub,codes in CASES:
            for _ in range(2):
                await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
                await pg.evaluate("FieldKit.job.setActive(null)"); await pg.reload(); await pg.wait_for_timeout(900)
                if await pg.get_by_text('Start New SA').count(): break
            await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
            N=pg.locator('#newjob'); await pg.locator('#njRef').fill('1234567')
            await N.locator('button').filter(has_text=X(work)).click(); await N.locator('button').filter(has_text=X(fam)).click()
            if sub: await N.locator('button').filter(has_text=X(sub)).click()
            await N.locator('[data-nj=tech]').first.click(); await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2200)
            await pg.evaluate("window.__sel=[]; capture = async () => { window.__sel.push(S.sel.join(' + ')); return null; }")
            await pg.locator('#snBtn').click(); await pg.wait_for_timeout(400)
            out=[]
            for c in codes:
                await pg.evaluate(f"window.__sel=[]; readAim = async () => '{c}'; scanOnce()"); await pg.wait_for_timeout(1200)
                out.append((c[:8], await pg.evaluate("window.__sel")))
                if await pg.locator('.fkj-opt:visible').count(): await pg.locator('.fkj-opt:visible').first.click(); await pg.wait_for_timeout(500)
            print(f'{fam:15}', out)
        # recovered scans keep the "<item> SN" label
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
