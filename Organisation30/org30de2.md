# Logikschaltungen, die nicht als statische boolesche Formel formalisierbar sind

Die genannte Bedingung („**nicht als statische boolesche Formel** \( Q = f(\text{Eingänge}) \) formalisierbar“) trifft **ausschließlich auf sequentielle Logikschaltungen** zu.

**Grund:** Es gibt eine **Rückkopplung** (Feedback) oder einen internen **Zustandsspeicher**. Der Ausgang hängt daher nicht nur von den aktuellen Eingängen ab, sondern auch vom vorherigen Zustand.  
Formel:  
`Ausgang(t) = f(Eingänge(t), Zustand(t-1))`

## 1. ALU – **Nein**, die erfüllt die Bedingung nicht!
Eine **ALU** (Arithmetic Logic Unit) ist **rein kombinatorisch**.  
Sie hat keine Rückkopplung und keinen internen Speicher. Jedes Ergebnis lässt sich vollständig als boolesche Formel oder Wahrheitstabelle beschreiben.

## 2. Andere sequentielle Logikschaltungen (Beispiele)

| Schaltung                          | Warum keine reine Formel?                        | Typische Komplexität | Beispiel-Eingang/Ausgang |
|------------------------------------|--------------------------------------------------|----------------------|---------------------------|
| **D-Latch / D-Flipflop**           | Rückkopplung + Takt → Zustandsspeicher           | Klein                | D + CLK → Q speichert D bei Taktflanke |
| **JK-Flipflop**                    | Rückkopplung + J/K → Toggle-Modus                | Mittel               | J=1, K=1 → toggelt bei Takt |
| **T-Flipflop**                     | Rückkopplung → toggelt bei T=1                   | Klein                | T=1 + Takt → Q wechselt |
| **Schieberegister** (z. B. 4-Bit)  | Kette aus Flipflops mit Shift                    | Mittel               | Serielle Eingabe → parallele Ausgabe |
| **Binärer Zähler (Counter)**       | Kette aus Flipflops mit Feedback                 | Mittel–groß          | CLK-Pulse → zählt 0…15 |
| **Finite State Machine (FSM)**     | Interne Zustände + Übergangstabelle              | Mittel–sehr groß     | Zustand + Eingabe → neuer Zustand + Ausgabe |
| **Register** (z. B. 8-Bit)         | Mehrere Flipflops parallel + CLK                 | Mittel               | 8 Daten + CLK → speichert Byte |
| **SRAM-Speicherzelle**             | Kreuzgekoppelte Inverter                         | Sehr klein           | Schreib-/Lese-Operation speichert 1 Bit |
| **Vollständiger Mikroprozessor**   | Register + FSM + Pipeline                        | Sehr groß            | Befehle → sequentielle Zustandsänderungen |

## Merkregel
- **Mit Rückkopplung oder Takt + Speicher** → **keine Formel möglich**  
- **Ohne Rückkopplung (kombinatorisch)** → **immer als Formel möglich** (ALU, Addierer, Multiplexer …)

Diese Schaltungen sind alle sequentiell und benötigen eine Zustandsbeschreibung (z. B. Zustandsdiagramm oder nächste-Zustands-Gleichungen).
