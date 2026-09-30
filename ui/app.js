const state = {
  genesis: [],
  relations: [],
  closures: [],
  events: [],
  control: null
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



function renderAudit(cycle) {
  const target = $("audit-detail");
  const audit = cycle.audit;
  if (!audit) {
    target.className = "audit-detail empty-state";
    target.textContent = "No audit record returned for this cycle.";
    return;
  }
  target.className = "audit-detail";
  const rows = [
    ["Proposal", cycle.proposal_id],
    ["Verification", audit.verification_ids.join(", ")],
    ["Consensus", audit.consensus_id],
    ["Convergence", audit.convergence_id],
    ["Execution", audit.execution_id],
    ["Commit", audit.commit_id],
    ["Relational Utility", audit.utility_id],
    ["Ω-Credit", audit.credit_id],
    ["Memory", audit.memory_id],
    ["Memory before → after", audit.memory_before_id + " → " + audit.memory_after_id],
    ["Compute before → after", audit.compute_before_id + " → " + audit.compute_after_id],
    ["Next state", audit.state_id]
  ];
  target.innerHTML = '<div class="panel-heading"><div><p class="eyebrow">AUDIT</p><h3>Cycle ' +
    cycle.index + ' evidence chain</h3></div><span class="tag tag-ok">IMMUTABLE IDS</span></div>' +
    '<div class="audit-chain">' + rows.map(function(row) {
      return '<div><small>' + text(row[0]) + '</small><code>' + text(row[1]) + '</code></div>';
    }).join("") + '</div>';
}

function formatNumber(value, digits = 2) {
  return Number(value).toFixed(digits);
}

function renderControl() {
  const control = state.control;
  const metrics = $("f10-metrics");
  const feedback = $("feedback-state");
  const cycles = $("cycle-list");
  const status = $("control-status");

  if (!control) return;

  status.textContent = control.all_converged ? "CONVERGED" : "CHECK";
  status.className = "tag " + (control.all_converged ? "tag-ok" : "tag-warn");

  const latest = control.cycles[control.cycles.length - 1];
  metrics.className = "metric-grid";
  metrics.innerHTML = [
    ["K", latest.metrics.k, "> 0.80"],
    ["C", latest.metrics.c, "< 0.30"],
    ["R", latest.metrics.r, "> 5"],
    ["Φ", latest.metrics.phi, "> 0.70"]
  ].map(function(item) {
    return '<div class="metric compact"><span>' + item[0] + '</span><strong>' +
      formatNumber(item[1]) + '</strong><small>' + item[2] + '</small></div>';
  }).join("");

  const allocation = control.allocation;
  const improved = control.cycles.find(function(cycle) { return cycle.learning.verified_improvement; });
  feedback.className = "feedback";
  feedback.innerHTML =
    '<div class="feedback-flow"><span>Verified improvement</span><b>→</b><span>Ω-Credit</span><b>→</b>' +
    '<span>+' + formatNumber(allocation.improvement_bonus * 100, 0) + '% weight</span><b>→</b><span>next resources</span></div>' +
    '<div class="feedback-values"><div><small>Improving cycle</small><strong>' +
    (improved ? "#" + improved.index : "—") + '</strong></div><div><small>Memory budget</small><strong>' +
    formatNumber(allocation.total_memory) + '</strong></div><div><small>Compute budget</small><strong>' +
    formatNumber(allocation.total_compute) + '</strong></div></div>';

  cycles.className = "cycle-list";
  cycles.innerHTML = control.cycles.map(function(cycle) {
    return '<button class="cycle-card cycle-select" data-cycle="' + cycle.index + '"><div class="cycle-head"><strong>Cycle ' + cycle.index +
      '</strong><span class="tag ' + (cycle.learning.verified_improvement ? "tag-ok" : "") + '">' +
      (cycle.learning.verified_improvement ? "VERIFIED IMPROVEMENT" : (cycle.metrics.converged ? "CONVERGED" : "CHECK")) +
      '</span></div><div class="cycle-grid">' +
      '<div><small>Proposal</small><strong>' + text(cycle.proposal) + '</strong><code>' + text(cycle.proposal_id) + '</code></div>' +
      '<div><small>Evidence</small><strong>Memory dependency: ' + (cycle.learning.memory_dependency ? "yes" : "no") +
      '</strong><code>' + text(cycle.parent_memory_id || "—") + '</code></div>' +
      '<div><small>Outcome / utility</small><strong>' + formatNumber(cycle.utility) + '</strong><code>' +
      text(cycle.outcome_id) + '</code></div>' +
      '<div><small>Ω-Credit</small><strong>' + formatNumber(cycle.omega_credit) + '</strong><code>state v' +
      control.state_versions[cycle.index - 1] + '</code></div></div></div></button>';
  }).join("");
  document.querySelectorAll(".cycle-select").forEach(function(button) {
    button.addEventListener("click", function() {
      const cycle = control.cycles.find(function(item) {
        return item.index === Number(button.dataset.cycle);
      });
      if (cycle) renderAudit(cycle);
    });
  });
  renderAudit(control.cycles[control.cycles.length - 1]);
}

async function runControlDemo() {
  const button = $("run-control-demo");
  button.disabled = true;
  button.textContent = "Running…";
  try {
    const response = await fetch("/v1/control/demo", {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: "{}"
    });
    const data = await response.json();
    if (!response.ok) throw new Error(data.error || "Control Room demo failed");
    state.control = data;
    renderControl();
  } catch (error) {
    addEvent("ERROR", error.message);
  } finally {
    button.disabled = false;
    button.textContent = "Run 3-cycle demo";
  }
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



function inspectNode(type, id, meta = {}) {
  const target = $("node-inspector");
  target.className = "node-inspector";
  const refs = Object.entries(meta.refs || {}).map(function(entry) {
    return '<div><small>' + text(entry[0]) + '</small><code>' + text(entry[1]) + '</code></div>';
  }).join("");
  target.innerHTML =
    '<div class="panel-heading"><div><p class="eyebrow">NODE INSPECTOR</p><h3>' +
    text(type) + '</h3></div><span class="tag tag-ok">RUNTIME ID</span></div>' +
    '<div class="inspector-grid">' +
    '<div><small>ID</small><code>' + text(id) + '</code></div>' +
    '<div><small>TYPE</small><strong>' + text(type) + '</strong></div>' +
    '<div><small>LABEL</small><strong>' + text(meta.label || "—") + '</strong></div>' +
    '</div>' +
    (refs ? '<div class="inspector-refs">' + refs + '</div>' : '');
}

function renderGraphs() {
  const memory = $("memory-graph");
  const agents = $("agent-graph");

  if (state.control?.cycles?.length) {
    const cycles = state.control.cycles;
    memory.className = "evidence-graph";
    memory.innerHTML = cycles.map(function(cycle, index) {
      const previous = index === 0 ? "GENESIS" : cycles[index - 1].audit.memory_id;
      return '<div class="graph-row">' +
        '<button type="button" class="graph-node graph-click root" data-inspect-type="PARENT MEMORY" data-inspect-id="' + text(previous) + '"><small>PARENT MEMORY</small><code>' + text(previous) + '</code></button>' +
        '<span class="graph-arrow">→</span>' +
        '<button type="button" class="graph-node graph-click" data-inspect-type="PROPOSAL" data-inspect-id="' + text(cycle.proposal_id) + '"><small>PROPOSAL · CYCLE ' + cycle.index + '</small><code>' + text(cycle.proposal_id) + '</code></button>' +
        '<span class="graph-arrow">→</span>' +
        '<button type="button" class="graph-node graph-click" data-inspect-type="MEMORY" data-inspect-id="' + text(cycle.audit.memory_id) + '" data-inspect-label="cycle ' + cycle.index + '"><small>OUTCOME → MEMORY</small><code>' + text(cycle.audit.memory_id) + '</code></button>' +
        '<span class="graph-arrow">→</span>' +
        '<button type="button" class="graph-node graph-click" data-inspect-type="NEXT STATE" data-inspect-id="' + text(cycle.audit.state_id) + '"><small>NEXT STATE</small><code>' + text(cycle.audit.state_id) + '</code></button>' +
        '</div>';
    }).join("");
  } else {
    memory.className = "evidence-graph empty-state";
    memory.textContent = "Run a recursive cycle to build the memory lineage.";
  }

  if (state.relations.length) {
    agents.className = "evidence-graph";
    agents.innerHTML = state.relations.map(function(relation) {
      const source = state.genesis.find(function(item) { return item.id === relation.source_id; });
      const target = state.genesis.find(function(item) { return item.id === relation.target_id; });
      return '<div class="graph-row">' +
        '<button type="button" class="graph-node graph-click" data-inspect-type="AGENT" data-inspect-id="' + text(relation.source_id) + '" data-inspect-label="' + text(source?.subject ?? relation.source_id) + '"><small>SOURCE</small><strong>' + text(source?.subject ?? relation.source_id) + '</strong><code>' + text(relation.source_id) + '</code></button>' +
        '<span class="graph-arrow">→</span>' +
        '<button type="button" class="graph-node graph-click" data-inspect-type="AGENT" data-inspect-id="' + text(relation.target_id) + '" data-inspect-label="' + text(target?.subject ?? relation.target_id) + '"><small>' + text(relation.kind) + '</small><strong>' + text(target?.subject ?? relation.target_id) + '</strong><code>' + text(relation.target_id) + '</code></button>' +
        '</div>';
    }).join("");
  } else {
    agents.className = "evidence-graph empty-state";
    agents.textContent = "No runtime relations yet.";
  }

  document.querySelectorAll(".graph-click").forEach(function(button) {
    button.addEventListener("click", function() {
      inspectNode(button.dataset.inspectType, button.dataset.inspectId, {
        label: button.dataset.inspectLabel,
        refs: { "selected_from": button.dataset.inspectType }
      });
    });
  });
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
  renderControl();
  renderGraphs();
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

$("run-control-demo").addEventListener("click", runControlDemo);
