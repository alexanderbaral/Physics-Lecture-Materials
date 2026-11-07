# Übernahme der Physik-1-Übungsblätter

Die Quellen liegen neben dem Projekt unter `../Physik 1/Übungsblätter/`. Das Register in `common/config.tex` vergibt die aktuellen Nummern für Physik 1 und 2. Die Verzeichnisse und Aufgaben-IDs bleiben beim späteren Einfügen weiterer Blätter stabil.

| Physik-1-Quelldatei | Aktuelles Blatt | Kapitel-ID |
| --- | --- | --- |
| `Übungsblatt _01_Kinematik_1D.tex` | 1 · Kinematik in einer Dimension | `linear_kinematics` |
| `Übungsblatt _02_Kinematik_nD.tex` | 2 · Kinematik in mehreren Dimensionen | `multidimensional_kinematics` |
| `Übungsblatt _03_Kraefte.tex` | 3 · Kräfte | `forces` |
| `Übungsblatt _04_Arbeit und Energie.tex` | 4 · Arbeit und Energie | `work_and_energy` |
| `Übungsblatt _05_2TeilchenSysteme.tex` | 5 · Zwei-Teilchen-Systeme und Stöße | `two_particle_systems` |
| `Übungsblatt _06_Drehimpuls.tex` | 6 · Drehimpuls und Drehmoment | `angular_momentum` |
| `Übungsblatt _07_StarreKoerper.tex` | 7 · Starre Körper | `rigid_bodies` |
| `Übungsblatt _08_Schwingungen.tex` | 9 · Freie Schwingungen und eine Verständnisfrage auf Blatt 10 | `free_oscillations`, `forced_oscillations` |

## Aufgaben und Lösungen

Für die Blätter 1 bis 7 wurden 60 Aufgaben und sieben Blöcke mit Verständnisfragen in einzelne LaTeX-Dateien überführt. 56 handschriftliche Lösungs-PDFs mit insgesamt 88 Seiten liegen unverändert im jeweiligen Ordner `solutions/`. Die Lösung zum Python-Drehimpulsvektor verwendet die vorhandene Python-Datei in einer `Solution`-Umgebung. Die Berechnung verwendet die gesetzte Masse und begrenzt das Argument von `arccos` auf sein Definitionsintervall.

Die sieben Rechenaufgaben des Schwingungsblatts sind bereits auf Blatt 9 enthalten. Die Frage zur Erregerfrequenz steht auf Blatt 10. Bei sechs handschriftlichen Lösungen stimmen die Bilder der Seiten in beiden Quellen überein. Bei der anharmonischen Ionenfalle bleibt die vorhandene Fassung mit der korrigierten Kraftkurve aktiv.

Alle Verständnisfragen verwenden `\TrueFalseAnswer` direkt hinter der Aussage. Die Aufgabenfassung blendet die Kennzeichnung aus. Die Lösungsfassung zeigt an dieser Stelle nur **wahr** oder **falsch**. Das gilt auch für die übernommenen Blätter aus Physik 2.

## Fachliche Präzisierungen

- Kinematik. Momentangeschwindigkeit, vorzeichenbehaftete Integration und konstanter Fallbeschleunigungswert sind präzisiert. Beim schiefen Wurf ist der Luftwiderstand ausdrücklich ausgeschlossen.
- Kräfte. Die Aussagen unterscheiden Haft- und Gleitreibung und beziehen die Kraftzerlegung auf eine vorgegebene Richtung. Beim Fallschirmspringer ist das verwendete Modell für die Stirnfläche angegeben.
- Energie und Stöße. Die Aufgaben unterscheiden konstante Kraft und ideale Feder. Beim Stoß sind der vernachlässigbare äußere Kraftstoß und der Fall eines vollkommen inelastischen Stoßes angegeben.
- Drehimpuls und starre Körper. Bezugs- und Drehachsen sowie Bedingungen der Erhaltung sind angegeben. In der Trichteraufgabe bezeichnet α wie in der Originalrechnung den vollen Öffnungswinkel. Teilaufgabe b) fragt ausdrücklich nach der axialen Drehimpulskomponente. Beim Hinaufrollen sind Masse und Modell der Rollreibung angegeben.

## Offene Stellen der Vorlage

Für die Python-Aufgaben 1.10 (Bewegungsdiagramme), 2.09 (Winkelgeschwindigkeit und Winkelbeschleunigung) und 3.12 (Kraftvektoren) liegt keine Musterlösung vor. Die vorhandenen Codebeispiele für 1.10 und 3.12 gehören zur Aufgabenfassung. Der Verweis in 6.06 d) wurde über Aufgabe 33(d) in `Physik_Booklet_Sprint__4.pdf` aufgelöst. Aufgabenwortlaut und Kurzlösung sind für diese Teilaufgabe gesetzt. Für a) bis c) bleibt das handschriftliche Original eingebunden.

## Abbildungen

28 Originalabbildungen wurden mit ihren TikZ-Fassungen verglichen. Die drei Abbildungen zum Schwingungsblatt stammen aus der vorhandenen TikZ-Fassung. Skizzen in handschriftlichen Lösungsseiten bleiben Teil der jeweiligen Original-PDF.

Die gemeinsame Nachprüfung mit Astra und die anschließende Autorenprüfung umfassten 45 Originalvergleiche für 42 unterschiedliche TikZ-Abbildungen. Alle Abbildungen sind freigegeben; siehe [Freigabestand](abbildungen_freigabestand.md). Die Vergleichs-PDFs wurden nach Abschluss der Prüfung auf Autorenwunsch gelöscht. Der Originalordner `Physik 1` außerhalb des Projekts blieb unverändert.

Nach der Vergrößerung der Abbildungen steht das längere Python-Beispiel in `forces/python_force_vectors.tex` außerhalb des gemessenen `ExerciseBlock`. So kann die vorhandene `PythonCode`-Umgebung regulär umbrechen; die verschachtelte, umbrechbare Codebox hatte abhängig vom Seitenrest eine Seite je Codezeile erzeugt. Aufgabenstellung, Python-Quelle und gemeinsame Commands bleiben erhalten.
