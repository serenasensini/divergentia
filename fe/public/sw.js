/*
 * Self-destroying ("kill-switch") service worker.
 *
 * This app does NOT use a service worker. However, a previous deployment on
 * this same origin (e.g. an older PWA build or the legacy Angular app) may have
 * registered one that is still active in users' browsers. Such a stale worker
 * intercepts every fetch — including multipart POST uploads — and can stall the
 * request body, which surfaces as an nginx 408 (Request Timeout) and an upload
 * that "hangs" in the UI.
 *
 * By serving a real /sw.js that unregisters itself and clears caches, the
 * browser's periodic update check will install this worker and immediately
 * tear down the old one. Once every client has updated, this file simply keeps
 * any browser from holding a rogue worker.
 */
self.addEventListener('install', () => {
  // Activate immediately without waiting for existing clients to close.
  self.skipWaiting();
});

self.addEventListener('activate', (event) => {
  event.waitUntil(
    (async () => {
      // Drop any caches left behind by a previous service worker.
      try {
        const keys = await caches.keys();
        await Promise.all(keys.map((key) => caches.delete(key)));
      } catch {
        // Ignore: cache API may be unavailable.
      }

      // Remove this (and therefore the previous) service worker registration.
      try {
        await self.registration.unregister();
      } catch {
        // Ignore.
      }

      // Force-reload open tabs so they run without any worker interception.
      try {
        const clients = await self.clients.matchAll({ type: 'window' });
        for (const client of clients) {
          client.navigate(client.url);
        }
      } catch {
        // Ignore.
      }
    })(),
  );
});

// Never intercept requests: always go straight to the network. This guarantees
// that even before the unregister completes, uploads are not touched.
self.addEventListener('fetch', () => {
  // Intentionally empty: no event.respondWith(), so the browser performs the
  // default network fetch for every request.
});

