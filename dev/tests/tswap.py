import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.165: FW conversion cabling / surge / grounding as tick cards (same saved answers and comment text as the old buttons)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.removeItem('xplore_fsl_wip_v2')"); await pg.reload(); await pg.wait_for_timeout(1200)
        J=pg.locator('#form-mount')
        for n in ['Conversion','Fixed Wireless','Complete','FWN']: await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(300)
        out = "buildOutput(false).split('\\n').filter(l=>/^(Cabling|Surge|Grounding):/.test(l))"
        st = "['cabling','surge','grounding'].map(k=>STATE[k]||'-').join(' / ')"
        print('start:', await pg.evaluate(st), '| small ticks:', await pg.locator('.swap-sub').all_inner_texts())
        await pg.get_by_text('Reused existing cabling (meets Xplore standards)').click(); await pg.wait_for_timeout(200)
        await pg.get_by_text('Installed new surge suppressor').click(); await pg.wait_for_timeout(200)
        await pg.get_by_text('Replaced an existing surge suppressor').click(); await pg.wait_for_timeout(200)
        await pg.get_by_text('Installed new grounding').click(); await pg.wait_for_timeout(200)
        print('picked:', await pg.evaluate(st)); print('   ', await pg.evaluate(out))
        await pg.get_by_text('Installed new Xplore standard cabling').click(); await pg.wait_for_timeout(200)
        await pg.get_by_text("Existing grounding wasn't up to Xplore standards").click(); await pg.wait_for_timeout(200)
        print('changed:', await pg.evaluate(st)); print('   ', await pg.evaluate(out))
        await pg.locator('[data-field-id=cabling]').scroll_into_view_if_needed(); await pg.evaluate("scrollBy(0,-60)")
        await pg.evaluate("document.querySelectorAll('*').forEach(e=>{const p=getComputedStyle(e).position; if(p==='fixed'||p==='sticky') e.style.visibility='hidden'})")
        await pg.screenshot(path='/tmp/fk-shots/swap.png')
        print('errors', errs); await b.close()
asyncio.run(main())
