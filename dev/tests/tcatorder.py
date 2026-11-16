import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.212: Field Stock item picker in Curtis's order, categories = Manual Order sections (Jupiter / Viasat for satellite)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(1500)
        g = await pg.evaluate("[...document.querySelectorAll('#skuSel optgroup')].map(o=>o.label+': '+[...o.children].map(c=>c.textContent).join(' | '))")
        print('\n'.join(g))
        print('slots radio/ont/modem:', await pg.evaluate("(()=>{const s=(window.FieldKit&&FieldKit.job&&FieldKit.job.slots)?FieldKit.job.slots():null;return s?[s.radio.skus.length,s.ont.skus.length,s.modem.skus]:'n/a'})()"))
        print('errors', errs); await b.close()
asyncio.run(main())
