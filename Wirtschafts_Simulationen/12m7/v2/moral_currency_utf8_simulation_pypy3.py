#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Radial-hierarchical moral currency simulation
=============================================

PyPy3-compatible, standard library only.

The program simulates a vector-like currency layer for markets. The output is
intentionally very colorful and rich in UTF-8 terminal diagrams. It can print a
complete English report or a complete German report.

Run:
    pypy3 moral_currency_utf8_simulation_pypy3.py
    pypy3 moral_currency_utf8_simulation_pypy3.py --lang de
    pypy3 moral_currency_utf8_simulation_pypy3.py --seed 17 --ticks 8 --color always
"""

from __future__ import annotations

import argparse
import copy
import math
import os
import random
import re
import statistics
import sys
import textwrap
import time
from dataclasses import dataclass, field
from typing import Callable, Dict, Iterable, List, Optional, Sequence, Tuple

RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
UNDER = "\033[4m"
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
COLOR_ENABLED = True

# Every multi-letter abbreviation used in the report receives a stable color.
ABBR_COLORS: Dict[str, int] = {
    "GV": 46,   # goodness value / Gütewert
    "PV": 201,  # popularity value / Popularitätswert
    "HV": 226,  # hierarchy value / Hierarchiewert
    "AD": 51,   # axis direction / Achsendrehung
    "RW": 81,   # radial width / Radialweite
    "MW": 214,  # moral weight / Moralwert
    "IS": 39,   # institutional signal
    "PS": 207,  # population signal
    "KS": 118,  # knowledge signal
    "DG": 82,   # delta goodness
    "DP": 213,  # delta popularity
    "RP": 220,  # reference price
    "DI": 75,   # demand index
    "SU": 159,  # supply units
    "TR": 203,  # tax/relief rate
    "TX": 141,  # transactions
    "WP": 111,  # worker potential
    "SE": 207,  # selflessness
    "FR": 118,  # fairness rate
    "MG": 51,   # match grade
    "WA": 221,  # wage adjustment
    "SV": 81,   # share value
    "ER": 118,  # earnings rate
    "ES": 205,  # ethical spread
    "RS": 203,  # risk shadow
    "XR": 45,   # exchange rate
    "TC": 82,   # trust correction
    "RR": 196,  # risk reserve
    "RI": 203,  # risk index
    "SB": 45,   # solidarity buffer
    "PR": 220,  # premium reference
    "ND": 159,  # need
    "UP": 82,   # upward chance
    "DN": 196,  # downward pressure
    "MT": 214,  # movement trend
    "MP": 201,  # manipulation pressure
    "SP": 51,   # shield power
    "CL": 220,  # claim level
    "QU": 118,  # quota
    "IM": 147,  # impact mean
    "TD": 39,   # trend direction
    "EL": 82,   # ethical leverage
    "RM": 196,  # risk marker
}

UNIT_COLORS: Dict[str, int] = {
    "pts": 82,
    "Pkt": 82,
    "deg": 51,
    "Grad": 51,
    "MCU": 214,
    "MWU": 214,
    "EUR": 220,
    "%": 207,
    "pc": 118,
    "Stk": 118,
    "day": 39,
    "Tag": 39,
    "pers": 141,
    "Pers": 141,
    "tx": 208,
    "Tx": 208,
    "rate": 81,
    "Kurs": 81,
    "idx": 147,
    "Index": 147,
    "yr": 159,
    "Jahr": 159,
}

UNIT_BY_LANG = {
    "points": {"en": "pts", "de": "Pkt"},
    "degrees": {"en": "deg", "de": "Grad"},
    "mcu": {"en": "MCU", "de": "MWU"},
    "eur": {"en": "EUR", "de": "EUR"},
    "percent": {"en": "%", "de": "%"},
    "pieces": {"en": "pc", "de": "Stk"},
    "day": {"en": "day", "de": "Tag"},
    "people": {"en": "pers", "de": "Pers"},
    "tx": {"en": "tx", "de": "Tx"},
    "rate": {"en": "rate", "de": "Kurs"},
    "index": {"en": "idx", "de": "Index"},
    "year": {"en": "yr", "de": "Jahr"},
}


def tr(lang: str, en: str, de: str) -> str:
    return en if lang == "en" else de


def ansi(code: str) -> str:
    if not COLOR_ENABLED:
        return ""
    return "\033[" + code + "m"


def fg(n: int) -> str:
    return ansi("38;5;%d" % n)


def bg(n: int) -> str:
    return ansi("48;5;%d" % n)


def style(text: object, color: int = 15, *, bold: bool = False, dim: bool = False, under: bool = False) -> str:
    s = str(text)
    if not COLOR_ENABLED:
        return s
    prefix = ""
    if bold:
        prefix += BOLD
    if dim:
        prefix += DIM
    if under:
        prefix += UNDER
    return prefix + fg(color) + s + RESET


def ab(code: str) -> str:
    return style(code, ABBR_COLORS.get(code, 15), bold=True)


def unit_code(lang: str, key: str) -> str:
    return UNIT_BY_LANG[key][lang]


def un(lang: str, key: str) -> str:
    code = unit_code(lang, key)
    return style(code, UNIT_COLORS.get(code, 15), bold=True)


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", str(text))


def visible_len(text: object) -> int:
    return len(strip_ansi(str(text)))


def pad(text: object, width: int, align: str = "<") -> str:
    s = str(text)
    extra = max(0, width - visible_len(s))
    if align == ">":
        return " " * extra + s
    if align == "^":
        left = extra // 2
        return " " * left + s + " " * (extra - left)
    return s + " " * extra


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def signed(x: float, digits: int = 1) -> str:
    return ("%+." + str(digits) + "f") % x


def value_color(x: float) -> int:
    if x >= 75:
        return 82
    if x >= 40:
        return 118
    if x >= 0:
        return 226
    if x >= -35:
        return 208
    return 196


def color_num(x: float, digits: int = 1, *, signed_value: bool = False) -> str:
    c = value_color(x)
    fmt = signed(x, digits) if signed_value else (("%." + str(digits) + "f") % x)
    return style(fmt, c, bold=True)


def unit_num(lang: str, x: float, key: str, digits: int = 1, width: int = 8, signed_value: bool = False) -> str:
    return pad(color_num(x, digits, signed_value=signed_value), width, ">") + " " + un(lang, key)


def pct(lang: str, x: float, digits: int = 1, signed_value: bool = False) -> str:
    return unit_num(lang, x, "percent", digits=digits, width=7, signed_value=signed_value)


def eur(lang: str, x: float, digits: int = 2, signed_value: bool = False) -> str:
    return unit_num(lang, x, "eur", digits=digits, width=10, signed_value=signed_value)


def pts(lang: str, x: float, digits: int = 1, signed_value: bool = False) -> str:
    return unit_num(lang, x, "points", digits=digits, width=8, signed_value=signed_value)


def mcu(lang: str, x: float, digits: int = 1, signed_value: bool = False) -> str:
    return unit_num(lang, x, "mcu", digits=digits, width=8, signed_value=signed_value)


def deg(lang: str, x: float, digits: int = 1) -> str:
    return unit_num(lang, x, "degrees", digits=digits, width=8)


def repeat_gradient(char: str, length: int, colors: Sequence[int]) -> str:
    return "".join(style(char, colors[i % len(colors)], bold=True) for i in range(length))


def rule(width: int = 118) -> None:
    print(repeat_gradient("─", width, [240, 242, 244, 246, 248, 250, 252, 250, 248, 246, 244, 242]))


def title_bar(title: str, subtitle: str = "") -> None:
    width = 118
    rainbow = [196, 202, 208, 214, 220, 226, 118, 82, 45, 51, 39, 75, 111, 147, 201, 207]
    print()
    print(repeat_gradient("═", width, rainbow))
    print(style("◆ ", 214, bold=True) + style(title, 15, bold=True) + style(" ◆", 214, bold=True))
    if subtitle:
        print(style(subtitle, 159, bold=True))
    print(repeat_gradient("═", width, list(reversed(rainbow))))


def wrap_print(text: str, width: int = 110, indent: str = "  ") -> None:
    for para in text.split("\n"):
        if not para.strip():
            print()
            continue
        for line in textwrap.wrap(para, width=width, replace_whitespace=False):
            print(indent + line)


def row(cells: Sequence[object], widths: Sequence[int], aligns: Optional[Sequence[str]] = None) -> str:
    if aligns is None:
        aligns = ["<"] * len(cells)
    return "  ".join(pad(c, w, a) for c, w, a in zip(cells, widths, aligns))


def table(headers: Sequence[object], rows: Sequence[Sequence[object]], widths: Sequence[int], aligns: Optional[Sequence[str]] = None) -> None:
    print(row(headers, widths, aligns))
    print(row([style("─" * w, 244) for w in widths], widths))
    for r in rows:
        print(row(r, widths, aligns))


def signed_bar(x: float, width: int = 28, lo: float = -100.0, hi: float = 100.0) -> str:
    center = width // 2
    x = clamp(x, lo, hi)
    if x >= 0:
        n = int(round((x / hi) * center))
        return style("░" * center, 240) + style("█" * n, value_color(x), bold=True) + style("░" * (center - n), 240)
    n = int(round((abs(x) / abs(lo)) * center))
    return style("░" * (center - n), 240) + style("█" * n, value_color(x), bold=True) + style("░" * center, 240)


def positive_bar(x: float, width: int = 28, hi: float = 100.0, color: Optional[int] = None) -> str:
    x = clamp(x, 0.0, hi)
    n = int(round((x / hi) * width))
    c = color if color is not None else value_color(x)
    return style("█" * n, c, bold=True) + style("░" * (width - n), 240)


def sparkline(values: Sequence[float], color: int = 82, width: Optional[int] = None) -> str:
    if not values:
        return ""
    vals = list(values)
    if width and len(vals) > width:
        step = len(vals) / float(width)
        vals = [vals[int(i * step)] for i in range(width)]
    lo = min(vals)
    hi = max(vals)
    blocks = "▁▂▃▄▅▆▇█"
    if hi == lo:
        return style(blocks[3] * len(vals), color, bold=True)
    out = []
    for v in vals:
        idx = int(round((v - lo) / (hi - lo) * (len(blocks) - 1)))
        out.append(style(blocks[idx], color if v >= 0 else 196, bold=True))
    return "".join(out)


def heat_cell(value: float, lo: float = -100.0, hi: float = 100.0) -> str:
    value = clamp(value, lo, hi)
    if value >= 70:
        c = 82
    elif value >= 35:
        c = 118
    elif value >= 0:
        c = 226
    elif value >= -35:
        c = 208
    else:
        c = 196
    return bg(c) + style("  ", 15, bold=True) + RESET


def bullet(text: str, color: int = 220) -> None:
    print("  " + style("●", color, bold=True) + " " + text)


@dataclass
class MarketObject:
    key: str
    name_en: str
    name_de: str
    kind_en: str
    kind_de: str
    gv: float
    pv: float
    hv: float
    base_eur: float
    risk: float
    stock: int = 0
    demand: float = 0.0
    profit: float = 0.0
    tiers: List[int] = field(default_factory=list)
    owner_key: str = ""

    def name(self, lang: str) -> str:
        return self.name_en if lang == "en" else self.name_de

    def kind(self, lang: str) -> str:
        return self.kind_en if lang == "en" else self.kind_de

    def ad(self) -> float:
        ang = math.degrees(math.atan2(self.pv, self.gv))
        return ang + 360.0 if ang < 0 else ang

    def rw(self) -> float:
        return math.sqrt(self.gv * self.gv + self.pv * self.pv)

    def mw(self) -> float:
        return moral_weight(self.gv, self.pv, self.hv, self.risk)


@dataclass
class Worker:
    name: str
    wp: float
    se: float
    gv: float
    pv: float
    hv: float
    wage: float
    matched_key: str = ""

    def mw(self) -> float:
        return moral_weight((self.gv + self.se) / 2.0, self.pv, self.hv, max(0, 28 - self.wp * 0.18))


@dataclass
class Company:
    key: str
    name_en: str
    name_de: str
    gv: float
    pv: float
    hv: float
    base_price: float
    profit: float
    employees: int
    risk: float
    share: float = 0.0

    def name(self, lang: str) -> str:
        return self.name_en if lang == "en" else self.name_de

    def mw(self) -> float:
        return moral_weight(self.gv, self.pv, self.hv, self.risk)


@dataclass
class Country:
    key: str
    name: str
    gv: float
    pv: float
    hv: float
    risk: float
    course: float = 1.0

    def mw(self) -> float:
        return moral_weight(self.gv, self.pv, self.hv, self.risk)


@dataclass
class InsuranceCase:
    key: str
    name_en: str
    name_de: str
    risk: float
    gv: float
    hv: float
    nd: float
    premium_base: float

    def name(self, lang: str) -> str:
        return self.name_en if lang == "en" else self.name_de

    def mw(self) -> float:
        return moral_weight(self.gv, 0.0, self.hv, self.risk)


class World:
    def __init__(self, seed: int, ticks: int, compact: bool = False) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.ticks = max(1, ticks)
        self.compact = compact
        self.resource_stock = 86
        self.products: List[MarketObject] = []
        self.companies: List[Company] = []
        self.workers: List[Worker] = []
        self.countries: List[Country] = []
        self.insurance_cases: List[InsuranceCase] = []
        self._make_world()

    def jitter(self, x: float, amount: float) -> float:
        return x + self.rng.uniform(-amount, amount)

    def _tiers(self, bias: float) -> List[int]:
        arr = []
        for stage in range(1, 6):
            center = 8.0 + bias * (stage - 3)
            arr.append(max(0, int(round(self.rng.gauss(center, 2.7)))))
        if sum(arr) == 0:
            arr[self.rng.randrange(5)] = 1
        return arr

    def _make_world(self) -> None:
        company_specs = [
            ("nova", "NovaCare", "NovaPflege", 78, 22, 64, 72.0, 18.0, 420, 18),
            ("hype", "HypeNet", "HypeNet", -36, 78, 71, 41.0, 32.0, 650, 58),
            ("solar", "SolarWorks", "SolarWerk", 82, 41, 69, 96.0, 27.0, 500, 21),
            ("fashion", "FastFashion", "SchnellMode", -44, 66, 45, 28.0, 22.0, 980, 62),
            ("data", "DataPilot", "DatenLotse", -55, 52, 73, 88.0, 36.0, 350, 74),
            ("learn", "LearningHarbor", "LernHafen", 73, 16, 51, 39.0, 13.0, 210, 12),
            ("clinic", "ClinicUnion", "KlinikBund", 86, -8, 76, 110.0, 9.0, 1200, 17),
            ("bank", "SpeculaBank", "SpekulaBank", -18, 44, 81, 150.0, 48.0, 260, 69),
        ]
        for key, en, de, gv, pv, hv, bp, prof, emp, risk in company_specs:
            c = Company(
                key=key,
                name_en=en,
                name_de=de,
                gv=clamp(self.jitter(gv, 5), -100, 100),
                pv=clamp(self.jitter(pv, 8), -100, 100),
                hv=clamp(self.jitter(hv, 5), 0, 100),
                base_price=bp,
                profit=clamp(self.jitter(prof, 5), -20, 80),
                employees=emp,
                risk=clamp(self.jitter(risk, 8), 0, 100),
            )
            c.share = c.base_price * self.rng.uniform(0.84, 1.23)
            self.companies.append(c)

        prod_specs = [
            ("water_filter", "Healing-water filter", "Heilwasser-Filter", 81, 27, 64.0, 14, 180, "nova", 1.5),
            ("addiction_box", "Addiction-game box", "Suchtspiel-Box", -72, 84, 19.0, 82, 420, "hype", 0.8),
            ("care_robot", "Care robot", "Pflege-Roboter", 76, 13, 240.0, 22, 75, "nova", 2.2),
            ("cheap_fashion", "Cheap fashion bundle", "Billig-Modepaket", -49, 72, 12.0, 67, 900, "fashion", -0.4),
            ("open_course", "Open learning course", "Offener Lernkurs", 87, -5, 7.0, 8, 1200, "learn", 0.6),
            ("data_trade", "Private-data trade", "Privatdaten-Handel", -83, 61, 33.0, 91, 260, "data", 2.6),
            ("repair_lamp", "Repairable lamp", "Reparierbare Lampe", 65, -13, 31.0, 11, 380, "solar", 0.9),
            ("short_video", "Short-video app", "Kurzvideo-App", -29, 92, 0.0, 55, 10000, "hype", 1.1),
            ("eco_transport", "Eco transport", "Öko-Transport", 73, 38, 86.0, 20, 160, "solar", 1.6),
            ("status_watch", "Status watch", "Statusuhr", 4, 69, 510.0, 35, 60, "bank", 0.1),
            ("basic_research", "Basic research", "Grundlagenforschung", 93, -31, 0.0, 6, 999, "clinic", 3.0),
            ("security_software", "Security software", "Sicherheitssoftware", 68, 24, 49.0, 18, 340, "data", 2.0),
        ]
        for key, en, de, gv, pv, base, risk, stock, owner, bias in prod_specs:
            tiers = self._tiers(bias)
            hv = hierarchy_from_stages(tiers)
            self.products.append(
                MarketObject(
                    key=key,
                    name_en=en,
                    name_de=de,
                    kind_en="product",
                    kind_de="Produkt",
                    gv=clamp(self.jitter(gv, 8), -100, 100),
                    pv=clamp(self.jitter(pv, 10), -100, 100),
                    hv=hv,
                    base_eur=base,
                    risk=clamp(self.jitter(risk, 6), 0, 100),
                    stock=stock,
                    tiers=tiers,
                    owner_key=owner,
                )
            )

        first_names = [
            "Amina", "Bela", "Cem", "Daria", "Elif", "Falk", "Greta", "Hao", "Ida", "Jona",
            "Kira", "Luan", "Mina", "Niko", "Omar", "Pia", "Ravi", "Sofia", "Taro", "Yuna",
        ]
        for name in first_names:
            wp = clamp(self.rng.gauss(62, 18), 15, 100)
            se = clamp(self.rng.gauss(48, 22), -40, 100)
            gv = clamp(wp * 0.35 + se * 0.65 + self.rng.uniform(-18, 18), -100, 100)
            pv = clamp(self.rng.gauss(18, 35), -100, 100)
            hv = clamp(self.rng.gauss(38, 18), 0, 100)
            wage = 1500 + wp * 37 + hv * 28 + self.rng.uniform(-420, 420)
            self.workers.append(Worker(name, wp, se, gv, pv, hv, wage))

        self.countries = [
            Country("albia", "Albia", 62, 27, 55, 22),
            Country("borealis", "Borealis", 34, 44, 61, 33),
            Country("cyrenia", "Cyrenia", 75, -9, 71, 19),
            Country("deltora", "Deltora", -24, 71, 50, 67),
            Country("eldoria", "Eldoria", 49, 12, 37, 28),
            Country("feronia", "Feronia", -39, 38, 63, 72),
        ]
        for c in self.countries:
            c.gv = clamp(self.jitter(c.gv, 10), -100, 100)
            c.pv = clamp(self.jitter(c.pv, 10), -100, 100)
            c.hv = clamp(self.jitter(c.hv, 8), 0, 100)
            c.risk = clamp(self.jitter(c.risk, 8), 0, 100)
            c.course = 0.72 + (c.mw() + 80) / 250 + self.rng.uniform(-0.06, 0.06)

        self.insurance_cases = [
            InsuranceCase("care_pool", "care collective", "Pflegekollektiv", 28, 79, 62, 71, 210.0),
            InsuranceCase("data_platform", "data platform", "Datenplattform", 76, -51, 73, 42, 480.0),
            InsuranceCase("solar_fleet", "solar fleet", "Solarflotte", 24, 72, 57, 38, 330.0),
            InsuranceCase("fashion_chain", "fashion chain", "Modekette", 69, -42, 46, 29, 390.0),
            InsuranceCase("research_lab", "research lab", "Forschungslabor", 18, 91, 81, 88, 620.0),
            InsuranceCase("free_artists", "free artists", "Freie Künstler", 34, 41, 31, 65, 160.0),
        ]

    def all_objects(self) -> List[MarketObject]:
        company_objects = [
            MarketObject(
                key=c.key,
                name_en=c.name_en,
                name_de=c.name_de,
                kind_en="employer",
                kind_de="Arbeitgeber",
                gv=c.gv,
                pv=c.pv,
                hv=c.hv,
                base_eur=c.base_price,
                risk=c.risk,
                stock=c.employees,
                profit=c.profit,
            )
            for c in self.companies
        ]
        return self.products + company_objects


def radial_angle(gv: float, pv: float) -> float:
    angle = math.degrees(math.atan2(pv, gv))
    return angle + 360.0 if angle < 0 else angle


def radial_width(gv: float, pv: float) -> float:
    return math.sqrt(gv * gv + pv * pv)


def moral_weight(gv: float, pv: float, hv: float, risk: float = 0.0) -> float:
    base = 0.48 * gv + 0.18 * pv + 0.34 * hv
    penalty = 0.24 * abs(gv) if gv < 0 and pv > 35 else 0.0
    neglect_bonus = 0.12 * abs(pv) if gv > 45 and pv < 0 else 0.0
    risk_penalty = 0.22 * risk
    return clamp(base - penalty + neglect_bonus - risk_penalty, -120.0, 130.0)


def tax_relief_rate(gv: float, pv: float) -> float:
    if gv < -30 and pv > 20:
        return clamp(8 + abs(gv) * 0.25 + pv * 0.12, 0, 35)
    if gv > 35 and pv < 5:
        return -clamp(5 + gv * 0.12 + abs(pv) * 0.05, 0, 22)
    if gv > 35 and pv > 35:
        return -clamp(2 + gv * 0.04, 0, 8)
    return clamp((-gv) * 0.04 if gv < 0 else 0, 0, 10)


def hierarchy_from_stages(stages: Sequence[int]) -> float:
    total = sum(max(0, x) for x in stages)
    if total <= 0:
        return 0.0
    weighted = sum((i + 1) * max(0, x) for i, x in enumerate(stages)) / total
    return clamp((weighted - 1.0) / 4.0 * 100.0, 0.0, 100.0)


def explain_part(
    lang: str,
    title_en: str,
    title_de: str,
    what_en: str,
    what_de: str,
    why_en: str,
    why_de: str,
    abbreviations: Sequence[Tuple[str, str, str]],
    units: Sequence[Tuple[str, str, str]],
) -> None:
    title_bar(tr(lang, title_en, title_de))
    print(style(tr(lang, "What is simulated", "Was simuliert wird"), 220, bold=True) + style(" — ", 246) + tr(lang, what_en, what_de))
    print(style(tr(lang, "Why this is simulated", "Warum das simuliert wird"), 118, bold=True) + style(" — ", 246) + tr(lang, why_en, why_de))
    print()
    if abbreviations:
        print(style(tr(lang, "Abbreviations used only in this part", "Kürzel nur in diesem Simulationsteil"), 207, bold=True))
        for code, en, de in abbreviations:
            print("  " + ab(code) + style(" = ", 244) + tr(lang, en, de))
    if units:
        print(style(tr(lang, "Units used only in this part", "Einheiten nur in diesem Simulationsteil"), 45, bold=True))
        for key, en, de in units:
            print("  " + un(lang, key) + style(" = ", 244) + tr(lang, en, de))
    rule()


def scenario_eval(lang: str, rows: Sequence[Tuple[str, str, str]]) -> None:
    print()
    print(style(tr(lang, "Evaluation across possible starting scenarios", "Auswertung mehrerer möglicher Ausgangsszenarien"), 220, bold=True))
    headers = [tr(lang, "Starting scenario", "Ausgangsszenario"), tr(lang, "Simulated result", "Simulationsergebnis"), tr(lang, "Reading", "Lesart")]
    widths = [28, 34, 52]
    table(headers, rows, widths)


def compass_art(lang: str) -> None:
    top = tr(lang, "popular", "beliebt")
    bottom = tr(lang, "unpopular", "unbeliebt")
    left = tr(lang, "harmful", "schädlich")
    right = tr(lang, "good", "gut")
    toxic = tr(lang, "toxic", "toxisch")
    hype = tr(lang, "hype", "Hype")
    civic = tr(lang, "civic", "bürgerl.")
    trust = tr(lang, "trust", "Vertrauen")
    hidden = tr(lang, "hidden", "verdeckt")
    damage = tr(lang, "damage", "Schaden")
    needed = tr(lang, "needed", "nötig")
    service = tr(lang, "service", "Dienst")
    lines = [
        "                 ▲ " + top,
        "                 │",
        "      ╭──────────┼──────────╮",
        "      │ " + pad(toxic, 8, "^") + "│" + pad(civic, 10, "^") + "│",
        "      │ " + pad(hype, 8, "^") + "│" + pad(trust, 10, "^") + "│",
        "" + left + " ◀───┼──────────┼──────────┼───▶ " + right,
        "      │ " + pad(hidden, 8, "^") + "│" + pad(needed, 10, "^") + "│",
        "      │ " + pad(damage, 8, "^") + "│" + pad(service, 10, "^") + "│",
        "      ╰──────────┼──────────╯",
        "                 │",
        "                 ▼ " + bottom,
    ]
    palette = [196, 208, 226, 82, 45, 51, 201]
    for i, line in enumerate(lines):
        print("  " + style(line, palette[i % len(palette)], bold=True))


def scatter_map(lang: str, objects: Sequence[MarketObject], max_items: int = 18) -> None:
    width, height = 43, 19
    grid: List[List[str]] = [[style("·", 238) for _ in range(width)] for _ in range(height)]
    mid_x, mid_y = width // 2, height // 2
    for x in range(width):
        grid[mid_y][x] = style("─", 244)
    for y in range(height):
        grid[y][mid_x] = style("│", 244)
    grid[mid_y][mid_x] = style("┼", 250, bold=True)
    chosen = list(objects)[:max_items]
    legend = []
    symbols = "①②③④⑤⑥⑦⑧⑨⑩⑪⑫⑬⑭⑮⑯⑰⑱"
    for idx, obj in enumerate(chosen):
        x = int(round((obj.gv + 100.0) / 200.0 * (width - 1)))
        y = int(round((100.0 - (obj.pv + 100.0) / 200.0 * 200.0) / 200.0 * (height - 1)))
        # Equivalent: pv 100 top, -100 bottom.
        y = int(round((100.0 - obj.pv) / 200.0 * (height - 1)))
        symbol = symbols[idx]
        grid[y][x] = style(symbol, value_color(obj.mw()), bold=True)
        legend.append((symbol, obj.name(lang), obj.mw()))
    print("  " + style(tr(lang, "Popularity ↑", "Beliebtheit ↑"), 201, bold=True))
    for y in range(height):
        print("  " + "".join(grid[y]))
    print("  " + style(tr(lang, "Goodness −  ←──────────── center ────────────→  Goodness +", "Güte −  ←──────────── Mitte ────────────→  Güte +"), 46, bold=True))
    print()
    for symbol, name, mw in legend:
        print("  " + style(symbol, value_color(mw), bold=True) + " " + pad(style(name, 15, bold=True), 24) + mcu(lang, mw))


def hierarchy_tower(lang: str, name: str, stages: Sequence[int]) -> None:
    max_count = max(stages) if stages else 1
    print("  " + style(tr(lang, "Hierarchy stack for", "Hierarchiestapel für"), 220, bold=True) + " " + style(name, 15, bold=True))
    for idx in range(len(stages), 0, -1):
        count = stages[idx - 1]
        blocks = int(round(count / max(1, max_count) * 26))
        color = [111, 147, 201, 214, 82][idx - 1]
        label = tr(lang, "level", "Stufe") + " " + str(idx)
        print("  " + pad(label, 9) + style("▐", color, bold=True) + style("█" * blocks, color, bold=True) + style("░" * (26 - blocks), 240) + " " + str(count))


def signal_flow_art(lang: str) -> None:
    words = [
        (ab("IS"), tr(lang, "law / audit", "Recht / Prüfung"), 39),
        (ab("KS"), tr(lang, "evidence", "Evidenz"), 118),
        (ab("PS"), tr(lang, "public desire", "öffentlicher Wunsch"), 207),
    ]
    print("  " + style("╭" + "─" * 94 + "╮", 244))
    print("  " + style("│", 244) + " " + words[0][0] + " " + style("━▶", words[0][2], bold=True) + " " + pad(words[0][1], 18) + " " + style("┐", 244) + "                               " + style("┌", 244) + " " + words[2][0] + " " + style("◀━", words[2][2], bold=True) + " " + words[2][1])
    print("  " + style("│", 244) + " " + " " * 27 + style("├──────▶", 226, bold=True) + " " + style(tr(lang, "value vector", "Wertvektor"), 226, bold=True) + " " + style("◀──────┤", 226, bold=True))
    print("  " + style("│", 244) + " " + words[1][0] + " " + style("━▶", words[1][2], bold=True) + " " + pad(words[1][1], 18) + " " + style("┘", 244) + "                               " + style("└", 244) + " " + style(tr(lang, "slow correction", "langsame Korrektur"), 118, bold=True))
    print("  " + style("╰" + "─" * 94 + "╯", 244))


def funnel_art(lang: str) -> None:
    lines = [
        "████████████████████████████  " + tr(lang, "raw demand", "rohe Nachfrage"),
        "  ████████████████████████    " + tr(lang, "moral filter", "moralischer Filter"),
        "    ████████████████████      " + tr(lang, "tax or relief", "Steuer oder Entlastung"),
        "      ████████████████        " + tr(lang, "reference price", "Referenzpreis"),
        "        ████████████          " + tr(lang, "transactions", "Transaktionen"),
    ]
    for i, line in enumerate(lines):
        print("  " + style(line, [201, 51, 220, 118, 82][i], bold=True))


def labor_bipartite_art(lang: str) -> None:
    left = tr(lang, "workers", "Arbeitskräfte")
    right = tr(lang, "employers", "Arbeitgeber")
    print("  " + style("╭────────────╮        ╭──────────────╮", 244))
    print("  " + style("│", 244) + " " + style(left.center(10), 111, bold=True) + " " + style("│", 244) + style("  ╲  ╱  ╲  ╱  ", 250) + style("│", 244) + " " + style(right.center(12), 147, bold=True) + " " + style("│", 244))
    print("  " + style("│", 244) + " " + style("WP  SE  MW", 111, bold=True) + " " + style("│", 244) + style("──╳────╳──▶", 214, bold=True) + style("│", 244) + " " + style("FR  HV  MW", 147, bold=True) + "  " + style("│", 244))
    print("  " + style("╰────────────╯        ╰──────────────╯", 244))


def candles_art(lang: str, company_rows: Sequence[Tuple[str, List[float]]]) -> None:
    print("  " + style(tr(lang, "Mini share tracks", "Mini-Aktienverläufe"), 220, bold=True))
    for name, values in company_rows:
        last = values[-1]
        color = 82 if last >= values[0] else 196
        print("  " + pad(style(name, 15, bold=True), 18) + sparkline(values, color=color, width=28) + " " + eur(lang, last, 1))


def currency_wheel_art(lang: str, countries: Sequence[Country]) -> None:
    print("  " + style("           ◜──────────────◝", 45, bold=True))
    print("  " + style("      ◜────", 45, bold=True) + ab("XR") + style("────◝    ◜────", 45, bold=True) + ab("TC") + style("────◝", 45, bold=True))
    print("  " + style("   ◜──", 45, bold=True) + countries[0].name + style("──◎──", 220, bold=True) + countries[1].name + style("──◎──", 220, bold=True) + countries[2].name + style("──◝", 45, bold=True))
    print("  " + style("   ◟──", 45, bold=True) + countries[3].name + style("──◎──", 220, bold=True) + countries[4].name + style("──◎──", 220, bold=True) + countries[5].name + style("──◞", 45, bold=True))
    print("  " + style("      ◟────", 45, bold=True) + ab("RR") + style("────◞    ◟───────────◞", 45, bold=True))


def pool_art(lang: str) -> None:
    label = tr(lang, "shared protection pool", "gemeinsamer Schutzpool")
    risk_word = tr(lang, "risk", "Risiko")
    premium_word = tr(lang, "premium", "Prämie")
    print("  " + style("     ╭──────────────────────────────╮", 45, bold=True))
    print("  " + style("  ≋≋ │ ", 45, bold=True) + ab("SB") + style("  " + pad(label, 23, "^") + " ", 45, bold=True) + style("│ ≋≋", 45, bold=True))
    print("  " + style("     ╰───────┬────────────┬─────────╯", 45, bold=True))
    print("  " + style("             ▼            ▼", 118, bold=True))
    print("  " + style("          ", 244) + ab("RI") + style(" " + risk_word + "     ", 203, bold=True) + ab("PR") + style(" " + premium_word, 220, bold=True))


def ladder_art(lang: str) -> None:
    level = tr(lang, "level", "Stufe")
    labels = [
        tr(lang, "system steering", "Systemsteuerung"),
        tr(lang, "coordination", "Koordination"),
        tr(lang, "skilled action", "Fachhandlung"),
        tr(lang, "routine action", "Routinehandlung"),
        tr(lang, "unstable margin", "instabiler Rand"),
    ]
    print("  " + style("        ╭──────", 82, bold=True) + ab("UP") + style("──────╮", 82, bold=True))
    print("  " + style(pad(level + " 5", 8) + "│  " + pad(labels[0], 16) + " │", 147, bold=True))
    print("  " + style(pad(level + " 4", 8) + "│  " + pad(labels[1], 16) + " │", 111, bold=True))
    print("  " + style(pad(level + " 3", 8) + "│  " + pad(labels[2], 16) + " │", 75, bold=True))
    print("  " + style(pad(level + " 2", 8) + "│  " + pad(labels[3], 16) + " │", 220, bold=True))
    print("  " + style(pad(level + " 1", 8) + "│  " + pad(labels[4], 16) + " │", 196, bold=True))
    print("  " + style("        ╰──────", 196, bold=True) + ab("DN") + style("──────╯", 196, bold=True))


def timeline_art(lang: str, values: Sequence[Tuple[float, float]]) -> None:
    mp_line = "".join(style("█", 201 if m >= s else 208, bold=True) if m > 0 else style("░", 240) for m, s in values)
    sp_line = "".join(style("█", 51 if s >= m else 75, bold=True) if s > 0 else style("░", 240) for m, s in values)
    print("  " + ab("MP") + " " + mp_line)
    print("  " + ab("SP") + " " + sp_line)


def allocation_bar(lang: str, shares: Sequence[Tuple[str, int]]) -> None:
    total = max(1, sum(v for _, v in shares))
    palette = [82, 118, 51, 214, 201, 147, 220, 75, 208, 45]
    print("  " + style(tr(lang, "Allocation strip", "Zuteilungsstreifen"), 220, bold=True))
    bar = ""
    for i, (_, v) in enumerate(shares):
        n = max(1, int(round(v / total * 78)))
        bar += style("█" * n, palette[i % len(palette)], bold=True)
    print("  " + bar)
    for i, (name, v) in enumerate(shares):
        print("  " + style("■", palette[i % len(palette)], bold=True) + " " + pad(name, 25) + unit_num(lang, v, "pieces", 0, 5))


def matrix_heatmap(lang: str, labels: Sequence[str], matrix: Sequence[Sequence[float]]) -> None:
    print("  " + style(tr(lang, "Heat map: weak → strong / harmful → beneficial", "Heatmap: schwach → stark / schädlich → nützlich"), 220, bold=True))
    print("  " + " " * 17 + " ".join(pad(l[:7], 8, "^") for l in labels))
    for label, row_values in zip(labels, matrix):
        line = pad(label[:16], 17)
        for v in row_values:
            line += heat_cell(v) + "      "
        print("  " + line)


def dashboard_gauge(lang: str, code: str, value: float, high: float = 100.0, signed_value: bool = False) -> None:
    display_value = value + 100 if signed_value else value
    display_high = 200 if signed_value else high
    print("  " + ab(code) + " " + positive_bar(display_value, width=52, hi=display_high, color=ABBR_COLORS.get(code, 82)) + " " + (pts(lang, value, signed_value=True) if code != "EL" and code != "RM" else pct(lang, value)))


def objects_avg(objects: Sequence[MarketObject]) -> Tuple[float, float, float, float, float]:
    if not objects:
        return 0, 0, 0, 0, 0
    gv = statistics.mean(o.gv for o in objects)
    pv = statistics.mean(o.pv for o in objects)
    hv = statistics.mean(o.hv for o in objects)
    risk = statistics.mean(o.risk for o in objects)
    mw = statistics.mean(o.mw() for o in objects)
    return gv, pv, hv, risk, mw


def simulated_scenario_score(objects: Sequence[MarketObject], gv_shift: float, pv_shift: float, risk_shift: float, hv_shift: float = 0.0) -> float:
    values = []
    for o in objects:
        values.append(moral_weight(clamp(o.gv + gv_shift, -100, 100), clamp(o.pv + pv_shift, -100, 100), clamp(o.hv + hv_shift, 0, 100), clamp(o.risk + risk_shift, 0, 100)))
    return statistics.mean(values) if values else 0.0


# ---------------------------------------------------------------------------
# Simulation sections
# ---------------------------------------------------------------------------


def section_01_coordinate(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 01 — Radial value map and movable hierarchy",
        "Teil 01 — Radiale Wertkarte und bewegliche Hierarchie",
        "Each market object receives a point in a circular field: goodness on one axis, popularity on the other, hierarchy as a height-like layer above it.",
        "Jeder Marktgegenstand erhält einen Punkt im Kreisfeld: Güte auf einer Achse, Popularität auf der anderen, Hierarchie als höhenartige Schicht darüber.",
        "The model must separate what is liked from what is good; otherwise a harmful but attractive object looks the same as a useful object.",
        "Das Modell muss trennen, was gemocht wird, von dem, was gut ist; sonst sieht ein schädliches, aber attraktives Objekt genauso aus wie ein nützliches Objekt.",
        [
            ("GV", "Goodness value: positive values mean social benefit, fewer harms, fairer side effects; negative values mean damage or exploitation.", "Gütewert: positive Werte bedeuten gesellschaftlichen Nutzen, weniger Schäden und fairere Nebenwirkungen; negative Werte bedeuten Schaden oder Ausbeutung."),
            ("PV", "Popularity value: public demand, attraction, fashion, habit or approval; it is deliberately not identical to goodness.", "Popularitätswert: Nachfrage, Anziehung, Mode, Gewöhnung oder Zustimmung; er ist absichtlich nicht identisch mit Güte."),
            ("HV", "Hierarchy value: structural rank; high values mean many lower actions, roles or consequences depend on the object.", "Hierarchiewert: struktureller Rang; hohe Werte bedeuten, dass viele niedrigere Handlungen, Rollen oder Folgen vom Objekt abhängen."),
            ("AD", "Axis direction: the angle created by goodness and popularity; it reveals the quadrant of the object.", "Achsendrehung: der Winkel aus Güte und Popularität; er zeigt den Quadranten des Objekts."),
            ("RW", "Radial width: distance from the neutral center; high values mean a very clear or polarizing position.", "Radialweite: Entfernung vom neutralen Mittelpunkt; hohe Werte bedeuten eine sehr klare oder polarisierende Lage."),
            ("MW", "Moral weight: compressed comparison signal from goodness, popularity, hierarchy and risk.", "Moralwert: verdichtetes Vergleichssignal aus Güte, Popularität, Hierarchie und Risiko."),
        ],
        [
            ("points", "points on a normalized scale", "Punkte auf einer normalisierten Skala"),
            ("degrees", "angle degrees of the circular direction", "Winkelgrade der Kreisrichtung"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    compass_art(lang)
    objects = sorted(world.all_objects(), key=lambda o: o.mw(), reverse=True)
    print()
    scatter_map(lang, objects, max_items=12 if world.compact else 18)
    print()
    headers = [tr(lang, "object", "Objekt"), tr(lang, "kind", "Art"), ab("GV"), ab("PV"), ab("HV"), ab("AD"), ab("RW"), ab("MW"), tr(lang, "quadrant", "Quadrant")]
    widths = [24, 12, 13, 13, 13, 13, 13, 13, 22]
    rows = []
    for obj in objects[:12 if world.compact else 18]:
        if obj.gv >= 0 and obj.pv >= 0:
            quad = style(tr(lang, "good + popular", "gut + beliebt"), 82, bold=True)
        elif obj.gv >= 0 and obj.pv < 0:
            quad = style(tr(lang, "good + unpopular", "gut + unbeliebt"), 51, bold=True)
        elif obj.gv < 0 and obj.pv >= 0:
            quad = style(tr(lang, "harmful + popular", "schädlich + beliebt"), 196, bold=True)
        else:
            quad = style(tr(lang, "harmful + unpopular", "schädlich + unbeliebt"), 130, bold=True)
        rows.append([style(obj.name(lang), 15, bold=True), style(obj.kind(lang), 147), pts(lang, obj.gv), pts(lang, obj.pv), pts(lang, obj.hv), deg(lang, obj.ad()), pts(lang, obj.rw()), mcu(lang, obj.mw()), quad])
    table(headers, rows, widths)
    print()
    tower_obj = max(world.products, key=lambda p: p.hv)
    hierarchy_tower(lang, tower_obj.name(lang), tower_obj.tiers)
    all_objs = world.all_objects()
    base = statistics.mean(o.mw() for o in all_objs)
    scenario_eval(lang, [
        (tr(lang, "cooperative institutions", "kooperative Institutionen"), mcu(lang, simulated_scenario_score(all_objs, 12, 4, -6)), tr(lang, "good but neglected objects become visible earlier", "gute, aber vernachlässigte Objekte werden früher sichtbar")),
        (tr(lang, "pure popularity start", "reiner Popularitätsstart"), mcu(lang, simulated_scenario_score(all_objs, -5, 16, 8)), tr(lang, "attractive harmful objects gain speed before safeguards react", "attraktive schädliche Objekte gewinnen Tempo, bevor Sicherungen reagieren")),
        (tr(lang, "risk-aware start", "risikobewusster Start"), mcu(lang, simulated_scenario_score(all_objs, 4, -2, -14)), tr(lang, "the average signal improves because hidden costs are priced earlier", "das Durchschnittssignal verbessert sich, weil verdeckte Kosten früher eingepreist werden")),
        (tr(lang, "current seed state", "aktueller Seed-Zustand"), mcu(lang, base), tr(lang, "mixed field: civic and toxic quadrants both exist", "gemischtes Feld: bürgerliche und toxische Quadranten existieren zugleich")),
    ])


def section_02_governance(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 02 — Institution, population and knowledge signals",
        "Teil 02 — Institutionen-, Bevölkerungs- und Wissenssignale",
        "Selected products are repeatedly re-scored. Institutions push goodness, population shifts popularity, and knowledge corrects both when measured consequences appear.",
        "Ausgewählte Produkte werden wiederholt neu bewertet. Institutionen verschieben Güte, Bevölkerung verschiebt Popularität, Wissen korrigiert beide Seiten, sobald messbare Folgen sichtbar werden.",
        "A moral market layer is fragile if one actor can define truth alone. This step tests whether separated signals produce a more stable value vector.",
        "Eine moralische Marktschicht ist fragil, wenn ein Akteur allein Wahrheit definieren kann. Dieser Schritt testet, ob getrennte Signale einen stabileren Wertvektor erzeugen.",
        [
            ("IS", "Institutional signal: law, audit and public authority acting on harm, benefit and fairness.", "Institutionensignal: Recht, Prüfung und öffentliche Autorität wirken auf Schaden, Nutzen und Fairness."),
            ("PS", "Population signal: collective desire, dislike, fashion, habit and public attention.", "Popularitätssignal: kollektiver Wunsch, Abneigung, Mode, Gewöhnung und öffentliche Aufmerksamkeit."),
            ("KS", "Knowledge signal: measured consequences, research and evidence correcting both sides.", "Kenntnissignal: gemessene Folgen, Forschung und Evidenz korrigieren beide Seiten."),
            ("GV", "Goodness value after signal pressure.", "Gütewert nach Signaldruck."),
            ("PV", "Popularity value after signal pressure.", "Popularitätswert nach Signaldruck."),
            ("DG", "Delta goodness: the change of goodness in the current step.", "Differenz Güte: die Veränderung der Güte im aktuellen Schritt."),
            ("DP", "Delta popularity: the change of popularity in the current step.", "Differenz Popularität: die Veränderung der Popularität im aktuellen Schritt."),
        ],
        [
            ("points", "points on the value scale", "Punkte auf der Wertskala"),
            ("percent", "signal strength in percent", "Signalstärke in Prozent"),
            ("day", "simulated decision day", "simulierter Entscheidungstag"),
        ],
    )
    signal_flow_art(lang)
    watched_keys = {"addiction_box", "open_course", "data_trade", "repair_lamp", "basic_research", "short_video"}
    watched = [p for p in world.products if p.key in watched_keys]
    avg_path: List[float] = []
    for day in range(1, world.ticks + 1):
        print()
        print(style(tr(lang, "Decision day", "Entscheidungstag"), 39, bold=True) + " " + unit_num(lang, day, "day", 0, 3))
        rows = []
        for p in watched:
            inst = clamp(0.10 * p.gv - 0.10 * max(0, -p.gv) - 0.05 * p.risk + world.rng.uniform(-4, 4), -18, 18)
            pop = clamp(0.08 * p.pv + (0.04 * p.gv if p.gv > 50 else 0) + world.rng.uniform(-8, 8), -22, 22)
            know = clamp((p.gv - p.risk) * 0.08 + world.rng.uniform(-3, 3), -16, 16)
            dg = 0.25 * inst + 0.35 * know
            dp = 0.38 * pop + 0.04 * know
            p.gv = clamp(p.gv + dg, -100, 100)
            p.pv = clamp(p.pv + dp, -100, 100)
            rows.append([style(p.name(lang), 15, bold=True), pct(lang, inst, signed_value=True), pct(lang, pop, signed_value=True), pct(lang, know, signed_value=True), pts(lang, dg, signed_value=True), pts(lang, dp, signed_value=True), pts(lang, p.gv), pts(lang, p.pv)])
        avg_path.append(statistics.mean(p.mw() for p in watched))
        table([tr(lang, "object", "Objekt"), ab("IS"), ab("PS"), ab("KS"), ab("DG"), ab("DP"), ab("GV"), ab("PV")], rows, [24, 12, 12, 12, 13, 13, 13, 13])
    print()
    print("  " + style(tr(lang, "Average path", "Durchschnittspfad"), 220, bold=True) + " " + sparkline(avg_path, 82, width=40) + " " + mcu(lang, avg_path[-1]))
    scenario_eval(lang, [
        (tr(lang, "institution-only start", "nur Institutionen"), pts(lang, simulated_scenario_score(watched, 8, -3, -3)), tr(lang, "more orderly, but unpopular good work may remain under-loved", "ordentlicher, aber unpopuläre gute Arbeit bleibt möglicherweise ungeliebt")),
        (tr(lang, "population-only start", "nur Bevölkerung"), pts(lang, simulated_scenario_score(watched, -6, 18, 10)), tr(lang, "fast attention, weak truth filter, high danger of hype", "schnelle Aufmerksamkeit, schwacher Wahrheitsfilter, hohe Hype-Gefahr")),
        (tr(lang, "knowledge-heavy start", "wissensstarker Start"), pts(lang, simulated_scenario_score(watched, 14, -2, -12)), tr(lang, "slower but more robust because observed damage matters", "langsamer, aber robuster, weil beobachteter Schaden zählt")),
        (tr(lang, "balanced start", "balancierter Start"), pts(lang, avg_path[-1]), tr(lang, "the run keeps harmful popularity visible instead of hiding it", "der Lauf hält schädliche Popularität sichtbar, statt sie zu verdecken")),
    ])


def section_03_product_market(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 03 — Product market with moral price environment",
        "Teil 03 — Produktmarkt mit moralischer Preisumgebung",
        "Products are sold through demand, supply, tax or relief and moral weight. The price is still numeric, but it is embedded in a colored value context.",
        "Produkte werden durch Nachfrage, Angebot, Steuer oder Entlastung und Moralwert verkauft. Der Preis bleibt numerisch, liegt aber in einem farbigen Wertkontext.",
        "A market price can hide exploitation, addiction or external costs. The simulation makes the hidden context visible before transactions are counted.",
        "Ein Marktpreis kann Ausbeutung, Sucht oder externe Kosten verstecken. Die Simulation macht diesen Kontext sichtbar, bevor Transaktionen gezählt werden.",
        [
            ("RP", "Reference price: end price after popularity, goodness, hierarchy and tax-or-relief pressure.", "Referenzpreis: Endpreis nach Popularität, Güte, Hierarchie und Steuer- oder Entlastungsdruck."),
            ("DI", "Demand index: current pull of customers toward the product.", "Nachfrageindex: aktueller Zug der Kundschaft zum Produkt."),
            ("SU", "Supply units: available product pieces in this step.", "Angebotseinheiten: verfügbare Produktstücke in diesem Schritt."),
            ("TR", "Tax-or-relief rate: positive means surcharge, negative means support.", "Steuer-Entlastungsrate: positiv bedeutet Aufschlag, negativ bedeutet Förderung."),
            ("TX", "Transactions: simulated completed product exchanges.", "Transaktionen: simulierte abgeschlossene Produktwechsel."),
            ("GV", "Goodness value used by the filter.", "Gütewert, der vom Filter verwendet wird."),
            ("PV", "Popularity value used by demand.", "Popularitätswert, der die Nachfrage beeinflusst."),
            ("MW", "Moral weight used as context, not as a bare price.", "Moralwert als Kontext, nicht als bloßer Preis."),
        ],
        [
            ("eur", "conventional price reference", "konventionelle Preisreferenz"),
            ("percent", "rate, index or share", "Rate, Index oder Anteil"),
            ("pieces", "counted product pieces", "gezählte Produktstücke"),
            ("tx", "counted transactions", "gezählte Transaktionen"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    funnel_art(lang)
    rows = []
    total_tx = 0
    demand_values = []
    for p in sorted(world.products, key=lambda x: x.pv, reverse=True):
        tr_rate = tax_relief_rate(p.gv, p.pv)
        demand_index = clamp(45 + p.pv * 0.43 + p.gv * 0.08 - max(0, -p.gv) * 0.11 - tr_rate * 0.6 + world.rng.uniform(-8, 8), 0, 125)
        supply_units = p.stock
        transactions = int(round(min(supply_units, max(0, supply_units * demand_index / 110.0))))
        p.demand = demand_index
        total_tx += transactions
        demand_values.append(demand_index)
        rp = max(0.0, p.base_eur * (1 + (p.pv / 400.0)) * (1 + tr_rate / 100.0) * (1 + (p.hv - 50.0) / 900.0))
        outcome = style(tr(lang, "supported", "gefördert"), 82, bold=True) if tr_rate < -2 else style(tr(lang, "surcharged", "belastet"), 196, bold=True) if tr_rate > 5 else style(tr(lang, "neutral", "neutral"), 226, bold=True)
        rows.append([style(p.name(lang), 15, bold=True), eur(lang, rp), pct(lang, demand_index), unit_num(lang, supply_units, "pieces", 0, 5), pct(lang, tr_rate, signed_value=True), unit_num(lang, transactions, "tx", 0, 5), pts(lang, p.gv), pts(lang, p.pv), mcu(lang, p.mw()), outcome])
    table([tr(lang, "product", "Produkt"), ab("RP"), ab("DI"), ab("SU"), ab("TR"), ab("TX"), ab("GV"), ab("PV"), ab("MW"), tr(lang, "filter", "Filter")], rows, [24, 13, 12, 11, 12, 11, 12, 12, 12, 12])
    print()
    print("  " + style(tr(lang, "Demand rhythm", "Nachfragerhythmus"), 220, bold=True) + " " + sparkline(demand_values, 201, width=50))
    print("  " + style(tr(lang, "Total completed transactions", "Gesamtzahl abgeschlossener Transaktionen"), 118, bold=True) + " " + unit_num(lang, total_tx, "tx", 0, 7))
    products = world.products
    scenario_eval(lang, [
        (tr(lang, "cheap harmful goods", "billige schädliche Güter"), unit_num(lang, int(sum(p.stock * 0.72 for p in products if p.gv < 0)), "tx", 0, 6), tr(lang, "large volume moves unless the surcharge is strong", "großes Volumen bewegt sich, wenn der Aufschlag nicht stark ist")),
        (tr(lang, "useful unpopular goods", "nützliche unbeliebte Güter"), mcu(lang, simulated_scenario_score(products, 10, -10, -8)), tr(lang, "relief turns neglect into visible protection", "Entlastung verwandelt Vernachlässigung in sichtbaren Schutz")),
        (tr(lang, "fashion shock", "Modeschock"), pct(lang, statistics.mean(demand_values) + 18), tr(lang, "the market reacts quickly, but moral context shows the cost", "der Markt reagiert schnell, aber moralischer Kontext zeigt die Kosten")),
        (tr(lang, "balanced basket", "balancierter Warenkorb"), unit_num(lang, total_tx, "tx", 0, 6), tr(lang, "transactions continue, but not all trades are treated as equally innocent", "Transaktionen laufen weiter, aber nicht alle Tauschakte gelten als gleich unschuldig")),
    ])


def section_04_labor_market(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 04 — Labor market: workers choose employers too",
        "Teil 04 — Arbeitsmarkt: Arbeitskräfte bewerten Arbeitgeber ebenfalls",
        "Workers and employers are matched by productive ability, selfless contribution, fairness and moral weight. The employer does not monopolize judgment.",
        "Arbeitskräfte und Arbeitgeber werden über Produktivität, Selbstlosigkeit, Fairness und Moralwert gematcht. Der Arbeitgeber monopolisiert das Urteil nicht.",
        "Classic labor markets often overrate pay and underrate employer quality. This part tests a more symmetric market relation.",
        "Klassische Arbeitsmärkte überschätzen oft Lohn und unterschätzen Arbeitgeberqualität. Dieser Teil testet eine symmetrischere Marktbeziehung.",
        [
            ("WP", "Worker potential: skill, reliability and productive capacity of the worker.", "Arbeitskräftepotenzial: Können, Verlässlichkeit und produktive Fähigkeit der Arbeitskraft."),
            ("SE", "Selflessness: contribution beyond narrow private gain.", "Selbstlosigkeit: Beitrag über engen Eigennutz hinaus."),
            ("FR", "Fairness rate: employer-side fairness from wages, risk and goodness.", "Fairnessrate: arbeitgeberseitige Fairness aus Lohn, Risiko und Güte."),
            ("MG", "Match grade: quality of the worker-employer fit.", "Matchinggrad: Qualität der Passung zwischen Arbeitskraft und Arbeitgeber."),
            ("WA", "Wage adjustment: change in pay caused by match and fairness.", "Lohnanpassung: Lohnänderung durch Passung und Fairness."),
            ("MW", "Moral weight of worker and employer context.", "Moralwert des Arbeitskraft- und Arbeitgeberkontexts."),
        ],
        [
            ("points", "points for skill, fairness and fit", "Punkte für Fähigkeit, Fairness und Passung"),
            ("percent", "rate or probability share", "Rate oder Wahrscheinlichkeitsanteil"),
            ("eur", "monthly wage reference", "monatliche Lohnreferenz"),
            ("people", "number of people", "Anzahl von Personen"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    labor_bipartite_art(lang)
    rows = []
    matches: List[Tuple[Worker, Company, float, float, float]] = []
    for w in world.workers:
        best = None
        best_score = -9999.0
        for c in world.companies:
            fairness = clamp(55 + c.gv * 0.24 - c.risk * 0.18 + c.profit * 0.05, 0, 100)
            score = 0.36 * w.wp + 0.18 * w.se + 0.22 * c.gv + 0.14 * c.hv + 0.10 * fairness - abs(w.pv - c.pv) * 0.06 + world.rng.uniform(-4, 4)
            if score > best_score:
                best_score = score
                best = (c, fairness)
        assert best is not None
        c, fairness = best
        mg = clamp(best_score, 0, 100)
        wa = clamp((mg - 55) * 5.2 + (fairness - 50) * 3.0, -650, 900)
        w.wage = max(900, w.wage + wa)
        w.matched_key = c.key
        matches.append((w, c, fairness, mg, wa))
    shown = sorted(matches, key=lambda x: x[3], reverse=True)[:12 if world.compact else 20]
    for w, c, fairness, mg, wa in shown:
        rows.append([style(w.name, 15, bold=True), style(c.name(lang), 147, bold=True), pts(lang, w.wp), pts(lang, w.se, signed_value=True), pct(lang, fairness), pts(lang, mg), eur(lang, wa, 0, signed_value=True), mcu(lang, (w.mw() + c.mw()) / 2.0)])
    table([tr(lang, "worker", "Arbeitskraft"), tr(lang, "employer", "Arbeitgeber"), ab("WP"), ab("SE"), ab("FR"), ab("MG"), ab("WA"), ab("MW")], rows, [14, 18, 12, 12, 12, 12, 13, 12])
    avg_fair = statistics.mean(x[2] for x in matches)
    avg_match = statistics.mean(x[3] for x in matches)
    print()
    print("  " + style(tr(lang, "Match quality", "Matchingqualität"), 220, bold=True) + " " + positive_bar(avg_match, width=46) + " " + pts(lang, avg_match))
    print("  " + style(tr(lang, "Fairness level", "Fairnessniveau"), 118, bold=True) + " " + positive_bar(avg_fair, width=46, color=118) + " " + pct(lang, avg_fair))
    scenario_eval(lang, [
        (tr(lang, "high fairness employers", "faire Arbeitgeber stark"), pct(lang, min(100, avg_fair + 15)), tr(lang, "better matches and less wage pressure by threat", "bessere Passungen und weniger Lohndruck durch Drohung")),
        (tr(lang, "prestige-only hiring", "reines Prestige-Hiring"), pts(lang, avg_match - 11, signed_value=True), tr(lang, "popular employers attract workers even when moral weight is weaker", "populäre Arbeitgeber ziehen Menschen an, auch wenn der Moralwert schwächer ist")),
        (tr(lang, "selfless work shortage", "Mangel an selbstloser Arbeit"), unit_num(lang, sum(1 for w in world.workers if w.se < 20), "people", 0, 5), tr(lang, "necessary care-like roles become underfilled", "notwendige pflegeähnliche Rollen werden unterbesetzt")),
        (tr(lang, "symmetric choice", "symmetrische Wahl"), pts(lang, avg_match), tr(lang, "workers and employers both become legible market objects", "Arbeitskräfte und Arbeitgeber werden beide lesbare Marktobjekte")),
    ])


def section_05_stock_market(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 05 — Stock market: return is tinted by moral context",
        "Teil 05 — Aktienmarkt: Rendite wird moralisch eingefärbt",
        "Company shares move by earnings, popularity, risk and moral weight. A high profit can still carry a warning color.",
        "Unternehmensanteile bewegen sich durch Ertrag, Popularität, Risiko und Moralwert. Hoher Profit kann trotzdem eine Warnfarbe tragen.",
        "Capital allocation is powerful. This step tests whether investors can see when return comes from helpful production or from damaging extraction.",
        "Kapitalallokation ist mächtig. Dieser Schritt testet, ob Anleger sehen, ob Rendite aus hilfreicher Produktion oder aus schädlicher Abschöpfung stammt.",
        [
            ("SV", "Share value: simulated share reference after value-vector pressure.", "Aktienwert: simulierte Aktienreferenz nach Wertvektordruck."),
            ("ER", "Earnings rate: current profit pressure translated into market movement.", "Ertragsrate: aktueller Gewinndruck als Marktbewegung."),
            ("ES", "Ethical spread: moral premium or discount around the share.", "Ethikspread: moralischer Auf- oder Abschlag rund um die Aktie."),
            ("RS", "Risk shadow: risk and hidden-cost burden on the share.", "Risikoschatten: Risiko- und Folgekostenlast auf der Aktie."),
            ("MW", "Moral weight of the company behind the share.", "Moralwert des Unternehmens hinter der Aktie."),
        ],
        [
            ("eur", "share price reference", "Aktienpreisreferenz"),
            ("percent", "rate, spread or burden", "Rate, Spread oder Belastung"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    chart_rows = []
    rows = []
    for c in world.companies:
        values = [c.share]
        for _ in range(world.ticks + 3):
            er = clamp(c.profit * 0.42 + c.pv * 0.08 + world.rng.uniform(-5, 5), -35, 45)
            es = clamp(c.mw() * 0.11, -18, 18)
            rs = clamp(c.risk * 0.20 + max(0, -c.gv) * 0.18, 0, 40)
            move = er + es - rs * 0.35
            values.append(max(1.0, values[-1] * (1 + move / 380.0)))
        c.share = values[-1]
        chart_rows.append((c.name(lang), values))
        er = clamp(c.profit * 0.42 + c.pv * 0.08, -35, 45)
        es = clamp(c.mw() * 0.11, -18, 18)
        rs = clamp(c.risk * 0.20 + max(0, -c.gv) * 0.18, 0, 40)
        stance = style(tr(lang, "trusted", "vertrauensnah"), 82, bold=True) if es > 5 and rs < 20 else style(tr(lang, "extractive", "abschöpfend"), 196, bold=True) if es < -4 or rs > 25 else style(tr(lang, "contested", "umstritten"), 226, bold=True)
        rows.append([style(c.name(lang), 15, bold=True), eur(lang, c.share), pct(lang, er, signed_value=True), pct(lang, es, signed_value=True), pct(lang, rs), mcu(lang, c.mw()), stance])
    candles_art(lang, chart_rows)
    print()
    table([tr(lang, "company", "Unternehmen"), ab("SV"), ab("ER"), ab("ES"), ab("RS"), ab("MW"), tr(lang, "market reading", "Marktlesart")], rows, [18, 13, 12, 12, 12, 12, 18])
    avg_sv = statistics.mean(c.share for c in world.companies)
    avg_rs = statistics.mean(clamp(c.risk * 0.20 + max(0, -c.gv) * 0.18, 0, 40) for c in world.companies)
    scenario_eval(lang, [
        (tr(lang, "profit without context", "Profit ohne Kontext"), eur(lang, avg_sv * 1.08), tr(lang, "capital follows earnings and misses hidden damage", "Kapital folgt Ertrag und übersieht verdeckten Schaden")),
        (tr(lang, "ethics-weighted capital", "ethisch gewichtetes Kapital"), pct(lang, max(0, 100 - avg_rs)), tr(lang, "harmful firms face a visible discount", "schädliche Firmen erhalten einen sichtbaren Abschlag")),
        (tr(lang, "panic about risk", "Risikopanik"), pct(lang, avg_rs + 18), tr(lang, "risk shadows dominate and may punish even useful firms", "Risikoschatten dominieren und können auch nützliche Firmen bestrafen")),
        (tr(lang, "current market mix", "aktueller Marktmix"), eur(lang, avg_sv), tr(lang, "return remains possible, but moral provenance is no longer hidden", "Rendite bleibt möglich, aber moralische Herkunft ist nicht mehr versteckt")),
    ])


def section_06_currency_market(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 06 — Currency market between countries",
        "Teil 06 — Währungsmarkt zwischen Ländern",
        "Countries receive exchange-like references from trust, risk, hierarchy and moral weight. The output shows a currency field rather than a single neutral number.",
        "Länder erhalten wechselkursähnliche Referenzen aus Vertrauen, Risiko, Hierarchie und Moralwert. Die Ausgabe zeigt ein Währungsfeld statt einer einzigen neutralen Zahl.",
        "If currency reflects only liquidity, large harmful systems may look strong. This part tests a value-aware exchange layer.",
        "Wenn Währung nur Liquidität spiegelt, können große schädliche Systeme stark aussehen. Dieser Teil testet eine wertbewusste Wechselkursschicht.",
        [
            ("XR", "Exchange rate: simulated rate against the shared moral currency reference.", "Wechselkurs: simulierter Kurs gegenüber der gemeinsamen Moralwährungsreferenz."),
            ("TC", "Trust correction: credibility gain or loss from goodness and stability.", "Vertrauenskorridor: Glaubwürdigkeitsgewinn oder -verlust aus Güte und Stabilität."),
            ("RR", "Risk reserve: extra buffer demanded for risk and harmful popularity.", "Risikoreserve: zusätzlicher Puffer für Risiko und schädliche Popularität."),
            ("GV", "Goodness value of the country-level system.", "Gütewert des länderbezogenen Systems."),
            ("PV", "Popularity value of the country-level system.", "Popularitätswert des länderbezogenen Systems."),
            ("HV", "Hierarchy value of the country-level system.", "Hierarchiewert des länderbezogenen Systems."),
            ("MW", "Moral weight behind the exchange reference.", "Moralwert hinter der Wechselkursreferenz."),
        ],
        [
            ("rate", "exchange-rate reference", "Wechselkursreferenz"),
            ("percent", "correction, reserve or pressure", "Korrektur, Reserve oder Druck"),
            ("points", "points for value dimensions", "Punkte für Wertdimensionen"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    currency_wheel_art(lang, world.countries)
    rows = []
    xr_values = []
    for c in world.countries:
        tc = clamp(c.gv * 0.10 + c.hv * 0.06 - c.risk * 0.08 + world.rng.uniform(-3, 3), -18, 22)
        rr = clamp(c.risk * 0.35 + max(0, -c.gv) * 0.25 + max(0, c.pv - 65) * 0.08, 0, 55)
        xr = max(0.2, c.course * (1 + tc / 120.0) * (1 - rr / 260.0))
        c.course = xr
        xr_values.append(xr)
        stance = style(tr(lang, "trusted", "vertrauensstark"), 82, bold=True) if tc > 5 and rr < 22 else style(tr(lang, "buffered", "gepuffert"), 226, bold=True) if rr < 35 else style(tr(lang, "strained", "angespannt"), 196, bold=True)
        rows.append([style(c.name, 15, bold=True), unit_num(lang, xr, "rate", 3, 8), pct(lang, tc, signed_value=True), pct(lang, rr), pts(lang, c.gv), pts(lang, c.pv), pts(lang, c.hv), mcu(lang, c.mw()), stance])
    table([tr(lang, "country", "Land"), ab("XR"), ab("TC"), ab("RR"), ab("GV"), ab("PV"), ab("HV"), ab("MW"), tr(lang, "reading", "Lesart")], rows, [12, 13, 12, 12, 12, 12, 12, 12, 14])
    print()
    print("  " + style(tr(lang, "Exchange field", "Wechselkursfeld"), 220, bold=True) + " " + sparkline([x * 100 for x in xr_values], 45, width=36))
    scenario_eval(lang, [
        (tr(lang, "liquidity-only start", "nur Liquidität"), unit_num(lang, statistics.mean(xr_values) * 1.06, "rate", 3, 8), tr(lang, "strong-looking systems may hide risk", "stark wirkende Systeme können Risiko verstecken")),
        (tr(lang, "trust-weighted start", "vertrauensgewichteter Start"), pct(lang, statistics.mean(clamp(c.gv * 0.10 + c.hv * 0.06 - c.risk * 0.08, -18, 22) for c in world.countries), signed_value=True), tr(lang, "credibility improves the exchange reference", "Glaubwürdigkeit verbessert die Wechselkursreferenz")),
        (tr(lang, "risk-reserve shock", "Risikoreserveschock"), pct(lang, statistics.mean(c.risk for c in world.countries) + 12), tr(lang, "buffers rise and low-trust currencies weaken", "Puffer steigen und schwache Vertrauenswährungen sinken")),
        (tr(lang, "balanced field", "balanciertes Feld"), unit_num(lang, statistics.mean(xr_values), "rate", 3, 8), tr(lang, "currency becomes a trust-and-risk map", "Währung wird zur Vertrauens- und Risikokarte")),
    ])


def section_07_insurance(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 07 — Insurance market and solidarity buffer",
        "Teil 07 — Versicherungsmarkt und Solidaritätspuffer",
        "Risks are priced, but premiums are modified by need, public usefulness and solidarity. Not every risk is treated as privately deserved.",
        "Risiken werden bepreist, aber Prämien werden durch Bedarf, öffentlichen Nutzen und Solidarität verändert. Nicht jedes Risiko gilt als privat verdient.",
        "A value-aware market must distinguish between self-caused harmful risk and socially necessary exposure.",
        "Ein wertbewusster Markt muss selbstverursachtes schädliches Risiko von gesellschaftlich notwendiger Belastung unterscheiden.",
        [
            ("RI", "Risk index: expected burden from accidents, uncertainty and external damage.", "Risikoindex: erwartete Belastung durch Unfälle, Unsicherheit und externe Schäden."),
            ("SB", "Solidarity buffer: relief when need and useful purpose justify shared protection.", "Solidaritätspuffer: Entlastung, wenn Bedarf und nützlicher Zweck gemeinsamen Schutz rechtfertigen."),
            ("PR", "Premium reference: simulated insurance premium after risk and solidarity.", "Prämienreferenz: simulierte Versicherungsprämie nach Risiko und Solidarität."),
            ("ND", "Need: urgency of protection for the insured case.", "Bedarf: Dringlichkeit des Schutzes für den Versicherungsfall."),
            ("MW", "Moral weight of the insured case.", "Moralwert des versicherten Falls."),
        ],
        [
            ("eur", "premium reference", "Prämienreferenz"),
            ("percent", "risk or relief share", "Risiko- oder Entlastungsanteil"),
            ("points", "need and value points", "Bedarfs- und Wertpunkte"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    pool_art(lang)
    rows = []
    premiums = []
    for case in world.insurance_cases:
        ri = clamp(case.risk + max(0, -case.gv) * 0.25 + (100 - case.hv) * 0.04, 0, 100)
        sb = clamp((case.gv * 0.16 + case.hv * 0.08 + case.nd * 0.10) - ri * 0.20, -30, 30)
        premium = max(15, case.premium_base * (0.55 + ri / 100.0) * (1 - sb / 100.0))
        premiums.append(premium)
        outcome = style(tr(lang, "relieved", "entlastet"), 82, bold=True) if sb > 8 else style(tr(lang, "burdened", "belastet"), 196, bold=True) if sb < -8 else style(tr(lang, "smoothed", "geglättet"), 226, bold=True)
        rows.append([style(case.name(lang), 15, bold=True), pct(lang, ri), pct(lang, sb, signed_value=True), eur(lang, premium, 0), pts(lang, case.nd), mcu(lang, case.mw()), outcome])
    table([tr(lang, "case", "Fall"), ab("RI"), ab("SB"), ab("PR"), ab("ND"), ab("MW"), tr(lang, "effect", "Wirkung")], rows, [20, 12, 12, 13, 12, 12, 13])
    print()
    print("  " + style(tr(lang, "Premium spread", "Prämienspanne"), 220, bold=True) + " " + sparkline(premiums, 220, width=38))
    scenario_eval(lang, [
        (tr(lang, "private blame start", "Privatschuld-Start"), eur(lang, statistics.mean(premiums) * 1.14, 0), tr(lang, "premiums rise even for socially needed exposure", "Prämien steigen auch bei gesellschaftlich notwendiger Belastung")),
        (tr(lang, "solidarity-heavy start", "solidaritätsstarker Start"), pct(lang, 22), tr(lang, "shared protection lowers exclusion risk", "gemeinsamer Schutz senkt Ausschlussrisiko")),
        (tr(lang, "risk-hidden start", "risikoverdeckter Start"), pct(lang, statistics.mean(c.risk for c in world.insurance_cases) - 10), tr(lang, "cheap premiums become unstable because damage is underpriced", "billige Prämien werden instabil, weil Schäden unterbewertet sind")),
        (tr(lang, "balanced pool", "balancierter Pool"), eur(lang, statistics.mean(premiums), 0), tr(lang, "risk is priced, but social purpose remains visible", "Risiko wird bepreist, aber sozialer Zweck bleibt sichtbar")),
    ])


def section_08_mobility(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 08 — Career, ascent and descent across markets",
        "Teil 08 — Karriere, Aufstieg und Abstieg über Märkte hinweg",
        "Workers, companies and products can rise or fall in hierarchy. Popularity alone is not enough if the moral signal is weak.",
        "Arbeitskräfte, Unternehmen und Produkte können in der Hierarchie steigen oder fallen. Popularität allein reicht nicht, wenn das moralische Signal schwach ist.",
        "The original idea treats hierarchy as movable. This part tests promotion, demotion and unstable status.",
        "Die Ausgangsidee behandelt Hierarchie als beweglich. Dieser Teil testet Aufstieg, Abstieg und instabilen Status.",
        [
            ("UP", "Upward chance: probability of reaching a higher responsibility layer.", "Aufstiegschance: Wahrscheinlichkeit, eine höhere Verantwortungsschicht zu erreichen."),
            ("DN", "Downward pressure: probability of falling because of risk, harm or weak contribution.", "Abstiegsdruck: Wahrscheinlichkeit zu fallen, weil Risiko, Schaden oder schwacher Beitrag wirken."),
            ("MT", "Movement trend: current productive direction of the object.", "Bewegungstrend: aktuelle produktive Richtung des Objekts."),
            ("GV", "Goodness value influencing stable ascent.", "Gütewert, der stabilen Aufstieg beeinflusst."),
            ("PV", "Popularity value influencing fast ascent.", "Popularitätswert, der schnellen Aufstieg beeinflusst."),
            ("HV", "Hierarchy value before movement.", "Hierarchiewert vor der Bewegung."),
            ("MW", "Moral weight as a final interpretation layer.", "Moralwert als abschließende Deutungsschicht."),
        ],
        [
            ("percent", "chance or pressure", "Chance oder Druck"),
            ("points", "trend and hierarchy points", "Trend- und Hierarchiepunkte"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    ladder_art(lang)
    candidates: List[Tuple[str, str, float, float, float, float, float, float]] = []
    for w in world.workers:
        mt = clamp(w.wp * 0.55 + w.se * 0.25 + world.rng.uniform(-14, 14), -100, 100)
        up = clamp(18 + mt * 0.30 + w.gv * 0.18 + w.pv * 0.08 - w.hv * 0.05, 0, 95)
        dn = clamp(12 - mt * 0.12 + max(0, -w.gv) * 0.22 + max(0, w.pv - 70) * 0.08, 0, 90)
        candidates.append((w.name, tr(lang, "worker", "Arbeitskraft"), up, dn, mt, w.gv, w.hv, w.mw()))
    for c in world.companies:
        mt = clamp(c.profit * 1.2 + c.pv * 0.15 - c.risk * 0.15 + world.rng.uniform(-10, 10), -100, 100)
        up = clamp(16 + mt * 0.25 + c.gv * 0.16 + c.pv * 0.06, 0, 95)
        dn = clamp(10 - mt * 0.10 + max(0, -c.gv) * 0.28 + c.risk * 0.15, 0, 90)
        candidates.append((c.name(lang), tr(lang, "company", "Unternehmen"), up, dn, mt, c.gv, c.hv, c.mw()))
    for p in world.products:
        mt = clamp(p.demand * 0.12 + p.pv * 0.25 + p.gv * 0.15 - p.risk * 0.18 + world.rng.uniform(-12, 12), -100, 100)
        up = clamp(14 + mt * 0.22 + p.gv * 0.19 + p.pv * 0.05, 0, 95)
        dn = clamp(14 - mt * 0.08 + max(0, -p.gv) * 0.25 + p.risk * 0.12, 0, 95)
        candidates.append((p.name(lang), tr(lang, "product", "Produkt"), up, dn, mt, p.gv, p.hv, p.mw()))
    candidates.sort(key=lambda x: x[2] - x[3], reverse=True)
    rows = []
    for name, kind, up, dn, mt, gv, hv, mw in candidates[:16 if world.compact else 28]:
        movement = style(tr(lang, "ascent", "Aufstieg"), 82, bold=True) if up - dn > 25 else style(tr(lang, "descent", "Abstieg"), 196, bold=True) if dn - up > 12 else style(tr(lang, "hold", "halten"), 226, bold=True)
        rows.append([style(name, 15, bold=True), style(kind, 147), pct(lang, up), pct(lang, dn), pts(lang, mt, signed_value=True), pts(lang, gv), pts(lang, hv), mcu(lang, mw), movement])
    table([tr(lang, "object", "Objekt"), tr(lang, "kind", "Art"), ab("UP"), ab("DN"), ab("MT"), ab("GV"), ab("HV"), ab("MW"), tr(lang, "movement", "Bewegung")], rows, [24, 14, 12, 12, 12, 12, 12, 12, 11])
    avg_up = statistics.mean(x[2] for x in candidates)
    avg_dn = statistics.mean(x[3] for x in candidates)
    scenario_eval(lang, [
        (tr(lang, "virtue and skill start", "Tugend-und-Können-Start"), pct(lang, avg_up + 10), tr(lang, "ascent is earned by useful capacity", "Aufstieg wird durch nützliche Fähigkeit verdient")),
        (tr(lang, "celebrity start", "Prominenzstart"), pct(lang, avg_up + 5), tr(lang, "fast ascent becomes unstable if goodness lags", "schneller Aufstieg wird instabil, wenn Güte zurückbleibt")),
        (tr(lang, "risk collapse", "Risikokollaps"), pct(lang, avg_dn + 15), tr(lang, "high shadow costs push demotion", "hohe Schattenkosten treiben Abstieg")),
        (tr(lang, "current mobility", "aktuelle Mobilität"), pct(lang, avg_up - avg_dn, signed_value=True), tr(lang, "hierarchy is moving instead of fixed", "Hierarchie bewegt sich, statt festzustehen")),
    ])


def section_09_manipulation(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 09 — Manipulation stress test",
        "Teil 09 — Manipulations-Stresstest",
        "A harmful but attractive product receives artificial popularity. Shielding mechanisms then try to slow the drift into the harmful-popular quadrant.",
        "Ein schädliches, aber attraktives Produkt erhält künstliche Popularität. Schutzmechanismen versuchen danach, das Wandern in den schädlich-beliebten Quadranten zu bremsen.",
        "The model is dangerous if popularity can be manufactured cheaply. This part shows the race between manipulation and protection.",
        "Das Modell ist gefährlich, wenn Popularität billig hergestellt werden kann. Dieser Teil zeigt das Rennen zwischen Manipulation und Schutz.",
        [
            ("MP", "Manipulation pressure: artificial popularity from ads, data tricks, bots or habit loops.", "Manipulationsdruck: künstliche Popularität aus Werbung, Datentricks, Bots oder Gewöhnungsschleifen."),
            ("SP", "Shield power: ability of transparency, audit and public learning to slow manipulation.", "Schutzpower: Fähigkeit von Transparenz, Prüfung und öffentlichem Lernen, Manipulation zu bremsen."),
            ("GV", "Goodness value during the stress test.", "Gütewert während des Stresstests."),
            ("PV", "Popularity value during the stress test.", "Popularitätswert während des Stresstests."),
            ("AD", "Axis direction showing the rotation of the object in the field.", "Achsendrehung, die die Rotation des Objekts im Feld zeigt."),
            ("MW", "Moral weight after manipulation and shielding pressure.", "Moralwert nach Manipulations- und Schutzdruck."),
        ],
        [
            ("percent", "pressure or protection share", "Druck- oder Schutzanteil"),
            ("points", "value points", "Wertpunkte"),
            ("degrees", "angle degrees", "Winkelgrade"),
            ("day", "stress-test day", "Stresstesttag"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    target = max(world.products, key=lambda p: p.pv + max(0, -p.gv) * 1.4)
    print("  " + style(tr(lang, "Target object", "Zielobjekt"), 220, bold=True) + ": " + style(target.name(lang), 15, bold=True))
    rows = []
    timeline_values = []
    mp = 18.0
    sp = 24.0
    gv = target.gv
    pv = target.pv
    for day in range(1, world.ticks + 6):
        mp = clamp(mp + world.rng.uniform(4, 13) - sp * 0.04, 0, 100)
        sp = clamp(sp + 5.0 + max(0, -gv) * 0.05 + world.rng.uniform(-2, 4), 0, 100)
        dp = mp * 0.07 - sp * 0.055 + world.rng.uniform(-2, 2)
        dg = -mp * 0.035 + sp * 0.030 - target.risk * 0.012
        pv = clamp(pv + dp, -100, 100)
        gv = clamp(gv + dg, -100, 100)
        mw = moral_weight(gv, pv, target.hv, target.risk + mp * 0.15)
        ad_angle = radial_angle(gv, pv)
        state = style(tr(lang, "hype rises", "Hype steigt"), 201, bold=True) if dp > 1.5 else style(tr(lang, "shield grips", "Schutz greift"), 82, bold=True) if sp > mp else style(tr(lang, "contested", "umkämpft"), 226, bold=True)
        rows.append([unit_num(lang, day, "day", 0, 3), pct(lang, mp), pct(lang, sp), pts(lang, gv), pts(lang, pv), deg(lang, ad_angle), mcu(lang, mw), state])
        timeline_values.append((mp, sp))
    timeline_art(lang, timeline_values)
    print()
    table([tr(lang, "step", "Schritt"), ab("MP"), ab("SP"), ab("GV"), ab("PV"), ab("AD"), ab("MW"), tr(lang, "state", "Zustand")], rows, [10, 12, 12, 12, 12, 12, 12, 14])
    target.gv = gv
    target.pv = pv
    scenario_eval(lang, [
        (tr(lang, "weak shield start", "schwacher Schutzstart"), pct(lang, max(m for m, _ in timeline_values)), tr(lang, "manufactured popularity outruns correction", "hergestellte Popularität überholt die Korrektur")),
        (tr(lang, "transparent start", "transparenter Start"), pct(lang, max(s for _, s in timeline_values)), tr(lang, "public learning catches the manipulation earlier", "öffentliches Lernen erkennt die Manipulation früher")),
        (tr(lang, "attention monopoly", "Aufmerksamkeitsmonopol"), deg(lang, radial_angle(gv - 10, pv + 12)), tr(lang, "the object rotates deeper into the harmful-popular zone", "das Objekt dreht tiefer in die schädlich-beliebte Zone")),
        (tr(lang, "current stress run", "aktueller Stresslauf"), mcu(lang, moral_weight(gv, pv, target.hv, target.risk)), tr(lang, "the race is visible instead of hidden inside demand", "das Rennen ist sichtbar statt in Nachfrage versteckt")),
    ])


def section_10_claim_allocation(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 10 — Allocation of scarce goods by claim",
        "Teil 10 — Zuteilung knapper Güter nach Anspruch",
        "A scarce resource is allocated not merely by purchasing power. Need, goodness, hierarchy, popularity and moral weight form a claim level.",
        "Eine knappe Ressource wird nicht bloß nach Kaufkraft verteilt. Bedarf, Güte, Hierarchie, Popularität und Moralwert bilden eine Anspruchsstufe.",
        "This tests the radical core of the idea: a currency-like system should reveal whom something is due to, without destroying minimum protection.",
        "Dies testet den radikalen Kern der Idee: Ein währungsähnliches System soll sichtbar machen, wem etwas zusteht, ohne Mindestschutz zu zerstören.",
        [
            ("CL", "Claim level: combined claim from need, value, hierarchy and public relevance.", "Anspruchsstufe: kombinierter Anspruch aus Bedarf, Wert, Hierarchie und öffentlicher Relevanz."),
            ("ND", "Need: urgency of the recipient or purpose.", "Bedarf: Dringlichkeit des Empfängers oder Zwecks."),
            ("QU", "Quota: share of the scarce resource after minimum protection and claim weighting.", "Quote: Anteil an der knappen Ressource nach Mindestschutz und Anspruchsgewichtung."),
            ("GV", "Goodness value of the recipient or purpose.", "Gütewert des Empfängers oder Zwecks."),
            ("PV", "Popularity value; included weakly so popularity does not dominate.", "Popularitätswert; schwach einbezogen, damit Popularität nicht dominiert."),
            ("HV", "Hierarchy value; higher if collapse would affect many others.", "Hierarchiewert; höher, wenn Ausfall viele andere betreffen würde."),
            ("MW", "Moral weight entering the claim calculation.", "Moralwert, der in die Anspruchsrechnung eingeht."),
        ],
        [
            ("pieces", "pieces of the scarce resource", "Stücke der knappen Ressource"),
            ("points", "need and value points", "Bedarfs- und Wertpunkte"),
            ("percent", "allocation share", "Zuteilungsanteil"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    recipients: List[Tuple[str, float, float, float, float, float]] = []
    for case in world.insurance_cases:
        nd = clamp(case.nd + world.rng.uniform(-10, 10), 0, 100)
        recipients.append((case.name(lang), nd, case.gv, 0.0, case.hv, case.mw()))
    product_keys = {"basic_research", "care_robot", "short_video", "repair_lamp", "water_filter"}
    for p in [x for x in world.products if x.key in product_keys]:
        nd = clamp(40 + max(0, p.gv) * 0.35 + max(0, -p.pv) * 0.12 + world.rng.uniform(-12, 12), 0, 100)
        recipients.append((p.name(lang), nd, p.gv, p.pv, p.hv, p.mw()))
    floor = 2
    remaining = max(0, world.resource_stock - floor * len(recipients))
    claim_rows = []
    weights = []
    for name, nd, gv, pv, hv, mw in recipients:
        cl = clamp(0.46 * nd + 0.24 * max(0, mw) + 0.18 * hv + 0.12 * max(0, gv) + 0.04 * max(0, pv), 1, 180)
        weights.append(cl)
    total_weight = sum(weights)
    shares_for_bar = []
    for (name, nd, gv, pv, hv, mw), cl in zip(recipients, weights):
        share = floor + int(round(remaining * cl / total_weight))
        qu = share / max(1, world.resource_stock) * 100
        rank = style(tr(lang, "high", "hoch"), 82, bold=True) if cl > 80 else style(tr(lang, "middle", "mittel"), 226, bold=True) if cl > 45 else style(tr(lang, "low", "niedrig"), 208, bold=True)
        claim_rows.append((cl, [style(name, 15, bold=True), pts(lang, nd), mcu(lang, mw), pts(lang, gv), pts(lang, pv), pts(lang, hv), pts(lang, cl), unit_num(lang, share, "pieces", 0, 5), pct(lang, qu), rank]))
        shares_for_bar.append((name, share))
    claim_rows.sort(key=lambda x: x[0], reverse=True)
    shares_for_bar.sort(key=lambda x: x[1], reverse=True)
    allocation_bar(lang, shares_for_bar)
    print()
    table([tr(lang, "recipient", "Empfänger"), ab("ND"), ab("MW"), ab("GV"), ab("PV"), ab("HV"), ab("CL"), tr(lang, "allocation", "Zuteilung"), ab("QU"), tr(lang, "rank", "Rang")], [r for _, r in claim_rows], [24, 12, 12, 12, 12, 12, 12, 12, 12, 9])
    scenario_eval(lang, [
        (tr(lang, "money-only start", "nur Kaufkraft"), unit_num(lang, world.resource_stock, "pieces", 0, 5), tr(lang, "scarcity concentrates where payment is strongest", "Knappheit konzentriert sich dort, wo Zahlung am stärksten ist")),
        (tr(lang, "need-only start", "nur Bedarf"), pts(lang, statistics.mean(x[1] for x in recipients)), tr(lang, "urgency is protected, but systemic hierarchy may be ignored", "Dringlichkeit wird geschützt, aber Systemhierarchie kann fehlen")),
        (tr(lang, "claim-vector start", "Anspruchsvektor-Start"), pts(lang, statistics.mean(weights)), tr(lang, "need, value and dependency are visible together", "Bedarf, Wert und Abhängigkeit werden zusammen sichtbar")),
        (tr(lang, "minimum protection", "Mindestschutz"), unit_num(lang, floor, "pieces", 0, 5), tr(lang, "nobody is reduced to zero before ranking begins", "niemand wird vor der Rangordnung auf null gesetzt")),
    ])


def section_11_market_matrix(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 11 — Matrix of market segments",
        "Teil 11 — Matrix der Marktsegmente",
        "All market areas are compared: product, labor, stock, currency and insurance. The matrix shows where impact, risk and moral weight pull apart.",
        "Alle Marktbereiche werden verglichen: Produkt-, Arbeits-, Aktien-, Währungs- und Versicherungsmarkt. Die Matrix zeigt, wo Wirkung, Risiko und Moralwert auseinanderlaufen.",
        "A system can fail not in one object, but in the relation between whole markets. This part searches for distorted segments.",
        "Ein System kann nicht nur an einem Objekt scheitern, sondern an der Beziehung ganzer Märkte. Dieser Teil sucht verzerrte Segmente.",
        [
            ("IM", "Impact mean: average segment strength; high values move many other processes.", "Wirkungsmittel: durchschnittliche Segmentstärke; hohe Werte bewegen viele andere Prozesse."),
            ("RS", "Risk shadow: average distortion from harm, uncertainty and hidden costs.", "Risikoschatten: durchschnittliche Verzerrung durch Schaden, Unsicherheit und verdeckte Kosten."),
            ("GV", "Average goodness value of the segment.", "Durchschnittlicher Gütewert des Segments."),
            ("PV", "Average popularity value of the segment.", "Durchschnittlicher Popularitätswert des Segments."),
            ("HV", "Average hierarchy value of the segment.", "Durchschnittlicher Hierarchiewert des Segments."),
            ("MW", "Average moral weight of the segment.", "Durchschnittlicher Moralwert des Segments."),
        ],
        [
            ("points", "segment points", "Segmentpunkte"),
            ("percent", "risk or distortion percentage", "Risiko- oder Verzerrungsprozent"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    segments: List[Tuple[str, List[object], List[float], List[float]]] = []
    segments.append((tr(lang, "products", "Produkte"), list(world.products), [p.risk for p in world.products], [p.base_eur for p in world.products]))
    segments.append((tr(lang, "labor", "Arbeit"), list(world.workers), [max(0, 30 - w.wp * 0.2) for w in world.workers], [w.wage for w in world.workers]))
    segments.append((tr(lang, "stocks", "Aktien"), list(world.companies), [c.risk for c in world.companies], [c.share for c in world.companies]))
    segments.append((tr(lang, "currencies", "Währungen"), list(world.countries), [c.risk for c in world.countries], [c.course * 100 for c in world.countries]))
    segments.append((tr(lang, "insurance", "Versicherung"), list(world.insurance_cases), [i.risk for i in world.insurance_cases], [i.premium_base for i in world.insurance_cases]))
    rows = []
    labels = []
    heat = []
    for name, objects, risks, moneylike in segments:
        gv_vals = [getattr(o, "gv") for o in objects]
        pv_vals = [getattr(o, "pv", 0.0) for o in objects]
        hv_vals = [getattr(o, "hv") for o in objects]
        mw_vals = [o.mw() for o in objects]
        gv = statistics.mean(gv_vals)
        pv = statistics.mean(pv_vals)
        hv = statistics.mean(hv_vals)
        mw_val = statistics.mean(mw_vals)
        rs = statistics.mean(risks)
        im = clamp(statistics.mean([abs(v) for v in mw_vals]) * 0.55 + statistics.mean(moneylike) * 0.04 + hv * 0.25, 0, 150)
        rows.append([style(name, 15, bold=True), pts(lang, im), pct(lang, rs), pts(lang, gv), pts(lang, pv), pts(lang, hv), mcu(lang, mw_val), positive_bar(max(0, mw_val + 60), hi=160, width=22)])
        labels.append(name)
        heat.append([im - 75, 50 - rs, gv, pv, hv, mw_val])
    matrix_heatmap(lang, [ab("IM"), ab("RS"), ab("GV"), ab("PV"), ab("HV"), ab("MW")], heat)
    print()
    table([tr(lang, "segment", "Segment"), ab("IM"), ab("RS"), ab("GV"), ab("PV"), ab("HV"), ab("MW"), tr(lang, "trace", "Spur")], rows, [16, 12, 12, 12, 12, 12, 12, 24])
    avg_im = statistics.mean(float(strip_ansi(r[1]).split()[0]) for r in rows)
    avg_rs = statistics.mean(float(strip_ansi(r[2]).split()[0]) for r in rows)
    scenario_eval(lang, [
        (tr(lang, "one-market blindness", "Einmarkt-Blindheit"), pts(lang, avg_im), tr(lang, "local success can hide system-level distortion", "lokaler Erfolg kann systemweite Verzerrung verstecken")),
        (tr(lang, "risk-shadow start", "Risikoschatten-Start"), pct(lang, avg_rs + 12), tr(lang, "segments with high impact and high risk need priority review", "Segmente mit hoher Wirkung und hohem Risiko brauchen Vorrangprüfung")),
        (tr(lang, "moral-weight start", "Moralwert-Start"), mcu(lang, statistics.mean(float(strip_ansi(r[6]).split()[0]) for r in rows)), tr(lang, "the matrix turns scattered values into a system picture", "die Matrix macht aus Einzelwerten ein Systembild")),
        (tr(lang, "balanced supervision", "balancierte Aufsicht"), pct(lang, max(0, 100 - avg_rs)), tr(lang, "oversight focuses on distorted segments, not on everything equally", "Aufsicht fokussiert verzerrte Segmente, nicht alles gleich")),
    ])


def section_12_final(lang: str, world: World) -> None:
    explain_part(
        lang,
        "Part 12 — Final diagnosis: benefit, leverage and danger",
        "Teil 12 — Finale Diagnose: Nutzen, Hebel und Gefahr",
        "The final view does not claim perfect justice. It summarizes whether the simulated system makes harmful popularity, useful neglect and hierarchy movement visible.",
        "Die Endansicht behauptet keine perfekte Gerechtigkeit. Sie fasst zusammen, ob das simulierte System schädliche Popularität, nützliche Vernachlässigung und Hierarchiebewegung sichtbar macht.",
        "The construction is powerful and dangerous. It must be judged by its ability to reveal value without becoming a domination machine.",
        "Die Konstruktion ist mächtig und gefährlich. Sie muss daran gemessen werden, ob sie Wert sichtbar macht, ohne zur Herrschaftsmaschine zu werden.",
        [
            ("TD", "Trend direction: final direction of the simulated value system.", "Trendrichtung: abschließende Richtung des simulierten Wertsystems."),
            ("EL", "Ethical leverage: how strongly goodness explains decisions instead of popularity or power alone.", "Ethikhebel: wie stark Güte Entscheidungen erklärt, statt bloßer Popularität oder Macht."),
            ("RM", "Risk marker: warning signal for manipulation, harmful popularity and concentrated judgment power.", "Risikomarker: Warnsignal für Manipulation, schädliche Popularität und konzentrierte Urteilsmacht."),
            ("GV", "Final average goodness value.", "Abschließender durchschnittlicher Gütewert."),
            ("PV", "Final average popularity value.", "Abschließender durchschnittlicher Popularitätswert."),
            ("HV", "Final average hierarchy value.", "Abschließender durchschnittlicher Hierarchiewert."),
            ("MW", "Final average moral weight.", "Abschließender durchschnittlicher Moralwert."),
        ],
        [
            ("points", "final signal points", "abschließende Signalpunkte"),
            ("percent", "leverage or risk percentage", "Hebel- oder Risikoprozent"),
            ("mcu", "moral currency units", "Moralwährungseinheiten"),
        ],
    )
    objects = world.all_objects()
    gv, pv, hv, risk, mw_val = objects_avg(objects)
    harmful_popular = [o for o in objects if o.gv < -20 and o.pv > 45]
    good_unpopular = [o for o in objects if o.gv > 45 and o.pv < 5]
    el = clamp(55 + gv * 0.25 + len(good_unpopular) * 2.5 - len(harmful_popular) * 3.0, 0, 100)
    rm = clamp(len(harmful_popular) * 12 + max(0, pv - gv) * 0.28 + risk * 0.24, 0, 100)
    td = clamp(0.38 * gv + 0.18 * pv + 0.28 * hv + 0.16 * mw_val - rm * 0.20, -100, 100)
    print("  " + style(tr(lang, "Final dashboard", "Finales Armaturenbrett"), 220, bold=True))
    dashboard_gauge(lang, "TD", td, signed_value=True)
    dashboard_gauge(lang, "EL", el)
    dashboard_gauge(lang, "RM", rm)
    print()
    table([ab("TD"), ab("EL"), ab("RM"), ab("GV"), ab("PV"), ab("HV"), ab("MW")], [[pts(lang, td, signed_value=True), pct(lang, el), pct(lang, rm), pts(lang, gv), pts(lang, pv), pts(lang, hv), mcu(lang, mw_val)]], [13, 12, 12, 12, 12, 12, 12])
    print()
    if harmful_popular:
        bullet(style(tr(lang, "Danger quadrant", "Gefahrenquadrant"), 196, bold=True) + ": " + ", ".join(style(o.name(lang), 196, bold=True) for o in harmful_popular[:6]), 196)
    if good_unpopular:
        bullet(style(tr(lang, "Protection quadrant", "Schutzquadrant"), 51, bold=True) + ": " + ", ".join(style(o.name(lang), 51, bold=True) for o in good_unpopular[:6]), 51)
    bullet(style(tr(lang, "Main gain", "Hauptgewinn"), 82, bold=True) + ": " + tr(lang, "prices remain usable, but their moral and social context becomes legible.", "Preise bleiben nutzbar, aber ihr moralischer und sozialer Kontext wird lesbar."), 82)
    bullet(style(tr(lang, "Main danger", "Hauptgefahr"), 196, bold=True) + ": " + tr(lang, "whoever controls goodness labels or popularity channels can bend the whole market.", "wer Güteetiketten oder Popularitätskanäle kontrolliert, kann den ganzen Markt verbiegen."), 196)
    scenario_eval(lang, [
        (tr(lang, "open review culture", "offene Prüfungskultur"), pct(lang, min(100, el + 12)), tr(lang, "the model becomes an accountability layer", "das Modell wird zur Rechenschaftsschicht")),
        (tr(lang, "central moral monopoly", "zentrales Moralmonopol"), pct(lang, min(100, rm + 25)), tr(lang, "the same tool can become a political command system", "dasselbe Werkzeug kann zum politischen Kommandosystem werden")),
        (tr(lang, "attention capture", "Aufmerksamkeitsfang"), pct(lang, min(100, rm + 18)), tr(lang, "popularity manipulation corrupts allocation before truth catches up", "Popularitätsmanipulation korrumpiert Zuteilung, bevor Wahrheit aufholt")),
        (tr(lang, "transparent plural signals", "transparente plurale Signale"), pts(lang, td, signed_value=True), tr(lang, "the currency layer is useful when no single actor owns the whole judgment", "die Währungsschicht ist nützlich, wenn kein Einzelakteur das ganze Urteil besitzt")),
    ])


def intro(lang: str, world: World) -> None:
    title_bar(
        tr(lang, "Radial-hierarchical moral currency simulation", "Radial-hierarchische Moralwährungs-Simulation"),
        tr(lang, "very colorful PyPy3-compatible UTF-8 terminal report", "sehr bunter PyPy3-kompatibler UTF-8-Terminalbericht"),
    )
    print(style(tr(lang, "Language", "Sprache"), 220, bold=True) + style(" — ", 244) + ("English" if lang == "en" else "Deutsch"))
    print(style(tr(lang, "Start values", "Startwerte"), 220, bold=True) + style(" — ", 244) + tr(lang, "seed", "Zufallsstart") + " " + str(world.seed) + ", " + tr(lang, "steps", "Schritte") + " " + str(world.ticks) + ", " + tr(lang, "market objects", "Marktobjekte") + " " + str(len(world.products) + len(world.companies) + len(world.workers)))
    print()
    wrap_print(tr(
        lang,
        "This program simulates a currency-like value protocol rather than ordinary money alone. Market objects receive goodness, popularity, hierarchy, risk and claim signals. Each simulation part first explains what and why it simulates, then explains only the abbreviations and units used in that part.",
        "Dieses Programm simuliert ein währungsähnliches Wertprotokoll statt bloß gewöhnlichem Geld. Marktgegenstände erhalten Güte-, Popularitäts-, Hierarchie-, Risiko- und Anspruchssignale. Jeder Simulationsteil erklärt zuerst, was und warum simuliert wird, und danach nur die Kürzel und Einheiten, die genau in diesem Teil vorkommen.",
    ))
    print()
    print("  " + repeat_gradient("▰", 92, [196, 202, 208, 214, 220, 226, 118, 82, 45, 51, 39, 75, 111, 147, 201, 207]))
    print()
    compass_art(lang)


def outro(lang: str) -> None:
    print()
    print(repeat_gradient("═", 118, [207, 201, 147, 111, 75, 39, 51, 45, 82, 118, 226, 220, 214, 208, 202, 196]))
    print(style(tr(lang, "End of simulation", "Ende der Simulation"), 15, bold=True) + style(" — ", 244) + tr(lang, "all values are model values, not claims about real persons, firms or states.", "alle Werte sind Modellwerte, keine Behauptungen über reale Personen, Firmen oder Staaten."))
    print(repeat_gradient("═", 118, [196, 202, 208, 214, 220, 226, 118, 82, 45, 51, 39, 75, 111, 147, 201, 207]))


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Colorful PyPy3 UTF-8 simulation of a radial-hierarchical moral currency.")
    p.add_argument("--lang", choices=["en", "de"], default="en", help="Output language: en for English, de for German. Default: en.")
    p.add_argument("--seed", type=int, default=42, help="Random seed for reproducible simulation.")
    p.add_argument("--ticks", type=int, default=6, help="Number of dynamic simulation steps.")
    p.add_argument("--compact", action="store_true", help="Shorter tables while keeping all simulation parts.")
    p.add_argument("--color", choices=["always", "auto", "never"], default="always", help="ANSI color mode. Default: always.")
    p.add_argument("--no-animation", action="store_true", help="Disable tiny pauses between parts.")
    return p.parse_args(argv)


def maybe_pause(no_animation: bool) -> None:
    if not no_animation:
        time.sleep(0.045)


def main(argv: Optional[Sequence[str]] = None) -> int:
    global COLOR_ENABLED
    args = parse_args(argv)
    if args.color == "never":
        COLOR_ENABLED = False
    elif args.color == "auto":
        COLOR_ENABLED = sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb"
    else:
        COLOR_ENABLED = True

    world = World(seed=args.seed, ticks=args.ticks, compact=args.compact)
    intro(args.lang, world)
    parts: List[Callable[[str, World], None]] = [
        section_01_coordinate,
        section_02_governance,
        section_03_product_market,
        section_04_labor_market,
        section_05_stock_market,
        section_06_currency_market,
        section_07_insurance,
        section_08_mobility,
        section_09_manipulation,
        section_10_claim_allocation,
        section_11_market_matrix,
        section_12_final,
    ]
    for part in parts:
        maybe_pause(args.no_animation)
        part(args.lang, world)
    outro(args.lang)
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
        raise SystemExit(0)
