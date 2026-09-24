# Resume Compass

A beginner-friendly resume keyword comparison project built with **Python, FastAPI, SQLite, HTML, CSS and JavaScript**. This is a deliberately smaller implementation of the supplied internship brief. It is a local, single-user learning app, with rule-based suggestions rather than AI.

## Run on Windows

Install Python 3.12 or newer, open PowerShell in this folder, then run:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn main:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000. API documentation is at http://127.0.0.1:8000/docs.
Click **Try a sample**, then **Compare my resume**. Stop the server with Ctrl+C.
If `py` is unavailable, install Python with its Windows launcher or replace `py` with your Python executable's full path. Port busy? Use `--port 8001` and open that port instead.

## Test

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests -v
```

## What is implemented

- Text-based PDF extraction using pypdf, or manual text entry.
- 5 MB upload limit, 10-page limit, PDF signature and parser checks; helpful empty, encrypted and malformed PDF errors.
- Editable extracted text, explicit skill aliases, punctuation-aware matching.
- Score = matched unique job skills / recognized unique job skills × 100, rounded. No recognized skills produces N/A.
- Two simple verb substitution rules, with optional acceptance and reviewed-text copy.
- SQLite report history, reopen, deletion, and text summary download.
- No external requests or API keys at runtime.

## Read the code in this order

1. `matcher.py`: dictionary, regular expressions, sets, score, wording rules.
2. `database.py`: SQLite table and four parameterized operations.
3. `main.py`: validation and HTTP endpoints; serves the frontend too.
4. `static/index.html`: accessible form and result containers.
5. `static/app.js`: fetch requests, DOM updates, accepted suggestions.
6. `tests/test_app.py`: deterministic scoring and API integration tests.

Browser → FastAPI → matcher → SQLite → JSON response → browser.
PDF bytes are parsed in memory and discarded. Extracted text is saved only when you run a comparison. Each report stores its own input texts and result JSON. A single table keeps this version easy to explain; separate users/resumes/jobs tables would suit a multi-user version.

## Scope and limitations

Keep the server bound to `127.0.0.1`. There is **no authentication or user isolation**; everyone using this local app can access its reports. This is not ready for public deployment. Original PDFs are not stored. Reports live in `data/reports.db`; delete a report through the UI. SQLite deletion removes it from application access, but is not guaranteed forensic erasure, and copies/backups are not removed. Do not use real sensitive documents for a public demo.

The skill dictionary is small and focused on software roles. It does not understand context, negation (e.g. “no Python experience”), skill proficiency, or mandatory versus optional requirements. The job description can mention a technology without requiring it. Review the input and result. No OCR, AI, login, React, PostgreSQL, Docker, embeddings, or machine learning is implemented. Do not list those as completed technologies on your resume.

The PDF byte/page limits are practical local safeguards, not a sandbox against malicious decompression or parser resource exhaustion. Use trusted sample documents; public hosting needs stronger request limits and isolated parsing. Accept/reject choices are local to the current view; saved reports retain original results.

`RESUME_DB` optionally overrides the database path. No `.env` loader or secrets are needed. Schema creation is `CREATE TABLE IF NOT EXISTS`, not a migration system. Pin top-level packages in `requirements.txt`; `requirements-lock.txt` records the complete verified dependency set.

## Learning milestones

- [x] Build and test the comparison engine and upload flow.
- [x] Add SQLite history and review/export controls.
- [x] Write interview explanations and honest resume bullets.
- [ ] Explain every function aloud and change the skill dictionary yourself.
- [ ] Add a meaningful rule and a corresponding test independently.
- [ ] Optional later project: real AI suggestions with validated output.
- [ ] Optional later project: login, ownership checks and deployment safeguards.

References: [FastAPI](https://fastapi.tiangolo.com/), [pypdf text extraction](https://pypdf.readthedocs.io/en/stable/user/extract-text.html), [Python SQLite](https://docs.python.org/3/library/sqlite3.html).
