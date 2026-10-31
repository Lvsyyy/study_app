class QuestionRepository:
    def __init__(self, db):
        self.db = db

    def list_subjects(self):
        return self.db.fetch_all(
            "SELECT id, name, icon FROM subjects ORDER BY name"
        )

    def get_subject_id(self, subject_name):
        row = self.db.fetch_one(
            "SELECT id FROM subjects WHERE name = ?", (subject_name,)
        )
        return row["id"] if row else None

    def add_topic(self, subject_name, topic_name):
        subject_id = self.get_subject_id(subject_name)
        if subject_id is None:
            raise ValueError(f"Unknown subject: {subject_name}")
        with self.db.connection:
            self.db.execute(
                "INSERT OR IGNORE INTO topics(subject_id, name) VALUES (?, ?)",
                (subject_id, topic_name),
            )
            row = self.db.fetch_one(
                "SELECT id FROM topics WHERE subject_id = ? AND name = ?",
                (subject_id, topic_name),
            )
        return row["id"]

    def add_question(
        self, subject_name, topic_name, question_text, answer,
        hint=None, question_image=None, difficulty=1, question_type="text"
    ):
        topic_id = self.add_topic(subject_name, topic_name)
        with self.db.connection:
            cursor = self.db.execute(
                """INSERT INTO questions
                   (topic_id, question_text, answer, hint, question_image,
                    difficulty, question_type)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (topic_id, question_text, answer, hint, question_image,
                 difficulty, question_type),
            )
        return cursor.lastrowid

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
                """SELECT COUNT(*) AS count FROM questions q
                   JOIN topics t ON t.id=q.topic_id
                   JOIN subjects s ON s.id=t.subject_id
                   WHERE s.name=?""", (subject_name,)
            )
        else:
            row = self.db.fetch_one("SELECT COUNT(*) AS count FROM questions")
        return row["count"]

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

    def list_saved(self):
        return self.db.fetch_all(
            """SELECT q.*, t.name AS topic_name, s.name AS subject_name
               FROM saved_questions sq
               JOIN questions q ON q.id=sq.question_id
               JOIN topics t ON t.id=q.topic_id
               JOIN subjects s ON s.id=t.subject_id
               ORDER BY sq.saved_at DESC"""
        )
