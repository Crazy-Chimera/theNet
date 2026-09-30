const state = {
  genesis: [],
  relations: [],
  closures: [],
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

function addEvent(kind, message) {
  state.events.unshift({ kind, message, createdAt: new Date().toISOString() });
  render();
}

async function api(path, payload) {
  const response = await fetch(path, {
    method: "POST",
    headers: {"Content-Type": "application/json"},
    body: JSON.stringify(payload)
  });
  const data = await response.json();
  if (!response.ok) throw new Error(data.error || "request failed");
  return data;
}

async function loadState() {
  const response = await fetch("/v1/state", {cache: "no-store"});
  if (!response.ok) throw new Error("state unavailable");
  const data = await response.json();
  state.genesis = data.genesis || [];
  state.relations = data.relations || [];
  state.closures = data.closures || [];
  state.events = data.events || [];
  render();
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
    <div class="row-meta">version ${item.version} · ${text(item.created_at)}</div>
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
    const source = state.genesis.find((item) => item.id === relation.source_id);
    const target = state.genesis.find((item) => item.id === relation.target_id);

    return `
      <div class="relation-row">
        <div class="row-title">${text(source?.subject ?? relation.source_id)} → ${text(target?.subject ?? relation.target_id)}</div>
        <div class="row-meta">${text(relation.kind)} · ${text(relation.created_at)}</div>
        <div class="mono">${text(relation.id)}</div>
      </div>
    `;
  }).join("");
}

function renderClosures() {
  const item = state.closures.at(-1);
  if (!item) {
    $("closure-result").className = "empty-state";
    $("closure-result").textContent = "No Agent Ω closure yet.";
    return;
  }

  $("closure-result").className = "state-card";
  $("closure-result").innerHTML = `
    <div class="row-title">Agent Ω Genesis Closure</div>
    <div class="row-meta">Σ / ΙΩΤΑ closure verified in deterministic runtime</div>
    <div class="mono">agent_state: ${text(item.agent_state.id)}</div>
    <div class="mono">ΙΩΤΑ: ${text(item.iota.id)}</div>
  `;
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
      <div class="row-meta">${text(event.message)}</div>
    </div>
  `).join("");
}

function render() {
  $("genesis-count").textContent = state.genesis.length;
  $("relation-count").textContent = state.relations.length;
  $("event-count").textContent = state.events.length;
  $("closure-count").textContent = state.closures.length;
  renderGenesisOptions();
  renderSelectedGenesis();
  renderRelations();
  renderClosures();
  renderEvents();
}

$("genesis-created-at").value = nowInputValue();
$("relation-created-at").value = nowInputValue();
$("closure-created-at").value = nowInputValue();

$("genesis-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/v1/genesis", {
      subject: $("genesis-subject").value.trim(),
      created_at: $("genesis-created-at").value
    });
    event.target.reset();
    $("genesis-created-at").value = nowInputValue();
    await loadState();
  } catch (error) {
    addEvent("ERROR", error.message);
  }
});

$("relation-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    const sourceId = $("relation-source").value;
    const targetId = $("relation-target").value;
    if (!sourceId || !targetId || sourceId === targetId) {
      throw new Error("Relation requires distinct source and target.");
    }
    await api("/v1/relations", {
      source_id: sourceId,
      target_id: targetId,
      kind: $("relation-kind").value.trim(),
      created_at: $("relation-created-at").value
    });
    event.target.reset();
    $("relation-created-at").value = nowInputValue();
    await loadState();
  } catch (error) {
    addEvent("ERROR", error.message);
  }
});

$("closure-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  try {
    await api("/v1/closure", {
      source_subject: $("closure-source").value.trim(),
      target_subject: $("closure-target").value.trim(),
      relation_kind: $("closure-kind").value.trim(),
      proposal_text: $("closure-proposal").value.trim(),
      evidence: $("closure-evidence").value.trim(),
      expression_id: $("closure-expression").value.trim(),
      created_at: $("closure-created-at").value
    });
    event.target.reset();
    $("closure-created-at").value = nowInputValue();
    await loadState();
  } catch (error) {
    addEvent("ERROR", error.message);
  }
});

loadState().catch((error) => addEvent("ERROR", error.message));
