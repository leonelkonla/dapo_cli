# Software Requirements Specification  
## DaPo CLI  
Version 1.3 

---

## 1. Einleitung

Dieses Dokument beschreibt die Anforderungen an das System **DaPo CLI**.  
Es definiert funktionale und nicht-funktionale Anforderungen sowie technische Rahmenbedingungen.  
Die Spezifikation dient als Grundlage für Implementierung, Tests und Weiterentwicklung.

---

## 2. Systemüberblick

DaPo CLI ist ein schema-getriebenes Command-Line-Tool zur Generierung synthetischer Multi-Source-Testdaten.

Das System simuliert typische Herausforderungen realer Datenlandschaften:

- Mehrere heterogene Quellen  
- Unterschiedliche Schema-Repräsentationen  
- Fehlende Werte  
- Tippfehler  
- Veraltete Informationen  
- Duplikate  

Die erzeugten Daten können als CSV-Dateien exportiert oder in eine PostgreSQL-Datenbank geschrieben werden.

---

## 3. Systemkontext

DaPo CLI ist ein eigenständiges CLI-Tool ohne externe Webservices.

Optionale externe Systeme:

- PostgreSQL (Persistierung)
- Power BI (Analyse)
- GitHub Actions (Continuous Integration)

---

## 4. Anforderungen

### Funktionale Anforderungen

| ID   | Anforderung                    | Beschreibung                                                                 | Akzeptanzkriterium |
|------|--------------------------------|------------------------------------------------------------------------------|--------------------|
| FR1  | Interaktive Konfiguration      | CLI fragt Domain, Entität und Feldliste ab.                                | Eingaben werden korrekt übernommen und im Schema gespeichert. |
| FR2  | Schema-Ableitung               | Datentypen werden automatisch aus Feldnamen abgeleitet.                    | `entity_id` ist vorhanden und eindeutig referenzierbar. |
| FR3  | Clean Base Generation          | Erzeugung einer sauberen Basistabelle mit konfigurierbarer Zeilenanzahl.   | Gleicher Seed erzeugt identische Daten. |
| FR4  | Multi-Source-Erzeugung         | Generierung mehrerer Datenquellen (S1…SN).                                  | Jede Quelle enthält eine eigene `record_id`. |
| FR5  | Schema-Heterogenität           | Unterschiedliche Spaltenformate je Quelle (snake_case, camelCase, UPPERCASE). | `entity_id` bleibt logisch identifizierbar. |
| FR6  | Datenverschmutzung             | Simulation von Missing Values, Tippfehlern, veralteten Werten und Duplikaten. | Fehler treten gemäß konfigurierter Raten auf. |
| FR7  | Historienbildung               | Erzeugung von mindestens zwei Zeitständen (t0, t1).                         | Änderungen zwischen t0 und t1 sind nachvollziehbar. |
| FR8  | Gold-Standard-Erzeugung        | Mapping von `(source, record_id)` auf `entity_id`.                          | Jede Quellzeile ist eindeutig zuordenbar. |
| FR9  | Integration                    | Zusammenführung aller Quellen in einer integrierten Tabelle.                | Integrierte Tabelle enthält alle Quellzeilen. |
| FR10 | Qualitätsmetriken              | Berechnung von Zeilenanzahl, Spaltenanzahl, Missing Rate, Duplicate Rate pro Quelle. | Metriken sind numerisch korrekt. |
| FR11 | CSV-Export                     | Speicherung aller Ergebnisse als CSV-Bundle.                                 | Alle erwarteten Dateien werden erzeugt. |
| FR12 | PostgreSQL-Speicherung         | Persistierung der Daten in PostgreSQL.                                      | Tabellen werden korrekt erstellt oder ersetzt. |

---

### Nicht-funktionale Anforderungen

| ID    | Anforderung          | Beschreibung                                                | Messkriterium |
|-------|---------------------|------------------------------------------------------------|--------------|
| NFR1  | Reproduzierbarkeit  | Jeder Lauf ist über einen Seed deterministisch steuerbar. | Identischer Seed → identischer Output. |
| NFR2  | Modularität         | Klare Trennung der Verantwortlichkeiten pro Modul.        | Keine zyklischen Abhängigkeiten; klare Struktur. |
| NFR3  | Testbarkeit         | Kernfunktionen sind automatisiert testbar.                | Pytest-Tests laufen erfolgreich. |
| NFR4  | Wartbarkeit         | Code ist nachvollziehbar und strukturiert.                | Verständliche Modulaufteilung. |
| NFR5  | Bedienbarkeit       | CLI ist einfach nutzbar.                                  | Verständliche Fehlermeldungen und Parameter. |
| NFR6  | Performance         | Verarbeitung mittelgroßer Datensätze ohne Abbruch.        | ≤ 50.000 Zeilen laufen stabil auf Standard-Hardware. |
| NFR7  | Erweiterbarkeit     | Neue Feldtypen oder Fehlerarten können ergänzt werden.    | Erweiterungen ohne Architekturänderung möglich. |
| NFR8  | Integrationsfähigkeit | Exportierte Daten sind direkt analysierbar.             | Kompatibilität mit PostgreSQL und Power BI. |
