/**
 * app.js — Contract Clause Analyzer UI ↔ OpenEnv Backend
 *
 * Wire format (from openenv.core.env_server):
 *
 *   POST /reset  body: { task_name?, seed?, episode_id? }
 *   Response:    { observation: { task_name, clause_text, instructions, available_actions,
 *                                 feedback, step_number, max_steps },
 *                  reward: float|null, done: bool }
 *
 *   POST /step   body: { action: { action_type, payload, reasoning } }
 *   Response:    { observation: { ... }, reward: float|null, done: bool }
 *
 *   GET /state   Response: { episode_id, step_count, task_name, current_clause_index,
 *                            total_clauses, cumulative_reward, is_done, action_history }
 *
 *   GET /health  Response: { status: "healthy" }
 */

const API = window.location.origin;

// ── State ────────────────────────────────────────────────────────────────────
let currentTask = "clause-classify";
let currentObs  = null;
let episodeLog  = [];

// ── DOM shortcut ─────────────────────────────────────────────────────────────
const $ = id => document.getElementById(id);

// ── API helper ───────────────────────────────────────────────────────────────
async function apiFetch(path, method = "GET", body = null) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(`${API}${path}`, opts);
  if (!res.ok) throw new Error(`${res.status} ${await res.text()}`);
  return res.json();
}

// ── Color helpers ────────────────────────────────────────────────────────────
function scoreColor(s) {
  if (s >= 0.8) return "#16a34a";
  if (s >= 0.5) return "#c2652a";
  return "#c0392b";
}
function scoreColorBg(s) {
  if (s >= 0.8) return "rgba(22,163,74,0.08)";
  if (s >= 0.5) return "rgba(194,101,42,0.08)";
  return "rgba(192,57,43,0.08)";
}
function scorePercent(s) { return Math.round(s * 100); }
function scoreGrade(s) {
  if (s >= 0.9) return "Excellent";
  if (s >= 0.7) return "Good";
  if (s >= 0.5) return "Fair";
  if (s >= 0.3) return "Partial";
  return "Poor";
}

// ── Toast ────────────────────────────────────────────────────────────────────
function showToast(msg, type = "info") {
  const colors = {
    success: "bg-success-container text-success border-success/20",
    error:   "bg-error-container text-error border-error/20",
    info:    "bg-surface-container-high text-on-surface border-outline-variant/30",
  };
  const icons = { success: "check_circle", error: "error", info: "info" };
  const container = $("toast-container");
  const el = document.createElement("div");
  el.className = `toast pointer-events-auto flex items-center space-x-3 px-5 py-3.5 rounded-2xl border shadow-warm-md font-label text-sm font-semibold ${colors[type] ?? colors.info}`;
  el.innerHTML = `
    <span class="material-symbols-outlined text-lg filled">${icons[type] ?? icons.info}</span>
    <span>${msg}</span>`;
  container.appendChild(el);
  requestAnimationFrame(() => el.classList.add("show"));
  setTimeout(() => {
    el.classList.remove("show");
    setTimeout(() => el.remove(), 400);
  }, 3500);
}

// ── Status badge ─────────────────────────────────────────────────────────────
function setStatus(msg, ok = true) {
  const el = $("status-badge");
  const textSpan = el.querySelector("span:last-child");
  const dot = el.querySelector("span:first-child");
  if (textSpan) textSpan.textContent = msg;
  if (dot) dot.style.background = ok ? "#16a34a" : "#c0392b";
  el.style.color = ok ? "#3a302a" : "#c0392b";
}

function showSpinner(show) {
  $("spinner").classList.toggle("show", show);
  $("analyze-btn").disabled = show;
}

// ── Step progress dots ───────────────────────────────────────────────────────
function renderStepProgress(current, max) {
  const container = $("step-progress");
  container.innerHTML = "";
  for (let i = 0; i < max; i++) {
    if (i > 0) {
      const line = document.createElement("div");
      line.className = `step-line ${i < current ? "completed" : "upcoming"}`;
      container.appendChild(line);
    }
    const dot = document.createElement("div");
    dot.className = `step-dot ${i < current ? "completed" : i === current ? "current" : "upcoming"}`;
    dot.title = `Step ${i + 1}`;
    container.appendChild(dot);
  }
  $("step-counter").textContent = `Step ${current} / ${max}`;
}

// ── Parse OpenEnv response ───────────────────────────────────────────────────
// Both /reset and /step return: { observation: {...}, reward, done }
function parseEnvResponse(result) {
  const obsData = result.observation ?? result;
  return {
    task_name:         obsData.task_name        ?? "",
    clause_text:       obsData.clause_text      ?? "",
    instructions:      obsData.instructions     ?? "",
    available_actions: obsData.available_actions ?? [],
    feedback:          obsData.feedback          ?? "",
    step_number:       obsData.step_number       ?? 0,
    max_steps:         obsData.max_steps         ?? 1,
    reward:            result.reward             ?? null,
    done:              result.done               ?? false,
  };
}

// ── Render observation ───────────────────────────────────────────────────────
function renderObs(obs) {
  const taskLabels = {
    "clause-classify": "Clause Classification",
    "risk-assess":     "Risk Assessment",
    "clause-rewrite":  "Clause Rewrite",
  };
  $("doc-ref").textContent = obs.task_name || "—";
  $("section-title").textContent = taskLabels[obs.task_name] ?? obs.task_name ?? "—";

  // Clause text
  const clauseEl = $("clause-text");
  clauseEl.textContent = obs.clause_text || "No clause data available.";
  clauseEl.style.opacity = obs.clause_text ? "1" : "0.4";

  // Instructions
  $("instructions-box").textContent = obs.instructions || "";

  // Action selector
  const sel = $("action-select");
  sel.innerHTML = "";
  (obs.available_actions ?? []).forEach(a => {
    const opt = document.createElement("option");
    opt.value = a;
    opt.textContent = a.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase());
    sel.appendChild(opt);
  });

  // Step progress
  renderStepProgress(obs.step_number, obs.max_steps);

  // Feedback
  if (obs.feedback) renderFeedback(obs.feedback, obs.reward, obs.done);
  else $("feedback-box").classList.add("hidden");

  // Done state
  if (obs.done) {
    $("payload-input").disabled = true;
    $("reasoning-input").disabled = true;
    $("analyze-btn").disabled = true;
    $("done-banner").classList.remove("hidden");
    refreshState();
  } else {
    $("payload-input").disabled = false;
    $("reasoning-input").disabled = false;
    $("analyze-btn").disabled = false;
    $("done-banner").classList.add("hidden");
    $("payload-input").focus();
  }

  // Hide error banner on success
  $("error-banner").classList.add("hidden");
}

// ── Render feedback ──────────────────────────────────────────────────────────
function renderFeedback(feedback, reward, done) {
  const box = $("feedback-box");
  const hasScore = reward !== null && reward !== undefined;
  const pct = hasScore ? scorePercent(reward) : 0;
  const color = hasScore ? scoreColor(reward) : "#9ca3af";
  const bgColor = hasScore ? scoreColorBg(reward) : "transparent";
  const grade = hasScore ? scoreGrade(reward) : "";

  box.innerHTML = `
    <div class="bg-surface-container-lowest p-6 md:p-8 rounded-2xl border border-outline-variant/30 shadow-warm-soft">
      <div class="flex items-start justify-between mb-5">
        <div class="flex items-center">
          <div class="w-8 h-8 rounded-lg flex items-center justify-center mr-3" style="background:${bgColor}">
            <span class="material-symbols-outlined text-lg filled" style="color:${color}">${done ? "verified" : "rate_review"}</span>
          </div>
          <div>
            <span class="font-label text-[11px] uppercase tracking-[0.1em] text-on-surface-variant font-semibold block">Grader Feedback</span>
            ${done ? '<span class="font-label text-[10px] text-primary font-semibold mt-0.5 block">Episode Complete</span>' : ""}
          </div>
        </div>
        ${hasScore ? `
          <div class="text-right">
            <div class="font-headline text-3xl font-bold leading-none" style="color:${color}">${pct}</div>
            <div class="font-label text-[10px] text-on-surface-variant mt-1">/100 · ${grade}</div>
          </div>` : ""}
      </div>
      ${hasScore ? `
        <div class="w-full bg-outline-variant/20 h-1.5 rounded-full mb-5 overflow-hidden">
          <div class="h-1.5 rounded-full transition-all duration-700" style="width:${pct}%;background:${color}"></div>
        </div>` : ""}
      <p class="font-body text-sm leading-[1.8] text-on-surface">${feedback}</p>
    </div>`;
  box.classList.remove("hidden");
}

// ── Refresh state ────────────────────────────────────────────────────────────
async function refreshState() {
  try {
    const state = await apiFetch("/state");
    const pct = scorePercent(state.cumulative_reward ?? 0);
    $("cumulative-score").textContent = `${pct}/100`;
    $("cumulative-bar").style.width = `${pct}%`;
    $("episode-id").textContent = (state.episode_id ?? "—").slice(0, 12) + "…";
    const diffLabel = { "clause-classify":"Easy","risk-assess":"Medium","clause-rewrite":"Hard" };
    $("task-difficulty").textContent = diffLabel[state.task_name] ?? "";
  } catch (_) { /* non-critical */ }
}

// ── Episode log ──────────────────────────────────────────────────────────────
function appendLog(step, action, payload, reward, feedback) {
  episodeLog.push({ step, action, payload, reward, feedback });
  const list = $("log-list");
  if (episodeLog.length === 1) list.innerHTML = "";

  const hasScore = reward !== null && reward !== undefined;
  const pct = hasScore ? scorePercent(reward) : null;
  const color = hasScore ? scoreColor(reward) : "#9ca3af";

  const row = document.createElement("div");
  row.className = "px-6 py-4 border-b border-outline-variant/15 last:border-b-0 animate-slide-up";
  row.innerHTML = `
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center space-x-2.5">
        <div class="w-6 h-6 rounded-lg flex items-center justify-center text-[11px] font-bold text-on-primary" style="background:${color}">${step}</div>
        <span class="font-label text-sm font-semibold text-on-surface">${action.replace(/_/g, " ").replace(/\b\w/g, c => c.toUpperCase())}</span>
      </div>
      ${hasScore ? `<span class="font-label text-sm font-bold" style="color:${color}">${pct}/100</span>` : ""}
    </div>
    <p class="font-body text-xs text-on-surface-variant leading-relaxed mb-1.5 line-clamp-2">${payload}</p>
    <p class="font-body text-xs text-on-surface/70 leading-relaxed">${feedback}</p>`;
  list.prepend(row);
  $("log-count").textContent = `${episodeLog.length} step${episodeLog.length > 1 ? "s" : ""}`;
}

// ── Start episode ────────────────────────────────────────────────────────────
async function startEpisode(taskName) {
  showSpinner(true);
  setStatus("Starting episode…");
  try {
    // OpenEnv ResetRequest: { seed?, episode_id?, ...extra_kwargs }
    // Our env.reset() accepts task_name as a keyword arg
    const result = await apiFetch("/reset", "POST", { task_name: taskName });
    const obs = parseEnvResponse(result);
    currentObs = obs;
    episodeLog = [];
    $("log-list").innerHTML = `
      <div class="px-6 py-8 text-center">
        <span class="material-symbols-outlined text-on-surface-variant/20 text-4xl mb-2 block">inbox</span>
        <p class="font-body text-sm text-on-surface-variant/40">No steps recorded yet.</p>
      </div>`;
    $("log-count").textContent = "0 steps";
    $("feedback-box").classList.add("hidden");
    renderObs(obs);
    setStatus("Environment active", true);
    showToast("Episode started", "success");
    await refreshState();
  } catch (e) {
    setStatus("Reset failed", false);
    showError(`Could not start episode: ${e.message}`);
    showToast("Failed to start episode", "error");
    console.error("Reset error:", e);
  } finally {
    showSpinner(false);
  }
}

// ── Submit step ──────────────────────────────────────────────────────────────
async function submitStep() {
  const payload  = $("payload-input").value.trim();
  const reasoning = $("reasoning-input").value.trim();
  const actionType = $("action-select").value;

  if (!payload) {
    showToast("Please enter a response before submitting.", "error");
    $("payload-input").focus();
    return;
  }

  showSpinner(true);
  setStatus("Processing step…");
  try {
    // OpenEnv StepRequest: { action: { ...action_fields }, timeout_s?, request_id? }
    const result = await apiFetch("/step", "POST", {
      action: {
        action_type: actionType,
        payload,
        reasoning,
      }
    });

    const obs = parseEnvResponse(result);
    currentObs = obs;

    appendLog(obs.step_number, actionType, payload, obs.reward, obs.feedback);
    renderObs(obs);
    $("payload-input").value = "";
    $("reasoning-input").value = "";

    if (obs.done) {
      setStatus("Episode complete", true);
      showToast(`Episode complete — Score: ${scorePercent(obs.reward)}/100`, obs.reward >= 0.5 ? "success" : "info");
    } else {
      setStatus("Environment active", true);
      showToast(`Step ${obs.step_number} graded: ${scorePercent(obs.reward)}/100`, "info");
    }
  } catch (e) {
    setStatus("Step failed", false);
    showToast(`Step failed: ${e.message}`, "error");
    console.error("Step error:", e);
  } finally {
    showSpinner(false);
  }
}

// ── Error display ────────────────────────────────────────────────────────────
function showError(msg) {
  $("error-banner").classList.remove("hidden");
  $("error-msg").textContent = msg;
}

// ── Mobile sidebar ───────────────────────────────────────────────────────────
function openSidebar()  { $("sidebar").classList.remove("-translate-x-full"); $("sidebar-overlay").classList.add("show"); }
function closeSidebar() { $("sidebar").classList.add("-translate-x-full");    $("sidebar-overlay").classList.remove("show"); }

// ── Copy clause ──────────────────────────────────────────────────────────────
function copyClause() {
  const text = $("clause-text").textContent;
  if (text && navigator.clipboard) {
    navigator.clipboard.writeText(text).then(() => showToast("Clause copied", "success"));
  }
}

// ── Task nav switching ───────────────────────────────────────────────────────
document.querySelectorAll("[data-task]").forEach(link => {
  link.addEventListener("click", e => {
    e.preventDefault();
    currentTask = link.dataset.task;

    document.querySelectorAll(".task-nav").forEach(l => {
      l.classList.remove("bg-primary/8", "text-primary", "border-primary", "font-bold");
      l.classList.add("text-on-surface-variant", "border-transparent");
    });
    link.classList.add("bg-primary/8", "text-primary", "border-primary", "font-bold");
    link.classList.remove("text-on-surface-variant", "border-transparent");

    startEpisode(currentTask);
    closeSidebar();
  });
});

// ── Button bindings ──────────────────────────────────────────────────────────
$("analyze-btn").addEventListener("click", () => {
  if (!currentObs) startEpisode(currentTask);
  else submitStep();
});

$("new-doc-btn").addEventListener("click",  () => startEpisode(currentTask));
$("restart-btn").addEventListener("click",  () => startEpisode(currentTask));
$("retry-btn").addEventListener("click",    () => startEpisode(currentTask));
$("clear-btn").addEventListener("click",    () => { $("payload-input").value = ""; $("reasoning-input").value = ""; $("payload-input").focus(); });
$("copy-clause-btn").addEventListener("click", copyClause);
$("menu-btn").addEventListener("click", openSidebar);
$("sidebar-overlay").addEventListener("click", closeSidebar);

// ── Keyboard shortcuts ───────────────────────────────────────────────────────
document.addEventListener("keydown", e => {
  if ((e.ctrlKey || e.metaKey) && e.key === "Enter") {
    e.preventDefault();
    if (currentObs && !currentObs.done) submitStep();
  }
  if (e.key === "Escape") closeSidebar();
});

// ── Expose globals ───────────────────────────────────────────────────────────
window.startEpisode = startEpisode;
window.currentTask = currentTask;

// ── Boot ─────────────────────────────────────────────────────────────────────
(async () => {
  try {
    await apiFetch("/health");
    setStatus("Environment active", true);
    await startEpisode(currentTask);
  } catch (e) {
    setStatus("Backend offline", false);
    showError("Could not reach the backend. Is the server running?");
    $("clause-text").textContent = "Could not reach backend.";
    $("clause-text").style.opacity = "0.4";
    console.error("Boot error:", e);
  }
})();
