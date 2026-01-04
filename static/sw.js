const CACHE_NAME = 'ritualos-v1';
const ASSETS_TO_CACHE = [
    '/taskflowai/',
    '/taskflowai/login',
    '/taskflowai/dashboard',
    '/taskflowai/static/css/custom.css',
    '/taskflowai/static/manifest.json',
    'https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css',
    'https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.2/font/bootstrap-icons.css',
    'https://cdn.tailwindcss.com',
    'https://unpkg.com/alpinejs'
];

// Install Event - Cache Assets
self.addEventListener('install', (event) => {
    event.waitUntil(
        caches.open(CACHE_NAME).then((cache) => {
            console.log('[Service Worker] Caching app shell');
            return cache.addAll(ASSETS_TO_CACHE);
        })
    );
});

// Activate Event - Clean old caches
self.addEventListener('activate', (event) => {
    event.waitUntil(
        caches.keys().then((keyList) => {
            return Promise.all(
                keyList.map((key) => {
                    if (key !== CACHE_NAME) {
                        console.log('[Service Worker] Removing old cache', key);
                        return caches.delete(key);
                    }
                })
            );
        })
    );
    return self.clients.claim();
});

// Fetch Event - Network First, fallback to Cache
self.addEventListener('fetch', (event) => {
    // Ignore API calls for caching strategy (handled by app logic or specific strategy)
    if (event.request.url.includes('/api/')) {
        return;
    }

    event.respondWith(
        fetch(event.request)
            .then((response) => {
                // Check if we received a valid response
                if (!response || response.status !== 200 || response.type !== 'basic') {
                    return response;
                }

                // Clone the response
                const responseToCache = response.clone();

                caches.open(CACHE_NAME).then((cache) => {
                    cache.put(event.request, responseToCache);
                });

                return response;
            })
            .catch(() => {
                // If offline, try cache
                return caches.match(event.request).then((response) => {
                    if (response) {
                        return response;
                    }
                    // Fallback for HTML pages (offline page could be here)
                    if (event.request.headers.get('accept').includes('text/html')) {
                        return caches.match('/taskflowai/dashboard') || caches.match('/taskflowai/login');
                    }
                });
            })
    );
});
