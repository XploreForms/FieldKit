import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':800}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.grant_permissions(['clipboard-read','clipboard-write'], origin=B[:-1])
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        if not await pg.get_by_text('Start New SA').count(): await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(1200)
        await pg.goto(B+'index.html#job'); await pg.wait_for_timeout(1200)
        gear = pg.locator('#lbGear')
        names = await gear.locator('.fkj-sh b').all_inner_texts(); print('slots:', names)
        t = await pg.locator('body').inner_text(); print('also logged?', 'Also logged' in t, '| leave line?', 'You can leave any time' in t)
        # type + Add on Radio
        rin = gear.locator('[data-slot-in="radio"]'); await rin.fill('ZTEABC123456')
        await gear.locator('[data-slot-add="radio"]').click(); await pg.wait_for_timeout(1200)
        await pg.screenshot(path='/tmp/fk-shots/after_add.png')
        opts = await pg.evaluate("()=>[...document.querySelectorAll('button')].filter(b=>b.offsetParent&&b.closest('[role=dialog],.fkj-pick,.fkj-modal,dialog')).map(b=>b.className+':'+b.innerText)")
        print('dialog buttons', opts[:6])
        if opts:
            await pg.locator('[role=dialog] button:visible, dialog button:visible, .fkj-pick button:visible').first.click(); await pg.wait_for_timeout(800)
        print('after Add:', (await gear.inner_text()).replace('\n',' | ')[:260])
        # paste icon on Router
        await pg.evaluate("navigator.clipboard.writeText('SN: RTR99887766')")
        await gear.locator('[data-slot-paste="router"]').click(); await pg.wait_for_timeout(1200)
        if await pg.locator('.fkj-opt:visible').count(): await pg.locator('.fkj-opt:visible').first.click(); await pg.wait_for_timeout(800)
        print('after paste:', 'RTR99887766' in await gear.inner_text())
        await pg.evaluate("document.querySelector('[data-slot-set]').scrollIntoView()"); await pg.screenshot(path='/tmp/fk-shots/lb_slots.png')
        # XWH / XTV appear when Field Notes says so
        r = await pg.evaluate('''()=>{ const J=FieldKit.job, j=J.active(); const a=J.slotModel(j,{xwh:"2",tv:"None"}).rows.map(r=>r.name); const b=J.slotModel(j,null).rows.map(r=>r.name); return [a,b]; }''')
        print('notes says 2 XWH:', r[0]); print('notes silent   :', r[1])
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
