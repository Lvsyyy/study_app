import json
from urllib.error import HTTPError, URLError

import pytest

from core import webuntis


class FakeResponse:
    def __init__(self, payload):
        self.payload = payload

    def read(self):
        return json.dumps(self.payload).encode("utf-8")

    def __enter__(self):
        return self

    def __exit__(self, *exc_info):
        return False


def day(date_value, *types):
    return {
        "date": date_value,
        "gridEntries": [
            {
                "type": entry_type,
                "duration": {"start": f"{date_value}T07:50", "end": f"{date_value}T08:35"},
                "lessonInfo": "Schulaufgabe" if entry_type == "EXAM" else None,
                "position1": [
                    {
                        "current": {
                            "shortName": "NWT",
                            "longName": "Netzwerktechnik",
                            "type": "SUBJECT",
                        }
                    }
                ],
                "position2": [{"current": {"longName": "Frau Muster"}}],
                "position3": [{"current": {"longName": "A1.12"}}],
            }
            for entry_type in types
        ],
    }


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr(webuntis.time, "sleep", lambda _seconds: None)


def test_edge_page_becomes_a_short_reason():
    body = "<html><head><title>bsz-roth.webuntis.com</title></head><body>Error 1004: Host Not Configured</body></html>"

    reason = webuntis._http_reason(409, body)

    assert "1004" in reason
    assert "409" in reason
    assert "<" not in reason and "html" not in reason.lower()


def test_plain_http_error_keeps_its_message():
    assert webuntis._http_reason(403, '{"error":"forbidden"}') == (
        'WebUntis HTTP 403: {"error":"forbidden"}'
    )


def test_reset_connection_is_retried(monkeypatch):
    attempts = []
    payload = {"days": [day("2026-11-23", "NORMAL_TEACHING_PERIOD")]}

    def fake_urlopen(*_args, **_kwargs):
        attempts.append(1)
        if len(attempts) == 1:
            raise ConnectionResetError(104, "Connection reset by peer")
        return FakeResponse(payload)

    monkeypatch.setattr(webuntis, "urlopen", fake_urlopen)

    result = webuntis._fetch_entries(webuntis.date(2026, 11, 23), webuntis.date(2026, 11, 27))

    assert result == payload
    assert len(attempts) == 2


def test_retryable_status_is_retried_then_succeeds(monkeypatch):
    attempts = []

    def fake_urlopen(*_args, **_kwargs):
        attempts.append(1)
        if len(attempts) < 3:
            raise HTTPError("url", 409, "Conflict", {}, None)
        return FakeResponse({"days": []})

    monkeypatch.setattr(webuntis, "urlopen", fake_urlopen)

    assert webuntis._fetch_entries(webuntis.date(2026, 11, 23), webuntis.date(2026, 11, 27)) == {
        "days": []
    }
    assert len(attempts) == 3


def test_giving_up_reports_the_edge_code(monkeypatch):
    class Page:
        def read(self):
            return b"<html>Error 1004: Host Not Configured to Serve Web Traffic</html>"

        def close(self):
            pass

    def fake_urlopen(*_args, **_kwargs):
        raise HTTPError("url", 409, "Conflict", {}, Page())

    monkeypatch.setattr(webuntis, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError) as error:
        webuntis.fetch_timetable()

    assert "1004" in str(error.value)


def test_client_errors_are_not_retried(monkeypatch):
    attempts = []

    def fake_urlopen(*_args, **_kwargs):
        attempts.append(1)
        raise HTTPError("url", 403, "Forbidden", {}, None)

    monkeypatch.setattr(webuntis, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="403"):
        webuntis._fetch_entries(webuntis.date(2026, 11, 23), webuntis.date(2026, 11, 27))

    assert len(attempts) == 1


def test_unreachable_host_is_reported(monkeypatch):
    def fake_urlopen(*_args, **_kwargs):
        raise URLError("Name or service not known")

    monkeypatch.setattr(webuntis, "urlopen", fake_urlopen)

    with pytest.raises(RuntimeError, match="Could not reach WebUntis"):
        webuntis._fetch_entries(webuntis.date(2026, 11, 23), webuntis.date(2026, 11, 27))


def test_one_request_covers_the_whole_window(monkeypatch):
    calls = []

    def fake_fetch(start, end):
        calls.append((start, end))
        return {"days": [day("2026-11-23", "NORMAL_TEACHING_PERIOD", "EXAM")]}

    monkeypatch.setattr(webuntis, "_fetch_entries", fake_fetch)

    entries, exams = webuntis.fetch_timetable(weeks=6)

    assert len(calls) == 1
    assert (calls[0][1] - calls[0][0]).days == 42
    assert [entry["type"] for entry in entries] == ["NORMAL_TEACHING_PERIOD", "EXAM"]
    assert len(exams) == 1
    assert exams[0]["subject"] == "Netzwerktechnik"
    assert exams[0]["room"] == "A1.12"
    assert exams[0]["teacher"] == "Frau Muster"
    assert exams[0]["description"] == "Schulaufgabe"
