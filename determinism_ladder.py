#!/usr/bin/env python3
"""
KAIROS — ÉCHELLE DE DÉTERMINISME NUMÉRIQUE
==========================================
Question : le déterminisme byte-identique survit-il au calcul flottant ?

Protocole : escalade en 6 niveaux, du hachage pur (doit passer) au ML multi-thread
(cassera probablement). Le niveau où ça casse EST le résultat.

Usage — sur A puis sur B, deux passes :

    # Passe 1 — non contraint (état actuel du système)
    python3 determinism_ladder.py > ladder_$(hostname)_unconstrained.txt

    # Passe 2 — contraint
    OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
    PYTHONHASHSEED=0 python3 determinism_ladder.py > ladder_$(hostname)_constrained.txt

Puis, sur le Mac :
    diff ladder_hote-A_constrained.txt ladder_hote-B_constrained.txt

Lecture seule. N'écrit rien. Ne touche à aucune instance.
"""

import hashlib
import os
import platform
import sys

import numpy as np

# ── Hachage indépendant de la représentation ──────────────────────────────────
# On ne hache JAMAIS un repr() : numpy 2 affiche np.float64(1.0) là où numpy 1
# affiche 1.0. On hache les octets bruts du float64. Représentation-neutre.

def h(x):
    a = np.ascontiguousarray(np.asarray(x, dtype=np.float64))
    return hashlib.sha256(a.tobytes()).hexdigest()[:16]


def line(level, name, value, note=""):
    print(f"{level:<4} {name:<34} {value:<18} {note}")


# ── Contexte ──────────────────────────────────────────────────────────────────
print("=" * 78)
print("KAIROS — DETERMINISM LADDER")
print("=" * 78)
print(f"host           : {platform.node()}")
print(f"python         : {platform.python_version()}")
print(f"numpy          : {np.__version__}")
try:
    import pandas as pd
    print(f"pandas         : {pd.__version__}")
except ImportError:
    pd = None
    print("pandas         : ABSENT")
print(f"OMP_NUM_THREADS      : {os.environ.get('OMP_NUM_THREADS', 'NON FIXE')}")
print(f"MKL_NUM_THREADS      : {os.environ.get('MKL_NUM_THREADS', 'NON FIXE')}")
print(f"OPENBLAS_NUM_THREADS : {os.environ.get('OPENBLAS_NUM_THREADS', 'NON FIXE')}")
print(f"PYTHONHASHSEED       : {os.environ.get('PYTHONHASHSEED', 'NON FIXE')}")
print("=" * 78)
print(f"{'LVL':<4} {'TEST':<34} {'HASH':<18} NOTE")
print("-" * 78)

# ── L0 — Contrôle : hachage pur, aucun flottant ───────────────────────────────
# Doit être identique partout. Si L0 diverge, le protocole est cassé, pas le système.
data = b"kairos-determinism-ladder-control-vector"
line("L0", "sha256 control (no float)",
     hashlib.sha256(data).hexdigest()[:16], "doit passer partout")

# ── L1 — Somme flottante simple ───────────────────────────────────────────────
# Teste l'ordre de réduction. numpy utilise une sommation par paires.
rng = np.random.default_rng(42)
arr = rng.standard_normal(10_000_000)
line("L1", "np.sum(10M gaussians)", h(arr.sum()), "ordre de reduction")
line("L1b", "np.mean / np.std", h([arr.mean(), arr.std()]), "")

# ── L2 — Sommation naive vs vectorisee ────────────────────────────────────────
# Sensible a l'ordre d'accumulation.
sub = arr[:100_000]
naive = 0.0
for v in sub:
    naive += v
line("L2", "naive loop vs np.sum", h([naive, sub.sum()]), "accumulation seq.")

# ── L3 — BLAS : LE test qui casse ─────────────────────────────────────────────
# Multiplication matricielle = multi-thread par defaut. L'ordre de reduction
# depend du nombre de threads. C'EST ICI QUE CA CASSE, si ca doit casser.
m = rng.standard_normal((1200, 1200))
prod = m @ m.T
line("L3", "matmul 1200x1200 (BLAS)", h(prod), "<<< THREAD-SENSIBLE")
line("L3b", "matmul trace", h(np.trace(prod)), "")

# ── L4 — Casting mixte : NEP 50 (numpy 1.x vs 2.x) ────────────────────────────
# Les regles de promotion de type ont change entre numpy 1 et 2.
# A = numpy 1.21.5, B = numpy 2.2.6. C'est le point de rupture attendu.
i32 = np.arange(1000, dtype=np.int32)
f32 = np.float32(2.5)
mixed = i32 * f32
line("L4", "int32 * float32 (NEP 50)", h(mixed), f"dtype={mixed.dtype}")

f16 = np.float16(1.1)
line("L4b", "float16 promotion", h(np.array([f16 * 3], dtype=np.float64)), "")

# ── L5 — pandas groupby : le cas reel du pipeline ─────────────────────────────
if pd is not None:
    df = pd.DataFrame({
        "k": rng.integers(0, 50, 500_000),
        "v": rng.standard_normal(500_000),
    })
    g = df.groupby("k", sort=True)["v"].agg(["mean", "sum", "std"])
    line("L5", "pandas groupby agg (sorted)", h(g.values.ravel()), "cas pipeline")

    g2 = df.groupby("k", sort=False)["v"].mean()
    line("L5b", "groupby sort=False", h(g2.sort_index().values), "ordre non garanti")
else:
    line("L5", "pandas groupby", "SKIPPED", "pandas absent")

# ── L6 — apprentissage automatique, mono- puis multi-thread ──────────────────
try:
    import xgboost as xgb
    X = rng.standard_normal((20_000, 20))
    y = (X[:, 0] + X[:, 1] * 0.5 + rng.standard_normal(20_000) * 0.1 > 0).astype(int)
    dtrain = xgb.DMatrix(X, label=y)

    for nthread in (1, 0):  # 1 = force mono-thread ; 0 = tous les coeurs
        params = {
            "max_depth": 4, "eta": 0.3, "objective": "binary:logistic",
            "seed": 42, "nthread": nthread, "tree_method": "hist",
        }
        bst = xgb.train(params, dtrain, num_boost_round=20)
        pred = bst.predict(dtrain)
        tag = "mono-thread" if nthread == 1 else "<<< MULTI-THREAD"
        line("L6", f"xgboost nthread={nthread}", h(pred), tag)
except ImportError:
    line("L6", "xgboost", "ABSENT", "installer xgboost pour ce niveau")

print("-" * 78)
print("""
LECTURE DES RESULTATS
─────────────────────
1. Comparer deux environnements, meme passe :
   diff ladder_env1_constrained.txt ladder_env2_constrained.txt
2. Comparer contraint vs non contraint :
   diff ladder_constrained.txt ladder_unconstrained.txt

Le niveau ou la divergence apparait EST le resultat.

  L0 diverge          -> erreur de protocole, pas le systeme
  L1-L2 divergent     -> inattendu. A investiguer.
  L3 diverge non-contraint mais passe contraint
                      -> BLAS multi-thread. OMP_NUM_THREADS=1 est un element
                         constitutif de l'enveloppe, pas une option.
  L4 diverge          -> NEP 50. Aucun casting mixte implicite ne doit subsister.
  L5 diverge          -> pandas. Trier explicitement.
  L6 nthread=0 diverge-> attendu hors enveloppe mono-thread.
     nthread=1 passe  -> le determinisme est atteignable au prix du mono-thread.
                         Cout : temps de calcul.

PORTEE
──────
Ce script mesure. Il ne conclut pas. Le resultat obtenu sur votre environnement
prevaut sur toute empreinte publiee ailleurs.
""")
