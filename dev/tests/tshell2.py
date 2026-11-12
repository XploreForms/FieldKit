"""1.20.82 shell: Field Cam and Comments kept loaded. Pictures / Comments open instantly the second time (and the first,
once preloaded on the SA page), going back and forth doesn't reload either, a change on the SA page (outcome) reaches
both, a new SA gets fresh pages, a completed SA drops them, and the camera pauses while hidden."""
import asyncio, json, time
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True}), "fieldkit.shell": "test"}
CAM="""(()=>{const g=navigator.mediaDevices&&navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);if(g)navigator.mediaDevices.getUserMedia=c=>{if(c&&c.video&&typeof c.video==='object'){const v=Object.assign({},c.video);delete v.facingMode;delete v.deviceId;c=Object.assign({},c,{video:v});}return g(c);};})()"""
U='http://localhost:8765/'
ok=True
def check(name, cond, extra=''):
    global ok; ok = ok and bool(cond); print(('PASS ' if cond else 'FAIL ')+name, '' if cond else extra)
async def cur(pg):
    h=await pg.query_selector('#stage iframe.on'); return await h.content_frame() if h else None
async def curpage(pg):
    f=await cur(pg); return f.url.split('/')[-1] if f else None
async def until(pg, want, ms=8000):
    t=time.time()
    while time.time()-t<ms/1000:
        if (await curpage(pg))==want: return round((time.time()-t)*1000)
        await pg.wait_for_timeout(15)
    return None
async def fr(pg, src):
    h=await pg.query_selector('#stage iframe[src="%s"]'%src); return await h.content_frame() if h else None
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
    ctx=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,permissions=['camera'])
    await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)"%json.dumps(SEED)); await ctx.add_init_script(CAM)
    pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(U+'index.html'); await pg.wait_for_timeout(5000)
    home=await cur(pg)
    async def startSA(ref, pt):
      h=await cur(pg)
      await h.locator('#jobStart').click(); await pg.wait_for_timeout(200)
      await h.get_by_role('button',name='Install',exact=True).click(); await h.locator('[data-nj=pt][data-v=%s]'%pt).click()
      if pt=='ATX': await h.get_by_role('button',name='Existing Drop',exact=True).click()
      await h.locator('#njRef').fill(ref); await h.locator('#njStart').click(); await pg.wait_for_timeout(300)
    async def open_(txt, want):
      h=await cur(pg); await h.locator('#lobby button, #lobby a').filter(has_text=txt).first.click(); return await until(pg, want)
    async def back():
      c=await cur(pg); await c.locator('.fk-back').first.click(); return await until(pg,'index.html#job')
    await startSA('1234567','ATX')
    await pg.wait_for_timeout(7000)   # Pictures, then Comments, load in the background
    srcs=await pg.evaluate("[...document.querySelectorAll('#stage iframe')].map(f=>f.getAttribute('src')+(f.dataset.fkHidden?'(hidden)':''))")
    check('Pictures and Comments preloaded hidden on the SA page', 'fieldcam.html#job(hidden)' in srcs and 'fieldnotes.html#job(hidden)' in srcs, srcs)
    cam=await fr(pg,'fieldcam.html#job')
    check('preloaded Pictures has no camera yet', not await cam.evaluate("!!document.getElementById('video').srcObject"))
    await cam.evaluate("window.__m=1"); nt=await fr(pg,'fieldnotes.html#job'); await nt.evaluate("window.__m=1")
    t=await open_('Pictures','fieldcam.html#job'); print('   Pictures (first) after',t,'ms')
    check('Pictures opens instantly the first time', t is not None and t<200, t)
    await pg.wait_for_timeout(2500)
    check('camera starts once shown', await cam.evaluate("S.started && !S.paused && !!document.getElementById('video').srcObject"))
    await cam.locator('#shutter').click(); await pg.wait_for_timeout(2500)
    await back(); await pg.wait_for_timeout(300)
    check('camera paused while hidden', await cam.evaluate("S.paused && !FieldKit.shown()"))
    h=await cur(pg); check('SA page shows the photo', '1 NOT SAVED' in (await h.locator('#lobby').inner_text()), (await h.locator('#lobby').inner_text())[:200])
    t=await open_('Comments','fieldnotes.html#job'); print('   Comments after',t,'ms')
    check('Comments instant', t is not None and t<200, t)
    check('…same page (not reloaded)', await nt.evaluate("window.__m")==1)
    await nt.evaluate("STATE.other_notes='kept'; wipSaveNow()")
    await back()
    for i in range(2):
      t=await open_('Pictures','fieldcam.html#job'); a=await cam.evaluate("window.__m")
      check(f'Pictures again ({i+1}): instant, not reloaded', t is not None and t<200 and a==1, [t,a]); await pg.wait_for_timeout(1200)
      check(f'…camera running again ({i+1})', await cam.evaluate("S.started && !S.paused && document.getElementById('video').srcObject.getVideoTracks()[0].readyState==='live'"))
      await back()
      t=await open_('Comments','fieldnotes.html#job'); a=await nt.evaluate("window.__m")
      check(f'Comments again ({i+1}): instant, not reloaded', t is not None and t<200 and a==1, [t,a])
      check(f'…answer still there ({i+1})', await nt.evaluate("STATE.other_notes")=='kept')
      await back()
    # hidden a while: the camera is let go, and comes back when shown
    await pg.wait_for_timeout(21000)
    check('camera released after 20 s hidden', await cam.evaluate("S.stream.getVideoTracks()[0].readyState")=='ended')
    t=await open_('Pictures','fieldcam.html#job'); await pg.wait_for_timeout(2000)
    check('…and restarts when shown', t is not None and t<200 and await cam.evaluate("document.getElementById('video').srcObject.getVideoTracks()[0].readyState")=='live', t)
    await back()
    # outcome changed on the SA page: both follow
    h=await cur(pg); await h.locator('#lbOutBtn').click(); await pg.wait_for_timeout(150)
    await h.locator('[data-out=CC]').first.click(); await pg.wait_for_timeout(1500)
    t=await open_('Comments','fieldnotes.html#job'); nt=await cur(pg); await pg.wait_for_timeout(400)
    check('Comments shows the new outcome', await nt.evaluate("STATE.job_outcome")=='Cannot Complete', await nt.evaluate("STATE.job_outcome"))
    check('…and kept the other answer', await nt.evaluate("STATE.other_notes")=='kept')
    await back()
    t=await open_('Pictures','fieldcam.html#job'); cam=await cur(pg); await pg.wait_for_timeout(400)
    check('Pictures shows the new outcome', await cam.evaluate("curJob().outcome")=='CC', await cam.evaluate("curJob().outcome"))
    check('…and still has the photo', await cam.evaluate("curPhotos().length")==1)
    await back()
    oc=await h.evaluate("JSON.parse(localStorage.getItem('fieldkit.jobs'))[localStorage.getItem('fieldkit.activeJob')].outcome") if False else None
    h=await cur(pg); j=await h.evaluate("JSON.parse(localStorage.getItem('fieldkit.jobs'))[localStorage.getItem('fieldkit.activeJob')]")
    check('SA still Cannot Complete after the round trip', j['outcome']=='CC', j['outcome'])
    # complete the SA: kept pages dropped; a new SA gets fresh ones
    await h.evaluate("FieldKit.job.complete(localStorage.getItem('fieldkit.activeJob'))"); await h.locator('#lbBack').click(); await pg.wait_for_timeout(1500)
    srcs=await pg.evaluate("[...document.querySelectorAll('#stage iframe')].map(f=>f.getAttribute('src'))")
    check('completed SA: Pictures and Comments dropped', not any('#job' in s and 'index' not in s for s in srcs), srcs)
    await startSA('7654321','FWN'); await pg.wait_for_timeout(7000)
    t=await open_('Pictures','fieldcam.html#job'); cam=await cur(pg); await pg.wait_for_timeout(500)
    check('new SA: Pictures instant and for the new SA', t is not None and t<200 and await cam.evaluate("curJob() ? curJob().ref : ''")=='SA-7654321' and await cam.evaluate("curPhotos().length")==0, [t, await cam.evaluate("curJob() && curJob().ref")])
    await back()
    t=await open_('Comments','fieldnotes.html#job'); nt=await cur(pg); await pg.wait_for_timeout(300)
    check('new SA: Comments fresh', await nt.evaluate("STATE.other_notes||''")=='' and await nt.evaluate("STATE.job_plat")=='Fixed Wireless', await nt.evaluate("[STATE.other_notes, STATE.job_plat]"))
    await back()
    # Field Cam on its own stays its own
    h=await cur(pg); await h.locator('#lbBack').click(); await pg.wait_for_timeout(500)
    h=await cur(pg); await h.locator('.tiles a',has_text='Field Cam').first.click(); t=await until(pg,'fieldcam.html')
    solo=await cur(pg); await pg.wait_for_timeout(1500)
    check('Field Cam on its own opens, not in the SA', t is not None and not await solo.evaluate("fkJob()"), t)
    await solo.evaluate("window.__m=5"); await solo.locator('.fk-back').first.click(); await until(pg,'index.html')
    h=await cur(pg); await h.locator('.tiles a',has_text='Field Cam').first.click(); t=await until(pg,'fieldcam.html')
    check('…and again instantly (kept)', t is not None and t<200 and await solo.evaluate("window.__m")==5, t)
    errs=[e for e in errs if 'ViewTransition' not in e]; check('no page errors', not errs, errs)
    print('ALL PASS' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
