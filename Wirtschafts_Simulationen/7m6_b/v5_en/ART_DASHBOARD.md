# V6 UTF-8/ANSI Dashboard Guide

The dashboard intentionally shows the same vector economy from many angles. Its goal is not minimalism. Its goal is to make the central mechanics visible while the simulation runs.

## Color language

```text
green      = good, popular, or positive value
red        = risk, badness, loss, crisis, fraud, or harm
magenta    = popularity, media power, and the y-axis of the currency
yellow     = money, value, liquidity, and angle rotation
blue/cyan  = institutions, finance, supply chains, data flows, and infrastructure
```

## Major panels

### Macro cockpit

Shows GDP, money supply, inflation, unemployment, mean confidence, goodness, popularity, legitimacy, inequality, and angle spread.

### Money-mass river

Shows which actor class holds how much directed money: households, firms, banks, funds, governments, and central banks.

### Vector balance by actor class

Splits held purchasing power into x and y components:

```text
x = goodness / badness
y = popularity / unpopularity
```

### Vector compass

Displays the world money angle, representative cash angle, buy angle, and sell angle on the good/bad and popular/unpopular axes.

### Angle liquidity wheel

Shows liquidity around the full 360-degree circle for cash, buy angles, sell angles, and missing opposite-side liquidity.

### Circular order book

Shows buy-bid depth and sell-ask depth by angle segment. This is the market where directions themselves become tradable.

### Order execution ladder

Pairs buyers and sellers, comparing the buyer's buy angle with the seller's sell angle. The compatible value is roughly:

```text
min(cash) · confidence · cos(delta_angle / 2)
```

### Triadic trade panels

Show trading among value, goodness, and popularity:

```text
value -> goodness
value -> popularity
popularity -> goodness
goodness -> popularity
```

This makes the politically dangerous question explicit: can goodness be bought with value and popularity, or only earned credibly?

### Financial-system map

Shows credit, bonds, equities, mortgages, insurance, FX, defaults, dividends, reserve interventions, and financial flows.

### Firm map and sector heatmap

Show firms and sectors on the goodness × popularity plane, weighted by value.

### Supply-chain matrix

Shows how a product inherits angles from intermediate inputs such as energy, data, raw materials, media, software, transport, and services.

### Corporate network panel

Shows holding groups, subsidiaries, opacity, tax havens, transfer pricing, and the attack surface for separating value from provenance and goodness.

### Oracle divergence

Compares government/court angles, people/media angles, and currency angles. Large divergence means legitimacy risk.

### Constitutional safety board

Shows court independence, constitution score, minority protection, corruption, regulatory capture, propaganda, contract disputes, and overrides.

### Crisis seismograph

Tracks early signals such as inflation, unemployment, legitimacy gap, angle volatility, angle laundering, black-market volume, capital flows, and pollution change.

## Width safety

Every panel is capped to detected terminal width minus five characters. Long text is wrapped inside the frame. ANSI color codes do not count toward visible width.
