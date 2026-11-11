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
        await pg.get_by_text('Start New Job').first.click(); await pg.wait_for_timeout(500)
        await pg.locator('#njRef').fill('1234567'); await pg.get_by_role('button', name='Install').click(); await pg.get_by_role('button', name='Fixed Wireless').click()
        await pg.get_by_role('button', name='Start Job').click(); print('B cam  ', await where(pg))
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
        print('errors', errs); await b.close()
asyncio.run(main())
