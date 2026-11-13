"""1.20.85 iPhone history in the shell: no spare Back entries; each home screen is its own entry, so the swipe back
goes to the screen before (not a copy of the same one)."""
import asyncio, json
exec(open('dev/tests/tshell2.py').read().split('async def main')[0])
async def main():
  async with async_playwright() as p:
    b=await p.chromium.launch(args=['--use-fake-ui-for-media-stream','--use-fake-device-for-media-stream'])
    ctx=await b.new_context(viewport={'width':390,'height':844},is_mobile=True,has_touch=True,permissions=['camera'])
    await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)"%json.dumps(SEED)); await ctx.add_init_script(CAM)
    await ctx.add_init_script("if (/frame\\.html/.test(location.pathname)) window.__fkIOS=1")
    pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto(U+'index.html'); await pg.wait_for_timeout(3000)
    vis=lambda: cur(pg)
    async def view():
      h=await cur(pg); return await h.evaluate("['menu','setup','settings','lobby','newjob','histView'].find(v=>!document.getElementById(v).hidden)")
    L0=await pg.evaluate("history.length")
    h=await cur(pg); await h.locator('.head').first.click(); await pg.wait_for_timeout(200)
    check('a tap adds no spare entry', await pg.evaluate("history.length")==L0, [L0, await pg.evaluate("history.length")])
    await h.locator('#openSettings').click(); await pg.wait_for_timeout(300)
    check('Settings is its own entry', await pg.evaluate("history.length")==L0+1 and 'settings' in pg.url, pg.url)
    await pg.go_back(); await pg.wait_for_timeout(500)
    check('swipe back -> menu', await view()=='menu', await view())
    h=await cur(pg); await h.locator('#openSettings').click(); await pg.wait_for_timeout(300)
    await h.locator('#settings .fk-back, #settings [id$=Back]').first.click(); await pg.wait_for_timeout(500)
    check('‹ in Settings -> menu without growing history', await view()=='menu' and await pg.evaluate("history.length")==L0+1, [await view(), await pg.evaluate("history.length")])
    # SA: New SA -> Start SA replaces it
    await h.locator('#jobStart').click(); await pg.wait_for_timeout(300)
    await h.get_by_role('button',name='Install',exact=True).click(); await h.locator('[data-nj=fam][data-v="Fixed Wireless"]').click(); await h.locator('[data-nj=tech][data-v=FWN]').click(); await h.locator('#njRef').fill('1234567'); await h.locator('#njStart').click(); await pg.wait_for_timeout(500)
    check('SA page shown', await view()=='lobby', await view())
    await h.locator('#lobby button, #lobby a').filter(has_text='Pictures').first.click(); await until(pg,'fieldcam.html#job'); await pg.wait_for_timeout(800)
    await pg.go_back(); t=await until(pg,'index.html#job')
    check('swipe back from Pictures -> SA page', t is not None and await view()=='lobby', [await curpage(pg), await view()])
    await pg.go_back(); await pg.wait_for_timeout(500)
    check('swipe back from SA page -> menu (not New SA)', await view()=='menu', await view())
    errs=[e for e in errs if 'ViewTransition' not in e]; check('no page errors', not errs, errs)
    print('ALL PASS' if ok else 'SOME FAILED'); await b.close()
asyncio.run(main())
