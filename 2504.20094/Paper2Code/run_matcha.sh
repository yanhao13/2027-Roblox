#!/bin/bash
set -e
BASE=/Users/yanhao/Downloads/paper2code-work
CODES=$BASE/Paper2Code/codes
PAPER=$BASE/matcha_src/MATCHA_cleaned.tex
OUT=$BASE/outputs/MATCHA
REPO=$BASE/outputs/MATCHA_repo
PY=/Users/yanhao/.workbuddy/binaries/python/envs/default/bin/python

mkdir -p "$OUT" "$REPO"

echo "===== [1/4] Planning ====="
$PY "$CODES/1_planning.py" \
    --paper_name MATCHA \
    --gpt_version claude-fable-5 \
    --pdf_latex_path "$PAPER" \
    --paper_format LaTeX \
    --output_dir "$OUT"

echo "===== [2/4] Extract config ====="
$PY "$CODES/1.1_extract_config.py" --paper_name MATCHA --output_dir "$OUT"
cp -f "$OUT/planning_config.yaml" "$REPO/config.yaml"

echo "===== [3/4] Analyzing ====="
$PY "$CODES/2_analyzing.py" \
    --paper_name MATCHA \
    --gpt_version claude-fable-5 \
    --pdf_latex_path "$PAPER" \
    --paper_format LaTeX \
    --output_dir "$OUT"

echo "===== [4/4] Coding ====="
$PY "$CODES/3_coding.py" \
    --paper_name MATCHA \
    --gpt_version claude-fable-5 \
    --pdf_latex_path "$PAPER" \
    --paper_format LaTeX \
    --output_dir "$OUT" \
    --output_repo_dir "$REPO"

echo "===== DONE ====="
echo "--- repo files ---"
find "$REPO" -type f | sort
