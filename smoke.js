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
  '\nglobalThis.__T={B1_WORDS,todayWordSet,renderDailyWords,renderWrongWords,renderReviewWords,init};\n' +
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

process.exit(0);
