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
        # photos as the earlier version left them: old device names, a "Device SN", and a normal custom one
        await pg.evaluate("""async()=>{ const c=document.createElement('canvas'); c.width=120;c.height=120; c.getContext('2d').fillRect(0,0,120,120); const blob=await (await fetch(c.toDataURL('image/jpeg'))).blob();
          const sid=current.id; const mk=(id,label,note)=>({id,sessionId:sid,created:Date.now()+S.photos.length,blob,thumb:blob,raw:blob,labels:[label],label,unlabelled:false,downloaded:true,note});
          const add=async r=>{ S.photos.push(r); await DB.put(r); };
          await add(mk('o1','ONT','Scanned S/N ALCLFFDBFA43')); await add(mk('o2','XWR','Scanned S/N 854V6W4QV0A3F3GA')); await add(mk('o3','XWH','Scanned S/N 834V6N317MA17G45'));
          await add(mk('o4','XTV','Scanned S/N E66AV5974844233')); await add(mk('o5','Device SN','Scanned S/N 854V6ZV15FSZ3A3X')); await add(mk('o6','Chargers',''));
          renderAll(); }""")
        print('before:', await pg.evaluate("JSON.stringify(countLabels())"))
        await pg.reload(); await pg.wait_for_timeout(3500)
        print('after reload:', await pg.evaluate("JSON.stringify(countLabels())"))
        print('tiles:', await pg.locator('#lGrid button').all_inner_texts())
        # now scan from the SA page: ONT, XWH and XTV
        await pg.goto(B+'index.html#job'); await pg.wait_for_timeout(1200)
        async def scan(code):
            await pg.locator('#lbGear [data-scanret=many]').first.click(); await pg.wait_for_timeout(2500)
            await pg.evaluate(f"capture = async () => null; readAim = async () => '{code}'; scanOnce()"); await pg.wait_for_timeout(1500)
            return await pg.evaluate("JSON.stringify(countLabels())")
        await pg.evaluate("location.href='fieldcam.html#job'"); await pg.wait_for_timeout(2500)
        await pg.screenshot(path='/tmp/fk-shots/sn_fixed.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
