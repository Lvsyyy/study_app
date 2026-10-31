class AttemptRepository:
    def __init__(self, db):
        self.db = db

    def record(self, question_id, user_answer, is_correct, time_taken=None):
        with self.db.connection:
            cursor = self.db.execute(
                """INSERT INTO attempts
                   (question_id, user_answer, is_correct, time_taken)
                   VALUES (?, ?, ?, ?)""",
                (question_id, user_answer, int(is_correct),
                 None if time_taken is None else round(float(time_taken), 2)),
                (question_id, user_answer, int(is_correct), time_taken),
            )
        return cursor.lastrowid

    def totals(self):
        """Overall counts plus accuracy (None when there are no attempts)."""
        row = self.db.fetch_one(
            """SELECT COUNT(*) AS total,
                      COALESCE(SUM(is_correct), 0) AS correct,
                      AVG(time_taken) AS avg_time
               FROM attempts"""
        )
        total, correct = row["total"], row["correct"]
        return {
            "total": total,
            "correct": correct,
            "wrong": total - correct,
            "accuracy": 100.0 * correct / total if total else None,
            "avg_time": row["avg_time"],
        }
        return self.db.fetch_one(
            """SELECT COUNT(*) AS total,
                      COALESCE(SUM(is_correct), 0) AS correct,
                      COUNT(*) - COALESCE(SUM(is_correct), 0) AS wrong
               FROM attempts"""
        )

    def daily_activity(self, year, month):
        return self.db.fetch_all(
            """SELECT date(created_at) AS day,
                      COUNT(*) AS questions,
                      COALESCE(SUM(time_taken), 0) AS seconds
               FROM attempts
               WHERE strftime('%Y', created_at)=?
                 AND strftime('%m', created_at)=?
               GROUP BY date(created_at)""",
            (f"{year:04d}", f"{month:02d}"),
        )

    def weak_points(self, limit=5):
        return self.db.fetch_all(
            """SELECT t.name AS topic_name, s.name AS subject_name,
                      COUNT(a.id) AS attempts,
                      CAST(ROUND(100.0 * SUM(a.is_correct) / COUNT(a.id)) AS INTEGER) AS accuracy
                      ROUND(100.0 * SUM(a.is_correct) / COUNT(a.id)) AS accuracy
               FROM attempts a
               JOIN questions q ON q.id=a.question_id
               JOIN topics t ON t.id=q.topic_id
               JOIN subjects s ON s.id=t.subject_id
               GROUP BY t.id
               HAVING COUNT(a.id) >= 2
               ORDER BY accuracy ASC, attempts DESC
               LIMIT ?""",
            (limit,),
        )

    def topic_accuracy(self, topic_id):
        row = self.db.fetch_one(
            """SELECT COUNT(a.id) AS attempts,
                      CAST(ROUND(100.0 * SUM(a.is_correct) / COUNT(a.id)) AS INTEGER) AS accuracy
               FROM attempts a JOIN questions q ON q.id=a.question_id
               WHERE q.topic_id=?""",
            (topic_id,),
        )
        return row if row and row["attempts"] else None
