class StatisticsRepository:
    def __init__(self, db):
        self.db = db

    def dashboard_totals(self):
        attempts = self.db.fetch_one(
            """SELECT COUNT(*) AS total,
                      COALESCE(SUM(is_correct), 0) AS correct,
                      COUNT(*) - COALESCE(SUM(is_correct), 0) AS wrong
               FROM attempts"""
        )
        sessions = self.db.fetch_one(
            "SELECT COUNT(*) AS count FROM study_sessions WHERE duration > 0"
        )
        return {
            "total": attempts["total"],
            "correct": attempts["correct"],
            "wrong": attempts["wrong"],
            "sessions": sessions["count"],
        }

    def current_streak(self):
        rows = self.db.fetch_all(
            """SELECT DISTINCT date(started_at) AS day
               FROM study_sessions WHERE duration > 0
               ORDER BY day DESC"""
        )
        if not rows:
            return 0
        from datetime import date, timedelta
        days = {date.fromisoformat(row["day"]) for row in rows}
        today = date.today()
        cursor = today if today in days else today - timedelta(days=1)
        streak = 0
        while cursor in days:
            streak += 1
            cursor -= timedelta(days=1)
        return streak

    def monthly_activity(self, year, month):
        return self.db.fetch_all(
            """SELECT date(started_at) AS day,
                      SUM(duration) AS duration,
                      SUM(questions_completed) AS questions
               FROM study_sessions
               WHERE strftime('%Y', started_at)=?
                 AND strftime('%m', started_at)=?
               GROUP BY date(started_at)""",
            (f"{year:04d}", f"{month:02d}"),
        )
