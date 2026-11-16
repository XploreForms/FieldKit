import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.204: inside an SA, Comments shows the job and the outcome as one line each with Change
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234566'); await pg.get_by_role('button', name='Install').first.click(); await pg.locator('[data-nj=fam][data-v="Fibre"]').click(); await pg.locator('[data-nj=tech][data-v=FTX]').click()
        await pg.locator('#newjob').get_by_text('Drop Required', exact=True).first.click()
        await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1500)
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
        S=pg.locator('.job-section')
        print((await S.inner_text()).replace('\n',' | '), '| radios:', await S.locator('[role=radio]').count())
        await S.locator('.sa-reason-btn').first.click(); await pg.wait_for_timeout(1500)
        print('job Change ->', pg.url.split('/')[-1])
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
        await pg.locator('.job-section .sa-reason-btn').nth(1).click(); await pg.wait_for_timeout(1500)
        print('outcome Change ->', pg.url.split('/')[-1], '| list open:', await pg.locator('.olist2').count())
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1200)
        await pg.evaluate('scrollTo(0,0)'); await pg.wait_for_timeout(200); await pg.screenshot(path='/tmp/jobrow.png', clip={'x':0,'y':0,'width':360,'height':330})
        print('errors', errs); await b.close()
asyncio.run(main())
