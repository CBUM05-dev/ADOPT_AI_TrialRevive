"""Garde-fous de style (base : docs/charte/CHARTE_GRAPHIQUE.md).

Écart assumé à la charte : un accent « vert médical » (et de l'ambre pour les alertes) s'ajoute à la palette grise,
parce que le tout gris était jugé trop sombre pour un produit de santé. Cet écart est listé ci-dessous et nulle part ailleurs.
Restent interdits : ombres, dégradés, coins arrondis, effets 3D, autres polices que Manrope, ressources distantes.
"""
import re
from pathlib import Path

WEB = Path(__file__).resolve().parent.parent / "web"
FILES = [WEB / "css" / "app.css", WEB / "js" / "app.js", WEB / "js" / "illustration.js", WEB / "index.html"]

# Palette officielle de la charte + trois gris du filigrane et des bordures de tableau cités par la charte
CHARTE = {"0a0a0a", "262626", "4a4a4a", "6e6e6e", "bdbdbd", "e4e4e4", "f5f5f5", "ffffff", "d9d9d9", "171717", "ededed", "d0d0d0"}
# Accent médical (vert, menthe, ambre d'alerte) et tons des illustrations de personnages
ACCENT = {
    "1b7f58", "115a3d", "6fcf9f", "b8ecd2", "e3f5ec", "86d1ae", "3fae7f", "bfe6d3", "dbe4df",
    "7a4d00", "fff3d6", "efd08a", "d99a0b",
    "f1c7a3", "8c5a3c", "e3ab83", "2b2b2b", "1d1d1d", "1a1a1a",
}


def read(path):
    return path.read_text(encoding="utf-8")


def test_only_listed_colors():
    for path in FILES:
        for m in re.finditer(r"#([0-9a-fA-F]{3}|[0-9a-fA-F]{6})\b", read(path)):
            value = m.group(1).lower()
            value = value * 2 if len(value) == 3 and value == value[0] * 3 else value
            assert value in CHARTE | ACCENT, f"{path.name} : couleur non listée #{m.group(1)}"


def test_rgba_is_neutral_only():
    for path in FILES:
        text = read(path)
        assert "hsl" not in text.lower(), f"{path.name} : hsl interdit"
        for m in re.finditer(r"rgba?\(([^)]*)\)", text):
            channels = [c.strip() for c in re.split(r"[ ,/]+", m.group(1)) if c.strip()]
            assert len({channels[0], channels[1], channels[2]}) == 1, f"{path.name} : couleur non listée {m.group(0)}"


def test_square_corners_no_shadow_gradient_or_3d():
    css = read(WEB / "css" / "app.css")
    for value in re.findall(r"border-radius\s*:\s*([^;]+);", css):
        assert value.strip() in ("0", "0px"), f"coin arrondi interdit : {value}"
    for banned in ("box-shadow", "text-shadow", "drop-shadow", "gradient(", "backdrop-filter", "perspective", "rotate3d"):
        assert banned not in css, f"effet interdit : {banned}"
    assert "three" not in read(WEB / "index.html").lower()  # plus de 3D
    assert not (WEB / "js" / "capsule.js").exists()


def test_manrope_everywhere_and_no_remote_resource():
    css = read(WEB / "css" / "app.css")
    families = set(re.findall(r"font-family\s*:\s*([^;]+);", css)) | set(re.findall(r"--police\s*:\s*([^;]+);", css))
    assert families and all("Manrope" in f or "var(--police)" in f for f in families)
    assert (WEB / "fonts" / "Manrope-Variable.ttf").exists()
    for path in FILES:
        text = re.sub(r"http://www\.w3\.org/\d+/svg", "", read(path))
        assert "http://" not in text and "https://" not in text, f"ressource distante dans {path.name}"


def test_official_logo_is_used_unmodified():
    html = read(WEB / "index.html")
    assert "TrialRevive_logo_horizontal_noir.svg" in html
    logo = read(WEB / "brand" / "TrialRevive_logo_horizontal_noir.svg")
    assert 'aria-label="TrialRevive"' in logo and "#0A0A0A" in logo
