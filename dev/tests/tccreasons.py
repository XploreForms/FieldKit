import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.199: Cannot Complete reasons = the JotForm list (Fibre all 20, others 14) on the SA page and in Comments; old SA reasons move over
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for fam, tech, extra in (('Fixed Wireless','FWN',None), ('Fibre','FTX','Existing Drop')):
            await pg.goto(B+'index.html'); await pg.evaluate("localStorage.removeItem('fieldkit.activeJob')"); await pg.reload(); await pg.wait_for_timeout(1200)
            await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
            await pg.locator('#njRef').fill('1234566'); await pg.get_by_role('button', name='Install').first.click(); await pg.locator(f'[data-nj=fam][data-v="{fam}"]').click(); await pg.locator(f'[data-nj=tech][data-v={tech}]').click()
            if extra: await pg.locator('#newjob').get_by_text(extra, exact=True).first.click()
            await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1800)
            await pg.locator('#lbOutBtn').click(); await pg.wait_for_timeout(300)
            cc = await pg.locator('[data-out=CC]').evaluate_all("bs=>bs.map(b=>b.dataset.r)")
            print(fam, 'SA page CC reasons:', len(cc), cc[:4], '...')
            await pg.locator('[data-out=CC][data-r="Unable to Contact Customer / Customer Not Home"]').click(); await pg.wait_for_timeout(500)
            print('  photos needed:', await pg.evaluate("FieldKit.job.active().need"), '| Pictures list:', await pg.evaluate("""fetch('fieldcam.html').then(r=>r.text()).then(t=>{const a=t.indexOf('const PHOTOS = {');return t.includes('INS|Fixed Wireless|CC|Unable to Contact Customer / Customer Not Home')})"""))
            await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
            print('  comments reason:', (await pg.locator('[data-field-id=cc_reason]').inner_text()).replace('\n',' | '), '| checklist:', await pg.locator('[data-field-id=cc_noshow]').count())
            print('  ', [l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if l.startswith('Reason')])
        # old reason name on a saved SA moves over
        await pg.evaluate("(()=>{const a=JSON.parse(localStorage.getItem('fieldkit.jobs'));const j=a[localStorage.getItem('fieldkit.activeJob')];j.reason='Customer No Show';j.title=j.base+' · Cannot Complete · Customer No Show';localStorage.setItem('fieldkit.jobs',JSON.stringify(a));})()")
        await pg.goto(B+'index.html#job'); await pg.reload(); await pg.wait_for_timeout(1200)
        print('migrated:', await pg.evaluate("FieldKit.job.active().reason"), '|', await pg.evaluate("FieldKit.job.active().title"))
        print('errors', errs); await b.close()
asyncio.run(main())
