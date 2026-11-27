# Baer-Gitter mit r ausgelagerten Vollgeraden (Baer-v2)

- **Status / Belegart:** Informelles Argument und Prototyp-Check auf M(R) (q = 4, 9, 16, 25, 49). Erfinder: Gemini (Planerrolle); Implementierung: Antigravity; unabhängige Fremdprüfung / blinder Nachbau durch den Prüfer-Chat sowie Regel-2d-Prüfung stehen aus.
- **Kein Neuheitsanspruch:** Einordnung erfolgt nach Abschluss der Regel-2c-Prüfung durch den Prüfer-Chat.

## 1. Eingabe und Körperkonvention

Gegeben q = n^2 (n >= 2 Primzahlpotenz), F in {0, ..., n}, Alphabetgröße v = q - n + F sowie Parameter r in {0, ..., min(F, n - 1)}. Setze s := F - r >= 0.

1. **Endlicher Körper F_q:** Elementnummerierung 0, ..., q - 1 identisch zu `GeneralGF` in `scripts/gen_general_tqv.py`.
2. **Unterkörper & Ordnung:** F_n := { x in F_q : x^n = x } in aufsteigender Elementnummerierung Fn[0] < ... < Fn[n - 1] (stets Fn[0] = 0). Setze num(Fn[u]) := u, Fn_nz := Fn[1..n-1] und nz_idx(x) := num(x) - 1 in {0, ..., n - 2} für x in Fn_nz.
3. **Basiszerlegung:** om := min(F_q \ F_n). Jedes z in F_q schreibt sich eindeutig als z = z1 + z2 * om mit z1, z2 in F_n; setze p1(z) := z1, p2(z) := z2.
4. **Symbolnummerierung** (identisch für a und b, Werte 0, ..., v - 1):
   - K(i, j) := (num(i) - 1) * n + num(j) für i in Fn_nz, j in F_n   (q - n Baer-Symbole)
   - V_m     := q - n + m für m in {0, ..., F - 1}                  (F Vollgeraden-Symbole)
   - Fuell   := V_0 (= q - n) falls F >= 1, sonst 0.

## 2. Vertreterliste R (deterministische Reihenfolge: d = 0..q-1, darin c = 0..q-1)

### (B) Gerade d = 0
Für jedes c in F_q mit (c1, c2) = (p1(c), p2(c)) und t := num(c1) in {0, ..., n - 1}:

- **Fall c2 != 0:** Sei iota := nz_idx(c2) in {0, ..., n - 2}. Definiere die geordnete Liste L(iota):
  - falls iota < r:  L(iota) = [ V_m : m in {0, ..., F - 1} \ {iota} ]   (Länge s_loc = F - 1)
  - falls iota >= r: L(iota) = [ V_m : m in {r, ..., F - 1} ]            (Länge s_loc = F - r)
  (Stets gilt s_loc <= n.)
  - Für l = 0, ..., s_loc - 1 (mit k_l := K(c2, Fn[(t + l) mod n])):
    füge erst (c, 0, L[l], k_l) und dann (c, 0, k_l, L[l]) ein.
  - Für l = s_loc, ..., n - 1 (mit k_l := K(c2, Fn[(t + l) mod n])):
    füge (c, 0, k_l, k_l) ein.
  (Exakt n + s_loc Vertreter an diesem Punkt.)

- **Fall c2 = 0:**
  - Falls F = 0: ein Vertreter (c, 0, Fuell, Fuell).
  - Falls F >= 1 und s = 0 (also r = F):
    Ordne alle F^2 Paare (m_a, m_b) in {0, ..., F - 1}^2 mit Index idx = m_a * F + m_b dem Punkt t = idx mod n zu.
    Erhält Punkt t mindestens ein Paar, füge alle zugeordneten (c, 0, V_{m_a}, V_{m_b}) in aufsteigender idx-Reihenfolge ein; sonst einen Vertreter (c, 0, Fuell, Fuell).
  - Falls F >= 1 und s >= 1:
    - Ist t < F: füge für m = 0, ..., F - 1 die F Vertreter (c, 0, V_m, V_{(m + t) mod F}) ein.
    - Ist t >= F: füge für m = r, ..., F - 1 die s Vertreter (c, 0, V_m, V_m) ein.

### (A) Geraden d = 1..q-1
Setze w := 1 / d und (w1, w2) := (p1(w), p2(w)). Je c in F_q genau EIN Vertreter (c, d, a, b):

- **a-Spalte:**
  - Falls w2 != 0: a := K(w2, p2((c - w2 * om) * w)).
  - Falls w2 = 0 (iota1 := nz_idx(w1)):
    - falls iota1 < r: a := V_{iota1};
    - sonst sei m := num(p2(c * w)): a := V_m falls m < r, sonst Fuell.

- **b-Spalte:**
  - Falls w1 != 0: b := K(w1, p1((c - w1 * om) * w)).
  - Falls w1 = 0 (iota2 := nz_idx(w2)):
    - falls iota2 < r: b := V_{iota2};
    - sonst sei m := num(p1(c * w)): b := V_m falls m < r, sonst Fuell.

## 3. Zählformel und Sollwerte

|R(n, F, r)| = q*(q - 1) + (q - n)*(n + F) - n * r * (n - r) + max(n, F^2 + (n - F)*(F - r)).

- Für r = 0 identisch zu Baer-v1: q*(q - 1) + (q - n)*(n + F) + n*max(F, 1).
- Für v = q (F = n) ist r* = floor(n / 2) optimal:
  |R| = q^2 + 2*q*sqrt(q) - 2*q - sqrt(q) * floor(sqrt(q)/2) * ceil(sqrt(q)/2)
      = q^2 + (7/4)*q^(3/2) - 2*q + ((n mod 2)/4)*sqrt(q).

Sollwerte bei optimalem r*:
- q = 4  (F=0..2): 18 (r=0), 18 (r=1), 22 (r=1)
- q = 9  (F=0..3): 93 (r=0), 93 (r=1), 100 (r=2), 111 (r=1)
- q = 16 (F=0..4): 292 (r=0), 292 (r=1), 300 (r=2), 318 (r=2), 336 (r=2)
- q = 25 (F=0..5): 705 (r=0), 705 (r=1), 715 (r=2), 739 (r=3), 767 (r=3), 795 (r=2)
- q = 49 (F=0,3,7): 2653 (r=0), 2697 (r=3), 2905 (r=3)

## 4. Korrektheitsargument (gemischte Stärke 2 für M(R))

1. **Punktabdeckung:** Auf d != 0 exakt 1 Vertreter je Punkt; auf d = 0, c2 != 0 exakt n + s_loc >= n >= 1 Vertreter; auf d = 0, c2 = 0 in allen drei Fällen >= 1 Vertreter je Punkt.
2. **Geradentreffer (Inzidenz):**
   - Jede Klasse K(i, j) trägt auf d != 0 und d = 0 dieselbe Punktmenge wie in Baer-v1 (bei festem c2 = i durchläuft (t + l) mod n für l = 0..n-1 ganz {0..n-1}, sodass jedes K(i, j) an allen n Punkten (c1 + i*om, 0) einmal auf a- und einmal auf b-Seite erscheint).
   - Jedes V_m mit 0 <= m < r hat die volle waagerechte Gerade w = Fn_nz[m] (a-Seite) bzw. w = Fn_nz[m]*om (b-Seite).
   - Jedes V_m mit r <= m < F erscheint auf d = 0 an allen q Punkten (in jedem L(iota) für c2 != 0 sowie an allen t in {0..n-1} bei c2 = 0).
3. **Paarabdeckung (V^2):**
   - (K(i, j), K(i', j')): unverändert auf w = i' + i*om (w1, w2 != 0).
   - (V_m, K(i', j')) mit iota' = nz_idx(i'):
     - iota' = m (m < r): auf der vollen Geraden w = i' (a = V_m konstant, b durchläuft alle K(i', j')).
     - m < r und iota' >= r: auf w = i' (w2 = 0) ist c -> (p1((c - i'*om)*w), p2(c*w)) bijektiv von F_q auf F_n^2, also trifft a = V_m jedes b = K(i', j') einmal.
     - Übrige Fälle (iota' < r mit iota' != m, oder m >= r mit beliebigem iota'): genau dann gilt V_m in L(iota'); über t = 0..n-1 durchläuft (t + l) mod n alle j' in F_n, sodass (V_m, K(i', j')) auf d = 0, c2 = i' entsteht.
   - (K(i, j), V_m): symmetrisch über w1 = 0 und (c, 0, k_l, L[l]) auf d = 0.
   - (V_m, V_{m'}): alle F^2 Paare auf d = 0, c2 = 0 (für s = 0 explizit verteilt, für s >= 1 über (m, (m + t) mod F) für t = 0..F-1 <= n-1).
