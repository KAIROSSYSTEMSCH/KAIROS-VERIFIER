# Expected hashes

Measured 2026-07-21 → 2026-07-24 with `determinism_ladder.py`
(sha256 `f23de8df0d216dc6d79d0402103dcb2bb5ed1132eee83f10bf698c2cbae6d75c`).

**Platform of the published values: Linux x86_64.** macOS is measured and
reported separately below; its values differ by design, not by defect.

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
| **E1** | Kaggle | Intel Xeon @ 2.20 GHz, then AMD EPYC 7B12 | 3.12.13 | 2.2.6 | 2.3.3 | 3.2.0 |
| **E2** | Scaleway (FR) | AMD EPYC 9555P 64-Core | 3.10.12 | 2.2.6 | 2.3.3 | 3.2.0 |
| **E3** | Infomaniak (CH) | AMD EPYC (Genoa) | 3.10.12 | 2.2.6 | 2.3.3 | 3.2.0 |
| **E4** | Google Colab | Intel Xeon @ 2.20 GHz (GenuineIntel) | 3.12.13 | 2.2.6 | 2.3.3 | 3.2.0 |
| **E5** | GitHub Codespaces | AMD EPYC 9V74 80-Core | 3.12.1 | 2.2.6 | 2.3.3 | 3.2.0 |

All five are `x86_64`, Linux, across five independent providers and three Python
versions. Kaggle allocated an Intel Xeon on 2026-07-21 and an AMD EPYC 7B12 on
2026-07-24; both produced the values below. Four distinct AMD EPYC parts and one
Intel Xeon have been measured in total.

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

`OPENBLAS_CORETYPE` has no effect on macOS: numpy links against Apple's
Accelerate framework, not OpenBLAS.

| Date | OS | CPU | numpy | Identical | Differing values |
|---|---|---|---|---|---|
| 2026-07-21 | macOS 13 | Intel Core i5-7360U | 1.26.4 | 11 of 12 | L3 `a0dff7a2a4c25ac3` |
| 2026-07-24 | macOS 13 | Intel Core i5-7360U | 2.2.6 | 9 of 12 | L3 `a0dff7a2a4c25ac3`, L6 ×2 `e113a7436dc21812` |
| 2026-07-24 | macOS 14 | Apple M1 (arm64) | 2.2.6 | 8 of 12 | L3 `19ea7a60195f404e`, L5 `16b00268e85dab2d`, L6 ×2 `5a74cec7f7796ad1` |

Three observations.

**L3 is set by the BLAS implementation, not by the numpy version.** The two Intel
runs use different numpy versions on the same host and return the same L3.

**L6 is deterministic on every platform, at a value of its own.** Single-thread
and multi-thread agree within each platform; the three platforms return three
different values, tracking the xgboost build rather than the run.

**On arm64, L5 also differs.** The divergence is therefore not confined to
libraries called through a native backend.

None of these values is a defect: each platform is internally stable and
reproducible. The published set is the Linux x86_64 one, because that is the
platform Kairos runs on. These values are published so that anyone running the
verifier on a Mac can compare against a reference rather than read a difference
as a failure.

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
- **macOS is measured but outside the declared envelope**, on both x86_64 Intel
  and Apple Silicon. Its values are published above for reference.
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
2026-07-23  Editorial pass on determinism_ladder.py: comments and printed text
            only, no computation changed. Verified by comparing all twelve
            hashes before and after on the same host. Published sha256 becomes
            f23de8df.
2026-07-24  A macOS environment previously labelled "Apple Silicon (arm64)" in an
            earlier revision of this file was in fact Intel x86_64. Both macOS
            architectures have now been measured and are reported separately.
2026-07-24  Second Intel macOS run at numpy 2.2.6 returns the same L3 as at
            1.26.4, isolating the BLAS implementation as the cause of the
            divergence. The numpy version is not the cause.
```
