const state = {
  chairs: [],
  people: [],
  lastAssignment: null,
};

let idCounter = 0;
const newId = (prefix) => `${prefix}_${idCounter++}`;

const svg = document.getElementById("canvas");
const CHAIR_R = 16;

function svgPoint(evt) {
  const r = svg.getBoundingClientRect();
  const cs = getComputedStyle(svg);
  const left = r.left + parseFloat(cs.borderLeftWidth);
  const top = r.top + parseFloat(cs.borderTopWidth);
  const w = r.width - parseFloat(cs.borderLeftWidth) - parseFloat(cs.borderRightWidth);
  const h = r.height - parseFloat(cs.borderTopWidth) - parseFloat(cs.borderBottomWidth);
  const vb = svg.viewBox.baseVal;
  const scale = Math.min(w / vb.width, h / vb.height);
  const offsetX = (w - vb.width * scale) / 2;
  const offsetY = (h - vb.height * scale) / 2;
  const x = (evt.clientX - left - offsetX) / scale;
  const y = (evt.clientY - top - offsetY) / scale;
  return {
    x: Math.min(vb.width - CHAIR_R, Math.max(CHAIR_R, x)),
    y: Math.min(vb.height - CHAIR_R, Math.max(CHAIR_R, y)),
  };
}

svg.addEventListener("click", (evt) => {

  if (evt.target !== svg) return;
  const { x, y } = svgPoint(evt);
  state.chairs.push({ id: newId("chair"), x, y });
  renderCanvas();
  renderPeople();
});

let dragChair = null;

svg.addEventListener("pointerdown", (evt) => {
  const chairId = evt.target.dataset.chairId;
  if (!chairId) return;
  dragChair = state.chairs.find((c) => c.id === chairId);
});

svg.addEventListener("pointermove", (evt) => {
  if (!dragChair) return;
  const p = svgPoint(evt);
  dragChair.x = p.x;
  dragChair.y = p.y;
  renderCanvas();
});

window.addEventListener("pointerup", () => { dragChair = null; });

function renderCanvas() {
  svg.innerHTML = "";
  for (const chair of state.chairs) {
    const g = document.createElementNS("http://www.w3.org/2000/svg", "g");

    const rect = document.createElementNS("http://www.w3.org/2000/svg", "rect");
    const size = CHAIR_R * 2;
    rect.setAttribute("x", chair.x - CHAIR_R);
    rect.setAttribute("y", chair.y - CHAIR_R);
    rect.setAttribute("width", size);
    rect.setAttribute("height", size);
    rect.setAttribute("rx", 4);
    rect.setAttribute("class", "chair-circle");
    rect.dataset.chairId = chair.id;

    const personId = state.lastAssignment ? state.lastAssignment[chair.id] : null;
    const person = personId ? state.people.find((p) => p.id === personId) : null;

    const label = document.createElementNS("http://www.w3.org/2000/svg", "text");
    label.setAttribute("x", chair.x);
    label.setAttribute("y", chair.y + CHAIR_R + 14);
    label.setAttribute("class", "chair-label");
    label.textContent = person ? person.name : "";

    rect.addEventListener("contextmenu", (evt) => {
      evt.preventDefault();
      state.chairs = state.chairs.filter((c) => c.id !== chair.id);
      renderCanvas();
    });

    g.appendChild(rect);
    g.appendChild(label);
    svg.appendChild(g);
  }
}

const peopleListEl = document.getElementById("people-list");

document.getElementById("add-person-btn").addEventListener("click", () => {
  const input = document.getElementById("new-person-name");
  const name = input.value.trim();
  if (!name) return;
  state.people.push({ id: newId("person"), name, desired: [], avoid: [], position_mode: "keine" });
  input.value = "";
  renderPeople();
});

function toggleTag(person, otherId, listName) {
  const otherList = listName === "desired" ? "avoid" : "desired";
  person[otherList] = person[otherList].filter((id) => id !== otherId);
  if (person[listName].includes(otherId)) {
    person[listName] = person[listName].filter((id) => id !== otherId);
  } else {
    person[listName].push(otherId);
  }
  renderPeople();
}

function renderPeople() {
  peopleListEl.innerHTML = "";
  for (const person of state.people) {
    const card = document.createElement("div");
    card.className = "person-card";

    const nameRow = document.createElement("div");
    nameRow.className = "row";
    nameRow.innerHTML = `<strong>${person.name}</strong>`;
    const delBtn = document.createElement("button");
    delBtn.className = "delete-btn";
    delBtn.textContent = "Entfernen";
    delBtn.addEventListener("click", () => {
      state.people = state.people.filter((p) => p.id !== person.id);
      for (const p of state.people) {
        p.desired = p.desired.filter((id) => id !== person.id);
        p.avoid = p.avoid.filter((id) => id !== person.id);
      }
      renderPeople();
    });
    nameRow.appendChild(delBtn);
    card.appendChild(nameRow);

    const posRow = document.createElement("div");
    posRow.className = "row";
    posRow.innerHTML = `<span class="label">Position:</span>`;
    const select = document.createElement("select");
    for (const [value, text] of [
      ["keine", "keine Präferenz"],
      ["wunsch", "möglichst vorne (Wunsch)"],
      ["erforderlich", "muss vorne sein (erforderlich)"],
    ]) {
      const opt = document.createElement("option");
      opt.value = value;
      opt.textContent = text;
      if (person.position_mode === value) opt.selected = true;
      select.appendChild(opt);
    }
    select.addEventListener("change", () => (person.position_mode = select.value));
    posRow.appendChild(select);
    card.appendChild(posRow);

    const others = state.people.filter((p) => p.id !== person.id);
    if (others.length > 0) {
      const desiredRow = document.createElement("div");
      desiredRow.className = "row";
      desiredRow.innerHTML = `<span class="label">Möchte neben:</span>`;
      const tagList = document.createElement("div");
      tagList.className = "tag-list";
      for (const other of others) {
        const tag = document.createElement("span");
        tag.className = "tag" + (person.desired.includes(other.id) ? " selected desired" : "");
        tag.textContent = other.name;
        tag.addEventListener("click", () => toggleTag(person, other.id, "desired"));
        tagList.appendChild(tag);
      }
      desiredRow.appendChild(tagList);
      card.appendChild(desiredRow);

      const avoidRow = document.createElement("div");
      avoidRow.className = "row";
      avoidRow.innerHTML = `<span class="label">Nicht neben:</span>`;
      const avoidTagList = document.createElement("div");
      avoidTagList.className = "tag-list";
      for (const other of others) {
        const tag = document.createElement("span");
        tag.className = "tag" + (person.avoid.includes(other.id) ? " selected avoid" : "");
        tag.textContent = other.name;
        tag.addEventListener("click", () => toggleTag(person, other.id, "avoid"));
        avoidTagList.appendChild(tag);
      }
      avoidRow.appendChild(avoidTagList);
      card.appendChild(avoidRow);
    }

    peopleListEl.appendChild(card);
  }
}

const canvasSection = document.getElementById("canvas-section");
const peopleSection = document.getElementById("people-section");
const modeChairsBtn = document.getElementById("mode-chairs");
const modePeopleBtn = document.getElementById("mode-people");

modeChairsBtn.addEventListener("click", () => {
  modeChairsBtn.classList.add("active");
  modePeopleBtn.classList.remove("active");
  canvasSection.classList.remove("hidden");
  peopleSection.classList.add("hidden");
});
modePeopleBtn.addEventListener("click", () => {
  modePeopleBtn.classList.add("active");
  modeChairsBtn.classList.remove("active");
  peopleSection.classList.remove("hidden");
  canvasSection.classList.add("hidden");
});

document.getElementById("solve-btn").addEventListener("click", async () => {
  const resultPanel = document.getElementById("result-panel");
  const statusEl = document.getElementById("result-status");
  resultPanel.classList.remove("hidden");
  statusEl.textContent = "Berechne...";

  const payload = {
    chairs: state.chairs.map((c) => ({ id: c.id, x: c.x, y: c.y })),
    people: state.people.map((p) => ({
      id: p.id,
      name: p.name,
      desired: p.desired,
      avoid: p.avoid,
      position_mode: p.position_mode,
    })),
  };

  try {
    const response = await fetch("/api/assign", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {

      const errorBody = await response.json();
      statusEl.textContent = `Fehler: ${errorBody.detail}`;
      return;
    }

    const data = await response.json();
    state.lastAssignment = data.assignment;
    statusEl.textContent = `Fertig - ${Object.keys(data.assignment).length} von ${state.chairs.length} Stühlen belegt.`;
    renderCanvas();
  } catch (err) {
    statusEl.textContent = `Verbindungsfehler: ${err.message}`;
  }
});

renderCanvas();
renderPeople();
