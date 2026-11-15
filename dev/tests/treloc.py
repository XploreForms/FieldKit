import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for w in ['Conversion','Repair']:
            await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
            J=pg.locator('#form-mount')
            for n in [w,'Fixed Wireless','Complete','FWN']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
            opts = await pg.evaluate("[...document.querySelectorAll('[data-field-id=cabling] button.choice')].map(b=>b.textContent).join(' | ')")
            print(w, '| reloc tick:', await pg.get_by_text('CPE relocation required').count(), '| cabling:', opts)
            if w=='Conversion':
                await pg.get_by_text('CPE relocation required').click(); await pg.wait_for_timeout(250)
                print('   ', [l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if 'Relocation' in l or l.startswith('CPE:')])
                await pg.locator('[data-field-id=cpe]').scroll_into_view_if_needed(); await pg.evaluate("scrollBy(0,-60)")
                await pg.evaluate("document.querySelectorAll('*').forEach(e=>{const p=getComputedStyle(e).position; if(p==='fixed'||p==='sticky') e.style.visibility='hidden'})")
                await pg.screenshot(path='/tmp/fk-shots/reloc.png')
        print('errors', errs); await b.close()
asyncio.run(main())
