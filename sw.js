const V = "fz-v1";
self.addEventListener("install", e => {
  e.waitUntil(caches.open(V).then(c => c.addAll(["./", "index.html", "manifest.json", "icon-192.png"])).then(() => self.skipWaiting()));
});
self.addEventListener("activate", e => {
  e.waitUntil(caches.keys().then(k => Promise.all(k.filter(x => x !== V).map(x => caches.delete(x)))).then(() => self.clients.claim()));
});
self.addEventListener("fetch", e => {
  const r = e.request;
  if (r.method !== "GET") return;
  if (new URL(r.url).origin !== location.origin) {   // escudos externos: primero la copia guardada
    e.respondWith(caches.open(V).then(c => c.match(r).then(m => m || fetch(r).then(x => { c.put(r, x.clone()); return x; }).catch(() => m))));
    return;
  }
  e.respondWith(fetch(r).then(x => { const y = x.clone(); caches.open(V).then(c => c.put(r, y)); return x; }).catch(() => caches.match(r)));
});
