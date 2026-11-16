import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.218: one spelling per item (Bipod, Tri-Mast; 1.20.219) on the SA page, Comments and Manual Order; Pictures says SA, not job
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234566'); await pg.get_by_role('button', name='Install').first.click(); await pg.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await pg.locator('[data-nj=tech][data-v=FWN]').click()
        await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1500)
        G=pg.locator('#lbGear')
        print('SA mount buttons:', await G.locator('[data-slot-set=mount]').all_inner_texts())
        await G.locator('[data-slot-set=mount]').filter(has_text='Bipod').first.click(); await pg.wait_for_timeout(400)
        print('folded:', await G.locator('.fkj-val').first.inner_text(), '| saved:', await pg.evaluate("FieldKit.job.active().slots.mount"))
        # old Comments answer is renamed
        await pg.goto(B+'fieldnotes.html'); await pg.evaluate("localStorage.setItem('xplore_fsl_wip_v2', JSON.stringify({at:Date.now(), state:{job_type:'Install',job_plat:'Fixed Wireless',job_outcome:'Complete',job_tech:'FWN',fw_plat:'FWN',mount:'Bi-pod'}}))"); await pg.reload(); await pg.wait_for_timeout(1500)
        r = pg.get_by_role('button', name='Restore')
        if await r.count(): await r.first.click(); await pg.wait_for_timeout(600)
        print('comments mount:', await pg.evaluate("STATE.mount"), '| buttons:', await pg.locator('[data-field-id=mount] .choice').all_inner_texts())
        await pg.goto(B+'fieldstock.html#order'); await pg.wait_for_timeout(1200)
        print('order mount lines:', [t.replace('\n',' ') for t in await pg.locator('.ord-row').filter(has_text='Bipod').all_inner_texts()])
        print('errors', errs); await b.close()
asyncio.run(main())
