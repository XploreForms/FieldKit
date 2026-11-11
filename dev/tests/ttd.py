import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
async def tiles(pg): return [t.replace('\n',' ') for t in await pg.locator('#lGrid button').all_inner_texts()]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1100)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300); N=pg.locator('#newjob')
        await pg.locator('#njRef').fill('1111111'); await N.locator('button').filter(has_text=X('Install')).click(); await N.locator('button').filter(has_text=X('Fibre')).click(); await N.locator('button').filter(has_text=X('Drop Required')).click(); await N.locator('[data-nj=tech]').first.click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2000)
        base = await tiles(pg); prog0 = (await pg.locator('#jobProg').inner_text()).strip()
        print('before: counter', prog0, '| Temp Drop Form tile:', any('Temp Drop Form' in t for t in base))
        # Field Notes: a buried span with Temp Drop Deployed ticked
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(2500)
        R = pg.locator('[data-field-id=route]'); await R.scroll_into_view_if_needed()
        await R.locator('button', has_text='MPT Vault').click(); await pg.wait_for_timeout(300)
        await R.locator('button:has-text("Buried")').first.click(); await pg.wait_for_timeout(300)
        h = await pg.evaluate("(()=>{const f=document.querySelector('[data-field-id=route]')||document.querySelector('[data-field-id=drop_route]'); const ids=[...document.querySelectorAll('#form-mount [data-field-id]')].map(e=>e.dataset.fieldId); return {ids: ids.join(','), route: f? f.innerText.slice(0,200):'(no route field)'}})()")
        print('fields:', h['ids'][:300]); print('route text:', h['route'].replace('\n',' | '))
        print('Notes tick label shown:', await pg.evaluate("(()=>{const t=document.body.innerText; return /Temp Drop Deployed/.test(t)})()"), '| tempDropNeeded before tick:', await pg.evaluate("tempDropNeeded()"))
        print('after picking Buried:', (await R.inner_text()).replace('\n',' | ')[:160])
        tick = R.locator('label, .mini-check, button', has_text='Temp Drop Deployed').first
        await tick.scroll_into_view_if_needed(); await tick.click(); await pg.wait_for_timeout(600)
        await R.locator('button', has_text='Structure').first.click(); await pg.wait_for_timeout(500)
        print('tempDropNeeded after tick:', await pg.evaluate("tempDropNeeded()"), '| Notes pictures checklist has it:', await pg.evaluate("dropPhotos().includes('Temp drop form')"))
        print('comment route line:', await pg.evaluate("(buildOutput(false).split('\\n').find(l=>/Temp Drop Deployed/.test(l))||'(none)')"))
        await pg.screenshot(path='/tmp/fk-shots/td_notes.png')
        await pg.goto(B+'fieldcam.html#job'); await pg.wait_for_timeout(2500)
        t = await tiles(pg); prog1 = (await pg.locator('#jobProg').inner_text()).strip()
        print('Field Cam: counter', prog1, '| tile:', [x for x in t if 'Temp Drop' in x])
        # untick -> gone
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(2200)
        tick = pg.locator('[data-field-id=route] label, [data-field-id=route] .mini-check, [data-field-id=route] button', has_text='Temp Drop Deployed').first; await tick.scroll_into_view_if_needed(); await tick.click(); await pg.wait_for_timeout(600)
        await pg.goto(B+'fieldcam.html#job'); await pg.wait_for_timeout(2500)
        print('after untick: counter', (await pg.locator('#jobProg').inner_text()).strip(), '| tile there:', any('Temp Drop Form' in x for x in await tiles(pg)))
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
