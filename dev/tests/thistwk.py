import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.187: Settings > SA history (1/2/4/8 weeks, default 4); older completed SAs are cleared on load
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
        d=864e5
        await pg.evaluate("d=>{const n=Date.now(),a={};[['a',10],['b',20],['c',40]].forEach(([k,age])=>a[k]={id:k,sa:'SA-'+k,status:'complete',created:n-age*d,updated:n-age*d,notes:{}});localStorage.setItem('fieldkit.jobs',JSON.stringify(a));}", d)
        await pg.goto(B+'index.html#history'); await pg.wait_for_timeout(300); await pg.reload(); await pg.wait_for_timeout(1000)
        print('default keeps:', await pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('fieldkit.jobs')))"), '|', await pg.locator('#histCount').inner_text())
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1000); await pg.locator('#openSettings').click(); await pg.wait_for_timeout(500)
        print('pressed:', await pg.locator('[data-hist-weeks][aria-pressed=true]').inner_text())
        await pg.locator('[data-hist-weeks="2"]').click(); await pg.wait_for_timeout(300)
        print('prefs:', await pg.evaluate("localStorage.getItem('fieldkit.prefs')"))
        await pg.goto(B+'index.html#history'); await pg.wait_for_timeout(300); await pg.reload(); await pg.wait_for_timeout(1000)
        print('2 weeks keeps:', await pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('fieldkit.jobs')))"), '|', await pg.locator('#histCount').inner_text())
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(800)
        print('FLHA:', await pg.locator('[data-soon=flha] small').inner_text())
        print('errors', errs); await b.close()
asyncio.run(main())
