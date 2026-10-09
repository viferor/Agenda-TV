/* Service worker de Agenda TV.
   - Página y datos: primero la red (para tener siempre la guía del día) y, sin conexión, la última copia guardada.
   - Iconos y fuentes: primero la caché. */
const CACHE = "agendatv-v2";
const PRECACHE = ["./", "index.html", "datos.json", "manifest.json",
  "iconos/icono-192.png", "iconos/icono-512.png", "iconos/favicon.png"];

self.addEventListener("install", e => {
  e.waitUntil(caches.open(CACHE).then(c => c.addAll(PRECACHE)).then(() => self.skipWaiting()));
});

self.addEventListener("activate", e => {
  e.waitUntil(caches.keys()
    .then(keys => Promise.all(keys.filter(k => k !== CACHE).map(k => caches.delete(k))))
    .then(() => self.clients.claim()));
});

self.addEventListener("fetch", e => {
  const req = e.request;
  if (req.method !== "GET") return;
  const url = new URL(req.url);
  const isFont = /fonts\.(googleapis|gstatic)\.com$/.test(url.hostname);
  if (url.origin !== location.origin && !isFont) return;

  const isStatic = isFont || url.pathname.includes("/iconos/");
  if (isStatic) {
    e.respondWith(caches.match(req).then(hit => hit || fetch(req).then(res => {
      const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); return res;
    })));
    return;
  }
  e.respondWith(fetch(req).then(res => {
    if (res.ok) { const copy = res.clone(); caches.open(CACHE).then(c => c.put(req, copy)); }
    return res;
  }).catch(() => caches.match(req, {ignoreSearch: true})
    .then(hit => hit || (req.mode === "navigate" ? caches.match("index.html") : undefined))));
});
