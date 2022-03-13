// This is a service worker using 'workbox'.
// The below code was taken directly from https://github.com/umluizlima/flask-pwa
// Parts not used are disabled w/ comment

console.log('Hello from sw.js');

importScripts('https://storage.googleapis.com/workbox-cdn/releases/3.2.0/workbox-sw.js');

if (workbox) {
  console.log(`Yay! Workbox is loaded 🎉`);

  // Disabling this block as I believe 'route caching' doesn't
  // apply to this application. The contents of the site change
  // based on the spotify api and user actions, so I don't think
  // there are scenarios where a page could safely be loaded from
  // cache...it's highly likely to be out of date...
  // workbox.precaching.precacheAndRoute([
  //   {
  //     "url": "/",
  //     "revision": "1"
  //   }
  // ]);

  workbox.routing.registerRoute(
    /\.(?:js|css)$/,
    workbox.strategies.staleWhileRevalidate({
      cacheName: 'static-resources',
    }),
  );

  workbox.routing.registerRoute(
    /\.(?:png|gif|jpg|jpeg|svg)$/,
    workbox.strategies.cacheFirst({
      cacheName: 'images',
      plugins: [
        new workbox.expiration.Plugin({
          maxEntries: 60,
          maxAgeSeconds: 30 * 24 * 60 * 60, // 30 Days
        }),
      ],
    }),
  );

  workbox.routing.registerRoute(
    new RegExp('https://fonts.(?:googleapis|gstatic).com/(.*)'),
    workbox.strategies.cacheFirst({
      cacheName: 'googleapis',
      plugins: [
        new workbox.expiration.Plugin({
          maxEntries: 30,
        }),
      ],
    }),
  );
} else {
  console.log(`Boo! Workbox didn't load 😬`);
}
