# Baselines (`baselines/`)

Dieses Verzeichnis enthält verifizierte Covering Arrays als Referenz für die Dual-Verifier-Testsuite (`verifiers/test_verifiers.py`) und als Ausgangsbasis für spätere Suchphasen.

| Datei | Parameter `CA(N; t, k, v)` | SHA-256 | Quelle & Lizenz |
| --- | --- | --- | --- |
| `CA_27_3_4_3.txt` | `CA(27; 3, 4, 3)` | `b9c441074a8c1bd148fbc96cda16cbdf7cbe35a9b81f1d734787261ea903f7b4` | Deterministisch erzeugtes orthogonales Array $\mathrm{OA}(27;3,4,3)$: $\{(a,b,c,(a+b+c)\bmod 3)\}$ |
| `CA_135_4_9_3.txt` | `CA(135; 4, 9, 3)` | `20d8a78665874780e0137321902ae14307a5d6210e896a725cfad40a8f0755e5` | `chrispbsmolen/ca-tools` (`table/arrays/CA_135_4_9_3.txt`, Commit `47596cf`, 2026-11-24; Christopher Smolen, CC BY 4.0) |
| `CA_185_3_10_5.txt` | `CA(185; 3, 10, 5)` | `9d0452533ece0fe428e93152acd87a04873792a4d0b718413ed8f661b43af33d` | `chrispbsmolen/ca-tools` (`table/arrays/CA_185_3_10_5.txt`, Commit `47596cf`, 2026-11-24; Christopher Smolen, CC BY 4.0) |
| `CA_361_3_9_6.txt` | `CA(361; 3, 9, 6)` | `4a09d2f4537cd5f92d505976a0ebe8e687fe1893a477310b3561d69df30784d3` | `chrispbsmolen/ca-tools` (`table/arrays/CA_361_3_9_6.txt`, Commit `47596cf`, 2026-11-24; Christopher Smolen, CC BY 4.0) |
| `CA_165_3_8_5.txt` | `CA(165; 3, 8, 5)` | `c96b7b1cc70530558a35fecc83df25105f2fad193801652c6716f13f39ba6295` | `dzoba/covering-arrays-2026` (`arrays/CA_165_3_8_5.txt`, Commit `3b536d6`, 2026-10-21; MIT License; Kommentar-Header für kanonisches Format entfernt) |

Alle drei `ca-tools`-SHA-256-Hashes wurden gegen `table/MANIFEST.csv` (Commit `47596cf`) abgeglichen und stimmen exakt überein. Der kanonische SHA-256-Hash von `CA_165_3_8_5.txt` stimmt exakt mit dem im Upstream-Kommentar-Header angegebenen Datenzeilen-Hash überein (Rohdatei-SHA-256 vor Header-Entfernung: `ecf99f95c8f82097ae1ed1842dbce4a84bd795d2ab8037cf04a4bb397fc36714`) und wurde mit beiden Verifiern geprüft.

