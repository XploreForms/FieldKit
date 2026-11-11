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
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300); N=pg.locator('#newjob')
        await pg.locator('#njRef').fill('1234567'); await N.locator('button').filter(has_text=X('Install')).click(); await N.locator('button').filter(has_text=X('VAS Only')).click(); await N.locator('button').filter(has_text=X('XTV')).click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2000)
        await pg.evaluate("location.replace('fieldnotes.html#job')"); await pg.wait_for_timeout(3800)
        print('to answer:', await pg.evaluate("validate().filter(i=>i.id!=='tech').map(i=>i.id+':'+i.label)"))
        # answer each by tapping the first choice in its question
        for step in range(15):
            iss = await pg.evaluate("validate().filter(i=>i.id!=='tech').map(i=>i.id)")
            if not iss: break
            fid = iss[0]; f = pg.locator(f'#form-mount [data-field-id="{fid}"]')
            await f.scroll_into_view_if_needed()
            btn = f.locator('button.choice:not([disabled])')
            if step==0:
                bb = await btn.first.bounding_box(); print('xwh first btn box', bb)
                print('at point:', await pg.evaluate(f"(()=>{{const e=document.elementFromPoint({bb['x']+bb['width']/2},{bb['y']+bb['height']/2}); return e? e.tagName+'.'+e.className+' '+(e.textContent||'').slice(0,40):''}})()"))
                await pg.screenshot(path='/tmp/fk-shots/fin_dbg.png')
            no = btn.filter(has_text=X('1' if fid=='tv' else 'No'))
            if await no.count(): await no.first.click()
            elif await f.locator('[role=radiogroup]').count():
                groups = f.locator('[role=radiogroup]')
                for gi in range(await groups.count()):
                    g = groups.nth(gi)
                    if not await g.locator('[aria-checked=true]').count() and await g.locator('button:not([disabled])').count():
                        await g.locator('button:not([disabled])').first.click(); await pg.wait_for_timeout(150)
            elif await btn.count(): await btn.first.click()
            else:
                inp = f.locator('input:visible, textarea:visible').first; await inp.fill('Living room'); await inp.blur()
            await pg.wait_for_timeout(300)
            if step<2: print('  STATE.'+fid, await pg.evaluate(f"JSON.stringify(STATE['{fid}'])"), 'no-count', await no.count())
            print(f'answered {fid:14} y={await pg.evaluate("Math.round(pageYOffset)")}')
        await pg.wait_for_timeout(1200)
        r = await pg.evaluate("(()=>{const p=document.getElementById('preview').getBoundingClientRect(); return [Math.round(pageYOffset), Math.round(p.top), innerHeight]})()")
        print('after last answer: y=%d, comment top at %d of %d px screen' % tuple(r))
        await pg.screenshot(path='/tmp/fk-shots/fin.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
