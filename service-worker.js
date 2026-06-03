// Service Worker para cache offline
const CACHE_NAME = 'ps4-store-v1';
const urlsToCache = [
  './',
  './index.html',
  './gamepad-controller.js',
  './GAMES_format.json',
  './manifest.json',
  './background.jpg'
];

self.addEventListener('install', event => {
  event.waitUntil(
    caches.open(CACHE_NAME)
      .then(cache => cache.addAll(urlsToCache))
  );
});

self.addEventListener('fetch', event => {
  event.respondWith(
    caches.match(event.request)
      .then(response => response || fetch(event.request))
      .catch(() => caches.match('./index.html'))
  );
});
