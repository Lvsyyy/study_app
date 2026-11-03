SCHEMA_VERSION = 11

DEFAULT_SUBJECTS = ("NT", "AE", "Math", "CS_P", "CS", "English", "BS", "PuG", "Ethik")

# Version 1 is the base schema. Migrations are applied in ascending order.
MIGRATIONS = {
    11: """
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'BIOS update' FROM subjects WHERE name = 'BS';

    UPDATE questions
    SET topic_id = (
        SELECT target.id FROM topics target
        JOIN subjects subject ON subject.id = target.subject_id
        WHERE subject.name = 'BS' AND target.name = 'BIOS update'
    )
    WHERE topic_id IN (
        SELECT source.id FROM topics source
        JOIN subjects subject ON subject.id = source.subject_id
        WHERE subject.name = 'BS' AND source.name = 'BIOS und UEFI'
    );

    DELETE FROM topics
    WHERE subject_id = (SELECT id FROM subjects WHERE name = 'BS')
      AND name = 'BIOS und UEFI';
    """,

    10: """
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Bootvorgang' FROM subjects WHERE name = 'BS';

    UPDATE questions
    SET topic_id = (
        SELECT target.id
        FROM topics target
        JOIN subjects subject ON subject.id = target.subject_id
        WHERE subject.name = 'BS' AND target.name = 'Bootvorgang'
    )
    WHERE topic_id IN (
        SELECT source.id
        FROM topics source
        JOIN subjects subject ON subject.id = source.subject_id
        WHERE subject.name = 'BS'
          AND source.name IN ('Bootvorgang und POST', 'PAP')
    );

    DELETE FROM topics
    WHERE subject_id = (SELECT id FROM subjects WHERE name = 'BS')
      AND name IN ('Bootvorgang und POST', 'PAP');
    """,

    9: """
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'PAP' FROM subjects WHERE name = 'BS';

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Erstelle einen PAP für den Bootvorgang. Verwende Start/Ende-, Verarbeitungs- und Entscheidungsblöcke und verbinde sie mit den passenden Ja-/Nein-Zweigen.',
           '{"nodes":[{"id":1,"type":"Start/End","text":"Start des Bootvorgangs"},{"id":2,"type":"Process","text":"PC einschalten"},{"id":3,"type":"Process","text":"BIOS laden"},{"id":4,"type":"Process","text":"Selbsttest (POST)"},{"id":5,"type":"Decision","text":"Hardware OK?"},{"id":6,"type":"Process","text":"CMOS lesen"},{"id":7,"type":"Process","text":"Grundkonfiguration der Komponenten"},{"id":8,"type":"Decision","text":"Betriebssystem vorhanden?"},{"id":9,"type":"Process","text":"Betriebssystem starten"},{"id":10,"type":"Start/End","text":"Betriebssystem geladen"},{"id":11,"type":"Process","text":"Fehlermeldung"},{"id":12,"type":"Process","text":"Fehlerbeseitigung"},{"id":13,"type":"Start/End","text":"PC ausschalten"}],"edges":[{"from":1,"to":2,"label":"Normal"},{"from":2,"to":3,"label":"Normal"},{"from":3,"to":4,"label":"Normal"},{"from":4,"to":5,"label":"Normal"},{"from":5,"to":6,"label":"Ja"},{"from":5,"to":11,"label":"Nein"},{"from":6,"to":7,"label":"Normal"},{"from":7,"to":8,"label":"Normal"},{"from":8,"to":9,"label":"Ja"},{"from":8,"to":11,"label":"Nein"},{"from":9,"to":10,"label":"Normal"},{"from":11,"to":12,"label":"Normal"},{"from":12,"to":13,"label":"Normal"}]}',
           'Beginne mit Start des Bootvorgangs. Bei einer fehlgeschlagenen Prüfung führen beide Nein-Zweige zur Fehlermeldung und anschließend zum Ausschalten.',
           3, 'pap'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='PAP'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_type='pap');
    """,

    8: """
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Batch' FROM subjects WHERE name = 'BS';

    UPDATE questions
    SET topic_id = (
        SELECT target.id FROM topics target
        WHERE target.name = 'Batch'
          AND target.subject_id = (SELECT id FROM subjects WHERE name = 'BS')
    )
    WHERE topic_id = (
        SELECT source.id FROM topics source
        WHERE source.name = 'Batch'
          AND source.subject_id = (SELECT id FROM subjects WHERE name = 'CS_P')
    );

    DELETE FROM topics
    WHERE name = 'Batch'
      AND subject_id = (SELECT id FROM subjects WHERE name = 'CS_P');
    """,

    7: """
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Batch' FROM subjects WHERE name = 'CS_P';

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Gib die Ausgabe „Das ist eine Ausgabe“ aus.',
           '{"expected_output":["Das ist eine Ausgabe"],"inputs":[],"solution":"echo Das ist eine Ausgabe"}',
           'Verwende den Befehl echo.',
           1, 'batch'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='CS_P' AND t.name='Batch'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Gib die Ausgabe „Das ist eine Ausgabe“ aus.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Gib „Das ist eine Ausgabe“ aus, ändere die Konsolenfarbe und halte das Fenster anschließend an.',
           '{"expected_output":["Das ist eine Ausgabe","Drücken Sie eine beliebige Taste . . ."],"inputs":[],"solution":"@echo off\\ncolor 2F\\necho Das ist eine Ausgabe\\npause"}',
           'Nutze echo, color und pause.',
           2, 'batch'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='CS_P' AND t.name='Batch'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Gib „Das ist eine Ausgabe“ aus, ändere die Konsolenfarbe und halte das Fenster anschließend an.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Frage den Benutzer nach seinem Namen und gib anschließend „Hallo [Name]“ aus.',
           '{"expected_output":["Wie ist dein Name? Cooler Name","","Hallo Cooler Name","Drücken Sie eine beliebige Taste . . ."],"inputs":["Cooler Name"],"solution":"@echo off\\nset /p NAME=Wie ist dein Name? \\necho.\\necho Hallo %NAME%\\npause"}',
           'Verwende set /p, eine Variable und echo.',
           2, 'batch'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='CS_P' AND t.name='Batch'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Frage den Benutzer nach seinem Namen und gib anschließend „Hallo [Name]“ aus.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Lies eine Zahl ein und gib ihr Quadrat aus. Beispiel-Eingabe: 10.',
           '{"expected_output":["Zahl eingeben: 10","Das Quadrat ist 100","Drücken Sie eine beliebige Taste . . ."],"inputs":["10"],"solution":"@echo off\\nset /p ZAHL=Zahl eingeben: \\nset /a Resultat=%ZAHL%*%ZAHL%\\necho Das Quadrat ist %Resultat%\\npause"}',
           'Berechne das Quadrat mit set /a.',
           3, 'batch'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='CS_P' AND t.name='Batch'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Lies eine Zahl ein und gib ihr Quadrat aus. Beispiel-Eingabe: 10.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id,
           'Frage nach OK. Bei der Eingabe „j“ soll „Alles ist richtig weiter so“ erscheinen.',
           '{"expected_output":["j","Alles ist richtig weiter so","Drücken Sie eine beliebige Taste . . ."],"inputs":["j"],"solution":"@echo off\\nset /p OK=\\nIF /I \\"%OK%\\" == \\"j\\" (echo Alles ist richtig weiter so)\\npause"}',
           'Verwende IF /I für einen Vergleich ohne Beachtung der Groß-/Kleinschreibung.',
           3, 'batch'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='CS_P' AND t.name='Batch'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Frage nach OK. Bei der Eingabe „j“ soll „Alles ist richtig weiter so“ erscheinen.');
    """,
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
