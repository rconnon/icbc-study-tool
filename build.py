#!/usr/bin/env python3
"""Build index.html: embed data/*.json into src/template.html."""
import json
import glob
import os

ROOT = os.path.dirname(os.path.abspath(__file__))


def load_data():
    chapters = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "ch*.json"))):
        with open(path) as f:
            d = json.load(f)
        ch = d["chapter"]
        for kind in ("cards", "questions"):
            for i, item in enumerate(d[kind]):
                item["id"] = f"{ch}-{kind[0]}{i}"
                item["chapter"] = ch
        chapters[str(ch)] = {
            "title": d["title"],
            "cards": d["cards"],
            "questions": d["questions"],
        }
    with open(os.path.join(ROOT, "data", "extras.json")) as f:
        extras = json.load(f)
    lessons = {}
    for path in sorted(glob.glob(os.path.join(ROOT, "data", "lessons", "*.json"))):
        with open(path) as f:
            d = json.load(f)
        lessons[str(d["chapter"])] = d
    return {"chapters": chapters, "extras": extras, "lessons": lessons}


def build():
    data = load_data()
    with open(os.path.join(ROOT, "src", "template.html")) as f:
        template = f.read()
    blob = json.dumps(data, ensure_ascii=False, separators=(",", ":"))
    # keep the JSON safe inside a <script> block
    blob = blob.replace("</", "<\\/")
    assert "__STUDY_DATA__" in template, "template placeholder missing"
    html = template.replace("__STUDY_DATA__", blob)
    out = os.path.join(ROOT, "index.html")
    with open(out, "w") as f:
        f.write(html)
    n_c = sum(len(c["cards"]) for c in data["chapters"].values())
    n_q = sum(len(c["questions"]) for c in data["chapters"].values())
    print(f"wrote index.html ({len(html)//1024} KB, {n_c} cards, {n_q} questions)")


if __name__ == "__main__":
    build()
