# Kairos Replay Kit — Numerical Determinism Verifier

**Don't trust us. Run it.**

Kairos Systems claims that its execution layer is byte-reproducible. This repository
contains the verifier we used to measure that claim, the exact hashes we obtained,
and the protocol to reproduce them on your own machine. We do not participate.

If your hashes differ from ours, [open an issue](../../issues). A verifier that
cannot contradict us verifies nothing.

---

## 1. What you are about to do

Run a ~200-line script that uses nothing but `numpy`, `pandas` and `xgboost`.
Compare your output to ours. It takes about 3 minutes.

## 2. Protocol

```bash
# 1 — authenticate the script (it must be the one we measured)
sha256sum determinism_ladder.py
# expected: f23de8df0d216dc6d79d0402103dcb2bb5ed1132eee83f10bf698c2cbae6d75c

# 2 — isolated environment, pinned versions
python3 -m venv env
./env/bin/pip install -r requirements.txt

# 3 — pass 1: unconstrained (your system as-is)
./env/bin/python3 determinism_ladder.py > ladder_unconstrained.txt

# 4 — pass 2: the declared envelope
OPENBLAS_CORETYPE=Haswell \
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
PYTHONHASHSEED=0 ./env/bin/python3 determinism_ladder.py > ladder_constrained.txt

# 5 — compare
diff ladder_unconstrained.txt ladder_constrained.txt
cat ladder_constrained.txt
```

Then compare your `L0`–`L6` lines to [`EXPECTED_HASHES.md`](EXPECTED_HASHES.md).

The script is read-only. It writes nothing, opens no network connection, and
touches no Kairos system.

## 3. What the levels measure

| Level | Test | What it probes |
|---|---|---|
| L0 | SHA-256 of a fixed byte string | control — must match everywhere. If L0 differs, the protocol is broken, not the system. |
| L1 / L1b | sum / mean / std of 10M gaussians | float reduction order |
| L2 | naive loop vs vectorised sum | sequential accumulation |
| L3 / L3b | 1200×1200 matrix product | BLAS implementation |
| L4 / L4b | int32 × float32, float16 promotion | NEP 50 type promotion rules |
| L5 / L5b | pandas groupby, sorted and unsorted | the real pipeline case |
| L6 | XGBoost predictions, `nthread=1` and `nthread=0` | ML determinism, single- vs multi-thread |

## 4. What this proves — and what it does not

**It proves** that Kairos states a reproducibility envelope that is explicit,
complete, and testable — and that we correct the envelope when measurement
contradicts it rather than softening the claim. Inside the declared envelope,
**12 of 12 measurements are byte-identical across five independent environments**
— two Intel Xeon and three distinct AMD EPYC parts, five providers (Kaggle,
Scaleway, Infomaniak, Colab, Codespaces) and three Python versions.

The envelope is: pinned library versions, `OPENBLAS_CORETYPE`, thread caps,
`PYTHONHASHSEED`. Every element is a variable we control and publish — none of it
is hardware we have to hope for. See `EXPECTED_HASHES.md`, including the kernel
table: L3 follows the BLAS kernel actually loaded (`OPENBLAS_VERBOSE=2`), and
`OPENBLAS_CORETYPE=Haswell` fixes it to the same value on Intel and AMD.

**It does not prove** that the Kairos pipeline is correct, nor that our sealed
Shadow Run of 2026-06-06 is valid. This kit tests the numerical substrate, not
the product.

**What is not done yet, stated here before anyone asks us:** the full Kairos
pipeline (46 datasets, 9.67M rows) has never been replayed on a third-party
environment. That is a separate campaign and it is not complete. Anyone claiming
otherwise — including us — would be wrong.

## 5. If your hashes differ

- **Different library versions than ours?** Expected. The envelope *is* the
  versions. Pin them (`requirements.txt`) and try again.
- **Did you set `OPENBLAS_CORETYPE=Haswell`?** Without it, OpenBLAS picks a
  kernel from your CPU and L3 changes with it. This is the most likely cause of a
  lone L3 mismatch. Check what is actually loaded with `OPENBLAS_VERBOSE=2`.
- **Running on arm64 / Apple Silicon?** L3 will differ regardless: Accelerate is
  not OpenBLAS and takes no `CORETYPE`. The other ten levels should match.
- **Envelope set, x86_64, and hashes still differ?** That is interesting to us.
  [Open an issue](../../issues) with your `ladder_constrained.txt`, the
  environment header the script prints, and `lscpu | grep "Model name"`. We will
  publish the finding either way — the last person who contradicted this table
  was us, and the table changed.

## 6. Contact

Security reports: see [`security.txt`](security.txt) — RFC 9116.
Everything else: open an issue.

---

## About

Kairos Systems (Aether Paris SAS) builds deterministic decision infrastructure
for regulated industries: every pipeline execution is sealed and replayable,
with RFC 3161 dual-TSA timestamping.

Guided demonstration — live replay, walkthrough of the sealed run, Q&A — on
request: see the website.

Licensed under Apache 2.0. See [`LICENSE`](LICENSE).
