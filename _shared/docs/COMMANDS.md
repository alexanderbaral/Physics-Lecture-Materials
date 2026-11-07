# Befehlsübersicht

Skript und Übungsblätter laden die gemeinsamen Sprach-, Mathematik-, TikZ- und Python-Befehle aus `_shared/commands/`.

| Datei | Zentrale Schnittstellen |
| --- | --- |
| `language.tex` | `\Lang{de}{en}`, `\IfEnglishTF`, `\EnglishTerm`, `\GermanTerm` |
| `math.tex` | `\EquationBranches`, `\EquationMerge`, `\TransformOp`, `\MathHighlight`, `\RightAngleMark`, `\R`, `\N`, `\Q`, `\Z`, `\C` |
| `figures.tex` | `\CachedTikzFigure{pfad.tex}` |
| `python-code.tex` | `\PythonCode[Titel]{pfad.py}` und `\PythonCode[Titel]{pfad.ipynb}` |
| `cloze.tex` | `\IfClozeTF`, `\Cloze{Breite}{Inhalt}`, `ClozeArea[Spalten]{Zeilen}`, `ClozeContinuation[Spalten]{Zeilen}` |

Das Skript lädt zusätzlich `cloze.tex`. Die Rastermaße zählen 5-mm-Quadrate.

Die Übungsblätter verwenden `ExerciseBlock` und `\ExerciseHeading` für die Aufgaben. `Solution` und `\UseExerciseSolution` stehen in `Exercise Sheets/common/commands.tex` und folgen dem Schalter `ShowSolutions`. Eingabetabellen und Koordinatensysteme mit fachlicher Funktion gehören zur Aufgabe.
