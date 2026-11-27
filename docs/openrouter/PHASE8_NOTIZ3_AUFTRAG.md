# Auftrag: Prüfung von Notiz 3 zu Phase 8 (Untergrenze und Baer-Gitter)

> **Entwurf vom 27.11.2026, 10:10 MEZ (Claude, Phase-8-Chat Nachfolger). NICHT abgeschickt.** Ein Aufruf über die
> Bridge braucht die Freigabe von Justus in seinen Worten. Vorgesehen: ein unbeteiligtes Modell, Denkstufe `high`,
> mit `docs/phase8/NOTIZ_3_UNTERGRENZE_BAER.md` im Stand des dann aktuellen Commits und als Hintergrund
> `docs/PHASE7_T2_REDUCTION.md` (§2, §3, §11) sowie `docs/PHASE8_ARGUMENTE.md` (nur „Rahmen und Notation“).

Du bekommst das Dokument `docs/phase8/NOTIZ_3_UNTERGRENZE_BAER.md` (verfasst von einem Sprachmodell, das die Bauart
selbst entwickelt und gerechnet hat; §2.4 stammt von einem zweiten Sprachmodell) und als Hintergrund
`docs/PHASE7_T2_REDUCTION.md` und den Abschnitt „Rahmen und Notation“ aus `docs/PHASE8_ARGUMENTE.md`.
Du hast an nichts davon mitgewirkt. Deine Aufgabe ist, Fehler zu finden.

1. Prüfe Schritt für Schritt und gib je Punkt ein Urteil: korrekt / korrekt mit Lücke (welche) / falsch (wo, mit
   Gegenbeispiel wenn möglich).
   - **Lemma J** (§2.1): `|A| >= q + m - 1`. Ist der Schluss aus dem Satz von Jamison bzw. Brouwer–Schrijver
     (`2q - 1` Punkte für eine Menge, die jede Gerade von `AG(2, q)` trifft) richtig angewandt? Gilt er für jede
     Primzahlpotenz `q`? Stimmen die drei Gleichheitsfälle?
   - **Satz U** (§2.2), Schritte (a) bis (d): insbesondere `p_d <= M_d`, `p_d <= mu_d * nu_d`, die Summe
     `sum_s m_s = sum_d mu_d`, die Ungleichung `sqrt(p) >= min(p, q)/sqrt(q)` und die Kombination in (d).
   - **Aussage U'** (§2.4): die Sekante auf `[q, q^2]`, die Ungleichung
     `sqrt(p) >= p/sqrt(q) - max(0, p - q)/(sqrt(q) + 1)` auf ganz `[0, q^2]` und die Kombination zu
     `|R| >= q^2 + (q^2 - q)/(sqrt(q) + 2)`.
   - **Baer-Gitter** (§3.1, §3.2): Sind die Klassen `K(i, j)` wirklich affine Teile von Baer-Unterebenen, die den
     Fernpunkt der Waagerechten enthalten und die Ferngerade nur dort treffen? Trifft jede Klasse jede Gerade
     `c + al*d = u`? Sind Punktabdeckung, alle Symbolpaare (Klasse mit Klasse, Klasse mit Vollgeraden-Symbol,
     Vollgeraden-Symbol mit Vollgeraden-Symbol) und die Zählung `|R| = q(q-1) + (q-n)(n+F) + n*max(F,1)` richtig?
2. Rechne kleine Fälle von Hand nach, wo das geht: das Baer-Gitter für `q = 4` (`n = 2`, `F = 0, 1, 2`, Sollwerte
   `18, 20, 24`) vollständig; für `q = 9` mindestens eine `a`-Klasse und eine `b`-Klasse samt ihrem gemeinsamen
   Punkt; `L(q)` und `L'(q)` für `q = 2, 3, 4, 9`. Sage dazu, was du wirklich gerechnet hast.
3. Nenne stillschweigende Voraussetzungen und Randfälle: Charakteristik `2`; `F = 0` (Füllsymbol); `F = n`;
   `n = 2`; die Wahl von `om`; Listen als Multimengen; `v < q` (wo gilt Satz U nicht?); ob `p_d` wohldefiniert ist,
   wenn ein Paar auf mehreren Waagerechten liegt.
4. Prüfe, ob die Notiz irgendwo mehr behauptet, als ihre Argumente tragen (zum Beispiel in §1, §4 und §5), und ob
   die Belegarten („Argument“, „gezählt“, „dual-verifiziert“, „Vorhersage“, „Überschlag“) zu den Aussagen passen.
5. Kein Urteil über Neuheit oder Bedeutung. Du führst kein Programm aus und hast weder Listen noch Skripte noch die
   Originalquellen (Jamison 1977; Brouwer–Schrijver 1978) gesehen; sage ausdrücklich, was du nicht prüfen konntest.

Antworte auf Deutsch, knapp, mit einer Tabelle der Urteile am Anfang.
