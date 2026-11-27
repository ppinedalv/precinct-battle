// Precinct Battle offline cache. VERSION is rewritten by tools/build_mobile.py on every build.
const VERSION='7713bc3c08';
const CACHE='pb-'+VERSION;
const FILES=['./','index.html','manifest.json','vendor/three.module.js','vendor/addons/geometries/RoundedBoxGeometry.js',
  'vendor/addons/environments/RoomEnvironment.js','icons/icon-180.png','icons/icon-192.png','icons/icon-512.png','music/dusk_dishonor.mp3'];
self.addEventListener('install',e=>{e.waitUntil(caches.open(CACHE).then(c=>c.addAll(FILES)).then(()=>self.skipWaiting()));});
self.addEventListener('activate',e=>{e.waitUntil(caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k)))).then(()=>self.clients.claim()));});
self.addEventListener('fetch',e=>{const r=e.request;if(r.method!=='GET'||new URL(r.url).origin!==location.origin)return;
  if(new URL(r.url).pathname.endsWith('version.txt'))return;   // always from the network: the app compares it to its own build to self-update
  // the game page: newest from the network when online, the saved copy when offline
  if(r.mode==='navigate'){e.respondWith(fetch(r).then(res=>{const c=res.clone();caches.open(CACHE).then(x=>x.put('index.html',c));return res;})
    .catch(()=>caches.match('index.html',{ignoreSearch:true})));return;}
  e.respondWith(caches.match(r,{ignoreSearch:true}).then(hit=>hit||fetch(r).then(res=>{if(res.ok){const c=res.clone();caches.open(CACHE).then(x=>x.put(r,c));}return res;})));});
