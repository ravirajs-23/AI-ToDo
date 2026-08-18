const notesEl = document.getElementById("notes");
const btn = document.getElementById("organizeBtn");
const statusEl = document.getElementById("status");
const resultsEl = document.getElementById("results");
const groupsEl = document.getElementById("groups");
const sourceTag = document.getElementById("source-tag");

const PRIORITY_ORDER = { High: 0, Medium: 1, Low: 2 };

btn.addEventListener("click", async () => {
  const notes = notesEl.value.trim();
  if (!notes) {
    statusEl.textContent = "Paste some notes first.";
    return;
  }
  btn.disabled = true;
  statusEl.textContent = "Organizing...";
  resultsEl.classList.add("hidden");

  try {
    const res = await fetch("/api/organize", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ notes }),
    });
    if (!res.ok) throw new Error("Request failed: " + res.status);
    const data = await res.json();
    render(data);
  } catch (err) {
    statusEl.textContent = "Something went wrong: " + err.message;
  } finally {
    btn.disabled = false;
  }
});

function render(data) {
  const tasks = data.tasks || [];
  statusEl.textContent = tasks.length
    ? `${tasks.length} task${tasks.length === 1 ? "" : "s"} organized.`
    : "No tasks found.";

  sourceTag.textContent =
    data.source === "claude"
      ? "Organized by Claude"
      : data.source === "fallback-heuristic"
      ? "Organized by built-in rules (no API key configured)"
      : "";

  const byCategory = {};
  for (const t of tasks) {
    if (!byCategory[t.category]) byCategory[t.category] = [];
    byCategory[t.category].push(t);
  }

  groupsEl.innerHTML = "";
  const categories = Object.keys(byCategory).sort();
  for (const cat of categories) {
    const items = byCategory[cat].slice().sort(
      (a, b) => PRIORITY_ORDER[a.priority] - PRIORITY_ORDER[b.priority]
    );
    const group = document.createElement("div");
    group.className = "group";
    const h3 = document.createElement("h3");
    h3.textContent = `${cat} (${items.length})`;
    group.appendChild(h3);

    for (const t of items) {
      const row = document.createElement("div");
      row.className = "task-row";
      row.innerHTML = `
        <span class="badge ${t.priority}">${t.priority}</span>
        <span class="task-title">${escapeHtml(t.title)}${
          t.notes ? `<span class="task-notes">${escapeHtml(t.notes)}</span>` : ""
        }</span>
      `;
      group.appendChild(row);
    }
    groupsEl.appendChild(group);
  }

  resultsEl.classList.remove("hidden");
}

function escapeHtml(str) {
  const div = document.createElement("div");
  div.textContent = str;
  return div.innerHTML;
}
