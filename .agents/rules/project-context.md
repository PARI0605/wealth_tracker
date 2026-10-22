# Project Context & Engineering Discipline Rule

## Mandatory Pre-Task Routine:
Before starting ANY development, modification, or debugging task:
1. **Always Read Context First:** Read `docs/00_PROJECT_OVERVIEW.md`, `docs/01_FEATURES.md`, and the latest entries in `docs/09_PROGRESS_LOG.md`.
2. **Respect the Fixed Stack:**
   - **Title:** "Smart Wealth Tracker and Budget Planner using Python (Django) and MySQL" (Do not change).
   - **Python:** 3.13
   - **Django:** 5.1.5 (Pinned due to MySQL 8.0.40 compatibility).
   - **Database:** MySQL 8.0.40 (`wealth_tracker_db`).
   - **ML Stack:** scikit-learn & pandas.
   - **Frontend:** Bootstrap 5.3 + custom CSS tokens in `style.css` + Chart.js.
   - **Virtual Environment:** `venv` located at `wealth_tracker/venv/`.

## Mandatory Coding Constraints:
1. **Never Drop or Corrupt Data:** Use safe Django migrations for all schema adjustments.
2. **Multi-Tenant Security:** Every query must be scoped by `request.user`. No user may ever access or view another user's financial records.
3. **Financial Math:** Use Python `Decimal` and Django `DecimalField` for all currency amounts (never `float`).
4. **Thin Views / Fat Services:** Business logic must reside in `tracker/services/`, not bloated inside views.
5. **No Broken Links:** Ensure all newly created views, models, and forms have corresponding URL patterns and responsive templates.

## Mandatory Post-Task Routine:
At the end of every task:
1. Run `python manage.py check` to verify zero system warnings or syntax errors.
2. Update `docs/09_PROGRESS_LOG.md` with the dated task summary.
3. Update `docs/01_FEATURES.md` status flags.
4. Update `docs/10_VIVA_QA.md` with relevant viva defense questions.
