self.addEventListener("install", (e) => { self.skipWaiting(); });
self.addEventListener("activate", (e) => { self.clients.claim(); });
self.addEventListener("fetch", (e) => {
  e.respondWith(
    fetch(e.request, {cache: "no-store"}).catch(() => new Response("Hors ligne. Reconnectez-vous à internet."))
  );
});
