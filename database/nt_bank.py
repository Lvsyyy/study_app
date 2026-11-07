"""The NT question bank.

Every German subject-matter sentence below is copied from the NT course notes
unchanged, typos included. What is new is the question wording around those
sentences, the wrong answer options and the distribution over the existing NT
topics. Nothing here claims a fact that the notes do not contain.
"""
import json

ARCH = "Architekturen"
TOPO = "Topologien"
BASE = "Grundbasis"
KOMM = "Kommunikationsteilnehmer"
SCOPE = "Ausdehnungen"
ADDR = "Adressbereiche"

# The NT topics the app already ships with; the bank never creates a new one.
NT_TOPICS = (BASE, SCOPE, TOPO, ARCH, KOMM, ADDR)


def _question(topic, text, answer, kind, hint="", difficulty=2, alt=()):
    if not isinstance(answer, str):
        answer = json.dumps(answer, ensure_ascii=False)
    return {
        "topic": topic,
        "text": text,
        "answer": answer,
        "kind": kind,
        "hint": hint,
        "difficulty": difficulty,
        "alt": json.dumps(list(alt), ensure_ascii=False) if alt else None,
    }


def _single(topic, text, correct, distractors, hint="", difficulty=2):
    """One right answer among wrong ones; the UI shuffles the order."""
    return _question(
        topic, text,
        {"options": [correct, *distractors], "correct": [0]},
        "multi_select", hint, difficulty,
    )


def _choice(topic, text, options, correct, hint="", difficulty=2):
    return _question(
        topic, text,
        {"options": list(options), "correct": list(correct)},
        "multi_select", hint, difficulty,
    )


def _pairs(topic, text, pairs, hint="", difficulty=2):
    return _question(
        topic, text,
        {"pairs": [{"left": left, "right": right} for left, right in pairs]},
        "matching", hint, difficulty,
    )


def _order(topic, text, items, hint="", difficulty=2):
    return _question(topic, text, {"items": list(items)}, "ordering", hint, difficulty)


def _sort(topic, text, categories, cards, hint="", difficulty=2):
    return _question(
        topic, text,
        {
            "categories": list(categories),
            "cards": [{"text": text_, "category": category} for text_, category in cards],
        },
        "table_sort", hint, difficulty,
    )


def _answer(topic, text, expected, hint="", difficulty=2, alt=()):
    return _question(topic, text, expected, "text", hint, difficulty, alt)


# --- Architekturen -----------------------------------------------------------
P2P = "Peer-to-Peer"
CS = "Client/Server-Architekturen"
CLOUD = "Cloud Computing"

P2P_DESC = (
    "Jeder Rechner ist gleichberechtigt und jeder Nutzer ist ein Admin und "
    "arbeitet mit eigenen Betriebsmitteln (Software)"
)
CS_DESC = "Wird verwaltet auf zentralen Server / Rechner mit verteilten Ressourcen"
CLOUD_DESC = "Bietet Nutzern / Unternehmen eigene IT-Infrastruktur wenn nichts vorhanden ist"

P2P_PRO = (
    "Preiswerte Implementierung (Günstig)",
    "Kein Netzwerkbetriebssystem vorausgesetzt",
    "Kein Netzwerkadministrator notwendig",
)
P2P_CON = (
    "Schlechte Skalierbarkeit bei großen Netzwerken",
    "Sicherheitsprobleme",
    "Jeder Nutzer benötigt Administrationskenntnisse",
)
CS_PRO = (
    "Zentralisierte Administration",
    "Skalierbarkeit und flexible Architektur",
    "Verbesserte Sicherheit",
)
CS_CON = (
    "Server verlangen höherwertige Ausstattung (Teuer)",
    "Administrator notwendig",
    "Single Point of Failure in Form des Servers",
)
CLOUD_PRO = (
    "Schnelle Verfügbarkeit",
    "Geringer Aufwand (Keine Kabelverlegung / IT-Infrastruktur)",
    "Kosten senken",
    "Technische und wirtschaftliche Vorteile",
    "Hohe Skalierbarkeit (Mehr Speicher) und Flexibilität",
)
CLOUD_CON = (
    "Datenschutz, Datensicherheit, mangelndes Vertrauen",
    "Abhängigkeit von Internetverbindung",
    "Abhängigkeit vom Cloud-Anbieter",
    "Kann nicht einfach Anbieter wechseln",
)

IAAS = "IaaS (Infrastructure as a Service)"
PAAS = "PaaS (Platform as a Service)"
SAAS = "SaaS (Software as a Service)"
IAAS_DESC = "Zurverfügungstellung und Nutzung von Infrastrukturkomponenten"
PAAS_DESC = "Bereitstellung von Laufzeit- und Entwicklungsplattformen"
SAAS_DESC = "Angebot von Software zur Nutzung von Geschäftsprozessen"

# --- Topologien --------------------------------------------------------------
BUS_AUFBAU = "Zentrales Kabel verbindet alle Geräte"
BUS_ANWENDUNG = "Kleineren lokalen Netzen in 90er Jahre"
BUS_PRO = "Passive Topologie, Erweiterbarkeit, Günstig"
BUS_CON = "Nur ein Medium, Nicht unendlich"

STERN_AUFBAU = "Geräte separat angeschlossen, Zentralen Verteiler (Switch)"
STERN_ANWENDUNG = "Häufigste Netzwerkstruktur, Neuinstallation auf Etagen- oder Gebäudeebene"
STERN_PRO = "Kein Einzelpunktausfall, Erweiterbarkeit, Verteiler = Signalverstärker"
STERN_CON = "Große Kabelmenge, Hohe Kosten, Kein Verteiler = kein Netzverkehr"

RING_AUFBAU = "Alle Knoten an einen Ring verbunden, Datenverkehr eine Richtung"
RING_ANWENDUNG = "Automatisierungstechnik"
RING_PRO = "Knoten verarbeiten und verstärken die Signale, Einfache Fehlersuche"
RING_CON = "Datenverkehr nur in eine Richtung, Hoher Aufwand der Kabelverlegung, Schwere Erweiterbarkeit"

STERN_STERN_AUFBAU = "Multilayerswitch verbindet Switches mit Glasfaser"
STERN_STERN_ANWENDUNG = "In mehrstöckigen Bürogebäuden"
BAUM_AUFBAU = "Wurzel die zu Verteilungsstellen führt"
BAUM_ANWENDUNG = "Firmengelände verbindet Gebäude"
MASCHEN_AUFBAU = "Baum-Topologie aber alle Netzknoten sind verbunden (redundant)"
MASCHEN_ANWENDUNG = "Sicherheitsrelevanten lokalen Netzen, Weitverkehrsnetzen"

# --- Grundbasis --------------------------------------------------------------
NW_DEF = (
    "Verbindung und Kommunikation zwischen verschiedenen Geräten und Systemen, "
    "um Datenaustausch zu ermöglichen"
)
NW_PRO = "Einfache Kommunikation, Erweiterbarkeit, einfache Verwaltung, Verfügbarkeit"
NW_NEEDED = "Router, IPS, Computer, Ethernet Kabel, Server, Switch"
NW_WATCH = "Dass man die richtigen IPs vergibt und dass die Frequenz des Gerätes unterstützt ist"
NW_TROUBLE = "Falsche Konfiguration, Signalstörungen, Geräte sind nicht sofort sichtbar, Kosten"

NODE_DESC = "Verbindbare Komponenten"
INFRA_DESC = "Datensignale leiten, Datenverkehr klassifizieren - erlauben - unterbinden"
MEDIA_DESC = "Physikalische / drahtlose Verbindung (LAN Kabel, WLAN)"
PROTOCOL_DESC = "Definiert Regeln für Nachrichtenaustausch"

BANDWIDTH_DESC = "Kapazität des Mediums in Bit/s"
THROUGHPUT_DESC = "Echte transportierte Menge an Daten, Durchsatz <= Bandbreite"
GOODPUT_DESC = (
    "Maß der übertragenen Nutzdaten, Nettodaten ohne Protokolloverhead (nur Inhalt)"
)

# --- Kommunikationsteilnehmer -----------------------------------------------
SIMPLEX = "simplex"
HALF_DUPLEX = "half-duplex"
DUPLEX = "duplex"
SIMPLEX_DESC = "Nachrichtenfluss in nur eine Richtung von Sender zu Empfänger"
HALF_DUPLEX_DESC = "Jeder Knoten kann senden und empfangen jedoch nur abwechselnd"
DUPLEX_DESC = "Jeder Knoten kann Nachrichten jeweils gleichzeitig senden als auch empfangen"

UNICAST = "Unicast One-to-One Kommunikation"
ANYCAST = "Anycast One-to-nearest Kommunikation"
MULTICAST = "Multicast One-to-many Kommunikation"
UNICAST_DESC = (
    "Punkt zu Punkt Verbindung mit Zuordnung von Sender mit genau einem Empfänger"
)
ANYCAST_DESC = (
    "Punkt zu Punkt Verbindung mit Zuordnung von Sender mit dem nächstliegenden "
    "Empfänger einer Gruppe"
)
MULTICAST_DESC = (
    "Verbindung zu einer ausgewählten Gruppe mit Zuordnung von Sender zu "
    "mehreren Empfängern"
)

ROUTER = "Sucht den Weg für die Datenpakete"
SWITCH = "Verbindet Computer innerhalb eines Netzwerks, steuert den Datenverkehr"
PROXY = "Belastung abzunehmen und für Sicherheit, vermittelt zwischen Computer und Internet"
FIREWALL = "Kontrolliert die Datenpakete, blockiert nicht erlaubte Pakete"

# --- Ausdehnungen ------------------------------------------------------------
WAN = "Weltumspannend; Unterseekabel / Internet"
MAN = "Bis zu 100km; Öffentliches Telefonnetz, Stadtnetzwerk"
LAN = "Ca. 100m; Computer, TV, Konsolen"
PAN = "Ca. 10m; Bluetooth, USB, Infrarot"
CAN = "0,1 bis 10m; Mikrocontroller / elektronische Steuergeräte in Autos (CAN-Bus)"
BAN = "0,1 bis 1m; Medizinische Sensoren, Smart Watch"

# --- Adressbereiche ----------------------------------------------------------
PRIVATE_RANGE = "10.x.x.x/8"
PRIVATE_RANGE_172 = "172.16.0.0/12 - 172.31.255.255/12"
PRIVATE_RANGE_192 = "192.168.x.x/16"
LOOPBACK_RANGE = "127.0.0.0 - 127.255.255.255"
LINK_LOCAL_RANGE = "169.254.0.0 - 169.254.255.255"

PRIVATE_DESC = (
    "Adressbereich für private Netzwerke; Adressen aus diesem Bereich dürfen "
    "nicht im öffentlichen Internet verwendet werden"
)
LOOPBACK_DESC = (
    "Loopback-Adressen; Jedes an diese Adresse gesendete Paket soll den Host "
    "nicht verlassen sondern intern zurückgeschickt werden"
)
LINK_LOCAL_DESC = (
    "Link-lokale Adressen; Weist sich der Rechner selbst zu wenn die automatische "
    "Konfiguration per DHCP fehlgeschlagen hat; Link-lokale Adressen liegen im "
    "selben Adressbereich; Kommunikation zwischen Clients im lokalen Netz möglich"
)


BANK = (
    # =====================================================================
    # Architekturen
    # =====================================================================
    _sort(
        ARCH, "Ordne jede Beschreibung dem passenden Architekturtyp zu.",
        (P2P, CS, CLOUD),
        ((P2P_DESC, P2P), (CS_DESC, CS), (CLOUD_DESC, CLOUD)),
        "Achte darauf, wer die Ressourcen bereitstellt und verwaltet.", 1,
    ),
    _sort(
        ARCH, "Ordne die Vorteile dem passenden Architekturtyp zu.",
        (P2P, CS, CLOUD),
        tuple((text, P2P) for text in P2P_PRO)
        + tuple((text, CS) for text in CS_PRO)
        + tuple((text, CLOUD) for text in CLOUD_PRO),
        "Gehe die Vorteile der Reihe nach durch die drei Architekturen.", 3,
    ),
    _sort(
        ARCH, "Ordne die Nachteile dem passenden Architekturtyp zu.",
        (P2P, CS, CLOUD),
        tuple((text, P2P) for text in P2P_CON)
        + tuple((text, CS) for text in CS_CON)
        + tuple((text, CLOUD) for text in CLOUD_CON),
        "Ordne jeden Nachteil der Architektur zu, die er beschreibt.", 3,
    ),
    _pairs(
        ARCH, "Ordne jeder Beschreibung den passenden Architekturtyp zu.",
        ((P2P_DESC, P2P), (CS_DESC, CS), (CLOUD_DESC, CLOUD)),
        "Die Beschreibung nennt, wie die Rechner zusammenarbeiten.", 1,
    ),
    _choice(
        ARCH, "Welche Vorteile hat Peer-to-Peer? Wähle alle passenden Antworten.",
        [*P2P_PRO, CS_PRO[0], CS_PRO[2], CLOUD_PRO[2]],
        [0, 1, 2],
        "Zentralisierte Verwaltung gehört nicht zu Peer-to-Peer.", 2,
    ),
    _choice(
        ARCH, "Welche Nachteile hat Peer-to-Peer? Wähle alle passenden Antworten.",
        [*P2P_CON, CS_PRO[1], P2P_PRO[1], CS_CON[0]],
        [0, 1, 2],
        "Ohne zentralen Server fehlt auch dessen Skalierbarkeit und Ausstattung.", 2,
    ),
    _choice(
        ARCH, "Welche Vorteile hat Client/Server? Wähle alle passenden Antworten.",
        [*CS_PRO, P2P_PRO[1], P2P_PRO[2], CLOUD_CON[1]],
        [0, 1, 2],
        "Der zentrale Server bringt Verwaltung, Skalierbarkeit und Sicherheit.", 2,
    ),
    _choice(
        ARCH, "Welche Nachteile hat Client/Server? Wähle alle passenden Antworten.",
        [*CS_CON, P2P_PRO[0], P2P_CON[2], CLOUD_PRO[4]],
        [0, 1, 2],
        "Der Server kostet Geld, braucht einen Administrator und kann ausfallen.", 2,
    ),
    _choice(
        ARCH, "Welche Vorteile hat Cloud Computing? Wähle alle passenden Antworten.",
        [*CLOUD_PRO, P2P_PRO[2], CS_PRO[0], P2P_CON[0]],
        [0, 1, 2, 3, 4],
        "Die Vorteile betreffen Verfügbarkeit, Aufwand, Kosten und Skalierbarkeit.", 3,
    ),
    _choice(
        ARCH, "Welche Nachteile hat Cloud Computing? Wähle alle passenden Antworten.",
        [*CLOUD_CON, CS_PRO[0], P2P_PRO[0], CLOUD_PRO[0]],
        [0, 1, 2, 3],
        "Die Nachteile betreffen Datenschutz, Internet und den Anbieter.", 3,
    ),
    _sort(
        ARCH, "Ordne jede Serviceart ihrer Beschreibung zu.",
        ("IaaS", "PaaS", "SaaS"),
        (
            (IAAS, "IaaS"),
            (IAAS_DESC, "IaaS"),
            (PAAS, "PaaS"),
            (PAAS_DESC, "PaaS"),
            (SAAS, "SaaS"),
            (SAAS_DESC, "SaaS"),
        ),
        "Infrastruktur, Plattform, Software – in dieser Reihenfolge.", 2,
    ),
    _pairs(
        ARCH, "Ordne jeder Serviceart die passende Beschreibung zu.",
        ((IAAS, IAAS_DESC), (PAAS, PAAS_DESC), (SAAS, SAAS_DESC)),
        "IaaS liefert Infrastruktur, PaaS die Plattform, SaaS die fertige Software.", 2,
    ),
                    _choice(
        ARCH, "Welche Architekturtypen werden in diesem Thema behandelt? Wähle alle passenden Antworten.",
        [P2P, CS, "Monolithische Anwendungssysteme", CLOUD, "Bus", "Stern"],
        [0, 1, 2, 3],
        "Topologien wie Bus und Stern gehören nicht zu den Architekturtypen.", 1,
    ),

    # =====================================================================
    # Topologien
    # =====================================================================
    _sort(
        TOPO, "Ordne Aufbau, Anwendung, Vorteile und Nachteile der passenden Topologie zu.",
        ("Bus", "Stern", "Ring"),
        (
            (f"Aufbau: {BUS_AUFBAU}", "Bus"),
            (f"Anwendung: {BUS_ANWENDUNG}", "Bus"),
            (f"Vorteile: {BUS_PRO}", "Bus"),
            (f"Nachteile: {BUS_CON}", "Bus"),
            (f"Aufbau: {STERN_AUFBAU}", "Stern"),
            (f"Anwendung: {STERN_ANWENDUNG}", "Stern"),
            (f"Vorteile: {STERN_PRO}", "Stern"),
            (f"Nachteile: {STERN_CON}", "Stern"),
            (f"Aufbau: {RING_AUFBAU}", "Ring"),
            (f"Anwendung: {RING_ANWENDUNG}", "Ring"),
            (f"Vorteile: {RING_PRO}", "Ring"),
            (f"Nachteile: {RING_CON}", "Ring"),
        ),
        "Jede Topologie hat genau einen Aufbau, eine Anwendung, Vorteile und Nachteile.", 3,
    ),
    _sort(
        TOPO, "Ordne Aufbau und Anwendung der passenden Mischform zu.",
        ("Stern-Stern", "Baum-Topologie", "Maschennetz"),
        (
            (f"Aufbau: {STERN_STERN_AUFBAU}", "Stern-Stern"),
            (f"Anwendung: {STERN_STERN_ANWENDUNG}", "Stern-Stern"),
            (f"Aufbau: {BAUM_AUFBAU}", "Baum-Topologie"),
            (f"Anwendung: {BAUM_ANWENDUNG}", "Baum-Topologie"),
            (f"Aufbau: {MASCHEN_AUFBAU}", "Maschennetz"),
            (f"Anwendung: {MASCHEN_ANWENDUNG}", "Maschennetz"),
        ),
        "Drei Mischformen, je ein Aufbau und eine Anwendung.", 2,
    ),
    _pairs(
        TOPO, "Ordne jeder Topologie ihren Aufbau zu.",
        ((BUS_AUFBAU, "Bus"), (STERN_AUFBAU, "Stern"), (RING_AUFBAU, "Ring")),
        "Frage dich, wie die Geräte miteinander verbunden sind.", 1,
    ),
    _pairs(
        TOPO, "Ordne jedem Nachteil die passende Topologie zu.",
        ((BUS_CON, "Bus"), (STERN_CON, "Stern"), (RING_CON, "Ring")),
        "Achte auf Kabelmenge, Medium und Richtung des Datenverkehrs.", 2,
    ),
    _pairs(
        TOPO, "Ordne jedem Vorteil die passende Topologie zu.",
        ((BUS_PRO, "Bus"), (STERN_PRO, "Stern"), (RING_PRO, "Ring")),
        "Signalverstärkung, Fehlersuche und passive Topologie sind die Hinweise.", 2,
    ),
    _single(
        TOPO, "Welche Topologie verbindet alle Geräte über ein zentrales Kabel?",
        BUS_AUFBAU, [STERN_AUFBAU, RING_AUFBAU],
        "Ein einziges Medium für alle Geräte.", 1,
    ),
    _single(
        TOPO,
        "Bei welcher Topologie sind alle Knoten an einem Ring verbunden und der Datenverkehr läuft in eine Richtung?",
        RING_AUFBAU, [BUS_AUFBAU, STERN_AUFBAU],
        "Denke an einen geschlossenen Kreis.", 1,
    ),
    _single(
        TOPO, "Wo wird die Ring-Topologie eingesetzt?",
        RING_ANWENDUNG, [BUS_ANWENDUNG, STERN_ANWENDUNG, STERN_STERN_ANWENDUNG],
        "Der Einsatzbereich liegt in der Technik, nicht im Büro.", 2,
    ),
    _single(
        TOPO, "Welche Vorteile hat die Stern-Topologie?",
        STERN_PRO, [BUS_PRO, RING_PRO],
        "Der Verteiler verstärkt das Signal und ein Ausfall eines Geräts stoppt das Netz nicht.", 2,
    ),
    _single(
        TOPO, "Welche Nachteile hat die Ring-Topologie?",
        RING_CON, [BUS_CON, STERN_CON],
        "Richtung und Verkabelung sind hier die Probleme.", 2,
    ),
    _single(
        TOPO, "Welche Nachteile hat die Bus-Topologie?",
        BUS_CON, [STERN_CON, RING_CON],
        "Es gibt nur ein Medium, und es ist begrenzt.", 2,
    ),
            _pairs(
        TOPO, "Ordne jeder Mischform ihren Aufbau zu.",
        ((STERN_STERN_AUFBAU, "Stern-Stern"), (BAUM_AUFBAU, "Baum-Topologie"), (MASCHEN_AUFBAU, "Maschennetz")),
        "Glasfaser, Wurzel und redundante Verbindungen sind die Hinweise.", 2,
    ),
    _choice(
        TOPO, "Welche Mischformen werden in diesem Thema behandelt? Wähle alle passenden Antworten.",
        ["Stern-Stern", "Baum-Topologie", "Maschennetz", "Bus", "Ring"],
        [0, 1, 2],
        "Bus und Ring sind Grundtopologien, keine Mischformen.", 1,
    ),

    # =====================================================================
    # Grundbasis
    # =====================================================================
    _pairs(
        BASE, "Ordne jeder Beschreibung den passenden Begriff der Netzwerkgrundlagen zu.",
        ((NODE_DESC, "Rechnern oder Knoten"),
         (INFRA_DESC, "Infrastrukturkomponenten"),
         (MEDIA_DESC, "Verkabelung / Übertragungsmedien"),
         (PROTOCOL_DESC, "Protokoll")),
        "Geräte, Leitung, Regeln und die Komponenten dazwischen.", 2,
    ),
    _pairs(
        BASE, "Ordne jeder Frage die passende Antwort aus den Netzwerkgrundlagen zu.",
        (("Was ist Netzwerktechnik?", NW_DEF),
         ("Was sind die Vorteile eines Netzwerkes?", NW_PRO),
         ("Was benötigen Sie, um IT-Netzwerke einrichten zu können?", NW_NEEDED),
         ("Was ist bei der Einrichtung von Netzwerken zu beachten?", NW_WATCH),
         ("Welche Schwierigkeiten können bei der Einrichtung eines Netzwerkes auftreten?", NW_TROUBLE)),
        "Jede Frage hat in den Notizen genau eine Antwort.", 3,
    ),
    _single(
        BASE, "Welche Aussage beschreibt Netzwerktechnik?",
        NW_DEF, [NW_WATCH, NW_PRO, NW_TROUBLE],
        "Es geht um Verbindung, Kommunikation und Datenaustausch.", 1,
    ),
    _choice(
        BASE, "Was benötigen Sie, um IT-Netzwerke einrichten zu können? Wähle alle passenden Antworten.",
        ["Router", "IPS", "Computer", "Ethernet Kabel", "Server", "Switch",
         "Bluetooth-Kopfhörer", "Beamer", "Tastatur"],
        [0, 1, 2, 3, 4, 5],
        "Es sind sechs Geräte aus den Notizen.", 1,
    ),
    _choice(
        BASE, "Welche Schwierigkeiten können bei der Einrichtung eines Netzwerkes auftreten? Wähle alle passenden Antworten.",
        ["Falsche Konfiguration", "Signal Störungen", "Geräte sind nicht sofot seebar", "Kosten",
         "Zu viele Administratoren", "Keine Kabel vorhanden"],
        [0, 1, 2, 3],
        "Vier Punkte stehen in den Notizen.", 2,
    ),
    _choice(
        BASE, "Welche Vorteile hat ein Netzwerk? Wähle alle passenden Antworten.",
        ["Einfache Kommunikation", "Erweiterkeit", "einfache Verwaltung", "Verfügbarkeit",
         "Automatische Verschlüsselung", "Kein Administrator notwendig"],
        [0, 1, 2, 3],
        "Vier Vorteile stehen in den Notizen.", 1,
    ),
    _pairs(
        BASE, "Ordne jeder Kenngröße die passende Beschreibung zu.",
        ((BANDWIDTH_DESC, "Bandbreite"), (THROUGHPUT_DESC, "Durchsatz"), (GOODPUT_DESC, "Goodput")),
        "Kapazität, tatsächliche Menge und Nutzdaten sind drei verschiedene Dinge.", 2,
    ),
                _single(
        BASE,
        "Welche Kenngröße bezeichnet die echte transportierte Datenmenge und kann die Bandbreite nicht überschreiten?",
        THROUGHPUT_DESC, [BANDWIDTH_DESC, GOODPUT_DESC],
        "Es ist die tatsächlich übertragene Menge.", 2,
    ),
    _choice(
        BASE, "Welche Informationen stehen auf einem IP-Paket? Wähle alle passenden Antworten.",
        ["IP-Header", "Empfänger", "Absender", "Proxy Server Adresse", "Pakettyp",
         "MAC-Adresse des Switches", "WLAN-Passwort", "Bildschirmauflösung"],
        [0, 1, 2, 3, 4],
        "Fünf Angaben stehen in den Notizen.", 2,
    ),
    _single(
        BASE, "Was ist bei der Einrichtung von Netzwerken zu beachten?",
        NW_WATCH, [NW_TROUBLE, NW_DEF, NW_NEEDED],
        "Es geht um IP-Adressen und die Frequenz der Geräte.", 2,
    ),

    # =====================================================================
    # Kommunikationsteilnehmer
    # =====================================================================
    _pairs(
        KOMM, "Ordne jeder Kommunikationsrichtung die passende Beschreibung zu.",
        ((SIMPLEX_DESC, SIMPLEX), (HALF_DUPLEX_DESC, HALF_DUPLEX), (DUPLEX_DESC, DUPLEX)),
        "Achte darauf, ob beide Seiten gleichzeitig dürfen.", 1,
    ),
    _pairs(
        KOMM, "Ordne jedem Kommunikationsteilnehmer die passende Beschreibung zu.",
        ((UNICAST_DESC, UNICAST), (ANYCAST_DESC, ANYCAST), (MULTICAST_DESC, MULTICAST)),
        "One-to-One, One-to-nearest und One-to-many.", 2,
    ),
    _sort(
        KOMM, "Ordne jede Beschreibung der passenden Kommunikationsrichtung zu.",
        (SIMPLEX, HALF_DUPLEX, DUPLEX),
        ((SIMPLEX_DESC, SIMPLEX), (HALF_DUPLEX_DESC, HALF_DUPLEX), (DUPLEX_DESC, DUPLEX)),
        "Eine Richtung, abwechselnd, gleichzeitig.", 1,
    ),
    _single(
        KOMM, "Bei welcher Kommunikationsrichtung können beide Knoten gleichzeitig senden und empfangen?",
        DUPLEX_DESC, [SIMPLEX_DESC, HALF_DUPLEX_DESC],
        "Gleichzeitig ist der entscheidende Hinweis.", 1,
    ),
    _single(
        KOMM, "Bei welcher Kommunikationsrichtung ist Senden und Empfangen nur abwechselnd möglich?",
        HALF_DUPLEX_DESC, [SIMPLEX_DESC, DUPLEX_DESC],
        "Beide dürfen, aber nicht zur selben Zeit.", 1,
    ),
    _single(
        KOMM, "Bei welcher Kommunikationsrichtung fließen Nachrichten nur vom Sender zum Empfänger?",
        SIMPLEX_DESC, [HALF_DUPLEX_DESC, DUPLEX_DESC],
        "Der Empfänger antwortet nicht.", 1,
    ),
    _single(
        KOMM, "Welche Kommunikationsform ist eine One-to-One-Kommunikation?",
        UNICAST, [ANYCAST, MULTICAST],
        "Genau ein Empfänger.", 1,
    ),
    _single(
        KOMM, "Welche Kommunikationsform erreicht den nächstliegenden Empfänger einer Gruppe?",
        ANYCAST, [UNICAST, MULTICAST],
        "One-to-nearest steht im Namen.", 1,
    ),
    _single(
        KOMM, "Welche Kommunikationsform erreicht mehrere Empfänger einer ausgewählten Gruppe?",
        MULTICAST, [UNICAST, ANYCAST],
        "One-to-many steht im Namen.", 1,
    ),
    _pairs(
        KOMM, "Ordne jedem Netzwerkgerät die passende Aufgabe zu.",
        ((ROUTER, "Router"), (SWITCH, "Switch"), (PROXY, "Proxy"), (FIREWALL, "Firewall")),
        "Weg suchen, Geräte verbinden, vermitteln, kontrollieren.", 2,
    ),
    _single(KOMM, "Was macht der Switch?", SWITCH, [ROUTER, PROXY, FIREWALL],
            "Er arbeitet innerhalb eines Netzwerks.", 1),
    _single(KOMM, "Welche Aufgabe hat der Proxy?", PROXY, [ROUTER, SWITCH, FIREWALL],
            "Er vermittelt zwischen Computer und Internet.", 2),
    _single(KOMM, "Was macht eine Firewall?", FIREWALL, [ROUTER, SWITCH, PROXY],
            "Sie blockiert nicht erlaubte Pakete.", 1),
    _answer(KOMM, "Firewall-Eingänge. Wie heißen diese in der Fachsprache?", "Ports",
            "Es ist ein kurzes Wort.", 1),
    _pairs(
        KOMM, "Wofür werden die Eingänge 80 und 25 genutzt?",
        (("80", "80 für Datenpakete (HTTP)"), ("25", "25 für E-Mails (SMTP)")),
        "HTTP läuft über 80, SMTP über 25.", 2,
    ),
    
    # =====================================================================
    # Ausdehnungen
    # =====================================================================
    _sort(
        SCOPE, "Ordne jedem Netzwerktyp Reichweite und Beispiele zu.",
        ("WAN", "MAN", "LAN", "PAN", "CAN", "BAN"),
        (
            ("Reichweite: Weltumspannend", "WAN"),
            ("Beispiele: Unterseekabel / Internet", "WAN"),
            ("Reichweite: Bis zu 100km", "MAN"),
            ("Beispiele: Öffentliches Telefonnetz, Stadtnetzwerk", "MAN"),
            ("Reichweite: Ca. 100m", "LAN"),
            ("Beispiele: Computers, TV, Konsolen", "LAN"),
            ("Reichweite: Ca. 10m", "PAN"),
            ("Beispiele: Bluetooth, USB, Infrarot", "PAN"),
            ("Reichweite: 0,1 bis 10m", "CAN"),
            ("Beispiele: Mikrokontroller / elektronische Steuergeräte in Autos (CAN-Bus)", "CAN"),
            ("Reichweite: 0,1 bis 1m", "BAN"),
            ("Beispiele: Medizinischen Sensoren, Smart Watch", "BAN"),
        ),
        "Von weltumspannend bis wenige Zentimeter.", 3,
    ),
    _pairs(
        SCOPE, "Ordne jedem Netztyp Reichweite und Beispiele zu.",
        (("WAN", WAN), ("MAN", MAN), ("LAN", LAN), ("PAN", PAN), ("CAN", CAN), ("BAN", BAN)),
        "Sechs Kürzel, je eine Reichweite mit Beispielen.", 2,
    ),
    _pairs(
        SCOPE, "Ordne jeder Reichweite den passenden Netztyp zu.",
        (("Weltumspannend", "WAN"), ("Bis zu 100km", "MAN"), ("Ca. 100m", "LAN"),
         ("Ca. 10m", "PAN"), ("0,1 bis 10m", "CAN"), ("0,1 bis 1m", "BAN")),
        "Beginne bei der größten Reichweite.", 2,
    ),
    _order(
        SCOPE, "Ordne die Netztypen nach ihrer Reichweite – vom kürzesten zum größten.",
        ("BAN", "CAN", "PAN", "LAN", "MAN", "WAN"),
        "BAN ist am kürzesten, WAN am größten.", 2,
    ),
    _single(SCOPE, "Welcher Netztyp reicht bis zu 100 km?", "MAN", ["LAN", "WAN", "PAN"],
            "Zwischen LAN und WAN.", 1),
    _single(SCOPE, "Ca. 10m – Bluetooth, USB, Infrarot: Welcher Netztyp ist das?",
            "PAN", ["CAN", "BAN", "LAN"], "Der persönliche Bereich.", 1),
    _single(SCOPE, "Welcher Netztyp ist weltumspannend und nutzt Unterseekabel bzw. das Internet?",
            "WAN", ["MAN", "LAN", "CAN"], "Der größte der sechs Typen.", 1),
    _choice(
        SCOPE, "Welche Beispiele gehören zum PAN? Wähle alle passenden Antworten.",
        ["Bluetooth", "USB", "Infrarot", "Unterseekabel", "Glasfaser zwischen Gebäuden"],
        [0, 1, 2],
        "Es sind drei Beispiele aus den Notizen.", 1,
    ),

    # =====================================================================
    # Adressbereiche
    # =====================================================================
    _pairs(
        ADDR, "Ordne jedem Adressbereich die passende Bedeutung zu.",
        ((PRIVATE_RANGE, PRIVATE_DESC),
         (LOOPBACK_RANGE, LOOPBACK_DESC),
         (LINK_LOCAL_RANGE, LINK_LOCAL_DESC)),
        "Drei Bereiche, drei verschiedene Bedeutungen.", 2,
    ),
    _sort(
        ADDR, "Ordne jeden Adressbereich der passenden Kategorie zu.",
        ("Private Netzwerke", "Loopback-Adressen", "Link-lokale Adressen"),
        (
            (PRIVATE_RANGE, "Private Netzwerke"),
            (PRIVATE_RANGE_172, "Private Netzwerke"),
            (PRIVATE_RANGE_192, "Private Netzwerke"),
            (LOOPBACK_RANGE, "Loopback-Adressen"),
            (LINK_LOCAL_RANGE, "Link-lokale Adressen"),
        ),
        "Drei private Bereiche stehen in den Notizen.", 2,
    ),
        _choice(
        ADDR, "Welche dieser Adressbereiche sind für private Netzwerke reserviert? Wähle alle passenden Antworten.",
        [PRIVATE_RANGE, PRIVATE_RANGE_172, PRIVATE_RANGE_192, LOOPBACK_RANGE, LINK_LOCAL_RANGE],
        [0, 1, 2],
        "Loopback und link-lokal sind eigene Bereiche.", 2,
    ),
    _single(
        ADDR,
        "Wohin werden Pakete gesendet, die an eine Adresse aus 127.0.0.0 - 127.255.255.255 adressiert sind?",
        "Jedes an diese Adresse gesendete Paket soll den Host nicht verlassen sondern intern zurückgeschikt werden",
        ["Adressen aus diesem Bereich dürfen nicht im öffentlichen Internet verwendet werden",
         "Weist sich der Rechner selbst zu wenn die automatische Konfiguration per DHCP fehlgeschlagen hat"],
        "Der Host verlässt sich selbst nicht.", 2,
    ),
    _single(
        ADDR,
        "Wann weist sich ein Rechner selbst eine link-lokale Adresse aus 169.254.0.0 - 169.254.255.255 zu?",
        "wenn die automatische Konfiguration per DHCP fehlgeschlagen hat",
        ["wenn der Rechner in einem privaten Netzwerk startet",
         "wenn die Loopback-Adresse bereits belegt ist"],
        "Ohne DHCP bleibt dem Rechner nur dieser Weg.", 2,
    ),
        _single(
        ADDR, "Welche Bedeutung haben die Netzklassen A-E heute?",
        "nicht mehr relevant",
        ["Standard im Internet", "Nur für private Netzwerke", "Pflicht für Loopback-Adressen"],
        "Sie wurden abgelöst.", 1,
    ),
    _choice(
        ADDR, "Welche Aussagen zu link-lokalen Adressen sind korrekt? Wähle alle passenden Antworten.",
        ["Weist sich der Rechner selbst zu wenn die automatische Konfiguration per DHCP fehlgeschlagen hat",
         "Link-lokale Adressen liegen im selben Adressbereich",
         "Kommunikation zwischen Clients im lokalen Netz möglich",
         "Link-lokale Adressen dürfen nicht im lokalen Netz verwendet werden"],
        [0, 1, 2],
        "Drei Aussagen stehen in den Notizen, eine widerspricht ihnen.", 2,
    ),

    # =====================================================================
    # Welche Aussage passt nicht? (odd one out)
    # =====================================================================
    _single(
        ARCH, "Welche Aussage passt nicht zu Peer-to-Peer?",
        CS_PRO[0], [P2P_PRO[0], P2P_PRO[1], P2P_PRO[2]],
        "Drei Aussagen beschreiben Peer-to-Peer, eine gehört zu Client/Server.", 2,
    ),
    _single(
        ARCH, "Welche Serviceart passt nicht zu den drei Servicearten?",
        "Public Cloud", [IAAS, PAAS, SAAS],
        "Drei sind Servicearten, eine ist eine Cloud-Art.", 1,
    ),
    _single(
        TOPO, "Welche Aussage passt nicht zur Stern-Topologie?",
        RING_CON.split(", ")[0], [STERN_PRO, STERN_AUFBAU, STERN_CON.split(", ")[0]],
        "Drei Aussagen gehören zum Stern, eine zur Ring-Topologie.", 2,
    ),
    _single(
        BASE, "Welcher Begriff passt nicht zu den Komponenten eines Netzwerks?",
        "Bildschirmauflösung",
        ["Rechnern oder Knoten", "Infrastrukturkomponenten", "Verkabelung / Übertragungsmedien"],
        "Drei Begriffe stehen in den Notizen als Komponenten.", 1,
    ),
    _single(
        KOMM, "Welche Aussage passt nicht zu den Kommunikationsrichtungen?",
        MULTICAST, [SIMPLEX_DESC, HALF_DUPLEX_DESC, DUPLEX_DESC],
        "Drei beschreiben eine Richtung, eine beschreibt einen Teilnehmer.", 2,
    ),
    _single(
        SCOPE, "Welche Reichweite passt nicht zu den Typen im Meterbereich?",
        "Weltumspannend", ["Ca. 10m", "0,1 bis 10m", "0,1 bis 1m"],
        "Drei Angaben liegen im Meterbereich, eine ist weltumspannend.", 1,
    ),
    _single(
        ADDR, "Welcher Adressbereich passt nicht zu den privaten Netzen?",
        LOOPBACK_RANGE, [PRIVATE_RANGE, PRIVATE_RANGE_172, PRIVATE_RANGE_192],
        "Drei Bereiche sind privat, einer ist Loopback.", 2,
    ),
)


def seed_nt_questions(connection):
    """Insert every bank question that is not in the database yet.

    Existing rows are never touched: attempts and saved questions stay attached
    to them, and re-running is a no-op.
    """
    known = {
        row[0]
        for row in connection.execute(
            """SELECT t.name FROM topics t JOIN subjects s ON s.id = t.subject_id
               WHERE s.name = 'NT'"""
        )
    }
    unknown = {question["topic"] for question in BANK} - known
    if unknown:
        raise RuntimeError(f"Unknown NT topics in the bank: {sorted(unknown)}")

    # Compare against what is already stored instead of issuing one conditional
    # insert per question: an up-to-date database costs a single query.
    stored = {
        (topic, text)
        for topic, text in connection.execute(
            """SELECT t.name, q.question_text
               FROM questions q
               JOIN topics t ON t.id = q.topic_id
               JOIN subjects s ON s.id = t.subject_id
               WHERE s.name = 'NT'"""
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
           WHERE s.name = 'NT' AND t.name = ?
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
