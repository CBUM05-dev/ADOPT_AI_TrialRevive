"""Serveur web TrialRevive : API JSON + interface (dossier web/).

Lancer :  python server.py          puis ouvrir http://localhost:8000
Réutilise la logique de src/ sans la modifier. Fonctionne hors ligne (polices et 3D en local).
"""
import json
import sys
from functools import lru_cache
from pathlib import Path

import numpy as np
from starlette.applications import Starlette
from starlette.responses import FileResponse, JSONResponse, PlainTextResponse
from starlette.routing import Mount, Route
from starlette.staticfiles import StaticFiles

from src import compare, dossier, engine, fake_data, question

WEB = Path(__file__).resolve().parent / "web"
MAX_BODY = 2_000_000  # 2 Mo : suffisant pour une réponse d'IA importée


def _default(o):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return None if np.isnan(o) else float(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return str(o)


class Json(JSONResponse):
    def render(self, content) -> bytes:
        return json.dumps(content, ensure_ascii=False, default=_default).encode("utf-8")


@lru_cache(maxsize=32)
def analyse(text: str) -> dict:
    q = question.parse_question(text)
    screening = engine.screen_trials(q, engine.load_cvs())
    usable = engine.count_usable(fake_data.load(), q)
    groups = engine.group_summary(usable["data"], q)
    d = dossier.build_dossier(q, screening, engine.rejection_summary(screening), usable, groups)
    return {"question": q, "dossier": d, "markdown": dossier.to_markdown(d)}


async def read_json(request):
    body = await request.body()
    if len(body) > MAX_BODY:
        raise ValueError("Requête trop volumineuse.")
    try:
        data = json.loads(body.decode("utf-8") or "{}")
    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
        raise ValueError("JSON invalide.") from exc
    if not isinstance(data, dict):
        raise ValueError("Un objet JSON est attendu.")
    return data


def bad(message: str, status: int = 400):
    return Json({"error": message}, status_code=status)


async def api_analyze(request):
    try:
        data = await read_json(request)
        text = str(data.get("question") or "").strip()
        if not text:
            return bad("Écrivez une question avant de lancer l'analyse.")
        if len(text) > 600:
            return bad("La question est trop longue (600 caractères maximum).")
        out = analyse(text)
    except ValueError as exc:
        return bad(str(exc))
    except Exception as exc:  # base absente, etc.
        return bad(f"Analyse impossible : {exc}. Avez-vous lancé « python -m src.fetch --offline » puis « python -m src.cv » ?", 500)
    return Json({"dossier": out["dossier"], "markdown": out["markdown"], "exemple": question.CAS_VEDETTE_TEXTE})


async def api_info(request):
    return Json({"exemple": question.CAS_VEDETTE_TEXTE})


async def api_baselines(request):
    records, errors = compare.load_baselines()
    return Json({"records": records, "errors": errors})


async def api_baseline_validate(request):
    try:
        data = await read_json(request)
        record = compare.parse_record(str(data.get("text") or ""))
    except ValueError as exc:
        return bad(str(exc))
    return Json({"record": record})


async def api_baseline_archive(request):
    try:
        data = await read_json(request)
        path = compare.archive_record(data.get("record"))
    except (ValueError, OSError) as exc:
        return bad(str(exc))
    return Json({"archive": path.name})


async def api_compare(request):
    try:
        data = await read_json(request)
        record = compare.validate_record(data.get("record"))
        d = analyse(str(data.get("question") or question.CAS_VEDETTE_TEXTE).strip())["dossier"]
    except ValueError as exc:
        return bad(str(exc))
    return Json({
        "rows": compare.comparison_rows(d, record),
        "meme_question": compare.same_question(d["question"], record["question"]),
        "nct": compare.audit_nct_references(record["reponse_ia"]),
    })


async def api_dossier_md(request):
    text = request.query_params.get("question") or question.CAS_VEDETTE_TEXTE
    try:
        md = analyse(text.strip())["markdown"]
    except ValueError as exc:
        return PlainTextResponse(str(exc), status_code=400)
    return PlainTextResponse(md, media_type="text/markdown; charset=utf-8",
                             headers={"Content-Disposition": 'attachment; filename="dossier_trialrevive.md"'})


class FreshStatic(StaticFiles):
    """Fichiers statiques toujours revalidés : on voit la dernière version après une modification."""

    def file_response(self, *args, **kwargs):
        response = super().file_response(*args, **kwargs)
        response.headers["Cache-Control"] = "no-cache"
        return response


async def index(request):
    return FileResponse(WEB / "index.html", headers={"Cache-Control": "no-cache"})


routes = [
    Route("/", index),
    Route("/api/info", api_info),
    Route("/api/analyze", api_analyze, methods=["POST"]),
    Route("/api/baselines", api_baselines),
    Route("/api/baselines/validate", api_baseline_validate, methods=["POST"]),
    Route("/api/baselines/archive", api_baseline_archive, methods=["POST"]),
    Route("/api/compare", api_compare, methods=["POST"]),
    Route("/api/dossier.md", api_dossier_md),
    Mount("/assets", FreshStatic(directory=WEB), name="assets"),
]
app = Starlette(routes=routes)

if __name__ == "__main__":
    import uvicorn

    port = int(sys.argv[1]) if len(sys.argv) > 1 else 8000
    print(f"TrialRevive : http://localhost:{port}")
    uvicorn.run(app, host="127.0.0.1", port=port, log_level="warning")
