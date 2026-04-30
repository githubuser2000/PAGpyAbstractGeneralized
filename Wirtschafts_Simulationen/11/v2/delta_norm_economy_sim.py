#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Delta-Norm Economy Simulation / Delta-Norm-Wirtschaftssimulation
================================================================

Ein lauffähiges PyPy3-Programm für eine Wirtschaft, in der Geld als Differenz
zwischen zwei mathematischen Normen von Verhalten entsteht.

Mathematischer Kern:
    mu(e) = lambda_d * ( ||Phi_d(e)||_+ - ||Phi_d(e)||_- )

Jedes wirtschaftliche Ereignis ist ein Verhalten:
Arbeit, Essen, Konsum, Medienpublikation, Nachrichtenkonsum, Reparatur,
Orbitbetrieb, Mondlogistik, Kredit, Versicherung, Governance, Bildung usw.

Ausgaben:
    - report.md
    - daily_metrics.csv
    - events.csv
    - transactions.csv
    - actors.csv
    - final_state.json

Beispiele:
    pypy3 delta_norm_economy_sim.py --days 365 --persons 700 --scenario media_crisis --out run_media
    pypy3 delta_norm_economy_sim.py --days 180 --persons 400 --scenario orbit_emergency
    pypy3 delta_norm_economy_sim.py --self-test

Keine externen Bibliotheken.
"""

from __future__ import print_function

import argparse
import csv
import json
import math
import os
import random
import re
import time
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

VERSION = "1.2.0"
EPS = 1e-9


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------

def clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def div(a: float, b: float, default: float = 0.0) -> float:
    return default if abs(b) < EPS else a / b


def avg(xs: List[float], default: float = 0.0) -> float:
    return sum(xs) / len(xs) if xs else default


def gini(xs: List[float]) -> float:
    vals = sorted(max(0.0, x) for x in xs)
    n = len(vals)
    s = sum(vals)
    if n == 0 or s <= EPS:
        return 0.0
    return 2.0 * sum((i + 1) * v for i, v in enumerate(vals)) / (n * s) - (n + 1.0) / n


def weighted_choice(rng: random.Random, items: List[Tuple[Any, float]]) -> Any:
    total = sum(max(0.0, w) for _, w in items)
    if total <= 0:
        return items[rng.randrange(len(items))][0]
    r = rng.random() * total
    acc = 0.0
    for item, w in items:
        acc += max(0.0, w)
        if r <= acc:
            return item
    return items[-1][0]


def norm(features: Dict[str, float], weights: Dict[str, float], p: float = 2.0) -> float:
    if p == float("inf"):
        return max((abs(features.get(k, 0.0)) * w for k, w in weights.items()), default=0.0)
    s = 0.0
    for k, w in weights.items():
        v = abs(float(features.get(k, 0.0)))
        if w > 0 and v > 0:
            s += w * (v ** p)
    return s ** (1.0 / p) if s > 0 else 0.0


def mkdir(path: str) -> None:
    if path and not os.path.exists(path):
        os.makedirs(path)


def dumps(obj: Any) -> str:
    return json.dumps(obj, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def f2(x: float) -> str:
    return "%.2f" % float(x)


def f3(x: float) -> str:
    return "%.3f" % float(x)


ANSI_RESET = "\033[0m"
ANSI_BOLD = "\033[1m"
ANSI_DIM = "\033[2m"
ANSI_COLORS = [31, 33, 32, 36, 34, 35, 91, 92, 94, 95, 96]
UTF8_BLOCKS = "▁▂▃▄▅▆▇█"


def ansi(text: str, code: int, enable: bool = True) -> str:
    if not enable:
        return text
    return "\033[%sm%s%s" % (code, text, ANSI_RESET)


def ansi_bold(text: str, enable: bool = True) -> str:
    if not enable:
        return text
    return ANSI_BOLD + text + ANSI_RESET


def rainbow(text: str, enable: bool = True) -> str:
    if not enable:
        return text
    out = []
    for i, ch in enumerate(text):
        out.append("\033[%sm%s%s" % (ANSI_COLORS[i % len(ANSI_COLORS)], ch, ANSI_RESET))
    return "".join(out)


def strip_ansi(text: str) -> str:
    return re.sub(r"\x1b\[[0-9;]*m", "", text)


def pad_ansi(text: str, width: int) -> str:
    plain = strip_ansi(text)
    if len(plain) >= width:
        return text
    return text + (" " * (width - len(plain)))


def sparkline(values: List[float], width: int = 64, color: bool = False) -> str:
    if not values:
        return "·" * max(1, width)
    vals = list(values)
    if len(vals) > width:
        step = float(len(vals)) / float(width)
        vals = [vals[min(len(vals) - 1, int(i * step))] for i in range(width)]
    elif len(vals) < width:
        pad = [vals[-1]] * (width - len(vals))
        vals = vals + pad
    lo = min(vals)
    hi = max(vals)
    rng = hi - lo
    if abs(rng) < EPS:
        chars = [UTF8_BLOCKS[len(UTF8_BLOCKS) // 2] for _ in vals]
    else:
        chars = []
        for v in vals:
            idx = int(round((len(UTF8_BLOCKS) - 1) * (v - lo) / rng))
            idx = max(0, min(len(UTF8_BLOCKS) - 1, idx))
            chars.append(UTF8_BLOCKS[idx])
    if not color:
        return "".join(chars)
    out = []
    for ch in chars:
        idx = UTF8_BLOCKS.find(ch)
        idx = max(0, idx)
        code = ANSI_COLORS[min(len(ANSI_COLORS) - 1, idx)]
        out.append(ansi(ch, code, True))
    return "".join(out)


def simple_bar(value: float, max_value: float, width: int = 32, color_code: int = 36, color: bool = False) -> str:
    width = max(4, int(width))
    max_value = max(EPS, max_value)
    fill = int(round(width * max(0.0, value) / max_value))
    fill = max(0, min(width, fill))
    body = "█" * fill + "░" * (width - fill)
    if color:
        if fill > 0:
            body = ansi("█" * fill, color_code, True) + ansi("░" * (width - fill), 90, True)
        else:
            body = ansi("░" * width, 90, True)
    return body


def ratio_bar(ratio: float, width: int = 32, color: bool = False) -> str:
    ratio = clamp(ratio, 0.0, 2.0)
    fill = int(round(width * min(1.0, ratio)))
    fill = max(0, min(width, fill))
    over = int(round(width * max(0.0, ratio - 1.0)))
    over = max(0, min(width - fill, over))
    rest = width - fill - over
    if color:
        return ansi("█" * fill, 32, True) + ansi("▓" * over, 36, True) + ansi("░" * rest, 90, True)
    return "█" * fill + "▓" * over + "░" * rest


def signed_bar(value: float, max_abs: float, width: int = 40, color: bool = False) -> str:
    width = max(8, int(width))
    half = width // 2
    max_abs = max(EPS, max_abs)
    magnitude = int(round(half * min(1.0, abs(value) / max_abs)))
    if value >= 0:
        left = " " * half
        right = "█" * magnitude + "░" * (half - magnitude)
        if color:
            right = ansi("█" * magnitude, 32, True) + ansi("░" * (half - magnitude), 90, True)
            left = ansi(left, 90, True)
    else:
        left = "░" * (half - magnitude) + "█" * magnitude
        right = " " * half
        if color:
            left = ansi("░" * (half - magnitude), 90, True) + ansi("█" * magnitude, 31, True)
            right = ansi(right, 90, True)
    center = ansi("│", 37, True) if color else "│"
    return left + center + right


def histogram(values: List[float], bins: int = 8, width: int = 28, color: bool = False) -> List[Tuple[str, int, str]]:
    if not values:
        return []
    lo = min(values)
    hi = max(values)
    if abs(hi - lo) < EPS:
        return [("%s..%s" % (f2(lo), f2(hi)), len(values), simple_bar(len(values), len(values), width, 36, color))]
    counts = [0 for _ in range(bins)]
    for v in values:
        idx = int((v - lo) / (hi - lo + EPS) * bins)
        if idx >= bins:
            idx = bins - 1
        counts[idx] += 1
    mx = max(counts) or 1
    out = []
    for i, c in enumerate(counts):
        a = lo + (hi - lo) * i / bins
        b = lo + (hi - lo) * (i + 1) / bins
        out.append(("%s..%s" % (f2(a), f2(b)), c, simple_bar(c, mx, width, 35 + (i % 3), color)))
    return out


def wrap_text(text: str, width: int = 96, indent: str = "") -> List[str]:
    words = text.split()
    if not words:
        return [indent]
    lines = []
    cur = indent
    for w in words:
        plain_len = len(strip_ansi(cur))
        if plain_len > len(indent) and plain_len + 1 + len(w) > width:
            lines.append(cur)
            cur = indent + w
        else:
            if strip_ansi(cur).strip():
                cur += " " + w
            else:
                cur = indent + w
    if cur:
        lines.append(cur)
    return lines


def pct(x: float) -> str:
    return f2(100.0 * x) + "%"


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Wallet:
    alltag: float = 0.0
    grundversorgung: float = 0.0
    vertrag: float = 0.0
    haftung: float = 0.0
    reserve: float = 0.0

    def total(self) -> float:
        return self.alltag + self.grundversorgung + self.vertrag + self.haftung + self.reserve

    def positive(self) -> float:
        return max(0, self.alltag) + max(0, self.grundversorgung) + max(0, self.vertrag) + max(0, self.reserve)

    def spendable(self, basic: bool = False) -> float:
        x = max(0, self.alltag) + max(0, self.vertrag) + max(0, self.reserve)
        if basic:
            x += max(0, self.grundversorgung)
        return x

    def credit(self, amount: float, account: str = "alltag") -> None:
        if amount <= 0:
            return
        if not hasattr(self, account):
            account = "alltag"
        setattr(self, account, getattr(self, account) + amount)

    def debit(self, amount: float, basic: bool = False, allow_debt: bool = False) -> Tuple[float, float]:
        """Return (paid, unpaid). If allow_debt, remaining becomes negative liability and counts as paid."""
        if amount <= 0:
            return 0.0, 0.0
        rest = amount
        paid = 0.0
        order = ["alltag", "vertrag", "reserve"]
        if basic:
            order.append("grundversorgung")
        for acc in order:
            bal = getattr(self, acc)
            take = min(max(0.0, bal), rest)
            if take > 0:
                setattr(self, acc, bal - take)
                rest -= take
                paid += take
            if rest <= EPS:
                return amount, 0.0
        if allow_debt and rest > EPS:
            self.haftung -= rest
            paid += rest
            rest = 0.0
        return paid, rest

    def charge_norm_loss(self, amount: float) -> Tuple[float, float]:
        """Negative Normereignisse: gezahlter Teil wird vernichtet; Rest wird Haftung."""
        paid, unpaid = self.debit(amount, basic=False, allow_debt=False)
        if unpaid > EPS:
            self.haftung -= unpaid
        return paid, unpaid


@dataclass
class NormProfile:
    domain: str
    plus: Dict[str, float]
    minus: Dict[str, float]
    lam: float
    p_plus: float = 2.0
    p_minus: float = 2.0
    cap: float = 30.0
    protected: bool = False

    def evaluate(self, features: Dict[str, float]) -> Tuple[float, float, float]:
        p = norm(features, self.plus, self.p_plus)
        m = norm(features, self.minus, self.p_minus)
        return p, m, self.lam * (p - m)


@dataclass
class Location:
    name: str
    kind: str
    scarcity: Dict[str, float]
    risk: float
    delay_seconds: float
    infrastructure: float
    oxygen_safety: float
    water_security: float
    debris_risk: float
    trust: float

    def scarce(self, good: str) -> float:
        return max(0.25, float(self.scarcity.get(good, 1.0)))

    def decay(self, rng: random.Random) -> None:
        self.infrastructure = clamp(self.infrastructure - rng.uniform(0.0005, 0.004) * self.risk, 0.05, 1.25)
        if self.kind in ("moon", "orbit", "station"):
            self.oxygen_safety = clamp(self.oxygen_safety - rng.uniform(0.0002, 0.004) * self.risk, 0.05, 1.20)
            self.water_security = clamp(self.water_security - rng.uniform(0.0002, 0.003) * self.risk, 0.05, 1.20)
        if self.kind in ("orbit", "station"):
            self.debris_risk = clamp(self.debris_risk + rng.uniform(0.0, 0.0025) * self.risk, 0.0, 1.0)


@dataclass
class Actor:
    aid: str
    name: str
    kind: str
    location: str
    sector: str = ""
    wallet: Wallet = field(default_factory=Wallet)
    skills: Dict[str, float] = field(default_factory=dict)
    employees: List[str] = field(default_factory=list)
    employer: Optional[str] = None
    health: float = 0.85
    stress: float = 0.25
    fatigue: float = 0.20
    trust: float = 0.65
    reputation: float = 0.50
    media_literacy: float = 0.55
    integrity: float = 0.70
    pressure: float = 0.35
    productivity: float = 1.0
    capital: float = 100.0
    active: bool = True
    meta: Dict[str, Any] = field(default_factory=dict)

    def skill(self, domain: str) -> float:
        return clamp(float(self.skills.get(domain, self.skills.get("general", 0.45))), 0.0, 1.5)

    def row(self) -> Dict[str, Any]:
        return {
            "actor_id": self.aid, "name": self.name, "kind": self.kind, "location": self.location,
            "sector": self.sector, "employer": self.employer or "", "employees": len(self.employees),
            "alltag": self.wallet.alltag, "grundversorgung": self.wallet.grundversorgung,
            "vertrag": self.wallet.vertrag, "haftung": self.wallet.haftung, "reserve": self.wallet.reserve,
            "wallet_total": self.wallet.total(), "positive_money": self.wallet.positive(),
            "health": self.health, "stress": self.stress, "fatigue": self.fatigue,
            "trust": self.trust, "reputation": self.reputation, "media_literacy": self.media_literacy,
            "integrity": self.integrity, "pressure": self.pressure, "productivity": self.productivity,
            "capital": self.capital, "skills": dumps(self.skills), "meta": dumps(self.meta)
        }


@dataclass
class GoodState:
    good: str
    base_price: float
    stock: float
    target: float
    critical: bool
    perish: float
    quality: float = 0.80
    demand_today: float = 0.0
    supply_today: float = 0.0

    def price(self, loc: Location) -> float:
        market_scarcity = clamp((self.target + 1.0) / (self.stock + 1.0), 0.25, 9.0)
        elasticity = 0.78 if self.critical else 0.55
        p = self.base_price * (market_scarcity ** elasticity) * loc.scarce(self.good)
        p *= clamp(1.12 - 0.20 * self.quality, 0.70, 1.25)
        if self.critical and self.stock < 0.25 * self.target:
            p *= 1.18
        return max(0.01, p)

    def tick(self) -> None:
        self.stock *= max(0.0, 1.0 - self.perish)
        self.quality = clamp(0.985 * self.quality + 0.015 * 0.80, 0.05, 1.25)
        self.demand_today = 0.0
        self.supply_today = 0.0


@dataclass
class Event:
    eid: int
    day: int
    actor: str
    actor_name: str
    kind: str
    location: str
    domain: str
    action: str
    features: Dict[str, float]
    plus_norm: float = 0.0
    minus_norm: float = 0.0
    gross_delta: float = 0.0
    net_delta: float = 0.0
    tax: float = 0.0
    destroyed: float = 0.0
    liability: float = 0.0
    disputed: bool = False
    verified: bool = True
    note: str = ""

    def row(self) -> Dict[str, Any]:
        return {
            "event_id": self.eid, "day": self.day, "actor_id": self.actor,
            "actor_name": self.actor_name, "actor_kind": self.kind, "location": self.location,
            "domain": self.domain, "action": self.action, "plus_norm": self.plus_norm,
            "minus_norm": self.minus_norm, "gross_delta": self.gross_delta, "net_delta": self.net_delta,
            "tax": self.tax, "destroyed": self.destroyed, "liability": self.liability,
            "disputed": self.disputed, "verified": self.verified, "features": dumps(self.features), "note": self.note
        }


@dataclass
class Tx:
    tid: int
    day: int
    payer: str
    payer_name: str
    payee: str
    payee_name: str
    amount: float
    requested: float
    reason: str
    domain: str
    good: str
    location: str
    note: str = ""

    def row(self) -> Dict[str, Any]:
        return {
            "tx_id": self.tid, "day": self.day, "payer_id": self.payer, "payer_name": self.payer_name,
            "payee_id": self.payee, "payee_name": self.payee_name, "amount": self.amount,
            "requested_amount": self.requested, "reason": self.reason, "domain": self.domain,
            "good": self.good, "location": self.location, "note": self.note
        }


@dataclass
class Topic:
    title: str
    location: str
    category: str
    factuality: float
    relevance: float
    urgency: float
    emotion: float
    safety_value: float
    rumor: bool = False
    effects: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Norms, goods, sectors
# ---------------------------------------------------------------------------

def make_norms() -> Dict[str, NormProfile]:
    specs = {
        "labor": (
            {"productive_time": 1.0, "quality": 1.7, "reliability": 1.2, "cooperation": 1.1, "safety": 1.1, "learning": 0.7},
            {"fatigue": 0.8, "resource_use": 0.7, "accident_risk": 1.6, "exploitation": 2.1, "coordination_cost": 0.5}, 8.5, 24, False),
        "food": (
            {"nutrition": 1.8, "supply_security": 1.6, "soil_health": 1.1, "health_gain": 1.2, "scarcity_relief": 1.8, "cultural_value": 0.4},
            {"water_use": 1.4, "energy_use": 1.0, "waste": 1.5, "emissions": 1.1, "health_risk": 2.2, "scarcity_use": 1.6}, 9.0, 18, True),
        "water": (
            {"clean_water": 2.0, "recycling": 1.8, "leak_repair": 1.5, "supply_security": 1.8, "health_gain": 1.2},
            {"waste": 1.8, "contamination": 2.4, "scarcity_use": 1.6, "energy_use": 0.8, "infrastructure_wear": 0.8}, 9.5, 20, True),
        "energy": (
            {"energy_output": 1.7, "reliability": 1.4, "storage": 1.0, "grid_stability": 1.5, "scarcity_relief": 1.2, "renewable_share": 1.1},
            {"emissions": 1.6, "hazard": 1.8, "waste_heat": 0.7, "resource_depletion": 1.1, "infrastructure_wear": 0.8}, 8.8, 28, True),
        "media": (
            {"truth": 2.2, "source_quality": 1.9, "public_relevance": 1.6, "correction": 1.3, "public_safety": 1.5, "plurality": 1.0, "context": 1.2},
            {"manipulation": 2.5, "panic": 1.8, "attention_drain": 1.2, "privacy_violation": 1.7, "misinformation_risk": 2.4, "monopoly_power": 1.0}, 10.5, 40, False),
        "consumption": (
            {"utility": 1.2, "need_satisfaction": 1.6, "repairability": 1.0, "shared_use": 0.8, "cultural_value": 0.8},
            {"waste": 1.5, "overconsumption": 1.4, "resource_use": 1.2, "addiction_risk": 1.4, "attention_drain": 0.7}, 6.5, 16, True),
        "transport": (
            {"delivery_value": 1.4, "time_saved": 0.9, "supply_chain_security": 1.5, "access": 1.0, "orbit_stability": 1.7},
            {"fuel_use": 1.2, "accident_risk": 1.6, "emissions": 1.1, "orbital_debris": 2.3, "congestion": 0.8}, 8.0, 32, False),
        "infrastructure": (
            {"maintenance": 1.7, "safety": 1.8, "shelter": 1.3, "resilience": 1.5, "capacity": 1.2, "fault_detection": 1.3},
            {"material_use": 1.0, "energy_loss": 1.2, "delay_risk": 0.9, "failure_risk": 2.3, "bureaucracy": 0.6}, 9.2, 36, True),
        "health": (
            {"health_gain": 2.0, "prevention": 1.7, "empathy": 0.8, "triage_quality": 1.3, "public_health": 1.5, "care_access": 1.1},
            {"infection_risk": 1.8, "resource_use": 0.8, "misdiagnosis_risk": 2.2, "burnout": 1.2, "privacy_violation": 1.0}, 9.8, 28, True),
        "education": (
            {"knowledge_gain": 1.8, "skill_gain": 1.4, "reproducibility": 1.2, "critical_thinking": 1.5, "innovation": 1.2, "social_mobility": 1.1},
            {"misinformation_risk": 1.7, "credential_inflation": 0.8, "energy_use": 0.5, "exclusion": 1.2, "burnout": 0.9}, 8.7, 22, True),
        "governance": (
            {"transparency": 1.8, "appeal_access": 1.6, "participation": 1.2, "conflict_resolution": 1.4, "audit_quality": 1.6, "rights_protection": 2.0},
            {"bureaucracy": 1.0, "coercion": 2.5, "corruption_risk": 2.2, "surveillance": 2.0, "delay_risk": 0.8}, 8.2, 34, False),
        "finance": (
            {"liquidity": 1.4, "risk_sharing": 1.5, "investment": 1.2, "solvency_support": 1.3, "price_discovery": 0.9},
            {"speculation": 1.5, "default_risk": 2.0, "fraud": 2.6, "leverage": 1.6, "systemic_risk": 2.2}, 7.8, 42, False),
        "space": (
            {"oxygen_recycling": 2.1, "station_safety": 2.2, "orbit_stability": 2.0, "research_value": 1.3, "logistics_reliability": 1.6, "debris_removal": 2.2, "life_support": 2.3},
            {"delta_v_cost": 1.2, "debris_risk": 2.5, "radiation_risk": 1.8, "oxygen_loss": 2.2, "launch_emissions": 1.1, "mission_failure_risk": 2.4}, 12.5, 58, True),
        "environment": (
            {"carbon_capture": 1.5, "biodiversity": 1.7, "water_cleaning": 1.5, "soil_health": 1.4, "repair": 1.3, "risk_reduction": 1.5},
            {"pollution": 2.0, "land_use": 1.1, "emissions": 1.7, "toxicity": 2.3, "resource_depletion": 1.3}, 9.0, 35, False),
        "culture": (
            {"cohesion": 1.2, "meaning": 1.0, "inclusion": 1.2, "creativity": 1.3, "conflict_reduction": 0.9},
            {"addiction_risk": 1.3, "attention_drain": 0.9, "exclusion": 1.4, "manipulation": 1.4, "resource_use": 0.6}, 5.8, 16, False),
    }
    return {d: NormProfile(d, p, m, lam, cap=cap, protected=prot) for d, (p, m, lam, cap, prot) in specs.items()}


GOODS = {
    "food": (3.2, 7.0, True, 0.035), "water": (1.1, 10.0, True, 0.002),
    "energy": (2.4, 8.0, True, 0.0), "housing": (7.0, 3.0, True, 0.0),
    "healthcare": (5.5, 2.5, True, 0.01), "education": (4.2, 2.2, False, 0.0),
    "consumer_goods": (6.0, 4.0, False, 0.005), "media": (0.8, 8.0, False, 0.25),
    "transport": (4.5, 3.0, False, 0.0), "spares": (9.0, 1.6, True, 0.0),
    "oxygen": (2.8, 8.0, True, 0.01), "raw_materials": (4.0, 3.0, False, 0.0),
    "data_bandwidth": (1.4, 6.0, False, 0.0), "research": (9.0, 1.0, False, 0.02),
}
BASIC_GOODS = set(["food", "water", "energy", "housing", "healthcare", "oxygen"])


SECTORS = {
    "agriculture": ("food", "food", 2.8, 8, 4.3, {"water": .22, "energy": .07, "raw_materials": .02}),
    "water_utility": ("water", "water", 3.4, 7, 4.6, {"energy": .09, "spares": .01}),
    "energy": ("energy", "energy", 3.0, 8, 4.8, {"raw_materials": .05, "spares": .02}),
    "construction": ("infrastructure", "housing", 1.2, 9, 5.0, {"raw_materials": .28, "energy": .12, "spares": .03}),
    "manufacturing": ("consumption", "consumer_goods", 2.2, 10, 4.7, {"raw_materials": .20, "energy": .16, "spares": .02}),
    "logistics": ("transport", "transport", 2.0, 7, 4.4, {"energy": .20, "spares": .025}),
    "healthcare": ("health", "healthcare", 1.7, 8, 5.2, {"energy": .05, "spares": .025, "water": .05}),
    "education": ("education", "education", 1.9, 7, 4.7, {"energy": .04, "data_bandwidth": .08}),
    "research": ("education", "research", 1.1, 6, 5.6, {"energy": .12, "data_bandwidth": .15, "spares": .03}),
    "media": ("media", "media", 4.0, 5, 4.5, {"data_bandwidth": .08, "energy": .02}),
    "finance": ("finance", "data_bandwidth", 0.8, 5, 5.0, {"data_bandwidth": .06, "energy": .02}),
    "space_ops": ("space", "oxygen", 1.6, 7, 6.2, {"energy": .18, "spares": .12, "water": .04}),
    "mining": ("environment", "raw_materials", 1.9, 8, 5.4, {"energy": .18, "water": .03, "spares": .04}),
    "data_network": ("infrastructure", "data_bandwidth", 2.5, 6, 5.2, {"energy": .08, "spares": .04}),
}


# Feature templates: used for production events, adjusted by quality/safety/scarcity.
PLUS_FEATURES = {
    "food": {"nutrition": .7, "supply_security": .75, "soil_health": .5, "scarcity_relief": .2, "health_gain": .35},
    "water": {"clean_water": .8, "recycling": .65, "supply_security": .75, "leak_repair": .45},
    "energy": {"energy_output": .85, "reliability": .75, "grid_stability": .65, "renewable_share": .55},
    "infrastructure": {"maintenance": .55, "safety": .65, "shelter": .55, "resilience": .55, "capacity": .65, "fault_detection": .45},
    "consumption": {"utility": .65, "repairability": .55, "shared_use": .25, "need_satisfaction": .55},
    "transport": {"delivery_value": .75, "time_saved": .55, "supply_chain_security": .70, "access": .55},
    "health": {"health_gain": .85, "prevention": .55, "empathy": .60, "triage_quality": .65, "care_access": .60},
    "education": {"knowledge_gain": .78, "skill_gain": .70, "critical_thinking": .65, "social_mobility": .55, "innovation": .25},
    "media": {"truth": .65, "source_quality": .60, "public_relevance": .55, "context": .50, "plurality": .45},
    "finance": {"liquidity": .65, "risk_sharing": .55, "investment": .50, "price_discovery": .45},
    "space": {"oxygen_recycling": .78, "station_safety": .82, "orbit_stability": .65, "life_support": .82, "logistics_reliability": .60},
    "environment": {"repair": .30, "risk_reduction": .25, "soil_health": .25, "water_cleaning": .25},
}
MINUS_FEATURES = {
    "food": {"water_use": .45, "energy_use": .20, "waste": .18, "emissions": .25},
    "water": {"energy_use": .20, "infrastructure_wear": .12, "waste": .10, "contamination": .04},
    "energy": {"emissions": .28, "hazard": .18, "waste_heat": .14, "resource_depletion": .12},
    "infrastructure": {"material_use": .38, "energy_loss": .18, "delay_risk": .12, "failure_risk": .16},
    "consumption": {"resource_use": .38, "waste": .25, "overconsumption": .18},
    "transport": {"fuel_use": .38, "accident_risk": .18, "emissions": .24, "congestion": .16},
    "health": {"resource_use": .18, "infection_risk": .12, "burnout": .18},
    "education": {"energy_use": .10, "burnout": .12, "exclusion": .10, "misinformation_risk": .05},
    "media": {"attention_drain": .25, "misinformation_risk": .16, "manipulation": .10},
    "finance": {"speculation": .18, "default_risk": .20, "leverage": .18, "systemic_risk": .12},
    "space": {"delta_v_cost": .30, "debris_risk": .18, "radiation_risk": .16, "oxygen_loss": .10, "mission_failure_risk": .18},
    "environment": {"land_use": .30, "resource_depletion": .38, "pollution": .20, "emissions": .16},
}


# ---------------------------------------------------------------------------
# Market
# ---------------------------------------------------------------------------

class Market:
    def __init__(self, loc: Location, actor_id: str, population: int):
        self.loc = loc
        self.actor_id = actor_id
        self.goods: Dict[str, GoodState] = {}
        pop = max(4, population)
        for good, (base, per_person, critical, perish) in GOODS.items():
            target = per_person * pop
            if loc.kind in ("moon", "orbit", "station") and good in ("water", "energy", "oxygen", "spares"):
                target *= 1.35
            stock = target * max(0.42, 1.12 / loc.scarce(good))
            self.goods[good] = GoodState(good, base, stock, target, critical, perish)

    def price(self, good: str) -> float:
        return self.goods[good].price(self.loc) if good in self.goods else 1.0

    def buy(self, sim: "Simulation", buyer: str, good: str, qty: float, reason: str,
            basic: bool = False, debt: bool = False) -> Tuple[float, float]:
        if qty <= 0 or good not in self.goods:
            return 0.0, 0.0
        g = self.goods[good]
        q = min(qty, max(0.0, g.stock))
        if q <= EPS:
            g.demand_today += qty
            return 0.0, 0.0
        amount = q * self.price(good)
        paid = sim.transfer(buyer, self.actor_id, amount, reason, "market", good, self.loc.name, basic, debt)
        delivered = q * clamp(div(paid, amount, 0.0), 0.0, 1.0)
        g.stock -= delivered
        g.demand_today += delivered
        return delivered, paid

    def sell(self, sim: "Simulation", seller: str, good: str, qty: float, quality: float, reason: str) -> float:
        if qty <= 0 or good not in self.goods:
            return 0.0
        g = self.goods[good]
        price = self.price(good) * clamp(0.65 + 0.45 * quality, 0.40, 1.35)
        amount = qty * price
        old = g.stock
        g.stock += qty
        g.supply_today += qty
        g.quality = clamp((old * g.quality + qty * quality) / max(EPS, old + qty), 0.05, 1.25)
        return sim.transfer(self.actor_id, seller, amount, reason, "market", good, self.loc.name, False, True)

    def index(self, only_basic: bool = False) -> float:
        if only_basic:
            weights = {"food": .28, "water": .18, "energy": .18, "housing": .18, "healthcare": .10,
                       "oxygen": .08 if self.loc.kind in ("moon", "orbit", "station") else 0.0}
        else:
            weights = {"food": .18, "water": .08, "energy": .12, "housing": .18, "healthcare": .09,
                       "education": .06, "consumer_goods": .10, "media": .03, "transport": .07,
                       "spares": .04, "data_bandwidth": .03,
                       "oxygen": .02 if self.loc.kind in ("moon", "orbit", "station") else 0.0}
        wsum, bsum = 0.0, 0.0
        for good, w in weights.items():
            if w <= 0:
                continue
            base = GOODS[good][0] * self.loc.scarce(good)
            wsum += w * self.price(good)
            bsum += w * base
        return 100.0 * div(wsum, bsum, 1.0)

    def tick(self) -> None:
        for g in self.goods.values():
            g.tick()


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

class Simulation:
    def __init__(self, days: int, persons: int, seed: int, scenario: str, out: str, quiet: bool = False):
        self.days = days
        self.person_count = persons
        self.seed = seed
        self.scenario = scenario
        self.out = out
        self.quiet = quiet
        self.rng = random.Random(seed)
        self.day = 0
        self.norms = make_norms()
        self.actors: Dict[str, Actor] = {}
        self.locations: Dict[str, Location] = {}
        self.markets: Dict[str, Market] = {}
        self.events: List[Event] = []
        self.transactions: List[Tx] = []
        self.metrics: List[Dict[str, Any]] = []
        self.topics: List[Topic] = []
        self.last_reports: List[Dict[str, Any]] = []
        self.topic_history: List[Dict[str, Any]] = []
        self.gov = "PUBLIC_ZEMO"
        self.bank = "BANK_DELTA"
        self.insurer = "INSURANCE_MUTUAL"
        self.market_ids: List[str] = []
        self.eid = 0
        self.tid = 0
        self.aid = 0
        self.created = 0.0
        self.destroyed = 0.0
        self.liability_created = 0.0
        self.disputed = 0
        self.appeals_granted = 0
        self.tax_rate = 0.14
        self.transaction_tax = 0.006
        self.negative_used: Dict[Tuple[int, str], float] = defaultdict(float)
        self.action_counter: Dict[Tuple[int, str, str, str], int] = defaultdict(int)
        self.initial_index = 100.0
        self.notes: List[str] = []
        self.build_world()

    # IDs and filters
    def next_aid(self, prefix: str) -> str:
        self.aid += 1
        return "%s_%05d" % (prefix, self.aid)

    def next_eid(self) -> int:
        self.eid += 1
        return self.eid

    def next_tid(self) -> int:
        self.tid += 1
        return self.tid

    def people(self) -> List[Actor]:
        return [a for a in self.actors.values() if a.kind == "person" and a.active]

    def firms(self) -> List[Actor]:
        return [a for a in self.actors.values() if a.kind == "firm" and a.active]

    def media(self) -> List[Actor]:
        return [a for a in self.actors.values() if a.kind == "media" and a.active]

    def infrastructure(self) -> List[Actor]:
        return [a for a in self.actors.values() if a.kind == "infrastructure" and a.active]

    # World creation
    def build_world(self) -> None:
        self.build_locations()
        self.build_public_actors()
        self.build_people()
        self.build_firms()
        self.build_media()
        self.build_infrastructure()
        self.build_markets()
        self.allocate_jobs(initial=True)
        self.seed_loans()
        self.initial_index = self.price_index()

    def build_locations(self) -> None:
        self.locations = {
            "Earth": Location("Earth", "earth",
                              {"food": 1.0, "water": .95, "energy": 1.0, "housing": 1.05, "oxygen": .35,
                               "spares": 1.0, "data_bandwidth": .9}, .65, 0.0, .86, 1.20, .92, .03, .65),
            "Moon": Location("Moon", "moon",
                             {"food": 1.9, "water": 2.4, "energy": 1.7, "housing": 2.0, "oxygen": 2.2,
                              "spares": 2.3, "raw_materials": .75, "transport": 2.2, "data_bandwidth": 1.3}, 1.35, 1.3, .72, .78, .62, .05, .58),
            "Orbit": Location("Orbit", "orbit",
                              {"food": 2.3, "water": 2.2, "energy": 1.55, "housing": 2.4, "oxygen": 2.7,
                               "spares": 2.8, "transport": 2.4, "data_bandwidth": .8}, 1.55, .1, .74, .74, .68, .11, .60),
            "Station": Location("Station", "station",
                                {"food": 2.6, "water": 2.5, "energy": 1.8, "housing": 2.7, "oxygen": 3.2,
                                 "spares": 3.0, "transport": 2.7, "data_bandwidth": .95}, 1.80, .05, .70, .72, .66, .13, .62),
        }
        if self.scenario == "scarcity":
            for l in self.locations.values():
                l.scarcity["food"] *= 1.25
                l.scarcity["energy"] *= 1.20
            self.notes.append("scarcity: Nahrung und Energie starten knapper.")
        elif self.scenario == "media_crisis":
            for l in self.locations.values():
                l.trust -= .15
            self.notes.append("media_crisis: Öffentliches Vertrauen startet niedriger.")
        elif self.scenario == "orbit_emergency":
            self.locations["Orbit"].debris_risk += .18
            self.locations["Station"].debris_risk += .18
            self.locations["Station"].oxygen_safety -= .10
            self.notes.append("orbit_emergency: Erhöhtes Trümmer- und Sauerstoffrisiko.")
        elif self.scenario == "lunar_expansion":
            self.locations["Moon"].infrastructure += .08
            self.locations["Moon"].scarcity["housing"] *= .85
            self.notes.append("lunar_expansion: Bessere Mondinfrastruktur.")
        elif self.scenario == "boom":
            for l in self.locations.values():
                l.infrastructure += .06
                l.scarcity["energy"] *= .9
            self.notes.append("boom: Bessere Infrastruktur und Energieversorgung.")

    def build_public_actors(self) -> None:
        self.actors[self.gov] = Actor(self.gov, "ZEMO Public Council / Öffentlicher Fonds", "public", "Earth", "governance",
                                      Wallet(250000, 0, 0, 0, 200000), {"governance": .85, "finance": .80},
                                      integrity=.82, reputation=.75)
        self.actors[self.bank] = Actor(self.bank, "Delta Clearing Bank", "firm", "Earth", "finance",
                                       Wallet(120000, 0, 0, 0, 180000), {"finance": .85, "governance": .55},
                                       productivity=1.15, capital=250, integrity=.70, pressure=.45,
                                       meta={"target": 8, "loans": []})
        self.actors[self.insurer] = Actor(self.insurer, "Mutual Risk & Life-Support Insurance", "firm", "Earth", "finance",
                                          Wallet(100000, 0, 0, 0, 150000), {"finance": .80, "space": .55, "health": .55},
                                          productivity=1.05, capital=210, integrity=.76, pressure=.36,
                                          meta={"target": 7, "pool": 100000})

    def build_people(self) -> None:
        first = "Ada Lina Mira Noah Samir Lea Jonas Aiko Nia Omar Iris Mika Ravi Elena Theo Mina Yara Kian Sofia Tariq Nora Luis Hana Juri Amal Rin David Eva Malik Zoe".split()
        last = "Keller Novak Singh Rossi Chen Yilmaz Okafor Weber Silva Nguyen Hoffmann Rahman Ito Garcia Kowalski Mensah Dubois Schmidt Patel Sato".split()
        loc_weights = [("Earth", .78), ("Moon", .075), ("Orbit", .075), ("Station", .07)]
        if self.scenario == "lunar_expansion":
            loc_weights = [("Earth", .70), ("Moon", .16), ("Orbit", .07), ("Station", .07)]
        if self.scenario == "orbit_emergency":
            loc_weights = [("Earth", .80), ("Moon", .08), ("Orbit", .06), ("Station", .06)]
        domains = list(self.norms.keys())
        sectors = list(SECTORS.keys())
        for _ in range(self.person_count):
            loc = weighted_choice(self.rng, loc_weights)
            pref = self.rng.choice(sectors)
            base = clamp(self.rng.gauss(.52, .17), .08, 1.1)
            skills = {"general": base}
            for d in domains:
                skills[d] = clamp(base + self.rng.gauss(0, .16), .02, 1.2)
            skills[SECTORS[pref][0]] = clamp(skills[SECTORS[pref][0]] + self.rng.uniform(.08, .35), .02, 1.35)
            if loc in ("Moon", "Orbit", "Station") or pref == "space_ops":
                skills["space"] = clamp(skills["space"] + self.rng.uniform(.06, .30), .02, 1.35)
            aid = self.next_aid("P")
            trust = self.locations[loc].trust + self.rng.gauss(0, .12)
            self.actors[aid] = Actor(
                aid, "%s %s" % (self.rng.choice(first), self.rng.choice(last)), "person", loc, pref,
                Wallet(self.rng.uniform(80, 260), self.rng.uniform(8, 32), 0, 0, self.rng.uniform(0, 60)),
                skills, health=clamp(self.rng.gauss(.82, .12), .20, 1.0), fatigue=clamp(self.rng.gauss(.22, .08), 0, .7),
                stress=clamp(self.rng.gauss(.27, .12), 0, .9), trust=clamp(trust, .05, 1.0),
                reputation=clamp(self.rng.gauss(.52, .12), .05, 1.0), media_literacy=clamp(self.rng.gauss(.55, .18), .05, 1.0),
                productivity=clamp(self.rng.gauss(1.0, .15), .45, 1.45), integrity=clamp(self.rng.gauss(.68, .15), .10, 1.0),
                pressure=clamp(self.rng.gauss(.35, .15), 0, 1.0), meta={"preferred_sector": pref, "education": clamp(self.rng.gauss(.55, .2), .05, 1.0)}
            )

    def allowed_sectors(self, loc: str) -> List[str]:
        if loc == "Earth":
            return ["agriculture", "water_utility", "energy", "construction", "manufacturing", "logistics",
                    "healthcare", "education", "research", "media", "finance", "data_network", "mining"]
        if loc == "Moon":
            return ["space_ops", "mining", "energy", "construction", "water_utility", "agriculture",
                    "logistics", "healthcare", "research", "data_network", "education"]
        if loc == "Orbit":
            return ["space_ops", "data_network", "energy", "logistics", "research", "healthcare",
                    "manufacturing", "media", "finance"]
        return ["space_ops", "data_network", "energy", "healthcare", "research", "education",
                "logistics", "manufacturing", "media"]

    def build_firms(self) -> None:
        pops = Counter(p.location for p in self.people())
        for loc, pop in pops.items():
            sectors = self.allowed_sectors(loc)
            weighted = []
            for s in sectors:
                w = 1.0
                if s in ("agriculture", "water_utility", "energy", "space_ops", "healthcare"):
                    w = 1.8
                if loc in ("Orbit", "Station") and s == "space_ops":
                    w = 3.0
                if loc == "Moon" and s in ("mining", "space_ops"):
                    w = 2.4
                weighted.append((s, w))
            for _ in range(max(4, pop // 22)):
                self.create_firm(weighted_choice(self.rng, weighted), loc)
            for s in ("energy", "water_utility", "healthcare"):
                if s in sectors:
                    self.create_firm(s, loc)
            if loc in ("Moon", "Orbit", "Station"):
                self.create_firm("space_ops", loc)

    def create_firm(self, sector: str, loc: str) -> None:
        domain, good, base_output, target, wage, inputs = SECTORS[sector]
        aid = self.next_aid("F")
        names = {
            "agriculture": "Nahrung", "water_utility": "Wasser", "energy": "Energie", "construction": "Infrastruktur",
            "manufacturing": "Industrie", "logistics": "Logistik", "healthcare": "Gesundheit", "education": "Bildung",
            "research": "Forschung", "media": "Medien", "finance": "Finanz", "space_ops": "Raumfahrt",
            "mining": "Rohstoffe", "data_network": "Daten"
        }
        self.actors[aid] = Actor(
            aid, "%s %s Cooperative" % (loc, names.get(sector, sector)), "firm", loc, sector,
            Wallet(self.rng.uniform(1600, 6500) * self.locations[loc].scarce("housing") ** .15, 0, 0, 0, self.rng.uniform(600, 4000)),
            {domain: clamp(self.rng.gauss(.65, .14), .25, 1.2), "finance": self.rng.uniform(.25, .8)},
            productivity=clamp(self.rng.gauss(1.0, .20), .45, 1.6), capital=self.rng.uniform(80, 250),
            integrity=clamp(self.rng.gauss(.68, .16), .10, 1.0), pressure=clamp(self.rng.gauss(.38, .18), 0, 1),
            reputation=clamp(self.rng.gauss(.55, .13), .05, 1.0),
            meta={"target": max(2, int(target * self.rng.uniform(.55, 1.35))), "quality": clamp(self.rng.gauss(.78, .12), .25, 1.1),
                  "fraud_risk": clamp(self.rng.gauss(.08 + .18 * (1 - self.rng.random()), .05), 0, .5), "loans": []}
        )

    def build_media(self) -> None:
        names = [("Delta Public News", "Earth", .84, .18), ("Orbit Signal", "Orbit", .72, .35),
                 ("Lunar Ledger", "Moon", .76, .30), ("Earth Commons Daily", "Earth", .70, .38),
                 ("FastFeed Network", "Earth", .58, .78), ("DeepContext Review", "Earth", .86, .20),
                 ("Station Safety Bulletin", "Station", .84, .18)]
        for name, loc, integ, pressure in names:
            if self.scenario == "media_crisis" and "FastFeed" in name:
                integ = .46
                pressure = .88
            aid = self.next_aid("M")
            self.actors[aid] = Actor(
                aid, name, "media", loc, "media", Wallet(self.rng.uniform(1800, 8000), 0, 0, 0, self.rng.uniform(1000, 6000)),
                {"media": clamp(self.rng.gauss(.75, .12), .25, 1.2), "education": self.rng.uniform(.35, .9)},
                productivity=clamp(self.rng.gauss(1.0, .18), .5, 1.4), integrity=integ, pressure=pressure,
                reputation=clamp(self.rng.gauss(.62, .16), .05, 1.0),
                meta={"target": self.rng.randint(3, 10), "audience": self.rng.uniform(.03, .18),
                      "last_truth": .6, "last_manipulation": .2, "last_attention": .3, "correction_policy": self.rng.uniform(.25, .85)}
            )

    def build_infrastructure(self) -> None:
        for name, loc, sector in [("Earth Grid Backbone", "Earth", "infrastructure"), ("Lunar Habitat Ring", "Moon", "space"),
                                  ("LEO Satellite Net", "Orbit", "space"), ("Orbital Research Station", "Station", "space")]:
            aid = self.next_aid("I")
            self.actors[aid] = Actor(
                aid, name, "infrastructure", loc, sector, Wallet(25000, 0, 0, 0, 50000),
                {"infrastructure": .70, "space": .75 if loc != "Earth" else .45}, health=self.locations[loc].infrastructure,
                integrity=.80, reputation=.70, meta={"safety": self.locations[loc].infrastructure, "backlog": self.rng.uniform(.05, .22)}
            )

    def build_markets(self) -> None:
        pops = Counter(p.location for p in self.people())
        for loc, obj in self.locations.items():
            mid = "MARKET_%s" % loc.upper()
            self.market_ids.append(mid)
            self.actors[mid] = Actor(mid, "Aggregierter Markt %s" % loc, "market", loc, "market",
                                     Wallet(900000, 0, 0, 0, 900000), {"finance": .6}, meta={"role": "market_maker"})
            self.markets[loc] = Market(obj, mid, pops.get(loc, 5))

    def allocate_jobs(self, initial: bool = False) -> None:
        free = [p for p in self.people() if p.employer is None]
        self.rng.shuffle(free)
        byloc = defaultdict(list)
        for p in free:
            byloc[p.location].append(p)
        employers = [f for f in self.firms() if f.aid not in (self.bank, self.insurer)] + self.media()
        self.rng.shuffle(employers)
        for firm in employers:
            target = int(firm.meta.get("target", 5))
            if len(firm.employees) >= target:
                continue
            candidates = byloc.get(firm.location, [])
            domain = SECTORS.get(firm.sector, (firm.sector, "", 0, 0, 0, {}))[0]
            candidates.sort(key=lambda p: p.skill(domain) + .12 * p.reputation - .10 * p.stress, reverse=True)
            while candidates and len(firm.employees) < target:
                p = candidates.pop(0)
                p.employer = firm.aid
                firm.employees.append(p.aid)
                if initial:
                    p.meta["preferred_sector"] = firm.sector

    def seed_loans(self) -> None:
        bank = self.actors[self.bank]
        for firm in self.firms():
            if firm.aid in (self.bank, self.insurer):
                continue
            if self.rng.random() < .28:
                principal = self.rng.uniform(600, 4500)
                paid, _ = bank.wallet.debit(principal, allow_debt=False)
                firm.wallet.credit(paid, "reserve")
                firm.meta.setdefault("loans", []).append({"principal": paid, "rate": self.rng.uniform(.00015, .00055), "lender": self.bank})

    # Core settlement
    def emit(self, actor: Actor, domain: str, action: str, features: Dict[str, float],
             verified: bool = True, note: str = "", location: Optional[str] = None) -> Event:
        prof = self.norms[domain] if domain in self.norms else self.norms["consumption"]
        clean = {k: clamp(float(v), 0.0, 3.0) for k, v in features.items()}
        plus, minus, raw = prof.evaluate(clean)

        if not verified:
            raw *= .60 if raw >= 0 else .85

        key = (self.day, actor.aid, domain, action)
        count = self.action_counter[key]
        self.action_counter[key] += 1
        if raw > 0 and count > 4:
            raw *= 1.0 / math.sqrt(1.0 + .20 * (count - 4))

        ev = Event(self.next_eid(), self.day, actor.aid, actor.name, actor.kind, location or actor.location,
                   domain, action, clean, plus, minus, raw, verified=verified, note=note)

        if raw >= 0:
            tax = raw * self.tax_rate
            actor.wallet.credit(raw - tax)
            self.actors[self.gov].wallet.credit(tax, "vertrag")
            ev.tax = tax
            ev.net_delta = raw - tax
            self.created += raw
            actor.reputation = clamp(actor.reputation + .0025 * math.tanh(raw / 20), 0, 1.2)
        else:
            dispute_p = .02 + (.03 if prof.protected else 0) + (.08 if not verified else 0)
            if self.rng.random() < dispute_p:
                ev.disputed = True
                self.disputed += 1
                if self.rng.random() < .55:
                    raw *= .25
                    ev.gross_delta = raw
                    self.appeals_granted += 1
            cap = prof.cap * clamp(.75 + .45 * self.locations.get(actor.location, self.locations["Earth"]).risk, .65, 1.8)
            used = self.negative_used[(self.day, actor.aid)]
            charge = min(-raw, max(0.0, cap - used))
            if prof.protected and actor.wallet.spendable(False) < 12.0:
                charge *= .35
            paid, unpaid = actor.wallet.charge_norm_loss(charge)
            ev.destroyed = paid
            ev.liability = unpaid
            ev.net_delta = -charge
            self.negative_used[(self.day, actor.aid)] += charge
            self.destroyed += paid
            self.liability_created += unpaid
            actor.reputation = clamp(actor.reputation - .003 * math.tanh(charge / 20), 0, 1.2)
        self.events.append(ev)
        return ev

    def transfer(self, payer_id: str, payee_id: str, amount: float, reason: str, domain: str = "transfer",
                 good: str = "", location: str = "", basic: bool = False, debt: bool = False, note: str = "") -> float:
        if amount <= 0 or payer_id not in self.actors or payee_id not in self.actors:
            return 0.0
        payer = self.actors[payer_id]
        payee = self.actors[payee_id]
        paid, unpaid = payer.wallet.debit(amount, basic=basic, allow_debt=debt)
        if paid > 0:
            payee.wallet.credit(paid)
        tax_paid = 0.0
        if paid > 0 and good not in BASIC_GOODS and reason not in ("basic_access",):
            tax_paid, _ = payee.wallet.debit(paid * self.transaction_tax)
            if tax_paid > 0:
                self.actors[self.gov].wallet.credit(tax_paid, "vertrag")
        if note:
            note2 = note
        else:
            note2 = ""
        if unpaid > EPS:
            note2 += "; partial"
        if tax_paid > 0:
            note2 += "; tx_tax=" + f3(tax_paid)
        self.transactions.append(Tx(self.next_tid(), self.day, payer_id, payer.name, payee_id, payee.name,
                                    paid, amount, reason, domain, good, location or payer.location, note2.strip("; ")))
        return paid

    # Run loop
    def run(self) -> None:
        mkdir(self.out)
        if not self.quiet:
            print("Delta-Norm-Wirtschaftssimulation v%s | days=%d persons=%d seed=%d scenario=%s" %
                  (VERSION, self.days, self.person_count, self.seed, self.scenario))
        t0 = time.time()
        for d in range(1, self.days + 1):
            self.day = d
            self.simulate_day()
            if not self.quiet and (d == 1 or d == self.days or d % max(1, self.days // 10) == 0):
                m = self.metrics[-1]
                print("Tag %4d | Preisindex %7.2f | Geldmenge %11.1f | Arbeitslosigkeit %5.1f%% | Vertrauen %.2f" %
                      (d, m["price_index"], m["broad_money"], 100 * m["unemployment"], m["avg_trust"]))
        runtime = time.time() - t0
        self.write_outputs(runtime)
        if not self.quiet:
            print("\n" + self.build_utf8_dashboard(runtime, color=True))
            print("Fertig: %s" % os.path.abspath(self.out))

    def simulate_day(self) -> None:
        self.action_counter = defaultdict(int)
        for loc in self.locations.values():
            loc.decay(self.rng)
        self.topics = self.generate_topics()
        for t in self.topics:
            self.topic_history.append({"day": self.day, "title": t.title, "location": t.location, "category": t.category, "rumor": t.rumor, "factuality": t.factuality, "urgency": t.urgency, "emotion": t.emotion})
        self.apply_topic_effects()
        self.basic_access()
        self.labor_cycle()
        self.production_cycle()
        self.space_cycle()
        self.media_cycle()
        self.consumption_cycle()
        self.education_health_culture_cycle()
        self.finance_cycle()
        self.governance_cycle()
        self.logistics_balance()
        for m in self.markets.values():
            m.tick()
        self.collect_metrics()
        self.policy_update()

    # Topics and world shocks
    def generate_topics(self) -> List[Topic]:
        topics = [Topic("Daily Delta Supply Index", "Earth", "economy", .92, .55, .25, .18, .35)]
        probs = {"weather": .10, "solar": .045, "dust": .04, "station": .035, "research": .045, "rumor": .075, "cyber": .035, "supply": .06}
        if self.scenario == "media_crisis":
            probs["rumor"] += .12
        if self.scenario == "orbit_emergency":
            probs["solar"] += .06
            probs["station"] += .08
        if self.scenario == "scarcity":
            probs["weather"] += .08
            probs["supply"] += .06
        if self.scenario == "boom":
            probs["research"] += .06
        r = self.rng.random
        if r() < probs["weather"]:
            severe = r() < .45
            topics.append(Topic("Earth weather shock affects food logistics" if severe else "Good harvest improves food supply",
                                "Earth", "food", .88, .80, .65 if severe else .35, .55 if severe else .25, .65,
                                effects={"food": -.08 if severe else .06, "water": -.04 if severe else .02}))
        if r() < probs["solar"]:
            topics.append(Topic("Solar storm warning for satellites and stations", "Orbit", "space", .84, .90, .85, .62, .95,
                                effects={"debris": .03, "energy_orbit": -.07, "data": -.05}))
        if r() < probs["dust"]:
            topics.append(Topic("Lunar dust storm reduces solar collection", "Moon", "energy", .86, .74, .60, .44, .70,
                                effects={"energy_moon": -.09, "spares_moon": -.03}))
        if r() < probs["station"]:
            topics.append(Topic("Station life-support anomaly under review", "Station", "space", .78, .96, .92, .72, 1.0,
                                effects={"oxygen_safety": -.05, "oxygen_station": -.05}))
        if r() < probs["research"]:
            loc = weighted_choice(self.rng, [("Earth", .6), ("Moon", .16), ("Orbit", .12), ("Station", .12)])
            topics.append(Topic("Open research breakthrough improves recycling efficiency", loc, "research", .90, .68, .30, .28, .55,
                                effects={"research": .03}))
        if r() < probs["rumor"]:
            loc = weighted_choice(self.rng, [("Earth", .55), ("Moon", .14), ("Orbit", .15), ("Station", .16)])
            topics.append(Topic("Unverified viral claim about supply failure", loc, "rumor", self.rng.uniform(.10, .42), .45, .70, .95, .10, True,
                                effects={"panic": .06}))
        if r() < probs["cyber"]:
            topics.append(Topic("Cyber incident slows settlement and data oracles", "Earth", "governance", .82, .72, .62, .50, .70,
                                effects={"data": -.08, "trust": -.02}))
        if r() < probs["supply"]:
            loc = weighted_choice(self.rng, [("Earth", .55), ("Moon", .18), ("Orbit", .13), ("Station", .14)])
            topics.append(Topic("Supply convoy delay changes local scarcity", loc, "transport", .85, .78, .65, .44, .70,
                                effects={"spares": -.05}))
        return topics

    def apply_topic_effects(self) -> None:
        for t in self.topics:
            market = self.markets.get(t.location, self.markets["Earth"])
            loc = self.locations.get(t.location, self.locations["Earth"])
            for k, v in t.effects.items():
                if k in market.goods:
                    market.goods[k].stock *= clamp(1.0 + v, .65, 1.35)
                elif k == "energy_orbit":
                    self.markets["Orbit"].goods["energy"].stock *= clamp(1 + v, .65, 1.2)
                elif k == "energy_moon":
                    self.markets["Moon"].goods["energy"].stock *= clamp(1 + v, .65, 1.2)
                elif k == "spares_moon":
                    self.markets["Moon"].goods["spares"].stock *= clamp(1 + v, .65, 1.2)
                elif k == "oxygen_station":
                    self.markets["Station"].goods["oxygen"].stock *= clamp(1 + v, .65, 1.2)
                elif k == "oxygen_safety":
                    self.locations["Station"].oxygen_safety = clamp(self.locations["Station"].oxygen_safety + v, .05, 1.2)
                elif k == "debris":
                    loc.debris_risk = clamp(loc.debris_risk + v, 0, 1)
                elif k == "data":
                    market.goods["data_bandwidth"].stock *= clamp(1 + v, .65, 1.2)
                elif k == "trust":
                    loc.trust = clamp(loc.trust + v, .05, 1)
                elif k == "panic":
                    loc.trust = clamp(loc.trust - .5 * v, .05, 1)

    # Monetary constitution
    def basic_access(self) -> None:
        if self.day % 7 != 0:
            return
        for p in self.people():
            idx = self.markets[p.location].index(True)
            amount = max(.15, 2.2 * div(idx, 100, 1.0) * clamp(1.25 - p.wallet.spendable() / 220.0, .10, 1.0))
            p.wallet.credit(amount, "grundversorgung")
            self.created += amount
            self.transactions.append(Tx(self.next_tid(), self.day, "ZEMO", "ZEMO Grundversorgung", p.aid, p.name,
                                        amount, amount, "basic_access", "governance", "basic_access", p.location,
                                        "Verfassungsrechtlicher Mindestzugang"))

    def policy_update(self) -> None:
        if not self.metrics:
            return
        m = self.metrics[-1]
        gap = div(m["price_index"] - self.initial_index, self.initial_index, 0.0)
        factor = clamp(1.0 - .33 * gap * .012, .988, 1.012)
        for prof in self.norms.values():
            prof.lam = clamp(prof.lam * factor, .05, 250)
        if m["food_stock_ratio"] < .65:
            self.norms["food"].lam *= 1.008
        if m["water_stock_ratio"] < .65:
            self.norms["water"].lam *= 1.009
        if m["energy_stock_ratio"] < .65:
            self.norms["energy"].lam *= 1.008
        if m["oxygen_stock_ratio"] < .72 or m["station_safety"] < .72:
            self.norms["space"].lam *= 1.010
        if m["avg_trust"] < .48:
            self.norms["media"].lam *= 1.006
        for mid in self.market_ids:
            ma = self.actors[mid]
            if ma.wallet.alltag < 500:
                ma.wallet.credit(4000, "reserve")
                self.created += 4000

    # Labor and production
    def labor_cycle(self) -> None:
        for p in self.people():
            if p.employer and self.rng.random() < .002 + .012 * p.stress:
                old = self.actors.get(p.employer)
                if old and p.aid in old.employees:
                    old.employees.remove(p.aid)
                p.employer = None
        self.allocate_jobs(False)

        for firm in self.firms() + self.media():
            if firm.sector not in SECTORS:
                continue
            domain, good, base_output, target, base_wage, inputs = SECTORS[firm.sector]
            for pid in list(firm.employees):
                p = self.actors.get(pid)
                if not p or not p.active or p.employer != firm.aid:
                    continue
                if self.rng.random() < .03 + .08 * p.stress + .05 * p.fatigue:
                    p.stress = clamp(p.stress + .02, 0, 1)
                    p.fatigue = clamp(p.fatigue - .05, 0, 1)
                    continue
                hours = clamp(self.rng.gauss(7.2, 1.0), 3, 10.5)
                skill = p.skill(domain)
                quality = clamp(.25 + .55 * skill + .20 * p.health - .20 * p.fatigue + self.rng.gauss(0, .08), .05, 1.25)
                reliability = clamp(.45 + .45 * p.health - .25 * p.stress + self.rng.gauss(0, .08), .05, 1.15)
                cooperation = clamp(.35 + .40 * p.reputation + .20 * p.trust + self.rng.gauss(0, .10), .05, 1.15)
                safety = clamp(.40 + .35 * skill + .20 * p.health - .25 * p.fatigue + self.rng.gauss(0, .07), .05, 1.15)
                exploitation = clamp(max(0, hours - 8.2) / 2.5 + max(0, 4.6 - base_wage) / 8.0, 0, 1)
                features = {
                    "productive_time": hours / 8, "quality": quality, "reliability": reliability, "cooperation": cooperation,
                    "safety": safety, "learning": clamp(.15 + .30 * (1 - skill) + .05 * self.rng.random(), 0, 1),
                    "fatigue": clamp(.12 + hours / 12 + p.fatigue * .35, 0, 1.5),
                    "resource_use": clamp(.15 + .30 * (1 - safety), 0, 1), "accident_risk": clamp(.08 + .45 * (1 - safety) + .12 * self.locations[p.location].risk, 0, 1.5),
                    "exploitation": exploitation, "coordination_cost": clamp(.15 + .20 * (1 - cooperation), 0, 1)
                }
                self.emit(p, "labor", "employee_work", features, note="Arbeit fuer %s" % firm.name)
                local_idx = self.markets[p.location].index(True) / 100
                wage = base_wage * (.65 + .50 * quality) * hours / 8 * clamp(local_idx, .7, 2.5)
                paid = self.transfer(firm.aid, p.aid, wage, "labor_wage", "labor", "", p.location, False, False, "Lohn")
                if paid + EPS < wage:
                    self.emit(firm, "finance", "wage_arrears",
                              {"liquidity": .05, "default_risk": clamp(1 - div(paid, wage, 0), 0, 1), "fraud": .10 * (1 - firm.integrity), "leverage": .35, "systemic_risk": .10},
                              note="Lohn teilweise nicht bezahlt")
                p.fatigue = clamp(p.fatigue + .055 * hours / 8 - .02 * p.health, 0, 1)
                p.stress = clamp(p.stress + .015 * exploitation - .006 * div(paid, wage, 0), 0, 1)
                firm.meta["labor_quality"] = firm.meta.get("labor_quality", 0.0) + quality
                firm.meta["labor_safety"] = firm.meta.get("labor_safety", 0.0) + safety
                firm.meta["labor_hours"] = firm.meta.get("labor_hours", 0.0) + hours

    def production_cycle(self) -> None:
        for firm in self.firms():
            if firm.sector not in SECTORS or firm.sector in ("media", "finance"):
                continue
            domain, good, base_output, target_emp, wage, inputs = SECTORS[firm.sector]
            market = self.markets[firm.location]
            employees = max(1, len(firm.employees))
            qsum = float(firm.meta.pop("labor_quality", 0.0))
            ssum = float(firm.meta.pop("labor_safety", 0.0))
            hsum = float(firm.meta.pop("labor_hours", 0.0))
            avg_q = clamp(qsum / employees, .05, 1.3)
            avg_s = clamp(ssum / employees, .05, 1.3)
            active = clamp(hsum / (employees * 8.0), 0, 1.2)
            if active <= .05:
                self.emit(firm, "infrastructure", "idle_capacity", {"capacity": .05, "safety": .25, "failure_risk": .20, "delay_risk": .30}, note="Ungenutzte Kapazität")
                continue
            output = base_output * active * employees * (max(10, firm.capital) / 100) ** .35 * firm.productivity * self.rng.uniform(.75, 1.25)
            input_ratio = 1.0
            for ingood, per_unit in inputs.items():
                need = output * per_unit
                delivered, _ = market.buy(self, firm.aid, ingood, need, "production_input")
                input_ratio = min(input_ratio, clamp(div(delivered, need, 1.0), 0, 1))
            output *= input_ratio
            if output <= EPS:
                continue
            features = self.production_features(firm, domain, good, output, avg_q, avg_s, input_ratio)
            self.emit(firm, domain, "produce_" + good, features, note="Produktion von %s" % good)
            quality = clamp(float(firm.meta.get("quality", .78)) * (.75 + .35 * avg_q), .10, 1.25)
            market.sell(self, firm.aid, good, output, quality, "sell_production_" + good)
            reinvest = min(firm.wallet.spendable(), output * .06 * market.price(good))
            if reinvest > 0 and self.rng.random() < .35:
                paid = self.transfer(firm.aid, market.actor_id, reinvest, "capital_reinvestment", "finance", "spares", firm.location)
                firm.capital += paid / 20.0
            firm.capital = clamp(firm.capital * (1 - (.015 + .020 * (1 - avg_s) + .010 * self.locations[firm.location].risk) * .01), 10, 500)

    def production_features(self, firm: Actor, domain: str, good: str, output: float, q: float, safety: float, input_ratio: float) -> Dict[str, float]:
        loc = self.locations[firm.location]
        features = {}
        for k, v in PLUS_FEATURES.get(domain, {}).items():
            features[k] = clamp(v * (.55 + .55 * q) * (.75 + .25 * input_ratio), 0, 2)
        for k, v in MINUS_FEATURES.get(domain, {}).items():
            features[k] = clamp(v * (1.20 - .45 * safety) * (1.15 - .25 * firm.integrity), 0, 2)
        if good in self.markets[firm.location].goods:
            g = self.markets[firm.location].goods[good]
            scarcity_relief = clamp(1 - div(g.stock, g.target, 1), 0, 1.5)
            if domain in ("food", "energy"):
                features["scarcity_relief"] = scarcity_relief
            if domain == "water":
                features["supply_security"] = max(features.get("supply_security", 0), .4 + scarcity_relief)
        if domain == "space":
            features["station_safety"] = max(features.get("station_safety", 0), safety * loc.infrastructure)
            features["debris_risk"] = max(features.get("debris_risk", 0), loc.debris_risk * .7)
            features["oxygen_loss"] = max(features.get("oxygen_loss", 0), max(0, .75 - loc.oxygen_safety))
        if domain == "infrastructure":
            features["resilience"] = max(features.get("resilience", 0), loc.infrastructure * .5)
            features["failure_risk"] = max(features.get("failure_risk", 0), max(0, .8 - loc.infrastructure))
        return features

    # Space, station, satellites
    def space_cycle(self) -> None:
        for infra in self.infrastructure():
            loc = self.locations[infra.location]
            safety = float(infra.meta.get("safety", loc.infrastructure))
            backlog = float(infra.meta.get("backlog", .1))
            safety = clamp(safety - .004 * loc.risk - .010 * backlog + self.rng.gauss(0, .003), .05, 1.2)
            backlog = clamp(backlog + .006 * loc.risk + self.rng.uniform(0, .006), 0, 1)
            if safety < .78 or backlog > .22 or self.rng.random() < .10:
                providers = [f for f in self.firms() if f.location == infra.location and f.sector in ("space_ops", "construction", "data_network", "energy")]
                if not providers:
                    providers = [f for f in self.firms() if f.sector in ("space_ops", "construction", "data_network")]
                if providers:
                    provider = max(providers, key=lambda f: f.skill("space") + f.reputation + .0001 * f.wallet.spendable())
                    budget = 80 * loc.risk * (1 + backlog)
                    self.transfer(self.gov, provider.aid, budget, "public_infrastructure_contract", "infrastructure", "", infra.location)
                    quality = clamp(.25 + .55 * provider.skill("space") + .20 * provider.reputation + self.rng.gauss(0, .08), .05, 1.2)
                    if infra.location in ("Moon", "Orbit", "Station"):
                        features = {
                            "oxygen_recycling": quality * (.75 if infra.location != "Orbit" else .45),
                            "station_safety": quality, "orbit_stability": quality * (.8 if infra.location in ("Orbit", "Station") else .35),
                            "life_support": quality * (.9 if infra.location in ("Station", "Moon") else .35),
                            "logistics_reliability": quality * .65, "debris_removal": quality * (.45 if infra.location in ("Orbit", "Station") else .05),
                            "delta_v_cost": .20 * loc.risk, "debris_risk": loc.debris_risk * .5,
                            "radiation_risk": .18 * loc.risk, "mission_failure_risk": max(0, .8 - quality)
                        }
                        self.emit(provider, "space", "critical_maintenance", features, note="Wartung an " + infra.name, location=infra.location)
                    else:
                        features = {"maintenance": quality, "safety": quality, "resilience": quality * .75, "capacity": quality * .45,
                                    "fault_detection": quality * .55, "material_use": .18 * loc.risk, "energy_loss": .12,
                                    "failure_risk": max(0, .8 - quality)}
                        self.emit(provider, "infrastructure", "critical_maintenance", features, note="Wartung an " + infra.name, location=infra.location)
                    safety = clamp(safety + .10 * quality, .05, 1.2)
                    backlog = clamp(backlog - .18 * quality, 0, 1)
            infra.meta["safety"] = safety
            infra.meta["backlog"] = backlog
            infra.health = safety
            loc.infrastructure = clamp(.8 * loc.infrastructure + .2 * safety, .05, 1.25)
            if infra.location in ("Orbit", "Station"):
                loc.debris_risk = clamp(loc.debris_risk + .002 * backlog - .006 * (1 - backlog), 0, 1)
                loc.oxygen_safety = clamp(loc.oxygen_safety + .004 * (safety - .7), .05, 1.2)

    # Media and news
    def media_cycle(self) -> None:
        self.last_reports = []
        outlets = self.media() + [f for f in self.firms() if f.sector == "media"]
        if not outlets:
            return
        weighted_topics = [(t, .25 + t.relevance + .5 * t.emotion) for t in self.topics]
        for outlet in outlets:
            t = weighted_choice(self.rng, weighted_topics)
            integ, pressure, skill = outlet.integrity, outlet.pressure, outlet.skill("media")
            source = clamp(.25 + .45 * skill + .35 * integ - .15 * pressure + self.rng.gauss(0, .10), 0, 1.2)
            truth = clamp(t.factuality * (.50 + .35 * integ + .25 * source) + self.rng.gauss(0, .08), 0, 1.2)
            relevance = clamp(t.relevance * (.65 + .20 * skill) + self.rng.gauss(0, .05), 0, 1.2)
            context = clamp(.20 + .45 * skill + .30 * integ - .25 * pressure + self.rng.gauss(0, .08), 0, 1.2)
            sensational = clamp(.10 + .65 * pressure + .45 * t.emotion - .35 * integ + self.rng.gauss(0, .10), 0, 1.3)
            misinformation = clamp((1 - truth) * .75 + (1 - source) * .40 + (.45 if t.rumor else 0), 0, 1.5)
            manipulation = clamp(.10 + .55 * sensational + .25 * (1 - integ) - .30 * context, 0, 1.5)
            panic = clamp(t.urgency * t.emotion * (.35 + .65 * sensational) - .25 * context, 0, 1.5)
            attention = clamp(.20 + .80 * sensational + .25 * outlet.meta.get("audience", .05), 0, 1.7)
            correction = 0.0
            if self.rng.random() < outlet.meta.get("correction_policy", .5) * max(0, .8 - truth):
                correction = clamp(.35 + .45 * integ + self.rng.random() * .2, 0, 1.2)
                truth = clamp(truth + .20 * correction, 0, 1.2)
                misinformation = clamp(misinformation - .35 * correction, 0, 1.5)
                manipulation = clamp(manipulation - .15 * correction, 0, 1.5)
            features = {"truth": truth, "source_quality": source, "public_relevance": relevance, "correction": correction,
                        "public_safety": clamp(t.safety_value * truth, 0, 1.2), "plurality": clamp(.40 + .30 * (1 - outlet.meta.get("audience", .1)), 0, 1),
                        "context": context, "manipulation": manipulation, "panic": panic, "attention_drain": attention,
                        "privacy_violation": clamp(.05 + .20 * sensational - .10 * integ, 0, 1), "misinformation_risk": misinformation,
                        "monopoly_power": clamp(outlet.meta.get("audience", .08) * 1.4, 0, 1)}
            self.emit(outlet, "media", "publish_news", features, verified=(source > .35 or not t.rumor), note="Thema: " + t.title)
            reach = clamp(.02 + .20 * outlet.reputation + .22 * sensational + .10 * relevance + .08 * truth, .01, .55)
            if self.scenario == "media_crisis":
                reach = clamp(reach + .08 * sensational, .01, .65)
            outlet.meta["audience"] = clamp(.80 * outlet.meta.get("audience", .08) + .20 * reach, .005, .75)
            outlet.meta["last_truth"] = truth
            outlet.meta["last_manipulation"] = manipulation
            outlet.meta["last_attention"] = attention
            outlet.meta["last_topic"] = t.title
            ad_revenue = max(1, int(reach * len(self.people()))) * (.05 + .18 * sensational + .07 * relevance)
            market_id = self.markets.get(outlet.location, self.markets["Earth"]).actor_id
            self.transfer(market_id, outlet.aid, ad_revenue, "attention_market_revenue", "media", "media", outlet.location, debt=True)
            if truth > .72 and relevance > .55 and manipulation < .35:
                self.transfer(self.gov, outlet.aid, 10 * (truth + relevance + t.safety_value), "news_fund_quality_payment", "media", "media", outlet.location)
            self.last_reports.append({"outlet": outlet.aid, "name": outlet.name, "topic": t.title, "truth": truth, "source": source,
                                      "relevance": relevance, "manipulation": manipulation, "panic": panic, "attention": attention, "reach": reach})
        weighted_reports = [(r, .05 + r["reach"] + .20 * r["relevance"] + .05 * r["truth"]) for r in self.last_reports]
        for p in self.people():
            if self.rng.random() > clamp(.35 + .30 * p.trust + .20 * p.media_literacy, .10, .95):
                continue
            r = weighted_choice(self.rng, weighted_reports)
            outlet = self.actors[r["outlet"]]
            self.transfer(p.aid, outlet.aid, .05 + .09 * r["attention"], "news_subscription_or_attention", "media", "media", p.location)
            awareness = clamp(r["truth"] * r["relevance"] * (.5 + .5 * p.media_literacy), 0, 1.2)
            features = {"truth": r["truth"] * p.media_literacy, "source_quality": r["source"] * p.media_literacy,
                        "public_relevance": r["relevance"], "public_safety": awareness * .5, "context": awareness,
                        "plurality": .25 + .25 * p.media_literacy, "attention_drain": r["attention"] * (1.1 - .5 * p.media_literacy),
                        "panic": r["panic"] * (1 - .35 * p.media_literacy), "misinformation_risk": max(0, 1 - r["truth"]) * (1 - .45 * p.media_literacy),
                        "manipulation": r["manipulation"] * (1 - .35 * p.media_literacy)}
            self.emit(p, "media", "consume_news", features, note="Konsumiert: " + r["topic"])
            p.trust = clamp(p.trust + .018 * (r["truth"] - r["manipulation"]) - .010 * r["panic"], .02, 1)
            p.stress = clamp(p.stress + .018 * r["panic"] + .010 * r["attention"] - .006 * awareness, 0, 1)

    # Consumption, food, water, energy
    def consumption_cycle(self) -> None:
        for p in self.people():
            market = self.markets[p.location]
            loc = self.locations[p.location]
            food_need = clamp(self.rng.gauss(1.0, .08), .7, 1.35)
            water_need = clamp(self.rng.gauss(1.1, .12), .75, 1.6)
            energy_need = clamp(self.rng.gauss(.65, .12), .35, 1.10)
            housing_need = .11
            oxygen_need = clamp(self.rng.gauss(1.0, .05), .8, 1.25) if loc.kind in ("moon", "orbit", "station") else 0.0
            food, _ = market.buy(self, p.aid, "food", food_need, "basic_food_purchase", True)
            water, _ = market.buy(self, p.aid, "water", water_need, "basic_water_purchase", True)
            energy, _ = market.buy(self, p.aid, "energy", energy_need, "basic_energy_purchase", True)
            housing, _ = market.buy(self, p.aid, "housing", housing_need, "housing_service", True)
            oxygen = oxygen_need
            if oxygen_need > 0:
                oxygen, _ = market.buy(self, p.aid, "oxygen", oxygen_need, "oxygen_life_support", True)
            fr, wr, er = div(food, food_need, 0), div(water, water_need, 0), div(energy, energy_need, 0)
            hr = div(housing, housing_need, 0)
            oxr = div(oxygen, oxygen_need, 1) if oxygen_need > 0 else 1
            waste = clamp(.08 + .18 * self.rng.random() + .15 * max(0, food - food_need), 0, 1)
            self.emit(p, "food", "eat_food", {"nutrition": fr, "health_gain": .55 * fr + .25 * wr, "cultural_value": self.rng.uniform(.05, .45),
                    "water_use": .05 * loc.scarce("water"), "energy_use": .04 * loc.scarce("energy"), "waste": waste,
                    "health_risk": .65 * max(0, .75 - fr) + .55 * max(0, .75 - wr),
                    "scarcity_use": clamp(.20 * loc.scarce("food") * food_need, 0, 1.5)}, note="Nahrung als Verhalten")
            self.emit(p, "water", "use_water", {"clean_water": wr, "health_gain": .65 * wr, "recycling": .20 + .45 * p.integrity + .20 * loc.water_security,
                    "waste": max(0, water - water_need) + .05 * self.rng.random(), "scarcity_use": .12 * loc.scarce("water") * water_need,
                    "energy_use": .03 * loc.scarce("energy"), "contamination": .45 * max(0, .70 - wr)}, note="Wasserverbrauch")
            self.emit(p, "energy", "use_energy", {"energy_output": .25 * er, "reliability": er, "storage": .15 + .20 * p.integrity,
                    "renewable_share": .35 if p.location == "Earth" else .55, "emissions": .18 * loc.scarce("energy"),
                    "waste_heat": max(0, energy - energy_need) * .25, "resource_depletion": .10 * loc.scarce("energy"),
                    "hazard": .30 * max(0, .65 - er)}, note="Energieverbrauch")
            if oxygen_need > 0:
                self.emit(p, "space", "life_support_consumption", {"life_support": oxr, "oxygen_recycling": .35 + .35 * loc.oxygen_safety + .20 * p.integrity,
                        "station_safety": loc.infrastructure, "logistics_reliability": oxr * .55,
                        "oxygen_loss": .30 * max(0, 1 - oxr) + .10 * loc.scarce("oxygen"),
                        "mission_failure_risk": .45 * max(0, .7 - oxr), "radiation_risk": .08 * loc.risk, "delta_v_cost": .04 * loc.risk},
                        note="Sauerstoff/Life-Support")
            p.health = clamp(p.health + .015 * min(fr, wr, oxr) - .030 * max(0, .70 - fr) - .045 * max(0, .70 - wr) - .035 * max(0, .75 - oxr), .02, 1.05)
            p.stress = clamp(p.stress + .04 * max(0, .85 - min(fr, wr, oxr)) - .006 * hr, 0, 1)
            p.fatigue = clamp(p.fatigue - .08 * min(1, er) + .02 * p.stress, 0, 1)
            if self.rng.random() < clamp(.35 + .35 * p.wallet.spendable() / 300 - .25 * p.stress, .05, .85):
                good = weighted_choice(self.rng, [("consumer_goods", .45), ("transport", .22), ("data_bandwidth", .18), ("spares", .10), ("media", .05)])
                qty = self.rng.uniform(.05, .50)
                got, _ = market.buy(self, p.aid, good, qty, "general_consumption")
                if got > 0:
                    self.emit(p, "consumption", "general_consumption", {"utility": .35 + got, "need_satisfaction": .25 + .7 * got,
                            "repairability": .30 if good in ("spares", "consumer_goods") else .10, "shared_use": .20 + .30 * p.trust,
                            "cultural_value": .25 if good in ("media", "data_bandwidth") else .10,
                            "waste": .10 + .20 * self.rng.random() - .10 * p.integrity,
                            "overconsumption": max(0, p.wallet.spendable() / 700 - .25),
                            "resource_use": .10 + .20 * got * loc.scarce(good),
                            "addiction_risk": .25 if good in ("media", "data_bandwidth") else .05,
                            "attention_drain": .25 if good in ("media", "data_bandwidth") else .02}, note="Konsum von " + good)
            if p.fatigue > .45 or self.rng.random() < .18:
                rest = clamp(.35 + .45 * hr + .25 * (1 - p.stress) + self.rng.gauss(0, .08), 0, 1.2)
                self.emit(p, "health", "rest_and_recovery", {"health_gain": .35 * rest, "prevention": .45 * rest, "empathy": .10,
                        "care_access": .20 * hr, "resource_use": .08 * loc.scarce("energy"), "burnout": max(0, p.fatigue - rest), "infection_risk": .02},
                        note="Erholung als Verhalten")
                p.fatigue = clamp(p.fatigue - .18 * rest, 0, 1)
                p.health = clamp(p.health + .012 * rest, .02, 1.05)

    def education_health_culture_cycle(self) -> None:
        for p in self.people():
            market = self.markets[p.location]
            if p.health < .62 or self.rng.random() < .035:
                need = self.rng.uniform(.12, .45)
                got, _ = market.buy(self, p.aid, "healthcare", need, "healthcare_service", True)
                if got > 0:
                    q = clamp(div(got, need, 0), 0, 1.2)
                    self.emit(p, "health", "receive_healthcare", {"health_gain": .70 * q, "prevention": .35 * q, "empathy": .25,
                            "triage_quality": .35 * q, "care_access": q, "resource_use": .14 * need, "infection_risk": .06 * (1 - q), "privacy_violation": .02},
                            note="Gesundheitsdienst")
                    p.health = clamp(p.health + .10 * q, .02, 1.05)
                    p.stress = clamp(p.stress - .04 * q, 0, 1)
            if self.rng.random() < clamp(.025 + .09 * p.meta.get("education", .5) + .05 * (1 - p.fatigue), .01, .22):
                need = self.rng.uniform(.08, .35)
                got, _ = market.buy(self, p.aid, "education", need, "education_service", True)
                if got > 0:
                    gain = clamp(got * (.5 + .7 * p.media_literacy), 0, 1)
                    self.emit(p, "education", "learn_skill", {"knowledge_gain": .65 * gain, "skill_gain": .75 * gain,
                            "critical_thinking": .55 * gain, "social_mobility": .45 * gain, "reproducibility": .25 * gain,
                            "misinformation_risk": .05 * (1 - p.media_literacy), "energy_use": .06, "burnout": .05 * p.fatigue},
                            note="Bildung")
                    d = weighted_choice(self.rng, [(x, 1.0) for x in list(self.norms.keys())])
                    p.skills[d] = clamp(p.skills.get(d, p.skill("general")) + .010 * gain, 0, 1.35)
                    p.media_literacy = clamp(p.media_literacy + .006 * gain, .02, 1)
            if self.rng.random() < .05:
                cohesion = clamp(.30 + .45 * p.trust + self.rng.gauss(0, .10), 0, 1.2)
                self.emit(p, "culture", "community_culture", {"cohesion": cohesion, "meaning": .25 + .45 * (1 - p.stress),
                        "inclusion": .30 + .45 * p.reputation, "creativity": self.rng.uniform(.05, .65),
                        "conflict_reduction": .25 * p.trust, "attention_drain": .12, "resource_use": .05,
                        "addiction_risk": .04, "exclusion": max(0, .35 - p.trust)}, note="Kultur/Soziales")
                p.trust = clamp(p.trust + .012 * cohesion, .02, 1)
                p.stress = clamp(p.stress - .016 * cohesion, 0, 1)

    def finance_cycle(self) -> None:
        bank = self.actors[self.bank]
        insurer = self.actors[self.insurer]
        for firm in self.firms():
            if firm.aid in (self.bank, self.insurer):
                continue
            if firm.wallet.spendable() < 500 and self.rng.random() < .25:
                principal = self.rng.uniform(800, 3500)
                paid = self.transfer(bank.aid, firm.aid, principal, "firm_credit_disbursement", "finance", "", firm.location, debt=True)
                if paid > 0:
                    firm.meta.setdefault("loans", []).append({"principal": paid, "rate": self.rng.uniform(.00022, .00075), "lender": bank.aid})
                    self.emit(bank, "finance", "provide_credit", {"liquidity": .65, "risk_sharing": .55, "investment": .45, "solvency_support": .60,
                            "price_discovery": .30, "default_risk": .30 + .50 * (1 - firm.reputation), "leverage": paid / 6000, "systemic_risk": .10},
                            note="Kredit an " + firm.name)
            loans = []
            for loan in firm.meta.get("loans", []):
                principal = float(loan.get("principal", 0))
                if principal <= 1:
                    continue
                due = principal * float(loan.get("rate", .0004)) + min(principal * .002, max(0, firm.wallet.spendable() - 250) * .04)
                paid = self.transfer(firm.aid, loan.get("lender", self.bank), due, "loan_service", "finance", "", firm.location)
                if paid + EPS < due:
                    self.emit(firm, "finance", "credit_stress", {"liquidity": .05, "risk_sharing": .05, "default_risk": 1 - div(paid, due, 0),
                            "fraud": .05 * (1 - firm.integrity), "leverage": principal / 6000, "systemic_risk": .12}, note="Kreditstress")
                principal = max(0, principal - max(0, paid - principal * loan.get("rate", .0004)))
                if principal > 1:
                    loan["principal"] = principal
                    loans.append(loan)
            firm.meta["loans"] = loans
            loc = self.locations[firm.location]
            if firm.sector in ("space_ops", "energy", "water_utility", "healthcare") or loc.risk > 1.1:
                self.transfer(firm.aid, insurer.aid, 1.5 * loc.risk * (1 + .5 * (1 - firm.reputation)),
                              "insurance_premium", "finance", "", firm.location)
        for infra in self.infrastructure():
            loc = self.locations[infra.location]
            if self.rng.random() < .002 + .012 * max(0, .75 - infra.health) + .008 * loc.debris_risk:
                claim = self.rng.uniform(500, 2500) * loc.risk
                self.transfer(insurer.aid, infra.aid, claim, "insurance_claim", "finance", "", infra.location, debt=True)
                self.emit(insurer, "finance", "pay_claim", {"liquidity": .30, "risk_sharing": .90, "solvency_support": .70,
                        "investment": .10, "default_risk": .10, "leverage": .20, "systemic_risk": .10}, note="Versicherungsleistung")
                infra.health = clamp(infra.health - self.rng.uniform(.02, .10), .02, 1.1)

    def governance_cycle(self) -> None:
        gov = self.actors[self.gov]
        if self.day % 3 == 0:
            self.emit(gov, "governance", "rights_and_norm_transparency",
                      {"transparency": .55 + .20 * gov.integrity, "appeal_access": .55 + .15 * div(self.appeals_granted + 1, self.disputed + 1, 1),
                       "participation": self.rng.uniform(.25, .75), "conflict_resolution": self.rng.uniform(.30, .80),
                       "audit_quality": self.rng.uniform(.35, .85), "rights_protection": .65 + .20 * gov.integrity,
                       "bureaucracy": self.rng.uniform(.10, .45), "coercion": .02, "corruption_risk": .10 * (1 - gov.integrity),
                       "surveillance": .08, "delay_risk": self.rng.uniform(.05, .30)}, note="Rechtekammer, Normenkammer, Orakelkammer")
        candidates = self.firms() + self.media()
        n = max(1, int(.035 * len(candidates)))
        for actor in self.rng.sample(candidates, min(n, len(candidates))):
            fraud = float(actor.meta.get("fraud_risk", .05))
            manip = float(actor.meta.get("last_manipulation", 0.0)) if actor.kind == "media" else 0.0
            q = self.rng.uniform(.45, .95)
            self.emit(gov, "governance", "audit", {"transparency": .35 + .35 * q, "audit_quality": q, "rights_protection": .45 + .20 * q,
                    "appeal_access": .55, "conflict_resolution": .35, "participation": .20, "bureaucracy": .20 + .25 * q,
                    "coercion": .04, "corruption_risk": .05, "surveillance": .10, "delay_risk": .10}, note="Audit von " + actor.name)
            if self.rng.random() < .08 + .35 * fraud + .18 * manip:
                if actor.kind == "media":
                    self.emit(actor, "media", "audit_detected_manipulation",
                              {"truth": .05, "source_quality": .05, "public_relevance": .10, "context": .05,
                               "manipulation": .65 + manip, "misinformation_risk": .55 + manip,
                               "panic": float(actor.meta.get("last_attention", .3)) * .3, "attention_drain": float(actor.meta.get("last_attention", .3)),
                               "privacy_violation": .12, "monopoly_power": float(actor.meta.get("audience", .1))},
                              note="Audit findet Manipulation/fehlende Quellen")
                else:
                    self.emit(actor, "finance", "audit_detected_gaming",
                              {"liquidity": .05, "fraud": .55 + fraud, "default_risk": .35, "leverage": .25, "systemic_risk": .18},
                              note="Audit findet Norm-Gaming/Scheinverhalten")
                actor.reputation = clamp(actor.reputation - .06 * q, 0, 1)

    def logistics_balance(self) -> None:
        for good in ("food", "water", "energy", "spares", "oxygen", "data_bandwidth", "raw_materials"):
            ratios = sorted((div(m.goods[good].stock, m.goods[good].target, 0), loc) for loc, m in self.markets.items())
            low, lowloc = ratios[0]
            high, highloc = ratios[-1]
            if low < .55 and high > 1.10 and lowloc != highloc:
                src, dst = self.markets[highloc], self.markets[lowloc]
                qty = min(src.goods[good].stock - src.goods[good].target * .90, dst.goods[good].target * (.75 - low), .05 * dst.goods[good].target)
                if qty <= 0:
                    continue
                dist = 1.0 + (.8 if (lowloc in ("Moon", "Orbit", "Station") or highloc in ("Moon", "Orbit", "Station")) else 0) + (.4 if "Earth" not in (lowloc, highloc) else 0)
                loss = clamp(.02 * dist + .03 * self.locations[lowloc].risk, 0, .22)
                src.goods[good].stock -= qty
                dst.goods[good].stock += qty * (1 - loss)
                self.emit(self.actors[self.gov], "transport", "cross_location_supply_balancing",
                          {"delivery_value": .6 + (.75 - low), "supply_chain_security": .6 + (high - low) * .4,
                           "access": .45, "time_saved": .25, "orbit_stability": .2 if lowloc in ("Orbit", "Station") or highloc in ("Orbit", "Station") else 0,
                           "fuel_use": .18 * dist, "accident_risk": .08 * dist, "emissions": .10 * dist,
                           "orbital_debris": .06 * dist if lowloc in ("Orbit", "Station") or highloc in ("Orbit", "Station") else 0, "congestion": .05},
                          note="Logistik: %s von %s nach %s" % (good, highloc, lowloc), location=lowloc)

    # Metrics and output
    def price_index(self) -> float:
        pops = Counter(p.location for p in self.people())
        total = max(1, sum(pops.values()))
        return sum((pops.get(loc, 0) / total or .02) * market.index(False) for loc, market in self.markets.items())

    def stock_ratio(self, good: str) -> float:
        return div(sum(m.goods[good].stock for m in self.markets.values()), sum(m.goods[good].target for m in self.markets.values()), 1)

    def collect_metrics(self) -> None:
        people = self.people()
        actors = list(self.actors.values())
        today_events = [e for e in self.events if e.day == self.day]
        today_txs = [t for t in self.transactions if t.day == self.day]
        reports = self.last_reports
        station_safety = avg([self.locations["Station"].infrastructure, self.locations["Station"].oxygen_safety], 1)
        m = {
            "day": self.day,
            "price_index": self.price_index(),
            "basic_price_index": avg([m.index(True) for m in self.markets.values()], 100),
            "broad_money": sum(a.wallet.positive() for a in actors),
            "net_money": sum(a.wallet.total() for a in actors),
            "total_liability": -sum(min(0, a.wallet.haftung) for a in actors),
            "created_today": sum(max(0, e.gross_delta) for e in today_events),
            "destroyed_today": sum(e.destroyed for e in today_events),
            "liability_today": sum(e.liability for e in today_events),
            "events_today": len(today_events),
            "tx_volume_today": sum(t.amount for t in today_txs),
            "unemployment": div(len([p for p in people if not p.employer]), len(people), 0),
            "avg_health": avg([p.health for p in people], 0),
            "avg_stress": avg([p.stress for p in people], 0),
            "avg_trust": avg([p.trust for p in people], 0),
            "avg_reputation": avg([p.reputation for p in people], 0),
            "gini_positive_money": gini([p.wallet.positive() for p in people]),
            "food_stock_ratio": self.stock_ratio("food"),
            "water_stock_ratio": self.stock_ratio("water"),
            "energy_stock_ratio": self.stock_ratio("energy"),
            "oxygen_stock_ratio": self.stock_ratio("oxygen"),
            "spares_stock_ratio": self.stock_ratio("spares"),
            "media_truth_index": avg([r["truth"] for r in reports], .65),
            "media_manipulation_index": avg([r["manipulation"] for r in reports], .25),
            "station_safety": station_safety,
            "orbit_debris_risk": avg([self.locations["Orbit"].debris_risk, self.locations["Station"].debris_risk], 0),
            "appeals_granted_total": self.appeals_granted,
            "events_disputed_total": self.disputed,
            "lambda_food": self.norms["food"].lam,
            "lambda_media": self.norms["media"].lam,
            "lambda_space": self.norms["space"].lam,
        }
        self.metrics.append(m)
        for p in people:
            p.stress = clamp(.995 * p.stress + .005 * (1 - p.trust), 0, 1)
            p.fatigue = clamp(p.fatigue - .030 * p.health, 0, 1)
            if p.health < .08 and self.rng.random() < .004:
                p.active = False
                if p.employer and p.employer in self.actors and p.aid in self.actors[p.employer].employees:
                    self.actors[p.employer].employees.remove(p.aid)

    def write_outputs(self, runtime: float) -> None:
        mkdir(self.out)
        self.write_csv("daily_metrics.csv", self.metrics)
        self.write_csv("events.csv", [e.row() for e in self.events])
        self.write_csv("transactions.csv", [t.row() for t in self.transactions])
        self.write_csv("actors.csv", [a.row() for a in self.actors.values()])
        with open(os.path.join(self.out, "final_state.json"), "w", encoding="utf-8") as fh:
            json.dump(self.final_state(runtime), fh, ensure_ascii=False, indent=2, sort_keys=True)
        self.write_report(runtime)
        self.write_utf8_dashboard(runtime)

    def write_csv(self, filename: str, rows: List[Dict[str, Any]]) -> None:
        path = os.path.join(self.out, filename)
        if not rows:
            open(path, "w", encoding="utf-8").close()
            return
        fields = list(rows[0].keys())
        seen = set(fields)
        for r in rows:
            for k in r:
                if k not in seen:
                    seen.add(k)
                    fields.append(k)
        with open(path, "w", encoding="utf-8", newline="") as fh:
            w = csv.DictWriter(fh, fieldnames=fields)
            w.writeheader()
            for r in rows:
                w.writerow(r)

    def final_state(self, runtime: float) -> Dict[str, Any]:
        dd = defaultdict(float)
        dc = Counter()
        for e in self.events:
            dd[e.domain] += e.gross_delta
            dc[e.domain] += 1
        return {
            "version": VERSION, "days": self.days, "persons_requested": self.person_count, "seed": self.seed,
            "scenario": self.scenario, "runtime_seconds": runtime, "last_metrics": self.metrics[-1] if self.metrics else {},
            "zemo": {"created_total": self.created, "destroyed_total": self.destroyed,
                     "liability_created_total": self.liability_created, "tax_rate": self.tax_rate,
                     "transaction_tax": self.transaction_tax, "appeals_granted": self.appeals_granted,
                     "events_disputed": self.disputed, "lambdas": {k: v.lam for k, v in self.norms.items()}},
            "counts": {"actors": len(self.actors), "persons_active": len(self.people()), "firms": len(self.firms()),
                       "media_outlets": len(self.media()), "events": len(self.events), "transactions": len(self.transactions)},
            "gross_delta_by_domain": dict(dd), "events_by_domain": dict(dc),
            "top_balances": [{"name": a.name, "kind": a.kind, "location": a.location, "money": a.wallet.positive()}
                             for a in sorted(self.actors.values(), key=lambda x: x.wallet.positive(), reverse=True)[:15]]
        }

    def write_report(self, runtime: float) -> None:
        first = self.metrics[0] if self.metrics else {}
        last = self.metrics[-1] if self.metrics else {}
        dd = defaultdict(float)
        dc = Counter()
        ac = Counter()
        for e in self.events:
            dd[e.domain] += e.gross_delta
            dc[e.domain] += 1
            ac[(e.domain, e.action)] += 1
        top_money = sorted([a for a in self.actors.values() if a.kind != "market"], key=lambda a: a.wallet.positive(), reverse=True)[:12]
        low_people = sorted(self.people(), key=lambda a: a.wallet.total())[:10]
        with open(os.path.join(self.out, "report.md"), "w", encoding="utf-8") as f:
            f.write("# Delta-Norm-Wirtschaftssimulation – Bericht\n\n")
            f.write("**Version:** %s  \n**Tage:** %d  \n**Personen:** %d  \n**Seed:** %d  \n**Szenario:** %s  \n**Laufzeit:** %s Sekunden  \n\n" %
                    (VERSION, self.days, self.person_count, self.seed, self.scenario, f2(runtime)))
            f.write("## Mathematischer Kern\n\n")
            f.write("```text\nmu(e) = lambda_d * ( ||Phi_d(e)||_+ - ||Phi_d(e)||_- )\n```\n\n")
            f.write("Jedes Verhalten wird als Vektor abgebildet. Die Plusnorm misst Beitrag; die Minusnorm misst Belastung. Die Differenz ist Delta-Geld.\n\n")
            if self.notes:
                f.write("## Szenario\n\n")
                for n in self.notes:
                    f.write("- %s\n" % n)
                f.write("\n")
            f.write("## Schlusskennzahlen\n\n| Kennzahl | Start | Ende |\n|---|---:|---:|\n")
            for key, label in [("price_index", "Preisindex"), ("basic_price_index", "Grundversorgungspreisindex"),
                               ("broad_money", "Positive Geldmenge"), ("net_money", "Netto-Geld inkl. Haftung"),
                               ("total_liability", "Haftung"), ("unemployment", "Arbeitslosigkeit"),
                               ("avg_health", "Gesundheit"), ("avg_stress", "Stress"), ("avg_trust", "Vertrauen"),
                               ("gini_positive_money", "Gini positive Geldbestände"), ("media_truth_index", "Medien-Wahrheit"),
                               ("media_manipulation_index", "Medien-Manipulation"), ("station_safety", "Stationssicherheit"),
                               ("orbit_debris_risk", "Orbit-Trümmerrisiko")]:
                a, b = first.get(key, 0), last.get(key, 0)
                if key == "unemployment":
                    f.write("| %s | %s%% | %s%% |\n" % (label, f2(100 * a), f2(100 * b)))
                else:
                    f.write("| %s | %s | %s |\n" % (label, f3(a), f3(b)))
            f.write("\n## Geldschöpfung und Haftung\n\n")
            f.write("- Geschaffenes Delta: **%s D**\n- Vernichtetes Delta: **%s D**\n- Neu gebuchte Haftung: **%s D**\n- Bestrittene Ereignisse: **%d**, erfolgreiche Einsprüche: **%d**\n\n" %
                    (f2(self.created), f2(self.destroyed), f2(self.liability_created), self.disputed, self.appeals_granted))
            f.write("## Delta nach Domänen\n\n| Domäne | Ereignisse | Brutto-Delta |\n|---|---:|---:|\n")
            for domain, delta in sorted(dd.items(), key=lambda kv: kv[1], reverse=True):
                f.write("| %s | %d | %s |\n" % (domain, dc[domain], f2(delta)))
            f.write("\n## Häufigste Handlungen\n\n| Domäne | Handlung | Anzahl |\n|---|---|---:|\n")
            for (domain, action), count in ac.most_common(14):
                f.write("| %s | `%s` | %d |\n" % (domain, action, count))
            f.write("\n## Wohlhabendste Nicht-Markt-Akteure\n\n| Akteur | Art | Ort | Positives Geld | Haftung |\n|---|---|---|---:|---:|\n")
            for a in top_money:
                f.write("| %s | %s | %s | %s | %s |\n" % (a.name, a.kind, a.location, f2(a.wallet.positive()), f2(a.wallet.haftung)))
            f.write("\n## Verletzliche Personen nach Netto-Konto\n\n| Person | Ort | Netto | Gesundheit | Stress | Beschäftigt |\n|---|---|---:|---:|---:|---|\n")
            for a in low_people:
                f.write("| %s | %s | %s | %s | %s | %s |\n" % (a.name, a.location, f2(a.wallet.total()), f3(a.health), f3(a.stress), "ja" if a.employer else "nein"))
            f.write("\n## ZEMO-Lambda-Faktoren\n\n| Domäne | Lambda |\n|---|---:|\n")
            for k, v in sorted(self.norms.items()):
                f.write("| %s | %s |\n" % (k, f3(v.lam)))
            f.write("\n## English Summary\n\n")
            f.write("This run models an Earth-Moon-Orbit Delta-Norm economy. Money is created from the spread between a contribution norm and a burden norm. Agents work, eat, consume, publish and consume news, maintain satellites and stations, pay wages, take loans, buy insurance, and receive protected basic access. The model exports CSV ledgers and a final JSON state for further analysis.\n")


    def build_utf8_dashboard(self, runtime: float, color: bool = False) -> str:
        lines = []
        metrics = self.metrics
        if not metrics:
            return "Keine Metriken vorhanden."

        def add(title: str, explanation: str, art_lines: List[str], evaluation: str) -> None:
            lines.append(rainbow("═" * 94, color))
            lines.append(ansi_bold(title, color))
            lines.append(rainbow("─" * 94, color))
            lines.append(ansi("Erklärung:", 33, color))
            for row in wrap_text(explanation, 96, "  "):
                lines.append(row)
            lines.append(ansi("Grafik:", 36, color))
            for row in art_lines:
                lines.append("  " + row)
            lines.append(ansi("Auswertung:", 35, color))
            for row in wrap_text(evaluation, 96, "  "):
                lines.append(row)
            lines.append("")

        last = metrics[-1]
        first = metrics[0]
        actors = list(self.actors.values())
        people = self.people()
        firms = self.firms()
        events_by_domain = defaultdict(float)
        event_count_by_domain = Counter()
        action_counts = Counter()
        for e in self.events:
            events_by_domain[e.domain] += e.gross_delta
            event_count_by_domain[e.domain] += 1
            action_counts[(e.domain, e.action)] += 1
        location_people = Counter(p.location for p in people)
        location_positive_money = defaultdict(float)
        location_net_money = defaultdict(float)
        location_unemployed = Counter()
        for p in people:
            location_positive_money[p.location] += p.wallet.positive()
            location_net_money[p.location] += p.wallet.total()
            if not p.employer:
                location_unemployed[p.location] += 1
        sector_employment = Counter()
        sector_firms = Counter()
        for f in firms:
            sector_firms[f.sector] += 1
            sector_employment[f.sector] += len(f.employees)
        topic_categories = Counter()
        rumor_topics = 0
        for t in self.topic_history:
            topic_categories[t['category']] += 1
            if t['rumor']:
                rumor_topics += 1
        outstanding_loans = 0.0
        loan_count = 0
        for a in firms:
            for loan in a.meta.get('loans', []):
                outstanding_loans += float(loan.get('principal', 0.0))
                loan_count += 1
        pop_total = max(1, len(people))
        max_loc_pop = max(location_people.values()) if location_people else 1
        max_loc_money = max(location_positive_money.values()) if location_positive_money else 1.0
        max_sector_emp = max(sector_employment.values()) if sector_employment else 1
        max_action = max(action_counts.values()) if action_counts else 1
        max_domain_abs = max([abs(v) for v in events_by_domain.values()] or [1.0])

        header = [
            rainbow("Δ DELTA-NORM WIRTSCHAFTSSIMULATION – BUNTE UTF8-ART AUSWERTUNG Δ", color),
            ansi_bold("Tage=%d | Personen=%d | Seed=%d | Szenario=%s | Laufzeit=%s s" % (self.days, self.person_count, self.seed, self.scenario, f2(runtime)), color),
            rainbow("═" * 94, color),
        ]
        lines.extend(header)
        lines.append("")

        add(
            "1. Makro-Puls der Gesamtwirtschaft",
            "Hier wird der grundlegende Puls des Systems gezeigt: Preisniveau, Geldmenge, Arbeitslosigkeit, Vertrauen und tägliches Handelsvolumen. Diese Größen werden simuliert, weil ein Wirtschaftssystem nur dann verstehbar ist, wenn man gleichzeitig Kosten, Liquidität, Arbeitsintegration, soziale Koordination und Marktaktivität beobachtet.",
            [
                pad_ansi("Preisindex         " + sparkline([m['price_index'] for m in metrics], 62, color) + "  Ende=" + f2(last['price_index']), 96),
                pad_ansi("Geldmenge          " + sparkline([m['broad_money'] for m in metrics], 62, color) + "  Ende=" + f2(last['broad_money']), 96),
                pad_ansi("Arbeitslosigkeit   " + sparkline([100 * m['unemployment'] for m in metrics], 62, color) + "  Ende=" + pct(last['unemployment']), 96),
                pad_ansi("Vertrauen          " + sparkline([m['avg_trust'] for m in metrics], 62, color) + "  Ende=" + f3(last['avg_trust']), 96),
                pad_ansi("Handelsvolumen/Tag " + sparkline([m['tx_volume_today'] for m in metrics], 62, color) + "  Ende=" + f2(last['tx_volume_today']), 96),
            ],
            "Am Ende liegt der Preisindex bei %s, die positive Geldmenge bei %s D und die Arbeitslosigkeit bei %s. Das Vertrauen endet bei %s. Wenn Preisindex und Geldmenge schneller steigen als Versorgung, deutet das auf Druck und Verteilungsstress hin. Sinkende Arbeitslosigkeit zusammen mit stabilem Vertrauen deutet dagegen auf eine robuste Verhaltensökonomie hin." % (f2(last['price_index']), f2(last['broad_money']), pct(last['unemployment']), f3(last['avg_trust']))
        )

        add(
            "2. Delta-Geldschöpfung, Vernichtung und Haftung",
            "Dieses Panel zeigt, wie das System seine Währung aus Verhalten erzeugt und wieder vernichtet. Simuliert werden tägliche Neuschöpfung durch positive Delta-Ereignisse, Vernichtung durch negative Normabweichungen und Haftungsaufbau, wenn Akteure Belastungen nicht direkt bezahlen können. Das ist zentral, weil Geld hier nicht exogen, sondern verhaltensgebunden entsteht.",
            [
                "Erzeugung/Tag      " + sparkline([m['created_today'] for m in metrics], 62, color) + "  Summe=" + f2(self.created),
                "Vernichtung/Tag    " + sparkline([m['destroyed_today'] for m in metrics], 62, color) + "  Summe=" + f2(self.destroyed),
                "Haftung/Tag        " + sparkline([m['liability_today'] for m in metrics], 62, color) + "  Summe=" + f2(self.liability_created),
                "Breitgeld          " + simple_bar(last['broad_money'], max(last['broad_money'], last['total_liability'] + 1), 40, 32, color) + " " + f2(last['broad_money']),
                "Haftungsbestand    " + simple_bar(last['total_liability'], max(last['broad_money'], last['total_liability'] + 1), 40, 31, color) + " " + f2(last['total_liability']),
            ],
            "Insgesamt wurden %s D geschaffen, %s D vernichtet und %s D als neue Haftung gebucht. Hohe Vernichtung bei gleichzeitig wachsender Haftung bedeutet, dass das System Fehlverhalten oder Belastungen zwar erkennt, aber ein Teil davon nur in die Zukunft verschoben wird. Eine gesunde Lage entsteht, wenn die Geldschöpfung aus produktivem Verhalten schneller wächst als die Schuldlast." % (f2(self.created), f2(self.destroyed), f2(self.liability_created))
        )

        goods = [('food', 'Nahrung', 'food_stock_ratio'), ('water', 'Wasser', 'water_stock_ratio'), ('energy', 'Energie', 'energy_stock_ratio'), ('oxygen', 'Sauerstoff', 'oxygen_stock_ratio'), ('spares', 'Ersatzteile', 'spares_stock_ratio')]
        art_goods = []
        for key, label, metric_key in goods:
            art_goods.append(pad_ansi(label.ljust(14) + ratio_bar(last.get(metric_key, 0.0), 42, color) + '  ' + f2(last.get(metric_key, 0.0)) + 'x Ziel', 96))
        add(
            "3. Grundversorgung und Bestandslage",
            "Hier wird simuliert, wie gut die Grundversorgung relativ zum Zielbestand gedeckt ist. Nahrung, Wasser, Energie, Sauerstoff und Ersatzteile sind systemische Kerngüter. Ohne diese Darstellung wäre nicht erkennbar, ob Geldschöpfung auf realer Versorgung ruht oder ob nur eine nominale Scheinökonomie wächst.",
            art_goods,
            "Bestandsverhältnisse über 1,0 bedeuten Überdeckung, Werte darunter Unterdeckung. Kritisch sind besonders Sauerstoff und Ersatzteile in Mond-, Orbit- und Stationsökonomien. Die aktuelle Lage zeigt Nahrung=%s, Wasser=%s, Energie=%s, Sauerstoff=%s und Ersatzteile=%s mal Zielbestand." % tuple(f2(last.get(metric_key, 0.0)) for _, _, metric_key in goods)
        )

        art_prices = []
        current_basic_indices = []
        for loc in ('Earth', 'Moon', 'Orbit', 'Station'):
            market = self.markets[loc]
            bidx = market.index(True)
            gidx = market.index(False)
            current_basic_indices.append(bidx)
            art_prices.append('%-8s Basis %s %s  |  Gesamt %s %s' % (loc, simple_bar(bidx, max(130.0, max(current_basic_indices) + 5), 18, 33, color), f2(bidx), simple_bar(gidx, max(150.0, gidx + 5), 18, 36, color), f2(gidx)))
        add(
            "4. Preislandschaft nach Ort",
            "Dieses Panel simuliert die Preisstruktur für Erde, Mond, Orbit und Raumstation. Das ist wichtig, weil dieselbe Verhaltensleistung an verschiedenen Orten auf verschiedene Knappheiten trifft. Dadurch wird sichtbar, wo das Delta-Geld real mehr oder weniger Kaufkraft hat.",
            art_prices,
            "Hohe Basispreisindizes im All zeigen, dass Lebenserhaltung und Logistik die Kosten stark erhöhen. Wenn Erde deutlich günstiger bleibt als Orbit und Station, entsteht ein natürlicher Ausgleichsdruck über Logistik, Politik und Transfers. Preisunterschiede sind also ein Signal für räumliche Knappheit und nicht bloß nominale Inflation."
        )

        art_pop = []
        for loc in ('Earth', 'Moon', 'Orbit', 'Station'):
            pop = location_people.get(loc, 0)
            unemp = location_unemployed.get(loc, 0)
            emp = max(0, pop - unemp)
            art_pop.append('%-8s Bev %s %3d  | Besch %s %3d  | Unbesch %s %3d' % (loc, simple_bar(pop, max_loc_pop, 18, 34, color), pop, simple_bar(emp, max_loc_pop, 18, 32, color), emp, simple_bar(unemp, max_loc_pop, 18, 31, color), unemp))
        add(
            "5. Bevölkerung und Beschäftigung im Raum Erde–Mond–Orbit",
            "Hier wird gezeigt, wie viele Menschen an jedem Ort leben und wie viele davon beschäftigt oder unbeschäftigt sind. Das wird simuliert, weil Beschäftigung in diesem Modell nicht nur Einkommen liefert, sondern auch als verhaltensbezogene Einbindung in die gesellschaftliche Reproduktion wirkt.",
            art_pop,
            "Die Beschäftigungsstruktur zeigt, wo Produktivität sozial verankert ist und wo Integrationsprobleme entstehen. Hohe Unbeschäftigung in kleinen Raumökonomien ist besonders gefährlich, weil dort Grundversorgung und technische Aufrechterhaltung stärker gekoppelt sind als auf der Erde."
        )

        art_sectors = []
        for sector, count in sector_employment.most_common(10):
            art_sectors.append('%-16s %s %3d | Firmen %2d' % (sector, simple_bar(count, max_sector_emp, 34, 35, color), count, sector_firms.get(sector, 0)))
        add(
            "6. Arbeitssektoren und produktive Schwerpunkte",
            "Dieses Diagramm simuliert, in welchen Sektoren Arbeitskraft gebunden ist. Es ist wichtig, weil ein Wirtschaftssystem nicht nur Geldflüsse, sondern auch Struktur braucht: Nahrung, Energie, Medien, Forschung, Raumfahrt, Gesundheit und Logistik müssen miteinander im Gleichgewicht stehen.",
            art_sectors,
            "Hohe Beschäftigung in Basis- und Infrastruktursektoren stärkt die Reproduktion der Wirtschaft. Dominieren nur Medien, Finanz- oder Konsumbereiche, ohne dass Grundversorgung mithält, entsteht ein empfindliches Ungleichgewicht zwischen Darstellung, Kredit und realer Versorgung."
        )

        art_domains = []
        for domain, delta in sorted(events_by_domain.items(), key=lambda kv: abs(kv[1]), reverse=True)[:12]:
            art_domains.append('%-14s %s %9s | Events %5d' % (domain, signed_bar(delta, max_domain_abs, 40, color), f2(delta), event_count_by_domain[domain]))
        add(
            "7. Delta-Bilanz nach Verhaltensdomänen",
            "Hier wird simuliert, welche Verhaltensdomänen per Saldo Delta-Geld schaffen oder vernichten. Das ist essenziell, weil das System nicht auf Branchengewinnen im herkömmlichen Sinn beruht, sondern auf normierten Beiträgen und Belastungen jeder Handlungsklasse.",
            art_domains,
            "Positive Balken bedeuten Netto-Geldschöpfung aus nützlichem Verhalten, negative Balken Netto-Vernichtung durch Belastungen. Damit wird sichtbar, welche Bereiche das System tragen und welche Bereiche Kosten- oder Risikozentren sind. Besonders interessant ist, ob Medien, Raumfahrt, Nahrung und Arbeit dauerhaft positive oder fragile Salden erzeugen."
        )

        art_actions = []
        for (domain, action), count in action_counts.most_common(12):
            label = (domain + '/' + action)[:28]
            art_actions.append('%-28s %s %5d' % (label, simple_bar(count, max_action, 34, 36, color), count))
        add(
            "8. Häufigste konkrete Handlungen",
            "Dieses Panel zeigt, welche Mikrohandlungen tatsächlich das Wirtschaftsgeschehen dominieren. Simuliert wird dies, weil die Gesamtökonomie aus wiederholten Verhaltensakten besteht: arbeiten, konsumieren, berichten, warten, transportieren, reparieren, lernen und finanzieren.",
            art_actions,
            "Die häufigsten Handlungen zeigen den operativen Kern des Systems. Wenn konsumierende oder kompensierende Handlungen dominieren, aber zu wenig produktive oder reparierende Handlungen stattfinden, verschiebt sich die Ökonomie in Richtung Abbau. Eine gute Lage braucht Wiederholung produktiver, versorgender und koordinierender Akte."
        )

        media_art = [
            'Wahrheit         ' + sparkline([m['media_truth_index'] for m in metrics], 62, color) + '  Ende=' + f3(last['media_truth_index']),
            'Manipulation     ' + sparkline([m['media_manipulation_index'] for m in metrics], 62, color) + '  Ende=' + f3(last['media_manipulation_index']),
            'Vertrauen        ' + sparkline([m['avg_trust'] for m in metrics], 62, color) + '  Ende=' + f3(last['avg_trust']),
            'Gerüchtethemen   ' + simple_bar(rumor_topics, max(1, sum(topic_categories.values())), 40, 31, color) + ' %d/%d' % (rumor_topics, sum(topic_categories.values())),
        ]
        for cat, c in topic_categories.most_common(6):
            media_art.append('%-14s %s %4d' % (cat, simple_bar(c, max(topic_categories.values()) if topic_categories else 1, 34, 33, color), c))
        add(
            "9. Massenmedien, Nachrichten und Informationsökologie",
            "Hier wird simuliert, wie wahrheitsnah oder manipulationsanfällig die Nachrichtenlage ist und welche Themen dominieren. Das ist in dieser Ökonomie zentral, weil Medien selbst Verhalten auslösen: Vertrauen, Panik, Koordination, Fehlsteuerung und Nachfrage hängen direkt von Informationsqualität ab.",
            media_art,
            "Wenn Wahrheit sinkt und Manipulation steigt, leidet die Koordinationsfähigkeit der gesamten Wirtschaft. Besonders schädlich sind Gerüchtedynamiken, weil sie sowohl Märkte als auch Verhalten verzerren. Stabile Medien verbessern dagegen Lernfähigkeit, Risikoerkennung und faire Delta-Bewertung."
        )

        wellbeing_art = [
            'Gesundheit       ' + sparkline([m['avg_health'] for m in metrics], 62, color) + '  Ende=' + f3(last['avg_health']),
            'Stress           ' + sparkline([m['avg_stress'] for m in metrics], 62, color) + '  Ende=' + f3(last['avg_stress']),
            'Vertrauen        ' + sparkline([m['avg_trust'] for m in metrics], 62, color) + '  Ende=' + f3(last['avg_trust']),
            'Reputation       ' + sparkline([m['avg_reputation'] for m in metrics], 62, color) + '  Ende=' + f3(last['avg_reputation']),
        ]
        add(
            "10. Soziales Befinden: Gesundheit, Stress, Vertrauen, Reputation",
            "Dieses Panel simuliert das soziale und psychische Klima. In einer Verhaltenswährung ist das nicht Nebenbedingung, sondern Kernbestandteil: Gesundheit beeinflusst Leistungsfähigkeit, Stress beeinflusst Fehler und Konflikte, Vertrauen beeinflusst Kooperation, Reputation beeinflusst Zugang und Gewichtung künftiger Handlungen.",
            wellbeing_art,
            "Eine gute Wirtschaft im Delta-Norm-Modell ist nicht nur reich, sondern auch sozial tragfähig. Steigender Stress bei sinkendem Vertrauen ist ein Frühwarnsignal für spätere Produktions-, Medien- und Governance-Probleme. Gesundheit und Reputation stabilisieren dagegen die langfristige Normerfüllung."
        )

        net_values = [p.wallet.total() for p in people]
        pos_values = [p.wallet.positive() for p in people]
        hist_art = []
        for label, count, bar in histogram(net_values, 8, 30, color):
            hist_art.append('%-18s %s %4d' % (label, bar, count))
        hist_art.append('Gini positiv      ' + sparkline([m['gini_positive_money'] for m in metrics], 46, color) + '  Ende=' + f3(last['gini_positive_money']))
        add(
            "11. Vermögensverteilung und soziale Verwundbarkeit",
            "Hier wird die Verteilung der Netto-Konten der Personen sowie die Entwicklung der Ungleichheit gezeigt. Das wird simuliert, weil eine Verhaltenswährung nur dann legitim bleibt, wenn produktive Beiträge nicht automatisch in extreme Konzentration und Ausschluss umschlagen.",
            hist_art,
            "Das Histogramm zeigt, wie viele Personen in welchen Netto-Bereichen liegen. Ein steigender Gini-Koeffizient deutet auf Konzentration positiver Bestände hin. Negative oder schwache Netto-Konten markieren Verwundbarkeit; wenn diese Gruppe wächst, steigt der politische und ökonomische Druck auf Grundversorgung und Einspruchssysteme."
        )

        space_art = []
        for loc in ('Earth', 'Moon', 'Orbit', 'Station'):
            info = self.locations[loc]
            space_art.append('%-8s Infra %s %s | O2 %s %s | Wasser %s %s | Trümmer %s %s' % (
                loc, simple_bar(info.infrastructure, 1.25, 10, 32, color), f2(info.infrastructure),
                simple_bar(info.oxygen_safety, 1.25, 10, 36, color), f2(info.oxygen_safety),
                simple_bar(info.water_security, 1.25, 10, 34, color), f2(info.water_security),
                simple_bar(info.debris_risk, 1.0, 10, 31, color), f2(info.debris_risk)
            ))
        space_art.insert(0, 'Stationssicherheit ' + sparkline([m['station_safety'] for m in metrics], 58, color) + '  Ende=' + f3(last['station_safety']))
        space_art.insert(1, 'Orbit-Trümmer     ' + sparkline([m['orbit_debris_risk'] for m in metrics], 58, color) + '  Ende=' + f3(last['orbit_debris_risk']))
        add(
            "12. Raumwirtschaft und Lebenssicherheit",
            "Dieses Panel simuliert die technische und ökologische Lage von Mond, Orbit und Station. Das ist unverzichtbar, weil Raumökonomien empfindliche Systeme sind: Infrastruktur, Sauerstoff, Wasser und Trümmerrisiko entscheiden dort direkt darüber, ob Verhalten überhaupt in wirtschaftlichen Wert übersetzt werden kann.",
            space_art,
            "Sinkende Stationssicherheit oder steigendes Trümmerrisiko machen deutlich, dass die Raumwirtschaft nicht nur von Preisen und Löhnen abhängt, sondern von physischer Systemstabilität. Hohe Werte bei Sauerstoff- und Wassersicherheit sind ebenso wichtig wie Geldbestände, weil sie die materielle Grundlage jeder weiteren Aktivität bilden."
        )

        top_money = sorted([a for a in self.actors.values() if a.kind != 'market'], key=lambda a: a.wallet.positive(), reverse=True)[:8]
        vulnerable = sorted(people, key=lambda a: a.wallet.total())[:8]
        wealth_art = []
        max_top = max([a.wallet.positive() for a in top_money] or [1.0])
        for a in top_money:
            wealth_art.append(('Top ' + a.name[:22]).ljust(28) + simple_bar(a.wallet.positive(), max_top, 26, 32, color) + ' ' + f2(a.wallet.positive()))
        wealth_art.append('')
        min_v = min([a.wallet.total() for a in vulnerable] or [0.0])
        max_abs_v = max(abs(min_v), max([abs(a.wallet.total()) for a in vulnerable] or [1.0]))
        for a in vulnerable:
            wealth_art.append(('Vuln ' + a.name[:21]).ljust(28) + signed_bar(a.wallet.total(), max_abs_v, 26, color) + ' ' + f2(a.wallet.total()))
        add(
            "13. Akteure an Spitze und Rand des Systems",
            "Hier werden die vermögensstärksten Akteure und die verletzlichsten Personen dargestellt. Dies wird simuliert, weil Systemdesign immer auch Verteilungsdesign ist: Wer akkumuliert Stabilitätsgewinne, und wer trägt die Last von Knappheit, Belastung und Fehlverhalten?",
            wealth_art,
            "Die Spitze zeigt, wohin positives Delta konzentriert fließt. Die vulnerable Gruppe zeigt, wo Grundversorgung, Haftungsschutz und Einspruchsrechte besonders wichtig sind. Eine robuste Verhaltensökonomie braucht beides: Leistungsanreize und starke Schutzmechanismen gegen systemische Verelendung."
        )

        finance_art = [
            'Ausstehende Kredite ' + simple_bar(outstanding_loans, max(outstanding_loans, last['broad_money'] + 1), 38, 33, color) + ' ' + f2(outstanding_loans),
            'Anzahl Kredite      ' + simple_bar(loan_count, max(1, loan_count), 38, 36, color) + ' ' + str(loan_count),
            'Einsprüche gesamt   ' + simple_bar(self.disputed, max(1, self.disputed), 38, 35, color) + ' ' + str(self.disputed),
            'Erfolgreich         ' + simple_bar(self.appeals_granted, max(1, self.disputed), 38, 32, color) + ' ' + str(self.appeals_granted),
            'Lambda Food         ' + simple_bar(self.norms['food'].lam, max(v.lam for v in self.norms.values()), 38, 34, color) + ' ' + f3(self.norms['food'].lam),
            'Lambda Media        ' + simple_bar(self.norms['media'].lam, max(v.lam for v in self.norms.values()), 38, 34, color) + ' ' + f3(self.norms['media'].lam),
            'Lambda Space        ' + simple_bar(self.norms['space'].lam, max(v.lam for v in self.norms.values()), 38, 34, color) + ' ' + f3(self.norms['space'].lam),
        ]
        add(
            "14. Finanz- und Governance-Schicht",
            "Dieses Panel simuliert Kreditbestand, Einsprüche und einige zentrale Lambda-Faktoren der Normbewertung. Das ist wichtig, weil die Ökonomie nicht nur aus spontanen Märkten besteht, sondern aus institutionellen Regeln: Kredit überbrückt Zeit, Einsprüche sichern Fairness, und die Lambda-Faktoren bestimmen die monetäre Stärke von Verhaltensdifferenzen.",
            finance_art,
            "Hohe Kreditbestände können Wachstum finanzieren, machen das System aber empfindlicher für Vertrauensschocks. Einsprüche zeigen, dass die Verhaltensbewertung anfechtbar bleibt und somit nicht in eine blinde Strafmaschine kippt. Lambda-Faktoren sind politische Hebel der Zentralbank und Governance, weil sie direkt in die Geldschöpfung eingreifen."
        )

        lines.append(rainbow("═" * 94, color))
        lines.append(ansi_bold("Ende der bunten UTF8-Art-Auswertung", color))
        lines.append(rainbow("═" * 94, color))
        return "\n".join(lines)

    def write_utf8_dashboard(self, runtime: float) -> None:
        plain = self.build_utf8_dashboard(runtime, color=False)
        ansi_dash = self.build_utf8_dashboard(runtime, color=True)
        with open(os.path.join(self.out, 'utf8_dashboard.md'), 'w', encoding='utf-8') as fh:
            fh.write('# Bunte UTF8-Art-Auswertung\n\n```text\n' + plain + '\n```\n')
        with open(os.path.join(self.out, 'utf8_dashboard_ansi.txt'), 'w', encoding='utf-8') as fh:
            fh.write(ansi_dash + '\n')



# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def self_test() -> int:
    out = "/tmp/delta_norm_self_test_%d" % int(time.time())
    sim = Simulation(days=10, persons=70, seed=123, scenario="baseline", out=out, quiet=True)
    sim.run()
    assert len(sim.events) > 500, "zu wenige Events"
    assert len(sim.transactions) > 300, "zu wenige Transaktionen"
    assert sim.metrics[-1]["broad_money"] > 0, "Geldmenge nicht positiv"
    assert os.path.exists(os.path.join(out, "report.md")), "report fehlt"
    print("Self-test OK:", out)
    return 0


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Delta-Norm-Wirtschaftssimulation für PyPy3", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    p.add_argument("--days", type=int, default=180, help="simulierte Tage")
    p.add_argument("--persons", type=int, default=300, help="Anzahl Personen")
    p.add_argument("--seed", type=int, default=42, help="Zufallsseed")
    p.add_argument("--scenario", choices=["baseline", "media_crisis", "orbit_emergency", "lunar_expansion", "scarcity", "boom"], default="baseline")
    p.add_argument("--out", default="delta_norm_run", help="Ausgabeverzeichnis")
    p.add_argument("--quiet", action="store_true", help="weniger Konsolenausgabe")
    p.add_argument("--self-test", action="store_true", help="kurzen Selbsttest ausführen")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.self_test:
        return self_test()
    if args.days <= 0 or args.persons <= 0:
        raise SystemExit("--days und --persons müssen positiv sein")
    sim = Simulation(args.days, args.persons, args.seed, args.scenario, args.out, args.quiet)
    sim.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
