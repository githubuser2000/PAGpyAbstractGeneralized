# Alternative mathematische Objekte für 43 bis 55

Ja. Für **43–55** würde ich die alte Liste deutlich schärfen. Der Kernfehler wäre hier, **KI-, Software- und Gesellschaftsbegriffe direkt als mathematische Objekte** zu setzen. Besser ist: erst das abstrakte mathematische Objekt finden, dann Software/KI/Gesellschaft nur als Anwendung lesen.

## Kurzempfehlung

| Zahl | Stärkste mathematische Lesart | Gute Alternativen |
|---:|---|---|
| 43 | **Effektsemantik / algebraischer Effekt / Monad-Morphismus** | Kleisli-Kategorie, Eilenberg-Moore-Kategorie, distributive Gesetze, Monad Transformer |
| 44 | **Zustandsautomat / Transitionssystem / Lifecycle-System** | Petri-Netz, Prozessalgebra, Statechart, Hybridautomat, Kohalgebra |
| 45 | **abstrakter Datentyp / initiale Algebra / algebraische Struktur** | Lawvere-Theorie, universelle Algebra, Kontext, Concept Lattice, Kernel |
| 46 | **Optic: Lens, Prism, Traversal** | Profunctor Optic, Zipper, Store-Comonad, Fokussierungsstruktur |
| 47 | **Operad / Wiring-Diagram-Operad / Systemarchitektur** | Hypergraph-Kategorie, dekorierter Cospan, Sheaf-Architektur, Double Category |
| 48 | **parametrisierter Rechengraph / gewichteter gerichteter Graph / neuronales Netz** | Tensor-Netzwerk, Factor Graph, GNN, Hypergraph-Netz |
| 49 | **Differential / Gradient / Tangentenvektor** | Vektorfeld, Jacobi-Matrix, Differentialform, Richtungsableitung |
| 50 | **Fold / Catamorphism / Stream-Aggregator / Trainingsoperator** | Transducer, Streaming-Algorithmus, Estimator, Pipeline |
| 51 | **Bayes-Update / Likelihood / Posterior / Informationsmaß** | Entropie, KL-Divergenz, Bayesian Network, statistisches Experiment |
| 52 | **formale Metasprache / Grammatik + Semantik** | Übersetzungsfunktor, Interpretation, Kontextlogik, Pragmatikmodell |
| 53 | **Spiel / Mechanismus / Social-Choice-Funktion** | Nash-Gleichgewicht, Wahlregel, Fair-Division-Problem, kooperatives Spiel |
| 54 | **Inferenzsystem / Pattern-Recognizer / Klassifikator** | CSP, Graph Matching, Feature Map, Proof System, Query-Evaluator |
| 55 | **Generator / generatives Modell / freies Objekt** | Grammatikgenerator, Zufallsprozess, Sampling-Operator, GAN/VAE, freie Algebra |

Meine härteste Normalform wäre:

> **43 = Effektmodell**  
> **44 = Zustandsprozess**  
> **45 = abstrakter Datentyp**  
> **46 = Optic/Fokusstruktur**  
> **47 = Architektur-Operad**  
> **48 = Rechengraph/Netz**  
> **49 = Differential/Gradient**  
> **50 = Fold/Training/Aggregation**  
> **51 = Inferenzinformation**  
> **52 = Metasprache**  
> **53 = strategisches Entscheidungssystem**  
> **54 = Inferenz-/Mustererkennungssystem**  
> **55 = Generator**

---

# 43 — Effektmodell, Monad-Transformation, Semantikschicht

43 ist **Primzahl**. Also sollte 43 in deinem System eher eine neue Grundachse sein, nicht einfach „42 plus 1“. Da 42 bei dir sehr plausibel die **Monade** ist, liegt 43 direkt danach als:

> **nicht die Monade selbst, sondern das Modell, wie Effekte transformiert, interpretiert oder semantisch verwaltet werden.**

## 43A — Monad-Morphismus / Monad-Transformation

Eine naheliegende mathematische Form:

$$
\alpha : T \Rightarrow S
$$

also eine natürliche Transformation zwischen Monaden, die Einheit und Multiplikation der Monaden respektiert.

Das passt zu deinem alten Satz:

> „funktionales Modell z.B. als Monaden-Transformation“

Das ist mathematisch sauberer als „funktionales Modell“ allgemein.

**Lesart:**

- 42 = Monade.
- 43 = Transformation zwischen Effektwelten.
- Beispiel: von Fehler-Effekt zu Logging-Effekt, von Zustands-Effekt zu IO-Effekt, von abstrakter Semantik zu konkreter Ausführung.

Monad-Morphismen werden genau als natürliche Transformationen verstanden, die die Monadenstruktur respektieren. Siehe: [nLab: Monad transformations](https://ncatlab.org/nlab/show/monad%2Btransformations).

**Stärke:** sehr hoch.

## 43B — algebraischer Effekt

Noch stärker, wenn du 43 als „Effektmodell“ statt nur als „Monadentransformation“ liest.

Algebraische Effekte beschreiben Effekte durch Operationen und Gleichungen, etwa:

- Zustand,
- Ausnahme,
- Nichtdeterminismus,
- Eingabe/Ausgabe,
- Nebenläufigkeit,
- Zeit,
- Interaktion.

Plotkin/Pretnar behandeln algebraische Effekte und Handler gerade als allgemeine Semantik für solche Recheneffekte. Siehe: [Handling Algebraic Effects](https://arxiv.org/abs/1312.1399).

Dann wäre:

> **43 = Theorie der Effekte.**

Das passt extrem gut zwischen:

- 42 = Monade,
- 44 = Ablauf/Zustand/Lifecycle,
- 50 = Training/Fold/Stream,
- 55 = Generator.

**Stärke:** sehr hoch.

## 43C — Kleisli-Kategorie

Zu jeder Monade \(T\) gehört eine Kleisli-Kategorie.

Wenn normale Funktionen so aussehen:

$$
f : A \to B
$$

dann sehen effektvolle Funktionen so aus:

$$
f : A \to T(B)
$$

Das ist die klassische mathematische Form von „Berechnung mit Effekt“.

**Lesart:**

> 43 = Raum effektvoller Funktionen.

Das ist weniger allgemein als „Effektmodell“, aber sehr klar.

**Stärke:** hoch.

## 43D — Eilenberg-Moore-Kategorie

Die Eilenberg-Moore-Kategorie einer Monade besteht aus den Algebren dieser Monade. Wenn Kleisli eher „Berechnung ausführen“ meint, meint Eilenberg-Moore eher:

> **Strukturen, die den Effekt bereits absorbiert haben.**

Für dein System wäre das interessant, wenn 43 nicht „Transformation“ meint, sondern:

> **stabilisierte Semantik eines Effekts.**

**Stärke:** gut, aber spezieller.

## 43E — Monad Transformer

Ein Monad Transformer macht aus einer Monade eine neue Monade, typischerweise um Effekte zu stapeln. In Haskell-Dokumentationen wird ein Monad Transformer genau als Konstruktion beschrieben, die aus einer vorhandenen Monade eine neue Monade macht, wobei alte Berechnungen eingebettet werden können. Siehe: [Control.Monad.Trans](https://haddocks.haskell-miso.org/mtl/Control-Monad-Trans.html).

Beispielhaft:

$$
T \mapsto StateT\;s\;T
$$

Das passt zu deiner alten Formulierung „Monaden-Transformation“, aber ich würde es nicht als Hauptkern von 43 setzen. Eher:

- 43 = Effektmodell,
- 84 = Effektstapel / Monad-Transformer-System.

**Stärke:** gut, aber wahrscheinlich eher 84 als 43.

## Empfehlung für 43

Beste Reihenfolge:

1. **Effektsemantik / algebraischer Effekt**
2. **Monad-Morphismus**
3. **Kleisli-Kategorie**
4. **Eilenberg-Moore-Kategorie**
5. **Monad Transformer**

Kurz:

> **43 = Effektmodell: die semantische Verwaltung von Berechnungseffekten.**

---

# 44 — Zustandsautomat, Lifecycle, Transitionssystem

44 ist zusammengesetzt:

$$
44 = 4 \times 11
$$

4 = Veränderung, Iterator, Zustandsschritt.  
11 = Differenz, Delta, Abweichung.

Also:

> **44 = System von Zustandsänderungen.**

Das passt sehr gut zu deinem alten Eintrag:

> Init-System, Boot, Shutdown, Sessions, Robotik.

Aber mathematisch sollte man es nicht zuerst „Init-System“ nennen. Das ist Software-Anwendung. Das mathematische Objekt darunter ist:

> **Transitionssystem / Zustandsautomat.**

## 44A — Zustandsautomat

Klassisch:

$$
(S, \Sigma, \delta, s_0, F)
$$

mit:

- \(S\) = Zustandsmenge,
- \(\Sigma\) = Eingabealphabet,
- \(\delta\) = Übergangsfunktion,
- \(s_0\) = Startzustand,
- \(F\) = akzeptierende oder finale Zustände.

Das passt zu:

- Boot,
- Shutdown,
- Sessions,
- Init-Zuständen,
- Robotik-Modi,
- Systemzuständen,
- Prozesszuständen.

**Stärke:** sehr hoch.

## 44B — Labelled Transition System

Ein Labelled Transition System hat Übergänge mit Bezeichnungen:

$$
s \xrightarrow{a} s'
$$

Das ist noch besser, wenn die Übergänge benannte Aktionen tragen:

- `boot`,
- `login`,
- `suspend`,
- `resume`,
- `shutdown`,
- `recover`,
- `fail`,
- `restart`.

**Stärke:** sehr hoch.

## 44C — Petri-Netz

Ein Petri-Netz ist besser als ein einfacher Automat, wenn mehrere Dinge parallel laufen:

- Ressourcen,
- Sperren,
- Prozesse,
- Warteschlangen,
- konkurrierende Zustände,
- Synchronisation.

Das passt zu deinem früheren Bereich 27, Deadlock/Livelock. Für 44 wäre ein Petri-Netz geeignet, wenn Lifecycle nicht linear ist, sondern nebenläufig.

**Stärke:** hoch.

## 44D — Kohalgebra

Kohalgebren modellieren zustandsbasierte Systeme sehr allgemein. Rutten beschreibt Universal Coalgebra ausdrücklich als Theorie von Systemen; Kohalgebren eignen sich für Automaten, Transitionssysteme und dynamische Systeme. Siehe: [Universal Coalgebra: A Theory of Systems](https://www.cs.cornell.edu/courses/cs6861/2024sp/Handouts/Rutten.pdf).

Allgemeine Form:

$$
c : X \to F(X)
$$

Das ist eine sehr elegante kategoriale Lesart für 44.

**Aber:** Ich würde Kohalgebra eher bei 41 als Grundobjekt setzen und 44 als konkrete Lifecycle-/Transitionsform davon.

**Stärke:** hoch, aber wahrscheinlich allgemeiner als 44.

## 44E — Hybridautomat

Wenn Robotik, reale Zeit und kontinuierliche Bewegung wichtig werden:

- diskrete Zustände,
- kontinuierliche Dynamik,
- Übergangsbedingungen,
- Kontrollsignale.

Dann passt ein Hybridautomat.

Beispiel:

- Roboter steht.
- Roboter fährt.
- Roboter bremst.
- Roboter kollidiert.
- Roboter wechselt Modus.

**Stärke:** gut, besonders für Robotik.

## Empfehlung für 44

Beste Reihenfolge:

1. **Zustandsautomat / Transitionssystem**
2. **Labelled Transition System**
3. **Petri-Netz**
4. **Kohalgebra**
5. **Hybridautomat**

Kurz:

> **44 = Lifecycle-Transitionssystem.**

---

# 45 — abstrakter Datentyp, initiale Algebra, algebraische Struktur

45 hat mehrere gute Faktorisierungen:

$$
45 = 3 \times 15
$$

3 = Lokator/Existenz/Adresse.  
15 = Universalität/Rekursion/Traversal.

Und:

$$
45 = 5 \times 9
$$

5 = Ganzheit/Container.  
9 = Variable/Einheit.

Das ergibt:

> **45 = ein containerisierter Variablen-/Strukturkern, der universell benutzt werden kann.**

Dein alter Begriff „Kernel / Betriebssystemkern“ ist als Analogie okay. Mathematisch besser ist:

> **abstrakter Datentyp / algebraische Struktur / initiale Algebra.**

## 45A — abstrakter Datentyp

Ein abstrakter Datentyp wird nicht primär durch seine konkrete Speicherform beschrieben, sondern durch:

- Träger,
- Operationen,
- Gleichungen,
- Schnittstelle,
- Verhaltensgesetze.

Das passt extrem gut zu „Kernel“ im Sinne von:

> innerer Kern einer Struktur, der Operationen bereitstellt.

Die algebraische Spezifikation abstrakter Datentypen ist ein klassisches Thema in Informatik und algebraischer Semantik. Siehe: [Algebraic specifications of abstract data types](https://www.sciencedirect.com/science/article/pii/S0304397582800017).

**Stärke:** sehr hoch.

## 45B — initiale Algebra

Für rekursive Datenstrukturen:

$$
\mu F
$$

Beispiel:

- Listen,
- Bäume,
- natürliche Zahlen,
- Syntaxbäume,
- algebraische Datentypen.

Initiale Algebren sind besonders passend, wenn 45 mit 15 = Rekursion/Universalität verbunden wird.

**Lesart:**

> 45 = rekursiver Strukturkern.

**Stärke:** sehr hoch.

## 45C — algebraische Struktur

Allgemein:

$$
(A, \Omega)
$$

mit Trägermenge \(A\) und Operationen \(\Omega\).

Beispiele:

- Gruppe,
- Ring,
- Monoid,
- Verband,
- Modul,
- Algebra.

Das ist die breiteste mathematische Lesart von 45.

**Stärke:** hoch.

## 45D — Lawvere-Theorie

Eine Lawvere-Theorie beschreibt algebraische Theorien kategorisch; Modelle solcher Theorien entsprechen algebraischen Strukturen mit Operationen und Gleichungen. Lawveres ursprüngliche Perspektive verbindet algebraische Theorien, algebraische Kategorien und algebraische Funktoren. Siehe: [Lawvere: Algebraic Theories, Algebraic Categories, and Algebraic Functors](https://lawverearchives.com/wp-content/uploads/2024/12/1965-algebraic-theories-algebraic-categories-and-algebraic-functors.pdf).

Das passt, wenn 45 nicht nur eine einzelne Struktur meint, sondern:

> **den abstrakten Theorie-Kern hinter vielen konkreten Strukturen.**

**Stärke:** hoch, aber etwas metatheoretischer.

## 45E — Formal Concept Lattice

Wenn du bei 45 „universelle Ordnung und Klasse“ meinst, ist auch ein **Begriffsverband** aus der Formal Concept Analysis interessant. Formal Concept Analysis mathematisiert Begriffe und Begriffshierarchien und verwendet dabei Verbände/Ordnungsstrukturen. Siehe: [Formal Concept Analysis](https://philpapers.org/rec/GANFCA-2).

Das passt zu:

- Klassen,
- Eigenschaften,
- Ordnung,
- Taxonomie,
- Ontologie,
- Wissensstruktur.

**Stärke:** gut, wenn 45 stärker epistemisch/ontologisch gelesen wird.

## Empfehlung für 45

Beste Reihenfolge:

1. **abstrakter Datentyp**
2. **initiale Algebra**
3. **algebraische Struktur**
4. **Lawvere-Theorie**
5. **Concept Lattice**

Kurz:

> **45 = abstrakter Strukturkern / algebraisch spezifizierter Datentyp.**

---

# 46 — Optic, Lens, Traversal, Fokussierungsstruktur

46 ist:

$$
46 = 2 \times 23
$$

23 = Aspekt / Querschnittsbelang.  
2 = Rahmen, Mehrzahl, zweite Ebene.

Also:

> **46 = Rahmen von Aspekt-Zugriffen.**

Dein alter Eintrag „Lenses mit Traversals“ ist hier sehr gut. Ich würde nur den Oberbegriff korrigieren:

> **46 = Optic.**

Optics sind bidirektionale oder fokussierende Zugriffsstrukturen auf Daten. Profunctor Optics verallgemeinern Lenses, Prisms, Traversals usw. und geben ihnen eine kompositionale Darstellung. Siehe: [Profunctor Optics](https://www.cs.ox.ac.uk/people/jeremy.gibbons/publications/poptics.pdf).

## 46A — Lens

Eine Lens fokussiert auf einen Teil eines Ganzen:

$$
S \leftrightarrow A
$$

Intuitiv:

- `get`: Hole Teil aus Ganzem.
- `set`: Setze Teil im Ganzen zurück.

Das passt zu:

- Objektfeld,
- Record-Zugriff,
- Datenbankfeld,
- UI-Komponente,
- Aspektzugriff.

**Stärke:** sehr hoch.

## 46B — Traversal

Traversal ist stärker als Lens, weil mehrere Foki vorhanden sein können.

Beispiel:

- alle Elemente einer Liste,
- alle Werte in einem Baum,
- alle Treffer in einer Struktur.

Das passt gut zu deinem „Querschnittsmodell“.

**Stärke:** sehr hoch.

## 46C — Prism

Ein Prism fokussiert auf einen Fall in einer Summentyp-Struktur.

Beispiel:

- `Either Error Value`,
- `Maybe a`,
- Variante eines algebraischen Datentyps.

Das passt, wenn 46 nicht nur Feldzugriff, sondern Auswahl eines möglichen Falls meint.

**Stärke:** hoch.

## 46D — Profunctor Optic

Das ist die mathematisch stärkste Oberform:

- Lens,
- Prism,
- Traversal,
- Iso,
- Getter,
- Setter,
- Fold

als Varianten einer allgemeineren Optic-Struktur.

**Stärke:** sehr hoch, aber abstrakter.

## 46E — Zipper

Ein Zipper ist ein Datenstruktur-Fokus mit Kontext.

Beispiel:

- Cursor in einem Baum,
- Cursor in einer Liste,
- Bearbeitung einer lokalen Stelle mit Rückkehr zum Ganzen.

Das verbindet 46 mit 4 = Cursor/Iterator und 23 = Aspekt.

**Stärke:** gut.

## Empfehlung für 46

Beste Reihenfolge:

1. **Optic**
2. **Lens**
3. **Traversal**
4. **Profunctor Optic**
5. **Zipper**

Kurz:

> **46 = kompositionale Fokussierungsstruktur.**

---

# 47 — Architektur, Operad, Wiring Diagram

47 ist **Primzahl**. Also wieder neue Grundachse.

Dein alter Begriff „Architektur“ ist gut, aber mathematisch zu unbestimmt. Das beste mathematische Objekt für Architektur ist meistens:

> **Operad / Wiring-Diagram-Operad.**

Denn Architektur meint nicht nur „Graph“, sondern:

- Teile,
- Schnittstellen,
- Verschachtelung,
- Zusammensetzung,
- Anschlussregeln,
- Module,
- Subsysteme,
- Komposition.

Genau dafür sind Operaden sehr stark.

## 47A — Operad

Ein Operad beschreibt, wie Operationen mit mehreren Eingängen zu größeren Operationen zusammengesetzt werden.

Für Architektur heißt das:

- Module haben Ports.
- Module werden verschaltet.
- Verschaltungen können verschachtelt werden.
- Kleine Systeme bilden größere Systeme.
- Komposition ist selbst formal geregelt.

Operaden werden in der angewandten Kategorientheorie gerade für modulare Systemkomposition und Systemdesign verwendet. Siehe: [Operads for complex system design specification](https://royalsocietypublishing.org/doi/10.1098/rspa.2021.0099).

**Stärke:** sehr hoch.

## 47B — Wiring-Diagram-Operad

Noch präziser:

> **47 = Operad der Verdrahtungsdiagramme.**

Das passt extrem gut zu Architektur, Software, Robotik, sozio-technischen Systemen und Systemkonstruktion.

Vagner, Spivak und Lerman benutzen Operaden von Wiring Diagrams, um offene dynamische Systeme aus einfacheren Systemen zusammenzusetzen. Siehe: [Algebras of open dynamical systems on the operad of wiring diagrams](https://arxiv.org/abs/1408.1598).

**Stärke:** extrem hoch.

## 47C — dekorierter Cospan

Ein Cospan:

$$
A \to X \leftarrow B
$$

modelliert ein offenes System mit Eingangs-/Ausgangsgrenzen. Dekorierte Cospans fügen interne Struktur hinzu.

Das passt zu:

- offenen Systemen,
- Schaltkreisen,
- Netzwerken,
- Interfaces,
- Systemgrenzen.

Fong zeigt, dass dekorierte Cospan-Kategorien Hypergraph-Kategorien liefern; diese Formalismen werden für kompositionale Netzwerke benutzt. Siehe: [Decorated cospans](https://www.tac.mta.ca/tac/volumes/30/33/30-33.pdf).

**Stärke:** sehr hoch.

## 47D — Hypergraph-Kategorie

Eine Hypergraph-Kategorie ist gut, wenn Architektur nicht nur aus Kanten zwischen zwei Knoten besteht, sondern aus Verbindungen vieler Einheiten.

Fong/Spivak beschreiben Hypergraph-Kategorien als anwendungsreich, unter anderem für Automaten, Datenbanken, Schaltkreise, lineare Relationen, Graph-Rewriting und Belief Propagation. Siehe: [Seven Sketches in Compositionality: An Invitation to Applied Category Theory](https://arxiv.org/abs/1806.08304).

**Stärke:** hoch.

## 47E — Sheaf-Architektur

Eine Garbe/Sheaf passt, wenn Architektur aus lokalen Komponenten besteht, die global verklebt werden.

Das wäre interessant für:

- sozio-ökologische Systeme,
- regionale Daten,
- föderale Systeme,
- lokale Modelle,
- globale Konsistenz.

Aber als Hauptbegriff ist Sheaf eher 31/62/93, nicht 47.

**Stärke:** gut, aber sekundär.

## Empfehlung für 47

Beste Reihenfolge:

1. **Wiring-Diagram-Operad**
2. **Operad**
3. **dekorierter Cospan**
4. **Hypergraph-Kategorie**
5. **Sheaf-Architektur**

Kurz:

> **47 = kompositionale Architektur / Operad der Systemverschaltungen.**

---

# 48 — Rechengraph, neuronales Netz, gewichteter Graph

48 hat starke Faktorisierungen:

$$
48 = 2 \times 24
$$

24 = Graph/Netz.  
2 = Rahmen, Mehrzahl, zweite Ebene.

Also:

> **48 = Netz höherer Ordnung / Grapharchitektur.**

Auch:

$$
48 = 3 \times 16
$$

3 = Lokator.  
16 = Funktion.

Also:

> **48 = lokal verteilte Funktionen.**

Und:

$$
48 = 4 \times 12
$$

4 = Veränderung.  
12 = Menge/Typ/Eigenschaften.

Also:

> **48 = trainierbare Veränderung von Merkmalsräumen.**

Darum ist 48 tatsächlich ein sehr guter Ort für neuronale Netze.

## 48A — parametrisierter Rechengraph

Ein neuronales Netz ist mathematisch sehr gut als parametrisierter Rechengraph lesbar:

- Knoten = Operationen/Aktivierungen,
- Kanten = Datenfluss,
- Gewichte = Parameter,
- Ausgabe = zusammengesetzte Funktion.

Das ist wahrscheinlich die allgemeinste Lesart.

**Stärke:** extrem hoch.

## 48B — gewichteter gerichteter Graph

Ein einfacheres Objekt:

$$
G = (V,E,w)
$$

mit Gewichten:

$$
w:E\to \mathbb{R}
$$

Das passt zu klassischen neuronalen Netzen, aber es reicht noch nicht ganz: Man braucht zusätzlich Aktivierungsfunktionen und Komposition.

**Stärke:** hoch.

## 48C — neuronales Netz als Funktionsfamilie

Formal:

$$
f_\theta : X \to Y
$$

mit Parametern \(\theta\).

Dann ist das Netz nicht nur Graph, sondern eine parametrisierte Familie von Funktionen.

Das passt sehr gut zu:

- Training,
- Optimierung,
- Gradienten,
- Generalisierung.

**Stärke:** sehr hoch.

## 48D — Tensor-Netzwerk

Ein Tensor-Netzwerk ist ein Graph, dessen Knoten Tensoren tragen und dessen Kanten Indexkontraktionen anzeigen.

Das passt, wenn du 8 = Tensor ernst nimmst und 48 als höhere Netzstruktur über Tensoren liest.

**Stärke:** hoch, aber spezieller.

## 48E — Factor Graph / Bayesian Network

Ein Factor Graph modelliert Faktorisierungen einer Funktion oder Wahrscheinlichkeitsverteilung. Bayesian Networks verwenden Graphen für Abhängigkeitsstrukturen; Pearl beschreibt Graphen als Werkzeug zur Darstellung von Unabhängigkeiten und kausaler/probabilistischer Information. Siehe: [Pearl: Bayesian Networks](https://link.springer.com/chapter/10.1007/978-1-4899-1424-8_9).

Das verbindet 48 mit 51.

**Stärke:** hoch, wenn Wahrscheinlichkeit zentral ist.

## 48F — Graph Neural Network

Wenn die Eingabedaten selbst Graphen sind, ist ein Graph Neural Network passend. Hamilton beschreibt GNNs als Framework für Deep Neural Networks auf Graphdaten, bei denen Knotenrepräsentationen von Graphstruktur und Features abhängen. Siehe: [Graph Representation Learning](https://www.cs.mcgill.ca/~wlh/grl_book/files/GRL_Book.pdf).

Das ist eher eine Spezialisierung von 48 als dessen Kern.

**Stärke:** gut bis hoch.

## Empfehlung für 48

Beste Reihenfolge:

1. **parametrisierter Rechengraph**
2. **neuronales Netz als Funktionsfamilie**
3. **gewichteter gerichteter Graph**
4. **Tensor-Netzwerk**
5. **Factor Graph / Bayesian Network**
6. **Graph Neural Network**

Kurz:

> **48 = trainierbare Graph-Funktionsarchitektur.**

---

# 49 — Differential, Gradient, Trend

49 ist:

$$
49 = 7 \times 7
$$

7 = Richtung, Orientierung, Winkel.

Also:

> **49 = Richtung der Richtung / Änderungsrichtung / gerichteter Trend.**

Dein alter Begriff „Trend“, „Synapse“, „Differential“ ist gut. Ich würde nur „Synapse“ als Anwendung auslagern. Mathematisch ist der Kern:

> **Differential / Gradient / Tangentenvektor.**

## 49A — Differential

Für eine Funktion:

$$
df_x : T_xX \to T_{f(x)}Y
$$

Das Differential beschreibt die lokale lineare Änderung einer Funktion.

**Stärke:** extrem hoch.

## 49B — Gradient

Für eine skalare Funktion:

$$
\nabla f
$$

Der Gradient zeigt in Richtung des stärksten lokalen Anstiegs.

Das passt perfekt zu „Trend“ und zu maschinellem Lernen:

- Verlustfunktion,
- Gradientenabstieg,
- Richtung der Verbesserung,
- Synapsengewichte ändern sich entlang Gradienten.

**Stärke:** extrem hoch.

## 49C — Tangentenvektor

Ein Tangentenvektor ist eine lokale Richtung an einem Punkt eines Raums.

Wenn 40 = Mannigfaltigkeit oder Moduli-Raum ist, dann ist 49:

> **Richtung im Klassen-/Modellraum.**

**Stärke:** sehr hoch.

## 49D — Vektorfeld

Ein Vektorfeld weist jedem Punkt eine Richtung zu:

$$
x \mapsto v(x)
$$

Das ist stärker als ein einzelner Gradient.

**Stärke:** hoch, aber vielleicht eher 98 als Feld von Trends.

## 49E — Jacobi-Matrix

Für mehrdimensionale Funktionen:

$$
J_f(x)
$$

Sie beschreibt lokale lineare Abhängigkeiten zwischen Eingangs- und Ausgangsrichtungen.

Das passt, wenn 49 nicht nur Richtung, sondern lokale Sensitivität meint.

**Stärke:** hoch.

## Empfehlung für 49

Beste Reihenfolge:

1. **Gradient**
2. **Differential**
3. **Tangentenvektor**
4. **Jacobi-Matrix**
5. **Vektorfeld**

Kurz:

> **49 = lokale Änderungsrichtung.**

---

# 50 — Fold, Catamorphism, Stream-Aggregator, Training

50 ist:

$$
50 = 2 \times 25
$$

25 = Datenstrom, Stack, Queue, gerichteter Fluss.  
2 = Rahmen/System von 25.

Also:

> **50 = System zur Verarbeitung von Strömen.**

Auch:

$$
50 = 5 \times 10
$$

5 = Ganzheit/Container.  
10 = Prädikat/Wahrheitsprüfung.

Also:

> **50 = aus vielen Daten eine entscheidbare Ganzheit machen.**

Damit ist deine alte Intuition gut:

> Folding aus Datenströmen, Stream Processing, maschinelles Lernen.

Aber ich würde **maschinelles Lernen nicht vollständig auf 50 setzen**. 50 ist eher der mathematische Kern von Training/Aggregation.

## 50A — Fold / Catamorphism

Ein Fold reduziert eine rekursive Struktur zu einem Ergebnis.

Beispiel:

$$
fold : [a] \to b
$$

oder kategorisch:

$$
cata
$$

Das passt perfekt zu deiner Formulierung:

> aus Datenströmen ein Etwas machen.

**Stärke:** extrem hoch.

## 50B — Streaming-Algorithmus

Ein Streaming-Algorithmus verarbeitet Daten nacheinander, oft mit begrenztem Speicher.

Das passt zu:

- Datenstrom,
- Online-Verarbeitung,
- inkrementeller Analyse,
- Echtzeitverarbeitung.

**Stärke:** sehr hoch.

## 50C — Transducer

Ein Transducer wandelt einen Eingabestrom in einen Ausgabestrom um.

$$
Stream(A) \to Stream(B)
$$

Das passt besser als Fold, wenn nicht alles zu einem Ergebnis zusammengefasst wird, sondern ein neuer Strom entsteht.

**Stärke:** hoch.

## 50D — Estimator / Lernoperator

In Statistik/ML:

$$
\mathcal{A}: D \mapsto \theta
$$

Ein Lernalgorithmus macht aus Daten \(D\) Modellparameter \(\theta\).

Das ist die präziseste mathematische Form von „Training“.

**Stärke:** sehr hoch.

## 50E — empirische Risikominimierung

Maschinelles Lernen kann oft als Optimierung eines empirischen Risikos formuliert werden:

$$
\hat{\theta} = \arg\min_\theta \frac{1}{n}\sum_i L(f_\theta(x_i), y_i)
$$

Das verbindet 50 mit 38 und 49:

- 38 = Optimierungsproblem,
- 49 = Gradient,
- 50 = Trainings-/Aggregationsprozess.

**Stärke:** hoch.

## Empfehlung für 50

Beste Reihenfolge:

1. **Fold / Catamorphism**
2. **Lernoperator / Estimator**
3. **Streaming-Algorithmus**
4. **Transducer**
5. **empirische Risikominimierung**

Kurz:

> **50 = Aggregation und Training aus Datenströmen.**

---

# 51 — Bayes-Update, Information, Inferenz

51 ist:

$$
51 = 3 \times 17
$$

3 = Lokator, Adresse, Gegebenheit.  
17 = Wahrscheinlichkeit, Unsicherheit.

Also:

> **51 = lokalisierte Wahrscheinlichkeit / Aktualisierung von Unsicherheit durch Evidenz.**

Deine Kandidaten „Informationstheorie“, „Bayes-Theorie“, „Bayes-Statistik“ sind alle nah dran. Ich würde 51 aber nicht einfach „Informationstheorie“ nennen. Besser:

> **51 = probabilistische Inferenzinformation.**

## 51A — Bayes-Update

Klassisch:

$$
P(H\mid E)=\frac{P(E\mid H)P(H)}{P(E)}
$$

Das ist genau:

- Hypothese,
- Evidenz,
- Wahrscheinlichkeit,
- Aktualisierung.

**Stärke:** extrem hoch.

## 51B — Likelihood-Funktion

$$
L(\theta \mid x)
$$

Die Likelihood sagt: Wie plausibel sind Parameter \(\theta\), wenn Daten \(x\) beobachtet wurden?

Das passt zu:

- Evidenz,
- Inferenz,
- statistischer Modellierung,
- Lernen.

**Stärke:** sehr hoch.

## 51C — Posterior-Verteilung

$$
p(\theta \mid x)
$$

Das ist die aktualisierte Wahrscheinlichkeitsverteilung nach Beobachtung.

**Stärke:** sehr hoch.

## 51D — Informationsentropie

Shannons Informationstheorie führt Entropie und Kommunikation über Kanäle als mathematische Grundlage der Information ein. Siehe: [Shannon: A Mathematical Theory of Communication](https://people.math.harvard.edu/~ctm/home/text/others/shannon/entropy/entropy.pdf).

Entropie:

$$
H(X)=-\sum_x p(x)\log p(x)
$$

Das passt, wenn 51 eher „Informationsgehalt einer Unsicherheit“ meint.

**Stärke:** hoch.

## 51E — KL-Divergenz

$$
D_{KL}(P\|Q)
$$

Misst, wie verschieden zwei Verteilungen sind.

Das passt sehr gut zu:

- Lernen,
- Bayes,
- Informationsgewinn,
- Modellvergleich.

**Stärke:** hoch.

## 51F — Bayesian Network

Ein Bayesian Network verbindet Graphstruktur und Wahrscheinlichkeiten. Pearl beschreibt Graphen als formale Sprache zur Darstellung von Unabhängigkeiten und kausaler/probabilistischer Information. Siehe: [Pearl: Bayesian Networks](https://link.springer.com/chapter/10.1007/978-1-4899-1424-8_9).

Das verbindet 51 mit 48.

**Stärke:** hoch, aber eher zusammengesetzt.

## Empfehlung für 51

Beste Reihenfolge:

1. **Bayes-Update**
2. **Posterior-Verteilung**
3. **Likelihood**
4. **Entropie / Informationsmaß**
5. **KL-Divergenz**
6. **Bayesian Network**

Kurz:

> **51 = evidenzbasierte Aktualisierung von Wahrscheinlichkeit.**

---

# 52 — Metasprache, Grammatik, Semantik, Kontext

52 ist:

$$
52 = 4 \times 13
$$

4 = Veränderung/Prozess.  
13 = Negation, Polarität, Zeichen, Ja/Nein.

Auch:

$$
52 = 2 \times 26
$$

26 = Bidirektionalität/Kanal mit Gegenrichtung.  
2 = Rahmen.

Daher passt dein alter Begriff **Metasprache** ziemlich gut.

Mathematisch sollte man 52 aber nicht nur als Gestik/Mimik verstehen, sondern allgemeiner:

> **Sprache über Sprache / Interpretation von Zeichen unter Kontext.**

## 52A — formale Grammatik

Eine Grammatik:

$$
G=(N,\Sigma,P,S)
$$

beschreibt, welche Ausdrücke einer Sprache gebildet werden können.

Das passt zu:

- Syntax,
- Ausdrucksbildung,
- Metasprache,
- Sprachstruktur.

**Stärke:** hoch.

## 52B — Semantikfunktion

Eine Semantikfunktion interpretiert syntaktische Ausdrücke in Bedeutungsobjekten:

$$
\llbracket - \rrbracket : Syntax \to Semantik
$$

Das ist für 52 wahrscheinlich noch besser als Grammatik.

**Lesart:**

> 52 = nicht nur Sprache, sondern Bedeutungsschicht.

**Stärke:** sehr hoch.

## 52C — Übersetzungsfunktor

Wenn verschiedene Sprachen oder Theorien ineinander übersetzt werden:

$$
F : \mathcal{L}_1 \to \mathcal{L}_2
$$

Das passt zu:

- Dialekt,
- Übersetzung,
- Metasprache,
- kulturelle Codierung,
- Sprachmodell,
- Interpretation.

**Stärke:** hoch.

## 52D — Kontextlogik / Indexsemantik

Wenn Bedeutung vom Kontext abhängt, braucht man eine Semantik, die über Kontexten variiert.

Das kann man prägarbenartig oder kategorisch modellieren:

$$
C^{op}\to Set
$$

Das wäre eine Brücke zu 31/62.

**Stärke:** gut bis hoch.

## 52E — Pragmatikmodell / Spielsemantik

Gestik, Mimik, Akzent, Tonfall und „zwischen den Zeilen lesen“ sind nicht nur Syntax/Semantik, sondern Pragmatik.

Mathematisch kann man das über:

- Spielsemantik,
- Signaling Games,
- dynamische Semantik,
- epistemische Logik

modellieren.

**Stärke:** gut, aber spezieller.

## Empfehlung für 52

Beste Reihenfolge:

1. **Semantikfunktion**
2. **formale Metasprache**
3. **formale Grammatik**
4. **Übersetzungsfunktor**
5. **Kontextsemantik**
6. **Pragmatikmodell**

Kurz:

> **52 = Metasprache als Syntax-Semantik-Kontext-Schicht.**

---

# 53 — Spiel, Mechanismus, Social Choice

53 ist **Primzahl**. Also neue Grundachse.

Dein alter Eintrag ist hier stark:

> Spieltheorie, Entscheidungsfindung, Computational Social Choice, Mathematik vom Teilen.

Ich würde 53 als abstrakten Kern setzen:

> **strategische Mehr-Agenten-Entscheidung.**

Computational Social Choice behandelt kollektive Entscheidungsverfahren wie Wählen, Ressourcenzuteilung und Fair Division; genau diese Themen passen zu deiner alten Intuition. Siehe: [Computational Social Choice: 10 Years Later](https://pub.dss.in.tum.de/brandt-research/comsoc10years.pdf).

## 53A — Normalformspiel

Ein Spiel:

$$
G=(N,(S_i)_{i\in N},(u_i)_{i\in N})
$$

mit:

- Spieler,
- Strategien,
- Nutzenfunktionen.

Das ist der klassische Grundkörper.

**Stärke:** extrem hoch.

## 53B — extensive-form game

Wenn Zeit, Reihenfolge und Information wichtig sind:

- Wer zieht zuerst?
- Wer weiß was?
- Welche Entscheidung folgt auf welche?
- Gibt es unvollständige Information?

Dann passt ein Spielbaum.

**Stärke:** hoch.

## 53C — Mechanismus

Ein Mechanismus ist eine Regel, die aus privaten Präferenzen oder Signalen eine kollektive Entscheidung erzeugt.

Das passt extrem gut zu:

- Governance,
- Institutionen,
- Abstimmungen,
- Marktregeln,
- Auktionen,
- faire Verteilung.

**Stärke:** extrem hoch.

## 53D — Social-Choice-Funktion

$$
f : \text{Präferenzprofile} \to \text{Entscheidung}
$$

Das ist der präziseste Kandidat für „Computational Social Choice“.

**Stärke:** sehr hoch.

## 53E — Fair-Division-Problem

Mathematisch:

- Güter,
- Agenten,
- Präferenzen,
- Allokationen,
- Fairnesskriterien.

Das passt zu „Mathematik vom Teilen“.

**Stärke:** sehr hoch.

## 53F — Nash-Gleichgewicht

Ein Nash-Gleichgewicht ist ein stabiler Strategiepunkt, an dem kein einzelner Spieler durch einseitige Abweichung besser wird.

Das ist aber eher Lösungskonzept als Grundobjekt. Also nicht 53 selbst, sondern:

> 53 mit 19/38 = Gleichgewichts-/Optimierungsanalyse eines Spiels.

**Stärke:** gut, aber nicht Hauptobjekt.

## Empfehlung für 53

Beste Reihenfolge:

1. **Spiel / Game Form**
2. **Mechanismus**
3. **Social-Choice-Funktion**
4. **Fair-Division-Problem**
5. **Nash-Gleichgewicht**
6. **kooperatives Spiel**

Kurz:

> **53 = strategisches Entscheidungsobjekt mehrerer Akteure.**

---

# 54 — Inferenzsystem, Mustererkennung, Klassifikator

54 ist sehr gut zusammengesetzt:

$$
54 = 3 \times 18
$$

3 = Lokator.  
18 = Relation.

Also:

> **54 = lokalisierte Relation / erkannte Beziehung an Daten.**

Auch:

$$
54 = 2 \times 27
$$

27 = Konfliktauflösung, Nebenläufigkeit, Deadlock/Livelock.  
2 = Rahmen.

Also:

> **54 = Rahmen zur Auflösung relationaler Unklarheit.**

Das passt zu deinem alten Eintrag:

> Datenverarbeitung, Mustererkennung, Inferenzbildung.

## 54A — Klassifikator

Ein Klassifikator:

$$
h : X \to Y
$$

ordnet Eingaben Klassen zu.

Das ist der einfachste mathematische Kern von Mustererkennung.

**Stärke:** sehr hoch.

## 54B — Feature Map

$$
\phi : X \to \mathbb{R}^n
$$

Eine Feature Map transformiert Rohdaten in Merkmalsräume.

Das passt gut zu:

- Mustererkennung,
- ML,
- Repräsentation,
- Inferenzvorbereitung.

**Stärke:** hoch.

## 54C — Inferenzregel / Proof System

Ein Inferenzsystem besteht aus Regeln:

$$
\frac{A \quad A\Rightarrow B}{B}
$$

Das passt, wenn 54 eher logisch gelesen wird:

- Daten,
- Regeln,
- Schlussfolgerung.

**Stärke:** sehr hoch.

## 54D — Constraint Satisfaction Problem

Ein CSP besteht aus:

- Variablen,
- Wertebereichen,
- Constraints.

Es fragt:

> Gibt es eine Belegung, die alle Bedingungen erfüllt?

Das passt zu Datenverarbeitung und relationaler Mustererkennung.

**Stärke:** hoch.

## 54E — Graph Pattern Matching

Wenn Daten relational oder graphartig sind:

- Subgraph Matching,
- Homomorphismen,
- Muster in Netzwerken,
- Query Matching.

Das verbindet 54 mit 24/48/72/108.

**Stärke:** hoch.

## 54F — probabilistisches Inferenzsystem

Bishop verbindet Pattern Recognition und Machine Learning stark mit probabilistischen und Bayes’schen Methoden; dieser Zugang macht 54 anschlussfähig an 51. Siehe: [Pattern Recognition and Machine Learning](https://www.microsoft.com/en-us/research/wp-content/uploads/2006/01/Bishop-Pattern-Recognition-and-Machine-Learning-2006.pdf).

Das ist stark, wenn 54 nicht nur logisch, sondern unsicherheitsbasiert gelesen wird.

**Stärke:** hoch.

## Empfehlung für 54

Beste Reihenfolge:

1. **Inferenzsystem**
2. **Klassifikator**
3. **Feature Map**
4. **Constraint Satisfaction Problem**
5. **Graph Pattern Matching**
6. **probabilistisches Inferenzsystem**

Kurz:

> **54 = Muster- und Schlussfolgerungsobjekt.**

---

# 55 — Generator, generatives Modell, freies Objekt

55 ist:

$$
55 = 5 \times 11
$$

5 = Ganzheit/Container.  
11 = Differenz/Delta/Abweichung.

Also:

> **55 = Ganzheit, die Differenzen erzeugt.**

Dein alter Eintrag „Generator“ ist hier sehr gut. Aber „künstliche Intelligenz“ ist zu breit. Besser:

> **55 = Generator / generatives Modell.**

KI insgesamt wäre ein Verbund aus vielen Zahlen:

$$
48 + 49 + 50 + 51 + 54 + 55
$$

also:

- Netz,
- Gradient,
- Training,
- Inferenz,
- Mustererkennung,
- Generierung.

## 55A — Generator in Algebra

Ein Erzeugendensystem \(S\) einer Struktur \(A\):

$$
\langle S \rangle = A
$$

Beispiel:

- eine Gruppe wird von Elementen erzeugt,
- ein Vektorraum von Basisvektoren,
- eine Algebra von Generatoren und Relationen.

Das ist mathematisch sehr sauber.

**Stärke:** extrem hoch.

## 55B — freies Objekt

Ein freies Objekt ist das allgemeinste Objekt, das aus Generatoren gebaut wird.

Beispiele:

- freie Gruppe,
- freier Monoid,
- freie Algebra,
- freie Kategorie.

Das passt perfekt zu:

> aus wenigen Ausgangsdingen viele Strukturen erzeugen.

**Stärke:** extrem hoch.

## 55C — formale Grammatik als Generator

Eine Grammatik generiert eine Sprache:

$$
G \Rightarrow L(G)
$$

Das passt zu:

- Sprache,
- Syntax,
- Programme,
- Texte,
- Symbolsysteme.

Das verbindet 55 mit 52.

**Stärke:** hoch.

## 55D — probabilistisches generatives Modell

Ein generatives Modell beschreibt, wie Daten aus latenten oder beobachtbaren Zufallsvariablen entstehen:

$$
z \sim p(z), \quad x \sim p_\theta(x\mid z)
$$

Das ist der Kern vieler moderner ML-Modelle.

GANs formulieren generative Modellierung durch ein adversariales Verfahren, bei dem ein Generator \(G\) und ein Diskriminator \(D\) gemeinsam trainiert werden. Siehe: [Generative Adversarial Nets](https://arxiv.org/abs/1406.2661).

VAEs formulieren Lernen und Inferenz in probabilistischen Modellen mit latenten Variablen über variationale Approximation. Siehe: [Auto-Encoding Variational Bayes](https://arxiv.org/abs/1312.6114).

**Stärke:** extrem hoch.

## 55E — Sampling-Operator

Ein Sampling-Operator erzeugt Stichproben aus einer Verteilung:

$$
sample : P(X) \to X
$$

Das passt, wenn 55 eher „Ausgabe erzeugen“ als „Modellstruktur“ meint.

**Stärke:** hoch.

## 55F — Zufallsprozess

Ein stochastischer Prozess erzeugt zeitlich geordnete Zufallsvariablen:

$$
(X_t)_{t\in T}
$$

Das passt zu:

- Textgenerierung,
- Simulation,
- zufälligen Pfaden,
- Markov-Ketten,
- Diffusionsprozessen.

**Stärke:** hoch.

## Empfehlung für 55

Beste Reihenfolge:

1. **Generator / Erzeugendensystem**
2. **freies Objekt**
3. **generatives probabilistisches Modell**
4. **Sampling-Operator**
5. **formale Grammatik als Generator**
6. **Zufallsprozess**

Kurz:

> **55 = Erzeugungsobjekt.**

---

# Beste Gesamtfassung 43–55

So würde ich die Reihe jetzt stabilisieren:

| Zahl | Normalisierte Fassung |
|---:|---|
| 43 | **Effektmodell / algebraischer Effekt / Monad-Morphismus** |
| 44 | **Transitionssystem / Lifecycle-Automat** |
| 45 | **abstrakter Datentyp / initiale Algebra / algebraische Struktur** |
| 46 | **Optic: Lens, Prism, Traversal** |
| 47 | **Operad / Wiring-Diagram-Architektur** |
| 48 | **parametrisierter Rechengraph / neuronales Netz** |
| 49 | **Gradient / Differential / Tangentenrichtung** |
| 50 | **Fold / Catamorphism / Stream-Aggregator / Trainingsoperator** |
| 51 | **Bayes-Update / Posterior / Informationsmaß** |
| 52 | **Metasprache / Semantikfunktion / formale Grammatik** |
| 53 | **Spiel / Mechanismus / Social-Choice-Funktion** |
| 54 | **Inferenzsystem / Klassifikator / Mustererkenner** |
| 55 | **Generator / generatives Modell / freies Objekt** |

# Die stärkste interpretative Kette

Man kann 43–55 als Funktionskette lesen:

| Bereich | Zahlen | Bedeutung |
|---|---:|---|
| Effekt und Ablauf | 43–44 | Wie Berechnungen Wirkungen haben und Zustände wechseln |
| Strukturkern und Zugriff | 45–46 | Welche Datenstruktur existiert und wie man gezielt darauf zugreift |
| Architektur und Netz | 47–48 | Wie Systeme zusammengesetzt und als Netz/Funktionsgraph realisiert werden |
| Lernen und Trend | 49–50 | Wie Änderung gemessen und aus Daten gelernt wird |
| Unsicherheit und Bedeutung | 51–52 | Wie Evidenz und Sprache interpretiert werden |
| Entscheidung und Inferenz | 53–54 | Wie Akteure entscheiden und Systeme Schlüsse ziehen |
| Erzeugung | 55 | Wie neue Objekte, Daten, Texte, Strukturen oder Modelle generiert werden |

Die beste Kurzformel:

> **43–55 = von Effektsemantik über Systemarchitektur zu Lernen, Entscheidung, Inferenz und Generierung.**

Oder noch kompakter:

> **43–55 beschreibt den Übergang von strukturierter Berechnung zu generativer Intelligenz — aber mathematisch sauber, ohne „KI“ als Einzelobjekt zu überladen.**
