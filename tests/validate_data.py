#!/usr/bin/env python3
"""Validate the study data and that index.html is freshly built from it."""
import json
import glob
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from build import load_data  # noqa: E402

# chapters each class studies, per the guide's licence study chart (p. 2);
# "dg" = the dangerous-goods slice of chapter 5 (guide pp. 110-111)
CLASS_CHAPTERS = {
    "c1": [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11],
    "c2": [1, 2, 3, 4, "dg", 6, 7, 8, 9, 10, 11],
    "c3": [1, 2, 3, 4, 5, 7, 8, 9, 10, 11],
    "c4": [1, 2, 3, 4, "dg", 6, 7, 8, 9, 10, 11],
}

errors = []


def check(cond, msg):
    if not cond:
        errors.append(msg)


def main():
    data = load_data()
    chapters = data["chapters"]

    check(set(chapters) == {str(n) for n in range(1, 12)},
          f"expected chapters 1-11, got {sorted(chapters)}")

    ids = set()
    for ch, d in sorted(chapters.items(), key=lambda kv: int(kv[0])):
        check(len(d["cards"]) >= 10, f"ch{ch}: too few cards ({len(d['cards'])})")
        check(len(d["questions"]) >= 15, f"ch{ch}: too few questions ({len(d['questions'])})")
        for c in d["cards"]:
            check(c["front"].strip() and c["back"].strip(), f"ch{ch} card {c['id']}: empty side")
            check(c["id"] not in ids, f"duplicate id {c['id']}")
            ids.add(c["id"])
        seen_q = set()
        answer_hist = [0, 0, 0, 0]
        for q in d["questions"]:
            qid = q["id"]
            check(isinstance(q["choices"], list) and len(q["choices"]) == 4,
                  f"ch{ch} {qid}: needs exactly 4 choices")
            check(len(set(q["choices"])) == 4, f"ch{ch} {qid}: duplicate choices")
            check(isinstance(q["answerIndex"], int) and 0 <= q["answerIndex"] <= 3,
                  f"ch{ch} {qid}: answerIndex out of range")
            check(q["q"].strip() != "", f"ch{ch} {qid}: empty question")
            check(q.get("explanation", "").strip() != "", f"ch{ch} {qid}: missing explanation")
            check(isinstance(q.get("page"), int) and q["page"] > 0,
                  f"ch{ch} {qid}: missing/invalid page")
            check(not re.search(r"\b(diagram|pictured|shown here|in this (image|picture))\b",
                                q["q"], re.I),
                  f"ch{ch} {qid}: references an image")
            key = q["q"].strip().lower()
            check(key not in seen_q, f"ch{ch} {qid}: duplicate question text")
            seen_q.add(key)
            check(qid not in ids, f"duplicate id {qid}")
            ids.add(qid)
            answer_hist[q["answerIndex"]] += 1
        check(max(answer_hist) <= len(d["questions"]) * 0.5,
              f"ch{ch}: answerIndex heavily skewed {answer_hist}")

    dg = [q for q in chapters["5"]["questions"] if q.get("section") == "dg"]
    check(len(dg) >= 5, f"too few dangerous-goods questions ({len(dg)})")
    check(all(108 <= q["page"] <= 113 for q in dg),
          "dg questions cite pages outside the 110-111 range")

    lessons = data["lessons"]
    expected_lessons = {str(n) for n in range(1, 12)} | {"dg"}
    check(set(lessons) == expected_lessons,
          f"expected lessons for chapters 1-11 + dg, got {sorted(lessons)}")
    for key, les in sorted(lessons.items()):
        check(len(les.get("objectives", [])) >= 3, f"lesson {key}: needs >=3 objectives")
        check(len(les.get("summary", [])) >= 3, f"lesson {key}: needs >=3 summary bullets")
        secs = les.get("sections", [])
        check(2 <= len(secs) <= 10, f"lesson {key}: odd section count ({len(secs)})")
        for si, sec in enumerate(secs):
            check(sec.get("title", "").strip() != "", f"lesson {key} s{si}: no title")
            check(3 <= len(sec.get("points", [])) <= 8,
                  f"lesson {key} s{si}: needs 3-8 points")
            checks_ = sec.get("check", [])
            check(1 <= len(checks_) <= 2, f"lesson {key} s{si}: needs 1-2 checks")
            for qi, q in enumerate(checks_):
                check(isinstance(q.get("choices"), list) and len(q["choices"]) == 4,
                      f"lesson {key} s{si} check {qi}: needs 4 choices")
                check(len(set(q["choices"])) == 4,
                      f"lesson {key} s{si} check {qi}: duplicate choices")
                check(isinstance(q.get("answerIndex"), int) and 0 <= q["answerIndex"] <= 3,
                      f"lesson {key} s{si} check {qi}: bad answerIndex")
                check(q.get("explanation", "").strip() != "",
                      f"lesson {key} s{si} check {qi}: missing explanation")

    extras = data["extras"]
    check(len(extras["examinersTips"]["general"]) >= 5, "too few examiners' tips")
    check(len(extras["knowledgeTestFacts"]) >= 5, "too few knowledge-test facts")

    for cls, chs in CLASS_CHAPTERS.items():
        pool = 0
        for k in chs:
            if k == "dg":
                pool += len(dg)
            else:
                pool += len(chapters[str(k)]["questions"])
        check(pool >= 100, f"{cls}: question pool too small ({pool})")

    # index.html must be the current build of template + data
    with open(os.path.join(ROOT, "index.html")) as f:
        html = f.read()
    m = re.search(r'<script type="application/json" id="study-data">(.*?)</script>',
                  html, re.S)
    check(bool(m), "index.html: study-data block missing")
    if m:
        embedded = json.loads(m.group(1).replace("<\\/", "</"))
        check(embedded == data,
              "index.html is stale — run ./build.py and commit the result")

    if errors:
        print(f"FAIL — {len(errors)} problem(s):")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    n_q = sum(len(c["questions"]) for c in chapters.values())
    n_c = sum(len(c["cards"]) for c in chapters.values())
    n_sec = sum(len(l["sections"]) for l in data["lessons"].values())
    print(f"OK — {n_c} cards, {n_q} questions, {len(dg)} dangerous-goods items, "
          f"{len(data['lessons'])} lessons ({n_sec} sections), index.html in sync")


if __name__ == "__main__":
    main()
