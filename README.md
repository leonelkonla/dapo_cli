# DaPo CLI

Schema-getriebenes CLI-Tool zur Generierung synthetischer Multi-Source-Testdaten nach dem DaPo⁺-Prinzip

Version 1.2
Projektkontext: Bachelorarbeit – Medieninformatik

## Überblick

DaPo CLI ist ein kompaktes, modular aufgebautes Command-Line-Tool zur Erzeugung synthetischer Testdaten über mehrere heterogene Datenquellen hinweg.

Das System simuliert typische Datenqualitätsprobleme wie fehlende Werte, Tippfehler, veraltete Informationen und Duplikate. Die erzeugten Datensätze können entweder als CSV-Bundle exportiert oder direkt in eine PostgreSQL-Datenbank geschrieben und anschließend in Power BI analysiert werden.

Das Projekt orientiert sich konzeptionell am Paper “Towards Scalable Generation of Realistic Test Data for Duplicate Detection” (Panse, Wingerath, Wollmer), setzt den Ansatz jedoch bewusst vereinfacht und prototypisch um.

Der Fokus liegt auf:
- Reproduzierbarkeit
- Modularität
- kontrollierter Fehler-Simulation
- Gold-Standard-Erzeugung
- analytischer Weiterverwendung der Daten

## Ziel des Projekts

In vielen datengetriebenen Systemen entstehen Duplikate und Inkonsistenzen durch heterogene Quellen, Formatunterschiede oder manuelle Eingriffe. Für die Entwicklung und Evaluierung von Datenqualitäts- oder Duplikaterkennungsverfahren werden realistische Testdaten benötigt.

### DaPo CLI ermöglicht:

- Simulation mehrerer Quellen (S1…SN)
- Erzeugung kontrollierter Datenverschmutzung
- Nachvollziehbare Ground-Truth-Abbildung
- Berechnung einfacher Qualitätsmetriken
- Persistierung für Analyse- und BI-Zwecke

## Funktionsumfang

### Interaktiver CLI

- Abfrage von Domain/Kontext
- Definition einer Entität
- Feldliste (Schema wird automatisch abgeleitet)
- Standardfeld entity_id wird sichergestellt

### Clean Base Generation

- Deterministische Generierung via Seed
- Typbasierte Daten mit Faker
- Reproduzierbare Runs

### Multi-Source-Simulation

- Frei definierbare Anzahl an Quellen
- Unterschiedliche Schema-Repräsentationen:
    - snake_case
    - camelCase
    - UPPERCASE

### Datenverschmutzung (Pollution)

#### Konfigurierbar über Raten:

- Missing Values
- Tippfehler
- Veraltete Werte
- Duplikate
- Copying-Effekte zwischen Quellen

### Gold Standard

- Erzeugung eines Mappings:`(source, record_id) → entity_id`
Dient als Ground Truth für spätere Evaluierungen.

### Minimaler Integrationsschritt (ETL)

- Zusammenführung aller Quellen
- String-Normalisierung
- Null-Werte-Behandlung

### Qualitätsmetriken

Pro Quelle:

- Anzahl Zeilen
- Anzahl Spalten
- Missing Rate
- Duplicate Rate

### Persistierung

- CSV-Bundle (pro Run eigener Output-Ordner)
- PostgreSQL-Tabellen (Überschreiben pro Run)

## Projektstruktur

DAPO_CLI/

github/workflows/     # CI Pipeline
docs/                 # Forschungsquellen, Diagrammen, usw.
Outputs               # Outputs (Kommt nach dem ersten run...)
src/
    config.py             # Laufparameter
    schemas.py            # Schema-Modelle
    generator.py          # Clean Base Generation
    pollution.py          # History + Fehler + Duplikate
    etl.py                # Integration
    quality.py            # Qualitätsmetriken
    storage.py            # CSV / Postgres Persistierung
    main.py               # CLI-Orchestrierung
tests/                # Pytest Tests
requirements.txt
README.md

Jedes Modul besitzt eine klar definierte Verantwortung.
Die Pipeline ist bewusst flach und nachvollziehbar gehalten.

## Installation

1. Virtuelle Umgebung erstellen

python -m venv .venv
Windows (PowerShell):
.\.venv\Scripts\Activate.ps1
2. Abhängigkeiten installieren
pip install -r requirements.txt

## Ausführung des Programs
- CSV
- python -m src.main --rows 2000 --sources 3 --store csv

### Beispielinteraktion:

Domain/Kontext: Banking
Entität: transactions
Felder: entity_id,email,city,amount,status,order_date

### Output:

outputs/<timestamp>/
    S1.csv
    S2.csv
    S3.csv
    integrated.csv
    gold_standard.csv
    quality_metrics.csv

## PostgreSQL

Voraussetzung: lokal laufende PostgreSQL-Instanz.

python -m src.main \
  --rows 2000 \
  --sources 3 \
  --store postgres \
  --pg-dsn "postgresql+psycopg2://USER:PASSWORD@localhost:PORT/YOUR_DATABASE"

`Speichereung im CSV und PostgreSQL auch möglich: python -m src.main --rows 2000 --sources 3 --store both --pg-dsn "postgresql+psycopg2://USER:PASSWORD@localhost:5432/dapo_db"`

### Erzeugte Tabellen:

- source_s1 … source_sn
- integrated
- gold_standard
- quality_metrics

## Power BI Integration

- Power BI Desktop öffnen
- Daten abrufen → PostgreSQL
- Server: localhost (Standard)
- Port: 5432 (Standard)
- Datenbank: YOUR_DATABASE

### Empfohlene Starttabellen:

- quality_metrics (Übersicht)
- integrated (Analyse)
- gold_standard (Evaluierung)

## Testing & CI
- Lokal testen
- pytest

### Empfohlene Tests:

- Unit Tests für Generator und Qualitätsmetriken
- Optionaler End-to-End-Test für CLI-Run

### GitHub Actions

Bei jedem Push oder Pull Request werden Tests automatisch ausgeführt.

## Designprinzipien

- Reproduzierbarkeit durch Seed
- Klare Modulverantwortung
- Keine unnötige Architekturkomplexität
- Konfigurierbare Fehler-Simulation
- Analytische Weiterverwendbarkeit

`Das Projekt ist als prototypische Umsetzung konzipiert, nicht als skalierbares Produktionssystem.`

## Erweiterungsmöglichkeiten

- Neue Feldtypen (z. B. IBAN, Country, usw.)
- Realistischere Fehler-Events (Transpositions, Abbreviations)
- Run-Versionierung in PostgreSQL
- Anschluss von Dedup-Algorithmen (Blocking + Similarity)
- KI-Verknüpfung

## Wissenschaftlicher Kontext

Die Umsetzung orientiert sich am konzeptionellen Rahmen von:

Panse, F.; Wingerath, W.; Wollmer, B.
Towards Scalable Generation of Realistic Test Data for Duplicate Detection.

### LICENSE

Copyright (c) 2026 Leonel Konla - All rights reserved. This repository is publicly visible for viewing purposes only.