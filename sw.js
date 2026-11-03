/* Field Kit offline support: every page and the shared bridge are kept on the phone, so the app
   opens with no signal. Pages are fetched fresh when there's a connection (so updates arrive),
   and the saved copy is used when there isn't. A new version waits until the tech taps Update. */
const CACHE = "fieldkit-v1";
const FILES = ["./", "index.html", "camera.html", "stock.html", "comments.html", "toolkit.js"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(FILES)));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim()));
});
self.addEventListener("message", e => { if (e.data === "update" || e.data === "SKIP_WAITING") self.skipWaiting(); });

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  // fonts and libraries from CDNs: saved copy first, they never change
  if (url.origin !== location.origin) {
    if (!/fonts\.(googleapis|gstatic)\.com|cdnjs\.cloudflare\.com|cdn\.jsdelivr\.net|unpkg\.com/.test(url.host)) return;
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
      if (res.ok || res.type === "opaque") { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
      return res;
    })));
    return;
  }
  // version checks must always hit the network
  if (url.searchParams.has("check")) return;
  // the app's own files: network first, saved copy when offline
  e.respondWith(fetch(req).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  }).catch(() => caches.match(req, { ignoreSearch: true }).then(hit => hit || caches.match("index.html"))));
});
