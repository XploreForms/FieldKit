import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.196: Fibre conversions ask what happened to the original equipment (same choices as Fixed Wireless's Original CPE)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for path in (['Conversion','Fibre','Complete','FTX','Existing Drop'], ['Conversion','Fibre','Complete','FTX','Drop Required'], ['Conversion','Fixed Wireless','Complete','FWN']):
            await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
            J=pg.locator('#form-mount')
            for n in path: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
            R=pg.locator('[data-field-id=recovery]')
            lbl = await R.locator('.q').first.inner_text() if await R.count() else None
            if await R.count(): await R.get_by_text('Recovered for RMA', exact=True).click(); await pg.wait_for_timeout(300)
            print(path[1], path[-1], '|', lbl, '|', [l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if l.startswith('Recovery')])
        print('errors', errs); await b.close()
asyncio.run(main())
