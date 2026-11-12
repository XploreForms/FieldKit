"""1.20.81 shell (frame.html): pages kept loaded, instant switching, Back button, stale Field Stock refresh, off switch."""
import asyncio, json, time
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True}), "fieldkit.shell": "test"}
CAM="""(()=>{const g=navigator.mediaDevices&&navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);if(g)navigator.mediaDevices.getUserMedia=c=>{if(c&&c.video&&typeof c.video==='object'){const v=Object.assign({},c.video);delete v.facingMode;delete v.deviceId;c=Object.assign({},c,{video:v});}return g(c);};
 window.__geo=0;if(navigator.geolocation){const o=navigator.geolocation.getCurrentPosition.bind(navigator.geolocation);navigator.geolocation.getCurrentPosition=(...a)=>{window.__geo++;return o(...a)};}})()"""
U='http://localhost:8765/'
ok=True
def check(name, cond, extra=''):
    global ok; ok = ok and bool(cond); print(('PASS ' if cond else 'FAIL ')+name, '' if cond else extra)
async def frame(pg, sel):
    h=await pg.query_selector(sel); return await h.content_frame() if h else None
async def cur(pg): return await frame(pg,'#stage iframe.on')
async def curpage(pg):
    f=await cur(pg); return f.url.split('/')[-1] if f else None
async def until(pg, fn, ms=6000):
    t=time.time()
    while time.time()-t<ms/1000:
        if await fn(): return round((time.time()-t)*1000)
        await pg.wait_for_timeout(20)
    return None
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
    ctx=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,permissions=['camera'])
    await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)"%json.dumps(SEED)); await ctx.add_init_script(CAM)
    pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    ctx.on('page', lambda x: None)
    await pg.goto(U+'index.html'); await pg.wait_for_timeout(800)
    check('opens in the shell', 'frame.html?u=index.html' in pg.url, pg.url)
    check('home on screen', (await curpage(pg))=='index.html', await curpage(pg))
    await pg.wait_for_timeout(5000)
    n=await pg.evaluate("[...document.querySelectorAll('#stage iframe')].map(f=>f.contentWindow.location.pathname.split('/').pop()+f.contentWindow.location.hash+(f.dataset.fkHidden?'(hidden)':''))")
    check('Field Stock and Manual Order preloaded hidden', sorted(n)==sorted(['index.html','fieldstock.html(hidden)','fieldstock.html#order(hidden)']), n)
    st=await frame(pg,'#stage iframe[src="fieldstock.html"]')
    check('hidden Field Stock: not shown, no GPS asked', (await st.evaluate("FieldKit.shown()"))==False and (await st.evaluate("window.__geo"))==0, await st.evaluate("[FieldKit.shown(),window.__geo]"))
    await st.evaluate("window.__mark=1")
    home=await cur(pg)
    # instant switch to Field Stock
    await home.locator('.tiles a',has_text='Field Stock').click()
    t=await until(pg, lambda: _is(pg,'fieldstock.html'))
    print('   Field Stock on screen after',t,'ms')
    check('Field Stock instant (<150 ms)', t is not None and t<150, t)
    check('address shows Field Stock', 'u=fieldstock.html' in pg.url, pg.url)
    check('same Field Stock (kept loaded)', await st.evaluate("window.__mark")==1)
    await pg.wait_for_timeout(300)
    check('shown Field Stock asks for GPS', await st.evaluate("FieldKit.shown() && window.__geo>0"))
    # back link -> home
    await st.locator('.fk-back').first.click()
    t=await until(pg, lambda: _is(pg,'index.html')); check('‹ back to home, instant', t is not None and t<150, t)
    check('address back to home', 'u=index.html' in pg.url, pg.url)
    # Manual Order then the phone's Back button
    home=await cur(pg); await home.locator('.tiles a',has_text='Manual Order').click()
    t=await until(pg, lambda: _is(pg,'fieldstock.html#order')); check('Manual Order instant', t is not None and t<150, t)
    await pg.go_back(); t=await until(pg, lambda: _is(pg,'index.html')); check('phone Back -> home', t is not None, await curpage(pg))
    # Back on home: warn first
    home=await cur(pg); await home.locator('.head').first.click(); await pg.wait_for_timeout(100)
    await pg.go_back(); await pg.wait_for_timeout(400)
    check('Back on home warns and stays', 'frame.html' in pg.url and (await pg.evaluate("document.getElementById('toast').classList.contains('show') && document.getElementById('toast').textContent")) == 'Press back again to close Field Kit', [pg.url, await pg.evaluate("document.getElementById('toast').textContent")])
    # SA flow
    home=await cur(pg)
    await home.locator('#jobStart').click(); await pg.wait_for_timeout(200)
    await home.get_by_role('button',name='Install',exact=True).click(); await home.locator('[data-nj=pt][data-v=FWN]').click(); await home.locator('#njRef').fill('1234567'); await home.locator('#njStart').click(); await pg.wait_for_timeout(400)
    await home.locator('#lobby button, #lobby a').filter(has_text='Pictures').first.click()
    t=await until(pg, lambda: _is(pg,'fieldcam.html#job'), 8000); check('Pictures opens (fresh page)', t is not None, await curpage(pg)); print('   Pictures on screen after',t,'ms')
    cam=await cur(pg); await pg.wait_for_timeout(2500)
    check('camera running in the shell', await cam.evaluate("S.started && !S.paused && !!document.getElementById('video').srcObject"))
    await cam.locator('#shutter').click(); await pg.wait_for_timeout(2500)
    await cam.locator('.fk-back').first.click()
    t=await until(pg, lambda: _is(pg,'index.html#job')); check('Pictures ‹ back to the SA page', t is not None, await curpage(pg))
    home=await cur(pg)
    check('SA page shows the new photo', '1' in (await home.locator('#lobby').inner_text()).split('Pictures')[1][:4], (await home.locator('#lobby').inner_text())[:200])
    check('Field Cam page closed', await pg.evaluate("![...document.querySelectorAll('#stage iframe')].some(f=>/fieldcam/.test(f.src))"))
    await home.locator('#lobby button, #lobby a').filter(has_text='Comments').first.click()
    t=await until(pg, lambda: _is(pg,'fieldnotes.html#job'), 8000); check('Comments opens', t is not None, await curpage(pg))
    nt=await cur(pg); await pg.wait_for_timeout(500); await nt.evaluate("STATE.other_notes='via shell'; wipSaveNow()")
    await nt.locator('.fk-back').first.click()
    t=await until(pg, lambda: _is(pg,'index.html#job')); check('Comments ‹ back to the SA page', t is not None, await curpage(pg))
    home=await cur(pg)
    check('answers reached the SA', await home.evaluate("(JSON.parse(localStorage.getItem('fieldkit.jobs'))[localStorage.getItem('fieldkit.activeJob')].notes.state||{}).other_notes")=='via shell')
    # stale Field Stock: a change elsewhere refreshes the hidden copy before it's shown
    st=await frame(pg,'#stage iframe[src="fieldstock.html"]'); await st.evaluate("window.__mark=2")
    await home.evaluate("localStorage.setItem('techstock.zztest', String(Date.now()))")
    await home.locator('#lbBack').click(); await pg.wait_for_timeout(1500)
    st=await frame(pg,'#stage iframe[src="fieldstock.html"]')
    check('Field Stock refreshed in the background', (await st.evaluate("window.__mark||0"))==0)
    home=await cur(pg); await home.locator('.tiles a',has_text='Field Stock').click()
    t=await until(pg, lambda: _is(pg,'fieldstock.html')); check('…and still opens instantly', t is not None and t<150, t)
    st=await cur(pg); await st.locator('.fk-back').first.click(); await until(pg, lambda: _is(pg,'index.html'))
    # reload keeps the page
    await pg.reload(); await pg.wait_for_timeout(1500); check('reload stays in the shell on home', (await curpage(pg)) in ('index.html',), [pg.url, await curpage(pg)])
    # off switch
    home=await cur(pg); await home.locator('#openSettings').click(); await pg.wait_for_timeout(300)
    await home.locator('#shellTog').click(); await pg.wait_for_timeout(1500)
    check('Instant switching off -> plain pages', 'frame.html' not in pg.url and pg.url.endswith('#settings') and await pg.evaluate("localStorage.getItem('fieldkit.shell')")=='off', pg.url)
    await pg.locator('#shellTog').click(); await pg.wait_for_timeout(1500)
    check('…and back on (switch cleared; tests stay on plain pages)', await pg.evaluate("localStorage.getItem('fieldkit.shell')") is None and 'shell=on' in pg.url, [pg.url, await pg.evaluate("localStorage.getItem('fieldkit.shell')")])
    await pg.evaluate("localStorage.setItem('fieldkit.shell','test')"); await pg.goto(U+'index.html'); await pg.wait_for_timeout(1200)
    check('…shell again', 'frame.html' in pg.url and (await curpage(pg))=='index.html', pg.url)
    errs=[e for e in errs if 'ViewTransition' not in e]; check('no page errors (shell)', not errs, errs)
    print('ALL PASS' if ok else 'SOME FAILED'); await b.close()
async def _is(pg, want): return (await curpage(pg))==want
asyncio.run(main())
