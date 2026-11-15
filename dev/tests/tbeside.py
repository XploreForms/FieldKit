import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.127: location cards (no side bar / Floor-Room labels) and "Router is beside the …"
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for plat, first, extra in [('Fixed Wireless','power',['FWN']), ('Satellite','modem',['HJ3']), ('Fibre','ont',['FTX','Existing Drop'])]:
            await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
            J=pg.locator('#form-mount')
            for n in ['Install',plat,'Complete']+extra: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(350)
            P=pg.locator(f'[data-field-id={first}]')
            await P.get_by_text('Main Floor', exact=True).click(); await pg.wait_for_timeout(250); await P.get_by_text('Utility Room', exact=True).click(); await pg.wait_for_timeout(250)
            print(plat, '| label:', (await P.locator('.q').first.inner_text()), '| sub-labels:', await P.locator('.sub-q').count(), '| tick:', await pg.locator('[data-field-id=router_beside]').inner_text())
            print('   router cards before tick:', await pg.locator('[data-field-id=router] .choices').count())
            await pg.get_by_text('Router is beside', exact=False).click(); await pg.wait_for_timeout(300)
            print('   after tick: router choices', await pg.locator('[data-field-id=router] .choices').count(), '| own router tick:', await pg.get_by_text('Customer using their own router').count())
            txt = await pg.evaluate("document.body.innerText")
            print('   comment:', [l for l in txt.split('\n') if l.startswith('Router Location') or l.startswith(('Power Supply Location','Modem Location','ONT Location'))][:3])
            if plat=='Fixed Wireless':
                await pg.evaluate("document.querySelectorAll('*').forEach(e=>{const p=getComputedStyle(e).position; if(p==='fixed'||p==='sticky') e.style.visibility='hidden'})")
                await P.scroll_into_view_if_needed(); await pg.evaluate("scrollBy(0,-60)"); await pg.screenshot(path='/tmp/fk-shots/beside.png')
            await pg.get_by_text('Router is beside', exact=False).click(); await pg.wait_for_timeout(300)
            print('   untick: router choices back', await pg.locator('[data-field-id=router] .choices').count())
        print('errors', errs); await b.close()
asyncio.run(main())
