"""Build Toolkit's tool pages from the current Field Cam, Stock Tracker and FSL Comments Generator.
Each tool stays its own file and can keep being developed separately; this script applies the
small Toolkit hooks (shared bridge, Home/Comments buttons, serial -> Stock deployment) on top.
Usage: python3 build.py <fieldcam.html> <stocktracker.html> <fslcomments.html>"""
import sys, re, pathlib

OUT = pathlib.Path(__file__).parent
fc_src, st_src, cm_src = (pathlib.Path(p).read_text(encoding="utf-8") for p in sys.argv[1:4])


def sub(text, old, new, count=1):
    if text.count(old) < 1:
        raise SystemExit(f"patch target not found: {old[:80]!r}")
    return text.replace(old, new, count)


HOME_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/></svg>'
NOTE_SVG = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 4h16v12H8l-4 4z"/><path d="M8 9h8M8 12h5"/></svg>'

# ------------------------------------------------------------------ Camera (Field Cam)
fc = fc_src
fc = sub(fc, "<body>", '<body>\n<script src="toolkit.js" data-app="camera"></script>')
fc = sub(fc, "<title>Field Cam</title>", "<title>Field Kit Camera</title>")
fc = sub(fc, '<meta name="apple-mobile-web-app-title" content="Field Cam">', '<meta name="apple-mobile-web-app-title" content="Field Kit">')
fc = sub(fc, '<button class="pill jobpill" id="jobBtn"',
         f'<a class="iconbtn" id="tkHome" href="index.html" aria-label="Field Kit home">{HOME_SVG}</a>\n    <button class="pill jobpill" id="jobBtn"')
fc = sub(fc, '<button class="iconbtn" id="setBtn"',
         f'<a class="iconbtn" id="tkNotes" href="comments.html" aria-label="Write completion comments">{NOTE_SVG}</a>\n    <button class="iconbtn" id="setBtn"')
fc = sub(fc, '<div class="brandrow">', '<a class="tkback" href="index.html">‹ Field Kit</a>\n    <div class="brandrow">')
fc = sub(fc, ".brandrow{display:flex;align-items:center;gap:14px}",
         ".brandrow{display:flex;align-items:center;gap:14px}\n.tkback{justify-self:start;color:var(--accent);font-weight:600;text-decoration:none;padding:6px 0;font-size:15px}\na.iconbtn{text-decoration:none}")
# scanned serial: work out the model, then it goes on the job (and from there into Stock)
fc = sub(fc, """  const item = snItem(code);
  j.serials = [...(j.serials || []), { code, item }]; jobChanged();
  aimFlash("hit"); try { navigator.vibrate && navigator.vibrate(40); } catch {}
  scanMsg(`Added <b>${esc(code)}</b>${item ? " · " + esc(item) : ""}. Scan another or tap Done`);""",
"""  let item = snItem(code), sku = null, note = "";
  aimFlash("hit"); try { navigator.vibrate && navigator.vibrate(40); } catch {}
  if (window.Toolkit) {
    const ms = Toolkit.modelsFor(code);
    sku = ms.length === 1 ? ms[0] : await Toolkit.pickModel(code, ms);
    if (sku && !item) item = Toolkit.modelName(sku);
    note = Toolkit.stockNote(code, j.ref);
  }
  j.serials = [...(j.serials || []), { code, item, sku }]; jobChanged();
  const logged = sku && (!j.outcome || j.outcome === "OK");
  scanMsg(`Added <b>${esc(code)}</b>${item ? " · " + esc(item) : ""}${window.Toolkit ? `<br><small>${logged ? "Logged in Stock as deployed on " + esc(j.ref) : "Not logged in Stock"} · ${esc(note)}</small>` : ""}`);""")
# serial list shows whether each one is in Stock, and lets the tech pick a model later
fc = sub(fc, """<span>${esc(x.item || "Item not recognised")}${j.outcome && j.outcome !== "OK" ? " · not stamped (job isn’t Complete)" : ""}</span></div><button class="btn sm danger" data-sndel="${i}">Remove</button></div>`""",
"""<span>${esc(x.item || "Item not recognised")}${j.outcome && j.outcome !== "OK" ? " · not stamped (job isn’t Complete)" : ""}${window.Toolkit ? (x.sku ? (j.outcome && j.outcome !== "OK" ? " · not in Stock" : " · deployed in Stock") : " · not in Stock") : ""}</span></div>${window.Toolkit && !x.sku ? `<button class="btn sm" data-snpick="${i}">Pick Model</button>` : ""}<button class="btn sm danger" data-sndel="${i}">Remove</button></div>`""")
fc = sub(fc, """  const b = e.target.closest("[data-sndel]"); if (!b) return;""",
"""  const pk = e.target.closest("[data-snpick]");
  if (pk && window.Toolkit) {
    const j = curJob(), x = j && j.serials && j.serials[+pk.dataset.snpick]; if (!x) return;
    Toolkit.pickModel(x.code, Toolkit.modelsFor(x.code)).then(sku => { if (!sku) return; x.sku = sku; if (!x.item) x.item = Toolkit.modelName(sku); jobChanged(); renderSerials(); });
    return;
  }
  const b = e.target.closest("[data-sndel]"); if (!b) return;""")
# every save keeps Stock and Home/Comments in step with the job
fc = sub(fc, 'function save() { store("fieldcam.settings", settings); store("fieldcam.jobs", jobs); store("fieldcam.current", current); }',
'''function save() { store("fieldcam.settings", settings); store("fieldcam.jobs", jobs); store("fieldcam.current", current); tkSync(); }
/* Toolkit: deploy this job's serials in Stock, and publish the job for Home and Comments */
function tkSync() {
  if (!window.Toolkit) return;
  try {
    const j = curJob();
    if (!j) { Toolkit.publishJob(null); return; }
    const r = Toolkit.syncDeploys(current.id, j, typeof S !== "undefined" ? S.pos : null);
    if (r.failed) toast("Couldn’t log the deployment in Stock: this phone’s storage is full.", 4000);
    tkPublish();
  } catch (e) {}
}
function tkPublish() {
  if (!window.Toolkit) return;
  try {
    const j = curJob(); if (!j) { Toolkit.publishJob(null); return; }
    const ps = curPhotos(), labels = countLabels(), req = baseShots(j);
    Toolkit.publishJob(current.id, j, { title: jobTitle(j), photos: ps.length, labels, missing: req.filter(l => !labels[l]) });
  } catch (e) {}
}''')
fc = sub(fc, "function renderAll() { prepDividers();", "function renderAll() { tkPublish(); prepDividers();")
fc = sub(fc, "fetch(`index.html?check=${Date.now()}`", "fetch(`camera.html?check=${Date.now()}`")
(OUT / "camera.html").write_text(fc, encoding="utf-8")

# ------------------------------------------------------------------ Stock (Stock Tracker)
st = st_src
st = sub(st, "<body>", '<body>\n<script src="toolkit.js" data-app="stock"></script>')
st = sub(st, "<title>Stock Tracker</title>", "<title>Field Kit Stock</title>")
st = sub(st, '<meta name="apple-mobile-web-app-title" content="Stock Tracker">', '<meta name="apple-mobile-web-app-title" content="Field Kit">')
st = sub(st, '<div class="top-in">\n    <div class="mark" aria-hidden="true">',
         f'<div class="top-in">\n    <a class="mark tkhome" href="index.html" aria-label="Field Kit home">{HOME_SVG}</a>\n    <div class="mark" hidden aria-hidden="true">')
st = sub(st, ".mark svg{width:20px;height:20px}", ".mark svg{width:20px;height:20px}\n.tkhome{text-decoration:none}")
# entries logged from Camera carry their note; label them in the history so a tech knows where they came from
(OUT / "stock.html").write_text(st, encoding="utf-8")

# ------------------------------------------------------------------ Comments (FSL Comments Generator)
cm = cm_src
# the published copy is wrapped twice: keep only the real document
start = cm.index("<!DOCTYPE html>")
cm = cm[start:]
cm = cm[: cm.rindex("</html>", 0, cm.rindex("</html>")) + len("</html>")]
cm = sub(cm, '<meta charset="UTF-8">', '<meta charset="UTF-8">\n<script src="toolkit.js" data-app="comments"></script>\n<meta name="apple-mobile-web-app-capable" content="yes">\n<meta name="apple-mobile-web-app-title" content="Field Kit">')
cm = sub(cm, "<title>FSL Comments Generator</title>", "<title>Field Kit Comments</title>")
JOBBAR = """
<style>
.tkbar{position:sticky;top:0;z-index:50;background:#002B2B;color:#EAF2EE;padding:calc(env(safe-area-inset-top,0px) + 8px) max(14px,env(safe-area-inset-right,0px)) 8px max(14px,env(safe-area-inset-left,0px));display:flex;align-items:center;gap:10px;font:14px/1.3 -apple-system,BlinkMacSystemFont,system-ui,sans-serif}
.tkbar a{color:#58C774;text-decoration:none;font-weight:600;white-space:nowrap;padding:6px 0}
.tkbar .tkjob{flex:1;min-width:0;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.tkbar .tkjob b{font-family:ui-monospace,Menlo,monospace;margin-right:6px}
.tkwarn{background:#F2B84B;color:#2A1A00;padding:8px max(14px,env(safe-area-inset-right,0px)) 8px max(14px,env(safe-area-inset-left,0px));font:13.5px/1.35 -apple-system,BlinkMacSystemFont,system-ui,sans-serif}
</style>
<div class="tkbar" id="tkBar"><a href="index.html">‹ Field Kit</a><span class="tkjob" id="tkJob">No job open</span><a href="camera.html" id="tkCam">Camera</a></div>
<div class="tkwarn" id="tkWarn" hidden></div>
<script>
(function () {
  var T = window.Toolkit, j = T && T.currentJob();
  var job = document.getElementById("tkJob"), w = document.getElementById("tkWarn");
  if (!T) return;
  if (j) job.innerHTML = "<b>" + T.esc(j.ref || "No SA-#") + "</b>" + T.esc(j.title || "");
  else document.getElementById("tkCam").textContent = "Start a Job";
  if (j && !T.commentsFit(j)) {
    w.textContent = "Comments are only built for " + T.commentTypes.map(function (t) { return t.name; }).join(", ") + " so far. This job is " + (j.title || "a different type") + ", so check every answer before pasting into FSL.";
    w.hidden = false;
  }
})();
</script>
"""
cm = re.sub(r"(<body[^>]*>)", lambda m: m.group(1) + JOBBAR, cm, count=1)
(OUT / "comments.html").write_text(cm, encoding="utf-8")
print("built camera.html, stock.html, comments.html")
