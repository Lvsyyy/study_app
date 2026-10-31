<<<<<<< HEAD
# Study App

A PySide6 study app with a local SQLite database: practice questions by subject,
track accuracy and study time, save questions for later, and see your streak.
=======
# Study App GUI

A modular PySide6 study-app starter with a local SQLite database.
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f

## Run

```bash
python -m venv .venv
<<<<<<< HEAD
source .venv/bin/activate          # Linux / macOS
# .venv\Scripts\activate           # Windows
=======
source .venv/bin/activate          # Linux
# .venv\\Scripts\\activate         # Windows
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f
pip install -r requirements.txt
python main.py
```

<<<<<<< HEAD
## Develop

```bash
pip install -r requirements-dev.txt
ruff check .
pytest
```

## Features

- **Practice** – questions are ordered unseen first, then weakest, then least recently seen.
  Only your first answer to a question counts toward statistics; the time you took is recorded.
  Answers ignore case, extra spaces and trailing punctuation, accept `45` = `45.0` = `45,0`,
  and can have extra accepted alternatives.
- **Dashboard / Statistics** – streak, accuracy, study time (active time in the app only),
  average time per question, per-subject accuracy, weakest topics and a monthly activity heatmap.
- **Saved** – star a question while practising, then practise all saved ones.
- **Adding questions** – done from the backend (see below); the app itself has no add-question UI.
- **Settings** – colour theme and icon pack (Unicode glyph sets); window size is remembered.

## Importing questions from JSON (backend)

```python
from database.database import Database
from database.question_repository import QuestionRepository
from core.importer import import_file

print(import_file("questions.json", QuestionRepository(Database())))  # (count, errors)
```

A list of objects. `subject` must be one of the subjects in the sidebar. The import is
all-or-nothing: if anything is invalid, nothing is imported and every problem is listed.

```json
[
  {
    "subject": "Math",
    "topic": "Binary",
    "question": "Convert 101101 to decimal.",
    "answer": "45",
    "alt_answers": ["45.0"],
    "hint": "Use binary place values.",
    "image": "diagrams/binary.png",
    "difficulty": 2
  }
]
```

`alt_answers`, `hint`, `image` (path relative to the JSON file; copied into the app's
assets folder) and `difficulty` (1–5, default 1) are optional.

## Adding a question from Python

```python
question_repository.add_question(
    subject_name="Math", topic_name="Binary",
    question_text="Convert 101101 to decimal.", answer="45",
    alt_answers=["45.0"], hint="Use binary place values.",
    question_image="/path/to/question.png", difficulty=1,
)
```

## Data

`study_app.sqlite3` lives in the OS application-data directory (WAL mode, foreign keys,
indexes). Schema changes are applied as numbered migrations (`database/schema.py`).
All timestamps are stored in UTC and converted to local time when grouped by day.
Tables: `subjects`, `topics`, `questions`, `attempts`, `study_sessions`, `saved_questions`.

## Structure

- `core/` – theme, settings, icons, answer checking, session tracking, JSON import, paths
- `database/` – connection + migrations, schema and repositories
- `ui/` – pages, dialogs and widgets
- `tests/` – pytest suite (database logic and an offscreen UI smoke test)
=======
## Data storage

The app creates `study_app.sqlite3` in the operating system's application-data directory.
It uses SQLite WAL mode, foreign keys, indexes, transactions and a schema version.

Database tables:
- `subjects`
- `topics`
- `questions` (includes nullable `question_image` path)
- `attempts`
- `study_sessions`
- `saved_questions`

The nine configured subject names are inserted automatically. No sample questions or fake statistics are inserted. The dashboard displays zeros/empty states until real activity is recorded.

`question_image` stores a path to an image file. Keep image assets in an application-managed assets directory and store the path in the database; avoid storing large image blobs directly in SQLite.

## Add a question from Python

```python
question_id = question_repository.add_question(
    subject_name="Math",
    topic_name="Binary",
    question_text="Convert 101101 to decimal.",
    answer="45",
    hint="Use binary place values.",
    question_image="/path/to/question.png",  # optional
    difficulty=1,
)
```

## Structure

- `core/` — theme and settings
- `database/` — SQLite connection, schema and repositories
- `ui/` — reusable PySide6 screens and widgets
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f
