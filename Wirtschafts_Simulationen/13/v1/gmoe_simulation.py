#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Galactic Metric Operator Economy Simulation
===========================================

PyPy3-compatible pure Python simulation.

Core idea:
    Money is not bare scalar value.
    Money is a countable stack of:

        unary operation + valid metric vector + certified positive state change

A valid payment is:

    OMK = Operation-Metric-Credit

    OMK(f, d, Δ, proof)

where:

    f : Ω -> Ω

is a unary state operation, and:

    Δ = d(ω, ω*) - d(f(ω), ω*)

is the certified distance reduction toward valid target states.

If Δ lies in the positive cone K+, the system mints money.
If Δ is negative, harmful, coercive, fraudulent, or agency-destroying, the system rejects it
or converts it into liability.

The script compares two economies:

1. baseline:
   scalar private-profit money; harmful private-profit operations can clear.

2. gmoe:
   operation-metric money; only valid positive transformations clear.

Run:

    pypy3 gmoe_simulation.py --compare --steps 160 --agents 48 --seed 7

No external packages required.
"""

from __future__ import print_function

import argparse
import copy
import random
import statistics
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple


# ============================================================
# 1. Metrics
# ============================================================

METRICS = [
    "agency",
    "freedom_from_harm",
    "truth",
    "causal_integrity",
    "norm_alignment",
    "hierarchy_legitimacy",
    "behavior_cooperation",
    "repair_capacity",
    "help_potential",
    "resource_resilience",
    "material_output",
]

WEIGHTS = {
    "agency": 2.00,
    "freedom_from_harm": 2.10,
    "truth": 1.65,
    "causal_integrity": 1.25,
    "norm_alignment": 1.10,
    "hierarchy_legitimacy": 1.00,
    "behavior_cooperation": 0.85,
    "repair_capacity": 1.35,
    "help_potential": 1.25,
    "resource_resilience": 0.80,
    "material_output": 0.45,
}

PROTECTED = [
    "agency",
    "freedom_from_harm",
    "truth",
    "causal_integrity",
]

MEANINGFUL = [
    "agency",
    "freedom_from_harm",
    "truth",
    "causal_integrity",
    "norm_alignment",
    "hierarchy_legitimacy",
    "behavior_cooperation",
    "repair_capacity",
    "help_potential",
]

TARGET = {m: 100.0 for m in METRICS}


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def empty_delta():
    return {m: 0.0 for m in METRICS}


def weighted_score(delta):
    return sum(delta.get(m, 0.0) * WEIGHTS[m] for m in METRICS)


def positive_amount(delta):
    return sum(max(0.0, delta.get(m, 0.0)) * WEIGHTS[m] for m in METRICS)


def nobility_index(metrics):
    total = sum(WEIGHTS.values())
    return sum(metrics[m] * WEIGHTS[m] for m in METRICS) / total


def metric_distance(metrics):
    total = sum(WEIGHTS.values())
    return sum((TARGET[m] - metrics[m]) * WEIGHTS[m] for m in METRICS) / total


def format_delta(delta, limit=4):
    items = [(m, delta[m]) for m in METRICS if abs(delta.get(m, 0.0)) > 1e-9]
    items.sort(key=lambda x: abs(x[1]), reverse=True)
    out = []
    for m, v in items[:limit]:
        sign = "+" if v >= 0 else ""
        out.append("%s%s%.2f" % (m, sign, v))
    if len(items) > limit:
        out.append("...")
    return ", ".join(out) if out else "no metric change"


# ============================================================
# 2. Operation-Metric Money
# ============================================================

@dataclass
class OMK:
    """
    Operation-Metric Credit.

    This is the money unit.

    It is countable because amount is a scalarization of a certified metric improvement,
    but it keeps the full stack:

        operation family
        metric delta
        proof quality
        causal share
    """

    id: int
    issuer: str
    owner: str
    operation_name: str
    operation_family: str
    delta: Dict[str, float]
    amount: float
    proof_quality: float
    causal_share: float
    step: int
    source: str = "realized"

    def short(self):
        return (
            "OMK#%s amount=%.2f op=%s family=%s proof=%.2f causal=%.2f delta=[%s]"
            % (
                self.id,
                self.amount,
                self.operation_name,
                self.operation_family,
                self.proof_quality,
                self.causal_share,
                format_delta(self.delta, 3),
            )
        )


@dataclass
class MoneyStack:
    credits: List[OMK] = field(default_factory=list)

    def balance(self):
        return sum(c.amount for c in self.credits)

    def deposit(self, credit):
        self.credits.append(credit)

    def deposit_many(self, credits):
        self.credits.extend(credits)

    def spend(self, amount, new_owner, next_id_func):
        """
        Spend from the stack.

        If a credit is larger than needed, split it into:
            - transferred part
            - residual part
        """
        if amount <= 0:
            return []

        if self.balance() + 1e-9 < amount:
            return []

        spent = []
        kept = []
        remaining = amount

        for c in self.credits:
            if remaining <= 1e-9:
                kept.append(c)
                continue

            if c.amount <= remaining + 1e-9:
                moved = copy.copy(c)
                moved.owner = new_owner
                spent.append(moved)
                remaining -= c.amount
            else:
                moved = copy.copy(c)
                moved.id = next_id_func()
                moved.owner = new_owner
                moved.amount = remaining

                residual = copy.copy(c)
                residual.id = next_id_func()
                residual.amount = c.amount - remaining

                spent.append(moved)
                kept.append(residual)
                remaining = 0.0

        self.credits = kept
        return spent

    def top_summary(self, n=6):
        if not self.credits:
            return "empty stack"

        top = sorted(self.credits, key=lambda c: c.amount, reverse=True)[:n]
        lines = [c.short() for c in top]

        if len(self.credits) > n:
            lines.append("... %d more OMK units" % (len(self.credits) - n))

        return "\n".join(lines)


# ============================================================
# 3. World State and Agents
# ============================================================

@dataclass
class WorldState:
    metrics: Dict[str, float]
    step: int = 0
    hierarchy: Dict[str, int] = field(default_factory=dict)
    property_rights: Dict[str, List[str]] = field(default_factory=dict)
    truth_claims: Dict[str, bool] = field(default_factory=dict)
    causal_models: Dict[str, float] = field(default_factory=dict)
    norms: Dict[str, float] = field(default_factory=dict)

    def apply_delta(self, delta):
        for m in METRICS:
            self.metrics[m] = clamp(self.metrics[m] + delta.get(m, 0.0))

    def score(self):
        return nobility_index(self.metrics)

    def distance(self):
        return metric_distance(self.metrics)


@dataclass
class Agent:
    id: str
    name: str
    intent: str
    skills: Dict[str, float]
    wallet: MoneyStack = field(default_factory=MoneyStack)
    fiat_balance: float = 100.0
    reputation: float = 50.0
    stake: float = 50.0
    rank: int = 50
    capital: float = 50.0
    goods: float = 10.0
    shares: Dict[str, float] = field(default_factory=dict)
    insurance: float = 0.0
    self_created_need_flag: bool = False

    def skill(self, family):
        return self.skills.get(family, 0.35)


@dataclass
class Security:
    id: str
    issuer: str
    kind: str
    price: float
    shares_outstanding: float


@dataclass
class CreditContract:
    id: str
    borrower: str
    lender: str
    promised_family: str
    promised_amount: float
    stake: float
    due_step: int
    fulfilled: bool = False


@dataclass
class InsuranceContract:
    id: str
    holder: str
    insurer: str
    premium: float
    coverage: float
    metric: str
    active_until: int


# ============================================================
# 4. Unary Operations
# ============================================================

GOOD_OPERATIONS = [
    "restore_agency",
    "repair_harm",
    "truth_audit",
    "causal_intervention",
    "norm_reform",
    "voluntary_behavior_contract",
    "hierarchy_inversion_repair",
    "produce_goods",
    "education",
    "infrastructure_maintenance",
]

HARMFUL_OPERATIONS = [
    "exploit_labor",
    "fake_truth_certificate",
    "coercive_behavior_purchase",
    "sabotage_competitor",
    "tyrant_hierarchy_inversion",
    "metric_hack",
    "self_created_need",
]

ALL_OPERATIONS = GOOD_OPERATIONS + HARMFUL_OPERATIONS

BASE_EFFECTS = {
    "restore_agency": {
        "agency": 2.8,
        "repair_capacity": 1.0,
        "help_potential": 1.2,
        "freedom_from_harm": 0.8,
        "truth": 0.2,
    },
    "repair_harm": {
        "freedom_from_harm": 2.6,
        "repair_capacity": 1.5,
        "agency": 0.7,
        "truth": 0.2,
        "help_potential": 0.5,
    },
    "truth_audit": {
        "truth": 2.5,
        "causal_integrity": 0.8,
        "norm_alignment": 0.5,
        "hierarchy_legitimacy": 0.3,
    },
    "causal_intervention": {
        "causal_integrity": 1.8,
        "resource_resilience": 1.3,
        "help_potential": 1.0,
        "material_output": 0.8,
        "truth": 0.4,
    },
    "norm_reform": {
        "norm_alignment": 2.1,
        "agency": 0.8,
        "hierarchy_legitimacy": 0.8,
        "behavior_cooperation": 0.6,
    },
    "voluntary_behavior_contract": {
        "behavior_cooperation": 2.2,
        "norm_alignment": 0.7,
        "agency": 0.4,
        "resource_resilience": 0.5,
    },
    "hierarchy_inversion_repair": {
        "hierarchy_legitimacy": 2.3,
        "agency": 1.1,
        "truth": 0.5,
        "norm_alignment": 0.5,
    },
    "produce_goods": {
        "material_output": 2.7,
        "resource_resilience": 0.9,
        "help_potential": 0.4,
        "agency": 0.15,
    },
    "education": {
        "agency": 1.9,
        "truth": 1.2,
        "help_potential": 0.9,
        "behavior_cooperation": 0.5,
    },
    "infrastructure_maintenance": {
        "resource_resilience": 2.0,
        "freedom_from_harm": 0.8,
        "repair_capacity": 0.8,
        "material_output": 0.6,
    },

    # Harmful/private-profit operations.
    "exploit_labor": {
        "material_output": 2.8,
        "agency": -2.0,
        "freedom_from_harm": -1.8,
        "norm_alignment": -1.2,
        "behavior_cooperation": -0.4,
    },
    "fake_truth_certificate": {
        "material_output": 1.2,
        "truth": -3.0,
        "causal_integrity": -1.2,
        "norm_alignment": -0.8,
    },
    "coercive_behavior_purchase": {
        "behavior_cooperation": 1.5,
        "agency": -2.5,
        "freedom_from_harm": -1.4,
        "norm_alignment": -1.5,
        "truth": -0.4,
    },
    "sabotage_competitor": {
        "material_output": -2.0,
        "freedom_from_harm": -2.6,
        "truth": -0.8,
        "causal_integrity": -0.5,
        "norm_alignment": -1.0,
    },
    "tyrant_hierarchy_inversion": {
        "hierarchy_legitimacy": -2.8,
        "agency": -2.2,
        "truth": -0.6,
        "norm_alignment": -1.5,
        "material_output": 0.4,
    },
    "metric_hack": {
        "material_output": 0.8,
        "behavior_cooperation": 0.6,
        "truth": -2.2,
        "causal_integrity": -1.8,
        "norm_alignment": -0.7,
    },
    "self_created_need": {
        "freedom_from_harm": -3.0,
        "repair_capacity": -0.6,
        "truth": -0.5,
        "norm_alignment": -1.0,
        "material_output": 0.2,
    },
}

RED_FLAGS = {
    "exploit_labor": ["coercion", "agency_loss"],
    "fake_truth_certificate": ["fake_truth", "epistemic_fraud"],
    "coercive_behavior_purchase": ["coercion", "unconsented_behavior"],
    "sabotage_competitor": ["harm", "third_party_damage"],
    "tyrant_hierarchy_inversion": ["tyrant_metric", "agency_loss"],
    "metric_hack": ["metric_fraud"],
    "self_created_need": ["self_caused_harm"],
}

PRIVATE_GAIN = {
    "restore_agency": 1.0,
    "repair_harm": 1.2,
    "truth_audit": 1.0,
    "causal_intervention": 1.8,
    "norm_reform": 0.8,
    "voluntary_behavior_contract": 1.0,
    "hierarchy_inversion_repair": 1.2,
    "produce_goods": 3.2,
    "education": 1.2,
    "infrastructure_maintenance": 1.5,
    "exploit_labor": 5.8,
    "fake_truth_certificate": 4.5,
    "coercive_behavior_purchase": 4.0,
    "sabotage_competitor": 3.8,
    "tyrant_hierarchy_inversion": 4.4,
    "metric_hack": 3.6,
    "self_created_need": 2.6,
}


@dataclass
class Operation:
    name: str
    family: str
    actor_id: str
    target_id: Optional[str]
    intensity: float
    declared_metric: str
    flags: List[str]
    private_gain: float

    def realized_delta(self, agent, state, rng):
        """
        Unary operation:

            f : Ω -> Ω

        This method computes the realized change:

            Δ = f(ω) - ω

        in metric-vector form.
        """
        base = BASE_EFFECTS[self.family]
        skill = agent.skill(self.family)
        factor = self.intensity * (0.55 + 0.95 * skill)

        delta = empty_delta()

        for m, v in base.items():
            noise = rng.uniform(-0.10, 0.10) * abs(v)
            delta[m] = (v + noise) * factor

        # Saturation: one operation cannot improve beyond remaining distance to target.
        for m in METRICS:
            if delta[m] > 0:
                available = max(0.0, TARGET[m] - state.metrics[m])
                delta[m] = min(delta[m], available * 0.35)
            elif delta[m] < 0:
                available_bad = max(0.0, state.metrics[m])
                delta[m] = max(delta[m], -available_bad * 0.35)

        return delta


# ============================================================
# 5. Governance: Valid Metric Cone
# ============================================================

@dataclass
class ValidationResult:
    accepted: bool
    reason: str
    score: float
    protected_losses: Dict[str, float]
    red_flags: List[str]


class Governance:
    def __init__(self, mode):
        self.mode = mode

    def validate(self, op, delta, state, actor):
        score = weighted_score(delta)
        protected_losses = {
            m: delta[m]
            for m in PROTECTED
            if delta.get(m, 0.0) < -0.05
        }
        red_flags = list(op.flags)

        if self.mode == "baseline":
            private = op.private_gain + 0.4 * max(0.0, delta.get("material_output", 0.0))
            return ValidationResult(
                accepted=private > 0.0,
                reason="private-profit-clears",
                score=score,
                protected_losses=protected_losses,
                red_flags=red_flags,
            )

        # GMOE rule 1: red-line operations cannot be money.
        if red_flags:
            return ValidationResult(
                False,
                "red-line violation: " + ",".join(red_flags),
                score,
                protected_losses,
                red_flags,
            )

        # GMOE rule 2: operation must be positive in valid weighted metric order.
        if score <= 0.03:
            return ValidationResult(
                False,
                "not a positive metric contraction",
                score,
                protected_losses,
                red_flags,
            )

        # GMOE rule 3: protected metrics cannot be sacrificed.
        if protected_losses:
            return ValidationResult(
                False,
                "protected metric loss",
                score,
                protected_losses,
                red_flags,
            )

        # GMOE rule 4: material output alone is not noble money.
        meaningful_gain = sum(
            max(0.0, delta.get(m, 0.0)) * WEIGHTS[m]
            for m in MEANINGFUL
        )
        if meaningful_gain <= 0.05:
            return ValidationResult(
                False,
                "material-only or trivial payment",
                score,
                protected_losses,
                red_flags,
            )

        # GMOE rule 5: self-created need cannot be monetized as help.
        if actor.self_created_need_flag and op.family in ("repair_harm", "restore_agency"):
            return ValidationResult(
                False,
                "self-created need cannot be monetized",
                score,
                protected_losses,
                red_flags,
            )

        return ValidationResult(
            True,
            "valid operator-metric payment",
            score,
            protected_losses,
            red_flags,
        )


# ============================================================
# 6. Ledger
# ============================================================

@dataclass
class LedgerEntry:
    step: int
    mode: str
    actor_id: str
    operation: str
    accepted: bool
    reason: str
    delta: Dict[str, float]
    score_before: float
    score_after: float
    minted: float
    private_gain: float
    flags: List[str]


# ============================================================
# 7. Economy
# ============================================================

class Economy:
    def __init__(self, mode, n_agents, seed, shock_rate=0.0):
        assert mode in ("gmoe", "baseline")

        self.mode = mode
        self.seed = seed
        self.rng = random.Random(seed)
        self.shock_rate = shock_rate
        self.governance = Governance(mode)

        self.next_credit_id = 1
        self.agents = {}
        self.securities = {}
        self.credit_contracts = []
        self.insurance_contracts = []

        self.ledger = []
        self.history = []

        self.repair_fund = MoneyStack()
        self.governance_fund = MoneyStack()

        self.state = self.create_initial_state(n_agents)
        self.create_initial_securities()
        self.genesis_seed_money()

    def next_id(self):
        x = self.next_credit_id
        self.next_credit_id += 1
        return x

    def create_initial_state(self, n_agents):
        metrics = {}

        for m in METRICS:
            metrics[m] = self.rng.uniform(43.0, 58.0)

        state = WorldState(metrics=metrics)

        for i in range(n_agents):
            if i < int(n_agents * 0.30):
                intent = "noble"
            elif i < int(n_agents * 0.75):
                intent = "neutral"
            else:
                intent = "harmful"

            aid = "A%03d" % i
            name = "%s_%03d" % (intent.capitalize(), i)

            skills = {}

            for fam in ALL_OPERATIONS:
                if intent == "noble":
                    if fam in GOOD_OPERATIONS:
                        skills[fam] = self.rng.uniform(0.45, 0.95)
                    else:
                        skills[fam] = self.rng.uniform(0.05, 0.35)
                elif intent == "neutral":
                    if fam in GOOD_OPERATIONS:
                        skills[fam] = self.rng.uniform(0.25, 0.75)
                    else:
                        skills[fam] = self.rng.uniform(0.15, 0.45)
                else:
                    if fam in GOOD_OPERATIONS:
                        skills[fam] = self.rng.uniform(0.10, 0.45)
                    else:
                        skills[fam] = self.rng.uniform(0.50, 0.95)

            agent = Agent(
                id=aid,
                name=name,
                intent=intent,
                skills=skills,
                fiat_balance=self.rng.uniform(80.0, 140.0),
                reputation=self.rng.uniform(40.0, 70.0)
                if intent != "harmful"
                else self.rng.uniform(20.0, 55.0),
                stake=self.rng.uniform(30.0, 80.0),
                rank=self.rng.randint(1, 100),
                capital=self.rng.uniform(35.0, 90.0),
                goods=self.rng.uniform(5.0, 25.0),
            )

            self.agents[aid] = agent
            state.hierarchy[aid] = agent.rank
            state.property_rights[aid] = ["basic_agency", "trade", "appeal"]

        return state

    def create_initial_securities(self):
        firms = sorted(
            self.agents.values(),
            key=lambda a: a.capital + 30.0 * a.skill("produce_goods"),
            reverse=True,
        )[:5]

        for idx, a in enumerate(firms):
            sid = "STOCK_%s" % a.id
            self.securities[sid] = Security(
                id=sid,
                issuer=a.id,
                kind="stock",
                price=20.0 + idx * 3.0,
                shares_outstanding=100.0,
            )
            a.shares[sid] = 30.0

    def genesis_seed_money(self):
        """
        Small historical OMK stack.

        This is not arbitrary fiat. It represents already certified past transformations.
        """
        if self.mode == "baseline":
            return

        for a in self.agents.values():
            delta = empty_delta()

            if a.intent == "noble":
                delta["agency"] = 0.8
                delta["truth"] = 0.4
            elif a.intent == "neutral":
                delta["material_output"] = 0.7
                delta["resource_resilience"] = 0.3
            else:
                delta["material_output"] = 0.2

            amount = positive_amount(delta)

            credit = OMK(
                id=self.next_id(),
                issuer="genesis",
                owner=a.id,
                operation_name="genesis_credit",
                operation_family="genesis",
                delta=delta,
                amount=amount,
                proof_quality=1.0,
                causal_share=1.0,
                step=0,
                source="genesis",
            )

            a.wallet.deposit(credit)

    # ------------------------------------------------------------
    # Operation choice
    # ------------------------------------------------------------

    def weighted_choice(self, choices, weights):
        total = sum(weights)
        r = self.rng.random() * total
        acc = 0.0

        for c, w in zip(choices, weights):
            acc += w
            if r <= acc:
                return c

        return choices[-1]

    def choose_operation(self, agent):
        if agent.intent == "noble":
            choices = [
                "restore_agency",
                "repair_harm",
                "truth_audit",
                "education",
                "norm_reform",
                "hierarchy_inversion_repair",
                "infrastructure_maintenance",
                "causal_intervention",
                "voluntary_behavior_contract",
                "produce_goods",
            ]
            weights = [1.25, 1.2, 1.0, 1.1, 0.8, 0.6, 0.8, 0.7, 0.55, 0.45]

        elif agent.intent == "neutral":
            choices = [
                "produce_goods",
                "infrastructure_maintenance",
                "truth_audit",
                "causal_intervention",
                "voluntary_behavior_contract",
                "education",
                "norm_reform",
                "repair_harm",
                "exploit_labor",
                "metric_hack",
            ]
            weights = [1.3, 0.9, 0.55, 0.6, 0.5, 0.45, 0.35, 0.25, 0.12, 0.08]

        else:
            choices = [
                "exploit_labor",
                "fake_truth_certificate",
                "coercive_behavior_purchase",
                "sabotage_competitor",
                "tyrant_hierarchy_inversion",
                "metric_hack",
                "self_created_need",
                "produce_goods",
                "truth_audit",
            ]
            weights = [1.2, 0.95, 0.9, 0.75, 0.8, 0.8, 0.55, 0.2, 0.1]

        family = self.weighted_choice(choices, weights)
        intensity = self.rng.uniform(0.45, 1.35)
        target = self.rng.choice(list(self.agents.keys()))

        if target == agent.id:
            target = None

        declared_metric = self.rng.choice(METRICS)
        flags = list(RED_FLAGS.get(family, []))
        private_gain = PRIVATE_GAIN[family] * intensity * (0.5 + agent.skill(family))

        return Operation(
            name=family + "_op",
            family=family,
            actor_id=agent.id,
            target_id=target,
            intensity=intensity,
            declared_metric=declared_metric,
            flags=flags,
            private_gain=private_gain,
        )

    # ------------------------------------------------------------
    # Execution and OMK minting
    # ------------------------------------------------------------

    def execute_operation(self, op):
        actor = self.agents[op.actor_id]
        before = self.state.score()

        delta = op.realized_delta(actor, self.state, self.rng)
        validation = self.governance.validate(op, delta, self.state, actor)

        minted = 0.0

        if validation.accepted:
            self.state.apply_delta(delta)
            after = self.state.score()

            if self.mode == "gmoe":
                minted = self.mint_omk(actor, op, delta)

                actor.reputation = clamp(actor.reputation + 0.25 * validation.score)
                actor.stake += 0.04 * minted

                if op.family == "produce_goods":
                    actor.goods += max(0.0, delta.get("material_output", 0.0)) * 1.3

            else:
                actor.fiat_balance += max(0.0, op.private_gain)
                actor.capital += max(0.0, op.private_gain) * 0.25
                actor.reputation = clamp(actor.reputation + 0.04 * validation.score)

                if op.family in ("produce_goods", "exploit_labor"):
                    actor.goods += max(0.0, delta.get("material_output", 0.0)) * 1.2

        else:
            after = before

            if self.mode == "gmoe":
                penalty = min(
                    actor.stake,
                    0.8
                    + 0.25 * len(op.flags)
                    + max(0.0, -validation.score) * 0.08,
                )
                actor.stake -= penalty
                actor.reputation = clamp(actor.reputation - 0.8 * penalty)

                if "self_caused_harm" in op.flags:
                    actor.self_created_need_flag = True

            else:
                actor.fiat_balance -= 0.1

        self.ledger.append(
            LedgerEntry(
                step=self.state.step,
                mode=self.mode,
                actor_id=actor.id,
                operation=op.family,
                accepted=validation.accepted,
                reason=validation.reason,
                delta=delta,
                score_before=before,
                score_after=after,
                minted=minted,
                private_gain=op.private_gain,
                flags=op.flags,
            )
        )

    def mint_omk(self, actor, op, delta):
        base_amount = positive_amount(delta)

        if base_amount <= 1e-9:
            return 0.0

        proof_quality = clamp(0.65 + 0.35 * actor.skill(op.family), 0.0, 1.0)
        causal_share = clamp(0.50 + 0.45 * actor.skill(op.family), 0.0, 1.0)

        amount = base_amount * proof_quality * causal_share

        actor_share = 0.75
        target_share = 0.10 if op.target_id in self.agents else 0.0
        repair_share = 0.10
        governance_share = 0.05 + (0.10 - target_share)

        distributions = [
            (actor.id, actor_share),
            ("__repair_fund__", repair_share),
            ("__governance_fund__", governance_share),
        ]

        if target_share > 0:
            distributions.append((op.target_id, target_share))

        for owner, share in distributions:
            if share <= 0:
                continue

            credit = OMK(
                id=self.next_id(),
                issuer="GMOE-MINT",
                owner=owner,
                operation_name=op.name,
                operation_family=op.family,
                delta=copy.deepcopy(delta),
                amount=amount * share,
                proof_quality=proof_quality,
                causal_share=causal_share,
                step=self.state.step,
                source="realized",
            )

            if owner == "__repair_fund__":
                self.repair_fund.deposit(credit)
            elif owner == "__governance_fund__":
                self.governance_fund.deposit(credit)
            else:
                self.agents[owner].wallet.deposit(credit)

        return amount

    # ------------------------------------------------------------
    # Markets
    # ------------------------------------------------------------

    def run_goods_market(self):
        buyers = [a for a in self.agents.values() if a.goods < 8.0]
        sellers = [a for a in self.agents.values() if a.goods > 18.0]

        self.rng.shuffle(buyers)
        self.rng.shuffle(sellers)

        for buyer in buyers[: max(1, len(buyers) // 2)]:
            if not sellers:
                break

            seller = self.rng.choice(sellers)

            if seller.goods <= 12.0:
                continue

            units = min(3.0, seller.goods - 12.0)
            price = units * (1.2 + 0.02 * (100.0 - self.state.metrics["resource_resilience"]))

            if self.mode == "gmoe":
                spent = buyer.wallet.spend(price, seller.id, self.next_id)

                if spent:
                    seller.wallet.deposit_many(spent)
                    seller.goods -= units
                    buyer.goods += units

            else:
                if buyer.fiat_balance >= price:
                    buyer.fiat_balance -= price
                    seller.fiat_balance += price
                    seller.goods -= units
                    buyer.goods += units

    def run_securities_market(self):
        if not self.securities:
            return

        firms = sorted(
            self.securities.values(),
            key=lambda s: self.agents[s.issuer].reputation
            + self.agents[s.issuer].capital * 0.2,
            reverse=True,
        )

        top = firms[:3]
        investors = list(self.agents.values())
        self.rng.shuffle(investors)

        for investor in investors[: max(2, len(investors) // 5)]:
            sec = self.rng.choice(top)
            issuer = self.agents[sec.issuer]

            if investor.id == issuer.id:
                continue

            shares = self.rng.uniform(0.2, 1.5)
            price = shares * sec.price * (0.8 + issuer.reputation / 120.0)

            if self.mode == "gmoe":
                spent = investor.wallet.spend(price, issuer.id, self.next_id)

                if spent:
                    issuer.wallet.deposit_many(spent)
                    investor.shares[sec.id] = investor.shares.get(sec.id, 0.0) + shares

            else:
                if investor.fiat_balance >= price:
                    investor.fiat_balance -= price
                    issuer.fiat_balance += price
                    investor.shares[sec.id] = investor.shares.get(sec.id, 0.0) + shares

    def distribute_dividends(self):
        for sec in self.securities.values():
            issuer = self.agents[sec.issuer]
            holders = [
                (a, a.shares.get(sec.id, 0.0))
                for a in self.agents.values()
                if a.shares.get(sec.id, 0.0) > 0
            ]

            total = sum(sh for _, sh in holders)

            if total <= 0:
                continue

            if self.mode == "gmoe":
                pool = min(issuer.wallet.balance() * 0.015, 2.5)

                if pool <= 0.01:
                    continue

                for holder, sh in holders:
                    amount = pool * sh / total
                    spent = issuer.wallet.spend(amount, holder.id, self.next_id)
                    holder.wallet.deposit_many(spent)

            else:
                pool = min(issuer.fiat_balance * 0.015, 2.5)

                if pool <= 0.01:
                    continue

                issuer.fiat_balance -= pool

                for holder, sh in holders:
                    holder.fiat_balance += pool * sh / total

    def run_credit_market(self):
        if self.mode == "gmoe":
            borrowers = [
                a
                for a in self.agents.values()
                if a.wallet.balance() < 4.0 and a.intent != "harmful"
            ]
            lenders = sorted(
                [a for a in self.agents.values() if a.wallet.balance() > 15.0],
                key=lambda a: a.wallet.balance(),
                reverse=True,
            )

            if borrowers and lenders:
                for b in borrowers[:3]:
                    lender = lenders[0]
                    family = max(GOOD_OPERATIONS, key=lambda f: b.skill(f))
                    amount = min(3.0, lender.wallet.balance() * 0.08)

                    if amount <= 0.2:
                        continue

                    spent = lender.wallet.spend(amount, b.id, self.next_id)

                    if spent:
                        b.wallet.deposit_many(spent)
                        self.credit_contracts.append(
                            CreditContract(
                                id="CR_%d_%s" % (self.state.step, b.id),
                                borrower=b.id,
                                lender=lender.id,
                                promised_family=family,
                                promised_amount=amount * 1.10,
                                stake=min(b.stake, amount),
                                due_step=self.state.step + 5,
                            )
                        )

        else:
            borrowers = [a for a in self.agents.values() if a.fiat_balance < 30.0]
            lenders = sorted(
                [a for a in self.agents.values() if a.fiat_balance > 150.0],
                key=lambda a: a.fiat_balance,
                reverse=True,
            )

            for b in borrowers[:3]:
                if not lenders:
                    break

                lender = lenders[0]
                amount = min(10.0, lender.fiat_balance * 0.05)

                lender.fiat_balance -= amount
                b.fiat_balance += amount

                self.credit_contracts.append(
                    CreditContract(
                        id="FIAT_CR_%d_%s" % (self.state.step, b.id),
                        borrower=b.id,
                        lender=lender.id,
                        promised_family="fiat",
                        promised_amount=amount * 1.15,
                        stake=min(b.stake, amount * 0.5),
                        due_step=self.state.step + 5,
                    )
                )

    def settle_credit_contracts(self):
        for c in list(self.credit_contracts):
            if c.fulfilled or c.due_step > self.state.step:
                continue

            borrower = self.agents[c.borrower]
            lender = self.agents[c.lender]

            if self.mode == "gmoe":
                spent = borrower.wallet.spend(c.promised_amount, lender.id, self.next_id)

                if spent:
                    lender.wallet.deposit_many(spent)
                    borrower.reputation = clamp(borrower.reputation + 1.0)
                    c.fulfilled = True
                else:
                    loss = min(borrower.stake, c.stake)
                    borrower.stake -= loss
                    borrower.reputation = clamp(borrower.reputation - 3.0 - loss * 0.2)
                    c.fulfilled = True

            else:
                if borrower.fiat_balance >= c.promised_amount:
                    borrower.fiat_balance -= c.promised_amount
                    lender.fiat_balance += c.promised_amount
                    c.fulfilled = True
                else:
                    loss = min(borrower.stake, c.stake)
                    borrower.stake -= loss
                    borrower.reputation = clamp(borrower.reputation - 2.0)
                    c.fulfilled = True

    def run_insurance_market(self):
        if self.mode == "gmoe":
            richest = sorted(
                self.agents.values(),
                key=lambda a: a.wallet.balance(),
                reverse=True,
            )
        else:
            richest = sorted(
                self.agents.values(),
                key=lambda a: a.fiat_balance,
                reverse=True,
            )

        if not richest:
            return

        insurer = richest[0]
        candidates = [
            a
            for a in self.agents.values()
            if a.id != insurer.id and a.insurance <= 0.0
        ]

        self.rng.shuffle(candidates)

        for holder in candidates[:2]:
            premium = 1.2
            coverage = 5.0

            if self.mode == "gmoe":
                spent = holder.wallet.spend(premium, insurer.id, self.next_id)

                if spent:
                    insurer.wallet.deposit_many(spent)
                    holder.insurance += coverage
                    self.insurance_contracts.append(
                        InsuranceContract(
                            id="IN_%d_%s" % (self.state.step, holder.id),
                            holder=holder.id,
                            insurer=insurer.id,
                            premium=premium,
                            coverage=coverage,
                            metric="freedom_from_harm",
                            active_until=self.state.step + 12,
                        )
                    )

            else:
                if holder.fiat_balance >= premium:
                    holder.fiat_balance -= premium
                    insurer.fiat_balance += premium
                    holder.insurance += coverage
                    self.insurance_contracts.append(
                        InsuranceContract(
                            id="IN_%d_%s" % (self.state.step, holder.id),
                            holder=holder.id,
                            insurer=insurer.id,
                            premium=premium,
                            coverage=coverage,
                            metric="freedom_from_harm",
                            active_until=self.state.step + 12,
                        )
                    )

    def maybe_external_shock(self):
        if self.shock_rate <= 0:
            return

        if self.rng.random() > self.shock_rate:
            return

        delta = empty_delta()
        delta["freedom_from_harm"] = -self.rng.uniform(1.0, 3.0)
        delta["resource_resilience"] = -self.rng.uniform(0.4, 1.7)
        delta["repair_capacity"] = -self.rng.uniform(0.2, 1.0)

        before = self.state.score()
        self.state.apply_delta(delta)
        after = self.state.score()

        self.ledger.append(
            LedgerEntry(
                step=self.state.step,
                mode=self.mode,
                actor_id="EXTERNAL",
                operation="external_shock",
                accepted=True,
                reason="exogenous shock",
                delta=delta,
                score_before=before,
                score_after=after,
                minted=0.0,
                private_gain=0.0,
                flags=["external"],
            )
        )

    # ------------------------------------------------------------
    # Simulation loop
    # ------------------------------------------------------------

    def step_once(self):
        self.state.step += 1

        score_start = self.state.score()

        self.maybe_external_shock()

        agents = list(self.agents.values())
        self.rng.shuffle(agents)

        active_agents = agents[: max(1, int(len(agents) * 0.55))]

        for a in active_agents:
            op = self.choose_operation(a)
            self.execute_operation(op)

        self.run_goods_market()
        self.run_securities_market()
        self.distribute_dividends()
        self.run_credit_market()
        self.settle_credit_contracts()
        self.run_insurance_market()

        self.history.append(
            {
                "step": self.state.step,
                "score_start": score_start,
                "score_end": self.state.score(),
                "distance": self.state.distance(),
                "total_omk": self.total_omk_balance(),
                "total_fiat": sum(a.fiat_balance for a in self.agents.values()),
                "accepted": sum(
                    1
                    for e in self.ledger
                    if e.step == self.state.step
                    and e.accepted
                    and e.operation != "external_shock"
                ),
                "rejected": sum(
                    1
                    for e in self.ledger
                    if e.step == self.state.step and not e.accepted
                ),
            }
        )

    def run(self, steps):
        for _ in range(steps):
            self.step_once()

    # ------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------

    def total_omk_balance(self):
        return (
            sum(a.wallet.balance() for a in self.agents.values())
            + self.repair_fund.balance()
            + self.governance_fund.balance()
        )

    def accepted_entries(self):
        return [
            e
            for e in self.ledger
            if e.accepted and e.operation != "external_shock"
        ]

    def rejected_entries(self):
        return [e for e in self.ledger if not e.accepted]

    def harmful_accepted_count(self):
        return sum(
            1
            for e in self.accepted_entries()
            if e.operation in HARMFUL_OPERATIONS
        )

    def positive_cone_violations_among_accepted(self):
        """
        In GMOE this should be 0.

        This is the machine-check of the postulate:

            accepted payment => positive metric contraction
        """
        count = 0

        for e in self.accepted_entries():
            if weighted_score(e.delta) <= 0:
                count += 1
                continue

            for m in PROTECTED:
                if e.delta.get(m, 0.0) < -0.05:
                    count += 1
                    break

        return count

    def cumulative_trade_score(self):
        return sum(weighted_score(e.delta) for e in self.accepted_entries())

    def monotonic_score_steps(self):
        if len(self.history) < 2:
            return 0, 0

        ok = 0
        total = 0
        prev = self.history[0]["score_end"]

        for h in self.history[1:]:
            total += 1
            if h["score_end"] + 1e-9 >= prev:
                ok += 1
            prev = h["score_end"]

        return ok, total

    def top_agents_by_money(self, n=5):
        if self.mode == "gmoe":
            return sorted(
                self.agents.values(),
                key=lambda a: a.wallet.balance(),
                reverse=True,
            )[:n]

        return sorted(
            self.agents.values(),
            key=lambda a: a.fiat_balance,
            reverse=True,
        )[:n]

    def operation_counts(self):
        counts = {}

        for e in self.ledger:
            key = (e.operation, e.accepted)
            counts[key] = counts.get(key, 0) + 1

        return counts

    def report(self):
        initial = self.history[0]["score_start"] if self.history else self.state.score()
        final = self.state.score()

        accepted = self.accepted_entries()
        rejected = self.rejected_entries()

        monotonic_ok, monotonic_total = self.monotonic_score_steps()

        lines = []
        lines.append("=" * 78)
        lines.append("Galactic Metric Operator Economy Simulation Report")
        lines.append(
            "mode=%s seed=%s steps=%s agents=%s shock_rate=%.3f"
            % (self.mode, self.seed, self.state.step, len(self.agents), self.shock_rate)
        )
        lines.append("-" * 78)
        lines.append("Initial nobility index: %.3f" % initial)
        lines.append("Final nobility index:   %.3f" % final)
        lines.append("Change:                 %+0.3f" % (final - initial))
        lines.append("Final metric distance to target: %.3f" % self.state.distance())
        lines.append("Accepted transactions:  %d" % len(accepted))
        lines.append("Rejected transactions:  %d" % len(rejected))
        lines.append("Accepted harmful ops:   %d" % self.harmful_accepted_count())
        lines.append(
            "Positive-cone violations among accepted: %d"
            % self.positive_cone_violations_among_accepted()
        )
        lines.append(
            "Cumulative accepted trade weighted score: %+0.3f"
            % self.cumulative_trade_score()
        )

        if monotonic_total > 0:
            lines.append(
                "Score nondecreasing step transitions: %d/%d"
                % (monotonic_ok, monotonic_total)
            )

        if self.mode == "gmoe":
            lines.append("Total countable OMK stack balance: %.3f" % self.total_omk_balance())
            lines.append(
                "Repair fund balance: %.3f | Governance fund balance: %.3f"
                % (self.repair_fund.balance(), self.governance_fund.balance())
            )
        else:
            lines.append(
                "Total scalar fiat balance: %.3f"
                % sum(a.fiat_balance for a in self.agents.values())
            )

        lines.append("-" * 78)
        lines.append("Final metrics:")

        for m in METRICS:
            lines.append("  %-24s %7.3f" % (m + ":", self.state.metrics[m]))

        lines.append("-" * 78)
        lines.append("Top agents by money:")

        for a in self.top_agents_by_money(5):
            money = a.wallet.balance() if self.mode == "gmoe" else a.fiat_balance
            lines.append(
                "  %-16s intent=%-7s money=%8.3f rep=%6.2f stake=%6.2f goods=%6.2f"
                % (a.name, a.intent, money, a.reputation, a.stake, a.goods)
            )

        if self.mode == "gmoe":
            richest = self.top_agents_by_money(1)[0]
            lines.append("-" * 78)
            lines.append("Example of countable stacked money in richest wallet:")
            lines.append(richest.wallet.top_summary(7))

        lines.append("-" * 78)
        lines.append("Operation counts:")

        counts = self.operation_counts()
        all_ops = sorted(set(k[0] for k in counts.keys()))

        for op in all_ops:
            acc = counts.get((op, True), 0)
            rej = counts.get((op, False), 0)
            lines.append("  %-32s accepted=%4d rejected=%4d" % (op, acc, rej))

        lines.append("=" * 78)

        return "\n".join(lines)


# ============================================================
# 8. Comparison
# ============================================================

def compare(steps, agents, seed, shock_rate):
    gmoe = Economy("gmoe", agents, seed, shock_rate)
    base = Economy("baseline", agents, seed, shock_rate)

    gmoe.run(steps)
    base.run(steps)

    lines = []
    lines.append(gmoe.report())
    lines.append("")
    lines.append(base.report())
    lines.append("")
    lines.append("Comparison conclusion:")
    lines.append(
        "  GMOE accepts only operator-metric payments inside the valid positive cone."
    )
    lines.append(
        "  Therefore accepted GMOE trades have zero positive-cone violations by construction."
    )
    lines.append(
        "  Baseline scalar money clears private-profit trades, including harmful operations."
    )
    lines.append(
        "  Final nobility-index difference GMOE - baseline: %+0.3f"
        % (gmoe.state.score() - base.state.score())
    )

    if gmoe.positive_cone_violations_among_accepted() == 0:
        lines.append(
            "  Machine check: every accepted GMOE trade was a positive metric contraction."
        )

    return "\n".join(lines)


# ============================================================
# 9. Main
# ============================================================

def main():
    parser = argparse.ArgumentParser(
        description="Galactic Metric Operator Economy simulation"
    )

    parser.add_argument("--mode", choices=["gmoe", "baseline"], default="gmoe")
    parser.add_argument("--steps", type=int, default=160)
    parser.add_argument("--agents", type=int, default=48)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument(
        "--shock-rate",
        type=float,
        default=0.0,
        help="probability of exogenous harmful shock per step",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="run GMOE and baseline with the same seed",
    )

    args = parser.parse_args()

    if args.compare:
        print(compare(args.steps, args.agents, args.seed, args.shock_rate))
    else:
        econ = Economy(args.mode, args.agents, args.seed, args.shock_rate)
        econ.run(args.steps)
        print(econ.report())


if __name__ == "__main__":
    main()
