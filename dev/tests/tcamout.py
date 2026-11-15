import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.162: inside an SA, Pictures shows the outcome but doesn't change it (or the job type)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=['--use-fake-device-for-media-stream','--use-fake-ui-for-media-stream']); ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234566'); await pg.get_by_role('button', name='Install').click(); await pg.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await pg.locator('[data-nj=tech][data-v=FWN]').click()
        await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1000)
        await pg.goto(B+'fieldcam.html#job'); await pg.wait_for_timeout(2500)
        print('chip:', repr(await pg.locator('#outBtn').inner_text()), '| hidden:', await pg.locator('#outBtn').is_hidden())
        await pg.evaluate("document.getElementById('outBtn').click()"); await pg.wait_for_timeout(400)
        print('outcome sheet open:', await pg.evaluate("document.getElementById('outSheet').classList.contains('open')"), '| toast:', await pg.evaluate("(document.querySelector('.toast')||{}).textContent||''"))
        await pg.evaluate("document.getElementById('jobBtn').click()"); await pg.wait_for_timeout(400)
        print('job sheet: picker hidden', await pg.locator('#sheetPicker').is_hidden(), '| outcome hidden', await pg.locator('#sheetOutcome').is_hidden(), '| hint:', await pg.locator('#jobEditHint').inner_text())
        print('errors', errs); await b.close()
asyncio.run(main())
