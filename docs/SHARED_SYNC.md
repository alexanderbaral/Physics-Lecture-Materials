# Übernahme der gemeinsamen Infrastruktur

Die Referenz ist der am 07.11.2026 direkt vom Datenträger gelesene lokale Arbeitsstand von Mathematik/Lecture Materials. Die Dateien wurden als eigenständige Physik-Kopien übernommen. Die Prüfung mit SHA-256 schließt Dateikodierung, Zeilenenden, Kommentare und Leerzeichen ein.

## Physik-Konfiguration und lokale Anpassungen

| Datei | Grund für die Abweichung |
| --- | --- |
| `_shared/lecture_metadata.tex` | Titel Physik / Physics. Semester WS 26/27, Autor, Hochschule und Fakultät entsprechen den vorhandenen Physik-Daten. |
| `_shared/tools/cache_paths.json` | Verwendet die bestehenden Physik-Verzeichnisse `AppData/Local/Temp/Physics-Skript-def15e3b6ea5` und `AppData/Local/_tmp_LatexCache/physics_exercise_sheets_def15e3b6ea5` unter dem Benutzerprofil. |
| `_shared/tools/build_variants.json` | Projektfreigaben bleiben Deutsch für Voll- und Lückenskript und beide Modi aller acht Blätter. Englisch bleibt deaktiviert. |
| `Skript/main.tex` | Der gemeinsame Einstieg lädt weiterhin die Physik-Kapitel und das Physik-Vorspannmaterial. |
| `Exercise Sheets/main.tex` | Der gemeinsame Einstieg verwendet `differential_equations` als Physik-Standardblatt. |
| `Exercise Sheets/common/config.tex` | Physik-Blattliste, Lösungsregister und Beschnittoptionen sind erhalten. Die Blattdeklarationen werden außerhalb von `ExplSyntaxOn` gelesen, damit die Titel Leerzeichen behalten. |
| `Exercise Sheets/common/commands.tex` | Eingebettete Original-PDFs können den Beschnitt überschreiben. Die Aufgabennummer wird für den Laufkopf der zugehörigen Lösungsseiten gesetzt. |
| `Exercise Sheets/common/layout.tex` | Der Blattkopf erhält den Physik-Laufkopf und das Dezimalkomma für Deutsch. Grundlayout, Logo, Seitenpunkt und Fußzeile kommen aus `_shared/style`. |
| `Exercise Sheets/tools/combine_pdfs.py` | PDF-Metadaten der Physik-Sammelblätter bleiben produktspezifisch. |
| `README.md` | Der optionale Cache-Override verwendet den Namen `EXERCISE_SHEETS_CACHE` aus der gemeinsamen Steuerung. Die früher in Physik dokumentierte Variable `PHYSICS_EXERCISE_SHEETS_CACHE` entfällt. |

Die 123 geprüften Kapitel-, Aufgaben-, Lösungs- und fachlichen Ressourcendateien sowie die 41 Blatt- und Lösungseinträge sind unverändert übernommen. Die Übungsblätter laden die Aufgaben- und Lösungsschalter. Eingabetabellen und Koordinatenachsen mit fachlicher Funktion bleiben Teil der Aufgaben. Das Skript verwendet die gemeinsame Cloze-Implementierung mit 5-mm-Raster.

## Prüfung und Bauten

- Alle 39 vorhandenen Tests bestanden. Der TeX-Recorder des Standalone-Baus bestätigt die gemeinsame Quelle `smiley_happy.tex`. Beide Produkt-Recorder bestätigen die zentralen Hochschulgrafiken. Die PDFs beider Produkte enthalten Plus Jakarta Sans und Libertinus Math.
- Nach dem Referenzabgleich wurden zwei lokale Symbolkopien und 16 identische Schrift- und Brandingkopien entfernt. Die Schlussprüfung hat die verbliebenen Quellprüfsummen mit den erfolgreich gebauten Snapshots abgeglichen.
- Skript `9e2819d0d65c` in 12,63 s vollständig gebaut. Die deutsche Voll- und Lückenfassung haben je sechs Seiten. Im Schlusslauf wurden je Fassung alle drei TikZ-Figuren wiederverwendet. Das Raster wurde auf der gerenderten Lückenseite mit einem Abstand von 5 mm geprüft.
- Übungsblätter `05eeb59c04f7` in 34,0 s vollständig gebaut. Acht deutsche Einzelblätter je Modus sind in den Sammelfassungen mit 29 Seiten ohne und 99 Seiten mit Lösungen enthalten. Der Textabgleich der Aufgabenfassung findet keine Lösungsüberschriften oder Korrekturhinweise.
- Titel-, Lücken- und Blattseiten wurden gerendert und visuell geprüft. Beim Zusammenführen erschienen die bereits aus dem Bestand bekannten Hinweise auf doppelte `/Group`-Einträge in einzelnen Blatt-PDFs. Die Sammelfassungen wurden erfolgreich veröffentlicht und konnten gelesen werden.

## Gemeinsame Dateien (40)

| Pfad | SHA-256 |
| --- | --- |
| `_shared/commands/.gitkeep` | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` |
| `_shared/commands/cloze.tex` | `5e63cd17549d5488c707ae307ab76436cceae55535f4da3c53be3cdd4fbe9a81` |
| `_shared/commands/figures.tex` | `6aa2c5ca7818408d4e84bedd6cc72d352641820d92fb6261b70875767ab6d762` |
| `_shared/commands/language.tex` | `38c561e7c5814daa6912c50d14b51971b5cce15bdd8e2c72b86d5f275b0fb722` |
| `_shared/commands/math.tex` | `78b4bb8db7d05e13b3d2e5328849eec482b9353efcd07cd5cdc6f8f01c495f1e` |
| `_shared/commands/python-code.lua` | `f635e6570ce024ee1f46b5c94e39850073e89ce5e748d667ae5a72e4d518d6aa` |
| `_shared/commands/python-code.tex` | `e6bba60128dfdd901439c5188c5dcd99164705feeaad722fdb4a9cebcee61352` |
| `_shared/resources/.gitkeep` | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` |
| `_shared/resources/branding/THM_Logo_Fak_M_hochkant_RGB_blau.pdf` | `59b49ed807ad551fbb4ddf81a780c3967a4dc8b07689b49b8859bccca9e17993` |
| `_shared/resources/branding/THM_Logo_Fak_M_hochkant_RGB_blau.png` | `f1fb822a64d3544429ec6806ed943c28bed0eda40923f1ff4780771734d0ceea` |
| `_shared/resources/branding/THM_Logo_Fak_M_hochkant_RGB_blau.svg` | `1af93f23cb8c57f55f8aed057cf50a747fc8f24bddeba381d327cc112b80cc3d` |
| `_shared/resources/branding/THM_Logo_Fak_M_quer_RGB_blau.png` | `8ca91829ed504f93c17666abd1a22debf75d496729851827e0a1933c182f6538` |
| `_shared/resources/branding/TH_Mannheim_Favicon.pdf` | `5845ca6a08ca0633d81d0207061cdd22ef33125f3f54d44aa583f8ea5ba73a92` |
| `_shared/resources/branding/TH_Mannheim_Favicon.png` | `8e63dc4f89159851940d6c7581efdd6079c74982eae3adb920ea7c0fa9f748a4` |
| `_shared/resources/branding/TH_Mannheim_Favicon.svg` | `d0e0bc9640dc76e775f6180e41185ae8b6ab28910bc805d6863083dacf02651f` |
| `_shared/resources/branding/TH_Mannheim_Logo_RGB_blau.png` | `86be78adc60fbc6e2b1666782627d9d551248f9cdf734e15a60da12ca4b7205d` |
| `_shared/resources/branding/TH_Mannheim_TitleVisual.pdf` | `3cbde725d69af8e37f24cc26ff0b218172d2dc3547420328a31c034aefaf5ede` |
| `_shared/resources/fonts/plus_jakarta_sans/OFL.txt` | `e305459e0dab960db8295955f5abc813efb09d4fea89138572b593bee53d015c` |
| `_shared/resources/fonts/plus_jakarta_sans/PlusJakartaSans-Bold.ttf` | `3e08701b69e94031d861fa7535630815b18bc5c5382e364d17107b532fcd2995` |
| `_shared/resources/fonts/plus_jakarta_sans/PlusJakartaSans-BoldItalic.ttf` | `4486ec3d48135bf96127cc94b273d648d380f50f0ff37b3939dbcc5ec8d8635a` |
| `_shared/resources/fonts/plus_jakarta_sans/PlusJakartaSans-Italic.ttf` | `b15bc27e88f93f1dd3058ed137b799b5355cc96d58827fe3b505f77114fb1cd0` |
| `_shared/resources/fonts/plus_jakarta_sans/PlusJakartaSans-Regular.ttf` | `f7e7cebd26ac8ad800783dbc41e661dbe14ee8bc58e53c532995b13274276933` |
| `_shared/resources/tikz/smiley_happy.tex` | `e457bf3e55c609169031ea056d727e108f0354dea08ddf5f178e60cae78fecec` |
| `_shared/resources/tikz/smiley_sad.tex` | `767681dbff1f5e468a7099d358f89193ed8707736185a7e33c0a340a8a2fc5a3` |
| `_shared/style/.gitkeep` | `01ba4719c80b6fe911b091a7c05124b64eeece964e09c058ef8f9805daca546b` |
| `_shared/style/boxes.tex` | `696bebcbf90362de5f7553d7f9c370ddd8cabb442b2e8830a8d3a6f4dcacd1f3` |
| `_shared/style/branding.tex` | `59df1614aae18f98f8741b3dae7e1351eae8833898900706a3ecae16b6f5ce98` |
| `_shared/style/branding_colors.tex` | `a6a0f0ef5a89b41f9625d1d4c1ad0462c49ba908ae7942d58dfc9d28cb2b96c1` |
| `_shared/style/document.tex` | `6004992509c797c4be16696f978b091c0b20d548f9805e665bbd5659c082f9f5` |
| `_shared/style/layout.tex` | `dfe096f4b83e6d9b7ff1884ee26de9d27998260e3e1e02878240bfafe3f014a1` |
| `_shared/style/preamble.tex` | `b458883208e65832f921d6022d501e7fd80fc2fae1e19d548ac58a754a5b5816` |
| `_shared/tools/build-cache.ps1` | `345897a571b4e5120e400b1a13bc63aa591b2af3aa2b1b7c72f5f2eeb982beb5` |
| `_shared/tools/build.ps1` | `e23fb695ea3198b9e7b3dfdde528366438d473396b887425393cf4563ecb4e15` |
| `_shared/tools/build.py` | `c1ba75327a56d1d017f3a006c9064f10c471116d8a28e97fd6f3e85a413773c3` |
| `_shared/tools/build_preview.py` | `8576284f5fa79cf2755ed607866f9179b0ff188e8e475001fe83fe065ce61c22` |
| `_shared/tools/build_runtime.py` | `f154a2464350254916474bb4cf2d0f1e7b1447f033ced922dab8b785c89fa97c` |
| `_shared/tools/latexmk_common.pl` | `1cf5df6fcbc65b6c80dd29b15305b1074de079a4506ddddb294850215b04a61e` |
| `_shared/tools/requirements.txt` | `e4468726b1d529e9258794b8adf0cfab9b6a6bb3142307649aca12f573f6d8bb` |
| `_shared/tools/test_build_preview.py` | `bde8dd6a414f50910d5eaa011b509177a6dde717578bd05281528f1c77bf7f55` |
| `_shared/tools/test_build_runtime.py` | `ec76b46dc3701c7873254a36497fac432e453d20d6e4def3c2626ff311f33263` |

## Einbindungen, Bauadapter und Dokumentation (14)

| Pfad | SHA-256 |
| --- | --- |
| `_shared/README.md` | `1b8fb6af0b73cd309f7ef6efaf67e796293ce9281fdcae577aa959b18c86cb2a` |
| `Skript/common/config.tex` | `2c0347b00713cb606ecd6c5e4bad5027269c96d629f8bcbf86db8886882146ec` |
| `Skript/common/preamble.tex` | `111a4b7579b74192c71286cc4efa4641696cf145bbd56249d78cefb74a195a10` |
| `Skript/common/commands.tex` | `ff10e9cb38e5ff9228e1134c83bc9562bb9dc28dd94e34fe9abb8565b4608d79` |
| `Skript/common/layout.tex` | `d3607b16abf8e0f6e1b21835672ae714f8b538cad518fefe1dc6668c0587aaec` |
| `Skript/latexmkrc` | `2b0a69aed2afa692e8feb0bf0a96ebfb781be67dbc719f1bf35b04b6b704de01` |
| `Skript/tools/build_coordinator.py` | `bd1ea065f743acba749bebfc57964f9c2cd3e468f2ff4aebf6bd660e445db52b` |
| `Skript/tools/build-engine.ps1` | `2cc7a3969bfad8af437104b3c6cea73b875754bd9411198f00693c97ed8f36bf` |
| `Exercise Sheets/common/preamble.tex` | `7dad3e48280a99feff66bf8dcb4d5be0dcdf180a6bc5c9da8e8300471e042010` |
| `Exercise Sheets/latexmkrc` | `39320f902b92de4e42d096a27a034442da420934352df44747c3cb2cec3b956d` |
| `Exercise Sheets/tools/build_coordinator.py` | `a31596fe3b4a4d1d9feb05591241cbc766fc571a9438205592747168e39f23f1` |
| `Exercise Sheets/tools/build-engine.ps1` | `197cfb7d38f1e6653d2fb318299a1c72ada827c9b00e7bb8cbfa03869d0f4eea` |
| `Exercise Sheets/tools/cache_paths.py` | `b2cfa0e7f798158b5668f1b716c2605371fc231c903fd23202a6f7969f1a0585` |
| `Exercise Sheets/tools/requirements.txt` | `d86a40905a36ec5f451daedbc7ffdd2cb0235793abb8304d2ecd6970ffc09fb3` |

