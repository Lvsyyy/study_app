import json
import sqlite3
from datetime import UTC, datetime, timedelta

import pytest

from core.importer import import_file, load_questions
from database.attempt_repository import AttemptRepository
from database.database import Database
from database.question_repository import QuestionRepository
from database.schema import DEFAULT_SUBJECTS, SCHEMA, SCHEMA_VERSION
from database.session_repository import SessionRepository
from database.statistics_repository import StatisticsRepository


@pytest.fixture
def db():
    database = Database(":memory:")
    yield database
    database.close()


@pytest.fixture
def repos(db):
    return (QuestionRepository(db), AttemptRepository(db),
            StatisticsRepository(db), SessionRepository(db))


def add(questions, n=1, subject="Math", topic="Binary"):
    return [questions.add_question(subject, topic, f"Q{i}", str(i)) for i in range(n)]


def stamp(days_ago=0, hours_ago=0):
    moment = datetime.now(UTC) - timedelta(days=days_ago, hours=hours_ago)
    return moment.strftime("%Y-%m-%d %H:%M:%S")


def test_fresh_database_is_current_version_and_seeded(db):
    assert db.fetch_one("PRAGMA user_version")[0] == SCHEMA_VERSION
    assert {r["name"] for r in db.fetch_all("SELECT name FROM subjects")} == set(DEFAULT_SUBJECTS)


def test_migrates_a_version_1_database(tmp_path):
    path = tmp_path / "old.sqlite3"
    old = sqlite3.connect(path)
    old.executescript(SCHEMA)
    old.execute("PRAGMA user_version = 1")
    old.commit()
    old.close()
    migrated = Database(path)
    columns = [r[1] for r in migrated.fetch_all("PRAGMA table_info(questions)")]
    assert "alt_answers" in columns
    assert migrated.fetch_one("PRAGMA user_version")[0] == SCHEMA_VERSION
    migrated.close()


def test_rejects_newer_database(tmp_path):
    path = tmp_path / "new.sqlite3"
    conn = sqlite3.connect(path)
    conn.execute(f"PRAGMA user_version = {SCHEMA_VERSION + 1}")
    conn.commit()
    conn.close()
    with pytest.raises(RuntimeError):
        Database(path)


def test_alternatives_round_trip(repos):
    questions = repos[0]
    qid = questions.add_question("Math", "T", "Q", "45", alt_answers=["45.0", "forty-five"])
    assert questions.alternatives(questions.get_question(qid)) == ["45.0", "forty-five"]


def test_unknown_subject_rejected_and_nothing_written(repos):
    questions = repos[0]
    with pytest.raises(ValueError):
        questions.add_question("Nope", "T", "Q", "A")
    assert questions.count_questions() == 0


def test_study_queue_unseen_first_then_weakest(repos):
    questions, attempts, *_ = repos
    a, b, c = add(questions, 3)
    attempts.record(a, "x", True)    # 100%
    attempts.record(b, "x", False)   # 0%
    assert questions.get_study_queue("Math") == [c, b, a]


def test_attempt_totals_and_time(repos):
    questions, attempts, *_ = repos
    (qid,) = add(questions)
    attempts.record(qid, "a", True, 4.0)
    attempts.record(qid, "b", False, 8.0)
    totals = attempts.totals()
    assert (totals["total"], totals["correct"], totals["wrong"]) == (2, 1, 1)
    assert totals["accuracy"] == 50.0 and totals["avg_time"] == 6.0
    assert attempts.totals()["accuracy"] is not None


def test_empty_totals_have_no_accuracy(repos):
    assert repos[1].totals()["accuracy"] is None


def test_weak_points_accuracy_is_integer(repos):
    questions, attempts, *_ = repos
    (qid,) = add(questions)
    for correct in (True, False, False):
        attempts.record(qid, "x", correct)
    (row,) = attempts.weak_points()
    assert isinstance(row["accuracy"], int) and row["accuracy"] == 33


def test_streak_counts_consecutive_local_days(db, repos):
    questions, attempts, stats, _ = repos
    (qid,) = add(questions)
    for days in (0, 1, 2, 5):
        db.execute("INSERT INTO attempts(question_id,user_answer,is_correct,created_at) "
                   "VALUES (?,?,?,?)", (qid, "x", 1, stamp(days)))
    db.connection.commit()
    assert stats.current_streak() == 3
    assert stats.longest_streak() == 3


def test_streak_survives_missing_today(db, repos):
    questions, _, stats, _ = repos
    (qid,) = add(questions)
    for days in (1, 2):
        db.execute("INSERT INTO attempts(question_id,user_answer,is_correct,created_at) "
                   "VALUES (?,?,?,?)", (qid, "x", 1, stamp(days)))
    db.connection.commit()
    assert stats.current_streak() == 2


def test_session_lifecycle_and_monthly_activity(repos):
    questions, attempts, stats, sessions = repos
    (qid,) = add(questions)
    attempts.record(qid, "x", True, 3)
    sid = sessions.start()
    sessions.update(sid, 125, 1)
    assert stats.study_totals() == {"sessions": 1, "seconds": 125}
    sessions.finish(sid, 130, 1)
    now = datetime.now()
    rows = stats.monthly_activity(now.year, now.month)
    assert len(rows) == 1 and rows[0]["duration"] == 130 and rows[0]["questions"] == 1
    assert stats.current_streak() == 1


def test_subject_stats(repos):
    questions, attempts, stats, _ = repos
    (qid,) = add(questions)
    attempts.record(qid, "x", True)
    math = next(s for s in stats.subject_stats() if s["name"] == "Math")
    assert (math["questions"], math["attempts"], math["correct"]) == (1, 1, 1)


def test_saved_questions(repos):
    questions = repos[0]
    a, b = add(questions, 2)
    questions.set_saved(a)
    questions.set_saved(a)  # idempotent
    questions.set_saved(b)
    assert questions.is_saved(a)
    assert {r["id"] for r in questions.list_saved()} == {a, b}
    questions.set_saved(a, False)
    assert not questions.is_saved(a)


def test_import_is_all_or_nothing(tmp_path, repos):
    questions = repos[0]
    good = {"subject": "Math", "topic": "T", "question": "Q", "answer": "A"}
    bad = {"subject": "Nope", "topic": "T", "question": "Q", "answer": "A"}
    path = tmp_path / "q.json"
    path.write_text(json.dumps([good, bad]))
    count, errors = import_file(path, questions)
    assert count == 0 and errors and questions.count_questions() == 0
    path.write_text(json.dumps([good, {**good, "alt_answers": ["B"], "difficulty": 3}]))
    count, errors = import_file(path, questions)
    assert count == 2 and not errors and questions.count_questions() == 2


def test_import_validation(tmp_path):
    path = tmp_path / "q.json"
    path.write_text(json.dumps([{"subject": "Math", "topic": "T", "question": "Q", "answer": "A",
                                  "difficulty": 9}]))
    _, errors = load_questions(path, {"Math"})
    assert errors and "difficulty" in errors[0]
    path.write_text("not json")
    assert load_questions(path, {"Math"})[1]
