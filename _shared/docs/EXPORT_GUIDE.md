# Spätere Exporte und Konsolidierung
Für jede Vorlesung alle ein bis zwei Jahre einen bereinigten Export mit derselben Struktur erstellen. Keine alten PDF-Caches, Git-Objekte, absoluten Benutzerpfade oder fremden Quellen aufnehmen.

Beilegen: AGENTS-Regeln, README, STARTPROMPT, komplette common-Dateien, _shared Commands/Tools/Style, Build-Einstiege, Editor-Aufgaben, notwendige Branding-/Font-Dateien mit Lizenzen, kleine baubare Muster statt vollständiger Vorlesung, freigegebene Varianten, Abhängigkeiten, Prüfbericht und Maschinenmanifest.

INVENTORY.json Schema 1: Paketname/Version/Datum, Herkunftsrepository/Commit, lokaler Exportstand (kann vom Commit abweichen), Cache-Namen und je Datei Pfad, Größe, SHA-256 sowie ggf. ursprüngliche SHA-256. Neue Exportpakete mit eigener Vorlesungskennung versehen.

Änderungen an Stil, Commands oder Bauablauf künftig kurz in _shared/docs/STYLE_CHANGES.md festhalten, inklusive Motivation und betroffenem Produkt. Bei Konsolidierung Unterschiede anhand der Manifeste ermitteln, Gemeinsamkeiten übernehmen und vorlesungsspezifische Entscheidungen erhalten; Konflikte nicht nach Änderungsdatum blind überschreiben. Abschließend Muster aller Produkte/Varianten bauen und visuell vergleichen. Cache-IDs bleiben pro unabhängiger Vorlesung unterschiedlich. Keine Pflicht zu einem zentralen Stil-Repository.
