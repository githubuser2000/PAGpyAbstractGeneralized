# Delta-Norm-Wirtschaftssimulation – Bericht

**Version:** 1.1.0  
**Tage:** 30  
**Personen:** 120  
**Seed:** 42  
**Szenario:** orbit_emergency  
**Laufzeit:** 0.83 Sekunden  

## Mathematischer Kern

```text
mu(e) = lambda_d * ( ||Phi_d(e)||_+ - ||Phi_d(e)||_- )
```

Jedes Verhalten wird als Vektor abgebildet. Die Plusnorm misst Beitrag; die Minusnorm misst Belastung. Die Differenz ist Delta-Geld.

## Szenario

- orbit_emergency: Erhöhtes Trümmer- und Sauerstoffrisiko.

## Schlusskennzahlen

| Kennzahl | Start | Ende |
|---|---:|---:|
| Preisindex | 110.122 | 330.264 |
| Grundversorgungspreisindex | 157.870 | 556.776 |
| Positive Geldmenge | 8774340.496 | 8888451.140 |
| Netto-Geld inkl. Haftung | 8774340.496 | 8888451.140 |
| Haftung | 0.000 | 0.000 |
| Arbeitslosigkeit | 18.33% | 18.33% |
| Gesundheit | 0.841 | 0.582 |
| Stress | 0.277 | 0.560 |
| Vertrauen | 0.649 | 0.911 |
| Gini positive Geldbestände | 0.121 | 0.153 |
| Medien-Wahrheit | 0.858 | 0.787 |
| Medien-Manipulation | 0.114 | 0.120 |
| Stationssicherheit | 0.662 | 0.613 |
| Orbit-Trümmerrisiko | 0.295 | 0.222 |

## Geldschöpfung und Haftung

- Geschaffenes Delta: **151580.08 D**
- Vernichtetes Delta: **30208.31 D**
- Neu gebuchte Haftung: **0.00 D**
- Bestrittene Ereignisse: **221**, erfolgreiche Einsprüche: **113**

## Delta nach Domänen

| Domäne | Ereignisse | Brutto-Delta |
|---|---:|---:|
| water | 3638 | 30980.06 |
| labor | 2760 | 26073.06 |
| media | 2701 | 24280.04 |
| energy | 3630 | 20876.57 |
| health | 1646 | 17385.84 |
| space | 928 | 15718.24 |
| consumption | 2690 | 3203.96 |
| culture | 194 | 1102.11 |
| education | 449 | 924.68 |
| transport | 38 | 537.63 |
| governance | 40 | 416.06 |
| infrastructure | 506 | 297.00 |
| finance | 4 | -19.08 |
| food | 3600 | -20808.08 |

## Häufigste Handlungen

| Domäne | Handlung | Anzahl |
|---|---|---:|
| food | `eat_food` | 3600 |
| water | `use_water` | 3600 |
| energy | `use_energy` | 3600 |
| labor | `employee_work` | 2760 |
| consumption | `general_consumption` | 2690 |
| media | `consume_news` | 2491 |
| health | `receive_healthcare` | 958 |
| space | `life_support_consumption` | 900 |
| health | `rest_and_recovery` | 653 |
| infrastructure | `idle_capacity` | 451 |
| education | `learn_skill` | 444 |
| media | `publish_news` | 210 |
| culture | `community_culture` | 194 |
| water | `produce_water` | 38 |

## Wohlhabendste Nicht-Markt-Akteure

| Akteur | Art | Ort | Positives Geld | Haftung |
|---|---|---|---:|---:|
| ZEMO Public Council / Öffentlicher Fonds | public | Earth | 468597.16 | 0.00 |
| Delta Clearing Bank | firm | Earth | 281483.02 | 0.00 |
| Mutual Risk & Life-Support Insurance | firm | Earth | 250337.42 | 0.00 |
| LEO Satellite Net | infrastructure | Orbit | 76636.98 | 0.00 |
| Earth Grid Backbone | infrastructure | Earth | 75000.00 | 0.00 |
| Lunar Habitat Ring | infrastructure | Moon | 75000.00 | 0.00 |
| Orbital Research Station | infrastructure | Station | 75000.00 | 0.00 |
| Moon Raumfahrt Cooperative | firm | Moon | 14635.85 | 0.00 |
| Station Energie Cooperative | firm | Station | 11793.59 | 0.00 |
| Orbit Gesundheit Cooperative | firm | Orbit | 11107.53 | 0.00 |
| Earth Energie Cooperative | firm | Earth | 10995.74 | 0.00 |
| Moon Raumfahrt Cooperative | firm | Moon | 10197.81 | 0.00 |

## Verletzliche Personen nach Netto-Konto

| Person | Ort | Netto | Gesundheit | Stress | Beschäftigt |
|---|---|---:|---:|---:|---|
| Juri Sato | Moon | 362.05 | 0.518 | 0.780 | ja |
| Samir Novak | Earth | 373.77 | 0.719 | 0.598 | nein |
| Amal Hoffmann | Earth | 385.53 | 0.623 | 0.723 | nein |
| Zoe Nguyen | Moon | 424.28 | 0.561 | 0.810 | ja |
| Iris Sato | Earth | 429.50 | 0.699 | 0.448 | nein |
| Ada Rossi | Earth | 439.60 | 0.624 | 0.393 | nein |
| Lina Hoffmann | Earth | 445.42 | 0.664 | 0.786 | nein |
| Ravi Rahman | Moon | 449.24 | 0.525 | 0.884 | ja |
| Kian Ito | Earth | 464.15 | 0.621 | 0.650 | nein |
| Juri Novak | Earth | 466.22 | 0.673 | 0.557 | nein |

## ZEMO-Lambda-Faktoren

| Domäne | Lambda |
|---|---:|
| consumption | 5.473 |
| culture | 4.883 |
| education | 7.325 |
| energy | 9.115 |
| environment | 7.578 |
| finance | 6.567 |
| food | 9.547 |
| governance | 6.904 |
| health | 8.251 |
| infrastructure | 7.746 |
| labor | 7.157 |
| media | 8.840 |
| space | 14.185 |
| transport | 6.736 |
| water | 10.188 |

## English Summary

This run models an Earth-Moon-Orbit Delta-Norm economy. Money is created from the spread between a contribution norm and a burden norm. Agents work, eat, consume, publish and consume news, maintain satellites and stations, pay wages, take loans, buy insurance, and receive protected basic access. The model exports CSV ledgers and a final JSON state for further analysis.
