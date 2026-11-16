"""The PuG question bank for Arbeitsvertrag and Arbeitszeitgesetz.

Every German sentence below is taken from the course notes unchanged. Only the
question wording, the interaction type and the wrong options are new, so no
question tests a fact the notes do not state.
"""
import json

ARBEITSVERTRAG = "Arbeitsvertrag"
ARBEITSZEITGESETZ = "Arbeitszeitgesetz"

PUG_TOPICS = (ARBEITSVERTRAG, ARBEITSZEITGESETZ)


def _question(topic, text, answer, kind, difficulty=2):
    if not isinstance(answer, str):
        answer = json.dumps(answer, ensure_ascii=False)
    return {
        "topic": topic,
        "text": text,
        "answer": answer,
        "kind": kind,
        "hint": "",
        "difficulty": difficulty,
        "alt": None,
    }


def _single(topic, text, correct, distractors, difficulty=2):
    """One right answer among wrong ones; the UI shuffles the order."""
    return _question(
        topic, text,
        {"options": [correct, *distractors], "correct": [0]},
        "multi_select", difficulty,
    )


def _choice(topic, text, options, correct, difficulty=2):
    return _question(
        topic, text,
        {"options": list(options), "correct": list(correct)},
        "multi_select", difficulty,
    )


def _pairs(topic, text, pairs, difficulty=2):
    return _question(
        topic, text,
        {"pairs": [{"left": left, "right": right} for left, right in pairs]},
        "matching", difficulty,
    )


def _sort(topic, text, categories, cards, difficulty=2):
    return _question(
        topic, text,
        {
            "categories": list(categories),
            "cards": [{"text": text_, "category": category} for text_, category in cards],
        },
        "table_sort", difficulty,
    )


# --- Arbeitsvertrag ----------------------------------------------------------
PFLICHT = "Muss im Arbeitsvertrag enthalten sein"
KEINE_PFLICHT = "Muss nicht enthalten sein"

BANK = (
    _sort(
        ARBEITSVERTRAG,
        "Welche Angaben müssen in einem Arbeitsvertrag enthalten sein?",
        (PFLICHT, KEINE_PFLICHT),
        (
            ("Name und Anschrift", PFLICHT),
            ("Beginn und Ende des Arbeitsverhältnisses", PFLICHT),
            ("Beschreibung der Tätigkeit", PFLICHT),
            ("Arbeitsort", PFLICHT),
            ("Urlaub", PFLICHT),
            ("Gehalt und Gehaltsgruppe", PFLICHT),
            ("Sondervereinbarungen und Betriebsvereinbarungen", PFLICHT),
            ("Arbeitszeit", PFLICHT),
            ("Probezeit", PFLICHT),
            ("Hobbys und Freizeitgestaltung", KEINE_PFLICHT),
            ("Anzahl der Geschwister", KEINE_PFLICHT),
            ("Lieblingsspeise", KEINE_PFLICHT),
        ),
        1,
    ),
    _single(
        ARBEITSVERTRAG,
        "Was versteht man unter der Beschreibung der Tätigkeit?",
        "Sie beschreibt, welche Aufgaben und Tätigkeiten der Arbeitnehmer übernehmen muss.",
        (
            "Sie beschreibt die Anzahl der Urlaubstage, die dem Arbeitnehmer pro Jahr zustehen.",
            "Sie beschreibt die Einstufung nach Tätigkeit und Qualifikation.",
            "Sie beschreibt den Ort, an dem der Arbeitnehmer seine Arbeit verrichtet.",
        ),
    ),
    _single(
        ARBEITSVERTRAG,
        "Was wird bezüglich des Urlaubs im Arbeitsvertrag geregelt?",
        "Die Anzahl der Urlaubstage, die dem Arbeitnehmer pro Jahr zustehen.",
        (
            "Die Anzahl der Krankheitstage, die dem Arbeitnehmer pro Jahr zustehen.",
            "Die Anzahl der Überstunden, die der Arbeitnehmer pro Monat leisten muss.",
            "Die Anzahl der Fortbildungstage, die dem Arbeitnehmer pro Jahr zustehen.",
        ),
    ),
    _single(
        ARBEITSVERTRAG,
        "Was versteht man unter dem Arbeitsort?",
        "Der Ort, an dem der Arbeitnehmer seine Arbeit verrichtet.",
        (
            "Der Ort, an dem der Arbeitgeber seinen Sitz hat.",
            "Der Ort, an dem der Arbeitsvertrag unterschrieben wird.",
            "Der Ort, an dem die Gehaltsabrechnung erstellt wird.",
        ),
    ),
    _pairs(
        ARBEITSVERTRAG,
        "Was ist mit Gehalt und Gehaltsgruppe gemeint?",
        (
            ("Gehalt", "Die Bezahlung für die geleistete Arbeit."),
            ("Gehaltsgruppe", "Die Einstufung nach Tätigkeit und Qualifikation."),
        ),
    ),
    _pairs(
        ARBEITSVERTRAG,
        "Was sind Sondervereinbarungen und Betriebsvereinbarungen?",
        (
            (
                "Sondervereinbarungen",
                "Individuelle Abmachungen zwischen Arbeitgeber und Arbeitnehmer.",
            ),
            (
                "Betriebsvereinbarungen",
                "Vereinbarungen zwischen Arbeitgeber und Betriebsrat, die für den Betrieb gelten.",
            ),
        ),
    ),
    _pairs(
        ARBEITSVERTRAG,
        "Was wird bezüglich der Arbeitszeit und Probezeit festgelegt?",
        (
            ("Arbeitszeit", "Wie viele Stunden und wann gearbeitet wird."),
            (
                "Probezeit",
                "Ein vereinbarter Zeitraum zum gegenseitigen Kennenlernen und "
                "Prüfen des Arbeitsverhältnisses.",
            ),
        ),
    ),
    _single(
        ARBEITSVERTRAG,
        "Was ist ein befristeter Arbeitsvertrag?",
        "Ein Arbeitsvertrag, der nur für einen bestimmten Zeitraum abgeschlossen "
        "wird und zu einem festgelegten Zeitpunkt endet.",
        (
            "Ein Arbeitsvertrag ohne festgelegtes Enddatum. Er ist zeitlich nicht begrenzt.",
            "Ein Arbeitsvertrag, der erst nach der Probezeit beginnt.",
            "Ein Arbeitsvertrag, der nur mündlich geschlossen wird.",
        ),
    ),
    _single(
        ARBEITSVERTRAG,
        "Wie lange darf ein Arbeitsvertrag bei einer Neueinstellung ohne Sachgrund "
        "maximal befristet werden?",
        "Maximal 2 Jahre. Innerhalb dieser Zeit darf er höchstens dreimal verlängert werden.",
        (
            "Maximal 1 Jahr. Innerhalb dieser Zeit darf er höchstens einmal verlängert werden.",
            "Maximal 2 Jahre. Innerhalb dieser Zeit darf er beliebig oft verlängert werden.",
            "Maximal 3 Jahre. Innerhalb dieser Zeit darf er höchstens zweimal verlängert werden.",
        ),
        3,
    ),
    _single(
        ARBEITSVERTRAG,
        "Was bedeutet eine Befristung aus sonstigen Gründen? Nenne ein Beispiel.",
        "Eine Befristung mit einem sachlichen Grund, beispielsweise eine "
        "Schwangerschaftsvertretung.",
        (
            "Eine Befristung ohne sachlichen Grund, beispielsweise bei einer Neueinstellung.",
            "Eine Befristung, die nur mündlich vereinbart wird.",
            "Eine Befristung, die nach Ablauf automatisch in ein unbefristetes "
            "Arbeitsverhältnis übergeht.",
        ),
        3,
    ),
    _single(
        ARBEITSVERTRAG,
        "Was ist ein unbefristeter Arbeitsvertrag?",
        "Ein Arbeitsvertrag ohne festgelegtes Enddatum. Er ist zeitlich nicht begrenzt.",
        (
            "Ein Arbeitsvertrag, der nur für einen bestimmten Zeitraum abgeschlossen "
            "wird und zu einem festgelegten Zeitpunkt endet.",
            "Ein Arbeitsvertrag, der nach zwei Jahren automatisch endet.",
            "Ein Arbeitsvertrag, der nur während der Probezeit gilt.",
        ),
    ),

    # --- Arbeitszeitgesetz ---------------------------------------------------
    _single(
        ARBEITSZEITGESETZ,
        "Wie viele Stunden darf ein Arbeitnehmer täglich grundsätzlich arbeiten?",
        "Grundsätzlich maximal 8 Stunden werktäglich.",
        (
            "Grundsätzlich maximal 6 Stunden werktäglich.",
            "Grundsätzlich maximal 10 Stunden werktäglich.",
            "Grundsätzlich maximal 12 Stunden werktäglich.",
        ),
        1,
    ),
    _single(
        ARBEITSZEITGESETZ,
        "Unter welchen Voraussetzungen darf die tägliche Arbeitszeit auf 10 Stunden "
        "verlängert werden?",
        "Wenn innerhalb von 6 Kalendermonaten oder 24 Wochen durchschnittlich "
        "8 Stunden werktäglich nicht überschritten werden.",
        (
            "Wenn der Arbeitnehmer der Verlängerung schriftlich zustimmt.",
            "Wenn innerhalb von 3 Monaten durchschnittlich 10 Stunden werktäglich "
            "erreicht werden.",
            "Wenn der Betrieb mehr als 15 Arbeitnehmer beschäftigt.",
        ),
        3,
    ),
    _single(
        ARBEITSZEITGESETZ,
        "Wie lange muss die Ruhezeit zwischen zwei Arbeitstagen mindestens betragen?",
        "Mindestens 11 Stunden ununterbrochen.",
        (
            "Mindestens 8 Stunden ununterbrochen.",
            "Mindestens 9 Stunden ununterbrochen.",
            "Mindestens 12 Stunden ununterbrochen.",
        ),
    ),
    _single(
        ARBEITSZEITGESETZ,
        "Zählt der Arbeitsweg zur gesetzlichen Ruhezeit?",
        "Ja. Der normale Arbeitsweg zählt nicht zur Arbeitszeit und liegt "
        "grundsätzlich innerhalb der Ruhezeit.",
        (
            "Nein. Der Arbeitsweg zählt zur Arbeitszeit.",
            "Nein. Der Arbeitsweg verlängert die Ruhezeit.",
            "Ja. Der Arbeitsweg zählt als Arbeitszeit und verlängert die Ruhezeit.",
        ),
    ),
    _single(
        ARBEITSZEITGESETZ,
        "Herr Huber arbeitet fünf Tage lang jeweils 10 Stunden. Unter welcher "
        "Voraussetzung ist das zulässig?",
        "Wenn innerhalb von 6 Kalendermonaten oder 24 Wochen der Durchschnitt von "
        "8 Stunden werktäglich eingehalten wird.",
        (
            "Wenn er an den fünf Tagen auf seine Ruhepausen verzichtet.",
            "Wenn sein Arbeitgeber die Überstunden nicht bezahlt.",
            "Wenn der Betrieb weniger als 15 Arbeitnehmer beschäftigt.",
        ),
        3,
    ),
    _single(
        ARBEITSZEITGESETZ,
        "Wie viele Stunden Freizeit stehen einem Arbeitnehmer nach einem Arbeitstag "
        "mindestens zu?",
        "Mindestens 11 Stunden ununterbrochene Ruhezeit.",
        (
            "Mindestens 8 Stunden ununterbrochene Ruhezeit.",
            "Mindestens 10 Stunden ununterbrochene Ruhezeit.",
            "Mindestens 12 Stunden ununterbrochene Ruhezeit.",
        ),
    ),
    _choice(
        ARBEITSZEITGESETZ,
        "Frau Schobert hat 8,5 Stunden gearbeitet. Wie lange war sie mindestens im "
        "Betrieb? Begründe deine Antwort.",
        (
            "Mindestens 9 Stunden.",
            "Bei mehr als 6 bis zu 9 Stunden Arbeitszeit sind mindestens 30 Minuten "
            "Ruhepause vorgeschrieben.",
            "Diese zählen nicht als Arbeitszeit.",
            "Mindestens 8,5 Stunden, weil die Ruhepause als Arbeitszeit zählt.",
            "Bei mehr als 6 bis zu 9 Stunden Arbeitszeit sind mindestens 45 Minuten "
            "Ruhepause vorgeschrieben.",
        ),
        [0, 1, 2],
        3,
    ),
    _sort(
        ARBEITSZEITGESETZ,
        "In welchen Berufen darf auch an Sonn- und Feiertagen gearbeitet werden? "
        "Nenne Beispiele.",
        ("Arbeit an Sonn- und Feiertagen erlaubt", "Keine Sonn- und Feiertagsarbeit vorgesehen"),
        (
            ("Not- und Rettungsdienste", "Arbeit an Sonn- und Feiertagen erlaubt"),
            ("Feuerwehr", "Arbeit an Sonn- und Feiertagen erlaubt"),
            ("Krankenhäuser und Pflegeeinrichtungen", "Arbeit an Sonn- und Feiertagen erlaubt"),
            ("Gastronomie", "Arbeit an Sonn- und Feiertagen erlaubt"),
            ("Landwirtschaft", "Arbeit an Sonn- und Feiertagen erlaubt"),
            ("Verkehrsbetriebe", "Arbeit an Sonn- und Feiertagen erlaubt"),
            ("Bürotätigkeit", "Keine Sonn- und Feiertagsarbeit vorgesehen"),
            ("Schulunterricht", "Keine Sonn- und Feiertagsarbeit vorgesehen"),
        ),
    ),
    _choice(
        ARBEITSZEITGESETZ,
        "Ab welcher Betriebsgröße besteht grundsätzlich ein gesetzlicher Anspruch "
        "auf Teilzeitarbeit?",
        (
            "Bei regelmäßig mehr als 15 Arbeitnehmern (mindestens 16).",
            "Zusätzlich muss das Arbeitsverhältnis länger als 6 Monate bestehen.",
            "Bei regelmäßig mehr als 10 Arbeitnehmern (mindestens 11).",
            "Das Arbeitsverhältnis muss länger als 2 Jahre bestehen.",
        ),
        [0, 1],
        3,
    ),
    _single(
        ARBEITSZEITGESETZ,
        "Herr Lutz verkürzt seine tägliche Arbeitszeit von 8 auf 6 Stunden. Sein "
        "Arbeitgeber zahlt ihm daraufhin 30 % weniger Gehalt. Ist das zulässig? "
        "Begründe deine Antwort.",
        "Nein, grundsätzlich nicht. Er reduziert seine Arbeitszeit um 25 %. Deshalb "
        "darf sein anteiliges Gehalt grundsätzlich ebenfalls nur um 25 % reduziert "
        "werden.",
        (
            "Ja, weil der Arbeitgeber das Gehalt frei festlegen darf.",
            "Ja, weil eine Reduktion um 30 % der Reduktion der Arbeitszeit entspricht.",
            "Nein, weil eine Teilzeitbeschäftigung grundsätzlich nicht zulässig ist.",
        ),
        3,
    ),
    _choice(
        ARBEITSZEITGESETZ,
        "Welche vier Themenbereiche werden im Zusammenhang mit der gesetzlichen "
        "Arbeitszeitregelung behandelt?",
        (
            "Tägliche Arbeitszeit",
            "Ruhepausen",
            "Ruhezeit",
            "Nacht- und Schichtarbeit",
            "Urlaubsanspruch",
            "Kündigungsfristen",
        ),
        [0, 1, 2, 3],
    ),
)


def seed_pug_questions(connection):
    """Insert every bank question that is not in the database yet.

    Existing rows are never touched: attempts and saved questions stay attached
    to them, and re-running is a no-op.
    """
    known = {
        row[0]
        for row in connection.execute(
            """SELECT t.name FROM topics t JOIN subjects s ON s.id = t.subject_id
               WHERE s.name = 'PuG'"""
        )
    }
    unknown = {question["topic"] for question in BANK} - known
    if unknown:
        raise RuntimeError(f"Unknown PuG topics in the bank: {sorted(unknown)}")

    stored = {
        (topic, text)
        for topic, text in connection.execute(
            """SELECT t.name, q.question_text
               FROM questions q
               JOIN topics t ON t.id = q.topic_id
               JOIN subjects s ON s.id = t.subject_id
               WHERE s.name = 'PuG'"""
        )
    }
    missing = [
        question for question in BANK
        if (question["topic"], question["text"]) not in stored
    ]
    if not missing:
        return

    connection.executemany(
        """INSERT INTO questions
               (topic_id, question_text, answer, hint, difficulty, question_type, alt_answers)
           SELECT t.id, ?, ?, ?, ?, ?, ?
           FROM topics t JOIN subjects s ON s.id = t.subject_id
           WHERE s.name = 'PuG' AND t.name = ?
             AND NOT EXISTS (
                 SELECT 1 FROM questions q
                 WHERE q.topic_id = t.id AND q.question_text = ?
             )""",
        [
            (
                question["text"], question["answer"], question["hint"],
                question["difficulty"], question["kind"], question["alt"],
                question["topic"], question["text"],
            )
            for question in missing
        ],
    )
