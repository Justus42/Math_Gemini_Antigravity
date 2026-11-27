# Übergabe des Phase-8-Chats (Claude), 2026-11-27, 06:14 MEZ

Für den nächsten Claude-Chat, der Phase 8 weiterführt. Erst lesen: `RULES.md`, `AGENTS.md`, `STATUS.md`,
`docs/UEBERGABE_PRUEFER_CHAT_2026-11-27.md` (Abschnitt 4, Regeln von Justus), dann `docs/PHASE8_UEBERSICHT.md`.

## 1. Rolle

Du übernimmst die **Erzeugerrolle** für Phase 8 (Bauart entwickelt, Listen gebaut). Du bist damit **nicht** ihr Prüfer.
Ein Prüfer-Chat für Phase 8 fehlt noch. Gemini plant und liest, Antigravity rechnet und baut nach; beider Aussagen
werden nachgeprüft, bevor sie in eine Antwort oder ins Repo gehen. Ein „Go“ von Gemini ist keine Freigabe von Justus.

## 2. Stand im Repo

- `main @ 11b79a8`: PR `#40` und PR `#41` sind gemergt (`#41` am 27.11., 06:07 MEZ); `#41` enthielt den Nachbau von
  Antigravity (PR `#42`) per Merge-Commit. Diese Übergabe kommt mit einem eigenen kleinen Pull Request nach.
- `chrispbsmolen/ca-tools @ 697325b`: die `37` Zeilen aus PR `#91` stehen in `table/ca_frame.csv`.
  Nach außen ist alles gesperrt, bis Justus in eigenen Worten freigibt. Nächste Meldung nur einmal und erst,
  wenn sie nicht absehbar von uns selbst überholt wird.

## 3. Was vorliegt (Belegart in Klammern)

- **Dichotomie:** Jede Symbolklasse enthält eine volle Gerade `d = const` oder hat mindestens `q + sqrt(q)` Punkte
  (Argument, zitierte Sätze; `docs/PHASE8_ARGUMENTE.md` 1.1).
- **Klassen-Regel** für ungerade Primzahlpotenzen mit gemeinsamem Punkt `O` (Argument 1.2; gerechnet für die Primzahlen
  `11` bis `43` und über gebaute Listen für `q = 9, 25, 27`).
- **Zählformel** `|R| = q(v + x_b) - G + (n - 1)`, Bedingung `x_b <= min(v - 1, q - 1)` (Argument 1.3; trifft alle
  gebauten Regel-Listen). Formel (a) und Leitkonstante `7/5` in diesem Skelett mit diesen Klassen (Argument 1.4).
  Vollgeraden-Untergrenze `q^2 + C(q, 2)` (Argument 1.5).
- **Lesung durch `openai/gpt-6.2-sol`** am 27.11., 06:03 MEZ: kein Fehler gemeldet, fünf Präzisierungen offen
  (im Dokument vermerkt, nicht eingearbeitet). Das ist kein formaler Beweis.
- **Drei Stufen:** (a) geschlossene Formel, (b) Regel mit gezähltem `j`, `n`, `S`, (c) Löserlisten. Im Tabellenbereich
  ist (c) am kleinsten; Optimalität ist nirgends gezeigt.
- **Löserlisten** `data/phase8/` (`v = q`): `q = 9`: `113`; `11`: `170`; `13`: `238`; `17`: `412`; `19`: `513`;
  `23`: `746`; `29`: `1190`; `31`: `1356`; `37`: `1942`; `(23, 22)`: `722` (`M(R)` gerechnet; Arrays `t = 3, 4` in
  `results/phase8/` dual-verifiziert, siehe `results/phase8/VERIFICATION_LOG_phase8.md`).
- **Regel-Listen** `data/phase8_repro/` (Skript von Antigravity, ohne Löser): `116, 172, 520, 516, 768, 746, 828` und
  für Primzahlpotenzen `792, 863, 888, 930, 968` (`M(R)` gerechnet, `t = 3` dual-verifiziert, `t >= 4` nicht).
- **Gegen die Tabelle `697325b`:** kleiner sind `(3, 11, 9)` `1017`, `(3, 13, 11)` `1870`, `(3, 21, 19)` `9747`
  (dual-verifiziert) und als Vorhersage `(4, 27, 22)`, `(4, 27, 23)`, `(4, 29, 24)`, `(4, 29, 25)` aus Regel-Listen.

## 4. Offen

1. Untergrenze im Modell `M(R)`, wenn Klassen ohne volle Gerade erlaubt sind. Ist `7/5` das Ende? Andere Skelette
   (mehrere Punkte `O`, verschobene Klassen, unsymmetrische Steigungspaare, Baer-Unterebenen bei Quadraten).
2. Löserlisten für `q = 25, 27`; gerade `q`; `v < q` planmäßig.
3. Fünf Präzisierungen aus der Lesung einarbeiten, danach neu lesen lassen (nur mit Freigabe von Justus, kostet Guthaben).
4. Literaturprüfung mit Prüfvermerk (Regel 2c): CKRS im Original, Begleitarbeit von Bai, Volltexte auf Zenodo sind ungelesen.
   Bisher kein Fund, der Covering Arrays mit Rédei-Mengen verbindet; das ist kein Beleg für Neuheit.
5. Vor jeder Meldung: Regel 2a bis 2e, dual-verifizierte Arrays auch für `t = 5, 6`, offene Pull Requests des Ziels.

## 5. Verworfen oder schwächer (nicht wiederholen)

- Kern mit einer oder keiner Nullspalte und polynomialen Vertretern: schlechter (`q = 5`: `40/42` gegen `34`).
- Baer-Klassen können nicht `q - sqrt(q)` Punkte streichen; die Klasse muss an `h_b` schweren Punkten bleiben.
- `v < q` hilft nicht überall: bei `q = 23` nur `v = 22, 21`; bei `q = 25` erst ab `v = 22`, bei `q = 27` ab `v = 24`.
- Formel (a) ist im linearen Term nicht das Beste der Regel: weniger Klassen können günstiger sein (`q = 37`: `1942`
  mit `n = 13` gegen `1944` mit `n = 15`).
- CP-SAT beweist hier keine Optima; alle Läufe sind Heuristik mit Zeitgrenze.

## 6. Handwerk

- Skripte: `scripts/phase8/` (`README.md` dort), `scripts/phase8_spec_repro.py`, `scripts/phase7_lift.py`,
  `scripts/pruefer/tabelle.py` (Tabellenpfad als erstes Argument, mit `/` am Ende).
- Verifier bauen: `gcc -O3 -march=native -pthread -o verifiers/ca_verify verifiers/ca_verify.c -lm`; `verifiers/` nie ändern.
- Pull Requests über `gh api` (REST); Push mit `git -c push.negotiate=true push`. Eigene Änderungen nur auf einem Branch.
- Push-Recht und jeder Bridge-Aufruf brauchen eine neue Freigabe von Justus in seinen Worten.
- Justus liest am Handy und ist kein Programmierer: Deutsch, du, kurz, Ergebnis zuerst, Widerspruch statt Bestätigung,
  keine Befehle für ihn, Uhrzeiten in deutscher Zeit (vorher mit `date` prüfen), am Ende der `HANDOVER`-Block.
- Wortwahl: „kleiner als die Tabelle am Commit X“; kein „neu“, kein „Rekord“, kein Neuheitsanspruch.
