#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solar Hierarchy Market Economy Simulation
=========================================

PyPy3-compatible, dependency-free simulation of a hierarchy-currency economy.

Model implemented here:

- The market remains.
- The currency is hierarchy, not plain money.
- A hierarchy bundle is structured by hierarchy level and hierarchy element.
- For settlement it can be compressed into a number by addition and multiplication:

      settlement_value = sum(raw_amount[level, element] * height_multiplier[level])

- People, companies, products, countries, alliances, defense organizations,
  UN-like bodies and markets all have hierarchy positions.
- Markets are also tradable assets. They are not only places where trading occurs.
- Privileges and disadvantages/burdens can be traded as structured hierarchy assets.
- The simulation covers Earth, Moon, Mars and a Solar System level.
- There are 12 hierarchy levels.
- Strong military/economic actors rise automatically; helpers/media/care workers
  receive manual status lifts from UN-like organizations.

Run examples:

    pypy3 solar_hierarchy_market_sim_pypy3.py --profile demo --ticks 2
    pypy3 solar_hierarchy_market_sim_pypy3.py --profile large --ticks 5 --seed 42
    pypy3 solar_hierarchy_market_sim_pypy3.py --profile huge --ticks 2 --json report.json

The implementation deliberately stores relationships mostly as IDs instead of
cyclic object pointers. This keeps large runs practical on PyPy3 and CPython.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict
from typing import Dict, Iterable, List, Optional, Sequence, Tuple, Any


# ---------------------------------------------------------------------------
# Deterministic fast RNG: no dependency on random.Random internals.
# ---------------------------------------------------------------------------

class FastRNG:
    """Small xorshift64* RNG with utility methods.

    It is deterministic, fast, PyPy-friendly, and avoids implementation-specific
    behavior in Python's random module for very large simulations.
    """

    __slots__ = ("state",)

    def __init__(self, seed: int = 1) -> None:
        self.state = (seed ^ 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
        if self.state == 0:
            self.state = 0xA5A5A5A5A5A5A5A5

    def u64(self) -> int:
        x = self.state
        x ^= (x >> 12) & 0xFFFFFFFFFFFFFFFF
        x ^= (x << 25) & 0xFFFFFFFFFFFFFFFF
        x ^= (x >> 27) & 0xFFFFFFFFFFFFFFFF
        self.state = x & 0xFFFFFFFFFFFFFFFF
        return (x * 0x2545F4914F6CDD1D) & 0xFFFFFFFFFFFFFFFF

    def random(self) -> float:
        return (self.u64() >> 11) * (1.0 / (1 << 53))

    def uniform(self, lo: float, hi: float) -> float:
        return lo + (hi - lo) * self.random()

    def randint(self, lo: int, hi: int) -> int:
        if hi <= lo:
            return lo
        return lo + int(self.random() * ((hi - lo) + 1))

    def choice(self, seq: Sequence[Any]) -> Any:
        if not seq:
            raise IndexError("choice from empty sequence")
        return seq[int(self.random() * len(seq))]

    def chance(self, p: float) -> bool:
        return self.random() < p

    def sample(self, seq: Sequence[Any], k: int) -> List[Any]:
        """Fast sample. If k is close to n, use shuffle; otherwise replacement-free picks."""
        n = len(seq)
        if k <= 0 or n == 0:
            return []
        if k >= n:
            result = list(seq)
            self.shuffle(result)
            return result
        # For moderate k this simple set-based sample is fast and deterministic.
        seen = set()
        out = []
        while len(out) < k:
            idx = int(self.random() * n)
            if idx not in seen:
                seen.add(idx)
                out.append(seq[idx])
        return out

    def shuffle(self, seq: List[Any]) -> None:
        for i in range(len(seq) - 1, 0, -1):
            j = int(self.random() * (i + 1))
            seq[i], seq[j] = seq[j], seq[i]

    def triangular_like(self, lo: float, hi: float, mode: float) -> float:
        if hi <= lo:
            return lo
        m = clamp((mode - lo) / (hi - lo), 0.0, 1.0)
        center = (self.random() + self.random()) * 0.5
        x = 0.63 * center + 0.37 * m
        return lo + (hi - lo) * clamp(x, 0.0, 1.0)

    def beta_like(self, alpha: float, beta: float) -> float:
        mean = alpha / max(1e-12, alpha + beta)
        concentration = clamp((alpha + beta) / 12.0, 0.12, 0.92)
        rough = self.triangular_like(0.0, 1.0, mean)
        noise = self.uniform(-0.07, 0.07) * (1.0 - concentration)
        return clamp(mean * concentration + rough * (1.0 - concentration) + noise, 0.0, 1.0)


# ---------------------------------------------------------------------------
# Hierarchy constants
# ---------------------------------------------------------------------------

EPS = 1e-9

LEVEL_NAMES = {
    1: "Survival",
    2: "Basic",
    3: "Local",
    4: "Skilled",
    5: "Professional",
    6: "Regional",
    7: "National",
    8: "Alliance",
    9: "Planetary",
    10: "Interplanetary",
    11: "Systemic",
    12: "Solar Apex",
}

HEIGHT_MULTIPLIERS = {
    1: 1.00,
    2: 1.35,
    3: 1.85,
    4: 2.55,
    5: 3.55,
    6: 5.10,
    7: 7.40,
    8: 10.80,
    9: 15.90,
    10: 23.50,
    11: 35.00,
    12: 52.00,
}

LEVEL_THRESHOLDS = [
    0.0,
    160.0,
    420.0,
    950.0,
    2100.0,
    4800.0,
    11000.0,
    25000.0,
    60000.0,
    145000.0,
    350000.0,
    850000.0,
]

ELEMENTS = (
    "labor", "skill", "care", "media", "science", "risk", "trust",
    "governance", "military", "capital", "logistics", "infrastructure",
    "market_access", "privilege", "burden",
)

DOMAINS = (
    "food", "water", "oxygen", "housing", "energy", "medicine", "education",
    "compute", "transport", "shipbuilding", "agriculture", "manufacturing",
    "defense", "media", "culture", "research", "care", "finance", "data",
    "orbital_slots", "terraforming", "market_rights", "labor", "privilege", "burden",
)

SECTORS = (
    "food", "water", "oxygen", "housing", "energy", "medicine", "education",
    "compute", "transport", "shipbuilding", "agriculture", "manufacturing",
    "defense", "media", "culture", "research", "care", "finance", "data", "terraforming",
)

SEXES = ("female", "male", "other")


def clamp(x: float, lo: float, hi: float) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def level_from_number(value: float) -> int:
    level = 1
    for idx, threshold in enumerate(LEVEL_THRESHOLDS, start=1):
        if value >= threshold:
            level = idx
    return int(clamp(level, 1, 12))


def gaussian(x: float, mu: float, sigma: float, floor: float = 0.28) -> float:
    return floor + (1.0 - floor) * math.exp(-((x - mu) ** 2) / (2.0 * sigma * sigma))


def age_curve(age: int, sex: str) -> float:
    if sex == "female":
        return gaussian(age, 38.0, 15.0)
    if sex == "male":
        return gaussian(age, 48.0, 16.5)
    return gaussian(age, 43.0, 16.0)


# ---------------------------------------------------------------------------
# UTF-8 chart helpers
# ---------------------------------------------------------------------------

SPARK_CHARS = "▁▂▃▄▅▆▇█"
HEAT_CHARS = " ·░▒▓█"
TREE_MID = "├─ "
TREE_LAST = "└─ "
TREE_PIPE = "│  "
TREE_BLANK = "   "


def short_number(value: float) -> str:
    value = float(value)
    sign = "-" if value < 0 else ""
    value = abs(value)
    if value >= 1_000_000_000:
        return "%s%.1fB" % (sign, value / 1_000_000_000.0)
    if value >= 1_000_000:
        return "%s%.1fM" % (sign, value / 1_000_000.0)
    if value >= 1_000:
        return "%s%.1fk" % (sign, value / 1_000.0)
    if value >= 100:
        return "%s%.0f" % (sign, value)
    if value >= 10:
        return "%s%.1f" % (sign, value)
    return "%s%.2f" % (sign, value)


def utf8_bar(value: float, max_value: float, width: int = 28, fill: str = "█", empty: str = "░") -> str:
    if width <= 0:
        return ""
    if max_value <= 0:
        return empty * width
    ratio = clamp(value / max_value, 0.0, 1.0)
    full = int(ratio * width)
    return fill * full + empty * (width - full)


def sparkline(values: Sequence[float]) -> str:
    if not values:
        return ""
    vals = list(values)
    lo = min(vals)
    hi = max(vals)
    if hi - lo <= EPS:
        return SPARK_CHARS[0] * len(vals)
    out = []
    for v in vals:
        idx = int((v - lo) / (hi - lo) * (len(SPARK_CHARS) - 1))
        idx = int(clamp(idx, 0, len(SPARK_CHARS) - 1))
        out.append(SPARK_CHARS[idx])
    return "".join(out)


def pad(text: Any, width: int) -> str:
    s = str(text)
    if len(s) <= width:
        return s + " " * (width - len(s))
    if width <= 1:
        return s[:width]
    return s[: width - 1] + "…"


def age_band(age: int) -> str:
    if age < 18:
        return "00-17"
    if age < 25:
        return "18-24"
    if age < 35:
        return "25-34"
    if age < 45:
        return "35-44"
    if age < 55:
        return "45-54"
    if age < 65:
        return "55-64"
    return "65+"


def chart_title(title: str, width: int = 78, char: str = "═") -> str:
    core = " %s " % title
    if len(core) >= width:
        return core
    left = (width - len(core)) // 2
    right = width - len(core) - left
    return char * left + core + char * right


def render_histogram(mapping: Dict[Any, float], title: str, width: int = 26, sort_numeric: bool = False, value_fmt: Optional[Any] = None) -> str:
    if not mapping:
        return chart_title(title) + "\n(no data)"
    items = list(mapping.items())
    if sort_numeric:
        items.sort(key=lambda kv: kv[0])
    else:
        items.sort(key=lambda kv: (-kv[1], str(kv[0])))
    maxv = max(float(v) for _, v in items)
    lines = [chart_title(title)]
    for key, value in items:
        shown = value_fmt(value) if value_fmt else short_number(value)
        lines.append("%s │%s│ %s" % (pad(key, 18), utf8_bar(float(value), maxv, width=width), shown))
    return "\n".join(lines)


def render_level_chart(mapping: Dict[int, int], title: str, width: int = 30) -> str:
    lines = [chart_title(title)]
    maxv = max([float(v) for v in mapping.values()] or [1.0])
    for level in range(1, 13):
        value = float(mapping.get(level, 0))
        label = "L%02d %-12s" % (level, LEVEL_NAMES[level][:12])
        lines.append("%s │%s│ %s" % (label, utf8_bar(value, maxv, width=width), short_number(value)))
    return "\n".join(lines)


def render_heatmap(rows: Sequence[str], cols: Sequence[Any], data: Dict[str, Dict[Any, float]], title: str) -> str:
    lines = [chart_title(title)]
    if not rows or not cols:
        return "\n".join(lines + ["(no data)"])
    maxv = 0.0
    for r in rows:
        row = data.get(r, {})
        for c in cols:
            maxv = max(maxv, float(row.get(c, 0.0)))
    if maxv <= 0:
        maxv = 1.0
    header = " " * 12 + " ".join([pad(c, 3) for c in cols])
    lines.append(header)
    for r in rows:
        row = data.get(r, {})
        cells = []
        for c in cols:
            v = float(row.get(c, 0.0))
            idx = int(round(clamp(v / maxv, 0.0, 1.0) * (len(HEAT_CHARS) - 1)))
            cells.append(" %s " % HEAT_CHARS[idx])
        lines.append("%s %s" % (pad(r, 11), "".join(cells)))
    lines.append("Legend: · low  ░▒▓█ high")
    return "\n".join(lines)


def render_table(rows: Sequence[Sequence[Any]], headers: Sequence[str], title: str, widths: Sequence[int]) -> str:
    lines = [chart_title(title)]
    head = " | ".join([pad(h, w) for h, w in zip(headers, widths)])
    sep = "-+-".join(["-" * w for w in widths])
    lines.append(head)
    lines.append(sep)
    for row in rows:
        lines.append(" | ".join([pad(v, w) for v, w in zip(row, widths)]))
    return "\n".join(lines)


def render_tree(node: Tuple[str, List[Any]], title: str) -> str:
    lines = [chart_title(title)]

    def walk(current: Tuple[str, List[Any]], prefix: str = "", is_last: bool = True, root: bool = False) -> None:
        label, children = current
        if root:
            lines.append(label)
        else:
            lines.append(prefix + (TREE_LAST if is_last else TREE_MID) + label)
        if not children:
            return
        next_prefix = prefix + (TREE_BLANK if is_last else TREE_PIPE)
        for idx, child in enumerate(children):
            walk(child, next_prefix, idx == len(children) - 1, False)

    walk(node, root=True)
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Structured hierarchy currency
# ---------------------------------------------------------------------------

class HierarchyBundle:
    __slots__ = ("parts",)

    def __init__(self, parts: Optional[Dict[Tuple[int, str], float]] = None) -> None:
        self.parts: Dict[Tuple[int, str], float] = {}
        if parts:
            for (level, element), amount in parts.items():
                self.add(level, element, amount)

    @classmethod
    def single(cls, level: int, element: str, amount: float) -> "HierarchyBundle":
        b = cls()
        b.add(level, element, amount)
        return b

    @classmethod
    def from_elements(cls, level: int, elements: Dict[str, float]) -> "HierarchyBundle":
        b = cls()
        for element, amount in elements.items():
            b.add(level, element, amount)
        return b

    def copy(self) -> "HierarchyBundle":
        return HierarchyBundle(dict(self.parts))

    def add(self, level: int, element: str, amount: float) -> None:
        if amount <= EPS:
            return
        level = int(clamp(level, 1, 12))
        key = (level, element)
        self.parts[key] = self.parts.get(key, 0.0) + float(amount)

    def add_bundle(self, other: "HierarchyBundle") -> None:
        for (level, element), amount in other.parts.items():
            self.add(level, element, amount)

    def scaled(self, factor: float) -> "HierarchyBundle":
        b = HierarchyBundle()
        if factor <= EPS:
            return b
        for (level, element), amount in self.parts.items():
            b.add(level, element, amount * factor)
        return b

    def to_number(self) -> float:
        return sum(amount * HEIGHT_MULTIPLIERS[level] for (level, _element), amount in self.parts.items())

    def dominant_element(self) -> str:
        if not self.parts:
            return "capital"
        scores: Dict[str, float] = defaultdict(float)
        for (level, element), amount in self.parts.items():
            scores[element] += amount * HEIGHT_MULTIPLIERS[level]
        return max(scores.items(), key=lambda kv: kv[1])[0]

    def short(self, max_parts: int = 4) -> str:
        if not self.parts:
            return "∅"
        ranked = sorted(self.parts.items(), key=lambda kv: kv[1] * HEIGHT_MULTIPLIERS[kv[0][0]], reverse=True)
        out = []
        for (level, element), raw in ranked[:max_parts]:
            out.append(f"L{level}:{element}={raw:.1f}")
        if len(ranked) > max_parts:
            out.append("...")
        return ", ".join(out)


class Wallet:
    __slots__ = ("balance",)

    def __init__(self) -> None:
        self.balance = HierarchyBundle()

    def deposit(self, bundle: HierarchyBundle) -> None:
        self.balance.add_bundle(bundle)

    def value(self) -> float:
        return self.balance.to_number()

    def can_pay(self, value: float) -> bool:
        return self.value() + EPS >= value

    def withdraw_number(self, value: float, prefer: Optional[str] = None) -> HierarchyBundle:
        if value <= EPS:
            return HierarchyBundle()
        if not self.can_pay(value):
            raise ValueError("insufficient hierarchy currency")
        payment = HierarchyBundle()
        remaining = value
        items = list(self.balance.parts.items())

        def key(item: Tuple[Tuple[int, str], float]) -> Tuple[int, int, str]:
            (level, element), _amount = item
            pref = 0 if prefer and element == prefer else 1
            return (pref, level, element)

        items.sort(key=key)
        for (level, element), raw in items:
            if remaining <= EPS:
                break
            component_value = raw * HEIGHT_MULTIPLIERS[level]
            used_value = min(component_value, remaining)
            used_raw = used_value / HEIGHT_MULTIPLIERS[level]
            current = self.balance.parts.get((level, element), 0.0)
            new_raw = current - used_raw
            if new_raw <= EPS:
                self.balance.parts.pop((level, element), None)
            else:
                self.balance.parts[(level, element)] = new_raw
            payment.add(level, element, used_raw)
            remaining -= used_value
        return payment


# ---------------------------------------------------------------------------
# Deep inheritance chain
# ---------------------------------------------------------------------------

class EntityBase:
    kind = "entity"
    __slots__ = ("id", "name")

    def __init__(self, entity_id: int, name: str) -> None:
        self.id = entity_id
        self.name = name


class NamedEntity(EntityBase):
    kind = "named_entity"


class IndexedEntity(NamedEntity):
    kind = "indexed_entity"
    __slots__ = ("created_tick",)

    def __init__(self, entity_id: int, name: str, created_tick: int = 0) -> None:
        super().__init__(entity_id, name)
        self.created_tick = created_tick


class LocatedEntity(IndexedEntity):
    kind = "located_entity"
    __slots__ = ("scope", "body", "country_id")

    def __init__(self, entity_id: int, name: str, created_tick: int = 0, scope: str = "Solar System", body: str = "Solar System", country_id: Optional[int] = None) -> None:
        super().__init__(entity_id, name, created_tick)
        self.scope = scope
        self.body = body
        self.country_id = country_id


class HierarchyEntity(LocatedEntity):
    kind = "hierarchy_entity"
    __slots__ = ("level", "domain", "elements", "last_score")

    def __init__(self, entity_id: int, name: str, created_tick: int = 0, scope: str = "Solar System", body: str = "Solar System", country_id: Optional[int] = None, level: int = 1, domain: str = "general", elements: Optional[Dict[str, float]] = None) -> None:
        super().__init__(entity_id, name, created_tick, scope, body, country_id)
        self.level = int(clamp(level, 1, 12))
        self.domain = domain
        self.elements = dict(elements or {})
        self.last_score = 0.0

    def structural_bundle(self) -> HierarchyBundle:
        return HierarchyBundle.from_elements(self.level, self.elements)

    def structural_number(self) -> float:
        return self.structural_bundle().to_number()


class AccountEntity(HierarchyEntity):
    kind = "account_entity"
    __slots__ = ("wallet", "privilege_ids", "burden_ids", "inventory_units")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.wallet = Wallet()
        self.privilege_ids: List[int] = []
        self.burden_ids: List[int] = []
        self.inventory_units = 0

    def status_number(self, privileges: Optional[Dict[int, "Privilege"]] = None, burdens: Optional[Dict[int, "Disadvantage"]] = None) -> float:
        boost = 0.0
        drag = 0.0
        if privileges:
            for pid in self.privilege_ids:
                p = privileges.get(pid)
                if p and p.active:
                    boost += p.structural_number() * 0.15
        if burdens:
            for bid in self.burden_ids:
                b = burdens.get(bid)
                if b and b.active:
                    drag += b.structural_number() * 0.15
        return self.structural_number() + self.wallet.value() + boost - drag

    def refresh_level(self, privileges: Optional[Dict[int, "Privilege"]] = None, burdens: Optional[Dict[int, "Disadvantage"]] = None) -> None:
        self.last_score = self.status_number(privileges, burdens)
        self.level = level_from_number(self.last_score)

    def entitlement_level(self, domain: str, privileges: Dict[int, "Privilege"], burdens: Dict[int, "Disadvantage"]) -> int:
        delta = 0
        for pid in self.privilege_ids:
            p = privileges.get(pid)
            if p and p.active and (p.domain == domain or p.domain == "general"):
                delta += p.level_boost
        for bid in self.burden_ids:
            b = burdens.get(bid)
            if b and b.active and (b.domain == domain or b.domain == "general"):
                delta -= b.level_penalty
        return int(clamp(self.level + delta, 1, 12))


class TradableEntity(AccountEntity):
    kind = "tradable_entity"
    __slots__ = ("tradable", "owner_id")

    def __init__(self, *args: Any, owner_id: Optional[int] = None, tradable: bool = True, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.owner_id = owner_id
        self.tradable = tradable

    def quote(self) -> HierarchyBundle:
        base = max(1.0, self.structural_number() * 0.08)
        raw = base / HEIGHT_MULTIPLIERS[self.level]
        return HierarchyBundle.single(self.level, "capital", raw)


class InstitutionalEntity(TradableEntity):
    kind = "institutional_entity"
    __slots__ = ("member_ids",)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.member_ids: List[int] = []


class Organization(InstitutionalEntity):
    kind = "organization"
    __slots__ = ()


class CelestialBody(Organization):
    kind = "celestial_body"
    __slots__ = ("body_type", "un_id", "defense_id", "country_ids")

    def __init__(self, *args: Any, body_type: str = "planet", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.body_type = body_type
        self.un_id: Optional[int] = None
        self.defense_id: Optional[int] = None
        self.country_ids: List[int] = []


class PoliticalOrganization(Organization):
    kind = "political_organization"
    __slots__ = ()


class UNOrganization(PoliticalOrganization):
    kind = "un_organization"
    __slots__ = ()


class DefenseOrganization(PoliticalOrganization):
    kind = "defense_organization"
    __slots__ = ("readiness",)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.readiness = 0.5


class Alliance(DefenseOrganization):
    kind = "alliance"
    __slots__ = ("country_ids",)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.country_ids: List[int] = []


class Country(PoliticalOrganization):
    kind = "country"
    __slots__ = ("company_ids", "worker_ids", "alliance_ids", "economic_power", "military_power")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.company_ids: List[int] = []
        self.worker_ids: List[int] = []
        self.alliance_ids: List[int] = []
        self.economic_power = 0.0
        self.military_power = 0.0


class EmployerOrganization(Organization):
    kind = "employer_organization"
    __slots__ = ("capacity", "worker_ids", "production_score")

    def __init__(self, *args: Any, capacity: int = 0, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.capacity = capacity
        self.worker_ids: List[int] = []
        self.production_score = 0.0


class Company(EmployerOrganization):
    kind = "company"
    __slots__ = ("sector", "product_ids", "research_intensity", "military_contract_share")

    def __init__(self, *args: Any, sector: str = "general", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.sector = sector
        self.product_ids: List[int] = []
        self.research_intensity = 0.0
        self.military_contract_share = 0.0

    def quote(self) -> HierarchyBundle:
        base = max(100.0, self.status_number() * 0.35)
        raw = base / HEIGHT_MULTIPLIERS[self.level]
        b = HierarchyBundle.single(self.level, "capital", raw * 0.55)
        b.add(self.level, "market_access", raw * 0.30)
        b.add(self.level, self.sector, raw * 0.15)
        return b


class HumanEntity(TradableEntity):
    kind = "human_entity"
    __slots__ = ("age", "sex", "traits", "employer_id")

    def __init__(self, *args: Any, age: int = 30, sex: str = "other", traits: Optional[Dict[str, float]] = None, **kwargs: Any) -> None:
        super().__init__(*args, tradable=False, **kwargs)
        self.age = age
        self.sex = sex
        self.traits = dict(traits or {})
        self.employer_id: Optional[int] = None

    def work_power(self) -> float:
        af = age_curve(self.age, self.sex)
        t = self.traits
        base = (
            t.get("skill", 0.5) * 80.0 + t.get("trust", 0.5) * 40.0 +
            t.get("risk", 0.5) * 25.0 + t.get("leadership", 0.5) * 25.0 +
            t.get("care", 0.5) * 18.0 + t.get("media", 0.5) * 16.0 +
            t.get("science", 0.5) * 30.0 + t.get("military", 0.5) * 18.0
        )
        return base * af * (1.0 + self.level * 0.035)


class Worker(HumanEntity):
    kind = "worker"
    __slots__ = ("occupation",)

    def __init__(self, *args: Any, occupation: str = "labor", **kwargs: Any) -> None:
        super().__init__(*args, domain=occupation, **kwargs)
        self.occupation = occupation

    def recalc_elements(self) -> None:
        p = self.work_power()
        t = self.traits
        self.elements["labor"] = p * 0.45
        self.elements["skill"] = p * (0.25 + t.get("skill", 0.5) * 0.15)
        self.elements["trust"] = p * t.get("trust", 0.5) * 0.12
        self.elements["care"] = p * t.get("care", 0.5) * 0.08
        self.elements["media"] = p * t.get("media", 0.5) * 0.07
        self.elements["science"] = p * t.get("science", 0.5) * 0.08
        self.elements["military"] = p * t.get("military", 0.5) * 0.06


class Product(TradableEntity):
    kind = "product"
    __slots__ = ("min_level", "stock", "quality", "units_sold")

    def __init__(self, *args: Any, min_level: int = 1, stock: int = 0, quality: float = 1.0, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.min_level = int(clamp(min_level, 1, 12))
        self.stock = stock
        self.quality = quality
        self.units_sold = 0

    def quote(self) -> HierarchyBundle:
        scarcity = 1.0 + 2.0 / math.sqrt(max(1, self.stock))
        raw = max(1.0, self.min_level * (0.65 + self.quality) * scarcity * (1.0 + self.level / 5.0))
        b = HierarchyBundle.single(self.min_level, self.domain, raw * 0.58)
        b.add(self.level, "market_access", raw * 0.24)
        b.add(max(1, self.level - 1), "capital", raw * 0.18)
        return b


class Privilege(TradableEntity):
    kind = "privilege"
    __slots__ = ("level_boost", "duration", "active")

    def __init__(self, *args: Any, level_boost: int = 1, duration: int = 3, active: bool = True, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.level_boost = int(clamp(level_boost, 1, 4))
        self.duration = duration
        self.active = active
        self.elements.setdefault("privilege", 10.0 * self.level_boost)

    def quote(self) -> HierarchyBundle:
        raw = max(3.0, (self.level_boost ** 2) * (2.0 + self.duration) * (1.0 + self.level))
        b = HierarchyBundle.single(self.level, "privilege", raw * 0.70)
        b.add(self.level, self.domain, raw * 0.30)
        return b


class Disadvantage(Privilege):
    kind = "disadvantage"
    __slots__ = ("level_penalty",)

    def __init__(self, *args: Any, level_penalty: int = 1, **kwargs: Any) -> None:
        super().__init__(*args, level_boost=1, **kwargs)
        self.level_boost = 0
        self.level_penalty = int(clamp(level_penalty, 1, 5))
        self.elements.setdefault("burden", 10.0 * self.level_penalty)

    def quote(self) -> HierarchyBundle:
        raw = max(4.0, (self.level_penalty ** 2) * (2.0 + self.duration) * (1.0 + self.level))
        b = HierarchyBundle.single(self.level, "burden", raw * 0.60)
        b.add(self.level, self.domain, raw * 0.40)
        return b


class Market(TradableEntity):
    kind = "market"
    __slots__ = ("listed_product_ids", "listed_market_ids", "fee_rate", "trade_count", "failed_count", "market_trade_count", "volume", "recent")

    def __init__(self, *args: Any, fee_rate: float = 0.015, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.listed_product_ids: List[int] = []
        self.listed_market_ids: List[int] = []
        self.fee_rate = fee_rate
        self.trade_count = 0
        self.failed_count = 0
        self.market_trade_count = 0
        self.volume = 0.0
        self.recent: List[str] = []

    def quote(self) -> HierarchyBundle:
        base = max(500.0, self.volume * 0.12 + self.trade_count * 8.0 + self.structural_number() * 0.70)
        scope_factor = {"Solar System": 4.5, "Earth": 2.5, "Moon": 1.8, "Mars": 2.1}.get(self.scope, 1.4)
        raw = base * scope_factor / HEIGHT_MULTIPLIERS[self.level]
        b = HierarchyBundle.single(self.level, "market_access", raw * 0.48)
        b.add(self.level, self.domain, raw * 0.34)
        b.add(max(1, self.level - 1), "governance", raw * 0.18)
        return b

    def remember(self, text: str) -> None:
        self.recent.append(text)
        if len(self.recent) > 8:
            self.recent.pop(0)


class MarketRightsExchange(Market):
    kind = "market_rights_exchange"
    __slots__ = ()


# ---------------------------------------------------------------------------
# Scale configs
# ---------------------------------------------------------------------------

SCALE_CONFIGS = {
    "demo": {
        "earth_countries": 8, "moon_countries": 3, "mars_countries": 4,
        "companies": 100, "workers": 1500, "products": 700,
        "product_trades": 2200, "privilege_trades": 140, "burden_trades": 90, "market_trades": 40,
    },
    "large": {
        "earth_countries": 72, "moon_countries": 12, "mars_countries": 18,
        "companies": 1600, "workers": 30000, "products": 12000,
        "product_trades": 42000, "privilege_trades": 2200, "burden_trades": 1500, "market_trades": 520,
    },
    "huge": {
        "earth_countries": 180, "moon_countries": 30, "mars_countries": 45,
        "companies": 5500, "workers": 150000, "products": 42000,
        "product_trades": 180000, "privilege_trades": 9000, "burden_trades": 6500, "market_trades": 2200,
    },
}


# ---------------------------------------------------------------------------
# Simulation engine
# ---------------------------------------------------------------------------

class SolarHierarchyMarketSimulation:
    def __init__(self, profile: str = "large", seed: int = 42, quiet: bool = False) -> None:
        if profile not in SCALE_CONFIGS:
            raise ValueError("unknown profile")
        self.profile = profile
        self.cfg = dict(SCALE_CONFIGS[profile])
        self.rng = FastRNG(seed)
        self.seed = seed
        self.quiet = quiet
        self.tick = 0
        self.next_id = 1

        self.entities: Dict[int, AccountEntity] = {}
        self.organizations: Dict[int, Organization] = {}
        self.bodies: Dict[str, CelestialBody] = {}
        self.un_by_scope: Dict[str, int] = {}
        self.defense_by_scope: Dict[str, int] = {}
        self.countries: Dict[int, Country] = {}
        self.alliances: Dict[int, Alliance] = {}
        self.companies: Dict[int, Company] = {}
        self.workers: Dict[int, Worker] = {}
        self.products: Dict[int, Product] = {}
        self.privileges: Dict[int, Privilege] = {}
        self.burdens: Dict[int, Disadvantage] = {}
        self.markets: Dict[int, Market] = {}
        self.market_rights_exchanges: List[int] = []
        self.product_markets: List[int] = []
        self.actor_ids: List[int] = []

        self.market_ownership_changes = 0
        self.manual_lifts = 0

    # ----------------------------- helpers -----------------------------

    def new_id(self) -> int:
        eid = self.next_id
        self.next_id += 1
        return eid

    def register(self, e: AccountEntity) -> int:
        self.entities[e.id] = e
        if isinstance(e, Organization):
            self.organizations[e.id] = e
        if isinstance(e, CelestialBody):
            self.bodies[e.name] = e
        if isinstance(e, Country):
            self.countries[e.id] = e
        if isinstance(e, Alliance):
            self.alliances[e.id] = e
        if isinstance(e, Company):
            self.companies[e.id] = e
        if isinstance(e, Worker):
            self.workers[e.id] = e
        if isinstance(e, Product):
            self.products[e.id] = e
        if isinstance(e, Privilege) and not isinstance(e, Disadvantage):
            self.privileges[e.id] = e
        if isinstance(e, Disadvantage):
            self.burdens[e.id] = e
        if isinstance(e, Market):
            self.markets[e.id] = e
        if isinstance(e, MarketRightsExchange):
            self.market_rights_exchanges.append(e.id)
        return e.id

    def log(self, s: str) -> None:
        if not self.quiet:
            print(s)

    def get(self, eid: int) -> AccountEntity:
        return self.entities[eid]

    def weighted_country_id(self) -> int:
        ids = list(self.countries.keys())
        total = 0.0
        weights = []
        for cid in ids:
            c = self.countries[cid]
            body_bonus = 5.0 if c.body == "Earth" else (1.6 if c.body == "Mars" else 1.1)
            w = body_bonus * max(1.0, c.level)
            weights.append(w)
            total += w
        roll = self.rng.random() * total
        acc = 0.0
        for cid, w in zip(ids, weights):
            acc += w
            if roll <= acc:
                return cid
        return ids[-1]

    def settle(self, buyer_id: int, seller_id: int, price: HierarchyBundle, prefer: Optional[str] = None) -> bool:
        buyer = self.entities[buyer_id]
        seller = self.entities[seller_id]
        value = price.to_number()
        if not buyer.wallet.can_pay(value):
            return False
        payment = buyer.wallet.withdraw_number(value, prefer=prefer)
        seller.wallet.deposit(payment)
        return True

    # ----------------------------- building ----------------------------

    def build(self) -> None:
        self.log(f"Building hierarchy-market simulation profile={self.profile} seed={self.seed}")
        self.build_bodies_un_defense()
        self.build_countries_alliances()
        self.build_markets()
        self.build_companies()
        self.build_workers()
        self.assign_workers()
        self.build_products()
        self.seed_wallets()
        self.refresh_levels()
        self.actor_ids = list(self.workers.keys()) + list(self.companies.keys()) + list(self.countries.keys()) + list(self.un_by_scope.values()) + list(self.defense_by_scope.values())
        self.log(self.build_report())

    def build_bodies_un_defense(self) -> None:
        solar_id = self.register(Organization(self.new_id(), "Solar System", scope="Solar System", body="Solar System", level=12, domain="governance", elements={"governance": 8000, "infrastructure": 5000, "market_access": 4000}, owner_id=None))
        solar_un = self.register(UNOrganization(self.new_id(), "Solar System United Nations", scope="Solar System", body="Solar System", level=12, domain="governance", elements={"governance": 5000, "trust": 2700, "market_access": 3000}, owner_id=solar_id))
        solar_def = self.register(DefenseOrganization(self.new_id(), "Solar System Defense Organization", scope="Solar System", body="Solar System", level=12, domain="defense", elements={"military": 4500, "governance": 2000, "logistics": 2500}, owner_id=solar_un))
        self.un_by_scope["Solar System"] = solar_un
        self.defense_by_scope["Solar System"] = solar_def

        for name, body_type, level, elements in [
            ("Earth", "planet", 10, {"infrastructure": 6000, "capital": 5500, "governance": 2800}),
            ("Moon", "moon", 8, {"infrastructure": 1600, "logistics": 1800, "market_access": 1050}),
            ("Mars", "planet", 9, {"infrastructure": 2400, "science": 1500, "market_access": 1600}),
        ]:
            body_id = self.register(CelestialBody(self.new_id(), name, scope=name, body=name, level=level, domain="governance", elements=elements, body_type=body_type, owner_id=solar_un))
            un_id = self.register(UNOrganization(self.new_id(), f"United Nations of {name}", scope=name, body=name, level=level, domain="governance", elements={"governance": 1200 * level, "trust": 700 * level, "market_access": 550 * level}, owner_id=body_id))
            defense_id = self.register(DefenseOrganization(self.new_id(), f"{name} Defense Organization", scope=name, body=name, level=level, domain="defense", elements={"military": 900 * level, "logistics": 450 * level, "trust": 220 * level}, owner_id=un_id))
            self.bodies[name].un_id = un_id
            self.bodies[name].defense_id = defense_id
            self.un_by_scope[name] = un_id
            self.defense_by_scope[name] = defense_id
            self.organizations[solar_un].member_ids.append(un_id)
            self.organizations[solar_def].member_ids.append(defense_id)

    def build_countries_alliances(self) -> None:
        specs = [("Earth", self.cfg["earth_countries"], "Earth Republic", 4, 8), ("Moon", self.cfg["moon_countries"], "Lunar Canton", 3, 7), ("Mars", self.cfg["mars_countries"], "Martian Commonwealth", 4, 8)]
        for body, count, prefix, lo, hi in specs:
            un_id = self.un_by_scope[body]
            for i in range(1, count + 1):
                level = self.rng.randint(lo, hi)
                cid = self.register(Country(self.new_id(), f"{prefix} {i:03d}", scope=body, body=body, level=level, domain="governance", elements={"governance": self.rng.uniform(80, 260) * level, "capital": self.rng.uniform(120, 420) * level, "military": self.rng.uniform(60, 260) * level, "infrastructure": self.rng.uniform(100, 380) * level, "trust": self.rng.uniform(40, 160) * level}, owner_id=un_id))
                self.bodies[body].country_ids.append(cid)
                self.organizations[un_id].member_ids.append(cid)
                self.organizations[self.un_by_scope["Solar System"]].member_ids.append(cid)

        for body in ("Earth", "Moon", "Mars"):
            defense_id = self.defense_by_scope[body]
            country_ids = list(self.bodies[body].country_ids)
            alliance_count = max(2, int(math.sqrt(len(country_ids))))
            alliance_ids = []
            for i in range(1, alliance_count + 1):
                level = int(clamp(self.bodies[body].level - 2 + self.rng.randint(0, 3), 3, 11))
                aid = self.register(Alliance(self.new_id(), f"{body} Defense Alliance {i:02d}", scope=body, body=body, level=level, domain="defense", elements={"military": self.rng.uniform(200, 600) * level, "logistics": self.rng.uniform(120, 400) * level, "trust": self.rng.uniform(80, 260) * level}, owner_id=defense_id))
                alliance_ids.append(aid)
                self.organizations[defense_id].member_ids.append(aid)
            for cid in country_ids:
                aid = self.rng.choice(alliance_ids)
                self.alliances[aid].country_ids.append(cid)
                self.countries[cid].alliance_ids.append(aid)

    def build_markets(self) -> None:
        for scope, ceiling in [("Solar System", 12), ("Earth", 10), ("Moon", 8), ("Mars", 9)]:
            owner = self.un_by_scope[scope]
            for level in range(1, 13):
                if level > ceiling + 2:
                    continue
                for domain in DOMAINS:
                    cls = MarketRightsExchange if domain == "market_rights" else Market
                    mid = self.register(cls(self.new_id(), f"{scope} L{level:02d} {domain.replace('_', ' ').title()} Market", scope=scope, body=scope if scope != "Solar System" else "Solar System", level=level, domain=domain, elements={"market_access": 35 * level, "logistics": 12 * level, domain: 20 * level}, owner_id=owner, fee_rate=0.010 + 0.002 * level))
                    self.organizations[owner].member_ids.append(mid)

    def build_companies(self) -> None:
        country_ids = list(self.countries.keys())
        for i in range(1, self.cfg["companies"] + 1):
            cid = self.weighted_country_id() if country_ids else self.rng.choice(country_ids)
            country = self.countries[cid]
            sector = self.rng.choice(SECTORS)
            level = int(clamp(round(self.rng.triangular_like(2, 9, country.level)), 1, 11))
            company = Company(self.new_id(), f"{sector.title()} Hierarchy Company {i:05d}", scope=country.scope, body=country.body, country_id=cid, level=level, domain=sector, elements={"capital": self.rng.uniform(60, 420) * level, "skill": self.rng.uniform(30, 260) * level, "market_access": self.rng.uniform(20, 280) * level, "logistics": self.rng.uniform(20, 200) * level, "science": self.rng.uniform(10, 180) * level if sector in ("research", "compute", "medicine", "terraforming") else self.rng.uniform(0, 40) * level, "military": self.rng.uniform(20, 180) * level if sector == "defense" else self.rng.uniform(0, 20) * level, "trust": self.rng.uniform(15, 90) * level}, owner_id=cid, sector=sector, capacity=self.rng.randint(30, 500))
            company.research_intensity = self.rng.random() if sector in ("research", "compute", "medicine", "terraforming") else self.rng.random() * 0.35
            company.military_contract_share = self.rng.random() if sector == "defense" else self.rng.random() * 0.12
            self.register(company)
            self.countries[cid].company_ids.append(company.id)

    def build_workers(self) -> None:
        for i in range(1, self.cfg["workers"] + 1):
            cid = self.weighted_country_id()
            country = self.countries[cid]
            occupation = self.rng.choice(SECTORS)
            sex_roll = self.rng.random()
            sex = "female" if sex_roll < 0.49 else ("male" if sex_roll < 0.98 else "other")
            age = int(clamp(round(39 + (self.rng.random() + self.rng.random() + self.rng.random() - 1.5) * 28), 16, 82))
            base_skill = self.rng.beta_like(2.5, 2.2)
            traits = {"skill": base_skill, "trust": self.rng.beta_like(3.0, 2.0), "risk": self.rng.beta_like(2.0, 2.6), "leadership": self.rng.beta_like(1.8, 3.0), "care": self.rng.beta_like(2.0, 2.4), "media": self.rng.beta_like(1.5, 3.5), "science": self.rng.beta_like(1.6, 3.0), "military": self.rng.beta_like(1.3, 4.0)}
            if occupation == "care":
                traits["care"] = max(traits["care"], self.rng.beta_like(4.5, 1.7)); traits["trust"] = max(traits["trust"], self.rng.beta_like(4.0, 1.8))
            if occupation == "media":
                traits["media"] = max(traits["media"], self.rng.beta_like(4.0, 1.8))
            if occupation in ("research", "compute", "medicine", "terraforming"):
                traits["science"] = max(traits["science"], self.rng.beta_like(4.0, 1.8))
            if occupation == "defense":
                traits["military"] = max(traits["military"], self.rng.beta_like(4.0, 1.8)); traits["risk"] = max(traits["risk"], self.rng.beta_like(3.5, 2.0))
            level = int(clamp(round(self.rng.triangular_like(1, 7, 3 + base_skill * 4)), 1, 10))
            w = Worker(self.new_id(), f"Worker {i:07d}", scope=country.scope, body=country.body, country_id=cid, level=level, occupation=occupation, age=age, sex=sex, traits=traits, owner_id=None, elements={})
            w.recalc_elements()
            self.register(w)
            country.worker_ids.append(w.id)

    def assign_workers(self) -> None:
        by_country_sector: Dict[Tuple[int, str], List[int]] = defaultdict(list)
        by_country_any: Dict[int, List[int]] = defaultdict(list)
        for cid, c in self.countries.items():
            for comp_id in c.company_ids:
                comp = self.companies[comp_id]
                by_country_sector[(cid, comp.sector)].append(comp_id)
                by_country_any[cid].append(comp_id)
        for worker in self.workers.values():
            candidates = by_country_sector.get((worker.country_id, worker.occupation)) or by_country_any.get(worker.country_id, []) or list(self.companies.keys())
            for _ in range(5):
                comp = self.companies[self.rng.choice(candidates)]
                if len(comp.worker_ids) < comp.capacity:
                    comp.worker_ids.append(worker.id)
                    worker.employer_id = comp.id
                    break

    def build_products(self) -> None:
        market_by_scope_domain_level: Dict[Tuple[str, str, int], List[int]] = defaultdict(list)
        for mid, m in self.markets.items():
            market_by_scope_domain_level[(m.scope, m.domain, m.level)].append(mid)
        company_ids = list(self.companies.keys())
        for i in range(1, self.cfg["products"] + 1):
            comp = self.companies[self.rng.choice(company_ids)]
            level = int(clamp(round(self.rng.triangular_like(1, 10, comp.level)), 1, 12))
            min_level = int(clamp(level + self.rng.choice([-1, 0, 0, 1]), 1, 12))
            p = Product(self.new_id(), f"{comp.sector.title()} Product {i:07d}", scope=comp.scope, body=comp.body, country_id=comp.country_id, level=level, domain=comp.sector, elements={comp.sector: self.rng.uniform(10, 120) * level, "skill": self.rng.uniform(2, 50) * level, "market_access": self.rng.uniform(2, 40) * level}, owner_id=comp.id, min_level=min_level, stock=self.rng.randint(40, 5000), quality=self.rng.uniform(0.5, 1.8) + comp.level * 0.035)
            self.register(p)
            comp.product_ids.append(p.id)
            choices: List[int] = []
            for lv in (min_level - 1, min_level, min_level + 1):
                choices.extend(market_by_scope_domain_level.get((comp.scope, comp.sector, lv), []))
            if not choices:
                choices = market_by_scope_domain_level.get(("Solar System", comp.sector, min_level), [])
            if choices:
                mid = self.rng.choice(choices)
                self.markets[mid].listed_product_ids.append(p.id)
                if mid not in self.product_markets:
                    self.product_markets.append(mid)
        for ex_id in self.market_rights_exchanges:
            ex = self.markets[ex_id]
            eligible = [mid for mid, m in self.markets.items() if mid != ex_id and m.scope == ex.scope and abs(m.level - ex.level) <= 2]
            self.rng.shuffle(eligible)
            ex.listed_market_ids.extend(eligible[:220])

    def seed_wallets(self) -> None:
        for e in self.entities.values():
            n = max(1.0, e.structural_number())
            raw = max(4.0, math.sqrt(n) * self.rng.uniform(0.8, 2.4))
            if isinstance(e, Worker): raw *= 0.45
            elif isinstance(e, Company): raw *= 8.0
            elif isinstance(e, Country): raw *= 35.0
            elif isinstance(e, UNOrganization): raw *= 75.0
            elif isinstance(e, DefenseOrganization): raw *= 45.0
            elif isinstance(e, Market): raw *= 5.0
            e.wallet.deposit(HierarchyBundle.single(e.level, "capital", raw * 0.55))
            e.wallet.deposit(HierarchyBundle.single(e.level, "market_access", raw * 0.25))
            e.wallet.deposit(HierarchyBundle.single(e.level, e.domain if e.domain != "general" else "trust", raw * 0.20))

    # ----------------------------- simulation --------------------------

    def simulate(self, ticks: int) -> None:
        for _ in range(ticks):
            self.tick += 1
            self.age_and_decay()
            self.production()
            self.country_and_defense_power()
            self.automatic_mobility()
            self.manual_lift()
            self.trade_products()
            self.trade_privileges()
            self.trade_burdens()
            self.trade_markets_as_assets()
            self.refresh_levels()
            if not self.quiet:
                print(self.tick_report())

    def age_and_decay(self) -> None:
        # Full worker loop is feasible because relationships are ID-based.
        for w in self.workers.values():
            w.age += 1
            w.recalc_elements()
        for p in self.privileges.values():
            p.duration -= 1
            if p.duration <= 0: p.active = False
        for b in self.burdens.values():
            b.duration -= 1
            if b.duration <= 0: b.active = False

    def production(self) -> None:
        workers = self.workers
        for comp in self.companies.values():
            wp = 0.0
            for wid in comp.worker_ids:
                wp += workers[wid].work_power()
            account_factor = math.log1p(max(0.0, comp.wallet.value()))
            sector_bonus = 1.0 + comp.research_intensity * 0.3 + comp.military_contract_share * 0.2
            volatility = self.rng.uniform(0.82, 1.18)
            comp.production_score = (wp * 1.25 + comp.structural_number() * 0.18 + account_factor * 15.0) * sector_bonus * volatility
            raw_income = max(0.0, comp.production_score / HEIGHT_MULTIPLIERS[comp.level] * 0.018)
            comp.wallet.deposit(HierarchyBundle.single(comp.level, comp.sector, raw_income))
            if comp.product_ids:
                add_stock = int(max(0, comp.production_score / 5500.0))
                if add_stock:
                    for pid in self.rng.sample(comp.product_ids, min(3, len(comp.product_ids))):
                        self.products[pid].stock += add_stock

    def country_and_defense_power(self) -> None:
        for country in self.countries.values():
            company_power = sum(self.companies[cid].production_score + self.companies[cid].status_number() * 0.03 for cid in country.company_ids)
            sample_workers = country.worker_ids if len(country.worker_ids) <= 500 else self.rng.sample(country.worker_ids, 500)
            worker_power = sum(self.workers[wid].work_power() for wid in sample_workers)
            if country.worker_ids:
                worker_power *= len(country.worker_ids) / max(1, len(sample_workers))
            country.economic_power = company_power + worker_power * 0.4
            country.military_power = country.elements.get("military", 0.0) * HEIGHT_MULTIPLIERS[country.level] + country.economic_power * 0.04
            country.elements["capital"] = max(country.elements.get("capital", 0.0), country.economic_power / HEIGHT_MULTIPLIERS[country.level] * 0.008)
            country.elements["military"] = max(country.elements.get("military", 0.0), country.military_power / HEIGHT_MULTIPLIERS[country.level] * 0.012)
            raw = country.economic_power * 0.00025 / HEIGHT_MULTIPLIERS[country.level]
            if raw > 0:
                country.wallet.deposit(HierarchyBundle.single(country.level, "governance", raw))
        for defense in self.defense_by_scope.values():
            d = self.entities[defense]
            if isinstance(d, DefenseOrganization):
                member_power = sum(self.entities[mid].status_number() for mid in d.member_ids[:80])
                d.readiness = clamp(math.log1p(member_power) / 18.0, 0.05, 1.0)
                d.elements["military"] = max(d.elements.get("military", 0.0), d.readiness * 500.0)

    def automatic_mobility(self) -> None:
        for c in self.countries.values():
            raw = (c.economic_power * 0.035 + c.military_power * 0.055) / HEIGHT_MULTIPLIERS[c.level] * 0.0015
            if raw > 0: c.wallet.deposit(HierarchyBundle.single(c.level, "governance", raw))
        for comp in self.companies.values():
            raw = (comp.production_score + comp.military_contract_share * comp.production_score * 0.35) / HEIGHT_MULTIPLIERS[comp.level] * 0.001
            if raw > 0: comp.wallet.deposit(HierarchyBundle.single(comp.level, comp.sector, raw))
        for m in self.markets.values():
            if m.trade_count:
                m.elements["market_access"] = m.elements.get("market_access", 0.0) + math.log1p(m.trade_count) * (1.0 + m.level * 0.08)

    def manual_lift(self) -> None:
        worker_ids = list(self.workers.keys())
        sample = self.rng.sample(worker_ids, min(len(worker_ids), max(600, len(worker_ids) // 10)))
        scored = []
        for wid in sample:
            w = self.workers[wid]
            s = w.traits.get("care", 0.0) * 2.0 + w.traits.get("trust", 0.0) * 1.6 + w.traits.get("media", 0.0) * 1.4
            if w.occupation in ("care", "education", "media", "culture"):
                s += 1.0
            s -= w.level * 0.06
            scored.append((s, wid))
        scored.sort(reverse=True)
        targets = [wid for _s, wid in scored[:max(10, len(worker_ids) // 250)]]
        for wid in targets:
            w = self.workers[wid]
            issuer_id = self.un_by_scope.get(w.body, self.un_by_scope["Solar System"])
            boost = 1 if w.level >= 8 else (2 if self.rng.chance(0.35) else 1)
            domain = w.occupation if w.occupation in ("care", "education", "media", "culture") else "care"
            p = Privilege(self.new_id(), f"Manual Uplift {domain.title()} Grant {self.tick}-{self.manual_lifts + 1}", scope=w.scope, body=w.body, country_id=w.country_id, level=int(clamp(w.level + boost, 1, 12)), domain=domain, elements={"privilege": 15.0 * boost, domain: 9.0 * boost, "trust": 5.0 * boost}, owner_id=wid, level_boost=boost, duration=self.rng.randint(2, 6))
            self.register(p)
            w.privilege_ids.append(p.id)
            issuer = self.entities[issuer_id]
            grant_value = 350.0 + w.level * 45.0
            if issuer.wallet.can_pay(grant_value):
                w.wallet.deposit(issuer.wallet.withdraw_number(grant_value, prefer="trust"))
            else:
                w.wallet.deposit(HierarchyBundle.single(w.level, "trust", grant_value / HEIGHT_MULTIPLIERS[w.level]))
            self.manual_lifts += 1

    def actor(self) -> int:
        return self.rng.choice(self.actor_ids)

    def can_access(self, actor_id: int, market: Market, min_level: int, domain: str) -> bool:
        a = self.entities[actor_id]
        return a.entitlement_level(domain, self.privileges, self.burdens) >= max(market.level, min_level)

    def market_fee(self, market: Market, seller_id: int, price_value: float) -> None:
        if market.owner_id and self.entities[seller_id].wallet.can_pay(price_value * market.fee_rate):
            fee = self.entities[seller_id].wallet.withdraw_number(price_value * market.fee_rate, prefer="capital")
            self.entities[market.owner_id].wallet.deposit(fee)

    def trade_products(self) -> None:
        if not self.product_markets: return
        for _ in range(self.cfg["product_trades"]):
            m = self.markets[self.rng.choice(self.product_markets)]
            if not m.listed_product_ids: continue
            p = self.products[self.rng.choice(m.listed_product_ids)]
            if p.stock <= 0 or p.owner_id is None:
                m.failed_count += 1; continue
            buyer_id = self.actor()
            if buyer_id == p.owner_id or not self.can_access(buyer_id, m, p.min_level, p.domain):
                m.failed_count += 1; continue
            price = p.quote().scaled(1.0 + m.level * 0.015)
            value = price.to_number()
            if not self.settle(buyer_id, p.owner_id, price, prefer=p.domain):
                m.failed_count += 1; continue
            self.market_fee(m, p.owner_id, value)
            p.stock -= 1; p.units_sold += 1
            self.entities[buyer_id].inventory_units += 1
            m.trade_count += 1; m.volume += value
            if self.rng.chance(0.02): m.remember(f"PRODUCT {p.name} -> {self.entities[buyer_id].name} for {value:.1f}H")

    def trade_privileges(self) -> None:
        markets = [mid for mid, m in self.markets.items() if m.domain == "privilege"]
        for _ in range(self.cfg["privilege_trades"]):
            buyer_id = self.actor()
            buyer = self.entities[buyer_id]
            issuer_id = self.un_by_scope.get(buyer.body, self.un_by_scope["Solar System"])
            domain = self.rng.choice(DOMAINS[:-2])
            boost = self.rng.choice([1, 1, 1, 2, 2, 3])
            p = Privilege(self.new_id(), f"Tradable {domain.title()} Privilege {self.tick}-{len(self.privileges)+1}", scope=buyer.scope, body=buyer.body, country_id=buyer.country_id, level=int(clamp(buyer.level + boost, 1, 12)), domain=domain, elements={"privilege": 8.0 * boost, domain: 7.0 * boost}, owner_id=issuer_id, level_boost=boost, duration=self.rng.randint(1, 5))
            price = p.quote()
            if self.settle(buyer_id, issuer_id, price, prefer="privilege"):
                self.register(p)
                buyer.privilege_ids.append(p.id)
                p.owner_id = buyer_id
                m = self.markets[self.rng.choice(markets)]
                m.trade_count += 1; m.volume += price.to_number(); m.remember(f"PRIVILEGE {p.name} -> {buyer.name}")

    def trade_burdens(self) -> None:
        markets = [mid for mid, m in self.markets.items() if m.domain == "burden"]
        compensators = list(self.companies.keys()) + list(self.countries.keys()) + list(self.un_by_scope.values())
        for _ in range(self.cfg["burden_trades"]):
            taker_id = self.actor()
            taker = self.entities[taker_id]
            if isinstance(taker, UNOrganization): continue
            comp_id = self.rng.choice(compensators)
            if comp_id == taker_id: continue
            domain = self.rng.choice(["housing", "transport", "labor", "energy", "market_access", "data"])
            penalty = self.rng.choice([1, 1, 2, 2, 3])
            b = Disadvantage(self.new_id(), f"Tradable {domain.title()} Burden {self.tick}-{len(self.burdens)+1}", scope=taker.scope, body=taker.body, country_id=taker.country_id, level=taker.level, domain=domain, elements={"burden": 8.0 * penalty, domain: 5.0 * penalty}, owner_id=comp_id, level_penalty=penalty, duration=self.rng.randint(1, 4))
            price = b.quote()
            if self.entities[comp_id].wallet.can_pay(price.to_number()) and taker.level > 1:
                taker.wallet.deposit(self.entities[comp_id].wallet.withdraw_number(price.to_number(), prefer="burden"))
                self.register(b)
                taker.burden_ids.append(b.id)
                b.owner_id = taker_id
                m = self.markets[self.rng.choice(markets)]
                m.trade_count += 1; m.volume += price.to_number(); m.remember(f"BURDEN {b.name} accepted by {taker.name}")

    def trade_markets_as_assets(self) -> None:
        buyers = list(self.companies.keys()) + list(self.countries.keys()) + list(self.un_by_scope.values()) + list(self.defense_by_scope.values())
        for _ in range(self.cfg["market_trades"]):
            ex = self.markets[self.rng.choice(self.market_rights_exchanges)]
            if not ex.listed_market_ids: continue
            asset = self.markets[self.rng.choice(ex.listed_market_ids)]
            seller_id = asset.owner_id
            buyer_id = self.rng.choice(buyers)
            if not seller_id or buyer_id == seller_id: continue
            buyer = self.entities[buyer_id]
            if buyer.entitlement_level("market_access", self.privileges, self.burdens) < min(12, asset.level + 1):
                ex.failed_count += 1; continue
            price = asset.quote().scaled(0.20)
            if self.settle(buyer_id, seller_id, price, prefer="market_access"):
                asset.owner_id = buyer_id
                ex.market_trade_count += 1; ex.trade_count += 1; ex.volume += price.to_number()
                self.market_ownership_changes += 1
                ex.remember(f"MARKET {asset.name} control -> {buyer.name} for {price.to_number():.1f}H")

    def refresh_levels(self) -> None:
        for w in self.workers.values():
            w.refresh_level(self.privileges, self.burdens)
        for comp in self.companies.values():
            comp.elements["labor"] = sum(self.workers[wid].work_power() for wid in comp.worker_ids) * 0.06
            comp.elements["market_access"] = comp.elements.get("market_access", 0.0) + len(comp.product_ids) * 0.2
            comp.refresh_level(self.privileges, self.burdens)
        for c in self.countries.values():
            c.refresh_level(self.privileges, self.burdens)
        for org in self.organizations.values():
            if isinstance(org, (Company, Country)):
                continue
            if org.member_ids:
                sample = org.member_ids if len(org.member_ids) <= 80 else self.rng.sample(org.member_ids, 80)
                aggregate = math.log1p(sum(self.entities[mid].status_number(self.privileges, self.burdens) for mid in sample))
                org.elements["governance"] = max(org.elements.get("governance", 0.0), aggregate * 40.0)
            org.refresh_level(self.privileges, self.burdens)
        for p in self.products.values(): p.refresh_level(self.privileges, self.burdens)
        for m in self.markets.values(): m.refresh_level(self.privileges, self.burdens)

    # ----------------------------- reports -----------------------------

    def owner_kind(self, owner_id: Optional[int]) -> str:
        if owner_id is None or owner_id not in self.entities:
            return "None"
        owner = self.entities[owner_id]
        return owner.kind

    def count_levels_by_body(self, values: Iterable[HierarchyEntity]) -> Dict[str, Dict[int, int]]:
        out: Dict[str, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
        for v in values:
            out[v.body][v.level] += 1
        return {k: dict(v) for k, v in out.items()}

    def company_sector_stats(self) -> List[Tuple[str, int, float]]:
        counts: Dict[str, int] = defaultdict(int)
        total_status: Dict[str, float] = defaultdict(float)
        for comp in self.companies.values():
            counts[comp.sector] += 1
            total_status[comp.sector] += comp.status_number(self.privileges, self.burdens)
        rows = []
        for sector, count in counts.items():
            rows.append((sector, count, total_status[sector] / max(1, count)))
        rows.sort(key=lambda x: (-x[1], x[0]))
        return rows

    def market_domain_stats(self) -> List[Tuple[str, int, float, float]]:
        counts: Dict[str, int] = defaultdict(int)
        volume: Dict[str, float] = defaultdict(float)
        trades: Dict[str, float] = defaultdict(float)
        for m in self.markets.values():
            counts[m.domain] += 1
            volume[m.domain] += m.volume
            trades[m.domain] += m.trade_count
        rows = []
        for domain, count in counts.items():
            rows.append((domain, count, volume[domain], trades[domain]))
        rows.sort(key=lambda x: (-x[2], x[0]))
        return rows

    def worker_age_stats(self) -> List[Tuple[str, int, float]]:
        counts: Dict[str, int] = defaultdict(int)
        level_sum: Dict[str, float] = defaultdict(float)
        for w in self.workers.values():
            band = age_band(w.age)
            counts[band] += 1
            level_sum[band] += w.level
        order = ["00-17", "18-24", "25-34", "35-44", "45-54", "55-64", "65+"]
        rows = []
        for band in order:
            if counts.get(band, 0):
                rows.append((band, counts[band], level_sum[band] / counts[band]))
        return rows

    def privilege_domain_counts(self) -> Tuple[Dict[str, int], Dict[str, int]]:
        priv: Dict[str, int] = defaultdict(int)
        bur: Dict[str, int] = defaultdict(int)
        for p in self.privileges.values():
            if p.active:
                priv[p.domain] += 1
        for b in self.burdens.values():
            if b.active:
                bur[b.domain] += 1
        return dict(priv), dict(bur)

    def ownership_kind_counts(self, values: Iterable[TradableEntity]) -> Dict[str, int]:
        out: Dict[str, int] = defaultdict(int)
        for v in values:
            out[self.owner_kind(v.owner_id)] += 1
        return dict(out)

    def product_min_level_distribution(self) -> Dict[int, int]:
        out: Dict[int, int] = defaultdict(int)
        for p in self.products.values():
            out[p.min_level] += 1
        return dict(out)

    def organizational_tree(self) -> Tuple[str, List[Any]]:
        def body_branch(body_name: str) -> Tuple[str, List[Any]]:
            countries = [c for c in self.countries.values() if c.body == body_name]
            alliances = [a for a in self.alliances.values() if a.body == body_name]
            companies = [c for c in self.companies.values() if c.body == body_name]
            workers = [w for w in self.workers.values() if w.body == body_name]
            markets = [m for m in self.markets.values() if m.body == body_name]
            children = []
            if body_name in self.un_by_scope:
                un = self.entities[self.un_by_scope[body_name]]
                children.append(("%s [L%02d]" % (un.name, un.level), []))
            if body_name in self.defense_by_scope:
                d = self.entities[self.defense_by_scope[body_name]]
                children.append(("%s [L%02d]" % (d.name, d.level), []))
            children.append(("Alliances: %d" % len(alliances), []))
            children.append(("Countries: %d" % len(countries), []))
            children.append(("Companies: %d" % len(companies), []))
            children.append(("Workers: %d" % len(workers), []))
            children.append(("Markets: %d" % len(markets), []))
            return ("%s  (countries=%d companies=%d workers=%d)" % (body_name, len(countries), len(companies), len(workers)), children)

        root_children = []
        if "Solar System" in self.un_by_scope:
            u = self.entities[self.un_by_scope["Solar System"]]
            root_children.append(("%s [L%02d]" % (u.name, u.level), []))
        if "Solar System" in self.defense_by_scope:
            d = self.entities[self.defense_by_scope["Solar System"]]
            root_children.append(("%s [L%02d]" % (d.name, d.level), []))
        for body_name in ["Earth", "Moon", "Mars"]:
            root_children.append(body_branch(body_name))
        return ("Solar System Hierarchy Root", root_children)

    def visual_report(self) -> str:
        parts: List[str] = []

        parts.append(render_tree(self.organizational_tree(), "ORGANIZATIONAL HIERARCHY TREE"))

        parts.append(render_level_chart(self.level_distribution(self.workers.values()), "WORKER HIERARCHY LEVELS"))
        parts.append(render_level_chart(self.level_distribution(self.companies.values()), "COMPANY HIERARCHY LEVELS"))
        parts.append(render_level_chart(self.level_distribution(self.countries.values()), "COUNTRY HIERARCHY LEVELS"))
        parts.append(render_level_chart(self.level_distribution(self.products.values()), "PRODUCT HIERARCHY LEVELS"))
        parts.append(render_level_chart(self.level_distribution(self.markets.values()), "MARKET HIERARCHY LEVELS"))
        parts.append(render_level_chart(self.product_min_level_distribution(), "PRODUCT ACCESS LEVELS (MIN LEVEL REQUIRED)"))

        body_levels = self.count_levels_by_body(self.workers.values())
        parts.append(render_heatmap([b for b in ["Earth", "Moon", "Mars"] if b in body_levels], list(range(1, 13)), body_levels, "WORKERS BY BODY × LEVEL"))
        company_body_levels = self.count_levels_by_body(self.companies.values())
        parts.append(render_heatmap([b for b in ["Earth", "Moon", "Mars"] if b in company_body_levels], list(range(1, 13)), company_body_levels, "COMPANIES BY BODY × LEVEL"))

        market_heat: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        for m in self.markets.values():
            market_heat[m.domain][m.level] += m.volume if m.volume > 0 else 1.0
        hot_domains = [row[0] for row in self.market_domain_stats()[:10]]
        parts.append(render_heatmap(hot_domains, list(range(1, 13)), market_heat, "MARKET DOMAIN × LEVEL HEATMAP (BY VOLUME)"))

        market_volume_by_domain = {row[0]: row[2] for row in self.market_domain_stats()[:14]}
        parts.append(render_histogram(market_volume_by_domain, "MARKET VOLUME BY DOMAIN", width=32))
        market_trade_by_domain = {row[0]: row[3] for row in self.market_domain_stats()[:14]}
        parts.append(render_histogram(market_trade_by_domain, "MARKET TRADES BY DOMAIN", width=32))

        sector_rows = []
        for sector, count, avg_status in self.company_sector_stats()[:14]:
            sector_rows.append((sector, count, short_number(avg_status), sparkline([count, avg_status])))
        parts.append(render_table(sector_rows, ["Sector", "Companies", "Avg Status", "Shape"], "COMPANY SECTOR TABLE", [18, 10, 12, 12]))

        age_rows = []
        age_counts = {}
        for band, count, avg_level in self.worker_age_stats():
            age_rows.append((band, count, "%.2f" % avg_level, sparkline([count, avg_level])))
            age_counts[band] = count
        parts.append(render_table(age_rows, ["Age band", "Workers", "Avg level", "Shape"], "WORKER AGE TABLE", [12, 10, 10, 12]))
        parts.append(render_histogram(age_counts, "WORKER AGE DISTRIBUTION", width=32, sort_numeric=False))

        priv_counts, bur_counts = self.privilege_domain_counts()
        parts.append(render_histogram(dict(sorted(priv_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:14]), "ACTIVE PRIVILEGES BY DOMAIN", width=32))
        parts.append(render_histogram(dict(sorted(bur_counts.items(), key=lambda kv: (-kv[1], kv[0]))[:14]), "ACTIVE BURDENS BY DOMAIN", width=32))

        parts.append(render_histogram(self.ownership_kind_counts(self.markets.values()), "MARKET OWNERSHIP BY OWNER KIND", width=32))
        parts.append(render_histogram(self.ownership_kind_counts(self.products.values()), "PRODUCT OWNERSHIP BY OWNER KIND", width=32))

        body_entity_counts = {"Earth": 0, "Moon": 0, "Mars": 0, "Solar System": 0}
        for e in self.entities.values():
            body_entity_counts[e.body] = body_entity_counts.get(e.body, 0) + 1
        parts.append(render_histogram(body_entity_counts, "ALL ENTITIES BY BODY", width=32))

        wallet_rows = []
        for name, values in (("workers", self.workers.values()), ("companies", self.companies.values()), ("countries", self.countries.values()), ("markets", self.markets.values())):
            vals = [v.wallet.value() for v in values]
            if vals:
                wallet_rows.append((name, short_number(min(vals)), short_number(sum(vals) / len(vals)), short_number(max(vals)), sparkline(vals[:32])))
        parts.append(render_table(wallet_rows, ["Group", "Min", "Mean", "Max", "Spark"], "WALLET VALUE SUMMARY", [12, 10, 10, 10, 24]))

        # trade sparkline by top markets
        top_markets = sorted(self.markets.values(), key=lambda m: m.volume, reverse=True)[:10]
        trade_rows = []
        for m in top_markets:
            series = [m.volume, m.trade_count * 10.0, m.market_trade_count * 100.0, float(len(m.listed_product_ids) + len(m.listed_market_ids))]
            trade_rows.append((m.name[:20], m.domain, short_number(m.volume), sparkline(series)))
        parts.append(render_table(trade_rows, ["Market", "Domain", "Volume", "Spark"], "TOP MARKET MICRO-SHAPES", [20, 14, 10, 20]))

        return "\n\n".join(parts)

    def build_report(self) -> str:
        return (f"Built: countries={len(self.countries)}, alliances={len(self.alliances)}, companies={len(self.companies)}, "
                f"workers={len(self.workers)}, products={len(self.products)}, markets={len(self.markets)}, market_rights_exchanges={len(self.market_rights_exchanges)}")

    def tick_report(self) -> str:
        return f"tick={self.tick} volume={sum(m.volume for m in self.markets.values()):,.1f}H market_trades={self.market_ownership_changes} manual_lifts={self.manual_lifts}"

    def level_distribution(self, values: Iterable[HierarchyEntity]) -> Dict[int, int]:
        c = Counter(v.level for v in values)
        return dict(sorted(c.items()))

    def top(self, values: Iterable[AccountEntity], n: int = 8) -> List[AccountEntity]:
        return sorted(values, key=lambda e: e.status_number(self.privileges, self.burdens), reverse=True)[:n]

    def summary_entity(self, e: AccountEntity) -> Dict[str, Any]:
        return {"name": e.name, "kind": e.kind, "level": e.level, "level_name": LEVEL_NAMES[e.level], "domain": e.domain, "scope": e.scope, "owner": self.entities[e.owner_id].name if isinstance(e, TradableEntity) and e.owner_id in self.entities else None, "status_number": round(e.status_number(self.privileges, self.burdens), 2), "wallet": round(e.wallet.value(), 2)}

    def report(self) -> Dict[str, Any]:
        top_worker_pool = self.workers.values()
        if len(self.workers) > 12000:
            top_worker_pool = [self.workers[wid] for wid in self.rng.sample(list(self.workers.keys()), 12000)]
        recent = []
        for m in sorted(self.markets.values(), key=lambda x: len(x.recent), reverse=True)[:12]:
            for item in m.recent[-2:]:
                recent.append(f"{m.name}: {item}")
        return {
            "seed": self.seed,
            "profile": self.profile,
            "ticks": self.tick,
            "counts": {"entities": len(self.entities), "countries": len(self.countries), "alliances": len(self.alliances), "companies": len(self.companies), "workers": len(self.workers), "products": len(self.products), "markets": len(self.markets), "market_rights_exchanges": len(self.market_rights_exchanges), "privileges": len(self.privileges), "burdens": len(self.burdens)},
            "trade": {"volume_H": round(sum(m.volume for m in self.markets.values()), 2), "market_ownership_changes": self.market_ownership_changes, "market_asset_trades": sum(m.market_trade_count for m in self.markets.values()), "product_sales": sum(p.units_sold for p in self.products.values())},
            "level_distributions": {"workers": self.level_distribution(self.workers.values()), "companies": self.level_distribution(self.companies.values()), "countries": self.level_distribution(self.countries.values()), "markets": self.level_distribution(self.markets.values()), "products": self.level_distribution(self.products.values())},
            "top_countries": [self.summary_entity(e) for e in self.top(self.countries.values())],
            "top_companies": [self.summary_entity(e) for e in self.top(self.companies.values())],
            "top_markets": [self.summary_entity(e) for e in self.top(self.markets.values())],
            "top_workers": [self.summary_entity(e) for e in self.top(top_worker_pool)],
            "recent_trades": recent[:20],
        }

    def print_report(self, json_path: Optional[str] = None, include_visuals: bool = True) -> None:
        report = self.report()
        if json_path:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
        print("=" * 78)
        print("SOLAR HIERARCHY MARKET ECONOMY REPORT")
        print("=" * 78)
        print(f"seed={report['seed']} profile={report['profile']} ticks={report['ticks']}")
        print("Counts:")
        for k, v in report["counts"].items(): print(f"  {k:28s} {v}")
        print("Trade:")
        for k, v in report["trade"].items(): print(f"  {k:28s} {v}")
        print("Level distributions:")
        for k, v in report["level_distributions"].items(): print(f"  {k:12s} {v}")
        for title, key in [("Top countries", "top_countries"), ("Top companies", "top_companies"), ("Top markets", "top_markets"), ("Top workers", "top_workers")]:
            print("\n" + title)
            for e in report[key]:
                print(f"  L{e['level']:02d} {e['level_name']:<16s} {e['name'][:48]:<48s} {e['status_number']:>12,.1f}H domain={e['domain']} owner={e['owner']}")
        print("\nRecent trades")
        for t in report["recent_trades"][:15]: print("  - " + t)
        if include_visuals:
            print("\n" + chart_title("UTF-8 VISUAL HIERARCHY DASHBOARD", 78, "#"))
            print(self.visual_report())


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Solar hierarchy-currency market simulation")
    p.add_argument("--profile", choices=sorted(SCALE_CONFIGS), default="large")
    p.add_argument("--ticks", type=int, default=3)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--json", default=None, help="optional JSON report output path")
    p.add_argument("--no-visuals", action="store_true", help="disable UTF-8 charts and diagrams")
    return p.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    sim = SolarHierarchyMarketSimulation(profile=args.profile, seed=args.seed, quiet=args.quiet)
    sim.build()
    sim.simulate(max(0, args.ticks))
    sim.print_report(args.json, include_visuals=not args.no_visuals)
    sys.stdout.flush(); sys.stderr.flush()
    return 0


if __name__ == "__main__":
    code = main(sys.argv[1:])
    os._exit(code)
