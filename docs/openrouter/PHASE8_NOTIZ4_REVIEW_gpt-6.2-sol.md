> **OpenRouter-Antwort**
>
> - Modell: openai/gpt-6.2-sol
> - Betreiber: OpenAI (laut OpenRouter)
> - Datum: 28.11.2026, 11:44
> - Tokens: Eingabe 34.553 · Ausgabe 7.576 (davon Denken 4.435) · gesamt 42.129
> - Kosten laut OpenRouter: 0,16 US-$
> - Datenregel: kein Training (data_collection: deny)
> - Denkstufe: high
> - finish_reason: stop
> - Eingelesen: docs/openrouter/PHASE8_NOTIZ4_AUFTRAG.md (3.050 Zeichen), docs/phase8/NOTIZ_4_UNTERGRENZEN_C1_C2.md (20.698 Zeichen), docs/phase8/NOTIZ_3_UNTERGRENZE_BAER.md (25.998 Zeichen), docs/PHASE8_ARGUMENTE.md (36.242 Zeichen)

---

| Stelle | Urteil | Befund |
|---|---|---|
| §1: Blokhuis, Bruen, Lemma J | **korrekt** | Die Voraussetzungen gelten für die **Punktträger**, nicht für die Vertreter als Multimengen. |
| C.1 §2.2, Zuordnung und Schritte 1–3 | **korrekt** | Eine volle Waagerechte je Symbol wird **ausgewählt**; weitere sind erlaubt. Die Schranken für die Klassengrößen, den Zeilenüberhang und \(S\) stimmen. |
| C.1 §2.2, Schritte 4–6 | **korrekt** | Paarzeugen, Inklusion–Exklusion und die Kopplung über gemiedene Waagerechte sind korrekt bilanziert. |
| C.1 §2.3 | **korrekt mit Lücke** | Der Ersatz von \(S/p^2\) durch \(uv\) ist nicht punktweise in der behaupteten Richtung zulässig. Zwei angebliche Minima sind nur Unterabschätzungen über erweiterte Bereiche. Beides ist reparierbar. |
| C.2 §3.2, Schritte 1–3 | **korrekt** | Vielfachheitsüberhang, Bruen und beide Varianten der Kopplung ergeben die angegebene endliche Schranke. |
| C.2 §3.3 | **korrekt mit Lücke** | Der symmetrische Ansatz liefert keinen Beweis für das globale Minimum. Die fehlende Abschätzung für unsymmetrische Parameter folgt aber aus \(e_Y\). |
| **Gesamt C.1** | **trägt mit Lücke** | Die endliche Schranke trägt; die asymptotische Herleitung braucht die unten angegebene Präzisierung. |
| **Gesamt C.2** | **trägt mit Lücke** | Die endliche Schranke trägt; der asymptotische Untergrenzenbeweis fehlt in der Notiz und wird unten ergänzt. |

### Voraussetzungen und Zählungen

**Geometrie.** \(A\cup\{P_\infty\}\) blockiert die projektive Ebene und kann eine projektive Gerade nur dann enthalten, wenn \(A\) eine volle Waagerechte enthält. Damit sind Blokhuis für ungerade Primzahlen und Bruen für die betrachteten Quadratordnungen anwendbar. Die zusätzliche Falltrennung nach einer vollen *nicht*-waagerechten affinen Geraden ist unnötig, aber korrekt: Ihre \(q-1\) Parallelen erfordern \(q-1\) weitere Punkte. Lemma J folgt direkt wie in Notiz 3: Die Ergänzung um je einen Punkt auf jeder gemiedenen Waagerechten ergibt eine affine blockierende **Menge**; erst darauf wird Jamison/Brouwer–Schrijver angewandt. Für Vertreterzahlen gilt anschließend \(|R_s|\ge |A_s|\) bzw. \(|R_s|\ge |B_s|\).

**C.1, Schritte 1–6.**

1. Die Klassen partitionieren die Vertreter auf jeder Seite für sich; die Blokhuis-Summe stimmt.
2. Die \(\alpha_d\) verschiedenen Symbole benötigen an jedem Punkt \(\alpha_d\) Vertreter. Auf den übrigen Waagerechten gilt Punktabdeckung. Die beiden Seiten werden nicht addiert; man nimmt das Maximum.
3. Die Fälle \(t_{11}=0\) und \(t_{11}>0\) sind vollständig. Für den zweiten gilt \(\sum x_dy_d\le UV\). \(S\) muss nicht erreichbar sein: Als Obergrenze hat es die richtige Richtung.
4. Ein Paar mit verschiedenen zugeordneten Waagerechten liefert mindestens einen Extrabeitrag. Verschiedene Paare haben verschiedene Zeugen. Ein Zeuge darf in **beiden** Extrasummen stehen: Abgeschätzt wird \(\Delta_A+\Delta_B\), nicht die Größe ihrer Vereinigung.
5. Bei der Inklusion–Exklusion ist \(X_d\) genau der abzuziehende Schnitt. Die Paarabdeckung liefert \(x_a-\beta_d\le\delta_a\); jedes \(a\) wird dabei nur auf seiner **einen zugeordneten** Waagerechten summiert. Danach werden \( |R|+\Delta_A\) und \( |R|-\Delta_A\) addiert, nicht zwei angeblich disjunkte Vertreterbestände.
6. Verschiedene gemiedene Waagerechte liefern verschiedene gewählte \(b_d\). Ihre Paarzeugen liegen außerhalb der jeweiligen Basiswaagerechten und zählen in \(\Delta_B^{(N)}\), getrennt von den in der Schwer–Schwer-Rechnung verwendeten \(\Delta_B^{(H)}\). Lemma J gibt die behauptete Klassenschranke auch hier; der leere Randfall ist trivial.

**C.2, Schritte 1–3.** Schritt 1 ist dieselbe einseitige Zeilenzählung wie in C.1; Schritt 2 summiert die Bruen-Überschüsse korrekt. In Schritt 3 sind die \(a_d\) verschieden. Daher gehören die Zeugen für die gemiedenen Waagerechten zu verschiedenen Paaren und zählen jeweils außerhalb der Basis in \(\Delta_A\). Bei der gemischten Summe wird Lemma J für die vollen \(b\)-Klassen und Bruen für die übrigen verwendet; nur die dort benötigten \(r_b\) werden durch \(\Delta_A\) nach oben abgeschätzt. Die beiden Varianten für \(c_{2X}\) werden **maximiert**, nicht addiert. Die Addition mit (3) eliminiert \(\Delta_A\) korrekt; die Gegenseite ist symmetrisch.

Damit brauchen beide endlichen Beweise weder ein bestimmtes Skelett noch eine einzige schwere Gerade noch bestimmte Klassenformen. Auch Multiplizitäten sind zulässig. Alle Aufrundungen erfolgen erst aus einer unteren Schranke für eine ganzzahlige Vertreterzahl bzw. einen ganzzahligen Überschuss.

### Handrechnung und Unterbietungsversuch

Ich habe die angegebenen Parameterzeugen eingesetzt und jeweils die nächstkleinere ganze Zahl **für alle zulässigen Parameter** ausgeschlossen. Das ist keine Listensuche.

| Fall | Parameterzeuge aus der Notiz | Von Hand eingesetztes Maximum | Minimum der Formel |
|---|---|---|---:|
| \(p=3\) | \((3,3,0,0,3)\) | \(e_{3a}=e_4=12\) | **12** |
| \(p=5\) | \((4,4,1,1,1)\) | \(e_4=e_{5a}=34\) | **34** |
| \(p=7\) | \((5,5,2,2,1)\) | \(e_{3a}=66\) | **66** |
| \(q=4\) | \((2,2,1,1)\) | \(E=4\) | **20** |
| \(q=9\) | \((3,3,1,1)\) | \(E=18\) | **99** |

**Ausschluss für C.1.** Setze \(a=h_a,\ b=h_b,\ z=UV\). Für eine Unterbietung mit Maximum \(\le N\) muss wegen \(S\le z+F\) gelten
\[
(p-1)F\le 2N-p^2-e_1+z,\qquad
S\ge e_1+e_2+ab-2N.
\]
- **\(p=3,\ N=11\):** \(e_1,e_6\) erzwingen \(a\ge2\), \(U=V=0\). Dann gilt \(a+b-3\le t_{11}\le a-1\), also \(a=b=2,\ t_{11}=1\). Aber \(e_4=13\).
- **\(p=5,\ N=33\):** \(a\ge3,\ z\le1\). Erforderlich ist \(S\ge5+(a-3)(b-3)\), möglich höchstens \(S\le1+\lfloor(2+3a)/4\rfloor\). Für \(a=3,4,5\) sind die oberen Werte \(3,4,5\), die unteren mindestens \(5,5,9\).
- **\(p=7,\ N=65\):** \(a\ge3,\ U,V\le2\). Erforderlich ist \(S\ge8+(a-4)(b-4)\), und \(6F\le4+4a+z\). Für \(a=5,6,7\) ist die untere Schranke mindestens \(9,12,17\), die obere \(z+F\) höchstens \(8,9,10\). Für \(a=4\) erfordert \(S\ge8\) den Wert \(z=4\); dann ist \(U+V=4\) und \(F\le4\), also \(t_{11}=0\) und \(S=0\). Für \(a=3\) braucht man \(S\ge5\), aber \(F\le3\). Also müsste \(t_{11}\ge1\) und damit \(U+V\le2,\ z\le1\) sein. Das verschärft \(F\le2\) und ergibt \(S\le3\).

**Ausschluss für C.2.** Für \(E<qn-q\) erzwingen \(c_{1X}\) und der Überhang \(k_A\ge n+1\) und \(h_B-1\ge k_B-n+1\). Einsetzen des ersten Terms von \(c_{2Y}\) gibt, mit \(k_B\ge k_A\),
\[
2E\ge 2qn+k_A^2-(3n-1)k_A.
\]
Für \(n=2,\ k_A\ge3\) ist die rechte Seite mindestens \(10\); für \(n=3,\ k_A\ge4\) mindestens \(38\). Das schließt \(E<4\) bzw. \(E<18\) aus.

Eine Belegung **aller** Beweisungleichungen unter den endlichen Formelschranken ist damit ausgeschlossen: Schon ihre Konsequenzen im jeweiligen Maximum widersprechen der Unterbietung, unabhängig von der Verteilung der \(M_d\). Die Parameterzeugen sind aber keine Listenzeugen.

**Das Modellminimum \(12\) für \(p=3\)** folgt nicht allein aus der Untergrenze, lässt sich aber ohne Suche beweisen. Auf jeder Waagerechten \(d\in\mathbb F_3\) setze an \(c=1,2\) je das Symbolpaar \((d,d)\), an \(c=0\) die beiden Paare \((d,d+1),(d+1,d)\), modulo \(3\). Das sind zwölf Vertreter, alle Punkte und alle neun Paare sind abgedeckt, und jedes Symbol hat auf beiden Seiten seine volle Waagerechte. Notiz 3 berichtet für \(p=3\) dagegen nur einen Fund, keinen abgeschlossenen Optimalitätsnachweis durch CP-SAT.

### Asymptotik

**C.1.** Für endliches \(p\) kann \(S>UV\) sein; dann würde der wörtliche Ersatz durch \(UV\) die Ausdrücke mit \(-S\) **erhöhen**. Richtig ist die uniforme Abschätzung \(S\le UV+F=UV+O(p)\). In \(e_{3a}\) kann man zudem den nichtnegativen Beitrag \(pt_{11}\) weglassen. So erhält man die angegebenen \(f\)-Ausdrücke als Unterabschätzungen bis auf \(O(1/p)\), ohne \(t_{11}/p\to0\) für beliebige Listen vorauszusetzen.

Die Konvexkombination und die Fallgrenzen stimmen. Für \(\alpha\le11/34\) reicht \(f_1\). Für \(11/34<\alpha\le1/2\) sind die verwendeten Minima tatsächlich zulässig: \(\beta=v+1/2\) bei \(v\le1/2\), sonst \(\beta=1,\alpha=1/2\). Für \(\alpha>1/2\) sind \(\beta=v+1/2\) bzw. \(\beta=\alpha\) nicht immer zulässig, liefern durch Monotonie aber weiterhin **untere** Vergleichswerte. Die quadratische Abschätzung im letzten Fall stimmt. Damit folgt \(|R|\ge(91/68)p^2-O(p)\).

**C.2.** Der symmetrische Ansatz allein zeigt nur, was ein Parameterzeuge erreichen kann. Für das globale Minimum sei \(E\) das Maximum der endlichen Formel. Falls \(E\ge qn\) oder \(k_A<n\), reicht der Überhang bzw. \(c_{1X}\) bereits. Sonst folgt aus der Ganzzahligkeit \(h_B-1\ge k_B-n\). Wieder liefert \(e_Y\)
\[
2E\ge 2qn+(k_A-n)k_B-2nk_A
\ge 2qn+k_A^2-3nk_A
\ge 2qn-\tfrac94n^2 .
\]
Das beweist sogar \(|R|\ge q^2+q^{3/2}-\tfrac98q\) ohne Fehlerterm. Umgekehrt ergibt der symmetrische **Parameterzeuge** \(k_A=k_B\) nahe \(3n/2\), \(h_A=h_B=k_A-n+2\), den Wert \(qn-\tfrac98q+O(n)\) für \(E\). Damit stimmt der Koeffizient auch für das Minimum der Formel, nicht notwendig für das Listenoptimum.

**Beleggrenzen.** „Exakt“ ist für die ganzzahlige Auswertung der jeweiligen Formel angemessen, nicht als Synonym für ein Modelloptimum. Bei \(p=5\) folgt „scharf“ aus der Untergrenze **und** der Gültigkeit der berichteten 34er-Liste; Letztere habe ich nicht geprüft. Ich habe kein Programm ausgeführt und weder Repository-Listen noch Skripte noch Originalquellen gesehen. Die gemeldeten Suchläufe, Listenprüfungen, übrigen Tabellenwerte und exakten Literaturzuordnungen sind daher nicht unabhängig überprüft.
