# Die Schleife (Rückkopplung) in sequentieller Logik – Was sie alles ermöglicht

**Die Gemeinsamkeit ist die Schleife (Rückkopplung / Feedback).**  
Damit kann man nicht nur **speichern, zählen und schalten**, sondern noch viel mehr.  
Statt reiner **Formeln** entstehen echte **Algorithmen** in Hardware.

## Was alles mit einer Schleife möglich wird

| Fähigkeit                    | Was die Schleife ermöglicht                          | Beispiele in der Praxis                              | Typische Schaltung                  |
|------------------------------|------------------------------------------------------|------------------------------------------------------|-------------------------------------|
| **Speichern**                | Zustand wird festgehalten                            | 1-Bit-Speicher, Register, RAM                       | SR-Latch, SRAM-Zelle                |
| **Zählen**                   | Impulse werden addiert / dekrementiert               | Binärzähler, Frequenzteiler                          | T-Flipflop-Kette                    |
| **Schalten / Steuern**       | Zustandswechsel nach Regeln                          | Verkehrsampel, Automaten, Steuerwerke               | Finite State Machine (FSM)          |
| **Synchronisieren**          | Alles passiert zum gleichen Takt                     | Prozessoren, Busse, Pipelines                        | Getaktete Flipflops + Taktgenerator |
| **Sequenzieren**             | Schritte werden nacheinander ausgeführt              | Befehlsausführung in einer CPU                       | Programm-Counter + Steuerwerk       |
| **Verzögern / Timing**       | Signale werden zeitlich verschoben                   | Ein-Takt-Verzögerung, Pipeline-Stufen               | Schieberegister                     |
| **Oszillieren**              | Dauerhafte Schwingung (Takt) erzeugen                | Ringoszillatoren, Uhren in Chips                     | 3–5 invertierte Schleifen           |
| **Multi-Schritt-Berechnung** | Komplexe Operationen über mehrere Takte             | Multiplikation, Division, Gleitkomma-Rechnung       | ALU + Register + FSM                |
| **Algorithmen ausführen**    | Hardware führt echte Programme / Algorithmen aus     | Jeder Mikroprozessor, Microcontroller                | CPU (Register + ALU + FSM)          |

## Ja – Algorithmen statt Formeln!

- **Kombinatorische Logik** = **Formel**  
  → Einmal Eingabe → sofort Ausgabe (wie eine mathematische Gleichung).

- **Sequentielle Logik (mit Schleife)** = **Algorithmus**  
  → Eingabe + aktueller Zustand → neuer Zustand + Ausgabe  
  → Das System hat ein „Gedächtnis“ und kann über mehrere Schritte hinweg etwas **berechnen**.

**Beispiel:**  
Eine ALU allein ist nur eine Formel (A + B).  
Aber ALU + Register + Programm-Counter + FSM = ein Prozessor, der einen **Algorithmus** (z. B. „Multipliziere zwei Zahlen mit Shift-and-Add“) Schritt für Schritt ausführt.

## Gibt es noch etwas anderes?

Ja, zwei weitere wichtige Dinge, die nur durch Schleifen möglich werden:

1. **Turing-Vollständigkeit** (theoretisch)  
   Mit genug Flipflops, einer ALU und einer FSM kannst du **jeden Algorithmus** ausführen, den ein Computer kann. Die Schleife ist der Grund, warum Hardware überhaupt universell programmierbar ist.

2. **Selbst-Modifikation / Lernfähigkeit** (bei Erweiterung)  
   In modernen Systemen (z. B. mit konfigurierbaren Logikbausteinen wie FPGA) kann die Schleife sogar ihre eigenen Regeln ändern – aber das ist schon eher „Reconfigurable Computing“.

**Kurz gesagt:**  
Die Schleife ist der „Geist in der Maschine“. Ohne sie gäbe es nur starre Formeln. Mit ihr entsteht alles, was wir unter „Digitaltechnik“, „Computer“ und „programmierbarer Hardware“ verstehen.
