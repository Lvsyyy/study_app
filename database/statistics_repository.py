from datetime import date, timedelta

# Days on which the user studied: any answered question, or a session of 1+ minute.
_STUDY_DAYS_SQL = """
    SELECT date(created_at, 'localtime') AS day FROM attempts
    UNION
    SELECT date(started_at, 'localtime') FROM study_sessions WHERE duration >= 60
"""


class StatisticsRepository:
    def __init__(self, db):
        self.db = db

    def study_totals(self):
        row = self.db.fetch_one(
            "SELECT COUNT(*) AS sessions, COALESCE(SUM(duration), 0) AS seconds "
            "FROM study_sessions WHERE duration > 0"
        )
        return {"sessions": row["sessions"], "seconds": row["seconds"]}

    def _study_days(self):
        return {date.fromisoformat(r["day"]) for r in self.db.fetch_all(_STUDY_DAYS_SQL)}

    def current_streak(self):
        days = self._study_days()
        today = date.today()
        cursor = today if today in days else today - timedelta(days=1)
        streak = 0
        while cursor in days:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    def longest_streak(self):
        best = run = 0
        previous = None
        for day in sorted(self._study_days()):
            run = run + 1 if previous and day - previous == timedelta(days=1) else 1
            best = max(best, run)
            previous = day
        return best

    def monthly_activity(self, year, month):
        """Per local day: study seconds (sessions) and answered questions (attempts)."""
        key = f"{year:04d}-{month:02d}"
        return self.db.fetch_all(
            """SELECT day, SUM(duration) AS duration, SUM(questions) AS questions FROM (
                   SELECT date(started_at, 'localtime') AS day, duration, 0 AS questions
                   FROM study_sessions
                   WHERE strftime('%Y-%m', started_at, 'localtime') = ?
                   UNION ALL
                   SELECT date(created_at, 'localtime'), 0, 1
                   FROM attempts
                   WHERE strftime('%Y-%m', created_at, 'localtime') = ?
               ) GROUP BY day""",
            (key, key),
        )

    def subject_stats(self):
        return self.db.fetch_all(
            """SELECT s.name AS name,
                      COUNT(DISTINCT q.id) AS questions,
                      COUNT(a.id) AS attempts,
                      COALESCE(SUM(a.is_correct), 0) AS correct
               FROM subjects s
               LEFT JOIN topics t ON t.subject_id = s.id
               LEFT JOIN questions q ON q.topic_id = t.id
               LEFT JOIN attempts a ON a.question_id = q.id
               GROUP BY s.id ORDER BY s.id"""
        )
