/* 雨宝工作台 — Service Worker（离线支持）
   策略：页面导航 network-first（保证推送/更新后下次打开是最新的），离线时回退缓存；
   其它静态资源 cache-first（vendor 脚本、manifest 等）。
*/
const CACHE='yubao-v1';
const ASSETS=[
  './',
  './index.html',
  './manifest.webmanifest',
  './vendor/qrcode.js',
  './vendor/jsQR.js'
];

self.addEventListener('install',e=>{
  e.waitUntil(
    caches.open(CACHE).then(c=>c.addAll(ASSETS).catch(()=>{}))
      .then(()=>self.skipWaiting())
  );
});

self.addEventListener('activate',e=>{
  e.waitUntil(
    caches.keys().then(ks=>Promise.all(ks.filter(k=>k!==CACHE).map(k=>caches.delete(k))))
      .then(()=>self.clients.claim())
  );
});

self.addEventListener('fetch',e=>{
  if(e.request.method!=='GET')return;
  const url=new URL(e.request.url);
  // 同域 + 导航请求：优先网络，失败回退缓存（离线可用）
  if(e.request.mode==='navigate'){
    e.respondWith(
      fetch(e.request).then(r=>{
        const cp=r.clone();
        caches.open(CACHE).then(c=>c.put('./index.html',cp)).catch(()=>{});
        return r;
      }).catch(()=>caches.match('./index.html').then(c=>c||caches.match('./')))
    );
    return;
  }
  // 同源静态资源：cache-first，同时后台更新
  if(url.origin===location.origin){
    e.respondWith(
      caches.match(e.request).then(cached=>{
        if(cached)return cached;
        return fetch(e.request).then(r=>{
          if(r&&r.status===200&&r.type==='basic'){
            const cp=r.clone();caches.open(CACHE).then(c=>c.put(e.request,cp)).catch(()=>{});
          }
          return r;
        }).catch(()=>cached);
      })
    );
  }
});
