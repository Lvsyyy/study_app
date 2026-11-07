class InfoRepository:
    """Reads the reference information grouped by subject and topic."""

    def __init__(self, db):
        self.db = db

    def list_subjects(self):
        """Every subject, including the ones that have no information yet."""
        return self.db.fetch_all(
            """SELECT s.name AS name, COUNT(i.id) AS sections
               FROM subjects s
               LEFT JOIN topics t ON t.subject_id = s.id
               LEFT JOIN infos i ON i.topic_id = t.id
               GROUP BY s.id
               ORDER BY s.name"""
        )

    def list_topics(self, subject):
        return self.db.fetch_all(
            """SELECT t.name AS name, COUNT(i.id) AS sections
               FROM topics t
               JOIN subjects s ON s.id = t.subject_id
               LEFT JOIN infos i ON i.topic_id = t.id
               WHERE s.name = ?
               GROUP BY t.id
               ORDER BY t.id""",
            (subject,),
        )

    def topic_sections(self, subject, topic):
        return self.db.fetch_all(
            """SELECT i.heading AS heading, i.body AS body
               FROM infos i
               JOIN topics t ON t.id = i.topic_id
               JOIN subjects s ON s.id = t.subject_id
               WHERE s.name = ? AND t.name = ?
               ORDER BY i.position, i.id""",
            (subject, topic),
        )

    def all_sections(self):
        return self.db.fetch_all(
            """SELECT s.name AS subject, t.name AS topic,
                      i.heading AS heading, i.body AS body
               FROM infos i
               JOIN topics t ON t.id = i.topic_id
               JOIN subjects s ON s.id = t.subject_id
               ORDER BY s.name, t.id, i.position, i.id"""
        )

    def section_count(self):
        return self.db.fetch_one("SELECT COUNT(*) AS total FROM infos")["total"]
