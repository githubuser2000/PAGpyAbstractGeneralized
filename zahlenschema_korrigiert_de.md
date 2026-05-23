# Korrigierte und vervollständigte Fassung des Zahlenschemas

Ich würde das Schema **nicht komplett verwerfen**, aber ab 37 deutlich härter normalisieren. Der Hauptfehler ist: Dort springt die Deutung oft von einer plausiblen Zahl-Komposition zu einem sehr speziellen Fachwort, ohne dass die Komposition dieses Fachwort wirklich erzwingt.

Besonders bei Primzahlen größer als 36 ist Vorsicht nötig: **37, 41, 43, 47, 53, 59, 61, 67, 71, 73, 79, 83, 89, 97, 101, 103, 107, 109** können in diesem System nicht aus früheren Faktoren erklärt werden. Sie müssen neue Grundbegriffe sein oder bewusst offen bleiben.

Ein paar harte mathematische Korrekturen vorweg:

- Eine Prägarbe ist sauber als kontravarianter Funktor `C^op -> Set` zu verstehen; eine Garbe ist dann eine Prägarbe mit zusätzlicher Lokalitäts- und Verklebungsbedingung. Siehe [Stacks Project][stacks-presheaf].
- Eine natürliche Transformation ist in der 2-Kategorie `Cat` eine **2-Zelle / ein 2-Morphismus** zwischen Funktoren, nicht ein „1-Transfor“ im üblichen kategorialen Level-Sinn. Siehe [nLab: Natural Transformation][nlab-natural-transformation].
- `Applicative` in Haskell ist nicht allgemein „Informationsanreicherung“, sondern eine Struktur zwischen Funktor und Monade, mit `pure`, `<*>` beziehungsweise `liftA2`. Siehe [Hackage: Control.Applicative][hackage-applicative].
- `Arrow` ist kein KI-/Herrschaftsbegriff, sondern eine strukturierte Rechen- und Kompositionsabstraktion mit `arr`, `first`, `***`, `&&&` usw. Siehe [Hackage: Control.Arrow][hackage-arrow].
- Für kategoriale Datenbanken ist die Intuition gut: Schemata können als kleine Kategorien und Instanzen als mengenwertige Funktoren modelliert werden; natürliche Transformationen passen dort als Transformationen beziehungsweise Provenienz zwischen Instanzen. Siehe [Spivak/Wisnesky: Relational Foundations for Functorial Data Migration][spivak-db].

## Korrigierte Basis 1–36

| Nr. | Korrigierter Kern | Kommentar |
|---:|---|---|
| 1 | Identität, Einzelpunkt, Referenz | Punkt/Identität ist gut. |
| 2 | Konkretion, Grenze, Kante, Paarung/Rahmen | Nicht „die Ecke Kante“ als einzelnes Ding, sondern Grenz- und Rahmenbildung. In Komposita: `2*n` = Mehrzahl, Rahmen, zweite Ebene von `n`. |
| 3 | Existenz, Lokator, Koordinate, Adresse | Gut. „Haken“ eher als Pointer/Handle. |
| 4 | Veränderung, Iteration, Cursor, Zustandsschritt | Gut. Cursor/Iterator passt. |
| 5 | Ganzheit, Atom, Container, diskrete Einheit | „Diskret“ passt, aber Topologie erst bei 28/56. |
| 6 | Wert, Skalar, Zahl ohne Zahlart | Gut. |
| 7 | Richtung, Orientierung, Winkel | „Das Gute“ ist philosophisch möglich, mathematisch aber Richtung/Orientierung. |
| 8 | Zustand, Struktur, Tensor/mehrdimensionale Komponente | Tensor nur, wenn wirklich multilineare oder indexierte Struktur gemeint ist. |
| 9 | Einheit, Variable, benannte Stelle | Gut. |
| 10 | Prädikat, Wirklichkeitsprüfung, Wahrheitswert unter Interpretation | Wahrheit entsteht nicht aus 10 allein, sondern aus Objekt + Modell/Interpretation + Prädikat. |
| 11 | Differenz, Delta, Abweichung | Gut. |
| 12 | Typ, Menge, Eigenschaft, Containerart | „Menge“ gut. Besser: Set/Typ/Property-space. Eine Menge kann als diskrete Kategorie gesehen werden; „(0,0)-Kategorie“ ist nicht der übliche Ausdruck. |
| 13 | Polarität, Negation, Vorzeichen, unärer Operator | Gut. |
| 14 | Kombination, Operation, Algebra, Synthese | Gut. |
| 15 | Universalität, Rekursion, Traversierung, Wiederholung | Gut, aber „alle mathematischen Objekte“ besser als Universalisierungsprinzip, nicht als einzelnes Objekt. |
| 16 | Funktion, Abbildung, Analysis | Gut. |
| 17 | Wahrscheinlichkeit, Unsicherheit, Inferenz | **Nicht** „das Absolute“. Wahrscheinlichkeit ist gerade Nicht-Absolutheit unter Information. |
| 18 | Relation, Ordnung, Vergleich, Verhältnis | Gut. Vergleiche können als Relationen oder Prädikate erscheinen. |
| 19 | Extremum, Optimierung, Grenzwert, Limesverhalten | Gut. |
| 20 | Klasse, Typklasse, Klassifikation, OOP-Klasse | Gut. Nicht automatisch „Wahrheitsstruktur“, eher Klassifikationsstruktur. |
| 21 | Instanz, Belegung, Binding | Sehr gut. |
| 22 | Verknüpfung, Subtyping, Vererbung, Polymorphie | Trennen: Vererbung = Strukturbeziehung; Polymorphie = mehrere Implementierungen/Dispatch unter gemeinsamer Schnittstelle. |
| 23 | Aspekt, Querschnittsbelang, AOP | Gut. |
| 24 | Graph, Netz, Knoten-Kanten-Struktur | Sehr gut. |
| 25 | linearer Datenfluss, Stream, Queue, Stack | Stack/Queue sind ADTs; Stream/Kanal ist der bessere Oberbegriff. FIFO = Queue, LIFO = Stack. |
| 26 | Bidirektionalität, Duplex, Reversibilität, Kanal mit Gegenrichtung | Ganze Zahlen sind nicht „bidirektional“, aber sie besitzen additive Inversen und eine zweiseitige Ordnung. |
| 27 | Nebenläufigkeit, Konflikt, Synchronisation, Deadlock/Livelock | Gut. |
| 28 | Topologie, Nähe-/Offenheitsstruktur, Raumstruktur | Nicht Algebra. Nicht „gesamte diskrete Mathematik“. Diskrete Topologie ist nur ein Spezialfall. |
| 29 | Morphismus, strukturerhaltender Pfeil | Sehr gut. |
| 30 | universelle Eigenschaft, universelles Objekt | Gut, aber braucht kategorialen Kontext. |
| 31 | Prägarbe/Garbe, lokale Daten mit Verklebung | Prägarbe ist wahrscheinlicher als Garbe, wenn die Verklebungsaxiome nicht explizit vorkommen. |
| 32 | Kategorie | Sehr gut. Kategorie = Objekte, Morphismen, Identitäten, Komposition. |
| 33 | Funktor | Gut. Ein Diagramm ist meist ein Funktor aus einer Indexkategorie. |
| 34 | Wahrscheinlichkeitsraum, Verteilungsraum, probabilistisches Modell | „Meta-Wahrscheinlichkeit“ besser: Verteilung über Verteilungen / hierarchisches Bayes / probabilistischer Modellraum. |
| 35 | natürliche Transformation | Gut, aber kategorial eine 2-Zelle zwischen Funktoren. |
| 36 | Datenbank: Schema + Instanz + Constraints + Queries | Gut. Nicht nur SQL; SQL ist eine konkrete Sprache/Technologie. |

## Sauberere Fassung ab 37

| Nr. | Besserer Begriff | Korrektur |
|---:|---|---|
| 37 | Modellstruktur, Managementstruktur, Schema-Verwaltung | **DBMS** passt nur als `36 mit 37`: Datenbank + Management. „Modellkategorientheorie“ ist zu speziell. „Kategoriale Winkeltheorie“ streichen. |
| 38 | Optimierungsrahmen, Optimizer, Query-Optimierung | `38 = 2*19`: Rahmen/Mehrfachheit von Extremierung. „Kategoriale Optimierungstheorie“ höchstens Spezialfall, nicht Kern. |
| 39 | unäre Signatur, Vorzeichen-/Operatorzeichen, markierter Locator | `39 = 3*13`: lokalisierte Polarität/unärer Marker. „Kategoriale Unär-Theorie“ klingt künstlich; besser: Signatur/Operation mit Stelligkeit 1. |
| 40 | Mannigfaltigkeit, Varietät, stratifizierte Klassenstruktur | Mannigfaltigkeit nur, wenn lokal koordinierbare Struktur gemeint ist. Gesellschaftsklassen allein machen noch keine Mannigfaltigkeit. „Varietät“ ist je nach Fach anders belegt. |
| 41 | Dynamik, Prozess, dynamisches System | Als Primzahl neuer Basisbegriff. „Kategoriale Dynamik“ geht, wenn Dynamik als Funktor/Endofunktor/Koalgebra modelliert wird. |
| 42 | Monade | Sehr gut. Mathematisch: Monade = Endofunktor mit Einheit und Multiplikation; in Haskell: kontrollierte Effekt-/Sequenzierungsstruktur. Siehe [nLab: Monad][nlab-monad]. |
| 43 | Effektmodell, Semantikmodell, Transformationsmodell | „Funktionales Modell“ ist zu breit. Wenn 42 beteiligt ist: Monad Transformer / Effekttransformation. |
| 44 | Zustandsübergangsmodell, Lifecycle-System, Kontrollsystem | Boot, Shutdown, Sessions, Robotik passen hier. „Kategoriale Vererbungstheorie“ eher nicht. |
| 45 | abstrakte Datenstruktur, algebraische Struktur, Systemkern | Kernel als Analogie okay. Mathematisch besser: abstrakte Datenstruktur / algebraische Struktur / Kernschicht. |
| 46 | Optics: Lens, Prism, Traversal; Querschnittszugriff | Sehr gut. „Lenses mit Traversals“ passt. Sprach-/Ausrichtungsmodell nur als Analogie. |
| 47 | Architektur, Systementwurf, Konstruktionsgrammatik | Gut als neuer Primbegriff. Nicht zwingend mathematisches Objekt, aber formal modellierbar durch Graphen, Operaden, Sheaves, Hypergraphen. |
| 48 | Netzwerkarchitektur, gewichteter Graph, neuronales Netz | Neural Net = spezialisierter gewichteter gerichteter Graph mit Aktivierungen und Training. Graphentheorie liegt eher bei 24; 48 ist Graph/Netz auf höherer Ebene. |
| 49 | Gradient, Trend, Differentialrichtung | Sehr gut. Differentialgleichungen gehören zusätzlich zu Funktion/Relation/Wahrheit; 49 allein ist eher Gradient/Trendrichtung. |
| 50 | Fold, Aggregation aus Streams, Stream Processing, Trainingspipeline | `50 = 2*25`: Stream-Rahmen. Maschinelles Lernen als Ganzes ist eher 48+49+50+51+54+55, nicht nur 50. |
| 51 | statistische Inferenz, Bayes-Update, Informationsgewinn | `51 = 3*17`: Wahrscheinlichkeit lokalisieren/aktualisieren. Informationstheorie ist nah, aber nicht exakt identisch. |
| 52 | Pragmatik, Metakommunikation, Modulation, paralinguistische Schicht | Metasprache-Idee passt: Akzent, Gestik, Mimik, Ton, Kontext. |
| 53 | Spieltheorie, Entscheidungstheorie, Social Choice | Gut als Primbegriff. |
| 54 | Mustererkennung, Inferenzbildung, Datenverarbeitung | Gut. `54 = 3*18 = lokalisierte Relationen`; passt zu Pattern/Inference. |
| 55 | Generator, generatives Modell, KI-Generator | „Künstliche Intelligenz“ ist zu groß. Besser: generatives System. KI insgesamt ist ein Verbund aus 48, 49, 50, 51, 54, 55. |
| 56 | topologischer Raum | Sehr gut. Aber: Topologien sind nicht einfach „Typen in Software“. In Homotopy Type Theory gibt es tiefe Bezüge zwischen Typen und Homotopieräumen/∞-Gruppoiden; das ist nicht dasselbe wie normale Programmiertypen. |
| 60 | Ontologie, Typuniversum, universelle Klassifikation | „Universelle Ordnung und Klasse“ ist gut. Mathematisch eventuell: Typuniversum, Taxonomie, Ontologie, Klassifikationsschema. |
| 64 | 2-Kategorie `Cat`, Kategorien-Framework, Kategorientheorie | Besser als „Kategorie selbst“. Wenn 32 = Kategorie, dann 64 = Kategorie-über-Kategorien / 2-kategorialer Rahmen. |
| 66 | Applicative Functor | Ja. Aber nicht primär „langweilige Informationen anreichern“, sondern unabhängige Effektkombination: `pure`, `<*>`, `liftA2`. Informationsanreicherung ist nur ein Anwendungsfall. |
| 70 | Funktorkategorie, 2-kategorialer Transformationsraum | Das „noch nicht erfundene Objekt“ gibt es: Die Funktorkategorie `[C,D]` hat Funktoren als Objekte und natürliche Transformationen als Morphismen. Für höhere Beziehungen: 2-/3-Kategorien, Modifikationen. |
| 75 | Stream-Koalgebra, Prozessstrom, Event-Trace | „Universeller Strom“ besser formal als koalgebraischer Stream oder Prozessmodell. „Menschenmasse“ ist soziologische Anwendung, nicht Kern. |
| 77 | Arrow, strukturierte Eingabe-Ausgabe-Komputation | Haskell Arrow passt. Der Satz „Maschinen regieren uns und werden kreativ“ ist kein mathematischer Kern; streichen oder als Kulturkommentar auslagern. |
| 84 | Monad Transformer, Effektstapel, distributive Gesetze von Monaden | Nicht „noch nicht erfunden“. Wenn „mehrere Monaden verwalten“ gemeint ist: Monad Transformer, Effect System, algebraic effects, distributive laws. |
| 90 | universelle Relation, universelles Schema, relationales Universum | Passt besonders für ReTa/SQL-Spalten-Abgleich. Aber sauberer: Universal Relation Model oder globales Schema. |
| 92 | Game Loop, interaktiver Zustandsautomat, Spielmechanik | Gaming/Jump’n’Run ist eine Anwendung. Der abstrakte Kern ist interaktive Zustandsdynamik mit Regeln, Input, Kollisionslogik, Feedback. |
| 94 | System-of-Systems, sozio-ökologisches Systemmodell, Architekturverbund | Gut. Mathematisch modellierbar durch Hypergraphen, Netzwerke, Sheaves, Operaden, Constraint-Systeme. |
| 105 | Modifikation, 2-/3-kategoriale Transformationsstruktur | Das „Objekt, das natürliche Transformationen in Beziehung setzt“ existiert teilweise: Modifikationen sind Transformationen zwischen natürlichen Transformationen in höherkategorialem Kontext. |
| 112 | topologische Analysis, Funktionalanalysis, Differentialtopologie oder TDA | Nicht „wohl noch nicht erfunden“. Je nach Akzent: Funktionalanalysis, Differentialtopologie, topologische Datenanalyse, topologische Dynamik. |

## Sinnvolle Ergänzungen der Lücken

Die folgenden Einträge folgen so weit wie möglich der eigenen Faktorlogik. Primzahlen bleiben bewusst offen, weil sonst wieder beliebige Begriffe angeklebt würden.

| Nr. | Faktorlogik | Vorschlag |
|---:|---|---|
| 57 | `3*19` | kritischer Punkt, Argmax/Argmin-Lokator, Extremstellenfinder |
| 58 | `2*29` | Hom-Menge, Morphismenfamilie, Pfeilraum |
| 59 | Primzahl | offen: neuer Basisbegriff nötig |
| 61 | Primzahl | offen |
| 62 | `2*31` | Garbensystem, Stack, Prägarben-/Garbenschicht |
| 63 | `7*9` | Vektor, gerichtete Variable, orientierte Einheit |
| 65 | `5*13` | signierter Container, Boolescher/negierbarer Zustand, Polaritätsklasse |
| 67 | Primzahl | offen |
| 68 | `2*34` | hierarchisches probabilistisches Modell, Verteilung über Verteilungen |
| 69 | `3*23` | Pointcut, lokalisierter Aspekt, aspektueller Zugriffspunkt |
| 71 | Primzahl | offen |
| 72 | `2*36`, `3*24` | Datenbankgraph, Knowledge Graph, relationaler Datenraum |
| 73 | Primzahl | offen |
| 74 | `2*37` | Modellmanagementsystem, Meta-Management, DBMS-Rahmen |
| 76 | `2*38` | Optimizer-System, Optimierungspipeline, Query-Plan-Raum |
| 78 | `2*39` | Signaturraum unärer Operationen, Operatorenfamilie |
| 79 | Primzahl | offen |
| 80 | `2*40` | Faserbündel, Atlasfamilie, Mannigfaltigkeitsfamilie |
| 81 | `9*9` | Matrix, Variablenraster, Tabellenkoordinaten |
| 82 | `2*41` | dynamisches System zweiter Ordnung, Automatenverbund |
| 83 | Primzahl | offen |
| 85 | `5*17` | Wahrscheinlichkeitsverteilung, Wahrscheinlichkeitsmaß als Ganzheit |
| 86 | `2*43` | Effektstapel, Transformationssystem, Semantikverbund |
| 87 | `3*29` | Quelle/Ziel-Lokator eines Morphismus, Hom-Indexierung |
| 88 | `2*44` | Lifecycle-Architektur, Kontrollsystemverbund, Automatenarchitektur |
| 89 | Primzahl | offen |
| 91 | `7*13` | Orientierung mit Vorzeichen, Richtungsnegation, Sign-Konvention |
| 93 | `3*31` | Halm/Stalk einer Garbe, lokale Garbendaten an einem Punkt |
| 95 | `5*19` | Optimierungslandschaft, Zielfunktionsraum, Extremwert-Container |
| 96 | `3*32`, `4*24` | kategoriale Semantik, Diagrammkategorie, Graphdynamik |
| 97 | Primzahl | offen |
| 98 | `2*49` | Gradientenfeld, Differentialstruktur, Trendfamilie |
| 99 | `9*11` | Kovarianz, Variablendifferenz, Abweichungsmatrix |
| 100 | `2*50` | Datenpipeline, Stream-Processing-System, Trainingssystem |
| 101 | Primzahl | offen |
| 102 | `2*51` | Bayes-Netz, probabilistisches Inferenzsystem |
| 103 | Primzahl | offen |
| 104 | `2*52` | multimodale Kommunikation, Kontext-/Pragmatiksystem |
| 106 | `2*53` | Multi-Agent-Spiel, kollektive Entscheidung, Social-Choice-System |
| 107 | Primzahl | offen |
| 108 | `2*54`, `3*36` | Datenbank-Inferenz, Knowledge-Base-Reasoning, Query-Inferenz |
| 109 | Primzahl | offen |
| 110 | `2*55` | generatives KI-System, Generatorfamilie, Modellensemble |
| 111 | `3*37` | Modellselektion, Modell-Lokator, Managementadresse |

## Wichtigste Streichungen und Relativierungen

**Streichen oder stark relativieren:**

- „Das Absolute = Wahrscheinlichkeitsrechnung“ → besser **Unsicherheit/Inferenz**. Wahrscheinlichkeit ist gerade nicht absolut.
- „Kategoriale Winkeltheorie“ → streichen. Dafür gibt es keinen naheliegenden Standardkern in diesem Schema.
- „Topologien sind dasselbe wie Typen in Software“ → zu stark. Korrekt nur in speziellen Kontexten wie Homotopy Type Theory oder kategorialer Semantik.
- „Natürliche Transformation = 1-Transfor“ → nur als „ein einzelner Transformationsgegenstand“ okay; kategorial ist sie eine **2-Zelle**.
- „AI = 55“ → zu groß. **55 = Generator/generatives Modell**; KI als Gesamtsystem ist eher ein Verbund: `48 Netzwerk + 49 Gradient/Trend + 50 Training/Fold/Stream + 51 Inferenz + 54 Mustererkennung + 55 Generator`.
- „84/105 noch nicht erfunden“ → größtenteils falsch. Dafür existieren bereits Funktorkategorien, 2-Kategorien, 3-Kategorien, Modifikationen, Monad Transformer, Effektstapel und distributive Gesetze.

## Sauberste Gesamtformel

Die stabilste Lesart des Systems wäre:

- **Primzahlen = neue ontologische Grundachsen.**
- **Komposita = kontrollierte Bedeutungsprodukte.**
- **`2*n` = Rahmen/Familie/System von `n`.**
- **`3*n` = lokalisierte/adressierte Form von `n`.**
- **`4*n` = dynamisierte/prozessierte Form von `n`.**
- **`5*n` = containerisierte/ganzheitliche Form von `n`.**
- **`7*n` = gerichtete/orientierte Form von `n`.**
- **`10*n` = prädikative/wahrheitsprüfende Form von `n`.**

Damit wird die Liste wesentlich stabiler. Der wichtigste Gewinn: Ab 37 werden nicht mehr prestigeträchtige Fachbegriffe auf Zahlen geklebt, sondern die Zahl muss durch die innere Kompositionslogik tragen, was sie bedeuten soll.

[stacks-presheaf]: https://stacks.math.columbia.edu/tag/001L
[nlab-natural-transformation]: https://ncatlab.org/nlab/show/natural%2Btransformation
[hackage-applicative]: https://hackage.haskell.org/package/base/docs/Control-Applicative.html
[hackage-arrow]: https://hackage.haskell.org/package/base/docs/Control-Arrow.html
[spivak-db]: https://www.sciencedirect.com/science/article/pii/S0890540112001010
[nlab-monad]: https://ncatlab.org/nlab/show/monad
