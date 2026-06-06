#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Vector Currency Economy Simulation V5
=====================================

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
macro metrics. V2 adds explicit holding-company graphs, securities and bond
markets, an FX/capital-flow orderbook approximation, real estate, mortgages,
insurance, rating agencies, investment/pension funds, political parties,
constitutional safeguards, infrastructure, demographics, human capital,
privacy/crime/health/biodiversity ledgers, and richer adversarial dynamics.

This is not a calibrated economic model. It is a runnable research scaffold:
it contains the mechanisms, accounting interfaces, and adversarial dynamics
needed to experiment with this currency foundation.

Run:
    pypy3 vector_currency_sim.py --steps 120 --countries 3 --households 900 --firms 120 --seed 42 --out metrics.csv --summary summary.json

Dense adaptive terminal-safe color dashboard:
    pypy3 vector_currency_sim.py --steps 24 --countries 3 --households 600 --firms 120 --banks 9 --art --art-every 6 --verbose

No external packages required.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import shutil
import statistics
import unicodedata
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
    age: int = 35
    human_capital: float = 1.0
    health: float = 1.0
    dependents: int = 0
    home_property_id: Optional[int] = None
    mortgage_debt: float = 0.0
    mortgage_lender_id: Optional[int] = None
    pension_balance: float = 0.0
    insurance_policy_ids: List[int] = field(default_factory=list)
    portfolio_equity: Dict[int, float] = field(default_factory=dict)
    portfolio_bonds: List[int] = field(default_factory=list)
    data_privacy_preference: float = 0.5
    mobility: float = 0.4
    minority_status: float = 0.0


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
    parent_group_id: Optional[int] = None
    subsidiary_ids: List[int] = field(default_factory=list)
    listed: bool = False
    shares_outstanding: float = 0.0
    share_price: float = 0.0
    bond_debt: float = 0.0
    tax_haven_score: float = 0.0
    transfer_pricing_aggression: float = 0.0
    rd_budget: float = 0.0
    compute_capacity: float = 0.0
    brand_capital: float = 0.0
    real_estate_holdings: List[int] = field(default_factory=list)
    insurance_policy_ids: List[int] = field(default_factory=list)
    rating: float = 0.5
    systemic_importance: float = 0.0
    contract_reliability: float = 0.75

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
    deposits: float = 0.0
    mortgage_book: float = 0.0
    sovereign_bonds: List[int] = field(default_factory=list)
    corporate_bonds: List[int] = field(default_factory=list)
    equity_holdings: Dict[int, float] = field(default_factory=dict)
    liquidity_stress: float = 0.0


@dataclass
class InvestmentFund(ActorBase):
    assets_under_management: float = 0.0
    risk_aversion: float = 0.5
    pension_share: float = 0.5
    holdings_equity: Dict[int, float] = field(default_factory=dict)
    holdings_bonds: List[int] = field(default_factory=list)
    mandate_theta: float = 0.0
    failed: bool = False


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
    constitution_score: float = 0.7
    minority_protection: float = 0.7
    civil_rights: float = 0.7
    capital_controls: float = 0.1
    sovereign_bond_yield: float = 0.04
    public_trust: float = 0.55
    party_support: Dict[int, float] = field(default_factory=dict)
    regulatory_capture: float = 0.0
    privacy_enforcement: float = 0.5


@dataclass
class CentralBank(ActorBase):
    base_rate: float = 0.04
    inflation_target: float = 0.02
    unemployment_target: float = 0.05
    money_supply_target: float = 100000.0
    angle_policy_theta: float = 0.0
    lender_of_last_resort: float = 0.5
    qe_bias_goodness: float = 0.1
    fx_reserves: float = 50000.0
    reserve_currency_weight: float = 0.2
    macroprudential_tightness: float = 0.5


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
    housing_supply: float = 0.0
    land_price_index: float = 1.0
    infrastructure_quality: float = 0.75
    health_burden: float = 0.0
    biodiversity: float = 1.0
    crime_index: float = 0.08
    carbon_stock: float = 0.0
    data_privacy_norm: float = 0.5
    data_privacy_damage: float = 0.0
    reserve_status: float = 0.2
    capital_account_openness: float = 0.6
    human_capital_index: float = 1.0
    technology_frontier: Dict[str, float] = field(default_factory=dict)


@dataclass
class CorporateGroup:
    id: int
    name: str
    parent_firm_id: int
    subsidiary_ids: List[int]
    tax_haven_country_id: int
    control_power: float
    opacity: float
    consolidation_theta: float
    consolidation_confidence: float


@dataclass
class PropertyAsset:
    id: int
    country_id: int
    owner_kind: str
    owner_id: int
    use: str
    value: float
    rent: float
    mortgage_debt: float
    mortgage_lender_id: Optional[int]
    theta: float
    confidence: float
    condition: float = 1.0


@dataclass
class InsurancePolicy:
    id: int
    insurer_kind: str
    insurer_id: int
    holder_kind: str
    holder_id: int
    kind: str
    premium: float
    coverage: float
    theta: float
    confidence: float
    deductible: float = 0.1
    active: bool = True


@dataclass
class Bond:
    id: int
    issuer_kind: str
    issuer_id: int
    holder_kind: str
    holder_id: int
    principal: float
    coupon_rate: float
    remaining_steps: int
    theta: float
    confidence: float
    market_price: float = 1.0
    defaulted: bool = False


@dataclass
class EquityListing:
    firm_id: int
    exchange_country_id: int
    shares_outstanding: float
    free_float: float
    price: float
    theta: float
    confidence: float
    volatility: float = 0.12


@dataclass
class RatingAgency:
    id: int
    name: str
    country_id: int
    bias_theta: float
    accuracy: float
    corruption: float
    influence: float
    ratings_firm: Dict[int, float] = field(default_factory=dict)
    ratings_country: Dict[int, float] = field(default_factory=dict)


@dataclass
class PoliticalParty:
    id: int
    country_id: int
    name: str
    ideology_theta: float
    economic_policy: float
    authoritarianism: float
    support: float
    donor_firm_ids: List[int] = field(default_factory=list)


@dataclass
class TradeAgreement:
    id: int
    country_a: int
    country_b: int
    tariff_discount: float
    angle_alignment: float
    remaining_steps: int


@dataclass
class InfrastructureAsset:
    id: int
    country_id: int
    sector: str
    capacity: float
    condition: float
    owner_kind: str
    owner_id: int
    theta: float
    maintenance_need: float


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
    fx_orderbook_volume: float = 0.0
    capital_flow_volume: float = 0.0
    reserve_intervention: float = 0.0
    bond_issuance: float = 0.0
    bond_defaults: float = 0.0
    equity_issuance: float = 0.0
    equity_trading_volume: float = 0.0
    dividends: float = 0.0
    transfer_pricing_volume: float = 0.0
    tax_avoided: float = 0.0
    real_estate_rents: float = 0.0
    mortgages_issued: float = 0.0
    insurance_premiums: float = 0.0
    insurance_claims: float = 0.0
    r_and_d_spend: float = 0.0
    patent_events: int = 0
    rating_actions: int = 0
    constitutional_overrides: int = 0
    minority_harm_index: float = 0.0
    migration_count: int = 0
    infrastructure_spending: float = 0.0
    privacy_damage: float = 0.0
    health_damage: float = 0.0
    biodiversity_loss: float = 0.0
    crime_delta: float = 0.0
    contract_disputes: int = 0
    value_buy_goodness_volume: float = 0.0
    value_buy_popularity_volume: float = 0.0
    popularity_buy_goodness_volume: float = 0.0
    goodness_buy_popularity_volume: float = 0.0
    value_good_pop_exchange_fees: float = 0.0
    triadic_exchange_count: int = 0


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
        self.investment_funds: Dict[int, InvestmentFund] = {}
        self.corporate_groups: Dict[int, CorporateGroup] = {}
        self.properties: Dict[int, PropertyAsset] = {}
        self.insurance_policies: Dict[int, InsurancePolicy] = {}
        self.bonds: Dict[int, Bond] = {}
        self.equities: Dict[int, EquityListing] = {}
        self.rating_agencies: Dict[int, RatingAgency] = {}
        self.political_parties: Dict[int, PoliticalParty] = {}
        self.trade_agreements: Dict[int, TradeAgreement] = {}
        self.infrastructure_assets: Dict[int, InfrastructureAsset] = {}
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
                constitution_score=self.rng.uniform(0.35, 0.95),
                minority_protection=self.rng.uniform(0.25, 0.95),
                civil_rights=self.rng.uniform(0.30, 0.95),
                capital_controls=self.rng.uniform(0.0, 0.45),
                sovereign_bond_yield=self.rng.uniform(0.025, 0.09),
                public_trust=self.rng.uniform(0.35, 0.85),
                regulatory_capture=self.rng.uniform(0.0, 0.35),
                privacy_enforcement=self.rng.uniform(0.25, 0.95),
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
                fx_reserves=self.rng.uniform(25000.0, 120000.0),
                reserve_currency_weight=self.rng.uniform(0.05, 0.55),
                macroprudential_tightness=self.rng.uniform(0.25, 0.85),
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
                housing_supply=self.rng.uniform(0.75, 1.25),
                land_price_index=self.rng.uniform(0.75, 1.45),
                infrastructure_quality=self.rng.uniform(0.50, 0.92),
                health_burden=self.rng.uniform(0.0, 0.20),
                biodiversity=self.rng.uniform(0.65, 1.0),
                crime_index=self.rng.uniform(0.03, 0.22),
                carbon_stock=self.rng.uniform(0.0, 0.35),
                data_privacy_norm=self.rng.uniform(0.25, 0.95),
                reserve_status=self.rng.uniform(0.05, 0.50),
                capital_account_openness=self.rng.uniform(0.35, 0.95),
                human_capital_index=self.rng.uniform(0.75, 1.25),
                technology_frontier={sec: self.rng.uniform(0.75, 1.25) for sec in SECTORS},
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
                age=self.rng.randint(18, 78),
                human_capital=clamp(self.rng.lognormvariate(0.0, 0.20), 0.45, 2.2),
                health=self.rng.uniform(0.55, 1.0),
                dependents=max(0, int(self.rng.expovariate(0.75)) - 1),
                pension_balance=self.rng.uniform(0.0, 6000.0) * max(0.0, (income_factor - 0.35)),
                data_privacy_preference=self.rng.uniform(0.05, 0.95),
                mobility=self.rng.uniform(0.05, 0.95),
                minority_status=1.0 if self.rng.random() < 0.12 else 0.0,
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
                tax_haven_score=self.rng.uniform(0.0, 0.85 if sector in ("finance", "data", "software", "luxury") else 0.35),
                transfer_pricing_aggression=self.rng.uniform(0.0, 0.55 if sector in ("finance", "data", "software", "raw_materials", "luxury") else 0.25),
                rd_budget=self.rng.uniform(20.0, 900.0 if sector in ("software", "data", "machinery", "health", "energy") else 250.0),
                compute_capacity=self.rng.uniform(0.0, 5.0 if sector in ("data", "software", "media", "finance") else 0.7),
                brand_capital=self.rng.uniform(0.0, 4.0 if sector in ("luxury", "media", "entertainment", "clothing", "food") else 1.2),
                contract_reliability=self.rng.uniform(0.45, 0.98),
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
                deposits=self.rng.uniform(20000.0, 120000.0),
                mortgage_book=self.rng.uniform(0.0, 35000.0),
                liquidity_stress=self.rng.uniform(0.0, 0.18),
            )
            self.banks[bid] = bank

        # V2: explicit balance-sheet overlays: funds, holdings, property, insurance, securities, politics.
        self.generate_extended_structures()

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
    # V2 extended economy: ownership, real estate, securities, FX, insurance,
    # politics, infrastructure, externality ledgers, human capital
    # ------------------------------------------------------------------
    def all_transaction_actors(self) -> List[ActorBase]:
        actors: List[ActorBase] = []
        actors.extend(self.households.values())
        actors.extend(self.firms.values())
        actors.extend(self.banks.values())
        actors.extend(self.investment_funds.values())
        actors.extend(self.governments.values())
        actors.extend(self.central_banks.values())
        return actors

    def get_actor(self, kind: str, actor_id: int) -> Optional[ActorBase]:
        if kind == "household":
            return self.households.get(actor_id)
        if kind == "firm":
            return self.firms.get(actor_id)
        if kind == "bank":
            return self.banks.get(actor_id)
        if kind == "fund":
            return self.investment_funds.get(actor_id)
        if kind == "government":
            return self.governments.get(actor_id)
        if kind == "central_bank":
            return self.central_banks.get(actor_id)
        return None

    def random_holder(self, country_id: Optional[int] = None, prefer_institution: bool = True) -> Tuple[str, int]:
        pool: List[Tuple[str, ActorBase]] = []
        if prefer_institution:
            pool.extend(("fund", f) for f in self.investment_funds.values() if f.active and (country_id is None or f.country_id == country_id))
            pool.extend(("bank", b) for b in self.banks.values() if b.active and (country_id is None or b.country_id == country_id))
        if self.rng.random() < 0.35:
            pool.extend(("household", h) for h in self.households.values() if h.active and h.cash.amount > 500 and (country_id is None or h.country_id == country_id))
        if not pool:
            pool.extend(("bank", b) for b in self.banks.values() if b.active)
            pool.extend(("fund", f) for f in self.investment_funds.values() if f.active)
        if not pool:
            gov = next(iter(self.governments.values()))
            return "government", gov.id
        kind, actor = self.rng.choice(pool)
        return kind, actor.id

    def generate_extended_structures(self) -> None:
        # Investment/pension funds.
        for c in self.countries.values():
            for j in range(2):
                fid = self.ids()
                theta = angle_blend(c.currency_theta, random_angle(self.rng), 0.18)
                fund = InvestmentFund(
                    id=fid,
                    name=f"Fund-{c.name}-{j}",
                    country_id=c.id,
                    cash=self.make_money(self.rng.uniform(12000.0, 65000.0), theta, self.rng.uniform(0.55, 0.88), "fund-capital"),
                    buy_angle=angle_blend(theta, c.currency_theta, 0.45),
                    sell_angle=theta,
                    reputation_theta=theta,
                    reputation_confidence=self.rng.uniform(0.50, 0.90),
                    assets_under_management=self.rng.uniform(30000.0, 180000.0),
                    risk_aversion=self.rng.uniform(0.25, 0.90),
                    pension_share=self.rng.uniform(0.25, 0.85),
                    mandate_theta=angle_blend(c.currency_theta, rad(45.0), self.rng.uniform(0.15, 0.55)),
                )
                self.investment_funds[fid] = fund

        # Political parties.
        party_names = ["Labor", "Civic", "Market", "Green", "Order", "Digital", "Tradition", "Solidarity"]
        for c in self.countries.values():
            raw = [self.rng.random() + 0.2 for _ in range(3)]
            total = sum(raw)
            for k in range(3):
                pid = self.ids()
                party = PoliticalParty(
                    id=pid,
                    country_id=c.id,
                    name=f"{party_names[(c.id * 3 + k) % len(party_names)]}-{c.name}",
                    ideology_theta=random_angle(self.rng, self.governments[c.government_id].ideology_theta, math.pi * 0.75),
                    economic_policy=self.rng.uniform(-1.0, 1.0),
                    authoritarianism=self.rng.uniform(0.05, 0.95),
                    support=raw[k] / total,
                )
                self.political_parties[pid] = party
                self.governments[c.government_id].party_support[pid] = party.support

        # Rating agencies as alternative quasi-oracles.
        for j in range(max(2, min(6, len(self.countries) * 2))):
            c = self.rng.choice(list(self.countries.values()))
            rid = self.ids()
            self.rating_agencies[rid] = RatingAgency(
                id=rid,
                name=f"RatingOracle-{j}",
                country_id=c.id,
                bias_theta=random_angle(self.rng, c.currency_theta, math.pi),
                accuracy=self.rng.uniform(0.45, 0.92),
                corruption=self.rng.uniform(0.0, 0.35),
                influence=self.rng.uniform(0.25, 1.0),
            )

        # Infrastructure assets.
        infra_sectors = ["energy", "transport", "data", "health", "education", "housing", "security"]
        for c in self.countries.values():
            gov = self.governments[c.government_id]
            for sec in infra_sectors:
                iid = self.ids()
                spec = GOOD_SPECS.get(sec, GOOD_SPECS["security"])
                theta = angle_from_axes(spec.social_good - spec.environmental_harm, c.sentiment_sector.get(sec, 0.0))
                self.infrastructure_assets[iid] = InfrastructureAsset(
                    id=iid,
                    country_id=c.id,
                    sector=sec,
                    capacity=self.rng.uniform(0.65, 1.45),
                    condition=self.rng.uniform(0.45, 0.95),
                    owner_kind="government" if self.rng.random() < 0.75 else "firm",
                    owner_id=gov.id,
                    theta=theta,
                    maintenance_need=self.rng.uniform(60.0, 700.0),
                )

        # Corporate holding groups with subsidiaries and tax-haven targets.
        firms_sorted = sorted(self.firms.values(), key=lambda f: f.equity + f.cash.amount + f.market_power * 30000.0, reverse=True)
        used_children = set()
        n_groups = max(1, len(firms_sorted) // 22)
        low_tax_country = min(self.countries.values(), key=lambda c: self.governments[c.government_id].tax_rate_profit)
        for gi, parent in enumerate(firms_sorted[:n_groups]):
            candidates = [f for f in firms_sorted[n_groups:] if f.id != parent.id and f.id not in used_children and self.rng.random() < 0.25]
            self.rng.shuffle(candidates)
            children = candidates[: self.rng.randint(2, min(8, max(2, len(candidates))))] if candidates else []
            if not children:
                continue
            gid = self.ids()
            parent.subsidiary_ids = [c.id for c in children]
            parent.parent_group_id = gid
            for child in children:
                child.parent_group_id = gid
                used_children.add(child.id)
            theta, conf = angle_mean([(parent.reputation_theta, parent.cash.amount)] + [(c.reputation_theta, c.cash.amount) for c in children])
            self.corporate_groups[gid] = CorporateGroup(
                id=gid,
                name=f"Group-{parent.name}",
                parent_firm_id=parent.id,
                subsidiary_ids=[c.id for c in children],
                tax_haven_country_id=low_tax_country.id if self.rng.random() < 0.7 else self.rng.choice(list(self.countries.values())).id,
                control_power=clamp(parent.market_power + len(children) * 0.05, 0.05, 1.0),
                opacity=self.rng.uniform(0.05, 0.85),
                consolidation_theta=theta,
                consolidation_confidence=conf,
            )

        # Equity listings for larger firms.
        for f in firms_sorted[: max(5, len(firms_sorted) // 3)]:
            if self.rng.random() > 0.70 and f.market_power < 0.18:
                continue
            shares = self.rng.uniform(5000.0, 200000.0)
            equity_value = max(100.0, f.equity + f.cash.amount - f.debt)
            price = equity_value / shares
            f.listed = True
            f.shares_outstanding = shares
            f.share_price = price
            self.equities[f.id] = EquityListing(
                firm_id=f.id,
                exchange_country_id=f.country_id,
                shares_outstanding=shares,
                free_float=self.rng.uniform(0.25, 0.90),
                price=price,
                theta=f.reputation_theta,
                confidence=f.reputation_confidence,
                volatility=self.rng.uniform(0.05, 0.35),
            )
            # Seed some institutional holdings.
            holders = list(self.investment_funds.values()) + list(self.banks.values())
            for holder in self.rng.sample(holders, min(len(holders), self.rng.randint(1, 4))):
                qty = shares * self.rng.uniform(0.002, 0.025)
                if isinstance(holder, InvestmentFund):
                    holder.holdings_equity[f.id] = holder.holdings_equity.get(f.id, 0.0) + qty
                elif isinstance(holder, Bank):
                    holder.equity_holdings[f.id] = holder.equity_holdings.get(f.id, 0.0) + qty

        # Properties: owner-occupied housing plus rentals owned by firms/banks/governments.
        housing_firms = [f for f in self.firms.values() if f.sector in ("housing", "finance") and f.active]
        for c in self.countries.values():
            households = [h for h in self.households.values() if h.country_id == c.id]
            banks = [b for b in self.banks.values() if b.country_id == c.id and b.active]
            gov = self.governments[c.government_id]
            for h in households:
                if self.rng.random() < 0.46:
                    value = self.rng.uniform(35000.0, 240000.0) * c.land_price_index
                    mortgage = value * self.rng.uniform(0.0, 0.72)
                    lender = self.rng.choice(banks).id if banks and mortgage > 1000 else None
                    pid = self.ids()
                    prop = PropertyAsset(pid, c.id, "household", h.id, "home", value, value * self.rng.uniform(0.0025, 0.006), mortgage, lender, c.currency_theta, c.currency_confidence, self.rng.uniform(0.45, 1.0))
                    self.properties[pid] = prop
                    h.home_property_id = pid
                    h.mortgage_debt = mortgage
                    h.mortgage_lender_id = lender
                    if lender is not None:
                        self.banks[lender].mortgage_book += mortgage
            rental_count = max(4, int(len(households) * self.rng.uniform(0.25, 0.55)))
            possible_owners: List[Tuple[str, int]] = [("government", gov.id)]
            possible_owners += [("bank", b.id) for b in banks]
            possible_owners += [("firm", f.id) for f in housing_firms if f.country_id == c.id]
            if not possible_owners:
                possible_owners = [("government", gov.id)]
            for _ in range(rental_count):
                owner_kind, owner_id = self.rng.choice(possible_owners)
                value = self.rng.uniform(25000.0, 180000.0) * c.land_price_index
                pid = self.ids()
                prop = PropertyAsset(pid, c.id, owner_kind, owner_id, "rental", value, value * self.rng.uniform(0.003, 0.009), 0.0, None, c.currency_theta, c.currency_confidence, self.rng.uniform(0.35, 1.0))
                self.properties[pid] = prop
                owner = self.get_actor(owner_kind, owner_id)
                if isinstance(owner, Firm):
                    owner.real_estate_holdings.append(pid)
            c.housing_supply = len([p for p in self.properties.values() if p.country_id == c.id]) / max(1, len(households))

        # Insurance policies.
        insurer_candidates: List[Tuple[str, ActorBase]] = [("firm", f) for f in self.firms.values() if f.sector in ("finance", "health") and f.active]
        insurer_candidates += [("bank", b) for b in self.banks.values() if b.active]
        if insurer_candidates:
            for h in self.households.values():
                if self.rng.random() < 0.55:
                    kind, insurer = self.rng.choice(insurer_candidates)
                    pol_id = self.ids()
                    pol = InsurancePolicy(pol_id, kind, insurer.id, "household", h.id, self.rng.choice(["health", "unemployment", "property"]), self.rng.uniform(2.0, 18.0), self.rng.uniform(150.0, 2500.0), angle_blend(h.buy_angle, insurer.reputation_theta, 0.45), min(h.reputation_confidence, insurer.reputation_confidence))
                    self.insurance_policies[pol_id] = pol
                    h.insurance_policy_ids.append(pol_id)
                # Pension contributions are routed to local funds.
                local_funds = [f for f in self.investment_funds.values() if f.country_id == h.country_id]
                if local_funds and h.pension_balance > EPS:
                    fund = self.rng.choice(local_funds)
                    fund.assets_under_management += h.pension_balance
            for f in self.firms.values():
                if self.rng.random() < 0.36 and insurer_candidates:
                    kind, insurer = self.rng.choice(insurer_candidates)
                    pol_id = self.ids()
                    pol = InsurancePolicy(pol_id, kind, insurer.id, "firm", f.id, self.rng.choice(["liability", "cyber", "property", "political-risk"]), self.rng.uniform(12.0, 150.0), self.rng.uniform(800.0, 25000.0), angle_blend(f.reputation_theta, insurer.reputation_theta, 0.45), min(f.reputation_confidence, insurer.reputation_confidence))
                    self.insurance_policies[pol_id] = pol
                    f.insurance_policy_ids.append(pol_id)

        # Initial sovereign and corporate bonds.
        for c in self.countries.values():
            gov = self.governments[c.government_id]
            for _ in range(3):
                kind, hid = self.random_holder(c.id, True)
                principal = self.rng.uniform(2000.0, 18000.0)
                bid = self.ids()
                bond = Bond(bid, "government", gov.id, kind, hid, principal, gov.sovereign_bond_yield, self.rng.randint(24, 120), gov.reputation_theta, gov.reputation_confidence, market_price=self.rng.uniform(0.82, 1.05))
                self.bonds[bid] = bond
                holder = self.get_actor(kind, hid)
                if isinstance(holder, Bank):
                    holder.sovereign_bonds.append(bid)
                elif isinstance(holder, InvestmentFund):
                    holder.holdings_bonds.append(bid)
        for f in firms_sorted[: max(5, len(firms_sorted) // 4)]:
            kind, hid = self.random_holder(f.country_id, True)
            principal = self.rng.uniform(1000.0, 12000.0)
            spread = 0.03 + 0.08 * (1.0 - f.reputation_confidence) + 0.05 * f.fraud_level
            bid = self.ids()
            bond = Bond(bid, "firm", f.id, kind, hid, principal, 0.04 + spread, self.rng.randint(18, 84), f.reputation_theta, f.reputation_confidence, market_price=self.rng.uniform(0.65, 1.1))
            self.bonds[bid] = bond
            f.bond_debt += principal
            holder = self.get_actor(kind, hid)
            if isinstance(holder, Bank):
                holder.corporate_bonds.append(bid)
            elif isinstance(holder, InvestmentFund):
                holder.holdings_bonds.append(bid)

        # Trade agreements between some countries.
        country_ids = list(self.countries.keys())
        for i, a in enumerate(country_ids):
            for b in country_ids[i + 1:]:
                if self.rng.random() < 0.38:
                    aid = self.ids()
                    self.trade_agreements[aid] = TradeAgreement(aid, a, b, self.rng.uniform(0.08, 0.55), self.rng.uniform(0.05, 0.60), self.rng.randint(24, 120))
        # Guarantee that international trade has at least a minimal treaty network when multiple countries exist.
        if len(country_ids) > 1 and len(self.trade_agreements) < len(country_ids) - 1:
            existing = {(min(a.country_a, a.country_b), max(a.country_a, a.country_b)) for a in self.trade_agreements.values()}
            for a, b in zip(country_ids[:-1], country_ids[1:]):
                key = (min(a, b), max(a, b))
                if key in existing:
                    continue
                aid = self.ids()
                self.trade_agreements[aid] = TradeAgreement(aid, a, b, self.rng.uniform(0.12, 0.45), self.rng.uniform(0.10, 0.55), self.rng.randint(36, 144))
                existing.add(key)
                if len(self.trade_agreements) >= len(country_ids) - 1:
                    break

    def infrastructure_and_public_goods(self, stats: StepStats) -> None:
        by_country: Dict[int, List[InfrastructureAsset]] = defaultdict(list)
        for asset in self.infrastructure_assets.values():
            by_country[asset.country_id].append(asset)
            asset.condition = clamp(asset.condition - self.rng.uniform(0.001, 0.010) * (1.0 + self.countries[asset.country_id].pollution * 0.15), 0.02, 1.0)
        for c in self.countries.values():
            gov = self.governments[c.government_id]
            assets = by_country.get(c.id, [])
            if not assets:
                continue
            maintenance_budget = min(gov.cash.amount * 0.025, 1200.0 + 300.0 * (1.0 - c.infrastructure_quality))
            # Prioritize sectors essential to productivity.
            assets_sorted = sorted(assets, key=lambda a: (a.condition, -a.capacity))
            for asset in assets_sorted[:4]:
                if maintenance_budget <= EPS:
                    break
                spend = min(maintenance_budget, asset.maintenance_need * self.rng.uniform(0.25, 0.90))
                if spend <= EPS:
                    continue
                owner = self.get_actor(asset.owner_kind, asset.owner_id) or gov
                if self.transaction(gov, owner, spend, asset.theta, gov.reputation_confidence, stats, "infrastructure-maintenance", allow_black_market=False):
                    maintenance_budget -= spend
                    stats.infrastructure_spending += spend
                    asset.condition = clamp(asset.condition + spend / max(100.0, asset.maintenance_need) * 0.08, 0.02, 1.0)
            c.infrastructure_quality = clamp(sum(a.condition * a.capacity for a in assets) / max(EPS, sum(a.capacity for a in assets)), 0.02, 1.0)

    def fx_orderbook_and_capital_flows(self, stats: StepStats) -> None:
        # A compact FX orderbook approximation: pressures from trade balances, rates, legitimacy, reserves, and angle confidence.
        countries = list(self.countries.values())
        if len(countries) < 2:
            return
        avg_rate = statistics.mean([self.central_banks[c.central_bank_id].base_rate for c in countries])
        avg_legit = statistics.mean([self.governments[c.government_id].legitimacy for c in countries])
        total_fx = 0.0
        for c in countries:
            cb = self.central_banks[c.central_bank_id]
            gov = self.governments[c.government_id]
            rate_pull = cb.base_rate - avg_rate
            legit_pull = gov.legitimacy - avg_legit
            trade_pressure = clamp(c.trade_balance / 50000.0, -1.5, 1.5)
            confidence_pull = c.currency_confidence - 0.65
            open_factor = c.capital_account_openness * (1.0 - gov.capital_controls)
            order_imbalance = 0.22 * rate_pull + 0.12 * legit_pull + 0.08 * trade_pressure + 0.10 * confidence_pull
            noise = triangular_noise(self.rng, 0.025) * open_factor
            flow = abs(order_imbalance + noise) * (2500.0 + 0.015 * sum(h.cash.amount for h in self.households.values() if h.country_id == c.id))
            total_fx += flow
            stats.fx_orderbook_volume += flow
            stats.capital_flow_volume += flow * open_factor
            # Positive imbalance appreciates local currency; negative depreciates.
            change = clamp((order_imbalance + noise) * open_factor, -0.045, 0.045)
            # Central bank intervention buffers disorderly moves.
            intervention = 0.0
            if abs(change) > 0.018 and cb.fx_reserves > 1000.0:
                intervention = min(cb.fx_reserves * 0.015, flow * 0.25)
                cb.fx_reserves -= intervention
                stats.reserve_intervention += intervention
                change *= 0.65
            c.exchange_rate = clamp(c.exchange_rate * (1.0 + change), 0.12, 8.0)
            cb.fx_reserves = max(0.0, cb.fx_reserves + max(0.0, c.trade_balance) * 0.015)
            c.currency_confidence = clamp(c.currency_confidence + 0.006 * legit_pull - 0.003 * abs(change) - 0.004 * c.protests, 0.05, 1.0)
            c.currency_theta = angle_blend(c.currency_theta, gov.reputation_theta, 0.015 + 0.02 * max(0.0, legit_pull))
            c.trade_balance *= 0.92
            if abs(change) > 0.04 and self.rng.random() < 0.25:
                self.events.append(Event(self.t, c.id, "currency_dislocation", abs(change), f"FX orderbook gap in {c.currency_name}"))
        # Reserve currency status evolves endogenously.
        for c in countries:
            c.reserve_status = clamp(0.985 * c.reserve_status + 0.015 * (c.currency_confidence * self.governments[c.government_id].legitimacy * (1.0 / max(0.2, c.exchange_rate))), 0.0, 1.0)

    def trade_agreements_and_geopolitics(self, stats: StepStats) -> None:
        # Agreements reduce average tariffs and align angle translations; they can decay or collapse under conflict.
        discounts_by_country: Dict[int, List[float]] = defaultdict(list)
        for aid, ag in list(self.trade_agreements.items()):
            ag.remaining_steps -= 1
            a = self.countries[ag.country_a]
            b = self.countries[ag.country_b]
            discounts_by_country[a.id].append(ag.tariff_discount)
            discounts_by_country[b.id].append(ag.tariff_discount)
            # Mutual angle translation slowly aligns.
            a.angle_translation[b.id] = angle_diff_signed(a.angle_translation.get(b.id, 0.0), 0.0) * (1.0 - 0.005 * ag.angle_alignment)
            b.angle_translation[a.id] = angle_diff_signed(b.angle_translation.get(a.id, 0.0), 0.0) * (1.0 - 0.005 * ag.angle_alignment)
            conflict = abs(self.governments[a.government_id].legitimacy - self.governments[b.government_id].legitimacy) + abs(a.protests - b.protests)
            if ag.remaining_steps <= 0 or (conflict > 1.2 and self.rng.random() < 0.03):
                self.events.append(Event(self.t, None, "trade_agreement_expired", 0.3 + min(0.7, conflict / 2.0), f"Agreement {ag.id} between {a.name} and {b.name} ended"))
                del self.trade_agreements[aid]
        for c in self.countries.values():
            if discounts_by_country.get(c.id):
                avg_disc = sum(discounts_by_country[c.id]) / len(discounts_by_country[c.id])
                c.tariff_rate = clamp(c.tariff_rate * (1.0 - 0.01 * avg_disc), 0.0, 0.55)
            else:
                c.tariff_rate = clamp(c.tariff_rate * 1.001 + 0.0002 * c.protests, 0.0, 0.55)

    def securities_and_bond_markets(self, stats: StepStats) -> None:
        # Coupon payments and defaults.
        for bond in list(self.bonds.values()):
            if bond.defaulted:
                continue
            issuer = self.get_actor(bond.issuer_kind, bond.issuer_id)
            holder = self.get_actor(bond.holder_kind, bond.holder_id)
            if issuer is None or holder is None or not issuer.active or not holder.active:
                bond.defaulted = True
                stats.bond_defaults += bond.principal
                continue
            coupon = bond.principal * bond.coupon_rate / 12.0
            principal_pay = 0.0
            bond.remaining_steps -= 1
            if bond.remaining_steps <= 0:
                principal_pay = bond.principal
            due = coupon + principal_pay
            if due > EPS:
                if self.transaction(issuer, holder, due, bond.theta, bond.confidence, stats, "bond-coupon-principal", allow_black_market=False):
                    if principal_pay > EPS:
                        bond.principal = 0.0
                else:
                    bond.defaulted = True
                    stats.bond_defaults += bond.principal
                    if isinstance(issuer, Firm):
                        issuer.defaulted = True
                        issuer.reputation_theta = angle_blend(issuer.reputation_theta, rad(210.0), 0.10)
                    elif isinstance(issuer, Government):
                        issuer.legitimacy = clamp(issuer.legitimacy - 0.05, 0.0, 1.0)
                        self.countries[issuer.country_id].currency_confidence *= 0.96

        # New sovereign issuance when fiscal position is weak or infrastructure is decaying.
        for c in self.countries.values():
            gov = self.governments[c.government_id]
            issue_need = max(0.0, 6000.0 - gov.cash.amount) + max(0.0, 0.70 - c.infrastructure_quality) * 4000.0
            if issue_need > 500.0 and self.rng.random() < 0.55:
                kind, hid = self.random_holder(c.id, True)
                holder = self.get_actor(kind, hid)
                if holder is None:
                    continue
                principal = min(holder.cash.amount * 0.10, issue_need * self.rng.uniform(0.25, 0.75))
                if principal > 200.0:
                    theta = angle_blend(gov.reputation_theta, c.currency_theta, 0.35)
                    if self.transaction(holder, gov, principal, theta, gov.reputation_confidence, stats, "sovereign-bond-issue", allow_black_market=False):
                        bid = self.ids()
                        rate = gov.sovereign_bond_yield + 0.05 * (1.0 - gov.legitimacy) + 0.02 * c.inflation
                        self.bonds[bid] = Bond(bid, "government", gov.id, kind, hid, principal, clamp(rate, 0.005, 0.35), self.rng.randint(24, 120), theta, gov.reputation_confidence)
                        gov.debt += principal
                        stats.bond_issuance += principal
                        if isinstance(holder, Bank):
                            holder.sovereign_bonds.append(bid)
                        elif isinstance(holder, InvestmentFund):
                            holder.holdings_bonds.append(bid)

        # Corporate bonds/equity issuance for cash-short but viable firms.
        viable = [f for f in self.firms.values() if f.active and f.reputation_confidence > 0.25]
        for f in self.rng.sample(viable, min(len(viable), max(1, len(viable) // 8))):
            need = max(0.0, f.target_employees * f.wage_offer * 1.5 - f.cash.amount) + max(0.0, f.expected_demand - f.inventory) * f.price * 0.08
            if need <= 200.0:
                continue
            kind, hid = self.random_holder(f.country_id, True)
            holder = self.get_actor(kind, hid)
            if holder is None or holder.cash.amount < 300.0:
                continue
            if f.listed and self.rng.random() < 0.45:
                amount = min(holder.cash.amount * 0.08, need)
                if self.transaction(holder, f, amount, f.reputation_theta, f.reputation_confidence, stats, "equity-issuance", allow_black_market=False):
                    stats.equity_issuance += amount
                    eq = self.equities.get(f.id)
                    if eq:
                        new_shares = max(1.0, amount / max(0.01, eq.price))
                        eq.shares_outstanding += new_shares
                        f.shares_outstanding = eq.shares_outstanding
                        eq.price *= 0.995
                        if isinstance(holder, InvestmentFund):
                            holder.holdings_equity[f.id] = holder.holdings_equity.get(f.id, 0.0) + new_shares
                        elif isinstance(holder, Bank):
                            holder.equity_holdings[f.id] = holder.equity_holdings.get(f.id, 0.0) + new_shares
            else:
                principal = min(holder.cash.amount * 0.07, need)
                if principal > 250.0 and self.transaction(holder, f, principal, f.reputation_theta, f.reputation_confidence, stats, "corporate-bond-issue", allow_black_market=False):
                    bid = self.ids()
                    rate = 0.035 + 0.12 * (1.0 - f.rating) + 0.07 * f.fraud_level + 0.03 * (1.0 - f.reputation_confidence)
                    self.bonds[bid] = Bond(bid, "firm", f.id, kind, hid, principal, clamp(rate, 0.01, 0.55), self.rng.randint(18, 96), f.reputation_theta, f.reputation_confidence)
                    f.bond_debt += principal
                    stats.bond_issuance += principal
                    if isinstance(holder, Bank):
                        holder.corporate_bonds.append(bid)
                    elif isinstance(holder, InvestmentFund):
                        holder.holdings_bonds.append(bid)

        # Mark-to-market equity prices.
        for fid, eq in list(self.equities.items()):
            f = self.firms.get(fid)
            if f is None or not f.active:
                eq.price *= 0.75
                continue
            expected_return = 0.010 * math.tanh(f.profit / max(1000.0, f.equity)) + 0.006 * (f.reputation_confidence - 0.5) - 0.006 * f.fraud_level
            shock = triangular_noise(self.rng, eq.volatility / 12.0)
            eq.price = max(0.005, eq.price * (1.0 + expected_return + shock))
            eq.theta = angle_blend(eq.theta, f.reputation_theta, 0.08)
            eq.confidence = clamp(0.96 * eq.confidence + 0.04 * f.reputation_confidence, 0.02, 1.0)
            f.share_price = eq.price
            stats.equity_trading_volume += abs(shock) * eq.price * eq.shares_outstanding * eq.free_float * 0.03

    def corporate_transfer_pricing(self, stats: StepStats) -> None:
        for group in self.corporate_groups.values():
            parent = self.firms.get(group.parent_firm_id)
            if parent is None or not parent.active:
                continue
            parent_tax = self.governments[self.countries[parent.country_id].government_id].tax_rate_profit
            haven_tax = self.governments[self.countries[group.tax_haven_country_id].government_id].tax_rate_profit
            moved_angles: List[Tuple[float, float]] = [(parent.reputation_theta, max(1.0, parent.cash.amount))]
            for sid in group.subsidiary_ids:
                sub = self.firms.get(sid)
                if sub is None or not sub.active or sub.cash.amount < 500.0:
                    continue
                profit_proxy = max(0.0, sub.sales - sub.costs)
                aggression = clamp((sub.transfer_pricing_aggression + parent.transfer_pricing_aggression + group.opacity) / 3.0, 0.0, 1.0)
                tax_gap = max(0.0, self.governments[self.countries[sub.country_id].government_id].tax_rate_profit - min(parent_tax, haven_tax))
                amount = min(sub.cash.amount * 0.045, (profit_proxy * 0.35 + sub.sales * 0.015) * aggression * (0.5 + 3.0 * tax_gap))
                if amount <= 25.0:
                    continue
                ctx = angle_blend(sub.reputation_theta, parent.reputation_theta, 0.55)
                if self.transaction(sub, parent, amount, ctx, min(sub.reputation_confidence, parent.reputation_confidence) * (1.0 - 0.25 * group.opacity), stats, "transfer-pricing", tax_rate=0.0, allow_black_market=False):
                    stats.transfer_pricing_volume += amount
                    stats.tax_avoided += amount * tax_gap
                    stats.laundering_index += amount * aggression * group.opacity / 10000.0
                    sub.profit -= amount * tax_gap
                    moved_angles.append((ctx, amount))
            if len(moved_angles) > 1:
                group.consolidation_theta, conc = angle_mean(moved_angles)
                group.consolidation_confidence = clamp(0.90 * group.consolidation_confidence + 0.10 * conc * (1.0 - 0.25 * group.opacity), 0.02, 1.0)
                parent.reputation_theta = angle_blend(parent.reputation_theta, group.consolidation_theta, 0.025)

    def corporate_governance_and_dividends(self, stats: StepStats) -> None:
        # Listed firms distribute some profits; holding parents extract dividends.
        for f in self.firms.values():
            if not f.active or f.cash.amount < 500.0:
                continue
            payout_base = max(0.0, f.profit)
            if f.listed and payout_base > 50.0:
                payout = min(f.cash.amount * 0.035, payout_base * self.rng.uniform(0.08, 0.35))
                holders: List[Tuple[str, ActorBase, float]] = []
                for fund in self.investment_funds.values():
                    qty = fund.holdings_equity.get(f.id, 0.0)
                    if qty > 0:
                        holders.append(("fund", fund, qty))
                for bank in self.banks.values():
                    qty = bank.equity_holdings.get(f.id, 0.0)
                    if qty > 0:
                        holders.append(("bank", bank, qty))
                # add small household shareholder lottery
                if self.rng.random() < 0.35:
                    wealthy = [h for h in self.households.values() if h.cash.amount > 1000.0 and h.country_id == f.country_id]
                    if wealthy:
                        holders.append(("household", self.rng.choice(wealthy), f.shares_outstanding * 0.002))
                total_qty = sum(q for _, _, q in holders)
                for _, holder, qty in holders[:12]:
                    if payout <= EPS or total_qty <= EPS:
                        break
                    amount = payout * qty / total_qty
                    if self.transaction(f, holder, amount, f.reputation_theta, f.reputation_confidence, stats, "dividend", allow_black_market=False):
                        stats.dividends += amount
            if f.parent_group_id is not None:
                group = self.corporate_groups.get(f.parent_group_id)
                if group and f.id != group.parent_firm_id and f.profit > 100.0:
                    parent = self.firms.get(group.parent_firm_id)
                    if parent and parent.active:
                        amount = min(f.cash.amount * 0.025, f.profit * 0.20)
                        if self.transaction(f, parent, amount, group.consolidation_theta, group.consolidation_confidence, stats, "intra-group-dividend", allow_black_market=False):
                            stats.dividends += amount

    def real_estate_market(self, stats: StepStats) -> None:
        rentals_by_country: Dict[int, List[PropertyAsset]] = defaultdict(list)
        for p in self.properties.values():
            if p.use == "rental":
                rentals_by_country[p.country_id].append(p)
        for h in self.households.values():
            if not h.active:
                continue
            c = self.countries[h.country_id]
            if h.home_property_id is None:
                rentals = rentals_by_country.get(h.country_id, [])
                if rentals:
                    prop = self.rng.choice(rentals)
                    landlord = self.get_actor(prop.owner_kind, prop.owner_id)
                    rent = prop.rent * c.price_index * self.rng.uniform(0.85, 1.25)
                    if landlord and rent > EPS:
                        ok = self.transaction(h, landlord, rent, prop.theta, prop.confidence, stats, "rent", tax_rate=0.0, allow_black_market=False)
                        if ok:
                            stats.real_estate_rents += rent
                            h.welfare -= rent / max(30.0, h.last_income + 1.0)
                        else:
                            group = c.people_groups[h.group_id]
                            group.anger = clamp(group.anger + 0.015 * group.activism, 0.0, 1.0)
                            c.protests = clamp(c.protests + 0.0015, 0.0, 1.0)
                # New mortgage/home purchase for sufficiently liquid households.
                if h.cash.amount > 4000.0 and self.rng.random() < 0.002 * c.housing_supply:
                    banks = [b for b in self.banks.values() if b.country_id == h.country_id and b.active and b.reserves > 2000]
                    if banks:
                        bank = self.rng.choice(banks)
                        value = self.rng.uniform(30000.0, 160000.0) * c.land_price_index
                        down = min(h.cash.amount * 0.35, value * 0.25)
                        mortgage = max(0.0, value - down)
                        if down > 500 and h.pay_amount(down):
                            pid = self.ids()
                            self.properties[pid] = PropertyAsset(pid, h.country_id, "household", h.id, "home", value, value * 0.004, mortgage, bank.id, c.currency_theta, c.currency_confidence, self.rng.uniform(0.65, 1.0))
                            h.home_property_id = pid
                            h.mortgage_debt = mortgage
                            h.mortgage_lender_id = bank.id
                            bank.mortgage_book += mortgage
                            bank.reserves = max(0.0, bank.reserves - mortgage * 0.08)
                            stats.mortgages_issued += mortgage
            else:
                prop = self.properties.get(h.home_property_id)
                if prop is None:
                    continue
                prop.condition = clamp(prop.condition - self.rng.uniform(0.0005, 0.004), 0.05, 1.0)
                if h.mortgage_debt > EPS and h.mortgage_lender_id is not None:
                    bank = self.banks.get(h.mortgage_lender_id)
                    if bank and bank.active:
                        pay = min(h.mortgage_debt, h.mortgage_debt * (0.0025 + self.central_banks[c.central_bank_id].base_rate / 12.0))
                        if self.transaction(h, bank, pay, prop.theta, prop.confidence, stats, "mortgage-payment", allow_black_market=False):
                            h.mortgage_debt -= pay * 0.65
                            prop.mortgage_debt = h.mortgage_debt
        # Property repricing.
        for c in self.countries.values():
            local_props = [p for p in self.properties.values() if p.country_id == c.id]
            if not local_props:
                continue
            demand_pressure = (1.0 - c.unemployment) * 0.015 + c.inflation * 0.03 - max(0.0, c.housing_supply - 1.0) * 0.015
            c.land_price_index = clamp(c.land_price_index * (1.0 + demand_pressure + triangular_noise(self.rng, 0.006)), 0.25, 8.0)
            for p in self.rng.sample(local_props, min(len(local_props), 80)):
                p.value = max(1000.0, p.value * (1.0 + demand_pressure + triangular_noise(self.rng, 0.01)) * (0.995 + 0.010 * p.condition))
                p.rent = clamp(p.value * 0.0045 * (1.0 + 0.35 * max(0.0, 1.0 - c.housing_supply)), 25.0, 4000.0)

    def insurance_market(self, stats: StepStats) -> None:
        recent_events = [e for e in self.events if e.t == self.t]
        event_pressure = defaultdict(float)
        for e in recent_events:
            if e.kind in ("natural_disaster", "energy_crisis"):
                event_pressure[(e.country_id, "property")] += e.severity
            if e.kind == "cyberattack":
                event_pressure[(e.country_id, "cyber")] += e.severity
            if e.kind in ("firm_scandal", "corruption_leak"):
                event_pressure[(e.country_id, "liability")] += e.severity
            if e.kind == "war_scare":
                event_pressure[(e.country_id, "political-risk")] += e.severity
        for pol in list(self.insurance_policies.values()):
            if not pol.active:
                continue
            insurer = self.get_actor(pol.insurer_kind, pol.insurer_id)
            holder = self.get_actor(pol.holder_kind, pol.holder_id)
            if insurer is None or holder is None or not insurer.active or not holder.active:
                pol.active = False
                continue
            premium = pol.premium * (1.0 + 0.40 * max(0.0, 0.5 - pol.confidence))
            if self.transaction(holder, insurer, premium, pol.theta, pol.confidence, stats, "insurance-premium", allow_black_market=False):
                stats.insurance_premiums += premium
            else:
                pol.active = False
                continue
            claim_prob = 0.0
            if pol.kind == "health" and pol.holder_kind == "household":
                c = self.countries[holder.country_id]
                claim_prob = 0.005 + 0.025 * c.health_burden + 0.02 * max(0.0, 0.7 - getattr(holder, "health", 0.7))
            elif pol.kind == "unemployment" and pol.holder_kind == "household":
                claim_prob = 0.02 if getattr(holder, "employer_id", None) is None else 0.002
            else:
                claim_prob = 0.003 + 0.06 * event_pressure[(holder.country_id, pol.kind)]
            if self.rng.random() < clamp(claim_prob, 0.0, 0.65):
                payout = min(pol.coverage, pol.coverage * self.rng.uniform(0.12, 0.75)) * (1.0 - pol.deductible)
                if self.transaction(insurer, holder, payout, pol.theta, pol.confidence * 0.95, stats, "insurance-claim", allow_black_market=False):
                    stats.insurance_claims += payout
                else:
                    insurer.reputation_theta = angle_blend(insurer.reputation_theta, rad(205.0), 0.03)
                    insurer.reputation_confidence *= 0.99

    def r_and_d_and_innovation(self, stats: StepStats) -> None:
        sector_spillovers: Dict[Tuple[int, str], float] = defaultdict(float)
        for f in self.firms.values():
            if not f.active:
                continue
            c = self.countries[f.country_id]
            desired = min(f.cash.amount * 0.035, f.rd_budget * self.rng.uniform(0.15, 1.10))
            if desired <= 10.0:
                continue
            if f.pay_amount(desired):
                stats.r_and_d_spend += desired
                learning = math.log1p(desired / 200.0) * (0.004 + 0.006 * c.human_capital_index) * (1.0 + 0.08 * f.compute_capacity)
                f.technology = clamp(f.technology + learning * self.rng.uniform(0.4, 1.4), 0.25, 5.0)
                f.quality = clamp(f.quality + learning * self.rng.uniform(0.1, 0.9), 0.10, 3.5)
                if self.rng.random() < min(0.35, learning * 5.0 + f.patents * 0.002):
                    f.patents += 1.0
                    stats.patent_events += 1
                    self.events.append(Event(self.t, f.country_id, "patent_grant", min(1.0, learning * 5.0), f"Patent granted to {f.name}", f.id))
                if GOOD_SPECS[f.sector].environmental_harm > 0.2 and self.rng.random() < 0.35:
                    f.environmental_damage = clamp(f.environmental_damage * (1.0 - 0.01 * learning * 20.0), 0.0, 2.0)
                sector_spillovers[(f.country_id, f.sector)] += learning * (0.25 + 0.35 * c.media_freedom)
        for (cid, sec), val in sector_spillovers.items():
            c = self.countries[cid]
            c.technology_frontier[sec] = clamp(c.technology_frontier.get(sec, 1.0) + val, 0.25, 5.0)
            # Diffusion: lagging firms in the country/sector catch up a little.
            frontier = c.technology_frontier[sec]
            for f in self.firms.values():
                if f.country_id == cid and f.sector == sec and f.active and f.technology < frontier:
                    f.technology += (frontier - f.technology) * 0.004 * c.human_capital_index

    def rating_agencies_and_oracle_competition(self, stats: StepStats) -> None:
        # Rating agencies provide non-governmental evaluations that can support or contradict government oracles.
        sampled_firms = self.rng.sample(list(self.firms.values()), min(len(self.firms), max(10, len(self.firms) // 3))) if self.firms else []
        for agency in self.rating_agencies.values():
            for f in sampled_firms:
                if not f.active:
                    continue
                gov = self.governments[self.countries[f.country_id].government_id]
                fundamentals = 0.35 + 0.22 * f.current_goodness_estimate() + 0.18 * math.tanh(f.profit / max(500.0, f.equity)) + 0.18 * f.reputation_confidence - 0.22 * f.fraud_level - 0.10 * max(0.0, f.debt / max(1000.0, f.equity + f.cash.amount))
                bias = 0.08 * math.cos(angle_diff_signed(agency.bias_theta, f.reputation_theta))
                corruption_bias = agency.corruption * f.lobbying_budget / 2500.0
                noise = triangular_noise(self.rng, (1.0 - agency.accuracy) * 0.35)
                rating = clamp(fundamentals + bias + corruption_bias + noise, 0.0, 1.0)
                old = agency.ratings_firm.get(f.id, rating)
                agency.ratings_firm[f.id] = 0.82 * old + 0.18 * rating
                if abs(agency.ratings_firm[f.id] - old) > 0.08:
                    stats.rating_actions += 1
                # Market-visible rating nudges firm financing conditions and confidence.
                f.rating = clamp(0.90 * f.rating + 0.10 * agency.ratings_firm[f.id] * agency.influence, 0.0, 1.0)
                gov_score = gov.moral_memory.get(f.id, f.current_goodness_estimate())
                disagreement = abs(gov_score - (2.0 * agency.ratings_firm[f.id] - 1.0))
                if disagreement > 0.9 and self.rng.random() < agency.influence * self.countries[f.country_id].media_freedom * 0.02:
                    self.events.append(Event(self.t, f.country_id, "oracle_disagreement", min(1.0, disagreement / 2.0), f"Rating agency disputes official score for {f.name}", f.id))
            for c in self.countries.values():
                gov = self.governments[c.government_id]
                macro = 0.45 + 0.25 * gov.legitimacy + 0.15 * c.currency_confidence + 0.10 * c.infrastructure_quality - 0.15 * c.inflation - 0.12 * c.protests - 0.08 * c.debt if hasattr(c, "debt") else 0.45 + 0.25 * gov.legitimacy + 0.15 * c.currency_confidence
                macro += triangular_noise(self.rng, (1.0 - agency.accuracy) * 0.25)
                agency.ratings_country[c.id] = clamp(0.86 * agency.ratings_country.get(c.id, macro) + 0.14 * macro, 0.0, 1.0)
                gov.sovereign_bond_yield = clamp(0.02 + 0.18 * (1.0 - agency.ratings_country[c.id]) + 0.04 * c.inflation, 0.005, 0.45)

    def political_parties_constitution_and_civil_society(self, stats: StepStats) -> None:
        for c in self.countries.values():
            gov = self.governments[c.government_id]
            parties = [p for p in self.political_parties.values() if p.country_id == c.id]
            if parties:
                # Support changes with economic pain, values, media, donor influence.
                pain = clamp(c.unemployment * 1.5 + c.inflation * 2.0 + c.protests + c.health_burden * 0.5, 0.0, 2.0)
                raw_supports = []
                for p in parties:
                    group_fit = sum(g.weight * math.cos(angle_diff_signed(g.ideology_theta, p.ideology_theta)) for g in c.people_groups)
                    incumbent_fit = math.cos(angle_diff_signed(p.ideology_theta, gov.ideology_theta))
                    donor_push = 0.0
                    for f in self.firms.values():
                        if f.country_id == c.id and f.active and f.lobbying_budget > 20 and math.cos(angle_diff_signed(f.reputation_theta, p.ideology_theta)) > 0.2:
                            if self.rng.random() < min(0.12, f.lobbying_budget / 10000.0):
                                p.donor_firm_ids.append(f.id)
                            donor_push += min(0.05, f.lobbying_budget / 20000.0) * (0.5 + f.market_power)
                    authoritarian_backlash = -0.20 * p.authoritarianism * gov.civil_rights if c.media_freedom > 0.5 else 0.08 * p.authoritarianism * pain
                    support = p.support * 0.90 + 0.10 * clamp(0.35 + 0.25 * group_fit - 0.20 * pain * incumbent_fit + donor_push + authoritarian_backlash, 0.01, 1.0)
                    raw_supports.append(max(0.01, support))
                total = sum(raw_supports)
                for p, val in zip(parties, raw_supports):
                    p.support = val / total
                    gov.party_support[p.id] = p.support
                leader = max(parties, key=lambda p: p.support)
                # Even between elections, dominant party slowly pulls government ideology.
                gov.ideology_theta = angle_blend(gov.ideology_theta, leader.ideology_theta, 0.006 * (0.5 + leader.support))
                gov.regulatory_capture = clamp(0.97 * gov.regulatory_capture + 0.03 * min(1.0, sum(len(p.donor_firm_ids) for p in parties) / max(1.0, len(self.firms) * 0.05)), 0.0, 1.0)

            # Constitutional checks against arbitrary sanctioning and mass-hysteria effects.
            check_strength = gov.constitution_score * gov.court_independence * c.legal_quality * (0.5 + 0.5 * c.media_freedom)
            for fid, intensity in list(gov.sanctions.items()):
                f = self.firms.get(fid)
                if f is None:
                    continue
                evidence = 1.0 - gov.uncertainty_memory.get(fid, 0.5)
                arbitrary_risk = max(0.0, intensity - evidence) * check_strength
                if self.rng.random() < arbitrary_risk * 0.05:
                    gov.sanctions[fid] *= 0.55
                    f.sanctioned = gov.sanctions[fid] > 0.10
                    stats.constitutional_overrides += 1
                    self.events.append(Event(self.t, c.id, "constitutional_override", arbitrary_risk, f"Court reduces sanction against {f.name}", fid))
            # Civil society investigations uncover fraud when media/courts are open.
            pressure = c.media_freedom * gov.civil_rights * statistics.mean([g.activism for g in c.people_groups])
            if self.rng.random() < 0.03 * pressure:
                suspicious = [f for f in self.firms.values() if f.country_id == c.id and f.active and f.fraud_level > 0.25]
                if suspicious:
                    f = self.rng.choice(suspicious)
                    c.sentiment_firm[f.id] = clamp(c.sentiment_firm.get(f.id, 0.0) - 0.25 * pressure, -1, 1)
                    gov.moral_memory[f.id] = clamp(gov.moral_memory.get(f.id, f.current_goodness_estimate()) - 0.25 * pressure, -1, 1)
                    self.events.append(Event(self.t, c.id, "civil_society_investigation", pressure, f"Civil society investigates {f.name}", f.id))
            # Minority harm index: popularity waves can punish minorities unless rights are strong.
            minority_groups = [g for g in c.people_groups if "minor" in g.name or g.activism > 0.75]
            harm = max(0.0, c.polarization + c.protests - gov.minority_protection * 0.7 - gov.civil_rights * 0.4)
            if minority_groups:
                stats.minority_harm_index += harm / max(1, len(self.countries))
                for h in self.households.values():
                    if h.country_id == c.id and h.minority_status > 0 and self.rng.random() < harm * 0.003:
                        h.welfare -= 0.5 * harm
                        h.reputation_confidence *= 0.998

    def human_capital_demographics_and_migration(self, stats: StepStats) -> None:
        for c in self.countries.values():
            households = [h for h in self.households.values() if h.country_id == c.id and h.active]
            if households:
                c.human_capital_index = clamp(statistics.mean([h.human_capital * h.health for h in households]), 0.25, 3.0)
        for h in self.households.values():
            if not h.active:
                continue
            c = self.countries[h.country_id]
            # Age monthly with stochastic annual birthday.
            if self.rng.random() < 1.0 / 12.0:
                h.age += 1
            # Education/health consumption has persistent effects.
            education_gain = 0.0008 * sum(1 for e in self.events if e.t == self.t and e.country_id == h.country_id and e.kind == "patent_grant")
            if h.last_consumption > 0:
                education_gain += 0.0005 * GOOD_SPECS["education"].essentiality * c.infrastructure_quality
            h.human_capital = clamp(h.human_capital + education_gain - 0.0008 * max(0.0, c.health_burden - 0.25), 0.2, 3.5)
            h.health = clamp(h.health + 0.0015 * (1.0 - c.health_burden) - 0.002 * c.pollution - 0.001 * c.crime_index + triangular_noise(self.rng, 0.002), 0.05, 1.2)
            # Retirement lowers labor participation; mortality removes very old/sick agents from active economy.
            if h.age > 66 and h.employer_id is not None and self.rng.random() < 0.003 * (h.age - 65):
                f = self.firms.get(h.employer_id)
                if f and h.id in f.employees:
                    f.employees.remove(h.id)
                h.employer_id = None
            death_prob = max(0.0, (h.age - 82) * 0.0008) + max(0.0, 0.18 - h.health) * 0.004
            if self.rng.random() < death_prob:
                h.active = False
                if h.employer_id is not None and h.employer_id in self.firms:
                    try:
                        self.firms[h.employer_id].employees.remove(h.id)
                    except ValueError:
                        pass
                continue
            # Migration if another country offers much better legitimacy/jobs and borders are open.
            if self.rng.random() < 0.0015 * h.mobility * c.border_openness:
                current_score = self.governments[c.government_id].legitimacy - c.unemployment - c.crime_index - c.pollution * 0.1
                candidates = []
                for tc in self.countries.values():
                    if tc.id == c.id:
                        continue
                    score = self.governments[tc.government_id].legitimacy - tc.unemployment - tc.crime_index - tc.pollution * 0.1 - 0.2 * angle_dist(h.buy_angle, tc.currency_theta) / math.pi
                    if score > current_score + 0.15 and tc.border_openness > self.rng.random():
                        candidates.append((score, tc))
                if candidates:
                    tc = max(candidates, key=lambda x: x[0])[1]
                    h.country_id = tc.id
                    h.buy_angle = self.translate_angle(h.buy_angle, c.id, tc.id)
                    h.sell_angle = self.translate_angle(h.sell_angle, c.id, tc.id)
                    h.employer_id = None
                    stats.migration_count += 1

    def externality_ledger(self, stats: StepStats) -> None:
        # Pollution already exists; add carbon, health, biodiversity, privacy, crime, and public safety ledgers.
        by_country = defaultdict(lambda: {"carbon": 0.0, "health": 0.0, "bio": 0.0, "privacy": 0.0})
        for f in self.firms.values():
            if not f.active:
                continue
            spec = GOOD_SPECS[f.sector]
            scale = max(0.0, f.units_sold + 0.15 * f.inventory)
            by_country[f.country_id]["carbon"] += scale * (spec.energy_intensity + spec.material_intensity) * spec.environmental_harm * 0.00007
            by_country[f.country_id]["health"] += scale * max(0.0, spec.environmental_harm - 0.20) * 0.00004
            by_country[f.country_id]["bio"] += scale * max(0.0, spec.material_intensity + spec.environmental_harm - 0.65) * 0.00002
            if f.sector in ("data", "media", "software", "finance"):
                privacy_harm = scale * (1.0 - f.transparency) * (0.3 + f.data_power) * 0.00006
                by_country[f.country_id]["privacy"] += privacy_harm
        for c in self.countries.values():
            vals = by_country[c.id]
            gov = self.governments[c.government_id]
            c.carbon_stock = clamp(c.carbon_stock + vals["carbon"] - 0.0005 * c.infrastructure_quality, 0.0, 12.0)
            c.health_burden = clamp(0.985 * c.health_burden + vals["health"] + 0.002 * c.pollution + 0.001 * c.crime_index, 0.0, 3.0)
            c.biodiversity = clamp(c.biodiversity - vals["bio"] + 0.0004 * gov.civil_rights * c.infrastructure_quality, 0.0, 1.0)
            c.data_privacy_damage = clamp(0.985 * c.data_privacy_damage + vals["privacy"] * (1.0 - gov.privacy_enforcement), 0.0, 5.0)
            # Crime responds to unemployment, inequality pressure, black-market volume, and legitimacy.
            crime_change = 0.003 * c.unemployment + 0.002 * c.protests + stats.black_market_volume / max(1000000.0, len(self.households) * 1000.0) - 0.0025 * gov.legitimacy - 0.001 * c.infrastructure_quality
            c.crime_index = clamp(c.crime_index + crime_change + triangular_noise(self.rng, 0.002), 0.0, 1.0)
            stats.privacy_damage += vals["privacy"]
            stats.health_damage += vals["health"]
            stats.biodiversity_loss += vals["bio"]
            stats.crime_delta += crime_change
            if c.health_burden > 1.2 and self.rng.random() < 0.02:
                self.events.append(Event(self.t, c.id, "public_health_alert", min(1.0, c.health_burden / 2.0), f"Health burden rises in {c.name}"))

    def contracts_and_disputes(self, stats: StepStats) -> None:
        # Contract law overlay: unreliable firms generate disputes that courts may resolve or let fester.
        for f in self.rng.sample(list(self.firms.values()), min(len(self.firms), max(1, len(self.firms) // 10))):
            if not f.active:
                continue
            c = self.countries[f.country_id]
            p_dispute = 0.003 + 0.025 * (1.0 - f.contract_reliability) + 0.018 * f.fraud_level + 0.006 * c.crime_index
            if self.rng.random() < p_dispute:
                stats.contract_disputes += 1
                resolution = c.legal_quality * self.governments[c.government_id].court_independence * (1.0 - self.governments[c.government_id].corruption)
                if self.rng.random() < resolution:
                    fine = min(f.cash.amount * 0.05, self.rng.uniform(40.0, 900.0) * (1.0 - f.contract_reliability + f.fraud_level))
                    gov = self.governments[c.government_id]
                    if fine > 1.0:
                        self.transaction(f, gov, fine, f.reputation_theta, f.reputation_confidence, stats, "contract-dispute-fine", allow_black_market=False)
                    f.contract_reliability = clamp(f.contract_reliability + 0.02, 0.0, 1.0)
                else:
                    f.reputation_confidence = clamp(f.reputation_confidence * 0.985, 0.02, 1.0)
                    c.protests = clamp(c.protests + 0.0015, 0.0, 1.0)

    # ------------------------------------------------------------------
    # Simulation step
    # ------------------------------------------------------------------
    def step(self) -> Dict[str, Any]:
        self.t += 1
        stats = StepStats()
        for f in self.firms.values():
            f.reset_period()

        self.generate_shocks(stats)
        self.trade_agreements_and_geopolitics(stats)
        self.update_media_and_sentiment(stats)
        self.political_parties_constitution_and_civil_society(stats)
        self.government_oracles_and_policy(stats)
        self.rating_agencies_and_oracle_competition(stats)
        self.central_bank_policy(stats)
        self.fx_orderbook_and_capital_flows(stats)
        self.infrastructure_and_public_goods(stats)
        self.labor_market(stats)
        self.pay_wages(stats)
        self.real_estate_market(stats)
        self.human_capital_demographics_and_migration(stats)
        self.credit_market(stats)
        self.securities_and_bond_markets(stats)
        self.production_and_supply_chains(stats)
        self.product_and_service_markets(stats)
        self.loan_servicing(stats)
        self.insurance_market(stats)
        self.corporate_transfer_pricing(stats)
        self.taxes_subsidies_and_public_spending(stats)
        self.corporate_governance_and_dividends(stats)
        self.triadic_value_goodness_popularity_market(stats)
        self.angle_market(stats)
        self.contracts_and_disputes(stats)
        self.legal_system_and_audits(stats)
        self.r_and_d_and_innovation(stats)
        self.update_reputations(stats)
        self.environment_feedback(stats)
        self.externality_ledger(stats)
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
            country_infra = self.countries[f.country_id].infrastructure_quality
            shock_factor = max(0.25, (0.70 + 0.30 * country_infra) * (1.0 - self.countries[f.country_id].pollution * 0.06) * (0.85 + 0.15 * self.countries[f.country_id].human_capital_index))
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


    def triadic_value_goodness_popularity_market(self, stats: StepStats) -> None:
        """Explicit market layer for exchanging scalar value, goodness and popularity.

        The simulation already prices value (amount), goodness (government/court/audit
        axis) and popularity (people/media axis). This layer makes the exchange visible:

        * value -> goodness: compliance, worker safety, cleaner production, audits.
        * value -> popularity: advertising, service quality, community spending.
        * popularity -> goodness: a trusted brand/social mandate lowers the cost of
          real reforms and makes rehabilitation credible.
        * goodness -> popularity: verified good conduct slowly becomes socially liked,
          especially under free media and high civic attention.

        This is deliberately not a magic moral laundering machine. Fraud, low media
        freedom and low legal quality convert some spending into fees/noise and reduce
        confidence instead of true improvement.
        """
        active_firms = [f for f in self.firms.values() if f.active and not f.defaulted and f.cash.amount > 80.0]
        if not active_firms:
            return
        # Sort by economic weight so the limited exchange capacity hits important actors.
        active_firms.sort(key=lambda f: f.cash.amount + max(0.0, f.sales) + max(0.0, f.market_power * 800.0), reverse=True)
        max_participants = max(8, int(math.sqrt(len(active_firms)) * 4))
        for f in active_firms[:max_participants]:
            country = self.countries[f.country_id]
            gov = self.governments[country.government_id]
            goodness = f.current_goodness_estimate()
            popularity = self.people_popularity_score(country, f)[0]
            cash_room = max(0.0, f.cash.amount - 50.0)
            if cash_room <= EPS:
                continue

            # Bad or mediocre firms face pressure to purchase real reforms.
            reform_pressure = clamp(0.55 - goodness + 0.25 * max(0.0, -popularity) + 0.20 * country.protests, 0.0, 1.6)
            sanction_pressure = 0.55 if f.sanctioned else 0.0
            if reform_pressure + sanction_pressure > 0.10 and self.rng.random() < clamp(0.10 + 0.18 * reform_pressure, 0.05, 0.55):
                spend = min(cash_room * self.rng.uniform(0.006, 0.030), 350.0 * (0.4 + reform_pressure + sanction_pressure))
                if spend > 1.0 and f.pay_amount(spend):
                    # Real effectiveness: legal quality and transparency convert value into actual goodness.
                    effectiveness = country.legal_quality * (0.35 + 0.65 * f.transparency) * (0.55 + 0.45 * gov.court_independence)
                    fraud_drag = clamp(f.fraud_level * (0.55 + 0.45 * (1.0 - country.media_freedom)), 0.0, 0.9)
                    real_gain = (spend / 900.0) * effectiveness * (1.0 - 0.65 * fraud_drag)
                    fee = spend * clamp(0.06 + 0.30 * fraud_drag + 0.08 * gov.corruption, 0.02, 0.45)
                    f.compliance = clamp(f.compliance + 0.55 * real_gain, 0.0, 1.0)
                    f.transparency = clamp(f.transparency + 0.38 * real_gain, 0.0, 1.0)
                    f.environmental_damage = clamp(f.environmental_damage - 0.25 * real_gain, 0.0, 1.0)
                    f.fraud_level = clamp(f.fraud_level - 0.28 * real_gain * country.legal_quality, 0.0, 1.0)
                    f.reputation_confidence = clamp(f.reputation_confidence + 0.06 * real_gain - 0.04 * fraud_drag, 0.02, 1.0)
                    # Move reputation slightly toward the true product angle.
                    f.reputation_theta = angle_blend(f.reputation_theta, f.product_angle(), clamp(0.05 + 0.25 * real_gain, 0.0, 0.35))
                    stats.value_buy_goodness_volume += spend
                    stats.value_good_pop_exchange_fees += fee
                    stats.triadic_exchange_count += 1
                    if real_gain > 0.03 and self.rng.random() < min(0.25, real_gain):
                        self.events.append(Event(self.t, f.country_id, "value_bought_goodness", min(1.0, real_gain), f"{f.name} bought verified goodness via compliance/audit spending", f.id))

            # Firms can buy popularity with value. That helps sales, but not necessarily goodness.
            popularity_need = clamp(0.35 - popularity + 0.10 * f.market_power, 0.0, 1.4)
            if popularity_need > 0.05 and cash_room > 20.0 and self.rng.random() < clamp(0.08 + 0.20 * popularity_need + 0.04 * f.brand_capital, 0.05, 0.48):
                spend = min(cash_room * self.rng.uniform(0.004, 0.026), 260.0 * (0.4 + popularity_need + f.market_power))
                if spend > 1.0 and f.pay_amount(spend):
                    media_amp = 0.7 + 0.6 * country.media_freedom + 0.2 * f.media_power
                    fake_drag = clamp(f.fraud_level + max(0.0, 0.45 - f.quality), 0.0, 1.0)
                    pop_gain = (spend / 760.0) * media_amp * (1.0 - 0.35 * fake_drag)
                    f.advertising_budget = clamp(f.advertising_budget + spend * 0.55, 0.0, 1800.0)
                    f.brand_capital = clamp(f.brand_capital + 0.65 * pop_gain, 0.0, 8.0)
                    country.sentiment_firm[f.id] = clamp(country.sentiment_firm.get(f.id, 0.0) + 0.55 * pop_gain, -1.0, 1.0)
                    # Too much purchased popularity without substance reduces confidence: the art dashboard will show this split.
                    if fake_drag > 0.45:
                        f.reputation_confidence = clamp(f.reputation_confidence - 0.025 * fake_drag, 0.02, 1.0)
                        stats.laundering_index += 0.015 * fake_drag
                    stats.value_buy_popularity_volume += spend
                    stats.value_good_pop_exchange_fees += spend * clamp(0.03 + 0.16 * fake_drag, 0.02, 0.28)
                    stats.triadic_exchange_count += 1

            # Popularity can buy goodness: trusted firms can mobilize customers/employees/investors
            # to accept costly reforms without the same scalar cash burn.
            popularity = self.people_popularity_score(country, f)[0]
            goodness = f.current_goodness_estimate()
            if popularity > 0.25 and goodness < 0.75 and f.brand_capital > 0.15 and self.rng.random() < clamp(0.04 + 0.14 * popularity, 0.02, 0.30):
                social_mandate = popularity * f.brand_capital * (0.45 + 0.55 * country.media_freedom)
                mandate_gain = clamp(social_mandate / 90.0, 0.0, 0.035)
                if mandate_gain > 0.001:
                    f.brand_capital = max(0.0, f.brand_capital - 0.35 * mandate_gain)
                    f.compliance = clamp(f.compliance + 0.65 * mandate_gain, 0.0, 1.0)
                    f.transparency = clamp(f.transparency + 0.35 * mandate_gain, 0.0, 1.0)
                    f.quality = clamp(f.quality + 0.20 * mandate_gain, 0.2, 2.5)
                    stats.popularity_buy_goodness_volume += social_mandate
                    stats.triadic_exchange_count += 1

            # Goodness can buy popularity when courts/media/consumers notice verified conduct.
            goodness = f.current_goodness_estimate()
            if goodness > 0.40 and country.media_freedom > 0.35 and self.rng.random() < clamp(0.03 + 0.10 * goodness + 0.04 * f.transparency, 0.02, 0.22):
                credibility = goodness * f.transparency * country.media_freedom * (0.7 + 0.3 * gov.public_trust)
                pop_credit = clamp(credibility * 0.018, 0.0, 0.035)
                country.sentiment_firm[f.id] = clamp(country.sentiment_firm.get(f.id, 0.0) + pop_credit, -1.0, 1.0)
                f.brand_capital = clamp(f.brand_capital + 0.15 * pop_credit, 0.0, 8.0)
                stats.goodness_buy_popularity_volume += max(0.0, credibility * 25.0)
                if pop_credit > 0.01:
                    stats.triadic_exchange_count += 1

    def angle_market(self, stats: StepStats) -> None:
        # Actors quote buy/sell angle. Large spreads reduce liquidity. Rotation costs are paid to market makers/banks.
        actors: List[ActorBase] = []
        actors.extend(self.households.values())
        actors.extend(self.firms.values())
        actors.extend(self.banks.values())
        actors.extend(self.investment_funds.values())
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
        for a in list(self.households.values()) + list(self.firms.values()) + list(self.banks.values()) + list(self.investment_funds.values()) + list(self.governments.values()) + list(self.central_banks.values()):
            if a.active and a.cash.amount > EPS:
                entries.append((a.cash.theta, a.cash.amount * a.cash.confidence))
        return angle_mean(entries)

    def money_axes(self) -> Tuple[float, float, float]:
        theta, conc = self.world_money_angle()
        x, y = axes_from_angle(theta)
        return x * conc, y * conc, conc

    def avg_angle_spread(self) -> float:
        actors = list(self.households.values()) + list(self.firms.values()) + list(self.banks.values()) + list(self.investment_funds.values())
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
        for a in list(self.households.values()) + list(self.firms.values()) + list(self.banks.values()) + list(self.investment_funds.values()) + list(self.governments.values()):
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
        total_cash = sum(a.cash.amount for a in list(self.households.values()) + list(self.firms.values()) + list(self.banks.values()) + list(self.investment_funds.values()) + list(self.governments.values()) + list(self.central_banks.values()) if a.active)
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
        active_funds = [f for f in self.investment_funds.values() if f.active]
        mean_conf = statistics.mean([a.cash.confidence for a in list(self.households.values()) + active_firms + active_banks + active_funds if a.active]) if (self.households or active_firms or active_banks or active_funds) else 0.0
        avg_profit = statistics.mean([f.profit for f in active_firms]) if active_firms else 0.0
        avg_pollution = statistics.mean([c.pollution for c in self.countries.values()]) if self.countries else 0.0
        total_gdp = stats.consumer_sales + stats.b2b_sales
        for country in self.countries.values():
            # approximate GDP by domestic firm sales.
            country.gdp = sum(f.sales for f in active_firms if f.country_id == country.id)
        avg_inflation = statistics.mean([c.inflation for c in self.countries.values()]) if self.countries else 0.0
        avg_legitimacy = statistics.mean([self.governments[c.government_id].legitimacy for c in self.countries.values()]) if self.countries else 0.0
        avg_polarization = statistics.mean([c.polarization for c in self.countries.values()]) if self.countries else 0.0
        avg_infra = statistics.mean([c.infrastructure_quality for c in self.countries.values()]) if self.countries else 0.0
        avg_health_burden = statistics.mean([c.health_burden for c in self.countries.values()]) if self.countries else 0.0
        avg_biodiversity = statistics.mean([c.biodiversity for c in self.countries.values()]) if self.countries else 0.0
        avg_crime = statistics.mean([c.crime_index for c in self.countries.values()]) if self.countries else 0.0
        avg_privacy_damage = statistics.mean([c.data_privacy_damage for c in self.countries.values()]) if self.countries else 0.0
        avg_land_price = statistics.mean([c.land_price_index for c in self.countries.values()]) if self.countries else 0.0
        active_funds = [f for f in self.investment_funds.values() if f.active]
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
            "fx_orderbook_volume": round(stats.fx_orderbook_volume, 6),
            "capital_flow_volume": round(stats.capital_flow_volume, 6),
            "reserve_intervention": round(stats.reserve_intervention, 6),
            "bond_issuance": round(stats.bond_issuance, 6),
            "bond_defaults": round(stats.bond_defaults, 6),
            "equity_issuance": round(stats.equity_issuance, 6),
            "equity_trading_volume": round(stats.equity_trading_volume, 6),
            "dividends": round(stats.dividends, 6),
            "transfer_pricing_volume": round(stats.transfer_pricing_volume, 6),
            "tax_avoided": round(stats.tax_avoided, 6),
            "real_estate_rents": round(stats.real_estate_rents, 6),
            "mortgages_issued": round(stats.mortgages_issued, 6),
            "insurance_premiums": round(stats.insurance_premiums, 6),
            "insurance_claims": round(stats.insurance_claims, 6),
            "r_and_d_spend": round(stats.r_and_d_spend, 6),
            "patent_events": stats.patent_events,
            "rating_actions": stats.rating_actions,
            "constitutional_overrides": stats.constitutional_overrides,
            "minority_harm_index": round(stats.minority_harm_index, 6),
            "migration_count": stats.migration_count,
            "infrastructure_spending": round(stats.infrastructure_spending, 6),
            "privacy_damage": round(stats.privacy_damage, 8),
            "health_damage": round(stats.health_damage, 8),
            "biodiversity_loss": round(stats.biodiversity_loss, 8),
            "crime_delta": round(stats.crime_delta, 8),
            "contract_disputes": stats.contract_disputes,
            "value_buy_goodness_volume": round(stats.value_buy_goodness_volume, 6),
            "value_buy_popularity_volume": round(stats.value_buy_popularity_volume, 6),
            "popularity_buy_goodness_volume": round(stats.popularity_buy_goodness_volume, 6),
            "goodness_buy_popularity_volume": round(stats.goodness_buy_popularity_volume, 6),
            "value_good_pop_exchange_fees": round(stats.value_good_pop_exchange_fees, 6),
            "triadic_exchange_count": stats.triadic_exchange_count,
            "money_supply": round(total_cash, 6),
            "household_gini": round(gini(hh_cash), 6),
            "firm_cash_gini": round(gini(firm_cash), 6),
            "unemployment": round(unemployment, 6),
            "avg_wage_offer": round(avg_wage, 6),
            "avg_profit": round(avg_profit, 6),
            "avg_inflation": round(avg_inflation, 6),
            "avg_pollution": round(avg_pollution, 6),
            "avg_infrastructure_quality": round(avg_infra, 6),
            "avg_health_burden": round(avg_health_burden, 6),
            "avg_biodiversity": round(avg_biodiversity, 6),
            "avg_crime_index": round(avg_crime, 6),
            "avg_privacy_damage": round(avg_privacy_damage, 6),
            "avg_land_price_index": round(avg_land_price, 6),
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
            "active_funds": len(active_funds),
            "corporate_groups": len(self.corporate_groups),
            "listed_equities": len(self.equities),
            "bonds_total": len(self.bonds),
            "properties_total": len(self.properties),
            "insurance_policies_active": sum(1 for p in self.insurance_policies.values() if p.active),
            "trade_agreements": len(self.trade_agreements),
            "infrastructure_assets": len(self.infrastructure_assets),
            "rating_agencies": len(self.rating_agencies),
            "political_parties": len(self.political_parties),
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
            row[f"country_{c.id}_infrastructure"] = round(c.infrastructure_quality, 6)
            row[f"country_{c.id}_health_burden"] = round(c.health_burden, 6)
            row[f"country_{c.id}_biodiversity"] = round(c.biodiversity, 6)
            row[f"country_{c.id}_crime_index"] = round(c.crime_index, 6)
            row[f"country_{c.id}_privacy_damage"] = round(c.data_privacy_damage, 6)
            row[f"country_{c.id}_land_price_index"] = round(c.land_price_index, 6)
            row[f"country_{c.id}_reserve_status"] = round(c.reserve_status, 6)
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
                "infrastructure_quality": round(c.infrastructure_quality, 5),
                "health_burden": round(c.health_burden, 5),
                "biodiversity": round(c.biodiversity, 5),
                "crime_index": round(c.crime_index, 5),
                "privacy_damage": round(c.data_privacy_damage, 5),
                "land_price_index": round(c.land_price_index, 5),
                "reserve_status": round(c.reserve_status, 5),
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
                    "listed": f.listed,
                    "share_price": round(f.share_price, 5),
                    "rating": round(f.rating, 5),
                    "technology": round(f.technology, 5),
                    "patents": round(f.patents, 3),
                    "parent_group_id": f.parent_group_id,
                    "bond_debt": round(f.bond_debt, 4),
                    "transfer_pricing_aggression": round(f.transfer_pricing_aggression, 5),
                }
                for f in firm_rank
            ],
            "extended_counts": {
                "investment_funds": len(self.investment_funds),
                "corporate_groups": len(self.corporate_groups),
                "properties": len(self.properties),
                "insurance_policies": len(self.insurance_policies),
                "bonds": len(self.bonds),
                "equities": len(self.equities),
                "rating_agencies": len(self.rating_agencies),
                "political_parties": len(self.political_parties),
                "trade_agreements": len(self.trade_agreements),
                "infrastructure_assets": len(self.infrastructure_assets),
            },
            "top_corporate_groups": [
                {
                    "id": g.id,
                    "name": g.name,
                    "parent_firm_id": g.parent_firm_id,
                    "subsidiary_count": len(g.subsidiary_ids),
                    "tax_haven_country_id": g.tax_haven_country_id,
                    "opacity": round(g.opacity, 5),
                    "theta_deg": round(deg(g.consolidation_theta), 3),
                    "confidence": round(g.consolidation_confidence, 5),
                } for g in list(self.corporate_groups.values())[:10]
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



# ----------------------------------------------------------------------
# Colorful UTF-8 / ANSI art dashboard
# ----------------------------------------------------------------------

_ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
    "bg_red": "\033[41m",
    "bg_green": "\033[42m",
    "bg_yellow": "\033[43m",
    "bg_blue": "\033[44m",
    "bg_magenta": "\033[45m",
    "bg_cyan": "\033[46m",
}


def _c(text: str, color_name: str, enabled: bool = True, bold: bool = False) -> str:
    if not enabled:
        return text
    return (_ANSI["bold"] if bold else "") + _ANSI.get(color_name, "") + text + _ANSI["reset"]


# Dashboard width state. It is updated by render_art_dashboard() before any
# box/diagram renderer runs. All borders and fallback line wrapping use this
# value, so no rendered line should be wider than the detected terminal width
# minus the safety margin.
_ART_MAX_WIDTH = 115
_ART_MIN_WIDTH = 5
_ART_WIDTH_SAFETY = 5


def _terminal_columns(fallback: int = 120) -> int:
    try:
        return int(shutil.get_terminal_size((fallback, 24)).columns)
    except Exception:
        return fallback


def _resolve_art_width(requested: int = 0, safety: int = _ART_WIDTH_SAFETY) -> int:
    # The user requested: detect terminal capacity and subtract 5 chars.
    terminal_cols = max(1, _terminal_columns())
    terminal_safe = max(_ART_MIN_WIDTH if terminal_cols >= _ART_MIN_WIDTH else terminal_cols, terminal_cols - max(0, int(safety)))
    terminal_safe = min(terminal_cols, terminal_safe)
    try:
        requested_i = int(requested)
    except (TypeError, ValueError):
        requested_i = 0
    # A positive --art-width can make the dashboard narrower, never wider than
    # the terminal-safe limit. 0/negative means fully automatic.
    if requested_i > 0:
        return max(_ART_MIN_WIDTH, min(requested_i, terminal_safe))
    return terminal_safe


def _ansi_seq_end(s: str, i: int) -> int:
    # Supports the SGR sequences emitted by _c(), and is intentionally tolerant
    # of other ANSI CSI sequences. Returns the first index after the sequence.
    j = i + 1
    if j < len(s) and s[j] == "[":
        j += 1
        while j < len(s) and not ("@" <= s[j] <= "~"):
            j += 1
        if j < len(s):
            return j + 1
    return i + 1


def _is_reset_ansi(seq: str) -> bool:
    return seq.endswith("m") and (seq == _ANSI["reset"] or "[0m" in seq)


def _char_display_width(ch: str) -> int:
    if not ch or ch in "\r\n\t":
        return 0 if ch != "\t" else 4
    code = ord(ch)
    cat = unicodedata.category(ch)
    if cat in ("Mn", "Me", "Cf", "Cc"):
        return 0
    # Wide/fullwidth CJK and most emoji occupy two terminal cells. Ambiguous
    # box drawing remains width 1 to match typical Western terminals.
    if unicodedata.east_asian_width(ch) in ("W", "F"):
        return 2
    if 0x1F300 <= code <= 0x1FAFF:
        return 2
    return 1


def _visible_len(s: str) -> int:
    n = 0
    i = 0
    while i < len(s):
        if s[i] == "\033":
            i = _ansi_seq_end(s, i)
            continue
        n += _char_display_width(s[i])
        i += 1
    return n


def _pad(s: str, width: int) -> str:
    return s + " " * max(0, width - _visible_len(s))


def _truncate_display(s: str, max_width: int, ellipsis: str = "…") -> str:
    max_width = max(0, int(max_width))
    if _visible_len(s) <= max_width:
        return s
    ell_w = _visible_len(ellipsis)
    target = max(0, max_width - ell_w)
    out: List[str] = []
    active = ""
    used = 0
    i = 0
    while i < len(s):
        if s[i] == "\033":
            j = _ansi_seq_end(s, i)
            seq = s[i:j]
            out.append(seq)
            active = "" if _is_reset_ansi(seq) else (active + seq)
            i = j
            continue
        w = _char_display_width(s[i])
        if used + w > target:
            break
        out.append(s[i])
        used += w
        i += 1
    if active:
        out.append(_ANSI["reset"])
    out.append(ellipsis if max_width >= ell_w else "")
    return "".join(out)


def _wrap_ansi_line(s: str, max_width: int) -> List[str]:
    """Hard-wrap one ANSI/UTF-8 string by terminal-cell width.

    The wrapper never counts ANSI escape sequences as visible cells and treats
    wide Unicode characters conservatively. It prefers the last whitespace break
    inside the current line, but falls back to hard wrapping for diagrams/bars.
    """
    max_width = max(1, int(max_width))
    if s == "":
        return [""]
    lines: List[str] = []
    cur: List[str] = []
    cur_w = 0
    active = ""
    last_space_idx: Optional[int] = None
    last_space_w: Optional[int] = None
    i = 0
    while i < len(s):
        if s[i] == "\033":
            j = _ansi_seq_end(s, i)
            seq = s[i:j]
            cur.append(seq)
            active = "" if _is_reset_ansi(seq) else (active + seq)
            i = j
            continue
        ch = s[i]
        w = _char_display_width(ch)
        if ch.isspace() and ch != "\n":
            last_space_idx = len(cur)
            last_space_w = cur_w
        if ch == "\n":
            if active:
                cur.append(_ANSI["reset"])
            lines.append("".join(cur).rstrip())
            cur = [active] if active else []
            cur_w = 0
            last_space_idx = None
            last_space_w = None
            i += 1
            continue
        if cur_w + w > max_width and cur:
            if last_space_idx is not None and last_space_idx > 0 and last_space_w is not None and last_space_w > 0:
                line_parts = cur[:last_space_idx]
                rest_parts = cur[last_space_idx + 1:]
                if active:
                    line_parts.append(_ANSI["reset"])
                lines.append("".join(line_parts).rstrip())
                # Preserve active color state for whatever remained after the space.
                cur = ([active] if active else []) + rest_parts
                cur_w = max(0, _visible_len("".join(cur)))
            else:
                if active:
                    cur.append(_ANSI["reset"])
                lines.append("".join(cur).rstrip())
                cur = [active] if active else []
                cur_w = 0
            last_space_idx = None
            last_space_w = None
            continue
        cur.append(ch)
        cur_w += w
        i += 1
    if cur or not lines:
        if active:
            cur.append(_ANSI["reset"])
        lines.append("".join(cur).rstrip())
    return lines


def _wrap_lines(lines: Iterable[str], max_width: int) -> List[str]:
    out: List[str] = []
    for line in lines:
        out.extend(_wrap_ansi_line(str(line), max_width))
    return out


def _short(s: str, n: int) -> str:
    return _truncate_display(s, n)


def _val(row: Dict[str, Any], key: str, default: float = 0.0) -> float:
    try:
        return float(row.get(key, default))
    except (TypeError, ValueError):
        return default


def _fmt_num(x: float, places: int = 2) -> str:
    sign = "-" if x < 0 else ""
    x = abs(float(x))
    if x >= 1_000_000_000:
        return f"{sign}{x / 1_000_000_000:.{places}f}B"
    if x >= 1_000_000:
        return f"{sign}{x / 1_000_000:.{places}f}M"
    if x >= 1_000:
        return f"{sign}{x / 1_000:.{places}f}K"
    return f"{sign}{x:.{places}f}"


def _fmt_pct(x: float, places: int = 1, signed: bool = False) -> str:
    if signed:
        return f"{x * 100:+.{places}f}%"
    return f"{x * 100:.{places}f}%"


def _bar(value: float, max_value: float, width: int = 24, color_name: str = "cyan", color: bool = True, fill: str = "█") -> str:
    max_value = max(EPS, max_value)
    frac = clamp(value / max_value, 0.0, 1.0)
    n = int(round(frac * width))
    return _c(fill * n, color_name, color) + _c("░" * (width - n), "dim", color)


def _bar01(value: float, width: int = 24, color_name: str = "green", color: bool = True) -> str:
    return _bar(clamp(value, 0.0, 1.0), 1.0, width, color_name, color)


def _signed_bar(value: float, width: int = 31, color_pos: str = "green", color_neg: str = "red", color: bool = True) -> str:
    value = clamp(value, -1.0, 1.0)
    half = max(2, width // 2)
    if value >= 0:
        left = "░" * half
        n = int(round(value * half))
        right = _c("█" * n, color_pos, color) + _c("░" * (half - n), "dim", color)
    else:
        n = int(round(abs(value) * half))
        left = _c("░" * (half - n), "dim", color) + _c("█" * n, color_neg, color)
        right = "░" * half
    return left + _c("┊", "white", color, bold=True) + right


def _spark(values: List[float], width: int = 34, color_name: str = "cyan", color: bool = True) -> str:
    if not values:
        return _c("·" * width, "dim", color)
    vals = values[-width:]
    lo = min(vals)
    hi = max(vals)
    chars = "▁▂▃▄▅▆▇█"
    out = []
    for v in vals:
        if hi <= lo + EPS:
            idx = 3
        else:
            idx = int(round((v - lo) / (hi - lo) * (len(chars) - 1)))
        out.append(chars[clamp(idx, 0, len(chars) - 1) if isinstance(idx, int) else 0])
    return _c("".join(out), color_name, color)


def _hr(title: str, width: int = 118, color: bool = True, color_name: str = "bright_cyan") -> str:
    width = max(_ART_MIN_WIDTH, min(int(width), _ART_MAX_WIDTH))
    # Separator rows are single-line by nature; shorten only the caption, never
    # the border width. Content boxes below do true wrapping.
    caption = _truncate_display(str(title), max(1, width - 4))
    inner = f" {caption} "
    inner_w = _visible_len(inner)
    left = max(0, (width - inner_w) // 2)
    right = max(0, width - inner_w - left)
    return _c("═" * left, color_name, color, bold=True) + _c(inner, "white", color, bold=True) + _c("═" * right, color_name, color, bold=True)


def _box(title: str, lines: List[str], color: bool = True, border_color: str = "bright_blue", max_width: Optional[int] = None) -> List[str]:
    total_width = max(_ART_MIN_WIDTH, min(int(max_width or _ART_MAX_WIDTH), _ART_MAX_WIDTH))
    inner_cap = max(1, total_width - 4)  # visible width inside │ ... │
    title_parts = _wrap_ansi_line(str(title), inner_cap)
    body_parts = _wrap_lines(lines, inner_cap)
    raw_width = max([1] + [_visible_len(x) for x in title_parts + body_parts])
    raw_width = max(1, min(inner_cap, raw_width))
    top = _c("╭" + "─" * (raw_width + 2) + "╮", border_color, color)
    bot = _c("╰" + "─" * (raw_width + 2) + "╯", border_color, color)
    out: List[str] = [top]
    for idx, tline in enumerate(title_parts):
        styled = _c(tline, "white", color, bold=True) if tline else ""
        out.append(_c("│ ", border_color, color) + _pad(styled, raw_width) + _c(" │", border_color, color))
    out.append(_c("├" + "─" * (raw_width + 2) + "┤", border_color, color))
    for line in body_parts:
        out.append(_c("│ ", border_color, color) + _pad(line, raw_width) + _c(" │", border_color, color))
    out.append(bot)
    return out


def _angle_quadrant(theta: float) -> Tuple[str, str]:
    g, p = axes_from_angle(theta)
    if g >= 0.0 and p >= 0.0:
        return "gut + beliebt", "bright_green"
    if g >= 0.0 and p < 0.0:
        return "gut + unbeliebt", "yellow"
    if g < 0.0 and p >= 0.0:
        return "böse + beliebt", "bright_magenta"
    return "böse + unbeliebt", "bright_red"


def _angle_color(theta: float) -> str:
    return _angle_quadrant(theta)[1]


def _angle_label(theta: float, color: bool = True) -> str:
    q, col = _angle_quadrant(theta)
    return _c(f"{deg(theta):6.1f}° {q}", col, color, bold=True)


def _actor_stream(sim: VectorEconomySim) -> List[Tuple[str, ActorBase]]:
    actors: List[Tuple[str, ActorBase]] = []
    actors.extend(("HH", h) for h in sim.households.values() if h.active)
    actors.extend(("F", f) for f in sim.firms.values() if f.active)
    actors.extend(("B", b) for b in sim.banks.values() if b.active)
    actors.extend(("FND", f) for f in sim.investment_funds.values() if f.active)
    actors.extend(("GOV", g) for g in sim.governments.values() if g.active)
    actors.extend(("CB", cb) for cb in sim.central_banks.values() if cb.active)
    return actors


def _weighted_angle_bins(sim: VectorEconomySim, attr: str, bins: int = 12) -> List[float]:
    out = [0.0 for _ in range(bins)]
    for _, a in _actor_stream(sim):
        theta = getattr(a, attr)
        idx = int(norm_angle(theta) / TAU * bins) % bins
        out[idx] += max(0.0, a.cash.amount) * max(0.02, a.cash.confidence)
    return out


def _ascii_compass(theta: float, buy: Optional[float] = None, sell: Optional[float] = None, cash: Optional[float] = None, color: bool = True) -> List[str]:
    w, h = 43, 19
    cx, cy = w // 2, h // 2
    rx, ry = 17, 7
    grid = [[" " for _ in range(w)] for _ in range(h)]
    # axes
    for x in range(2, w - 2):
        grid[cy][x] = "─"
    for y in range(1, h - 1):
        grid[y][cx] = "│"
    grid[cy][cx] = "┼"
    # ellipse
    for deg_i in range(0, 360, 5):
        a = math.radians(deg_i)
        x = int(round(cx + rx * math.cos(a)))
        y = int(round(cy - ry * math.sin(a)))
        if 0 <= x < w and 0 <= y < h and grid[y][x] == " ":
            grid[y][x] = "·"
    # fixed labels
    label_top = "beliebt +"
    for i, ch in enumerate(label_top):
        grid[0][max(0, cx - len(label_top)//2 + i)] = ch
    label_bottom = "unbeliebt -"
    for i, ch in enumerate(label_bottom):
        grid[h-1][max(0, cx - len(label_bottom)//2 + i)] = ch
    for i, ch in enumerate("böse -"):
        grid[cy][max(0, 1 + i)] = ch
    for i, ch in enumerate("gut +"):
        grid[cy][min(w-1, w-7+i)] = ch

    points: List[Tuple[float, str, str]] = []
    if buy is not None:
        points.append((buy, "K", "bright_green"))
    if sell is not None:
        points.append((sell, "V", "bright_red"))
    if cash is not None:
        points.append((cash, "¤", "bright_yellow"))
    points.append((theta, "◎", _angle_color(theta)))
    colored: Dict[Tuple[int, int], str] = {}
    for th, ch, col in points:
        x = int(round(cx + rx * math.cos(th)))
        y = int(round(cy - ry * math.sin(th)))
        key = (x, y)
        if key in colored:
            colored[key] = _c("◆", "white", color, bold=True)
        else:
            colored[key] = _c(ch, col, color, bold=True)
    lines = []
    for y in range(h):
        row = []
        for x in range(w):
            if (x, y) in colored:
                row.append(colored[(x, y)])
            else:
                ch = grid[y][x]
                if ch in "─│┼":
                    row.append(_c(ch, "blue", color))
                elif ch == "·":
                    row.append(_c(ch, "dim", color))
                elif ch in "gut +belösiunpt-":
                    row.append(_c(ch, "white", color))
                else:
                    row.append(ch)
        lines.append("".join(row))
    lines.append("Legende: " + _c("◎ Weltwinkel", _angle_color(theta), color, True) + "  " + _c("¤ Cashwinkel", "bright_yellow", color, True) + "  " + _c("K Kaufwinkel", "bright_green", color, True) + "  " + _c("V Verkaufswinkel", "bright_red", color, True))
    return lines


def _global_representative_angles(sim: VectorEconomySim) -> Tuple[float, float, float]:
    actors = _actor_stream(sim)
    cash_angles = [(a.cash.theta, max(0.0, a.cash.amount) * max(0.02, a.cash.confidence)) for _, a in actors]
    buy_angles = [(a.buy_angle, max(1.0, a.cash.amount)) for _, a in actors]
    sell_angles = [(a.sell_angle, max(1.0, a.cash.amount)) for _, a in actors]
    cash_theta = angle_mean(cash_angles)[0] if cash_angles else 0.0
    buy_theta = angle_mean(buy_angles)[0] if buy_angles else 0.0
    sell_theta = angle_mean(sell_angles)[0] if sell_angles else 0.0
    return cash_theta, buy_theta, sell_theta


def _render_macro_panel(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    hist = sim.metrics[-36:]
    gdp_spark = _spark([_val(r, "gdp") for r in hist], 36, "bright_green", color)
    money_spark = _spark([_val(r, "money_supply") for r in hist], 36, "bright_yellow", color)
    conf_spark = _spark([_val(r, "mean_cash_confidence") for r in hist], 36, "bright_cyan", color)
    good_spark = _spark([_val(r, "avg_goodness_axis") for r in hist], 36, "green", color)
    pop_spark = _spark([_val(r, "avg_popularity_axis") for r in hist], 36, "magenta", color)
    lines = [
        f"t={int(_val(row, 't')):4d}  BIP={_c(_fmt_num(_val(row, 'gdp')), 'bright_green', color, True)}  Geldmenge={_c(_fmt_num(_val(row, 'money_supply')), 'bright_yellow', color, True)}  Inflation={_c(_fmt_pct(_val(row, 'avg_inflation'), signed=True), 'yellow' if _val(row,'avg_inflation') >= 0 else 'cyan', color, True)}  Arbeitslosigkeit={_c(_fmt_pct(_val(row, 'unemployment')), 'bright_red' if _val(row, 'unemployment') > 0.12 else 'green', color, True)}",
        f"Konfidenz    {_bar01(_val(row, 'mean_cash_confidence'), 28, 'bright_cyan', color)} {_val(row, 'mean_cash_confidence'):.3f}",
        f"Gutartigkeit  {_signed_bar(_val(row, 'avg_goodness_axis'), 31, 'bright_green', 'bright_red', color)} {_val(row, 'avg_goodness_axis'):+.3f}",
        f"Beliebtheit   {_signed_bar(_val(row, 'avg_popularity_axis'), 31, 'bright_magenta', 'yellow', color)} {_val(row, 'avg_popularity_axis'):+.3f}",
        f"Legitimität   {_bar01(_val(row, 'avg_legitimacy'), 28, 'green', color)} {_val(row, 'avg_legitimacy'):.3f}   Legitimitätslücke={_val(row, 'legitimacy_gap'):.3f}",
        f"Ungleichheit  Haushalte={_val(row, 'household_gini'):.3f} Firmen={_val(row, 'firm_cash_gini'):.3f}  Winkelspread Ø={deg(_val(row, 'avg_angle_spread')):.1f}°",
        f"GDP   {gdp_spark}",
        f"Geld  {money_spark}",
        f"Conf  {conf_spark}",
        f"Gut   {good_spark}",
        f"Pop   {pop_spark}",
    ]
    return _box("Makro-Cockpit: Wert, Richtung, Sicherheit", lines, color, "bright_cyan")


def _render_vector_compass(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    world_theta = rad(_val(row, "world_money_theta_deg"))
    cash_theta, buy_theta, sell_theta = _global_representative_angles(sim)
    lines = []
    lines.append(f"Weltgeldwinkel θ={_angle_label(world_theta, color)}   Konzentration R={_val(row, 'world_money_concentration'):.3f}")
    lines.append(f"repräsentativ: Cash={deg(cash_theta):6.1f}°  Kauf={deg(buy_theta):6.1f}°  Verkauf={deg(sell_theta):6.1f}°  K↔V Distanz={deg(angle_dist(buy_theta, sell_theta)):5.1f}°")
    lines.extend(_ascii_compass(world_theta, buy_theta, sell_theta, cash_theta, color))
    lines.append("Achsen: x=Gut/Böse durch Regierungen+Gerichte, y=Beliebt/Unbeliebt durch Völker+Medien.")
    return _box("Vektor-Kompass der Währung", lines, color, "bright_magenta")


def _render_triadic_exchange(row: Dict[str, Any], color: bool) -> List[str]:
    flows = [
        ("💰 Wert", "⚖ Gutartigkeit", _val(row, "value_buy_goodness_volume"), "bright_green", "Compliance, Audits, Umwelt, Arbeitsschutz"),
        ("💰 Wert", "♥ Beliebtheit", _val(row, "value_buy_popularity_volume"), "bright_magenta", "Werbung, Service, Community, Medien"),
        ("♥ Beliebtheit", "⚖ Gutartigkeit", _val(row, "popularity_buy_goodness_volume"), "cyan", "soziales Mandat senkt Reformkosten"),
        ("⚖ Gutartigkeit", "♥ Beliebtheit", _val(row, "goodness_buy_popularity_volume"), "yellow", "glaubwürdiges Verhalten wird sichtbar"),
    ]
    maxv = max([v for _, _, v, _, _ in flows] + [1.0])
    lines = []
    for left, right, v, col, note in flows:
        lines.append(f"{_pad(_c(left, col, color, True), 16)} ─{_bar(v, maxv, 32, col, color, '━')}▶ {_pad(_c(right, col, color, True), 18)} {_fmt_num(v)}   {note}")
    lines.append("")
    lines.append(f"Dreifachbörsen-Gebühren / Reibung: {_c(_fmt_num(_val(row, 'value_good_pop_exchange_fees')), 'bright_red', color, True)}   Trades: {int(_val(row, 'triadic_exchange_count'))}   Winkelwäscheindex: {_val(row, 'laundering_index'):.4f}")
    lines.append("Kernaussage: Gutartigkeit ist kaufbar nur über nachprüfbare Kosten + soziale Glaubwürdigkeit; reine Beliebtheit ohne Substanz senkt Konfidenz.")
    lines.append(f"Live-Formel: M = m·e^(iθ), θ=atan2(Beliebtheit, Gutartigkeit), Kaufkraft≈m·ρ·cos(Δθ/2)")
    return _box("Dreifachhandel: Wert ↔ Gutartigkeit ↔ Beliebtheit", lines, color, "bright_green")


def _render_market_flows(row: Dict[str, Any], color: bool) -> List[str]:
    flow_keys = [
        ("Haushalte → Firmen", "consumer_sales", "bright_green"),
        ("Firmen → Firmen", "b2b_sales", "cyan"),
        ("Firmen → Arbeit", "wages", "yellow"),
        ("Privat → Staat", "taxes", "bright_blue"),
        ("Staat → Wirtschaft", "subsidies", "green"),
        ("Banken → Kredit", "loans_issued", "bright_magenta"),
        ("International", "trade_volume", "blue"),
        ("Winkelrotation", "angle_rotation_volume", "bright_yellow"),
        ("Schwarzmarkt", "black_market_volume", "bright_red"),
        ("Kapitalfluss/FX", "capital_flow_volume", "magenta"),
    ]
    maxv = max([_val(row, k) for _, k, _ in flow_keys] + [1.0])
    lines = []
    lines.append(_c("Haushalte", "bright_green", color, True) + " ═Konsum═▶ " + _c("Firmen", "cyan", color, True) + " ═Löhne═▶ " + _c("Haushalte", "bright_green", color, True) + "   │   " + _c("Steuern/Subventionen", "bright_blue", color, True) + "   │   " + _c("Banken/Kredit", "magenta", color, True))
    lines.append(_c("Firmen", "cyan", color, True) + " ═B2B/Lieferketten═▶ " + _c("Firmen", "cyan", color, True) + " ═Handel═▶ " + _c("Ausland", "blue", color, True) + " ═FX═▶ " + _c("Reserve/Zentralbank", "bright_yellow", color, True))
    lines.append(_c("Alle Akteure", "white", color, True) + " ═Kaufwinkel/Verkaufswinkel═▶ " + _c("Winkelmarkt", "bright_yellow", color, True) + " ═Rotation/Reibung═▶ " + _c("neuer Cashwinkel", "bright_green", color, True))
    lines.append("")
    for label, key, col in flow_keys:
        lines.append(f"{_pad(label, 22)} {_bar(_val(row, key), maxv, 42, col, color)} {_fmt_num(_val(row, key))}")
    return _box("Marktfluss-Diagramm der simulierten Abschnitte", lines, color, "yellow")


def _render_angle_orderbook(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    bins = 12
    buy_bins = _weighted_angle_bins(sim, "buy_angle", bins)
    sell_bins = _weighted_angle_bins(sim, "sell_angle", bins)
    maxv = max(buy_bins + sell_bins + [1.0])
    lines = []
    lines.append("Jeder Akteur quotiert zwei Richtungen: " + _c("Kaufwinkel K", "bright_green", color, True) + " und " + _c("Verkaufswinkel V", "bright_red", color, True) + ". Der Betrag/Geldbestand gewichtet die Ordertiefe.")
    lines.append("         Kauf-Bid-Tiefe                         Winkelzone                         Verkauf-Ask-Tiefe")
    for i in range(bins):
        center = (i + 0.5) * TAU / bins
        label, col = _angle_quadrant(center)
        b = buy_bins[i]
        a = sell_bins[i]
        left = _bar(b, maxv, 28, "bright_green", color, "█")
        right = _bar(a, maxv, 28, "bright_red", color, "█")
        lines.append(f"{left} {_c(f'{int(i*360/bins):03d}°-{int((i+1)*360/bins):03d}°', col, color, True)} {_pad(_c(label, col, color), 18)} {right}")
    lines.append(f"Ø Winkelspread: {_c(f'{deg(_val(row, 'avg_angle_spread')):.1f}°', 'bright_yellow', color, True)}   Rotationskosten: {_c(_fmt_num(_val(row, 'angle_rotation_cost')), 'bright_red', color, True)}   Rotationsvolumen: {_fmt_num(_val(row, 'angle_rotation_volume'))}")
    return _box("Kreis-Orderbuch: Handel der Winkel", lines, color, "bright_yellow")


def _render_actor_angles(sim: VectorEconomySim, color: bool) -> List[str]:
    actors = sorted(_actor_stream(sim), key=lambda x: x[1].cash.amount, reverse=True)[:14]
    lines = []
    header = f"{'Typ':<4} {'Name':<24} {'Wert':>10} {'Cashθ':>8} {'Kaufθ':>8} {'Verkaufθ':>9} {'Spread':>8} {'ρ':>5}  Richtung"
    lines.append(_c(header, "white", color, True))
    for typ, a in actors:
        spread = angle_dist(a.buy_angle, a.sell_angle)
        q, col = _angle_quadrant(a.cash.theta)
        lines.append(f"{typ:<4} {_short(a.name,24):<24} {_fmt_num(a.cash.amount):>10} {deg(a.cash.theta):7.1f}° {deg(a.buy_angle):7.1f}° {deg(a.sell_angle):8.1f}° {deg(spread):7.1f}° {a.cash.confidence:5.2f}  {_c(q, col, color, True)}")
    lines.append("K=was dieser Akteur akzeptiert/kaufen will; V=welche Winkelqualität er beim Verkaufen verlangt.")
    return _box("Akteure mit zwei Winkeln: Kaufen und Verkaufen", lines, color, "bright_green")


def _render_country_panel(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    countries = list(sim.countries.values())
    max_gdp = max([_val(row, f"country_{c.id}_gdp") for c in countries] + [1.0])
    lines = []
    for c in countries:
        gov = sim.governments[c.government_id]
        gdp = _val(row, f"country_{c.id}_gdp")
        unemp = _val(row, f"country_{c.id}_unemployment")
        infl = _val(row, f"country_{c.id}_inflation")
        leg = _val(row, f"country_{c.id}_legitimacy")
        q, col = _angle_quadrant(c.currency_theta)
        line1 = f"{_c(_short(c.name,12), 'white', color, True):<20} BIP {_bar(gdp, max_gdp, 18, 'bright_green', color)} {_fmt_num(gdp):>8}  FX={c.exchange_rate:5.3f}  θ={_c(f'{deg(c.currency_theta):6.1f}°', col, color, True)} {q}"
        line2 = f"    Legitimität {_bar01(leg, 14, 'green', color)} {leg:.2f}  Unemp={_fmt_pct(unemp)}  Infl={_fmt_pct(infl, signed=True)}  Protest={c.protests:.2f}  Infra={c.infrastructure_quality:.2f}  Bio={c.biodiversity:.2f}  Crime={c.crime_index:.2f}  Courts={gov.court_independence:.2f}"
        lines.append(line1)
        lines.append(line2)
    return _box("Länder/Jurisdiktionen: Makro, Legitimität, Währungswinkel", lines, color, "bright_blue")


def _render_firm_quadrant_map(sim: VectorEconomySim, color: bool) -> List[str]:
    w, h = 49, 21
    cx, cy = w // 2, h // 2
    grid = [[" " for _ in range(w)] for _ in range(h)]
    for x in range(w):
        grid[cy][x] = "─"
    for y in range(h):
        grid[y][cx] = "│"
    grid[cy][cx] = "┼"
    # Borders of conceptual plane.
    for x in range(w):
        grid[0][x] = "─"
        grid[h-1][x] = "─"
    for y in range(h):
        grid[y][0] = "│"
        grid[y][w-1] = "│"
    grid[0][0] = "╭"; grid[0][w-1] = "╮"; grid[h-1][0] = "╰"; grid[h-1][w-1] = "╯"
    labels = [
        (2, 1, "böse + beliebt"),
        (w - 18, 1, "gut + beliebt"),
        (2, h - 2, "böse + unbeliebt"),
        (w - 20, h - 2, "gut + unbeliebt"),
    ]
    for x, y, text in labels:
        for i, ch in enumerate(text):
            if 0 <= x + i < w:
                grid[y][x+i] = ch
    firm_points: Dict[Tuple[int, int], Tuple[str, str]] = {}
    active = sorted([f for f in sim.firms.values() if f.active], key=lambda f: f.cash.amount + f.sales, reverse=True)[:180]
    for f in active:
        c = sim.countries[f.country_id]
        goodness = f.current_goodness_estimate()
        popularity = sim.people_popularity_score(c, f)[0]
        x = int(round((goodness + 1.0) / 2.0 * (w - 3))) + 1
        y = int(round((1.0 - (popularity + 1.0) / 2.0) * (h - 3))) + 1
        x = max(1, min(w - 2, x))
        y = max(1, min(h - 2, y))
        theta = angle_from_axes(goodness, popularity)
        symbol = "◆" if f.cash.amount > 2500 or f.systemic_importance > 0.5 else ("●" if f.cash.amount > 900 else "•")
        key = (x, y)
        if key in firm_points:
            symbol = "✦"
        firm_points[key] = (symbol, _angle_color(theta))
    lines = []
    for y in range(h):
        out = []
        for x in range(w):
            if (x, y) in firm_points:
                sym, col = firm_points[(x, y)]
                out.append(_c(sym, col, color, True))
            else:
                ch = grid[y][x]
                if ch in "╭╮╰╯│─┼":
                    out.append(_c(ch, "blue", color))
                elif ch.strip():
                    out.append(_c(ch, "white", color))
                else:
                    out.append(ch)
        lines.append("".join(out))
    lines.append("x-Achse: Regierung/Gerichte Gutartigkeit ← böse | gut →   y-Achse: Volks-/Medien-Beliebtheit ↑ beliebt | unbeliebt ↓")
    lines.append("Punkte sind Firmen; Größe/Symbol ≈ Wertgewicht. Genau hier kollidieren Profit, Moral und Popularität.")
    return _box("Firmenkarte: Gutartigkeit × Beliebtheit, gewichtet durch Wert", lines, color, "bright_magenta")


def _render_externalities(row: Dict[str, Any], color: bool) -> List[str]:
    items = [
        ("Verschmutzung", _val(row, "avg_pollution"), 2.0, "bright_red"),
        ("Health burden", _val(row, "avg_health_burden"), 1.5, "yellow"),
        ("Biodiversität", _val(row, "avg_biodiversity"), 1.0, "bright_green"),
        ("Crime index", _val(row, "avg_crime_index"), 1.0, "red"),
        ("Privacy damage", _val(row, "avg_privacy_damage"), 1.0, "magenta"),
        ("Infraqualität", _val(row, "avg_infrastructure_quality"), 1.0, "cyan"),
        ("Minority harm", _val(row, "minority_harm_index"), 1.0, "bright_red"),
    ]
    lines = []
    for label, v, maxv, col in items:
        # For good variables like biodiversity/infrastructure, the label color already indicates desirability.
        lines.append(f"{label:<18} {_bar(v, maxv, 36, col, color)} {v:.4f}")
    lines.append(f"Schocks: Scandals={int(_val(row, 'scandals'))}, Strikes={int(_val(row, 'strikes'))}, Defaults={int(_val(row, 'firms_defaulted'))}, Overrides={int(_val(row, 'constitutional_overrides'))}")
    return _box("Externe Effekte und politische Sicherheitsventile", lines, color, "bright_red")


def _render_events(sim: VectorEconomySim, color: bool) -> List[str]:
    events = sorted(sim.events[-30:], key=lambda e: (e.t, e.severity), reverse=True)[:10]
    lines = []
    if not events:
        lines.append(_c("Noch keine Ereignisse.", "dim", color))
    for e in events:
        col = "bright_red" if e.severity > 0.65 else "yellow" if e.severity > 0.35 else "cyan"
        cid = "world" if e.country_id is None else f"C{e.country_id}"
        lines.append(f"t={e.t:4d} {cid:<5} {_c(e.kind, col, color, True):<25} sev={e.severity:4.2f} target={str(e.target_id):<6} {e.description}")
    return _box("Ereignisband: Schocks, Skandale, Gerichte, Politik", lines, color, "white")



# ----------------------------------------------------------------------
# V5 extra dense UTF-8 / ANSI art renderers
# ----------------------------------------------------------------------

def _weighted_avg(vals: Iterable[Tuple[float, float]], default: float = 0.0) -> float:
    total = 0.0
    weight = 0.0
    for v, w in vals:
        if w > 0:
            total += v * w
            weight += w
    return total / weight if weight > EPS else default


def _money_groups(sim: VectorEconomySim) -> List[Tuple[str, str, List[ActorBase]]]:
    return [
        ("HH", "Haushalte", [h for h in sim.households.values() if h.active]),
        ("F", "Firmen", [f for f in sim.firms.values() if f.active]),
        ("B", "Banken", [b for b in sim.banks.values() if b.active]),
        ("FND", "Fonds", [f for f in sim.investment_funds.values() if f.active]),
        ("GOV", "Regierungen", [g for g in sim.governments.values() if g.active]),
        ("CB", "Zentralbanken", [cb for cb in sim.central_banks.values() if cb.active]),
    ]


def _group_money_summary(sim: VectorEconomySim) -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for code, label, actors in _money_groups(sim):
        amount = sum(max(0.0, a.cash.amount) for a in actors)
        theta, conc = angle_mean((a.cash.theta, max(0.0, a.cash.amount) * max(0.02, a.cash.confidence)) for a in actors)
        conf = _weighted_avg(((a.cash.confidence, max(0.0, a.cash.amount)) for a in actors), 0.0)
        x = sum(a.cash.amount * a.cash.confidence * math.cos(a.cash.theta) for a in actors)
        y = sum(a.cash.amount * a.cash.confidence * math.sin(a.cash.theta) for a in actors)
        out.append({"code": code, "label": label, "actors": len(actors), "amount": amount, "theta": theta, "conc": conc, "conf": conf, "x": x, "y": y})
    return out


def _heat_char(v: float, lo: float = 0.0, hi: float = 1.0) -> str:
    chars = " ·░▒▓█"
    if hi <= lo + EPS:
        return chars[0]
    idx = int(round(clamp((v - lo) / (hi - lo), 0.0, 1.0) * (len(chars) - 1)))
    return chars[max(0, min(len(chars) - 1, idx))]


def _heat_color(v: float, good_high: bool = True) -> str:
    vv = clamp(v, 0.0, 1.0)
    if not good_high:
        vv = 1.0 - vv
    if vv >= 0.78:
        return "bright_green"
    if vv >= 0.58:
        return "green"
    if vv >= 0.38:
        return "yellow"
    if vv >= 0.18:
        return "bright_magenta"
    return "bright_red"


def _linear_angle_markers(items: List[Tuple[float, str, str]], width: int = 50, color: bool = True) -> str:
    width = max(8, width)
    cells = [_c("─", "dim", color) for _ in range(width)]
    for theta, marker, col in items:
        pos = int(norm_angle(theta) / TAU * (width - 1))
        if _visible_len(cells[pos]) > 1 and cells[pos] != _c("─", "dim", color):
            cells[pos] = _c("◆", "white", color, True)
        else:
            cells[pos] = _c(marker, col, color, True)
    return _c("0°", "white", color) + " " + "".join(cells) + " " + _c("360°", "white", color)


def _mini_heat_line(values: List[float], width: int, color_name: str, color: bool = True) -> str:
    if not values:
        return _c("·" * width, "dim", color)
    vals = list(values)
    if len(vals) < width:
        vals = vals + [0.0] * (width - len(vals))
    if len(vals) > width:
        # aggregate into visible buckets
        buckets: List[float] = []
        for i in range(width):
            start = int(i * len(vals) / width)
            end = int((i + 1) * len(vals) / width)
            chunk = vals[start:max(start + 1, end)]
            buckets.append(sum(chunk) / max(1, len(chunk)))
        vals = buckets
    mx = max(vals + [EPS])
    chars = []
    for v in vals[:width]:
        chars.append(_heat_char(v, 0.0, mx))
    return _c("".join(chars), color_name, color)


def _render_dashboard_legend(color: bool) -> List[str]:
    lines = [
        _c("██", "bright_green", color) + " gut/beliebt oder positiver Wert   " + _c("██", "bright_red", color) + " Risiko, Böse, Verlust oder Krise   " + _c("██", "bright_magenta", color) + " Beliebtheit/Medienmacht   " + _c("██", "bright_yellow", color) + " Geld/Winkelrotation",
        "UTF‑8-Diagramme sind absichtlich redundant: dieselbe Ökonomie wird als Geldfluss, Winkelmarkt, Orakelkonflikt, Sektorstruktur, Finanzsystem, Risiko und Machtkarte sichtbar.",
        "Alle Boxen werden weiterhin auf die erkannte Terminalbreite minus 5 Zeichen gedeckelt; lange Diagramme werden hart umbrochen statt über den Bildschirm zu laufen.",
    ]
    return _box("V5 Art-Legende: sehr bunte Mehrfachsicht auf dieselbe Vektorökonomie", lines, color, "bright_cyan")


def _render_money_mass_river(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    groups = _group_money_summary(sim)
    total = max(1.0, sum(g["amount"] for g in groups))
    maxv = max([g["amount"] for g in groups] + [1.0])
    lines = []
    river_parts = []
    for g in groups:
        frac = g["amount"] / total
        n = max(1, int(round(frac * 54))) if g["amount"] > EPS else 0
        col = _angle_color(g["theta"])
        river_parts.append(_c(g["code"] + " " + "█" * n, col, color, True))
    lines.append("Geldmassen-Flussband: " + " ".join(river_parts))
    lines.append("")
    for g in groups:
        col = _angle_color(g["theta"])
        label = f"{g['label']} ({g['actors']})"
        lines.append(f"{_pad(label, 18)} {_bar(g['amount'], maxv, 34, col, color)} {_fmt_num(g['amount']):>9}  θ={_c(f'{deg(g['theta']):6.1f}°', col, color, True)}  ρ={g['conf']:.2f}  R={g['conc']:.2f}")
    lines.append("Interpretation: Der Betrag ist Gewicht; der Winkel zeigt die moralisch-soziale Richtung der jeweiligen Geldmasse.")
    return _box("Geldmassen-River: Wer hält wie viel gerichtetes Geld?", lines, color, "bright_yellow")


def _render_class_vector_balance(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    groups = _group_money_summary(sim)
    maxcomp = max([abs(g["x"]) for g in groups] + [abs(g["y"]) for g in groups] + [1.0])
    lines = []
    lines.append(_c("x-Komponente", "bright_green", color, True) + " = Gutartigkeit/Bösartigkeit der gehaltenen Kaufkraft; " + _c("y-Komponente", "bright_magenta", color, True) + " = Beliebtheit/Unbeliebtheit.")
    for g in groups:
        xn = g["x"] / maxcomp
        yn = g["y"] / maxcomp
        xlab = "gut" if g["x"] >= 0 else "böse"
        ylab = "beliebt" if g["y"] >= 0 else "unbeliebt"
        lines.append(f"{_pad(g['label'], 15)} x {_signed_bar(xn, 25, 'bright_green', 'bright_red', color)} {_fmt_num(g['x']):>9} {xlab:<5}   y {_signed_bar(yn, 25, 'bright_magenta', 'yellow', color)} {_fmt_num(g['y']):>9} {ylab}")
    lines.append("Wenn x und y gegeneinander laufen, ist das System nicht einfach arm/reich, sondern normativ gespalten.")
    return _box("Vektor-Bilanz nach Akteursklasse: Wert zerlegt in Gutartigkeit und Beliebtheit", lines, color, "bright_green")


def _render_angle_liquidity_wheel(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    bins = 36
    # Cash is not a direct angle attribute; compute it from each actor's VectorMoney.
    cash_bins = [0.0 for _ in range(bins)]
    for _, a in _actor_stream(sim):
        idx = int(norm_angle(a.cash.theta) / TAU * bins) % bins
        cash_bins[idx] += max(0.0, a.cash.amount) * max(0.02, a.cash.confidence)
    buy_bins = _weighted_angle_bins(sim, "buy_angle", bins)
    sell_bins = _weighted_angle_bins(sim, "sell_angle", bins)
    spread_bins = [abs(buy_bins[i] - sell_bins[i]) for i in range(bins)]
    lines = [
        "0° gut→ | 90° beliebt↑ | 180° böse← | 270° unbeliebt↓ | zurück zu 360°",
        "Cash θ   " + _mini_heat_line(cash_bins, bins, "bright_yellow", color),
        "Kauf θ   " + _mini_heat_line(buy_bins, bins, "bright_green", color),
        "Verkaufθ " + _mini_heat_line(sell_bins, bins, "bright_red", color),
        "K/V Gap  " + _mini_heat_line(spread_bins, bins, "bright_magenta", color),
        "          " + _c("0        90        180       270       360", "white", color),
        "Helle Blöcke = hohe Liquidität/Gewichtung im jeweiligen Winkelabschnitt; K/V Gap zeigt fehlende Marktgegenseite.",
    ]
    return _box("360° Winkel-Liquiditätsrad: Cash, Kaufwinkel, Verkaufswinkel, Spread", lines, color, "bright_magenta")


def _render_execution_ladder(sim: VectorEconomySim, color: bool) -> List[str]:
    buyers = sorted(_actor_stream(sim), key=lambda x: x[1].cash.amount, reverse=True)[:10]
    sellers = sorted(_actor_stream(sim), key=lambda x: (x[1].cash.amount * x[1].cash.confidence), reverse=True)[10:20]
    if len(sellers) < len(buyers):
        sellers = list(reversed(buyers))
    lines = []
    lines.append(_c("Ausführungsidee:", "white", color, True) + " Käufer-Kaufwinkel K trifft Verkäufer-Verkaufswinkel V; kompatibler Wert ≈ min(Cash)·ρ·cos(Δθ/2).")
    header = f"{'Käufer K':<18} {'Verkäufer V':<18} {'Δθ':>7} {'Kompat.':>8} {'eff.Wert':>10}  Brücke"
    lines.append(_c(header, "white", color, True))
    for (bt, b), (st, s) in zip(buyers[:9], sellers[:9]):
        d = angle_dist(b.buy_angle, s.sell_angle)
        comp = cosine_compat(b.buy_angle, s.sell_angle, 0.0)
        eff = min(max(0.0, b.cash.amount), max(0.0, s.cash.amount)) * comp * min(b.cash.confidence, s.cash.confidence)
        col = "bright_green" if comp > 0.78 else "yellow" if comp > 0.45 else "bright_red"
        bridge = _bar(comp, 1.0, 24, col, color, "━")
        lines.append(f"{_short(b.name,16):<18} {_short(s.name,16):<18} {deg(d):6.1f}° {comp:8.3f} {_fmt_num(eff):>10}  {bridge}")
    lines.append("Das ist der konkrete Handel der drei Dinge: Wert wird nur dann voll wirksam, wenn Kaufwinkel und Verkaufswinkel nahe genug liegen.")
    return _box("Order-Ausführungsleiter: zwei Winkel pro Akteur im Handelskontakt", lines, color, "bright_yellow")


def _render_sector_heatmap(sim: VectorEconomySim, color: bool) -> List[str]:
    sector_rows = []
    for sector in SECTORS:
        firms = [f for f in sim.firms.values() if f.active and f.sector == sector]
        if not firms:
            continue
        weights = [max(1.0, f.sales + f.cash.amount) for f in firms]
        sales = sum(f.sales for f in firms)
        cash = sum(f.cash.amount for f in firms)
        goodness = _weighted_avg(((f.current_goodness_estimate(), w) for f, w in zip(firms, weights)), 0.0)
        popularity = _weighted_avg(((sim.people_popularity_score(sim.countries[f.country_id], f)[0], w) for f, w in zip(firms, weights)), 0.0)
        conf = _weighted_avg(((f.reputation_confidence, w) for f, w in zip(firms, weights)), 0.0)
        theta = angle_from_axes(goodness, popularity)
        sector_rows.append((sector, sales, cash, goodness, popularity, conf, theta, len(firms)))
    sector_rows.sort(key=lambda x: x[1] + x[2], reverse=True)
    maxv = max([r[1] + r[2] for r in sector_rows] + [1.0])
    lines = []
    lines.append(f"{'Sektor':<15} {'Wertgewicht':<28} {'Gut':<27} {'Pop':<27} {'ρ':>4} θ")
    for sector, sales, cash, goodness, popularity, conf, theta, n in sector_rows[:18]:
        col = _angle_color(theta)
        value = sales + cash
        lines.append(f"{_short(sector,14):<15} {_bar(value, maxv, 24, col, color)} {_signed_bar(goodness, 23, 'bright_green', 'bright_red', color)} {_signed_bar(popularity, 23, 'bright_magenta', 'yellow', color)} {conf:4.2f} {_c(f'{deg(theta):6.1f}°', col, color, True)} n={n}")
    lines.append("Sektorzeilen zeigen: Wertmenge, Gut/Böse-Achse, Beliebt/Unbeliebt-Achse und daraus entstehenden Winkel.")
    return _box("Sektor-Heatmap: Wert × Gutartigkeit × Beliebtheit", lines, color, "bright_green")


def _render_sector_economics(sim: VectorEconomySim, color: bool) -> List[str]:
    rows = []
    for sector in SECTORS:
        firms = [f for f in sim.firms.values() if f.active and f.sector == sector]
        if not firms:
            continue
        employees = sum(len(f.employees) for f in firms)
        avg_price = statistics.mean([f.price for f in firms]) if firms else 0.0
        avg_wage = statistics.mean([f.wage_offer for f in firms]) if firms else 0.0
        profit = sum(f.profit for f in firms)
        productivity = statistics.mean([f.productivity * f.technology for f in firms]) if firms else 0.0
        rows.append((sector, employees, avg_price, avg_wage, profit, productivity, len(firms)))
    rows.sort(key=lambda x: x[1] + abs(x[4]) / 100.0, reverse=True)
    max_emp = max([r[1] for r in rows] + [1.0])
    max_profit = max([abs(r[4]) for r in rows] + [1.0])
    lines = []
    lines.append(f"{'Sektor':<15} {'Arbeit':<22} {'Preis':>8} {'Lohn':>8} {'Profit':<24} {'Tech×Prod':>9}")
    for sector, employees, price, wage, profit, prod, n in rows[:16]:
        pcol = "bright_green" if profit >= 0 else "bright_red"
        lines.append(f"{_short(sector,14):<15} {_bar(employees, max_emp, 19, 'cyan', color)} {price:8.2f} {wage:8.2f} {_bar(abs(profit), max_profit, 20, pcol, color)} {_fmt_num(profit):>8} {prod:9.2f}")
    lines.append("Diese Box macht den realwirtschaftlichen Körper hinter den Winkeln sichtbar: Arbeit, Preise, Löhne, Profit, Technologie.")
    return _box("Sektorökonomie: Arbeitsmarkt, Preise, Löhne, Produktivität", lines, color, "cyan")


def _render_oracle_divergence(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    lines = []
    lines.append("G=Regierungs-/Gerichtswinkel, P=gewichtete Volksideologie, W=Währungswinkel. Große G↔P-Distanz = Legitimitätsrisiko.")
    for c in sim.countries.values():
        gov = sim.governments[c.government_id]
        ptheta, pconc = angle_mean((pg.ideology_theta, pg.weight) for pg in c.people_groups)
        d_gp = angle_dist(gov.ideology_theta, ptheta)
        d_wc = angle_dist(c.currency_theta, angle_blend(gov.ideology_theta, ptheta, 0.5))
        avg_sat = _weighted_avg(((pg.current_satisfaction, pg.weight) for pg in c.people_groups), 0.0)
        avg_anger = _weighted_avg(((pg.anger, pg.weight) for pg in c.people_groups), 0.0)
        col = "bright_green" if d_gp < math.radians(35) else "yellow" if d_gp < math.radians(90) else "bright_red"
        markers = _linear_angle_markers([(gov.ideology_theta, "G", "bright_blue"), (ptheta, "P", "bright_magenta"), (c.currency_theta, "W", _angle_color(c.currency_theta))], 38, color)
        lines.append(f"{_short(c.name,12):<13} ΔG/P={_c(f'{deg(d_gp):5.1f}°', col, color, True)} ΔW/Mitte={deg(d_wc):5.1f}°  Sat={avg_sat:+.2f} Ärger={avg_anger:.2f} Pol={c.polarization:.2f}  {markers}")
    return _box("Orakel-Divergenz: Regierungen legen Gut/Böse fest, Völker Beliebt/Unbeliebt", lines, color, "bright_blue")


def _render_confidence_spectrum(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    bins = [0.0 for _ in range(10)]
    counts = [0 for _ in range(10)]
    for _, a in _actor_stream(sim):
        idx = min(9, max(0, int(a.cash.confidence * 10)))
        bins[idx] += max(0.0, a.cash.amount)
        counts[idx] += 1
    maxv = max(bins + [1.0])
    lines = []
    for i, v in enumerate(bins):
        lo = i / 10.0
        hi = (i + 1) / 10.0
        col = _heat_color((lo + hi) / 2.0, True)
        lines.append(f"ρ {lo:.1f}-{hi:.1f} {_bar(v, maxv, 42, col, color)} {_fmt_num(v):>9} Akteure={counts[i]}")
    lines.append(f"Mittelkonfidenz: {_val(row, 'mean_cash_confidence'):.3f}; niedrige ρ erzeugt Winkelinflation: alles behauptet gut zu sein, aber niemand glaubt es vollständig.")
    return _box("Konfidenz-Spektrum der Geldwinkel", lines, color, "bright_cyan")


def _render_spread_histogram(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    bins = [0.0 for _ in range(6)]
    counts = [0 for _ in range(6)]
    labels = ["0-30°", "30-60°", "60-90°", "90-120°", "120-150°", "150-180°"]
    for _, a in _actor_stream(sim):
        d = deg(angle_dist(a.buy_angle, a.sell_angle))
        idx = min(5, int(d // 30.0))
        bins[idx] += max(0.0, a.cash.amount)
        counts[idx] += 1
    maxv = max(bins + [1.0])
    lines = []
    for i, label in enumerate(labels):
        col = "bright_green" if i <= 1 else "yellow" if i <= 3 else "bright_red"
        lines.append(f"{label:<9} {_bar(bins[i], maxv, 48, col, color)} {_fmt_num(bins[i]):>9} Akteure={counts[i]}")
    lines.append("Kleiner Spread = hohe Winkel-Liquidität. Großer Spread = moralisch-soziale Marktspaltung und teure Rotation.")
    return _box("Kauf-/Verkaufswinkel-Spread-Histogramm", lines, color, "bright_yellow")


def _render_value_good_pop_triangle(row: Dict[str, Any], color: bool) -> List[str]:
    vg = _val(row, "value_buy_goodness_volume")
    vp = _val(row, "value_buy_popularity_volume")
    pg = _val(row, "popularity_buy_goodness_volume")
    gp = _val(row, "goodness_buy_popularity_volume")
    fees = _val(row, "value_good_pop_exchange_fees")
    mx = max(vg, vp, pg, gp, fees, 1.0)
    lines = [
        "                         " + _c("⚖ GUTARTIGKEIT", "bright_green", color, True),
        "                       ╱" + _bar(pg, mx, 14, "cyan", color, "━") + "╲",
        "                      ╱  Pop→Gut " + _fmt_num(pg) + "  ╲",
        _c("💰 WERT", "bright_yellow", color, True) + " " + _bar(vg, mx, 18, "bright_green", color, "━") + "▶" + " " * 8 + "◀" + _bar(gp, mx, 18, "yellow", color, "━") + " " + _c("♥ BELIEBTHEIT", "bright_magenta", color, True),
        "  Wert→Gut " + _fmt_num(vg) + "        Gut→Pop " + _fmt_num(gp),
        "                       ╲" + _bar(vp, mx, 14, "bright_magenta", color, "━") + "╱",
        "                        Wert→Pop " + _fmt_num(vp),
        f"Reibung/Gebühren: {_bar(fees, mx, 32, 'bright_red', color)} {_fmt_num(fees)}   Trades={int(_val(row, 'triadic_exchange_count'))}",
        "Dieses Dreieck zeigt die politisch gefährliche Frage direkt: Kann man Gutartigkeit mit Wert und Beliebtheit kaufen — oder nur glaubwürdig erarbeiten?",
    ]
    return _box("Dreiecksbörse: Wert, Gutartigkeit, Beliebtheit", lines, color, "bright_magenta")


def _render_financial_system_map(row: Dict[str, Any], color: bool) -> List[str]:
    flows = [
        ("Kredite neu", "loans_issued", "bright_magenta"),
        ("Loan defaults", "loan_defaults", "bright_red"),
        ("Bond emission", "bond_issuance", "bright_blue"),
        ("Bond defaults", "bond_defaults", "bright_red"),
        ("Equity emission", "equity_issuance", "green"),
        ("Equity trading", "equity_trading_volume", "bright_green"),
        ("Dividenden", "dividends", "yellow"),
        ("Hypotheken", "mortgages_issued", "cyan"),
        ("Versicherungsprämien", "insurance_premiums", "bright_cyan"),
        ("Versicherungsclaims", "insurance_claims", "bright_red"),
        ("FX Orderbook", "fx_orderbook_volume", "blue"),
        ("Reserveintervention", "reserve_intervention", "bright_yellow"),
    ]
    maxv = max([_val(row, key) for _, key, _ in flows] + [1.0])
    lines = [
        _c("Haushalte", "bright_green", color, True) + " ⇄ " + _c("Banken", "bright_magenta", color, True) + " ⇄ " + _c("Firmen", "cyan", color, True) + " ⇄ " + _c("Börsen", "bright_blue", color, True) + " ⇄ " + _c("Fonds/Pensionen", "green", color, True) + " ⇄ " + _c("Staat/Zentralbank", "bright_yellow", color, True),
        "Finanzmärkte handeln nicht nur Risiko und Zeit, sondern auch Winkelrisiko, Konfidenz und politische Umwertung.",
        "",
    ]
    for label, key, col in flows:
        lines.append(f"{_pad(label, 22)} {_bar(_val(row, key), maxv, 42, col, color)} {_fmt_num(_val(row, key))}")
    return _box("Finanzsystem-Karte: Kredit, Bonds, Aktien, Hypotheken, Versicherung, FX", lines, color, "bright_blue")


def _render_corporate_network_panel(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    groups = list(sim.corporate_groups.values())[:14]
    lines = []
    if not groups:
        lines.append(_c("Keine Konzernstrukturen aktiv.", "dim", color))
    else:
        lines.append(f"{'Konzern':<20} {'Subs':>4} {'Opacity':<20} {'TaxHaven':>8} {'θ':>8} {'ρ':>4} Parent → Töchter")
        for g in groups:
            parent = sim.firms.get(g.parent_firm_id)
            col = _angle_color(g.consolidation_theta)
            opacity_col = _heat_color(g.opacity, good_high=False)
            subs = [sim.firms[sid].name for sid in g.subsidiary_ids[:3] if sid in sim.firms]
            chain = (_short(parent.name if parent else "?", 14) + " → " + ", ".join(_short(x, 9) for x in subs)) if parent else "?"
            lines.append(f"{_short(g.name,19):<20} {len(g.subsidiary_ids):4d} {_bar01(g.opacity, 17, opacity_col, color)} {g.tax_haven_country_id:8d} {_c(f'{deg(g.consolidation_theta):6.1f}°', col, color, True)} {g.consolidation_confidence:4.2f} {chain}")
    lines.append(f"Transfer Pricing: {_c(_fmt_num(_val(row, 'transfer_pricing_volume')), 'bright_red', color, True)}   vermiedene Steuern: {_c(_fmt_num(_val(row, 'tax_avoided')), 'bright_red', color, True)}")
    lines.append("Konzernopazität ist eine Winkel-Angriffsfläche: Wert, Gutartigkeit und Herkunft können auseinandergezogen werden.")
    return _box("Konzern-/Holding-Netzwerk: Macht, Opazität, Steuerarbitrage", lines, color, "bright_red")


def _render_supply_chain_matrix(sim: VectorEconomySim, color: bool) -> List[str]:
    sectors = sorted(SECTORS, key=lambda s: sum(f.sales for f in sim.firms.values() if f.active and f.sector == s), reverse=True)[:12]
    lines = []
    lines.append("Jede Endware trägt Winkel aus Vorleistungen: Energie, Daten, Rohstoffe, Medien, Software, Transport usw.")
    for sector in sectors:
        spec = GOOD_SPECS[sector]
        inputs = sorted(spec.input_sectors.items(), key=lambda kv: kv[1], reverse=True)
        pieces = []
        for inp, w in inputs[:5]:
            pieces.append(_c(_short(inp, 10), "cyan", color, True) + _bar(w, 0.35, 8, "bright_yellow", color, "▰"))
        harm_col = _heat_color(spec.environmental_harm, good_high=False)
        social_col = _heat_color((spec.social_good + 0.15) / 1.1, good_high=True)
        lines.append(f"{_short(sector,14):<15} ← {' '.join(pieces) if pieces else _c('keine großen Inputs', 'dim', color)}")
        lines.append(f"    Umwelt {_bar(spec.environmental_harm, 1.0, 18, harm_col, color)} {spec.environmental_harm:.2f}  Sozialnutzen {_bar(clamp(spec.social_good, -0.2, 1.0)+0.2, 1.2, 18, social_col, color)} {spec.social_good:+.2f}  Winkel-Sensitivität={spec.angle_sensitivity:.2f}")
    return _box("Lieferketten-Matrix: Woher der Winkel eines Produkts kommt", lines, color, "cyan")


def _render_institution_safety_board(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    lines = []
    lines.append(f"Overrides={int(_val(row, 'constitutional_overrides'))}  Vertragsstreitigkeiten={int(_val(row, 'contract_disputes'))}  Minority-Harm={_val(row, 'minority_harm_index'):.4f}")
    lines.append(f"{'Land':<13} {'Courts':<16} {'Constitution':<16} {'Minority':<16} {'Corruption':<16} {'Capture':<16} {'Propaganda'}")
    for c in sim.countries.values():
        gov = sim.governments[c.government_id]
        lines.append(f"{_short(c.name,12):<13} {_bar01(gov.court_independence, 13, 'bright_blue', color)} {_bar01(gov.constitution_score, 13, 'green', color)} {_bar01(gov.minority_protection, 13, 'bright_green', color)} {_bar01(gov.corruption, 13, 'bright_red', color)} {_bar01(gov.regulatory_capture, 13, 'yellow', color)} {_fmt_num(gov.propaganda_budget)}")
    lines.append("Diese Schutzschicht verhindert, dass Winkelgeld bloß politisches Gehorsamsgeld wird.")
    return _box("Verfassungs-/Gerichtsschutz gegen Winkelmissbrauch", lines, color, "white")


def _render_crisis_seismograph(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    hist = sim.metrics[-48:]
    keys = [
        ("Inflation", "avg_inflation", "yellow"),
        ("Arbeitslosigkeit", "unemployment", "bright_red"),
        ("Legitimitätslücke", "legitimacy_gap", "bright_magenta"),
        ("Winkelvolatilität", "angle_volatility", "bright_yellow"),
        ("Winkelwäsche", "laundering_index", "bright_red"),
        ("Black Market", "black_market_volume", "red"),
        ("Kapitalflüsse", "capital_flow_volume", "blue"),
        ("Pollution Δ", "pollution_delta", "bright_red"),
    ]
    lines = []
    for label, key, col in keys:
        vals = [_val(r, key) for r in hist]
        lines.append(f"{_pad(label, 18)} {_spark(vals, 44, col, color)} jetzt={_fmt_num(_val(row, key), 4)}")
    lines.append("Seismographen zeigen nicht Kalibrierung, sondern Regimewechsel: Panik, Misstrauen, Rotation, Umwelt-/Politikschocks.")
    return _box("Krisen-Seismograph: Frühsignale im Zeitverlauf", lines, color, "bright_red")


def _render_demography_human_capital(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    households = [h for h in sim.households.values() if h.active]
    if not households:
        return _box("Demografie und Human Capital", [_c("Keine Haushalte aktiv.", "dim", color)], color, "green")
    age_bins = [("0-24", 0, 24), ("25-39", 25, 39), ("40-54", 40, 54), ("55-64", 55, 64), ("65+", 65, 200)]
    counts = []
    for label, lo, hi in age_bins:
        hs = [h for h in households if lo <= h.age <= hi]
        counts.append((label, len(hs), statistics.mean([h.human_capital for h in hs]) if hs else 0.0, statistics.mean([h.health for h in hs]) if hs else 0.0))
    maxc = max([c for _, c, _, _ in counts] + [1])
    lines = []
    for label, n, hc, health in counts:
        lines.append(f"Alter {label:<5} {_bar(n, maxc, 32, 'bright_green', color)} n={n:<5} HumanCapital={hc:.2f} Gesundheit={health:.2f}")
    lines.append(f"Migration in diesem Schritt: {int(_val(row, 'migration_count'))}; Humankapital verändert Produktivität, Löhne, politische Geduld und Winkelpräferenzen.")
    return _box("Demografie & Human Capital: Arbeitskräftekörper der Simulation", lines, color, "bright_green")


def _render_media_power_map(sim: VectorEconomySim, color: bool) -> List[str]:
    firms = sorted([f for f in sim.firms.values() if f.active], key=lambda f: f.media_power + f.advertising_budget + f.brand_capital, reverse=True)[:14]
    maxv = max([f.media_power + f.advertising_budget + f.brand_capital for f in firms] + [1.0])
    lines = []
    lines.append("Medien-/Markenmacht verschiebt Beliebtheit schneller als reale Gutartigkeit; dadurch entstehen Populismus- und Winkelwäschepfade.")
    for f in firms:
        v = f.media_power + f.advertising_budget + f.brand_capital
        pop = axes_from_angle(f.reputation_theta)[1]
        col = "bright_magenta" if pop >= 0 else "yellow"
        lines.append(f"{_short(f.name,22):<23} {_short(f.sector,12):<13} Medien {_bar(v, maxv, 24, 'bright_magenta', color)} Pop={_signed_bar(pop, 17, 'bright_magenta', 'yellow', color)} Brand={f.brand_capital:.2f} Ads={_fmt_num(f.advertising_budget)}")
    return _box("Medien-/Beliebtheitsmacht: Wer kann den y-Winkel bewegen?", lines, color, "bright_magenta")


def _render_rating_market(sim: VectorEconomySim, row: Dict[str, Any], color: bool) -> List[str]:
    agencies = list(sim.rating_agencies.values())
    firms = sorted([f for f in sim.firms.values() if f.active], key=lambda f: abs(f.rating - f.reputation_confidence), reverse=True)[:10]
    lines = []
    lines.append(f"Ratingaktionen in diesem Schritt: {int(_val(row, 'rating_actions'))}; Ratingagenturen sind zusätzliche, fehlbare Orakel neben Regierung und Volk.")
    for a in agencies[:8]:
        col = _angle_color(a.bias_theta)
        lines.append(f"Agentur {_short(a.name,14):<15} bias θ={_c(f'{deg(a.bias_theta):6.1f}°', col, color, True)} Accuracy={a.accuracy:.2f} Corruption={a.corruption:.2f} Influence={a.influence:.2f}")
    if firms:
        lines.append(_c("Auffällige Firmenratings:", "white", color, True))
    for f in firms:
        goodness = f.current_goodness_estimate()
        lines.append(f"{_short(f.name,20):<21} Rating {_bar01(f.rating, 14, 'bright_blue', color)} {f.rating:.2f}  ρ={f.reputation_confidence:.2f}  Gut={goodness:+.2f}  Fraud={f.fraud_level:.2f}")
    return _box("Ratingmarkt: Dritt-Orakel, Bonität und Winkelkonfidenz", lines, color, "bright_blue")


def render_art_dashboard(sim: VectorEconomySim, row: Dict[str, Any], width: int = 0, color: bool = True, final: bool = False) -> str:
    global _ART_MAX_WIDTH
    width = _resolve_art_width(width, _ART_WIDTH_SAFETY)
    _ART_MAX_WIDTH = width
    title = "V5 EXTREME UTF-8/ANSI Dashboard — Vektorwährung: Wert × Gutartigkeit × Beliebtheit"
    lines: List[str] = []
    lines.append(_hr(title, width, color, "bright_cyan"))
    if final:
        lines.extend(_wrap_ansi_line(_c("FINALER SNAPSHOT", "bright_yellow", color, True), width))
    lines.extend(_render_dashboard_legend(color))
    lines.extend(_render_macro_panel(sim, row, color))
    lines.extend(_render_money_mass_river(sim, row, color))
    lines.extend(_render_class_vector_balance(sim, row, color))
    lines.extend(_render_vector_compass(sim, row, color))
    lines.extend(_render_angle_liquidity_wheel(sim, row, color))
    lines.extend(_render_angle_orderbook(sim, row, color))
    lines.extend(_render_spread_histogram(sim, row, color))
    lines.extend(_render_execution_ladder(sim, color))
    lines.extend(_render_triadic_exchange(row, color))
    lines.extend(_render_value_good_pop_triangle(row, color))
    lines.extend(_render_market_flows(row, color))
    lines.extend(_render_financial_system_map(row, color))
    lines.extend(_render_actor_angles(sim, color))
    lines.extend(_render_country_panel(sim, row, color))
    lines.extend(_render_oracle_divergence(sim, row, color))
    lines.extend(_render_institution_safety_board(sim, row, color))
    lines.extend(_render_firm_quadrant_map(sim, color))
    lines.extend(_render_sector_heatmap(sim, color))
    lines.extend(_render_sector_economics(sim, color))
    lines.extend(_render_supply_chain_matrix(sim, color))
    lines.extend(_render_corporate_network_panel(sim, row, color))
    lines.extend(_render_media_power_map(sim, color))
    lines.extend(_render_rating_market(sim, row, color))
    lines.extend(_render_demography_human_capital(sim, row, color))
    lines.extend(_render_externalities(row, color))
    lines.extend(_render_crisis_seismograph(sim, row, color))
    lines.extend(_render_events(sim, color))
    lines.append(_hr("Ende Dashboard — CSV/JSON enthalten dieselben Messgrößen maschinenlesbar", width, color, "bright_cyan"))
    # Defensive final pass: even if a future renderer adds a too-wide line, the
    # dashboard still wraps to the terminal-safe width instead of corrupting the
    # frame.
    safe_lines = _wrap_lines(lines, width)
    return "\n".join(safe_lines)


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Vector currency economy simulation, PyPy3-compatible, no external dependencies.")
    p.add_argument("--steps", type=int, default=60, help="number of monthly steps")
    p.add_argument("--countries", type=int, default=3, help="number of countries")
    p.add_argument("--households", type=int, default=600, help="number of household agents")
    p.add_argument("--firms", type=int, default=120, help="number of firm agents")
    p.add_argument("--banks", type=int, default=9, help="number of bank agents")
    p.add_argument("--seed", type=int, default=42, help="random seed")
    p.add_argument("--out", default="metrics.csv", help="CSV output path")
    p.add_argument("--summary", default="summary.json", help="JSON summary output path")
    p.add_argument("--events", default="events.csv", help="event log CSV output path")
    p.add_argument("--verbose", action="store_true", help="print periodic progress")
    p.add_argument("--art", action="store_true", help="print very dense colorful UTF-8/ANSI dashboard diagrams during the run")
    p.add_argument("--art-every", type=int, default=12, help="print art dashboard every N steps when --art is enabled")
    p.add_argument("--art-width", type=int, default=0, help="optional maximum art width; 0=auto-detect terminal columns minus 5 chars; explicit values are still capped to that safe width")
    p.add_argument("--no-color", action="store_true", help="disable ANSI colors while keeping UTF-8 diagrams")
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
    if args.art_every < 1:
        raise SystemExit("--art-every must be >= 1")
    sim = VectorEconomySim(args.seed, args.countries, args.households, args.firms, args.banks, args.verbose)
    for _ in range(args.steps):
        row = sim.step()
        if args.art and (sim.t == 1 or sim.t % max(1, args.art_every) == 0 or sim.t == args.steps):
            print(render_art_dashboard(sim, row, width=args.art_width, color=not args.no_color, final=(sim.t == args.steps)))
        elif args.verbose and (sim.t == 1 or sim.t % max(1, args.steps // 10) == 0 or sim.t == args.steps):
            print(
                "t={t:4d} gdp={gdp:10.2f} unemp={unemployment:.3f} infl={avg_inflation:+.3f} "
                "theta={world_money_theta_deg:7.2f} conf={mean_cash_confidence:.3f} black={black_market_volume:.2f} "
                "V→G={value_buy_goodness_volume:.2f} V→P={value_buy_popularity_volume:.2f}".format(**row)
            )
    sim.write_csv(args.out)
    sim.write_summary(args.summary)
    sim.write_events(args.events)
    if args.verbose:
        print(f"Wrote {args.out}, {args.summary}, {args.events}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
