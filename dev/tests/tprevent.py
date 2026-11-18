import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.222: Complete repairs ask Preventable Truck Roll (Yes/No, required); Yes asks what care could have done (required); both in the comment
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for path in (['Repair','Fixed Wireless','Complete','FWN'], ['Repair','Fibre','Complete','FTX'], ['Repair','VAS Only','Complete','XWR'], ['Install','Fixed Wireless','Complete','FWN'], ['Repair','Fixed Wireless','Cannot Complete','FWN']):
            await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
            J=pg.locator('#form-mount')
            for n in path: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(250)
            P=pg.locator('[data-field-id=preventable]'); has=await P.count()
            line=' '.join(path)
            if not has: print(line, '| no question'); continue
            secs=await pg.evaluate("[...document.querySelectorAll('[data-sec]')].map(e=>e.dataset.sec)")
            miss=await pg.evaluate("(()=>{const r=validate?validate():null;return JSON.stringify(r).includes('Remotely')})()") if False else None
            await P.get_by_text('Yes', exact=True).click(); await pg.wait_for_timeout(250)
            why=await pg.locator('[data-field-id=preventable_why]').count()
            await pg.locator('[data-field-id=preventable_why] textarea').fill('Radio locked to the wrong cell; care could re-lock it remotely.'); await pg.wait_for_timeout(200)
            out=[l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if 'Preventable' in l or 'Care Could' in l or 'PREVENTABLE' in l]
            print(line, '| sections:', secs, '| why box:', why, '|', out)
        await pg.screenshot(path='/tmp/prev.png')
        print('errors', errs); await b.close()
asyncio.run(main())
