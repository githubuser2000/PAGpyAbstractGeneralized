# Q-Economy: A Complete Economic System for a Line-Value Currency

**Language:** English  
**Version:** 1.0  
**Basis:** The currency consists of Q-coins. The row height is the coin value.

---

## 1. Core Idea

The Q-Economy is a semantic monetary, credit, and production order. It treats not only money as an economic unit, but also difficulty, structure, code, interfaces, architecture, operation, and finished modules.

One coin is one table row. **The row height** is its value. **The numbering** is its mint mark. The continuum text is its semantic backing.

```text
Coin Qn = (number n, value h, meaning B)
Value(Qn) = row height h
Meaning(Qn) = semantic content in the continuum
```

Q20 therefore does not mean “twenty units.” Q20 is the coin stamped with number 20 and valued at 4. Four Q1 coins may have the same nominal value as one Q20 coin, but they do not perform the same function.

---

## 2. Base Units

The base unit is called the **line value**.

```text
1 LV = 1 line value
```

A smaller unit can be the **octadegram**:

```text
1 LV = 18 octadegrams
```

Therefore:

```text
Value 1 = 1 LV = 18 octadegrams
Value 2 = 2 LV = 36 octadegrams
Value 3 = 3 LV = 54 octadegrams
Value 4 = 4 LV = 72 octadegrams
```

---

## 3. Coin Catalog

| Coin | Value | Layer | Economic meaning |
|---:|---:|---|---|
| Q1 | 1 | Basic difficulty | task, difficulty, knot, problem core |
| Q2 | 1 | Complexity | part, complication, molecular element, substructure |
| Q3 | 1 | Abstraction | theory, model, intermediate state between loose and fixed |
| Q4 | 1 | Crystallization | formal object, thread, mathematical form |
| Q5 | 2 | Operation | encoding, command, imperative programming |
| Q6 | 2 | Declaration | declarative description, rule, thread instead of command |
| Q7 | 2 | Delegation | delegating, referencing, transfer of responsibility |
| Q8 | 2 | Library | reusable stone, honeycomb, mineral, collection of building blocks |
| Q9 | 2 | Framework | frame, organic structure, general intelligence structure |
| Q10 | 3 | Constraint | limitation, structure, rope, possibility space |
| Q11 | 3 | Interface | intervention, interface, insertion of thought |
| Q12 | 3 | Toolbox | methods, mathematics, algebra, analysis, topology, category theory |
| Q13 | 3 | Program | service, paradigm, thought approach |
| Q14 | 3 | Orchestration | composition, choreography, conducting, mastery |
| Q15 | 3 | Application | application, work, opus |
| Q16 | 3 | Operation | menu, kernel, operating system, execution |
| Q17 | 4 | Compression | compression; inverse operation: decompression |
| Q18 | 4 | Architecture | construction, blueprint, load-bearing whole form |
| Q19 | 4 | Generation | generation; inverse movement: degeneration or decadence |
| Q20 | 4 | Module/Machine | finished development, device, pattern, difficulty machine |

The four value layers:

```text
Value 1: Q1–Q4     base coins
Value 2: Q5–Q9     operation coins
Value 3: Q10–Q16   system coins
Value 4: Q17–Q20   capital coins
```

---

## 4. Addition, Wealth, and Portfolios

Coins can be added. The first addition is the line value.

Example:

```text
2 × Q1
1 × Q8
3 × Q10
1 × Q20
```

Nominal value:

```text
2 × 1 LV = 2 LV
1 × 2 LV = 2 LV
3 × 3 LV = 9 LV
1 × 4 LV = 4 LV
Total value = 17 LV
```

In octadegrams:

```text
17 LV × 18 = 306 octadegrams
```

Portfolio:

```text
Wallet = (Q1:2, Q8:1, Q10:3, Q20:1)
Value = 17 LV
```

Important: equal nominal value does not mean equal semantic function.

```text
4 × Q1 = 4 LV
1 × Q20 = 4 LV
but: 4 × Q1 ≠ 1 × Q20
```

Four task cores are not yet a finished machine. A finished machine may be decomposed into task cores, but it is not identical to them.

---

## 5. Debts and Inverse Operations

Debts are negative coin balances.

```text
-1 × Q18 = I owe one architecture unit
```

An account may be nominally positive but semantically endangered:

```text
+3 × Q5 -1 × Q10
```

Nominally:

```text
3 × Q5 = 6 LV
-1 × Q10 = -3 LV
Net = +3 LV
```

Semantically, Q10 is missing: structure and constraint are missing.

> An actor can be nominally rich and semantically illiquid.

Debt and inverse operation are different:

```text
-Q17  = debt of compression
1/Q17 = decompression
-Q19  = debt of generation
1/Q19 = degeneration
```

Four kinds of debt:

| Debt type | Meaning | Example |
|---|---|---|
| Value debt | only an amount of value is owed | 10 LV |
| Height debt | a value class is owed | three coins of height 2 |
| Type debt | a specific coin type is owed | 2 × Q10 |
| Project debt | a concrete deliverable is owed | Q13 service with Q11 interface |

---

## 6. Accounts, Balance Sheets, and Wealth

An account is not a single balance but a vector of 20 coin types.

```text
Account A:
Q1:  10
Q2:   5
Q3:   2
Q5:   8
Q6:  -1
Q8:   3
Q9:   1
Q10: -2
Q20:  1
```

Negative values are debts. The account is read in two ways:

```text
Nominal reading = sum of all balances × line value
Semantic balance = surpluses and deficits by coin type
```

Three forms of wealth:

1. **Nominal wealth:** total value in LV.
2. **Semantic wealth:** ownership of the right coin types for real action.
3. **Liquidity wealth:** ability to pay due debts in the correct coin type.

A company with much Q5 and Q13 owns much code and many services. If it owes Q10, Q16, and Q18, it carries structural, operational, and architectural debt.

---

## 7. Markets

The Q-Economy needs several markets.

### Coin Market

Q-coins are exchanged against one another:

```text
1 × Q20 for 4 × Q1
1 × Q18 for 2 × Q5
1 × Q13 for 1 × Q10
```

A trade can be nominally balanced but semantically unbalanced.

### Labor Market

Humans or agents sell work:

```text
Q5 work: coding
Q6 work: specification
Q10 work: constraints and structure
Q11 work: interfaces
Q18 work: architecture
Q20 work: module building
```

### Goods Market

Products and services have a Q-signature. Example:

```text
Analysis service:
Q10: 2
Q11: 1
Q12: 1
Q13: 2
Q16: 1
```

### Credit Market

Claims and debts are traded here.

```text
A owes B 5 × Q18.
B sells the claim to C.
C pays less than nominal value because of default risk.
```

### Futures Market

Future deliveries are traded.

```text
Delivery in 30 days: 3 × Q13 + 1 × Q16
Price today: 12 LV
```

### Insurance Market

Insurance covers failures of specific coin types, especially Q16, Q18, and Q20.

### Commons Market

Q8, Q9, Q12, and Q16 are often commons. Libraries, frameworks, tools, and infrastructure need partly public or collective funding.

---

## 8. Prices and Exchange Rates

There is a nominal price and a market price.

```text
Nominal price(Qi) = line value h(Qi)
```

The market price arises from scarcity, quality, urgency, and trust:

```text
Market price(Qi) =
Nominal value(Qi)
× scarcity
× quality factor
× urgency factor
× trust factor
```

Example:

```text
Q18 nominal = 4 LV
scarcity: ×1.5
quality: ×1.2
urgency: ×1.3
trust: ×1.1
market price = 4 × 1.5 × 1.2 × 1.3 × 1.1 = 10.296 LV
```

For type debts, equal nominal value is not enough. Whoever owes Q18 cannot automatically pay with Q17. The creditor may define a semantic haircut:

```text
1 × Q17 counts as 60% substitute for 1 × Q18
```

---

## 9. Production and Production Recipes

Production means transforming difficulty into structured, executable, and reusable forms.

Main value chain:

```text
Q1 task
→ Q2 decomposition
→ Q3 abstraction
→ Q4 formal form
→ Q5/Q6 programming or specification
→ Q8/Q9 reuse and framework
→ Q10/Q11 structure and interface
→ Q13 service
→ Q15 application
→ Q18 architecture
→ Q20 machine/module
```

Production recipes:

```text
Output Q5 coding:
Q1 task + Q3 model + labor time

Output Q6 specification:
Q1 task + Q3 abstraction + Q10 constraint

Output Q8 library:
several Q5 + at least one Q6 + Q12 tool competence + Q17 compression

Output Q9 framework:
Q8 libraries + Q10 constraints + Q11 interfaces + Q13 service logic

Output Q13 service:
Q5 code + Q6 specification + Q10 constraints + Q11 interface + Q8 library

Output Q18 architecture:
Q10 constraints + Q11 interfaces + Q14 orchestration + Q17 compression + Q3/Q4 form

Output Q20 module/machine:
Q13 program + Q15 application + Q16 operation + Q18 architecture + Q19 generation
```

---

## 10. Money Creation and the Mint

New coins are not created arbitrarily. They are minted when a performance has been verified and recognized.

```text
validated architecture → new Q18 coins
validated service → new Q13 coins
validated module → new Q20 coins
```

The mint has five tasks:

```text
1. mint coins
2. destroy coins
3. classify coin types
4. prevent counterfeiting
5. secure price stability
```

The currency is backed not by gold but by **verified semantic work**.

Validators inspect work:

```text
Q5 validator checks code.
Q6 validator checks specifications.
Q10 validator checks constraints.
Q18 validator checks architecture.
Q20 validator checks module maturity.
```

False validation leads to reputation loss and penalty debts.

---

## 11. Banks, Credit, and Interest

Banks issue credit, but they do not automatically create real value. Credit creates purchasing power; backing arises only through productive work.

Example:

```text
Bank lends firm F:
3 × Q18
2 × Q13

Firm F receives:
+3 Q18 +2 Q13

At the same time there arises:
-3 Q18 -2 Q13 plus interest
```

Interest arises from time, risk, scarcity, and semantic difficulty:

```text
Interest(Qi) =
base rate
+ default risk
+ scarcity surcharge
+ complexity surcharge
- collateral discount
```

High coins such as Q18 and Q20 often carry higher interest because their failure can damage entire systems.

---

## 12. Technical Debt as Real Debt

Technical debt is booked as real Q-debt.

| Debt | Meaning |
|---|---|
| -Q1 | unsolved basic task |
| -Q2 | undecomposed problem |
| -Q3 | missing model |
| -Q4 | missing formal precision |
| -Q5 | missing implementation |
| -Q6 | missing specification |
| -Q7 | unclear responsibility |
| -Q8 | missing library or reuse |
| -Q9 | missing framework |
| -Q10 | missing constraints |
| -Q11 | broken interface |
| -Q12 | missing tool |
| -Q13 | missing service |
| -Q14 | coordination debt |
| -Q15 | undelivered application |
| -Q16 | operational or runtime debt |
| -Q17 | uncompressed complexity |
| -Q18 | architectural debt |
| -Q19 | missing generative capability |
| -Q20 | missing module or unfinished machine |

A project with much Q5 but negative Q10 and Q18 looks productive but is structurally sick.

```text
+20 Q5
-10 Q10
-5 Q18
```

This means: much code, bad structure, bad architecture.

---

## 13. Actors, Division of Labor, and Capabilities

Actors are households, firms, banks, validators, the state, commons funds, and foreign trade partners.

Capabilities are described as a Q-profile:

```text
Agent A:
Q1: 0.8
Q2: 0.7
Q3: 0.5
Q5: 0.9
Q6: 0.4
Q10: 0.3
Q18: 0.1
```

This means: strong in recognizing and coding, weak in structure and architecture.

Professions emerge along coin types:

```text
Q1/Q2 analyst: finds and decomposes problems
Q3/Q4 theorist: models and formalizes
Q5 programmer: implements
Q6 specifier: describes declaratively
Q7 coordinator: delegates and references
Q8 librarian: builds reusable components
Q9 framework builder: creates frames
Q10 constraint engineer: sets limits and structure
Q11 interface designer: connects systems
Q12 toolsmith: builds tools
Q13 service builder: creates services
Q14 orchestrator: composes processes
Q15 application builder: builds usable works
Q16 operations engineer: keeps execution stable
Q17 compressor: condenses complexity
Q18 architect: constructs load-bearing forms
Q19 generator builder: builds generative systems
Q20 module builder: delivers finished machines
```

---

## 14. State, Taxes, and Commons

The state protects the currency, stabilizes crises, and funds commons. Taxes can be collected in LV:

```text
income tax: percentage of nominal value
transaction tax: small levy on market trades
debt levy: surcharge on risky Q18/Q20 leverage
```

Public spending especially supports:

```text
Q8 libraries
Q9 frameworks
Q12 tools
Q16 infrastructure
education
validation
public safety
```

Antimonopoly rules matter because Q8, Q9, Q16, Q18, and Q20 can control the conditions of production. Tools include open interfaces, interoperability obligations, compulsory licenses, commons contributions, and, if necessary, break-ups.

---

## 15. Inflation, Deflation, and Crises

Inflation here does not only mean rising prices. It means a coin type is multiplied without sufficient semantic backing.

```text
Q5 inflation  = much code without specification, constraints, and architecture
Q13 inflation = many services without reliability
Q18 inflation = claimed architecture without load-bearing construction
Q20 inflation = unfinished modules sold as machines
```

Deflation means: there are too few valid coins for existing tasks. Example: many Q1 tasks, but too little Q5, Q10, and Q18.

Typical crisis:

```text
Q5:  very high
Q13: high
Q15: high
Q10: low
Q16: low
Q18: low
```

This means: much code and many applications, but too little structure, operation, and architecture. The crisis appears as outages, integration problems, security gaps, and maintenance backlog.

Crisis policy must not blindly print money. It must strengthen the missing coin types.

---

## 16. Quality, Reputation, and Ownership

Not every coin of the same type has the same quality. Quality classes:

```text
A = verified, stable, reusable
B = usable, but limited
C = experimental
D = problematic
F = invalid or failed
```

Q18-A is more valuable than Q18-C, although both are nominally worth 4 LV.

Reputation is tracked by coin type:

```text
Agent A:
Q5 reputation: 90
Q6 reputation: 60
Q10 reputation: 45
Q18 reputation: 20
```

Ownership exists in coins, artifacts, and usage rights:

```text
coin ownership: 5 × Q10
artifact ownership: program, library, machine
usage right: license to Q8, Q9, or Q20
```

---

## 17. Licensing Economy and Task Trading

Q8 libraries, Q9 frameworks, Q13 services, Q15 applications, and Q20 modules can be licensed.

Example:

```text
Q8 library:
one-time use: 1 LV
commercial use: 2 Q5 per month
open commons license: publicly funded
```

Tasks can also be traded. Q1 is raw material: a good task, research question, or customer requirement can be bought and sold. A good task is valuable because it can become the basis of a Q1→Q20 chain.

---

## 18. Value Chain Q1 → Q20 and Intelligence

The central economic movement:

```text
Q1 → Q20
task → machine
```

Complete chain:

```text
Q1  recognize task
Q2  decompose task
Q3  form model
Q4  formalize
Q5  implement
Q6  declare
Q7  delegate
Q8  build library
Q9  create framework
Q10 set constraints
Q11 build interfaces
Q12 provide tools
Q13 create service
Q14 orchestrate services
Q15 build application
Q16 secure operation
Q17 compress complexity
Q18 construct architecture
Q19 enable generation
Q20 deliver module/machine
```

Intelligence is transformation capability:

```text
Intelligence = ability to transform Q1 into higher Q-forms
```

Low transformation:

```text
Q1 → Q5 = task becomes code
```

High transformation:

```text
Q1 → Q18 → Q19 → Q20 = task is architecturally framed, made generative, and delivered as machine
```

---

## 19. Exchange, Price Index, Money Supply, and Insolvency

On the Q-exchange, coins have market prices. Example:

| Coin | Nominal | Market price |
|---:|---:|---:|
| Q1 | 1 | 0.8 |
| Q5 | 2 | 2.4 |
| Q8 | 2 | 3.1 |
| Q10 | 3 | 5.0 |
| Q13 | 3 | 3.6 |
| Q18 | 4 | 9.5 |
| Q20 | 4 | 7.8 |

The Q-price index measures a typical development cycle:

```text
4 × Q1
2 × Q5
2 × Q8
2 × Q10
1 × Q13
1 × Q16
1 × Q18
1 × Q20
```

Money supply is measured by coin type:

```text
M(Q18) = amount of valid Q18 coins
L(Q18) = outstanding debt in Q18
```

Dangerous:

```text
L(Q18) very high
M(Q18) low
```

This is an architectural debt crisis.

Insolvency can be nominal or semantic. Nominal insolvency means total debts exceed total assets. Semantic insolvency means total value is sufficient, but the right coin types are missing.

---

## 20. Research, Foreign Trade, and the R-Continuum

Research mainly creates:

```text
Q1 new tasks
Q3 new abstractions
Q4 new formal objects
Q12 new tools
Q17 compressions
Q19 generative principles
```

Foreign trade connects the Q-Economy with other economies. Q8, Q9, Q13, Q15, Q18, and Q20 are especially exportable. Imports include raw materials, hardware, energy, data, labor, and capital.

The R-continuum is real execution or practical reality. Q-value becomes strongest when it passes into R-effect:

```text
Q18 architecture + Q20 module → real machine → R-value
Q13 service + Q16 operation → running service → R-benefit
```

---

## 21. Triple-Store Ledger, Contracts, and Simulation

Accounting is kept as a semantic triple-store ledger:

```text
(subject, predicate, object)
```

Examples:

```text
(Agent A, owns, 3 × Q10)
(Agent A, owes, 1 × Q18 to Agent B)
(Project P, requires, 2 × Q5)
(Project P, produces, 1 × Q13)
(Q17, inverse operation, decompression)
```

A contract contains:

```text
parties
deliverable
Q-signature
price
due date
quality grade
sanction
validation
```

Simulation runs in periods:

```text
1. Tasks emerge.
2. Actors choose actions.
3. Markets open.
4. Production happens.
5. Results are validated.
6. Coins are minted or rejected.
7. Payments are booked.
8. Debts are updated.
9. Prices are adjusted.
10. Reputation is updated.
11. State and mint react.
```

---

## 22. Laws of the Q-Economy

```text
1. Coin law: every Q-coin has a number, line value, and meaning.
2. Addition law: coin values add by row height.
3. Semantic law: equal nominal value does not mean equal function.
4. Debt law: negative coin balances are debts.
5. Inversion law: 1/Qi is inverse operation, -Qi is debt.
6. Production law: production transforms Q1 difficulty into higher Q-forms.
7. Validation law: new coins arise only from verified performance.
8. Price law: market prices arise from nominal value, scarcity, quality, risk, and trust.
9. Solvency law: health requires nominal and semantic solvency.
10. Stability law: high coins must be backed by structure, operation, and architecture.
```

---

## 23. Final Definition

The Q-Economy is a semantic monetary, credit, and production order.

Its currency consists of Q1 through Q20. The value of each coin is its row height. Coins can be added, exchanged, lent, and owed. Debts are negative Q-balances. Inverse operations are written as 1/Qi and are not debts.

Production is the transformation of difficulty into structured, executable, and reusable forms. Wealth arises when Q1 tasks are converted into real effects through Q5 code, Q10 structure, Q13 services, Q18 architecture, and Q20 modules.

Crises arise when nominal wealth and semantic solvency diverge. Stability arises through validation, open interfaces, good architecture, visible debts, and public commons.

**Core sentence:** This economy does not merely pay for labor. It pays for the successful transformation of difficulty into functioning intelligence.
