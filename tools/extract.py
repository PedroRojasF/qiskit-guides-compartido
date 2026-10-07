"""Convierte las guías (.mdx / .ipynb) de docs/guides en texto legible en docs/text/<nombre>.md.

    uv run python tools/extract.py
Las celdas de código van entre ```python y sus salidas de texto entre ```salida (las imágenes se omiten).
"""
import json
from pathlib import Path

ROOT = Path(__file__).parent.parent
SRC, OUT = ROOT / "docs" / "guides", ROOT / "docs" / "text"
OUT.mkdir(parents=True, exist_ok=True)

for f in sorted(SRC.iterdir()):
    if f.suffix == ".mdx":
        txt = f.read_text(encoding="utf-8")
    else:
        parts = []
        for c in json.loads(f.read_text(encoding="utf-8"))["cells"]:
            src = "".join(c["source"])
            if c["cell_type"] == "markdown":
                parts.append(src)
            elif c["cell_type"] == "code":
                parts.append(f"```python\n{src}\n```")
                for o in c.get("outputs", []):
                    t = o.get("text") or o.get("data", {}).get("text/plain")
                    if t:
                        parts.append("```salida\n" + "".join(t)[:1500] + "\n```")
                    elif "image/png" in o.get("data", {}):
                        parts.append("[imagen]")
        txt = "\n\n".join(parts)
    (OUT / f"{f.stem}.md").write_text(txt, encoding="utf-8")
print(len(list(OUT.iterdir())), "páginas")
