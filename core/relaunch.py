"""Restart the running app in a detached process."""
import subprocess
import sys
from pathlib import Path


def app_root() -> Path:
    return Path(__file__).resolve().parent.parent


def launch_command():
    script = Path(sys.argv[0]).resolve()
    return [sys.executable, str(script), *sys.argv[1:]]


def relaunch():
    """Start a detached copy of the app. Returns True when it was started."""
    flags = 0
    if sys.platform == "win32":
        flags = subprocess.CREATE_NEW_PROCESS_GROUP | subprocess.DETACHED_PROCESS

    try:
        subprocess.Popen(
            launch_command(),
            cwd=app_root(),
            creationflags=flags,
            start_new_session=(sys.platform == "darwin"),
        )
    except OSError:
        return False
    return True
