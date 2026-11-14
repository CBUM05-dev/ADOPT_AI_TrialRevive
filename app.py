import json
from pathlib import Path

import pandas as pd
import streamlit as st

from src import dossier, engine, fake_data, question

BASELINE_DIR = Path(__file__).parent / "data" / "baseline"

st.set_page_config(page_title="TrialRevive", page_icon="🧪", layout="wide")
st.markdown("<style>html, body, [class*='css'] {font-size: 18px;}</style>", unsafe_allow_html=True)

st.title("TrialRevive")
st.caption("Une question scientifique entre, un dossier de faisabilité sort. "
           "Prototype : essais publics (ClinicalTrials.gov) + essai interne FICTIF.")


@st.cache_data(show_spinner=False)
def run_analysis(text: str) -> dict:
    q = question.parse_question(text)
    cvs = engine.load_cvs()
    screening = engine.screen_trials(q, cvs)
    usable = engine.count_usable(fake_data.load(), q)
    groups = engine.group_summary(usable["data"], q)
    d = dossier.build_dossier(q, screening, engine.rejection_summary(screening), usable, groups)
    return {"q": q, "dossier": d, "markdown": dossier.to_markdown(d)}


if "text" not in st.session_state:
    st.session_state["text"] = question.CAS_VEDETTE_TEXTE
if "result" not in st.session_state:
    st.session_state["result"] = None
if "error" not in st.session_state:
    st.session_state["error"] = None


def analyse():
    st.session_state["error"], st.session_state["result"] = None, None
    try:
        st.session_state["result"] = run_analysis(st.session_state["text"])
    except ValueError as exc:
        st.session_state["error"] = str(exc)
    except Exception as exc:  # base absente, etc.
        st.session_state["error"] = f"Erreur inattendue : {exc}. Avez-vous lancé `python -m src.fetch` puis `python -m src.cv` ?"


def demo():
    st.session_state["text"] = question.CAS_VEDETTE_TEXTE
    analyse()


st.text_area("Votre question scientifique", key="text", height=90)
c1, c2, _ = st.columns([1, 1, 4])
c1.button("Analyser", type="primary", on_click=analyse)
c2.button("Cas de démo", on_click=demo)

if st.session_state["error"]:
    st.error(st.session_state["error"])

res = st.session_state["result"]
if res:
    d = res["dossier"]
    tabs = st.tabs(["Essais retenus", "Essais écartés", "Patients (fictifs)", "Dossier final", "Comparaison IA"])

    with tabs[0]:
        v = d["verdict"]
        m1, m2, m3 = st.columns(3)
        m1.metric("R : comment obtenir la réponse", v["R"], v["R_texte"][:45], delta_color="off")
        m2.metric("E : force de la preuve (atteignable)", v["E"], v["E_texte"], delta_color="off")
        m3.metric("G : gains possibles", len(v["G"]), ", ".join(g["code"] for g in v["G"]), delta_color="off")
        st.subheader(f"{len(d['retenus'])} essais peuvent répondre à la question")
        st.dataframe(
            pd.DataFrame(
                [{"NCT": r["nct_id"], "Essai": r["titre"], "Patients": r["nb_patients"],
                  "Médicament": "exact" if r["niveau"] == "direct" else "même classe",
                  "Preuve": r["E"], "Score": r["score"],
                  "Écarts tolérés": " ; ".join(r["ecarts"]) or "aucun",
                  "Lien": r["lien"]} for r in d["retenus"]]
            ),
            hide_index=True, use_container_width=True,
            column_config={"Lien": st.column_config.LinkColumn("Lien")},
        )

    with tabs[1]:
        rs = d["rejection"]
        st.subheader(f"{rs['total'] - rs['retenus']} essais écartés sur {rs['total']}, avec la raison")
        st.bar_chart(pd.Series(rs["ecartes_par_etape"]))
        st.dataframe(
            pd.DataFrame([{"NCT": r["nct_id"], "Essai": r["titre"], "Raison du rejet": r["raison"], "Lien": r["lien"]}
                          for r in d["ecartes"]]),
            hide_index=True, use_container_width=True,
            column_config={"Lien": st.column_config.LinkColumn("Lien")},
        )

    with tabs[2]:
        if d["utilisables"] is None:
            st.subheader("Comptage INDÉTERMINÉ : le lien entre les données n'est pas validé")
        else:
            st.subheader(f"{d['utilisables']} patients complets sur {d['entonnoir'][0]['n']} (données FICTIVES)")
        funnel = pd.DataFrame(d["entonnoir"]).set_index("etape")[["n"]]
        st.bar_chart(funnel)
        st.dataframe(pd.DataFrame(d["groupes"]), hide_index=True, use_container_width=True)
        st.caption("Médianes de survie (Kaplan-Meier) en mois. Descriptif sur données fabriquées, pas un test statistique.")

    with tabs[3]:
        st.markdown(res["markdown"])
        st.download_button("Télécharger le dossier (Markdown)", res["markdown"], "dossier_trialrevive.md", "text/markdown")

    with tabs[4]:
        files = sorted(BASELINE_DIR.glob("*.json")) if BASELINE_DIR.exists() else []
        if not files:
            st.info("Aucune réponse d'IA généraliste enregistrée. Voir data/baseline/LISEZ_MOI.md pour les ajouter.")
        for f in files:
            try:
                b = json.loads(f.read_text(encoding="utf-8"))
            except json.JSONDecodeError:
                st.warning(f"{f.name} illisible")
                continue
            st.markdown(f"#### Question : {b.get('question', f.stem)}")
            a, t = st.columns(2)
            a.markdown("**IA généraliste**  \n" + str(b.get("reponse_ia", "")))
            a.caption(f"Modèle : {b.get('modele', '?')} — {b.get('date', '?')}")
            t.markdown("**TrialRevive**  \n" + f"{len(d['retenus'])} essais retenus, {d['utilisables']} patients utilisables comptés, sources cliquables.")
            st.table(pd.DataFrame(
                {"Critère": ["Compte les patients utilisables ?", "Sources vérifiables ?", "Explique les rejets ?"],
                 "IA généraliste": [b.get("compte_patients", "?"), b.get("sources_verifiables", "?"), b.get("explique_rejets", "?")],
                 "TrialRevive": ["oui", "oui (liens NCT)", "oui"]}))
