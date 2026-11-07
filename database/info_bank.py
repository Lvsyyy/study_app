"""Reference information shown by the Information page.

The German text is the NT course notes, only split into headings and bullet
lists. It is the same wording the NT question bank is built from, so a fact can
never appear in a question and differently in the information view.
"""
from .nt_bank import (
    ADDR,
    ANYCAST,
    ANYCAST_DESC,
    ARCH,
    BAN,
    BANDWIDTH_DESC,
    BASE,
    BAUM_ANWENDUNG,
    BAUM_AUFBAU,
    BUS_ANWENDUNG,
    BUS_AUFBAU,
    BUS_CON,
    BUS_PRO,
    CAN,
    CLOUD_CON,
    CLOUD_DESC,
    CLOUD_PRO,
    CS_CON,
    CS_DESC,
    CS_PRO,
    DUPLEX,
    DUPLEX_DESC,
    FIREWALL,
    GOODPUT_DESC,
    HALF_DUPLEX,
    HALF_DUPLEX_DESC,
    IAAS,
    IAAS_DESC,
    INFRA_DESC,
    KOMM,
    LAN,
    LINK_LOCAL_DESC,
    LINK_LOCAL_RANGE,
    LOOPBACK_DESC,
    LOOPBACK_RANGE,
    MAN,
    MASCHEN_ANWENDUNG,
    MASCHEN_AUFBAU,
    MEDIA_DESC,
    MULTICAST,
    MULTICAST_DESC,
    NODE_DESC,
    NW_DEF,
    NW_NEEDED,
    NW_PRO,
    NW_TROUBLE,
    NW_WATCH,
    P2P_CON,
    P2P_DESC,
    P2P_PRO,
    PAAS,
    PAAS_DESC,
    PAN,
    PRIVATE_DESC,
    PRIVATE_RANGE,
    PRIVATE_RANGE_172,
    PRIVATE_RANGE_192,
    PROTOCOL_DESC,
    PROXY,
    RING_ANWENDUNG,
    RING_AUFBAU,
    RING_CON,
    RING_PRO,
    ROUTER,
    SAAS,
    SAAS_DESC,
    SCOPE,
    SIMPLEX,
    SIMPLEX_DESC,
    STERN_ANWENDUNG,
    STERN_AUFBAU,
    STERN_CON,
    STERN_PRO,
    STERN_STERN_ANWENDUNG,
    STERN_STERN_AUFBAU,
    SWITCH,
    THROUGHPUT_DESC,
    TOPO,
    UNICAST,
    UNICAST_DESC,
    WAN,
)


def _bullets(items):
    return "\n".join(f"• {item}" for item in items)


def _block(heading, lines):
    return "\n".join(lines)


INFO_BANK = (
    # --- NT · Architekturen --------------------------------------------------
    ("NT", ARCH, "Architekturtypen", _block("Architekturtypen", (
        "Peer-to-Peer",
        "Client/Server-Architekturen",
        "Monolithische Anwendungssysteme",
        "Cloud Computing",
    ))),
    ("NT", ARCH, "Peer-to-Peer", _block("Peer-to-Peer", (
        "Beschreibung:",
        P2P_DESC,
        "",
        "Vorteile:",
        _bullets(P2P_PRO),
        "",
        "Nachteile:",
        _bullets(P2P_CON),
    ))),
    ("NT", ARCH, "Client/Server-Architekturen", _block("Client/Server-Architekturen", (
        "Beschreibung:",
        CS_DESC,
        "",
        "Vorteile:",
        _bullets(CS_PRO),
        "",
        "Nachteile:",
        _bullets(CS_CON),
    ))),
    ("NT", ARCH, "Cloud Computing", _block("Cloud Computing", (
        "Beschreibung:",
        CLOUD_DESC,
        "",
        "Vorteile:",
        _bullets(CLOUD_PRO),
        "",
        "Nachteile:",
        _bullets(CLOUD_CON),
    ))),
    ("NT", ARCH, "Servicearten", _block("Servicearten", (
        f"{IAAS} = {IAAS_DESC}",
        f"{PAAS} = {PAAS_DESC}",
        f"{SAAS} = {SAAS_DESC}",
    ))),
    ("NT", ARCH, "Cloud-Arten", _block("Cloud-Arten", (
        "Public Cloud",
        "Private Cloud",
    ))),

    # --- NT · Topologien -----------------------------------------------------
    ("NT", TOPO, "Bus", _block("Bus", (
        f"Aufbau: {BUS_AUFBAU}",
        f"Anwendung: {BUS_ANWENDUNG}",
        f"Vorteile: {BUS_PRO}",
        f"Nachteile: {BUS_CON}",
    ))),
    ("NT", TOPO, "Stern", _block("Stern", (
        f"Aufbau: {STERN_AUFBAU}",
        f"Anwendung: {STERN_ANWENDUNG}",
        f"Vorteile: {STERN_PRO}",
        f"Nachteile: {STERN_CON}",
    ))),
    ("NT", TOPO, "Ring", _block("Ring", (
        f"Aufbau: {RING_AUFBAU}",
        f"Anwendung: {RING_ANWENDUNG}",
        f"Vorteile: {RING_PRO}",
        f"Nachteile: {RING_CON}",
    ))),
    ("NT", TOPO, "Begriffe", _block("Begriffe", (
        "Shared Medium: Wenn Knoten sich ein Übertragungsmedium teilen",
        "",
        "Single Point of Failure: Die Stelle im Netz die den Netzverkehr steuert",
    ))),
    ("NT", TOPO, "Mischformen", _block("Mischformen", (
        "Stern-Stern",
        f"Aufbau: {STERN_STERN_AUFBAU}",
        f"Anwendung: {STERN_STERN_ANWENDUNG}",
        "",
        "Baum-Topologie",
        f"Aufbau: {BAUM_AUFBAU}",
        f"Anwendung: {BAUM_ANWENDUNG}",
        "",
        "Maschennetz",
        f"Aufbau: {MASCHEN_AUFBAU}",
        f"Anwendung: {MASCHEN_ANWENDUNG}",
    ))),

    # --- NT · Grundbasis -----------------------------------------------------
    ("NT", BASE, "Netzwerktechnik", _block("Netzwerktechnik", (
        "Was ist Netzwerktechnik?",
        NW_DEF,
        "",
        "Was sind die Vorteile eines Netzwerkes?",
        NW_PRO,
        "",
        "Was benötigen Sie, um IT-Netzwerke einrichten zu können?",
        NW_NEEDED,
        "",
        "Was ist bei der Einrichtung von Netzwerken zu beachten?",
        NW_WATCH,
        "",
        "Welche Schwierigkeiten können bei der Einrichtung eines Netzwerkes auftreten?",
        NW_TROUBLE,
    ))),
    ("NT", BASE, "Komponenten", _block("Komponenten", (
        f"Rechnern oder Knoten: {NODE_DESC}",
        f"Infrastrukturkomponenten: {INFRA_DESC}",
        f"Verkabelung / Übertragungsmedien: {MEDIA_DESC}",
        f"Protokoll: {PROTOCOL_DESC}",
    ))),
    ("NT", BASE, "Bandbreite, Durchsatz, Goodput", _block("Bandbreite, Durchsatz, Goodput", (
        f"Bandbreite: {BANDWIDTH_DESC}",
        f"Durchsatz: {THROUGHPUT_DESC}",
        f"Goodput: {GOODPUT_DESC}",
    ))),
    ("NT", BASE, "IP-Paket", _block("IP-Paket", (
        "Welche Informationen stehen auf einem IP-Paket?",
        _bullets(("IP-Header", "Empfänger", "Absender", "Proxy Server Adresse", "Pakettyp")),
    ))),

    # --- NT · Kommunikationsteilnehmer --------------------------------------
    ("NT", KOMM, "Kommunikationsrichtungen", _block("Kommunikationsrichtungen", (
        f"{SIMPLEX}: {SIMPLEX_DESC}",
        f"{HALF_DUPLEX}: {HALF_DUPLEX_DESC}",
        f"{DUPLEX}: {DUPLEX_DESC}",
    ))),
    ("NT", KOMM, "Kommunikationsteilnehmer", _block("Kommunikationsteilnehmer", (
        f"{UNICAST}: {UNICAST_DESC}",
        f"{ANYCAST}: {ANYCAST_DESC}",
        f"{MULTICAST}: {MULTICAST_DESC}",
    ))),
    ("NT", KOMM, "Netzwerkgeräte", _block("Netzwerkgeräte", (
        f"Router: {ROUTER}",
        f"Switch: {SWITCH}",
        f"Proxy: {PROXY}",
        f"Firewall: {FIREWALL}",
    ))),
    ("NT", KOMM, "Ports", _block("Ports", (
        "Firewall-Eingänge heißen in der Fachsprache Ports.",
        "",
        "80 für Datenpakete (HTTP)",
        "25 für E-Mails (SMTP)",
        "",
        "Datenpakete, die nicht ankommen: Ein Ersatzpaket wird geschickt.",
    ))),

    # --- NT · Ausdehnungen ---------------------------------------------------
    ("NT", SCOPE, "Netzwerktypen", _block("Netzwerktypen", (
        f"WAN: {WAN}",
        f"MAN: {MAN}",
        f"LAN: {LAN}",
        f"PAN: {PAN}",
        f"CAN: {CAN}",
        f"BAN: {BAN}",
    ))),

    # --- NT · Adressbereiche -------------------------------------------------
    ("NT", ADDR, "Private Adressbereiche", _block("Private Adressbereiche", (
        PRIVATE_RANGE,
        PRIVATE_RANGE_172,
        PRIVATE_RANGE_192,
        "",
        PRIVATE_DESC,
    ))),
    ("NT", ADDR, "Loopback-Adressen", _block("Loopback-Adressen", (
        LOOPBACK_RANGE,
        "",
        LOOPBACK_DESC,
    ))),
    ("NT", ADDR, "Link-lokale Adressen", _block("Link-lokale Adressen", (
        LINK_LOCAL_RANGE,
        "",
        LINK_LOCAL_DESC,
    ))),
    ("NT", ADDR, "Netzklassen", _block("Netzklassen", (
        "Netzklassen A-E sind nicht mehr relevant.",
        "",
        "Relevant ist noch: Class-full Routing",
    ))),
)


def seed_infos(connection):
    """Insert every info section that is not stored yet; re-running is a no-op."""
    stored = {
        (subject, topic, heading)
        for subject, topic, heading in connection.execute(
            """SELECT s.name, t.name, i.heading
               FROM infos i
               JOIN topics t ON t.id = i.topic_id
               JOIN subjects s ON s.id = t.subject_id"""
        )
    }
    missing = [
        (position, entry)
        for position, entry in enumerate(INFO_BANK)
        if (entry[0], entry[1], entry[2]) not in stored
    ]
    if not missing:
        return

    connection.executemany(
        """INSERT INTO infos(topic_id, heading, body, position)
           SELECT t.id, ?, ?, ?
           FROM topics t JOIN subjects s ON s.id = t.subject_id
           WHERE s.name = ? AND t.name = ?
             AND NOT EXISTS (
                 SELECT 1 FROM infos i
                 WHERE i.topic_id = t.id AND i.heading = ?
             )""",
        [
            (heading, body, position, subject, topic, heading)
            for position, (subject, topic, heading, body) in missing
        ],
    )
