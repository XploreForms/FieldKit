import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.194: Fibre Drop Required asks NID too, starting on Installed New (Existing Drop still starts blank)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
        J=pg.locator('#form-mount')
        for n in ['Install','Fibre','Complete','FTX','Drop Required']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
        N=pg.locator('[data-field-id=nid]')
        print('DR picked:', await N.locator('[aria-checked=true]').all_inner_texts(), '|', [l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if l.startswith('NID:')])
        await N.get_by_text('Pre-Installed', exact=True).click(); await pg.wait_for_timeout(300)
        print('changed:', [l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if l.startswith('NID:')])
        toast_before = await pg.locator('.toast').count()
        await J.get_by_text('Existing Drop', exact=True).first.click(); await pg.wait_for_timeout(400)
        print('ED picked:', await pg.locator('[data-field-id=nid] [aria-checked=true]').all_inner_texts())
        await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
        for n in ['Install','Fibre','Complete','FTX','Drop Required','Existing Drop']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
        print('untouched DR -> ED toast:', await pg.get_by_text('Answers cleared').count())
        print('errors', errs); await b.close()
asyncio.run(main())
