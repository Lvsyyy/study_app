"""Source updater: periodic update checks plus the one-click install flow."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from urllib.request import Request, urlopen

from PySide6.QtCore import QObject, QThread, QTimer, Signal
from PySide6.QtWidgets import QApplication, QMessageBox

from core.i18n import tr
from core.net import ssl_context
from core.paths import app_data_dir

API_URL = "https://api.github.com/repos/Lvsyyy/study_app/commits/main"
ARCHIVE_URL = "https://github.com/Lvsyyy/study_app/archive/{commit}.zip"
CHECK_INTERVAL_MS = 30 * 60 * 1000
HEADERS = {"User-Agent": "Study-App-Updater"}


def _open_url(request, timeout):
    return urlopen(request, timeout=timeout, context=ssl_context())


HELPER = r"""
import json
import os
import shutil
import subprocess
import sys
import time
import zipfile
from pathlib import Path

archive, app_root, parent_pid, launch_command, commit = sys.argv[1:]
archive = Path(archive)
app_root = Path(app_root)
launch_command = json.loads(launch_command)

# Wait until the running app has closed before replacing its files.
for _ in range(300):
    try:
        os.kill(int(parent_pid), 0)
    except OSError:
        break
    time.sleep(0.1)
else:
    raise SystemExit("The app did not close; update cancelled.")

with zipfile.ZipFile(archive) as bundle:
    entries = bundle.infolist()
    root_name = entries[0].filename.split("/", 1)[0]
    staging = archive.parent / "extracted"
    for entry in entries:
        target = (staging / entry.filename).resolve()
        if not target.is_relative_to(staging.resolve()):
            raise RuntimeError("Unsafe path in update archive.")
    bundle.extractall(staging)

source = staging / root_name
excluded = {".git", ".venv", "__pycache__"}
for current, dirs, files in os.walk(source):
    dirs[:] = [name for name in dirs if name not in excluded]
    relative = Path(current).relative_to(source)
    destination = app_root / relative
    destination.mkdir(parents=True, exist_ok=True)
    for filename in files:
        if filename.endswith(".pyc"):
            continue
        shutil.copy2(Path(current) / filename, destination / filename)

(app_root / ".study_app_commit").write_text(commit, encoding="utf-8")
subprocess.Popen(launch_command, cwd=app_root)
"""


def project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def local_commit():
    """Commit of the running copy: the update marker, else the git checkout."""
    marker = project_root() / ".study_app_commit"
    try:
        if marker.is_file():
            return marker.read_text(encoding="utf-8").strip() or None
    except OSError:
        return None
    try:
        result = subprocess.run(
            ["git", "-C", str(project_root()), "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            timeout=10,
            check=True,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    return result.stdout.strip() or None


def fetch_remote_commit(timeout=20):
    request = Request(API_URL, headers=HEADERS)
    with _open_url(request, timeout=timeout) as response:
        return json.loads(response.read())["sha"]


def _state_path() -> Path:
    return app_data_dir() / "update_state.json"


def _known_commit():
    try:
        data = json.loads(_state_path().read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    return data.get("known_commit") if isinstance(data, dict) else None


def _remember_commit(commit):
    try:
        _state_path().write_text(
            json.dumps({"known_commit": commit}), encoding="utf-8"
        )
    except OSError:
        pass


class UpdateWorker(QThread):
    """Downloads the source archive, optionally for an already-known commit."""

    completed = Signal(str, str, str)

    def __init__(self, parent=None, commit=None):
        super().__init__(parent)
        self._commit = commit

    def run(self):
        try:
            commit = self._commit or fetch_remote_commit()
            if local_commit() == commit:
                self.completed.emit("", "", "UP_TO_DATE")
                return

            folder = Path(tempfile.mkdtemp(prefix="study-app-update-"))
            archive = folder / "update.zip"
            request = Request(ARCHIVE_URL.format(commit=commit), headers=HEADERS)
            with _open_url(request, timeout=60) as response, archive.open("wb") as output:
                shutil.copyfileobj(response, output)
            self.completed.emit(str(archive), commit, "")
        except Exception as error:
            self.completed.emit("", "", str(error))


class _CheckWorker(QThread):
    checked = Signal(str, str)

    def run(self):
        try:
            self.checked.emit(fetch_remote_commit(), "")
        except Exception as error:
            self.checked.emit("", str(error))


class UpdateChecker(QObject):
    """Looks for a newer commit on launch and then every CHECK_INTERVAL_MS."""

    update_available = Signal(str)

    def __init__(self, parent=None, interval_ms=CHECK_INTERVAL_MS):
        super().__init__(parent)
        self._worker = None
        self._timer = QTimer(self)
        self._timer.setInterval(interval_ms)
        self._timer.timeout.connect(self.check_now)

    def start(self):
        self.check_now()
        self._timer.start()

    def stop(self):
        self._timer.stop()
        worker = self._worker
        self._worker = None
        if worker is not None and worker.isRunning():
            worker.wait(5000)

    def check_now(self):
        if self._worker is not None and self._worker.isRunning():
            return
        self._worker = _CheckWorker(self)
        self._worker.checked.connect(self._handle)
        self._worker.start()

    def _handle(self, commit, error):
        if error or not commit:
            return
        known = local_commit() or _known_commit()
        if not known:
            # A fresh ZIP carries no version marker, so adopt what we see first
            # instead of announcing the version the app was downloaded with.
            _remember_commit(commit)
            return
        if commit != known:
            self.update_available.emit(commit)


def apply_archive(window, archive, commit):
    """Start the detached helper that replaces files and restarts the app.

    Returns an error message, or None once the helper was launched.
    """
    launch_script = Path(sys.argv[0]).resolve()
    launch_command = [sys.executable, str(launch_script), *sys.argv[1:]]
    folder = Path(archive).parent
    helper = folder / "apply_update.py"
    try:
        helper.write_text(HELPER, encoding="utf-8")
    except OSError as error:
        return str(error)

    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    try:
        subprocess.Popen(
            [
                sys.executable,
                str(helper),
                archive,
                str(project_root()),
                str(os.getpid()),
                json.dumps(launch_command),
                commit,
            ],
            cwd=folder,
            creationflags=flags,
            start_new_session=(sys.platform == "darwin"),
        )
    except Exception as error:
        return str(error)

    _remember_commit(commit)
    QMessageBox.information(
        window, tr("Update ready"), tr("The app will close, update, and restart.")
    )
    return None


def start_update(dialog):
    """Manual update entry point used by the settings dialog."""
    answer = QMessageBox.question(
        dialog,
        tr("Update Study App"),
        tr(
            "Check GitHub for updates and install the latest version? "
            "Your progress and settings will be kept."
        ),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes,
    )
    if answer != QMessageBox.StandardButton.Yes:
        return

    dialog.update_button.setEnabled(False)
    dialog.update_button.setText(tr("Checking…"))
    dialog.update_worker = UpdateWorker(dialog)
    dialog.update_worker.completed.connect(
        lambda archive, commit, error: _finish_update(dialog, archive, commit, error)
    )
    dialog.update_worker.start()


def _reset_update_button(dialog):
    dialog.update_button.setEnabled(True)
    dialog.update_button.setText(tr("Check for updates"))


def _report_failure(window, error):
    QMessageBox.critical(
        window,
        tr("Update failed"),
        tr("Could not check for or download the update:\n{error}", error=error),
    )


def _report_launch_failure(window, error):
    QMessageBox.critical(
        window,
        tr("Update failed"),
        tr("Could not start the updater:\n{error}", error=error),
    )


def _finish_update(dialog, archive, commit, error):
    if error == "UP_TO_DATE":
        _reset_update_button(dialog)
        QMessageBox.information(
            dialog, tr("No updates"), tr("You are already using the latest version.")
        )
        return

    if error:
        _reset_update_button(dialog)
        _report_failure(dialog, error)
        return

    launch_error = apply_archive(dialog, archive, commit)
    if launch_error:
        _reset_update_button(dialog)
        _report_launch_failure(dialog, launch_error)
        return

    window = dialog.parentWidget()
    dialog.reject()
    if window is not None:
        window.close()
    else:
        QApplication.quit()


def prompt_install(window, commit):
    """Offer a background-detected update and install it when accepted.

    Returns True when the download was started, False when the user declined.
    """
    answer = QMessageBox.question(
        window,
        tr("Update available"),
        tr(
            "A new version of Study App is available. Install it now? "
            "Your progress and settings will be kept."
        ),
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes,
    )
    if answer != QMessageBox.StandardButton.Yes:
        return False

    # Deliberately unparented: the window may close while the download runs.
    worker = UpdateWorker(None, commit=commit)
    window.update_worker = worker

    def finished(archive, finished_commit, error):
        if error == "UP_TO_DATE":
            QMessageBox.information(
                window, tr("No updates"), tr("You are already using the latest version.")
            )
            return
        if error:
            _report_failure(window, error)
            return
        launch_error = apply_archive(window, archive, finished_commit)
        if launch_error:
            _report_launch_failure(window, launch_error)
            return
        window.close()

    worker.completed.connect(finished)
    worker.start()
    return True
