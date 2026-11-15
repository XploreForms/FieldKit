import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.172: FW repair cabling = conversion layout; Surge Protector may be reused (Installed New / Reused Existing)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
        J=pg.locator('#form-mount')
        for n in ['Repair','Fixed Wireless','Complete','FWN']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
        print('labels:', await pg.evaluate("['cab_out','surge','cab_in','grounding'].map(k=>{const e=document.querySelector('[data-field-id='+k+'] .q'); return e?e.textContent:'-'}).join(' | ')"))
        print('surge buttons:', await pg.locator('[data-field-id=surge] button.choice').all_inner_texts())
        out = "buildOutput(false).split('\\n').filter(l=>/^(Outdoor Cable|Indoor Cable|Surge|Grounding):/.test(l))"
        await pg.locator('[data-field-id=cab_out]').get_by_text('Installed New').click(); await pg.wait_for_timeout(200)
        await pg.locator('[data-field-id=surge]').get_by_text('Reused Existing').click(); await pg.wait_for_timeout(200)
        await pg.locator('[data-field-id=cab_in]').get_by_text('Reused Existing').click(); await pg.wait_for_timeout(300); await pg.get_by_role('button', name='I Confirm').click(); await pg.wait_for_timeout(200)
        await pg.locator('[data-field-id=grounding]').get_by_text('Reused Existing').click(); await pg.wait_for_timeout(200)
        print('   ', await pg.evaluate(out))
        print('errors', errs); await b.close()
asyncio.run(main())
