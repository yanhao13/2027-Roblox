import sys, json, os
sys.path.insert(0, "/Users/yanhao/Downloads/paper2code-work/Paper2Code/codes")
from utils import extract_planning, content_to_json

BASE = "/Users/yanhao/Downloads/paper2code-work"
OUT = f"{BASE}/outputs/MATCHA"
REPO = f"{BASE}/outputs/MATCHA_repo"

ctx = extract_planning(f"{OUT}/planning_trajectories.json")
overview = ctx[0]      # overall plan
arch = content_to_json(ctx[1])   # architecture design
logic = content_to_json(ctx[2])  # logic design (task list, required packages)

approach = arch.get("Implementation approach", "")
file_list = arch.get("File list", [])
class_diagram = arch.get("Data structures and interfaces", "")
seq_diagram = arch.get("Program call flow", "")
unclear = arch.get("Anything UNCLEAR", "")
required_pkgs = logic.get("Required packages", [])
logic_analysis = logic.get("Logic Analysis", [])

# --- architecture_prompt.txt ---
lines = []
lines.append("# MATCHA — 架构蓝图（Architecture Prompt）")
lines.append("")
lines.append("论文：Toward Safe and Human-Aligned Game Conversational Recommendation")
lines.append("      via Multi-Agent Decomposition (arXiv 2504.20094)")
lines.append("")
lines.append("## 1. Implementation approach（实现思路）")
lines.append("")
lines.append(approach.strip())
lines.append("")
lines.append("## 2. File list（文件清单）")
lines.append("")
for f in file_list:
    lines.append(f"- `{f}`")
lines.append("")
lines.append("## 3. Data structures & interfaces（类设计，mermaid classDiagram）")
lines.append("")
lines.append("```mermaid")
# best-effort reformat: split on class boundaries and relation tokens
diag = class_diagram.replace("class ", "\nclass ").replace("Main -->", "\nMain -->").replace(
    "BaselineSystem <|--", "\nBaselineSystem <|--").replace("MatchaPipeline -->", "\nMatchaPipeline -->").replace(
    "CandidateAgent -->", "\nCandidateAgent -->").replace("ToolRegistry -->", "\nToolRegistry -->").replace(
    "RankingAgent -->", "\nRankingAgent -->").replace("RiskControlAgent -->", "\nRiskControlAgent -->").replace(
    "IntentAgent -->", "\nIntentAgent -->").replace("ReflectionAgent -->", "\nReflectionAgent -->").replace(
    "ExplanationAgent -->", "\nExplanationAgent -->").replace("ExplanationJudge -->", "\nExplanationJudge -->").replace(
    "Evaluator -->", "\nEvaluator -->").replace("DatasetLoader -->", "\nDatasetLoader -->")
lines.append(diag.strip())
lines.append("```")
lines.append("")
lines.append("## 4. Program call flow（调用流程，mermaid sequenceDiagram）")
lines.append("")
lines.append("```mermaid")
seq = seq_diagram.replace("participant ", "\nparticipant ").replace("M->>", "\nM->>").replace(
    "P->>", "\nP->>").replace("RC->>", "\nRC->>").replace("IA->>", "\nIA->>").replace(
    "CA->>", "\nCA->>").replace("TR->>", "\nTR->>").replace("RA->>", "\nRA->>").replace(
    "RF->>", "\nRF->>").replace("EA->>", "\nEA->>").replace("LC-->>", "\nLC-->>").replace(
    "DB-->>", "\nDB-->>").replace("DL-->>", "\nDL-->>").replace("EV->>", "\nEV->>").replace(
    "JG->>", "\nJG->>")
lines.append(seq.strip())
lines.append("```")
lines.append("")
lines.append("## 5. Anything UNCLEAR / assumptions（未明事项与假设）")
lines.append("")
lines.append(unclear.strip())
lines.append("")
with open(f"{REPO}/architecture_prompt.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(lines))
print("[OK] architecture_prompt.txt")

# --- requirements.txt ---
with open(f"{REPO}/requirements.txt", "w", encoding="utf-8") as f:
    f.write("\n".join(required_pkgs) + "\n")
print("[OK] requirements.txt")
print("packages:", len(required_pkgs))
