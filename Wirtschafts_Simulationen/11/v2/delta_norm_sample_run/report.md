# Delta-Norm-Wirtschaftssimulation – Bericht

**Version:** 1.2.0  
**Tage:** 30  
**Personen:** 120  
**Seed:** 42  
**Szenario:** media_crisis  
**Laufzeit:** 1.03 Sekunden  

## Mathematischer Kern

```text
mu(e) = lambda_d * ( ||Phi_d(e)||_+ - ||Phi_d(e)||_- )
```

Jedes Verhalten wird als Vektor abgebildet. Die Plusnorm misst Beitrag; die Minusnorm misst Belastung. Die Differenz ist Delta-Geld.

## Szenario

- media_crisis: Öffentliches Vertrauen startet niedriger.

## Schlusskennzahlen

| Kennzahl | Start | Ende |
|---|---:|---:|
| Preisindex | 112.524 | 314.717 |
| Grundversorgungspreisindex | 158.268 | 523.504 |
| Positive Geldmenge | 8774835.410 | 8894074.106 |
| Netto-Geld inkl. Haftung | 8774835.410 | 8894074.106 |
| Haftung | 0.000 | 0.000 |
| Arbeitslosigkeit | 6.67% | 6.67% |
| Gesundheit | 0.847 | 0.675 |
| Stress | 0.280 | 0.608 |
| Vertrauen | 0.501 | 0.725 |
| Gini positive Geldbestände | 0.124 | 0.146 |
| Medien-Wahrheit | 0.925 | 0.887 |
| Medien-Manipulation | 0.061 | 0.072 |
| Stationssicherheit | 0.716 | 0.771 |
| Orbit-Trümmerrisiko | 0.116 | 0.024 |

## Geldschöpfung und Haftung

- Geschaffenes Delta: **154309.93 D**
- Vernichtetes Delta: **27379.24 D**
- Neu gebuchte Haftung: **0.00 D**
- Bestrittene Ereignisse: **239**, erfolgreiche Einsprüche: **133**

## Delta nach Domänen

| Domäne | Ereignisse | Brutto-Delta |
|---|---:|---:|
| water | 3671 | 39418.41 |
| labor | 3131 | 28778.39 |
| energy | 3633 | 20542.51 |
| media | 2512 | 17988.46 |
| health | 1624 | 16878.71 |
| space | 1070 | 14057.36 |
| consumption | 2686 | 1818.31 |
| culture | 193 | 1049.03 |
| education | 489 | 952.23 |
| transport | 32 | 506.16 |
| governance | 40 | 424.57 |
| infrastructure | 462 | 76.64 |
| finance | 4 | -19.94 |
| food | 3600 | -16100.18 |

## Häufigste Handlungen

| Domäne | Handlung | Anzahl |
|---|---|---:|
| food | `eat_food` | 3600 |
| water | `use_water` | 3600 |
| energy | `use_energy` | 3600 |
| labor | `employee_work` | 3131 |
| consumption | `general_consumption` | 2686 |
| media | `consume_news` | 2271 |
| space | `life_support_consumption` | 1050 |
| health | `receive_healthcare` | 909 |
| health | `rest_and_recovery` | 664 |
| education | `learn_skill` | 489 |
| infrastructure | `idle_capacity` | 427 |
| media | `publish_news` | 240 |
| culture | `community_culture` | 193 |
| water | `produce_water` | 71 |

## Wohlhabendste Nicht-Markt-Akteure

| Akteur | Art | Ort | Positives Geld | Haftung |
|---|---|---|---:|---:|
| ZEMO Public Council / Öffentlicher Fonds | public | Earth | 469974.73 | 0.00 |
| Delta Clearing Bank | firm | Earth | 288133.06 | 0.00 |
| Mutual Risk & Life-Support Insurance | firm | Earth | 250936.90 | 0.00 |
| Lunar Habitat Ring | infrastructure | Moon | 76096.31 | 0.00 |
| Earth Grid Backbone | infrastructure | Earth | 75000.00 | 0.00 |
| LEO Satellite Net | infrastructure | Orbit | 75000.00 | 0.00 |
| Orbital Research Station | infrastructure | Station | 75000.00 | 0.00 |
| Earth Energie Cooperative | firm | Earth | 11538.63 | 0.00 |
| Earth Wasser Cooperative | firm | Earth | 11052.87 | 0.00 |
| DeepContext Review | media | Earth | 10217.63 | 0.00 |
| Station Gesundheit Cooperative | firm | Station | 10048.71 | 0.00 |
| Station Raumfahrt Cooperative | firm | Station | 9559.32 | 0.00 |

## Verletzliche Personen nach Netto-Konto

| Person | Ort | Netto | Gesundheit | Stress | Beschäftigt |
|---|---|---:|---:|---:|---|
| Malik Silva | Moon | 157.61 | 0.633 | 0.820 | ja |
| Ravi Rahman | Moon | 231.17 | 0.648 | 0.790 | ja |
| Juri Sato | Moon | 269.66 | 0.696 | 0.782 | ja |
| Zoe Nguyen | Moon | 293.44 | 0.667 | 0.798 | ja |
| Mira Novak | Moon | 337.26 | 0.698 | 0.610 | ja |
| Mira Schmidt | Moon | 356.50 | 0.719 | 0.657 | ja |
| Amal Nguyen | Station | 440.94 | 0.673 | 0.566 | ja |
| Mira Rahman | Station | 444.32 | 0.710 | 0.611 | ja |
| Kian Okafor | Station | 499.68 | 0.655 | 0.273 | ja |
| Aiko Silva | Station | 505.89 | 0.729 | 0.384 | ja |

## ZEMO-Lambda-Faktoren

| Domäne | Lambda |
|---|---:|
| consumption | 5.518 |
| culture | 4.924 |
| education | 7.386 |
| energy | 9.190 |
| environment | 7.640 |
| finance | 6.622 |
| food | 9.627 |
| governance | 6.961 |
| health | 8.319 |
| infrastructure | 7.810 |
| labor | 7.216 |
| media | 8.914 |
| space | 10.718 |
| transport | 6.791 |
| water | 10.000 |

## English Summary

This run models an Earth-Moon-Orbit Delta-Norm economy. Money is created from the spread between a contribution norm and a burden norm. Agents work, eat, consume, publish and consume news, maintain satellites and stations, pay wages, take loans, buy insurance, and receive protected basic access. The model exports CSV ledgers and a final JSON state for further analysis.
