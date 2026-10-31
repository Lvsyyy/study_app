<<<<<<< HEAD
from .database import utc_now
=======
from datetime import datetime
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f


class SessionRepository:
    def __init__(self, db):
        self.db = db

    def start(self):
<<<<<<< HEAD
        with self.db.connection:
            cursor = self.db.execute(
                "INSERT INTO study_sessions(started_at) VALUES (?)", (utc_now(),)
            )
        return cursor.lastrowid

    def update(self, session_id, duration_seconds, questions_completed):
        """Persist progress without ending the session (called periodically)."""
        with self.db.connection:
            self.db.execute(
                "UPDATE study_sessions SET duration=?, questions_completed=? WHERE id=?",
                (max(0, int(duration_seconds)), max(0, int(questions_completed)), session_id),
            )

    def finish(self, session_id, duration_seconds, questions_completed):
=======
        started = datetime.now().astimezone().isoformat(timespec="seconds")
        with self.db.connection:
            cursor = self.db.execute(
                "INSERT INTO study_sessions(started_at) VALUES (?)", (started,)
            )
        return cursor.lastrowid

    def finish(self, session_id, duration_seconds, questions_completed):
        ended = datetime.now().astimezone().isoformat(timespec="seconds")
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f
        with self.db.connection:
            self.db.execute(
                """UPDATE study_sessions
                   SET ended_at=?, duration=?, questions_completed=?
                   WHERE id=?""",
<<<<<<< HEAD
                (utc_now(), max(0, int(duration_seconds)),
=======
                (ended, max(0, int(duration_seconds)),
>>>>>>> 4bb8daa84d7e37533766a7591af47a7d1b8d368f
                 max(0, int(questions_completed)), session_id),
            )
