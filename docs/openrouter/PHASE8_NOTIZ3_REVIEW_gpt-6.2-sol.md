> **OpenRouter-Antwort**
>
> - Modell: openai/gpt-6.2-sol
> - Betreiber: OpenAI (laut OpenRouter)
> - Datum: 27.11.2026, 10:29
> - Tokens: Eingabe 36.233 · Ausgabe 10.387 (davon Denken 6.676) · gesamt 46.620
> - Kosten laut OpenRouter: 0,19 US-$
> - Datenregel: kein Training (data_collection: deny)
> - Denkstufe: high
> - finish_reason: stop
> - Eingelesen: docs/openrouter/PHASE8_NOTIZ3_AUFTRAG.md (2.988 Zeichen), docs/phase8/NOTIZ_3_UNTERGRENZE_BAER.md (19.421 Zeichen), docs/PHASE7_T2_REDUCTION.md (32.832 Zeichen), docs/PHASE8_ARGUMENTE.md (35.521 Zeichen)

---

| Prüfpunkt | Urteil |
|---|---|
| Lemma J (§2.1) | **Korrekt** für jede Primzahlpotenz. Die drei Gleichheitsbeispiele stimmen in ihrem jeweiligen Geltungsbereich; sie sind keine vollständige Liste. |
| Satz U, Schritte (a)–(d) | **Korrekt** für \(v=q\). Die Zuordnung der Paare muss einmal gewählt werden, aber nicht eindeutig vorgegeben sein. |
| Zusatz zu U: „für \(v<q\) nichts über \(q^2\) hinaus“ | **Falsch.** Die unveränderte Schranke gilt nicht, aber das angepasste Argument liefert für manche \(v<q\) mehr als \(q^2\). |
| U′ (§2.4) | **Korrekt.** Sekante, stückweise Abschätzung, Elimination und Schrankenwert stimmen. |
| Baer-Klassen und Geradentreffer (§3.2.1) | **Korrekt mit Lücke:** Die angekündigten affinen Abbildungen sind nicht angegeben. Sie lassen sich explizit ergänzen. |
| Punktabdeckung, Paare und Zählung (§3.1–2) | **Korrekt mit Lücke** bei Nummerierung und Füllung. **Falsch** ist die unbeschränkte Aussage vom einzigen gemeinsamen Punkt in §3.2.3: Sie gilt nur für \(d\ne0\). |
| Zusammenfassung und Belegstatus (§§1, 4, 5) | **Teils falsch bzw. zu weit formuliert:** erster Symbolzuwachs, endlicher Faktor \(2\), Reichweite der zwei Zähler. Die Statusangaben in §4 unterscheiden die Prüfarten dagegen sauber. |

### Untergrenzen

**J.** Die Geraden \(c+\alpha d=u\), für alle \(\alpha,u\in\mathbb F_q\), sind genau die nicht-waagerechten affinen Geraden. Die \(q-m\) hinzugefügten Punkte sind neu und ergänzen genau die fehlenden Waagerechten. Der affine Blockierungssatz von Jamison bzw. Brouwer–Schrijver gilt in dieser Form für jede Primzahlpotenz, nicht nur für Primzahlen. Damit ist \(|A|+q-m\ge 2q-1\) richtig. Die angegebenen Werte \((m,|A|)\) sind \((1,q)\), \((n+1,q+n)\) für die geometrische Baer-Klasse und \(((q+3)/2,(3q+1)/2)\) für \(A(e)\) bei ungeradem \(q\). Beim letzten Beispiel verwende ich den referierten Geradentreffer aus 1.2, ohne ihn hier zu prüfen. Falls „Gleichheit“ als Klassifikation gemeint ist: Schon eine volle Waagerechte plus ein Punkt auf einer zweiten gibt für \(q\ge3\) einen weiteren Fall.

**U, schrittweise.** Setze \(r=\sqrt q\), \(N=|R|\) und \(X=N-q^2\).
- **(a)** Einmal pro Paar eine bezeugende Waagerechte wählen. Verschiedene Paare brauchen verschiedene Vertreter, daher \(p_d\le M_d\); sie liegen außerdem im Produkt der dort vorkommenden Symbolmengen, daher \(p_d\le\mu_d\nu_d\). Punktabdeckung gibt \(M_d\ge q\), zusammen also \(X\ge E\). Liegt ein Paar auf mehreren Waagerechten, hängt \(p_d\) von der Wahl ab; der Beweis gilt für jede Wahl.
- **(b)** \(\sum_s m_s=\sum_d\mu_d\) zählt dieselben Inzidenzen \((s,d)\). Die Klassen sind Punktmengen, die Vertreterliste ist eine Multimenge: Wiederholungen erhöhen \(N\), nicht die Klassengrößen. Deshalb ist \(N\ge\sum_s|A_s|\) richtig. J auf beiden Seiten, Mittelwert und AM–GM ergeben \(N\ge q^2-q+\sum_d\sqrt{p_d}\).
- **(c)** Für \(0\le p\le q\) gilt \(\sqrt p\ge p/r\), für \(p\ge q\) gilt \(\sqrt p\ge r\). Da \(\sum_d p_d=q^2\), ist \(\sum_d\min(p_d,q)=q^2-E\).
- **(d)** Damit \(X\ge q(r-1)-E/r\). Addition von \(X/r\ge E/r\) ergibt die behauptete Schranke.

**U′.** Die Sekante auf \([q,q^2]\) hat Steigung \((q-r)/(q^2-q)=1/(q+r)=1/r-1/(r+1)\). Der angegebene Ausdruck ist dort genau diese Sekante und auf \([0,q]\) gleich \(p/r\). Also \(X\ge q(r-1)-E/(r+1)\); mit \(X\ge E\) folgt \(X\ge(q^2-q)/(r+2)\). Auch der angegebene Gewinn stimmt. „Kleinste ganze Zahl über“ muss **Aufrundung** heißen, nicht „strikt größer“.

| \(q\) | Reelle Schranke U | \(L(q)\) | Reelle Schranke U′ | \(L'(q)\) |
|---:|---:|---:|---:|---:|
| 2 | \(4{,}485\ldots\) | 5 | \(4{,}586\ldots\) | 5 |
| 3 | \(10{,}392\ldots\) | 11 | \(10{,}608\ldots\) | 11 |
| 4 | \(18\tfrac23\) | 19 | \(19\) exakt | 19 |
| 9 | \(94{,}5\) | 95 | \(95{,}4\) | 96 |

Für **\(v<q\)** bleiben J und (a) gültig, aber in (b) steht \(v(q-1)\) statt \(q(q-1)\), und \(\sum_d p_d=v^2\). Damit liefert dasselbe Verfahren
\[
X(1+1/r)\ge v(q-1)+v^2/r-q^2.
\]
Bei \((q,v)=(9,8)\) folgt schon \(N\ge85>81\). Die unveränderte Schranke U ist dagegen bei \((4,2)\) falsch: Das Baer-Gitter unten hat \(18<18\tfrac23\) Vertreter. Auch für Lifts ist U keine allgemeine Untergrenze, sondern eine Schranke unter der Stärke-2-Voraussetzung an \(M(R)\).

### Baer-Gitter

In homogenen Koordinaten \((C:D:Z)\) ist die angegebene lineare Abbildung invertierbar, weil \(w_0\notin\mathbb F_n\epsilon\). Auf \(Z=0\) erzwingt das \(z=y=0\), also bleibt nur \((1:0:0)\), der Fernpunkt der Waagerechten. Der affine Teil hat auf \(d=0\) die \(c\)-Werte \(\epsilon^{-1}\mathbb F_n\); auf \(w\in w_0+\mathbb F_n\epsilon\) gilt \(cw\in\mathbb F_n\). Die fehlenden Parameter der Abbildung \(c\mapsto kc+rd+t\) sind:
- \(a\): \((\epsilon,w_0;k,r,t)=(1,i\omega;1,j\omega,i\omega)\);
- \(b\): \((\epsilon,w_0;k,r,t)=(\omega,i;\omega,j,i\omega)\).

Damit sind es tatsächlich affine Teile von Baer-Unterebenen. Jede projektive Gerade trifft die Unterebene: Ihre Gleichung auf den drei \(\mathbb F_n\)-Parametern hat höchstens zwei unabhängige \(\mathbb F_n\)-Bedingungen. Bei \(c+\alpha d=u\) kann der Treffer nicht der waagerechte Fernpunkt sein. Das funktioniert auch in Charakteristik \(2\), mit **jedem** \(\omega\notin\mathbb F_n\).

Die Vertreter decken alle Punkte ab. Für zwei Klassensymbole gibt es auf \(w=i'+i\omega\) genau einen gemeinsamen Punkt, weil zwei unabhängige Koordinaten von \(cw\) festgelegt werden. **Auf \(d=0\)** haben Klassen mit \(i=i'\) dagegen alle \(n\) Punkte gemeinsam, auch wenn dort das Paar nur für \(j=j'\) gesetzt wird. Auf den Achsen \(w_2=0\) bzw. \(w_1=0\) variiert in der vorhandenen Klasse gerade die Koordinate, die das Vollgeraden-Symbol der Gegenseite bestimmt. So erscheinen alle gemischten Paare. Zwei Vollgeraden-Symbole werden durch die zyklischen Verschiebungen auf \(d=0,\ c_2=0\) gepaart, **sofern** die Nummern von \(c\in\mathbb F_n\) modulo \(F\) alle Reste liefern. Eine feste Nummerierung \(0,\ldots,n-1\) des Unterkörpers genügt; beliebige Nummern des Oberkörpers genügen nicht automatisch.

Für \(F=0\) heißt „Füllsymbol“ ein **vorhandenes** Klassensymbol der jeweiligen Seite, kein neues Symbol. Dadurch kann sein tatsächlicher Symbolträger größer als die geometrische Baer-Klasse werden; kein Treffer geht verloren. Für \(F=n\) braucht man keinen Füller. Für \(n=2\) gibt es noch zwei Klassensymbole pro Seite und alle drei Fälle \(F=0,1,2\) funktionieren. Die Zählung stimmt: \(q(q-1)\) Vertreter außerhalb \(d=0\), dort \((q-n)(n+F)+n\max(F,1)\).

### Handrechnung

**\(q=4\), vollständig.** Ich habe \(\omega^2=\omega+1=\tau\) gewählt. \(a_j,b_j\) bezeichnen die Klassen \((1,j)\), \(A_j,B_j\) die Vollgeraden-Symbole. Die Einträge sind die Paare am jeweiligen Punkt:

| \(d\backslash c\) | \(0\) | \(1\) | \(\omega\) | \(\tau\) |
|---|---|---|---|---|
| \(1\) | \(A_0b_0\) | \(A_0b_1\) | \(A_1b_0\) | \(A_1b_1\) |
| \(\omega\) | \(a_0b_1\) | \(a_1b_0\) | \(a_0b_0\) | \(a_1b_1\) |
| \(\tau\) | \(a_1B_0\) | \(a_0B_0\) | \(a_0B_1\) | \(a_1B_1\) |

Fehlende Großbuchstaben ersetze ich für \(F=0\) durch \(a_0,b_0\), für \(F=1\) durch \(A_0,B_0\) der jeweiligen Seite. Auf \(d=0\) stehen bei \(c=\omega,\tau\) jeweils \(a_0b_0,a_1b_1\) und alle vorhandenen \(A_jB_j\). Bei \(c=0,1\) stehen für \(F=0\) je \(a_0b_0\), für \(F=1\) je \(A_0B_0\), für \(F=2\) die Diagonale bzw. die Gegendiagonale. Damit sind alle Punkte und Paararten ablesbar. Für die Geradentreffer habe ich \(c+\alpha d\) eingesetzt: \(d=0\) liefert jeder geometrischen Klasse \(\omega,\tau\). Für \(\alpha=0,1,\omega,\tau\) liefert \(d=\omega\) aus \(\{0,1\}\) bei \(a_0,a_1,b_0,b_1\) jeweils die Folgen \(0011,1100,1010,0101\); die jeweils andere Nichtnullzeile liefert die Komplementärfolge. Die Vollgeraden-Symbole treffen alle Geraden schon auf \(d=0\). Die Summen sind **\(12+4+2=18,\ 12+6+2=20,\ 12+8+4=24\)**.

**\(q=9\), zwei Klassen.** Mit \(\omega^2=2\) habe ich für \(a(1,0)\) bzw. \(b(2,0)\) diese \(c\)-Mengen ausgerechnet; „–“ bedeutet keine Punkte:

| \(d\) | \(a(1,0)\) | \(b(2,0)\) |
|---|---|---|
| \(0\) | \(\omega+\mathbb F_3\) | \(2\omega+\mathbb F_3\) |
| \(2\omega\) | \(0,\omega,2\omega\) | – |
| \(2+\omega\) | \(\omega,2+2\omega,1\) | – |
| \(1+\omega\) | \(\omega,1+2\omega,2\) | \(2\omega,2,1+\omega\) |
| \(2\) | – | \(0,\omega,2\omega\) |
| \(1+2\omega\) | – | \(2\omega,1,2+\omega\) |

Ihr gemeinsamer Punkt ist \((2,1+\omega)\), zu \(w=2+\omega\). Das ist keine vollständige \(q=9\)-Listenprüfung.

### Reichweite und Belege

- **§1:** Der erste Symbolzuwachs kostet \(q-n\), erst danach kostet jeder \(q\). Zwei Zähler sind laut §3.3 nur für \(q=4,9,16,25\) berichtet. Die Baer-Formel unterbietet \(7/5\) bei \(v=q\) für \(n\ge4\), nicht schon für \(n=2,3\). Der Faktor \(2\) gilt **asymptotisch** für die führenden Überschussterme. Das Verhältnis von Bauüberschuss zur reellen U′-Schranke für den Überschuss ist \(2(n+2)/(n+1)>2\); ein Grenzwert für den optimalen normierten Überschuss ist damit nicht bewiesen.
- **§§2.3, 4:** „Argument“ passt zu den allgemeinen Schlüssen, „gezählt“ nur zu den angegebenen Instanzen. „Exaktes Minimum“ ist für die offenen Fälle \(q=3,4\) als Zeilenüberschrift irreführend. „Dual-verifiziert“ ist nach dem berichteten Status nur bei zwei erfolgreichen Verifierläufen passend. Die \(t=5,6\)-Zahlen sind Vorhersagen **für nicht erzeugte Dateien**; die Zeilenzahl selbst folgt aus der Liftformel unter A/A′.
- **§5:** Die Primzahl-Überschläge begründen weder \(11/8\) noch \(1{,}2\) als Schranken; sie sind zu Recht als offen gekennzeichnet. Die \(q+q/s\)-Klassen für andere Potenzen sind in der Notiz nicht hergeleitet. Die Klassenexistenz ist separat begründbar: Für eine \(\mathbb F_s\)-Hyperebene \(W\subset\mathbb F_q\) und \(w_0\notin W\) nehme man \(c\in\mathbb F_s/w\) bei \(w\in w_0+W\), dazu auf \(d=0\) die Werte \(0\) und \(1/W^\times\). Für \(u\ne0\) trifft man bei \(u^{-1}\in W\) auf \(d=0\), sonst wegen \(uW+\mathbb F_s=\mathbb F_q\) außerhalb. Das belegt **kein** Gitter und keine Listenlänge \(1026\).

Ich habe kein Programm ausgeführt und keine gespeicherten Listen, Skripte, Arrays, Logs, externen Tabellen oder Originalquellen von Jamison (1977) und Brouwer–Schrijver (1978) gesehen. Geprüft sind die angegebenen Schlüsse und die ausgewiesenen Handrechnungen, nicht die berichteten Läufe, Bytevergleiche, Solverstatus oder Tabellenrekorde. Die Aussagen 1.1–1.5 des Hintergrunddokuments waren nicht Gegenstand der Prüfung.
