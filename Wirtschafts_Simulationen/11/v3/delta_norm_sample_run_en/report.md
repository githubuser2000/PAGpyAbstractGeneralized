# Delta-Norm Economy Simulation – Report

**Version:** 1.3.0  
**Days:** 30  
**People:** 120  
**Seed:** 42  
**Scenario:** media_crisis  
**Runtime:** 1.04 seconds  
**Language:** en  

## Mathematical Core

```text
mu(e) = lambda_d * ( ||Phi_d(e)||_+ - ||Phi_d(e)||_- )
```

Each behavior is mapped to a vector. The plus norm measures contribution; the minus norm measures burden. The difference is Delta money.

## Scenario

- media_crisis: public trust starts lower.

## Final Indicators

| Indicator | Start | End |
|---|---:|---:|
| Price index | 112.525 | 314.452 |
| Basic access price index | 158.275 | 523.463 |
| Positive money stock | 8774833.534 | 8893375.529 |
| Net money incl. liability | 8774833.534 | 8893375.529 |
| Liability | 0.000 | 0.000 |
| Unemployment | 6.67% | 6.67% |
| Health | 0.847 | 0.676 |
| Stress | 0.280 | 0.612 |
| Trust | 0.501 | 0.718 |
| Gini positive money balances | 0.124 | 0.146 |
| Media truth | 0.925 | 0.472 |
| Media manipulation | 0.061 | 0.207 |
| Station safety | 0.716 | 0.766 |
| Orbit debris risk | 0.116 | 0.024 |

## Money Creation and Liability

- Created Delta: **153753.46 D**
- Destroyed Delta: **27521.34 D**
- Newly booked liability: **0.00 D**
- Disputed events: **243**, successful appeals: **134**

## Delta by Domain

| Domain | Events | Gross Delta |
|---|---:|---:|
| water | 3671 | 39419.89 |
| labor | 3132 | 28797.98 |
| energy | 3633 | 20543.08 |
| media | 2510 | 17328.99 |
| health | 1619 | 16888.41 |
| space | 1069 | 13983.53 |
| consumption | 2682 | 1805.74 |
| culture | 195 | 1061.61 |
| education | 498 | 969.40 |
| transport | 32 | 454.85 |
| governance | 40 | 422.12 |
| infrastructure | 462 | 76.64 |
| finance | 4 | -19.94 |
| food | 3600 | -16091.17 |

## Most Frequent Actions

| Domain | Action | Count |
|---|---|---:|
| food | `eat_food` | 3600 |
| water | `use_water` | 3600 |
| energy | `use_energy` | 3600 |
| labor | `employee_work` | 3132 |
| consumption | `general_consumption` | 2682 |
| media | `consume_news` | 2269 |
| space | `life_support_consumption` | 1050 |
| health | `receive_healthcare` | 911 |
| health | `rest_and_recovery` | 657 |
| education | `learn_skill` | 498 |
| infrastructure | `idle_capacity` | 427 |
| media | `publish_news` | 240 |
| culture | `community_culture` | 195 |
| water | `produce_water` | 71 |

## Wealthiest Non-Market Actors

| Actor | Kind | Place | Positive money | Newly booked liability |
|---|---|---|---:|---:|
| ZEMO Public Council / Öffentlicher Fonds | public | Earth | 470109.04 | 0.00 |
| Delta Clearing Bank | firm | Earth | 288133.06 | 0.00 |
| Mutual Risk & Life-Support Insurance | firm | Earth | 250936.90 | 0.00 |
| Lunar Habitat Ring | infrastructure | Moon | 76096.31 | 0.00 |
| Earth Grid Backbone | infrastructure | Earth | 75000.00 | 0.00 |
| LEO Satellite Net | infrastructure | Orbit | 75000.00 | 0.00 |
| Orbital Research Station | infrastructure | Station | 75000.00 | 0.00 |
| Earth Energie Cooperative | firm | Earth | 11526.64 | 0.00 |
| Earth Wasser Cooperative | firm | Earth | 11059.44 | 0.00 |
| DeepContext Review | media | Earth | 10211.66 | 0.00 |
| Station Gesundheit Cooperative | firm | Station | 10048.71 | 0.00 |
| Station Raumfahrt Cooperative | firm | Station | 9398.49 | 0.00 |

## Vulnerable People by Net Account

| Person | Place | Net | Health | Stress | Employed |
|---|---|---:|---:|---:|---|
| Malik Silva | Moon | 149.67 | 0.630 | 0.831 | yes |
| Juri Sato | Moon | 265.94 | 0.696 | 0.776 | yes |
| Ravi Rahman | Moon | 272.75 | 0.626 | 0.798 | yes |
| Zoe Nguyen | Moon | 297.01 | 0.666 | 0.798 | yes |
| Mira Novak | Moon | 329.20 | 0.698 | 0.624 | yes |
| Mira Schmidt | Moon | 340.90 | 0.719 | 0.667 | yes |
| Amal Nguyen | Station | 447.30 | 0.673 | 0.561 | yes |
| Mira Rahman | Station | 458.81 | 0.710 | 0.574 | yes |
| Kian Okafor | Station | 489.93 | 0.655 | 0.281 | yes |
| Aiko Silva | Station | 496.33 | 0.720 | 0.382 | yes |

## ZEMO Lambda Factors

| Domain | Lambda |
|---|---:|
| consumption | 5.518 |
| culture | 4.924 |
| education | 7.386 |
| energy | 9.190 |
| environment | 7.640 |
| finance | 6.622 |
| food | 9.626 |
| governance | 6.961 |
| health | 8.319 |
| infrastructure | 7.810 |
| labor | 7.216 |
| media | 8.914 |
| space | 10.718 |
| transport | 6.791 |
| water | 9.999 |

## Summary

This run models an Earth-Moon-Orbit Delta-Norm economy. Money is created from the spread between a contribution norm and a burden norm. Agents work, eat, consume, publish and consume news, maintain satellites and stations, pay wages, take loans, buy insurance, and receive protected basic access. The model exports CSV ledgers and a final JSON state for further analysis.
