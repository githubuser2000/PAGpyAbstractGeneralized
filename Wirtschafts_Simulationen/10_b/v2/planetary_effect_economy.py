#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Planetary Effect Economy Simulation
===================================

PyPy3-compatible simulation of a planetary economy built from the concepts in
this chat: no money, no commodity price, no national GDP core. The system
coordinates real states and effects: causality, time, intensity, existence,
potencies, effects, substance, matter, difference, determination, phenomena, and
angle-direction.

Deutsch: Dies ist eine Planetenwirtschafts-Simulation, keine Volkswirtschaft.
Die primäre Frage ist nicht: "Was ist profitabel?" sondern:
"Welche reale Differenz zwischen Bedarf, Substanz, Potenzen und Wirkung muss
innerhalb planetarer Grenzen aufgelöst werden?"

Run:
    pypy3 planetary_effect_economy.py --steps 120 --scenario planetary_commons --out out
or, if PyPy3 is not installed:
    python3 planetary_effect_economy.py --steps 120 --out out

Outputs:
    summary.json        final system metrics
    timeline.csv          global time series
    macro_accounts.csv    planetary accounts by domain/sector/need/gap
    effect_flow_audit.csv last-step buy/sell replacement: causal effect flows
    communes_final.csv    final commune-level states
    truth_audit.csv       top truth-vector priorities from the last step
    manifest.md           human-readable interpretation of the simulation

The model is intentionally synthetic. It is for concept development,
experimentation, and policy/game/simulation design, not a calibrated forecast.

Version note: this extended build adds macroeconomic replacements for sector
accounts, labour contribution, capital/investment, public coordination,
knowledge, resilience, material circulation and external trade. All remain
non-monetary: no price, wage, profit, rent, GDP, import value or export value.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import sys
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Core vocabulary: stacked logical truth values
# ---------------------------------------------------------------------------

TRUTH_DIMS = (
    "causality",          # confidence that a chosen intervention actually acts on the cause
    "time",               # urgency in time
    "intensity",          # strength/severity of the phenomenon
    "existence",          # how real/present the phenomenon is
    "potencies",          # how much solvable possibility exists
    "effects",            # expected positive systemic effect if solved
    "substance",          # input/substance availability
    "matter",             # material/infrastructure proximity
    "difference",         # gap between need and state
    "determination",      # democratically confirmed priority / social determination
    "phenomena",          # visible or reported appearance of the issue
    "angle_direction",    # alignment of the action with planetary regeneration and human freedom
)

TRUTH_WEIGHTS = {
    "causality": 0.08,
    "time": 0.12,
    "intensity": 0.12,
    "existence": 0.08,
    "potencies": 0.08,
    "effects": 0.12,
    "substance": 0.07,
    "matter": 0.07,
    "difference": 0.14,
    "determination": 0.08,
    "phenomena": 0.07,
    "angle_direction": 0.09,
}

# Domains are not "markets". They are real need/effect fields.
DOMAINS = (
    "water",
    "food",
    "energy",
    "shelter",
    "health",
    "care",
    "education",
    "mobility",
    "manufacturing",
    "storage",
    "governance",
    "knowledge",
    "resilience",
    "repair",
    "ecology",
    "waste",
)

# Sectors replace national-account categories such as agriculture, industry,
# services, state, capital formation and foreign trade. They are not markets;
# they are fields of planetary reproduction.
SECTOR_FOR_DOMAIN = {
    "water": "primary_reproduction",
    "food": "primary_reproduction",
    "energy": "infrastructure_energy",
    "shelter": "social_infrastructure",
    "health": "care_reproduction",
    "care": "care_reproduction",
    "education": "knowledge_reproduction",
    "mobility": "logistics_circulation",
    "manufacturing": "material_transformation",
    "storage": "resilience_capital",
    "governance": "institutional_coordination",
    "knowledge": "knowledge_reproduction",
    "resilience": "risk_protection",
    "repair": "circular_industry",
    "ecology": "planetary_regeneration",
    "waste": "material_difference_resolution",
}

CONSUMABLE_DOMAINS = ("water", "food", "energy")
SERVICE_DOMAINS = ("health", "care", "education", "mobility", "governance", "knowledge", "resilience")
CAPACITY_DOMAINS = ("shelter", "manufacturing", "storage")
MACRO_CAPACITY_DOMAINS = CAPACITY_DOMAINS + SERVICE_DOMAINS

# One simulation step = one month. Units are normalized person-months or
# capability-months. These are not prices and not exchange values.
NEED_PER_PERSON = {
    "water": 1.0,
    "food": 1.0,
    "energy": 1.0,
    "shelter": 1.0,   # capacity for one person
    "health": 0.22,   # average monthly health service need
    "care": 0.18,     # care load, higher for children/elders/unwell cohorts
    "education": 0.20,
    "mobility": 0.23,
    "manufacturing": 0.12,  # tools, basic industry, replacement parts
    "storage": 0.08,        # buffers, warehouses, grid/storage systems
    "governance": 0.06,     # democratic coordination and dispute resolution
    "knowledge": 0.07,      # research, open plans, technical learning
    "resilience": 0.09,     # emergency readiness and redundancy
}

# Planetary pressure names. Pressure > 1 means overshoot beyond safe operating space.
BOUNDARY_NAMES = (
    "climate",
    "biosphere",
    "freshwater",
    "soil",
    "pollution",
    "material_throughput",
    "energy_throughput",
)

BOUNDARY_WEIGHTS = {
    "climate": 1.3,
    "biosphere": 1.25,
    "freshwater": 1.1,
    "soil": 1.0,
    "pollution": 1.05,
    "material_throughput": 0.85,
    "energy_throughput": 0.85,
}


# ---------------------------------------------------------------------------
# Utility functions
# ---------------------------------------------------------------------------


def clamp(x: float, lo: float = 0.0, hi: float = 1.0) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if abs(b) < 1e-12:
        return default
    return a / b


def scale4(x: float) -> float:
    """Convert a 0..1 normalized number to the 0..4 truth scale."""
    return 4.0 * clamp(x)


def mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = list(values)
    if not vals:
        return default
    return sum(vals) / float(len(vals))


def weighted_mean(items: Iterable[Tuple[float, float]], default: float = 0.0) -> float:
    total_w = 0.0
    total = 0.0
    for value, weight in items:
        total += value * weight
        total_w += weight
    if total_w <= 1e-12:
        return default
    return total / total_w


def weighted_gini(items: Iterable[Tuple[float, float]]) -> float:
    """Weighted Gini for inequality of satisfaction/wellbeing.

    0 means equal distribution. 1 would mean maximum inequality.
    This is distributional diagnostics, not moral value in money terms.
    """
    data = [(max(0.0, v), max(0.0, w)) for v, w in items if w > 0.0]
    if not data:
        return 0.0
    data.sort(key=lambda x: x[0])
    total_w = sum(w for _, w in data)
    total_xw = sum(v * w for v, w in data)
    if total_w <= 1e-12 or total_xw <= 1e-12:
        return 0.0
    cum_w = 0.0
    cum_xw = 0.0
    area = 0.0
    prev_w_share = 0.0
    prev_x_share = 0.0
    for value, weight in data:
        cum_w += weight
        cum_xw += value * weight
        w_share = cum_w / total_w
        x_share = cum_xw / total_xw
        area += (x_share + prev_x_share) * (w_share - prev_w_share) / 2.0
        prev_w_share = w_share
        prev_x_share = x_share
    return clamp(1.0 - 2.0 * area)


def normalized_need_gap(need: float, available: float) -> float:
    """0 means covered, 1 means almost completely missing."""
    if need <= 1e-12:
        return 0.0
    return clamp((need - available) / need)


def sat_ratio(available: float, need: float) -> float:
    if need <= 1e-12:
        return 1.0
    return clamp(available / need)


def lognormal_near(rng: random.Random, center: float, spread: float) -> float:
    """Small helper to avoid relying on statistics/numpy."""
    return center * math.exp(rng.gauss(0.0, spread))


def format_big(x: float) -> str:
    abs_x = abs(x)
    if abs_x >= 1_000_000_000:
        return "%.3fb" % (x / 1_000_000_000.0)
    if abs_x >= 1_000_000:
        return "%.3fm" % (x / 1_000_000.0)
    if abs_x >= 1_000:
        return "%.3fk" % (x / 1_000.0)
    return "%.3f" % x


# ---------------------------------------------------------------------------
# Data structures
# ---------------------------------------------------------------------------


@dataclass
class TruthVector:
    """Stacked logical truth values on a 0..4 scale."""

    domain: str
    values: Dict[str, float]
    commune: str = ""
    region: str = ""
    explanation: str = ""

    def priority(self) -> float:
        """Priority is not price. It is weighted urgency/effect/difference."""
        total = 0.0
        weight_sum = 0.0
        for dim in TRUTH_DIMS:
            weight = TRUTH_WEIGHTS.get(dim, 0.0)
            total += clamp(self.values.get(dim, 0.0), 0.0, 4.0) * weight
            weight_sum += weight
        if weight_sum <= 0.0:
            return 0.0
        return total / (4.0 * weight_sum)

    def as_row(self, step: int) -> Dict[str, object]:
        row = {
            "step": step,
            "region": self.region,
            "commune": self.commune,
            "domain": self.domain,
            "priority": round(self.priority(), 6),
            "explanation": self.explanation,
        }
        for dim in TRUTH_DIMS:
            row[dim] = round(self.values.get(dim, 0.0), 6)
        return row


@dataclass
class EffectFlow:
    """A non-market action record.

    It replaces buy/sell/import/export with causal effect activation:
    - need_acceptance: what older language would call buying/consuming
    - contribution_offer: what older language would call selling/labour supply
    - planetary_transfer: what older language would call trade/import/export

    The numeric field is called activated_effect, not price, worth or value.
    """

    step: int
    kind: str
    legacy_term_replaced: str
    action: str
    domain: str
    sector: str
    from_region: str
    from_commune: str
    to_region: str
    to_commune: str
    activated_effect: float
    causal_link: str
    direction_vector: str
    values: Dict[str, float]
    note: str = ""

    def as_row(self) -> Dict[str, object]:
        row = {
            "step": self.step,
            "kind": self.kind,
            "legacy_term_replaced": self.legacy_term_replaced,
            "action": self.action,
            "domain": self.domain,
            "sector": self.sector,
            "from_region": self.from_region,
            "from_commune": self.from_commune,
            "to_region": self.to_region,
            "to_commune": self.to_commune,
            "activated_effect": round(self.activated_effect, 6),
            "causal_link": self.causal_link,
            "direction_vector": self.direction_vector,
            "note": self.note,
        }
        for dim in TRUTH_DIMS:
            row[dim] = round(self.values.get(dim, 0.0), 6)
        return row


@dataclass
class MacroAccountRow:
    """Planetary macro-account row without monetary value categories."""

    step: int
    domain: str
    sector: str
    need: float
    available: float
    gap: float
    satisfaction: float
    priority: float
    labor_share: float
    contribution_time: float
    stock_or_capacity: float
    boundary_penalty: float
    truth_error: float
    democratic_quality: float
    activated_flows: int

    def as_row(self) -> Dict[str, object]:
        return {
            "step": self.step,
            "domain": self.domain,
            "sector": self.sector,
            "need": round(self.need, 6),
            "available": round(self.available, 6),
            "gap": round(self.gap, 6),
            "satisfaction": round(self.satisfaction, 6),
            "priority": round(self.priority, 6),
            "labor_share": round(self.labor_share, 6),
            "contribution_time": round(self.contribution_time, 6),
            "stock_or_capacity": round(self.stock_or_capacity, 6),
            "boundary_penalty": round(self.boundary_penalty, 6),
            "truth_error": round(self.truth_error, 6),
            "democratic_quality": round(self.democratic_quality, 6),
            "activated_flows": self.activated_flows,
        }


@dataclass
class BoundaryState:
    """Planetary operating space. Values are pressures; >1.0 means overshoot."""

    pressures: Dict[str, float]

    def overshoot(self) -> float:
        return sum(max(0.0, self.pressures.get(name, 0.0) - 1.0) for name in BOUNDARY_NAMES)

    def mean_pressure(self) -> float:
        return mean(self.pressures.get(name, 0.0) for name in BOUNDARY_NAMES)

    def worst(self) -> Tuple[str, float]:
        if not self.pressures:
            return "none", 0.0
        return max(self.pressures.items(), key=lambda kv: kv[1])

    def penalty(self) -> float:
        """Overshoot reduces system effectiveness but never makes action impossible."""
        overs = self.overshoot()
        # Smooth penalty. At zero overshoot = 1.0, at severe overshoot maybe ~0.55.
        return clamp(1.0 / (1.0 + 0.33 * overs), 0.45, 1.0)

    def apply_impacts(self, impacts: Dict[str, float], regeneration: Dict[str, float]) -> None:
        # Scale constants keep values stable for synthetic runs.
        for name in BOUNDARY_NAMES:
            before = self.pressures.get(name, 0.7)
            pressure = before
            pressure += impacts.get(name, 0.0)
            pressure -= regeneration.get(name, 0.0)
            # Natural repair is slow if under low pressure; degradation is sticky above 1.
            if pressure < 0.75:
                pressure += 0.005 * (0.75 - pressure)
            if pressure > 1.0:
                pressure += 0.002 * (pressure - 1.0)
            self.pressures[name] = clamp(pressure, 0.2, 2.2)


@dataclass
class PopulationCohort:
    name: str
    size: float
    health: float
    education: float
    autonomy: float
    trust: float
    skill: Dict[str, float]
    age_factor: float = 1.0

    def productive_time(self) -> float:
        # Labour is not bought/sold. This is available contribution time.
        return self.size * self.age_factor * clamp(0.35 + 0.65 * self.health) * clamp(0.45 + 0.55 * self.autonomy)

    def update_from_satisfaction(self, satisfaction: Dict[str, float], governance_quality: float, privacy_pressure: float) -> None:
        basic = 0.40 * satisfaction.get("water", 1.0) + 0.35 * satisfaction.get("food", 1.0) + 0.25 * satisfaction.get("shelter", 1.0)
        service = 0.45 * satisfaction.get("health", 1.0) + 0.25 * satisfaction.get("care", 1.0) + 0.20 * satisfaction.get("education", 1.0) + 0.10 * satisfaction.get("mobility", 1.0)
        civic = 0.34 * satisfaction.get("governance", 1.0) + 0.33 * satisfaction.get("knowledge", 1.0) + 0.33 * satisfaction.get("resilience", 1.0)
        energy = satisfaction.get("energy", 1.0)
        # Health moves slowly; severe basic deficits hit it fast.
        health_delta = 0.018 * (basic - 0.78) + 0.010 * (service - 0.75) + 0.006 * (energy - 0.70)
        self.health = clamp(self.health + health_delta, 0.05, 1.0)
        # Education responds to education satisfaction, not instantly.
        self.education = clamp(self.education + 0.006 * (satisfaction.get("education", 1.0) - 0.55) + 0.003 * (satisfaction.get("knowledge", 1.0) - 0.55), 0.05, 1.0)
        # Autonomy drops under unmet basics and high privacy/control pressure; it rises with civic capability.
        self.autonomy = clamp(self.autonomy + 0.010 * (mean(satisfaction.values(), 0.9) - 0.72) + 0.006 * (civic - 0.65) - 0.018 * privacy_pressure, 0.05, 1.0)
        # Trust is a local truth-feedback quality. It falls when the system claims truth but fails people.
        self.trust = clamp(self.trust + 0.018 * (mean(satisfaction.values(), 0.9) - 0.70) + 0.016 * (governance_quality - 0.5) + 0.008 * (civic - 0.65) - 0.012 * privacy_pressure, 0.02, 1.0)
        # Skills improve with education and degrade slowly if health is bad.
        for k in list(self.skill.keys()):
            self.skill[k] = clamp(self.skill[k] + 0.003 * (self.education - 0.5) + 0.002 * (self.health - 0.5), 0.05, 1.0)


@dataclass
class Commune:
    name: str
    region_name: str
    biome: str
    cohorts: List[PopulationCohort]
    stocks: Dict[str, float]
    capacities: Dict[str, float]
    environment: Dict[str, float]
    group_base: Dict[str, float]
    democratic_quality: float
    truth_error: float = 0.15
    last_satisfaction: Dict[str, float] = field(default_factory=dict)
    last_priorities: Dict[str, float] = field(default_factory=dict)
    last_labor_shares: Dict[str, float] = field(default_factory=dict)
    last_truth_values: Dict[str, Dict[str, float]] = field(default_factory=dict)

    def population(self) -> float:
        return sum(c.size for c in self.cohorts)

    def productive_time(self) -> float:
        return sum(c.productive_time() for c in self.cohorts)

    def average_health(self) -> float:
        return weighted_mean(((c.health, c.size) for c in self.cohorts), default=0.7)

    def average_education(self) -> float:
        return weighted_mean(((c.education, c.size) for c in self.cohorts), default=0.6)

    def average_autonomy(self) -> float:
        return weighted_mean(((c.autonomy, c.size) for c in self.cohorts), default=0.7)

    def average_trust(self) -> float:
        return weighted_mean(((c.trust, c.size) for c in self.cohorts), default=0.6)

    def skill(self, field_name: str) -> float:
        return weighted_mean(((c.skill.get(field_name, 0.4), c.size) for c in self.cohorts), default=0.4)

    def need(self, domain: str) -> float:
        pop = self.population()
        if domain == "health":
            # More need if health is low.
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.75 * (1.0 - self.average_health()))
        if domain == "care":
            child_elder_share = 0.0
            for c in self.cohorts:
                if c.name in ("children", "elders"):
                    child_elder_share += c.size
            dependency = safe_div(child_elder_share, pop, 0.33)
            return pop * NEED_PER_PERSON[domain] * (0.65 + 1.35 * dependency)
        if domain == "education":
            # Higher education demand if education is low; still lifelong education if high.
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.75 * (1.0 - self.average_education()))
        if domain == "mobility":
            return pop * NEED_PER_PERSON[domain] * (0.8 + 0.3 * self.environment.get("remoteness", 0.5))
        if domain == "governance":
            # Coordination need rises with complexity, low trust and truth error.
            complexity = 0.45 + 0.35 * self.environment.get("remoteness", 0.5) + 0.20 * self.truth_error
            legitimacy_gap = 1.0 - 0.5 * self.democratic_quality - 0.5 * self.average_trust()
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.55 * complexity + 0.60 * max(0.0, legitimacy_gap))
        if domain == "knowledge":
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.65 * (1.0 - self.average_education()) + 0.25 * (1.0 - self.environment.get("renewable_infrastructure", 0.5)))
        if domain == "manufacturing":
            repair_gap = normalized_need_gap(max(1.0, pop * 0.18), self.stocks.get("repair_materials", 0.0))
            capacity_gap = normalized_need_gap(max(1.0, pop * NEED_PER_PERSON[domain]), self.capacities.get("manufacturing", 0.0))
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.65 * repair_gap + 0.40 * capacity_gap)
        if domain == "storage":
            basic_need = self.need("water") + self.need("food") + self.need("energy")
            basic_stock = self.stocks.get("water", 0.0) + self.stocks.get("food", 0.0) + self.stocks.get("energy", 0.0)
            buffer_gap = normalized_need_gap(1.20 * basic_need, basic_stock)
            return pop * NEED_PER_PERSON[domain] * (0.70 + 1.10 * buffer_gap)
        if domain == "resilience":
            climate_exposure = self.environment.get("local_pollution", 0.2) + (1.0 - self.environment.get("watershed", 0.7))
            buffer_gap = normalized_need_gap(max(1.0, pop * 0.60), self.stocks.get("water", 0.0) + self.stocks.get("food", 0.0))
            return pop * NEED_PER_PERSON[domain] * (0.75 + 0.45 * climate_exposure + 0.55 * buffer_gap)
        if domain in NEED_PER_PERSON:
            return pop * NEED_PER_PERSON[domain]
        return 0.0

    def available_for_need(self, domain: str) -> float:
        if domain in CONSUMABLE_DOMAINS:
            return self.stocks.get(domain, 0.0)
        if domain in SERVICE_DOMAINS:
            return self.capacities.get(domain, 0.0)
        if domain in CAPACITY_DOMAINS:
            return self.capacities.get(domain, 0.0)
        if domain == "repair":
            return self.stocks.get("repair_materials", 0.0)
        if domain == "ecology":
            # Deficit relative to healthy ecosystems.
            pop = self.population()
            soil_gap = max(0.0, 1.0 - self.environment.get("soil_health", 0.7))
            bio_gap = max(0.0, 1.0 - self.environment.get("biodiversity", 0.7))
            water_gap = max(0.0, 1.0 - self.environment.get("watershed", 0.7))
            return pop * (1.0 - mean([soil_gap, bio_gap, water_gap]))
        if domain == "waste":
            return self.stocks.get("waste", 0.0)
        return 0.0

    def ecology_need(self) -> float:
        pop = self.population()
        soil_gap = max(0.0, 1.0 - self.environment.get("soil_health", 0.7))
        bio_gap = max(0.0, 1.0 - self.environment.get("biodiversity", 0.7))
        water_gap = max(0.0, 1.0 - self.environment.get("watershed", 0.7))
        pollution = self.environment.get("local_pollution", 0.25)
        return pop * (0.18 + 0.50 * mean([soil_gap, bio_gap, water_gap, pollution]))

    def waste_need(self) -> float:
        # Waste is an unresolved material difference. High stock => high need.
        return max(1.0, self.population() * 0.10)

    def truth_vector(self, domain: str, global_boundary: BoundaryState, planner: "EffectPlanner") -> TruthVector:
        pop = self.population()
        env_penalty = 1.0 - global_boundary.penalty()
        if domain == "ecology":
            need = self.ecology_need()
            # Ecology availability is environmental integrity.
            available = max(0.0, pop * mean([
                self.environment.get("soil_health", 0.7),
                self.environment.get("biodiversity", 0.7),
                self.environment.get("watershed", 0.7),
                1.0 - self.environment.get("local_pollution", 0.2),
            ]))
            gap = clamp(need / max(pop * 0.70, 1.0))
        elif domain == "waste":
            need = self.waste_need()
            available = max(0.0, need - self.stocks.get("waste", 0.0))
            gap = clamp(self.stocks.get("waste", 0.0) / max(need, 1.0))
        else:
            need = self.need(domain)
            available = self.available_for_need(domain)
            gap = normalized_need_gap(need, available)

        domain_skill = self.skill(planner.skill_for_domain(domain))
        group_strength = self.group_base.get(planner.group_for_domain(domain), 0.4)
        local_potencies = clamp(0.45 * domain_skill + 0.35 * group_strength + 0.20 * self.democratic_quality)
        substance = clamp(0.35 * sat_ratio(self.stocks.get("repair_materials", 0.0), max(1.0, pop * 0.05)) +
                          0.25 * sat_ratio(self.stocks.get("energy", 0.0), max(1.0, self.need("energy") * 0.35)) +
                          0.20 * self.environment.get("watershed", 0.7) +
                          0.20 * self.environment.get("soil_health", 0.7))
        matter = clamp(0.55 * (1.0 - self.environment.get("remoteness", 0.5)) + 0.45 * sat_ratio(self.capacities.get("mobility", 0.0), max(1.0, self.need("mobility"))))
        criticality = planner.domain_criticality.get(domain, 0.5)
        time_urgency = clamp(0.45 * gap + 0.40 * criticality + 0.15 * env_penalty)
        intensity = clamp(0.70 * gap + 0.20 * criticality + 0.10 * (1.0 - self.average_health()))
        # Democracy should influence determination, but not allow a majority to erase critical needs.
        collective_claim = clamp(0.55 * gap + 0.25 * self.democratic_quality + 0.20 * self.average_trust())
        # Phenomena combines measured and reported reality; truth_error is noise/uncertainty.
        phenomena = clamp(gap * (1.0 - 0.50 * self.truth_error) + self.average_trust() * 0.15 + self.democratic_quality * 0.10)
        angle = planner.angle_alignment(domain, global_boundary, self)
        values = {
            "causality": scale4(planner.causal_confidence.get(domain, 0.65)),
            "time": scale4(time_urgency),
            "intensity": scale4(intensity),
            "existence": scale4(clamp(0.7 * gap + 0.3 * criticality)),
            "potencies": scale4(local_potencies),
            "effects": scale4(planner.effect_weight.get(domain, 0.6)),
            "substance": scale4(substance),
            "matter": scale4(matter),
            "difference": scale4(gap),
            "determination": scale4(collective_claim),
            "phenomena": scale4(phenomena),
            "angle_direction": scale4(angle),
        }
        return TruthVector(
            domain=domain,
            values=values,
            commune=self.name,
            region=self.region_name,
            explanation="need_gap=%.3f potencies=%.3f trust=%.3f boundary_penalty=%.3f" % (
                gap, local_potencies, self.average_trust(), global_boundary.penalty()
            ),
        )

    def update_truth_error(self, avg_satisfaction: float, planner: "EffectPlanner") -> None:
        # More democratic feedback and trust reduces truth error. High centralization raises it.
        correction = 0.018 * self.democratic_quality * self.average_trust() * planner.democratic_feedback
        failure = 0.014 * max(0.0, 0.68 - avg_satisfaction)
        central_error = 0.010 * planner.centralization * (1.0 - self.democratic_quality)
        self.truth_error = clamp(self.truth_error - correction + failure + central_error, 0.02, 0.75)


@dataclass
class Region:
    name: str
    biome: str
    communes: List[Commune]
    logistic_hub: float
    climate_risk: float

    def population(self) -> float:
        return sum(c.population() for c in self.communes)


@dataclass
class GlobalMetrics:
    step: int
    population: float
    wellbeing: float
    unmet_basic: float
    avg_trust: float
    avg_autonomy: float
    avg_health: float
    avg_education: float
    avg_truth_error: float
    overshoot: float
    mean_boundary_pressure: float
    worst_boundary: str
    worst_boundary_pressure: float
    waste_stock: float
    repair_materials: float
    food_stock: float
    water_stock: float
    energy_stock: float
    global_transfers: float
    contribution_time: float
    contribution_time_per_person: float
    satisfaction_inequality: float
    resilience_index: float
    circularity_index: float
    coordination_quality: float
    basic_buffer_months: float
    macro_capacity: float
    planetary_reproduction_index: float

    def as_row(self) -> Dict[str, object]:
        return {
            "step": self.step,
            "population": round(self.population, 3),
            "wellbeing": round(self.wellbeing, 6),
            "unmet_basic": round(self.unmet_basic, 6),
            "avg_trust": round(self.avg_trust, 6),
            "avg_autonomy": round(self.avg_autonomy, 6),
            "avg_health": round(self.avg_health, 6),
            "avg_education": round(self.avg_education, 6),
            "avg_truth_error": round(self.avg_truth_error, 6),
            "overshoot": round(self.overshoot, 6),
            "mean_boundary_pressure": round(self.mean_boundary_pressure, 6),
            "worst_boundary": self.worst_boundary,
            "worst_boundary_pressure": round(self.worst_boundary_pressure, 6),
            "waste_stock": round(self.waste_stock, 3),
            "repair_materials": round(self.repair_materials, 3),
            "food_stock": round(self.food_stock, 3),
            "water_stock": round(self.water_stock, 3),
            "energy_stock": round(self.energy_stock, 3),
            "global_transfers": round(self.global_transfers, 3),
            "contribution_time": round(self.contribution_time, 3),
            "contribution_time_per_person": round(self.contribution_time_per_person, 6),
            "satisfaction_inequality": round(self.satisfaction_inequality, 6),
            "resilience_index": round(self.resilience_index, 6),
            "circularity_index": round(self.circularity_index, 6),
            "coordination_quality": round(self.coordination_quality, 6),
            "basic_buffer_months": round(self.basic_buffer_months, 6),
            "macro_capacity": round(self.macro_capacity, 3),
            "planetary_reproduction_index": round(self.planetary_reproduction_index, 6),
        }


# ---------------------------------------------------------------------------
# Planner / policy logic
# ---------------------------------------------------------------------------


@dataclass
class EffectPlanner:
    """Coordinates effects, not prices."""

    democratic_feedback: float = 0.75
    centralization: float = 0.30
    privacy_pressure: float = 0.10
    cooperation: float = 0.82
    sufficiency_norm: float = 0.80
    climate_discipline: float = 0.78
    redistribution_strength: float = 0.85
    innovation_rate: float = 0.40
    logistics_efficiency: float = 0.76
    renewable_bias: float = 0.72

    domain_criticality: Dict[str, float] = field(default_factory=lambda: {
        "water": 1.00,
        "food": 0.95,
        "energy": 0.78,
        "shelter": 0.86,
        "health": 0.90,
        "care": 0.76,
        "education": 0.62,
        "mobility": 0.50,
        "manufacturing": 0.66,
        "storage": 0.64,
        "governance": 0.74,
        "knowledge": 0.68,
        "resilience": 0.82,
        "repair": 0.58,
        "ecology": 0.92,
        "waste": 0.70,
    })

    causal_confidence: Dict[str, float] = field(default_factory=lambda: {
        "water": 0.88,
        "food": 0.82,
        "energy": 0.78,
        "shelter": 0.73,
        "health": 0.76,
        "care": 0.81,
        "education": 0.70,
        "mobility": 0.66,
        "manufacturing": 0.72,
        "storage": 0.77,
        "governance": 0.67,
        "knowledge": 0.69,
        "resilience": 0.63,
        "repair": 0.82,
        "ecology": 0.69,
        "waste": 0.84,
    })

    effect_weight: Dict[str, float] = field(default_factory=lambda: {
        "water": 0.97,
        "food": 0.94,
        "energy": 0.80,
        "shelter": 0.88,
        "health": 0.91,
        "care": 0.80,
        "education": 0.75,
        "mobility": 0.57,
        "manufacturing": 0.74,
        "storage": 0.77,
        "governance": 0.86,
        "knowledge": 0.82,
        "resilience": 0.88,
        "repair": 0.72,
        "ecology": 0.96,
        "waste": 0.76,
    })

    def group_for_domain(self, domain: str) -> str:
        mapping = {
            "water": "water",
            "food": "agriculture",
            "energy": "energy",
            "shelter": "housing",
            "health": "health",
            "care": "care",
            "education": "education",
            "mobility": "logistics",
            "manufacturing": "manufacturing",
            "storage": "storage",
            "governance": "governance",
            "knowledge": "knowledge",
            "resilience": "resilience",
            "repair": "repair",
            "ecology": "ecology",
            "waste": "repair",
        }
        return mapping.get(domain, domain)

    def skill_for_domain(self, domain: str) -> str:
        mapping = {
            "water": "infrastructure",
            "food": "agriculture",
            "energy": "energy",
            "shelter": "construction",
            "health": "health",
            "care": "care",
            "education": "education",
            "mobility": "logistics",
            "manufacturing": "manufacturing",
            "storage": "storage",
            "governance": "governance",
            "knowledge": "knowledge",
            "resilience": "resilience",
            "repair": "repair",
            "ecology": "ecology",
            "waste": "repair",
        }
        return mapping.get(domain, "general")

    def angle_alignment(self, domain: str, boundary: BoundaryState, commune: Commune) -> float:
        # Positive direction means the action solves need while respecting planetary boundaries.
        overs = boundary.overshoot()
        climate = boundary.pressures.get("climate", 0.9)
        pollution = boundary.pressures.get("pollution", 0.8)
        material = boundary.pressures.get("material_throughput", 0.8)
        if domain in ("ecology", "repair", "waste"):
            return clamp(0.82 + 0.16 * min(1.0, overs))
        if domain in ("water", "food", "health", "care"):
            return clamp(0.78 - 0.08 * max(0.0, material - 1.0) + 0.06 * commune.democratic_quality)
        if domain == "energy":
            return clamp(0.55 + 0.35 * self.renewable_bias - 0.20 * max(0.0, climate - 1.0))
        if domain == "mobility":
            return clamp(0.58 + 0.18 * self.logistics_efficiency - 0.16 * max(0.0, climate - 1.0) - 0.08 * max(0.0, pollution - 1.0))
        if domain == "shelter":
            # Repair/reuse shelter is better than new material throughput.
            reuse = sat_ratio(commune.stocks.get("repair_materials", 0.0), max(1.0, commune.population() * 0.10))
            return clamp(0.58 + 0.20 * reuse - 0.12 * max(0.0, material - 1.0))
        if domain == "manufacturing":
            circular = sat_ratio(commune.stocks.get("repair_materials", 0.0), max(1.0, commune.population() * 0.18))
            return clamp(0.50 + 0.25 * circular + 0.18 * self.sufficiency_norm - 0.18 * max(0.0, material - 1.0))
        if domain == "storage":
            return clamp(0.68 + 0.20 * self.sufficiency_norm - 0.06 * max(0.0, material - 1.0))
        if domain in ("governance", "knowledge", "resilience"):
            democratic_direction = 0.50 + 0.35 * commune.democratic_quality + 0.20 * self.democratic_feedback - 0.22 * self.privacy_pressure
            if domain == "resilience":
                democratic_direction += 0.10 * min(1.0, overs)
            return clamp(democratic_direction)
        return clamp(0.65 - 0.08 * max(0.0, overs))

    def labor_shares(self, truth_vectors: List[TruthVector], commune: Commune, boundary: BoundaryState) -> Dict[str, float]:
        # Base shares prevent neglect of long-term fields. Priorities redirect contribution time.
        base = {
            "water": 0.070,
            "food": 0.120,
            "energy": 0.085,
            "shelter": 0.070,
            "health": 0.085,
            "care": 0.075,
            "education": 0.065,
            "mobility": 0.050,
            "manufacturing": 0.060,
            "storage": 0.040,
            "governance": 0.045,
            "knowledge": 0.045,
            "resilience": 0.050,
            "repair": 0.070,
            "ecology": 0.095,
            "waste": 0.070,
        }
        priority = {tv.domain: tv.priority() for tv in truth_vectors}
        # Planetary overshoot boosts ecology/repair/waste and moderates material-heavy sectors.
        overs = boundary.overshoot()
        for domain in ("ecology", "repair", "waste", "resilience", "storage"):
            priority[domain] = priority.get(domain, 0.0) + 0.16 * min(1.0, overs)
        if boundary.pressures.get("material_throughput", 0.0) > 1.0:
            priority["repair"] = priority.get("repair", 0.0) + 0.08
            priority["manufacturing"] = max(0.0, priority.get("manufacturing", 0.0) - 0.05)
        if boundary.pressures.get("climate", 0.0) > 1.0:
            priority["energy"] = priority.get("energy", 0.0) + 0.10 * self.renewable_bias
            priority["resilience"] = priority.get("resilience", 0.0) + 0.06
            priority["mobility"] = priority.get("mobility", 0.0) - 0.04 * boundary.pressures.get("climate", 1.0)
        # Centralization dampens local truth. Democratic feedback amplifies it.
        local_weight = clamp(0.45 + 0.45 * commune.democratic_quality * self.democratic_feedback - 0.25 * self.centralization)
        raw = {}
        for d in DOMAINS:
            raw[d] = max(0.005, base[d] * (1.0 - local_weight) + priority.get(d, 0.0) * local_weight)
        total = sum(raw.values())
        return {d: raw[d] / total for d in DOMAINS}


# ---------------------------------------------------------------------------
# Synthetic planet generator
# ---------------------------------------------------------------------------


BIOME_LIBRARY = {
    "equatorial_forest": {
        "soil_health": 0.78, "biodiversity": 0.92, "watershed": 0.88, "solar": 0.75,
        "wind": 0.42, "agri": 0.58, "remoteness": 0.45, "pollution": 0.22,
    },
    "temperate_mixed": {
        "soil_health": 0.72, "biodiversity": 0.63, "watershed": 0.70, "solar": 0.55,
        "wind": 0.62, "agri": 0.78, "remoteness": 0.28, "pollution": 0.34,
    },
    "drylands": {
        "soil_health": 0.43, "biodiversity": 0.48, "watershed": 0.32, "solar": 0.90,
        "wind": 0.58, "agri": 0.38, "remoteness": 0.52, "pollution": 0.25,
    },
    "coastal_delta": {
        "soil_health": 0.67, "biodiversity": 0.70, "watershed": 0.78, "solar": 0.68,
        "wind": 0.66, "agri": 0.82, "remoteness": 0.20, "pollution": 0.38,
    },
    "mountain_water": {
        "soil_health": 0.60, "biodiversity": 0.72, "watershed": 0.90, "solar": 0.62,
        "wind": 0.70, "agri": 0.42, "remoteness": 0.66, "pollution": 0.18,
    },
    "urban_corridor": {
        "soil_health": 0.42, "biodiversity": 0.32, "watershed": 0.55, "solar": 0.58,
        "wind": 0.50, "agri": 0.25, "remoteness": 0.12, "pollution": 0.55,
    },
    "steppe_grainland": {
        "soil_health": 0.66, "biodiversity": 0.54, "watershed": 0.48, "solar": 0.70,
        "wind": 0.73, "agri": 0.88, "remoteness": 0.40, "pollution": 0.24,
    },
    "subpolar_periphery": {
        "soil_health": 0.52, "biodiversity": 0.58, "watershed": 0.66, "solar": 0.35,
        "wind": 0.80, "agri": 0.22, "remoteness": 0.72, "pollution": 0.16,
    },
}

REGION_NAMES = [
    "Aqua-North Basin", "Forest Equator Belt", "Delta Commons", "Temperate Ring",
    "Dryland Solar Arc", "Mountain Water Towers", "Steppe Grain Commons", "Urban Repair Web",
    "Coastal Wind Belt", "Subpolar Storage Rim", "Island Commons", "Highland Care Ring",
    "Inland Logistics Mesh", "Rainfed Agroforest Zone", "Desert Edge Settlements", "River City Chain",
]

GROUP_NAMES = ("water", "agriculture", "energy", "housing", "health", "care", "education", "logistics", "manufacturing", "storage", "governance", "knowledge", "resilience", "repair", "ecology")
SKILL_NAMES = ("infrastructure", "agriculture", "energy", "construction", "health", "care", "education", "logistics", "manufacturing", "storage", "governance", "knowledge", "resilience", "repair", "ecology", "general")


def make_cohorts(rng: random.Random, population: float, base_health: float, base_education: float, democracy: float) -> List[PopulationCohort]:
    child_share = clamp(rng.uniform(0.18, 0.28), 0.12, 0.35)
    elder_share = clamp(rng.uniform(0.10, 0.20), 0.05, 0.28)
    adult_share = max(0.45, 1.0 - child_share - elder_share)
    shares = [("children", child_share, 0.10), ("adults", adult_share, 1.0), ("elders", elder_share, 0.15)]
    cohorts = []
    for name, share, age_factor in shares:
        skill = {}
        for sk in SKILL_NAMES:
            if name == "children":
                val = base_education * rng.uniform(0.35, 0.65)
            elif name == "elders":
                val = base_education * rng.uniform(0.55, 1.05)
            else:
                val = base_education * rng.uniform(0.75, 1.25)
            skill[sk] = clamp(val, 0.05, 1.0)
        if name == "children":
            health = clamp(base_health * rng.uniform(0.90, 1.10), 0.05, 1.0)
            education = clamp(base_education * rng.uniform(0.55, 0.85), 0.05, 1.0)
        elif name == "elders":
            health = clamp(base_health * rng.uniform(0.65, 0.95), 0.05, 1.0)
            education = clamp(base_education * rng.uniform(0.85, 1.15), 0.05, 1.0)
        else:
            health = clamp(base_health * rng.uniform(0.85, 1.15), 0.05, 1.0)
            education = clamp(base_education * rng.uniform(0.85, 1.15), 0.05, 1.0)
        cohorts.append(PopulationCohort(
            name=name,
            size=population * share,
            health=health,
            education=education,
            autonomy=clamp(rng.uniform(0.55, 0.88) * (0.75 + 0.35 * democracy), 0.05, 1.0),
            trust=clamp(rng.uniform(0.45, 0.82) * (0.70 + 0.45 * democracy), 0.02, 1.0),
            skill=skill,
            age_factor=age_factor,
        ))
    return cohorts


def create_commune(rng: random.Random, region_name: str, biome: str, population: float, scenario: str) -> Commune:
    b = BIOME_LIBRARY[biome]
    base_health = clamp(rng.uniform(0.55, 0.84) - (0.06 if scenario == "scarcity_shock" else 0.0), 0.1, 1.0)
    base_education = clamp(rng.uniform(0.50, 0.86) - (0.05 if scenario == "technocratic_control" else 0.0), 0.1, 1.0)
    democracy = clamp(rng.uniform(0.45, 0.86), 0.1, 1.0)
    if scenario == "technocratic_control":
        democracy *= 0.62
    if scenario == "local_democracy":
        democracy = clamp(democracy * 1.20, 0.1, 1.0)

    cohorts = make_cohorts(rng, population, base_health, base_education, democracy)
    pop = population

    # Initial stocks/capacities. They represent normalized person-months.
    water_stock = pop * rng.uniform(0.55, 1.75) * (0.65 + b["watershed"])
    food_stock = pop * rng.uniform(0.50, 1.60) * (0.55 + b["agri"])
    energy_stock = pop * rng.uniform(0.45, 1.35) * (0.55 + 0.50 * max(b["solar"], b["wind"]))
    if scenario == "scarcity_shock":
        water_stock *= 0.70
        food_stock *= 0.68
        energy_stock *= 0.78

    shelter_capacity = pop * rng.uniform(0.78, 1.18)
    if biome == "urban_corridor":
        shelter_capacity *= rng.uniform(0.88, 1.15)
    health_cap = pop * NEED_PER_PERSON["health"] * rng.uniform(0.55, 1.25) * (0.65 + base_education)
    care_cap = pop * NEED_PER_PERSON["care"] * rng.uniform(0.60, 1.20) * (0.65 + base_health)
    edu_cap = pop * NEED_PER_PERSON["education"] * rng.uniform(0.60, 1.30) * (0.65 + base_education)
    mobility_cap = pop * NEED_PER_PERSON["mobility"] * rng.uniform(0.55, 1.25) * (1.1 - b["remoteness"])
    manufacturing_cap = pop * NEED_PER_PERSON["manufacturing"] * rng.uniform(0.45, 1.15) * (0.70 + base_education)
    storage_cap = pop * NEED_PER_PERSON["storage"] * rng.uniform(0.45, 1.30) * (0.70 + (1.0 - b["remoteness"]))
    governance_cap = pop * NEED_PER_PERSON["governance"] * rng.uniform(0.55, 1.25) * (0.65 + democracy)
    knowledge_cap = pop * NEED_PER_PERSON["knowledge"] * rng.uniform(0.45, 1.25) * (0.65 + base_education)
    resilience_cap = pop * NEED_PER_PERSON["resilience"] * rng.uniform(0.40, 1.10) * (0.65 + democracy)

    stocks = {
        "water": water_stock,
        "food": food_stock,
        "energy": energy_stock,
        "repair_materials": pop * rng.uniform(0.05, 0.22),
        "waste": pop * rng.uniform(0.06, 0.23) * (1.0 + b["pollution"]),
    }
    capacities = {
        "shelter": shelter_capacity,
        "health": health_cap,
        "care": care_cap,
        "education": edu_cap,
        "mobility": mobility_cap,
        "manufacturing": manufacturing_cap,
        "storage": storage_cap,
        "governance": governance_cap,
        "knowledge": knowledge_cap,
        "resilience": resilience_cap,
    }
    environment = {
        "soil_health": clamp(b["soil_health"] * rng.uniform(0.82, 1.12), 0.05, 1.0),
        "biodiversity": clamp(b["biodiversity"] * rng.uniform(0.78, 1.12), 0.05, 1.0),
        "watershed": clamp(b["watershed"] * rng.uniform(0.80, 1.15), 0.05, 1.0),
        "solar": clamp(b["solar"] * rng.uniform(0.90, 1.10), 0.05, 1.0),
        "wind": clamp(b["wind"] * rng.uniform(0.90, 1.10), 0.05, 1.0),
        "agri": clamp(b["agri"] * rng.uniform(0.82, 1.15), 0.05, 1.0),
        "remoteness": clamp(b["remoteness"] * rng.uniform(0.85, 1.20), 0.02, 1.0),
        "local_pollution": clamp(b["pollution"] * rng.uniform(0.80, 1.25), 0.02, 1.0),
        "renewable_infrastructure": clamp(rng.uniform(0.30, 0.70) * (0.65 + max(b["solar"], b["wind"])), 0.05, 1.0),
    }

    group_base = {}
    for g in GROUP_NAMES:
        val = rng.uniform(0.35, 0.85)
        if g == "agriculture":
            val *= 0.65 + b["agri"]
        elif g == "energy":
            val *= 0.65 + max(b["solar"], b["wind"])
        elif g == "ecology":
            val *= 0.70 + 0.35 * b["biodiversity"]
        elif g == "logistics":
            val *= 1.15 - 0.55 * b["remoteness"]
        elif g == "water":
            val *= 0.70 + 0.50 * b["watershed"]
        elif g == "manufacturing":
            val *= 0.75 + base_education
        elif g == "storage":
            val *= 0.80 + 0.25 * (1.0 - b["remoteness"])
        elif g == "governance":
            val *= 0.65 + democracy
        elif g == "knowledge":
            val *= 0.70 + base_education
        elif g == "resilience":
            val *= 0.70 + 0.25 * democracy + 0.20 * b["watershed"]
        group_base[g] = clamp(val, 0.05, 1.0)

    return Commune(
        name="%s Commune %03d" % (region_name[:9].replace(" ", ""), rng.randint(1, 999)),
        region_name=region_name,
        biome=biome,
        cohorts=cohorts,
        stocks=stocks,
        capacities=capacities,
        environment=environment,
        group_base=group_base,
        democratic_quality=democracy,
        truth_error=clamp(rng.uniform(0.08, 0.26) + (0.12 if scenario == "technocratic_control" else 0.0), 0.02, 0.75),
    )


def create_planet(seed: int, total_population: float, regions_count: int, communes_per_region: int, scenario: str) -> Tuple[List[Region], BoundaryState, EffectPlanner]:
    rng = random.Random(seed)
    biomes = list(BIOME_LIBRARY.keys())
    rng.shuffle(biomes)
    region_pops_raw = [lognormal_near(rng, 1.0, 0.75) for _ in range(regions_count)]
    pop_sum = sum(region_pops_raw)
    regions: List[Region] = []
    for i in range(regions_count):
        name = REGION_NAMES[i % len(REGION_NAMES)]
        if i >= len(REGION_NAMES):
            name += " %d" % (i + 1)
        biome = biomes[i % len(biomes)]
        b = BIOME_LIBRARY[biome]
        region_pop = total_population * region_pops_raw[i] / pop_sum
        commune_raw = [lognormal_near(rng, 1.0, 0.60) for _ in range(communes_per_region)]
        commune_sum = sum(commune_raw)
        communes = []
        for j in range(communes_per_region):
            cpop = region_pop * commune_raw[j] / commune_sum
            communes.append(create_commune(rng, name, biome, cpop, scenario))
        regions.append(Region(
            name=name,
            biome=biome,
            communes=communes,
            logistic_hub=clamp((1.0 - b["remoteness"]) * rng.uniform(0.70, 1.15), 0.05, 1.0),
            climate_risk=clamp(rng.uniform(0.25, 0.75) + (0.25 if biome in ("drylands", "coastal_delta") else 0.0), 0.05, 1.0),
        ))

    if scenario == "ecological_crisis":
        pressures = {
            "climate": 1.18,
            "biosphere": 1.12,
            "freshwater": 1.08,
            "soil": 1.04,
            "pollution": 1.06,
            "material_throughput": 1.10,
            "energy_throughput": 1.08,
        }
    elif scenario == "scarcity_shock":
        pressures = {
            "climate": 1.02,
            "biosphere": 0.96,
            "freshwater": 1.07,
            "soil": 0.98,
            "pollution": 0.95,
            "material_throughput": 1.03,
            "energy_throughput": 1.00,
        }
    else:
        pressures = {
            "climate": 0.96,
            "biosphere": 0.92,
            "freshwater": 0.88,
            "soil": 0.86,
            "pollution": 0.91,
            "material_throughput": 0.94,
            "energy_throughput": 0.93,
        }
    boundary = BoundaryState(pressures=pressures)

    if scenario == "technocratic_control":
        planner = EffectPlanner(democratic_feedback=0.35, centralization=0.82, privacy_pressure=0.42,
                                cooperation=0.72, redistribution_strength=0.72, climate_discipline=0.70,
                                innovation_rate=0.36, renewable_bias=0.66)
    elif scenario == "local_democracy":
        planner = EffectPlanner(democratic_feedback=0.92, centralization=0.16, privacy_pressure=0.06,
                                cooperation=0.88, redistribution_strength=0.82, climate_discipline=0.76,
                                innovation_rate=0.42, renewable_bias=0.75)
    elif scenario == "ecological_crisis":
        planner = EffectPlanner(democratic_feedback=0.78, centralization=0.34, privacy_pressure=0.12,
                                cooperation=0.86, redistribution_strength=0.88, climate_discipline=0.88,
                                innovation_rate=0.46, renewable_bias=0.84)
    elif scenario == "scarcity_shock":
        planner = EffectPlanner(democratic_feedback=0.76, centralization=0.35, privacy_pressure=0.13,
                                cooperation=0.83, redistribution_strength=0.91, climate_discipline=0.80,
                                innovation_rate=0.38, renewable_bias=0.74)
    else:
        planner = EffectPlanner()
    return regions, boundary, planner


# ---------------------------------------------------------------------------
# Simulation dynamics
# ---------------------------------------------------------------------------


@dataclass
class StepImpacts:
    step: int = 0
    impacts: Dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in BOUNDARY_NAMES})
    regeneration: Dict[str, float] = field(default_factory=lambda: {name: 0.0 for name in BOUNDARY_NAMES})
    global_transfers: float = 0.0
    truth_vectors: List[TruthVector] = field(default_factory=list)
    flows: List[EffectFlow] = field(default_factory=list)
    domain_labor: Dict[str, float] = field(default_factory=lambda: {domain: 0.0 for domain in DOMAINS})
    domain_outputs: Dict[str, float] = field(default_factory=lambda: {domain: 0.0 for domain in DOMAINS})

    def add_impact(self, name: str, value: float) -> None:
        self.impacts[name] = self.impacts.get(name, 0.0) + value

    def add_regen(self, name: str, value: float) -> None:
        self.regeneration[name] = self.regeneration.get(name, 0.0) + value

    def add_labor(self, domain: str, value: float) -> None:
        self.domain_labor[domain] = self.domain_labor.get(domain, 0.0) + value

    def add_output(self, domain: str, value: float) -> None:
        self.domain_outputs[domain] = self.domain_outputs.get(domain, 0.0) + value

    def add_flow(self, flow: EffectFlow) -> None:
        self.flows.append(flow)


def flow_values(commune: Commune, domain: str) -> Dict[str, float]:
    values = commune.last_truth_values.get(domain, {})
    if values:
        return dict(values)
    return {dim: 0.0 for dim in TRUTH_DIMS}


def make_effect_flow(step: int, kind: str, legacy_term_replaced: str, action: str, domain: str,
                     source: Commune, target: Commune, activated_effect: float, note: str = "") -> EffectFlow:
    values = flow_values(target, domain)
    direction = "angle=%.3f; difference=%.3f; determination=%.3f" % (
        values.get("angle_direction", 0.0),
        values.get("difference", 0.0),
        values.get("determination", 0.0),
    )
    causal_link = "%s:%s->%s" % (domain, source.name, target.name)
    return EffectFlow(
        step=step,
        kind=kind,
        legacy_term_replaced=legacy_term_replaced,
        action=action,
        domain=domain,
        sector=SECTOR_FOR_DOMAIN.get(domain, "unmapped"),
        from_region=source.region_name,
        from_commune=source.name,
        to_region=target.region_name,
        to_commune=target.name,
        activated_effect=max(0.0, activated_effect),
        causal_link=causal_link,
        direction_vector=direction,
        values=values,
        note=note,
    )


def produce_local_effects(commune: Commune, shares: Dict[str, float], boundary: BoundaryState, planner: EffectPlanner, step_impacts: StepImpacts) -> None:
    pop = commune.population()
    labor = commune.productive_time()
    boundary_penalty = boundary.penalty()
    education = commune.average_education()
    health = commune.average_health()
    cooperation = planner.cooperation * (0.65 + 0.35 * commune.average_trust())
    # A normalized labour productivity unit. 0.12 means full adult-time roughly covers monthly needs with tech/capacity factors.
    base_prod = 12.0 * labor * boundary_penalty * cooperation

    # Local effect domains. All outputs are person-month-ish normalized units.
    for domain in DOMAINS:
        domain_labor = base_prod * shares.get(domain, 0.0)
        if domain_labor <= 0.0:
            continue
        step_impacts.add_labor(domain, domain_labor)
        step_impacts.add_output(domain, domain_labor)
        step_impacts.add_flow(make_effect_flow(
            step_impacts.step,
            kind="contribution_offer",
            legacy_term_replaced="sell/labour_supply",
            action="activate_causal_effect",
            domain=domain,
            source=commune,
            target=commune,
            activated_effect=domain_labor,
            note="contribution time directed by truth-vector priority, not wage/price",
        ))
        if domain == "water":
            skill = commune.skill("infrastructure")
            watershed = commune.environment.get("watershed", 0.7)
            energy_use = 0.09 * domain_labor
            actual_energy = min(commune.stocks.get("energy", 0.0), energy_use)
            energy_factor = 0.45 + 0.55 * sat_ratio(actual_energy, energy_use)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - actual_energy
            output = domain_labor * (0.9 + 1.1 * watershed) * (0.55 + skill) * energy_factor
            commune.stocks["water"] = commune.stocks.get("water", 0.0) + output
            step_impacts.add_impact("freshwater", 0.0000000000016 * output * max(0.2, 1.1 - watershed))
            step_impacts.add_impact("energy_throughput", 0.0000000000002 * actual_energy)

        elif domain == "food":
            skill = commune.skill("agriculture")
            soil = commune.environment.get("soil_health", 0.7)
            water_need = 0.20 * domain_labor * (1.05 - 0.35 * soil)
            energy_need = 0.08 * domain_labor
            water_used = min(commune.stocks.get("water", 0.0), water_need)
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["water"] = commune.stocks.get("water", 0.0) - water_used
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            input_factor = 0.30 + 0.45 * sat_ratio(water_used, water_need) + 0.25 * sat_ratio(energy_used, energy_need)
            regenerative = clamp(0.25 + 0.45 * shares.get("ecology", 0.0) + 0.20 * planner.climate_discipline)
            output = domain_labor * (0.55 + skill) * (0.55 + commune.environment.get("agri", 0.6)) * (0.55 + soil) * input_factor
            commune.stocks["food"] = commune.stocks.get("food", 0.0) + output
            # Soil can degrade or improve depending on regenerative direction.
            commune.environment["soil_health"] = clamp(soil + 0.0015 * regenerative - 0.0018 * (1.0 - regenerative))
            step_impacts.add_impact("freshwater", 0.0000000000012 * water_used)
            step_impacts.add_impact("soil", 0.0000000000010 * output * (1.0 - regenerative))
            step_impacts.add_regen("soil", 0.0000000000011 * output * regenerative)

        elif domain == "energy":
            skill = commune.skill("energy")
            renewable = commune.environment.get("renewable_infrastructure", 0.5)
            solar_wind = max(commune.environment.get("solar", 0.5), commune.environment.get("wind", 0.5))
            repair_need = 0.10 * domain_labor * (0.85 - 0.45 * renewable)
            repair_used = min(commune.stocks.get("repair_materials", 0.0), max(0.0, repair_need))
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - repair_used
            output = domain_labor * (0.60 + skill) * (0.55 + solar_wind) * (0.70 + renewable)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) + output
            # Infrastructure improves with material and innovation.
            commune.environment["renewable_infrastructure"] = clamp(renewable + 0.0015 * planner.innovation_rate * sat_ratio(repair_used, max(repair_need, 1.0)))
            fossil_fraction = clamp((1.0 - renewable) * (1.0 - planner.renewable_bias) + 0.20 * max(0.0, boundary.pressures.get("energy_throughput", 0.9) - 1.0), 0.02, 0.65)
            step_impacts.add_impact("climate", 0.0000000000024 * output * fossil_fraction)
            step_impacts.add_impact("energy_throughput", 0.00000000000025 * output)
            step_impacts.add_impact("material_throughput", 0.0000000000010 * max(0.0, repair_need - repair_used) + 0.0000000000004 * repair_used)

        elif domain == "shelter":
            skill = commune.skill("construction")
            repair_material = commune.stocks.get("repair_materials", 0.0)
            # First reallocate/repair existing capacity; only then build.
            reuse_bias = clamp(0.55 + 0.35 * planner.sufficiency_norm + 0.25 * shares.get("repair", 0.0))
            material_need = domain_labor * (0.10 + 0.25 * (1.0 - reuse_bias))
            used_mat = min(repair_material, material_need)
            commune.stocks["repair_materials"] = repair_material - used_mat
            gained = domain_labor * (0.25 + 0.75 * reuse_bias) * (0.65 + skill) * (0.55 + sat_ratio(used_mat, max(material_need, 1.0)))
            commune.capacities["shelter"] = commune.capacities.get("shelter", 0.0) + gained
            waste_created = 0.035 * gained * (1.0 - reuse_bias)
            commune.stocks["waste"] = commune.stocks.get("waste", 0.0) + waste_created
            step_impacts.add_impact("material_throughput", 0.0000000000018 * max(0.0, material_need - used_mat) + 0.0000000000006 * used_mat)
            step_impacts.add_impact("pollution", 0.0000000000010 * waste_created)

        elif domain == "health":
            skill = commune.skill("health")
            energy_need = 0.05 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            output = domain_labor * (0.70 + skill) * (0.70 + health) * (0.65 + 0.35 * sat_ratio(energy_used, energy_need))
            commune.capacities["health"] = commune.capacities.get("health", 0.0) + output
            step_impacts.add_impact("energy_throughput", 0.00000000000018 * energy_used)

        elif domain == "care":
            skill = commune.skill("care")
            output = domain_labor * (0.75 + skill) * (0.70 + commune.average_autonomy())
            commune.capacities["care"] = commune.capacities.get("care", 0.0) + output

        elif domain == "education":
            skill = commune.skill("education")
            energy_need = 0.025 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            output = domain_labor * (0.72 + skill) * (0.70 + commune.democratic_quality) * (0.75 + 0.25 * sat_ratio(energy_used, energy_need))
            commune.capacities["education"] = commune.capacities.get("education", 0.0) + output
            step_impacts.add_impact("energy_throughput", 0.00000000000012 * energy_used)

        elif domain == "mobility":
            skill = commune.skill("logistics")
            energy_need = 0.11 * domain_labor * (0.70 + commune.environment.get("remoteness", 0.5))
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            efficiency = planner.logistics_efficiency * (0.75 + 0.25 * commune.environment.get("renewable_infrastructure", 0.5))
            output = domain_labor * (0.58 + skill) * (0.62 + efficiency) * (0.60 + 0.40 * sat_ratio(energy_used, energy_need))
            commune.capacities["mobility"] = commune.capacities.get("mobility", 0.0) + output
            carbon_intensity = (1.0 - commune.environment.get("renewable_infrastructure", 0.5)) * (1.0 - planner.renewable_bias)
            step_impacts.add_impact("climate", 0.0000000000015 * energy_used * carbon_intensity)
            step_impacts.add_impact("energy_throughput", 0.00000000000030 * energy_used)

        elif domain == "manufacturing":
            skill = commune.skill("manufacturing")
            energy_need = 0.14 * domain_labor
            material_need = 0.10 * domain_labor * (1.0 - 0.35 * shares.get("repair", 0.0))
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            material_used = min(commune.stocks.get("repair_materials", 0.0), material_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - material_used
            input_factor = 0.35 + 0.40 * sat_ratio(energy_used, energy_need) + 0.25 * sat_ratio(material_used, material_need)
            tools = domain_labor * (0.50 + skill) * input_factor
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) + 0.42 * tools
            commune.capacities["manufacturing"] = commune.capacities.get("manufacturing", 0.0) + 0.58 * tools
            step_impacts.add_impact("material_throughput", 0.0000000000014 * max(0.0, material_need - material_used) + 0.0000000000005 * material_used)
            step_impacts.add_impact("energy_throughput", 0.00000000000025 * energy_used)
            step_impacts.add_impact("pollution", 0.0000000000007 * max(0.0, tools - material_used))

        elif domain == "storage":
            skill = commune.skill("storage")
            energy_need = 0.035 * domain_labor
            material_need = 0.07 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            material_used = min(commune.stocks.get("repair_materials", 0.0), material_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - material_used
            gained = domain_labor * (0.55 + skill) * (0.55 + 0.45 * sat_ratio(material_used, material_need))
            commune.capacities["storage"] = commune.capacities.get("storage", 0.0) + gained
            # Storage reduces spoilage and grid losses by preserving basic stocks.
            protection = clamp(0.000025 * gained / max(1.0, pop))
            commune.stocks["water"] = commune.stocks.get("water", 0.0) * (1.0 + protection)
            commune.stocks["food"] = commune.stocks.get("food", 0.0) * (1.0 + protection)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) * (1.0 + 0.5 * protection)
            step_impacts.add_impact("material_throughput", 0.0000000000007 * material_used)
            step_impacts.add_impact("energy_throughput", 0.00000000000010 * energy_used)

        elif domain == "governance":
            skill = commune.skill("governance")
            output = domain_labor * (0.55 + skill) * (0.45 + commune.democratic_quality)
            commune.capacities["governance"] = commune.capacities.get("governance", 0.0) + output
            correction = 0.00000000035 * output / max(1.0, pop)
            commune.truth_error = clamp(commune.truth_error - correction * planner.democratic_feedback + 0.00003 * planner.centralization * planner.privacy_pressure)
            commune.democratic_quality = clamp(commune.democratic_quality + 0.00000000022 * output / max(1.0, pop) - 0.00002 * planner.centralization * planner.privacy_pressure)

        elif domain == "knowledge":
            skill = commune.skill("knowledge")
            energy_need = 0.020 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            output = domain_labor * (0.60 + skill) * (0.70 + commune.average_education()) * (0.70 + 0.30 * sat_ratio(energy_used, energy_need))
            commune.capacities["knowledge"] = commune.capacities.get("knowledge", 0.0) + output
            learning = 0.00000000018 * output / max(1.0, pop)
            for cohort in commune.cohorts:
                for sk in ("infrastructure", "agriculture", "energy", "construction", "health", "logistics", "manufacturing", "storage", "repair", "ecology"):
                    cohort.skill[sk] = clamp(cohort.skill.get(sk, 0.4) + learning)
            commune.environment["renewable_infrastructure"] = clamp(commune.environment.get("renewable_infrastructure", 0.5) + 0.00000000008 * output / max(1.0, pop) * planner.innovation_rate)
            step_impacts.add_impact("energy_throughput", 0.00000000000007 * energy_used)

        elif domain == "resilience":
            skill = commune.skill("resilience")
            material_need = 0.06 * domain_labor
            material_used = min(commune.stocks.get("repair_materials", 0.0), material_need)
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) - material_used
            output = domain_labor * (0.55 + skill) * (0.60 + commune.democratic_quality) * (0.55 + 0.45 * sat_ratio(material_used, material_need))
            commune.capacities["resilience"] = commune.capacities.get("resilience", 0.0) + output
            # Emergency readiness creates small local buffers and lowers damage from shocks.
            commune.stocks["water"] = commune.stocks.get("water", 0.0) + 0.04 * output
            commune.stocks["food"] = commune.stocks.get("food", 0.0) + 0.03 * output
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) + 0.02 * output
            step_impacts.add_impact("material_throughput", 0.0000000000005 * material_used)

        elif domain == "repair":
            skill = commune.skill("repair")
            waste = commune.stocks.get("waste", 0.0)
            processed = min(waste, domain_labor * (0.75 + skill))
            commune.stocks["waste"] = waste - processed
            material_gain = processed * (0.42 + 0.38 * skill)
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) + material_gain
            # Repair also maintains existing capacities.
            for cap in MACRO_CAPACITY_DOMAINS:
                commune.capacities[cap] = commune.capacities.get(cap, 0.0) * (1.0 + 0.00015 * skill)
            step_impacts.add_regen("material_throughput", 0.0000000000014 * material_gain)
            step_impacts.add_regen("pollution", 0.0000000000010 * processed)

        elif domain == "ecology":
            skill = commune.skill("ecology")
            energy_need = 0.025 * domain_labor
            energy_used = min(commune.stocks.get("energy", 0.0), energy_need)
            commune.stocks["energy"] = commune.stocks.get("energy", 0.0) - energy_used
            effect = domain_labor * (0.55 + skill) * (0.65 + commune.democratic_quality) * (0.65 + 0.35 * sat_ratio(energy_used, energy_need))
            commune.environment["soil_health"] = clamp(commune.environment.get("soil_health", 0.7) + 0.00000000020 * effect)
            commune.environment["biodiversity"] = clamp(commune.environment.get("biodiversity", 0.7) + 0.00000000018 * effect)
            commune.environment["watershed"] = clamp(commune.environment.get("watershed", 0.7) + 0.00000000016 * effect)
            commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) - 0.00000000016 * effect)
            step_impacts.add_regen("biosphere", 0.0000000000022 * effect)
            step_impacts.add_regen("soil", 0.0000000000018 * effect)
            step_impacts.add_regen("freshwater", 0.0000000000013 * effect)
            step_impacts.add_regen("pollution", 0.0000000000015 * effect)
            # Biosphere and soil also draw down a small share of climate pressure.
            step_impacts.add_regen("climate", 0.00000000000055 * effect)

        elif domain == "waste":
            skill = commune.skill("repair")
            waste = commune.stocks.get("waste", 0.0)
            processed = min(waste, domain_labor * (0.65 + skill))
            commune.stocks["waste"] = waste - processed
            commune.stocks["repair_materials"] = commune.stocks.get("repair_materials", 0.0) + processed * (0.28 + 0.28 * skill)
            commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) - 0.00000000010 * processed)
            step_impacts.add_regen("pollution", 0.0000000000012 * processed)
            step_impacts.add_regen("material_throughput", 0.0000000000008 * processed)

    # Capacity decay / maintenance burden: if not maintained, infrastructure slowly decays.
    maintenance_quality = clamp(shares.get("repair", 0.0) * 5.0 + shares.get("waste", 0.0) * 2.0 + commune.average_trust() * 0.15)
    decay = 0.0045 * (1.0 - maintenance_quality)
    for cap in MACRO_CAPACITY_DOMAINS:
        commune.capacities[cap] = max(0.0, commune.capacities.get(cap, 0.0) * (1.0 - decay))


def redistribute_planetary_commons(regions: List[Region], planner: EffectPlanner, step_impacts: StepImpacts) -> None:
    """Planetary transfers across regions/communes without prices.

    This is what makes it a planet economy rather than a national economy:
    the algorithm checks real need and surplus globally, constrained by logistics
    and ecological cost. It does not care about national currency, exports, or GDP.
    """
    communes = [c for r in regions for c in r.communes]
    for domain in CONSUMABLE_DOMAINS:
        # Basic sufficiency target. Surplus above target can move.
        target_factor = 1.03
        donors = []
        receivers = []
        total_surplus = 0.0
        total_deficit = 0.0
        for c in communes:
            need = c.need(domain)
            stock = c.stocks.get(domain, 0.0)
            target = target_factor * need
            if stock > target:
                surplus = (stock - target) * planner.redistribution_strength
                donors.append([c, surplus])
                total_surplus += surplus
            else:
                deficit = max(0.0, need - stock)
                if deficit > 0.0:
                    priority = c.last_priorities.get(domain, 0.5)
                    receivers.append([c, deficit, priority])
                    total_deficit += deficit
        if total_surplus <= 0.0 or total_deficit <= 0.0:
            continue
        receivers.sort(key=lambda x: x[2], reverse=True)
        transfer_budget = min(total_surplus, total_deficit)
        # Global logistics capacity from mobility + logistics hubs.
        mobility_cap = sum(c.capacities.get("mobility", 0.0) for c in communes)
        mobility_need = sum(c.need("mobility") for c in communes)
        logistics_factor = clamp(sat_ratio(mobility_cap, max(mobility_need, 1.0)) * planner.logistics_efficiency)
        transfer_budget *= logistics_factor
        if transfer_budget <= 0.0:
            continue

        donor_i = 0
        for recv in receivers:
            rc, deficit, priority = recv
            if transfer_budget <= 1e-9:
                break
            want = min(deficit, transfer_budget)
            received = 0.0
            while want > 1e-9 and donor_i < len(donors):
                dc, avail = donors[donor_i]
                move = min(want, avail)
                if move <= 1e-9:
                    donor_i += 1
                    continue
                dc.stocks[domain] = dc.stocks.get(domain, 0.0) - move
                step_impacts.add_flow(make_effect_flow(
                    step_impacts.step,
                    kind="planetary_transfer",
                    legacy_term_replaced="buy/sell/import/export",
                    action="causal_transfer_to_need",
                    domain=domain,
                    source=dc,
                    target=rc,
                    activated_effect=move,
                    note="surplus and deficit matched by urgency, not purchasing power",
                ))
                received += move
                want -= move
                transfer_budget -= move
                donors[donor_i][1] -= move
                if donors[donor_i][1] <= 1e-9:
                    donor_i += 1
            rc.stocks[domain] = rc.stocks.get(domain, 0.0) + received
            step_impacts.global_transfers += received
            # Transfer has ecological cost but is less damaging if energy system is renewable.
            if received > 0.0:
                avg_renew = mean(c.environment.get("renewable_infrastructure", 0.5) for c in communes)
                carbon = (1.0 - avg_renew) * (1.0 - planner.renewable_bias)
                step_impacts.add_impact("climate", 0.00000000000055 * received * carbon)
                step_impacts.add_impact("energy_throughput", 0.00000000000016 * received)
                step_impacts.add_impact("material_throughput", 0.00000000000020 * received)


def consume_and_update_people(commune: Commune, planner: EffectPlanner, step_impacts: Optional[StepImpacts] = None) -> None:
    satisfaction: Dict[str, float] = {}
    # Consumables: water, food, energy.
    for domain in CONSUMABLE_DOMAINS:
        need = commune.need(domain)
        stock = commune.stocks.get(domain, 0.0)
        sat = sat_ratio(stock, need)
        used = min(stock, need)
        commune.stocks[domain] = max(0.0, stock - used)
        satisfaction[domain] = sat
        if step_impacts is not None and used > 0.0:
            step_impacts.add_flow(make_effect_flow(
                step_impacts.step,
                kind="need_acceptance",
                legacy_term_replaced="buy/consumption",
                action="accept_effect_for_need",
                domain=domain,
                source=commune,
                target=commune,
                activated_effect=used,
                note="need satisfaction accepted through existence/intensity/time, not purchasing power",
            ))

    # Capacities: shelter is not consumed like food; health/care/education/mobility capacity is used this month.
    shelter_need = commune.need("shelter")
    shelter_sat = sat_ratio(commune.capacities.get("shelter", 0.0), shelter_need)
    satisfaction["shelter"] = shelter_sat
    if step_impacts is not None:
        step_impacts.add_flow(make_effect_flow(
            step_impacts.step,
            kind="need_acceptance",
            legacy_term_replaced="buy/rent",
            action="stabilize_shelter_existence",
            domain="shelter",
            source=commune,
            target=commune,
            activated_effect=min(commune.capacities.get("shelter", 0.0), shelter_need),
            note="housing access through real need and capacity, not rent/price",
        ))

    for domain in SERVICE_DOMAINS:
        need = commune.need(domain)
        cap = commune.capacities.get(domain, 0.0)
        sat = sat_ratio(cap, need)
        used = min(cap, need)
        # Service capacity partly persists as institution, partly consumed as monthly service.
        commune.capacities[domain] = max(0.0, cap - 0.72 * used)
        satisfaction[domain] = sat
        if step_impacts is not None and used > 0.0:
            step_impacts.add_flow(make_effect_flow(
                step_impacts.step,
                kind="need_acceptance",
                legacy_term_replaced="buy/service_purchase",
                action="accept_service_effect",
                domain=domain,
                source=commune,
                target=commune,
                activated_effect=used,
                note="service is used as social effect, not purchased service value",
            ))

    # Waste from consumption; lower if repair/sufficiency norms are strong.
    pop = commune.population()
    consumption_shortfall = 1.0 - mean(satisfaction.get(d, 1.0) for d in CONSUMABLE_DOMAINS)
    waste_created = pop * 0.028 * (0.65 + 0.35 * mean([satisfaction.get("food", 1.0), satisfaction.get("energy", 1.0)])) * (1.0 - 0.30 * planner.sufficiency_norm)
    # Crisis can create unmanaged waste through breakdown.
    waste_created += pop * 0.012 * consumption_shortfall
    commune.stocks["waste"] = commune.stocks.get("waste", 0.0) + waste_created
    commune.environment["local_pollution"] = clamp(commune.environment.get("local_pollution", 0.2) + 0.00000000005 * waste_created)

    # Update cohorts. If system is highly centralized, privacy pressure is stronger.
    privacy = clamp(planner.privacy_pressure + 0.15 * planner.centralization * (1.0 - commune.democratic_quality))
    gov_quality = clamp(0.55 * commune.democratic_quality + 0.30 * commune.average_trust() + 0.15 * (1.0 - commune.truth_error))
    for cohort in commune.cohorts:
        cohort.update_from_satisfaction(satisfaction, gov_quality, privacy)

    # Demographic dynamics: cautious and bounded. This is not a detailed population model.
    avg_sat = mean(satisfaction.values(), 0.85)
    edu = commune.average_education()
    health = commune.average_health()
    # Good conditions sustain; severe unmet basics cause contraction. Higher education moderates growth.
    monthly_growth = 0.00055 * (avg_sat - 0.62) + 0.00035 * (health - 0.55) - 0.00028 * (edu - 0.55)
    monthly_growth = clamp(monthly_growth, -0.0045, 0.0035)
    for cohort in commune.cohorts:
        cohort.size = max(0.0, cohort.size * (1.0 + monthly_growth))

    commune.last_satisfaction = satisfaction
    commune.update_truth_error(avg_sat, planner)


def simulate_step(regions: List[Region], boundary: BoundaryState, planner: EffectPlanner, step: int) -> Tuple[GlobalMetrics, List[TruthVector], StepImpacts]:
    step_impacts = StepImpacts(step=step)

    # 1) Compute truth vectors: reality -> logical stacked values -> priority.
    for region in regions:
        for commune in region.communes:
            tvs = [commune.truth_vector(domain, boundary, planner) for domain in DOMAINS]
            step_impacts.truth_vectors.extend(tvs)
            commune.last_priorities = {tv.domain: tv.priority() for tv in tvs}
            commune.last_truth_values = {tv.domain: dict(tv.values) for tv in tvs}
            shares = planner.labor_shares(tvs, commune, boundary)
            commune.last_labor_shares = shares

    # 2) Produce local effects according to truth-vector priority.
    for region in regions:
        for commune in region.communes:
            produce_local_effects(commune, commune.last_labor_shares, boundary, planner, step_impacts)

    # 3) Redistribute planetary commons: global real need and surplus, no price/currency.
    redistribute_planetary_commons(regions, planner, step_impacts)

    # 4) Consume/satisfy needs and update individuals/cohorts.
    for region in regions:
        for commune in region.communes:
            consume_and_update_people(commune, planner, step_impacts)

    # 5) Planetary boundary update. Add baseline impacts from unmanaged waste and local pollution.
    total_pop = sum(r.population() for r in regions)
    total_waste = sum(c.stocks.get("waste", 0.0) for r in regions for c in r.communes)
    avg_local_pollution = weighted_mean(((c.environment.get("local_pollution", 0.2), c.population()) for r in regions for c in r.communes), default=0.2)
    avg_soil_gap = weighted_mean(((1.0 - c.environment.get("soil_health", 0.7), c.population()) for r in regions for c in r.communes), default=0.3)
    avg_bio_gap = weighted_mean(((1.0 - c.environment.get("biodiversity", 0.7), c.population()) for r in regions for c in r.communes), default=0.3)
    step_impacts.add_impact("pollution", 0.00000000000035 * total_waste + 0.0008 * max(0.0, avg_local_pollution - 0.55))
    step_impacts.add_impact("soil", 0.0005 * max(0.0, avg_soil_gap - 0.30))
    step_impacts.add_impact("biosphere", 0.0005 * max(0.0, avg_bio_gap - 0.30))
    # Sufficiency and climate discipline slowly lower systemic pressure.
    step_impacts.add_regen("material_throughput", 0.0020 * planner.sufficiency_norm * mean((c.average_trust() for r in regions for c in r.communes), default=0.5))
    step_impacts.add_regen("energy_throughput", 0.0030 * planner.sufficiency_norm * planner.renewable_bias)
    step_impacts.add_regen("climate", 0.0009 * planner.climate_discipline * planner.renewable_bias)

    boundary.apply_impacts(step_impacts.impacts, step_impacts.regeneration)

    metrics = collect_metrics(regions, boundary, step, step_impacts.global_transfers)
    return metrics, step_impacts.truth_vectors, step_impacts


def collect_metrics(regions: List[Region], boundary: BoundaryState, step: int, transfers: float) -> GlobalMetrics:
    communes = [c for r in regions for c in r.communes]
    total_pop = sum(c.population() for c in communes)
    # Wellbeing from satisfaction, health, autonomy, trust, and ecological safety.
    wellbeing_items = []
    unmet_items = []
    basic_buffer_items = []
    resilience_items = []
    for c in communes:
        sat = c.last_satisfaction or {d: 0.8 for d in ("water", "food", "energy", "shelter", "health", "care", "education", "mobility", "governance", "knowledge", "resilience")}
        basic_sat = 0.30 * sat.get("water", 1.0) + 0.30 * sat.get("food", 1.0) + 0.18 * sat.get("shelter", 1.0) + 0.12 * sat.get("energy", 1.0) + 0.10 * sat.get("health", 1.0)
        civic_sat = 0.36 * sat.get("governance", 1.0) + 0.34 * sat.get("knowledge", 1.0) + 0.30 * sat.get("resilience", 1.0)
        freedom = 0.55 * c.average_autonomy() + 0.45 * c.average_trust()
        ecological_safety = boundary.penalty()
        wellbeing = clamp(0.50 * basic_sat + 0.17 * freedom + 0.11 * c.average_health() + 0.10 * civic_sat + 0.12 * ecological_safety)
        wellbeing_items.append((wellbeing, c.population()))
        unmet_basic = 1.0 - clamp(0.35 * sat.get("water", 1.0) + 0.35 * sat.get("food", 1.0) + 0.15 * sat.get("shelter", 1.0) + 0.15 * sat.get("health", 1.0))
        unmet_items.append((unmet_basic, c.population()))
        basic_need = max(1.0, c.need("water") + c.need("food") + c.need("energy"))
        basic_stock = c.stocks.get("water", 0.0) + c.stocks.get("food", 0.0) + c.stocks.get("energy", 0.0)
        basic_buffer_items.append((safe_div(basic_stock, basic_need, 0.0), c.population()))
        resilience = clamp(0.40 * sat_ratio(c.capacities.get("resilience", 0.0), max(1.0, c.need("resilience"))) +
                           0.25 * sat_ratio(c.capacities.get("storage", 0.0), max(1.0, c.need("storage"))) +
                           0.20 * sat_ratio(basic_stock, 1.20 * basic_need) +
                           0.15 * boundary.penalty())
        resilience_items.append((resilience, c.population()))
    worst_name, worst_pressure = boundary.worst()
    waste_stock = sum(c.stocks.get("waste", 0.0) for c in communes)
    repair_materials = sum(c.stocks.get("repair_materials", 0.0) for c in communes)
    food_stock = sum(c.stocks.get("food", 0.0) for c in communes)
    water_stock = sum(c.stocks.get("water", 0.0) for c in communes)
    energy_stock = sum(c.stocks.get("energy", 0.0) for c in communes)
    contribution_time = sum(c.productive_time() for c in communes)
    macro_capacity = sum(c.capacities.get(domain, 0.0) for c in communes for domain in MACRO_CAPACITY_DOMAINS)
    avg_truth_error = weighted_mean(((c.truth_error, c.population()) for c in communes), default=0.0)
    avg_democracy = weighted_mean(((c.democratic_quality, c.population()) for c in communes), default=0.0)
    avg_trust = weighted_mean(((c.average_trust(), c.population()) for c in communes), default=0.0)
    circularity_index = clamp(repair_materials / max(1.0, repair_materials + waste_stock))
    coordination_quality = clamp(0.36 * avg_democracy + 0.34 * avg_trust + 0.30 * (1.0 - avg_truth_error))
    basic_buffer_months = weighted_mean(basic_buffer_items, default=0.0)
    resilience_index = weighted_mean(resilience_items, default=0.0)
    satisfaction_inequality = weighted_gini(wellbeing_items)
    planetary_reproduction_index = clamp(0.30 * weighted_mean(wellbeing_items, default=0.0) +
                                         0.22 * (1.0 - weighted_mean(unmet_items, default=0.0)) +
                                         0.18 * boundary.penalty() +
                                         0.12 * circularity_index +
                                         0.10 * coordination_quality +
                                         0.08 * resilience_index)
    return GlobalMetrics(
        step=step,
        population=total_pop,
        wellbeing=weighted_mean(wellbeing_items, default=0.0),
        unmet_basic=weighted_mean(unmet_items, default=0.0),
        avg_trust=avg_trust,
        avg_autonomy=weighted_mean(((c.average_autonomy(), c.population()) for c in communes), default=0.0),
        avg_health=weighted_mean(((c.average_health(), c.population()) for c in communes), default=0.0),
        avg_education=weighted_mean(((c.average_education(), c.population()) for c in communes), default=0.0),
        avg_truth_error=avg_truth_error,
        overshoot=boundary.overshoot(),
        mean_boundary_pressure=boundary.mean_pressure(),
        worst_boundary=worst_name,
        worst_boundary_pressure=worst_pressure,
        waste_stock=waste_stock,
        repair_materials=repair_materials,
        food_stock=food_stock,
        water_stock=water_stock,
        energy_stock=energy_stock,
        global_transfers=transfers,
        contribution_time=contribution_time,
        contribution_time_per_person=safe_div(contribution_time, total_pop, 0.0),
        satisfaction_inequality=satisfaction_inequality,
        resilience_index=resilience_index,
        circularity_index=circularity_index,
        coordination_quality=coordination_quality,
        basic_buffer_months=basic_buffer_months,
        macro_capacity=macro_capacity,
        planetary_reproduction_index=planetary_reproduction_index,
    )


def collect_macro_accounts(regions: List[Region], boundary: BoundaryState, step: int, step_impacts: Optional[StepImpacts] = None) -> List[MacroAccountRow]:
    """Global accounts for a planet economy.

    These rows are analogous to national accounts, sector accounts, labour accounts,
    public-goods accounts and external-sector accounts, but without money, prices,
    income, profit or GDP. The core balance is need/available/difference/effect.
    """
    communes = [c for r in regions for c in r.communes]
    rows: List[MacroAccountRow] = []
    flow_counts: Dict[str, int] = {domain: 0 for domain in DOMAINS}
    if step_impacts is not None:
        for flow in step_impacts.flows:
            flow_counts[flow.domain] = flow_counts.get(flow.domain, 0) + 1
    total_labor = sum(step_impacts.domain_labor.values()) if step_impacts is not None else 0.0
    for domain in DOMAINS:
        need = 0.0
        available = 0.0
        stock_or_capacity = 0.0
        priority_items = []
        labor_share_items = []
        truth_error_items = []
        democracy_items = []
        for c in communes:
            pop = c.population()
            if domain == "ecology":
                n = c.ecology_need()
                a = c.available_for_need(domain)
            elif domain == "waste":
                n = c.waste_need()
                a = max(0.0, c.waste_need() - c.stocks.get("waste", 0.0))
            else:
                n = c.need(domain)
                a = c.available_for_need(domain)
            need += n
            available += a
            if domain in CONSUMABLE_DOMAINS:
                stock_or_capacity += c.stocks.get(domain, 0.0)
            elif domain == "repair":
                stock_or_capacity += c.stocks.get("repair_materials", 0.0)
            elif domain == "waste":
                stock_or_capacity += c.stocks.get("waste", 0.0)
            elif domain in MACRO_CAPACITY_DOMAINS:
                stock_or_capacity += c.capacities.get(domain, 0.0)
            priority_items.append((c.last_priorities.get(domain, 0.0), pop))
            labor_share_items.append((c.last_labor_shares.get(domain, 0.0), pop))
            truth_error_items.append((c.truth_error, pop))
            democracy_items.append((c.democratic_quality, pop))
        gap = normalized_need_gap(need, available)
        satisfaction = sat_ratio(available, need)
        contribution_time = 0.0
        if step_impacts is not None:
            contribution_time = step_impacts.domain_labor.get(domain, 0.0)
        rows.append(MacroAccountRow(
            step=step,
            domain=domain,
            sector=SECTOR_FOR_DOMAIN.get(domain, "unmapped"),
            need=need,
            available=available,
            gap=gap,
            satisfaction=satisfaction,
            priority=weighted_mean(priority_items, default=0.0),
            labor_share=weighted_mean(labor_share_items, default=safe_div(contribution_time, total_labor, 0.0)),
            contribution_time=contribution_time,
            stock_or_capacity=stock_or_capacity,
            boundary_penalty=boundary.penalty(),
            truth_error=weighted_mean(truth_error_items, default=0.0),
            democratic_quality=weighted_mean(democracy_items, default=0.0),
            activated_flows=flow_counts.get(domain, 0),
        ))
    return rows


def run_simulation(seed: int, steps: int, population: float, regions_count: int, communes_per_region: int, scenario: str) -> Tuple[List[Region], BoundaryState, EffectPlanner, List[GlobalMetrics], List[TruthVector], List[MacroAccountRow], List[EffectFlow]]:
    regions, boundary, planner = create_planet(seed, population, regions_count, communes_per_region, scenario)
    timeline: List[GlobalMetrics] = []
    macro_accounts: List[MacroAccountRow] = []
    last_truth: List[TruthVector] = []
    last_flows: List[EffectFlow] = []
    # Initial metrics with no consumption history yet.
    timeline.append(collect_metrics(regions, boundary, 0, 0.0))
    macro_accounts.extend(collect_macro_accounts(regions, boundary, 0, None))
    for step in range(1, steps + 1):
        metrics, truth_vectors, step_impacts = simulate_step(regions, boundary, planner, step)
        timeline.append(metrics)
        macro_accounts.extend(collect_macro_accounts(regions, boundary, step, step_impacts))
        last_truth = truth_vectors
        last_flows = step_impacts.flows
    return regions, boundary, planner, timeline, last_truth, macro_accounts, last_flows


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def ensure_dir(path: str) -> None:
    if not path:
        return
    if not os.path.exists(path):
        os.makedirs(path)


def write_timeline(path: str, timeline: List[GlobalMetrics]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(timeline[0].as_row().keys()))
        writer.writeheader()
        for m in timeline:
            writer.writerow(m.as_row())


def write_communes(path: str, regions: List[Region]) -> None:
    fields = [
        "region", "commune", "biome", "population", "wellbeing_proxy", "avg_health", "avg_education",
        "avg_autonomy", "avg_trust", "truth_error", "democratic_quality",
        "water_stock", "food_stock", "energy_stock", "shelter_capacity", "health_capacity",
        "care_capacity", "education_capacity", "mobility_capacity", "manufacturing_capacity",
        "storage_capacity", "governance_capacity", "knowledge_capacity", "resilience_capacity",
        "repair_materials", "waste",
        "soil_health", "biodiversity", "watershed", "local_pollution", "renewable_infrastructure",
        "top_priority_domain", "top_priority", "top_labor_domain", "top_labor_share",
    ]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for r in regions:
            for c in r.communes:
                sat = c.last_satisfaction or {}
                wellbeing_proxy = clamp(0.55 * mean(sat.values(), 0.8) + 0.15 * c.average_health() + 0.15 * c.average_autonomy() + 0.15 * c.average_trust())
                top_priority = max(c.last_priorities.items(), key=lambda kv: kv[1]) if c.last_priorities else ("none", 0.0)
                top_labor = max(c.last_labor_shares.items(), key=lambda kv: kv[1]) if c.last_labor_shares else ("none", 0.0)
                row = {
                    "region": r.name,
                    "commune": c.name,
                    "biome": c.biome,
                    "population": round(c.population(), 3),
                    "wellbeing_proxy": round(wellbeing_proxy, 6),
                    "avg_health": round(c.average_health(), 6),
                    "avg_education": round(c.average_education(), 6),
                    "avg_autonomy": round(c.average_autonomy(), 6),
                    "avg_trust": round(c.average_trust(), 6),
                    "truth_error": round(c.truth_error, 6),
                    "democratic_quality": round(c.democratic_quality, 6),
                    "water_stock": round(c.stocks.get("water", 0.0), 3),
                    "food_stock": round(c.stocks.get("food", 0.0), 3),
                    "energy_stock": round(c.stocks.get("energy", 0.0), 3),
                    "shelter_capacity": round(c.capacities.get("shelter", 0.0), 3),
                    "health_capacity": round(c.capacities.get("health", 0.0), 3),
                    "care_capacity": round(c.capacities.get("care", 0.0), 3),
                    "education_capacity": round(c.capacities.get("education", 0.0), 3),
                    "mobility_capacity": round(c.capacities.get("mobility", 0.0), 3),
                    "manufacturing_capacity": round(c.capacities.get("manufacturing", 0.0), 3),
                    "storage_capacity": round(c.capacities.get("storage", 0.0), 3),
                    "governance_capacity": round(c.capacities.get("governance", 0.0), 3),
                    "knowledge_capacity": round(c.capacities.get("knowledge", 0.0), 3),
                    "resilience_capacity": round(c.capacities.get("resilience", 0.0), 3),
                    "repair_materials": round(c.stocks.get("repair_materials", 0.0), 3),
                    "waste": round(c.stocks.get("waste", 0.0), 3),
                    "soil_health": round(c.environment.get("soil_health", 0.0), 6),
                    "biodiversity": round(c.environment.get("biodiversity", 0.0), 6),
                    "watershed": round(c.environment.get("watershed", 0.0), 6),
                    "local_pollution": round(c.environment.get("local_pollution", 0.0), 6),
                    "renewable_infrastructure": round(c.environment.get("renewable_infrastructure", 0.0), 6),
                    "top_priority_domain": top_priority[0],
                    "top_priority": round(top_priority[1], 6),
                    "top_labor_domain": top_labor[0],
                    "top_labor_share": round(top_labor[1], 6),
                }
                writer.writerow(row)


def write_truth_audit(path: str, truth_vectors: List[TruthVector], step: int, limit: int = 500) -> None:
    if not truth_vectors:
        return
    ordered = sorted(truth_vectors, key=lambda tv: tv.priority(), reverse=True)[:limit]
    fields = list(ordered[0].as_row(step).keys())
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for tv in ordered:
            writer.writerow(tv.as_row(step))




def write_macro_accounts(path: str, rows: List[MacroAccountRow]) -> None:
    if not rows:
        return
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].as_row().keys()))
        writer.writeheader()
        for row in rows:
            writer.writerow(row.as_row())


def write_effect_flows(path: str, flows: List[EffectFlow], limit: int = 20000) -> None:
    if not flows:
        return
    selected = flows[:limit]
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(selected[0].as_row().keys()))
        writer.writeheader()
        for flow in selected:
            writer.writerow(flow.as_row())

def write_summary(path: str, regions: List[Region], boundary: BoundaryState, planner: EffectPlanner, timeline: List[GlobalMetrics], scenario: str, seed: int) -> None:
    first = timeline[0]
    last = timeline[-1]
    summary = {
        "model": "Planetary Effect Economy / Kommunismus 2.0 conceptual simulation",
        "scenario": scenario,
        "seed": seed,
        "steps": len(timeline) - 1,
        "regions": len(regions),
        "communes": sum(len(r.communes) for r in regions),
        "initial": first.as_row(),
        "final": last.as_row(),
        "delta": {
            "wellbeing": round(last.wellbeing - first.wellbeing, 6),
            "unmet_basic": round(last.unmet_basic - first.unmet_basic, 6),
            "overshoot": round(last.overshoot - first.overshoot, 6),
            "avg_trust": round(last.avg_trust - first.avg_trust, 6),
            "avg_autonomy": round(last.avg_autonomy - first.avg_autonomy, 6),
            "avg_truth_error": round(last.avg_truth_error - first.avg_truth_error, 6),
            "satisfaction_inequality": round(last.satisfaction_inequality - first.satisfaction_inequality, 6),
            "resilience_index": round(last.resilience_index - first.resilience_index, 6),
            "circularity_index": round(last.circularity_index - first.circularity_index, 6),
            "coordination_quality": round(last.coordination_quality - first.coordination_quality, 6),
            "planetary_reproduction_index": round(last.planetary_reproduction_index - first.planetary_reproduction_index, 6),
        },
        "planetary_boundaries_final": {k: round(v, 6) for k, v in boundary.pressures.items()},
        "planner": {
            "democratic_feedback": planner.democratic_feedback,
            "centralization": planner.centralization,
            "privacy_pressure": planner.privacy_pressure,
            "cooperation": planner.cooperation,
            "sufficiency_norm": planner.sufficiency_norm,
            "climate_discipline": planner.climate_discipline,
            "redistribution_strength": planner.redistribution_strength,
            "innovation_rate": planner.innovation_rate,
            "logistics_efficiency": planner.logistics_efficiency,
            "renewable_bias": planner.renewable_bias,
        },
        "interpretation": interpretation(first, last),
    }
    with open(path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)


def interpretation(first: GlobalMetrics, last: GlobalMetrics) -> str:
    parts = []
    if last.wellbeing > first.wellbeing + 0.02:
        parts.append("general_improvement")
    elif last.wellbeing < first.wellbeing - 0.02:
        parts.append("general_deterioration")
    else:
        parts.append("mixed_or_stable")
    if last.overshoot < first.overshoot - 0.02:
        parts.append("planetary_overshoot_reduced")
    elif last.overshoot > first.overshoot + 0.02:
        parts.append("planetary_overshoot_increased")
    else:
        parts.append("planetary_boundaries_roughly_stable")
    if last.avg_truth_error < first.avg_truth_error:
        parts.append("truth_feedback_improved")
    else:
        parts.append("truth_feedback_not_improved")
    if last.avg_autonomy < first.avg_autonomy - 0.02:
        parts.append("freedom_warning")
    return ", ".join(parts)


def write_manifest(path: str, timeline: List[GlobalMetrics], boundary: BoundaryState, scenario: str) -> None:
    first = timeline[0]
    last = timeline[-1]
    lines = []
    lines.append("# Planetenwirtschaft-Simulation: erweiterte Wirkungswirtschaft")
    lines.append("")
    lines.append("Diese Simulation modelliert keine nationale Wirtschaft mit Geld, Preisen, BIP, Löhnen, Profit, Miete oder Außenhandelswerten.")
    lines.append("Sie modelliert eine planetare Wirkungswirtschaft: Bedürfnisse, Stoffe, Potenzen, ökologische Grenzen, Zeitbeiträge, Kapazitäten, Sektoren und soziale Rückkopplung.")
    lines.append("")
    lines.append("## Kernprinzip")
    lines.append("")
    lines.append("Eine wirtschaftliche Handlung ist hier keine Kauf-/Verkauf-Transaktion, sondern eine Zustandsänderung:")
    lines.append("")
    lines.append("```text")
    lines.append("Phänomen + Kausalität + Zeit + Intensität + Existenz + Potenzen + Wirkungen")
    lines.append("+ Substanz + Materie + Differenz + Bestimmung + Winkelrichtung")
    lines.append("→ Beitrag / Annahme / Transfer → neue Wirklichkeit")
    lines.append("```")
    lines.append("")
    lines.append("## Erweiterung gegenüber der Grundversion")
    lines.append("")
    lines.append("- `manufacturing`: Grundindustrie, Werkzeuge, Ersatzteile, materielle Transformation.")
    lines.append("- `storage`: Lager, Puffer, Stromspeicher, Vorratssicherheit.")
    lines.append("- `governance`: demokratische Koordination, Konfliktlösung, Wahrheitskorrektur.")
    lines.append("- `knowledge`: Forschung, offene Pläne, technisches Lernen.")
    lines.append("- `resilience`: Katastrophenschutz, Redundanz, Schockabsorption.")
    lines.append("- `macro_accounts.csv`: planetare Makrokonten ohne Geldlogik.")
    lines.append("- `effect_flow_audit.csv`: Kauf/Verkauf/Handel als Wirkungsfluss-Audit.")
    lines.append("")
    lines.append("## Was planetar ist")
    lines.append("")
    lines.append("- Planetare Grenzen wirken auf alle Kommunen, nicht nur auf ein Land.")
    lines.append("- Regionen sind Bioregionen und Versorgungsknoten, keine Nationalstaaten.")
    lines.append("- Überschüsse werden über reale Dringlichkeit und Logistik verteilt, nicht über Kaufkraft.")
    lines.append("- Abfall ist eine ungelöste Materialdifferenz und wird in Reparatur/Stoffkreisläufe zurückgeführt.")
    lines.append("- Natur ist kein externes Rohstofflager, sondern Bedingung der Simulation.")
    lines.append("- Wahrheitswerte sind korrigierbar: Vertrauen, Demokratie und Fehlerprüfung beeinflussen die Steuerung.")
    lines.append("")
    lines.append("## Szenario")
    lines.append("")
    lines.append("`%s`" % scenario)
    lines.append("")
    lines.append("## Anfang → Ende")
    lines.append("")
    lines.append("| Kennzahl | Anfang | Ende | Veränderung |")
    lines.append("|---|---:|---:|---:|")
    lines.append("| Bevölkerung | %s | %s | %s |" % (format_big(first.population), format_big(last.population), format_big(last.population - first.population)))
    lines.append("| Wohlbefinden | %.3f | %.3f | %.3f |" % (first.wellbeing, last.wellbeing, last.wellbeing - first.wellbeing))
    lines.append("| unerfüllte Grundbedürfnisse | %.3f | %.3f | %.3f |" % (first.unmet_basic, last.unmet_basic, last.unmet_basic - first.unmet_basic))
    lines.append("| Vertrauen | %.3f | %.3f | %.3f |" % (first.avg_trust, last.avg_trust, last.avg_trust - first.avg_trust))
    lines.append("| Autonomie | %.3f | %.3f | %.3f |" % (first.avg_autonomy, last.avg_autonomy, last.avg_autonomy - first.avg_autonomy))
    lines.append("| Wahrheitsfehler | %.3f | %.3f | %.3f |" % (first.avg_truth_error, last.avg_truth_error, last.avg_truth_error - first.avg_truth_error))
    lines.append("| Versorgungsungleichheit | %.3f | %.3f | %.3f |" % (first.satisfaction_inequality, last.satisfaction_inequality, last.satisfaction_inequality - first.satisfaction_inequality))
    lines.append("| Resilienzindex | %.3f | %.3f | %.3f |" % (first.resilience_index, last.resilience_index, last.resilience_index - first.resilience_index))
    lines.append("| Zirkularitätsindex | %.3f | %.3f | %.3f |" % (first.circularity_index, last.circularity_index, last.circularity_index - first.circularity_index))
    lines.append("| Koordinationsqualität | %.3f | %.3f | %.3f |" % (first.coordination_quality, last.coordination_quality, last.coordination_quality - first.coordination_quality))
    lines.append("| planetarer Reproduktionsindex | %.3f | %.3f | %.3f |" % (first.planetary_reproduction_index, last.planetary_reproduction_index, last.planetary_reproduction_index - first.planetary_reproduction_index))
    lines.append("| planetare Überschreitung | %.3f | %.3f | %.3f |" % (first.overshoot, last.overshoot, last.overshoot - first.overshoot))
    lines.append("| mittlerer Grenzdruck | %.3f | %.3f | %.3f |" % (first.mean_boundary_pressure, last.mean_boundary_pressure, last.mean_boundary_pressure - first.mean_boundary_pressure))
    lines.append("")
    lines.append("## Endzustand planetarer Grenzen")
    lines.append("")
    for k in BOUNDARY_NAMES:
        lines.append("- `%s`: %.3f%s" % (k, boundary.pressures.get(k, 0.0), "  ⚠️ Überschreitung" if boundary.pressures.get(k, 0.0) > 1.0 else ""))
    lines.append("")
    lines.append("## Lesart")
    lines.append("")
    lines.append("Ein Wert über `1.0` bei planetaren Grenzen bedeutet Überschreitung. Ein sinkender Wahrheitsfehler bedeutet, dass Rückkopplung und demokratische Korrektur besser wurden. Sinkende Autonomie ist ein Warnsignal: Dann kippt die Wirkungswirtschaft in Kontrolle.")
    lines.append("")
    lines.append("## Wichtig")
    lines.append("")
    lines.append("Das Modell ist synthetisch und nicht kalibriert. Es ist ein Baukasten für Simulation, Spielmechanik, Systemdesign und Theorieentwicklung.")
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines) + "\n")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PyPy3-compatible planetary effect economy simulation: truth-values to action, no money/prices/GDP.",
    )
    parser.add_argument("--steps", type=int, default=120, help="simulation months, default 120")
    parser.add_argument("--seed", type=int, default=42, help="random seed, default 42")
    parser.add_argument("--population", type=float, default=8_100_000_000.0, help="synthetic total population, default 8.1e9")
    parser.add_argument("--regions", type=int, default=12, help="number of bioregions, default 12")
    parser.add_argument("--communes-per-region", type=int, default=8, help="communes per region, default 8")
    parser.add_argument("--scenario", choices=("planetary_commons", "local_democracy", "technocratic_control", "ecological_crisis", "scarcity_shock"), default="planetary_commons")
    parser.add_argument("--out", default="out_planetenwirtschaft", help="output directory")
    parser.add_argument("--quiet", action="store_true", help="do not print final summary")
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    if args.steps < 0:
        raise SystemExit("--steps must be >= 0")
    if args.population <= 0:
        raise SystemExit("--population must be > 0")
    if args.regions <= 0 or args.communes_per_region <= 0:
        raise SystemExit("--regions and --communes-per-region must be > 0")

    regions, boundary, planner, timeline, last_truth, macro_accounts, last_flows = run_simulation(
        seed=args.seed,
        steps=args.steps,
        population=args.population,
        regions_count=args.regions,
        communes_per_region=args.communes_per_region,
        scenario=args.scenario,
    )
    ensure_dir(args.out)
    write_timeline(os.path.join(args.out, "timeline.csv"), timeline)
    write_communes(os.path.join(args.out, "communes_final.csv"), regions)
    write_truth_audit(os.path.join(args.out, "truth_audit.csv"), last_truth, args.steps)
    write_macro_accounts(os.path.join(args.out, "macro_accounts.csv"), macro_accounts)
    write_effect_flows(os.path.join(args.out, "effect_flow_audit.csv"), last_flows)
    write_summary(os.path.join(args.out, "summary.json"), regions, boundary, planner, timeline, args.scenario, args.seed)
    write_manifest(os.path.join(args.out, "manifest.md"), timeline, boundary, args.scenario)

    if not args.quiet:
        first = timeline[0]
        last = timeline[-1]
        print("Planetary Effect Economy Simulation")
        print("scenario:", args.scenario)
        print("steps:", args.steps)
        print("regions:", args.regions, "communes:", args.regions * args.communes_per_region)
        print("population:", format_big(first.population), "->", format_big(last.population))
        print("wellbeing: %.4f -> %.4f (Δ %.4f)" % (first.wellbeing, last.wellbeing, last.wellbeing - first.wellbeing))
        print("unmet basic needs: %.4f -> %.4f (Δ %.4f)" % (first.unmet_basic, last.unmet_basic, last.unmet_basic - first.unmet_basic))
        print("planetary overshoot: %.4f -> %.4f (Δ %.4f)" % (first.overshoot, last.overshoot, last.overshoot - first.overshoot))
        print("truth error: %.4f -> %.4f (Δ %.4f)" % (first.avg_truth_error, last.avg_truth_error, last.avg_truth_error - first.avg_truth_error))
        print("autonomy: %.4f -> %.4f (Δ %.4f)" % (first.avg_autonomy, last.avg_autonomy, last.avg_autonomy - first.avg_autonomy))
        print("reproduction index: %.4f -> %.4f (Δ %.4f)" % (first.planetary_reproduction_index, last.planetary_reproduction_index, last.planetary_reproduction_index - first.planetary_reproduction_index))
        print("resilience index: %.4f -> %.4f (Δ %.4f)" % (first.resilience_index, last.resilience_index, last.resilience_index - first.resilience_index))
        print("coordination quality: %.4f -> %.4f (Δ %.4f)" % (first.coordination_quality, last.coordination_quality, last.coordination_quality - first.coordination_quality))
        print("satisfaction inequality: %.4f -> %.4f (Δ %.4f)" % (first.satisfaction_inequality, last.satisfaction_inequality, last.satisfaction_inequality - first.satisfaction_inequality))
        print("worst boundary:", last.worst_boundary, "= %.3f" % last.worst_boundary_pressure)
        print("outputs:", os.path.abspath(args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
