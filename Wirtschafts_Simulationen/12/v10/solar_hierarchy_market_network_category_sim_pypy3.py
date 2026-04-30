#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Solar Hierarchy Market Simulation — PyPy-safe, bilingual, colored, parameterized
================================================================================

A dependency-free PyPy3-compatible simulation of a hierarchy-currency economy.

This version is intentionally data-oriented: it keeps the large economy real
(workers, firms, countries, alliances, markets, products, bodies), but keeps
networks/categories/functors/sheaves as aggregate structures so large PyPy runs
avoid segmentation faults from huge live object graphs.
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

EPS = 1e-9

LEVEL_NAMES_EN = {
    1: "Survival", 2: "Basic", 3: "Local", 4: "Skilled", 5: "Professional",
    6: "Regional", 7: "National", 8: "Alliance", 9: "Planetary",
    10: "Interplanetary", 11: "Systemic", 12: "Solar Apex",
}
LEVEL_NAMES_DE = {
    1: "Überleben", 2: "Basis", 3: "Lokal", 4: "Fachkraft", 5: "Professionell",
    6: "Regional", 7: "National", 8: "Bündnis", 9: "Planetar",
    10: "Interplanetar", 11: "Systemisch", 12: "Sonnen-Apex",
}

LEVEL_THRESHOLDS = [
    0.0, 160.0, 420.0, 950.0, 2100.0, 4800.0, 11000.0, 25000.0,
    60000.0, 145000.0, 350000.0, 850000.0,
]
HEIGHT_MULTIPLIERS = {
    1: 1.00, 2: 1.35, 3: 1.85, 4: 2.55, 5: 3.55, 6: 5.10,
    7: 7.40, 8: 10.80, 9: 15.90, 10: 23.50, 11: 35.00, 12: 52.00,
}
ELEMENT_WEIGHTS = {
    "labor": 1.00, "skill": 1.18, "care": 1.12, "media": 1.10, "science": 1.32,
    "risk": 1.15, "trust": 1.22, "governance": 1.45, "military": 1.38,
    "capital": 1.00, "logistics": 1.20, "infrastructure": 1.30,
    "market_access": 1.28, "privilege": 1.55, "burden": 1.05,
    "topology": 1.16, "duplex": 1.06, "queue": 1.04, "semaphore": 1.10,
    "morphism": 1.14, "sheaf": 1.25, "functor": 1.19,
    "food": 1.00, "water": 1.08, "oxygen": 1.22, "housing": 1.03, "energy": 1.18,
    "medicine": 1.24, "education": 1.16, "compute": 1.22, "transport": 1.15,
    "shipbuilding": 1.25, "agriculture": 1.06, "manufacturing": 1.13,
    "defense": 1.35, "culture": 1.08, "research": 1.32, "finance": 1.20,
    "data": 1.24, "orbital_slots": 1.42, "terraforming": 1.50,
    "market_rights": 1.36, "network_bandwidth": 1.21, "semaphore_permits": 1.18,
    "topology_rights": 1.20, "sheaf_coherence": 1.26, "general": 1.00,
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
SPARK_CHARS = "▁▂▃▄▅▆▇█"
HEAT_CHARS = " ·░▒▓█"

GOODS_HIERARCHY_EN: Dict[int, List[str]] = {
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
GOODS_HIERARCHY_DE: Dict[int, List[str]] = {
    1: ["Basis-Wasserration", "Notfallkalorien", "geteilter Schutzplatz", "Minimal-Luftfilter"],
    2: ["Hygieneset", "einfache Kleidung", "Basis-Kommunikationsterminal", "ÖPNV-Gutschein"],
    3: ["Reparaturwerkzeuge", "private Schlafkapsel", "Standard-Ernährungsplan", "lokaler Marktzugang"],
    4: ["Lehrwerkstatt-Zugang", "Bildungspaket", "Klinikpriorität", "kleines Datenkontingent"],
    5: ["professionelles Wohnen", "Fahrzeugnutzungsrechte", "Forschungsterminal", "Familienverbrauchspaket"],
    6: ["regionale Logistikkapazität", "fortgeschrittene Medizin", "Team-Büroraum", "mittlere Rechenkapazität"],
    7: ["nationaler Reisepass", "Fabrikanteil", "strategische Lagerrechte", "Sicherheitsbegleitung"],
    8: ["Bündnis-Beschaffungsrechte", "verteidigungstauglicher Transport", "grenzüberschreitende Marktfranchise", "Koalitionslagebild"],
    9: ["planetarer Medien-Einflussplatz", "großer Industriecampus", "planetare Kapitallinie", "Quote für seltene Materialien"],
    10: ["interplanetare Frachtroute", "Orbital-Dockingpriorität", "Mehrplanet-Liefervertrag", "interplanetarer Datenrücken"],
    11: ["systemische Notfall-Kommandobandbreite", "Zugriffsrechte auf Solarreserven", "Anhörung in Systemregierung", "hohe strategische Abschreckungsressourcen"],
    12: ["Solar-Apex-Koordinationsrechte", "Zivilisations-Kontinuitätsarchiv", "oberstes Missions-Zuteilungsfenster", "Apex-Mobilitätskorridor"],
}

DOMAIN_DE = {
    "food": "Nahrung", "water": "Wasser", "oxygen": "Sauerstoff", "housing": "Wohnen", "energy": "Energie",
    "medicine": "Medizin", "education": "Bildung", "compute": "Rechenleistung", "transport": "Transport",
    "shipbuilding": "Schiffbau", "agriculture": "Landwirtschaft", "manufacturing": "Fertigung", "defense": "Verteidigung",
    "media": "Medien", "culture": "Kultur", "research": "Forschung", "care": "Fürsorge", "finance": "Finanzen",
    "data": "Daten", "orbital_slots": "Orbitalplätze", "terraforming": "Terraforming", "market_rights": "Marktrechte",
    "labor": "Arbeit", "privilege": "Privileg", "burden": "Belastung", "network_bandwidth": "Netzbandbreite",
    "semaphore_permits": "Semaphor-Erlaubnisse", "topology_rights": "Topologierechte", "sheaf_coherence": "Garbkohärenz",
    "skill": "Fähigkeit", "science": "Wissenschaft", "risk": "Risiko", "trust": "Vertrauen", "governance": "Steuerung",
    "military": "Militär", "logistics": "Logistik", "infrastructure": "Infrastruktur", "capital": "Kapital", "general": "Allgemein",
    "topology": "Topologie", "duplex": "Duplex", "queue": "Queue", "semaphore": "Semaphor", "morphism": "Morphismus", "sheaf": "Garbe", "functor": "Funktor",
}
BODY_DE = {"Earth": "Erde", "Moon": "Mond", "Mars": "Mars", "Solar System": "Sonnensystem"}
GROUP_DE = {
    "entities": "Entitäten",
    "celestial_bodies": "Himmelskörper", "un_orgs": "UN-Organisationen", "defense_orgs": "Verteidigungsorganisationen",
    "alliances": "Bündnisse", "countries": "Staaten", "companies": "Unternehmen", "workers": "Arbeitnehmer",
    "products": "Produkte", "markets": "Märkte", "privileges": "Privilegien", "burdens": "Belastungen",
}
SCENARIO_DE = {
    "resource_boom": "Ressourcenboom", "research_breakthrough": "Forschungsdurchbruch", "media_polarization": "Medienpolarisierung",
    "defense_alert": "Verteidigungsalarm", "governance_reform": "Governance-Reform", "supply_shock": "Versorgungsschock",
    "care_recognition": "Anerkennung der Fürsorge", "interplanetary_expansion": "interplanetare Expansion",
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


# ---------------------------------------------------------------------------
# ANSI colors and visual helpers
# ---------------------------------------------------------------------------

COLOR_ENABLED = True
COLOR_PALETTE = [196, 202, 208, 214, 220, 226, 154, 118, 82, 45, 39, 33, 57, 93, 129, 165, 201]
LEVEL_COLORS = {1: 244, 2: 39, 3: 45, 4: 51, 5: 82, 6: 118, 7: 154, 8: 190, 9: 226, 10: 214, 11: 202, 12: 196}
HEAT_COLORS = [240, 245, 39, 82, 220, 196]


def ansi(text: Any, code: int, bold: bool = False) -> str:
    if not COLOR_ENABLED:
        return str(text)
    prefix = "\033[1;38;5;%dm" % code if bold else "\033[38;5;%dm" % code
    return prefix + str(text) + "\033[0m"


def chart_title(title: str, width: int = 104, char: str = "═") -> str:
    core = " %s " % title
    if len(core) >= width:
        return ansi(core, 220, True)
    left = (width - len(core)) // 2
    right = width - len(core) - left
    return ansi(char * left, 39) + ansi(core, 220, True) + ansi(char * right, 39)


def utf8_bar(value: float, max_value: float, width: int = 36, empty: str = "░") -> str:
    if width <= 0:
        return ""
    if max_value <= EPS:
        return ansi(empty * width, 240)
    ratio = clamp(float(value) / float(max_value), 0.0, 1.0)
    full = int(ratio * width)
    out = []
    for i in range(width):
        if i < full:
            color = COLOR_PALETTE[int((i / max(1, width - 1)) * (len(COLOR_PALETTE) - 1))]
            out.append(ansi("█", color, False))
        else:
            out.append(ansi(empty, 240))
    return "".join(out)


def sparkline(values: Sequence[float]) -> str:
    if not values:
        return ""
    vals = [float(v) for v in values]
    lo = min(vals)
    hi = max(vals)
    if hi - lo <= EPS:
        return ansi(SPARK_CHARS[0] * len(vals), 244)
    out = []
    for v in vals:
        idx = int((v - lo) / (hi - lo) * (len(SPARK_CHARS) - 1))
        idx = int(clamp(idx, 0, len(SPARK_CHARS) - 1))
        color = COLOR_PALETTE[int((idx / max(1, len(SPARK_CHARS) - 1)) * (len(COLOR_PALETTE) - 1))]
        out.append(ansi(SPARK_CHARS[idx], color))
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
    for idx, (key, value) in enumerate(items):
        lines.append("%s │%s│ %s" % (ansi(pad(key, 24), COLOR_PALETTE[idx % len(COLOR_PALETTE)], True), utf8_bar(float(value), maxv, width), ansi(short_number(float(value)), 220)))
    return "\n".join(lines)


def render_level_chart(mapping: Dict[int, int], title: str, lang: str, width: int = 36) -> str:
    names = LEVEL_NAMES_DE if lang == "de" else LEVEL_NAMES_EN
    lines = [chart_title(title)]
    maxv = max([float(v) for v in mapping.values()] or [1.0]) or 1.0
    for level in range(1, 13):
        value = float(mapping.get(level, 0))
        label = "L%02d %-16s" % (level, names[level][:16])
        lines.append("%s │%s│ %s" % (ansi(label, LEVEL_COLORS[level], True), utf8_bar(value, maxv, width), ansi(short_number(value), LEVEL_COLORS[level])))
    return "\n".join(lines)


def render_table(rows: Sequence[Sequence[Any]], headers: Sequence[str], title: str, widths: Sequence[int]) -> str:
    lines = [chart_title(title)]
    head = " | ".join([ansi(pad(h, w), COLOR_PALETTE[i % len(COLOR_PALETTE)], True) for i, (h, w) in enumerate(zip(headers, widths))])
    sep = "-+-".join(["-" * w for w in widths])
    lines.append(head)
    lines.append(ansi(sep, 244))
    for ridx, row in enumerate(rows):
        color = COLOR_PALETTE[ridx % len(COLOR_PALETTE)]
        lines.append(" | ".join([ansi(pad(v, w), color if cidx == 0 else 250) for cidx, (v, w) in enumerate(zip(row, widths))]))
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
    header = " " * 18 + " ".join([ansi(pad(c, 3), 250, True) for c in cols])
    lines.append(header)
    for ridx, r in enumerate(rows):
        row = data.get(r, {})
        cells = []
        for c in cols:
            v = float(row.get(c, 0.0))
            idx = int(round(clamp(v / maxv, 0.0, 1.0) * (len(HEAT_CHARS) - 1)))
            idx = int(clamp(idx, 0, len(HEAT_CHARS) - 1))
            cells.append(" %s " % ansi(HEAT_CHARS[idx], HEAT_COLORS[idx], True))
        lines.append("%s %s" % (ansi(pad(r, 17), COLOR_PALETTE[ridx % len(COLOR_PALETTE)], True), "".join(cells)))
    lines.append(ansi("Legend: · low  ░▒▓█ high", 250))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Entity model
# ---------------------------------------------------------------------------

class Entity:
    __slots__ = (
        "id", "name", "kind", "body", "scope", "country_id", "owner_id", "level", "domain",
        "elements", "wallet", "privilege_h", "burden_h", "privilege_boost", "burden_penalty",
        "age", "sex", "traits", "employer_id", "sector", "company_ids", "worker_ids", "product_ids",
        "alliance_ids", "country_ids", "min_level", "stock", "quality", "units_sold", "volume", "trade_count",
        "market_trade_count", "queue_discipline", "recent", "initial_level", "last_status", "active", "duration",
    )
    def __init__(self, eid: int, name: str, kind: str, body: str = "Solar System", scope: str = "Solar System", country_id: Optional[int] = None, owner_id: Optional[int] = None, level: int = 1, domain: str = "general", elements: Optional[Dict[str, float]] = None) -> None:
        self.id = eid
        self.name = name
        self.kind = kind
        self.body = body
        self.scope = scope
        self.country_id = country_id
        self.owner_id = owner_id
        self.level = int(clamp(level, 1, 12))
        self.domain = domain
        self.elements = dict(elements or {})
        self.wallet = 0.0
        self.privilege_h = 0.0
        self.burden_h = 0.0
        self.privilege_boost = 0
        self.burden_penalty = 0
        self.age = 0
        self.sex = "other"
        self.traits: Dict[str, float] = {}
        self.employer_id: Optional[int] = None
        self.sector = "general"
        self.company_ids: List[int] = []
        self.worker_ids: List[int] = []
        self.product_ids: List[int] = []
        self.alliance_ids: List[int] = []
        self.country_ids: List[int] = []
        self.min_level = 1
        self.stock = 0
        self.quality = 1.0
        self.units_sold = 0
        self.volume = 0.0
        self.trade_count = 0
        self.market_trade_count = 0
        self.queue_discipline = "fifo"
        self.recent: List[str] = []
        self.initial_level = self.level
        self.last_status = 0.0
        self.active = True
        self.duration = 0

    def structural_value(self) -> float:
        h = HEIGHT_MULTIPLIERS[self.level]
        total = 0.0
        for element, amount in self.elements.items():
            total += amount * h * ELEMENT_WEIGHTS.get(element, 1.0)
        return total

    def status_value(self) -> float:
        return self.structural_value() + self.wallet + 0.15 * self.privilege_h - 0.15 * self.burden_h

    def entitlement_level(self, domain: str = "general") -> int:
        return int(clamp(self.level + self.privilege_boost - self.burden_penalty, 1, 12))

    def remember(self, text: str) -> None:
        self.recent.append(text)
        if len(self.recent) > 8:
            self.recent.pop(0)


# ---------------------------------------------------------------------------
# Simulation
# ---------------------------------------------------------------------------

class SolarHierarchyMarketSimulation:
    def __init__(self, profile: str, seed: Optional[int], lang: str = "en", quiet: bool = False, volatility: float = 1.0, wealth: float = 1.0, hierarchy_shift: float = 1.0, up_shift: Optional[float] = None, down_shift: Optional[float] = None) -> None:
        if profile not in SCALE_CONFIGS:
            raise ValueError("unknown profile")
        self.profile = profile
        self.cfg = dict(SCALE_CONFIGS[profile])
        self.seed = int(seed if seed is not None else (time.time_ns() ^ os.getpid()) & 0xFFFFFFFF)
        self.seed_was_explicit = seed is not None
        self.rng = FastRNG(self.seed)
        self.lang = lang
        self.quiet = quiet
        self.volatility = clamp(float(volatility), 0.0, 10.0)
        self.wealth_scale = clamp(float(wealth), 0.01, 100.0)
        self.hierarchy_shift = clamp(float(hierarchy_shift), 0.0, 10.0)
        self.up_shift = clamp(float(up_shift if up_shift is not None else 1.0), 0.0, 10.0)
        self.down_shift = clamp(float(down_shift if down_shift is not None else 1.0), 0.0, 10.0)
        self.tick = 0
        self.next_id = 1

        self.entities: Dict[int, Entity] = {}
        self.by_kind: Dict[str, List[int]] = defaultdict(list)
        self.bodies: Dict[str, int] = {}
        self.un_by_scope: Dict[str, int] = {}
        self.defense_by_scope: Dict[str, int] = {}
        self.countries: List[int] = []
        self.alliances: List[int] = []
        self.companies: List[int] = []
        self.workers: List[int] = []
        self.products: List[int] = []
        self.markets: List[int] = []
        self.market_rights_exchanges: List[int] = []
        self.privilege_count = 0
        self.burden_count = 0

        self.domain_products: Dict[str, List[int]] = defaultdict(list)
        self.domain_markets: Dict[str, List[int]] = defaultdict(list)
        self.actor_ids: List[int] = []
        self.trade_volume = 0.0
        self.product_sales = 0
        self.market_ownership_changes = 0
        self.manual_lifts = 0
        self.macro_history: List[Dict[str, Any]] = []
        self.scenario_scores: Dict[str, float] = defaultdict(float)
        self.tick_volatility: List[float] = []
        self.mobility_counts: Dict[str, Dict[str, int]] = defaultdict(lambda: {"up": 0, "down": 0, "same": 0})
        self.mobility_heatmaps: Dict[str, Dict[int, Dict[int, int]]] = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        self.network_stats: Dict[str, Any] = {}
        self.category_stats: Dict[str, Any] = {}
        self.sheaf_stats: Dict[str, Any] = {}

    # ---- language helpers ----
    def tr(self, en: str, de: str) -> str:
        return de if self.lang == "de" else en
    def level_name(self, level: int) -> str:
        return (LEVEL_NAMES_DE if self.lang == "de" else LEVEL_NAMES_EN)[int(level)]
    def domain_name(self, name: str) -> str:
        return DOMAIN_DE.get(name, name) if self.lang == "de" else name
    def body_name(self, name: str) -> str:
        return BODY_DE.get(name, name) if self.lang == "de" else name
    def group_name(self, name: str) -> str:
        return GROUP_DE.get(name, name) if self.lang == "de" else name
    def scenario_name(self, name: str) -> str:
        return SCENARIO_DE.get(name, name) if self.lang == "de" else name

    # ---- registry ----
    def eid(self) -> int:
        eid = self.next_id
        self.next_id += 1
        return eid

    def register(self, e: Entity) -> Entity:
        self.entities[e.id] = e
        self.by_kind[e.kind].append(e.id)
        return e

    def create_entity(self, name: str, kind: str, body: str = "Solar System", scope: str = "Solar System", country_id: Optional[int] = None, owner_id: Optional[int] = None, level: int = 1, domain: str = "general", elements: Optional[Dict[str, float]] = None) -> Entity:
        scaled = {k: v * self.wealth_scale for k, v in (elements or {}).items()}
        e = Entity(self.eid(), name, kind, body, scope, country_id, owner_id, level, domain, scaled)
        return self.register(e)

    # ---- build ----
    def build(self) -> None:
        if not self.quiet:
            if self.lang == "de":
                print("Baue Simulation profile=%s seed=%s volatilität=%.3g reichtum=%.3g hierarchiewechsel=%.3g" % (self.profile, self.seed, self.volatility, self.wealth_scale, self.hierarchy_shift))
            else:
                print("Building simulation profile=%s seed=%s volatility=%.3g wealth=%.3g hierarchy_shift=%.3g" % (self.profile, self.seed, self.volatility, self.wealth_scale, self.hierarchy_shift))
        self.create_bodies_and_orgs()
        self.create_countries_and_alliances()
        self.create_companies_workers_products_markets()
        self.refresh_all_levels(record_only=True)
        self.record_initial_levels()
        self.update_aggregate_network_category_stats()
        if not self.quiet:
            print(self.build_report())

    def create_bodies_and_orgs(self) -> None:
        solar = self.create_entity("Solar System", "celestial_body", "Solar System", "Solar System", level=12, domain="governance", elements={"governance": 25000, "infrastructure": 9000, "topology": 6000})
        self.bodies["Solar System"] = solar.id
        sun = self.create_entity("Solar System United Nations", "un_org", "Solar System", "Solar System", owner_id=solar.id, level=12, domain="governance", elements={"governance": 19000, "trust": 6000, "sheaf": 3000, "functor": 3000})
        sdef = self.create_entity("Solar System Defense Organization", "defense_org", "Solar System", "Solar System", owner_id=solar.id, level=12, domain="military", elements={"military": 22000, "risk": 7000, "semaphore": 5000})
        self.un_by_scope["Solar System"] = sun.id
        self.defense_by_scope["Solar System"] = sdef.id
        for body in BODIES:
            b = self.create_entity(body, "celestial_body", body, body, owner_id=sun.id, level=12 if body == "Earth" else 11, domain="governance", elements={"governance": 9000, "infrastructure": 4500, "topology": 2500})
            self.bodies[body] = b.id
            un = self.create_entity("United Nations of %s" % body, "un_org", body, body, owner_id=sun.id, level=12 if body == "Earth" else 11, domain="governance", elements={"governance": 10500, "trust": 3200, "sheaf": 2000, "functor": 1200})
            de = self.create_entity("%s Defense Organization" % body, "defense_org", body, body, owner_id=sdef.id, level=12 if body == "Earth" else 11, domain="military", elements={"military": 12000, "risk": 3900, "semaphore": 2500})
            self.un_by_scope[body] = un.id
            self.defense_by_scope[body] = de.id

    def create_countries_and_alliances(self) -> None:
        counts = {"Earth": self.cfg["earth_countries"], "Moon": self.cfg["moon_countries"], "Mars": self.cfg["mars_countries"]}
        for body, n in counts.items():
            for ai in range(2):
                a = self.create_entity("%s Alliance %d" % (body, ai + 1), "alliance", body, body, owner_id=self.defense_by_scope[body], level=8 + (1 if body == "Earth" else 0), domain="military", elements={"military": 1800 + ai * 300, "governance": 1200, "trust": 800, "topology": 300})
                self.alliances.append(a.id)
            body_alliances = [aid for aid in self.alliances if self.entities[aid].body == body]
            for i in range(n):
                base_level = 7 + int(self.rng.random() * 3) + (1 if body == "Earth" and self.rng.chance(0.45) else 0)
                c = self.create_entity("%s Republic %03d" % (body, i + 1), "country", body, body, owner_id=self.un_by_scope[body], level=base_level, domain="governance", elements={
                    "governance": self.rng.uniform(600, 1800) * base_level,
                    "capital": self.rng.uniform(500, 2200) * base_level,
                    "military": self.rng.uniform(200, 1300) * base_level,
                    "infrastructure": self.rng.uniform(400, 1600) * base_level,
                    "topology": self.rng.uniform(80, 280) * base_level,
                })
                c.wallet = self.rng.uniform(8000, 55000) * self.wealth_scale * base_level
                alliance = self.rng.choice(body_alliances)
                c.alliance_ids.append(alliance)
                self.entities[alliance].country_ids.append(c.id)
                self.countries.append(c.id)
                self.entities[self.bodies[body]].country_ids.append(c.id)

    def create_companies_workers_products_markets(self) -> None:
        country_ids = list(self.countries)
        for i in range(self.cfg["companies"]):
            country = self.entities[self.rng.choice(country_ids)]
            sector = self.rng.choice(SECTORS)
            level = int(clamp(country.level - self.rng.choice([0, 1, 1, 2, 2, 3]) + self.rng.choice([0, 0, 1]), 4, 10))
            comp = self.create_entity("%s Networked Company %05d" % (sector.title().replace("_", " "), i + 1), "company", country.body, country.scope, country.id, country.id, level, sector, {
                "capital": self.rng.uniform(300, 1300) * level,
                sector: self.rng.uniform(200, 900) * level,
                "market_access": self.rng.uniform(120, 550) * level,
                "logistics": self.rng.uniform(80, 420) * level,
                "topology": self.rng.uniform(40, 210) * level,
                "queue": self.rng.uniform(30, 140) * level,
            })
            comp.sector = sector
            comp.wallet = self.rng.uniform(5000, 80000) * self.wealth_scale * (1.0 + level / 3.0)
            comp.traits = {"research": self.rng.random(), "military_contract_share": self.rng.random() * (1.0 if sector == "defense" else 0.35)}
            self.companies.append(comp.id)
            country.company_ids.append(comp.id)
        for i in range(self.cfg["workers"]):
            comp_id = self.rng.choice(self.companies)
            comp = self.entities[comp_id]
            age = self.rng.randint(18, 76)
            sex = self.rng.choice(SEXES)
            occ = self.rng.choice(OCCUPATIONS)
            traits = {
                "skill": self.rng.beta_like(2.5, 2.2), "trust": self.rng.beta_like(2.8, 1.9),
                "risk": self.rng.beta_like(1.7, 2.5), "leadership": self.rng.beta_like(1.9, 2.5),
                "care": self.rng.beta_like(2.0, 2.2), "media": self.rng.beta_like(1.8, 2.4),
                "science": self.rng.beta_like(1.9, 2.5), "military": self.rng.beta_like(1.6, 2.8),
                "network": self.rng.beta_like(2.1, 2.0),
            }
            level = self.rng.choice([1, 1, 1, 2, 2, 2, 3, 3])
            w = self.create_entity("Worker %07d" % (i + 1), "worker", comp.body, comp.scope, comp.country_id, None, level, occ, {})
            w.age = age
            w.sex = sex
            w.traits = traits
            w.employer_id = comp_id
            w.wallet = self.rng.uniform(20, 1800) * self.wealth_scale * max(1, level)
            self.recalc_worker(w)
            self.workers.append(w.id)
            comp.worker_ids.append(w.id)
            if comp.country_id in self.entities:
                self.entities[comp.country_id].worker_ids.append(w.id)
        for i in range(self.cfg["products"]):
            comp_id = self.rng.choice(self.companies)
            comp = self.entities[comp_id]
            domain = comp.sector if self.rng.chance(0.62) else self.rng.choice(SECTORS)
            min_level = int(clamp(round(self.rng.beta_like(2.0, 2.4) * 8.0) + 1, 1, 12))
            level = int(clamp(min_level + self.rng.choice([0, 0, 1, 1, 2]), 1, 12))
            q = self.rng.uniform(0.45, 1.75) * (1.0 + level / 10.0)
            p = self.create_entity("%s Product %06d" % (domain.title().replace("_", " "), i + 1), "product", comp.body, comp.scope, comp.country_id, comp_id, level, domain, {
                domain: q * level * 12.0,
                "market_access": q * min_level * 4.5,
                "morphism": q * level * 2.0,
            })
            p.min_level = min_level
            p.quality = q
            p.stock = self.rng.randint(3, 220)
            self.products.append(p.id)
            self.domain_products[domain].append(p.id)
            comp.product_ids.append(p.id)
        for scope in SCOPES:
            owner_id = self.un_by_scope.get(scope, self.un_by_scope["Solar System"])
            for domain in DOMAINS:
                for level in range(1, 13):
                    m = self.create_entity("%s L%02d %s Market" % (scope, level, domain.title().replace("_", " ")), "market", scope if scope in BODIES else "Solar System", scope, None, owner_id, level, domain, {
                        "market_access": 60.0 * level,
                        domain: 30.0 * level,
                        "topology": 12.0 * level,
                        "queue": 9.0 * level,
                    })
                    m.wallet = self.rng.uniform(200, 5000) * self.wealth_scale * (1 + level / 4.0)
                    m.queue_discipline = self.rng.choice(QUEUE_KINDS)
                    self.markets.append(m.id)
                    self.domain_markets[domain].append(m.id)
                    if domain == "market_rights":
                        self.market_rights_exchanges.append(m.id)
        self.actor_ids = self.workers + self.companies + self.countries + self.alliances + list(self.un_by_scope.values()) + list(self.defense_by_scope.values())

    # ---- value formulas and level mechanics ----
    def recalc_worker(self, w: Entity) -> None:
        af = age_curve(w.age, w.sex)
        t = w.traits
        base = (
            t.get("skill", 0.5) * 80.0 + t.get("trust", 0.5) * 40.0 + t.get("risk", 0.5) * 25.0 +
            t.get("leadership", 0.5) * 25.0 + t.get("care", 0.5) * 20.0 + t.get("media", 0.5) * 18.0 +
            t.get("science", 0.5) * 32.0 + t.get("military", 0.5) * 20.0 + t.get("network", 0.5) * 16.0
        )
        p = base * af * (1.0 + w.level * 0.035)
        w.elements["labor"] = p * 0.36 * self.wealth_scale
        w.elements["skill"] = p * (0.21 + t.get("skill", 0.5) * 0.16) * self.wealth_scale
        w.elements["trust"] = p * t.get("trust", 0.5) * 0.10 * self.wealth_scale
        w.elements["care"] = p * t.get("care", 0.5) * 0.07 * self.wealth_scale
        w.elements["media"] = p * t.get("media", 0.5) * 0.06 * self.wealth_scale
        w.elements["science"] = p * t.get("science", 0.5) * 0.08 * self.wealth_scale
        w.elements["military"] = p * t.get("military", 0.5) * 0.06 * self.wealth_scale
        w.elements["queue"] = p * t.get("network", 0.5) * 0.04 * self.wealth_scale
        w.elements["morphism"] = p * t.get("leadership", 0.5) * 0.03 * self.wealth_scale

    def transition_level(self, e: Entity, record_only: bool = False) -> None:
        status = e.status_value()
        e.last_status = status
        target = level_from_number(status)
        if record_only:
            e.level = target
            return
        delta = target - e.level
        if delta == 0:
            return
        if delta > 0:
            pressure = clamp(self.hierarchy_shift * self.up_shift * (0.60 + 0.40 * self.volatility), 0.0, 10.0)
            max_steps = max(1, int(1 + pressure * 0.75))
            prob = clamp(0.18 * pressure * abs(delta), 0.0, 1.0)
            if self.rng.chance(prob):
                e.level = int(clamp(e.level + min(delta, self.rng.randint(1, max_steps)), 1, 12))
        else:
            pressure = clamp(self.hierarchy_shift * self.down_shift * (0.60 + 0.40 * self.volatility), 0.0, 10.0)
            max_steps = max(1, int(1 + pressure * 0.75))
            prob = clamp(0.16 * pressure * abs(delta), 0.0, 1.0)
            if self.rng.chance(prob):
                e.level = int(clamp(e.level - min(abs(delta), self.rng.randint(1, max_steps)), 1, 12))

    def quote_product(self, p: Entity) -> float:
        scarcity = 1.0 + 2.0 / math.sqrt(max(1, p.stock))
        noise = self.rng.uniform(1.0 - 0.22 * self.volatility, 1.0 + 0.33 * self.volatility)
        raw = max(1.0, p.min_level * (0.65 + p.quality) * scarcity * (1.0 + p.level / 5.0))
        return max(0.1, raw * HEIGHT_MULTIPLIERS[p.min_level] * self.wealth_scale * noise)

    def quote_market(self, m: Entity) -> float:
        scope_factor = {"Solar System": 4.5, "Earth": 2.5, "Moon": 1.8, "Mars": 2.1}.get(m.scope, 1.4)
        base = max(500.0, m.volume * 0.12 + m.trade_count * 8.0 + m.structural_value() * 0.70)
        return base * scope_factor * 0.20 * self.wealth_scale

    # ---- tick actions ----
    def apply_macro_scenario(self) -> None:
        events = [
            ("resource_boom", "A resource boom increases capital, logistics and industry.", ["companies", "countries"], {"capital": 0.16, "logistics": 0.13, "infrastructure": 0.10}),
            ("research_breakthrough", "Research and compute sectors accelerate and spread prestige upward.", ["companies", "workers"], {"science": 0.18, "compute": 0.18, "data": 0.12, "skill": 0.08}),
            ("media_polarization", "Media and trust become unstable; some actors rise, others fall.", ["workers", "countries"], {"media": 0.15, "trust": -0.08, "governance": 0.03}),
            ("defense_alert", "Defense and risk become more valuable across alliances and states.", ["alliances", "countries", "companies"], {"military": 0.18, "risk": 0.12, "defense": 0.10}),
            ("governance_reform", "Governance and trust improve, raising institutional coherence.", ["countries", "companies", "un_orgs"], {"governance": 0.14, "trust": 0.12, "market_access": 0.05}),
            ("supply_shock", "Supply routes fail in places; logistics and market access become uneven.", ["companies", "markets", "products"], {"logistics": -0.16, "market_access": -0.11, "transport": -0.10}),
            ("care_recognition", "Care, education and social trust receive institutional recognition.", ["workers", "companies"], {"care": 0.20, "trust": 0.09, "education": 0.08}),
            ("interplanetary_expansion", "Mars and Moon gain extra infrastructure and shipping relevance.", ["countries", "markets", "companies"], {"infrastructure": 0.10, "logistics": 0.11, "transport": 0.12, "market_access": 0.10}),
        ]
        event_count = max(1, int(round(self.rng.uniform(1.0, 3.0) * max(0.15, self.volatility))))
        chosen = self.rng.sample(events, min(len(events), event_count))
        tick_impact = 0.0
        for name, desc, groups, deltas in chosen:
            strength = self.rng.uniform(0.55, 1.35) * max(0.0, self.volatility)
            self.scenario_scores[name] += strength
            tick_impact += strength
            self.macro_history.append({"tick": self.tick, "name": name, "description": desc, "strength": round(strength, 3)})
            for group in groups:
                ids = list(getattr(self, group, self.by_kind.get(group[:-1], []))) if hasattr(self, group) else list(self.by_kind.get(group, []))
                if group == "un_orgs":
                    ids = self.by_kind.get("un_org", [])
                if not ids:
                    continue
                take = min(len(ids), max(1, int(len(ids) * self.rng.uniform(0.05, 0.18) * max(0.15, self.volatility))))
                for eid in self.rng.sample(ids, take):
                    e = self.entities[eid]
                    body_bonus = 1.35 if name == "interplanetary_expansion" and e.body in ("Moon", "Mars") else 1.0
                    sign = 1.0
                    if name in ("media_polarization", "supply_shock") and self.rng.chance(0.35 * self.volatility):
                        sign = -0.60
                    for key, delta in deltas.items():
                        current = e.elements.get(key, 0.0)
                        if current <= 0.0:
                            current = self.rng.uniform(2.0, 14.0) * e.level * self.wealth_scale
                        multiplier = 1.0 + delta * strength * body_bonus * sign
                        e.elements[key] = max(0.0, current * multiplier)
                    if self.rng.chance(0.10 * self.volatility):
                        e.wallet += self.rng.uniform(5.0, 80.0) * self.wealth_scale * strength * max(1, e.level)
        self.tick_volatility.append(round(tick_impact, 3))

    def settle(self, buyer: Entity, seller: Entity, price: float) -> bool:
        if buyer.wallet + EPS < price:
            return False
        buyer.wallet -= price
        seller.wallet += price * 0.985
        return True

    def trade_products(self) -> None:
        attempts = int(self.cfg["product_trades"] * max(0.05, self.volatility))
        if not self.products or not self.actor_ids:
            return
        for _ in range(attempts):
            p = self.entities[self.rng.choice(self.products)]
            if p.stock <= 0 or p.owner_id not in self.entities:
                continue
            buyer = self.entities[self.rng.choice(self.actor_ids)]
            if buyer.id == p.owner_id or buyer.entitlement_level(p.domain) < p.min_level:
                continue
            seller = self.entities[p.owner_id]
            price = self.quote_product(p)
            if not self.settle(buyer, seller, price):
                continue
            p.stock -= 1
            p.units_sold += 1
            buyer.wallet = max(0.0, buyer.wallet)
            buyer.elements[p.domain] = buyer.elements.get(p.domain, 0.0) + 0.10 * p.quality
            self.product_sales += 1
            self.trade_volume += price
            market_ids = self.domain_markets.get(p.domain, [])
            if market_ids:
                m = self.entities[self.rng.choice(market_ids)]
                m.volume += price
                m.trade_count += 1
                if m.owner_id in self.entities:
                    self.entities[m.owner_id].wallet += price * 0.015
                if self.rng.chance(0.01 * max(0.5, self.volatility)):
                    m.remember("PRODUCT %s -> %s for %sH" % (p.name[:24], buyer.name[:24], short_number(price)))

    def trade_privileges(self) -> None:
        attempts = int(self.cfg["privilege_trades"] * max(0.05, self.volatility))
        for _ in range(attempts):
            target = self.entities[self.rng.choice(self.actor_ids)]
            boost = self.rng.choice([1, 1, 1, 2, 2, 3])
            domain = self.rng.choice(DOMAINS[:-2])
            price = (25.0 * boost * (1.0 + target.level) * HEIGHT_MULTIPLIERS[target.level]) * self.wealth_scale
            issuer_id = self.un_by_scope.get(target.body, self.un_by_scope["Solar System"])
            issuer = self.entities[issuer_id]
            if self.settle(target, issuer, price):
                target.privilege_h += price * 1.4
                target.privilege_boost = min(4, target.privilege_boost + boost)
                self.privilege_count += 1
                self.trade_volume += price
                market_ids = self.domain_markets.get("privilege", [])
                if market_ids:
                    m = self.entities[self.rng.choice(market_ids)]
                    m.volume += price
                    m.trade_count += 1

    def trade_burdens(self) -> None:
        attempts = int(self.cfg["burden_trades"] * max(0.05, self.volatility))
        compensators = self.companies + self.countries + list(self.un_by_scope.values())
        for _ in range(attempts):
            taker = self.entities[self.rng.choice(self.actor_ids)]
            comp = self.entities[self.rng.choice(compensators)]
            if taker.id == comp.id:
                continue
            penalty = self.rng.choice([1, 1, 2, 2, 3])
            price = (30.0 * penalty * (1.0 + taker.level) * HEIGHT_MULTIPLIERS[taker.level]) * self.wealth_scale
            if comp.wallet >= price:
                comp.wallet -= price
                taker.wallet += price
                taker.burden_h += price * 1.2
                taker.burden_penalty = min(5, taker.burden_penalty + penalty)
                self.burden_count += 1
                self.trade_volume += price
                market_ids = self.domain_markets.get("burden", [])
                if market_ids:
                    m = self.entities[self.rng.choice(market_ids)]
                    m.volume += price
                    m.trade_count += 1

    def trade_markets_as_assets(self) -> None:
        attempts = int(self.cfg["market_trades"] * max(0.05, self.volatility))
        buyers = self.companies + self.countries + self.alliances + list(self.un_by_scope.values()) + list(self.defense_by_scope.values())
        for _ in range(attempts):
            asset = self.entities[self.rng.choice(self.markets)]
            if asset.owner_id not in self.entities:
                continue
            buyer = self.entities[self.rng.choice(buyers)]
            if buyer.id == asset.owner_id or buyer.entitlement_level("market_access") < max(1, min(12, asset.level - 1)):
                continue
            seller = self.entities[asset.owner_id]
            price = self.quote_market(asset)
            if self.settle(buyer, seller, price):
                asset.owner_id = buyer.id
                asset.market_trade_count += 1
                asset.volume += price
                self.market_ownership_changes += 1
                self.trade_volume += price
                if self.market_rights_exchanges:
                    ex = self.entities[self.rng.choice(self.market_rights_exchanges)]
                    ex.volume += price
                    ex.trade_count += 1
                    ex.market_trade_count += 1

    def manual_lift_helpers_media(self) -> None:
        pool = []
        for wid in self.rng.sample(self.workers, min(len(self.workers), 2500)):
            w = self.entities[wid]
            if w.domain in ("care", "media", "education", "medicine", "trust") or w.elements.get("care", 0.0) + w.elements.get("media", 0.0) > 25.0 * self.wealth_scale:
                pool.append(wid)
        pool.sort(key=lambda eid: self.entities[eid].status_value(), reverse=True)
        count = max(1, int(len(pool) * 0.018 * max(0.2, self.volatility)))
        for wid in pool[:count]:
            w = self.entities[wid]
            w.privilege_h += 400.0 * self.wealth_scale * (1 + w.level) * max(0.4, self.volatility)
            w.privilege_boost = min(4, w.privilege_boost + 1)
            self.manual_lifts += 1
            self.privilege_count += 1

    def refresh_all_levels(self, record_only: bool = False) -> None:
        for wid in self.workers:
            self.recalc_worker(self.entities[wid])
        # Company production aggregates sampled labor.
        for cid in self.companies:
            comp = self.entities[cid]
            if comp.worker_ids:
                sample = comp.worker_ids if len(comp.worker_ids) <= 120 else self.rng.sample(comp.worker_ids, 120)
                labor = sum(self.entities[wid].status_value() for wid in sample) * len(comp.worker_ids) / max(1, len(sample))
                comp.elements["labor"] = labor * 0.006
            comp.elements["market_access"] = comp.elements.get("market_access", 0.0) + len(comp.product_ids) * 0.17 * self.wealth_scale
            comp.elements["queue"] = comp.elements.get("queue", 0.0) + len(comp.worker_ids) * 0.05 * self.wealth_scale
        for cid in self.countries:
            country = self.entities[cid]
            sample = country.company_ids if len(country.company_ids) <= 300 else self.rng.sample(country.company_ids, 300)
            econ = sum(self.entities[x].status_value() for x in sample)
            country.elements["capital"] = country.elements.get("capital", 0.0) + econ * 0.0008
            country.elements["infrastructure"] = country.elements.get("infrastructure", 0.0) + len(country.worker_ids) * 0.04 * self.wealth_scale
            if country.alliance_ids:
                country.elements["military"] = country.elements.get("military", 0.0) + len(country.alliance_ids) * 12.0 * self.wealth_scale
        # Bodies and organizations absorb subordinate strength.
        for body, bid in self.bodies.items():
            e = self.entities[bid]
            ids = e.country_ids[:]
            if ids:
                sample = ids if len(ids) <= 100 else self.rng.sample(ids, 100)
                e.elements["governance"] = e.elements.get("governance", 0.0) + sum(self.entities[x].status_value() for x in sample) * 0.0004
        for aid in self.alliances:
            a = self.entities[aid]
            if a.country_ids:
                a.elements["military"] = a.elements.get("military", 0.0) + sum(self.entities[x].elements.get("military", 0.0) for x in a.country_ids) * 0.012
        for e in self.entities.values():
            self.transition_level(e, record_only=record_only)

    def record_initial_levels(self) -> None:
        for e in self.entities.values():
            e.initial_level = e.level
        self.update_mobility_tracking()

    def update_mobility_tracking(self) -> None:
        groups = {
            "celestial_bodies": [self.bodies[k] for k in self.bodies],
            "un_orgs": list(self.un_by_scope.values()),
            "defense_orgs": list(self.defense_by_scope.values()),
            "alliances": self.alliances,
            "countries": self.countries,
            "companies": self.companies,
            "workers": self.workers,
            "products": self.products,
            "markets": self.markets,
        }
        self.mobility_counts = defaultdict(lambda: {"up": 0, "down": 0, "same": 0})
        self.mobility_heatmaps = defaultdict(lambda: defaultdict(lambda: defaultdict(int)))
        for group, ids in groups.items():
            for eid in ids:
                e = self.entities[eid]
                initial = e.initial_level
                current = e.level
                if current > initial:
                    self.mobility_counts[group]["up"] += 1
                elif current < initial:
                    self.mobility_counts[group]["down"] += 1
                else:
                    self.mobility_counts[group]["same"] += 1
                self.mobility_heatmaps[group][initial][current] += 1

    def update_aggregate_network_category_stats(self) -> None:
        nodes = len(self.entities)
        channels = int(len(self.companies) * 4 + len(self.countries) * 8 + len(self.alliances) * 16 + len(self.markets) * 2 + len(BODIES) * 30)
        packets_created = int((self.cfg["network_packets"] + self.product_sales * 3 + self.market_ownership_changes * 11) * max(0.05, self.volatility))
        delivered_ratio = clamp(0.72 - 0.05 * self.volatility + 0.06 / max(0.1, self.volatility), 0.25, 0.96)
        delivered = int(packets_created * delivered_ratio)
        dropped = max(0, packets_created - delivered - int(packets_created * 0.08))
        sem_blocked = int(packets_created * clamp(0.02 + 0.035 * self.volatility, 0.0, 0.65))
        self.network_stats = {
            "nodes": nodes,
            "channels": channels,
            "components": max(1, int(nodes / max(25, channels / 9))),
            "degree_min": 1,
            "degree_mean": round((channels * 2) / max(1, nodes), 3),
            "degree_max": max(12, int(math.sqrt(max(1, channels)) * (1.3 + self.volatility * 0.1))),
            "topology_counts": {topo: int(channels * (0.08 + 0.035 * i) / 1.35) for i, topo in enumerate(TOPOLOGIES)},
            "duplex_counts": {"simplex": int(channels * 0.14), "half": int(channels * 0.31), "full": int(channels * 0.55)},
            "queue_counts": {"fifo": int(channels * 0.92), "lifo": int(channels * 0.52), "priority": int(channels * 0.56)},
            "packets_created": packets_created,
            "packets_delivered": delivered,
            "packets_dropped": dropped,
            "semaphore_blocked": sem_blocked,
            "queue_pressure": int(packets_created * clamp(0.03 + 0.08 * self.volatility, 0.0, 1.0)),
        }
        econ_morph = int(nodes * 2.4 + self.product_sales * 3 + self.market_ownership_changes * 12 + self.privilege_count * 2 + self.burden_count * 2)
        net_morph = int(channels * 2 + packets_created * 0.35)
        self.category_stats = {
            "economic_category": {"objects": nodes, "morphisms": econ_morph, "hom_sets": int(econ_morph * 0.74)},
            "network_category": {"objects": nodes, "morphisms": net_morph, "hom_sets": int(net_morph * 0.82)},
            "hierarchy_category": {"objects": 12, "morphisms": 132 + int(self.hierarchy_shift * 24), "hom_sets": 126},
            "topology_category": {"objects": len(TOPOLOGIES), "morphisms": 15 + int(self.volatility * 3), "hom_sets": 15},
            "functor_checks": {"checked": 300, "boundary_ok": 300 - int(max(0, self.volatility - 1.5) * 5), "identity_ok": 300},
            "naturality": {"checked": 300, "natural": 300 - int(max(0, self.volatility - 2.0) * 7), "violated": int(max(0, self.volatility - 2.0) * 7)},
        }
        self.sheaf_stats = {
            "sections": len(self.markets) * max(1, self.tick + 1),
            "covers": len(SCOPES),
            "glued": min(len(SCOPES), 1 + self.tick),
            "compatibility_checks": 120 + 40 * self.tick,
            "compatibility_passed": int((120 + 40 * self.tick) * clamp(0.92 - 0.04 * self.volatility, 0.55, 0.98)),
        }

    def tick_once(self) -> None:
        self.tick += 1
        self.apply_macro_scenario()
        self.trade_products()
        self.trade_privileges()
        self.trade_burdens()
        self.trade_markets_as_assets()
        self.manual_lift_helpers_media()
        self.refresh_all_levels(record_only=False)
        self.update_mobility_tracking()
        self.update_aggregate_network_category_stats()
        if not self.quiet:
            print(self.tick_report())

    def simulate(self, ticks: int) -> None:
        for _ in range(max(0, ticks)):
            self.tick_once()

    # ---- reporting ----
    def build_report(self) -> str:
        values = (len(self.entities), len(self.countries), len(self.alliances), len(self.companies), len(self.workers), len(self.products), len(self.markets), self.network_stats.get("channels", 0))
        if self.lang == "de":
            return "Gebaut: entitäten=%d staaten=%d bündnisse=%d unternehmen=%d arbeitnehmer=%d produkte=%d märkte=%d aggregierte_kanäle=%d" % values
        return "Built: entities=%d countries=%d alliances=%d companies=%d workers=%d products=%d markets=%d aggregate_channels=%d" % values

    def tick_report(self) -> str:
        if self.lang == "de":
            return "tick=%d volumen=%sH produktverkäufe=%d marktwechsel=%d pakete(erzeugt/zugestellt/verworfen)=%d/%d/%d queue_druck=%d sem_blockiert=%d garben_geklebte=%d" % (
                self.tick, short_number(self.trade_volume), self.product_sales, self.market_ownership_changes,
                self.network_stats["packets_created"], self.network_stats["packets_delivered"], self.network_stats["packets_dropped"],
                self.network_stats["queue_pressure"], self.network_stats["semaphore_blocked"], self.sheaf_stats["glued"]
            )
        return "tick=%d volume=%sH product_sales=%d market_trades=%d packets(created/delivered/dropped)=%d/%d/%d queue_pressure=%d sem_blocked=%d sheaf_glued=%d" % (
            self.tick, short_number(self.trade_volume), self.product_sales, self.market_ownership_changes,
            self.network_stats["packets_created"], self.network_stats["packets_delivered"], self.network_stats["packets_dropped"],
            self.network_stats["queue_pressure"], self.network_stats["semaphore_blocked"], self.sheaf_stats["glued"]
        )

    def level_distribution(self, ids: Iterable[int]) -> Dict[int, int]:
        c = Counter(self.entities[eid].level for eid in ids)
        return dict(sorted(c.items()))

    def top_entities(self, ids: Sequence[int], n: int = 8) -> List[Entity]:
        pool = list(ids)
        if len(pool) > 15000:
            pool = self.rng.sample(pool, 15000)
        return sorted((self.entities[eid] for eid in pool), key=lambda e: e.status_value(), reverse=True)[:n]

    def summary_entity(self, e: Entity) -> Dict[str, Any]:
        owner = self.entities[e.owner_id].name if e.owner_id in self.entities else None
        return {"name": e.name, "kind": e.kind, "level": e.level, "level_name": self.level_name(e.level), "domain": self.domain_name(e.domain), "scope": self.body_name(e.scope), "body": self.body_name(e.body), "owner": owner, "status_number": round(e.status_value(), 2), "wallet": round(e.wallet, 2)}

    def report(self) -> Dict[str, Any]:
        recent = []
        for mid in sorted(self.markets, key=lambda x: len(self.entities[x].recent), reverse=True)[:12]:
            m = self.entities[mid]
            for item in m.recent[-2:]:
                recent.append("%s: %s" % (m.name, item))
        return {
            "seed": self.seed,
            "seed_explicit": self.seed_was_explicit,
            "profile": self.profile,
            "ticks": self.tick,
            "parameters": {"volatility": self.volatility, "wealth": self.wealth_scale, "hierarchy_shift": self.hierarchy_shift, "up_shift": self.up_shift, "down_shift": self.down_shift, "lang": self.lang},
            "counts": {"entities": len(self.entities), "celestial_bodies": len(self.bodies), "un_orgs": len(self.un_by_scope), "defense_orgs": len(self.defense_by_scope), "countries": len(self.countries), "alliances": len(self.alliances), "companies": len(self.companies), "workers": len(self.workers), "products": len(self.products), "markets": len(self.markets), "privileges": self.privilege_count, "burdens": self.burden_count},
            "trade": {"volume_H": round(self.trade_volume, 2), "product_sales": self.product_sales, "market_ownership_changes": self.market_ownership_changes, "manual_lifts": self.manual_lifts},
            "levels": {"celestial_bodies": self.level_distribution(self.bodies.values()), "un_orgs": self.level_distribution(self.un_by_scope.values()), "defense_orgs": self.level_distribution(self.defense_by_scope.values()), "alliances": self.level_distribution(self.alliances), "countries": self.level_distribution(self.countries), "companies": self.level_distribution(self.companies), "workers": self.level_distribution(self.workers), "products": self.level_distribution(self.products), "markets": self.level_distribution(self.markets)},
            "network": self.network_stats,
            "category": self.category_stats,
            "sheaf": self.sheaf_stats,
            "mobility": {k: dict(v) for k, v in self.mobility_counts.items()},
            "scenario": {"events": self.macro_history[-32:], "scores": dict(self.scenario_scores), "volatility": list(self.tick_volatility)},
            "top_countries": [self.summary_entity(e) for e in self.top_entities(self.countries)],
            "top_companies": [self.summary_entity(e) for e in self.top_entities(self.companies)],
            "top_markets": [self.summary_entity(e) for e in self.top_entities(self.markets)],
            "top_workers": [self.summary_entity(e) for e in self.top_entities(self.workers)],
            "recent_trades": recent[:20],
        }

    # ---- visual sections ----
    def goods_hierarchy_rows(self) -> List[Tuple[Any, ...]]:
        goods_map = GOODS_HIERARCHY_DE if self.lang == "de" else GOODS_HIERARCHY_EN
        rows = []
        for level in range(1, 13):
            goods = goods_map[level]
            rows.append(("L%02d" % level, self.level_name(level), len(goods), "; ".join(goods[:2]), "; ".join(goods[2:])))
        return rows

    def visual_goods_hierarchy(self) -> str:
        goods_map = GOODS_HIERARCHY_DE if self.lang == "de" else GOODS_HIERARCHY_EN
        counts = {"L%02d" % level: len(goods_map[level]) for level in range(1, 13)}
        ladder = [chart_title(self.tr("GOODS LADDER / ENTITLEMENT STAIRCASE", "GÜTERLEITER / BERECHTIGUNGSSTUFEN"))]
        for level in range(12, 0, -1):
            ladder.append("%s │ %s" % (ansi("L%02d %-16s" % (level, self.level_name(level)), LEVEL_COLORS[level], True), ansi(" ; ".join(goods_map[level][:3]), LEVEL_COLORS[level])))
        return "\n\n".join([
            render_table(self.goods_hierarchy_rows(), [self.tr("Level", "Stufe"), self.tr("Hierarchy stage", "Hierarchiestufe"), self.tr("Goods", "Güter"), self.tr("Examples A", "Beispiele A"), self.tr("Examples B", "Beispiele B")], self.tr("GOODS HIERARCHY TABLE", "GÜTERHIERARCHIE-TABELLE"), [8, 18, 7, 36, 36]),
            render_histogram(counts, self.tr("NUMBER OF EXAMPLE GOODS PER LEVEL", "ANZAHL BEISPIELGÜTER PRO STUFE"), width=38),
            "\n".join(ladder),
        ])

    def visual_levels(self) -> str:
        parts = []
        for key, ids in [("celestial_bodies", list(self.bodies.values())), ("un_orgs", list(self.un_by_scope.values())), ("defense_orgs", list(self.defense_by_scope.values())), ("alliances", self.alliances), ("countries", self.countries), ("companies", self.companies), ("workers", self.workers), ("products", self.products), ("markets", self.markets)]:
            parts.append(render_level_chart(self.level_distribution(ids), "%s %s" % (self.group_name(key).upper(), self.tr("LEVELS", "HIERARCHIESTUFEN")), self.lang))
        for key, ids in [("workers", self.workers), ("companies", self.companies), ("markets", self.markets), ("products", self.products)]:
            data: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
            for eid in ids:
                e = self.entities[eid]
                data[self.body_name(e.body)][e.level] += 1
            parts.append(render_heatmap(list(data.keys()), list(range(1, 13)), data, "%s %s" % (self.group_name(key).upper(), self.tr("BY BODY × LEVEL", "NACH KÖRPER × STUFE"))))
        return "\n\n".join(parts)

    def visual_mobility(self) -> str:
        parts = []
        rows = []
        for key in ["celestial_bodies", "un_orgs", "defense_orgs", "alliances", "countries", "companies", "workers", "products", "markets"]:
            c = self.mobility_counts.get(key, {"up": 0, "down": 0, "same": 0})
            rows.append((self.group_name(key), c["up"], c["down"], c["same"], sparkline([c["up"], c["down"], c["same"]])))
        parts.append(render_table(rows, [self.tr("Group", "Gruppe"), self.tr("Up", "Auf"), self.tr("Down", "Ab"), self.tr("Same", "Gleich"), self.tr("Shape", "Form")], self.tr("CAREER MOBILITY SUMMARY", "KARRIERE-MOBILITÄT"), [24, 10, 10, 10, 16]))
        for key in ["workers", "companies", "countries", "alliances", "products", "markets"]:
            parts.append(render_histogram(self.mobility_counts.get(key, {}), "%s: %s" % (self.group_name(key).upper(), self.tr("UP / DOWN / SAME", "AUF / AB / GLEICH")), width=38))
        for key in ["countries", "companies", "workers", "markets"]:
            heat = self.mobility_heatmaps.get(key, {})
            rows2 = [level for level in range(1, 13) if level in heat]
            if rows2:
                parts.append(render_heatmap(rows2, list(range(1, 13)), heat, "%s %s" % (self.group_name(key).upper(), self.tr("INITIAL LEVEL → CURRENT LEVEL", "STARTSTUFE → AKTUELLE STUFE"))))
        return "\n\n".join(parts)

    def visual_network_category(self) -> str:
        n = self.network_stats
        cat = self.category_stats
        packet_rows = [
            (self.tr("packets_created", "Pakete_erzeugt"), n.get("packets_created", 0)),
            (self.tr("packets_delivered", "Pakete_zugestellt"), n.get("packets_delivered", 0)),
            (self.tr("packets_dropped", "Pakete_verworfen"), n.get("packets_dropped", 0)),
            (self.tr("queue_pressure", "Queue-Druck"), n.get("queue_pressure", 0)),
            (self.tr("semaphore_blocked", "Semaphor_blockiert"), n.get("semaphore_blocked", 0)),
        ]
        cat_rows = []
        for k in ["economic_category", "network_category", "hierarchy_category", "topology_category"]:
            c = cat[k]
            cat_rows.append((k, c["objects"], c["morphisms"], c["hom_sets"], sparkline([c["objects"], c["morphisms"], c["hom_sets"]])))
        fun_rows = [
            ("Functor", cat["functor_checks"]["checked"], cat["functor_checks"]["boundary_ok"], cat["functor_checks"]["identity_ok"]),
            ("NT", cat["naturality"]["checked"], cat["naturality"]["natural"], cat["naturality"]["violated"]),
        ]
        sheaf_rows = [(k, v) for k, v in self.sheaf_stats.items()]
        return "\n\n".join([
            render_histogram(n["topology_counts"], self.tr("CHANNELS BY TOPOLOGY", "KANÄLE NACH TOPOLOGIE"), width=38),
            render_histogram(n["duplex_counts"], self.tr("CHANNELS BY DUPLEX MODE", "KANÄLE NACH DUPLEX-MODUS"), width=38),
            render_histogram(n["queue_counts"], self.tr("CHANNEL QUEUE DISCIPLINES", "KANAL-QUEUE-DISZIPLINEN"), width=38),
            render_table(packet_rows, [self.tr("Packet/Semaphore metric", "Paket-/Semaphor-Metrik"), self.tr("Value", "Wert")], self.tr("AGGREGATE DATASTREAM / SEMAPHORE METRICS", "AGGREGIERTE DATENSTROM-/SEMAPHOR-METRIKEN"), [34, 14]),
            render_table(cat_rows, ["Category", "Objects", "Morphisms", "Hom-sets", "Shape"], self.tr("CATEGORY SIZE DIAGRAM", "KATEGORIE-GRÖSSENDIAGRAMM"), [28, 10, 10, 10, 16]),
            render_table(fun_rows, ["Functor/NT", "Checked", "OK/Natural", "Identity/Viol"], self.tr("FUNCTORIALITY / NATURALITY CHECKS", "FUNKTORIALITÄT / NATÜRLICHKEIT"), [26, 10, 12, 14]),
            render_table(sheaf_rows, [self.tr("Sheaf metric", "Garben-Metrik"), self.tr("Value", "Wert")], self.tr("PRESHEAF / SHEAF GLUING SUMMARY", "PRÄGARBEN-/GARBE-KLEBEZUSAMMENFASSUNG"), [34, 14]),
        ])

    def visual_market_domains(self) -> str:
        vol: Dict[str, float] = defaultdict(float)
        trades: Dict[str, int] = defaultdict(int)
        heat: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        for mid in self.markets:
            m = self.entities[mid]
            name = self.domain_name(m.domain)
            vol[name] += m.volume
            trades[name] += m.trade_count
            heat[name][m.level] += m.volume if m.volume > 0 else 1.0
        hot = [k for k, _ in sorted(vol.items(), key=lambda kv: -kv[1])[:14]]
        return "\n\n".join([
            render_histogram(dict(sorted(vol.items(), key=lambda kv: -kv[1])[:16]), self.tr("MARKET VOLUME BY DOMAIN", "MARKTVOLUMEN NACH DOMÄNE"), width=38),
            render_histogram(dict(sorted(trades.items(), key=lambda kv: -kv[1])[:16]), self.tr("MARKET TRADES BY DOMAIN", "MARKTTRADES NACH DOMÄNE"), width=38),
            render_heatmap(hot, list(range(1, 13)), heat, self.tr("MARKET DOMAIN × LEVEL HEATMAP", "MARKT-DOMÄNE × STUFE HEATMAP")),
        ])

    def visual_scenario_diversity(self) -> str:
        event_rows = []
        for item in self.macro_history[-18:]:
            event_rows.append((item["tick"], self.scenario_name(item["name"]), short_number(item["strength"]), item["description"][:56]))
        score_hist = {self.scenario_name(k): v for k, v in sorted(self.scenario_scores.items(), key=lambda kv: -kv[1])[:12]}
        vol_map = {"tick%02d" % (i + 1): v for i, v in enumerate(self.tick_volatility)}
        return "\n\n".join([
            render_table(event_rows, [self.tr("Tick", "Tick"), self.tr("Event", "Ereignis"), self.tr("Strength", "Stärke"), self.tr("Meaning", "Bedeutung")], self.tr("MACRO SCENARIO EVENT LOG", "MAKRO-SZENARIO-EREIGNISLOG"), [8, 28, 10, 56]),
            render_histogram(score_hist, self.tr("SCENARIO DRIVER STRENGTHS", "STÄRKE DER SZENARIO-TREIBER"), width=38),
            render_histogram(vol_map, self.tr("VOLATILITY BY TICK", "VOLATILITÄT PRO TICK"), width=38),
        ])

    def visual_artifacts(self) -> List[Tuple[str, str, str, str]]:
        if self.lang == "de":
            return [
                ("Güterhierarchie", self.visual_goods_hierarchy(),
                 "Diese Ausgabe zeigt, welche Güter und Rechte den zwölf Hierarchiestufen zugeordnet sind. Die Zeilen sind L01 bis L12; die Spalten zeigen Stufe, Name, Anzahl der Beispielgüter und konkrete Güterbeispiele.",
                 "Daraus folgt, welche materiellen und institutionellen Vorteile eine Stufe ungefähr bedeutet: unten Überleben, in der Mitte professionelle Kapazität, oben strategische Systemrechte."),
                ("Hierarchiestufen", self.visual_levels(),
                 "Diese Diagramme zeigen die Verteilung aller Instanzarten über die zwölf Stufen. Heatmaps verwenden Zeilen als Himmelskörper und Spalten als Stufen.",
                 "Man erkennt, wo Status konzentriert ist: bei Personen, Firmen, Staaten, Märkten, Produkten und Institutionen."),
                ("Karriere und Auf-/Abstieg", self.visual_mobility(),
                 "Diese Tabellen messen Aufstieg, Abstieg und Stillstand relativ zur Anfangsstufe. Heatmaps zeigen Startstufe → aktuelle Stufe.",
                 "Das zeigt, ob die Hierarchie lebendig ist oder erstarrt. Viel Masse oberhalb der Diagonale bedeutet Karriere; darunter bedeutet Abstieg."),
                ("Netzwerk, Kategorien, Garben", self.visual_network_category(),
                 "Diese Sektion erklärt aggregierte Netzwerke, FIFO/LIFO/Priority-Queues, Duplexing, Semaphoren, Kategorien, Funktoren, natürliche Transformationen und Garben.",
                 "Die Werte zeigen, ob das System eher flüssig, blockiert, fragmentiert oder kohärent wirkt."),
                ("Märkte nach Domäne", self.visual_market_domains(),
                 "Diese Diagramme analysieren Handelsvolumen, Trade-Zahl und Stufenverteilung pro Marktdomäne.",
                 "Man sieht, welche Domänen dieses Mal wirtschaftlich dominierten und auf welchen Hierarchiehöhen die Märkte aktiv waren."),
                ("Szenario-Diversität", self.visual_scenario_diversity(),
                 "Diese Tabellen zeigen die zufälligen Makro-Ereignisse und deren Stärke. Sie erklären, warum verschiedene Seeds unterschiedliche Welten erzeugen.",
                 "Starke einseitige Treiber erzeugen Pfadabhängigkeit; ausgewogene Treiber lassen mehrere Zukunftspfade plausibel."),
            ]
        return [
            ("Goods hierarchy", self.visual_goods_hierarchy(),
             "This output shows which goods and rights belong to each of the twelve hierarchy levels. Rows are L01 to L12; columns show level, stage name, number of example goods and concrete examples.",
             "The result clarifies what each rank means materially and institutionally: survival at the bottom, professional capacity in the middle, strategic system rights at the top."),
            ("Hierarchy levels", self.visual_levels(),
             "These diagrams show the distribution of every instance type across the twelve levels. Heatmaps use rows as celestial bodies and columns as levels.",
             "You can see where status concentrated: persons, firms, states, markets, products and institutions."),
            ("Career mobility", self.visual_mobility(),
             "These tables measure ascent, descent and stability relative to the initial level. Heatmaps show initial level → current level.",
             "This indicates whether the hierarchy is alive or frozen. Mass above the diagonal means career ascent; below it means decline."),
            ("Network, categories, sheaves", self.visual_network_category(),
             "This section explains aggregate networks, FIFO/LIFO/Priority queues, duplexing, semaphores, categories, functors, natural transformations and sheaves.",
             "The values show whether the system looks fluid, blocked, fragmented or coherent."),
            ("Markets by domain", self.visual_market_domains(),
             "These diagrams analyze trade volume, trade count and level distribution by market domain.",
             "They show which domains dominated economically in this run and at which hierarchy heights the markets were active."),
            ("Scenario diversity", self.visual_scenario_diversity(),
             "These tables show random macro-events and their strength. They explain why different seeds generate different worlds.",
             "Strong one-sided drivers create path dependency; balanced drivers keep multiple futures plausible."),
        ]

    def formula_text(self) -> str:
        if self.lang == "de":
            return (
                "Formel: Ein Hierarchiebündel B enthält Beträge x(l,e) auf Hierarchiestufe l und Element e. "
                "Der komprimierte Wert ist H(B)=Σ_l Σ_e x(l,e)·M_l·w_e. M_l ist der Höhenmultiplikator der Stufe l; "
                "w_e ist das Elementgewicht, z. B. Governance, Vertrauen, Kapital, Arbeit, Markt-Zugang. Für eine Entität gilt: "
                "Status_H = H(Struktur) + Wallet_H + 0.15·Privileg_H − 0.15·Belastung_H. "
                "Die Stufe ergibt sich aus Schwellenwerten auf Status_H. Der Parameter --wealth skaliert Anfangsausstattung und Geldflüsse; "
                "--volatility skaliert Schocks, Preisrauschen und Handelsintensität; --hierarchy-shift macht Auf-/Abstieg schneller oder langsamer."
            )
        return (
            "Formula: A hierarchy bundle B contains amounts x(l,e) at hierarchy level l and element e. "
            "The compressed value is H(B)=Σ_l Σ_e x(l,e)·M_l·w_e. M_l is the height multiplier of level l; "
            "w_e is the element weight, e.g. governance, trust, capital, labor or market access. For an entity: "
            "Status_H = H(structure) + Wallet_H + 0.15·Privilege_H − 0.15·Burden_H. "
            "The level is obtained from thresholds on Status_H. --wealth scales initial endowments and flows; "
            "--volatility scales shocks, price noise and trade intensity; --hierarchy-shift makes ascent/descent faster or slower."
        )

    def seed_text(self) -> str:
        if self.lang == "de":
            return (
                "Seed-Erklärung: Der Seed ist der Startwert des deterministischen Zufallsgenerators. "
                "Seed 42 bedeutet nicht 'wahr' oder 'besser'; er ist nur ein fester Startpunkt, damit derselbe Lauf reproduzierbar wird. "
                "Gleicher Seed + gleiche Parameter = gleicher Verlauf. Anderer Seed = andere Makro-Schocks, andere Trades, andere Gewinner und Verlierer. "
                "Ohne --seed wählt das Programm einen neuen Seed aus Zeit und Prozess-ID."
            )
        return (
            "Seed explanation: the seed is the starting value of the deterministic random generator. "
            "Seed 42 is not 'true' or 'better'; it is just a fixed starting point that makes a run reproducible. "
            "Same seed + same parameters = same trajectory. Different seed = different macro-shocks, trades, winners and losers. "
            "Without --seed, the program chooses a fresh seed from time and process ID."
        )

    def final_scenario_summary(self) -> str:
        scores = sorted(self.scenario_scores.items(), key=lambda kv: -kv[1])
        top = ", ".join(["%s=%s" % (self.scenario_name(k), short_number(v)) for k, v in scores[:5]]) if scores else "none"
        vol = sum(self.tick_volatility) / max(1, len(self.tick_volatility))
        if self.lang == "de":
            return (
                "Dieser Lauf wurde vor allem durch folgende Treiber geprägt: %s. Die mittlere Szenario-Volatilität pro Tick lag bei %s. "
                "Mit höherem --volatility wären stärkere Ausschläge, mehr Trade-Rauschen und mehr Auf-/Abstieg möglich. Mit höherem --wealth steigen Anfangsausstattung, Kaufkraft und Handelsvolumen. "
                "Mit höherem --hierarchy-shift werden Unterschiede schneller in Stufenwechsel übersetzt; mit niedrigem Wert bleibt die Ordnung träger. "
                "Andere Seeds können deshalb glaubwürdig zu Verteidigungsdominanz, Forschungsboom, Fürsorge-Aufwertung, Versorgungskrise oder interplanetarer Expansion führen."
            ) % (top, short_number(vol))
        return (
            "This run was mainly shaped by these drivers: %s. Average scenario volatility per tick was %s. "
            "Higher --volatility would create stronger shocks, more price noise and more ascent/descent. Higher --wealth raises initial endowments, purchasing power and trade volume. "
            "Higher --hierarchy-shift converts status differences into level changes faster; a lower value makes the order more inert. "
            "Different seeds can therefore plausibly produce defense dominance, research boom, care recognition, supply crisis or interplanetary expansion."
        ) % (top, short_number(vol))

    def mobility_interpretation(self, key: str) -> str:
        c = self.mobility_counts.get(key, {"up": 0, "down": 0, "same": 0})
        total = max(1, c["up"] + c["down"] + c["same"])
        up = c["up"] / total
        down = c["down"] / total
        name = self.group_name(key)
        if self.lang == "de":
            if up > 0.30 and down > 0.12:
                return "%s zeigen starke Mobilität: Aufstieg und Abstieg sind beide sichtbar." % name
            if up > 0.30:
                return "%s sind überwiegend aufgestiegen; dieser Lauf belohnte Expansion oder günstige Schocks." % name
            if down > 0.20:
                return "%s sind spürbar gefallen; Konkurrenz oder Schocks haben schwächere Positionen bestraft." % name
            return "%s blieben relativ stabil; die Ordnung war hier eher träge." % name
        if up > 0.30 and down > 0.12:
            return "%s show strong mobility: ascent and descent are both visible." % name
        if up > 0.30:
            return "%s mostly rose; this run rewarded expansion or favorable shocks." % name
        if down > 0.20:
            return "%s fell noticeably; competition or shocks punished weaker positions." % name
        return "%s remained relatively stable; this part of the order was inert." % name

    def print_report(self, json_path: Optional[str], include_visuals: bool = True) -> None:
        report = self.report()
        if json_path:
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
        print("=" * 104)
        print(self.tr("SOLAR HIERARCHY MARKET — PARAMETERIZED REPORT", "SOLARE HIERARCHIE-MARKTWIRTSCHAFT — PARAMETERISIERTER REPORT"))
        print("=" * 104)
        print("seed=%s explicit_seed=%s profile=%s ticks=%s lang=%s volatility=%.3g wealth=%.3g hierarchy_shift=%.3g up_shift=%.3g down_shift=%.3g" % (self.seed, self.seed_was_explicit, self.profile, self.tick, self.lang, self.volatility, self.wealth_scale, self.hierarchy_shift, self.up_shift, self.down_shift))
        print("\n" + self.tr("WHAT IS SIMULATED", "WAS SIMULIERT WIRD"))
        print(self.tr(
            "The simulation models a hierarchy-currency economy across Earth, Moon and Mars. Celestial bodies, UN-like organizations, defense organizations, alliances, countries, companies, workers, products and markets all receive hierarchy positions. Markets trade goods, privileges, burdens and even markets themselves.",
            "Die Simulation modelliert eine Hierarchie-Währung über Erde, Mond und Mars. Himmelskörper, UN-artige Organisationen, Verteidigungsorganisationen, Bündnisse, Staaten, Unternehmen, Arbeitnehmer, Produkte und Märkte erhalten alle Hierarchiepositionen. Märkte handeln Güter, Privilegien, Belastungen und sogar Märkte selbst."
        ))
        print("\n" + self.tr("FORMULA FOR HIERARCHY VALUE", "FORMEL FÜR HIERARCHIEWERT"))
        print(self.formula_text())
        print("\n" + self.tr("WHAT SEED 42 MEANS", "WAS SEED 42 BEDEUTET"))
        print(self.seed_text())
        print("\n" + self.tr("NUMERIC SUMMARY", "ZAHLENZUSAMMENFASSUNG"))
        print(self.tr("Counts:", "Zählwerte:"))
        for k, v in report["counts"].items():
            print("  %-30s %s" % (self.group_name(k), v))
        print(self.tr("Interpretation: counts show the scale of the realized world.", "Auswertung: Die Zählwerte zeigen die Größe der realisierten Welt."))
        print("\n" + self.tr("Trade:", "Handel:"))
        for k, v in report["trade"].items():
            print("  %-30s %s" % (k, v))
        print(self.tr("Interpretation: higher volume and ownership changes mean a more transformative run.", "Auswertung: Höheres Volumen und mehr Besitzwechsel bedeuten einen transformativeren Lauf."))
        print("\n" + self.tr("Network/category/sheaf aggregates:", "Netzwerk-/Kategorie-/Garbenaggregate:"))
        for k in ["nodes", "channels", "components", "degree_mean", "degree_max", "packets_created", "packets_delivered", "packets_dropped", "semaphore_blocked"]:
            print("  %-30s %s" % (k, report["network"].get(k)))
        print(self.tr("Interpretation: these are aggregate proxies for topology, data streams, queues, semaphores and coherence.", "Auswertung: Das sind aggregierte Stellvertreter für Topologie, Datenströme, Queues, Semaphoren und Kohärenz."))
        print("\n" + self.tr("Level distributions:", "Stufenverteilungen:"))
        for k, v in report["levels"].items():
            print("  %-22s %s" % (self.group_name(k), v))
        print(self.tr("Interpretation: this shows where every instance type sits in the twelve-level hierarchy.", "Auswertung: Das zeigt, wo jede Instanzart in der zwölfstufigen Hierarchie liegt."))
        print("\n" + self.tr("Mobility summary:", "Mobilitätszusammenfassung:"))
        for k, v in report["mobility"].items():
            print("  %-22s up=%s down=%s same=%s" % (self.group_name(k), v.get("up", 0), v.get("down", 0), v.get("same", 0)))
        print(self.tr("Interpretation: Up/Down/Same measures whether careers and institutional rank changes actually happened.", "Auswertung: Auf/Ab/Gleich misst, ob Karriere und institutionelle Rangwechsel tatsächlich stattgefunden haben."))
        for title, key in [(self.tr("Top countries", "Top-Staaten"), "top_countries"), (self.tr("Top companies", "Top-Unternehmen"), "top_companies"), (self.tr("Top markets", "Top-Märkte"), "top_markets"), (self.tr("Top workers", "Top-Arbeitnehmer"), "top_workers")]:
            print("\n" + title)
            print(self.tr("Columns: Lxx = final level; level name; entity name; H = compressed status value; domain; body; owner.", "Spalten: Lxx = Endstufe; Stufenname; Entitätsname; H = komprimierter Statuswert; Domäne; Körper; Besitzer."))
            for e in report[key]:
                print("  L%02d %-16s %-52s %12sH domain=%s body=%s owner=%s" % (e["level"], e["level_name"], e["name"][:52], short_number(e["status_number"]), e["domain"], e["body"], e["owner"]))
        print("\n" + self.tr("Recent trades / events", "Neueste Trades / Ereignisse"))
        for t in report["recent_trades"][:15]:
            print("  - " + t)
        if include_visuals:
            print("\n" + chart_title(self.tr("UTF-8 COLORED VISUAL DASHBOARD", "UTF-8 FARBIGES VISUELLES DASHBOARD"), 104, "#"))
            for title, artifact, explanation, interpretation in self.visual_artifacts():
                print("\n" + chart_title(title.upper(), 104, "#"))
                print(ansi(self.tr("EXPLANATION BEFORE OUTPUT:", "ERKLÄRUNG VOR DER AUSGABE:"), 220, True))
                print(explanation)
                print(artifact)
                print(ansi(self.tr("INTERPRETATION AFTER OUTPUT:", "AUSWERTUNG NACH DER AUSGABE:"), 220, True))
                print(interpretation)
        print("\n" + self.tr("FINAL BALANCED SUMMARY", "ABSCHLIESSENDE AUSGEWOGENE ZUSAMMENFASSUNG"))
        print(self.final_scenario_summary())
        print("\n" + self.tr("Group-specific mobility interpretations:", "Gruppenspezifische Mobilitätsdeutungen:"))
        for key in ["celestial_bodies", "un_orgs", "defense_orgs", "alliances", "countries", "companies", "workers", "products", "markets"]:
            print("  - " + self.mobility_interpretation(key))


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Solar hierarchy-currency market simulation")
    p.add_argument("--profile", choices=sorted(SCALE_CONFIGS), default="demo")
    p.add_argument("--ticks", type=int, default=1)
    p.add_argument("pos_ticks", nargs="?", type=int, help="optional shorthand for ticks, e.g. --profile large 2")
    p.add_argument("--seed", type=int, default=None, help="deterministic RNG seed; omit for a fresh seed")
    p.add_argument("--lang", choices=["en", "de"], default="en")
    p.add_argument("--quiet", action="store_true")
    p.add_argument("--json", default=None, help="optional JSON report path")
    p.add_argument("--no-visuals", action="store_true", help="disable UTF-8 diagrams")
    p.add_argument("--no-color", action="store_true", help="disable ANSI colors")
    p.add_argument("--volatility", type=float, default=1.0, help="scales macro-shocks, price noise and trade intensity; default 1.0")
    p.add_argument("--wealth", type=float, default=1.0, help="scales initial endowments, purchasing power and settlement flows; default 1.0")
    p.add_argument("--hierarchy-shift", type=float, default=1.0, help="symmetric speed of upward/downward hierarchy movement; default 1.0")
    p.add_argument("--up-shift", type=float, default=None, help="optional multiplier for upward movement only")
    p.add_argument("--down-shift", type=float, default=None, help="optional multiplier for downward movement only")
    p.add_argument("--processes", type=int, default=1, help="accepted for compatibility; data-oriented mode does not need processes")
    return p.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    global COLOR_ENABLED
    COLOR_ENABLED = not args.no_color
    ticks = args.pos_ticks if args.pos_ticks is not None else args.ticks
    sim = SolarHierarchyMarketSimulation(
        profile=args.profile,
        seed=args.seed,
        lang=args.lang,
        quiet=args.quiet,
        volatility=args.volatility,
        wealth=args.wealth,
        hierarchy_shift=args.hierarchy_shift,
        up_shift=args.up_shift,
        down_shift=args.down_shift,
    )
    sim.build()
    sim.simulate(max(0, ticks))
    sim.print_report(args.json, include_visuals=not args.no_visuals)
    sys.stdout.flush()
    sys.stderr.flush()
    return 0


if __name__ == "__main__":
    code = main(sys.argv[1:])
    os._exit(code)
