import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
X=lambda t: re.compile('^'+re.escape(t)+'$')
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for fam,sub in [('Fixed Wireless',None),('Fibre','Existing Drop')]:
            for _ in range(2):
                await pg.goto(B+'index.html'); await pg.wait_for_timeout(1200)
                await pg.evaluate("FieldKit.job.setActive(null)"); await pg.reload(); await pg.wait_for_timeout(900)
                if await pg.get_by_text('Start New SA').count(): break
            await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300); N=pg.locator('#newjob')
            await pg.locator('#njRef').fill('1234567'); await N.locator('button').filter(has_text=X('Install')).click(); await N.locator('button').filter(has_text=X(fam)).click()
            if sub: await N.locator('button').filter(has_text=X(sub)).click()
            await N.locator('[data-nj=tech]').first.click(); await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2000)
            await pg.evaluate("location.replace('fieldnotes.html#job')"); await pg.wait_for_timeout(2600)
            first = await pg.evaluate("(validate().filter(i=>i.id!=='tech')[0]||{}).label")
            top = await pg.evaluate("()=>{const h=document.querySelector('header.app-header').getBoundingClientRect().height; const els=[...document.querySelectorAll('#form-mount h2, #form-mount [data-field-id] > label, #form-mount .field-label, #form-mount [data-field-id] .lbl')]; const v=els.filter(e=>e.getBoundingClientRect().top>=h-2)[0]; return v? v.textContent.trim().slice(0,40):''}")
            print(f'{fam:15} scrolled to y={await pg.evaluate("Math.round(pageYOffset)")} | first unanswered: {first!r} | top of screen: {top!r}')
            await pg.screenshot(path=f'/tmp/fk-shots/fn_skip_{fam[:3]}.png')
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
