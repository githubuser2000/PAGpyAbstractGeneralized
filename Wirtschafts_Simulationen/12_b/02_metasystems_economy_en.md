# Meta-Economy: Money as a Hierarchical Entitlement Tree

## Original question

Suppose the economic system does not trade things, but metasystems and properties, where money is not numbers but tuples inside tuples, that is, a hierarchical tree that can be converted back and forth into a number using two sums and multiplication. An economic system in which, instead of gaining selfish advantages, people obtain status, privileges, and bonuses — stepwise advantages through career drive, like vouchers. Then products cost jobs, not numbers, but hierarchies that are metasystems and properties.

## Answer

Yes. At its core, you are no longer describing a normal monetary economy, but a **meta-economy**: what is traded is not primarily things, but **access rights, status positions, properties, roles, permissions, and transformation rules**.

The decisive sentence is:

> Products do not cost “5 units of money,” but a certain **hierarchy of conditions** that makes their production, earning, and access possible.

That is a strong idea.

## 1. Money would no longer be a scalar, but a structured claim

Normal money is roughly:

```text
money = number
```

Your model is closer to:

```text
money = tree of properties, rights, status, contributions, bindings
```

For example:

```text
G = {
  Contribution: {
    Work: {
      Time: 40h,
      Difficulty: high,
      Quality: verified,
      Rarity: medium
    },
    Usefulness: {
      social: high,
      infrastructural: medium
    }
  },
  Status: {
    Rank: 3,
    Trust: 0.82,
    CareerPath: Engineering → Leadership → System Responsibility
  },
  Rights: {
    Housing: Priority B,
    Mobility: Voucher Class 2,
    Education: unlimited,
    Luxury: limited
  },
  Bindings: {
    expires: partially,
    transferable: no,
    inheritable: no,
    purpose_bound: yes
  }
}
```

That is not an “amount.” It is a **social-semantic token**.

A person does not simply possess purchasing power, but a bundle of answers to questions such as:

```text
What have you contributed?
What role do you have?
What status do you have?
What rights do you have?
For what may you use those rights?
What properties does your claim have?
```

Money itself thereby becomes a metasystem.

## 2. The number would only be a projection of the tree

When you say the tree can be converted “back and forth” into a number using two sums and multiplication, we need to distinguish two cases.

A mapping from the tree to a number is easy:

```text
π(tree) = number
```

For example:

```text
value = Σ level_value × weight
```

or:

```text
value = Σ_i α_i · Σ_j β_ij · property_ij
```

The problem is that a true reverse conversion is normally not unique.

From:

```text
number = 100
```

you do not know whether it came from:

```text
80 work + 20 status
```

or:

```text
30 work + 40 trust + 30 privilege
```

or:

```text
10 risk + 90 rarity
```

A number usually destroys structure.

So the rule is:

> If the path tree → number → tree is truly lossless, then the number is not an ordinary value number, but rather an **encoding** of the tree.

The number would then be like a serial number, a decodable hash, a Gödel code, or a compressed data carrier.

But if the number performs real economic valuation, then the return path is not unique. The tree is simplified by the number, and part of the metasystem is lost.

This matters because your system breaks at precisely this point:

**Variant A:**  
The tree is decisive, and the number is only a display.  
Then you have a genuine meta-economy.

**Variant B:**  
The number is ultimately decisive.  
Then you again have a monetary economy, only with more complicated accounting.

## 3. Products would not have prices, but entitlement profiles

A normal product has:

```text
Product P costs 100
```

In your system, a product would instead have something like:

```text
Product P requires entitlement tree C(P)
```

For example, a bicycle:

```text
C(bicycle) = {
  Work: {
    Metalworking: medium,
    Assembly: medium,
    Logistics: low,
    Maintainability: high
  },
  Material: {
    Steel/Aluminum: x,
    Rubber: y,
    Energy: z
  },
  Social Priority: {
    Mobility: high,
    Luxury: low,
    Health: medium
  },
  Access: {
    StatusRequirement: low,
    NeedBonus: commuter,
    Region: local
  }
}
```

Then one does not pay “money.” One must possess a compatible entitlement tree:

```text
buyer_money_tree ≥ product_cost_tree
```

But “≥” is not a simple greater-than relation here. It means something closer to:

```text
fits structurally
covers required properties
has sufficient rights
has the appropriate purpose binding
```

That is closer to type checking than to payment.

In software terms:

```text
purchase = typecheck(entitlement, product_requirement)
```

Not:

```text
if balance >= price
```

but:

```text
if entitlement_tree satisfies cost_schema
```

That is a very elegant way to think about it.

## 4. “Products cost jobs” means: they cost production roles

The sentence “products cost jobs” is strong, but it should be made precise.

A product does not simply cost “jobs” in the sense of arbitrary employment. It costs a **production hierarchy**:

```text
product → required roles → required skills → required infrastructure → required institutions
```

Example: a smartphone does not only cost material and working time. It costs an entire tree:

```text
Smartphone = {
  raw_material_extraction,
  chip_design,
  semiconductor_manufacturing,
  mechanical_engineering,
  logistics,
  software_development,
  patent_system,
  energy_supply,
  quality_control,
  repair_infrastructure,
  disposal_system
}
```

In your language:

> The price of a product is the shadow of its production hierarchy.

Or even sharper:

> A product is the visible tip of an invisible metasystem.

Then “price” would no longer be a number, but the compressed representation of the social, technical, and institutional structure that makes the product possible.

## 5. Status does not automatically replace egoism

Here we need to be hard-nosed: if you replace selfish monetary advantages with status, privileges, career, and bonuses, self-interest does not disappear. It merely changes form.

This:

```text
I want more money.
```

becomes:

```text
I want higher rank.
I want better vouchers.
I want privileged access.
I want reputation.
I want a higher career level.
```

That can be more productive than greed for money, but it can also be more dangerous.

Money is relatively dumb. Status reaches deeper psychologically. People often defend status more irrationally than possessions. A status economy may therefore motivate more strongly, but it can also become harsher, more rank-fixated, and more manipulative.

The main problem would be:

> You are not replacing capitalism with communal spirit, but with a career-and-entitlement economy.

That can be good if status is tied to real performance, responsibility, and system benefit.

It can become terrible if status is tied to loyalty, bureaucracy, political closeness, or metric gaming.

## 6. The system would be more powerful than money, but also more authoritarian

Normal money has a brutal simplicity:

```text
everything becomes comparable
```

That is often morally ugly, but operationally very efficient.

Your system preserves more meaning:

```text
not every contribution is equal
not every product is equal
not every claim is equal
not every use is allowed
```

That is semantically smarter.

But it creates a central question of power:

> Who defines the tree?

Who decides:

```text
which properties count?
which status levels exist?
how work is weighted?
which vouchers apply to what?
which career paths are privileged?
which entitlement profiles products have?
```

In a normal monetary economy, power controls capital flows.

In your meta-economy, power controls the **ontology**.

That is deeper.

Whoever controls the categories controls the reality of the system.

## 7. The real currency would not be money, but recognition plus access

Your system would probably have four basic currencies:

```text
1. Contribution
2. Status
3. Access
4. Trust
```

That means:

**Contribution:**  
What have you actually done?

**Status:**  
What position do you hold in the system?

**Access:**  
What are you allowed to use, receive, enter, or consume?

**Trust:**  
How much autonomy does the system grant you?

Money in the old sense then becomes secondary. The central question is not:

```text
How much do you have?
```

but:

```text
What kind of claim are you?
```

That is a massive shift.

## 8. A good formal description

You could formulate your system as follows:

```text
Person A possesses entitlement tree G(A).

Product P possesses cost tree C(P).

A may receive P if:

G(A) ⊨ C(P)
```

That is:

```text
A's entitlement tree satisfies P's entitlement schema.
```

After consumption, the tree is transformed:

```text
G(A)' = T_P(G(A))
```

Not simply:

```text
account_balance = account_balance - price
```

but:

```text
status/rights/claims are rewritten
```

This is more of a **rewrite system** than accounting.

Example:

```text
Purchase of a luxury product:
- consumes luxury voucher
- lowers available priority
- minimally affects status
- creates maintenance claim
- binds future resources
```

Example:

```text
Taking on difficult work:
- increases trust value
- opens new product classes
- raises career path
- creates bonus rights
- improves priority for scarce goods
```

This is an economy of state transitions.

## 9. The best technical analogy: typed money

Normal money is untyped:

```text
100 euros = 100 euros
```

Your money is typed:

```text
100 care-contribution ≠ 100 luxury-voucher
100 infrastructure-responsibility ≠ 100 consumption-right
100 trust-points ≠ 100 working-hours
```

It is like the difference between:

```text
number
```

and:

```text
type-safe structured object
```

Normal money permits dangerous convertibility. Everything can buy everything.

Your system says:

> No. Not every form of economic energy may flow in every direction.

That is the actual core.

You are building a system against universal fungibility.

## 10. The deepest advantage: it could prevent false equivalences

Normal money implicitly claims:

```text
€1,000 from speculation
=
€1,000 from care work
=
€1,000 from corruption
=
€1,000 from invention
```

Once the money exists, its origin is largely irrelevant.

Your system could preserve origin, purpose, and social meaning:

```text
contribution remains semantically marked.
```

That is extremely important.

Then a claim would not just be quantity, but history:

```text
This claim comes from dangerous work.
This claim comes from long-term responsibility.
This claim comes from creative innovation.
This claim can only be used for education.
This claim cannot be converted into luxury.
```

That makes the economy morally and systemically more precise.

## 11. The deepest disadvantage: it can become a caste order

If status, career, rights, and product access are coupled, a danger immediately appears:

```text
high status → better opportunities → more bonuses → higher status
```

That is a positive feedback loop.

Meritocracy then quickly becomes aristocracy.

To prevent this, your system would need hard counter-rules:

```text
Status partially decays.
Privileges are not inheritable.
Basic rights are status-independent.
Status must remain domain-specific.
Career must not dominate every area of life.
Conversion between types of status must be limited.
```

Otherwise, a society emerges in which people are not poor in money, but poor in permission, rank, and visibility.

Psychologically, that could be even more brutal.

## 12. Condensation

Your model can be summarized like this:

> Economy is not the exchange of things for numbers, but the transformation of entitlement trees inside a social metasystem.

Or:

> Money is not a carrier of value, but a typed, hierarchical permission state.

Or even shorter:

> Price becomes structure. Payment becomes status transformation. Possession becomes access right.

This is a serious idea.

But the decisive fracture point is this:

> If your tree is ultimately fully convertible into a number, the old logic of money returns.  
> If it is not fully convertible, a genuine meta-economy emerges — but with enormous power over categories, status, and permissions.

So the real design question is not “How do we replace money?” but:

> Which properties may be converted into one another — and which must never be converted?

That is where the morality of your system sits.
