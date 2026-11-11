import json, html
d=json.load(open('codes.json'))
L1=open('/home/claude/namer/l1.b64').read().strip(); L2=open('/home/claude/namer/l2.b64').read().strip()
E=html.escape
ORDER=['5G & fixed wireless','LTE','Wi-Fi & routers','Fiber ONTs','TV','Hughes satellite','SurfBeam satellite']
NICE={'5G & fixed wireless':'5G radios','LTE':'LTE radios','Wi-Fi & routers':'Routers & Wi-Fi','Fiber ONTs':'Fibre ONTs','TV':'XTV boxes','Hughes satellite':'Hughes satellite','SurfBeam satellite':'SurfBeam satellite'}
def card(o, note=None):
    if len(o['skus'])==1: what=f'<h3>{E(o["names"][0])}</h3><p class="pn">{E(o["skus"][0])}</p>'
    elif o['skus']: what=f'<h3>{E(" or ".join(o["names"]))}</h3><p class="pn">{E(" / ".join(o["skus"]))}</p><p class="ask">The app asks which model it is</p>'
    else: what=''
    if note: what=f'<h3>{E(note[0])}</h3><p class="ask">{E(note[1])}</p>'
    return f'<article class="card">{what}<div class="code">{o["svg"]}</div><div class="sn"><span>{E(o["code"])}</span><button type="button" class="copy" data-copy="{E(o["code"])}" aria-label="Copy {E(o["code"])}">Copy</button></div></article>'
secs=''
for g in ORDER:
    its=[o for o in d['items'] if o['group']==g]
    if not its: continue
    secs+=f'<section><h2>{E(NICE[g])}</h2><div class="grid">'+''.join(card(o) for o in its)+'</div></section>'
other=('<section><h2>Should be refused</h2><div class="grid">'+card(d['mac'],('MAC address, not a serial','Scanning this should say it’s the MAC address and ask for the S/N.'))+
  f'<article class="card"><h3>SA number to paste</h3><p class="ask">Copy this, then tap the clipboard in New SA. It should fill in SA-7654321.</p><div class="sn"><span>Service Appointment SA-7654321 for customer</span><button type="button" class="copy" data-copy="Service Appointment SA-7654321 for customer" aria-label="Copy the SA text">Copy</button></div></article>'
  '</div></section>')
page=f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<title>Test serial numbers</title>
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
:root{{--xp-green:#5CBC5D;--xp-dark:#012929;--xp-orange:#FFB21C;--bg:#FFFFFF;--ink:#012929;--muted:#4D6969;--line:#E5E5E5;
  --xp-font:'Poppins','Segoe UI',system-ui,sans-serif;color-scheme:light;box-sizing:border-box;
  padding-top:env(safe-area-inset-top,0px);padding-bottom:env(safe-area-inset-bottom,0px)}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]){{--bg:#012929;--ink:#FFFFFF;--muted:#CEEBCE;--line:#4D6969;color-scheme:dark}}}}
:root[data-theme="dark"]{{--bg:#012929;--ink:#FFFFFF;--muted:#CEEBCE;--line:#4D6969;color-scheme:dark}}
*,*::before,*::after{{box-sizing:inherit}}
body{{margin:0;background:var(--bg);color:var(--ink);font:400 15px/1.45 var(--xp-font)}}
.wrap{{max-width:900px;margin:0 auto;padding:18px 16px 40px}}
.brand{{display:flex;align-items:center;justify-content:space-between;gap:12px}}
h1{{margin:0;font:700 1.4rem/1.15 var(--xp-font);letter-spacing:-.01em}}
.logo{{height:26px;width:auto}}.logo.on-dark{{display:none}}
@media (prefers-color-scheme:dark){{:root:not([data-theme="light"]) .logo.on-light{{display:none}}:root:not([data-theme="light"]) .logo.on-dark{{display:block}}}}
:root[data-theme="dark"] .logo.on-light{{display:none}}:root[data-theme="dark"] .logo.on-dark{{display:block}}
.lede{{margin:8px 0 0;color:var(--muted);font-size:.92rem;max-width:62ch}}
section{{margin-top:28px}}
h2{{margin:0 0 12px;font:700 1.05rem/1.2 var(--xp-font);border-bottom:2px solid var(--xp-green);padding-bottom:6px}}
.grid{{display:grid;grid-template-columns:repeat(auto-fill,minmax(min(100%,300px),1fr));gap:10px}}
.card{{border:1px solid var(--line);border-radius:8px;padding:12px;display:flex;flex-direction:column;gap:8px;min-width:0}}
.card h3{{margin:0;font:600 .95rem/1.3 var(--xp-font)}}
.pn,.ask{{margin:-4px 0 0;color:var(--muted);font-size:.8rem}}
.ask{{margin-top:-2px}}
.code{{background:#FFFFFF;border-radius:6px;padding:10px 6px;margin-top:auto}}
.code svg{{display:block;width:100%;height:64px}}
.sn{{display:flex;align-items:center;gap:8px;justify-content:space-between}}
.sn span{{font-weight:600;letter-spacing:.04em;overflow-wrap:anywhere;min-width:0}}
.copy{{flex:none;height:36px;border:1px solid var(--ink);border-radius:8px;background:transparent;color:var(--ink);font:600 .82rem var(--xp-font);padding:0 12px;cursor:pointer}}
.copy.done{{background:var(--xp-green);border-color:var(--xp-green);color:#012929}}
.copy:focus-visible{{outline:2px solid var(--xp-green);outline-offset:2px}}
.foot{{margin-top:28px;color:var(--muted);font-size:.85rem;border-top:1px solid var(--line);padding-top:12px}}
@media print{{.copy{{display:none}}.card{{break-inside:avoid}}:root{{--bg:#FFFFFF;--ink:#012929;--muted:#4D6969;--line:#E5E5E5}}}}
</style></head><body><main class="wrap">
<div class="brand"><h1>Test serial numbers</h1>
<img class="logo on-light" alt="Xplore" src="data:image/png;base64,{L1}"><img class="logo on-dark" alt="Xplore" src="data:image/png;base64,{L2}"></div>
<p class="lede">Made-up serials in the same format as real stock, two for every item the app recognises by its S/N. Scan them from this screen with another phone, print the page, or tap Copy and paste them into a serial box. Drops, NIDs, mounts, poles and surge protectors have no serials, so they aren’t here.</p>
{secs}{other}
<p class="foot">These serials don’t belong to real equipment. Anything you scan while testing is logged in that phone’s Field Stock, so test on a spare SA-# and remove the entries afterwards.</p>
</main>
<script>
document.addEventListener("click", function (e) {{
  var b = e.target.closest("[data-copy]"); if (!b) return;
  var t = b.getAttribute("data-copy");
  var ok = function () {{ b.textContent = "Copied"; b.classList.add("done"); setTimeout(function () {{ b.textContent = "Copy"; b.classList.remove("done"); }}, 1400); }};
  var fallback = function () {{ var ta = document.createElement("textarea"); ta.value = t; ta.setAttribute("readonly", ""); ta.style.position = "fixed"; ta.style.opacity = "0"; document.body.appendChild(ta); ta.select(); try {{ document.execCommand("copy"); ok(); }} catch (x) {{}} ta.remove(); }};
  try {{ navigator.clipboard.writeText(t).then(ok, fallback); }} catch (x) {{ fallback(); }}
}});
</script></body></html>'''
open('/mnt/user-data/outputs/test-serials.html','w',encoding='utf-8').write(page); print(len(page))
