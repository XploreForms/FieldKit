import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.133: SA history and a completed SA's page show the finish time
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234566'); await pg.get_by_role('button', name='Repair').click(); await pg.locator('[data-nj=fam][data-v="Satellite"]').click(); await pg.locator('[data-nj=tech][data-v=HJ3]').click()
        await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1000)
        await pg.evaluate("(()=>{const j=FieldKit.job.active(); j.created=Date.now()-95*60000; FieldKit.job.save(j); FieldKit.job.complete(j.id)})()")
        await pg.goto(B+'fieldstock.html'); await pg.wait_for_timeout(600); await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
        await pg.locator('#openHist').click(); await pg.wait_for_timeout(500)
        print('history:', (await pg.locator('#hist li').first.inner_text()).replace('\n',' | '))
        await pg.locator('#hist [data-job]').first.click(); await pg.wait_for_timeout(600)
        print('SA page:', (await pg.locator('#lbStart').inner_text()).replace('\n',' | '))
        print('errors', errs); await b.close()
asyncio.run(main())
