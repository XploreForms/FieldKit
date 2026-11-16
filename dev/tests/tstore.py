import asyncio, json
from playwright.async_api import async_playwright
exec(open('dev/tests/tm2.py').read().split('async def main')[0])
# 1.20.189: Settings > SA history shows the space Field Kit uses (photos in IndexedDB, saved text)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(); ctx = await b.new_context(viewport={'width':360,'height':780}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(1000)
        await pg.evaluate("""()=>new Promise(res=>{const r=indexedDB.open('fieldcam',1);r.onupgradeneeded=()=>r.result.createObjectStore('photos',{keyPath:'id'});r.onsuccess=()=>{const st=r.result.transaction('photos','readwrite').objectStore('photos');for(let i=0;i<30;i++)st.put({id:'p'+i,blob:new Blob([new Uint8Array(400*1024)]),thumb:new Blob([new Uint8Array(25*1024)])});st.transaction.oncomplete=()=>{r.result.close();res()}}})""")
        await pg.locator('#openSettings').click(); await pg.wait_for_timeout(1200)
        print((await pg.locator('#sStore').inner_text()).replace('\n',' | '))
        await pg.locator('#sLim').fill('6.5'); await pg.wait_for_timeout(800)
        print('prefs:', await pg.evaluate("localStorage.getItem('fieldkit.prefs')"), '|', await pg.locator('#sUsed').inner_text())
        await pg.locator('#sStore').screenshot(path='/tmp/store.png')
        print('errors', errs); await b.close()
asyncio.run(main())
