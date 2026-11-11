import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':800}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        if not await pg.get_by_text('Start New SA').count(): await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(1500)
        await pg.goto(B+'index.html#job'); await pg.wait_for_timeout(1200)
        G = pg.locator('#lbGear')
        async def state(tag):
            v = await pg.evaluate("()=>{const j=FieldKit.job.active(); return [j.slots&&j.slots.mount, FieldKit.job.deployed(j).map(e=>e.sku).filter(s=>s!=='PVFWSURGE').join(',')]}")
            chks = await G.locator('.fkj-chk').all_inner_texts()
            print(f'{tag:28}', v, '| ticks:', [c.split('\n')[0] for c in chks])
        await state('start')
        await G.locator('[data-slot-set=mount]').filter(has_text='Gable Mount').click(); await pg.wait_for_timeout(300); await state('tap Gable Mount')
        await G.locator('.fkj-chk', has_text='10ft pole').click(); await pg.wait_for_timeout(300); await state('untick pole')
        await G.locator('[data-slot-set=mount]').filter(has_text='Gable Mount').click(); await pg.wait_for_timeout(300); await state('tap Gable again')
        await G.locator('[data-slot-set=mount]').filter(has_text='Tripod').click(); await pg.wait_for_timeout(300); await state('tap Tripod')
        await pg.evaluate("document.querySelector('#lbGear .fkj-slot').scrollIntoView({block:'start'})"); await pg.evaluate("scrollBy(0,-120)"); await pg.wait_for_timeout(200)
        await pg.screenshot(path='/tmp/fk-shots/mount1.png')
        await G.locator('.fkj-chk', has_text='No new mount').click(); await pg.wait_for_timeout(300); await state('tick No new mount')
        await pg.screenshot(path='/tmp/fk-shots/mount2.png')
        await G.locator('.fkj-chk', has_text='No new mount').click(); await pg.wait_for_timeout(300); await state('untick No new mount')
        await G.locator('[data-slot-set=mount]').filter(has_text='J-Arm').click(); await pg.wait_for_timeout(300); await state('tap J-Arm')
        await G.locator('[data-slot-set=mount]').filter(has_text='Bipod').click(); await pg.wait_for_timeout(300); await state('tap Bipod')
        # Field Notes answers carry over
        for mount, reused in [('Tower', False), ('J-Arm + Side Stays', False), ('Gable Mount + 10ft Pole', True), ('Tripod + 10ft Pole', False)]:
            await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1000)
            await pg.evaluate(f"()=>{{ STATE.mount={json.dumps(mount)}; STATE.mount_reused={'true' if reused else 'false'}; const w=JSON.parse(localStorage.getItem('xplore_fsl_wip_v2')); w.state.mount=STATE.mount; w.state.mount_reused=STATE.mount_reused; localStorage.setItem('xplore_fsl_wip_v2', JSON.stringify(w)); }}")
            await pg.goto(B+'index.html#job'); await pg.wait_for_timeout(1000)
            await state(f'Notes: {mount}{" + reused" if reused else ""}'[:28])
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
