# Physics Lecture Materials

Das Physikprojekt verwendet lokale Kopien der aus Mathematik übernommenen gemeinsamen Infrastruktur.
Der aktuelle Blattbestand umfasst die aus Physik 2 übernommenen Übungsblätter. [Übernahmeprotokoll](Exercise%20Sheets/docs/physics_2_migration.md)

Dieser Ordner bündelt Skript, Exercise Sheets und den gemeinsamen Bereich _shared.

- Skript: Vorlesungsskript mit deutscher Voll- und Lückenversion.
- Exercise Sheets: Aufgabenblätter und Musterlösungen.
- [Vorlesungsdaten](_shared/lecture_metadata.tex): Titel, Hochschule und Fakultät (DE/EN) sowie Semester und Autor für beide Dokumente.
- [Hochschulfarbe](_shared/style/branding_colors.tex): gemeinsames THM-Blau für beide Dokumente und TikZ.
- _shared/commands: gemeinsame Befehle, darunter die Python-Codebeispiele für beide Dokumente.
- `_shared/resources/`: Hochschulgrafiken, TikZ-Symbole und Plus Jakarta Sans mit Lizenz.
- _shared/tools: gemeinsame Bausteuerung und Tests.
- _shared/legacy: gemeinsame Ablage für unverändert erhaltene Altmaterialien.

## Voraussetzungen

Windows mit PowerShell, TeX Live mit LuaLaTeX und latexmk sowie Python. Die gemeinsame
Textschrift Plus Jakarta Sans ist gebündelt, Libertinus Math kommt aus TeX Live.
Python-Abhängigkeiten bei Bedarf aus dem Hauptordner installieren:

```powershell
python -m pip install -r _shared/tools/requirements.txt
```

Poppler dient der visuellen Prüfung. Die Arbeitsregeln stehen in [AGENTS.md](AGENTS.md).

## VS Code

Strg+Shift+B startet in diesem Hauptordner sowie in `Skript` und `Exercise Sheets` denselben
gemeinsamen Bau. Die feste Datei `build/Vorschau.pdf` im Hauptordner enthält geänderte
Abschnitte des deutschen Vollskripts und betroffene Übungsblätter, jeweils ohne und mit
Lösungen direkt hintereinander. Beim nächsten Auftrag werden die Änderungen seit der letzten
erfolgreichen gemeinsamen Vorschau betrachtet. Ohne Inhaltsänderung bleibt die Vorschau erhalten.

Die zusätzliche VS-Code-Aufgabe „Lecture Materials: Vorschau zusätzlich mit Lückenfassung“
ergänzt die deutsche Lückenfassung direkt nach dem jeweiligen Vollskriptabschnitt.
PDF-Lesezeichen und die Seitenbezeichnungen im Viewer kennzeichnen Herkunft und Variante.
Es werden keine Deckblätter, Kopfzeilen oder sonstigen Inhalte in die Seiten eingefügt.
Die Zusammenführung bewahrt Inhalt, Seitenmaße und Seitenumbrüche der Ausgangs-PDFs.
Die isolierte Skript-Abschnittsvorschau kann dennoch vom Gesamt-PDF abweichende Umbrüche,
Nummerierungen und Verweise haben. Für die abschließende Layoutkontrolle gilt das Gesamt-PDF.

Nach Veröffentlichung der Vorschau starten die Vollbauten im Hintergrund. Unveränderte
Ergebnisse und bestehende TikZ- und LaTeX-Caches werden weiterverwendet. Skript und Blätter
haben jeweils einen gegen parallele Vollbauten gesperrten Worker. Während er arbeitet,
ersetzt ein neuer Auftrag den zuvor wartenden Auftrag. Ein laufender Vollbau wird beendet.
Vorschau und Vollbau teilen bei Übungsblättern den geschützten Blatt-Cache. Ein gerade
laufender Blattbau kann deshalb die Blattvorschau kurz verzögern.

## Gemeinsame Infrastruktur

Beide Produkte laden die gemeinsamen LaTeX-Befehle aus `_shared/commands` und
die gemeinsame Gestaltung aus `_shared/style`. Ihre `common`-Ordner enthalten
produktspezifische Einstellungen, etwa den Blattkopf, die Skripttitelseite und die Lösungsmodi.

Die gemeinsame Konfiguration `_shared/tools/cache_paths.json` verweist auf die
bestehenden, getrennten lokalen Caches für Skript und Übungsblätter.
Beide Produkte verwenden die gemeinsame Steuerung in `_shared/tools/build_runtime.py`: unveränderliche
Quellstände, unabhängige Warteschlangen, Prozesssperren, sichere PDF-Veröffentlichung und fortlaufende
Zeitprotokolle. Ein laufender Bau wird beendet; anschließend folgt nur der neueste vorgemerkte Stand.
Bei Fehlern bleiben die letzten erfolgreichen PDFs erhalten. Ein identischer fehlerhafter Stand
wird ohne ausdrücklichen neuen Auftrag nicht wiederholt gebaut.

`python _shared/tools/build.py status --product all` zeigt beide Bauzustände. Mit
`python _shared/tools/build.py full --product all` wird bis zum Abschluss beider Produkte gewartet.
Aktive Änderungen unter `_shared` werden bei beiden Dokumenttypen berücksichtigt. `_shared/legacy`
ist ausgenommen: Dort abgelegte Altmaterialien lösen keine Bauten aus. Die gemeinsame
Abhängigkeitsprüfung für TikZ liegt in `_shared/tools/build-cache.ps1`. Der Skriptbau
berücksichtigt auch `_shared/resources/tikz` und verwendet gültige Figurencaches weiter.
Die lokale Speicherüberwachung der Blätter bleibt als zusätzliche Aufgabe verfügbar.

Zeitprotokolle liegen außerhalb des Projekts: für das Skript unter
`%USERPROFILE%/AppData/Local/Temp/Physics-Skript-def15e3b6ea5/updates/timings.csv`, für die Blätter unter
`%USERPROFILE%/AppData/Local/_tmp_LatexCache/physics_exercise_sheets_def15e3b6ea5/updates/timings.csv`.
Deutsch bleibt die Masterfassung, Englisch folgt auf ausdrücklichen Auftrag.

`_shared/tools/build_variants.json` hält die freigegebenen Sprachen fest. Für das Skript
aktiviert jeder Eintrag in `script_languages` Voll- und Lückenfassung. Für Übungsblätter
aktiviert `sheet_languages` beide Lösungsmodi pro Blatt-ID; `*` bedeutet alle registrierten
Blätter. Aktuell ist Deutsch freigegeben, Englisch noch nicht. Eine englische Datei allein
gilt nicht als Freigabe. Eine freigegebene, aber fehlende Übersetzung meldet einen Fehler.

Gemeinsame Bedienung im Terminal:

```powershell
python _shared/tools/build.py update
python _shared/tools/build.py update --cloze
python _shared/tools/build.py update --wait
python _shared/tools/build.py status
```

Das zusätzliche Vorschau-Zeitprotokoll liegt unter
`%USERPROFILE%/AppData/Local/Temp/Physics-Skript-def15e3b6ea5/updates/joint-preview/timings.csv`.

Die Cache-Konfiguration verweist auf die bereits verwendeten Physik-Cachepfade. Ein ausdrücklich gesetztes `EXERCISE_SHEETS_CACHE` muss auf einen separaten Physik-Cache zeigen.

Die Vollfassungen des Skripts liegen als `Skript/build/build-de.pdf` und `Skript/build/build-de-cloze.pdf` vor. Die Einzel- und Sammelblätter liegen unter `Exercise Sheets/build/`.

## Starter-Export

Die Unterlagen zum Starter-Export liegen unter `_shared/docs/`. Die Pfade und Prüfsummen im Inventar beziehen sich auf das ursprüngliche Archiv.

- [Inventar](_shared/docs/INVENTORY.json)
- [Leitfaden für spätere Exporte](_shared/docs/EXPORT_GUIDE.md)
- [Prüfbericht](_shared/docs/VALIDATION.md)
- [Ursprünglicher Startprompt](_shared/docs/STARTPROMPT.md)
