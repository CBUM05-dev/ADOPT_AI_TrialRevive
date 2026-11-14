"""Dossier de secours hors ligne, sans serveur ni API.

Usage : python -m src.demo --output-dir outputs/demo
Préparer la base avec src.fetch --offline puis src.cv.
"""
import argparse
import html
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from src import dossier, engine, fake_data, question


def export_demo(output_dir: Path) -> dict:
    started = time.perf_counter()
    q = question.parse_question(question.CAS_VEDETTE_TEXTE)
    screening = engine.screen_trials(q, engine.load_cvs())
    usable = engine.count_usable(fake_data.load(), q)
    groups = engine.group_summary(usable["data"], q)
    d = dossier.build_dossier(q, screening, engine.rejection_summary(screening), usable, groups)
    summary = {
        "question": q["question"],
        "essais_publics": d["rejection"]["total"],
        "retenus": len(d["retenus"]),
        "ecartes": len(d["ecartes"]),
        "ecartes_par_etape": d["rejection"]["ecartes_par_etape"],
        "patients_fictifs": d["entonnoir"][0]["n"],
        "patients_complets": d["utilisables"],
        "entonnoir": [{"etape": r["etape"], "n": r["n_publie"]} for r in d["entonnoir"]],
        "preuve_atteignable": d["verdict"]["E"],
        "preuve_validee": d["verdict"]["preuve_verifiee"],
        "question_validee_par_humain": q["validee_par_humain"],
        "genere_le_utc": datetime.now(timezone.utc).isoformat(),
        "duree_calcul_secondes": round(time.perf_counter() - started, 3),
    }
    markdown = dossier.to_markdown(d)
    sources = "".join(
        f'<li><a href="{html.escape(s["lien"], quote=True)}">{html.escape(s["nct_id"])}</a>'
        + (f' — <a href="{html.escape(s["publication_lien"], quote=True)}">publication</a>'
           if s.get("publication_lien") else "") + " (validation scientifique à faire)</li>"
        for s in d["sources"])
    page = f"""<!doctype html>
<html lang="fr"><meta charset="utf-8"><meta name="viewport" content="width=device-width">
<title>TrialRevive — dossier de secours</title>
<style>body{{font:18px/1.6 system-ui,sans-serif;max-width:1100px;margin:40px auto;padding:0 24px;color:#0b2a3c;background:#f4fafb}}
h1{{color:#0f766e}}.notice{{padding:16px;background:#fff7ed;border:1px solid #fed7aa}}
pre{{white-space:pre-wrap;font:inherit;background:white;padding:24px;border:1px solid #d5e6e8}}a{{color:#0f766e}}</style>
<h1>TrialRevive — démonstration hors ligne</h1>
<p class="notice">Essais publics et patients FICTIFS uniquement. Preuve atteignable, non validée.
Cette page est un export statique ; ce n'est pas une vidéo ni une analyse clinique validée.</p>
<p><b>{summary['essais_publics']} essais · {summary['retenus']} retenus · {summary['ecartes']} écartés
· {summary['patients_complets']} patients fictifs complets sur {summary['patients_fictifs']}</b></p>
<pre>{html.escape(markdown)}</pre><h2>Sources à consulter en ligne</h2><ul>{sources}</ul></html>
"""
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "dossier.md").write_text(markdown, encoding="utf-8")
    (output_dir / "dossier.html").write_text(page, encoding="utf-8")
    (output_dir / "chiffres.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/demo"))
    args = parser.parse_args()
    summary = export_demo(args.output_dir)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"Dossier statique : {(args.output_dir / 'dossier.html').resolve()}")


if __name__ == "__main__":
    main()
