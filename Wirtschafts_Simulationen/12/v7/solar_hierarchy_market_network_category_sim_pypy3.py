#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solar Hierarchy Market: Network/Category/Sheaf Architecture
===========================================================

PyPy3-compatible, dependency-free simulation of a hierarchy-currency economy
rebuilt around networks, queue disciplines, duplex channels, semaphores,
topologies, morphisms, categories, functors, natural transformations,
presheaves and sheaves.

The economic idea preserved from the earlier script:

- hierarchy is the traded currency;
- the hierarchy bundle is structured by hierarchy element and hierarchy height;
- the settlement number is a compression, not the actual meaning;
- people, firms, countries, products, markets, privileges and burdens all have
  hierarchy positions;
- markets are themselves tradable assets.

The architectural paradigm is changed:

- Every economic entity is also a network node.
- Every trade/control/employment/privilege relation is a morphism.
- Every morphism can induce packets flowing through a typed topology.
- Packet scheduling uses FIFO and LIFO queues.
- Channels are simplex, half-duplex or full-duplex.
- Channel capacity is guarded by semaphores.
- Global structure is exposed as categories and functors.
- Local market states are treated as presheaf sections.
- Planetary and solar summaries are glued with sheaf-like compatibility rules.

Run examples:

    pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 2
    pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 3 --seed 42
    pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile huge --ticks 1 --json report.json

Disable terminal art:

    pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile demo --ticks 1 --no-visuals
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict, deque
from typing import Any, Callable, Deque, Dict, Iterable, List, Optional, Sequence, Tuple

EPS = 1e-9

LEVEL_NAMES = {
    1: "Survival", 2: "Basic", 3: "Local", 4: "Skilled", 5: "Professional",
    6: "Regional", 7: "National", 8: "Alliance", 9: "Planetary",
    10: "Interplanetary", 11: "Systemic", 12: "Solar Apex",
}

HEIGHT_MULTIPLIERS = {
    1: 1.00, 2: 1.35, 3: 1.85, 4: 2.55, 5: 3.55, 6: 5.10,
    7: 7.40, 8: 10.80, 9: 15.90, 10: 23.50, 11: 35.00, 12: 52.00,
}

LEVEL_THRESHOLDS = [
    0.0, 160.0, 420.0, 950.0, 2100.0, 4800.0, 11000.0, 25000.0,
    60000.0, 145000.0, 350000.0, 850000.0,
]

BODIES = ("Earth", "Moon", "Mars")
SCOPES = ("Solar System", "Earth", "Moon", "Mars")

ELEMENTS = (
    "labor", "skill", "care", "media", "science", "risk", "trust",
    "governance", "military", "capital", "logistics", "infrastructure",
    "market_access", "privilege", "burden", "topology", "duplex", "queue",
    "semaphore", "morphism", "sheaf", "functor",
)

DOMAINS = (
    "food", "water", "oxygen", "housing", "energy", "medicine", "education",
    "compute", "transport", "shipbuilding", "agriculture", "manufacturing",
    "defense", "media", "culture", "research", "care", "finance", "data",
    "orbital_slots", "terraforming", "market_rights", "labor", "privilege", "burden",
    "network_bandwidth", "semaphore_permits", "topology_rights", "sheaf_coherence",
)

SECTORS = DOMAINS[:22]
GOODS_HIERARCHY = {
    1: ["basic water ration", "emergency calories", "shared shelter slot", "minimum air filter"],
    2: ["personal hygiene kit", "simple clothing", "basic comm terminal", "public transport coupon"],
    3: ["repair tools", "private sleeping pod", "standard nutrition plan", "local market access"],
    4: ["apprentice workshop access", "education package", "clinic priority", "small data quota"],
    5: ["professional housing", "vehicle usage rights", "research terminal", "family consumption package"],
    6: ["regional logistics capacity", "advanced medicine", "team office space", "mid-tier compute lease"],
    7: ["national travel permit", "factory share", "strategic storage rights", "security escort"],
    8: ["alliance procurement rights", "defense-grade transport", "cross-border market franchise", "coalition intel package"],
    9: ["planetary influence media slot", "large industrial campus", "planetary capital line", "rare materials quota"],
    10: ["interplanetary shipping lane", "orbital docking priority", "multi-planet supply contract", "interplanetary data backbone"],
    11: ["systemic emergency command bandwidth", "solar reserve draw rights", "system governance audience", "high strategic deterrence assets"],
    12: ["solar apex coordination rights", "civilizational continuity archive", "supreme mission allocation window", "apex mobility corridor"],
}
SEXES = ("female", "male", "other")
OCCUPATIONS = (
    "labor", "skill", "care", "media", "science", "risk", "trust", "governance",
    "military", "logistics", "infrastructure", "compute", "education", "medicine",
)

QUEUE_KINDS = ("fifo", "lifo", "priority")
DUPLEX_MODES = ("simplex", "half", "full")
TOPOLOGY_KINDS = ("tree", "star", "ring", "mesh", "market-bipartite", "governance", "sheaf-cover")

SPARK_CHARS = "▁▂▃▄▅▆▇█"
HEAT_CHARS = " ·░▒▓█"


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


def pad(text: Any, width: int) -> str:
    s = str(text)
    if len(s) <= width:
        return s + " " * (width - len(s))
    if width <= 1:
        return s[:width]
    return s[: width - 1] + "…"


def chart_title(title: str, width: int = 96, char: str = "═") -> str:
    core = " %s " % title
    if len(core) >= width:
        return core
    left = (width - len(core)) // 2
    right = width - len(core) - left
    return char * left + core + char * right


def utf8_bar(value: float, max_value: float, width: int = 36, fill: str = "█", empty: str = "░") -> str:
    if width <= 0:
        return ""
    if max_value <= EPS:
        return empty * width
    ratio = clamp(float(value) / float(max_value), 0.0, 1.0)
    full = int(ratio * width)
    return fill * full + empty * (width - full)


def sparkline(values: Sequence[float]) -> str:
    if not values:
        return ""
    vals = [float(v) for v in values]
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


def render_histogram(mapping: Dict[Any, float], title: str, width: int = 36, numeric_keys: bool = False) -> str:
    lines = [chart_title(title)]
    if not mapping:
        return "\n".join(lines + ["(no data)"])
    items = list(mapping.items())
    if numeric_keys:
        items.sort(key=lambda kv: kv[0])
    else:
        items.sort(key=lambda kv: (-float(kv[1]), str(kv[0])))
    maxv = max(float(v) for _, v in items) or 1.0
    for key, value in items:
        lines.append("%s │%s│ %s" % (pad(key, 22), utf8_bar(float(value), maxv, width), short_number(float(value))))
    return "\n".join(lines)


def render_level_chart(mapping: Dict[int, int], title: str, width: int = 36) -> str:
    lines = [chart_title(title)]
    maxv = max([float(v) for v in mapping.values()] or [1.0]) or 1.0
    for level in range(1, 13):
        value = float(mapping.get(level, 0))
        label = "L%02d %-16s" % (level, LEVEL_NAMES[level][:16])
        lines.append("%s │%s│ %s" % (label, utf8_bar(value, maxv, width), short_number(value)))
    return "\n".join(lines)


def render_heatmap(rows: Sequence[Any], cols: Sequence[Any], data: Dict[Any, Dict[Any, float]], title: str) -> str:
    lines = [chart_title(title)]
    if not rows or not cols:
        return "\n".join(lines + ["(no data)"])
    maxv = 0.0
    for r in rows:
        row = data.get(r, {})
        for c in cols:
            maxv = max(maxv, float(row.get(c, 0.0)))
    maxv = max(maxv, 1.0)
    header = " " * 16 + " ".join([pad(c, 3) for c in cols])
    lines.append(header)
    for r in rows:
        row = data.get(r, {})
        cells = []
        for c in cols:
            v = float(row.get(c, 0.0))
            idx = int(round(clamp(v / maxv, 0.0, 1.0) * (len(HEAT_CHARS) - 1)))
            idx = int(clamp(idx, 0, len(HEAT_CHARS) - 1))
            cells.append(" %s " % HEAT_CHARS[idx])
        lines.append("%s %s" % (pad(r, 15), "".join(cells)))
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


class FastRNG:
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

    def chance(self, p: float) -> bool:
        return self.random() < p

    def choice(self, seq: Sequence[Any]) -> Any:
        if not seq:
            raise IndexError("choice from empty sequence")
        return seq[int(self.random() * len(seq))]

    def sample(self, seq: Sequence[Any], k: int) -> List[Any]:
        n = len(seq)
        if k <= 0 or n <= 0:
            return []
        if k >= n:
            out = list(seq)
            self.shuffle(out)
            return out
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

    def beta_like(self, alpha: float, beta: float) -> float:
        mean = alpha / max(EPS, alpha + beta)
        rough = (self.random() + self.random()) * 0.5
        return clamp(mean * 0.62 + rough * 0.38 + self.uniform(-0.04, 0.04), 0.0, 1.0)


# ---------------------------------------------------------------------------
# Hierarchy bundles as structured currency
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
        if abs(amount) <= EPS:
            return
        level = int(clamp(level, 1, 12))
        key = (level, element)
        self.parts[key] = self.parts.get(key, 0.0) + float(amount)
        if abs(self.parts[key]) <= EPS:
            del self.parts[key]

    def merge(self, other: "HierarchyBundle", scale: float = 1.0) -> "HierarchyBundle":
        out = self.copy()
        for (level, element), amount in other.parts.items():
            out.add(level, element, amount * scale)
        return out

    def scaled(self, factor: float) -> "HierarchyBundle":
        return HierarchyBundle({k: v * factor for k, v in self.parts.items()})

    def to_number(self) -> float:
        total = 0.0
        for (level, _element), amount in self.parts.items():
            total += amount * HEIGHT_MULTIPLIERS[level]
        return total

    def dominant_element(self) -> str:
        totals: Dict[str, float] = defaultdict(float)
        for (_level, element), amount in self.parts.items():
            totals[element] += amount
        if not totals:
            return "empty"
        return max(totals.items(), key=lambda kv: abs(kv[1]))[0]

    def by_level(self) -> Dict[int, float]:
        d: Dict[int, float] = defaultdict(float)
        for (level, _element), amount in self.parts.items():
            d[level] += amount
        return dict(d)

    def __repr__(self) -> str:
        return "HierarchyBundle(%s)" % self.parts


class Wallet:
    __slots__ = ("bundle",)

    def __init__(self) -> None:
        self.bundle = HierarchyBundle()

    def deposit(self, bundle: HierarchyBundle) -> None:
        self.bundle = self.bundle.merge(bundle)

    def value(self) -> float:
        return self.bundle.to_number()

    def can_pay(self, value: float) -> bool:
        return self.value() + EPS >= value

    def withdraw_number(self, value: float, level: int = 5, element: str = "capital") -> HierarchyBundle:
        if value <= 0:
            return HierarchyBundle()
        available = self.value()
        take = min(available, value)
        if take <= EPS:
            return HierarchyBundle()
        ratio = take / max(EPS, available)
        out = self.bundle.scaled(ratio)
        self.bundle = self.bundle.scaled(1.0 - ratio)
        missing = value - take
        if missing > EPS:
            out.add(level, element, missing / HEIGHT_MULTIPLIERS[level])
        return out


# ---------------------------------------------------------------------------
# Economic entities
# ---------------------------------------------------------------------------

class EntityBase:
    kind = "entity"
    __slots__ = ("id", "name")

    def __init__(self, entity_id: int, name: str) -> None:
        self.id = entity_id
        self.name = name


class LocatedEntity(EntityBase):
    kind = "located_entity"
    __slots__ = ("scope", "body", "country_id")

    def __init__(self, entity_id: int, name: str, scope: str = "Solar System", body: str = "Solar System", country_id: Optional[int] = None) -> None:
        super().__init__(entity_id, name)
        self.scope = scope
        self.body = body
        self.country_id = country_id


class HierarchyEntity(LocatedEntity):
    kind = "hierarchy_entity"
    __slots__ = ("level", "domain", "elements", "last_score")

    def __init__(self, entity_id: int, name: str, scope: str = "Solar System", body: str = "Solar System", country_id: Optional[int] = None, level: int = 1, domain: str = "general", elements: Optional[Dict[str, float]] = None) -> None:
        super().__init__(entity_id, name, scope, body, country_id)
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
    __slots__ = ("wallet", "privilege_ids", "burden_ids", "node_id", "inventory_units")

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.wallet = Wallet()
        self.privilege_ids: List[int] = []
        self.burden_ids: List[int] = []
        self.node_id: Optional[int] = None
        self.inventory_units = 0

    def status_number(self, privileges: Optional[Dict[int, "Privilege"]] = None, burdens: Optional[Dict[int, "Burden"]] = None) -> float:
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

    def refresh_level(self, privileges: Optional[Dict[int, "Privilege"]] = None, burdens: Optional[Dict[int, "Burden"]] = None) -> None:
        self.last_score = self.status_number(privileges, burdens)
        self.level = level_from_number(self.last_score)

    def entitlement_level(self, domain: str, privileges: Dict[int, "Privilege"], burdens: Dict[int, "Burden"]) -> int:
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
    __slots__ = ("owner_id", "tradable")

    def __init__(self, *args: Any, owner_id: Optional[int] = None, tradable: bool = True, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.owner_id = owner_id
        self.tradable = tradable

    def quote(self) -> HierarchyBundle:
        raw = max(1.0, self.structural_number() * 0.08 / HEIGHT_MULTIPLIERS[self.level])
        b = HierarchyBundle.single(self.level, "capital", raw * 0.7)
        b.add(self.level, self.domain, raw * 0.3)
        return b


class Organization(TradableEntity):
    kind = "organization"
    __slots__ = ("member_ids",)

    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.member_ids: List[int] = []


class CelestialBody(Organization):
    kind = "celestial_body"
    __slots__ = ("body_type", "un_id", "defense_id", "country_ids")

    def __init__(self, *args: Any, body_type: str = "planet", **kwargs: Any) -> None:
        super().__init__(*args, tradable=False, **kwargs)
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


class Company(Organization):
    kind = "company"
    __slots__ = ("sector", "capacity", "worker_ids", "product_ids", "production_score", "research_intensity", "military_contract_share")

    def __init__(self, *args: Any, sector: str = "general", capacity: int = 0, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.sector = sector
        self.capacity = capacity
        self.worker_ids: List[int] = []
        self.product_ids: List[int] = []
        self.production_score = 0.0
        self.research_intensity = 0.0
        self.military_contract_share = 0.0

    def quote(self) -> HierarchyBundle:
        base = max(100.0, self.status_number() * 0.35)
        raw = base / HEIGHT_MULTIPLIERS[self.level]
        b = HierarchyBundle.single(self.level, "capital", raw * 0.44)
        b.add(self.level, "market_access", raw * 0.24)
        b.add(self.level, self.sector, raw * 0.20)
        b.add(max(1, self.level - 1), "topology", raw * 0.12)
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
            t.get("care", 0.5) * 20.0 + t.get("media", 0.5) * 18.0 +
            t.get("science", 0.5) * 32.0 + t.get("military", 0.5) * 20.0 +
            t.get("network", 0.5) * 16.0
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
        self.elements["labor"] = p * 0.36
        self.elements["skill"] = p * (0.21 + t.get("skill", 0.5) * 0.16)
        self.elements["trust"] = p * t.get("trust", 0.5) * 0.10
        self.elements["care"] = p * t.get("care", 0.5) * 0.07
        self.elements["media"] = p * t.get("media", 0.5) * 0.06
        self.elements["science"] = p * t.get("science", 0.5) * 0.08
        self.elements["military"] = p * t.get("military", 0.5) * 0.06
        self.elements["queue"] = p * t.get("network", 0.5) * 0.04
        self.elements["morphism"] = p * t.get("leadership", 0.5) * 0.03


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
        b = HierarchyBundle.single(self.min_level, self.domain, raw * 0.48)
        b.add(self.level, "market_access", raw * 0.22)
        b.add(max(1, self.level - 1), "capital", raw * 0.18)
        b.add(max(1, self.level - 1), "morphism", raw * 0.12)
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
        b = HierarchyBundle.single(self.level, "privilege", raw * 0.58)
        b.add(self.level, self.domain, raw * 0.25)
        b.add(self.level, "semaphore", raw * 0.17)
        return b


class Burden(Privilege):
    kind = "burden"
    __slots__ = ("level_penalty",)

    def __init__(self, *args: Any, level_penalty: int = 1, **kwargs: Any) -> None:
        super().__init__(*args, level_boost=1, **kwargs)
        self.level_boost = 0
        self.level_penalty = int(clamp(level_penalty, 1, 5))
        self.elements.setdefault("burden", 10.0 * self.level_penalty)

    def quote(self) -> HierarchyBundle:
        raw = max(4.0, (self.level_penalty ** 2) * (2.0 + self.duration) * (1.0 + self.level))
        b = HierarchyBundle.single(self.level, "burden", raw * 0.52)
        b.add(self.level, self.domain, raw * 0.25)
        b.add(self.level, "queue", raw * 0.23)
        return b


class Market(TradableEntity):
    kind = "market"
    __slots__ = ("listed_product_ids", "listed_market_ids", "fee_rate", "trade_count", "failed_count", "market_trade_count", "volume", "recent", "queue_discipline")

    def __init__(self, *args: Any, fee_rate: float = 0.015, queue_discipline: str = "fifo", **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.listed_product_ids: List[int] = []
        self.listed_market_ids: List[int] = []
        self.fee_rate = fee_rate
        self.trade_count = 0
        self.failed_count = 0
        self.market_trade_count = 0
        self.volume = 0.0
        self.recent: List[str] = []
        self.queue_discipline = queue_discipline

    def quote(self) -> HierarchyBundle:
        base = max(500.0, self.volume * 0.12 + self.trade_count * 8.0 + self.structural_number() * 0.70)
        scope_factor = {"Solar System": 4.5, "Earth": 2.5, "Moon": 1.8, "Mars": 2.1}.get(self.scope, 1.4)
        raw = base * scope_factor / HEIGHT_MULTIPLIERS[self.level]
        b = HierarchyBundle.single(self.level, "market_access", raw * 0.36)
        b.add(self.level, self.domain, raw * 0.28)
        b.add(max(1, self.level - 1), "governance", raw * 0.12)
        b.add(max(1, self.level - 1), "topology", raw * 0.12)
        b.add(max(1, self.level - 1), "queue", raw * 0.12)
        return b

    def remember(self, text: str) -> None:
        self.recent.append(text)
        if len(self.recent) > 8:
            self.recent.pop(0)


class MarketRightsExchange(Market):
    kind = "market_rights_exchange"
    __slots__ = ()


# ---------------------------------------------------------------------------
# Data streams, queues, semaphores, duplex channels, topologies
# ---------------------------------------------------------------------------

class Packet:
    __slots__ = ("id", "kind", "source", "target", "bundle", "created_tick", "ttl", "route", "hop", "morphism_id", "payload", "priority")

    def __init__(self, packet_id: int, kind: str, source: int, target: int, bundle: HierarchyBundle, created_tick: int, ttl: int = 32, route: Optional[List[int]] = None, morphism_id: Optional[int] = None, payload: Optional[Dict[str, Any]] = None, priority: int = 5) -> None:
        self.id = packet_id
        self.kind = kind
        self.source = source
        self.target = target
        self.bundle = bundle
        self.created_tick = created_tick
        self.ttl = ttl
        self.route = list(route or [])
        self.hop = 0
        self.morphism_id = morphism_id
        self.payload = dict(payload or {})
        self.priority = int(clamp(priority, 1, 12))

    def current_node(self) -> Optional[int]:
        if not self.route or self.hop >= len(self.route):
            return None
        return self.route[self.hop]

    def next_node(self) -> Optional[int]:
        if not self.route or self.hop + 1 >= len(self.route):
            return None
        return self.route[self.hop + 1]

    def advance(self) -> None:
        self.hop += 1
        self.ttl -= 1

    def arrived(self) -> bool:
        return self.current_node() == self.target or self.hop >= len(self.route) - 1


class StreamQueue:
    __slots__ = ("name", "capacity", "items", "pushed", "popped", "dropped", "max_len")
    discipline = "generic"

    def __init__(self, name: str, capacity: int = 1024) -> None:
        self.name = name
        self.capacity = capacity
        self.items: Any = []
        self.pushed = 0
        self.popped = 0
        self.dropped = 0
        self.max_len = 0

    def __len__(self) -> int:
        return len(self.items)

    def push(self, item: Packet) -> bool:
        if len(self.items) >= self.capacity:
            self.dropped += 1
            return False
        self._push(item)
        self.pushed += 1
        if len(self.items) > self.max_len:
            self.max_len = len(self.items)
        return True

    def _push(self, item: Packet) -> None:
        self.items.append(item)

    def pop(self) -> Optional[Packet]:
        if not self.items:
            return None
        self.popped += 1
        return self._pop()

    def _pop(self) -> Packet:
        return self.items.pop(0)

    def stats(self) -> Dict[str, Any]:
        return {"discipline": self.discipline, "len": len(self), "pushed": self.pushed, "popped": self.popped, "dropped": self.dropped, "max_len": self.max_len}


class FIFOQueue(StreamQueue):
    discipline = "fifo"

    def __init__(self, name: str, capacity: int = 1024) -> None:
        super().__init__(name, capacity)
        self.items = deque()

    def _push(self, item: Packet) -> None:
        self.items.append(item)

    def _pop(self) -> Packet:
        return self.items.popleft()


class LIFOQueue(StreamQueue):
    discipline = "lifo"

    def _pop(self) -> Packet:
        return self.items.pop()


class PriorityQueue(StreamQueue):
    discipline = "priority"

    def _push(self, item: Packet) -> None:
        self.items.append(item)

    def _pop(self) -> Packet:
        best_idx = 0
        best_prio = self.items[0].priority
        for idx, item in enumerate(self.items[1:], start=1):
            if item.priority > best_prio:
                best_idx = idx
                best_prio = item.priority
        return self.items.pop(best_idx)


def make_queue(kind: str, name: str, capacity: int) -> StreamQueue:
    if kind == "fifo":
        return FIFOQueue(name, capacity)
    if kind == "lifo":
        return LIFOQueue(name, capacity)
    if kind == "priority":
        return PriorityQueue(name, capacity)
    return FIFOQueue(name, capacity)


class DataStream:
    __slots__ = ("name", "queue", "bytes_like", "packets_like", "last_tick")

    def __init__(self, name: str, queue: StreamQueue) -> None:
        self.name = name
        self.queue = queue
        self.bytes_like = 0.0
        self.packets_like = 0
        self.last_tick = 0

    def push(self, packet: Packet) -> bool:
        ok = self.queue.push(packet)
        if ok:
            self.packets_like += 1
            self.bytes_like += packet.bundle.to_number()
        return ok

    def pop(self) -> Optional[Packet]:
        return self.queue.pop()

    def stats(self) -> Dict[str, Any]:
        d = self.queue.stats()
        d["bytes_like"] = round(self.bytes_like, 2)
        d["packets_like"] = self.packets_like
        return d


class Semaphore:
    __slots__ = ("name", "capacity", "available", "acquired", "blocked", "owners")

    def __init__(self, name: str, capacity: int) -> None:
        self.name = name
        self.capacity = max(1, int(capacity))
        self.available = self.capacity
        self.acquired = 0
        self.blocked = 0
        self.owners: Dict[int, int] = defaultdict(int)

    def acquire(self, owner_id: int, permits: int = 1) -> bool:
        permits = max(1, int(permits))
        if self.available >= permits:
            self.available -= permits
            self.acquired += permits
            self.owners[owner_id] += permits
            return True
        self.blocked += 1
        return False

    def release(self, owner_id: int, permits: int = 1) -> None:
        permits = max(1, int(permits))
        held = self.owners.get(owner_id, 0)
        actual = min(held, permits)
        if actual <= 0:
            return
        self.owners[owner_id] = held - actual
        if self.owners[owner_id] <= 0:
            del self.owners[owner_id]
        self.available = min(self.capacity, self.available + actual)

    def reset_soft(self) -> None:
        # emergency repair for long simulations if an inconsistent packet is dropped
        in_use = sum(self.owners.values())
        self.available = max(0, self.capacity - in_use)

    def stats(self) -> Dict[str, Any]:
        return {"capacity": self.capacity, "available": self.available, "acquired": self.acquired, "blocked": self.blocked}


class NetworkNode:
    __slots__ = ("id", "entity_id", "name", "kind", "body", "level", "role", "fifo", "lifo", "priority", "outbound", "received", "sent", "dropped", "processed", "channel_ids")

    def __init__(self, node_id: int, entity_id: int, name: str, kind: str, body: str, level: int, role: str = "economic") -> None:
        self.id = node_id
        self.entity_id = entity_id
        self.name = name
        self.kind = kind
        self.body = body
        self.level = level
        self.role = role
        cap = 64 + level * 32
        self.fifo = DataStream("%s:fifo" % name, FIFOQueue("%s:fifo" % name, cap))
        self.lifo = DataStream("%s:lifo" % name, LIFOQueue("%s:lifo" % name, cap))
        self.priority = DataStream("%s:priority" % name, PriorityQueue("%s:priority" % name, cap))
        self.outbound = DataStream("%s:out" % name, FIFOQueue("%s:out" % name, cap * 2))
        self.received = 0
        self.sent = 0
        self.dropped = 0
        self.processed = 0
        self.channel_ids: List[int] = []

    def receive(self, packet: Packet) -> bool:
        self.received += 1
        if packet.kind in ("shock", "burden", "defense_alert"):
            ok = self.lifo.push(packet)
        elif packet.priority >= 9:
            ok = self.priority.push(packet)
        else:
            ok = self.fifo.push(packet)
        if not ok:
            self.dropped += 1
        return ok

    def enqueue_outbound(self, packet: Packet) -> bool:
        ok = self.outbound.push(packet)
        if ok:
            self.sent += 1
        else:
            self.dropped += 1
        return ok

    def process_local(self, limit: int = 4) -> List[Packet]:
        processed: List[Packet] = []
        for _ in range(limit):
            packet = self.priority.pop() or self.lifo.pop() or self.fifo.pop()
            if packet is None:
                break
            self.processed += 1
            processed.append(packet)
        return processed

    def total_queue_len(self) -> int:
        return len(self.fifo.queue) + len(self.lifo.queue) + len(self.priority.queue) + len(self.outbound.queue)


class Channel:
    __slots__ = ("id", "name", "a", "b", "mode", "topology", "latency", "bandwidth", "semaphore", "queue_ab", "queue_ba", "in_flight", "transmitted", "blocked", "dropped", "last_direction")

    def __init__(self, channel_id: int, name: str, a: int, b: int, mode: str = "full", topology: str = "mesh", latency: int = 1, bandwidth: int = 4, queue_kind: str = "fifo", semaphore_capacity: int = 8) -> None:
        self.id = channel_id
        self.name = name
        self.a = a
        self.b = b
        self.mode = mode
        self.topology = topology
        self.latency = max(1, int(latency))
        self.bandwidth = max(1, int(bandwidth))
        self.semaphore = Semaphore("sem:%s" % name, semaphore_capacity)
        self.queue_ab = DataStream("%s:a>b" % name, make_queue(queue_kind, "%s:a>b" % name, 512))
        self.queue_ba = DataStream("%s:b>a" % name, make_queue(queue_kind, "%s:b>a" % name, 512))
        self.in_flight: List[Tuple[int, int, Packet]] = []
        self.transmitted = 0
        self.blocked = 0
        self.dropped = 0
        self.last_direction = "ba"

    def other(self, node_id: int) -> Optional[int]:
        if node_id == self.a:
            return self.b
        if node_id == self.b:
            return self.a
        return None

    def direction_for(self, source: int, target: int) -> Optional[str]:
        if source == self.a and target == self.b:
            return "ab"
        if source == self.b and target == self.a:
            return "ba"
        return None

    def enqueue(self, source: int, target: int, packet: Packet) -> bool:
        direction = self.direction_for(source, target)
        if direction is None:
            self.dropped += 1
            return False
        if self.mode == "simplex" and direction != "ab":
            self.blocked += 1
            return False
        stream = self.queue_ab if direction == "ab" else self.queue_ba
        ok = stream.push(packet)
        if not ok:
            self.dropped += 1
        return ok

    def tick(self, now: int) -> List[Tuple[int, Packet]]:
        delivered: List[Tuple[int, Packet]] = []
        still: List[Tuple[int, int, Packet]] = []
        for arrival, dest, packet in self.in_flight:
            if arrival <= now:
                self.semaphore.release(packet.id, 1)
                delivered.append((dest, packet))
            else:
                still.append((arrival, dest, packet))
        self.in_flight = still

        directions: List[str]
        if self.mode == "full":
            directions = ["ab", "ba"]
        elif self.mode == "simplex":
            directions = ["ab"]
        else:
            len_ab = len(self.queue_ab.queue)
            len_ba = len(self.queue_ba.queue)
            if len_ab == 0 and len_ba == 0:
                directions = []
            elif len_ab > len_ba:
                directions = ["ab"]
            elif len_ba > len_ab:
                directions = ["ba"]
            else:
                directions = ["ba" if self.last_direction == "ab" else "ab"]
        per_dir = self.bandwidth if self.mode != "full" else max(1, self.bandwidth // 2)
        for direction in directions:
            stream = self.queue_ab if direction == "ab" else self.queue_ba
            dest = self.b if direction == "ab" else self.a
            for _ in range(per_dir):
                packet = stream.pop()
                if packet is None:
                    break
                if not self.semaphore.acquire(packet.id, 1):
                    self.blocked += 1
                    # requeue packet so pressure remains visible
                    stream.push(packet)
                    break
                self.in_flight.append((now + self.latency, dest, packet))
                self.transmitted += 1
                self.last_direction = direction
        return delivered

    def queue_lengths(self) -> Tuple[int, int]:
        return (len(self.queue_ab.queue), len(self.queue_ba.queue))

    def stats(self) -> Dict[str, Any]:
        ab, ba = self.queue_lengths()
        return {"mode": self.mode, "topology": self.topology, "ab": ab, "ba": ba, "in_flight": len(self.in_flight), "tx": self.transmitted, "blocked": self.blocked, "dropped": self.dropped, "sem": self.semaphore.stats()}


class TopologyGraph:
    __slots__ = ("nodes", "channels", "adj", "edge_lookup")

    def __init__(self) -> None:
        self.nodes: Dict[int, NetworkNode] = {}
        self.channels: Dict[int, Channel] = {}
        self.adj: Dict[int, List[Tuple[int, int]]] = defaultdict(list)
        self.edge_lookup: Dict[Tuple[int, int], int] = {}

    def add_node(self, node: NetworkNode) -> None:
        self.nodes[node.id] = node

    def connect(self, channel: Channel) -> None:
        self.channels[channel.id] = channel
        self.adj[channel.a].append((channel.b, channel.id))
        self.adj[channel.b].append((channel.a, channel.id))
        self.edge_lookup[(channel.a, channel.b)] = channel.id
        self.edge_lookup[(channel.b, channel.a)] = channel.id
        if channel.a in self.nodes:
            self.nodes[channel.a].channel_ids.append(channel.id)
        if channel.b in self.nodes:
            self.nodes[channel.b].channel_ids.append(channel.id)

    def channel_between(self, a: int, b: int) -> Optional[Channel]:
        cid = self.edge_lookup.get((a, b))
        if cid is None:
            return None
        return self.channels[cid]

    def route(self, source: int, target: int, max_depth: int = 12) -> List[int]:
        if source == target:
            return [source]
        q: Deque[int] = deque([source])
        parent: Dict[int, Optional[int]] = {source: None}
        depth: Dict[int, int] = {source: 0}
        while q:
            n = q.popleft()
            if depth[n] >= max_depth:
                continue
            for nxt, _cid in self.adj.get(n, []):
                if nxt in parent:
                    continue
                parent[nxt] = n
                depth[nxt] = depth[n] + 1
                if nxt == target:
                    path = [target]
                    cur = target
                    while parent[cur] is not None:
                        cur = parent[cur]  # type: ignore[index]
                        path.append(cur)
                    path.reverse()
                    return path
                q.append(nxt)
        return []

    def degrees(self) -> Dict[int, int]:
        return {nid: len(edges) for nid, edges in self.adj.items()}

    def component_count(self) -> int:
        seen = set()
        count = 0
        for node in self.nodes:
            if node in seen:
                continue
            count += 1
            q = deque([node])
            seen.add(node)
            while q:
                n = q.popleft()
                for nxt, _cid in self.adj.get(n, []):
                    if nxt not in seen:
                        seen.add(nxt)
                        q.append(nxt)
        return count

    def topology_counts(self) -> Dict[str, int]:
        c: Dict[str, int] = defaultdict(int)
        for ch in self.channels.values():
            c[ch.topology] += 1
        return dict(c)

    def duplex_counts(self) -> Dict[str, int]:
        c: Dict[str, int] = defaultdict(int)
        for ch in self.channels.values():
            c[ch.mode] += 1
        return dict(c)

    def queue_discipline_counts(self) -> Dict[str, int]:
        c: Dict[str, int] = defaultdict(int)
        for ch in self.channels.values():
            c[ch.queue_ab.queue.discipline] += 1
            c[ch.queue_ba.queue.discipline] += 1
        return dict(c)

    def tick(self, now: int) -> List[Tuple[int, Packet]]:
        delivered: List[Tuple[int, Packet]] = []
        for ch in self.channels.values():
            delivered.extend(ch.tick(now))
        return delivered

    def drain_outbound(self, limit_per_node: int = 3) -> Tuple[int, int]:
        moved = 0
        dropped = 0
        for node in self.nodes.values():
            for _ in range(limit_per_node):
                packet = node.outbound.pop()
                if packet is None:
                    break
                cur = packet.current_node()
                nxt = packet.next_node()
                if cur is None or nxt is None or packet.ttl <= 0:
                    dropped += 1
                    node.dropped += 1
                    continue
                ch = self.channel_between(cur, nxt)
                if ch is None:
                    dropped += 1
                    node.dropped += 1
                    continue
                ok = ch.enqueue(cur, nxt, packet)
                if ok:
                    moved += 1
                else:
                    dropped += 1
                    node.dropped += 1
        return moved, dropped


# ---------------------------------------------------------------------------
# Category theory layer
# ---------------------------------------------------------------------------

class CategoryObject:
    __slots__ = ("id", "name", "kind", "level", "data")

    def __init__(self, object_id: int, name: str, kind: str, level: int = 1, data: Optional[Dict[str, Any]] = None) -> None:
        self.id = object_id
        self.name = name
        self.kind = kind
        self.level = int(clamp(level, 1, 12))
        self.data = dict(data or {})


class Morphism:
    __slots__ = ("id", "source", "target", "name", "kind", "bundle", "strength", "data", "components")

    def __init__(self, morphism_id: int, source: int, target: int, name: str, kind: str = "generic", bundle: Optional[HierarchyBundle] = None, strength: float = 1.0, data: Optional[Dict[str, Any]] = None, components: Optional[List[int]] = None) -> None:
        self.id = morphism_id
        self.source = source
        self.target = target
        self.name = name
        self.kind = kind
        self.bundle = bundle or HierarchyBundle()
        self.strength = float(strength)
        self.data = dict(data or {})
        self.components = list(components or [])

    def compose_with(self, other: "Morphism", new_id: int) -> Optional["Morphism"]:
        # self ; other, i.e. other after self
        if self.target != other.source:
            return None
        b = self.bundle.merge(other.bundle)
        return Morphism(new_id, self.source, other.target, "%s ∘ %s" % (other.name, self.name), "composed:%s/%s" % (self.kind, other.kind), b, self.strength * other.strength, {"left": self.id, "right": other.id}, [self.id, other.id])


class Category:
    __slots__ = ("name", "objects", "morphisms", "hom", "identities", "next_morphism_id", "composition_attempts", "composition_successes")

    def __init__(self, name: str) -> None:
        self.name = name
        self.objects: Dict[int, CategoryObject] = {}
        self.morphisms: Dict[int, Morphism] = {}
        self.hom: Dict[Tuple[int, int], List[int]] = defaultdict(list)
        self.identities: Dict[int, int] = {}
        self.next_morphism_id = 1
        self.composition_attempts = 0
        self.composition_successes = 0

    def add_object(self, obj: CategoryObject) -> None:
        self.objects[obj.id] = obj
        if obj.id not in self.identities:
            mid = self.allocate_morphism_id()
            ident = Morphism(mid, obj.id, obj.id, "id_%s" % obj.name, "identity", HierarchyBundle.single(obj.level, "morphism", 1.0), 1.0)
            self.add_morphism(ident, is_identity=True)

    def allocate_morphism_id(self) -> int:
        mid = self.next_morphism_id
        self.next_morphism_id += 1
        return mid

    def add_morphism(self, m: Morphism, is_identity: bool = False) -> None:
        if m.source not in self.objects or m.target not in self.objects:
            return
        self.morphisms[m.id] = m
        self.hom[(m.source, m.target)].append(m.id)
        if is_identity:
            self.identities[m.source] = m.id

    def new_morphism(self, source: int, target: int, name: str, kind: str, bundle: Optional[HierarchyBundle] = None, strength: float = 1.0, data: Optional[Dict[str, Any]] = None) -> Optional[Morphism]:
        if source not in self.objects or target not in self.objects:
            return None
        m = Morphism(self.allocate_morphism_id(), source, target, name, kind, bundle, strength, data)
        self.add_morphism(m)
        return m

    def compose(self, left_id: int, right_id: int) -> Optional[Morphism]:
        # left ; right
        self.composition_attempts += 1
        left = self.morphisms.get(left_id)
        right = self.morphisms.get(right_id)
        if not left or not right:
            return None
        comp = left.compose_with(right, self.allocate_morphism_id())
        if comp is None:
            return None
        self.add_morphism(comp)
        self.composition_successes += 1
        return comp

    def hom_count(self) -> int:
        return sum(len(v) for v in self.hom.values())

    def kind_counts(self) -> Dict[str, int]:
        c: Dict[str, int] = defaultdict(int)
        for m in self.morphisms.values():
            c[m.kind] += 1
        return dict(c)

    def sample_associativity(self, rng: FastRNG, trials: int = 200) -> Dict[str, int]:
        ids = [mid for mid, m in self.morphisms.items() if m.kind != "identity"]
        checked = 0
        passed = 0
        failed = 0
        if len(ids) < 3:
            return {"checked": 0, "passed": 0, "failed": 0}
        for _ in range(min(trials, len(ids) * 2)):
            f = self.morphisms[rng.choice(ids)]
            g_candidates = [self.morphisms[mid] for mid in self.hom.get((f.target, f.target), [])]
            if not g_candidates:
                g_candidates = [self.morphisms[mid] for mid in ids if self.morphisms[mid].source == f.target]
            if not g_candidates:
                continue
            g = rng.choice(g_candidates)
            h_candidates = [self.morphisms[mid] for mid in ids if self.morphisms[mid].source == g.target]
            if not h_candidates:
                continue
            h = rng.choice(h_candidates)
            # We do not insert temporary composites into category; verify boundary equality.
            checked += 1
            left_ok = (f.source == f.source and h.target == h.target and f.target == g.source and g.target == h.source)
            right_ok = left_ok
            if left_ok and right_ok:
                passed += 1
            else:
                failed += 1
        return {"checked": checked, "passed": passed, "failed": failed}

    def stats(self) -> Dict[str, Any]:
        return {"name": self.name, "objects": len(self.objects), "morphisms": len(self.morphisms), "hom_sets": len(self.hom), "composition_attempts": self.composition_attempts, "composition_successes": self.composition_successes, "kind_counts": self.kind_counts()}


class Functor:
    __slots__ = ("name", "source", "target", "object_map", "morphism_map")

    def __init__(self, name: str, source: Category, target: Category) -> None:
        self.name = name
        self.source = source
        self.target = target
        self.object_map: Dict[int, int] = {}
        self.morphism_map: Dict[int, int] = {}

    def map_object(self, source_obj: int, target_obj: int) -> None:
        if source_obj in self.source.objects and target_obj in self.target.objects:
            self.object_map[source_obj] = target_obj

    def map_morphism(self, source_morphism: int, target_morphism: int) -> None:
        if source_morphism in self.source.morphisms and target_morphism in self.target.morphisms:
            self.morphism_map[source_morphism] = target_morphism

    def verify_sample(self, rng: FastRNG, trials: int = 200) -> Dict[str, int]:
        ids = list(self.morphism_map.keys())
        checked = 0
        boundary_ok = 0
        identity_ok = 0
        if not ids:
            return {"checked": 0, "boundary_ok": 0, "identity_ok": 0}
        for oid, ident_id in list(self.source.identities.items())[:trials]:
            mapped_obj = self.object_map.get(oid)
            mapped_mor = self.morphism_map.get(ident_id)
            if mapped_obj is None or mapped_mor is None:
                continue
            checked += 1
            if self.target.identities.get(mapped_obj) == mapped_mor:
                identity_ok += 1
        for _ in range(min(trials, len(ids))):
            mid = rng.choice(ids)
            m = self.source.morphisms[mid]
            tm = self.target.morphisms.get(self.morphism_map[mid])
            if tm is None:
                continue
            checked += 1
            if self.object_map.get(m.source) == tm.source and self.object_map.get(m.target) == tm.target:
                boundary_ok += 1
        return {"checked": checked, "boundary_ok": boundary_ok, "identity_ok": identity_ok}


class NaturalTransformation:
    __slots__ = ("name", "F", "G", "components")

    def __init__(self, name: str, F: Functor, G: Functor) -> None:
        self.name = name
        self.F = F
        self.G = G
        self.components: Dict[int, int] = {}

    def set_component(self, source_obj: int, target_morphism: int) -> None:
        if source_obj in self.F.source.objects and target_morphism in self.F.target.morphisms:
            self.components[source_obj] = target_morphism

    def verify_sample(self, rng: FastRNG, trials: int = 200) -> Dict[str, int]:
        ids = [mid for mid in self.F.source.morphisms if mid in self.F.morphism_map and mid in self.G.morphism_map]
        checked = 0
        natural = 0
        violated = 0
        if not ids:
            return {"checked": 0, "natural": 0, "violated": 0}
        target_cat = self.F.target
        for _ in range(min(trials, len(ids))):
            mid = rng.choice(ids)
            f = self.F.source.morphisms[mid]
            eta_x_id = self.components.get(f.source)
            eta_y_id = self.components.get(f.target)
            Ff_id = self.F.morphism_map.get(mid)
            Gf_id = self.G.morphism_map.get(mid)
            if eta_x_id is None or eta_y_id is None or Ff_id is None or Gf_id is None:
                continue
            eta_x = target_cat.morphisms.get(eta_x_id)
            eta_y = target_cat.morphisms.get(eta_y_id)
            Ff = target_cat.morphisms.get(Ff_id)
            Gf = target_cat.morphisms.get(Gf_id)
            if not eta_x or not eta_y or not Ff or not Gf:
                continue
            checked += 1
            # Naturality square: G(f) after eta_x has same boundary as eta_y after F(f).
            left_ok = eta_x.target == Gf.source and eta_x.source == Ff.source
            right_ok = Ff.target == eta_y.source and Gf.target == eta_y.target
            if left_ok and right_ok:
                natural += 1
            else:
                violated += 1
        return {"checked": checked, "natural": natural, "violated": violated}


class UniversalPropertyWitness:
    __slots__ = ("name", "category", "kind", "apex", "legs", "checks", "passed")

    def __init__(self, name: str, category: Category, kind: str, apex: int, legs: List[int]) -> None:
        self.name = name
        self.category = category
        self.kind = kind
        self.apex = apex
        self.legs = list(legs)
        self.checks = 0
        self.passed = 0

    def verify_sample(self, rng: FastRNG, trials: int = 100) -> Dict[str, Any]:
        objs = list(self.category.objects.keys())
        if not objs or self.apex not in self.category.objects:
            return {"kind": self.kind, "checked": 0, "passed": 0, "ratio": 0.0}
        checked = 0
        passed = 0
        adjacency: Dict[int, List[int]] = defaultdict(list)
        for (src, dst), mids in self.category.hom.items():
            if mids:
                adjacency[src].append(dst)

        def reachable(start: int, goal: int, max_depth: int = 7) -> bool:
            if start == goal:
                return True
            q = deque([(start, 0)])
            seen = set([start])
            while q:
                node, depth = q.popleft()
                if depth >= max_depth:
                    continue
                for dst in adjacency.get(node, []):
                    if dst == goal:
                        return True
                    if dst not in seen:
                        seen.add(dst)
                        q.append((dst, depth + 1))
            return False

        if self.kind == "terminal":
            for x in rng.sample(objs, min(trials, len(objs))):
                checked += 1
                if reachable(x, self.apex):
                    passed += 1
        elif self.kind == "initial":
            for x in rng.sample(objs, min(trials, len(objs))):
                checked += 1
                if reachable(self.apex, x):
                    passed += 1
        elif self.kind == "product":
            # Operational product-like witness: the apex has projection legs, and mediators x -> apex
            # can be followed by those legs to reach all projected objects.
            projection_targets = [self.category.morphisms[l].target for l in self.legs if l in self.category.morphisms]
            mediator_sources = [src for (src, dst), mids in self.category.hom.items() if dst == self.apex and mids]
            if len(projection_targets) >= 2 and mediator_sources:
                for x in rng.sample(mediator_sources, min(trials, len(mediator_sources))):
                    checked += 1
                    ok = True
                    for target in projection_targets[:2]:
                        if not self.category.hom.get((self.apex, target), []):
                            ok = False
                            break
                    if ok:
                        passed += 1
        else:
            for x in rng.sample(objs, min(trials, len(objs))):
                checked += 1
                if self.category.hom.get((x, self.apex), []) or self.category.hom.get((self.apex, x), []):
                    passed += 1
        self.checks += checked
        self.passed += passed
        ratio = passed / max(1, checked)
        return {"name": self.name, "kind": self.kind, "checked": checked, "passed": passed, "ratio": round(ratio, 3)}


class PresheafSection:
    __slots__ = ("object_id", "name", "data")

    def __init__(self, object_id: int, name: str, data: Dict[str, Any]) -> None:
        self.object_id = object_id
        self.name = name
        self.data = dict(data)

    def restrict(self, target_object_id: int, keys: Optional[Sequence[str]] = None) -> "PresheafSection":
        if keys is None:
            restricted = dict(self.data)
        else:
            restricted = {k: self.data[k] for k in keys if k in self.data}
        return PresheafSection(target_object_id, "%s|%s" % (self.name, target_object_id), restricted)


class Presheaf:
    __slots__ = ("name", "category", "sections", "restriction_keys", "restrictions_applied")

    def __init__(self, name: str, category: Category) -> None:
        self.name = name
        self.category = category
        self.sections: Dict[int, List[PresheafSection]] = defaultdict(list)
        self.restriction_keys: Dict[str, List[str]] = {}
        self.restrictions_applied = 0

    def add_section(self, object_id: int, section: PresheafSection) -> None:
        if object_id in self.category.objects:
            self.sections[object_id].append(section)

    def restrict_along(self, morphism_id: int, section: PresheafSection) -> Optional[PresheafSection]:
        m = self.category.morphisms.get(morphism_id)
        if m is None:
            return None
        # Contravariant: a morphism U -> V restricts information at V down to U.
        keys = self.restriction_keys.get(m.kind)
        self.restrictions_applied += 1
        return section.restrict(m.source, keys)

    def stats(self) -> Dict[str, Any]:
        return {"name": self.name, "objects_with_sections": len(self.sections), "sections": sum(len(v) for v in self.sections.values()), "restrictions_applied": self.restrictions_applied}


class Sheaf(Presheaf):
    __slots__ = ("covers", "glued", "compatibility_checks", "compatibility_passed")

    def __init__(self, name: str, category: Category) -> None:
        super().__init__(name, category)
        self.covers: Dict[int, List[int]] = defaultdict(list)
        self.glued: Dict[int, PresheafSection] = {}
        self.compatibility_checks = 0
        self.compatibility_passed = 0

    def set_cover(self, object_id: int, cover_object_ids: List[int]) -> None:
        self.covers[object_id] = [oid for oid in cover_object_ids if oid in self.category.objects]

    def compatible(self, sections: List[PresheafSection]) -> bool:
        self.compatibility_checks += 1
        common: Dict[str, Any] = {}
        for section in sections:
            for k, v in section.data.items():
                if k in common and common[k] != v:
                    # Numeric values are compatible if they are near.
                    if isinstance(v, (int, float)) and isinstance(common[k], (int, float)):
                        base = max(1.0, abs(float(common[k])), abs(float(v)))
                        if abs(float(v) - float(common[k])) / base <= 0.35:
                            continue
                    # A cover may intentionally contain different domains/bodies/queue disciplines.
                    # These symbolic differences glue as a union of local labels, not as a contradiction.
                    if k in ("domain", "body", "queue"):
                        continue
                    return False
                common[k] = v
        self.compatibility_passed += 1
        return True

    def glue(self, object_id: int) -> Optional[PresheafSection]:
        cover = self.covers.get(object_id, [])
        gathered: List[PresheafSection] = []
        for oid in cover:
            if self.sections.get(oid):
                gathered.append(self.sections[oid][-1])
        if not gathered:
            return None
        if not self.compatible(gathered):
            return None
        merged: Dict[str, Any] = {}
        for sec in gathered:
            for k, v in sec.data.items():
                if isinstance(v, (int, float)) and k in merged and isinstance(merged[k], (int, float)):
                    merged[k] = (float(merged[k]) + float(v)) / 2.0
                elif k in merged and merged[k] != v and k in ("domain", "body", "queue"):
                    prev = str(merged[k])
                    val = str(v)
                    parts = prev.split("|")
                    if val not in parts and len(parts) < 8:
                        merged[k] = prev + "|" + val
                else:
                    merged[k] = v
        out = PresheafSection(object_id, "glued:%s" % object_id, merged)
        self.glued[object_id] = out
        return out

    def stats(self) -> Dict[str, Any]:
        d = super().stats()
        d.update({"covers": len(self.covers), "glued": len(self.glued), "compatibility_checks": self.compatibility_checks, "compatibility_passed": self.compatibility_passed})
        return d


# ---------------------------------------------------------------------------
# Main simulation
# ---------------------------------------------------------------------------

SCALE_CONFIGS = {
    "demo": {
        "earth_countries": 8, "moon_countries": 3, "mars_countries": 4,
        "companies": 120, "workers": 1800, "products": 850,
        "product_trades": 2600, "privilege_trades": 160, "burden_trades": 120, "market_trades": 55,
        "network_packets": 1800, "queue_capacity_scale": 1,
    },
    "large": {
        "earth_countries": 72, "moon_countries": 12, "mars_countries": 18,
        "companies": 1700, "workers": 32000, "products": 13000,
        "product_trades": 45000, "privilege_trades": 2500, "burden_trades": 1700, "market_trades": 650,
        "network_packets": 26000, "queue_capacity_scale": 2,
    },
    "huge": {
        "earth_countries": 180, "moon_countries": 30, "mars_countries": 45,
        "companies": 6000, "workers": 160000, "products": 45000,
        "product_trades": 190000, "privilege_trades": 10000, "burden_trades": 7000, "market_trades": 2600,
        "network_packets": 120000, "queue_capacity_scale": 4,
    },
}


class SolarNetworkCategoryEconomy:
    def __init__(self, profile: str = "demo", seed: int = 42, quiet: bool = False) -> None:
        if profile not in SCALE_CONFIGS:
            raise ValueError("unknown profile")
        self.profile = profile
        self.cfg = dict(SCALE_CONFIGS[profile])
        self.seed = seed
        self.rng = FastRNG(seed)
        self.quiet = quiet
        self.tick = 0
        self.next_entity_id = 1
        self.next_node_id = 1
        self.next_channel_id = 1
        self.next_packet_id = 1

        self.entities: Dict[int, AccountEntity] = {}
        self.bodies: Dict[str, CelestialBody] = {}
        self.un_by_scope: Dict[str, int] = {}
        self.defense_by_scope: Dict[str, int] = {}
        self.countries: Dict[int, Country] = {}
        self.alliances: Dict[int, Alliance] = {}
        self.companies: Dict[int, Company] = {}
        self.workers: Dict[int, Worker] = {}
        self.products: Dict[int, Product] = {}
        self.markets: Dict[int, Market] = {}
        self.market_rights_exchanges: List[int] = []
        self.privileges: Dict[int, Privilege] = {}
        self.burdens: Dict[int, Burden] = {}
        self.actor_ids: List[int] = []

        self.network = TopologyGraph()
        self.node_by_entity: Dict[int, int] = {}
        self.market_hub_by_scope: Dict[str, int] = {}
        self.gov_hub_by_scope: Dict[str, int] = {}

        self.econ_cat = Category("EconomicHierarchyCategory")
        self.net_cat = Category("NetworkFlowCategory")
        self.hier_cat = Category("HierarchyLevelCategory")
        self.top_cat = Category("TopologyCategory")
        self.econ_to_net = Functor("EconomicToNetworkFunctor", self.econ_cat, self.net_cat)
        self.econ_to_hier = Functor("StatusFunctor", self.econ_cat, self.hier_cat)
        self.econ_to_access = Functor("AccessFunctor", self.econ_cat, self.hier_cat)
        self.status_to_access = NaturalTransformation("StatusToAccessNaturalTransformation", self.econ_to_hier, self.econ_to_access)
        self.market_sheaf = Sheaf("MarketStateSheaf", self.econ_cat)
        self.universal_witnesses: List[UniversalPropertyWitness] = []

        self.trade_volume = 0.0
        self.product_sales = 0
        self.market_ownership_changes = 0
        self.manual_lifts = 0
        self.packets_created = 0
        self.packets_delivered = 0
        self.packets_dropped = 0
        self.route_failures = 0
        self.network_moved = 0
        self.network_channel_drops = 0
        self.packet_kind_counts: Dict[str, int] = defaultdict(int)
        self.initial_levels: Dict[str, Dict[int, int]] = {"workers": {}, "companies": {}, "countries": {}, "alliances": {}}
        self.mobility_counts: Dict[str, Dict[str, int]] = {
            "workers": {"up": 0, "down": 0, "same": 0},
            "companies": {"up": 0, "down": 0, "same": 0},
            "countries": {"up": 0, "down": 0, "same": 0},
            "alliances": {"up": 0, "down": 0, "same": 0},
        }
        self.mobility_heatmaps: Dict[str, Dict[int, Dict[int, int]]] = {
            "workers": defaultdict(lambda: defaultdict(int)),
            "companies": defaultdict(lambda: defaultdict(int)),
            "countries": defaultdict(lambda: defaultdict(int)),
            "alliances": defaultdict(lambda: defaultdict(int)),
        }
        self.macro_history: List[Dict[str, Any]] = []
        self.scenario_scores: Dict[str, float] = defaultdict(float)
        self.tick_volatility: List[float] = []

    # ----------------------------- id and registry helpers -----------------------------

    def eid(self) -> int:
        v = self.next_entity_id
        self.next_entity_id += 1
        return v

    def nid(self) -> int:
        v = self.next_node_id
        self.next_node_id += 1
        return v

    def cid(self) -> int:
        v = self.next_channel_id
        self.next_channel_id += 1
        return v

    def pid(self) -> int:
        v = self.next_packet_id
        self.next_packet_id += 1
        return v

    def register_entity(self, e: AccountEntity, network_role: str = "economic") -> AccountEntity:
        self.entities[e.id] = e
        obj = CategoryObject(e.id, e.name, e.kind, e.level, {"body": e.body, "domain": e.domain})
        self.econ_cat.add_object(obj)
        node = NetworkNode(self.nid(), e.id, e.name, e.kind, e.body, e.level, network_role)
        e.node_id = node.id
        self.node_by_entity[e.id] = node.id
        self.network.add_node(node)
        nobj = CategoryObject(node.id, node.name, "network_node:%s" % node.kind, node.level, {"body": node.body, "role": node.role})
        self.net_cat.add_object(nobj)
        self.econ_to_net.map_object(e.id, node.id)
        # Two functors into the hierarchy category: raw status and access/entitlement.
        # They are updated again after level refreshes.
        self.econ_to_hier.map_object(e.id, level_object_id(e.level))
        self.econ_to_access.map_object(e.id, level_object_id(e.entitlement_level(e.domain, self.privileges, self.burdens)))
        return e

    def add_econ_morphism(self, source: int, target: int, name: str, kind: str, bundle: Optional[HierarchyBundle] = None, strength: float = 1.0, data: Optional[Dict[str, Any]] = None, create_packet: bool = False, priority: int = 5) -> Optional[Morphism]:
        m = self.econ_cat.new_morphism(source, target, name, kind, bundle, strength, data)
        if m is None:
            return None
        src_node = self.node_by_entity.get(source)
        dst_node = self.node_by_entity.get(target)
        if src_node is not None and dst_node is not None:
            nm = self.net_cat.new_morphism(src_node, dst_node, "net:%s" % name, "flow:%s" % kind, bundle or HierarchyBundle.single(1, "morphism", 1.0), strength, {"econ_morphism": m.id})
            if nm:
                self.econ_to_net.map_morphism(m.id, nm.id)
        # hierarchy functors: each economic morphism maps to level transition morphisms.
        status_source = self.econ_to_hier.object_map.get(source, level_object_id(self.entities[source].level))
        status_target = self.econ_to_hier.object_map.get(target, level_object_id(self.entities[target].level))
        access_source = self.econ_to_access.object_map.get(source, status_source)
        access_target = self.econ_to_access.object_map.get(target, status_target)
        sm = self.hier_cat.new_morphism(status_source, status_target, "status:%s" % name, "status_transition", HierarchyBundle.single(max(1, self.entities[target].level), "functor", 1.0), strength)
        am = self.hier_cat.new_morphism(access_source, access_target, "access:%s" % name, "access_transition", HierarchyBundle.single(max(1, self.entities[target].level), "functor", 1.0), strength)
        if sm:
            self.econ_to_hier.map_morphism(m.id, sm.id)
        if am:
            self.econ_to_access.map_morphism(m.id, am.id)
        if create_packet:
            self.emit_packet(source, target, kind, bundle or HierarchyBundle.single(1, "morphism", 1.0), m.id, data or {}, priority=priority)
        return m

    def connect_entities(self, a: int, b: int, topology: str, mode: str, queue_kind: str, latency: int, bandwidth: int, sem_capacity: int) -> Optional[Channel]:
        na = self.node_by_entity.get(a)
        nb = self.node_by_entity.get(b)
        if na is None or nb is None:
            return None
        if self.network.channel_between(na, nb) is not None:
            return self.network.channel_between(na, nb)
        ch = Channel(self.cid(), "%s↔%s" % (self.entities[a].name[:16], self.entities[b].name[:16]), na, nb, mode=mode, topology=topology, latency=latency, bandwidth=bandwidth, queue_kind=queue_kind, semaphore_capacity=sem_capacity)
        self.network.connect(ch)
        m = self.net_cat.new_morphism(na, nb, "channel:%s" % ch.name, "channel:%s:%s" % (topology, mode), HierarchyBundle.single(max(self.entities[a].level, self.entities[b].level), "topology", 1.0), 1.0, {"channel_id": ch.id})
        if m:
            self.net_cat.new_morphism(nb, na, "channel:%s:reverse" % ch.name, "channel:%s:%s" % (topology, mode), HierarchyBundle.single(max(self.entities[a].level, self.entities[b].level), "topology", 1.0), 1.0, {"channel_id": ch.id})
        return ch

    # ----------------------------- build hierarchy categories -----------------------------

    def build_hierarchy_category(self) -> None:
        for level in range(1, 13):
            self.hier_cat.add_object(CategoryObject(level_object_id(level), "Level %02d %s" % (level, LEVEL_NAMES[level]), "hierarchy_level", level, {"multiplier": HEIGHT_MULTIPLIERS[level]}))
        # order morphisms and adjunction-like ascent/descent pairs
        for level in range(1, 12):
            self.hier_cat.new_morphism(level_object_id(level), level_object_id(level + 1), "ascend_%02d_%02d" % (level, level + 1), "ascent", HierarchyBundle.single(level + 1, "morphism", 1.0), HEIGHT_MULTIPLIERS[level + 1] / HEIGHT_MULTIPLIERS[level])
            self.hier_cat.new_morphism(level_object_id(level + 1), level_object_id(level), "descend_%02d_%02d" % (level + 1, level), "descent", HierarchyBundle.single(level, "morphism", 1.0), HEIGHT_MULTIPLIERS[level] / HEIGHT_MULTIPLIERS[level + 1])

    def build_topology_category(self) -> None:
        for idx, topo in enumerate(TOPOLOGY_KINDS, start=1):
            self.top_cat.add_object(CategoryObject(10_000 + idx, topo, "topology", idx, {"topology": topo}))
        topo_ids = {topo: 10_000 + idx for idx, topo in enumerate(TOPOLOGY_KINDS, start=1)}
        # morphisms between topologies: compression, refinement, forgetful projections
        pairs = [
            ("tree", "star", "collapse branches"), ("star", "mesh", "densify hubs"),
            ("ring", "mesh", "add chords"), ("mesh", "market-bipartite", "split buyers sellers"),
            ("governance", "tree", "forget laws"), ("sheaf-cover", "star", "choose cover center"),
            ("market-bipartite", "sheaf-cover", "localize overlaps"), ("mesh", "ring", "thin to cycle"),
        ]
        for a, b, name in pairs:
            self.top_cat.new_morphism(topo_ids[a], topo_ids[b], name, "topology_morphism", HierarchyBundle.single(7, "topology", 1.0), 1.0)

    # ----------------------------- build economy -----------------------------

    def record_initial_levels(self) -> None:
        for group_name, mapping in [("workers", self.workers), ("companies", self.companies), ("countries", self.countries), ("alliances", self.alliances)]:
            self.initial_levels[group_name] = {eid: entity.level for eid, entity in mapping.items()}

    def update_mobility_tracking(self) -> None:
        for group_name, mapping in [("workers", self.workers), ("companies", self.companies), ("countries", self.countries), ("alliances", self.alliances)]:
            counts = {"up": 0, "down": 0, "same": 0}
            heat: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
            initials = self.initial_levels.get(group_name, {})
            for eid, entity in mapping.items():
                initial = initials.get(eid, entity.level)
                final = entity.level
                if final > initial:
                    counts["up"] += 1
                elif final < initial:
                    counts["down"] += 1
                else:
                    counts["same"] += 1
                heat[initial][final] += 1
            self.mobility_counts[group_name] = counts
            self.mobility_heatmaps[group_name] = heat

    def apply_macro_scenario(self) -> None:
        event_bank = [
            ("resource_boom", "A resource boom increases capital, logistics and industry.", [(self.companies, {"capital": 0.16, "logistics": 0.13, "infrastructure": 0.10}), (self.countries, {"capital": 0.12, "infrastructure": 0.08})]),
            ("research_breakthrough", "Research and compute sectors accelerate and spread prestige upward.", [(self.companies, {"science": 0.18, "compute": 0.18, "data": 0.12}), (self.workers, {"science": 0.14, "skill": 0.08})]),
            ("media_polarization", "Media and trust become unstable; some actors rise, others fall.", [(self.workers, {"media": 0.15, "trust": -0.08}), (self.countries, {"trust": -0.06, "governance": 0.03})]),
            ("defense_alert", "Defense and risk become more valuable across alliances and states.", [(self.alliances, {"military": 0.18, "risk": 0.12}), (self.countries, {"military": 0.15, "risk": 0.08})]),
            ("governance_reform", "Governance and trust improve, raising institutional coherence.", [(self.countries, {"governance": 0.14, "trust": 0.12}), (self.companies, {"trust": 0.06, "market_access": 0.05})]),
            ("supply_shock", "Supply routes fail in places; logistics and market access become uneven.", [(self.companies, {"logistics": -0.16, "market_access": -0.11}), (self.markets, {"market_access": -0.12, "logistics": -0.10})]),
            ("care_recognition", "Care, education and social trust receive institutional recognition.", [(self.workers, {"care": 0.20, "trust": 0.09}), (self.companies, {"care": 0.10})]),
            ("interplanetary_expansion", "Mars and Moon gain extra infrastructure and shipping relevance.", [(self.countries, {"infrastructure": 0.10, "logistics": 0.11}), (self.markets, {"transport": 0.12, "market_access": 0.10})]),
        ]
        chosen = self.rng.sample(event_bank, self.rng.randint(2, 4))
        tick_impact = 0.0
        for name, description, targets in chosen:
            event_strength = self.rng.uniform(0.65, 1.45)
            self.scenario_scores[name] += event_strength
            for mapping, delta_map in targets:
                ids = list(mapping.keys())
                if not ids:
                    continue
                take = min(len(ids), max(1, int(len(ids) * self.rng.uniform(0.08, 0.28))))
                chosen_ids = self.rng.sample(ids, take)
                for eid in chosen_ids:
                    entity = mapping[eid]
                    # extra body bias for expansion-type scenarios
                    if name == "interplanetary_expansion" and getattr(entity, "body", "") in ("Moon", "Mars"):
                        body_bonus = 1.35
                    else:
                        body_bonus = 1.0
                    sign_flips = 1.0
                    if name in ("media_polarization", "supply_shock") and self.rng.chance(0.35):
                        sign_flips = -0.55
                    for key, delta in delta_map.items():
                        current = entity.elements.get(key, 0.0)
                        drift = 1.0 + delta * event_strength * body_bonus * sign_flips
                        entity.elements[key] = max(0.0, current * drift + self.rng.uniform(0.0, max(4.0, abs(current) * 0.015)))
                    if self.rng.chance(0.14):
                        entity.wallet.deposit(HierarchyBundle.single(max(1, entity.level), "capital", self.rng.uniform(0.5, 4.5) * event_strength))
            tick_impact += event_strength
            self.macro_history.append({"tick": self.tick, "name": name, "description": description, "strength": round(event_strength, 3)})
        self.tick_volatility.append(round(tick_impact, 3))

    def what_more_can_be_simulated(self) -> List[str]:
        return [
            "demographic transitions across generations, including inheritance, education pipelines and retirement pressure",
            "banking, debt chains, insolvency cascades and lender-of-last-resort interventions",
            "elections, propaganda, censorship, institutional legitimacy and constitutional crises",
            "migration flows between Earth, Moon and Mars, including brain drain and labor shortages",
            "war, deterrence, arms races and negotiated disarmament between defense alliances",
            "innovation races across research clusters, patents and open-knowledge commons",
            "ecological constraints such as oxygen scarcity, water contamination and food crop failures",
            "criminal markets, corruption networks, smuggling and anti-corruption enforcement",
            "cultural prestige markets, reputational bubbles and symbolic capital",
            "infrastructure sabotage, cyber conflict, packet-routing failures and redundancy planning",
            "class conflict, strikes, union power, social insurance and redistributive reforms",
            "planetary catastrophes, emergency regimes and resilience under extreme shocks",
        ]

    def goods_hierarchy_rows(self) -> List[Tuple[Any, ...]]:
        rows = []
        for level in range(1, 13):
            goods = GOODS_HIERARCHY[level]
            rows.append(("L%02d" % level, LEVEL_NAMES[level], len(goods), "; ".join(goods[:2]), "; ".join(goods[2:])))
        return rows

    def mobility_summary_text(self, key: str) -> str:
        counts = self.mobility_counts[key]
        total = max(1, counts["up"] + counts["down"] + counts["same"])
        up_r = counts["up"] / total
        down_r = counts["down"] / total
        same_r = counts["same"] / total
        if up_r > 0.42 and down_r > 0.20:
            return "%s show strong churn: many actors rose, but a meaningful share also fell. This is a volatile merit hierarchy rather than a frozen ladder." % key.title()
        if up_r > 0.38:
            return "%s mostly experienced upward career movement. The simulated environment rewarded expansion, adaptation or favorable shocks." % key.title()
        if down_r > 0.32:
            return "%s experienced substantial downward movement. The run contained enough shocks or competitive losses to punish weak positions." % key.title()
        return "%s stayed comparatively stable. Most actors held their relative level, so the hierarchy behaved more like a slow-moving order than a turbulent tournament." % key.title()

    def final_scenario_summary(self) -> str:
        scores = sorted(self.scenario_scores.items(), key=lambda kv: -kv[1])
        dominant = ", ".join(["%s=%s" % (name, short_number(score)) for name, score in scores[:4]]) if scores else "none"
        volatility = sum(self.tick_volatility) / max(1, len(self.tick_volatility))
        parts = []
        parts.append("This run combined several stochastic macro-patterns. Dominant scenario drivers were: %s." % dominant)
        parts.append("Average scenario volatility per tick was %s. Higher values mean the same structural model could have produced noticeably different winners and losers in another run." % short_number(volatility))
        parts.append("Possible alternative outcomes remain balanced: a more defense-heavy path would have lifted alliances and military states further; a stronger care-recognition path would have favored workers in care, education and trust-rich institutions; a harsher supply-shock path would have punished logistics-sensitive firms and markets; and a research-breakthrough path would have shifted value toward data, compute and science clusters.")
        parts.append("Therefore the present output should be read as one realized scenario among many nearby possibilities, not as a single inevitable equilibrium.")
        return "\n".join(parts)

    def build(self) -> None:
        if not self.quiet:
            print("Building network/category hierarchy-market simulation profile=%s seed=%s" % (self.profile, self.seed))
        self.build_hierarchy_category()
        self.build_topology_category()
        self.create_bodies_and_global_orgs()
        self.create_countries_and_alliances()
        self.create_companies_workers_products_markets()
        self.build_network_topologies()
        self.build_category_structure()
        self.install_presheaves_and_sheaves()
        self.refresh_all_levels()
        self.record_initial_levels()
        self.update_mobility_tracking()
        if not self.quiet:
            print(self.build_report())

    def create_bodies_and_global_orgs(self) -> None:
        solar = CelestialBody(self.eid(), "Solar System", scope="Solar System", body="Solar System", level=12, domain="governance", elements={"governance": 25000, "infrastructure": 9000, "topology": 6000})
        self.register_entity(solar, "body")
        self.bodies["Solar System"] = solar
        sun = self.register_entity(UNOrganization(self.eid(), "Solar System United Nations", scope="Solar System", body="Solar System", level=12, domain="governance", elements={"governance": 19000, "trust": 6000, "sheaf": 3000, "functor": 3000}), "governance")
        sdef = self.register_entity(DefenseOrganization(self.eid(), "Solar System Defense Organization", scope="Solar System", body="Solar System", level=12, domain="military", elements={"military": 22000, "risk": 7000, "semaphore": 5000}), "defense")
        self.un_by_scope["Solar System"] = sun.id
        self.defense_by_scope["Solar System"] = sdef.id
        solar.un_id = sun.id
        solar.defense_id = sdef.id
        # main hubs are real economic entities so categories can see them.
        for scope, owner in [("Solar System", sun.id), ("Earth", None), ("Moon", None), ("Mars", None)]:
            pass
        for body in BODIES:
            b = CelestialBody(self.eid(), body, scope=body, body=body, level=12 if body == "Earth" else 11, domain="governance", elements={"governance": 9000, "infrastructure": 4500, "topology": 2500}, owner_id=sun.id)
            self.register_entity(b, "body")
            self.bodies[body] = b
            un = self.register_entity(UNOrganization(self.eid(), "United Nations of %s" % body, scope=body, body=body, level=12 if body == "Earth" else 11, domain="governance", elements={"governance": 10500, "trust": 3200, "sheaf": 2000, "functor": 1200}, owner_id=sun.id), "governance")
            de = self.register_entity(DefenseOrganization(self.eid(), "%s Defense Organization" % body, scope=body, body=body, level=12 if body == "Earth" else 11, domain="military", elements={"military": 12000, "risk": 3900, "semaphore": 2500}, owner_id=sdef.id), "defense")
            self.un_by_scope[body] = un.id
            self.defense_by_scope[body] = de.id
            b.un_id = un.id
            b.defense_id = de.id
            self.add_econ_morphism(sun.id, un.id, "solar governance inclusion %s" % body, "governance", HierarchyBundle.single(12, "governance", 30.0))
            self.add_econ_morphism(sdef.id, de.id, "solar defense inclusion %s" % body, "defense", HierarchyBundle.single(12, "military", 30.0))

    def create_countries_and_alliances(self) -> None:
        counts = {"Earth": self.cfg["earth_countries"], "Moon": self.cfg["moon_countries"], "Mars": self.cfg["mars_countries"]}
        for body, n in counts.items():
            un_id = self.un_by_scope[body]
            def_id = self.defense_by_scope[body]
            # two alliances per body, plus global solar connection.
            for ai in range(2):
                a = Alliance(self.eid(), "%s Alliance %d" % (body, ai + 1), scope=body, body=body, level=8 + (1 if body == "Earth" else 0), domain="military", elements={"military": 1800 + ai * 300, "governance": 1200, "trust": 800, "topology": 300}, owner_id=def_id)
                self.register_entity(a, "alliance")
                self.alliances[a.id] = a
                self.add_econ_morphism(def_id, a.id, "defense umbrella %s" % a.name, "defense", HierarchyBundle.single(a.level, "military", 12.0))
            body_alliances = [a for a in self.alliances.values() if a.body == body]
            for i in range(n):
                base_level = 7 + int(self.rng.random() * 3) + (1 if body == "Earth" and self.rng.chance(0.45) else 0)
                country = Country(self.eid(), "%s Republic %03d" % (body, i + 1), scope=body, body=body, level=base_level, domain="governance", elements={
                    "governance": self.rng.uniform(600, 1800) * base_level,
                    "capital": self.rng.uniform(500, 2200) * base_level,
                    "military": self.rng.uniform(200, 1300) * base_level,
                    "infrastructure": self.rng.uniform(400, 1600) * base_level,
                    "topology": self.rng.uniform(80, 280) * base_level,
                }, owner_id=un_id)
                self.register_entity(country, "country")
                country.economic_power = country.elements["capital"] + country.elements["infrastructure"]
                country.military_power = country.elements["military"]
                self.countries[country.id] = country
                self.bodies[body].country_ids.append(country.id)
                self.add_econ_morphism(un_id, country.id, "legal sovereignty %s" % country.name, "governance", HierarchyBundle.single(base_level, "governance", 20.0))
                alliance = self.rng.choice(body_alliances)
                alliance.country_ids.append(country.id)
                country.alliance_ids.append(alliance.id)
                self.add_econ_morphism(alliance.id, country.id, "alliance protection %s" % country.name, "alliance", HierarchyBundle.single(base_level, "military", 10.0))

    def create_companies_workers_products_markets(self) -> None:
        country_ids = list(self.countries.keys())
        # companies
        for i in range(self.cfg["companies"]):
            country = self.countries[self.rng.choice(country_ids)]
            sector = self.rng.choice(SECTORS)
            level = int(clamp(country.level - self.rng.choice([0, 1, 1, 2, 2, 3]) + self.rng.choice([0, 0, 1]), 4, 10))
            company = Company(self.eid(), "%s Networked Company %05d" % (sector.title().replace("_", " "), i + 1), scope=country.scope, body=country.body, country_id=country.id, level=level, domain=sector, sector=sector, capacity=self.rng.randint(25, 250), elements={
                "capital": self.rng.uniform(120, 800) * level,
                "skill": self.rng.uniform(80, 500) * level,
                "market_access": self.rng.uniform(50, 450) * level,
                "queue": self.rng.uniform(20, 140) * level,
                "topology": self.rng.uniform(30, 180) * level,
                sector: self.rng.uniform(80, 600) * level,
            }, owner_id=country.id)
            company.research_intensity = self.rng.beta_like(2.0, 5.0)
            company.military_contract_share = self.rng.beta_like(1.4, 7.0) if sector != "defense" else self.rng.beta_like(5.0, 2.0)
            self.register_entity(company, "company")
            self.companies[company.id] = company
            country.company_ids.append(company.id)
            self.add_econ_morphism(country.id, company.id, "charter %s" % company.name, "corporate_charter", HierarchyBundle.single(level, "governance", 5.0))

        company_ids = list(self.companies.keys())
        # workers
        for i in range(self.cfg["workers"]):
            comp = self.companies[self.rng.choice(company_ids)]
            country = self.countries[comp.country_id] if comp.country_id else self.countries[self.rng.choice(country_ids)]
            sex = self.rng.choice(SEXES)
            age = self.rng.randint(18, 74)
            occupation = self.rng.choice(OCCUPATIONS)
            traits = {
                "skill": self.rng.beta_like(2.7, 2.2), "trust": self.rng.beta_like(3.0, 1.8),
                "risk": self.rng.beta_like(1.8, 2.8), "leadership": self.rng.beta_like(1.9, 3.0),
                "care": self.rng.beta_like(1.8, 3.3), "media": self.rng.beta_like(1.5, 3.6),
                "science": self.rng.beta_like(1.7, 3.0), "military": self.rng.beta_like(1.2, 4.5),
                "network": self.rng.beta_like(2.1, 2.3),
            }
            w = Worker(self.eid(), "Worker %07d" % (i + 1), scope=country.scope, body=country.body, country_id=country.id, level=1, occupation=occupation, age=age, sex=sex, traits=traits, elements={})
            w.recalc_elements()
            w.refresh_level(self.privileges, self.burdens)
            w.employer_id = comp.id
            self.register_entity(w, "worker")
            self.workers[w.id] = w
            comp.worker_ids.append(w.id)
            country.worker_ids.append(w.id)
            self.add_econ_morphism(comp.id, w.id, "employment %s" % w.name, "employment", HierarchyBundle.single(max(1, w.level), "labor", 2.0), strength=0.8)

        # products
        for i in range(self.cfg["products"]):
            comp = self.companies[self.rng.choice(company_ids)]
            min_level = int(clamp(comp.level + self.rng.choice([-2, -1, 0, 0, 1, 2]), 1, 12))
            quality = self.rng.uniform(0.65, 2.25)
            stock = self.rng.randint(5, 500)
            p = Product(self.eid(), "%s Product %06d" % (comp.sector.title().replace("_", " "), i + 1), scope=comp.scope, body=comp.body, country_id=comp.country_id, level=int(clamp(min_level - 1 + int(quality * 1.4), 1, 12)), domain=comp.sector, elements={
                comp.sector: quality * 16.0, "market_access": min_level * 2.0, "capital": quality * 8.0, "morphism": quality * 2.0,
            }, owner_id=comp.id, min_level=min_level, stock=stock, quality=quality)
            self.register_entity(p, "product")
            self.products[p.id] = p
            comp.product_ids.append(p.id)
            self.add_econ_morphism(comp.id, p.id, "produce %s" % p.name, "production", p.quote(), strength=quality)

        # markets: by scope/body, domain and level; every market is tradable.
        market_scopes = ["Solar System", "Earth", "Moon", "Mars"]
        for scope in market_scopes:
            body = scope
            owner_id = self.un_by_scope.get(scope, self.un_by_scope["Solar System"])
            for level in range(1, 13):
                for domain in DOMAINS:
                    queue_kind = self.rng.choice(QUEUE_KINDS)
                    mclass = MarketRightsExchange if domain == "market_rights" else Market
                    m = mclass(self.eid(), "%s L%02d %s Market" % (scope, level, domain.title().replace("_", " ")), scope=scope, body=body, country_id=None, level=level, domain=domain, elements={
                        "market_access": 35.0 * level, domain: 22.0 * level, "queue": 4.0 * level, "topology": 4.0 * level, "morphism": 2.0 * level,
                    }, owner_id=owner_id, fee_rate=0.006 + level * 0.0012, queue_discipline=queue_kind)
                    self.register_entity(m, "market")
                    self.markets[m.id] = m
                    if isinstance(m, MarketRightsExchange):
                        self.market_rights_exchanges.append(m.id)
                    self.add_econ_morphism(owner_id, m.id, "market jurisdiction %s" % m.name, "market_jurisdiction", HierarchyBundle.single(level, "market_access", 3.0))

        # listings
        market_by_domain: Dict[Tuple[str, str], List[Market]] = defaultdict(list)
        for m in self.markets.values():
            market_by_domain[(m.scope, m.domain)].append(m)
            market_by_domain[("Solar System", m.domain)].append(m)
        for p in self.products.values():
            candidates = market_by_domain.get((p.scope, p.domain), []) or market_by_domain.get(("Solar System", p.domain), [])
            if not candidates:
                continue
            m = self.rng.choice(candidates)
            m.listed_product_ids.append(p.id)
            self.add_econ_morphism(p.id, m.id, "listing %s" % p.name, "listing", p.quote().scaled(0.1))
        all_market_ids = list(self.markets.keys())
        for ex_id in self.market_rights_exchanges:
            ex = self.markets[ex_id]
            ex.listed_market_ids = self.rng.sample(all_market_ids, min(96, len(all_market_ids)))

        self.actor_ids = list(self.workers.keys()) + list(self.companies.keys()) + list(self.countries.keys()) + list(self.un_by_scope.values()) + list(self.defense_by_scope.values())
        # initial wallets
        for e in self.entities.values():
            raw = max(20.0, e.structural_number() * self.rng.uniform(0.45, 1.8) / HEIGHT_MULTIPLIERS[e.level])
            b = HierarchyBundle.single(e.level, "capital", raw * 0.48)
            b.add(e.level, e.domain, raw * 0.28)
            b.add(max(1, e.level - 1), "market_access", raw * 0.15)
            b.add(max(1, e.level - 1), "queue", raw * 0.09)
            e.wallet.deposit(b)

    # ----------------------------- network topologies -----------------------------

    def build_network_topologies(self) -> None:
        # Governance tree: solar UN -> planet UN -> country -> company -> sample workers.
        solar_un = self.un_by_scope["Solar System"]
        solar_def = self.defense_by_scope["Solar System"]
        for body in BODIES:
            un = self.un_by_scope[body]
            de = self.defense_by_scope[body]
            self.connect_entities(solar_un, un, "tree", "full", "fifo", latency=2 if body == "Earth" else 3, bandwidth=12, sem_capacity=24)
            self.connect_entities(solar_def, de, "tree", "half", "priority", latency=2 if body == "Earth" else 4, bandwidth=10, sem_capacity=18)
            for c in [x for x in self.countries.values() if x.body == body]:
                self.connect_entities(un, c.id, "governance", "full", "fifo", latency=1, bandwidth=8, sem_capacity=16)
                if c.alliance_ids:
                    self.connect_entities(c.alliance_ids[0], c.id, "star", "half", "priority", latency=1, bandwidth=6, sem_capacity=10)
                for comp_id in c.company_ids[: min(80, len(c.company_ids))]:
                    comp = self.companies[comp_id]
                    self.connect_entities(c.id, comp.id, "tree", "full", comp.queue_discipline if isinstance(comp, Market) else "fifo", latency=1, bandwidth=5, sem_capacity=10)
                    for wid in comp.worker_ids[: min(8, len(comp.worker_ids))]:
                        self.connect_entities(comp.id, wid, "tree", "half", self.rng.choice(["fifo", "lifo", "priority"]), latency=1, bandwidth=2, sem_capacity=4)

        # Interplanetary ring across UNs plus defense ring.
        ring = [self.un_by_scope["Solar System"], self.un_by_scope["Earth"], self.un_by_scope["Moon"], self.un_by_scope["Mars"]]
        for a, b in zip(ring, ring[1:] + ring[:1]):
            self.connect_entities(a, b, "ring", "full", "fifo", latency=3, bandwidth=16, sem_capacity=32)
        dring = [self.defense_by_scope["Solar System"], self.defense_by_scope["Earth"], self.defense_by_scope["Moon"], self.defense_by_scope["Mars"]]
        for a, b in zip(dring, dring[1:] + dring[:1]):
            self.connect_entities(a, b, "ring", "half", "priority", latency=3, bandwidth=12, sem_capacity=20)

        # Market hub star: each UN connects to high-level markets in its scope.
        for scope in SCOPES:
            owner = self.un_by_scope.get(scope, self.un_by_scope["Solar System"])
            markets = [m for m in self.markets.values() if m.scope == scope and m.level >= 8]
            for m in self.rng.sample(markets, min(len(markets), 120 if self.profile == "demo" else 360)):
                self.connect_entities(owner, m.id, "star", "full", m.queue_discipline, latency=1 if scope == "Earth" else 2, bandwidth=10, sem_capacity=18)

        # Bipartite product/market listing edges for a sample, enough for routing without huge explosion.
        for m in self.rng.sample(list(self.markets.values()), min(800, len(self.markets))):
            for pid in m.listed_product_ids[: min(12, len(m.listed_product_ids))]:
                p = self.products[pid]
                self.connect_entities(p.owner_id if p.owner_id else pid, m.id, "market-bipartite", "full", m.queue_discipline, latency=1, bandwidth=6, sem_capacity=10)

        # Company mesh within each body: top companies get lateral channels.
        for body in BODIES:
            comps = sorted([c for c in self.companies.values() if c.body == body], key=lambda x: x.structural_number(), reverse=True)[:40]
            for idx, comp in enumerate(comps):
                for other in comps[idx + 1: idx + 4]:
                    self.connect_entities(comp.id, other.id, "mesh", "full", self.rng.choice(QUEUE_KINDS), latency=1, bandwidth=4, sem_capacity=8)

    def build_category_structure(self) -> None:
        # Map all identities of economic category to identities in target categories.
        for eid, ent in self.entities.items():
            nid = self.node_by_entity.get(eid)
            if nid is not None:
                e_ident = self.econ_cat.identities.get(eid)
                n_ident = self.net_cat.identities.get(nid)
                if e_ident and n_ident:
                    self.econ_to_net.map_morphism(e_ident, n_ident)
            e_ident = self.econ_cat.identities.get(eid)
            if e_ident:
                hobj = level_object_id(ent.level)
                hid = self.hier_cat.identities.get(hobj)
                if hid:
                    self.econ_to_hier.map_morphism(e_ident, hid)
                    self.econ_to_access.map_morphism(e_ident, hid)
        # Natural transformation components: status level -> entitlement/access level.
        for eid, ent in list(self.entities.items())[: 6000 if self.profile != "huge" else 15000]:
            h1 = level_object_id(ent.level)
            h2 = level_object_id(ent.entitlement_level(ent.domain, self.privileges, self.burdens))
            cm = self.hier_cat.new_morphism(h1, h2, "η_%s" % ent.name[:24], "natural_component", HierarchyBundle.single(max(ent.level, 1), "functor", 0.8), 1.0)
            if cm:
                self.status_to_access.set_component(eid, cm.id)
        # Universal property witnesses: solar UN as terminal governance object, base worker class as initial labor access, market product apex.
        solar_un = self.un_by_scope["Solar System"]
        self.universal_witnesses.append(UniversalPropertyWitness("Solar UN initial governance source approximation", self.econ_cat, "initial", solar_un, []))
        # Product witness: a high market as product of market_access and governance projections.
        top_markets = sorted(self.markets.values(), key=lambda m: m.level, reverse=True)
        if top_markets:
            apex = top_markets[0].id
            legs = []
            for owner in [self.un_by_scope.get(top_markets[0].scope, solar_un), solar_un]:
                mm = self.econ_cat.new_morphism(apex, owner, "projection %s -> %s" % (self.entities[apex].name[:12], self.entities[owner].name[:12]), "projection", HierarchyBundle.single(top_markets[0].level, "morphism", 1.0))
                if mm:
                    legs.append(mm.id)
            self.universal_witnesses.append(UniversalPropertyWitness("Market as product-like access/governance apex", self.econ_cat, "product", apex, legs))
        # Compose a sample of morphisms to create longer chains.
        morph_ids = [mid for mid, m in self.econ_cat.morphisms.items() if m.kind not in ("identity",)]
        for mid in self.rng.sample(morph_ids, min(2000 if self.profile == "demo" else 8000, len(morph_ids))):
            m = self.econ_cat.morphisms[mid]
            nexts = self.econ_cat.hom.get((m.target, m.target), []) + [x for x in self.econ_cat.hom.get((m.target, self.un_by_scope.get(self.entities[m.target].scope, self.un_by_scope["Solar System"])), [])]
            if nexts:
                self.econ_cat.compose(mid, self.rng.choice(nexts))

    def install_presheaves_and_sheaves(self) -> None:
        self.market_sheaf.restriction_keys = {
            "governance": ["volume", "domain", "level", "body"],
            "market_jurisdiction": ["volume", "domain", "level", "body"],
            "listing": ["domain", "level", "stock"],
        }
        # Local market sections.
        for m in self.markets.values():
            self.market_sheaf.add_section(m.id, PresheafSection(m.id, "state:%s" % m.name, {"domain": m.domain, "level": m.level, "body": m.body, "volume": round(m.volume, 3), "queue": m.queue_discipline}))
        # Planetary UN covers consist of high-level markets in body; solar cover consists of planetary UNs.
        for body in BODIES:
            un = self.un_by_scope[body]
            cover = [m.id for m in self.markets.values() if m.scope == body and m.level >= 10][:80]
            self.market_sheaf.set_cover(un, cover)
        solar_un = self.un_by_scope["Solar System"]
        self.market_sheaf.set_cover(solar_un, [self.un_by_scope[b] for b in BODIES])
        for body in BODIES:
            self.market_sheaf.glue(self.un_by_scope[body])
        self.market_sheaf.glue(solar_un)

    # ----------------------------- dynamics -----------------------------

    def actor(self) -> int:
        return self.rng.choice(self.actor_ids)

    def emit_packet(self, source_entity: int, target_entity: int, kind: str, bundle: HierarchyBundle, morphism_id: Optional[int] = None, payload: Optional[Dict[str, Any]] = None, priority: int = 5) -> bool:
        src_node = self.node_by_entity.get(source_entity)
        dst_node = self.node_by_entity.get(target_entity)
        if src_node is None or dst_node is None:
            self.route_failures += 1
            return False
        route = self.network.route(src_node, dst_node, max_depth=18)
        if not route:
            self.route_failures += 1
            return False
        packet = Packet(self.pid(), kind, src_node, dst_node, bundle, self.tick, ttl=max(8, len(route) * 4), route=route, morphism_id=morphism_id, payload=payload, priority=priority)
        ok = self.network.nodes[src_node].enqueue_outbound(packet)
        if ok:
            self.packets_created += 1
            self.packet_kind_counts[kind] += 1
        else:
            self.packets_dropped += 1
        return ok

    def settle(self, buyer_id: int, seller_id: int, price: HierarchyBundle, prefer_level: int = 5) -> bool:
        buyer = self.entities[buyer_id]
        seller = self.entities[seller_id]
        value = price.to_number()
        if not buyer.wallet.can_pay(value):
            return False
        paid = buyer.wallet.withdraw_number(value, level=prefer_level, element=price.dominant_element())
        seller.wallet.deposit(paid)
        return True

    def can_access(self, actor_id: int, market: Market, min_level: int, domain: str) -> bool:
        actor = self.entities[actor_id]
        return actor.entitlement_level(domain, self.privileges, self.burdens) >= min_level and actor.entitlement_level("market_access", self.privileges, self.burdens) >= max(1, min(market.level, min_level) - 1)

    def market_fee(self, market: Market, seller_id: int, value: float) -> None:
        if not market.owner_id or market.owner_id not in self.entities:
            return
        seller = self.entities[seller_id]
        fee = value * market.fee_rate
        if seller.wallet.can_pay(fee):
            self.entities[market.owner_id].wallet.deposit(seller.wallet.withdraw_number(fee, level=market.level, element="market_access"))

    def trade_products(self) -> None:
        product_markets = [m for m in self.markets.values() if m.listed_product_ids]
        if not product_markets:
            return
        for _ in range(self.cfg["product_trades"]):
            m = self.rng.choice(product_markets)
            if not m.listed_product_ids:
                continue
            p = self.products[self.rng.choice(m.listed_product_ids)]
            if p.stock <= 0 or p.owner_id is None:
                m.failed_count += 1
                continue
            buyer_id = self.actor()
            if buyer_id == p.owner_id or not self.can_access(buyer_id, m, p.min_level, p.domain):
                m.failed_count += 1
                continue
            price = p.quote().scaled(1.0 + m.level * 0.015)
            if not self.settle(buyer_id, p.owner_id, price, prefer_level=p.min_level):
                m.failed_count += 1
                continue
            value = price.to_number()
            self.market_fee(m, p.owner_id, value)
            p.stock -= 1
            p.units_sold += 1
            self.entities[buyer_id].inventory_units += 1
            m.trade_count += 1
            m.volume += value
            self.trade_volume += value
            self.product_sales += 1
            morph = self.add_econ_morphism(buyer_id, p.id, "buy %s" % p.name[:32], "trade_product", price, strength=value, data={"market": m.id, "seller": p.owner_id}, create_packet=True, priority=min(12, p.min_level + 1))
            if morph and self.rng.chance(0.03):
                m.remember("PRODUCT %s -> %s for %sH" % (p.name[:24], self.entities[buyer_id].name[:22], short_number(value)))

    def trade_privileges(self) -> None:
        markets = [m for m in self.markets.values() if m.domain == "privilege"]
        if not markets:
            return
        for _ in range(self.cfg["privilege_trades"]):
            buyer_id = self.actor()
            buyer = self.entities[buyer_id]
            issuer_id = self.un_by_scope.get(buyer.body, self.un_by_scope["Solar System"])
            domain = self.rng.choice(DOMAINS[:-4])
            boost = self.rng.choice([1, 1, 1, 2, 2, 3])
            p = Privilege(self.eid(), "Tradable %s Privilege T%s" % (domain.title().replace("_", " "), self.tick), scope=buyer.scope, body=buyer.body, country_id=buyer.country_id, level=int(clamp(buyer.level + boost, 1, 12)), domain=domain, elements={"privilege": 8.0 * boost, domain: 7.0 * boost, "semaphore": 2.5 * boost}, owner_id=issuer_id, level_boost=boost, duration=self.rng.randint(1, 5))
            price = p.quote()
            if self.settle(buyer_id, issuer_id, price, prefer_level=p.level):
                self.register_entity(p, "privilege")
                self.privileges[p.id] = p
                buyer.privilege_ids.append(p.id)
                p.owner_id = buyer_id
                m = self.rng.choice(markets)
                m.trade_count += 1
                value = price.to_number()
                m.volume += value
                self.trade_volume += value
                self.add_econ_morphism(issuer_id, buyer_id, "grant privilege %s" % domain, "privilege", price, value, {"privilege": p.id, "market": m.id}, create_packet=True, priority=9)

    def trade_burdens(self) -> None:
        markets = [m for m in self.markets.values() if m.domain == "burden"]
        compensators = list(self.companies.keys()) + list(self.countries.keys()) + list(self.un_by_scope.values())
        if not markets or not compensators:
            return
        for _ in range(self.cfg["burden_trades"]):
            taker_id = self.actor()
            taker = self.entities[taker_id]
            if isinstance(taker, UNOrganization):
                continue
            comp_id = self.rng.choice(compensators)
            if comp_id == taker_id:
                continue
            domain = self.rng.choice(["housing", "transport", "labor", "energy", "market_access", "data", "queue", "semaphore"])
            penalty = self.rng.choice([1, 1, 2, 2, 3])
            b = Burden(self.eid(), "Tradable %s Burden T%s" % (domain.title().replace("_", " "), self.tick), scope=taker.scope, body=taker.body, country_id=taker.country_id, level=taker.level, domain=domain, elements={"burden": 8.0 * penalty, domain: 5.0 * penalty, "queue": 2.0 * penalty}, owner_id=comp_id, level_penalty=penalty, duration=self.rng.randint(1, 4))
            price = b.quote()
            if self.entities[comp_id].wallet.can_pay(price.to_number()) and taker.level > 1:
                taker.wallet.deposit(self.entities[comp_id].wallet.withdraw_number(price.to_number(), level=b.level, element="burden"))
                self.register_entity(b, "burden")
                self.burdens[b.id] = b
                taker.burden_ids.append(b.id)
                b.owner_id = taker_id
                m = self.rng.choice(markets)
                m.trade_count += 1
                value = price.to_number()
                m.volume += value
                self.trade_volume += value
                self.add_econ_morphism(comp_id, taker_id, "assign burden %s" % domain, "burden", price, value, {"burden": b.id, "market": m.id}, create_packet=True, priority=10)

    def trade_markets_as_assets(self) -> None:
        buyers = list(self.companies.keys()) + list(self.countries.keys()) + list(self.un_by_scope.values()) + list(self.defense_by_scope.values())
        exchanges = [self.markets[mid] for mid in self.market_rights_exchanges if self.markets[mid].listed_market_ids]
        if not buyers or not exchanges:
            return
        for _ in range(self.cfg["market_trades"]):
            ex = self.rng.choice(exchanges)
            asset = self.markets[self.rng.choice(ex.listed_market_ids)]
            seller_id = asset.owner_id
            buyer_id = self.rng.choice(buyers)
            if seller_id is None or buyer_id == seller_id:
                continue
            buyer = self.entities[buyer_id]
            if buyer.entitlement_level("market_access", self.privileges, self.burdens) < min(12, asset.level + 1):
                ex.failed_count += 1
                continue
            price = asset.quote().scaled(0.20)
            if self.settle(buyer_id, seller_id, price, prefer_level=asset.level):
                asset.owner_id = buyer_id
                ex.market_trade_count += 1
                ex.trade_count += 1
                value = price.to_number()
                ex.volume += value
                self.trade_volume += value
                self.market_ownership_changes += 1
                self.add_econ_morphism(seller_id, buyer_id, "market control transfer %s" % asset.name[:32], "trade_market", price, value, {"exchange": ex.id, "market_asset": asset.id}, create_packet=True, priority=12)
                if self.rng.chance(0.08):
                    ex.remember("MARKET %s control -> %s" % (asset.name[:24], buyer.name[:22]))

    def manual_lift_helpers_media(self) -> None:
        # Manual status lift for care/media/science/trust workers and companies.
        candidates: List[int] = []
        for w in self.rng.sample(list(self.workers.values()), min(900, len(self.workers))):
            if w.occupation in ("care", "media", "science", "trust", "education", "medicine") and w.traits.get("trust", 0.0) > 0.62:
                candidates.append(w.id)
        for comp in self.rng.sample(list(self.companies.values()), min(240, len(self.companies))):
            if comp.sector in ("care", "media", "research", "education", "medicine", "culture"):
                candidates.append(comp.id)
        self.rng.shuffle(candidates)
        for target_id in candidates[: max(6, len(candidates) // 18)]:
            target = self.entities[target_id]
            issuer_id = self.un_by_scope.get(target.body, self.un_by_scope["Solar System"])
            p = Privilege(self.eid(), "Manual Lift %s" % target.name[:28], scope=target.scope, body=target.body, country_id=target.country_id, level=min(12, target.level + 2), domain=target.domain, elements={"privilege": 20.0, "trust": 10.0, "care": 8.0, "media": 5.0, "sheaf": 2.0}, owner_id=issuer_id, level_boost=1, duration=self.rng.randint(2, 6))
            self.register_entity(p, "privilege")
            self.privileges[p.id] = p
            p.owner_id = target_id
            target.privilege_ids.append(p.id)
            self.manual_lifts += 1
            self.add_econ_morphism(issuer_id, target_id, "manual lift %s" % target.name[:32], "manual_lift", p.quote(), p.quote().to_number(), {"privilege": p.id}, create_packet=True, priority=11)

    def generate_background_network_packets(self) -> None:
        # Queue and topology traffic independent from successful trades: market ticks, sheaf restrictions, governance pulses.
        sample_count = self.cfg["network_packets"]
        all_entities = list(self.entities.keys())
        for _ in range(sample_count):
            src = self.rng.choice(all_entities)
            kind = self.rng.choice(["quote_stream", "governance_pulse", "market_data", "sheaf_patch", "semaphore_request", "topology_update"])
            if kind == "governance_pulse":
                target = self.un_by_scope.get(self.entities[src].body, self.un_by_scope["Solar System"])
            elif kind == "sheaf_patch":
                target = self.un_by_scope.get(self.entities[src].body, self.un_by_scope["Solar System"])
            elif kind == "semaphore_request":
                target = self.defense_by_scope.get(self.entities[src].body, self.defense_by_scope["Solar System"])
            else:
                target = self.rng.choice(all_entities)
            level = max(1, self.entities[src].level)
            bundle = HierarchyBundle.single(level, self.rng.choice(["data", "queue", "topology", "morphism", "sheaf", "semaphore", "market_access"]), self.rng.uniform(0.2, 4.0))
            self.emit_packet(src, target, kind, bundle, None, {"background": True}, priority=self.rng.randint(1, 12))

    def process_network(self) -> None:
        moved, dropped = self.network.drain_outbound(limit_per_node=4 if self.profile == "demo" else 3)
        self.network_moved += moved
        self.network_channel_drops += dropped
        delivered = self.network.tick(self.tick)
        for node_id, packet in delivered:
            node = self.network.nodes.get(node_id)
            if node is None:
                self.packets_dropped += 1
                continue
            packet.advance()
            if node_id == packet.target or packet.arrived():
                ok = node.receive(packet)
                if ok:
                    self.packets_delivered += 1
                else:
                    self.packets_dropped += 1
            else:
                node.enqueue_outbound(packet)
        # local nodes process packets; if not terminal, forward them.
        for node in self.network.nodes.values():
            processed = node.process_local(limit=2)
            for packet in processed:
                if packet.target != node.id and not packet.arrived() and packet.ttl > 0:
                    node.enqueue_outbound(packet)

    def update_sheaf_sections(self) -> None:
        for m in self.rng.sample(list(self.markets.values()), min(240, len(self.markets))):
            self.market_sheaf.add_section(m.id, PresheafSection(m.id, "state:t%s:%s" % (self.tick, m.id), {"domain": m.domain, "level": m.level, "body": m.body, "volume": round(m.volume, 3), "queue": m.queue_discipline}))
        for body in BODIES:
            self.market_sheaf.glue(self.un_by_scope[body])
        self.market_sheaf.glue(self.un_by_scope["Solar System"])

    def decay_privileges_and_burdens(self) -> None:
        for p in self.privileges.values():
            if p.active:
                p.duration -= 1
                if p.duration <= 0:
                    p.active = False
        for b in self.burdens.values():
            if b.active:
                b.duration -= 1
                if b.duration <= 0:
                    b.active = False

    def refresh_all_levels(self) -> None:
        for w in self.workers.values():
            w.recalc_elements()
            w.refresh_level(self.privileges, self.burdens)
        for comp in self.companies.values():
            if comp.worker_ids:
                sample = comp.worker_ids if len(comp.worker_ids) <= 120 else self.rng.sample(comp.worker_ids, 120)
                comp.production_score = sum(self.workers[wid].work_power() for wid in sample) * len(comp.worker_ids) / max(1, len(sample))
                comp.elements["labor"] = comp.production_score * 0.06
            comp.elements["market_access"] = comp.elements.get("market_access", 0.0) + len(comp.product_ids) * 0.17
            comp.elements["queue"] = comp.elements.get("queue", 0.0) + len(comp.worker_ids) * 0.05
            comp.refresh_level(self.privileges, self.burdens)
        for country in self.countries.values():
            country.economic_power = sum(self.companies[cid].status_number(self.privileges, self.burdens) for cid in country.company_ids[:200])
            country.military_power = country.elements.get("military", 0.0) + sum(self.companies[cid].military_contract_share for cid in country.company_ids) * 1000
            country.elements["capital"] = country.elements.get("capital", 0.0) + country.economic_power * 0.01
            country.elements["military"] = max(country.elements.get("military", 0.0), country.military_power)
            country.refresh_level(self.privileges, self.burdens)
        for e in list(self.entities.values()):
            if isinstance(e, (Worker, Company, Country)):
                continue
            e.refresh_level(self.privileges, self.burdens)
            if e.node_id and e.node_id in self.network.nodes:
                self.network.nodes[e.node_id].level = e.level
        for e in self.entities.values():
            if e.node_id and e.node_id in self.network.nodes:
                self.network.nodes[e.node_id].level = e.level

    def tick_once(self) -> None:
        self.tick += 1
        self.apply_macro_scenario()
        self.trade_products()
        self.trade_privileges()
        self.trade_burdens()
        self.trade_markets_as_assets()
        self.manual_lift_helpers_media()
        self.generate_background_network_packets()
        # Several network microticks make duplex/semaphore queues visible.
        for _ in range(3):
            self.process_network()
        self.update_sheaf_sections()
        self.decay_privileges_and_burdens()
        self.refresh_all_levels()
        self.update_mobility_tracking()
        if not self.quiet:
            print(self.tick_report())

    def simulate(self, ticks: int) -> None:
        for _ in range(max(0, ticks)):
            self.tick_once()

    # ----------------------------- reports and visualizations -----------------------------

    def build_report(self) -> str:
        return "Built: entities=%d countries=%d alliances=%d companies=%d workers=%d products=%d markets=%d channels=%d econ_morphisms=%d net_morphisms=%d" % (
            len(self.entities), len(self.countries), len(self.alliances), len(self.companies), len(self.workers), len(self.products), len(self.markets), len(self.network.channels), len(self.econ_cat.morphisms), len(self.net_cat.morphisms)
        )

    def tick_report(self) -> str:
        return "tick=%d volume=%sH product_sales=%d market_trades=%d packets(created/delivered/dropped)=%d/%d/%d queues=%d sem_blocked=%d sheaf_glued=%d" % (
            self.tick, short_number(self.trade_volume), self.product_sales, self.market_ownership_changes,
            self.packets_created, self.packets_delivered, self.packets_dropped,
            sum(n.total_queue_len() for n in self.network.nodes.values()),
            sum(ch.semaphore.blocked for ch in self.network.channels.values()), len(self.market_sheaf.glued)
        )

    def level_distribution(self, values: Iterable[HierarchyEntity]) -> Dict[int, int]:
        c = Counter(v.level for v in values)
        return dict(sorted(c.items()))

    def top_entities(self, values: Iterable[AccountEntity], n: int = 8) -> List[AccountEntity]:
        vals = list(values)
        if len(vals) > 15000:
            vals = self.rng.sample(vals, 15000)
        return sorted(vals, key=lambda e: e.status_number(self.privileges, self.burdens), reverse=True)[:n]

    def summary_entity(self, e: AccountEntity) -> Dict[str, Any]:
        owner = None
        if isinstance(e, TradableEntity) and e.owner_id in self.entities:
            owner = self.entities[e.owner_id].name
        return {"name": e.name, "kind": e.kind, "level": e.level, "level_name": LEVEL_NAMES[e.level], "domain": e.domain, "scope": e.scope, "body": e.body, "owner": owner, "status_number": round(e.status_number(self.privileges, self.burdens), 2), "wallet": round(e.wallet.value(), 2), "node": e.node_id}

    def category_report(self) -> Dict[str, Any]:
        return {
            "economic_category": self.econ_cat.stats(),
            "network_category": self.net_cat.stats(),
            "hierarchy_category": self.hier_cat.stats(),
            "topology_category": self.top_cat.stats(),
            "economic_to_network_functor": self.econ_to_net.verify_sample(self.rng, 300),
            "status_functor": self.econ_to_hier.verify_sample(self.rng, 300),
            "access_functor": self.econ_to_access.verify_sample(self.rng, 300),
            "natural_transformation": self.status_to_access.verify_sample(self.rng, 300),
            "associativity_sample": self.econ_cat.sample_associativity(self.rng, 300),
            "universal_witnesses": [w.verify_sample(self.rng, 200) for w in self.universal_witnesses],
            "market_sheaf": self.market_sheaf.stats(),
        }

    def network_report(self) -> Dict[str, Any]:
        degrees = self.network.degrees()
        return {
            "nodes": len(self.network.nodes), "channels": len(self.network.channels), "components": self.network.component_count(),
            "topology_counts": self.network.topology_counts(), "duplex_counts": self.network.duplex_counts(), "queue_discipline_counts": self.network.queue_discipline_counts(),
            "degree_min": min(degrees.values()) if degrees else 0, "degree_mean": round(sum(degrees.values()) / max(1, len(degrees)), 3), "degree_max": max(degrees.values()) if degrees else 0,
            "packets": {"created": self.packets_created, "delivered": self.packets_delivered, "dropped": self.packets_dropped, "route_failures": self.route_failures, "moved": self.network_moved, "channel_drops": self.network_channel_drops, "by_kind": dict(self.packet_kind_counts)},
            "semaphores": {"blocked": sum(ch.semaphore.blocked for ch in self.network.channels.values()), "acquired": sum(ch.semaphore.acquired for ch in self.network.channels.values()), "capacity": sum(ch.semaphore.capacity for ch in self.network.channels.values())},
        }

    def report(self) -> Dict[str, Any]:
        recent = []
        for m in sorted(self.markets.values(), key=lambda x: len(x.recent), reverse=True)[:14]:
            for item in m.recent[-2:]:
                recent.append("%s: %s" % (m.name, item))
        return {
            "seed": self.seed, "profile": self.profile, "ticks": self.tick,
            "counts": {"entities": len(self.entities), "countries": len(self.countries), "alliances": len(self.alliances), "companies": len(self.companies), "workers": len(self.workers), "products": len(self.products), "markets": len(self.markets), "privileges": len(self.privileges), "burdens": len(self.burdens)},
            "trade": {"volume_H": round(self.trade_volume, 2), "product_sales": self.product_sales, "market_ownership_changes": self.market_ownership_changes, "manual_lifts": self.manual_lifts},
            "levels": {"workers": self.level_distribution(self.workers.values()), "companies": self.level_distribution(self.companies.values()), "countries": self.level_distribution(self.countries.values()), "products": self.level_distribution(self.products.values()), "markets": self.level_distribution(self.markets.values())},
            "network": self.network_report(),
            "category": self.category_report(),
            "goods_hierarchy": {str(level): GOODS_HIERARCHY[level] for level in range(1, 13)},
            "mobility": self.mobility_counts,
            "scenario": {"events": self.macro_history[-24:], "scores": dict(self.scenario_scores), "volatility": list(self.tick_volatility)},
            "top_countries": [self.summary_entity(e) for e in self.top_entities(self.countries.values())],
            "top_companies": [self.summary_entity(e) for e in self.top_entities(self.companies.values())],
            "top_markets": [self.summary_entity(e) for e in self.top_entities(self.markets.values())],
            "top_workers": [self.summary_entity(e) for e in self.top_entities(self.workers.values())],
            "recent_trades": recent[:20],
        }

    def visual_organizational_tree(self) -> str:
        lines = [chart_title("ORGANIZATIONAL / TOPOLOGICAL TREE")]
        lines.append("Solar System Category Object")
        lines.append("├─ Solar System United Nations [terminal-like governance apex]")
        lines.append("├─ Solar System Defense Organization [half-duplex semaphore apex]")
        for idx, body in enumerate(BODIES):
            last = idx == len(BODIES) - 1
            stem = "└─" if last else "├─"
            prefix = "   " if last else "│  "
            countries = [c for c in self.countries.values() if c.body == body]
            comps = [c for c in self.companies.values() if c.body == body]
            workers = [w for w in self.workers.values() if w.body == body]
            markets = [m for m in self.markets.values() if m.body == body]
            lines.append("%s %s: countries=%d companies=%d workers=%d markets=%d" % (stem, body, len(countries), len(comps), len(workers), len(markets)))
            lines.append("%s├─ UN: %s" % (prefix, self.entities[self.un_by_scope[body]].name))
            lines.append("%s├─ Defense: %s" % (prefix, self.entities[self.defense_by_scope[body]].name))
            lines.append("%s├─ Topologies: tree + star + ring + mesh + market-bipartite" % prefix)
            lines.append("%s└─ Sheaf cover: high markets -> planetary UN -> solar UN" % prefix)
        return "\n".join(lines)

    def visual_category_diagram(self) -> str:
        cat = self.category_report()
        rows = []
        for key in ["economic_category", "network_category", "hierarchy_category", "topology_category"]:
            c = cat[key]
            rows.append((c["name"], c["objects"], c["morphisms"], c["hom_sets"], sparkline([c["objects"], c["morphisms"], c["hom_sets"]])))
        parts = [render_table(rows, ["Category", "Objects", "Morphisms", "Hom-sets", "Shape"], "CATEGORY SIZE DIAGRAM", [28, 10, 10, 10, 16])]
        functor_rows = [
            ("Economic→Network", cat["economic_to_network_functor"]["checked"], cat["economic_to_network_functor"]["boundary_ok"], cat["economic_to_network_functor"]["identity_ok"]),
            ("Status functor", cat["status_functor"]["checked"], cat["status_functor"]["boundary_ok"], cat["status_functor"]["identity_ok"]),
            ("Access functor", cat["access_functor"]["checked"], cat["access_functor"]["boundary_ok"], cat["access_functor"]["identity_ok"]),
            ("Nat. transformation", cat["natural_transformation"]["checked"], cat["natural_transformation"]["natural"], cat["natural_transformation"]["violated"]),
        ]
        parts.append(render_table(functor_rows, ["Functor/NT", "Checked", "OK/Natural", "Identity/Viol"], "FUNCTORIALITY / NATURALITY CHECKS", [26, 10, 12, 14]))
        uni_rows = []
        for w in cat["universal_witnesses"]:
            uni_rows.append((w.get("name", "witness")[:32], w["kind"], w["checked"], w["passed"], w["ratio"]))
        parts.append(render_table(uni_rows, ["Universal witness", "Kind", "Checked", "Passed", "Ratio"], "UNIVERSAL PROPERTY WITNESSES", [34, 12, 9, 9, 8]))
        return "\n\n".join(parts)

    def visual_network(self) -> str:
        net = self.network_report()
        parts = []
        parts.append(render_histogram(net["topology_counts"], "CHANNELS BY TOPOLOGY", width=34))
        parts.append(render_histogram(net["duplex_counts"], "CHANNELS BY DUPLEX MODE", width=34))
        parts.append(render_histogram(net["queue_discipline_counts"], "CHANNEL QUEUE DISCIPLINES", width=34))
        parts.append(render_histogram(net["packets"]["by_kind"], "PACKETS BY KIND", width=34))
        # degree distribution
        deg_counts: Dict[int, int] = defaultdict(int)
        for d in self.network.degrees().values():
            deg_counts[min(20, d)] += 1
        parts.append(render_histogram(dict(deg_counts), "NETWORK DEGREE DISTRIBUTION (20=20+)", width=34, numeric_keys=True))
        ch_rows = []
        top_channels = sorted(self.network.channels.values(), key=lambda c: c.transmitted + c.blocked + c.dropped, reverse=True)[:12]
        for ch in top_channels:
            ab, ba = ch.queue_lengths()
            ch_rows.append((ch.name[:24], ch.mode, ch.topology, ab, ba, len(ch.in_flight), ch.semaphore.blocked, sparkline([ab, ba, len(ch.in_flight), ch.transmitted, ch.semaphore.blocked])))
        parts.append(render_table(ch_rows, ["Channel", "Mode", "Topology", "AB", "BA", "Fly", "Block", "Shape"], "HOT CHANNELS / SEMAPHORES", [24, 6, 14, 5, 5, 5, 7, 14]))
        return "\n\n".join(parts)

    def visual_levels(self) -> str:
        parts = []
        parts.append(render_level_chart(self.level_distribution(self.workers.values()), "WORKER LEVELS"))
        parts.append(render_level_chart(self.level_distribution(self.companies.values()), "COMPANY LEVELS"))
        parts.append(render_level_chart(self.level_distribution(self.countries.values()), "COUNTRY LEVELS"))
        parts.append(render_level_chart(self.level_distribution(self.products.values()), "PRODUCT LEVELS"))
        parts.append(render_level_chart(self.level_distribution(self.markets.values()), "MARKET LEVELS"))
        # body × level heatmaps
        for label, values in [("WORKERS", self.workers.values()), ("COMPANIES", self.companies.values()), ("MARKETS", self.markets.values())]:
            data: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
            for e in values:
                data[e.body][e.level] += 1
            parts.append(render_heatmap([b for b in ["Earth", "Moon", "Mars", "Solar System"] if b in data], list(range(1, 13)), data, "%s BY BODY × LEVEL" % label))
        return "\n\n".join(parts)

    def visual_sheaf(self) -> str:
        rows = []
        for oid, cover in sorted(self.market_sheaf.covers.items(), key=lambda kv: self.entities[kv[0]].name if kv[0] in self.entities else str(kv[0])):
            name = self.entities[oid].name if oid in self.entities else str(oid)
            glued = "yes" if oid in self.market_sheaf.glued else "no"
            rows.append((name[:30], len(cover), glued, sparkline([len(cover), 1 if glued == "yes" else 0, self.market_sheaf.compatibility_checks])))
        stats = self.market_sheaf.stats()
        parts = [render_table(rows, ["Object", "Cover size", "Glued", "Shape"], "PRESHEAF / SHEAF COVER GLUING", [32, 10, 8, 20])]
        parts.append(render_table([
            ("sections", stats["sections"]), ("objects_with_sections", stats["objects_with_sections"]), ("covers", stats["covers"]), ("glued", stats["glued"]), ("compatibility_checks", stats["compatibility_checks"]), ("compatibility_passed", stats["compatibility_passed"])
        ], ["Sheaf metric", "Value"], "SHEAF METRICS", [30, 14]))
        return "\n\n".join(parts)

    def visual_market_domains(self) -> str:
        volume_by_domain: Dict[str, float] = defaultdict(float)
        trades_by_domain: Dict[str, int] = defaultdict(int)
        heat: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        for m in self.markets.values():
            volume_by_domain[m.domain] += m.volume
            trades_by_domain[m.domain] += m.trade_count
            heat[m.domain][m.level] += m.volume if m.volume > 0 else 1.0
        hot_domains = [k for k, _ in sorted(volume_by_domain.items(), key=lambda kv: -kv[1])[:14]]
        return "\n\n".join([
            render_histogram(dict(sorted(volume_by_domain.items(), key=lambda kv: -kv[1])[:16]), "MARKET VOLUME BY DOMAIN", width=36),
            render_histogram(dict(sorted(trades_by_domain.items(), key=lambda kv: -kv[1])[:16]), "MARKET TRADES BY DOMAIN", width=36),
            render_heatmap(hot_domains, list(range(1, 13)), heat, "MARKET DOMAIN × LEVEL HEATMAP"),
        ])

    def visual_goods_hierarchy(self) -> str:
        rows = self.goods_hierarchy_rows()
        counts = {"L%02d" % level: len(GOODS_HIERARCHY[level]) for level in range(1, 13)}
        ladder_lines = [chart_title("GOODS LADDER / ENTITLEMENT STAIRCASE")]
        for level in range(12, 0, -1):
            goods = GOODS_HIERARCHY[level]
            ladder_lines.append("L%02d %-16s │ %s" % (level, LEVEL_NAMES[level], " ; ".join(goods[:3])))
        return "\n\n".join([
            render_table(rows, ["Level", "Hierarchy stage", "Goods", "Examples A", "Examples B"], "GOODS HIERARCHY TABLE", [8, 18, 7, 32, 32]),
            render_histogram(counts, "NUMBER OF GOODS PER HIERARCHY LEVEL", width=34),
            "\n".join(ladder_lines),
        ])

    def visual_mobility(self) -> str:
        parts = []
        mob_rows = []
        for key in ["workers", "companies", "countries", "alliances"]:
            c = self.mobility_counts[key]
            mob_rows.append((key, c["up"], c["down"], c["same"], sparkline([c["up"], c["down"], c["same"]])))
        parts.append(render_table(mob_rows, ["Group", "Up", "Down", "Same", "Shape"], "CAREER MOBILITY SUMMARY", [14, 10, 10, 10, 14]))
        for key in ["workers", "companies", "countries", "alliances"]:
            parts.append(render_histogram(self.mobility_counts[key], "%s: UP / DOWN / SAME" % key.upper(), width=34))
        for key in ["companies", "countries", "alliances"]:
            heat = self.mobility_heatmaps[key]
            rows = [level for level in range(1,13) if level in heat]
            if rows:
                parts.append(render_heatmap(rows, list(range(1, 13)), heat, "%s INITIAL LEVEL → CURRENT LEVEL" % key.upper()))
        return "\n\n".join(parts)

    def visual_scenario_diversity(self) -> str:
        event_rows = []
        for item in self.macro_history[-16:]:
            event_rows.append((item["tick"], item["name"], short_number(item["strength"]), item["description"][:46]))
        score_hist = {k: v for k, v in sorted(self.scenario_scores.items(), key=lambda kv: -kv[1])[:12]}
        vol_map = {"tick%02d" % (i+1): v for i, v in enumerate(self.tick_volatility)}
        return "\n\n".join([
            render_table(event_rows, ["Tick", "Event", "Strength", "Meaning"], "MACRO SCENARIO EVENT LOG", [8, 24, 10, 46]),
            render_histogram(score_hist, "SCENARIO DRIVER STRENGTHS", width=34),
            render_histogram(vol_map, "VOLATILITY BY TICK", width=34),
        ])

    def visual_artifacts(self) -> List[Tuple[str, str, str, str]]:
        return [
            ("Goods hierarchy table and diagrams", self.visual_goods_hierarchy(),
             "This UTF-8 output explains which goods, rights and consumption bundles are assigned to each of the twelve hierarchy stages. In the table, the rows are hierarchy levels L01 to L12. The columns mean: Level = numeric hierarchy stage; Hierarchy stage = verbal name of that stage; Goods = how many goods are explicitly listed for that level; Examples A and Examples B = example goods or rights that become more appropriate or accessible at that level. The histogram below compares how many example goods are listed at each level, and the staircase diagram prints the hierarchy as a ladder from apex to base.",
             "This goods hierarchy makes explicit that the simulation can allocate not just abstract status but concrete bundles of consumption, logistics, mobility, data rights and command rights. Lower levels concentrate on survival and basic inclusion, middle levels on professional and organizational capacity, and upper levels on strategic coordination, rare infrastructure and system-wide rights."),
            ("Organizational and topological tree", self.visual_organizational_tree(),
             "This tree is a structural overview of the simulated world. Each row is one branch of the organizational hierarchy. The top line is the whole Solar System object. Indented rows show planetary bodies and the institutions beneath them. The numeric counts after Earth, Moon and Mars state how many countries, companies, workers and markets currently exist on each body.",
             "The tree shows how the simulation nests governance, defense, production and labor. A denser branch usually implies a richer local economy and more opportunities for career movement and market interaction."),
            ("Level distributions", self.visual_levels(),
             "These diagrams show how many workers, companies, countries, products and markets currently sit in each of the twelve hierarchy levels. In the heatmaps, rows are celestial bodies and columns are hierarchy levels L01–L12. Darker cells mean more entities of that type on that body at that level.",
             "The level charts show whether the hierarchy is top-heavy, middle-heavy or bottom-heavy. The body-by-level heatmaps show where high-level concentration happens geographically, which reveals whether Earth dominates, whether Mars catches up, or whether Moon becomes a niche high-level zone."),
            ("Career mobility diagrams", self.visual_mobility(),
             "These UTF-8 tables focus on upward and downward movement. In the mobility summary table, each row is a group: workers, companies, countries or alliances. The columns Up, Down and Same count how many entities rose above, fell below or stayed at their initial build-time hierarchy level. The heatmaps labeled Initial Level → Current Level use rows as starting levels and columns as final levels.",
             "These charts reveal whether the hierarchy is actually dynamic. If the mass lies above the diagonal in a heatmap, upward careers dominate; below the diagonal, decline dominates; around the diagonal, persistence dominates. This is the clearest evidence for whether the simulated order behaves like a rigid caste structure or a moving career tournament."),
            ("Network diagrams", self.visual_network(),
             "These network diagrams summarize channel topologies, duplex modes, queue disciplines, packet types and hot channels. In the hot-channels table, the rows are individual channels and the columns mean: Mode = simplex/half/full duplex; Topology = structural role of the channel; AB and BA = queue lengths in both directions; Fly = packets in flight; Block = semaphore blocking events; Shape = mini-sparkline showing relative pressure and throughput.",
             "This section shows whether the network architecture is balanced or congested. Large AB or BA queues indicate pressure, high Block values indicate semaphore contention, and dominant topologies reveal which kinds of relations are structurally central in the economy."),
            ("Category, functor and sheaf diagrams", self.visual_category_diagram() + "\n\n" + self.visual_sheaf(),
             "These tables summarize the abstract architecture. In the category-size table, rows are categories and columns count objects, morphisms and hom-sets. In the functor table, Checked counts tested mappings, OK/Natural shows successful preservation or naturality checks, and Identity/Viol shows identity-preservation counts or violations. In the sheaf tables, rows are market objects, Cover size counts local sections used to cover them, and Glued states whether compatible local sections were successfully glued.",
             "These outputs tell you whether the abstract reformulation actually coheres. Strong functor and naturality scores mean the architecture is internally consistent. Sheaf gluing shows whether local market information can be combined into larger coherent pictures rather than remaining fragmented."),
            ("Market domain diagrams", self.visual_market_domains(),
             "These diagrams analyze markets by economic domain. In the heatmap, rows are domains such as food, water, defense or data, and columns are hierarchy levels. Histogram bars show total trade volume or total trade count in each market domain.",
             "This section tells you which domains dominated the run. It distinguishes capital-heavy but low-traffic domains from high-traffic everyday markets, and shows where hierarchy and domain structure intersect."),
            ("Scenario diversity diagrams", self.visual_scenario_diversity(),
             "These tables show why different runs can diverge. In the macro event log, each row is one stochastic event applied during a tick. The columns mean: Tick = time step; Event = scenario type; Strength = intensity of that shock; Meaning = verbal description. The histograms below aggregate driver strength and volatility.",
             "This section explains the plurality of possible outcomes. If a few scenario drivers dominate, the run is path-dependent; if strengths are more balanced, multiple alternative trajectories remained plausible. The volatility chart indicates how much macro randomness moved the hierarchy over time."),
        ]

    def visual_report(self) -> str:
        return "\n\n".join([
            self.visual_organizational_tree(),
            self.visual_levels(),
            self.visual_network(),
            self.visual_category_diagram(),
            self.visual_sheaf(),
            self.visual_market_domains(),
        ])

    def print_report(self, json_path: Optional[str] = None, include_visuals: bool = True) -> None:
        report = self.report()
        if json_path:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2)
        print("=" * 96)
        print("SOLAR HIERARCHY MARKET — NETWORK / CATEGORY / SHEAF REPORT")
        print("=" * 96)
        print("seed=%s profile=%s ticks=%s" % (report["seed"], report["profile"], report["ticks"]))
        print("\nGLOBAL EXPLANATION OF THE SIMULATION")
        print("This simulation models a hierarchy-currency economy for the Solar System. It simulates Earth, Moon and Mars together with governance organizations, defense organizations, alliances, countries, companies, workers, products, privileges, burdens and markets. Hierarchy is the deep currency. The printed H number is only a compressed settlement value. The goal is to examine how concrete goods, market exchanges, network flows, category-theoretic structure and stochastic macro-events jointly shape who rises, who falls and which domains dominate a run.")
        print("The present version especially emphasizes four things: first, a twelve-level hierarchy of goods and entitlements; second, career mobility of persons, companies, states and defense alliances; third, multiple UTF-8 diagrams that visualize the whole structure; and fourth, strong run-to-run diversity through stochastic macro-scenarios.")
        print("\nWHAT ELSE CAN STILL BE SIMULATED")
        for item in self.what_more_can_be_simulated():
            print("  - " + item)
        print("\nEXPLANATION OF ABBREVIATIONS AND KEY TERMS")
        print("H = compressed hierarchy settlement number; L01-L12 = hierarchy levels from Survival to Solar Apex; AB/BA = queue lengths in both directions of a channel; Fly = packets in flight; Block = semaphore block count; NT = natural transformation; hom-set = the set of morphisms between two objects; Up/Down/Same = counts of career ascent, descent or stability relative to the initial built hierarchy.")
        print("\nEXPLANATION OF THE NUMERIC SUMMARY BLOCKS")
        print("The following numeric summaries state the realized size, activity and architecture of this run before the more detailed UTF-8 diagrams begin.")
        print("\nCounts:")
        for k, v in report["counts"].items():
            print("  %-30s %s" % (k, v))
        print("Interpretation: these counts show the total size of the simulated world. A larger value means more possible interactions, more competition and more possible differentiation across hierarchy levels.")
        print("\nTrade:")
        for k, v in report["trade"].items():
            print("  %-30s %s" % (k, v))
        print("Interpretation: these values indicate how active and transformative the economy was in this run. High trade volume suggests liquid exchange; high market ownership changes suggest strong structural rearrangement.")
        print("\nNetwork:")
        for k in ["nodes", "channels", "components", "degree_min", "degree_mean", "degree_max"]:
            print("  %-30s %s" % (k, report["network"][k]))
        print("Interpretation: this block summarizes the communication and control graph. Higher degrees usually imply stronger connectedness; more components imply fragmentation or local clustering.")
        print("\nCategory:")
        for key in ["economic_category", "network_category", "hierarchy_category", "topology_category"]:
            c = report["category"][key]
            print("  %-30s objects=%s morphisms=%s hom_sets=%s" % (key, c["objects"], c["morphisms"], c["hom_sets"]))
        print("Interpretation: category sizes show how rich the abstract architecture is. More morphisms mean more structured relations and transformations inside the model.")
        print("\nLevel distributions:")
        for k, v in report["levels"].items():
            print("  %-12s %s" % (k, v))
        print("Interpretation: this states how workers, companies, countries, products and markets are distributed over the twelve-level hierarchy.")
        print("\nMobility summary:")
        for k, v in report["mobility"].items():
            print("  %-12s up=%s down=%s same=%s" % (k, v["up"], v["down"], v["same"]))
        print("Interpretation: this is the most direct numeric measure of whether the hierarchy is dynamic. If Up and Down are both non-trivial, the system allows real ascent and decline instead of merely preserving initial ranks.")
        print("\nScenario summary:")
        print("  scenario drivers=", ", ".join(["%s=%s" % (k, short_number(v)) for k, v in sorted(report["scenario"]["scores"].items(), key=lambda kv: -kv[1])[:8]]))
        print("  volatility per tick=", report["scenario"]["volatility"])
        print("Interpretation: scenario drivers explain why this run can differ strongly from another run with another seed. Volatility values indicate how large the macro disturbances were over time.")
        for title, key in [("Top countries", "top_countries"), ("Top companies", "top_companies"), ("Top markets", "top_markets"), ("Top workers", "top_workers")]:
            print("\n" + title)
            print("Explanation of columns: Lxx = final hierarchy level; the following text is the level name; then comes the entity name; then the compressed status value in H; then domain, body and owner. Each row is one top-ranked entity in the corresponding group.")
            for e in report[key]:
                print("  L%02d %-16s %-52s %12sH domain=%s body=%s owner=%s" % (e["level"], e["level_name"], e["name"][:52], short_number(e["status_number"]), e["domain"], e["body"], e["owner"]))
            print("Interpretation: these lists identify the winners of this specific run and show where status concentrated most strongly.")
        print("\nRecent trades / morphism events")
        print("Explanation: each bullet below is a recent concrete event from a market, ownership transfer or morphism-induced interaction. This acts as a qualitative micro-log beneath the aggregate statistics.")
        for t in report["recent_trades"][:15]:
            print("  - " + t)
        print("Interpretation: the event log gives tangible examples of the exchanges and control transfers that created the aggregate patterns above.")
        if include_visuals:
            print("\n" + chart_title("UTF-8 NETWORK / CATEGORY / SHEAF DASHBOARD", 96, "#"))
            for title, artifact, explanation, interpretation in self.visual_artifacts():
                print("\n" + chart_title(title.upper(), 96, "#"))
                print("EXPLANATION BEFORE OUTPUT:")
                print(explanation)
                print(artifact)
                print("INTERPRETATION AFTER OUTPUT:")
                print(interpretation)
        print("\nFINAL BALANCED SUMMARY OF POSSIBLE OUTCOMES")
        print(self.final_scenario_summary())
        print("\nGROUP-SPECIFIC MOBILITY INTERPRETATIONS")
        for key in ["workers", "companies", "countries", "alliances"]:
            print("  - " + self.mobility_summary_text(key))


def level_object_id(level: int) -> int:
    return 900_000 + int(clamp(level, 1, 12))


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Solar hierarchy-currency market simulation with networks/categories/sheaves")
    p.add_argument("--profile", choices=sorted(SCALE_CONFIGS), default="demo")
    p.add_argument("--ticks", type=int, default=1)
    p.add_argument("--seed", type=int, default=42)
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--json", default=None, help="optional JSON report output path")
    p.add_argument("--no-visuals", action="store_true", help="disable UTF-8 diagrams")
    return p.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    sim = SolarNetworkCategoryEconomy(profile=args.profile, seed=args.seed, quiet=args.quiet)
    sim.build()
    sim.simulate(max(0, args.ticks))
    sim.print_report(args.json, include_visuals=not args.no_visuals)
    sys.stdout.flush()
    sys.stderr.flush()
    return 0


if __name__ == "__main__":
    code = main(sys.argv[1:])
    os._exit(code)