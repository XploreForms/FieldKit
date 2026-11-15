import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.149: Drop Route from MPT Strand is always Aerial, to a Pole or a Midspan; off a midspan it's aerial too
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
        J=pg.locator('#form-mount')
        for n in ['Install','Fibre','Complete','FTX','Drop Required']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
        R=pg.locator('[data-field-id=route]')
        st = "[...document.querySelectorAll('[data-field-id=route] .rt-ghosts button')].map(b=>b.textContent+(b.disabled||b.getAttribute('aria-disabled')==='true'?'(off)':'')).join(', ')"
        await R.get_by_role('radio', name='MPT Strand').click(); await pg.wait_for_timeout(500)
        print('type buttons:', await R.locator('.rt-types button').count(), '| chosen:', await R.locator('.rt-type-chosen').all_inner_texts(), '| stops:', await pg.evaluate(st))
        await R.locator('[data-field-id=route] .rt-ghosts button, .rt-ghosts button').filter(has_text='Midspan').first.click(); await pg.wait_for_timeout(500)
        print('after Midspan -> chosen:', await R.locator('.rt-type-chosen').all_inner_texts(), '| stops:', await pg.evaluate(st))
        await R.locator('.rt-ghosts button').filter(has_text='Structure').first.click(); await pg.wait_for_timeout(500)
        print([l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if l.startswith('Drop Route')])
        await R.scroll_into_view_if_needed(); await R.screenshot(path='/tmp/fk-shots/strand.png')
        print('errors', errs); await b.close()
asyncio.run(main())
