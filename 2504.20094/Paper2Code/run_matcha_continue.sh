#!/bin/bash
set -e
BASE=/Users/yanhao/Downloads/paper2code-work
CODES=$BASE/Paper2Code/codes
PAPER=$BASE/matcha_src/MATCHA_cleaned.tex
OUT=$BASE/outputs/MATCHA
REPO=$BASE/outputs/MATCHA_repo
PY=/Users/yanhao/.workbuddy/binaries/python/envs/default/bin/python

mkdir -p "$OUT" "$REPO"

echo "===== [3/4] Analyzing (resume) ====="
$PY "$CODES/2_analyzing.py" \
    --paper_name MATCHA \
    --gpt_version deepseek-v4-pro \
    --pdf_latex_path "$PAPER" \
    --paper_format LaTeX \
    --output_dir "$OUT"

echo "===== [4/4] Coding ====="
$PY "$CODES/3_coding.py" \
    --paper_name MATCHA \
    --gpt_version deepseek-v4-pro \
    --pdf_latex_path "$PAPER" \
    --paper_format LaTeX \
    --output_dir "$OUT" \
    --output_repo_dir "$REPO"

echo "===== DONE ====="
find "$REPO" -type f | sort
