import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.198: in an SA, Comments takes the outcome and reason from the SA page (read-only there, "Change on SA page");
# tapping another outcome in Comments opens the SA page's Change Outcome, and picking one comes back to Comments
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234566'); await pg.get_by_role('button', name='Install').first.click(); await pg.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await pg.locator('[data-nj=tech][data-v=FWN]').click()
        await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1500)
        await pg.evaluate("FieldKit.job.setOutcome(FieldKit.job.active(),'CC','Customer No Show')")
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
        R=pg.locator('[data-field-id=cc_reason]')
        print('reason row:', (await R.inner_text()).replace('\n',' | '), '| checklist:', await pg.locator('[data-field-id=cc_noshow]').count())
        print([l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if l.startswith('Reason')])
        await pg.locator('#form-mount').get_by_text('Complete', exact=True).first.click(); await pg.wait_for_timeout(1500)
        print('went to:', pg.url.split('/')[-1], '| outcome list open:', await pg.locator('.olist2').count())
        await pg.locator('[data-out=NR][data-r="NLOS - No serviceable signal"]').click(); await pg.wait_for_timeout(1800)
        print('back to:', pg.url.split('/')[-1], '| outcome:', await pg.evaluate("STATE.job_outcome"), '| reason row:', (await pg.locator('[data-field-id=nr_reason]').inner_text()).replace('\n',' | '))
        print([l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if l.startswith('Reason')], '| towers asked:', await pg.locator('[data-field-id=towers]').count())
        print('errors', errs); await b.close()
asyncio.run(main())
