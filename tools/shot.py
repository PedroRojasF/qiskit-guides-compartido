"""Capturas de una lección en varios tamaños, en beats concretos.
uv run --with playwright python tools/shot.py <id> <beat,beat,...> [movil|laptop]
Ej.: tools/shot.py cap01-conservacion-de-la-norma 0,3,8 laptop
"""
import sys
from pathlib import Path
from playwright.sync_api import sync_playwright

lid = sys.argv[1]
beats = [int(b) for b in sys.argv[2].split(",")]
sizes = {"movil": (390, 844), "laptop": (1366, 768)}
which = sys.argv[3] if len(sys.argv) > 3 else "laptop"
w, h = sizes[which]
url = f"http://localhost:8810/lesson.html?l={lid}"
out = Path(__file__).parent.parent / "shots"
out.mkdir(exist_ok=True)
with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = b.new_page(viewport={"width": w, "height": h})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(url)
    pg.wait_for_timeout(1200)
    pg.click("#go")
    cur = 0
    for t in beats:
        while cur < t:
            pg.click("#next"); cur += 1
        pg.wait_for_timeout(int(sys.argv[4]) if len(sys.argv) > 4 else 9000)
        pg.screenshot(path=str(out / f"{which}-b{t}.png"))
    print("errores:", errs)
    b.close()
