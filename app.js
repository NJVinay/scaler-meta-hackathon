/**
 * app.js — Contract Clause Analyzer UI ↔ OpenEnv Backend
 *
 * Endpoints used:
 *   POST /reset  { task_name }              → ContractObservation
 *   POST /step   { action_type, payload, reasoning } → [obs, reward, done]
 *   GET  /state                             → ContractState
 *   GET  /health                            → { status }
 */

const API = window.location.origin; // same origin — served by FastAPI

// ── State ────────────────────────────────────────────────────────────────────
let currentTask = "clause-classify";
let currentObs  = null;   // latest ContractObservation
let episodeLog  = [];     // { step, action, reward, feedback }

// ── DOM refs ─────────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

// ── Helpers ──────────────────────────────────────────────────────────────────
async function apiFetch(path, method = "GET", body = null) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API}${path}`, opts);
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

function riskColor(level) {
  return { low: "#4ade80", medium: "#fb923c", high: "#f87171" }[level] ?? "#9ca3af";
}

function scoreColor(s) {
  if (s >= 0.8) return "#4ade80";
  if (s >= 0.5) return "#fb923c";
  return "#f87171";
}

function scorePercent(s) { return Math.round(s * 100); }

function setStatus(msg, ok = true) {
  const el = $("status-badge");
  // Target only the text span (second child), preserve the pulse dot (first child)
  const textSpan = el.querySelector("span:last-child");
  if (textSpan) textSpan.textContent = msg;
  el.style.color = ok ? "#c2652a" : "#ef4444";
}

function showSpinner(show) {
  // CSS uses #spinner { display:none } / #spinner.show { display:inline-block }
  $("spinner").classList.toggle("show", show);
  $("analyze-btn").disabled = show;
}

// ── Render helpers ────────────────────────────────────────────────────────────
function renderObs(obs) {
  // Document ref / task label
  const taskLabels = {
    "clause-classify": "Clause Classification",
    "risk-assess":     "Risk Assessment",
    "clause-rewrite":  "Clause Rewrite",
  };
  $("doc-ref").textContent = obs.task_name;
  $("section-title").textContent = taskLabels[obs.task_name] ?? obs.task_name;

  // Clause text
  $("clause-text").textContent = obs.clause_text || "—";

  // Instructions
  $("instructions-box").textContent = obs.instructions || "";

  // Available actions → populate action selector
  const sel = $("action-select");
  sel.innerHTML = "";
  (obs.available_actions ?? []).forEach(a => {
    const opt = document.createElement("option");
    opt.value = a;
    opt.textContent = a;
    sel.appendChild(opt);
  });

  // Step progress
  $("step-counter").textContent = `Step ${obs.step_number} / ${obs.max_steps}`;

  // Feedback from last step
  if (obs.feedback) renderFeedback(obs.feedback, obs.reward ?? null, obs.done);

  // Done state
  if (obs.done) {
    $("payload-input").disabled = true;
    $("analyze-btn").disabled = true;
    $("done-banner").classList.remove("hidden");
    refreshState();
  } else {
    $("payload-input").disabled = false;
    $("analyze-btn").disabled = false;
    $("done-banner").classList.add("hidden");
  }
}

function renderFeedback(feedback, reward, done) {
  const box = $("feedback-box");
  const scoreVal = reward !== null && reward !== undefined ? reward : null;

  box.innerHTML = `
    <div class="mb-3 flex items-center justify-between">
      <span class="font-label text-xs uppercase tracking-widest text-on-surface-variant">Grader Feedback</span>
      ${scoreVal !== null ? `
        <span style="color:${scoreColor(scoreVal)}" class="font-headline text-2xl font-semibold">
          ${scorePercent(scoreVal)}<span class="text-on-surface-variant text-sm font-body font-normal">/100</span>
        </span>` : ""}
    </div>
    <p class="font-body text-sm leading-relaxed text-on-surface">${feedback}</p>
    ${done ? `<p class="mt-3 font-label text-xs text-primary font-semibold">✓ Episode complete</p>` : ""}
  `;
  box.classList.remove("hidden");
}

async function refreshState() {
  try {
    const state = await apiFetch("/state");
    const pct = scorePercent(state.cumulative_reward ?? 0);
    $("cumulative-score").textContent = `${pct}/100`;
    $("cumulative-bar").style.width = `${pct}%`;
    $("cumulative-bar").style.background = scoreColor(state.cumulative_reward ?? 0);
    $("episode-id").textContent = (state.episode_id ?? "—").slice(0, 12) + "…";
  } catch (_) { /* non-critical */ }
}

// ── Episode log ───────────────────────────────────────────────────────────────
function appendLog(step, action, payload, reward, feedback) {
  episodeLog.push({ step, action, payload, reward, feedback });
  const list = $("log-list");
  const row = document.createElement("div");
  row.className = "border-b border-outline-variant/30 py-3 text-sm font-body";
  row.innerHTML = `
    <div class="flex justify-between mb-1">
      <span class="font-semibold text-primary">Step ${step} — <em>${action}</em></span>
      ${reward !== null ? `<span style="color:${scoreColor(reward)}" class="font-semibold">${scorePercent(reward)}/100</span>` : ""}
    </div>
    <p class="text-on-surface-variant text-xs truncate">${payload.slice(0, 120)}${payload.length > 120 ? "…" : ""}</p>
    <p class="text-on-surface text-xs mt-1">${feedback}</p>
  `;
  list.prepend(row);
}

// ── Core actions ──────────────────────────────────────────────────────────────
async function startEpisode(taskName) {
  showSpinner(true);
  setStatus("Starting episode…");
  try {
    const obs = await apiFetch("/reset", "POST", { task_name: taskName });
    currentObs = obs;
    episodeLog = [];
    $("log-list").innerHTML = "";
    renderObs(obs);
    setStatus("Environment active", true);
  } catch (e) {
    setStatus(`Reset failed: ${e.message}`, false);
  } finally {
    showSpinner(false);
  }
}

async function submitStep() {
  const payload  = $("payload-input").value.trim();
  const reasoning = $("reasoning-input").value.trim();
  const actionType = $("action-select").value;

  if (!payload) { alert("Enter your response before submitting."); return; }

  showSpinner(true);
  setStatus("Processing step…");
  try {
    // OpenEnv returns [obs, reward, done] — Gymnasium-style tuple
    const result = await apiFetch("/step", "POST", {
      action_type: actionType,
      payload,
      reasoning,
    });

    // Handle both tuple array and direct obs object
    const obs    = Array.isArray(result) ? result[0] : result;
    const reward = Array.isArray(result) ? result[1] : obs.reward;
    const done   = Array.isArray(result) ? result[2] : obs.done;

    obs.reward = reward;
    obs.done   = done;
    currentObs = obs;

    appendLog(obs.step_number, actionType, payload, reward, obs.feedback ?? "");
    renderObs(obs);
    $("payload-input").value = "";
    $("reasoning-input").value = "";
    setStatus(done ? "Episode complete" : "Environment active", true);
  } catch (e) {
    setStatus(`Step failed: ${e.message}`, false);
  } finally {
    showSpinner(false);
  }
}

// ── Nav: task switching ───────────────────────────────────────────────────────
document.querySelectorAll("[data-task]").forEach(link => {
  link.addEventListener("click", e => {
    e.preventDefault();
    const task = link.dataset.task;
    currentTask = task;

    // Update active styles
    document.querySelectorAll("[data-task]").forEach(l => {
      l.classList.remove("bg-secondary-container/20", "text-primary", "border-l-2", "border-primary", "font-bold", "translate-x-1");
      l.classList.add("text-on-surface-variant", "opacity-70");
    });
    link.classList.add("bg-secondary-container/20", "text-primary", "border-l-2", "border-primary", "font-bold", "translate-x-1");
    link.classList.remove("text-on-surface-variant", "opacity-70");

    startEpisode(task);
  });
});

// ── Analyze button ────────────────────────────────────────────────────────────
$("analyze-btn").addEventListener("click", () => {
  if (!currentObs) { startEpisode(currentTask); }
  else { submitStep(); }
});

// ── Header CTA ───────────────────────────────────────────────────────────────
$("new-doc-btn").addEventListener("click", () => startEpisode(currentTask));

// ── Restart button (in done-banner) ──────────────────────────────────────────
$("restart-btn").addEventListener("click", () => startEpisode(currentTask));

// ── Clear button ─────────────────────────────────────────────────────────────
$("clear-btn").addEventListener("click", () => {
  $("payload-input").value = "";
  $("reasoning-input").value = "";
});

// ── Expose globals needed by any remaining inline handlers ───────────────────
window.startEpisode = startEpisode;
window.currentTask  = currentTask;

// ── Health check then auto-start ──────────────────────────────────────────────
(async () => {
  try {
    await apiFetch("/health");
    setStatus("Environment active", true);
    await startEpisode(currentTask);
  } catch {
    setStatus("Backend offline", false);
    $("clause-text").textContent = "Could not reach backend. Is the server running?";
  }
})();
