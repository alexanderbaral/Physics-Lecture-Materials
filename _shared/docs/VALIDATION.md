# Prüfbericht — 2026-11-07

- 39 automatisierte Tests erfolgreich: 16 gemeinsame Steuerung, 15 Skript, 8 Übungsblätter.
- Gemeinsamer Aufruf `python -B _shared/tools/build.py update --cloze --wait` erfolgreich.
- Deutsches Vollskript und Lückenskript jeweils 6 Seiten; Musterblatt ohne und mit Lösungen jeweils 1 Seite; Sammelblätter ebenfalls erfolgreich.
- Python-Datei in beiden Produkten, Notebook mit zwei Codezellen und Markdown-Zelle im Skript gebaut.
- Musterseiten, Notebook, Lückenraster und Blattlösung gerendert und visuell geprüft. Keine beschädigten Umlaute in der PDF-Textextraktion.
- Englische Varianten bewusst nicht freigegeben und nicht gebaut; noch keine EN-Inhalte enthalten.
- Nach Korrekturen: gemeinsame Vorschau einschließlich optionaler Lückenfassung 15,22 s, Skript-Vollbau 11,89 s, Blätter 4,80 s. Erster erfolgreicher kalter Skript-Vollbau 56,56 s. Zeiten sind lokal gemessen, keine Zusicherung für andere Rechner oder größere Inhalte.
- PDF-Leser meldet bei zwei generierten Blatt-PDFs einen doppelten /Group-Eintrag; Seiten lassen sich lesen, zusammenführen und rendern. Kein Buildfehler.

## Technische Anpassungen gegenüber dem Mathematik-Ausgangsstand
- Eigene Physik-Metadaten, Musterinhalte und isolierte Cache-Namen; alte Mathematik-Blatt-/Lösungsregister und Migrationsberichte entfernt.
- Windows-Ausgabepfade im Skript-Preview und in PowerShell normalisiert. Das verhindert Fehler beim Schreiben von Notebook-/Markdown-Hilfsdateien.
- Dokument-LuaLaTeX explizit ohne Shell-Ausführung; Notebook-Zellschreiber mit erklärter Fehlermeldung und relativem Fallback im externen Build-Workspace.
- Exporttexte auf UTF-8 vereinheitlicht; Vorschau-/Sammel-PDF-Metadaten auf Physik angepasst.
- Arbeitsregeln konsolidiert: gemeinsame Bausteuerung, aktuelle Querverweise zwischen Produkten, selbstständige Pfadwahl, keine alten Mathematik-Migrationsaufträge.

Das Mathematik-Original wurde für diese Anpassungen nicht verändert. Keine automatische Clipboard-Funktion oder Garantie für kopierte Python-Einrückungen ergänzt. UI-Kopieren wurde in diesem Prüflauf nicht getestet.
