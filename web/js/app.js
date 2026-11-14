import { Capsule } from "./capsule.js";
import { ILLUSTRATION, ART } from "./illustration.js";

/* ================= utilitaires ================= */
const $ = (sel, el = document) => el.querySelector(sel);
const nf = new Intl.NumberFormat("fr-FR");
const fmt = (n) => (n == null ? "—" : nf.format(n));
const pct = (x) => (x == null ? "inconnue" : `${Math.round(x * 100)} %`);

// Construit le DOM sans innerHTML : les textes venant des données restent du texte (pas de HTML injecté).
function h(tag, attrs, ...kids) {
  const el = document.createElement(tag);
  for (const [k, v] of Object.entries(attrs || {})) {
    if (v == null || v === false) continue;
    if (k === "class") el.className = v;
    else if (k === "html") el.innerHTML = v; // réservé aux constantes écrites ici (icônes)
    else if (k.startsWith("on")) el.addEventListener(k.slice(2), v);
    else el.setAttribute(k, v === true ? "" : v);
  }
  for (const kid of kids.flat(Infinity)) {
    if (kid == null || kid === false) continue;
    el.append(kid.nodeType ? kid : document.createTextNode(String(kid)));
  }
  return el;
}
const svgNS = "http://www.w3.org/2000/svg";
function s(tag, attrs) {
  const el = document.createElementNS(svgNS, tag);
  for (const [k, v] of Object.entries(attrs || {})) el.setAttribute(k, v);
  return el;
}

const ICONS = {
  book: '<path d="M4 5a2 2 0 0 1 2-2h13v15H6a2 2 0 0 0-2 2z"/><path d="M4 20a2 2 0 0 0 2 2h13v-4M8 7h7M8 11h5"/>',
  search: '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
  grid: '<rect x="3" y="3" width="7" height="7" rx="1.5"/><rect x="14" y="3" width="7" height="7" rx="1.5"/><rect x="3" y="14" width="7" height="7" rx="1.5"/><rect x="14" y="14" width="7" height="7" rx="1.5"/>',
  flask: '<path d="M9 3h6M10 3v6L4.5 19a2 2 0 0 0 1.7 3h11.6a2 2 0 0 0 1.7-3L14 9V3"/><path d="M7 15h10"/>',
  ban: '<circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8"/>',
  users: '<path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="10" cy="7" r="4"/><path d="M21 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
  file: '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6M8 13h8M8 17h8"/>',
  scale: '<path d="M12 3v18M5 21h14M5 7h14M5 7l-3 7a3 3 0 0 0 6 0zM19 7l-3 7a3 3 0 0 0 6 0z"/>',
  arrow: '<path d="M5 12h14M13 6l6 6-6 6"/>',
  link: '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>',
  download: '<path d="M12 3v12M7 10l5 5 5-5M5 21h14"/>',
  upload: '<path d="M12 15V3M7 8l5-5 5 5M5 21h14"/>',
  alert: '<path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0zM12 9v4M12 17h.01"/>',
};
const icon = (name, size = 18) =>
  h("span", { class: "ic", "aria-hidden": "true", html: `<svg width="${size}" height="${size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.9" stroke-linecap="round" stroke-linejoin="round">${ICONS[name]}</svg>` });

async function api(path, body) {
  let res;
  try {
    res = await fetch(path, body === undefined ? {} : { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(body) });
  } catch (e) {
    throw new Error("Le serveur TrialRevive ne répond pas. Relancez « python server.py ».");
  }
  let data = {};
  try { data = await res.json(); } catch (e) { /* réponse non JSON */ }
  if (!res.ok) throw new Error(data.error || `Erreur ${res.status}`);
  return data;
}

/* ================= état ================= */
const state = { dossier: null, markdown: "", question: "", example: "", loading: false };
let capsule = null;
const E_COLOR = { E0: "#dbe4df", E1: "#bfe6d3", E2: "#86d1ae", E3: "#3fae7f", E4: "#1b7f58" };
const DEFAULT_EXAMPLE = "Le statut KRAS change-t-il l'effet du panitumumab dans le cancer colorectal métastatique ?";
const REJECT = {
  1: ["Pas de tirage au sort", "#e6ebf2"],
  2: ["Autre médicament", "#d6dfeb"],
  3: ["Marqueur non mesuré", "#c7d3e3"],
  4: ["Un seul statut du marqueur", "#b8c6dc"],
  5: ["Trop peu de patients", "#a9bad4"],
  6: ["Statut connu pour trop peu de patients", "#9aaecb"],
};
const ROUTES = {
  apercu: ["Aperçu", "grid"],
  essais: ["Essais retenus", "flask"],
  ecartes: ["Essais écartés", "ban"],
  patients: ["Patients", "users"],
  dossier: ["Dossier", "file"],
  comparaison: ["Comparaison IA", "scale"],
  guide: ["Comment ça marche", "book"],
};
const route = () => (location.hash.match(/^#\/([a-z]+)/) || [])[1] || "accueil";

/* ================= composants ================= */
function meter(level, small) {
  const idx = Number(level.slice(1));
  const segs = [1, 2, 3, 4].map((i) => h("i", { style: i <= idx ? `background:${E_COLOR[level]}` : "" }));
  return h("div", { class: "meter" + (small ? " meter-sm" : ""), role: "img", "aria-label": `Preuve ${level}` }, segs);
}
const evidenceTag = (level) => h("span", { class: "num", style: "display:inline-flex;gap:10px;align-items:center" }, meter(level, true), h("b", {}, level));
const kindBadge = (niveau) => h("span", { class: "badge " + (niveau === "direct" ? "badge-cobalt" : "badge-slate") }, niveau === "direct" ? "Médicament exact" : "Même classe");

function artRow(names) {
  return h("div", { class: "art" }, names.map((n) => h("span", { class: `art-${n}`, html: ART[n] })));
}
function pageHead(title, text, names, extra) {
  return h("header", { class: "pagehead" },
    h("div", { class: "pagehead-copy" }, h("h2", {}, title), text && h("p", {}, text), extra),
    names && names.length ? artRow(names) : null);
}
const HEAD_ART = {
  "Essais retenus": ["doctor", "molecule"],
  "Essais écartés": ["magnifier", "nurse"],
  "Patients de l'essai interne": ["tubes", "man"],
  "Dossier de faisabilité": ["clipboard", "doctor"],
  "Comparaison avec une IA généraliste": ["doctor", "nurse"],
};
const viewHead = (title, text, extra) => pageHead(title, text, HEAD_ART[title], extra);
function emptyState(title, text) {
  return h("section", { class: "empty" }, artRow(["clipboard", "magnifier"]), h("h3", {}, title), h("p", {}, text),
    h("a", { class: "btn btn-primary", href: "#/", style: "display:inline-grid;place-items:center;text-decoration:none" }, "Poser une question"));
}

/* ----- infobulle ----- */
const tip = $("#tip");
function showTip(e, title, text) {
  tip.replaceChildren(h("b", {}, title), h("span", {}, text));
  tip.hidden = false;
  const r = (e.currentTarget || e.target).getBoundingClientRect();
  const x = Math.min(innerWidth - 320, Math.max(8, r.left + r.width / 2 - 140));
  tip.style.left = `${x}px`;
  tip.style.top = `${Math.max(8, r.top - tip.offsetHeight - 10)}px`;
}
const hideTip = () => (tip.hidden = true);

/* ----- tiroir de détail ----- */
let lastFocus = null;
function openDrawer(content) {
  lastFocus = document.activeElement;
  $("#drawerBody").replaceChildren(content);
  $("#drawer").hidden = false;
  $("#drawer .close").focus();
}
function closeDrawer() {
  $("#drawer").hidden = true;
  lastFocus?.focus?.();
}
function trialDrawer(t) {
  const d = state.dossier;
  const src = d.sources.find((x) => x.nct_id === t.nct_id);
  const body = h("div", {}, h("p", { class: "t-sub" }, t.nct_id), h("h3", {}, t.titre));
  if (t.retenu) {
    body.append(
      h("div", { style: "display:flex;gap:8px;flex-wrap:wrap;margin-top:6px" }, kindBadge(t.niveau), h("span", { class: "badge" }, evidenceTag(t.E))),
      h("dl", { class: "facts" },
        h("div", {}, h("dt", {}, "Patients inclus"), h("dd", { class: "num" }, fmt(t.nb_patients))),
        h("div", {}, h("dt", {}, "Statut du marqueur connu"), h("dd", { class: "num" }, pct(t.couverture))),
        h("div", {}, h("dt", {}, "Score de compatibilité"), h("dd", { class: "num" }, t.score)),
        h("div", {}, h("dt", {}, "Plafond de preuve"), h("dd", {}, t.plafond)),
      ),
      h("h4", {}, "Comment obtenir la réponse"), h("p", {}, `${t.R} : ${t.R_pourquoi}.`),
      h("h4", {}, "Écarts acceptés"),
      t.ecarts.length ? h("ul", {}, t.ecarts.map((e) => h("li", {}, e))) : h("p", {}, "Aucun écart : l'essai remplit toutes les exigences."),
      h("h4", {}, "À confirmer par un humain"), h("ul", {}, t.conditions.map((c) => h("li", {}, c))),
    );
    if (src?.reanalyse) {
      body.append(h("h4", {}, "Réanalyse publiée du marqueur"), h("p", {}, src.reanalyse),
        h("p", { style: "margin-top:6px" }, src.reanalyse_verifiee ? "Vérifiée par un humain." : "Référence rattachée au registre ; effectifs et conclusions encore à vérifier."),
        src.publication_lien && h("p", { style: "margin-top:6px" }, h("a", { href: src.publication_lien, target: "_blank", rel: "noopener" }, "Ouvrir la publication")));
    }
  } else {
    body.append(h("div", { style: "margin-top:8px" }, h("span", { class: "badge badge-slate" }, "Écarté")), h("h4", {}, "Raison"), h("p", {}, t.raison));
  }
  body.append(h("p", { style: "margin-top:22px" }, h("a", { href: t.lien, target: "_blank", rel: "noopener" }, "Voir la fiche sur ClinicalTrials.gov")));
  return body;
}

/* ================= vues ================= */
function landing() {
  const example = state.example || DEFAULT_EXAMPLE;
  const all = [
    { q: example, tag: "Cas de démo" },
    { q: example.replace("panitumumab", "cetuximab"), tag: "Sans comptage interne" },
  ];
  if (state.question && !all.some((x) => x.q === state.question)) all.push({ q: state.question, tag: "Dernière analyse" });

  const canvas = h("canvas", { "aria-hidden": "true" });
  const fallback = h("div", { class: "fallback", hidden: true, html: '<svg width="120" height="120" viewBox="0 0 64 64" aria-hidden="true"><g transform="rotate(-45 32 32)"><rect x="8" y="22" width="48" height="20" rx="10" fill="#e8eeea" stroke="#1a1a1a" stroke-width="2"/><path d="M32 22h14a10 10 0 0 1 0 20H32z" fill="#3fae7f" stroke="#1a1a1a" stroke-width="2"/></g></svg>' });

  const input = h("input", { id: "finder", type: "text", maxlength: "600", autocomplete: "off", role: "combobox", "aria-expanded": "true", "aria-controls": "suggest",
    "aria-autocomplete": "list", "aria-label": "Rechercher une question scientifique", placeholder: "Rechercher une question scientifique" });
  const list = h("ul", { class: "suggest", id: "suggest", role: "listbox", "aria-label": "Questions proposées" });
  let active = -1, shown = [];
  const draw = () => {
    const needle = input.value.trim().toLowerCase();
    shown = all.filter((x) => !needle || x.q.toLowerCase().includes(needle));
    active = shown.length ? Math.min(active, shown.length - 1) : -1;
    list.replaceChildren(...(shown.length
      ? shown.map((x, i) => h("li", { id: `opt${i}`, role: "option", "aria-selected": String(i === active), onclick: () => { input.value = x.q; run(x.q); } },
          icon("search", 18), h("span", { class: "txt" }, x.q), h("span", { class: "tag" }, x.tag)))
      : [h("li", { role: "option", "aria-disabled": "true" }, icon("search", 18), h("span", { class: "txt" }, "Appuyez sur Entrée pour analyser cette question."))]));
    input.setAttribute("aria-activedescendant", active >= 0 ? `opt${active}` : "");
  };
  input.addEventListener("input", () => { active = -1; draw(); });
  input.addEventListener("keydown", (e) => {
    if (e.key === "ArrowDown" || e.key === "ArrowUp") {
      e.preventDefault();
      if (!shown.length) return;
      active = (active + (e.key === "ArrowDown" ? 1 : -1) + shown.length) % shown.length;
      draw();
    }
  });
  draw();

  const go = h("button", { class: "finder-go", type: "submit", "aria-label": "Analyser la question" }, icon("arrow", 20));
  const form = h("form", { onsubmit: (e) => { e.preventDefault(); run(active >= 0 && shown[active] ? shown[active].q : input.value); } }, input, go);

  setTimeout(() => { capsule?.dispose(); capsule = new Capsule(canvas, fallback); }, 0);
  return h("section", { class: "home", "aria-labelledby": "h1" },
    h("h1", { id: "h1" }, "Trouvez les essais qui peuvent répondre à votre question"),
    h("div", { class: "illus" }, h("div", { html: ILLUSTRATION }), h("div", { class: "cap3d" }, canvas, fallback)),
    h("div", { class: "finder" }, form, list),
    h("p", { class: "home-note" }, "Essais publics de ClinicalTrials.gov. Patients de l'essai interne fictifs.",
      state.dossier && [" ", h("a", { href: "#/apercu" }, "Revenir au dernier dossier")]),
  );
}

function reading(d) {
  const v = d.verdict;
  const gains = v.G.slice(0, 3).map((g) => h("li", {}, h("b", {}, g.code), g.gain));
  const panel = (art, k, value, valueStyle, ...rest) =>
    h("div", { class: "rpanel" }, h("span", { class: "rico", html: ART[art] }), h("p", { class: "k" }, k), h("p", { class: "v", style: valueStyle }, value), ...rest);
  return h("section", { class: "reading", "aria-label": "Verdict" },
    panel("syringe", "Comment obtenir la réponse", v.R, "", h("p", { class: "d" }, v.R_texte)),
    panel("heart", "Force de la preuve atteignable", v.E, `color:${E_COLOR[v.E]}`, meter(v.E), h("p", { class: "d" }, `${v.E_texte}. Atteignable, pas acquis.`),
      !v.preuve_verifiee && h("p", { class: "note" }, "Les références des réanalyses sont en cours de vérification par un humain.")),
    panel("kit", "Ce que ça apporte", `${v.G.length} gains`, "", h("ul", {}, gains, v.G.length > 3 && h("li", {}, h("a", { href: "#/dossier" }, `et ${v.G.length - 3} autres dans le dossier`)))),
  );
}

function blister(d) {
  const kept = d.retenus;
  const groupOf = (t) => (t.retenu ? (t.niveau === "direct" ? "k-direct" : "k-classe") : `r${t.etape_rejet}`);
  const items = [
    ...kept.map((t) => ({ t, g: groupOf(t) })),
    ...[...d.ecartes].sort((a, b) => a.etape_rejet - b.etape_rejet).map((t) => ({ t, g: groupOf(t) })),
  ];
  const cols = 13, cell = 32, rows = Math.ceil(items.length / cols);
  const svg = s("svg", { class: "blister", viewBox: `0 0 ${cols * cell} ${rows * cell}`, role: "group", "aria-label": `${items.length} essais : ${kept.length} retenus, ${items.length - kept.length} écartés` });
  const tints = (g) => (g.startsWith("r") ? REJECT[g.slice(1)][1] : "#f4f6fa");
  items.forEach(({ t, g }, i) => {
    const cx = (i % cols) * cell + cell / 2, cy = Math.floor(i / cols) * cell + cell / 2;
    const node = s("g", { class: "dimple", tabindex: "0", role: "button", "data-g": g, "aria-label": `${t.nct_id} : ${t.retenu ? "retenu, preuve " + t.E : "écarté, " + t.raison}` });
    node.style.animationDelay = `${i * 8}ms`;
    node.append(s("circle", { class: "cup", cx, cy, r: 13, fill: tints(g) }));
    if (t.retenu) {
      node.append(t.niveau === "direct"
        ? s("circle", { cx, cy, r: 8.5, fill: E_COLOR[t.E] })
        : s("circle", { cx, cy, r: 7.5, fill: "none", stroke: E_COLOR[t.E], "stroke-width": 3.2 }));
    }
    const label = t.retenu ? `Retenu, preuve ${t.E}, ${t.niveau === "direct" ? "médicament exact" : "même classe"}` : t.raison;
    node.addEventListener("mouseenter", (e) => showTip(e, `${t.nct_id}`, `${t.titre.length > 70 ? t.titre.slice(0, 68) + "…" : t.titre} — ${label}`));
    node.addEventListener("focus", (e) => showTip(e, `${t.nct_id}`, label));
    node.addEventListener("mouseleave", hideTip);
    node.addEventListener("blur", hideTip);
    node.addEventListener("click", () => { hideTip(); openDrawer(trialDrawer(t)); });
    node.addEventListener("keydown", (e) => { if (e.key === "Enter" || e.key === " ") { e.preventDefault(); node.dispatchEvent(new Event("click")); } });
    svg.append(node);
  });

  const count = (g) => items.filter((x) => x.g === g).length;
  const legendDefs = [
    ["k-direct", "Retenu, médicament exact", "#1b7f58"],
    ["k-classe", "Retenu, même classe", "#86d1ae"],
    ...[1, 2, 3, 4, 5, 6].map((n) => [`r${n}`, REJECT[n][0], REJECT[n][1]]),
  ].filter(([g]) => count(g) > 0);
  let active = null;
  const legend = h("ul", { class: "legend" }, legendDefs.map(([g, label, color]) =>
    h("li", {}, h("button", { type: "button", "aria-pressed": "false", onclick: (e) => {
      active = active === g ? null : g;
      svg.classList.toggle("is-filtering", active !== null);
      svg.querySelectorAll(".dimple").forEach((n) => n.classList.toggle("on", n.dataset.g === active));
      legend.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", "false"));
      if (active) e.currentTarget.setAttribute("aria-pressed", "true");
    } }, h("span", { class: "sw", style: `background:${color}` }), h("span", {}, label), h("span", { class: "n num" }, count(g))))));
  return h("div", { class: "blister-wrap" }, h("div", { class: "panel-box" }, svg), h("div", {},
    legend,
    h("p", { class: "t-sub", style: "margin-top:12px;font-family:inherit" }, "Cliquez sur une alvéole pour le détail, sur une ligne de légende pour isoler un groupe."),
  ));
}

function funnelBars(d, withDrops) {
  const top = d.entonnoir[0].n || 1;
  return h("div", { class: "funnel" }, d.entonnoir.map((st, i) => {
    const [code, ...rest] = st.etape.split(" : ");
    const prev = i ? d.entonnoir[i - 1].n : null;
    const bar = h("i", { style: `width:${(100 * st.n) / top}%` });
    return h("div", { class: "frow" },
      h("div", { class: "lab" }, h("b", {}, code), rest.length ? ` : ${rest.join(" : ")}` : ""),
      h("div", { class: "bar" }, bar),
      h("div", { class: "val num" }, st.n_publie == null ? "<5" : fmt(st.n_publie), withDrops && prev != null && st.n < prev ? h("small", {}, `−${prev - st.n}`) : ""),
    );
  }));
}

function overview() {
  const d = state.dossier;
  const nbTotal = d.rejection.total;
  const wrap = h("div", {},
    pageHead(d.question, `${fmt(nbTotal)} essais publics analysés : ${d.retenus.length} peuvent répondre, ${fmt(d.ecartes.length)} sont écartés avec une raison.`, ["heart", "tubes", "syringe"]),
    reading(d),
    h("section", { class: "section" }, h("h3", {}, `${fmt(nbTotal)} essais, une alvéole chacun`),
      h("p", { class: "sub" }, "Les essais retenus sont remplis. Les autres restent vides, regroupés par raison d'écart."), blister(d)),
    h("section", { class: "section" }, h("h3", {}, "Du prévu au complet, sur l'essai interne"),
      h("p", { class: "sub" }, "Patients fictifs. Avoir 400 lignes ne veut pas dire avoir 400 patients analysables."), h("div", { class: "panel-box" }, funnelBars(d, true),
        h("p", { style: "margin-top:16px" }, h("a", { href: "#/patients" }, "Voir le détail et les effets par groupe")))),
  );
  document.body.classList.add("reveal");
  setTimeout(() => document.body.classList.remove("reveal"), 1800);
  return wrap;
}

function trialsView() {
  const d = state.dossier;
  const rows = d.retenus.map((t, i) => h("tr", { tabindex: "0", onclick: () => openDrawer(trialDrawer(t)),
    onkeydown: (e) => { if (e.key === "Enter") openDrawer(trialDrawer(t)); } },
    h("td", { class: "num" }, i + 1),
    h("td", {}, h("div", { class: "t-title" }, t.titre), h("div", { class: "t-sub" }, t.nct_id)),
    h("td", {}, kindBadge(t.niveau)),
    h("td", { class: "right num" }, fmt(t.nb_patients)),
    h("td", {}, evidenceTag(t.E)),
    h("td", { class: "right num" }, t.score),
    h("td", { class: "right num" }, pct(t.couverture)),
  ));
  return h("div", {}, viewHead("Essais retenus", "Classés par plafond de preuve, puis score de compatibilité, puis effectif. Cliquez une ligne pour les écarts acceptés et ce qu'il reste à confirmer."),
    h("div", { class: "table-wrap" }, h("table", {},
      h("thead", {}, h("tr", {}, ["Rang", "Essai", "Médicament", "Patients", "Preuve", "Score", "Statut connu"].map((c, i) => h("th", { class: i > 2 && c !== "Preuve" ? "right" : "" }, c)))),
      h("tbody", {}, rows))));
}

function rejectedView() {
  const d = state.dossier;
  let q = "", only = null;
  const counts = {};
  d.ecartes.forEach((t) => (counts[t.etape_rejet] = (counts[t.etape_rejet] || 0) + 1));
  const body = h("tbody");
  const draw = () => {
    const rows = d.ecartes.filter((t) => (only == null || t.etape_rejet === only) && (`${t.titre} ${t.nct_id} ${t.raison}`).toLowerCase().includes(q));
    body.replaceChildren(...(rows.length ? rows.map((t) => h("tr", { tabindex: "0", onclick: () => openDrawer(trialDrawer(t)), onkeydown: (e) => { if (e.key === "Enter") openDrawer(trialDrawer(t)); } },
      h("td", {}, h("div", { class: "t-title" }, t.titre), h("div", { class: "t-sub" }, t.nct_id)), h("td", {}, t.raison))) : [h("tr", {}, h("td", { colspan: 2 }, "Aucun essai ne correspond à ce filtre."))]));
    count.textContent = `${rows.length} essai${rows.length > 1 ? "s" : ""} affiché${rows.length > 1 ? "s" : ""}`;
  };
  const count = h("span", { class: "t-sub", style: "font-family:inherit" });
  const chips = h("div", { class: "chips" }, Object.keys(counts).map(Number).sort().map((n) =>
    h("button", { class: "chip", type: "button", "aria-pressed": "false", onclick: (e) => {
      only = only === n ? null : n;
      chips.querySelectorAll(".chip").forEach((c) => c.setAttribute("aria-pressed", "false"));
      if (only != null) e.currentTarget.setAttribute("aria-pressed", "true");
      draw();
    } }, `${REJECT[n][0]} (${counts[n]})`)));
  draw();
  return h("div", {}, viewHead("Essais écartés", "Chaque essai écarté garde la raison qui l'a exclu. Filtrez par raison ou cherchez un titre."),
    h("div", { class: "toolbar" }, h("input", { type: "search", placeholder: "Chercher un essai", "aria-label": "Chercher un essai écarté", oninput: (e) => { q = e.target.value.toLowerCase(); draw(); } }), count),
    h("div", { class: "toolbar" }, chips),
    h("div", { class: "table-wrap" }, h("table", {}, h("thead", {}, h("tr", {}, h("th", {}, "Essai"), h("th", {}, "Raison de l'écart"))), body)));
}

function patientsView() {
  const d = state.dossier;
  const first = d.entonnoir[0].n;
  const head = d.utilisables == null
    ? h("div", { class: "hero-num" }, h("span", { class: "b" }, "Indéterminé"), h("p", { class: "d" }, d.raison_indetermination || "Effectif inférieur à 5 : masqué."))
    : h("div", { class: "hero-num num" }, h("span", { class: "a" }, fmt(first)), icon("arrow", 34), h("span", { class: "b" }, fmt(d.utilisables)), h("span", { style: "color:var(--ink2)" }, "patients réellement analysables"));
  const maxM = Math.max(1, ...d.groupes.flatMap((g) => [g.mediane_traite || 0, g.mediane_controle || 0]));
  const groups = h("div", { class: "groups" }, d.groupes.map((g) => {
    if (g.mediane_traite == null || g.mediane_controle == null) return h("div", { class: "panel-box group" }, h("h4", {}, `Marqueur ${g.statut}`), h("p", {}, "Effectif trop petit : masqué (moins de 5)."));
    const pair = (lab, val, color, n) => h("div", { class: "pair" }, h("span", {}, `${lab} (${fmt(n)})`), h("div", { class: "bar" }, h("i", { style: `width:${(100 * val) / maxM}%;background:${color}` })), h("span", { class: "val num" }, `${String(val).replace(".", ",")} mois`));
    return h("div", { class: "panel-box group" }, h("h4", {}, `Marqueur ${g.statut} : gain de ${String(g.gain_mois > 0 ? "+" + g.gain_mois : g.gain_mois).replace(".", ",")} mois`),
      pair("Avec traitement", g.mediane_traite, "var(--cobalt)", g.n_traite), pair("Sans traitement", g.mediane_controle, "#9aa5b8", g.n_controle),
      h("p", { class: "t-sub", style: "font-family:inherit;margin-top:8px" }, "Survie médiane."));
  }));
  const st = d.statistique, c = d.essai_confirmation;
  return h("div", {},
    viewHead("Patients de l'essai interne", "Chaque patient monte cinq marches, de prévu à complet. Seuls ceux qui arrivent en haut comptent."),
    h("p", { class: "note", style: "display:inline-block;margin:0 0 18px" }, "Données fictives générées par programme. Aucun patient réel."),
    head, h("div", { class: "panel-box" }, funnelBars(d, true)),
    h("section", { class: "section" }, h("h3", {}, "Effet du traitement selon le statut du marqueur"), h("p", { class: "sub" }, "Descriptif sur données fabriquées : ce n'est pas un test statistique."), groups),
    h("section", { class: "section" }, h("h3", {}, "Faut-il plus de patients ?"),
      h("p", { class: "sub" }, `Pour détecter une différence d'effet entre les deux statuts, il faut environ ${fmt(st.evenements_necessaires_par_groupe)} événements (décès ou rechutes) par groupe, avec une hypothèse d'effet de ${String(st.hr_hypothese).replace(".", ",")}.`),
      h("div", { class: "panel-box" }, h("dl", { class: "doc kv", style: "max-width:none" },
        h("dt", {}, "Événements observés"), h("dd", { class: "num" }, Object.entries(st.evenements_internes).map(([k, v]) => `${k} : ${fmt(v)}`).join("   ")),
        h("dt", {}, "Verdict"), h("dd", {}, st.suffisant ? "Suffisant" : "Insuffisant sur l'essai interne"),
        h("dt", {}, "Essai de confirmation"), h("dd", { class: "num" }, `environ ${fmt(c.evenements_tous)} événements pour tous les patients, ${fmt(c.evenements_selectionnes)} s'il est réservé au sous-groupe ciblé`)))),
  );
}

function dossierView() {
  const d = state.dossier, v = d.verdict, st = d.statistique, c = d.essai_confirmation, g = d.gain;
  const link = `/api/dossier.md?question=${encodeURIComponent(state.question)}`;
  return h("div", {},
    viewHead("Dossier de faisabilité", d.question, h("div", { style: "margin-top:16px" }, h("a", { class: "btn btn-primary btn-small", href: link, download: "dossier_trialrevive.md", style: "display:inline-flex;gap:8px;align-items:center;text-decoration:none" }, icon("download", 16), "Télécharger en Markdown"))),
    h("div", { class: "doc panel-box" },
    h("h3", {}, "Verdict"),
    h("dl", { class: "kv" },
      h("dt", {}, "Voie (R)"), h("dd", {}, `${v.R} : ${v.R_texte}`),
      h("dt", {}, "Preuve atteignable (E)"), h("dd", {}, `${v.E} : ${v.E_texte}`),
      h("dt", {}, "Gains possibles (G)"), h("dd", {}, v.G.map((x) => `${x.code} ${x.gain}`).join(" ; "))),
    h("p", {}, v.E_pourquoi + "."),
    h("h3", {}, `Essais retenus (${d.retenus.length})`),
    h("ul", {}, d.retenus.map((t) => h("li", {}, h("a", { href: t.lien, target: "_blank", rel: "noopener" }, t.nct_id), ` : ${t.titre} (${fmt(t.nb_patients)} patients, preuve ${t.E}, ${t.niveau === "direct" ? "médicament exact" : "même classe"})`))),
    h("h3", {}, `Essais écartés (${d.ecartes.length})`),
    h("ul", {}, Object.entries(d.rejection.ecartes_par_etape).filter(([, n]) => n > 0).map(([k, n]) => h("li", {}, `${k} : ${n}`))),
    h("h3", {}, "Comment obtenir la réponse"),
    h("p", {}, d.methode),
    h("p", {}, `Exigence statistique : ${fmt(st.evenements_necessaires_par_groupe)} événements par groupe (hypothèse d'effet ${String(st.hr_hypothese).replace(".", ",")}). Essai interne : ${st.suffisant ? "suffisant" : "insuffisant"}.`),
    h("p", {}, `Essai de confirmation : environ ${fmt(c.evenements_tous)} événements pour tous les patients, contre ${fmt(c.evenements_selectionnes)} s'il est réservé au sous-groupe ciblé.`),
    h("h3", {}, "Gain attendu"),
    h("p", {}, `${g.pct_sauvage ?? "—"} % de patients au statut sauvage parmi les patients complets. Gain de survie médiane : ${g.gain_sauvage_mois ?? "—"} mois pour le statut sauvage, ${g.gain_mute_mois ?? "—"} mois pour le statut muté. ${g.note}`),
    h("h3", {}, "Sources"),
    h("ul", {}, d.sources.map((x) => h("li", {}, h("a", { href: x.lien, target: "_blank", rel: "noopener" }, x.nct_id),
      x.reanalyse && [" : ", x.publication_lien ? h("a", { href: x.publication_lien, target: "_blank", rel: "noopener" }, x.reanalyse) : x.reanalyse, x.reanalyse_verifiee ? " (vérifiée)" : " (à vérifier)"]))),
    h("h3", {}, "Limites"), h("ul", {}, d.limites.map((x) => h("li", {}, x))),
    ),
  );
}

function guideView() {
  const step = (n, art, title, text) => h("li", { class: "gstep" }, h("span", { class: "gart", html: ART[art] }),
    h("div", {}, h("h3", {}, h("span", { class: "gnum num" }, n), title), h("p", {}, text)));
  return h("div", {},
    pageHead("Comment ça marche", "TrialRevive transforme une question scientifique en dossier de faisabilité, en quatre étapes.", ["man", "doctor", "nurse"]),
    h("ol", { class: "gsteps" },
      step(1, "clipboard", "Vous posez une question", "Par exemple : le statut KRAS change-t-il l'effet du panitumumab ? La question devient une liste d'exigences précises : tirage au sort, médicament, marqueur mesuré."),
      step(2, "molecule", "Il trie les essais publics", "Chaque essai de ClinicalTrials.gov est comparé aux exigences. Ceux qui ne conviennent pas sont écartés, et la raison de chaque écart est conservée."),
      step(3, "tubes", "Il compte les patients utilisables", "Sur un essai interne fictif, chaque patient monte cinq marches : prévu, collecté, existant, utilisable, complet. Seuls les patients complets comptent."),
      step(4, "heart", "Il rend un dossier sourcé", "Trois notes (R, E, G), la taille du prochain essai, des sources cliquables et les limites. Chaque chiffre vient du calcul, rien n'est écrit par une IA.")),
    h("section", { class: "section" }, h("h3", {}, "Lire les trois notes"),
      h("div", { class: "panel-box" }, h("dl", { class: "doc kv", style: "max-width:none;margin:0" },
        h("dt", {}, "R : la voie"), h("dd", {}, "Comment obtenir la réponse. R0 veut dire que le marqueur est déjà mesuré dans les données."),
        h("dt", {}, "E : la preuve"), h("dd", {}, "La force de preuve atteignable, de E0 (non testable) à E4 (confirmée dans un second essai). Atteignable ne veut pas dire acquise."),
        h("dt", {}, "G : le gain"), h("dd", {}, "Ce que la réponse apporte : mieux cibler les patients, un essai de confirmation plus petit, un test diagnostique associé.")))),
    h("section", { class: "section" }, h("h3", {}, "Ce qui n'est pas encore validé"),
      h("div", { class: "panel-box" }, h("ul", { class: "plain" },
        h("li", {}, "Les patients de l'essai interne sont fictifs : aucun patient réel n'est utilisé."),
        h("li", {}, "Les références des six articles sont rattachées au registre, mais leurs chiffres restent à vérifier par une personne du domaine."),
        h("li", {}, "La fiche de la question n'est pas encore validée par un clinicien."),
        h("li", {}, "Seul le marqueur KRAS est pris en charge."),
        h("li", {}, "La comparaison avec une IA généraliste n'a pas encore été menée : importez une vraie réponse pour la voir.")))),
  );
}

async function comparisonView() {
  const wrap = h("div", {}, viewHead("Comparaison avec une IA généraliste", "Importez la réponse réelle d'une IA à la même question. Rien n'est inventé : sans réponse importée, aucune comparaison n'est affichée."));
  const file = h("input", { type: "file", accept: "application/json,.json", class: "sr", id: "importFile" });
  const importBtn = h("label", { class: "btn btn-ghost btn-small", for: "importFile", style: "display:inline-flex;gap:8px;align-items:center;cursor:pointer" }, icon("upload", 16), "Importer une réponse (JSON)");
  const msg = h("p", { role: "status", style: "color:var(--ink2);margin-top:8px" });
  let records = [], errors = [], current = null, imported = null;
  try { const r = await api("/api/baselines"); records = r.records; errors = r.errors; } catch (e) { errors = [e.message]; }
  const detail = h("div", {});
  const list = h("div", { class: "rec-list" });

  const select = async (rec, isImported) => {
    current = rec; imported = isImported ? rec : null;
    list.querySelectorAll("button").forEach((b) => b.setAttribute("aria-pressed", String(b.__rec === rec)));
    detail.replaceChildren(h("p", {}, "Chargement…"));
    try {
      const r = await api("/api/compare", { question: state.question, record: rec });
      const keys = ["Critère", "TrialRevive", "IA généraliste (évaluation déclarée)"];
      detail.replaceChildren(
        h("h3", { style: "font-size:1.1rem;margin-bottom:6px" }, rec.question),
        h("p", { class: "t-sub", style: "font-family:inherit" }, `Modèle : ${rec.modele}. Date : ${rec.date}.`),
        rec.contexte && h("p", { style: "margin-top:6px" }, `Contexte : ${rec.contexte}`),
        !r.meme_question && h("p", { class: "note" }, "La question archivée diffère de la question analysée : les résultats TrialRevive ne sont pas comparables."),
        h("div", { class: "table-wrap", style: "margin-top:14px" }, h("table", {}, h("thead", {}, h("tr", {}, keys.map((k) => h("th", {}, k)))), h("tbody", {}, r.rows.map((row) => h("tr", {}, keys.map((k) => h("td", {}, row[k]))))))),
        h("h4", { style: "margin:20px 0 8px;font:650 1rem var(--display)" }, "Réponse brute, intégrale"),
        h("textarea", { class: "raw", readonly: true, "aria-label": "Réponse brute de l'IA" }, rec.reponse_ia),
        h("h4", { style: "margin:20px 0 8px;font:650 1rem var(--display)" }, "Numéros NCT cités"),
        h("p", { class: "t-sub", style: "font-family:inherit;margin-bottom:8px" }, "Retrouver un essai dans le cache ne valide ni les chiffres, ni la conclusion. Un NCT absent du cache peut exister."),
        r.nct.length ? h("div", { class: "table-wrap" }, h("table", {}, h("thead", {}, h("tr", {}, ["NCT cité", "Cache local", "Titre du registre", "Lien"].map((k) => h("th", {}, k)))),
          h("tbody", {}, r.nct.map((n) => h("tr", {}, h("td", { class: "num" }, n["NCT cité"]), h("td", {}, n["Cache local"]), h("td", {}, n["Titre du registre"]),
            h("td", {}, h("a", { href: n["Lien"], target: "_blank", rel: "noopener" }, "Ouvrir"))))))) : h("p", {}, "Aucun numéro NCT détecté : les autres références restent à vérifier."),
        h("div", { style: "display:flex;gap:10px;margin-top:18px;flex-wrap:wrap" },
          h("button", { class: "btn btn-ghost btn-small", type: "button", onclick: () => {
            const url = URL.createObjectURL(new Blob([JSON.stringify(rec, null, 2)], { type: "application/json" }));
            h("a", { href: url, download: "comparaison_ia.json" }).click(); setTimeout(() => URL.revokeObjectURL(url), 1000);
          } }, "Télécharger l'archive JSON"),
          imported && h("button", { class: "btn btn-primary btn-small", type: "button", onclick: async () => {
            try { const a = await api("/api/baselines/archive", { record: imported }); msg.textContent = `Réponse archivée localement : ${a.archive}`; }
            catch (e) { msg.textContent = `Archivage impossible : ${e.message}`; }
          } }, "Archiver cette réponse localement")),
      );
    } catch (e) { detail.replaceChildren(h("p", { class: "alert", style: "margin:0" }, e.message)); }
  };
  const addToList = (rec, isImported) => {
    const b = h("button", { type: "button", "aria-pressed": "false", onclick: () => select(rec, isImported) }, h("b", {}, rec.modele), h("small", {}, `${rec.date}${isImported ? " (importée)" : ""}`));
    b.__rec = rec; list.append(b); return b;
  };
  records.forEach((r) => addToList(r, false));
  file.addEventListener("change", async () => {
    const f = file.files[0]; if (!f) return;
    try {
      if (f.size > 1_500_000) throw new Error("Fichier trop volumineux (1,5 Mo maximum).");
      const r = await api("/api/baselines/validate", { text: await f.text() });
      const b = addToList(r.record, true); msg.textContent = ""; b.click(); empty.hidden = true;
    } catch (e) { msg.textContent = `Import impossible : ${e.message}`; }
    file.value = "";
  });
  const empty = h("div", { class: "empty", hidden: records.length > 0 }, h("h3", {}, "Aucune réponse d'IA enregistrée"),
    h("p", {}, "Posez la même question à une IA généraliste, copiez sa réponse complète dans un fichier JSON (modèle et protocole dans data/baseline/LISEZ_MOI.md), puis importez-le ici. Aucune comparaison n'a encore été effectuée."));
  wrap.append(h("div", { class: "toolbar" }, file, importBtn), msg, ...errors.map((e) => h("p", { class: "note" }, e)), empty,
    h("div", { class: "cmp-layout" }, list, detail));
  if (records.length) list.firstChild.click();
  return wrap;
}

/* ================= pilotage ================= */
function setAlert(text) { const a = $("#alert"); a.textContent = text || ""; a.hidden = !text; }

function setBusy(on) {
  document.querySelectorAll(".ask button[type=submit]").forEach((b) => { b.disabled = on; b.textContent = on ? "Analyse…" : "Analyser"; });
  document.querySelectorAll(".finder-go").forEach((b) => { b.disabled = on; });
}

async function run(text) {
  text = (text || "").trim();
  if (!text) { setAlert("Écrivez une question avant de lancer l'analyse, ou cliquez sur « Cas de démo »."); return; }
  if (state.loading) return;
  state.loading = true; setAlert("");
  setBusy(true);
  const opening = route() === "accueil" && capsule ? capsule.open() : Promise.resolve();
  try {
    const [res] = await Promise.all([api("/api/analyze", { question: text }), opening]);
    Object.assign(state, { dossier: res.dossier, markdown: res.markdown, question: text, example: res.exemple });
    $("#qCompact").value = text;
    if (route() === "apercu") render(); else location.hash = "#/apercu";
  } catch (e) {
    capsule?.close(); setAlert(e.message);
  } finally {
    state.loading = false;
    setBusy(false);
  }
}

function renderNav(current) {
  const d = state.dossier;
  $("#nav").replaceChildren(...Object.entries(ROUTES).map(([id, [label, ic]]) => {
    const count = d && id === "essais" ? d.retenus.length : d && id === "ecartes" ? d.ecartes.length : null;
    return h("li", {}, h("a", { href: `#/${id}`, "aria-current": current === id ? "page" : null }, icon(ic, 19), h("span", {}, label), count != null && h("span", { class: "count num" }, count)));
  }));
}

async function render() {
  hideTip(); $("#drawer").hidden = true;
  const r = route();
  document.body.dataset.state = r === "accueil" ? "landing" : "work";
  renderNav(r);
  if (r !== "accueil") { capsule?.dispose(); capsule = null; }
  const main = $("#main");
  let view;
  if (r === "accueil") view = landing();
  else if (!ROUTES[r]) view = emptyState("Cette page n'existe pas", "Revenez à l'accueil pour poser une question.");
  else if (!state.dossier && r !== "guide") view = emptyState("Aucune analyse pour le moment", "Posez une question, ou lancez le cas de démonstration : les essais, les patients et le dossier apparaîtront ici.");
  else view = { apercu: overview, essais: trialsView, ecartes: rejectedView, patients: patientsView, dossier: dossierView, comparaison: comparisonView, guide: guideView }[r]();
  const node = await view;
  main.replaceChildren(node);
  document.title = r === "accueil" ? "TrialRevive" : `${ROUTES[r]?.[0] ?? "Page introuvable"} | TrialRevive`;
  if (r !== "accueil") window.scrollTo({ top: 0 });
}

/* ================= démarrage ================= */
$("#askFormCompact").addEventListener("submit", (e) => { e.preventDefault(); run($("#qCompact").value); });
$("[data-demo]").addEventListener("click", () => run(state.example));
document.addEventListener("click", (e) => { if (e.target.closest("[data-close]")) closeDrawer(); });
document.addEventListener("keydown", (e) => {
  if (e.key === "Escape" && !$("#drawer").hidden) closeDrawer();
  if (e.key === "/" && !/input|textarea/i.test(document.activeElement.tagName)) { e.preventDefault(); ($("#finder") || $("#qCompact")).focus(); }
});
addEventListener("hashchange", render);
api("/api/info").then((i) => { state.example = i.exemple; $("#qCompact").placeholder = "Posez une question scientifique"; }).catch(() => {}).finally(render);
