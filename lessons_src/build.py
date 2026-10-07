"""Genera site/lessons/<id>/lesson.json y site/course.json a partir de plan.py y de los módulos parte*.py.

    python lessons_src/build.py              # escribe los JSON y comprueba la cobertura de las guías
    python lessons_src/build.py --tts        # además genera la narración (necesita uv y red)

La numeración de secciones (1.1, 1.2, …) sale del orden de plan.PARTS; la primera parte de la
etiqueta de cada paso se sustituye por esa sección. Las lecciones del plan que aún no están escritas
aparecen en el índice como «en preparación».
"""
import importlib
import json
import re
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent
ROOT = HERE.parent
sys.path.insert(0, str(HERE))
from plan import PARTS  # noqa: E402

SITE = ROOT / "site"
GUIDE = "https://quantum.cloud.ibm.com/docs/en/guides/"
ALL = {}
for f in sorted(HERE.glob("parte*.py")):
    for les in importlib.import_module(f.stem).LESSONS:
        if les["id"] in ALL:
            raise SystemExit(f"lección duplicada: {les['id']}")
        ALL[les["id"]] = les


def toc_pages():
    toc = json.loads((ROOT / "docs" / "_toc.json").read_text(encoding="utf-8"))
    out = []

    def walk(n):
        for c in n.get("children", []):
            u = c.get("url", "")
            if u == "/docs/guides":
                out.append("index")
            elif u.startswith("/docs/guides/"):
                out.append(u.rsplit("/", 1)[1])
            walk(c)
    walk(toc)
    return list(dict.fromkeys(out))


def coverage():
    planned = [g for p in PARTS for _, _, gs in p["lessons"] for g in gs]
    dup = {g for g in planned if planned.count(g) > 1}
    missing = [g for g in toc_pages() if g not in planned]
    extra = [g for g in planned if g not in toc_pages()]
    if dup or missing or extra:
        raise SystemExit(f"cobertura: repetidas {sorted(dup)}, sin lección {missing}, inexistentes {extra}")


ERRORS = []


def check(lesson):
    """Errores de autoría que conviene detectar antes de generar audio (se acumulan en ERRORS)."""
    def fail(msg):
        ERRORS.append(msg)
    for b in lesson["beats"]:
        marks = re.findall(r"\[\[(\w+)\]\]", b["say"])
        if len(marks) != len(set(marks)):
            fail(f"{lesson['id']}/{b['id']}: marca repetida")
        ids = set()

        def collect(items):
            for s in items:
                if s.get("id"):
                    ids.add(s["id"])
                collect([x for x in s.get("items", []) + s.get("body", []) if isinstance(x, dict)])
        collect(b["scene"])
        for a in b["actions"]:
            if a.get("at") == b["id"] and a["at"] not in marks:
                del a["at"]  # at=<id del paso> significa «al empezar el paso»
            if a.get("at") and a["at"] not in marks:
                fail(f"{lesson['id']}/{b['id']}: marca '{a['at']}' no está en la narración")
            if a.get("id") and a["id"] not in ids:
                fail(f"{lesson['id']}/{b['id']}: objeto '{a['id']}' no existe")
    if len({b["id"] for b in lesson["beats"]}) != len(lesson["beats"]):
        fail(f"{lesson['id']}: ids de paso repetidos")


def main():
    coverage()
    course = dict(parts=[])
    ordered = []
    for part in PARTS:
        entry = dict(title=part["title"], desc=part["desc"], lessons=[])
        for k, (lid, title, guides) in enumerate(part["lessons"], 1):
            section = f"{part['n']}.{k}"
            les = ALL.get(lid)
            if not les:
                entry["lessons"].append(dict(id=lid, section=section, title=title, summary="", minutes=0, pending=True))
                continue
            les["part"], les["section"] = part["title"], section
            for b in les["beats"]:
                b["tag"][0] = section
            names = {g: g for g in guides}
            les["practice"] = list(les["practice"]) + [
                "Guías originales: " + " · ".join(f"[{g}]({GUIDE}{'' if g == 'index' else g})" for g in names)]
            check(les)
            ordered.append(les)
            out = SITE / "lessons" / lid
            out.mkdir(parents=True, exist_ok=True)
            tf = out / "timings.json"
            beat_ids = {b["id"] for b in les["beats"]}
            if tf.exists():
                secs = sum(v["dur"] for key, v in json.loads(tf.read_text(encoding="utf-8")).items() if key in beat_ids)
            else:
                secs = sum(len(b["say"].split()) for b in les["beats"]) / 140 * 60
            secs += 45 * sum(1 for b in les["beats"] if "ask" in b)
            entry["lessons"].append(dict(id=lid, section=section, title=les["title"], summary=les["summary"],
                                         minutes=round(secs / 60)))
        course["parts"].append(entry)
    if ERRORS:
        raise SystemExit("\n".join(ERRORS))
    for a, b in zip(ordered, ordered[1:] + [None]):
        a["next"] = b["id"] if b else None
        (SITE / "lessons" / a["id"] / "lesson.json").write_text(json.dumps(a, ensure_ascii=False, indent=1), encoding="utf-8")
    (SITE / "course.json").write_text(json.dumps(course, ensure_ascii=False, indent=1), encoding="utf-8")
    total = sum(len(p["lessons"]) for p in PARTS)
    print(f"{len(ordered)} de {total} lecciones escritas, {sum(len(l['beats']) for l in ordered)} pasos; "
          f"cobertura de las {len(toc_pages())} guías: completa")
    if "--tts" in sys.argv:
        for les in ordered:
            subprocess.run(["uv", "run", "python", str(ROOT / "tools" / "tts.py"), str(SITE / "lessons" / les["id"])],
                           check=True, cwd=ROOT)


if __name__ == "__main__":
    main()
