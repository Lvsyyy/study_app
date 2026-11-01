"""One-click source updater for Windows and macOS."""
import json
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from PySide6.QtCore import QThread, Signal
from PySide6.QtWidgets import QApplication, QMessageBox

API_URL = "https://api.github.com/repos/Lvsyyy/study_app/commits/main"
ARCHIVE_URL = "https://github.com/Lvsyyy/study_app/archive/{commit}.zip"

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
excluded = {".git", ".venv", "__pycache__", ".pytest_cache"}
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


class UpdateWorker(QThread):
    completed = Signal(str, str, str)

    def run(self):
        try:
            from urllib.request import Request, urlopen

            headers = {"User-Agent": "Study-App-Updater"}
            request = Request(API_URL, headers=headers)
            with urlopen(request, timeout=20) as response:
                commit = json.loads(response.read())["sha"]

            app_root = Path(__file__).resolve().parent.parent
            marker = app_root / ".study_app_commit"
            if marker.is_file() and marker.read_text(encoding="utf-8").strip() == commit:
                self.completed.emit("", "", "UP_TO_DATE")
                return

            folder = Path(tempfile.mkdtemp(prefix="study-app-update-"))
            archive = folder / "update.zip"
            request = Request(ARCHIVE_URL.format(commit=commit), headers=headers)
            with urlopen(request, timeout=60) as response, archive.open("wb") as output:
                shutil.copyfileobj(response, output)
            self.completed.emit(str(archive), commit, "")
        except Exception as error:
            self.completed.emit("", "", str(error))


def start_update(dialog):
    answer = QMessageBox.question(
        dialog,
        "Update Study App",
        "Check GitHub for updates and install the latest version? Your progress and settings will be kept.",
        QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        QMessageBox.StandardButton.Yes,
    )
    if answer != QMessageBox.StandardButton.Yes:
        return

    dialog.update_button.setEnabled(False)
    dialog.update_button.setText("Checking…")
    dialog.update_worker = UpdateWorker(dialog)
    dialog.update_worker.completed.connect(
        lambda archive, commit, error: _finish_update(dialog, archive, commit, error)
    )
    dialog.update_worker.start()


def _finish_update(dialog, archive, commit, error):
    if error == "UP_TO_DATE":
        dialog.update_button.setEnabled(True)
        dialog.update_button.setText("Check for updates")
        QMessageBox.information(dialog, "No updates", "You are already using the latest version.")
        return

    if error:
        dialog.update_button.setEnabled(True)
        dialog.update_button.setText("Check for updates")
        QMessageBox.critical(dialog, "Update failed", f"Could not check for or download the update:\n{error}")
        return

    app_root = Path(__file__).resolve().parent.parent
    launch_script = Path(sys.argv[0]).resolve()
    launch_command = [sys.executable, str(launch_script), *sys.argv[1:]]
    folder = Path(archive).parent
    helper = folder / "apply_update.py"
    helper.write_text(HELPER, encoding="utf-8")

    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    try:
        subprocess.Popen(
            [
                sys.executable,
                str(helper),
                archive,
                str(app_root),
                str(os.getpid()),
                json.dumps(launch_command),
                commit,
            ],
            cwd=folder,
            creationflags=flags,
            start_new_session=(sys.platform == "darwin"),
        )
    except Exception as launch_error:
        dialog.update_button.setEnabled(True)
        dialog.update_button.setText("Check for updates")
        QMessageBox.critical(dialog, "Update failed", f"Could not start the updater:\n{launch_error}")
        return

    QMessageBox.information(dialog, "Update ready", "The app will close, update, and restart.")
    window = dialog.parentWidget()
    dialog.reject()
    if window is not None:
        window.close()
    else:
        QApplication.quit()
