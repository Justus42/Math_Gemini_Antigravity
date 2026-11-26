> **OpenRouter-Antwort**
>
> - Modell: openai/gpt-6.2-sol
> - Betreiber: OpenAI (laut OpenRouter)
> - Datum: 26.11.2026, 20:22
> - Tokens: Eingabe 25.722 · Ausgabe 6.455 (davon Denken 3.609) · gesamt 32.177
> - Kosten laut OpenRouter: 0,13 US-$
> - Datenregel: kein Training (data_collection: deny)
> - Denkstufe: high
> - finish_reason: stop
> - Eingelesen: docs/PHASE7_T2_REDUCTION.md (32.271 Zeichen), scripts/phase7_reps_vq.py (2.261 Zeichen), scripts/phase7_lift.py (5.178 Zeichen), scripts/gen_general_tqv.py (14.037 Zeichen), docs/LITERATURE_CHECK_PHASE7_VQ.md (13.414 Zeichen)

---

# Mathematisches Gutachten

**(1) Korrekt — §2 und §3, Aussage A einschließlich der Präzisierungen.**  
Zwei verschiedene Spalten \(c+\alpha d\) und \(c+\beta d\) bestimmen \((c,d)\) eindeutig, weil \(\beta-\alpha\ne0\). Ihre Paarüberdeckung garantiert daher, dass jeder Punkt \((c,d)\) in \(R\) vertreten ist. Bei \(j=t\) liefert die Interpolation auf den \(t\) gewählten Auswertungspunkten das eindeutige formale Polynom vom Grad \(\le t-1\); ein Vertreter für seine beiden höchsten Koeffizienten genügt.

Bei \(j=t-1\) sei \(f_0\) der Interpolant vom Grad \(\le t-2\), mit Koeffizient \(u\) bei \(x^{t-2}\). Für \(\sigma=\sum_{s\in S}s\) beginnt \(\prod_{s\in S}(x-s)\) mit \(x^{t-1}-\sigma x^{t-2}\). Folglich hat \(f_0+d\prod_{s\in S}(x-s)\) die Koeffizienten \(d\) und \(c=u-\sigma d\). **Das Pluszeichen in \(c+\sigma d=u\) ist richtig.** Die Paarüberdeckung der Spalte mit Index \(\sigma\) und der gewählten Zusatzspalte liefert genau den benötigten Vertreter. Bei \(t=q+1\) ist das Produkt \(x^q-x\): Es ist als Auswertungsfunktion null, aber als formales Polynom nicht null. Insbesondere ist für \(q=2\) die Summe aller Körperelemente \(1\), nicht \(0\). Handprobe: Für \(q=2,t=3\), Zielwerte \((0,1)\) auf \(\{0,1\}\) und \(a=0\) liefert der §14-Vertreter \((0,1,0,1)\) das Polynom \(x^2\) mit \(c+d=1\).

Bei \(j=t-2\) genügt ein Vertreter mit dem gewünschten Paar \((a,b)\); nach Abzug seiner beiden höchsten Terme bestimmt die Interpolation die unteren Koeffizienten eindeutig. Bei \(t=2\) ist dies das leere Tupel, und \(L_2=M\). Die angegebenen Leerfälle stimmen; bei \(t=q+2\) bleibt nur \(j=t-2\). Für \(q=v=2,t=4\) liefern etwa die Vertreter \((0,0,0,0)\) und \((1,0,0,0)\) mit den Polynomen \(0\) bzw. \(x^2+x\) dieselbe Zeile. Das widerspricht der Zeilenzahl mit Vielfachheit nicht.

**(2) Korrekt — §3, Aussage B.**  
Die knappe Begründung lässt sich wie folgt vervollständigen. Da \(t\le q\), kann man auf \(t\) Auswertungspunkten die Werte eines Polynoms mit beliebig vorgegebenem \((c,d)\) verlangen. Die Eindeutigkeit der Interpolation erzwingt einen Vertreter für diesen Punkt. Für die gemischten Spaltenpaare verschiebe man eine feste \((t-1)\)-elementige Menge \(S\) um \(h\); ihre Summe ändert sich um \((t-1)h\). Weil \(q\) prim und \(1\le t-1<q\) ist, werden alle \(\sigma\) erreicht. Für jedes \(u\) verlange man auf dem passenden \(S\) die Werte von \(u x^{t-2}\) und in der gewählten Zusatzspalte das gewünschte Symbol. Jede passende Liftzeile erzwingt dann \(c+\sigma d=u\). Die Paarüberdeckung von \((a,b)\) folgt durch gemeinsame Wahl beider Zusatzspalten und beliebiger \(t-2\) Auswertungsspalten. Damit sind alle Paartypen erfasst.

Die Einschränkung auf Primzahlen ist substanziell: In \(\mathrm{GF}(4)\) ist die Summe zweier verschiedener Elemente nie null. Für \(q=4,t=3\) kann man aus der vollständigen Vertreterliste alle Vertreter mit \(c=a=0\) streichen. Jeder Punkt bleibt vertreten, jede Gerade mit \(\sigma\ne0\) enthält einen Punkt mit \(c\ne0\), und alle \((a,b)\) bleiben vertreten. Der Lift deckt weiterhin Stärke 3 ab, obwohl in \(M\) das Paar \((0,0)\) in den Spalten \(c,a\) fehlt. Das ist kein Gegenbeispiel zur behaupteten Aussage B.

**(3) Korrekt — §11.1, Aussage A′.**  
Für jedes gewünschte Auswertungssymbol nimmt man das Körperelement mit derselben Nummer als Urbild unter \(\pi\). Damit greifen die drei Interpolationsfälle aus (1) unverändert. Bei \(j=t-1\) braucht man **einen** passenden Vertreter auf der Geraden, nicht das verlangte Symbol an jedem Punkt dieser Geraden. Dabei wird \(u\) im Körper berechnet und nicht re­trahiert. Die Zusatzsymbole werden nur auf Gleichheit geprüft und gehen in keine Körperrechnung ein. Die drei Bedingungen sind genau gemischte Stärke 2: Bedingung 1 ist wegen der invertierbaren Zweispaltenabbildung äquivalent zur Überdeckung aller Paare von Auswertungsspalten in \(M\); 2 und 3 erfassen die übrigen Paartypen. Eine Notwendigkeit für den re­trahierten Lift folgt daraus nicht.

**(4) Korrekt — §14.1–§14.3.**  
Die Intervalle für \(d\) sind disjunkt und passen in die \(q\) Geraden, da \(w+2n=2v-w\le q\). Jeder Punkt erhält genau einen Vertreter außer bei \(c<d<w\), wo zwei verschiedene Beschriftungen entstehen. Das ergibt genau \(q^2+\binom w2\). Für \(v=q\) stimmt die Liste punktweise mit Phase 6A überein; für \(v<q\) gilt \(w\le v-1\), also die behauptete strikte Einsparung gegenüber \(\binom v2\).

Bedingung 1 ist damit erfüllt. Für Bedingung 2 hat jedes Symbol in jeder Zusatzspalte eine feste \(d\)-Gerade, auf der es an jedem Punkt in mindestens einem Vertreter erscheint. Die Gerade \(c+\alpha d=u\) schneidet diese bei \(c=u-\alpha d\) eindeutig. Für Bedingung 3: Ist \(s\ge w\), nimmt man \(c=m\) auf der „nur \(a\)“-Geraden von \(s\); ist \(m\ge w\), entsprechend \(c=s\) auf der „nur \(b\)“-Geraden von \(m\). Sonst liefert \((s,s)\) den Diagonalfall, und am Punkt \((\min(s,m),\max(s,m))\) stehen für \(s\ne m\) beide Anordnungen. Die Vergleiche betreffen ausschließlich Nummern.

Handproben: Bei \((q,v,t)=(3,2,2)\) liefern die Spalten \(1,2\) das Ziel \((0,1)\) am Punkt \((c,d)=(2,1)\). Bei \((4,2,5)\) ist \(w=0\) und \(\sigma=0\) auf dem ganzen Körper. Für Zielwert \(1\) bei \(x=1\) und sonst \(0\) ist \(f_0=1-(x-1)^3\), also \(u=1\); der Punkt \((1,3)\) trägt das gewünschte Zusatzsymbol \(b=1\), und \(f_0+d(x^4-x)\) liefert die Zielwerte. Bei \((4,3)\) gibt es genau einen Zusatzvertreter, am Punkt \((0,1)\); bei \((5,2)\) bleibt \(d=4\) frei für die Standardbeschriftung \((0,0)\), und bei \((5,4)\) liegen die drei Zusatzvertreter an \((0,1),(0,2),(1,2)\).

**(5) Korrekt — die genannten Skripte für gültige Eingaben.**  
`reps_vq` setzt alle vier Fälle mit den richtigen Intervallgrenzen um; `sorted` ändert nur die Reihenfolge. `lift` erzeugt Potenzen von \(0\) bis \(t-1\) und genau \(t-2\) freie Koeffizienten vor `[c, d]`. Auch für `t=2` liefert `itertools.product` genau ein leeres Tupel. `pi` wird erst auf den fertigen Auswertungswert angewandt. `m_rows` rechnet im Körper ohne Retraktion; `uncovered_pairs` verwendet für das Spaltenpaar genau das Produkt der zugehörigen Alphabetgrößen. Bei gültigen Symbolbereichen ist die Differenz zur Zahl verschiedener beobachteter Paare exakt die Fehlzahl. `--check-m` prüft also die Voraussetzung, nicht unmittelbar den Lift.

`GeneralGF` implementiert für Primzahlen die Rechnung modulo \(p\), sonst die Rechnung in der Polynombasis modulo einem irreduziblen Polynom. `_is_irreducible` erfasst jeden möglichen irreduziblen Faktor vom Grad \(k\le\lfloor r/2\rfloor\) über \(X^{p^k}-X\); ein reduzibles Polynom hätte mindestens einen solchen Faktor. Die Ziffernrechnung stimmt damit überein. Handprobe für \(q=4\): Modulus \(X^2+X+1\), Nummer \(2\) für \(X\), also \(2\cdot2=3\) und \(2+3=1\) in Elementnummern. Kein Indexfehler im geprüften Bereich.

**(6) Korrekt — Literaturvergleich, beschränkt auf die Beschreibung in §2.6.**

- **(a)** Die CKRS-Liste besetzt alle Punkte, auch den Ursprung, und hat wegen der disjunkten Teile genau \(q^2-1+q(q-1)\) Vertreter. Für ein gemischtes Paar mit Symbol \(s\) nimmt man auf \(c+\alpha d=u\) den Punkt mit \(d=s\). Ist dies der Ursprung, liefern die dortigen ungleichen Paare das Symbol \(0\) in beiden Zusatzspalten, gegebenenfalls in verschiedenen Vertretern. Ungleiche \((a,b)\) liegen am Ursprung; \((s,s)\) erhält man bei \(d=s,c\ne0\). Das gilt auch für \(q=2\).
- **(b)** Bei \(t=s\) liefert der erste Listenteil genau die Polynome mit verdoppeltem Leitkoeffizienten, nach Entfernung des Blocks \(c=d=0\). Jeder Vertreter des zweiten Teils liefert genau die Polynome vom Grad \(<s-2\) mit einem festen ungleichen Paar. Die Beschreibung und die Liste entsprechen einander.
- **(c)** „Verfeinerung“ ist als Bezeichnung des gemeinsamen Konstruktionsprinzips sachgerecht: dieselben unteren Polynomkoeffizienten als Blockparameter, aber andere Beschriftung und Verteilung der Zusatzblöcke. Irreführend wäre „Ausdünnung“ im Sinne einer Teilmenge des CKRS-Arrays. Der Vergleich mit \(q(q-1)-1\) betrifft den **Nettoüberschuss** gegenüber \(q^2\), und bei \(q=2\) gibt es keine strikte Einsparung.

**Stillschweigende Konventionen und Vorbedingungen.** Die Nummerierung muss überall dieselbe sein und insbesondere die Körpernull und -eins durch `0` und `1` darstellen. Der leere untere Koeffiziententeil bezeichnet das Nullpolynom. „Vertreter“ sind Koeffizientenvorgaben, keine Garantie verschiedener Nebenklassen oder Ausgabezeilen; die in §14.1 genannte Vielfachheitskonvention gilt schon in §2. `uncovered_pairs` setzt direkt aufgerufen eine nichtleere, rechteckige Tabelle mit gültigen Symbolen voraus. Für die CLI ist ohne `--known` eine Vertreterdatei, bei `--t` ein Ausgabepfad nötig; fehlende Argumente werden nicht eigens abgefangen.

**Gesamturteil:** Die geprüfte Beweiskette ist tragfähig, und der vorgelegte Code setzt sie auf dem angegebenen Eingabebereich korrekt um.

**Nicht geprüft:** CKRS-Original und dessen exakter Geltungsbereich jenseits der vorgegebenen Beschreibung; tatsächliche Skriptläufe, Dateihashes und externe Verifikatoren; Löserprotokolle, gespeicherte Arrays und Tabellenvergleiche außerhalb der sechs Prüfglieder.
