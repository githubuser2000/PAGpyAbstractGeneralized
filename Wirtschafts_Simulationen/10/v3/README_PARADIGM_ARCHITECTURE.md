# Planet Truth Economy — Paradigma-Architektur-Edition

Diese Version transformiert die Simulation der gestapelten Wahrheitswert-Währung in eine Architektur aus Netzwerken, Queues, Duplex-Kanälen, Semaphoren, Topologie, Kategorien, Morphismen, Funktoren, natürlichen Transformationen, Prägarben und Garben.

## Start

```bash
python planet_truth_paradigm_architecture.py --preset tiny --months 24 --print-art
```

Größer:

```bash
python planet_truth_paradigm_architecture.py --preset standard --months 120 --seed 7 --out paradigm_standard
```

Maximaler Lauf:

```bash
python planet_truth_paradigm_architecture.py --preset epic --months 720 --seed 42 --out paradigm_epic
```

## Architekturbegriffe im Code

- **Netzwerke**: `TradeNetwork`, `CreditNetwork`, `GovernanceNetwork`, `DefenseNetwork`, `KnowledgeNetwork`, `TruthNetwork`
- **Topologien**: `MeshTopology`, `RingTopology`, `StarTopology`, `CorePeripheryTopology`
- **Queues**: `FIFOQueue`, `LIFOQueue`, `PriorityMessageQueue`
- **Duplex**: `HalfDuplexChannel`, `FullDuplexChannel`, `SecureFullDuplexChannel`
- **Semaphore**: `SimpleSemaphore` als ökonomische Knappheits-/Durchleitungsprimitive
- **Kategorie**: `EconomicCategory`, `TruthCategory`, `LegalCategory`, `SecurityCategory`
- **Morphismen**: `Morphism`, `Transaction`, `PurchaseTransaction`, `LoanOriginationTransaction`, `AuditTransaction`, `SanctionTransaction`
- **Funktoren**: `FiatToTruthFunctor`, `LegalityFunctor`, `SecurityFunctor`
- **Natürliche Transformationen**: `NaturalTransformation`, z. B. `η: F⇒L` und `η: F⇒S`
- **Universelle Eigenschaften**: Terminalobjekt, Produkt, Pullback, Pushout, Equalizer
- **Topologie / Prägarben / Garben**: `TopologicalSpace`, `GrothendieckTopology`, `Presheaf`, `LocalTruthPresheaf`, `Sheaf`

## Outputs

Die Simulation schreibt:

```text
history.csv
agents.csv
morphisms.csv
events.json
summary.json
summary.txt
utf8_paradigm_architecture_report.txt
```

Der UTF-8-Art-Report enthält Diagramme für Klassenvererbung, Netzwerk-Topologien, Queue-/Duplex-/Semaphore-Zustände, Kategorien/Funktoren/natürliche Transformationen, Garbenkleben, WK-Vektoren, Länder-Heatmaps, Zeitreihen-Sparklines und Morphismenflüsse.
