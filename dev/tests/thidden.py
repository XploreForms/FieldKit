"""1.20.80: a page loaded in the background (frame marked data-fk-hidden="1") does nothing "on arrival" until the shell shows it."""
import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"approver@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
CAM="""(()=>{const g=navigator.mediaDevices.getUserMedia.bind(navigator.mediaDevices);window.__gum=0;navigator.mediaDevices.getUserMedia=c=>{window.__gum++;if(c&&c.video&&typeof c.video==='object'){const v=Object.assign({},c.video);delete v.facingMode;delete v.deviceId;c=Object.assign({},c,{video:v});}return g(c);};})()"""
U='http://localhost:8765/'
ok=True
def check(name, cond, extra=''):
    global ok; ok = ok and bool(cond); print(('PASS ' if cond else 'FAIL ')+name, extra if not cond else '')
ADD="""(u)=>new Promise(r=>{const f=document.createElement('iframe');f.setAttribute('data-fk-hidden','1');f.id='bg'+document.querySelectorAll('iframe').length;f.allow='camera';f.style.cssText='position:fixed;left:0;top:0;width:390px;height:844px;visibility:hidden';f.onload=()=>r(f.id);f.src=u;document.body.appendChild(f)})"""
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
    ctx=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,permissions=['camera'])
    await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)"%json.dumps(SEED)); await ctx.add_init_script(CAM)
    pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(U+'index.html'); await pg.wait_for_timeout(600); await pg.locator('#jobStart').click(); await pg.wait_for_timeout(300)
    await pg.get_by_role('button',name='Install',exact=True).click(); await pg.locator('[data-nj=pt][data-v=FWN]').click(); await pg.locator('#njRef').fill('1234567'); await pg.locator('#njStart').click(); await pg.wait_for_timeout(600)
    before=await pg.evaluate("[localStorage.getItem('fieldcam.jobs'),localStorage.getItem('fieldcam.current')]")
    # Field Cam on its own, in the background
    fid=await pg.evaluate(ADD,'fieldcam.html'); await pg.wait_for_timeout(3000)
    fr=[f for f in pg.frames if f.url.endswith('fieldcam.html')][0]
    check('cam hidden: camera not asked for', await fr.evaluate("window.__gum")==0)
    check('cam hidden: not started', not await fr.evaluate("S.started"))
    check('cam hidden: no new set of photos saved', await pg.evaluate("[localStorage.getItem('fieldcam.jobs'),localStorage.getItem('fieldcam.current')]")==before)
    check('cam hidden: reports not shown', await fr.evaluate("FieldKit.shown()")==False)
    await fr.evaluate("FieldKit._host(true)"); await pg.wait_for_timeout(2500)
    check('cam shown: camera started', await fr.evaluate("S.started && !!document.getElementById('video').srcObject"))
    await fr.evaluate("FieldKit._host(false)"); await pg.wait_for_timeout(300)
    check('cam hidden again: paused', await fr.evaluate("S.paused")==True)
    await fr.evaluate("FieldKit._host(true)"); await pg.wait_for_timeout(500)
    check('cam shown again: running', await fr.evaluate("S.paused")==False)
    await fr.evaluate("FieldKit._host(false)")
    # Comments inside the SA, in the background
    step=lambda: pg.evaluate("JSON.parse(localStorage.getItem('fieldkit.jobs'))[localStorage.getItem('fieldkit.activeJob')].step")
    s0=await step()
    await pg.evaluate(ADD,'fieldnotes.html#job'); await pg.wait_for_timeout(1500)
    fn=[f for f in pg.frames if 'fieldnotes.html' in f.url][0]
    check('notes hidden: SA step not moved on', await step()==s0=='cam', await step())
    await fn.evaluate("FieldKit._host(true)"); await pg.wait_for_timeout(200)
    check('notes shown: SA step is notes', await step()=='notes', await step())
    await fn.evaluate("STATE.other_notes='typed then hidden'; FieldKit._host(false)"); await pg.wait_for_timeout(200)
    st=await pg.evaluate("(JSON.parse(localStorage.getItem('fieldkit.jobs'))[localStorage.getItem('fieldkit.activeJob')].notes.state||{}).other_notes")
    check('notes hidden by shell: answers saved to the SA', st=='typed then hidden', st)
    # one way to change page
    await fn.evaluate("window.__n=[]; window.__fkNav=(u,r)=>window.__n.push([u,r]); FieldKit.go('index.html#job', true)")
    check('FieldKit.go hands over to the shell', await fn.evaluate("JSON.stringify(window.__n)")=='[["index.html#job",true]]')
    errs=[e for e in errs if 'ViewTransition' not in e]; check('no page errors', not errs, errs)
    print('ALL PASS' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
