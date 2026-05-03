# RWÖ – sehr bunte PyPy3-Simulation

Diese Simulation nutzt eine relationale Währung, die keine einzelne Zahl ist. Die Währung ist ein `RWB`: ein relationales Wertbündel aus Rechten, Pflichten, Risiken, Zeitbindungen, Nachweisen, Umweltlasten und Schutzgrenzen.

## Ausführen

```bash
pypy3 rwoe_bunte_pypy3_simulation.py
```

Falls PyPy3 nicht installiert ist:

```bash
python3 rwoe_bunte_pypy3_simulation.py
```

## Einzelne Simulationsteile ausführen

```bash
pypy3 rwoe_bunte_pypy3_simulation.py --teile 1,5,7
pypy3 rwoe_bunte_pypy3_simulation.py --teile 3-8
```

## Farben ausschalten

```bash
pypy3 rwoe_bunte_pypy3_simulation.py --no-color
```

## Zufalls-Startwert ändern

```bash
pypy3 rwoe_bunte_pypy3_simulation.py --seed 99
```

Die dunklen Simulationsteile sind Warnmodelle. Sie beschreiben, welche amoralische Seite durch Gesetze blockiert werden muss; sie sind keine Empfehlung.
