const API = "http://127.0.0.1:8765";
const TOKEN = "dev-token";

function headers() {
  return { "X-Sovereign-Token": TOKEN };
}

function setStatus(id, text, kind) {
  const el = document.getElementById(id);
  el.textContent = text;
  el.className = "status" + (kind ? " " + kind : "");
}

async function fetchJSON(path, opts = {}) {
  const r = await fetch(API + path, {
    ...opts,
    headers: { ...headers(), ...(opts.headers || {}) },
  });
  const body = await r.json().catch(() => ({}));
  if (!r.ok) throw new Error(body?.error?.reason || `HTTP ${r.status}`);
  return body;
}

async function checkHealth() {
  try {
    const d = await fetchJSON("/api/health");
    setStatus("health-status", `up — ${d.service} ${d.version}`, "ok");
  } catch (e) {
    setStatus("health-status", `down — ${e.message}`, "fail");
  }
}

async function runClassify() {
  const btn = document.getElementById("run-classify");
  const corpus = document.getElementById("corpus").value;
  btn.disabled = true;
  try {
    const d = await fetchJSON(`/api/classify?corpus=${encodeURIComponent(corpus)}`);
    const tbody = document.querySelector("#classify-table tbody");
    tbody.innerHTML = "";
    for (const [regime, count] of Object.entries(d.distribution)) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td class="regime-${regime}">${regime}</td><td>${count}</td>`;
      tbody.appendChild(tr);
    }
  } catch (e) {
    alert(`classify: ${e.message}`);
  } finally {
    btn.disabled = false;
  }
}

async function runPipe() {
  const btn = document.getElementById("run-pipe");
  btn.disabled = true;
  try {
    const d = await fetchJSON("/api/pipe", { method: "POST" });
    const tbody = document.querySelector("#pipe-table tbody");
    tbody.innerHTML = "";
    for (const s of d.stages) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${s.name}</td><td class="state-${s.passed ? "PASS" : "FAIL"}">${s.passed ? "PASS" : "FAIL"}</td><td>${s.reason || ""}</td>`;
      tbody.appendChild(tr);
    }
  } catch (e) {
    alert(`pipe: ${e.message}`);
  } finally {
    btn.disabled = false;
  }
}

async function loadStandards() {
  const btn = document.getElementById("load-standards");
  btn.disabled = true;
  try {
    const d = await fetchJSON("/api/standards");
    const tbody = document.querySelector("#standards-table tbody");
    tbody.innerHTML = "";
    for (const a of d.generated) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${a}</td><td class="state-PASS">present</td>`;
      tbody.appendChild(tr);
    }
    for (const o of d.omitted) {
      const tr = document.createElement("tr");
      tr.innerHTML = `<td>${o}</td><td class="state-FAIL">omitted</td>`;
      tbody.appendChild(tr);
    }
  } catch (e) {
    alert(`standards: ${e.message}`);
  } finally {
    btn.disabled = false;
  }
}

document.getElementById("run-classify").addEventListener("click", runClassify);
document.getElementById("run-pipe").addEventListener("click", runPipe);
document.getElementById("load-standards").addEventListener("click", loadStandards);
checkHealth();
