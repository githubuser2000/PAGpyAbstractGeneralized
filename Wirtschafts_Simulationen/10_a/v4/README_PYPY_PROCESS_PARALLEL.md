# Planet Truth Economy — PyPy3 Process-Parallel Edition

Diese Edition bleibt bei der Paradigma-Architektur mit Klassenvererbung, Kategorien, Morphismen, Funktoren, natürlichen Transformationen, Topologien, Prägarben/Garben, FIFO/LIFO/Priority-Queues, Half-/Full-Duplex-Kanälen und Semaphoren.

## Änderungen in dieser Version

1. **UTF-8-Art-Breite**
   - Alle `box(...)`-Renderings werden zentral zwei Zeichen schmaler gerendert.
   - Zusätzlich wird die aktuelle Terminalbreite berücksichtigt.
   - Dadurch passen die Boxdrawing-Visualisierungen besser in Fenster, die bei exakt voller Breite umbrechen.

2. **PyPy3-freundliche Prozessparallelität**
   - Keine Threads.
   - `multiprocessing` / `ProcessPoolExecutor` mit groben Batches.
   - Automatischer Fallback auf seriell, falls eine Umgebung Pool- oder Pickle-Probleme hat.

Parallelisierte Bereiche:

- Monatsalterung von Agenten
- Produktion und Handelsintents von Unternehmen
- Kreditintents von Banken
- Arbeitsmarktanpassungen
- Netzwerk-Ticks über Channel-Batches
- Garben-/Prägarben-Sektionen
- Funktor-Mapping der jüngsten Morphismen
- Naturalitätslücken
- planetare Aggregation von GDP und WK-Vektor

## Start

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py --preset tiny --months 24 --workers auto --print-art
```

Seriell:

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py --preset tiny --months 24 --workers 1
```

Explizit mit 4 Prozessen:

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py --preset standard --months 120 --workers 4 --out run_standard
```

Sehr groß:

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py --preset epic --months 720 --workers auto --out epic_world
```

## Optionen

```text
--workers auto|N            Anzahl Prozesse, auto wählt abhängig von Preset und CPU
--mp-start-method auto|fork|spawn|forkserver
--parallel-min-items N      Mindestgröße, ab der ein Prozessbatch genutzt wird
```

Für Unix/PyPy3 ist `fork` meistens am schnellsten. Auf Plattformen ohne `fork` fällt `auto` auf `forkserver` oder `spawn` zurück.
