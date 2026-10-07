"""Prueba el avance dentro de un paso: clic a mitad de un segmento de la línea de tiempo.
    uv run --with playwright python tools/seektest.py
"""
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    b = p.chromium.launch(args=["--autoplay-policy=no-user-gesture-required"])
    pg = b.new_page(viewport={"width": 1366, "height": 768}, color_scheme="dark")
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.goto("http://localhost:8810/lesson.html?l=a1-espacios-vectoriales")
    pg.wait_for_timeout(1200)
    pg.click("#go"); pg.wait_for_timeout(2500)
    seg = pg.locator("#timeline .seg").nth(2)          # paso "axiomas"
    box = seg.bounding_box()
    pg.mouse.click(box["x"] + box["width"] * 0.6, box["y"] + box["height"] / 2)
    pg.wait_for_timeout(1500)
    t = pg.evaluate("[window.__nar.currentTime, window.__nar.duration]")
    print("audio en", [round(x, 2) for x in t])
    shown = pg.evaluate("[...document.querySelectorAll('#scene li')].filter(li => !li.classList.contains('hid')).length")
    print("tag:", pg.inner_text("#tag"), "| ítems visibles de la lista:", shown)
    print("subtítulo:", pg.inner_text("#caption")[:80])
    pg.screenshot(path="shots/seek-1.png")
    pg.keyboard.press("Shift+ArrowLeft"); pg.wait_for_timeout(1200)
    print("tras −5 s, ítems visibles:", pg.evaluate("[...document.querySelectorAll('#scene li')].filter(li => !li.classList.contains('hid')).length"))
    pg.click("#fwd5"); pg.wait_for_timeout(800)
    print("tras +5 s, tag:", pg.inner_text("#tag"))
    done = pg.evaluate("[...document.querySelectorAll('#timeline .seg')].map(s => s.className).join(' | ')")
    print("segmentos:", done[:160])
    pg.goto("http://localhost:8810/lesson.html?l=a1-espacios-vectoriales"); pg.wait_for_timeout(1000)
    print("botón continuar:", pg.is_visible("#resume"), pg.inner_text("#resume") if pg.is_visible("#resume") else "")
    print("errores:", errs or "ninguno")
    b.close()
