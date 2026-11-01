# Installation

## 1. Voraussetzungen installieren

Unter Arch Linux:

```bash
sudo pacman -S --needed git python python-pip
```

## 2. Projekt herunterladen

```bash
git clone https://github.com/Lvsyyy/study_app.git
cd study_app
```

## 3. Virtuelle Python-Umgebung erstellen

```bash
python -m venv .venv
```

## 4. Virtuelle Umgebung aktivieren

```bash
source .venv/bin/activate
```

## 5. Benötigte Pakete installieren

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

## 6. Programm starten

```bash
python main.py
```

## Programm später erneut starten

Im Projektordner:

```bash
source .venv/bin/activate
python main.py
```

## Programm aktualisieren

Im Projektordner:

```bash
git pull
source .venv/bin/activate
python -m pip install -r requirements.txt
```
