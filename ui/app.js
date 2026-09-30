const state = {
  genesis: [],
  relations: [],
  events: []
};

const $ = (id) => document.getElementById(id);

function nowInputValue() {
  const date = new Date();
  const local = new Date(date.getTime() - date.getTimezoneOffset() * 60000);
  return local.toISOString().slice(0, 16);
}

function text(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

async function digest(payload) {
  const bytes = new TextEncoder().encode(JSON.stringify(payload));
  const hash = await crypto.subtle.digest("SHA-256", bytes);
  return [...new Uint8Array(hash)]
    .map((byte) => byte.toString(16).padStart(2, "0"))
    .join("");
}

function addEvent(kind, message) {
  state.events.unshift({ kind, message, createdAt: new Date().toISOString() });
  render();
}

async function createGenesis(subject, createdAt) {
  const payload = { created_at: createdAt, subject, version: 1 };
  const id = await digest(payload);
  state.genesis.push({ id, subject, createdAt, version: 1 });
  addEvent("GENESIS", `Created ${subject}`);
}

async function createRelation(sourceId, targetId, kind, createdAt) {
  const payload = {
    created_at: createdAt,
    kind,
    source_id: sourceId,
    target_id: targetId,
    version: 1
  };
  const id = await digest(payload);
  state.relations.push({ id, sourceId, targetId, kind, createdAt, version: 1 });
  addEvent("RELATION", `Created ${kind} relation`);
}

function renderGenesisOptions() {
  const options = state.genesis
    .map((item) => `<option value="${text(item.id)}">${text(item.subject)}</option>`)
    .join("");

  $("relation-source").innerHTML = options;
  $("relation-target").innerHTML = options;
}

function renderSelectedGenesis() {
  const item = state.genesis.at(-1);
  if (!item) {
    $("selected-genesis").className = "empty-state";
    $("selected-genesis").textContent = "No Genesis selected.";
    return;
  }

  $("selected-genesis").className = "state-card";
  $("selected-genesis").innerHTML = `
    <div class="row-title">${text(item.subject)}</div>
    <div class="row-meta">version ${item.version} · ${text(item.createdAt)}</div>
    <div class="mono">${text(item.id)}</div>
  `;
}

function renderRelations() {
  if (!state.relations.length) {
    $("relation-list").className = "list empty-state";
    $("relation-list").textContent = "No relations yet.";
    return;
  }

  $("relation-list").className = "list";
  $("relation-list").innerHTML = state.relations.map((relation) => {
    const source = state.genesis.find((item) => item.id === relation.sourceId);
    const target = state.genesis.find((item) => item.id === relation.targetId);

    return `
      <div class="relation-row">
        <div class="row-title">${text(source?.subject ?? relation.sourceId)} → ${text(target?.subject ?? relation.targetId)}</div>
        <div class="row-meta">${text(relation.kind)} · ${text(relation.createdAt)}</div>
        <div class="mono">${text(relation.id)}</div>
      </div>
    `;
  }).join("");
}

function renderEvents() {
  if (!state.events.length) {
    $("event-list").className = "events empty-state";
    $("event-list").textContent = "No events yet.";
    return;
  }

  $("event-list").className = "events";
  $("event-list").innerHTML = state.events.map((event) => `
    <div class="event-row">
      <div class="row-title">${text(event.kind)}</div>
      <div class="row-meta">${text(event.message)} · ${text(event.createdAt)}</div>
    </div>
  `).join("");
}

function render() {
  $("genesis-count").textContent = state.genesis.length;
  $("relation-count").textContent = state.relations.length;
  $("event-count").textContent = state.events.length;
  renderGenesisOptions();
  renderSelectedGenesis();
  renderRelations();
  renderEvents();
}

$("genesis-created-at").value = nowInputValue();
$("relation-created-at").value = nowInputValue();

$("genesis-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const subject = $("genesis-subject").value.trim();
  const createdAt = $("genesis-created-at").value;
  if (!subject || !createdAt) return;

  await createGenesis(subject, createdAt);
  event.target.reset();
  $("genesis-created-at").value = nowInputValue();
});

$("relation-form").addEventListener("submit", async (event) => {
  event.preventDefault();

  const sourceId = $("relation-source").value;
  const targetId = $("relation-target").value;
  const kind = $("relation-kind").value.trim();
  const createdAt = $("relation-created-at").value;

  if (!sourceId || !targetId || !kind || !createdAt) return;
  if (sourceId === targetId) {
    addEvent("REJECTED", "A relation currently requires distinct source and target.");
    return;
  }

  await createRelation(sourceId, targetId, kind, createdAt);
  event.target.reset();
  $("relation-created-at").value = nowInputValue();
});

render();
