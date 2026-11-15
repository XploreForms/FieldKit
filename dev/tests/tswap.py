import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.166: FW conversion: Cabling Installed New / Reused Existing (reused needs the confirmation), Surge = install tick, Grounding New / Reused
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
        J=pg.locator('#form-mount')
        for n in ['Conversion','Fixed Wireless','Complete','FWN']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
        out = "buildOutput(false).split('\\n').filter(l=>/^(Cabling|Surge|Grounding):/.test(l))"
        C=pg.locator('[data-field-id=cabling]')
        await C.get_by_text('Reused Existing Cabling').click(); await pg.wait_for_timeout(300)
        print('popup:', await pg.locator('.ack-card').count(), '| cabling before confirm:', await pg.evaluate("STATE.cabling||'-'"))
        await pg.locator('.ack-card').screenshot(path='/tmp/fk-shots/ack.png')
        await pg.get_by_role('button', name='Cancel').click(); await pg.wait_for_timeout(300); print('after cancel:', await pg.evaluate("STATE.cabling||'-'"))
        await C.get_by_text('Reused Existing Cabling').click(); await pg.wait_for_timeout(300); await pg.get_by_role('button', name='I Confirm').click(); await pg.wait_for_timeout(300)
        print('after confirm:', await pg.evaluate("STATE.cabling"), '| selected:', await C.locator('[aria-checked=true]').inner_text())
        await pg.locator('[data-field-id=grounding]').get_by_text('Reused Existing Grounding').click(); await pg.wait_for_timeout(200)
        print('   ', await pg.evaluate(out))
        print('surge done unticked?', await pg.evaluate("validate().some(x=>x.id==='surge')"))
        await pg.get_by_text('Installed new Surge Protector').click(); await pg.wait_for_timeout(200); print('   ', await pg.evaluate(out))
        await C.scroll_into_view_if_needed(); await pg.evaluate("scrollBy(0,-60)")
        await pg.evaluate("document.querySelectorAll('*').forEach(e=>{const p=getComputedStyle(e).position; if(p==='fixed'||p==='sticky') e.style.visibility='hidden'})")
        await pg.screenshot(path='/tmp/fk-shots/swap.png')
        print('errors', errs); await b.close()
asyncio.run(main())
