# Auftrag: Prüfung von Notiz 4 zu Phase 8 (Untergrenzen C.1 und C.2)

Du bekommst das Dokument `docs/phase8/NOTIZ_4_UNTERGRENZEN_C1_C2.md` (verfasst von Sprachmodellen, die die Schranken
selbst entwickelt haben) und als Hintergrund `docs/phase8/NOTIZ_3_UNTERGRENZE_BAER.md` (Lemma J, Satz U, Aussage U')
und `docs/PHASE8_ARGUMENTE.md` (Rahmen und Notation, Aussagen 1.1 und 1.5). Du hast an nichts davon mitgewirkt.
Deine Aufgabe ist, Fehler zu finden. Die Schranken liegen sehr nah an den besten bekannten Listen (für `p = 5` ist
die Schranke gleich dem besten bekannten Wert `34`); gerade deshalb ist jeder einzelne Schritt verdächtig.

1. Prüfe Satz C.1 (ungerade Primzahlen, `v = p`) und Satz C.2 (Quadratzahlen, `v = q`) Schritt für Schritt und gib je
   Schritt ein Urteil: korrekt / korrekt mit Lücke (welche) / falsch (wo, mit Gegenbeispiel wenn möglich).
   Achte besonders auf:
   - ob die Schranke für **jede** Liste `R` im Modell gilt oder stillschweigend eine Struktur voraussetzt (zum
     Beispiel ein bestimmtes Skelett, eine einzige schwere Gerade, Klassen einer bestimmten Bauart, Mengen statt
     Multimengen, jede Klasse höchstens eine volle Waagerechte);
   - jede Fallunterscheidung: Sind die Fälle vollständig? Wird in jedem Fall wirklich das Minimum genommen?
   - jede Stelle, an der zwei Ungleichungen addiert oder gemittelt werden: Zählen sie dieselben Vertreter doppelt?
   - den Einsatz der Sätze von Blokhuis (`(3p+1)/2` Punkte für eine Klasse ohne volle Waagerechte), Jamison bzw.
     Brouwer–Schrijver und von Lemma J: Sind die Voraussetzungen jeweils erfüllt?
   - Ganzzahligkeit: Wo wird gerundet, und ist die Rundungsrichtung zulässig?
   - die Asymptotik `91/68 * p^2` und `q^2 + q^(3/2) - (9/8) q`: Folgt sie aus der exakten Schranke?
2. Rechne kleine Fälle von Hand nach und sage, was du wirklich gerechnet hast: die Werte der Schranke C.1 für
   `p = 3, 5, 7` (laut Notiz `12, 34, 66`) und der Schranke C.2 für `q = 4, 9` (laut Notiz `20, 99`). Prüfe für
   `p = 3`, ob die Behauptung „kleinster Wert im Modell ist `12`“ aus dem Argument folgt oder nur aus einer Suche.
3. Versuche ausdrücklich, die Schranken zu **unterbieten**: Gibt es eine Liste oder auch nur eine Belegung der in den
   Beweisen benutzten Größen (Zahl der Klassen ohne volle Gerade je Seite, Verteilung der vollen Geraden auf die
   Waagerechten, Vertreterzahlen je Waagerechte), die alle im Beweis benutzten Ungleichungen erfüllt und kleiner ist
   als die behauptete Schranke? Wenn ja, ist der Satz in dieser Form nicht bewiesen.
4. Prüfe, ob die Notiz irgendwo mehr behauptet, als ihre Argumente tragen (zum Beispiel „exakt“, „Optimum“,
   „Minimum“), und ob die Belegart zu den Aussagen passt.
5. Kein Urteil über Neuheit oder Bedeutung. Du führst kein Programm aus und hast weder Listen noch Skripte noch die
   Originalquellen gesehen; sage ausdrücklich, was du nicht prüfen konntest.

Antworte auf Deutsch, knapp, mit einer Tabelle der Urteile am Anfang und einem Gesamturteil je Satz:
„trägt“ / „trägt mit Lücke“ / „trägt nicht“.
