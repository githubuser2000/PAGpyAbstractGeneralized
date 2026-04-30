# Delta-Norm-Wirtschaftssimulation – Bericht

**Version:** 1.1.0  
**Tage:** 180  
**Personen:** 300  
**Seed:** 42  
**Szenario:** baseline  
**Laufzeit:** 9.36 Sekunden  

## Mathematischer Kern

```text
mu(e) = lambda_d * ( ||Phi_d(e)||_+ - ||Phi_d(e)||_- )
```

Jedes Verhalten wird als Vektor abgebildet. Die Plusnorm misst Beitrag; die Minusnorm misst Belastung. Die Differenz ist Delta-Geld.

## Schlusskennzahlen

| Kennzahl | Start | Ende |
|---|---:|---:|
| Preisindex | 111.677 | 547.022 |
| Grundversorgungspreisindex | 160.657 | 628.652 |
| Positive Geldmenge | 8887181.293 | 9277053.762 |
| Netto-Geld inkl. Haftung | 8887181.293 | 9274105.805 |
| Haftung | 0.000 | 2947.957 |
| Arbeitslosigkeit | 34.33% | 10.81% |
| Gesundheit | 0.841 | 0.023 |
| Stress | 0.277 | 0.999 |
| Vertrauen | 0.641 | 1.000 |
| Gini positive Geldbestände | 0.122 | 0.306 |
| Medien-Wahrheit | 0.761 | 0.806 |
| Medien-Manipulation | 0.191 | 0.177 |
| Stationssicherheit | 0.689 | 0.579 |
| Orbit-Trümmerrisiko | 0.115 | 0.000 |

## Geldschöpfung und Haftung

- Geschaffenes Delta: **816466.18 D**
- Vernichtetes Delta: **408940.71 D**
- Neu gebuchte Haftung: **2947.96 D**
- Bestrittene Ereignisse: **3010**, erfolgreiche Einsprüche: **1713**

## Delta nach Domänen

| Domäne | Ereignisse | Brutto-Delta |
|---|---:|---:|
| water | 46290 | 193817.10 |
| media | 35911 | 134410.95 |
| space | 11995 | 125908.07 |
| labor | 29207 | 114431.58 |
| energy | 46344 | 96028.98 |
| health | 28923 | 78766.83 |
| culture | 2333 | 7235.20 |
| education | 3441 | 4778.84 |
| governance | 240 | 1282.81 |
| transport | 105 | 1157.37 |
| infrastructure | 810 | 133.77 |
| finance | 1056 | -2505.41 |
| consumption | 17008 | -2857.09 |
| food | 46205 | -362792.01 |

## Häufigste Handlungen

| Domäne | Handlung | Anzahl |
|---|---|---:|
| food | `eat_food` | 46190 |
| water | `use_water` | 46190 |
| energy | `use_energy` | 46190 |
| media | `consume_news` | 34291 |
| labor | `employee_work` | 29207 |
| health | `rest_and_recovery` | 23933 |
| consumption | `general_consumption` | 16970 |
| space | `life_support_consumption` | 11905 |
| health | `receive_healthcare` | 4909 |
| education | `learn_skill` | 3441 |
| culture | `community_culture` | 2333 |
| media | `publish_news` | 1620 |
| finance | `wage_arrears` | 953 |
| infrastructure | `idle_capacity` | 757 |

## Wohlhabendste Nicht-Markt-Akteure

| Akteur | Art | Ort | Positives Geld | Haftung |
|---|---|---|---:|---:|
| ZEMO Public Council / Öffentlicher Fonds | public | Earth | 551094.66 | 0.00 |
| Mutual Risk & Life-Support Insurance | firm | Earth | 261444.16 | 0.00 |
| Delta Clearing Bank | firm | Earth | 216024.40 | 0.00 |
| Earth Grid Backbone | infrastructure | Earth | 76527.41 | 0.00 |
| Lunar Habitat Ring | infrastructure | Moon | 75000.00 | 0.00 |
| LEO Satellite Net | infrastructure | Orbit | 75000.00 | 0.00 |
| Orbital Research Station | infrastructure | Station | 75000.00 | 0.00 |
| Moon Energie Cooperative | firm | Moon | 11554.36 | 0.00 |
| Orbit Medien Cooperative | firm | Orbit | 11420.86 | 0.00 |
| Earth Energie Cooperative | firm | Earth | 10856.09 | 0.00 |
| Station Raumfahrt Cooperative | firm | Station | 9156.84 | 0.00 |
| Orbit Raumfahrt Cooperative | firm | Orbit | 8631.21 | 0.00 |

## Verletzliche Personen nach Netto-Konto

| Person | Ort | Netto | Gesundheit | Stress | Beschäftigt |
|---|---|---:|---:|---:|---|
| Mika Nguyen | Earth | 147.27 | 0.020 | 0.995 | nein |
| Lina Sato | Earth | 160.29 | 0.020 | 0.995 | nein |
| Lina Hoffmann | Earth | 167.83 | 0.027 | 0.995 | nein |
| Lina Yilmaz | Earth | 175.68 | 0.024 | 0.995 | nein |
| Lina Schmidt | Earth | 190.72 | 0.020 | 0.995 | nein |
| Luis Hoffmann | Earth | 191.09 | 0.020 | 0.995 | nein |
| Mika Okafor | Earth | 191.68 | 0.025 | 0.995 | ja |
| Elena Yilmaz | Earth | 194.36 | 0.020 | 0.995 | nein |
| Sofia Mensah | Earth | 201.83 | 0.024 | 0.995 | nein |
| Mika Weber | Earth | 203.15 | 0.020 | 0.995 | nein |

## ZEMO-Lambda-Faktoren

| Domäne | Lambda |
|---|---:|
| consumption | 0.869 |
| culture | 0.775 |
| education | 1.163 |
| energy | 4.704 |
| environment | 1.203 |
| finance | 1.042 |
| food | 5.007 |
| governance | 1.096 |
| health | 1.309 |
| infrastructure | 1.229 |
| labor | 1.136 |
| media | 1.403 |
| space | 8.541 |
| transport | 1.069 |
| water | 6.199 |

## English Summary

This run models an Earth-Moon-Orbit Delta-Norm economy. Money is created from the spread between a contribution norm and a burden norm. Agents work, eat, consume, publish and consume news, maintain satellites and stations, pay wages, take loans, buy insurance, and receive protected basic access. The model exports CSV ledgers and a final JSON state for further analysis.
