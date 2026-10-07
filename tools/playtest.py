"""Prueba de reproducción real (con audio y tiempos): avanza, espera la pregunta, responde y continúa.
    uv run --with playwright python tools/playtest.py
"""
from playwright.sync_api import sync_playwright
from pathlib import Path
import os
import sys

lesson_id = sys.argv[1] if len(sys.argv) > 1 else "p6-panorama"
base_url = os.environ.get("PLAYTEST_URL", "http://localhost:8810").rstrip("/")
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
browser_path = next((p for p in (
    Path(r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Microsoft\Edge\Application\msedge.exe"),
    Path(r"C:\Program Files\Google\Chrome\Application\chrome.exe"),
    Path(r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"),
) if p.exists()), None)

with sync_playwright() as p:
    b = p.chromium.launch(
        executable_path=str(browser_path) if browser_path else None,
        args=["--autoplay-policy=no-user-gesture-required"],
    )
    pg = b.new_page(viewport={"width": 1366, "height": 768})
    errs = []
    pg.on("pageerror", lambda e: errs.append(str(e)))
    pg.on("console", lambda m: errs.append(m.text) if m.type == "error" else None)
    pg.goto(f"{base_url}/lesson.html?l={lesson_id}")
    pg.wait_for_timeout(1500)
    print("inicio:", pg.inner_text("#start-meta"))
    pg.click("#go")
    pg.wait_for_timeout(4000)
    print("subtítulo t=4s:", pg.inner_text("#caption")[:70])
    pg.screenshot(path="shots/play-1.png")
    pg.locator("#timeline .seg.q").nth(0).click()   # primera pregunta de la lección
    pg.wait_for_selector("#ask.on", timeout=60000)
    print("pregunta visible en beat:", pg.evaluate("[...document.querySelectorAll('#timeline .seg')].findIndex(s => s.querySelector('i').style.width && s.querySelector('i').style.width !== '0%' && !s.classList.contains('done'))"))
    pg.click("#ask .opt >> nth=1")                 # incorrecta
    print("feedback error:", pg.inner_text("#ask .fb")[:60])
    pg.click("#ask .opt >> nth=2")                 # correcta
    print("feedback acierto:", pg.inner_text("#ask .fb")[:60])
    pg.screenshot(path="shots/play-2.png")
    pg.click("#ask .next-row .primary")
    pg.wait_for_timeout(3000)
    print("tras continuar:", pg.inner_text("#tag"))
    pg.locator("#timeline .seg.q").nth(1).click()
    pg.wait_for_selector("#ask.on", timeout=60000)
    pg.fill("#ask input", "4")
    pg.click("#ask .numrow .primary")
    print("numérica:", pg.inner_text("#ask .fb")[:50])
    pg.click("#ask .next-row .primary")
    pg.wait_for_timeout(500)
    pg.click("#next"); pg.wait_for_timeout(1500)
    print("fin visible:", pg.is_visible("#end"), "|", pg.inner_text("#end-score"))
    pg.screenshot(path="shots/play-3.png")
    print("errores:", errs or "ninguno")
    b.close()
