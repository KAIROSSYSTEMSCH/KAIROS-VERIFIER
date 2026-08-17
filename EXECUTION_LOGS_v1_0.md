# EXECUTION_LOGS — Campagne v1.0, 2026-08-16

Sorties brutes, verbatim, des cinq exécutions ayant produit les empreintes
publiées dans `EXPECTED_HASHES.md` et le dossier de preuve v1.1. Script
vérifié SHA-256 `e2f6cd4b4e67e98d19adbd76e9e8c12eae0276cca3755b324e55f3b966525be4`
sur chaque environnement avant exécution.

---

## 1. Google Colab

```
==============================================================================
KAIROS — DETERMINISM LADDER — v1.0
==============================================================================
host           : b8523d35f708
os             : Linux
arch           : x86_64
python         : 3.12.13
numpy          : 2.2.6
pandas         : 2.3.3
xgboost        : 3.2.0
OPENBLAS_CORETYPE      : Haswell
OMP_NUM_THREADS        : 1
MKL_NUM_THREADS        : 1
OPENBLAS_NUM_THREADS   : 1
PYTHONHASHSEED         : 0
==============================================================================
VERDICT ENVELOPPE : SEALED_RUNTIME_MATCH
==============================================================================
Répétition intra-enveloppe : 3 passes
LVL      TEST                               HASH                                                               NOTE
------------------------------------------------------------------------------
L0       sha256 control (no float)          1d9e01d16d6389002d78dd1a6456743273cdf2277fd781c872bc428a567ef85b   doit passer partout
L1       np.sum(10M gaussians)              84af2aaa28305585d54e02e8de41148d894fe66faadab54f38b3727c82e78580   ordre de reduction
L1b      np.mean / np.std                   9984517da6ef41ff74b85274d57301e063b46dfbce4892ea3841b19800a6785f
L2       naive loop vs np.sum               86ca842440c89f745a9b4aa1b0c7972fa6879c055f334b867d7cfb1ccd233f4a   accumulation seq.
L3       matmul 1200x1200 (BLAS)            60da9d0bfeb7bb992dfa73ced6bb6634840be86783f20979e44bfcfbf8906fe9   <<< THREAD-SENSIBLE
L3b      matmul trace                       db791086e49a76e2087927d7a010666707b3945fafb71b2446164d672a8c6872
L4       int32 * float32 (NEP 50)           0bf4f040e2ee2721aca6e3c74d20f74198cef85ca4bba4348a7152f00e44e9b3
L4b      float16 promotion                  9d40cfbddb0c14caadec21c852b5d6578767fb14da59ad563a70bdc8b23dcb18
L5       pandas groupby agg (sorted)        687b5cae54c0f69f4bf6c54bb60d737a27b1a2c9965e577c7846e462fe976703   cas pipeline
L5b      groupby sort=False                 d36851807abf6013acd4b7be2c66f25d3ec4e82d84b6e451bf84fc1beafd38d3   ordre non garanti
L6_mono  xgboost nthread=1                  e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6   mono-thread
L6_multi xgboost nthread=0                  e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6   <<< MULTI-THREAD
------------------------------------------------------------------------------
Répétition : les 3 passes produisent des empreintes
identiques à chaque niveau.
VERDICT DÉTERMINISME : DETERMINISM_PASS
```

## 2. Kaggle

*Note opérationnelle : un premier essai sur cet environnement a produit
`numpy 2.0.2` (préinstallation Kaggle non remplacée avant redémarrage du
kernel) → `OUTSIDE_SEALED_RUNTIME`, écart `numpy` seul. Après
`--force-reinstall` et redémarrage du kernel, second essai conforme. Seul
le second essai, ci-dessous, constitue une mesure de référence.*

```
==============================================================================
KAIROS — DETERMINISM LADDER — v1.0
==============================================================================
host           : 0b957a430d11
os             : Linux
arch           : x86_64
python         : 3.12.13
numpy          : 2.2.6
pandas         : 2.3.3
xgboost        : 3.2.0
OPENBLAS_CORETYPE      : Haswell
OMP_NUM_THREADS        : 1
MKL_NUM_THREADS        : 1
OPENBLAS_NUM_THREADS   : 1
PYTHONHASHSEED         : 0
==============================================================================
VERDICT ENVELOPPE : SEALED_RUNTIME_MATCH
==============================================================================
Répétition intra-enveloppe : 3 passes
LVL      TEST                               HASH                                                               NOTE
------------------------------------------------------------------------------
L0       sha256 control (no float)          1d9e01d16d6389002d78dd1a6456743273cdf2277fd781c872bc428a567ef85b   doit passer partout
L1       np.sum(10M gaussians)              84af2aaa28305585d54e02e8de41148d894fe66faadab54f38b3727c82e78580   ordre de reduction
L1b      np.mean / np.std                   9984517da6ef41ff74b85274d57301e063b46dfbce4892ea3841b19800a6785f
L2       naive loop vs np.sum               86ca842440c89f745a9b4aa1b0c7972fa6879c055f334b867d7cfb1ccd233f4a   accumulation seq.
L3       matmul 1200x1200 (BLAS)            60da9d0bfeb7bb992dfa73ced6bb6634840be86783f20979e44bfcfbf8906fe9   <<< THREAD-SENSIBLE
L3b      matmul trace                       db791086e49a76e2087927d7a010666707b3945fafb71b2446164d672a8c6872
L4       int32 * float32 (NEP 50)           0bf4f040e2ee2721aca6e3c74d20f74198cef85ca4bba4348a7152f00e44e9b3
L4b      float16 promotion                  9d40cfbddb0c14caadec21c852b5d6578767fb14da59ad563a70bdc8b23dcb18
L5       pandas groupby agg (sorted)        687b5cae54c0f69f4bf6c54bb60d737a27b1a2c9965e577c7846e462fe976703   cas pipeline
L5b      groupby sort=False                 d36851807abf6013acd4b7be2c66f25d3ec4e82d84b6e451bf84fc1beafd38d3   ordre non garanti
L6_mono  xgboost nthread=1                  e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6   mono-thread
L6_multi xgboost nthread=0                  e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6   <<< MULTI-THREAD
------------------------------------------------------------------------------
Répétition : les 3 passes produisent des empreintes
identiques à chaque niveau.
VERDICT DÉTERMINISME : DETERMINISM_PASS
```

## 3. Infomaniak (CH)

```
==============================================================================
KAIROS — DETERMINISM LADDER — v1.0
==============================================================================
host           : kairos-systems
os             : Linux
arch           : x86_64
python         : 3.10.12
numpy          : 2.2.6
pandas         : 2.3.3
xgboost        : 3.2.0
OPENBLAS_CORETYPE      : Haswell
OMP_NUM_THREADS        : 1
MKL_NUM_THREADS        : 1
OPENBLAS_NUM_THREADS   : 1
PYTHONHASHSEED         : 0
==============================================================================
VERDICT ENVELOPPE : SEALED_RUNTIME_MATCH
==============================================================================
Répétition intra-enveloppe : 3 passes
LVL      TEST                               HASH                                                               NOTE
------------------------------------------------------------------------------
L0       sha256 control (no float)          1d9e01d16d6389002d78dd1a6456743273cdf2277fd781c872bc428a567ef85b   doit passer partout
L1       np.sum(10M gaussians)              84af2aaa28305585d54e02e8de41148d894fe66faadab54f38b3727c82e78580   ordre de reduction
L1b      np.mean / np.std                   9984517da6ef41ff74b85274d57301e063b46dfbce4892ea3841b19800a6785f
L2       naive loop vs np.sum               86ca842440c89f745a9b4aa1b0c7972fa6879c055f334b867d7cfb1ccd233f4a   accumulation seq.
L3       matmul 1200x1200 (BLAS)            60da9d0bfeb7bb992dfa73ced6bb6634840be86783f20979e44bfcfbf8906fe9   <<< THREAD-SENSIBLE
L3b      matmul trace                       db791086e49a76e2087927d7a010666707b3945fafb71b2446164d672a8c6872
L4       int32 * float32 (NEP 50)           0bf4f040e2ee2721aca6e3c74d20f74198cef85ca4bba4348a7152f00e44e9b3
L4b      float16 promotion                  9d40cfbddb0c14caadec21c852b5d6578767fb14da59ad563a70bdc8b23dcb18
L5       pandas groupby agg (sorted)        687b5cae54c0f69f4bf6c54bb60d737a27b1a2c9965e577c7846e462fe976703   cas pipeline
L5b      groupby sort=False                 d36851807abf6013acd4b7be2c66f25d3ec4e82d84b6e451bf84fc1beafd38d3   ordre non garanti
L6_mono  xgboost nthread=1                  e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6   mono-thread
L6_multi xgboost nthread=0                  e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6   <<< MULTI-THREAD
------------------------------------------------------------------------------
Répétition : les 3 passes produisent des empreintes
identiques à chaque niveau.
VERDICT DÉTERMINISME : DETERMINISM_PASS
```

## 4. Scaleway (FR)

*Note opérationnelle : disque système `/` initialement plein (100%),
exécution déplacée vers `/srv/kairos/verifier_test` (second volume monté,
142 Go disponibles). Un premier transfert du script s'est révélé tronqué
(`SyntaxError` détectée avant toute exécution — jamais un résultat invalide
produit) ; le fichier a été retransféré intégralement avant l'exécution
ci-dessous.*

```
==============================================================================
KAIROS — DETERMINISM LADDER — v1.0
==============================================================================
host           : kairos-shadow-instanceb
os             : Linux
arch           : x86_64
python         : 3.10.12
numpy          : 2.2.6
pandas         : 2.3.3
xgboost        : 3.2.0
OPENBLAS_CORETYPE      : Haswell
OMP_NUM_THREADS        : 1
MKL_NUM_THREADS        : 1
OPENBLAS_NUM_THREADS   : 1
PYTHONHASHSEED         : 0
==============================================================================
VERDICT ENVELOPPE : SEALED_RUNTIME_MATCH
==============================================================================
Répétition intra-enveloppe : 3 passes
LVL      TEST                               HASH                                                               NOTE
------------------------------------------------------------------------------
L0       sha256 control (no float)          1d9e01d16d6389002d78dd1a6456743273cdf2277fd781c872bc428a567ef85b   doit passer partout
L1       np.sum(10M gaussians)              84af2aaa28305585d54e02e8de41148d894fe66faadab54f38b3727c82e78580   ordre de reduction
L1b      np.mean / np.std                   9984517da6ef41ff74b85274d57301e063b46dfbce4892ea3841b19800a6785f
L2       naive loop vs np.sum               86ca842440c89f745a9b4aa1b0c7972fa6879c055f334b867d7cfb1ccd233f4a   accumulation seq.
L3       matmul 1200x1200 (BLAS)            60da9d0bfeb7bb992dfa73ced6bb6634840be86783f20979e44bfcfbf8906fe9   <<< THREAD-SENSIBLE
L3b      matmul trace                       db791086e49a76e2087927d7a010666707b3945fafb71b2446164d672a8c6872
L4       int32 * float32 (NEP 50)           0bf4f040e2ee2721aca6e3c74d20f74198cef85ca4bba4348a7152f00e44e9b3
L4b      float16 promotion                  9d40cfbddb0c14caadec21c852b5d6578767fb14da59ad563a70bdc8b23dcb18
L5       pandas groupby agg (sorted)        687b5cae54c0f69f4bf6c54bb60d737a27b1a2c9965e577c7846e462fe976703   cas pipeline
L5b      groupby sort=False                 d36851807abf6013acd4b7be2c66f25d3ec4e82d84b6e451bf84fc1beafd38d3   ordre non garanti
L6_mono  xgboost nthread=1                  e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6   mono-thread
L6_multi xgboost nthread=0                  e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6   <<< MULTI-THREAD
------------------------------------------------------------------------------
Répétition : les 3 passes produisent des empreintes
identiques à chaque niveau.
VERDICT DÉTERMINISME : DETERMINISM_PASS
```

## 5. GitHub Codespaces

```
==============================================================================
KAIROS — DETERMINISM LADDER — v1.0
==============================================================================
host           : codespaces-8e7bba
os             : Linux
arch           : x86_64
python         : 3.12.13
numpy          : 2.2.6
pandas         : 2.3.3
xgboost        : 3.2.0
OPENBLAS_CORETYPE      : Haswell
OMP_NUM_THREADS        : 1
MKL_NUM_THREADS        : 1
OPENBLAS_NUM_THREADS   : 1
PYTHONHASHSEED         : 0
==============================================================================
VERDICT ENVELOPPE : SEALED_RUNTIME_MATCH
==============================================================================
Répétition intra-enveloppe : 3 passes
LVL      TEST                               HASH                                                               NOTE
------------------------------------------------------------------------------
L0       sha256 control (no float)          1d9e01d16d6389002d78dd1a6456743273cdf2277fd781c872bc428a567ef85b   doit passer partout
L1       np.sum(10M gaussians)              84af2aaa28305585d54e02e8de41148d894fe66faadab54f38b3727c82e78580   ordre de reduction
L1b      np.mean / np.std                   9984517da6ef41ff74b85274d57301e063b46dfbce4892ea3841b19800a6785f
L2       naive loop vs np.sum               86ca842440c89f745a9b4aa1b0c7972fa6879c055f334b867d7cfb1ccd233f4a   accumulation seq.
L3       matmul 1200x1200 (BLAS)            60da9d0bfeb7bb992dfa73ced6bb6634840be86783f20979e44bfcfbf8906fe9   <<< THREAD-SENSIBLE
L3b      matmul trace                       db791086e49a76e2087927d7a010666707b3945fafb71b2446164d672a8c6872
L4       int32 * float32 (NEP 50)           0bf4f040e2ee2721aca6e3c74d20f74198cef85ca4bba4348a7152f00e44e9b3
L4b      float16 promotion                  9d40cfbddb0c14caadec21c852b5d6578767fb14da59ad563a70bdc8b23dcb18
L5       pandas groupby agg (sorted)        687b5cae54c0f69f4bf6c54bb60d737a27b1a2c9965e577c7846e462fe976703   cas pipeline
L5b      groupby sort=False                 d36851807abf6013acd4b7be2c66f25d3ec4e82d84b6e451bf84fc1beafd38d3   ordre non garanti
L6_mono  xgboost nthread=1                  e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6   mono-thread
L6_multi xgboost nthread=0                  e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6   <<< MULTI-THREAD
------------------------------------------------------------------------------
Répétition : les 3 passes produisent des empreintes
identiques à chaque niveau.
VERDICT DÉTERMINISME : DETERMINISM_PASS
```

---

## Résumé

| Environnement | Python | Verdict enveloppe | Verdict déterminisme |
|---|---|---|---|
| Google Colab | 3.12.13 | SEALED_RUNTIME_MATCH | DETERMINISM_PASS |
| Kaggle | 3.12.13 | SEALED_RUNTIME_MATCH | DETERMINISM_PASS |
| Infomaniak (CH) | 3.10.12 | SEALED_RUNTIME_MATCH | DETERMINISM_PASS |
| Scaleway (FR) | 3.10.12 | SEALED_RUNTIME_MATCH | DETERMINISM_PASS |
| GitHub Codespaces | 3.12.13 | SEALED_RUNTIME_MATCH | DETERMINISM_PASS |

5/5 environnements, 5/5 `SEALED_RUNTIME_MATCH`, 5/5 `DETERMINISM_PASS`, 12/12
empreintes strictement identiques, caractère pour caractère, sur les cinq
environnements.
