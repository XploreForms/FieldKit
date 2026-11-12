/* Field Kit jobs: the guided "Start New Job" flow.
   A job runs Field Cam (SA-#, job type, platform, photos, scanned equipment), then Field Notes (prefilled),
   then the job summary on the menu (photos, comments, deployed equipment, Complete Job).
   A job stays open until Complete Job, and every job is kept in Job history for 7 days.

   Tools know they're part of a job when their address ends in #job (fieldcam.html#job, fieldnotes.html#job).
   Each tool keeps working on its own data; this file swaps the job's work in and out around it:
     - Field Cam: which Field Cam job is open (fieldcam.current)
     - Field Notes: the comment form (xplore_fsl_wip_v2)
   so a job never mixes with work done in a tool on its own (one-time use).
   Equipment scanned in Field Cam during a job is logged in Field Stock as deployed on the job's SA-#,
   sealed the same way Field Stock seals its own entries, so its History Check stays verified.

   Load after fieldkit-catalog.js and fieldkit.js, before the tool's own scripts. */
(function () {
  "use strict";
  var FK = window.FieldKit; if (!FK) return;
  var APP = FK.app;
  function get(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  function raw(k) { try { return localStorage.getItem(k) || ""; } catch (e) { return ""; } }
  function setRaw(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function del(k) { try { localStorage.removeItem(k); } catch (e) {} }
  var keyOf = function (s) { return String(s || "").replace(/\s+/g, "").toUpperCase(); };
  var esc = function (s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); };

  var K = { jobs: "fieldkit.jobs", active: "fieldkit.activeJob", camOwner: "fieldkit.camOwner", camSolo: "fieldkit.camStandalone",
            notesOwner: "fieldkit.notesOwner", notesSolo: "fieldkit.notesStandalone" };
  var WEEK = 7 * 864e5, WIP = "xplore_fsl_wip_v2";

  /* ---------- job store ---------- */
  function all() { return get(K.jobs, {}) || {}; }
  function save(job) { var a = all(); job.updated = Date.now(); a[job.id] = job; set(K.jobs, a); return job; }
  function byId(id) { return all()[id] || null; }
  function active() { var id = raw(K.active); var j = id && byId(id); return j || null; }
  function setActive(id) { if (id) setRaw(K.active, id); else del(K.active); }
  function start() {
    var job = { id: "j" + Date.now().toString(36) + Math.random().toString(36).slice(2, 6), created: Date.now(), status: "active", step: "cam",
      sa: "", work: "", plat: "", outcome: "", reason: "", title: "", camJobId: "", camJobIds: [], photos: 0, unsaved: 0, labels: {}, serials: [],
      notes: { state: null, comment: "", copiedAt: 0, ticked: [] } };
    save(job); setActive(job.id); return job;
  }
  function list() { var a = all(); return Object.keys(a).map(function (k) { return a[k]; }).sort(function (x, y) { return y.created - x.created; }); }
  function complete(id) { var j = byId(id); if (!j) return; j.status = "complete"; j.completedAt = Date.now(); j.step = "lobby"; save(j); if (raw(K.active) === id) setActive(null); }
  function open(id) { var j = byId(id); if (j) setActive(id); return j; }
  // Job history keeps 7 days; the job that's open is never removed
  (function purge() {
    var a = all(), act = raw(K.active), changed = false, now = Date.now();
    Object.keys(a).forEach(function (k) { if (k !== act && now - (a[k].updated || a[k].created) > WEEK) { delete a[k]; changed = true; } });
    if (changed) set(K.jobs, a);
  })();

  var jobMode = /^#job\b/.test(location.hash) && !!active();

  /* ---------- Field Cam's work swapped in and out ---------- */
  /* Every page that isn't a tool inside a job puts the one-time-use work back first, so the menu and the
     tools on their own always see their own work and never the job's. */
  var camInJob = jobMode && APP === "cam", notesInJob = jobMode && APP === "notes";
  var camOwner = raw(K.camOwner);
  if (camOwner && (!camInJob || camOwner !== active().id)) {
    set("fieldcam.current", get(K.camSolo, null)); del(K.camSolo); setRaw(K.camOwner, ""); camOwner = "";
  }
  if (camInJob && !camOwner) {
    var cj = active(), camJobs = get("fieldcam.jobs", {}) || {};
    set(K.camSolo, get("fieldcam.current", null));   // one-time-use Field Cam work, put back later
    set("fieldcam.current", cj.camJobId && camJobs[cj.camJobId] ? { id: cj.camJobId, sel: [] } : null);
    setRaw(K.camOwner, cj.id);
  }

  /* ---------- equipment slots: what each install usually deploys ----------
     Install and Conversion jobs get a slot for each piece of equipment their platform normally uses.
     Choice slots (mount, NID, drop...) are picked; serial slots are filled by scanning. A scanned serial goes in the
     first slot that takes its item; anything else is listed as other equipment. XWH and XTV get one slot per unit (none at all until Field Notes says some were installed or one is scanned)
     Field Notes says was installed. Repairs, recoveries and VAS jobs have no slots (scan freely). */
  var SLOT_CACHE = null;
  function slotSet() {
    if (SLOT_CACHE) return SLOT_CACHE;
    var C = window.FK_CATALOG || { SKUS: [] };
    var inGroup = function () { var g = [].slice.call(arguments); return C.SKUS.filter(function (x) { return g.indexOf(x.group) >= 0 && x.serial && !x.hidden; }).map(function (x) { return x.id; }); };
    var DROPS = [["Not Needed", []], ["100m", ["00D101EB49R100MP"]], ["200m", ["00D101EB49R200MP"]], ["300m", ["00D101EB49R300MP"]], ["500m", ["00D101EB49R500MP"]], ["750m", ["00D101EB49R750MP"]], ["1000m", ["FK-DROP1000"]]];
    SLOT_CACHE = {
      /* Mount (for stock levels): the mount type, a "Deployed 10ft pole" tick for Gable Mount and Tripod, and an
         opt-out tick when no new mount went up (reused existing, or on a tower). Stored as one value:
         "J-Arm", "Gable Mount" / "Gable Mount + 10ft Pole", "Bipod", "Tripod" / "Tripod + 10ft Pole", or "No new mount".
         Bipod still logs its 5ft pole, as before. */
      mount: { name: "Mount", ui: "mount", types: ["J-Arm", "Gable Mount", "Bipod", "Tripod"], poles: ["Gable Mount", "Tripod"], none: "No new mount",
        opts: [["J-Arm", ["PVJM-39"]], ["Gable Mount", ["FK-GABLE"]], ["Gable Mount + 10ft Pole", ["FK-GABLE", "FK-POLE10"]], ["Bipod", ["FK-BIPOD", "FK-POLE5"]],
          ["Tripod", ["FK-TRIPOD"]], ["Tripod + 10ft Pole", ["FK-TRIPOD", "FK-POLE10"]], ["No new mount", []]] },
      surge: { name: "Surge", opts: [["Deployed", ["PVFWSURGE"]]], def: "Deployed" },
      nid: { name: "NID", opts: [["Deployed", ["FTH602A010XP"]], ["Not Needed", []]] },
      drop: { name: "Drop", opts: DROPS },
      trimast: { name: "Trimast", opts: [["Deployed", ["1140662"]], ["Reused existing", []], ["Pole mount", ["FK-SATPOLE"]]] },
      azel: { name: "AzEl", opts: [["Deployed", ["1172770"]], ["Reused existing", []]] },
      dish: { name: "Dish", opts: [["Deployed", ["1172769-004"]], ["Reused existing", []]] },
      radio: { name: "Radio", skus: inGroup("5G & fixed wireless", "LTE") },
      ont: { name: "ONT", skus: inGroup("Fibre ONTs") },
      router: { name: "Router", skus: ["854-V6", "ARIA3321V-XPL", "EMG6726-B10A-MT"] },
      modem: { name: "Modem", skus: ["RM4100N-043"] },
      tria: { name: "TRIA", skus: ["X01012000A001"] },
      xwh: { name: "XWH", skus: ["834-V6", "WAP6804-MT"], multi: "xwh" },
      xtv: { name: "XTV", skus: ["EVOFORCE1", "9988030065MFG"], multi: "tv" }
    };
    return SLOT_CACHE;
  }
  function slotIds(src) {
    if (!src || (src.work !== "INS" && src.work !== "CON" && src.work !== "REP")) return [];
    var p = src.plat || "";
    if (p === "Fibre") return ["drop", "nid", "ont", "router", "xwh", "xtv"];   // repairs: Fibre has no drop type, so every fibre slot
    if (p === "Fixed Wireless") return ["mount", "surge", "radio", "router", "xwh", "xtv"];
    if (p === "Fibre (Existing Drop)") return ["nid", "ont", "router", "xwh", "xtv"];
    if (p === "Fibre (Drop Required)" || p === "Fibre (Drop Only)") return ["drop", "nid", "ont", "router", "xwh", "xtv"];
    if (p === "Satellite") return ["trimast", "azel", "dish", "modem", "tria"];
    return [];
  }
  // conversions and repairs can also recover equipment from the customer
  function canRecover(src) { return !!src && (src.work === "CON" || src.work === "REP"); }
  function unitsWanted(ns, key) { if (!ns || ns[key] == null || ns[key] === "") return null; return ns[key] === "None" ? 0 : (parseInt(ns[key], 10) || 0); }
  // src: {work, plat, serials, slots}; ns: Field Notes answers (for how many XWH / XTV)
  function slotModel(src, ns) {
    // Cannot Complete / Not Required: nothing is deployed, so no slots (scanned serials are kept in case it changes back)
    if (src && src.outcome && src.outcome !== "OK") return { rows: [], extras: [], total: 0, done: 0, has: false, off: true };
    var D = slotSet(), ids = slotIds(src), picks = (src && src.slots) || {}, got = {}, extras = [], rows = [], recovered = [];
    var maybe = !!src && src.work === "REP";   // repairs: same slots, but deploying anything is the exception, so nothing is required
    ids.forEach(function (id) { got[id] = []; });
    ((src && src.serials) || []).forEach(function (s) {
      if (s.rec) { recovered.push(s); return; }
      var to = null;
      if (s.sku) for (var i = 0; i < ids.length; i++) { var d = D[ids[i]]; if (d.skus && d.skus.indexOf(s.sku) >= 0 && (d.multi || !got[ids[i]].length)) { to = ids[i]; break; } }
      if (to) got[to].push(s); else extras.push(s);
    });
    ids.forEach(function (id) {
      var d = D[id];
      if (d.opts) {
        var opts = d.opts.map(function (o) { return o[0]; }), def = maybe ? "" : (d.def || "");
        if (maybe && !d.ui && opts.indexOf("Not Needed") < 0) opts = opts.concat(["Not Needed"]);   // Surge on a repair isn't a given
        var v = picks[id] || def;
        if (d.ui === "mount") v = MOUNT_OLD[v] || v;
        v = ({ Yes: "Deployed", No: "Not Needed", "J-arm": "J-Arm", "Bi-pod": "Bipod + 5ft Pole", "Gable mount + 10ft pole": "Gable Mount + 10ft Pole", "Tripod + 10ft pole": "Tripod + 10ft Pole" })[v] || v;   // answers saved before the wording changed
        if (v && opts.indexOf(v) < 0) v = def;
        rows.push({ id: id, kind: "choice", ui: d.ui || "", name: d.name, opts: opts, value: v, done: !!v, optional: maybe }); return;
      }
      if (!d.multi) { rows.push({ id: id, kind: "serial", name: d.name, item: got[id][0] || null, done: !!got[id][0], optional: maybe, hint: maybe && !got[id][0] ? "If deployed" : "" }); return; }
      var want = unitsWanted(ns, d.multi), have = got[id], n = Math.max(want || 0, have.length);
      for (var k = 0; k < n; k++) rows.push({ id: id, kind: "serial", name: n > 1 ? d.name + " " + (k + 1) : d.name, item: have[k] || null, done: !!have[k], optional: maybe });
      // nothing scanned and Field Notes hasn't said any were installed: no XWH / XTV slot at all
    });
    var need = rows.filter(function (r) { return !r.optional; });
    return { rows: rows, extras: extras, recovered: recovered, canRecover: canRecover(src), total: need.length, done: need.filter(function (r) { return r.done; }).length,
      deployedCount: rows.filter(function (r) { return r.kind === "serial" ? !!r.item : r.value && r.value !== "Not Needed" && r.value !== "Reused existing" && r.value !== "No new mount"; }).length + extras.length, has: ids.length > 0 };
  }
  // mount answers saved before the mount slot changed (and Field Notes' Mount Type names)
  var MOUNT_OLD = { "J-arm": "J-Arm", "J-Arm + Side Stays": "J-Arm", "Bi-pod": "Bipod", "Bipod + 5ft Pole": "Bipod", "Gable mount + 10ft pole": "Gable Mount + 10ft Pole",
    "Tripod + 10ft pole": "Tripod + 10ft Pole", "Tower": "No new mount", "Tower Leg": "No new mount", "Not Needed": "No new mount", "No": "No new mount" };
  // the items a job's choice slots deploy: [{slot, sku}]
  function slotItems(src) {
    var D = slotSet(), out = [];
    slotModel(src, null).rows.forEach(function (r) {
      if (r.kind !== "choice" || !r.value) return;
      var o = D[r.id].opts.filter(function (x) { return x[0] === r.value; })[0];
      (o ? o[1] : []).forEach(function (sku) { out.push({ slot: r.id, sku: sku }); });
    });
    return out;
  }
  /* A serial typed or pasted into a slot. Resolves to {code, sku, item} or {error}. The slot narrows which item it is;
     it asks only when the slot takes more than one item and the serial doesn't say which. */
  function slotEntry(src, slotId, text) {
    var code = keyOf(text).replace(/^(S\/?N|SN)[:#]?/, "");
    if (code.length < 5) return Promise.resolve({ error: "That serial number looks too short." });
    if (((src && src.serials) || []).some(function (x) { return keyOf(x.code) === code; })) return Promise.resolve({ error: code + " is already on this SA." });
    var rec = slotId === "__rec", d = slotSet()[slotId], skus = (d && d.skus) || [];
    var all = modelsFor(code), fits = rec ? all : all.filter(function (id) { return skus.indexOf(id) >= 0; }), cand = rec ? fits : (fits.length ? fits : skus);
    var pick = cand.length === 1 ? Promise.resolve(cand[0]) : pickModel(code, cand);
    return pick.then(function (sku) { var r = { code: code, sku: sku || "", item: sku && SKU[sku] ? SKU[sku].name : "" }; if (rec) r.rec = true; return r; });
  }
  /* Paste button: puts what's on the clipboard in the box. Typed serials go in when the tech taps Done / away. */
  function pasteInto(inp) {
    if (!navigator.clipboard || !navigator.clipboard.readText) { inp.focus(); return Promise.resolve(false); }
    return navigator.clipboard.readText().then(function (t) { t = String(t || "").trim(); if (!t) return false; inp.value = t; return true; }, function () { inp.focus(); return false; });
  }
  // add a serial from the job summary: onto the Field Cam job too, so Field Cam doesn't drop it
  function addSerial(job, entry) {
    var s = { code: entry.code, item: entry.item || "", sku: entry.sku || "" }; if (entry.rec) s.rec = true;
    job.serials = (job.serials || []).concat([s]);
    var camJobs = get("fieldcam.jobs", {}) || {}, cj = job.camJobId && camJobs[job.camJobId];
    if (cj) { cj.serials = (cj.serials || []).concat([Object.assign({}, s)]); set("fieldcam.jobs", camJobs); }
    save(job); return syncDeploys(job);
  }
  // the job's choices live on its Field Cam job too, so Field Cam and the job summary always agree
  function setSlot(job, id, value) {
    job.slots = Object.assign({}, job.slots || {}); job.slots[id] = value;
    var camJobs = get("fieldcam.jobs", {}) || {}, cj = job.camJobId && camJobs[job.camJobId];
    if (cj) { cj.slots = Object.assign({}, cj.slots || {}); cj.slots[id] = value; set("fieldcam.jobs", camJobs); }
    save(job); return syncDeploys(job);
  }
  /* One way to show the slots, used by Field Cam and the job summary.
     o.scan: html for an empty serial slot's button; o.status(code): line under a filled serial; o.pick: offer Pick Item */
  // slots the tech opened to change (id -> the answer when opened)
  var OPEN_SLOT = {};
  function openSlot(id, value) { OPEN_SLOT[id] = value || ""; }
  // any answer tapped in an opened slot (even the same one) folds it again
  document.addEventListener("click", function (e) { var t = e.target && e.target.closest && e.target.closest("[data-slot-set]"); if (t) delete OPEN_SLOT[t.getAttribute("data-slot-set")]; }, true);
  // the Paste button that sits inside the serial box (clipboard icon)
  function pasteIn(id) {
    return '<button type="button" class="fk-pastein fkj-pastein" data-slot-paste="' + esc(id) + '" aria-label="Paste" title="Paste">' +
      '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><rect x="8" y="2" width="8" height="4" rx="1"/><path d="M16 4h2a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h2"/></svg></button>';
  }
  function slotsHTML(model, o) {
    css(); o = o || {};
    var tick = '<i class="fkj-ok" aria-hidden="true">✓</i>', dot = '<i class="fkj-need" aria-hidden="true"></i>';
    var html = '<div class="fkj-slots">' + model.rows.map(function (r) {
      if (r.kind === "choice" && r.ui === "mount") {
        var M = slotSet().mount, none = r.value === M.none, base = none ? "" : String(r.value || "").replace(/ \+ 10ft Pole$/, ""), pole = / \+ 10ft Pole$/.test(r.value || "");
        // once answered it folds to one line, like Surge; tap it to change (opened stays open until the answer changes)
        if (r.value && OPEN_SLOT[r.id] !== r.value)
          return '<div class="fkj-slot fkj-row"><div class="fkj-sh">' + tick + '<b>' + esc(r.name) + '</b></div><button type="button" class="fkj-change" data-slot-open="' + esc(r.id) + '" data-v="' + esc(r.value) + '" aria-label="Change mount">' +
            '<span class="fkj-val">' + esc(none ? "New mount not required" : base + (pole ? " + 10ft pole" : "")) + '</span><span class="fkj-chev" aria-hidden="true">▾</span></button></div>';
        // "New mount not required" sits on the right of the Mount heading (reused existing, or on a tower: nothing to log)
        var mh = '<div class="fkj-slot"><div class="fkj-sh">' + (r.done ? tick : r.optional ? '<i class="fkj-need fkj-maybe" aria-hidden="true"></i>' : dot) + '<b>' + esc(r.name) + '</b>' +
          '<label class="fkj-chk fkj-chk-r"><input type="checkbox" data-slot-set="mount" data-v="' + (none ? "" : esc(M.none)) + '"' + (none ? " checked" : "") + '><span>New mount not required</span></label></div>' +
          '<div class="fkj-seg' + (none ? ' fkj-off' : '') + '" role="group" aria-label="Mount type">' + M.types.map(function (t) {
            var v = M.poles.indexOf(t) >= 0 ? t + " + 10ft Pole" : t;   // a gable mount or tripod starts with its pole ticked
            if (t === base) v = r.value;                                   // tapping the picked one keeps the pole answer
            return '<button type="button" style="grid-column:span 3" data-slot-set="mount" data-v="' + esc(v) + '" aria-pressed="' + (t === base) + '">' + esc(t) + '</button>';
          }).join("") + '</div>';
        if (M.poles.indexOf(base) >= 0)
          mh += '<label class="fkj-chk"><input type="checkbox" data-slot-set="mount" data-v="' + esc(pole ? base : base + " + 10ft Pole") + '"' + (pole ? " checked" : "") + '><span>Deployed 10ft pole</span></label>';
        return mh + '</div>';
      }
      if (r.kind === "choice") {
        // only one possible answer (Surge): just shows it
        if (r.opts.length === 1) return '<div class="fkj-slot fkj-row"><div class="fkj-sh">' + tick + '<b>' + esc(r.name) + '</b></div><span class="fkj-val">' + esc(r.value) + '</span></div>';
        // 6-column grid: up to 3 choices share a row equally; otherwise short ones go 3 to a row, long ones 2
        var long = r.opts.length > 3 && r.opts.some(function (v) { return v.length > 10; });   // long names (Mount): two to a row
        var span = function (v) { return r.opts.length <= 3 ? 6 / r.opts.length : long ? 3 : 2; };
        return '<div class="fkj-slot"><div class="fkj-sh">' + (r.done ? tick : r.optional ? '<i class="fkj-need fkj-maybe" aria-hidden="true"></i>' : dot) + '<b>' + esc(r.name) + '</b></div><div class="fkj-seg" role="group" aria-label="' + esc(r.name) + '">' +
          r.opts.map(function (v) { return '<button type="button" style="grid-column:span ' + span(v) + '" data-slot-set="' + esc(r.id) + '" data-v="' + esc(v) + '" aria-pressed="' + (r.value === v) + '">' + esc(v) + '</button>'; }).join("") + '</div></div>';
      }
      if (r.item) {
        return '<div class="fkj-slot fkj-row"><div class="fkj-sh">' + tick + '<div class="fkj-txt"><b>' + esc(r.name) + '</b><span class="fkj-snum">' + esc(r.item.code) + '</span><small>' + esc(r.item.item || "") + '</small>' + (o.status ? o.status(r.item.code) : "") + '</div></div>' +
          '<button type="button" class="fkj-btn" data-slot-rm="' + esc(r.item.code) + '">Remove</button></div>';
      }
      return '<div class="fkj-slot"><div class="fkj-sh">' + (r.optional ? '<i class="fkj-need fkj-maybe" aria-hidden="true"></i>' : dot) + '<div class="fkj-txt"><b>' + esc(r.name) + '</b>' + (r.hint ? '<small>' + esc(r.hint) + '</small>' : "") + '</div></div>' +
        '<div class="fkj-add"><span class="fkj-in"><input type="text" data-slot-in="' + esc(r.id) + '" placeholder="Enter S/N" aria-label="' + esc(r.name) + ' serial number" autocapitalize="characters" autocomplete="off" autocorrect="off" spellcheck="false" enterkeyhint="done">' +
        pasteIn(r.id) + '</span><button type="button" class="fkj-btn" data-slot-add="' + esc(r.id) + '">Add</button>' + (o.scan || "") + '</div></div>';
    }).join("");
    if (model.extras.length) {
      html += '<p class="fkj-grp">' + (model.has ? "Other equipment" : "Equipment") + '</p>' + model.extras.map(function (s) {
        return '<div class="fkj-slot fkj-row"><div class="fkj-sh">' + (s.sku ? tick : dot) + '<div class="fkj-txt"><b>' + esc(s.item || (s.sku && SKU[s.sku] && SKU[s.sku].name) || "Unknown item") + '</b><span class="fkj-snum">' + esc(s.code) + '</span>' +
          (o.status ? o.status(s.code, s) : "") + '</div></div><div class="fkj-btns">' + (o.pick && !s.sku ? '<button type="button" class="fkj-btn" data-pick="' + esc(s.code) + '">Pick Item</button>' : "") +
          '<button type="button" class="fkj-btn" data-slot-rm="' + esc(s.code) + '">Remove</button></div></div>';
      }).join("");
    }
    if (model.canRecover) {
      html += '<p class="fkj-grp fkj-recgrp">Recovered from the customer</p>' + model.recovered.map(function (s) {
        return '<div class="fkj-slot fkj-row"><div class="fkj-sh"><i class="fkj-ok fkj-rec" aria-hidden="true">↩</i><div class="fkj-txt"><b>' + esc(s.item || (s.sku && SKU[s.sku] && SKU[s.sku].name) || "Unknown item") + '</b><span class="fkj-snum">' + esc(s.code) + '</span>' +
          (o.status ? o.status(s.code, s) : "") + '</div></div><div class="fkj-btns">' + (o.pick && !s.sku ? '<button type="button" class="fkj-btn" data-pick="' + esc(s.code) + '">Pick Item</button>' : "") +
          '<button type="button" class="fkj-btn" data-slot-rm="' + esc(s.code) + '">Remove</button></div></div>';
      }).join("") +
        '<div class="fkj-slot"><div class="fkj-add"><span class="fkj-in"><input type="text" data-slot-in="__rec" placeholder="Recovered S/N" aria-label="Recovered equipment serial number" autocapitalize="characters" autocomplete="off" autocorrect="off" spellcheck="false" enterkeyhint="done">' +
        pasteIn("__rec") + '</span><button type="button" class="fkj-btn" data-slot-add="__rec">Add</button>' + (o.scanRec || "") + '</div>' +
        (model.recovered.length ? "" : '<small class="fkj-recnote">Only if you took equipment back. It goes into your stock in Field Stock.</small>') + '</div>';
    }
    return html + '</div>';
  }

  /* ---------- Field Notes: same idea for the comment form, prefilled from Field Cam ---------- */
  var NOTE_TYPE = { INS: "Install", CON: "Conversion", REP: "Repair", REC: "Recovery" };
  var NOTE_OUT = { OK: "Complete", CC: "Cannot Complete", NR: "Not Required" };
  // Field Cam photo label -> Field Notes picture checklist item(s)
  var PHOTO_MAP = {
    "Temp Drop Form": ["Temp drop form"],
    "Install Overview": ["Total install overview"], "NID w/ Door Open": ["NID location with door open"], "Fibre Patch Run": ["Fibre patch cable run"],
    "Cable Entry Point": ["Cable entrypoint"], "Cable Entry Hole Sealed": ["Cable entrypoint"], "ONT Placement": ["ONT placement"], "Router Placement": ["Router placement"], "MPT": ["MPT"],
    "Drop Route": ["Drop route"], "Buried Drop Route": ["Drop route"], "Line of Sight": ["CPE line of sight", "Line of sight"],
    "CPE & Mount": ["CPE & mount overview"], "Dish & Mount": ["Dish & mount overview"], "Outdoor Cable Run": ["Cable run"],
    "Ground Connection": ["Grounding overview"], "Grounding": ["Grounding overview"], "Indoor Cable Run": ["Indoor cable run"],
    "Modem Placement": ["Indoor equipment"], "XWR Placement": ["Indoor equipment"], "XWH Placement": ["Indoor equipment"], "PoE Placement": ["Indoor equipment"], "XTV Box Placement": ["Indoor equipment"],
    // device photos (1.17.0)
    "ONT SN": ["ONT placement"], "XWR SN": ["Indoor equipment"], "XWH SN": ["Indoor equipment"], "XTV SN": ["Indoor equipment"], "Modem SN": ["Indoor equipment"],
    "Issue(s) Found": ["Issue(s) found", "Issue found"], "Issue(s) Repaired": ["Issue resolved after repair", "Issue after repair"]
  };
  function notesFill(job, st) {
    st = st || {};
    var plat = job.plat || "", drop = "";
    var m = /^Fibre \((.+)\)$/.exec(plat); if (m) { plat = "Fibre"; drop = m[1]; }
    if (plat === "VAS") plat = "Value Added Services";
    if (!st.job_type && NOTE_TYPE[job.work]) st.job_type = NOTE_TYPE[job.work];
    if (!st.job_plat && plat) st.job_plat = plat;
    if (!st.job_outcome) st.job_outcome = NOTE_OUT[job.outcome] || "Complete";
    // the SA's Technology: Field Notes' Technology, Fixed Wireless Platform (FWN / LTE), and the VAS repair's equipment
    var tech = job.tech || job.vas || ((/· VAS · (XWR|XWH|XTV)\b/.exec(job.base || "") || [])[1]) || "";
    if (!st.job_tech && tech) st.job_tech = tech;
    if (!st.fw_plat && plat === "Fixed Wireless" && (tech === "FWN" || tech === "LTE")) st.fw_plat = tech;
    if (!st.vas_gear && plat === "Value Added Services" && job.work === "REP" && /^(XWR|XWH|XTV)$/.test(tech)) { st.vas_gear = {}; st.vas_gear[tech] = true; }
    if (!st.job_drop && drop && (st.job_type === "Install" || st.job_type === "Conversion") && st.job_outcome === "Complete") st.job_drop = drop;
    // drop length picked in the Drop slot; XWH / XTV counts from what was scanned
    var dsl = job.slots && job.slots.drop;
    if (!st.drop_len && dsl && dsl !== "No" && dsl !== "Not Needed" && slotIds(job).indexOf("drop") >= 0) st.drop_len = dsl;
    var mdl = slotModel(job, null);
    ["xwh", "xtv"].forEach(function (id) {
      var key = id === "xtv" ? "tv" : "xwh", n = mdl.rows.filter(function (r) { return r.id === id && r.item; }).length;
      if (!st[key] && n) st[key] = String(n);
    });
    // tick each picture Field Cam took (once per item, so the tech can still untick it)
    var done = (job.notes && job.notes.ticked) || [], items = [];
    Object.keys(job.labels || {}).forEach(function (l) { if (job.labels[l] && PHOTO_MAP[l]) items = items.concat(PHOTO_MAP[l]); });
    if ((job.serials || []).length && (!job.outcome || job.outcome === "OK")) items.push("Equipment SNs");
    st.photos = st.photos || {};
    items.forEach(function (it) { if (done.indexOf(it) < 0) { st.photos[it] = true; done.push(it); } });
    job.notes = Object.assign({ state: null, comment: "", copiedAt: 0 }, job.notes || {}, { ticked: done });
    return st;
  }
  function wipState() { var w = get(WIP, null); return w && w.state ? w.state : null; }
  // Field Notes' Drop Route: a buried span ticked "Temp Drop Deployed". Reads the SA's own comment form (the live one while it's open).
  function tempDrop() {
    var j = active(); if (!j) return false;
    var st = (raw(K.notesOwner) === j.id ? wipState() : null) || (j.notes && j.notes.state); if (!st) return false;
    for (var i = 1; i <= 20; i++) if (st["span" + i + "_type"] === "Buried" && st["span" + i + "_temp"] === true) return true;
    return false;
  }
  var notesOwner = raw(K.notesOwner);
  if (notesOwner && (!notesInJob || notesOwner !== active().id)) {
    var oj = byId(notesOwner), ows = wipState();
    if (oj && ows) { oj.notes.state = ows; save(oj); }                 // the job's comment form goes back into the job
    var back = get(K.notesSolo, null); if (back) set(WIP, back); else del(WIP);
    del(K.notesSolo); setRaw(K.notesOwner, ""); notesOwner = "";
  }
  if (APP === "notes") {
    if (notesInJob) {
      var nj = active(), st;
      if (notesOwner === nj.id) st = wipState() || (nj.notes && nj.notes.state);   // page reloaded inside the job
      else { var solo = get(WIP, null); if (solo) set(K.notesSolo, solo); else del(K.notesSolo); setRaw(K.notesOwner, nj.id); st = nj.notes && nj.notes.state; }
      st = notesFill(nj, st ? JSON.parse(JSON.stringify(st)) : null);
      nj.notes.state = st; if (nj.step === "cam") nj.step = "notes"; save(nj);
      set(WIP, { at: Date.now(), state: st });
    }
    if (notesInJob) {
      var keepNotes = function () { var j = active(), s = wipState(); if (j && s) { j.notes.state = s; save(j); notesToSlots(j, s); } };
      addEventListener("pagehide", keepNotes);
      document.addEventListener("visibilitychange", function () { if (document.hidden) keepNotes(); });
    }
  }

  /* ---------- tools in a job: the way back goes to the job summary, and reads as the job's SA-# ---------- */
  if (jobMode && APP !== "home") {
    document.addEventListener("DOMContentLoaded", function () {
      var j = active(), label = "‹ " + ((j && j.sa) || "SA");
      [].forEach.call(document.querySelectorAll(".fk-back"), function (a) { a.setAttribute("href", "index.html#job"); a.classList.add("sa"); /* keeps its arrow icon (1.20.31: just the arrow) */ a.setAttribute("aria-label", "Back to SA " + ((j && j.sa) || "")); });
    });
  }

  /* ---------- Field Cam reports the job as it goes ---------- */
  // the job's outcome changed: Field Notes follows, and a comment already copied needs redoing
  function outcomeFollow(j, outcome) {
    var st = j.notes && j.notes.state, name = NOTE_OUT[outcome] || "";
    if (st && name && st.job_outcome !== name) { st.job_outcome = name; if (st.job_drop && name !== "Complete") delete st.job_drop; }
    if (j.notes && j.notes.comment) j.notes.stale = true;
  }
  // the SA's Technology (FTX, FWN, HJ3...) goes after the platform: "Install · Fixed Wireless · FWN"
  function withTech(s, tech) {
    if (!s || !tech) return s;
    var p = String(s).split(" · "); if (p.indexOf(tech) >= 0) return s;
    p.splice(Math.min(2, p.length), 0, tech); return p.join(" · ");
  }
  function fromCam(info) {
    var j = active(); if (!j || !info) return;
    if (info.outcome != null && (j.outcome || "") !== info.outcome && (j.outcome || info.outcome !== "OK")) outcomeFollow(j, info.outcome);
    if (info.base) j.base = info.base;
    if (info.outcomes) j.outcomeOpts = info.outcomes;
    if (info.camJobId) { j.camJobId = info.camJobId; if (j.camJobIds.indexOf(info.camJobId) < 0) j.camJobIds.push(info.camJobId); }
    ["sa", "work", "plat", "outcome", "reason", "title"].forEach(function (k) { if (info[k] != null) j[k] = info[k]; });
    if (j.tech) { j.base = withTech(j.base, j.tech); j.title = withTech(j.title, j.tech); }
    if (info.photos != null) j.photos = info.photos;
    if (info.unsaved != null) j.unsaved = info.unsaved;
    if (info.need != null) { j.need = info.need; j.missing = info.missing || 0; }   // required photos, for the menu's SA card
    if (info.labels) j.labels = info.labels;
    if (info.serials) j.serials = info.serials;
    if (info.slots) j.slots = info.slots;
    save(j);
    syncDeploys(j);
  }

  /* ---------- equipment: identify a scanned serial, log it in Field Stock ---------- */
  var CAT = window.FK_CATALOG || { SKUS: [], GROUPS: [], SERIAL_RULES: [] };
  var SKU = {}; CAT.SKUS.forEach(function (s) { SKU[s.id] = s; });
  function events() { return get("techstock.events", []); }
  function stockRecord(serial) {
    var k = keyOf(serial), last = null;
    events().forEach(function (e) { if (!e.voided && e.serialKey === k && (!last || e.ts > last.ts)) last = e; });
    return last;
  }
  // which item a serial is: this phone's stock records first, then the inventory team's patterns
  function modelsFor(serial) {
    var rec = stockRecord(serial); if (rec && SKU[rec.sku]) return [rec.sku];
    // known serials, then patterns; items sharing a name count once, so e.g. any Nokia XS-010X needs no question
    return CAT.match ? CAT.match(serial).filter(function (id) { return SKU[id]; }) : [];
  }
  /* The Field Cam photo a scanned serial counts as: radio -> CPE, router -> XWR, ONT -> ONT, modem -> Modem,
     TRIA -> TRIA, XWH -> XWH, XTV -> XTV. Found from the item the serial belongs to. */
  var DEVICE_PHOTO = { radio: "CPE SN", router: "XWR SN", ont: "ONT SN", modem: "Modem SN", tria: "TRIA SN", xwh: "XWH SN", xtv: "XTV SN" };
  // by the item's product family in the catalogue, so every model counts (Hughes modems and TRIAs too), not just the ones in an SA slot
  var FAM_PHOTO = { "5G CPE": "CPE SN", "HIGH-GAIN": "CPE SN", "CAT4 3.5GHZ": "CPE SN", "CAT12 2.5GHZ": "CPE SN", "CAT12 3.5GHZ": "CPE SN",
    "ROUTER": "XWR SN", "CUBE": "XWH SN", "MESH": "XWH SN", "ONT": "ONT SN", "STB": "XTV SN",
    "MODEM": "Modem SN", "HT2000": "Modem SN", "HT3000": "Modem SN", "1 WATT RADIO": "TRIA SN", "2 WATT RADIO": "TRIA SN", "ETRIA": "TRIA SN" };
  function devicePhoto(serial) {
    var ids = modelsFor(serial), D = slotSet(), i;
    for (i = 0; i < ids.length; i++) { var s = SKU[ids[i]]; if (s && FAM_PHOTO[s.fam]) return FAM_PHOTO[s.fam]; }
    for (var k in DEVICE_PHOTO) { var d = D[k]; if (d && d.skus && ids.some(function (id) { return d.skus.indexOf(id) >= 0; })) return DEVICE_PHOTO[k]; }
    return "";
  }
  function stockNote(serial, sa) {
    var r = stockRecord(serial);
    if (!r) return "Not in your stock records";
    if (r.type === "receive") return "From your stock";
    if (r.type === "deploy") return r.sa === sa ? "Deployed on this SA" : "Already deployed" + (r.sa ? " on " + r.sa : "");
    return "Last logged as " + r.type;
  }
  /* SHA-256 and sealing: the same as Field Stock, so its History Check accepts these entries */
  var sha256 = (function () {
    var KK = new Uint32Array([0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5, 0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174, 0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da, 0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967, 0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85, 0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070, 0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3, 0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2]);
    var enc = new TextEncoder(), W = new Uint32Array(64);
    return function (s) {
      var m = enc.encode(String(s)), l = m.length, n = ((l + 9 + 63) >> 6) << 6, b = new Uint8Array(n);
      b.set(m); b[l] = 0x80; var dv = new DataView(b.buffer);
      dv.setUint32(n - 8, Math.floor(l / 0x20000000)); dv.setUint32(n - 4, (l << 3) >>> 0);
      var h0 = 0x6a09e667, h1 = 0xbb67ae85, h2 = 0x3c6ef372, h3 = 0xa54ff53a, h4 = 0x510e527f, h5 = 0x9b05688c, h6 = 0x1f83d9ab, h7 = 0x5be0cd19;
      var r = function (x, k) { return (x >>> k) | (x << (32 - k)); };
      for (var o = 0; o < n; o += 64) {
        for (var i = 0; i < 16; i++) W[i] = dv.getUint32(o + i * 4);
        for (i = 16; i < 64; i++) { var a0 = W[i - 15], c0 = W[i - 2]; W[i] = (W[i - 16] + (r(a0, 7) ^ r(a0, 18) ^ (a0 >>> 3)) + W[i - 7] + (r(c0, 17) ^ r(c0, 19) ^ (c0 >>> 10))) >>> 0; }
        var a = h0, bb = h1, c = h2, d = h3, e = h4, f = h5, g = h6, h = h7;
        for (i = 0; i < 64; i++) {
          var t1 = (h + (r(e, 6) ^ r(e, 11) ^ r(e, 25)) + ((e & f) ^ (~e & g)) + KK[i] + W[i]) >>> 0, t2 = ((r(a, 2) ^ r(a, 13) ^ r(a, 22)) + ((a & bb) ^ (a & c) ^ (bb & c))) >>> 0;
          h = g; g = f; f = e; e = (d + t1) >>> 0; d = c; c = bb; bb = a; a = (t1 + t2) >>> 0;
        }
        h0 = (h0 + a) >>> 0; h1 = (h1 + bb) >>> 0; h2 = (h2 + c) >>> 0; h3 = (h3 + d) >>> 0; h4 = (h4 + e) >>> 0; h5 = (h5 + f) >>> 0; h6 = (h6 + g) >>> 0; h7 = (h7 + h) >>> 0;
      }
      return [h0, h1, h2, h3, h4, h5, h6, h7].map(function (x) { return x.toString(16).padStart(8, "0"); }).join("");
    };
  })();
  var SEAL = ["id", "seq", "type", "ts", "sku", "serial", "qty", "account", "sa", "toTech", "from", "rma", "tracking", "note", "lat", "lng", "jobId", "prev"];
  var sealText = function (e) { return JSON.stringify(SEAL.map(function (f) { return e[f] == null ? "" : String(e[f]); })); };
  var voidText = function (e) { return JSON.stringify([e.hash || "", e.voided ? "1" : "", e.voidedAt == null ? "" : String(e.voidedAt), e.voidReason || "", e.deleted ? "1" : ""]); };
  function sealEntry(e, list) { var t = null; list.forEach(function (x) { if (x.seq && (!t || x.seq > t.seq)) t = x; }); e.seq = (t ? t.seq : 0) + 1; e.prev = t ? t.hash : "start"; e.hash = sha256(sealText(e)); }
  var newId = function () { return "e" + Date.now().toString(36) + Math.random().toString(36).slice(2, 10); };
  var lastPos = null;
  try { if (navigator.geolocation && APP === "cam") navigator.geolocation.getCurrentPosition(function (p) { lastPos = p.coords; }, function () {}, { maximumAge: 300000, timeout: 8000 }); } catch (e) {}

  /* Make Field Stock match the job: each identified serial on a job with a valid SA-# (and not Cannot Complete or
     Not Required) is deployed on that SA. A serial taken off the job, a changed SA-# or a changed outcome voids
     the old entry (kept in history, never deleted). */
  function syncDeploys(job) {
    if (!job) return { added: 0, voided: 0 };
    var list = events(), tag = "fk-" + job.id, ts = Date.now();
    var okRef = /^SA-\d{7}$/.test(job.sa || ""), okOutcome = !job.outcome || job.outcome === "OK";
    var want = okRef && okOutcome ? (job.serials || []).filter(function (s) { return !s.rec && s.sku && SKU[s.sku]; }) : [];
    // recovered equipment goes into the tech's stock: received, from Recovery, on the job's SA-# (same as Field Stock's own Receive)
    var wantRec = okRef && okOutcome && canRecover(job) ? (job.serials || []).filter(function (s) { return s.rec && s.sku && SKU[s.sku]; }) : [];
    var wantItems = okRef && okOutcome ? slotItems(job).filter(function (x) { return SKU[x.sku]; }) : [];
    var mine = list.filter(function (e) { return (e.type === "deploy" || e.type === "receive") && e.jobId === tag && !e.voided; });
    var added = 0, voided = 0;
    mine.forEach(function (e) {
      if (e.type === "receive") { if (e.sa === job.sa && wantRec.some(function (s) { return keyOf(s.code) === e.serialKey && s.sku === e.sku; })) return; }
      else if (e.sa === job.sa && !e.serialKey && wantItems.some(function (x) { return x.sku === e.sku && x.slot === e.slot; })) return;
      if (e.sa === job.sa && e.serialKey && want.some(function (s) { return keyOf(s.code) === e.serialKey && s.sku === e.sku; })) return;
      e.voided = true; e.voidedAt = ts;
      e.voidReason = e.sa !== job.sa ? "SA-# changed in the SA" : !okOutcome ? "SA outcome changed" : e.serialKey ? "Taken off the SA" : "Changed in the SA";
      e.vhash = sha256(voidText(e)); voided++;
    });
    want.forEach(function (s) {
      var k = keyOf(s.code);
      if (mine.some(function (e) { return e.type === "deploy" && !e.voided && e.serialKey === k && e.sku === s.sku && e.sa === job.sa; })) return;
      var e = { type: "deploy", ts: ts + added, jobId: tag, sa: job.sa, account: "", accountKey: "", toTech: "", from: "", rma: "", note: "Logged from a Field Kit SA",
        lat: lastPos ? lastPos.latitude : null, lng: lastPos ? lastPos.longitude : null, acc: lastPos ? lastPos.accuracy : null,
        voided: false, sku: s.sku, skuName: SKU[s.sku].name, serial: s.code, serialKey: k, qty: 1, src: "fieldkit-job" };
      e.id = newId(); sealEntry(e, list); list.push(e); added++;
    });
    wantRec.forEach(function (s) {
      var k = keyOf(s.code);
      if (mine.some(function (e) { return e.type === "receive" && !e.voided && e.serialKey === k && e.sku === s.sku && e.sa === job.sa; })) return;
      var e = { type: "receive", ts: ts + added, jobId: tag, sa: job.sa, account: "", accountKey: "", toTech: "", from: "Recovery", rma: "", note: "Recovered on a Field Kit SA",
        lat: lastPos ? lastPos.latitude : null, lng: lastPos ? lastPos.longitude : null, acc: lastPos ? lastPos.accuracy : null,
        voided: false, sku: s.sku, skuName: SKU[s.sku].name, serial: s.code, serialKey: k, qty: 1, src: "fieldkit-job" };
      e.id = newId(); sealEntry(e, list); list.push(e); added++;
    });
    wantItems.forEach(function (x) {
      if (mine.some(function (e) { return e.type === "deploy" && !e.voided && !e.serialKey && e.sku === x.sku && e.slot === x.slot && e.sa === job.sa; })) return;
      var e = { type: "deploy", ts: ts + added, jobId: tag, sa: job.sa, account: "", accountKey: "", toTech: "", from: "", rma: "", note: "Logged from a Field Kit SA",
        lat: lastPos ? lastPos.latitude : null, lng: lastPos ? lastPos.longitude : null, acc: lastPos ? lastPos.accuracy : null,
        voided: false, sku: x.sku, skuName: SKU[x.sku].name, serial: "", serialKey: "", qty: 1, src: "fieldkit-job", slot: x.slot };
      e.id = newId(); sealEntry(e, list); list.push(e); added++;
    });
    if (!added && !voided) return { added: 0, voided: 0 };
    list.sort(function (a, b) { return b.ts - a.ts; });
    if (!set("techstock.events", list)) return { added: 0, voided: 0, failed: true };
    var gs = get("techstock.gs", null); if (gs && gs.connected) { gs.rev = (gs.rev || 0) + 1; set("techstock.gs", gs); }   // Google Sheets picks it up next time Field Stock opens
    return { added: added, voided: voided };
  }
  function deployed(job) { var tag = "fk-" + job.id; return events().filter(function (e) { return e.type === "deploy" && e.jobId === tag && !e.voided; }); }
  function recoveredEvents(job) { var tag = "fk-" + job.id; return events().filter(function (e) { return e.type === "receive" && e.jobId === tag && !e.voided; }); }
  // take a serial off a job (from the job summary): off the Field Cam job too, so they stay in step
  function removeSerial(job, code) {
    var k = keyOf(code);
    job.serials = (job.serials || []).filter(function (s) { return keyOf(s.code) !== k; });
    var camJobs = get("fieldcam.jobs", {}) || {};
    (job.camJobIds || []).forEach(function (id) { var cj = camJobs[id]; if (cj && cj.serials) cj.serials = cj.serials.filter(function (s) { return keyOf(s.code) !== k; }); });
    set("fieldcam.jobs", camJobs);
    save(job); return syncDeploys(job);
  }

  /* Model picker: for a serial that fits more than one item, or none */
  function pickModel(serial, choices) {
    return new Promise(function (done) {
      css();
      var ids = choices && choices.length ? choices : null;
      var w = document.createElement("div"); w.className = "fkj-pick"; w.setAttribute("role", "dialog"); w.setAttribute("aria-label", "Which item is this?");
      function btn(id) { return '<button type="button" class="fkj-opt" data-id="' + esc(id) + '"><b>' + esc(SKU[id].name) + '</b><span>' + esc(SKU[id].famName || id) + '</span></button>'; }
      var body = ids ? ids.map(btn).join("") : CAT.GROUPS.map(function (g) {
        var its = (CAT.firstOfName || function (l) { return l; })(CAT.SKUS.filter(function (s) { return s.group === g && s.serial && !s.hidden; }));
        return its.length ? '<p class="fkj-grp">' + esc(g) + '</p>' + its.map(function (s) { return btn(s.id); }).join("") : "";
      }).join("");
      w.innerHTML = '<div class="fkj-card"><h3>Which item is this?</h3><p class="fkj-sn">' + esc(serial) + '</p><p class="fkj-sub">' +
        (ids ? "This serial fits more than one item. Pick the one on the box so Field Stock logs the right thing." : "Field Stock doesn't recognise this serial. Pick the item so it's logged as deployed.") +
        '</p><div class="fkj-list">' + body + '</div><button type="button" class="fkj-skip">Skip, don\'t log it in Field Stock</button></div>';
      w.addEventListener("click", function (e) { var b = e.target.closest(".fkj-opt"), s = e.target.closest(".fkj-skip"); if (!b && !s) return; w.remove(); done(b ? b.getAttribute("data-id") : null); });
      document.body.appendChild(w);
    });
  }
  var cssDone = false;
  function css() {
    if (cssDone) return; cssDone = true;
    var st = document.createElement("style");
    st.textContent = ".fkj-pick{position:fixed;inset:0;z-index:9998;background:rgba(0,15,14,.6);display:flex;align-items:flex-end;justify-content:center;padding:12px max(12px,env(safe-area-inset-right,0px)) calc(12px + env(safe-area-inset-bottom,0px)) max(12px,env(safe-area-inset-left,0px));font:15px/1.4 var(--fk-body,system-ui,sans-serif)}" +
      ".fkj-card{width:100%;max-width:536px;max-height:80vh;overflow:auto;background:var(--fk-surface,#fff);color:var(--fk-ink,#0E2A27);border-radius:16px;padding:18px 16px 12px;display:flex;flex-direction:column;gap:8px}" +
      ".fkj-card h3{margin:0;font:700 1.3rem/1.1 var(--fk-display,sans-serif)}.fkj-sn{margin:0;font:600 15px var(--fk-mono,monospace);color:var(--fk-accent-text,#23864A);word-break:break-all}.fkj-sub{margin:0 0 4px;color:var(--fk-muted,#5A6F69);font-size:.9rem}" +
      ".fkj-list{display:grid;gap:6px}.fkj-grp{margin:8px 0 0;font-size:.72rem;font-weight:600;letter-spacing:.08em;text-transform:uppercase;color:var(--fk-muted,#5A6F69)}" +
      ".fkj-opt{display:flex;flex-direction:column;align-items:flex-start;gap:2px;text-align:left;border:0;border-radius:10px;padding:11px 12px;background:var(--fk-surface-2,#E6EDE9);color:inherit;font:inherit;cursor:pointer}" +
      ".fkj-opt b{font-weight:600}.fkj-opt span{font:12px var(--fk-mono,monospace);color:var(--fk-muted,#5A6F69)}.fkj-opt:active{background:var(--fk-accent,#58C774);color:var(--fk-accent-ink,#06301A)}" +
      ".fkj-skip{margin-top:4px;border:0;background:none;color:var(--fk-muted,#5A6F69);font:inherit;padding:12px;cursor:pointer;text-decoration:underline}" +
      ".fkj-slots{display:flex;flex-direction:column;font:15px/1.35 var(--fk-body,system-ui,sans-serif);color:var(--fk-ink,#0E2A27)}" +
      ".fkj-slot{display:flex;flex-direction:column;gap:8px;padding:11px 0}.fkj-slot+.fkj-slot{border-top:1px solid var(--fk-line,rgba(0,43,43,.09))}" +
      ".fkj-row{flex-direction:row;align-items:center;justify-content:space-between;gap:10px}" +
      ".fkj-sh{display:flex;align-items:flex-start;gap:10px;min-width:0;flex:1}.fkj-sh>b{font-weight:600;line-height:22px}.fkj-txt{min-width:0}.fkj-txt b{display:block;font-weight:600}" +
      ".fkj-snum{display:block;font:500 .85rem/1.3 var(--fk-mono,monospace);word-break:break-all}.fkj-txt small{display:block;font-size:.8rem;color:var(--fk-muted,#5A6F69)}" +
      ".fkj-txt small.ok{color:var(--fk-accent-text,#23864A);font-weight:600}.fkj-txt small.no{color:var(--fk-warn,#B4400E);font-weight:600}" +
      ".fkj-ok,.fkj-need{flex:none;width:22px;height:22px;border-radius:50%;display:grid;place-items:center;font:700 .75rem/1 var(--fk-body,sans-serif);font-style:normal}" +
      ".fkj-ok{background:var(--fk-accent,#58C774);color:var(--fk-accent-ink,#06301A)}.fkj-need{box-shadow:inset 0 0 0 2px var(--fk-warn,#B4400E)}.fkj-need.fkj-maybe{box-shadow:inset 0 0 0 2px var(--fk-line,rgba(0,43,43,.2))}" +
      ".fkj-seg{display:grid;grid-template-columns:repeat(6,minmax(0,1fr));gap:6px}" +
      ".fkj-seg button{border:0;border-radius:10px;padding:8px 6px;min-height:46px;background:var(--fk-surface-2,#E6EDE9);color:inherit;font:600 .88rem/1.15 var(--fk-body,sans-serif);cursor:pointer;text-align:center;text-wrap:balance}" +
      ".fkj-val{flex:none;font-weight:600;color:var(--fk-accent-text,#23864A)}" +
      ".fkj-add{display:flex;gap:6px}.fkj-add input{flex:1;min-width:0;border:0;border-radius:10px;padding:0 12px;min-height:44px;background:var(--fk-surface-2,#E6EDE9);box-shadow:inset 0 0 0 1px var(--fk-line,rgba(0,43,43,.09));color:inherit;font:500 15px var(--fk-mono,monospace);text-transform:uppercase}" +
      ".fkj-add input::placeholder{font-family:var(--fk-body,sans-serif);text-transform:none;color:var(--fk-muted,#5A6F69)}.fkj-add input:focus{outline:none;box-shadow:inset 0 0 0 2px var(--fk-accent-text,#23864A)}.fkj-add .fkj-btn{min-height:44px}" +
      ".fkj-chk{display:flex;align-items:flex-start;gap:10px;margin-top:10px;font:600 .92rem/1.3 var(--fk-body,sans-serif);cursor:pointer}" +
      ".fkj-chk input{flex:none;width:22px;height:22px;margin:0;accent-color:var(--fk-accent-text,#23864A)}.fkj-chk small{display:block;font-weight:400;font-size:.82rem;color:var(--fk-muted,#5A6F69)}" +
      ".fkj-change{display:flex;align-items:center;gap:6px;border:0;background:none;padding:6px 0 6px 8px;margin:-6px 0;min-height:36px;color:inherit;font:inherit;cursor:pointer;text-align:right;min-width:0}.fkj-change .fkj-val{flex:0 1 auto}.fkj-chev{color:var(--fk-muted,#5A6F69);font-size:.8rem}" +
      ".fkj-seg.fkj-off button{opacity:.55}.fkj-chk-r{margin:-9px 0 -9px auto;align-items:center;gap:8px;font-size:.88rem;min-height:40px;text-align:right}" +
      ".fkj-in{position:relative;flex:1;min-width:0;display:flex}.fkj-in input{padding-right:46px}" +
      ".fkj-pastein{position:absolute;right:4px;top:50%;transform:translateY(-50%);width:38px;height:38px;border:0;border-radius:8px;background:transparent;color:var(--fk-muted,#5A6F69);display:grid;place-items:center;cursor:pointer;padding:0}" +
      ".fkj-pastein svg{width:20px;height:20px}.fkj-pastein:active{background:var(--fk-line,rgba(0,43,43,.09))}" +
      ".fkj-rec{background:var(--fk-surface-2,#E6EDE9)!important;color:var(--fk-ink,#0E2A27)!important;font-size:.85rem!important}.fkj-recgrp{margin-top:14px!important}.fkj-recnote{display:block;margin-top:6px;font-size:.8rem;color:var(--fk-muted,#5A6F69)}" +
      ".fkj-err{margin:0;font-size:.85rem;color:var(--fk-warn,#B4400E);font-weight:600}" +
      ".fkj-seg button[aria-pressed=\"true\"]{background:var(--fk-accent,#58C774);color:var(--fk-accent-ink,#06301A)}" +
      ".fkj-btns{display:flex;gap:6px;flex:none}.fkj-btn{flex:none;border:0;border-radius:10px;min-height:40px;padding:8px 12px;background:var(--fk-surface-2,#E6EDE9);color:inherit;font:600 .88rem/1 var(--fk-body,sans-serif);cursor:pointer;text-decoration:none;display:inline-flex;align-items:center}" +
      ".fkj-btn.primary{background:var(--fk-accent,#58C774);color:var(--fk-accent-ink,#06301A)}.fkj-btn.sure{background:var(--fk-warn-bg,#FBE7DC);color:var(--fk-warn,#B4400E)}";
    document.head.appendChild(st);
  }

  /* ---------- Field Notes: comment copied ---------- */
  function notesCopied(text, state) {
    var j = active(); if (!j) return;
    j.notes = Object.assign({}, j.notes || {}, { stale: false, comment: text, copiedAt: Date.now(), state: state ? JSON.parse(JSON.stringify(state)) : (j.notes && j.notes.state) });
    j.step = "lobby"; save(j);
    if (state) notesToSlots(j, state);
  }
  /* Answers in Field Notes that are also equipment slots: the drop length and the mount type.
     A slot follows Field Notes whenever that answer changes there; picking the slot by hand afterwards still sticks. */
  // Field Notes' Mount Type -> the mount slot (side stays aren't tracked; a tower or a reused mount means no new mount)
  var NOTES_MOUNT = { "J-Arm": "J-Arm", "Gable Mount": "Gable Mount", "Bipod": "Bipod", "Tripod": "Tripod", "Tower": "No new mount", "Tower Leg": "No new mount",
    // older Field Notes names
    "J-Arm + Side Stays": "J-Arm", "Gable Mount + 10ft Pole": "Gable Mount + 10ft Pole", "Bipod + 5ft Pole": "Bipod", "Tripod + 10ft Pole": "Tripod + 10ft Pole" };
  function notesToSlots(j, st) {
    if (!j || !st) return;
    var ids = slotIds(j), D = slotSet(), seen = (j.notes && j.notes.applied) || {}, want = {};
    if (ids.indexOf("drop") >= 0 && st.drop_len && D.drop.opts.some(function (o) { return o[0] === st.drop_len; })) want.drop = st.drop_len;
    if (ids.indexOf("mount") >= 0 && st.mount && NOTES_MOUNT[st.mount]) {
      var nm = NOTES_MOUNT[st.mount];
      if ((nm === "Gable Mount" || nm === "Tripod") && st.mount_pole === true) nm += " + 10ft Pole";   // Field Notes' 10ft pole tick
      want.mount = st.mount_reused === true ? "No new mount" : nm;   // a reused mount isn't deployed
    }
    var changed = false;
    Object.keys(want).forEach(function (k) {
      if (seen[k] === want[k]) return;   // already followed this answer
      seen[k] = want[k]; changed = true;
      if ((j.slots || {})[k] !== want[k]) { j.slots = Object.assign({}, j.slots || {}); j.slots[k] = want[k]; var cams = get("fieldcam.jobs", {}) || {}, cj = j.camJobId && cams[j.camJobId]; if (cj) { cj.slots = Object.assign({}, cj.slots || {}); cj.slots[k] = want[k]; set("fieldcam.jobs", cams); } }
    });
    if (!changed) return;
    j.notes = Object.assign({}, j.notes || {}, { applied: seen });
    save(j); syncDeploys(j);
  }
  // change the outcome from the job summary: the job, its Field Cam job (photos not saved yet are restamped next time
  // Field Cam opens), Field Notes and Field Stock all follow
  function setOutcome(job, outcome, reason) {
    if (job.outcome === outcome && (job.reason || "") === (reason || "")) return;
    var changed = job.outcome !== outcome;
    job.outcome = outcome; job.reason = reason || "";
    var oname = ({ OK: "Complete", CC: "Cannot Complete", NR: "Not Required" })[outcome] || "";
    if (job.base) job.title = job.base + " · " + oname + (reason ? " · " + reason : "");
    if (changed) outcomeFollow(job, outcome); else if (job.notes && job.notes.comment) job.notes.stale = true;
    var camJobs = get("fieldcam.jobs", {}) || {}, cj = job.camJobId && camJobs[job.camJobId];
    if (cj) { cj.outcome = outcome; cj.reason = reason || null; cj.fkRestamp = true; set("fieldcam.jobs", camJobs); }
    save(job); return syncDeploys(job);
  }
  function setStep(step) { var j = active(); if (j && j.step !== step) { j.step = step; save(j); } }

  FK.job = {
    inMode: function () { return jobMode; }, active: active, get: byId, list: list, start: start, complete: complete, open: open, save: save, setActive: setActive,
    fromCam: fromCam, modelsFor: modelsFor, modelName: function (id) { return SKU[id] ? SKU[id].name : ""; }, pickModel: pickModel, stockNote: stockNote,
    deployed: deployed, recoveredEvents: recoveredEvents, canRecover: canRecover, removeSerial: removeSerial, slotModel: slotModel, slotsHTML: slotsHTML, tempDrop: tempDrop, openSlot: openSlot, devicePhoto: devicePhoto, withTech: withTech, setSlot: setSlot, setOutcome: setOutcome, slotEntry: slotEntry, addSerial: addSerial, pasteInto: pasteInto, hasSlots: function (src) { return slotIds(src).length > 0; }, syncDeploys: syncDeploys, notesCopied: notesCopied, setStep: setStep, keepDays: 7
  };
})();
