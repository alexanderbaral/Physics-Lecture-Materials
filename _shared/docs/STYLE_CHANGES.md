# Änderungen gegenüber Exportquelle

Am 07.11.2026 entstand die eigenständige Physik-Vorlage mit eigenen Metadaten, separaten Caches und neuen Mustern. Das Layout beider Produkte wurde übernommen. Der Prüfbericht enthält auch die technischen Pfadkorrekturen für Notebook-Bauten. [Prüfbericht zum Starter-Export](VALIDATION.md)

Alle späteren vorlesungsübergreifenden Stil-/Command-Entscheidungen hier kurz ergänzen.

Am 07.11.2026 wurden beim Import der Physik-2-Übungsblätter Leerzeichen in Blatttiteln und das Dezimalkomma für die deutsche Fassung sichergestellt. Aufgabennummern stehen im Laufkopf der eingefügten Lösungsseiten. Für einzelne Original-PDFs lässt sich der Standardbeschnitt im Lösungsregister verringern, damit randnahe Handschrift sichtbar bleibt.

Am 07.11.2026 wurden Präambel, Schrift, Layoutbasis, Befehle, Hochschulgrafiken und Bausteuerung nach dem lokalen Mathematik-Arbeitsstand zentralisiert. Das Protokoll führt die SHA-256-Werte, Physik-spezifischen Einstellungen und Bauprüfungen auf. [Übernahme der gemeinsamen Infrastruktur](SHARED_SYNC.md)

Auf Autorenwunsch liegt die gemeinsame `Vorschau.pdf` nun im bestehenden lokalen Skript-Cache unter `updates/joint-preview/`, außerhalb von Google Drive. `_shared/tools/build_preview.py` veröffentlicht dort, `build.py` bietet `--open-preview`, und `build.ps1` aktiviert das Öffnen für den gemeinsamen Editor-Bau. Die vollständigen PDFs bleiben in den bisherigen Produkt-Bauordnern in Google Drive. Vorschau-Tests prüfen die externe Ablage, Wiederverwendung, optionales Öffnen und den Erhalt des letzten erfolgreichen Stands bei Fehlern. Diese vier Werkzeugdateien weichen deshalb vom ursprünglich bytegleich übernommenen Mathematik-Stand ab.
