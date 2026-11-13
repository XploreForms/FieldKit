import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1"}
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        for gs in (False, True):
          for (w,h) in [(320,568),(360,600),(360,640),(360,740),(390,700),(412,780),(412,880)]:
            ctx = await b.new_context(viewport={'width':w,'height':h}, device_scale_factor=2, has_touch=True, is_mobile=True)
            seed=dict(SEED)
            if gs: seed["techstock.gs"]=json.dumps({"connected":True})
            await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(seed))
            pg = await ctx.new_page()
            await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(500)
            await pg.locator('#jobStart').click(); await pg.wait_for_timeout(200)
            await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await pg.locator('[data-nj=tech][data-v=FWN]').click()
            await pg.locator('#njStart').click(); await pg.wait_for_timeout(400)
            res=[]
            for k in range(3):
                await pg.goto('http://localhost:8765/index.html'); await pg.wait_for_timeout(500)
                if k==2: await pg.reload(); await pg.wait_for_timeout(500)
                r = await pg.evaluate("""(()=>{const m=document.getElementById('menu'),cls=m.className,ja=document.getElementById('jobArea').getBoundingClientRect(),cut=[...document.querySelectorAll('.tiles small')].filter(e=>e.scrollHeight>e.clientHeight+1).length,tile=document.querySelector('.tiles a').getBoundingClientRect().height;return [document.documentElement.scrollHeight-innerHeight, Math.round(ja.bottom-innerHeight), cut, Math.round(tile), cls]})()""")
                res.append(r)
            print(w,h,'banner' if not gs else '-', res)
            await pg.screenshot(path=f'/tmp/fk-shots/fit_{w}x{h}_{int(gs)}.png'); await ctx.close()
        await b.close()
asyncio.run(main())
