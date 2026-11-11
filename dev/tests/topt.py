import asyncio, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw, ImageFont
SEED = {"fieldkit.profile": json.dumps({"name":"Curtis Gibbons","email":"c@xplore.ca","phone":"519-555-1234","manager":"a@xplore.ca","dealer":"Cambridge XCI Tech","sap":"123456","sf":"1700123","street":"1 Main St","city":"Cambridge","prov":"ON","postal":"N1R 1A1"}), "fieldkit.setupDone": "1", "techstock.gs": json.dumps({"connected":True})}
B='http://localhost:8765/'
CAM='<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M3 8h4l2-3h6l2 3h4v12H3z"/><circle cx="12" cy="13" r="4"/></svg>'
A_JS = r'''()=>{
 const s=document.createElement('style'); s.textContent=`
 #jobArea .job{min-height:150px!important;height:auto!important;align-items:flex-start!important;padding:20px 18px!important;background:var(--fk-accent,#58C774)!important;color:#06301A!important;border:0!important}
 #jobArea .job i{width:52px!important;height:52px!important;background:#06301A!important;color:#58C774!important}
 #jobArea .job b{font-size:1.45rem!important}
 #jobArea .job span{white-space:normal!important;font-size:.95rem!important;line-height:1.35!important;color:#06301A!important;opacity:.85}
 #jobArea .job .chev{align-self:center;color:#06301A!important}
 .solo{display:flex;justify-content:space-between;align-items:center;width:100%;border:0;background:none;color:var(--muted,#5A6F69);font:600 .95rem var(--f-body,sans-serif);padding:14px 4px;border-top:1px solid var(--line,rgba(0,0,0,.08));border-bottom:1px solid var(--line,rgba(0,0,0,.08));margin-top:14px}
 `; document.head.appendChild(s);
 const sp=document.querySelector('#jobArea .job span'); if(sp) sp.textContent='Photos, comments and equipment in one place. Your stock is logged for you.';
 const sec=document.getElementById('toolsH').parentElement; sec.innerHTML='<button class="solo">Use a tool without an SA<span>›</span></button>';
}'''
B_JS = r'''()=>{
 document.getElementById('toolsH').textContent='Without an SA';
 const s=document.createElement('style'); s.textContent=`
 .scrim{position:fixed;inset:0;background:rgba(0,20,20,.45);z-index:50}
 .sheet2{position:fixed;left:0;right:0;bottom:0;z-index:51;background:var(--surface,#fff);border-radius:18px 18px 0 0;padding:22px 18px 28px;box-shadow:0 -8px 30px rgba(0,0,0,.2);font-family:var(--f-body,sans-serif)}
 .sheet2 h3{margin:0 0 6px;font:700 1.25rem/1.2 var(--f-display,sans-serif);color:var(--fg,#0E2A27)}
 .sheet2 p{margin:0 0 16px;color:var(--muted,#5A6F69);font-size:.95rem;line-height:1.4}
 .sheet2 button{display:block;width:100%;min-height:52px;border:0;border-radius:12px;font:600 1rem var(--f-body,sans-serif);margin-top:8px}
 .sheet2 .p{background:#58C774;color:#06301A}.sheet2 .s{background:var(--surface-2,#E6EDE9);color:var(--fg,#0E2A27)}
 `; document.head.appendChild(s);
 document.body.insertAdjacentHTML('beforeend','<div class="scrim"></div><div class="sheet2"><h3>Is this for a customer job?</h3><p>Start a New SA so the photos, comments and equipment stay together, and your stock is logged for you.</p><button class="p">Start New SA</button><button class="s">Use Field Cam on its own</button></div>');
}'''
C_JS = r'''()=>{
 const s=document.createElement('style'); s.textContent=`
 #jobArea .job{min-height:96px!important;height:auto!important}
 .minitools{display:grid;grid-template-columns:repeat(3,1fr);gap:8px;margin:0}
 .minitools a{display:flex;flex-direction:column;align-items:center;gap:6px;padding:10px 4px;border-radius:12px;background:transparent;border:1px solid var(--line,rgba(0,0,0,.1));color:var(--fg,#0E2A27);font:600 .82rem var(--f-body,sans-serif);text-decoration:none}
 .minitools svg{width:20px;height:20px;color:var(--muted,#5A6F69)}
 `; document.head.appendChild(s);
 const tools=[...document.querySelectorAll('#tools li')].map(li=>({name:li.querySelector('b')?.textContent||'', icon:li.querySelector('svg')?.outerHTML||''}));
 const sec=document.getElementById('toolsH').parentElement;
 const more=document.getElementById('moreH').parentElement;
 sec.remove();
 more.insertAdjacentHTML('afterend','<section><h2 class="eyebrow">Without an SA</h2><div class="minitools">'+tools.map(t=>'<a>'+t.icon+t.name+'</a>').join('')+'</div></section>');
}'''
async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch()
        ctx = await b.new_context(viewport={'width':375,'height':760}, device_scale_factor=2, has_touch=True, is_mobile=True)
        await ctx.add_init_script("(s=>{for(const k in s) if(!localStorage.getItem(k)) localStorage.setItem(k,s[k]);})(%s)" % json.dumps(SEED))
        pg = await ctx.new_page()
        shots=[]
        for name, js in [('now',None),('A',A_JS),('B',B_JS),('C',C_JS)]:
            for _ in range(2):
                await pg.goto(B+'index.html'); await pg.wait_for_timeout(1500)
                if await pg.get_by_text('Start New SA').count(): break
            if js: await pg.evaluate(js)
            await pg.wait_for_timeout(300); await pg.screenshot(path=f'/tmp/opt_{name}.png'); shots.append(name)
        await b.close()
    f=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',40)
    titles={'now':'Today','A':'A · One big button','B':'B · Ask first','C':'C · Tools tucked away'}
    ims=[Image.open(f'/tmp/opt_{n}.png') for n in shots]; w,h=ims[0].size
    o=Image.new('RGB',(w*4+90,h+90),'white'); d=ImageDraw.Draw(o)
    for i,(n,im) in enumerate(zip(shots,ims)):
        x=i*(w+30); o.paste(im,(x,90)); d.text((x+10,22),titles[n],fill='#012929',font=f)
    o.resize((o.width//2,o.height//2)).save('/tmp/fk-shots/sa-first-options.png'); print('ok')
asyncio.run(main())
