"""Brique : essai interne FICTIF (400 faux patients). Aucune donnée réelle. Reproductible (seed fixe).

Usage : python -m src.fake_data
"""
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "data" / "internal_trial.csv"
N = 400
SEED = 42
HEADER = "# DONNÉES FICTIVES - générées par programme (seed=42). Aucun patient réel.\n"

# Effet fabriqué : le traitement aide les KRAS sauvages, pas les mutés
MEDIAN_MONTHS = {
    ("controle", "sauvage"): 9.0,
    ("panitumumab", "sauvage"): 14.0,
    ("controle", "muté"): 9.0,
    ("panitumumab", "muté"): 8.0,
    ("controle", "inconnu"): 9.0,
    ("panitumumab", "inconnu"): 11.0,
}


def generate(n: int = N, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    traitement = rng.permutation(np.array(["panitumumab", "controle"] * (n // 2)))
    kras = rng.choice(["muté", "sauvage", "inconnu"], size=n, p=[0.40, 0.50, 0.10])

    methode = np.empty(n, dtype=object)
    for i, k in enumerate(kras):
        if k == "inconnu":
            methode[i] = "non testé"
        else:
            methode[i] = rng.choice(
                ["KRAS exons 2-4 (complet)", "KRAS exon 2 seulement", "test partiel (non valide)"],
                p=[0.70, 0.20, 0.10],
            )

    medians = np.array([MEDIAN_MONTHS[(t, k)] for t, k in zip(traitement, kras)])
    true_time = rng.exponential(medians / np.log(2))  # exponentielle : médiane = scale*ln2
    followup = rng.uniform(12, 40, size=n)
    evenement = (true_time <= followup).astype(int)
    survie = np.round(np.minimum(true_time, followup), 1)

    df = pd.DataFrame(
        {
            "patient_id": [f"FAKE-{i + 1:04d}" for i in range(n)],
            "age": np.clip(rng.normal(63, 10, n).round(), 30, 90).astype(int),
            "sexe": rng.choice(["F", "M"], size=n),
            "traitement": traitement,
            "kras_statut": kras,
            "methode_test": methode,
            "survie_mois": survie,
            "evenement": evenement,
            "date_inclusion": pd.to_datetime("2015-01-01") + pd.to_timedelta(rng.integers(0, 365 * 5, n), unit="D"),
        }
    )
    # valeurs manquantes volontaires (~5 % de survie non renseignée)
    missing = rng.choice(n, size=int(0.05 * n), replace=False)
    df.loc[missing, "survie_mois"] = np.nan
    df["date_inclusion"] = df["date_inclusion"].dt.strftime("%Y-%m-%d")
    return df


def write(path: Path = OUT) -> pd.DataFrame:
    path.parent.mkdir(parents=True, exist_ok=True)
    df = generate()
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(HEADER)
        df.to_csv(f, index=False)
    return df


def load(path: Path = OUT) -> pd.DataFrame:
    if not path.exists():
        write(path)
    return pd.read_csv(path, comment="#")


if __name__ == "__main__":
    df = write()
    print(f"{len(df)} faux patients -> {OUT}")
    print(df["kras_statut"].value_counts(normalize=True).round(2).to_dict())
