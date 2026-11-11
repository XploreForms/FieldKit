import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(400)
        print('outcome note gone:', 'Outcome starts as Complete' not in await pg.locator('body').inner_text())
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(1500)
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
        print(await pg.evaluate("[...document.querySelectorAll('#form-mount [data-field-id]')].map(e=>e.dataset.fieldId).join(',')"))
        M = pg.locator('#form-mount [data-field-id="mount"]')
        print('mount buttons:', (await M.locator('button').all_inner_texts())[:10])
        await M.scroll_into_view_if_needed()
        async def pick(t):
            import re as _r; await M.locator('button').filter(has_text=_r.compile('^'+_r.escape(t)+'$')).first.click(force=True); await pg.wait_for_timeout(300)
        async def ticks(): return [x.strip() for x in await M.locator('.mini-check').all_inner_texts()]
        async def comment():
            return await pg.evaluate("()=>{const t=document.body.innerText.split('\\n').find(l=>/^Mount:/.test(l.trim())); return t||'(no Mount line shown)'}")
        await pick('Tripod'); print('Tripod     ', await ticks(), '|', await comment(), '|', await pg.evaluate("[STATE.mount,STATE.mount_pole]"))
        await pg.screenshot(path='/tmp/fk-shots/fn_mount.png')
        await M.locator('.mini-check', has_text='10ft pole').click(); await pg.wait_for_timeout(300); print('pole off   ', await comment(), await pg.evaluate("[STATE.mount,STATE.mount_pole]"))
        await pick('J-Arm'); await M.locator('.mini-check', has_text='Side stays').click(); await pg.wait_for_timeout(300)
        print('J-Arm+stays', await ticks(), '|', await comment())
        await pick('Tower'); print('Tower      ', await ticks(), '|', await comment())
        await pick('Gable Mount'); print('Gable      ', await ticks(), '|', await comment())
        await pg.goto(B+'index.html#job'); await pg.wait_for_timeout(1200)
        print('slot after Notes Gable:', await pg.evaluate("FieldKit.job.active().slots.mount"))
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
