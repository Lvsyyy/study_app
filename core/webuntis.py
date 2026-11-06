"""Public WebUntis exam retrieval and local new-exam tracking."""
import hashlib
import json
from datetime import date, datetime, timedelta
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from PySide6.QtCore import QObject, QThread, Signal

from core.net import ssl_context
from core.paths import app_data_dir

SCHOOL = "bsz-roth"
CLASS_ID = 4215
ENTRIES_URL = f"https://{SCHOOL}.webuntis.com/WebUntis/api/rest/view/v1/timetable/entries"


def _fetch_chunk(start: date, end: date) -> dict:
    params = {
        "start": start.isoformat(),
        "end": end.isoformat(),
        "format": 2,
        "resourceType": "CLASS",
        "resources": CLASS_ID,
        "periodTypes": "",
        "timetableType": "STANDARD",
        "layout": "START_TIME",
    }
    request = Request(
        f"{ENTRIES_URL}?{urlencode(params)}",
        headers={
            "Accept": "application/json, text/plain, */*",
            "Anonymous-School": SCHOOL,
            "Referer": (
                f"https://{SCHOOL}.webuntis.com/timetable/class"
                f"?date={start.isoformat()}&entityId={CLASS_ID}"
            ),
            "User-Agent": "Mozilla/5.0",
            "X-WebUntis-Api-School-Year-Id": "28",
        },
    )
    try:
        with urlopen(request, timeout=20, context=ssl_context()) as response:
            return json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"WebUntis HTTP {exc.code}: {body[:300]}") from exc
    except URLError as exc:
        raise RuntimeError(f"Could not reach WebUntis: {exc.reason}") from exc


def _first_resource(value):
    """First entry of a WebUntis position list, or an empty dict."""
    return value[0] if isinstance(value, list) and value else {}


def _resource_name(value):
    if isinstance(value, dict):
        current = value.get("current") or value
        return current.get("longName") or current.get("shortName") or current.get("name") or ""
    return str(value) if value is not None else ""


def fetch_timetable(weeks: int = 6) -> tuple[list[dict], list[dict]]:
    start = date.today()
    end = start + timedelta(weeks=max(3, weeks))
    days = []
    chunk_start = start
    while chunk_start <= end:
        if QThread.currentThread().isInterruptionRequested():
            raise RuntimeError("WebUntis update cancelled")
        chunk_end = min(chunk_start + timedelta(days=4), end)
        payload = _fetch_chunk(chunk_start, chunk_end)
        days.extend(payload.get("days", []))
        chunk_start = chunk_end + timedelta(days=1)

    entries = {}
    exams = {}
    for day in days:
        for entry in day.get("gridEntries", []):
            duration = entry.get("duration") or {}
            start_value = duration.get("start")
            end_value = duration.get("end")
            if not start_value:
                continue
            subject_data = _first_resource(entry.get("position1"))
            subject = _resource_name(subject_data) or "Unspecified"
            subject_current = subject_data.get("current") or subject_data
            subject_short = subject_current.get("shortName") or ""
            room = _resource_name(_first_resource(entry.get("position3")))
            teacher = _resource_name(_first_resource(entry.get("position2")))
            description = entry.get("lessonInfo") or next(
                (
                    item.get("text", "")
                    for item in entry.get("texts", [])
                    if item.get("type") == "LESSON_INFO"
                ),
                "",
            )
            entry_type = entry.get("type") or "LESSON"
            identity = "|".join((start_value, end_value or "", subject, entry_type, description))
            entry_id = hashlib.sha256(identity.encode("utf-8")).hexdigest()[:20]
            item = {
                "id": entry_id, "start": start_value, "end": end_value or "",
                "subject": subject, "subject_short": subject_short,
                "room": room, "teacher": teacher,
                "description": description, "type": entry_type,
            }
            entries[entry_id] = item
            if entry_type == "EXAM":
                exams[entry_id] = item.copy()
    ordered_entries = sorted(entries.values(), key=lambda item: item["start"])
    ordered_exams = sorted(exams.values(), key=lambda item: item["start"])
    return ordered_entries, ordered_exams


def fetch_exams(weeks: int = 6) -> list[dict]:
    return fetch_timetable(weeks)[1]


class _ExamWorker(QThread):
    finished_with_result = Signal(list, list, str)

    def run(self):
        try:
            timetable, exams = fetch_timetable()
            self.finished_with_result.emit(exams, timetable, "")
        except Exception as error:
            self.finished_with_result.emit([], [], str(error))


class WebUntisExamManager(QObject):
    exams_updated = Signal(list, str)
    timetable_updated = Signal(list, str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.worker = None
        self.state_path = app_data_dir() / "webuntis_exams.json"
        self._new_until = {}
        self._known_ids = set()
        self._load_state()

    def _load_state(self):
        try:
            data = json.loads(self.state_path.read_text(encoding="utf-8"))
            self._new_until = data.get("new_until", {})
            self._known_ids = set(data.get("known_ids", []))
        except (OSError, ValueError, TypeError):
            self._new_until = {}
            self._known_ids = set()

    def _save_state(self):
        self.state_path.parent.mkdir(parents=True, exist_ok=True)
        self.state_path.write_text(
            json.dumps(
                {"new_until": self._new_until, "known_ids": sorted(self._known_ids)},
                indent=2,
            ),
            encoding="utf-8",
        )

    def shutdown(self):
        worker = self.worker
        if worker is None or not worker.isRunning():
            return
        # Ask the worker to stop between request chunks. A request already in
        # flight can take up to the HTTP timeout, but closing the app must not
        # wait for it, so fall back to terminating the thread.
        worker.requestInterruption()
        if worker.wait(3000):
            return
        worker.terminate()
        worker.wait(1000)

    def check(self):
        if self.worker is not None and self.worker.isRunning():
            return
        self.worker = _ExamWorker(self)
        self.worker.finished_with_result.connect(self._handle_results)
        self.worker.start()

    def _handle_results(self, exams, timetable, error):
        if error:
            self.exams_updated.emit([], error)
            self.timetable_updated.emit([], error)
            return

        now = datetime.now().astimezone()
        incoming_ids = {exam["id"] for exam in exams}
        for exam in exams:
            if exam["id"] not in self._known_ids:
                self._new_until[exam["id"]] = (now + timedelta(days=2)).isoformat()

        self._known_ids = incoming_ids
        # Expire badges after two days and discard exams no longer upcoming.
        self._new_until = {
            exam_id: expiry
            for exam_id, expiry in self._new_until.items()
            if exam_id in incoming_ids and datetime.fromisoformat(expiry) > now
        }
        self._save_state()

        for exam in exams:
            expiry = self._new_until.get(exam["id"])
            exam["is_new"] = bool(expiry and datetime.fromisoformat(expiry) > now)
            exam["date"] = datetime.fromisoformat(exam["start"]).astimezone().date().isoformat()
        self.exams_updated.emit(exams, "")
        self.timetable_updated.emit(timetable, "")
