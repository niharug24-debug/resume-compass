# Verification — 24 September 2026

- Python 3.12, Windows; 9 unittest tests passed.
- Tests cover technology boundaries/aliases, deterministic scoring, zero-skill input, grounded wording rules, PDF extraction, blank/malformed/encrypted/oversized/too-many-page rejection, input validation, report save/reopen/delete, health and static routes.
- Full API flow used a generated synthetic resume PDF and a temporary SQLite database.
- JavaScript syntax check passed with Node.
- Headless Microsoft Edge browser check passed: sample form → 50% comparison → accept wording → summary download → reload → reopen history → delete.
- No uncaught JavaScript errors in that browser flow.
- Desktop (1365 px) and mobile (390 px) screenshots inspected; mobile horizontal overflow check passed.
- Test-discovered SQLite connection leak fixed; suite rerun successfully.

The browser automation used the pasted sample; PDF upload was tested at the API layer. Clipboard success was not automatically tested; the UI has a manual-copy fallback. No live AI, OCR, authentication, public deployment, or performance benchmark is claimed. Starlette emits a deprecation warning for its httpx test transport; the tests pass. A malformed PDF intentionally emits pypdf's EOF warning during its rejection test.

Top-level versions are in requirements.txt; complete tested versions are in requirements-lock.txt. Install the lock file for the closest reproduction of this environment.
