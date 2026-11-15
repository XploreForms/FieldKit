import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.134: Change Outcome on the SA page lists the reasons before Pictures is ever opened (from Field Cam's SETUP)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234566'); await pg.get_by_role('button', name='Install').click(); await pg.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await pg.locator('[data-nj=tech][data-v=FWN]').click()
        await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1200)
        await pg.locator('#lbOutBtn').click(); await pg.wait_for_timeout(300)
        print('install FW:', (await pg.locator('#lbOut .olist2').inner_text()).replace('\n',' | '))
        await pg.locator('[data-out=CC][data-r="Customer No Show"]').click(); await pg.wait_for_timeout(300)
        print('picked ->', (await pg.locator('#lbOut .ov').inner_text()).replace('\n',' | '))
        # change the SA to a Satellite repair: its own reasons
        await pg.locator('#lbChange').click(); await pg.wait_for_timeout(300)
        await pg.get_by_role('button', name='Repair').click(); await pg.locator('[data-nj=fam][data-v="Satellite"]').click(); await pg.locator('[data-nj=tech][data-v=HJ3]').click()
        await pg.locator('#njWhy').fill('test'); await pg.locator('#njStart').click(); await pg.wait_for_timeout(800)
        await pg.locator('#lbOutBtn').click(); await pg.wait_for_timeout(300)
        print('repair Sat:', (await pg.locator('#lbOut .olist2').inner_text()).replace('\n',' | '))
        print('errors', errs); await b.close()
asyncio.run(main())
