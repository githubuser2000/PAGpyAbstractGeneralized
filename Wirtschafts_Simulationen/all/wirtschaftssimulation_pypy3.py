#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Wirtschaftssimulation nach Größenordnung / Currency-by-scale simulation
======================================================================

Dieses Skript übersetzt das vorher definierte abstrakte Währungsmodell in eine
reproduzierbare, ausführbare Wirtschaftssimulation. Es nutzt ausschließlich die
Python-Standardbibliothek und ist damit für PyPy3 geeignet.

Modellierte Währungen / Ebenen:

1. Land: Zahl
2. Mehrere verbündete Länder: Winkel mit Achsen gut/böse und beliebt/unbeliebt
3. Verteidigungsorganisation: Raum statt Zahl, beliebig viele Dimensionen,
   über Volumen in Zahl umrechenbar. Menschenbezogene Dimensionen sind als
   geschützte Bindungs-/Verantwortungsrelation modelliert und nicht handelbar.
4. UN-Assets: Aktien, Derivate, Fonds, Zertifikate, Währungsmarkt
5. Planet: gestapelte Fuzzy-Wahrheitswerte von -1 bis +1
6. Sternensystem: Hierarchie, durch zwei Summen und Multiplikation zu Zahl
7. Galaxie: topologischer Monoid für unäre Operationen
8. Cluster von Galaxien: topologische Gruppe für additionsähnliche Operationen
9. Universum: For-Schleifen-Zirkulationen mit Kreislaufwirtschaftsschuld und
   Kreislaufwirtschaftsbeitrag; bei 20 Punkten ergeben 3 Durchläufe 60 Einheiten.

Beispiele:

    pypy3 wirtschaftssimulation_pypy3.py --steps 120 --seed 42
    pypy3 wirtschaftssimulation_pypy3.py --steps 200 --scenario regenerative --json-out result.json
    pypy3 wirtschaftssimulation_pypy3.py --monte-carlo 20 --steps 80 --quiet
    pypy3 wirtschaftssimulation_pypy3.py --help

Die Simulation ist ein abstraktes Spiel-/Analysemodell, kein ökonomischer Rat.
"""

from __future__ import print_function

import argparse
import csv
import json
import math
import random
import sys
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

EPS = 1.0e-9
TAN_EPS = 1.0e-5
MAX_ABS_VALUE = 1.0e12
MAX_VOLUME_LOG = 50.0


# ---------------------------------------------------------------------------
# Utility
# ---------------------------------------------------------------------------


def clamp(x: float, lo: float, hi: float) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if abs(b) < EPS:
        return default
    return a / b


def sigmoid(x: float) -> float:
    # Stable enough for the ranges used here.
    if x >= 0:
        z = math.exp(-x)
        return 1.0 / (1.0 + z)
    z = math.exp(x)
    return z / (1.0 + z)


def softsign(x: float) -> float:
    return x / (1.0 + abs(x))


def mean(values: Iterable[float], default: float = 0.0) -> float:
    vals = list(values)
    if not vals:
        return default
    return sum(vals) / float(len(vals))


def weighted_mean(pairs: Iterable[Tuple[float, float]], default: float = 0.0) -> float:
    total_w = 0.0
    total = 0.0
    for value, weight in pairs:
        if weight <= 0:
            continue
        total += value * weight
        total_w += weight
    if total_w <= EPS:
        return default
    return total / total_w


def safe_tan(theta: float) -> float:
    theta = clamp(theta, -math.pi / 2.0 + TAN_EPS, math.pi / 2.0 - TAN_EPS)
    return math.tan(theta)


def safe_cotan(theta: float) -> float:
    t = safe_tan(theta)
    if abs(t) < EPS:
        return 1.0 / EPS if theta >= 0 else -1.0 / EPS
    return 1.0 / t


def rand_name(rng: random.Random, prefix: str, index: int) -> str:
    stems = [
        "Aster", "Boreal", "Cygn", "Dara", "Eon", "Faro", "Gaia", "Helio",
        "Iris", "Juno", "Kappa", "Lumen", "Meridian", "Nadir", "Orion",
        "Pax", "Quanta", "Rho", "Sol", "Torus", "Umbra", "Vega", "Warden",
        "Xeno", "Yara", "Zenit",
    ]
    suffixes = ["-I", "-II", "-Nord", "-Süd", "-Ring", "-Kern", "-Delta", "-Prime"]
    return "%s-%s%s" % (prefix, rng.choice(stems), rng.choice(suffixes)) if index < 1000 else "%s-%d" % (prefix, index)


def round_float(x: Any, ndigits: int = 6) -> Any:
    if isinstance(x, float):
        if math.isnan(x) or math.isinf(x):
            return str(x)
        return round(x, ndigits)
    return x


def recursively_round(obj: Any, ndigits: int = 6) -> Any:
    if isinstance(obj, dict):
        return {k: recursively_round(v, ndigits) for k, v in obj.items()}
    if isinstance(obj, list):
        return [recursively_round(v, ndigits) for v in obj]
    if isinstance(obj, tuple):
        return [recursively_round(v, ndigits) for v in obj]
    return round_float(obj, ndigits)


def fmt_num(x: float, width: int = 12, precision: int = 2) -> str:
    """Compact numeric formatting for terminal reports."""
    try:
        ax = abs(float(x))
    except Exception:
        return str(x).rjust(width)
    if ax >= 1.0e7 or (0.0 < ax < 1.0e-3):
        return ("%*.3e" % (width, x))
    return ("%*.*f" % (width, precision, x))


# ---------------------------------------------------------------------------
# Events and metrics
# ---------------------------------------------------------------------------


@dataclass
class Event:
    step: int
    kind: str
    target: str
    intensity: float
    description: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step,
            "kind": self.kind,
            "target": self.target,
            "intensity": self.intensity,
            "description": self.description,
        }


@dataclass
class Metrics:
    step: int
    total_country_number: float
    avg_country_number: float
    avg_inflation: float
    avg_government_goodness: float
    avg_popularity: float
    avg_alliance_angle_value: float
    avg_alliance_tan_value: float
    defense_volume_number: float
    protected_human_agency_links: float
    un_asset_value: float
    avg_truth_mean: float
    stacked_truth_number: float
    hierarchy_number: float
    cluster_number: float
    universe_units: int
    circular_debt: float
    circular_contribution: float
    universe_stacked_value: float
    systemic_risk: float

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round(self.__dict__)


# ---------------------------------------------------------------------------
# Currency: country number
# ---------------------------------------------------------------------------


@dataclass
class CountryNumberCurrency:
    """Land-Währung: einfache Zahl mit Inflations- und Schuldenkontext."""

    unit_name: str
    value: float
    inflation: float = 0.02
    debt: float = 0.0

    def mint(self, amount: float, reason: str = "") -> None:
        self.value = clamp(self.value + amount, -MAX_ABS_VALUE, MAX_ABS_VALUE)
        # Inflation reacts to aggressive minting. Negative amounts are handled by burn.
        if amount > 0:
            self.inflation = clamp(self.inflation + math.log1p(amount / (abs(self.value) + 1.0)) * 0.02, -0.10, 1.50)

    def burn(self, amount: float) -> None:
        self.value = clamp(self.value - amount, -MAX_ABS_VALUE, MAX_ABS_VALUE)
        if amount > 0:
            self.inflation = clamp(self.inflation - math.log1p(amount / (abs(self.value) + 1.0)) * 0.01, -0.20, 1.50)

    def debt_service(self) -> float:
        real_rate = 0.015 + max(0.0, self.inflation) * 0.05
        return max(0.0, self.debt * real_rate)

    def purchasing_power(self) -> float:
        return self.value / (1.0 + max(-0.95, self.inflation))

    def stress(self) -> float:
        debt_ratio = safe_div(self.debt, abs(self.value) + 1.0)
        return clamp(0.5 * softsign(debt_ratio) + 0.5 * softsign(self.inflation * 3.0), -1.0, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "unit_name": self.unit_name,
            "value": self.value,
            "inflation": self.inflation,
            "debt": self.debt,
            "purchasing_power": self.purchasing_power(),
        })


# ---------------------------------------------------------------------------
# Currency: allied countries angle
# ---------------------------------------------------------------------------


@dataclass
class AlliedAngleCurrency:
    """
    Winkel-Währung für mehrere verbündete Länder.

    Zwei unscharfe Achsen:
      - government_axis: gut (+1) vs böse (-1), von Regierungen bestimmt
      - population_axis: beliebt (+1) vs unbeliebt (-1), von Bevölkerung bestimmt

    Die Währung selbst ist der Winkel. Zur Zahl wird sie über tan/cotan.
    Der Halbkreisumfang pi*r wird als Intensitätsmaß genutzt.
    """

    government_axis: float = 0.0
    population_axis: float = 0.0
    radius: float = 1.0
    mode: str = "tan"  # tan or cotan

    def update_from_axes(self, government_axis: float, population_axis: float) -> None:
        self.government_axis = clamp(government_axis, -1.0, 1.0)
        self.population_axis = clamp(population_axis, -1.0, 1.0)
        self.radius = clamp(math.sqrt(self.government_axis ** 2 + self.population_axis ** 2), 0.0, math.sqrt(2.0))

    @property
    def raw_angle(self) -> float:
        # Geometric angle of the two-axis vector.
        return math.atan2(self.population_axis, self.government_axis + EPS)

    @property
    def folded_angle(self) -> float:
        # Fold into the open interval needed by tan/cotan.
        polarity = clamp((self.government_axis + self.population_axis) / 2.0, -1.0, 1.0)
        return polarity * (math.pi / 2.0 - TAN_EPS)

    @property
    def semicircle_circumference(self) -> float:
        return math.pi * self.radius

    def tan_number(self) -> float:
        return self.semicircle_circumference * safe_tan(self.folded_angle)

    def cotan_number(self) -> float:
        return self.semicircle_circumference * safe_cotan(self.folded_angle)

    def to_number(self) -> float:
        if self.mode == "cotan":
            return self.cotan_number()
        return self.tan_number()

    def invert_plus_minus(self) -> None:
        self.government_axis *= -1.0
        self.population_axis *= -1.0
        self.update_from_axes(self.government_axis, self.population_axis)

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "government_axis": self.government_axis,
            "population_axis": self.population_axis,
            "radius": self.radius,
            "raw_angle": self.raw_angle,
            "folded_angle": self.folded_angle,
            "semicircle_circumference": self.semicircle_circumference,
            "tan_number": self.tan_number(),
            "cotan_number": self.cotan_number(),
            "mode": self.mode,
            "number": self.to_number(),
        })


# ---------------------------------------------------------------------------
# Currency: defense organization space
# ---------------------------------------------------------------------------


@dataclass
class DefenseSpaceCurrency:
    """
    Raum-statt-Zahl-Währung.

    - beliebig viele Dimensionen
    - Volumen -> Zahl
    - Besitz statt Eigentum
    - menschenbezogene Dimensionen sind nicht handelbar, sondern als geschützte
      Agency-/Verantwortungslinks modelliert
    """

    dimensions: Dict[str, float] = field(default_factory=dict)
    protected_dimensions: List[str] = field(default_factory=lambda: ["protected_human_agency_links"])
    orientation: float = 1.0

    def ensure_dimension(self, name: str, initial: float = 0.0, protected: bool = False) -> None:
        if name not in self.dimensions:
            self.dimensions[name] = initial
        if protected and name not in self.protected_dimensions:
            self.protected_dimensions.append(name)

    def add(self, name: str, amount: float) -> None:
        self.ensure_dimension(name, 0.0)
        self.dimensions[name] = clamp(self.dimensions[name] + amount, -1.0e6, 1.0e6)

    def scale(self, factor: float, include_protected: bool = False) -> None:
        for key in list(self.dimensions.keys()):
            if key in self.protected_dimensions and not include_protected:
                continue
            self.dimensions[key] = clamp(self.dimensions[key] * factor, -1.0e6, 1.0e6)

    def transferable_dimensions(self) -> Dict[str, float]:
        return {k: v for k, v in self.dimensions.items() if k not in self.protected_dimensions}

    def protected_human_agency(self) -> float:
        return sum(max(0.0, self.dimensions.get(k, 0.0)) for k in self.protected_dimensions)

    def volume_number(self) -> float:
        # Hyper-rectangular soft volume. Uses log to avoid overflow.
        log_sum = 0.0
        for val in self.dimensions.values():
            log_sum += math.log1p(abs(val))
        log_sum = clamp(log_sum, 0.0, MAX_VOLUME_LOG)
        return self.orientation * (math.exp(log_sum) - 1.0)

    def invert_orientation(self) -> None:
        self.orientation *= -1.0

    def social_legitimacy_penalty(self) -> float:
        # Human-related links are protected, not owned/traded. A high value means
        # large stewardship burden and social scrutiny, not asset power.
        return softsign(self.protected_human_agency() / 1000.0)

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "dimensions": self.dimensions,
            "protected_dimensions": self.protected_dimensions,
            "orientation": self.orientation,
            "volume_number": self.volume_number(),
            "protected_human_agency_links": self.protected_human_agency(),
            "social_legitimacy_penalty": self.social_legitimacy_penalty(),
        })


# ---------------------------------------------------------------------------
# Currency: UN assets
# ---------------------------------------------------------------------------


@dataclass
class AssetPosition:
    asset_class: str
    name: str
    units: float
    price: float
    volatility: float
    leverage: float = 1.0
    currency_unit: str = "UNU"

    def value(self) -> float:
        return self.units * self.price * self.leverage

    def update_price(self, rng: random.Random, growth_signal: float, truth_signal: float, systemic_risk: float) -> None:
        # Derivatives amplify both signal and noise. Truth lowers volatility; lies raise it.
        truth_vol_modifier = 1.0 + max(0.0, -truth_signal) * 1.5
        risk_modifier = 1.0 + systemic_risk * 0.8
        noise = rng.gauss(0.0, self.volatility * truth_vol_modifier * risk_modifier)
        drift_by_class = {
            "stock": 0.004,
            "derivative": 0.000,
            "fund": 0.002,
            "certificate": 0.001,
            "forex": 0.000,
        }.get(self.asset_class, 0.0)
        leverage_noise = noise * max(1.0, abs(self.leverage))
        delta = drift_by_class + growth_signal * 0.01 + leverage_noise
        if self.asset_class == "derivative":
            delta += systemic_risk * rng.choice([-1.0, 1.0]) * 0.04
        if self.asset_class == "forex":
            delta += rng.gauss(0.0, 0.01 + systemic_risk * 0.02)
        self.price = clamp(self.price * math.exp(clamp(delta, -1.5, 1.5)), 0.0001, 1.0e9)

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "asset_class": self.asset_class,
            "name": self.name,
            "units": self.units,
            "price": self.price,
            "volatility": self.volatility,
            "leverage": self.leverage,
            "currency_unit": self.currency_unit,
            "value": self.value(),
        })


@dataclass
class UNAssetCurrency:
    """UN-Asset-Ebene: Portfolio aus Aktien, Derivaten, Fonds, Zertifikaten, Währungen."""

    positions: List[AssetPosition] = field(default_factory=list)
    unit: str = "UNU"

    def total_value(self) -> float:
        return sum(pos.value() for pos in self.positions)

    def class_values(self) -> Dict[str, float]:
        out: Dict[str, float] = {}
        for pos in self.positions:
            out[pos.asset_class] = out.get(pos.asset_class, 0.0) + pos.value()
        return out

    def update_market(self, rng: random.Random, growth_signal: float, truth_signal: float, systemic_risk: float) -> None:
        for pos in self.positions:
            pos.update_price(rng, growth_signal, truth_signal, systemic_risk)

    def shock(self, rng: random.Random, intensity: float) -> None:
        for pos in self.positions:
            sensitivity = 1.0 + (abs(pos.leverage) - 1.0) * 0.3
            pos.price = clamp(pos.price * math.exp(-abs(intensity) * sensitivity * rng.uniform(0.4, 1.2)), 0.0001, 1.0e9)

    def merge_additive(self, other: "UNAssetCurrency") -> None:
        # Additive group-like operation: same named positions get unit addition.
        by_name: Dict[str, AssetPosition] = {p.name: p for p in self.positions}
        for op in other.positions:
            if op.name in by_name:
                by_name[op.name].units += op.units
            else:
                self.positions.append(AssetPosition(
                    op.asset_class, op.name, op.units, op.price, op.volatility, op.leverage, op.currency_unit
                ))

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "unit": self.unit,
            "total_value": self.total_value(),
            "class_values": self.class_values(),
            "positions": [p.to_dict() for p in self.positions],
        })


# ---------------------------------------------------------------------------
# Currency: fuzzy truth stack
# ---------------------------------------------------------------------------


@dataclass
class FuzzyTruthStackCurrency:
    """Planet-Währung: gestapelte Fuzzy-Wahrheitswerte von -1 bis +1."""

    values: List[float] = field(default_factory=list)
    max_stack: int = 200

    def add(self, value: float) -> None:
        self.values.append(clamp(value, -1.0, 1.0))
        if len(self.values) > self.max_stack:
            self.values = self.values[-self.max_stack:]

    def extend(self, values: Iterable[float]) -> None:
        for v in values:
            self.add(v)

    def number(self) -> float:
        return sum(self.values)

    def mean(self) -> float:
        return mean(self.values, 0.0)

    def lie_debt(self) -> float:
        return sum(max(0.0, -v) for v in self.values)

    def truth_capital(self) -> float:
        return sum(max(0.0, v) for v in self.values)

    def invert_truth_lie(self) -> None:
        self.values = [-v for v in self.values]

    def noise(self, rng: random.Random, magnitude: float) -> None:
        self.values = [clamp(v + rng.gauss(0.0, magnitude), -1.0, 1.0) for v in self.values]

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "count": len(self.values),
            "number": self.number(),
            "mean": self.mean(),
            "truth_capital": self.truth_capital(),
            "lie_debt": self.lie_debt(),
            "tail": self.values[-12:],
        })


# ---------------------------------------------------------------------------
# Currency: hierarchy in a star system
# ---------------------------------------------------------------------------


@dataclass
class HierarchyCurrency:
    """
    Sternensystem-Währung: Hierarchie, wandelbar in Zahl durch zwei Summen und
    Multiplikation.

    tiers[0] ist Spitze/Koordination, tiers[1:] sind untere Ebenen.
    number = (sum_top + sum_lower) * product(1 + |tier_sum|/(tier_size+depth+1))
    """

    tiers: List[List[float]] = field(default_factory=list)
    labels: List[str] = field(default_factory=list)

    def two_sums(self) -> Tuple[float, float]:
        if not self.tiers:
            return 0.0, 0.0
        top = sum(self.tiers[0])
        lower = sum(sum(t) for t in self.tiers[1:])
        return top, lower

    def multiplicative_factor(self) -> float:
        factor = 1.0
        for depth, tier in enumerate(self.tiers):
            if not tier:
                continue
            tier_sum = sum(tier)
            tier_size = float(len(tier))
            factor *= 1.0 + abs(tier_sum) / (tier_size + depth + 1.0) * 0.01
            factor = clamp(factor, 0.0, 1.0e6)
        return factor

    def to_number(self) -> float:
        a, b = self.two_sums()
        return clamp((a + b) * self.multiplicative_factor(), -MAX_ABS_VALUE, MAX_ABS_VALUE)

    def concatenate(self, other: "HierarchyCurrency") -> None:
        max_len = max(len(self.tiers), len(other.tiers))
        while len(self.tiers) < max_len:
            self.tiers.append([])
        while len(self.labels) < max_len:
            self.labels.append("tier-%d" % len(self.labels))
        for i in range(max_len):
            if i < len(other.tiers):
                self.tiers[i].extend(other.tiers[i])

    def twist(self, rng: random.Random, intensity: float = 1.0) -> None:
        if not self.tiers:
            return
        tier_index = rng.randrange(0, len(self.tiers))
        tier = self.tiers[tier_index]
        if not tier:
            return
        rng.shuffle(tier)
        # "Verdrehen" can invert some signs. For humans this is interpreted as
        # role/order inversion, not as ownership transfer.
        flips = max(1, int(len(tier) * clamp(intensity, 0.0, 1.0) * 0.25))
        for _ in range(flips):
            j = rng.randrange(0, len(tier))
            tier[j] = clamp(-tier[j], -1.0e6, 1.0e6)

    def normalize(self) -> None:
        for i, tier in enumerate(self.tiers):
            if not tier:
                continue
            m = mean(abs(x) for x in tier)
            if m > EPS:
                self.tiers[i] = [x / (1.0 + m * 0.001) for x in tier]

    def to_dict(self) -> Dict[str, Any]:
        top, lower = self.two_sums()
        return recursively_round({
            "labels": self.labels,
            "tier_sizes": [len(t) for t in self.tiers],
            "two_sums": {"top": top, "lower": lower},
            "multiplicative_factor": self.multiplicative_factor(),
            "number": self.to_number(),
            "tiers_preview": [tier[:8] for tier in self.tiers[:5]],
        })


# ---------------------------------------------------------------------------
# Currency: galaxy monoid for unary operations
# ---------------------------------------------------------------------------


@dataclass
class MonoidOperation:
    name: str
    target_type: str
    intensity: float

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({"name": self.name, "target_type": self.target_type, "intensity": self.intensity})


@dataclass
class GalaxyMonoidCurrency:
    """
    Galaxie-Währung: topologischer Monoid von unären Operationen.

    Monoid-Struktur:
      - identity = keine Operation
      - compose = Operationenliste hintereinander
      - apply = Anwendung auf Währungen kleinerer Größenordnung
    """

    operations: List[MonoidOperation] = field(default_factory=list)

    def identity(self) -> None:
        self.operations = []

    def compose(self, op: MonoidOperation) -> None:
        self.operations.append(op)

    def apply(self, world: "World", step: int) -> List[Event]:
        events: List[Event] = []
        for op in self.operations:
            if op.name == "invert_country_number" and world.countries:
                c = world.rng.choice(world.countries)
                c.currency.value = clamp(-c.currency.value * clamp(op.intensity, 0.1, 2.0), -MAX_ABS_VALUE, MAX_ABS_VALUE)
                events.append(Event(step, "galaxy_monoid", c.name, op.intensity,
                                    "Zahlenpolarität einer Landeswährung wurde invertiert."))
            elif op.name == "invert_angle" and world.alliances:
                a = world.rng.choice(world.alliances)
                a.currency.invert_plus_minus()
                events.append(Event(step, "galaxy_monoid", a.name, op.intensity,
                                    "Winkelwährung wurde plus/minus invertiert."))
            elif op.name == "invert_truth" and world.planets:
                p = world.rng.choice(world.planets)
                p.truth_currency.invert_truth_lie()
                events.append(Event(step, "galaxy_monoid", p.name, op.intensity,
                                    "Wahrheitsstapel wurde Wahrheit/Lüge invertiert."))
            elif op.name == "twist_hierarchy":
                world.star_system.hierarchy.twist(world.rng, op.intensity)
                events.append(Event(step, "galaxy_monoid", world.star_system.name, op.intensity,
                                    "Hierarchieteile wurden verdreht."))
            elif op.name == "invert_space_orientation" and world.defense_orgs:
                d = world.rng.choice(world.defense_orgs)
                d.space_currency.invert_orientation()
                events.append(Event(step, "galaxy_monoid", d.name, op.intensity,
                                    "Raumorientierung wurde positiv/negativ invertiert."))
        self.identity()
        return events

    def to_dict(self) -> Dict[str, Any]:
        return {"pending_operations": [op.to_dict() for op in self.operations]}


# ---------------------------------------------------------------------------
# Currency: cluster group for additive operations
# ---------------------------------------------------------------------------


@dataclass
class ClusterGroupCurrency:
    """
    Cluster-von-Galaxien-Währung: topologische Gruppe additionsähnlicher
    Rechnungen. Sie kann kleinere Währungen additiv bündeln, subtrahieren oder
    konkatenieren.
    """

    aggregate_number: float = 0.0
    aggregate_space_volume: float = 0.0
    aggregate_truth_number: float = 0.0
    aggregate_hierarchy_number: float = 0.0
    aggregate_asset_value: float = 0.0
    concatenation_count: int = 0

    def recompute(self, world: "World") -> None:
        self.aggregate_number = sum(c.currency.value for c in world.countries)
        self.aggregate_space_volume = sum(d.space_currency.volume_number() for d in world.defense_orgs)
        self.aggregate_truth_number = sum(p.truth_currency.number() for p in world.planets)
        self.aggregate_hierarchy_number = world.star_system.hierarchy.to_number()
        self.aggregate_asset_value = world.un_assets.total_value()
        self.concatenation_count = sum(len(t) for t in world.star_system.hierarchy.tiers)

    def group_number(self) -> float:
        # Additionsähnliche Rechnung: all lower currencies are added with scale
        # normalization. This preserves the spirit of a group operation without
        # pretending all units are physically identical.
        return (
            self.aggregate_number
            + softsign(self.aggregate_space_volume) * 100000.0
            + self.aggregate_truth_number * 1000.0
            + self.aggregate_hierarchy_number
            + self.aggregate_asset_value * 0.1
        )

    def inverse_number(self) -> float:
        return -self.group_number()

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "aggregate_number": self.aggregate_number,
            "aggregate_space_volume": self.aggregate_space_volume,
            "aggregate_truth_number": self.aggregate_truth_number,
            "aggregate_hierarchy_number": self.aggregate_hierarchy_number,
            "aggregate_asset_value": self.aggregate_asset_value,
            "concatenation_count": self.concatenation_count,
            "group_number": self.group_number(),
            "inverse_number": self.inverse_number(),
        })


# ---------------------------------------------------------------------------
# Currency: universe for-loop circular economy
# ---------------------------------------------------------------------------


@dataclass
class UniverseLoopCurrency:
    """
    Universums-Währung: For-Schleifen-Zirkulationen.

    Bei loop_length=20 gilt:
      loop_runs=3, loop_point=0 -> 60 Währungseinheiten.

    stacked_value verbindet diese Einheiten mit Kreislaufwirtschaftsbeitrag
    minus Kreislaufwirtschaftsschuld.
    """

    loop_length: int = 20
    loop_runs: int = 0
    loop_point: int = 0
    circular_debt: Dict[str, float] = field(default_factory=lambda: {
        "compost_debt": 0.0,
        "waste_debt": 0.0,
        "repair_debt": 0.0,
        "energy_debt": 0.0,
        "social_debt": 0.0,
    })
    circular_contribution: Dict[str, float] = field(default_factory=lambda: {
        "compost": 0.0,
        "reuse": 0.0,
        "repair": 0.0,
        "recycling": 0.0,
        "regeneration": 0.0,
    })

    def currency_units(self) -> int:
        return self.loop_runs * self.loop_length + self.loop_point

    def total_debt(self) -> float:
        return sum(max(0.0, v) for v in self.circular_debt.values())

    def total_contribution(self) -> float:
        return sum(max(0.0, v) for v in self.circular_contribution.values())

    def stacked_value(self) -> float:
        return float(self.currency_units()) + self.total_contribution() - self.total_debt()

    def tick(self, debt_delta: Dict[str, float], contribution_delta: Dict[str, float]) -> None:
        for k, v in debt_delta.items():
            self.circular_debt[k] = max(0.0, self.circular_debt.get(k, 0.0) + v)
        for k, v in contribution_delta.items():
            self.circular_contribution[k] = max(0.0, self.circular_contribution.get(k, 0.0) + v)
        self.loop_point += 1
        if self.loop_point >= self.loop_length:
            self.loop_point = 0
            self.loop_runs += 1

    def decay(self, rate: float) -> None:
        # Closed loops amortize debt and also consume contribution.
        for k in list(self.circular_debt.keys()):
            self.circular_debt[k] *= (1.0 - rate)
        for k in list(self.circular_contribution.keys()):
            self.circular_contribution[k] *= (1.0 - rate * 0.25)

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "loop_length": self.loop_length,
            "loop_runs": self.loop_runs,
            "loop_point": self.loop_point,
            "currency_units": self.currency_units(),
            "circular_debt": self.circular_debt,
            "circular_contribution": self.circular_contribution,
            "total_debt": self.total_debt(),
            "total_contribution": self.total_contribution(),
            "stacked_value": self.stacked_value(),
        })


# ---------------------------------------------------------------------------
# Economic entities
# ---------------------------------------------------------------------------


@dataclass
class Country:
    name: str
    currency: CountryNumberCurrency
    population: float
    productivity: float
    resource_stock: float
    government_goodness: float
    popularity: float
    circular_policy: float
    defense_preference: float
    market_regulation: float
    environmental_damage: float = 0.0
    last_output: float = 0.0
    trade_balance: float = 0.0
    alliance_name: Optional[str] = None

    def governance_signal(self) -> float:
        return clamp(0.6 * self.government_goodness + 0.4 * self.popularity, -1.0, 1.0)

    def step(
        self,
        rng: random.Random,
        truth_signal: float,
        alliance_signal: float,
        defense_security: float,
        market_signal: float,
        circular_pressure: float,
    ) -> Tuple[float, Dict[str, float], Dict[str, float]]:
        # Production depends on trust, truth, alliance angle, security, resources,
        # market mood and ecological pressure.
        resource_factor = clamp(self.resource_stock / 1000.0, 0.15, 2.0)
        legitimacy = self.governance_signal()
        inflation_drag = max(0.0, self.currency.inflation) * 0.10
        ecological_drag = self.environmental_damage * 0.08 + circular_pressure * 0.04
        shock_noise = rng.gauss(0.0, 0.025)
        multiplier = (
            1.0
            + legitimacy * 0.08
            + truth_signal * 0.06
            + softsign(alliance_signal / 100.0) * 0.05
            + defense_security * self.defense_preference * 0.03
            + market_signal * 0.04
            - inflation_drag
            - ecological_drag
            + shock_noise
        )
        multiplier = clamp(multiplier, 0.25, 1.75)
        base_output = self.population * self.productivity * 0.001
        output = max(0.0, base_output * resource_factor * multiplier)
        self.last_output = output

        # Treasury / currency update.
        tax_take = output * (0.16 + self.market_regulation * 0.08)
        debt_service = self.currency.debt_service()
        green_investment = output * max(0.0, self.circular_policy) * 0.05
        defense_cost = output * self.defense_preference * 0.03
        fiscal_delta = tax_take - debt_service - green_investment - defense_cost + self.trade_balance
        if fiscal_delta >= 0:
            self.currency.mint(fiscal_delta, "productive surplus")
        else:
            self.currency.debt += abs(fiscal_delta) * 0.6
            self.currency.burn(abs(fiscal_delta) * 0.2)

        # Inflation mean reversion and volatility.
        self.currency.inflation = clamp(
            self.currency.inflation * 0.985 + rng.gauss(0.0, 0.003) + max(0.0, -truth_signal) * 0.002,
            -0.20,
            1.50,
        )

        # Resources and circular economy.
        extraction = output * (0.20 - self.circular_policy * 0.08)
        extraction = max(0.01, extraction)
        self.resource_stock = max(1.0, self.resource_stock - extraction + green_investment * 0.05)
        waste = output * (0.12 - self.circular_policy * 0.06)
        waste = max(0.0, waste)
        compost = output * max(0.0, self.circular_policy) * 0.03
        repair = output * max(0.0, self.circular_policy) * 0.02
        regeneration = green_investment * 0.04
        self.environmental_damage = clamp(
            self.environmental_damage + waste * 0.0003 - regeneration * 0.0004 - compost * 0.0001,
            0.0,
            10.0,
        )

        debt_delta = {
            "compost_debt": max(0.0, waste * 0.02 - compost * 0.03),
            "waste_debt": max(0.0, waste * 0.04),
            "repair_debt": max(0.0, output * 0.01 - repair * 0.02),
            "energy_debt": max(0.0, extraction * 0.03),
            "social_debt": max(0.0, (1.0 - self.popularity) * output * 0.002),
        }
        contribution_delta = {
            "compost": compost,
            "reuse": output * max(0.0, self.circular_policy) * 0.015,
            "repair": repair,
            "recycling": output * max(0.0, self.circular_policy) * 0.025,
            "regeneration": regeneration,
        }

        # Government/popularity feedback.
        prosperity_signal = softsign(output / (base_output + EPS) - 1.0)
        debt_stress = self.currency.stress()
        self.popularity = clamp(
            self.popularity
            + prosperity_signal * 0.025
            + truth_signal * 0.010
            - debt_stress * 0.020
            - self.environmental_damage * 0.004
            + rng.gauss(0.0, 0.015),
            -1.0,
            1.0,
        )
        self.government_goodness = clamp(
            self.government_goodness
            + self.circular_policy * 0.004
            + self.market_regulation * 0.002
            + truth_signal * 0.006
            - max(0.0, -self.popularity) * 0.006
            + rng.gauss(0.0, 0.010),
            -1.0,
            1.0,
        )
        return output, debt_delta, contribution_delta

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "name": self.name,
            "currency": self.currency.to_dict(),
            "population": self.population,
            "productivity": self.productivity,
            "resource_stock": self.resource_stock,
            "government_goodness": self.government_goodness,
            "popularity": self.popularity,
            "circular_policy": self.circular_policy,
            "defense_preference": self.defense_preference,
            "market_regulation": self.market_regulation,
            "environmental_damage": self.environmental_damage,
            "last_output": self.last_output,
            "trade_balance": self.trade_balance,
            "alliance_name": self.alliance_name,
        })


@dataclass
class Alliance:
    name: str
    member_names: List[str]
    currency: AlliedAngleCurrency = field(default_factory=AlliedAngleCurrency)
    cohesion: float = 0.5
    trade_corridor: float = 1.0

    def update(self, countries_by_name: Dict[str, Country]) -> None:
        members = [countries_by_name[n] for n in self.member_names if n in countries_by_name]
        if not members:
            self.currency.update_from_axes(0.0, 0.0)
            return
        gov = weighted_mean(((c.government_goodness, c.population) for c in members), 0.0)
        pop = weighted_mean(((c.popularity, c.population) for c in members), 0.0)
        # Cohesion suppresses extreme disagreement.
        disagreement = mean((abs(c.government_goodness - gov) + abs(c.popularity - pop) for c in members), 0.0)
        self.cohesion = clamp(self.cohesion + 0.015 * (1.0 - disagreement) - 0.005 * disagreement, 0.0, 1.0)
        self.trade_corridor = clamp(1.0 + self.cohesion + softsign(gov + pop), 0.1, 3.0)
        self.currency.update_from_axes(gov * (0.5 + self.cohesion * 0.5), pop * (0.5 + self.cohesion * 0.5))

    def numeric_trade_signal(self) -> float:
        return self.currency.to_number() * self.trade_corridor

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "name": self.name,
            "member_names": self.member_names,
            "currency": self.currency.to_dict(),
            "cohesion": self.cohesion,
            "trade_corridor": self.trade_corridor,
            "numeric_trade_signal": self.numeric_trade_signal(),
        })


@dataclass
class DefenseOrganization:
    name: str
    protected_country_names: List[str]
    space_currency: DefenseSpaceCurrency
    readiness: float = 0.5

    def update(self, rng: random.Random, countries_by_name: Dict[str, Country], threat_signal: float) -> None:
        members = [countries_by_name[n] for n in self.protected_country_names if n in countries_by_name]
        budget = sum(max(0.0, c.last_output) * c.defense_preference * 0.04 for c in members)
        legitimacy = mean((c.governance_signal() for c in members), 0.0)
        self.space_currency.add("logistics", budget * rng.uniform(0.02, 0.08))
        self.space_currency.add("territory", budget * rng.uniform(0.005, 0.025))
        self.space_currency.add("cyber", budget * rng.uniform(0.01, 0.06))
        self.space_currency.add("time", budget * rng.uniform(0.01, 0.04))
        self.space_currency.add("attention", budget * rng.uniform(0.01, 0.05))
        # Protected, non-tradeable stewardship pressure. It can rise under threat,
        # but it is never sold/transferred in the model.
        self.space_currency.add("protected_human_agency_links", max(0.0, threat_signal) * len(members) * rng.uniform(0.1, 0.7))
        penalty = self.space_currency.social_legitimacy_penalty()
        self.readiness = clamp(
            self.readiness + softsign(budget / 1000.0) * 0.03 + threat_signal * 0.02 + legitimacy * 0.01 - penalty * 0.02,
            0.0,
            1.0,
        )
        # Expensive organizations slowly decay if not maintained.
        self.space_currency.scale(0.995, include_protected=False)

    def security_signal(self) -> float:
        vol = self.space_currency.volume_number()
        return clamp(self.readiness * 0.5 + softsign(vol / 100000.0) * 0.5, -1.0, 1.0)

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "name": self.name,
            "protected_country_names": self.protected_country_names,
            "space_currency": self.space_currency.to_dict(),
            "readiness": self.readiness,
            "security_signal": self.security_signal(),
        })


@dataclass
class Planet:
    name: str
    country_names: List[str]
    truth_currency: FuzzyTruthStackCurrency
    biosphere_health: float = 0.8

    def update(self, rng: random.Random, countries_by_name: Dict[str, Country], market_stress: float) -> None:
        countries = [countries_by_name[n] for n in self.country_names if n in countries_by_name]
        if not countries:
            self.truth_currency.add(rng.gauss(0.0, 0.2))
            return
        governance = weighted_mean(((c.government_goodness, c.population) for c in countries), 0.0)
        popularity = weighted_mean(((c.popularity, c.population) for c in countries), 0.0)
        env_damage = mean((c.environmental_damage for c in countries), 0.0)
        # Truth event: governance + popularity - market stress - ecological denial noise.
        truth_event = governance * 0.45 + popularity * 0.20 - market_stress * 0.25 - env_damage * 0.05 + rng.gauss(0.0, 0.22)
        self.truth_currency.add(truth_event)
        self.truth_currency.noise(rng, 0.005 + max(0.0, market_stress) * 0.002)
        self.biosphere_health = clamp(self.biosphere_health - env_damage * 0.001 + mean((c.circular_policy for c in countries), 0.0) * 0.002, 0.0, 1.0)

    def truth_signal(self) -> float:
        return self.truth_currency.mean()

    def to_dict(self) -> Dict[str, Any]:
        return recursively_round({
            "name": self.name,
            "country_names": self.country_names,
            "truth_currency": self.truth_currency.to_dict(),
            "biosphere_health": self.biosphere_health,
            "truth_signal": self.truth_signal(),
        })


@dataclass
class StarSystem:
    name: str
    hierarchy: HierarchyCurrency

    def rebuild_from_world(self, world: "World") -> None:
        # Tier 0: coordinating institutions / country currency signs.
        country_tier = [softsign(c.currency.value / 100000.0) * 100.0 for c in world.countries]
        # Tier 1: productive firms / outputs.
        output_tier = [softsign(c.last_output / 1000.0) * 80.0 for c in world.countries]
        # Tier 2: social legitimacy / popularity.
        social_tier = [(c.government_goodness + c.popularity) * 40.0 for c in world.countries]
        # Tier 3: assets by class.
        asset_values = world.un_assets.class_values()
        asset_tier = [softsign(v / 100000.0) * 60.0 for v in asset_values.values()]
        # Tier 4: planetary truth stacks.
        truth_tier = [p.truth_currency.number() * 5.0 for p in world.planets]
        self.hierarchy.tiers = [country_tier, output_tier, social_tier, asset_tier, truth_tier]
        self.hierarchy.labels = ["countries", "production", "social", "assets", "truth"]
        self.hierarchy.normalize()

    def to_dict(self) -> Dict[str, Any]:
        return {"name": self.name, "hierarchy": self.hierarchy.to_dict()}


# ---------------------------------------------------------------------------
# Configuration and world
# ---------------------------------------------------------------------------


@dataclass
class SimulationConfig:
    steps: int = 120
    seed: int = 42
    countries: int = 8
    alliances: int = 2
    planets: int = 2
    defense_orgs: int = 2
    loop_length: int = 20
    scenario: str = "balanced"
    report_every: int = 20
    quiet: bool = False
    json_out: Optional[str] = None
    csv_out: Optional[str] = None
    monte_carlo: int = 0
    event_tail: int = 12


SCENARIO_PROFILES: Dict[str, Dict[str, float]] = {
    "balanced": {
        "goodness_bias": 0.0,
        "popularity_bias": 0.0,
        "circular_bias": 0.0,
        "defense_bias": 0.0,
        "asset_volatility": 1.0,
        "shock_rate": 1.0,
        "resource_bias": 1.0,
    },
    "regenerative": {
        "goodness_bias": 0.18,
        "popularity_bias": 0.10,
        "circular_bias": 0.45,
        "defense_bias": -0.05,
        "asset_volatility": 0.85,
        "shock_rate": 0.8,
        "resource_bias": 1.1,
    },
    "extraction": {
        "goodness_bias": -0.12,
        "popularity_bias": -0.05,
        "circular_bias": -0.35,
        "defense_bias": 0.10,
        "asset_volatility": 1.15,
        "shock_rate": 1.1,
        "resource_bias": 1.35,
    },
    "militarized": {
        "goodness_bias": -0.05,
        "popularity_bias": -0.12,
        "circular_bias": -0.10,
        "defense_bias": 0.55,
        "asset_volatility": 1.25,
        "shock_rate": 1.25,
        "resource_bias": 1.0,
    },
    "volatile": {
        "goodness_bias": 0.0,
        "popularity_bias": 0.0,
        "circular_bias": 0.0,
        "defense_bias": 0.0,
        "asset_volatility": 1.75,
        "shock_rate": 1.8,
        "resource_bias": 1.0,
    },
}


class World:
    def __init__(self, config: SimulationConfig):
        self.config = config
        self.rng = random.Random(config.seed)
        self.profile = SCENARIO_PROFILES.get(config.scenario, SCENARIO_PROFILES["balanced"])
        self.countries: List[Country] = []
        self.alliances: List[Alliance] = []
        self.defense_orgs: List[DefenseOrganization] = []
        self.planets: List[Planet] = []
        self.un_assets = UNAssetCurrency(unit="UNU")
        self.star_system = StarSystem("Sternensystem-Orion", HierarchyCurrency())
        self.galaxy_monoid = GalaxyMonoidCurrency()
        self.cluster_group = ClusterGroupCurrency()
        self.universe_loop = UniverseLoopCurrency(loop_length=config.loop_length)
        self.events: List[Event] = []
        self.history: List[Metrics] = []
        self._init_world()
        self.record_metrics(step=0)

    # ----- initialization ---------------------------------------------------

    def _init_world(self) -> None:
        self._init_countries()
        self._init_alliances()
        self._init_defense_orgs()
        self._init_planets()
        self._init_assets()
        self.star_system.rebuild_from_world(self)
        self.cluster_group.recompute(self)

    def _init_countries(self) -> None:
        for i in range(max(1, self.config.countries)):
            name = rand_name(self.rng, "Land", i)
            population = self.rng.uniform(2.0e6, 150.0e6)
            productivity = self.rng.uniform(30.0, 140.0)
            value = self.rng.uniform(5.0e4, 5.0e5)
            debt = value * self.rng.uniform(0.05, 0.95)
            goodness = clamp(self.rng.gauss(self.profile["goodness_bias"], 0.35), -1.0, 1.0)
            popularity = clamp(self.rng.gauss(self.profile["popularity_bias"], 0.35), -1.0, 1.0)
            circular_policy = clamp(self.rng.uniform(-0.2, 0.8) + self.profile["circular_bias"], -1.0, 1.0)
            defense_preference = clamp(self.rng.uniform(0.0, 0.8) + self.profile["defense_bias"], 0.0, 1.0)
            market_regulation = clamp(self.rng.uniform(0.0, 1.0), 0.0, 1.0)
            resource_stock = self.rng.uniform(400.0, 2200.0) * self.profile["resource_bias"]
            currency = CountryNumberCurrency("C%d" % (i + 1), value, self.rng.uniform(0.0, 0.08), debt)
            self.countries.append(Country(
                name=name,
                currency=currency,
                population=population,
                productivity=productivity,
                resource_stock=resource_stock,
                government_goodness=goodness,
                popularity=popularity,
                circular_policy=circular_policy,
                defense_preference=defense_preference,
                market_regulation=market_regulation,
            ))

    def _init_alliances(self) -> None:
        count = max(1, min(self.config.alliances, len(self.countries)))
        buckets: List[List[str]] = [[] for _ in range(count)]
        shuffled = list(self.countries)
        self.rng.shuffle(shuffled)
        for i, country in enumerate(shuffled):
            buckets[i % count].append(country.name)
        for i, members in enumerate(buckets):
            a = Alliance("Bündnis-%d" % (i + 1), members, cohesion=self.rng.uniform(0.25, 0.75))
            self.alliances.append(a)
            for name in members:
                self.country_by_name()[name].alliance_name = a.name
            a.update(self.country_by_name())

    def _init_defense_orgs(self) -> None:
        count = max(1, min(self.config.defense_orgs, max(1, len(self.alliances))))
        for i in range(count):
            alliance = self.alliances[i % len(self.alliances)]
            dims = {
                "logistics": self.rng.uniform(50.0, 400.0),
                "territory": self.rng.uniform(10.0, 160.0),
                "cyber": self.rng.uniform(20.0, 250.0),
                "time": self.rng.uniform(10.0, 100.0),
                "attention": self.rng.uniform(10.0, 100.0),
                "protected_human_agency_links": self.rng.uniform(0.0, 25.0),
            }
            space = DefenseSpaceCurrency(dimensions=dims)
            org = DefenseOrganization("Verteidigungsraum-%d" % (i + 1), list(alliance.member_names), space)
            self.defense_orgs.append(org)

    def _init_planets(self) -> None:
        count = max(1, self.config.planets)
        buckets: List[List[str]] = [[] for _ in range(count)]
        for i, country in enumerate(self.countries):
            buckets[i % count].append(country.name)
        for i, members in enumerate(buckets):
            truth = FuzzyTruthStackCurrency(max_stack=250)
            for _ in range(20):
                truth.add(clamp(self.rng.gauss(self.profile["goodness_bias"] * 0.3, 0.45), -1.0, 1.0))
            self.planets.append(Planet("Planet-%d" % (i + 1), members, truth, self.rng.uniform(0.55, 0.95)))

    def _init_assets(self) -> None:
        volatility_factor = self.profile["asset_volatility"]
        asset_specs = [
            ("stock", "UN-Industrie-Aktie", 1200.0, 80.0, 0.025, 1.0),
            ("stock", "UN-Nahrungs-Aktie", 800.0, 55.0, 0.018, 1.0),
            ("derivative", "Hierarchie-Swap", 150.0, 120.0, 0.045, 3.5),
            ("derivative", "Wahrheits-Future", 300.0, 35.0, 0.060, 2.5),
            ("fund", "Kreislauf-Fonds", 500.0, 70.0, 0.015, 1.0),
            ("fund", "Bündnis-Indexfonds", 650.0, 65.0, 0.018, 1.0),
            ("certificate", "Raum-Volumen-Zertifikat", 400.0, 90.0, 0.022, 1.2),
            ("certificate", "Kompost-Schuld-Zertifikat", 350.0, 45.0, 0.028, -0.8),
            ("forex", "UNU-FX-Korb", 10000.0, 1.0, 0.010, 1.0),
        ]
        for cls, name, units, price, vol, lev in asset_specs:
            jitter_units = units * self.rng.uniform(0.75, 1.25)
            jitter_price = price * self.rng.uniform(0.75, 1.25)
            self.un_assets.positions.append(AssetPosition(cls, name, jitter_units, jitter_price, vol * volatility_factor, lev, "UNU"))

    # ----- lookup and signals ----------------------------------------------

    def country_by_name(self) -> Dict[str, Country]:
        return {c.name: c for c in self.countries}

    def alliance_by_name(self) -> Dict[str, Alliance]:
        return {a.name: a for a in self.alliances}

    def average_truth_signal(self) -> float:
        return mean((p.truth_signal() for p in self.planets), 0.0)

    def total_country_number(self) -> float:
        return sum(c.currency.value for c in self.countries)

    def total_output(self) -> float:
        return sum(c.last_output for c in self.countries)

    def average_defense_security(self) -> float:
        return mean((d.security_signal() for d in self.defense_orgs), 0.0)

    def current_systemic_risk(self) -> float:
        avg_infl = mean((max(0.0, c.currency.inflation) for c in self.countries), 0.0)
        avg_debt_stress = mean((c.currency.stress() for c in self.countries), 0.0)
        lie_debt = sum(p.truth_currency.lie_debt() for p in self.planets)
        circular_debt = self.universe_loop.total_debt()
        defense_penalty = mean((d.space_currency.social_legitimacy_penalty() for d in self.defense_orgs), 0.0)
        risk = (
            softsign(avg_infl * 4.0) * 0.20
            + softsign(avg_debt_stress * 2.0) * 0.20
            + softsign(lie_debt / 50.0) * 0.20
            + softsign(circular_debt / 2000.0) * 0.20
            + defense_penalty * 0.20
        )
        return clamp(risk, 0.0, 1.0)

    # ----- simulation step --------------------------------------------------

    def step(self, step: int) -> None:
        # 1) Random shocks/events.
        self._maybe_random_shock(step)

        # 2) Planets update truth before country decisions.
        countries_by_name = self.country_by_name()
        market_stress = softsign(abs(self.un_assets.total_value()) / 1.0e6 - 0.5) + self.current_systemic_risk() * 0.2
        for planet in self.planets:
            planet.update(self.rng, countries_by_name, market_stress)

        truth_signal = self.average_truth_signal()

        # 3) Alliances recompute angle currencies.
        for alliance in self.alliances:
            alliance.update(countries_by_name)

        # 4) Defense spaces update.
        threat_signal = clamp(self.current_systemic_risk() + max(0.0, -truth_signal) * 0.5 + self.rng.gauss(0.0, 0.1), 0.0, 1.0)
        for org in self.defense_orgs:
            org.update(self.rng, countries_by_name, threat_signal)

        defense_security = self.average_defense_security()
        market_signal = softsign(self.un_assets.total_value() / 250000.0)
        circular_pressure = softsign(self.universe_loop.total_debt() / 1000.0)

        # 5) Countries produce, pay, accumulate circular debt/contribution.
        debt_delta_total: Dict[str, float] = {}
        contribution_delta_total: Dict[str, float] = {}
        alliance_lookup = self.alliance_by_name()
        for c in self.countries:
            alliance_signal = 0.0
            if c.alliance_name and c.alliance_name in alliance_lookup:
                alliance_signal = alliance_lookup[c.alliance_name].numeric_trade_signal()
            output, debt_delta, contribution_delta = c.step(
                self.rng,
                truth_signal,
                alliance_signal,
                defense_security,
                market_signal,
                circular_pressure,
            )
            for k, v in debt_delta.items():
                debt_delta_total[k] = debt_delta_total.get(k, 0.0) + v
            for k, v in contribution_delta.items():
                contribution_delta_total[k] = contribution_delta_total.get(k, 0.0) + v

        # 6) Trade balances: alliance corridors redistribute moderate surpluses.
        self._update_trade_balances()

        # 7) UN asset market update.
        growth_signal = softsign(self.total_output() / max(1.0, len(self.countries) * 1000.0) - 1.0)
        systemic_risk = self.current_systemic_risk()
        self.un_assets.update_market(self.rng, growth_signal, truth_signal, systemic_risk)

        # 8) Universe loop currency ticks with circular stack.
        self.universe_loop.tick(debt_delta_total, contribution_delta_total)
        if self.universe_loop.loop_point == 0:
            decay_rate = clamp(0.02 + mean((c.circular_policy for c in self.countries), 0.0) * 0.015, 0.0, 0.08)
            self.universe_loop.decay(decay_rate)
            self.events.append(Event(step, "universe_loop", "Universum", decay_rate,
                                     "For-Schleife abgeschlossen; Kreislaufbestand wurde teilweise amortisiert."))

        # 9) Star hierarchy rebuild and optional galaxy monoid operation.
        self.star_system.rebuild_from_world(self)
        self._maybe_galaxy_operation(step)
        mono_events = self.galaxy_monoid.apply(self, step)
        self.events.extend(mono_events)

        # 10) Cluster group concatenates/aggregates all smaller currencies.
        self.cluster_group.recompute(self)

        # 11) Record metrics.
        self.record_metrics(step)

    def _update_trade_balances(self) -> None:
        # Trade effect is small and temporary. Positive angle corridors support
        # members; negative corridors impose mistrust costs.
        for c in self.countries:
            c.trade_balance *= 0.25
        countries_by_name = self.country_by_name()
        for alliance in self.alliances:
            signal = softsign(alliance.numeric_trade_signal() / 100.0)
            members = [countries_by_name[n] for n in alliance.member_names if n in countries_by_name]
            if not members:
                continue
            avg_output = mean((m.last_output for m in members), 0.0)
            for m in members:
                competitiveness = safe_div(m.last_output - avg_output, avg_output + 1.0)
                m.trade_balance += (signal * 0.02 + competitiveness * 0.01) * avg_output

    def _maybe_random_shock(self, step: int) -> None:
        shock_rate = self.profile["shock_rate"]
        probability = min(0.35, 0.045 * shock_rate)
        if self.rng.random() > probability:
            return
        kind = self.rng.choice([
            "scandal",
            "cooperation",
            "market_crash",
            "truth_leak",
            "disinformation",
            "resource_boom",
            "circular_windfall",
            "military_tension",
        ])
        intensity = self.rng.uniform(0.1, 1.0) * shock_rate
        if kind == "scandal" and self.countries:
            c = self.rng.choice(self.countries)
            c.government_goodness = clamp(c.government_goodness - intensity * 0.25, -1.0, 1.0)
            c.popularity = clamp(c.popularity - intensity * 0.20, -1.0, 1.0)
            self.events.append(Event(step, "shock", c.name, intensity, "Skandal senkt Gut/Böse-Achse und Beliebtheit."))
        elif kind == "cooperation" and self.alliances:
            a = self.rng.choice(self.alliances)
            a.cohesion = clamp(a.cohesion + intensity * 0.20, 0.0, 1.0)
            self.events.append(Event(step, "shock", a.name, intensity, "Kooperationsvertrag erhöht Bündniskohäsion."))
        elif kind == "market_crash":
            self.un_assets.shock(self.rng, intensity)
            self.events.append(Event(step, "shock", "UN-Assets", intensity, "Marktkrise reduziert Assetpreise, Derivate reagieren stärker."))
        elif kind == "truth_leak" and self.planets:
            p = self.rng.choice(self.planets)
            p.truth_currency.add(clamp(0.5 + intensity * 0.4, -1.0, 1.0))
            self.events.append(Event(step, "shock", p.name, intensity, "Wahrheitsleck fügt positiven Fuzzy-Wert hinzu."))
        elif kind == "disinformation" and self.planets:
            p = self.rng.choice(self.planets)
            p.truth_currency.add(clamp(-0.5 - intensity * 0.4, -1.0, 1.0))
            self.events.append(Event(step, "shock", p.name, intensity, "Desinformationswelle fügt negativen Fuzzy-Wert hinzu."))
        elif kind == "resource_boom" and self.countries:
            c = self.rng.choice(self.countries)
            c.resource_stock += intensity * self.rng.uniform(100.0, 600.0)
            self.events.append(Event(step, "shock", c.name, intensity, "Ressourcenfund erhöht Rohstoffbestand."))
        elif kind == "circular_windfall":
            gain = intensity * 50.0
            self.universe_loop.circular_contribution["compost"] += gain
            self.universe_loop.circular_contribution["reuse"] += gain * 0.5
            self.events.append(Event(step, "shock", "Universum", intensity, "Kreislaufgewinn erhöht Kompost und Wiederverwendung."))
        elif kind == "military_tension" and self.defense_orgs:
            d = self.rng.choice(self.defense_orgs)
            d.space_currency.add("logistics", intensity * 40.0)
            d.space_currency.add("attention", intensity * 30.0)
            d.space_currency.add("protected_human_agency_links", intensity * 5.0)
            self.events.append(Event(step, "shock", d.name, intensity, "Militärische Spannung erweitert Raumdimensionen und Schutzlast."))

    def _maybe_galaxy_operation(self, step: int) -> None:
        # Galaxy monoid operations are rare because they are extremely strong.
        risk = self.current_systemic_risk()
        if self.rng.random() > 0.025 + risk * 0.04:
            return
        op_name = self.rng.choice([
            "invert_angle",
            "invert_truth",
            "twist_hierarchy",
            "invert_space_orientation",
            "invert_country_number",
        ])
        intensity = clamp(self.rng.uniform(0.25, 1.25) + risk * 0.4, 0.1, 1.8)
        target_type = {
            "invert_angle": "alliance_angle_currency",
            "invert_truth": "planet_truth_stack_currency",
            "twist_hierarchy": "star_system_hierarchy_currency",
            "invert_space_orientation": "defense_space_currency",
            "invert_country_number": "country_number_currency",
        }[op_name]
        self.galaxy_monoid.compose(MonoidOperation(op_name, target_type, intensity))

    # ----- metrics, serialization, reporting --------------------------------

    def compute_metrics(self, step: int) -> Metrics:
        total_country_number = self.total_country_number()
        avg_country_number = total_country_number / float(max(1, len(self.countries)))
        avg_inflation = mean((c.currency.inflation for c in self.countries), 0.0)
        avg_government_goodness = mean((c.government_goodness for c in self.countries), 0.0)
        avg_popularity = mean((c.popularity for c in self.countries), 0.0)
        avg_alliance_angle_value = mean((a.currency.folded_angle for a in self.alliances), 0.0)
        avg_alliance_tan_value = mean((a.currency.tan_number() for a in self.alliances), 0.0)
        defense_volume_number = sum(d.space_currency.volume_number() for d in self.defense_orgs)
        protected_human_agency_links = sum(d.space_currency.protected_human_agency() for d in self.defense_orgs)
        un_asset_value = self.un_assets.total_value()
        avg_truth_mean = self.average_truth_signal()
        stacked_truth_number = sum(p.truth_currency.number() for p in self.planets)
        hierarchy_number = self.star_system.hierarchy.to_number()
        self.cluster_group.recompute(self)
        cluster_number = self.cluster_group.group_number()
        universe_units = self.universe_loop.currency_units()
        circular_debt = self.universe_loop.total_debt()
        circular_contribution = self.universe_loop.total_contribution()
        universe_stacked_value = self.universe_loop.stacked_value()
        systemic_risk = self.current_systemic_risk()
        return Metrics(
            step=step,
            total_country_number=total_country_number,
            avg_country_number=avg_country_number,
            avg_inflation=avg_inflation,
            avg_government_goodness=avg_government_goodness,
            avg_popularity=avg_popularity,
            avg_alliance_angle_value=avg_alliance_angle_value,
            avg_alliance_tan_value=avg_alliance_tan_value,
            defense_volume_number=defense_volume_number,
            protected_human_agency_links=protected_human_agency_links,
            un_asset_value=un_asset_value,
            avg_truth_mean=avg_truth_mean,
            stacked_truth_number=stacked_truth_number,
            hierarchy_number=hierarchy_number,
            cluster_number=cluster_number,
            universe_units=universe_units,
            circular_debt=circular_debt,
            circular_contribution=circular_contribution,
            universe_stacked_value=universe_stacked_value,
            systemic_risk=systemic_risk,
        )

    def record_metrics(self, step: int) -> None:
        self.history.append(self.compute_metrics(step))

    def to_dict(self, include_full_state: bool = True) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "config": self.config.__dict__,
            "final_metrics": self.history[-1].to_dict() if self.history else {},
            "history": [m.to_dict() for m in self.history],
            "events": [e.to_dict() for e in self.events],
        }
        if include_full_state:
            data["state"] = {
                "countries": [c.to_dict() for c in self.countries],
                "alliances": [a.to_dict() for a in self.alliances],
                "defense_orgs": [d.to_dict() for d in self.defense_orgs],
                "planets": [p.to_dict() for p in self.planets],
                "un_assets": self.un_assets.to_dict(),
                "star_system": self.star_system.to_dict(),
                "galaxy_monoid": self.galaxy_monoid.to_dict(),
                "cluster_group": self.cluster_group.to_dict(),
                "universe_loop": self.universe_loop.to_dict(),
            }
        return recursively_round(data)

    def report_line(self, metrics: Metrics) -> str:
        return (
            "t={step:>4} | LandZahl={country} | WinkelTan={angle} | "
            "RaumVol={space} | Wahrheit={truth:>7.3f} | Hier={hier} | "
            "Cluster={cluster} | Loop={loop:>5} | Kreis={circ} | Risiko={risk:>5.3f}"
        ).format(
            step=metrics.step,
            country=fmt_num(metrics.total_country_number),
            angle=fmt_num(metrics.avg_alliance_tan_value, width=10),
            space=fmt_num(metrics.defense_volume_number),
            truth=metrics.avg_truth_mean,
            hier=fmt_num(metrics.hierarchy_number, width=9),
            cluster=fmt_num(metrics.cluster_number),
            loop=metrics.universe_units,
            circ=fmt_num(metrics.universe_stacked_value),
            risk=metrics.systemic_risk,
        )

    def final_report(self, event_tail: int = 12) -> str:
        m = self.history[-1]
        lines = []
        lines.append("\n=== Finale Wirtschaftssimulation ===")
        lines.append("Szenario: %s | Seed: %s | Schritte: %s" % (self.config.scenario, self.config.seed, self.config.steps))
        lines.append(self.report_line(m))
        lines.append("")
        lines.append("Währungsebenen:")
        lines.append("  Land/Zahl:                 total %.2f, Ø %.2f, Ø Inflation %.4f" % (
            m.total_country_number, m.avg_country_number, m.avg_inflation))
        lines.append("  Bündnis/Winkel:            Ø Winkel %.4f rad, Ø tan-Zahl %.2f" % (
            m.avg_alliance_angle_value, m.avg_alliance_tan_value))
        lines.append("  Verteidigungsraum:         Volumenzahl %.2f, geschützte Human-Agency-Links %.2f" % (
            m.defense_volume_number, m.protected_human_agency_links))
        lines.append("  UN-Assets:                 Gesamtwert %.2f %s" % (m.un_asset_value, self.un_assets.unit))
        lines.append("  Planet/Wahrheit:           Ø Wahrheit %.4f, gestapelte Zahl %.2f" % (
            m.avg_truth_mean, m.stacked_truth_number))
        lines.append("  Sternensystem/Hierarchie:  Zahl %.2f" % m.hierarchy_number)
        lines.append("  Cluster/Gruppe:            additionsähnliche Gruppenzahl %.2f" % m.cluster_number)
        lines.append("  Universum/For-Schleife:    %d Einheiten; Schuld %.2f, Beitrag %.2f, Stack %.2f" % (
            m.universe_units, m.circular_debt, m.circular_contribution, m.universe_stacked_value))
        lines.append("")
        top_countries = sorted(self.countries, key=lambda c: c.currency.value, reverse=True)[:5]
        lines.append("Stärkste Länder nach Zahlenwährung:")
        for c in top_countries:
            lines.append("  %-24s %12.2f  gut=%+.3f beliebt=%+.3f output=%.2f" % (
                c.name, c.currency.value, c.government_goodness, c.popularity, c.last_output))
        if self.events:
            lines.append("")
            lines.append("Letzte Ereignisse:")
            for e in self.events[-event_tail:]:
                lines.append("  t=%-4d %-15s %-24s %+6.3f  %s" % (e.step, e.kind, e.target, e.intensity, e.description))
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Simulation runners
# ---------------------------------------------------------------------------


def run_world(config: SimulationConfig) -> World:
    world = World(config)
    if not config.quiet:
        print("=== Wirtschaftssimulation startet ===")
        print("Szenario: %s | Seed: %s | Länder: %d | Schritte: %d" % (
            config.scenario, config.seed, config.countries, config.steps))
        print(world.report_line(world.history[-1]))
    for step in range(1, config.steps + 1):
        world.step(step)
        if not config.quiet and config.report_every > 0 and (step % config.report_every == 0 or step == config.steps):
            print(world.report_line(world.history[-1]))
    return world


def run_monte_carlo(config: SimulationConfig) -> Dict[str, Any]:
    runs = max(1, config.monte_carlo)
    summaries: List[Dict[str, Any]] = []
    for i in range(runs):
        c = SimulationConfig(**config.__dict__)
        c.seed = config.seed + i
        c.quiet = True
        c.json_out = None
        c.csv_out = None
        c.monte_carlo = 0
        world = run_world(c)
        fm = world.history[-1].to_dict()
        fm["seed"] = c.seed
        summaries.append(fm)
    fields = [
        "total_country_number", "avg_inflation", "avg_alliance_tan_value",
        "defense_volume_number", "un_asset_value", "avg_truth_mean",
        "hierarchy_number", "cluster_number", "universe_stacked_value", "systemic_risk",
    ]
    aggregate: Dict[str, Dict[str, float]] = {}
    for f in fields:
        vals = [float(s[f]) for s in summaries]
        vals_sorted = sorted(vals)
        aggregate[f] = {
            "mean": mean(vals),
            "min": min(vals),
            "max": max(vals),
            "p10": vals_sorted[int(0.10 * (len(vals_sorted) - 1))],
            "p50": vals_sorted[int(0.50 * (len(vals_sorted) - 1))],
            "p90": vals_sorted[int(0.90 * (len(vals_sorted) - 1))],
        }
    return recursively_round({
        "config": config.__dict__,
        "runs": summaries,
        "aggregate": aggregate,
    })


def write_json(path: str, data: Dict[str, Any]) -> None:
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)


def write_csv(path: str, history: Sequence[Metrics]) -> None:
    if not history:
        return
    fields = list(history[0].to_dict().keys())
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for m in history:
            writer.writerow(m.to_dict())


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Sequence[str]) -> SimulationConfig:
    parser = argparse.ArgumentParser(
        description="Umfangreiche abstrakte Wirtschaftssimulation für PyPy3.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--steps", type=int, default=120, help="Simulationsschritte")
    parser.add_argument("--seed", type=int, default=42, help="Zufallsseed")
    parser.add_argument("--countries", type=int, default=8, help="Anzahl Länder")
    parser.add_argument("--alliances", type=int, default=2, help="Anzahl Bündnisse")
    parser.add_argument("--planets", type=int, default=2, help="Anzahl Planeten")
    parser.add_argument("--defense-orgs", type=int, default=2, help="Anzahl Verteidigungsorganisationen")
    parser.add_argument("--loop-length", type=int, default=20, help="Punkte pro Universums-For-Schleife")
    parser.add_argument("--scenario", choices=sorted(SCENARIO_PROFILES.keys()), default="balanced", help="Szenarioprofil")
    parser.add_argument("--report-every", type=int, default=20, help="Bericht alle N Schritte")
    parser.add_argument("--quiet", action="store_true", help="Keine Zwischenberichte ausgeben")
    parser.add_argument("--json-out", default=None, help="JSON-Datei für kompletten Zustand")
    parser.add_argument("--csv-out", default=None, help="CSV-Datei für Zeitreihe")
    parser.add_argument("--monte-carlo", type=int, default=0, help="N unabhängige Läufe; >0 aktiviert Monte-Carlo-Modus")
    parser.add_argument("--event-tail", type=int, default=12, help="Anzahl Ereignisse im finalen Bericht")
    ns = parser.parse_args(argv)
    if ns.steps < 0:
        parser.error("--steps muss >= 0 sein")
    if ns.countries < 1:
        parser.error("--countries muss >= 1 sein")
    if ns.alliances < 1:
        parser.error("--alliances muss >= 1 sein")
    if ns.planets < 1:
        parser.error("--planets muss >= 1 sein")
    if ns.defense_orgs < 1:
        parser.error("--defense-orgs muss >= 1 sein")
    if ns.loop_length < 1:
        parser.error("--loop-length muss >= 1 sein")
    return SimulationConfig(
        steps=ns.steps,
        seed=ns.seed,
        countries=ns.countries,
        alliances=ns.alliances,
        planets=ns.planets,
        defense_orgs=ns.defense_orgs,
        loop_length=ns.loop_length,
        scenario=ns.scenario,
        report_every=ns.report_every,
        quiet=ns.quiet,
        json_out=ns.json_out,
        csv_out=ns.csv_out,
        monte_carlo=ns.monte_carlo,
        event_tail=ns.event_tail,
    )


def main(argv: Sequence[str]) -> int:
    config = parse_args(argv)
    if config.monte_carlo and config.monte_carlo > 0:
        data = run_monte_carlo(config)
        if config.json_out:
            write_json(config.json_out, data)
        if not config.quiet:
            print("=== Monte-Carlo-Zusammenfassung ===")
            print("Szenario: %s | Läufe: %d | Schritte je Lauf: %d | Seed-Basis: %d" % (
                config.scenario, config.monte_carlo, config.steps, config.seed))
            for key, stats in data["aggregate"].items():
                print("%-28s mean=%12.4f p10=%12.4f p50=%12.4f p90=%12.4f min=%12.4f max=%12.4f" % (
                    key,
                    stats["mean"], stats["p10"], stats["p50"], stats["p90"], stats["min"], stats["max"],
                ))
            if config.json_out:
                print("JSON geschrieben: %s" % config.json_out)
        return 0

    world = run_world(config)
    if config.csv_out:
        write_csv(config.csv_out, world.history)
    if config.json_out:
        write_json(config.json_out, world.to_dict(include_full_state=True))
    if not config.quiet:
        print(world.final_report(config.event_tail))
        if config.csv_out:
            print("CSV geschrieben: %s" % config.csv_out)
        if config.json_out:
            print("JSON geschrieben: %s" % config.json_out)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main(sys.argv[1:]))
    except KeyboardInterrupt:
        print("\nAbgebrochen.", file=sys.stderr)
        raise SystemExit(130)
