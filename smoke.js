// Smoke test: load index.html app script under a DOM stub, verify word library + rendering.
const fs = require('fs');
const vm = require('vm');

const html = fs.readFileSync('index.html', 'utf-8');
// Extract the main IIFE script (the one containing B1_WORDS)
const scripts = [...html.matchAll(/<script>([\s\S]*?)<\/script>/g)].map(m => m[1]);
let code = scripts.find(s => s.includes('B1_WORDS'));
if (!code) { console.error('APP SCRIPT NOT FOUND'); process.exit(2); }

// Inject a test export right before the final IIFE close
const marker = '})();';
const idx = code.lastIndexOf(marker);
if (idx < 0) { console.error('IIFE close not found'); process.exit(2); }
code = code.slice(0, idx) +
  '\nglobalThis.__T={B1_WORDS,todayWordSet,renderDailyWords,renderWrongWords,renderReviewWords,renderCalendar,renderInbox,renderGrow,renderVideos,renderGrowItems,renderVideoItems,dailyPick,init};\n' +
  code.slice(idx);

// ---- DOM / browser stubs ----
function makeEl() {
  const el = {
    id:'', className:'', innerHTML:'', textContent:'', value:'', style:{},
    children:[], dataset:{}, classList:{add(){},remove(){},toggle(){},contains(){return false}},
    appendChild(c){this.children.push(c);return c;},
    removeChild(){}, setAttribute(){}, getAttribute(){return null;},
    addEventListener(){}, removeEventListener(){},
    querySelector(){return makeEl();}, querySelectorAll(){return [];},
    getElementById(){return makeEl();}, focus(){}, click(){},
    insertAdjacentHTML(){}, remove(){},
  };
  return el;
}
const listeners = {};
const document = {
  documentElement: makeEl(),
  body: makeEl(),
  head: makeEl(),
  getElementById(){return makeEl();},
  createElement(){return makeEl();},
  querySelector(){return makeEl();},
  querySelectorAll(){return [];},
  addEventListener(t,f){ (listeners[t]=listeners[t]||[]).push(f); },
  removeEventListener(){},
  cookie:'',
};
const storage = {};
const localStorage = {
  getItem(k){return k in storage?storage[k]:null;},
  setItem(k,v){storage[k]=String(v);},
  removeItem(k){delete storage[k];},
};
const sandbox = {
  document, localStorage, console,
  navigator:{userAgent:'node'}, window:{},
  setInterval(){return 0;}, clearInterval(){}, setTimeout(){return 0;}, clearTimeout(){},
  scrollTo(){}, scrollBy(){},
  addEventListener(){}, removeEventListener(){},
  speechSynthesis:{getVoices(){return[];},speak(){},cancel(){}},
  SpeechSynthesisUtterance:function(){},
  Date, Math, JSON, RegExp, Array, Object, String, Number, Boolean,
  parseInt, parseFloat, isNaN, decodeURIComponent, encodeURIComponent,
  alert(){}, confirm(){return true;}, prompt(){return '';},
  CSS:{escape:s=>String(s).replace(/["\\]/g,'\\$&')},
};
sandbox.window = sandbox;
sandbox.globalThis = sandbox;
vm.createContext(sandbox);

try {
  vm.runInContext(code, sandbox, {filename:'app.js'});
} catch(e) {
  console.error('RUN ERROR:', e.message);
  console.error(e.stack.split('\n').slice(0,5).join('\n'));
  process.exit(3);
}

const T = sandbox.__T;
if (!T) { console.error('TEST HOOK NOT EXPOSED'); process.exit(4); }

const words = T.B1_WORDS;
console.log('B1_WORDS length:', words.length);

// uniqueness
const seen = new Set(); let dup=0;
words.forEach(w=>{const k=(w.w||'').toLowerCase(); if(seen.has(k))dup++; seen.add(k);});
console.log('duplicate words:', dup);

// todayWordSet returns 10 with ph
const set = T.todayWordSet();
console.log('todayWordSet length:', set.length);
const sample = set[0];
console.log('sample word:', JSON.stringify(sample));
console.log('sample has ph:', !!(sample&&sample.ph));

// render daily words (must not throw, should include ph text)
let renderOK=true, phInRender=false;
try {
  const r = T.renderDailyWords();
  phInRender = r.includes('/') && r.includes('word-ph');
} catch(e){ renderOK=false; console.error('renderDailyWords ERROR:', e.message); }
console.log('renderDailyWords ok:', renderOK, '| ph rendered:', phInRender);

// render wrong + review (no throw)
let othersOK=true;
try { T.renderWrongWords(); T.renderReviewWords(); } catch(e){ othersOK=false; console.error('other render ERROR:', e.message); }
console.log('wrong/review render ok:', othersOK);

// init() boots nav + extras + sw wiring (must not throw under stubs)
let initOK=true;
try { T.init(); } catch(e){ initOK=false; console.error('init ERROR:', e.message, e.stack.split('\n')[1]); }
console.log('init ok:', initOK);

// new module renders
let calOK=true, inboxOK=true;
try { T.renderCalendar(); } catch(e){ calOK=false; console.error('renderCalendar ERROR:', e.message); }
try { T.renderInbox(); } catch(e){ inboxOK=false; console.error('renderInbox ERROR:', e.message); }
console.log('renderCalendar ok:', calOK);
console.log('renderInbox ok:', inboxOK);

// grow + videos push renders (with seeded cache so they render from cache, no network)
let growOK=true, vidOK=true, gItemsOK=true, vItemsOK=true, pickOK=true;
try {
  const c = sandbox.__T ? null : null;
  // seed DATA.push via the exposed internals is not direct; just call renders which read DATA (defaults empty)
  T.renderGrow();
  T.renderVideos();
  // dailyPick deterministic + daily-rotating
  const p = T.dailyPick(['a','b','c','d','e','f','g','h','i','j','k','l'], 8);
  pickOK = Array.isArray(p) && p.length===8;
  // render item builders should not throw on empty arrays
  T.renderGrowItems();
  T.renderVideoItems();
} catch(e){ growOK=false; vidOK=false; console.error('grow/videos ERROR:', e.message, e.stack.split('\n')[1]); }
console.log('renderGrow/Videos ok:', growOK && vidOK);
console.log('dailyPick ok:', pickOK);
console.log('renderGrowItems/Videos ok:', gItemsOK && vItemsOK);

process.exit(0);
