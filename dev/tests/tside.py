"""1.20.79: pages no longer swap shared work at load, so two pages can be loaded at once.
Checks Field Cam on its own vs inside an SA, Comments inside an SA, a second page loading alongside, and the one-time migration."""
import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
CAM="""(()=>{const g=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);navigator.mediaDevices.getUserMedia=c=>{if(c&&c.video&&typeof c.video==='object'){const v=Object.assign({},c.video);delete v.facingMode;delete v.deviceId;c=Object.assign({},c,{video:v});}return g(c);};})()"""
U='http://localhost:8765/'
LS=lambda k: f"JSON.parse(localStorage.getItem('{k}')||'null')"
ok=True
def check(name, cond, extra=''):
    global ok; ok = ok and bool(cond); print(('PASS ' if cond else 'FAIL ')+name, extra if not cond else '')
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
    ctx=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,permissions=['camera'])
    await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)"%json.dumps(SEED)); await ctx.add_init_script(CAM)
    pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    # A. Field Cam on its own
    await pg.goto(U+'fieldcam.html'); await pg.wait_for_timeout(3500); await pg.locator('#shutter').click(); await pg.wait_for_timeout(2500)
    solo=await pg.evaluate(LS('fieldcam.current')); check('A solo set started', solo and solo.get('id'))
    # B. SA pictures
    await pg.goto(U+'index.html'); await pg.wait_for_timeout(600); await pg.locator('#jobStart').click(); await pg.wait_for_timeout(300)
    await pg.get_by_role('button',name='Install',exact=True).click(); await pg.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await pg.locator('[data-nj=tech][data-v=FWN]').click(); await pg.locator('#njRef').fill('1234567'); await pg.locator('#njStart').click(); await pg.wait_for_timeout(600)
    await pg.goto(U+'fieldcam.html#job'); await pg.wait_for_timeout(3500); await pg.locator('#shutter').click(); await pg.wait_for_timeout(2500)
    kc=await pg.evaluate(LS('fieldkit.camInJob')); job=await pg.evaluate("localStorage.getItem('fieldkit.activeJob')")
    check('B SA pictures under their own key', kc and kc['owner']==job and kc['cur'] and kc['cur']['id']!=solo['id'], kc)
    check('B solo set untouched while in the SA', await pg.evaluate(LS('fieldcam.current'))==solo)
    check('B no old swap keys', not await pg.evaluate("localStorage.getItem('fieldkit.camOwner')||localStorage.getItem('fieldkit.camStandalone')"))
    # C. a second page loads alongside
    pg2=await ctx.new_page(); await pg2.goto(U+'index.html'); await pg2.wait_for_timeout(800)
    pg3=await ctx.new_page(); await pg3.goto(U+'fieldcam.html'); await pg3.wait_for_timeout(2500)
    check('C SA key unchanged by home + solo Field Cam loading', (await pg.evaluate(LS('fieldkit.camInJob')))['cur']['id']==kc['cur']['id'])
    await pg.bring_to_front(); await pg.locator('#shutter').click(); await pg.wait_for_timeout(2500)
    n=await pg.evaluate("curPhotos().length"); check('C second SA photo lands in the SA', n==2, n)
    check('C solo Field Cam still shows its own set', await pg3.evaluate("current && current.id")==solo['id'])
    await pg3.close()
    await pg.goto(U+'fieldcam.html#job'); await pg.wait_for_timeout(3000)
    check('C reopening Pictures shows the SA photos', await pg.evaluate("curPhotos().length")==2)
    # D. Comments
    await pg.goto(U+'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
    kn=await pg.evaluate(LS('fieldkit.notesInJob')); check('D comments under their own key', kn and kn['owner']==job, kn)
    check('D Field Notes own slot untouched', await pg.evaluate("localStorage.getItem('xplore_fsl_wip_v2')") is None)
    await pg.evaluate("STATE.other_notes='side by side'; wipSaveNow()")
    await pg2.reload(); await pg2.wait_for_timeout(800)
    st=await pg2.evaluate("(JSON.parse(localStorage.getItem('fieldkit.jobs'))[localStorage.getItem('fieldkit.activeJob')].notes.state||{}).other_notes")
    check('D home loading alongside picks up the latest answers', st=='side by side', st)
    await pg.reload(); await pg.wait_for_timeout(1500)
    check('D answers kept after reload', await pg.evaluate("STATE.other_notes")=='side by side')
    await pg2.close()
    # E. migration from a phone updated mid-SA
    await pg.goto(U+'index.html'); await pg.wait_for_timeout(500)
    await pg.evaluate("""(()=>{const j=localStorage.getItem('fieldkit.activeJob');localStorage.setItem('fieldkit.camOwner',j);localStorage.setItem('fieldkit.camStandalone',JSON.stringify({id:'SOLO',sel:[]}));
      localStorage.setItem('fieldcam.current',JSON.stringify({id:'JOBCUR',sel:[]}));localStorage.removeItem('fieldkit.camInJob');
      localStorage.setItem('fieldkit.notesOwner',j);localStorage.setItem('fieldkit.notesStandalone',JSON.stringify({at:Date.now(),state:{x:'solo'}}));localStorage.setItem('xplore_fsl_wip_v2',JSON.stringify({at:Date.now(),state:{x:'job'}}));localStorage.removeItem('fieldkit.notesInJob');})()""")
    await pg.reload(); await pg.wait_for_timeout(600)
    kc=await pg.evaluate(LS('fieldkit.camInJob')); kn=await pg.evaluate(LS('fieldkit.notesInJob'))
    check('E cam migrated', kc['owner']==job and kc['cur']['id']=='JOBCUR' and (await pg.evaluate(LS('fieldcam.current')))['id']=='SOLO', kc)
    check('E notes migrated', kn['owner']==job and kn['state']['x']=='job' and (await pg.evaluate(LS('xplore_fsl_wip_v2')))['state']['x']=='solo', kn)
    check('E old keys gone', not await pg.evaluate("['fieldkit.camOwner','fieldkit.camStandalone','fieldkit.notesOwner','fieldkit.notesStandalone'].some(k=>localStorage.getItem(k))"))
    errs=[e for e in errs if 'ViewTransition' not in e]; check('no page errors', not errs, errs)
    print('ALL PASS' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
