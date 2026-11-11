import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream']); ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True, permissions=['camera'])
        await ctx.add_init_script("window.BarcodeDetector = class { static async getSupportedFormats(){ return ['code_128']; } async detect(){ return []; } };")
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300); N=pg.locator('#newjob')
        await pg.locator('#njRef').fill('1111111'); await N.locator('button').filter(has_text=X('Install')).click(); await N.locator('button').filter(has_text=X('Fibre')).click(); await N.locator('button').filter(has_text=X('Existing Drop')).click(); await N.locator('[data-nj=tech]').first.click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2200)
        await pg.goto(B+'index.html#job'); await pg.wait_for_timeout(1200)
        # Scan beside each slot on the SA page (ONT, Router, then XWH via Scan More), one serial each
        for slot, code in [('ont','ALCLFFDBFA43'),('router','854V6W4QV0A3F3GA')]:
            await pg.locator(f'#lbGear .fkj-slot:has([data-slot-in="{slot}"]) [data-scanret=one]').click(); await pg.wait_for_timeout(2500)
            await pg.evaluate(f"""(async()=>{{ const c=document.createElement('canvas'); c.width=120;c.height=120; c.getContext('2d').fillRect(0,0,120,120); const blob=await (await fetch(c.toDataURL('image/jpeg'))).blob();
              capture = async () => {{ const labels=[...S.sel]; const r={{id:'x'+Math.random().toString(36).slice(2,6),sessionId:current.id,created:Date.now(),blob,thumb:blob,raw:blob,labels,label:labels[0]||'',unlabelled:!labels.length,downloaded:false,note:S.note}}; S.photos.unshift(r); await DB.put(r); renderAll(); return r; }};
              readAim = async () => '{code}'; scanOnce(); }})()"""); await pg.wait_for_timeout(2200)
            print(slot, 'back on', pg.url.replace(B,''))
        await pg.evaluate("location.href='fieldcam.html#job'"); await pg.wait_for_timeout(2500)
        print('tiles after scanning from the SA page:', [t.replace('\\n',' ') for t in await pg.locator('#lGrid button').all_inner_texts()][6:])
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
