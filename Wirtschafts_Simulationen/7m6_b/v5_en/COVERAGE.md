# Model Coverage — V6 English Edition

This simulation is a research scaffold, not a calibrated real-world macroeconomic model. Its purpose is to place the proposed vector currency into a dynamic economy where actors can trade value, goodness, popularity, and confidence under uncertainty.

## Core currency

```text
M = (amount, theta, confidence, origin, history)
theta = atan2(popularity, goodness)
```

The amount is scalar purchasing power and also the market weight of the angle. Confidence measures agreement and evidence quality.

## Actor coverage

- households and individuals
- firms and sectors
- banks and central banks
- governments and courts
- investment and pension funds
- rating agencies
- corporate groups and holding structures
- countries and jurisdictions
- people groups with ideologies, satisfaction, and anger

## Market coverage

- goods and services
- labor
- business-to-business supply chains
- credit and loans
- bonds
- equities
- mortgages
- insurance
- foreign exchange and capital flows
- real estate
- black markets
- angle rotation markets
- triadic value/goodness/popularity exchange

## Political and institutional coverage

- government good/bad evaluation
- people and media popular/unpopular evaluation
- courts, constitutional protections, and overrides
- corruption, regulatory capture, propaganda, lobbying, protests, elections, and legitimacy
- contract disputes and minority-harm tracking

## Adversarial coverage

- fraud
- angle laundering
- fake popularity
- weak transparency
- weak courts
- tax havens
- transfer pricing
- rating corruption
- black markets
- scandals, audits, strikes, defaults, shocks, and crises

## Environmental and social ledgers

- pollution
- carbon stock
- biodiversity
- health burden
- crime index
- privacy damage
- infrastructure quality
- social benefit

## Dashboard coverage

The V6 dashboard includes:

- macro cockpit
- money-mass river
- vector balance by actor class
- vector compass
- angle liquidity wheel
- circular order book
- buy/sell angle spread histogram
- order execution ladder
- triadic exchange panels
- market-flow diagram
- financial-system map
- actor two-angle table
- country panels
- oracle divergence
- constitutional safety board
- firm quadrant map
- sector heatmap
- sector economics
- supply-chain matrix
- corporate network panel
- media and popularity power map
- rating market panel
- demography and human-capital panel
- externality panel
- crisis seismograph
- event tape

## Simplifications

- The economy is stylized and not calibrated to real data.
- Accounting is stock-flow inspired but not a full deposit matrix for every bank-household relationship.
- Product bills of materials are sectoral input weights, not detailed item-level manufacturing plans.
- FX is an order-book approximation, not a tick-by-tick limit order book.
- Securities markets are institutional overlays, not full microstructure simulations.
- Demography is compact: age, retirement, death, migration, health, and human capital are represented without full family trees.
- Media and civil society are represented as influence mechanisms, not full social-network simulations.

These simplifications keep the model as one large runnable PyPy3-compatible file while preserving the central mechanics of the vector-currency idea.
