#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Winkelwährungswirtschaft - eine bunte PyPy3-Simulation
======================================================

Dieses Skript simuliert ein Wirtschaftssystem, in dem nicht Reichtum die
Hauptzielgröße ist, sondern Macht und Wohlbefinden. Die Währung besteht aus
3 konkurrierenden Euro-Vektoren. Alle drei Vektoren haben dieselbe Länge,
weil jeder einzelne Vektor-Euro ein Euro ist. Konkurrenz entsteht nicht durch
unterschiedliche Länge oder Wechselkurs-Multiplikatoren, sondern ausschließlich
über Winkel.

Start:
    pypy3 winkelwirtschaft_simulation_pypy3.py

Beispiele:
    pypy3 winkelwirtschaft_simulation_pypy3.py --ticks 18 --detail voll
    pypy3 winkelwirtschaft_simulation_pypy3.py --ticks 8 --ohne-farbe --export-csv verlauf.csv
    pypy3 winkelwirtschaft_simulation_pypy3.py --nur-handbuch

Keine externen Bibliotheken. Läuft mit PyPy3 und CPython3.
"""

import argparse
import csv
import math
import os
import random
import sys
import textwrap
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Iterable, Optional

# -----------------------------------------------------------------------------
# 1. Terminalfarben und Ausgabehelfer
# -----------------------------------------------------------------------------

class Ansi:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    BLACK = "\033[30m"
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


def col(text: str, code: str) -> str:
    if not COLOR_ON:
        return str(text)
    return code + str(text) + Ansi.RESET


def bold(text: str) -> str:
    return col(text, Ansi.BOLD)


def dim(text: str) -> str:
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
            out.append(textwrap.fill(p.strip(), width=width, initial_indent=prefix,
                                     subsequent_indent=prefix))
    return "\n".join(out)


def section(title: str, color: str = Ansi.BRIGHT_CYAN) -> None:
    print()
    print(col(hr("═"), color))
    print(col(title, color + Ansi.BOLD if COLOR_ON else ""))
    print(col(hr("═"), color))


def small_section(title: str, color: str = Ansi.CYAN) -> None:
    print()
    print(col("── " + title + " " + "─" * max(1, WRAP_WIDTH - len(title) - 4), color))


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


def angle_arrow(angle: float) -> str:
    # Acht grobe Richtungen. Der Pfeil ist nur eine Lesehilfe; die Rechnung nutzt Grad.
    arrows = ["→", "↗", "↑", "↖", "←", "↙", "↓", "↘"]
    idx = int(((norm_angle(angle) + 22.5) % 360) // 45)
    return arrows[idx]


def angle_label(angle: float) -> str:
    return f"{angle_arrow(angle)} {norm_angle(angle):6.1f}°"


def table(headers: List[str], rows: List[List[object]], colors: Optional[List[str]] = None) -> str:
    # Robuster Einfach-Tabellenbau ohne externe Bibliothek.
    str_rows = [[str(x) for x in r] for r in rows]
    widths = [len(h) for h in headers]
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
        line_cells = []
        for i, cell in enumerate(r):
            line_cells.append(pad_cell(cell, widths[i]))
        line = "│ " + " │ ".join(line_cells) + " │"
        if colors and ri < len(colors) and colors[ri]:
            line = col(line, colors[ri])
        out.append(line)
    out.append(end)
    return "\n".join(out)


def strip_ansi(s: str) -> str:
    # Kleine ANSI-Entfernung, ausreichend für Tabellenbreiten.
    out = []
    i = 0
    s = str(s)
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

# -----------------------------------------------------------------------------
# 2. Winkelmathematik
# -----------------------------------------------------------------------------


def norm_angle(a: float) -> float:
    return a % 360.0


def signed_delta(a: float, b: float) -> float:
    """Kürzeste Drehung von Winkel a nach Winkel b in Grad, Bereich [-180, 180)."""
    return ((b - a + 180.0) % 360.0) - 180.0


def angle_distance(a: float, b: float) -> float:
    return abs(signed_delta(a, b))


def klang(a: float, b: float) -> float:
    """
    Winkelklang zwischen zwei Richtungen.
    1.0 = gleiche Richtung, 0.0 = Gegenrichtung.
    Das ist kein Gut/Böse-Wert und kein Positiv/Negativ-Wert, sondern nur Nähe auf dem Kreis.
    """
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
    # Scores sind 0..1. Temperatur macht klare Vorlieben sichtbar, ohne harte Entscheidung.
    if not scores:
        return []
    m = max(scores)
    vals = [math.exp((s - m) * temperature) for s in scores]
    total = sum(vals)
    if total == 0:
        return [1.0 / len(scores)] * len(scores)
    return [v / total for v in vals]


def circular_noise(rng: random.Random, span: float) -> float:
    return rng.uniform(-span, span)

# -----------------------------------------------------------------------------
# 3. Datenklassen des Modells
# -----------------------------------------------------------------------------

ACTIONS = ["KAUF", "VERKAUF", "ARBEIT"]
ACTION_LABELS = {
    "KAUF": "Kaufmarkt",
    "VERKAUF": "Verkaufsmarkt",
    "ARBEIT": "Arbeitsmarkt",
}
ACTION_OFFSET = {
    "KAUF": 0.0,
    "VERKAUF": 32.0,
    "ARBEIT": -42.0,
}

@dataclass
class VectorCurrency:
    code: str
    name: str
    home: str
    angle: float
    color: str
    length: float = 1.0
    macht: float = 50.0
    flow: float = 0.0
    share: float = 1.0 / 3.0
    last_target: float = 0.0

    def reset_flow(self) -> None:
        self.flow = 0.0

@dataclass
class Sector:
    code: str
    name: str
    need: float
    labor_need: float
    productivity: float
    base_price: float
    angle_bias: float
    exportability: float
    volatility: float
    color: str

@dataclass
class AngleState:
    gbw: float  # Gut-Böse-Winkel: Richtung des Gut-Pols, Regierung setzt diese Richtung.
    buw: float  # Beliebt-Unbeliebt-Winkel: Richtung des Beliebt-Pols, Bevölkerung setzt diese Richtung.
    last_hw: float = 0.0
    last_currency: str = ""
    last_klang: float = 0.0

    def handlungswinkel(self) -> float:
        # Der Handlungswinkel liegt zwischen Gut-Pol und Beliebt-Pol.
        # Bei genau orthogonalen Achsen liegt er auf der Diagonale Gut+Beliebt.
        self.last_hw = circular_mean([self.gbw, self.buw], [0.54, 0.46])
        return self.last_hw

    def orth_error(self) -> float:
        # Ideale Orthogonalität: BUW liegt 90° neben GBW.
        return angle_distance(self.buw, self.gbw + 90.0)

    def moral_nearness(self, angle: Optional[float] = None) -> Tuple[float, float]:
        h = self.last_hw if angle is None else angle
        return klang(h, self.gbw), klang(h, self.gbw + 180.0)

    def popular_nearness(self, angle: Optional[float] = None) -> Tuple[float, float]:
        h = self.last_hw if angle is None else angle
        return klang(h, self.buw), klang(h, self.buw + 180.0)

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
    imports: Dict[str, float] = field(default_factory=dict)
    exports: Dict[str, float] = field(default_factory=dict)
    demand: Dict[str, float] = field(default_factory=dict)
    satisfaction: Dict[str, float] = field(default_factory=dict)
    prices: Dict[str, float] = field(default_factory=dict)
    angles: Dict[Tuple[str, str], AngleState] = field(default_factory=dict)
    wbi: float = 55.0  # Wohlbefindenindex
    mpi: float = 55.0  # Machtindex
    wsk: float = 55.0  # Wirtschaftsstärke
    spg: float = 25.0  # Spannung
    fatigue: float = 0.0
    last_currency_mix: Dict[str, float] = field(default_factory=dict)
    notes: List[str] = field(default_factory=list)

    def reset_tick(self, sectors: List[Sector]) -> None:
        self.production = {s.code: 0.0 for s in sectors}
        self.imports = {s.code: 0.0 for s in sectors}
        self.exports = {s.code: 0.0 for s in sectors}
        self.demand = {s.code: 0.0 for s in sectors}
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
# 4. Simulationswelt
# -----------------------------------------------------------------------------

class AngularEconomy:
    def __init__(self, seed: int = 7, ticks: int = 18, detail: str = "voll",
                 bericht_jeder: int = 1, breite: int = 118, colors: bool = True,
                 erklaerungen: bool = True):
        global COLOR_ON, WRAP_WIDTH
        COLOR_ON = colors
        WRAP_WIDTH = breite
        self.rng = random.Random(seed)
        self.seed = seed
        self.max_ticks = ticks
        self.detail = detail
        self.bericht_jeder = max(1, bericht_jeder)
        self.erklaerungen = erklaerungen
        self.t = 0
        self.sectors = self._make_sectors()
        self.currencies = self._make_currencies()
        self.countries = self._make_countries()
        self.history: List[Dict[str, object]] = []
        self.transaction_history: List[TransactionRecord] = []
        self.trade_history: List[TradeRecord] = []
        self.currency_history: List[Dict[str, object]] = []
        self._init_angles()

    # -------------------------------------------------------------------------
    # Initialisierung
    # -------------------------------------------------------------------------

    def _make_sectors(self) -> List[Sector]:
        return [
            Sector("NAH", "Nahrung",        1.18, 0.84, 1.10, 1.10,   6.0, 0.35, 0.38, Ansi.BRIGHT_GREEN),
            Sector("ENE", "Energie",        1.05, 0.96, 0.86, 1.62,  38.0, 0.62, 0.62, Ansi.BRIGHT_YELLOW),
            Sector("WOH", "Wohnen",         1.00, 0.92, 0.76, 1.86, -24.0, 0.12, 0.30, Ansi.YELLOW),
            Sector("GES", "Gesundheit",     1.12, 1.18, 0.92, 1.72,  74.0, 0.08, 0.34, Ansi.BRIGHT_MAGENTA),
            Sector("BIL", "Bildung",        0.88, 0.78, 1.12, 1.12, 112.0, 0.05, 0.28, Ansi.BRIGHT_CYAN),
            Sector("KUL", "Kultur",         0.68, 0.42, 1.18, 0.82, 146.0, 0.30, 0.72, Ansi.MAGENTA),
            Sector("SIC", "Sicherheit",     0.74, 0.86, 0.98, 1.28, -82.0, 0.04, 0.58, Ansi.BRIGHT_BLUE),
            Sector("DAT", "Daten",          0.92, 0.56, 1.46, 1.20, 190.0, 0.76, 0.66, Ansi.CYAN),
            Sector("MOB", "Mobilität",      0.82, 0.73, 0.90, 1.40, 232.0, 0.58, 0.48, Ansi.BLUE),
        ]

    def _make_currencies(self) -> Dict[str, VectorCurrency]:
        # Alle Längen bleiben 1.0. Die 120°-Startteilung macht Konkurrenz sichtbar.
        return {
            "EA": VectorCurrency("EA", "Euro-Aur", "AUR", 8.0,   Ansi.BRIGHT_RED,    1.0, 62.0),
            "EB": VectorCurrency("EB", "Euro-Bel", "BEL", 128.0, Ansi.BRIGHT_GREEN,  1.0, 48.0),
            "EC": VectorCurrency("EC", "Euro-Cal", "CAL", 248.0, Ansi.BRIGHT_BLUE,   1.0, 55.0),
        }

    def _make_countries(self) -> Dict[str, Country]:
        return {
            "AUR": Country("AUR", "Auron", "EA", Ansi.BRIGHT_RED,   1.12, 0.82, 0.68, 0.32, wbi=54, mpi=63, wsk=58, spg=28),
            "BEL": Country("BEL", "Belvar", "EB", Ansi.BRIGHT_GREEN, 0.98, 0.58, 0.43, 0.67, wbi=66, mpi=47, wsk=57, spg=24),
            "CAL": Country("CAL", "Caldra", "EC", Ansi.BRIGHT_BLUE,  1.06, 0.70, 0.57, 0.49, wbi=51, mpi=56, wsk=61, spg=31),
        }

    def _init_angles(self) -> None:
        country_offsets = {"AUR": -12.0, "BEL": 18.0, "CAL": -28.0}
        pop_offsets = {"AUR": 7.0, "BEL": -16.0, "CAL": 11.0}
        for c in self.countries.values():
            cur = self.currencies[c.currency]
            for sec in self.sectors:
                for action in ACTIONS:
                    gbw = cur.angle + sec.angle_bias + ACTION_OFFSET[action] + country_offsets[c.code]
                    gbw += circular_noise(self.rng, 18.0)
                    # Beliebt-Pol startet nahe orthogonal, aber nicht perfekt.
                    buw = gbw + 90.0 + pop_offsets[c.code] + circular_noise(self.rng, 22.0)
                    c.angles[(action, sec.code)] = AngleState(norm_angle(gbw), norm_angle(buw))

    # -------------------------------------------------------------------------
    # Grundlegende Modellfunktionen
    # -------------------------------------------------------------------------

    def choose_currency(self, hw: float) -> Tuple[str, float, Dict[str, float]]:
        codes = list(self.currencies.keys())
        scores = [klang(self.currencies[k].angle, hw) for k in codes]
        shares_list = softmax01(scores, temperature=7.5)
        shares = {k: shares_list[i] for i, k in enumerate(codes)}
        best = max(codes, key=lambda k: shares[k])
        return best, scores[codes.index(best)], shares

    def price_for(self, country: Country, sec: Sector, action: str, hw: float, supply_ratio: float) -> float:
        # Preis = Anzahl gleich langer Vektor-Euro-Einheiten. Die einzelne Länge bleibt 1.
        home_cur = self.currencies[country.currency]
        currency_fit = klang(home_cur.angle, hw)
        shortage_factor = 1.0 + clamp(1.0 - supply_ratio, 0.0, 1.0) * 0.85
        angle_factor = 0.72 + (1.0 - currency_fit) * 0.95
        action_factor = {"KAUF": 1.00, "VERKAUF": 0.94, "ARBEIT": 0.82}[action]
        mood_factor = 1.08 - clamp(country.wbi / 100.0, 0.0, 1.0) * 0.16
        return max(0.05, sec.base_price * shortage_factor * angle_factor * action_factor * mood_factor)

    def record_transaction(self, rec: TransactionRecord) -> None:
        self.transaction_history.append(rec)
        for code, share in rec.shares.items():
            self.currencies[code].flow += rec.amount_ve * share

    # -------------------------------------------------------------------------
    # Ausführliches Handbuch in der Skriptausgabe
    # -------------------------------------------------------------------------

    def print_header(self) -> None:
        title = "WINKELWÄHRUNGSWIRTSCHAFT — BUNTE PYTHON/PYPY3-SIMULATION"
        print(rainbow(title))
        print(col(hr("═"), Ansi.BRIGHT_MAGENTA))
        print(wrap(
            "Dieses Programm simuliert ein System mit drei Länderregierungen, drei konkurrierenden "
            "Vektor-Währungen und drei Marktarten: Kauf, Verkauf und Arbeit. Die drei Währungen "
            "sind keine verschieden langen Geldbeträge. Alle sind Euro-Vektoren mit derselben Länge. "
            "Der Wettbewerb entsteht aus Richtung, Winkelklang, Machtbindung und Wohlbefinden, nicht aus "
            "Reichtumsmaximierung.", WRAP_WIDTH))
        print()
        print(col("Startparameter:", Ansi.BOLD),
              f"Seed={self.seed}, Ticks={self.max_ticks}, Detail={self.detail}, Farben={'an' if COLOR_ON else 'aus'}")

    def print_manual(self) -> None:
        section("0) Grundidee und Einheiten", Ansi.BRIGHT_MAGENTA)
        print(wrap(
            "Die Simulation behandelt Geld nicht zuerst als Zahlenmenge, sondern als Richtungsträger. "
            "Eine Währungseinheit ist ein Vektor-Euro. Die Vektorlänge aller drei Währungen ist immer "
            "gleich: |EA| = |EB| = |EC| = 1 VE. Der Ausdruck VE bedeutet Vektor-Euro-Einheit. Wenn ein "
            "Preis 3.20 VE beträgt, heißt das nicht, dass ein Euro-Vektor länger geworden ist. Es heißt nur, "
            "dass 3.20 gleich lange Euro-Vektoren benötigt werden. Der eigentliche Wettbewerb liegt im Winkel: "
            "welche Währung zeigt für eine konkrete Marktentscheidung in die passendere Richtung?"))
        print()
        print(wrap(
            "Die Regierung jedes Landes bestimmt für jeden Markt und jeden Sektor einen Gut-Böse-Winkel. "
            "Das Skript nennt ihn GBW°. GBW° ist kein Subventionswert, keine Strafe und kein Positiv/Negativ-Score. "
            "Er ist die Richtung des Gut-Pols auf dem Kreis. Der Gegenpol, also GBW° + 180°, ist der Böse-Pol. "
            "Die Bevölkerung bestimmt eine dazu orthogonale Achse Beliebt-Unbeliebt. Das Skript nennt die Richtung "
            "des Beliebt-Pols BUW°. Im idealen Fall liegt BUW° etwa 90° neben GBW°. In der Simulation kann diese "
            "Orthogonalität driften, weil Bevölkerungserfahrung, Arbeitsermüdung, Mangel und Erfolg den Beliebt-Pol "
            "drehen."))
        print()
        print(table(
            ["Kürzel", "Einheit", "Bedeutung im Modell"],
            [
                ["VE", "Vektor-Euro", "Eine gleich lange Euro-Vektoreinheit. Jede Währungseinheit hat Länge 1."],
                ["EA/EB/EC", "Währungscode", "Euro-Aur, Euro-Bel, Euro-Cal: drei konkurrierende Winkelwährungen."],
                ["°", "Grad", "Richtung auf dem Kreis. 0° und 360° sind dieselbe Richtung."],
                ["GBW°", "Grad", "Gut-Böse-Winkel: Richtung des Gut-Pols, gesetzt durch Regierung."],
                ["BUW°", "Grad", "Beliebt-Unbeliebt-Winkel: Richtung des Beliebt-Pols, gesetzt durch Bevölkerung."],
                ["HW°", "Grad", "Handlungswinkel: konkrete Richtung einer Kauf-, Verkaufs- oder Arbeitsentscheidung."],
                ["OEA°", "Grad", "Orthogonalitätsabweichung: Abstand zwischen BUW° und GBW°+90°. Weniger ist ruhiger."],
                ["KLG", "0..1", "Winkelklang zwischen Währung und Handlung. 1 = gleiche Richtung, 0 = Gegenrichtung."],
                ["WK°", "Grad", "Winkelkurs zwischen zwei Währungen. Kein Geldkurs, sondern Drehabstand."],
                ["UA", "rad·VE", "Umlenkungsarbeit: VE-Menge mal Winkel in Radiant bei Handel oder Währungswechsel."],
                ["WBI", "0..100", "Wohlbefindenindex. Zielgröße der Bevölkerung, nicht Reichtum."],
                ["MPI", "0..100", "Machtindex. Zielgröße der Regierung und der eigenen Währung."],
                ["WSK", "0..100", "Wirtschaftsstärke: Leistungsfähigkeit unter Winkelspannung."],
                ["SPG", "0..100", "Spannung: Reibung zwischen Regierung, Bevölkerung, Währung und Markt."],
            ]))

        section("1) Simulationsteil: Währungsring", Ansi.BRIGHT_CYAN)
        print(wrap(
            "Im Währungsring stehen EA, EB und EC gleichzeitig zur Verfügung. Alle drei haben Länge 1 VE. "
            "Die Währungen konkurrieren also nicht dadurch, dass eine mehr Euro wäre als die andere. Sie konkurrieren "
            "dadurch, dass sie für eine Handlung besser oder schlechter im Winkel liegen. Das Skript berechnet den "
            "Klang KLG zwischen Währungswinkel und Handlungswinkel. Daraus entsteht ein Marktanteil der Währung. "
            "Der Marktanteil ist keine staatliche Förderung und keine Strafe. Er ist die Folge davon, welche Richtung "
            "in diesem Augenblick am meisten Sinnbindung erzeugt."))

        section("2) Simulationsteil: Marktwinkel für Kauf, Verkauf und Arbeit", Ansi.BRIGHT_CYAN)
        print(wrap(
            "Jeder Sektor besitzt drei Marktarten: KAUF, VERKAUF und ARBEIT. Für jede dieser Marktarten existiert "
            "ein GBW° der Regierung und ein BUW° der Bevölkerung. Aus beiden entsteht der HW°, der konkrete Winkel "
            "der Handlung. Beispiel: Nahrung kaufen kann in einem Land gut und beliebt nah beieinander liegen; "
            "Energie verkaufen kann in einem anderen Land gut, aber wenig beliebt liegen; Arbeit im Sicherheitssektor "
            "kann machtstark, aber wohlbefindensschwer sein. Das Modell bewertet solche Fälle nicht über Ja/Nein oder "
            "Subvention/Strafe, sondern über Kreisabstände."))

        section("3) Simulationsteil: Arbeitsmarkt", Ansi.BRIGHT_CYAN)
        print(wrap(
            "Der Arbeitsmarkt simuliert, wie viel Arbeitskraft in Sektoren fließt. Arbeit entsteht nicht nur, weil ein "
            "Lohn bezahlt wird, sondern weil der Arbeitswinkel mit Währung, Gut-Böse-Achse und Beliebt-Achse zusammenklingt. "
            "Ein Sektor kann viel Macht erzeugen, aber das Wohlbefinden senken, wenn sein Arbeitswinkel weit vom Beliebt-Pol "
            "entfernt liegt. Das Skript führt dafür Ermüdung als FTD ein. FTD steht für Fatigue/Ermüdung. Sie ist keine Strafe, "
            "sondern ein Modell für Lebensdruck durch unpassende Arbeitswinkel."))

        section("4) Simulationsteil: Gütermarkt und Vektor-Euro-Preise", Ansi.BRIGHT_CYAN)
        print(wrap(
            "Der Gütermarkt berechnet Bedarf, Produktion, Mangel, Zufriedenheit und Preis. Der Preis wird in VE angegeben. "
            "Wichtig: Der Preis verändert nicht die Länge des einzelnen Euro-Vektors. Wenn Energie 2.40 VE kostet, sind das "
            "2.40 Vektor-Euro-Einheiten mit Länge 1. Die Preiszahl beschreibt Menge von gleich langen Vektoren. Winkelspannung "
            "kann Preise erhöhen, weil mehr institutionelle, soziale und symbolische Umlenkung nötig wird. Das ist kein klassischer "
            "Inflationsbegriff, sondern eine Winkelpreisbildung."))

        section("5) Simulationsteil: Handelsdreieck zwischen drei Ländern", Ansi.BRIGHT_CYAN)
        print(wrap(
            "Das Handelsdreieck simuliert Export und Import. Ein Export wird nur dann kräftig, wenn der Verkaufswinkel des Exportlandes "
            "und der Kaufwinkel des Importlandes gemeinsam eine halbwegs tragbare Richtung bilden. Die Zahlung kann nominell weiter Euro "
            "bleiben, aber die benutzte Winkelwährung entscheidet, welche Regierung Machtbindung gewinnt. Der WK° zwischen zwei Währungen "
            "zeigt, wie groß die Drehung ist. Die UA, Umlenkungsarbeit, misst rad·VE: Wie viel Vektor-Euro-Menge musste um welchen Winkel "
            "gedreht werden, damit Handel möglich wird?"))

        section("6) Simulationsteil: Macht und Wohlbefinden statt Reichtum", Ansi.BRIGHT_CYAN)
        print(wrap(
            "Nach jedem Tick werden WBI, MPI, WSK und SPG berechnet. WBI steigt, wenn Bedürfnisse gedeckt werden und Handlungen nahe am "
            "Beliebt-Pol liegen. MPI steigt, wenn die eigene Währung in vielen Handlungen genutzt wird und der Regierungswinkel mit der "
            "Währung zusammenklingt. WSK steigt, wenn Produktion, Handel und Bedarfserfüllung trotz Winkelkonkurrenz stabil bleiben. "
            "SPG steigt, wenn Gut-Böse-Achse, Beliebt-Achse und Währungswinkel auseinanderfallen. Die Simulation strebt deshalb nicht "
            "nach größtmöglichem Reichtum, sondern zeigt ein Kräftefeld aus Macht, Wohlbefinden und Richtungskohärenz."))

        section("7) Simulationsteil: Drehung der Winkel über Zeit", Ansi.BRIGHT_CYAN)
        print(wrap(
            "Die Winkel bleiben nicht starr. Regierungen drehen ihre Gut-Böse-Winkel langsam dorthin, wo ihre Währung Machtbindung gewinnt. "
            "Bevölkerungen drehen ihre Beliebt-Winkel dorthin, wo Bedarfserfüllung und Lebensgefühl stimmen. Währungen drehen sich langsam "
            "in Richtung der Handlungen, in denen sie häufig benutzt werden. Alle Drehungen sind begrenzt. Dadurch entstehen Pfadabhängigkeit, "
            "Tradition, plötzliche Resonanz, Blockbildung und Wirtschaftsschwächung durch Fehlwinkel."))

    # -------------------------------------------------------------------------
    # Tick-Module
    # -------------------------------------------------------------------------

    def run(self) -> None:
        self.print_header()
        if self.erklaerungen:
            self.print_manual()
        for t in range(1, self.max_ticks + 1):
            self.t = t
            self.step()
            if t % self.bericht_jeder == 0:
                self.print_tick_report(t)
        self.print_final_report()

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
                st = c.angles[("ARBEIT", sec.code)]
                hw = st.handlungswinkel()
                best, best_k, shares = self.choose_currency(hw)
                st.last_currency = best
                st.last_klang = best_k
                own_fit = klang(self.currencies[c.currency].angle, hw)
                popular_fit = klang(hw, st.buw)
                gov_fit = klang(hw, st.gbw)
                # Arbeitsmenge: Bedarf * Bevölkerung * Klangmischung * Produktivität.
                base_hours = c.population * sec.labor_need * 38.0
                hours = base_hours * (0.48 + 0.52 * best_k) * (0.72 + 0.28 * popular_fit)
                # Tradition stabilisiert auch unmoderne Winkel, kann aber Ermüdung verdecken.
                hours *= (0.92 + 0.10 * c.tradition)
                production = hours / 38.0 * sec.productivity * (0.82 + 0.26 * gov_fit)
                c.production[sec.code] = production
                # Ermüdung: Arbeitswinkel nahe Unbeliebt-Pol erzeugt Druck. Nicht Strafe, sondern Lebensreibung.
                unpop = klang(hw, st.buw + 180.0)
                labor_pressure += sec.labor_need * unpop * (0.8 + 0.4 * sec.volatility)
                price = self.price_for(c, sec, "ARBEIT", hw, supply_ratio=1.0)
                self.record_transaction(TransactionRecord(
                    self.t, c.code, sec.code, "ARBEIT", amount_ve=hours * price / 38.0,
                    hw=hw, chosen_currency=best, klang_best=best_k, shares=shares, price_ve=price))
            c.fatigue = clamp(0.72 * c.fatigue + 3.3 * labor_pressure / max(1.0, len(self.sectors)), 0.0, 100.0)

    def _simulate_trade_triangle(self) -> None:
        # Erst grober Bedarf, damit Überschuss/Mangel für Handel erkennbar wird.
        for c in self.countries.values():
            for sec in self.sectors:
                # Bedarf reagiert auf Wohlbefinden: Wer sich wohl fühlt, fragt Kultur/Bildung/Daten stärker nach.
                soft_need = 1.0 + (c.wbi - 55.0) / 230.0
                if sec.code in ("KUL", "BIL", "DAT", "MOB"):
                    need = c.population * sec.need * clamp(soft_need, 0.75, 1.25)
                else:
                    need = c.population * sec.need
                c.demand[sec.code] = max(0.01, need)

        for sec in self.sectors:
            excess = []
            deficit = []
            for c in self.countries.values():
                e = c.production[sec.code] - c.demand[sec.code]
                if e > 0:
                    excess.append([c, e])
                elif e < 0:
                    deficit.append([c, -e])
            # Paarweise grob nach größtem Überschuss/Mangel.
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
                    sell_st = exporter.angles[("VERKAUF", sec.code)]
                    buy_st = importer.angles[("KAUF", sec.code)]
                    sell_hw = sell_st.handlungswinkel()
                    buy_hw = buy_st.handlungswinkel()
                    joint_hw = circular_mean([sell_hw, buy_hw], [0.50, 0.50])
                    best, best_k, shares = self.choose_currency(joint_hw)
                    # Handelstauglichkeit: nicht Förderung, sondern gemeinsamer Winkelraum.
                    trade_fit = best_k * (0.62 + 0.38 * klang(sell_hw, buy_hw))
                    amount = min(ex_amt, df_amt) * sec.exportability * (0.28 + 0.72 * trade_fit)
                    if amount <= 0.0001:
                        continue
                    exporter.exports[sec.code] += amount
                    importer.imports[sec.code] += amount
                    ex_amt -= amount
                    df[1] -= amount
                    price = (self.price_for(exporter, sec, "VERKAUF", sell_hw, 1.0) +
                             self.price_for(importer, sec, "KAUF", buy_hw, 1.0)) / 2.0
                    amount_ve = amount * price
                    for code, share in shares.items():
                        self.currencies[code].flow += amount_ve * share
                    # Winkelkurs zwischen Export-Heimatwährung und benutzter Handelswährung.
                    wk = angle_distance(self.currencies[exporter.currency].angle, self.currencies[best].angle)
                    ua = math.radians(wk) * amount_ve
                    self.trade_history.append(TradeRecord(self.t, sec.code, exporter.code, importer.code,
                                                          amount, best, wk, ua, joint_hw))
                ex[1] = ex_amt

    def _simulate_goods_and_transactions(self) -> None:
        for c in self.countries.values():
            for sec in self.sectors:
                final_supply = max(0.0, c.production[sec.code] - c.exports[sec.code] + c.imports[sec.code])
                demand = max(0.01, c.demand[sec.code])
                supply_ratio = clamp(final_supply / demand, 0.0, 1.6)
                satisfaction = clamp(final_supply / demand, 0.0, 1.0)
                c.satisfaction[sec.code] = satisfaction

                # Kaufhandlung
                buy_st = c.angles[("KAUF", sec.code)]
                buy_hw = buy_st.handlungswinkel()
                best, best_k, shares = self.choose_currency(buy_hw)
                buy_st.last_currency = best
                buy_st.last_klang = best_k
                price_buy = self.price_for(c, sec, "KAUF", buy_hw, supply_ratio)
                c.prices[sec.code] = price_buy
                amount_ve_buy = demand * price_buy * (0.42 + 0.58 * satisfaction)
                self.record_transaction(TransactionRecord(self.t, c.code, sec.code, "KAUF", amount_ve_buy,
                                                          buy_hw, best, best_k, shares, price_buy))

                # Verkaufshandlung: Produktion + Exportwirkung.
                sell_st = c.angles[("VERKAUF", sec.code)]
                sell_hw = sell_st.handlungswinkel()
                best2, best_k2, shares2 = self.choose_currency(sell_hw)
                sell_st.last_currency = best2
                sell_st.last_klang = best_k2
                price_sell = self.price_for(c, sec, "VERKAUF", sell_hw, max(0.2, supply_ratio))
                amount_ve_sell = (c.production[sec.code] + c.exports[sec.code]) * price_sell * (0.35 + 0.65 * best_k2)
                self.record_transaction(TransactionRecord(self.t, c.code, sec.code, "VERKAUF", amount_ve_sell,
                                                          sell_hw, best2, best_k2, shares2, price_sell))

    def _compute_indices(self) -> None:
        total_flow = sum(cur.flow for cur in self.currencies.values()) or 1.0
        for cur in self.currencies.values():
            cur.share = cur.flow / total_flow

        # Landbezogene Transaktionsmischungen.
        for c in self.countries.values():
            mix = {code: 0.0 for code in self.currencies.keys()}
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
                    hw = st.last_hw if st.last_hw else st.handlungswinkel()
                    # Nähe zum Beliebt-Pol für Wohlbefinden.
                    pop_harmony += klang(hw, st.buw) * (w / 3.0)
                    # Regierung/Bevölkerung fallen auseinander: Gut-Pol gegen Beliebt-Pol.
                    gov_pop_gap += angle_distance(st.gbw, st.buw - 90.0) / 90.0 * (w / 3.0)
                    # Währung/Handlung fallen auseinander.
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
            # Wohlbefindenstil verstärkt die Wirkung von erfülltem Bedarf.
            wbi_target = wbi_target * (0.90 + 0.12 * c.wellbeing_style)

            mpi_target = 100.0 * (0.52 * own_share + 0.26 * gov_fit_avg + 0.14 * clamp(prod_ratio / 1.25, 0.0, 1.0) + 0.08 * trade_norm)
            mpi_target = mpi_target * (0.92 + 0.10 * c.govt_power_style)

            spg_target = 100.0 * clamp(0.34 * gov_pop + 0.28 * curr_g + 0.22 * orth_g + 0.16 * clamp(price_p - 1.0, 0.0, 1.4), 0.0, 1.0)

            wsk_target = 100.0 * clamp(0.42 * sat + 0.27 * clamp(prod_ratio / 1.2, 0.0, 1.0) + 0.17 * trade_norm + 0.14 * (1.0 - spg_target / 110.0), 0.0, 1.0)

            c.wbi = clamp(0.72 * c.wbi + 0.28 * wbi_target, 0.0, 100.0)
            c.mpi = clamp(0.70 * c.mpi + 0.30 * mpi_target, 0.0, 100.0)
            c.spg = clamp(0.68 * c.spg + 0.32 * spg_target, 0.0, 100.0)
            c.wsk = clamp(0.70 * c.wsk + 0.30 * wsk_target, 0.0, 100.0)

            # Kurze Ereignisnotizen.
            weakest = min(self.sectors, key=lambda s: c.satisfaction[s.code])
            strongest = max(self.sectors, key=lambda s: c.satisfaction[s.code])
            if c.satisfaction[weakest.code] < 0.72:
                c.notes.append(f"Mangelwinkel bei {weakest.name} ({c.satisfaction[weakest.code]*100:.0f}% Bedarf gedeckt)")
            if c.last_currency_mix.get(c.currency, 0.0) < 0.36:
                dominant = max(c.last_currency_mix, key=lambda k: c.last_currency_mix[k])
                c.notes.append(f"Fremdwährung {dominant} überklingt eigene Währung")
            if c.satisfaction[strongest.code] > 0.98:
                c.notes.append(f"stabile Deckung bei {strongest.name}")

        # Währungs-Macht aus Marktanteil und Heimat-Macht aktualisieren.
        for code, cur in self.currencies.items():
            home = self.countries[cur.home]
            target = 100.0 * (0.58 * cur.share + 0.42 * home.mpi / 100.0)
            cur.macht = clamp(0.78 * cur.macht + 0.22 * target, 0.0, 100.0)

    def _rotate_angles(self) -> None:
        # Zielwinkel der Währungen: Handlungen, in denen sie benutzt werden, plus Heimat-Gutwinkel.
        for code, cur in self.currencies.items():
            angles = [cur.angle]
            weights = [2.0 + cur.macht / 50.0]
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
            cur.angle = rotate_towards(cur.angle, target, 0.020 + 0.0006 * cur.macht)
            cur.length = 1.0  # harte Modellregel: alle Währungslängen bleiben Euro-Länge.

        # Regierungs- und Bevölkerungswinkel drehen langsam.
        # Regierung: Richtung der eigenen Währung und machtstarke Handlungswinkel.
        # Bevölkerung: Richtung von bedarfsdeckenden Handlungen und weg von ermüdenden Arbeitserfahrungen.
        for c in self.countries.values():
            own_cur = self.currencies[c.currency]
            for sec in self.sectors:
                sat = c.satisfaction.get(sec.code, 0.8)
                for action in ACTIONS:
                    st = c.angles[(action, sec.code)]
                    hw = st.last_hw if st.last_hw else st.handlungswinkel()
                    # Regierung hält Tradition, bewegt sich aber in Richtung eigener Währung und erfolgreicher Handlung.
                    gov_target = circular_mean([st.gbw, own_cur.angle, hw], [2.4 * c.tradition, 1.1 * c.govt_power_style, 0.6 + c.mpi / 120.0])
                    st.gbw = rotate_towards(st.gbw, gov_target, 0.006 + 0.010 * sec.volatility)
                    # Bevölkerung: hohes Bedürfnis-Erfüllen macht Handlung beliebter; Mangel dreht Beliebtheit weg.
                    if action == "KAUF":
                        pop_target = hw if sat >= 0.82 else norm_angle(hw + 180.0)
                        pop_rate = 0.012 + 0.018 * sec.volatility
                    elif action == "ARBEIT":
                        if c.fatigue < 32:
                            pop_target = hw
                        else:
                            pop_target = norm_angle(hw + 180.0)
                        pop_rate = 0.009 + 0.012 * sec.volatility
                    else:  # VERKAUF
                        export_signal = clamp(c.exports[sec.code] / max(0.01, c.production[sec.code]), 0.0, 1.0)
                        pop_target = hw if export_signal > 0.10 or sat > 0.88 else circular_mean([hw, st.buw], [0.4, 1.0])
                        pop_rate = 0.007 + 0.010 * sec.volatility
                    # Orthogonalitätsanker: Bevölkerung bleibt grundsätzlich quer zum Gut/Böse-Kreis, driftet aber.
                    ortho_anchor = norm_angle(st.gbw + 90.0)
                    mixed_target = circular_mean([pop_target, ortho_anchor], [1.0, 0.55 + c.tradition])
                    st.buw = rotate_towards(st.buw, mixed_target, pop_rate)

    def _snapshot_history(self) -> None:
        for c in self.countries.values():
            row = {
                "tick": self.t,
                "land": c.code,
                "WBI": round(c.wbi, 4),
                "MPI": round(c.mpi, 4),
                "WSK": round(c.wsk, 4),
                "SPG": round(c.spg, 4),
                "FTD": round(c.fatigue, 4),
                "eigene_waehrung_anteil": round(c.last_currency_mix.get(c.currency, 0.0), 4),
                "importe": round(sum(c.imports.values()), 4),
                "exporte": round(sum(c.exports.values()), 4),
                "produktion": round(sum(c.production.values()), 4),
                "bedarf": round(sum(c.demand.values()), 4),
            }
            for sec in self.sectors:
                row[f"sat_{sec.code}"] = round(c.satisfaction[sec.code], 4)
                row[f"preis_{sec.code}"] = round(c.prices[sec.code], 4)
            self.history.append(row)
        crow = {"tick": self.t}
        for code, cur in self.currencies.items():
            crow[f"{code}_winkel"] = round(cur.angle, 4)
            crow[f"{code}_laenge"] = round(cur.length, 4)
            crow[f"{code}_macht"] = round(cur.macht, 4)
            crow[f"{code}_fluss"] = round(cur.flow, 4)
            crow[f"{code}_anteil"] = round(cur.share, 4)
        self.currency_history.append(crow)

    # -------------------------------------------------------------------------
    # Berichte
    # -------------------------------------------------------------------------

    def print_tick_report(self, t: int) -> None:
        section(f"TICK {t}: Simulation eines Zeitabschnitts", Ansi.BRIGHT_MAGENTA)
        print(wrap(
            "Ein Tick ist eine abstrakte Periode. Er kann einen Monat, ein Quartal oder einen politischen Zyklus bedeuten. "
            "Die Einheiten bleiben gleich: Winkel in Grad, Preise in VE, Umlenkungsarbeit in rad·VE, Indizes von 0 bis 100."))
        self.print_currency_ring()
        self.print_country_summary()
        self.print_market_details()
        self.print_trade_summary()
        self.print_events()

    def print_currency_ring(self) -> None:
        small_section("A) Währungsring: drei gleich lange Euro-Vektoren", Ansi.BRIGHT_CYAN)
        print(wrap(
            "Die Tabelle zeigt die drei Währungen. Die Spalte |€⃗| bleibt 1.000 für alle. Anteil ist der Anteil am gesamten "
            "Transaktionsfluss dieses Ticks. Macht ist die akkumulierte Bindung der Währung an politische Ordnung und Marktgebrauch."))
        rows = []
        row_colors = []
        for cur in self.currencies.values():
            rows.append([
                cur.code,
                cur.name,
                cur.home,
                f"{cur.length:.3f} VE",
                angle_label(cur.angle),
                f"{cur.share*100:5.1f}%",
                f"{cur.macht:5.1f}",
                angle_label(cur.last_target),
            ])
            row_colors.append(cur.color)
        print(table(["Code", "Name", "Heimat", "|€⃗|", "Winkel", "Anteil", "Macht", "Zieldrehung"], rows, row_colors))
        pairs = []
        codes = list(self.currencies.keys())
        for i in range(len(codes)):
            for j in range(i + 1, len(codes)):
                a = self.currencies[codes[i]]
                b = self.currencies[codes[j]]
                pairs.append([f"{a.code}↔{b.code}", f"{angle_distance(a.angle, b.angle):6.1f}°", f"{klang(a.angle, b.angle):.3f}"])
        print(table(["Währungspaar", "WK°", "KLG"], pairs))

    def print_country_summary(self) -> None:
        small_section("B) Länder: Macht, Wohlbefinden, Stärke, Spannung", Ansi.BRIGHT_CYAN)
        print(wrap(
            "WBI ist das Wohlbefinden der Bevölkerung. MPI ist Machtbindung von Regierung und eigener Währung. WSK ist die "
            "Wirtschaftsstärke unter Winkelkonkurrenz. SPG ist Spannung; dort ist ein kleinerer Wert ruhiger. EigW ist der Anteil "
            "der eigenen Winkelwährung im Inland dieses Ticks."))
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
        print(table(["Land", "Name", "WBI", "MPI", "WSK", "SPG", "EigW", "DomW", "Prod", "Imp/Exp"], rows, colors))

    def sectors_for_detail(self, c: Country) -> List[Sector]:
        if self.detail == "kurz":
            # Die vier auffälligsten Sektoren je Land nach niedriger Deckung oder hohem Preis.
            scored = []
            for s in self.sectors:
                score = (1.0 - c.satisfaction[s.code]) * 1.5 + c.prices[s.code] / max(0.01, s.base_price) * 0.25
                scored.append((score, s))
            return [s for _, s in sorted(scored, key=lambda x: x[0], reverse=True)[:4]]
        if self.detail == "mittel":
            codes = {"NAH", "ENE", "WOH", "GES", "ARBEIT", "DAT"}
            return [s for s in self.sectors if s.code in {"NAH", "ENE", "WOH", "GES", "DAT", "KUL"}]
        return self.sectors

    def print_market_details(self) -> None:
        small_section("C) Märkte je Land und Sektor", Ansi.BRIGHT_CYAN)
        print(wrap(
            "Jede Zeile zeigt einen Sektor. Bed ist Bedarf, Prod ist Produktion, Dck ist Bedarfsdeckung, Preis ist VE je Einheit. "
            "Kauf-HW, Verkauf-HW und Arbeit-HW sind die Handlungswinkel. KW/VW/AW sind die jeweils stärksten Winkelwährungen "
            "für Kauf, Verkauf und Arbeit. OEA ist die mittlere Orthogonalitätsabweichung der drei Marktachsen im Sektor."))
        for c in self.countries.values():
            print()
            print(col(f"Land {c.code} — {c.name}", c.color + Ansi.BOLD if COLOR_ON else ""))
            rows = []
            row_colors = []
            for sec in self.sectors_for_detail(c):
                buy = c.angles[("KAUF", sec.code)]
                sell = c.angles[("VERKAUF", sec.code)]
                work = c.angles[("ARBEIT", sec.code)]
                oea = (buy.orth_error() + sell.orth_error() + work.orth_error()) / 3.0
                rows.append([
                    sec.code,
                    sec.name,
                    f"{c.demand[sec.code]:.2f}",
                    f"{c.production[sec.code]:.2f}",
                    f"{c.satisfaction[sec.code]*100:5.1f}%",
                    f"{c.prices[sec.code]:.2f} VE",
                    angle_label(buy.last_hw), buy.last_currency,
                    angle_label(sell.last_hw), sell.last_currency,
                    angle_label(work.last_hw), work.last_currency,
                    f"{oea:5.1f}°",
                ])
                row_colors.append(sec.color)
            print(table(["Sek", "Name", "Bed", "Prod", "Dck", "Preis", "Kauf-HW", "KW", "Verk-HW", "VW", "Arb-HW", "AW", "OEA"], rows, row_colors))

    def print_trade_summary(self) -> None:
        small_section("D) Handelsdreieck und Umlenkungsarbeit", Ansi.BRIGHT_CYAN)
        trades = [tr for tr in self.trade_history if tr.tick == self.t]
        if not trades:
            print(wrap("In diesem Tick entstand kein nennenswerter Dreieckshandel. Das kann bei sehr niedriger Exportfähigkeit oder starker Winkeltrennung passieren."))
            return
        print(wrap(
            "Jede Handelszeile zeigt Exportland, Importland, Sektor, Menge, genutzte Winkelwährung, WK° zur Export-Heimatwährung und "
            "UA. Eine hohe UA bedeutet: Der Handel bleibt möglich, braucht aber viel symbolische und institutionelle Winkel-Umlenkung."))
        # Bei sehr vielen Handelszeilen begrenzen wir für Lesbarkeit, summieren aber unten alles.
        max_rows = 14 if self.detail != "voll" else 30
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
        print(table(["Route", "Sek", "Menge", "W", "Joint-HW", "WK°", "UA"], rows))
        total_ua = sum(tr.angular_work for tr in trades)
        total_amount = sum(tr.amount for tr in trades)
        print(wrap(f"Summe Handel: {total_amount:.3f} Gütereinheiten; Summe UA: {total_ua:.3f} rad·VE."))

    def print_events(self) -> None:
        small_section("E) Ereignisnotizen dieses Ticks", Ansi.BRIGHT_CYAN)
        any_note = False
        for c in self.countries.values():
            if c.notes:
                any_note = True
                print(col(c.code + ": ", c.color + Ansi.BOLD if COLOR_ON else "") + "; ".join(c.notes))
        if not any_note:
            print("Keine starken Ereignisnotizen. Die Winkelwirtschaft läuft in diesem Tick relativ ruhig.")

    def print_final_report(self) -> None:
        section("ABSCHLUSSBERICHT", Ansi.BRIGHT_MAGENTA)
        print(wrap(
            "Der Abschlussbericht fasst nicht zusammen, welches Land am reichsten geworden ist. Er zeigt, welche Winkelwährung "
            "Machtbindung gewann, wo Wohlbefinden stabil war und wo die Wirtschaftsstärke durch Winkelspannung geschwächt wurde."))
        rows = []
        colors = []
        for c in self.countries.values():
            hist = [r for r in self.history if r["land"] == c.code]
            wbi_values = [float(r["WBI"]) for r in hist]
            mpi_values = [float(r["MPI"]) for r in hist]
            wsk_values = [float(r["WSK"]) for r in hist]
            spg_values = [float(r["SPG"]) for r in hist]
            rows.append([
                c.code,
                c.name,
                f"{c.wbi:5.1f} {spark(wbi_values, 0, 100)}",
                f"{c.mpi:5.1f} {spark(mpi_values, 0, 100)}",
                f"{c.wsk:5.1f} {spark(wsk_values, 0, 100)}",
                f"{c.spg:5.1f} {spark(spg_values, 0, 100)}",
                f"{c.last_currency_mix.get(c.currency, 0)*100:5.1f}%",
            ])
            colors.append(c.color)
        print(table(["Land", "Name", "WBI Verlauf", "MPI Verlauf", "WSK Verlauf", "SPG Verlauf", "EigW zuletzt"], rows, colors))
        print()
        cur_rows = []
        cur_colors = []
        for cur in self.currencies.values():
            cur_rows.append([
                cur.code, cur.name, cur.home,
                f"{cur.length:.3f} VE",
                angle_label(cur.angle),
                f"{cur.share*100:5.1f}%",
                f"{cur.macht:5.1f}",
            ])
            cur_colors.append(cur.color)
        print(table(["Währung", "Name", "Heimat", "Länge", "Endwinkel", "Anteil", "Macht"], cur_rows, cur_colors))
        print()
        print(wrap(
            "Interpretation: Wenn ein Land hohe WBI-Werte, aber niedrige MPI-Werte hat, lebt die Bevölkerung vergleichsweise gut, "
            "während die eigene Regierung oder Währung wenig Machtbindung gewinnt. Wenn MPI hoch und WBI niedrig ist, dominiert Macht "
            "über Wohlbefinden. Wenn WSK fällt, liegt das meist an Mangel, starker UA im Handel oder an auseinanderfallenden GBW-/BUW-/Währungswinkeln. "
            "Die Längen der Währungen bleiben trotzdem unverändert bei 1 VE."))

    # -------------------------------------------------------------------------
    # Exporte
    # -------------------------------------------------------------------------

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
        lines.append("# Abschlussbericht der Winkelwährungswirtschaft\n")
        lines.append(f"Seed: `{self.seed}`  \nTicks: `{self.max_ticks}`  \n")
        lines.append("## Währungen\n")
        lines.append("| Währung | Heimat | Länge | Endwinkel | Anteil zuletzt | Macht |\n")
        lines.append("|---|---:|---:|---:|---:|---:|\n")
        for cur in self.currencies.values():
            lines.append(f"| {cur.code} {cur.name} | {cur.home} | {cur.length:.3f} VE | {cur.angle:.2f}° | {cur.share*100:.2f}% | {cur.macht:.2f} |\n")
        lines.append("\n## Länder\n")
        lines.append("| Land | WBI | MPI | WSK | SPG | Eigene Währung zuletzt |\n")
        lines.append("|---|---:|---:|---:|---:|---:|\n")
        for c in self.countries.values():
            lines.append(f"| {c.code} {c.name} | {c.wbi:.2f} | {c.mpi:.2f} | {c.wsk:.2f} | {c.spg:.2f} | {c.last_currency_mix.get(c.currency, 0)*100:.2f}% |\n")
        lines.append("\n## Deutung\n")
        lines.append("Die Simulation maximiert keinen Reichtum. Sie verfolgt Machtbindung, Wohlbefinden und Wirtschaftsstärke unter Winkelspannung. Alle drei Währungen behalten dieselbe Vektorlänge von 1 VE; die Konkurrenz entsteht durch Winkel.\n")
        with open(path, "w", encoding="utf-8") as f:
            f.write("".join(lines))

# -----------------------------------------------------------------------------
# 5. CLI
# -----------------------------------------------------------------------------


def parse_args(argv: List[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="Bunte Simulation einer Winkelwährungswirtschaft mit 3 gleich langen Euro-Vektorwährungen.")
    p.add_argument("--ticks", type=int, default=18, help="Anzahl Simulationsperioden. Standard: 18")
    p.add_argument("--seed", type=int, default=7, help="Zufallsseed für reproduzierbare Winkel. Standard: 7")
    p.add_argument("--detail", choices=["kurz", "mittel", "voll"], default="voll",
                   help="Ausgabedetail für Markttabellen. Standard: voll")
    p.add_argument("--bericht-jeder", type=int, default=1,
                   help="Nur jeden n-ten Tick ausführlich ausgeben. Standard: 1")
    p.add_argument("--breite", type=int, default=118, help="Textbreite der Ausgabe. Standard: 118")
    p.add_argument("--ohne-farbe", action="store_true", help="ANSI-Farben ausschalten.")
    p.add_argument("--ohne-erklaerungen", action="store_true", help="Handbuch/Erklärblöcke am Anfang überspringen.")
    p.add_argument("--nur-handbuch", action="store_true", help="Nur Modellhandbuch ausgeben, keine Simulation laufen lassen.")
    p.add_argument("--export-csv", default="", help="Pfad für Länder-Verlauf als CSV.")
    p.add_argument("--export-waehrungen-csv", default="", help="Pfad für Währungs-Verlauf als CSV.")
    p.add_argument("--export-md", default="", help="Pfad für Abschlussbericht als Markdown.")
    return p.parse_args(argv)


def main(argv: List[str]) -> int:
    args = parse_args(argv)
    sim = AngularEconomy(seed=args.seed, ticks=max(1, args.ticks), detail=args.detail,
                         bericht_jeder=max(1, args.bericht_jeder), breite=max(80, args.breite),
                         colors=not args.ohne_farbe, erklaerungen=not args.ohne_erklaerungen)
    if args.nur_handbuch:
        sim.print_header()
        sim.print_manual()
        return 0
    sim.run()
    if args.export_csv:
        sim.export_csv(args.export_csv)
        print(col(f"\nCSV exportiert: {args.export_csv}", Ansi.BRIGHT_GREEN))
    if args.export_waehrungen_csv:
        sim.export_currency_csv(args.export_waehrungen_csv)
        print(col(f"CSV Währungen exportiert: {args.export_waehrungen_csv}", Ansi.BRIGHT_GREEN))
    if args.export_md:
        sim.export_markdown(args.export_md)
        print(col(f"Markdownbericht exportiert: {args.export_md}", Ansi.BRIGHT_GREEN))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
