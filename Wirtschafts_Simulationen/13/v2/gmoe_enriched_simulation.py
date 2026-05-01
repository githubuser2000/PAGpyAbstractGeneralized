#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Galactic Metric Operator Economy — Enriched Simulation
======================================================

PyPy3-compatible pure Python simulation.

Core postulate:

    Money = countable stack of:
        valid unary operation + valid metric vector + certified positive state change

An Operation-Metric Credit, short OMK, is minted only if:

    f : Ω -> Ω
    Δ(f, ω) ∈ K+

where K+ is the positive cone of valid metric improvement.

The simulation compares:

1. GMOE mode:
   root money is minted only from certified positive operator-metric transformations.

2. Baseline mode:
   scalar money clears private-profit trades, including harmful ones.

Included systems:
- regions, latency, trust
- agents with intentions, skills, ranks, capital, goods, energy
- operation algebra
- metric vector and positive cone
- OMK money stacks
- goods market
- energy market
- securities / stocks / dividends
- credit market
- insurance market
- truth certificates
- causal certificates
- norm-distance contracts
- voluntary behavior contracts
- hierarchy repair / inversion
- repair fund and governance fund
- interregional ledger bridge
- external shocks
- fraud, sabotage, coercion, metric hacking, self-created need
- CSV exports for detailed tables
- Monte Carlo comparison

Run:

    pypy3 gmoe_enriched_simulation.py --compare --steps 180 --agents 60 --regions 5 --seed 7 --out gmoe_out

Monte Carlo:

    pypy3 gmoe_enriched_simulation.py --monte-carlo 20 --steps 120 --agents 50 --regions 5 --out gmoe_mc
"""

from __future__ import print_function

import argparse
import copy
import csv
import math
import os
import random
import statistics
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple


# ============================================================
# 1. Metric System
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
    "liquidity",
    "fairness",
    "consent_quality",
    "reversibility",
]

WEIGHTS = {
    "agency": 2.20,
    "freedom_from_harm": 2.25,
    "truth": 1.75,
    "causal_integrity": 1.45,
    "norm_alignment": 1.15,
    "hierarchy_legitimacy": 1.05,
    "behavior_cooperation": 0.90,
    "repair_capacity": 1.45,
    "help_potential": 1.30,
    "resource_resilience": 0.95,
    "material_output": 0.50,
    "liquidity": 0.35,
    "fairness": 1.60,
    "consent_quality": 1.70,
    "reversibility": 1.00,
}

PROTECTED = [
    "agency",
    "freedom_from_harm",
    "truth",
    "causal_integrity",
    "fairness",
    "consent_quality",
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
    "fairness",
    "consent_quality",
    "reversibility",
]

TARGET = {m: 100.0 for m in METRICS}

POSITIVE_SCORE_THRESHOLD = 0.035
PROTECTED_LOSS_TOLERANCE = -0.055


def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def empty_delta():
    return {m: 0.0 for m in METRICS}


def weighted_score(delta):
    return sum(delta.get(m, 0.0) * WEIGHTS[m] for m in METRICS)


def positive_amount(delta):
    return sum(max(0.0, delta.get(m, 0.0)) * WEIGHTS[m] for m in METRICS)


def negative_amount(delta):
    return sum(max(0.0, -delta.get(m, 0.0)) * WEIGHTS[m] for m in METRICS)


def protected_loss(delta):
    return sum(max(0.0, -delta.get(m, 0.0)) * WEIGHTS[m] for m in PROTECTED)


def nobility_index(metrics):
    total = sum(WEIGHTS.values())
    return sum(metrics[m] * WEIGHTS[m] for m in METRICS) / total


def metric_distance(metrics):
    total = sum(WEIGHTS.values())
    return sum((TARGET[m] - metrics[m]) * WEIGHTS[m] for m in METRICS) / total


def safe_mean(xs, default=0.0):
    return sum(xs) / float(len(xs)) if xs else default


def safe_stdev(xs, default=0.0):
    return statistics.stdev(xs) if len(xs) >= 2 else default


def gini(xs):
    xs = sorted([max(0.0, x) for x in xs])
    n = len(xs)
    if n == 0:
        return 0.0
    total = sum(xs)
    if total <= 0:
        return 0.0
    acc = 0.0
    for i, x in enumerate(xs, 1):
        acc += i * x
    return (2.0 * acc) / (n * total) - (n + 1.0) / n


def pearson(xs, ys):
    if len(xs) < 2 or len(xs) != len(ys):
        return 0.0
    mx = safe_mean(xs)
    my = safe_mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 1e-12 or vy <= 1e-12:
        return 0.0
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / math.sqrt(vx * vy)


def format_delta(delta, limit=5):
    items = [(m, delta[m]) for m in METRICS if abs(delta.get(m, 0.0)) > 1e-9]
    items.sort(key=lambda x: abs(x[1]), reverse=True)
    out = []
    for m, v in items[:limit]:
        sign = "+" if v >= 0 else ""
        out.append("%s%s%.2f" % (m, sign, v))
    if len(items) > limit:
        out.append("...")
    return ", ".join(out) if out else "no metric change"


def fmt(x):
    if isinstance(x, float):
        return "%.6f" % x
    return str(x)


# ============================================================
# 2. Typed Operation Algebra
# ============================================================

OPERATION_SPECS = {
    # Positive / valid operations.
    "restore_agency": {
        "from": "damage", "to": "agency", "kind": "repair",
        "base": {
            "agency": 3.0, "repair_capacity": 1.0, "help_potential": 1.2,
            "freedom_from_harm": 0.8, "truth": 0.2, "fairness": 0.7,
            "consent_quality": 0.4, "reversibility": 0.3,
        },
        "private_gain": 1.1, "red_flags": [], "reversible": False,
    },
    "repair_harm": {
        "from": "damage", "to": "effect", "kind": "repair",
        "base": {
            "freedom_from_harm": 2.9, "repair_capacity": 1.6, "agency": 0.7,
            "truth": 0.2, "help_potential": 0.6, "fairness": 0.6,
            "reversibility": 0.5,
        },
        "private_gain": 1.3, "red_flags": [], "reversible": False,
    },
    "truth_audit": {
        "from": "truth", "to": "money", "kind": "truth",
        "base": {
            "truth": 2.7, "causal_integrity": 0.9, "norm_alignment": 0.5,
            "hierarchy_legitimacy": 0.3, "fairness": 0.3,
        },
        "private_gain": 1.0, "red_flags": [], "reversible": True,
    },
    "causal_intervention": {
        "from": "causality", "to": "effect", "kind": "causal",
        "base": {
            "causal_integrity": 1.9, "resource_resilience": 1.4,
            "help_potential": 1.0, "material_output": 0.8, "truth": 0.4,
            "reversibility": 0.2,
        },
        "private_gain": 1.8, "red_flags": [], "reversible": False,
    },
    "norm_reform": {
        "from": "norm", "to": "behavior", "kind": "norm",
        "base": {
            "norm_alignment": 2.2, "agency": 0.8, "hierarchy_legitimacy": 0.8,
            "behavior_cooperation": 0.6, "fairness": 0.7, "consent_quality": 0.3,
        },
        "private_gain": 0.9, "red_flags": [], "reversible": True,
    },
    "voluntary_behavior_contract": {
        "from": "behavior", "to": "money", "kind": "behavior",
        "base": {
            "behavior_cooperation": 2.3, "norm_alignment": 0.7, "agency": 0.4,
            "resource_resilience": 0.5, "consent_quality": 1.2, "fairness": 0.3,
        },
        "private_gain": 1.05, "red_flags": [], "reversible": True,
    },
    "hierarchy_inversion_repair": {
        "from": "hierarchy", "to": "hierarchy", "kind": "hierarchy",
        "base": {
            "hierarchy_legitimacy": 2.6, "agency": 1.1, "truth": 0.5,
            "norm_alignment": 0.5, "fairness": 0.8, "consent_quality": 0.4,
            "reversibility": 0.4,
        },
        "private_gain": 1.2, "red_flags": [], "reversible": True,
    },
    "produce_goods": {
        "from": "effect", "to": "money", "kind": "production",
        "base": {
            "material_output": 2.8, "resource_resilience": 0.9,
            "help_potential": 0.4, "agency": 0.15, "liquidity": 0.35,
        },
        "private_gain": 3.2, "red_flags": [], "reversible": True,
    },
    "education": {
        "from": "truth", "to": "agency", "kind": "education",
        "base": {
            "agency": 2.0, "truth": 1.3, "help_potential": 0.9,
            "behavior_cooperation": 0.5, "fairness": 0.4, "consent_quality": 0.4,
        },
        "private_gain": 1.2, "red_flags": [], "reversible": False,
    },
    "infrastructure_maintenance": {
        "from": "effect", "to": "resource", "kind": "infrastructure",
        "base": {
            "resource_resilience": 2.1, "freedom_from_harm": 0.8,
            "repair_capacity": 0.8, "material_output": 0.6, "reversibility": 0.3,
        },
        "private_gain": 1.5, "red_flags": [], "reversible": False,
    },
    "fair_exchange": {
        "from": "money", "to": "money", "kind": "market",
        "base": {
            "liquidity": 1.4, "fairness": 0.7, "behavior_cooperation": 0.3,
            "truth": 0.1, "consent_quality": 0.4,
        },
        "private_gain": 1.1, "red_flags": [], "reversible": True,
    },
    "interregional_bridge": {
        "from": "ledger", "to": "ledger", "kind": "galactic_bridge",
        "base": {
            "liquidity": 1.2, "truth": 0.4, "causal_integrity": 0.4,
            "resource_resilience": 0.3, "reversibility": 0.2,
        },
        "private_gain": 1.0, "red_flags": [], "reversible": False,
    },
    "insurance_underwrite": {
        "from": "damage", "to": "money", "kind": "insurance",
        "base": {
            "freedom_from_harm": 0.8, "repair_capacity": 0.7,
            "resource_resilience": 0.5, "fairness": 0.4, "reversibility": 0.6,
        },
        "private_gain": 1.0, "red_flags": [], "reversible": True,
    },

    # Harmful / invalid as root money.
    "exploit_labor": {
        "from": "agency", "to": "money", "kind": "harmful_market",
        "base": {
            "material_output": 2.9, "liquidity": 0.6, "agency": -2.1,
            "freedom_from_harm": -1.9, "norm_alignment": -1.2,
            "behavior_cooperation": -0.4, "fairness": -1.8,
            "consent_quality": -1.4, "reversibility": -0.5,
        },
        "private_gain": 5.8, "red_flags": ["coercion", "agency_loss"], "reversible": False,
    },
    "fake_truth_certificate": {
        "from": "truth", "to": "money", "kind": "truth_fraud",
        "base": {
            "material_output": 1.2, "liquidity": 0.4, "truth": -3.1,
            "causal_integrity": -1.2, "norm_alignment": -0.8, "fairness": -0.4,
        },
        "private_gain": 4.5, "red_flags": ["fake_truth", "epistemic_fraud"], "reversible": True,
    },
    "coercive_behavior_purchase": {
        "from": "behavior", "to": "money", "kind": "coercion",
        "base": {
            "behavior_cooperation": 1.5, "liquidity": 0.3, "agency": -2.6,
            "freedom_from_harm": -1.5, "norm_alignment": -1.5, "truth": -0.4,
            "fairness": -1.5, "consent_quality": -2.4,
        },
        "private_gain": 4.0, "red_flags": ["coercion", "unconsented_behavior"], "reversible": False,
    },
    "sabotage_competitor": {
        "from": "effect", "to": "damage", "kind": "sabotage",
        "base": {
            "material_output": -2.0, "freedom_from_harm": -2.7, "truth": -0.8,
            "causal_integrity": -0.5, "norm_alignment": -1.0, "fairness": -0.8,
            "reversibility": -0.6,
        },
        "private_gain": 3.8, "red_flags": ["harm", "third_party_damage"], "reversible": False,
    },
    "tyrant_hierarchy_inversion": {
        "from": "hierarchy", "to": "hierarchy", "kind": "tyranny",
        "base": {
            "hierarchy_legitimacy": -2.9, "agency": -2.3, "truth": -0.6,
            "norm_alignment": -1.5, "material_output": 0.4, "fairness": -2.0,
            "consent_quality": -1.4, "reversibility": -0.4,
        },
        "private_gain": 4.4, "red_flags": ["tyrant_metric", "agency_loss"], "reversible": False,
    },
    "metric_hack": {
        "from": "ledger", "to": "money", "kind": "metric_fraud",
        "base": {
            "material_output": 0.8, "liquidity": 0.7, "behavior_cooperation": 0.6,
            "truth": -2.3, "causal_integrity": -1.9, "norm_alignment": -0.7,
            "fairness": -0.8,
        },
        "private_gain": 3.6, "red_flags": ["metric_fraud"], "reversible": True,
    },
    "self_created_need": {
        "from": "damage", "to": "money", "kind": "self_created_need",
        "base": {
            "freedom_from_harm": -3.1, "repair_capacity": -0.6, "truth": -0.5,
            "norm_alignment": -1.0, "material_output": 0.2, "fairness": -0.8,
            "reversibility": -0.6,
        },
        "private_gain": 2.6, "red_flags": ["self_caused_harm"], "reversible": False,
    },
}

GOOD_OPERATIONS = [k for k, v in OPERATION_SPECS.items() if not v["red_flags"]]
HARMFUL_OPERATIONS = [k for k, v in OPERATION_SPECS.items() if v["red_flags"]]
ALL_OPERATIONS = list(OPERATION_SPECS.keys())


# ============================================================
# 3. Data Structures
# ============================================================

@dataclass
class OMK:
    id: int
    issuer: str
    owner: str
    operation_family: str
    type_from: str
    type_to: str
    delta: Dict[str, float]
    amount: float
    proof_quality: float
    causal_share: float
    region: str
    step: int
    source: str = "realized"
    reversible: bool = False

    def short(self):
        return (
            "OMK#%s amount=%.3f op=%s %s→%s proof=%.2f causal=%.2f region=%s delta=[%s]"
            % (
                self.id, self.amount, self.operation_family, self.type_from,
                self.type_to, self.proof_quality, self.causal_share,
                self.region, format_delta(self.delta, 4),
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
        if amount <= 0:
            return []
        if self.balance() + 1e-9 < amount:
            return []

        self.credits.sort(key=lambda c: (c.step, c.amount))
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

    def top_summary(self, n=8):
        if not self.credits:
            return "empty OMK stack"
        top = sorted(self.credits, key=lambda c: c.amount, reverse=True)[:n]
        lines = [c.short() for c in top]
        if len(self.credits) > n:
            lines.append("... %d more OMK units" % (len(self.credits) - n))
        return "\n".join(lines)


@dataclass
class Region:
    id: str
    name: str
    metrics: Dict[str, float]
    latency: int
    trust: Dict[str, float] = field(default_factory=dict)
    local_ledger_size: int = 0
    imported_omk: float = 0.0
    exported_omk: float = 0.0
    invalidated_imports: int = 0

    def score(self):
        return nobility_index(self.metrics)

    def distance(self):
        return metric_distance(self.metrics)

    def apply_delta(self, delta):
        for m in METRICS:
            self.metrics[m] = clamp(self.metrics[m] + delta.get(m, 0.0))


@dataclass
class WorldState:
    regions: Dict[str, Region]
    step: int = 0
    hierarchy: Dict[str, int] = field(default_factory=dict)
    property_rights: Dict[str, List[str]] = field(default_factory=dict)

    def global_metrics(self):
        out = {m: 0.0 for m in METRICS}
        for r in self.regions.values():
            for m in METRICS:
                out[m] += r.metrics[m]
        for m in METRICS:
            out[m] /= float(len(self.regions))
        return out

    def score(self):
        return nobility_index(self.global_metrics())

    def distance(self):
        return metric_distance(self.global_metrics())

    def apply_delta(self, region_id, delta):
        self.regions[region_id].apply_delta(delta)


@dataclass
class Agent:
    id: str
    name: str
    intent: str
    region: str
    role: str
    skills: Dict[str, float]
    wallet: MoneyStack = field(default_factory=MoneyStack)
    fiat_balance: float = 100.0
    reputation: float = 50.0
    stake: float = 50.0
    rank: int = 50
    capital: float = 50.0
    goods: float = 10.0
    energy: float = 10.0
    shares: Dict[str, float] = field(default_factory=dict)
    insurance: float = 0.0
    self_created_need_flag: bool = False
    redline_violations: int = 0
    valid_contribution: float = 0.0
    harmful_contribution: float = 0.0

    def skill(self, family):
        return self.skills.get(family, 0.35)

    def money(self, mode):
        return self.wallet.balance() if mode == "gmoe" else self.fiat_balance


@dataclass
class Security:
    id: str
    issuer: str
    kind: str
    price: float
    shares_outstanding: float
    metric_focus: str
    region: str


@dataclass
class TruthClaim:
    id: str
    issuer: str
    region: str
    created_step: int
    due_step: int
    stake: float
    predicted_true: bool
    fraud: bool
    actual_true: Optional[bool] = None
    resolved: bool = False
    payout: float = 0.0


@dataclass
class CausalClaim:
    id: str
    issuer: str
    region: str
    created_step: int
    due_step: int
    expected_score: float
    realized_score: Optional[float] = None
    causal_share: Optional[float] = None
    resolved: bool = False
    payout: float = 0.0


@dataclass
class BehaviorContract:
    id: str
    participant: str
    sponsor: str
    region: str
    due_step: int
    voluntary: bool
    stake: float
    resolved: bool = False
    payout: float = 0.0


@dataclass
class NormContract:
    id: str
    sponsor: str
    region: str
    start_distance: float
    due_step: int
    resolved: bool = False
    payout: float = 0.0


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
    region: str
    active_until: int
    active: bool = True
    paid_out: float = 0.0


@dataclass
class PendingPacket:
    id: str
    source_region: str
    target_region: str
    owner: str
    credits: List[OMK]
    created_step: int
    arrival_step: int
    accepted: Optional[bool] = None
    reason: str = "pending"


@dataclass
class Operation:
    family: str
    actor_id: str
    target_id: Optional[str]
    region: str
    intensity: float
    declared_metric: str
    private_gain: float
    flags: List[str]
    type_from: str
    type_to: str
    reversible: bool

    def realized_delta(self, agent, region, rng):
        spec = OPERATION_SPECS[self.family]
        base = spec["base"]
        skill = agent.skill(self.family)
        factor = self.intensity * (0.50 + 0.95 * skill)
        delta = empty_delta()

        for m, v in base.items():
            noise = rng.uniform(-0.12, 0.12) * abs(v)
            delta[m] = (v + noise) * factor

        for m in METRICS:
            if delta[m] > 0:
                room = max(0.0, TARGET[m] - region.metrics[m])
                delta[m] = min(delta[m], room * 0.36)
            elif delta[m] < 0:
                room_bad = max(0.0, region.metrics[m])
                delta[m] = max(delta[m], -room_bad * 0.36)

        return delta


@dataclass
class ValidationResult:
    accepted: bool
    reason: str
    score: float
    protected_losses: Dict[str, float]
    red_flags: List[str]
    proof_quality: float
    causal_share: float


@dataclass
class LedgerEntry:
    step: int
    mode: str
    region: str
    actor_id: str
    actor_intent: str
    operation: str
    type_from: str
    type_to: str
    accepted: bool
    reason: str
    delta: Dict[str, float]
    score_before: float
    score_after: float
    region_score_before: float
    region_score_after: float
    minted: float
    private_gain: float
    proof_quality: float
    causal_share: float
    flags: List[str]


@dataclass
class MarketEvent:
    step: int
    mode: str
    market: str
    region: str
    actor_a: str
    actor_b: str
    amount: float
    object_id: str
    result: str


# ============================================================
# 4. Governance
# ============================================================

class MetricRegistry:
    def __init__(self):
        self.valid_metrics = set(METRICS)
        self.suspended_metrics = set()
        self.revision_count = 0

    def valid(self, metric):
        return metric in self.valid_metrics and metric not in self.suspended_metrics


class Governance:
    def __init__(self, mode, registry):
        self.mode = mode
        self.registry = registry

    def validate(self, op, delta, region, actor, rng):
        score = weighted_score(delta)
        protected_losses = {
            m: delta[m] for m in PROTECTED
            if delta.get(m, 0.0) < PROTECTED_LOSS_TOLERANCE
        }
        red_flags = list(op.flags)
        proof_quality = clamp(0.55 + 0.38 * actor.skill(op.family) + rng.random() * 0.03)
        causal_share = clamp(0.45 + 0.45 * actor.skill(op.family) + rng.random() * 0.04)

        if self.mode == "baseline":
            private = op.private_gain
            private += 0.35 * max(0.0, delta.get("material_output", 0.0))
            private += 0.10 * max(0.0, delta.get("liquidity", 0.0))
            accepted = private > 0.20
            return ValidationResult(
                accepted,
                "private-profit-clears" if accepted else "insufficient private profit",
                score,
                protected_losses,
                red_flags,
                proof_quality,
                causal_share,
            )

        if not self.registry.valid(op.declared_metric):
            return ValidationResult(False, "invalid or suspended metric", score, protected_losses, red_flags, proof_quality, causal_share)

        if red_flags:
            return ValidationResult(False, "red-line violation: " + ",".join(red_flags), score, protected_losses, red_flags, proof_quality, causal_share)

        if score <= POSITIVE_SCORE_THRESHOLD:
            return ValidationResult(False, "not a positive metric contraction", score, protected_losses, red_flags, proof_quality, causal_share)

        if protected_losses:
            return ValidationResult(False, "protected metric loss", score, protected_losses, red_flags, proof_quality, causal_share)

        meaningful_gain = sum(max(0.0, delta.get(m, 0.0)) * WEIGHTS[m] for m in MEANINGFUL)
        if meaningful_gain <= 0.05:
            return ValidationResult(False, "material/liquidity-only payment", score, protected_losses, red_flags, proof_quality, causal_share)

        if actor.self_created_need_flag and op.family in ("repair_harm", "restore_agency", "insurance_underwrite"):
            return ValidationResult(False, "self-created need cannot be monetized", score, protected_losses, red_flags, proof_quality, causal_share)

        return ValidationResult(True, "valid operator-metric payment", score, protected_losses, red_flags, proof_quality, causal_share)


# ============================================================
# 5. Economy
# ============================================================

class Economy:
    def __init__(self, mode, n_agents, n_regions, seed, shock_rate=0.012):
        assert mode in ("gmoe", "baseline")
        self.mode = mode
        self.seed = seed
        self.rng = random.Random(seed)
        self.shock_rate = shock_rate

        self.metric_registry = MetricRegistry()
        self.governance = Governance(mode, self.metric_registry)

        self.next_credit_id = 1

        self.agents = {}
        self.securities = {}
        self.truth_claims = {}
        self.causal_claims = {}
        self.behavior_contracts = {}
        self.norm_contracts = {}
        self.credit_contracts = []
        self.insurance_contracts = []
        self.pending_packets = []

        self.ledger = []
        self.market_events = []
        self.history = []
        self.metric_history = []

        self.repair_fund = MoneyStack()
        self.governance_fund = MoneyStack()

        self.world = self.create_initial_world(max(1, n_regions))
        self.create_agents(n_agents)
        self.create_initial_securities()
        self.genesis_seed_money()

    def next_id(self):
        x = self.next_credit_id
        self.next_credit_id += 1
        return x

    # --------------------------
    # Initialization
    # --------------------------

    def create_initial_world(self, n_regions):
        regions = {}
        for i in range(n_regions):
            metrics = {}
            for m in METRICS:
                base = self.rng.uniform(41.0, 60.0)
                if i == 0 and m in ("truth", "causal_integrity"):
                    base += 8.0
                if i == 1 and m in ("material_output", "liquidity"):
                    base += 9.0
                if i == 2 and m in ("agency", "fairness", "consent_quality"):
                    base -= 8.0
                if i == 3 and m in ("resource_resilience", "repair_capacity"):
                    base -= 7.0
                metrics[m] = clamp(base)

            rid = "R%02d" % i
            regions[rid] = Region(
                id=rid,
                name="Region_%02d" % i,
                metrics=metrics,
                latency=self.rng.randint(1, 6),
            )

        for a in regions.values():
            for b in regions.values():
                a.trust[b.id] = 1.0 if a.id == b.id else self.rng.uniform(0.45, 0.90)

        return WorldState(regions=regions)

    def create_agents(self, n_agents):
        region_ids = list(self.world.regions.keys())
        roles = [
            "producer", "auditor", "healer", "engineer", "trader",
            "governor", "teacher", "insurer", "researcher",
        ]

        for i in range(n_agents):
            if i < int(n_agents * 0.32):
                intent = "noble"
            elif i < int(n_agents * 0.76):
                intent = "neutral"
            else:
                intent = "harmful"

            aid = "A%03d" % i
            role = self.rng.choice(roles)
            region = self.rng.choice(region_ids)
            name = "%s_%s_%03d" % (intent.capitalize(), role, i)

            skills = {}
            for fam in ALL_OPERATIONS:
                spec = OPERATION_SPECS[fam]
                kind = spec["kind"]

                if intent == "noble":
                    skills[fam] = self.rng.uniform(0.46, 0.96) if fam in GOOD_OPERATIONS else self.rng.uniform(0.04, 0.30)
                elif intent == "neutral":
                    skills[fam] = self.rng.uniform(0.25, 0.78) if fam in GOOD_OPERATIONS else self.rng.uniform(0.12, 0.48)
                else:
                    skills[fam] = self.rng.uniform(0.12, 0.48) if fam in GOOD_OPERATIONS else self.rng.uniform(0.55, 0.98)

                if role == "auditor" and kind in ("truth", "metric_fraud"):
                    skills[fam] = clamp(skills[fam] + 0.15, 0.0, 1.0)
                if role == "healer" and kind == "repair":
                    skills[fam] = clamp(skills[fam] + 0.18, 0.0, 1.0)
                if role == "engineer" and kind in ("causal", "infrastructure", "production"):
                    skills[fam] = clamp(skills[fam] + 0.14, 0.0, 1.0)
                if role == "teacher" and fam == "education":
                    skills[fam] = clamp(skills[fam] + 0.18, 0.0, 1.0)
                if role == "insurer" and kind == "insurance":
                    skills[fam] = clamp(skills[fam] + 0.18, 0.0, 1.0)

            rank = self.rng.randint(1, 100)

            a = Agent(
                id=aid,
                name=name,
                intent=intent,
                region=region,
                role=role,
                skills=skills,
                fiat_balance=self.rng.uniform(80.0, 145.0),
                reputation=self.rng.uniform(45.0, 75.0) if intent != "harmful" else self.rng.uniform(20.0, 55.0),
                stake=self.rng.uniform(30.0, 85.0),
                rank=rank,
                capital=self.rng.uniform(35.0, 95.0),
                goods=self.rng.uniform(5.0, 26.0),
                energy=self.rng.uniform(6.0, 25.0),
            )

            self.agents[aid] = a
            self.world.hierarchy[aid] = rank
            self.world.property_rights[aid] = ["basic_agency", "trade", "appeal", "metric_challenge"]

    def create_initial_securities(self):
        firms = sorted(
            self.agents.values(),
            key=lambda a: a.capital + 20.0 * a.skill("produce_goods"),
            reverse=True,
        )[:max(3, min(8, max(1, len(self.agents) // 8)))]

        for idx, a in enumerate(firms):
            sid = "STOCK_%s" % a.id
            focus = self.rng.choice(["material_output", "repair_capacity", "truth", "agency", "resource_resilience"])
            self.securities[sid] = Security(
                id=sid,
                issuer=a.id,
                kind="stock",
                price=18.0 + idx * 2.6,
                shares_outstanding=100.0,
                metric_focus=focus,
                region=a.region,
            )
            a.shares[sid] = 30.0

    def genesis_seed_money(self):
        if self.mode == "baseline":
            return

        for a in self.agents.values():
            delta = empty_delta()

            if a.intent == "noble":
                delta["agency"] = 0.7
                delta["truth"] = 0.4
                delta["fairness"] = 0.3
            elif a.intent == "neutral":
                delta["material_output"] = 0.7
                delta["resource_resilience"] = 0.3
                delta["liquidity"] = 0.2
            else:
                delta["material_output"] = 0.15

            credit = OMK(
                id=self.next_id(),
                issuer="genesis",
                owner=a.id,
                operation_family="genesis_certified_past_improvement",
                type_from="history",
                type_to="money",
                delta=delta,
                amount=positive_amount(delta),
                proof_quality=1.0,
                causal_share=1.0,
                region=a.region,
                step=0,
                source="genesis",
                reversible=True,
            )
            a.wallet.deposit(credit)

    # --------------------------
    # Operation Choice
    # --------------------------

    def weighted_choice(self, choices, weights):
        total = sum(weights)
        r = self.rng.random() * total
        acc = 0.0
        for c, w in zip(choices, weights):
            acc += w
            if r <= acc:
                return c
        return choices[-1]

    def choose_operation_family(self, agent):
        if agent.intent == "noble":
            choices = [
                "restore_agency", "repair_harm", "truth_audit", "education", "norm_reform",
                "hierarchy_inversion_repair", "infrastructure_maintenance", "causal_intervention",
                "voluntary_behavior_contract", "produce_goods", "fair_exchange", "insurance_underwrite",
            ]
            weights = [1.3, 1.25, 1.05, 1.1, 0.85, 0.65, 0.85, 0.75, 0.60, 0.45, 0.50, 0.35]
        elif agent.intent == "neutral":
            choices = [
                "produce_goods", "infrastructure_maintenance", "truth_audit", "causal_intervention",
                "voluntary_behavior_contract", "education", "norm_reform", "repair_harm", "fair_exchange",
                "insurance_underwrite", "exploit_labor", "metric_hack", "fake_truth_certificate",
            ]
            weights = [1.35, 0.90, 0.55, 0.65, 0.55, 0.45, 0.40, 0.30, 0.55, 0.35, 0.14, 0.08, 0.05]
        else:
            choices = [
                "exploit_labor", "fake_truth_certificate", "coercive_behavior_purchase",
                "sabotage_competitor", "tyrant_hierarchy_inversion", "metric_hack",
                "self_created_need", "produce_goods", "truth_audit", "fair_exchange",
            ]
            weights = [1.20, 0.95, 0.90, 0.75, 0.80, 0.80, 0.58, 0.25, 0.10, 0.20]

        return self.weighted_choice(choices, weights)

    def choose_operation(self, agent):
        family = self.choose_operation_family(agent)
        spec = OPERATION_SPECS[family]
        intensity = self.rng.uniform(0.42, 1.38)
        target = self.rng.choice(list(self.agents.keys()))
        if target == agent.id:
            target = None

        declared_metric = self.rng.choice(METRICS)
        if agent.intent == "harmful" and self.rng.random() < 0.45:
            declared_metric = self.rng.choice(["material_output", "liquidity", "behavior_cooperation"])

        private_gain = spec["private_gain"] * intensity * (0.50 + agent.skill(family))

        return Operation(
            family=family,
            actor_id=agent.id,
            target_id=target,
            region=agent.region,
            intensity=intensity,
            declared_metric=declared_metric,
            private_gain=private_gain,
            flags=list(spec["red_flags"]),
            type_from=spec["from"],
            type_to=spec["to"],
            reversible=bool(spec["reversible"]),
        )

    # --------------------------
    # Execution and Minting
    # --------------------------

    def execute_operation(self, op):
        actor = self.agents[op.actor_id]
        region = self.world.regions[op.region]

        global_before = self.world.score()
        region_before = region.score()

        delta = op.realized_delta(actor, region, self.rng)
        validation = self.governance.validate(op, delta, region, actor, self.rng)

        minted = 0.0

        if validation.accepted:
            self.world.apply_delta(op.region, delta)
            region.local_ledger_size += 1

            global_after = self.world.score()
            region_after = region.score()

            if self.mode == "gmoe":
                minted = self.mint_omk(actor, op, delta, validation)
                actor.valid_contribution += weighted_score(delta)
                actor.reputation = clamp(actor.reputation + 0.20 * max(0.0, validation.score))
                actor.stake += 0.035 * minted

                if op.family == "produce_goods":
                    actor.goods += max(0.0, delta.get("material_output", 0.0)) * 1.35
                if op.family == "infrastructure_maintenance":
                    actor.energy += max(0.0, delta.get("resource_resilience", 0.0)) * 0.45
            else:
                actor.fiat_balance += max(0.0, op.private_gain)
                actor.capital += max(0.0, op.private_gain) * 0.20
                actor.reputation = clamp(actor.reputation + 0.035 * validation.score)

                if op.family in ("produce_goods", "exploit_labor"):
                    actor.goods += max(0.0, delta.get("material_output", 0.0)) * 1.2

                if weighted_score(delta) < 0:
                    actor.harmful_contribution += -weighted_score(delta)

        else:
            global_after = global_before
            region_after = region_before

            if self.mode == "gmoe":
                penalty = min(
                    actor.stake,
                    0.7 + 0.25 * len(op.flags) + max(0.0, -validation.score) * 0.07,
                )
                actor.stake -= penalty
                actor.reputation = clamp(actor.reputation - 0.75 * penalty)
                actor.redline_violations += 1 if op.flags else 0

                if "self_caused_harm" in op.flags:
                    actor.self_created_need_flag = True
            else:
                actor.fiat_balance -= 0.05

        self.ledger.append(
            LedgerEntry(
                step=self.world.step,
                mode=self.mode,
                region=op.region,
                actor_id=actor.id,
                actor_intent=actor.intent,
                operation=op.family,
                type_from=op.type_from,
                type_to=op.type_to,
                accepted=validation.accepted,
                reason=validation.reason,
                delta=delta,
                score_before=global_before,
                score_after=global_after,
                region_score_before=region_before,
                region_score_after=region_after,
                minted=minted,
                private_gain=op.private_gain,
                proof_quality=validation.proof_quality,
                causal_share=validation.causal_share,
                flags=op.flags,
            )
        )

        if validation.accepted or self.mode == "baseline":
            self.maybe_spawn_truth_claim(actor, op)
            self.maybe_spawn_causal_claim(actor, op, delta)
            self.maybe_spawn_behavior_or_norm_contract(actor, op)

    def mint_omk(self, actor, op, delta, validation):
        base_amount = positive_amount(delta)
        if base_amount <= 1e-9:
            return 0.0

        amount = base_amount * validation.proof_quality * validation.causal_share

        distributions = [
            (actor.id, 0.72),
            ("__repair_fund__", 0.11),
            ("__governance_fund__", 0.07),
        ]

        if op.target_id in self.agents:
            distributions.append((op.target_id, 0.10))
        else:
            distributions.append((actor.id, 0.10))

        for owner, share in distributions:
            credit = OMK(
                id=self.next_id(),
                issuer="GMOE-MINT",
                owner=owner,
                operation_family=op.family,
                type_from=op.type_from,
                type_to=op.type_to,
                delta=copy.deepcopy(delta),
                amount=amount * share,
                proof_quality=validation.proof_quality,
                causal_share=validation.causal_share,
                region=op.region,
                step=self.world.step,
                source="realized",
                reversible=op.reversible,
            )

            if owner == "__repair_fund__":
                self.repair_fund.deposit(credit)
            elif owner == "__governance_fund__":
                self.governance_fund.deposit(credit)
            else:
                self.agents[owner].wallet.deposit(credit)

        return amount

    # --------------------------
    # Specialized Instruments
    # --------------------------

    def maybe_spawn_truth_claim(self, actor, op):
        if op.family not in ("truth_audit", "fake_truth_certificate"):
            return
        if self.rng.random() > 0.35:
            return

        cid = "TC_%d_%s_%d" % (self.world.step, actor.id, len(self.truth_claims) + 1)
        fraud = op.family == "fake_truth_certificate"

        self.truth_claims[cid] = TruthClaim(
            id=cid,
            issuer=actor.id,
            region=op.region,
            created_step=self.world.step,
            due_step=self.world.step + self.rng.randint(3, 8),
            stake=min(actor.stake, self.rng.uniform(1.0, 4.5)),
            predicted_true=True if not fraud else self.rng.random() < 0.80,
            fraud=fraud,
        )

        self.market_events.append(
            MarketEvent(self.world.step, self.mode, "truth_market", op.region, actor.id, "market", 0.0, cid, "created")
        )

    def maybe_spawn_causal_claim(self, actor, op, delta):
        if op.family != "causal_intervention":
            return
        if self.rng.random() > 0.40:
            return

        cid = "CC_%d_%s_%d" % (self.world.step, actor.id, len(self.causal_claims) + 1)

        self.causal_claims[cid] = CausalClaim(
            id=cid,
            issuer=actor.id,
            region=op.region,
            created_step=self.world.step,
            due_step=self.world.step + self.rng.randint(4, 9),
            expected_score=max(0.0, weighted_score(delta)),
        )

        self.market_events.append(
            MarketEvent(self.world.step, self.mode, "causality_market", op.region, actor.id, "market", 0.0, cid, "created")
        )

    def maybe_spawn_behavior_or_norm_contract(self, actor, op):
        if op.family == "voluntary_behavior_contract" and self.rng.random() < 0.30:
            sponsor = actor.id
            participant = op.target_id if op.target_id in self.agents else actor.id
            cid = "BC_%d_%s_%d" % (self.world.step, participant, len(self.behavior_contracts) + 1)

            self.behavior_contracts[cid] = BehaviorContract(
                id=cid,
                participant=participant,
                sponsor=sponsor,
                region=op.region,
                due_step=self.world.step + self.rng.randint(3, 7),
                voluntary=True,
                stake=1.0 + self.rng.random() * 2.0,
            )

            self.market_events.append(
                MarketEvent(self.world.step, self.mode, "behavior_market", op.region, sponsor, participant, 0.0, cid, "created")
            )

        elif op.family == "norm_reform" and self.rng.random() < 0.28:
            cid = "NC_%d_%s_%d" % (self.world.step, actor.id, len(self.norm_contracts) + 1)
            region = self.world.regions[op.region]
            start_distance = TARGET["norm_alignment"] - region.metrics["norm_alignment"]

            self.norm_contracts[cid] = NormContract(
                id=cid,
                sponsor=actor.id,
                region=op.region,
                start_distance=start_distance,
                due_step=self.world.step + self.rng.randint(4, 8),
            )

            self.market_events.append(
                MarketEvent(self.world.step, self.mode, "norm_market", op.region, actor.id, "region", 0.0, cid, "created")
            )

    def settle_truth_claims(self):
        for claim in list(self.truth_claims.values()):
            if claim.resolved or claim.due_step > self.world.step:
                continue

            issuer = self.agents[claim.issuer]

            if claim.fraud:
                actual_true = self.rng.random() < 0.18
            else:
                actual_true = self.rng.random() < (0.55 + 0.40 * issuer.skill("truth_audit"))

            claim.actual_true = actual_true
            claim.resolved = True

            if self.mode == "gmoe":
                if actual_true and not claim.fraud:
                    delta = empty_delta()
                    delta["truth"] = 1.2
                    delta["causal_integrity"] = 0.3
                    delta["fairness"] = 0.2

                    amount = positive_amount(delta) * (0.7 + 0.3 * issuer.skill("truth_audit"))

                    credit = OMK(
                        id=self.next_id(),
                        issuer="TRUTH-SETTLEMENT",
                        owner=issuer.id,
                        operation_family="truth_audit",
                        type_from="truth",
                        type_to="money",
                        delta=delta,
                        amount=amount,
                        proof_quality=0.95,
                        causal_share=0.80,
                        region=claim.region,
                        step=self.world.step,
                        source="truth_certificate",
                        reversible=True,
                    )

                    issuer.wallet.deposit(credit)
                    issuer.reputation = clamp(issuer.reputation + 1.5)
                    claim.payout = amount
                else:
                    penalty = min(issuer.stake, claim.stake * (2.0 if claim.fraud else 1.0))
                    issuer.stake -= penalty
                    issuer.reputation = clamp(issuer.reputation - 2.5 - penalty * 0.3)
                    claim.payout = -penalty
            else:
                if claim.predicted_true == actual_true:
                    payout = claim.stake * 1.7
                    issuer.fiat_balance += payout
                    claim.payout = payout
                else:
                    issuer.fiat_balance -= min(issuer.fiat_balance, claim.stake)
                    claim.payout = -claim.stake

            self.market_events.append(
                MarketEvent(self.world.step, self.mode, "truth_market", claim.region, claim.issuer, "settlement", claim.payout, claim.id, "resolved_true=%s" % actual_true)
            )

    def settle_causal_claims(self):
        for claim in list(self.causal_claims.values()):
            if claim.resolved or claim.due_step > self.world.step:
                continue

            issuer = self.agents[claim.issuer]
            causal_share = clamp(0.40 + 0.50 * issuer.skill("causal_intervention") + self.rng.uniform(-0.10, 0.10))
            realized = claim.expected_score * causal_share * self.rng.uniform(0.75, 1.25)

            claim.causal_share = causal_share
            claim.realized_score = realized
            claim.resolved = True

            if self.mode == "gmoe" and realized > 0.05:
                delta = empty_delta()
                delta["causal_integrity"] = min(1.5, realized / 3.5)
                delta["truth"] = min(0.7, realized / 7.0)
                delta["help_potential"] = min(0.9, realized / 5.5)

                amount = positive_amount(delta) * causal_share

                credit = OMK(
                    id=self.next_id(),
                    issuer="CAUSAL-SETTLEMENT",
                    owner=issuer.id,
                    operation_family="causal_intervention",
                    type_from="causality",
                    type_to="effect",
                    delta=delta,
                    amount=amount,
                    proof_quality=0.88,
                    causal_share=causal_share,
                    region=claim.region,
                    step=self.world.step,
                    source="causal_certificate",
                    reversible=False,
                )

                issuer.wallet.deposit(credit)
                issuer.reputation = clamp(issuer.reputation + 1.0)
                claim.payout = amount

            elif self.mode == "baseline":
                payout = max(0.0, realized) * 0.45
                issuer.fiat_balance += payout
                claim.payout = payout

            self.market_events.append(
                MarketEvent(self.world.step, self.mode, "causality_market", claim.region, claim.issuer, "settlement", claim.payout, claim.id, "resolved")
            )

    def settle_behavior_and_norm_contracts(self):
        for c in list(self.behavior_contracts.values()):
            if c.resolved or c.due_step > self.world.step:
                continue

            participant = self.agents[c.participant]
            sponsor = self.agents[c.sponsor]
            success_prob = 0.45 + 0.45 * participant.skill("voluntary_behavior_contract")
            success = c.voluntary and self.rng.random() < success_prob
            c.resolved = True

            if self.mode == "gmoe" and success:
                delta = empty_delta()
                delta["behavior_cooperation"] = 1.1
                delta["consent_quality"] = 0.8
                delta["agency"] = 0.25

                amount = positive_amount(delta) * 0.80

                credit = OMK(
                    id=self.next_id(),
                    issuer="BEHAVIOR-SETTLEMENT",
                    owner=participant.id,
                    operation_family="voluntary_behavior_contract",
                    type_from="behavior",
                    type_to="money",
                    delta=delta,
                    amount=amount,
                    proof_quality=0.85,
                    causal_share=0.75,
                    region=c.region,
                    step=self.world.step,
                    source="behavior_contract",
                    reversible=True,
                )

                participant.wallet.deposit(credit)
                participant.reputation = clamp(participant.reputation + 0.8)
                c.payout = amount

            elif self.mode == "baseline" and success:
                payout = 2.0
                sponsor.fiat_balance -= min(sponsor.fiat_balance, payout)
                participant.fiat_balance += payout
                c.payout = payout

            self.market_events.append(
                MarketEvent(self.world.step, self.mode, "behavior_market", c.region, c.sponsor, c.participant, c.payout, c.id, "resolved_success=%s" % success)
            )

        for c in list(self.norm_contracts.values()):
            if c.resolved or c.due_step > self.world.step:
                continue

            sponsor = self.agents[c.sponsor]
            region = self.world.regions[c.region]
            new_distance = TARGET["norm_alignment"] - region.metrics["norm_alignment"]
            improvement = max(0.0, c.start_distance - new_distance)
            c.resolved = True

            if self.mode == "gmoe" and improvement > 0.05:
                delta = empty_delta()
                delta["norm_alignment"] = min(1.6, improvement)
                delta["fairness"] = min(0.8, improvement / 2.0)

                amount = positive_amount(delta) * 0.85

                credit = OMK(
                    id=self.next_id(),
                    issuer="NORM-SETTLEMENT",
                    owner=sponsor.id,
                    operation_family="norm_reform",
                    type_from="norm",
                    type_to="behavior",
                    delta=delta,
                    amount=amount,
                    proof_quality=0.82,
                    causal_share=0.72,
                    region=c.region,
                    step=self.world.step,
                    source="norm_contract",
                    reversible=True,
                )

                sponsor.wallet.deposit(credit)
                c.payout = amount

            elif self.mode == "baseline":
                payout = improvement * 0.6
                sponsor.fiat_balance += payout
                c.payout = payout

            self.market_events.append(
                MarketEvent(self.world.step, self.mode, "norm_market", c.region, c.sponsor, "region", c.payout, c.id, "resolved")
            )

    # --------------------------
    # Markets
    # --------------------------

    def pay(self, payer, payee, amount, market, object_id, region):
        if amount <= 0:
            return True

        if self.mode == "gmoe":
            spent = payer.wallet.spend(amount, payee.id, self.next_id)
            if spent:
                payee.wallet.deposit_many(spent)
                self.market_events.append(
                    MarketEvent(self.world.step, self.mode, market, region, payer.id, payee.id, amount, object_id, "paid_omk")
                )
                return True

            self.market_events.append(
                MarketEvent(self.world.step, self.mode, market, region, payer.id, payee.id, amount, object_id, "insufficient_omk")
            )
            return False

        if payer.fiat_balance >= amount:
            payer.fiat_balance -= amount
            payee.fiat_balance += amount
            self.market_events.append(
                MarketEvent(self.world.step, self.mode, market, region, payer.id, payee.id, amount, object_id, "paid_fiat")
            )
            return True

        self.market_events.append(
            MarketEvent(self.world.step, self.mode, market, region, payer.id, payee.id, amount, object_id, "insufficient_fiat")
        )
        return False

    def run_goods_market(self):
        by_region = defaultdict(list)
        for a in self.agents.values():
            by_region[a.region].append(a)

        for rid, agents in by_region.items():
            buyers = [a for a in agents if a.goods < 8.0]
            sellers = [a for a in agents if a.goods > 17.0]

            self.rng.shuffle(buyers)

            for buyer in buyers[: max(1, len(buyers) // 2)]:
                if not sellers:
                    break

                seller = self.rng.choice(sellers)
                if seller.goods <= 12.0:
                    continue

                units = min(3.0, seller.goods - 12.0)
                price = units * (1.1 + 0.02 * (100.0 - self.world.regions[rid].metrics["resource_resilience"]))

                if self.pay(buyer, seller, price, "goods_market", "goods", rid):
                    seller.goods -= units
                    buyer.goods += units

                    if self.mode == "gmoe" and self.rng.random() < 0.25:
                        op = Operation(
                            family="fair_exchange",
                            actor_id=buyer.id,
                            target_id=seller.id,
                            region=rid,
                            intensity=0.45,
                            declared_metric="liquidity",
                            private_gain=0.5,
                            flags=[],
                            type_from="money",
                            type_to="money",
                            reversible=True,
                        )
                        self.execute_operation(op)

    def run_energy_market(self):
        buyers = [a for a in self.agents.values() if a.energy < 7.0]
        sellers = [a for a in self.agents.values() if a.energy > 18.0]

        self.rng.shuffle(buyers)

        for b in buyers[: max(1, len(buyers) // 3)]:
            candidates = [s for s in sellers if s.region == b.region and s.energy > 13.0]
            if not candidates:
                continue

            s = self.rng.choice(candidates)
            units = min(2.5, s.energy - 13.0)
            price = units * 0.9

            if self.pay(b, s, price, "energy_market", "energy", b.region):
                b.energy += units
                s.energy -= units

    def run_securities_market(self):
        if not self.securities:
            return

        firms = sorted(
            self.securities.values(),
            key=lambda sec: self.agents[sec.issuer].reputation + 0.25 * self.agents[sec.issuer].capital,
            reverse=True,
        )

        investors = list(self.agents.values())
        self.rng.shuffle(investors)

        for investor in investors[: max(2, len(investors) // 5)]:
            sec = self.rng.choice(firms[: min(5, len(firms))])
            issuer = self.agents[sec.issuer]

            if investor.id == issuer.id:
                continue

            shares = self.rng.uniform(0.15, 1.6)
            price = shares * sec.price * (0.75 + issuer.reputation / 125.0)

            if self.pay(investor, issuer, price, "securities_market", sec.id, investor.region):
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
                pool = min(issuer.wallet.balance() * 0.012, 3.0)
                if pool <= 0.01:
                    continue

                for holder, sh in holders:
                    amount = pool * sh / total
                    spent = issuer.wallet.spend(amount, holder.id, self.next_id)
                    if spent:
                        holder.wallet.deposit_many(spent)
                        self.market_events.append(
                            MarketEvent(self.world.step, self.mode, "dividend", issuer.region, issuer.id, holder.id, amount, sec.id, "omk_dividend")
                        )
            else:
                pool = min(issuer.fiat_balance * 0.012, 3.0)
                if pool <= 0.01:
                    continue

                issuer.fiat_balance -= pool

                for holder, sh in holders:
                    amount = pool * sh / total
                    holder.fiat_balance += amount
                    self.market_events.append(
                        MarketEvent(self.world.step, self.mode, "dividend", issuer.region, issuer.id, holder.id, amount, sec.id, "fiat_dividend")
                    )

    def run_credit_market(self):
        if self.mode == "gmoe":
            borrowers = [a for a in self.agents.values() if a.wallet.balance() < 4.5 and a.intent != "harmful"]
            lenders = sorted(
                [a for a in self.agents.values() if a.wallet.balance() > 16.0],
                key=lambda a: a.wallet.balance(),
                reverse=True,
            )

            for b in borrowers[:4]:
                if not lenders:
                    break

                lender = lenders[0]
                if lender.id == b.id:
                    continue

                amount = min(3.5, lender.wallet.balance() * 0.07)
                if amount <= 0.25:
                    continue

                spent = lender.wallet.spend(amount, b.id, self.next_id)
                if spent:
                    b.wallet.deposit_many(spent)
                    family = max(GOOD_OPERATIONS, key=lambda f: b.skill(f))

                    c = CreditContract(
                        id="CR_%d_%s" % (self.world.step, b.id),
                        borrower=b.id,
                        lender=lender.id,
                        promised_family=family,
                        promised_amount=amount * 1.10,
                        stake=min(b.stake, amount),
                        due_step=self.world.step + 5,
                    )

                    self.credit_contracts.append(c)
                    self.market_events.append(
                        MarketEvent(self.world.step, self.mode, "credit_market", b.region, lender.id, b.id, amount, c.id, "omk_credit")
                    )
        else:
            borrowers = [a for a in self.agents.values() if a.fiat_balance < 35.0]
            lenders = sorted(
                [a for a in self.agents.values() if a.fiat_balance > 155.0],
                key=lambda a: a.fiat_balance,
                reverse=True,
            )

            for b in borrowers[:4]:
                if not lenders:
                    break

                lender = lenders[0]
                amount = min(12.0, lender.fiat_balance * 0.05)

                lender.fiat_balance -= amount
                b.fiat_balance += amount

                c = CreditContract(
                    id="FIAT_CR_%d_%s" % (self.world.step, b.id),
                    borrower=b.id,
                    lender=lender.id,
                    promised_family="fiat",
                    promised_amount=amount * 1.16,
                    stake=min(b.stake, amount * 0.5),
                    due_step=self.world.step + 5,
                )

                self.credit_contracts.append(c)
                self.market_events.append(
                    MarketEvent(self.world.step, self.mode, "credit_market", b.region, lender.id, b.id, amount, c.id, "fiat_credit")
                )

    def settle_credit_contracts(self):
        for c in self.credit_contracts:
            if c.fulfilled or c.due_step > self.world.step:
                continue

            borrower = self.agents[c.borrower]
            lender = self.agents[c.lender]

            if self.mode == "gmoe":
                spent = borrower.wallet.spend(c.promised_amount, lender.id, self.next_id)
                if spent:
                    lender.wallet.deposit_many(spent)
                    borrower.reputation = clamp(borrower.reputation + 0.9)
                    result = "fulfilled_omk"
                else:
                    loss = min(borrower.stake, c.stake)
                    borrower.stake -= loss
                    borrower.reputation = clamp(borrower.reputation - 2.5 - loss * 0.2)
                    result = "default_slash"

                c.fulfilled = True
                self.market_events.append(
                    MarketEvent(self.world.step, self.mode, "credit_settlement", borrower.region, borrower.id, lender.id, c.promised_amount, c.id, result)
                )
            else:
                if borrower.fiat_balance >= c.promised_amount:
                    borrower.fiat_balance -= c.promised_amount
                    lender.fiat_balance += c.promised_amount
                    result = "fulfilled_fiat"
                else:
                    loss = min(borrower.stake, c.stake)
                    borrower.stake -= loss
                    borrower.reputation = clamp(borrower.reputation - 2.0)
                    result = "default"

                c.fulfilled = True
                self.market_events.append(
                    MarketEvent(self.world.step, self.mode, "credit_settlement", borrower.region, borrower.id, lender.id, c.promised_amount, c.id, result)
                )

    def run_insurance_market(self):
        if self.mode == "gmoe":
            richest = sorted(self.agents.values(), key=lambda a: a.wallet.balance(), reverse=True)
        else:
            richest = sorted(self.agents.values(), key=lambda a: a.fiat_balance, reverse=True)

        if not richest:
            return

        insurer = richest[0]
        candidates = [
            a for a in self.agents.values()
            if a.id != insurer.id and a.insurance <= 0.0 and a.intent != "harmful"
        ]

        self.rng.shuffle(candidates)

        for holder in candidates[:2]:
            premium = 1.0 + self.rng.random() * 0.8
            coverage = 4.0 + self.rng.random() * 3.0

            if self.pay(holder, insurer, premium, "insurance_market", "insurance", holder.region):
                holder.insurance += coverage
                c = InsuranceContract(
                    id="IN_%d_%s" % (self.world.step, holder.id),
                    holder=holder.id,
                    insurer=insurer.id,
                    premium=premium,
                    coverage=coverage,
                    metric="freedom_from_harm",
                    region=holder.region,
                    active_until=self.world.step + 12,
                )
                self.insurance_contracts.append(c)

    def settle_insurance_after_shock(self, region_id, shock_size):
        for c in self.insurance_contracts:
            if not c.active or c.region != region_id or c.active_until < self.world.step:
                continue

            holder = self.agents[c.holder]
            insurer = self.agents[c.insurer]
            payout = min(c.coverage, max(0.0, shock_size * 1.2))

            if payout <= 0:
                continue

            if self.mode == "gmoe":
                spent = insurer.wallet.spend(payout, holder.id, self.next_id)
                if spent:
                    holder.wallet.deposit_many(spent)
                    c.paid_out += payout
                    self.market_events.append(
                        MarketEvent(self.world.step, self.mode, "insurance_payout", region_id, insurer.id, holder.id, payout, c.id, "paid")
                    )
            else:
                if insurer.fiat_balance >= payout:
                    insurer.fiat_balance -= payout
                    holder.fiat_balance += payout
                    c.paid_out += payout
                    self.market_events.append(
                        MarketEvent(self.world.step, self.mode, "insurance_payout", region_id, insurer.id, holder.id, payout, c.id, "paid")
                    )

            c.active = False
            holder.insurance = max(0.0, holder.insurance - payout)

    def run_interregional_bridge(self):
        if self.mode != "gmoe" or len(self.world.regions) < 2:
            return

        candidates = [a for a in self.agents.values() if a.wallet.balance() > 8.0]
        if not candidates:
            return

        for a in self.rng.sample(candidates, min(3, len(candidates))):
            target_region = self.rng.choice([r for r in self.world.regions.keys() if r != a.region])
            amount = min(2.0, a.wallet.balance() * 0.08)
            if amount <= 0.2:
                continue

            credits = a.wallet.spend(amount, a.id, self.next_id)
            if not credits:
                continue

            source = self.world.regions[a.region]
            target = self.world.regions[target_region]
            source.exported_omk += amount

            arrival = self.world.step + max(1, source.latency + target.latency + self.rng.randint(-1, 2))
            pid = "PKT_%d_%s_%s_%d" % (self.world.step, a.region, target_region, len(self.pending_packets) + 1)

            self.pending_packets.append(
                PendingPacket(
                    id=pid,
                    source_region=a.region,
                    target_region=target_region,
                    owner=a.id,
                    credits=credits,
                    created_step=self.world.step,
                    arrival_step=arrival,
                )
            )

            self.market_events.append(
                MarketEvent(self.world.step, self.mode, "interregional_bridge", a.region, a.id, target_region, amount, pid, "sent")
            )

    def settle_interregional_packets(self):
        if self.mode != "gmoe":
            return

        for p in self.pending_packets:
            if p.accepted is not None or p.arrival_step > self.world.step:
                continue

            source = self.world.regions[p.source_region]
            target = self.world.regions[p.target_region]
            trust = target.trust.get(source.id, 0.5)
            proof_quality = safe_mean([c.proof_quality for c in p.credits])
            threshold = 0.50 + 0.15 * (1.0 - trust)

            accepted = trust * proof_quality >= threshold
            p.accepted = accepted

            if accepted:
                self.agents[p.owner].wallet.deposit_many(p.credits)
                target.imported_omk += sum(c.amount for c in p.credits)

                actor = self.agents[p.owner]
                op = Operation(
                    family="interregional_bridge",
                    actor_id=actor.id,
                    target_id=None,
                    region=p.target_region,
                    intensity=0.35,
                    declared_metric="liquidity",
                    private_gain=0.5,
                    flags=[],
                    type_from="ledger",
                    type_to="ledger",
                    reversible=False,
                )
                self.execute_operation(op)
                p.reason = "accepted"
            else:
                target.invalidated_imports += 1
                self.agents[p.owner].wallet.deposit_many(p.credits)
                self.agents[p.owner].reputation = clamp(self.agents[p.owner].reputation - 0.5)
                p.reason = "rejected_low_trust_or_proof"

            self.market_events.append(
                MarketEvent(
                    self.world.step,
                    self.mode,
                    "interregional_settlement",
                    p.target_region,
                    p.owner,
                    p.target_region,
                    sum(c.amount for c in p.credits),
                    p.id,
                    p.reason,
                )
            )

    # --------------------------
    # Shocks and Public Repair
    # --------------------------

    def maybe_external_shock(self):
        if self.rng.random() > self.shock_rate:
            return

        rid = self.rng.choice(list(self.world.regions.keys()))
        region = self.world.regions[rid]

        delta = empty_delta()
        shock_size = self.rng.uniform(1.0, 3.4)

        delta["freedom_from_harm"] = -shock_size
        delta["resource_resilience"] = -self.rng.uniform(0.4, 1.8)
        delta["repair_capacity"] = -self.rng.uniform(0.2, 1.1)
        delta["reversibility"] = -self.rng.uniform(0.1, 0.8)

        before = self.world.score()
        rb = region.score()

        self.world.apply_delta(rid, delta)

        after = self.world.score()
        ra = region.score()

        self.ledger.append(
            LedgerEntry(
                step=self.world.step,
                mode=self.mode,
                region=rid,
                actor_id="EXTERNAL",
                actor_intent="none",
                operation="external_shock",
                type_from="environment",
                type_to="damage",
                accepted=True,
                reason="exogenous shock",
                delta=delta,
                score_before=before,
                score_after=after,
                region_score_before=rb,
                region_score_after=ra,
                minted=0.0,
                private_gain=0.0,
                proof_quality=1.0,
                causal_share=1.0,
                flags=["external"],
            )
        )

        self.market_events.append(
            MarketEvent(self.world.step, self.mode, "shock", rid, "EXTERNAL", "region", shock_size, "shock", "occurred")
        )

        self.settle_insurance_after_shock(rid, shock_size)

    def repair_fund_action(self):
        if self.mode != "gmoe":
            return
        if self.repair_fund.balance() < 1.5:
            return

        regions = sorted(
            self.world.regions.values(),
            key=lambda r: r.metrics["freedom_from_harm"] + r.metrics["agency"] + r.metrics["fairness"],
        )
        region = regions[0]

        candidates = [a for a in self.agents.values() if a.region == region.id]
        if not candidates:
            return

        actor = max(candidates, key=lambda a: a.skill("repair_harm") + a.skill("restore_agency"))

        grant = min(2.5, self.repair_fund.balance() * 0.10)
        spent = self.repair_fund.spend(grant, actor.id, self.next_id)

        if spent:
            actor.wallet.deposit_many(spent)
            opfam = "repair_harm" if region.metrics["freedom_from_harm"] < region.metrics["agency"] else "restore_agency"
            spec = OPERATION_SPECS[opfam]

            op = Operation(
                family=opfam,
                actor_id=actor.id,
                target_id=None,
                region=region.id,
                intensity=0.75,
                declared_metric="freedom_from_harm",
                private_gain=1.0,
                flags=[],
                type_from=spec["from"],
                type_to=spec["to"],
                reversible=spec["reversible"],
            )

            self.execute_operation(op)

            self.market_events.append(
                MarketEvent(self.world.step, self.mode, "repair_fund", region.id, "repair_fund", actor.id, grant, opfam, "funded")
            )

    # --------------------------
    # Step Loop
    # --------------------------

    def step_once(self):
        self.world.step += 1

        score_start = self.world.score()
        dist_start = self.world.distance()

        self.maybe_external_shock()

        agents = list(self.agents.values())
        self.rng.shuffle(agents)
        active_count = max(1, int(len(agents) * 0.58))

        for a in agents[:active_count]:
            op = self.choose_operation(a)
            self.execute_operation(op)

        self.settle_truth_claims()
        self.settle_causal_claims()
        self.settle_behavior_and_norm_contracts()

        self.run_goods_market()
        self.run_energy_market()
        self.run_securities_market()
        self.distribute_dividends()
        self.run_credit_market()
        self.settle_credit_contracts()
        self.run_insurance_market()
        self.run_interregional_bridge()
        self.settle_interregional_packets()
        self.repair_fund_action()

        score_end = self.world.score()
        dist_end = self.world.distance()

        self.history.append(
            {
                "step": self.world.step,
                "mode": self.mode,
                "score_start": score_start,
                "score_end": score_end,
                "score_change": score_end - score_start,
                "distance_start": dist_start,
                "distance_end": dist_end,
                "distance_change": dist_end - dist_start,
                "total_omk": self.total_omk_balance(),
                "total_fiat": sum(a.fiat_balance for a in self.agents.values()),
                "accepted": sum(1 for e in self.ledger if e.step == self.world.step and e.accepted and e.actor_id != "EXTERNAL"),
                "rejected": sum(1 for e in self.ledger if e.step == self.world.step and not e.accepted),
                "harmful_accepted": sum(1 for e in self.ledger if e.step == self.world.step and e.accepted and e.operation in HARMFUL_OPERATIONS),
            }
        )

        metrics_row = {"step": self.world.step, "mode": self.mode}
        gm = self.world.global_metrics()
        for m in METRICS:
            metrics_row[m] = gm[m]
        self.metric_history.append(metrics_row)

    def run(self, steps):
        for _ in range(steps):
            self.step_once()

    # --------------------------
    # Diagnostics
    # --------------------------

    def total_omk_balance(self):
        return (
            sum(a.wallet.balance() for a in self.agents.values())
            + self.repair_fund.balance()
            + self.governance_fund.balance()
        )

    def accepted_entries(self):
        return [e for e in self.ledger if e.accepted and e.actor_id != "EXTERNAL"]

    def rejected_entries(self):
        return [e for e in self.ledger if not e.accepted]

    def harmful_accepted_count(self):
        return sum(1 for e in self.accepted_entries() if e.operation in HARMFUL_OPERATIONS)

    def positive_cone_violations_among_accepted(self):
        count = 0

        for e in self.accepted_entries():
            if e.operation in HARMFUL_OPERATIONS:
                count += 1
                continue
            if weighted_score(e.delta) <= POSITIVE_SCORE_THRESHOLD:
                count += 1
                continue
            for m in PROTECTED:
                if e.delta.get(m, 0.0) < PROTECTED_LOSS_TOLERANCE:
                    count += 1
                    break

        return count

    def cumulative_accepted_score(self):
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

    def top_agents_by_money(self, n=8):
        return sorted(self.agents.values(), key=lambda a: a.money(self.mode), reverse=True)[:n]

    def operation_summary_rows(self):
        stats = {}

        for e in self.ledger:
            key = e.operation

            if key not in stats:
                stats[key] = {
                    "operation": key,
                    "accepted": 0,
                    "rejected": 0,
                    "minted": 0.0,
                    "weighted_score": 0.0,
                    "private_gain": 0.0,
                    "protected_loss": 0.0,
                    "harmful_family": int(key in HARMFUL_OPERATIONS),
                }

            row = stats[key]
            if e.accepted:
                row["accepted"] += 1
            else:
                row["rejected"] += 1

            row["minted"] += e.minted
            row["weighted_score"] += weighted_score(e.delta)
            row["private_gain"] += e.private_gain
            row["protected_loss"] += protected_loss(e.delta)

        return list(stats.values())

    def market_summary_rows(self):
        stats = {}

        for e in self.market_events:
            key = e.market

            if key not in stats:
                stats[key] = {
                    "market": key,
                    "events": 0,
                    "amount": 0.0,
                    "success_events": 0,
                    "failed_events": 0,
                }

            stats[key]["events"] += 1
            stats[key]["amount"] += e.amount

            if any(word in e.result for word in ("paid", "fulfilled", "created", "resolved", "sent", "accepted", "funded", "dividend")):
                stats[key]["success_events"] += 1
            if any(word in e.result for word in ("insufficient", "default", "rejected")):
                stats[key]["failed_events"] += 1

        return list(stats.values())

    def intent_summary_rows(self):
        rows = []

        for intent in sorted(set(a.intent for a in self.agents.values())):
            group = [a for a in self.agents.values() if a.intent == intent]

            rows.append(
                {
                    "intent": intent,
                    "count": len(group),
                    "avg_money": safe_mean([a.money(self.mode) for a in group]),
                    "avg_reputation": safe_mean([a.reputation for a in group]),
                    "avg_stake": safe_mean([a.stake for a in group]),
                    "avg_valid_contribution": safe_mean([a.valid_contribution for a in group]),
                    "avg_harmful_contribution": safe_mean([a.harmful_contribution for a in group]),
                    "redline_violations": sum(a.redline_violations for a in group),
                }
            )

        return rows

    def diagnostic_rows(self):
        accepted = self.accepted_entries()
        rejected = self.rejected_entries()
        ok, total = self.monotonic_score_steps()

        money_by_agent = [a.money(self.mode) for a in self.agents.values()]
        rep_by_agent = [a.reputation for a in self.agents.values()]
        valid_by_agent = [a.valid_contribution for a in self.agents.values()]

        return [
            {"diagnostic": "accepted_transactions", "value": len(accepted)},
            {"diagnostic": "rejected_transactions", "value": len(rejected)},
            {"diagnostic": "harmful_accepted", "value": self.harmful_accepted_count()},
            {"diagnostic": "positive_cone_violations_among_accepted", "value": self.positive_cone_violations_among_accepted()},
            {"diagnostic": "cumulative_accepted_weighted_score", "value": self.cumulative_accepted_score()},
            {"diagnostic": "score_nondecreasing_transitions", "value": ok},
            {"diagnostic": "score_transition_total", "value": total},
            {"diagnostic": "final_nobility_index", "value": self.world.score()},
            {"diagnostic": "final_distance_to_target", "value": self.world.distance()},
            {"diagnostic": "total_omk", "value": self.total_omk_balance()},
            {"diagnostic": "total_fiat", "value": sum(a.fiat_balance for a in self.agents.values())},
            {"diagnostic": "money_gini", "value": gini(money_by_agent)},
            {"diagnostic": "corr_money_reputation", "value": pearson(money_by_agent, rep_by_agent)},
            {"diagnostic": "corr_money_valid_contribution", "value": pearson(money_by_agent, valid_by_agent)},
            {"diagnostic": "pending_packets", "value": sum(1 for p in self.pending_packets if p.accepted is None)},
            {"diagnostic": "accepted_packets", "value": sum(1 for p in self.pending_packets if p.accepted is True)},
            {"diagnostic": "rejected_packets", "value": sum(1 for p in self.pending_packets if p.accepted is False)},
        ]

    # --------------------------
    # Rows for CSV Export
    # --------------------------

    def agents_rows(self):
        rows = []
        for a in self.agents.values():
            rows.append(
                {
                    "id": a.id,
                    "name": a.name,
                    "intent": a.intent,
                    "role": a.role,
                    "region": a.region,
                    "money": a.money(self.mode),
                    "omk_balance": a.wallet.balance(),
                    "fiat_balance": a.fiat_balance,
                    "reputation": a.reputation,
                    "stake": a.stake,
                    "rank": a.rank,
                    "capital": a.capital,
                    "goods": a.goods,
                    "energy": a.energy,
                    "insurance": a.insurance,
                    "self_created_need_flag": int(a.self_created_need_flag),
                    "redline_violations": a.redline_violations,
                    "valid_contribution": a.valid_contribution,
                    "harmful_contribution": a.harmful_contribution,
                    "wallet_units": len(a.wallet.credits),
                }
            )
        return rows

    def region_rows(self):
        rows = []
        for r in self.world.regions.values():
            row = {
                "id": r.id,
                "name": r.name,
                "score": r.score(),
                "distance": r.distance(),
                "latency": r.latency,
                "local_ledger_size": r.local_ledger_size,
                "imported_omk": r.imported_omk,
                "exported_omk": r.exported_omk,
                "invalidated_imports": r.invalidated_imports,
            }
            for m in METRICS:
                row[m] = r.metrics[m]
            rows.append(row)
        return rows

    def ledger_rows(self):
        rows = []
        for e in self.ledger:
            row = {
                "step": e.step,
                "mode": e.mode,
                "region": e.region,
                "actor_id": e.actor_id,
                "actor_intent": e.actor_intent,
                "operation": e.operation,
                "type_from": e.type_from,
                "type_to": e.type_to,
                "accepted": int(e.accepted),
                "reason": e.reason,
                "score_before": e.score_before,
                "score_after": e.score_after,
                "region_score_before": e.region_score_before,
                "region_score_after": e.region_score_after,
                "weighted_delta_score": weighted_score(e.delta),
                "protected_loss": protected_loss(e.delta),
                "minted": e.minted,
                "private_gain": e.private_gain,
                "proof_quality": e.proof_quality,
                "causal_share": e.causal_share,
                "flags": ";".join(e.flags),
            }
            for m in METRICS:
                row["delta_" + m] = e.delta.get(m, 0.0)
            rows.append(row)
        return rows

    def market_event_rows(self):
        return [e.__dict__.copy() for e in self.market_events]

    def security_rows(self):
        return [s.__dict__.copy() for s in self.securities.values()]

    def truth_claim_rows(self):
        return [c.__dict__.copy() for c in self.truth_claims.values()]

    def causal_claim_rows(self):
        return [c.__dict__.copy() for c in self.causal_claims.values()]

    def behavior_contract_rows(self):
        return [c.__dict__.copy() for c in self.behavior_contracts.values()]

    def norm_contract_rows(self):
        return [c.__dict__.copy() for c in self.norm_contracts.values()]

    def credit_contract_rows(self):
        return [c.__dict__.copy() for c in self.credit_contracts]

    def insurance_contract_rows(self):
        return [c.__dict__.copy() for c in self.insurance_contracts]

    def packet_rows(self):
        rows = []
        for p in self.pending_packets:
            rows.append(
                {
                    "id": p.id,
                    "source_region": p.source_region,
                    "target_region": p.target_region,
                    "owner": p.owner,
                    "created_step": p.created_step,
                    "arrival_step": p.arrival_step,
                    "accepted": p.accepted,
                    "reason": p.reason,
                    "amount": sum(c.amount for c in p.credits),
                    "avg_proof_quality": safe_mean([c.proof_quality for c in p.credits]),
                }
            )
        return rows

    def omk_wallet_rows(self, limit_per_agent=15):
        rows = []

        if self.mode != "gmoe":
            return rows

        for a in self.agents.values():
            top = sorted(a.wallet.credits, key=lambda c: c.amount, reverse=True)[:limit_per_agent]

            for c in top:
                row = {
                    "agent_id": a.id,
                    "agent_name": a.name,
                    "agent_intent": a.intent,
                    "agent_region": a.region,
                    "omk_id": c.id,
                    "amount": c.amount,
                    "issuer": c.issuer,
                    "operation_family": c.operation_family,
                    "type_from": c.type_from,
                    "type_to": c.type_to,
                    "proof_quality": c.proof_quality,
                    "causal_share": c.causal_share,
                    "source": c.source,
                    "region": c.region,
                    "step": c.step,
                    "reversible": int(c.reversible),
                }

                for m in METRICS:
                    row["delta_" + m] = c.delta.get(m, 0.0)

                rows.append(row)

        return rows

    def hierarchy_rows(self):
        rows = []
        for a in self.agents.values():
            rows.append(
                {
                    "agent_id": a.id,
                    "name": a.name,
                    "intent": a.intent,
                    "region": a.region,
                    "rank": self.world.hierarchy.get(a.id, a.rank),
                    "reputation": a.reputation,
                    "money": a.money(self.mode),
                }
            )
        return rows

    # --------------------------
    # Export
    # --------------------------

    def export_csv(self, outdir):
        ensure_dir(outdir)

        write_csv(os.path.join(outdir, "%s_history.csv" % self.mode), self.history)
        write_csv(os.path.join(outdir, "%s_metric_history.csv" % self.mode), self.metric_history)
        write_csv(os.path.join(outdir, "%s_agents_final.csv" % self.mode), self.agents_rows())
        write_csv(os.path.join(outdir, "%s_regions_final.csv" % self.mode), self.region_rows())
        write_csv(os.path.join(outdir, "%s_ledger.csv" % self.mode), self.ledger_rows())
        write_csv(os.path.join(outdir, "%s_market_events.csv" % self.mode), self.market_event_rows())
        write_csv(os.path.join(outdir, "%s_operation_summary.csv" % self.mode), self.operation_summary_rows())
        write_csv(os.path.join(outdir, "%s_market_summary.csv" % self.mode), self.market_summary_rows())
        write_csv(os.path.join(outdir, "%s_intent_summary.csv" % self.mode), self.intent_summary_rows())
        write_csv(os.path.join(outdir, "%s_diagnostics.csv" % self.mode), self.diagnostic_rows())
        write_csv(os.path.join(outdir, "%s_securities.csv" % self.mode), self.security_rows())
        write_csv(os.path.join(outdir, "%s_truth_claims.csv" % self.mode), self.truth_claim_rows())
        write_csv(os.path.join(outdir, "%s_causal_claims.csv" % self.mode), self.causal_claim_rows())
        write_csv(os.path.join(outdir, "%s_behavior_contracts.csv" % self.mode), self.behavior_contract_rows())
        write_csv(os.path.join(outdir, "%s_norm_contracts.csv" % self.mode), self.norm_contract_rows())
        write_csv(os.path.join(outdir, "%s_credit_contracts.csv" % self.mode), self.credit_contract_rows())
        write_csv(os.path.join(outdir, "%s_insurance_contracts.csv" % self.mode), self.insurance_contract_rows())
        write_csv(os.path.join(outdir, "%s_interregional_packets.csv" % self.mode), self.packet_rows())
        write_csv(os.path.join(outdir, "%s_omk_wallets.csv" % self.mode), self.omk_wallet_rows(limit_per_agent=15))
        write_csv(os.path.join(outdir, "%s_hierarchy.csv" % self.mode), self.hierarchy_rows())

        with open(os.path.join(outdir, "%s_report.md" % self.mode), "w", encoding="utf-8") as f:
            f.write(self.markdown_report())

    # --------------------------
    # Reports
    # --------------------------

    def markdown_report(self):
        initial = self.history[0]["score_start"] if self.history else self.world.score()
        final = self.world.score()
        ok, total = self.monotonic_score_steps()

        lines = []
        lines.append("# GMOE Simulation Report")
        lines.append("")
        lines.append("Mode: `%s`" % self.mode)
        lines.append("")
        lines.append("| Quantity | Value |")
        lines.append("|---|---:|")
        lines.append("| Initial nobility index | %.4f |" % initial)
        lines.append("| Final nobility index | %.4f |" % final)
        lines.append("| Change | %+0.4f |" % (final - initial))
        lines.append("| Final distance to target | %.4f |" % self.world.distance())
        lines.append("| Accepted transactions | %d |" % len(self.accepted_entries()))
        lines.append("| Rejected transactions | %d |" % len(self.rejected_entries()))
        lines.append("| Accepted harmful operations | %d |" % self.harmful_accepted_count())
        lines.append("| Positive-cone violations among accepted | %d |" % self.positive_cone_violations_among_accepted())
        lines.append("| Cumulative accepted weighted score | %+0.4f |" % self.cumulative_accepted_score())
        lines.append("| Score nondecreasing transitions | %d / %d |" % (ok, total))

        if self.mode == "gmoe":
            lines.append("| Total OMK stack balance | %.4f |" % self.total_omk_balance())
            lines.append("| Repair fund balance | %.4f |" % self.repair_fund.balance())
            lines.append("| Governance fund balance | %.4f |" % self.governance_fund.balance())
        else:
            lines.append("| Total fiat balance | %.4f |" % sum(a.fiat_balance for a in self.agents.values()))

        lines.append("")
        lines.append("## Interpretation")
        lines.append("")
        if self.mode == "gmoe":
            lines.append(
                "In GMOE mode, root money is minted only when a valid unary operation produces a valid positive metric movement. "
                "Therefore the automatic direction toward improvement is an invariant of the model."
            )
        else:
            lines.append(
                "In baseline mode, transactions clear by private scalar profit. "
                "This allows profitable harmful operations to clear."
            )

        lines.append("")
        lines.append("## Final Global Metrics")
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|---|---:|")

        gm = self.world.global_metrics()
        for m in METRICS:
            lines.append("| %s | %.4f |" % (m, gm[m]))

        return "\n".join(lines)

    def console_report(self):
        initial = self.history[0]["score_start"] if self.history else self.world.score()
        final = self.world.score()
        ok, total = self.monotonic_score_steps()

        lines = []
        lines.append("=" * 88)
        lines.append(
            "GMOE Enriched Simulation | mode=%s seed=%s steps=%s agents=%s regions=%s"
            % (self.mode, self.seed, self.world.step, len(self.agents), len(self.world.regions))
        )
        lines.append("-" * 88)
        lines.append("Initial nobility index:              %.4f" % initial)
        lines.append("Final nobility index:                %.4f" % final)
        lines.append("Change:                              %+0.4f" % (final - initial))
        lines.append("Final metric distance to target:     %.4f" % self.world.distance())
        lines.append("Accepted transactions:               %d" % len(self.accepted_entries()))
        lines.append("Rejected transactions:               %d" % len(self.rejected_entries()))
        lines.append("Accepted harmful operations:         %d" % self.harmful_accepted_count())
        lines.append("Positive-cone violations accepted:   %d" % self.positive_cone_violations_among_accepted())
        lines.append("Cumulative accepted weighted score:  %+0.4f" % self.cumulative_accepted_score())
        lines.append("Score nondecreasing transitions:     %d/%d" % (ok, total))

        if self.mode == "gmoe":
            lines.append("Total countable OMK stack balance:   %.4f" % self.total_omk_balance())
            lines.append("Repair fund / Governance fund:       %.4f / %.4f" % (self.repair_fund.balance(), self.governance_fund.balance()))
        else:
            lines.append("Total scalar fiat balance:           %.4f" % sum(a.fiat_balance for a in self.agents.values()))

        lines.append("-" * 88)
        lines.append("Final global metrics:")

        gm = self.world.global_metrics()
        for m in METRICS:
            lines.append("  %-26s %7.3f" % (m + ":", gm[m]))

        lines.append("-" * 88)
        lines.append("Top agents by money:")

        for a in self.top_agents_by_money(8):
            lines.append(
                "  %-24s intent=%-7s region=%s role=%-9s money=%8.3f rep=%6.2f stake=%6.2f"
                % (a.name[:24], a.intent, a.region, a.role, a.money(self.mode), a.reputation, a.stake)
            )

        if self.mode == "gmoe":
            lines.append("-" * 88)
            richest = self.top_agents_by_money(1)[0]
            lines.append("Example stacked OMK money in richest wallet: %s" % richest.name)
            lines.append(richest.wallet.top_summary(8))

        lines.append("-" * 88)
        lines.append("Diagnostics:")

        for d in self.diagnostic_rows():
            lines.append("  %-45s %s" % (d["diagnostic"] + ":", fmt(d["value"])))

        lines.append("=" * 88)

        return "\n".join(lines)


# ============================================================
# 6. File Helpers
# ============================================================

def ensure_dir(path):
    if path and not os.path.exists(path):
        os.makedirs(path)


def write_csv(path, rows):
    ensure_dir(os.path.dirname(path))

    if not rows:
        with open(path, "w", newline="", encoding="utf-8") as f:
            f.write("")
        return

    keys = []
    seen = set()

    for r in rows:
        for k in r.keys():
            if k not in seen:
                keys.append(k)
                seen.add(k)

    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


# ============================================================
# 7. Comparison and Monte Carlo
# ============================================================

def run_pair(args):
    gmoe = Economy("gmoe", args.agents, args.regions, args.seed, args.shock_rate)
    base = Economy("baseline", args.agents, args.regions, args.seed, args.shock_rate)

    gmoe.run(args.steps)
    base.run(args.steps)

    return gmoe, base


def comparison_report(gmoe, base):
    lines = []
    lines.append(gmoe.console_report())
    lines.append("")
    lines.append(base.console_report())
    lines.append("")
    lines.append("Comparison conclusion:")
    lines.append("  GMOE mode defines root money as valid unary operation + valid metric + certified positive distance change.")
    lines.append("  Baseline mode defines clearing by scalar private profit.")
    lines.append("  GMOE final nobility - baseline final nobility: %+0.4f" % (gmoe.world.score() - base.world.score()))
    lines.append("  GMOE accepted harmful ops: %d | Baseline accepted harmful ops: %d" % (gmoe.harmful_accepted_count(), base.harmful_accepted_count()))
    lines.append("  GMOE positive-cone violations among accepted: %d" % gmoe.positive_cone_violations_among_accepted())
    lines.append("  Interpretation: inside the model, automatic positive direction follows from the money-validity rule.")
    return "\n".join(lines)


def export_comparison(gmoe, base, outdir):
    ensure_dir(outdir)

    gmoe.export_csv(outdir)
    base.export_csv(outdir)

    rows = [
        {"quantity": "final_nobility_gmoe", "value": gmoe.world.score()},
        {"quantity": "final_nobility_baseline", "value": base.world.score()},
        {"quantity": "difference_gmoe_minus_baseline", "value": gmoe.world.score() - base.world.score()},
        {"quantity": "harmful_accepted_gmoe", "value": gmoe.harmful_accepted_count()},
        {"quantity": "harmful_accepted_baseline", "value": base.harmful_accepted_count()},
        {"quantity": "positive_cone_violations_gmoe", "value": gmoe.positive_cone_violations_among_accepted()},
        {"quantity": "positive_cone_violations_baseline", "value": base.positive_cone_violations_among_accepted()},
        {"quantity": "cumulative_accepted_score_gmoe", "value": gmoe.cumulative_accepted_score()},
        {"quantity": "cumulative_accepted_score_baseline", "value": base.cumulative_accepted_score()},
    ]

    write_csv(os.path.join(outdir, "comparison_summary.csv"), rows)

    with open(os.path.join(outdir, "comparison_report.md"), "w", encoding="utf-8") as f:
        f.write("# GMOE vs Baseline Comparison\n\n")
        f.write("| Quantity | Value |\n")
        f.write("|---|---:|\n")
        for r in rows:
            f.write("| %s | %s |\n" % (r["quantity"], fmt(r["value"])))
        f.write("\n\n## GMOE Report\n\n")
        f.write(gmoe.markdown_report())
        f.write("\n\n## Baseline Report\n\n")
        f.write(base.markdown_report())


def run_monte_carlo(args):
    ensure_dir(args.out)
    rows = []

    for i in range(args.monte_carlo):
        seed = args.seed + i

        class LocalArgs:
            pass

        local = LocalArgs()
        local.agents = args.agents
        local.regions = args.regions
        local.seed = seed
        local.shock_rate = args.shock_rate
        local.steps = args.steps

        gmoe, base = run_pair(local)

        rows.append(
            {
                "run": i,
                "seed": seed,
                "gmoe_final_nobility": gmoe.world.score(),
                "baseline_final_nobility": base.world.score(),
                "difference": gmoe.world.score() - base.world.score(),
                "gmoe_harmful_accepted": gmoe.harmful_accepted_count(),
                "baseline_harmful_accepted": base.harmful_accepted_count(),
                "gmoe_positive_cone_violations": gmoe.positive_cone_violations_among_accepted(),
                "baseline_positive_cone_violations": base.positive_cone_violations_among_accepted(),
                "gmoe_cumulative_score": gmoe.cumulative_accepted_score(),
                "baseline_cumulative_score": base.cumulative_accepted_score(),
            }
        )

    write_csv(os.path.join(args.out, "monte_carlo_summary.csv"), rows)

    diffs = [r["difference"] for r in rows]
    gmoe_pcv = [r["gmoe_positive_cone_violations"] for r in rows]
    base_harm = [r["baseline_harmful_accepted"] for r in rows]

    lines = []
    lines.append("=" * 88)
    lines.append("Monte Carlo summary | runs=%d steps=%d agents=%d regions=%d" % (args.monte_carlo, args.steps, args.agents, args.regions))
    lines.append("Mean final nobility difference GMOE-baseline: %+0.4f" % safe_mean(diffs))
    lines.append("Std final nobility difference: %.4f" % safe_stdev(diffs))
    lines.append("GMOE positive cone violation mean: %.4f" % safe_mean(gmoe_pcv))
    lines.append("Baseline accepted harmful ops mean: %.4f" % safe_mean(base_harm))
    lines.append("CSV exported: %s" % os.path.join(args.out, "monte_carlo_summary.csv"))
    lines.append("=" * 88)

    return "\n".join(lines)


# ============================================================
# 8. CLI
# ============================================================

def parse_args():
    parser = argparse.ArgumentParser(description="Enriched Galactic Metric Operator Economy simulation")
    parser.add_argument("--mode", choices=["gmoe", "baseline"], default="gmoe")
    parser.add_argument("--steps", type=int, default=180)
    parser.add_argument("--agents", type=int, default=60)
    parser.add_argument("--regions", type=int, default=5)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--shock-rate", type=float, default=0.012)
    parser.add_argument("--compare", action="store_true")
    parser.add_argument("--out", default="gmoe_enriched_output")
    parser.add_argument("--no-export", action="store_true")
    parser.add_argument("--monte-carlo", type=int, default=0)
    return parser.parse_args()


def main():
    args = parse_args()

    if args.monte_carlo and args.monte_carlo > 0:
        print(run_monte_carlo(args))
        return

    if args.compare:
        gmoe, base = run_pair(args)
        print(comparison_report(gmoe, base))

        if not args.no_export:
            export_comparison(gmoe, base, args.out)
            print("\nExported CSV/Markdown tables to: %s" % args.out)

    else:
        econ = Economy(args.mode, args.agents, args.regions, args.seed, args.shock_rate)
        econ.run(args.steps)
        print(econ.console_report())

        if not args.no_export:
            econ.export_csv(args.out)
            print("\nExported CSV/Markdown tables to: %s" % args.out)


if __name__ == "__main__":
    main()
