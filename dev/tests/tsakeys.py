import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.211: with the keyboard up (simulated by shrinking the window), the New SA bar sits right above it, no gap
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.get_by_role('button', name='Install').first.click(); await pg.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await pg.locator('[data-nj=tech][data-v=FWN]').click()
        await pg.wait_for_timeout(300)
        await pg.locator('#njRef').focus(); await pg.wait_for_timeout(100)
        await pg.evaluate("scrollTo(0, 0)")   # what the phone did: page scrolled the wrong way
        await pg.set_viewport_size({'width':360,'height':430}); await pg.wait_for_timeout(700)
        r = await pg.evaluate("(()=>{const b=document.querySelector('#newjob .njgo').getBoundingClientRect();return [Math.round(b.top),Math.round(b.bottom),innerHeight,scrollY]})()")
        print('bar top/bottom, window, scrollY:', r, '| gap under bar:', r[2]-r[1])
        await pg.screenshot(path='/tmp/keys.png')
        print('meta:', await pg.evaluate("document.querySelector('meta[name=viewport]').content"))
        print('errors', errs); await b.close()
asyncio.run(main())
