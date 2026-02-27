# Requirement-Engineering
## DaPo CLI  
Version 1.3 

---

## 1. Einleitung

Anforderungen an das System **DaPo CLI** sowie technische Rahmenbedingungen.  
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

| ID   | Anforderung                    | Beschreibung                                                                 |
|------|--------------------------------|------------------------------------------------------------------------------|
| FR1  | Interaktive Konfiguration      | CLI fragt Domain, Entität und Feldliste ab.                                | 
| FR2  | Schema-Ableitung               | Datentypen werden automatisch aus Feldnamen abgeleitet.                    | 
| FR3  | Clean Base Generation          | Erzeugung einer sauberen Basistabelle mit konfigurierbarer Zeilenanzahl.   | 
| FR4  | Multi-Source-Erzeugung         | Generierung mehrerer Datenquellen (S1…SN).                                  | 
| FR5  | Schema-Heterogenität           | Unterschiedliche Spaltenformate je Quelle (snake_case, camelCase, UPPERCASE). | 
| FR6  | Datenverschmutzung             | Simulation von Missing Values, Tippfehlern, veralteten Werten und Duplikaten. | 
| FR7  | Historienbildung               | Erzeugung von mindestens zwei Zeitständen (t0, t1).                         | 
| FR8  | Gold-Standard-Erzeugung        | Mapping von `(source, record_id)` auf `entity_id`.                          | 
| FR9  | Integration                    | Zusammenführung aller Quellen in einer integrierten Tabelle. Minimaler ETL-Prozess   | 
| FR10 | Qualitätsmetriken              | Berechnung von Zeilenanzahl, Spaltenanzahl, Missing Rate, Duplicate Rate pro Quelle. | 
| FR11 | CSV-Export                     | Speicherung aller Ergebnisse als CSV-Bundle.                                 | 
| FR12 | PostgreSQL-Speicherung         | Persistierung der Daten in PostgreSQL.                                      | 

---

### Nicht-funktionale Anforderungen

| ID    | Anforderung          | Beschreibung                                             | 
|-------|---------------------|-----------------------------------------------------------|
| NFR1  | Reproduzierbarkeit  | Jeder Lauf ist über einen Seed deterministisch steuerbar. | 
| NFR2  | Modularität         | Klare Trennung der Verantwortlichkeiten pro Modul.        | 
| NFR3  | Testbarkeit         | Kernfunktionen sind automatisiert testbar.                | 
| NFR4  | Wartbarkeit         | Code ist nachvollziehbar und strukturiert.                | 
| NFR5  | Bedienbarkeit       | CLI ist einfach nutzbar.                                  | 
| NFR6  | Performance         | Verarbeitung mittelgroßer Datensätze ohne Abbruch.        | 
| NFR7  | Erweiterbarkeit     | Neue Feldtypen oder Fehlerarten können ergänzt werden.    | 
| NFR8  | Integrationsfähigkeit | Exportierte Daten sind direkt analysierbar.             | 
