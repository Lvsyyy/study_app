from datetime import date, timedelta

_STUDY_DAYS_SQL = """
    SELECT date(created_at, 'localtime') AS day FROM attempts
    UNION
    SELECT date(started_at, 'localtime') AS day
    FROM study_sessions
    WHERE duration >= 60 OR questions_completed > 0
"""


class StatisticsRepository:
    def __init__(self, db):
        self.db = db

    def study_totals(self):
        row = self.db.fetch_one(
            """SELECT COUNT(*) AS sessions,
                      COALESCE(SUM(duration), 0) AS seconds
               FROM study_sessions
               WHERE duration > 0 OR questions_completed > 0"""
        )
        return {"sessions": row["sessions"], "seconds": row["seconds"]}

    def _study_days(self):
        return {
            date.fromisoformat(row["day"])
            for row in self.db.fetch_all(_STUDY_DAYS_SQL)
            if row["day"]
        }

    def current_streak(self):
        days = self._study_days()
        if not days:
            return 0
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
        key = f"{year:04d}-{month:02d}"
        return self.db.fetch_all(
            """WITH session_days AS (
                   SELECT date(started_at, 'localtime') AS day,
                          SUM(duration) AS duration,
                          SUM(questions_completed) AS questions
                   FROM study_sessions
                   WHERE (duration >= 60 OR questions_completed > 0)
                     AND strftime('%Y-%m', started_at, 'localtime') = ?
                   GROUP BY day
               ),
               attempt_days AS (
                   SELECT date(created_at, 'localtime') AS day,
                          COUNT(*) AS questions
                   FROM attempts
                   WHERE strftime('%Y-%m', created_at, 'localtime') = ?
                   GROUP BY day
               ),
               active_days AS (
                   SELECT day FROM session_days
                   UNION
                   SELECT day FROM attempt_days
               )
               SELECT active_days.day,
                      COALESCE(session_days.duration, 0) AS duration,
                      MAX(COALESCE(session_days.questions, 0),
                          COALESCE(attempt_days.questions, 0)) AS questions
               FROM active_days
               LEFT JOIN session_days USING (day)
               LEFT JOIN attempt_days USING (day)
               ORDER BY active_days.day""",
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
               GROUP BY s.id
               ORDER BY s.name"""
        )
