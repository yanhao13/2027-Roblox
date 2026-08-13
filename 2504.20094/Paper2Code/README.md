**not o3-mini, claude fable 5 is the model working here. for reference: [going-doer/Paper2Code(4.8k)](https://github.com/going-doer/paper2code).**

# Paper2Code → MATCHA

This repository documents a complete **paper-to-code** run: taking the MATCHA
paper and producing a faithful code repository with the official
[Paper2Code / PaperCoder](https://github.com/going-doer/Paper2Code) multi-agent
pipeline, **adapted to run on the Anthropic API** (`claude-fable-5`) instead of
the original OpenAI / vLLM backends.

Target paper: *Toward Safe and Human-Aligned Game Conversational Recommendation
via Multi-Agent Decomposition* (arXiv:2504.20094).

## What's here

```
paper2code-work/
├── Paper2Code/          # PaperCoder pipeline (official repo + DeepSeek adaptation)
│   ├── codes/
│   │   ├── anthropic_adapter.py
│   │   ├── 1_planning.py / 2_analyzing.py / 3_coding.py / 4_debugging.py
│   │   └── utils.py / eval.py / 0_pdf_process.py / 1.1_extract_config.py …
│   └── scripts/run_latex.sh, run.sh, …
├── matcha_src/          # MATCHA paper LaTeX source (from arXiv e-print)
│   └── MATCHA_cleaned.tex   # flattened/cleaned input fed to PaperCoder
├── outputs/
│   └── MATCHA/          # final generated repository (17 .py + config + walkthrough)
├── clean_latex.py       # LaTeX flattening/cleaning script
├── gen_walkthrough.py   # generates walkthrough.ipynb
├── build_deliverables.py
├── run_matcha.sh        # full run (planning → config → analyzing → coding)
└── run_matcha_continue.sh
```

## Adaptations vs. the official repo

1. **Backend**: `from openai import OpenAI` replaced with a
   `deepseek_adapter.OpenAI` shim (stdlib `urllib` → `api.deepseek.com/chat/completions`).
2. **Bug fix — nested paths**: `2_analyzing.py` crashed writing artifacts for
   nested task files (`agents/risk_control.py`); added `os.makedirs(dirname)`.
3. **Bug fix — resume**: added skip-if-exists logic to `2_analyzing.py` and
   `3_coding.py` so an interrupted run can resume without re-spending.
4. **Robustness**: `utils.cal_cost` zero-fallback for unknown models;
   `content_to_json` strips markdown code fences.

## Note

A sibling production implementation (FastAPI + ChromaDB + Celery + Streamlit +
Prometheus + Docker) lives in the directory of the parent workspace.
