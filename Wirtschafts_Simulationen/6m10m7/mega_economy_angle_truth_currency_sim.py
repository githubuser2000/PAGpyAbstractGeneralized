#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Mega Economy Simulation with Tradeable Fuzzy-Truth Currency and Angular Moral Currency
=====================================================================================

A deliberately broad, standard-library-only, PyPy3-compatible economic simulator.
It is not a prediction machine. It is a laboratory for causal mechanisms.

Core goals built into the simulator
-----------------------------------
1. Inflation diagnostics:
   - demand inflation, wage-price loops, energy/import shocks, markups, supply bottlenecks.
2. Financial stability:
   - bank capital, credit rationing, defaults, collateral cycles, asset-price feedbacks.
3. Labor-market dynamics:
   - search/matching, skill mismatch, unemployment, wage bargaining, automation pressure.
4. Distributional analysis:
   - income/wealth inequality, poverty, renters vs owners, regional divergence.
5. Housing-system analysis:
   - rents, house prices, mortgage credit, construction lags, affordability.
6. Energy and climate transition:
   - fossil-price shocks, carbon pricing, renewables, emissions, green investment.
7. Supply-chain propagation:
   - input-output costs, supplier fragility, import dependence, bottleneck amplification.
8. Fiscal and monetary policy:
   - taxes, transfers, public services, debt, central-bank reaction functions.
9. Platform/digital-market concentration:
   - network effects, take rates, market power, digital productivity.
10. Open-economy stress:
   - exchange rates, exports, imports, tariffs, capital-flow pressure.
11. Social systems:
   - education, health, insurance, human capital, long-run productivity.
12. Robust stress testing:
   - scenarios can be combined, extended, or run in batches.
13. Tradeable fuzzy-truth currency:
   - each monetary flow is also mapped into an n-ary logic predicate.
   - predicate values range from -1 (lie/wrong) to +1 (truth/right).
   - stacked predicate values are rational numbers and form a second currency.
   - verification/falsification increases predicate arity by adding audit elements.
   - resource and energy quotas create fuzzy truth ranges for allowed planetary use.
   - exceeding one quota throttles all other resource quotas per time step.
   - firms trade truth stacks, correctness models, knowledge, education, audits, and balance-sheet verification.
14. Tradeable angular moral currency:
   - fiat and LOGOS exchanges also mint or destroy ANGLE/ARETE units.
   - two economies define benevolence at 0° and 90°; the synthetic shared good lies at 45°.
   - evil lies opposite at 225°; the orthogonal 135°/315° axis measures popular/unpopular.
   - good wealth is bounded by the half-circle circumference between evil and good.
   - every market object receives an angle: labor, goods, credit, housing, resources, data, education, audits.
   - actors can trade angular units, moral models, knowledge, and angle-improved resource rights.

Run examples
------------
    pypy3 mega_economy_sim.py --steps 180 --households 800 --firms 160 --banks 7 \
        --scenario baseline --out baseline.csv --json baseline_summary.json

    pypy3 mega_economy_sim.py --scenario energy_shock --steps 120 --seed 7

    pypy3 mega_economy_sim.py --compare baseline energy_shock financial_crisis \
        housing_boom_bust climate_transition ai_automation --steps 160 --out comparison.csv

Design philosophy
-----------------
The model is intentionally large, but each mechanism is simple enough to inspect.
The point is to make feedback loops visible, not to hide them behind opaque math.
All numbers are stylized. Calibrate before using it for serious empirical work.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import statistics
import sys
from fractions import Fraction
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from typing import Any, Deque, Dict, Iterable, List, Optional, Sequence, Tuple

EPS = 1e-9


# ---------------------------------------------------------------------------
# Utility functions
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


def logistic(x: float) -> float:
    if x >= 40:
        return 1.0
    if x <= -40:
        return 0.0
    return 1.0 / (1.0 + math.exp(-x))


def mean(xs: Iterable[float], default: float = 0.0) -> float:
    xs = list(xs)
    if not xs:
        return default
    return sum(xs) / len(xs)


def median(xs: Iterable[float], default: float = 0.0) -> float:
    xs = list(xs)
    if not xs:
        return default
    return statistics.median(xs)


def percentile(xs: Iterable[float], p: float, default: float = 0.0) -> float:
    xs = sorted(xs)
    if not xs:
        return default
    if len(xs) == 1:
        return xs[0]
    p = clamp(p, 0.0, 1.0)
    idx = p * (len(xs) - 1)
    lo = int(math.floor(idx))
    hi = int(math.ceil(idx))
    if lo == hi:
        return xs[lo]
    return xs[lo] * (hi - idx) + xs[hi] * (idx - lo)


def gini(xs: Iterable[float]) -> float:
    values = sorted(max(0.0, x) for x in xs)
    n = len(values)
    if n == 0:
        return 0.0
    total = sum(values)
    if total <= EPS:
        return 0.0
    weighted = sum((i + 1) * x for i, x in enumerate(values))
    return (2.0 * weighted) / (n * total) - (n + 1.0) / n


def hhi(shares: Iterable[float]) -> float:
    ss = list(shares)
    total = sum(ss)
    if total <= EPS:
        return 0.0
    return sum((s / total) ** 2 for s in ss)


def weighted_choice(rng: random.Random, items: Sequence[Any], weights: Sequence[float]) -> Any:
    if not items:
        raise ValueError("weighted_choice on empty items")
    total = sum(max(0.0, w) for w in weights)
    if total <= EPS:
        return items[rng.randrange(len(items))]
    r = rng.random() * total
    acc = 0.0
    for item, weight in zip(items, weights):
        acc += max(0.0, weight)
        if acc >= r:
            return item
    return items[-1]


def correlated_noise(rng: random.Random, last: float, rho: float, sigma: float) -> float:
    return rho * last + rng.gauss(0.0, sigma)


def fmt_money(x: float) -> str:
    return f"{x:,.2f}"


def weighted_average(pairs: Iterable[Tuple[float, float]], default: float = 0.0) -> float:
    num = 0.0
    den = 0.0
    for value, weight in pairs:
        if weight > 0:
            num += value * weight
            den += weight
    if den <= EPS:
        return default
    return num / den


# ---------------------------------------------------------------------------
# Fuzzy-truth rational currency helpers
# ---------------------------------------------------------------------------

TRUTH_DENOMINATOR = 1_000_000
TRUTH_LIMIT_DENOMINATOR = 1_000_000


def truth_zero() -> Fraction:
    return Fraction(0, 1)


def rationalize(x: float, denominator: int = TRUTH_DENOMINATOR) -> Fraction:
    """Represent a fuzzy value or truth-money amount as a bounded rational."""
    if not math.isfinite(x):
        x = 0.0
    return Fraction(int(round(x * denominator)), denominator).limit_denominator(TRUTH_LIMIT_DENOMINATOR)


def rational_float(x: Fraction) -> float:
    if x.denominator == 0:
        return 0.0
    return float(x.numerator) / float(x.denominator)


def truth_clamp(x: Fraction, lo: float = -100_000.0, hi: float = 100_000.0) -> Fraction:
    return rationalize(clamp(rational_float(x), lo, hi))


def truth_balance_score(x: Fraction, scale: float = 22.0) -> float:
    return math.tanh(rational_float(x) / max(0.5, scale))


def fuzzy_range(value: float, safe: float, warning: float, hard: float) -> float:
    """Map use inside/outside a quota range to a fuzzy truth value in [-1, 1]."""
    value = max(0.0, value)
    safe = max(EPS, safe)
    warning = max(safe + EPS, warning)
    hard = max(warning + EPS, hard)
    if value <= safe:
        return 1.0
    if value <= warning:
        return 1.0 - 0.75 * safe_div(value - safe, warning - safe, 0.0)
    if value <= hard:
        return 0.25 - 1.25 * safe_div(value - warning, hard - warning, 0.0)
    return -1.0


def fuzzy_stack_mean(values: Iterable[float]) -> Fraction:
    vals = [clamp(v, -1.0, 1.0) for v in values]
    if not vals:
        return Fraction(0, 1)
    return rationalize(sum(vals) / len(vals))


# ---------------------------------------------------------------------------
# Angular moral currency helpers
# ---------------------------------------------------------------------------

ANGLE_STATE_A_GOOD_DEG = 0.0
ANGLE_STATE_B_GOOD_DEG = 90.0
ANGLE_OBJECTIVE_GOOD_DEG = 45.0
ANGLE_EVIL_DEG = 225.0
ANGLE_POPULAR_DEG = 135.0
ANGLE_UNPOPULAR_DEG = 315.0
ANGLE_HALF_CIRCLE_CIRCUMFERENCE = math.pi


def norm_angle(deg: float) -> float:
    if not math.isfinite(deg):
        deg = ANGLE_OBJECTIVE_GOOD_DEG
    deg = deg % 360.0
    if deg < 0.0:
        deg += 360.0
    return deg


def signed_angle_delta(a: float, b: float) -> float:
    """Smallest signed angular difference a-b in degrees."""
    return ((norm_angle(a) - norm_angle(b) + 180.0) % 360.0) - 180.0


def angular_distance(a: float, b: float) -> float:
    return abs(signed_angle_delta(a, b))


def angle_axis_coordinate(angle_deg: float, axis_deg: float) -> float:
    """Cosine coordinate on an axis: +1 on axis, -1 on the opposite side."""
    return math.cos(math.radians(signed_angle_delta(angle_deg, axis_deg)))


def angle_goodness_fraction(angle_deg: float) -> float:
    """0 at evil/opposite, 1 at shared good; linear along the half-circle."""
    return clamp(1.0 - angular_distance(angle_deg, ANGLE_OBJECTIVE_GOOD_DEG) / 180.0, 0.0, 1.0)


def angle_good_circumference_value(angle_deg: float, radius: float = 1.0) -> float:
    """Good as a number: at most the circumference of a half-circle, pi*r."""
    return ANGLE_HALF_CIRCLE_CIRCUMFERENCE * max(0.0, radius) * angle_goodness_fraction(angle_deg)


def angle_wealth_score(balance: float, debt: float = 0.0, scale: float = 35.0) -> float:
    return math.tanh((balance - debt) / max(0.50, scale))


def circular_mean_deg(angles: Sequence[float], weights: Optional[Sequence[float]] = None, default: float = ANGLE_OBJECTIVE_GOOD_DEG) -> float:
    if not angles:
        return norm_angle(default)
    if weights is None:
        weights = [1.0] * len(angles)
    x = 0.0
    y = 0.0
    total = 0.0
    for a, w in zip(angles, weights):
        w = max(0.0, float(w))
        if w <= 0.0:
            continue
        rad = math.radians(norm_angle(a))
        x += math.cos(rad) * w
        y += math.sin(rad) * w
        total += w
    if total <= EPS or abs(x) + abs(y) <= EPS:
        return norm_angle(default)
    return norm_angle(math.degrees(math.atan2(y, x)))


def blend_angles(source: float, target: float, strength: float) -> float:
    strength = clamp(strength, 0.0, 1.0)
    return norm_angle(source + signed_angle_delta(target, source) * strength)


# ---------------------------------------------------------------------------
# Economy constants
# ---------------------------------------------------------------------------

REGIONS = ["Capital", "North", "South", "East", "West", "Rural"]

SECTORS = [
    "Food",
    "Retail",
    "Manufacturing",
    "Construction",
    "HousingServices",
    "Energy",
    "Transport",
    "Health",
    "Education",
    "Finance",
    "DigitalPlatform",
    "ProfessionalServices",
    "Exportables",
    "GovernmentSupply",
]

TRADABLE_SECTORS = {"Food", "Manufacturing", "Energy", "Transport", "DigitalPlatform", "Exportables"}
SERVICE_SECTORS = {"Retail", "HousingServices", "Health", "Education", "Finance", "ProfessionalServices", "GovernmentSupply"}
PUBLIC_SERVICE_SECTORS = {"Health", "Education", "GovernmentSupply", "Transport"}
HIGH_SKILL_SECTORS = {"Finance", "DigitalPlatform", "ProfessionalServices", "Education", "Health"}
CAPITAL_HEAVY_SECTORS = {"Manufacturing", "Energy", "Transport", "Construction", "DigitalPlatform", "Exportables"}
LOW_MARGIN_SECTORS = {"Food", "Retail", "Transport"}

SECTOR_WEIGHTS_FOR_FIRMS = {
    "Food": 0.09,
    "Retail": 0.12,
    "Manufacturing": 0.13,
    "Construction": 0.07,
    "HousingServices": 0.05,
    "Energy": 0.04,
    "Transport": 0.07,
    "Health": 0.08,
    "Education": 0.06,
    "Finance": 0.05,
    "DigitalPlatform": 0.05,
    "ProfessionalServices": 0.08,
    "Exportables": 0.08,
    "GovernmentSupply": 0.05,
}

BASE_CONSUMPTION_PREFS = {
    "Food": 0.18,
    "Retail": 0.15,
    "Manufacturing": 0.08,
    "Construction": 0.00,
    "HousingServices": 0.18,
    "Energy": 0.07,
    "Transport": 0.07,
    "Health": 0.08,
    "Education": 0.04,
    "Finance": 0.02,
    "DigitalPlatform": 0.07,
    "ProfessionalServices": 0.04,
    "Exportables": 0.01,
    "GovernmentSupply": 0.00,
}

# Stylized input-output requirements: sector -> inputs as share of output value.
INPUT_OUTPUT = {
    "Food": {"Energy": 0.07, "Transport": 0.05, "Manufacturing": 0.03},
    "Retail": {"Transport": 0.04, "DigitalPlatform": 0.03, "Energy": 0.03},
    "Manufacturing": {"Energy": 0.12, "Transport": 0.05, "ProfessionalServices": 0.03},
    "Construction": {"Manufacturing": 0.12, "Energy": 0.06, "Transport": 0.05, "ProfessionalServices": 0.02},
    "HousingServices": {"Energy": 0.03, "ProfessionalServices": 0.02},
    "Energy": {"Manufacturing": 0.05, "Transport": 0.04, "ProfessionalServices": 0.02},
    "Transport": {"Energy": 0.18, "Manufacturing": 0.04},
    "Health": {"Energy": 0.04, "Manufacturing": 0.04, "ProfessionalServices": 0.03},
    "Education": {"Energy": 0.03, "DigitalPlatform": 0.03, "ProfessionalServices": 0.02},
    "Finance": {"DigitalPlatform": 0.05, "ProfessionalServices": 0.04, "Energy": 0.01},
    "DigitalPlatform": {"Energy": 0.10, "ProfessionalServices": 0.05},
    "ProfessionalServices": {"DigitalPlatform": 0.06, "Energy": 0.02},
    "Exportables": {"Energy": 0.12, "Transport": 0.09, "Manufacturing": 0.08},
    "GovernmentSupply": {"Energy": 0.05, "Transport": 0.03, "ProfessionalServices": 0.05},
}

ENERGY_INTENSITY = {
    "Food": 0.06,
    "Retail": 0.03,
    "Manufacturing": 0.13,
    "Construction": 0.09,
    "HousingServices": 0.03,
    "Energy": 0.08,
    "Transport": 0.18,
    "Health": 0.04,
    "Education": 0.03,
    "Finance": 0.02,
    "DigitalPlatform": 0.11,
    "ProfessionalServices": 0.02,
    "Exportables": 0.12,
    "GovernmentSupply": 0.05,
}

EMISSIONS_INTENSITY = {
    "Food": 0.08,
    "Retail": 0.03,
    "Manufacturing": 0.18,
    "Construction": 0.14,
    "HousingServices": 0.04,
    "Energy": 0.35,
    "Transport": 0.28,
    "Health": 0.05,
    "Education": 0.03,
    "Finance": 0.02,
    "DigitalPlatform": 0.06,
    "ProfessionalServices": 0.02,
    "Exportables": 0.20,
    "GovernmentSupply": 0.06,
}

INITIAL_PRICE = {
    "Food": 1.00,
    "Retail": 1.10,
    "Manufacturing": 1.25,
    "Construction": 1.40,
    "HousingServices": 1.20,
    "Energy": 1.00,
    "Transport": 1.05,
    "Health": 1.20,
    "Education": 1.10,
    "Finance": 1.30,
    "DigitalPlatform": 1.00,
    "ProfessionalServices": 1.35,
    "Exportables": 1.20,
    "GovernmentSupply": 1.10,
}

REGION_PRODUCTIVITY = {
    "Capital": 1.18,
    "North": 1.02,
    "South": 0.96,
    "East": 0.93,
    "West": 1.06,
    "Rural": 0.86,
}

REGION_HOUSING_SCARCITY = {
    "Capital": 1.45,
    "North": 1.02,
    "South": 0.96,
    "East": 0.90,
    "West": 1.10,
    "Rural": 0.72,
}

REGION_POP_WEIGHTS = {
    "Capital": 0.21,
    "North": 0.17,
    "South": 0.17,
    "East": 0.14,
    "West": 0.20,
    "Rural": 0.11,
}


# The second currency judges planetary/resource correctness, not merely profit.
# These stylized resource channels are intentionally broad: physical energy,
# material throughput, land, ecological sink capacity, human attention, and data.
RESOURCE_TYPES = [
    "fossil_energy",
    "renewable_energy",
    "carbon_budget",
    "water",
    "materials",
    "land",
    "biodiversity",
    "waste_capacity",
    "labor_attention",
    "data_privacy",
]

# Fuzzy allowed ranges per aggregate resource. The lower bound is the minimum
# acceptable truth value; below it, the resource predicate is treated as falsified
# and cross-resource throttling becomes severe.
RESOURCE_ALLOWED_TRUTH_RANGE = {
    "fossil_energy": (0.20, 1.00),
    "renewable_energy": (0.30, 1.00),
    "carbon_budget": (0.25, 1.00),
    "water": (0.30, 1.00),
    "materials": (0.25, 1.00),
    "land": (0.30, 1.00),
    "biodiversity": (0.35, 1.00),
    "waste_capacity": (0.25, 1.00),
    "labor_attention": (0.20, 1.00),
    "data_privacy": (0.35, 1.00),
}

# Population-scaled monthly baseline quota. The resource market tightens this
# quota when any one resource is overused.
RESOURCE_BASE_QUOTA_PER_HOUSEHOLD = {
    # Calibrated so baseline is not automatically collapsed, while energy/
    # climate/supply shocks still push resources into falsification ranges.
    "fossil_energy": 0.800,
    "renewable_energy": 0.400,
    "carbon_budget": 0.650,
    "water": 0.550,
    "materials": 0.750,
    "land": 0.350,
    "biodiversity": 0.320,
    "waste_capacity": 0.600,
    "labor_attention": 0.220,
    "data_privacy": 0.160,
}

# Abstract resource intensities per unit of firm output. These are not empirical;
# they are designed to make the causal mechanics inspectable.
SECTOR_TRUTH_RESOURCE_INTENSITY = {
    "Food": {"fossil_energy": 0.030, "renewable_energy": 0.018, "carbon_budget": 0.055, "water": 0.200, "materials": 0.100, "land": 0.180, "biodiversity": 0.160, "waste_capacity": 0.090, "labor_attention": 0.035, "data_privacy": 0.003},
    "Retail": {"fossil_energy": 0.025, "renewable_energy": 0.014, "carbon_budget": 0.030, "water": 0.050, "materials": 0.130, "land": 0.050, "biodiversity": 0.040, "waste_capacity": 0.130, "labor_attention": 0.050, "data_privacy": 0.020},
    "Manufacturing": {"fossil_energy": 0.090, "renewable_energy": 0.040, "carbon_budget": 0.095, "water": 0.150, "materials": 0.340, "land": 0.070, "biodiversity": 0.070, "waste_capacity": 0.220, "labor_attention": 0.040, "data_privacy": 0.004},
    "Construction": {"fossil_energy": 0.070, "renewable_energy": 0.030, "carbon_budget": 0.070, "water": 0.100, "materials": 0.420, "land": 0.180, "biodiversity": 0.120, "waste_capacity": 0.240, "labor_attention": 0.050, "data_privacy": 0.003},
    "HousingServices": {"fossil_energy": 0.030, "renewable_energy": 0.020, "carbon_budget": 0.030, "water": 0.060, "materials": 0.060, "land": 0.150, "biodiversity": 0.050, "waste_capacity": 0.050, "labor_attention": 0.030, "data_privacy": 0.004},
    "Energy": {"fossil_energy": 0.160, "renewable_energy": 0.095, "carbon_budget": 0.165, "water": 0.180, "materials": 0.180, "land": 0.080, "biodiversity": 0.100, "waste_capacity": 0.180, "labor_attention": 0.030, "data_privacy": 0.004},
    "Transport": {"fossil_energy": 0.100, "renewable_energy": 0.025, "carbon_budget": 0.105, "water": 0.040, "materials": 0.190, "land": 0.080, "biodiversity": 0.080, "waste_capacity": 0.160, "labor_attention": 0.050, "data_privacy": 0.007},
    "Health": {"fossil_energy": 0.045, "renewable_energy": 0.030, "carbon_budget": 0.040, "water": 0.100, "materials": 0.140, "land": 0.040, "biodiversity": 0.030, "waste_capacity": 0.160, "labor_attention": 0.095, "data_privacy": 0.015},
    "Education": {"fossil_energy": 0.025, "renewable_energy": 0.018, "carbon_budget": 0.025, "water": 0.050, "materials": 0.060, "land": 0.040, "biodiversity": 0.020, "waste_capacity": 0.040, "labor_attention": 0.115, "data_privacy": 0.012},
    "Finance": {"fossil_energy": 0.020, "renewable_energy": 0.018, "carbon_budget": 0.018, "water": 0.030, "materials": 0.040, "land": 0.030, "biodiversity": 0.020, "waste_capacity": 0.030, "labor_attention": 0.070, "data_privacy": 0.030},
    "DigitalPlatform": {"fossil_energy": 0.035, "renewable_energy": 0.060, "carbon_budget": 0.030, "water": 0.080, "materials": 0.150, "land": 0.030, "biodiversity": 0.030, "waste_capacity": 0.080, "labor_attention": 0.055, "data_privacy": 0.095},
    "ProfessionalServices": {"fossil_energy": 0.018, "renewable_energy": 0.018, "carbon_budget": 0.016, "water": 0.040, "materials": 0.050, "land": 0.030, "biodiversity": 0.020, "waste_capacity": 0.040, "labor_attention": 0.080, "data_privacy": 0.020},
    "Exportables": {"fossil_energy": 0.070, "renewable_energy": 0.030, "carbon_budget": 0.075, "water": 0.140, "materials": 0.300, "land": 0.080, "biodiversity": 0.080, "waste_capacity": 0.190, "labor_attention": 0.040, "data_privacy": 0.006},
    "GovernmentSupply": {"fossil_energy": 0.040, "renewable_energy": 0.025, "carbon_budget": 0.040, "water": 0.080, "materials": 0.100, "land": 0.060, "biodiversity": 0.040, "waste_capacity": 0.080, "labor_attention": 0.075, "data_privacy": 0.012},
}

HOUSEHOLD_TRUTH_RESOURCE_INTENSITY = {
    "fossil_energy": 0.012,
    "renewable_energy": 0.010,
    "carbon_budget": 0.012,
    "water": 0.018,
    "materials": 0.010,
    "land": 0.006,
    "biodiversity": 0.004,
    "waste_capacity": 0.009,
    "labor_attention": 0.020,
    "data_privacy": 0.006,
}

# Safe/warning/hard multipliers over expected use for local actor predicates.
RESOURCE_RANGE_MULTIPLIER = {
    "fossil_energy": (0.78, 1.00, 1.22),
    "renewable_energy": (1.30, 1.75, 2.30),
    "carbon_budget": (0.70, 0.95, 1.20),
    "water": (0.82, 1.05, 1.32),
    "materials": (0.82, 1.05, 1.30),
    "land": (0.78, 1.00, 1.24),
    "biodiversity": (0.72, 0.95, 1.16),
    "waste_capacity": (0.78, 1.05, 1.34),
    "labor_attention": (0.75, 1.02, 1.30),
    "data_privacy": (0.72, 0.96, 1.18),
}

# Regions are split into two stylized economies/countries.  Country A calls
# benevolence 0°, country B calls it 90°. The negotiated common good is 45°.
ANGLE_STATE_A_REGIONS = {"Capital", "North", "West"}
ANGLE_STATE_B_REGIONS = {"South", "East", "Rural"}

SECTOR_BASE_ANGLE = {
    "Food": 52.0,
    "Retail": 72.0,
    "Manufacturing": 88.0,
    "Construction": 96.0,
    "HousingServices": 82.0,
    "Energy": 132.0,
    "Transport": 102.0,
    "Health": 34.0,
    "Education": 28.0,
    "Finance": 76.0,
    "DigitalPlatform": 118.0,
    "ProfessionalServices": 58.0,
    "Exportables": 92.0,
    "GovernmentSupply": 44.0,
}

RESOURCE_BASE_ANGLE = {
    "fossil_energy": 165.0,
    "renewable_energy": 38.0,
    "carbon_budget": 155.0,
    "water": 46.0,
    "materials": 88.0,
    "land": 74.0,
    "biodiversity": 34.0,
    "waste_capacity": 118.0,
    "labor_attention": 62.0,
    "data_privacy": 132.0,
}

PURPOSE_BASE_ANGLE = {
    "wage": 42.0,
    "labor": 45.0,
    "education": 30.0,
    "knowledge": 30.0,
    "health": 34.0,
    "green": 36.0,
    "renewable": 36.0,
    "carbon_rebate": 38.0,
    "public": 45.0,
    "transfer": 48.0,
    "pension": 50.0,
    "basic_transfer": 48.0,
    "tax": 58.0,
    "carbon_tax": 44.0,
    "rent": 96.0,
    "mortgage": 88.0,
    "home": 72.0,
    "credit": 80.0,
    "loan": 86.0,
    "deposit": 70.0,
    "default": 215.0,
    "bankruptcy": 212.0,
    "bailout": 135.0,
    "fossil": 170.0,
    "emissions": 174.0,
    "platform": 132.0,
    "data": 142.0,
    "insurance": 50.0,
    "truth": 45.0,
    "audit": 42.0,
    "model": 45.0,
    "import": 110.0,
    "export": 78.0,
    "consumption": 72.0,
    "sale": 72.0,
    "investment": 62.0,
}


# ---------------------------------------------------------------------------
# Configuration and event logging
# ---------------------------------------------------------------------------


@dataclass
class SimulationConfig:
    seed: int = 42
    steps: int = 60
    households: int = 300
    firms: int = 80
    banks: int = 5
    scenario: str = "baseline"
    policy_mode: str = "balanced"  # balanced, hawkish, dovish, austerity, stimulus, green
    currency_name: str = "ECU"
    truth_currency_name: str = "LOGOS"
    truth_market_enabled: bool = True
    truth_money_scale: float = 80.0
    truth_resource_strictness: float = 1.0
    truth_verification_depth: int = 3
    truth_public_audit_rate: float = 0.055
    truth_negative_credit_penalty: float = 0.25
    truth_trade_intensity: float = 0.18
    truth_cross_resource_penalty: float = 0.78
    truth_to_fiat_fx: float = 1.0
    angle_currency_name: str = "ARETE"
    angle_market_enabled: bool = True
    angle_money_scale: float = 42.0
    angle_trade_intensity: float = 0.14
    angle_to_fiat_fx: float = 1.0
    angle_state_a_good: float = ANGLE_STATE_A_GOOD_DEG
    angle_state_b_good: float = ANGLE_STATE_B_GOOD_DEG
    angle_objective_good: float = ANGLE_OBJECTIVE_GOOD_DEG
    angle_popularity_weight: float = 0.22
    angle_truth_weight: float = 0.42
    angle_resource_weight: float = 0.35
    angle_moral_credit_bonus: float = 0.020
    initial_policy_rate: float = 0.025
    inflation_target: float = 0.02 / 12.0
    natural_unemployment: float = 0.055
    income_tax: float = 0.20
    corporate_tax: float = 0.20
    vat: float = 0.12
    capital_tax: float = 0.08
    property_tax: float = 0.006 / 12.0
    carbon_price: float = 0.03
    unemployment_benefit_replacement: float = 0.42
    basic_transfer: float = 0.0
    public_education_intensity: float = 1.00
    public_health_intensity: float = 1.00
    green_subsidy: float = 0.00
    infrastructure_intensity: float = 1.00
    bank_capital_requirement: float = 0.085
    max_household_loan_to_income: float = 4.5
    max_mortgage_ltv: float = 0.85
    labor_mobility: float = 0.16
    construction_lag: int = 8
    open_economy: bool = True
    verbose: bool = False
    shock_compound: str = ""  # comma-separated extra shock names
    calibration_note: str = "stylized-defaults"


@dataclass
class EventLog:
    messages: List[str] = field(default_factory=list)

    def add(self, t: int, msg: str) -> None:
        self.messages.append(f"t={t:04d}: {msg}")

    def recent(self, n: int = 10) -> List[str]:
        return self.messages[-n:]


# ---------------------------------------------------------------------------
# Agent data structures
# ---------------------------------------------------------------------------


@dataclass
class Loan:
    loan_id: int
    bank_id: int
    borrower_kind: str  # household, firm, government
    borrower_id: int
    principal: float
    rate: float
    maturity: int
    collateral_value: float
    purpose: str
    age: int = 0
    delinquency: int = 0
    status: str = "performing"

    def scheduled_payment(self) -> float:
        if self.principal <= EPS or self.status != "performing":
            return 0.0
        amort = self.principal / max(1, self.maturity - self.age)
        interest = self.principal * self.rate / 12.0
        return amort + interest

    def interest_due(self) -> float:
        if self.principal <= EPS or self.status != "performing":
            return 0.0
        return self.principal * self.rate / 12.0


@dataclass
class Household:
    hid: int
    region: str
    age: int
    education: float
    skill: float
    health: float
    risk_aversion: float
    patience: float
    preference_shift: Dict[str, float]
    bank_id: int
    cash: float
    debt: float
    mortgage: float
    home_owner: bool
    home_value: float
    rent_payment: float
    asset_portfolio: float
    pension_wealth: float
    employed: bool = False
    employer_id: Optional[int] = None
    wage: float = 0.0
    last_income: float = 0.0
    last_consumption: float = 0.0
    last_taxes: float = 0.0
    unemployment_duration: int = 0
    children: int = 0
    energy_efficiency: float = 1.0
    insured_health: bool = True
    defaulted: bool = False
    migration_desire: float = 0.0
    platform_user: bool = True
    social_capital: float = 1.0
    truth_balance: Fraction = field(default_factory=truth_zero)
    truth_debt: Fraction = field(default_factory=truth_zero)
    knowledge_assets: Fraction = field(default_factory=truth_zero)
    last_truth_flow: Fraction = field(default_factory=truth_zero)
    last_resource_truth: Fraction = field(default_factory=truth_zero)
    truth_score: float = 0.0
    verification_skill: float = 0.0
    angle_balance: float = 0.0
    angle_debt: float = 0.0
    angle_position: float = ANGLE_OBJECTIVE_GOOD_DEG
    angle_reputation: float = 0.0
    last_angle_flow: float = 0.0
    angle_country_good: float = ANGLE_OBJECTIVE_GOOD_DEG

    def labor_productivity(self) -> float:
        age_factor = 1.0
        if self.age < 23:
            age_factor = 0.82
        elif self.age > 58:
            age_factor = 0.90
        elif self.age > 66:
            age_factor = 0.40
        return max(0.05, self.skill * (0.55 + 0.45 * self.education) * (0.55 + 0.45 * self.health) * age_factor)

    def labor_force_member(self) -> bool:
        return 18 <= self.age <= 67 and self.health > 0.18

    def wealth(self) -> float:
        return max(0.0, self.cash) + max(0.0, self.asset_portfolio) + max(0.0, self.pension_wealth) + max(0.0, self.home_value) - max(0.0, self.debt) - max(0.0, self.mortgage)

    def liquidity_need(self) -> float:
        return 0.35 * self.last_income + 2.0 + self.children * 0.4

    def propensity_to_consume(self, macro_uncertainty: float) -> float:
        wealth_buffer = safe_div(self.cash, self.liquidity_need(), 0.0)
        base = 0.82 - 0.12 * self.patience + 0.08 * self.children
        if not self.employed:
            base += 0.05
        base -= 0.14 * clamp(wealth_buffer, 0.0, 5.0)
        base -= 0.10 * macro_uncertainty
        return clamp(base, 0.35, 0.97)

    def sector_preference(self, sector: str, energy_price: float, cpi: float) -> float:
        base = BASE_CONSUMPTION_PREFS.get(sector, 0.0)
        shift = self.preference_shift.get(sector, 1.0)
        # Poor households have less discretionary spending.
        if self.cash < self.liquidity_need():
            if sector in {"DigitalPlatform", "ProfessionalServices", "Retail"}:
                shift *= 0.78
            if sector in {"Food", "HousingServices", "Energy"}:
                shift *= 1.10
        if sector == "Energy" and energy_price > cpi * 1.25:
            shift *= 0.92 * self.energy_efficiency
        return max(0.0, base * shift)


@dataclass
class Firm:
    fid: int
    sector: str
    region: str
    productivity: float
    capital: float
    cash: float
    debt: float
    bank_id: int
    wage_offer: float
    price: float
    markup: float
    quality: float
    innovation: float
    automation: float
    market_power: float
    energy_intensity: float
    emissions_intensity: float
    exporter_share: float
    platform_dependency: float
    supplier_ids: List[int] = field(default_factory=list)
    employees: List[int] = field(default_factory=list)
    desired_labor: int = 0
    inventory: float = 0.0
    output: float = 0.0
    expected_demand: float = 10.0
    last_revenue: float = 0.0
    last_cost: float = 0.0
    last_profit: float = 0.0
    last_quantity_sold: float = 0.0
    last_unfilled_demand: float = 0.0
    last_wage_bill: float = 0.0
    last_energy_bill: float = 0.0
    last_input_bill: float = 0.0
    last_tax: float = 0.0
    bankrupt: bool = False
    age: int = 0
    default_count: int = 0
    supply_chain_fragility: float = 0.0
    truth_balance: Fraction = field(default_factory=truth_zero)
    truth_debt: Fraction = field(default_factory=truth_zero)
    knowledge_assets: Fraction = field(default_factory=truth_zero)
    model_reputation: float = 0.0
    resource_penalty: float = 1.0
    resource_overuse_score: float = 0.0
    last_resource_truth: Fraction = field(default_factory=truth_zero)
    last_truth_flow: Fraction = field(default_factory=truth_zero)
    last_truth_model_sales: float = 0.0
    last_truth_model_buys: float = 0.0
    last_resource_usage: Dict[str, float] = field(default_factory=dict)
    angle_balance: float = 0.0
    angle_debt: float = 0.0
    angle_position: float = ANGLE_OBJECTIVE_GOOD_DEG
    angle_reputation: float = 0.0
    last_angle_flow: float = 0.0
    angle_country_good: float = ANGLE_OBJECTIVE_GOOD_DEG

    def alive(self) -> bool:
        return not self.bankrupt

    def target_markup(self, concentration: float, demand_pressure: float, policy_pressure: float = 0.0) -> float:
        sector_base = 0.12
        if self.sector in LOW_MARGIN_SECTORS:
            sector_base = 0.08
        if self.sector in HIGH_SKILL_SECTORS:
            sector_base = 0.16
        if self.sector == "DigitalPlatform":
            sector_base = 0.22
        return clamp(sector_base + 0.25 * self.market_power + 0.12 * concentration + 0.05 * demand_pressure - policy_pressure, 0.03, 0.55)

    def production_capacity(self, labor_effort: float, energy_constraint: float, supply_constraint: float) -> float:
        cap_term = max(0.1, self.capital) ** (0.28 if self.sector in CAPITAL_HEAVY_SECTORS else 0.18)
        labor_term = max(0.1, labor_effort * (1.0 + 0.55 * self.automation)) ** (0.72 if self.sector not in CAPITAL_HEAVY_SECTORS else 0.60)
        platform_bonus = 1.0 + (0.18 * self.market_power if self.sector == "DigitalPlatform" else 0.0)
        innov_bonus = 1.0 + 0.25 * self.innovation
        scale = 4.25  # turns abstract labor/capital into marketable monthly output units
        return max(0.0, scale * self.productivity * cap_term * labor_term * energy_constraint * supply_constraint * platform_bonus * innov_bonus)

    def leverage(self) -> float:
        return safe_div(self.debt, max(1.0, self.capital + self.cash), 0.0)


@dataclass
class Bank:
    bid: int
    region: str
    equity: float
    reserves: float
    deposits: float
    risk_appetite: float
    operating_cost_rate: float
    loan_book: Dict[int, Loan] = field(default_factory=dict)
    npl_losses: float = 0.0
    last_interest_income: float = 0.0
    last_deposit_cost: float = 0.0
    last_new_credit: float = 0.0
    last_writeoffs: float = 0.0
    liquidity_support: float = 0.0
    failed: bool = False
    truth_balance: Fraction = field(default_factory=truth_zero)
    truth_debt: Fraction = field(default_factory=truth_zero)
    audit_quality: float = 0.55
    truth_reserves: Fraction = field(default_factory=truth_zero)
    last_truth_flow: Fraction = field(default_factory=truth_zero)
    angle_balance: float = 0.0
    angle_debt: float = 0.0
    angle_position: float = ANGLE_OBJECTIVE_GOOD_DEG
    angle_reputation: float = 0.0
    last_angle_flow: float = 0.0
    angle_country_good: float = ANGLE_OBJECTIVE_GOOD_DEG

    def performing_loans(self) -> List[Loan]:
        return [ln for ln in self.loan_book.values() if ln.status == "performing" and ln.principal > EPS]

    def total_loans(self) -> float:
        return sum(ln.principal for ln in self.loan_book.values() if ln.status == "performing")

    def risk_weighted_assets(self) -> float:
        total = 0.0
        for ln in self.performing_loans():
            w = 1.0
            if ln.purpose == "mortgage":
                w = 0.55
            elif ln.borrower_kind == "government":
                w = 0.20
            elif ln.purpose == "working_capital":
                w = 0.95
            elif ln.purpose == "green_investment":
                w = 0.75
            total += ln.principal * w
        return total

    def capital_ratio(self) -> float:
        return safe_div(self.equity, self.risk_weighted_assets(), 1.0)

    def liquidity_ratio(self) -> float:
        return safe_div(self.reserves, self.deposits, 1.0)

    def credit_tightness(self, capital_requirement: float, stress: float) -> float:
        cap_gap = capital_requirement - self.capital_ratio()
        liq_gap = 0.05 - self.liquidity_ratio()
        return clamp(0.25 + 2.8 * max(0.0, cap_gap) + 1.8 * max(0.0, liq_gap) + 0.75 * stress - 0.30 * self.risk_appetite, 0.0, 1.0)


# ---------------------------------------------------------------------------
# Institutions and market state
# ---------------------------------------------------------------------------


@dataclass
class CentralBank:
    policy_rate: float
    target_inflation: float
    neutral_rate: float = 0.025
    inflation_response: float = 1.25
    unemployment_response: float = 0.75
    financial_stress_response: float = 0.90
    min_rate: float = -0.005
    max_rate: float = 0.18
    liquidity_facility_rate: float = 0.04
    qe_strength: float = 0.0

    def update(self, inflation: float, unemployment: float, financial_stress: float, config: SimulationConfig) -> None:
        hawkish = 1.0
        dovish = 1.0
        if config.policy_mode == "hawkish":
            hawkish = 1.45
            dovish = 0.65
        elif config.policy_mode == "dovish":
            hawkish = 0.70
            dovish = 1.40
        elif config.policy_mode == "stimulus":
            hawkish = 0.80
            dovish = 1.30
        inflation_gap = inflation - self.target_inflation
        unemployment_gap = unemployment - config.natural_unemployment
        target = (
            self.neutral_rate
            + hawkish * self.inflation_response * inflation_gap
            - dovish * self.unemployment_response * unemployment_gap
            - self.financial_stress_response * financial_stress
        )
        smoothing = 0.82
        self.policy_rate = clamp(smoothing * self.policy_rate + (1.0 - smoothing) * target, self.min_rate, self.max_rate)
        self.liquidity_facility_rate = clamp(self.policy_rate + 0.020 + 0.060 * financial_stress, 0.0, 0.25)
        self.qe_strength = clamp(0.60 * financial_stress + 0.20 * max(0.0, unemployment_gap), 0.0, 1.0)


@dataclass
class Government:
    income_tax: float
    corporate_tax: float
    vat: float
    capital_tax: float
    property_tax: float
    carbon_price: float
    unemployment_replacement: float
    basic_transfer: float
    debt: float = 0.0
    cash: float = 0.0
    last_revenue: float = 0.0
    last_spending: float = 0.0
    last_deficit: float = 0.0
    last_transfers: float = 0.0
    last_public_wages: float = 0.0
    last_interest_payment: float = 0.0
    last_bailouts: float = 0.0
    public_education_quality: float = 1.0
    public_health_quality: float = 1.0
    infrastructure_quality: float = 1.0
    green_subsidy: float = 0.0
    regulatory_pressure: float = 0.0
    carbon_revenue: float = 0.0
    truth_balance: Fraction = field(default_factory=truth_zero)
    truth_debt: Fraction = field(default_factory=truth_zero)
    planetary_trust: float = 0.55
    last_truth_flow: Fraction = field(default_factory=truth_zero)
    angle_balance: float = 0.0
    angle_debt: float = 0.0
    angle_position: float = ANGLE_OBJECTIVE_GOOD_DEG
    angle_reputation: float = 0.0
    last_angle_flow: float = 0.0
    angle_country_good: float = ANGLE_OBJECTIVE_GOOD_DEG

    def reset_flows(self) -> None:
        self.last_revenue = 0.0
        self.last_spending = 0.0
        self.last_deficit = 0.0
        self.last_transfers = 0.0
        self.last_public_wages = 0.0
        self.last_interest_payment = 0.0
        self.last_bailouts = 0.0
        self.carbon_revenue = 0.0

    def collect(self, amount: float) -> None:
        amount = max(0.0, amount)
        self.cash += amount
        self.last_revenue += amount

    def spend(self, amount: float) -> None:
        amount = max(0.0, amount)
        self.cash -= amount
        self.last_spending += amount

    def finalize_budget(self, cb_rate: float, gdp: float) -> None:
        interest = max(0.0, self.debt) * max(0.0, cb_rate + 0.005) / 12.0
        self.cash -= interest
        self.last_spending += interest
        self.last_interest_payment = interest
        deficit = -self.cash
        if deficit > 0:
            self.debt += deficit
            self.cash = 0.0
        elif self.cash > 0:
            repay = min(self.cash, self.debt * 0.01)
            self.debt -= repay
            self.cash -= repay
        self.last_deficit = self.last_spending - self.last_revenue
        # If debt gets large, regulatory pressure/fiscal constraint rises.
        debt_ratio = safe_div(self.debt, max(1.0, gdp * 12.0), 0.0)
        self.regulatory_pressure = clamp(0.02 * max(0.0, debt_ratio - 0.8), 0.0, 0.08)


@dataclass
class EnergyMarket:
    fossil_price: float = 1.0
    energy_price: float = 1.0
    fossil_capacity: float = 1000.0
    renewable_capacity: float = 280.0
    storage_capacity: float = 80.0
    grid_reliability: float = 0.96
    renewable_share: float = 0.25
    last_demand: float = 300.0
    last_supply: float = 320.0
    shortage_ratio: float = 0.0
    emissions: float = 0.0
    green_investment: float = 0.0
    volatility_state: float = 0.0

    def available_supply(self) -> float:
        renew = self.renewable_capacity * (0.80 + 0.20 * self.grid_reliability)
        fossil = self.fossil_capacity
        return max(1.0, renew + fossil + 0.35 * self.storage_capacity)

    def pre_step_update(self, rng: random.Random, government: Government, scenario_pressure: float) -> None:
        self.volatility_state = correlated_noise(rng, self.volatility_state, 0.72, 0.018 + 0.04 * scenario_pressure)
        capacity = self.available_supply()
        demand_pressure = safe_div(self.last_demand, capacity, 0.85)
        shortage = clamp(demand_pressure - 1.0, 0.0, 0.80)
        self.shortage_ratio = 0.65 * self.shortage_ratio + 0.35 * shortage
        fossil_component = self.fossil_price * (1.0 - self.renewable_share)
        renewable_component = 0.62 * self.renewable_share
        carbon_component = government.carbon_price * (1.0 - self.renewable_share) * 2.5
        reliability_premium = 0.20 * max(0.0, 0.92 - self.grid_reliability)
        self.energy_price = max(
            0.20,
            fossil_component + renewable_component + carbon_component + 0.80 * self.shortage_ratio + reliability_premium + self.volatility_state,
        )

    def post_step_update(self, demand: float, output_energy_sector: float, emissions: float, green_investment: float) -> None:
        self.last_demand = max(1.0, demand)
        self.last_supply = max(1.0, output_energy_sector + self.available_supply())
        self.emissions = emissions
        self.green_investment = green_investment
        # Green investment takes time but steadily improves renewable capacity and reliability.
        self.renewable_capacity += 0.012 * green_investment
        self.storage_capacity += 0.004 * green_investment
        self.fossil_capacity *= 0.9996
        self.renewable_share = clamp(self.renewable_capacity / max(1.0, self.renewable_capacity + self.fossil_capacity), 0.0, 0.95)
        self.grid_reliability = clamp(self.grid_reliability + 0.00002 * green_investment - 0.0008 * self.shortage_ratio, 0.75, 0.995)


@dataclass
class HousingMarket:
    price_index: Dict[str, float]
    rent_index: Dict[str, float]
    stock: Dict[str, float]
    vacancies: Dict[str, float]
    construction_pipeline: Dict[str, Deque[float]]
    affordability: Dict[str, float] = field(default_factory=dict)
    last_transactions: int = 0
    last_new_units: float = 0.0

    @staticmethod
    def create(config: SimulationConfig) -> "HousingMarket":
        stock = {}
        price = {}
        rent = {}
        vacancies = {}
        pipeline = {}
        households_by_region = config.households / len(REGIONS)
        for region in REGIONS:
            scarcity = REGION_HOUSING_SCARCITY[region]
            stock[region] = households_by_region * 1.08 / scarcity
            price[region] = 160.0 * scarcity
            rent[region] = 1.25 * scarcity
            vacancies[region] = max(1.0, stock[region] * 0.04)
            pipeline[region] = deque([0.0 for _ in range(config.construction_lag)], maxlen=config.construction_lag)
        return HousingMarket(price, rent, stock, vacancies, pipeline)

    def update(self, world: "EconomicWorld", construction_output_by_region: Dict[str, float]) -> None:
        self.last_new_units = 0.0
        transactions = 0
        mortgage_rate = world.central_bank.policy_rate + 0.022 + world.financial_market.credit_spread
        for region in REGIONS:
            # Construction output is transformed into units with lag.
            new_starts = max(0.0, construction_output_by_region.get(region, 0.0)) * 0.03 * world.government.infrastructure_quality
            pipe = self.construction_pipeline[region]
            if pipe.maxlen == 0:
                completed = new_starts
            else:
                pipe.append(new_starts)
                completed = pipe[0]
            self.stock[region] += completed
            self.last_new_units += completed

            pop = sum(1 for h in world.households if h.region == region)
            renter_count = sum(1 for h in world.households if h.region == region and not h.home_owner)
            demand = pop * 1.00
            vacancy = max(0.0, self.stock[region] - demand)
            self.vacancies[region] = vacancy
            vacancy_rate = safe_div(vacancy, self.stock[region], 0.02)
            income_region = mean((h.last_income for h in world.households if h.region == region), 1.0)
            credit_ease = clamp(1.0 - 8.0 * mortgage_rate - world.financial_market.financial_stress, 0.2, 1.4)
            scarcity_pressure = clamp(0.06 - vacancy_rate, -0.06, 0.12)
            income_pressure = 0.0007 * (income_region - 8.0)
            price_change = 0.006 * credit_ease + scarcity_pressure + income_pressure - 0.02 * world.financial_market.asset_crash_pressure
            rent_change = 0.45 * scarcity_pressure + 0.0004 * (income_region - 8.0)
            self.price_index[region] *= max(0.86, 1.0 + clamp(price_change, -0.08, 0.10))
            self.rent_index[region] *= max(0.90, 1.0 + clamp(rent_change, -0.04, 0.06))
            self.affordability[region] = safe_div(self.rent_index[region] * 12.0, max(1.0, income_region * 12.0), 1.0)

            for h in world.households:
                if h.region != region:
                    continue
                if h.home_owner:
                    h.home_value *= max(0.90, 1.0 + clamp(price_change, -0.10, 0.12))
                else:
                    h.rent_payment = self.rent_index[region] * (0.85 + 0.35 * h.children + 0.25 * h.social_capital)
                    # Purchase attempt for liquid, employed households.
                    if h.employed and h.cash > self.price_index[region] * 0.18 and h.age < 58:
                        desire = logistic(1.4 * h.patience + 0.004 * h.cash - 2.3 * mortgage_rate - 0.7 * self.affordability[region])
                        if world.rng.random() < 0.010 * desire and self.vacancies[region] > 0.5:
                            home_price = self.price_index[region] * world.rng.uniform(0.75, 1.35)
                            down = min(h.cash * 0.35, home_price * 0.25)
                            loan_amt = home_price - down
                            if world.request_household_loan(h, loan_amt, purpose="mortgage", collateral=home_price):
                                h.cash -= down
                                if world.config.truth_market_enabled and down > EPS:
                                    home_truth = 0.20 - 0.35 * self.affordability.get(region, 0.4) + 0.15 * h.patience
                                    world.truth_market.record_money_event(world, "household", h.hid, "market", 0, down, "home_down_payment", fuzzy=clamp(home_truth, -1.0, 1.0), confidence=0.55, weight=0.25)
                                h.home_owner = True
                                h.home_value = home_price
                                h.rent_payment = 0.0
                                self.vacancies[region] -= 1.0
                                transactions += 1
        self.last_transactions = transactions


@dataclass
class ForeignSector:
    exchange_rate: float = 1.0
    import_price_index: float = 1.0
    export_demand_index: float = 1.0
    tariff_rate: float = 0.02
    capital_flow_pressure: float = 0.0
    trade_balance: float = 0.0
    last_imports: float = 0.0
    last_exports: float = 0.0
    fx_noise: float = 0.0

    def update_pre(self, rng: random.Random, policy_rate: float, inflation: float, scenario_pressure: float) -> None:
        self.fx_noise = correlated_noise(rng, self.fx_noise, 0.65, 0.012 + 0.025 * scenario_pressure)
        rate_support = 0.15 * (policy_rate - 0.025)
        inflation_drag = -0.08 * max(0.0, inflation - 0.002)
        tb_drag = -0.0002 * self.trade_balance
        change = rate_support + inflation_drag + tb_drag + self.fx_noise + self.capital_flow_pressure
        self.exchange_rate = clamp(self.exchange_rate * (1.0 + clamp(change, -0.06, 0.06)), 0.45, 1.80)
        self.import_price_index = clamp((1.0 / self.exchange_rate) * (1.0 + self.tariff_rate), 0.55, 2.50)

    def update_post(self, imports: float, exports: float) -> None:
        self.last_imports = imports
        self.last_exports = exports
        self.trade_balance = exports - imports


@dataclass
class FinancialMarket:
    stock_index: float = 100.0
    bond_yield: float = 0.03
    credit_spread: float = 0.025
    risk_premium: float = 0.04
    financial_stress: float = 0.0
    asset_crash_pressure: float = 0.0
    volatility: float = 0.05
    last_return: float = 0.0

    def update(self, rng: random.Random, world: "EconomicWorld") -> None:
        profits = [f.last_profit for f in world.firms if f.alive()]
        profit_rate = safe_div(sum(profits), max(1.0, sum(max(1.0, f.capital) for f in world.firms if f.alive())), 0.0)
        failures = world.step_firm_bankruptcies + world.step_bank_failures
        bank_cap = mean((b.capital_ratio() for b in world.banks if not b.failed), 0.1)
        npl = world.metrics_last.get("npl_ratio", 0.0)
        self.financial_stress = clamp(0.60 * npl + 0.20 * failures + 0.35 * max(0.0, 0.08 - bank_cap) + self.asset_crash_pressure, 0.0, 1.5)
        self.credit_spread = clamp(0.012 + 0.10 * self.financial_stress + 0.05 * max(0.0, world.central_bank.policy_rate - 0.04), 0.005, 0.25)
        self.bond_yield = clamp(world.central_bank.policy_rate + 0.006 + 0.015 * safe_div(world.government.debt, max(1.0, world.metrics_last.get("gdp", 1.0) * 12.0), 0.0), 0.0, 0.25)
        noise = rng.gauss(0.0, self.volatility)
        expected = 0.35 * profit_rate - 0.45 * world.central_bank.policy_rate - 0.60 * self.financial_stress + 0.12 * world.central_bank.qe_strength
        ret = clamp(expected + noise, -0.20, 0.18)
        self.stock_index = max(8.0, self.stock_index * (1.0 + ret))
        self.last_return = ret
        self.asset_crash_pressure = clamp(0.80 * self.asset_crash_pressure + max(0.0, -ret - 0.06), 0.0, 1.0)
        self.volatility = clamp(0.035 + 0.08 * self.financial_stress, 0.02, 0.18)


@dataclass
class PlatformMarket:
    user_share: float = 0.62
    take_rate: float = 0.08
    concentration: float = 0.35
    data_advantage: float = 0.40
    last_fee_revenue: float = 0.0

    def update(self, world: "EconomicWorld") -> None:
        digital_firms = [f for f in world.firms if f.alive() and f.sector == "DigitalPlatform"]
        if digital_firms:
            revenues = [max(0.0, f.last_revenue) for f in digital_firms]
            self.concentration = hhi(revenues)
            avg_quality = weighted_average(((f.quality + f.innovation, max(0.0, f.last_revenue)) for f in digital_firms), 1.0)
        else:
            self.concentration = 1.0
            avg_quality = 0.7
        network_pull = 0.025 * (avg_quality - 1.0) + 0.030 * self.data_advantage + 0.045 * self.concentration
        regulation_drag = world.government.regulatory_pressure
        self.user_share = clamp(self.user_share + network_pull - regulation_drag + world.rng.gauss(0.0, 0.004), 0.20, 0.96)
        self.take_rate = clamp(0.04 + 0.10 * self.concentration + 0.06 * self.user_share - 0.40 * regulation_drag, 0.02, 0.22)
        self.data_advantage = clamp(0.97 * self.data_advantage + 0.05 * self.user_share, 0.0, 1.0)
        # Platform fees are charged to dependent firms; digital platform firms receive them.
        fee_pool = 0.0
        for f in world.firms:
            if not f.alive() or f.sector == "DigitalPlatform":
                continue
            fee = max(0.0, f.last_revenue) * f.platform_dependency * self.take_rate
            f.cash -= fee
            f.last_cost += fee
            fee_pool += fee
            if world.config.truth_market_enabled and fee > EPS:
                platform_truth = 0.15 + 0.25 * f.platform_dependency - 0.35 * self.concentration - 0.25 * self.data_advantage
                world.truth_market.record_money_event(world, "firm", f.fid, "platform", 0, fee, "platform_fee_data_rent", fuzzy=clamp(platform_truth, -1.0, 1.0), confidence=0.55, weight=0.25)
        self.last_fee_revenue = fee_pool
        if digital_firms and fee_pool > 0:
            weights = [max(0.01, f.market_power * f.quality) for f in digital_firms]
            total = sum(weights)
            for f, w in zip(digital_firms, weights):
                platform_rev = fee_pool * w / total
                f.cash += platform_rev
                f.last_revenue += platform_rev
                if world.config.truth_market_enabled and platform_rev > EPS:
                    platform_rev_truth = 0.10 + 0.20 * f.quality + 0.15 * f.innovation - 0.30 * self.concentration
                    world.truth_market.record_money_event(world, "firm", f.fid, "market", 0, platform_rev, "platform_fee_revenue", fuzzy=clamp(platform_rev_truth, -1.0, 1.0), confidence=0.55, weight=0.20)


@dataclass
class InsuranceMarket:
    premium_rate: float = 0.035
    reserves: float = 120.0
    last_premiums: float = 0.0
    last_payouts: float = 0.0
    solvency: float = 1.0

    def update(self, world: "EconomicWorld") -> None:
        premiums = 0.0
        payouts = 0.0
        macro_health_risk = max(0.0, 1.0 - world.government.public_health_quality)
        for h in world.households:
            if h.insured_health:
                premium = max(0.02, self.premium_rate * max(1.0, h.last_income))
                premium = min(premium, max(0.0, h.cash * 0.05))
                h.cash -= premium
                premiums += premium
                if world.config.truth_market_enabled and premium > EPS:
                    world.truth_market.record_money_event(world, "household", h.hid, "insurance", 0, premium, "insurance_premium_health", fuzzy=0.35 + 0.25 * h.health, confidence=0.55, weight=0.20)
                # Payouts cover part of health shocks.
                if h.health < 0.55:
                    payout = 0.35 * (0.65 - h.health) * max(1.0, h.last_income)
                    h.cash += payout
                    payouts += payout
                    if world.config.truth_market_enabled and payout > EPS:
                        world.truth_market.record_money_event(world, "household", h.hid, "insurance", 0, payout, "insurance_payout_health", fuzzy=0.55 + 0.20 * (0.65 - h.health), confidence=0.58, weight=0.25)
            else:
                if world.rng.random() < 0.002 + 0.010 * macro_health_risk:
                    h.cash -= min(h.cash, world.rng.uniform(0.5, 2.5))
        self.reserves += premiums - payouts
        self.last_premiums = premiums
        self.last_payouts = payouts
        self.solvency = safe_div(self.reserves, max(1.0, payouts * 12.0), 1.0)
        if self.solvency < 0.6:
            self.premium_rate *= 1.02
        else:
            self.premium_rate *= 0.999
        self.premium_rate = clamp(self.premium_rate, 0.015, 0.090)



# ---------------------------------------------------------------------------
# Tradeable fuzzy-truth currency market
# ---------------------------------------------------------------------------


@dataclass
class TruthPredicate:
    """
    N-ary fuzzy logic predicate used as a currency substrate.

    A normal money flow such as "firm pays wage" becomes a predicate with
    elements such as actor, counterparty, amount, purpose, resource state, and
    time. Verification/falsification adds one more element, so a verified
    predicate has arity n+1; verification of that verification has n+2, etc.
    """

    pid: int
    time: int
    name: str
    subject_kind: str
    subject_id: int
    elements: Tuple[str, ...]
    fuzzy: Fraction
    confidence: Fraction
    monetary_amount: float = 0.0
    parent_pid: int = 0
    depth: int = 0

    def arity(self) -> int:
        return len(self.elements)

    def currency_value(self) -> Fraction:
        # Arity makes a predicate "n-stellig" as a token; confidence prevents
        # unverified statements from becoming too valuable.
        arity_weight = Fraction(max(1, self.arity()), max(1, self.depth + 1))
        return truth_clamp(self.fuzzy * self.confidence * arity_weight)

    def verified_child(self, pid: int, time: int, verifier: str, result: float, confidence_boost: float) -> "TruthPredicate":
        result_frac = rationalize(clamp(result, -1.0, 1.0))
        old = rational_float(self.fuzzy)
        # Falsification can pull a previously positive claim negative; repeated
        # verification makes the predicate deeper, not magically true.
        blended = rationalize(clamp(0.70 * old + 0.30 * rational_float(result_frac), -1.0, 1.0))
        new_conf = truth_clamp(self.confidence + rationalize(confidence_boost), 0.0, 1.0)
        return TruthPredicate(
            pid=pid,
            time=time,
            name=self.name + ".verified",
            subject_kind=self.subject_kind,
            subject_id=self.subject_id,
            elements=self.elements + (f"verification_by={verifier};result={rational_float(result_frac):.4f}",),
            fuzzy=blended,
            confidence=new_conf,
            monetary_amount=self.monetary_amount,
            parent_pid=self.pid,
            depth=self.depth + 1,
        )


@dataclass
class TruthCurrencyMarket:
    currency_name: str = "LOGOS"
    price: float = 1.0
    liquidity: float = 1.0
    pid_counter: int = 1
    predicate_log: Deque[TruthPredicate] = field(default_factory=lambda: deque(maxlen=6000))
    resource_use: Dict[str, float] = field(default_factory=lambda: {r: 0.0 for r in RESOURCE_TYPES})
    resource_quota: Dict[str, float] = field(default_factory=lambda: {r: 1.0 for r in RESOURCE_TYPES})
    resource_truth: Dict[str, float] = field(default_factory=lambda: {r: 1.0 for r in RESOURCE_TYPES})
    cross_resource_throttle: float = 1.0
    planetary_stress: float = 0.0
    correctness_index: float = 0.0
    last_trade_volume: float = 0.0
    last_fiat_volume: float = 0.0
    last_model_trade_volume: float = 0.0
    last_knowledge_trade_volume: float = 0.0
    last_verifications: int = 0
    last_predicates_created: int = 0
    total_predicates_created: int = 0
    total_verifications: int = 0
    truth_issued: Fraction = field(default_factory=truth_zero)
    truth_destroyed: Fraction = field(default_factory=truth_zero)
    model_competition_index: float = 0.0
    audit_pressure: float = 0.0

    def start_step(self, world: "EconomicWorld") -> None:
        self.resource_use = {r: 0.0 for r in RESOURCE_TYPES}
        pop_scale = max(1.0, len(world.households))
        self.resource_quota = {}
        for r in RESOURCE_TYPES:
            base = RESOURCE_BASE_QUOTA_PER_HOUSEHOLD.get(r, 0.08) * pop_scale
            # Cross-resource throttling: if one resource was overused earlier,
            # every other resource gets dramatically less allowed capacity.
            strictness = max(0.05, world.config.truth_resource_strictness)
            self.resource_quota[r] = max(0.01, (base / strictness) * self.cross_resource_throttle)
        self.resource_truth = {r: 1.0 for r in RESOURCE_TYPES}
        self.last_trade_volume = 0.0
        self.last_fiat_volume = 0.0
        self.last_model_trade_volume = 0.0
        self.last_knowledge_trade_volume = 0.0
        self.last_verifications = 0
        self.last_predicates_created = 0
        self.audit_pressure = 0.0
        # Partial recovery if the economy returns inside quotas.
        self.cross_resource_throttle = clamp(0.88 * self.cross_resource_throttle + 0.12, 0.05, 1.0)
        for h in world.households:
            h.last_truth_flow = Fraction(0, 1)
            h.last_resource_truth = Fraction(0, 1)
        for f in world.firms:
            f.last_truth_flow = Fraction(0, 1)
            f.last_resource_truth = Fraction(0, 1)
            f.last_truth_model_sales = 0.0
            f.last_truth_model_buys = 0.0
            f.last_resource_usage = {}
        for b in world.banks:
            b.last_truth_flow = Fraction(0, 1)
        world.government.last_truth_flow = Fraction(0, 1)

    def seed_initial_balances(self, world: "EconomicWorld") -> None:
        for h in world.households:
            seed = 1.2 * h.education + 0.8 * h.health + 0.5 * h.social_capital - 0.4 * h.debt
            h.truth_balance = rationalize(seed)
            h.knowledge_assets = rationalize(1.5 * h.education + 0.25 * h.social_capital)
            h.verification_skill = clamp(0.25 + 0.55 * h.education + 0.20 * h.health, 0.0, 1.0)
        for f in world.firms:
            clean = 1.0 - clamp(f.emissions_intensity + 0.25 * f.energy_intensity, 0.0, 1.6) / 1.6
            f.truth_balance = rationalize(2.0 * clean + 1.2 * f.quality + 1.6 * f.innovation - 0.4 * f.leverage())
            f.knowledge_assets = rationalize(0.8 * f.innovation + 0.5 * f.quality + 0.3 * f.automation)
            f.model_reputation = clamp(0.35 + 0.35 * f.innovation + 0.20 * clean + 0.10 * f.quality, 0.0, 1.0)
            f.resource_penalty = 1.0
        for b in world.banks:
            b.truth_balance = rationalize(2.0 * b.capital_ratio() + 0.8 * b.risk_appetite)
            b.truth_reserves = rationalize(0.5 + 0.8 * b.capital_ratio())
            b.audit_quality = clamp(0.35 + 0.40 * b.capital_ratio() + 0.20 * b.risk_appetite, 0.05, 1.0)
        world.government.truth_balance = rationalize(3.0 * world.government.public_education_quality + 2.0 * world.government.public_health_quality)
        world.government.planetary_trust = 0.55

    def actor(self, world: "EconomicWorld", kind: str, actor_id: int) -> Any:
        if kind == "household":
            return world.household_by_id(actor_id)
        if kind == "firm":
            return world.firm_by_id(actor_id)
        if kind == "bank":
            if 0 <= actor_id < len(world.banks):
                return world.banks[actor_id]
            return None
        if kind == "government":
            return world.government
        return None

    def credit_actor(self, world: "EconomicWorld", kind: str, actor_id: int, amount: Fraction, note: str = "") -> None:
        if not world.config.truth_market_enabled or amount == 0:
            return
        actor = self.actor(world, kind, actor_id)
        if actor is None or not hasattr(actor, "truth_balance"):
            return
        actor.truth_balance = truth_clamp(actor.truth_balance + amount)
        actor.last_truth_flow = truth_clamp(getattr(actor, "last_truth_flow", Fraction(0, 1)) + amount)
        if amount >= 0:
            self.truth_issued = truth_clamp(self.truth_issued + amount)
        else:
            self.truth_destroyed = truth_clamp(self.truth_destroyed - amount)
        if getattr(world.config, "angle_market_enabled", False) and getattr(world, "angle_market", None) is not None:
            amount_f = abs(rational_float(amount))
            if amount_f > EPS:
                world.angle_market.record_exchange(
                    world,
                    kind,
                    actor_id,
                    "truth_market",
                    0,
                    amount_f,
                    "logos_credit_" + (note or "truth_balance_update"),
                    truth_hint=0.50 if amount >= 0 else -0.50,
                    confidence=0.55,
                    weight=0.18,
                    currency_context=world.config.truth_currency_name,
                    issue=True,
                )

    def transfer_truth(self, world: "EconomicWorld", seller_kind: str, seller_id: int, buyer_kind: str, buyer_id: int, amount: Fraction) -> bool:
        if amount <= 0:
            return False
        seller = self.actor(world, seller_kind, seller_id)
        buyer = self.actor(world, buyer_kind, buyer_id)
        if seller is None or buyer is None:
            return False
        if not hasattr(seller, "truth_balance") or not hasattr(buyer, "truth_balance"):
            return False
        available = max(0.0, rational_float(seller.truth_balance))
        units = min(rational_float(amount), available)
        if units <= 0.0001:
            return False
        amt = rationalize(units)
        seller.truth_balance = truth_clamp(seller.truth_balance - amt)
        buyer.truth_balance = truth_clamp(buyer.truth_balance + amt)
        seller.last_truth_flow = truth_clamp(getattr(seller, "last_truth_flow", Fraction(0, 1)) - amt)
        buyer.last_truth_flow = truth_clamp(getattr(buyer, "last_truth_flow", Fraction(0, 1)) + amt)
        if getattr(world.config, "angle_market_enabled", False) and getattr(world, "angle_market", None) is not None:
            world.angle_market.record_exchange(
                world,
                seller_kind,
                seller_id,
                buyer_kind,
                buyer_id,
                units,
                "logos_truth_transfer",
                truth_hint=0.55,
                confidence=0.62,
                weight=0.35,
                currency_context=world.config.truth_currency_name,
            )
        return True

    def actor_reputation(self, world: "EconomicWorld", kind: str, actor_id: int) -> float:
        actor = self.actor(world, kind, actor_id)
        if actor is None or not hasattr(actor, "truth_balance"):
            return 0.0
        return truth_balance_score(actor.truth_balance)

    def make_predicate(
        self,
        world: "EconomicWorld",
        name: str,
        subject_kind: str,
        subject_id: int,
        elements: Sequence[str],
        fuzzy: float,
        confidence: float,
        monetary_amount: float = 0.0,
    ) -> TruthPredicate:
        pred = TruthPredicate(
            pid=self.pid_counter,
            time=world.t,
            name=name,
            subject_kind=subject_kind,
            subject_id=subject_id,
            elements=tuple(elements),
            fuzzy=rationalize(clamp(fuzzy, -1.0, 1.0)),
            confidence=rationalize(clamp(confidence, 0.0, 1.0)),
            monetary_amount=monetary_amount,
        )
        self.pid_counter += 1
        self.predicate_log.append(pred)
        self.last_predicates_created += 1
        self.total_predicates_created += 1
        return pred

    def issue_from_predicate(self, world: "EconomicWorld", pred: TruthPredicate, weight: float = 1.0) -> Fraction:
        # Every amount of fiat money can become truth-money, but not linearly;
        # log scaling prevents huge GDP flows from dominating all verification.
        money_scale = max(0.04, math.log1p(abs(pred.monetary_amount)) / max(1.0, world.config.truth_money_scale))
        units = pred.currency_value() * rationalize(money_scale * weight)
        self.credit_actor(world, pred.subject_kind, pred.subject_id, units, note=pred.name)
        return units

    def record_money_event(
        self,
        world: "EconomicWorld",
        subject_kind: str,
        subject_id: int,
        counterparty_kind: str,
        counterparty_id: int,
        amount: float,
        purpose: str,
        fuzzy: Optional[float] = None,
        confidence: float = 0.58,
        weight: float = 1.0,
        extra: Sequence[str] = (),
    ) -> Fraction:
        if not world.config.truth_market_enabled or amount <= EPS:
            return Fraction(0, 1)
        if fuzzy is None:
            fuzzy = self.default_money_truth(world, purpose, amount)
        elements = (
            f"subject={subject_kind}:{subject_id}",
            f"counterparty={counterparty_kind}:{counterparty_id}",
            f"amount={amount:.6f}:{world.config.currency_name}",
            f"purpose={purpose}",
            f"truth_price={self.price:.5f}",
            f"planetary_stress={self.planetary_stress:.5f}",
            f"t={world.t}",
        ) + tuple(extra)
        pred = self.make_predicate(world, "MoneyFlowIsRight", subject_kind, subject_id, elements, fuzzy, confidence, monetary_amount=amount)
        units = self.issue_from_predicate(world, pred, weight=weight)
        if counterparty_kind in {"household", "firm", "bank", "government"}:
            # Counterparty shares part of the truth/falsity of the transaction.
            self.credit_actor(world, counterparty_kind, counterparty_id, truth_clamp(units * Fraction(1, 3)), note="counterparty_share")
        if getattr(world.config, "angle_market_enabled", False) and getattr(world, "angle_market", None) is not None:
            world.angle_market.record_exchange(
                world,
                subject_kind,
                subject_id,
                counterparty_kind,
                counterparty_id,
                amount,
                purpose,
                truth_hint=clamp(float(fuzzy), -1.0, 1.0),
                confidence=confidence,
                weight=weight,
                currency_context=world.config.currency_name,
                extra=extra,
            )
        return units

    def default_money_truth(self, world: "EconomicWorld", purpose: str, amount: float) -> float:
        p = purpose.lower()
        base = 0.15 + 0.35 * self.correctness_index - 0.20 * self.planetary_stress
        if "wage" in p:
            base += 0.45
        if "education" in p or "knowledge" in p or "health" in p:
            base += 0.42
        if "green" in p or "renewable" in p or "carbon_rebate" in p:
            base += 0.55
        if "tax" in p or "public" in p or "transfer" in p or "pension" in p:
            base += 0.20
        if "rent" in p and world.metrics_last.get("housing_affordability", 0.4) > 0.5:
            base -= 0.25
        if "fossil" in p or "emissions" in p:
            base -= 0.45
        if "bailout" in p:
            base -= 0.15
        if "import" in p and world.foreign_sector.import_price_index > 1.25:
            base -= 0.12
        return clamp(base, -1.0, 1.0)

    def record_resource_use(
        self,
        world: "EconomicWorld",
        subject_kind: str,
        subject_id: int,
        resource: str,
        amount: float,
        expected_amount: float,
        sector: str,
        monetary_amount: float = 0.0,
    ) -> float:
        if not world.config.truth_market_enabled or amount <= EPS or resource not in RESOURCE_TYPES:
            return 0.0
        expected_amount = max(EPS, expected_amount)
        safe_m, warning_m, hard_m = RESOURCE_RANGE_MULTIPLIER.get(resource, (0.80, 1.0, 1.25))
        fuzzy = fuzzy_range(amount, expected_amount * safe_m, expected_amount * warning_m, expected_amount * hard_m)
        self.resource_use[resource] = self.resource_use.get(resource, 0.0) + amount
        pred = self.make_predicate(
            world,
            "ResourceUseWithinFuzzyQuota",
            subject_kind,
            subject_id,
            (
                f"actor={subject_kind}:{subject_id}",
                f"resource={resource}",
                f"amount={amount:.6f}",
                f"expected={expected_amount:.6f}",
                f"sector={sector}",
                f"cross_throttle={self.cross_resource_throttle:.5f}",
                f"t={world.t}",
            ),
            fuzzy,
            confidence=0.62,
            monetary_amount=monetary_amount,
        )
        units = self.issue_from_predicate(world, pred, weight=1.35)
        actor = self.actor(world, subject_kind, subject_id)
        if actor is not None:
            if hasattr(actor, "last_resource_truth"):
                actor.last_resource_truth = truth_clamp(actor.last_resource_truth + units)
            if hasattr(actor, "resource_overuse_score"):
                actor.resource_overuse_score = clamp(0.85 * actor.resource_overuse_score + 0.15 * max(0.0, -fuzzy), 0.0, 1.0)
            if hasattr(actor, "last_resource_usage"):
                actor.last_resource_usage[resource] = actor.last_resource_usage.get(resource, 0.0) + amount
        if getattr(world.config, "angle_market_enabled", False) and getattr(world, "angle_market", None) is not None:
            world.angle_market.record_exchange(
                world,
                subject_kind,
                subject_id,
                "planet",
                0,
                max(float(monetary_amount), amount),
                "resource_use_" + resource,
                truth_hint=fuzzy,
                confidence=0.62,
                weight=world.config.angle_resource_weight,
                currency_context="RESOURCE_QUOTA",
                object_angle=RESOURCE_BASE_ANGLE.get(resource, ANGLE_OBJECTIVE_GOOD_DEG),
            )
        return fuzzy

    def firm_resource_bundle(self, firm: Firm, output: float, world: "EconomicWorld") -> Dict[str, Tuple[float, float]]:
        intensities = SECTOR_TRUTH_RESOURCE_INTENSITY.get(firm.sector, {})
        bundle: Dict[str, Tuple[float, float]] = {}
        clean_bonus = clamp(1.0 + 0.65 * firm.innovation + 0.55 * firm.automation + 0.55 * firm.model_reputation, 0.60, 3.00)
        penalty = max(0.08, getattr(firm, "resource_penalty", 1.0))
        for r in RESOURCE_TYPES:
            base_intensity = intensities.get(r, 0.03)
            if r == "fossil_energy":
                actual = output * firm.energy_intensity * max(0.0, 1.0 - world.energy_market.renewable_share) * 0.42
            elif r == "renewable_energy":
                actual = output * firm.energy_intensity * world.energy_market.renewable_share * 0.38
            elif r == "carbon_budget":
                actual = output * firm.emissions_intensity * max(0.0, 1.0 - world.energy_market.renewable_share)
            elif r == "data_privacy":
                actual = output * base_intensity * (1.0 + 2.0 * firm.platform_dependency + 0.8 * (firm.sector == "DigitalPlatform"))
            elif r == "labor_attention":
                actual = max(0.0, len(firm.employees)) * base_intensity * (1.10 - 0.35 * firm.automation)
            else:
                actual = output * base_intensity
            expected = max(0.001, output * base_intensity / clean_bonus) * penalty
            bundle[r] = (actual, expected)
        return bundle

    def household_resource_bundle(self, household: Household, consumption: float, direct_energy_amount: float) -> Dict[str, Tuple[float, float]]:
        bundle: Dict[str, Tuple[float, float]] = {}
        education_bonus = 1.0 + 0.40 * household.education + 0.20 * household.energy_efficiency
        for r in RESOURCE_TYPES:
            base = HOUSEHOLD_TRUTH_RESOURCE_INTENSITY.get(r, 0.006)
            if r == "fossil_energy":
                actual = direct_energy_amount * max(0.0, 1.0 - household.energy_efficiency * 0.35)
            elif r == "renewable_energy":
                actual = direct_energy_amount * household.energy_efficiency * 0.35
            elif r == "carbon_budget":
                actual = direct_energy_amount * 0.65 / max(0.5, household.energy_efficiency)
            elif r == "data_privacy":
                actual = base * (1.0 + 2.0 * float(household.platform_user)) * max(0.5, consumption)
            elif r == "labor_attention":
                actual = base * (1.0 + household.children) * max(0.5, consumption)
            else:
                actual = base * max(0.5, consumption)
            expected = max(0.001, actual / education_bonus)
            bundle[r] = (actual, expected)
        return bundle

    def consumer_spending_truth(self, household: Household, spent: float, prefs: Dict[str, float]) -> float:
        necessity_share = safe_div(prefs.get("Food", 0.0) + prefs.get("Health", 0.0) + prefs.get("Education", 0.0), max(EPS, sum(prefs.values())), 0.0)
        energy_drag = prefs.get("Energy", 0.0) / max(EPS, sum(prefs.values()))
        platform_drag = prefs.get("DigitalPlatform", 0.0) / max(EPS, sum(prefs.values())) * (1.0 if household.platform_user else 0.4)
        affordability = clamp(spent / max(0.5, household.last_income + household.cash + 1.0), 0.0, 2.0)
        return clamp(0.15 + 0.45 * necessity_share + 0.30 * household.education - 0.25 * energy_drag - 0.18 * platform_drag - 0.20 * max(0.0, affordability - 1.0), -1.0, 1.0)

    def production_throttle_for_firm(self, firm: Firm) -> float:
        score = truth_balance_score(firm.truth_balance)
        knowledge = clamp(rational_float(firm.knowledge_assets) / 5.0, 0.0, 1.0)
        model = clamp(firm.model_reputation, 0.0, 1.0)
        overuse = clamp(firm.resource_overuse_score, 0.0, 1.0)
        angle_score = getattr(firm, "angle_reputation", 0.0)
        local = clamp(0.55 + 0.28 * score + 0.20 * knowledge + 0.22 * model + 0.12 * angle_score - 0.55 * overuse, 0.12, 1.25)
        return clamp(self.cross_resource_throttle * local, 0.05, 1.15)

    def finalize_resources(self, world: "EconomicWorld") -> None:
        violations = []
        truths = []
        for r in RESOURCE_TYPES:
            use = self.resource_use.get(r, 0.0)
            quota = max(EPS, self.resource_quota.get(r, 1.0))
            safe = quota * 0.80
            warning = quota * 1.00
            hard = quota * 1.24
            fuzzy = fuzzy_range(use, safe, warning, hard)
            self.resource_truth[r] = fuzzy
            truths.append(fuzzy)
            lo, _hi = RESOURCE_ALLOWED_TRUTH_RANGE.get(r, (0.25, 1.0))
            if fuzzy < lo:
                violations.append((r, lo - fuzzy, safe_div(use, quota, 0.0)))
            pred = self.make_predicate(
                world,
                "AggregateResourceUseWithinPlanetaryRange",
                "government",
                0,
                (f"resource={r}", f"use={use:.6f}", f"quota={quota:.6f}", f"allowed_truth_min={lo:.4f}", f"t={world.t}"),
                fuzzy,
                confidence=0.70,
                monetary_amount=max(0.0, use),
            )
            self.issue_from_predicate(world, pred, weight=0.75)
        self.correctness_index = clamp(0.5 + 0.5 * rational_float(fuzzy_stack_mean(truths)), 0.0, 1.0)
        if violations:
            severity = min(1.0, sum(v[1] for v in violations) / max(1.0, len(violations)))
            worst_ratio = max(v[2] for v in violations)
            throttle = clamp(1.0 - world.config.truth_cross_resource_penalty * (0.35 + severity + max(0.0, worst_ratio - 1.0)), 0.05, 0.95)
            self.cross_resource_throttle = min(self.cross_resource_throttle, throttle)
            self.audit_pressure = clamp(severity + 0.15 * len(violations), 0.0, 1.0)
            world.events.add(world.t, f"Truth-resource regime throttled all quotas to {self.cross_resource_throttle:.3f}; violated: {', '.join(v[0] for v in violations[:4])}.")
        self.planetary_stress = clamp(1.0 - self.correctness_index + 0.65 * (1.0 - self.cross_resource_throttle), 0.0, 1.5)
        world.government.planetary_trust = clamp(0.80 * world.government.planetary_trust + 0.20 * self.correctness_index, 0.0, 1.0)

    def verify_predicates(self, world: "EconomicWorld") -> None:
        if not self.predicate_log:
            return
        audit_budget = int(max(1, world.config.truth_public_audit_rate * len(self.predicate_log) * (0.5 + self.audit_pressure)))
        audit_budget = min(audit_budget, max(1, 12 + int(0.04 * len(world.households))))
        candidate_log = list(self.predicate_log)[-min(len(self.predicate_log), 900):]
        verifiers_h = sorted(world.households, key=lambda h: h.verification_skill + 0.3 * h.education + 0.1 * truth_balance_score(h.truth_balance), reverse=True)[: max(4, min(40, len(world.households)//8 or 4))]
        verifiers_b = [b for b in world.banks if not b.failed]
        for _ in range(audit_budget):
            if not candidate_log:
                break
            pred = world.rng.choice(candidate_log)
            if pred.depth >= world.config.truth_verification_depth:
                continue
            if verifiers_b and world.rng.random() < 0.35:
                b = world.rng.choice(verifiers_b)
                accuracy = clamp(b.audit_quality + 0.20 * truth_balance_score(b.truth_balance), 0.05, 1.0)
                verifier = f"bank:{b.bid}"
                verifier_kind, verifier_id = "bank", b.bid
            else:
                h = world.rng.choice(verifiers_h or world.households)
                accuracy = clamp(h.verification_skill + 0.15 * h.education + 0.10 * truth_balance_score(h.truth_balance), 0.05, 1.0)
                verifier = f"household:{h.hid}"
                verifier_kind, verifier_id = "household", h.hid
            trueish = rational_float(pred.fuzzy)
            audit_noise = world.rng.gauss(0.0, max(0.03, 0.34 * (1.0 - accuracy)))
            result = clamp(trueish + audit_noise, -1.0, 1.0)
            child = pred.verified_child(self.pid_counter, world.t, verifier, result, confidence_boost=0.08 + 0.18 * accuracy)
            self.pid_counter += 1
            self.predicate_log.append(child)
            self.total_verifications += 1
            self.last_verifications += 1
            # Audit labor is paid in truth and a little fiat: knowledge becomes tradeable.
            reward = child.currency_value() * rationalize(0.10 + 0.25 * accuracy)
            self.credit_actor(world, verifier_kind, verifier_id, reward, note="verification_reward")
            if verifier_kind == "household":
                vh = world.household_by_id(verifier_id)
                if vh:
                    vh.knowledge_assets = truth_clamp(vh.knowledge_assets + rationalize(0.01 + 0.04 * accuracy))
                    vh.cash += 0.003 * max(0.0, rational_float(reward)) * self.price
            elif verifier_kind == "bank":
                vb = world.banks[verifier_id]
                vb.truth_reserves = truth_clamp(vb.truth_reserves + max(Fraction(0, 1), reward))

    def trade_truth_currency(self, world: "EconomicWorld") -> None:
        if not world.config.truth_market_enabled:
            return
        firms = [f for f in world.firms if f.alive()]
        if not firms:
            return
        sellers = [f for f in firms if rational_float(f.truth_balance) > 2.5 and f.cash > -5.0]
        buyers = [f for f in firms if rational_float(f.truth_balance) < 1.0 or f.resource_overuse_score > 0.15]
        world.rng.shuffle(sellers)
        world.rng.shuffle(buyers)
        demand_pressure = safe_div(len(buyers), max(1.0, len(sellers)), 0.0)
        self.price = clamp(self.price * (1.0 + 0.020 * (demand_pressure - 1.0) + 0.035 * self.planetary_stress), 0.05, 50.0)
        max_trades = int(max(2, world.config.truth_trade_intensity * len(firms)))
        for seller, buyer in zip(sellers[:max_trades], buyers[:max_trades]):
            if seller.fid == buyer.fid:
                continue
            supply = max(0.0, rational_float(seller.truth_balance) - 2.0)
            need = max(0.0, 2.0 - rational_float(buyer.truth_balance)) + 1.5 * buyer.resource_overuse_score
            units_f = min(supply, need, world.rng.uniform(0.05, 0.60) * (1.0 + self.planetary_stress))
            if units_f <= 0.001:
                continue
            fiat_price = units_f * self.price * world.config.truth_to_fiat_fx
            if buyer.cash < fiat_price:
                fiat_price = max(0.0, buyer.cash * 0.40)
                units_f = fiat_price / max(EPS, self.price * world.config.truth_to_fiat_fx)
            if fiat_price <= EPS or units_f <= EPS:
                continue
            units = rationalize(units_f)
            if self.transfer_truth(world, "firm", seller.fid, "firm", buyer.fid, units):
                buyer.cash -= fiat_price
                seller.cash += fiat_price
                self.last_trade_volume += units_f
                self.last_fiat_volume += fiat_price
                self.record_money_event(world, "firm", buyer.fid, "firm", seller.fid, fiat_price, "truth_currency_purchase", fuzzy=0.25 + 0.50 * seller.model_reputation, confidence=0.64, weight=0.45)

    def trade_correctness_models(self, world: "EconomicWorld") -> None:
        firms = [f for f in world.firms if f.alive()]
        if len(firms) < 3:
            return
        sellers = sorted(firms, key=lambda f: f.model_reputation + 0.20 * rational_float(f.knowledge_assets) + 0.10 * truth_balance_score(f.truth_balance), reverse=True)[: max(2, len(firms)//8)]
        buyers = sorted(firms, key=lambda f: f.model_reputation - 0.50 * f.resource_overuse_score)[: max(2, len(firms)//8)]
        trades = 0
        for buyer in buyers:
            seller = world.rng.choice(sellers)
            if seller.fid == buyer.fid or rational_float(seller.knowledge_assets) <= 0.05:
                continue
            model_quality_gap = max(0.0, seller.model_reputation - buyer.model_reputation)
            if model_quality_gap <= 0.01:
                continue
            fiat_fee = min(max(0.0, buyer.cash * 0.035), (0.2 + 1.8 * model_quality_gap) * self.price)
            truth_fee_units = rationalize(min(max(0.0, rational_float(buyer.truth_balance) * 0.10), 0.08 + 0.35 * model_quality_gap))
            if fiat_fee <= EPS and truth_fee_units <= 0:
                continue
            buyer.cash -= fiat_fee
            seller.cash += fiat_fee
            if truth_fee_units > 0:
                self.transfer_truth(world, "firm", buyer.fid, "firm", seller.fid, truth_fee_units)
            buyer.model_reputation = clamp(buyer.model_reputation + 0.055 * model_quality_gap + 0.015, 0.0, 1.0)
            buyer.knowledge_assets = truth_clamp(buyer.knowledge_assets + rationalize(0.08 * model_quality_gap))
            buyer.innovation = clamp(buyer.innovation + 0.006 * model_quality_gap, 0.0, 1.0)
            buyer.resource_penalty = clamp(buyer.resource_penalty * (1.0 - 0.025 * model_quality_gap), 0.30, 1.20)
            seller.last_truth_model_sales += fiat_fee
            buyer.last_truth_model_buys += fiat_fee
            self.last_model_trade_volume += fiat_fee + rational_float(truth_fee_units) * self.price
            self.record_money_event(world, "firm", buyer.fid, "firm", seller.fid, fiat_fee + rational_float(truth_fee_units) * self.price, "correctness_model_license", fuzzy=0.45 + 0.45 * model_quality_gap, confidence=0.66, weight=0.70)
            trades += 1
        if firms:
            reps = [f.model_reputation for f in firms]
            self.model_competition_index = clamp(gini(reps) + mean(reps, 0.0), 0.0, 1.4)
        if trades and world.rng.random() < 0.15:
            world.events.add(world.t, f"{trades} correctness-model trades improved the LOGOS market.")

    def trade_knowledge_and_balance_sheets(self, world: "EconomicWorld") -> None:
        high_skill_households = [h for h in world.households if h.education > 0.68 and h.health > 0.45 and rational_float(h.knowledge_assets) > 0.30]
        firms = [f for f in world.firms if f.alive() and f.cash > 0]
        if not high_skill_households or not firms:
            return
        trades = min(len(high_skill_households), max(1, int(0.015 * len(world.households))))
        for h in world.rng.sample(high_skill_households, min(trades, len(high_skill_households))):
            f = world.rng.choice(firms)
            knowledge_units = min(0.10 + 0.25 * h.education, max(0.0, rational_float(h.knowledge_assets) * 0.12))
            if knowledge_units <= EPS:
                continue
            fee = min(f.cash * 0.012, knowledge_units * self.price * (1.0 + 0.5 * h.education))
            if fee <= EPS:
                continue
            f.cash -= fee
            h.cash += fee
            h.knowledge_assets = truth_clamp(h.knowledge_assets - rationalize(knowledge_units * 0.20))
            f.knowledge_assets = truth_clamp(f.knowledge_assets + rationalize(knowledge_units))
            f.innovation = clamp(f.innovation + 0.002 * knowledge_units, 0.0, 1.0)
            self.last_knowledge_trade_volume += fee
            self.record_money_event(world, "firm", f.fid, "household", h.hid, fee, "knowledge_education_trade", fuzzy=0.65 + 0.20 * h.education, confidence=0.68, weight=0.60)
        # Banks audit balance sheets as tradeable truth services.
        for b in [b for b in world.banks if not b.failed]:
            if world.rng.random() > 0.06 + 0.08 * self.audit_pressure:
                continue
            candidates = [f for f in firms if f.bank_id == b.bid or f.debt > 0]
            if not candidates:
                continue
            f = world.rng.choice(candidates)
            audit_fee = min(max(0.0, f.cash * 0.010), 0.20 * self.price * (0.5 + b.audit_quality))
            leverage_truth = clamp(1.0 - f.leverage() / 4.0 + 0.30 * (f.last_profit > 0), -1.0, 1.0)
            if audit_fee > EPS:
                f.cash -= audit_fee
                b.reserves += audit_fee * 0.20
                b.equity += audit_fee * 0.50
                self.record_money_event(world, "bank", b.bid, "firm", f.fid, audit_fee, "balance_sheet_truth_audit", fuzzy=leverage_truth, confidence=0.70 + 0.20 * b.audit_quality, weight=0.70)

    def update_agent_scores(self, world: "EconomicWorld") -> None:
        for h in world.households:
            h.truth_score = truth_balance_score(h.truth_balance)
        for f in world.firms:
            f.resource_penalty = clamp(1.0 - 0.35 * truth_balance_score(f.truth_balance) + 0.70 * f.resource_overuse_score, 0.20, 1.50)
            # Overuse decays, but slowly; wrongness has memory.
            f.resource_overuse_score *= 0.92
        for b in world.banks:
            b.audit_quality = clamp(0.96 * b.audit_quality + 0.04 * (0.45 + 0.35 * b.capital_ratio() + 0.20 * truth_balance_score(b.truth_balance)), 0.05, 1.0)

    def update(self, world: "EconomicWorld") -> None:
        if not world.config.truth_market_enabled:
            return
        self.finalize_resources(world)
        self.verify_predicates(world)
        self.trade_truth_currency(world)
        self.trade_correctness_models(world)
        self.trade_knowledge_and_balance_sheets(world)
        self.update_agent_scores(world)

    def metrics(self, world: "EconomicWorld") -> Dict[str, float]:
        household_balances = [rational_float(h.truth_balance) for h in world.households]
        firm_balances = [rational_float(f.truth_balance) for f in world.firms if f.alive()]
        bank_balances = [rational_float(b.truth_balance) for b in world.banks if not b.failed]
        return {
            "truth_price": self.price,
            "truth_correctness_index": self.correctness_index,
            "truth_planetary_stress": self.planetary_stress,
            "truth_cross_resource_throttle": self.cross_resource_throttle,
            "truth_trade_volume": self.last_trade_volume,
            "truth_fiat_volume": self.last_fiat_volume,
            "truth_model_trade_volume": self.last_model_trade_volume,
            "truth_knowledge_trade_volume": self.last_knowledge_trade_volume,
            "truth_verifications": float(self.last_verifications),
            "truth_predicates_created": float(self.last_predicates_created),
            "truth_total_predicates": float(self.total_predicates_created),
            "truth_total_verifications": float(self.total_verifications),
            "truth_issued": rational_float(self.truth_issued),
            "truth_destroyed": rational_float(self.truth_destroyed),
            "truth_household_mean": mean(household_balances, 0.0),
            "truth_firm_mean": mean(firm_balances, 0.0),
            "truth_bank_mean": mean(bank_balances, 0.0),
            "truth_government_balance": rational_float(world.government.truth_balance),
            "truth_model_competition": self.model_competition_index,
            "truth_audit_pressure": self.audit_pressure,
        }


# ---------------------------------------------------------------------------
# Tradeable angular moral currency market
# ---------------------------------------------------------------------------


@dataclass
class AngleCurrencyEvent:
    """
    A third currency event. The unit is not fiat and not LOGOS; it is an
    angular claim about the market object. Two state reference frames are
    included: State A at 0° and State B at 90°. Their negotiated good is 45°.
    The opposite point, 225°, is evil; 135°/315° is popular/unpopular.
    """

    eid: int
    time: int
    subject_kind: str
    subject_id: int
    counterparty_kind: str
    counterparty_id: int
    amount: float
    currency_context: str
    purpose: str
    object_angle: float
    subject_angle: float
    counterparty_angle: float
    state_a_good: float
    state_b_good: float
    objective_good: float
    evil_angle: float
    popular_axis: float
    unpopular_axis: float
    good_circumference: float
    good_evil_coordinate: float
    popularity_coordinate: float
    truth_hint: float
    units: float


@dataclass
class AngleCurrencyMarket:
    currency_name: str = "ARETE"
    price: float = 1.0
    liquidity: float = 1.0
    eid_counter: int = 1
    event_log: Deque[AngleCurrencyEvent] = field(default_factory=lambda: deque(maxlen=6000))
    state_a_good: float = ANGLE_STATE_A_GOOD_DEG
    state_b_good: float = ANGLE_STATE_B_GOOD_DEG
    objective_good: float = ANGLE_OBJECTIVE_GOOD_DEG
    evil_angle: float = ANGLE_EVIL_DEG
    popular_axis: float = ANGLE_POPULAR_DEG
    unpopular_axis: float = ANGLE_UNPOPULAR_DEG
    half_circle_circumference: float = ANGLE_HALF_CIRCLE_CIRCUMFERENCE
    last_trade_volume: float = 0.0
    last_fiat_volume: float = 0.0
    last_model_trade_volume: float = 0.0
    last_events_created: int = 0
    total_events_created: int = 0
    last_units_issued: float = 0.0
    last_units_destroyed: float = 0.0
    total_units_issued: float = 0.0
    total_units_destroyed: float = 0.0
    market_alignment_index: float = 0.0
    popularity_index: float = 0.0
    polarization_index: float = 0.0
    moral_arbitrage_volume: float = 0.0
    angle_model_competition: float = 0.0

    def configure_from_world(self, world: "EconomicWorld") -> None:
        self.currency_name = world.config.angle_currency_name
        self.state_a_good = norm_angle(world.config.angle_state_a_good)
        self.state_b_good = norm_angle(world.config.angle_state_b_good)
        self.objective_good = norm_angle(world.config.angle_objective_good)
        self.evil_angle = norm_angle(self.objective_good + 180.0)
        self.popular_axis = norm_angle(self.objective_good + 90.0)
        self.unpopular_axis = norm_angle(self.objective_good - 90.0)
        self.half_circle_circumference = ANGLE_HALF_CIRCLE_CIRCUMFERENCE

    def start_step(self, world: "EconomicWorld") -> None:
        self.configure_from_world(world)
        self.last_trade_volume = 0.0
        self.last_fiat_volume = 0.0
        self.last_model_trade_volume = 0.0
        self.last_events_created = 0
        self.last_units_issued = 0.0
        self.last_units_destroyed = 0.0
        self.moral_arbitrage_volume = 0.0
        stress = 0.0
        if getattr(world, "truth_market", None) is not None:
            stress += 0.40 * getattr(world.truth_market, "planetary_stress", 0.0)
        stress += 0.25 * getattr(world.financial_market, "financial_stress", 0.0)
        self.price = clamp(self.price * (0.995 + 0.010 * stress), 0.03, 75.0)
        for h in world.households:
            h.last_angle_flow = 0.0
        for f in world.firms:
            f.last_angle_flow = 0.0
        for b in world.banks:
            b.last_angle_flow = 0.0
        world.government.last_angle_flow = 0.0

    def state_good_for_region(self, region: str) -> float:
        if region in ANGLE_STATE_A_REGIONS:
            return self.state_a_good
        if region in ANGLE_STATE_B_REGIONS:
            return self.state_b_good
        return self.objective_good

    def actor(self, world: "EconomicWorld", kind: str, actor_id: int) -> Any:
        if kind == "household":
            return world.household_by_id(actor_id)
        if kind == "firm":
            return world.firm_by_id(actor_id)
        if kind == "bank":
            if 0 <= actor_id < len(world.banks):
                return world.banks[actor_id]
            return None
        if kind == "government":
            return world.government
        return None

    def actor_angle(self, world: "EconomicWorld", kind: str, actor_id: int) -> float:
        actor = self.actor(world, kind, actor_id)
        if actor is not None and hasattr(actor, "angle_position"):
            return norm_angle(actor.angle_position)
        return self.objective_good

    def actor_reputation(self, world: "EconomicWorld", kind: str, actor_id: int) -> float:
        actor = self.actor(world, kind, actor_id)
        if actor is None or not hasattr(actor, "angle_balance"):
            return 0.0
        return angle_wealth_score(actor.angle_balance, getattr(actor, "angle_debt", 0.0))

    def credit_actor(self, world: "EconomicWorld", kind: str, actor_id: int, units: float, reason_angle: Optional[float] = None) -> None:
        if not world.config.angle_market_enabled or abs(units) <= EPS:
            return
        actor = self.actor(world, kind, actor_id)
        if actor is None or not hasattr(actor, "angle_balance"):
            return
        if units >= 0.0:
            actor.angle_balance = max(0.0, actor.angle_balance + units)
            actor.last_angle_flow += units
            self.last_units_issued += units
            self.total_units_issued += units
        else:
            debt = -units
            burn = min(actor.angle_balance, debt)
            actor.angle_balance -= burn
            actor.angle_debt += max(0.0, debt - burn)
            actor.last_angle_flow -= debt
            self.last_units_destroyed += debt
            self.total_units_destroyed += debt
        if reason_angle is not None:
            current_weight = 1.0 + max(0.0, actor.angle_balance) * 0.015
            event_weight = max(0.15, abs(units))
            actor.angle_position = circular_mean_deg([actor.angle_position, reason_angle], [current_weight, event_weight], default=self.objective_good)
        actor.angle_reputation = self.actor_reputation(world, kind, actor_id)

    def transfer_angle(self, world: "EconomicWorld", seller_kind: str, seller_id: int, buyer_kind: str, buyer_id: int, units: float) -> bool:
        if units <= EPS:
            return False
        seller = self.actor(world, seller_kind, seller_id)
        buyer = self.actor(world, buyer_kind, buyer_id)
        if seller is None or buyer is None:
            return False
        if not hasattr(seller, "angle_balance") or not hasattr(buyer, "angle_balance"):
            return False
        amount = min(max(0.0, seller.angle_balance), units)
        if amount <= EPS:
            return False
        seller.angle_balance -= amount
        buyer.angle_balance += amount
        seller.last_angle_flow -= amount
        buyer.last_angle_flow += amount
        seller.angle_reputation = self.actor_reputation(world, seller_kind, seller_id)
        buyer.angle_reputation = self.actor_reputation(world, buyer_kind, buyer_id)
        self.last_trade_volume += amount
        return True

    def seed_initial_balances(self, world: "EconomicWorld") -> None:
        self.configure_from_world(world)
        for h in world.households:
            local_good = self.state_good_for_region(h.region)
            truth = truth_balance_score(h.truth_balance) if hasattr(h, "truth_balance") else 0.0
            h.angle_country_good = local_good
            h.angle_position = circular_mean_deg(
                [local_good, self.objective_good, 40.0],
                [0.45, 0.55 + h.education + 0.35 * max(0.0, truth), 0.15 * h.health],
                default=self.objective_good,
            )
            h.angle_position = blend_angles(h.angle_position, self.evil_angle, max(0.0, h.debt) / max(25.0, h.wealth() + 25.0) * 0.10)
            h.angle_balance = max(0.0, angle_good_circumference_value(h.angle_position) * (0.7 + h.education + 0.10 * math.log1p(max(0.0, h.cash))))
            h.angle_debt = max(0.0, (1.0 - angle_goodness_fraction(h.angle_position)) * 0.4 * max(0.0, h.debt))
            h.angle_reputation = self.actor_reputation(world, "household", h.hid)
        for f in world.firms:
            local_good = self.state_good_for_region(f.region)
            sector_angle = SECTOR_BASE_ANGLE.get(f.sector, self.objective_good)
            truth = truth_balance_score(f.truth_balance) if hasattr(f, "truth_balance") else 0.0
            clean = 1.0 - clamp(f.emissions_intensity + 0.25 * f.energy_intensity, 0.0, 1.6) / 1.6
            f.angle_country_good = local_good
            f.angle_position = circular_mean_deg(
                [sector_angle, local_good, self.objective_good],
                [0.70, 0.25, 0.40 + 0.55 * f.model_reputation + 0.35 * clean + 0.25 * max(0.0, truth)],
                default=self.objective_good,
            )
            f.angle_position = blend_angles(f.angle_position, self.evil_angle, 0.18 * clamp(f.leverage() / 5.0, 0.0, 1.0) + 0.10 * f.resource_overuse_score)
            f.angle_balance = max(0.0, angle_good_circumference_value(f.angle_position) * (0.55 + f.model_reputation + 0.20 * math.log1p(max(0.0, f.cash))))
            f.angle_debt = max(0.0, (1.0 - angle_goodness_fraction(f.angle_position)) * 0.25 * max(0.0, f.debt))
            f.angle_reputation = self.actor_reputation(world, "firm", f.fid)
        for b in world.banks:
            local_good = self.state_good_for_region(b.region)
            b.angle_country_good = local_good
            b.angle_position = circular_mean_deg(
                [68.0, local_good, self.objective_good],
                [0.55, 0.25, 0.45 + b.audit_quality + 0.35 * b.capital_ratio()],
                default=self.objective_good,
            )
            b.angle_balance = max(0.0, angle_good_circumference_value(b.angle_position) * (0.8 + b.audit_quality + 0.3 * b.capital_ratio()))
            b.angle_debt = max(0.0, (1.0 - angle_goodness_fraction(b.angle_position)) * 0.10 * max(0.0, b.deposits / 100.0))
            b.angle_reputation = self.actor_reputation(world, "bank", b.bid)
        world.government.angle_country_good = self.objective_good
        world.government.angle_position = self.objective_good
        world.government.angle_balance = angle_good_circumference_value(self.objective_good) * (1.0 + world.government.planetary_trust)
        world.government.angle_debt = 0.0
        world.government.angle_reputation = self.actor_reputation(world, "government", 0)

    def purpose_base_angle(self, purpose: str, default: float = ANGLE_OBJECTIVE_GOOD_DEG) -> float:
        p = purpose.lower()
        best = default
        best_len = -1
        for key, value in PURPOSE_BASE_ANGLE.items():
            if key in p and len(key) > best_len:
                best = value
                best_len = len(key)
        if p.startswith("market_sale_"):
            sector = p.replace("market_sale_", "")
            for s in SECTORS:
                if s.lower() == sector.lower():
                    best = SECTOR_BASE_ANGLE.get(s, best)
                    break
        if p.startswith("public_spending_"):
            sector = p.replace("public_spending_", "")
            for s in SECTORS:
                if s.lower() == sector.lower():
                    best = circular_mean_deg([SECTOR_BASE_ANGLE.get(s, best), self.objective_good], [0.40, 0.60])
                    break
        if p.startswith("resource_use_"):
            r = p.replace("resource_use_", "")
            best = RESOURCE_BASE_ANGLE.get(r, best)
        return norm_angle(best)

    def determine_object_angle(
        self,
        world: "EconomicWorld",
        purpose: str,
        subject_kind: str,
        subject_id: int,
        counterparty_kind: str,
        counterparty_id: int,
        truth_hint: float,
        amount: float,
        object_angle: Optional[float] = None,
    ) -> float:
        if object_angle is None:
            subject_angle = self.actor_angle(world, subject_kind, subject_id)
            counter_angle = self.actor_angle(world, counterparty_kind, counterparty_id)
            base = self.purpose_base_angle(purpose, default=circular_mean_deg([subject_angle, counter_angle], [0.7, 0.3]))
        else:
            base = norm_angle(object_angle)
        p = purpose.lower()
        if truth_hint >= 0.0:
            base = blend_angles(base, self.objective_good, world.config.angle_truth_weight * clamp(truth_hint, 0.0, 1.0))
        else:
            base = blend_angles(base, self.evil_angle, world.config.angle_truth_weight * clamp(-truth_hint, 0.0, 1.0))
        planetary_stress = getattr(getattr(world, "truth_market", None), "planetary_stress", 0.0)
        if "resource_use" in p or "fossil" in p or "emissions" in p or "energy" in p:
            base = blend_angles(base, self.evil_angle, world.config.angle_resource_weight * clamp(planetary_stress, 0.0, 1.0))
        if "platform" in p or "data" in p:
            pop_angle = self.popular_axis if world.platform_market.user_share >= 0.5 else self.unpopular_axis
            base = blend_angles(base, pop_angle, 0.20 + 0.25 * world.platform_market.concentration)
        if "rent" in p and world.metrics_last.get("housing_affordability", 0.4) > 0.55:
            base = blend_angles(base, self.evil_angle, 0.20)
        return norm_angle(base)

    def record_exchange(
        self,
        world: "EconomicWorld",
        subject_kind: str,
        subject_id: int,
        counterparty_kind: str,
        counterparty_id: int,
        amount: float,
        purpose: str,
        truth_hint: float = 0.0,
        confidence: float = 0.58,
        weight: float = 1.0,
        currency_context: str = "FIAT",
        extra: Sequence[str] = (),
        object_angle: Optional[float] = None,
        issue: bool = True,
    ) -> float:
        if not world.config.angle_market_enabled or amount <= EPS:
            return 0.0
        truth_hint = clamp(float(truth_hint), -1.0, 1.0)
        confidence = clamp(float(confidence), 0.0, 1.0)
        object_angle = self.determine_object_angle(world, purpose, subject_kind, subject_id, counterparty_kind, counterparty_id, truth_hint, amount, object_angle)
        subject_angle = self.actor_angle(world, subject_kind, subject_id)
        counter_angle = self.actor_angle(world, counterparty_kind, counterparty_id)
        good_circ = self.half_circle_circumference * clamp(1.0 - angular_distance(object_angle, self.objective_good) / 180.0, 0.0, 1.0)
        good_fraction = clamp(good_circ / max(EPS, self.half_circle_circumference), 0.0, 1.0)
        good_evil_coord = angle_axis_coordinate(object_angle, self.objective_good)
        popularity_coord = angle_axis_coordinate(object_angle, self.popular_axis)
        amount_scale = math.log1p(abs(amount)) / max(1.0, world.config.angle_money_scale)
        if currency_context == world.config.truth_currency_name:
            amount_scale *= max(0.25, getattr(world.truth_market, "price", 1.0))
        elif currency_context == "RESOURCE_QUOTA":
            amount_scale *= 0.70 + 0.60 * clamp(getattr(world.truth_market, "planetary_stress", 0.0), 0.0, 1.0)
        base_units = max(0.0001, amount_scale * max(0.0, weight) * (0.65 + 0.35 * confidence))
        moral_units = base_units * (2.0 * good_fraction - 1.0)
        truth_units = base_units * world.config.angle_truth_weight * truth_hint * 0.35
        popularity_units = base_units * world.config.angle_popularity_weight * popularity_coord
        units = clamp(moral_units + truth_units + popularity_units, -25.0, 25.0)
        event = AngleCurrencyEvent(
            eid=self.eid_counter,
            time=world.t,
            subject_kind=subject_kind,
            subject_id=subject_id,
            counterparty_kind=counterparty_kind,
            counterparty_id=counterparty_id,
            amount=amount,
            currency_context=currency_context,
            purpose=purpose,
            object_angle=object_angle,
            subject_angle=subject_angle,
            counterparty_angle=counter_angle,
            state_a_good=self.state_a_good,
            state_b_good=self.state_b_good,
            objective_good=self.objective_good,
            evil_angle=self.evil_angle,
            popular_axis=self.popular_axis,
            unpopular_axis=self.unpopular_axis,
            good_circumference=good_circ,
            good_evil_coordinate=good_evil_coord,
            popularity_coordinate=popularity_coord,
            truth_hint=truth_hint,
            units=units,
        )
        self.eid_counter += 1
        self.event_log.append(event)
        self.last_events_created += 1
        self.total_events_created += 1
        if issue:
            self.credit_actor(world, subject_kind, subject_id, units, reason_angle=object_angle)
            if counterparty_kind in {"household", "firm", "bank", "government"}:
                self.credit_actor(world, counterparty_kind, counterparty_id, units / 3.0, reason_angle=object_angle)
        return units

    def trade_angle_currency(self, world: "EconomicWorld") -> None:
        if not world.config.angle_market_enabled:
            return
        firms = [f for f in world.firms if f.alive()]
        if len(firms) < 3:
            return
        sellers = [f for f in firms if f.angle_balance > 1.8 and f.cash > -5.0 and f.angle_reputation > -0.05]
        buyers = [f for f in firms if f.angle_debt > 0.25 or f.angle_reputation < 0.05 or f.resource_overuse_score > 0.12]
        world.rng.shuffle(sellers)
        world.rng.shuffle(buyers)
        demand_pressure = safe_div(len(buyers), max(1.0, len(sellers)), 0.0)
        self.price = clamp(self.price * (1.0 + 0.018 * (demand_pressure - 1.0) + 0.020 * getattr(world.truth_market, "planetary_stress", 0.0)), 0.03, 75.0)
        max_trades = int(max(2, world.config.angle_trade_intensity * len(firms)))
        for seller, buyer in zip(sellers[:max_trades], buyers[:max_trades]):
            if seller.fid == buyer.fid:
                continue
            supply = max(0.0, seller.angle_balance - 1.2)
            need = max(0.0, 1.2 - buyer.angle_balance) + 0.80 * buyer.angle_debt + 0.65 * buyer.resource_overuse_score
            units = min(supply, need, world.rng.uniform(0.04, 0.42) * (1.0 + getattr(world.truth_market, "planetary_stress", 0.0)))
            if units <= EPS:
                continue
            fiat_price = units * self.price * world.config.angle_to_fiat_fx
            if buyer.cash < fiat_price:
                fiat_price = max(0.0, buyer.cash * 0.35)
                units = fiat_price / max(EPS, self.price * world.config.angle_to_fiat_fx)
            if fiat_price <= EPS or units <= EPS:
                continue
            if self.transfer_angle(world, "firm", seller.fid, "firm", buyer.fid, units):
                buyer.cash -= fiat_price
                seller.cash += fiat_price
                self.last_fiat_volume += fiat_price
                self.moral_arbitrage_volume += units
                self.record_exchange(
                    world,
                    "firm",
                    buyer.fid,
                    "firm",
                    seller.fid,
                    fiat_price,
                    "angle_currency_purchase",
                    truth_hint=0.10 + 0.40 * seller.angle_reputation,
                    confidence=0.58,
                    weight=0.35,
                    currency_context=world.config.currency_name,
                    object_angle=circular_mean_deg([seller.angle_position, self.objective_good], [0.55, 0.45]),
                    issue=False,
                )

    def trade_angle_models(self, world: "EconomicWorld") -> None:
        firms = [f for f in world.firms if f.alive() and f.cash > 0]
        if len(firms) < 4:
            return
        sellers = sorted(firms, key=lambda f: f.angle_reputation + 0.35 * f.model_reputation + 0.10 * rational_float(f.knowledge_assets), reverse=True)[: max(2, len(firms)//9)]
        buyers = sorted(firms, key=lambda f: f.angle_reputation - 0.45 * f.resource_overuse_score)[: max(2, len(firms)//9)]
        trades = 0
        for buyer in buyers:
            seller = world.rng.choice(sellers)
            if buyer.fid == seller.fid:
                continue
            quality_gap = max(0.0, seller.angle_reputation - buyer.angle_reputation + 0.15 * (seller.model_reputation - buyer.model_reputation))
            if quality_gap <= 0.01:
                continue
            fee = min(max(0.0, buyer.cash * 0.018), (0.12 + 1.1 * quality_gap) * self.price)
            angle_fee = min(max(0.0, buyer.angle_balance * 0.08), 0.05 + 0.22 * quality_gap)
            if fee <= EPS and angle_fee <= EPS:
                continue
            buyer.cash -= fee
            seller.cash += fee
            if angle_fee > EPS:
                self.transfer_angle(world, "firm", buyer.fid, "firm", seller.fid, angle_fee)
            buyer.angle_position = blend_angles(buyer.angle_position, self.objective_good, 0.035 + 0.10 * quality_gap)
            buyer.angle_debt *= max(0.60, 1.0 - 0.10 * quality_gap)
            buyer.angle_reputation = self.actor_reputation(world, "firm", buyer.fid)
            buyer.model_reputation = clamp(buyer.model_reputation + 0.010 * quality_gap, 0.0, 1.0)
            buyer.resource_penalty = clamp(buyer.resource_penalty * (1.0 - 0.015 * quality_gap), 0.25, 1.20)
            self.last_model_trade_volume += fee + angle_fee * self.price
            self.record_exchange(
                world,
                "firm",
                buyer.fid,
                "firm",
                seller.fid,
                fee + angle_fee * self.price,
                "angular_correctness_model_license",
                truth_hint=0.35 + 0.45 * quality_gap,
                confidence=0.64,
                weight=0.50,
                currency_context=world.config.currency_name,
                object_angle=self.objective_good,
            )
            trades += 1
        if firms:
            reps = [f.angle_reputation for f in firms]
            self.angle_model_competition = clamp(mean(reps, 0.0) + 0.50 * gini([r + 1.0 for r in reps]), 0.0, 1.8)
        if trades and world.rng.random() < 0.12:
            world.events.add(world.t, f"{trades} angular-correctness model trades moved firms toward the shared 45° good.")

    def update_agent_scores(self, world: "EconomicWorld") -> None:
        for h in world.households:
            h.angle_reputation = self.actor_reputation(world, "household", h.hid)
            local = self.state_good_for_region(h.region)
            h.angle_country_good = local
            h.angle_position = blend_angles(h.angle_position, self.objective_good, 0.002 * h.education + 0.001 * max(0.0, h.truth_score))
        for f in world.firms:
            f.angle_reputation = self.actor_reputation(world, "firm", f.fid)
            clean_pull = 0.001 + 0.002 * f.model_reputation + 0.001 * max(0.0, truth_balance_score(f.truth_balance))
            dirty_push = 0.003 * f.resource_overuse_score
            f.angle_position = blend_angles(f.angle_position, self.objective_good, clean_pull)
            if dirty_push > 0:
                f.angle_position = blend_angles(f.angle_position, self.evil_angle, dirty_push)
        for b in world.banks:
            b.angle_reputation = self.actor_reputation(world, "bank", b.bid)
            b.angle_position = blend_angles(b.angle_position, self.objective_good, 0.0015 * b.audit_quality)
        world.government.angle_reputation = self.actor_reputation(world, "government", 0)

    def update_indices(self, world: "EconomicWorld") -> None:
        recent = list(self.event_log)[-min(1000, len(self.event_log)):]
        if not recent:
            self.market_alignment_index = 0.0
            self.popularity_index = 0.0
            self.polarization_index = 0.0
            return
        weights = [max(0.001, math.log1p(e.amount)) for e in recent]
        self.market_alignment_index = clamp(weighted_average(((clamp(1.0 - angular_distance(e.object_angle, self.objective_good) / 180.0, 0.0, 1.0), w) for e, w in zip(recent, weights)), 0.0), 0.0, 1.0)
        self.popularity_index = clamp(weighted_average(((e.popularity_coordinate, w) for e, w in zip(recent, weights)), 0.0), -1.0, 1.0)
        self.polarization_index = clamp(weighted_average(((angular_distance(e.object_angle, self.objective_good) / 180.0, w) for e, w in zip(recent, weights)), 0.0), 0.0, 1.0)

    def update(self, world: "EconomicWorld") -> None:
        if not world.config.angle_market_enabled:
            return
        self.trade_angle_currency(world)
        self.trade_angle_models(world)
        self.update_agent_scores(world)
        self.update_indices(world)

    def metrics(self, world: "EconomicWorld") -> Dict[str, float]:
        household_balances = [h.angle_balance - h.angle_debt for h in world.households]
        firm_balances = [f.angle_balance - f.angle_debt for f in world.firms if f.alive()]
        bank_balances = [b.angle_balance - b.angle_debt for b in world.banks if not b.failed]
        actor_angles = [h.angle_position for h in world.households]
        actor_angles.extend(f.angle_position for f in world.firms if f.alive())
        mean_actor_goodness = mean((clamp(1.0 - angular_distance(a, self.objective_good) / 180.0, 0.0, 1.0) for a in actor_angles), 0.0)
        return {
            "angle_price": self.price,
            "angle_market_alignment": self.market_alignment_index,
            "angle_popularity_index": self.popularity_index,
            "angle_polarization_index": self.polarization_index,
            "angle_trade_volume": self.last_trade_volume,
            "angle_fiat_volume": self.last_fiat_volume,
            "angle_model_trade_volume": self.last_model_trade_volume,
            "angle_events_created": float(self.last_events_created),
            "angle_total_events": float(self.total_events_created),
            "angle_units_issued_step": self.last_units_issued,
            "angle_units_destroyed_step": self.last_units_destroyed,
            "angle_total_units_issued": self.total_units_issued,
            "angle_total_units_destroyed": self.total_units_destroyed,
            "angle_moral_arbitrage_volume": self.moral_arbitrage_volume,
            "angle_household_mean": mean(household_balances, 0.0),
            "angle_firm_mean": mean(firm_balances, 0.0),
            "angle_bank_mean": mean(bank_balances, 0.0),
            "angle_government_balance": world.government.angle_balance - world.government.angle_debt,
            "angle_mean_actor_goodness": mean_actor_goodness,
            "angle_objective_good_deg": self.objective_good,
            "angle_evil_deg": self.evil_angle,
            "angle_popular_axis_deg": self.popular_axis,
            "angle_unpopular_axis_deg": self.unpopular_axis,
            "angle_model_competition": self.angle_model_competition,
        }

# ---------------------------------------------------------------------------
# Scenario shocks
# ---------------------------------------------------------------------------


class ScenarioEngine:
    """Applies stylized shocks. Add new methods for new research questions."""

    def __init__(self, name: str, compound: str = "") -> None:
        self.names = [name] if name else ["baseline"]
        if compound:
            self.names.extend([x.strip() for x in compound.split(",") if x.strip()])
        self.state: Dict[str, float] = defaultdict(float)

    def pressure(self, t: int) -> float:
        p = 0.0
        for name in self.names:
            if name == "baseline":
                continue
            if name in {"energy_shock", "supply_chain_break", "stagflation_combo"} and 10 <= t <= 55:
                p += 0.8
            elif name in {"financial_crisis", "housing_boom_bust"} and 25 <= t <= 70:
                p += 0.9
            elif name == "pandemic_like" and 8 <= t <= 42:
                p += 1.0
            elif name in {"climate_transition", "ai_automation", "protectionism"}:
                p += 0.35
        return clamp(p, 0.0, 2.0)

    def apply_pre_step(self, world: "EconomicWorld") -> None:
        t = world.t
        for name in self.names:
            if name == "baseline":
                continue
            getattr(self, f"_pre_{name}", self._pre_unknown)(world, t)

    def apply_post_step(self, world: "EconomicWorld") -> None:
        t = world.t
        for name in self.names:
            if name == "baseline":
                continue
            getattr(self, f"_post_{name}", self._post_unknown)(world, t)

    def _pre_unknown(self, world: "EconomicWorld", t: int) -> None:
        if t == 0:
            world.events.add(t, f"Unknown scenario ignored: {world.config.scenario}")

    def _post_unknown(self, world: "EconomicWorld", t: int) -> None:
        return

    def _pre_energy_shock(self, world: "EconomicWorld", t: int) -> None:
        if t == 10:
            world.events.add(t, "Energy shock begins: fossil prices and volatility rise.")
        if 10 <= t <= 35:
            world.energy_market.fossil_price *= 1.018
        if 36 <= t <= 70:
            world.energy_market.fossil_price *= 0.995

    def _pre_supply_chain_break(self, world: "EconomicWorld", t: int) -> None:
        if t == 14:
            world.events.add(t, "Supply-chain break: manufacturing/transport bottlenecks hit input costs.")
        if 14 <= t <= 45:
            for f in world.firms:
                if f.sector in {"Manufacturing", "Transport", "Exportables", "Construction"}:
                    f.supply_chain_fragility = clamp(f.supply_chain_fragility + 0.020, 0.0, 0.85)
        if 46 <= t <= 90:
            for f in world.firms:
                f.supply_chain_fragility *= 0.985

    def _pre_financial_crisis(self, world: "EconomicWorld", t: int) -> None:
        if t == 28:
            world.events.add(t, "Financial crisis: asset prices fall, bank risk appetite collapses.")
            world.financial_market.asset_crash_pressure = max(world.financial_market.asset_crash_pressure, 0.35)
            world.financial_market.stock_index *= 0.72
            for b in world.banks:
                b.equity *= world.rng.uniform(0.82, 0.94)
                b.risk_appetite *= 0.58
        if 29 <= t <= 65:
            world.financial_market.asset_crash_pressure = max(world.financial_market.asset_crash_pressure, 0.15)
            for b in world.banks:
                b.risk_appetite = clamp(b.risk_appetite * 0.995, 0.05, 1.20)

    def _pre_housing_boom_bust(self, world: "EconomicWorld", t: int) -> None:
        if t == 1:
            world.events.add(t, "Housing boom phase: credit appetite and house prices rise.")
        if 1 <= t <= 30:
            world.config.max_mortgage_ltv = min(0.95, world.config.max_mortgage_ltv + 0.0015)
            for b in world.banks:
                b.risk_appetite = clamp(b.risk_appetite + 0.005, 0.05, 1.25)
            for r in REGIONS:
                world.housing_market.price_index[r] *= 1.006
        if t == 42:
            world.events.add(t, "Housing bust: collateral values fall and mortgage risk rises.")
            world.financial_market.asset_crash_pressure = max(world.financial_market.asset_crash_pressure, 0.25)
            for r in REGIONS:
                world.housing_market.price_index[r] *= 0.82
            for h in world.households:
                if h.home_owner:
                    h.home_value *= 0.82
        if 43 <= t <= 70:
            for r in REGIONS:
                world.housing_market.price_index[r] *= 0.994

    def _pre_climate_transition(self, world: "EconomicWorld", t: int) -> None:
        if t == 1:
            world.events.add(t, "Climate transition: carbon price and green subsidies ramp up.")
        world.government.carbon_price = clamp(world.government.carbon_price + 0.00055, 0.0, 0.20)
        world.government.green_subsidy = clamp(world.government.green_subsidy + 0.0007, 0.0, 0.10)
        if t % 12 == 0:
            world.energy_market.renewable_capacity *= 1.015

    def _pre_protectionism(self, world: "EconomicWorld", t: int) -> None:
        if t == 3:
            world.events.add(t, "Protectionism: tariffs rise, exports weaken, imports become dearer.")
        world.foreign_sector.tariff_rate = clamp(world.foreign_sector.tariff_rate + 0.0007, 0.02, 0.18)
        world.foreign_sector.export_demand_index *= 0.999
        if 20 <= t <= 60:
            world.foreign_sector.capital_flow_pressure -= 0.0005

    def _pre_ai_automation(self, world: "EconomicWorld", t: int) -> None:
        if t == 1:
            world.events.add(t, "AI automation: productivity rises in digital/professional sectors; low-skill labor demand weakens.")
        for f in world.firms:
            if f.sector in {"DigitalPlatform", "ProfessionalServices", "Finance", "Manufacturing", "Retail"}:
                f.automation = clamp(f.automation + 0.0035, 0.0, 1.0)
                f.productivity *= 1.0015
            if f.sector in {"Retail", "Manufacturing"} and t > 20:
                f.desired_labor = max(0, int(f.desired_labor * 0.998))

    def _pre_austerity(self, world: "EconomicWorld", t: int) -> None:
        if t == 1:
            world.events.add(t, "Austerity: public spending and transfers are compressed.")
        world.config.infrastructure_intensity *= 0.999
        world.config.public_education_intensity *= 0.999
        world.config.public_health_intensity *= 0.999
        world.config.unemployment_benefit_replacement = max(0.25, world.config.unemployment_benefit_replacement * 0.999)

    def _pre_stimulus(self, world: "EconomicWorld", t: int) -> None:
        if t == 1:
            world.events.add(t, "Stimulus: transfers, infrastructure, and public demand rise.")
        if t <= 48:
            world.config.basic_transfer += 0.002
            world.config.infrastructure_intensity = min(1.35, world.config.infrastructure_intensity + 0.002)
            world.government.green_subsidy = max(world.government.green_subsidy, 0.015)

    def _pre_pandemic_like(self, world: "EconomicWorld", t: int) -> None:
        if t == 8:
            world.events.add(t, "Pandemic-like shock: health and contact-service demand fall; digital demand rises.")
        if 8 <= t <= 36:
            for h in world.households:
                if world.rng.random() < 0.015:
                    h.health = clamp(h.health - world.rng.uniform(0.02, 0.12), 0.05, 1.0)
            for f in world.firms:
                if f.sector in {"Retail", "Transport", "Food", "ProfessionalServices"}:
                    f.expected_demand *= 0.985
                if f.sector == "DigitalPlatform":
                    f.expected_demand *= 1.015
        if 37 <= t <= 55:
            for h in world.households:
                h.health = clamp(h.health + 0.003, 0.05, 1.0)

    def _pre_stagflation_combo(self, world: "EconomicWorld", t: int) -> None:
        self._pre_energy_shock(world, t)
        self._pre_supply_chain_break(world, t)
        if 15 <= t <= 55:
            for f in world.firms:
                f.productivity *= 0.999

    def _post_financial_crisis(self, world: "EconomicWorld", t: int) -> None:
        if 65 <= t <= 110:
            for b in world.banks:
                b.risk_appetite = clamp(b.risk_appetite + 0.003, 0.05, 1.10)

    def _post_climate_transition(self, world: "EconomicWorld", t: int) -> None:
        # Dirtier firms face adaptation pressure; clean firms improve quality and export appeal.
        for f in world.firms:
            if not f.alive():
                continue
            dirtiness = f.emissions_intensity * (1.0 - f.innovation)
            if dirtiness > 0.14 and f.cash > 0:
                adaptation = min(f.cash * 0.006, 0.025 * f.capital)
                f.cash -= adaptation
                f.emissions_intensity *= 0.999
                f.innovation = clamp(f.innovation + 0.0006, 0.0, 1.0)
            elif f.emissions_intensity < 0.08:
                f.quality *= 1.0003


# ---------------------------------------------------------------------------
# The economic world
# ---------------------------------------------------------------------------


class EconomicWorld:
    def __init__(self, config: SimulationConfig) -> None:
        self.config = config
        self.rng = random.Random(config.seed)
        self.t = 0
        self.events = EventLog()
        self.scenarios = ScenarioEngine(config.scenario, config.shock_compound)
        self.central_bank = CentralBank(config.initial_policy_rate, config.inflation_target)
        self.government = Government(
            income_tax=config.income_tax,
            corporate_tax=config.corporate_tax,
            vat=config.vat,
            capital_tax=config.capital_tax,
            property_tax=config.property_tax,
            carbon_price=config.carbon_price,
            unemployment_replacement=config.unemployment_benefit_replacement,
            basic_transfer=config.basic_transfer,
            public_education_quality=config.public_education_intensity,
            public_health_quality=config.public_health_intensity,
            infrastructure_quality=config.infrastructure_intensity,
            green_subsidy=config.green_subsidy,
        )
        self.energy_market = EnergyMarket()
        self.housing_market = HousingMarket.create(config)
        self.foreign_sector = ForeignSector()
        self.financial_market = FinancialMarket()
        self.platform_market = PlatformMarket()
        self.insurance_market = InsuranceMarket()
        self.truth_market = TruthCurrencyMarket(currency_name=config.truth_currency_name)
        self.angle_market = AngleCurrencyMarket(currency_name=config.angle_currency_name)
        self.households: List[Household] = []
        self.firms: List[Firm] = []
        self.banks: List[Bank] = []
        self.sector_price_index: Dict[str, float] = dict(INITIAL_PRICE)
        self.sector_output: Dict[str, float] = {s: 0.0 for s in SECTORS}
        self.sector_revenue: Dict[str, float] = {s: 0.0 for s in SECTORS}
        self.sector_unfilled: Dict[str, float] = {s: 0.0 for s in SECTORS}
        self.sector_hhi: Dict[str, float] = {s: 0.0 for s in SECTORS}
        self.loan_id_counter = 1
        self.metrics: List[Dict[str, float]] = []
        initial_gdp_proxy = max(100.0, config.households * 3.0)
        self.metrics_last: Dict[str, float] = {"cpi": 1.0, "gdp": initial_gdp_proxy, "inflation": 0.0, "unemployment": 0.05, "npl_ratio": 0.0}
        self.step_household_defaults = 0
        self.step_firm_bankruptcies = 0
        self.step_bank_failures = 0
        self.step_new_credit = 0.0
        self.step_imports = 0.0
        self.step_exports = 0.0
        self._initialize_agents()
        self._initialize_supplier_network()
        self._initial_employment()
        self.truth_market.seed_initial_balances(self)
        if self.config.angle_market_enabled:
            self.angle_market.seed_initial_balances(self)

    # ------------------------------------------------------------------
    # Initialization
    # ------------------------------------------------------------------

    def _initialize_agents(self) -> None:
        region_items = list(REGION_POP_WEIGHTS.keys())
        region_weights = [REGION_POP_WEIGHTS[r] for r in region_items]
        sector_items = list(SECTOR_WEIGHTS_FOR_FIRMS.keys())
        sector_weights = [SECTOR_WEIGHTS_FOR_FIRMS[s] for s in sector_items]

        for bid in range(self.config.banks):
            region = REGIONS[bid % len(REGIONS)]
            equity = self.rng.uniform(130.0, 260.0) * (self.config.households / 600.0)
            reserves = self.rng.uniform(250.0, 460.0) * (self.config.households / 600.0)
            deposits = self.rng.uniform(1000.0, 1800.0) * (self.config.households / 600.0)
            risk_appetite = self.rng.uniform(0.50, 0.95)
            self.banks.append(Bank(bid, region, equity, reserves, deposits, risk_appetite, operating_cost_rate=0.004))

        for hid in range(self.config.households):
            region = weighted_choice(self.rng, region_items, region_weights)
            age = int(clamp(self.rng.gauss(41, 16), 18, 82))
            education = clamp(self.rng.betavariate(3.0, 2.2), 0.05, 1.0)
            regional_productivity = REGION_PRODUCTIVITY[region]
            skill = clamp(self.rng.lognormvariate(0.0, 0.24) * (0.55 + 0.75 * education) * regional_productivity, 0.25, 3.0)
            health = clamp(self.rng.betavariate(7.5, 2.0), 0.15, 1.0)
            risk_aversion = clamp(self.rng.betavariate(3.5, 3.0), 0.05, 1.0)
            patience = clamp(self.rng.betavariate(2.4, 2.5), 0.05, 1.0)
            bank_id = self.rng.randrange(len(self.banks))
            cash = self.rng.lognormvariate(1.4 + 0.7 * education, 0.75)
            asset_portfolio = self.rng.lognormvariate(0.8 + 1.0 * education, 1.0) if self.rng.random() < 0.45 else 0.0
            pension = self.rng.lognormvariate(1.3 + 0.8 * education, 0.7) if age > 35 else self.rng.uniform(0.0, 4.0)
            owner_prob = logistic(-1.8 + 0.055 * (age - 25) + 0.55 * education + 0.020 * cash)
            home_owner = self.rng.random() < owner_prob
            home_value = 0.0
            mortgage = 0.0
            debt = 0.0
            rent_payment = self.housing_market.rent_index[region] * self.rng.uniform(0.85, 1.25)
            if home_owner:
                home_value = self.housing_market.price_index[region] * self.rng.uniform(0.65, 1.55)
                mortgage = home_value * self.rng.uniform(0.05, 0.75) if age < 62 else home_value * self.rng.uniform(0.0, 0.25)
                rent_payment = 0.0
            if self.rng.random() < 0.38:
                debt = self.rng.lognormvariate(0.6, 0.8)
            pref_shift = {}
            for s in SECTORS:
                pref_shift[s] = clamp(self.rng.lognormvariate(0.0, 0.15), 0.55, 1.75)
            children = max(0, int(self.rng.gauss(1.0, 1.1))) if 24 <= age <= 55 else 0
            h = Household(
                hid=hid,
                region=region,
                age=age,
                education=education,
                skill=skill,
                health=health,
                risk_aversion=risk_aversion,
                patience=patience,
                preference_shift=pref_shift,
                bank_id=bank_id,
                cash=cash,
                debt=debt,
                mortgage=mortgage,
                home_owner=home_owner,
                home_value=home_value,
                rent_payment=rent_payment,
                asset_portfolio=asset_portfolio,
                pension_wealth=pension,
                children=children,
                energy_efficiency=clamp(self.rng.lognormvariate(0.0, 0.10), 0.65, 1.35),
                insured_health=self.rng.random() < 0.82,
                platform_user=self.rng.random() < self.platform_market.user_share,
                social_capital=clamp(self.rng.lognormvariate(0.0, 0.15), 0.6, 1.6),
            )
            self.households.append(h)

        for fid in range(self.config.firms):
            sector = weighted_choice(self.rng, sector_items, sector_weights)
            region = weighted_choice(self.rng, region_items, region_weights)
            regional_productivity = REGION_PRODUCTIVITY[region]
            productivity = clamp(self.rng.lognormvariate(0.1, 0.22) * regional_productivity, 0.25, 3.5)
            if sector in HIGH_SKILL_SECTORS:
                productivity *= 1.10
            capital = self.rng.lognormvariate(3.0 if sector in CAPITAL_HEAVY_SECTORS else 2.3, 0.55)
            cash = self.rng.lognormvariate(2.0, 0.7)
            debt = capital * self.rng.uniform(0.05, 0.65)
            bank_id = self.rng.randrange(len(self.banks))
            base_wage = 2.6 + 1.0 * (sector in HIGH_SKILL_SECTORS) + 0.25 * REGION_PRODUCTIVITY[region]
            price = INITIAL_PRICE[sector] * self.rng.uniform(0.85, 1.25)
            markup = self.rng.uniform(0.06, 0.22)
            market_power = clamp(self.rng.betavariate(1.8, 4.5), 0.02, 0.9)
            if sector == "DigitalPlatform":
                market_power = clamp(market_power + 0.25, 0.05, 0.95)
            exporter_share = self.rng.uniform(0.05, 0.45) if sector in TRADABLE_SECTORS else self.rng.uniform(0.0, 0.05)
            platform_dep = self.rng.uniform(0.10, 0.70) if sector in {"Retail", "Food", "ProfessionalServices", "Exportables"} else self.rng.uniform(0.0, 0.25)
            f = Firm(
                fid=fid,
                sector=sector,
                region=region,
                productivity=productivity,
                capital=capital,
                cash=cash,
                debt=debt,
                bank_id=bank_id,
                wage_offer=base_wage * self.rng.uniform(0.75, 1.30),
                price=price,
                markup=markup,
                quality=clamp(self.rng.lognormvariate(0.0, 0.18), 0.55, 1.7),
                innovation=clamp(self.rng.betavariate(2.2, 4.0), 0.0, 1.0),
                automation=clamp(self.rng.betavariate(1.8, 4.2), 0.0, 1.0),
                market_power=market_power,
                energy_intensity=ENERGY_INTENSITY[sector] * self.rng.uniform(0.75, 1.35),
                emissions_intensity=EMISSIONS_INTENSITY[sector] * self.rng.uniform(0.75, 1.35),
                exporter_share=exporter_share,
                platform_dependency=platform_dep,
                inventory=self.rng.uniform(4.0, 25.0),
                expected_demand=self.rng.uniform(8.0, 40.0),
            )
            f.desired_labor = max(1, int(self.rng.uniform(2, 12) * (1.3 if sector in {"Retail", "Health", "Education"} else 1.0)))
            self.firms.append(f)

        # Create initial loan books so balance sheets are not empty.
        for h in self.households:
            if h.mortgage > 0:
                b = self.banks[h.bank_id]
                self._book_loan(b, "household", h.hid, h.mortgage, self.central_bank.policy_rate + 0.030, 240, h.home_value, "mortgage", add_cash=False)
            if h.debt > 0:
                b = self.banks[h.bank_id]
                self._book_loan(b, "household", h.hid, h.debt, self.central_bank.policy_rate + 0.075, 60, 0.0, "consumer", add_cash=False)
        for f in self.firms:
            if f.debt > 0:
                b = self.banks[f.bank_id]
                self._book_loan(b, "firm", f.fid, f.debt, self.central_bank.policy_rate + 0.050, 84, f.capital * 0.70, "investment", add_cash=False)

    def _initialize_supplier_network(self) -> None:
        by_sector = defaultdict(list)
        for f in self.firms:
            by_sector[f.sector].append(f.fid)
        for f in self.firms:
            needed = INPUT_OUTPUT.get(f.sector, {})
            suppliers = []
            for input_sector, share in needed.items():
                pool = by_sector.get(input_sector, [])
                if not pool:
                    continue
                k = 1 if share < 0.06 else 2
                for _ in range(k):
                    suppliers.append(self.rng.choice(pool))
            f.supplier_ids = list(sorted(set(suppliers)))[:6]

    def _initial_employment(self) -> None:
        workers = [h for h in self.households if h.labor_force_member()]
        self.rng.shuffle(workers)
        firms = [f for f in self.firms if f.alive()]
        for h in workers:
            if self.rng.random() < 0.08:
                continue
            local = [f for f in firms if f.region == h.region and len(f.employees) < f.desired_labor]
            if not local:
                local = [f for f in firms if len(f.employees) < f.desired_labor]
            if not local:
                continue
            weights = [f.wage_offer * (1.2 if f.sector in HIGH_SKILL_SECTORS and h.education > 0.6 else 1.0) for f in local]
            f = weighted_choice(self.rng, local, weights)
            self._hire(f, h)

    # ------------------------------------------------------------------
    # Lookup and banking helpers
    # ------------------------------------------------------------------

    def firm_by_id(self, fid: int) -> Optional[Firm]:
        if 0 <= fid < len(self.firms):
            return self.firms[fid]
        return None

    def household_by_id(self, hid: int) -> Optional[Household]:
        if 0 <= hid < len(self.households):
            return self.households[hid]
        return None

    def _book_loan(
        self,
        bank: Bank,
        borrower_kind: str,
        borrower_id: int,
        amount: float,
        rate: float,
        maturity: int,
        collateral: float,
        purpose: str,
        add_cash: bool = True,
    ) -> Loan:
        amount = max(0.0, amount)
        loan = Loan(
            loan_id=self.loan_id_counter,
            bank_id=bank.bid,
            borrower_kind=borrower_kind,
            borrower_id=borrower_id,
            principal=amount,
            rate=max(0.0, rate),
            maturity=max(1, maturity),
            collateral_value=max(0.0, collateral),
            purpose=purpose,
        )
        self.loan_id_counter += 1
        bank.loan_book[loan.loan_id] = loan
        bank.reserves -= amount * 0.12
        bank.deposits += amount * 0.85
        bank.last_new_credit += amount
        self.step_new_credit += amount
        if getattr(self, "truth_market", None) is not None and self.config.truth_market_enabled and (self.metrics or self.t > 0):
            borrower_truth = 0.10
            if borrower_kind == "firm":
                ftmp = self.firm_by_id(borrower_id)
                borrower_truth = 0.15 + 0.35 * (ftmp.model_reputation if ftmp else 0.0) - 0.25 * ((ftmp.leverage() if ftmp else 0.0) / 4.0)
            elif borrower_kind == "household":
                htmp = self.household_by_id(borrower_id)
                borrower_truth = 0.10 + 0.35 * (htmp.education if htmp else 0.0) - 0.20 * ((htmp.debt + htmp.mortgage) / max(1.0, htmp.last_income + 1.0) if htmp else 0.0)
            elif borrower_kind == "government":
                borrower_truth = 0.25 + 0.35 * self.government.planetary_trust
            if purpose == "green_investment":
                borrower_truth += 0.35
            self.truth_market.record_money_event(self, "bank", bank.bid, borrower_kind, borrower_id, amount, "credit_creation_" + purpose, fuzzy=clamp(borrower_truth, -1.0, 1.0), confidence=0.64, weight=0.65)
        if add_cash:
            if borrower_kind == "household":
                h = self.household_by_id(borrower_id)
                if h:
                    h.cash += amount
                    if purpose == "mortgage":
                        h.mortgage += amount
                    else:
                        h.debt += amount
            elif borrower_kind == "firm":
                f = self.firm_by_id(borrower_id)
                if f:
                    f.cash += amount
                    f.debt += amount
            elif borrower_kind == "government":
                self.government.cash += amount
                self.government.debt += amount
        return loan

    def request_firm_loan(self, firm: Firm, amount: float, purpose: str = "working_capital", collateral: Optional[float] = None) -> bool:
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
        truth_bonus = self.truth_market.actor_reputation(self, "firm", firm.fid) if self.config.truth_market_enabled else 0.0
        bank_truth = self.truth_market.actor_reputation(self, "bank", bank.bid) if self.config.truth_market_enabled else 0.0
        angle_bonus = self.angle_market.actor_reputation(self, "firm", firm.fid) if self.config.angle_market_enabled else 0.0
        bank_angle = self.angle_market.actor_reputation(self, "bank", bank.bid) if self.config.angle_market_enabled else 0.0
        rate = self.central_bank.policy_rate + self.financial_market.credit_spread + 0.025 + 0.035 * leverage + 0.020 * tightness - 0.010 * truth_bonus - self.config.angle_moral_credit_bonus * max(0.0, angle_bonus)
        profitability = safe_div(firm.last_profit, max(1.0, firm.last_revenue), 0.0)
        score = 1.2 * bank.risk_appetite + 0.35 * profitability + 0.45 * safe_div(collateral_value, amount, 0.0) - 0.55 * leverage - 1.3 * tightness + 0.34 * truth_bonus + 0.12 * bank_truth + 0.20 * angle_bonus + 0.08 * bank_angle
        if purpose == "green_investment":
            score += 0.15 + self.government.green_subsidy
            rate -= self.government.green_subsidy * 0.25
        approve_prob = logistic(score)
        if self.rng.random() < approve_prob:
            self._book_loan(bank, "firm", firm.fid, amount, rate, 72 if purpose != "working_capital" else 18, collateral_value, purpose)
            return True
        return False

    def request_household_loan(self, household: Household, amount: float, purpose: str = "consumer", collateral: float = 0.0) -> bool:
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
                # Stylized monthly-scale constraint.
                return False
        else:
            if total_debt > max(4.0, income * 6.0):
                return False
        tightness = bank.credit_tightness(self.config.bank_capital_requirement, self.financial_market.financial_stress)
        truth_bonus = self.truth_market.actor_reputation(self, "household", household.hid) if self.config.truth_market_enabled else 0.0
        angle_bonus = self.angle_market.actor_reputation(self, "household", household.hid) if self.config.angle_market_enabled else 0.0
        risk = 0.35 * household.risk_aversion + 0.45 * safe_div(total_debt, max(1.0, income * 12.0), 0.0) + 0.35 * (not household.employed) - 0.18 * truth_bonus - 0.12 * angle_bonus
        collateral_score = safe_div(collateral, amount, 0.0)
        score = 1.0 * bank.risk_appetite + 0.25 * collateral_score + 0.18 * household.education - risk - 1.1 * tightness + 0.28 * truth_bonus + 0.18 * angle_bonus
        approve_prob = logistic(score)
        if self.rng.random() < approve_prob:
            rate = self.central_bank.policy_rate + self.financial_market.credit_spread + (0.028 if purpose == "mortgage" else 0.075) + 0.025 * risk - 0.006 * truth_bonus - self.config.angle_moral_credit_bonus * max(0.0, angle_bonus)
            maturity = 240 if purpose == "mortgage" else 48
            self._book_loan(bank, "household", household.hid, amount, rate, maturity, collateral, purpose)
            return True
        return False

    # ------------------------------------------------------------------
    # Simulation step
    # ------------------------------------------------------------------

    def run(self) -> List[Dict[str, float]]:
        for t in range(self.config.steps):
            self.t = t
            self.step()
        return self.metrics

    def step(self) -> None:
        self._reset_step_counters()
        self.scenarios.apply_pre_step(self)
        pressure = self.scenarios.pressure(self.t)
        self.energy_market.pre_step_update(self.rng, self.government, pressure)
        self.foreign_sector.update_pre(self.rng, self.central_bank.policy_rate, self.metrics_last.get("inflation", 0.0), pressure)
        self._update_policy_pre_market()
        self._labor_market()
        self._production()
        self._household_income_taxes_and_rents()
        self._goods_and_services_market()
        self._corporate_taxes_and_debt_service()
        self._credit_investment_and_capital_formation()
        self._housing_and_mortgages()
        self._health_education_demography()
        self._insurance_market()
        self._platform_market()
        self._truth_currency_market()
        self._banking_system()
        self._financial_market()
        self._foreign_sector_finalize()
        self._government_finalize()
        self._bankruptcy_resolution()
        self.scenarios.apply_post_step(self)
        self._collect_metrics()

    def _reset_step_counters(self) -> None:
        if self.config.truth_market_enabled:
            self.truth_market.start_step(self)
        if self.config.angle_market_enabled:
            self.angle_market.start_step(self)
        self.step_household_defaults = 0
        self.step_firm_bankruptcies = 0
        self.step_bank_failures = 0
        self.step_new_credit = 0.0
        self.step_imports = 0.0
        self.step_exports = 0.0
        self.government.reset_flows()
        for b in self.banks:
            b.last_interest_income = 0.0
            b.last_deposit_cost = 0.0
            b.last_new_credit = 0.0
            b.last_writeoffs = 0.0
        for f in self.firms:
            f.last_revenue = 0.0
            f.last_cost = 0.0
            f.last_profit = 0.0
            f.last_quantity_sold = 0.0
            f.last_unfilled_demand = 0.0
            f.last_wage_bill = 0.0
            f.last_energy_bill = 0.0
            f.last_input_bill = 0.0
            f.last_tax = 0.0
            f.output = 0.0
        self.sector_output = {s: 0.0 for s in SECTORS}
        self.sector_revenue = {s: 0.0 for s in SECTORS}
        self.sector_unfilled = {s: 0.0 for s in SECTORS}

    def _update_policy_pre_market(self) -> None:
        self.government.income_tax = self.config.income_tax
        self.government.corporate_tax = self.config.corporate_tax
        self.government.vat = self.config.vat
        self.government.capital_tax = self.config.capital_tax
        self.government.property_tax = self.config.property_tax
        self.government.unemployment_replacement = self.config.unemployment_benefit_replacement
        self.government.basic_transfer = self.config.basic_transfer
        self.government.public_education_quality = clamp(self.config.public_education_intensity * (1.0 + 0.0007 * self.government.last_spending), 0.55, 1.60)
        self.government.public_health_quality = clamp(self.config.public_health_intensity * (1.0 + 0.0006 * self.government.last_spending), 0.55, 1.55)
        self.government.infrastructure_quality = clamp(self.config.infrastructure_intensity * (1.0 + 0.0004 * self.government.last_spending), 0.50, 1.50)
        if self.config.policy_mode == "green":
            self.government.green_subsidy = max(self.government.green_subsidy, 0.035)
            self.government.carbon_price = max(self.government.carbon_price, self.config.carbon_price + 0.0005 * self.t)
        elif self.config.policy_mode == "austerity":
            self.government.basic_transfer *= 0.995
            self.government.public_education_quality *= 0.998
            self.government.public_health_quality *= 0.998
        elif self.config.policy_mode == "stimulus":
            self.government.basic_transfer = max(self.government.basic_transfer, 0.10)
            self.government.infrastructure_quality = max(self.government.infrastructure_quality, 1.12)

    # ------------------------------------------------------------------
    # Labor market
    # ------------------------------------------------------------------

    def _labor_market(self) -> None:
        unemployment = self.metrics_last.get("unemployment", 0.06)
        sector_hhi = self._compute_sector_hhi()
        # Firms revise labor demand and wage offers.
        for f in self.firms:
            if not f.alive():
                continue
            pressure = safe_div(f.expected_demand, max(1.0, f.inventory + f.output), 1.0) - 1.0
            labor_prod_proxy = max(0.6, f.productivity * (0.7 + 0.5 * f.automation) * (max(1.0, f.capital) ** 0.12))
            desired = int(max(0.0, f.expected_demand * (1.0 + 0.20 * max(0.0, pressure)) / labor_prod_proxy))
            if f.sector in HIGH_SKILL_SECTORS:
                desired = int(desired * 0.90)
            if f.sector == "DigitalPlatform":
                desired = int(desired * (0.75 + 0.35 * (1.0 - f.automation)))
            if f.sector == "GovernmentSupply":
                desired = int(desired * (0.85 + 0.25 * self.government.infrastructure_quality))
            f.desired_labor = max(0, int(clamp(0.65 * f.desired_labor + 0.35 * desired, 0, 250)))
            demand_pressure = clamp(pressure, -1.0, 1.5)
            concentration = sector_hhi.get(f.sector, 0.0)
            # More unemployment suppresses wages; tight markets lift them.
            wage_change = 0.008 * demand_pressure - 0.018 * max(0.0, unemployment - self.config.natural_unemployment) + 0.004 * f.quality
            if f.sector in HIGH_SKILL_SECTORS:
                wage_change += 0.004 * (1.0 - unemployment)
            if concentration > 0.30:
                wage_change -= 0.004 * concentration  # monopsony-ish wage pressure
            f.wage_offer = max(0.25, f.wage_offer * (1.0 + clamp(wage_change, -0.035, 0.04)))

        # Fire excess labor or bankrupt-firm workers.
        for f in self.firms:
            if not f.alive():
                self._separate_all(f)
                continue
            excess = len(f.employees) - f.desired_labor
            if excess > 0:
                self.rng.shuffle(f.employees)
                for hid in f.employees[:excess]:
                    h = self.household_by_id(hid)
                    if h:
                        self._separate(h)

        unemployed = [h for h in self.households if h.labor_force_member() and not h.employed]
        self.rng.shuffle(unemployed)
        vacancies = []
        for f in self.firms:
            if f.alive():
                for _ in range(max(0, f.desired_labor - len(f.employees))):
                    vacancies.append(f)
        self.rng.shuffle(vacancies)
        # Group candidates by region for speed.
        unemployed_by_region: Dict[str, List[Household]] = defaultdict(list)
        for h in unemployed:
            unemployed_by_region[h.region].append(h)
        all_unemployed = unemployed[:]

        for f in vacancies:
            if not all_unemployed:
                break
            local_pool = unemployed_by_region.get(f.region, [])
            use_local = local_pool and self.rng.random() > self.config.labor_mobility
            pool = local_pool if use_local else all_unemployed
            if not pool:
                continue
            # Sample a small candidate set rather than sorting everybody.
            sample_size = min(len(pool), 8)
            candidates = self.rng.sample(pool, sample_size)
            best = None
            best_score = -1e9
            for h in candidates:
                if h.employed or not h.labor_force_member():
                    continue
                skill_fit = h.education if f.sector in HIGH_SKILL_SECTORS else (1.0 - abs(h.education - 0.45))
                region_bonus = 0.25 if h.region == f.region else -0.15
                long_unemp_penalty = 0.02 * h.unemployment_duration
                score = 0.70 * h.labor_productivity() + 0.35 * skill_fit + 0.12 * f.wage_offer + region_bonus - long_unemp_penalty + self.rng.gauss(0.0, 0.08)
                if score > best_score:
                    best_score = score
                    best = h
            if best is not None and self.rng.random() < logistic(best_score - 1.0):
                self._hire(f, best)
                if best in all_unemployed:
                    all_unemployed.remove(best)
                if best in unemployed_by_region.get(best.region, []):
                    unemployed_by_region[best.region].remove(best)

        for h in self.households:
            if h.labor_force_member() and not h.employed:
                h.unemployment_duration += 1
            elif h.employed:
                h.unemployment_duration = 0

    def _hire(self, firm: Firm, household: Household) -> None:
        if household.employed:
            self._separate(household)
        household.employed = True
        household.employer_id = firm.fid
        household.wage = firm.wage_offer * household.labor_productivity() * self.rng.uniform(0.88, 1.12)
        household.unemployment_duration = 0
        if household.hid not in firm.employees:
            firm.employees.append(household.hid)

    def _separate(self, household: Household) -> None:
        if household.employer_id is not None:
            f = self.firm_by_id(household.employer_id)
            if f and household.hid in f.employees:
                try:
                    f.employees.remove(household.hid)
                except ValueError:
                    pass
        household.employed = False
        household.employer_id = None
        household.wage = 0.0

    def _separate_all(self, firm: Firm) -> None:
        for hid in list(firm.employees):
            h = self.household_by_id(hid)
            if h:
                h.employed = False
                h.employer_id = None
                h.wage = 0.0
        firm.employees.clear()

    # ------------------------------------------------------------------
    # Production and goods market
    # ------------------------------------------------------------------

    def _production(self) -> None:
        sector_prices = self._sector_prices_from_firms()
        economy_supply_pressure = 0.0
        total_energy_demand = 0.0
        total_emissions = 0.0
        green_investment = 0.0
        for f in self.firms:
            if not f.alive():
                continue
            labor_effort = sum(self.household_by_id(hid).labor_productivity() for hid in f.employees if self.household_by_id(hid))
            # Supply-chain constraint worsens when suppliers have poor inventory/profits.
            supplier_health = 1.0
            if f.supplier_ids:
                scores = []
                for sid in f.supplier_ids:
                    sfirm = self.firm_by_id(sid)
                    if sfirm and sfirm.alive():
                        scores.append(clamp(0.65 + 0.20 * safe_div(sfirm.inventory, max(1.0, sfirm.expected_demand), 1.0) + 0.15 * (sfirm.last_profit >= 0), 0.2, 1.2))
                    else:
                        scores.append(0.35)
                supplier_health = mean(scores, 0.8)
            supply_constraint = clamp(supplier_health - 0.55 * f.supply_chain_fragility, 0.20, 1.15)
            energy_need = max(0.0, f.expected_demand * f.energy_intensity * (0.7 + 0.4 * f.productivity))
            energy_constraint = clamp(1.0 - 0.65 * self.energy_market.shortage_ratio, 0.25, 1.05)
            if self.config.truth_market_enabled:
                truth_throttle = self.truth_market.production_throttle_for_firm(f)
                energy_constraint *= truth_throttle
                supply_constraint *= clamp(0.70 + 0.30 * truth_throttle, 0.15, 1.10)
            capacity = f.production_capacity(labor_effort, energy_constraint, supply_constraint)
            desired = max(0.0, 0.65 * f.expected_demand + 0.35 * max(0.0, f.expected_demand - f.inventory))
            f.output = min(capacity, desired * self.rng.uniform(0.92, 1.08))
            f.inventory += f.output
            self.sector_output[f.sector] += f.output
            # Cost accrual.
            wage_bill = sum(self.household_by_id(hid).wage for hid in f.employees if self.household_by_id(hid))
            io = INPUT_OUTPUT.get(f.sector, {})
            input_bill = 0.0
            for input_sector, share in io.items():
                input_bill += share * f.output * sector_prices.get(input_sector, INITIAL_PRICE[input_sector]) * self.foreign_sector.import_price_index ** (0.25 if input_sector in TRADABLE_SECTORS else 0.0)
            energy_bill = f.output * f.energy_intensity * self.energy_market.energy_price
            carbon_tax = f.output * f.emissions_intensity * self.government.carbon_price * (1.0 - self.energy_market.renewable_share)
            depreciation = 0.006 * f.capital
            # Actual wages are paid later in _household_income_taxes_and_rents.
            # Keep wage_bill out of last_cost here to avoid double-counting labor costs.
            f.last_wage_bill = 0.0
            f.last_input_bill = input_bill
            f.last_energy_bill = energy_bill
            f.last_cost += input_bill + energy_bill + carbon_tax + depreciation
            f.cash -= input_bill + energy_bill + carbon_tax + depreciation
            if carbon_tax > 0:
                self.government.collect(carbon_tax)
                self.government.carbon_revenue += carbon_tax
                if self.config.truth_market_enabled:
                    self.truth_market.record_money_event(self, "firm", f.fid, "government", 0, carbon_tax, "carbon_tax_emissions", fuzzy=0.45 + 0.35 * self.energy_market.renewable_share - 0.35 * f.emissions_intensity, confidence=0.68, weight=0.55)
            if self.config.truth_market_enabled and f.output > EPS:
                resource_bundle = self.truth_market.firm_resource_bundle(f, f.output, self)
                resource_value_base = max(0.0, input_bill + energy_bill + carbon_tax + depreciation)
                for resource, (amount_used, expected_amount) in resource_bundle.items():
                    self.truth_market.record_resource_use(self, "firm", f.fid, resource, amount_used, expected_amount, f.sector, monetary_amount=resource_value_base)
            total_energy_demand += f.output * f.energy_intensity
            total_emissions += f.output * f.emissions_intensity * (1.0 - self.energy_market.renewable_share)
            if f.sector == "Energy" or f.emissions_intensity < 0.08:
                green_investment += max(0.0, f.last_profit) * 0.05 + max(0.0, self.government.green_subsidy * f.output)
            economy_supply_pressure += max(0.0, safe_div(f.expected_demand, max(1.0, f.inventory), 1.0) - 1.0)
        # Households also demand direct energy and receive resource-truth predicates.
        household_energy_demand = 0.0
        for h in self.households:
            direct = (1.0 + 0.30 * h.children) * h.energy_efficiency * 0.045
            household_energy_demand += direct
            if self.config.truth_market_enabled:
                bundle = self.truth_market.household_resource_bundle(h, max(0.0, h.last_consumption), direct)
                for resource, (amount_used, expected_amount) in bundle.items():
                    self.truth_market.record_resource_use(self, "household", h.hid, resource, amount_used, expected_amount, "Household", monetary_amount=max(0.0, h.last_consumption))
        total_energy_demand += household_energy_demand
        self.energy_market.post_step_update(total_energy_demand, self.sector_output.get("Energy", 0.0), total_emissions, green_investment)

    def _goods_and_services_market(self) -> None:
        macro_uncertainty = clamp(self.financial_market.financial_stress + self.energy_market.shortage_ratio + abs(self.metrics_last.get("inflation", 0.0)) * 10.0, 0.0, 2.0)
        sector_demand: Dict[str, float] = {s: 0.0 for s in SECTORS}
        sector_spending: Dict[str, float] = {s: 0.0 for s in SECTORS}

        # Household consumption.
        cpi = max(0.2, self.metrics_last.get("cpi", 1.0))
        for h in self.households:
            disposable = max(0.0, h.cash)
            mpc = h.propensity_to_consume(macro_uncertainty)
            budget = disposable * mpc
            # Keep a minimal liquidity floor if possible.
            budget = min(budget, max(0.0, disposable - 0.25 * h.liquidity_need()))
            if budget <= EPS:
                h.last_consumption = 0.0
                continue
            prefs = {s: h.sector_preference(s, self.energy_market.energy_price, cpi) for s in SECTORS}
            total_pref = sum(prefs.values())
            if total_pref <= EPS:
                continue
            spent = 0.0
            for sector, pref in prefs.items():
                if pref <= 0:
                    continue
                amount_money = budget * pref / total_pref
                sector_demand[sector] += amount_money / max(0.05, self.sector_price_index.get(sector, INITIAL_PRICE[sector]))
                sector_spending[sector] += amount_money
                spent += amount_money
            h.cash -= spent
            h.last_consumption = spent
            vat = spent * self.government.vat / (1.0 + self.government.vat)
            self.government.collect(vat)
            if self.config.truth_market_enabled:
                consume_truth = self.truth_market.consumer_spending_truth(h, spent, prefs)
                self.truth_market.record_money_event(self, "household", h.hid, "market", 0, spent, "household_consumption", fuzzy=consume_truth, confidence=0.55, weight=0.50)
                if vat > EPS:
                    self.truth_market.record_money_event(self, "household", h.hid, "government", 0, vat, "vat_tax", fuzzy=0.20 + 0.25 * self.government.planetary_trust, confidence=0.58, weight=0.25)

        # Government demand: public services, infrastructure, stabilizers.
        unemployment = self.metrics_last.get("unemployment", 0.06)
        gdp_last = max(self.metrics_last.get("gdp", 100.0), self.config.households * 2.0)
        public_budget = (0.07 + 0.08 * self.config.infrastructure_intensity + 0.05 * unemployment) * gdp_last
        if self.config.policy_mode == "austerity":
            public_budget *= 0.78
        elif self.config.policy_mode == "stimulus":
            public_budget *= 1.30
        public_alloc = {
            "Health": 0.26 * self.config.public_health_intensity,
            "Education": 0.22 * self.config.public_education_intensity,
            "GovernmentSupply": 0.25,
            "Construction": 0.17 * self.config.infrastructure_intensity,
            "Transport": 0.10 * self.config.infrastructure_intensity,
        }
        total_alloc = sum(public_alloc.values())
        for sector, w in public_alloc.items():
            spending = public_budget * w / max(EPS, total_alloc)
            sector_demand[sector] += spending / max(0.05, self.sector_price_index.get(sector, INITIAL_PRICE[sector]))
            sector_spending[sector] += spending
            self.government.spend(spending)
            if self.config.truth_market_enabled:
                public_truth = 0.35 + 0.25 * (sector in {"Health", "Education"}) + 0.20 * (sector == "Construction") * self.government.infrastructure_quality
                self.truth_market.record_money_event(self, "government", 0, "market", 0, spending, "public_spending_" + sector, fuzzy=clamp(public_truth, -1.0, 1.0), confidence=0.61, weight=0.45)

        # Firm investment demand for capital goods and professional services.
        for f in self.firms:
            if not f.alive():
                continue
            default_investment = f.capital * 0.025 if self.t <= 1 else 0.0
            invest_budget = max(0.0, getattr(f, "planned_investment_budget", default_investment))
            if invest_budget > 0:
                cap_sector = "Manufacturing" if f.sector != "Construction" else "Construction"
                service_sector = "ProfessionalServices"
                sector_demand[cap_sector] += (0.72 * invest_budget) / max(0.05, self.sector_price_index.get(cap_sector, 1.0))
                sector_spending[cap_sector] += 0.72 * invest_budget
                sector_demand[service_sector] += (0.28 * invest_budget) / max(0.05, self.sector_price_index.get(service_sector, 1.0))
                sector_spending[service_sector] += 0.28 * invest_budget
                f.cash -= invest_budget
                if self.config.truth_market_enabled:
                    investment_truth = 0.25 + 0.35 * f.innovation + 0.25 * (f.sector == "Energy" or f.emissions_intensity < 0.08) - 0.20 * f.resource_overuse_score
                    self.truth_market.record_money_event(self, "firm", f.fid, "market", 0, invest_budget, "productive_investment", fuzzy=clamp(investment_truth, -1.0, 1.0), confidence=0.62, weight=0.50)

        # Exports.
        self.step_exports = 0.0
        for sector in TRADABLE_SECTORS:
            competitiveness = 1.0 / max(0.2, self.sector_price_index.get(sector, 1.0) * self.foreign_sector.exchange_rate)
            export_scale = max(1.0, self.config.households / 80.0)
            export_qty = self.foreign_sector.export_demand_index * competitiveness * self.rng.uniform(0.8, 1.2)
            export_qty *= export_scale * (9.0 if sector == "Exportables" else 2.6)
            sector_demand[sector] += export_qty
            export_value = export_qty * self.sector_price_index.get(sector, 1.0)
            sector_spending[sector] += export_value
            self.step_exports += export_value
            if self.config.truth_market_enabled and export_value > EPS:
                self.truth_market.record_money_event(self, "government", 0, "foreign", 0, export_value, "export_" + sector, fuzzy=0.20 + 0.25 * competitiveness - 0.15 * (sector == "Energy"), confidence=0.54, weight=0.25)

        # Allocate sector demand to firms.
        firms_by_sector: Dict[str, List[Firm]] = defaultdict(list)
        for f in self.firms:
            if f.alive():
                firms_by_sector[f.sector].append(f)

        self.step_imports = 0.0
        for sector in SECTORS:
            demand_qty = max(0.0, sector_demand.get(sector, 0.0))
            firms = firms_by_sector.get(sector, [])
            if not firms:
                # If tradable, imports satisfy some demand.
                if sector in TRADABLE_SECTORS:
                    imports = demand_qty * self.sector_price_index.get(sector, 1.0) * self.foreign_sector.import_price_index
                    self.step_imports += imports
                    if self.config.truth_market_enabled and imports > EPS:
                        self.truth_market.record_money_event(self, "government", 0, "foreign", 0, imports, "import_unfilled_" + sector, fuzzy=-0.10 - 0.25 * (sector == "Energy"), confidence=0.50, weight=0.25)
                self.sector_unfilled[sector] += demand_qty
                continue
            weights = []
            for f in firms:
                price_score = 1.0 / max(0.05, f.price)
                quality_score = f.quality
                locality = 1.05
                platform_score = 1.0 + self.platform_market.user_share * f.platform_dependency * 0.25
                inventory_score = clamp(f.inventory / max(1.0, f.expected_demand), 0.2, 2.0)
                weights.append(max(0.001, price_score * quality_score * platform_score * inventory_score * locality * (1.0 + f.market_power)))
            total_weight = sum(weights)
            remaining_demand = demand_qty
            for f, w in zip(firms, weights):
                share = w / max(EPS, total_weight)
                target_qty = demand_qty * share
                sold_qty = min(f.inventory, target_qty)
                revenue = sold_qty * f.price
                f.inventory -= sold_qty
                f.cash += revenue
                f.last_revenue += revenue
                f.last_quantity_sold += sold_qty
                self.sector_revenue[sector] += revenue
                remaining_demand -= sold_qty
                if self.config.truth_market_enabled and revenue > EPS:
                    sale_truth = 0.10 + 0.25 * f.quality + 0.20 * f.model_reputation - 0.30 * f.resource_overuse_score
                    self.truth_market.record_money_event(self, "firm", f.fid, "market", 0, revenue, "market_sale_" + sector, fuzzy=clamp(sale_truth, -1.0, 1.0), confidence=0.52, weight=0.22)
            if remaining_demand > EPS:
                importable = sector in TRADABLE_SECTORS
                if importable:
                    import_qty = remaining_demand * clamp(0.65 + 0.25 * self.foreign_sector.exchange_rate, 0.35, 1.0)
                    import_value = import_qty * self.sector_price_index.get(sector, 1.0) * self.foreign_sector.import_price_index
                    self.step_imports += import_value
                    if self.config.truth_market_enabled and import_value > EPS:
                        import_truth = -0.05 - 0.20 * (sector == "Energy") - 0.08 * max(0.0, self.foreign_sector.import_price_index - 1.0)
                        self.truth_market.record_money_event(self, "government", 0, "foreign", 0, import_value, "import_substitution_" + sector, fuzzy=clamp(import_truth, -1.0, 1.0), confidence=0.50, weight=0.25)
                    remaining_demand -= import_qty
                self.sector_unfilled[sector] += max(0.0, remaining_demand)
            # Expectations and prices update after sales.
            sector_pressure = safe_div(demand_qty, max(1.0, sum(max(0.0, f.output + f.inventory) for f in firms)), 1.0) - 1.0
            concentration = self.sector_hhi.get(sector, 0.0)
            for f in firms:
                realized = f.last_quantity_sold
                f.expected_demand = clamp(0.72 * f.expected_demand + 0.28 * (realized + max(0.0, sector_pressure) * realized), 0.1, 10000.0)
                unit_cost = safe_div(f.last_cost, max(1.0, f.output), 0.0)
                demand_pressure = safe_div(realized, max(1.0, f.output), 1.0) - 1.0
                policy_pressure = self.government.regulatory_pressure if f.sector in {"DigitalPlatform", "Finance", "HousingServices"} else 0.0
                f.markup = f.target_markup(concentration, demand_pressure, policy_pressure)
                target_price = max(0.05, unit_cost * (1.0 + f.markup))
                # Firms do not instantly jump to target; they adjust with pricing frictions.
                f.price = max(0.04, 0.80 * f.price + 0.20 * target_price)
                # Shortages can lift prices even above cost target.
                if sector_pressure > 0.05:
                    f.price *= 1.0 + clamp(0.015 * sector_pressure + 0.020 * f.market_power, 0.0, 0.045)
                elif f.inventory > f.expected_demand * 1.8:
                    f.price *= 0.990
        self.foreign_sector.update_post(self.step_imports, self.step_exports)
        self.sector_price_index = self._sector_prices_from_firms()

    # ------------------------------------------------------------------
    # Income, taxes, transfers, rents
    # ------------------------------------------------------------------

    def _household_income_taxes_and_rents(self) -> None:
        average_wage = mean((h.wage for h in self.households if h.employed), 2.5)
        rent_pool = 0.0
        for h in self.households:
            h.last_income = 0.0
            h.last_taxes = 0.0
            income = 0.0
            if h.employed and h.employer_id is not None:
                f = self.firm_by_id(h.employer_id)
                if f and f.alive():
                    wage = h.wage
                    f.cash -= wage
                    f.last_cost += wage
                    f.last_wage_bill += wage
                    income += wage
                    if self.config.truth_market_enabled:
                        fair_wage = clamp(0.20 + 0.55 * safe_div(wage, max(0.1, average_wage), 1.0) + 0.15 * h.education - 0.15 * f.market_power, -1.0, 1.0)
                        self.truth_market.record_money_event(self, "firm", f.fid, "household", h.hid, wage, "wage_payment", fuzzy=fair_wage, confidence=0.66, weight=0.55)
                else:
                    self._separate(h)
            else:
                if h.labor_force_member():
                    benefit = self.government.unemployment_replacement * average_wage * clamp(1.0 - 0.006 * h.unemployment_duration, 0.60, 1.0)
                    income += benefit
                    self.government.spend(benefit)
                    self.government.last_transfers += benefit
                    if self.config.truth_market_enabled and benefit > EPS:
                        self.truth_market.record_money_event(self, "government", 0, "household", h.hid, benefit, "unemployment_transfer", fuzzy=0.45 + 0.20 * h.unemployment_duration / 12.0, confidence=0.58, weight=0.35)
            # Basic transfer, pensions, dividends.
            transfer = self.government.basic_transfer
            if h.age > 67:
                pension = 0.45 * average_wage * (0.7 + 0.6 * h.pension_wealth / max(1.0, h.pension_wealth + 20.0))
                income += pension
                self.government.spend(pension)
                self.government.last_transfers += pension
                if self.config.truth_market_enabled and pension > EPS:
                    self.truth_market.record_money_event(self, "government", 0, "household", h.hid, pension, "pension_transfer", fuzzy=0.42 + 0.20 * self.government.planetary_trust, confidence=0.58, weight=0.30)
            if transfer > 0:
                income += transfer
                self.government.spend(transfer)
                self.government.last_transfers += transfer
                if self.config.truth_market_enabled and transfer > EPS:
                    self.truth_market.record_money_event(self, "government", 0, "household", h.hid, transfer, "basic_transfer", fuzzy=0.35 + 0.25 * self.government.planetary_trust, confidence=0.55, weight=0.25)
            # Capital income and asset returns.
            cap_income = max(0.0, h.asset_portfolio) * (0.002 + max(0.0, self.financial_market.last_return) * 0.08)
            if cap_income > 0:
                tax = cap_income * self.government.capital_tax
                cap_income -= tax
                self.government.collect(tax)
                h.last_taxes += tax
                if self.config.truth_market_enabled and tax > EPS:
                    self.truth_market.record_money_event(self, "household", h.hid, "government", 0, tax, "capital_income_tax", fuzzy=0.15 + 0.20 * self.government.planetary_trust, confidence=0.54, weight=0.20)
                income += cap_income
            # Income tax.
            tax = max(0.0, income) * self.government.income_tax
            income -= tax
            self.government.collect(tax)
            h.last_taxes += tax
            if self.config.truth_market_enabled and tax > EPS:
                self.truth_market.record_money_event(self, "household", h.hid, "government", 0, tax, "income_tax", fuzzy=0.20 + 0.20 * self.government.planetary_trust, confidence=0.55, weight=0.20)
            # Rent and property tax.
            if not h.home_owner:
                rent = min(max(0.0, h.rent_payment), max(0.0, income + h.cash) * 0.55)
                h.cash -= max(0.0, rent - income)
                income -= min(income, rent)
                rent_pool += rent
                if self.config.truth_market_enabled and rent > EPS:
                    rent_truth = 0.25 - 0.45 * self.housing_market.affordability.get(h.region, 0.4) + 0.20 * (h.home_owner == False)
                    self.truth_market.record_money_event(self, "household", h.hid, "market", 0, rent, "rent_payment", fuzzy=clamp(rent_truth, -1.0, 1.0), confidence=0.52, weight=0.25)
            else:
                prop_tax = max(0.0, h.home_value) * self.government.property_tax
                pay = min(max(0.0, h.cash + income), prop_tax)
                if income >= pay:
                    income -= pay
                else:
                    h.cash -= pay - income
                    income = 0.0
                self.government.collect(pay)
                h.last_taxes += pay
                if self.config.truth_market_enabled and pay > EPS:
                    self.truth_market.record_money_event(self, "household", h.hid, "government", 0, pay, "property_tax", fuzzy=0.20 + 0.15 * self.government.planetary_trust, confidence=0.55, weight=0.20)
            h.cash += income
            h.last_income = max(0.0, income + h.last_taxes)

        # Rent pool distribution: homeowners and housing-service firms receive landlord income.
        homeowners = [h for h in self.households if h.home_owner and h.home_value > 0]
        owner_weight = sum(h.home_value for h in homeowners)
        if owner_weight > EPS:
            for h in homeowners:
                h.cash += rent_pool * 0.55 * h.home_value / owner_weight
        housing_firms = [f for f in self.firms if f.alive() and f.sector == "HousingServices"]
        if housing_firms:
            wsum = sum(max(0.01, f.capital) for f in housing_firms)
            for f in housing_firms:
                rev = rent_pool * 0.35 * max(0.01, f.capital) / wsum
                f.cash += rev
                f.last_revenue += rev
                self.sector_revenue[f.sector] += rev
        self.government.collect(rent_pool * 0.10 * self.government.vat)

        # Deposit interest and debt service for household loans.
        for h in self.households:
            if h.cash > 0:
                dep_interest = h.cash * max(0.0, self.central_bank.policy_rate - 0.006) / 12.0
                h.cash += dep_interest
                b = self.banks[h.bank_id]
                b.last_deposit_cost += dep_interest
                b.equity -= dep_interest
                if self.config.truth_market_enabled and dep_interest > EPS:
                    self.truth_market.record_money_event(self, "bank", b.bid, "household", h.hid, dep_interest, "deposit_interest", fuzzy=0.10 + 0.20 * self.truth_market.actor_reputation(self, "bank", b.bid), confidence=0.52, weight=0.15)
            # loan payments are managed through bank loan books.

    # ------------------------------------------------------------------
    # Debt service, credit, investment
    # ------------------------------------------------------------------

    def _corporate_taxes_and_debt_service(self) -> None:
        for f in self.firms:
            if not f.alive():
                continue
            f.last_profit = f.last_revenue - f.last_cost
            if f.last_profit > 0:
                tax = f.last_profit * self.government.corporate_tax
                f.cash -= tax
                f.last_tax = tax
                f.last_profit -= tax
                self.government.collect(tax)
                if self.config.truth_market_enabled and tax > EPS:
                    tax_truth = 0.18 + 0.20 * self.government.planetary_trust + 0.15 * f.model_reputation - 0.18 * f.resource_overuse_score
                    self.truth_market.record_money_event(self, "firm", f.fid, "government", 0, tax, "corporate_tax", fuzzy=clamp(tax_truth, -1.0, 1.0), confidence=0.58, weight=0.22)

        # Loan servicing across banks.
        for bank in self.banks:
            if bank.failed:
                continue
            for loan in list(bank.loan_book.values()):
                if loan.status != "performing" or loan.principal <= EPS:
                    continue
                borrower_cash_getter = self._borrower_cash_getter(loan)
                borrower_cash_setter = self._borrower_cash_setter(loan)
                if borrower_cash_getter is None or borrower_cash_setter is None:
                    self._default_loan(bank, loan, reason="borrower missing")
                    continue
                due = loan.scheduled_payment()
                interest = loan.interest_due()
                cash = borrower_cash_getter()
                if cash >= due:
                    borrower_cash_setter(cash - due)
                    principal_pay = max(0.0, due - interest)
                    loan.principal = max(0.0, loan.principal - principal_pay)
                    loan.age += 1
                    bank.reserves += due * 0.18
                    bank.equity += interest * 0.75
                    bank.last_interest_income += interest
                    if self.config.truth_market_enabled and due > EPS:
                        payer_truth = 0.18 + 0.20 * (principal_pay > 0) - 0.10 * (loan.rate > self.central_bank.policy_rate + 0.08)
                        self.truth_market.record_money_event(self, loan.borrower_kind, loan.borrower_id, "bank", bank.bid, due, "loan_service_" + loan.purpose, fuzzy=clamp(payer_truth, -1.0, 1.0), confidence=0.60, weight=0.20)
                    self._reduce_borrower_debt_field(loan, principal_pay)
                    if loan.principal <= 0.01:
                        loan.status = "paid"
                else:
                    # Partial payment, then delinquency. Productive firms are sometimes restructured
                    # instead of immediately forced into default; this avoids turning baseline
                    # inventory cycles into mechanical mass bankruptcies.
                    if loan.borrower_kind == "firm":
                        firm = self.firm_by_id(loan.borrower_id)
                        if firm is not None and firm.alive() and firm.last_revenue > 0.35 * due and loan.delinquency < 5:
                            loan.principal += max(0.0, interest) * 0.55
                            loan.maturity += 6
                            loan.age += 1
                            loan.delinquency = max(0, loan.delinquency - 1)
                            bank.equity -= max(0.0, interest) * 0.05
                            continue
                    pay = max(0.0, cash)
                    if pay > 0:
                        borrower_cash_setter(0.0)
                        principal_pay = max(0.0, pay - interest)
                        loan.principal = max(0.0, loan.principal - principal_pay)
                        bank.reserves += pay * 0.12
                        bank.equity += min(pay, interest) * 0.50
                        if self.config.truth_market_enabled and pay > EPS:
                            self.truth_market.record_money_event(self, loan.borrower_kind, loan.borrower_id, "bank", bank.bid, pay, "partial_loan_service_" + loan.purpose, fuzzy=-0.15 + 0.20 * safe_div(pay, max(EPS, due), 0.0), confidence=0.56, weight=0.16)
                        self._reduce_borrower_debt_field(loan, principal_pay)
                    loan.delinquency += 1
                    loan.age += 1
                    severe_firm_distress = False
                    if loan.borrower_kind == "firm":
                        firm = self.firm_by_id(loan.borrower_id)
                        if firm is not None:
                            severe_firm_distress = firm.cash < -max(60.0, 1.50 * firm.capital) and loan.delinquency >= 3
                    if loan.delinquency >= 12 or severe_firm_distress:
                        self._default_loan(bank, loan, reason="delinquency")

    def _borrower_cash_getter(self, loan: Loan):
        if loan.borrower_kind == "household":
            h = self.household_by_id(loan.borrower_id)
            if not h:
                return None
            return lambda h=h: h.cash
        if loan.borrower_kind == "firm":
            f = self.firm_by_id(loan.borrower_id)
            if not f or f.bankrupt:
                return None
            return lambda f=f: f.cash
        if loan.borrower_kind == "government":
            return lambda: self.government.cash
        return None

    def _borrower_cash_setter(self, loan: Loan):
        if loan.borrower_kind == "household":
            h = self.household_by_id(loan.borrower_id)
            if not h:
                return None
            return lambda value, h=h: setattr(h, "cash", value)
        if loan.borrower_kind == "firm":
            f = self.firm_by_id(loan.borrower_id)
            if not f or f.bankrupt:
                return None
            return lambda value, f=f: setattr(f, "cash", value)
        if loan.borrower_kind == "government":
            return lambda value: setattr(self.government, "cash", value)
        return None

    def _reduce_borrower_debt_field(self, loan: Loan, principal_pay: float) -> None:
        if principal_pay <= 0:
            return
        if loan.borrower_kind == "household":
            h = self.household_by_id(loan.borrower_id)
            if h:
                if loan.purpose == "mortgage":
                    h.mortgage = max(0.0, h.mortgage - principal_pay)
                else:
                    h.debt = max(0.0, h.debt - principal_pay)
        elif loan.borrower_kind == "firm":
            f = self.firm_by_id(loan.borrower_id)
            if f:
                f.debt = max(0.0, f.debt - principal_pay)
        elif loan.borrower_kind == "government":
            self.government.debt = max(0.0, self.government.debt - principal_pay)

    def _default_loan(self, bank: Bank, loan: Loan, reason: str) -> None:
        if loan.status != "performing":
            return
        recovery_rate = 0.0
        if loan.collateral_value > 0:
            recovery_rate = clamp(0.20 + 0.65 * safe_div(loan.collateral_value, loan.principal, 0.0), 0.0, 0.90)
            recovery_rate *= 1.0 - 0.35 * self.financial_market.asset_crash_pressure
        else:
            recovery_rate = 0.08 if loan.borrower_kind == "household" else 0.18
        recovery = loan.principal * recovery_rate
        loss = max(0.0, loan.principal - recovery)
        bank.equity -= loss
        bank.reserves += recovery * 0.10
        bank.last_writeoffs += loss
        bank.npl_losses += loss
        loan.status = "defaulted"
        if self.config.truth_market_enabled and loss > EPS:
            self.truth_market.record_money_event(self, loan.borrower_kind, loan.borrower_id, "bank", bank.bid, loss, "loan_default_" + loan.purpose, fuzzy=-0.70, confidence=0.72, weight=0.60)
            self.truth_market.credit_actor(self, "bank", bank.bid, rationalize(-0.03 * math.log1p(loss)), note="default_risk_misestimation")
        if loan.borrower_kind == "household":
            h = self.household_by_id(loan.borrower_id)
            if h:
                if loan.purpose == "mortgage":
                    h.mortgage = max(0.0, h.mortgage - loan.principal)
                    h.home_owner = False
                    h.home_value = 0.0
                    h.rent_payment = self.housing_market.rent_index[h.region] * self.rng.uniform(0.8, 1.2)
                    self.housing_market.vacancies[h.region] += 1.0
                else:
                    h.debt = max(0.0, h.debt - loan.principal)
                h.defaulted = True
                h.cash = max(0.0, h.cash * 0.35)
                self.step_household_defaults += 1
        elif loan.borrower_kind == "firm":
            f = self.firm_by_id(loan.borrower_id)
            if f:
                f.debt = max(0.0, f.debt - loan.principal)
                f.default_count += 1
                # One delinquent loan should not automatically kill a productive firm; banks can restructure.
                lethal_cash_hole = f.cash < -max(70.0, 1.75 * f.capital)
                repeated_default = f.default_count >= 8 and f.last_profit < 0
                if lethal_cash_hole or repeated_default:
                    self._bankrupt_firm(f, reason=f"loan default: {reason}")
        elif loan.borrower_kind == "government":
            self.government.debt = max(0.0, self.government.debt - loan.principal)
            self.events.add(self.t, "Government debt restructuring occurred in the model.")

    def _credit_investment_and_capital_formation(self) -> None:
        for f in self.firms:
            if not f.alive():
                continue
            # Emergency working capital if liquidity is negative but business is viable.
            if f.cash < 0 and f.last_revenue > 0:
                need = min(abs(f.cash) + 1.0, max(1.0, f.last_revenue * 0.25))
                self.request_firm_loan(f, need, purpose="working_capital", collateral=f.capital * 0.35)
            # Investment decision.
            capacity_pressure = safe_div(f.expected_demand, max(1.0, f.inventory + f.output), 1.0) - 1.0
            profit_margin = safe_div(f.last_profit, max(1.0, f.last_revenue), 0.0)
            rate_penalty = 2.8 * self.central_bank.policy_rate + self.financial_market.credit_spread
            invest_propensity = 0.05 + 0.12 * max(0.0, capacity_pressure) + 0.18 * max(0.0, profit_margin) + 0.05 * f.innovation - rate_penalty
            if f.sector == "Energy" and self.government.green_subsidy > 0:
                invest_propensity += self.government.green_subsidy
            if f.sector == "DigitalPlatform":
                invest_propensity += 0.04 * self.platform_market.user_share
            invest_propensity = clamp(invest_propensity, 0.0, 0.28)
            desired_investment = f.capital * invest_propensity * self.rng.uniform(0.6, 1.3)
            if desired_investment <= 0.02:
                f.planned_investment_budget = 0.0
                continue
            internal = min(max(0.0, f.cash * 0.35), desired_investment)
            external = max(0.0, desired_investment - internal)
            purpose = "green_investment" if (f.sector == "Energy" or f.emissions_intensity < 0.08) else "investment"
            approved = True
            if external > 0.05:
                approved = self.request_firm_loan(f, external, purpose=purpose, collateral=f.capital * 0.60)
            if approved:
                f.planned_investment_budget = desired_investment
                # Capital formation is only partly immediate; the rest is represented by investment demand in goods market.
                f.capital += 0.55 * desired_investment * (1.0 + 0.20 * self.government.infrastructure_quality)
                if f.sector == "Energy" or purpose == "green_investment":
                    f.emissions_intensity *= 0.997
                    f.innovation = clamp(f.innovation + 0.002, 0.0, 1.0)
                if f.sector in {"DigitalPlatform", "Manufacturing", "ProfessionalServices"}:
                    f.automation = clamp(f.automation + 0.0015 * desired_investment / max(1.0, f.capital), 0.0, 1.0)
            else:
                f.planned_investment_budget = internal * 0.40

    def _housing_and_mortgages(self) -> None:
        construction_by_region: Dict[str, float] = defaultdict(float)
        for f in self.firms:
            if f.alive() and f.sector == "Construction":
                construction_by_region[f.region] += f.output
        self.housing_market.update(self, construction_by_region)

    # ------------------------------------------------------------------
    # Health, education, insurance, platform, banking, financial
    # ------------------------------------------------------------------

    def _health_education_demography(self) -> None:
        unemployment = self.metrics_last.get("unemployment", 0.06)
        for h in self.households:
            # Aging every 12 steps.
            if self.t > 0 and self.t % 12 == 0:
                h.age += 1
            # Health evolves: public health and income help; unemployment and poverty hurt.
            poverty_stress = 1.0 if h.cash < 0.3 * h.liquidity_need() else 0.0
            health_change = 0.002 * (self.government.public_health_quality - 1.0) + 0.001 * h.insured_health - 0.003 * poverty_stress
            if h.age > 60:
                health_change -= 0.0015
            if self.rng.random() < 0.002 + 0.004 * poverty_stress:
                health_change -= self.rng.uniform(0.02, 0.08)
            h.health = clamp(h.health + health_change, 0.05, 1.0)
            if h.health < 0.14 and h.employed:
                self._separate(h)
            # Education/human capital improves for children, students, and unemployed retraining.
            retraining_prob = 0.004 + 0.010 * unemployment + 0.008 * (self.government.public_education_quality - 1.0)
            if h.age < 28 or (not h.employed and self.rng.random() < retraining_prob):
                gain = 0.0025 * self.government.public_education_quality * (1.0 - h.education)
                h.education = clamp(h.education + gain, 0.0, 1.0)
                h.skill = clamp(h.skill * (1.0 + 0.0015 * self.government.public_education_quality), 0.1, 4.0)
            # Migration: unemployed people in weak regions move sometimes.
            if not h.employed and h.labor_force_member() and h.unemployment_duration > 8 and self.rng.random() < 0.004 * self.config.labor_mobility:
                best_region = min(REGIONS, key=lambda r: self.housing_market.affordability.get(r, 0.4) - 0.04 * REGION_PRODUCTIVITY[r])
                if best_region != h.region:
                    h.region = best_region
                    h.rent_payment = self.housing_market.rent_index[h.region] * self.rng.uniform(0.8, 1.2)

    def _insurance_market(self) -> None:
        self.insurance_market.update(self)

    def _platform_market(self) -> None:
        self.platform_market.update(self)
        # Households adopt or leave platform based on user share and data advantage.
        for h in self.households:
            p_join = 0.010 * self.platform_market.user_share * (1.0 + 0.4 * h.education)
            p_leave = 0.006 * (1.0 - self.platform_market.user_share) + 0.004 * self.platform_market.take_rate
            if not h.platform_user and self.rng.random() < p_join:
                h.platform_user = True
            elif h.platform_user and self.rng.random() < p_leave:
                h.platform_user = False

    def _truth_currency_market(self) -> None:
        if self.config.truth_market_enabled:
            self.truth_market.update(self)
        if self.config.angle_market_enabled:
            self.angle_market.update(self)

    def _banking_system(self) -> None:
        # Recompute deposits from household/firms cash roughly; banks pay operating costs and may fail.
        deposits_by_bank = defaultdict(float)
        for h in self.households:
            deposits_by_bank[h.bank_id] += max(0.0, h.cash)
        for f in self.firms:
            if f.alive():
                deposits_by_bank[f.bank_id] += max(0.0, f.cash) * 0.55
        for b in self.banks:
            if b.failed:
                continue
            b.deposits = 0.65 * b.deposits + 0.35 * deposits_by_bank[b.bid]
            operating_cost = b.operating_cost_rate * max(1.0, b.deposits) / 12.0
            b.equity -= operating_cost + b.last_deposit_cost
            # Central bank liquidity support if needed.
            if b.liquidity_ratio() < 0.03 and b.capital_ratio() > self.config.bank_capital_requirement * 0.5:
                support = max(0.0, 0.05 * b.deposits - b.reserves)
                b.reserves += support
                b.liquidity_support += support
                b.equity -= support * self.central_bank.liquidity_facility_rate / 12.0
            if b.capital_ratio() < self.config.bank_capital_requirement * 0.35 or b.equity < -10.0:
                self._fail_or_bailout_bank(b)
            else:
                # Profit retention slowly rebuilds capital.
                b.equity += max(0.0, b.last_interest_income - operating_cost) * 0.25
                b.risk_appetite = clamp(b.risk_appetite + 0.004 * (b.capital_ratio() - self.config.bank_capital_requirement), 0.04, 1.25)

    def _fail_or_bailout_bank(self, bank: Bank) -> None:
        if bank.failed:
            return
        systemic = safe_div(bank.deposits, max(1.0, sum(b.deposits for b in self.banks)), 0.0) > 0.12
        if systemic:
            bailout = max(0.0, self.config.bank_capital_requirement * bank.risk_weighted_assets() - bank.equity) + 5.0
            bank.equity += bailout
            bank.reserves += bailout * 0.40
            bank.risk_appetite *= 0.55
            self.government.spend(bailout)
            self.government.last_bailouts += bailout
            if self.config.truth_market_enabled:
                bailout_truth = 0.20 if systemic else -0.40
                self.truth_market.record_money_event(self, "government", 0, "bank", bank.bid, bailout, "bank_bailout", fuzzy=bailout_truth - 0.20 * self.financial_market.financial_stress, confidence=0.60, weight=0.35)
            self.events.add(self.t, f"Bank {bank.bid} bailed out with {fmt_money(bailout)}.")
        else:
            bank.failed = True
            self.step_bank_failures += 1
            self.events.add(self.t, f"Bank {bank.bid} failed; loans transferred at a discount.")
            survivors = [b for b in self.banks if not b.failed and b.bid != bank.bid]
            if survivors:
                acquirer = max(survivors, key=lambda b: b.capital_ratio())
                for loan in bank.loan_book.values():
                    if loan.status == "performing":
                        loan.bank_id = acquirer.bid
                        acquirer.loan_book[loan.loan_id] = loan
                acquirer.equity -= max(0.0, -bank.equity) * 0.25
            for h in self.households:
                if h.bank_id == bank.bid and survivors:
                    h.bank_id = survivors[0].bid
            for f in self.firms:
                if f.bank_id == bank.bid and survivors:
                    f.bank_id = survivors[0].bid

    def _financial_market(self) -> None:
        self.financial_market.update(self.rng, self)
        for h in self.households:
            if h.asset_portfolio > 0:
                h.asset_portfolio = max(0.0, h.asset_portfolio * (1.0 + self.financial_market.last_return * (0.6 + 0.4 * h.risk_aversion)))
                # Wealthy households rebalance into financial assets.
                if h.cash > 2.5 * h.liquidity_need() and self.rng.random() < 0.08 * (1.0 - h.risk_aversion):
                    invest = h.cash * 0.04
                    h.cash -= invest
                    h.asset_portfolio += invest

    def _foreign_sector_finalize(self) -> None:
        # Open-economy feedback: persistent trade deficits weaken currency.
        if self.config.open_economy:
            self.foreign_sector.capital_flow_pressure = clamp(0.00004 * self.foreign_sector.trade_balance, -0.02, 0.02)
        else:
            self.foreign_sector.last_imports = 0.0
            self.foreign_sector.last_exports = 0.0
            self.foreign_sector.trade_balance = 0.0

    def _government_finalize(self) -> None:
        gdp = self._nominal_gdp_proxy()
        self.government.finalize_budget(self.central_bank.policy_rate, gdp)
        # If deficit is large, government may borrow from banks.
        if self.government.cash < 0:
            deficit = abs(self.government.cash)
            bank = max((b for b in self.banks if not b.failed), key=lambda b: b.capital_ratio(), default=None)
            if bank:
                self._book_loan(bank, "government", 0, deficit, self.financial_market.bond_yield, 120, 0.0, "government_bond")
        # Carbon revenue recycling: small equal rebate to households.
        if self.government.carbon_revenue > 0:
            rebate_pool = self.government.carbon_revenue * 0.35
            per_h = rebate_pool / max(1, len(self.households))
            for h in self.households:
                h.cash += per_h
                if self.config.truth_market_enabled and per_h > EPS:
                    self.truth_market.record_money_event(self, "government", 0, "household", h.hid, per_h, "carbon_rebate", fuzzy=0.65 + 0.25 * self.energy_market.renewable_share, confidence=0.58, weight=0.18)
            self.government.spend(rebate_pool)

    def _bankruptcy_resolution(self) -> None:
        for f in self.firms:
            if not f.alive():
                continue
            # Negative cash for multiple periods or extreme leverage kills firms.
            severe_cash_stress = f.cash < -max(120.0, 3.00 * f.capital)
            severe_leverage_stress = f.leverage() > 8.0 and f.last_profit < -0.60 * max(1.0, f.last_revenue)
            if severe_cash_stress or severe_leverage_stress:
                if self.request_firm_loan(f, min(abs(f.cash) + 8.0, max(12.0, f.last_revenue * 0.65)), "working_capital", f.capital * 0.45):
                    continue
                self._bankrupt_firm(f, reason="cash/leverage stress")
            else:
                # Gradual aging and productivity evolution.
                f.age += 1
                if f.last_profit > 0:
                    f.productivity *= 1.0 + 0.0006 * f.innovation
                else:
                    f.productivity *= 0.9995
                f.capital = max(0.05, f.capital * 0.996)
                f.supply_chain_fragility *= 0.992

        # Entry: replace some bankrupt firms and add entrepreneurial entry in profitable sectors.
        bankrupt_count = sum(1 for f in self.firms if f.bankrupt)
        entries = 0
        if bankrupt_count > 0:
            entries += min(bankrupt_count, max(1, int(0.02 * self.config.firms)))
        profitable_sectors = sorted(SECTORS, key=lambda s: self.sector_revenue.get(s, 0.0) - self.sector_unfilled.get(s, 0.0), reverse=True)[:4]
        if self.rng.random() < 0.15:
            entries += 1
        # Keep the model computationally bounded. IDs are list positions, so old bankrupt
        # firms remain as historical records; new entry is capped relative to the starting economy.
        max_total_firms = max(self.config.firms, int(self.config.firms * 1.50))
        entries = max(0, min(entries, max_total_firms - len(self.firms)))
        for _ in range(entries):
            self._spawn_firm(sector=self.rng.choice(profitable_sectors))

    def _bankrupt_firm(self, firm: Firm, reason: str) -> None:
        if firm.bankrupt:
            return
        firm.bankrupt = True
        self.step_firm_bankruptcies += 1
        self._separate_all(firm)
        # Fire-sale impact on bank collateral.
        for b in self.banks:
            for ln in b.loan_book.values():
                if ln.borrower_kind == "firm" and ln.borrower_id == firm.fid and ln.status == "performing":
                    self._default_loan(b, ln, reason=reason)
        if self.config.truth_market_enabled:
            self.truth_market.record_money_event(self, "firm", firm.fid, "market", 0, max(0.0, firm.debt + abs(firm.cash)), "firm_bankruptcy_resolution", fuzzy=-0.65, confidence=0.70, weight=0.40)
        self.events.add(self.t, f"Firm {firm.fid} ({firm.sector}/{firm.region}) bankrupt: {reason}.")

    def _spawn_firm(self, sector: Optional[str] = None) -> None:
        fid = len(self.firms)
        sector = sector or self.rng.choice(SECTORS)
        region = weighted_choice(self.rng, REGIONS, [REGION_POP_WEIGHTS[r] for r in REGIONS])
        bank = self.rng.choice([b for b in self.banks if not b.failed] or self.banks)
        f = Firm(
            fid=fid,
            sector=sector,
            region=region,
            productivity=clamp(self.rng.lognormvariate(0.08, 0.20) * REGION_PRODUCTIVITY[region], 0.25, 3.0),
            capital=self.rng.lognormvariate(2.2 if sector not in CAPITAL_HEAVY_SECTORS else 2.8, 0.45),
            cash=self.rng.lognormvariate(1.6, 0.6),
            debt=0.0,
            bank_id=bank.bid,
            wage_offer=(2.5 + 1.0 * (sector in HIGH_SKILL_SECTORS)) * self.rng.uniform(0.85, 1.20),
            price=INITIAL_PRICE[sector] * self.rng.uniform(0.90, 1.15),
            markup=self.rng.uniform(0.06, 0.18),
            quality=clamp(self.rng.lognormvariate(0.0, 0.15), 0.6, 1.5),
            innovation=clamp(self.rng.betavariate(2.0, 4.0), 0.0, 1.0),
            automation=clamp(self.rng.betavariate(1.8, 4.2), 0.0, 1.0),
            market_power=clamp(self.rng.betavariate(1.5, 5.0), 0.01, 0.70),
            energy_intensity=ENERGY_INTENSITY[sector] * self.rng.uniform(0.80, 1.30),
            emissions_intensity=EMISSIONS_INTENSITY[sector] * self.rng.uniform(0.80, 1.30),
            exporter_share=self.rng.uniform(0.05, 0.35) if sector in TRADABLE_SECTORS else 0.0,
            platform_dependency=self.rng.uniform(0.05, 0.55),
            expected_demand=self.rng.uniform(4.0, 18.0),
            desired_labor=max(1, int(self.rng.uniform(1.0, 6.0))),
        )
        self.firms.append(f)
        if self.config.truth_market_enabled:
            clean = 1.0 - clamp(f.emissions_intensity + 0.25 * f.energy_intensity, 0.0, 1.6) / 1.6
            f.truth_balance = rationalize(1.0 * clean + 0.8 * f.quality + 0.9 * f.innovation)
            f.knowledge_assets = rationalize(0.4 * f.innovation + 0.3 * f.quality)
            f.model_reputation = clamp(0.30 + 0.25 * f.innovation + 0.15 * clean, 0.0, 1.0)
        self._initialize_supplier_network_for_firm(f)
        seed_loan = f.capital * self.rng.uniform(0.10, 0.35)
        if seed_loan > 0:
            self.request_firm_loan(f, seed_loan, "investment", f.capital * 0.65)

    def _initialize_supplier_network_for_firm(self, firm: Firm) -> None:
        by_sector = defaultdict(list)
        for f in self.firms:
            if f.alive() and f.fid != firm.fid:
                by_sector[f.sector].append(f.fid)
        suppliers = []
        for input_sector, share in INPUT_OUTPUT.get(firm.sector, {}).items():
            pool = by_sector.get(input_sector, [])
            if not pool:
                continue
            k = 1 if share < 0.06 else 2
            for _ in range(k):
                suppliers.append(self.rng.choice(pool))
        firm.supplier_ids = sorted(set(suppliers))[:6]

    # ------------------------------------------------------------------
    # Metrics and indices
    # ------------------------------------------------------------------

    def _sector_prices_from_firms(self) -> Dict[str, float]:
        prices = {}
        for sector in SECTORS:
            firms = [f for f in self.firms if f.alive() and f.sector == sector]
            if firms:
                prices[sector] = weighted_average(((f.price, max(0.1, f.last_quantity_sold + f.inventory * 0.05)) for f in firms), INITIAL_PRICE[sector])
            else:
                prices[sector] = self.sector_price_index.get(sector, INITIAL_PRICE[sector]) * (1.0 + (0.02 if sector in TRADABLE_SECTORS else 0.05))
        return prices

    def _compute_sector_hhi(self) -> Dict[str, float]:
        hhis = {}
        for sector in SECTORS:
            revenues = [max(0.0, f.last_revenue) + 0.1 * max(0.0, f.inventory) for f in self.firms if f.alive() and f.sector == sector]
            hhis[sector] = hhi(revenues)
        self.sector_hhi = hhis
        return hhis

    def _cpi(self) -> float:
        total = sum(BASE_CONSUMPTION_PREFS.values())
        if total <= EPS:
            return 1.0
        cpi = 0.0
        for sector, w in BASE_CONSUMPTION_PREFS.items():
            cpi += (w / total) * self.sector_price_index.get(sector, INITIAL_PRICE.get(sector, 1.0))
        return cpi

    def _nominal_gdp_proxy(self) -> float:
        # Production-side proxy with trade correction.
        value_added = 0.0
        for f in self.firms:
            if f.alive():
                intermediate = f.last_input_bill + f.last_energy_bill
                value_added += max(0.0, f.last_revenue - 0.55 * intermediate)
        return max(0.1, value_added + self.step_exports - self.step_imports * 0.20)

    def _collect_metrics(self) -> None:
        cpi = self._cpi()
        inflation = safe_div(cpi - self.metrics_last.get("cpi", cpi), self.metrics_last.get("cpi", cpi), 0.0)
        labor_force = [h for h in self.households if h.labor_force_member()]
        unemployed = [h for h in labor_force if not h.employed]
        unemployment = safe_div(len(unemployed), len(labor_force), 0.0)
        gdp = self._nominal_gdp_proxy()
        wages = [h.wage for h in self.households if h.employed]
        incomes = [h.last_income for h in self.households]
        wealths = [h.wealth() for h in self.households]
        profits = [f.last_profit for f in self.firms if f.alive()]
        bank_capital = [b.capital_ratio() for b in self.banks if not b.failed]
        total_loans = sum(b.total_loans() for b in self.banks if not b.failed)
        npl = sum(ln.principal for b in self.banks for ln in b.loan_book.values() if ln.status == "defaulted")
        npl_ratio = safe_div(npl, total_loans + npl, 0.0)
        avg_housing_price = mean(self.housing_market.price_index.values(), 1.0)
        avg_rent = mean(self.housing_market.rent_index.values(), 1.0)
        affordability = mean(self.housing_market.affordability.values(), 0.0)
        emissions = self.energy_market.emissions
        total_output = sum(self.sector_output.values())
        poverty_line = percentile(incomes, 0.25, 1.0) * 0.55
        poverty = safe_div(sum(1 for x in incomes if x < poverty_line), len(incomes), 0.0)
        avg_hhi = mean(self.sector_hhi.values(), 0.0)
        bank_fail_count = sum(1 for b in self.banks if b.failed)
        firm_alive_count = sum(1 for f in self.firms if f.alive())
        credit_growth = safe_div(self.step_new_credit, max(1.0, total_loans), 0.0)
        productivity = safe_div(total_output, max(1.0, len([h for h in self.households if h.employed])), 0.0)
        welfare = self._welfare_index(incomes, wealths, unemployment, emissions, inflation)
        metrics = {
            "t": float(self.t),
            "gdp": gdp,
            "real_output": total_output,
            "cpi": cpi,
            "inflation": inflation,
            "unemployment": unemployment,
            "avg_wage": mean(wages, 0.0),
            "median_income": median(incomes, 0.0),
            "income_gini": gini(incomes),
            "wealth_gini": gini(wealths),
            "poverty_rate": poverty,
            "avg_profit": mean(profits, 0.0),
            "firm_bankruptcies": float(self.step_firm_bankruptcies),
            "firm_alive": float(firm_alive_count),
            "household_defaults": float(self.step_household_defaults),
            "bank_failures_step": float(self.step_bank_failures),
            "banks_failed_total": float(bank_fail_count),
            "bank_capital_ratio": mean(bank_capital, 0.0),
            "npl_ratio": npl_ratio,
            "total_credit": total_loans,
            "new_credit": self.step_new_credit,
            "credit_growth": credit_growth,
            "policy_rate": self.central_bank.policy_rate,
            "financial_stress": self.financial_market.financial_stress,
            "stock_index": self.financial_market.stock_index,
            "credit_spread": self.financial_market.credit_spread,
            "housing_price": avg_housing_price,
            "rent_index": avg_rent,
            "housing_affordability": affordability,
            "housing_transactions": float(self.housing_market.last_transactions),
            "new_housing_units": self.housing_market.last_new_units,
            "energy_price": self.energy_market.energy_price,
            "energy_shortage": self.energy_market.shortage_ratio,
            "renewable_share": self.energy_market.renewable_share,
            "emissions": emissions,
            "carbon_price": self.government.carbon_price,
            "imports": self.step_imports,
            "exports": self.step_exports,
            "trade_balance": self.foreign_sector.trade_balance,
            "exchange_rate": self.foreign_sector.exchange_rate,
            "gov_revenue": self.government.last_revenue,
            "gov_spending": self.government.last_spending,
            "gov_deficit": self.government.last_deficit,
            "gov_debt": self.government.debt,
            "gov_debt_to_annual_gdp": safe_div(self.government.debt, max(1.0, gdp * 12.0), 0.0),
            "platform_user_share": self.platform_market.user_share,
            "platform_take_rate": self.platform_market.take_rate,
            "platform_concentration": self.platform_market.concentration,
            "market_concentration_hhi": avg_hhi,
            "insurance_solvency": self.insurance_market.solvency,
            "productivity": productivity,
            "welfare_index": welfare,
        }
        if self.config.truth_market_enabled:
            truth_metrics = self.truth_market.metrics(self)
            metrics.update(truth_metrics)
            for resource in RESOURCE_TYPES:
                metrics[f"truth_resource_use_{resource}"] = self.truth_market.resource_use.get(resource, 0.0)
                metrics[f"truth_resource_truth_{resource}"] = self.truth_market.resource_truth.get(resource, 1.0)
                metrics[f"truth_resource_limit_{resource}"] = self.truth_market.resource_quota.get(resource, 0.0)
            metrics["truth_adjusted_welfare"] = (
                welfare
                + 0.45 * metrics.get("truth_correctness_index", 0.0)
                - 0.35 * metrics.get("truth_planetary_stress", 0.0)
                + 0.10 * metrics.get("truth_model_competition", 0.0)
            )
        else:
            metrics["truth_adjusted_welfare"] = welfare
        if self.config.angle_market_enabled:
            angle_metrics = self.angle_market.metrics(self)
            metrics.update(angle_metrics)
            metrics["truth_angle_adjusted_welfare"] = (
                metrics.get("truth_adjusted_welfare", welfare)
                + 0.35 * metrics.get("angle_market_alignment", 0.0)
                + 0.15 * metrics.get("angle_mean_actor_goodness", 0.0)
                - 0.25 * metrics.get("angle_polarization_index", 0.0)
            )
        else:
            metrics["truth_angle_adjusted_welfare"] = metrics.get("truth_adjusted_welfare", welfare)
        for sector in SECTORS:
            key = sector.lower().replace(" ", "_")
            metrics[f"price_{key}"] = self.sector_price_index.get(sector, 0.0)
            metrics[f"output_{key}"] = self.sector_output.get(sector, 0.0)
            metrics[f"hhi_{key}"] = self.sector_hhi.get(sector, 0.0)
        self.metrics.append(metrics)
        self.metrics_last = metrics
        self.central_bank.update(inflation, unemployment, self.financial_market.financial_stress, self.config)

    def _welfare_index(self, incomes: List[float], wealths: List[float], unemployment: float, emissions: float, inflation: float) -> float:
        avg_income = mean(incomes, 0.0)
        med_income = median(incomes, 0.0)
        inequality_penalty = 0.6 * gini(incomes) + 0.25 * gini(wealths)
        macro_penalty = 0.90 * unemployment + 0.70 * abs(inflation) + 0.00005 * emissions
        return max(0.0, math.log1p(max(0.0, avg_income + med_income)) * (1.0 - clamp(inequality_penalty, 0.0, 0.85)) - macro_penalty)

    def final_summary(self) -> Dict[str, Any]:
        if not self.metrics:
            return {}
        last = self.metrics[-1]
        first = self.metrics[0]
        avg = lambda k: mean((m.get(k, 0.0) for m in self.metrics), 0.0)
        summary = {
            "scenario": self.config.scenario,
            "compound_shocks": self.config.shock_compound,
            "seed": self.config.seed,
            "steps": self.config.steps,
            "population": self.config.households,
            "firms_initial": self.config.firms,
            "firms_final_alive": int(last.get("firm_alive", 0)),
            "banks_failed_total": int(last.get("banks_failed_total", 0)),
            "final_gdp": last.get("gdp", 0.0),
            "gdp_change": safe_div(last.get("gdp", 0.0) - first.get("gdp", 0.0), max(1.0, first.get("gdp", 1.0)), 0.0),
            "avg_inflation": avg("inflation"),
            "final_inflation": last.get("inflation", 0.0),
            "avg_unemployment": avg("unemployment"),
            "final_unemployment": last.get("unemployment", 0.0),
            "final_income_gini": last.get("income_gini", 0.0),
            "final_wealth_gini": last.get("wealth_gini", 0.0),
            "final_financial_stress": last.get("financial_stress", 0.0),
            "final_bank_capital_ratio": last.get("bank_capital_ratio", 0.0),
            "final_npl_ratio": last.get("npl_ratio", 0.0),
            "final_housing_affordability": last.get("housing_affordability", 0.0),
            "final_energy_price": last.get("energy_price", 0.0),
            "final_emissions": last.get("emissions", 0.0),
            "final_renewable_share": last.get("renewable_share", 0.0),
            "final_gov_debt_to_annual_gdp": last.get("gov_debt_to_annual_gdp", 0.0),
            "final_platform_concentration": last.get("platform_concentration", 0.0),
            "final_welfare_index": last.get("welfare_index", 0.0),
            "final_truth_adjusted_welfare": last.get("truth_adjusted_welfare", 0.0),
            "final_truth_angle_adjusted_welfare": last.get("truth_angle_adjusted_welfare", 0.0),
            "truth_currency_name": self.config.truth_currency_name,
            "angle_currency_name": self.config.angle_currency_name,
            "final_truth_price": last.get("truth_price", 0.0),
            "final_truth_correctness_index": last.get("truth_correctness_index", 0.0),
            "final_truth_planetary_stress": last.get("truth_planetary_stress", 0.0),
            "final_truth_cross_resource_throttle": last.get("truth_cross_resource_throttle", 0.0),
            "avg_truth_trade_volume": avg("truth_trade_volume"),
            "avg_truth_fiat_volume": avg("truth_fiat_volume"),
            "final_truth_predicates_total": last.get("truth_total_predicates", 0.0),
            "final_truth_predicates_created_step": last.get("truth_predicates_created", 0.0),
            "final_truth_verifications_total": last.get("truth_total_verifications", 0.0),
            "final_truth_household_mean": last.get("truth_household_mean", 0.0),
            "final_truth_firm_mean": last.get("truth_firm_mean", 0.0),
            "final_truth_bank_mean": last.get("truth_bank_mean", 0.0),
            "final_truth_government_balance": last.get("truth_government_balance", 0.0),
            "final_truth_model_competition": last.get("truth_model_competition", 0.0),
            "final_truth_audit_pressure": last.get("truth_audit_pressure", 0.0),
            "final_angle_price": last.get("angle_price", 0.0),
            "final_angle_market_alignment": last.get("angle_market_alignment", 0.0),
            "final_angle_popularity_index": last.get("angle_popularity_index", 0.0),
            "final_angle_polarization_index": last.get("angle_polarization_index", 0.0),
            "avg_angle_trade_volume": avg("angle_trade_volume"),
            "avg_angle_fiat_volume": avg("angle_fiat_volume"),
            "final_angle_total_events": last.get("angle_total_events", 0.0),
            "final_angle_household_mean": last.get("angle_household_mean", 0.0),
            "final_angle_firm_mean": last.get("angle_firm_mean", 0.0),
            "final_angle_bank_mean": last.get("angle_bank_mean", 0.0),
            "final_angle_government_balance": last.get("angle_government_balance", 0.0),
            "final_angle_mean_actor_goodness": last.get("angle_mean_actor_goodness", 0.0),
            "final_angle_moral_arbitrage_volume": last.get("angle_moral_arbitrage_volume", 0.0),
            "final_angle_model_competition": last.get("angle_model_competition", 0.0),
            "events_recent": self.events.recent(20),
        }
        return summary


# ---------------------------------------------------------------------------
# Output helpers and CLI
# ---------------------------------------------------------------------------


def write_csv(path: str, rows: List[Dict[str, float]]) -> None:
    if not rows:
        return
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    fieldnames = list(rows[0].keys())
    # Keep later extra fields if any.
    all_fields = []
    seen = set()
    for row in rows:
        for k in row.keys():
            if k not in seen:
                all_fields.append(k)
                seen.add(k)
    fieldnames = all_fields
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_json(path: str, obj: Dict[str, Any]) -> None:
    os.makedirs(os.path.dirname(os.path.abspath(path)) or ".", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(obj, f, indent=2, sort_keys=True)


def print_summary(summary: Dict[str, Any]) -> None:
    keys = [
        "scenario",
        "compound_shocks",
        "seed",
        "steps",
        "final_gdp",
        "gdp_change",
        "avg_inflation",
        "final_inflation",
        "avg_unemployment",
        "final_unemployment",
        "final_income_gini",
        "final_wealth_gini",
        "final_financial_stress",
        "final_bank_capital_ratio",
        "final_npl_ratio",
        "final_housing_affordability",
        "final_energy_price",
        "final_emissions",
        "final_renewable_share",
        "final_gov_debt_to_annual_gdp",
        "final_platform_concentration",
        "final_welfare_index",
        "final_truth_adjusted_welfare",
        "final_truth_angle_adjusted_welfare",
        "truth_currency_name",
        "angle_currency_name",
        "final_truth_price",
        "final_truth_correctness_index",
        "final_truth_planetary_stress",
        "final_truth_cross_resource_throttle",
        "avg_truth_trade_volume",
        "final_truth_predicates_total",
        "final_truth_verifications_total",
        "final_truth_household_mean",
        "final_truth_firm_mean",
        "final_truth_model_competition",
        "final_angle_price",
        "final_angle_market_alignment",
        "final_angle_popularity_index",
        "final_angle_polarization_index",
        "avg_angle_trade_volume",
        "final_angle_total_events",
        "final_angle_household_mean",
        "final_angle_firm_mean",
        "final_angle_mean_actor_goodness",
    ]
    print("\n=== Mega Economy Simulation Summary ===")
    for k in keys:
        if k in summary:
            v = summary[k]
            if isinstance(v, float):
                print(f"{k:34s}: {v:.6f}")
            else:
                print(f"{k:34s}: {v}")
    events = summary.get("events_recent") or []
    if events:
        print("\nRecent events:")
        for e in events:
            print("  -", e)


def run_single(config: SimulationConfig, out_csv: str = "", out_json: str = "") -> Dict[str, Any]:
    world = EconomicWorld(config)
    metrics = world.run()
    summary = world.final_summary()
    if out_csv:
        write_csv(out_csv, metrics)
    if out_json:
        write_json(out_json, summary)
    return {"summary": summary, "metrics": metrics}


def run_compare(base_config: SimulationConfig, scenarios: List[str], out_csv: str = "", out_json: str = "") -> Dict[str, Any]:
    comparison_rows: List[Dict[str, float]] = []
    summaries: Dict[str, Any] = {}
    for i, scenario in enumerate(scenarios):
        cfg = SimulationConfig(**vars(base_config))
        cfg.scenario = scenario
        cfg.seed = base_config.seed + i * 1009
        world = EconomicWorld(cfg)
        world.run()
        summary = world.final_summary()
        summaries[scenario] = summary
        row = {"scenario": scenario}
        for k, v in summary.items():
            if isinstance(v, (int, float)):
                row[k] = v
        comparison_rows.append(row)  # type: ignore[arg-type]
    if out_csv:
        # DictWriter can handle str scenario and numeric fields.
        os.makedirs(os.path.dirname(os.path.abspath(out_csv)) or ".", exist_ok=True)
        fields = []
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
    p = argparse.ArgumentParser(description="Large PyPy3-compatible agent-based economic simulator.")
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
    # Policy/calibration knobs.
    p.add_argument("--income-tax", type=float, default=0.20)
    p.add_argument("--corporate-tax", type=float, default=0.20)
    p.add_argument("--vat", type=float, default=0.12)
    p.add_argument("--carbon-price", type=float, default=0.03)
    p.add_argument("--bank-capital-requirement", type=float, default=0.085)
    p.add_argument("--labor-mobility", type=float, default=0.16)
    p.add_argument("--open-economy", action="store_true", default=True)
    p.add_argument("--closed-economy", action="store_true", help="Disable imports/exports feedbacks")
    # Truth-currency knobs.
    p.add_argument("--truth-currency-name", type=str, default="LOGOS")
    p.add_argument("--disable-truth-market", action="store_true", help="Disable fuzzy truth currency and resource correctness market")
    p.add_argument("--truth-money-scale", type=float, default=80.0, help="Higher means fiat flows mint fewer truth units")
    p.add_argument("--truth-resource-strictness", type=float, default=1.0, help="Higher means tighter planetary quotas")
    p.add_argument("--truth-verification-depth", type=int, default=3, help="Maximum recursive verification arity added per predicate")
    p.add_argument("--truth-public-audit-rate", type=float, default=0.055)
    p.add_argument("--truth-trade-intensity", type=float, default=0.18)
    p.add_argument("--truth-cross-resource-penalty", type=float, default=0.78)
    p.add_argument("--truth-to-fiat-fx", type=float, default=1.0)
    # Angular moral-currency knobs.
    p.add_argument("--angle-currency-name", type=str, default="ARETE")
    p.add_argument("--disable-angle-market", action="store_true", help="Disable angular moral currency market")
    p.add_argument("--angle-money-scale", type=float, default=42.0, help="Higher means fiat/LOGOS flows mint fewer angle units")
    p.add_argument("--angle-trade-intensity", type=float, default=0.14)
    p.add_argument("--angle-to-fiat-fx", type=float, default=1.0)
    p.add_argument("--angle-state-a-good", type=float, default=ANGLE_STATE_A_GOOD_DEG)
    p.add_argument("--angle-state-b-good", type=float, default=ANGLE_STATE_B_GOOD_DEG)
    p.add_argument("--angle-objective-good", type=float, default=ANGLE_OBJECTIVE_GOOD_DEG)
    p.add_argument("--angle-popularity-weight", type=float, default=0.22)
    p.add_argument("--angle-truth-weight", type=float, default=0.42)
    p.add_argument("--angle-resource-weight", type=float, default=0.35)
    p.add_argument("--angle-moral-credit-bonus", type=float, default=0.020)
    return p


def config_from_args(args: argparse.Namespace) -> SimulationConfig:
    return SimulationConfig(
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
        truth_market_enabled=not args.disable_truth_market,
        truth_money_scale=args.truth_money_scale,
        truth_resource_strictness=args.truth_resource_strictness,
        truth_verification_depth=args.truth_verification_depth,
        truth_public_audit_rate=args.truth_public_audit_rate,
        truth_trade_intensity=args.truth_trade_intensity,
        truth_cross_resource_penalty=args.truth_cross_resource_penalty,
        truth_to_fiat_fx=args.truth_to_fiat_fx,
        angle_currency_name=args.angle_currency_name,
        angle_market_enabled=not args.disable_angle_market,
        angle_money_scale=args.angle_money_scale,
        angle_trade_intensity=args.angle_trade_intensity,
        angle_to_fiat_fx=args.angle_to_fiat_fx,
        angle_state_a_good=args.angle_state_a_good,
        angle_state_b_good=args.angle_state_b_good,
        angle_objective_good=args.angle_objective_good,
        angle_popularity_weight=args.angle_popularity_weight,
        angle_truth_weight=args.angle_truth_weight,
        angle_resource_weight=args.angle_resource_weight,
        angle_moral_credit_bonus=args.angle_moral_credit_bonus,
    )


def main(argv: Optional[List[str]] = None) -> int:
    parser = make_arg_parser()
    args = parser.parse_args(argv)
    cfg = config_from_args(args)
    if args.compare is not None and len(args.compare) > 0:
        result = run_compare(cfg, args.compare, out_csv=args.out, out_json=args.json)
        print("\n=== Scenario comparison ===")
        for row in result["rows"]:
            print(
                f"{row['scenario']:22s} "
                f"GDP={row.get('final_gdp', 0.0):10.3f} "
                f"unemp={row.get('final_unemployment', 0.0):7.3f} "
                f"infl={row.get('final_inflation', 0.0):8.4f} "
                f"stress={row.get('final_financial_stress', 0.0):7.3f} "
                f"welfare={row.get('final_welfare_index', 0.0):7.3f} "
                f"truthW={row.get('final_truth_adjusted_welfare', 0.0):7.3f} "
                f"angleW={row.get('final_truth_angle_adjusted_welfare', 0.0):7.3f} "
                f"truth={row.get('final_truth_correctness_index', 0.0):6.3f} "
                f"angle={row.get('final_angle_market_alignment', 0.0):6.3f}"
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
