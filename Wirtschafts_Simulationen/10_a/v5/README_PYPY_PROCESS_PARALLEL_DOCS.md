# Planet Truth Economy — PyPy3 Process Parallel + Documentation Default Art

Diese Edition simuliert eine planetare Wirtschaft mit zwei Geldschichten:

1. **Fiat-Währungen** je Land: klassische Zahlenwährungen, Zentralbanken, Banken, Kredite, Wechselkurse.
2. **WK = Wahrheitskapital**: eine globale gestapelte Vektorwährung. WK beschreibt, wie stark Aussagen über Realität gedeckt sind: Existenz, Recht, Anerkennung, Kausalität, Sicherheit, Zeitbindung, Potenzial, Risiko, Wahrnehmung, Infrastruktur, Gesundheit, Kohärenz usw.

## Was wird simuliert?

- Länder mit eigener Fiat-Währung, GDP, Steuern, Zentralbank und lokaler Wahrheitsbilanz.
- Unternehmen, Haushalte, Geschäftsbanken, Entwicklungsbanken und Investmentbanken.
- Eine UN-ähnliche globale Institution und mehrere Verteidigungsorganisationen.
- Handels-, Kredit-, Wissens-, Wahrheits-, Governance- und Verteidigungsnetzwerke.
- FIFO-, LIFO- und Priority-Queues für ökonomische Intents und Nachrichtenflüsse.
- Half-Duplex- und Full-Duplex-Kanäle mit Semaphoren als Kapazitätsgrenzen.
- Transaktionen als Morphismen in Kategorien: Economy, Truth, Law, Security.
- Funktoren zwischen diesen Kategorien und natürliche Transformationen als Kohärenzlücken.
- Topologische Räume, Prägarben und Garben für lokale/globale Wahrheitskonsistenz.
- Universal Properties: Terminalobjekt, Produkt, Pullback, Pushout, Equalizer.
- Krisen, Audits, Kredite, Wahrheitsschulden, Sanktionen, Konflikte und Durchbrüche.
- Prozessparallelisierung über `multiprocessing` / `ProcessPoolExecutor`, nicht über Threads.

## Abkürzungen

| Kürzel | Bedeutung |
|---|---|
| WK | Wahrheitskapital; planetare Vektorwährung aus gestapelten Wahrheitswerten |
| TV | TruthVector; Datenstruktur des WK-Vektors |
| Fiat | nationale Zahlenwährung eines Landes |
| FX | Foreign Exchange / Wechselkurs |
| GDP | Bruttoinlandsprodukt / Gross Domestic Product |
| CB | Central Bank / Zentralbank |
| UN | globale Vermittlungs- und Normsetzungsinstitution |
| FIFO | First In, First Out |
| LIFO | Last In, First Out |
| PRIO | Priority Queue |
| HALF | Half-Duplex: ein Kanal sendet je Tick nur in eine Richtung |
| FULL | Full-Duplex: ein Kanal sendet gleichzeitig in beide Richtungen |
| SEM | Semaphore; begrenzte Kapazität für Durchleitung, Liquidität oder Vertrauen |
| 𝓔 / E | Economy Category |
| 𝓣 / T | Truth Category |
| 𝓛 / L | Law Category |
| 𝓢 / S | Security Category |
| F | Funktor zwischen Kategorien |
| η | natürliche Transformation; Kohärenzbrücke oder Lücke zwischen Funktoren |
| Gap | Kohärenzlücke: Reibung, Blase, Widerspruch, Schuld oder ungeklebte Wahrheit |
| U | offene Menge im topologischen Raum |
| F(U) | lokale Prägarben-/Garben-Sektion über U |
| s_i | lokale Sektion / lokaler Wahrheitszustand |
| Morphismus | gerichteter Übergang: Kauf, Kredit, Sanktion, Audit, Versicherung, Produktion |
| Pullback | gemeinsamer Ursprung zweier Ansprüche |
| Pushout | gemeinsames Kleben zweier Prozesse |
| Equalizer | Ausgleich zwischen zwei abweichenden Prozessen |

## Start

UTF-8-Art ist jetzt standardmäßig aktiv:

```bash
python planet_truth_paradigm_architecture_pypy_process.py --preset tiny --months 24
```

Mit PyPy3 und Prozessparallelisierung:

```bash
pypy3 planet_truth_paradigm_architecture_pypy_process.py --preset standard --months 120 --workers auto --out run_standard
```

Ohne Konsolen-Art, aber weiterhin mit Report-Dateien:

```bash
python planet_truth_paradigm_architecture_pypy_process.py --preset tiny --months 24 --no-print-art
```

## Ausgabedateien

- `history.csv`
- `agents.csv`
- `morphisms.csv`
- `events.json`
- `summary.json`
- `summary.txt`
- `utf8_paradigm_architecture_report.txt`

Der UTF-8-Report beginnt jetzt mit einer Dokumentation der Abkürzungen und der Modell-Lesart.
