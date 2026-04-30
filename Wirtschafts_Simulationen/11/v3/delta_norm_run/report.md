# Delta-Norm Economy Simulation – Report

**Version:** 1.3.0  
**Days:** 180  
**People:** 300  
**Seed:** 42  
**Scenario:** baseline  
**Runtime:** 11.61 seconds  
**Language:** en  

## Mathematical Core

```text
mu(e) = lambda_d * ( ||Phi_d(e)||_+ - ||Phi_d(e)||_- )
```

Each behavior is mapped to a vector. The plus norm measures contribution; the minus norm measures burden. The difference is Delta money.

## Final Indicators

| Indicator | Start | End |
|---|---:|---:|
| Price index | 111.679 | 547.304 |
| Basic access price index | 160.664 | 628.644 |
| Positive money stock | 8887179.000 | 9273431.878 |
| Net money incl. liability | 8887179.000 | 9270057.129 |
| Liability | 0.000 | 3374.749 |
| Unemployment | 34.33% | 9.34% |
| Health | 0.841 | 0.023 |
| Stress | 0.277 | 0.999 |
| Trust | 0.641 | 1.000 |
| Gini positive money balances | 0.122 | 0.316 |
| Media truth | 0.761 | 0.869 |
| Media manipulation | 0.191 | 0.135 |
| Station safety | 0.689 | 0.607 |
| Orbit debris risk | 0.115 | 0.006 |

## Money Creation and Liability

- Created Delta: **813394.48 D**
- Destroyed Delta: **409490.90 D**
- Newly booked liability: **3374.75 D**
- Disputed events: **3156**, successful appeals: **1759**

## Delta by Domain

| Domain | Events | Gross Delta |
|---|---:|---:|
| water | 46258 | 193396.41 |
| media | 35886 | 134696.41 |
| space | 11906 | 121554.26 |
| labor | 29181 | 114698.92 |
| energy | 46313 | 96270.66 |
| health | 29053 | 79258.15 |
| culture | 2310 | 7280.82 |
| education | 3432 | 4822.48 |
| governance | 240 | 1287.44 |
| transport | 107 | 1064.21 |
| infrastructure | 1096 | 77.86 |
| finance | 1269 | -3038.52 |
| consumption | 17175 | -3237.77 |
| food | 46171 | -362817.29 |

## Most Frequent Actions

| Domain | Action | Count |
|---|---|---:|
| food | `eat_food` | 46156 |
| water | `use_water` | 46156 |
| energy | `use_energy` | 46156 |
| media | `consume_news` | 34265 |
| labor | `employee_work` | 29181 |
| health | `rest_and_recovery` | 24017 |
| consumption | `general_consumption` | 17137 |
| space | `life_support_consumption` | 11820 |
| health | `receive_healthcare` | 4954 |
| education | `learn_skill` | 3432 |
| culture | `community_culture` | 2310 |
| media | `publish_news` | 1620 |
| finance | `wage_arrears` | 1139 |
| infrastructure | `idle_capacity` | 1047 |

## Wealthiest Non-Market Actors

| Actor | Kind | Place | Positive money | Newly booked liability |
|---|---|---|---:|---:|
| ZEMO Public Council / Öffentlicher Fonds | public | Earth | 551021.67 | 0.00 |
| Mutual Risk & Life-Support Insurance | firm | Earth | 259764.81 | 0.00 |
| Delta Clearing Bank | firm | Earth | 205766.77 | 0.00 |
| Lunar Habitat Ring | infrastructure | Moon | 78213.04 | 0.00 |
| Earth Grid Backbone | infrastructure | Earth | 75000.00 | 0.00 |
| LEO Satellite Net | infrastructure | Orbit | 75000.00 | 0.00 |
| Orbital Research Station | infrastructure | Station | 75000.00 | 0.00 |
| Earth Energie Cooperative | firm | Earth | 10808.93 | 0.00 |
| Moon Energie Cooperative | firm | Moon | 10802.17 | 0.00 |
| Station Raumfahrt Cooperative | firm | Station | 10717.13 | 0.00 |
| Orbit Medien Cooperative | firm | Orbit | 10279.99 | 0.00 |
| Orbit Raumfahrt Cooperative | firm | Orbit | 9031.46 | 0.00 |

## Vulnerable People by Net Account

| Person | Place | Net | Health | Stress | Employed |
|---|---|---:|---:|---:|---|
| Juri Novak | Earth | 156.72 | 0.020 | 0.995 | yes |
| Lina Hoffmann | Earth | 159.68 | 0.022 | 0.995 | no |
| Aiko Dubois | Earth | 159.79 | 0.020 | 0.995 | no |
| Lina Sato | Earth | 160.54 | 0.024 | 0.995 | yes |
| Lina Yilmaz | Earth | 161.53 | 0.020 | 0.985 | no |
| Iris Rahman | Earth | 166.24 | 0.020 | 0.995 | no |
| Ada Ito | Earth | 174.59 | 0.024 | 0.995 | no |
| Kian Keller | Earth | 215.55 | 0.020 | 0.995 | no |
| Elena Yilmaz | Earth | 216.12 | 0.020 | 0.995 | no |
| Kian Ito | Earth | 217.51 | 0.024 | 0.995 | no |

## ZEMO Lambda Factors

| Domain | Lambda |
|---|---:|
| consumption | 0.869 |
| culture | 0.775 |
| education | 1.162 |
| energy | 4.704 |
| environment | 1.203 |
| finance | 1.042 |
| food | 5.007 |
| governance | 1.096 |
| health | 1.309 |
| infrastructure | 1.229 |
| labor | 1.136 |
| media | 1.403 |
| space | 10.015 |
| transport | 1.069 |
| water | 6.199 |

## Summary

This run models an Earth-Moon-Orbit Delta-Norm economy. Money is created from the spread between a contribution norm and a burden norm. Agents work, eat, consume, publish and consume news, maintain satellites and stations, pay wages, take loans, buy insurance, and receive protected basic access. The model exports CSV ledgers and a final JSON state for further analysis.
