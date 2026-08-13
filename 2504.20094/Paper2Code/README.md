**not o3-mini, claude fable 5 is the model working here. for reference: [going-doer/Paper2Code(4.8k)](https://github.com/going-doer/paper2code).**

# Paper2Code → MATCHA
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

## Note

A sibling production implementation (FastAPI + ChromaDB + Celery + Streamlit +
Prometheus + Docker) lives in the directory of the parent workspace.
