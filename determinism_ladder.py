#!/usr/bin/env python3
"""
KAIROS — ÉCHELLE DE DÉTERMINISME NUMÉRIQUE — v1.0
===================================================
Question : le déterminisme byte-identique survit-il au calcul flottant ?

Protocole : escalade en 6 niveaux, du hachage pur (doit passer) au ML multi-thread
(cassera probablement). Le niveau où ça casse EST le résultat.

Ce script :
  1. Déclare une enveloppe d'exécution scellée (OS, architecture, versions,
     configuration BLAS, threads, hashseed).
  2. Vérifie explicitement si l'environnement courant y correspond, avant
     toute mesure.
  3. À l'intérieur de l'enveloppe uniquement, répète les mesures N fois pour
     détecter une instabilité qu'un seul passage ne verrait pas.
  4. Produit un verdict machine-readable en deux temps :
       SEALED_RUNTIME_MATCH | OUTSIDE_SEALED_RUNTIME
       puis, seulement si scellé : DETERMINISM_PASS | DETERMINISM_FAIL

Hors enveloppe, les mesures sont affichées à titre informatif — jamais
comparées aux empreintes de référence, jamais qualifiées de PASS/FAIL.

Usage :
    OPENBLAS_CORETYPE=Haswell \\
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \\
    PYTHONHASHSEED=0 python3 determinism_ladder.py

Lecture seule. N'écrit rien. Ne touche à aucune instance.
"""

import hashlib
import os
import platform
import sys

import numpy as np

# ── Enveloppe scellée ──────────────────────────────────────────────────────
# Chaque valeur ici est un élément que Kairos contrôle et publie — pas une
# supposition sur le matériel. Modifier cette déclaration modifie l'enveloppe
# vérifiée ; ça ne modifie jamais un résultat de mesure.
SEALED_ENVELOPE = {
    "os": "Linux",
    "arch": "x86_64",
    "python_minor_accepted": ["3.10", "3.11", "3.12"],  # plage mesurée à ce jour
    "numpy": "2.2.6",
    "pandas": "2.3.3",
    "xgboost": "3.2.0",
    "OPENBLAS_CORETYPE": "Haswell",
    "OMP_NUM_THREADS": "1",
    "MKL_NUM_THREADS": "1",
    "OPENBLAS_NUM_THREADS": "1",
    "PYTHONHASHSEED": "0",
}

REPEAT_COUNT = 3  # nombre de passes pour le test de répétition intra-enveloppe


def h(x):
    """Hachage indépendant de la représentation — octets bruts du float64,
    jamais un repr() (numpy 1 et 2 affichent les scalaires différemment)."""
    a = np.ascontiguousarray(np.asarray(x, dtype=np.float64))
    return hashlib.sha256(a.tobytes()).hexdigest()


def check_envelope():
    """Compare l'environnement réel à SEALED_ENVELOPE. Retourne (sealed: bool,
    deviations: list[str])."""
    deviations = []

    if platform.system() != SEALED_ENVELOPE["os"]:
        deviations.append(f"OS: attendu {SEALED_ENVELOPE['os']}, obtenu {platform.system()}")

    if platform.machine() != SEALED_ENVELOPE["arch"]:
        deviations.append(f"arch: attendu {SEALED_ENVELOPE['arch']}, obtenu {platform.machine()}")

    py_minor = f"{sys.version_info.major}.{sys.version_info.minor}"
    if py_minor not in SEALED_ENVELOPE["python_minor_accepted"]:
        deviations.append(
            f"python: {py_minor} hors plage mesurée "
            f"{SEALED_ENVELOPE['python_minor_accepted']}"
        )

    if np.__version__ != SEALED_ENVELOPE["numpy"]:
        deviations.append(f"numpy: attendu {SEALED_ENVELOPE['numpy']}, obtenu {np.__version__}")

    try:
        import pandas as pd
        if pd.__version__ != SEALED_ENVELOPE["pandas"]:
            deviations.append(f"pandas: attendu {SEALED_ENVELOPE['pandas']}, obtenu {pd.__version__}")
    except ImportError:
        deviations.append("pandas: absent")

    try:
        import xgboost as xgb
        if xgb.__version__ != SEALED_ENVELOPE["xgboost"]:
            deviations.append(f"xgboost: attendu {SEALED_ENVELOPE['xgboost']}, obtenu {xgb.__version__}")
    except ImportError:
        deviations.append("xgboost: absent")

    for var in ("OPENBLAS_CORETYPE", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                "OPENBLAS_NUM_THREADS", "PYTHONHASHSEED"):
        actual = os.environ.get(var)
        expected = SEALED_ENVELOPE[var]
        if actual != expected:
            deviations.append(f"{var}: attendu {expected!r}, obtenu {actual!r}")

    return (len(deviations) == 0, deviations)


def run_ladder():
    """Exécute les 12 mesures L0-L6, dans un état totalement indépendant de
    tout appel précédent (rng réinitialisé). Retourne un dict ordonné
    {clé_niveau: hash_hex}. Logique de test identique à toutes les versions
    précédentes — seule la structure (fonction réutilisable) a changé."""
    results = {}

    # L0 — Contrôle : hachage pur, aucun flottant.
    data = b"kairos-determinism-ladder-control-vector"
    results["L0"] = hashlib.sha256(data).hexdigest()

    rng = np.random.default_rng(42)

    # L1 / L1b — Somme flottante simple, ordre de réduction.
    arr = rng.standard_normal(10_000_000)
    results["L1"] = h(arr.sum())
    results["L1b"] = h([arr.mean(), arr.std()])

    # L2 — Sommation naïve vs vectorisée, accumulation séquentielle.
    sub = arr[:100_000]
    naive = 0.0
    for v in sub:
        naive += v
    results["L2"] = h([naive, sub.sum()])

    # L3 / L3b — BLAS : le test le plus sensible au threading.
    m = rng.standard_normal((1200, 1200))
    prod = m @ m.T
    results["L3"] = h(prod)
    results["L3b"] = h(np.trace(prod))

    # L4 / L4b — Casting mixte, NEP 50.
    i32 = np.arange(1000, dtype=np.int32)
    f32 = np.float32(2.5)
    mixed = i32 * f32
    results["L4"] = h(mixed)
    f16 = np.float16(1.1)
    results["L4b"] = h(np.array([f16 * 3], dtype=np.float64))

    # L5 / L5b — pandas groupby, cas pipeline réel.
    try:
        import pandas as pd
        df = pd.DataFrame({
            "k": rng.integers(0, 50, 500_000),
            "v": rng.standard_normal(500_000),
        })
        g = df.groupby("k", sort=True)["v"].agg(["mean", "sum", "std"])
        results["L5"] = h(g.values.ravel())
        g2 = df.groupby("k", sort=False)["v"].mean()
        results["L5b"] = h(g2.sort_index().values)
    except ImportError:
        results["L5"] = None
        results["L5b"] = None

    # L6 — apprentissage automatique, mono- puis multi-thread.
    try:
        import xgboost as xgb
        X = rng.standard_normal((20_000, 20))
        y = (X[:, 0] + X[:, 1] * 0.5 + rng.standard_normal(20_000) * 0.1 > 0).astype(int)
        dtrain = xgb.DMatrix(X, label=y)
        for nthread in (1, 0):
            params = {
                "max_depth": 4, "eta": 0.3, "objective": "binary:logistic",
                "seed": 42, "nthread": nthread, "tree_method": "hist",
            }
            bst = xgb.train(params, dtrain, num_boost_round=20)
            pred = bst.predict(dtrain)
            key = "L6_mono" if nthread == 1 else "L6_multi"
            results[key] = h(pred)
    except ImportError:
        results["L6_mono"] = None
        results["L6_multi"] = None

    return results


LEVEL_LABELS = {
    "L0": ("sha256 control (no float)", "doit passer partout"),
    "L1": ("np.sum(10M gaussians)", "ordre de reduction"),
    "L1b": ("np.mean / np.std", ""),
    "L2": ("naive loop vs np.sum", "accumulation seq."),
    "L3": ("matmul 1200x1200 (BLAS)", "<<< THREAD-SENSIBLE"),
    "L3b": ("matmul trace", ""),
    "L4": ("int32 * float32 (NEP 50)", ""),
    "L4b": ("float16 promotion", ""),
    "L5": ("pandas groupby agg (sorted)", "cas pipeline"),
    "L5b": ("groupby sort=False", "ordre non garanti"),
    "L6_mono": ("xgboost nthread=1", "mono-thread"),
    "L6_multi": ("xgboost nthread=0", "<<< MULTI-THREAD"),
}


def print_table(results):
    print(f"{'LVL':<8} {'TEST':<34} {'HASH':<66} NOTE")
    print("-" * 78)
    for key, (name, note) in LEVEL_LABELS.items():
        val = results.get(key)
        display = val if val is not None else "ABSENT"
        print(f"{key:<8} {name:<34} {display:<66} {note}")


def main():
    print("=" * 78)
    print("KAIROS — DETERMINISM LADDER — v1.0")
    print("=" * 78)
    print(f"host           : {platform.node()}")
    print(f"os             : {platform.system()}")
    print(f"arch           : {platform.machine()}")
    print(f"python         : {platform.python_version()}")
    print(f"numpy          : {np.__version__}")
    try:
        import pandas as pd
        print(f"pandas         : {pd.__version__}")
    except ImportError:
        print("pandas         : ABSENT")
    try:
        import xgboost as xgb
        print(f"xgboost        : {xgb.__version__}")
    except ImportError:
        print("xgboost        : ABSENT")
    for var in ("OPENBLAS_CORETYPE", "OMP_NUM_THREADS", "MKL_NUM_THREADS",
                "OPENBLAS_NUM_THREADS", "PYTHONHASHSEED"):
        print(f"{var:<22} : {os.environ.get(var, 'NON FIXE')}")
    print("=" * 78)

    sealed, deviations = check_envelope()

    if sealed:
        print("VERDICT ENVELOPPE : SEALED_RUNTIME_MATCH")
    else:
        print("VERDICT ENVELOPPE : OUTSIDE_SEALED_RUNTIME")
        print("Écarts détectés :")
        for d in deviations:
            print(f"  - {d}")
        print()
        print("Les mesures ci-dessous sont affichées à titre informatif.")
        print("Elles ne sont PAS comparées aux empreintes de référence et ne")
        print("produisent aucun verdict PASS/FAIL.")
    print("=" * 78)

    if not sealed:
        results = run_ladder()
        print_table(results)
        print("-" * 78)
        print("Hors enveloppe : aucun verdict de déterminisme émis.")
        return

    # Enveloppe scellée confirmée : répétition intra-enveloppe.
    all_runs = [run_ladder() for _ in range(REPEAT_COUNT)]

    print(f"Répétition intra-enveloppe : {REPEAT_COUNT} passes")
    print_table(all_runs[0])
    print("-" * 78)

    stable = True
    unstable_levels = []
    for key in LEVEL_LABELS:
        values = {run[key] for run in all_runs}
        if len(values) > 1:
            stable = False
            unstable_levels.append(key)

    if stable:
        print(f"Répétition : les {REPEAT_COUNT} passes produisent des empreintes")
        print("identiques à chaque niveau.")
        print("VERDICT DÉTERMINISME : DETERMINISM_PASS")
    else:
        print(f"Répétition : instabilité détectée sur {len(unstable_levels)} niveau(x) :")
        for lvl in unstable_levels:
            print(f"  - {lvl}")
        print("VERDICT DÉTERMINISME : DETERMINISM_FAIL")

    print("=" * 78)
    print("""
LECTURE DES RESULTATS
─────────────────────
Comparer les empreintes SEALED_RUNTIME_MATCH ci-dessus à EXPECTED_HASHES.md.
Une divergence, une fois l'enveloppe confirmée scellée, est le résultat —
pas une erreur de protocole.

PORTEE
──────
Ce script mesure. Il ne conclut pas. Le résultat obtenu sur votre
environnement prévaut sur toute empreinte publiée ailleurs.
""")


if __name__ == "__main__":
    main()
