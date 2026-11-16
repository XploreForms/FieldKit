import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.197: one XAP reason list and one Lawn Sign reason list (with Ground frozen) on every platform
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for path in (['Install','Fibre','Complete','FTX','Existing Drop'], ['Install','Fixed Wireless','Complete','FWN'], ['Install','Satellite','Complete','HJ3'], ['Conversion','Satellite','Complete','HJ3']):
            await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
            J=pg.locator('#form-mount')
            for n in path: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(250)
            out=[]
            for f in ('xap','lawn'):
                F=pg.locator(f'[data-field-id={f}]')
                if not await F.count(): out.append(f+': none'); continue
                await F.get_by_text('No', exact=True).first.click(); await pg.wait_for_timeout(250)
                out.append(f+': '+' / '.join([t for t in await F.locator('[data-anim$=_reason] .choice').all_inner_texts()]).replace('\n',''))
            print(path[0], path[1], '\n  ', '\n   '.join(out))
        print('errors', errs); await b.close()
asyncio.run(main())
