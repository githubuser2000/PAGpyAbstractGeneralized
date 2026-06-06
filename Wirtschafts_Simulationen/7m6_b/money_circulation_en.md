# How does money made of value, goodness level, and popularity level circulate when there are two angles?

Money no longer circulates as a simple stream from buyer to seller. It circulates as a **double stream**:

\[
\text{Goods/services flow from the seller to the buyer}
\]

\[
\text{Money flows from the buyer to the seller}
\]

Both streams have a direction in angle space.

The central point is:

\[
\boxed{
\text{Every trade is a double angle exchange.}
}
\]

The buyer does not merely buy a product.  
At the same time, the seller buys the buyer's money.

---

# 1. The money object

A unit of money does not consist only of value:

\[
M = m
\]

but of:

\[
M = (m,g,b,\rho,h)
\]

where:

\[
m = \text{numerical value}
\]

\[
g = \text{degree of goodness}
\]

\[
b = \text{degree of popularity}
\]

\[
\rho = \text{confidence / certainty of the evaluation}
\]

\[
h = \text{history / origin}
\]

The angle results from goodness and popularity:

\[
\theta = \operatorname{atan2}(b,g)
\]

So:

\[
g = \text{x-axis: good vs. evil}
\]

\[
b = \text{y-axis: popular vs. unpopular}
\]

The amount of money is:

\[
m
\]

The direction is:

\[
\theta
\]

The credibility of the direction is:

\[
\rho
\]

A payment is therefore not merely:

\[
100
\]

but for example:

\[
100 \angle 35^\circ,\quad \rho=0.82
\]

That means: 100 value units, with a specific goodness/popularity direction and a specific certainty.

---

# 2. Every actor has two angles

Every actor \(i\) has:

\[
\theta_i^K = \text{buy angle}
\]

\[
\theta_i^V = \text{sell angle}
\]

The best definition is:

\[
\boxed{
\theta_i^K = \text{the direction I want to receive}
}
\]

\[
\boxed{
\theta_i^V = \text{the direction I want to spend or sell}
}
\]

So:

- The **buy angle** is an input filter.
- The **sell angle** is an output signal.

An actor therefore becomes an **angle transformer**.

It receives things from one direction and emits things in another direction.

\[
\theta_i^K \rightarrow \theta_i^V
\]

If both angles are almost equal, the actor is coherent.

If they are far apart, the actor earns from, or lives from, angle transformation.

---

# 3. Every trade has two angle checks

Assume:

- Buyer \(A\) buys from seller \(B\).
- Seller \(B\) delivers a product or service.
- Buyer \(A\) pays money.

Then there are two flows:

```text
Product / service:
B ─────────────────────────▶ A

Money:
A ─────────────────────────▶ B
```

But now with angles:

```text
Product flow:
B sells with θ_B^V ─────▶ A receives with θ_A^K

Money flow:
A pays with θ_A^V ──────▶ B receives with θ_B^K
```

So two angle distances must fit:

\[
d_X = d(\theta_A^K,\theta_B^V)
\]

for the product stream.

And:

\[
d_M = d(\theta_B^K,\theta_A^V)
\]

for the money stream.

This is extremely important.

The buyer asks:

> Does the product I receive fit my buy angle?

The seller asks:

> Does the money I receive fit my buy angle?

Because for the seller, money is the received good.

---

# 4. Circular distance decides tradability

The distance between two angles is:

\[
d(\alpha,\beta)=\arccos(\cos(\alpha-\beta))
\]

So:

\[
d \in [0,\pi]
\]

Thus:

\[
d=0
\]

means perfect compatibility.

\[
d=\pi
\]

means maximum opposition.

A simple compatibility function would be:

\[
\phi(d)=\cos\left(\frac{d}{2}\right)
\]

Then:

\[
d=0 \Rightarrow \phi=1
\]

\[
d=\pi \Rightarrow \phi=0
\]

Trade becomes stronger the better the angles fit.

For a complete trade, both sides are needed:

\[
\Phi = \phi(d_X)\cdot \phi(d_M)\cdot \rho_X \cdot \rho_M
\]

where:

\[
d_X = \text{product angle distance}
\]

\[
d_M = \text{money angle distance}
\]

\[
\rho_X = \text{confidence of the product angle}
\]

\[
\rho_M = \text{confidence of the money angle}
\]

If \(\Phi\) is high, money circulates easily.

If \(\Phi\) is low, discounts, fees, insurance, audits, rotation, or no trade arise.

---

# 5. The trade as a process

A complete trade looks like this:

## Step 1: The buyer creates demand

Buyer \(A\) says:

\[
\text{I want a good with direction near } \theta_A^K
\]

For example:

\[
\theta_A^K = 30^\circ
\]

This means: the buyer seeks something that is good and reasonably popular.

## Step 2: The seller offers

Seller \(B\) says:

\[
\text{I sell a good with direction } \theta_B^V
\]

For example:

\[
\theta_B^V = 55^\circ
\]

Then the product distance is:

\[
d_X = 25^\circ
\]

This is relatively close. The buyer will likely accept.

## Step 3: The buyer offers payment

Buyer \(A\) does not pay with neutral money, but with money from his output angle:

\[
\theta_A^V
\]

For example:

\[
\theta_A^V = 80^\circ
\]

The money may be very popular, but only moderately good.

## Step 4: The seller checks payment

Seller \(B\) has a buy angle for incoming values:

\[
\theta_B^K
\]

For example:

\[
\theta_B^K = 70^\circ
\]

Then the money distance is:

\[
d_M = 10^\circ
\]

The money fits the seller well.

## Step 5: The trade is executed

If both distances are small enough:

\[
d_X \leq \varepsilon_X
\]

\[
d_M \leq \varepsilon_M
\]

then trade happens.

The buyer receives the product.

The seller receives the money.

But both receive not only value, but also angle quality.

---

# 6. What actually circulates?

Three things circulate at the same time:

\[
\boxed{
\text{Value}
}
\]

\[
\boxed{
\text{Goodness}
}
\]

\[
\boxed{
\text{Popularity}
}
\]

But they do not circulate in the same way.

## Value circulates through payment

\[
A \rightarrow B
\]

The buyer loses numerical value.

The seller gains numerical value.

## Goodness circulates through origin, production, and evaluation

Goodness arises or disappears through real actions:

- clean supply chains
- fair labor
- low harm
- good products
- repair of damage
- legality
- environmental effect
- social effect
- transparency
- audits
- courts
- government evaluation

Goodness is therefore not merely opinion. It is more strongly bound to real consequences and institutional review.

## Popularity circulates through acceptance and attention

Popularity arises through:

- demand
- customer satisfaction
- media
- trends
- advertising
- social networks
- cultural symbolism
- political camps
- boycotts
- protests
- influencers
- herd behavior

Popularity moves faster than goodness.

Therefore popularity can rise faster and crash faster.

---

# 7. The balance-sheet change for the buyer

Before the purchase, buyer \(A\) has:

\[
M_A = (m_A,g_A,b_A)
\]

He pays:

\[
\Delta M = (p,g_{\text{pay}},b_{\text{pay}})
\]

Then his money stock falls:

\[
m_A' = m_A - p
\]

His outgoing money direction is:

\[
\theta_A^V
\]

At the same time he receives a product:

\[
X = (u,g_X,b_X)
\]

with utility \(u\), goodness \(g_X\), popularity \(b_X\).

When the product is consumed, it does not simply become money. It changes:

- utility
- standard of living
- reputation
- future preferences
- political opinion
- demand
- possibly the actor's own productivity

For a household:

\[
\text{Product} \rightarrow \text{utility / satisfaction / opinion}
\]

For a firm:

\[
\text{Product} \rightarrow \text{input / supply chain / new production angle}
\]

This is important: if a firm buys a bad input, that bad angle can later enter its own product.

---

# 8. The balance-sheet change for the seller

Seller \(B\) gives up a product:

\[
X_B = (u,g_X,b_X)
\]

and receives money:

\[
M_{\text{in}} = (p,g_M,b_M)
\]

His money stock rises:

\[
m_B' = m_B + p
\]

But his money quality also changes:

\[
g_B' = g_B + g_M
\]

\[
b_B' = b_B + b_M
\]

His new cash angle becomes:

\[
\theta_B^{\text{cash}}=
\operatorname{atan2}(b_B',g_B')
\]

If many customers pay with good and popular money, the firm's cash is pulled in that direction.

If many customers pay with toxic money, the firm's cash is burdened.

That means:

\[
\boxed{
\text{Not only products have origin. Customer money also has origin.}
}
\]

---

# 9. Vector wallet: money is held as bundles

In practice, an actor should not store its wallet only as a sum.

It has many money lots:

\[
M_i = \{M_{i1},M_{i2},M_{i3},...\}
\]

Each lot has:

\[
(m,g,b,\rho,h)
\]

For example:

```text
Lot 1: 500 value, good angle, high confidence
Lot 2: 200 value, popular but questionable
Lot 3: 100 value, toxic, low confidence
```

When the actor pays, he chooses which money to spend.

This is called coin selection.

Possible strategies:

## Best money first

The actor pays with good money to get better prices.

## Worst money first

The actor tries to get rid of toxic money.

## Matching money first

The actor searches for money lots whose angles fit the seller's buy angle.

## Camouflage mixing

The actor mixes bad money with good money to create an acceptable average angle.

This is exactly where angle laundering emerges.

---

# 10. The seller can reject payment

The seller does not accept every kind of money equally.

He checks:

\[
d_M = d(\theta_B^K,\theta_A^V)
\]

If the money is too far from his buy angle, there are several possibilities:

## Rejection

\[
d_M > \varepsilon
\Rightarrow
\text{no trade}
\]

## Discount

The seller accepts the money, but only with a value loss:

\[
m_{\text{eff}} = m \cdot \phi(d_M)
\]

For example:

\[
100 \angle 160^\circ
\]

may count for him only as:

\[
62
\]

## Surcharge

The buyer must pay more:

\[
p_{\text{required}} = \frac{p}{\phi(d_M)}
\]

## Rotation

An angle trader or bank rotates the money for a fee:

\[
\theta_A^V \rightarrow \theta_B^K
\]

with cost:

\[
C_{\text{rot}}=\lambda m \tan^2\left(\frac{d_M}{2}\right)
\]

The greater the angle distance, the more expensive the rotation.

## Audit

The origin is checked. If the bad angle is based on false information, confidence or direction can be corrected.

---

# 11. The buyer can reject the product

At the same time, the buyer checks:

\[
d_X = d(\theta_A^K,\theta_B^V)
\]

If the product is too far from the desired buy angle:

## No purchase

The product remains unsold.

## Price discount

The seller must become cheaper.

## Product improvement

The seller invests in real improvement:

\[
\text{Value} \rightarrow \text{Goodness}
\]

## Marketing

The seller invests in perception:

\[
\text{Value} \rightarrow \text{Popularity}
\]

## Certification

The seller makes the angle more credible:

\[
\rho \uparrow
\]

This means: the product angle determines sales ability.

The money angle determines payment ability.

---

# 12. The two angles create four roles in every transaction

In every transaction there are four relevant angles:

\[
\theta_A^K = \text{buyer receives product}
\]

\[
\theta_A^V = \text{buyer gives money}
\]

\[
\theta_B^K = \text{seller receives money}
\]

\[
\theta_B^V = \text{seller gives product}
\]

This creates two matchings:

\[
\theta_A^K \leftrightarrow \theta_B^V
\]

for the good.

\[
\theta_B^K \leftrightarrow \theta_A^V
\]

for the money.

This is the complete circulation mechanics.

```text
                 Product angle
          θ_B^V ───────────────▶ θ_A^K
          Seller                  Buyer


                   Money angle
          θ_B^K ◀─────────────── θ_A^V
          Seller                  Buyer
```

A trade is stable when both links are short.

A trade is unstable when one link is short and the other is long.

---

# 13. Example: good trade

Buyer \(A\):

\[
\theta_A^K = 40^\circ
\]

\[
\theta_A^V = 60^\circ
\]

Seller \(B\):

\[
\theta_B^K = 55^\circ
\]

\[
\theta_B^V = 45^\circ
\]

Then:

\[
d_X = d(40^\circ,45^\circ)=5^\circ
\]

\[
d_M = d(55^\circ,60^\circ)=5^\circ
\]

Both sides fit.

The product fits the buyer.

The money fits the seller.

The trade is highly liquid.

\[
\Phi \approx 1
\]

Money circulates easily.

---

# 14. Example: the product fits, the money does not

Buyer \(A\):

\[
\theta_A^K = 40^\circ
\]

\[
\theta_A^V = 150^\circ
\]

Seller \(B\):

\[
\theta_B^K = 50^\circ
\]

\[
\theta_B^V = 45^\circ
\]

Then:

\[
d_X = d(40^\circ,45^\circ)=5^\circ
\]

The product fits.

But:

\[
d_M = d(50^\circ,150^\circ)=100^\circ
\]

The money does not fit.

Consequence:

- Buyer wants to buy.
- Seller wants to sell.
- But the seller distrusts the money.
- A surcharge, rotation, audit, or different money is needed.

This is like a payment problem despite existing purchasing power.

The buyer has value, but the wrong angle.

---

# 15. Example: the money fits, the product does not

Buyer \(A\):

\[
\theta_A^K = 30^\circ
\]

\[
\theta_A^V = 60^\circ
\]

Seller \(B\):

\[
\theta_B^K = 55^\circ
\]

\[
\theta_B^V = 150^\circ
\]

Then:

\[
d_M = d(55^\circ,60^\circ)=5^\circ
\]

The money fits.

But:

\[
d_X = d(30^\circ,150^\circ)=120^\circ
\]

The product does not fit.

Consequence:

- The seller would gladly take the money.
- The buyer does not want the product in that direction.
- The seller must improve, become cheaper, or find another buyer group.

This is a sales problem despite solvent customers.

---

# 16. Example: neither direction fits

Buyer \(A\):

\[
\theta_A^K = 20^\circ
\]

\[
\theta_A^V = 160^\circ
\]

Seller \(B\):

\[
\theta_B^K = 30^\circ
\]

\[
\theta_B^V = 170^\circ
\]

Then:

\[
d_X = d(20^\circ,170^\circ)=150^\circ
\]

\[
d_M = d(30^\circ,160^\circ)=130^\circ
\]

The product does not fit.

The money does not fit.

The trade probably does not happen — except in a shadow market or with extreme discounts.

---

# 17. Circulation as a transformation chain

Every actor receives incoming values close to its buy angle:

\[
\theta^K
\]

and emits outgoing values close to its sell angle:

\[
\theta^V
\]

Thus every actor is a kind of economic angle transformer:

\[
T_i:
(m,g,b)_{\text{in}}
\rightarrow
(m',g',b')_{\text{out}}
\]

or:

\[
\theta_i^K \rightarrow \theta_i^V
\]

Examples:

## Firm

Buys inputs and labor:

\[
\theta^K_{\text{firm}}
\]

produces goods:

\[
\theta^V_{\text{firm}}
\]

If it creates real quality:

\[
g \uparrow
\]

If it does good advertising:

\[
b \uparrow
\]

If it outsources harm:

\[
g \downarrow
\]

If it remains popular despite harm:

\[
b \uparrow,\quad g \downarrow
\]

## Household

Receives wages:

\[
\theta^K_{\text{household}}
\]

spends consumption money:

\[
\theta^V_{\text{household}}
\]

Its purchase decisions change the popularity of firms.

## Bank

Receives deposits:

\[
\theta^K_{\text{bank}}
\]

issues loans:

\[
\theta^V_{\text{bank}}
\]

It creates new money with an angle depending on borrower, purpose, and risk.

## Government

Receives taxes:

\[
\theta^K_{\text{state}}
\]

spends public money:

\[
\theta^V_{\text{state}}
\]

It can define goodness through laws and shift angles through spending.

## Media

Receive attention and money:

\[
\theta^K_{\text{media}}
\]

emit popularity or unpopularity:

\[
\theta^V_{\text{media}}
\]

They mainly influence \(b\), i.e. popularity.

## Courts / audits

Receive cases, evidence, and fees:

\[
\theta^K_{\text{court/audit}}
\]

emit confidence and goodness corrections:

\[
\theta^V_{\text{court/audit}}
\]

They mainly influence \(g\) and \(\rho\).

---

# 18. The most important circulation formula

For a transaction between buyer \(A\) and seller \(B\):

\[
d_X = d(\theta_A^K,\theta_B^V)
\]

\[
d_M = d(\theta_B^K,\theta_A^V)
\]

Then:

\[
\text{Trade volume}
=
Q \cdot \phi(d_X)\cdot \phi(d_M)\cdot \rho_X\cdot\rho_M
\]

Or compactly:

\[
Q_T = Q_0 \Phi
\]

with:

\[
\Phi =
\phi(d_X)\phi(d_M)\rho_X\rho_M
\]

If \(\Phi\) is high, much circulates.

If \(\Phi\) is low, little circulates.

If many actors have incompatible buy and sell angles, the liquidity of the whole economy falls.

---

# 19. How value buys goodness

Value can buy goodness, but only through real change.

For example:

\[
\text{Value} \rightarrow \text{better working conditions}
\]

\[
\text{Value} \rightarrow \text{clean energy}
\]

\[
\text{Value} \rightarrow \text{compensation for damage}
\]

\[
\text{Value} \rightarrow \text{product safety}
\]

\[
\text{Value} \rightarrow \text{supply-chain inspection}
\]

Then:

\[
g \uparrow
\]

A possible simulation rule:

\[
\Delta g
=
\eta_g \cdot \log(1+I_g)\cdot R_{\text{real}}\cdot \rho_{\text{audit}}
\]

where:

\[
I_g = \text{investment in real improvement}
\]

\[
R_{\text{real}} = \text{reality factor}
\]

\[
\rho_{\text{audit}} = \text{audit confidence}
\]

If a firm only claims to be good but makes no real improvement:

\[
R_{\text{real}} \approx 0
\]

Then, at most, popularity rises briefly, but not real goodness.

---

# 20. How value buys popularity

Value can buy popularity more easily:

\[
\text{Value} \rightarrow \text{advertising}
\]

\[
\text{Value} \rightarrow \text{discounts}
\]

\[
\text{Value} \rightarrow \text{influencers}
\]

\[
\text{Value} \rightarrow \text{media campaigns}
\]

\[
\text{Value} \rightarrow \text{sponsorship}
\]

Then:

\[
b \uparrow
\]

A possible simulation rule:

\[
\Delta b
=
\eta_b \cdot \log(1+I_b)\cdot M_{\text{media}}\cdot S_{\text{trend}}
-
B_{\text{backlash}}
\]

where:

\[
I_b = \text{advertising / PR spending}
\]

\[
M_{\text{media}} = \text{media amplification}
\]

\[
S_{\text{trend}} = \text{trend factor}
\]

\[
B_{\text{backlash}} = \text{backlash}
\]

Popularity is faster than goodness, but less stable.

Therefore often:

\[
b \uparrow,\quad g \text{ remains the same}
\]

or even:

\[
b \uparrow,\quad g \downarrow
\]

This is the case:

\[
\text{popular but evil}
\]

---

# 21. How popularity can buy goodness

Popularity cannot buy goodness directly, but it can make reforms easier.

A popular firm has:

- more customer trust
- more political capital
- easier access to employees
- more patience from investors
- higher pricing power
- less resistance to change

Then it can transform popularity into real reform capacity:

\[
b \rightarrow g
\]

For example:

\[
\Delta g
=
\eta_{bg}\cdot b \cdot I_g \cdot \rho
\]

But here too, real investment is required.

Popularity alone is not goodness.

It is only a resource with which goodness can be produced more easily.

---

# 22. How goodness can buy popularity

Goodness can generate popularity, but only if it becomes visible.

\[
g \rightarrow b
\]

This requires:

- transparency
- free media
- credible audits
- understandable communication
- education
- time
- trust

A possible rule:

\[
\Delta b
=
\eta_{gb}\cdot g \cdot T_{\text{visibility}}\cdot \rho
\]

where:

\[
T_{\text{visibility}} = \text{visibility}
\]

If nobody sees the goodness, popularity barely rises.

Therefore a good but invisible firm can remain unpopular.

---

# 23. The dangerous circulation: angle laundering

Angle laundering arises when someone turns bad value into a better apparent angle.

For example:

\[
1000 \angle 160^\circ
\rightarrow
900 \angle 40^\circ
\]

but without real improvement.

This can happen through:

- subsidiaries
- intermediaries
- fake audits
- PR campaigns
- donations
- bought ratings
- artificial popularity
- bot networks
- tax and angle havens

Then apparently:

\[
g \uparrow,\quad b \uparrow
\]

but confidence should fall:

\[
\rho \downarrow
\]

and history \(h\) should become suspicious.

Therefore the system needs an origin trail:

\[
h = \text{transaction history}
\]

Without history, angle money becomes washable.

---

# 24. Circulation in the labor market

The labor market is especially important.

A firm buys labor.

A worker sells labor.

For the firm, labor is an input:

\[
\theta_{\text{firm}}^K
\]

For the worker, wages are an incoming value:

\[
\theta_{\text{worker}}^K
\]

At the same time:

- The worker sells labor power with his sell angle.
- The firm pays wages with its sell angle.

So again there are two matchings:

\[
d_{\text{labor}} = d(\theta_{\text{firm}}^K,\theta_{\text{worker}}^V)
\]

\[
d_{\text{wage}} = d(\theta_{\text{worker}}^K,\theta_{\text{firm}}^V)
\]

If the labor fits but the wage angle is bad, the worker demands more wage.

If the wage is good but the activity is bad, he can still refuse.

This explains real cases:

\[
\text{high wage, bad employer}
\]

\[
\text{low wage, good purpose}
\]

\[
\text{popular firm, bad working conditions}
\]

\[
\text{unpopular job, high social value}
\]

---

# 25. Circulation in the credit market

In credit, money is newly created or shifted across time.

A bank issues credit:

\[
\theta_{\text{bank}}^V
\]

The debtor receives credit:

\[
\theta_{\text{debtor}}^K
\]

Later the debtor repays:

\[
\theta_{\text{debtor}}^V
\]

The bank receives repayment:

\[
\theta_{\text{bank}}^K
\]

So:

\[
d_{\text{credit}}=d(\theta_{\text{debtor}}^K,\theta_{\text{bank}}^V)
\]

\[
d_{\text{repayment}}=d(\theta_{\text{bank}}^K,\theta_{\text{debtor}}^V)
\]

If the credit serves a good purpose:

\[
g_{\text{credit}} \uparrow
\]

If the credit finances popular speculation:

\[
b_{\text{credit}} \uparrow,\quad g_{\text{credit}} \text{ uncertain}
\]

If the credit finances toxic activities:

\[
g_{\text{credit}} \downarrow
\]

Then interest rates or collateral requirements rise.

The interest rate then consists of:

\[
i = i_0 + i_{\text{default}} + i_{\text{angle risk}} + i_{\rho}
\]

So:

\[
\text{Interest} = \text{time price} + \text{risk} + \text{angle penalty}
\]

---

# 26. Circulation in the state

The state receives taxes:

\[
\theta_{\text{state}}^K
\]

and spends public money:

\[
\theta_{\text{state}}^V
\]

Taxes from toxic sources can be problematic:

\[
\text{Should the state accept bad money?}
\]

If yes, it may need to cleanse it:

\[
\theta_{\text{toxic}} \rightarrow \theta_{\text{publicly legitimate}}
\]

through:

- courts
- transparency
- redistribution
- repair of harm
- public investment

Public spending creates new angles:

- Education can increase \(g\).
- Propaganda can artificially increase \(b\).
- Infrastructure can increase value and goodness.
- Repression can create short-term order, but long-term bad angle.
- War can receive very different angles depending on people and government.

The state is therefore a huge angle transformer.

---

# 27. Circulation between countries

Every country has its own axes.

What is good in country A is not necessarily good in country B.

So angle translation is needed:

\[
T_{A\rightarrow B}(\theta)
\]

An export transaction then has:

\[
\theta_{\text{export, A}}
\rightarrow
T_{A\rightarrow B}(\theta_{\text{export, A}})
\]

Example:

\[
40^\circ \text{ in country A}
\]

can become:

\[
110^\circ \text{ in country B}
\]

Then international angle arbitrage emerges.

Firms seek countries where:

- their product is more popular
- their goodness is evaluated better
- their bad effects are less visible
- their history is checked less strictly

This is moral location arbitrage.

---

# 28. What happens across multiple markets?

Each market has its own angle structure.

## Product market

\[
\theta_{\text{buyer}}^K
\leftrightarrow
\theta_{\text{seller}}^V
\]

## Payment market

\[
\theta_{\text{seller}}^K
\leftrightarrow
\theta_{\text{buyer}}^V
\]

## Labor market

\[
\theta_{\text{firm}}^K
\leftrightarrow
\theta_{\text{worker}}^V
\]

and:

\[
\theta_{\text{worker}}^K
\leftrightarrow
\theta_{\text{firm}}^V
\]

## Credit market

\[
\theta_{\text{debtor}}^K
\leftrightarrow
\theta_{\text{bank}}^V
\]

and later:

\[
\theta_{\text{bank}}^K
\leftrightarrow
\theta_{\text{debtor}}^V
\]

## Capital market

Investors buy firm shares:

\[
\theta_{\text{investor}}^K
\leftrightarrow
\theta_{\text{firm}}^V
\]

Firms buy capital:

\[
\theta_{\text{firm}}^K
\leftrightarrow
\theta_{\text{investor}}^V
\]

## Angle market

Here direction is traded directly:

\[
(m,g,b)
\rightarrow
(m',g',b')
\]

with fee, risk, and confidence loss.

---

# 29. What the two angles mean economically

The difference between buy angle and sell angle is the core of business logic:

\[
s_i = d(\theta_i^K,\theta_i^V)
\]

This is the actor's angle spread.

## Small spread

\[
s_i \approx 0
\]

The actor buys and sells in a similar direction.

That means:

- coherent
- credible
- little transformation work
- little arbitrage
- high trustworthiness

## Large spread

\[
s_i \gg 0
\]

The actor buys in one direction and sells in another.

That can be good or bad.

### Good variant

It buys bad inputs and improves them for real.

\[
\theta^K = \text{bad}
\]

\[
\theta^V = \text{good}
\]

Then it creates real value improvement.

### Bad variant

It buys bad inputs and only sells them in better packaging.

\[
\theta^K = \text{bad}
\]

\[
\theta^V = \text{apparently good}
\]

Then it practices angle laundering.

### Extractive variant

It buys good inputs and sells bad outputs.

\[
\theta^K = \text{good}
\]

\[
\theta^V = \text{bad}
\]

Then it destroys goodness or trust.

---

# 30. Circulation as a loop in the whole economy

The whole economy then looks like this:

```text
Households
  │ buy products
  ▼
Firms
  │ pay wages, buy inputs, take loans
  ▼
Banks / capital markets
  │ finance firms and states
  ▼
States
  │ tax, regulate, subsidize
  ▼
Media / peoples / courts / governments
  │ evaluate goodness, popularity, and confidence
  ▼
Angle markets
  │ rotate, insure, audit, and trade directions
  ▼
Households and firms
```

Value flows through payments.

Goodness flows through real consequences and institutional judgments.

Popularity flows through demand, media, and social acceptance.

Confidence flows through proof, transparency, and dispute.

History flows through the transaction chain.

---

# 31. Money circulation becomes selective

In normal money:

\[
100 = 100
\]

In your system:

\[
100 \angle 30^\circ \neq 100 \angle 150^\circ
\]

Therefore money no longer circulates equally everywhere.

Zones form:

## Clean high-confidence circuit

Good money circulates among trustworthy actors.

\[
g \uparrow,\quad b \uparrow,\quad \rho \uparrow
\]

There, interest rates are low, trade is fast, and spreads are small.

## Popular but questionable circuit

Popular money circulates quickly, but with risk.

\[
b \uparrow,\quad g \text{ uncertain}
\]

There are bubbles and scandals.

## Good but unpopular circuit

Good but unpopular activities require patience, subsidies, or education.

\[
g \uparrow,\quad b \downarrow
\]

There is a threat of underfunding.

## Toxic circuit

Bad money circulates in shadow markets or with high discounts.

\[
g \downarrow,\quad b \downarrow,\quad \rho \downarrow
\]

There, interest rates are high, fraud is common, and liquidity is low.

---

# 32. Why circulation does not automatically become moral

A common mistake would be:

> If goodness and popularity are embedded in money, the economy automatically becomes good.

No.

The system makes moral direction tradable.

That also makes it manipulable.

It leads to three possible forms:

## Real improvement

\[
\text{Value} \rightarrow \text{real goodness}
\]

## Symbolic improvement

\[
\text{Value} \rightarrow \text{popularity}
\]

## Fraudulent improvement

\[
\text{Value} \rightarrow \text{apparent goodness}
\]

Therefore \(\rho\), confidence, is absolutely central.

Without confidence, the angle becomes a propaganda label.

With confidence, the angle becomes verifiable.

---

# 33. The shortest mechanism

The shortest complete description is:

\[
\boxed{
\text{Actors receive through their buy angle and send through their sell angle.}
}
\]

Every trade checks:

\[
\boxed{
\text{Does the sell angle of the good fit the buyer's buy angle?}
}
\]

and:

\[
\boxed{
\text{Does the sell angle of the money fit the seller's buy angle?}
}
\]

If yes, value, goodness, and popularity flow easily.

If no, the result is:

- discounts
- surcharges
- rotation
- audit costs
- insurance
- waiting time
- shadow markets
- reputation risks
- political conflicts

Money circulation is therefore no longer a circle, but a directed network:

\[
\boxed{
\text{Value flows along compatible angles.}
}
\]

\[
\boxed{
\text{Goodness flows along real improvement and recognition.}
}
\]

\[
\boxed{
\text{Popularity flows along attention and approval.}
}
\]

The two angles of every actor determine **what it wants to absorb** and **what it emits into the world**.

That is exactly where the economic dynamic comes from.
