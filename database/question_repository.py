
import json


def _decode_alternatives(row):
    raw = row["alt_answers"] if row and "alt_answers" in row.keys() else None

    if not raw:
        return []

    try:
        value = json.loads(raw)
    except json.JSONDecodeError:
        return []

    return [str(v) for v in value] if isinstance(value, list) else []


_QUESTION_SELECT = """SELECT q.*, t.name AS topic_name, s.name AS subject_name
                      FROM questions q
                      JOIN topics t ON t.id = q.topic_id
                      JOIN subjects s ON s.id = t.subject_id"""


class QuestionRepository:
    def __init__(self, db):
        self.db = db

    # -- subjects & topics ---------------------------------------------------

    def list_subjects(self):
        return self.db.fetch_all(
            "SELECT id, name, icon FROM subjects ORDER BY name"
        )

    def get_subject_id(self, subject_name):
        row = self.db.fetch_one(
            "SELECT id FROM subjects WHERE name = ?",
            (subject_name,),
        )
        return row["id"] if row else None

    def list_topics(self, subject_name):
        rows = self.db.fetch_all(
            """SELECT t.name
               FROM topics t
               JOIN subjects s ON s.id = t.subject_id
               WHERE s.name = ?
               ORDER BY t.name""",
            (subject_name,),
        )
        return [row["name"] for row in rows]

    def _ensure_topic(self, subject_name, topic_name):
        """Get or create a topic id. Does not commit; callers wrap it in a transaction."""
        subject_id = self.get_subject_id(subject_name)

        if subject_id is None:
            raise ValueError(f"Unknown subject: {subject_name}")

        self.db.execute(
            "INSERT OR IGNORE INTO topics(subject_id, name) VALUES (?, ?)",
            (subject_id, topic_name),
        )

        row = self.db.fetch_one(
            "SELECT id FROM topics WHERE subject_id = ? AND name = ?",
            (subject_id, topic_name),
        )

        return row["id"]

    def add_topic(self, subject_name, topic_name):
        with self.db.connection:
            return self._ensure_topic(subject_name, topic_name)

    def add_topics(self, subject_name, topic_names):
        """Create several topics in one transaction and return their ids in input order."""
        names = tuple(dict.fromkeys(
            str(name).strip() for name in topic_names if name is not None and str(name).strip()
        ))
        if not names:
            return []

        placeholders = ",".join("?" for _ in names)
        with self.db.connection:
            subject_id = self.get_subject_id(subject_name)
            if subject_id is None:
                raise ValueError(f"Unknown subject: {subject_name}")
            self.db.connection.executemany(
                "INSERT OR IGNORE INTO topics(subject_id, name) VALUES (?, ?)",
                ((subject_id, name) for name in names),
            )
            rows = self.db.fetch_all(
                f"SELECT name, id FROM topics WHERE subject_id = ? AND name IN ({placeholders})",
                (subject_id, *names),
            )

        ids = {row["name"]: row["id"] for row in rows}
        return [ids[name] for name in names]

    # -- questions -----------------------------------------------------------

    def _insert_question(
        self,
        subject_name,
        topic_name,
        question_text,
        answer,
        hint=None,
        question_image=None,
        difficulty=1,
        question_type="text",
        alt_answers=None,
        answer_template=None,
    ):
        topic_id = self._ensure_topic(subject_name, topic_name)

        cursor = self.db.execute(
            """INSERT INTO questions
               (topic_id, question_text, answer, hint, question_image,
                difficulty, question_type, alt_answers, answer_template)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                topic_id,
                question_text,
                answer,
                hint,
                question_image,
                difficulty,
                question_type,
                json.dumps(list(alt_answers)) if alt_answers else None,
                answer_template,
            ),
        )

        return cursor.lastrowid

    def add_question(
        self,
        subject_name,
        topic_name,
        question_text,
        answer,
        hint=None,
        question_image=None,
        difficulty=1,
        question_type="text",
        alt_answers=None,
        answer_template=None,
    ):
        with self.db.connection:
            return self._insert_question(
                subject_name,
                topic_name,
                question_text,
                answer,
                hint,
                question_image,
                difficulty,
                question_type,
                alt_answers,
                answer_template,
            )

    def add_questions(self, questions):
        """Insert many questions (dicts of add_question kwargs) in one transaction."""
        with self.db.connection:
            return [
                self._insert_question(**question)
                for question in questions
            ]

    def get_question(self, question_id):
        return self.db.fetch_one(
            f"{_QUESTION_SELECT} WHERE q.id = ?",
            (question_id,),
        )

    @staticmethod
    def alternatives(question) -> list[str]:
        return _decode_alternatives(question)

    def get_study_queue(self, subject_name):
        """Question ids for a practice round: never-seen first, then weakest, then oldest."""
        rows = self.db.fetch_all(
            """SELECT q.id
               FROM questions q
               JOIN topics t ON t.id = q.topic_id
               JOIN subjects s ON s.id = t.subject_id
               LEFT JOIN (
                   SELECT question_id,
                          COUNT(*) AS n,
                          SUM(is_correct) AS c,
                          MAX(created_at) AS last
                   FROM attempts
                   GROUP BY question_id
               ) a ON a.question_id = q.id
               WHERE s.name = ?
               ORDER BY
                   (a.n IS NOT NULL),
                   CASE
                       WHEN a.n IS NULL THEN 0
                       ELSE 1.0 * a.c / a.n
                   END ASC,
                   a.last ASC,
                   RANDOM()""",
            (subject_name,),
        )

        return [row["id"] for row in rows]

    def get_review_question(self, subject_name, exclude_id=None):
        """Choose one previously attempted question, strongly favoring weak answers."""
        row = self.db.fetch_one(
            """SELECT q.id
               FROM questions q
               JOIN topics t ON t.id = q.topic_id
               JOIN subjects s ON s.id = t.subject_id
               JOIN (
                   SELECT question_id,
                          COUNT(*) AS attempts,
                          SUM(CASE WHEN is_correct = 0 THEN 1 ELSE 0 END) AS wrong,
                          SUM(is_correct) AS correct,
                          MAX(created_at) AS last
                   FROM attempts
                   GROUP BY question_id
               ) a ON a.question_id = q.id
               WHERE s.name = ? AND (? IS NULL OR q.id != ?)
               ORDER BY
                   (1.0 * a.wrong / a.attempts) DESC,
                   a.wrong DESC,
                   (1.0 * a.correct / a.attempts) ASC,
                   a.last ASC,
                   RANDOM()
               LIMIT 1""",
            (subject_name, exclude_id, exclude_id),
        )
        return row["id"] if row else None

    def get_topic_study_queue(self, subject_name, topic_name):
        """Question ids for one topic, ordered by weakest performance first."""
        rows = self.db.fetch_all(
            """SELECT q.id
               FROM questions q
               JOIN topics t ON t.id = q.topic_id
               JOIN subjects s ON s.id = t.subject_id
               LEFT JOIN (
                   SELECT question_id,
                          COUNT(*) AS n,
                          SUM(is_correct) AS c,
                          MAX(created_at) AS last
                   FROM attempts
                   GROUP BY question_id
               ) a ON a.question_id = q.id
               WHERE s.name = ? AND t.name = ?
               ORDER BY
                   (a.n IS NOT NULL),
                   CASE
                       WHEN a.n IS NULL THEN 0
                       ELSE 1.0 * a.c / a.n
                   END ASC,
                   a.last ASC,
                   RANDOM()""",
            (subject_name, topic_name),
        )
        return [row["id"] for row in rows]

    def get_topics_study_queue(self, subject_name, topic_names):
        """Question ids for a selected set of topics, ordered by weakest performance first."""
        topic_names = tuple(topic_names)
        if not topic_names:
            return []

        placeholders = ",".join("?" for _ in topic_names)
        rows = self.db.fetch_all(
            f"""SELECT q.id
                FROM questions q
                JOIN topics t ON t.id = q.topic_id
                JOIN subjects s ON s.id = t.subject_id
                LEFT JOIN (
                    SELECT question_id,
                           COUNT(*) AS n,
                           SUM(is_correct) AS c,
                           MAX(created_at) AS last
                    FROM attempts
                    GROUP BY question_id
                ) a ON a.question_id = q.id
                WHERE s.name = ? AND t.name IN ({placeholders})
                ORDER BY
                    (a.n IS NOT NULL),
                    CASE
                        WHEN a.n IS NULL THEN 0
                        ELSE 1.0 * a.c / a.n
                    END ASC,
                    a.last ASC,
                    RANDOM()""",
            (subject_name, *topic_names),
        )
        return [row["id"] for row in rows]

    def get_next_question(self, subject_name, offset=0):
        return self.db.fetch_one(
            """SELECT q.*, t.name AS topic_name, s.name AS subject_name
               FROM questions q
               JOIN topics t ON t.id = q.topic_id
               JOIN subjects s ON s.id = t.subject_id
               WHERE s.name = ?
               ORDER BY q.id
               LIMIT 1 OFFSET ?""",
            (subject_name, offset),
        )

    def count_questions(self, subject_name=None):
        if subject_name:
            row = self.db.fetch_one(
                """SELECT COUNT(*) AS count
                   FROM questions q
                   JOIN topics t ON t.id = q.topic_id
                   JOIN subjects s ON s.id = t.subject_id
                   WHERE s.name = ?""",
                (subject_name,),
            )
        else:
            row = self.db.fetch_one(
                "SELECT COUNT(*) AS count FROM questions"
            )

        return row["count"]

    # -- saved ---------------------------------------------------------------

    def set_saved(self, question_id, saved=True):
        with self.db.connection:
            if saved:
                self.db.execute(
                    "INSERT OR IGNORE INTO saved_questions(question_id) VALUES (?)",
                    (question_id,),
                )
            else:
                self.db.execute(
                    "DELETE FROM saved_questions WHERE question_id = ?",
                    (question_id,),
                )

    def is_saved(self, question_id):
        return self.db.fetch_one(
            "SELECT 1 FROM saved_questions WHERE question_id = ?",
            (question_id,),
        ) is not None

    def list_saved(self):
        return self.db.fetch_all(
            f"""{_QUESTION_SELECT}
                JOIN saved_questions sq ON sq.question_id = q.id
                ORDER BY sq.saved_at DESC, q.id DESC"""
        )