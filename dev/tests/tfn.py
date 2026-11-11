import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
CASES=[('Install','Fixed Wireless',None,'LTE'),('Install','Fibre','Existing Drop','ATX'),('Conversion','Satellite',None,'HTV'),('Repair','VAS Only',None,'XWH'),('Install','VAS Only',None,'XTV')]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for work,fam,sub,tech in CASES:
            for _ in range(2):
                await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
                await pg.evaluate("FieldKit.job.setActive(null)"); await pg.reload(); await pg.wait_for_timeout(900)
                if await pg.get_by_text('Start New SA').count(): break
            await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300); N=pg.locator('#newjob')
            await pg.locator('#njRef').fill('1234567'); await N.locator('button').filter(has_text=X(work)).click(); await N.locator('button').filter(has_text=X(fam)).click()
            if sub: await N.locator('button').filter(has_text=X(sub)).click()
            await N.locator('button').filter(has_text=X(tech)).click(); await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2000)
            await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
            r = await pg.evaluate("[STATE.job_tech||'', STATE.fw_plat||'', JSON.stringify(STATE.vas_gear||null), buildOutput(false).split('\\n')[0]]")
            shown = await pg.evaluate("[...document.querySelectorAll('[data-field-id=job] .choice[aria-checked=true]')].map(b=>b.textContent.replace('✓','').trim())")
            print(f'{work} {fam} {tech}: tech={r[0]} fw_plat={r[1]} vas_gear={r[2]} | picked={shown} || title: {r[3]}')
            if tech=='HTV': await pg.locator('[data-field-id=job]').screenshot(path='/tmp/fk-shots/fn_tech.png')
        # one-time Field Notes: switching platform clears a technology that doesn't fit
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(800); await pg.evaluate("FieldKit.job.setActive(null)")
        await pg.goto(B+'fieldnotes.html'); await pg.wait_for_timeout(1300)
        J=pg.locator('[data-field-id=job]')
        await J.locator('button').filter(has_text=X('Install')).click(); await J.locator('button').filter(has_text=X('Satellite')).click(); await J.locator('button').filter(has_text=X('HJ3')).click()
        a = await pg.evaluate("STATE.job_tech"); await J.locator('button').filter(has_text=X('Fixed Wireless')).click(); bb = await pg.evaluate("STATE.job_tech||''")
        await J.locator('button').filter(has_text=X('FWN')).click(); c = await pg.evaluate("[STATE.job_tech, STATE.fw_plat]")
        print('one-time: Satellite HJ3 ->', a, '| switch to FW ->', repr(bb), '| pick FWN ->', c)
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
