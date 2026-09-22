/* Constructor de ejemplos de entrenamiento.
   Las reglas que se comprueban aquí son las mismas que valida el servidor en
   POST /api/examples. Esto es para que la interfaz explique por qué el botón
   está apagado; la comprobación que cuenta es la del servidor. */

const TAGS = ['arte', 'ciencia', 'cultura', 'deporte', 'economía',
              'historia', 'política', 'salud', 'casual', 'otros'];

const $ = (id) => document.getElementById(id);

let contact = null;
let turns = [];
let chosenTags = new Set();

/* ---------------- paso 1: consentimiento ---------------- */

const consentFields = ['name', 'institution', 'email'].map($);
const consentChecks = ['t1', 't2', 't3'].map($);

function consentReady() {
  return consentFields.every((f) => f.value.trim()) &&
         consentChecks.every((c) => c.checked);
}

function refreshConsent() { $('continue').disabled = !consentReady(); }

consentFields.forEach((f) => f.addEventListener('input', refreshConsent));
consentChecks.forEach((c) => c.addEventListener('change', refreshConsent));

$('continue').addEventListener('click', () => {
  if (!consentReady()) return;
  contact = {
    name: $('name').value.trim(),
    institution: $('institution').value.trim(),
    email: $('email').value.trim(),
  };
  $('step-intro').classList.add('hidden');
  $('step-build').classList.remove('hidden');
  $('whoami').textContent = `Enviando como ${contact.name} · ${contact.institution}`;
  $('composer').focus();
  window.scrollTo(0, 0);
});

/* ---------------- etiquetas ---------------- */

for (const tag of TAGS) {
  const b = document.createElement('button');
  b.type = 'button';
  b.className = 'tag';
  b.textContent = tag;
  b.setAttribute('aria-pressed', 'false');
  b.addEventListener('click', () => {
    if (chosenTags.has(tag)) { chosenTags.delete(tag); b.setAttribute('aria-pressed', 'false'); }
    else { chosenTags.add(tag); b.setAttribute('aria-pressed', 'true'); }
    refreshBuild();
  });
  $('tags').appendChild(b);
}

/* ---------------- turnos ---------------- */

const nextRole = () => (turns.length % 2 === 0 ? 'user' : 'assistant');

function renderTurns() {
  const box = $('turns');
  box.innerHTML = '';

  if (turns.length === 0) {
    const p = document.createElement('p');
    p.className = 'empty';
    p.textContent = 'Todavía no hay mensajes. Empiece escribiendo lo que diría el usuario.';
    box.appendChild(p);
  }

  for (const turn of turns) {
    const div = document.createElement('div');
    div.className = `turn ${turn.role}`;
    const who = document.createElement('div');
    who.className = 'who';
    who.textContent = turn.role === 'user' ? 'Usuario' : 'Cecilia';
    const said = document.createElement('div');
    said.className = 'said';
    said.textContent = turn.content;   // textContent, no innerHTML: nada de lo que escriban se interpreta
    div.append(who, said);
    box.appendChild(div);
  }

  $('turn-controls').classList.toggle('hidden', turns.length === 0);
  $('composer-label').textContent = nextRole() === 'user'
    ? 'Escriba el mensaje del usuario'
    : 'Escriba la respuesta de Cecilia';
}

function addTurn() {
  const text = $('composer').value.trim();
  if (!text) return;
  turns.push({ role: nextRole(), content: text });
  $('composer').value = '';
  $('composer').focus();
  renderTurns();
  refreshBuild();
}

$('add').addEventListener('click', addTurn);
$('composer').addEventListener('keydown', (e) => {
  if (e.key === 'Enter' && (e.ctrlKey || e.metaKey)) { e.preventDefault(); addTurn(); }
});
$('undo').addEventListener('click', () => { turns.pop(); renderTurns(); refreshBuild(); });
$('clear').addEventListener('click', () => { turns = []; renderTurns(); refreshBuild(); });

/* ---------------- estado del botón de envío ---------------- */

function blockingReason() {
  if (turns.length < 2) return 'Hacen falta al menos un mensaje del usuario y una respuesta.';
  if (turns.length % 2 !== 0) return 'Falta la respuesta de Cecilia al último mensaje.';
  if (chosenTags.size === 0) return 'Seleccione al menos una etiqueta.';
  return '';
}

function refreshBuild() {
  const reason = blockingReason();
  $('submit').disabled = reason !== '';
  $('why').textContent = reason;
}

/* ---------------- envío ---------------- */

let sending = false;

$('submit').addEventListener('click', async () => {
  if (sending || blockingReason()) return;
  sending = true;
  $('submit').disabled = true;

  try {
    const res = await fetch('/api/examples', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        contact_info: contact,
        example_type: $('example_type').value,
        tags: [...chosenTags],
        context: $('context').value.trim(),
        messages: turns,
      }),
    });

    if (!res.ok) throw new Error(`el servidor respondió ${res.status}`);

    turns = [];
    chosenTags.clear();
    document.querySelectorAll('.tag').forEach((b) => b.setAttribute('aria-pressed', 'false'));
    $('context').value = '';
    renderTurns();
    toast('Ejemplo enviado. Muchas gracias — puede escribir otro.');
  } catch (err) {
    toast(`No se pudo enviar: ${err.message}`, true);
  } finally {
    sending = false;
    refreshBuild();
  }
});

/* ---------------- aviso flotante ---------------- */

let toastTimer = null;

function toast(text, isError = false) {
  const el = $('toast');
  el.textContent = text;
  el.classList.toggle('error', isError);
  el.classList.add('show');
  clearTimeout(toastTimer);
  toastTimer = setTimeout(() => el.classList.remove('show'), 4000);
}

renderTurns();
refreshBuild();
refreshConsent();
