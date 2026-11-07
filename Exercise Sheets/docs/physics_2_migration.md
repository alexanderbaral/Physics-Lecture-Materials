# Übernahme der Physik-2-Übungsblätter

Die Blattnummern 1 bis 8 geben die Arbeitsreihenfolge in `common/config.tex` an. Die technischen Pfade eignen sich als Zuordnung für die entsprechenden Abschnitte im späteren Gesamtskript. Bei der Ergänzung von Physik 1 wird die Nummerierung im Register angepasst.

## Herkunft und Lösungen

Die Quellen liegen unter `../../_shared/legacy/Exercise Sheets/`. Seitenangaben zählen ab der ersten PDF-Seite. Die 30 extrahierten Lösungsdateien enthalten zusammen 52 Originalseiten. Die gesetzten Lösungen und Antwortschlüssel stehen in `Solution` in der zugehörigen Aufgabendatei.

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

Der Bildvergleich stellt 17 TikZ-Abbildungen und drei Labortabellen den jeweiligen Originalausschnitten gegenüber. [Abbildungsvergleich](abbildungsvergleich_physik_2.pdf)
