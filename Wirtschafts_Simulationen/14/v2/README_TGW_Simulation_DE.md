# TGW-PyPy3-Simulation: Topologische Gruppenwirtschaft

Diese Simulation setzt das diskutierte Wirtschaftssystem als lauffähiges, umfangreiches PyPy3-kompatibles Modell um. Es ist keine Prognosemaschine und keine magische Ökonomie, sondern ein experimentelles Simulationslabor für die Idee:

\[
\text{Währung} = \text{Stack aus Topologie + additiver Gruppe}
\]

Die einzige Währung heißt **LZ** (*Lösungszahl*). Konten können positiv oder negativ werden. Positive LZ entstehen durch Problemlösung, negative LZ durch Problemverursachung, Betrug, Krieg, Externalitäten, Vertragsbruch oder ungelöste Verpflichtungen.

## Dateien

- `tgw_pypy3_simulation.py` — Hauptsimulation, nur Python-Standardbibliothek, PyPy3-kompatibel.
- `README_TGW_Simulation_DE.md` — diese Anleitung.
- `run_examples.sh` — Beispielbefehle.
- `tgw_sample_report.txt` — Beispielbericht eines 80-Tick-Laufs.
- `tgw_sample_timeseries.csv` — Beispiel-Zeitreihe.
- `tgw_sample_final.json` — Beispiel-Endzustand.
- `tgw_conflict_sample_report.txt` — Beispiel für ein Konfliktszenario mit heißen Konflikten.

## Ausführen

```bash
pypy3 tgw_pypy3_simulation.py --ticks 250 --seed 42 --report-every 25
```

Falls PyPy3 nicht installiert ist, läuft das Skript auch mit normalem Python 3:

```bash
python3 tgw_pypy3_simulation.py --ticks 250 --seed 42
```

## Beispiel mit CSV- und JSON-Ausgabe

```bash
pypy3 tgw_pypy3_simulation.py \
  --scenario baseline \
  --ticks 200 \
  --seed 7 \
  --csv-out tgw_timeseries.csv \
  --json-out tgw_final.json
```

## Szenarien

```bash
pypy3 tgw_pypy3_simulation.py --scenario baseline
pypy3 tgw_pypy3_simulation.py --scenario conflict
pypy3 tgw_pypy3_simulation.py --scenario fraud
pypy3 tgw_pypy3_simulation.py --scenario intergalactic
pypy3 tgw_pypy3_simulation.py --scenario scarcity
```

- `baseline`: normale Wirtschaft mit Problemen, Märkten, Banken, Steuern, Audits.
- `conflict`: mehr geopolitische Spannung, kalte Konfliktkosten und heiße Konfliktschäden.
- `fraud`: höherer Betrugsdruck und mehr Korrekturbuchungen.
- `intergalactic`: mehr Remote-Projekte über Galaxien mit Escrow und Verzögerung.
- `scarcity`: mehr Anfangsprobleme und mehr Externalitäten.

## Mathematischer Kern im Code

### 1. Gruppe

Die Währung ist die additive Gruppe reeller Zahlen:

\[
G = (\mathbb{R}, +, 0, -)
\]

Im Code wird sie durch `float` repräsentiert. Jede Zahlung ist Gruppenaddition:

\[
B(A) := B(A)-x
\]

\[
B(B) := B(B)+x
\]

Die Summe aller Konten bleibt dadurch nahe 0. Kleine Abweichungen kommen nur von Gleitkommaarithmetik.

### 2. Topologie

Problem- und Lösungskontexte sind offene Mengen von Domänen-Tags, zum Beispiel:

```text
{energy, infrastructure, industry}
{water, health, environment}
{security, governance, diplomacy}
```

Kompatibilität entsteht durch Schnittmengen oder Nachbarschaft in der Topologie. Eine Lösung passt gut zu einem Problem, wenn ihre offenen Mengen überlappen.

### 3. Stack

Ein Stack besteht aus Schichten:

\[
S = ((U_1,g_1),(U_2,g_2),...,(U_n,g_n))
\]

Dabei ist `U_i` ein offener Bereich und `g_i` ein Gruppenwert in LZ.

Der Zahlenwert ist:

\[
Z(S)=\sum_i g_i
\]

Der Anwendungsbereich ist:

\[
D(S)=\bigcap_i U_i
\]

Fusion zweier Stacks:

\[
Z(S\oplus T)=Z(S)+Z(T)
\]

\[
D(S\oplus T)=D(S)\cap D(T)
\]

## Simulierte Akteure

Die Simulation enthält:

- Haushalte / Arbeitnehmer
- Unternehmen / Arbeitgeber
- Banken
- Staaten / Länder
- lokale Reparaturfonds
- Auditoren / Prüfer
- intergalaktisches Escrow
- universelles Clearinghouse

Alles wird in **einer einzigen Währung, LZ**, bilanziert.

## Simulierte Märkte

Die Simulation enthält mehrere Märkte, aber keine zweite Währung:

1. **Arbeitsmarkt**  
   Unternehmen stellen Haushalte ein und zahlen Löhne in LZ.

2. **Konsum-/Gütermarkt**  
   Haushalte kaufen Güter und Dienstleistungen von Unternehmen.

3. **Problemlösungsmarkt**  
   Staaten, Fonds oder geschädigte Systeme schreiben Probleme aus. Unternehmen lösen sie gegen LZ.

4. **Kreditmarkt**  
   Banken vergeben Kredite. Die Bank kann dabei selbst negativ werden; das bleibt als Gruppenbilanz sichtbar.

5. **Steuern und öffentliche Ausgaben**  
   Staaten erheben Steuern und finanzieren öffentliche Problemlösung.

6. **Auditmarkt**  
   Prüfer kontrollieren Projekte. Betrug oder Unterleistung erzeugt inverse/negative Buchungen.

7. **Konfliktmarkt**  
   Kalte Konflikte und heiße Konflikte erzeugen negative Stacks. Diplomatie- und Sicherheitslösungen können Spannungen reduzieren.

8. **Intergalaktischer Markt**  
   Remote-Projekte zwischen Galaxien verwenden Escrow und Verzögerung. Es gibt keine magische Echtzeit-Finalität.

## Wichtige Mechaniken

### Problemformalisierung

Wenn ein Problem entsteht oder formal anerkannt wird, wird der Verursacher oder Eigentümer negativ belastet, und ein Reparaturfonds erhält positive LZ, um Lösung zu finanzieren.

Beispiel:

```text
Firma verursacht Umweltschaden: -500 LZ
Lokaler Reparaturfonds erhält: +500 LZ
Problem bleibt offen, bis es gelöst wird.
```

### Problemlösung

Ein Unternehmen kann ein Problem teilweise oder vollständig lösen. Dann erhält es eine Zahlung aus dem Reparaturfonds oder Escrow. Die Problemschwere sinkt.

### Betrug

Ein Unternehmen kann behaupten, mehr gelöst zu haben als tatsächlich geschehen ist. Audits können das entdecken. Dann wird eine inverse Buchung erzeugt:

```text
Falsche Lösung: +500 LZ erhalten
Audit-Korrektur: -500 LZ oder mehr
```

Die Historie wird nicht gelöscht, sondern korrigiert.

### Krieg und Konflikt

Im Konfliktszenario erzeugt Krieg massive negative Stacks:

- Schäden an Infrastruktur
- Gesundheits- und Sicherheitsprobleme
- eigene Kriegskosten
- Reparaturfonds beim Geschädigten
- negative Reputation beim Verursacher

Dadurch wird sichtbar: Beute oder Machtgewinn verschwindet nicht aus der Bilanz, weil Schaden als negative LZ erscheint.

### Intergalaktische Verzögerung

Transaktionen zwischen Galaxien verwenden Verzögerungen:

```text
Dauer = Projektdauer + Galaxienabstand * intergalactic_delay
```

Remote-Zahlungen werden in Escrow gesperrt und später freigegeben.

## Konsolenausgabe lesen

Eine typische Zeile:

```text
t=  80 | actors= 430 neg=  1 | openP= 256 sev= -56.92k LZ | projects= 41 solved=+212.39k LZ damage=-269.33k LZ | fraud= 86 war= 0 | unemp=  0 | Σbal=-0.000000
```

Bedeutung:

- `actors`: Anzahl aller Akteure
- `neg`: Akteure mit negativem Kontostand
- `openP`: offene Probleme
- `sev`: aktuelle negative Problemschwere
- `projects`: aktive Problemlösungsprojekte
- `solved`: kumulierter positiver Lösungswert
- `damage`: kumulierter negativer Problem-/Schadenswert
- `fraud`: entdeckte Betrugsfälle
- `war`: heiße Konfliktereignisse
- `unemp`: arbeitslose Haushalte
- `Σbal`: Summe aller Konten; sollte nahe 0 bleiben

## Wichtige Parameter

```bash
--ticks                         Anzahl Simulationsschritte
--seed                          Zufallsseed
--scenario                      baseline, conflict, fraud, intergalactic, scarcity
--galaxies                      Anzahl Galaxien
--planets-per-galaxy            Planeten je Galaxie
--states-per-planet             Staaten/Länder je Planet
--households                    Haushalte/Arbeitnehmer
--firms                         Unternehmen
--initial-problems-per-state    Startprobleme je Staat
--max-projects-started-per-tick Neue Problemlösungsprojekte je Tick
--max-active-projects           Parallele Projekte
--intergalactic-delay           Verzögerung zwischen Galaxien
--war-probability               Basiswahrscheinlichkeit heißer Konflikte
--fraud-pressure                Betrugsdruck
--externality-rate              Häufigkeit externer Schäden
--credit-leverage               Wie weit Banken negativ gehen dürfen
--csv-out                       Zeitreihe exportieren
--json-out                      Endzustand exportieren
--quiet                         Keine Konsolenausgabe
```

## Konkrete Beispielbefehle

### 1. Kompakter Testlauf

```bash
pypy3 tgw_pypy3_simulation.py --ticks 50 --seed 1 --households 80 --firms 20
```

### 2. Konfliktmodell

```bash
pypy3 tgw_pypy3_simulation.py \
  --scenario conflict \
  --ticks 120 \
  --war-probability 0.03 \
  --report-every 20
```

### 3. Intergalaktischer Handel

```bash
pypy3 tgw_pypy3_simulation.py \
  --scenario intergalactic \
  --galaxies 5 \
  --ticks 250 \
  --remote-project-probability 0.25 \
  --intergalactic-delay 25
```

### 4. Betrugstest

```bash
pypy3 tgw_pypy3_simulation.py \
  --scenario fraud \
  --ticks 200 \
  --fraud-pressure 2.5 \
  --json-out fraud_final.json
```

## Grenzen des Modells

Diese Simulation ist bewusst ein Modell, kein realer Wirtschaftsplan. Sie vereinfacht stark:

- Topologie wird als endliche Tag-Struktur abgebildet.
- Die additive Gruppe wird numerisch als `float` simuliert.
- Preise entstehen heuristisch, nicht durch echte Auktionen.
- Audits sind probabilistisch.
- Kriegsschäden sind abstrakte LZ-Schäden, keine realen Opfermodelle.
- Intergalaktische Physik wird nur durch Verzögerung und Escrow angenähert.

Der wichtigste Zweck ist, die Systemidee testbar zu machen:

> Wer Probleme löst, wird positiv. Wer Probleme erzeugt, wird negativ. Wer beides tut, wird ehrlich bilanziert.
