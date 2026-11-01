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

**1.** [Python](https://www.python.org/downloads/) und [Git](https://git-scm.com/downloads) installieren. Bei Python die Option **Add Python to PATH** aktivieren.

**2.** PowerShell öffnen und die Befehle nacheinander ausführen:

```powershell
git clone https://github.com/Lvsyyy/study_app.git
cd study_app
py -m venv .venv
.\.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
py main.py
```

Falls PowerShell die Aktivierung blockiert, einmal diesen Befehl ausführen und danach die Aktivierung erneut versuchen:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

## Später starten

Im Projektordner:

- **Linux:** `source .venv/bin/activate` und danach `python main.py`
- **Windows:** `.\.venv\Scripts\Activate.ps1` und danach `py main.py`

## Aktualisieren

Im Projektordner:

```bash
git pull
```
