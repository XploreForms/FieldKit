/* Toolkit bridge — shared by every page of the Toolkit app (Home, Camera, Stock, Comments).
   All pages live on one site, so they share this phone's storage. Each tool keeps its own data
   exactly as before (fieldcam.*, techstock.*, xplore_fsl_*); this file only connects them:
     1. One profile (name + dealer) copied into every tool, so a tech enters it once.
     2. The current job (from Camera) published as toolkit.job, for Home and Comments.
     3. Serials scanned in Camera logged in Stock as deployments on the job's SA-#,
        sealed the same way Stock Tracker seals its own entries.
     4. Comments drafts kept per job, with the photo checklist ticked from Camera's photos.
   Load it first in <head>, before the tool's own scripts: <script src="toolkit.js" data-app="camera"></script> */
(function () {
  "use strict";
  var VERSION = "1.0.0";
  var me = document.currentScript, APP = (me && me.getAttribute("data-app")) || "home";

  function get(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  function raw(k) { try { return localStorage.getItem(k) || ""; } catch (e) { return ""; } }
  function setRaw(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  function del(k) { try { localStorage.removeItem(k); } catch (e) {} }
  var str = function (v) { return String(v == null ? "" : v).trim(); };
  var keyOf = function (s) { return String(s || "").replace(/\s+/g, "").toUpperCase(); };

  /* ---------------- 1. shared profile ---------------- */
  var K = { profile: "toolkit.profile", job: "toolkit.job", drafts: "toolkit.commentDrafts", draftFor: "toolkit.commentsFor", ticked: "toolkit.autoTicked" };
  var FSL_DRAFT = "xplore_fsl_draft_fibre_existing_v16", FSL_FIRST = "xplore_fsl_tech_first_name", FSL_LAST = "xplore_fsl_tech_last_name";

  function fromApps() {
    var fc = get("fieldcam.settings", {}), ts = get("techstock.me", {});
    var fsl = [str(raw(FSL_FIRST)), str(raw(FSL_LAST))].filter(Boolean).join(" ");
    return {
      camera: { name: str(fc.name), dealer: str(fc.dealer) },
      stock: { name: str(ts.name), dealer: str(ts.dealer) },
      comments: { name: fsl, dealer: "" }
    };
  }
  function profile() {
    var p = get(K.profile, null);
    if (p && p.name) return p;
    var a = fromApps(), name = a.camera.name || a.stock.name || a.comments.name, dealer = a.camera.dealer || a.stock.dealer;
    return { name: name || "", dealer: dealer || "" };
  }
  function pushProfile(p) {
    if (!p || !p.name) return;
    set(K.profile, { name: p.name, dealer: p.dealer || "" });
    var fc = get("fieldcam.settings", {}); fc.name = p.name; if (p.dealer) fc.dealer = p.dealer; set("fieldcam.settings", fc);
    var ts = get("techstock.me", {}); ts.name = p.name; if (p.dealer) ts.dealer = p.dealer; set("techstock.me", ts);
    var parts = p.name.split(/\s+/); setRaw(FSL_FIRST, parts.shift() || ""); setRaw(FSL_LAST, parts.join(" "));
  }
  // Before the tool's own scripts read their settings: give them the shared name and dealer
  pushProfile(profile());
  // If the tech changed their name or dealer inside a tool, that becomes the shared profile
  function pullBack() {
    var a = fromApps()[APP], p = profile();
    if (!a || !a.name) return;
    if (a.name !== p.name || (a.dealer && a.dealer !== p.dealer)) pushProfile({ name: a.name, dealer: a.dealer || p.dealer });
  }
  addEventListener("pagehide", pullBack);
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") pullBack(); });
  // Coming back with the Back button can show an old copy of the page: reload so it reads the latest data
  addEventListener("pageshow", function (e) { if (e.persisted) location.reload(); });

  /* ---------------- 2. the current job ---------------- */
  // Camera calls this whenever the job or its photos change. job = Field Cam job object.
  function publishJob(id, job, info) {
    if (!id || !job) { del(K.job); return; }
    var prev = get(K.job, {}) || {};
    set(K.job, {
      id: id, ref: job.ref || "", work: job.work || null, plat: job.plat || null, vas: job.vas || null,
      outcome: job.outcome || null, reason: job.reason || null, started: job.started || null,
      title: (info && info.title) || "", photos: (info && info.photos) || 0, labels: (info && info.labels) || {},
      missing: (info && info.missing) || [], serials: (job.serials || []).map(function (s) { return { code: s.code, item: s.item || "", sku: s.sku || null }; }),
      deployed: prev.id === id ? (prev.deployed || 0) : 0, updated: Date.now()
    });
  }
  function currentJob() { return get(K.job, null); }

  /* ---------------- 3. stock: models, lookups, sealed deployments ---------------- */
  // From Stock Tracker's inventory list (serialized items only) and its serial patterns
  var MODELS = {
    "O5-100M1": "5G Next Generation Outdoor CPE", "O5M-NA": "5G NR Rel 15 Outdoor CPE with 1Gbps 2.5G", "O5 PRO MAX": "O5 PRO MAX High Gain Outdoor CPE",
    "B5-100M": "5G High Gain Outdoor CPE", "B5-100M1": "5G High Gain Outdoor CPE (T830)", "OA-335 B42/43": "CAT12 LTE - B42/43/48",
    "FWCAT12-3.5M": "CPE-CAT12 LTE Band 42/43 MassiveMIMO", "FWCAT12-2.5M": "2.5GHz CAT12 LTE Band 42/43 M MIMO", "735060": "DUAL MODE CPE 7000",
    "854-V6": "Adtran Wi-Fi 6 Router", "834-V6": "Adtran Wi-Fi 6 Extender", "WAP6804-MT": "Metroloop Zyxel Mesh", "EMG6726-B10A-MT": "NLA Metroloop Zyxel Router",
    "3TN00665AA": "Nokia XGSPON ONT XS-010X-R", "3TN01554AA": "Nokia ONT XS-010X-D", "1287987F1": "2.5GbE GPON ONT with VOIP 601qv", "1287835F1": "Adtran 424 ONT",
    "EVOFORCE1": "Android TV Streaming Player (IPA2112HDW)", "9988030065MFG": "STB KAMAI 7XM W/NOVA REMOTE",
    "1505216-0122": "Hughes HT2000 Modem J2", "1507883-1104": "HT3000 XCI Modem", "1507724-0002": "RADIO ASSY, HC210-L, MULTI-J, LHCP", "1507724-1004": "HC210 2w Radio (LH)",
    "1504000-0022": "Assy, Radio, LHCP, Jupiter 2W", "1502938-0001": "HTJ RADIO ASSY", "1502938-0002": "HTJ RADIO ASSY, LHCP", "1502938-0016": "HTJ 1 WATT RADIO ASSY, LHCP",
    "1505328-0014": "Hughes 1 Watt Left Radio for J2", "RM4100N-043": "Satellite Modem (30V) - SurfBeam 2", "X01012000A001": "eTRIA - SurfBeam 2 (4 pack)"
  };
  var GROUPS = [
    ["5G & fixed wireless", ["O5-100M1", "O5M-NA", "O5 PRO MAX", "B5-100M", "B5-100M1"]], ["LTE", ["OA-335 B42/43", "FWCAT12-3.5M", "FWCAT12-2.5M", "735060"]],
    ["Wi-Fi & routers", ["854-V6", "834-V6", "WAP6804-MT", "EMG6726-B10A-MT"]], ["Fiber ONTs", ["3TN00665AA", "3TN01554AA", "1287987F1", "1287835F1"]],
    ["TV", ["EVOFORCE1", "9988030065MFG"]], ["Hughes satellite", ["1505216-0122", "1507883-1104", "1507724-0002", "1507724-1004", "1504000-0022", "1502938-0001", "1502938-0002", "1502938-0016", "1505328-0014"]],
    ["SurfBeam satellite", ["RM4100N-043", "X01012000A001"]]
  ];
  var RULES = [
    [/^854V6[A-Z0-9]{11}$/, ["854-V6"]], [/^834V6[A-Z0-9]{11}$/, ["834-V6"]], [/^O5SGS\d{9}$/, ["O5-100M1"]], [/^O5MGS\d{9}$/, ["O5M-NA"]],
    [/^O5PGS\d{9}$/, ["O5 PRO MAX"]], [/^B5SGS\d{9}$/, ["B5-100M", "B5-100M1"]], [/^OAK[A-Z]{2}\d{9}$/, ["OA-335 B42/43"]], [/^GMK\d{12}$/, ["FWCAT12-3.5M", "FWCAT12-2.5M"]],
    [/^GMB\d{9}$/, ["735060"]], [/^BY\d{10}[A-Z0-9]{2}$/, ["1505216-0122"]], [/^E\d{11}[A-Z0-9]{2}$/, ["1507883-1104"]], [/^902\d{9}$/, ["1507724-0002", "1507724-1004"]],
    [/^501\d{9}$/, ["1502938-0002", "1502938-0001", "1502938-0016", "1504000-0022"]], [/^601\d{9}$/, ["1505328-0014"]], [/^2837\d{8}$/, ["RM4100N-043"]],
    [/^10\d{8}$/, ["X01012000A001"]], [/^ALCLFF[0-9A-F]{6}$/, ["3TN00665AA"]], [/^ALCLFE[0-9A-F]{6}$/, ["3TN01554AA"]], [/^ALCL[0-9A-F]{8}$/, ["3TN00665AA", "3TN01554AA"]],
    [/^ADTN21[0-9A-F]{6}$/, ["1287835F1"]], [/^ADTN25[0-9A-F]{6}$/, ["1287987F1"]], [/^ADTN[0-9A-F]{8}$/, ["1287987F1", "1287835F1"]],
    [/^S2\d{2}Z\d{8}$/, ["WAP6804-MT", "EMG6726-B10A-MT"]], [/^E66AV\d{10}$/, ["EVOFORCE1"]], [/^101-\d{8}$/, ["9988030065MFG"]]
  ];
  function events() { return get("techstock.events", []); }

  // Where this serial stands in Stock: its last live entry decides
  function stockRecord(serial) {
    var k = keyOf(serial), last = null;
    events().forEach(function (e) { if (!e.voided && e.serialKey === k && (!last || e.ts > last.ts)) last = e; });
    return last;
  }
  // Which model a serial is: this phone's own Stock records first, then the inventory team's patterns
  function modelsFor(serial) {
    var rec = stockRecord(serial);
    if (rec && MODELS[rec.sku]) return [rec.sku];
    var k = keyOf(serial);
    for (var i = 0; i < RULES.length; i++) if (RULES[i][0].test(k)) return RULES[i][1].slice();
    return [];
  }
  // Short note for the tech after a scan: is it in their stock?
  function stockNote(serial, sa) {
    var r = stockRecord(serial);
    if (!r) return "Not in your stock yet (never received on this phone)";
    if (r.type === "receive") return "In your stock";
    if (r.type === "deploy") return r.sa && r.sa === sa ? "Deployed on this SA" : "Already deployed" + (r.sa ? " on " + r.sa : "");
    return "Last logged as " + r.type;
  }

  /* SHA-256 + sealing: identical to Stock Tracker, so its History Check accepts these entries */
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

  /* Make Stock match the job: every serial on a Complete (or not yet decided) job with a valid SA-#
     is deployed on that SA; a serial taken off the job, a changed SA-# or a changed outcome voids the
     old entry (voided, never deleted, so the history keeps it). Returns {added, voided}. */
  function syncDeploys(jobId, job, pos) {
    if (!jobId || !job) return { added: 0, voided: 0 };
    var list = events(), tag = "fc-" + jobId, ts = Date.now();
    var okRef = /^SA-\d{7}$/.test(job.ref || ""), okOutcome = !job.outcome || job.outcome === "OK";
    var want = okRef && okOutcome ? (job.serials || []).filter(function (s) { return s.sku && MODELS[s.sku]; }) : [];
    var mine = list.filter(function (e) { return e.type === "deploy" && e.jobId === tag && !e.voided; });
    var added = 0, voided = 0;
    mine.forEach(function (e) {
      var keep = e.sa === job.ref && want.some(function (s) { return keyOf(s.code) === e.serialKey && s.sku === e.sku; });
      if (keep) return;
      e.voided = true; e.voidedAt = ts;
      e.voidReason = e.sa !== job.ref ? "SA-# changed in Camera" : !okOutcome ? "Job outcome changed in Camera" : "Serial removed from the job in Camera";
      e.vhash = sha256(voidText(e)); voided++;
    });
    want.forEach(function (s) {
      var k = keyOf(s.code);
      if (mine.some(function (e) { return !e.voided && e.serialKey === k && e.sku === s.sku && e.sa === job.ref; })) return;
      var e = { type: "deploy", ts: ts + added, jobId: tag, sa: job.ref, account: "", accountKey: "", toTech: "", from: "", rma: "", note: "Logged from Camera",
        lat: pos && pos.latitude != null ? pos.latitude : null, lng: pos && pos.longitude != null ? pos.longitude : null, acc: pos && pos.accuracy != null ? pos.accuracy : null,
        voided: false, sku: s.sku, skuName: MODELS[s.sku], serial: s.code, serialKey: k, qty: 1, src: "camera" };
      e.id = newId(); sealEntry(e, list); list.push(e); added++;
    });
    if (!added && !voided) return { added: 0, voided: 0 };
    list.sort(function (a, b) { return b.ts - a.ts; });
    if (!set("techstock.events", list)) return { added: 0, voided: 0, failed: true };
    // Tell Stock's Google Sheets backup there's something new to send next time Stock opens
    var gs = get("techstock.gs", null); if (gs && gs.connected) { gs.rev = (gs.rev || 0) + 1; set("techstock.gs", gs); }
    var j = get(K.job, null); if (j && j.id === jobId) { j.deployed = list.filter(function (e) { return e.jobId === tag && !e.voided; }).length; set(K.job, j); }
    return { added: added, voided: voided };
  }
  function deployedOn(jobId) { var tag = "fc-" + jobId; return events().filter(function (e) { return e.type === "deploy" && e.jobId === tag && !e.voided; }); }

  /* Model picker, for serials that match more than one model (or none). Resolves a model id, or null. */
  function pickModel(serial, choices) {
    return new Promise(function (done) {
      injectCss();
      var ids = choices && choices.length ? choices : null;
      var wrap = document.createElement("div"); wrap.className = "tk-pick"; wrap.setAttribute("role", "dialog"); wrap.setAttribute("aria-label", "Which model is this?");
      var body = ids ? ids.map(btn).join("") : GROUPS.map(function (g) { return "<p class=\"tk-grp\">" + esc(g[0]) + "</p>" + g[1].map(btn).join(""); }).join("");
      function btn(id) { return "<button type=\"button\" class=\"tk-opt\" data-id=\"" + esc(id) + "\"><b>" + esc(MODELS[id]) + "</b><span>" + esc(id) + "</span></button>"; }
      wrap.innerHTML = "<div class=\"tk-card\"><h3>Which model is this?</h3><p class=\"tk-sn\">" + esc(serial) + "</p><p class=\"tk-sub\">" +
        (ids ? "This serial fits more than one model. Pick the one on the box so Stock logs the right item." : "Stock doesn't recognise this serial. Pick the item so it's logged as deployed.") +
        "</p><div class=\"tk-list\">" + body + "</div><button type=\"button\" class=\"tk-skip\">Skip, don't log it in Stock</button></div>";
      wrap.addEventListener("click", function (e) {
        var b = e.target.closest(".tk-opt"), s = e.target.closest(".tk-skip");
        if (!b && !s) return;
        wrap.remove(); done(b ? b.getAttribute("data-id") : null);
      });
      document.body.appendChild(wrap);
    });
  }
  function esc(s) { return String(s == null ? "" : s).replace(/[&<>"']/g, function (c) { return { "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]; }); }
  var cssDone = false;
  function injectCss() {
    if (cssDone) return; cssDone = true;
    var st = document.createElement("style");
    st.textContent = ".tk-pick{position:fixed;inset:0;z-index:9999;background:rgba(0,15,14,.72);display:flex;align-items:flex-end;justify-content:center;padding:12px max(12px,env(safe-area-inset-right,0px)) calc(12px + env(safe-area-inset-bottom,0px)) max(12px,env(safe-area-inset-left,0px));font:15px/1.4 -apple-system,BlinkMacSystemFont,system-ui,sans-serif}" +
      ".tk-card{width:100%;max-width:460px;max-height:80vh;overflow:auto;background:#0F1F1C;color:#EAF2EE;border-radius:18px;padding:18px 16px 14px;display:flex;flex-direction:column;gap:8px}" +
      ".tk-card h3{margin:0;font-size:18px}.tk-sn{margin:0;font:600 15px ui-monospace,Menlo,monospace;color:#58C774;word-break:break-all}.tk-sub{margin:0 0 4px;color:#9DB3AB;font-size:13.5px}" +
      ".tk-list{display:grid;gap:6px}.tk-grp{margin:8px 0 0;font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:#9DB3AB}" +
      ".tk-opt{display:flex;flex-direction:column;align-items:flex-start;gap:2px;text-align:left;border:0;border-radius:11px;padding:11px 12px;background:#1A2D29;color:inherit;font:inherit;cursor:pointer}" +
      ".tk-opt b{font-weight:600}.tk-opt span{font:12px ui-monospace,Menlo,monospace;color:#9DB3AB}.tk-opt:active{background:#58C774;color:#05230F}" +
      ".tk-skip{margin-top:6px;border:0;background:none;color:#9DB3AB;font:inherit;padding:10px;cursor:pointer;text-decoration:underline}";
    document.head.appendChild(st);
  }

  /* ---------------- 4. Comments: one draft per job, photo checklist from Camera ---------------- */
  // Camera photo label -> Comments photo checklist item (Install · Fibre (Existing Drop))
  var PHOTO_MAP = { "Install Overview": "Total install overview", "NID w/ Door Open": "NID location with door open", "Fibre Patch Run": "Fibre patch cable run",
    "Cable Entry Point": "Cable entrypoint", "ONT Placement": "ONT placement", "Router Placement": "Router placement" };
  function prepareComments() {
    var job = currentJob(); if (!job) return null;
    var owner = raw(K.draftFor) ? get(K.draftFor, "") : "";
    var drafts = get(K.drafts, {});
    if (owner !== job.id) {
      var cur = raw(FSL_DRAFT);
      if (owner && cur) drafts[owner] = cur;                // keep the other job's comments
      if (drafts[job.id]) setRaw(FSL_DRAFT, drafts[job.id]); else del(FSL_DRAFT);
      delete drafts[job.id];
      // keep the 20 most recent other drafts
      var ks = Object.keys(drafts); if (ks.length > 20) ks.slice(0, ks.length - 20).forEach(function (k) { delete drafts[k]; });
      set(K.drafts, drafts); set(K.draftFor, job.id);
    }
    // tick each photo Camera has taken (once per item, so a tech can still untick it)
    var state = {}; try { state = JSON.parse(raw(FSL_DRAFT) || "{}") || {}; } catch (e) { state = {}; }
    var ticked = get(K.ticked, {}), done = ticked[job.id] || [], changed = false;
    state.photos = state.photos || {};
    Object.keys(job.labels || {}).forEach(function (l) {
      var item = PHOTO_MAP[l]; if (!item || !job.labels[l] || done.indexOf(item) >= 0) return;
      state.photos[item] = true; done.push(item); changed = true;
    });
    if (changed) { setRaw(FSL_DRAFT, JSON.stringify(state)); ticked[job.id] = done; set(K.ticked, ticked); }
    return job;
  }
  var COMMENT_TYPES = [{ work: "INS", plat: "Fibre (Existing Drop)", name: "Install · Fibre (Existing Drop)" }];
  function commentsFit(job) { return !!job && COMMENT_TYPES.some(function (t) { return t.work === job.work && t.plat === job.plat; }); }

  window.Toolkit = {
    version: VERSION, app: APP, profile: profile, setProfile: pushProfile,
    publishJob: publishJob, currentJob: currentJob,
    modelsFor: modelsFor, modelName: function (id) { return MODELS[id] || ""; }, pickModel: pickModel, stockNote: stockNote,
    syncDeploys: syncDeploys, deployedOn: deployedOn,
    prepareComments: prepareComments, commentsFit: commentsFit, commentTypes: COMMENT_TYPES, esc: esc
  };
  // Comments reads its draft as soon as its script runs, so the job's draft is put in place first
  if (APP === "comments") { try { prepareComments(); } catch (e) {} }
})();
