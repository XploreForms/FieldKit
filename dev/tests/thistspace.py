import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.191: SA history depends on space, not age. A completed SA leaves once Field Cam cleared all its photos
# (its Field Cam job is gone); SAs without photos and SAs whose photos remain stay, however old.
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1000)
        await pg.evaluate("""()=>{const n=Date.now(),d=864e5,a={};
          a.kept={id:'kept',sa:'SA-1',status:'complete',created:n-90*d,updated:n-90*d,photos:12,camJobIds:['c1'],camJobId:'c1',notes:{}};
          a.gone={id:'gone',sa:'SA-2',status:'complete',created:n-20*d,updated:n-20*d,photos:9,camJobIds:['c2'],camJobId:'c2',notes:{}};
          a.nophotos={id:'nophotos',sa:'SA-3',status:'complete',created:n-60*d,updated:n-60*d,photos:0,camJobIds:[],notes:{}};
          localStorage.setItem('fieldkit.jobs',JSON.stringify(a)); localStorage.setItem('fieldcam.jobs',JSON.stringify({c1:{id:'c1'}}));}""")
        await pg.goto(B+'index.html#history'); await pg.wait_for_timeout(300); await pg.reload(); await pg.wait_for_timeout(1000)
        print('kept:', sorted(await pg.evaluate("Object.keys(JSON.parse(localStorage.getItem('fieldkit.jobs')))")), '|', await pg.locator('#histCount').inner_text())
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(800); await pg.locator('#openSettings').click(); await pg.wait_for_timeout(800)
        print('settings has weeks:', await pg.locator('[data-hist-weeks]').count(), '| storage:', (await pg.locator('#sStore').inner_text()).replace('\n',' | '))
        print('errors', errs); await b.close()
asyncio.run(main())
