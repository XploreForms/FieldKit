import asyncio, json
from playwright.async_api import async_playwright
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"curtis.gibbons@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1","shipHold":"","shipNotes":""}),
        "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
async def where(pg):
    await pg.wait_for_timeout(1200)
    u = pg.url.replace(B,'')
    view = await pg.evaluate("()=>{const v=['menu','lobby','newjob'].filter(id=>{const e=document.getElementById(id);return e&&!e.hidden});return v.join(',')}")
    return f"{u} [{view}] hist={await pg.evaluate('history.length')}"
async def tap(pg):  # a harmless tap to arm the Back guard
    await pg.mouse.click(200, 400 if 'fieldnotes' in pg.url else 120); await pg.wait_for_timeout(200)
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':390,'height':844}, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page(); errs=[]; pg.on('pageerror', lambda e: errs.append(str(e)))
        await pg.goto(B+'index.html'); print('A start', await where(pg))
        await pg.locator('a,button').filter(has_text='Field Cam').first.click(); print('A cam  ', await where(pg))
        await tap(pg); await pg.go_back(); print('A back ', await where(pg))
        await pg.locator('a,button').filter(has_text='Field Notes').first.click(); print('E notes', await where(pg))
        await tap(pg); await pg.go_back(); print('E back ', await where(pg))
        await pg.get_by_text('Start New SA').first.click(); await pg.wait_for_timeout(500)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click(); await pg.locator('#newjob [data-nj=tech]').first.click()
        await pg.get_by_role('button', name='Start SA').click(); print('B cam  ', await where(pg))
        await tap(pg); await pg.go_back(); print('B back ', await where(pg))
        await pg.goto(B+'index.html#job') if False else None
        # lobby -> cam again, then cam hands over to notes (as after saving photos), then Back
        await pg.evaluate("location.href='fieldcam.html#job'"); print('D cam  ', await where(pg))
        await pg.evaluate("location.replace('fieldnotes.html#job')"); print('D notes', await where(pg))
        await tap(pg); await pg.go_back(); print('D back ', await where(pg))
        # on-screen link from notes in a job
        await pg.evaluate("location.href='fieldnotes.html#job'"); await where(pg)
        await pg.locator('a.fk-back').first.click(); print('F link ', await where(pg))
        # no tap first (guard not armed): natural Back
        await pg.evaluate("location.href='fieldcam.html#job'"); await where(pg)
        await pg.go_back(); print('G back*', await where(pg))
        # menu: unfinished SA card goes to the SA home even when the SA was last in Field Notes
        await pg.evaluate("location.href='fieldnotes.html#job'"); await where(pg)
        await pg.goto(B+'index.html'); await pg.wait_for_timeout(800)
        print('H card text', (await pg.locator('#jobGo').inner_text()).replace('\n',' | '))
        await pg.locator('#jobGo').click(); print('H card ', await where(pg))
        # cam -> 'Go to Field Notes' style link -> notes -> Back
        await pg.evaluate("location.href='fieldcam.html#job'"); await where(pg)
        await pg.evaluate("const a=document.createElement('a');a.href='fieldnotes.html#job';a.textContent='x';document.body.appendChild(a);a.click()"); print('I notes', await where(pg))
        await tap(pg); await pg.go_back(); print('I back ', await where(pg))
        # iPhone-style: Field Cam -> Field Notes kept in history (push, not replace), then comments copied
        await pg.evaluate("location.href='fieldcam.html#job'"); await where(pg)
        await pg.evaluate("location.href='fieldnotes.html#job'"); print('J notes', await where(pg))
        await tap(pg); await pg.evaluate("FieldKit.goHome()"); print('J copied ->', await where(pg))
        # SA START card time
        await pg.evaluate("location.href='fieldcam.html#job'"); await where(pg)
        r = await pg.evaluate('''async()=>{ const jobs=JSON.parse(localStorage.getItem('fieldcam.jobs')); const id=Object.keys(jobs).pop();
            jobs[id].started=new Date(2026,10,8,9,5).getTime(); localStorage.setItem('fieldcam.jobs',JSON.stringify(jobs));
            return id; }''')
        await pg.reload(); await pg.wait_for_timeout(1500)
        r = await pg.evaluate('''async()=>{ const id=Object.keys(jobs).pop(); S.photos.push({id:'p1',sessionId:id,created:new Date(2026,10,8,10,40).getTime(),job:jobs[id]});
            const f=await makeDivider(id,'start'); const g=await makeDivider(id,'end'); return [jobs[id].started, f&&f.name, g&&g.name]; }''')
        print('cards', r)
        print('errors', [e for e in errs if 'ViewTransition' not in e]); await b.close()
asyncio.run(main())
