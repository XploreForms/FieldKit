/* Field Kit offline support and updates.
   - Pages open instantly from the copy saved on the phone (works with no signal), and a fresh copy is fetched
     in the background each time.
   - A new version is noticed when version.js changes; fieldkit.js then switches every open page over to it.
   To release: change version.js. Nothing in this file needs to change. */
importScripts("version.js");
const VERSION = (self.FIELDKIT_VERSION && self.FIELDKIT_VERSION.version) || "0";
const UPDATED = (self.FIELDKIT_VERSION && self.FIELDKIT_VERSION.updated) || "";
const CACHE = "fieldkit-" + VERSION;
const FILES = ["./", "index.html", "fieldcam.html", "fieldstock.html", "fieldnotes.html", "fieldkit.js", "fieldkit.css", "fieldkit-catalog.js", "fieldkit-jobs.js", "version.js", "icon.svg", "favicon-32.png", "apple-touch-icon.png"];

self.addEventListener("install", e => {
  // fetch every file fresh from the site, skipping the browser's own cache
  e.waitUntil(caches.open(CACHE).then(c => Promise.all(FILES.map(f => fetch(new Request(f, { cache: "reload" })).then(r => { if (r.ok) return c.put(f, r); })))));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("message", e => {
  if (e.data === "update" || e.data === "SKIP_WAITING") self.skipWaiting();
  if (e.data === "version" && e.source) e.source.postMessage({ type: "version", version: VERSION, updated: UPDATED });
});
self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  if (url.origin !== location.origin) {
    // fonts and libraries never change: saved copy first
    if (!/fonts\.(googleapis|gstatic)\.com|cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net|unpkg\.com/.test(url.host)) return;
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
      if (res.ok || res.type === "opaque") { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      return res;
    })));
    return;
  }
  if (url.searchParams.has("check")) return;
  // Field Kit's own files open instantly from the copy on the phone, and a fresh copy is fetched from the
  // site in the background for next time. A new release (version.js changed) swaps every page over within
  // seconds (see fieldkit.js), so nobody stays on an old version.
  e.respondWith(caches.open(CACHE).then(c => c.match(req, { ignoreSearch: true }).then(hit => {
    const fresh = fetch(req, { cache: "no-cache" }).then(res => { if (res.ok) c.put(req, res.clone()); return res; });
    if (hit) { e.waitUntil(fresh.catch(() => {})); return hit; }
    return fresh.catch(() => c.match("index.html"));
  })));
});
