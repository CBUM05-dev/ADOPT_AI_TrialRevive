"""Interface TrialRevive : tableau de bord web (barre latérale, icônes SVG, pilule 3D).

Lancer : python -m streamlit run app_ui.py
Même logique que app.py (src/ inchangé) : seule l'apparence change.
"""
import html
import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src import dossier, engine, fake_data, question
from src.pill3d import render_pill

BASELINE_DIR = Path(__file__).parent / "data" / "baseline"
E_COLORS = {"E0": "#ef4444", "E1": "#f97316", "E2": "#f59e0b", "E3": "#16a34a", "E4": "#0f766e"}
E_LEVELS = ["E0", "E1", "E2", "E3", "E4"]

PAGES = [  # (nom, icône Material pour le menu)
    ("Tableau de bord", ":material/dashboard:"),
    ("Essais retenus", ":material/science:"),
    ("Essais écartés", ":material/block:"),
    ("Patients", ":material/groups:"),
    ("Dossier", ":material/description:"),
    ("Comparaison", ":material/compare_arrows:"),
]

st.set_page_config(page_title="TrialRevive", page_icon=":material/science:", layout="wide")

# ---------------------------------------------------------------- icônes SVG (style trait, 24x24)
_ICONS = {
    "search": '<circle cx="11" cy="11" r="7"/><path d="M21 21l-4.3-4.3"/>',
    "flask": '<path d="M9 3h6M10 3v6L4.5 19a2 2 0 0 0 1.7 3h11.6a2 2 0 0 0 1.7-3L14 9V3"/><path d="M7 15h10"/>',
    "users": '<path d="M17 21v-2a4 4 0 0 0-4-4H7a4 4 0 0 0-4 4v2"/><circle cx="10" cy="7" r="4"/><path d="M21 21v-2a4 4 0 0 0-3-3.9M16 3.1a4 4 0 0 1 0 7.8"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M9 12l2 2 4-4"/>',
    "alert": '<path d="M10.3 3.9L1.8 18a2 2 0 0 0 1.7 3h17a2 2 0 0 0 1.7-3L13.7 3.9a2 2 0 0 0-3.4 0z"/><path d="M12 9v4M12 17h.01"/>',
    "check": '<path d="M20 6L9 17l-5-5"/>',
    "help": '<circle cx="12" cy="12" r="10"/><path d="M9.1 9a3 3 0 0 1 5.8 1c0 2-3 3-3 3M12 17h.01"/>',
    "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
    "file": '<path d="M14 3H6a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9zM14 3v6h6M8 13h8M8 17h8"/>',
    "database": '<ellipse cx="12" cy="5" rx="8" ry="3"/><path d="M4 5v14c0 1.7 3.6 3 8 3s8-1.3 8-3V5M4 12c0 1.7 3.6 3 8 3s8-1.3 8-3"/>',
    "lock": '<rect x="4" y="11" width="16" height="10" rx="2"/><path d="M8 11V7a4 4 0 0 1 8 0v4"/>',
    "link": '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6M15 3h6v6M10 14L21 3"/>',
    "pulse": '<path d="M22 12h-4l-3 9L9 3l-3 9H2"/>',
    "target": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M12 3v3M12 18v3M3 12h3M18 12h3"/>',
    "pill": '<rect x="2.5" y="8" width="19" height="8" rx="4" transform="rotate(-45 12 12)"/><path d="M8.6 8.6l6.8 6.8"/>',
    "gain": '<path d="M3 17l6-6 4 4 8-8M15 7h6v6"/>',
}


def icon(name: str, size: int = 20, color: str = "currentColor", stroke: float = 2) -> str:
    return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="{color}" stroke-width="{stroke}" stroke-linecap="round" stroke-linejoin="round" '
            f'style="vertical-align:-0.2em;flex:none">{_ICONS[name]}</svg>')


def block(markup: str) -> str:
    """Aplatit le HTML (évite que le markdown le prenne pour du code à cause des indentations)."""
    return "\n".join(line.strip() for line in markup.strip().splitlines() if line.strip())


def e(txt) -> str:
    return html.escape(str(txt))


def short(title: str, limit: int = 90) -> str:
    return title if len(title) <= limit else title[:limit].rsplit(" ", 1)[0] + "…"


CSS = """
<style>
:root { --teal:#0f766e; --teal2:#14b8a6; --navy:#0b3b5b; --ink:#0b2a3c; --mut:#5b7285; --line:#d5e6e8; }
html, body, [class*="css"] { font-size: 17px; }
header[data-testid="stHeader"] { background: transparent; }
.stDeployButton, #MainMenu, footer { visibility: hidden; }
.block-container { padding-top: 1.2rem; max-width: 1320px; }

/* ---------- barre latérale ---------- */
[data-testid="stSidebar"] > div:first-child { background: linear-gradient(185deg,#04202f 0%,#0b3b5b 62%,#0f766e 130%); }
[data-testid="stSidebar"] { min-width: 290px !important; }
[data-testid="stSidebar"] * { color: #d7efee; }
.brand { display:flex; align-items:center; gap:12px; padding: 6px 6px 18px 6px; }
.brand .logo { width:44px; height:44px; border-radius:14px; display:flex; align-items:center; justify-content:center;
               background: linear-gradient(135deg,#14b8a6,#5eead4); color:#04202f; box-shadow:0 8px 20px rgba(20,184,166,.45); }
.brand b { font-size:1.35rem; color:#fff; letter-spacing:.3px; } .brand small { display:block; color:#7fd6cc; font-size:.72rem; letter-spacing:1.6px; text-transform:uppercase; }
.navlabel { font-size:.7rem; letter-spacing:2px; text-transform:uppercase; color:#6fb9b3; margin: 10px 6px 4px 6px; }
[data-testid="stSidebar"] .stButton button { width:100%; justify-content:flex-start; background:transparent; border:1px solid transparent;
        border-radius:12px; padding:.62rem .9rem; font-weight:600; color:#d7efee; transition: all .15s; }
[data-testid="stSidebar"] .stButton button > div, [data-testid="stSidebar"] .stButton button [data-testid="stMarkdownContainer"] { width:100%; justify-content:flex-start !important; text-align:left !important; }
[data-testid="stSidebar"] .stButton button:hover { background: rgba(255,255,255,.09); border-color: rgba(255,255,255,.12); color:#fff; }
[data-testid="stSidebar"] .stButton button[kind="primary"] { background: linear-gradient(90deg,#14b8a6,#0f766e); color:#fff;
        box-shadow: 0 8px 20px rgba(20,184,166,.35); }
.sidenote { margin-top:26px; padding:12px 14px; border-radius:14px; background:rgba(255,255,255,.07); border:1px solid rgba(255,255,255,.12);
            font-size:.8rem; line-height:1.4; display:flex; gap:10px; }

/* ---------- barre du haut ---------- */
.topbar { display:flex; justify-content:space-between; align-items:center; margin: 2px 0 14px 0; }
.topbar h2 { margin:0; font-size:1.7rem; color:var(--ink); } .crumb { color:var(--mut); font-size:.85rem; }
.chip { display:inline-flex; align-items:center; gap:7px; padding:6px 13px; border-radius:999px; font-size:.82rem; font-weight:600;
        background:#fff; border:1px solid var(--line); color:var(--navy); margin-left:8px; box-shadow:0 2px 8px rgba(11,59,91,.06); }
.chip.warn { background:#fff7ed; border-color:#fed7aa; color:#9a3412; }
.chip.ok { background:#ecfdf5; border-color:#a7f3d0; color:#065f46; }

/* ---------- bloc hero (pilule 3D) ---------- */
.st-key-hero { background: radial-gradient(800px 380px at 80% 45%, rgba(20,184,166,.55), transparent 62%),
        linear-gradient(135deg,#06243a 0%,#0b3b5b 48%,#0f766e 100%); border-radius:26px; padding:14px 32px 0 32px; margin-bottom:18px;
        overflow:hidden; box-shadow:0 24px 60px rgba(6,36,58,.32), inset 0 1px 0 rgba(255,255,255,.12); }
.st-key-hero iframe { background: transparent !important; }
.eyebrow { display:inline-flex; align-items:center; gap:8px; font-size:.76rem; letter-spacing:2px; text-transform:uppercase; color:#7fe9dc;
           background:rgba(255,255,255,.08); border:1px solid rgba(255,255,255,.18); padding:5px 14px; border-radius:999px; }
.herotitle { font-size:3.7rem; line-height:1; font-weight:900; margin:14px 0 10px 0; color:#fff; letter-spacing:-1px; }
.herotitle span { background:linear-gradient(90deg,#5eead4,#a7f3d0); -webkit-background-clip:text; color:transparent; }
.herosub { color:#cfeeee; font-size:1.1rem; max-width:520px; line-height:1.45; margin-bottom:14px; }
.chips span { display:inline-flex; align-items:center; gap:8px; margin:0 8px 10px 0; padding:7px 13px; border-radius:12px; color:#e6fffb; font-size:.88rem;
              background:rgba(255,255,255,.10); border:1px solid rgba(255,255,255,.18); }

/* ---------- cartes ---------- */
.kpis { display:grid; grid-template-columns: repeat(4, 1fr); gap:16px; margin-bottom:18px; }
.kpi { background:rgba(255,255,255,.9); border:1px solid #cfe5e7; border-radius:22px; padding:18px 20px; box-shadow:0 14px 34px rgba(11,59,91,.10); transition:transform .2s; }
.kpi:hover, .vcard:hover, .trial:hover { transform: translateY(-4px); }
.kpi .ic { width:44px; height:44px; border-radius:14px; display:flex; align-items:center; justify-content:center; color:#fff; margin-bottom:10px; }
.kpi .v { font-size:2.3rem; font-weight:900; color:var(--ink); line-height:1.1; } .kpi .l { color:var(--mut); font-size:.85rem; }
.verdict { display:grid; grid-template-columns: repeat(3, 1fr); gap:16px; margin: 4px 0 18px 0; }
.vcard { background:rgba(255,255,255,.9); border:1px solid #cfe5e7; border-radius:22px; padding:18px 22px; box-shadow:0 14px 34px rgba(11,59,91,.10); transition:transform .2s; }
.vcard .lab { color:var(--mut); font-size:.8rem; text-transform:uppercase; letter-spacing:.9px; display:flex; align-items:center; gap:8px; }
.vcard .big { font-size:2.6rem; font-weight:900; color:var(--teal); line-height:1.15; } .vcard .sub { color:var(--ink); font-size:.92rem; }
.gauge { display:flex; gap:4px; margin-top:8px; } .gauge span { flex:1; height:10px; border-radius:6px; background:#dbe7e9; }
.gauge span.on { animation: pop .9s ease both; } .gl { display:flex; justify-content:space-between; color:var(--mut); font-size:.72rem; margin-top:2px; }
.steps { display:grid; grid-template-columns: repeat(3, 1fr); gap:16px; }
.step { background:rgba(255,255,255,.9); border:1px solid #cfe5e7; border-radius:22px; padding:20px 22px; box-shadow:0 14px 34px rgba(11,59,91,.08); }
.step .n { color:var(--teal2); font-weight:800; letter-spacing:2px; font-size:.78rem; } .step h4 { margin:6px 0 4px 0; color:var(--ink); } .step p { margin:0; color:var(--mut); font-size:.92rem; }
.trial { background:rgba(255,255,255,.94); border:1px solid var(--line); border-left:6px solid var(--teal); border-radius:18px; padding:14px 16px;
         margin-bottom:14px; box-shadow:0 2px 8px rgba(11,59,91,.06); transition: transform .2s, box-shadow .2s; }
.trial:hover { box-shadow:0 16px 34px rgba(11,59,91,.16); }
.trial .nct { font-family: ui-monospace, monospace; color:var(--mut); font-size:.8rem; }
.trial .title { font-weight:700; color:var(--ink); font-size:.98rem; margin:4px 0 8px 0; }
.trial .row { display:flex; gap:8px; flex-wrap:wrap; align-items:center; font-size:.85rem; color:var(--ink); }
.trial .warn { margin-top:8px; font-size:.8rem; color:#92400e; background:#fffbeb; border-radius:8px; padding:6px 9px; display:flex; gap:8px; }
.trial a { color:var(--teal); font-weight:600; font-size:.85rem; text-decoration:none; display:inline-flex; align-items:center; gap:6px; }
.pill { display:inline-block; padding:3px 12px; border-radius:999px; font-weight:700; font-size:.8rem; color:#fff; }
.funnel { margin: 8px 0 18px 0; } .frow { display:flex; align-items:center; gap:12px; margin:9px 0; } .flabel { width:46%; font-size:.95rem; color:var(--ink); }
.fbarwrap { flex:1; background:#e1eef0; border-radius:10px; height:34px; overflow:hidden; }
.fbar { height:34px; border-radius:10px; display:flex; align-items:center; justify-content:flex-end; padding-right:12px; color:#fff; font-weight:800;
        background:linear-gradient(90deg,#14b8a6,#0f766e); animation: grow 1.3s ease both; }
@keyframes grow { from { width:0 } } @keyframes pop { from { transform:scaleY(0); } to { transform:scaleY(1); } }
.bignum { display:flex; align-items:center; gap:16px; margin:4px 0 10px 0; color:var(--teal2); }
.bignum .a { font-size:3rem; font-weight:800; color:var(--mut); } .bignum .b { font-size:4rem; font-weight:900; color:var(--teal); line-height:1; }
.rej { display:flex; align-items:center; gap:10px; margin:7px 0; } .rej .n { width:46px; text-align:right; font-weight:800; color:var(--navy); }
.rej .bar { height:20px; border-radius:6px; background:linear-gradient(90deg,#94a3b8,#64748b); animation: grow 1.1s ease both; }
.grp { background:#fff; border:1px solid var(--line); border-radius:18px; padding:16px 20px; box-shadow:0 8px 22px rgba(11,59,91,.07); }
.grp h4 { margin:0 0 6px 0; color:var(--navy); }
.dual { display:flex; align-items:center; gap:10px; margin:5px 0; font-size:.92rem; white-space:nowrap; } .dual .w { width:150px; color:var(--mut); }
.dual .b { height:18px; border-radius:6px; animation: grow 1.1s ease both; }
.cmp { display:grid; grid-template-columns: 1fr 1fr; gap:16px; }
.cmp .box { background:#fff; border:1px solid var(--line); border-radius:20px; padding:18px 22px; box-shadow:0 10px 26px rgba(11,59,91,.08); }
.cmp .box.tr { border-top:6px solid var(--teal); } .cmp .box.ai { border-top:6px solid #94a3b8; }
.cmp p { display:flex; gap:10px; align-items:flex-start; margin:10px 0; }
.ok { color:#16a34a; } .tbd { color:#b45309; }
.empty { background:#fff; border:2px dashed #b9d9dc; border-radius:22px; padding:46px; text-align:center; color:var(--mut); }
div[data-testid="stButton"] button { border-radius:12px; font-weight:700; }
.foot { color:var(--mut); font-size:.8rem; text-align:center; margin-top:28px; }
</style>
"""
st.markdown(CSS, unsafe_allow_html=True)


# ---------------------------------------------------------------- logique (inchangée)
@st.cache_data(show_spinner=False)
def run_analysis(text: str) -> dict:
    q = question.parse_question(text)
    screening = engine.screen_trials(q, engine.load_cvs())
    usable = engine.count_usable(fake_data.load(), q)
    groups = engine.group_summary(usable["data"], q)
    d = dossier.build_dossier(q, screening, engine.rejection_summary(screening), usable, groups)
    return {"q": q, "dossier": d, "markdown": dossier.to_markdown(d)}


for key, default in (("text", question.CAS_VEDETTE_TEXTE), ("result", None), ("error", None), ("page", PAGES[0][0])):
    st.session_state.setdefault(key, default)


def analyse():
    st.session_state["error"], st.session_state["result"] = None, None
    try:
        st.session_state["result"] = run_analysis(st.session_state["text"])
    except ValueError as exc:
        st.session_state["error"] = str(exc)
    except Exception as exc:
        st.session_state["error"] = f"Erreur inattendue : {exc}. Lancez `python -m src.fetch` puis `python -m src.cv`."


def demo():
    st.session_state["text"] = question.CAS_VEDETTE_TEXTE
    st.session_state["page"] = PAGES[0][0]
    analyse()


def goto(name: str):
    st.session_state["page"] = name


# ---------------------------------------------------------------- barre latérale
with st.sidebar:
    st.markdown(block(f"""
        <div class="brand"><div class="logo">{icon('pill', 26, '#04202f', 2.2)}</div>
        <div><b>TrialRevive</b><small>Adopt AI for Health</small></div></div>
        <div class="navlabel">Navigation</div>"""), unsafe_allow_html=True)
    for i, (name, mat) in enumerate(PAGES):
        st.button(name, icon=mat, key=f"nav_{i}", use_container_width=True,
                  type="primary" if st.session_state["page"] == name else "secondary", on_click=goto, args=(name,))
    st.markdown(block(f"""
        <div class="sidenote">{icon('lock', 20, '#5eead4')}<div>Données publiques ou fabriquées.<br>Aucun patient réel.</div></div>
        <div class="sidenote">{icon('database', 20, '#5eead4')}<div>Source : ClinicalTrials.gov<br>+ essai interne fictif</div></div>"""),
        unsafe_allow_html=True)

res = st.session_state["result"]
page = st.session_state["page"]

# ---------------------------------------------------------------- barre du haut + question
status = (f'<span class="chip ok">{icon("check", 16)} Analyse prête</span>' if res
          else f'<span class="chip">{icon("pulse", 16)} En attente d\'une question</span>')
st.markdown(block(f"""
    <div class="topbar"><div><div class="crumb">TrialRevive / {e(page)}</div><h2>{e(page)}</h2></div>
    <div>{status}<span class="chip warn">{icon('alert', 16)} Prototype · données fictives</span></div></div>"""),
    unsafe_allow_html=True)

with st.container(border=True):
    st.text_area("Votre question scientifique", key="text", height=78)
    b1, b2, _ = st.columns([1.7, 2.1, 5])
    b1.button("Analyser", type="primary", icon=":material/search:", on_click=analyse)
    b2.button("Cas de démo", icon=":material/play_arrow:", on_click=demo)

if st.session_state["error"]:
    st.error(st.session_state["error"])

st.write("")


def gauge(level: str) -> str:
    idx = E_LEVELS.index(level)
    segs = "".join(f'<span class="{"on" if i <= idx else ""}" style="{"background:" + E_COLORS[level] if i <= idx else ""}"></span>' for i in range(5))
    return f'<div class="gauge">{segs}</div><div class="gl">{"".join(f"<span>{l}</span>" for l in E_LEVELS)}</div>'


def need_result():
    st.markdown(block(f"""<div class="empty">{icon('flask', 46, '#14b8a6', 1.6)}
        <h3>Aucune analyse pour le moment</h3>Cliquez sur « Cas de démo » ou posez votre question ci-dessus.</div>"""),
        unsafe_allow_html=True)


# ---------------------------------------------------------------- pages
if page == "Tableau de bord":
    hero = st.container(key="hero")
    with hero:
        hc1, hc2 = st.columns([3, 2], vertical_alignment="center")
        with hc1:
            st.markdown(block(f"""
                <div class="eyebrow">{icon('target', 16)} Hackathon · Adopt AI for Health</div>
                <div class="herotitle">Trial<span>Revive</span></div>
                <div class="herosub">Une question scientifique entre. Un dossier de faisabilité sort : quels essais, quelle preuve, quel gain.</div>
                <div class="chips"><span>{icon('flask', 17)} Essais cliniques publics</span><span>{icon('pill', 17)} Marqueur KRAS</span><span>{icon('shield', 17)} Données jamais exposées</span></div>"""),
                unsafe_allow_html=True)
        with hc2:
            render_pill(height=330)

    if not res:
        st.markdown(block(f"""<div class="steps">
            <div class="step"><div class="n">ÉTAPE 1</div>{icon('search', 30, '#14b8a6')}<h4>La question</h4><p>Une hypothèse scientifique devient une liste d'exigences précises.</p></div>
            <div class="step"><div class="n">ÉTAPE 2</div>{icon('flask', 30, '#14b8a6')}<h4>Le tri des essais</h4><p>Chaque essai est comparé aux exigences, avec la raison de chaque refus.</p></div>
            <div class="step"><div class="n">ÉTAPE 3</div>{icon('file', 30, '#14b8a6')}<h4>Le dossier</h4><p>Un verdict sourcé : comment répondre, quelle preuve, quel gain.</p></div></div>"""),
            unsafe_allow_html=True)
    else:
        d = res["dossier"]
        v = d["verdict"]
        n_usable = d["utilisables"] if d["utilisables"] is not None else "?"
        st.markdown(block(f"""<div class="kpis">
            <div class="kpi"><div class="ic" style="background:linear-gradient(135deg,#0b3b5b,#0f766e)">{icon('database', 24, '#fff')}</div><div class="v">{d['rejection']['total']}</div><div class="l">essais publics analysés</div></div>
            <div class="kpi"><div class="ic" style="background:linear-gradient(135deg,#0f766e,#14b8a6)">{icon('check', 24, '#fff')}</div><div class="v">{len(d['retenus'])}</div><div class="l">essais retenus</div></div>
            <div class="kpi"><div class="ic" style="background:linear-gradient(135deg,#64748b,#94a3b8)">{icon('target', 24, '#fff')}</div><div class="v">{d['rejection']['total'] - len(d['retenus'])}</div><div class="l">essais écartés, avec raison</div></div>
            <div class="kpi"><div class="ic" style="background:linear-gradient(135deg,#14b8a6,#5eead4)">{icon('users', 24, '#04202f')}</div><div class="v">{n_usable}</div><div class="l">patients analysables (fictifs)</div></div></div>"""),
            unsafe_allow_html=True)
        g_codes = " · ".join(x["code"] for x in v["G"])
        st.markdown(block(f"""<div class="verdict">
            <div class="vcard"><div class="lab">{icon('pulse', 16)} R · Comment obtenir la réponse</div><div class="big">{e(v['R'])}</div><div class="sub">{e(v['R_texte'])}</div></div>
            <div class="vcard"><div class="lab">{icon('shield', 16)} E · Force de la preuve (atteignable)</div><div class="big" style="color:{E_COLORS[v['E']]}">{e(v['E'])}</div><div class="sub">{e(v['E_texte'])}</div>{gauge(v['E'])}</div>
            <div class="vcard"><div class="lab">{icon('gain', 16)} G · Ce que ça apporte</div><div class="big">{len(v['G'])}</div><div class="sub">{e(g_codes)}</div></div></div>"""),
            unsafe_allow_html=True)
        if not v["preuve_verifiee"]:
            st.markdown(f'<span class="chip warn" style="margin-left:0">{icon("alert", 16)} Références des réanalyses en cours de vérification par un humain</span>',
                        unsafe_allow_html=True)

elif page == "Essais retenus":
    if not res:
        need_result()
    else:
        d = res["dossier"]
        st.subheader(f"{len(d['retenus'])} essais sur {d['rejection']['total']} peuvent répondre")
        cols = st.columns(3)
        for i, r in enumerate(d["retenus"]):
            exact = r["niveau"] == "direct"
            warn = f'<div class="warn">{icon("alert", 16, "#92400e")}<span>{e(" ; ".join(r["ecarts"]))}</span></div>' if r["ecarts"] else ""
            cols[i % 3].markdown(block(f"""
                <div class="trial" style="border-left-color:{'#0f766e' if exact else '#f59e0b'}">
                <div class="nct">{e(r['nct_id'])}</div><div class="title">{e(short(r['titre']))}</div>
                <div class="row"><span class="pill" style="background:{E_COLORS[r['E']]}">Preuve {e(r['E'])}</span>
                <span class="pill" style="background:{'#0f766e' if exact else '#64748b'}">{'Médicament exact' if exact else 'Même classe'}</span>
                <span style="display:inline-flex;gap:5px;align-items:center">{icon('users', 15, '#5b7285')} {r['nb_patients']}</span><span>score {r['score']}</span></div>{warn}
                <div style="margin-top:8px"><a href="{e(r['lien'])}" target="_blank">Voir sur ClinicalTrials.gov {icon('link', 14)}</a></div></div>"""),
                unsafe_allow_html=True)

elif page == "Essais écartés":
    if not res:
        need_result()
    else:
        d = res["dossier"]
        rs = d["rejection"]
        st.subheader(f"{rs['total'] - rs['retenus']} essais écartés, chacun avec sa raison")
        mx = max(rs["ecartes_par_etape"].values()) or 1
        st.markdown(block("".join(
            f'<div class="rej"><div class="n">{n}</div><div class="bar" style="width:{max(3, 100 * n / mx) * 0.7:.0f}%"></div><div>{e(label)}</div></div>'
            for label, n in sorted(rs["ecartes_par_etape"].items(), key=lambda x: -x[1]))), unsafe_allow_html=True)
        with st.expander("Voir la liste complète avec la raison de chaque rejet"):
            st.dataframe(pd.DataFrame([{"NCT": r["nct_id"], "Essai": r["titre"], "Raison": r["raison"], "Lien": r["lien"]} for r in d["ecartes"]]),
                         hide_index=True, use_container_width=True, column_config={"Lien": st.column_config.LinkColumn("Lien")})

elif page == "Patients":
    if not res:
        need_result()
    else:
        d = res["dossier"]
        st.markdown(f'<span class="chip warn" style="margin-left:0">{icon("alert", 16)} DONNÉES FICTIVES : aucun patient réel</span>', unsafe_allow_html=True)
        f = d["entonnoir"]
        if d["utilisables"] is None:
            st.markdown("### Comptage INDÉTERMINÉ : le lien entre les données n'est pas validé")
        else:
            st.markdown(block(f"""<div class="bignum"><span class="a">{f[0]['n']}</span>{icon('arrow', 38, '#14b8a6', 2.4)}
                <span class="b">{d['utilisables']}</span><span style="color:#0b2a3c">patients réellement analysables</span></div>"""), unsafe_allow_html=True)
        top = f[0]["n"] or 1
        st.markdown('<div class="funnel">' + block("".join(
            f'<div class="frow"><div class="flabel">{e(s["etape"])}</div><div class="fbarwrap"><div class="fbar" style="width:{100 * s["n"] / top:.0f}%;animation-delay:{i * 0.25}s">{s["n"]}</div></div></div>'
            for i, s in enumerate(f))) + "</div>", unsafe_allow_html=True)
        for col, g in zip(st.columns(2), d["groupes"]):
            mt, mc = g["mediane_traite"], g["mediane_controle"]
            if mt is None or mc is None:
                col.markdown(f'<div class="grp"><h4>KRAS {e(g["statut"])}</h4>Effectif trop petit : masqué (&lt;5)</div>', unsafe_allow_html=True)
                continue
            scale = max(mt, mc) or 1
            col.markdown(block(f"""<div class="grp"><h4>KRAS {e(g['statut'])} — gain : {g['gain_mois']:+} mois</h4>
                <div class="dual"><div class="w">Avec traitement</div><div class="b" style="width:{100 * mt / scale * 0.55:.0f}%;background:#0f766e"></div>{mt} mois</div>
                <div class="dual"><div class="w">Sans traitement</div><div class="b" style="width:{100 * mc / scale * 0.55:.0f}%;background:#94a3b8"></div>{mc} mois</div>
                <div style="color:#5b7285;font-size:.8rem">Survie médiane. {g['n_traite']} traités, {g['n_controle']} contrôles.</div></div>"""), unsafe_allow_html=True)

elif page == "Dossier":
    if not res:
        need_result()
    else:
        st.download_button("Télécharger le dossier (Markdown)", res["markdown"], "dossier_trialrevive.md", "text/markdown", icon=":material/download:")
        st.markdown(res["markdown"])

elif page == "Comparaison":
    if not res:
        need_result()
    else:
        d = res["dossier"]
        loaded = []
        for fpath in (sorted(BASELINE_DIR.glob("*.json")) if BASELINE_DIR.exists() else []):
            try:
                loaded.append(json.loads(fpath.read_text(encoding="utf-8")))
            except json.JSONDecodeError:
                continue
        b = loaded[0] if loaded else {}
        ia_answer = e(b.get("reponse_ia", "À tester en direct devant le jury : poser la même question à une IA généraliste."))
        ia = lambda k: b.get(k, "à tester en direct")  # noqa: E731
        ck, hp = icon("check", 20, "#16a34a", 2.6), icon("help", 20, "#b45309", 2.2)
        st.markdown(block(f"""<div class="cmp">
            <div class="box tr"><h3 style="display:flex;gap:10px;align-items:center">{icon('pill', 26, '#0f766e')} TrialRevive</h3>
              <p>{ck}<span>{len(d['retenus'])} essais retenus, {d['rejection']['total'] - len(d['retenus'])} écartés avec raison</span></p>
              <p>{ck}<span>Compte les patients réellement analysables ({d['utilisables']})</span></p>
              <p>{ck}<span>Sources cliquables (ClinicalTrials.gov)</span></p>
              <p>{ck}<span>Même question = même résultat</span></p></div>
            <div class="box ai"><h3 style="display:flex;gap:10px;align-items:center">{icon('search', 26, '#64748b')} IA généraliste</h3>
              <p>{hp}<span>Compte les patients : {e(ia('compte_patients'))}</span></p>
              <p>{hp}<span>Sources vérifiables : {e(ia('sources_verifiables'))}</span></p>
              <p>{hp}<span>Explique les rejets : {e(ia('explique_rejets'))}</span></p>
              <p style="color:#5b7285;font-size:.85rem">{ia_answer[:600]}</p></div></div>"""), unsafe_allow_html=True)
        if not loaded:
            st.caption("Aucune réponse enregistrée : voir data/baseline/LISEZ_MOI.md pour remplir cette colonne avec une vraie réponse.")

st.markdown('<div class="foot">Prototype · essais publics ClinicalTrials.gov + essai interne fictif · aucune donnée de santé réelle</div>', unsafe_allow_html=True)
