# Die zwei kleinsten Logikschaltungen, die sich nicht als Formel formalisieren lassen

**Die beiden SR-Latches (auch RS-Flipflops genannt)** – einmal aus zwei NOR-Gattern und einmal aus zwei NAND-Gattern.

## Erklärung

Alle **kombinatorischen** Logikschaltungen lassen sich problemlos als boolesche Formel formalisieren.

Die beiden **kleinsten sequentiellen** Logikschaltungen hingegen **nicht**:

### 1. NOR-basiertes SR-Latch (zwei kreuzgekoppelte NOR-Gatter)
Der Ausgang \( Q \) hängt nicht nur von den aktuellen Eingängen \( S \) und \( R \) ab, sondern auch vom vorherigen Zustand durch die Feedback-Schleife. Es existiert keine statische boolesche Formel \( Q = f(S, R) \).

### 2. NAND-basiertes SR-Latch (zwei kreuzgekoppelte NAND-Gatter)
Genau dasselbe Problem: Speicherverhalten durch Rückkopplung – keine reine Formel ohne Zeit- bzw. Zustandsabhängigkeit.

Diese beiden Schaltungen sind die klassischen kleinsten Beispiele in der Digitaltechnik, die nicht mehr rein kombinatorisch (also als einfache Formel) beschrieben werden können.
