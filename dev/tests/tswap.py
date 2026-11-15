import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.171: FW conversion cabling = Outdoor Cable (radio to surge) and Indoor Cable (surge to power supply), each New / Reused;
# reused asks for a confirmation (Other = type why); surge sits between them
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
        J=pg.locator('#form-mount')
        for n in ['Conversion','Fixed Wireless','Complete','FWN']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
        order = await pg.evaluate("[...document.querySelectorAll('#form-mount [data-field-id]')].map(e=>e.dataset.fieldId).filter(x=>['cab_out','surge','cab_in','grounding','ground_src'].includes(x)).join(' > ')")
        print('order:', order)
        out = "buildOutput(false).split('\\n').filter(l=>/^(Outdoor Cable|Indoor Cable|Surge|Grounding):/.test(l))"
        O=pg.locator('[data-field-id=cab_out]'); I=pg.locator('[data-field-id=cab_in]')
        await O.get_by_text('Installed New').click(); await pg.wait_for_timeout(250); print('outdoor new, popup:', await pg.locator('.ack-card').count())
        await I.get_by_text('Reused Existing').click(); await pg.wait_for_timeout(300)
        print('indoor popup:', await pg.locator('.ack-card p').inner_text())
        await pg.locator('.ack-card').screenshot(path='/tmp/fk-shots/ack3.png')
        await pg.get_by_role('button', name='I Confirm').click(); await pg.wait_for_timeout(250)
        await pg.get_by_text('Installed new Surge Protector').click(); await pg.wait_for_timeout(200)
        print('   ', await pg.evaluate(out))
        await O.get_by_text('Reused Existing').click(); await pg.wait_for_timeout(300); await pg.get_by_role('button', name='Other').click(); await pg.wait_for_timeout(300)
        print('outdoor other box:', await O.locator('input').count(), '| outdoor done?', not await pg.evaluate("validate().some(x=>x.id==='cab_out')"))
        await O.locator('input').fill('messenger cable replaced last year by Xplore contractor'); await pg.wait_for_timeout(200)
        print('   ', await pg.evaluate(out))
        # older single cabling answer maps to both runs
        await pg.evaluate("delete STATE.cab_out; delete STATE.cab_in; STATE.cabling='Installed New Xplore Cabling'; STATE.cabling_ack=true; render()"); await pg.wait_for_timeout(300)
        print('old answer mapped:', await pg.evaluate("[STATE.cab_out, STATE.cab_in, STATE.cabling||'-'].join(' / ')"))
        await O.scroll_into_view_if_needed(); await pg.evaluate("scrollBy(0,-60)")
        await pg.evaluate("document.querySelectorAll('*').forEach(e=>{const p=getComputedStyle(e).position; if(p==='fixed'||p==='sticky') e.style.visibility='hidden'})")
        await pg.screenshot(path='/tmp/fk-shots/segs.png')
        print('errors', errs); await b.close()
asyncio.run(main())
