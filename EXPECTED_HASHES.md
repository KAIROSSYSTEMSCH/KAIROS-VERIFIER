# Expected hashes

Measured 2026-07-21 with `determinism_ladder.py`
(sha256 `c8b518ff484d9940f7c2da05a2b5ac58fd8a1ebf1b3123b2136d5fb6a691ec66`).

**Constrained envelope** — pinned versions plus environment. All of it matters:

```bash
numpy==2.2.6   pandas==2.3.3   xgboost==3.2.0
export OPENBLAS_CORETYPE=Haswell
export OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
export PYTHONHASHSEED=0
```

Hashes are the first 16 hex characters of the SHA-256 of the raw float64 bytes,
as printed by the script. Each CPU line below is the raw `lscpu` output of the
host that produced the hashes — not a label assigned after the fact.

## Environments (inside the envelope)

| # | Provider | CPU | Python | numpy | pandas | xgboost |
|---|---|---|---|---|---|---|
| **E1** | Kaggle | Intel Xeon @ 2.20 GHz (GenuineIntel) | 3.12.13 | 2.2.6 | 2.3.3 | 3.2.0 |
| **E2** | Scaleway (FR) | AMD EPYC 9555P 64-Core | 3.10.12 | 2.2.6 | 2.3.3 | 3.2.0 |
| **E3** | Infomaniak (CH) | AMD EPYC (Genoa) | 3.10.12 | 2.2.6 | 2.3.3 | 3.2.0 |
| **E4** | Google Colab | Intel Xeon @ 2.20 GHz (GenuineIntel) | 3.12.13 | 2.2.6 | 2.3.3 | 3.2.0 |
| **E5** | GitHub Codespaces | AMD EPYC 9V74 80-Core | 3.12.1 | 2.2.6 | 2.3.3 | 3.2.0 |

All five are `x86_64`, Linux. Two Intel hosts and three distinct AMD EPYC parts,
across five independent providers and three Python versions.

## Results — inside the envelope (identical on E1–E5)

| Level | Test | Hash |
|---|---|---|
| L0 | SHA-256 control (no float) | `1d9e01d16d638900` |
| L1 | np.sum(10M gaussians) | `84af2aaa28305585` |
| L1b | np.mean / np.std | `9984517da6ef41ff` |
| L2 | naive loop vs np.sum | `86ca842440c89f74` |
| L3 | matmul 1200×1200 (BLAS) | `60da9d0bfeb7bb99` |
| L3b | matmul trace | `db791086e49a76e2` |
| L4 | int32 × float32 (NEP 50) | `0bf4f040e2ee2721` |
| L4b | float16 promotion | `9d40cfbddb0c14ca` |
| L5 | pandas groupby agg (sorted) | `687b5cae54c0f69f` |
| L5b | groupby sort=False | `d36851807abf6013` |
| L6 `nthread=1` | xgboost predictions | `e05c0b80de5ce5e4` |
| L6 `nthread=0` | xgboost predictions | `e05c0b80de5ce5e4` |

**12 of 12 measurements are byte-identical across all five environments** — two
Intel and three AMD CPUs, five providers, three Python versions — and
**L6 `nthread=1` == L6 `nthread=0`** on every one.

## L3 is determined by the BLAS kernel, not the CPU directly

`OPENBLAS_CORETYPE` was the only variable changed on each host. The loaded kernel
was confirmed with `OPENBLAS_VERBOSE=2`. L3 follows the kernel, and the same
kernel gives the same L3 on Intel and on AMD:

| OPENBLAS_CORETYPE | Kernel loaded | L3 |
|---|---|---|
| Haswell | Haswell | `60da9d0bfeb7bb99` |
| SKYLAKEX | SkylakeX | `c210e706aa1d8a4f` |
| NEHALEM | Nehalem | `f89587dc64cc1ef1` |
| PRESCOTT | **Katmai** | `2b15dec0caa62a22` |

Note: the `PRESCOTT` directive actually loads the **Katmai** kernel (per
`OPENBLAS_VERBOSE=2`); the hash shown is that kernel's.

Without a directive, the kernel depends on whether the host exposes AVX-512:

| Host | AVX-512 | OPENBLAS_CORETYPE | L3 |
|---|---|---|---|
| E1 Intel Xeon 2.20 | absent | unset | `60da9d0bfeb7bb99` |
| E4 Intel Xeon 2.20 | absent | unset | `60da9d0bfeb7bb99` |
| E5 AMD EPYC 9V74 | absent | unset | `60da9d0bfeb7bb99` |
| E2 AMD EPYC 9555P | present | unset | `c210e706aa1d8a4f` |
| E2 AMD EPYC 9555P | present | Haswell | `60da9d0bfeb7bb99` |
| E3 AMD EPYC Genoa | present | unset | `c210e706aa1d8a4f` |
| E3 AMD EPYC Genoa | present | Haswell | `60da9d0bfeb7bb99` |

Hosts without AVX-512 fall back to Haswell on their own and already produce
`60da9d0b`. Hosts with AVX-512 select SkylakeX by default; `OPENBLAS_CORETYPE=Haswell`
brings them back to the common value. **This is why the envelope pins it — it is
not optional.**

## L3 outside the envelope

| Environment | Architecture | BLAS | numpy | L3 |
|---|---|---|---|---|
| macOS 13 | x86_64 (Intel Core i5) | Accelerate | 1.26.4 | `a0dff7a2a4c25ac3` |

Accelerate is not OpenBLAS and takes no `CORETYPE`, so L3 differs; the other ten
levels match E1–E5. This line is declared outside the envelope on purpose.

## Reproduce it yourself

Create a free Kaggle or Colab notebook (or any x86_64 Linux host), add
`determinism_ladder.py`, verify its sha256, `pip install -r requirements.txt`,
and run with the envelope above. You should get the E1–E5 column. Check the
loaded kernel with `OPENBLAS_VERBOSE=2` and your CPU with `lscpu`. If your hashes
differ, tell us: [open an issue](../../issues). A verifier that cannot contradict
us verifies nothing.

## Scope — what this does and does not establish

- **Inside the declared envelope, five independent environments — two Intel, three
  AMD — produce byte-identical results.** Two CPU vendors, five providers, three
  Python versions.
- **L6 covers one model:** 20 000 × 20, `tree_method=hist`, 20 rounds, seed 42.
  It does not generalise to large or deep models without a new measurement.
- **arm64 / Apple Silicon is not covered.** The macOS line above is x86_64 Intel.
- **This kit tests the numerical substrate, not the Kairos product.** The full
  Kairos pipeline has never been replayed on a third-party environment. Anyone
  claiming otherwise — including us — would be wrong.

## Correction log

```
2026-07-21  All measurements re-run from the published script on five live
            environments (Kaggle, Scaleway, Infomaniak, Colab, Codespaces) plus
            one macOS host outside the envelope. Every CPU label in this file is
            the lscpu output of the host that produced the hashes.
2026-07-21  Corrected: the OPENBLAS_CORETYPE=PRESCOTT directive loads the Katmai
            kernel (confirmed by OPENBLAS_VERBOSE=2), not Prescott. Hash unchanged.
```
