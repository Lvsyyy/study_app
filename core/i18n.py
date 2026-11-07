"""Runtime UI translations.

Only interface text is translated. Questions, topics, answers and exercise
content always stay in German, which is why nothing here is applied to them.
"""

LANGUAGES = ("English", "Deutsch")
DEFAULT_LANGUAGE = "English"

_WEEKDAYS = {
    "English": ("Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"),
    "Deutsch": ("Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"),
}

_WEEKDAYS_LONG = {
    "English": (
        "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday",
    ),
    "Deutsch": (
        "Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag",
    ),
}

_MONTHS = {
    "English": (
        "January", "February", "March", "April", "May", "June",
        "July", "August", "September", "October", "November", "December",
    ),
    "Deutsch": (
        "Januar", "Februar", "März", "April", "Mai", "Juni",
        "Juli", "August", "September", "Oktober", "November", "Dezember",
    ),
}

# Keys are the English source text so call sites stay readable.
GERMAN = {
    # Navigation and shells
    "Home": "Start",
    "Subjects": "Fächer",
    "Statistics": "Statistik",
    "Information": "Informationen",
    "Saved": "Gespeichert",
    "Settings": "Einstellungen",
    "SUBJECTS": "FÄCHER",
    "Practice": "Übung",
    "←  Back": "←  Zurück",
    # Dashboard
    "Dashboard": "Übersicht",
    "Your learning overview": "Dein Lernfortschritt",
    "Day streak": "Tage in Folge",
    "Consecutive study days": "Aufeinanderfolgende Lerntage",
    "Correct": "Richtig",
    "Correct answers": "Richtige Antworten",
    "Wrong": "Falsch",
    "Incorrect answers": "Falsche Antworten",
    "Total questions": "Fragen insgesamt",
    "All recorded attempts": "Alle erfassten Versuche",
    "Study time": "Lernzeit",
    "Active time in the app": "Aktive Zeit in der App",
    "Weak points": "Schwache Themen",
    "Topics with the lowest recorded accuracy": "Themen mit der niedrigsten Trefferquote",
    "Study activity": "Lernaktivität",
    "Each cell is one day. Brighter means more study.": (
        "Jede Zelle ist ein Tag. Heller bedeutet mehr Lernen."
    ),
    "Upcoming Exams": "Anstehende Prüfungen",
    "Loading…": "Lädt…",
    "School schedule": "Stundenplan",
    "Unavailable": "Nicht verfügbar",
    "No upcoming exams found.": "Keine anstehenden Prüfungen gefunden.",
    "No schedule entries found.": "Keine Einträge im Stundenplan gefunden.",
    "Today": "Heute",
    "In {days} days": "In {days} Tagen",
    "{days} days ago": "Vor {days} Tagen",
    "NEW": "NEU",
    "Exam details": "Prüfungsdetails",
    "Study for exam": "Für Prüfung lernen",
    "Close": "Schließen",
    "Less": "Weniger",
    "More": "Mehr",
    "No attempts yet": "Noch keine Versuche",
    "Not enough attempt data yet.": "Noch nicht genug Daten.",
    "Avg {seconds:.1f}s per question": "Ø {seconds:.1f}s pro Frage",
    "{percent} accuracy": "{percent} Trefferquote",
    "{accuracy}% accuracy": "{accuracy}% Trefferquote",
    "{entries} entries": "{entries} Einträge",
    "Unspecified": "Ohne Fach",
    "Could not load exams: {error}": "Prüfungen konnten nicht geladen werden: {error}",
    "Could not load school schedule: {error}": (
        "Stundenplan konnte nicht geladen werden: {error}"
    ),
    "Study time: {minutes} min": "Lernzeit: {minutes} Min",
    "Questions: {questions}": "Fragen: {questions}",
    "{weekday}, {day} {month} {year}": "{weekday}, {day}. {month} {year}",
    # Subjects page
    "Pick a subject to practise": "Wähle ein Fach zum Üben",
    "Random questions generated as you practise": (
        "Zufällige Fragen werden beim Üben erzeugt"
    ),
    "{questions} question(s)  ·  {attempts} attempt(s)": (
        "{questions} Frage(n)  ·  {attempts} Versuch(e)"
    ),
    "Accuracy: {percent}": "Trefferquote: {percent}",
    # Subject menu
    "Choose a topic or practise a selection.": "Wähle ein Thema oder eine Auswahl.",
    "Mixed practice": "Gemischte Übung",
    "Questions from every topic in this subject": (
        "Fragen aus allen Themen dieses Fachs"
    ),
    "Mixed {group} practice": "Gemischte Übung: {group}",
    "Start mixed practice": "Gemischte Übung starten",
    "Topics": "Themen",
    "No topics available yet.": "Noch keine Themen vorhanden.",
    "Exam practice": "Prüfungsübung",
    # Statistics page
    "Calculated from your answers and study sessions": (
        "Berechnet aus deinen Antworten und Lernsitzungen"
    ),
    "Accuracy": "Trefferquote",
    "Correct / all attempts": "Richtig / alle Versuche",
    "Total active time": "Gesamte aktive Zeit",
    "Avg. per question": "Ø pro Frage",
    "Time to answer": "Zeit bis zur Antwort",
    "Sessions": "Sitzungen",
    "Times you studied": "Anzahl deiner Lernsitzungen",
    "Longest streak": "Längste Serie",
    "Consecutive days": "Aufeinanderfolgende Tage",
    "Accuracy by subject": "Trefferquote pro Fach",
    "Weakest topics": "Schwächste Themen",
    "No attempts recorded yet.": "Noch keine Versuche erfasst.",
    "Not enough attempt data yet (needs 2+ per topic).": (
        "Noch nicht genug Daten (mindestens 2 pro Thema)."
    ),
    "{percent}  ({attempts} attempts)": "{percent}  ({attempts} Versuche)",
    "{accuracy}%  ({attempts} attempts)": "{accuracy}%  ({attempts} Versuche)",
    "{days} d": "{days} T",
    "{streak} day": "{streak} Tag",
    "{streak} days": "{streak} Tage",
    "{seconds}s": "{seconds}s",
    "{minutes} min": "{minutes} Min",
    "{hours} h {minutes:02d} min": "{hours} Std {minutes:02d} Min",
    # Saved page
    "Saved questions": "Gespeicherte Fragen",
    "Questions you starred while practising": (
        "Fragen, die du beim Üben markiert hast"
    ),
    "Practice all saved": "Alle gespeicherten üben",
    "Nothing saved yet. Press “☆ Save” on a question to keep it here.": (
        "Noch nichts gespeichert. Drücke bei einer Frage auf „☆ Speichern“."
    ),
    "Remove": "Entfernen",
    # Information page
    "Pick a subject to read": "Wähle ein Fach zum Lesen",
    "Show all information": "Alle Informationen anzeigen",
    "All information in this subject": "Alle Informationen dieses Fachs",
    "All info": "Alle Infos",
    "Every subject and topic in one document": (
        "Alle Fächer und Themen in einem Dokument"
    ),
    "Contents": "Inhalt",
    "Open": "Öffnen",
    "No information for this subject yet.": (
        "Noch keine Informationen für dieses Fach."
    ),
    "No information for this topic yet.": (
        "Noch keine Informationen für dieses Thema."
    ),
    "{count} section(s)": "{count} Abschnitt(e)",
    "{topic}  ·  {count} section(s)": "{topic}  ·  {count} Abschnitt(e)",
    "{topic}  ·  empty": "{topic}  ·  leer",
    # Subnetting page
    "Network address": "Netzwerkadresse",
    "Broadcast address": "Broadcastadresse",
    "Enter an IPv4 address": "IPv4-Adresse eingeben",
    "Decimal": "Dezimal",
    "Binary": "Binär",
    "IP address": "IP-Adresse",
    "Subnet mask": "Subnetzmaske",
    "Choose one of the pre-split rooms and split it further. {count} split(s) left.": (
        "Wähle einen der vorgeteilten Räume und teile ihn weiter. "
        "Noch {count} Teilung(en)."
    ),
    "Split the selected room. {count} split(s) left.": (
        "Teile den markierten Raum. Noch {count} Teilung(en)."
    ),
    "Calculate and label the network. {detail}": (
        "Berechne und beschrifte das Netzwerk. {detail}"
    ),
    "Calculate and label the network. Enter the network and broadcast addresses of all subnets into the fields in the square.": (
        "Berechne und beschrifte das Netzwerk. Trage die Netzwerk- und "
        "Broadcastadressen aller Teilnetze in die Felder im Quadrat ein."
    ),
    "Hint: Calculate the network address first from the IP address and subnet mask. Each split increases the prefix by 1.": (
        "Tipp: Berechne zuerst die Netzwerkadresse mit der IP-Adresse und "
        "Subnetzmaske. Jede Teilung erhöht den Präfix um 1."
    ),
    "Solutions have been filled in.": "Lösungen wurden eingetragen.",
    "Finish the split first.": "Schließe zuerst die Aufteilung ab.",
    "All network and broadcast addresses are correct.": (
        "Alle Netzwerk- und Broadcastadressen sind korrekt."
    ),
    "Some addresses are wrong or missing. Check the marked fields.": (
        "Einige Adressen sind falsch oder fehlen. Prüfe die markierten Felder."
    ),
    # Flowchart editor
    "Edit connection": "Verbindung bearbeiten",
    "Line type:": "Linientyp:",
    "Edit flowchart block": "PAP-Block bearbeiten",
    "Block text:": "Blocktext:",
    "Add flowchart block": "PAP-Block hinzufügen",
    "Add block": "Block hinzufügen",
    "Delete selected block": "Ausgewählten Block löschen",
    "Drag blocks · Mouse wheel: zoom · Middle/right mouse button: move canvas · Connection: drag a circle": (
        "Blöcke ziehen · Mausrad: Zoom · Mittlere/rechte Maustaste: "
        "Arbeitsfläche bewegen · Verbindung: Kreis ziehen"
    ),
    "Drag a connection and release it on another circle.": (
        "Verbindung ziehen und auf einem anderen Kreis loslassen."
    ),
    "No connection created.": "Keine Verbindung erstellt.",
    "Connection created.": "Verbindung erstellt.",
    # Code editors and batch console
    "Run": "Ausführen",
    "// Write your code here": "// Schreibe deinen Code hier",
    "Command prompt": "Eingabeaufforderung",
    "Expected output": "Vorgegebene Ausgabe",
    "C:\\Users\\ExampleUser>": "C:\\Users\\Supercoolerbenutzer>",
    "Output matches the expected output.": (
        "Ausgabe stimmt mit der Vorgabe überein."
    ),
    "The output does not match the expected output yet.": (
        "Die Ausgabe stimmt noch nicht mit der Vorgabe überein."
    ),
    "Batch error: {error}": "Batch-Fehler: {error}",
    # Math menu
    "Choose which type of question to practise.": (
        "Wähle den Aufgabentyp, den du üben möchtest."
    ),
    "All question types in random order": "Alle Aufgabentypen in zufälliger Reihenfolge",
    "Question types": "Aufgabentypen",
    # Question page
    "Type your answer…": "Antwort eingeben…",
    "Complete the calculation…": "Berechnung vervollständigen…",
    "Correct solution": "Richtige Lösung",
    "Correct solution shown below your answer.": (
        "Die richtige Lösung steht unter deiner Antwort."
    ),
    "Check answer": "Antwort prüfen",
    "Skip": "Überspringen",
    "Hint": "Tipp",
    "Show answer": "Lösung zeigen",
    "☆  Save": "☆  Speichern",
    "★  Saved": "★  Gespeichert",
    "Next  →": "Weiter  →",
    "Practice again": "Noch einmal üben",
    "Round complete": "Runde abgeschlossen",
    "You answered {answered} question(s): {correct} correct.": (
        "Du hast {answered} Frage(n) beantwortet: {correct} richtig."
    ),
    "Enter an answer first.": "Gib zuerst eine Antwort ein.",
    "Correct ✓": "Richtig ✓",
    "Correct ✓{took}": "Richtig ✓{took}",
    "Subject": "Fach",
    "Correct ✓ (first try counted)": "Richtig ✓ (erster Versuch zählt)",
    "Incorrect. {note}Try again or show the answer.": (
        "Falsch. {note}Versuche es erneut oder zeige die Lösung."
    ),
    "Only your first attempt counts. ": "Nur dein erster Versuch zählt. ",
    "Hint: {hint}": "Tipp: {hint}",
    "Question {number}": "Frage {number}",
    "Question {number} of {total}": "Frage {number} von {total}",
    "Topic accuracy: {accuracy}% over {attempts} attempts": (
        "Themen-Trefferquote: {accuracy}% bei {attempts} Versuchen"
    ),
    "No attempts in this topic yet": "Noch keine Versuche in diesem Thema",
    "difficulty": "Schwierigkeit",
    "The question image could not be loaded.": (
        "Das Bild zur Frage konnte nicht geladen werden."
    ),
    "No questions for {heading} yet.": "Noch keine Fragen für {heading}.",
    "Choose a subject from the sidebar to start practising.": (
        "Wähle ein Fach in der Seitenleiste, um zu üben."
    ),
    "The flowchart solution could not be loaded.": (
        "Die PAP-Lösung konnte nicht geladen werden."
    ),
    "Flowchart blocks:": "PAP-Blöcke:",
    "Connections:": "Verbindungen:",
    "Correct options:": "Richtige Optionen:",
    "Correct order:": "Richtige Reihenfolge:",
    "Correct matches:": "Richtige Zuordnungen:",
    "Correct categories:": "Richtige Kategorien:",
    "Solution:": "Lösung:",
    "Expected output:": "Erwartete Ausgabe:",
    "Console output:": "Konsolenausgabe:",
    "Drag the items into the correct order:": (
        "Ziehe die Elemente in die richtige Reihenfolge:"
    ),
    "Select a definition…": "Wähle eine Definition…",
    "Drop here": "Hier ablegen",
    "All cards placed correctly.": "Alle Karten richtig zugeordnet.",
    "Right": "Richtig",
    "Wrong – try again.": "Falsch – versuche es erneut.",
    # Settings
    "Appearance": "Darstellung",
    "Color theme": "Farbschema",
    "Icon pack": "Symbolpaket",
    "Language": "Sprache",
    "Cancel": "Abbrechen",
    "Save": "Speichern",
    "Language changed": "Sprache geändert",
    "Restart Study App to apply the new language.": (
        "Starte Study App neu, um die neue Sprache zu übernehmen."
    ),
    # Updates
    "Check for updates": "Nach Updates suchen",
    "Checking…": "Prüfe…",
    "Update Study App": "Study App aktualisieren",
    "Check GitHub for updates and install the latest version? Your progress and settings will be kept.": (
        "Nach Updates auf GitHub suchen und die neueste Version installieren? "
        "Dein Fortschritt und deine Einstellungen bleiben erhalten."
    ),
    "No updates": "Keine Updates",
    "You are already using the latest version.": (
        "Du verwendest bereits die neueste Version."
    ),
    "Update failed": "Update fehlgeschlagen",
    "Could not check for or download the update:\n{error}": (
        "Update konnte nicht geprüft oder heruntergeladen werden:\n{error}"
    ),
    "Could not start the updater:\n{error}": (
        "Der Updater konnte nicht gestartet werden:\n{error}"
    ),
    "Update ready": "Update bereit",
    "The app will close, update, and restart.": (
        "Die App wird geschlossen, aktualisiert und neu gestartet."
    ),
    "Update available": "Update verfügbar",
    "A new version of Study App is available. Install it now? Your progress and settings will be kept.": (
        "Eine neue Version von Study App ist verfügbar. Jetzt installieren? "
        "Dein Fortschritt und deine Einstellungen bleiben erhalten."
    ),
    "Later": "Später",
    "Update now": "Jetzt aktualisieren",
}

_current = DEFAULT_LANGUAGE


def set_language(name):
    """Select the active UI language; unknown names fall back to English."""
    global _current
    _current = name if name in LANGUAGES else DEFAULT_LANGUAGE


def tr(text, **values):
    """Translate UI text, formatting `{placeholders}` when values are given."""
    translated = GERMAN.get(text, text) if _current == "Deutsch" else text
    return translated.format(**values) if values else translated


def weekday_short(index):
    return _WEEKDAYS[_current][index % 7]


def weekday_long(index):
    return _WEEKDAYS_LONG[_current][index % 7]


def month_name(number):
    return _MONTHS[_current][(int(number) - 1) % 12]
