import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.129: a repair's Equipment isn't done until something is deployed/recovered or "No equipment deployed or recovered" is ticked
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234566'); await pg.get_by_role('button', name='Repair').click(); await pg.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await pg.locator('[data-nj=tech][data-v=FWN]').click()
        await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1500)
        G=pg.locator('#lbGear')
        async def st(t): print(f'{t:22}', '| head done:', await G.locator('.lstep.done').count(), '| pill:', await G.locator('.pill').inner_text(), '| tick:', await pg.locator('#lbNoGear').count(), '| slots:', await G.locator('[data-slot-set]').count(), '| scan btn:', await G.locator('[data-scanret=many]').count())
        await st('new repair')
        await pg.evaluate("(()=>{const c=document.getElementById('lbNoGear'); c.checked=!c.checked; c.dispatchEvent(new Event('change',{bubbles:true}))})()"); await pg.wait_for_timeout(300); await st('ticked')
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1000); await pg.locator('[data-open-sa]').first.click(); await pg.wait_for_timeout(1000); await st('after reopen')
        await pg.evaluate("(()=>{const c=document.getElementById('lbNoGear'); c.checked=!c.checked; c.dispatchEvent(new Event('change',{bubbles:true}))})()"); await pg.wait_for_timeout(300); await st('unticked')
        await pg.locator('#lbDone').click(); await pg.wait_for_timeout(300); print('complete warning:', await pg.locator('#lbWarn').inner_text())
        await G.locator('[data-slot-set=mount]').filter(has_text='J-Arm').first.click(); await pg.wait_for_timeout(300); await st('J-Arm picked')
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1000); print('home chips:', (await pg.locator('.jprog').first.inner_text()).replace('\n',' '))
        print('errors', errs); await b.close()
asyncio.run(main())
