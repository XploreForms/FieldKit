import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(1500)
        await pg.goto(B+'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
        J=pg.locator('#form-mount')
        for n in ['Install','Fixed Wireless','Complete']:
            await J.get_by_text(n, exact=True).first.click(); await pg.wait_for_timeout(400)
        print('section titles:', await pg.locator('#form-mount .form-section-title').all_inner_texts())
        pass
        M=pg.locator('[data-field-id=mount]')
        await M.get_by_text('J-Arm', exact=True).click(); await pg.wait_for_timeout(300)
        print('J-Arm reused tick:', await pg.get_by_text('Reused existing mount').count())
        await pg.get_by_text('Reused existing mount').click(); await pg.wait_for_timeout(200)
        await M.get_by_text('Tower', exact=True).click(); await pg.wait_for_timeout(300)
        print('Tower reused tick:', await pg.get_by_text('Reused existing mount').count(), '| reused state:', await pg.evaluate("STATE.mount_reused"))
        await M.scroll_into_view_if_needed(); await pg.evaluate("scrollBy(0,-250)"); await pg.screenshot(path='/tmp/fk-shots/tower.png')
        print('errors', errs); await b.close()
asyncio.run(main())
