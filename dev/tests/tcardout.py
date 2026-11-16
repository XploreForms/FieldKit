import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.206: the home SA card's pill shows the outcome (Complete / Cannot Complete / Not Required) instead of In progress
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for w, th in ((320,'light'), (360,'black')):
            ctx = await b.new_context(viewport={'width':w,'height':700}, device_scale_factor=2, has_touch=True, is_mobile=True)
            await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
            pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(800)
            await pg.evaluate("t=>FieldKit.setPrefs({theme:t})", th)
            await pg.reload(); await pg.wait_for_timeout(1000)
            await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
            await pg.locator('#njRef').fill('1111111'); await pg.get_by_role('button', name='Install').first.click(); await pg.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await pg.locator('[data-nj=tech][data-v=FWN]').click()
            await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1200)
            for o, r in (('OK',''), ('CC','Reschedule'), ('NR','NLOS - No serviceable signal')):
                await pg.evaluate("([o,r])=>FieldKit.job.setOutcome(FieldKit.job.active(),o,r)", [o, r])
                await pg.goto(B+'index.html'); await pg.wait_for_timeout(1000)
                L=pg.locator('.jobwrap .live')
                print(w, th, o, await L.inner_text(), await pg.evaluate("(()=>{const h=document.querySelector('.jobwrap .job b');return h.scrollWidth<=h.clientWidth+1})()"))
                await pg.locator('.jobwrap').first.screenshot(path=f'/tmp/card-{w}-{o}.png')
            print('errors', errs); await ctx.close()
        await b.close()
asyncio.run(main())
