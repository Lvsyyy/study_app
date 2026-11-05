SCHEMA_VERSION = 20

DEFAULT_SUBJECTS = ("NT", "AE", "Math", "CS_P", "CS", "English", "BS", "PuG", "Ethik")

# Version 1 is the base schema. Migrations are applied in ascending order.
MIGRATIONS = {
    20: """
    UPDATE questions
    SET answer='{"pairs":[{"left":"80","right":"Datenpakete (HTTP)"},{"left":"25","right":"E-Mails (SMTP)"}]}'
    WHERE question_text='Wofür werden die Eingänge 80 und 25 genutzt?'
      AND question_type='matching'
      AND topic_id IN (
        SELECT t.id FROM topics t
        JOIN subjects s ON s.id=t.subject_id
        WHERE s.name='NT'
      );
    """,

    19: """
    UPDATE questions
    SET answer='{"pairs":[{"left":"Verbindung und Kommunikation zwischen verschiedenen Geräten und Systemen, um Datenaustausch zu ermöglichen","right":"Definition der Vernetzung"},{"left":"Einfache Kommunikation, Erweiterkeit, einfache Verwaltung, Verfügbarkeit","right":"Vorteile eines Netzwerkes"},{"left":"Router, IPS, Computer, Ethernet Kabel, Server, Switch","right":"Was benötigen Sie, um IT-Netzwerke einrichten zu können?"},{"left":"Das man die richtigen IPs vergibt und das die Frequenz des Gerätes unterstüzt ist","right":"Was ist bei der Einrichtung von Netzwerken zu beachten?"},{"left":"Falsche Konfiguration, Signal Störungen, Geräte sind nicht sofot seebar, Kosten","right":"Welche Schwierigkeiten können bei der Einrichtung eines Netzwerkes auftreten?"},{"left":"Was bedeutet Shared Medium?","right":"Wenn Knoten sich ein Übertragungsmedium teilen"},{"left":"Was bedeutet Single Point of Failure?","right":"Die Stelle im Netz die den Netzverkehr steuert"},{"left":"Was passiert mit Datenpaketen, die nicht ankommen?","right":"Ein Ersatz Pakete wird geschickt"},{"left":"Welche Cloud-Arten gibt es?","right":"Public Cloud; Private Cloud"}]}'
    WHERE question_text='Ordne jede Aussage der passenden Kategorie zu.'
      AND topic_id IN (
        SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id
        WHERE s.name='NT'
      );

    DELETE FROM questions
    WHERE question_text IN (
        'Was bedeutet Shared Medium?',
        'Was bedeutet Single Point of Failure?',
        'Was passiert mit Datenpaketen, die nicht ankommen?',
        'Welche Cloud-Arten gibt es?'
    )
      AND topic_id IN (
        SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id
        WHERE s.name='NT'
      );

    UPDATE questions
    SET question_type='table_sort',
        answer='{"categories":["IaaS","PaaS","SaaS"],"cards":[{"text":"Infrastructure as a Service","category":"IaaS"},{"text":"Zurverfügungstellung und Nutzung von Infrastrukturkomponenten","category":"IaaS"},{"text":"Platform as a Service","category":"PaaS"},{"text":"Bereitstellung von Laufzeit- und Entwicklungsplattformen","category":"PaaS"},{"text":"Software as a Service","category":"SaaS"},{"text":"Angebot von Software zur Nutzung von Geschäftsprozessen","category":"SaaS"}]}'
    WHERE question_text='Ordne die Serviceart der passenden Beschreibung zu.'
      AND topic_id IN (
        SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id
        WHERE s.name='NT'
      );

    UPDATE questions
    SET question_type='table_sort',
        answer='{"categories":["WAN","MAN","LAN","PAN","CAN","BAN"],"cards":[{"text":"Weltumspannend","category":"WAN"},{"text":"Unterseekabel / Internet","category":"WAN"},{"text":"Bis zu 100km","category":"MAN"},{"text":"Öffentliches Telefonnetz, Stadtnetzwerk","category":"MAN"},{"text":"Ca. 100m","category":"LAN"},{"text":"Computers, TV, Konsolen","category":"LAN"},{"text":"Ca. 10m","category":"PAN"},{"text":"Bluetooth, USB, Infrarot","category":"PAN"},{"text":"0,1 bis 10m","category":"CAN"},{"text":"Mikrokontroller / elektronische Steuergeräte in Autos (CAN-Bus)","category":"CAN"},{"text":"0,1 bis 1m","category":"BAN"},{"text":"Medizinischen Sensoren, Smart Watch","category":"BAN"}]}'
    WHERE question_text='Ordne jedem Netzwerktyp Reichweite und Beispiele zu.'
      AND topic_id IN (
        SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id
        WHERE s.name='NT'
      );
    """,

    18: """
    UPDATE questions
    SET question_text='Was ist im Zusammenhang mit Netzklassen noch relevant?',
        question_type='text',
        answer='Class-full Routing',
        topic_id=(
            SELECT id FROM topics
            WHERE subject_id=(SELECT id FROM subjects WHERE name='NT')
              AND name='Adressbereiche'
        )
    WHERE question_text IN (
        'Welche Aussagen zu den historischen IPv4-Netzklassen sind korrekt?',
        'Ordne die Angaben zu den Netzklassen zu.'
    )
      AND topic_id IN (
        SELECT t.id FROM topics t
        JOIN subjects s ON s.id=t.subject_id
        WHERE s.name='NT'
    );

    UPDATE questions
    SET question_type='matching',
        answer='{"pairs":[{"left":"80","right":"80 für Datenpakete (HTTP)"},{"left":"25","right":"25 für E-Mails (SMTP)"}]}'
    WHERE question_text='Wofür werden die Eingänge 80 und 25 genutzt?'
      AND topic_id IN (
        SELECT t.id FROM topics t
        JOIN subjects s ON s.id=t.subject_id
        WHERE s.name='NT'
    );

    UPDATE questions
    SET topic_id=(
        SELECT id FROM topics
        WHERE subject_id=(SELECT id FROM subjects WHERE name='NT')
          AND name='Topologien'
    )
    WHERE question_text='Was bedeutet Single Point of Failure?'
      AND topic_id IN (
        SELECT t.id FROM topics t
        JOIN subjects s ON s.id=t.subject_id
        WHERE s.name='NT'
    );
    """,


    17: """
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Grundbasis' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Ausdehnungen' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Topologien' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Architekturen' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Kommunikationsteilnehmer' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Adressbereiche' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name)
    SELECT id, 'Subnetting' FROM subjects WHERE name='NT';

    UPDATE questions
    SET topic_id=(SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name='Grundbasis')
    WHERE topic_id IN (SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name IN ('Netzwerkgrundlagen','Allgemeine Netzwerktechnik','IP-Paket'));

    UPDATE questions
    SET topic_id=(SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name='Ausdehnungen')
    WHERE topic_id IN (SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name='Netzwerkgrößen');

    UPDATE questions
    SET topic_id=(SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name='Topologien')
    WHERE topic_id IN (SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name='Topologien Mischformen');

    UPDATE questions
    SET topic_id=(SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name='Architekturen')
    WHERE topic_id IN (SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name IN ('Architekturtypen','Cloud Computing'));

    UPDATE questions
    SET topic_id=(SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name='Kommunikationsteilnehmer')
    WHERE topic_id IN (SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name IN ('Kommunizierungsrichtungen','Netzwerkgeräte'));

    UPDATE questions
    SET topic_id=(SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name='Adressbereiche')
    WHERE topic_id IN (SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name='Netzklassen');

    UPDATE questions
    SET topic_id=(SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT') AND name='Grundbasis')
    WHERE topic_id IN (
        SELECT id FROM topics
        WHERE subject_id=(SELECT id FROM subjects WHERE name='NT')
          AND name NOT IN ('Grundbasis','Ausdehnungen','Topologien','Architekturen','Kommunikationsteilnehmer','Adressbereiche','Subnetting')
    );

    UPDATE questions
    SET question_text='Welche Aussagen zu den historischen IPv4-Netzklassen sind korrekt?',
        question_type='multi_select',
        answer='{"options":["Die Netzklasse B hatte standardmäßig die Subnetzmaske 255.255.0.0 (/16).","Die Netzklasse D wurde für Multicast verwendet.","Classful Addressing wurde durch CIDR abgelöst.","Die Netzklasse A hatte standardmäßig die Subnetzmaske 255.0.0.0 (/8).","Die Netzklasse C hatte standardmäßig die Subnetzmaske 255.255.255.0 (/24).","Die Netzklasse E war für experimentelle Zwecke reserviert.","Die Netzklasse A verwendete standardmäßig /24.","Die Netzklasse B war für Multicast reserviert.","Die Netzklasse C umfasste Adressen ab 224.0.0.0.","Classful Addressing ist heute der Standard und hat CIDR ersetzt.","Die Netzklasse D war für normale private LAN-Clients vorgesehen.","Die Netzklassen A, B und C hatten alle dieselbe Standard-Subnetzmaske."],"correct":[0,1,2,3,4,5]}'
    WHERE question_text='Ordne die Angaben zu den Netzklassen zu.'
      AND topic_id IN (SELECT id FROM topics WHERE subject_id=(SELECT id FROM subjects WHERE name='NT'));

    DELETE FROM topics
    WHERE subject_id=(SELECT id FROM subjects WHERE name='NT')
      AND name NOT IN ('Grundbasis','Ausdehnungen','Topologien','Architekturen','Kommunikationsteilnehmer','Adressbereiche','Subnetting');
    """,

    16: """
    UPDATE questions
    SET topic_id = (
        SELECT target.id
        FROM topics target
        JOIN subjects s ON s.id = target.subject_id
        WHERE s.name = 'NT' AND target.name = 'Allgemeine Netzwerktechnik'
    )
    WHERE question_text IN (
        'Was bedeutet Single Point of Failure?',
        'Was passiert mit Datenpaketen, die nicht ankommen?'
    )
      AND topic_id IN (
        SELECT source.id
        FROM topics source
        JOIN subjects s ON s.id = source.subject_id
        WHERE s.name = 'NT'
    )
      AND EXISTS (
        SELECT 1
        FROM topics target
        JOIN subjects s ON s.id = target.subject_id
        WHERE s.name = 'NT' AND target.name = 'Allgemeine Netzwerktechnik'
    );
    """,


    15: """
    UPDATE questions
    SET question_type='table_sort',
        answer='{"categories":["Bus","Stern","Ring"],"cards":[{"text":"Aufbau: Zentrales Kabel verbindet alle Geräte","category":"Bus"},{"text":"Anwendung: Kleineren lokalen Netzen in 90er Jahre","category":"Bus"},{"text":"Vorteile: Passive Topologie, Erweiterbarkeit, Günstig","category":"Bus"},{"text":"Nachteile: Nur ein Medium, Nicht unendlich","category":"Bus"},{"text":"Aufbau: Geräte separat angeschlossen, Zentralen Verteiler (Switch)","category":"Stern"},{"text":"Anwendung: Häufigste Netzwerkstruktur, Neuinstallation auf Etagen- oder Gebäudeebene","category":"Stern"},{"text":"Vorteile: Kein Einzelpunktausfall, Erweiterbarkeit, Verteiler = Signalverstärker","category":"Stern"},{"text":"Nachteile: Große Kabelmenge, Hohe Kosten, Kein Verteiler = kein Netzverkehr","category":"Stern"},{"text":"Aufbau: Alle Knoten an einen Ring verbunden, Datenverkehr eine Richtung","category":"Ring"},{"text":"Anwendung: Automatisierungstechnik","category":"Ring"},{"text":"Vorteile: Knoten verarbeiten und verstärken die Signale, Einfache Fehlersuche","category":"Ring"},{"text":"Nachteile: Datenverkehr nur in eine Richtung, Hoher Aufwand der Kabelverlegung, Schwere Erweiterbarkeit","category":"Ring"}]}'
    WHERE question_text='Ordne Aufbau, Anwendung, Vorteile und Nachteile der passenden Topologie zu.'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Topologien');

    UPDATE questions
    SET question_type='table_sort',
        answer='{"categories":["Stern-Stern","Baum-Topologie","Maschennetz"],"cards":[{"text":"Aufbau: Multilayerswitch verbindet Switches mit Glasfaser","category":"Stern-Stern"},{"text":"Anwendung: In mehr stöckigen Bürogebäude","category":"Stern-Stern"},{"text":"Aufbau: Wurzle die zu Verteilungsstellen führt","category":"Baum-Topologie"},{"text":"Anwendung: Firmengelände verbindet Gebäude","category":"Baum-Topologie"},{"text":"Aufbau: Baum-Topologie aber alle Netzknoten sind verbunden (redundant)","category":"Maschennetz"},{"text":"Anwendung: Sicherheitsrelevanten lokalen Netzen, Weitverkehrsnetzen","category":"Maschennetz"}]}'
    WHERE question_text='Ordne Aufbau und Anwendung der passenden Mischform zu.'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Topologien Mischformen');

    UPDATE questions
    SET question_type='table_sort',
        answer='{"categories":["Client/Server-Architekturen","Peer-to-Peer","Monolithische Anwendungssysteme","Cloud Computing"],"cards":[{"text":"Beschreibung: Jeder Rechner ist gleichberechtigt und jeder Nutzer ist ein Admin und arbeitet mit eigenen Betriebsmitteln (Software)","category":"Peer-to-Peer"},{"text":"Vorteile: Preiswerte Implementierung (Günstig); Kein Netzwerkbetriebssystem vorausgesetzt; Kein Netzwerkadministrator notwending","category":"Peer-to-Peer"},{"text":"Nachteile: Schlechte Skalierbarkeit bei großen Netzwerken; Sicherheitsprobleme; Jeder Nutzer benötigt Administrationskenntnisse","category":"Peer-to-Peer"},{"text":"Beschreibung: Wird verwaltet auf zentralen Server / Rechner mit verteileten Ressourcen","category":"Client/Server-Architekturen"},{"text":"Vorteile: Zentralisierte Administration; Skalierbarkeit und flexible Architektur; Verbesserte Sicherheit","category":"Client/Server-Architekturen"},{"text":"Nachteile: Server verlangen höherwertige Ausstattung (Teuer); Administrator notwendig; Single Point of Failure in Form des Servers","category":"Client/Server-Architekturen"},{"text":"Beschreibung: Bietet Nutzern / Unternehmen eigenes IT-Infrakstruktur wenn nichts vorhanden ist","category":"Cloud Computing"},{"text":"Vorteile: Schnelle Verfügbarkeit; Geringer Aufwand (Keine Kabelverlegung / IT-Infrastruktur); Kosten senken; Technische und wirtschaftliche Vorteile; Hohe Skalierbarkeit (Mehr Speicher) und Flexibilität","category":"Cloud Computing"},{"text":"Nachteile: Datenschutz, Datensicherheit, mangelndes Vertrauen; Abhängigkeit von Internetverbindung; Abhängigkeit vom Cloud-Anbieter; Kann nicht einfach Anbieter wechseln","category":"Cloud Computing"}]}'
    WHERE question_text='Ordne die Beschreibungen, Vorteile und Nachteile dem passenden Architekturtyp zu.'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Architekturtypen');
    """,

    14: """
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Architekturtypen' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Cloud Computing' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Topologien' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Topologien Mischformen' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Netzwerkgrundlagen' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Kommunizierungsrichtungen' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Kommunikationsteilnehmer' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Netzwerkgrößen' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Netzklassen' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Adressbereiche' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'IP-Paket' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Netzwerkgeräte' FROM subjects WHERE name='NT';
    INSERT OR IGNORE INTO topics(subject_id, name) SELECT id, 'Allgemeine Netzwerktechnik' FROM subjects WHERE name='NT';
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne die Beschreibungen, Vorteile und Nachteile dem passenden Architekturtyp zu.', '{"pairs":[{"left":"Beschreibung: Jeder Rechner ist gleichberechtigt und jeder Nutzer ist ein Admin und arbeitet mit eigenen Betriebsmitteln (Software)","right":"Peer-to-Peer"},{"left":"Vorteile: Preiswerte Implementierung (Günstig); Kein Netzwerkbetriebssystem vorausgesetzt; Kein Netzwerkadministrator notwending","right":"Peer-to-Peer"},{"left":"Nachteile: Schlechte Skalierbarkeit bei großen Netzwerken; Sicherheitsprobleme; Jeder Nutzer benötigt Administrationskenntnisse","right":"Peer-to-Peer"},{"left":"Beschreibung: Wird verwaltet auf zentralen Server / Rechner mit verteileten Ressourcen","right":"Client/Server-Architekturen"},{"left":"Vorteile: Zentralisierte Administration; Skalierbarkeit und flexible Architektur; Verbesserte Sicherheit","right":"Client/Server-Architekturen"},{"left":"Nachteile: Server verlangen höherwertige Ausstattung (Teuer); Administrator notwendig; Single Point of Failure in Form des Servers","right":"Client/Server-Architekturen"},{"left":"Beschreibung: Bietet Nutzern / Unternehmen eigenes IT-Infrakstruktur wenn nichts vorhanden ist","right":"Cloud Computing"},{"left":"Vorteile: Schnelle Verfügbarkeit; Geringer Aufwand (Keine Kabelverlegung / IT-Infrastruktur); Kosten senken; Technische und wirtschaftliche Vorteile; Hohe Skalierbarkeit (Mehr Speicher) und Flexibilität","right":"Cloud Computing"},{"left":"Nachteile: Datenschutz, Datensicherheit, mangelndes Vertrauen; Abhängigkeit von Internetverbindung; Abhängigkeit vom Cloud-Anbieter; Kann nicht einfach Anbieter wechseln","right":"Cloud Computing"},{"left":"Monolithische Anwendungssysteme","right":"Monolithische Anwendungssysteme"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Architekturtypen' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne die Beschreibungen, Vorteile und Nachteile dem passenden Architekturtyp zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne die Serviceart der passenden Beschreibung zu.', '{"pairs":[{"left":"IaaS (Infrastructure as a Service)","right":"Zurverfügungstellung und Nutzung von Infrastrukturkomponenten"},{"left":"PaaS (Platform as a Service)","right":"Bereitstellung von Laufzeit- und Entwicklungsplattformen"},{"left":"SaaS (Software as a Service)","right":"Angebot von Software zur Nutzung von Geschäftsprozessen"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Cloud Computing' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne die Serviceart der passenden Beschreibung zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Welche Cloud-Arten gibt es?', 'Public Cloud; Private Cloud', '', 2, 'text' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Cloud Computing' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Welche Cloud-Arten gibt es?');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne Aufbau, Anwendung, Vorteile und Nachteile der passenden Topologie zu.', '{"pairs":[{"left":"Bus – Aufbau: Zentrales Kabel verbindet alle Geräte","right":"Bus"},{"left":"Bus – Anwendung: Kleineren lokalen Netzen in 90er Jahre","right":"Bus"},{"left":"Bus – Vorteile: Passive Topologie, Erweiterbarkeit, Günstig","right":"Bus"},{"left":"Bus – Nachteile: Nur ein Medium, Nicht unendlich","right":"Bus"},{"left":"Stern – Aufbau: Geräte separat angeschlossen, Zentralen Verteiler (Switch)","right":"Stern"},{"left":"Stern – Anwendung: Häufigste Netzwerkstruktur, Neuinstallation auf Etagen- oder Gebäudeebene","right":"Stern"},{"left":"Stern – Vorteile: Kein Einzelpunktausfall, Erweiterbarkeit, Verteiler = Signalverstärker","right":"Stern"},{"left":"Stern – Nachteile: Große Kabelmenge, Hohe Kosten, Kein Verteiler = kein Netzverkehr","right":"Stern"},{"left":"Ring – Aufbau: Alle Knoten an einen Ring verbunden, Datenverkehr eine Richtung","right":"Ring"},{"left":"Ring – Anwendung: Automatisierungstechnik","right":"Ring"},{"left":"Ring – Vorteile: Knoten verarbeiten und verstärken die Signale, Einfache Fehlersuche","right":"Ring"},{"left":"Ring – Nachteile: Datenverkehr nur in eine Richtung, Hoher Aufwand der Kabelverlegung, Schwere Erweiterbarkeit","right":"Ring"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Topologien' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne Aufbau, Anwendung, Vorteile und Nachteile der passenden Topologie zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne Aufbau und Anwendung der passenden Mischform zu.', '{"pairs":[{"left":"Stern-Stern – Aufbau: Multilayerswitch verbindet Switches mit Glasfaser","right":"Stern-Stern"},{"left":"Stern-Stern – Anwendung: In mehr stöckigen Bürogebäude","right":"Stern-Stern"},{"left":"Baum-Topologie – Aufbau: Wurzle die zu Verteilungsstellen führt","right":"Baum-Topologie"},{"left":"Baum-Topologie – Anwendung: Firmengelände verbindet Gebäude","right":"Baum-Topologie"},{"left":"Maschennetz – Aufbau: Baum-Topologie aber alle Netzknoten sind verbunden (redundant)","right":"Maschennetz"},{"left":"Maschennetz – Anwendung: Sicherheitsrelevanten lokalen Netzen, Weitverkehrsnetzen","right":"Maschennetz"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Topologien Mischformen' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne Aufbau und Anwendung der passenden Mischform zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Was bedeutet Shared Medium?', 'Wenn Knoten sich ein Übertragungsmedium teilen', '', 2, 'text' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Topologien' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Was bedeutet Shared Medium?');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Was bedeutet Single Point of Failure?', 'Die Stelle im Netz die den Netzverkehr steuert', '', 2, 'text' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Topologien' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Was bedeutet Single Point of Failure?');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne jedem Begriff die passende Beschreibung zu.', '{"pairs":[{"left":"Rechnern oder Knoten","right":"Verbindbare Komponenten"},{"left":"Infrastrukturkomponenten","right":"Datensignale leiten, Datenverkehr klassifizieren - erlauben - unterbinden"},{"left":"Verkabelung / Übertragungsmedien","right":"Physikalische / drahtlose Verbindung (LAN Kabel, WLAN)"},{"left":"Protokoll","right":"Definiert Regeln für Narichtenaustausch"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Netzwerkgrundlagen' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne jedem Begriff die passende Beschreibung zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne jeder Kommunikationsrichtung die passende Beschreibung zu.', '{"pairs":[{"left":"simplex","right":"Nachritenfluss in nur eine Richtung von Sender zu Empfänger"},{"left":"half-duplex","right":"Jeder Knoten kann senden und empfangen jedoch nur abwechselnd"},{"left":"duplex","right":"Jeder Knoten kann Nachrichten jeweils gleichzeitig senden als auch empfangen"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Kommunizierungsrichtungen' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne jeder Kommunikationsrichtung die passende Beschreibung zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne jedem Kommunikationsteilnehmer die passende Beschreibung zu.', '{"pairs":[{"left":"Unicast One-to-One Kommunikation","right":"Punkt zu Punkt Verbindung mit Zuordnung von Sender mit genau einem Empfänger"},{"left":"Anycast One-to-nearest Kommunikation","right":"Punkt zu Punkt Verbindung mit Zuordnung von Sender mit dem nächstliegenden Empfänger einer Gruppe"},{"left":"Multicast One-to-many Kommunikmation","right":"Verbindung zu einer ausgewählten Gruppe mit Zuordnung von Sender zu mehreren Empfängern"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Kommunikationsteilnehmer' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne jedem Kommunikationsteilnehmer die passende Beschreibung zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne jedem Netzwerktyp Reichweite und Beispiele zu.', '{"pairs":[{"left":"WAN","right":"Weltumspannend; Unterseekabel / Internet"},{"left":"MAN","right":"Bis zu 100km; Öffentliches Telefonnetz, Stadtnetzwerk"},{"left":"LAN","right":"Ca. 100m; Computers, TV, Konsolen"},{"left":"PAN","right":"Ca. 10m; Bluetooth, USB, Infrarot"},{"left":"CAN","right":"0,1 bis 10m; Mikrokontroller / elektronische Steuergeräte in Autos (CAN-Bus)"},{"left":"BAN","right":"0,1 bis 1m; Medizinischen Sensoren, Smart Watch"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Netzwerkgrößen' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne jedem Netzwerktyp Reichweite und Beispiele zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne die Angaben zu den Netzklassen zu.', '{"pairs":[{"left":"Netzklassen A-E","right":"nicht mehr relevant"},{"left":"Class-full Routing","right":"Netzklassen A-E"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Netzklassen' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne die Angaben zu den Netzklassen zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne jedem Adressbereich die passende Bedeutung und Information zu.', '{"pairs":[{"left":"10.x.x.x/8","right":"Adressbereich für private Netzwerke; Adressen aus diesem Bereich dürfen nicht im öffentlichen Internet verwendet werden"},{"left":"172.16.0.0/12 - 172.31.255.255/12","right":"Adressbereich für private Netzwerke; Adressen aus diesem Bereich dürfen nicht im öffentlichen Internet verwendet werden"},{"left":"192.168.x.x/16","right":"Adressbereich für private Netzwerke; Adressen aus diesem Bereich dürfen nicht im öffentlichen Internet verwendet werden"},{"left":"127.0.0.0 - 127.255.255.255","right":"Loopback-Adressen; Jedes an diese Adresse gesendete Paket soll den Host nicht verlassen sondern intern zurückgeschikt werden"},{"left":"169.254.0.0 - 169.254.255.255","right":"Link-lokale Adressen; Weist sich der Rechner selbst zu wenn die automatische Konfiguration per DHCP fehlgeschlagen hat; Link-lokale Adressen liegen im selben Adressbereich; Kommunikation zwischen Clients im lokalen Netz möglich"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Adressbereiche' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne jedem Adressbereich die passende Bedeutung und Information zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Welche Informationen stehen auf einem IP-Paket? Wähle alle passenden Antworten.', '{"options":["IP-Header","Empfänger","Absender","Proxy Server Adresse","Pakettyp","MAC-Adresse des Switches","WLAN-Passwort","Bildschirmauflösung"],"correct":[0,1,2,3,4]}', '', 2, 'multi_select' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='IP-Paket' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Welche Informationen stehen auf einem IP-Paket? Wähle alle passenden Antworten.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne jedem Begriff die passende Beschreibung zu.', '{"pairs":[{"left":"Router","right":"Sucht den Weg für die Datenpakete"},{"left":"Switch","right":"Verbindet Computer innerhalb eines Netzwerks, Steuert den Datenverkehr"},{"left":"Proxy","right":"Belastung abzunehmen und für Sicherheit, Vermittelt zwischen Computer und Internet"},{"left":"Firewall","right":"Kontrolliert die Datenpakete, Blockiert nicht erlaubte Pakete"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Netzwerkgeräte' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne jedem Begriff die passende Beschreibung zu.');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Was passiert mit Datenpaketen, die nicht ankommen?', 'Ein Ersatz Pakete wird geschickt', '', 2, 'text' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Netzwerkgeräte' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Was passiert mit Datenpaketen, die nicht ankommen?');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Firewall Eingängen. Wie heißen diese in der Fachsprache?', 'Ports', '', 2, 'text' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Netzwerkgeräte' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Firewall Eingängen. Wie heißen diese in der Fachsprache?');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Wofür werden die Eingänge 80 und 25 genutzt?', '80 für Datenpakete (HTTP), 25 für E-Mails (SMTP)', '', 2, 'text' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Netzwerkgeräte' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wofür werden die Eingänge 80 und 25 genutzt?');
    
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Ordne jede Aussage der passenden Kategorie zu.', '{"pairs":[{"left":"Verbindung und Kommunikation zwischen verschiedenen Geräten und Systemen, um Datenaustausch zu ermöglichen","right":"Definition der Vernetzung"},{"left":"Einfache Kommunikation, Erweiterkeit, einfache Verwaltung, Verfügbarkeit","right":"Vorteile eines Netzwerkes"},{"left":"Router, IPS, Computer, Ethernet Kabel, Server, Switch","right":"Was benötigen Sie, um IT-Netzwerke einrichten zu können?"},{"left":"Das man die richtigen IPs vergibt und das die Frequenz des Gerätes unterstüzt ist","right":"Was ist bei der Einrichtung von Netzwerken zu beachten?"},{"left":"Falsche Konfiguration, Signal Störungen, Geräte sind nicht sofot seebar, Kosten","right":"Welche Schwierigkeiten können bei der Einrichtung eines Netzwerkes auftreten?"}]}', '', 2, 'matching' FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='NT' AND t.name='Allgemeine Netzwerktechnik' AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Ordne jede Aussage der passenden Kategorie zu.');
    """,

    13: """
    UPDATE questions
    SET alt_answers = '["System Information (A7)","MsInfo32 (A2)","Aufkleber (A3)","Webseite des Herstellers (A4)","Handbuch (A5)","Tools (A6)"]'
    WHERE question_text='Welche Möglichkeiten gibt es, die installierte BIOS-Version zu ermitteln? Wähle alle passenden Antworten.'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='BS' AND t.name='BIOS update');

    UPDATE questions
    SET alt_answers = '["Wichtige Dateien"]'
    WHERE question_text='Welche Daten sollten vor einem BIOS-Update gesichert werden?'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='BS' AND t.name='BIOS update');

    UPDATE questions
    SET answer='Mit einem Backup ist sofortiger Zugriff auf die Festplatte möglich.',
        alt_answers='["Mit einem Backup ist sofortiger Zugriff auf wichtige Dateien möglich.","Mit einem Backup hat man sofortigen Zugriff auf die gesicherten Daten."]'
    WHERE question_text='Warum kann ein Backup trotz eines BIOS-Update-Fehlers, bei dem normalerweise keine Daten verloren gehen, sinnvoll sein?'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='BS' AND t.name='BIOS update');

    UPDATE questions
    SET question_text='Ordne die acht Schritte eines BIOS-Updates den Nummern 1–8 zu.',
        answer='{"items":["Mainboard und BIOS/UEFI-Version identifizieren","Update-Dateien finden und herunterladen","Backup wichtiger Dateien erstellen","Update-Methode wählen: Windows, UEFI-Flash-Menü oder bei alten Hauptplatinen DOS","BIOS vorbereiten: Schreibschutz prüfen und Einstellungen speichern","BIOS-Update durchführen","BIOS aufräumen: CMOS löschen und Strom entfernen","Bei Problemen das alte BIOS wiederherstellen"]}'
    WHERE question_text LIKE '%Schritte%BIOS-Update%'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='BS' AND t.name='BIOS update')
      AND question_type='ordering';

    UPDATE questions
    SET question_text='Ordne die Schritte des POST in die richtige Reihenfolge.',
        answer='{"items":["Funktionsfähigkeit der CPU prüfen","CPU-nahe Bausteine prüfen","CMOS-RAM prüfen","CPU-nahen Cache-Speicher prüfen","Erste 64 Kilobyte des Arbeitsspeichers prüfen","Grafikspeicher und Grafikausgabe prüfen"]}'
    WHERE question_text LIKE '%POST%Reihenfolge%'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='BS' AND t.name LIKE 'Bootvorgang%')
      AND question_type='ordering';

    UPDATE questions
    SET answer='{"nodes":[{"id":1,"type":"Start/End","text":"Start des Bootvorgangs"},{"id":2,"type":"Process","text":"PC einschalten"},{"id":3,"type":"Process","text":"BIOS laden"},{"id":4,"type":"Process","text":"Selbsttest (POST)"},{"id":5,"type":"Decision","text":"Hardware OK?"},{"id":6,"type":"Process","text":"CMOS lesen"},{"id":7,"type":"Process","text":"Grundkonfiguration der Komponenten"},{"id":8,"type":"Decision","text":"Betriebssystem vorhanden?"},{"id":9,"type":"Process","text":"Betriebssystem starten"},{"id":10,"type":"Start/End","text":"Betriebssystem geladen"},{"id":11,"type":"Process","text":"Fehlermeldung"},{"id":12,"type":"Process","text":"Fehlerbeseitigung"},{"id":13,"type":"Process","text":"PC ausschalten"}],"edges":[{"from":1,"to":2,"label":"Normal"},{"from":2,"to":3,"label":"Normal"},{"from":3,"to":4,"label":"Normal"},{"from":4,"to":5,"label":"Normal"},{"from":5,"to":6,"label":"Ja"},{"from":5,"to":11,"label":"Nein"},{"from":6,"to":7,"label":"Normal"},{"from":7,"to":8,"label":"Normal"},{"from":8,"to":9,"label":"Ja"},{"from":8,"to":11,"label":"Nein"},{"from":9,"to":10,"label":"Normal"},{"from":11,"to":12,"label":"Normal"},{"from":12,"to":13,"label":"Normal"},{"from":13,"to":1,"label":"Normal"}]}'
    WHERE question_type='pap'
      AND question_text LIKE 'Erstelle einen PAP für den Bootvorgang%'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='BS' AND t.name LIKE 'Bootvorgang%');

    UPDATE questions
    SET answer='{"expected_output":["Pfad>Das ist eine Ausgabe"],"inputs":[],"solution":"echo Das ist eine Ausgabe"}'
    WHERE question_text LIKE '%Pfad%Das ist eine Ausgabe%'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='BS' AND t.name='Batch')
      AND question_type='batch';

    """,


    12: """
    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Welche Daten sollten vor einem BIOS-Update gesichert werden?',
           'Wichtige Daten und wichtige Dateien.',
           'Sichere wichtige persönliche Dateien und andere wichtige Daten.',
           1, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='BIOS update'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Welche Daten sollten vor einem BIOS-Update gesichert werden?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Warum kann ein Backup trotz eines BIOS-Update-Fehlers, bei dem normalerweise keine Daten verloren gehen, sinnvoll sein?',
           'Mit einem Backup ist ein sofortiger Zugriff auf die gesicherten Daten möglich.',
           'Denke daran, wie schnell du nach einem Problem wieder auf wichtige Dateien zugreifen kannst.',
           2, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='BIOS update'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Warum kann ein Backup trotz eines BIOS-Update-Fehlers, bei dem normalerweise keine Daten verloren gehen, sinnvoll sein?');

    UPDATE questions
    SET answer = '{"options":["Systeminformation","System Information (A7)","MsInfo32 (A2)","Aufkleber (A3)","Webseite des Herstellers (A4)","Handbuch (A5)","Tools (A6)"],"correct":[0,1,2,3,4,5,6]}'
    WHERE question_text='Welche Möglichkeiten gibt es, die installierte BIOS-Version zu ermitteln? Wähle alle passenden Antworten.'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='BS' AND t.name='BIOS update');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Wofür steht BIOS?',
           'Basic Input / Output System',
           'Basic Input / Output System',
           1, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Bootvorgang'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wofür steht BIOS?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Wofür steht UEFI?',
           'Unified Extensible Firmware Interface',
           'Unified Extensible Firmware Interface',
           1, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Bootvorgang'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wofür steht UEFI?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Wofür steht CMOS?',
           'Complementary metal oxide semiconductor',
           'Complementary metal oxide semiconductor',
           1, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Bootvorgang'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wofür steht CMOS?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Wofür steht CPU?',
           'Central Processing Unit',
           'Central Processing Unit',
           1, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Bootvorgang'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wofür steht CPU?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Wofür steht POST?',
           'Power On Self Test',
           'Power On Self Test',
           1, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Bootvorgang'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wofür steht POST?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Was versteht man unter POST?',
           'Ein Selbsttest, der nach dem Einschalten durchgeführt wird. Er prüft beim Hochfahren die Funktionsfähigkeit der grundlegenden Komponenten des Geräts.',
           'POST ist der Selbsttest direkt nach dem Einschalten.',
           2, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Bootvorgang'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Was versteht man unter POST?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Welche Bedeutung hat das BIOS / UEFI für den PC?',
           'BIOS und UEFI bereiten alles für das Betriebssystem vor.',
           'Sie initialisieren und prüfen die Hardware und leiten den Betriebssystemstart ein.',
           2, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Bootvorgang'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Welche Bedeutung hat das BIOS / UEFI für den PC?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Worin liegt der Unterschied zwischen EFI und UEFI?',
           'EFI ist herstellerspezifisch, UEFI ist standardisiert.',
           'Achte darauf, ob die Firmware-Schnittstelle herstellerspezifisch oder standardisiert ist.',
           2, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Bootvorgang'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Worin liegt der Unterschied zwischen EFI und UEFI?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Was ist Secure Boot und welches Problem kann dadurch entstehen?',
           'Secure Boot überprüft digitale Signaturen. Nicht signierte bzw. nicht unterstützte Firmware kann dadurch blockiert werden.',
           'Secure Boot prüft digitale Signaturen beim Start.',
           3, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Bootvorgang'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Was ist Secure Boot und welches Problem kann dadurch entstehen?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Wie kann die Bootreihenfolge eines PCs verändert werden?',
           'Im Boot Priority Menü.',
           'Suche die Einstellung für die Startreihenfolge in den Firmware-Einstellungen.',
           1, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Bootvorgang'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wie kann die Bootreihenfolge eines PCs verändert werden?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Warum kann die Geschwindigkeit (insbesondere die Zugriffszeit) bei Festplatten nicht beliebig gesteigert werden?',
           'Festplatten bestehen aus beweglichen Teilen. Physikalische und materielle Grenzen müssen akzeptiert werden.',
           'Denke an die mechanischen, beweglichen Bauteile einer Festplatte.',
           2, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Festplatten'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Warum kann die Geschwindigkeit (insbesondere die Zugriffszeit) bei Festplatten nicht beliebig gesteigert werden?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Welche Faktoren beeinflussen die Zugriffszeit einer Festplatte?',
           'Suchzeit (Average Seek Time) und Zugriffsverzögerung durch Umdrehung (Average Rotational Latency Time).',
           'Es gibt eine Zeit für die Bewegung des Schreib-/Lesekopfs und eine für das Warten auf die richtige Position der Scheibe.',
           2, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Festplatten'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Welche Faktoren beeinflussen die Zugriffszeit einer Festplatte?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Beschreibe Suchzeit und Zugriffsverzögerung durch Umdrehung.',
           'Suchzeit: Die Zeit, die der Schwungarm benötigt, um eine Spur zu erreichen. Zugriffsverzögerung durch Umdrehung: Die Wartezeit, bis der Schreib-/Lesekopf den gewünschten Block erreicht; sie hängt von der Drehgeschwindigkeit der Scheiben ab.',
           'Unterscheide die Bewegung des Arms von der Rotation der Scheibe.',
           3, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Festplatten'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Beschreibe Suchzeit und Zugriffsverzögerung durch Umdrehung.');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Wie berechnet man die Kapazität einer Scheibe?',
           'Zylinder × Sektoren pro Spur (spt) × 512 Bytes',
           'Multipliziere die Zylinderzahl mit den Sektoren pro Spur und 512 Bytes.',
           2, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Festplatten'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wie berechnet man die Kapazität einer Scheibe?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Wie berechnet man die Größe einer Spur?',
           'Sektoren pro Spur (spt) × 512 Bytes',
           'Eine Spur enthält eine bestimmte Anzahl von Sektoren.',
           2, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Festplatten'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wie berechnet man die Größe einer Spur?');

    INSERT INTO questions (topic_id, question_text, answer, hint, difficulty, question_type)
    SELECT t.id, 'Wie berechnet man die Gesamtkapazität einer Festplatte?',
           'Zylinder × Köpfe × Sektoren pro Spur (spt) × 512 Bytes',
           'Berücksichtige zusätzlich zur Zylinderzahl die Anzahl der Köpfe.',
           2, 'text'
    FROM topics t JOIN subjects s ON s.id=t.subject_id
    WHERE s.name='BS' AND t.name='Festplatten'
      AND NOT EXISTS (SELECT 1 FROM questions q WHERE q.topic_id=t.id AND q.question_text='Wie berechnet man die Gesamtkapazität einer Festplatte?');

    UPDATE questions
    SET question_text='Benutze die Variablen "ZAHL" und "Resultat". Ausgabe: Bitte eine Zahl eingeben: 10; Die Quadratzahl von 10 lautet 100.',
        answer='{"expected_output":["Bitte eine Zahl eingeben: 10","Die Quadratzahl von 10 lautet 100","Drücken Sie eine beliebige Taste . . ."],"inputs":["10"],"solution":"@echo off\\nset /p ZAHL= Bitte eine Zahl eingeben:\\nset /a Resultat=%ZAHL%*%ZAHL%\\necho Die Quadratzahl von %ZAHL% lautet %Resultat%\\npause"}'
    WHERE question_text='Lies eine Zahl ein und gib ihr Quadrat aus. Beispiel-Eingabe: 10.'
      AND question_type='batch';

    UPDATE questions
    SET question_text='Benutze die Variable "OK". Ausgabe bei Eingabe j: Eingabe richtig? [j/n]: j; Alles ist richtig weiter so.',
        answer='{"expected_output":["Eingabe richtig? [j/n]: j","","Alles ist richtig weiter so","Drücken Sie eine beliebige Taste . . ."],"inputs":["j"],"solution":"@echo off\\nset /p OK= Eingabe richtig? [j/n]:\\necho.\\nIF /I \\"%OK%\\" == \\"j\\" (echo Alles ist richtig weiter so)\\necho.\\npause"}'
    WHERE question_text='Frage nach OK. Bei der Eingabe „j“ soll „Alles ist richtig weiter so“ erscheinen.'
      AND question_type='batch';

    UPDATE questions
    SET answer='{"nodes":[{"id":1,"type":"Start/End","text":"Start des Bootvorgangs"},{"id":2,"type":"Process","text":"PC einschalten"},{"id":3,"type":"Process","text":"BIOS laden"},{"id":4,"type":"Process","text":"Selbsttest (POST)"},{"id":5,"type":"Decision","text":"Hardware OK?"},{"id":6,"type":"Process","text":"CMOS lesen"},{"id":7,"type":"Process","text":"Grundkonfiguration der Komponenten"},{"id":8,"type":"Decision","text":"Betriebssystem vorhanden?"},{"id":9,"type":"Process","text":"Betriebssystem starten"},{"id":10,"type":"Start/End","text":"Betriebssystem geladen"},{"id":11,"type":"Process","text":"Fehlermeldung"},{"id":12,"type":"Process","text":"Fehlerbeseitigung"},{"id":13,"type":"Process","text":"PC ausschalten"}],"edges":[{"from":1,"to":2,"label":"Normal"},{"from":2,"to":3,"label":"Normal"},{"from":3,"to":4,"label":"Normal"},{"from":4,"to":5,"label":"Normal"},{"from":5,"to":6,"label":"Ja"},{"from":5,"to":11,"label":"Nein"},{"from":6,"to":7,"label":"Normal"},{"from":7,"to":8,"label":"Normal"},{"from":8,"to":9,"label":"Ja"},{"from":8,"to":11,"label":"Nein"},{"from":9,"to":10,"label":"Normal"},{"from":11,"to":12,"label":"Normal"},{"from":12,"to":13,"label":"Normal"}]}'
    WHERE question_type='pap'
      AND question_text='Erstelle einen PAP für den Bootvorgang. Verwende Start/Ende-, Verarbeitungs- und Entscheidungsblöcke und verbinde sie mit den passenden Ja-/Nein-Zweigen.'
      AND topic_id IN (SELECT t.id FROM topics t JOIN subjects s ON s.id=t.subject_id WHERE s.name='BS' AND t.name='Bootvorgang');
    """,

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
