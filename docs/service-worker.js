// PS4 Games Database - Service Worker
// Provides offline functionality by caching all necessary files

const CACHE_NAME = 'ps4-games-db-v3';
const CACHE_VERSION = '1.2.0';

// Files to cache for offline functionality
const CACHE_FILES = [
    './',
    './index.html',
    './GAMES_format.json',
    './manifest.json',
    './gamepad-controller.js',
    './background.jpg'
];

// Install event - cache all necessary files
self.addEventListener('install', (event) => {
    console.log('[Service Worker] Installing...');
    
    event.waitUntil(
        caches.open(CACHE_NAME)
            .then((cache) => {
                console.log('[Service Worker] Caching files');
                return cache.addAll(CACHE_FILES);
            })
            .then(() => {
                console.log('[Service Worker] All files cached successfully');
                return self.skipWaiting();
            })
            .catch((error) => {
                console.error('[Service Worker] Cache failed:', error);
            })
    );
});

// Activate event - clean up old caches
self.addEventListener('activate', (event) => {
    console.log('[Service Worker] Activating...');
    
    event.waitUntil(
        caches.keys()
            .then((cacheNames) => {
                return Promise.all(
                    cacheNames.map((cacheName) => {
                        if (cacheName !== CACHE_NAME) {
                            console.log('[Service Worker] Deleting old cache:', cacheName);
                            return caches.delete(cacheName);
                        }
                    })
                );
            })
            .then(() => {
                console.log('[Service Worker] Activated successfully');
                return self.clients.claim();
            })
    );
});

// Fetch event - serve from cache, fallback to network
self.addEventListener('fetch', (event) => {
    event.respondWith(
        fetch(event.request)
            .then((response) => {
                if (!response || response.status !== 200 || response.type !== 'basic') {
                    return response;
                }

                const responseToCache = response.clone();

                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseToCache);
                });

                return response;
            })
            .catch(() => caches.match(event.request))
    );
});

// Background sync for updates
self.addEventListener('sync', (event) => {
    if (event.tag === 'sync-games') {
        console.log('[Service Worker] Background sync triggered');
    }
});

console.log('[Service Worker] Script loaded - Version:', CACHE_VERSION);
