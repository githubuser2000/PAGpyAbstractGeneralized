#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Angular Vector-Currency Economy / Winkelwährungswirtschaft
==========================================================

PyPy3-compatible simulation with colorful terminal output, bilingual English/German
script output, and a large UTF-8 art gallery at the end.

Core rule: EA, EB and EC are all Euro vectors with identical vector length.
They compete by angle, not by numerical exchange-rate length.
"""

import argparse
import csv
import math
import random
import sys
import textwrap
import zipfile
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Tuple

# -----------------------------------------------------------------------------
# 1. Terminal colors and output helpers
# -----------------------------------------------------------------------------

class Ansi:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"

COLOR_ON = True
WRAP_WIDTH = 118


def strip_ansi(s: object) -> str:
    s = str(s)
    out = []
    i = 0
    while i < len(s):
        if s[i] == "\033" and i + 1 < len(s) and s[i + 1] == "[":
            i += 2
            while i < len(s) and s[i] != "m":
                i += 1
            if i < len(s):
                i += 1
        else:
            out.append(s[i])
            i += 1
    return "".join(out)


def col(text: object, code: str) -> str:
    if not COLOR_ON:
        return str(text)
    return code + str(text) + Ansi.RESET


def bold(text: object) -> str:
    return col(text, Ansi.BOLD)


def dim(text: object) -> str:
    return col(text, Ansi.DIM)


def rainbow(text: str) -> str:
    if not COLOR_ON:
        return text
    palette = [Ansi.BRIGHT_RED, Ansi.BRIGHT_YELLOW, Ansi.BRIGHT_GREEN,
               Ansi.BRIGHT_CYAN, Ansi.BRIGHT_BLUE, Ansi.BRIGHT_MAGENTA]
    out = []
    j = 0
    for ch in text:
        if ch.isspace():
            out.append(ch)
        else:
            out.append(palette[j % len(palette)] + ch + Ansi.RESET)
            j += 1
    return "".join(out)


def hr(char: str = "─", width: Optional[int] = None) -> str:
    return char * (width or WRAP_WIDTH)


def wrap(text: str, width: Optional[int] = None, indent: int = 0) -> str:
    width = width or WRAP_WIDTH
    prefix = " " * indent
    paras = str(text).split("\n")
    out = []
    for p in paras:
        if not p.strip():
            out.append("")
        else:
            out.append(textwrap.fill(p.strip(), width=width,
                                     initial_indent=prefix,
                                     subsequent_indent=prefix))
    return "\n".join(out)


def section(title: str, color: str = Ansi.BRIGHT_CYAN) -> None:
    print()
    print(col(hr("═"), color))
    print(col(title, color + Ansi.BOLD if COLOR_ON else ""))
    print(col(hr("═"), color))


def small_section(title: str, color: str = Ansi.CYAN) -> None:
    print()
    visible = len(strip_ansi(title))
    print(col("── " + title + " " + "─" * max(1, WRAP_WIDTH - visible - 4), color))


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def fmt(x: float, n: int = 2) -> str:
    return f"{x:.{n}f}"


def gauge(value: float, width: int = 22, lo: float = 0.0, hi: float = 100.0) -> str:
    if hi == lo:
        ratio = 0.0
    else:
        ratio = clamp((value - lo) / (hi - lo), 0.0, 1.0)
    filled = int(round(ratio * width))
    empty = width - filled
    bar = "█" * filled + "░" * empty
    if value >= 70:
        c = Ansi.BRIGHT_GREEN
    elif value >= 45:
        c = Ansi.BRIGHT_YELLOW
    else:
        c = Ansi.BRIGHT_RED
    return col(bar, c) + f" {value:5.1f}"


def tension_gauge(value: float, width: int = 22) -> str:
    ratio = clamp(value / 100.0, 0.0, 1.0)
    filled = int(round(ratio * width))
    empty = width - filled
    bar = "█" * filled + "░" * empty
    if value <= 30:
        c = Ansi.BRIGHT_GREEN
    elif value <= 60:
        c = Ansi.BRIGHT_YELLOW
    else:
        c = Ansi.BRIGHT_RED
    return col(bar, c) + f" {value:5.1f}"


def table(headers: List[str], rows: List[List[object]], colors: Optional[List[str]] = None) -> str:
    str_rows = [[str(x) for x in r] for r in rows]
    widths = [len(strip_ansi(h)) for h in headers]
    for r in str_rows:
        for i, cell in enumerate(r):
            widths[i] = max(widths[i], len(strip_ansi(cell)))

    def pad_cell(cell: str, w: int) -> str:
        visible = len(strip_ansi(cell))
        return cell + " " * max(0, w - visible)

    hline = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
    mid = "├" + "┼".join("─" * (w + 2) for w in widths) + "┤"
    end = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"
    out = [hline]
    out.append("│ " + " │ ".join(col(pad_cell(headers[i], widths[i]), Ansi.BOLD) for i in range(len(headers))) + " │")
    out.append(mid)
    for ri, r in enumerate(str_rows):
        line = "│ " + " │ ".join(pad_cell(cell, widths[i]) for i, cell in enumerate(r)) + " │"
        if colors and ri < len(colors) and colors[ri]:
            line = col(line, colors[ri])
        out.append(line)
    out.append(end)
    return "\n".join(out)


def spark(values: List[float], lo: Optional[float] = None, hi: Optional[float] = None) -> str:
    chars = "▁▂▃▄▅▆▇█"
    if not values:
        return ""
    if lo is None:
        lo = min(values)
    if hi is None:
        hi = max(values)
    if hi == lo:
        return chars[0] * len(values)
    return "".join(chars[int(clamp((v - lo) / (hi - lo), 0, 0.999) * len(chars))] for v in values)


def heat_block(value: float, lo: float = 0.0, hi: float = 100.0) -> str:
    ratio = clamp((value - lo) / max(1e-9, hi - lo), 0.0, 1.0)
    blocks = "▁▂▃▄▅▆▇█"
    ch = blocks[int(ratio * (len(blocks) - 1))]
    if ratio < 0.35:
        return col(ch, Ansi.BRIGHT_GREEN)
    if ratio < 0.65:
        return col(ch, Ansi.BRIGHT_YELLOW)
    return col(ch, Ansi.BRIGHT_RED)


# -----------------------------------------------------------------------------
# 2. Angle mathematics
# -----------------------------------------------------------------------------


def norm_angle(a: float) -> float:
    return a % 360.0


def signed_delta(a: float, b: float) -> float:
    return ((b - a + 180.0) % 360.0) - 180.0


def angle_distance(a: float, b: float) -> float:
    return abs(signed_delta(a, b))


def klang(a: float, b: float) -> float:
    # 1.0 = same direction, 0.0 = opposite direction. Not positive/negative.
    return (1.0 + math.cos(math.radians(angle_distance(a, b)))) / 2.0


def gegenklang(a: float, b: float) -> float:
    return 1.0 - klang(a, b)


def circular_mean(angles: Iterable[float], weights: Iterable[float]) -> float:
    sx = 0.0
    sy = 0.0
    total = 0.0
    for a, w in zip(angles, weights):
        r = math.radians(a)
        sx += math.cos(r) * w
        sy += math.sin(r) * w
        total += w
    if total == 0 or (abs(sx) < 1e-12 and abs(sy) < 1e-12):
        return 0.0
    return norm_angle(math.degrees(math.atan2(sy, sx)))


def rotate_towards(a: float, target: float, rate: float) -> float:
    return norm_angle(a + signed_delta(a, target) * clamp(rate, 0.0, 1.0))


def softmax01(scores: List[float], temperature: float = 6.0) -> List[float]:
    if not scores:
        return []
    m = max(scores)
    vals = [math.exp((s - m) * temperature) for s in scores]
    total = sum(vals)
    if total == 0:
        return [1.0 / len(scores)] * len(scores)
    return [v / total for v in vals]


def angle_arrow(angle: float) -> str:
    arrows = ["→", "↗", "↑", "↖", "←", "↙", "↓", "↘"]
    idx = int(((norm_angle(angle) + 22.5) % 360) // 45)
    return arrows[idx]


def angle_label(angle: float) -> str:
    return f"{angle_arrow(angle)} {norm_angle(angle):6.1f}°"


def circular_noise(rng: random.Random, span: float) -> float:
    return rng.uniform(-span, span)


# -----------------------------------------------------------------------------
# 3. Localized labels
# -----------------------------------------------------------------------------

ACTIONS = ["BUY", "SELL", "WORK"]
ACTION_OFFSET = {"BUY": 0.0, "SELL": 32.0, "WORK": -42.0}

SCENARIOS = ["baseline", "resonance", "power", "wellbeing", "fragmented", "scarcity", "tradeboom"]


def L(lang: str, en: str, de: str) -> str:
    return de if lang == "de" else en


def action_label(action: str, lang: str) -> str:
    labels = {
        "BUY": ("buy market", "Kaufmarkt"),
        "SELL": ("sell market", "Verkaufsmarkt"),
        "WORK": ("labor market", "Arbeitsmarkt"),
    }
    en, de = labels[action]
    return L(lang, en, de)


def scenario_label(scenario: str, lang: str) -> str:
    labels = {
        "baseline": ("baseline", "Basislauf"),
        "resonance": ("resonance", "Resonanz"),
        "power": ("power pursuit", "Machtstreben"),
        "wellbeing": ("well-being pursuit", "Wohlbefinden"),
        "fragmented": ("fragmented angles", "zersplitterte Winkel"),
        "scarcity": ("scarcity pressure", "Mangeldruck"),
        "tradeboom": ("trade boom", "Handelsboom"),
    }
    en, de = labels.get(scenario, (scenario, scenario))
    return L(lang, en, de)


# -----------------------------------------------------------------------------
# 4. Data classes
# -----------------------------------------------------------------------------

@dataclass
class VectorCurrency:
    code: str
    name_en: str
    name_de: str
    home: str
    angle: float
    color: str
    length: float = 1.0
    power: float = 50.0
    flow: float = 0.0
    share: float = 1.0 / 3.0
    last_target: float = 0.0
    start_angle: float = 0.0

    def reset_flow(self) -> None:
        self.flow = 0.0

    def name(self, lang: str) -> str:
        return self.name_de if lang == "de" else self.name_en


@dataclass
class Sector:
    code: str
    name_en: str
    name_de: str
    need: float
    labor_need: float
    productivity: float
    base_price: float
    angle_bias: float
    exportability: float
    volatility: float
    color: str

    def name(self, lang: str) -> str:
        return self.name_de if lang == "de" else self.name_en


@dataclass
class AngleState:
    gbw: float
    buw: float
    last_hw: float = 0.0
    last_currency: str = ""
    last_klang: float = 0.0

    def action_angle(self) -> float:
        # The action angle lies between the government good pole and the people's popular pole.
        self.last_hw = circular_mean([self.gbw, self.buw], [0.54, 0.46])
        return self.last_hw

    def orth_error(self) -> float:
        return angle_distance(self.buw, self.gbw + 90.0)


@dataclass
class Country:
    code: str
    name: str
    currency: str
    color: str
    population: float
    tradition: float
    govt_power_style: float
    wellbeing_style: float
    production: Dict[str, float] = field(default_factory=dict)
    labor_hours: Dict[str, float] = field(default_factory=dict)
    imports: Dict[str, float] = field(default_factory=dict)
    exports: Dict[str, float] = field(default_factory=dict)
    demand: Dict[str, float] = field(default_factory=dict)
    supply: Dict[str, float] = field(default_factory=dict)
    satisfaction: Dict[str, float] = field(default_factory=dict)
    prices: Dict[str, float] = field(default_factory=dict)
    angles: Dict[Tuple[str, str], AngleState] = field(default_factory=dict)
    wbi: float = 55.0
    mpi: float = 55.0
    wsk: float = 55.0
    spg: float = 25.0
    fatigue: float = 0.0
    last_currency_mix: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def reset_tick(self, sectors: List[Sector]) -> None:
        self.production = {s.code: 0.0 for s in sectors}
        self.labor_hours = {s.code: 0.0 for s in sectors}
        self.imports = {s.code: 0.0 for s in sectors}
        self.exports = {s.code: 0.0 for s in sectors}
        self.demand = {s.code: 0.0 for s in sectors}
        self.supply = {s.code: 0.0 for s in sectors}
        self.satisfaction = {s.code: 0.0 for s in sectors}
        self.prices = {s.code: 0.0 for s in sectors}
        self.notes = []
        self.last_currency_mix = {}


@dataclass
class TransactionRecord:
    tick: int
    country: str
    sector: str
    action: str
    amount_ve: float
    hw: float
    chosen_currency: str
    klang_best: float
    shares: Dict[str, float]
    price_ve: float


@dataclass
class TradeRecord:
    tick: int
    sector: str
    exporter: str
    importer: str
    amount: float
    currency: str
    wk_deg: float
    angular_work: float
    joint_hw: float


# -----------------------------------------------------------------------------
# 5. UTF-8 drawing canvas
# -----------------------------------------------------------------------------

class Canvas:
    def __init__(self, w: int, h: int):
        self.w = w
        self.h = h
        self.cells: List[List[Tuple[str, str]]] = [[(" ", "") for _ in range(w)] for _ in range(h)]

    def put(self, x: int, y: int, ch: str, color: str = "") -> None:
        if 0 <= x < self.w and 0 <= y < self.h:
            self.cells[y][x] = (ch, color)

    def put_text(self, x: int, y: int, text: str, color: str = "") -> None:
        for i, ch in enumerate(text):
            self.put(x + i, y, ch, color)

    def draw_line(self, x0: int, y0: int, x1: int, y1: int, ch: str, color: str = "") -> None:
        dx = abs(x1 - x0)
        dy = -abs(y1 - y0)
        sx = 1 if x0 < x1 else -1
        sy = 1 if y0 < y1 else -1
        err = dx + dy
        x, y = x0, y0
        while True:
            self.put(x, y, ch, color)
            if x == x1 and y == y1:
                break
            e2 = 2 * err
            if e2 >= dy:
                err += dy
                x += sx
            if e2 <= dx:
                err += dx
                y += sy

    def render(self) -> str:
        lines = []
        for row in self.cells:
            pieces = []
            for ch, color in row:
                pieces.append(col(ch, color) if color else ch)
            lines.append("".join(pieces).rstrip())
        return "\n".join(lines)


def compass_canvas(points: List[Tuple[float, str, str, str]], width: int = 65, height: int = 27,
                   radius: int = 11, title: str = "") -> str:
    c = Canvas(width, height)
    cx = width // 2
    cy = height // 2
    # Circle
    for deg in range(0, 360, 3):
        x = int(round(cx + math.cos(math.radians(deg)) * radius))
        y = int(round(cy - math.sin(math.radians(deg)) * radius))
        c.put(x, y, "◦", Ansi.DIM)
    # Axis
    for x in range(cx - radius - 2, cx + radius + 3):
        c.put(x, cy, "─", Ansi.DIM)
    for y in range(cy - radius - 1, cy + radius + 2):
        c.put(cx, y, "│", Ansi.DIM)
    c.put(cx, cy, "┼", Ansi.WHITE)
    c.put_text(cx + radius + 4, cy, "0°", Ansi.DIM)
    c.put_text(cx - radius - 6, cy, "180°", Ansi.DIM)
    c.put_text(cx - 2, cy - radius - 3, "90°", Ansi.DIM)
    c.put_text(cx - 3, cy + radius + 2, "270°", Ansi.DIM)
    if title:
        c.put_text(1, 0, title[:width - 2], Ansi.BOLD)
    # Points / vectors
    for angle, label, color, end_ch in points:
        x = int(round(cx + math.cos(math.radians(angle)) * radius))
        y = int(round(cy - math.sin(math.radians(angle)) * radius))
        c.draw_line(cx, cy, x, y, "•", color)
        c.put(x, y, end_ch or angle_arrow(angle), color + Ansi.BOLD if COLOR_ON else "")
        # label near endpoint
        lx = x + (2 if x >= cx else -len(label) - 1)
        ly = y + (1 if y >= cy else -1)
        c.put_text(lx, ly, label, color + Ansi.BOLD if COLOR_ON else "")
    return c.render()


# -----------------------------------------------------------------------------
# 6. Simulation world
# -----------------------------------------------------------------------------

class AngularEconomy:
    def __init__(self, seed: int = 7, ticks: int = 18, detail: str = "full",
                 report_every: int = 1, width: int = 118, colors: bool = True,
                 explanations: bool = True, lang: str = "en", scenario: str = "baseline",
                 gallery: bool = True, compare_scenarios: bool = True):
        global COLOR_ON, WRAP_WIDTH
        COLOR_ON = colors
        WRAP_WIDTH = width
        self.rng = random.Random(seed)
        self.seed = seed
        self.max_ticks = ticks
        self.detail = detail
        self.report_every = max(1, report_every)
        self.explanations = explanations
        self.lang = lang
        self.scenario = scenario
        self.gallery = gallery
        self.compare_scenarios = compare_scenarios
        self.t = 0
        self.params = self._scenario_parameters(scenario)
        self.sectors = self._make_sectors()
        self.currencies = self._make_currencies()
        self.countries = self._make_countries()
        self.history: List[Dict[str, object]] = []
        self.transaction_history: List[TransactionRecord] = []
        self.trade_history: List[TradeRecord] = []
        self.currency_history: List[Dict[str, object]] = []
        self._apply_scenario()
        self._init_angles()

    # ------------------------------------------------------------------
    # Initialization and scenarios
    # ------------------------------------------------------------------

    def _scenario_parameters(self, scenario: str) -> Dict[str, float]:
        base = {
            "angle_noise": 18.0,
            "pop_noise": 22.0,
            "orth_noise_multiplier": 1.0,
            "production_scale": 1.0,
            "demand_scale": 1.0,
            "trade_scale": 1.0,
            "power_bias": 0.0,
            "wellbeing_bias": 0.0,
            "currency_drift_scale": 1.0,
            "fragmentation": 0.0,
            "scarcity_price": 1.0,
        }
        if scenario == "resonance":
            base.update({"angle_noise": 6.0, "pop_noise": 7.0, "production_scale": 1.08,
                         "demand_scale": 0.98, "trade_scale": 1.05, "wellbeing_bias": 8.0,
                         "power_bias": 4.0, "fragmentation": -0.25})
        elif scenario == "power":
            base.update({"angle_noise": 11.0, "pop_noise": 22.0, "production_scale": 1.03,
                         "demand_scale": 1.00, "trade_scale": 0.92, "power_bias": 14.0,
                         "wellbeing_bias": -5.0, "currency_drift_scale": 1.25, "fragmentation": 0.12})
        elif scenario == "wellbeing":
            base.update({"angle_noise": 12.0, "pop_noise": 9.0, "production_scale": 1.02,
                         "demand_scale": 0.99, "trade_scale": 0.95, "power_bias": -4.0,
                         "wellbeing_bias": 13.0, "fragmentation": -0.15})
        elif scenario == "fragmented":
            base.update({"angle_noise": 38.0, "pop_noise": 55.0, "production_scale": 0.92,
                         "demand_scale": 1.04, "trade_scale": 0.68, "power_bias": -2.0,
                         "wellbeing_bias": -8.0, "fragmentation": 0.55, "scarcity_price": 1.14})
        elif scenario == "scarcity":
            base.update({"angle_noise": 20.0, "pop_noise": 25.0, "production_scale": 0.74,
                         "demand_scale": 1.24, "trade_scale": 1.10, "power_bias": 2.0,
                         "wellbeing_bias": -12.0, "fragmentation": 0.22, "scarcity_price": 1.35})
        elif scenario == "tradeboom":
            base.update({"angle_noise": 15.0, "pop_noise": 18.0, "production_scale": 1.10,
                         "demand_scale": 1.02, "trade_scale": 1.62, "power_bias": 5.0,
                         "wellbeing_bias": 3.0, "currency_drift_scale": 1.18, "fragmentation": 0.05})
        return base

    def _make_sectors(self) -> List[Sector]:
        return [
            Sector("FOO", "food",        "Nahrung",       1.18, 0.84, 1.10, 1.10,   6.0, 0.35, 0.38, Ansi.BRIGHT_GREEN),
            Sector("ENE", "energy",      "Energie",       1.05, 0.96, 0.86, 1.62,  38.0, 0.62, 0.62, Ansi.BRIGHT_YELLOW),
            Sector("HOU", "housing",     "Wohnen",        1.00, 0.92, 0.76, 1.86, -24.0, 0.12, 0.30, Ansi.YELLOW),
            Sector("HEA", "health",      "Gesundheit",    1.12, 1.18, 0.92, 1.72,  74.0, 0.08, 0.34, Ansi.BRIGHT_MAGENTA),
            Sector("EDU", "education",   "Bildung",       0.88, 0.78, 1.12, 1.12, 112.0, 0.05, 0.28, Ansi.BRIGHT_CYAN),
            Sector("CUL", "culture",     "Kultur",        0.68, 0.42, 1.18, 0.82, 146.0, 0.30, 0.72, Ansi.MAGENTA),
            Sector("SEC", "security",    "Sicherheit",    0.74, 0.86, 0.98, 1.28, -82.0, 0.04, 0.58, Ansi.BRIGHT_BLUE),
            Sector("DAT", "data",        "Daten",         0.92, 0.56, 1.46, 1.20, 190.0, 0.76, 0.66, Ansi.CYAN),
            Sector("MOB", "mobility",    "Mobilität",     0.82, 0.73, 0.90, 1.40, 232.0, 0.58, 0.48, Ansi.BLUE),
        ]

    def _make_currencies(self) -> Dict[str, VectorCurrency]:
        data = {
            "EA": VectorCurrency("EA", "Euro-Aur", "Euro-Aur", "AUR", 8.0,   Ansi.BRIGHT_RED,   1.0, 62.0),
            "EB": VectorCurrency("EB", "Euro-Bel", "Euro-Bel", "BEL", 128.0, Ansi.BRIGHT_GREEN, 1.0, 48.0),
            "EC": VectorCurrency("EC", "Euro-Cal", "Euro-Cal", "CAL", 248.0, Ansi.BRIGHT_BLUE,  1.0, 55.0),
        }
        for cur in data.values():
            cur.start_angle = cur.angle
        return data

    def _make_countries(self) -> Dict[str, Country]:
        return {
            "AUR": Country("AUR", "Auron", "EA", Ansi.BRIGHT_RED,    1.12, 0.82, 0.68, 0.32, wbi=54, mpi=63, wsk=58, spg=28),
            "BEL": Country("BEL", "Belvar", "EB", Ansi.BRIGHT_GREEN, 0.98, 0.58, 0.43, 0.67, wbi=66, mpi=47, wsk=57, spg=24),
            "CAL": Country("CAL", "Caldra", "EC", Ansi.BRIGHT_BLUE,  1.06, 0.70, 0.57, 0.49, wbi=51, mpi=56, wsk=61, spg=31),
        }

    def _apply_scenario(self) -> None:
        for c in self.countries.values():
            c.wbi = clamp(c.wbi + self.params["wellbeing_bias"], 0, 100)
            c.mpi = clamp(c.mpi + self.params["power_bias"], 0, 100)
            c.govt_power_style = clamp(c.govt_power_style + self.params["power_bias"] / 120.0, 0.1, 0.95)
            c.wellbeing_style = clamp(c.wellbeing_style + self.params["wellbeing_bias"] / 120.0, 0.1, 0.95)
        if self.scenario == "power":
            for cur in self.currencies.values():
                cur.power = clamp(cur.power + 8.0, 0, 100)
        if self.scenario == "fragmented":
            # Move currency angles slightly away from clean 120-degree spacing.
            shifts = {"EA": -18.0, "EB": 27.0, "EC": -34.0}
            for code, shift in shifts.items():
                self.currencies[code].angle = norm_angle(self.currencies[code].angle + shift)
                self.currencies[code].start_angle = self.currencies[code].angle
        if self.scenario == "resonance":
            # Keep identical length; only rotate currencies a little toward a clean common ring.
            shifts = {"EA": 0.0, "EB": -4.0, "EC": 4.0}
            for code, shift in shifts.items():
                self.currencies[code].angle = norm_angle(self.currencies[code].angle + shift)
                self.currencies[code].start_angle = self.currencies[code].angle

    def _init_angles(self) -> None:
        country_offsets = {"AUR": -12.0, "BEL": 18.0, "CAL": -28.0}
        pop_offsets = {"AUR": 7.0, "BEL": -16.0, "CAL": 11.0}
        for c in self.countries.values():
            cur = self.currencies[c.currency]
            for sec in self.sectors:
                for action in ACTIONS:
                    noise = circular_noise(self.rng, self.params["angle_noise"])
                    gbw = cur.angle + sec.angle_bias + ACTION_OFFSET[action] + country_offsets[c.code] + noise
                    pop_noise = circular_noise(self.rng, self.params["pop_noise"])
                    if self.params["fragmentation"] > 0.4:
                        pop_noise += circular_noise(self.rng, 80.0 * self.params["fragmentation"])
                    buw = gbw + 90.0 + pop_offsets[c.code] + pop_noise
                    c.angles[(action, sec.code)] = AngleState(norm_angle(gbw), norm_angle(buw))

    # ------------------------------------------------------------------
    # Core simulation functions
    # ------------------------------------------------------------------

    def specialization_multiplier(self, country_code: str, sector_code: str) -> float:
        # Country-sector competence creates actual export possibilities.
        # This is not wealth maximization; it is productive angle tradition.
        matrix = {
            "AUR": {"ENE": 1.65, "SEC": 1.45, "MOB": 1.30, "HOU": 0.86, "CUL": 0.92},
            "BEL": {"FOO": 1.58, "HEA": 1.35, "EDU": 1.35, "HOU": 1.18, "ENE": 0.86},
            "CAL": {"DAT": 1.80, "CUL": 1.65, "MOB": 1.50, "EDU": 1.15, "FOO": 0.90},
        }
        return matrix.get(country_code, {}).get(sector_code, 1.0)

    def choose_currency(self, hw: float) -> Tuple[str, float, Dict[str, float]]:
        codes = list(self.currencies.keys())
        scores = [klang(self.currencies[k].angle, hw) for k in codes]
        shares_list = softmax01(scores, temperature=7.5)
        shares = {k: shares_list[i] for i, k in enumerate(codes)}
        best = max(codes, key=lambda k: shares[k])
        return best, scores[codes.index(best)], shares

    def price_for(self, country: Country, sec: Sector, action: str, hw: float, supply_ratio: float) -> float:
        home_cur = self.currencies[country.currency]
        currency_fit = klang(home_cur.angle, hw)
        shortage_factor = 1.0 + clamp(1.0 - supply_ratio, 0.0, 1.0) * 0.85 * self.params["scarcity_price"]
        angle_factor = 0.72 + (1.0 - currency_fit) * 0.95
        action_factor = {"BUY": 1.00, "SELL": 0.94, "WORK": 0.82}[action]
        mood_factor = 1.08 - clamp(country.wbi / 100.0, 0.0, 1.0) * 0.16
        return max(0.05, sec.base_price * shortage_factor * angle_factor * action_factor * mood_factor)

    def record_transaction(self, rec: TransactionRecord) -> None:
        self.transaction_history.append(rec)
        for code, share in rec.shares.items():
            self.currencies[code].flow += rec.amount_ve * share

    def run(self) -> None:
        self.print_header()
        if self.explanations:
            self.print_preface()
        for t in range(1, self.max_ticks + 1):
            self.t = t
            self.step()
            if t % self.report_every == 0:
                self.print_tick_report(t)
        self.print_final_report()
        if self.gallery:
            self.print_utf8_gallery()

    def simulate_silent(self) -> None:
        for t in range(1, self.max_ticks + 1):
            self.t = t
            self.step()

    def step(self) -> None:
        for cur in self.currencies.values():
            cur.reset_flow()
        for c in self.countries.values():
            c.reset_tick(self.sectors)

        self._simulate_labor_and_production()
        self._simulate_trade_triangle()
        self._simulate_goods_and_transactions()
        self._compute_indices()
        self._rotate_angles()
        self._snapshot_history()

    def _simulate_labor_and_production(self) -> None:
        for c in self.countries.values():
            labor_pressure = 0.0
            for sec in self.sectors:
                st = c.angles[("WORK", sec.code)]
                hw = st.action_angle()
                best, best_k, shares = self.choose_currency(hw)
                st.last_currency = best
                st.last_klang = best_k
                popular_fit = klang(hw, st.buw)
                gov_fit = klang(hw, st.gbw)
                base_hours = c.population * sec.labor_need * 38.0
                hours = base_hours * (0.48 + 0.52 * best_k) * (0.72 + 0.28 * popular_fit)
                hours *= (0.92 + 0.10 * c.tradition)
                c.labor_hours[sec.code] = hours
                production = hours / 38.0 * sec.productivity * (0.82 + 0.26 * gov_fit)
                production *= self.specialization_multiplier(c.code, sec.code)
                production *= self.params["production_scale"]
                c.production[sec.code] = production
                unpop = klang(hw, st.buw + 180.0)
                labor_pressure += sec.labor_need * unpop * (0.8 + 0.4 * sec.volatility)
                price = self.price_for(c, sec, "WORK", hw, supply_ratio=1.0)
                self.record_transaction(TransactionRecord(
                    self.t, c.code, sec.code, "WORK", amount_ve=hours * price / 38.0,
                    hw=hw, chosen_currency=best, klang_best=best_k, shares=shares, price_ve=price))
            c.fatigue = clamp(0.72 * c.fatigue + 3.3 * labor_pressure / max(1.0, len(self.sectors)), 0.0, 100.0)

    def _simulate_trade_triangle(self) -> None:
        # Estimate demand before trade so that excess and deficit are visible.
        for c in self.countries.values():
            for sec in self.sectors:
                soft_need = 1.0 + (c.wbi - 55.0) / 230.0
                if sec.code in ("CUL", "EDU", "DAT", "MOB"):
                    need = c.population * sec.need * clamp(soft_need, 0.75, 1.25)
                else:
                    need = c.population * sec.need
                c.demand[sec.code] = max(0.01, need * self.params["demand_scale"])

        for sec in self.sectors:
            excess = []
            deficit = []
            for c in self.countries.values():
                e = c.production[sec.code] - c.demand[sec.code]
                if e > 0:
                    excess.append([c, e])
                elif e < 0:
                    deficit.append([c, -e])
            excess.sort(key=lambda x: x[1], reverse=True)
            deficit.sort(key=lambda x: x[1], reverse=True)
            for ex in excess:
                exporter, ex_amt = ex[0], ex[1]
                if ex_amt <= 0:
                    continue
                for df in deficit:
                    importer, df_amt = df[0], df[1]
                    if df_amt <= 0 or ex_amt <= 0 or exporter.code == importer.code:
                        continue
                    sell_st = exporter.angles[("SELL", sec.code)]
                    buy_st = importer.angles[("BUY", sec.code)]
                    sell_hw = sell_st.action_angle()
                    buy_hw = buy_st.action_angle()
                    joint_hw = circular_mean([sell_hw, buy_hw], [0.50, 0.50])
                    best, best_k, shares = self.choose_currency(joint_hw)
                    trade_fit = best_k * (0.62 + 0.38 * klang(sell_hw, buy_hw))
                    amount = min(ex_amt, df_amt) * sec.exportability * self.params["trade_scale"] * (0.28 + 0.72 * trade_fit)
                    if amount <= 0.0001:
                        continue
                    exporter.exports[sec.code] += amount
                    importer.imports[sec.code] += amount
                    ex_amt -= amount
                    df[1] -= amount
                    price = (self.price_for(exporter, sec, "SELL", sell_hw, 1.0) +
                             self.price_for(importer, sec, "BUY", buy_hw, 1.0)) / 2.0
                    amount_ve = amount * price
                    for code, share in shares.items():
                        self.currencies[code].flow += amount_ve * share
                    wk = angle_distance(self.currencies[exporter.currency].angle, self.currencies[best].angle)
                    ua = math.radians(wk) * amount_ve
                    self.trade_history.append(TradeRecord(self.t, sec.code, exporter.code, importer.code,
                                                          amount, best, wk, ua, joint_hw))
                ex[1] = ex_amt

    def _simulate_goods_and_transactions(self) -> None:
        for c in self.countries.values():
            for sec in self.sectors:
                final_supply = max(0.0, c.production[sec.code] - c.exports[sec.code] + c.imports[sec.code])
                c.supply[sec.code] = final_supply
                demand = max(0.01, c.demand[sec.code])
                supply_ratio = clamp(final_supply / demand, 0.0, 1.6)
                satisfaction = clamp(final_supply / demand, 0.0, 1.0)
                c.satisfaction[sec.code] = satisfaction

                buy_st = c.angles[("BUY", sec.code)]
                buy_hw = buy_st.action_angle()
                best, best_k, shares = self.choose_currency(buy_hw)
                buy_st.last_currency = best
                buy_st.last_klang = best_k
                price_buy = self.price_for(c, sec, "BUY", buy_hw, supply_ratio)
                c.prices[sec.code] = price_buy
                amount_ve_buy = demand * price_buy * (0.42 + 0.58 * satisfaction)
                self.record_transaction(TransactionRecord(self.t, c.code, sec.code, "BUY", amount_ve_buy,
                                                          buy_hw, best, best_k, shares, price_buy))

                sell_st = c.angles[("SELL", sec.code)]
                sell_hw = sell_st.action_angle()
                best_s, best_k_s, shares_s = self.choose_currency(sell_hw)
                sell_st.last_currency = best_s
                sell_st.last_klang = best_k_s
                price_sell = self.price_for(c, sec, "SELL", sell_hw, supply_ratio)
                amount_ve_sell = max(0.0, c.production[sec.code]) * price_sell * 0.36
                self.record_transaction(TransactionRecord(self.t, c.code, sec.code, "SELL", amount_ve_sell,
                                                          sell_hw, best_s, best_k_s, shares_s, price_sell))
        total_flow = sum(cur.flow for cur in self.currencies.values())
        for cur in self.currencies.values():
            cur.share = cur.flow / total_flow if total_flow > 0 else 1.0 / 3.0

    def _compute_indices(self) -> None:
        for c in self.countries.values():
            mix = {k: 0.0 for k in self.currencies}
            country_flow = 0.0
            for rec in self.transaction_history:
                if rec.tick == self.t and rec.country == c.code:
                    country_flow += rec.amount_ve
                    for code, sh in rec.shares.items():
                        mix[code] += rec.amount_ve * sh
            if country_flow > 0:
                c.last_currency_mix = {k: v / country_flow for k, v in mix.items()}
            else:
                c.last_currency_mix = {k: 1.0 / 3.0 for k in mix}

            need_weighted_sat = 0.0
            pop_harmony = 0.0
            gov_pop_gap = 0.0
            curr_gap = 0.0
            orth_gap = 0.0
            weight_sum = 0.0
            production_ratio_acc = 0.0
            price_pressure = 0.0

            for sec in self.sectors:
                w = sec.need
                weight_sum += w
                need_weighted_sat += c.satisfaction[sec.code] * w
                production_ratio_acc += clamp(c.production[sec.code] / max(0.01, c.demand[sec.code]), 0.0, 1.6) * w
                price_pressure += c.prices[sec.code] / max(0.01, sec.base_price) * w
                for action in ACTIONS:
                    st = c.angles[(action, sec.code)]
                    hw = st.last_hw if st.last_hw else st.action_angle()
                    pop_harmony += klang(hw, st.buw) * (w / 3.0)
                    gov_pop_gap += angle_distance(st.gbw, st.buw - 90.0) / 90.0 * (w / 3.0)
                    best_currency = self.currencies.get(st.last_currency, self.currencies[c.currency])
                    curr_gap += (1.0 - klang(best_currency.angle, hw)) * (w / 3.0)
                    orth_gap += st.orth_error() / 90.0 * (w / 3.0)

            weight_sum = max(weight_sum, 0.0001)
            sat = need_weighted_sat / weight_sum
            prod_ratio = production_ratio_acc / weight_sum
            pop_h = pop_harmony / weight_sum
            gov_pop = clamp(gov_pop_gap / weight_sum, 0.0, 2.0)
            curr_g = clamp(curr_gap / weight_sum, 0.0, 1.0)
            orth_g = clamp(orth_gap / weight_sum, 0.0, 2.0)
            price_p = price_pressure / weight_sum

            own_share = c.last_currency_mix.get(c.currency, 0.0)
            own_currency = self.currencies[c.currency]
            gov_currency_fit = []
            for sec in self.sectors:
                for action in ACTIONS:
                    st = c.angles[(action, sec.code)]
                    gov_currency_fit.append(klang(own_currency.angle, st.gbw))
            gov_fit_avg = sum(gov_currency_fit) / len(gov_currency_fit)

            trade_flow = sum(c.imports.values()) + sum(c.exports.values())
            trade_norm = clamp(trade_flow / (sum(c.demand.values()) + 0.01), 0.0, 1.0)

            wbi_target = 100.0 * (0.58 * sat + 0.30 * pop_h + 0.12 * clamp(1.0 - c.fatigue / 70.0, 0.0, 1.0))
            wbi_target = wbi_target * (0.90 + 0.12 * c.wellbeing_style)

            mpi_target = 100.0 * (0.52 * own_share + 0.26 * gov_fit_avg + 0.14 * clamp(prod_ratio / 1.25, 0.0, 1.0) + 0.08 * trade_norm)
            mpi_target = mpi_target * (0.92 + 0.10 * c.govt_power_style)

            spg_target = 100.0 * clamp(0.34 * gov_pop + 0.28 * curr_g + 0.22 * orth_g + 0.16 * clamp(price_p - 1.0, 0.0, 1.4), 0.0, 1.0)
            wsk_target = 100.0 * clamp(0.42 * sat + 0.27 * clamp(prod_ratio / 1.2, 0.0, 1.0) + 0.17 * trade_norm + 0.14 * (1.0 - spg_target / 110.0), 0.0, 1.0)

            c.wbi = clamp(0.72 * c.wbi + 0.28 * wbi_target, 0.0, 100.0)
            c.mpi = clamp(0.70 * c.mpi + 0.30 * mpi_target, 0.0, 100.0)
            c.spg = clamp(0.68 * c.spg + 0.32 * spg_target, 0.0, 100.0)
            c.wsk = clamp(0.70 * c.wsk + 0.30 * wsk_target, 0.0, 100.0)

            weakest = min(self.sectors, key=lambda s: c.satisfaction[s.code])
            strongest = max(self.sectors, key=lambda s: c.satisfaction[s.code])
            if c.satisfaction[weakest.code] < 0.72:
                c.notes.append(L(self.lang,
                    f"scarcity angle in {weakest.name(self.lang)} ({c.satisfaction[weakest.code]*100:.0f}% of need covered)",
                    f"Mangelwinkel bei {weakest.name(self.lang)} ({c.satisfaction[weakest.code]*100:.0f}% Bedarf gedeckt)"))
            if c.last_currency_mix.get(c.currency, 0.0) < 0.36:
                dominant = max(c.last_currency_mix, key=lambda k: c.last_currency_mix[k])
                c.notes.append(L(self.lang,
                    f"foreign vector currency {dominant} over-sounds the home vector",
                    f"Fremdwährung {dominant} überklingt die eigene Währung"))
            if c.satisfaction[strongest.code] > 0.98:
                c.notes.append(L(self.lang,
                    f"stable coverage in {strongest.name(self.lang)}",
                    f"stabile Deckung bei {strongest.name(self.lang)}"))

        for code, cur in self.currencies.items():
            home = self.countries[cur.home]
            target = 100.0 * (0.58 * cur.share + 0.42 * home.mpi / 100.0)
            cur.power = clamp(0.78 * cur.power + 0.22 * target, 0.0, 100.0)

    def _rotate_angles(self) -> None:
        for code, cur in self.currencies.items():
            angles = [cur.angle]
            weights = [2.0 + cur.power / 50.0]
            for rec in self.transaction_history:
                if rec.tick != self.t:
                    continue
                sh = rec.shares.get(code, 0.0)
                if sh > 0.08:
                    angles.append(rec.hw)
                    weights.append(sh * rec.amount_ve / 8.0)
            home = self.countries[cur.home]
            for sec in self.sectors:
                for action in ACTIONS:
                    st = home.angles[(action, sec.code)]
                    angles.append(st.gbw)
                    weights.append(0.06 * home.govt_power_style)
            target = circular_mean(angles, weights)
            cur.last_target = target
            cur.angle = rotate_towards(cur.angle, target, (0.020 + 0.0006 * cur.power) * self.params["currency_drift_scale"])
            cur.length = 1.0  # Hard rule: all vector-currency lengths remain Euro length.

        for c in self.countries.values():
            own_cur = self.currencies[c.currency]
            for sec in self.sectors:
                sat = c.satisfaction.get(sec.code, 0.8)
                for action in ACTIONS:
                    st = c.angles[(action, sec.code)]
                    hw = st.last_hw if st.last_hw else st.action_angle()
                    gov_target = circular_mean([st.gbw, own_cur.angle, hw],
                                               [2.4 * c.tradition, 1.1 * c.govt_power_style, 0.6 + c.mpi / 120.0])
                    st.gbw = rotate_towards(st.gbw, gov_target, 0.006 + 0.010 * sec.volatility)
                    if action == "BUY":
                        pop_target = hw if sat >= 0.82 else norm_angle(hw + 180.0)
                        pop_rate = 0.012 + 0.018 * sec.volatility
                    elif action == "WORK":
                        pop_target = hw if c.fatigue < 32 else norm_angle(hw + 180.0)
                        pop_rate = 0.009 + 0.012 * sec.volatility
                    else:
                        export_signal = clamp(c.exports[sec.code] / max(0.01, c.production[sec.code]), 0.0, 1.0)
                        pop_target = hw if export_signal > 0.10 or sat > 0.88 else circular_mean([hw, st.buw], [0.4, 1.0])
                        pop_rate = 0.007 + 0.010 * sec.volatility
                    ortho_anchor = norm_angle(st.gbw + 90.0)
                    mixed_target = circular_mean([pop_target, ortho_anchor], [1.0, 0.55 + c.tradition])
                    st.buw = rotate_towards(st.buw, mixed_target, pop_rate)

    def _snapshot_history(self) -> None:
        for c in self.countries.values():
            row = {
                "tick": self.t,
                "country": c.code,
                "WBI": round(c.wbi, 4),
                "MPI": round(c.mpi, 4),
                "ES": round(c.wsk, 4),
                "TD": round(c.spg, 4),
                "FTD": round(c.fatigue, 4),
                "own_currency_share": round(c.last_currency_mix.get(c.currency, 0.0), 4),
                "imports": round(sum(c.imports.values()), 4),
                "exports": round(sum(c.exports.values()), 4),
                "production": round(sum(c.production.values()), 4),
                "need": round(sum(c.demand.values()), 4),
            }
            for sec in self.sectors:
                row[f"sat_{sec.code}"] = round(c.satisfaction[sec.code], 4)
                row[f"price_{sec.code}"] = round(c.prices[sec.code], 4)
            self.history.append(row)
        crow = {"tick": self.t}
        for code, cur in self.currencies.items():
            crow[f"{code}_angle"] = round(cur.angle, 4)
            crow[f"{code}_length"] = round(cur.length, 4)
            crow[f"{code}_power"] = round(cur.power, 4)
            crow[f"{code}_flow"] = round(cur.flow, 4)
            crow[f"{code}_share"] = round(cur.share, 4)
        self.currency_history.append(crow)

    # ------------------------------------------------------------------
    # Local explanation blocks
    # ------------------------------------------------------------------

    def print_header(self) -> None:
        title = L(self.lang,
                  "ANGULAR VECTOR-CURRENCY ECONOMY — COLORFUL PYPY3 SIMULATION",
                  "WINKELWÄHRUNGSWIRTSCHAFT — BUNTE PYPY3-SIMULATION")
        print(rainbow(title))
        print(col(hr("═"), Ansi.BRIGHT_MAGENTA))
        print(wrap(L(self.lang,
            "The model simulates three governments, three markets and three competing Euro vectors. EA, EB and EC all have the same vector length: |€⃗| = 1 VE. Competition does not come from a numerical exchange-rate multiplier. It comes from angle, direction, resonance, power attachment and well-being.",
            "Das Modell simuliert drei Regierungen, drei Märkte und drei konkurrierende Euro-Vektoren. EA, EB und EC haben alle dieselbe Vektorlänge: |€⃗| = 1 VE. Konkurrenz entsteht nicht durch einen Zahlen-Wechselkurs. Sie entsteht durch Winkel, Richtung, Resonanz, Machtbindung und Wohlbefinden.")))
        print()
        print(col(L(self.lang, "Run parameters:", "Startparameter:"), Ansi.BOLD),
              f"seed={self.seed}, ticks={self.max_ticks}, detail={self.detail}, scenario={scenario_label(self.scenario, self.lang)}, lang={self.lang}, colors={'on' if COLOR_ON else 'off'}")

    def print_preface(self) -> None:
        section(L(self.lang, "How to read this output", "So liest du diese Ausgabe"), Ansi.BRIGHT_MAGENTA)
        print(wrap(L(self.lang,
            "The explanations are not collected into one giant global dictionary. Each simulation part prints only the abbreviations and units that are used in that part. This is intentional: the currency ring explains vector length and angle share; the labor part explains labor hours and fatigue; the goods part explains need, supply and vector-Euro prices; the trade part explains angular work; the index part explains power and well-being.",
            "Die Erklärungen werden nicht in einem einzigen globalen Wörterbuch gesammelt. Jeder Simulationsteil erklärt nur die Kürzel und Einheiten, die genau dort benutzt werden. Das ist Absicht: Der Währungsring erklärt Vektorlänge und Winkelanteil; der Arbeitsteil erklärt Arbeitsstunden und Ermüdung; der Güterteil erklärt Bedarf, Versorgung und Vektor-Euro-Preise; der Handelsteil erklärt Umlenkungsarbeit; der Indexteil erklärt Macht und Wohlbefinden.")))
        print()
        print(wrap(L(self.lang,
            "Important: good versus evil remains good versus evil in the angular sense of this model. It is not a subsidy axis, not a penalty axis, and not positive versus negative. The government sets a good/evil direction on a circle; the population sets an orthogonal popular/unpopular direction; the market action lies between these angular poles.",
            "Wichtig: Gut gegen Böse bleibt in diesem Modell Gut gegen Böse im Winkelsinn. Es ist keine Förderachse, keine Strafachse und nicht positiv gegen negativ. Die Regierung setzt eine Gut/Böse-Richtung auf dem Kreis; die Bevölkerung setzt eine orthogonale Beliebt/Unbeliebt-Richtung; die Markthandlung liegt zwischen diesen Winkelpolen.")))

    def explain_part(self, key: str) -> None:
        if not self.explanations:
            return
        data = self._part_explanations()[key]
        print(wrap(data["why"]))
        print(table(data["headers"], data["rows"]))

    def _part_explanations(self) -> Dict[str, Dict[str, object]]:
        lang = self.lang
        return {
            "currency": {
                "why": L(lang,
                    "This part simulates the three currencies as directions on one ring. Every currency unit has identical Euro-vector length. The table therefore explains angle competition, not numerical exchange rates. The simulated question is: which vector direction attracts the most action flow in this tick?",
                    "Dieser Teil simuliert die drei Währungen als Richtungen auf einem Ring. Jede Währungseinheit hat dieselbe Euro-Vektorlänge. Die Tabelle erklärt deshalb Winkelkonkurrenz, nicht Zahlen-Wechselkurse. Simuliert wird: Welche Vektorrichtung zieht in diesem Tick den meisten Handlungsfluss an?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["EA/EB/EC", L(lang, "currency code", "Währungscode"), L(lang, "The three competing Euro vectors.", "Die drei konkurrierenden Euro-Vektoren.")],
                    ["|€⃗|", "VE", L(lang, "Vector length. It must remain 1.000 for all currencies.", "Vektorlänge. Sie muss bei allen Währungen 1.000 bleiben.")],
                    ["θ°", L(lang, "degrees", "Grad"), L(lang, "Current direction of a currency on the ring.", "Aktuelle Richtung einer Währung auf dem Ring.")],
                    ["Share", L(lang, "0..100%", "0..100%"), L(lang, "Part of this tick's transaction flow captured by the currency angle.", "Anteil des Transaktionsflusses dieses Ticks, der vom Währungswinkel gebunden wird.")],
                    ["Power", "0..100", L(lang, "Accumulated attachment of market action and home government to this vector.", "Aufgebaute Bindung von Markthandlung und Heimatregierung an diesen Vektor.")],
                    ["WK°", L(lang, "degrees", "Grad"), L(lang, "Angle distance between two currencies; not a money exchange rate.", "Winkelabstand zwischen zwei Währungen; kein Geld-Wechselkurs.")],
                    ["KLG", "0..1", L(lang, "Angular resonance. 1 means same direction, 0 means opposite direction.", "Winkelklang. 1 bedeutet gleiche Richtung, 0 bedeutet Gegenrichtung.")],
                ],
            },
            "labor": {
                "why": L(lang,
                    "This part simulates labor as an angular action, not merely as paid time. Work produces goods when the labor angle resonates with a currency, the government's good pole and the population's popular pole. The simulated question is: where does work create capacity, and where does it create fatigue?",
                    "Dieser Teil simuliert Arbeit als Winkelhandlung, nicht nur als bezahlte Zeit. Arbeit erzeugt Güter, wenn der Arbeitswinkel mit Währung, Gut-Pol der Regierung und Beliebt-Pol der Bevölkerung zusammenklingt. Simuliert wird: Wo erzeugt Arbeit Kapazität, und wo erzeugt sie Ermüdung?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["Workθ", L(lang, "degrees", "Grad"), L(lang, "Action angle of labor in a sector.", "Handlungswinkel der Arbeit in einem Sektor.")],
                    ["WC", L(lang, "currency code", "Währungscode"), L(lang, "Currency whose angle fits the labor action best.", "Währung, deren Winkel am besten zur Arbeitsentscheidung passt.")],
                    ["h", L(lang, "hours", "Stunden"), L(lang, "Abstract labor hours allocated this tick.", "Abstrakte Arbeitsstunden dieses Ticks.")],
                    ["Prod", L(lang, "goods units", "Gütereinheiten"), L(lang, "Production created by labor and productivity.", "Produktion, die aus Arbeit und Produktivität entsteht.")],
                    ["FTD", "0..100", L(lang, "Fatigue from labor close to the unpopular pole.", "Ermüdung durch Arbeit nahe am Unbeliebt-Pol.")],
                ],
            },
            "goods": {
                "why": L(lang,
                    "This part simulates need, supply, satisfaction and vector-Euro prices. Price is a count of equal-length Euro vectors. It does not stretch a vector. The simulated question is: how many identical vector-Euro units are needed when supply, demand and angular tension meet?",
                    "Dieser Teil simuliert Bedarf, Versorgung, Deckung und Vektor-Euro-Preise. Preis ist eine Anzahl gleich langer Euro-Vektoren. Er verlängert keinen Vektor. Simuliert wird: Wie viele identische Vektor-Euro-Einheiten werden gebraucht, wenn Versorgung, Nachfrage und Winkelspannung zusammentreffen?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["Need", L(lang, "goods units", "Gütereinheiten"), L(lang, "Population demand in the sector.", "Bevölkerungsbedarf im Sektor.")],
                    ["Supply", L(lang, "goods units", "Gütereinheiten"), L(lang, "Production minus exports plus imports.", "Produktion minus Exporte plus Importe.")],
                    ["Sat", "0..100%", L(lang, "Need covered by final supply.", "Bedarf, der durch Endversorgung gedeckt wird.")],
                    ["Price", "VE/unit", L(lang, "Number of equal vector-Euro units per goods unit.", "Anzahl gleich langer Vektor-Euro-Einheiten pro Gütereinheit.")],
                    ["Buyθ/Sellθ", L(lang, "degrees", "Grad"), L(lang, "Buy and sell action angles.", "Kauf- und Verkaufs-Handlungswinkel.")],
                    ["BC/SC", L(lang, "currency code", "Währungscode"), L(lang, "Best currency for buy/sell angle.", "Beste Währung für Kauf-/Verkaufswinkel.")],
                    ["ODE", L(lang, "degrees", "Grad"), L(lang, "Average orthogonal deviation of good/evil versus popular/unpopular axes.", "Mittlere Orthogonalitätsabweichung der Gut/Böse- zur Beliebt/Unbeliebt-Achse.")],
                ],
            },
            "trade": {
                "why": L(lang,
                    "This part simulates the trade triangle between three countries. Trade is possible when the exporter's sell angle and the importer's buy angle can form a joint action direction. The simulated question is: how much angular work is needed to move goods without changing the equal Euro-vector length?",
                    "Dieser Teil simuliert das Handelsdreieck zwischen drei Ländern. Handel wird möglich, wenn Verkaufswinkel des Exportlandes und Kaufwinkel des Importlandes eine gemeinsame Handlungsrichtung bilden können. Simuliert wird: Wie viel Umlenkungsarbeit ist nötig, um Güter zu bewegen, ohne die gleiche Euro-Vektorlänge zu verändern?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["Route", L(lang, "country→country", "Land→Land"), L(lang, "Exporter to importer.", "Exportland zu Importland.")],
                    ["Q", L(lang, "goods units", "Gütereinheiten"), L(lang, "Traded quantity.", "Gehandelte Menge.")],
                    ["C", L(lang, "currency code", "Währungscode"), L(lang, "Currency angle used by the joint trade action.", "Währungswinkel, der von der gemeinsamen Handelshandlung genutzt wird.")],
                    ["Jointθ", L(lang, "degrees", "Grad"), L(lang, "Mean action angle between exporter sell angle and importer buy angle.", "Mittlerer Handlungswinkel aus Verkaufswinkel des Exporteurs und Kaufwinkel des Importeurs.")],
                    ["WK°", L(lang, "degrees", "Grad"), L(lang, "Angle distance between exporter's home currency and trade currency.", "Winkelabstand zwischen Heimatwährung des Exporteurs und Handelswährung.")],
                    ["UA", "rad·VE", L(lang, "Angular work: vector-Euro amount multiplied by rotation in radians.", "Umlenkungsarbeit: Vektor-Euro-Menge mal Drehung in Radiant.")],
                ],
            },
            "indices": {
                "why": L(lang,
                    "This part simulates the goal system. The economy does not maximize wealth. It tracks well-being, power, economic strength and tension. The simulated question is: who gains power, who gains well-being, and where does the economy weaken because angles do not cohere?",
                    "Dieser Teil simuliert das Zielsystem. Die Wirtschaft maximiert nicht Reichtum. Sie verfolgt Wohlbefinden, Macht, Wirtschaftsstärke und Spannung. Simuliert wird: Wer gewinnt Macht, wer gewinnt Wohlbefinden, und wo wird die Wirtschaft durch fehlenden Winkelzusammenhalt schwächer?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["WBI", "0..100", L(lang, "Well-being index of the population.", "Wohlbefindenindex der Bevölkerung.")],
                    ["MPI", "0..100", L(lang, "Power index of government/currency attachment.", "Machtindex der Bindung von Regierung und Währung.")],
                    ["ES", "0..100", L(lang, "Economic strength under angular competition.", "Wirtschaftsstärke unter Winkelkonkurrenz.")],
                    ["TD", "0..100", L(lang, "Tension degree. Lower is calmer.", "Spannungsgrad. Niedriger ist ruhiger.")],
                    ["OwnS", "0..100%", L(lang, "Domestic share of the home vector currency.", "Inlandsanteil der eigenen Vektorwährung.")],
                    ["DomC", L(lang, "currency code", "Währungscode"), L(lang, "Dominant currency in local transaction flow.", "Dominante Währung im lokalen Transaktionsfluss.")],
                ],
            },
            "drift": {
                "why": L(lang,
                    "This part simulates angle drift. Governments, populations and currencies do not stay frozen. They rotate slowly toward successful, powerful or livable actions. The simulated question is: which directions become habits, and which directions drift away?",
                    "Dieser Teil simuliert Winkeldrift. Regierungen, Bevölkerungen und Währungen bleiben nicht eingefroren. Sie drehen sich langsam zu erfolgreichen, machtvollen oder lebbaren Handlungen. Simuliert wird: Welche Richtungen werden Gewohnheit, und welche Richtungen driften weg?"),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["Targetθ", L(lang, "degrees", "Grad"), L(lang, "Direction toward which a currency is slowly rotating.", "Richtung, zu der sich eine Währung langsam dreht.")],
                    ["ΔStart", L(lang, "degrees", "Grad"), L(lang, "Distance between current currency angle and its initial angle.", "Abstand zwischen aktuellem Währungswinkel und Anfangswinkel.")],
                    ["GBW°", L(lang, "degrees", "Grad"), L(lang, "Government good/evil angle: direction of the good pole.", "Gut/Böse-Winkel der Regierung: Richtung des Gut-Pols.")],
                    ["BUW°", L(lang, "degrees", "Grad"), L(lang, "Population popular/unpopular angle: direction of the popular pole.", "Beliebt/Unbeliebt-Winkel der Bevölkerung: Richtung des Beliebt-Pols.")],
                    ["ODE", L(lang, "degrees", "Grad"), L(lang, "Deviation from ideal 90° orthogonality between the axes.", "Abweichung von idealer 90°-Orthogonalität der Achsen.")],
                ],
            },
            "final": {
                "why": L(lang,
                    "This final part reads the whole run. It compares final indices and sparks through time. It explains the result in terms of power, well-being and angular weakness, not in terms of being rich or poor.",
                    "Dieser Abschlussteil liest den ganzen Lauf. Er vergleicht Endindizes und Verlaufssparks. Er erklärt das Ergebnis über Macht, Wohlbefinden und Winkelschwäche, nicht über reich oder arm."),
                "headers": [L(lang, "Code", "Kürzel"), L(lang, "Unit", "Einheit"), L(lang, "Meaning only in this part", "Bedeutung nur in diesem Teil")],
                "rows": [
                    ["spark", L(lang, "UTF-8 mini chart", "UTF-8-Minikurve"), L(lang, "Tiny history line from low ▁ to high █.", "Kleine Verlaufslinie von niedrig ▁ bis hoch █.")],
                    ["OwnS last", "0..100%", L(lang, "Home vector currency share in the final tick.", "Anteil der eigenen Vektorwährung im letzten Tick.")],
                    ["Avg", L(lang, "arithmetic mean", "arithmetischer Mittelwert"), L(lang, "Average across three countries or full scenario run.", "Durchschnitt über drei Länder oder den ganzen Szenariolauf.")],
                ],
            },
        }

    # ------------------------------------------------------------------
    # Reports
    # ------------------------------------------------------------------

    def print_tick_report(self, t: int) -> None:
        section(L(self.lang, f"TICK {t}: one simulated period", f"TICK {t}: ein simulierter Zeitabschnitt"), Ansi.BRIGHT_MAGENTA)
        print(wrap(L(self.lang,
            "A tick can be read as a month, a quarter, or a political-market cycle. The order is: currency ring, labor/production, goods/prices, trade triangle, indices, then angle drift and events.",
            "Ein Tick kann als Monat, Quartal oder politischer Marktzyklus gelesen werden. Die Reihenfolge ist: Währungsring, Arbeit/Produktion, Güter/Preise, Handelsdreieck, Indizes, danach Winkeldrift und Ereignisse.")))
        self.print_currency_ring()
        self.print_labor_report()
        self.print_goods_report()
        self.print_trade_summary()
        self.print_country_indices()
        self.print_drift_and_events()

    def print_currency_ring(self) -> None:
        small_section(L(self.lang, "A) Currency ring: three equally long Euro vectors", "A) Währungsring: drei gleich lange Euro-Vektoren"), Ansi.BRIGHT_CYAN)
        self.explain_part("currency")
        rows = []
        row_colors = []
        for cur in self.currencies.values():
            rows.append([
                cur.code,
                cur.name(self.lang),
                cur.home,
                f"{cur.length:.3f} VE",
                angle_label(cur.angle),
                f"{cur.share*100:5.1f}%",
                f"{cur.power:5.1f}",
                angle_label(cur.last_target),
            ])
            row_colors.append(cur.color)
        print(table([L(self.lang, "Code", "Kürzel"), L(self.lang, "Name", "Name"), L(self.lang, "Home", "Heimat"), "|€⃗|", "θ°", L(self.lang, "Share", "Anteil"), L(self.lang, "Power", "Macht"), L(self.lang, "Targetθ", "Zielθ")], rows, row_colors))
        pairs = []
        codes = list(self.currencies.keys())
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                a = self.currencies[codes[i]]
                b = self.currencies[codes[j]]
                pairs.append([f"{a.code}↔{b.code}", f"{angle_distance(a.angle, b.angle):6.1f}°", f"{klang(a.angle, b.angle):.3f}"])
        print(table([L(self.lang, "Pair", "Paar"), "WK°", "KLG"], pairs))

    def sectors_for_detail(self, c: Country) -> List[Sector]:
        if self.detail == "short":
            scored = []
            for s in self.sectors:
                score = (1.0 - c.satisfaction.get(s.code, 0.0)) * 1.5 + c.prices.get(s.code, s.base_price) / max(0.01, s.base_price) * 0.25
                scored.append((score, s))
            return [s for _, s in sorted(scored, key=lambda x: x[0], reverse=True)[:4]]
        if self.detail == "medium":
            return [s for s in self.sectors if s.code in {"FOO", "ENE", "HOU", "HEA", "DAT", "CUL"}]
        return self.sectors

    def print_labor_report(self) -> None:
        small_section(L(self.lang, "B) Labor market and production", "B) Arbeitsmarkt und Produktion"), Ansi.BRIGHT_CYAN)
        self.explain_part("labor")
        for c in self.countries.values():
            print()
            print(col(f"{c.code} — {c.name}", c.color + Ansi.BOLD if COLOR_ON else ""))
            rows = []
            row_colors = []
            for sec in self.sectors_for_detail(c):
                st = c.angles[("WORK", sec.code)]
                rows.append([
                    sec.code,
                    sec.name(self.lang),
                    angle_label(st.last_hw),
                    st.last_currency,
                    f"{st.last_klang:.3f}",
                    f"{c.labor_hours[sec.code]:.2f} h",
                    f"{c.production[sec.code]:.2f}",
                    f"{c.fatigue:5.1f}",
                ])
                row_colors.append(sec.color)
            print(table([L(self.lang, "Sec", "Sek"), L(self.lang, "Name", "Name"), "Workθ", "WC", "KLG", "h", "Prod", "FTD"], rows, row_colors))

    def print_goods_report(self) -> None:
        small_section(L(self.lang, "C) Goods market and vector-Euro prices", "C) Gütermarkt und Vektor-Euro-Preise"), Ansi.BRIGHT_CYAN)
        self.explain_part("goods")
        for c in self.countries.values():
            print()
            print(col(f"{c.code} — {c.name}", c.color + Ansi.BOLD if COLOR_ON else ""))
            rows = []
            row_colors = []
            for sec in self.sectors_for_detail(c):
                buy = c.angles[("BUY", sec.code)]
                sell = c.angles[("SELL", sec.code)]
                work = c.angles[("WORK", sec.code)]
                oea = (buy.orth_error() + sell.orth_error() + work.orth_error()) / 3.0
                rows.append([
                    sec.code,
                    sec.name(self.lang),
                    f"{c.demand[sec.code]:.2f}",
                    f"{c.supply[sec.code]:.2f}",
                    f"{c.satisfaction[sec.code]*100:5.1f}%",
                    f"{c.prices[sec.code]:.2f} VE",
                    angle_label(buy.last_hw), buy.last_currency,
                    angle_label(sell.last_hw), sell.last_currency,
                    f"{oea:5.1f}°",
                ])
                row_colors.append(sec.color)
            print(table([L(self.lang, "Sec", "Sek"), L(self.lang, "Name", "Name"), L(self.lang, "Need", "Bedarf"), L(self.lang, "Supply", "Versorgung"), L(self.lang, "Sat", "Deckung"), L(self.lang, "Price", "Preis"), "Buyθ", "BC", "Sellθ", "SC", "ODE"], rows, row_colors))

    def print_trade_summary(self) -> None:
        small_section(L(self.lang, "D) Trade triangle and angular work", "D) Handelsdreieck und Umlenkungsarbeit"), Ansi.BRIGHT_CYAN)
        self.explain_part("trade")
        trades = [tr for tr in self.trade_history if tr.tick == self.t]
        if not trades:
            print(wrap(L(self.lang,
                "No relevant triangle trade emerged in this tick. That can happen when exportability is low or angles are too far apart.",
                "In diesem Tick entstand kein nennenswerter Dreieckshandel. Das kann passieren, wenn Exportfähigkeit niedrig ist oder Winkel zu weit auseinanderliegen.")))
            return
        max_rows = 12 if self.detail != "full" else 30
        rows = []
        for tr in trades[:max_rows]:
            rows.append([
                tr.exporter + "→" + tr.importer,
                tr.sector,
                f"{tr.amount:.3f}",
                tr.currency,
                angle_label(tr.joint_hw),
                f"{tr.wk_deg:5.1f}°",
                f"{tr.angular_work:.3f} rad·VE",
            ])
        print(table(["Route", L(self.lang, "Sec", "Sek"), "Q", "C", "Jointθ", "WK°", "UA"], rows))
        total_ua = sum(tr.angular_work for tr in trades)
        total_amount = sum(tr.amount for tr in trades)
        print(wrap(L(self.lang,
            f"Trade sum: {total_amount:.3f} goods units; angular work sum: {total_ua:.3f} rad·VE. High UA means trade remains possible, but it needs more symbolic and institutional rotation.",
            f"Handelssumme: {total_amount:.3f} Gütereinheiten; Summe Umlenkungsarbeit: {total_ua:.3f} rad·VE. Hohe UA bedeutet: Handel bleibt möglich, benötigt aber mehr symbolische und institutionelle Drehung.")))

    def print_country_indices(self) -> None:
        small_section(L(self.lang, "E) Power, well-being and economic strength", "E) Macht, Wohlbefinden und Wirtschaftsstärke"), Ansi.BRIGHT_CYAN)
        self.explain_part("indices")
        rows = []
        colors = []
        for c in self.countries.values():
            dominant = max(c.last_currency_mix, key=lambda k: c.last_currency_mix[k]) if c.last_currency_mix else "-"
            eig = c.last_currency_mix.get(c.currency, 0.0) * 100.0
            rows.append([
                c.code,
                c.name,
                gauge(c.wbi),
                gauge(c.mpi),
                gauge(c.wsk),
                tension_gauge(c.spg),
                f"{eig:5.1f}%",
                dominant,
                f"{sum(c.production.values()):.2f}",
                f"{sum(c.imports.values()):.2f}/{sum(c.exports.values()):.2f}",
            ])
            colors.append(c.color)
        print(table([L(self.lang, "Country", "Land"), L(self.lang, "Name", "Name"), "WBI", "MPI", "ES", "TD", "OwnS", "DomC", "Prod", "Imp/Exp"], rows, colors))

    def print_drift_and_events(self) -> None:
        small_section(L(self.lang, "F) Angle drift and event notes", "F) Winkeldrift und Ereignisnotizen"), Ansi.BRIGHT_CYAN)
        self.explain_part("drift")
        rows = []
        colors = []
        for cur in self.currencies.values():
            rows.append([
                cur.code,
                angle_label(cur.start_angle),
                angle_label(cur.angle),
                angle_label(cur.last_target),
                f"{angle_distance(cur.start_angle, cur.angle):5.1f}°",
                f"{cur.length:.3f} VE",
            ])
            colors.append(cur.color)
        print(table(["C", "Startθ", L(self.lang, "Nowθ", "Jetztθ"), L(self.lang, "Targetθ", "Zielθ"), "ΔStart", "|€⃗|"], rows, colors))
        any_note = False
        for c in self.countries.values():
            if c.notes:
                any_note = True
                print(col(c.code + ": ", c.color + Ansi.BOLD if COLOR_ON else "") + "; ".join(c.notes))
        if not any_note:
            print(L(self.lang,
                    "No strong event note. The angular economy is comparatively calm in this tick.",
                    "Keine starke Ereignisnotiz. Die Winkelwirtschaft läuft in diesem Tick vergleichsweise ruhig."))

    def print_final_report(self) -> None:
        section(L(self.lang, "FINAL REPORT", "ABSCHLUSSBERICHT"), Ansi.BRIGHT_MAGENTA)
        self.explain_part("final")
        print(wrap(L(self.lang,
            "The final report does not ask which country became richest. It asks which vector currency gained power attachment, where well-being stayed livable, and where economic strength was weakened by angular tension.",
            "Der Abschlussbericht fragt nicht, welches Land am reichsten wurde. Er fragt, welche Vektorwährung Machtbindung gewann, wo Wohlbefinden lebbar blieb und wo Wirtschaftsstärke durch Winkelspannung geschwächt wurde.")))
        rows = []
        colors = []
        for c in self.countries.values():
            hist = [r for r in self.history if r["country"] == c.code]
            wbi_values = [float(r["WBI"]) for r in hist]
            mpi_values = [float(r["MPI"]) for r in hist]
            es_values = [float(r["ES"]) for r in hist]
            td_values = [float(r["TD"]) for r in hist]
            rows.append([
                c.code,
                c.name,
                f"{c.wbi:5.1f} {spark(wbi_values, 0, 100)}",
                f"{c.mpi:5.1f} {spark(mpi_values, 0, 100)}",
                f"{c.wsk:5.1f} {spark(es_values, 0, 100)}",
                f"{c.spg:5.1f} {spark(td_values, 0, 100)}",
                f"{c.last_currency_mix.get(c.currency, 0)*100:5.1f}%",
            ])
            colors.append(c.color)
        print(table([L(self.lang, "Country", "Land"), L(self.lang, "Name", "Name"), "WBI", "MPI", "ES", "TD", L(self.lang, "OwnS last", "OwnS zuletzt")], rows, colors))
        print()
        cur_rows = []
        cur_colors = []
        for cur in self.currencies.values():
            cur_rows.append([
                cur.code, cur.name(self.lang), cur.home,
                f"{cur.length:.3f} VE",
                angle_label(cur.angle),
                f"{cur.share*100:5.1f}%",
                f"{cur.power:5.1f}",
            ])
            cur_colors.append(cur.color)
        print(table([L(self.lang, "Currency", "Währung"), L(self.lang, "Name", "Name"), L(self.lang, "Home", "Heimat"), L(self.lang, "Length", "Länge"), "Endθ", "Share", "Power"], cur_rows, cur_colors))
        print()
        print(wrap(self._final_interpretation()))

    def _final_interpretation(self) -> str:
        best_wbi = max(self.countries.values(), key=lambda c: c.wbi)
        best_mpi = max(self.countries.values(), key=lambda c: c.mpi)
        high_td = max(self.countries.values(), key=lambda c: c.spg)
        top_cur = max(self.currencies.values(), key=lambda cur: cur.power)
        return L(self.lang,
            f"Interpretation of this run: {best_wbi.code} has the strongest final well-being, {best_mpi.code} has the strongest power index, and {high_td.code} carries the highest tension degree. The strongest currency by power attachment is {top_cur.code}. Because every currency length remains exactly 1 VE, these differences are not caused by one Euro being longer than another Euro. They are caused by angular fit, angular drift, and how much market action each vector direction captures.",
            f"Interpretation dieses Laufs: {best_wbi.code} hat das stärkste End-Wohlbefinden, {best_mpi.code} den stärksten Machtindex, und {high_td.code} trägt den höchsten Spannungsgrad. Die stärkste Währung nach Machtbindung ist {top_cur.code}. Weil jede Währungslänge exakt 1 VE bleibt, entstehen diese Unterschiede nicht dadurch, dass ein Euro länger wäre als ein anderer Euro. Sie entstehen durch Winkelpassung, Winkeldrift und dadurch, wie viel Markthandlung jede Vektorrichtung bindet.")

    # ------------------------------------------------------------------
    # UTF-8 art gallery
    # ------------------------------------------------------------------

    def print_utf8_gallery(self) -> None:
        section(L(self.lang, "UTF-8 ART GALLERY OF THE ANGULAR ECONOMY", "UTF-8-ART-GALERIE DER WINKELWIRTSCHAFT"), Ansi.BRIGHT_MAGENTA)
        print(wrap(L(self.lang,
            "The gallery comes after the numerical report. It turns the same final state into colorful UTF-8 diagrams: circles, vectors, angle carpets, trade arrows and scenario maps. Each picture has a result summary underneath, including how the same picture should be read under different scenarios.",
            "Die Galerie kommt nach dem Zahlenbericht. Sie verwandelt denselben Endzustand in bunte UTF-8-Diagramme: Kreise, Vektoren, Winkelteppiche, Handelspfeile und Szenariokarten. Unter jedem Bild steht eine Ergebniszusammenfassung, inklusive Lesart für verschiedene Szenarien.")))
        scenario_rows = self._scenario_comparison() if self.compare_scenarios else []
        self.art_currency_compass(scenario_rows)
        self.art_equal_length_proof(scenario_rows)
        self.art_orthogonal_axes(scenario_rows)
        self.art_three_market_vectors(scenario_rows)
        self.art_power_wellbeing_map(scenario_rows)
        self.art_tension_heat_carpet(scenario_rows)
        self.art_trade_triangle(scenario_rows)
        self.art_currency_drift_trails(scenario_rows)
        self.art_sector_satisfaction_mosaic(scenario_rows)
        self.art_price_wave(scenario_rows)
        self.art_scenario_quadrants(scenario_rows)
        self.art_scenario_comparison_table(scenario_rows)

    def gallery_caption(self, no: int, title_en: str, title_de: str) -> None:
        print()
        print(col("╔" + "═" * (WRAP_WIDTH - 2) + "╗", Ansi.BRIGHT_MAGENTA))
        title = f"{no:02d}. " + L(self.lang, title_en, title_de)
        inside = "║ " + title + " " * max(0, WRAP_WIDTH - len(strip_ansi(title)) - 3) + "║"
        print(col(inside, Ansi.BRIGHT_MAGENTA + Ansi.BOLD if COLOR_ON else ""))
        print(col("╚" + "═" * (WRAP_WIDTH - 2) + "╝", Ansi.BRIGHT_MAGENTA))

    def _scenario_comparison(self) -> List[Dict[str, object]]:
        rows = []
        if not self.compare_scenarios:
            return rows
        # Keep scenario comparison silent and deterministic. Use the same tick count so that outputs are comparable.
        old_color = COLOR_ON
        old_width = WRAP_WIDTH
        for i, sc in enumerate(SCENARIOS):
            sim = AngularEconomy(seed=self.seed + 1000 + i * 31, ticks=self.max_ticks,
                                 detail="short", report_every=self.max_ticks, width=max(90, old_width),
                                 colors=False, explanations=False, lang=self.lang,
                                 scenario=sc, gallery=False, compare_scenarios=False)
            sim.simulate_silent()
            avg_wbi = sum(c.wbi for c in sim.countries.values()) / 3.0
            avg_mpi = sum(c.mpi for c in sim.countries.values()) / 3.0
            avg_es = sum(c.wsk for c in sim.countries.values()) / 3.0
            avg_td = sum(c.spg for c in sim.countries.values()) / 3.0
            total_ua = sum(tr.angular_work for tr in sim.trade_history)
            top_cur = max(sim.currencies.values(), key=lambda cur: cur.power).code
            rows.append({"scenario": sc, "WBI": avg_wbi, "MPI": avg_mpi, "ES": avg_es,
                         "TD": avg_td, "UA": total_ua, "top": top_cur})
        # Restore terminal settings of the main simulation.
        globals()["COLOR_ON"] = old_color
        globals()["WRAP_WIDTH"] = old_width
        return rows

    def scenario_sentence(self, scenario_rows: List[Dict[str, object]], focus: str) -> str:
        if not scenario_rows:
            return L(self.lang,
                "Scenario comparison was disabled, so the reading below refers only to the active run.",
                "Der Szenariovergleich wurde deaktiviert; die folgende Lesart bezieht sich nur auf den aktiven Lauf.")
        best_wbi = max(scenario_rows, key=lambda r: r["WBI"])
        best_mpi = max(scenario_rows, key=lambda r: r["MPI"])
        lowest_td = min(scenario_rows, key=lambda r: r["TD"])
        highest_td = max(scenario_rows, key=lambda r: r["TD"])
        return L(self.lang,
            f"Scenario reading for {focus}: in the silent comparison, {scenario_label(best_wbi['scenario'], self.lang)} has the highest average WBI, {scenario_label(best_mpi['scenario'], self.lang)} has the highest average MPI, {scenario_label(lowest_td['scenario'], self.lang)} has the calmest angle field, and {scenario_label(highest_td['scenario'], self.lang)} has the hardest tension field. Use this picture as a diagnostic: harmonious scenarios shrink visual conflict; power scenarios pull vectors toward state currency; scarcity or fragmentation thickens red/yellow tension signs.",
            f"Szenario-Lesart für {focus}: Im stillen Vergleich hat {scenario_label(best_wbi['scenario'], self.lang)} das höchste durchschnittliche WBI, {scenario_label(best_mpi['scenario'], self.lang)} das höchste durchschnittliche MPI, {scenario_label(lowest_td['scenario'], self.lang)} das ruhigste Winkelfeld, und {scenario_label(highest_td['scenario'], self.lang)} das härteste Spannungsfeld. Nutze dieses Bild als Diagnose: Harmonische Szenarien verkleinern sichtbare Konflikte; Machtszenarien ziehen Vektoren zur Staatswährung; Mangel oder Zersplitterung verdicken rote/gelbe Spannungszeichen.")

    def art_currency_compass(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(1, "Currency compass: three equal-length Euro vectors", "Währungskompass: drei gleich lange Euro-Vektoren")
        points = []
        for cur in self.currencies.values():
            label = f"{cur.code} |€⃗|=1"
            points.append((cur.angle, label, cur.color, angle_arrow(cur.angle)))
        print(compass_canvas(points, title=L(self.lang, "Final currency directions", "Endrichtungen der Währungen")))
        print(wrap(L(self.lang,
            "Result: the picture shows only direction, not monetary length. EA, EB and EC are drawn as different colored arrows because their angles differ; they are not drawn with different radii because their vector length is fixed at 1 VE. The winner of a transaction is therefore the vector whose direction best resonates with the action angle, not the vector with a longer Euro.",
            "Ergebnis: Das Bild zeigt nur Richtung, nicht Geldlänge. EA, EB und EC erscheinen als verschiedenfarbige Pfeile, weil ihre Winkel verschieden sind; sie erscheinen nicht mit unterschiedlichen Radien, weil ihre Vektorlänge fest bei 1 VE liegt. Eine Transaktion gewinnt also die Währung, deren Richtung am besten mit dem Handlungswinkel klingt, nicht die Währung mit einem längeren Euro.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "the currency compass", "den Währungskompass"))))

    def art_equal_length_proof(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(2, "Equal vector-length proof: price is count, not stretch", "Gleichlängenbeweis: Preis ist Anzahl, nicht Streckung")
        print(col("┌" + "─" * 72 + "┐", Ansi.BRIGHT_CYAN))
        for cur in self.currencies.values():
            bar = col("████████████████████", cur.color)
            print(col("│ ", Ansi.BRIGHT_CYAN) + f"{cur.code} {bar} |€⃗| = {cur.length:.3f} VE    θ={cur.angle:6.1f}°" + " " * 6 + col("│", Ansi.BRIGHT_CYAN))
        print(col("└" + "─" * 72 + "┘", Ansi.BRIGHT_CYAN))
        price_samples = []
        for c in self.countries.values():
            sec = max(self.sectors, key=lambda s: c.prices[s.code])
            price_samples.append([c.code, sec.code, sec.name(self.lang), f"{c.prices[sec.code]:.2f} VE/unit"])
        print(table([L(self.lang, "Country", "Land"), L(self.lang, "Sec", "Sek"), L(self.lang, "Sector", "Sektor"), L(self.lang, "Highest price", "Höchster Preis")], price_samples))
        print(wrap(L(self.lang,
            "Result: all three bars have identical length. The price table below the bars shows a different idea: high prices mean that more equal-length vector-Euro units are counted for a good. The price does not mean that EA, EB or EC has become longer. In scarcity scenarios the count usually rises; in resonance scenarios the count often falls because less angular detour is needed.",
            "Ergebnis: Alle drei Balken haben identische Länge. Die Preistabelle darunter zeigt eine andere Idee: Hohe Preise bedeuten, dass mehr gleich lange Vektor-Euro-Einheiten für ein Gut gezählt werden. Der Preis bedeutet nicht, dass EA, EB oder EC länger geworden wäre. In Mangelszenarien steigt diese Anzahl meist; in Resonanzszenarien fällt sie oft, weil weniger Winkelumweg nötig ist.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "equal vector length", "gleiche Vektorlänge"))))

    def _most_orthogonal_pressure(self) -> Tuple[Country, Sector, str, AngleState]:
        best = None
        best_score = -1.0
        for c in self.countries.values():
            for sec in self.sectors:
                for action in ACTIONS:
                    st = c.angles[(action, sec.code)]
                    score = st.orth_error() + 55.0 * gegenklang(st.last_hw if st.last_hw else st.action_angle(), self.currencies[c.currency].angle)
                    if score > best_score:
                        best_score = score
                        best = (c, sec, action, st)
        return best  # type: ignore

    def art_orthogonal_axes(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(3, "Government good/evil axis and population popular/unpopular axis", "Regierungsachse Gut/Böse und Bevölkerungsachse Beliebt/Unbeliebt")
        c, sec, action, st = self._most_orthogonal_pressure()
        hw = st.last_hw if st.last_hw else st.action_angle()
        points = [
            (st.gbw, "GOOD/GT", Ansi.BRIGHT_GREEN, "G"),
            (st.gbw + 180, "EVIL/BÖ", Ansi.BRIGHT_RED, "E"),
            (st.buw, "POPULAR/BEL", Ansi.BRIGHT_CYAN, "P"),
            (st.buw + 180, "UNPOPULAR/UNB", Ansi.BRIGHT_MAGENTA, "U"),
            (hw, "ACTION/HW", Ansi.BRIGHT_YELLOW, "◆"),
        ]
        print(compass_canvas(points, title=f"{c.code} {sec.code} {action_label(action, self.lang)}"))
        print(wrap(L(self.lang,
            f"Result: this is the strongest axis-pressure example found in the final state: {c.code}, sector {sec.name(self.lang)}, {action_label(action, self.lang)}. GBW° points to the government good pole; GBW°+180° is the evil pole. BUW° points to the population popular pole; BUW°+180° is the unpopular pole. The action angle lies between the axes. ODE here is {st.orth_error():.1f}°, so the popular/unpopular axis is that far away from ideal orthogonality.",
            f"Ergebnis: Dies ist das stärkste Achsendruck-Beispiel im Endzustand: {c.code}, Sektor {sec.name(self.lang)}, {action_label(action, self.lang)}. GBW° zeigt zum Gut-Pol der Regierung; GBW°+180° ist der Böse-Pol. BUW° zeigt zum Beliebt-Pol der Bevölkerung; BUW°+180° ist der Unbeliebt-Pol. Der Handlungswinkel liegt zwischen den Achsen. Die ODE beträgt hier {st.orth_error():.1f}°, also ist die Beliebt/Unbeliebt-Achse so weit von idealer Orthogonalität entfernt.")))
        print(wrap(L(self.lang,
            "Scenario meaning: resonance keeps the cyan popular axis close to a clean 90° relation with the green good axis; power pursuit often pulls the yellow action toward the government/currency side; well-being pursuit pulls action toward the popular side; fragmented angles scatter all poles and create high tension even when the Euro-vector length is unchanged.",
            "Szenario-Bedeutung: Resonanz hält die türkise Beliebt-Achse nahe an einer sauberen 90°-Beziehung zur grünen Gut-Achse; Machtstreben zieht die gelbe Handlung oft zur Regierungs-/Währungsseite; Wohlbefinden zieht Handlung zur Beliebt-Seite; zersplitterte Winkel streuen alle Pole und erzeugen hohe Spannung, obwohl die Euro-Vektorlänge unverändert bleibt.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "orthogonal axes", "orthogonale Achsen"))))

    def art_three_market_vectors(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(4, "Three market vectors: buy, sell and labor", "Drei Marktvektoren: Kauf, Verkauf und Arbeit")
        # Choose country/sector with lowest satisfaction for diagnostic value.
        c = max(self.countries.values(), key=lambda x: x.spg)
        sec = min(self.sectors, key=lambda s: c.satisfaction[s.code])
        points = []
        colors = {"BUY": Ansi.BRIGHT_GREEN, "SELL": Ansi.BRIGHT_BLUE, "WORK": Ansi.BRIGHT_MAGENTA}
        labels_short = {"BUY": "BUY/K", "SELL": "SELL/V", "WORK": "WORK/A"}
        for action in ACTIONS:
            st = c.angles[(action, sec.code)]
            hw = st.last_hw if st.last_hw else st.action_angle()
            points.append((hw, f"{labels_short[action]} {st.last_currency}", colors[action], "◆"))
        print(compass_canvas(points, title=f"{c.code} {sec.name(self.lang)}"))
        print(wrap(L(self.lang,
            f"Result: the three market actions in {c.code}/{sec.name(self.lang)} do not have to point in the same direction. Buy, sell and labor can use different dominant currencies because each action has its own angle. In the shown final state, need satisfaction in this sector is {c.satisfaction[sec.code]*100:.1f}% and the price is {c.prices[sec.code]:.2f} VE per unit. A weak sector is therefore not simply 'poor'; it can be angularly split between buying, selling and working.",
            f"Ergebnis: Die drei Markthandlungen in {c.code}/{sec.name(self.lang)} müssen nicht in dieselbe Richtung zeigen. Kauf, Verkauf und Arbeit können unterschiedliche dominante Währungen nutzen, weil jede Handlung ihren eigenen Winkel hat. Im gezeigten Endzustand beträgt die Bedarfsdeckung dieses Sektors {c.satisfaction[sec.code]*100:.1f}% und der Preis {c.prices[sec.code]:.2f} VE pro Einheit. Ein schwacher Sektor ist deshalb nicht einfach 'arm'; er kann winkelmäßig zwischen Kaufen, Verkaufen und Arbeiten gespalten sein.")))
        print(wrap(L(self.lang,
            "Scenario meaning: in resonance, the three diamonds cluster and the sector feels coherent; in power pursuit, the work vector may be forced near the state-currency orbit while buy demand remains elsewhere; in scarcity, buy vectors become expensive because need and supply collide; in trade boom, sell vectors become more important and can pull the sector toward export currencies.",
            "Szenario-Bedeutung: In Resonanz clustern die drei Rauten und der Sektor wirkt kohärent; im Machtstreben kann der Arbeitsvektor nahe an die Staatswährung gezogen werden, während Kaufbedarf woanders bleibt; im Mangel werden Kaufvektoren teuer, weil Bedarf und Versorgung kollidieren; im Handelsboom werden Verkaufsvektoren wichtiger und können den Sektor zu Exportwährungen ziehen.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "the three market vectors", "die drei Marktvektoren"))))

    def art_power_wellbeing_map(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(5, "Power versus well-being map", "Macht-gegen-Wohlbefinden-Karte")
        w, h = 64, 22
        canvas = Canvas(w, h)
        x0, y0 = 8, h - 4
        x1, y1 = w - 4, 2
        # Axes
        for x in range(x0, x1 + 1):
            canvas.put(x, y0, "─", Ansi.DIM)
        for y in range(y1, y0 + 1):
            canvas.put(x0, y, "│", Ansi.DIM)
        canvas.put(x0, y0, "└", Ansi.WHITE)
        canvas.put_text(x0 + 2, y0 + 1, "WBI →", Ansi.BRIGHT_GREEN)
        canvas.put_text(1, y1 - 1, "MPI ↑", Ansi.BRIGHT_BLUE)
        # Quadrant labels
        canvas.put_text(x0 + 2, y1 + 1, L(self.lang, "power", "Macht"), Ansi.BRIGHT_BLUE)
        canvas.put_text(x1 - 18, y1 + 1, L(self.lang, "resonance", "Resonanz"), Ansi.BRIGHT_GREEN)
        canvas.put_text(x0 + 2, y0 - 2, L(self.lang, "weak", "schwach"), Ansi.BRIGHT_RED)
        canvas.put_text(x1 - 22, y0 - 2, L(self.lang, "well-being", "Wohlbefinden"), Ansi.BRIGHT_CYAN)
        for c in self.countries.values():
            x = int(round(x0 + (x1 - x0) * clamp(c.wbi / 100.0, 0, 1)))
            y = int(round(y0 - (y0 - y1) * clamp(c.mpi / 100.0, 0, 1)))
            canvas.put(x, y, "●", c.color + Ansi.BOLD if COLOR_ON else "")
            canvas.put_text(min(w - 5, x + 2), y, c.code, c.color + Ansi.BOLD if COLOR_ON else "")
        print(canvas.render())
        print(wrap(L(self.lang,
            "Result: this diagram separates the two main goals. Moving right means higher well-being; moving upward means stronger power attachment. A country in the upper right is not necessarily rich; it is coherent in both goal dimensions. Upper left means power without enough well-being. Lower right means livable society with weak state/currency power. Lower left means weak coherence in both dimensions.",
            "Ergebnis: Dieses Diagramm trennt die zwei Hauptziele. Nach rechts bedeutet mehr Wohlbefinden; nach oben bedeutet stärkere Machtbindung. Ein Land rechts oben ist nicht unbedingt reich; es ist in beiden Zielrichtungen kohärent. Links oben bedeutet Macht ohne genug Wohlbefinden. Rechts unten bedeutet lebbares Gemeinwesen mit schwacher Staats-/Währungsmacht. Links unten bedeutet schwachen Zusammenhalt in beiden Dimensionen.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "power versus well-being", "Macht gegen Wohlbefinden"))))

    def art_tension_heat_carpet(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(6, "Tension heat carpet through time", "Spannungs-Heatcarpet über die Zeit")
        print(col(L(self.lang, "Legend: green low TD, yellow medium TD, red high TD", "Legende: Grün niedrige TD, Gelb mittlere TD, Rot hohe TD"), Ansi.BOLD))
        rows = []
        for c in self.countries.values():
            vals = [float(r["TD"]) for r in self.history if r["country"] == c.code]
            carpet = "".join(heat_block(v, 0, 100) for v in vals)
            rows.append([col(c.code, c.color + Ansi.BOLD if COLOR_ON else ""), carpet, f"last {c.spg:.1f}"])
        print(table([L(self.lang, "Country", "Land"), L(self.lang, "TD over ticks", "TD über Ticks"), L(self.lang, "Final", "Final")], rows))
        print(wrap(L(self.lang,
            "Result: the carpet shows whether tension is episodic or structural. A few yellow/red blocks mean temporary angular friction. A long red band means persistent mismatch between government good/evil axes, population popular/unpopular axes, currency directions and market actions. This directly weakens economic strength in the model.",
            "Ergebnis: Der Teppich zeigt, ob Spannung episodisch oder strukturell ist. Einzelne gelbe/rote Blöcke bedeuten vorübergehende Winkelreibung. Ein langes rotes Band bedeutet dauerhafte Fehlpassung zwischen Gut/Böse-Achsen der Regierung, Beliebt/Unbeliebt-Achsen der Bevölkerung, Währungsrichtungen und Markthandlungen. Das schwächt im Modell direkt die Wirtschaftsstärke.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "the tension carpet", "den Spannungsteppich"))))

    def art_trade_triangle(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(7, "Trade triangle: goods move, vectors rotate", "Handelsdreieck: Güter bewegen sich, Vektoren drehen")
        # Aggregate flows by route.
        flows: Dict[Tuple[str, str], float] = {}
        uas: Dict[Tuple[str, str], float] = {}
        for tr in self.trade_history:
            key = (tr.exporter, tr.importer)
            flows[key] = flows.get(key, 0.0) + tr.amount
            uas[key] = uas.get(key, 0.0) + tr.angular_work
        def arrow(a: str, b: str) -> str:
            q = flows.get((a, b), 0.0)
            ua = uas.get((a, b), 0.0)
            n = int(clamp(q * 5.0, 1, 12)) if q > 0 else 1
            color = Ansi.BRIGHT_GREEN if ua < 1.5 else (Ansi.BRIGHT_YELLOW if ua < 4.0 else Ansi.BRIGHT_RED)
            return col("═" * n + "▶", color) + f" {q:.2f}/{ua:.2f}UA"
        print("\n" + " " * 29 + col("▲ AUR", self.countries["AUR"].color + Ansi.BOLD if COLOR_ON else ""))
        print(" " * 24 + "╱" + " " * 12 + "╲")
        print(" " * 18 + arrow("BEL", "AUR") + " " * 6 + arrow("AUR", "CAL"))
        print(" " * 16 + "╱" + " " * 28 + "╲")
        print(col("BEL ◀", self.countries["BEL"].color + Ansi.BOLD if COLOR_ON else "") + " " * 16 + arrow("BEL", "CAL") + " " * 9 + col("▶ CAL", self.countries["CAL"].color + Ansi.BOLD if COLOR_ON else ""))
        print(" " * 16 + "╲" + " " * 28 + "╱")
        print(" " * 18 + arrow("AUR", "BEL") + " " * 6 + arrow("CAL", "AUR"))
        print(" " * 24 + "╲" + " " * 12 + "╱")
        print(" " * 29 + arrow("CAL", "BEL"))
        print(wrap(L(self.lang,
            "Result: each arrow lists quantity/angular work. The first number is traded goods quantity; the second is UA, the angular work in rad·VE. A route can have a modest goods flow but high angular work when the trade currency is far from the exporter's home vector. That route is politically and symbolically expensive even though every Euro-vector still has length 1.",
            "Ergebnis: Jeder Pfeil zeigt Menge/Umlenkungsarbeit. Die erste Zahl ist gehandelte Gütermenge; die zweite ist UA, die Umlenkungsarbeit in rad·VE. Eine Route kann geringe Gütermenge, aber hohe Umlenkungsarbeit haben, wenn die Handelswährung weit von der Heimatwährung des Exporteurs entfernt ist. Diese Route ist politisch und symbolisch teuer, obwohl jeder Euro-Vektor weiterhin Länge 1 hat.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "the trade triangle", "das Handelsdreieck"))))

    def art_currency_drift_trails(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(8, "Currency drift trails", "Währungsdrift-Spuren")
        points = []
        # Draw final arrows plus small trail points from history.
        for cur in self.currencies.values():
            points.append((cur.angle, f"{cur.code} now", cur.color, angle_arrow(cur.angle)))
        print(compass_canvas(points, title=L(self.lang, "Final arrows; trails listed below", "Endpfeile; Spuren darunter")))
        trail_rows = []
        for cur in self.currencies.values():
            vals = [float(r[f"{cur.code}_angle"]) for r in self.currency_history]
            # Create a compact symbolic drift line: arrow char by angle per tick.
            trail = "".join(col(angle_arrow(v), cur.color) for v in vals)
            trail_rows.append([cur.code, angle_label(cur.start_angle), angle_label(cur.angle), f"{angle_distance(cur.start_angle, cur.angle):.1f}°", trail])
        print(table(["C", "Startθ", "Endθ", "Δ", L(self.lang, "trail", "Spur")], trail_rows))
        print(wrap(L(self.lang,
            "Result: the trail is a history of direction changes, not of monetary length changes. A stable trail means the currency kept its angle identity. A turning trail means market action and government attachment pulled it into a new orbit. In power scenarios drift can be strategic; in well-being scenarios it can follow livable demand; in fragmented scenarios it can become unstable zigzagging.",
            "Ergebnis: Die Spur ist ein Verlauf der Richtungsänderungen, nicht der Geldlängenänderungen. Eine stabile Spur bedeutet, dass die Währung ihre Winkelidentität hält. Eine drehende Spur bedeutet, dass Markthandlung und Regierungsbindung sie in einen neuen Orbit gezogen haben. In Machtszenarien kann Drift strategisch sein; in Wohlbefindensszenarien folgt sie lebbarer Nachfrage; in zersplitterten Szenarien kann sie instabiles Zickzack werden.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "currency drift", "Währungsdrift"))))

    def art_sector_satisfaction_mosaic(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(9, "Sector satisfaction mosaic", "Sektor-Deckungs-Mosaik")
        headers = [L(self.lang, "Country", "Land")] + [s.code for s in self.sectors]
        rows = []
        for c in self.countries.values():
            row = [col(c.code, c.color + Ansi.BOLD if COLOR_ON else "")]
            for s in self.sectors:
                sat = c.satisfaction[s.code]
                if sat >= 0.95:
                    cell = col("██", Ansi.BRIGHT_GREEN)
                elif sat >= 0.75:
                    cell = col("▓▓", Ansi.BRIGHT_YELLOW)
                elif sat >= 0.55:
                    cell = col("▒▒", Ansi.YELLOW)
                else:
                    cell = col("░░", Ansi.BRIGHT_RED)
                row.append(cell + f" {sat*100:4.0f}%")
            rows.append(row)
        print(table(headers, rows))
        print(wrap(L(self.lang,
            "Result: the mosaic translates final need coverage into blocks. Green blocks mean that a sector is materially covered and angularly usable enough. Red blocks mean missing coverage, usually from low production, weak trade access, expensive vector count or mismatch between buy/sell/work angles. This is where economic strength weakens even without treating money as wealth maximization.",
            "Ergebnis: Das Mosaik übersetzt finale Bedarfsdeckung in Blöcke. Grüne Blöcke bedeuten, dass ein Sektor materiell gedeckt und winkelmäßig nutzbar genug ist. Rote Blöcke bedeuten fehlende Deckung, meist durch niedrige Produktion, schwachen Handelszugang, teure Vektoranzahl oder Fehlpassung zwischen Kauf-/Verkaufs-/Arbeitswinkeln. Hier wird Wirtschaftsstärke schwach, ohne Geld als Reichtumsmaximierung zu behandeln.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "sector satisfaction", "Sektordeckung"))))

    def art_price_wave(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(10, "Vector-Euro price waves", "Vektor-Euro-Preiswellen")
        for c in self.countries.values():
            vals = [c.prices[s.code] for s in self.sectors]
            lo, hi = min(vals), max(vals)
            wave = spark(vals, lo, hi)
            colored = "".join(col(ch, c.color) for ch in wave)
            labels = " ".join(s.code for s in self.sectors)
            print(col(c.code + " ", c.color + Ansi.BOLD if COLOR_ON else "") + colored + "   " + labels + f"   min={lo:.2f} max={hi:.2f} VE")
        print(wrap(L(self.lang,
            "Result: each wave is the final vector-Euro count per unit across sectors. Peaks are not longer Euros. They are places where more equal-length vector units are required because scarcity, angular mismatch, or local currency distance adds friction. In resonance scenarios waves flatten; in scarcity scenarios they rise; in trade-boom scenarios exportable sectors can either flatten through imports or spike through angular work.",
            "Ergebnis: Jede Welle ist die finale Vektor-Euro-Anzahl pro Einheit über die Sektoren. Spitzen sind keine längeren Euros. Sie sind Stellen, an denen mehr gleich lange Vektoreinheiten gebraucht werden, weil Mangel, Winkel-Fehlpassung oder Distanz zur lokalen Währung Reibung erzeugt. In Resonanzszenarien glätten sich Wellen; in Mangelszenarien steigen sie; in Handelsboom-Szenarien können exportierbare Sektoren durch Importe glatter werden oder durch Umlenkungsarbeit ausschlagen.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "price waves", "Preiswellen"))))

    def art_scenario_quadrants(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(11, "Scenario quadrants: how to classify the economy", "Szenario-Quadranten: wie die Wirtschaft einzuordnen ist")
        quadrants = {
            "resonance": [],
            "power_lock": [],
            "wellbeing_island": [],
            "fracture": [],
        }
        for c in self.countries.values():
            if c.wbi >= 60 and c.mpi >= 55 and c.spg < 50:
                quadrants["resonance"].append(c.code)
            elif c.mpi >= c.wbi + 8:
                quadrants["power_lock"].append(c.code)
            elif c.wbi >= c.mpi + 8:
                quadrants["wellbeing_island"].append(c.code)
            else:
                quadrants["fracture"].append(c.code)
        box_w = 30
        print(col("┌" + "─" * box_w + "┬" + "─" * box_w + "┐", Ansi.BRIGHT_CYAN))
        print(col("│", Ansi.BRIGHT_CYAN) + L(self.lang, " POWER LOCK ", " MACHTKLEMME ").center(box_w) + col("│", Ansi.BRIGHT_CYAN) + L(self.lang, " RESONANCE ", " RESONANZ ").center(box_w) + col("│", Ansi.BRIGHT_CYAN))
        print(col("│", Ansi.BRIGHT_CYAN) + (", ".join(quadrants["power_lock"]) or "—").center(box_w) + col("│", Ansi.BRIGHT_CYAN) + (", ".join(quadrants["resonance"]) or "—").center(box_w) + col("│", Ansi.BRIGHT_CYAN))
        print(col("├" + "─" * box_w + "┼" + "─" * box_w + "┤", Ansi.BRIGHT_CYAN))
        print(col("│", Ansi.BRIGHT_CYAN) + L(self.lang, " FRACTURE ", " BRUCH ").center(box_w) + col("│", Ansi.BRIGHT_CYAN) + L(self.lang, " WELL-BEING ISLAND ", " WOHLBEFINDENSINSEL ").center(box_w) + col("│", Ansi.BRIGHT_CYAN))
        print(col("│", Ansi.BRIGHT_CYAN) + (", ".join(quadrants["fracture"]) or "—").center(box_w) + col("│", Ansi.BRIGHT_CYAN) + (", ".join(quadrants["wellbeing_island"]) or "—").center(box_w) + col("│", Ansi.BRIGHT_CYAN))
        print(col("└" + "─" * box_w + "┴" + "─" * box_w + "┘", Ansi.BRIGHT_CYAN))
        print(wrap(L(self.lang,
            "Result: the quadrant picture gives a political-economic reading. Resonance means power and well-being can coexist with tolerable tension. Power lock means the state/currency side dominates over lived well-being. Well-being island means people live better than the state currency dominates. Fracture means the angles do not yet form a stable goal shape.",
            "Ergebnis: Das Quadrantenbild gibt eine politisch-ökonomische Lesart. Resonanz bedeutet, dass Macht und Wohlbefinden bei tragbarer Spannung zusammengehen. Machtklemme bedeutet, dass Staats-/Währungsseite über gelebtem Wohlbefinden dominiert. Wohlbefindensinsel bedeutet, dass Menschen besser leben, als die Staatswährung dominiert. Bruch bedeutet, dass die Winkel noch keine stabile Zielform bilden.")))
        print(wrap(self.scenario_sentence(scenario_rows, L(self.lang, "scenario quadrants", "Szenario-Quadranten"))))

    def art_scenario_comparison_table(self, scenario_rows: List[Dict[str, object]]) -> None:
        self.gallery_caption(12, "Silent scenario comparison", "Stiller Szenariovergleich")
        if not scenario_rows:
            print(L(self.lang, "Scenario comparison disabled.", "Szenariovergleich deaktiviert."))
            return
        rows = []
        colors = []
        for r in scenario_rows:
            label = scenario_label(str(r["scenario"]), self.lang)
            rows.append([
                label,
                f"{float(r['WBI']):5.1f}",
                f"{float(r['MPI']):5.1f}",
                f"{float(r['ES']):5.1f}",
                f"{float(r['TD']):5.1f}",
                f"{float(r['UA']):7.2f}",
                str(r["top"]),
            ])
            if str(r["scenario"]) == "resonance":
                colors.append(Ansi.BRIGHT_GREEN)
            elif str(r["scenario"]) in ("fragmented", "scarcity"):
                colors.append(Ansi.BRIGHT_RED)
            elif str(r["scenario"]) == "power":
                colors.append(Ansi.BRIGHT_BLUE)
            else:
                colors.append(Ansi.BRIGHT_CYAN)
        print(table([L(self.lang, "Scenario", "Szenario"), "Avg WBI", "Avg MPI", "Avg ES", "Avg TD", "Total UA", "Top C"], rows, colors))
        print(wrap(L(self.lang,
            "Result: this final table actually runs the model silently under several scenarios using the same structural rules. It is not a moral ranking. It shows which parameter climate produces more well-being, more power, more strength or more tension. Since all scenarios keep |€⃗|=1 VE for EA, EB and EC, differences across rows are angle-system differences, not Euro-length differences.",
            "Ergebnis: Diese letzte Tabelle lässt das Modell tatsächlich still unter mehreren Szenarien laufen, mit denselben Strukturregeln. Sie ist keine moralische Rangliste. Sie zeigt, welches Parameterklima mehr Wohlbefinden, mehr Macht, mehr Stärke oder mehr Spannung erzeugt. Da alle Szenarien |€⃗|=1 VE für EA, EB und EC beibehalten, sind Unterschiede zwischen den Zeilen Winkel-Systemunterschiede, keine Euro-Längenunterschiede.")))
        print(wrap(L(self.lang,
            "How to use it: choose --scenario resonance to see cleaner angular coherence, --scenario power to see stronger state/currency attachment, --scenario wellbeing to privilege livability, --scenario fragmented for scattered axes, --scenario scarcity for high needs and low production, or --scenario tradeboom for strong export/import motion.",
            "So nutzt du es: Wähle --scenario resonance für klareren Winkelzusammenhalt, --scenario power für stärkere Staats-/Währungsbindung, --scenario wellbeing für Vorrang des Lebbaren, --scenario fragmented für gestreute Achsen, --scenario scarcity für hohen Bedarf und niedrige Produktion oder --scenario tradeboom für starke Export-/Importbewegung.")))

    # ------------------------------------------------------------------
    # Exports
    # ------------------------------------------------------------------

    def export_csv(self, path: str) -> None:
        if not self.history:
            return
        fields = list(self.history[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in self.history:
                w.writerow(r)

    def export_currency_csv(self, path: str) -> None:
        if not self.currency_history:
            return
        fields = list(self.currency_history[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for r in self.currency_history:
                w.writerow(r)

    def export_markdown(self, path: str) -> None:
        lines = []
        if self.lang == "de":
            lines.append("# Abschlussbericht der Winkelwährungswirtschaft\n\n")
            lines.append(f"Szenario: `{scenario_label(self.scenario, self.lang)}`  \nSeed: `{self.seed}`  \nTicks: `{self.max_ticks}`  \n\n")
            lines.append("## Währungen\n\n")
            lines.append("| Währung | Heimat | Länge | Endwinkel | Anteil zuletzt | Macht |\n")
            lines.append("|---|---:|---:|---:|---:|---:|\n")
            for cur in self.currencies.values():
                lines.append(f"| {cur.code} {cur.name(self.lang)} | {cur.home} | {cur.length:.3f} VE | {cur.angle:.2f}° | {cur.share*100:.2f}% | {cur.power:.2f} |\n")
            lines.append("\n## Länder\n\n")
            lines.append("| Land | WBI | MPI | ES | TD | Eigene Währung zuletzt |\n")
            lines.append("|---|---:|---:|---:|---:|---:|\n")
            for c in self.countries.values():
                lines.append(f"| {c.code} {c.name} | {c.wbi:.2f} | {c.mpi:.2f} | {c.wsk:.2f} | {c.spg:.2f} | {c.last_currency_mix.get(c.currency, 0)*100:.2f}% |\n")
            lines.append("\nDie Simulation maximiert keinen Reichtum. Alle drei Währungen behalten dieselbe Vektorlänge von 1 VE; die Konkurrenz entsteht durch Winkel.\n")
        else:
            lines.append("# Angular Vector-Currency Economy Final Report\n\n")
            lines.append(f"Scenario: `{scenario_label(self.scenario, self.lang)}`  \nSeed: `{self.seed}`  \nTicks: `{self.max_ticks}`  \n\n")
            lines.append("## Currencies\n\n")
            lines.append("| Currency | Home | Length | End angle | Last share | Power |\n")
            lines.append("|---|---:|---:|---:|---:|---:|\n")
            for cur in self.currencies.values():
                lines.append(f"| {cur.code} {cur.name(self.lang)} | {cur.home} | {cur.length:.3f} VE | {cur.angle:.2f}° | {cur.share*100:.2f}% | {cur.power:.2f} |\n")
            lines.append("\n## Countries\n\n")
            lines.append("| Country | WBI | MPI | ES | TD | Home currency last |\n")
            lines.append("|---|---:|---:|---:|---:|---:|\n")
            for c in self.countries.values():
                lines.append(f"| {c.code} {c.name} | {c.wbi:.2f} | {c.mpi:.2f} | {c.wsk:.2f} | {c.spg:.2f} | {c.last_currency_mix.get(c.currency, 0)*100:.2f}% |\n")
            lines.append("\nThe simulation does not maximize wealth. All three currencies keep the same vector length of 1 VE; competition arises from angles.\n")
        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(lines))


# -----------------------------------------------------------------------------
# 7. CLI
# -----------------------------------------------------------------------------


def normalize_detail(s: str) -> str:
    mapping = {"kurz": "short", "mittel": "medium", "voll": "full",
               "short": "short", "medium": "medium", "full": "full"}
    return mapping.get(s, s)


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Colorful PyPy3 simulation of an angular vector-currency economy / Winkelwährungswirtschaft.")
    p.add_argument("--lang", "--language", "--sprache", choices=["en", "de"], default="en",
                   help="Output language. Standard/default: en. Use de for German.")
    p.add_argument("--deutsch", action="store_true", help="Shortcut for --lang de.")
    p.add_argument("--ticks", type=int, default=18, help="Number of simulation periods. Default: 18")
    p.add_argument("--seed", type=int, default=7, help="Random seed for reproducible angles. Default: 7")
    p.add_argument("--scenario", choices=SCENARIOS, default="baseline",
                   help="Scenario climate: baseline, resonance, power, wellbeing, fragmented, scarcity, tradeboom.")
    p.add_argument("--detail", choices=["short", "medium", "full", "kurz", "mittel", "voll"], default="full",
                   help="Output detail for sector tables. Default: full")
    p.add_argument("--report-every", "--bericht-jeder", type=int, default=1,
                   help="Print detailed report only every n-th tick. Default: 1")
    p.add_argument("--width", "--breite", type=int, default=118, help="Output text width. Default: 118")
    p.add_argument("--no-color", "--ohne-farbe", action="store_true", help="Disable ANSI colors.")
    p.add_argument("--without-explanations", "--ohne-erklaerungen", action="store_true",
                   help="Skip local explanatory blocks above each simulation part.")
    p.add_argument("--only-manual", "--nur-handbuch", action="store_true",
                   help="Print header and local glossary previews, then stop.")
    p.add_argument("--no-utf8-gallery", "--ohne-utf8-galerie", action="store_true",
                   help="Do not print the final UTF-8 art gallery.")
    p.add_argument("--no-scenario-comparison", action="store_true",
                   help="Do not run silent comparison scenarios for the gallery.")
    p.add_argument("--export-csv", default="", help="Path for country history CSV.")
    p.add_argument("--export-currencies-csv", "--export-waehrungen-csv", default="", help="Path for currency history CSV.")
    p.add_argument("--export-md", default="", help="Path for final Markdown report.")
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    lang = "de" if args.deutsch else args.lang
    detail = normalize_detail(args.detail)
    sim = AngularEconomy(seed=args.seed, ticks=max(1, args.ticks), detail=detail,
                         report_every=max(1, args.report_every), width=max(90, args.width),
                         colors=not args.no_color, explanations=not args.without_explanations,
                         lang=lang, scenario=args.scenario, gallery=not args.no_utf8_gallery,
                         compare_scenarios=not args.no_scenario_comparison)
    if args.only_manual:
        sim.print_header()
        sim.print_preface()
        for key in ["currency", "labor", "goods", "trade", "indices", "drift", "final"]:
            small_section(key.upper(), Ansi.BRIGHT_CYAN)
            sim.explain_part(key)
        return 0
    sim.run()
    if args.export_csv:
        sim.export_csv(args.export_csv)
        print(col(f"\nCSV exported: {args.export_csv}" if lang == "en" else f"\nCSV exportiert: {args.export_csv}", Ansi.BRIGHT_GREEN))
    if args.export_currencies_csv:
        sim.export_currency_csv(args.export_currencies_csv)
        print(col(f"Currency CSV exported: {args.export_currencies_csv}" if lang == "en" else f"Währungs-CSV exportiert: {args.export_currencies_csv}", Ansi.BRIGHT_GREEN))
    if args.export_md:
        sim.export_markdown(args.export_md)
        print(col(f"Markdown report exported: {args.export_md}" if lang == "en" else f"Markdownbericht exportiert: {args.export_md}", Ansi.BRIGHT_GREEN))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
