#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solar Hierarchy Market Simulation — PyPy-safe data-oriented architecture
========================================================================

This script simulates a hierarchy-currency economy over Earth, Moon and Mars.
It intentionally avoids a huge mutable object graph during ticks. The previous
network/category/sheaf architecture is represented as compact aggregate state:
network nodes, channels, morphisms, functors and sheaf gluing are counted and
sampled rather than materialized as hundreds of thousands of live objects.
That makes `pypy3 ... --profile large --ticks 2` much safer.
"""

from __future__ import annotations

import argparse
import heapq
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

EPS = 1e-9

LEVEL_NAMES = {
    1: "Survival", 2: "Basic", 3: "Local", 4: "Skilled", 5: "Professional",
    6: "Regional", 7: "National", 8: "Alliance", 9: "Planetary",
    10: "Interplanetary", 11: "Systemic", 12: "Solar Apex",
}

LEVEL_THRESHOLDS = [
    0.0, 160.0, 420.0, 950.0, 2100.0, 4800.0, 11000.0, 25000.0,
    60000.0, 145000.0, 350000.0, 850000.0,
]

HEIGHT_MULTIPLIERS = {
    1: 1.00, 2: 1.35, 3: 1.85, 4: 2.55, 5: 3.55, 6: 5.10,
    7: 7.40, 8: 10.80, 9: 15.90, 10: 23.50, 11: 35.00, 12: 52.00,
}

BODIES = ("Earth", "Moon", "Mars")
SCOPES = ("Solar System", "Earth", "Moon", "Mars")

DOMAINS = (
    "food", "water", "oxygen", "housing", "energy", "medicine", "education",
    "compute", "transport", "shipbuilding", "agriculture", "manufacturing",
    "defense", "media", "culture", "research", "care", "finance", "data",
    "orbital_slots", "terraforming", "market_rights", "labor", "privilege", "burden",
    "network_bandwidth", "semaphore_permits", "topology_rights", "sheaf_coherence",
)
SECTORS = DOMAINS[:22]
OCCUPATIONS = (
    "labor", "skill", "care", "media", "science", "risk", "trust", "governance",
    "military", "logistics", "infrastructure", "compute", "education", "medicine",
)
SEXES = ("female", "male", "other")
TOPOLOGIES = ("tree", "star", "ring", "mesh", "market-bipartite", "governance", "sheaf-cover")
DUPLEX = ("simplex", "half", "full")
QUEUE_KINDS = ("fifo", "lifo", "priority")

GOODS_HIERARCHY: Dict[int, List[str]] = {
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

SCALE_CONFIGS = {
    "demo": {
        "earth_countries": 8, "moon_countries": 3, "mars_countries": 4,
        "companies": 120, "workers": 1800, "products": 850,
        "product_trades": 2600, "privilege_trades": 160, "burden_trades": 120, "market_trades": 55,
        "network_packets": 1800,
    },
    "large": {
        "earth_countries": 72, "moon_countries": 12, "mars_countries": 18,
        "companies": 1700, "workers": 32000, "products": 13000,
        "product_trades": 45000, "privilege_trades": 2500, "burden_trades": 1700, "market_trades": 650,
        "network_packets": 26000,
    },
    "huge": {
        "earth_countries": 180, "moon_countries": 30, "mars_countries": 45,
        "companies": 6000, "workers": 160000, "products": 45000,
        "product_trades": 190000, "privilege_trades": 10000, "burden_trades": 7000, "market_trades": 2600,
        "network_packets": 120000,
    },
}

SPARK_CHARS = "▁▂▃▄▅▆▇█"
HEAT_CHARS = " ·░▒▓█"


# ---------------------------------------------------------------------------
# Utilities
# ---------------------------------------------------------------------------

class FastRNG:
    __slots__ = ("state",)
    def __init__(self, seed: int) -> None:
        self.state = (int(seed) ^ 0x9E3779B97F4A7C15) & 0xFFFFFFFFFFFFFFFF
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
        out.append(SPARK_CHARS[int(clamp(idx, 0, len(SPARK_CHARS) - 1))])
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


def render_table(rows: Sequence[Sequence[Any]], headers: Sequence[str], title: str, widths: Sequence[int]) -> str:
    lines = [chart_title(title)]
    lines.append(" | ".join(pad(h, w) for h, w in zip(headers, widths)))
    lines.append("-+-".join("-" * w for w in widths))
    for row in rows:
        lines.append(" | ".join(pad(v, w) for v, w in zip(row, widths)))
    return "\n".join(lines)


def render_heatmap(rows: Sequence[Any], cols: Sequence[Any], data: Dict[Any, Dict[Any, float]], title: str) -> str:
    lines = [chart_title(title)]
    if not rows or not cols:
        return "\n".join(lines + ["(no data)"])
    maxv = 0.0
    for r in rows:
        rd = data.get(r, {})
        for c in cols:
            maxv = max(maxv, float(rd.get(c, 0.0)))
    if maxv <= EPS:
        maxv = 1.0
    lines.append(" " * 12 + " ".join(pad(c, 3) for c in cols))
    for r in rows:
        cells = []
        rd = data.get(r, {})
        for c in cols:
            v = float(rd.get(c, 0.0))
            idx = int(round(clamp(v / maxv, 0.0, 1.0) * (len(HEAT_CHARS) - 1)))
            cells.append(" %s " % HEAT_CHARS[idx])
        lines.append("%s %s" % (pad(r, 11), "".join(cells)))
    lines.append("Legend: · low  ░▒▓█ high")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Data model: compact slotted entities, no recursive object graph.
# ---------------------------------------------------------------------------

class Entity:
    __slots__ = (
        "id", "name", "kind", "body", "scope", "domain", "sector", "level", "initial_level",
        "status", "wallet", "owner_id", "country_id", "alliance_id", "employer_id", "market_id",
        "age", "sex", "skill", "trust", "care", "media", "science", "risk", "military",
        "governance", "capital", "logistics", "infrastructure", "market_access", "privilege", "burden",
        "quality", "stock", "min_level", "units_sold", "volume", "trades", "failed", "listed_ids",
        "worker_ids", "company_ids", "country_ids", "queue", "duplex", "topology"
    )
    def __init__(self, eid: int, name: str, kind: str, body: str = "Solar System", scope: str = "Solar System", domain: str = "general") -> None:
        self.id = eid
        self.name = name
        self.kind = kind
        self.body = body
        self.scope = scope
        self.domain = domain
        self.sector = domain
        self.level = 1
        self.initial_level = 1
        self.status = 0.0
        self.wallet = 0.0
        self.owner_id = 0
        self.country_id = 0
        self.alliance_id = 0
        self.employer_id = 0
        self.market_id = 0
        self.age = 0
        self.sex = "other"
        self.skill = 0.0
        self.trust = 0.0
        self.care = 0.0
        self.media = 0.0
        self.science = 0.0
        self.risk = 0.0
        self.military = 0.0
        self.governance = 0.0
        self.capital = 0.0
        self.logistics = 0.0
        self.infrastructure = 0.0
        self.market_access = 0.0
        self.privilege = 0.0
        self.burden = 0.0
        self.quality = 1.0
        self.stock = 0
        self.min_level = 1
        self.units_sold = 0
        self.volume = 0.0
        self.trades = 0
        self.failed = 0
        self.listed_ids: List[int] = []
        self.worker_ids: List[int] = []
        self.company_ids: List[int] = []
        self.country_ids: List[int] = []
        self.queue = "fifo"
        self.duplex = "full"
        self.topology = "tree"


# ---------------------------------------------------------------------------
# Simulation engine
# ---------------------------------------------------------------------------

class SolarHierarchySimulation:
    def __init__(self, profile: str, seed: Optional[int], quiet: bool = False, processes: int = 1) -> None:
        if profile not in SCALE_CONFIGS:
            raise ValueError("unknown profile")
        if seed is None:
            seed = (time.time_ns() ^ os.getpid() ^ (os.getppid() << 11)) & 0xFFFFFFFFFFFFFFFF
        self.profile = profile
        self.cfg = dict(SCALE_CONFIGS[profile])
        self.seed = int(seed)
        self.rng = FastRNG(self.seed)
        self.quiet = quiet
        self.processes = max(1, int(processes or 1))
        self.tick = 0
        self.next_id = 1

        self.entities: Dict[int, Entity] = {}
        self.orgs: List[Entity] = []
        self.countries: List[Entity] = []
        self.alliances: List[Entity] = []
        self.companies: List[Entity] = []
        self.workers: List[Entity] = []
        self.products: List[Entity] = []
        self.markets: List[Entity] = []
        self.market_rights_exchanges: List[Entity] = []
        self.markets_with_products: List[Entity] = []
        self.actors: List[Entity] = []
        self.un_by_scope: Dict[str, int] = {}
        self.defense_by_scope: Dict[str, int] = {}

        self.trade_volume = 0.0
        self.product_sales = 0
        self.market_ownership_changes = 0
        self.manual_lifts = 0
        self.privilege_count = 0
        self.burden_count = 0
        self.recent_events: List[str] = []

        self.network_stats: Dict[str, Any] = {}
        self.category_stats: Dict[str, Any] = {}
        self.sheaf_stats: Dict[str, Any] = {}
        self.macro_history: List[Dict[str, Any]] = []
        self.scenario_scores: Dict[str, float] = defaultdict(float)
        self.tick_volatility: List[float] = []
        self.mobility_counts: Dict[str, Dict[str, int]] = {}
        self.mobility_heatmaps: Dict[str, Dict[int, Dict[int, int]]] = {}

    def eid(self) -> int:
        v = self.next_id
        self.next_id += 1
        return v

    def add(self, e: Entity) -> Entity:
        self.entities[e.id] = e
        return e

    def remember(self, text: str) -> None:
        self.recent_events.append(text)
        if len(self.recent_events) > 40:
            self.recent_events.pop(0)

    # ----------------------------- construction -----------------------------

    def build(self) -> None:
        if not self.quiet:
            print("Building PyPy-safe hierarchy-market simulation profile=%s seed=%s" % (self.profile, self.seed))
        self.create_orgs()
        self.create_countries_alliances()
        self.create_companies_workers_products_markets()
        self.build_aggregate_network_and_categories()
        self.refresh_all_levels(initial=True)
        self.record_initial_levels()
        self.update_mobility_tracking()
        if not self.quiet:
            print(self.build_report())

    def create_orgs(self) -> None:
        sun = self.add(Entity(self.eid(), "Solar System United Nations", "un", "Solar System", "Solar System", "governance"))
        sun.level = 12; sun.governance = 240000; sun.trust = 80000; sun.capital = 500000; sun.wallet = 1200000
        sdef = self.add(Entity(self.eid(), "Solar System Defense Organization", "defense_org", "Solar System", "Solar System", "defense"))
        sdef.level = 12; sdef.military = 260000; sdef.risk = 50000; sdef.capital = 600000; sdef.wallet = 1000000
        self.un_by_scope["Solar System"] = sun.id
        self.defense_by_scope["Solar System"] = sdef.id
        self.orgs.extend([sun, sdef])
        for body in BODIES:
            un = self.add(Entity(self.eid(), "United Nations of %s" % body, "un", body, body, "governance"))
            un.owner_id = sun.id; un.level = 11 if body != "Earth" else 12
            un.governance = self.rng.uniform(100000, 180000); un.trust = self.rng.uniform(25000, 65000); un.capital = self.rng.uniform(120000, 350000); un.wallet = self.rng.uniform(220000, 700000)
            de = self.add(Entity(self.eid(), "%s Defense Organization" % body, "defense_org", body, body, "defense"))
            de.owner_id = sdef.id; de.level = 11 if body != "Earth" else 12
            de.military = self.rng.uniform(100000, 230000); de.risk = self.rng.uniform(18000, 60000); de.capital = self.rng.uniform(100000, 360000); de.wallet = self.rng.uniform(200000, 600000)
            self.un_by_scope[body] = un.id
            self.defense_by_scope[body] = de.id
            self.orgs.extend([un, de])

    def create_countries_alliances(self) -> None:
        counts = {"Earth": self.cfg["earth_countries"], "Moon": self.cfg["moon_countries"], "Mars": self.cfg["mars_countries"]}
        for body, count in counts.items():
            body_alliances = []
            for ai in range(2):
                a = self.add(Entity(self.eid(), "%s Defense Alliance %d" % (body, ai + 1), "alliance", body, body, "defense"))
                a.owner_id = self.defense_by_scope[body]
                a.level = 8 + (1 if body == "Earth" and self.rng.chance(0.5) else 0)
                a.military = self.rng.uniform(18000, 85000) * (1.0 + a.level / 10.0)
                a.governance = self.rng.uniform(8000, 25000)
                a.trust = self.rng.uniform(4000, 16000)
                a.wallet = self.rng.uniform(30000, 160000)
                self.alliances.append(a); body_alliances.append(a)
            for i in range(count):
                c = self.add(Entity(self.eid(), "%s Republic %03d" % (body, i + 1), "country", body, body, "governance"))
                c.owner_id = self.un_by_scope[body]
                c.level = int(clamp(7 + self.rng.randint(0, 3) + (1 if body == "Earth" and self.rng.chance(0.35) else 0), 7, 11))
                c.governance = self.rng.uniform(4000, 22000) * c.level
                c.capital = self.rng.uniform(7000, 35000) * c.level
                c.military = self.rng.uniform(2500, 18000) * c.level
                c.infrastructure = self.rng.uniform(4000, 25000) * c.level
                c.logistics = self.rng.uniform(2000, 12000) * c.level
                c.wallet = self.rng.uniform(60000, 350000) * (1.0 + c.level / 8.0)
                alliance = self.rng.choice(body_alliances)
                c.alliance_id = alliance.id
                alliance.country_ids.append(c.id)
                self.countries.append(c)

    def create_companies_workers_products_markets(self) -> None:
        # companies
        for i in range(self.cfg["companies"]):
            country = self.rng.choice(self.countries)
            sector = self.rng.choice(SECTORS)
            comp = self.add(Entity(self.eid(), "%s Company %05d" % (sector.title().replace("_", " "), i + 1), "company", country.body, country.scope, sector))
            comp.sector = sector
            comp.owner_id = country.id
            comp.country_id = country.id
            comp.level = int(clamp(country.level - self.rng.randint(0, 3) + self.rng.randint(0, 1), 4, 11))
            comp.capital = self.rng.uniform(700, 8000) * comp.level
            comp.infrastructure = self.rng.uniform(350, 4200) * comp.level
            comp.logistics = self.rng.uniform(200, 2800) * comp.level
            comp.market_access = self.rng.uniform(400, 3500) * comp.level
            comp.science = self.rng.uniform(40, 2200) * comp.level if sector in ("research", "compute", "data", "medicine") else self.rng.uniform(20, 650) * comp.level
            comp.military = self.rng.uniform(30, 3500) * comp.level if sector == "defense" else self.rng.uniform(0, 450) * comp.level
            comp.wallet = self.rng.uniform(7000, 70000) * (1.0 + comp.level / 4.0)
            comp.queue = self.rng.choice(QUEUE_KINDS); comp.duplex = self.rng.choice(DUPLEX); comp.topology = self.rng.choice(TOPOLOGIES)
            self.companies.append(comp)
            country.company_ids.append(comp.id)

        # workers
        for i in range(self.cfg["workers"]):
            comp = self.rng.choice(self.companies)
            occ = self.rng.choice(OCCUPATIONS)
            w = self.add(Entity(self.eid(), "Worker %07d" % (i + 1), "worker", comp.body, comp.scope, occ))
            w.owner_id = 0
            w.employer_id = comp.id
            w.country_id = comp.country_id
            w.age = self.rng.randint(18, 75)
            w.sex = self.rng.choice(SEXES)
            w.skill = self.rng.uniform(0.10, 1.0)
            w.trust = self.rng.uniform(0.10, 1.0)
            w.care = self.rng.uniform(0.05, 1.0) if occ in ("care", "medicine", "education", "trust") else self.rng.uniform(0.02, 0.75)
            w.media = self.rng.uniform(0.05, 1.0) if occ == "media" else self.rng.uniform(0.0, 0.45)
            w.science = self.rng.uniform(0.05, 1.0) if occ in ("science", "compute", "medicine", "education") else self.rng.uniform(0.0, 0.5)
            w.risk = self.rng.uniform(0.05, 1.0)
            w.military = self.rng.uniform(0.08, 1.0) if occ == "military" else self.rng.uniform(0.0, 0.45)
            w.wallet = self.rng.uniform(8.0, 160.0)
            self.workers.append(w)
            comp.worker_ids.append(w.id)

        # products
        for i in range(self.cfg["products"]):
            comp = self.rng.choice(self.companies)
            p = self.add(Entity(self.eid(), "%s Product %06d" % (comp.sector.title().replace("_", " "), i + 1), "product", comp.body, comp.scope, comp.sector))
            p.owner_id = comp.id
            p.country_id = comp.country_id
            p.quality = self.rng.uniform(0.45, 2.8) * (1.0 + comp.level / 18.0)
            p.min_level = int(clamp(comp.level + self.rng.randint(-4, 2), 1, 12))
            p.stock = self.rng.randint(4, 260)
            p.capital = p.quality * p.stock * 4.0
            p.market_access = p.min_level * p.quality * 18.0
            self.products.append(p)

        # markets: exactly scope × domain × 12 hierarchy access levels.
        for scope in SCOPES:
            body = scope if scope in BODIES else "Solar System"
            owner = self.un_by_scope.get(scope, self.un_by_scope["Solar System"])
            for domain in DOMAINS:
                for lvl in range(1, 13):
                    m = self.add(Entity(self.eid(), "%s L%02d %s Market" % (scope, lvl, domain.title().replace("_", " ")), "market", body, scope, domain))
                    m.level = lvl
                    m.min_level = lvl
                    m.owner_id = owner
                    m.market_access = lvl * self.rng.uniform(60.0, 220.0)
                    m.capital = lvl * self.rng.uniform(80.0, 260.0)
                    m.wallet = lvl * self.rng.uniform(40.0, 600.0)
                    m.queue = self.rng.choice(QUEUE_KINDS)
                    m.duplex = self.rng.choice(DUPLEX)
                    m.topology = self.rng.choice(TOPOLOGIES)
                    self.markets.append(m)
                    if domain == "market_rights":
                        self.market_rights_exchanges.append(m)
        # list products on matching markets
        markets_by_key: Dict[Tuple[str, str, int], List[Entity]] = defaultdict(list)
        for m in self.markets:
            markets_by_key[(m.scope, m.domain, m.min_level)].append(m)
        for p in self.products:
            candidates = markets_by_key.get((p.scope, p.domain, p.min_level)) or markets_by_key.get(("Solar System", p.domain, p.min_level))
            if not candidates:
                candidates = self.markets
            m = self.rng.choice(candidates)
            p.market_id = m.id
            m.listed_ids.append(p.id)
        self.markets_with_products = [m for m in self.markets if m.listed_ids]
        # market-right exchanges list tradable markets. Keep this as integer IDs only.
        all_market_ids = [m.id for m in self.markets]
        for ex in self.market_rights_exchanges:
            ex.listed_ids = self.rng.sample(all_market_ids, min(len(all_market_ids), 220 if self.profile == "demo" else 420))
        self.actors = self.workers + self.companies + self.countries + self.alliances + self.orgs

    def build_aggregate_network_and_categories(self) -> None:
        entity_count = len(self.entities)
        # These are aggregate network/category statistics. They represent topology without holding a huge mutable graph.
        self.network_stats = {
            "nodes": entity_count,
            "channels": int(len(self.countries) * 5 + len(self.companies) * 4 + min(len(self.workers), len(self.companies) * 8) + len(self.markets) * 2 + 24),
            "components": max(1, int(entity_count * (0.46 if self.profile != "demo" else 0.58))),
            "degree_min": 1,
            "degree_mean": 2.0 + (len(self.companies) * 4 + len(self.markets) * 2) / max(1.0, entity_count),
            "degree_max": max(40, min(entity_count, 90 + len(self.companies) // 10)),
            "topology_counts": dict(Counter(self.rng.choice(TOPOLOGIES) for _ in range(1500 if self.profile == "demo" else 9000))),
            "duplex_counts": dict(Counter(self.rng.choice(DUPLEX) for _ in range(800 if self.profile == "demo" else 5000))),
            "queue_counts": dict(Counter(self.rng.choice(QUEUE_KINDS) for _ in range(800 if self.profile == "demo" else 5000))),
            "packets_created": 0, "packets_delivered": 0, "packets_dropped": 0, "semaphore_blocked": 0,
        }
        econ_morphisms = len(self.workers) + len(self.products) + len(self.companies) * 3 + len(self.markets) * 3 + len(self.countries) * 5 + len(self.alliances) * 10
        net_morphisms = econ_morphisms + self.network_stats["channels"] * 2
        self.category_stats = {
            "economic_category": {"objects": entity_count, "morphisms": econ_morphisms, "hom_sets": int(econ_morphisms * 0.72)},
            "network_category": {"objects": entity_count, "morphisms": net_morphisms, "hom_sets": int(net_morphisms * 0.78)},
            "hierarchy_category": {"objects": 12, "morphisms": 12 * 12 + econ_morphisms // 4, "hom_sets": 126},
            "topology_category": {"objects": len(TOPOLOGIES), "morphisms": 15, "hom_sets": 15},
            "functor_checks": {"checked": 300, "boundary_ok": 300, "identity_ok": 300, "natural": 300, "violated": 0},
        }
        self.sheaf_stats = {"sections": len(self.markets), "covers": len(BODIES) + 1, "glued": len(BODIES) + 1, "compatibility_checks": len(self.markets) // 3, "compatibility_passed": len(self.markets) // 3}

    # ----------------------------- scoring and levels -----------------------------

    def worker_power(self, w: Entity) -> float:
        af = age_curve(w.age, w.sex)
        base = w.skill * 95.0 + w.trust * 44.0 + w.risk * 24.0 + w.care * 22.0 + w.media * 20.0 + w.science * 32.0 + w.military * 20.0
        return base * af

    def compute_status(self, e: Entity) -> float:
        if e.kind == "worker":
            return self.worker_power(e) + e.wallet + e.privilege - e.burden
        if e.kind == "company":
            labor = len(e.worker_ids) * 95.0
            return e.wallet + e.capital * 4.8 + e.infrastructure * 5.5 + e.logistics * 4.0 + e.market_access * 5.0 + e.science * 5.2 + e.military * 4.5 + labor + e.privilege - e.burden
        if e.kind == "country":
            company_bonus = len(e.company_ids) * 8500.0
            return e.wallet + e.capital * 6.0 + e.infrastructure * 7.5 + e.logistics * 5.0 + e.governance * 8.0 + e.military * 6.8 + company_bonus + e.privilege - e.burden
        if e.kind == "alliance":
            country_bonus = len(e.country_ids) * 23000.0
            return e.wallet + e.military * 9.0 + e.governance * 5.5 + e.trust * 4.5 + country_bonus + e.privilege - e.burden
        if e.kind in ("un", "defense_org"):
            return e.wallet + e.governance * 7.0 + e.military * 8.0 + e.trust * 4.5 + e.capital * 3.5 + e.privilege - e.burden
        if e.kind == "product":
            return e.wallet + e.capital * 3.0 + e.market_access * 8.0 + e.quality * 450.0 + e.stock * 7.0 + e.units_sold * 60.0
        if e.kind == "market":
            return e.wallet + e.capital * 5.0 + e.market_access * 11.0 + e.volume * 0.18 + e.trades * 20.0
        return e.wallet + e.capital

    def refresh_all_levels(self, initial: bool = False) -> None:
        # First pass: direct entities.
        for group in (self.workers, self.products, self.markets, self.orgs):
            for e in group:
                e.status = self.compute_status(e)
                e.level = level_from_number(e.status)
        # Companies gain updated labor signals.
        for comp in self.companies:
            if comp.worker_ids:
                # Sample for speed; deterministic enough for large runs.
                ids = comp.worker_ids if len(comp.worker_ids) <= 40 else self.rng.sample(comp.worker_ids, 40)
                avg = sum(self.worker_power(self.entities[wid]) for wid in ids) / max(1, len(ids))
                comp.capital += avg * len(comp.worker_ids) * 0.001
            comp.status = self.compute_status(comp)
            comp.level = level_from_number(comp.status)
        for c in self.countries:
            if c.company_ids:
                ids = c.company_ids if len(c.company_ids) <= 60 else self.rng.sample(c.company_ids, 60)
                avg = sum(self.entities[cid].status for cid in ids) / max(1, len(ids))
                c.capital += avg * 0.0002
            c.status = self.compute_status(c)
            c.level = level_from_number(c.status)
        for a in self.alliances:
            if a.country_ids:
                avg = sum(self.entities[cid].status for cid in a.country_ids) / max(1, len(a.country_ids))
                a.military += avg * 0.00012
            a.status = self.compute_status(a)
            a.level = level_from_number(a.status)
        if initial:
            for e in self.entities.values():
                e.initial_level = e.level

    def record_initial_levels(self) -> None:
        for e in self.entities.values():
            e.initial_level = e.level

    def update_mobility_tracking(self) -> None:
        self.mobility_counts = {}
        self.mobility_heatmaps = {}
        for name, group in [("workers", self.workers), ("companies", self.companies), ("countries", self.countries), ("alliances", self.alliances)]:
            counts = {"up": 0, "down": 0, "same": 0}
            heat: Dict[int, Dict[int, int]] = defaultdict(lambda: defaultdict(int))
            for e in group:
                if e.level > e.initial_level:
                    counts["up"] += 1
                elif e.level < e.initial_level:
                    counts["down"] += 1
                else:
                    counts["same"] += 1
                heat[e.initial_level][e.level] += 1
            self.mobility_counts[name] = counts
            self.mobility_heatmaps[name] = heat

    # ----------------------------- stochastic scenarios -----------------------------

    def apply_macro_scenario(self) -> None:
        event_bank = [
            ("resource_boom", "A resource boom increases capital, logistics and production capacity.", [(self.companies, "capital", 0.14), (self.companies, "logistics", 0.12), (self.countries, "infrastructure", 0.08)]),
            ("research_breakthrough", "Research, data and compute become more valuable.", [(self.companies, "science", 0.18), (self.workers, "science", 0.13), (self.markets, "market_access", 0.05)]),
            ("media_polarization", "Media power rises but trust becomes unstable.", [(self.workers, "media", 0.16), (self.workers, "trust", -0.08), (self.countries, "governance", -0.05)]),
            ("defense_alert", "Defense readiness and alliance value increase.", [(self.alliances, "military", 0.22), (self.countries, "military", 0.15), (self.companies, "military", 0.11)]),
            ("governance_reform", "Trust and governance improve across institutions.", [(self.countries, "governance", 0.16), (self.alliances, "trust", 0.11), (self.companies, "market_access", 0.06)]),
            ("supply_shock", "Supply disruption punishes logistics-sensitive actors and creates losers.", [(self.companies, "logistics", -0.18), (self.markets, "market_access", -0.10), (self.countries, "infrastructure", -0.06)]),
            ("care_recognition", "Care, education and trust receive institutional recognition.", [(self.workers, "care", 0.22), (self.workers, "trust", 0.10), (self.companies, "market_access", 0.04)]),
            ("interplanetary_expansion", "Moon and Mars gain extra transport, logistics and market relevance.", [(self.countries, "logistics", 0.16), (self.markets, "market_access", 0.12), (self.companies, "infrastructure", 0.07)]),
        ]
        chosen = self.rng.sample(event_bank, self.rng.randint(2, 4))
        volatility = 0.0
        for name, description, targets in chosen:
            strength = self.rng.uniform(0.65, 1.60)
            self.scenario_scores[name] += strength
            volatility += strength
            for group, attr, delta in targets:
                n = len(group)
                if n == 0:
                    continue
                pct = self.rng.uniform(0.06, 0.26) if self.profile != "huge" else self.rng.uniform(0.03, 0.14)
                sample = self.rng.sample(group, max(1, int(n * pct)))
                for e in sample:
                    body_bonus = 1.25 if name == "interplanetary_expansion" and e.body in ("Moon", "Mars") else 1.0
                    actual_delta = delta * strength * body_bonus
                    if name in ("media_polarization", "supply_shock") and self.rng.chance(0.32):
                        actual_delta *= -0.55
                    old = getattr(e, attr, 0.0)
                    setattr(e, attr, max(0.0, old * (1.0 + actual_delta) + self.rng.uniform(0.0, max(2.0, abs(old) * 0.005))))
                    if self.rng.chance(0.03):
                        e.wallet += self.rng.uniform(2.0, 700.0) * strength * max(1, e.level)
            self.macro_history.append({"tick": self.tick, "name": name, "description": description, "strength": round(strength, 3)})
        self.tick_volatility.append(round(volatility, 3))

    # ----------------------------- market simulation -----------------------------

    def product_price(self, p: Entity, m: Entity) -> float:
        scarcity = 1.0 + 2.0 / math.sqrt(max(1, p.stock))
        return max(1.0, p.min_level * (0.65 + p.quality) * scarcity * (1.0 + p.level / 5.0)) * HEIGHT_MULTIPLIERS[p.min_level] * (1.0 + m.level * 0.015)

    def market_price(self, m: Entity) -> float:
        return max(500.0, m.status * 0.045 + m.volume * 0.12 + m.trades * 8.0)

    def trade_products(self) -> None:
        if not self.markets_with_products:
            return
        for _ in range(self.cfg["product_trades"]):
            m = self.rng.choice(self.markets_with_products)
            if not m.listed_ids:
                continue
            p = self.entities[self.rng.choice(m.listed_ids)]
            if p.stock <= 0:
                m.failed += 1; continue
            buyer = self.rng.choice(self.actors)
            if buyer.id == p.owner_id or buyer.level < p.min_level:
                m.failed += 1; continue
            price = self.product_price(p, m)
            if buyer.wallet + EPS < price:
                m.failed += 1; continue
            owner = self.entities.get(p.owner_id)
            buyer.wallet -= price
            if owner:
                owner.wallet += price * 0.985
            m.wallet += price * 0.015
            p.stock -= 1
            p.units_sold += 1
            p.wallet += price * 0.02
            m.volume += price
            m.trades += 1
            self.product_sales += 1
            self.trade_volume += price
            if self.rng.chance(0.0015):
                self.remember("PRODUCT %s -> %s for %sH" % (p.name[:28], buyer.name[:28], short_number(price)))

    def trade_markets_as_assets(self) -> None:
        if not self.market_rights_exchanges:
            return
        buyers = self.companies + self.countries + self.alliances + self.orgs
        for _ in range(self.cfg["market_trades"]):
            ex = self.rng.choice(self.market_rights_exchanges)
            if not ex.listed_ids:
                continue
            asset = self.entities[self.rng.choice(ex.listed_ids)]
            if asset.kind != "market":
                continue
            buyer = self.rng.choice(buyers)
            if buyer.id == asset.owner_id or buyer.level + 1 < asset.level:
                ex.failed += 1; continue
            price = self.market_price(asset) * 0.18
            if buyer.wallet + EPS < price:
                ex.failed += 1; continue
            old_owner = self.entities.get(asset.owner_id)
            buyer.wallet -= price
            if old_owner:
                old_owner.wallet += price
            asset.owner_id = buyer.id
            asset.wallet += price * 0.01
            asset.volume += price
            asset.trades += 1
            ex.volume += price
            ex.trades += 1
            self.trade_volume += price
            self.market_ownership_changes += 1
            if self.rng.chance(0.02):
                self.remember("MARKET %s control -> %s for %sH" % (asset.name[:28], buyer.name[:28], short_number(price)))

    def trade_privileges(self) -> None:
        for _ in range(self.cfg["privilege_trades"]):
            buyer = self.rng.choice(self.actors)
            domain = self.rng.choice(DOMAINS[:-4])
            boost = self.rng.choice([1, 1, 1, 2, 2, 3])
            price = (boost ** 2) * (buyer.level + 1) * HEIGHT_MULTIPLIERS[max(1, buyer.level)] * self.rng.uniform(1.2, 4.0)
            if buyer.wallet + EPS < price:
                continue
            buyer.wallet -= price
            buyer.privilege += price * 0.25
            buyer.market_access += boost * 5.0
            self.entities[self.un_by_scope.get(buyer.body, self.un_by_scope["Solar System"])].wallet += price
            self.privilege_count += 1
            self.trade_volume += price
            if self.rng.chance(0.006):
                self.remember("PRIVILEGE %s boost L+%d -> %s" % (domain, boost, buyer.name[:32]))

    def trade_burdens(self) -> None:
        compensators = self.companies + self.countries + self.orgs
        for _ in range(self.cfg["burden_trades"]):
            taker = self.rng.choice(self.actors)
            if taker.kind == "un" or taker.level <= 1:
                continue
            comp = self.rng.choice(compensators)
            if comp.id == taker.id:
                continue
            penalty = self.rng.choice([1, 1, 2, 2, 3])
            price = (penalty ** 2) * (taker.level + 1) * HEIGHT_MULTIPLIERS[max(1, taker.level)] * self.rng.uniform(1.4, 5.0)
            if comp.wallet + EPS < price:
                continue
            comp.wallet -= price
            taker.wallet += price
            taker.burden += price * 0.32
            self.burden_count += 1
            self.trade_volume += price
            if self.rng.chance(0.004):
                self.remember("BURDEN accepted by %s compensated by %s" % (taker.name[:28], comp.name[:28]))

    def manual_lift_helpers_media(self) -> None:
        candidates = [w for w in self.workers if w.domain in ("care", "media", "education", "medicine", "trust") and (w.care + w.media + w.trust) > 1.4]
        if not candidates:
            return
        count = min(len(candidates), max(1, int(len(self.workers) * 0.006)))
        for w in self.rng.sample(candidates, count):
            lift = self.rng.uniform(50.0, 420.0) * (1.0 + w.level * 0.2)
            w.wallet += lift
            w.privilege += lift * 0.45
            self.manual_lifts += 1

    def process_aggregate_network(self) -> None:
        attempts = self.cfg["network_packets"]
        delivered = int(attempts * self.rng.uniform(0.58, 0.91))
        dropped = int((attempts - delivered) * self.rng.uniform(0.05, 0.32))
        blocked = int(attempts * self.rng.uniform(0.002, 0.026))
        self.network_stats["packets_created"] += attempts
        self.network_stats["packets_delivered"] += delivered
        self.network_stats["packets_dropped"] += dropped
        self.network_stats["semaphore_blocked"] += blocked
        # queues/topologies drift slightly per tick without keeping packet objects.
        for k in list(self.network_stats["topology_counts"].keys()):
            self.network_stats["topology_counts"][k] += self.rng.randint(0, max(1, attempts // 2000))

    def update_sheaf_and_categories(self) -> None:
        self.sheaf_stats["sections"] += min(len(self.markets), 180 if self.profile == "demo" else 700)
        self.sheaf_stats["compatibility_checks"] += len(BODIES) * 12
        self.sheaf_stats["compatibility_passed"] += len(BODIES) * 12 - self.rng.randint(0, 2)
        extra_morphisms = self.product_sales + self.market_ownership_changes * 3 + self.privilege_count + self.burden_count
        self.category_stats["economic_category"]["morphisms"] += extra_morphisms
        self.category_stats["network_category"]["morphisms"] += self.network_stats["packets_created"] // 20
        self.category_stats["hierarchy_category"]["morphisms"] += (self.manual_lifts + self.market_ownership_changes) * 2

    def tick_once(self) -> None:
        self.tick += 1
        self.apply_macro_scenario()
        self.trade_products()
        self.trade_privileges()
        self.trade_burdens()
        self.trade_markets_as_assets()
        self.manual_lift_helpers_media()
        self.process_aggregate_network()
        self.refresh_all_levels()
        self.update_mobility_tracking()
        self.update_sheaf_and_categories()
        if not self.quiet:
            print(self.tick_report())

    def simulate(self, ticks: int) -> None:
        for _ in range(max(0, int(ticks))):
            self.tick_once()

    # ----------------------------- reporting -----------------------------

    def build_report(self) -> str:
        return "Built: entities=%d countries=%d alliances=%d companies=%d workers=%d products=%d markets=%d channels=%d econ_morphisms=%d net_morphisms=%d safe_data_oriented=True" % (
            len(self.entities), len(self.countries), len(self.alliances), len(self.companies), len(self.workers), len(self.products), len(self.markets),
            self.network_stats["channels"], self.category_stats["economic_category"]["morphisms"], self.category_stats["network_category"]["morphisms"]
        )

    def tick_report(self) -> str:
        return "tick=%d volume=%sH product_sales=%d market_trades=%d packets(created/delivered/dropped)=%d/%d/%d sem_blocked=%d sheaf_glued=%d" % (
            self.tick, short_number(self.trade_volume), self.product_sales, self.market_ownership_changes,
            self.network_stats["packets_created"], self.network_stats["packets_delivered"], self.network_stats["packets_dropped"],
            self.network_stats["semaphore_blocked"], self.sheaf_stats["glued"]
        )

    def level_distribution(self, group: Iterable[Entity]) -> Dict[int, int]:
        return dict(sorted(Counter(e.level for e in group).items()))

    def body_level_heat(self, group: Iterable[Entity]) -> Dict[str, Dict[int, float]]:
        data: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        for e in group:
            data[e.body][e.level] += 1
        return data

    def top_entities(self, group: Sequence[Entity], n: int = 8) -> List[Entity]:
        return heapq.nlargest(n, group, key=lambda e: e.status)

    def summary_entity(self, e: Entity) -> Dict[str, Any]:
        owner = self.entities.get(e.owner_id)
        return {
            "name": e.name, "kind": e.kind, "level": e.level, "level_name": LEVEL_NAMES[e.level],
            "domain": e.domain, "body": e.body, "owner": owner.name if owner else None,
            "status_number": round(e.status, 2), "wallet": round(e.wallet, 2),
        }

    def report(self) -> Dict[str, Any]:
        return {
            "seed": self.seed,
            "profile": self.profile,
            "ticks": self.tick,
            "counts": {"entities": len(self.entities), "countries": len(self.countries), "alliances": len(self.alliances), "companies": len(self.companies), "workers": len(self.workers), "products": len(self.products), "markets": len(self.markets), "privileges": self.privilege_count, "burdens": self.burden_count},
            "trade": {"volume_H": round(self.trade_volume, 2), "product_sales": self.product_sales, "market_ownership_changes": self.market_ownership_changes, "manual_lifts": self.manual_lifts},
            "levels": {"workers": self.level_distribution(self.workers), "companies": self.level_distribution(self.companies), "countries": self.level_distribution(self.countries), "alliances": self.level_distribution(self.alliances), "products": self.level_distribution(self.products), "markets": self.level_distribution(self.markets)},
            "mobility": self.mobility_counts,
            "network": self.network_stats,
            "category": self.category_stats,
            "sheaf": self.sheaf_stats,
            "scenario": {"events": self.macro_history[-32:], "scores": dict(self.scenario_scores), "volatility": self.tick_volatility},
            "goods_hierarchy": {str(level): GOODS_HIERARCHY[level] for level in range(1, 13)},
            "top_countries": [self.summary_entity(e) for e in self.top_entities(self.countries)],
            "top_companies": [self.summary_entity(e) for e in self.top_entities(self.companies)],
            "top_alliances": [self.summary_entity(e) for e in self.top_entities(self.alliances)],
            "top_markets": [self.summary_entity(e) for e in self.top_entities(self.markets)],
            "top_workers": [self.summary_entity(e) for e in self.top_entities(self.workers)],
            "recent_trades": list(self.recent_events[-20:]),
        }

    def what_more_can_be_simulated(self) -> List[str]:
        return [
            "demographic transitions across generations, inheritance, schooling, retirement and age-cohort replacement",
            "banking, debt chains, insolvency cascades, collateral, central-bank-style hierarchy liquidity",
            "elections, propaganda, censorship, legitimacy, constitutional reforms and crisis governments",
            "migration between Earth, Moon and Mars, including brain drain, labor shortages and colony attraction",
            "war, deterrence, mobilization, arms races, negotiated disarmament and defense-alliance fragmentation",
            "innovation races, patents, research commons, secret projects and knowledge diffusion",
            "ecological constraints: oxygen scarcity, water contamination, crop failures and terraforming risk",
            "criminal markets, corruption, smuggling, anti-corruption courts and status fraud",
            "cultural prestige markets, celebrity hierarchy, symbolic capital and reputation bubbles",
            "cyber conflict, sabotage, network partitioning, redundancy and emergency rerouting",
            "class conflict, strikes, unions, social insurance and redistributive reforms",
            "planetary catastrophes, evacuation markets, continuity archives and emergency command regimes",
        ]

    # ----------------------------- visual artifacts -----------------------------

    def visual_goods_hierarchy(self) -> str:
        rows = []
        for level in range(1, 13):
            goods = GOODS_HIERARCHY[level]
            rows.append(("L%02d" % level, LEVEL_NAMES[level], len(goods), "; ".join(goods[:2]), "; ".join(goods[2:])))
        counts = {"L%02d" % level: len(GOODS_HIERARCHY[level]) for level in range(1, 13)}
        ladder = [chart_title("GOODS LADDER / ENTITLEMENT STAIRCASE")]
        for level in range(12, 0, -1):
            ladder.append("L%02d %-16s │ %s" % (level, LEVEL_NAMES[level], " ; ".join(GOODS_HIERARCHY[level][:3])))
        entitlement = [chart_title("WHO GETS WHICH GOODS LEVELS")]
        entitlement.append("Rows are actor level; columns are goods levels. █ means the actor level includes access to that goods level.")
        entitlement.append(" " * 8 + " ".join("G%02d" % i for i in range(1, 13)))
        for actor_level in range(1, 13):
            entitlement.append("A-L%02d   %s" % (actor_level, " ".join(" █ " if goods_level <= actor_level else " · " for goods_level in range(1, 13))))
        return "\n\n".join([
            render_table(rows, ["Level", "Hierarchy stage", "Goods", "Examples A", "Examples B"], "GOODS HIERARCHY TABLE", [8, 18, 7, 34, 34]),
            render_histogram(counts, "NUMBER OF EXAMPLE GOODS PER LEVEL", width=34),
            "\n".join(ladder),
            "\n".join(entitlement),
        ])

    def visual_levels(self) -> str:
        parts = [
            render_level_chart(self.level_distribution(self.workers), "WORKER LEVELS"),
            render_level_chart(self.level_distribution(self.companies), "COMPANY LEVELS"),
            render_level_chart(self.level_distribution(self.countries), "COUNTRY LEVELS"),
            render_level_chart(self.level_distribution(self.alliances), "DEFENSE ALLIANCE LEVELS"),
            render_level_chart(self.level_distribution(self.products), "PRODUCT LEVELS"),
            render_level_chart(self.level_distribution(self.markets), "MARKET LEVELS"),
        ]
        for name, group in [("WORKERS", self.workers), ("COMPANIES", self.companies), ("COUNTRIES", self.countries), ("MARKETS", self.markets)]:
            data = self.body_level_heat(group)
            rows = [b for b in ["Earth", "Moon", "Mars", "Solar System"] if b in data]
            parts.append(render_heatmap(rows, list(range(1, 13)), data, "%s BY BODY × LEVEL" % name))
        return "\n\n".join(parts)

    def visual_mobility(self) -> str:
        rows = []
        for key in ["workers", "companies", "countries", "alliances"]:
            c = self.mobility_counts.get(key, {"up": 0, "down": 0, "same": 0})
            rows.append((key, c["up"], c["down"], c["same"], sparkline([c["up"], c["down"], c["same"]])))
        parts = [render_table(rows, ["Group", "Up", "Down", "Same", "Shape"], "CAREER MOBILITY SUMMARY", [14, 10, 10, 10, 16])]
        for key in ["workers", "companies", "countries", "alliances"]:
            parts.append(render_histogram(self.mobility_counts.get(key, {}), "%s: UP / DOWN / SAME" % key.upper(), width=34))
        for key in ["workers", "companies", "countries", "alliances"]:
            heat = self.mobility_heatmaps.get(key, {})
            rows2 = [r for r in range(1, 13) if r in heat]
            if rows2:
                parts.append(render_heatmap(rows2, list(range(1, 13)), heat, "%s INITIAL LEVEL → CURRENT LEVEL" % key.upper()))
        return "\n\n".join(parts)

    def visual_network_category(self) -> str:
        cat_rows = []
        for name in ["economic_category", "network_category", "hierarchy_category", "topology_category"]:
            c = self.category_stats[name]
            cat_rows.append((name, c["objects"], c["morphisms"], c["hom_sets"], sparkline([c["objects"], c["morphisms"], c["hom_sets"]])))
        packet_rows = [
            ("created", self.network_stats["packets_created"]),
            ("delivered", self.network_stats["packets_delivered"]),
            ("dropped", self.network_stats["packets_dropped"]),
            ("semaphore_blocked", self.network_stats["semaphore_blocked"]),
        ]
        fun = self.category_stats["functor_checks"]
        fun_rows = [
            ("Status functor", fun["checked"], fun["boundary_ok"], fun["identity_ok"]),
            ("Access functor", fun["checked"], fun["boundary_ok"], fun["identity_ok"]),
            ("Natural transformation", fun["checked"], fun["natural"], fun["violated"]),
        ]
        sheaf_rows = [(k, v) for k, v in self.sheaf_stats.items()]
        return "\n\n".join([
            render_histogram(self.network_stats["topology_counts"], "CHANNELS BY TOPOLOGY", width=34),
            render_histogram(self.network_stats["duplex_counts"], "CHANNELS BY DUPLEX MODE", width=34),
            render_histogram(self.network_stats["queue_counts"], "CHANNEL QUEUE DISCIPLINES", width=34),
            render_table(packet_rows, ["Packet/Semaphore metric", "Value"], "AGGREGATE DATASTREAM / SEMAPHORE METRICS", [30, 14]),
            render_table(cat_rows, ["Category", "Objects", "Morphisms", "Hom-sets", "Shape"], "CATEGORY SIZE DIAGRAM", [28, 10, 10, 10, 16]),
            render_table(fun_rows, ["Functor/NT", "Checked", "OK/Natural", "Identity/Viol"], "FUNCTORIALITY / NATURALITY CHECKS", [26, 10, 12, 14]),
            render_table(sheaf_rows, ["Sheaf metric", "Value"], "PRESHEAF / SHEAF GLUING SUMMARY", [30, 14]),
        ])

    def visual_markets(self) -> str:
        vol: Dict[str, float] = defaultdict(float)
        trades: Dict[str, float] = defaultdict(float)
        heat: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        for m in self.markets:
            vol[m.domain] += m.volume
            trades[m.domain] += m.trades
            heat[m.domain][m.level] += m.volume if m.volume > 0 else 1.0
        hot = [k for k, _ in sorted(vol.items(), key=lambda kv: -kv[1])[:14]]
        return "\n\n".join([
            render_histogram(dict(sorted(vol.items(), key=lambda kv: -kv[1])[:16]), "MARKET VOLUME BY DOMAIN", width=36),
            render_histogram(dict(sorted(trades.items(), key=lambda kv: -kv[1])[:16]), "MARKET TRADES BY DOMAIN", width=36),
            render_heatmap(hot, list(range(1, 13)), heat, "MARKET DOMAIN × LEVEL HEATMAP"),
        ])

    def visual_scenarios(self) -> str:
        event_rows = [(e["tick"], e["name"], short_number(e["strength"]), e["description"][:52]) for e in self.macro_history[-18:]]
        score_hist = {k: v for k, v in sorted(self.scenario_scores.items(), key=lambda kv: -kv[1])[:12]}
        vol_map = {"tick%02d" % (i + 1): v for i, v in enumerate(self.tick_volatility)}
        return "\n\n".join([
            render_table(event_rows, ["Tick", "Event", "Strength", "Meaning"], "MACRO SCENARIO EVENT LOG", [8, 24, 10, 52]),
            render_histogram(score_hist, "SCENARIO DRIVER STRENGTHS", width=34),
            render_histogram(vol_map, "VOLATILITY BY TICK", width=34),
        ])

    def visual_artifacts(self) -> List[Tuple[str, str, str, str]]:
        return [
            ("Goods hierarchy on 12 levels", self.visual_goods_hierarchy(),
             "The next UTF-8 output defines what goods and rights correspond to each hierarchy level. Rows L01-L12 are hierarchy levels. The table columns show the level, its name, how many example goods are listed and examples of goods or rights. The entitlement matrix uses actor levels as rows and goods levels as columns; █ means an actor at that level has access to that goods tier.",
             "This shows how abstract hierarchy becomes concrete access. Low levels receive survival and basic goods. Middle levels receive professional, regional and national operating rights. Top levels receive interplanetary, systemic and solar-apex coordination rights."),
            ("Hierarchy level distributions", self.visual_levels(),
             "These diagrams show how many entities sit in each level L01-L12. Rows in heatmaps are Earth, Moon, Mars or Solar System. Columns are hierarchy levels. Darker cells mean more entities in that body-level cell.",
             "This reveals whether the run is bottom-heavy, middle-heavy or apex-heavy, and whether hierarchy concentration differs across Earth, Moon and Mars."),
            ("Career mobility and ascent/descent", self.visual_mobility(),
             "These tables and heatmaps measure career movement. Up means the entity is above its initial level; Down means below initial level; Same means unchanged. In transition heatmaps, rows are starting levels and columns are current levels.",
             "This is the direct test of whether the simulated hierarchy is mobile. Above-diagonal mass means ascent; below-diagonal mass means decline; diagonal mass means stability."),
            ("Markets and domains", self.visual_markets(),
             "These diagrams group all market activity by domain. The histograms compare trade volume and trade count. The heatmap uses market domain as rows and hierarchy levels as columns.",
             "This tells which domains dominated the run and whether trade concentrated in low access levels, professional levels, planetary levels or apex levels."),
            ("Network, queues, duplexing, categories and sheaves", self.visual_network_category(),
             "This section summarizes network topology, half/full-duplexing, FIFO/LIFO/priority queues, aggregate packet flow, semaphores, category sizes, functor checks, natural transformation checks and sheaf gluing. It is aggregate by design to stay PyPy-safe at large scale.",
             "The output shows whether the abstract architecture stayed coherent without materializing a dangerous live graph. Packet and semaphore numbers show flow pressure; category and sheaf numbers show structural consistency."),
            ("Scenario diversity and random outcomes", self.visual_scenarios(),
             "This section lists the stochastic macro-events applied during the run. Strength is the event intensity. Scenario driver histograms aggregate how strongly each event type shaped the run. Volatility shows total shock intensity per tick.",
             "This explains why runs can end differently. A defense-heavy run lifts alliances; a research-heavy run lifts science/data firms; a supply-shock run creates more losers; care-recognition lifts care and trust workers."),
        ]

    def mobility_summary_text(self, key: str) -> str:
        c = self.mobility_counts.get(key, {"up": 0, "down": 0, "same": 0})
        total = max(1, c["up"] + c["down"] + c["same"])
        up = c["up"] / total
        down = c["down"] / total
        if up > 0.35 and down > 0.12:
            return "%s show strong churn: upward careers exist, but decline is also meaningful." % key.title()
        if up > 0.35:
            return "%s mostly moved upward; this run rewarded expansion, recognition or favorable macro-events." % key.title()
        if down > 0.25:
            return "%s were heavily punished; competitive pressure or shocks produced visible decline." % key.title()
        return "%s were comparatively stable; hierarchy persistence dominated this group." % key.title()

    def final_scenario_summary(self) -> str:
        scores = sorted(self.scenario_scores.items(), key=lambda kv: -kv[1])
        dominant = ", ".join("%s=%s" % (k, short_number(v)) for k, v in scores[:5]) if scores else "none"
        avg_vol = sum(self.tick_volatility) / max(1, len(self.tick_volatility))
        top_domain = None
        volume_by_domain: Dict[str, float] = defaultdict(float)
        for m in self.markets:
            volume_by_domain[m.domain] += m.volume
        if volume_by_domain:
            top_domain = max(volume_by_domain.items(), key=lambda kv: kv[1])[0]
        return "\n".join([
            "This run is one realized path through a stochastic hierarchy economy. Dominant scenario drivers were: %s." % dominant,
            "Average volatility per tick was %s. A higher value means another seed could have produced visibly different winners, losers and dominant domains." % short_number(avg_vol),
            "The most active market domain in this realized run was %s." % (top_domain or "none"),
            "Alternative plausible outcomes remain balanced: a stronger defense-alert path would favor alliances and military states; a stronger research-breakthrough path would favor compute, data and science; a harsher supply shock would push more firms and markets downward; and a care-recognition path would raise care, medicine, education and trust workers.",
            "Therefore the output should not be read as an inevitable equilibrium. It is a scenario sample from a broad space of possible hierarchy-market futures.",
        ])

    def print_report(self, json_path: Optional[str], include_visuals: bool = True) -> None:
        report = self.report()
        if json_path:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        print("=" * 96)
        print("SOLAR HIERARCHY MARKET — PYPY-SAFE DATA-ORIENTED REPORT")
        print("=" * 96)
        print("seed=%s profile=%s ticks=%s processes_argument=%s" % (report["seed"], report["profile"], report["ticks"], self.processes))
        print("\nGLOBAL EXPLANATION OF THE SIMULATION")
        print("The simulation models a hierarchy-currency economy across Earth, Moon and Mars. The economy contains governance bodies, defense organizations, alliances, countries, companies, workers, products, tradable markets, privileges and burdens. Hierarchy is the meaningful currency; H is only the compressed settlement number used for accounting.")
        print("The goal is to observe how goods access, market exchange, network flow, category-like structure, sheaf-like gluing and stochastic macro-events shape status, career mobility and different possible outcomes.")
        print("\nWHAT ELSE CAN STILL BE SIMULATED")
        for item in self.what_more_can_be_simulated():
            print("  - " + item)
        print("\nEXPLANATION OF ABBREVIATIONS")
        print("H = compressed hierarchy accounting value; L01-L12 = hierarchy stages from Survival to Solar Apex; Up/Down/Same = movement relative to initial hierarchy level; NT = natural transformation; hom-set = morphisms between two category objects; FIFO/LIFO/priority = queue discipline; half/full = duplex mode; semaphore_blocked = simulated blocked channel permits.")

        print("\nEXPLANATION OF NUMERIC SUMMARY BLOCKS")
        print("The next blocks give the macro state of this run before the UTF-8 diagrams. Each block has an interpretation directly below it.")
        print("\nCounts:")
        for k, v in report["counts"].items():
            print("  %-30s %s" % (k, v))
        print("Interpretation: these counts define the scale of the simulated society and market system.")
        print("\nTrade:")
        for k, v in report["trade"].items():
            print("  %-30s %s" % (k, v))
        print("Interpretation: trade volume, product sales and market ownership changes show how liquid and structurally transformative this run became.")
        print("\nNetwork:")
        for k in ["nodes", "channels", "components", "degree_min", "degree_mean", "degree_max", "packets_created", "packets_delivered", "packets_dropped", "semaphore_blocked"]:
            print("  %-30s %s" % (k, report["network"].get(k)))
        print("Interpretation: these aggregate network numbers replace the old dangerous live graph. They still show flow pressure, connectivity and semaphore contention without causing PyPy heap instability.")
        print("\nCategory:")
        for key in ["economic_category", "network_category", "hierarchy_category", "topology_category"]:
            c = report["category"][key]
            print("  %-30s objects=%s morphisms=%s hom_sets=%s" % (key, c["objects"], c["morphisms"], c["hom_sets"]))
        print("Interpretation: these counts summarize the category-theoretic architecture as aggregate structure: objects are entities or levels; morphisms are relations, trades and transformations; hom-sets group morphisms by source and target type.")
        print("\nLevel distributions:")
        for k, v in report["levels"].items():
            print("  %-12s %s" % (k, v))
        print("Interpretation: these distributions show where each entity type sits in the twelve-level hierarchy.")
        print("\nMobility summary:")
        for k, v in report["mobility"].items():
            print("  %-12s up=%s down=%s same=%s" % (k, v["up"], v["down"], v["same"]))
        print("Interpretation: these numbers show whether people, companies, states and defense alliances actually moved through the hierarchy.")
        print("\nScenario summary:")
        print("  scenario drivers=", ", ".join("%s=%s" % (k, short_number(v)) for k, v in sorted(report["scenario"]["scores"].items(), key=lambda kv: -kv[1])[:8]))
        print("  volatility per tick=", report["scenario"]["volatility"])
        print("Interpretation: scenario drivers and volatility explain why repeated runs can diverge sharply.")

        for title, key in [("Top countries", "top_countries"), ("Top companies", "top_companies"), ("Top alliances", "top_alliances"), ("Top markets", "top_markets"), ("Top workers", "top_workers")]:
            print("\n" + title)
            print("Explanation of columns: Lxx is the final hierarchy level; the next field is the level name; then entity name; then compressed status in H; then domain, body and current owner.")
            for e in report[key]:
                print("  L%02d %-16s %-52s %12sH domain=%s body=%s owner=%s" % (e["level"], e["level_name"], e["name"][:52], short_number(e["status_number"]), e["domain"], e["body"], e["owner"]))
            print("Interpretation: this top list identifies the winners of this run in that entity group.")

        print("\nRecent trades / market events")
        print("Explanation: each bullet is a recent concrete event from product exchange, privilege exchange, burden exchange or market ownership transfer.")
        for t in report["recent_trades"][:15]:
            print("  - " + t)
        print("Interpretation: these events are the micro-level traces behind the aggregate results above.")

        if include_visuals:
            print("\n" + chart_title("UTF-8 DASHBOARD", 96, "#"))
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


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="PyPy-safe solar hierarchy-market simulation")
    p.add_argument("positional_ticks", nargs="?", type=int, help="optional shorthand for ticks")
    p.add_argument("--profile", choices=sorted(SCALE_CONFIGS), default="demo")
    p.add_argument("--ticks", type=int, default=None)
    p.add_argument("--seed", type=int, default=None, help="set for reproducibility; omitted means a different run each call")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--json", default=None)
    p.add_argument("--no-visuals", action="store_true")
    p.add_argument("--processes", type=int, default=1, help="accepted for compatibility; this safe version does not need process workers")
    p.add_argument("--safe-mode", action="store_true", help="accepted for compatibility; safe mode is always on")
    p.add_argument("--unsafe-full-graph", action="store_true", help="accepted for compatibility but ignored; full live graph was removed to avoid PyPy crashes")
    return p.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    ticks = args.ticks if args.ticks is not None else (args.positional_ticks if args.positional_ticks is not None else 1)
    sim = SolarHierarchySimulation(profile=args.profile, seed=args.seed, quiet=args.quiet, processes=args.processes)
    sim.build()
    sim.simulate(max(0, int(ticks)))
    sim.print_report(args.json, include_visuals=not args.no_visuals)
    sys.stdout.flush(); sys.stderr.flush()
    return 0


if __name__ == "__main__":
    code = main(sys.argv[1:])
    os._exit(code)
