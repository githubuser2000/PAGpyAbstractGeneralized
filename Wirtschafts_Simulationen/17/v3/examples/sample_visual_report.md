# Q Economy Simulation – colorful UTF-8 art report

This report replaces dry terminal output with many colorful UTF-8 art panels. Every panel
first explains what is being simulated and why that view matters. An interpretation
follows after the drawing so the chart remains economically readable instead of merely
decorative.

The colors are intentionally strong: rainbow bars represent positive quantities,
production, employment or distribution; risk and debt indicators move from green through
yellow/orange to red. In the terminal version ANSI colors are added; in plain files the
colors remain as UTF-8/emoji blocks.

## UTF-8 Art 01 – Macro cockpit

### What is simulated, and why?
The final state of the whole economy is simulated: BQP, price level, inflation,
unemployment, positive Q money, Q debt, credit stock and inequality. This view matters
because it shows whether the economy is merely large or actually viable. In a Q economy,
high turnover is not enough; money, debt, labor and the semantic coin structure must fit
together.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🌈 Q Economy Simulation                                                                ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Scenario: balanced             Periods: 8     Households: 50    Firms: 20    Banks: 2… ║
║ BQP / market turnover  🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛  241.36 ZW ║
║ Price index            🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  1.26      ║
║ Unemployment           ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  0.0 %     ║
║ Inflation last period  🟩🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  2.1 %     ║
║ Positive Q money       🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧  5.89 Tsd… ║
║ Q debt                 ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  10.16 ZW… ║
║ Credit stock           🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  138.35 ZW ║
║ Household Gini         🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛  0.04      ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
The cockpit shows the final state of the simulation. The decisive point is the
simultaneous reading of real turnover, Q money, Q debt, employment and the price level.
These indicators must not be read in isolation: an economy can have high turnover and
still be semantically unhealthy if its debt sits in Q16, Q18 or Q20. Debt appears
relatively low. That leaves room for productive investment as long as money is not
concentrated only in low coins.

## UTF-8 Art 02 – BQP time path

### What is simulated, and why?
The time path of the Brutto-Q-Produkt, roughly the market value movement in the
simulation, is tracked over all periods. This is not a strict national-accounting GDP; it
is the simulated market turnover and value creation. The curve matters because it shows
whether production and demand grow, stagnate or break down during crises.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 📈 BQP time path                                                                       ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ BQP                    █▄▂▂▁▃▅▃                                                        ║
║                        Start 313.12 ZW │ End 241.36 ZW │ Min 204.62 ZW │ Max 313.12 ZW ║
║ Transactions           ▆▅▁▅▅██▄                                                        ║
║                        Start 635.00 │ End 602.00 │ Min 563.00 │ Max 656.00             ║
║ Exports                █▄▃▁▁▂▁▂                                                        ║
║                        Start 28.40 ZW │ End 4.19 ZW │ Min 0.61 ZW │ Max 28.40 ZW       ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
BQP fell from 313.12 ZW to 241.36 ZW; the observed range was between 204.62 ZW and 313.12
ZW. The direction is generally burdensome for this indicator. Transactions fell from
635.00 to 602.00; the observed range was between 563.00 and 656.00. The direction is
generally burdensome for this indicator. Read the BQP line together with transactions and
exports. If BQP rises while transactions fall, a few expensive goods or export channels
may dominate. If BQP falls while transactions continue, the economy is busy but value-
poor, which often means wrong prices, shortages or low productivity.

## UTF-8 Art 03 – Money, credit and debt

### What is simulated, and why?
Monetary carrying capacity is simulated: positive Q money, Q debt, credit stock, new
lending, repayments and default losses. The view is necessary because this economy has
semantic debt. Debt is especially critical when it appears in operation, architecture or
machine capability.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 💳 Money, credit and debt                                                              ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Positive Q money       ▁▂▃▄▅▆▇█                                                        ║
║                        Start 5.42 Tsd. ZW │ End 5.89 Tsd. ZW │ Min 5.42 Tsd. ZW │ Max… ║
║ Q debt                 ▁▁▁▁▁▁▁█                                                        ║
║                        Start 0.00 ZW │ End 10.16 ZW │ Min 0.00 ZW │ Max 10.16 ZW       ║
║ Credit stock           ▁▂▂▅▆▃▆█                                                        ║
║                        Start 54.53 ZW │ End 138.35 ZW │ Min 54.53 ZW │ Max 138.35 ZW   ║
║ Default losses         ▄▄▄▄▄▄▄▄                                                        ║
║                        Start 0.00 ZW │ End 0.00 ZW │ Min 0.00 ZW │ Max 0.00 ZW         ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
Positive Q money rose from 5.42 Tsd. ZW to 5.89 Tsd. ZW; the observed range was between
5.42 Tsd. ZW and 5.89 Tsd. ZW. The direction is generally favorable for this indicator. Q
debt rose from 0.00 ZW to 10.16 ZW; the observed range was between 0.00 ZW and 10.16 ZW.
The direction is generally burdensome for this indicator. Credit stock rose from 54.53 ZW
to 138.35 ZW; the observed range was between 54.53 ZW and 138.35 ZW. A healthy credit path
creates the right Q coins later. Credit that only creates liquidity while widening Q10,
Q16 or Q18 gaps becomes a structural crisis. Defaults are not just financial losses; they
reveal missing ability to deliver promised coin types.

## UTF-8 Art 04 – Labor market and wages

### What is simulated, and why?
The labor market is simulated through employment, unemployment, average wage and the
distribution across all labor types. This matters because the model is a full economy:
agriculture, construction, care, trade, industry, energy, research, software/AI and many
other forms of work. Labor here is social production capacity, not only intelligence work.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 👥 Labor market and wages                                                              ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Unemployment           ▄▄▄▄▄▄▄▄                                                        ║
║                        Start 0.0 % │ End 0.0 % │ Min 0.0 % │ Max 0.0 %                 ║
║ Employed               ▄▄▄▄▄▄▄▄                                                        ║
║                        Start 50.00 │ End 50.00 │ Min 50.00 │ Max 50.00                 ║
║ Wage                   ▁████▇▃▄                                                        ║
║                        Start 3.97 ZW │ End 4.26 ZW │ Min 3.97 ZW │ Max 4.67 ZW         ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 👷 Labor market and wages                                                              ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Labor type                    Employment                               Wage            ║
║ ────────────────────────────  ───────────────────────────────────  ──────────────────… ║
║ Management/Organisation       🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩   11                  … ║
║ Ingenieurwesen                🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛    8                  … ║
║ Software/KI/Automatisierung   🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛    7                  … ║
║ Forschung                     🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛    6                  … ║
║ Umweltarbeit                  🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛    5                  … ║
║ Recht/Verträge                🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    3                  … ║
║ Energiearbeit                 🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                  … ║
║ Bauarbeit                     🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                  … ║
║ Gesundheit                    🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                  … ║
║ Finanzwesen                   🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    2                  … ║
║ Industriearbeit               🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    1                  … ║
║ Bildung                       🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    1                  … ║
║ Einfache körperliche Arbeit   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Landwirtschaft                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Rohstoffarbeit                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Handwerk                      ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Logistik                      ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Handel                        ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Gastgewerbe                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Pflege                        ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Wartung                       ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Kreative Arbeit               ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Öffentlicher Dienst           ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
║ Sicherheit                    ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛    0                  … ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
Unemployment remained largely stable from 0.0 % to 0.0 %; the observed range was between
0.0 % and 0.0 %. Average wage rose from 3.97 ZW to 4.26 ZW; the observed range was between
3.97 ZW and 4.67 ZW. The direction is generally favorable for this indicator. The
employment bars show whether the economy works broadly or overuses single areas. A healthy
system needs food, energy, construction, care, logistics, education, maintenance and
public service besides software and AI. High unemployment with high shortages points to
mismatched skills or sectoral allocation, not to a lack of needs.

## UTF-8 Art 05 – Price level and inflation

### What is simulated, and why?
Price index and inflation are simulated across periods. This view matters because price
pressure in a Q economy is not only a money-supply problem. It can come from real goods
shortages, wrong Q structure, credit overextension or weak operating capacity.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🌡 Price level and inflation                                                           ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Price index            ▁▂▃▄▅▆▇█                                                        ║
║                        Start 1.06 │ End 1.26 │ Min 1.06 │ Max 1.26                     ║
║ Inflation last period  █▁▂▂▃▂▂▂                                                        ║
║                        Start 6.4 % │ End 2.1 % │ Min 1.7 % │ Max 6.4 %                 ║
║ Imports                ▇▂▅▁█▂▁▄                                                        ║
║                        Start 93.52 ZW │ End 87.38 ZW │ Min 82.25 ZW │ Max 96.53 ZW     ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
Price index rose from 1.06 to 1.26; the observed range was between 1.06 and 1.26. The
direction is generally burdensome for this indicator. Inflation last period fell from 6.4
% to 2.1 %; the observed range was between 1.7 % and 6.4 %. The direction is generally
favorable for this indicator. Imports can buffer shortages, but they are not an unlimited
rescue. Rising import values with persistent shortages point to a structural supply
problem. Deflation with high debt may be just as dangerous as inflation because debts
become harder to repair.

## UTF-8 Art 06 – Q coin matrix

### What is simulated, and why?
The full semantic balance of Q1 to Q20 is simulated: positive holdings, debts and market
prices. This matrix is the heart of the Q economy. It shows not just how much value exists
but which kind of value is missing or dominant. Four Q1 coins equal one Q20 nominally, but
they do not replace a finished machine.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🪙 Q coin matrix                                                                       ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Coin   Meaning                                  Assets                               … ║
║ ─────  ────────────────────────  ───────────────────────────────────  ───────────────… ║
║ Q01    Difficulty                🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩 987.27             … ║
║ Q02    Complexity                🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 306.75             … ║
║ Q03    Abstraction               🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 205.76             … ║
║ Q04    Crystallization           ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 4.22               … ║
║ Q05    Coding                    🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛ 690.06             … ║
║ Q06    Declaration               ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 3.94               … ║
║ Q07    Delegation                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 1.02               … ║
║ Q08    Library                   🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 207.05             … ║
║ Q09    Framework                 🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 83.40              … ║
║ Q10    Constraint                🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛ 641.92             … ║
║ Q11    Interface                 🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛ 533.46             … ║
║ Q12    Toolbox                   🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 302.38             … ║
║ Q13    Program/Service           🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛ 568.07             … ║
║ Q14    Orchestration             ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 2.97               … ║
║ Q15    Application               ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.81               … ║
║ Q16    Operation                 🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛ 651.82             … ║
║ Q17    Compression               ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 8.28               … ║
║ Q18    Architecture              🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛ 475.73             … ║
║ Q19    Generation                ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 16.94              … ║
║ Q20    Module/Machine            🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 201.11             … ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
The matrix reveals whether the economy is concentrated in low base coins, middle operation
coins or high system and capital coins. Red debt segments in Q16, Q18, Q19 or Q20 are
serious because they affect operation, architecture, generation and finished modules. High
Q5 holdings without Q10/Q18 cover indicate code or production bubbles.

## UTF-8 Art 07 – Q debt heatmap

### What is simulated, and why?
The concentration of Q debts by coin type is simulated. The heatmap matters because it
immediately shows where the semantic pressure sits. A Q1 debt is an unresolved task; a Q18
debt is missing architecture; a Q20 debt is missing module or machine maturity.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🔥 Q debt heatmap                                                                      ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Legend: green = almost no debt, yellow/orange = tense, red = strong semantic debt      ║
║ Q01🟩 0.0   Q02🟩 0.0   Q03🟩 0.0   Q04🟩 0.0                                          ║
║ Q05🟩 0.0   Q06🟩 0.0   Q07🟩 0.0   Q08🟩 0.0                                          ║
║ Q09🟩 0.0   Q10🟩 0.0   Q11🟥 10.2   Q12🟩 0.0                                         ║
║ Q13🟩 0.0   Q14🟩 0.0   Q15🟩 0.0   Q16🟩 0.0                                          ║
║ Q17🟩 0.0   Q18🟩 0.0   Q19🟩 0.0   Q20🟩 0.0                                          ║
║                                                                                        ║
║ Top debt coins: Q11 Interface 10.2 ZW │ Q1 Difficulty 0.0 ZW │ Q2 Complexity 0.0 ZW │… ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
The darkest or reddest fields are the first repair targets. They are not only financial
loads but missing capabilities. If top debts are system or capital coins, policy should
not merely stimulate demand; it should build structure, operation, architecture or module
capacity.

## UTF-8 Art 08 – Goods shortages

### What is simulated, and why?
The simulation shows which real goods and services were not sufficiently available. This
connects the Q system to ordinary economic supply: food, energy, housing, health,
education, transport, industry, culture, security and other goods. A currency remains
abstract unless it translates into real provision.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🧺 Goods shortages                                                                     ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Kultur/Kreativität         │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩│ 24.9  Price… ║
║ Handelsleistung            │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛│ 20.2  Price… ║
║ Wartung                    │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛│ 17.0  Price… ║
║ Gastgewerbe                │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 14.2  Price… ║
║ Industriegüter             │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 13.4  Price… ║
║ Nahrung                    │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 12.2  Price… ║
║ Rohstoffe                  │🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 8.8  Price×… ║
║ Umwelt/Resilienz           │🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 6.5  Price×… ║
║ Öffentliche Leistung       │🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 5.9  Price×… ║
║ Bildungsleistung           │🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 5.9  Price×… ║
║ Transport/Logistik         │🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 5.2  Price×… ║
║ Energie                    │🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 4.2  Price×… ║
║ Forschung/Wissen           │🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 2.5  Price×… ║
║ Sicherheit                 │🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 2.2  Price×… ║
║ Gesundheitsleistung        │🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 2.0  Price×… ║
║ Finanzdienst               │🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 1.2  Price×… ║
║ Wohnraum/Bau               │🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.6  Price×… ║
║ Software/KI/Automatisieru… │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.1  Price×… ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
High shortages mean demand was not met by production, imports or public stabilization. The
price multiplier is crucial: a high shortage with a strong price increase is a hard supply
bottleneck; a high shortage without price reaction may show market inertia or public
buffering.

## UTF-8 Art 09 – Sector map

### What is simulated, and why?
The economic structure is simulated by sector: sales, profit, firm count and automation.
This matters because a complete economy cannot depend on one sector. Agriculture, raw
materials, energy, industry, construction, health, education, logistics, trade, finance,
public services, culture, maintenance, research, environment and security must interact.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🏭 Sector map                                                                          ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Sector                    Sales                                Profit                … ║
║ ────────────────────────  ────────────────────────────────  ─────────────────────────… ║
║ Software/KI/Automatisie…  🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩 35.6             🟩⬛⬛⬛…  ║
║ Umwelt/Resilienz          🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛ 31.2             🟥🟥🟥🟥…  ║
║ Industrie                 🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛ 21.5             🟩🟩🟩🟩…  ║
║ Bau                       🟥🟧🟨🟩🟦🟪🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛ 18.2             🟩🟩🟩🟩…  ║
║ Forschung                 🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛ 16.3             🟥🟥⬛⬛…  ║
║ Wartung                   🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛ 15.8             🟩🟩🟩🟩…  ║
║ Gesundheit                🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛ 15.7             🟩🟩🟩🟩…  ║
║ Finanzwesen               🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛ 14.5             🟥🟥🟥🟥…  ║
║ Kreativwirtschaft         🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 13.6             🟩🟩🟩🟩…  ║
║ Handel                    🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 12.9             🟩🟩🟩🟩…  ║
║ Energie                   🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 12.1             🟥🟥⬛⬛…  ║
║ Öffentlicher Dienst       🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 11.7             🟥🟥🟥⬛…  ║
║ Gastgewerbe               🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 10.9             🟩🟩🟩🟩…  ║
║ Sicherheit                🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 4.3              🟥🟥🟥⬛…  ║
║ Landwirtschaft            🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 3.9              🟩🟩🟩⬛…  ║
║ Rohstoffe                 🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 2.9              ⬛⬛⬛⬛…  ║
║ Bildung                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.0              ⬛⬛⬛⬛…  ║
║ Logistik                  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.0              ⬛⬛⬛⬛…  ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
The largest sales bars show where demand is concentrated. Profit bars show whether sectors
build capital or bleed out. Negative profit zones can point to input shortages, price
caps, weak demand or heavy debt. High automation is productive only if employment, skill
and Q10/Q16/Q18 structure keep pace.

## UTF-8 Art 10 – Government, banks and foreign trade

### What is simulated, and why?
Public finances, credit channels and foreign trade are simulated. The panel is needed
because crises do not arise only inside firms. Transfers, public purchases, loans,
repayments, defaults, exports and imports can stabilize or destabilize the whole economy.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🏦 Government, banks and foreign trade                                                 ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Tax revenue            │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 37.28 ZW     ║
║ Transfers              │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 20.00 ZW     ║
║ Public purchases       │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 20.87 ZW     ║
║ Gov. net worth         │🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 1.07 Tsd. ZW ║
║ Credit stock           │🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 138.35 ZW    ║
║ New credit             │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 36.67 ZW     ║
║ Repayments             │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 14.12 ZW     ║
║ Default losses         │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.00 ZW      ║
║ Exports                │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 4.19 ZW      ║
║ Imports                │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 87.38 ZW     ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
A viable state stabilizes without merely shifting debt. Public buying is productive when
it creates Q16 infrastructure, Q12 tools, education, health or commons. Banks are useful
when loans finance real transformation; they become dangerous when defaults rise and
credit hides semantic gaps.

## UTF-8 Art 11 – Households and inequality

### What is simulated, and why?
The distribution of household wealth is simulated. This matters because an economy can be
unstable even when totals look good if households lack access to work, education, health
or consumption. Inequality weakens demand, social stability and the ability to turn new Q1
tasks into productive work.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 👥 Households and inequality                                                           ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Household wealth distribution. Negative ranges show debt or poverty positions.         ║
║ 39.6 to 40.9                 │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│    4   ║
║ 40.9 to 42.3                 │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛│    8   ║
║ 42.3 to 43.7                 │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛│    9   ║
║ 43.7 to 45.0                 │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪│   10   ║
║ 45.0 to 46.4                 │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪🟥⬛⬛⬛⬛⬛│    8   ║
║ 46.4 to 47.8                 │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│    4   ║
║ 47.8 to 49.1                 │🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│    2   ║
║ 49.1 to 50.5                 │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦🟪⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│    5   ║
║                                                                                        ║
║ Average 44.47 ZW │ Minimum 39.57 ZW │ Maximum 50.52 ZW │ Gini 0.036                    ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
The distribution shows whether wealth is broad or concentrated. A high Gini does not
automatically mean collapse, but it means participation and demand are narrowing. In a Q
economy this is especially important because education and skills determine which coins
households can create.

## UTF-8 Art 12 – Capital and automation

### What is simulated, and why?
The simulation shows which sectors build capital stock and automation. This matters
because automation is not only software or AI. Industry, logistics, energy, construction,
health, administration, agriculture and maintenance can all become automated or capital-
intensive. It is productive only when human and institutional structures catch up.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🤖 Capital and automation                                                              ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Sector                    Auto                             Capital stock               ║
║ ────────────────────────  ─────────────────────────────  ───────────────────────────── ║
║ Industrie                 🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.24             🟥🟧🟨🟩🟦🟪…  ║
║ Finanzwesen               🟥🟧🟨⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.21             🟥🟧🟨🟩⬛⬛…  ║
║ Forschung                 🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.11             🟥🟧🟨🟩🟦🟪…  ║
║ Kreativwirtschaft         🟥🟧⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.11             🟥🟧🟨🟩🟦🟪…  ║
║ Bau                       🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.09             🟥🟧🟨🟩⬛⬛…  ║
║ Logistik                  🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.09             🟥🟧🟨🟩🟦🟪…  ║
║ Sicherheit                🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.08             🟥🟧🟨⬛⬛⬛…  ║
║ Bildung                   🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.07             🟥🟧🟨🟩🟦🟪…  ║
║ Wartung                   🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.06             🟥🟧🟨🟩🟦🟪…  ║
║ Handel                    🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.06             🟥🟧🟨🟩🟦⬛…  ║
║ Gesundheit                🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.04             🟥🟧🟨🟩🟦⬛…  ║
║ Landwirtschaft            🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.04             🟥🟧🟨⬛⬛⬛…  ║
║ Gastgewerbe               🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.04             🟥🟧🟨🟩🟦🟪…  ║
║ Umwelt/Resilienz          🟥⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.04             🟥🟧🟨🟩🟦🟪…  ║
║ Software/KI/Automatisie…  ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.04             🟥🟧🟨🟩⬛⬛…  ║
║ Rohstoffe                 ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.03             🟥🟧🟨🟩🟦⬛…  ║
║ Energie                   ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.02             🟥🟧🟨🟩🟦⬛…  ║
║ Öffentlicher Dienst       ⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛ 0.01             🟥🟧🟨🟩🟦⬛…  ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
Sectors with high capital and high automation can raise productivity strongly. They can
also displace employment or create Q16/Q18 debt if operation and architecture do not grow
with them. A healthy automation wave needs education, maintenance, interfaces and robust
operating infrastructure.

## UTF-8 Art 13 – Q1 to Q20 production chain

### What is simulated, and why?
The basic movement of the Q economy is simulated: task becomes division, model, form,
operation, system, architecture, generation and finally module or machine. This view is
justified because it makes the meaning of the coins visible. The economy does not only
produce goods; it transforms difficulty into functioning structure.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🧭 Q1 to Q20 production chain                                                          ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Base coins      Q1🟩 ── Q2🟩 ── Q3🟩 ── Q4🟩                                           ║
║                     │       │       │       │                                          ║
║ Operations       Q5🟩 ── Q6🟩 ── Q7🟩 ── Q8🟩 ── Q9🟩                                  ║
║                     │       │       │       │       │                                  ║
║ Systems          Q10🟩 ─ Q11🔴 ─ Q12🟩 ─ Q13🟩 ─ Q14🟩 ─ Q15🟩 ─ Q16🟩                 ║
║                     │       │       │       │       │       │       │                  ║
║ Capital          Q17🟩 ───────── Q18🟩 ───────── Q19🟩 ───────── Q20🟩                 ║
║                                                                                        ║
║ Read as: task → division → model → form → code/rule/delegation → structure/service/op… ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
The markers show which stations are solid and which are stressed. A break between Q5/Q13
and Q18/Q20 is especially critical: then there is much implementation or service activity
but too little architecture and module maturity. A break between Q1 and Q3 means tasks are
not understood or modeled well.

## UTF-8 Art 14 – Risk radar

### What is simulated, and why?
The crisis sensitivity of the economy is simulated across several stress axes:
unemployment, debt load, inflation, architecture and operation debt, goods shortages,
inequality and credit defaults. This matters because crises rarely emerge from one number;
they emerge from coupled weaknesses.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🚨 Risk radar                                                                          ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ Unemployment         │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.0 %  ║
║ Debt load            │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.00 … ║
║ Inflation pressure   │🟩🟩🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 2.1 %  ║
║ Q18 Architecture     │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.0 %  ║
║ Q16 Operation        │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.0 %  ║
║ Goods shortages      │🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥🟥│ 147.0… ║
║ Inequality           │🟩🟩⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.036… ║
║ Credit defaults      │⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛⬛│ 0.00 … ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
Red or long risk bars are the priority crisis channels. If several axes are high at once,
the response should not be one-dimensional. Money policy alone does not fix architecture
debt, and a job program alone does not fix an energy bottleneck. The Q economy requires
repair by coin type and sector.

## UTF-8 Art 15 – Event timeline

### What is simulated, and why?
The timeline simulates the sequence of important events: warnings, defaults, bankruptcies,
public programs and stress signals. This view matters because metrics show states while
events explain paths. A crisis rarely appears suddenly; it accumulates warning signs.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🕰 Event timeline                                                                      ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ P   0 │ 🟦init              │ Simulation initialisiert                                 ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
The timeline helps sort causes. Early clusters of warnings mean the final state was
prepared. Late clusters of defaults point to credit or liquidity stress. Many public
measures show that the state already acted as stabilizer and should be evaluated for
effectiveness.

## UTF-8 Art 16 – Policy map

### What is simulated, and why?
This panel simulates a prioritization of possible economic policy levers from the end
state. It does not claim automatic truth; it translates measured stress into possible
interventions such as debt restructuring, Q18 architecture programs, Q16 operating
infrastructure, public jobs, bottleneck investment, commons funds or import buffers.

```text
╔════════════════════════════════════════════════════════════════════════════════════════╗
║ 🛠 Policy map                                                                          ║
╠════════════════════════════════════════════════════════════════════════════════════════╣
║ import/input buffer          │🟥🟧🟨🟩🟦🟪🟥🟧🟨🟩🟦⬛⬛⬛⬛⬛⬛⬛│ smooth short-term… ║
╚════════════════════════════════════════════════════════════════════════════════════════╝
```

### Interpretation
The policy map is a diagnostic translation, not a command. The main rule remains: do not
flood abstract money into a semantic coin gap. The missing coin type has to be repaired or
productively created.
