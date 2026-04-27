#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Mega Economy Simulation + Predicate Truth Currency
==================================================

This file extends ``mega_economy_sim.py`` with a second, tradeable currency.
The original currency remains ordinary fiat money (ECU by default). The new
currency is a rational-valued stack of fuzzy truth predicates. It is intended
as a stylized laboratory for the idea that economic success should compete not
only on profit, but also on correctness: resource discipline, energy discipline,
balance-sheet honesty, verification quality, knowledge, education, and long-run
planetary viability.

Core extension
--------------
1. Every major money flow is audited into an n-ary fuzzy predicate.
2. Predicate truth values live in [-1, 1], where -1 means falsified/lie and
   +1 means verified/truth.
3. Stacked fuzzy bits are converted into exact rational numbers via Fraction.
4. The rational truth units form a second tradeable currency (default: TCR).
5. Firms, households, banks, and the state hold truth balances and truth debts.
6. Resource and energy quotas are represented as fuzzy allowed bands.
7. Overshooting one planetary/resource quota throttles other resource uses in
   later periods.
8. A market for correctness models lets firms trade successful verified
   economic models, not only ordinary products.
9. Verification and meta-verification increase predicate arity: checking a
   truth value adds one logical element; checking the checking adds another.
10. Truth balances influence credit approval, loan pricing, investment quality,
    market selection, reputation, and long-run resource access.

Run examples
------------
    pypy3 mega_economy_sim_truth_currency.py --steps 120 --households 800 --firms 160 \
        --scenario climate_transition --policy green --out truth.csv --json truth.json

    pypy3 mega_economy_sim_truth_currency.py --compare baseline energy_shock financial_crisis \
        climate_transition truth_currency_transition planetary_overshoot \
        greenwashing_crackdown knowledge_commons --steps 80 --out truth_compare.csv --json truth_compare.json

The model is stylized. Treat it as a mechanism lab, not an empirical forecast.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
from collections import defaultdict
from dataclasses import dataclass, field
from fractions import Fraction
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import mega_economy_sim as base
except ImportError as exc:  # pragma: no cover - only triggered outside package
    raise SystemExit(
        "This extension requires mega_economy_sim.py in the same directory. "
        "Download the full package ZIP or keep both files together."
    ) from exc

EPS = base.EPS
TRUTH_DENOMINATOR = 1_000_000
TRUTH_MAX_DENOMINATOR = 10_000_000

RESOURCE_NAMES = [
    "energy_total",
    "fossil_energy",
    "emissions",
    "materials",
    "water",
    "land",
    "waste",
    "biodiversity_pressure",
    "compute_energy",
    "housing_land",
]

# Additional stylized resource intensities not present in the base model.
# They are deliberately rough. The goal is to let resource interactions exist.
SECTOR_RESOURCE_EXTRAS: Dict[str, Dict[str, float]] = {
    "Food": {"materials": 0.07, "water": 0.20, "land": 0.18, "waste": 0.08, "biodiversity_pressure": 0.16},
    "Retail": {"materials": 0.05, "water": 0.03, "land": 0.03, "waste": 0.09, "biodiversity_pressure": 0.03},
    "Manufacturing": {"materials": 0.20, "water": 0.08, "land": 0.04, "waste": 0.14, "biodiversity_pressure": 0.05},
    "Construction": {"materials": 0.28, "water": 0.07, "land": 0.16, "waste": 0.18, "biodiversity_pressure": 0.10, "housing_land": 0.12},
    "HousingServices": {"materials": 0.04, "water": 0.06, "land": 0.14, "waste": 0.05, "biodiversity_pressure": 0.04, "housing_land": 0.15},
    "Energy": {"materials": 0.11, "water": 0.07, "land": 0.06, "waste": 0.08, "biodiversity_pressure": 0.07},
    "Transport": {"materials": 0.07, "water": 0.03, "land": 0.06, "waste": 0.07, "biodiversity_pressure": 0.06},
    "Health": {"materials": 0.08, "water": 0.05, "land": 0.02, "waste": 0.12, "biodiversity_pressure": 0.03},
    "Education": {"materials": 0.04, "water": 0.03, "land": 0.03, "waste": 0.04, "biodiversity_pressure": 0.02, "compute_energy": 0.03},
    "Finance": {"materials": 0.02, "water": 0.02, "land": 0.02, "waste": 0.02, "biodiversity_pressure": 0.01, "compute_energy": 0.07},
    "DigitalPlatform": {"materials": 0.06, "water": 0.06, "land": 0.02, "waste": 0.04, "biodiversity_pressure": 0.02, "compute_energy": 0.22},
    "ProfessionalServices": {"materials": 0.03, "water": 0.02, "land": 0.02, "waste": 0.03, "biodiversity_pressure": 0.01, "compute_energy": 0.05},
    "Exportables": {"materials": 0.18, "water": 0.07, "land": 0.05, "waste": 0.12, "biodiversity_pressure": 0.06},
    "GovernmentSupply": {"materials": 0.07, "water": 0.05, "land": 0.05, "waste": 0.07, "biodiversity_pressure": 0.04},
}


def clamp(x: float, lo: float, hi: float) -> float:
    return base.clamp(x, lo, hi)


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    return base.safe_div(a, b, default)


def logistic(x: float) -> float:
    return base.logistic(x)


def mean(xs: Iterable[float], default: float = 0.0) -> float:
    return base.mean(xs, default)


def median(xs: Iterable[float], default: float = 0.0) -> float:
    return base.median(xs, default)


def gini(xs: Iterable[float]) -> float:
    return base.gini(xs)


def ffrac(x: float, denominator: int = TRUTH_DENOMINATOR) -> Fraction:
    """Convert a bounded fuzzy float to an exact rational approximation."""
    x = clamp(float(x), -1.0, 1.0)
    return Fraction(int(round(x * denominator)), denominator)


def amount_fraction(amount: float) -> Fraction:
    """Fiat amount -> rational cent-like scale, kept bounded for PyPy speed."""
    if not math.isfinite(amount):
        amount = 0.0
    amount = max(0.0, min(float(amount), 1_000_000_000.0))
    return Fraction(int(round(amount * 100.0)), 100)


def limit(fr: Fraction) -> Fraction:
    return fr.limit_denominator(TRUTH_MAX_DENOMINATOR)


def frac_float(fr: Fraction) -> float:
    return float(fr.numerator) / float(fr.denominator)


def stack_fuzzy_bits(bits: Sequence[float], weights: Optional[Sequence[float]] = None) -> Fraction:
    """
    Stack fuzzy truth bits into a rational number.

    This is the key alternative-number interpretation in the model:
    a number is not only a scalar, but a stack of checked propositions.
    The stack is stored as an exact rational average of bounded fuzzy bits.
    """
    if not bits:
        return Fraction(0, 1)
    if weights is None:
        weights = [1.0 for _ in bits]
    numerator = Fraction(0, 1)
    denominator = Fraction(0, 1)
    for bit, weight in zip(bits, weights):
        w = Fraction(max(0.0, float(weight))).limit_denominator(1000)
        numerator += ffrac(bit) * w
        denominator += w
    if denominator <= 0:
        return Fraction(0, 1)
    return limit(numerator / denominator)


def truth_units_from_money(amount: float, truth_value: Fraction, intensity: float) -> Fraction:
    # sqrt scaling prevents gigantic economies from making the truth ledger unusably huge.
    scaled = math.sqrt(max(0.0, amount)) * max(0.0, intensity)
    return limit(amount_fraction(scaled) * truth_value)


@dataclass
class TruthSimulationConfig(base.SimulationConfig):
    truth_currency_name: str = "TCR"
    truth_currency_enabled: bool = True
    truth_initial_price: float = 1.0
    truth_market_intensity: float = 0.18
    truth_verification_intensity: float = 0.10
    truth_resource_strictness: float = 1.35
    truth_trade_fraction: float = 0.10
    truth_meta_verification_rate: float = 0.15
    truth_min_credit_score: float = -0.35
    truth_quota_scale: float = 1.0
    truth_audit_sample: int = 32
    truth_print_events: bool = False


@dataclass
class FuzzyPredicateEvidence:
    subject_kind: str
    subject_id: int
    name: str
    arity: int
    verification_depth: int
    truth: Fraction
    amount_ecu: float
    dimensions: Tuple[str, ...]

    def as_jsonable(self) -> Dict[str, Any]:
        return {
            "subject_kind": self.subject_kind,
            "subject_id": self.subject_id,
            "name": self.name,
            "arity": self.arity,
            "verification_depth": self.verification_depth,
            "truth": frac_float(self.truth),
            "truth_rational": f"{self.truth.numerator}/{self.truth.denominator}",
            "amount_ecu": self.amount_ecu,
            "dimensions": list(self.dimensions),
        }


@dataclass
class ResourceBand:
    name: str
    ideal: float
    soft: float
    hard: float
    catastrophic: float

    def fuzzy_truth(self, usage: float) -> float:
        usage = max(0.0, usage)
        if usage <= self.ideal:
            return 1.0
        if usage <= self.soft:
            return clamp(1.0 - 0.55 * safe_div(usage - self.ideal, self.soft - self.ideal, 0.0), 0.45, 1.0)
        if usage <= self.hard:
            return clamp(0.45 - 1.15 * safe_div(usage - self.soft, self.hard - self.soft, 0.0), -0.70, 0.45)
        if usage <= self.catastrophic:
            return clamp(-0.70 - 0.30 * safe_div(usage - self.hard, self.catastrophic - self.hard, 0.0), -1.0, -0.70)
        return -1.0

    def overshoot_ratio(self, usage: float) -> float:
        return max(0.0, safe_div(usage - self.soft, max(EPS, self.hard - self.soft), 0.0))


@dataclass
class TruthModel:
    model_id: int
    owner_kind: str
    owner_id: int
    sector: str
    quality: float
    verification_depth: int
    arity: int
    market_share: float
    price_ecu: float
    truth_assets: Fraction = Fraction(0, 1)
    last_royalty_ecu: float = 0.0
    last_royalty_truth: Fraction = Fraction(0, 1)
    alive: bool = True


class TruthCurrencyMarket:
    """Predicate-currency, resource quota, audit, and correctness-model market."""

    def __init__(self, config: TruthSimulationConfig, rng: random.Random) -> None:
        self.config = config
        self.rng = rng
        self.currency_name = config.truth_currency_name
        self.price_ecu = max(0.001, config.truth_initial_price)
        self.total_positive_issued = Fraction(0, 1)
        self.total_negative_issued = Fraction(0, 1)
        self.trade_volume_truth = Fraction(0, 1)
        self.trade_volume_ecu = 0.0
        self.last_trade_volume_truth = Fraction(0, 1)
        self.last_trade_volume_ecu = 0.0
        self.resource_bands: Dict[str, ResourceBand] = {}
        self.resource_usage: Dict[str, float] = {r: 0.0 for r in RESOURCE_NAMES}
        self.resource_truth: Dict[str, float] = {r: 1.0 for r in RESOURCE_NAMES}
        self.resource_overshoot: Dict[str, float] = {r: 0.0 for r in RESOURCE_NAMES}
        self.planetary_truth: Fraction = Fraction(1, 1)
        self.active_resource_throttle: float = 1.0
        self.last_resource_throttle: float = 1.0
        self.max_resource_overshoot: float = 0.0
        self.models: Dict[int, TruthModel] = {}
        self.next_model_id: int = 1
        self.ledger_recent: List[FuzzyPredicateEvidence] = []
        self.predicate_count: int = 0
        self.verification_count: int = 0
        self.falsification_count: int = 0
        self.meta_verification_count: int = 0
        self._configure_bands(config)

    # ------------------------------------------------------------------
    # Setup and dynamic agent attributes
    # ------------------------------------------------------------------

    def _configure_bands(self, config: TruthSimulationConfig) -> None:
        scale = max(0.25, config.truth_quota_scale) * max(0.25, config.households / 300.0)
        # Per-step fuzzy quota bands. hard/catastrophic represent violations.
        base_ideal = {
            "energy_total": 34.0,
            "fossil_energy": 20.0,
            "emissions": 23.0,
            "materials": 42.0,
            "water": 36.0,
            "land": 22.0,
            "waste": 20.0,
            "biodiversity_pressure": 18.0,
            "compute_energy": 10.0,
            "housing_land": 9.0,
        }
        for name, ideal in base_ideal.items():
            ideal *= scale
            self.resource_bands[name] = ResourceBand(
                name=name,
                ideal=ideal,
                soft=ideal * 1.18,
                hard=ideal * 1.55,
                catastrophic=ideal * 2.15,
            )

    def attach_initial_balances(self, world: "TruthEconomicWorld") -> None:
        for h in world.households:
            score = 0.20 + 0.40 * h.education + 0.20 * h.health - 0.16 * safe_div(h.debt + h.mortgage, max(1.0, h.wealth() + h.last_income + 1.0), 0.0)
            setattr(h, "truth_balance", limit(Fraction(int(max(0.0, score) * 1200), 100)))
            setattr(h, "truth_debt", Fraction(0, 1))
            setattr(h, "knowledge_balance", limit(Fraction(int(h.education * 700), 100)))
            setattr(h, "last_truth_delta", Fraction(0, 1))
            setattr(h, "last_truth_score", clamp(score * 2.0 - 1.0, -1.0, 1.0))
            setattr(h, "predicate_arity", 5 + int(5 * h.education))
            setattr(h, "verification_depth", 0)
            setattr(h, "truth_model_shares", Fraction(0, 1))
        for f in world.firms:
            clean = 1.0 - clamp(1.4 * f.emissions_intensity + 0.8 * f.energy_intensity, 0.0, 1.0)
            score = 0.25 + 0.25 * f.innovation + 0.25 * clean + 0.15 * f.quality - 0.15 * f.leverage()
            setattr(f, "truth_balance", limit(Fraction(int(max(0.0, score) * 1800), 100)))
            setattr(f, "truth_debt", Fraction(0, 1))
            setattr(f, "last_truth_delta", Fraction(0, 1))
            setattr(f, "last_truth_score", clamp(score * 2.0 - 1.0, -1.0, 1.0))
            setattr(f, "predicate_arity", 8)
            setattr(f, "verification_depth", 0)
            setattr(f, "last_resource_vector", {r: 0.0 for r in RESOURCE_NAMES})
            setattr(f, "last_resource_overshoot", 0.0)
            setattr(f, "correctness_model_quality", clamp(score, 0.05, 1.0))
            mid = self._create_model("firm", f.fid, f.sector, clamp(score, 0.05, 1.0), market_share=1.0 / max(1, len(world.firms)))
            setattr(f, "correctness_model_id", mid)
        for b in world.banks:
            score = clamp(0.35 + 2.5 * (b.capital_ratio() - world.config.bank_capital_requirement) + 0.25 * b.liquidity_ratio(), 0.0, 1.0)
            setattr(b, "truth_balance", limit(Fraction(int(score * 1600), 100)))
            setattr(b, "truth_debt", Fraction(0, 1))
            setattr(b, "last_truth_delta", Fraction(0, 1))
            setattr(b, "last_truth_score", score * 2.0 - 1.0)
            setattr(b, "predicate_arity", 9)
            setattr(b, "verification_depth", 0)
            setattr(b, "balance_sheet_truth", score)
        gscore = 0.45 + 0.15 * world.government.public_education_quality + 0.15 * world.government.public_health_quality
        setattr(world.government, "truth_balance", limit(Fraction(int(gscore * 2500), 100)))
        setattr(world.government, "truth_debt", Fraction(0, 1))
        setattr(world.government, "last_truth_delta", Fraction(0, 1))
        setattr(world.government, "last_truth_score", clamp(gscore * 2.0 - 1.0, -1.0, 1.0))
        setattr(world.government, "predicate_arity", 12)
        setattr(world.government, "verification_depth", 0)
        self._renormalize_model_shares()

    def _create_model(self, owner_kind: str, owner_id: int, sector: str, quality: float, market_share: float) -> int:
        model_id = self.next_model_id
        self.next_model_id += 1
        self.models[model_id] = TruthModel(
            model_id=model_id,
            owner_kind=owner_kind,
            owner_id=owner_id,
            sector=sector,
            quality=clamp(quality, 0.0, 1.0),
            verification_depth=max(0, int(quality * 3)),
            arity=6 + int(quality * 12),
            market_share=max(0.0, market_share),
            price_ecu=clamp(0.10 + 1.40 * quality, 0.05, 5.0),
            truth_assets=limit(Fraction(int(max(0.0, quality) * 1000), 100)),
        )
        return model_id

    def _renormalize_model_shares(self) -> None:
        alive = [m for m in self.models.values() if m.alive]
        total = sum(max(0.0, m.market_share) for m in alive)
        if total <= EPS and alive:
            for m in alive:
                m.market_share = 1.0 / len(alive)
        elif total > 0:
            for m in alive:
                m.market_share = max(0.0, m.market_share) / total

    def ensure_agent(self, world: "TruthEconomicWorld", kind: str, agent_id: int = 0) -> Any:
        agent = self.get_agent(world, kind, agent_id)
        if agent is None:
            return None
        if not hasattr(agent, "truth_balance"):
            setattr(agent, "truth_balance", Fraction(0, 1))
        if not hasattr(agent, "truth_debt"):
            setattr(agent, "truth_debt", Fraction(0, 1))
        if not hasattr(agent, "last_truth_delta"):
            setattr(agent, "last_truth_delta", Fraction(0, 1))
        if not hasattr(agent, "last_truth_score"):
            setattr(agent, "last_truth_score", 0.0)
        if not hasattr(agent, "predicate_arity"):
            setattr(agent, "predicate_arity", 4)
        if not hasattr(agent, "verification_depth"):
            setattr(agent, "verification_depth", 0)
        return agent

    def get_agent(self, world: "TruthEconomicWorld", kind: str, agent_id: int = 0) -> Any:
        if kind == "household":
            return world.household_by_id(agent_id)
        if kind == "firm":
            return world.firm_by_id(agent_id)
        if kind == "bank":
            if 0 <= agent_id < len(world.banks):
                return world.banks[agent_id]
        if kind == "government":
            return world.government
        return None

    # ------------------------------------------------------------------
    # Resource ledger and fuzzy quota logic
    # ------------------------------------------------------------------

    def begin_step(self, world: "TruthEconomicWorld") -> None:
        self.last_trade_volume_truth = Fraction(0, 1)
        self.last_trade_volume_ecu = 0.0
        self.resource_usage = {r: 0.0 for r in RESOURCE_NAMES}
        for agent in list(world.households) + list(world.firms) + list(world.banks) + [world.government]:
            if hasattr(agent, "last_truth_delta"):
                setattr(agent, "last_truth_delta", Fraction(0, 1))
        # Previous quota overshoot throttles current production/consumption.
        self.active_resource_throttle = self._compute_throttle_from_previous_overshoot()
        self.last_resource_throttle = self.active_resource_throttle

    def _compute_throttle_from_previous_overshoot(self) -> float:
        worst = max(self.resource_overshoot.values()) if self.resource_overshoot else 0.0
        self.max_resource_overshoot = worst
        if worst <= 0:
            return 1.0
        # One exceeded quota forces all other resource access sharply lower.
        # The lower bound intentionally allows survival while making violation painful.
        return clamp(1.0 / (1.0 + self.config.truth_resource_strictness * 4.0 * worst), 0.08, 1.0)

    def production_throttle_for_firm(self, firm: Any) -> float:
        own = getattr(firm, "last_resource_overshoot", 0.0)
        model_quality = getattr(firm, "correctness_model_quality", 0.5)
        truth_score = getattr(firm, "last_truth_score", 0.0)
        repair = 1.0 + 0.18 * max(0.0, truth_score) + 0.15 * model_quality
        penalty = 1.0 / (1.0 + 1.8 * max(0.0, own))
        return clamp(self.active_resource_throttle * repair * penalty, 0.05, 1.15)

    def consumption_throttle_for_household(self, household: Any) -> float:
        score = getattr(household, "last_truth_score", 0.0)
        return clamp(self.active_resource_throttle * (1.0 + 0.10 * max(0.0, score)), 0.10, 1.05)

    def post_production_resource_accounting(self, world: "TruthEconomicWorld") -> None:
        for f in world.firms:
            if not f.alive():
                continue
            vector = self._firm_resource_vector(world, f, max(0.0, f.output))
            setattr(f, "last_resource_vector", vector)
            for name, amount in vector.items():
                self.resource_usage[name] += amount
        # Direct household energy/material/waste footprint from consumption.
        for h in world.households:
            consumption = max(0.0, h.last_consumption)
            if consumption <= 0:
                continue
            direct_energy = consumption * 0.012 * (1.0 + 0.25 * h.children) * h.energy_efficiency
            self.resource_usage["energy_total"] += direct_energy
            self.resource_usage["fossil_energy"] += direct_energy * (1.0 - world.energy_market.renewable_share)
            self.resource_usage["emissions"] += direct_energy * 0.42 * (1.0 - world.energy_market.renewable_share)
            self.resource_usage["waste"] += consumption * 0.006
            self.resource_usage["water"] += consumption * 0.004
        self._finalize_resource_truth(world)

    def _firm_resource_vector(self, world: "TruthEconomicWorld", f: Any, output: float) -> Dict[str, float]:
        vector = {r: 0.0 for r in RESOURCE_NAMES}
        energy = output * max(0.0, f.energy_intensity)
        fossil = energy * (1.0 - world.energy_market.renewable_share)
        emissions = output * max(0.0, f.emissions_intensity) * (1.0 - world.energy_market.renewable_share)
        vector["energy_total"] = energy
        vector["fossil_energy"] = fossil
        vector["emissions"] = emissions
        extras = SECTOR_RESOURCE_EXTRAS.get(f.sector, {})
        for name, intensity in extras.items():
            vector[name] = output * intensity
        if f.sector == "DigitalPlatform":
            vector["compute_energy"] += output * 0.08 * (1.0 + world.platform_market.user_share)
        if f.sector == "HousingServices":
            vector["housing_land"] += output * 0.05 * world.housing_market.last_new_units
        return vector

    def _finalize_resource_truth(self, world: "TruthEconomicWorld") -> None:
        truths = []
        overs = []
        for name in RESOURCE_NAMES:
            band = self.resource_bands[name]
            usage = self.resource_usage.get(name, 0.0)
            tv = band.fuzzy_truth(usage)
            ov = band.overshoot_ratio(usage)
            self.resource_truth[name] = tv
            self.resource_overshoot[name] = ov
            truths.append(tv)
            overs.append(ov)
        self.planetary_truth = stack_fuzzy_bits(truths)
        self.max_resource_overshoot = max(overs) if overs else 0.0
        for f in world.firms:
            vector = getattr(f, "last_resource_vector", None)
            if not vector:
                continue
            firm_overs = []
            for name, amount in vector.items():
                # The firm is judged against a proportional share of the planetary band.
                alive = max(1, sum(1 for x in world.firms if x.alive()))
                band = self.resource_bands[name]
                share_band = ResourceBand(name, band.ideal / alive * 1.8, band.soft / alive * 1.8, band.hard / alive * 1.8, band.catastrophic / alive * 1.8)
                firm_overs.append(share_band.overshoot_ratio(amount))
            setattr(f, "last_resource_overshoot", mean(firm_overs, 0.0))

    # ------------------------------------------------------------------
    # Truth scoring and predicate money flows
    # ------------------------------------------------------------------

    def record_money_flow(
        self,
        world: "TruthEconomicWorld",
        kind: str,
        agent_id: int,
        amount: float,
        predicate_name: str,
        bits: Sequence[float],
        dimensions: Sequence[str],
        verification_depth: Optional[int] = None,
    ) -> Fraction:
        if not self.config.truth_currency_enabled or amount <= EPS:
            return Fraction(0, 1)
        agent = self.ensure_agent(world, kind, agent_id)
        if agent is None:
            return Fraction(0, 1)
        depth = getattr(agent, "verification_depth", 0) if verification_depth is None else verification_depth
        stack = stack_fuzzy_bits(bits)
        arity = len(bits) + len(dimensions) + 2 + int(depth)
        delta = truth_units_from_money(amount, stack, self.config.truth_market_intensity)
        self.issue_truth(agent, delta)
        setattr(agent, "predicate_arity", max(getattr(agent, "predicate_arity", 0), arity))
        evidence = FuzzyPredicateEvidence(kind, agent_id, predicate_name, arity, int(depth), stack, amount, tuple(dimensions))
        self.ledger_recent.append(evidence)
        self.ledger_recent = self.ledger_recent[-200:]
        self.predicate_count += 1
        return delta

    def issue_truth(self, agent: Any, delta: Fraction) -> None:
        delta = limit(delta)
        balance = getattr(agent, "truth_balance", Fraction(0, 1))
        debt = getattr(agent, "truth_debt", Fraction(0, 1))
        if delta >= 0:
            if debt > 0:
                repay = min(delta, debt)
                debt -= repay
                delta -= repay
            balance = limit(balance + delta)
            self.total_positive_issued = limit(self.total_positive_issued + max(Fraction(0, 1), delta))
        else:
            penalty = -delta
            if balance >= penalty:
                balance = limit(balance - penalty)
            else:
                debt = limit(debt + penalty - balance)
                balance = Fraction(0, 1)
            self.total_negative_issued = limit(self.total_negative_issued + penalty)
        setattr(agent, "truth_balance", balance)
        setattr(agent, "truth_debt", debt)
        setattr(agent, "last_truth_delta", limit(getattr(agent, "last_truth_delta", Fraction(0, 1)) + delta))

    def agent_truth_score(self, world: "TruthEconomicWorld", kind: str, agent_id: int = 0) -> float:
        agent = self.ensure_agent(world, kind, agent_id)
        if agent is None:
            return 0.0
        balance = frac_float(getattr(agent, "truth_balance", Fraction(0, 1)))
        debt = frac_float(getattr(agent, "truth_debt", Fraction(0, 1)))
        raw = safe_div(balance - debt, 8.0 + balance + debt, 0.0)
        last = getattr(agent, "last_truth_score", 0.0)
        return clamp(0.55 * last + 0.45 * raw * 2.0, -1.0, 1.0)

    def firm_correctness_bits(self, world: "TruthEconomicWorld", f: Any) -> List[float]:
        margin = safe_div(f.last_profit, max(1.0, f.last_revenue), 0.0)
        profit_truth = clamp(math.tanh(3.0 * margin), -1.0, 1.0)
        leverage_truth = clamp(1.0 - f.leverage() / 3.0, -1.0, 1.0)
        avg_wage = mean((h.wage for h in world.households if h.employed), 1.0)
        firm_wage = mean((world.household_by_id(hid).wage for hid in f.employees if world.household_by_id(hid)), avg_wage)
        worker_truth = clamp(2.0 * safe_div(firm_wage, max(0.1, avg_wage), 1.0) - 1.4, -1.0, 1.0)
        resource_truth = clamp(1.0 - 1.4 * getattr(f, "last_resource_overshoot", 0.0), -1.0, 1.0)
        clean_truth = clamp(1.0 - 2.2 * f.emissions_intensity - 0.8 * f.energy_intensity, -1.0, 1.0)
        demand_truth = clamp(1.0 - safe_div(f.last_unfilled_demand, max(1.0, f.expected_demand), 0.0), -1.0, 1.0)
        knowledge_truth = clamp(-0.25 + 0.8 * f.innovation + 0.35 * getattr(f, "correctness_model_quality", 0.5), -1.0, 1.0)
        return [profit_truth, leverage_truth, worker_truth, resource_truth, clean_truth, demand_truth, knowledge_truth]

    def household_correctness_bits(self, world: "TruthEconomicWorld", h: Any) -> List[float]:
        income = max(0.1, h.last_income)
        debt_ratio = safe_div(h.debt + h.mortgage, max(1.0, income * 12.0 + h.wealth()), 0.0)
        debt_truth = clamp(1.0 - 2.0 * debt_ratio, -1.0, 1.0)
        knowledge_truth = clamp(2.0 * h.education - 0.6, -1.0, 1.0)
        health_truth = clamp(2.0 * h.health - 0.8, -1.0, 1.0)
        tax_truth = clamp(1.0 - abs(safe_div(h.last_taxes, max(0.1, h.last_income), 0.0) - world.government.income_tax), -1.0, 1.0)
        consumption_truth = clamp(1.0 - 0.05 * max(0.0, h.last_consumption - income * 1.2), -1.0, 1.0)
        energy_truth = clamp(1.0 - max(0.0, h.energy_efficiency - 1.0), -1.0, 1.0)
        employment_truth = 0.40 if h.employed else (-0.20 if h.labor_force_member() else 0.10)
        return [debt_truth, knowledge_truth, health_truth, tax_truth, consumption_truth, energy_truth, employment_truth]

    def bank_correctness_bits(self, world: "TruthEconomicWorld", b: Any) -> List[float]:
        cap_truth = clamp(6.0 * (b.capital_ratio() - world.config.bank_capital_requirement), -1.0, 1.0)
        liq_truth = clamp(8.0 * (b.liquidity_ratio() - 0.04), -1.0, 1.0)
        npl = world.metrics_last.get("npl_ratio", 0.0)
        npl_truth = clamp(1.0 - 7.0 * npl, -1.0, 1.0)
        real_lending = 0.0
        total = 0.0
        for ln in b.loan_book.values():
            if ln.status == "performing":
                total += ln.principal
                if ln.purpose in {"investment", "green_investment", "mortgage", "working_capital"}:
                    real_lending += ln.principal
        lending_truth = clamp(2.0 * safe_div(real_lending, max(1.0, total), 0.5) - 1.0, -1.0, 1.0)
        return [cap_truth, liq_truth, npl_truth, lending_truth]

    def government_correctness_bits(self, world: "TruthEconomicWorld") -> List[float]:
        last = world.metrics_last
        debt_truth = clamp(1.0 - 1.6 * last.get("gov_debt_to_annual_gdp", 0.0), -1.0, 1.0)
        poverty_truth = clamp(1.0 - 3.0 * last.get("poverty_rate", 0.0), -1.0, 1.0)
        education_truth = clamp(2.0 * world.government.public_education_quality - 1.0, -1.0, 1.0)
        health_truth = clamp(2.0 * world.government.public_health_quality - 1.0, -1.0, 1.0)
        planet_truth = frac_float(self.planetary_truth)
        financial_truth = clamp(1.0 - last.get("financial_stress", 0.0), -1.0, 1.0)
        return [debt_truth, poverty_truth, education_truth, health_truth, planet_truth, financial_truth]

    def evaluate_and_issue_step(self, world: "TruthEconomicWorld") -> None:
        for f in world.firms:
            if not f.alive():
                continue
            bits = self.firm_correctness_bits(world, f)
            amount = max(1.0, abs(f.last_revenue) + abs(f.last_cost) + max(0.0, getattr(f, "planned_investment_budget", 0.0)))
            self.record_money_flow(world, "firm", f.fid, amount, "firm_operating_predicate", bits, [f.sector, f.region, "profit", "resource", "worker", "balance"])
            score = frac_float(stack_fuzzy_bits(bits))
            setattr(f, "last_truth_score", score)
        for h in world.households:
            bits = self.household_correctness_bits(world, h)
            amount = max(1.0, abs(h.last_income) + abs(h.last_consumption) + abs(h.last_taxes) + abs(h.rent_payment))
            self.record_money_flow(world, "household", h.hid, amount, "household_life_predicate", bits, [h.region, "income", "education", "health", "debt"])
            setattr(h, "last_truth_score", frac_float(stack_fuzzy_bits(bits)))
        for b in world.banks:
            if b.failed:
                continue
            bits = self.bank_correctness_bits(world, b)
            amount = max(1.0, b.deposits + b.total_loans() * 0.05 + abs(b.last_interest_income))
            self.record_money_flow(world, "bank", b.bid, amount, "bank_balance_sheet_predicate", bits, [b.region, "capital", "liquidity", "real_lending"])
            setattr(b, "last_truth_score", frac_float(stack_fuzzy_bits(bits)))
            setattr(b, "balance_sheet_truth", getattr(b, "last_truth_score", 0.0))
        gbits = self.government_correctness_bits(world)
        gamount = max(1.0, abs(world.government.last_revenue) + abs(world.government.last_spending) + abs(world.government.debt) * 0.02)
        self.record_money_flow(world, "government", 0, gamount, "state_planetary_balance_predicate", gbits, ["tax", "spending", "planet", "public_goods", "debt"])
        setattr(world.government, "last_truth_score", frac_float(stack_fuzzy_bits(gbits)))
        # Planetary overshoot is additionally charged to resource-intensive firms.
        if frac_float(self.planetary_truth) < 0:
            dirty = []
            for f in world.firms:
                if f.alive():
                    burden = sum(getattr(f, "last_resource_vector", {}).values())
                    if burden > 0:
                        dirty.append((f, burden))
            total_burden = sum(b for _, b in dirty)
            for f, burden in dirty:
                penalty_strength = -frac_float(self.planetary_truth) * safe_div(burden, max(EPS, total_burden), 0.0)
                self.issue_truth(f, -truth_units_from_money(100.0 * penalty_strength, Fraction(1, 1), self.config.truth_market_intensity))

    # ------------------------------------------------------------------
    # Verification, falsification, and meta-verification
    # ------------------------------------------------------------------

    def verify_and_falsify(self, world: "TruthEconomicWorld") -> None:
        sample_size = max(1, min(self.config.truth_audit_sample, len(world.firms) + len(world.households)))
        agents: List[Tuple[str, int]] = []
        if world.firms:
            agents.extend(("firm", f.fid) for f in self.rng.sample(world.firms, min(len(world.firms), sample_size // 2 + 1)))
        if world.households:
            agents.extend(("household", h.hid) for h in self.rng.sample(world.households, min(len(world.households), sample_size // 2 + 1)))
        if world.banks:
            agents.extend(("bank", b.bid) for b in self.rng.sample(world.banks, min(len(world.banks), 2)))
        agents.append(("government", 0))

        for kind, aid in agents:
            agent = self.ensure_agent(world, kind, aid)
            if agent is None:
                continue
            declared = getattr(agent, "last_truth_score", 0.0)
            # Audits are better when the economy has education, model quality, and lower stress.
            verification_power = 0.45 + 0.20 * world.government.public_education_quality + 0.10 * max(0.0, frac_float(self.planetary_truth))
            noise = self.rng.gauss(0.0, 0.18 / max(0.25, verification_power))
            observed = clamp(declared + noise, -1.0, 1.0)
            verified = observed >= -0.05 or declared >= 0.25
            setattr(agent, "verification_depth", getattr(agent, "verification_depth", 0) + 1)
            setattr(agent, "predicate_arity", getattr(agent, "predicate_arity", 0) + 1)
            self.verification_count += 1
            if verified:
                self.issue_truth(agent, truth_units_from_money(4.0 + 7.0 * max(0.0, observed), ffrac(observed), self.config.truth_verification_intensity))
            else:
                self.issue_truth(agent, -truth_units_from_money(6.0 + 10.0 * abs(observed), Fraction(1, 1), self.config.truth_verification_intensity))
                self.falsification_count += 1
            # Verification of the verification: one more logical element.
            if self.rng.random() < self.config.truth_meta_verification_rate:
                setattr(agent, "verification_depth", getattr(agent, "verification_depth", 0) + 1)
                setattr(agent, "predicate_arity", getattr(agent, "predicate_arity", 0) + 1)
                self.meta_verification_count += 1
                meta_truth = clamp(observed + self.rng.gauss(0.0, 0.10), -1.0, 1.0)
                self.issue_truth(agent, truth_units_from_money(2.0 + 3.0 * abs(meta_truth), ffrac(meta_truth), self.config.truth_verification_intensity * 0.55))

    # ------------------------------------------------------------------
    # Tradeable currency market and correctness-model market
    # ------------------------------------------------------------------

    def trade_truth_currency(self, world: "TruthEconomicWorld") -> None:
        sellers: List[Tuple[str, int, Fraction]] = []
        buyers: List[Tuple[str, int, float, float]] = []  # kind, id, desired_truth, max_cash

        for h in world.households:
            bal = getattr(h, "truth_balance", Fraction(0, 1))
            score = getattr(h, "last_truth_score", 0.0)
            if frac_float(bal) > 1.0 and score > 0.10:
                need_cash = h.cash < h.liquidity_need()
                frac = 0.05 if need_cash else 0.010
                sellers.append(("household", h.hid, limit(bal * Fraction(int(frac * 1000), 1000))))
            if getattr(h, "truth_debt", Fraction(0, 1)) > 0 and h.cash > 0.5:
                desired = min(frac_float(getattr(h, "truth_debt")), h.cash / max(0.001, self.price_ecu) * 0.20)
                buyers.append(("household", h.hid, desired, h.cash * 0.20))

        for f in world.firms:
            if not f.alive():
                continue
            bal = getattr(f, "truth_balance", Fraction(0, 1))
            score = getattr(f, "last_truth_score", 0.0)
            if frac_float(bal) > 1.5 and (f.cash < 0 or score > 0.20):
                frac = 0.10 if f.cash < 0 else 0.025
                sellers.append(("firm", f.fid, limit(bal * Fraction(int(frac * 1000), 1000))))
            # Demand truth units if model/resource correctness is weak.
            deficit = max(0.0, 0.35 - score) + 0.65 * getattr(f, "last_resource_overshoot", 0.0)
            if deficit > 0.02 and f.cash > 0.5:
                desired = min(12.0 * deficit + frac_float(getattr(f, "truth_debt", Fraction(0, 1))) * 0.5, f.cash / max(0.001, self.price_ecu) * 0.35)
                buyers.append(("firm", f.fid, desired, f.cash * 0.35))

        for b in world.banks:
            if b.failed:
                continue
            bal = getattr(b, "truth_balance", Fraction(0, 1))
            if frac_float(bal) > 2.0 and b.capital_ratio() < world.config.bank_capital_requirement * 1.1:
                sellers.append(("bank", b.bid, limit(bal * Fraction(5, 100))))
            deficit = max(0.0, world.config.bank_capital_requirement - b.capital_ratio()) + max(0.0, -getattr(b, "last_truth_score", 0.0))
            if deficit > 0.01 and b.reserves > 1.0:
                buyers.append(("bank", b.bid, min(20.0 * deficit, b.reserves / max(0.001, self.price_ecu) * 0.15), b.reserves * 0.15))

        gbal = getattr(world.government, "truth_balance", Fraction(0, 1))
        if frac_float(gbal) > 5.0 and world.government.cash < 0:
            sellers.append(("government", 0, limit(gbal * Fraction(3, 100))))
        if frac_float(self.planetary_truth) < 0 and world.government.cash > 0.0:
            buyers.append(("government", 0, min(30.0 * -frac_float(self.planetary_truth), max(0.0, world.government.cash) / max(0.001, self.price_ecu) * 0.25), max(0.0, world.government.cash) * 0.25))

        supply_truth = sum(frac_float(x[2]) for x in sellers)
        desired_truth = sum(x[2] for x in buyers)
        demand_cash = sum(x[3] for x in buyers)
        if supply_truth <= EPS or desired_truth <= EPS or demand_cash <= EPS:
            self.price_ecu = clamp(self.price_ecu * (1.0 + 0.02 * self.max_resource_overshoot - 0.005), 0.01, 100.0)
            return
        target_price = clamp(demand_cash / max(EPS, supply_truth), 0.01, 100.0)
        scarcity_premium = 1.0 + 0.35 * self.max_resource_overshoot + 0.15 * max(0.0, -frac_float(self.planetary_truth))
        self.price_ecu = clamp(0.82 * self.price_ecu + 0.18 * target_price * scarcity_premium, 0.01, 100.0)

        executed_truth = min(supply_truth, desired_truth)
        if executed_truth <= EPS:
            return
        # First collect seller offers.
        actual_supply: List[Tuple[str, int, Fraction]] = []
        for kind, aid, offered in sellers:
            agent = self.ensure_agent(world, kind, aid)
            if agent is None:
                continue
            bal = getattr(agent, "truth_balance", Fraction(0, 1))
            sell = min(offered, bal)
            if sell <= 0:
                continue
            actual_supply.append((kind, aid, sell))
        supply_total = sum(frac_float(x[2]) for x in actual_supply)
        if supply_total <= EPS:
            return
        demand_total = sum(x[2] for x in buyers)
        # Sell proportionally.
        for kind, aid, sell in actual_supply:
            agent = self.ensure_agent(world, kind, aid)
            share = frac_float(sell) / supply_total
            sell_units = limit(sell * Fraction(int(min(1.0, executed_truth / supply_total) * 1_000_000), 1_000_000))
            ecu = frac_float(sell_units) * self.price_ecu
            self._set_agent_cash(world, kind, aid, self._get_agent_cash(world, kind, aid) + ecu)
            setattr(agent, "truth_balance", limit(getattr(agent, "truth_balance", Fraction(0, 1)) - sell_units))
            self.last_trade_volume_truth = limit(self.last_trade_volume_truth + sell_units)
            self.last_trade_volume_ecu += ecu
        # Buy proportionally.
        for kind, aid, desired, max_cash in buyers:
            agent = self.ensure_agent(world, kind, aid)
            if agent is None or desired <= 0:
                continue
            share = desired / max(EPS, demand_total)
            buy_units = executed_truth * share
            cost = min(max_cash, buy_units * self.price_ecu, max(0.0, self._get_agent_cash(world, kind, aid)))
            if cost <= EPS:
                continue
            units = limit(amount_fraction(cost / max(0.001, self.price_ecu)))
            self._set_agent_cash(world, kind, aid, self._get_agent_cash(world, kind, aid) - cost)
            debt = getattr(agent, "truth_debt", Fraction(0, 1))
            if debt > 0:
                repay = min(units, debt)
                debt -= repay
                units -= repay
                setattr(agent, "truth_debt", debt)
            setattr(agent, "truth_balance", limit(getattr(agent, "truth_balance", Fraction(0, 1)) + units))
        self.trade_volume_truth = limit(self.trade_volume_truth + self.last_trade_volume_truth)
        self.trade_volume_ecu += self.last_trade_volume_ecu

    def _get_agent_cash(self, world: "TruthEconomicWorld", kind: str, aid: int) -> float:
        agent = self.get_agent(world, kind, aid)
        if agent is None:
            return 0.0
        if kind == "bank":
            return max(0.0, getattr(agent, "reserves", 0.0))
        return float(getattr(agent, "cash", 0.0))

    def _set_agent_cash(self, world: "TruthEconomicWorld", kind: str, aid: int, value: float) -> None:
        agent = self.get_agent(world, kind, aid)
        if agent is None:
            return
        value = float(value)
        if kind == "bank":
            setattr(agent, "reserves", value)
        else:
            setattr(agent, "cash", value)

    def update_model_market(self, world: "TruthEconomicWorld") -> None:
        if not self.models:
            return
        # Update owner model qualities by observed correctness and economic success.
        for m in self.models.values():
            if not m.alive:
                continue
            owner = self.get_agent(world, m.owner_kind, m.owner_id)
            if owner is None or (m.owner_kind == "firm" and getattr(owner, "bankrupt", False)):
                m.alive = False
                continue
            owner_score = getattr(owner, "last_truth_score", 0.0)
            profit_signal = 0.0
            if m.owner_kind == "firm":
                profit_signal = clamp(math.tanh(2.0 * safe_div(getattr(owner, "last_profit", 0.0), max(1.0, getattr(owner, "last_revenue", 0.0)), 0.0)), -1.0, 1.0)
            q_target = clamp(0.55 * ((owner_score + 1.0) / 2.0) + 0.25 * ((profit_signal + 1.0) / 2.0) + 0.20 * max(0.0, frac_float(self.planetary_truth)), 0.0, 1.0)
            m.quality = clamp(0.90 * m.quality + 0.10 * q_target, 0.0, 1.0)
            m.price_ecu = clamp(0.06 + 1.8 * m.quality + 0.08 * m.verification_depth, 0.02, 12.0)
            if self.rng.random() < 0.02 + 0.06 * m.quality:
                m.verification_depth += 1
                m.arity += 1
                m.truth_assets = limit(m.truth_assets + truth_units_from_money(2.0 + 5.0 * m.quality, ffrac(2.0 * m.quality - 1.0), self.config.truth_verification_intensity))
        # Model share competition.
        by_sector: Dict[str, List[TruthModel]] = defaultdict(list)
        for m in self.models.values():
            if m.alive:
                by_sector[m.sector].append(m)
        for sector, models in by_sector.items():
            attractiveness = []
            for m in models:
                att = math.exp(3.0 * m.quality + 0.04 * m.verification_depth - 0.08 * m.price_ecu)
                attractiveness.append(att)
            total = sum(attractiveness)
            for m, att in zip(models, attractiveness):
                target_share = att / max(EPS, total)
                m.market_share = 0.88 * m.market_share + 0.12 * target_share
        self._renormalize_model_shares()
        # Firms buy/copy better models. This makes correctness itself competitive.
        for f in world.firms:
            if not f.alive():
                continue
            sector_models = [m for m in self.models.values() if m.alive and m.sector == f.sector]
            if not sector_models:
                continue
            current_quality = getattr(f, "correctness_model_quality", 0.5)
            best = max(sector_models, key=lambda m: m.quality + 0.08 * m.verification_depth)
            if best.quality > current_quality + 0.03 and f.cash > best.price_ecu and self.rng.random() < 0.04 + 0.10 * best.market_share:
                fee = min(f.cash * 0.025, best.price_ecu)
                f.cash -= fee
                owner = self.get_agent(world, best.owner_kind, best.owner_id)
                if owner is not None:
                    if best.owner_kind == "bank":
                        owner.reserves += fee
                    else:
                        owner.cash += fee
                # Truth royalty: model owner receives verified model-money.
                royalty = truth_units_from_money(fee, ffrac(2.0 * best.quality - 1.0), self.config.truth_market_intensity)
                best.last_royalty_ecu = fee
                best.last_royalty_truth = royalty
                best.truth_assets = limit(best.truth_assets + royalty)
                if owner is not None:
                    self.issue_truth(owner, royalty)
                setattr(f, "correctness_model_id", best.model_id)
                setattr(f, "correctness_model_quality", clamp(0.88 * current_quality + 0.12 * best.quality, 0.0, 1.0))
                setattr(f, "verification_depth", max(getattr(f, "verification_depth", 0), best.verification_depth))
                setattr(f, "predicate_arity", max(getattr(f, "predicate_arity", 0), best.arity))

    def end_step(self, world: "TruthEconomicWorld") -> None:
        if not self.config.truth_currency_enabled:
            return
        self.evaluate_and_issue_step(world)
        self.verify_and_falsify(world)
        self.trade_truth_currency(world)
        self.update_model_market(world)
        if self.config.truth_print_events and self.max_resource_overshoot > 0.25:
            world.events.add(world.t, f"Truth-resource throttling active: overshoot={self.max_resource_overshoot:.3f}, throttle={self.active_resource_throttle:.3f}.")

    # ------------------------------------------------------------------
    # Metrics
    # ------------------------------------------------------------------

    def add_metrics(self, row: Dict[str, float], world: "TruthEconomicWorld") -> None:
        firm_scores = [getattr(f, "last_truth_score", 0.0) for f in world.firms if f.alive()]
        household_scores = [getattr(h, "last_truth_score", 0.0) for h in world.households]
        bank_scores = [getattr(b, "last_truth_score", 0.0) for b in world.banks if not b.failed]
        truth_balances = []
        truth_debts = []
        predicate_arities = []
        verification_depths = []
        for agent in list(world.households) + list(world.firms) + list(world.banks) + [world.government]:
            if hasattr(agent, "truth_balance"):
                truth_balances.append(frac_float(getattr(agent, "truth_balance", Fraction(0, 1))))
                truth_debts.append(frac_float(getattr(agent, "truth_debt", Fraction(0, 1))))
                predicate_arities.append(float(getattr(agent, "predicate_arity", 0)))
                verification_depths.append(float(getattr(agent, "verification_depth", 0)))
        alive_models = [m for m in self.models.values() if m.alive]
        row["truth_price_ecu"] = self.price_ecu
        row["truth_currency_supply"] = sum(truth_balances)
        row["truth_debt_total"] = sum(truth_debts)
        row["truth_net_supply"] = sum(truth_balances) - sum(truth_debts)
        row["truth_trade_volume"] = frac_float(self.last_trade_volume_truth)
        row["truth_trade_volume_ecu"] = self.last_trade_volume_ecu
        row["truth_positive_issued_total"] = frac_float(self.total_positive_issued)
        row["truth_negative_issued_total"] = frac_float(self.total_negative_issued)
        row["truth_planetary_score"] = frac_float(self.planetary_truth)
        row["truth_resource_throttle"] = self.active_resource_throttle
        row["truth_max_resource_overshoot"] = self.max_resource_overshoot
        row["truth_avg_firm_score"] = mean(firm_scores, 0.0)
        row["truth_avg_household_score"] = mean(household_scores, 0.0)
        row["truth_avg_bank_score"] = mean(bank_scores, 0.0)
        row["truth_avg_predicate_arity"] = mean(predicate_arities, 0.0)
        row["truth_avg_verification_depth"] = mean(verification_depths, 0.0)
        row["truth_verification_count"] = float(self.verification_count)
        row["truth_falsification_count"] = float(self.falsification_count)
        row["truth_meta_verification_count"] = float(self.meta_verification_count)
        row["truth_model_count"] = float(len(alive_models))
        row["truth_model_top_quality"] = max((m.quality for m in alive_models), default=0.0)
        row["truth_model_concentration"] = base.hhi([m.market_share for m in alive_models]) if alive_models else 0.0
        for name in RESOURCE_NAMES:
            row[f"resource_use_{name}"] = self.resource_usage.get(name, 0.0)
            row[f"resource_truth_{name}"] = self.resource_truth.get(name, 0.0)
            row[f"resource_overshoot_{name}"] = self.resource_overshoot.get(name, 0.0)

    def summary(self, world: "TruthEconomicWorld") -> Dict[str, Any]:
        last = world.metrics[-1] if world.metrics else {}
        alive_models = [m for m in self.models.values() if m.alive]
        top_models = sorted(alive_models, key=lambda m: (m.market_share, m.quality), reverse=True)[:8]
        return {
            "truth_currency": self.currency_name,
            "final_truth_price_ecu": last.get("truth_price_ecu", self.price_ecu),
            "final_truth_planetary_score": last.get("truth_planetary_score", frac_float(self.planetary_truth)),
            "final_truth_resource_throttle": last.get("truth_resource_throttle", self.active_resource_throttle),
            "final_truth_max_resource_overshoot": last.get("truth_max_resource_overshoot", self.max_resource_overshoot),
            "final_truth_supply": last.get("truth_currency_supply", 0.0),
            "final_truth_debt_total": last.get("truth_debt_total", 0.0),
            "final_truth_net_supply": last.get("truth_net_supply", 0.0),
            "final_truth_avg_firm_score": last.get("truth_avg_firm_score", 0.0),
            "final_truth_avg_household_score": last.get("truth_avg_household_score", 0.0),
            "final_truth_avg_bank_score": last.get("truth_avg_bank_score", 0.0),
            "final_truth_avg_predicate_arity": last.get("truth_avg_predicate_arity", 0.0),
            "final_truth_avg_verification_depth": last.get("truth_avg_verification_depth", 0.0),
            "truth_verification_count": self.verification_count,
            "truth_falsification_count": self.falsification_count,
            "truth_meta_verification_count": self.meta_verification_count,
            "truth_total_trade_volume": frac_float(self.trade_volume_truth),
            "truth_total_trade_volume_ecu": self.trade_volume_ecu,
            "truth_top_correctness_models": [
                {
                    "model_id": m.model_id,
                    "sector": m.sector,
                    "owner_kind": m.owner_kind,
                    "owner_id": m.owner_id,
                    "quality": m.quality,
                    "verification_depth": m.verification_depth,
                    "arity": m.arity,
                    "market_share": m.market_share,
                    "price_ecu": m.price_ecu,
                    "truth_assets": frac_float(m.truth_assets),
                }
                for m in top_models
            ],
            "truth_recent_predicates": [ev.as_jsonable() for ev in self.ledger_recent[-12:]],
        }


class TruthEconomicWorld(base.EconomicWorld):
    def __init__(self, config: TruthSimulationConfig) -> None:
        self.truth_market: Optional[TruthCurrencyMarket] = None
        super().__init__(config)
        # Teach the base ScenarioEngine that truth-layer scenarios are handled
        # here, so it does not log them as unknown.
        for _name in ("truth_currency_transition", "planetary_overshoot", "greenwashing_crackdown", "knowledge_commons"):
            setattr(self.scenarios, f"_pre_{_name}", lambda world, t: None)
            setattr(self.scenarios, f"_post_{_name}", lambda world, t: None)
        self.truth_market = TruthCurrencyMarket(config, self.rng)
        self.truth_market.attach_initial_balances(self)
        self._truth_audit_initial_money_stock()
        self.metrics_last["truth_price_ecu"] = self.truth_market.price_ecu
        self.metrics_last["truth_planetary_score"] = 1.0
        self.metrics_last["truth_resource_throttle"] = 1.0

    def _book_loan(
        self,
        bank: Any,
        borrower_kind: str,
        borrower_id: int,
        amount: float,
        rate: float,
        maturity: int,
        collateral: float,
        purpose: str,
        add_cash: bool = True,
    ) -> Any:
        loan = super()._book_loan(bank, borrower_kind, borrower_id, amount, rate, maturity, collateral, purpose, add_cash)
        if getattr(self, "truth_market", None) is not None:
            if borrower_kind in {"household", "firm", "government"}:
                aid = borrower_id if borrower_kind != "government" else 0
                truth_score = self.truth_market.agent_truth_score(self, borrower_kind, aid)
                bank_score = self.truth_market.agent_truth_score(self, "bank", bank.bid)
                collateral_truth = clamp(2.0 * safe_div(collateral, max(1.0, amount), 0.0) - 1.0, -1.0, 1.0)
                leverage_truth = clamp(1.0 - 0.10 * maturity - 0.50 * max(0.0, rate), -1.0, 1.0)
                self.truth_market.record_money_flow(
                    self,
                    borrower_kind,
                    aid,
                    amount,
                    "credit_contract_predicate",
                    [truth_score, bank_score, collateral_truth, leverage_truth],
                    [purpose, "loan", "borrower", "bank", "collateral"],
                )
                self.truth_market.record_money_flow(
                    self,
                    "bank",
                    bank.bid,
                    amount,
                    "credit_issuer_predicate",
                    [bank_score, truth_score, collateral_truth],
                    [purpose, "loan_creation", "risk", "truth_collateral"],
                )
        return loan

    def request_firm_loan(self, firm: Any, amount: float, purpose: str = "working_capital", collateral: Optional[float] = None) -> bool:
        if amount <= EPS or firm.bankrupt:
            return False
        bank = self.banks[firm.bank_id]
        if bank.failed:
            candidates = [b for b in self.banks if not b.failed]
            if not candidates:
                return False
            bank = self.rng.choice(candidates)
            firm.bank_id = bank.bid
        collateral_value = firm.capital * 0.65 if collateral is None else collateral
        leverage = firm.leverage()
        stress = self.financial_market.financial_stress
        tightness = bank.credit_tightness(self.config.bank_capital_requirement, stress)
        firm_truth = self.truth_market.agent_truth_score(self, "firm", firm.fid) if self.truth_market else 0.0
        bank_truth = self.truth_market.agent_truth_score(self, "bank", bank.bid) if self.truth_market else 0.0
        truth_collateral = safe_div(frac_float(getattr(firm, "truth_balance", Fraction(0, 1))), max(1.0, amount), 0.0)
        rate = self.central_bank.policy_rate + self.financial_market.credit_spread + 0.025 + 0.035 * leverage + 0.020 * tightness
        rate -= 0.012 * max(0.0, firm_truth) + 0.006 * max(0.0, bank_truth)
        rate += 0.014 * max(0.0, -firm_truth)
        profitability = safe_div(firm.last_profit, max(1.0, firm.last_revenue), 0.0)
        score = (
            1.2 * bank.risk_appetite
            + 0.35 * profitability
            + 0.45 * safe_div(collateral_value, amount, 0.0)
            - 0.55 * leverage
            - 1.3 * tightness
            + 0.45 * firm_truth
            + 0.18 * bank_truth
            + 0.04 * min(10.0, truth_collateral)
        )
        if purpose == "green_investment":
            score += 0.15 + self.government.green_subsidy + 0.20 * max(0.0, firm_truth)
            rate -= self.government.green_subsidy * 0.25
        if firm_truth < self.config.truth_min_credit_score and purpose not in {"green_investment", "working_capital"}:
            score -= 0.45
        approve_prob = logistic(score)
        if self.rng.random() < approve_prob:
            self._book_loan(bank, "firm", firm.fid, amount, max(0.0, rate), 72 if purpose != "working_capital" else 18, collateral_value, purpose)
            return True
        return False

    def request_household_loan(self, household: Any, amount: float, purpose: str = "consumer", collateral: float = 0.0) -> bool:
        if amount <= EPS or household.defaulted:
            return False
        bank = self.banks[household.bank_id]
        if bank.failed:
            candidates = [b for b in self.banks if not b.failed]
            if not candidates:
                return False
            bank = self.rng.choice(candidates)
            household.bank_id = bank.bid
        income = max(0.5, household.last_income)
        total_debt = household.debt + household.mortgage + amount
        if purpose == "mortgage":
            if amount > collateral * self.config.max_mortgage_ltv:
                return False
            if total_debt > income * 12.0 * self.config.max_household_loan_to_income / 12.0:
                return False
        else:
            if total_debt > max(4.0, income * 6.0):
                return False
        household_truth = self.truth_market.agent_truth_score(self, "household", household.hid) if self.truth_market else 0.0
        bank_truth = self.truth_market.agent_truth_score(self, "bank", bank.bid) if self.truth_market else 0.0
        truth_collateral = safe_div(frac_float(getattr(household, "truth_balance", Fraction(0, 1))), max(1.0, amount), 0.0)
        tightness = bank.credit_tightness(self.config.bank_capital_requirement, self.financial_market.financial_stress)
        risk = 0.35 * household.risk_aversion + 0.45 * safe_div(total_debt, max(1.0, income * 12.0), 0.0) + 0.35 * (not household.employed)
        collateral_score = safe_div(collateral, amount, 0.0)
        score = (
            1.0 * bank.risk_appetite
            + 0.25 * collateral_score
            + 0.18 * household.education
            - risk
            - 1.1 * tightness
            + 0.35 * household_truth
            + 0.12 * bank_truth
            + 0.03 * min(10.0, truth_collateral)
        )
        approve_prob = logistic(score)
        if self.rng.random() < approve_prob:
            rate = self.central_bank.policy_rate + self.financial_market.credit_spread + (0.028 if purpose == "mortgage" else 0.075) + 0.025 * risk
            rate -= 0.010 * max(0.0, household_truth) + 0.004 * max(0.0, bank_truth)
            rate += 0.010 * max(0.0, -household_truth)
            maturity = 240 if purpose == "mortgage" else 48
            self._book_loan(bank, "household", household.hid, amount, max(0.0, rate), maturity, collateral, purpose)
            return True
        return False

    def _truth_audit_initial_money_stock(self) -> None:
        """Enter starting money/debt balances into predicate currency.

        The base simulator creates initial deposits, mortgages, consumer debt,
        and firm investment loans before the truth layer exists.  This audit makes
        the starting money stock participate in the same n-ary predicate logic as
        later transactions.
        """
        if self.truth_market is None:
            return
        for b in self.banks:
            self.truth_market.record_money_flow(
                self,
                "bank",
                b.bid,
                max(1.0, b.deposits + b.equity + b.reserves),
                "initial_bank_money_stock_predicate",
                self.truth_market.bank_correctness_bits(self, b),
                [b.region, "initial_money", "deposits", "equity", "reserves"],
                verification_depth=1,
            )
            for ln in b.loan_book.values():
                if ln.status != "performing" or ln.principal <= 0:
                    continue
                kind = ln.borrower_kind
                aid = ln.borrower_id if kind != "government" else 0
                if kind not in {"household", "firm", "government"}:
                    continue
                borrower_score = self.truth_market.agent_truth_score(self, kind, aid)
                bank_score = self.truth_market.agent_truth_score(self, "bank", b.bid)
                collateral_truth = clamp(2.0 * safe_div(ln.collateral_value, max(1.0, ln.principal), 0.0) - 1.0, -1.0, 1.0)
                self.truth_market.record_money_flow(
                    self,
                    kind,
                    aid,
                    ln.principal,
                    "initial_credit_stock_predicate",
                    [borrower_score, bank_score, collateral_truth, clamp(1.0 - 0.01 * ln.maturity, -1.0, 1.0)],
                    [ln.purpose, "initial_debt", "loan", "balance_sheet"],
                    verification_depth=1,
                )

    def _truth_specific_scenario_pre_step(self) -> None:
        """Additional scenarios for the predicate-truth currency layer.

        The base simulator already knows classic shocks.  These extra scenarios
        manipulate the second currency, resource quotas, verification intensity,
        and falsification risk without changing the base ScenarioEngine.
        """
        if self.truth_market is None:
            return
        names = set(getattr(self.scenarios, "names", [self.config.scenario]))
        t = self.t
        if "truth_currency_transition" in names:
            if t == 1:
                self.events.add(t, "Truth-currency transition: TCR accounting, verification, and correctness trading intensify.")
            self.config.truth_market_intensity = min(0.34, self.config.truth_market_intensity * 1.006)
            self.config.truth_verification_intensity = min(0.22, self.config.truth_verification_intensity * 1.004)
            self.config.truth_trade_fraction = min(0.22, self.config.truth_trade_fraction * 1.004)
            self.config.truth_meta_verification_rate = min(0.35, self.config.truth_meta_verification_rate + 0.0008)
            self.truth_market.price_ecu = clamp(self.truth_market.price_ecu * 1.001, 0.01, 100.0)
        if "planetary_overshoot" in names:
            if t == 1:
                self.events.add(t, "Planetary overshoot: resource bands tighten and cross-resource throttling becomes harsher.")
            self.config.truth_resource_strictness = min(2.60, self.config.truth_resource_strictness * 1.006)
            self.config.truth_quota_scale = max(0.58, self.config.truth_quota_scale * 0.997)
            # Reconfigure bands gradually so the resource market has a visible shock.
            if t % 4 == 0:
                self.truth_market._configure_bands(self.config)
            if 8 <= t <= 45:
                self.energy_market.fossil_price *= 1.004
        if "greenwashing_crackdown" in names:
            if t == 5:
                self.events.add(t, "Greenwashing crackdown: low-verification claims are falsified and costly to refinance.")
            if t >= 5:
                sample = [f for f in self.firms if f.alive()]
                if len(sample) > 36:
                    sample = self.rng.sample(sample, 36)
                for f in sample:
                    score = getattr(f, "last_truth_score", 0.0)
                    suspicious = score < -0.10 or getattr(f, "last_resource_overshoot", 0.0) > 0.20
                    if suspicious:
                        penalty = min(max(0.0, f.cash), 0.0035 * max(1.0, f.last_revenue + f.capital))
                        f.cash -= penalty
                        self.government.collect(penalty * 0.35)
                        self.truth_market.issue_truth(f, -truth_units_from_money(2.0 + 10.0 * abs(score), Fraction(1, 1), self.config.truth_verification_intensity))
                        setattr(f, "predicate_arity", getattr(f, "predicate_arity", 0) + 1)
                        setattr(f, "verification_depth", getattr(f, "verification_depth", 0) + 1)
                        self.truth_market.falsification_count += 1
        if "knowledge_commons" in names:
            if t == 1:
                self.events.add(t, "Knowledge commons: verified education and open correctness models diffuse faster.")
            self.config.truth_trade_fraction = min(0.24, self.config.truth_trade_fraction + 0.001)
            self.government.public_education_quality = clamp(self.government.public_education_quality + 0.0015, 0.55, 1.70)
            for f in self.firms:
                if f.alive() and f.sector in {"Education", "ProfessionalServices", "DigitalPlatform"}:
                    setattr(f, "correctness_model_quality", clamp(getattr(f, "correctness_model_quality", 0.5) + 0.001, 0.0, 1.0))

    def step(self) -> None:
        self._reset_step_counters()
        self.scenarios.apply_pre_step(self)
        self._truth_specific_scenario_pre_step()
        pressure = self.scenarios.pressure(self.t)
        if self.truth_market is not None:
            self.truth_market.begin_step(self)
            # Resource overshoot becomes a real scarcity signal for the ordinary economy.
            if self.truth_market.active_resource_throttle < 0.999:
                self.energy_market.shortage_ratio = max(self.energy_market.shortage_ratio, 1.0 - self.truth_market.active_resource_throttle)
                for f in self.firms:
                    if f.alive() and getattr(f, "last_resource_overshoot", 0.0) > 0:
                        f.supply_chain_fragility = clamp(f.supply_chain_fragility + 0.03 * getattr(f, "last_resource_overshoot", 0.0), 0.0, 0.95)
        self.energy_market.pre_step_update(self.rng, self.government, pressure)
        self.foreign_sector.update_pre(self.rng, self.central_bank.policy_rate, self.metrics_last.get("inflation", 0.0), pressure)
        self._update_policy_pre_market()
        self._labor_market()
        self._production()
        if self.truth_market is not None:
            self.truth_market.post_production_resource_accounting(self)
        self._household_income_taxes_and_rents()
        if self.truth_market is not None:
            # Major household income/rent/tax flows as predicate-money.
            for h in self.households:
                if h.last_income > 0:
                    self.truth_market.record_money_flow(
                        self,
                        "household",
                        h.hid,
                        h.last_income + h.last_taxes,
                        "income_tax_rent_predicate",
                        self.truth_market.household_correctness_bits(self, h),
                        [h.region, "income", "tax", "rent", "labor"],
                    )
        self._goods_and_services_market()
        if self.truth_market is not None:
            # Revenues and consumption as market-success predicates.
            for f in self.firms:
                if f.alive() and f.last_revenue > 0:
                    self.truth_market.record_money_flow(
                        self,
                        "firm",
                        f.fid,
                        f.last_revenue,
                        "sales_market_success_predicate",
                        self.truth_market.firm_correctness_bits(self, f),
                        [f.sector, "sales", "price", "quality", "resource"],
                    )
            for h in self.households:
                if h.last_consumption > 0:
                    self.truth_market.record_money_flow(
                        self,
                        "household",
                        h.hid,
                        h.last_consumption,
                        "consumption_correctness_predicate",
                        self.truth_market.household_correctness_bits(self, h),
                        [h.region, "consumption", "resource", "need", "planet"],
                    )
        self._corporate_taxes_and_debt_service()
        self._credit_investment_and_capital_formation()
        self._housing_and_mortgages()
        self._health_education_demography()
        self._insurance_market()
        self._platform_market()
        self._banking_system()
        self._financial_market()
        self._foreign_sector_finalize()
        self._government_finalize()
        self._bankruptcy_resolution()
        self.scenarios.apply_post_step(self)
        if self.truth_market is not None:
            self.truth_market.end_step(self)
        self._collect_metrics()

    def _collect_metrics(self) -> None:
        super()._collect_metrics()
        if self.truth_market is not None and self.metrics:
            self.truth_market.add_metrics(self.metrics[-1], self)
            self.metrics_last.update(self.metrics[-1])

    def final_summary(self) -> Dict[str, Any]:
        summary = super().final_summary()
        if self.truth_market is not None:
            summary.update(self.truth_market.summary(self))
        return summary


# ---------------------------------------------------------------------------
# Output helpers and CLI
# ---------------------------------------------------------------------------


def write_csv(path: str, rows: List[Dict[str, float]]) -> None:
    return base.write_csv(path, rows)


def write_json(path: str, obj: Dict[str, Any]) -> None:
    return base.write_json(path, obj)


def print_summary(summary: Dict[str, Any]) -> None:
    base.print_summary(summary)
    print("\n=== Predicate Truth Currency ===")
    keys = [
        "truth_currency",
        "final_truth_price_ecu",
        "final_truth_planetary_score",
        "final_truth_resource_throttle",
        "final_truth_max_resource_overshoot",
        "final_truth_supply",
        "final_truth_debt_total",
        "final_truth_net_supply",
        "final_truth_avg_firm_score",
        "final_truth_avg_household_score",
        "final_truth_avg_bank_score",
        "final_truth_avg_predicate_arity",
        "final_truth_avg_verification_depth",
        "truth_verification_count",
        "truth_falsification_count",
        "truth_meta_verification_count",
        "truth_total_trade_volume",
        "truth_total_trade_volume_ecu",
    ]
    for k in keys:
        if k in summary:
            print(f"{k:36s}: {summary[k]}")
    models = summary.get("truth_top_correctness_models", [])
    if models:
        print("\nTop correctness models:")
        for m in models[:5]:
            print(
                f"  model={m['model_id']:4d} sector={m['sector']:22s} "
                f"quality={m['quality']:.3f} depth={m['verification_depth']:3d} "
                f"arity={m['arity']:3d} share={m['market_share']:.3f} price={m['price_ecu']:.3f}"
            )


def run_single(config: TruthSimulationConfig, out_csv: str = "", out_json: str = "") -> Dict[str, Any]:
    world = TruthEconomicWorld(config)
    metrics = world.run()
    summary = world.final_summary()
    if out_csv:
        write_csv(out_csv, metrics)
    if out_json:
        write_json(out_json, summary)
    return {"summary": summary, "metrics": metrics}


def run_compare(base_config: TruthSimulationConfig, scenarios: List[str], out_csv: str = "", out_json: str = "") -> Dict[str, Any]:
    comparison_rows: List[Dict[str, Any]] = []
    summaries: Dict[str, Any] = {}
    for i, scenario in enumerate(scenarios):
        cfg = TruthSimulationConfig(**vars(base_config))
        cfg.scenario = scenario
        cfg.seed = base_config.seed + i * 1009
        world = TruthEconomicWorld(cfg)
        world.run()
        summary = world.final_summary()
        summaries[scenario] = summary
        row: Dict[str, Any] = {"scenario": scenario}
        for k, v in summary.items():
            if isinstance(v, (int, float, str)):
                row[k] = v
        comparison_rows.append(row)
    if out_csv:
        os.makedirs(os.path.dirname(os.path.abspath(out_csv)) or ".", exist_ok=True)
        fields: List[str] = []
        seen = set()
        for row in comparison_rows:
            for k in row.keys():
                if k not in seen:
                    fields.append(k)
                    seen.add(k)
        with open(out_csv, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for row in comparison_rows:
                writer.writerow(row)
    if out_json:
        write_json(out_json, summaries)
    return {"summaries": summaries, "rows": comparison_rows}


def make_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Mega economy simulator with tradeable rational fuzzy predicate truth currency.")
    p.add_argument("--steps", type=int, default=60)
    p.add_argument("--households", type=int, default=300)
    p.add_argument("--firms", type=int, default=80)
    p.add_argument("--banks", type=int, default=5)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--scenario", type=str, default="baseline")
    p.add_argument("--compound", type=str, default="", help="Comma-separated extra scenarios, e.g. energy_shock,financial_crisis")
    p.add_argument("--policy", type=str, default="balanced", choices=["balanced", "hawkish", "dovish", "austerity", "stimulus", "green"])
    p.add_argument("--out", type=str, default="", help="CSV path for full time series")
    p.add_argument("--json", type=str, default="", help="JSON path for final summary")
    p.add_argument("--compare", nargs="*", default=None, help="Run multiple scenarios and output comparison table")
    p.add_argument("--quiet", action="store_true")
    # Ordinary policy/calibration knobs.
    p.add_argument("--income-tax", type=float, default=0.20)
    p.add_argument("--corporate-tax", type=float, default=0.20)
    p.add_argument("--vat", type=float, default=0.12)
    p.add_argument("--carbon-price", type=float, default=0.03)
    p.add_argument("--bank-capital-requirement", type=float, default=0.085)
    p.add_argument("--labor-mobility", type=float, default=0.16)
    p.add_argument("--open-economy", action="store_true", default=True)
    p.add_argument("--closed-economy", action="store_true", help="Disable imports/exports feedbacks")
    # Truth-currency knobs.
    p.add_argument("--truth-currency-name", type=str, default="TCR")
    p.add_argument("--disable-truth-currency", action="store_true")
    p.add_argument("--truth-initial-price", type=float, default=1.0)
    p.add_argument("--truth-market-intensity", type=float, default=0.18)
    p.add_argument("--truth-verification-intensity", type=float, default=0.10)
    p.add_argument("--truth-resource-strictness", type=float, default=1.35)
    p.add_argument("--truth-trade-fraction", type=float, default=0.10)
    p.add_argument("--truth-meta-verification-rate", type=float, default=0.15)
    p.add_argument("--truth-min-credit-score", type=float, default=-0.35)
    p.add_argument("--truth-quota-scale", type=float, default=1.0)
    p.add_argument("--truth-audit-sample", type=int, default=32)
    p.add_argument("--truth-print-events", action="store_true")
    return p


def config_from_args(args: argparse.Namespace) -> TruthSimulationConfig:
    return TruthSimulationConfig(
        seed=args.seed,
        steps=args.steps,
        households=args.households,
        firms=args.firms,
        banks=args.banks,
        scenario=args.scenario,
        policy_mode=args.policy,
        income_tax=args.income_tax,
        corporate_tax=args.corporate_tax,
        vat=args.vat,
        carbon_price=args.carbon_price,
        bank_capital_requirement=args.bank_capital_requirement,
        labor_mobility=args.labor_mobility,
        open_economy=not args.closed_economy,
        shock_compound=args.compound,
        verbose=not args.quiet,
        truth_currency_name=args.truth_currency_name,
        truth_currency_enabled=not args.disable_truth_currency,
        truth_initial_price=args.truth_initial_price,
        truth_market_intensity=args.truth_market_intensity,
        truth_verification_intensity=args.truth_verification_intensity,
        truth_resource_strictness=args.truth_resource_strictness,
        truth_trade_fraction=args.truth_trade_fraction,
        truth_meta_verification_rate=args.truth_meta_verification_rate,
        truth_min_credit_score=args.truth_min_credit_score,
        truth_quota_scale=args.truth_quota_scale,
        truth_audit_sample=args.truth_audit_sample,
        truth_print_events=args.truth_print_events,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = make_arg_parser()
    args = parser.parse_args(argv)
    cfg = config_from_args(args)
    if args.compare is not None and len(args.compare) > 0:
        result = run_compare(cfg, args.compare, out_csv=args.out, out_json=args.json)
        print("\n=== Scenario comparison with Predicate Truth Currency ===")
        for row in result["rows"]:
            print(
                f"{row['scenario']:22s} "
                f"GDP={float(row.get('final_gdp', 0.0)):10.3f} "
                f"unemp={float(row.get('final_unemployment', 0.0)):7.3f} "
                f"truth={float(row.get('final_truth_planetary_score', 0.0)):7.3f} "
                f"TCR={float(row.get('final_truth_price_ecu', 0.0)):8.3f} "
                f"throttle={float(row.get('final_truth_resource_throttle', 0.0)):7.3f} "
                f"welfare={float(row.get('final_welfare_index', 0.0)):7.3f}"
            )
        if args.out:
            print(f"CSV written to: {args.out}")
        if args.json:
            print(f"JSON written to: {args.json}")
        return 0

    result = run_single(cfg, out_csv=args.out, out_json=args.json)
    if not args.quiet:
        print_summary(result["summary"])
    if args.out:
        print(f"\nCSV written to: {args.out}")
    if args.json:
        print(f"JSON written to: {args.json}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
