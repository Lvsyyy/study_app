# Study App GUI

A modular PySide6 study-app starter with a local SQLite database.

## Run

```bash
python -m venv .venv
source .venv/bin/activate          # Linux
# .venv\\Scripts\\activate         # Windows
pip install -r requirements.txt
python main.py
```

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
