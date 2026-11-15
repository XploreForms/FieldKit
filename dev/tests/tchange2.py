import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.140: changing the job type / platform / technology / drop in Comments (inside an SA) goes through Change SA, then back
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234566'); await pg.get_by_role('button', name='Repair').click(); await pg.locator('[data-nj=fam][data-v="Satellite"]').click(); await pg.locator('[data-nj=tech][data-v=HJ3]').click()
        await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1000)
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
        J=pg.locator('#form-mount')
        await J.get_by_text('Fixed Wireless', exact=True).first.click(); await pg.wait_for_timeout(1500)
        print('went to:', pg.url.split('/')[-1], '| title:', await pg.locator('#newjob .njtitle').inner_text(), '| pressed:', await pg.evaluate("[...document.querySelectorAll('#njPick [aria-pressed=true]')].map(b=>b.textContent).join(',')"))
        await pg.locator('[data-nj=tech][data-v=FWN]').click(); await pg.locator('#njWhy').fill('dish could not get line of sight, moved to fixed wireless'); await pg.locator('#njStart').click(); await pg.wait_for_timeout(1800)
        print('back to:', pg.url.split('/')[-1])
        print('comments job:', await pg.evaluate("[STATE.job_type, STATE.job_plat, STATE.job_tech].join(' / ')"))
        print('comment head:', ' | '.join((await pg.evaluate("buildOutput(false)")).split('\n')[:5]))
        # Back without changing returns to Comments unchanged
        await pg.locator('#form-mount button.choice', has_text='Conversion').first.click(); await pg.wait_for_timeout(1500)
        await pg.locator('#njBack').click(); await pg.wait_for_timeout(1500)
        print('back without change:', pg.url.split('/')[-1], await pg.evaluate("STATE.job_type"))
        print('errors', errs); await b.close()
asyncio.run(main())
