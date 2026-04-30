# Solar Hierarchy Market — Network / Category / Sheaf Architecture

Dies ist eine neue Architekturversion der Sonnensystem-Hierarchie-Märktewirtschaft-Simulation.

Der Paradigmenwechsel ist nicht nur kosmetisch: Handel, Besitz, Märkte, Privilegien, Benachteiligungen, Organisationen und Länder werden jetzt gleichzeitig als **ökonomische Entitäten**, **Netzwerkknoten**, **Datenströme** und **Morphismen in Kategorien** modelliert.

## Hauptdatei

```bash
solar_hierarchy_market_network_category_sim_pypy3.py
```

## Start

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 3 --seed 42
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile huge --ticks 1 --json report.json
```

Ohne UTF-8-Diagramme:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --no-visuals
```

## Profile

- `demo`: schnelle, aber bereits große Demo
- `large`: großer Lauf mit vielen Arbeitnehmern, Firmen, Produkten und Morphismen
- `huge`: sehr großer Lauf

## Architekturänderungen

### 1. Netzwerkmodell

Jede ökonomische Entität wird zu einem Netzwerkknoten:

- Arbeitnehmer
- Arbeitgeber / Unternehmen
- Länder
- Bündnisse
- Verteidigungsorganisationen
- UN-artige Organisationen
- Produkte
- Märkte
- Privilegien
- Benachteiligungen / Burdens

Kanäle verbinden diese Knoten in verschiedenen Topologien.

### 2. FIFO / LIFO / Priority Queues

Jeder Knoten besitzt mehrere Datenstrom-Warteschlangen:

- FIFO für normale Datenströme
- LIFO für Schocks, Burdens und militärische Alerts
- Priority Queue für hochrangige Pakete
- Outbound Queue für Weiterleitung

Auch Kanäle besitzen gerichtete Queue-Ströme.

### 3. Half- und Full-Duplexing

Kanäle können sein:

- `simplex`
- `half`
- `full`

Half-Duplex-Kanäle lassen pro Mikrozyklus nur eine Richtung dominant passieren. Full-Duplex-Kanäle können beide Richtungen gleichzeitig bedienen.

### 4. Semaphore

Jeder Kanal hat eine Semaphore. Sie modelliert knappe Durchleitungskapazität, Blockierung, Permit-Verbrauch und Engpässe.

### 5. Topologien

Eingebaut sind mehrere Topologiearten:

- Governance Tree
- Stern-Topologie um UN- und Markthubs
- Interplanetarer Ring
- Unternehmens-Mesh
- Market-Bipartite-Graphen
- Sheaf-Cover-Topologien

### 6. Kategorien und Morphismen

Die Simulation erzeugt mehrere Kategorien:

- `EconomicHierarchyCategory`
- `NetworkFlowCategory`
- `HierarchyLevelCategory`
- `TopologyCategory`

Jede relevante Beziehung ist ein Morphismus:

- Governance
- Defense
- Alliance
- Employment
- Production
- Listing
- Product Trade
- Market Trade
- Privilege Grant
- Burden Assignment
- Manual Lift
- Channel Flow
- Topology Morphism

Kompositionen werden erzeugt und stichprobenartig geprüft.

### 7. Funktoren

Enthalten sind Funktoren:

- Economic → Network
- Economic → Hierarchy Status
- Economic → Access / Entitlement

Die Funktorialität wird im Report stichprobenartig geprüft.

### 8. Natürliche Transformation

Es gibt eine natürliche Transformation von Status zu Access/Entitlement:

```text
StatusFunctor => AccessFunctor
```

Sie modelliert, dass Status und tatsächlicher Zugriff durch Privilegien und Burdens unterschiedlich sein können.

### 9. Universelle Eigenschaften

Der Report enthält Witnesses für universelle Eigenschaften, unter anderem:

- initiale Governance-Quelle im Sonnensystem
- produktartige Markt-/Governance-Apex-Strukturen

Diese werden operational auf den endlichen Simulationskategorien geprüft.

### 10. Prägarben und Garben

Marktzustände werden als lokale Sections einer Prägarbe modelliert. Planetare und solare Zustände werden über Cover-Strukturen geglued.

Dadurch wird sichtbar, ob lokale Marktinformationen zu einem globalen Zustand zusammenfügbar sind.

## Visualisierungen

Die Simulation gibt viele UTF-8-Diagramme aus:

- Organisations-/Topologiebaum
- Hierarchiestufen-Histogramme
- Body × Level Heatmaps
- Channels by Topology
- Channels by Duplex Mode
- Queue Discipline Histogramme
- Packet-Kind-Histogramme
- Network Degree Distribution
- Hot Channels / Semaphores
- Kategoriegrößen
- Funktor-/Natürlichkeitsprüfungen
- Universal Property Witnesses
- Presheaf-/Sheaf-Cover-Gluing
- Marktvolumen nach Domain
- Markt-Domain × Level Heatmaps

## Keine externen Abhängigkeiten

Das Skript nutzt nur die Python-Standardbibliothek und ist für PyPy3 geeignet.
