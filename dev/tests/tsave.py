import asyncio, json, re
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True, accept_downloads=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'fieldcam.html'); await pg.wait_for_timeout(1500)
        await pg.evaluate("""async()=>{ window.__t=[]; const ot=toast; toast=(h,ms)=>{ window.__t.push(String(h).replace(/<[^>]+>/g,'')); ot(h,ms); };
          const c=document.createElement('canvas'); c.width=200;c.height=200; c.getContext('2d').fillRect(0,0,200,200); const blob=await (await fetch(c.toDataURL('image/jpeg'))).blob();
          const sid=(current&&current.id)||'s1'; for(let i=0;i<3;i++){ S.photos.push({id:'p'+i,sessionId:sid,created:Date.now()+i,blob,thumb:blob,raw:blob,labels:['Install Overview'],label:'Install Overview'}); }
          await downloadPhotos(S.photos.filter(p=>p.id.startsWith('p'))); }""")
        await pg.wait_for_timeout(500)
        print('\n'.join(await pg.evaluate("window.__t")))
        print('errors', errs); await b.close()
asyncio.run(main())
