# Expected hashes — VERIFIER v1.0

Measured 2026-08-16 with `determinism_ladder.py`
(sha256 `e2f6cd4b4e67e98d19adbd76e9e8c12eae0276cca3755b324e55f3b966525be4`).

This is a full re-verification campaign tied to the v1.0 script rewrite
(sealed-envelope self-check, intra-run repetition, machine-readable verdict,
full 64-character SHA-256 output). It supersedes all previously published
16-character values, which were produced by an earlier script version and
are no longer the reference.

**Platform of the published values: Linux x86_64.** macOS is measured and
reported separately below; its values differ by design, not by defect.

## Sealed envelope

The script verifies this envelope itself at runtime and reports
`SEALED_RUNTIME_MATCH` or `OUTSIDE_SEALED_RUNTIME` — no manual comparison
required.

```bash
numpy==2.2.6   pandas==2.3.3   xgboost==3.2.0
export OPENBLAS_CORETYPE=Haswell
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONHASHSEED=0
```

Python: `3.10.x` and `3.12.x` have been measured; the script also accepts
`3.11.x` on the same basis (minor-version match) but that specific version
has not yet been run. Hashes are the full SHA-256 of the raw float64 bytes,
as printed by the script — no truncation.

## Environments (inside the envelope)

| Provider | Python | Verdict |
|---|---|---|
| Google Colab | 3.12.13 | `SEALED_RUNTIME_MATCH` · `DETERMINISM_PASS` |
| Kaggle | 3.12.13 | `SEALED_RUNTIME_MATCH` · `DETERMINISM_PASS` |
| Infomaniak (CH) | 3.10.12 | `SEALED_RUNTIME_MATCH` · `DETERMINISM_PASS` |
| Scaleway (FR) | 3.10.12 | `SEALED_RUNTIME_MATCH` · `DETERMINISM_PASS` |

Four independent providers, two Python minor versions. Each environment ran
the script's own intra-envelope repetition (3 passes) with no instability
detected on any level, in addition to matching across environments.

## Results — inside the envelope (identical on all four)

| Level | Test | Hash |
|---|---|---|
| L0 | SHA-256 control (no float) | `1d9e01d16d6389002d78dd1a6456743273cdf2277fd781c872bc428a567ef85b` |
| L1 | np.sum(10M gaussians) | `84af2aaa28305585d54e02e8de41148d894fe66faadab54f38b3727c82e78580` |
| L1b | np.mean / np.std | `9984517da6ef41ff74b85274d57301e063b46dfbce4892ea3841b19800a6785f` |
| L2 | naive loop vs np.sum | `86ca842440c89f745a9b4aa1b0c7972fa6879c055f334b867d7cfb1ccd233f4a` |
| L3 | matmul 1200×1200 (BLAS) | `60da9d0bfeb7bb992dfa73ced6bb6634840be86783f20979e44bfcfbf8906fe9` |
| L3b | matmul trace | `db791086e49a76e2087927d7a010666707b3945fafb71b2446164d672a8c6872` |
| L4 | int32 × float32 (NEP 50) | `0bf4f040e2ee2721aca6e3c74d20f74198cef85ca4bba4348a7152f00e44e9b3` |
| L4b | float16 promotion | `9d40cfbddb0c14caadec21c852b5d6578767fb14da59ad563a70bdc8b23dcb18` |
| L5 | pandas groupby agg (sorted) | `687b5cae54c0f69f4bf6c54bb60d737a27b1a2c9965e577c7846e462fe976703` |
| L5b | groupby sort=False | `d36851807abf6013acd4b7be2c66f25d3ec4e82d84b6e451bf84fc1beafd38d3` |
| L6 mono-thread | xgboost `nthread=1` | `e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6` |
| L6 multi-thread | xgboost `nthread=0` | `e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6` |

**12 of 12 measurements are byte-identical across all four environments**, and
**L6 mono-thread == L6 multi-thread** on every one.

These values are also byte-for-byte consistent with the previous campaign's
16-character values at every corresponding prefix — the underlying
computation has not changed, only the script's output format and its
self-verification layer.

## L3 outside the envelope

Values confirmed again in this campaign, consistent with prior measurement:

| Case | L3 |
|---|---|
| `OPENBLAS_CORETYPE=Haswell` (sealed) | `60da9d0bfeb7bb99...` |
| Unset, host has AVX-512 (SkylakeX kernel loaded) | `c210e706aa1d8a4f...` |
| macOS, Intel x86_64 (Accelerate, not OpenBLAS) | `a0dff7a2a4c25ac3...` |

`OPENBLAS_CORETYPE` has no effect on macOS: numpy links against Apple's
Accelerate framework, not OpenBLAS.

## macOS — outside the declared envelope

| Date | OS | numpy | xgboost | Verdict | Differing levels |
|---|---|---|---|---|---|
| 2026-08-16 | macOS, Intel x86_64 | 2.5.2 | 3.4.1 | `OUTSIDE_SEALED_RUNTIME` | L1, L3, L6 (mono==multi within platform) |

The script correctly identifies every deviation (OS, Python, and all three
pinned library versions differ from the sealed envelope on this host) and
emits no PASS/FAIL verdict — measurements are shown for reference only. L3
matches the value already on record for macOS Intel; L0, L2, L3b, L4, L4b,
L5, L5b match the Linux sealed values exactly, consistent with those levels
not depending on BLAS or ML-library internals.

## Reproduce it yourself

```bash
sha256sum determinism_ladder.py
# expected: e2f6cd4b4e67e98d19adbd76e9e8c12eae0276cca3755b324e55f3b966525be4

python3 -m venv env
./env/bin/pip install -r requirements.txt
OPENBLAS_CORETYPE=Haswell \
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
PYTHONHASHSEED=0 ./env/bin/python3 determinism_ladder.py
```

The script's own output tells you whether you matched the sealed envelope
and whether your measurements were internally repeatable. If it reports
`SEALED_RUNTIME_MATCH` and `DETERMINISM_PASS`, compare your twelve hashes to
the table above. Any divergence at that point is the result — not a protocol
error. [Open an issue](../../issues) with your full output.

## Scope — what this does and does not establish

- **Inside the declared envelope, four independent environments — two cloud
  notebook providers and two Kairos-operated instances — produce
  byte-identical results across two Python minor versions.**
- **L6 covers one model:** 20 000 × 20, `tree_method=hist`, 20 rounds, seed
  42. It does not generalise to large or deep models without a new
  measurement.
- **macOS is measured but outside the declared envelope.** Its values are
  published above for reference, not as a target the envelope is expected to
  reach.
- **This kit tests the numerical substrate, not the Kairos product.** The
  full Kairos pipeline is currently undergoing third-party replay
  validation. That campaign is separate from this kit, ongoing, and not yet
  complete. Anyone claiming it is finished — including us — would be wrong.

## Correction log

```
2026-08-16  V1.0 — full script rewrite. Sealed-envelope self-verification,
            intra-run repetition (3 passes per environment), machine-readable
            verdict (SEALED_RUNTIME_MATCH/OUTSIDE_SEALED_RUNTIME, then
            DETERMINISM_PASS/DETERMINISM_FAIL). Hashes now published in full
            (64 hex characters), not truncated to 16. Full re-verification
            campaign: Colab, Kaggle, Infomaniak, Scaleway — all
            SEALED_RUNTIME_MATCH, all DETERMINISM_PASS, all 12/12 identical.
            macOS re-measured, correctly reports OUTSIDE_SEALED_RUNTIME.
            Superseded values were produced by a prior script version
            (sha256 f23de8df...) truncated to 16 characters; this file no
            longer references them as current.
```
