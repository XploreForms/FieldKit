import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.195: VAS repair has no Equipment picker; it asks the location of the SA's Technology only
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
        J=pg.locator('#form-mount')
        for n in ['Repair','VAS Only','Complete','XWH']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
        print('picker:', await pg.locator('[data-field-id=vas_gear]').count(), '| fields:', await pg.evaluate("[...document.querySelectorAll('[data-field-id]')].map(e=>e.dataset.fieldId).filter(x=>/_loc$/.test(x))"))
        print([l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if 'XWH' in l or 'Equipment' in l])
        print('errors', errs); await b.close()
asyncio.run(main())
