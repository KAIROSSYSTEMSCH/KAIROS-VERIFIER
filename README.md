# Kairos Replay Kit — Numerical Determinism Verifier (v1.0)

**Don't trust us. Run it.**

Kairos Systems claims that its execution layer is byte-reproducible. This repository
contains the verifier we used to measure that claim, the exact hashes we obtained,
and the protocol to reproduce them on your own machine. We do not participate.

If your hashes differ from ours, [open an issue](../../issues). A verifier that
cannot contradict us verifies nothing.

---

## 1. What you are about to do

Run a script that uses nothing but `numpy`, `pandas` and `xgboost`. It checks its
own environment against a declared, sealed envelope before measuring anything, then
runs the measurement three times to confirm it is stable within that environment.
Compare your output to ours. It takes about 3 minutes.

## 2. Protocol

```bash
# 1 — authenticate the script (it must be the one we measured)
sha256sum determinism_ladder.py
# expected: e2f6cd4b4e67e98d19adbd76e9e8c12eae0276cca3755b324e55f3b966525be4

# 2 — isolated environment, pinned versions
python3 -m venv env
./env/bin/pip install -r requirements.txt

# 3 — run inside the declared envelope
OPENBLAS_CORETYPE=Haswell \
OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
PYTHONHASHSEED=0 ./env/bin/python3 determinism_ladder.py
```

The script tells you, before printing a single measurement, whether your
environment matches the sealed envelope (`SEALED_RUNTIME_MATCH` or
`OUTSIDE_SEALED_RUNTIME`, with every deviation listed by name). Inside the
envelope, it repeats the twelve measurements three times and reports whether
they were stable (`DETERMINISM_PASS` or `DETERMINISM_FAIL`) before you ever
compare a single hash by hand.

Then compare your `L0`–`L6` hashes to [`EXPECTED_HASHES.md`](EXPECTED_HASHES.md).

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
complete, testable, and self-checked by the tool itself — and that we correct
the envelope when measurement contradicts it rather than softening the claim.
Inside the declared envelope, **12 of 12 measurements are byte-identical
across four independent environments** — two cloud notebook providers
(Google Colab, Kaggle) and two Kairos-operated instances (Scaleway, France;
Infomaniak, Switzerland), across two Python minor versions.

The envelope is: pinned library versions, `OPENBLAS_CORETYPE`, thread caps,
`PYTHONHASHSEED`. Every element is a variable we control and publish — none of
it is hardware we have to hope for, and the script verifies every element of
it itself rather than asking you to check by hand. See `EXPECTED_HASHES.md`,
including the kernel table: L3 follows the BLAS kernel actually loaded
(`OPENBLAS_VERBOSE=2`), and `OPENBLAS_CORETYPE=Haswell` fixes it to the same
value across environments.

**Outside the envelope, the script says so and stops there.** It still runs
and prints the twelve measurements — nothing is hidden — but it does not
compare them to the sealed reference, and it emits no PASS/FAIL verdict.
Kairos does not claim byte-identical reproducibility across arbitrary
hardware; it claims it within a declared, verified envelope, and the tool
enforces that distinction automatically.

**It does not prove** that the Kairos pipeline is correct, nor that our sealed
Shadow Run of 2026-06-06 is valid. This kit tests the numerical substrate, not
the product.

**Where the broader pipeline stands, stated here before anyone asks:** the full
Kairos pipeline (46 datasets, 9.67M rows) is currently undergoing third-party
replay validation. That campaign is separate from this kit, ongoing, and not
yet complete. Anyone claiming it is finished — including us — would be wrong.

## 5. If your hashes differ

- **Script reports `OUTSIDE_SEALED_RUNTIME`?** Read the deviation list it
  prints — it names exactly which library version, OS, or environment
  variable does not match. Fix those and re-run before comparing anything.
- **`SEALED_RUNTIME_MATCH` but `DETERMINISM_FAIL`?** The script itself is
  telling you a level was unstable across its own three repeated passes,
  independent of our reference values. [Open an issue](../../issues) with
  the full output — this is a more interesting finding than a simple
  mismatch against our table.
- **`SEALED_RUNTIME_MATCH`, `DETERMINISM_PASS`, but hashes differ from
  `EXPECTED_HASHES.md`?** That is the most interesting case of all. Open an
  issue with your full output. We will publish the finding either way — the
  last person who contradicted this table was us, and the table changed.
- **Running on arm64 / Apple Silicon, or macOS generally?** The script will
  correctly report `OUTSIDE_SEALED_RUNTIME` — the envelope is Linux x86_64 by
  design. See `EXPECTED_HASHES.md` for macOS reference values, published so a
  divergence there is not misread as a failure.

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
