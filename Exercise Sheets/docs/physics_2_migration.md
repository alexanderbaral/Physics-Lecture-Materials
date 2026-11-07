# Übernahme der Physik-2-Übungsblätter

Die Blattnummern 1 bis 8 in diesem Protokoll entsprechen dem Stand des Imports. Im gemeinsamen Register für Physik 1 und 2 sind dies die Blätter 8 bis 15. Die Kapitelpfade bleiben als Zuordnung für das spätere Gesamtskript erhalten.

## Herkunft und Lösungen

Die importierten Quell-PDFs lagen im inzwischen auf Autorenwunsch entfernten Ordner `_shared/legacy/Exercise Sheets`. Die folgende Tabelle bewahrt Dateinamen und Seitenzuordnung. Seitenangaben zählen ab der ersten PDF-Seite. Die 30 weiterhin eingebundenen, extrahierten Lösungsdateien unter `content/resources/chapters/` enthalten zusammen 52 Originalseiten. Gesetzte Musterlösungen stehen in `Solution` in der zugehörigen Aufgabendatei. Bei Verständnisfragen steht der schaltbare Wahrheitswert direkt hinter der jeweiligen Aussage. Die benachbarten Originalordner `Physik 1` und `Physik 2` wurden bei der Bereinigung nicht verändert.

| Blatt | Verzeichnis | Quell-PDF | Eingebundene Originalseiten je Aufgabe |
| --- | --- | --- | --- |
| 1 | `differential_equations` | `Lösungen zum Übungsblatt 00 - DGLs in der Dynamik.pdf` | Lösungen aus S. 1, 3, 6–8 und 10–11 in LaTeX |
| 2 | `free_oscillations` | `PHY2_ExSheet1_withSol.pdf` | 1 → 3, 2 → 5, 3 → 7, 4 → 9, 5 → 11–12, 6 → 14–15, 7 → 17–18. Antwortschlüssel aus S. 1 in LaTeX. |
| 3 | `forced_oscillations` | `ExSheet2 - withSol.pdf` | 1 → 3–4, 2 → 6, 3 → 8–9. Antwortschlüssel und Python-Lösung aus S. 1 und 11 in LaTeX. |
| 4 | `wave_propagation` | `Physik___Exercise_Sheets.pdf` | 1 → 3, 2 → 5, 3 → 7–9, 4 → 11–12, 6 → 15–16. Antwortschlüssel aus S. 1 in LaTeX. |
| 5 | `doppler_and_interference` | `ExSheet 3 - mit Lsg.pdf` | 1 → 2–3, 2 → 5–6, 3 → 8–9, 4 → 11–12, 5 → 14–15 |
| 6 | `geometrical_and_wave_optics` | `ExSheet_Lsg.pdf` | 1 → 3–4, 2 → 6, 3 → 8, 4 → 10–11, 5 → 13, 6 → 15, 7 → 17. Antwortschlüssel aus S. 1 in LaTeX. |
| 7 | `quantum_optics` | `Lösungen zu Übungsblatt 7 - Quantenoptik.pdf` | Lösungen aus S. 1, 3, 5–6, 8, 10 und 12–13 in LaTeX |
| 8 | `laboratory_measurements` | `Physik___Exercise_Sheet X.pdf` | 4 → 5–6, 5 → 8–9, 6 → 12–16. Lösungen zu 1 und 2 aus S. 1–2 in LaTeX. |

Die Quellnummern springen von 5 auf 7. Ein altes Blatt 6 lag im Upload nicht vor. Für Blatt 4 Aufgabe 05, Blatt 5 Aufgabe 06 und Blatt 8 Aufgabe 03 lag keine Musterlösung im jeweiligen PDF vor. Diese drei Aufgaben sind mit Status `unavailable` registriert. Verweise auf Begleitdateien bleiben in den Aufgaben erhalten. Der Labordatenauszug ist vollständig als Tabelle erfasst. Er ersetzt die im Original erwähnte vollständige Excel-Datei nicht.

## Fachliche Präzisierungen

- **Blatt 1.** Die Anfangsbedingung beim Zerfall bezieht sich auf $t=1\,\mathrm{s}$. Für die sinkende Kugel sind Vorzeichenrichtung und Modellannahmen angegeben. Die allgemeine harmonische Lösung wird mit Linearität und zwei unabhängigen Anfangswerten begründet.
- **Blatt 2.** Auch andere Systeme als Federpendel können harmonisch schwingen. Beim aperiodischen Grenzfall ist $y(0)$ vorgegeben. Der Exponent der Ionenfallenkraft erhält mit $x/\ell$ ein dimensionsloses Argument.
- **Blatt 3.** Im Python-Plot markiert eine senkrechte Linie die Resonanzkreisfrequenz. Die Musterlösung behandelt auch den Fall ohne Resonanzmaximum bei positiver Frequenz.
- **Blatt 4.** Zeit- und Ortsperiodizität sind für die harmonische Welle formuliert. Die ideale ungedämpfte ebene Welle hat konstante Intensität. Für Ultraschall ist das verwendete Dehnwellenmodell im schlanken Stab angegeben.
- **Blatt 5.** Im vierten Doppler-Szenario ist Licht mit doppelter Frequenz gemeint. Die Dreiecksreihe beginnt wie im dargestellten Kurvenverlauf bei $n=1$. Die Rohrskizze zeigt die in der Lösung verwendeten Randbedingungen bei $x=0$ und $x=L$.
- **Blatt 6.** Stärkere Beugung bei gleicher Öffnung gehört zur größeren Wellenlänge. Das Fermatsche Prinzip ist über stationäre Laufzeit formuliert. Die Münzaufgabe benennt die rückwärtige Strahlverlängerung und die Doppelspaltaufgabe die Teilaufgabe, mit der verglichen werden soll.
- **Blatt 7.** Die Wasserstofftabelle wurde aus der reduzierten Masse neu berechnet. Das Maximum des Wärmespektrums wurde bei etwa 1050 nm abgelesen. Die natürliche und die Dopplerbreite werden einheitlich als volle Breiten bei halbem Maximum verglichen. Bei der Dopplerbreite zählt die Geschwindigkeitskomponente in Beobachtungsrichtung.
- **Blatt 8.** Die vier Messszenarien sind einzeln nummeriert. Im Diagramm der dynamischen Federmessung ist $\overline T^2$ aufzutragen. Der Verweis auf die Periodengleichung wird automatisch gesetzt.

Zwei gesetzte Hinweise ergänzen die jeweiligen Originalseiten in der Lösungsfassung. Beim Doppelspalt ergibt die vorgegebene Wellenlänge als höchste Ordnung 15. Bei der Fehlerfortpflanzung sind die relative Durchmesserunsicherheit und die vollständige Ableitung nach der Zeit berücksichtigt.

## Abbildungen

Die Aufgabenabbildungen und die gesetzte Skizze zur Endgeschwindigkeit sind als externe TikZ-Dateien übernommen. Die Messkurven wurden aus den Vorlagen abgelesen und als Vektorkurven nachgezeichnet. Tabellen sind als editierbare LaTeX-Tabellen gesetzt. Abbildungen innerhalb handschriftlicher Lösungen bleiben Bestandteil der Originalseiten.

17 TikZ-Abbildungen und drei Labortabellen wurden mit den jeweiligen Originalausschnitten verglichen. Die gemeinsame Nachprüfung mit Astra und die anschließende Autorenprüfung umfassten 45 Originalvergleiche für 42 unterschiedliche TikZ-Abbildungen. Alle Abbildungen sind freigegeben; siehe [Freigabestand](abbildungen_freigabestand.md). Die Vergleichs-PDFs wurden nach Abschluss der Prüfung auf Autorenwunsch gelöscht.

### Rückmeldungen zum Abbildungsvergleich

Die früheren Vergleiche 26/31 und 27/32 verwenden jeweils dieselbe TikZ-Quelle (`damped_displacement.tex` bzw. `disk_and_springs.tex`); lediglich die Originalvorlagen aus Physik 1 und 2 unterscheiden sich.

Beim Flötenmodell sind Mundstück und festes bzw. loses Ende für die Luftauslenkung ausdrücklich dargestellt. Die Begriffe entsprechen dem [Vorlesungsexperiment der Universität Mainz](https://vorlesungsexperimente.fb08.uni-mainz.de/versuch-109-reflexion-einer-welle-am-festen-und-losen-ende/). Die Randbedingungen der Vorlage bleiben erhalten; die Zeichnung beschreibt das vereinfachte Aufgabenmodell.

Das Wärmespektrum verwendet relative Intensität ohne den unnötigen Faktor 10^11. Kurvenform, Wellenlängenskala und die für die Aufgabe benötigte Lage des Maximums bleiben erhalten. Lichtstrahlen sind goldfarben; die Doppelspaltgrafik zeigt die ebene einfallende Welle als Fläche, den Gangunterschied als bemaßte Strecke B–Q und beide geometrisch gleichen Winkel. Die Punkte B und Q sind technische Koordinatennamen der TikZ-Quelle.
