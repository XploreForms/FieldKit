import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.158: MPT Light Level Reading is the first question after the drop type on Drop Required / Drop Only installs
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for drop in ['Drop Required','Drop Only','Existing Drop']:
            await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
            J=pg.locator('#form-mount')
            for n in ['Install','Fibre','Complete','FTX',drop]: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
            ids = await pg.evaluate("[...document.querySelectorAll('#form-mount .form-section [data-field-id]')].map(e=>e.dataset.fieldId).filter((v,i,a)=>a.indexOf(v)===i).slice(0,5).join(', ')")
            print(drop, '| first fields:', ids)
            if drop=='Drop Required':
                M=pg.locator('[data-field-id=mpt_light] input'); await M.fill('19'); await M.blur()
                N=pg.locator('[data-field-id=light] input'); await N.fill('30'); await N.blur(); await pg.wait_for_timeout(600)
                print('   lines:', [l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if 'Light Level' in l])
                print('   NID odd-reading warning shown:', await pg.locator('[data-field-id=light] .warn').count(), '| MPT warning:', await pg.locator('[data-field-id=mpt_light] .warn').count())
                await pg.locator('[data-field-id=mpt_light]').scroll_into_view_if_needed(); await pg.evaluate("scrollBy(0,-230)")
                await pg.evaluate("document.querySelectorAll('*').forEach(e=>{const p=getComputedStyle(e).position; if(p==='fixed'||p==='sticky') e.style.visibility='hidden'})")
                await pg.screenshot(path='/tmp/fk-shots/mpt.png')
        print('errors', errs); await b.close()
asyncio.run(main())
