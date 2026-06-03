/**
 * Service Worker — Réseau Académique Camerounais
 * Stratégie : Cache-first pour assets statiques, Network-first pour l'API.
 */

const CACHE_NAME      = 'cam-elearning-v1';
const OFFLINE_CACHE   = 'cam-elearning-offline-v1';
const STATIC_CACHE    = 'cam-elearning-static-v1';

const STATIC_ASSETS = [
  '/',
  '/index.html',
  '/login.html',
  '/register.html',
  '/profile.html',
  '/course_detail.html',
  '/create_course.html',
  '/offline.html',
  '/css/style.css',
  '/js/api.js',
  '/js/offline-sync.js',
  '/js/i18n.js',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css',
  'https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js',
];

// ── Installation ───────────────────────────────────────────────────────────────

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(STATIC_CACHE)
      .then(cache => cache.addAll(STATIC_ASSETS.filter(url => !url.startsWith('http'))))
      .then(() => self.skipWaiting())
  );
});

// ── Activation ─────────────────────────────────────────────────────────────────

self.addEventListener('activate', event => {
  event.waitUntil(
    caches.keys().then(keys =>
      Promise.all(
        keys
          .filter(k => k !== CACHE_NAME && k !== OFFLINE_CACHE && k !== STATIC_CACHE)
          .map(k => caches.delete(k))
      )
    ).then(() => self.clients.claim())
  );
});

// ── Stratégie de fetch ─────────────────────────────────────────────────────────

self.addEventListener('fetch', event => {
  const { request } = event;
  const url = new URL(request.url);

  // API → Network-first (avec fallback offline queue)
  if (url.pathname.startsWith('/api/')) {
    event.respondWith(networkFirst(request));
    return;
  }

  // Médias téléchargés → Cache-first
  if (url.pathname.startsWith('/media/')) {
    event.respondWith(cacheFirst(request, OFFLINE_CACHE));
    return;
  }

  // Assets statiques → Cache-first
  event.respondWith(cacheFirst(request, STATIC_CACHE));
});

async function networkFirst(request) {
  try {
    const response = await fetch(request);
    return response;
  } catch {
    // Hors ligne : renvoyer une réponse JSON vide
    if (request.method === 'GET') {
      return new Response(
        JSON.stringify({ success: false, message: 'Hors ligne / Offline', data: null }),
        { headers: { 'Content-Type': 'application/json' } }
      );
    }
    return new Response(null, { status: 503 });
  }
}

async function cacheFirst(request, cacheName) {
  const cached = await caches.match(request);
  if (cached) return cached;

  try {
    const response = await fetch(request);
    if (response.ok) {
      const cache = await caches.open(cacheName);
      cache.put(request, response.clone());
    }
    return response;
  } catch {
    // Page offline si navigation
    if (request.destination === 'document') {
      return caches.match('/offline.html');
    }
    return new Response('', { status: 503 });
  }
}

// ── Message depuis l'app ──────────────────────────────────────────────────────

self.addEventListener('message', event => {
  if (event.data?.type === 'CACHE_URLS') {
    const urls = event.data.urls || [];
    caches.open(OFFLINE_CACHE).then(cache => cache.addAll(urls));
  }
  if (event.data?.type === 'SKIP_WAITING') {
    self.skipWaiting();
  }
});
