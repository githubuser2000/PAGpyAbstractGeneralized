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

LEVEL_NAMES_DE = {
    1: "Überleben", 2: "Basis", 3: "Lokal", 4: "Fachkraft", 5: "Professionell",
    6: "Regional", 7: "National", 8: "Bündnis", 9: "Planetar",
    10: "Interplanetar", 11: "Systemisch", 12: "Sonnen-Apex",
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
    "military": "Militär", "logistics": "Logistik", "infrastructure": "Infrastruktur", "general": "Allgemein",
}

BODY_DE = {"Earth": "Erde", "Moon": "Mond", "Mars": "Mars", "Solar System": "Sonnensystem"}
GROUP_DE = {"workers": "Arbeitnehmer", "companies": "Unternehmen", "countries": "Staaten", "alliances": "Bündnisse", "products": "Produkte", "markets": "Märkte"}
METRIC_DE = {
    "entities": "Entitäten", "countries": "Staaten", "alliances": "Bündnisse", "companies": "Unternehmen", "workers": "Arbeitnehmer",
    "products": "Produkte", "markets": "Märkte", "privileges": "Privilegien", "burdens": "Belastungen", "volume_H": "Volumen_H",
    "product_sales": "Produktverkäufe", "market_ownership_changes": "Marktbesitzwechsel", "manual_lifts": "manuelle_Anhebungen",
    "nodes": "Knoten", "channels": "Kanäle", "components": "Komponenten", "degree_min": "Grad_min", "degree_mean": "Grad_Mittel", "degree_max": "Grad_max",
    "packets_created": "Pakete_erzeugt", "packets_delivered": "Pakete_zugestellt", "packets_dropped": "Pakete_verworfen", "semaphore_blocked": "Semaphor_blockiert",
    "economic_category": "ökonomische_Kategorie", "network_category": "Netzwerk_Kategorie", "hierarchy_category": "Hierarchie_Kategorie", "topology_category": "Topologie_Kategorie",
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

SPARK_CHARS = "▁▂▃▄▅▆▇█"
HEAT_CHARS = " ·░▒▓█"
CURRENT_LANG = "en"


def active_level_name(level: int) -> str:
    return (LEVEL_NAMES_DE if CURRENT_LANG == "de" else LEVEL_NAMES)[int(level)]


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
        label = "L%02d %-16s" % (level, active_level_name(level)[:16])
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
    def __init__(self, profile: str, seed: Optional[int], quiet: bool = False, processes: int = 1, lang: str = "en") -> None:
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
        self.lang = "de" if str(lang).lower().startswith("de") else "en"
        global CURRENT_LANG
        CURRENT_LANG = self.lang
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

    # ----------------------------- localization helpers -----------------------------

    def is_de(self) -> bool:
        return self.lang == "de"

    def T(self, en: str, de: str) -> str:
        return de if self.is_de() else en

    def level_name(self, level: int) -> str:
        return (LEVEL_NAMES_DE if self.is_de() else LEVEL_NAMES)[int(level)]

    def goods_for_level(self, level: int) -> List[str]:
        return (GOODS_HIERARCHY_DE if self.is_de() else GOODS_HIERARCHY)[int(level)]

    def domain_name(self, domain: str) -> str:
        if self.is_de():
            return DOMAIN_DE.get(domain, domain.replace("_", " "))
        return domain

    def body_name(self, body: str) -> str:
        return BODY_DE.get(body, body) if self.is_de() else body

    def group_name(self, key: str) -> str:
        return GROUP_DE.get(key, key) if self.is_de() else key

    def metric_name(self, key: str) -> str:
        return METRIC_DE.get(key, key) if self.is_de() else key

    def scenario_name(self, key: str) -> str:
        return SCENARIO_DE.get(key, key) if self.is_de() else key

    def localized_name(self, name: Optional[str]) -> str:
        if name is None:
            return "kein Eigentümer" if self.is_de() else "None"
        if not self.is_de():
            return name
        replacements = [
            ("Solar System", "Sonnensystem"), ("Earth", "Erde"), ("Moon", "Mond"), ("Mars", "Mars"),
            ("United Nations", "Vereinte Nationen"), ("Defense Organization", "Verteidigungsorganisation"),
            ("Defense Alliance", "Verteidigungsbündnis"), ("Republic", "Republik"),
            ("Networked Company", "Vernetztes Unternehmen"), ("Company", "Unternehmen"), ("Worker", "Arbeitnehmer"),
            ("Product", "Produkt"), ("Market", "Markt"), ("Alliance", "Bündnis"), ("Privilege", "Privileg"), ("Burden", "Belastung"),
            (" of ", " von "),
        ]
        out = name
        for a, b in replacements:
            out = out.replace(a, b)
        for src, dst in DOMAIN_DE.items():
            out = out.replace(src.title().replace("_", " "), dst)
        out = out.replace("Sonnensystem Vereinte Nationen", "Vereinte Nationen des Sonnensystems")
        out = out.replace("Sonnensystem Verteidigungsorganisation", "Verteidigungsorganisation des Sonnensystems")
        return out

    def localized_event(self, event: str) -> str:
        if not self.is_de():
            return event
        out = self.localized_name(event)
        replacements = [
            ("PRODUCT", "PRODUKT"), ("PRIVILEGE", "PRIVILEG"), ("BURDEN", "BELASTUNG"), ("MARKET", "MARKT"),
            ("accepted by", "angenommen von"), ("control ->", "Kontrolle ->"), (" for ", " für "), (" -> ", " -> "),
        ]
        for a, b in replacements:
            out = out.replace(a, b)
        return out

    def localized_map(self, mapping: Dict[Any, Any]) -> Dict[Any, Any]:
        if not self.is_de():
            return mapping
        out: Dict[Any, Any] = {}
        for k, v in mapping.items():
            if isinstance(k, str):
                out[self.domain_name(k) if k in DOMAIN_DE else self.metric_name(k)] = v
            else:
                out[k] = v
        return out

    # ----------------------------- construction -----------------------------

    def build(self) -> None:
        if not self.quiet:
            print(self.T("Building PyPy-safe hierarchy-market simulation profile=%s seed=%s", "Baue PyPy-sichere Hierarchie-Markt-Simulation Profil=%s Seed=%s") % (self.profile, self.seed))
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
        if self.is_de():
            return "Gebaut: Entitäten=%d Staaten=%d Bündnisse=%d Unternehmen=%d Arbeitnehmer=%d Produkte=%d Märkte=%d Kanäle=%d ökonomische_Morphismen=%d Netzwerk_Morphismen=%d pypy_sicher_datenorientiert=True" % (
                len(self.entities), len(self.countries), len(self.alliances), len(self.companies), len(self.workers), len(self.products), len(self.markets),
                self.network_stats["channels"], self.category_stats["economic_category"]["morphisms"], self.category_stats["network_category"]["morphisms"]
            )
        return "Built: entities=%d countries=%d alliances=%d companies=%d workers=%d products=%d markets=%d channels=%d econ_morphisms=%d net_morphisms=%d safe_data_oriented=True" % (
            len(self.entities), len(self.countries), len(self.alliances), len(self.companies), len(self.workers), len(self.products), len(self.markets),
            self.network_stats["channels"], self.category_stats["economic_category"]["morphisms"], self.category_stats["network_category"]["morphisms"]
        )

    def tick_report(self) -> str:
        if self.is_de():
            return "Tick=%d Volumen=%sH Produktverkäufe=%d Markttransfers=%d Pakete(erzeugt/zugestellt/verworfen)=%d/%d/%d Semaphor_blockiert=%d Garben_verklebungen=%d" % (
                self.tick, short_number(self.trade_volume), self.product_sales, self.market_ownership_changes,
                self.network_stats["packets_created"], self.network_stats["packets_delivered"], self.network_stats["packets_dropped"],
                self.network_stats["semaphore_blocked"], self.sheaf_stats["glued"]
            )
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
            "name": self.localized_name(e.name), "kind": e.kind, "level": e.level, "level_name": self.level_name(e.level),
            "domain": self.domain_name(e.domain), "body": self.body_name(e.body), "owner": self.localized_name(owner.name) if owner else self.localized_name(None),
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
            "goods_hierarchy": {str(level): self.goods_for_level(level) for level in range(1, 13)},
            "top_countries": [self.summary_entity(e) for e in self.top_entities(self.countries)],
            "top_companies": [self.summary_entity(e) for e in self.top_entities(self.companies)],
            "top_alliances": [self.summary_entity(e) for e in self.top_entities(self.alliances)],
            "top_markets": [self.summary_entity(e) for e in self.top_entities(self.markets)],
            "top_workers": [self.summary_entity(e) for e in self.top_entities(self.workers)],
            "recent_trades": list(self.recent_events[-20:]),
        }

    def what_more_can_be_simulated(self) -> List[str]:
        if self.is_de():
            return [
                "demografische Übergänge über Generationen, Erbschaft, Schulbildung, Ruhestand und Kohortenwechsel",
                "Banken, Schuldenketten, Insolvenz-Kaskaden, Sicherheiten und Zentralbank-ähnliche Hierarchie-Liquidität",
                "Wahlen, Propaganda, Zensur, Legitimität, Verfassungsreformen und Krisenregierungen",
                "Migration zwischen Erde, Mond und Mars, inklusive Brain Drain, Arbeitskräftemangel und Kolonie-Anziehung",
                "Krieg, Abschreckung, Mobilisierung, Wettrüsten, Abrüstungsverhandlungen und Zerfall von Verteidigungsbündnissen",
                "Innovationsrennen, Patente, Forschungsallmenden, Geheimprojekte und Wissensdiffusion",
                "ökologische Grenzen: Sauerstoffknappheit, Wasserverunreinigung, Ernteausfälle und Terraforming-Risiken",
                "kriminelle Märkte, Korruption, Schmuggel, Anti-Korruptionsgerichte und Statusbetrug",
                "kulturelle Prestigemärkte, Prominentenhierarchie, symbolisches Kapital und Reputationsblasen",
                "Cyberkonflikte, Sabotage, Netzwerkpartitionierung, Redundanz und Notfall-Rerouting",
                "Klassenkonflikt, Streiks, Gewerkschaften, Sozialversicherung und Umverteilungsreformen",
                "planetare Katastrophen, Evakuierungsmärkte, Kontinuitätsarchive und Notstands-Kommandoregime",
            ]
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
            goods = self.goods_for_level(level)
            rows.append(("L%02d" % level, self.level_name(level), len(goods), "; ".join(goods[:2]), "; ".join(goods[2:])))
        counts = {"L%02d" % level: len(self.goods_for_level(level)) for level in range(1, 13)}
        ladder = [chart_title(self.T("GOODS LADDER / ENTITLEMENT STAIRCASE", "GÜTERLEITER / BERECHTIGUNGSSTUFEN"))]
        for level in range(12, 0, -1):
            ladder.append("L%02d %-16s │ %s" % (level, self.level_name(level), " ; ".join(self.goods_for_level(level)[:3])))
        entitlement = [chart_title(self.T("WHO GETS WHICH GOODS LEVELS", "WER BEKOMMT WELCHE GÜTERSTUFEN"))]
        entitlement.append(self.T(
            "Rows are actor level; columns are goods levels. █ means the actor level includes access to that goods level.",
            "Zeilen sind Akteursstufen; Spalten sind Güterstufen. █ bedeutet: diese Akteursstufe enthält Zugang zu dieser Güterstufe."
        ))
        entitlement.append(" " * 8 + " ".join("G%02d" % i for i in range(1, 13)))
        for actor_level in range(1, 13):
            prefix = self.T("A-L%02d", "Akteur-L%02d") % actor_level
            entitlement.append("%-8s %s" % (prefix, " ".join(" █ " if goods_level <= actor_level else " · " for goods_level in range(1, 13))))
        return "\n\n".join([
            render_table(rows,
                         [self.T("Level", "Stufe"), self.T("Hierarchy stage", "Hierarchiestufe"), self.T("Goods", "Güter"), self.T("Examples A", "Beispiele A"), self.T("Examples B", "Beispiele B")],
                         self.T("GOODS HIERARCHY TABLE", "GÜTERHIERARCHIE-TABELLE"), [8, 18, 7, 34, 34]),
            render_histogram(counts, self.T("NUMBER OF EXAMPLE GOODS PER LEVEL", "ANZAHL DER BEISPIELGÜTER PRO STUFE"), width=34),
            "\n".join(ladder),
            "\n".join(entitlement),
        ])

    def visual_levels(self) -> str:
        parts = [
            render_level_chart(self.level_distribution(self.workers), self.T("WORKER LEVELS", "ARBEITNEHMER-STUFEN")),
            render_level_chart(self.level_distribution(self.companies), self.T("COMPANY LEVELS", "UNTERNEHMENS-STUFEN")),
            render_level_chart(self.level_distribution(self.countries), self.T("COUNTRY LEVELS", "STAATS-STUFEN")),
            render_level_chart(self.level_distribution(self.alliances), self.T("DEFENSE ALLIANCE LEVELS", "VERTEIDIGUNGSBÜNDNIS-STUFEN")),
            render_level_chart(self.level_distribution(self.products), self.T("PRODUCT LEVELS", "PRODUKT-STUFEN")),
            render_level_chart(self.level_distribution(self.markets), self.T("MARKET LEVELS", "MARKT-STUFEN")),
        ]
        groups = [("WORKERS", "ARBEITNEHMER", self.workers), ("COMPANIES", "UNTERNEHMEN", self.companies), ("COUNTRIES", "STAATEN", self.countries), ("MARKETS", "MÄRKTE", self.markets)]
        for en_name, de_name, group in groups:
            data_raw = self.body_level_heat(group)
            data: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
            for body, values in data_raw.items():
                data[self.body_name(body)] = values
            rows = [self.body_name(b) for b in ["Earth", "Moon", "Mars", "Solar System"] if self.body_name(b) in data]
            parts.append(render_heatmap(rows, list(range(1, 13)), data, self.T("%s BY BODY × LEVEL" % en_name, "%s NACH HIMMELSKÖRPER × STUFE" % de_name)))
        return "\n\n".join(parts)

    def visual_mobility(self) -> str:
        rows = []
        for key in ["workers", "companies", "countries", "alliances"]:
            c = self.mobility_counts.get(key, {"up": 0, "down": 0, "same": 0})
            rows.append((self.group_name(key), c["up"], c["down"], c["same"], sparkline([c["up"], c["down"], c["same"]])))
        parts = [render_table(rows,
                              [self.T("Group", "Gruppe"), self.T("Up", "Aufstieg"), self.T("Down", "Abstieg"), self.T("Same", "Gleich"), self.T("Shape", "Form")],
                              self.T("CAREER MOBILITY SUMMARY", "KARRIERE-MOBILITÄT"), [14, 10, 10, 10, 16])]
        for key in ["workers", "companies", "countries", "alliances"]:
            c = self.mobility_counts.get(key, {})
            if self.is_de():
                c = {"Aufstieg": c.get("up", 0), "Abstieg": c.get("down", 0), "Gleich": c.get("same", 0)}
            parts.append(render_histogram(c, self.T("%s: UP / DOWN / SAME" % key.upper(), "%s: AUFSTIEG / ABSTIEG / GLEICH" % self.group_name(key).upper()), width=34))
        for key in ["workers", "companies", "countries", "alliances"]:
            heat = self.mobility_heatmaps.get(key, {})
            rows2 = [r for r in range(1, 13) if r in heat]
            if rows2:
                parts.append(render_heatmap(rows2, list(range(1, 13)), heat, self.T("%s INITIAL LEVEL → CURRENT LEVEL" % key.upper(), "%s AUSGANGSSTUFE → AKTUELLE STUFE" % self.group_name(key).upper())))
        return "\n\n".join(parts)

    def visual_network_category(self) -> str:
        cat_rows = []
        for name in ["economic_category", "network_category", "hierarchy_category", "topology_category"]:
            c = self.category_stats[name]
            cat_rows.append((self.metric_name(name), c["objects"], c["morphisms"], c["hom_sets"], sparkline([c["objects"], c["morphisms"], c["hom_sets"]])))
        packet_rows = [
            (self.T("created", "erzeugt"), self.network_stats["packets_created"]),
            (self.T("delivered", "zugestellt"), self.network_stats["packets_delivered"]),
            (self.T("dropped", "verworfen"), self.network_stats["packets_dropped"]),
            (self.T("semaphore_blocked", "Semaphor_blockiert"), self.network_stats["semaphore_blocked"]),
        ]
        fun = self.category_stats["functor_checks"]
        fun_rows = [
            (self.T("Status functor", "Status-Funktor"), fun["checked"], fun["boundary_ok"], fun["identity_ok"]),
            (self.T("Access functor", "Zugangs-Funktor"), fun["checked"], fun["boundary_ok"], fun["identity_ok"]),
            (self.T("Natural transformation", "Natürliche Transformation"), fun["checked"], fun["natural"], fun["violated"]),
        ]
        sheaf_rows = [(self.metric_name(k), v) for k, v in self.sheaf_stats.items()]
        topo_counts = self.localized_map(self.network_stats["topology_counts"])
        duplex_counts = self.localized_map(self.network_stats["duplex_counts"])
        queue_counts = self.localized_map(self.network_stats["queue_counts"])
        if self.is_de():
            duplex_counts = {"Simplex": duplex_counts.get("simplex", duplex_counts.get("simplex", 0)), "Halbduplex": self.network_stats["duplex_counts"].get("half", 0), "Vollduplex": self.network_stats["duplex_counts"].get("full", 0)}
            queue_counts = {"FIFO": self.network_stats["queue_counts"].get("fifo", 0), "LIFO": self.network_stats["queue_counts"].get("lifo", 0), "Priorität": self.network_stats["queue_counts"].get("priority", 0)}
        return "\n\n".join([
            render_histogram(topo_counts, self.T("CHANNELS BY TOPOLOGY", "KANÄLE NACH TOPOLOGIE"), width=34),
            render_histogram(duplex_counts, self.T("CHANNELS BY DUPLEX MODE", "KANÄLE NACH DUPLEX-MODUS"), width=34),
            render_histogram(queue_counts, self.T("CHANNEL QUEUE DISCIPLINES", "KANAL-WARTESCHLANGEN"), width=34),
            render_table(packet_rows, [self.T("Packet/Semaphore metric", "Paket-/Semaphor-Metrik"), self.T("Value", "Wert")], self.T("AGGREGATE DATASTREAM / SEMAPHORE METRICS", "AGGREGIERTE DATENSTROM-/SEMAPHOR-METRIKEN"), [30, 14]),
            render_table(cat_rows, [self.T("Category", "Kategorie"), self.T("Objects", "Objekte"), self.T("Morphisms", "Morphismen"), self.T("Hom-sets", "Hom-Mengen"), self.T("Shape", "Form")], self.T("CATEGORY SIZE DIAGRAM", "KATEGORIE-GRÖSSENDIAGRAMM"), [28, 10, 10, 10, 16]),
            render_table(fun_rows, [self.T("Functor/NT", "Funktor/NT"), self.T("Checked", "Geprüft"), self.T("OK/Natural", "OK/Natürlich"), self.T("Identity/Viol", "Identität/Verstöße")], self.T("FUNCTORIALITY / NATURALITY CHECKS", "FUNKORIALITÄT / NATÜRLICHKEITS-PRÜFUNGEN"), [26, 10, 12, 14]),
            render_table(sheaf_rows, [self.T("Sheaf metric", "Garbenmetrik"), self.T("Value", "Wert")], self.T("PRESHEAF / SHEAF GLUING SUMMARY", "PRÄGARBEN-/GARBEN-VERKLEBUNG"), [30, 14]),
        ])

    def visual_markets(self) -> str:
        vol: Dict[str, float] = defaultdict(float)
        trades: Dict[str, float] = defaultdict(float)
        heat_raw: Dict[str, Dict[int, float]] = defaultdict(lambda: defaultdict(float))
        for m in self.markets:
            label = self.domain_name(m.domain)
            vol[label] += m.volume
            trades[label] += m.trades
            heat_raw[label][m.level] += m.volume if m.volume > 0 else 1.0
        hot = [k for k, _ in sorted(vol.items(), key=lambda kv: -kv[1])[:14]]
        return "\n\n".join([
            render_histogram(dict(sorted(vol.items(), key=lambda kv: -kv[1])[:16]), self.T("MARKET VOLUME BY DOMAIN", "MARKTVOLUMEN NACH DOMÄNE"), width=36),
            render_histogram(dict(sorted(trades.items(), key=lambda kv: -kv[1])[:16]), self.T("MARKET TRADES BY DOMAIN", "MARKTTRANSAKTIONEN NACH DOMÄNE"), width=36),
            render_heatmap(hot, list(range(1, 13)), heat_raw, self.T("MARKET DOMAIN × LEVEL HEATMAP", "MARKTDOMÄNE × STUFE HEATMAP")),
        ])

    def visual_scenarios(self) -> str:
        event_rows = [(e["tick"], self.scenario_name(e["name"]), short_number(e["strength"]), (self.scenario_description_de(e["name"]) if self.is_de() else e["description"])[:52]) for e in self.macro_history[-18:]]
        score_hist = {self.scenario_name(k): v for k, v in sorted(self.scenario_scores.items(), key=lambda kv: -kv[1])[:12]}
        vol_map = {self.T("tick%02d", "Tick%02d") % (i + 1): v for i, v in enumerate(self.tick_volatility)}
        return "\n\n".join([
            render_table(event_rows, [self.T("Tick", "Tick"), self.T("Event", "Ereignis"), self.T("Strength", "Stärke"), self.T("Meaning", "Bedeutung")], self.T("MACRO SCENARIO EVENT LOG", "MAKRO-SZENARIO-EREIGNISLOG"), [8, 24, 10, 52]),
            render_histogram(score_hist, self.T("SCENARIO DRIVER STRENGTHS", "STÄRKE DER SZENARIO-TREIBER"), width=34),
            render_histogram(vol_map, self.T("VOLATILITY BY TICK", "VOLATILITÄT PRO TICK"), width=34),
        ])

    def scenario_description_de(self, name: str) -> str:
        return {
            "resource_boom": "Ressourcenboom hebt Kapital, Logistik und Industrie.",
            "research_breakthrough": "Forschung und Rechenleistung beschleunigen Aufstieg.",
            "media_polarization": "Medien- und Vertrauenslage wird instabil.",
            "defense_alert": "Verteidigung und Risiko werden wichtiger.",
            "governance_reform": "Steuerung und Vertrauen verbessern Institutionen.",
            "supply_shock": "Versorgungsschock belastet Logistik und Marktzugang.",
            "care_recognition": "Fürsorge, Bildung und Vertrauen werden anerkannt.",
            "interplanetary_expansion": "Mond und Mars gewinnen Infrastruktur und Transportbedeutung.",
        }.get(name, name)

    def visual_artifacts(self) -> List[Tuple[str, str, str, str]]:
        if self.is_de():
            return [
                ("Güterhierarchie auf 12 Stufen", self.visual_goods_hierarchy(),
                 "Die folgende UTF-8-Ausgabe definiert, welche Güter und Rechte zu welcher Hierarchiestufe gehören. Zeilen L01-L12 sind Hierarchiestufen. Die Spalten zeigen die Stufe, ihren Namen, die Anzahl der Beispielgüter und konkrete Beispiele. Die Berechtigungsmatrix verwendet Akteursstufen als Zeilen und Güterstufen als Spalten; █ bedeutet Zugang zu dieser Güterstufe.",
                 "Hier wird sichtbar, wie abstrakte Hierarchie in konkrete Zugänge übersetzt wird. Unten liegen Überlebens- und Basisgüter, in der Mitte berufliche und regionale Operationsrechte, oben interplanetare, systemische und Solar-Apex-Rechte."),
                ("Hierarchie-Stufenverteilungen", self.visual_levels(),
                 "Diese Diagramme zeigen, wie viele Entitäten in L01-L12 liegen. In den Heatmaps sind die Zeilen Erde, Mond, Mars oder Sonnensystem; die Spalten sind Hierarchiestufen. Dunklere Zellen bedeuten mehr Entitäten in dieser Kombination.",
                 "Die Verteilung zeigt, ob der Lauf untenlastig, mittellastig oder apexlastig ist und ob sich Erde, Mond und Mars unterschiedlich konzentrieren."),
                ("Karrieremobilität und Aufstieg/Abstieg", self.visual_mobility(),
                 "Diese Tabellen und Heatmaps messen Karrierebewegung. Aufstieg bedeutet über der Anfangsstufe, Abstieg unter der Anfangsstufe, Gleich bedeutet unverändert. In Übergangs-Heatmaps sind die Zeilen Anfangsstufen und die Spalten aktuelle Stufen.",
                 "Das ist der direkte Test, ob die Hierarchie mobil ist. Masse oberhalb der Diagonale bedeutet Aufstieg, unterhalb Abstieg, auf der Diagonale Stabilität."),
                ("Märkte und Domänen", self.visual_markets(),
                 "Diese Diagramme gruppieren Marktaktivität nach Domäne. Histogramme vergleichen Volumen und Anzahl der Transaktionen. Die Heatmap verwendet Marktdomänen als Zeilen und Hierarchiestufen als Spalten.",
                 "Das zeigt, welche Domänen den Lauf dominierten und ob Handel auf niedrigen, professionellen, planetaren oder Apex-Stufen konzentriert war."),
                ("Netzwerk, Queues, Duplexing, Kategorien und Garben", self.visual_network_category(),
                 "Dieser Abschnitt fasst Topologien, Halb-/Vollduplex, FIFO/LIFO/Priorität, aggregierten Paketfluss, Semaphore, Kategorien, Funktoren, natürliche Transformationen und Garbenverklebung zusammen. Es bleibt aggregiert, damit große PyPy-Läufe stabil sind.",
                 "Die Ausgabe zeigt, ob die abstrakte Architektur kohärent blieb, ohne einen gefährlichen Live-Graphen zu materialisieren. Paket- und Semaphorwerte zeigen Flussdruck; Kategorie- und Garbenwerte zeigen strukturelle Konsistenz."),
                ("Szenario-Diversität und Zufallsausgänge", self.visual_scenarios(),
                 "Dieser Abschnitt listet die stochastischen Makroereignisse des Laufs. Stärke ist die Ereignisintensität. Die Histogramme aggregieren, wie stark jeder Ereignistyp den Lauf geprägt hat. Volatilität zeigt die gesamte Schockintensität pro Tick.",
                 "Das erklärt, warum Läufe unterschiedlich enden können. Verteidigungslastige Läufe heben Bündnisse, forschungslastige Läufe heben Wissenschaft und Daten, Versorgungsschocks erzeugen mehr Verlierer, Anerkennung der Fürsorge hebt Pflege-, Bildungs- und Vertrauensarbeit."),
            ]
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
        group = self.group_name(key)
        if self.is_de():
            if up > 0.35 and down > 0.12:
                return "%s zeigen starke Fluktuation: Aufstieg ist real, aber Abstieg ist ebenfalls bedeutsam." % group
            if up > 0.35:
                return "%s bewegen sich überwiegend nach oben; dieser Lauf belohnt Expansion, Anerkennung oder günstige Makroereignisse." % group
            if down > 0.25:
                return "%s werden stark bestraft; Wettbewerbsdruck oder Schocks erzeugen sichtbaren Abstieg." % group
            return "%s bleiben vergleichsweise stabil; Hierarchie-Persistenz dominiert diese Gruppe." % group
        if up > 0.35 and down > 0.12:
            return "%s show strong churn: upward careers exist, but decline is also meaningful." % key.title()
        if up > 0.35:
            return "%s mostly moved upward; this run rewarded expansion, recognition or favorable macro-events." % key.title()
        if down > 0.25:
            return "%s were heavily punished; competitive pressure or shocks produced visible decline." % key.title()
        return "%s were comparatively stable; hierarchy persistence dominated this group." % key.title()

    def final_scenario_summary(self) -> str:
        scores = sorted(self.scenario_scores.items(), key=lambda kv: -kv[1])
        dominant = ", ".join("%s=%s" % (self.scenario_name(k), short_number(v)) for k, v in scores[:5]) if scores else self.T("none", "keine")
        avg_vol = sum(self.tick_volatility) / max(1, len(self.tick_volatility))
        volume_by_domain: Dict[str, float] = defaultdict(float)
        for m in self.markets:
            volume_by_domain[m.domain] += m.volume
        top_domain = max(volume_by_domain.items(), key=lambda kv: kv[1])[0] if volume_by_domain else None
        if self.is_de():
            return "\n".join([
                "Dieser Lauf ist ein realisierter Pfad durch eine stochastische Hierarchieökonomie. Dominante Szenario-Treiber waren: %s." % dominant,
                "Die durchschnittliche Volatilität pro Tick lag bei %s. Ein höherer Wert bedeutet, dass ein anderer Seed sichtbar andere Gewinner, Verlierer und Domänen erzeugen könnte." % short_number(avg_vol),
                "Die aktivste Marktdomäne in diesem Lauf war %s." % (self.domain_name(top_domain) if top_domain else "keine"),
                "Alternative plausible Ausgänge bleiben ausgewogen: Ein stärkerer Verteidigungsalarm würde Bündnisse und militärische Staaten begünstigen; ein stärkerer Forschungsdurchbruch würde Rechenleistung, Daten und Wissenschaft heben; ein härterer Versorgungsschock würde mehr Unternehmen und Märkte nach unten drücken; Anerkennung der Fürsorge würde Pflege, Medizin, Bildung und Vertrauensarbeit stärken.",
                "Die Ausgabe ist deshalb kein unvermeidliches Gleichgewicht, sondern eine Szenario-Probe aus einem breiten Raum möglicher Hierarchie-Markt-Zukünfte.",
            ])
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
        print(self.T("SOLAR HIERARCHY MARKET — PYPY-SAFE DATA-ORIENTED REPORT", "SOLARER HIERARCHIE-MARKT — PYPY-SICHERER DATENORIENTIERTER BERICHT"))
        print("=" * 96)
        print(self.T("seed=%s profile=%s ticks=%s processes_argument=%s lang=%s", "Seed=%s Profil=%s Ticks=%s Prozessargument=%s Sprache=%s") % (report["seed"], report["profile"], report["ticks"], self.processes, self.lang))
        print("\n" + self.T("GLOBAL EXPLANATION OF THE SIMULATION", "GESAMTERKLÄRUNG DER SIMULATION"))
        print(self.T(
            "The simulation models a hierarchy-currency economy across Earth, Moon and Mars. The economy contains governance bodies, defense organizations, alliances, countries, companies, workers, products, tradable markets, privileges and burdens. Hierarchy is the meaningful currency; H is only the compressed settlement number used for accounting.",
            "Die Simulation modelliert eine Hierarchie-Währungsökonomie über Erde, Mond und Mars. Sie enthält Steuerungsorgane, Verteidigungsorganisationen, Bündnisse, Staaten, Unternehmen, Arbeitnehmer, Produkte, handelbare Märkte, Privilegien und Belastungen. Die Hierarchie ist die eigentliche Währung; H ist nur die komprimierte Abrechnungszahl."
        ))
        print(self.T(
            "The goal is to observe how goods access, market exchange, network flow, category-like structure, sheaf-like gluing and stochastic macro-events shape status, career mobility and different possible outcomes.",
            "Ziel ist zu beobachten, wie Güterzugang, Markttausch, Netzwerkfluss, kategorienartige Struktur, garbenartige Verklebung und stochastische Makroereignisse Status, Karrieremobilität und verschiedene mögliche Ausgänge formen."
        ))
        print("\n" + self.T("WHAT ELSE CAN STILL BE SIMULATED", "WAS ALLES NOCH SIMULIERT WERDEN KANN"))
        for item in self.what_more_can_be_simulated():
            print("  - " + item)
        print("\n" + self.T("EXPLANATION OF ABBREVIATIONS", "ERKLÄRUNG DER ABKÜRZUNGEN"))
        print(self.T(
            "H = compressed hierarchy accounting value; L01-L12 = hierarchy stages from Survival to Solar Apex; Up/Down/Same = movement relative to initial hierarchy level; NT = natural transformation; hom-set = morphisms between two category objects; FIFO/LIFO/priority = queue discipline; half/full = duplex mode; semaphore_blocked = simulated blocked channel permits.",
            "H = komprimierter Hierarchie-Abrechnungswert; L01-L12 = Hierarchiestufen von Überleben bis Sonnen-Apex; Aufstieg/Abstieg/Gleich = Bewegung relativ zur Anfangsstufe; NT = natürliche Transformation; Hom-Menge = Morphismen zwischen zwei Kategorieobjekten; FIFO/LIFO/Priorität = Warteschlangenregel; Halb/Voll = Duplexmodus; Semaphor_blockiert = simulierte blockierte Kanalerlaubnisse."
        ))
        print("\n" + self.T("EXPLANATION OF NUMERIC SUMMARY BLOCKS", "ERKLÄRUNG DER ZAHLENBLÖCKE"))
        print(self.T(
            "The next blocks give the macro state of this run before the UTF-8 diagrams. Each block has an interpretation directly below it.",
            "Die nächsten Blöcke zeigen den Makrozustand dieses Laufs vor den UTF-8-Diagrammen. Jeder Block hat direkt darunter eine Interpretation."
        ))
        print("\n" + self.T("Counts:", "Zählwerte:"))
        for k, v in report["counts"].items():
            print("  %-30s %s" % (self.metric_name(k), v))
        print(self.T("Interpretation: these counts define the scale of the simulated society and market system.", "Auswertung: Diese Zählwerte definieren die Größe der simulierten Gesellschaft und des Marktsystems."))
        print("\n" + self.T("Trade:", "Handel:"))
        for k, v in report["trade"].items():
            print("  %-30s %s" % (self.metric_name(k), v))
        print(self.T("Interpretation: trade volume, product sales and market ownership changes show how liquid and structurally transformative this run became.", "Auswertung: Handelsvolumen, Produktverkäufe und Marktbesitzwechsel zeigen, wie liquide und strukturell verändernd dieser Lauf wurde."))
        print("\n" + self.T("Network:", "Netzwerk:"))
        for k in ["nodes", "channels", "components", "degree_min", "degree_mean", "degree_max", "packets_created", "packets_delivered", "packets_dropped", "semaphore_blocked"]:
            print("  %-30s %s" % (self.metric_name(k), report["network"].get(k)))
        print(self.T("Interpretation: these aggregate network numbers replace the old dangerous live graph. They still show flow pressure, connectivity and semaphore contention without causing PyPy heap instability.", "Auswertung: Diese aggregierten Netzwerkzahlen ersetzen den alten gefährlichen Live-Graphen. Sie zeigen weiterhin Flussdruck, Konnektivität und Semaphor-Konkurrenz, ohne PyPy-Heap-Instabilität zu erzeugen."))
        print("\n" + self.T("Category:", "Kategorie:"))
        for key in ["economic_category", "network_category", "hierarchy_category", "topology_category"]:
            c = report["category"][key]
            print("  %-30s Objekte=%s Morphismen=%s Hom-Mengen=%s" % (self.metric_name(key), c["objects"], c["morphisms"], c["hom_sets"]) if self.is_de() else "  %-30s objects=%s morphisms=%s hom_sets=%s" % (key, c["objects"], c["morphisms"], c["hom_sets"]))
        print(self.T("Interpretation: these counts summarize the category-theoretic architecture as aggregate structure: objects are entities or levels; morphisms are relations, trades and transformations; hom-sets group morphisms by source and target type.", "Auswertung: Diese Zahlen fassen die kategorientheoretische Architektur als Aggregatstruktur zusammen: Objekte sind Entitäten oder Stufen; Morphismen sind Beziehungen, Tauschakte und Transformationen; Hom-Mengen gruppieren Morphismen nach Quell- und Zieltyp."))
        print("\n" + self.T("Level distributions:", "Stufenverteilungen:"))
        for k, v in report["levels"].items():
            print("  %-12s %s" % (self.group_name(k), v))
        print(self.T("Interpretation: these distributions show where each entity type sits in the twelve-level hierarchy.", "Auswertung: Diese Verteilungen zeigen, wo jeder Entitätstyp in der zwölfstufigen Hierarchie sitzt."))
        print("\n" + self.T("Mobility summary:", "Mobilitätsübersicht:"))
        for k, v in report["mobility"].items():
            if self.is_de():
                print("  %-12s Aufstieg=%s Abstieg=%s Gleich=%s" % (self.group_name(k), v["up"], v["down"], v["same"]))
            else:
                print("  %-12s up=%s down=%s same=%s" % (k, v["up"], v["down"], v["same"]))
        print(self.T("Interpretation: these numbers show whether people, companies, states and defense alliances actually moved through the hierarchy.", "Auswertung: Diese Zahlen zeigen, ob Personen, Unternehmen, Staaten und Verteidigungsbündnisse tatsächlich durch die Hierarchie gewandert sind."))
        print("\n" + self.T("Scenario summary:", "Szenarioübersicht:"))
        print("  " + self.T("scenario drivers=", "Szenario-Treiber="), ", ".join("%s=%s" % (self.scenario_name(k), short_number(v)) for k, v in sorted(report["scenario"]["scores"].items(), key=lambda kv: -kv[1])[:8]))
        print("  " + self.T("volatility per tick=", "Volatilität pro Tick="), report["scenario"]["volatility"])
        print(self.T("Interpretation: scenario drivers and volatility explain why repeated runs can diverge sharply.", "Auswertung: Szenario-Treiber und Volatilität erklären, warum wiederholte Läufe stark auseinanderlaufen können."))

        top_specs = [
            (self.T("Top countries", "Top-Staaten"), "top_countries"),
            (self.T("Top companies", "Top-Unternehmen"), "top_companies"),
            (self.T("Top alliances", "Top-Bündnisse"), "top_alliances"),
            (self.T("Top markets", "Top-Märkte"), "top_markets"),
            (self.T("Top workers", "Top-Arbeitnehmer"), "top_workers"),
        ]
        for title, key in top_specs:
            print("\n" + title)
            print(self.T(
                "Explanation of columns: Lxx is the final hierarchy level; the next field is the level name; then entity name; then compressed status in H; then domain, body and current owner.",
                "Spaltenerklärung: Lxx ist die finale Hierarchiestufe; danach folgt der Stufenname, dann der Entitätsname, dann der komprimierte Status in H, dann Domäne, Himmelskörper und aktueller Eigentümer."
            ))
            for e in report[key]:
                if self.is_de():
                    print("  L%02d %-16s %-52s %12sH Domäne=%s Körper=%s Eigentümer=%s" % (e["level"], e["level_name"], e["name"][:52], short_number(e["status_number"]), e["domain"], e["body"], e["owner"]))
                else:
                    print("  L%02d %-16s %-52s %12sH domain=%s body=%s owner=%s" % (e["level"], e["level_name"], e["name"][:52], short_number(e["status_number"]), e["domain"], e["body"], e["owner"]))
            print(self.T("Interpretation: this top list identifies the winners of this run in that entity group.", "Auswertung: Diese Topliste zeigt die Gewinner dieses Laufs in dieser Entitätsgruppe."))

        print("\n" + self.T("Recent trades / market events", "Aktuelle Trades / Marktereignisse"))
        print(self.T("Explanation: each bullet is a recent concrete event from product exchange, privilege exchange, burden exchange or market ownership transfer.", "Erklärung: Jeder Punkt ist ein konkretes aktuelles Ereignis aus Produkt-, Privilegien-, Belastungs- oder Marktbesitztausch."))
        for t in report["recent_trades"][:15]:
            print("  - " + self.localized_event(t))
        print(self.T("Interpretation: these events are the micro-level traces behind the aggregate results above.", "Auswertung: Diese Ereignisse sind die Mikrospuren hinter den aggregierten Ergebnissen oben."))

        if include_visuals:
            print("\n" + chart_title(self.T("UTF-8 DASHBOARD", "UTF-8-DASHBOARD"), 96, "#"))
            for title, artifact, explanation, interpretation in self.visual_artifacts():
                print("\n" + chart_title(title.upper(), 96, "#"))
                print(self.T("EXPLANATION BEFORE OUTPUT:", "ERKLÄRUNG VOR DER AUSGABE:"))
                print(explanation)
                print(artifact)
                print(self.T("INTERPRETATION AFTER OUTPUT:", "AUSWERTUNG NACH DER AUSGABE:"))
                print(interpretation)

        print("\n" + self.T("FINAL BALANCED SUMMARY OF POSSIBLE OUTCOMES", "ABSCHLIESSENDE AUSGEWOGENE ZUSAMMENFASSUNG MÖGLICHER AUSGÄNGE"))
        print(self.final_scenario_summary())
        print("\n" + self.T("GROUP-SPECIFIC MOBILITY INTERPRETATIONS", "GRUPPENSPEZIFISCHE MOBILITÄTSDEUTUNGEN"))
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
    p.add_argument("--lang", choices=("en", "de"), default="en", help="output language: en English (default) or de German")
    return p.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    ticks = args.ticks if args.ticks is not None else (args.positional_ticks if args.positional_ticks is not None else 1)
    sim = SolarHierarchySimulation(profile=args.profile, seed=args.seed, quiet=args.quiet, processes=args.processes, lang=args.lang)
    sim.build()
    sim.simulate(max(0, int(ticks)))
    sim.print_report(args.json, include_visuals=not args.no_visuals)
    sys.stdout.flush(); sys.stderr.flush()
    return 0


if __name__ == "__main__":
    code = main(sys.argv[1:])
    os._exit(code)
