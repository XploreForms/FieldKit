/* Field Kit shared script — loaded first on every page (menu, Field Cam, Field Stock, Field Notes).
   All pages share this phone's storage. Each tool keeps its own data as before
   (fieldcam.*, techstock.*, xplore_fsl_*); this file:
     1. keeps the tech's details (entered once in Field Kit setup) and copies them into every tool
     2. keeps appearance preferences and copies them into every tool
     3. sends a tech who hasn't finished setup back to the menu, where setup runs
   Load it in each page before the tool's own scripts: <script src="fieldkit.js" data-app="cam"></script>
   data-app: home | cam | stock | notes */
(function () {
  "use strict";
  var VERSION = (window.FIELDKIT_VERSION && window.FIELDKIT_VERSION.version) || "0";   // set in version.js
  var me = document.currentScript, APP = (me && me.getAttribute("data-app")) || "home";

  function get(k, d) { try { var v = localStorage.getItem(k); return v ? JSON.parse(v) : d; } catch (e) { return d; } }
  function set(k, v) { try { localStorage.setItem(k, JSON.stringify(v)); return true; } catch (e) { return false; } }
  function raw(k) { try { return localStorage.getItem(k) || ""; } catch (e) { return ""; } }
  function setRaw(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }
  var str = function (v) { return String(v == null ? "" : v).trim(); };

  var K = { profile: "fieldkit.profile", prefs: "fieldkit.prefs", setup: "fieldkit.setupDone" };
  var NOTES_FIRST = "xplore_fsl_tech_first_name", NOTES_LAST = "xplore_fsl_tech_last_name", NOTES_ASKED = "xplore_fsl_name_asked";
  // the details Field Stock keeps in its own record (techstock.me)
  var STOCK_FIELDS = ["name", "email", "dealer", "sap", "sf", "street", "city", "prov", "postal"];
  var SHIP_FIELDS = ["shipHold", "shipNotes"];   // stock order shipping options (can be cleared, so always copied)
  var FIELDS = STOCK_FIELDS.concat(["phone", "manager"], SHIP_FIELDS);

  // One-time carry-over from the Field Kit preview builds, which used "toolkit.*" keys
  if (!raw(K.setup) && raw("toolkit.setupDone")) setRaw(K.setup, raw("toolkit.setupDone"));

  /* ---------- details ---------- */
  function blank() { var o = {}; FIELDS.forEach(function (f) { o[f] = ""; }); return o; }
  // Before Field Kit has its own copy, start from what Field Stock and Field Cam already have on this phone
  function profile() {
    var p = Object.assign(blank(), get(K.profile, {}));
    if (p.name) return p;
    var stock = get("techstock.me", {}), cam = get("fieldcam.settings", {});
    STOCK_FIELDS.forEach(function (f) { p[f] = str(stock[f]); });
    if (!p.name) p.name = str(cam.name) || [str(raw(NOTES_FIRST)), str(raw(NOTES_LAST))].filter(Boolean).join(" ");
    if (!p.dealer) p.dealer = str(cam.dealer);
    p.manager = str(get("techstock.manager", ""));
    return p;
  }
  /* Save the details and copy them into every tool */
  function setProfile(p) {
    p = Object.assign(profile(), p || {});
    if (!p.name) return;
    var keep = {}; FIELDS.forEach(function (f) { keep[f] = str(p[f]); });
    keep.dealer = keep.dealer.replace(/\s+[-‒–—]\s+.*$/, "");   // dealer name is just the dealership, no "- First Last"
    set(K.profile, keep);
    var stock = get("techstock.me", {}); STOCK_FIELDS.forEach(function (f) { if (keep[f]) stock[f] = keep[f]; }); SHIP_FIELDS.forEach(function (f) { stock[f] = keep[f]; }); set("techstock.me", stock);
    if (keep.manager) set("techstock.manager", keep.manager);
    var cam = get("fieldcam.settings", {}); cam.name = keep.name; if (keep.dealer) cam.dealer = keep.dealer; set("fieldcam.settings", cam);
    var parts = keep.name.split(/\s+/); setRaw(NOTES_FIRST, parts.shift() || ""); setRaw(NOTES_LAST, parts.join(" ")); setRaw(NOTES_ASKED, "1");
  }

  /* ---------- appearance ---------- */
  // theme: light | dark | black (black = true black for OLED screens), the same in every tool. grid: Field Cam grid lines.
  var THEMES = ["light", "dark", "black"];
  function prefs() {
    var p = get(K.prefs, null);
    if (p) { p = Object.assign({ theme: "light", grid: false }, p); if (THEMES.indexOf(p.theme) < 0) p.theme = "light"; return p; }
    // first launch: light, no grid lines (changed in Settings). Keeps what Field Stock already had on this phone.
    var t = raw("techstock.theme");
    return { theme: /^(light|dark|black)$/.test(t) ? t : "light", grid: false };
  }
  function setPrefs(p) {
    p = Object.assign(prefs(), p || {});
    if (THEMES.indexOf(p.theme) < 0) p.theme = "light";
    set(K.prefs, { theme: p.theme, grid: !!p.grid });
    setRaw("techstock.theme", p.theme);                                   // Field Stock: light | dark | black
    var cam = get("fieldcam.settings", {}); cam.theme = p.theme; set("fieldcam.settings", cam);   // Field Cam: same (grid lines are set in Field Cam itself)
    setRaw("xplore_fsl_theme", p.theme === "light" ? "light" : "dark");   // Field Notes: black is dark with OLED on
    setRaw("xplore_fsl_oled", p.theme === "black" ? "on" : "off");
    keepTheme();
  }
  /* Every page marks its theme on the root element (fieldkit.css reads it). Keep it on the chosen one,
     even if something else on the page (like a preview window) tries to change it. */
  var watching = false;
  var BG = { light: "#F2F5F3", dark: "#0A1615", black: "#000000" };
  function keepTheme() {
    var root = document.documentElement, want = prefs().theme;
    if (root.getAttribute("data-theme") !== want) root.setAttribute("data-theme", want);
    root.style.backgroundColor = BG[want] || BG.light;   // painted before any stylesheet loads, so no white flash in dark mode
    if (!watching && window.MutationObserver) {
      watching = true;
      new MutationObserver(function () { var w = prefs().theme; if (root.getAttribute("data-theme") !== w) root.setAttribute("data-theme", w); })
        .observe(root, { attributes: true, attributeFilter: ["data-theme"] });
    }
  }

  // Before the tool's own scripts read their settings, give them the shared details and appearance
  setProfile(profile());
  setPrefs(prefs());

  // Field Cam can still change the name and dealer in its own settings: that becomes the shared copy
  function pullBack() {
    // Field Stock's manual order form can change the operations manager's email
    if (APP === "stock") { var m = str(get("techstock.manager", "")), pm = profile(); if (m && m !== pm.manager) setProfile({ manager: m }); return; }
    // name and dealer are only changed in Field Kit settings, so nothing comes back from Field Cam
  }
  addEventListener("pagehide", pullBack);
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") pullBack(); });

  // Going back with the Back button can show an old copy of a page: reload it so it shows the latest data
  addEventListener("pageshow", function (e) { if (e.persisted) location.reload(); });

  // A tool opened before setup is finished sends the tech to the menu, which runs setup
  if (APP !== "home" && !raw(K.setup)) { document.documentElement.style.visibility = "hidden"; location.replace("index.html"); }

  /* ---------- sessions in progress ----------
     Each tool saves its own work as it goes. When a tech leaves a tool with something unfinished, the tool
     notes it here ({title, sub, detail}) so the menu can show "In progress" and the tech can tap back in. */
  var SESS = "fieldkit.sessions";
  function sessions() { return get(SESS, {}) || {}; }
  function setSession(app, info) {
    var s = sessions();
    if (info) s[app] = Object.assign({ at: Date.now() }, info); else delete s[app];
    set(SESS, s);
  }
  /* Work left untouched for 8 hours is cleared, so the tool starts fresh. Checked as every page opens,
     before the tool reads its own saved work. clearTool() is also how the menu's "Start New" works. */
  var STALE = 8 * 3600000;
  function clearTool(app) {
    try {
      if (app === "cam") localStorage.setItem("fieldcam.current", "null");      // its photos stay saved in Field Cam
      if (app === "stock") localStorage.removeItem("techstock.draft");          // unsaved Logs form
      if (app === "notes") localStorage.removeItem("xplore_fsl_wip_v2");        // unfinished comment form
    } catch (e) {}
    setSession(app, null);
  }
  (function expire() {
    var s = sessions(), now = Date.now();
    Object.keys(s).forEach(function (a) { if (!s[a].at || now - s[a].at > STALE) clearTool(a); });
    var w = get("xplore_fsl_wip_v2", null); if (w && w.at && now - w.at > STALE) clearTool("notes");
  })();

  /* Coming back to a tool returns to the same spot on the page */
  var SCROLL = "fieldkit.scroll." + APP;
  function keepScroll() { try { sessionStorage.setItem(SCROLL, String(window.scrollY || 0)); } catch (e) {} }
  addEventListener("pagehide", keepScroll);
  document.addEventListener("visibilitychange", function () { if (document.visibilityState === "hidden") keepScroll(); });
  addEventListener("load", function () {
    var y = 0; try { y = Number(sessionStorage.getItem(SCROLL)) || 0; } catch (e) {}
    if (y > 0 && APP !== "home") setTimeout(function () { window.scrollTo(0, y); }, 250);
  });

  /* Pinned top bars go slim once the page is scrolled down (title smaller, tile smaller, line under the title hidden),
     and full size again back at the top. A gap between the two points stops it flickering.
     Smooth, not jarring:
       1. The page under the bar never moves. The bar gets shorter, so it keeps the height it gave up as space
          below itself (margin). Without this, everything jumped up and the browser could bounce back to full size.
       2. Where the phone supports it (Chrome / Samsung Internet, Safari 18+), the bar morphs between its two sizes
          (view transition); elsewhere it just switches. Reduce Motion turns the animation off. */
  if (APP === "notes" || APP === "stock" || APP === "home") {
    var slim = false, padded = null, anim = 0, root = document.documentElement;
    var HDR = ".lhead, header.top, header.app-header";
    var onScreen = function (el) { return !!el && el.getClientRects().length > 0; };
    var bar = function () { var l = document.querySelectorAll(HDR); for (var i = 0; i < l.length; i++) if (onScreen(l[i])) return l[i]; return null; };
    // the first thing after the bar that takes up room on the page
    var after = function (h) {
      for (var n = h.nextElementSibling; n; n = n.nextElementSibling) {
        var cs = getComputedStyle(n);
        if (cs.display !== "none" && cs.position !== "absolute" && cs.position !== "fixed" && onScreen(n)) return n;
      }
      return null;
    };
    var pageY = function (el) { return el.getBoundingClientRect().top + (window.scrollY || 0); };
    var apply = function (on) {
      if (!on) { root.classList.remove("fk-slim"); if (padded) { padded.style.marginBottom = ""; padded = null; } return; }
      var h = bar(), nx = h && after(h), was = nx ? pageY(nx) : 0;
      // the browser's own "keep my place" scrolling would pull the page up while the bar shrinks; we hold the place ourselves
      root.style.overflowAnchor = document.body.style.overflowAnchor = "none";
      requestAnimationFrame(function () { requestAnimationFrame(function () { root.style.overflowAnchor = document.body.style.overflowAnchor = ""; }); });
      root.classList.add("fk-slim");
      if (!nx) return;
      var mb = parseFloat(getComputedStyle(h).marginBottom) || 0;
      for (var i = 0; i < 2; i++) {   // twice: margins next to each other can share space
        var gap = was - pageY(nx);
        if (Math.abs(gap) < 0.5) break;
        mb += gap; h.style.marginBottom = mb + "px"; padded = h;
      }
    };
    var names = function (h, on) {
      if (!h) return;
      var back = h.querySelector(".fk-back");
      h.style.viewTransitionName = on ? "fk-hdr" : "";
      if (back && onScreen(back)) back.style.viewTransitionName = on ? "fk-hdr-back" : "";
    };
    var setSlim = function (on) {
      if (on === slim) return;
      slim = on;
      var h = bar();
      var still = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
      if (!document.startViewTransition || still || !h || document.hidden) { apply(on); return; }
      var me = ++anim;
      names(h, true); root.classList.add("fk-anim");
      var t;
      try { t = document.startViewTransition(function () { apply(on); }); }
      catch (e) { names(h, false); root.classList.remove("fk-anim"); apply(on); return; }
      var done = function () { if (me !== anim) return; names(h, false); root.classList.remove("fk-anim"); };
      t.finished.then(done, done);
    };
    var onScroll = function () {
      var y = window.scrollY || 0;
      if (!slim && y > 60) setSlim(true);
      else if (slim && y < 6) setSlim(false);
    };
    addEventListener("scroll", onScroll, { passive: true });
    addEventListener("load", onScroll);
  }

  /* ---------- updates: nobody stays on an old version ----------
     Checks for a new version when a page opens, whenever Field Kit comes back on screen, when signal returns,
     and every 5 minutes. A new version is put in place straight away on the menu, in the first few seconds
     after a tool opens, or as soon as Field Kit goes into the background. In the middle of using a tool,
     an Update Now bar shows instead; each tool keeps its work, so updating doesn't lose anything. */
  var IN_CLAUDE = !!(window.claude && typeof window.claude.use === "function");
  var LOADED = Date.now();
  function showUpdateBar(reg) {
    if (document.getElementById("fkUpd")) return;
    var bar = document.createElement("div");
    bar.id = "fkUpd"; bar.setAttribute("role", "status");
    bar.style.cssText = "position:fixed;left:50%;transform:translateX(-50%);top:calc(env(safe-area-inset-top,0px) + 8px);z-index:9999;width:calc(100% - 24px);max-width:536px;" +
      "display:flex;align-items:center;gap:10px;padding:10px 10px 10px 14px;border-radius:12px;background:var(--fk-ink,#0E2A27);color:var(--fk-bg,#F2F5F3);" +
      "box-shadow:0 6px 24px rgba(0,0,0,.25);font:500 14px/1.3 var(--fk-body,system-ui,sans-serif)";
    bar.innerHTML = '<span style="flex:1;min-width:0"><b style="display:block;font-weight:700">Field Kit has an update</b>Your work is saved. Takes a few seconds.</span>' +
      '<button type="button" style="flex:none;border:0;border-radius:8px;min-height:44px;padding:0 14px;background:var(--fk-accent,#58C774);color:var(--fk-accent-ink,#06301A);font:600 15px var(--fk-body,system-ui,sans-serif);cursor:pointer">Update Now</button>';
    bar.querySelector("button").addEventListener("click", function () { this.textContent = "Updating…"; this.disabled = true; applyUpdate(reg); setTimeout(function () { location.reload(); }, 4000); });
    (document.body || document.documentElement).appendChild(bar);
  }
  function applyUpdate(reg) { if (reg && reg.waiting) reg.waiting.postMessage("update"); }
  if ("serviceWorker" in navigator && !IN_CLAUDE && (location.protocol === "https:" || location.hostname === "localhost")) {
    var hadController = !!navigator.serviceWorker.controller;
    navigator.serviceWorker.addEventListener("controllerchange", function () { if (hadController) location.reload(); hadController = true; });
    navigator.serviceWorker.register("sw.js", { updateViaCache: "none" }).then(function (reg) {
      function onWaiting() {
        if (!reg.waiting || !navigator.serviceWorker.controller) return;
        if (APP === "home" || document.hidden || Date.now() - LOADED < 8000) applyUpdate(reg); else showUpdateBar(reg);
      }
      onWaiting();
      reg.addEventListener("updatefound", function () { var w = reg.installing; if (w) w.addEventListener("statechange", function () { if (w.state === "installed") onWaiting(); }); });
      function check() { if (navigator.onLine !== false) reg.update().catch(function () {}); }
      check(); setInterval(check, 5 * 60000);
      document.addEventListener("visibilitychange", function () { if (document.hidden) applyUpdate(reg); else check(); });
      addEventListener("online", check);
    }).catch(function () {});
  }

  window.FieldKit = {
    version: VERSION, app: APP, fields: FIELDS,
    profile: profile, setProfile: setProfile,
    prefs: prefs, setPrefs: setPrefs,
    sessions: sessions, setSession: setSession, clearTool: clearTool, staleAfter: STALE,
    setupDone: function () { return !!raw(K.setup); },
    markSetupDone: function () { setRaw(K.setup, String(Date.now())); }
  };
})();
