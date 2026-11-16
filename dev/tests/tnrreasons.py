import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.200: Not Required reasons per platform on the SA page and in Comments; follow-ups and photos by reason
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for fam, tech, extra, pick in (('Fixed Wireless','FWN',None,'NLOS - No serviceable signal'), ('Satellite','HJ3',None,'NLOS'), ('Fibre','FTX','Existing Drop','Not in Coverage Area'), ('VAS','XWR',None,'No Longer Required')):
            await pg.goto(B+'index.html'); await pg.evaluate("localStorage.removeItem('fieldkit.activeJob')"); await pg.reload(); await pg.wait_for_timeout(1200)
            await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
            await pg.locator('#njRef').fill('1234566'); await pg.get_by_role('button', name='Install').first.click(); await pg.locator(f'[data-nj=fam][data-v="{fam}"]').click(); await pg.locator(f'[data-nj={"vas" if fam=="VAS" else "tech"}][data-v={tech}]').click()
            if extra: await pg.locator('#newjob').get_by_text(extra, exact=True).first.click()
            await pg.get_by_role('button', name='Start SA').first.click(); await pg.wait_for_timeout(1800)
            await pg.locator('#lbOutBtn').click(); await pg.wait_for_timeout(300)
            nr = await pg.locator('[data-out=NR]').evaluate_all("bs=>bs.map(b=>b.dataset.r)")
            print(fam, len(nr), nr)
            await pg.locator(f'[data-out=NR][data-r="{pick}"]').click(); await pg.wait_for_timeout(500)
            await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
            print('  ', [l for l in (await pg.evaluate("buildOutput(false)")).split('\n') if l.startswith('Reason')], '| towers:', await pg.locator('[data-field-id=towers]').count(), '| structure:', await pg.locator('[data-field-id=nr_structure]').count())
        print('errors', errs); await b.close()
asyncio.run(main())
