self.addEventListener("install", (e) => {
	e.waitUntil(
		caches.open("cache").then((cache) => cache.addAll([
			/*
			// "/espacecate/res/style.css",
			// "/kt-static/style.css",
			// "/espacecate/res/script.js",
			// "/kt-static/global.js",
			// "/espacecate/favicon.ico",
			// "/espacecate/favicon.png",

			"https://fonts.googleapis.com/css2?family=Montserrat:ital,wght@0,400;0,700;1,400;1,700&display=swap",
			"https://cdn.jsdelivr.net/npm/jquery@3/dist/jquery.min.js",
			"https://cdn.jsdelivr.net/npm/chart.js@3/dist/chart.min.js",
			"https://cdn.jsdelivr.net/npm/sweetalert@2/dist/sweetalert.min.js",
			"https://cdn.jsdelivr.net/npm/moment@2/moment.min.js"
			*/
		]))
	);
});

self.addEventListener("fetch", (e) => {
	e.respondWith(
		// caches.match(e.request).then((response) => response || fetch(e.request)),
		fetch(e.request)
	);
});