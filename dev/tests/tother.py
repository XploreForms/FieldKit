import asyncio, json, sys
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
OUT=sys.argv[1]
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        for _ in range(2):
            await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
            if await pg.get_by_text('Start New SA').count(): break
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(300)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click(); await pg.locator('#newjob [data-nj=tech]').first.click()
        await pg.get_by_role('button', name='Start SA').click(); await pg.wait_for_timeout(2200)
        await pg.locator('#lGrid button', has_text='Other').click(); await pg.wait_for_timeout(400)
        print('camera view Other on top:', await pg.evaluate("()=>{const b=document.getElementById('otherBar'), r=b.getBoundingClientRect(); const t=document.elementFromPoint(r.x+r.width/2, r.y+r.height/2); return !b.hidden && b.contains(t)}"))
        await pg.keyboard.type('Shed'); await pg.keyboard.press('Enter'); await pg.wait_for_timeout(300); print('next photo label:', await pg.evaluate("S.sel"))
        # an unlabelled photo, then label it with Other…
        await pg.evaluate("""async()=>{ const c=document.createElement('canvas'); c.width=400;c.height=400; const x=c.getContext('2d'); x.fillStyle='#4a7';x.fillRect(0,0,400,400);
          const blob=await (await fetch(c.toDataURL('image/jpeg',.8))).blob(); const p={id:'t1',sessionId:current.id,created:Date.now(),blob,raw:blob,thumb:blob,unlabelled:true,labels:[]}; S.photos.push(p); try{await DB.put(p)}catch(e){}; renderAll(); openSorter(['t1']); }""")
        await pg.wait_for_timeout(600)
        print('sorter open:', await pg.evaluate("SO.open"), 'buttons:', (await pg.locator('#sorter button').all_inner_texts())[:30])
        await pg.locator('#sorter button', has_text='Other').first.click(); await pg.wait_for_timeout(500)
        vis = await pg.evaluate("""()=>{const b=document.getElementById('otherBar'), r=b.getBoundingClientRect(); const top=document.elementFromPoint(r.x+r.width/2, r.y+r.height/2); return {hidden:b.hidden, rect:[Math.round(r.x),Math.round(r.y),Math.round(r.width),Math.round(r.height)], onTop: !!top && b.contains(top), focus: document.activeElement.id}}""")
        print('Other bar:', vis)
        await pg.keyboard.type('Neighbours dish'); await pg.wait_for_timeout(200)
        await pg.screenshot(path=OUT)
        await pg.keyboard.press('Enter'); await pg.wait_for_timeout(500)
        print('label now:', await pg.evaluate("SO.sel"), '| shown:', (await pg.locator('#sorter').inner_text())[:160].replace('\n',' | '))
        print('errors', errs); await b.close()
asyncio.run(main())
