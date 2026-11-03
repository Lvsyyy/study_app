SCHEMA_VERSION = 6

DEFAULT_SUBJECTS = ("NT", "AE", "Math", "CS_P", "CS", "English", "BS", "PuG", "Ethik")

# Version 1 is the base schema. Migrations are applied in ascending order.
MIGRATIONS = {
    2: """
    ALTER TABLE questions ADD COLUMN alt_answers TEXT;
    CREATE INDEX IF NOT EXISTS idx_attempts_created_q
        ON attempts(question_id, created_at);
    """,
    3: """
    ALTER TABLE questions ADD COLUMN answer_template TEXT;
    """,

    6: """
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'BIOS und UEFI' FROM subjects WHERE name = 'BS';

    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Bootvorgang und POST' FROM subjects WHERE name = 'BS';

    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Festplatten' FROM subjects WHERE name = 'BS';

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Ordne die Schritte eines BIOS-Updates in die richtige Reihenfolge.',
           '{"items":["Mainboard und BIOS/UEFI-Version identifizieren","Update-Dateien finden und herunterladen","Backup wichtiger Dateien erstellen","Update-Methode auswählen: Windows, BIOS-Flash-Menü oder DOS","BIOS vorbereiten: Schreibschutz prüfen und Einstellungen speichern","BIOS-Update durchführen","BIOS aufräumen: CMOS löschen und Stromversorgung trennen","Bei Problemen das alte BIOS wiederherstellen"]}',
           'Beginne mit der Identifikation des Mainboards.',
           3, 'ordering'
    FROM topics t JOIN subjects s ON s.id = t.subject_id
    WHERE s.name = 'BS' AND t.name = 'BIOS und UEFI'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne die Schritte eines BIOS-Updates in die richtige Reihenfolge.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Welche Möglichkeiten gibt es, die installierte BIOS-Version zu ermitteln? Wähle alle passenden Antworten.',
           '{"options":["Systeminformation / MsInfo32","Aufkleber am Gerät oder Mainboard","Hersteller-Webseite","Handbuch","Hersteller-Tools","Nur über den Geräte-Manager","Nur durch Öffnen des Netzteils"],"correct":[0,1,2,3,4]}',
           'Es gibt mehrere Informationsquellen: Windows, Gerät und Hersteller.',
           2, 'multi_select'
    FROM topics t JOIN subjects s ON s.id = t.subject_id
    WHERE s.name = 'BS' AND t.name = 'BIOS und UEFI'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Welche Möglichkeiten gibt es, die installierte BIOS-Version zu ermitteln? Wähle alle passenden Antworten.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Welche drei Methoden können für ein BIOS-Update verwendet werden? Wähle alle drei.',
           '{"options":["Update unter Windows","Update über das BIOS-/UEFI-Flash-Menü","Update über DOS","Update über den Geräte-Manager","Update über den Task-Manager"],"correct":[0,1,2]}',
           'Eine Methode läuft direkt in Windows, eine im Firmware-Menü und eine in DOS.',
           2, 'multi_select'
    FROM topics t JOIN subjects s ON s.id = t.subject_id
    WHERE s.name = 'BS' AND t.name = 'BIOS und UEFI'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Welche drei Methoden können für ein BIOS-Update verwendet werden? Wähle alle drei.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Ordne die Schritte des POST-Selbsttests in die angegebene Reihenfolge.',
           '{"items":["Funktionsfähigkeit der CPU prüfen","CPU-nahe Bausteine prüfen","CMOS-RAM prüfen","CPU-nahen Cache-Speicher prüfen","Erste 64 Kilobyte des Arbeitsspeichers prüfen","Grafikspeicher und Grafikausgabe prüfen"]}',
           'Der Test beginnt mit der CPU und arbeitet sich zu Speicher und Grafik vor.',
           3, 'ordering'
    FROM topics t JOIN subjects s ON s.id = t.subject_id
    WHERE s.name = 'BS' AND t.name = 'Bootvorgang und POST'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne die Schritte des POST-Selbsttests in die angegebene Reihenfolge.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Wie kann das BIOS/UEFI Fehler während des POST melden? Wähle alle passenden Antworten.',
           '{"options":["Auf dem Bildschirm","Akustische Signale (Beep-Codes)","Visuelle Signale / Statusanzeigen","Per E-Mail","Über Lautsprecher mit gesprochenem Text"],"correct":[0,1,2]}',
           'Fehler werden visuell oder akustisch am Gerät signalisiert.',
           2, 'multi_select'
    FROM topics t JOIN subjects s ON s.id = t.subject_id
    WHERE s.name = 'BS' AND t.name = 'Bootvorgang und POST'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wie kann das BIOS/UEFI Fehler während des POST melden? Wähle alle passenden Antworten.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Welche Aufgaben übernimmt das BIOS/UEFI während des Bootvorgangs? Wähle alle passenden Antworten.',
           '{"options":["POST / Selbsttest durchführen","Hardware initialisieren","Systemkonfiguration auslesen","Bootloader bzw. Betriebssystemstart einleiten","Benutzerprogramme starten","Dateien des Benutzers sortieren"],"correct":[0,1,2,3]}',
           'Es prüft und initialisiert die Hardware und leitet den Start des Betriebssystems ein.',
           3, 'multi_select'
    FROM topics t JOIN subjects s ON s.id = t.subject_id
    WHERE s.name = 'BS' AND t.name = 'Bootvorgang und POST'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Welche Aufgaben übernimmt das BIOS/UEFI während des Bootvorgangs? Wähle alle passenden Antworten.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Welche Vorteile bietet UEFI gegenüber klassischem BIOS? Wähle alle passenden Antworten.',
           '{"options":["Secure Boot","Verbesserte Sicherheitsfunktionen","Schnellere Bootzeiten","Unterstützung moderner Hardware und größerer Datenträger","Kompatibilität mit modernen Systemen","Garantiert doppelte CPU-Leistung"],"correct":[0,1,2,3,4]}',
           'UEFI erweitert Firmware-Funktionen und unterstützt moderne Sicherheits- und Hardwarestandards.',
           3, 'multi_select'
    FROM topics t JOIN subjects s ON s.id = t.subject_id
    WHERE s.name = 'BS' AND t.name = 'Bootvorgang und POST'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Welche Vorteile bietet UEFI gegenüber klassischem BIOS? Wähle alle passenden Antworten.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Ordne jedem Begriff die passende Beschreibung zu.',
           '{"pairs":[{"left":"Sektoren","right":"Abschnitte einer Spur; kleinste adressierbare Einheiten bzw. Blöcke"},{"left":"Spuren","right":"Ringförmige Bereiche auf einer Plattenoberfläche"},{"left":"Zylinder","right":"Spuren mit gleicher Nummer auf allen Plattenoberflächen"},{"left":"Cluster","right":"Zusammenfassung mehrerer Sektoren; kleinste vom Dateisystem verwaltete Speichereinheit"}]}',
           'Unterscheide die physische Einteilung der Platte von der Verwaltung durch das Dateisystem.',
           3, 'matching'
    FROM topics t JOIN subjects s ON s.id = t.subject_id
    WHERE s.name = 'BS' AND t.name = 'Festplatten'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne jedem Begriff die passende Beschreibung zu.');
    """,
    5: """
    UPDATE questions
    SET answer = 'Console.WriteLine("Hallo Welt");'
    WHERE topic_id IN (
        SELECT t.id
        FROM topics t
        JOIN subjects s ON s.id = t.subject_id
        WHERE s.name = 'AE' AND t.name = 'Ausgabe'
    )
      AND question_text LIKE 'Gebe "Hallo Welt" aus%';
    """,
    4: """
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Ausgabe' FROM subjects WHERE name = 'AE';

    INSERT INTO questions
        (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT
        t.id,
        'Gebe "Hallo Welt" aus' || char(10) ||
        '    static void Main(string[] args)' || char(10) ||
        '    {' || char(10) ||
        '        ' || char(10) ||
        '    }',
        'Console.WriteLine("Hallo Welt")',
        'Console. benutzen',
        1,
        'code'
    FROM topics t
    JOIN subjects s ON s.id = t.subject_id
    WHERE s.name = 'AE'
      AND t.name = 'Ausgabe'
      AND NOT EXISTS (
          SELECT 1 FROM questions q
          WHERE q.topic_id = t.id
            AND q.question_text LIKE 'Gebe "Hallo Welt" aus%'
      );
    """,
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS subjects (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    icon TEXT
);

CREATE TABLE IF NOT EXISTS topics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    subject_id INTEGER NOT NULL REFERENCES subjects(id) ON DELETE CASCADE,
    name TEXT NOT NULL,
    UNIQUE(subject_id, name)
);

CREATE TABLE IF NOT EXISTS questions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic_id INTEGER NOT NULL REFERENCES topics(id) ON DELETE CASCADE,
    question_text TEXT NOT NULL,
    answer TEXT NOT NULL,
    hint TEXT,
    question_image TEXT,
    difficulty INTEGER NOT NULL DEFAULT 1 CHECK(difficulty BETWEEN 1 AND 5),
    question_type TEXT NOT NULL DEFAULT 'text',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attempts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    question_id INTEGER NOT NULL REFERENCES questions(id) ON DELETE CASCADE,
    user_answer TEXT NOT NULL,
    is_correct INTEGER NOT NULL CHECK(is_correct IN (0, 1)),
    time_taken REAL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS study_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT NOT NULL,
    ended_at TEXT,
    duration INTEGER NOT NULL DEFAULT 0,
    questions_completed INTEGER NOT NULL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS saved_questions (
    question_id INTEGER PRIMARY KEY REFERENCES questions(id) ON DELETE CASCADE,
    saved_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_topics_subject ON topics(subject_id);
CREATE INDEX IF NOT EXISTS idx_questions_topic ON questions(topic_id);
CREATE INDEX IF NOT EXISTS idx_attempts_question ON attempts(question_id);
CREATE INDEX IF NOT EXISTS idx_attempts_created ON attempts(created_at);
CREATE INDEX IF NOT EXISTS idx_sessions_started ON study_sessions(started_at);
"""
