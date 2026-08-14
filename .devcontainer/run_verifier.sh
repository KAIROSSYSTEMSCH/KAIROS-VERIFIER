#!/usr/bin/env bash
set -e

echo "=============================================================================="
echo "KAIROS VERIFIER — automatic replay (Codespaces)"
echo "=============================================================================="

EXPECTED_SHA="f23de8df0d216dc6d79d0402103dcb2bb5ed1132eee83f10bf698c2cbae6d75c"
GOT_SHA=$(sha256sum determinism_ladder.py | awk '{print $1}')

echo "expected sha256: $EXPECTED_SHA"
echo "got sha256     : $GOT_SHA"

if [ "$GOT_SHA" != "$EXPECTED_SHA" ]; then
  echo ""
  echo "✖ REPLAY NOT VERIFIED — script hash does not match v1.0."
  exit 1
fi
echo "✓ Script authenticated against v1.0."
echo ""

pip install -q -r requirements.txt

OPENBLAS_CORETYPE=Haswell OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 \
PYTHONHASHSEED=0 python3 determinism_ladder.py > ladder_constrained.txt

python3 << 'PYEOF'
import re

EXPECTED_HASHES = {
    "L0": "1d9e01d16d638900", "L1": "84af2aaa28305585", "L1b": "9984517da6ef41ff",
    "L2": "86ca842440c89f74", "L3": "60da9d0bfeb7bb99", "L3b": "db791086e49a76e2",
    "L4": "0bf4f040e2ee2721", "L4b": "9d40cfbddb0c14ca", "L5": "687b5cae54c0f69f",
    "L5b": "d36851807abf6013",
}

with open("ladder_constrained.txt") as f:
    text = f.read()

rows = re.findall(r"^(L\d+b?)\s+\S.*?\s([0-9a-f]{16})\s", text, re.MULTILINE)
got = {lvl: h for lvl, h in rows}
l6_hashes = re.findall(r"^L6\s+\S.*?\s([0-9a-f]{16})\s", text, re.MULTILINE)

matched, total = 0, 12
print(f"{'LEVEL':<6}{'YOUR RESULT':<20}{'STATUS'}")
for lvl, ref in EXPECTED_HASHES.items():
    ok = got.get(lvl) == ref
    matched += ok
    print(f"{lvl:<6}{got.get(lvl,'—'):<20}{'MATCH' if ok else 'DIVERGE'}")

l6_ref = "e05c0b80de5ce5e4"
for i, h in enumerate(l6_hashes[:2]):
    ok = h == l6_ref
    matched += ok
    print(f"{'L6#'+str(i+1):<6}{h:<20}{'MATCH' if ok else 'DIVERGE'}")

print("")
print("==============================================================================")
if matched == total:
    print(f"{matched} / {total} MATCH — YOUR REPLAY")
    print("REPLAY VERIFIED")
else:
    print(f"{matched} / {total} MATCH — YOUR REPLAY")
    print("REPLAY NOT FULLY VERIFIED")
print("==============================================================================")
PYEOF
