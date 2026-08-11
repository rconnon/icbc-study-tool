# BC Commercial Licence Study Tool

A self-contained, mobile-friendly study app for the ICBC knowledge tests for BC
Class 1, 2, 3 and 4 driver's licences. All content is derived from ICBC's official
[Driving Commercial Vehicles](https://www.icbc.com/assets/en/3ZRN0guL3MkbgvZvTCBfbu/drive_commercial_veh_full.pdf)
guide (August 2024 edition), with guide page references on every card and question.

**Live app:** https://rconnon.github.io/icbc-study-tool/ (GitHub Pages, deployed
from the `gh-pages` branch).

## Features

- **Class selection** — each class studies exactly the chapters ICBC's licence
  study chart (guide p. 2) assigns to it. Classes 2 and 4 get only the
  dangerous-goods pages (110–111) of chapter 5; classes 1 and 3 get all of it.
- **Learn** — guided chapter-by-chapter lessons built on evidence-based training
  design: chunked micro-sections, stated learning objectives, "must-know" callouts,
  retrieval-practice quick checks with immediate feedback, a mastery-threshold
  (80%) reinforcement quiz per chapter, interleaved review questions from earlier
  modules, and spaced-repetition "review due" nudges.
- **Cue cards** — 259 flip cards by chapter, with "got it / again" tracking.
- **Practice quizzes** — drawn at random from a 360-question bank, so every
  attempt is a different set; instant feedback with explanations and page refs.
- **Readiness check** — a timed 35-question practice exam mirroring the real
  test's reported format (35 questions, 80% to pass), a per-chapter mastery
  dashboard, and a three-part readiness checklist.

Progress is stored in `localStorage` on the device — no server, no accounts.

## Structure

| Path | What it is |
|---|---|
| `index.html` | The built app — a single self-contained file (open it, or serve statically) |
| `src/template.html` | App shell (UI + logic) with a `__STUDY_DATA__` placeholder |
| `data/ch01.json` … `ch11.json` | Study content per guide chapter (cards + questions) |
| `data/extras.json` | Examiners' tips and knowledge-test facts |
| `build.py` | Injects `data/` into the template → `index.html` |
| `tests/validate_data.py` | Schema/invariant checks + verifies `index.html` is freshly built |

## Development

```sh
python3 build.py              # rebuild index.html from src/ + data/
python3 tests/validate_data.py  # validate content and build freshness
```

Edit content in `data/`, then rebuild and commit both the data and `index.html`.

## Disclaimer

Unofficial study aid, not affiliated with ICBC. Always confirm details against
the current official guide; acts and regulations prevail over both the guide and
this app.
