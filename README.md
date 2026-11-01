# Installation

## Linux (Arch)

Alle Befehle im Terminal ausführen:

```bash
sudo pacman -S --needed git python python-pip
git clone https://github.com/Lvsyyy/study_app.git
cd study_app
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python main.py
```

## Windows

**1.** [Python herunterladen](https://www.python.org/downloads/) und installieren. Dabei **Add Python to PATH** aktivieren.

**2.** [Projekt als ZIP herunterladen](https://github.com/Lvsyyy/study_app/archive/refs/heads/main.zip) und entpacken.

**3.** Im entpackten Ordner PowerShell oder das Terminal öffnen und diese Befehle nacheinander ausführen:

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe main.py
```

## Später starten

Im Projektordner:

- **Linux:** `source .venv/bin/activate` und danach `python main.py`
- **Windows:** ` .\.venv\Scripts\python.exe main.py`

## Aktualisieren

- **Linux:** Im Projektordner `git pull` ausführen.
- **Windows:** Die aktuelle [ZIP-Datei](https://github.com/Lvsyyy/study_app/archive/refs/heads/main.zip) herunterladen und entpacken. Danach im Projektordner die App wie oben starten.
