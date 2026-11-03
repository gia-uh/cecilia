// CecilIA voces: read prompts aloud, validate recordings, see your share.
// Takes wait in IndexedDB until they upload, so a bad connection loses nothing.
'use strict';

const $ = (id) => document.getElementById(id);
const API = '/api/voces';
const MIN_S = 1, MAX_S = 30;
const SILENCE_RMS = 0.01, CLIPPED = 0.01;

const PROVINCES = {
  'Pinar del Río': ['Consolación del Sur', 'Guane', 'La Palma', 'Los Palacios', 'Mantua', 'Minas de Matahambre', 'Pinar del Río', 'San Juan y Martínez', 'San Luis', 'Sandino', 'Viñales'],
  'Artemisa': ['Alquízar', 'Artemisa', 'Bahía Honda', 'Bauta', 'Caimito', 'Candelaria', 'Guanajay', 'Güira de Melena', 'Mariel', 'San Antonio de los Baños', 'San Cristóbal'],
  'La Habana': ['Arroyo Naranjo', 'Boyeros', 'Centro Habana', 'Cerro', 'Cotorro', 'Diez de Octubre', 'Guanabacoa', 'La Habana del Este', 'La Habana Vieja', 'La Lisa', 'Marianao', 'Playa', 'Plaza de la Revolución', 'Regla', 'San Miguel del Padrón'],
  'Mayabeque': ['Batabanó', 'Bejucal', 'Güines', 'Jaruco', 'Madruga', 'Melena del Sur', 'Nueva Paz', 'Quivicán', 'San José de las Lajas', 'San Nicolás', 'Santa Cruz del Norte'],
  'Matanzas': ['Calimete', 'Cárdenas', 'Ciénaga de Zapata', 'Colón', 'Jagüey Grande', 'Jovellanos', 'Limonar', 'Los Arabos', 'Martí', 'Matanzas', 'Pedro Betancourt', 'Perico', 'Unión de Reyes'],
  'Cienfuegos': ['Abreus', 'Aguada de Pasajeros', 'Cienfuegos', 'Cruces', 'Cumanayagua', 'Lajas', 'Palmira', 'Rodas'],
  'Villa Clara': ['Caibarién', 'Camajuaní', 'Cifuentes', 'Corralillo', 'Encrucijada', 'Manicaragua', 'Placetas', 'Quemado de Güines', 'Ranchuelo', 'Remedios', 'Sagua la Grande', 'Santa Clara', 'Santo Domingo'],
  'Sancti Spíritus': ['Cabaiguán', 'Fomento', 'Jatibonico', 'La Sierpe', 'Sancti Spíritus', 'Taguasco', 'Trinidad', 'Yaguajay'],
  'Ciego de Ávila': ['Baraguá', 'Bolivia', 'Chambas', 'Ciego de Ávila', 'Ciro Redondo', 'Florencia', 'Majagua', 'Morón', 'Primero de Enero', 'Venezuela'],
  'Camagüey': ['Camagüey', 'Carlos Manuel de Céspedes', 'Esmeralda', 'Florida', 'Guáimaro', 'Jimaguayú', 'Minas', 'Najasa', 'Nuevitas', 'Santa Cruz del Sur', 'Sibanicú', 'Sierra de Cubitas', 'Vertientes'],
  'Las Tunas': ['Amancio', 'Colombia', 'Jesús Menéndez', 'Jobabo', 'Las Tunas', 'Majibacoa', 'Manatí', 'Puerto Padre'],
  'Holguín': ['Antilla', 'Báguanos', 'Banes', 'Cacocum', 'Calixto García', 'Cueto', 'Frank País', 'Gibara', 'Holguín', 'Mayarí', 'Moa', 'Rafael Freyre', 'Sagua de Tánamo', 'Urbano Noris'],
  'Granma': ['Bartolomé Masó', 'Bayamo', 'Buey Arriba', 'Campechuela', 'Cauto Cristo', 'Guisa', 'Jiguaní', 'Manzanillo', 'Media Luna', 'Niquero', 'Pilón', 'Río Cauto', 'Yara'],
  'Santiago de Cuba': ['Contramaestre', 'Guamá', 'Mella', 'Palma Soriano', 'San Luis', 'Santiago de Cuba', 'Segundo Frente', 'Songo-La Maya', 'Tercer Frente'],
  'Guantánamo': ['Baracoa', 'Caimanera', 'El Salvador', 'Guantánamo', 'Imías', 'Maisí', 'Manuel Tames', 'Niceto Pérez', 'San Antonio del Sur', 'Yateras'],
  'Isla de la Juventud': ['Isla de la Juventud'],
};
const SHORT = ['PR', 'Art', 'LH', 'May', 'Mat', 'Cfg', 'VC', 'SS', 'CA', 'Cam', 'LT', 'Hol', 'Gra', 'SC', 'Gtm', 'IJ'];

// ---- small helpers -------------------------------------------------------

const store = {
  get code() { return localStorage.getItem('voces.code'); },
  set code(v) { v ? localStorage.setItem('voces.code', v) : localStorage.removeItem('voces.code'); },
  get wifiOnly() { return localStorage.getItem('voces.wifi') === 'wifi'; },
  set wifiOnly(v) { localStorage.setItem('voces.wifi', v ? 'wifi' : 'any'); },
  get done() { return new Set(JSON.parse(localStorage.getItem('voces.done') || '[]')); },
  addDone(id) { const s = this.done; s.add(id); localStorage.setItem('voces.done', JSON.stringify([...s].slice(-3000))); },
};

function toast(text, error = false) {
  const t = $('toast');
  t.textContent = text;
  t.classList.toggle('error', error);
  t.classList.add('show');
  clearTimeout(toast.timer);
  toast.timer = setTimeout(() => t.classList.remove('show'), 4000);
}

async function api(path, opts = {}) {
  const headers = { ...(opts.headers || {}) };
  if (store.code) headers['X-Voz-Code'] = store.code;
  if (opts.json !== undefined) {
    headers['Content-Type'] = 'application/json';
    opts.body = JSON.stringify(opts.json);
  }
  const r = await fetch(API + path, { ...opts, headers });
  let data = null;
  try { data = await r.json(); } catch (e) { /* empty body */ }
  if (!r.ok) {
    const err = new Error((data && typeof data.detail === 'string') ? data.detail : `Error ${r.status}`);
    err.status = r.status;
    throw err;
  }
  return data;
}

const fmt = (n, d = 0) => n.toLocaleString('es', { minimumFractionDigits: d, maximumFractionDigits: d });
const clock = (s) => `${Math.floor(s / 60)}:${String(Math.floor(s % 60)).padStart(2, '0')}`;

// ---- screens -------------------------------------------------------------

const NEEDS_CODE = new Set(['leer', 'validar', 'aporte']);
function go(name) {
  if (location.hash === '#' + name) route(); else location.hash = name;
}

const SCREENS = { inicio: showHome, antes: showConsent, leer: showRead, validar: showReview, aporte: showMine };
let after = 'leer';

function route() {
  let name = location.hash.slice(1) || 'inicio';
  if (!SCREENS[name]) name = 'inicio';
  if (NEEDS_CODE.has(name) && !store.code) {
    after = name;
    name = 'antes';
  }
  if (name !== 'leer' && recorder.stream) {
    recorder.cancel();
    reading.recording = false;
    $('r-mic').classList.remove('on');
  }
  document.querySelectorAll('.screen').forEach((s) => s.classList.toggle('hidden', s.id !== 's-' + name));
  window.scrollTo(0, 0);
  SCREENS[name]();
}

// ---- portada -------------------------------------------------------------

async function showHome() {
  let s;
  try { s = await api('/stats'); } catch (e) { $('h-line').textContent = 'No pudimos cargar las cifras.'; return; }
  $('h-hours').textContent = fmt(s.hours, 1);
  $('h-goal').textContent = s.goal_hours;
  $('h-meter').style.width = Math.min(100, 100 * s.hours / s.goal_hours) + '%';
  const names = Object.keys(s.provinces);
  const withVoice = names.filter((p) => s.provinces[p] > 0);
  $('h-line').textContent = `${fmt(s.speakers)} ${s.speakers === 1 ? 'persona' : 'personas'} de ${withVoice.length} ${withVoice.length === 1 ? 'provincia' : 'provincias'} · ${fmt(s.validated)} grabaciones validadas`;
  const max = Math.max(...Object.values(s.provinces), 1e-9);
  $('h-provs').innerHTML = '';
  names.forEach((p, i) => {
    const span = document.createElement('span');
    span.style.setProperty('--h', (s.provinces[p] / max).toFixed(2));
    span.textContent = SHORT[i];
    span.title = `${p}: ${fmt(s.provinces[p] * 60)} min`;
    $('h-provs').appendChild(span);
  });
  const missing = names.filter((p) => !s.provinces[p]);
  $('h-missing').textContent = missing.length === 0 ? 'Ya hay voces de todas las provincias.'
    : missing.length <= 4 ? `Aún sin voces: ${missing.join(', ')}.`
    : `Faltan voces de ${missing.length} provincias.`;
}

// ---- consentimiento ------------------------------------------------------

function fillPlaces() {
  const prov = $('f-province');
  if (prov.options.length > 1) return;
  Object.keys(PROVINCES).forEach((p) => prov.add(new Option(p, p)));
  prov.addEventListener('change', () => {
    const m = $('f-municipality');
    m.length = 1;
    (PROVINCES[prov.value] || []).forEach((x) => m.add(new Option(x, x)));
  });
}

function showConsent() {
  fillPlaces();
  const form = $('consent-form');
  const check = () => { $('consent-ok').disabled = ![...form.querySelectorAll('.req')].every((c) => c.checked); };
  form.onchange = check;
  check();
}

$('consent-form').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const f = new FormData(ev.target);
  const body = { adult: true, license: true, deletion: true };
  ['province', 'municipality', 'age_range', 'gender', 'abroad'].forEach((k) => { body[k] = f.get(k) || null; });
  $('consent-ok').disabled = true;
  try {
    const r = await api('/participants', { method: 'POST', json: body });
    store.code = r.code;
    store.wifiOnly = f.get('wifi') === 'wifi';
    toast(`Su código es ${r.code}. Lo encuentra en «Mi aporte».`);
    go(after);
  } catch (e) {
    toast(e.status ? e.message : 'Sin conexión. Hace falta conexión para empezar.', true);
    $('consent-ok').disabled = false;
  }
});

$('code-form').addEventListener('submit', async (ev) => {
  ev.preventDefault();
  const code = $('code-input').value.trim();
  if (!code) return;
  try {
    await fetch(API + '/participants/check', { headers: { 'X-Voz-Code': code } }).then((r) => {
      if (!r.ok) throw new Error(r.status === 401 ? 'No conocemos ese código. Revise cómo lo escribió.' : `Error ${r.status}`);
    });
    store.code = code;
    toast('Bienvenido de nuevo.');
    go(after);
  } catch (e) {
    toast(e.message.startsWith('No') ? e.message : 'Sin conexión. Inténtelo cuando tenga conexión.', true);
  }
});

// ---- cola en IndexedDB ---------------------------------------------------

const queue = {
  db: null,
  open() {
    if (this.db) return this.db;
    this.db = new Promise((ok, fail) => {
      const req = indexedDB.open('voces', 1);
      req.onupgradeneeded = () => req.result.createObjectStore('takes', { keyPath: 'id' });
      req.onsuccess = () => ok(req.result);
      req.onerror = () => fail(req.error);
    });
    return this.db;
  },
  async tx(mode, fn) {
    const db = await this.open();
    return new Promise((ok, fail) => {
      const t = db.transaction('takes', mode);
      const r = fn(t.objectStore('takes'));
      t.oncomplete = () => ok(r && r.result);
      t.onerror = () => fail(t.error);
    });
  },
  add(take) { return this.tx('readwrite', (s) => s.put(take)); },
  remove(id) { return this.tx('readwrite', (s) => s.delete(id)); },
  all() { return this.tx('readonly', (s) => s.getAll()); },
};

let backoff = 5000, draining = false;

function allowedNetwork() {
  if (!store.wifiOnly) return true;
  const c = navigator.connection;
  if (!c || !c.type) return null; // unknown: the person decides with «Subir ahora»
  return c.type === 'wifi' || c.type === 'ethernet';
}

async function showQueue() {
  const n = (await queue.all()).length;
  const net = allowedNetwork();
  $('q').classList.toggle('ok', n === 0);
  $('q-now').classList.toggle('hidden', n === 0 || net !== null);
  $('q-text').textContent = n === 0 ? 'Todo subido'
    : `${n} ${n === 1 ? 'grabación espera' : 'grabaciones esperan'} conexión · ${net === null ? 'súbalas cuando tenga wifi' : 'se subirán solas'}`;
}

async function drain(force = false) {
  if (draining || !store.code) return;
  if (!force && allowedNetwork() !== true) { showQueue(); return; }
  draining = true;
  try {
    for (const take of await queue.all()) {
      const form = new FormData();
      form.append('id', take.id);
      form.append('prompt_id', take.prompt_id);
      form.append('duration', take.duration.toFixed(2));
      form.append('audio', new File([take.blob], 'toma' + (take.mime.includes('mp4') ? '.m4a' : '.webm'), { type: take.mime }));
      try {
        await api('/clips', { method: 'POST', body: form });
        await queue.remove(take.id);
      } catch (e) {
        if (e.status && e.status >= 400 && e.status < 500 && e.status !== 429 && e.status !== 401) {
          await queue.remove(take.id); // the server will never take it
          toast(`Una grabación no se aceptó: ${e.message}`, true);
          continue;
        }
        throw e;
      }
      showQueue();
    }
    backoff = 5000;
  } catch (e) {
    backoff = Math.min(backoff * 2, 5 * 60 * 1000);
  } finally {
    draining = false;
    showQueue();
  }
  if ((await queue.all()).length) setTimeout(drain, backoff);
}

$('q-now').addEventListener('click', () => drain(true));
window.addEventListener('online', () => drain());
if (navigator.connection) navigator.connection.addEventListener('change', () => drain());

// ---- grabación -----------------------------------------------------------

// Raw voice, as the microphone gives it: echo cancellation, noise
// suppression and automatic gain all reshape the voice, and the corpus
// also trains speech synthesis.
const CONSTRAINTS = {
  audio: { echoCancellation: false, noiseSuppression: false, autoGainControl: false, channelCount: 1 },
};

const WORKLET = `
class Meter extends AudioWorkletProcessor {
  process(inputs) {
    const ch = inputs[0] && inputs[0][0];
    if (ch) {
      let sum = 0, clipped = 0;
      for (let i = 0; i < ch.length; i++) { const v = ch[i]; sum += v * v; if (v >= 0.99 || v <= -0.99) clipped++; }
      this.port.postMessage({ sum, clipped, n: ch.length });
    }
    return true;
  }
}
registerProcessor('meter', Meter);`;

function pickMime() {
  for (const m of ['audio/webm;codecs=opus', 'audio/ogg;codecs=opus', 'audio/mp4']) {
    if (window.MediaRecorder && MediaRecorder.isTypeSupported(m)) return m;
  }
  return '';
}

const recorder = {
  stream: null, ctx: null, rec: null, chunks: [], started: 0, timer: null,
  stats: null, onstop: null,

  async start() {
    if (!this.stream) this.stream = await navigator.mediaDevices.getUserMedia(CONSTRAINTS);
    if (!this.ctx) {
      this.ctx = new AudioContext();
      const url = URL.createObjectURL(new Blob([WORKLET], { type: 'text/javascript' }));
      await this.ctx.audioWorklet.addModule(url);
      const node = new AudioWorkletNode(this.ctx, 'meter');
      this.ctx.createMediaStreamSource(this.stream).connect(node);
      node.port.onmessage = (ev) => this.meter(ev.data);
    }
    await this.ctx.resume();
    this.stats = { n: 0, clipped: 0, windows: [], acc: 0, accN: 0 };
    const mime = pickMime();
    this.rec = new MediaRecorder(this.stream, mime ? { mimeType: mime, audioBitsPerSecond: 64000 } : {});
    this.chunks = [];
    this.rec.ondataavailable = (e) => e.data.size && this.chunks.push(e.data);
    this.rec.onstop = () => this.finish();
    this.rec.start();
    this.started = performance.now();
    this.timer = setInterval(() => {
      const s = (performance.now() - this.started) / 1000;
      $('r-time').textContent = clock(s) + ' / 0:30';
      if (s >= MAX_S) this.stop();
    }, 200);
  },

  meter({ sum, clipped, n }) {
    if (!this.rec || this.rec.state !== 'recording') return;
    const st = this.stats;
    st.n += n; st.clipped += clipped; st.acc += sum; st.accN += n;
    if (st.accN >= 2400) { // about 50 ms
      const rms = Math.sqrt(st.acc / st.accN);
      st.windows.push(rms);
      st.acc = 0; st.accN = 0;
      const bars = $('r-level').children, lit = Math.min(bars.length, Math.round(rms * 120));
      [...bars].forEach((b, i) => { b.style.height = (i < lit ? 6 + 22 * (1 - i / bars.length) : 6) + 'px'; });
    }
  },

  stop() {
    clearInterval(this.timer);
    if (this.rec && this.rec.state === 'recording') this.rec.stop();
  },

  cancel() {
    this.onstop = null;
    this.stop();
    if (this.stream) { this.stream.getTracks().forEach((t) => t.stop()); this.stream = null; }
    if (this.ctx) { this.ctx.close(); this.ctx = null; }
  },

  finish() {
    const duration = (performance.now() - this.started) / 1000;
    const blob = new Blob(this.chunks, { type: this.rec.mimeType || 'audio/webm' });
    const st = this.stats;
    const loudest = Math.max(0, ...st.windows);
    let problem = null;
    if (duration < MIN_S) problem = 'La grabación es muy corta. Lea la frase completa.';
    else if (loudest < SILENCE_RMS) problem = 'Casi no se oye nada. Acérquese al micrófono y hable un poco más alto.';
    else if (st.n && st.clipped / st.n > CLIPPED) problem = 'El sonido sale saturado. Aleje un poco el teléfono de la boca.';
    if (this.onstop) this.onstop({ blob, duration, mime: blob.type.split(';')[0], problem });
  },
};

// ---- leer ----------------------------------------------------------------

const reading = { prompts: [], i: 0, take: null, recording: false, audio: null };

async function loadPrompts() {
  const done = store.done;
  const got = await api('/prompts?n=10');
  reading.prompts = got.filter((p) => !done.has(p.id));
  reading.i = 0;
}

async function showRead() {
  showQueue();
  drain();
  if (reading.i >= reading.prompts.length) {
    $('r-text').textContent = 'Cargando frases…';
    try { await loadPrompts(); } catch (e) {
      if (e.status === 401) { store.code = null; go('leer'); return; }
      $('r-text').textContent = 'Hace falta conexión para traer frases nuevas. Sus grabaciones guardadas se subirán solas.';
      $('r-mic').disabled = true;
      return;
    }
  }
  renderPrompt();
}

function renderPrompt() {
  const p = reading.prompts[reading.i];
  reading.take = null;
  $('r-after').classList.add('hidden');
  $('r-time').textContent = '';
  $('r-level').hidden = true;
  if (!p) {
    $('r-text').textContent = '¡Gracias! Ya leyó todas las frases que tenemos para usted por ahora.';
    $('r-mic').disabled = true;
    $('r-step').textContent = '';
    $('r-dots').innerHTML = '';
    return;
  }
  $('r-text').textContent = p.text;
  $('r-mic').disabled = false;
  $('r-state').textContent = 'Toque el micrófono y lea la frase en voz alta. Mejor en un lugar tranquilo, sin ventilador ni televisor.';
  $('r-state').classList.remove('check-err');
  const n = reading.prompts.length;
  $('r-step').textContent = `${p.kind === 'parrafo' ? 'Párrafo' : 'Frase'} ${reading.i + 1} de ${n}`;
  $('r-dots').innerHTML = Array.from({ length: n }, (_, k) => `<i class="${k < reading.i ? 'done' : k === reading.i ? 'now' : ''}"></i>`).join('');
}

$('r-mic').addEventListener('click', async () => {
  if (reading.recording) { recorder.stop(); return; }
  stopPlayback();
  try {
    recorder.onstop = gotTake;
    await recorder.start();
  } catch (e) {
    $('r-state').textContent = 'No pudimos usar el micrófono. Revise que el navegador tenga permiso para usarlo.';
    $('r-state').classList.add('check-err');
    return;
  }
  reading.recording = true;
  $('r-mic').classList.add('on');
  $('r-mic').setAttribute('aria-label', 'Parar');
  $('r-level').hidden = false;
  $('r-after').classList.add('hidden');
  $('r-state').textContent = 'Grabando… toque de nuevo al terminar.';
  $('r-state').classList.remove('check-err');
});

function gotTake(take) {
  reading.recording = false;
  $('r-mic').classList.remove('on');
  $('r-mic').setAttribute('aria-label', 'Grabar');
  $('r-level').hidden = true;
  if (take.problem) {
    $('r-state').textContent = take.problem;
    $('r-state').classList.add('check-err');
    return;
  }
  reading.take = take;
  $('r-state').textContent = 'Escúchese si quiere. Si está bien, guárdela y siga.';
  $('r-after').classList.remove('hidden');
}

function stopPlayback() {
  if (reading.audio) { reading.audio.pause(); URL.revokeObjectURL(reading.audio.src); reading.audio = null; }
}

$('r-play').addEventListener('click', () => {
  if (!reading.take) return;
  stopPlayback();
  reading.audio = new Audio(URL.createObjectURL(reading.take.blob));
  reading.audio.play();
});

$('r-redo').addEventListener('click', () => { stopPlayback(); renderPrompt(); $('r-mic').click(); });

$('r-next').addEventListener('click', async () => {
  const p = reading.prompts[reading.i];
  const t = reading.take;
  if (!p || !t) return;
  stopPlayback();
  await queue.add({ id: crypto.randomUUID(), prompt_id: p.id, duration: t.duration, mime: t.mime, blob: t.blob, created: Date.now() });
  store.addDone(p.id);
  reading.i++;
  showQueue();
  drain();
  if (reading.i >= reading.prompts.length) showRead(); else renderPrompt();
});

$('r-skip').addEventListener('click', (ev) => {
  ev.preventDefault();
  stopPlayback();
  reading.i++;
  if (reading.i >= reading.prompts.length) showRead(); else renderPrompt();
});

$('r-report').addEventListener('click', async (ev) => {
  ev.preventDefault();
  const p = reading.prompts[reading.i];
  if (!p) return;
  try { await api(`/prompts/${p.id}/report`, { method: 'POST' }); toast('Gracias. La revisaremos.'); } catch (e) { toast('No pudimos enviar el reporte.', true); }
  $('r-skip').click();
});

// ---- validar -------------------------------------------------------------

const review = { item: null, heard: 0, count: 0 };
const audioEl = $('c-audio');

async function showReview() {
  review.item = null;
  $('c-yes').disabled = true;
  document.querySelectorAll('[data-vote]').forEach((b) => { b.disabled = b.dataset.vote === 'yes'; });
  $('c-pos').style.width = '0';
  $('c-text').textContent = 'Cargando…';
  let item;
  try { item = await api('/review'); } catch (e) {
    if (e.status === 401) { store.code = null; go('validar'); return; }
    $('c-text').textContent = 'Hace falta conexión para validar.';
    return;
  }
  $('c-box').classList.toggle('hidden', !item);
  $('c-empty').classList.toggle('hidden', !!item);
  if (!item) return;
  review.item = item;
  review.heard = 0;
  $('c-text').textContent = item.text;
  $('c-time').textContent = `0:00 / ${clock(item.duration)}`;
  audioEl.src = item.audio_url;
  $('c-wait').textContent = '«Sí» se activa al terminar de escuchar la grabación completa. «No» puede marcarlo en cuanto oiga un error.';
}

$('c-play').addEventListener('click', () => {
  if (audioEl.paused) audioEl.play(); else audioEl.pause();
});
audioEl.addEventListener('play', () => { $('c-play').textContent = '❚❚'; });
audioEl.addEventListener('pause', () => { $('c-play').textContent = '▶'; });
audioEl.addEventListener('timeupdate', () => {
  // No skipping ahead: a yes means the whole recording was heard.
  if (audioEl.currentTime > review.heard + 1.5) audioEl.currentTime = review.heard;
  review.heard = Math.max(review.heard, audioEl.currentTime);
  const d = (review.item && review.item.duration) || audioEl.duration || 1;
  $('c-pos').style.width = Math.min(100, 100 * audioEl.currentTime / d) + '%';
  $('c-time').textContent = `${clock(audioEl.currentTime)} / ${clock(d)}`;
});
audioEl.addEventListener('ended', () => {
  $('c-yes').disabled = false;
  $('c-wait').textContent = 'Ya puede responder.';
});

document.querySelectorAll('[data-vote]').forEach((b) => b.addEventListener('click', async () => {
  if (!review.item) return;
  audioEl.pause();
  document.querySelectorAll('[data-vote]').forEach((x) => { x.disabled = true; });
  try {
    await api('/votes', { method: 'POST', json: { ticket: review.item.ticket, vote: b.dataset.vote } });
    if (b.dataset.vote !== 'skip') $('c-count').textContent = ++review.count;
  } catch (e) {
    toast(e.status ? e.message : 'Sin conexión. Su voto no se guardó.', true);
  }
  showReview();
}));

// ---- mi aporte -----------------------------------------------------------

async function showMine() {
  $('m-code').textContent = store.code;
  $('m-confirm').classList.add('hidden');
  const pending = (await queue.all()).length;
  $('m-pending').textContent = pending ? `${pending} ${pending === 1 ? 'grabación espera' : 'grabaciones esperan'} conexión en este teléfono y aún no cuentan aquí.` : '';
  try {
    const me = await api('/me');
    $('m-min').textContent = fmt(me.seconds / 60, me.seconds < 600 ? 1 : 0);
    $('m-clips').textContent = fmt(me.clips);
    $('m-votes').textContent = fmt(me.votes);
    $('m-n').textContent = fmt(me.clips);
  } catch (e) {
    if (e.status === 401) { toast('Ese código ya no existe en el servidor.', true); store.code = null; go('inicio'); }
  }
}

$('m-copy').addEventListener('click', async () => {
  try { await navigator.clipboard.writeText(store.code); toast('Código copiado.'); } catch (e) { toast('Cópielo a mano: ' + store.code); }
});
$('m-del').addEventListener('click', () => $('m-confirm').classList.remove('hidden'));
$('m-cancel').addEventListener('click', () => $('m-confirm').classList.add('hidden'));
$('m-del2').addEventListener('click', async () => {
  try {
    const r = await api('/me', { method: 'DELETE' });
    for (const t of await queue.all()) await queue.remove(t.id);
    store.code = null;
    localStorage.removeItem('voces.done');
    toast(`Borramos ${r.deleted} grabaciones.`);
    go('inicio');
  } catch (e) {
    toast(e.status ? e.message : 'Hace falta conexión para borrar.', true);
  }
});

// ---- arranque ------------------------------------------------------------

window.addEventListener('hashchange', route);
route();
drain();
