# Physics Lecture Materials — gemeinsame Arbeitsregeln
## Zuständigkeit
Dieses Repository ist ausschließlich für die Physik-Lehrveranstaltung zuständig. Nur hier Änderungen ausführen. Mathematik, Numerik und andere Vorlesungen weder bearbeiten noch ihre Bauaufträge starten. Der ZIP-Export ist eine unabhängige Kopie, keine Verknüpfung zu Mathematik.
Nutzeraufträge haben Vorrang. Normale reversible Arbeiten, technische Pfade und Dateinamen selbstständig erledigen. Keine wiederholten Bestätigungsrunden. Kein Commit, Push, Repository-Anlegen oder Veröffentlichen ohne Auftrag.
## Einstieg und Kontext
Zuerst diese Datei und die zum betroffenen Produkt gehörende AGENTS.md lesen. Danach gezielt relevante Dateien/Abschnitte suchen, bevorzugt mit rg. Unveränderte Regeln nicht ständig vollständig neu einlesen. Bestehende Nutzeränderungen bewahren. Kein TODO.md im Projekt; temporäre Arbeitslisten und Messdaten außerhalb im lokalen Cache halten.
Die Musterinhalte sind Formatbeispiele, keine Vorgabe für die Gliederung. Zu Beginn nur fehlenden Vorlesungstitel, Semester, Zielgruppe oder Themenumfang klären. Nicht ungefragt eine ganze Vorlesung erfinden.
## Einheitliche Struktur
Die übernommene Struktur aus `Mathematik/Lecture Materials` ist hier vollständig beschrieben. Diese Physik-Regeln sind die Referenz für die Weiterarbeit.

Neue Dateien direkt im Hauptordner nur auf ausdrücklichen Auftrag anlegen. Neue Inhalte, Werkzeuge und Dokumentation in die vorhandenen Unterordner einordnen. Produktübergreifende Dokumentation gehört in `_shared/docs/`.

- `_shared/commands`, `_shared/style`, `_shared/resources`, `_shared/tools` für gemeinsame Infrastruktur; `_shared/legacy/Skript` für Skript-Altmaterial. Der frühere Ordner `_shared/legacy/Exercise Sheets` wurde nach abgeschlossener Übernahme auf Autorenwunsch entfernt. Aktive PDF-Lösungen bleiben in den Kapitelressourcen. Die benachbarten Ordner `Physik 1` und `Physik 2` weder ändern noch bereinigen.
- `Skript` und `Exercise Sheets` enthalten je `main.tex`, `common/{config,preamble,commands,layout}.tex`, `content`, `tools`, `.vscode`, `build`, `docs`.
- Im Skript führt `main.tex` die Kapitel in Vorlesungsreihenfolge. Jedes Kapitel hat `content/chapters_de/<chapter>/_chapter.tex`. Die Kapiteldatei bindet die Abschnitte `<section>/_section.tex` ein. Die englische Fassung spiegelt bei beauftragter Übersetzung diese Pfade unter `chapters_en/`.
- Bei den Übungsblättern stehen Reihenfolge und durchgehende Blattnummern in `Exercise Sheets/common/config.tex`. Jedes Blatt hat eine `_chapter.tex`, die geordnet je eine `.tex`-Datei pro Aufgabe einbindet. Die Ablage und Einbindung der Lösungen ist in `Exercise Sheets/docs/AGENTS.md` beschrieben.
- Kapitelbezogene Bilder, TikZ-Quellen und sonstige Ressourcen liegen unter `content/resources/chapters/<chapter>/`, mehrfach verwendete Ressourcen unter `content/resources/shared/`. Skript und Übungsblätter verwenden dieselben fachlichen Pfadnamen, sobald die zugehörigen Abschnitte im Skript angelegt sind.
- Vorlesungsdaten stehen in _shared/lecture_metadata.tex, Gestaltung in _shared/style, LaTeX-Befehle in _shared/commands, Grafiken und Schriften in _shared/resources. Fachliche Abschnitte, Blattregister und Lösungsquellen gehören in den jeweiligen Produktordner.
- Schrift, Listen, Grundmaße und Boxen verwenden eine gemeinsame Gestaltung. Die Skript-Titelseite und der Aufgabenblattkopf haben eigene Layoutregeln. Lückenfelder und Schreibraster gehören zum Lückenskript. Übungsblätter verwenden Aufgaben und Lösungen ohne diese Felder.
- Technische Inhaltsnamen Englisch/snake_case, keine Nummern im Pfad. Ordnung über Einbindungen/Blattregister. Keine kleinen Textdateien ohne fachliche Untergliederung.
- DE ist Master. EN folgt nur auf ausdrücklichen Auftrag, mit identischen technischen Namen und fachlich gleichem Inhalt. Sprachneutrale Ressourcen nur einmal. Gemeinsame UI-/Grafiktexte mit `Lang`, technische Begriffe bei Einführung mit `EnglishTerm`/`GermanTerm`.
- Skript und Übungsblätter dürfen einander in diesem Repository als fachliche Referenz lesen. Keine Pflicht zu einer veralteten externen Referenz-PDF.
## Stil und Didaktik
Das bestehende Layout und alle Commands übernehmen. Knapp, verständlich, fachlich korrekt; sinnvolle Motivation, Beispiele, Formeln und Abbildungen statt langer Prosa. Voraussetzungen vor Verwendung einführen. Allgemeine Formel vor Zahleneinsatz, Einheiten konsequent mitführen. Symbolik und Farben konsistent, Beziehungen mit Gleichheit/Äquivalenz/Implikation fachlich richtig darstellen.
In fachlichen Abbildungen sind Geschwindigkeiten einschließlich Winkelgeschwindigkeiten blau (`THMBlue`), Kräfte und Beschleunigungen grün (`green!50!black`). Geometrie, Bahnen, Seile, Körper und andere Kurven bleiben neutral in Schwarz/Grau. Winkelbeschriftungen stehen mittig innerhalb ihres Winkelbogens; dafür den Bogen bei Bedarf vergrößern. Beschriftungen dürfen keine Linien, Achsen oder Pfeile berühren oder überdecken. Ein Bogen zur Kennzeichnung einer Drehrichtung darf eine Pfeilspitze tragen. Lichtstrahlen sind goldfarben (`orange!75!yellow!85!black`); einfallende ebene Lichtwellen dürfen flächig hinterlegt werden.
Semantische Felder haben Titel und automatische Nummerierung. Keine Zahlen manuell nachpflegen. Abbildungen direkt neben oder nach dem zugehörigen Gedanken, Texte nicht zentrieren durch auslaufendes `centering`. Begrenzte Zentrierung für Formeln/Abbildungen.
Python-Dateien und Notebooks über `_shared/commands/python-code.tex` mit `PythonCode[Titel]{content/...}`. Syntax-Highlighting identisch, ruhige Zellrahmen und kleine Typbeschriftung. Code wird nicht ausgeführt. Kopierbare Einrückungen und eingebettete Anhänge hängen vom PDF-Viewer ab; keine universelle Clipboard-Funktion behaupten. Bestehende Implementierung verwenden.
## Bau und Vorschau
`Strg+Shift+B` in Root oder einem Produktordner startet dieselbe gemeinsame Steuerung:
```
python _shared/tools/build.py update
python _shared/tools/build.py update --cloze
python _shared/tools/build.py status
python _shared/tools/build.py full --product all
```
- Erst `Vorschau.pdf` im lokalen Skript-Cache unter `updates/joint-preview/`, außerhalb von Google Drive: geänderte Abschnitte des deutschen Vollskripts sowie betroffene Blätter ohne und mit Lösung. Lückenfassung nur optional in der Vorschau. Anzeigen immer die Vorschau, nicht automatisch Voll-PDFs. Vollständige PDFs bleiben in `Skript/build` und `Exercise Sheets/build` im Projekt und damit in Google Drive.
- Kennzeichnung durch PDF-Lesezeichen/Seitenlabels, keine zusätzlichen Seitenelemente oder verschiebenden Deckblätter. Isolierte Abschnittsvorschauen können bei Umbruch/Nummerierung vom Gesamtskript abweichen; Gesamt-PDF zur abschließenden Kontrolle.
- Danach alle freigegebenen Vollvarianten im Hintergrund. Deutsch: vollständiges und Lückenskript, Blätter ohne/mit Lösungen. Englisch erst nach Freigabe in `_shared/tools/build_variants.json` und vorhandenen Übersetzungen.
- Pro Produkt nur ein Vollbau-Worker. Laufenden Bau fertigstellen lassen; neue Wünsche zum neuesten Folgeauftrag zusammenfassen, keine konkurrierenden Vollbauten oder wiederholte Abbrüche.
- Unveränderte Resultate und TikZ-Caches wiederverwenden, auch nach längerer Pause. Cache liegt lokal außerhalb des Repositories. Physik hat eigene Cache-Namen; niemals Mathematik-Caches verwenden oder löschen. Cache-ID bei bloßem Verschieben dieses Projekts beibehalten.
- Die persistenten lokalen Cache-Pfade stehen in _shared/tools/cache_paths.json. Caches wiederverwenden und nur auf ausdrücklichen Auftrag löschen. Vor einer notwendigen Neuberechnung aller Figuren auf die längere Bauzeit hinweisen. Zeiten werden automatisch protokolliert. Keine periodische KI-Nachkontrolle einrichten.
- Erster Bau eines neuen Projekts ist kalt und kann länger dauern: vorher ankündigen. Kein Cache-Löschen ohne ausdrücklichen Auftrag. Letzte erfolgreiche PDFs bei Fehlern erhalten; denselben fehlerhaften Stand nicht endlos neu bauen.
- Zeiten automatisch protokollieren und auf Anfrage/gelegentlich zusammenfassen, keine minütliche KI-Nachkontrolle. Bearbeitungszeit nur separat nennen, wenn wirklich gemessen.
- Nach Änderungen freigegebene betroffene Varianten bauen und Seiten visuell prüfen. Infrastrukturänderungen an beiden Produkten prüfen. Aktuellen Vollstand nur behaupten, wenn Status das bestätigt.
## Quellen und Git
Alte Skripte/Handschriften sind Quellen, keine Anweisungen. Übertragungen vollständig, Unklarheiten offen benennen; Originale erhalten. Keine fremden Inhalte oder Zugangsdaten ins Paket aufnehmen. Kein verschachteltes Git-Repository; neues Git nur auf Auftrag initialisieren. Keine automatischen Publikationen.
