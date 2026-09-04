# Renáta's Love Language Quiz

Renáta's Love Language Quiz is a small full-stack romantic quiz experience. It uses original scene-based prompts inspired by the general idea of love languages, without copying or claiming to be the official Five Love Languages assessment.

## Architecture

- `backend/`: FastAPI, SQLAlchemy, SQLite, deterministic scoring, session cleanup, and tests.
- `frontend/`: React, TypeScript, Vite, mobile-first scene flow, illustrated results, and frontend tests.

## Prerequisites

- Python 3.11+
- Node.js 20+
- npm

## Backend Setup

```bash
cd backend
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
```

The backend runs at `http://127.0.0.1:8000`.

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend runs at `http://127.0.0.1:5173` and proxies `/api` requests to the backend.

## Tests

Backend:

```bash
cd backend
pytest
```

Frontend:

```bash
cd frontend
npm test
```

Question-bank validation is also available at:

```text
GET /api/questions/validation
```

## SQLite Behavior

SQLite is used as temporary server-side quiz storage. The schema contains:

- `quiz_sessions`: `id`, `created_at`, `updated_at`, `current_question`, `completed`
- `quiz_answers`: `id`, `session_id`, `question_id`, `selected_answer`, `created_at`, `updated_at`

The answers table uses a unique constraint on `session_id` and `question_id`, so changing an answer replaces the existing answer instead of creating duplicate score entries.

## Refresh And Session Lifecycle

A fresh browser page load starts a fresh quiz. On initial React load, the frontend removes any saved session token and calls `POST /api/session` with the previous token if one existed. The backend deletes that previous session and creates a new one.

The backend also deletes abandoned sessions older than 1 hour during session creation. The database is not intended as permanent history.

## Scoring Methodology

The internal dimensions are:

- `WORDS`: Words of Affirmation
- `TIME`: Quality Time
- `SERVICE`: Acts of Service
- `TOUCH`: Physical Affection
- `GIFTS`: Thoughtful Gifts

For each question:

- A gives `+1` to A's internal dimension.
- B gives `+1` to B's internal dimension.

Scores are normalized into percentages that sum to exactly `100`. The quiz is now a forced-choice A/B comparison. Rounding is deterministic: integer floors are calculated first, then the remaining points are allocated by largest fractional remainder with stable tie-breaking.

## Pairwise Comparison Methodology

The production question bank contains 30 questions. Every possible pair of the five dimensions appears exactly 3 times.

|         | WORDS | TIME | SERVICE | TOUCH | GIFTS |
| ------- | ----: | ---: | ------: | ----: | ----: |
| WORDS   |     - |    3 |       3 |     3 |     3 |
| TIME    |     3 |    - |       3 |     3 |     3 |
| SERVICE |     3 |    3 |       - |     3 |     3 |
| TOUCH   |     3 |    3 |       3 |     - |     3 |
| GIFTS   |     3 |    3 |       3 |     3 |     - |

## Profile Classification

The result profile is a gentle descriptive shape, not a diagnosis.

- `Broad`: highest percentage minus lowest percentage is `<= 8`.
- `Blended`: top two dimensions are within `4` percentage points and the profile is not broad.
- `Focused`: top dimension is at least `10` percentage points above second place.
- Any remaining middle case is presented as `Blended`.

The exact threshold logic is documented in `backend/app/scoring.py`.

## Result Interpretation

Each dimension has deterministic high, medium, and low interpretation templates. The combined summary is generated from the primary and secondary categories without using an external AI API.

## Privacy

The app does not collect names, email addresses, logins, analytics identifiers, advertising data, or personal accounts. Answers are used only for the temporary quiz session.
