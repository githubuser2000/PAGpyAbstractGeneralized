#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Radial-hierarchische Moralwährungs-Simulation
==============================================

PyPy3-kompatible, reine Standardbibliothek.

Die Simulation übersetzt ein mehrdimensionales Marktmodell in farbige
Terminalausgaben: Gutartigkeit, Beliebtheit, Hierarchie, Winkelrichtung,
Arbeitsmarkt, Produktmarkt, Aktienmarkt, Währungsmarkt, Versicherungsmarkt,
Karrierebewegung, Manipulationsschutz und Anspruchsverteilung.

Start:
    pypy3 moralwaehrung_simulation_pypy3.py

Optionen:
    pypy3 moralwaehrung_simulation_pypy3.py --seed 17 --ticks 8 --color always
    pypy3 moralwaehrung_simulation_pypy3.py --no-animation --compact
    pypy3 moralwaehrung_simulation_pypy3.py --color never > bericht.txt
"""

from __future__ import annotations

import argparse
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
ITALIC = "\033[3m"
UNDER = "\033[4m"
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")

COLOR_ENABLED = True


def ansi(code: str) -> str:
    if not COLOR_ENABLED:
        return ""
    return f"\033[{code}m"


def fg(n: int) -> str:
    return ansi(f"38;5;{n}")


def bg(n: int) -> str:
    return ansi(f"48;5;{n}")


def style(text: object, color: int = 15, *, bold: bool = False, dim: bool = False, under: bool = False) -> str:
    txt = str(text)
    if not COLOR_ENABLED:
        return txt
    prefix = ""
    if bold:
        prefix += BOLD
    if dim:
        prefix += DIM
    if under:
        prefix += UNDER
    return f"{prefix}{fg(color)}{txt}{RESET}"


ABBR_COLORS: Dict[str, int] = {
    "GV": 46,
    "BV": 201,
    "HV": 226,
    "AR": 51,
    "RW": 81,
    "VW": 214,
    "REG": 39,
    "BEV": 207,
    "WIS": 118,
    "DG": 82,
    "DB": 213,
    "PR": 220,
    "NA": 75,
    "AN": 159,
    "SF": 203,
    "AG": 111,
    "AK": 213,
    "LF": 118,
    "SE": 207,
    "LO": 221,
    "AS": 220,
    "RN": 118,
    "BL": 196,
    "WK": 81,
    "RS": 203,
    "RP": 205,
    "PB": 221,
    "SA": 45,
    "AU": 82,
    "AB": 196,
    "LT": 118,
    "MP": 201,
    "SK": 51,
    "AZ": 214,
    "BR": 147,
    "QT": 118,
    "WM": 81,
    "ST": 226,
    "EH": 82,
    "RM": 196,
}

UNIT_COLORS: Dict[str, int] = {
    "Pkt": 82,
    "Grad": 51,
    "MWU": 214,
    "EUR": 220,
    "%": 207,
    "Pers": 141,
    "Trans": 208,
    "Tag": 39,
    "Stk": 118,
    "Jahr": 159,
    "Kurs": 81,
    "Zeile": 255,
}


def A(code: str) -> str:
    return style(code, ABBR_COLORS.get(code, 15), bold=True)


def U(unit: str) -> str:
    return style(unit, UNIT_COLORS.get(unit, 15), bold=True)


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", text)


def visible_len(text: str) -> int:
    return len(strip_ansi(str(text)))


def pad(text: object, width: int, align: str = "<") -> str:
    s = str(text)
    extra = max(0, width - visible_len(s))
    if align == ">":
        return " " * extra + s
    if align == "^":
        left = extra // 2
        right = extra - left
        return " " * left + s + " " * right
    return s + " " * extra


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def signed(x: float, digits: int = 1) -> str:
    return f"{x:+.{digits}f}"


def color_num(x: float, digits: int = 1, *, pos: int = 82, neg: int = 196, neu: int = 226) -> str:
    c = pos if x > 0 else neg if x < 0 else neu
    return style(signed(x, digits), c, bold=True)


def unit_num(x: float, unit: str, digits: int = 1, width: int = 7, signed_value: bool = False) -> str:
    if signed_value:
        val = color_num(x, digits)
    else:
        val_color = 82 if x > 0 else 196 if x < 0 else 226
        val = style(f"{x:.{digits}f}", val_color, bold=True)
    return pad(val, width, ">") + " " + U(unit)


def pct(x: float, digits: int = 1, signed_value: bool = False) -> str:
    return unit_num(x, "%", digits=digits, width=6, signed_value=signed_value)


def eur(x: float, digits: int = 2, signed_value: bool = False) -> str:
    return unit_num(x, "EUR", digits=digits, width=9, signed_value=signed_value)


def pkt(x: float, digits: int = 1, signed_value: bool = False) -> str:
    return unit_num(x, "Pkt", digits=digits, width=7, signed_value=signed_value)


def mwu(x: float, digits: int = 1, signed_value: bool = False) -> str:
    return unit_num(x, "MWU", digits=digits, width=7, signed_value=signed_value)


def grad(x: float, digits: int = 1) -> str:
    return unit_num(x, "Grad", digits=digits, width=7)


def repeat_gradient(chars: str, length: int, colors: Sequence[int]) -> str:
    out = []
    for i in range(length):
        out.append(style(chars[i % len(chars)], colors[i % len(colors)], bold=True))
    return "".join(out)


def title_bar(title: str, subtitle: Optional[str] = None) -> None:
    width = 112
    palette = [196, 202, 208, 214, 220, 226, 118, 82, 45, 51, 39, 75, 111, 147, 201, 207]
    print()
    print(repeat_gradient("═", width, palette))
    print(style("◆ ", 214, bold=True) + style(title, 15, bold=True) + style(" ◆", 214, bold=True))
    if subtitle:
        print(style(subtitle, 159, bold=True))
    print(repeat_gradient("═", width, list(reversed(palette))))


def small_rule() -> None:
    print(repeat_gradient("─", 112, [240, 242, 244, 246, 248, 250, 252, 250, 248, 246, 244, 242]))


def wrap_colored(text: str, width: int = 106, indent: str = "  ") -> None:
    # textwrap counts ANSI codes as visible, therefore this function is used only on mostly plain text.
    for line in textwrap.wrap(text, width=width, replace_whitespace=False):
        print(indent + line)


def explain_part(
    part_title: str,
    simulated: str,
    abbrevs: Sequence[Tuple[str, str]],
    units: Sequence[Tuple[str, str]],
) -> None:
    title_bar(part_title)
    print(style("Was hier simuliert wird", 220, bold=True) + style(" — ", 246) + simulated)
    print()
    if abbrevs:
        print(style("Kürzel in diesem Teil", 207, bold=True))
        for code, meaning in abbrevs:
            print("  " + A(code) + style(" = ", 244) + meaning)
    if units:
        print(style("Einheiten in diesem Teil", 45, bold=True))
        for code, meaning in units:
            print("  " + U(code) + style(" = ", 244) + meaning)
    small_rule()


def value_color(x: float) -> int:
    if x >= 70:
        return 82
    if x >= 30:
        return 118
    if x >= 0:
        return 226
    if x >= -30:
        return 208
    return 196


def signed_bar(x: float, *, lo: float = -100.0, hi: float = 100.0, width: int = 24) -> str:
    # centered bar for values that may be negative
    center = width // 2
    x = clamp(x, lo, hi)
    if x >= 0:
        n = int(round((x / hi) * center))
        return style("░" * center, 240) + style("█" * n, value_color(x), bold=True) + style("░" * (center - n), 240)
    n = int(round((abs(x) / abs(lo)) * center))
    return style("░" * (center - n), 240) + style("█" * n, value_color(x), bold=True) + style("░" * center, 240)


def positive_bar(x: float, *, hi: float = 100.0, width: int = 24, color: Optional[int] = None) -> str:
    x = clamp(x, 0, hi)
    n = int(round((x / hi) * width))
    c = color if color is not None else value_color(x)
    return style("█" * n, c, bold=True) + style("░" * (width - n), 240)


def row(cells: Sequence[object], widths: Sequence[int], aligns: Optional[Sequence[str]] = None) -> str:
    if aligns is None:
        aligns = ["<"] * len(cells)
    return "  ".join(pad(cell, w, a) for cell, w, a in zip(cells, widths, aligns))


def print_table(headers: Sequence[object], rows: Sequence[Sequence[object]], widths: Sequence[int], aligns: Optional[Sequence[str]] = None) -> None:
    print(row(headers, widths, aligns))
    print(row([style("─" * w, 244) for w in widths], widths))
    for r in rows:
        print(row(r, widths, aligns))


def radial_angle(gv: float, bv: float) -> float:
    ang = math.degrees(math.atan2(bv, gv))
    if ang < 0:
        ang += 360.0
    return ang


def radial_width(gv: float, bv: float) -> float:
    return math.sqrt(gv * gv + bv * bv)


def moral_value(gv: float, bv: float, hv: float, risk: float = 0.0) -> float:
    # Deliberately not pure price: good, liked and hierarchically useful objects rise.
    # Harmful but popular objects receive a penalty; positive but neglected objects receive a mild bonus.
    base = 0.48 * gv + 0.18 * bv + 0.34 * hv
    penalty = 0.24 * abs(gv) if gv < 0 and bv > 35 else 0.0
    bonus = 0.12 * abs(bv) if gv > 45 and bv < 0 else 0.0
    risk_penalty = 0.22 * risk
    return clamp(base - penalty + bonus - risk_penalty, -120.0, 130.0)


def subsidy_tax(gv: float, bv: float) -> float:
    # positive means surcharge/tax, negative means support/subsidy
    if gv < -30 and bv > 20:
        return clamp(8 + abs(gv) * 0.25 + bv * 0.12, 0, 35)
    if gv > 35 and bv < 5:
        return -clamp(5 + gv * 0.12 + abs(bv) * 0.05, 0, 22)
    if gv > 35 and bv > 35:
        return -clamp(2 + gv * 0.04, 0, 8)
    return clamp((-gv) * 0.04 if gv < 0 else 0, 0, 10)


def hierarchy_from_stages(stages: Sequence[int]) -> float:
    total = sum(max(0, x) for x in stages)
    if total <= 0:
        return 0.0
    weighted = sum((i + 1) * max(0, x) for i, x in enumerate(stages)) / total
    # five stages -> average 1..5 mapped to 0..100
    return clamp((weighted - 1.0) / 4.0 * 100.0, 0.0, 100.0)


@dataclass
class MarketObject:
    name: str
    art: str
    gv: float
    bv: float
    hv: float
    base_eur: float
    risk: float
    stock: int = 0
    demand: float = 0.0
    profit: float = 0.0
    tiers: List[int] = field(default_factory=list)
    owner: str = ""

    def ar(self) -> float:
        return radial_angle(self.gv, self.bv)

    def rw(self) -> float:
        return radial_width(self.gv, self.bv)

    def vw(self) -> float:
        return moral_value(self.gv, self.bv, self.hv, self.risk)


@dataclass
class Worker:
    name: str
    lf: float
    se: float
    gv: float
    bv: float
    hv: float
    wage: float
    matched_to: str = ""

    def vw(self) -> float:
        return moral_value((self.gv + self.se) / 2.0, self.bv, self.hv, risk=max(0, 25 - self.lf * 0.15))


@dataclass
class Company:
    name: str
    gv: float
    bv: float
    hv: float
    base_price: float
    profit: float
    employees: int
    risk: float
    share: float = 0.0

    def vw(self) -> float:
        return moral_value(self.gv, self.bv, self.hv, self.risk)


@dataclass
class Country:
    name: str
    gv: float
    bv: float
    hv: float
    risk: float
    course: float = 1.0

    def vw(self) -> float:
        return moral_value(self.gv, self.bv, self.hv, self.risk)


@dataclass
class InsuranceCase:
    name: str
    risk: float
    gv: float
    hv: float
    need: float
    premium_base: float

    def vw(self) -> float:
        return moral_value(self.gv, 0, self.hv, self.risk)


class World:
    def __init__(self, seed: int, ticks: int, compact: bool = False) -> None:
        self.rng = random.Random(seed)
        self.seed = seed
        self.ticks = ticks
        self.compact = compact
        self.products: List[MarketObject] = []
        self.companies: List[Company] = []
        self.workers: List[Worker] = []
        self.countries: List[Country] = []
        self.insurance_cases: List[InsuranceCase] = []
        self.resource_stock = 82
        self._make_world()

    def jitter(self, x: float, amount: float) -> float:
        return x + self.rng.uniform(-amount, amount)

    def _tiers(self, bias: float) -> List[int]:
        # bias > 0 pushes mass upward, bias < 0 downward
        arr = []
        for stage in range(1, 6):
            center = 8 + bias * (stage - 3)
            arr.append(max(0, int(round(self.rng.gauss(center, 2.6)))))
        if sum(arr) == 0:
            arr[self.rng.randrange(5)] = 1
        return arr

    def _make_product(self, name: str, gv: float, bv: float, base: float, risk: float, stock: int, owner: str, bias: float) -> MarketObject:
        tiers = self._tiers(bias)
        hv = hierarchy_from_stages(tiers)
        return MarketObject(
            name=name,
            art="Produkt",
            gv=clamp(self.jitter(gv, 8), -100, 100),
            bv=clamp(self.jitter(bv, 10), -100, 100),
            hv=hv,
            base_eur=base,
            risk=clamp(self.jitter(risk, 6), 0, 100),
            stock=stock,
            owner=owner,
            tiers=tiers,
        )

    def _make_world(self) -> None:
        company_specs = [
            ("NovaPflege", 78, 22, 64, 72.0, 18.0, 420, 18),
            ("HypeNet", -36, 78, 71, 41.0, 32.0, 650, 58),
            ("SolarWerk", 82, 41, 69, 96.0, 27.0, 500, 21),
            ("SchnellMode", -44, 66, 45, 28.0, 22.0, 980, 62),
            ("DatenLotse", -55, 52, 73, 88.0, 36.0, 350, 74),
            ("LernHafen", 73, 16, 51, 39.0, 13.0, 210, 12),
            ("KlinikBund", 86, -8, 76, 110.0, 9.0, 1200, 17),
            ("SpekulaBank", -18, 44, 81, 150.0, 48.0, 260, 69),
        ]
        self.companies = [
            Company(
                name=n,
                gv=clamp(self.jitter(gv, 5), -100, 100),
                bv=clamp(self.jitter(bv, 8), -100, 100),
                hv=clamp(self.jitter(hv, 5), 0, 100),
                base_price=bp,
                profit=clamp(self.jitter(p, 5), -20, 80),
                employees=emp,
                risk=clamp(self.jitter(r, 8), 0, 100),
                share=bp * self.rng.uniform(0.85, 1.2),
            )
            for n, gv, bv, hv, bp, p, emp, r in company_specs
        ]
        owner_cycle = [c.name for c in self.companies]
        prod_specs = [
            ("Heilwasser-Filter", 81, 27, 64.0, 14, 180, "NovaPflege", 1.5),
            ("Suchtspiel-Box", -72, 84, 19.0, 82, 420, "HypeNet", 0.8),
            ("Pflege-Roboter", 76, 13, 240.0, 22, 75, "NovaPflege", 2.2),
            ("Billig-Modepaket", -49, 72, 12.0, 67, 900, "SchnellMode", -0.4),
            ("Offener Lernkurs", 87, -5, 7.0, 8, 1200, "LernHafen", 0.6),
            ("Privatdaten-Handel", -83, 61, 33.0, 91, 260, "DatenLotse", 2.6),
            ("Reparierbare Lampe", 65, -13, 31.0, 11, 380, "SolarWerk", 0.9),
            ("Kurzvideo-App", -29, 92, 0.0, 55, 10000, "HypeNet", 1.1),
            ("Öko-Transport", 73, 38, 86.0, 20, 160, "SolarWerk", 1.6),
            ("Statusuhr", 4, 69, 510.0, 35, 60, "SpekulaBank", 0.1),
            ("Grundlagenforschung", 93, -31, 0.0, 6, 999, "KlinikBund", 3.0),
            ("Sicherheitssoftware", 68, 24, 49.0, 18, 340, "DatenLotse", 2.0),
        ]
        self.products = [self._make_product(*spec) for spec in prod_specs]

        first_names = [
            "Amina", "Bela", "Cem", "Daria", "Elif", "Falk", "Greta", "Hao", "Ida", "Jona",
            "Kira", "Luan", "Mina", "Niko", "Omar", "Pia", "Ravi", "Sofia", "Taro", "Yuna",
        ]
        self.workers = []
        for i, name in enumerate(first_names):
            lf = clamp(self.rng.gauss(62, 18), 15, 100)
            se = clamp(self.rng.gauss(48, 22), -40, 100)
            gv = clamp((lf * 0.35 + se * 0.65) + self.rng.uniform(-18, 18), -100, 100)
            bv = clamp(self.rng.gauss(18, 35), -100, 100)
            hv = clamp(self.rng.gauss(38, 18), 0, 100)
            wage = 1500 + lf * 37 + hv * 28 + self.rng.uniform(-420, 420)
            self.workers.append(Worker(name, lf, se, gv, bv, hv, wage))

        self.countries = [
            Country("Albia", 62, 27, 55, 22),
            Country("Borealis", 34, 44, 61, 33),
            Country("Cyrenia", 75, -9, 71, 19),
            Country("Deltora", -24, 71, 50, 67),
            Country("Eldoria", 49, 12, 37, 28),
            Country("Feronia", -39, 38, 63, 72),
        ]
        for c in self.countries:
            c.gv = clamp(self.jitter(c.gv, 10), -100, 100)
            c.bv = clamp(self.jitter(c.bv, 10), -100, 100)
            c.hv = clamp(self.jitter(c.hv, 8), 0, 100)
            c.risk = clamp(self.jitter(c.risk, 8), 0, 100)
            c.course = 0.72 + (c.vw() + 80) / 250 + self.rng.uniform(-0.06, 0.06)

        self.insurance_cases = [
            InsuranceCase("Pflegekollektiv", 28, 79, 62, 71, 210.0),
            InsuranceCase("Datenplattform", 76, -51, 73, 42, 480.0),
            InsuranceCase("Solarflotte", 24, 72, 57, 38, 330.0),
            InsuranceCase("Modekette", 69, -42, 46, 29, 390.0),
            InsuranceCase("Forschungslabor", 18, 91, 81, 88, 620.0),
            InsuranceCase("Freie Künstler", 34, 41, 31, 65, 160.0),
        ]

    def all_market_objects(self) -> List[MarketObject]:
        company_as_objects = [
            MarketObject(c.name, "Arbeitgeber", c.gv, c.bv, c.hv, c.base_price, c.risk, c.employees, profit=c.profit)
            for c in self.companies
        ]
        return self.products + company_as_objects


def section_01_coordinate_system(world: World) -> None:
    explain_part(
        "Teil 01 — Radiale Wertkarte und veränderliche Hierarchie",
        "Jeder Marktgegenstand erhält eine Lage im Kreisfeld: eine Achse bewertet Gutartigkeit, die andere Beliebtheit; die Hierarchie sitzt als zusätzliche Höhe darüber. Daraus entstehen Winkel, Radius und ein mehrdimensionaler Wertwährungswert.",
        [
            ("GV", "Gutartigkeitswert: zeigt, ob ein Gegenstand Nutzen stiftet, Schäden mindert und faire Nebenwirkungen erzeugt. Positive Werte bedeuten gesellschaftliche Güte; negative Werte bedeuten Schaden oder Ausbeutung."),
            ("BV", "Beliebtheitswert: zeigt, wie stark Bevölkerung, Kundschaft oder Öffentlichkeit ein Objekt nachfragen, mögen oder kulturell tragen. Er ist bewusst nicht dasselbe wie Gutartigkeit."),
            ("HV", "Hierarchiewert: zeigt die strukturelle Stufe eines Objekts. Hohe Werte bedeuten, dass viele untere Vorgänge, Rollen oder Folgewirkungen davon abhängen."),
            ("AR", "Achsenrichtung: der Winkel aus Gutartigkeit und Beliebtheit. Er macht sichtbar, in welchem Quadranten ein Objekt liegt: gut-beliebt, gut-unbeliebt, schädlich-beliebt oder schädlich-unbeliebt."),
            ("RW", "Radialweite: die Entfernung vom neutralen Mittelpunkt. Hohe Werte bedeuten, dass ein Objekt stark polarisiert oder sehr klar positioniert ist."),
            ("VW", "Wertwährungswert: verdichteter, aber nicht alleiniger Vergleichswert. Er kombiniert Gutartigkeit, Beliebtheit, Hierarchie und Risiko zu einer moralisch-sozialen Marktsignatur."),
        ],
        [
            ("Pkt", "Punkte auf einer normierten Skala."),
            ("Grad", "Winkelgrade der Kreisrichtung."),
            ("MWU", "Moralwährungseinheiten als farbig dargestellte Vergleichseinheit."),
        ],
    )
    objects = sorted(world.all_market_objects(), key=lambda x: x.vw(), reverse=True)
    if world.compact:
        objects = objects[:12]
    headers = ["Objekt", "Art", A("GV"), A("BV"), A("HV"), A("AR"), A("RW"), A("VW"), "Lagebild"]
    widths = [22, 13, 15, 15, 15, 16, 15, 15, 26]
    rows = []
    for obj in objects:
        quadrant = (
            style("gut + beliebt", 82, bold=True) if obj.gv >= 0 and obj.bv >= 0 else
            style("gut + unbeliebt", 51, bold=True) if obj.gv >= 0 and obj.bv < 0 else
            style("schädlich + beliebt", 196, bold=True) if obj.gv < 0 and obj.bv >= 0 else
            style("schädlich + unbeliebt", 130, bold=True)
        )
        rows.append([
            style(obj.name, 15, bold=True),
            style(obj.art, 147),
            pkt(obj.gv),
            pkt(obj.bv),
            pkt(obj.hv),
            grad(obj.ar()),
            pkt(obj.rw()),
            mwu(obj.vw()),
            quadrant,
        ])
    print_table(headers, rows, widths)
    print()
    print(style("Bunte Lesart:", 220, bold=True), "Je weiter ein Objekt vom Mittelpunkt entfernt ist, desto weniger neutral ist es. Ein hoher", A("VW"), "bedeutet nicht bloß hohen Preis, sondern ein starkes Anspruchs- und Vertrauenssignal.")
    print()
    for obj in objects[:6]:
        print("  " + pad(style(obj.name, 15, bold=True), 22) + " " + A("GV") + " " + signed_bar(obj.gv) + "  " + A("BV") + " " + signed_bar(obj.bv) + "  " + A("HV") + " " + positive_bar(obj.hv))


def section_02_governance_population(world: World) -> None:
    explain_part(
        "Teil 02 — Regierungssignal, Bevölkerungssignal und Wissenssignal",
        "Die Simulation trennt die normative Bewertung von der Popularität. Regierungen und Prüfstellen drücken Gutartigkeit nach oben oder unten; die Bevölkerung verschiebt Beliebtheit; ein Wissenssignal korrigiert beide Seiten, sobald Folgen messbar werden.",
        [
            ("REG", "Regierungssignal: institutionelle Einschätzung von Nutzen, Schaden, Fairness und zulässigen Nebenwirkungen. Es verändert vor allem den Gutartigkeitswert."),
            ("BEV", "Bevölkerungssignal: kollektive Nachfrage, Zustimmung, Ablehnung, Mode und Gewöhnung. Es verändert vor allem den Beliebtheitswert."),
            ("WIS", "Wissenssignal: sachliche Korrektur aus Forschung, Messdaten und Schadensbeobachtung. Es verhindert, dass bloße Propaganda dauerhaft als Wahrheit zählt."),
            ("GV", "Gutartigkeitswert: Zielgröße, die hier durch Regierungssignal und Wissenssignal angepasst wird."),
            ("BV", "Beliebtheitswert: Zielgröße, die hier durch Bevölkerungssignal und messbare Gewöhnung angepasst wird."),
            ("DG", "Differenz des Gutartigkeitswerts: die farbig markierte Veränderung des Gutartigkeitswerts in einem Simulationsschritt."),
            ("DB", "Differenz des Beliebtheitswerts: die farbig markierte Veränderung des Beliebtheitswerts in einem Simulationsschritt."),
        ],
        [
            ("Pkt", "Punkte auf der Wertskala."),
            ("%", "Prozentanteile für Signalstärke."),
            ("Tag", "Simulierter Entscheidungstag."),
        ],
    )
    watched = [p for p in world.products if p.name in {"Suchtspiel-Box", "Offener Lernkurs", "Privatdaten-Handel", "Reparierbare Lampe", "Grundlagenforschung", "Kurzvideo-App"}]
    for t in range(1, world.ticks + 1):
        print(style("Tag ", 39, bold=True) + unit_num(t, "Tag", digits=0, width=2) + style(" — Signale prallen aufeinander", 244))
        rows = []
        for p in watched:
            # REG: institutions reward good goods and punish harmful popular goods.
            reg = clamp(0.10 * p.gv - 0.10 * max(0, -p.gv) - 0.05 * p.risk + world.rng.uniform(-4, 4), -18, 18)
            # BEV: high popularity self-reinforces; useful unpopular goods receive slow discovery.
            bev = clamp(0.08 * p.bv + (0.04 * p.gv if p.gv > 50 else 0) + world.rng.uniform(-8, 8), -22, 22)
            # WIS: measured harm or benefit corrects REG and BEV.
            wis = clamp((p.gv - p.risk) * 0.08 + world.rng.uniform(-3, 3), -16, 16)
            dg = 0.25 * reg + 0.35 * wis
            db = 0.38 * bev + 0.04 * wis
            p.gv = clamp(p.gv + dg, -100, 100)
            p.bv = clamp(p.bv + db, -100, 100)
            rows.append([
                style(p.name, 15, bold=True),
                pct(reg, signed_value=True),
                pct(bev, signed_value=True),
                pct(wis, signed_value=True),
                pkt(dg, signed_value=True),
                pkt(db, signed_value=True),
                pkt(p.gv),
                pkt(p.bv),
            ])
        headers = ["Objekt", A("REG"), A("BEV"), A("WIS"), A("DG"), A("DB"), A("GV"), A("BV")]
        widths = [23, 13, 13, 13, 15, 15, 15, 15]
        print_table(headers, rows, widths)
        print()
    print(style("Zwischenbefund:", 220, bold=True), "Beliebtheit bewegt sich schneller als Gutartigkeit. Darum können schädliche, beliebte Objekte kurzfristig steigen, bevor", A("REG"), "und", A("WIS"), "sie bremsen.")


def section_03_product_market(world: World) -> None:
    explain_part(
        "Teil 03 — Produktmarkt mit moralischer Preisumgebung",
        "Produkte werden nicht nur nach Zahlungsbereitschaft verkauft. Nachfrage, Angebot, Steuer oder Förderung und Wertwährungswert bestimmen gemeinsam, ob ein Produkt künstlich gebremst, gestützt oder normal gehandelt wird.",
        [
            ("PR", "Preisreferenz: der simulierte Endpreis nach Beliebtheit, Gutartigkeit, Hierarchie und Steuer- oder Förderwirkung."),
            ("NA", "Nachfrageindex: zeigt, wie stark die Kundschaft ein Produkt im aktuellen Schritt zieht. Beliebtheit erhöht den Index, moralische Bremsen können ihn senken."),
            ("AN", "Angebotseinheiten: verfügbare Stückzahl des Produkts, die in diesem Schritt in den Markt gelangt."),
            ("SF", "Steuer-Förder-Satz: positiver Wert bedeutet Aufschlag für schädliche oder riskante Ware; negativer Wert bedeutet Förderung für nützliche, aber unterbewertete Ware."),
            ("GV", "Gutartigkeitswert: bestimmt, ob das Produkt eher gefördert, neutral behandelt oder belastet wird."),
            ("BV", "Beliebtheitswert: bestimmt, ob Nachfrage aus Zustimmung, Mode, Sucht oder kultureller Gewöhnung entsteht."),
            ("VW", "Wertwährungswert: verdichtetes Signal der moralisch-sozialen Qualität des Produkts."),
        ],
        [
            ("EUR", "Konventionelle Preisreferenz."),
            ("%", "Prozentwert für Nachfrage und Steuer oder Förderung."),
            ("Stk", "Stückzahl im simulierten Angebot."),
            ("MWU", "Moralwährungseinheiten."),
            ("Trans", "Gezählte Transaktionen."),
        ],
    )
    rows = []
    total_trans = 0
    for p in sorted(world.products, key=lambda x: x.bv, reverse=True):
        sf = subsidy_tax(p.gv, p.bv)
        demand_index = clamp(50 + 0.55 * p.bv + 0.12 * p.hv - max(0, -p.gv) * 0.10 - max(0, sf) * 0.35, 0, 160)
        p.demand = demand_index
        supply = max(1, int(p.stock * (0.58 + 0.42 * world.rng.random())))
        scarcity = clamp(demand_index / max(1, supply / 10), 0.35, 2.4)
        price = max(0, p.base_eur * (0.80 + scarcity * 0.19 + p.hv * 0.0025 + sf / 100.0))
        trans = int(min(supply, demand_index * world.rng.uniform(2.2, 4.8)))
        total_trans += trans
        sf_txt = pct(sf, signed_value=True)
        action = style("fördern", 82, bold=True) if sf < -1 else style("belasten", 196, bold=True) if sf > 1 else style("neutral", 226, bold=True)
        rows.append([
            style(p.name, 15, bold=True),
            eur(price),
            pct(demand_index),
            unit_num(supply, "Stk", digits=0, width=6),
            sf_txt,
            mwu(p.vw()),
            action,
        ])
    headers = ["Produkt", A("PR"), A("NA"), A("AN"), A("SF"), A("VW"), "Eingriff"]
    widths = [24, 15, 14, 12, 13, 14, 13]
    print_table(headers, rows, widths)
    print()
    print(style("Transaktionsbilanz:", 220, bold=True), unit_num(total_trans, "Trans", digits=0, width=8), "wurden simuliert. Der Marktpreis bleibt sichtbar, aber", A("SF"), "und", A("VW"), "machen die Nebenwirkungen farbig lesbar.")


def section_04_labor_market(world: World) -> None:
    explain_part(
        "Teil 04 — Arbeitsmarkt: Arbeitgeber und Arbeitskräfte bewerten einander",
        "Arbeitskräfte werden nicht allein über Lohn einsortiert, und Arbeitgeber nicht allein über Profit. Leistung, Selbstlosigkeit, hierarchische Verantwortung und moralische Unternehmensqualität bestimmen das Matching.",
        [
            ("AG", "Arbeitgeber: Organisation, die Arbeitskraft nachfragt. Ihr eigener Gutartigkeits- und Hierarchiewert beeinflusst, welche Arbeitskräfte sie verdient und anzieht."),
            ("AK", "Arbeitskraft: Person, die Leistung, Selbstlosigkeit, Beliebtheit und Aufstiegspotenzial in den Markt einbringt."),
            ("LF", "Leistungsfaktor: fachliche, organisatorische und ausdauerbezogene Fähigkeit einer Arbeitskraft."),
            ("SE", "Selbstlosigkeitsenergie: Anteil der Arbeitshaltung, der nicht nur persönlichen Gewinn, sondern auch Nutzen für andere berücksichtigt."),
            ("LO", "Lohnangebot: simulierte Geldzahlung, die aus Leistung, Hierarchie und Arbeitgeberqualität entsteht."),
            ("GV", "Gutartigkeitswert: hier sowohl persönliche als auch organisationale Güte der Handlung."),
            ("BV", "Beliebtheitswert: soziale Anschlussfähigkeit, Ruf und öffentliche Attraktivität."),
            ("HV", "Hierarchiewert: Verantwortungsstufe der Arbeitskraft oder des Arbeitgebers."),
        ],
        [
            ("EUR", "Monatliche Lohnreferenz."),
            ("Pkt", "Punkte für Leistung, Güte, Beliebtheit und Hierarchie."),
            ("Pers", "Anzahl von Personen."),
        ],
    )
    matches = []
    companies = sorted(world.companies, key=lambda c: c.vw(), reverse=True)
    for w in world.workers:
        best = None
        best_score = -10**9
        for c in companies:
            attraction = 0.42 * w.lf + 0.22 * w.se + 0.18 * c.gv + 0.18 * c.hv - abs(w.hv - c.hv) * 0.13
            if c.gv < -20 and w.se > 55:
                attraction -= 15
            attraction += world.rng.uniform(-7, 7)
            if attraction > best_score:
                best = c
                best_score = attraction
        assert best is not None
        w.matched_to = best.name
        lo = max(900, w.wage * (0.88 + best.hv / 220 + best.gv / 550))
        if best.gv < -25:
            lo *= 0.92
        if w.se > 70 and best.gv > 50:
            lo *= 1.05
        hv_change = clamp((best.hv - w.hv) * 0.025 + (w.lf - 50) * 0.015 + (best.gv / 100) * 0.6, -4.5, 5.5)
        w.hv = clamp(w.hv + hv_change, 0, 100)
        matches.append((w, best, lo, hv_change, best_score))

    if world.compact:
        matches = sorted(matches, key=lambda x: x[4], reverse=True)[:12]
    headers = [A("AK"), A("AG"), A("LF"), A("SE"), A("LO"), A("GV") + " " + A("AG"), A("HV") + " Δ"]
    widths = [15, 16, 14, 14, 15, 14, 12]
    rows = []
    for w, c, lo, hv_change, _ in sorted(matches, key=lambda x: x[2], reverse=True):
        rows.append([
            style(w.name, 15, bold=True),
            style(c.name, 147, bold=True),
            pkt(w.lf),
            pkt(w.se),
            eur(lo, 0),
            pkt(c.gv),
            pkt(hv_change, signed_value=True),
        ])
    print_table(headers, rows, widths)
    print()
    avg_wage = statistics.mean(m[2] for m in matches)
    high_moral_matches = sum(1 for w, c, _, _, _ in matches if w.se > 55 and c.gv > 40)
    print(style("Arbeitsmarkt-Befund:", 220, bold=True), unit_num(len(matches), "Pers", digits=0, width=4), "wurden zugeordnet. Durchschnittliches", A("LO"), "=", eur(avg_wage, 0), "; ethisch passende Kopplungen:", unit_num(high_moral_matches, "Pers", digits=0, width=3))


def section_05_stock_market(world: World) -> None:
    explain_part(
        "Teil 05 — Aktienmarkt: Rendite, Moralvektor und Blasenlast",
        "Unternehmen steigen nicht nur wegen Profit. Kapital sucht Gewinn, aber die Simulation markiert zusätzlich, ob ein profitabler Anstieg aus guter Wirkung oder aus gefährlicher Beliebtheit stammt.",
        [
            ("AS", "Aktienstand: simulierter Kurswert einer Unternehmensbeteiligung."),
            ("RN", "Renditenähe: kurzfristiger Gewinnimpuls aus Profit und Nachfrage nach der Aktie."),
            ("BL", "Blasenlast: Warnwert für schädliche, aber beliebte Unternehmen. Hohe Blasenlast bedeutet: Preis steigt, obwohl die moralische Grundlage schwach ist."),
            ("GV", "Gutartigkeitswert: moralischer Gegenpol zur rein finanziellen Rendite."),
            ("BV", "Beliebtheitswert: kann legitimes Vertrauen oder gefährlichen Hype anzeigen."),
            ("HV", "Hierarchiewert: zeigt die Systemrelevanz eines Unternehmens."),
            ("VW", "Wertwährungswert: zusammengesetzte Einordnung des Unternehmens jenseits des Aktienpreises."),
        ],
        [
            ("EUR", "Simulierter Aktienkurs."),
            ("%", "Prozentwert für Rendite und Blasenlast."),
            ("Pkt", "Punkte für Wertdimensionen."),
            ("MWU", "Moralwährungseinheiten."),
        ],
    )
    history: Dict[str, List[float]] = {c.name: [c.share] for c in world.companies}
    for _ in range(max(3, world.ticks)):
        for c in world.companies:
            rn = clamp(c.profit * 0.55 + c.bv * 0.08 + world.rng.uniform(-4, 4), -30, 55)
            moral_pull = c.vw() * 0.045
            bubble_drag = max(0.0, (c.bv - 35) * max(0.0, -c.gv) / 120.0)
            delta = rn * 0.018 + moral_pull * 0.012 - bubble_drag * 0.015
            c.share = max(1.0, c.share * (1 + delta / 100.0))
            history[c.name].append(c.share)
    rows = []
    for c in sorted(world.companies, key=lambda x: x.share, reverse=True):
        start = history[c.name][0]
        end = history[c.name][-1]
        rn = (end / start - 1) * 100
        bl = clamp((c.bv - 30) * max(0, -c.gv) / 65.0 + c.risk * 0.16, 0, 100)
        signal = style("solide", 82, bold=True) if c.gv > 40 and rn >= 0 else style("Hype", 201, bold=True) if bl > 45 else style("fragil", 208, bold=True) if rn < -2 else style("neutral", 226, bold=True)
        rows.append([
            style(c.name, 15, bold=True),
            eur(end),
            pct(rn, signed_value=True),
            pct(bl),
            pkt(c.gv),
            pkt(c.bv),
            pkt(c.hv),
            mwu(c.vw()),
            signal,
        ])
    headers = ["Unternehmen", A("AS"), A("RN"), A("BL"), A("GV"), A("BV"), A("HV"), A("VW"), "Lesart"]
    widths = [16, 15, 13, 13, 14, 14, 14, 14, 11]
    print_table(headers, rows, widths)
    print()
    print(style("Kapitaldiagnose:", 220, bold=True), A("BL"), "trennt profitable Güte von profitabler Verführung. Dadurch kann ein steigender", A("AS"), "gleichzeitig rot markiert werden.")


def section_06_currency_market(world: World) -> None:
    explain_part(
        "Teil 06 — Währungsmarkt: Staaten als aggregierte Wertvektoren",
        "Die Simulation übersetzt nationale Güte, Beliebtheit, Hierarchiestruktur und Risiko in Wechselkurse. Der Kurs ist dadurch nicht nur Kaufkraft, sondern auch institutionelles Vertrauen.",
        [
            ("WK", "Währungskurs: simulierter Außenwert einer Landeswährung gegenüber einer neutralen Referenz."),
            ("RS", "Risiko-Schatten: Belastung durch instabile Institutionen, Manipulierbarkeit, Krisenanfälligkeit oder hohe Schadenswerte."),
            ("GV", "Gutartigkeitswert: Qualität der öffentlichen Regeln, Produktionsfolgen und Schutzmechanismen."),
            ("BV", "Beliebtheitswert: Vertrauen, kulturelle Attraktivität und Nachfrage nach der Währung."),
            ("HV", "Hierarchiewert: strukturelle Bedeutung des Landes im simulierten Netz."),
            ("VW", "Wertwährungswert: verdichtetes Ländersignal aus Güte, Beliebtheit, Hierarchie und Risiko."),
        ],
        [
            ("Kurs", "Wechselkurszahl gegen eine neutrale Referenz."),
            ("Pkt", "Punkte für Wertdimensionen."),
            ("MWU", "Moralwährungseinheiten."),
            ("%", "Prozent für Risiko-Schatten."),
        ],
    )
    rows = []
    for c in world.countries:
        rs = clamp(c.risk + max(0, -c.gv) * 0.30 + max(0, c.bv - 60) * 0.12, 0, 100)
        institutional_pull = c.vw() * 0.009
        popularity_pull = c.bv * 0.0018
        c.course = max(0.15, c.course * (1 + institutional_pull + popularity_pull - rs * 0.0025 + world.rng.uniform(-0.025, 0.025)))
        rows.append([
            style(c.name, 15, bold=True),
            unit_num(c.course, "Kurs", digits=3, width=7),
            pct(rs),
            pkt(c.gv),
            pkt(c.bv),
            pkt(c.hv),
            mwu(c.vw()),
            positive_bar(max(0, c.vw() + 60), hi=160, width=20),
        ])
    rows.sort(key=lambda r: float(strip_ansi(r[1]).split()[0]), reverse=True)
    headers = ["Land", A("WK"), A("RS"), A("GV"), A("BV"), A("HV"), A("VW"), "Vertrauensband"]
    widths = [12, 15, 13, 14, 14, 14, 14, 24]
    print_table(headers, rows, widths)
    print()
    print(style("Währungsbefund:", 220, bold=True), "Hoher", A("BV"), "allein reicht nicht. Sobald", A("RS"), "zu hoch wird, verliert", A("WK"), "trotz Popularität Stabilität.")


def section_07_insurance_market(world: World) -> None:
    explain_part(
        "Teil 07 — Versicherungsmarkt: Risiko, Solidarität und Prämie",
        "Versicherung wird als Markt für Schutz simuliert. Hohe Risiken erhöhen die Prämie; gesellschaftlich nützliche oder systemrelevante Fälle erhalten solidarische Glättung, damit Schutz nicht nur Reichen zusteht.",
        [
            ("RP", "Risikoprofil: erwartete Schadenslast eines Falls. Es umfasst technische, soziale und moralische Risiken."),
            ("PB", "Prämienbetrag: zu zahlender Beitrag nach Risiko, Hierarchie und solidarischer Korrektur."),
            ("SA", "Solidarausgleich: Entlastung für nützliche, notwendige oder verletzliche Fälle; Belastung für riskante Ausbeutung."),
            ("GV", "Gutartigkeitswert: zeigt, ob der versicherte Fall gesellschaftlich nützlich oder schädlich wirkt."),
            ("HV", "Hierarchiewert: zeigt, ob der Fall systemisch wichtig ist und Ausfälle viele andere treffen würden."),
            ("VW", "Wertwährungswert: Gesamtlesart des Falls im Schutzmarkt."),
        ],
        [
            ("EUR", "Simulierter Monatsbeitrag."),
            ("%", "Prozentwert für Risiko und Solidarausgleich."),
            ("Pkt", "Punkte für Wertdimensionen."),
            ("MWU", "Moralwährungseinheiten."),
        ],
    )
    rows = []
    for case in world.insurance_cases:
        rp = clamp(case.risk + max(0, -case.gv) * 0.25 + (100 - case.hv) * 0.04, 0, 100)
        sa = clamp((case.gv * 0.16 + case.hv * 0.08 + case.need * 0.10) - rp * 0.20, -30, 30)
        premium = max(15, case.premium_base * (0.55 + rp / 100.0) * (1 - sa / 100.0))
        verdict = style("entlasten", 82, bold=True) if sa > 8 else style("belasten", 196, bold=True) if sa < -8 else style("glätten", 226, bold=True)
        rows.append([
            style(case.name, 15, bold=True),
            pct(rp),
            pct(sa, signed_value=True),
            eur(premium, 0),
            pkt(case.gv),
            pkt(case.hv),
            mwu(case.vw()),
            verdict,
        ])
    headers = ["Fall", A("RP"), A("SA"), A("PB"), A("GV"), A("HV"), A("VW"), "Wirkung"]
    widths = [18, 13, 13, 15, 14, 14, 14, 12]
    print_table(headers, rows, widths)
    print()
    print(style("Versicherungsbefund:", 220, bold=True), A("PB"), "ist kein nackter Risikopreis. Durch", A("SA"), "wird sichtbar, wann Risiko privat verursacht und wann Schutz gesellschaftlich begründet ist.")


def section_08_career_mobility(world: World) -> None:
    explain_part(
        "Teil 08 — Karriere, Aufstieg und Abstieg über Märkte hinweg",
        "Hierarchie ist beweglich. Arbeitskräfte, Unternehmen und Produkte steigen, wenn Leistung, Güte und tragfähige Beliebtheit zusammenkommen; sie fallen, wenn Risiko, Schaden oder leere Popularität dominieren.",
        [
            ("AU", "Aufstiegschance: Wahrscheinlichkeit, dass ein Objekt in der Hierarchie eine höhere Verantwortungsebene erreicht."),
            ("AB", "Abstiegsdruck: Wahrscheinlichkeit, dass ein Objekt wegen Schaden, Risiko, schwacher Leistung oder kollabierender Beliebtheit fällt."),
            ("LT", "Leistungstrend: aktuelle Richtung der produktiven Wirkung, berechnet aus Leistungsnähe, Profit oder Nachfrage."),
            ("GV", "Gutartigkeitswert: hebt Aufstieg, wenn Wirkung positiv ist; senkt Aufstieg, wenn Erfolg auf Schaden beruht."),
            ("BV", "Beliebtheitswert: kann Aufstieg beschleunigen, aber nur stabil, wenn der Gutartigkeitswert nicht dagegenarbeitet."),
            ("HV", "Hierarchiewert: veränderliche Ranghöhe des Objekts."),
            ("VW", "Wertwährungswert: Gesamtlesart für die Entscheidung, ob Aufstieg verdient oder riskant ist."),
        ],
        [
            ("%", "Prozentwert für Aufstiegschance und Abstiegsdruck."),
            ("Pkt", "Punkte für Trend und Hierarchie."),
            ("MWU", "Moralwährungseinheiten."),
        ],
    )
    candidates: List[Tuple[str, str, float, float, float, float, float, float]] = []
    for w in world.workers:
        lt = clamp(w.lf * 0.55 + w.se * 0.25 + world.rng.uniform(-14, 14), -100, 100)
        au = clamp(18 + lt * 0.30 + w.gv * 0.18 + w.bv * 0.08 - w.hv * 0.05, 0, 95)
        ab = clamp(12 - lt * 0.12 + max(0, -w.gv) * 0.22 + max(0, w.bv - 70) * 0.08, 0, 90)
        candidates.append((w.name, "Arbeitskraft", au, ab, lt, w.gv, w.hv, w.vw()))
    for c in world.companies:
        lt = clamp(c.profit * 1.2 + c.bv * 0.15 - c.risk * 0.15 + world.rng.uniform(-10, 10), -100, 100)
        au = clamp(16 + lt * 0.25 + c.gv * 0.16 + c.bv * 0.06, 0, 95)
        ab = clamp(10 - lt * 0.10 + max(0, -c.gv) * 0.28 + c.risk * 0.15, 0, 90)
        candidates.append((c.name, "Unternehmen", au, ab, lt, c.gv, c.hv, c.vw()))
    for p in world.products:
        lt = clamp(p.demand * 0.12 + p.bv * 0.25 + p.gv * 0.15 - p.risk * 0.18 + world.rng.uniform(-12, 12), -100, 100)
        au = clamp(14 + lt * 0.22 + p.gv * 0.19 + p.bv * 0.05, 0, 95)
        ab = clamp(14 - lt * 0.08 + max(0, -p.gv) * 0.25 + p.risk * 0.12, 0, 95)
        candidates.append((p.name, "Produkt", au, ab, lt, p.gv, p.hv, p.vw()))
    chosen = sorted(candidates, key=lambda x: x[2] - x[3], reverse=True)
    if world.compact:
        chosen = chosen[:16]
    headers = ["Objekt", "Art", A("AU"), A("AB"), A("LT"), A("GV"), A("HV"), A("VW"), "Bewegung"]
    widths = [22, 14, 13, 13, 14, 14, 14, 14, 12]
    rows = []
    for name, art, au, ab, lt, gv, hv, vw in chosen:
        movement = style("Aufstieg", 82, bold=True) if au - ab > 25 else style("Abstieg", 196, bold=True) if ab - au > 12 else style("halten", 226, bold=True)
        rows.append([style(name, 15, bold=True), style(art, 147), pct(au), pct(ab), pkt(lt, signed_value=True), pkt(gv), pkt(hv), mwu(vw), movement])
    print_table(headers, rows, widths)
    print()
    print(style("Karrierebefund:", 220, bold=True), "Der", A("HV"), "ist nicht starr. Ein beliebtes, aber schädliches Objekt kann kurzfristig oben stehen, doch hoher", A("AB"), "macht die Position instabil.")


def section_09_hype_manipulation(world: World) -> None:
    explain_part(
        "Teil 09 — Manipulations-Stresstest: schädliche Beliebtheit gegen Schutzkraft",
        "Ein beliebtes, aber schädliches Objekt erhält künstliche Popularität. Danach greifen Schutzmechanismen: Transparenz, Prüfpflicht, Verzögerung gegen Hype und stärkere Gewichtung messbarer Schäden.",
        [
            ("MP", "Manipulationspegel: künstlich erzeugte Beliebtheit durch Werbung, Gewöhnung, Datentricks oder koordinierte Verstärkung."),
            ("SK", "Schutzkraft: institutionelle und gesellschaftliche Fähigkeit, Manipulation zu erkennen und abzubremsen."),
            ("GV", "Gutartigkeitswert: fällt, wenn reale Schäden sichtbarer werden."),
            ("BV", "Beliebtheitswert: steigt durch Manipulation, kann aber durch Schutzkraft wieder sinken."),
            ("AR", "Achsenrichtung: zeigt, ob das Objekt in Richtung schädlich-beliebt kippt."),
            ("VW", "Wertwährungswert: wird durch Schaden und Manipulationsrisiko belastet."),
        ],
        [
            ("%", "Prozentwert für Manipulation und Schutzkraft."),
            ("Pkt", "Punkte für Wertdimensionen."),
            ("Grad", "Winkelgrad der Achsenrichtung."),
            ("MWU", "Moralwährungseinheiten."),
            ("Tag", "Simulierter Stresstesttag."),
        ],
    )
    target = max(world.products, key=lambda p: (p.bv + max(0, -p.gv) * 1.4))
    print(style("Zielobjekt:", 220, bold=True), style(target.name, 15, bold=True), "— hohe Beliebtheit trifft auf niedrige Güte.")
    print()
    rows = []
    mp = 18.0
    sk = 24.0
    gv = target.gv
    bv = target.bv
    for step in range(1, world.ticks + 5):
        mp = clamp(mp + world.rng.uniform(4, 13) - sk * 0.04, 0, 100)
        sk = clamp(sk + 5.0 + max(0, -gv) * 0.05 + world.rng.uniform(-2, 4), 0, 100)
        bv_delta = mp * 0.07 - sk * 0.055 + world.rng.uniform(-2, 2)
        gv_delta = -mp * 0.035 + sk * 0.030 - target.risk * 0.012
        bv = clamp(bv + bv_delta, -100, 100)
        gv = clamp(gv + gv_delta, -100, 100)
        vw = moral_value(gv, bv, target.hv, target.risk + mp * 0.15)
        ar = radial_angle(gv, bv)
        state = style("Hype steigt", 201, bold=True) if bv_delta > 1.5 else style("Schutz greift", 82, bold=True) if sk > mp else style("umkämpft", 226, bold=True)
        rows.append([
            unit_num(step, "Tag", digits=0, width=2),
            pct(mp),
            pct(sk),
            pkt(gv),
            pkt(bv),
            grad(ar),
            mwu(vw),
            state,
        ])
    headers = ["Schritt", A("MP"), A("SK"), A("GV"), A("BV"), A("AR"), A("VW"), "Zustand"]
    widths = [10, 13, 13, 14, 14, 15, 14, 14]
    print_table(headers, rows, widths)
    target.gv = gv
    target.bv = bv
    print()
    print(style("Stresstest-Befund:", 220, bold=True), "Wenn", A("MP"), "schneller wächst als", A("SK"), "wandert das Objekt in Richtung schädlich-beliebt. Der farbige", A("AR"), "macht diese Drehung sichtbar.")


def section_10_entitlement_allocation(world: World) -> None:
    explain_part(
        "Teil 10 — Anspruchsverteilung knapper Güter",
        "Ein knappes Gut wird nicht bloß an die höchste Zahlungsfähigkeit verteilt. Bedarf, Gutartigkeit, Hierarchie, Beliebtheit und Mindestschutz bilden eine Anspruchszahl; daraus entsteht eine Quote.",
        [
            ("AZ", "Anspruchszahl: kombinierter Anspruch aus Bedarf, Wertwährungswert und Hierarchieverantwortung. Sie soll anzeigen, wem ein knappes Gut eher zusteht."),
            ("BR", "Bedarf: Dringlichkeit des Falles. Hoher Bedarf kann auch bei niedriger Popularität einen Anspruch begründen."),
            ("QT", "Quote: Anteil am knappen Gut nach Mindestschutz und Anspruchsgewichtung."),
            ("GV", "Gutartigkeitswert: erhöht die Anspruchszahl, wenn der Empfänger oder Zweck positive Wirkung erzeugt."),
            ("BV", "Beliebtheitswert: fließt schwächer ein, damit bloße Popularität nicht alles dominiert."),
            ("HV", "Hierarchiewert: erhöht Anspruch, wenn ein Ausfall viele andere schädigen würde."),
            ("VW", "Wertwährungswert: Gesamtwert, der in die Anspruchszahl eingeht."),
        ],
        [
            ("Stk", "Stückzahl des knappen Guts."),
            ("Pkt", "Punkte für Bedarf und Wertdimensionen."),
            ("%", "Quote der Zuteilung."),
            ("MWU", "Moralwährungseinheiten."),
        ],
    )
    recipients: List[Tuple[str, float, float, float, float, float]] = []
    for case in world.insurance_cases:
        br = clamp(case.need + world.rng.uniform(-10, 10), 0, 100)
        recipients.append((case.name, br, case.gv, 0.0, case.hv, case.vw()))
    for p in [x for x in world.products if x.name in {"Grundlagenforschung", "Pflege-Roboter", "Kurzvideo-App", "Reparierbare Lampe", "Heilwasser-Filter"}]:
        br = clamp(40 + max(0, p.gv) * 0.35 + max(0, -p.bv) * 0.12 + world.rng.uniform(-12, 12), 0, 100)
        recipients.append((p.name, br, p.gv, p.bv, p.hv, p.vw()))
    # floor protects everyone a little; rest follows weighted claims
    floor = 2
    remaining = max(0, world.resource_stock - floor * len(recipients))
    weights = []
    for name, br, gv, bv, hv, vw in recipients:
        az = clamp(0.46 * br + 0.24 * max(0, vw) + 0.18 * hv + 0.12 * max(0, gv) + 0.04 * max(0, bv), 1, 180)
        weights.append(az)
    total_weight = sum(weights)
    rows = []
    for (name, br, gv, bv, hv, vw), az in zip(recipients, weights):
        share = floor + int(round(remaining * az / total_weight))
        qt = share / max(1, world.resource_stock) * 100
        note = style("hoch", 82, bold=True) if az > 80 else style("mittel", 226, bold=True) if az > 45 else style("niedrig", 208, bold=True)
        rows.append([
            style(name, 15, bold=True),
            pkt(br),
            mwu(vw),
            pkt(gv),
            pkt(bv),
            pkt(hv),
            pkt(az),
            unit_num(share, "Stk", digits=0, width=4),
            pct(qt),
            note,
        ])
    rows.sort(key=lambda r: float(strip_ansi(r[6]).split()[0]), reverse=True)
    headers = ["Empfänger", A("BR"), A("VW"), A("GV"), A("BV"), A("HV"), A("AZ"), "Zuteilung", A("QT"), "Rang"]
    widths = [22, 14, 14, 14, 14, 14, 14, 12, 13, 9]
    print_table(headers, rows, widths)
    print()
    print(style("Verteilungsbefund:", 220, bold=True), "Der Mindestschutz verhindert Ausschluss. Darüber entscheidet", A("AZ"), "stärker als Kaufkraft. So wird sichtbar, wem etwas zusteht, ohne Grundansprüche zu zerstören.")


def section_11_market_matrix(world: World) -> None:
    explain_part(
        "Teil 11 — Vergleich der Marktsegmente",
        "Alle Teilmärkte werden zusammengefasst. Die Matrix zeigt, wo der Wertvektor besonders stark reguliert, wo Popularität dominiert und wo Risiko die Ordnung verzerrt.",
        [
            ("WM", "Wirkungsmittel: mittlere Stärke des jeweiligen Marktsegments im System. Hohe Werte bedeuten, dass Entscheidungen in diesem Segment viele andere Vorgänge bewegen."),
            ("RS", "Risiko-Schatten: mittlere Verzerrung durch Schaden, Unsicherheit, Manipulation oder externe Kosten."),
            ("GV", "Gutartigkeitswert: durchschnittliche Güte des Marktsegments."),
            ("BV", "Beliebtheitswert: durchschnittliche öffentliche Attraktivität des Marktsegments."),
            ("HV", "Hierarchiewert: durchschnittliche strukturelle Höhe des Marktsegments."),
            ("VW", "Wertwährungswert: zusammenfassendes Signal des Marktsegments."),
        ],
        [
            ("Pkt", "Punkte für Mittelwerte."),
            ("MWU", "Moralwährungseinheiten."),
            ("%", "Prozentwert für Risiko-Schatten."),
        ],
    )
    segments = []
    prod = world.products
    comps = world.companies
    workers = world.workers
    countries = world.countries
    ins = world.insurance_cases
    segments.append(("Produktmarkt", prod, [p.risk for p in prod], [p.base_eur for p in prod]))
    segments.append(("Arbeitsmarkt", workers, [max(0, 30 - w.lf * 0.2) for w in workers], [w.wage for w in workers]))
    segments.append(("Aktienmarkt", comps, [c.risk for c in comps], [c.share for c in comps]))
    segments.append(("Währungsmarkt", countries, [c.risk for c in countries], [c.course * 100 for c in countries]))
    segments.append(("Versicherung", ins, [i.risk for i in ins], [i.premium_base for i in ins]))
    rows = []
    for name, objects, risks, moneylike in segments:
        gv_vals = [getattr(o, "gv") for o in objects]
        bv_vals = [getattr(o, "bv", 0.0) for o in objects]
        hv_vals = [getattr(o, "hv") for o in objects]
        vw_vals = [o.vw() for o in objects]
        gv = statistics.mean(gv_vals)
        bv = statistics.mean(bv_vals)
        hv = statistics.mean(hv_vals)
        vw = statistics.mean(vw_vals)
        rs = statistics.mean(risks)
        wm = clamp(statistics.mean([abs(v) for v in vw_vals]) * 0.55 + statistics.mean(moneylike) * 0.04 + hv * 0.25, 0, 150)
        rows.append([
            style(name, 15, bold=True),
            pkt(wm),
            pct(rs),
            pkt(gv),
            pkt(bv),
            pkt(hv),
            mwu(vw),
            positive_bar(max(0, vw + 60), hi=160, width=22),
        ])
    headers = ["Segment", A("WM"), A("RS"), A("GV"), A("BV"), A("HV"), A("VW"), "Farbspur"]
    widths = [16, 14, 13, 14, 14, 14, 14, 24]
    print_table(headers, rows, widths)
    print()
    print(style("Matrixbefund:", 220, bold=True), "Ein Marktsegment mit hohem", A("WM"), "und hohem", A("RS"), "ist besonders gefährlich, weil dort viele Folgen an einem verzerrten Signal hängen.")


def section_12_final_diagnosis(world: World) -> None:
    explain_part(
        "Teil 12 — Finale Diagnose: Nutzen, Hebel und Risikomarker",
        "Am Ende wird kein perfektes Urteil behauptet. Die Simulation zeigt, welche Tendenz das System erzeugt, wo ethische Hebel wirken und wo Machtmissbrauch, Hype oder falsche Hierarchie drohen.",
        [
            ("ST", "Systemtendenz: zusammenfassende Richtung des simulierten Markts nach allen Teilbewegungen."),
            ("EH", "Ethik-Hebel: Anteil der Wertentscheidungen, der tatsächlich durch Gutartigkeit statt durch bloße Beliebtheit oder Macht erklärt wird."),
            ("RM", "Risikomarker: Warnsignal für Manipulation, schädliche Popularität und zu starke staatliche oder private Bewertungsmacht."),
            ("GV", "Gutartigkeitswert: abschließender Durchschnitt über Produkte und Unternehmen."),
            ("BV", "Beliebtheitswert: abschließender Durchschnitt über Produkte und Unternehmen."),
            ("HV", "Hierarchiewert: abschließender Durchschnitt über Produkte und Unternehmen."),
            ("VW", "Wertwährungswert: abschließender Durchschnitt über Produkte und Unternehmen."),
        ],
        [
            ("Pkt", "Punkte für Gesamtsignale."),
            ("%", "Prozent für Hebel und Risikomarker."),
            ("MWU", "Moralwährungseinheiten."),
        ],
    )
    objs = world.all_market_objects()
    gv = statistics.mean(o.gv for o in objs)
    bv = statistics.mean(o.bv for o in objs)
    hv = statistics.mean(o.hv for o in objs)
    vw = statistics.mean(o.vw() for o in objs)
    harmful_popular = [o for o in objs if o.gv < -20 and o.bv > 45]
    good_unpopular = [o for o in objs if o.gv > 45 and o.bv < 5]
    eh = clamp(55 + gv * 0.25 + len(good_unpopular) * 2.5 - len(harmful_popular) * 3.0, 0, 100)
    rm = clamp(len(harmful_popular) * 12 + max(0, bv - gv) * 0.28 + statistics.mean(o.risk for o in objs) * 0.24, 0, 100)
    st = clamp(0.38 * gv + 0.18 * bv + 0.28 * hv + 0.16 * vw - rm * 0.20, -100, 100)
    headers = [A("ST"), A("EH"), A("RM"), A("GV"), A("BV"), A("HV"), A("VW")]
    rows = [[pkt(st), pct(eh), pct(rm), pkt(gv), pkt(bv), pkt(hv), mwu(vw)]]
    widths = [14, 13, 13, 14, 14, 14, 14]
    print_table(headers, rows, widths)
    print()
    print(style("Farbiges Endbild", 220, bold=True))
    print("  " + A("ST") + " " + positive_bar(max(0, st + 100), hi=200, width=44) + "  " + pkt(st, signed_value=True))
    print("  " + A("EH") + " " + positive_bar(eh, hi=100, width=44, color=82) + "  " + pct(eh))
    print("  " + A("RM") + " " + positive_bar(rm, hi=100, width=44, color=196 if rm > 45 else 226) + "  " + pct(rm))
    print()
    print(style("Interpretation:", 220, bold=True))
    wrap_colored(
        "Die Simulation zeigt eine Währung, die nicht nur zählt, sondern liest: Sie liest Güte, Beliebtheit, Hierarchie, Risiko und Anspruch. Ihr größter Vorteil ist Sichtbarkeit. Ihr größtes Risiko ist Machtkonzentration bei den Stellen, die Gutartigkeit definieren oder Beliebtheit manipulieren können.",
        width=106,
    )
    print()
    if harmful_popular:
        print(style("Rote Beobachtung:", 196, bold=True), "Schädlich-beliebte Objekte bleiben der gefährlichste Quadrant:", ", ".join(style(o.name, 196, bold=True) for o in harmful_popular[:5]))
    if good_unpopular:
        print(style("Türkise Beobachtung:", 51, bold=True), "Gut-unbeliebte Objekte brauchen Schutz vor Unterbewertung:", ", ".join(style(o.name, 51, bold=True) for o in good_unpopular[:5]))
    print()
    print(style("Praktische Regel:", 82, bold=True), "Preis darf handeln helfen, aber er darf nicht allein entscheiden. Der Wertvektor macht sichtbar, welche Transaktionen verdient, riskant, manipuliert oder schutzwürdig sind.")


def intro(world: World) -> None:
    title_bar("Radial-hierarchische Moralwährungs-Simulation", "Sehr bunte Terminalsimulation")
    print(style("Startwerte", 220, bold=True) + style(" — ", 244) + f"Seed {world.seed}, Schritte {world.ticks}, Objekte {len(world.products) + len(world.companies) + len(world.workers)}")
    print()
    wrap_colored(
        "Das Modell ordnet Marktgegenstände nicht nur nach Preis. Es kombiniert Gutartigkeit, Beliebtheit, Hierarchie, Risiko und Anspruch. Die Ausgabe erklärt vor jedem Simulationsteil nur die dort verwendeten Kürzel und färbt alle mehrbuchstabigen Kürzel sowie alle Einheiten farbig ein.",
        width=106,
    )
    print()
    print(repeat_gradient("▰", 112, [196, 202, 208, 214, 220, 226, 118, 82, 45, 51, 39, 75, 111, 147, 201, 207]))


def outro() -> None:
    print()
    print(repeat_gradient("═", 112, [207, 201, 147, 111, 75, 39, 51, 45, 82, 118, 226, 220, 214, 208, 202, 196]))
    print(style("Ende der Simulation", 15, bold=True), style("— alle Werte sind Modellwerte, keine Behauptung über reale Personen, Firmen oder Staaten.", 244))
    print(repeat_gradient("═", 112, [196, 202, 208, 214, 220, 226, 118, 82, 45, 51, 39, 75, 111, 147, 201, 207]))


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Bunte PyPy3-Simulation einer radial-hierarchischen Moralwährung.")
    p.add_argument("--seed", type=int, default=42, help="Zufallsstartwert für reproduzierbare Simulationen.")
    p.add_argument("--ticks", type=int, default=6, help="Anzahl der Simulationsschritte in dynamischen Teilen.")
    p.add_argument("--compact", action="store_true", help="Kürzere Tabellen, aber gleiche Simulationslogik.")
    p.add_argument("--color", choices=["always", "auto", "never"], default="always", help="Farbmodus der Terminalausgabe.")
    p.add_argument("--no-animation", action="store_true", help="Keine kleinen Pausen zwischen den Teilen.")
    return p.parse_args(argv)


def maybe_pause(no_animation: bool) -> None:
    if no_animation:
        return
    # Very short: colorful, but not annoying.
    time.sleep(0.06)


def main(argv: Optional[Sequence[str]] = None) -> int:
    global COLOR_ENABLED
    args = parse_args(argv)
    if args.color == "never":
        COLOR_ENABLED = False
    elif args.color == "auto":
        COLOR_ENABLED = sys.stdout.isatty() and os.environ.get("TERM", "") != "dumb"
    else:
        COLOR_ENABLED = True

    world = World(seed=args.seed, ticks=max(1, args.ticks), compact=args.compact)
    intro(world)
    parts: List[Callable[[World], None]] = [
        section_01_coordinate_system,
        section_02_governance_population,
        section_03_product_market,
        section_04_labor_market,
        section_05_stock_market,
        section_06_currency_market,
        section_07_insurance_market,
        section_08_career_mobility,
        section_09_hype_manipulation,
        section_10_entitlement_allocation,
        section_11_market_matrix,
        section_12_final_diagnosis,
    ]
    for part in parts:
        maybe_pause(args.no_animation)
        part(world)
    outro()
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
