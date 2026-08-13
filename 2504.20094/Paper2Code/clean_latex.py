"""Flatten and clean the MATCHA (arXiv 2504.20094) LaTeX source into a
PaperCoder-readable `.tex` (same style as examples/Transformer_cleaned.tex).

Run from the matcha_src/ directory containing acl_latex.tex and content/.
"""
import re
import os

def resolve_inputs(text, depth=0):
    if depth > 10:
        return text
    def repl(m):
        path = m.group(1).strip()
        candidates = [
            path,
            path + ".tex",
            os.path.join("content", path),
            os.path.join("content", path + ".tex"),
        ]
        for c in candidates:
            if os.path.exists(c):
                with open(c, encoding="utf-8") as f:
                    return resolve_inputs(f.read(), depth + 1)
        return f"% [UNRESOLVED INPUT: {path}]"
    return re.sub(r"\\input\s*\{([^}]*)\}", repl, text)

with open("acl_latex.tex", encoding="utf-8") as f:
    full = f.read()

# 1. Extract title (may span multiple lines)
title = ""
m = re.search(r"\\title\{(.*?)\}\s*\n", full, re.DOTALL)
if m:
    title = " ".join(m.group(1).split()).replace("\\\\", " ")
    title = title.replace("\\", "")

# 2. Extract body between document env
m = re.search(r"\\begin\{document\}(.*?)\\end\{document\}", full, re.DOTALL)
body = m.group(1) if m else ""

# 3. Resolve \input{...}
body = resolve_inputs(body)

# 4. Drop bibliography / style commands and any thebibliography env
body = re.sub(r"\\bibliography\s*\{[^}]*\}", "", body)
body = re.sub(r"\\bibliographystyle\s*\{[^}]*\}", "", body)
body = re.sub(r"\\begin\{thebibliography\}.*?\\end\{thebibliography\}",
              "", body, flags=re.DOTALL)

# 5. Drop full-line comments
lines = [ln for ln in body.split("\n") if not ln.lstrip().startswith("%")]
body = "\n".join(lines)

# 6. Drop \includegraphics (image noise), keep captions
body = re.sub(r"\\includegraphics(\[[^\]]*\])?\{[^}]*\}", "", body)

# 7. Collapse blank lines
body = re.sub(r"\n{3,}", "\n\n", body)

out = ""
if title:
    out += "\\title{" + title + "}\n\n"
out += body.strip() + "\n"

with open("MATCHA_cleaned.tex", "w", encoding="utf-8") as f:
    f.write(out)

print(f"[OK] wrote MATCHA_cleaned.tex ({len(out)} chars)")
print("--- preview ---")
print(out[:800])
