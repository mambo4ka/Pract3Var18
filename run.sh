#!/bin/sh
set -eu
cd "$(dirname "$0")"
if [ "$#" -eq 0 ]; then
    python3 src/assembler.py tests/data/test.asm output.bin --test
else
    python3 src/assembler.py "$@"
fi
