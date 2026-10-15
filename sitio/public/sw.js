// Service worker mínimo: habilita la instalación como app y sirve una página offline básica.
// Las páginas se piden siempre a la red (los datos cambian); solo se cachea el cascarón.
const CACHE = 'iglesias-v1';
const BASICO = ['/', '/cerca/', '/directorio/', '/manifest.webmanifest', '/icono.svg'];
self.addEventListener('install', e => { e.waitUntil(caches.open(CACHE).then(c => c.addAll(BASICO)).then(() => self.skipWaiting())); });
self.addEventListener('activate', e => { e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k)))).then(() => self.clients.claim())); });
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET') return;
  e.respondWith(fetch(e.request).then(r => { if (r.ok && new URL(e.request.url).origin === location.origin && !e.request.url.includes('/api/')) caches.open(CACHE).then(c => c.put(e.request, r.clone())); return r; })
    .catch(() => caches.match(e.request).then(m => m || caches.match('/'))));
});
