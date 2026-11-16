import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.201: Signal Requirements Not Met asks QOI Met For and Speed Customer Wanted inside the Best Option Found card
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
        J=pg.locator('#form-mount')
        for n in ['Install','Fixed Wireless','Not Required','FWN']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(250)
        await J.get_by_text('Signal Requirements Not Met', exact=True).first.click(); await pg.wait_for_timeout(400)
        C=pg.locator('.tower-card').first
        print('in card:', await C.locator('[data-field-id=nr_qoi]').count(), '| want shown before qoi:', await C.locator('[data-field-id=nr_min]').count())
        await C.locator('[data-field-id=nr_qoi]').get_by_text('50x10', exact=True).click(); await pg.wait_for_timeout(300)
        print('want options:', await C.locator('[data-field-id=nr_min] .choice').all_inner_texts())
        await C.locator('[data-field-id=nr_min]').get_by_text('100x10', exact=True).click(); await pg.wait_for_timeout(300)
        print([l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if 'Best option' in l])
        await C.locator('[data-field-id=nr_qoi]').get_by_text('250x25', exact=True).click(); await pg.wait_for_timeout(300)
        print('after raising QOI, want cleared:', await pg.evaluate("STATE.nr_min"), '| options:', await C.locator('[data-field-id=nr_min] .choice').all_inner_texts())
        await C.scroll_into_view_if_needed(); await C.screenshot(path='/tmp/srnm.png')
        print('errors', errs); await b.close()
asyncio.run(main())
