import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True}),
        "techstock.order": json.dumps({"qty":{"fam:ROUTER":3,"fam:CAT4 3.5GHZ":2,"fam:5G CPE":1},"reason":"","notes":""})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(700); await pg.goto(B+'fieldstock.html#order'); await pg.wait_for_timeout(1500)
        L=pg.locator('#ordList')
        rows = await L.evaluate("e=>[...e.querySelectorAll('.ord-group,.ord-pickhead,.ord-row')].map(c=>c.classList.contains('ord-group')?'## '+c.textContent:c.classList.contains('ord-pickhead')?'  '+c.innerText.replace(/\\n/g,' — ')+' [choose]':(c.classList.contains('sub')?'      · ':'  ')+c.querySelector('.ord-txt').innerText.replace(/\\n/g,' — ')+(c.querySelector('[data-oq]')?'':''))")
        print('\n'.join(rows))
        print('old any-model lines dropped; kept 5G CPE:', await pg.evaluate("localStorage.getItem('techstock.order')"))
        print('choose-a-model buttons:', await pg.locator('.ord-more').count(), '| CAT4 visible:', 'CAT4' in await L.inner_text(), '| Zyxel visible:', 'Zyxel EMG' in await L.inner_text())
        row = lambda t: L.locator('.ord-row').filter(has=pg.locator('b', has_text=re.compile('^'+re.escape(t)+'$')))
        for t in ['Adtran 854-V6','Hitron ARIA3321V','Nokia XS-010X','Drop - 300m - Evolv Dielectric Drop PushLok Tech','Kamai 7XM','AzEl - 90cm - Jupiter','Trimast - Viasat','Dish - 74cm - Jupiter','Pushlok Optitap Converter Kit (20)','Next Gen High Gain']:
            await row(t).locator('[data-d="1"]').click()
        await row('LTE CPE – CAT12 2.5 GHz').locator('[data-d="1"]').click()
        await pg.locator('#ordReason').fill('Warehouse short'); await pg.locator('#ordSend').click(); await pg.wait_for_timeout(600)
        body = await pg.evaluate("decodeURIComponent((document.querySelector('#detailSheet a[href^=\"mailto:\"]')||{}).href.split('body=')[1]||'')")
        print('--- email:'); print(body[body.index('Items'):body.index('Thank')].strip())
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await pg.screenshot(path='/tmp/fk-shots/ord2.png'); await b.close()
asyncio.run(main())
