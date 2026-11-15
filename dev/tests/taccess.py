import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.144: CPE Access defaults to serviceable from ladder; tick "Stepping onto roof required" (and "Tower climb required" on repairs)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        out = "[...buildOutput(false).split('\\n')].filter(l=>l.startsWith('CPE Access'))[0]"
        for work in ['Install','Repair']:
            await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
            J=pg.locator('#form-mount')
            for n in [work,'Fixed Wireless','Complete','FWN']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
            A=pg.locator('[data-field-id=cpe_access]')
            print(work, '| ticks:', await A.locator('.tick-row').all_inner_texts(), '|', await pg.evaluate(out))
            await A.get_by_text('Stepping onto roof required').click(); await pg.wait_for_timeout(250); print('   roof ->', await pg.evaluate(out))
            if work=='Repair':
                await A.get_by_text('Tower climb required').click(); await pg.wait_for_timeout(250); print('   + tower ->', await pg.evaluate(out))
                await A.scroll_into_view_if_needed(); await pg.evaluate("scrollBy(0,-40)"); await A.screenshot(path='/tmp/fk-shots/access.png')
        # an old saved answer
        await pg.evaluate("STATE.cpe_access='Stepping onto Roof Required'; delete STATE.cpe_roof; delete STATE.cpe_tower"); print('old answer ->', await pg.evaluate(out))
        print('errors', errs); await b.close()
asyncio.run(main())
