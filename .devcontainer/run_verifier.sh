#!/usr/bin/env bash
set -e

echo "=============================================================================="
echo "KAIROS VERIFIER — automatic replay (Codespaces)"
echo "=============================================================================="

EXPECTED_SHA="e2f6cd4b4e67e98d19adbd76e9e8c12eae0276cca3755b324e55f3b966525be4"
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
    "L0": "1d9e01d16d6389002d78dd1a6456743273cdf2277fd781c872bc428a567ef85b",
    "L1": "84af2aaa28305585d54e02e8de41148d894fe66faadab54f38b3727c82e78580",
    "L1b": "9984517da6ef41ff74b85274d57301e063b46dfbce4892ea3841b19800a6785f",
    "L2": "86ca842440c89f745a9b4aa1b0c7972fa6879c055f334b867d7cfb1ccd233f4a",
    "L3": "60da9d0bfeb7bb992dfa73ced6bb6634840be86783f20979e44bfcfbf8906fe9",
    "L3b": "db791086e49a76e2087927d7a010666707b3945fafb71b2446164d672a8c6872",
    "L4": "0bf4f040e2ee2721aca6e3c74d20f74198cef85ca4bba4348a7152f00e44e9b3",
    "L4b": "9d40cfbddb0c14caadec21c852b5d6578767fb14da59ad563a70bdc8b23dcb18",
    "L5": "687b5cae54c0f69f4bf6c54bb60d737a27b1a2c9965e577c7846e462fe976703",
    "L5b": "d36851807abf6013acd4b7be2c66f25d3ec4e82d84b6e451bf84fc1beafd38d3",
}

with open("ladder_constrained.txt") as f:
    text = f.read()

rows = re.findall(r"^(L\d+b?)\s+\S.*?\s([0-9a-f]{64})\s", text, re.MULTILINE)
got = {lvl: h for lvl, h in rows}
l6_hashes = re.findall(r"^L6\s+\S.*?\s([0-9a-f]{64})\s", text, re.MULTILINE)

matched, total = 0, 12
print(f"{'LEVEL':<6}{'YOUR RESULT':<68}{'STATUS'}")
for lvl, ref in EXPECTED_HASHES.items():
    ok = got.get(lvl) == ref
    matched += ok
    print(f"{lvl:<6}{got.get(lvl,'—'):<68}{'MATCH' if ok else 'DIVERGE'}")

l6_ref = "e05c0b80de5ce5e4f092d0de2277e40bebdee593d6fc1a8c96db8ceb03effaf6"
for i, h in enumerate(l6_hashes[:2]):
    ok = h == l6_ref
    matched += ok
    print(f"{'L6#'+str(i+1):<6}{h:<68}{'MATCH' if ok else 'DIVERGE'}")

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
