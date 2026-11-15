import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.167: FW conversion cabling: both answers confirmed in a pop-up naming Xplore-supplied cabling; Reused has Other (type why); X closes
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
        J=pg.locator('#form-mount')
        for n in ['Conversion','Fixed Wireless','Complete','FWN']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
        out = "buildOutput(false).split('\\n').filter(l=>/^Cabling:/.test(l))[0]"
        C=pg.locator('[data-field-id=cabling]')
        await C.get_by_text('Installed New Xplore Cabling').click(); await pg.wait_for_timeout(300)
        print('new: popup', await pg.locator('.ack-card').count(), '->', await pg.evaluate(out))
        await C.get_by_text('Reused Existing Cabling').click(); await pg.wait_for_timeout(300)
        print('reuse popup buttons:', await pg.locator('.ack-card button').all_inner_texts()); await pg.locator('.ack-card').screenshot(path='/tmp/fk-shots/ack2.png')
        await pg.locator('.ack-x').click(); await pg.wait_for_timeout(200); print('after X still new:', await pg.evaluate("STATE.cabling"))
        await C.get_by_text('Reused Existing Cabling').click(); await pg.wait_for_timeout(300)
        await pg.get_by_role('button', name='Other').click(); await pg.wait_for_timeout(300)
        print('other box:', await C.locator('input').count(), '| done?', not await pg.evaluate("validate().some(x=>x.id==='cabling')"))
        await C.locator('input').fill('customer refused new run through finished basement'); await pg.wait_for_timeout(200)
        print('other ->', await pg.evaluate(out), '| done?', not await pg.evaluate("validate().some(x=>x.id==='cabling')"))
        await C.get_by_text('Reused Existing Cabling').click(); await pg.wait_for_timeout(200); await pg.get_by_role('button', name='I Confirm').click(); await pg.wait_for_timeout(200)
        print('reuse ->', await pg.evaluate(out), '| box:', await C.locator('input').count())
        print('errors', errs); await b.close()
asyncio.run(main())
