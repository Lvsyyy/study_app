"""The BS question bank and the reference information for the BS subject.

Every German sentence is taken from the BS course notes unchanged; only the
question wording, the interaction type and the wrong options are new. The
semantic markers of the notes ([definition], [merkmal], [advantage], ...) are
not stored, so the same sentence can be read as a bullet in the information
page and used as an answer.
"""
import json

BOOT = "Bootvorgang"
FIRMWARE = "BIOS und UEFI"
BIOS_UPDATE = "BIOS-Update"
FILESYSTEMS = "Dateisysteme"
NTFS_STRUCTURE = "NTFS-Struktur"
HDD = "Festplatten"
PARTITIONING = "Partitionierung"
VIRTUALISATION = "Virtualisierung"
USERS = "Benutzerkonten und Benutzergruppen"
PROFILES = "Benutzerprofile"

BS_TOPICS = (
    BOOT,
    FIRMWARE,
    BIOS_UPDATE,
    FILESYSTEMS,
    NTFS_STRUCTURE,
    HDD,
    PARTITIONING,
    VIRTUALISATION,
    USERS,
    PROFILES,
)

POST_DEF = (
    "Der Power-On Self-Test (POST) ist ein Selbsttest, der nach dem Einschalten des PCs durchgeführt wird. "
    "Beim Hochfahren wird überprüft, ob die grundlegenden Komponenten des Gerätes funktionsfähig sind."
)

POST_COMPONENTS = (
    "Die Funktionsfähigkeit der CPU wird während des POST überprüft.",
    "CPU-nahe Bausteine werden während des POST auf ihre Funktionsfähigkeit überprüft.",
    "Das CMOS-RAM wird während des POST auf seine Funktionsfähigkeit überprüft.",
    "Der CPU-nahe Cache-Speicher wird während des POST auf seine Funktionsfähigkeit überprüft.",
    "Die ersten 64 Kilobyte des Arbeitsspeichers werden während des POST überprüft.",
    "Der Grafikspeicher und die Grafik-Ausgabe werden während des POST überprüft.",
)

POST_ERRORS = (
    "Fehler werden häufig durch akustische oder visuelle Signale gemeldet.",
    "Ein visuelles Signal kann beispielsweise durch eine Kontrollleuchte am Mainboard angezeigt werden.",
    "Wenn das Grafiksystem bereits überprüft wurde, können Fehlermeldungen auf dem Bildschirm angezeigt werden.",
)

BOOT_STEPS = (
    "Zuerst wird der PC eingeschaltet, um den Bootvorgang zu starten.",
    "Anschließend wird das BIOS geladen.",
    "Danach wird der Selbsttest (POST) durchgeführt.",
    "Wenn die Hardware nicht funktionsfähig ist, wird eine Fehlermeldung ausgegeben.",
    "Nach einer Fehlermeldung (Hardware) wird eine Fehlerbeseitigung durchgeführt und der PC ausgeschaltet.",
    "Wenn die Hardware funktionsfähig ist, wird das CMOS gelesen.",
    "Anschließend wird die Grundkonfiguration der Komponenten eingelesen.",
    "Danach wird überprüft, ob ein Betriebssystem vorhanden ist.",
    "Wenn kein Betriebssystem vorhanden ist, wird eine Fehlermeldung ausgegeben.",
    "Nach einer Fehlermeldung (kein Betriebssystem) wird eine Fehlerbeseitigung durchgeführt und der PC ausgeschaltet.",
    "Wenn ein Betriebssystem vorhanden ist, wird dieses gestartet.",
    "Der Bootvorgang endet, sobald das Betriebssystem vollständig geladen wurde.",
)

BIOS_UPDATE_STEPS = (
    "Zuerst müssen das Mainboard und die installierte BIOS- beziehungsweise UEFI-Version identifiziert werden.",
    "Anschließend müssen die passenden Update-Dateien gefunden und heruntergeladen werden.",
    "Vor dem BIOS-Update sollte ein Datenbackup wichtiger Dateien erstellt werden.",
    "Danach muss die geeignete Update-Methode ausgewählt werden.",
    "Mögliche Update-Methoden sind Windows, das Flash-Menü des BIOS oder DOS bei älteren Hauptplatinen.",
    "Vor dem Update muss das BIOS vorbereitet und gegebenenfalls der Schreibschutz deaktiviert werden.",
    "Vor dem Update sollten die BIOS-Einstellungen gespeichert werden.",
    "Anschließend wird das BIOS-Update durchgeführt.",
    "Nach dem Update wird das CMOS gelöscht und die Stromversorgung getrennt.",
    "Bei Problemen kann versucht werden, das alte BIOS wiederherzustellen.",
)

ADMIN_ACCOUNT_STEPS = (
    "Öffnen Sie die Computerverwaltung und wechseln Sie zu Systemwerkzeuge.",
    "Öffnen Sie Lokale Benutzer und Gruppen und wählen Sie anschließend Benutzer aus.",
    "Öffnen Sie über einen Rechtsklick die Eigenschaften des gewünschten Benutzerkontos.",
    "Wechseln Sie zum Register „Mitglied von“ und wählen Sie „Hinzufügen“ aus.",
    "Fügen Sie die Gruppe Administratoren hinzu, damit das Benutzerkonto Administratorrechte erhält.",
)

NTFS = "NTFS"
FAT = "FAT"


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


def _answers(topic, text, answers, distractors, difficulty=2):
    """Multi-select whose right options are the complete `answers` tuple."""
    return _choice(topic, text, [*answers, *distractors], range(len(answers)), difficulty)


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
            "cards": [{"text": card, "category": category} for card, category in cards],
        },
        "table_sort", difficulty,
    )


def _order(topic, text, items, difficulty=2):
    return _question(topic, text, {"items": list(items)}, "ordering", difficulty)


CHECKED = "Wird während des POST geprüft"
NOT_CHECKED = "Wird nicht während des POST geprüft"

BANK = (
    # --- Bootvorgang ---------------------------------------------------------
    _single(
        BOOT,
        "Was versteht man unter dem POST?",
        POST_DEF,
        (
            "Der POST prüft die digitalen Signaturen der Startdateien und verhindert den Start "
            "nicht vertrauenswürdiger Software.",
            "Der POST liest die Partitionstabelle und startet anschließend den Bootloader des Betriebssystems.",
            "Der POST legt die Bootreihenfolge der Datenträger im CMOS fest.",
        ),
    ),
    _sort(
        BOOT,
        "Welche Komponenten werden während des POST auf ihre Funktionsfähigkeit überprüft?",
        (CHECKED, NOT_CHECKED),
        (
            *((component, CHECKED) for component in POST_COMPONENTS),
            ("Das Betriebssystem wird während des POST vollständig geladen.", NOT_CHECKED),
            ("Die Benutzerprofile werden während des POST geladen.", NOT_CHECKED),
            ("Die installierte BIOS-Version wird während des POST aktualisiert.", NOT_CHECKED),
        ),
    ),
    _answers(
        BOOT,
        "Wie werden Fehler gemeldet, die während des POST festgestellt werden?",
        POST_ERRORS,
        (
            "Fehler werden ausschließlich per E-Mail an den Hersteller gemeldet.",
            "Fehler werden ausschließlich im Ereignisprotokoll von Windows gespeichert.",
            "Fehler werden erst nach dem vollständigen Start des Betriebssystems gemeldet.",
        ),
    ),
    _order(
        BOOT,
        "Welche Schritte werden beim Start eines PCs durchgeführt?",
        BOOT_STEPS,
        3,
    ),

    # --- BIOS und UEFI -------------------------------------------------------
    _pairs(
        FIRMWARE,
        "Welche Speicherstruktur verwendet das BIOS, welche UEFI?",
        (
            ("BIOS", "Master Boot Record (MBR)"),
            ("UEFI", "GUID Partition Table (GPT)"),
        ),
    ),
    _pairs(
        FIRMWARE,
        "Wofür stehen die Abkürzungen BIOS und UEFI?",
        (
            ("BIOS", "Basic Input/Output System; ermöglicht die Steuerung der Eingaben und Ausgaben des Systems"),
            (
                "UEFI",
                "Unified Extensible Firmware Interface; erweiterbare Firmware-Schnittstelle mit grafischer "
                "Bedienoberfläche",
            ),
        ),
    ),
    _answers(
        FIRMWARE,
        "Welche Bedeutung haben BIOS und UEFI für einen PC?",
        (
            "BIOS und UEFI bereiten die Hardware für den Start des Betriebssystems vor.",
            "BIOS und UEFI übernehmen die grundlegende Hardwarekonfiguration vor dem Start des Betriebssystems.",
        ),
        (
            "BIOS und UEFI installieren die Treiber für alle angeschlossenen Geräte.",
            "BIOS und UEFI verwalten die Benutzerkonten des Betriebssystems.",
            "BIOS und UEFI sichern die Benutzerprofile auf einem Server.",
        ),
    ),
    _answers(
        FIRMWARE,
        "Welche Aufgaben werden von BIOS und UEFI während des Bootvorgangs ausgeführt?",
        (
            "BIOS und UEFI führen den POST zur Überprüfung der grundlegenden Hardwarekomponenten durch.",
            "BIOS und UEFI initialisieren die Hardwarekomponenten während des Bootvorgangs.",
            "BIOS und UEFI laden den Bootloader, damit das Betriebssystem gestartet werden kann.",
            "BIOS und UEFI übernehmen die Systemkonfiguration während des Bootvorgangs.",
        ),
        (
            "BIOS und UEFI starten die Anwendungsprogramme des Benutzers.",
            "BIOS und UEFI verwalten die Dateien auf der Festplatte.",
        ),
    ),
    _answers(
        FIRMWARE,
        "Welche Vorteile bietet UEFI gegenüber BIOS?",
        (
            "UEFI bietet mit Secure Boot eine zusätzliche Sicherheitsfunktion für den Startvorgang.",
            "UEFI bietet bessere Sicherheitsmöglichkeiten gegenüber dem klassischen BIOS.",
            "UEFI ermöglicht schnellere Bootzeiten gegenüber dem klassischen BIOS.",
            "UEFI bietet eine umfangreichere Unterstützung moderner Hardware.",
            "UEFI bietet eine bessere Kompatibilität mit modernen Systemen.",
        ),
        (
            "UEFI unterstützt als Speicherstruktur ausschließlich den Master Boot Record.",
            "UEFI benötigt eine Diskette mit dem BIOS-Update.",
        ),
    ),
    _single(
        FIRMWARE,
        "Was ist der Unterschied zwischen EFI und UEFI?",
        "EFI war ursprünglich eine herstellerspezifische Firmware-Schnittstelle für die "
        "64-Bit-Itanium-Architektur. UEFI ist eine standardisierte Weiterentwicklung der EFI-Spezifikation.",
        (
            "EFI ist die standardisierte Weiterentwicklung von UEFI und wird nur auf 32-Bit-Systemen verwendet.",
            "EFI und UEFI sind zwei Namen für dieselbe Firmware-Schnittstelle ohne inhaltliche Unterschiede.",
            "EFI ist eine Partitionstabelle, UEFI ist die zugehörige Firmware.",
        ),
        3,
    ),
    _pairs(
        FIRMWARE,
        "Was ist Secure Boot und welches Problem kann dadurch entstehen?",
        (
            (
                "Was macht Secure Boot?",
                "Es überprüft digitale Signaturen, um sicherzustellen, dass nur vertrauenswürdige Software "
                "gestartet wird.",
            ),
            (
                "Welches Problem kann entstehen?",
                "Veraltete Firmware kann Probleme mit der Unterstützung von Secure Boot verursachen.",
            ),
        ),
        3,
    ),
    _single(
        FIRMWARE,
        "Wie kann die Bootreihenfolge eines PCs verändert werden?",
        "Die Bootreihenfolge kann im Boot Priority Menü des BIOS beziehungsweise UEFI verändert werden.",
        (
            "Die Bootreihenfolge kann im Task-Manager unter Autostart verändert werden.",
            "Die Bootreihenfolge kann in der Systemsteuerung unter Programme und Features verändert werden.",
            "Die Bootreihenfolge kann über den Geräte-Manager verändert werden.",
        ),
        1,
    ),

    # --- BIOS-Update ---------------------------------------------------------
    _single(
        BIOS_UPDATE,
        "Wie kann man die installierte BIOS-Version identifizieren?",
        "Die installierte BIOS-Version kann unter Windows über die Systeminformationen mit dem Befehl "
        "MsInfo32 identifiziert werden.",
        (
            "Die installierte BIOS-Version kann unter Windows über den Task-Manager auf dem Register "
            "Leistung identifiziert werden.",
            "Die installierte BIOS-Version kann über die Datenträgerverwaltung identifiziert werden.",
            "Die installierte BIOS-Version kann über den Geräte-Manager unter Firmware identifiziert werden.",
        ),
        1,
    ),
    _order(
        BIOS_UPDATE,
        "Welche Schritte sind bei einem BIOS-Update durchzuführen?",
        BIOS_UPDATE_STEPS,
        3,
    ),
    _single(
        BIOS_UPDATE,
        "Wann sollte bei einem BIOS-Update ein Backup erstellt werden?",
        "Ein Datenbackup sollte erstellt werden, wenn wichtige Daten vorhanden sind, die nicht verloren "
        "gehen dürfen.",
        (
            "Ein Datenbackup sollte immer erst nach dem BIOS-Update erstellt werden.",
            "Ein Datenbackup ist nur bei einem Wechsel des Mainboards erforderlich.",
            "Ein Datenbackup ist bei einem BIOS-Update grundsätzlich nicht möglich.",
        ),
    ),
    _answers(
        BIOS_UPDATE,
        "Warum ist ein Datenbackup bei einem fehlgeschlagenen BIOS-Update sinnvoll, obwohl keine Daten "
        "verloren gehen können?",
        (
            "Nach einem fehlgeschlagenen BIOS-Update kann es passieren, dass der PC nicht mehr funktioniert.",
            "Mit einem vorhandenen Datenbackup ist ein sofortiger Zugriff auf die gesicherten Daten möglich, "
            "beispielsweise über die Festplatte.",
        ),
        (
            "Ein Datenbackup verhindert, dass das BIOS-Update fehlschlägt.",
            "Ohne Datenbackup wird das BIOS-Update vom Hersteller nicht freigegeben.",
        ),
        3,
    ),
    _answers(
        BIOS_UPDATE,
        "Welche drei Möglichkeiten gibt es, ein BIOS-Update durchzuführen?",
        (
            "Ein BIOS-Update kann direkt über Windows durchgeführt werden.",
            "Ein BIOS-Update kann direkt über das UEFI durchgeführt werden.",
            "Ein BIOS-Update kann unter DOS durchgeführt werden.",
        ),
        (
            "Ein BIOS-Update kann über den Task-Manager durchgeführt werden.",
            "Ein BIOS-Update kann über die Datenträgerverwaltung durchgeführt werden.",
        ),
    ),

    # --- Dateisysteme --------------------------------------------------------
    _answers(
        FILESYSTEMS,
        "Warum werden Dateisysteme benötigt?",
        (
            "Dateisysteme ermöglichen das sinnvolle Ablegen und Ordnen von Dateien auf einem Speichermedium.",
            "Dateisysteme setzen die Speicherung von Nullen und Einsen in eine strukturierte Verwaltung von "
            "Dateien und Dateinamen um.",
        ),
        (
            "Dateisysteme erhöhen die Übertragungsgeschwindigkeit der Netzwerkkarte.",
            "Dateisysteme verschlüsseln grundsätzlich jede Datei automatisch.",
        ),
    ),
    _single(
        FILESYSTEMS,
        "Nennen Sie die beiden wichtigsten Dateisysteme in der Windows-Welt.",
        "Die beiden wichtigsten Dateisysteme in der Windows-Welt sind NTFS und FAT.",
        (
            "Die beiden wichtigsten Dateisysteme in der Windows-Welt sind NTFS und MFT.",
            "Die beiden wichtigsten Dateisysteme in der Windows-Welt sind FAT und GPT.",
            "Die beiden wichtigsten Dateisysteme in der Windows-Welt sind EFS und MBR.",
        ),
        1,
    ),
    _sort(
        FILESYSTEMS,
        "Ordnen Sie die Größenangaben dem passenden Dateisystem zu.",
        (NTFS, FAT),
        (
            ("Maximale Dateigröße von bis zu 16 TByte", NTFS),
            ("Maximale Dateigröße von 4 GB", FAT),
            ("Partitionsgrößen von bis zu 256 TByte", NTFS),
            ("Partitionsgrößen von bis zu 32 GB", FAT),
        ),
        3,
    ),
    _answers(
        FILESYSTEMS,
        "Warum kann mit dem NTFS-Dateisystem der vorhandene Speicherplatz besser genutzt werden als mit dem "
        "FAT-Dateisystem?",
        (
            "FAT verwendet teilweise größere Cluster als NTFS, wodurch kleine Dateien mehr Speicherplatz "
            "belegen können.",
            "Bei FAT wird immer ein vollständiger Cluster für eine Datei belegt, auch wenn die Datei kleiner "
            "als der Cluster ist.",
        ),
        (
            "NTFS speichert jede Datei ohne Cluster direkt in der Partitionstabelle.",
            "FAT komprimiert jede Datei automatisch und belegt dadurch mehr Speicherplatz.",
        ),
    ),
    _single(
        FILESYSTEMS,
        "In einem Office-Dokument erscheint die Meldung „Diese Datei stammt von einem Internetspeicherort“. "
        "Welches Dateisystem verwendet der PC?",
        "Der PC verwendet NTFS, da die Information über die Herkunft einer Datei zu den Dateiattributen gehört.",
        (
            "Der PC verwendet FAT, da die Information über die Herkunft einer Datei zu den Dateiattributen "
            "gehört.",
            "Der PC verwendet NTFS, da die Meldung aus der Master File Table stammt.",
            "Der PC verwendet FAT, da FAT die Herkunft einer Datei speichert.",
        ),
        3,
    ),
    _answers(
        FILESYSTEMS,
        "Welche Vorteile bietet NTFS gegenüber FAT hinsichtlich der Sicherheit?",
        (
            "NTFS ermöglicht die Verschlüsselung von Dateien mithilfe des Encrypting File System (EFS).",
            "NTFS ermöglicht die Einstellung von Zugriffsrechten für bestimmte Benutzer und Benutzergruppen.",
        ),
        (
            "FAT verschlüsselt Dateien automatisch mit dem Encrypting File System (EFS).",
            "NTFS schützt Dateien, indem es sie grundsätzlich schreibgeschützt speichert.",
        ),
    ),

    # --- NTFS-Struktur -------------------------------------------------------
    _single(
        NTFS_STRUCTURE,
        "Warum können gelöschte Dateien häufig wiederhergestellt werden?",
        "Gelöschte Dateien werden häufig nur als gelöscht markiert und bleiben so lange vorhanden, bis ihre "
        "Speicherbereiche überschrieben werden.",
        (
            "Gelöschte Dateien werden sofort vollständig von der Festplatte entfernt.",
            "Gelöschte Dateien werden automatisch in der Master File Table gesichert.",
            "Gelöschte Dateien werden vom Dateisystem in das Benutzerprofil verschoben.",
        ),
        3,
    ),
    _answers(
        NTFS_STRUCTURE,
        "Was ist in der Master File Table (MFT) eingetragen?",
        (
            "Die Master File Table enthält Einträge zu Dateien und deren zugehörigen Attributen.",
            "Kleine Dateien können direkt in der MFT gespeichert werden, sofern sie ungefähr 800 Bytes nicht "
            "überschreiten.",
            "Bei größeren Dateien enthält die MFT einen Verweis auf die Cluster, in denen die Datei gespeichert "
            "ist.",
            "Die MFT enthält unter anderem den Dateinamen und weitere Attribute wie Berechtigungen und "
            "Erstellungsdatum.",
        ),
        (
            "Die MFT enthält die BIOS-Einstellungen des Mainboards.",
            "Die MFT enthält die Bootreihenfolge des PCs.",
        ),
    ),
    _answers(
        NTFS_STRUCTURE,
        "Was versteht man unter einem Cluster-Zeiger?",
        (
            "Ein Cluster-Zeiger verweist auf das Start-Cluster einer Datei und gibt die Anzahl der von der "
            "Datei belegten Cluster an.",
            "Bei fragmentierten Dateien wird für jedes Fragment ein eigener Cluster-Zeiger angelegt.",
        ),
        (
            "Ein Cluster-Zeiger enthält die digitalen Signaturen der Startdateien.",
            "Ein Cluster-Zeiger legt die Clustergröße des Dateisystems fest.",
        ),
    ),
    _pairs(
        NTFS_STRUCTURE,
        "Ordnen Sie die Begriffe den passenden Beschreibungen zu.",
        (
            (
                "Master File Table (MFT)",
                "Enthält Einträge zu Dateien und deren zugehörigen Attributen.",
            ),
            (
                "Cluster-Zeiger",
                "Verweist auf das Start-Cluster einer Datei und gibt die Anzahl der belegten Cluster an.",
            ),
        ),
    ),

    # --- Festplatten ---------------------------------------------------------
    _answers(
        HDD,
        "Was gehört zu einer Festplatte (HDD)?",
        (
            "Zu den Komponenten einer Festplatte gehören die Platter und die Spindel.",
            "Zu den Komponenten einer Festplatte gehören der Aktorarm und die Schreib-/Leseköpfe.",
            "Zu den Komponenten einer Festplatte gehören der Aktor und die Aktorachse.",
            "Zu den Komponenten einer Festplatte gehören die Schnittstelle, das Jumperfeld und die "
            "Stromversorgung.",
        ),
        (
            "Zu den Komponenten einer Festplatte gehören der Touchscreen und die Webcam.",
            "Zu den Komponenten einer Festplatte gehören Tastatur und Maus.",
        ),
    ),
    _pairs(
        HDD,
        "Ordnen Sie die Begriffe rund um den Aufbau einer Festplatte den passenden Beschreibungen zu.",
        (
            ("Spur (Track)", "Schmale, ringförmige Streifen auf jeder Plattenseite einer Festplatte."),
            ("Sektor (Block)", "Abschnitt einer Spur, in dem später Daten gespeichert werden."),
            (
                "Zylinder (Cylinder)",
                "Spuren aller Plattenseiten, die jeweils dieselbe Spurnummer besitzen.",
            ),
            ("Cluster", "Der kleinste Speicherbereich, der von einem Dateisystem genutzt werden kann."),
        ),
        3,
    ),
    _single(
        HDD,
        "Was sind Spuren (Tracks)?",
        "Spuren sind schmale, ringförmige Streifen auf jeder Plattenseite einer Festplatte. Die Spur 0 "
        "befindet sich immer am äußeren Rand der Platte. Die Spur mit der höchsten Nummer befindet sich an "
        "der Achse der Platte.",
        (
            "Spuren sind die Köpfe, mit denen die Daten von der Platte gelesen werden.",
            "Spuren sind die Stromanschlüsse an der Rückseite der Festplatte.",
            "Spuren sind die Partitionen, in die eine Festplatte aufgeteilt wird.",
        ),
        3,
    ),
    _single(
        HDD,
        "Was sind Sektoren (Sectors beziehungsweise Blöcke)?",
        "Jede Spur einer Festplatte ist in Abschnitte unterteilt, in denen später Daten gespeichert werden. "
        "Diese Abschnitte werden als Sektoren beziehungsweise Blöcke bezeichnet.",
        (
            "Sektoren sind die ringförmigen Streifen auf einer Plattenseite.",
            "Sektoren sind die Bereiche, in denen die Firmware die BIOS-Einstellungen speichert.",
            "Sektoren sind die Partitionen einer Festplatte.",
        ),
        3,
    ),
    _single(
        HDD,
        "Was versteht man unter einem Zylinder (Cylinder)?",
        "Ein Zylinder besteht aus den Spuren aller Plattenseiten, die jeweils dieselbe Spurnummer besitzen. "
        "Zum Zylinder 0 gehören die Spuren 0 auf den Ober- und Unterseiten aller vorhandenen Platten.",
        (
            "Ein Zylinder ist ein einzelner Sektor auf der Unterseite der ersten Platte.",
            "Ein Zylinder ist die Gesamtheit aller Partitionen einer Festplatte.",
            "Ein Zylinder ist der Motor, der die Platter antreibt.",
        ),
        3,
    ),
    _answers(
        HDD,
        "Was versteht man bei einer Festplatte unter einem Kopf (Head)?",
        (
            "Die Elektronik des Laufwerks wählt einen Schreib-/Lesekopf aus und interagiert nur mit diesem "
            "ausgewählten Kopf.",
            "Alle anderen Tracks des jeweiligen Zylinders werden währenddessen ignoriert.",
        ),
        (
            "Alle Köpfe eines Zylinders lesen gleichzeitig dieselben Daten.",
            "Der Kopf legt die Clustergröße des Dateisystems fest.",
        ),
        3,
    ),
    _answers(
        HDD,
        "Was versteht man bei Festplatten unter Clustern?",
        (
            "Ein Cluster ist der kleinste Speicherbereich, der von einem Dateisystem genutzt werden kann.",
            "Cluster sind Verbünde aus mehreren Sektoren mit einer festgelegten Größe.",
            "Moderne Betriebssysteme verwenden beispielsweise Clustergrößen von 4 oder 8 kB.",
            "Cluster bilden die kleinste Zuordnungseinheit eines Dateisystems.",
        ),
        (
            "Ein Cluster ist immer genau ein Sektor.",
            "Cluster werden ausschließlich von der Firmware des Mainboards verwaltet.",
        ),
        3,
    ),
    _single(
        HDD,
        "Warum kann die Geschwindigkeit einer Festplatte, insbesondere die Zugriffszeit, nicht beliebig "
        "gesteigert werden?",
        "Festplatten bestehen aus beweglichen Teilen, deren Geschwindigkeit durch physikalische und materielle "
        "Grenzen eingeschränkt wird. Diese physikalischen und materiellen Grenzen müssen bei der "
        "Leistungssteigerung einer Festplatte berücksichtigt werden.",
        (
            "Festplatten bestehen ausschließlich aus elektronischen Bauteilen, deren Geschwindigkeit durch die "
            "Firmware begrenzt wird.",
            "Die Zugriffszeit wird ausschließlich vom Dateisystem begrenzt.",
            "Die Zugriffszeit wird ausschließlich von der Anzahl der Partitionen begrenzt.",
        ),
        3,
    ),
    _answers(
        HDD,
        "Welche Faktoren beeinflussen die Zugriffszeit einer Festplatte?",
        (
            "Die Suchzeit (Average Seek Time) beeinflusst die Zugriffszeit einer Festplatte.",
            "Die Zugriffsverzögerung durch Umdrehung (Average Rotational Latency Time) beeinflusst ebenfalls "
            "die Zugriffszeit einer Festplatte.",
        ),
        (
            "Die Anzahl der Partitionen beeinflusst die Zugriffszeit einer Festplatte.",
            "Die Clustergröße des Dateisystems bestimmt die Zugriffszeit einer Festplatte.",
        ),
        3,
    ),
    _pairs(
        HDD,
        "Beschreiben Sie die Suchzeit und die Zugriffsverzögerung durch Umdrehung.",
        (
            (
                "Suchzeit",
                "Die Zeit, die der Schwungarm benötigt, um die gewünschte Spur zu erreichen.",
            ),
            (
                "Zugriffsverzögerung durch Umdrehung",
                "Die Wartezeit, bis der Schreib-/Lesekopf den gewünschten Block erreicht; sie hängt "
                "ausschließlich von der Drehgeschwindigkeit der Scheiben ab.",
            ),
        ),
        3,
    ),
    _pairs(
        HDD,
        "Wie werden die Kapazität einer Scheibe, die Größe einer Spur und die Gesamtkapazität einer "
        "Festplatte berechnet?",
        (
            (
                "Kapazität einer Scheibe",
                "Alle relevanten Werte außer der Anzahl der Köpfe miteinander multiplizieren und das Ergebnis "
                "mit 512 Byte pro Sektor multiplizieren.",
            ),
            (
                "Größe einer Spur",
                "63 Sektoren pro Spur mit 512 Byte pro Sektor multiplizieren.",
            ),
            (
                "Gesamtkapazität einer Festplatte",
                "Alle relevanten Werte einschließlich der Anzahl der Köpfe miteinander multiplizieren; die "
                "Anzahl der Sektoren wird mit jeweils 512 Byte pro Sektor berücksichtigt.",
            ),
        ),
        3,
    ),

    # --- Partitionierung -----------------------------------------------------
    _answers(
        PARTITIONING,
        "Beschreiben Sie eine primäre Partition.",
        (
            "Eine primäre Partition ist ein abgegrenzter Bereich einer Festplatte, von dem ein Betriebssystem "
            "gestartet beziehungsweise gebootet werden kann.",
            "Bei einer MBR-partitionierten Festplatte sind maximal vier primäre Partitionen möglich.",
        ),
        (
            "Bei einer MBR-partitionierten Festplatte sind beliebig viele primäre Partitionen möglich.",
            "Eine primäre Partition ist ein Container für logische Partitionen.",
        ),
    ),
    _answers(
        PARTITIONING,
        "Beschreiben Sie eine aktive Partition.",
        (
            "Eine aktive Partition enthält die Startdateien des Betriebssystems.",
            "Die aktive Partition ermöglicht das Starten des PCs.",
            "Bei einer MBR-partitionierten Festplatte kann eine primäre Partition als aktiv gekennzeichnet sein.",
        ),
        (
            "Eine aktive Partition ist immer eine logische Partition.",
            "Eine aktive Partition enthält ausschließlich Benutzerdaten.",
        ),
    ),
    _answers(
        PARTITIONING,
        "Beschreiben Sie eine erweiterte Partition.",
        (
            "Eine erweiterte Partition ist nur bei der Partitionierung mit MBR vorgesehen.",
            "Eine erweiterte Partition wird benötigt, wenn eine Festplatte in mehr als vier Partitionen "
            "aufgeteilt werden soll.",
            "Eine erweiterte Partition kann in mehrere logische Partitionen aufgeteilt werden.",
            "Die erweiterte Partition selbst ist nicht bootfähig.",
            "Die erweiterte Partition dient als Container für logische Partitionen und wird nicht wie eine "
            "normale Datenpartition verwendet.",
        ),
        ("Eine erweiterte Partition ist nur bei der Partitionierung mit GPT vorgesehen.",),
        3,
    ),
    _answers(
        PARTITIONING,
        "Beschreiben Sie eine logische Partition.",
        (
            "Eine logische Partition ist ein eigener Bereich innerhalb einer erweiterten Partition und kann "
            "ein eigenes Laufwerk bilden.",
            "Eine logische Partition ist bei der hier behandelten MBR-Partitionierung nicht direkt bootfähig.",
        ),
        (
            "Eine logische Partition kann nur mit GPT angelegt werden.",
            "Eine logische Partition enthält zwingend die Startdateien des Betriebssystems.",
        ),
    ),
    _pairs(
        PARTITIONING,
        "Nennen Sie zwei weitere Partitionstypen und beschreiben Sie ihre Funktion.",
        (
            (
                "Systempartition",
                "Enthält die Dateien, die zum Starten des Betriebssystems benötigt werden; der Bootloader "
                "befindet sich auf ihr.",
            ),
            ("Startpartition", "Die Partition, auf der das Betriebssystem installiert ist."),
        ),
    ),
    _sort(
        PARTITIONING,
        "Welche Unterschiede bestehen zwischen MBR und GPT bei der Partitionierung?",
        ("MBR", "GPT"),
        (
            ("Maximal vier primäre Partitionen", "MBR"),
            ("Festplatten mit einer Größe von bis zu 2 TB", "MBR"),
            ("Wird typischerweise zusammen mit BIOS verwendet", "MBR"),
            ("Maximal 128 Partitionen unter Windows", "GPT"),
            ("Festplatten mit einer Größe von bis zu 18 EB", "GPT"),
            ("Wird typischerweise zusammen mit UEFI verwendet", "GPT"),
            ("Ist zuverlässiger als MBR", "GPT"),
        ),
        3,
    ),

    # --- Virtualisierung -----------------------------------------------------
    _single(
        VIRTUALISATION,
        "Was versteht man unter einem virtuellen PC?",
        "Ein virtueller PC ist ein softwarebasierter Computer, der innerhalb einer Virtualisierungssoftware "
        "ausgeführt wird. Für einen virtuellen PC ist kein zusätzlicher physischer Computer erforderlich.",
        (
            "Ein virtueller PC ist ein physischer Computer, der über das Netzwerk gestartet wird.",
            "Ein virtueller PC ist eine Partition, auf der ein zweites Betriebssystem installiert ist.",
            "Ein virtueller PC ist ein Benutzerprofil, das auf einem Server gespeichert wird.",
        ),
        3,
    ),
    _answers(
        VIRTUALISATION,
        "Beschreiben Sie drei Vorteile bei der Verwendung von virtuellen Maschinen (VMs).",
        (
            "Durch Virtualisierung können Hardwarekosten eingespart werden, da mehrere virtuelle Server auf "
            "einer physischen Hardware betrieben werden können.",
            "Die Hardwarekonfiguration einer virtuellen Maschine kann einfach geändert werden, ohne das "
            "Betriebssystem vollständig neu installieren zu müssen.",
            "Ältere Betriebssysteme und Programme können mithilfe virtueller Maschinen auf neuer Hardware "
            "betrieben werden.",
        ),
        (
            "Eine virtuelle Maschine benötigt grundsätzlich keinen Arbeitsspeicher des Hosts.",
            "Eine virtuelle Maschine kann ohne Virtualisierungssoftware gestartet werden.",
        ),
        3,
    ),
    _answers(
        VIRTUALISATION,
        "Nennen Sie drei Virtualisierungsplattformen.",
        (
            "VirtualBox ist eine Virtualisierungsplattform zur Erstellung und Ausführung virtueller Maschinen.",
            "VMware ist eine Virtualisierungsplattform zur Erstellung und Ausführung virtueller Maschinen.",
            "Hyper-V ist eine Virtualisierungsplattform von Microsoft zur Erstellung und Ausführung virtueller "
            "Maschinen.",
        ),
        (
            "MsInfo32 ist eine Virtualisierungsplattform von Microsoft.",
            "Der Task-Manager ist eine Virtualisierungsplattform.",
        ),
    ),
    _answers(
        VIRTUALISATION,
        "Welche Funktionen werden von VirtualBox unterstützt?",
        (
            "VirtualBox unterstützt das Erstellen und Wiederherstellen von Snapshots virtueller Maschinen.",
            "VirtualBox unterstützt Drag-and-drop zwischen Host und Gast.",
            "VirtualBox unterstützt eine gemeinsame Zwischenablage zwischen Host und Gast.",
            "VirtualBox unterstützt gemeinsam genutzte Ordner zwischen Host und Gast.",
            "VirtualBox unterstützt das Einbinden von USB-Geräten in virtuelle Maschinen.",
        ),
        ("VirtualBox unterstützt das Partitionieren der physischen Festplatte des Hosts.",),
        3,
    ),
    _single(
        VIRTUALISATION,
        "Was versteht man unter einem Snapshot?",
        "Ein Snapshot speichert den aktuellen Zustand einer virtuellen Maschine, sodass dieser Zustand später "
        "wiederhergestellt werden kann.",
        (
            "Ein Snapshot ist eine Sicherungskopie der Firmware des Mainboards.",
            "Ein Snapshot ist ein Abbild der physischen Festplatte des Hosts.",
            "Ein Snapshot ist eine Partition, die nur bei MBR verwendet wird.",
        ),
        1,
    ),
    _single(
        VIRTUALISATION,
        "Wozu dienen Shared Folders?",
        "Shared Folders sind gemeinsam genutzte Ordner, über die Daten zwischen dem Host OS und dem Guest OS "
        "ausgetauscht werden können.",
        (
            "Shared Folders sind Ordner, in denen das BIOS seine Einstellungen speichert.",
            "Shared Folders sind Ordner, in denen Windows die Benutzerprofile ablegt.",
            "Shared Folders sind Ordner, in denen die Master File Table gespeichert wird.",
        ),
        1,
    ),
    _single(
        VIRTUALISATION,
        "Was ist der Unterschied zwischen VMware Workstation Player und VMware Workstation Pro?",
        "VMware Workstation Player verzichtet im Vergleich zu VMware Workstation Pro auf die Snapshot-Funktion.",
        (
            "VMware Workstation Player unterstützt im Vergleich zu VMware Workstation Pro zusätzlich die "
            "Snapshot-Funktion.",
            "VMware Workstation Pro verzichtet im Vergleich zum Player auf die Snapshot-Funktion.",
            "Beide Versionen unterstützen die Snapshot-Funktion im gleichen Umfang.",
        ),
    ),
    _answers(
        VIRTUALISATION,
        "Welche Nachteile hat Hyper-V?",
        (
            "Bei Hyper-V ist kein flüssiger Wechsel des Mauszeigers zwischen dem Hauptbetriebssystem und der "
            "virtuellen Maschine möglich.",
            "Ältere Betriebssysteme können Schwierigkeiten mit der von Hyper-V emulierten Hardware haben.",
        ),
        (
            "Hyper-V unterstützt keine virtuellen Maschinen.",
            "Hyper-V kann nur unter Linux betrieben werden.",
        ),
    ),
    _answers(
        VIRTUALISATION,
        "Nennen Sie zwei Vorteile von Hyper-V.",
        (
            "Hyper-V unterstützt eine dynamische Arbeitsspeicherverwaltung für virtuelle Maschinen.",
            "Hyper-V bietet Skalierbarkeit und ermöglicht den parallelen Betrieb mehrerer virtueller Maschinen.",
        ),
        (
            "Hyper-V benötigt keinen Arbeitsspeicher für das Hauptbetriebssystem.",
            "Hyper-V ersetzt die Benutzerkontensteuerung von Windows.",
        ),
    ),
    _pairs(
        VIRTUALISATION,
        "Was versteht man unter Host OS und Guest OS?",
        (
            ("Host OS", "Das Betriebssystem, das direkt auf der physischen Hardware läuft."),
            (
                "Guest OS",
                "Das Betriebssystem, das innerhalb einer virtuellen Maschine auf der emulierten beziehungsweise "
                "virtualisierten Hardware läuft.",
            ),
        ),
    ),
    _single(
        VIRTUALISATION,
        "Was sind Gasterweiterungen und wo werden sie installiert?",
        "Gasterweiterungen (Guest Additions) sind zusätzliche Softwarekomponenten, die die Leistung und "
        "Integration einer virtuellen Maschine mit dem Host OS verbessern. Sie werden innerhalb des Guest OS "
        "einer virtuellen Maschine installiert.",
        (
            "Gasterweiterungen sind zusätzliche Hardwarekomponenten, die auf dem Mainboard installiert werden.",
            "Gasterweiterungen sind Firmware-Updates, die im BIOS installiert werden.",
            "Gasterweiterungen sind Partitionen, die auf der physischen Festplatte installiert werden.",
        ),
        3,
    ),
    _pairs(
        VIRTUALISATION,
        "Nennen Sie zwei bereitgestellte Gasterweiterungen.",
        (
            (
                "Shared Folders",
                "Ermöglichen den gemeinsamen Zugriff auf Ordner zwischen Host und Guest OS.",
            ),
            (
                "Shared Clipboard",
                "Ermöglicht die gemeinsame Nutzung der Zwischenablage zwischen Host und Guest OS.",
            ),
        ),
        1,
    ),
    _single(
        VIRTUALISATION,
        "Sie müssen den Arbeitsspeicher Ihrer VM festlegen. Was müssen Sie beachten?",
        "Der einer virtuellen Maschine zugewiesene Arbeitsspeicher steht dem Host OS während des Betriebs des "
        "Guest OS nicht zur Verfügung.",
        (
            "Der einer virtuellen Maschine zugewiesene Arbeitsspeicher steht dem Host OS zusätzlich zur "
            "Verfügung.",
            "Der Arbeitsspeicher einer virtuellen Maschine wird immer dynamisch aus der Festplatte bezogen.",
            "Der Arbeitsspeicher einer virtuellen Maschine wird in der Master File Table verwaltet.",
        ),
        3,
    ),
    _pairs(
        VIRTUALISATION,
        "Ordnen Sie die virtuellen Festplattenformate den jeweiligen Plattformen zu.",
        (
            ("Virtual Disk Image (VDI)", "VirtualBox"),
            ("Virtual Machine Disk (VMDK)", "VMware"),
            ("Virtual Hard Disk (VHD)", "Microsoft Hyper-V"),
        ),
    ),
    _sort(
        VIRTUALISATION,
        "Welche Vor- und Nachteile haben feste und dynamisch alloziierte virtuelle Festplatten?",
        ("Feste virtuelle Festplatte", "Dynamisch allozierte virtuelle Festplatte"),
        (
            ("Ist etwas schneller als eine dynamisch allozierte virtuelle Festplatte", "Feste virtuelle Festplatte"),
            (
                "Bei einer festen virtuellen Festplatte ist keine nachträgliche Vergrößerung der ursprünglich "
                "festgelegten Größe erforderlich",
                "Feste virtuelle Festplatte",
            ),
            (
                "Eine feste virtuelle Festplatte benötigt sofort den gesamten festgelegten Speicherplatz",
                "Feste virtuelle Festplatte",
            ),
            (
                "Eine feste virtuelle Festplatte belegt bereits bei der Erstellung den Speicherplatz für ihre "
                "maximale Größe",
                "Feste virtuelle Festplatte",
            ),
            (
                "Eine dynamisch allozierte virtuelle Festplatte benötigt zunächst nur wenig Speicherplatz",
                "Dynamisch allozierte virtuelle Festplatte",
            ),
            (
                "Eine dynamisch allozierte virtuelle Festplatte wächst mit dem tatsächlichen Speicherbedarf",
                "Dynamisch allozierte virtuelle Festplatte",
            ),
            (
                "Eine dynamisch allozierte virtuelle Festplatte ist etwas langsamer als eine feste virtuelle "
                "Festplatte",
                "Dynamisch allozierte virtuelle Festplatte",
            ),
            (
                "Der benötigte Speicherplatz einer dynamisch allozierten virtuellen Festplatte kann im Laufe der "
                "Zeit stark anwachsen",
                "Dynamisch allozierte virtuelle Festplatte",
            ),
            (
                "Eine dynamisch allozierte virtuelle Festplatte wird bei geringerem Datenbestand nicht "
                "automatisch verkleinert",
                "Dynamisch allozierte virtuelle Festplatte",
            ),
        ),
        3,
    ),
    _pairs(
        VIRTUALISATION,
        "Nach der Erstellung einer VM sehen Sie drei Dateien. Nennen Sie die Dateiformate und beschreiben Sie "
        "ihre Funktion.",
        (
            (
                ".vbox",
                "Enthält die Einstellungen des virtuellen PCs beziehungsweise des Gast-Systems.",
            ),
            (".vbox-prev", "Enthält eine vorherige Version der zugehörigen .vbox-Datei."),
            (".vdi", "Enthält die virtuelle Festplatte des virtuellen PCs."),
        ),
        1,
    ),

    # --- Benutzerkonten und Benutzergruppen ----------------------------------
    _answers(
        USERS,
        "Nennen Sie drei Möglichkeiten, ein lokales Benutzerkonto grafisch hinzuzufügen.",
        (
            "Ein lokales Benutzerkonto kann über die Systemsteuerung unter Benutzerkonten hinzugefügt werden.",
            "Ein lokales Benutzerkonto kann über die Computerverwaltung unter System, Lokale Benutzer und "
            "Gruppen und Benutzer hinzugefügt werden.",
            "Ein lokales Benutzerkonto kann über die Windows-Einstellungen unter Konten hinzugefügt werden.",
        ),
        (
            "Ein lokales Benutzerkonto kann über den Task-Manager unter Autostart hinzugefügt werden.",
            "Ein lokales Benutzerkonto kann über die Datenträgerverwaltung hinzugefügt werden.",
        ),
        1,
    ),
    _pairs(
        USERS,
        "Nennen Sie die zwei Kontotypen und beschreiben Sie diese.",
        (
            (
                "Standardbenutzer",
                "Kann die meisten Programme verwenden und Einstellungen ändern, die sich nur auf das eigene "
                "Benutzerkonto auswirken.",
            ),
            (
                "Administrator",
                "Besitzt weitreichende Verwaltungsrechte, kann die Einstellungen des gesamten Computers ändern "
                "und auf Dateien und Apps zugreifen, die auf dem PC gespeichert sind.",
            ),
        ),
        1,
    ),
    _answers(
        USERS,
        "Beschreiben Sie die Funktionsweise der Benutzerkontensteuerung.",
        (
            "Die Benutzerkontensteuerung sorgt dafür, dass administrative Änderungen nur mit den entsprechenden "
            "Rechten durchgeführt werden können.",
            "Die Ausführung administrativer Aktionen muss über ein Dialogfeld bestätigt werden.",
            "Administrative Aktionen können dadurch nicht unbemerkt im Hintergrund ausgeführt werden.",
        ),
        (
            "Die Benutzerkontensteuerung vergibt automatisch Administratorrechte an jedes neu erstellte Konto.",
            "Die Benutzerkontensteuerung verschlüsselt die Benutzerprofile mit EFS.",
        ),
        3,
    ),
    _answers(
        USERS,
        "Ein älteres Programm benötigt Administratorrechte. Welches Problem kann dabei entstehen und wie lässt "
        "es sich lösen?",
        (
            "Ältere Programme sind möglicherweise nicht entsprechend gekennzeichnet und werden deshalb von der "
            "Benutzerkontensteuerung nicht als Programme erkannt, die Administratorrechte benötigen.",
            "Solche Programme werden dadurch möglicherweise nur mit Standardrechten ausgeführt.",
            "Das Programm kann über einen Rechtsklick und die Auswahl von „Als Administrator ausführen“ mit "
            "Administratorrechten gestartet werden.",
        ),
        (
            "Die Benutzerkontensteuerung erteilt älteren Programmen automatisch Administratorrechte.",
            "Ältere Programme können grundsätzlich nicht mit Administratorrechten gestartet werden.",
        ),
        3,
    ),
    _pairs(
        USERS,
        "Nennen Sie die vier Einstellungen der Benutzerkontensteuerung.",
        (
            (
                "Always notify me when",
                "Benachrichtigt den Benutzer, wenn Apps versuchen, Software zu installieren oder Änderungen am "
                "Computer vorzunehmen, und auch, wenn er selbst Änderungen an den Windows-Einstellungen vornimmt.",
            ),
            (
                "Notify me only when apps try to make changes to my computer (default)",
                "Benachrichtigt den Benutzer nur, wenn Apps Änderungen am Computer vornehmen möchten; bei "
                "eigenen Änderungen an den Windows-Einstellungen erfolgt keine Benachrichtigung.",
            ),
            (
                "Notify me only when apps try to make changes to my computer (do not dim my desktop)",
                "Benachrichtigt den Benutzer nur bei Änderungsversuchen durch Apps, ohne den Desktop "
                "abzudunkeln; bei eigenen Änderungen an den Windows-Einstellungen erfolgt keine "
                "Benachrichtigung.",
            ),
            (
                "Never notify me when",
                "Deaktiviert Benachrichtigungen, wenn Apps Software installieren oder Änderungen am Computer "
                "vornehmen möchten; auch bei eigenen Änderungen an den Windows-Einstellungen erfolgen keine "
                "Benachrichtigungen.",
            ),
        ),
        3,
    ),
    _answers(
        USERS,
        "Wofür werden Benutzergruppen verwendet?",
        (
            "Benutzergruppen dienen dazu, Rechte, Zugriffsberechtigungen und die Zugehörigkeit von Benutzern zu "
            "Gruppen zu verwalten.",
            "Berechtigungen können mehreren Benutzern gleichzeitig über eine Benutzergruppe zugewiesen werden.",
            "Benutzergruppen vereinfachen die Verwaltung von Benutzern und deren Berechtigungen.",
        ),
        ("Benutzergruppen ersetzen die Benutzerkontensteuerung vollständig.",),
    ),
    _answers(
        USERS,
        "Was versteht man unter lokalen Gruppen?",
        (
            "Lokale Gruppen sind Benutzergruppen, die nur auf einem bestimmten Computer existieren.",
            "Lokale Gruppen haben keine Auswirkungen auf andere Computer.",
            "Lokale Gruppen können nicht exportiert oder importiert werden.",
            "Windows verfügt auf jedem Computer über lokale Gruppen.",
        ),
        ("Lokale Gruppen werden zentral auf einem Server verwaltet.",),
    ),
    _answers(
        USERS,
        "Welche Rechte hat ein Mitglied der Gruppe Administratoren?",
        (
            "Mitglieder der Gruppe Administratoren besitzen umfassende Verwaltungsrechte auf dem Computer.",
            "Die Gruppe Administratoren verfügt über die höchsten regulären Verwaltungsrechte in Windows.",
            "Administratoren können auf dem Computer grundsätzlich auch auf geschützte Daten zugreifen.",
        ),
        ("Mitglieder der Gruppe Administratoren dürfen nur ihre eigenen Dateien lesen.",),
    ),
    _single(
        USERS,
        "Wie kommt ein Benutzer in die Gruppe Benutzer?",
        "Ein lokaler oder Domänenbenutzer wird bei seiner Erstellung automatisch der Gruppe Benutzer zugeordnet.",
        (
            "Ein Benutzer muss der Gruppe Benutzer in der Computerverwaltung manuell hinzugefügt werden.",
            "Ein Benutzer wird der Gruppe Benutzer erst bei der ersten Anmeldung zugeordnet.",
            "Ein Benutzer wird der Gruppe Benutzer nur als Administrator zugeordnet.",
        ),
        1,
    ),
    _order(
        USERS,
        "Sie haben in der Computerverwaltung ein neues Benutzerkonto angelegt. Wie können Sie dieses Konto zu "
        "einem Administratorkonto machen?",
        ADMIN_ACCOUNT_STEPS,
        3,
    ),
    _answers(
        USERS,
        "Was versteht man unter dem Access-Token?",
        (
            "Ein Access-Token enthält die SID des Benutzers sowie die SIDs der Benutzergruppen, denen der "
            "Benutzer angehört.",
            "Das Access-Token enthält Informationen über die Berechtigungen, die dem angemeldeten Benutzer "
            "zugeordnet sind.",
        ),
        (
            "Das Access-Token enthält die BIOS-Einstellungen des Computers.",
            "Das Access-Token wird dauerhaft in der Master File Table gespeichert.",
        ),
        3,
    ),
    _single(
        USERS,
        "Wann wird das Access-Token erstellt?",
        "Das Access-Token wird beim Anmelden eines Benutzers erstellt.",
        (
            "Das Access-Token wird beim Start des Computers erstellt.",
            "Das Access-Token wird bei der Installation von Windows erstellt.",
            "Das Access-Token wird beim Abmelden eines Benutzers erstellt.",
        ),
        1,
    ),

    # --- Benutzerprofile -----------------------------------------------------
    _answers(
        PROFILES,
        "Erklären Sie, was man unter einem Benutzerprofil versteht.",
        (
            "Ein Benutzerprofil ist die individuelle Konfiguration und Benutzerumgebung eines Benutzerkontos.",
            "Jeder Benutzer, der sich an einem Rechner anmeldet, besitzt eine eigene Benutzerumgebung.",
            "Der Sinn eines Benutzerprofils besteht darin, dass jeder Benutzer seine Umgebung nach den eigenen "
            "Bedürfnissen konfigurieren kann.",
            "Änderungen eines Benutzers wirken sich nur auf dessen eigenes Benutzerprofil aus; andere "
            "Benutzerprofile bleiben von den Änderungen eines Benutzers unberührt.",
            "Benutzer können grundsätzlich nur auf Dateien und E-Mails zugreifen, für die sie die "
            "entsprechenden Berechtigungen besitzen.",
        ),
        (
            "Ein Benutzerprofil gilt für alle Benutzer eines Computers gemeinsam.",
            "Ein Benutzerprofil wird bereits bei der Installation von Windows für jeden Benutzer angelegt.",
        ),
        3,
    ),
    _answers(
        PROFILES,
        "Welche Bestandteile gehören zur Benutzerumgebung eines Benutzerprofils?",
        (
            "Der Desktop und das Hintergrundbild.",
            "Die eigenen Dateien.",
            "Favoriten, das Aussehen der Fenster und der Bildschirmschoner.",
            "Einstellungen für E-Mailsoftware und weitere benutzerspezifische Konfigurationen.",
        ),
        (
            "Die BIOS-Einstellungen des Mainboards.",
            "Die Partitionstabelle der Festplatte.",
        ),
    ),
    _single(
        PROFILES,
        "Wann wird das Benutzerprofil erstellt?",
        "Ein Benutzerprofil wird bei der ersten Anmeldung des Benutzers am Rechner erstellt.",
        (
            "Ein Benutzerprofil wird bei jeder Anmeldung des Benutzers neu erstellt.",
            "Ein Benutzerprofil wird beim Anlegen des Benutzerkontos in der Computerverwaltung erstellt.",
            "Ein Benutzerprofil wird beim Start des Computers erstellt.",
        ),
        1,
    ),
    _single(
        PROFILES,
        "Wo werden lokale Benutzerprofile gespeichert?",
        "Lokale Benutzerprofile werden standardmäßig im Verzeichnis C:\\Users\\{Benutzername} gespeichert.",
        (
            "Lokale Benutzerprofile werden standardmäßig im Verzeichnis C:\\Windows\\System32 gespeichert.",
            "Lokale Benutzerprofile werden standardmäßig im Verzeichnis C:\\Program Files gespeichert.",
            "Lokale Benutzerprofile werden standardmäßig im Verzeichnis C:\\ProgramData\\Users gespeichert.",
        ),
        1,
    ),
    _answers(
        PROFILES,
        "Was gehört zu einem lokalen Benutzerprofil?",
        (
            "Das Hauptverzeichnis eines lokalen Benutzerprofils befindet sich unter C:\\Users\\<Benutzername>.",
            "Der Ordner Desktop enthält die Dateien und Verknüpfungen des Benutzerdesktops.",
            "Der Ordner Documents enthält die persönlichen Dokumente des Benutzers.",
            "Der Ordner Downloads enthält heruntergeladene Dateien des Benutzers.",
            "Der Ordner Pictures enthält die Bilder des Benutzers.",
            "Der Ordner Videos enthält die Videos des Benutzers.",
            "Der Ordner Music enthält die Musikdateien des Benutzers.",
            "Der Ordner AppData enthält anwendungsbezogene und benutzerspezifische Einstellungen und Daten.",
            "Der Ordner OneDrive kann die lokal eingebundenen beziehungsweise synchronisierten "
            "OneDrive-Dateien enthalten.",
            "C:\\Users\\Public ist ein öffentliches Benutzerverzeichnis, das mehreren Benutzern zur Verfügung "
            "steht.",
        ),
        ("Der Ordner System32 enthält die Benutzerprofile aller Benutzer.",),
        3,
    ),
    _pairs(
        PROFILES,
        "Worauf verweisen die Umgebungsvariablen %USERPROFILE%, %APPDATA%, %LOCALAPPDATA% und %TEMP%?",
        (
            ("%USERPROFILE%", "Verweist auf das Profilverzeichnis des aktuell angemeldeten Benutzers."),
            (
                "%APPDATA%",
                "Verweist standardmäßig auf den Roaming-Unterordner AppData des Benutzerprofils.",
            ),
            ("%LOCALAPPDATA%", "Verweist auf den Local-Unterordner AppData des Benutzerprofils."),
            ("%TEMP%", "Verweist auf das temporäre Verzeichnis des Benutzers."),
        ),
        3,
    ),
    _answers(
        PROFILES,
        "Beschreiben Sie servergespeicherte Benutzerprofile.",
        (
            "Servergespeicherte Benutzerprofile werden auch als Roamingbenutzerprofile bezeichnet.",
            "Das Benutzerprofil wird auf einem Server gespeichert.",
            "Bei der Anmeldung wird das servergespeicherte Benutzerprofil auf den Computer heruntergeladen.",
            "Änderungen am Benutzerprofil werden beim Abmelden mit dem Server synchronisiert.",
        ),
        ("Servergespeicherte Benutzerprofile werden nur lokal auf dem Computer gespeichert.",),
        3,
    ),
    _answers(
        PROFILES,
        "Welche Vorteile bieten servergespeicherte Benutzerprofile?",
        (
            "Benutzer benötigen auf jedem Computer kein vollständig neues Benutzerprofil.",
            "Ein servergespeichertes Benutzerprofil kann auf mehreren Computern verwendet werden.",
            "Änderungen am Benutzerprofil werden beim Abmelden automatisch mit dem Server synchronisiert.",
        ),
        (
            "Servergespeicherte Benutzerprofile machen ein lokales Benutzerkonto überflüssig.",
            "Servergespeicherte Benutzerprofile benötigen keinen Server.",
        ),
    ),
)


def _bullets(items):
    return "\n".join(f"• {item}" for item in items)


ABBREVIATIONS_BOOT = (
    "BIOS = Basic Input/Output System",
    "CMOS = Complementary Metal Oxide Semiconductor",
    "CPU = Central Processing Unit",
    "POST = Power On Self Test",
)

ABBREVIATIONS_FIRMWARE = (
    "MBR = Master Boot Record",
    "GPT = GUID Partition Table",
    "UEFI = Unified Extensible Firmware Interface",
    "EFI = Extensible Firmware Interface",
)

ABBREVIATIONS_FILESYSTEMS = (
    "NTFS = New Technology File System",
    "FAT = File Allocation Table",
    "EFS = Encrypting File System",
)

ABBREVIATIONS_NTFS = ("MFT = Master File Table",)

BS_INFOS = (
    # --- Bootvorgang ---------------------------------------------------------
    ("BS", BOOT, "POST", _bullets((
        "Der Power-On Self-Test (POST) ist ein Selbsttest, der nach dem Einschalten des PCs durchgeführt wird.",
        "Beim Hochfahren wird überprüft, ob die grundlegenden Komponenten des Gerätes funktionsfähig sind.",
    ))),
    ("BS", BOOT, "Ablauf des POST", _bullets(POST_COMPONENTS)),
    ("BS", BOOT, "Fehlererkennung und Fehlermeldungen", _bullets(POST_ERRORS)),
    ("BS", BOOT, "Ablauf des Bootvorgangs", _bullets(BOOT_STEPS)),
    ("BS", BOOT, "Abkürzungen", _bullets(ABBREVIATIONS_BOOT)),

    # --- BIOS und UEFI -------------------------------------------------------
    ("BS", FIRMWARE, "Speicherstrukturen", _bullets((
        "Das BIOS verwendet den Master Boot Record (MBR) als Speicherstruktur für die Partitionierung.",
        "UEFI verwendet die GUID Partition Table (GPT) als Speicherstruktur für die Partitionierung.",
    ))),
    ("BS", FIRMWARE, "BIOS und UEFI Grundlagen", _bullets((
        "BIOS steht für Basic Input/Output System und ermöglicht die Steuerung der Eingaben und Ausgaben des "
        "Systems.",
        "UEFI steht für Unified Extensible Firmware Interface und stellt eine erweiterbare "
        "Firmware-Schnittstelle mit grafischer Bedienoberfläche bereit.",
        "BIOS und UEFI bereiten die Hardware für den Start des Betriebssystems vor.",
        "BIOS und UEFI übernehmen die grundlegende Hardwarekonfiguration vor dem Start des Betriebssystems.",
    ))),
    ("BS", FIRMWARE, "Aufgaben beim Booten", _bullets((
        "BIOS und UEFI führen den POST zur Überprüfung der grundlegenden Hardwarekomponenten durch.",
        "BIOS und UEFI initialisieren die Hardwarekomponenten während des Bootvorgangs.",
        "BIOS und UEFI laden den Bootloader, damit das Betriebssystem gestartet werden kann.",
        "BIOS und UEFI übernehmen die Systemkonfiguration während des Bootvorgangs.",
    ))),
    ("BS", FIRMWARE, "BIOS vs. UEFI", _bullets((
        "UEFI bietet mit Secure Boot eine zusätzliche Sicherheitsfunktion für den Startvorgang.",
        "UEFI bietet bessere Sicherheitsmöglichkeiten gegenüber dem klassischen BIOS.",
        "UEFI ermöglicht schnellere Bootzeiten gegenüber dem klassischen BIOS.",
        "UEFI bietet eine umfangreichere Unterstützung moderner Hardware.",
        "UEFI bietet eine bessere Kompatibilität mit modernen Systemen.",
        "EFI war ursprünglich eine herstellerspezifische Firmware-Schnittstelle für die "
        "64-Bit-Itanium-Architektur.",
        "UEFI ist eine standardisierte Weiterentwicklung der EFI-Spezifikation.",
    ))),
    ("BS", FIRMWARE, "Secure Boot", _bullets((
        "Secure Boot überprüft digitale Signaturen, um sicherzustellen, dass nur vertrauenswürdige Software "
        "gestartet wird.",
        "Veraltete Firmware kann Probleme mit der Unterstützung von Secure Boot verursachen.",
    ))),
    ("BS", FIRMWARE, "Bootreihenfolge", _bullets((
        "Die Bootreihenfolge kann im Boot Priority Menü des BIOS beziehungsweise UEFI verändert werden.",
    ))),
    ("BS", FIRMWARE, "Abkürzungen", _bullets(ABBREVIATIONS_FIRMWARE)),

    # --- BIOS-Update ---------------------------------------------------------
    ("BS", BIOS_UPDATE, "BIOS-Version identifizieren", _bullets((
        "Die installierte BIOS-Version kann unter Windows über die Systeminformationen mit dem Befehl "
        "MsInfo32 identifiziert werden.",
    ))),
    ("BS", BIOS_UPDATE, "Vorbereitung und Durchführung", _bullets(BIOS_UPDATE_STEPS)),
    ("BS", BIOS_UPDATE, "Backup und Wiederherstellung", _bullets((
        "Ein Datenbackup sollte erstellt werden, wenn wichtige Daten vorhanden sind, die nicht verloren gehen "
        "dürfen.",
        "Nach einem fehlgeschlagenen BIOS-Update kann es passieren, dass der PC nicht mehr funktioniert.",
        "Mit einem vorhandenen Datenbackup ist ein sofortiger Zugriff auf die gesicherten Daten möglich, "
        "beispielsweise über die Festplatte.",
    ))),
    ("BS", BIOS_UPDATE, "Update-Methoden", _bullets((
        "Ein BIOS-Update kann direkt über Windows durchgeführt werden.",
        "Ein BIOS-Update kann direkt über das UEFI durchgeführt werden.",
        "Ein BIOS-Update kann unter DOS durchgeführt werden.",
    ))),

    # --- Dateisysteme --------------------------------------------------------
    ("BS", FILESYSTEMS, "Grundlagen", _bullets((
        "Dateisysteme ermöglichen das sinnvolle Ablegen und Ordnen von Dateien auf einem Speichermedium.",
        "Dateisysteme setzen die Speicherung von Nullen und Einsen in eine strukturierte Verwaltung von Dateien "
        "und Dateinamen um.",
        "Die beiden wichtigsten Dateisysteme in der Windows-Welt sind NTFS und FAT.",
    ))),
    ("BS", FILESYSTEMS, "NTFS und FAT", _bullets((
        "NTFS unterstützt laut den vorliegenden Lernunterlagen eine maximale Dateigröße von bis zu 16 TByte.",
        "FAT unterstützt laut den vorliegenden Lernunterlagen eine maximale Dateigröße von 4 GB.",
        "NTFS unterstützt laut den vorliegenden Lernunterlagen Partitionsgrößen von bis zu 256 TByte.",
        "FAT unterstützt laut den vorliegenden Lernunterlagen Partitionsgrößen von bis zu 32 GB.",
    ))),
    ("BS", FILESYSTEMS, "Speicherplatz und Cluster", _bullets((
        "FAT verwendet teilweise größere Cluster als NTFS, wodurch kleine Dateien mehr Speicherplatz belegen "
        "können.",
        "Bei FAT wird immer ein vollständiger Cluster für eine Datei belegt, auch wenn die Datei kleiner als "
        "der Cluster ist.",
    ))),
    ("BS", FILESYSTEMS, "Dateiattribute und Sicherheit", _bullets((
        "Der PC verwendet NTFS, da die Information über die Herkunft einer Datei zu den Dateiattributen gehört.",
        "NTFS ermöglicht die Verschlüsselung von Dateien mithilfe des Encrypting File System (EFS).",
        "NTFS ermöglicht die Einstellung von Zugriffsrechten für bestimmte Benutzer und Benutzergruppen.",
    ))),
    ("BS", FILESYSTEMS, "Abkürzungen", _bullets(ABBREVIATIONS_FILESYSTEMS)),

    # --- NTFS-Struktur -------------------------------------------------------
    ("BS", NTFS_STRUCTURE, "Wiederherstellung gelöschter Dateien", _bullets((
        "Gelöschte Dateien werden häufig nur als gelöscht markiert und bleiben so lange vorhanden, bis ihre "
        "Speicherbereiche überschrieben werden.",
    ))),
    ("BS", NTFS_STRUCTURE, "Master File Table (MFT)", _bullets((
        "Die Master File Table enthält Einträge zu Dateien und deren zugehörigen Attributen.",
        "Kleine Dateien können direkt in der MFT gespeichert werden, sofern sie ungefähr 800 Bytes nicht "
        "überschreiten.",
        "Bei größeren Dateien enthält die MFT einen Verweis auf die Cluster, in denen die Datei gespeichert ist.",
        "Die MFT enthält unter anderem den Dateinamen und weitere Attribute wie Berechtigungen und "
        "Erstellungsdatum.",
        "Wenn eine Datei zu groß für die direkte Speicherung in der MFT ist, wird dort ein Cluster-Zeiger "
        "angelegt.",
    ))),
    ("BS", NTFS_STRUCTURE, "Cluster-Zeiger", _bullets((
        "Ein Cluster-Zeiger verweist auf das Start-Cluster einer Datei und gibt die Anzahl der von der Datei "
        "belegten Cluster an.",
        "Bei fragmentierten Dateien wird für jedes Fragment ein eigener Cluster-Zeiger angelegt.",
    ))),
    ("BS", NTFS_STRUCTURE, "Abkürzungen", _bullets(ABBREVIATIONS_NTFS)),

    # --- Festplatten ---------------------------------------------------------
    ("BS", HDD, "Aufbau einer Festplatte", _bullets((
        "Eine Festplatte besteht aus mehreren mechanischen und elektronischen Komponenten.",
        "Zu den Komponenten einer Festplatte gehören die Platter und die Spindel.",
        "Zu den Komponenten einer Festplatte gehören der Aktorarm und die Schreib-/Leseköpfe.",
        "Zu den Komponenten einer Festplatte gehören der Aktor und die Aktorachse.",
        "Zu den Komponenten einer Festplatte gehören die Schnittstelle, das Jumperfeld und die Stromversorgung.",
    ))),
    ("BS", HDD, "Spuren, Sektoren, Zylinder und Köpfe", _bullets((
        "Spuren sind schmale, ringförmige Streifen auf jeder Plattenseite einer Festplatte.",
        "Die Spur 0 befindet sich immer am äußeren Rand der Platte.",
        "Die Spur mit der höchsten Nummer befindet sich an der Achse der Platte.",
        "Jede Spur einer Festplatte ist in Abschnitte unterteilt, in denen später Daten gespeichert werden.",
        "Diese Abschnitte werden als Sektoren beziehungsweise Blöcke bezeichnet.",
        "Ein Zylinder besteht aus den Spuren aller Plattenseiten, die jeweils dieselbe Spurnummer besitzen.",
        "Zum Zylinder 0 gehören die Spuren 0 auf den Ober- und Unterseiten aller vorhandenen Platten.",
        "Die Elektronik des Laufwerks wählt einen Schreib-/Lesekopf aus und interagiert nur mit diesem "
        "ausgewählten Kopf.",
        "Alle anderen Tracks des jeweiligen Zylinders werden währenddessen ignoriert.",
    ))),
    ("BS", HDD, "Cluster", _bullets((
        "Ein oder mehrere Sektoren werden zu sogenannten Clustern zusammengefasst.",
        "Ein Cluster ist der kleinste Speicherbereich, der von einem Dateisystem genutzt werden kann.",
        "Cluster sind Verbünde aus mehreren Sektoren mit einer festgelegten Größe.",
        "Moderne Betriebssysteme verwenden beispielsweise Clustergrößen von 4 oder 8 kB.",
        "Cluster bilden die kleinste Zuordnungseinheit eines Dateisystems.",
    ))),
    ("BS", HDD, "Zugriffszeit und Festplattengeschwindigkeit", _bullets((
        "Festplatten bestehen aus beweglichen Teilen, deren Geschwindigkeit durch physikalische und materielle "
        "Grenzen eingeschränkt wird.",
        "Diese physikalischen und materiellen Grenzen müssen bei der Leistungssteigerung einer Festplatte "
        "berücksichtigt werden.",
        "Die Suchzeit (Average Seek Time) beeinflusst die Zugriffszeit einer Festplatte.",
        "Die Zugriffsverzögerung durch Umdrehung (Average Rotational Latency Time) beeinflusst ebenfalls die "
        "Zugriffszeit einer Festplatte.",
        "Die Suchzeit beschreibt die Zeit, die der Schwungarm benötigt, um die gewünschte Spur zu erreichen.",
        "Die Zugriffsverzögerung durch Umdrehung beschreibt die Wartezeit, bis der Schreib-/Lesekopf den "
        "gewünschten Block erreicht.",
        "Die Zugriffsverzögerung durch Umdrehung hängt ausschließlich von der Drehgeschwindigkeit der Scheiben ab.",
    ))),
    ("BS", HDD, "Kapazitätsberechnung", _bullets((
        "Zur Berechnung der Kapazität einer Scheibe werden alle relevanten Werte außer der Anzahl der Köpfe "
        "miteinander multipliziert.",
        "Anschließend wird das Ergebnis mit 512 Byte pro Sektor multipliziert.",
        "Die Größe einer Spur wird berechnet, indem die 63 Sektoren pro Spur mit 512 Byte pro Sektor "
        "multipliziert werden.",
        "Zur Berechnung der Gesamtkapazität werden alle relevanten Werte einschließlich der Anzahl der Köpfe "
        "miteinander multipliziert.",
        "Die Anzahl der Sektoren wird dabei mit jeweils 512 Byte pro Sektor berücksichtigt.",
    ))),

    # --- Partitionierung -----------------------------------------------------
    ("BS", PARTITIONING, "Primäre und aktive Partitionen", _bullets((
        "Eine primäre Partition ist ein abgegrenzter Bereich einer Festplatte, von dem ein Betriebssystem "
        "gestartet beziehungsweise gebootet werden kann.",
        "Bei einer MBR-partitionierten Festplatte sind maximal vier primäre Partitionen möglich.",
        "Eine aktive Partition enthält die Startdateien des Betriebssystems.",
        "Die aktive Partition ermöglicht das Starten des PCs.",
        "Bei einer MBR-partitionierten Festplatte kann eine primäre Partition als aktiv gekennzeichnet sein.",
    ))),
    ("BS", PARTITIONING, "Erweiterte und logische Partitionen", _bullets((
        "Eine erweiterte Partition ist nur bei der Partitionierung mit MBR vorgesehen.",
        "Eine erweiterte Partition wird benötigt, wenn eine Festplatte in mehr als vier Partitionen aufgeteilt "
        "werden soll.",
        "Eine erweiterte Partition kann in mehrere logische Partitionen aufgeteilt werden.",
        "Die erweiterte Partition selbst ist nicht bootfähig.",
        "Die erweiterte Partition dient als Container für logische Partitionen und wird nicht wie eine normale "
        "Datenpartition verwendet.",
        "Eine logische Partition ist ein eigener Bereich innerhalb einer erweiterten Partition und kann ein "
        "eigenes Laufwerk bilden.",
        "Eine logische Partition ist bei der hier behandelten MBR-Partitionierung nicht direkt bootfähig.",
    ))),
    ("BS", PARTITIONING, "Weitere Partitionstypen", _bullets((
        "Die Systempartition enthält die Dateien, die zum Starten des Betriebssystems benötigt werden.",
        "Der Bootloader befindet sich auf der Systempartition.",
        "Die Startpartition ist die Partition, auf der das Betriebssystem installiert ist.",
    ))),
    ("BS", PARTITIONING, "MBR und GPT", _bullets((
        "MBR steht für Master Boot Record und unterstützt maximal vier primäre Partitionen.",
        "MBR unterstützt in der hier behandelten Standarddarstellung Festplatten mit einer Größe von bis zu 2 TB.",
        "MBR wird typischerweise zusammen mit BIOS verwendet.",
        "GPT steht für GUID Partition Table und unterstützt unter Windows maximal 128 Partitionen.",
        "GPT unterstützt in der hier behandelten Lernunterlage Festplatten mit einer Größe von bis zu 18 EB.",
        "GPT wird typischerweise zusammen mit UEFI verwendet.",
        "GPT ist zuverlässiger als MBR.",
    ))),

    # --- Virtualisierung -----------------------------------------------------
    ("BS", VIRTUALISATION, "Virtuelle PCs und Vorteile", _bullets((
        "Ein virtueller PC ist ein softwarebasierter Computer, der innerhalb einer Virtualisierungssoftware "
        "ausgeführt wird.",
        "Für einen virtuellen PC ist kein zusätzlicher physischer Computer erforderlich.",
        "Durch Virtualisierung können Hardwarekosten eingespart werden, da mehrere virtuelle Server auf einer "
        "physischen Hardware betrieben werden können.",
        "Die Hardwarekonfiguration einer virtuellen Maschine kann einfach geändert werden, ohne das "
        "Betriebssystem vollständig neu installieren zu müssen.",
        "Ältere Betriebssysteme und Programme können mithilfe virtueller Maschinen auf neuer Hardware "
        "betrieben werden.",
    ))),
    ("BS", VIRTUALISATION, "Virtualisierungsplattformen", _bullets((
        "VirtualBox ist eine Virtualisierungsplattform zur Erstellung und Ausführung virtueller Maschinen.",
        "VMware ist eine Virtualisierungsplattform zur Erstellung und Ausführung virtueller Maschinen.",
        "Hyper-V ist eine Virtualisierungsplattform von Microsoft zur Erstellung und Ausführung virtueller "
        "Maschinen.",
    ))),
    ("BS", VIRTUALISATION, "VirtualBox-Funktionen", _bullets((
        "VirtualBox unterstützt das Erstellen und Wiederherstellen von Snapshots virtueller Maschinen.",
        "VirtualBox unterstützt Drag-and-drop zwischen Host und Gast.",
        "VirtualBox unterstützt eine gemeinsame Zwischenablage zwischen Host und Gast.",
        "VirtualBox unterstützt gemeinsam genutzte Ordner zwischen Host und Gast.",
        "VirtualBox unterstützt das Einbinden von USB-Geräten in virtuelle Maschinen.",
        "Ein Snapshot speichert den aktuellen Zustand einer virtuellen Maschine, sodass dieser Zustand später "
        "wiederhergestellt werden kann.",
        "Shared Folders sind gemeinsam genutzte Ordner, über die Daten zwischen dem Host OS und dem Guest OS "
        "ausgetauscht werden können.",
    ))),
    ("BS", VIRTUALISATION, "VMware und Hyper-V", _bullets((
        "VMware Workstation Player verzichtet im Vergleich zu VMware Workstation Pro auf die Snapshot-Funktion.",
        "Bei Hyper-V ist kein flüssiger Wechsel des Mauszeigers zwischen dem Hauptbetriebssystem und der "
        "virtuellen Maschine möglich.",
        "Ältere Betriebssysteme können Schwierigkeiten mit der von Hyper-V emulierten Hardware haben.",
        "Hyper-V unterstützt eine dynamische Arbeitsspeicherverwaltung für virtuelle Maschinen.",
        "Hyper-V bietet Skalierbarkeit und ermöglicht den parallelen Betrieb mehrerer virtueller Maschinen.",
    ))),
    ("BS", VIRTUALISATION, "Host OS und Guest OS", _bullets((
        "Das Host OS ist das Betriebssystem, das direkt auf der physischen Hardware läuft.",
        "Das Guest OS ist das Betriebssystem, das innerhalb einer virtuellen Maschine auf der emulierten "
        "beziehungsweise virtualisierten Hardware läuft.",
        "Gasterweiterungen (Guest Additions) sind zusätzliche Softwarekomponenten, die die Leistung und "
        "Integration einer virtuellen Maschine mit dem Host OS verbessern.",
        "Gasterweiterungen werden innerhalb des Guest OS einer virtuellen Maschine installiert.",
        "Shared Folders ermöglichen den gemeinsamen Zugriff auf Ordner zwischen Host und Guest OS.",
        "Shared Clipboard ermöglicht die gemeinsame Nutzung der Zwischenablage zwischen Host und Guest OS.",
    ))),
    ("BS", VIRTUALISATION, "VM-Arbeitsspeicher und virtuelle Festplatten", _bullets((
        "Der einer virtuellen Maschine zugewiesene Arbeitsspeicher steht dem Host OS während des Betriebs des "
        "Guest OS nicht zur Verfügung.",
        "Eine feste virtuelle Festplatte ist etwas schneller als eine dynamisch allozierte virtuelle Festplatte.",
        "Bei einer festen virtuellen Festplatte ist keine nachträgliche Vergrößerung der ursprünglich "
        "festgelegten Größe erforderlich.",
        "Eine feste virtuelle Festplatte benötigt sofort den gesamten festgelegten Speicherplatz.",
        "Eine dynamisch allozierte virtuelle Festplatte benötigt zunächst nur wenig Speicherplatz.",
        "Eine dynamisch allozierte virtuelle Festplatte wächst mit dem tatsächlichen Speicherbedarf.",
        "Eine dynamisch allozierte virtuelle Festplatte ist etwas langsamer als eine feste virtuelle Festplatte.",
        "Der benötigte Speicherplatz einer dynamisch allozierten virtuellen Festplatte kann im Laufe der Zeit "
        "stark anwachsen.",
        "Eine dynamisch allozierte virtuelle Festplatte wird bei geringerem Datenbestand nicht automatisch "
        "verkleinert.",
    ))),
    ("BS", VIRTUALISATION, "VM-Dateien und Festplattenformate", _bullets((
        "Virtual Disk Image (VDI) ist das virtuelle Festplattenformat von VirtualBox.",
        "Virtual Machine Disk (VMDK) ist ein virtuelles Festplattenformat von VMware.",
        "Virtual Hard Disk (VHD) ist ein virtuelles Festplattenformat von Microsoft Hyper-V.",
        "Die Datei mit der Endung .vbox enthält die Einstellungen des virtuellen PCs beziehungsweise des "
        "Gast-Systems.",
        "Die Datei mit der Endung .vbox-prev enthält eine vorherige Version der zugehörigen .vbox-Datei.",
        "Die Datei mit der Endung .vdi enthält die virtuelle Festplatte des virtuellen PCs.",
    ))),

    # --- Benutzerkonten und Benutzergruppen ----------------------------------
    ("BS", USERS, "Lokale Benutzerkonten", _bullets((
        "Ein lokales Benutzerkonto kann über die Systemsteuerung unter Benutzerkonten hinzugefügt werden.",
        "Ein lokales Benutzerkonto kann über die Computerverwaltung unter System, Lokale Benutzer und Gruppen "
        "und Benutzer hinzugefügt werden.",
        "Ein lokales Benutzerkonto kann über die Windows-Einstellungen unter Konten hinzugefügt werden.",
    ))),
    ("BS", USERS, "Kontotypen", _bullets((
        "Ein Standardbenutzer kann die meisten Programme verwenden und Einstellungen ändern, die sich nur auf "
        "das eigene Benutzerkonto auswirken.",
        "Ein Administrator besitzt weitreichende Verwaltungsrechte und kann die Einstellungen des gesamten "
        "Computers ändern.",
        "Ein Administrator kann auf Dateien und Apps zugreifen, die auf dem PC gespeichert sind.",
    ))),
    ("BS", USERS, "Benutzerkontensteuerung", _bullets((
        "Die Benutzerkontensteuerung sorgt dafür, dass administrative Änderungen nur mit den entsprechenden "
        "Rechten durchgeführt werden können.",
        "Die Ausführung administrativer Aktionen muss über ein Dialogfeld bestätigt werden.",
        "Administrative Aktionen können dadurch nicht unbemerkt im Hintergrund ausgeführt werden.",
        "Ältere Programme sind möglicherweise nicht entsprechend gekennzeichnet und werden deshalb von der "
        "Benutzerkontensteuerung nicht als Programme erkannt, die Administratorrechte benötigen.",
        "Solche Programme werden dadurch möglicherweise nur mit Standardrechten ausgeführt.",
        "Das Programm kann über einen Rechtsklick und die Auswahl von „Als Administrator ausführen“ mit "
        "Administratorrechten gestartet werden.",
        "„Always notify me when“ benachrichtigt den Benutzer, wenn Apps versuchen, Software zu installieren "
        "oder Änderungen am Computer vorzunehmen.",
        "„Always notify me when“ benachrichtigt den Benutzer auch, wenn er selbst Änderungen an den "
        "Windows-Einstellungen vornimmt.",
        "„Notify me only when apps try to make changes to my computer (default)“ benachrichtigt den Benutzer "
        "nur, wenn Apps Änderungen am Computer vornehmen möchten.",
        "Bei der Standardeinstellung wird der Benutzer nicht benachrichtigt, wenn er selbst Änderungen an den "
        "Windows-Einstellungen vornimmt.",
        "„Notify me only when apps try to make changes to my computer (do not dim my desktop)“ benachrichtigt "
        "den Benutzer nur bei Änderungsversuchen durch Apps, ohne den Desktop abzudunkeln.",
        "„Never notify me when“ deaktiviert Benachrichtigungen, wenn Apps Software installieren oder Änderungen "
        "am Computer vornehmen möchten.",
        "Bei „Never notify me when“ erfolgen auch bei eigenen Änderungen an den Windows-Einstellungen keine "
        "Benachrichtigungen.",
    ))),
    ("BS", USERS, "Benutzergruppen", _bullets((
        "Benutzergruppen dienen dazu, Rechte, Zugriffsberechtigungen und die Zugehörigkeit von Benutzern zu "
        "Gruppen zu verwalten.",
        "Berechtigungen können mehreren Benutzern gleichzeitig über eine Benutzergruppe zugewiesen werden.",
        "Benutzergruppen vereinfachen die Verwaltung von Benutzern und deren Berechtigungen.",
        "Lokale Gruppen sind Benutzergruppen, die nur auf einem bestimmten Computer existieren.",
        "Lokale Gruppen haben keine Auswirkungen auf andere Computer.",
        "Lokale Gruppen können nicht exportiert oder importiert werden.",
        "Windows verfügt auf jedem Computer über lokale Gruppen.",
        "Mitglieder der Gruppe Administratoren besitzen umfassende Verwaltungsrechte auf dem Computer.",
        "Die Gruppe Administratoren verfügt über die höchsten regulären Verwaltungsrechte in Windows.",
        "Administratoren können auf dem Computer grundsätzlich auch auf geschützte Daten zugreifen.",
        "Ein lokaler oder Domänenbenutzer wird bei seiner Erstellung automatisch der Gruppe Benutzer "
        "zugeordnet.",
    ))),
    ("BS", USERS, "Access-Token", _bullets((
        "Ein Access-Token enthält die SID des Benutzers sowie die SIDs der Benutzergruppen, denen der Benutzer "
        "angehört.",
        "Das Access-Token enthält Informationen über die Berechtigungen, die dem angemeldeten Benutzer "
        "zugeordnet sind.",
        "Das Access-Token wird beim Anmelden eines Benutzers erstellt.",
    ))),

    # --- Benutzerprofile -----------------------------------------------------
    ("BS", PROFILES, "Grundlagen des Benutzerprofils", _bullets((
        "Ein Benutzerprofil ist die individuelle Konfiguration und Benutzerumgebung eines Benutzerkontos.",
        "Jeder Benutzer, der sich an einem Rechner anmeldet, besitzt eine eigene Benutzerumgebung.",
        "Die Benutzerumgebung umfasst unter anderem den Desktop, das Hintergrundbild und die eigenen Dateien.",
        "Zur Benutzerumgebung gehören außerdem Favoriten, das Aussehen der Fenster und der Bildschirmschoner.",
        "Auch Einstellungen für E-Mailsoftware und weitere benutzerspezifische Konfigurationen gehören zum "
        "Benutzerprofil.",
        "Der Sinn eines Benutzerprofils besteht darin, dass jeder Benutzer seine Umgebung nach den eigenen "
        "Bedürfnissen konfigurieren kann.",
        "Änderungen eines Benutzers wirken sich nur auf dessen eigenes Benutzerprofil aus.",
        "Andere Benutzerprofile bleiben von den Änderungen eines Benutzers unberührt.",
        "Benutzer können grundsätzlich nur auf Dateien und E-Mails zugreifen, für die sie die entsprechenden "
        "Berechtigungen besitzen.",
        "Ein Benutzerprofil wird bei der ersten Anmeldung des Benutzers am Rechner erstellt.",
    ))),
    ("BS", PROFILES, "Lokale Benutzerprofile", _bullets((
        "Lokale Benutzerprofile werden standardmäßig im Verzeichnis C:\\Users\\{Benutzername} gespeichert.",
        "Der Ordner Desktop enthält die Dateien und Verknüpfungen des Benutzerdesktops.",
        "Der Ordner Documents enthält die persönlichen Dokumente des Benutzers.",
        "Der Ordner Downloads enthält heruntergeladene Dateien des Benutzers.",
        "Der Ordner Pictures enthält die Bilder des Benutzers.",
        "Der Ordner Videos enthält die Videos des Benutzers.",
        "Der Ordner Music enthält die Musikdateien des Benutzers.",
        "Der Ordner AppData enthält anwendungsbezogene und benutzerspezifische Einstellungen und Daten.",
        "Der Ordner OneDrive kann die lokal eingebundenen beziehungsweise synchronisierten OneDrive-Dateien "
        "enthalten.",
        "C:\\Users\\Public ist ein öffentliches Benutzerverzeichnis, das mehreren Benutzern zur Verfügung steht.",
        "Die Umgebungsvariable %USERPROFILE% verweist auf das Profilverzeichnis des aktuell angemeldeten "
        "Benutzers.",
        "Die Umgebungsvariable %APPDATA% verweist standardmäßig auf den Roaming-Unterordner AppData des "
        "Benutzerprofils.",
        "Die Umgebungsvariable %LOCALAPPDATA% verweist auf den Local-Unterordner AppData des Benutzerprofils.",
        "Die Umgebungsvariable %TEMP% verweist auf das temporäre Verzeichnis des Benutzers.",
    ))),
    ("BS", PROFILES, "Servergespeicherte Benutzerprofile", _bullets((
        "Servergespeicherte Benutzerprofile werden auch als Roamingbenutzerprofile bezeichnet.",
        "Das Benutzerprofil wird auf einem Server gespeichert.",
        "Bei der Anmeldung wird das servergespeicherte Benutzerprofil auf den Computer heruntergeladen.",
        "Änderungen am Benutzerprofil werden beim Abmelden mit dem Server synchronisiert.",
        "Benutzer benötigen auf jedem Computer kein vollständig neues Benutzerprofil.",
        "Ein servergespeichertes Benutzerprofil kann auf mehreren Computern verwendet werden.",
        "Änderungen am Benutzerprofil werden beim Abmelden automatisch mit dem Server synchronisiert.",
    ))),
)


def seed_bs_questions(connection):
    """Insert every bank question that is not in the database yet.

    Existing rows are never touched: attempts and saved questions stay attached
    to them, and re-running is a no-op.
    """
    known = {
        row[0]
        for row in connection.execute(
            """SELECT t.name FROM topics t JOIN subjects s ON s.id = t.subject_id
               WHERE s.name = 'BS'"""
        )
    }
    unknown = {question["topic"] for question in BANK} - known
    if unknown:
        raise RuntimeError(f"Unknown BS topics in the bank: {sorted(unknown)}")

    stored = {
        (topic, text)
        for topic, text in connection.execute(
            """SELECT t.name, q.question_text
               FROM questions q
               JOIN topics t ON t.id = q.topic_id
               JOIN subjects s ON s.id = t.subject_id
               WHERE s.name = 'BS'"""
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
           WHERE s.name = 'BS' AND t.name = ?
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
