#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Vector Currency Economy Simulation
==================================

A PyPy3-compatible, standard-library-only, agent-based / stock-flow hybrid
simulation of a political economy with vector money:

    M = (amount, angle, confidence, origin, history)

The angle encodes the combined government-defined good/bad axis and
people-defined popular/unpopular axis. The magnitude is ordinary purchasing
power and the weight of the angle. Confidence measures oracle agreement and
quality of evidence. The simulation includes multiple countries, governments,
peoples, households, firms, banks, central banks, products/services, labor,
credit, taxes, supply chains, media, courts, black markets, shocks,
international trade, angle markets, environmental externalities, fraud, and
macro metrics.

This is not a calibrated economic model. It is a runnable research scaffold:
it contains the mechanisms, accounting interfaces, and adversarial dynamics
needed to experiment with this currency foundation.

Run:
    pypy3 vector_currency_sim.py --steps 120 --countries 3 --households 900 --firms 120 --seed 42 --out metrics.csv --summary summary.json

No external packages required.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import statistics
from collections import defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Iterable, Any

TAU = 2.0 * math.pi
EPS = 1e-9


def clamp(x: float, lo: float, hi: float) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def norm_angle(theta: float) -> float:
    theta = theta % TAU
    if theta < 0:
        theta += TAU
    return theta


def angle_diff_signed(a: float, b: float) -> float:
    """Signed shortest difference a-b in [-pi, pi]."""
    return ((a - b + math.pi) % TAU) - math.pi


def angle_dist(a: float, b: float) -> float:
    return abs(angle_diff_signed(a, b))


def deg(theta: float) -> float:
    return norm_angle(theta) * 180.0 / math.pi


def rad(degrees: float) -> float:
    return norm_angle(degrees * math.pi / 180.0)


def cosine_compat(a: float, b: float, floor: float = 0.0) -> float:
    """Compatibility in [floor,1]; opposite directions approach floor."""
    d = angle_dist(a, b)
    return max(floor, math.cos(d / 2.0))


def angle_mean(weighted_angles: Iterable[Tuple[float, float]]) -> Tuple[float, float]:
    """Return (mean_angle, concentration). Weight may be zero."""
    c = 0.0
    s = 0.0
    wsum = 0.0
    for theta, w in weighted_angles:
        if w <= 0:
            continue
        c += math.cos(theta) * w
        s += math.sin(theta) * w
        wsum += w
    if wsum <= EPS:
        return 0.0, 0.0
    mean = norm_angle(math.atan2(s, c))
    r = math.sqrt(c * c + s * s) / wsum
    return mean, clamp(r, 0.0, 1.0)


def angle_blend(a: float, b: float, weight_b: float) -> float:
    weight_b = clamp(weight_b, 0.0, 1.0)
    mean, _ = angle_mean(((a, 1.0 - weight_b), (b, weight_b)))
    return mean


def angle_from_axes(goodness: float, popularity: float) -> float:
    return norm_angle(math.atan2(popularity, goodness))


def axes_from_angle(theta: float) -> Tuple[float, float]:
    return math.cos(theta), math.sin(theta)


def softplus(x: float) -> float:
    if x > 40:
        return x
    if x < -40:
        return math.exp(x)
    return math.log1p(math.exp(x))


def logistic(x: float) -> float:
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def gini(values: List[float]) -> float:
    if not values:
        return 0.0
    vals = sorted(max(0.0, v) for v in values)
    n = len(vals)
    total = sum(vals)
    if total <= EPS:
        return 0.0
    cum = 0.0
    for i, v in enumerate(vals, start=1):
        cum += i * v
    return (2.0 * cum) / (n * total) - (n + 1.0) / n


def random_angle(rng: random.Random, center: Optional[float] = None, spread: float = math.pi) -> float:
    if center is None:
        return rng.random() * TAU
    return norm_angle(center + rng.uniform(-spread, spread))


def triangular_noise(rng: random.Random, scale: float) -> float:
    return (rng.random() - rng.random()) * scale


@dataclass
class HistoryEntry:
    t: int
    kind: str
    note: str
    amount: float = 0.0
    theta: float = 0.0
    confidence: float = 1.0


@dataclass
class VectorMoney:
    amount: float
    theta: float
    confidence: float
    origin: str = "genesis"
    history: List[HistoryEntry] = field(default_factory=list)

    def clone(self) -> "VectorMoney":
        return VectorMoney(self.amount, self.theta, self.confidence, self.origin, list(self.history))

    def add_history(self, t: int, kind: str, note: str, amount: float = 0.0) -> None:
        self.history.append(HistoryEntry(t, kind, note, amount, self.theta, self.confidence))
        # Keep histories bounded; this preserves recent provenance without growing forever.
        if len(self.history) > 18:
            del self.history[: len(self.history) - 18]

    def value_against(self, target_theta: float) -> float:
        return self.amount * self.confidence * cosine_compat(self.theta, target_theta, 0.0)

    def rotate_to(self, target_theta: float, friction: float, t: int, note: str) -> float:
        """Rotate money angle toward target. Returns amount lost as rotation cost."""
        d = angle_dist(self.theta, target_theta)
        if self.amount <= EPS or d <= EPS:
            return 0.0
        keep = math.exp(-friction * d * d)
        lost = self.amount * (1.0 - keep)
        self.amount *= keep
        # Real rotation reduces confidence if the direction change is large.
        conf_penalty = 1.0 - clamp(0.12 * d / math.pi, 0.0, 0.12)
        self.confidence = clamp(self.confidence * conf_penalty, 0.02, 1.0)
        self.theta = target_theta
        self.add_history(t, "rotate", note, -lost)
        return lost

    def merge_with(self, incoming: "VectorMoney", t: int, note: str) -> None:
        if incoming.amount <= EPS:
            return
        if self.amount <= EPS:
            self.amount = incoming.amount
            self.theta = incoming.theta
            self.confidence = incoming.confidence
            self.origin = incoming.origin
            self.history = list(incoming.history)[-18:]
            self.add_history(t, "merge", note, incoming.amount)
            return
        # The amount is scalar balance. The angle is vector-weighted by amount*confidence.
        old_amount = self.amount
        old_weight = max(EPS, self.amount * self.confidence)
        inc_weight = max(EPS, incoming.amount * incoming.confidence)
        self.theta, conc = angle_mean(((self.theta, old_weight), (incoming.theta, inc_weight)))
        self.confidence = clamp((self.confidence * old_amount + incoming.confidence * incoming.amount) / (old_amount + incoming.amount) * (0.86 + 0.14 * conc), 0.02, 1.0)
        self.amount += incoming.amount
        self.add_history(t, "merge", note, incoming.amount)

    @staticmethod
    def from_axes(amount: float, goodness: float, popularity: float, confidence: float, origin: str) -> "VectorMoney":
        return VectorMoney(amount, angle_from_axes(goodness, popularity), confidence, origin, [])


@dataclass
class Loan:
    id: int
    borrower_id: int
    lender_id: int
    country_id: int
    principal: float
    outstanding: float
    annual_rate: float
    remaining_steps: int
    theta: float
    confidence: float
    defaulted: bool = False

    def scheduled_payment(self) -> float:
        if self.defaulted or self.remaining_steps <= 0:
            return 0.0
        monthly_interest = self.annual_rate / 12.0
        principal_pay = self.outstanding / max(1, self.remaining_steps)
        return self.outstanding * monthly_interest + principal_pay


@dataclass
class GoodSpec:
    name: str
    base_price: float
    essentiality: float
    income_elasticity: float
    angle_sensitivity: float
    labor_intensity: float
    energy_intensity: float
    material_intensity: float
    environmental_harm: float
    social_good: float
    service: bool = False
    input_sectors: Dict[str, float] = field(default_factory=dict)


GOOD_SPECS: Dict[str, GoodSpec] = {
    "food": GoodSpec("food", 8.0, 1.00, 0.20, 0.35, 0.50, 0.20, 0.25, 0.20, 0.55, False, {"energy": 0.10, "raw_materials": 0.08, "transport": 0.08}),
    "energy": GoodSpec("energy", 12.0, 0.90, 0.15, 0.55, 0.25, 0.05, 0.45, 0.85, 0.15, False, {"raw_materials": 0.25, "machinery": 0.08}),
    "housing": GoodSpec("housing", 35.0, 0.95, 0.30, 0.45, 0.35, 0.30, 0.45, 0.45, 0.65, True, {"energy": 0.10, "raw_materials": 0.15}),
    "health": GoodSpec("health", 20.0, 0.85, 0.40, 0.30, 0.70, 0.08, 0.20, 0.12, 0.95, True, {"software": 0.04, "machinery": 0.05}),
    "education": GoodSpec("education", 16.0, 0.75, 0.55, 0.35, 0.75, 0.04, 0.06, 0.05, 0.90, True, {"software": 0.06, "media": 0.03}),
    "transport": GoodSpec("transport", 10.0, 0.70, 0.45, 0.45, 0.42, 0.45, 0.28, 0.55, 0.35, True, {"energy": 0.30, "machinery": 0.06}),
    "clothing": GoodSpec("clothing", 9.0, 0.48, 0.65, 0.55, 0.55, 0.12, 0.30, 0.35, 0.25, False, {"raw_materials": 0.18, "transport": 0.05}),
    "entertainment": GoodSpec("entertainment", 14.0, 0.30, 0.95, 0.70, 0.60, 0.08, 0.04, 0.08, 0.20, True, {"media": 0.12, "software": 0.05}),
    "luxury": GoodSpec("luxury", 50.0, 0.12, 1.30, 0.95, 0.45, 0.25, 0.45, 0.55, -0.05, False, {"raw_materials": 0.30, "media": 0.05}),
    "data": GoodSpec("data", 18.0, 0.35, 1.00, 0.90, 0.35, 0.18, 0.05, 0.25, 0.10, True, {"software": 0.15, "energy": 0.10}),
    "software": GoodSpec("software", 22.0, 0.50, 1.10, 0.65, 0.80, 0.10, 0.02, 0.08, 0.45, True, {"education": 0.06, "data": 0.06}),
    "raw_materials": GoodSpec("raw_materials", 11.0, 0.60, 0.55, 0.70, 0.35, 0.35, 0.70, 0.90, -0.10, False, {"energy": 0.25, "machinery": 0.04}),
    "machinery": GoodSpec("machinery", 38.0, 0.50, 0.75, 0.45, 0.45, 0.22, 0.55, 0.35, 0.45, False, {"raw_materials": 0.35, "software": 0.06, "energy": 0.14}),
    "finance": GoodSpec("finance", 15.0, 0.35, 0.95, 0.95, 0.45, 0.04, 0.02, 0.06, 0.10, True, {"software": 0.08, "data": 0.08}),
    "security": GoodSpec("security", 25.0, 0.55, 0.65, 0.85, 0.60, 0.14, 0.30, 0.30, -0.05, True, {"machinery": 0.08, "data": 0.05}),
    "media": GoodSpec("media", 13.0, 0.38, 1.15, 1.05, 0.62, 0.06, 0.04, 0.05, 0.05, True, {"software": 0.07, "data": 0.09}),
}

SECTORS = list(GOOD_SPECS.keys())
ESSENTIAL_SECTORS = ["food", "energy", "housing", "health", "transport"]


@dataclass
class ActorBase:
    id: int
    name: str
    country_id: int
    cash: VectorMoney
    buy_angle: float
    sell_angle: float
    reputation_theta: float
    reputation_confidence: float
    active: bool = True

    def net_cash(self) -> float:
        return max(0.0, self.cash.amount)

    def receive(self, money: VectorMoney, t: int, note: str) -> None:
        self.cash.merge_with(money, t, note)

    def can_pay(self, amount: float) -> bool:
        return self.active and self.cash.amount + EPS >= amount and amount >= 0.0

    def pay_amount(self, amount: float) -> bool:
        if amount < -EPS:
            raise ValueError("negative payment")
        if self.cash.amount + EPS < amount:
            return False
        self.cash.amount = max(0.0, self.cash.amount - amount)
        return True


@dataclass
class PeopleGroup:
    id: int
    country_id: int
    name: str
    weight: float
    ideology_theta: float
    income_level: float
    susceptibility: float
    activism: float
    trust_government: float
    moral_strictness: float
    sector_preferences: Dict[str, float]
    current_satisfaction: float = 0.0
    anger: float = 0.0

    def sector_preference(self, sector: str) -> float:
        return self.sector_preferences.get(sector, 0.0)


@dataclass
class Household(ActorBase):
    group_id: int = 0
    skill: float = 1.0
    wage_reservation: float = 10.0
    employer_id: Optional[int] = None
    employed_steps: int = 0
    consumption_need: float = 1.0
    savings_propensity: float = 0.12
    risk_aversion: float = 0.5
    political_attention: float = 0.5
    welfare: float = 0.0
    last_income: float = 0.0
    last_consumption: float = 0.0
    last_taxes: float = 0.0
    strike: bool = False


@dataclass
class Firm(ActorBase):
    sector: str = "food"
    technology: float = 1.0
    productivity: float = 1.0
    quality: float = 1.0
    price: float = 10.0
    inventory: float = 0.0
    employees: List[int] = field(default_factory=list)
    target_employees: int = 4
    wage_offer: float = 15.0
    debt: float = 0.0
    equity: float = 1000.0
    owner_country_id: int = 0
    market_power: float = 0.1
    lobbying_budget: float = 0.0
    advertising_budget: float = 0.0
    fraud_level: float = 0.0
    transparency: float = 0.5
    compliance: float = 0.5
    environmental_damage: float = 0.0
    social_impact: float = 0.0
    supply_chain_theta: float = 0.0
    supply_chain_confidence: float = 0.7
    sales: float = 0.0
    units_sold: float = 0.0
    costs: float = 0.0
    profit: float = 0.0
    expected_demand: float = 10.0
    sanctioned: bool = False
    defaulted: bool = False
    black_market_tendency: float = 0.02
    patents: float = 0.0
    data_power: float = 0.0
    media_power: float = 0.0
    country_transform_bias: Dict[int, float] = field(default_factory=dict)

    def reset_period(self) -> None:
        self.sales = 0.0
        self.units_sold = 0.0
        self.costs = 0.0
        self.profit = 0.0

    def current_goodness_estimate(self) -> float:
        spec = GOOD_SPECS[self.sector]
        base = spec.social_good - spec.environmental_harm
        base += 0.40 * self.compliance + 0.18 * self.transparency + 0.12 * self.quality
        base -= 0.95 * self.fraud_level + 0.20 * self.market_power
        base -= 0.12 * max(0.0, self.debt / max(1.0, self.equity + self.cash.amount))
        return clamp(base, -1.0, 1.0)

    def product_angle(self) -> float:
        x = self.current_goodness_estimate()
        # Popularity proxy: reputation y plus advertising/quality-price desirability.
        _, rep_pop = axes_from_angle(self.reputation_theta)
        y = clamp(0.55 * rep_pop + 0.25 * self.quality + 0.18 * self.advertising_budget / max(10.0, self.sales + 10.0) - 0.12 * self.price / max(1.0, GOOD_SPECS[self.sector].base_price), -1.0, 1.0)
        return angle_from_axes(x, y)


@dataclass
class Bank(ActorBase):
    capital: float = 4000.0
    reserves: float = 2000.0
    risk_aversion: float = 0.5
    loans: List[int] = field(default_factory=list)
    failed: bool = False
    shadow_exposure: float = 0.0


@dataclass
class Government(ActorBase):
    competence: float = 0.7
    corruption: float = 0.1
    ideology_theta: float = 0.0
    information_quality: float = 0.7
    power: float = 0.6
    court_independence: float = 0.7
    propaganda_budget: float = 0.0
    emergency_power: float = 0.0
    tax_rate_consumption: float = 0.10
    tax_rate_income: float = 0.18
    tax_rate_profit: float = 0.20
    subsidy_pool: float = 0.0
    debt: float = 0.0
    legitimacy: float = 0.5
    sanctions: Dict[int, float] = field(default_factory=dict)
    moral_memory: Dict[int, float] = field(default_factory=dict)
    uncertainty_memory: Dict[int, float] = field(default_factory=dict)


@dataclass
class CentralBank(ActorBase):
    base_rate: float = 0.04
    inflation_target: float = 0.02
    unemployment_target: float = 0.05
    money_supply_target: float = 100000.0
    angle_policy_theta: float = 0.0
    lender_of_last_resort: float = 0.5
    qe_bias_goodness: float = 0.1


@dataclass
class Country:
    id: int
    name: str
    currency_name: str
    exchange_rate: float
    government_id: int
    central_bank_id: int
    people_groups: List[PeopleGroup]
    legal_quality: float
    media_freedom: float
    inequality_tolerance: float
    border_openness: float
    tariff_rate: float
    resource_stock: float
    pollution: float = 0.0
    inflation: float = 0.0
    unemployment: float = 0.0
    price_index: float = 1.0
    previous_price_index: float = 1.0
    gdp: float = 0.0
    trade_balance: float = 0.0
    protests: float = 0.0
    polarization: float = 0.0
    currency_theta: float = 0.0
    currency_confidence: float = 0.8
    sentiment_sector: Dict[str, float] = field(default_factory=dict)
    sentiment_firm: Dict[int, float] = field(default_factory=dict)
    angle_translation: Dict[int, float] = field(default_factory=dict)
    election_timer: int = 24


@dataclass
class Event:
    t: int
    country_id: Optional[int]
    kind: str
    severity: float
    description: str
    target_id: Optional[int] = None


@dataclass
class StepStats:
    consumer_sales: float = 0.0
    b2b_sales: float = 0.0
    wages: float = 0.0
    taxes: float = 0.0
    subsidies: float = 0.0
    loans_issued: float = 0.0
    loan_defaults: float = 0.0
    black_market_volume: float = 0.0
    angle_rotation_volume: float = 0.0
    angle_rotation_cost: float = 0.0
    laundering_index: float = 0.0
    scandals: int = 0
    strikes: int = 0
    bank_failures: int = 0
    firms_defaulted: int = 0
    trade_volume: float = 0.0
    pollution_delta: float = 0.0


class IdGen:
    def __init__(self) -> None:
        self.next_id = 1

    def __call__(self) -> int:
        i = self.next_id
        self.next_id += 1
        return i


class VectorEconomySim:
    def __init__(self, seed: int, n_countries: int, n_households: int, n_firms: int, n_banks: int, verbose: bool = False) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.verbose = verbose
        self.ids = IdGen()
        self.t = 0
        self.countries: Dict[int, Country] = {}
        self.households: Dict[int, Household] = {}
        self.firms: Dict[int, Firm] = {}
        self.banks: Dict[int, Bank] = {}
        self.governments: Dict[int, Government] = {}
        self.central_banks: Dict[int, CentralBank] = {}
        self.loans: Dict[int, Loan] = {}
        self.events: List[Event] = []
        self.metrics: List[Dict[str, Any]] = []
        self.price_history: Dict[Tuple[int, str], deque] = defaultdict(lambda: deque(maxlen=18))
        self.previous_world_angle = 0.0
        self.default_steps_per_year = 12
        self.generate_world(n_countries, n_households, n_firms, n_banks)

    # ------------------------------------------------------------------
    # World generation
    # ------------------------------------------------------------------
    def make_money(self, amount: float, theta: float, confidence: float, origin: str) -> VectorMoney:
        return VectorMoney(amount, theta, confidence, origin, [HistoryEntry(0, "issue", origin, amount, theta, confidence)])

    def generate_world(self, n_countries: int, n_households: int, n_firms: int, n_banks: int) -> None:
        country_names = ["Aster", "Boreal", "Civitas", "Deltora", "Eiren", "Falken", "Gaia", "Helion"]
        group_names = ["workers", "owners", "students", "retirees", "urban", "rural", "minorities", "technocrats", "traditionalists"]
        for ci in range(n_countries):
            gov_id = self.ids()
            cb_id = self.ids()
            ideology = random_angle(self.rng)
            currency_theta = angle_blend(ideology, rad(60.0), 0.35)
            gov = Government(
                id=gov_id,
                name=f"Government-{country_names[ci % len(country_names)]}",
                country_id=ci,
                cash=self.make_money(30000.0 + 8000.0 * self.rng.random(), currency_theta, 0.75, "treasury"),
                buy_angle=angle_blend(currency_theta, ideology, 0.30),
                sell_angle=angle_blend(currency_theta, ideology, 0.55),
                reputation_theta=currency_theta,
                reputation_confidence=0.75,
                competence=self.rng.uniform(0.45, 0.90),
                corruption=self.rng.uniform(0.02, 0.30),
                ideology_theta=ideology,
                information_quality=self.rng.uniform(0.45, 0.90),
                power=self.rng.uniform(0.45, 0.90),
                court_independence=self.rng.uniform(0.35, 0.90),
                propaganda_budget=self.rng.uniform(0.0, 150.0),
                emergency_power=self.rng.uniform(0.0, 0.10),
                tax_rate_consumption=self.rng.uniform(0.06, 0.18),
                tax_rate_income=self.rng.uniform(0.10, 0.28),
                tax_rate_profit=self.rng.uniform(0.12, 0.32),
                subsidy_pool=0.0,
                debt=self.rng.uniform(2000.0, 12000.0),
                legitimacy=self.rng.uniform(0.40, 0.80),
            )
            cb = CentralBank(
                id=cb_id,
                name=f"CentralBank-{country_names[ci % len(country_names)]}",
                country_id=ci,
                cash=self.make_money(120000.0, currency_theta, 0.85, "central-bank"),
                buy_angle=currency_theta,
                sell_angle=currency_theta,
                reputation_theta=currency_theta,
                reputation_confidence=0.85,
                base_rate=self.rng.uniform(0.015, 0.07),
                inflation_target=self.rng.uniform(0.015, 0.035),
                unemployment_target=self.rng.uniform(0.035, 0.080),
                money_supply_target=120000.0,
                angle_policy_theta=currency_theta,
                lender_of_last_resort=self.rng.uniform(0.35, 0.85),
                qe_bias_goodness=self.rng.uniform(-0.05, 0.20),
            )
            groups: List[PeopleGroup] = []
            raw_weights = [self.rng.random() + 0.2 for _ in range(5)]
            total_w = sum(raw_weights)
            for gi in range(5):
                theta = random_angle(self.rng, ideology, spread=math.pi * 0.85)
                prefs = {}
                for sec in SECTORS:
                    spec = GOOD_SPECS[sec]
                    cultural = 0.25 * math.cos(angle_diff_signed(theta, angle_from_axes(spec.social_good, spec.income_elasticity - 0.5)))
                    prefs[sec] = clamp(cultural + triangular_noise(self.rng, 0.35), -1.0, 1.0)
                groups.append(PeopleGroup(
                    id=gi,
                    country_id=ci,
                    name=group_names[(ci * 5 + gi) % len(group_names)],
                    weight=raw_weights[gi] / total_w,
                    ideology_theta=theta,
                    income_level=self.rng.uniform(0.55, 1.70),
                    susceptibility=self.rng.uniform(0.25, 0.90),
                    activism=self.rng.uniform(0.15, 0.85),
                    trust_government=self.rng.uniform(0.25, 0.85),
                    moral_strictness=self.rng.uniform(0.25, 0.90),
                    sector_preferences=prefs,
                ))
            sentiment = {sec: triangular_noise(self.rng, 0.20) for sec in SECTORS}
            country = Country(
                id=ci,
                name=country_names[ci % len(country_names)],
                currency_name=f"VC{ci}",
                exchange_rate=self.rng.uniform(0.75, 1.35),
                government_id=gov_id,
                central_bank_id=cb_id,
                people_groups=groups,
                legal_quality=self.rng.uniform(0.40, 0.90),
                media_freedom=self.rng.uniform(0.35, 0.95),
                inequality_tolerance=self.rng.uniform(0.25, 0.75),
                border_openness=self.rng.uniform(0.35, 0.90),
                tariff_rate=self.rng.uniform(0.02, 0.18),
                resource_stock=self.rng.uniform(30000.0, 90000.0),
                pollution=self.rng.uniform(0.0, 0.25),
                currency_theta=currency_theta,
                currency_confidence=0.78,
                sentiment_sector=sentiment,
                election_timer=self.rng.randint(18, 36),
            )
            self.countries[ci] = country
            self.governments[gov_id] = gov
            self.central_banks[cb_id] = cb

        # Cross-country angle translation: moral-cultural coordinate transformations.
        for ca in self.countries.values():
            for cb in self.countries.values():
                if ca.id == cb.id:
                    ca.angle_translation[cb.id] = 0.0
                else:
                    ca.angle_translation[cb.id] = triangular_noise(self.rng, math.pi / 3.0)

        # Households
        for hi in range(n_households):
            ci = hi % n_countries
            country = self.countries[ci]
            group_idx = self.weighted_group_index(country)
            group = country.people_groups[group_idx]
            income_factor = group.income_level * self.rng.lognormvariate(0.0, 0.28)
            buy = angle_blend(group.ideology_theta, country.currency_theta, 0.35)
            sell = angle_blend(group.ideology_theta, country.currency_theta, 0.20)
            cash_amt = self.rng.uniform(400.0, 2200.0) * income_factor
            hh = Household(
                id=self.ids(),
                name=f"HH-{hi}",
                country_id=ci,
                cash=self.make_money(cash_amt, random_angle(self.rng, country.currency_theta, math.pi / 5.0), self.rng.uniform(0.55, 0.9), "household-initial"),
                buy_angle=buy,
                sell_angle=sell,
                reputation_theta=buy,
                reputation_confidence=self.rng.uniform(0.45, 0.80),
                group_id=group_idx,
                skill=clamp(self.rng.lognormvariate(0.0, 0.32), 0.30, 2.40),
                wage_reservation=GOOD_SPECS["food"].base_price * self.rng.uniform(1.2, 2.5) * income_factor,
                consumption_need=self.rng.uniform(0.75, 1.45),
                savings_propensity=clamp(self.rng.gauss(0.14, 0.07), 0.02, 0.50),
                risk_aversion=self.rng.uniform(0.15, 0.95),
                political_attention=self.rng.uniform(0.10, 0.95),
            )
            self.households[hh.id] = hh

        # Firms. Ensure each country has basic sectors.
        for fi in range(n_firms):
            ci = fi % n_countries
            country = self.countries[ci]
            if fi < n_countries * len(SECTORS):
                sector = SECTORS[(fi // n_countries) % len(SECTORS)]
            else:
                # Weighted toward essentials and services.
                pool = SECTORS + ESSENTIAL_SECTORS + ["software", "media", "finance", "energy", "raw_materials"]
                sector = self.rng.choice(pool)
            spec = GOOD_SPECS[sector]
            firm_theta = angle_from_axes(spec.social_good - spec.environmental_harm + triangular_noise(self.rng, 0.25), triangular_noise(self.rng, 0.4))
            firm_id = self.ids()
            firm = Firm(
                id=firm_id,
                name=f"F-{sector[:4]}-{fi}",
                country_id=ci,
                cash=self.make_money(self.rng.uniform(2000.0, 13000.0), random_angle(self.rng, country.currency_theta, math.pi / 4), self.rng.uniform(0.50, 0.88), "firm-initial"),
                buy_angle=angle_blend(country.currency_theta, firm_theta, 0.45),
                sell_angle=angle_blend(firm_theta, country.currency_theta, 0.25),
                reputation_theta=firm_theta,
                reputation_confidence=self.rng.uniform(0.40, 0.82),
                sector=sector,
                technology=self.rng.uniform(0.65, 1.60),
                productivity=self.rng.uniform(0.70, 1.45),
                quality=self.rng.uniform(0.55, 1.50),
                price=spec.base_price * self.rng.uniform(0.78, 1.35),
                inventory=self.rng.uniform(10.0, 80.0),
                target_employees=self.rng.randint(2, 20),
                wage_offer=spec.base_price * spec.labor_intensity * self.rng.uniform(5.0, 12.0),
                debt=self.rng.uniform(0.0, 7000.0),
                equity=self.rng.uniform(3000.0, 30000.0),
                owner_country_id=ci if self.rng.random() < 0.82 else self.rng.randrange(n_countries),
                market_power=self.rng.betavariate(1.4, 5.5),
                lobbying_budget=self.rng.uniform(0.0, 200.0),
                advertising_budget=self.rng.uniform(0.0, 400.0),
                fraud_level=clamp(self.rng.betavariate(1.0, 7.5) + (0.12 if sector in ("finance", "luxury", "data", "raw_materials") and self.rng.random() < 0.35 else 0.0), 0.0, 1.0),
                transparency=self.rng.uniform(0.25, 0.95),
                compliance=self.rng.uniform(0.30, 0.95),
                environmental_damage=spec.environmental_harm * self.rng.uniform(0.6, 1.4),
                social_impact=spec.social_good * self.rng.uniform(0.7, 1.3),
                supply_chain_theta=angle_blend(firm_theta, country.currency_theta, self.rng.uniform(0.2, 0.7)),
                supply_chain_confidence=self.rng.uniform(0.35, 0.85),
                expected_demand=self.rng.uniform(10.0, 80.0),
                black_market_tendency=self.rng.uniform(0.0, 0.10),
                patents=self.rng.uniform(0.0, 3.0 if sector in ("software", "machinery", "health", "data") else 0.7),
                data_power=self.rng.uniform(0.0, 4.0 if sector in ("data", "software", "media", "finance") else 0.5),
                media_power=self.rng.uniform(0.0, 4.0 if sector == "media" else 0.4),
            )
            self.firms[firm_id] = firm

        # Banks
        for bi in range(n_banks):
            ci = bi % n_countries
            country = self.countries[ci]
            bank_theta = angle_blend(country.currency_theta, random_angle(self.rng), 0.20)
            bid = self.ids()
            bank = Bank(
                id=bid,
                name=f"Bank-{country.name}-{bi}",
                country_id=ci,
                cash=self.make_money(self.rng.uniform(18000.0, 70000.0), bank_theta, self.rng.uniform(0.55, 0.90), "bank-capital"),
                buy_angle=angle_blend(bank_theta, country.currency_theta, 0.45),
                sell_angle=bank_theta,
                reputation_theta=bank_theta,
                reputation_confidence=self.rng.uniform(0.50, 0.90),
                capital=self.rng.uniform(8000.0, 45000.0),
                reserves=self.rng.uniform(8000.0, 45000.0),
                risk_aversion=self.rng.uniform(0.20, 0.90),
                shadow_exposure=self.rng.uniform(0.0, 0.20),
            )
            self.banks[bid] = bank

        # Give initial employees by crude matching.
        self.initial_labor_matching()
        self.recompute_country_price_indices(initial=True)
        self.previous_world_angle = self.world_money_angle()[0]

    def weighted_group_index(self, country: Country) -> int:
        r = self.rng.random()
        acc = 0.0
        for g in country.people_groups:
            acc += g.weight
            if r <= acc:
                return g.id
        return country.people_groups[-1].id

    def initial_labor_matching(self) -> None:
        unemployed = list(self.households.values())
        self.rng.shuffle(unemployed)
        firms_by_country: Dict[int, List[Firm]] = defaultdict(list)
        for f in self.firms.values():
            firms_by_country[f.country_id].append(f)
        for hh in unemployed:
            candidates = firms_by_country[hh.country_id]
            if not candidates:
                continue
            # Random but biased toward wage/angle compatibility.
            best = None
            best_score = -1e18
            for f in self.rng.sample(candidates, min(10, len(candidates))):
                if len(f.employees) >= f.target_employees:
                    continue
                score = f.wage_offer * hh.skill * (0.4 + cosine_compat(hh.sell_angle, f.reputation_theta, 0.05))
                score += triangular_noise(self.rng, f.wage_offer)
                if score > best_score:
                    best = f
                    best_score = score
            if best is not None and best_score >= hh.wage_reservation * 0.5:
                best.employees.append(hh.id)
                hh.employer_id = best.id

    # ------------------------------------------------------------------
    # Money, transactions, and angle translation
    # ------------------------------------------------------------------
    def translate_angle(self, theta: float, from_country: int, to_country: int) -> float:
        if from_country == to_country:
            return theta
        rot = self.countries[from_country].angle_translation.get(to_country, 0.0)
        return norm_angle(theta + rot)

    def transaction(
        self,
        payer: ActorBase,
        payee: ActorBase,
        amount: float,
        context_theta: float,
        context_confidence: float,
        stats: StepStats,
        note: str,
        tax_rate: float = 0.0,
        tariff_rate: float = 0.0,
        allow_black_market: bool = True,
    ) -> bool:
        if amount <= EPS or not payer.active or not payee.active:
            return False
        # Cross-country exchange and tariffs are handled in scalar amount.
        tax = amount * tax_rate
        tariff = amount * tariff_rate
        total = amount + tax + tariff
        if not payer.can_pay(total):
            return False

        payer_country = self.countries[payer.country_id]
        payee_country = self.countries[payee.country_id]
        ctx = context_theta
        conf = context_confidence
        black = False
        if allow_black_market:
            angle_bad = 1.0 - cosine_compat(payer.buy_angle, context_theta, 0.0)
            gov = self.governments[payee_country.government_id]
            sanction = 0.0
            if isinstance(payee, Firm):
                sanction = gov.sanctions.get(payee.id, 0.0)
            p_black = clamp(0.02 + 0.15 * angle_bad + 0.25 * sanction, 0.0, 0.65)
            if self.rng.random() < p_black * getattr(payee, "black_market_tendency", 0.04):
                black = True
                # Black market avoids some taxes but worsens confidence and rotates toward bad/unpopular.
                tax *= 0.15
                tariff *= 0.25
                total = amount + tax + tariff
                ctx = angle_blend(ctx, rad(210.0), 0.25 + 0.35 * sanction)
                conf *= 0.45
                stats.black_market_volume += amount

        if not payer.pay_amount(total):
            return False

        if payer.country_id != payee.country_id:
            # Numeric exchange-rate adjustment. Seller receives in local currency units.
            fx = payer_country.exchange_rate / max(EPS, payee_country.exchange_rate)
            received_amount = amount * fx
            payee_country.trade_balance += received_amount
            payer_country.trade_balance -= amount
            stats.trade_volume += amount
            ctx = self.translate_angle(ctx, payer.country_id, payee.country_id)
            conf *= 0.90
        else:
            received_amount = amount

        incoming_theta = angle_mean(((payer.cash.theta, 0.35 * amount), (ctx, 0.65 * amount)))[0]
        incoming = VectorMoney(received_amount, incoming_theta, clamp(conf * payer.cash.confidence, 0.02, 1.0), payer.name, [])
        incoming.add_history(self.t, "tx", note, received_amount)
        payee.receive(incoming, self.t, note)

        if tax > EPS:
            gov = self.governments[payee_country.government_id]
            gov_money = VectorMoney(tax, angle_blend(incoming_theta, gov.reputation_theta, 0.25), clamp(conf * 0.92, 0.02, 1.0), "tax", [])
            gov.receive(gov_money, self.t, f"tax:{note}")
            stats.taxes += tax
        if tariff > EPS:
            gov = self.governments[payer_country.government_id]
            tariff_money = VectorMoney(tariff, angle_blend(incoming_theta, gov.reputation_theta, 0.15), clamp(conf * 0.85, 0.02, 1.0), "tariff", [])
            gov.receive(tariff_money, self.t, f"tariff:{note}")
            stats.taxes += tariff
        if black:
            # legal risk and low confidence degrade both parties a little.
            payer.reputation_theta = angle_blend(payer.reputation_theta, rad(210.0), 0.02)
            payee.reputation_theta = angle_blend(payee.reputation_theta, rad(210.0), 0.03)
            payer.reputation_confidence = clamp(payer.reputation_confidence * 0.995, 0.02, 1.0)
            payee.reputation_confidence = clamp(payee.reputation_confidence * 0.990, 0.02, 1.0)
        return True

    # ------------------------------------------------------------------
    # Simulation step
    # ------------------------------------------------------------------
    def step(self) -> Dict[str, Any]:
        self.t += 1
        stats = StepStats()
        for f in self.firms.values():
            f.reset_period()

        self.generate_shocks(stats)
        self.update_media_and_sentiment(stats)
        self.government_oracles_and_policy(stats)
        self.central_bank_policy(stats)
        self.labor_market(stats)
        self.pay_wages(stats)
        self.credit_market(stats)
        self.production_and_supply_chains(stats)
        self.product_and_service_markets(stats)
        self.loan_servicing(stats)
        self.taxes_subsidies_and_public_spending(stats)
        self.angle_market(stats)
        self.legal_system_and_audits(stats)
        self.update_reputations(stats)
        self.environment_feedback(stats)
        self.firm_pricing_and_survival(stats)
        self.elections_and_politics(stats)
        self.recompute_country_price_indices(initial=False)
        row = self.collect_metrics(stats)
        self.metrics.append(row)
        return row

    # ------------------------------------------------------------------
    # Shocks, media, oracles
    # ------------------------------------------------------------------
    def generate_shocks(self, stats: StepStats) -> None:
        # Country-level shocks
        for country in self.countries.values():
            p = 0.018
            if self.rng.random() < p:
                kind = self.rng.choice(["energy_shock", "corruption_leak", "cyberattack", "natural_disaster", "war_scare", "boycott_wave", "bank_run_fear"])
                severity = self.rng.betavariate(1.2, 4.0)
                desc = f"{kind} in {country.name}, severity={severity:.2f}"
                self.events.append(Event(self.t, country.id, kind, severity, desc))
                if kind == "energy_shock":
                    country.sentiment_sector["energy"] = clamp(country.sentiment_sector.get("energy", 0.0) - 0.35 * severity, -1, 1)
                    country.price_index *= 1.0 + 0.08 * severity
                elif kind == "corruption_leak":
                    gov = self.governments[country.government_id]
                    gov.legitimacy = clamp(gov.legitimacy - 0.30 * severity, 0.0, 1.0)
                    gov.reputation_theta = angle_blend(gov.reputation_theta, rad(190), 0.18 * severity)
                    gov.reputation_confidence = clamp(gov.reputation_confidence * (1.0 - 0.12 * severity), 0.02, 1.0)
                elif kind == "cyberattack":
                    for f in self.firms.values():
                        if f.country_id == country.id and f.sector in ("software", "data", "finance", "media"):
                            f.inventory *= max(0.2, 1.0 - 0.35 * severity)
                            f.reputation_theta = angle_blend(f.reputation_theta, rad(175), 0.10 * severity)
                elif kind == "natural_disaster":
                    country.resource_stock *= max(0.85, 1.0 - 0.08 * severity)
                    country.pollution = clamp(country.pollution + 0.05 * severity, 0.0, 2.0)
                    for f in self.firms.values():
                        if f.country_id == country.id and f.sector in ("food", "transport", "housing"):
                            f.inventory *= max(0.1, 1.0 - 0.45 * severity)
                elif kind == "war_scare":
                    country.sentiment_sector["security"] = clamp(country.sentiment_sector.get("security", 0.0) + 0.30 * severity, -1, 1)
                    country.border_openness = clamp(country.border_openness - 0.12 * severity, 0.05, 1.0)
                    country.tariff_rate = clamp(country.tariff_rate + 0.05 * severity, 0.0, 0.5)
                elif kind == "boycott_wave":
                    target = self.rng.choice(list(self.firms.values())) if self.firms else None
                    if target is not None:
                        country.sentiment_firm[target.id] = clamp(country.sentiment_firm.get(target.id, 0.0) - 0.65 * severity, -1, 1)
                        self.events.append(Event(self.t, country.id, "boycott_target", severity, f"Boycott targets {target.name}", target.id))
                elif kind == "bank_run_fear":
                    for b in self.banks.values():
                        if b.country_id == country.id:
                            b.reserves *= max(0.6, 1.0 - 0.25 * severity)
                            b.reputation_confidence *= max(0.6, 1.0 - 0.18 * severity)

        # Firm scandals are separate: fraud and low transparency increase probability.
        for f in list(self.firms.values()):
            if not f.active:
                continue
            c = self.countries[f.country_id]
            p_scandal = 0.002 + 0.035 * f.fraud_level * c.media_freedom * (1.0 - 0.45 * f.transparency)
            p_scandal += 0.008 * max(0.0, f.environmental_damage - 0.5) * c.media_freedom
            if self.rng.random() < p_scandal:
                sev = clamp(self.rng.betavariate(1.1, 3.2) + 0.40 * f.fraud_level, 0.05, 1.0)
                self.events.append(Event(self.t, f.country_id, "firm_scandal", sev, f"Scandal at {f.name}", f.id))
                c.sentiment_firm[f.id] = clamp(c.sentiment_firm.get(f.id, 0.0) - 0.8 * sev, -1, 1)
                f.reputation_theta = angle_blend(f.reputation_theta, rad(200.0), 0.22 * sev)
                f.reputation_confidence = clamp(f.reputation_confidence * (1.0 - 0.22 * sev), 0.02, 1.0)
                stats.scandals += 1

    def update_media_and_sentiment(self, stats: StepStats) -> None:
        # Sentiments decay, propaganda and advertising shift popularity. Media firms create amplification.
        media_power_by_country = defaultdict(float)
        for f in self.firms.values():
            if f.active and f.sector == "media":
                media_power_by_country[f.country_id] += max(0.0, f.media_power + f.advertising_budget / 500.0)
        for country in self.countries.values():
            gov = self.governments[country.government_id]
            for sec in SECTORS:
                country.sentiment_sector[sec] = clamp(country.sentiment_sector.get(sec, 0.0) * 0.985 + triangular_noise(self.rng, 0.015), -1.0, 1.0)
            # Government propaganda boosts sectors close to ideology and dampens scandal sentiment.
            propaganda_strength = gov.propaganda_budget / 1000.0 * (1.0 - country.media_freedom * 0.45)
            for sec in SECTORS:
                spec = GOOD_SPECS[sec]
                sec_theta = angle_from_axes(spec.social_good - spec.environmental_harm, spec.income_elasticity - 0.5)
                fit = math.cos(angle_diff_signed(gov.ideology_theta, sec_theta))
                country.sentiment_sector[sec] = clamp(country.sentiment_sector[sec] + propaganda_strength * 0.03 * fit, -1, 1)
            # Firm advertising: raises popularity, not necessarily goodness; too much ad vs substance reduces confidence later.
            for f in self.firms.values():
                if f.country_id != country.id or not f.active:
                    continue
                ad_effect = 0.020 * math.sqrt(max(0.0, f.advertising_budget)) / 10.0
                ad_effect *= 0.6 + 0.4 * media_power_by_country[country.id]
                country.sentiment_firm[f.id] = clamp(country.sentiment_firm.get(f.id, 0.0) * 0.975 + ad_effect, -1.0, 1.0)
            # Old firm sentiments decay toward zero to model forgetting.
            for fid in list(country.sentiment_firm.keys()):
                country.sentiment_firm[fid] *= 0.970
                if abs(country.sentiment_firm[fid]) < 0.003:
                    del country.sentiment_firm[fid]

    def government_moral_score(self, gov: Government, f: Firm) -> Tuple[float, float]:
        true_good = f.current_goodness_estimate()
        ideology_fit = math.cos(angle_diff_signed(gov.ideology_theta, f.product_angle()))
        lobby_bias = (f.lobbying_budget / 1000.0) * gov.corruption * (0.6 + 0.4 * f.market_power)
        hidden_fraud = f.fraud_level * (1.0 - gov.information_quality) * (1.0 - f.transparency)
        noise = triangular_noise(self.rng, (1.0 - gov.competence * gov.information_quality) * 0.35)
        score = true_good * (0.35 + 0.65 * gov.competence * gov.information_quality)
        score += 0.20 * ideology_fit + lobby_bias - 0.30 * hidden_fraud + noise
        score = clamp(score, -1.0, 1.0)
        uncertainty = clamp(0.08 + 0.55 * (1.0 - gov.information_quality) + 0.25 * (1.0 - f.transparency) + 0.15 * f.fraud_level, 0.02, 0.95)
        return score, uncertainty

    def people_popularity_score(self, country: Country, f: Firm) -> Tuple[float, float]:
        # Weighted across social groups. Popularity responds to price, quality, jobs, sector culture, advertising, and scandals.
        spec = GOOD_SPECS[f.sector]
        sector_sent = country.sentiment_sector.get(f.sector, 0.0)
        firm_sent = country.sentiment_firm.get(f.id, 0.0)
        employment_bonus = min(0.20, len(f.employees) / max(1.0, len(self.households) / max(1, len(self.countries))) * 3.0)
        price_penalty = clamp((f.price / max(1.0, spec.base_price) - 1.0) * 0.35, -0.35, 0.60)
        quality_bonus = clamp((f.quality - 1.0) * 0.25, -0.25, 0.30)
        ad_bonus = clamp(math.sqrt(max(0.0, f.advertising_budget)) / 100.0, 0.0, 0.25)
        values = []
        for g in country.people_groups:
            ideology_fit = math.cos(angle_diff_signed(g.ideology_theta, f.product_angle()))
            pref = g.sector_preference(f.sector)
            v = 0.24 * pref + 0.14 * ideology_fit + sector_sent * g.susceptibility + firm_sent * (0.7 + 0.3 * g.susceptibility)
            v += quality_bonus - price_penalty + employment_bonus + ad_bonus
            v -= 0.25 * f.fraud_level * g.moral_strictness if country.media_freedom > 0.4 else 0.05 * f.fraud_level
            values.append((clamp(v, -1.0, 1.0), g.weight))
        avg = sum(v * w for v, w in values)
        mean = avg / max(EPS, sum(w for _, w in values))
        variance = sum(w * (v - mean) ** 2 for v, w in values) / max(EPS, sum(w for _, w in values))
        uncertainty = clamp(math.sqrt(variance) + 0.08 + 0.10 * (1.0 - country.media_freedom), 0.02, 0.95)
        return clamp(mean, -1.0, 1.0), uncertainty

    def government_oracles_and_policy(self, stats: StepStats) -> None:
        # Governments evaluate firms. Sanctions and subsidies follow, but with errors and political bias.
        for country in self.countries.values():
            gov = self.governments[country.government_id]
            moral_angles = []
            for f in self.firms.values():
                if not f.active:
                    continue
                # Governments mostly evaluate domestic firms, but powerful/sanctioned foreign firms too.
                if f.country_id != country.id and self.rng.random() > (0.10 + 0.15 * f.market_power):
                    continue
                score, uncertainty = self.government_moral_score(gov, f)
                old = gov.moral_memory.get(f.id, score)
                mem = 0.88 * old + 0.12 * score
                gov.moral_memory[f.id] = mem
                gov.uncertainty_memory[f.id] = 0.85 * gov.uncertainty_memory.get(f.id, uncertainty) + 0.15 * uncertainty
                popularity, _ = self.people_popularity_score(country, f) if f.country_id == country.id else (0.0, 0.5)
                moral_angles.append((angle_from_axes(mem, popularity), max(0.01, 1.0 - uncertainty)))
                # Sanction if perceived bad with sufficient confidence.
                if mem < -0.45 and uncertainty < 0.55:
                    intensity = clamp((-mem - 0.35) * (1.0 - uncertainty) * gov.power, 0.0, 1.0)
                    gov.sanctions[f.id] = max(gov.sanctions.get(f.id, 0.0) * 0.98, intensity)
                    if f.country_id == country.id:
                        f.sanctioned = True
                else:
                    if f.id in gov.sanctions:
                        gov.sanctions[f.id] *= 0.96
                        if gov.sanctions[f.id] < 0.02:
                            del gov.sanctions[f.id]
                    if f.country_id == country.id:
                        f.sanctioned = False
            if moral_angles:
                mean_theta, conc = angle_mean(moral_angles)
                gov.reputation_theta = angle_blend(gov.reputation_theta, mean_theta, 0.04)
                gov.reputation_confidence = clamp(0.96 * gov.reputation_confidence + 0.04 * conc, 0.02, 1.0)
            # Budgets react to legitimacy and debt.
            if gov.cash.amount < 4000:
                gov.debt += 1200.0
                cb = self.central_banks[country.central_bank_id]
                issue = VectorMoney(1200.0, angle_blend(country.currency_theta, cb.angle_policy_theta, 0.5), country.currency_confidence * 0.95, "deficit-monetization", [])
                gov.receive(issue, self.t, "deficit issue")
            gov.propaganda_budget = clamp(gov.propaganda_budget * 0.97 + (1.0 - gov.legitimacy) * gov.power * 80.0, 0.0, 900.0)

    # ------------------------------------------------------------------
    # Central banks, credit, banking
    # ------------------------------------------------------------------
    def central_bank_policy(self, stats: StepStats) -> None:
        for country in self.countries.values():
            cb = self.central_banks[country.central_bank_id]
            inflation_gap = country.inflation - cb.inflation_target
            unemployment_gap = country.unemployment - cb.unemployment_target
            cb.base_rate = clamp(cb.base_rate + 0.012 * inflation_gap - 0.008 * unemployment_gap, 0.0, 0.25)
            # Currency confidence drops if inflation and legitimacy gap are high.
            gov = self.governments[country.government_id]
            country.currency_confidence = clamp(0.985 * country.currency_confidence + 0.015 * (0.4 + 0.6 * gov.legitimacy) - 0.04 * max(0.0, inflation_gap), 0.05, 1.0)
            cb.angle_policy_theta = angle_blend(cb.angle_policy_theta, country.currency_theta, 0.04)
            # Lender of last resort for weak banks.
            for bank in self.banks.values():
                if bank.country_id != country.id or not bank.active:
                    continue
                if bank.reserves < 0.08 * max(1.0, bank.capital) and self.rng.random() < cb.lender_of_last_resort:
                    bailout = min(cb.cash.amount * 0.02, max(500.0, 0.10 * bank.capital))
                    if cb.pay_amount(bailout):
                        theta = angle_blend(cb.angle_policy_theta, bank.reputation_theta, 0.30)
                        bank.receive(VectorMoney(bailout, theta, country.currency_confidence * 0.88, "central-bank-bailout", []), self.t, "lender of last resort")
                        bank.reserves += bailout * 0.7
                        stats.subsidies += bailout

    def credit_market(self, stats: StepStats) -> None:
        # Firms under liquidity pressure request loans.
        banks_by_country: Dict[int, List[Bank]] = defaultdict(list)
        for b in self.banks.values():
            if b.active and not b.failed:
                banks_by_country[b.country_id].append(b)
        for f in self.firms.values():
            if not f.active:
                continue
            payroll_need = len(f.employees) * f.wage_offer
            desired_buffer = max(500.0, 0.8 * payroll_need + 0.20 * f.expected_demand * f.price)
            if f.cash.amount >= desired_buffer or self.rng.random() < 0.35:
                continue
            amount = clamp(desired_buffer - f.cash.amount + self.rng.uniform(200.0, 1200.0), 100.0, max(3000.0, 0.5 * f.equity))
            if f.sanctioned:
                amount *= 0.45
            candidates = banks_by_country.get(f.country_id, [])[:]
            if not candidates and self.rng.random() < 0.25:
                candidates = list(self.banks.values())
            self.rng.shuffle(candidates)
            best_offer = None
            for b in candidates[:5]:
                country = self.countries[f.country_id]
                cb = self.central_banks[country.central_bank_id]
                angle_risk = 1.0 - cosine_compat(b.buy_angle, f.reputation_theta, 0.0)
                leverage = f.debt / max(1.0, f.equity + f.cash.amount)
                default_risk = clamp(0.02 + 0.18 * leverage + 0.18 * angle_risk + 0.20 * f.fraud_level + 0.10 * (1.0 - f.reputation_confidence), 0.0, 0.95)
                rate = cb.base_rate + default_risk * (0.05 + 0.24 * b.risk_aversion) + angle_risk * 0.04
                accept_score = (1.0 - default_risk) * (0.8 + 0.2 * b.capital / max(1.0, amount)) - b.risk_aversion * 0.25
                if b.reserves < amount * 0.05:
                    accept_score -= 0.3
                if accept_score > self.rng.random() * 0.8:
                    if best_offer is None or rate < best_offer[0]:
                        best_offer = (rate, b, default_risk)
            if best_offer is not None:
                rate, b, risk = best_offer
                loan_id = self.ids()
                theta = angle_mean(((b.reputation_theta, 0.45), (f.reputation_theta, 0.55)))[0]
                conf = clamp(0.65 * b.reputation_confidence + 0.35 * f.reputation_confidence - 0.25 * risk, 0.04, 1.0)
                loan = Loan(loan_id, f.id, b.id, f.country_id, amount, amount, rate, self.rng.randint(12, 60), theta, conf)
                self.loans[loan_id] = loan
                b.loans.append(loan_id)
                b.reserves -= amount * 0.04  # reserve requirement / liquidity lock
                b.capital -= amount * 0.01 * risk
                f.debt += amount
                f.receive(VectorMoney(amount, theta, conf, "bank-credit", []), self.t, f"loan from {b.name}")
                stats.loans_issued += amount

    def loan_servicing(self, stats: StepStats) -> None:
        for loan in list(self.loans.values()):
            if loan.defaulted or loan.outstanding <= EPS or loan.remaining_steps <= 0:
                continue
            borrower = self.firms.get(loan.borrower_id) or self.households.get(loan.borrower_id)
            bank = self.banks.get(loan.lender_id)
            if borrower is None or bank is None or not bank.active:
                continue
            payment = min(loan.scheduled_payment(), loan.outstanding * 1.15)
            if payment <= EPS:
                continue
            if borrower.can_pay(payment):
                ok = self.transaction(borrower, bank, payment, loan.theta, loan.confidence, stats, "loan-service", tax_rate=0.0, allow_black_market=False)
                if ok:
                    interest = loan.outstanding * (loan.annual_rate / 12.0)
                    principal = max(0.0, payment - interest)
                    loan.outstanding = max(0.0, loan.outstanding - principal)
                    loan.remaining_steps -= 1
                    bank.capital += interest * 0.35
                    bank.reserves += payment * 0.25
                    if isinstance(borrower, Firm):
                        borrower.debt = max(0.0, borrower.debt - principal)
            else:
                stress = (payment - borrower.cash.amount) / max(1.0, payment)
                p_default = clamp(0.08 + 0.55 * stress + 0.12 * getattr(borrower, "fraud_level", 0.0), 0.0, 0.95)
                if self.rng.random() < p_default:
                    loan.defaulted = True
                    recovery = borrower.cash.amount * self.rng.uniform(0.05, 0.45)
                    if recovery > EPS and borrower.pay_amount(recovery):
                        bank.receive(VectorMoney(recovery, loan.theta, loan.confidence * 0.55, "default-recovery", []), self.t, "default recovery")
                    loss = max(0.0, loan.outstanding - recovery)
                    bank.capital -= loss * 0.65
                    bank.reserves -= min(bank.reserves, loss * 0.15)
                    stats.loan_defaults += loss
                    if isinstance(borrower, Firm):
                        borrower.defaulted = True
                        borrower.debt = max(0.0, borrower.debt - loan.outstanding)
                        borrower.reputation_theta = angle_blend(borrower.reputation_theta, rad(200.0), 0.18)
                        borrower.reputation_confidence = clamp(borrower.reputation_confidence * 0.75, 0.02, 1.0)
                else:
                    # Missed payment degrades reputation but does not default yet.
                    borrower.reputation_confidence = clamp(borrower.reputation_confidence * 0.96, 0.02, 1.0)
        for b in self.banks.values():
            if b.active and b.capital < -0.10 * max(1.0, b.reserves):
                b.failed = True
                b.active = False
                b.reputation_theta = angle_blend(b.reputation_theta, rad(210.0), 0.40)
                b.reputation_confidence = clamp(b.reputation_confidence * 0.45, 0.02, 1.0)
                stats.bank_failures += 1

    # ------------------------------------------------------------------
    # Labor, production, product markets
    # ------------------------------------------------------------------
    def labor_market(self, stats: StepStats) -> None:
        # Firms adjust labor targets based on recent sales and inventory.
        for f in self.firms.values():
            if not f.active:
                continue
            demand_signal = 0.80 * f.expected_demand + 0.20 * max(0.0, f.units_sold)
            inventory_pressure = clamp((demand_signal - f.inventory) / max(1.0, demand_signal), -1.0, 1.0)
            if inventory_pressure > 0.25:
                f.target_employees = min(80, f.target_employees + 1 + int(inventory_pressure * 2))
            elif inventory_pressure < -0.45 and f.target_employees > 1:
                f.target_employees = max(1, f.target_employees - 1)
            # Sanctions/falling sales shrink employment.
            if f.sanctioned:
                f.target_employees = max(1, int(f.target_employees * 0.92))

        # Layoffs if over target or cash stress.
        for f in self.firms.values():
            if not f.active:
                continue
            while len(f.employees) > f.target_employees and f.employees:
                hid = f.employees.pop(self.rng.randrange(len(f.employees)))
                hh = self.households.get(hid)
                if hh:
                    hh.employer_id = None
                    hh.employed_steps = 0
            if f.cash.amount < f.wage_offer * max(1, len(f.employees)) * 0.3 and len(f.employees) > 1:
                layoffs = max(1, int(len(f.employees) * 0.08))
                for _ in range(min(layoffs, len(f.employees))):
                    hid = f.employees.pop(self.rng.randrange(len(f.employees)))
                    hh = self.households.get(hid)
                    if hh:
                        hh.employer_id = None
                        hh.employed_steps = 0

        # Quits/strikes from angle mismatch or low wage.
        for hh in self.households.values():
            if hh.employer_id is None:
                continue
            f = self.firms.get(hh.employer_id)
            if f is None or not f.active:
                hh.employer_id = None
                continue
            group = self.countries[hh.country_id].people_groups[hh.group_id]
            mismatch = 1.0 - cosine_compat(hh.sell_angle, f.reputation_theta, 0.0)
            low_wage = max(0.0, (hh.wage_reservation - f.wage_offer * hh.skill) / max(1.0, hh.wage_reservation))
            p_quit = 0.006 + 0.030 * mismatch * group.activism + 0.025 * low_wage
            if f.sanctioned:
                p_quit += 0.025 * group.moral_strictness
            if self.rng.random() < p_quit:
                try:
                    f.employees.remove(hh.id)
                except ValueError:
                    pass
                hh.employer_id = None
                hh.strike = self.rng.random() < group.activism * mismatch
                if hh.strike:
                    stats.strikes += 1

        # Match unemployed workers to vacancies. Country-local first; migration if border open.
        unemployed = [hh for hh in self.households.values() if hh.employer_id is None and hh.active]
        self.rng.shuffle(unemployed)
        firms_by_country: Dict[int, List[Firm]] = defaultdict(list)
        for f in self.firms.values():
            if f.active and len(f.employees) < f.target_employees:
                firms_by_country[f.country_id].append(f)
        for hh in unemployed:
            if hh.strike and self.rng.random() < 0.65:
                hh.strike = False
                continue
            country = self.countries[hh.country_id]
            candidates = firms_by_country.get(hh.country_id, [])[:]
            if self.rng.random() < country.border_openness * 0.04:
                candidates += [f for f in self.firms.values() if f.active and f.country_id != hh.country_id and len(f.employees) < f.target_employees]
            if not candidates:
                continue
            best_f = None
            best_score = -1e18
            for f in self.rng.sample(candidates, min(14, len(candidates))):
                wage = f.wage_offer * hh.skill
                angle_fit = cosine_compat(hh.sell_angle, self.translate_angle(f.reputation_theta, f.country_id, hh.country_id), 0.03)
                commute = 1.0 if f.country_id == hh.country_id else 0.75 * country.border_openness
                score = wage * (0.35 + angle_fit) * commute - hh.wage_reservation * 0.25
                score += triangular_noise(self.rng, max(1.0, wage) * 0.25)
                if score > best_score:
                    best_f, best_score = f, score
            if best_f is not None and best_score > hh.wage_reservation * self.rng.uniform(0.25, 0.95):
                best_f.employees.append(hh.id)
                hh.employer_id = best_f.id
                if len(best_f.employees) >= best_f.target_employees:
                    try:
                        firms_by_country[best_f.country_id].remove(best_f)
                    except ValueError:
                        pass

    def pay_wages(self, stats: StepStats) -> None:
        for f in self.firms.values():
            if not f.active:
                continue
            employees = list(f.employees)
            for hid in employees:
                hh = self.households.get(hid)
                if hh is None or not hh.active:
                    continue
                gross = f.wage_offer * hh.skill * self.rng.uniform(0.92, 1.08)
                gov = self.governments[self.countries[hh.country_id].government_id]
                tax_rate = gov.tax_rate_income
                # If cross-border employment, exchange/tariff not treated as tariff but wage translated.
                ctx = angle_mean(((f.reputation_theta, 0.70), (f.product_angle(), 0.30)))[0]
                if self.transaction(f, hh, gross, ctx, f.reputation_confidence, stats, "wage", tax_rate=tax_rate, allow_black_market=False):
                    hh.last_income += gross * (1.0 - tax_rate)
                    hh.employed_steps += 1
                    f.costs += gross
                    stats.wages += gross
                else:
                    # Failure to pay triggers immediate stress and possible layoff.
                    if self.rng.random() < 0.55:
                        try:
                            f.employees.remove(hid)
                        except ValueError:
                            pass
                        hh.employer_id = None
                    f.reputation_theta = angle_blend(f.reputation_theta, rad(195.0), 0.03)
                    f.reputation_confidence = clamp(f.reputation_confidence * 0.98, 0.02, 1.0)

    def choose_supplier(self, buyer_country: int, sector: str) -> Optional[Firm]:
        candidates = [f for f in self.firms.values() if f.active and f.sector == sector and f.inventory > 0.1]
        if not candidates:
            return None
        country = self.countries[buyer_country]
        # Sample a small candidate set, include imports sometimes.
        domestic = [f for f in candidates if f.country_id == buyer_country]
        foreign = [f for f in candidates if f.country_id != buyer_country]
        pool = []
        if domestic:
            pool += self.rng.sample(domestic, min(len(domestic), 8))
        if foreign and self.rng.random() < country.border_openness:
            pool += self.rng.sample(foreign, min(len(foreign), 5))
        if not pool:
            pool = self.rng.sample(candidates, min(len(candidates), 8))
        best = None
        best_score = 1e18
        for f in pool:
            tariff = country.tariff_rate if f.country_id != buyer_country else 0.0
            translated_theta = self.translate_angle(f.product_angle(), f.country_id, buyer_country)
            compat = cosine_compat(country.currency_theta, translated_theta, 0.05)
            price = f.price * (1.0 + tariff) / max(0.05, compat)
            # sanctions make supplier less attractive.
            gov = self.governments[country.government_id]
            price *= 1.0 + gov.sanctions.get(f.id, 0.0) * 1.5
            if price < best_score:
                best = f
                best_score = price
        return best

    def production_and_supply_chains(self, stats: StepStats) -> None:
        # Firms buy inputs, consume resources, produce inventory, and update supply-chain angle.
        for f in self.firms.values():
            if not f.active:
                continue
            spec = GOOD_SPECS[f.sector]
            employees = len(f.employees)
            if employees <= 0:
                # Small owner-operated output.
                labor_capacity = f.productivity * f.technology * 0.35
            else:
                labor_capacity = employees * f.productivity * f.technology
            shock_factor = max(0.35, 1.0 - self.countries[f.country_id].pollution * 0.06)
            desired_output = max(0.0, labor_capacity * shock_factor * self.rng.uniform(0.85, 1.15))
            input_factor = 1.0
            input_angles: List[Tuple[float, float]] = [(f.reputation_theta, 0.35)]
            total_input_spend = 0.0
            for sec, share in spec.input_sectors.items():
                needed_spend = desired_output * spec.base_price * share * self.rng.uniform(0.75, 1.15)
                if needed_spend <= EPS:
                    continue
                supplier = self.choose_supplier(f.country_id, sec)
                if supplier is None or supplier.inventory <= EPS:
                    input_factor *= 0.92
                    continue
                units = min(supplier.inventory, needed_spend / max(0.5, supplier.price))
                spend = units * supplier.price
                tariff = self.countries[f.country_id].tariff_rate if supplier.country_id != f.country_id else 0.0
                ctx = supplier.product_angle()
                ok = self.transaction(f, supplier, spend, ctx, supplier.reputation_confidence, stats, f"input {sec}", tax_rate=0.0, tariff_rate=tariff, allow_black_market=True)
                if ok:
                    supplier.inventory -= units
                    supplier.sales += spend
                    supplier.units_sold += units
                    stats.b2b_sales += spend
                    total_input_spend += spend
                    input_angles.append((self.translate_angle(ctx, supplier.country_id, f.country_id), spend))
                else:
                    input_factor *= 0.90
            # Resource constraints and environmental harm.
            country = self.countries[f.country_id]
            resource_use = desired_output * (spec.material_intensity + spec.energy_intensity) * 0.45
            if country.resource_stock < resource_use:
                input_factor *= max(0.25, country.resource_stock / max(EPS, resource_use))
                resource_use = country.resource_stock
            country.resource_stock = max(0.0, country.resource_stock - resource_use)
            produced = desired_output * input_factor
            if f.sanctioned:
                produced *= 0.75
            # Fraud can fake quantity/quality at the cost of later scandal risk.
            if f.fraud_level > 0.05 and self.rng.random() < f.fraud_level * 0.25:
                produced *= 1.0 + 0.12 * f.fraud_level
                f.quality = clamp(f.quality - 0.006 * f.fraud_level, 0.10, 2.5)
            f.inventory += produced
            f.costs += total_input_spend
            f.environmental_damage = clamp(0.96 * f.environmental_damage + 0.04 * spec.environmental_harm * (1.0 + produced / 100.0), 0.0, 2.0)
            country.pollution = clamp(country.pollution + produced * spec.environmental_harm * 0.00004, 0.0, 2.5)
            stats.pollution_delta += produced * spec.environmental_harm * 0.00004
            if input_angles:
                f.supply_chain_theta, conc = angle_mean(input_angles)
                f.supply_chain_confidence = clamp(0.92 * f.supply_chain_confidence + 0.08 * conc, 0.02, 1.0)

    def household_demand_units(self, hh: Household, sector: str, price: float) -> float:
        spec = GOOD_SPECS[sector]
        group = self.countries[hh.country_id].people_groups[hh.group_id]
        income = max(1.0, hh.last_income + (0.02 * hh.cash.amount))
        base = hh.consumption_need * spec.essentiality
        if sector not in ESSENTIAL_SECTORS:
            base *= max(0.05, (income / 1000.0) ** spec.income_elasticity)
        pref = 1.0 + 0.35 * group.sector_preference(sector)
        price_ratio = price / max(1.0, spec.base_price)
        elasticity = 0.25 + (1.25 - spec.essentiality) * 0.8
        units = base * pref / max(0.25, price_ratio ** elasticity)
        if sector == "luxury" and income < 700:
            units *= 0.2
        if sector in ("software", "data", "entertainment"):
            units *= 0.55 + 0.65 * group.income_level
        return max(0.0, units * self.rng.uniform(0.65, 1.35))

    def choose_firm_for_household(self, hh: Household, sector: str) -> Optional[Firm]:
        candidates = [f for f in self.firms.values() if f.active and f.sector == sector and f.inventory > 0.05]
        if not candidates:
            return None
        country = self.countries[hh.country_id]
        domestic = [f for f in candidates if f.country_id == hh.country_id]
        foreign = [f for f in candidates if f.country_id != hh.country_id]
        pool = []
        if domestic:
            pool += self.rng.sample(domestic, min(12, len(domestic)))
        if foreign and self.rng.random() < 0.22 * country.border_openness:
            pool += self.rng.sample(foreign, min(6, len(foreign)))
        if not pool:
            pool = self.rng.sample(candidates, min(14, len(candidates)))
        best = None
        best_score = -1e18
        for f in pool:
            translated_theta = self.translate_angle(f.product_angle(), f.country_id, hh.country_id)
            angle_fit = cosine_compat(hh.buy_angle, translated_theta, 0.02)
            spec = GOOD_SPECS[sector]
            effective_price = f.price * (1.0 + (country.tariff_rate if f.country_id != hh.country_id else 0.0))
            gov = self.governments[country.government_id]
            sanction = gov.sanctions.get(f.id, 0.0)
            effective_price *= 1.0 + 0.8 * sanction
            utility = (f.quality ** 0.7) * (angle_fit ** spec.angle_sensitivity) / max(0.2, effective_price / spec.base_price)
            utility += 0.05 * country.sentiment_firm.get(f.id, 0.0) + triangular_noise(self.rng, 0.05)
            if utility > best_score:
                best = f
                best_score = utility
        return best

    def product_and_service_markets(self, stats: StepStats) -> None:
        # Reset household period variables.
        for hh in self.households.values():
            hh.last_consumption = 0.0
            hh.last_taxes = 0.0
        # Consumption budget: households buy essentials then optional sectors.
        for hh in self.households.values():
            if not hh.active:
                continue
            country = self.countries[hh.country_id]
            gov = self.governments[country.government_id]
            budget = max(0.0, hh.cash.amount * (1.0 - hh.savings_propensity) * self.rng.uniform(0.18, 0.38))
            if budget <= EPS:
                continue
            sectors = ESSENTIAL_SECTORS[:]
            optional = [s for s in SECTORS if s not in sectors]
            self.rng.shuffle(optional)
            sectors += optional[: self.rng.randint(3, 7)]
            spent = 0.0
            for sector in sectors:
                if spent >= budget:
                    break
                firm = self.choose_firm_for_household(hh, sector)
                if firm is None:
                    continue
                tariff = country.tariff_rate if firm.country_id != hh.country_id else 0.0
                unit_price = firm.price * (1.0 + tariff)
                desired_units = self.household_demand_units(hh, sector, unit_price)
                if desired_units <= EPS:
                    continue
                units = min(firm.inventory, desired_units, (budget - spent) / max(0.5, unit_price))
                if units <= EPS:
                    continue
                amount = units * firm.price
                ctx = self.translate_angle(firm.product_angle(), firm.country_id, hh.country_id)
                tax_rate = gov.tax_rate_consumption
                ok = self.transaction(hh, firm, amount, ctx, firm.reputation_confidence, stats, f"buy {sector}", tax_rate=tax_rate, tariff_rate=tariff, allow_black_market=True)
                if ok:
                    firm.inventory -= units
                    firm.sales += amount
                    firm.units_sold += units
                    spent += amount * (1.0 + tax_rate + tariff)
                    hh.last_consumption += amount
                    hh.welfare += self.consumption_welfare(hh, firm, units, unit_price)
                    stats.consumer_sales += amount
                else:
                    break

    def consumption_welfare(self, hh: Household, f: Firm, units: float, price: float) -> float:
        spec = GOOD_SPECS[f.sector]
        theta = self.translate_angle(f.product_angle(), f.country_id, hh.country_id)
        angle_fit = cosine_compat(hh.buy_angle, theta, 0.03)
        return units * spec.essentiality * f.quality * (0.5 + 0.5 * angle_fit) / max(0.5, price / spec.base_price)

    # ------------------------------------------------------------------
    # Taxes, subsidies, public spending, angle market, legal system
    # ------------------------------------------------------------------
    def taxes_subsidies_and_public_spending(self, stats: StepStats) -> None:
        for country in self.countries.values():
            gov = self.governments[country.government_id]
            # Corporate profit tax.
            for f in self.firms.values():
                if f.country_id != country.id or not f.active:
                    continue
                f.profit = f.sales - f.costs
                if f.profit > EPS:
                    tax = f.profit * gov.tax_rate_profit
                    if self.transaction(f, gov, tax, f.reputation_theta, f.reputation_confidence, stats, "profit-tax", allow_black_market=False):
                        f.profit -= tax
            # Unemployment benefits and public sector purchases.
            unemployed = [hh for hh in self.households.values() if hh.country_id == country.id and hh.employer_id is None]
            benefit_per = clamp(8.0 + 0.004 * gov.cash.amount / max(1, len(unemployed) + 1), 4.0, 55.0)
            for hh in self.rng.sample(unemployed, min(len(unemployed), max(1, int(0.7 * len(unemployed))))):
                if gov.cash.amount <= benefit_per:
                    break
                theta = angle_blend(gov.reputation_theta, country.currency_theta, 0.45)
                if self.transaction(gov, hh, benefit_per, theta, gov.reputation_confidence, stats, "unemployment-benefit", allow_black_market=False):
                    stats.subsidies += benefit_per
                    hh.welfare += benefit_per / 20.0
            # Subsidies to high-good/low-popularity firms and infrastructure sectors.
            candidates = []
            for f in self.firms.values():
                if f.country_id != country.id or not f.active:
                    continue
                moral = gov.moral_memory.get(f.id, f.current_goodness_estimate())
                pop, _ = self.people_popularity_score(country, f)
                if moral > 0.30 and (pop < 0.05 or f.sector in ("health", "education", "food", "energy", "housing")):
                    candidates.append((moral - pop + GOOD_SPECS[f.sector].essentiality * 0.2, f))
            candidates.sort(reverse=True, key=lambda x: x[0])
            budget = min(gov.cash.amount * 0.05, 5000.0)
            for _, f in candidates[:8]:
                if budget <= 0:
                    break
                subsidy = min(budget, self.rng.uniform(80.0, 450.0))
                ctx = angle_from_axes(max(0.05, gov.moral_memory.get(f.id, 0.0)), self.people_popularity_score(country, f)[0])
                if self.transaction(gov, f, subsidy, ctx, gov.reputation_confidence, stats, "public-subsidy", allow_black_market=False):
                    budget -= subsidy
                    stats.subsidies += subsidy
                    f.compliance = clamp(f.compliance + 0.01, 0.0, 1.0)
            # Public procurement creates demand.
            procurement_budget = min(gov.cash.amount * 0.04, 3000.0)
            procure_sectors = ["health", "education", "security", "software", "machinery", "energy", "food"]
            for sec in procure_sectors:
                if procurement_budget <= EPS:
                    break
                supplier = self.choose_supplier(country.id, sec)
                if supplier is None:
                    continue
                spend = min(procurement_budget, supplier.price * self.rng.uniform(4.0, 20.0), supplier.inventory * supplier.price)
                if spend <= EPS:
                    continue
                tariff = country.tariff_rate if supplier.country_id != country.id else 0.0
                ctx = supplier.product_angle()
                if self.transaction(gov, supplier, spend, ctx, supplier.reputation_confidence, stats, "public-procurement", tax_rate=0.0, tariff_rate=tariff, allow_black_market=False):
                    units = spend / max(0.5, supplier.price)
                    supplier.inventory = max(0.0, supplier.inventory - units)
                    supplier.sales += spend
                    supplier.units_sold += units
                    procurement_budget -= spend
                    stats.consumer_sales += spend

    def angle_market(self, stats: StepStats) -> None:
        # Actors quote buy/sell angle. Large spreads reduce liquidity. Rotation costs are paid to market makers/banks.
        actors: List[ActorBase] = []
        actors.extend(self.households.values())
        actors.extend(self.firms.values())
        actors.extend(self.banks.values())
        actors.extend(self.governments.values())
        for a in actors:
            if not a.active or a.cash.amount <= 50.0:
                continue
            spread = angle_dist(a.buy_angle, a.sell_angle)
            # Desired direction is between buy and sell angle, biased by reputation.
            desired = angle_mean(((a.buy_angle, 0.35), (a.sell_angle, 0.35), (a.reputation_theta, 0.30)))[0]
            d = angle_dist(a.cash.theta, desired)
            if d < 0.25:
                continue
            p_rotate = clamp(0.02 + 0.10 * d / math.pi + 0.05 * spread / math.pi, 0.0, 0.35)
            if isinstance(a, Firm) and a.sanctioned:
                p_rotate += 0.10
            if self.rng.random() > p_rotate:
                continue
            amount_fraction = clamp(0.05 + 0.20 * d / math.pi, 0.02, 0.25)
            # Because cash is aggregated, rotate the aggregate partially by blending to an intermediate target.
            target = angle_blend(a.cash.theta, desired, amount_fraction)
            friction = 0.020 + 0.080 * (1.0 - a.reputation_confidence)
            if isinstance(a, Firm):
                # High transparency/compliance makes legitimate rotation cheaper; fraud makes it look like laundering.
                friction *= (1.35 - 0.45 * a.compliance + 0.55 * a.fraud_level)
            before = a.cash.amount
            lost = a.cash.rotate_to(target, friction, self.t, "angle-market-rotation")
            stats.angle_rotation_volume += before * amount_fraction
            stats.angle_rotation_cost += lost
            # Market makers/banks receive some fees.
            if lost > EPS:
                banks = [b for b in self.banks.values() if b.country_id == a.country_id and b.active]
                if banks:
                    b = self.rng.choice(banks)
                    b.receive(VectorMoney(lost * 0.35, target, max(0.05, a.cash.confidence * 0.7), "angle-market-fee", []), self.t, "angle market fee")
            if isinstance(a, Firm):
                true_improvement = max(0.0, a.compliance + a.transparency - a.fraud_level - 0.7)
                laundering = (d / math.pi) * max(0.0, 0.8 - true_improvement) * amount_fraction
                stats.laundering_index += laundering
                if laundering > 0.05:
                    # Bad rotations lower confidence and may trigger future scandals.
                    a.reputation_confidence = clamp(a.reputation_confidence * (1.0 - 0.05 * laundering), 0.02, 1.0)

    def legal_system_and_audits(self, stats: StepStats) -> None:
        # Courts/auditors detect fraud, impose fines, and can rehabilitate firms with verified compliance.
        for country in self.countries.values():
            gov = self.governments[country.government_id]
            audit_capacity = max(1, int(country.legal_quality * 4 + country.media_freedom * 3))
            domestic = [f for f in self.firms.values() if f.country_id == country.id and f.active]
            if not domestic:
                continue
            # Prioritize sanctioned, large, low-confidence, or high-fraud firms.
            scored = []
            for f in domestic:
                risk = f.fraud_level * 0.6 + (1.0 - f.transparency) * 0.25 + gov.sanctions.get(f.id, 0.0) * 0.4 + f.market_power * 0.15
                scored.append((risk + triangular_noise(self.rng, 0.05), f))
            scored.sort(reverse=True, key=lambda x: x[0])
            for _, f in scored[:audit_capacity]:
                detection = country.legal_quality * gov.court_independence * (0.35 + 0.65 * f.fraud_level) * (0.5 + 0.5 * f.transparency)
                if self.rng.random() < detection:
                    fine = min(f.cash.amount * 0.35, f.sales * (0.05 + 0.45 * f.fraud_level) + 100.0)
                    if fine > EPS:
                        self.transaction(f, gov, fine, rad(185.0), 0.55, stats, "legal-fine", allow_black_market=False)
                    f.fraud_level = clamp(f.fraud_level * (0.70 - 0.25 * country.legal_quality), 0.0, 1.0)
                    f.compliance = clamp(f.compliance + 0.08 * country.legal_quality, 0.0, 1.0)
                    f.transparency = clamp(f.transparency + 0.04 * country.legal_quality, 0.0, 1.0)
                    f.reputation_theta = angle_blend(f.reputation_theta, rad(170.0), 0.08)
                    f.reputation_confidence = clamp(f.reputation_confidence + 0.04 * country.legal_quality, 0.02, 1.0)
                    self.events.append(Event(self.t, country.id, "audit_fine", min(1.0, fine / 1000.0), f"Audit fine for {f.name}", f.id))
                elif f.compliance > 0.75 and f.transparency > 0.7 and self.rng.random() < country.legal_quality * 0.20:
                    # Rehabilitation: courts can improve confidence and reduce sanctions.
                    f.reputation_confidence = clamp(f.reputation_confidence + 0.03, 0.02, 1.0)
                    f.reputation_theta = angle_blend(f.reputation_theta, angle_from_axes(0.75, 0.20), 0.025)
                    if f.id in gov.sanctions:
                        gov.sanctions[f.id] *= 0.85

    # ------------------------------------------------------------------
    # Reputations, environment, prices, politics
    # ------------------------------------------------------------------
    def update_reputations(self, stats: StepStats) -> None:
        for f in self.firms.values():
            if not f.active:
                continue
            country = self.countries[f.country_id]
            gov = self.governments[country.government_id]
            moral = gov.moral_memory.get(f.id, f.current_goodness_estimate())
            moral_uncert = gov.uncertainty_memory.get(f.id, 0.4)
            pop, pop_uncert = self.people_popularity_score(country, f)
            new_theta = angle_from_axes(moral, pop)
            # Revenue and employment give weight to reputation changes.
            weight = clamp(0.03 + 0.06 * math.log1p(f.sales) / 8.0 + 0.03 * len(f.employees) / max(1, f.target_employees + 3), 0.02, 0.16)
            f.reputation_theta = angle_blend(f.reputation_theta, new_theta, weight)
            agreement = 1.0 - clamp((moral_uncert + pop_uncert) / 2.0, 0.0, 1.0)
            f.reputation_confidence = clamp(0.94 * f.reputation_confidence + 0.06 * agreement, 0.02, 1.0)
            # Buy/sell angles adapt: firms sell near product/reputation, buy near supply chain/currency.
            f.sell_angle = angle_blend(f.sell_angle, f.reputation_theta, 0.08)
            f.buy_angle = angle_blend(f.buy_angle, angle_mean(((f.supply_chain_theta, 0.5), (country.currency_theta, 0.5)))[0], 0.05)
        for hh in self.households.values():
            country = self.countries[hh.country_id]
            group = country.people_groups[hh.group_id]
            # Values shift slowly under media and lived welfare.
            pop_environment = sum(country.sentiment_sector.get(s, 0.0) for s in SECTORS) / len(SECTORS)
            welfare_signal = clamp((hh.last_consumption + hh.last_income) / 900.0 - 0.5, -1.0, 1.0)
            target = angle_blend(group.ideology_theta, angle_from_axes(welfare_signal, pop_environment), 0.20 * hh.political_attention)
            hh.buy_angle = angle_blend(hh.buy_angle, target, 0.025)
            hh.sell_angle = angle_blend(hh.sell_angle, target, 0.018)
            hh.reputation_theta = angle_blend(hh.reputation_theta, angle_mean(((hh.buy_angle, 0.5), (hh.sell_angle, 0.5)))[0], 0.05)
            hh.reputation_confidence = clamp(0.995 * hh.reputation_confidence + 0.005 * country.currency_confidence, 0.02, 1.0)
        for b in self.banks.values():
            if not b.active:
                continue
            defaults = sum(1 for lid in b.loans if self.loans.get(lid) and self.loans[lid].defaulted)
            total = max(1, len(b.loans))
            health = clamp(b.capital / max(1.0, b.capital + abs(b.shadow_exposure) * 1000.0), 0.0, 1.0)
            x = 0.6 * health - 0.9 * defaults / total
            y = 0.2 - 0.4 * defaults / total + 0.2 * math.log1p(max(0.0, b.capital)) / 12.0
            b.reputation_theta = angle_blend(b.reputation_theta, angle_from_axes(x, y), 0.05)
            b.reputation_confidence = clamp(0.97 * b.reputation_confidence + 0.03 * health, 0.02, 1.0)

    def environment_feedback(self, stats: StepStats) -> None:
        for country in self.countries.values():
            # Pollution decays slowly but damages productivity, health, and popularity of harmful sectors.
            country.pollution = clamp(country.pollution * 0.995, 0.0, 3.0)
            if country.pollution > 0.6:
                harm = (country.pollution - 0.6) * 0.02
                for sec in ("energy", "raw_materials", "transport", "luxury"):
                    country.sentiment_sector[sec] = clamp(country.sentiment_sector.get(sec, 0.0) - harm, -1.0, 1.0)
                for sec in ("health", "housing", "food"):
                    country.sentiment_sector[sec] = clamp(country.sentiment_sector.get(sec, 0.0) + 0.5 * harm, -1.0, 1.0)

    def firm_pricing_and_survival(self, stats: StepStats) -> None:
        by_country_sector_prices: Dict[Tuple[int, str], List[float]] = defaultdict(list)
        for f in self.firms.values():
            if f.active:
                by_country_sector_prices[(f.country_id, f.sector)].append(f.price)
        for f in self.firms.values():
            if not f.active:
                continue
            spec = GOOD_SPECS[f.sector]
            # Adaptive pricing: stockouts raise price; excess inventory lowers price. Market power dampens downward adjustment.
            demand = max(1.0, f.units_sold)
            inv_ratio = f.inventory / max(1.0, demand)
            if inv_ratio < 0.7:
                f.price *= 1.0 + 0.025 * (1.0 - inv_ratio) * (1.0 + f.market_power)
            elif inv_ratio > 3.0:
                f.price *= 1.0 - 0.018 * min(2.0, inv_ratio - 3.0) * (1.0 - 0.5 * f.market_power)
            # Costs and sanctions matter.
            margin_signal = f.profit / max(1.0, f.sales)
            f.price *= 1.0 + clamp(-margin_signal, -0.02, 0.035)
            if f.sanctioned:
                f.price *= 1.0 + 0.015
            f.price = clamp(f.price, spec.base_price * 0.25, spec.base_price * 6.0)
            # Wage adaptation.
            if len(f.employees) < f.target_employees:
                f.wage_offer *= 1.0 + 0.015
            elif f.cash.amount < len(f.employees) * f.wage_offer * 0.6:
                f.wage_offer *= 0.985
            f.wage_offer = clamp(f.wage_offer, 2.0, spec.base_price * 20.0)
            # Tech and innovation: reinvest some profit.
            if f.profit > 100.0:
                reinvest = min(f.profit * 0.10, f.cash.amount * 0.05)
                if f.pay_amount(reinvest):
                    f.technology = clamp(f.technology + 0.0004 * reinvest * (1.0 + f.patents), 0.20, 4.5)
                    f.quality = clamp(f.quality + 0.00015 * reinvest, 0.10, 3.5)
                    f.equity += reinvest * 0.65
            # Failures/defaults.
            if f.cash.amount < 5.0 and f.debt > max(1500.0, f.equity * 1.2):
                p_fail = clamp(0.08 + 0.20 * f.debt / max(1.0, f.equity + 1000.0), 0.0, 0.85)
                if self.rng.random() < p_fail:
                    f.active = False
                    f.defaulted = True
                    stats.firms_defaulted += 1
                    for hid in list(f.employees):
                        hh = self.households.get(hid)
                        if hh:
                            hh.employer_id = None
                    f.employees.clear()
                    self.events.append(Event(self.t, f.country_id, "firm_bankruptcy", min(1.0, f.debt / 10000.0), f"{f.name} bankrupt", f.id))
            # Expected demand smoothing.
            f.expected_demand = max(0.5, 0.86 * f.expected_demand + 0.14 * f.units_sold)
            # Advertising/lobbying budgets adapt to profit and fear.
            if f.profit > 0:
                f.advertising_budget = clamp(0.90 * f.advertising_budget + 0.10 * min(900.0, f.profit * (0.05 + 0.08 * f.market_power)), 0.0, 1500.0)
                f.lobbying_budget = clamp(0.94 * f.lobbying_budget + 0.06 * min(700.0, f.profit * (0.03 + 0.12 * f.market_power)), 0.0, 1200.0)
            else:
                f.advertising_budget *= 0.96
                f.lobbying_budget *= 0.96

    def elections_and_politics(self, stats: StepStats) -> None:
        for country in self.countries.values():
            gov = self.governments[country.government_id]
            households = [h for h in self.households.values() if h.country_id == country.id]
            if households:
                avg_welfare = sum(h.welfare for h in households) / max(1, len(households))
                avg_income = sum(h.last_income for h in households) / max(1, len(households))
                unemployment = sum(1 for h in households if h.employer_id is None) / max(1, len(households))
                legitimacy_signal = logistic((avg_welfare / 30.0) + (avg_income / 700.0) - 1.0 - 1.5 * unemployment - 1.2 * country.inflation)
            else:
                legitimacy_signal = 0.5
            # Group anger/polarization.
            group_scores = []
            for g in country.people_groups:
                gs = [h for h in households if h.group_id == g.id]
                if gs:
                    sat = sum(h.welfare + 0.004 * h.cash.amount for h in gs) / len(gs)
                    g.current_satisfaction = 0.92 * g.current_satisfaction + 0.08 * sat
                    g.anger = clamp(0.95 * g.anger + 0.05 * (1.0 - legitimacy_signal) * g.activism, 0.0, 1.0)
                    group_scores.append(g.current_satisfaction)
            if len(group_scores) >= 2:
                mean = sum(group_scores) / len(group_scores)
                var = sum((x - mean) ** 2 for x in group_scores) / len(group_scores)
                country.polarization = clamp(math.sqrt(var) / 10.0 + sum(g.anger * g.weight for g in country.people_groups) * 0.25, 0.0, 1.0)
            country.protests = clamp(sum(g.anger * g.weight * g.activism for g in country.people_groups), 0.0, 1.0)
            gov.legitimacy = clamp(0.94 * gov.legitimacy + 0.06 * legitimacy_signal - 0.03 * country.protests, 0.0, 1.0)
            # Election cycle: low legitimacy causes ideology/policy change.
            country.election_timer -= 1
            if country.election_timer <= 0:
                country.election_timer = self.rng.randint(20, 36)
                if gov.legitimacy < 0.46 or country.protests > 0.45:
                    # Swing toward weighted people ideology; corruption may or may not fall.
                    people_theta, conc = angle_mean((g.ideology_theta, g.weight * (1.0 + g.anger)) for g in country.people_groups)
                    gov.ideology_theta = angle_blend(gov.ideology_theta, people_theta, 0.35 + 0.30 * country.protests)
                    gov.competence = clamp(gov.competence + triangular_noise(self.rng, 0.10), 0.25, 0.95)
                    gov.corruption = clamp(gov.corruption + triangular_noise(self.rng, 0.08) - 0.03 * country.media_freedom, 0.0, 0.70)
                    gov.tax_rate_income = clamp(gov.tax_rate_income + triangular_noise(self.rng, 0.04), 0.02, 0.45)
                    gov.tax_rate_profit = clamp(gov.tax_rate_profit + triangular_noise(self.rng, 0.05), 0.02, 0.55)
                    gov.reputation_confidence = clamp(gov.reputation_confidence * (0.85 + 0.15 * conc), 0.02, 1.0)
                    self.events.append(Event(self.t, country.id, "government_change", 1.0 - gov.legitimacy, f"Election changes {country.name}"))
                else:
                    gov.legitimacy = clamp(gov.legitimacy + 0.04, 0.0, 1.0)
            # Reset household welfare slowly, not completely.
            for h in households:
                h.welfare *= 0.88
                h.last_income = 0.0

    # ------------------------------------------------------------------
    # Metrics and output
    # ------------------------------------------------------------------
    def recompute_country_price_indices(self, initial: bool = False) -> None:
        for country in self.countries.values():
            old = country.price_index
            weights_sum = 0.0
            idx = 0.0
            for sec, spec in GOOD_SPECS.items():
                prices = [f.price for f in self.firms.values() if f.active and f.country_id == country.id and f.sector == sec]
                if not prices:
                    continue
                avg_price = sum(prices) / len(prices)
                weight = spec.essentiality + 0.15 * spec.income_elasticity
                idx += weight * (avg_price / spec.base_price)
                weights_sum += weight
                self.price_history[(country.id, sec)].append(avg_price)
            if weights_sum > EPS:
                country.price_index = idx / weights_sum
            if initial:
                country.previous_price_index = country.price_index
                country.inflation = 0.0
            else:
                country.inflation = (country.price_index / max(EPS, country.previous_price_index) - 1.0) if country.previous_price_index > 0 else 0.0
                # Smooth monthly inflation.
                country.inflation = clamp(country.inflation, -0.50, 0.80)
                country.previous_price_index = 0.85 * country.previous_price_index + 0.15 * country.price_index
            households = [h for h in self.households.values() if h.country_id == country.id]
            if households:
                country.unemployment = sum(1 for h in households if h.employer_id is None) / len(households)
            else:
                country.unemployment = 0.0
            # Exchange rate responds to inflation, trade balance, confidence.
            country.exchange_rate *= 1.0 + clamp(-0.03 * country.trade_balance / 10000.0 - 0.03 * country.inflation + 0.01 * (country.currency_confidence - 0.7), -0.04, 0.04)
            country.exchange_rate = clamp(country.exchange_rate, 0.25, 4.0)
            country.trade_balance *= 0.92

    def world_money_angle(self) -> Tuple[float, float]:
        entries = []
        for a in list(self.households.values()) + list(self.firms.values()) + list(self.banks.values()) + list(self.governments.values()) + list(self.central_banks.values()):
            if a.active and a.cash.amount > EPS:
                entries.append((a.cash.theta, a.cash.amount * a.cash.confidence))
        return angle_mean(entries)

    def money_axes(self) -> Tuple[float, float, float]:
        theta, conc = self.world_money_angle()
        x, y = axes_from_angle(theta)
        return x * conc, y * conc, conc

    def avg_angle_spread(self) -> float:
        actors = list(self.households.values()) + list(self.firms.values()) + list(self.banks.values())
        weighted = 0.0
        total = 0.0
        for a in actors:
            if a.active:
                w = max(1.0, a.cash.amount)
                weighted += angle_dist(a.buy_angle, a.sell_angle) * w
                total += w
        return weighted / max(EPS, total)

    def angle_histogram(self, bins: int = 12) -> List[float]:
        hist = [0.0] * bins
        for a in list(self.households.values()) + list(self.firms.values()) + list(self.banks.values()) + list(self.governments.values()):
            if a.active and a.cash.amount > EPS:
                idx = int(norm_angle(a.cash.theta) / TAU * bins) % bins
                hist[idx] += a.cash.amount * a.cash.confidence
        total = sum(hist)
        if total > EPS:
            hist = [x / total for x in hist]
        return hist

    def legitimacy_gap(self) -> float:
        gaps = []
        for country in self.countries.values():
            gov = self.governments[country.government_id]
            domestic_firms = [f for f in self.firms.values() if f.country_id == country.id and f.active]
            if not domestic_firms:
                continue
            moral = sum(gov.moral_memory.get(f.id, f.current_goodness_estimate()) for f in domestic_firms) / len(domestic_firms)
            pop_vals = [self.people_popularity_score(country, f)[0] for f in self.rng.sample(domestic_firms, min(12, len(domestic_firms)))]
            pop = sum(pop_vals) / max(1, len(pop_vals))
            gaps.append(abs(moral - pop))
        return sum(gaps) / max(1, len(gaps))

    def collect_metrics(self, stats: StepStats) -> Dict[str, Any]:
        total_cash = sum(a.cash.amount for a in list(self.households.values()) + list(self.firms.values()) + list(self.banks.values()) + list(self.governments.values()) + list(self.central_banks.values()) if a.active)
        hh_cash = [h.cash.amount for h in self.households.values() if h.active]
        firm_cash = [f.cash.amount for f in self.firms.values() if f.active]
        active_firms = [f for f in self.firms.values() if f.active]
        active_banks = [b for b in self.banks.values() if b.active]
        employed = sum(1 for h in self.households.values() if h.employer_id is not None)
        unemployment = 1.0 - employed / max(1, len(self.households))
        avg_wage = 0.0
        wage_offers = [f.wage_offer for f in active_firms]
        if wage_offers:
            avg_wage = sum(wage_offers) / len(wage_offers)
        world_theta, world_conc = self.world_money_angle()
        good_axis, pop_axis, _ = self.money_axes()
        angle_vol = angle_dist(self.previous_world_angle, world_theta)
        self.previous_world_angle = world_theta
        mean_conf = statistics.mean([a.cash.confidence for a in list(self.households.values()) + active_firms + active_banks if a.active]) if (self.households or active_firms or active_banks) else 0.0
        avg_profit = statistics.mean([f.profit for f in active_firms]) if active_firms else 0.0
        avg_pollution = statistics.mean([c.pollution for c in self.countries.values()]) if self.countries else 0.0
        total_gdp = stats.consumer_sales + stats.b2b_sales
        for country in self.countries.values():
            # approximate GDP by domestic firm sales.
            country.gdp = sum(f.sales for f in active_firms if f.country_id == country.id)
        avg_inflation = statistics.mean([c.inflation for c in self.countries.values()]) if self.countries else 0.0
        avg_legitimacy = statistics.mean([self.governments[c.government_id].legitimacy for c in self.countries.values()]) if self.countries else 0.0
        avg_polarization = statistics.mean([c.polarization for c in self.countries.values()]) if self.countries else 0.0
        row: Dict[str, Any] = {
            "t": self.t,
            "gdp": round(total_gdp, 6),
            "consumer_sales": round(stats.consumer_sales, 6),
            "b2b_sales": round(stats.b2b_sales, 6),
            "wages": round(stats.wages, 6),
            "taxes": round(stats.taxes, 6),
            "subsidies": round(stats.subsidies, 6),
            "loans_issued": round(stats.loans_issued, 6),
            "loan_defaults": round(stats.loan_defaults, 6),
            "black_market_volume": round(stats.black_market_volume, 6),
            "angle_rotation_volume": round(stats.angle_rotation_volume, 6),
            "angle_rotation_cost": round(stats.angle_rotation_cost, 6),
            "laundering_index": round(stats.laundering_index, 6),
            "scandals": stats.scandals,
            "strikes": stats.strikes,
            "bank_failures": stats.bank_failures,
            "firms_defaulted": stats.firms_defaulted,
            "trade_volume": round(stats.trade_volume, 6),
            "pollution_delta": round(stats.pollution_delta, 8),
            "money_supply": round(total_cash, 6),
            "household_gini": round(gini(hh_cash), 6),
            "firm_cash_gini": round(gini(firm_cash), 6),
            "unemployment": round(unemployment, 6),
            "avg_wage_offer": round(avg_wage, 6),
            "avg_profit": round(avg_profit, 6),
            "avg_inflation": round(avg_inflation, 6),
            "avg_pollution": round(avg_pollution, 6),
            "avg_legitimacy": round(avg_legitimacy, 6),
            "avg_polarization": round(avg_polarization, 6),
            "legitimacy_gap": round(self.legitimacy_gap(), 6),
            "world_money_theta_deg": round(deg(world_theta), 6),
            "world_money_concentration": round(world_conc, 6),
            "avg_goodness_axis": round(good_axis, 6),
            "avg_popularity_axis": round(pop_axis, 6),
            "angle_volatility": round(angle_vol, 6),
            "avg_angle_spread": round(self.avg_angle_spread(), 6),
            "mean_cash_confidence": round(mean_conf, 6),
            "active_firms": len(active_firms),
            "active_banks": len(active_banks),
            "loans_active": sum(1 for l in self.loans.values() if not l.defaulted and l.outstanding > EPS),
            "loans_defaulted_total": sum(1 for l in self.loans.values() if l.defaulted),
        }
        # Add country metrics in compact columns.
        for c in self.countries.values():
            row[f"country_{c.id}_gdp"] = round(c.gdp, 6)
            row[f"country_{c.id}_inflation"] = round(c.inflation, 6)
            row[f"country_{c.id}_unemployment"] = round(c.unemployment, 6)
            row[f"country_{c.id}_legitimacy"] = round(self.governments[c.government_id].legitimacy, 6)
            row[f"country_{c.id}_pollution"] = round(c.pollution, 6)
            row[f"country_{c.id}_exchange_rate"] = round(c.exchange_rate, 6)
            row[f"country_{c.id}_protests"] = round(c.protests, 6)
        return row

    def top_events(self, n: int = 20) -> List[Dict[str, Any]]:
        events = sorted(self.events, key=lambda e: (e.t, e.severity), reverse=True)[:n]
        return [
            {"t": e.t, "country_id": e.country_id, "kind": e.kind, "severity": round(e.severity, 4), "target_id": e.target_id, "description": e.description}
            for e in events
        ]

    def final_summary(self) -> Dict[str, Any]:
        last = self.metrics[-1] if self.metrics else {}
        theta, conc = self.world_money_angle()
        firm_rank = sorted([f for f in self.firms.values()], key=lambda f: f.sales, reverse=True)[:10]
        countries = []
        for c in self.countries.values():
            gov = self.governments[c.government_id]
            countries.append({
                "id": c.id,
                "name": c.name,
                "currency": c.currency_name,
                "exchange_rate": round(c.exchange_rate, 5),
                "gdp": round(c.gdp, 4),
                "inflation": round(c.inflation, 5),
                "unemployment": round(c.unemployment, 5),
                "pollution": round(c.pollution, 5),
                "legitimacy": round(gov.legitimacy, 5),
                "protests": round(c.protests, 5),
                "currency_theta_deg": round(deg(c.currency_theta), 3),
                "currency_confidence": round(c.currency_confidence, 5),
            })
        return {
            "seed": self.seed,
            "steps": self.t,
            "last_metrics": last,
            "world_money_theta_deg": round(deg(theta), 5),
            "world_money_concentration": round(conc, 5),
            "angle_histogram_12_bins": [round(x, 6) for x in self.angle_histogram(12)],
            "countries": countries,
            "top_firms_by_sales": [
                {
                    "id": f.id,
                    "name": f.name,
                    "country_id": f.country_id,
                    "sector": f.sector,
                    "sales": round(f.sales, 4),
                    "cash": round(f.cash.amount, 4),
                    "debt": round(f.debt, 4),
                    "price": round(f.price, 4),
                    "employees": len(f.employees),
                    "reputation_theta_deg": round(deg(f.reputation_theta), 3),
                    "reputation_confidence": round(f.reputation_confidence, 5),
                    "fraud_level": round(f.fraud_level, 5),
                    "active": f.active,
                }
                for f in firm_rank
            ],
            "event_count": len(self.events),
            "top_recent_events": self.top_events(25),
        }

    def write_csv(self, path: str) -> None:
        if not self.metrics:
            return
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        # Stable field order: union in appearance order.
        fields: List[str] = []
        seen = set()
        for row in self.metrics:
            for k in row.keys():
                if k not in seen:
                    fields.append(k)
                    seen.add(k)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in self.metrics:
                writer.writerow(row)

    def write_summary(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.final_summary(), f, ensure_ascii=False, indent=2)

    def write_events(self, path: str) -> None:
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=["t", "country_id", "kind", "severity", "target_id", "description"])
            writer.writeheader()
            for e in self.events:
                writer.writerow({
                    "t": e.t,
                    "country_id": e.country_id,
                    "kind": e.kind,
                    "severity": round(e.severity, 6),
                    "target_id": e.target_id,
                    "description": e.description,
                })


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Vector currency economy simulation, PyPy3-compatible, no external dependencies.")
    p.add_argument("--steps", type=int, default=120, help="number of monthly steps")
    p.add_argument("--countries", type=int, default=3, help="number of countries")
    p.add_argument("--households", type=int, default=900, help="number of household agents")
    p.add_argument("--firms", type=int, default=120, help="number of firm agents")
    p.add_argument("--banks", type=int, default=9, help="number of bank agents")
    p.add_argument("--seed", type=int, default=42, help="random seed")
    p.add_argument("--out", default="metrics.csv", help="CSV output path")
    p.add_argument("--summary", default="summary.json", help="JSON summary output path")
    p.add_argument("--events", default="events.csv", help="event log CSV output path")
    p.add_argument("--verbose", action="store_true", help="print periodic progress")
    return p.parse_args(argv)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.countries < 1:
        raise SystemExit("--countries must be >= 1")
    if args.households < args.countries:
        raise SystemExit("--households should be at least --countries")
    if args.firms < args.countries:
        raise SystemExit("--firms should be at least --countries")
    if args.banks < 1:
        raise SystemExit("--banks must be >= 1")
    sim = VectorEconomySim(args.seed, args.countries, args.households, args.firms, args.banks, args.verbose)
    for _ in range(args.steps):
        row = sim.step()
        if args.verbose and (sim.t == 1 or sim.t % max(1, args.steps // 10) == 0 or sim.t == args.steps):
            print(
                "t={t:4d} gdp={gdp:10.2f} unemp={unemployment:.3f} infl={avg_inflation:+.3f} "
                "theta={world_money_theta_deg:7.2f} conf={mean_cash_confidence:.3f} black={black_market_volume:.2f}".format(**row)
            )
    sim.write_csv(args.out)
    sim.write_summary(args.summary)
    sim.write_events(args.events)
    if args.verbose:
        print(f"Wrote {args.out}, {args.summary}, {args.events}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
