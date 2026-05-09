#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Relational Currency Economy / Relationale Währungsökonomie
Ultra-color UTF-8 simulation for PyPy3 and Python 3.

The program simulates an economy whose currency is not a single number.
The currency is a structured bundle of relations: rights, duties, claims,
risks, time windows, legal limits, labour safeguards, ecological burdens,
credit quality, social shields and market compatibility.

Run:
    pypy3 rwoe_ultra_color_utf8_simulation.py
    pypy3 rwoe_ultra_color_utf8_simulation.py --lang de
    pypy3 rwoe_ultra_color_utf8_simulation.py --parts 1,4,7-9
    pypy3 rwoe_ultra_color_utf8_simulation.py --no-color

No external packages. Standard library only.
"""
from __future__ import print_function

import argparse
import math
import random
import re
import shutil
import sys
import textwrap
from typing import Dict, Iterable, List, Sequence, Tuple

try:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ---------------------------------------------------------------------------
# Global switches
# ---------------------------------------------------------------------------

USE_COLOR = True
LANG = "en"
WIDTH = 104
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")
ACTIVE_ABBRS = {}
ACTIVE_UNITS = []

# Many bright 256-color values. Every multi-letter abbreviation receives a
# deterministic color. Units are rendered as small color pills.
ABBR_PALETTE = [
    196, 202, 208, 214, 220, 226, 190, 154, 118, 82, 46, 48, 51, 45, 39,
    33, 27, 63, 99, 135, 141, 171, 201, 207, 213, 129, 93, 57, 177, 219,
]
UNIT_PALETTE = [229, 224, 223, 222, 221, 220, 159, 153, 147, 117, 111, 105]

# Some recurring abbreviations have fixed colors so their appearance remains
# stable across parts where they occur.
FIXED_ABBR_COLORS = {
    "RCE": 201, "RWÖ": 201, "RVB": 51, "RWB": 51,
    "ME": 214, "MW": 214, "BID": 82, "ASK": 203, "FIT": 226,
    "LCS": 118, "ASS": 118, "TCR": 196, "HCP": 198,
    "LBG": 45, "RGT": 45, "BRS": 87, "GRS": 87,
    "CBC": 39, "ZBK": 39, "ECO": 154, "UMK": 154,
}

FIXED_UNIT_COLORS = {
    "rel": 229, "rels": 229, "Rel": 229,
    "h": 159, "Std": 159,
    "d": 117, "Tg": 117,
    "kgCO2": 190,
    "kWh": 221,
    "%": 224,
    "pts": 213, "Pkt": 213,
    "tx": 153,
    "claims": 222, "Anspr": 222,
    "jobs": 120, "Arb": 120,
    "rights": 147, "Rechte": 147,
    "risks": 210, "Risiken": 210,
    "units": 183, "Einheiten": 183,
}

# ---------------------------------------------------------------------------
# Language helpers
# ---------------------------------------------------------------------------

TXT = {
    "en": {
        "program_title": "Relational Currency Economy — ultra-color Unicode simulation",
        "program_subtitle": "Currency is shown as structured relations, not as one plain number.",
        "part": "Simulation part",
        "what": "What is simulated",
        "why": "Why this is simulated",
        "abbr": "Abbreviations used in this part only",
        "unit": "Units colored in this part",
        "diagram": "Colored Unicode diagram",
        "scenarios": "Scenario run",
        "evaluation": "Evaluation of the simulated outcomes",
        "reading": "How to read this part",
        "result": "Result",
        "scenario": "Scenario",
        "value": "Value",
        "score": "Score",
        "risk": "Risk",
        "boom": "Boom",
        "freedom": "Freedom",
        "guarded": "Guarded",
        "open": "Open",
        "spec": "Speculative",
        "dark": "Dark",
        "green": "Green",
        "shock": "Shock",
        "fragile": "Fragile",
        "strict": "Strict",
        "balanced": "Balanced",
        "wild": "Wild",
        "best_balance": "Best balance",
        "highest_boom": "Highest boom",
        "highest_risk": "Highest dignity risk",
        "lowest_crisis": "Lowest crisis pressure",
        "stronger_than_me": "Why this is stronger than a plain market economy",
        "price": "The price of that strength",
        "not_moral_advice": "The dark scenario is simulated to expose the danger, not to endorse it.",
        "legend_hint": "Only the abbreviations that actually occur below are explained here.",
        "unit_hint": "Units are visual markers; they are not the currency itself.",
        "footer": "End of simulation. The model is illustrative, not a real policy recommendation.",
    },
    "de": {
        "program_title": "Relationale Währungsökonomie — ultra-bunte Unicode-Simulation",
        "program_subtitle": "Währung erscheint als strukturierte Relation, nicht als einzelne Zahl.",
        "part": "Simulationsteil",
        "what": "Was simuliert wird",
        "why": "Warum das simuliert wird",
        "abbr": "Kürzel, die nur in diesem Teil vorkommen",
        "unit": "Einheiten, die in diesem Teil farbig markiert werden",
        "diagram": "Bunte Unicode-Grafik",
        "scenarios": "Szenario-Lauf",
        "evaluation": "Auswertung der simulierten Ergebnisse",
        "reading": "Wie dieser Teil zu lesen ist",
        "result": "Ergebnis",
        "scenario": "Szenario",
        "value": "Wert",
        "score": "Punktwert",
        "risk": "Risiko",
        "boom": "Boom",
        "freedom": "Freiheit",
        "guarded": "Geschützt",
        "open": "Offen",
        "spec": "Spekulativ",
        "dark": "Dunkel",
        "green": "Grün",
        "shock": "Schock",
        "fragile": "Fragil",
        "strict": "Streng",
        "balanced": "Ausgewogen",
        "wild": "Wild",
        "best_balance": "Bestes Gleichgewicht",
        "highest_boom": "Stärkster Boom",
        "highest_risk": "Höchstes Würderisiko",
        "lowest_crisis": "Geringster Krisendruck",
        "stronger_than_me": "Warum dies stärker als eine bloße Marktwirtschaft ist",
        "price": "Der Preis dieser Stärke",
        "not_moral_advice": "Das dunkle Szenario wird simuliert, um die Gefahr sichtbar zu machen, nicht um sie zu befürworten.",
        "legend_hint": "Hier werden wirklich nur die Kürzel erklärt, die unten in diesem Teil vorkommen.",
        "unit_hint": "Einheiten sind sichtbare Markierungen; sie sind nicht selbst die Währung.",
        "footer": "Ende der Simulation. Das Modell ist veranschaulichend und keine reale Politikempfehlung.",
    },
}


def L(key: str) -> str:
    return TXT[LANG][key]


def cur_abbr() -> str:
    return "RCE" if LANG == "en" else "RWÖ"


def bundle_abbr() -> str:
    return "RVB" if LANG == "en" else "RWB"


def market_abbr() -> str:
    return "ME" if LANG == "en" else "MW"

# ---------------------------------------------------------------------------
# ANSI and layout helpers
# ---------------------------------------------------------------------------


def ansi(text, fg=None, bg=None, bold=False, dim=False, underline=False):
    if not USE_COLOR:
        return str(text)
    codes = []
    if bold:
        codes.append("1")
    if dim:
        codes.append("2")
    if underline:
        codes.append("4")
    if fg is not None:
        codes.append("38;5;%s" % int(fg))
    if bg is not None:
        codes.append("48;5;%s" % int(bg))
    if not codes:
        return str(text)
    return "\033[%sm%s\033[0m" % (";".join(codes), str(text))


def strip_ansi(text: str) -> str:
    return ANSI_RE.sub("", str(text))


def vlen(text: str) -> int:
    return len(strip_ansi(str(text)))


def pad(text, width, align="left"):
    s = str(text)
    gap = max(0, width - vlen(s))
    if align == "right":
        return " " * gap + s
    if align == "center":
        left = gap // 2
        return " " * left + s + " " * (gap - left)
    return s + " " * gap


def wrap_lines(text: str, width: int) -> List[str]:
    lines = []
    for para in str(text).split("\n"):
        if not para.strip():
            lines.append("")
        else:
            lines.extend(textwrap.wrap(para, width=width, replace_whitespace=False))
    return lines


def abbr_color(token: str, abbrs: Dict[str, str]) -> int:
    if token in FIXED_ABBR_COLORS:
        return FIXED_ABBR_COLORS[token]
    keys = list(abbrs.keys())
    try:
        idx = keys.index(token)
    except ValueError:
        idx = abs(hash(token))
    return ABBR_PALETTE[idx % len(ABBR_PALETTE)]


def unit_color(unit: str, units: Sequence[Tuple[str, str]]) -> int:
    if unit in FIXED_UNIT_COLORS:
        return FIXED_UNIT_COLORS[unit]
    keys = [u for u, _ in units]
    try:
        idx = keys.index(unit)
    except ValueError:
        idx = abs(hash(unit))
    return UNIT_PALETTE[idx % len(UNIT_PALETTE)]


def c_abbr(token: str, abbrs: Dict[str, str]) -> str:
    return ansi(token, fg=abbr_color(token, abbrs), bold=True)


def c_unit(unit: str, units: Sequence[Tuple[str, str]]) -> str:
    return ansi(unit, fg=16, bg=unit_color(unit, units), bold=True)


def paint(text: str, abbrs: Dict[str, str], units: Sequence[Tuple[str, str]]) -> str:
    """Color only abbreviations and units declared for the current part."""
    s = str(text)
    repl = {}
    for token in abbrs.keys():
        repl[token] = c_abbr(token, abbrs)
    for unit, _ in units:
        repl[unit] = c_unit(unit, units)
    if not repl:
        return s
    # Sort longest first. Look-around avoids coloring inside longer words.
    pattern = re.compile(r"(?<![A-Za-z0-9_ÄÖÜäöüß])(" + "|".join(re.escape(k) for k in sorted(repl, key=len, reverse=True)) + r")(?![A-Za-z0-9_ÄÖÜäöüß])")
    return pattern.sub(lambda m: repl[m.group(1)], s)


def rainbow_rule(width: int = None) -> str:
    if width is None:
        width = WIDTH
    if not USE_COLOR:
        return "=" * width
    colors = [196, 202, 208, 214, 220, 226, 190, 154, 118, 82, 46, 48, 51, 45, 39, 33, 27, 63, 99, 135, 171, 201]
    return "".join(ansi("█", fg=colors[i % len(colors)], bold=True) for i in range(width))


def thin_rule(width: int = None) -> str:
    if width is None:
        width = WIDTH
    if not USE_COLOR:
        return "-" * width
    colors = [39, 45, 51, 87, 123, 159, 195]
    return "".join(ansi("─", fg=colors[i % len(colors)]) for i in range(width))


def title_box(title: str, subtitle: str = "", width: int = None) -> str:
    if width is None:
        width = WIDTH
    out = [rainbow_rule(width)]
    out.append(ansi("╔" + "═" * (width - 2) + "╗", fg=15, bg=54, bold=True))
    out.append(ansi("║" + pad(fit_visible("  " + title + "  ", width - 2), width - 2, "center") + "║", fg=15, bg=54, bold=True))
    if subtitle:
        out.append(ansi("║" + pad(fit_visible("  " + subtitle + "  ", width - 2), width - 2, "center") + "║", fg=225, bg=54))
    out.append(ansi("╚" + "═" * (width - 2) + "╝", fg=15, bg=54, bold=True))
    out.append(rainbow_rule(width))
    return "\n".join(out)


def section_box(label: str, body: str, abbrs: Dict[str, str], units: Sequence[Tuple[str, str]], fg=15, bg=23, width: int = None) -> str:
    if width is None:
        width = WIDTH
    lines = [ansi("╭" + "─" * (width - 2) + "╮", fg=fg, bg=bg, bold=True)]
    lines.append(ansi("│" + pad("  " + label + "  ", width - 2, "center") + "│", fg=fg, bg=bg, bold=True))
    lines.append(ansi("├" + "─" * (width - 2) + "┤", fg=fg, bg=bg, bold=True))
    for line in wrap_lines(paint(body, abbrs, units), width - 6):
        lines.append(ansi("│", fg=fg, bg=bg) + "  " + pad(line, width - 6) + "  " + ansi("│", fg=fg, bg=bg))
    lines.append(ansi("╰" + "─" * (width - 2) + "╯", fg=fg, bg=bg, bold=True))
    return "\n".join(lines)


def table(headers: Sequence[str], rows: Sequence[Sequence[str]], align: Sequence[str] = None, title: str = "") -> str:
    if align is None:
        align = ["left"] * len(headers)
    # Paint only the abbreviations and units declared for the currently running part.
    if ACTIVE_ABBRS or ACTIVE_UNITS:
        title = paint(title, ACTIVE_ABBRS, ACTIVE_UNITS) if title else title
        headers = [paint(str(h), ACTIVE_ABBRS, ACTIVE_UNITS) for h in headers]
        rows = [[paint(str(c), ACTIVE_ABBRS, ACTIVE_UNITS) for c in row] for row in rows]
    all_rows = [headers] + list(rows)
    widths = [0] * len(headers)
    for row in all_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], vlen(cell))
    sep = "┼".join("─" * (w + 2) for w in widths)
    out = []
    if title:
        out.append(ansi(title, fg=213, bold=True, underline=True))
    out.append(ansi("┌" + "┬".join("─" * (w + 2) for w in widths) + "┐", fg=39))
    out.append(ansi("│", fg=39) + ansi("│", fg=39).join(" " + ansi(pad(headers[i], widths[i], "center"), fg=15, bg=60, bold=True) + " " for i in range(len(headers))) + ansi("│", fg=39))
    out.append(ansi("├" + sep + "┤", fg=39))
    for row in rows:
        cells = []
        for i, cell in enumerate(row):
            cells.append(" " + pad(cell, widths[i], align[i] if i < len(align) else "left") + " ")
        out.append(ansi("│", fg=39) + ansi("│", fg=39).join(cells) + ansi("│", fg=39))
    out.append(ansi("└" + "┴".join("─" * (w + 2) for w in widths) + "┘", fg=39))
    return "\n".join(out)


def bar(value: float, maximum: float = 100.0, width: int = 28, good: bool = True) -> str:
    value = max(0.0, min(float(maximum), float(value)))
    filled = int(round(width * value / maximum)) if maximum else 0
    empty = width - filled
    if not USE_COLOR:
        return "[" + "#" * filled + "." * empty + "] %3d" % round(value)
    if good:
        col = 46 if value >= 70 else (226 if value >= 40 else 196)
    else:
        col = 196 if value >= 70 else (208 if value >= 40 else 46)
    return "[" + ansi("█" * filled, fg=col, bold=True) + ansi("░" * empty, fg=238) + "] %3d" % round(value)


def mini_bar(value: float, maximum: float, width: int, color: int) -> str:
    value = max(0.0, min(float(maximum), float(value)))
    n = int(round(width * value / maximum)) if maximum else 0
    if not USE_COLOR:
        return "#" * n + "." * (width - n)
    return ansi("█" * n, fg=color, bold=True) + ansi("░" * (width - n), fg=238)


def num(value, unit: str, units: Sequence[Tuple[str, str]], digits=0) -> str:
    if isinstance(value, float) and digits > 0:
        s = ("%%.%df" % digits) % value
    else:
        s = str(int(round(value))) if isinstance(value, (int, float)) else str(value)
    return s + " " + c_unit(unit, units)


def spark(values: Sequence[float], width: int = 32) -> str:
    if not values:
        return ""
    blocks = "▁▂▃▄▅▆▇█"
    mn = min(values)
    mx = max(values)
    if mx == mn:
        idxs = [3 for _ in values]
    else:
        idxs = [int(round((len(blocks) - 1) * (v - mn) / (mx - mn))) for v in values]
    if len(idxs) > width:
        step = float(len(idxs)) / width
        idxs = [idxs[int(i * step)] for i in range(width)]
    if not USE_COLOR:
        return "".join(blocks[i] for i in idxs)
    colors = [196, 202, 208, 214, 220, 226, 190, 154]
    return "".join(ansi(blocks[i], fg=colors[i], bold=True) for i in idxs)


def heat_cell(value: float, maximum: float = 100.0, width: int = 3, invert: bool = False) -> str:
    value = max(0.0, min(maximum, value))
    ratio = value / maximum if maximum else 0.0
    if invert:
        ratio = 1.0 - ratio
    if not USE_COLOR:
        chars = " .:-=+*#%@"
        return chars[int(ratio * (len(chars) - 1))] * width
    scale = [196, 202, 208, 214, 220, 226, 118, 82, 46]
    col = scale[int(ratio * (len(scale) - 1))]
    return ansi("█" * width, fg=col, bold=True)


def matrix(labels_x: Sequence[str], labels_y: Sequence[str], values: Sequence[Sequence[float]], title: str = "", invert: bool = False) -> str:
    rows = []
    xw = max(5, min(13, max(vlen(x) for x in labels_x))) if labels_x else 5
    yw = max(8, min(14, max(vlen(y) for y in labels_y))) if labels_y else 8

    def fit_label(x, w):
        raw = strip_ansi(str(x))
        if len(raw) <= w:
            return str(x)
        return raw[:w - 1] + "…"

    head = " " * (yw + 1) + " ".join(pad(fit_label(x, xw), xw, "center") for x in labels_x)
    rows.append(ansi(title, fg=213, bold=True, underline=True) if title else "")
    rows.append(head)
    for y, row in zip(labels_y, values):
        cells = " ".join(pad(heat_cell(v, invert=invert), xw, "center") for v in row)
        rows.append(pad(fit_label(y, yw), yw, "right") + " " + cells)
    return "\n".join([r for r in rows if r != ""])


def line_art(lines: Sequence[str], abbrs: Dict[str, str], units: Sequence[Tuple[str, str]]) -> str:
    return "\n".join(paint(x, abbrs, units) for x in lines)


def legend_abbr(abbrs: Dict[str, str], units: Sequence[Tuple[str, str]]) -> str:
    rows = []
    for key, desc in abbrs.items():
        rows.append([c_abbr(key, abbrs), paint(desc, abbrs, units)])
    return table(["Code" if LANG == "en" else "Kürzel", "Meaning" if LANG == "en" else "Bedeutung"], rows, ["left", "left"], L("abbr"))


def legend_units(units: Sequence[Tuple[str, str]]) -> str:
    rows = [[c_unit(unit, units), desc] for unit, desc in units]
    return table(["Unit" if LANG == "en" else "Einheit", "Meaning" if LANG == "en" else "Bedeutung"], rows, ["left", "left"], L("unit"))

# ---------------------------------------------------------------------------
# Scenario model
# ---------------------------------------------------------------------------

BASE_SCENARIOS = [
    {
        "key": "guarded", "market": 0.55, "state": 0.86, "data": 0.50, "commod": 0.18,
        "trust": 0.78, "debt": 0.34, "ecology": 0.75, "shock": 0.10, "labor": 0.84,
        "platform": 0.42, "interoperability": 0.72, "external": 0.30,
    },
    {
        "key": "open", "market": 0.78, "state": 0.58, "data": 0.72, "commod": 0.38,
        "trust": 0.67, "debt": 0.48, "ecology": 0.48, "shock": 0.18, "labor": 0.55,
        "platform": 0.62, "interoperability": 0.58, "external": 0.45,
    },
    {
        "key": "spec", "market": 0.92, "state": 0.36, "data": 0.88, "commod": 0.62,
        "trust": 0.52, "debt": 0.76, "ecology": 0.34, "shock": 0.32, "labor": 0.31,
        "platform": 0.78, "interoperability": 0.42, "external": 0.63,
    },
    {
        "key": "dark", "market": 0.96, "state": 0.18, "data": 0.96, "commod": 0.91,
        "trust": 0.37, "debt": 0.86, "ecology": 0.22, "shock": 0.47, "labor": 0.12,
        "platform": 0.92, "interoperability": 0.25, "external": 0.82,
    },
]


def scenario_name(s: Dict[str, float]) -> str:
    return L(s["key"])


def clamp(x: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, x))


def rng_for(seed: int, part: int, scenario_idx: int) -> random.Random:
    return random.Random(seed * 1009 + part * 101 + scenario_idx * 17)


def jitter(rng: random.Random, spread: float = 3.0) -> float:
    return rng.uniform(-spread, spread)


def core_metrics(s: Dict[str, float], rng: random.Random) -> Dict[str, float]:
    market = s["market"]
    state = s["state"]
    data = s["data"]
    commod = s["commod"]
    trust = s["trust"]
    debt = s["debt"]
    ecology = s["ecology"]
    shock = s["shock"]
    labor = s["labor"]
    platform = s["platform"]
    interop = s["interoperability"]
    external = s["external"]

    transparency = clamp(18 + 52 * data + 24 * state + 12 * trust - 10 * platform + jitter(rng, 2))
    liquidity = clamp(14 + 58 * market + 23 * data + 17 * trust + 10 * interop - 18 * shock - 12 * state + jitter(rng, 3))
    productivity = clamp(20 + 43 * market + 20 * data + 20 * trust + 10 * interop - 12 * shock + jitter(rng, 3))
    dignity_risk = clamp(9 + 55 * commod + 25 * debt + 25 * data + 20 * platform - 40 * state - 28 * labor + jitter(rng, 3))
    crisis_risk = clamp(12 + 42 * debt + 28 * shock + 22 * market + 15 * platform - 34 * state - 20 * trust + jitter(rng, 3))
    ecology_balance = clamp(15 + 62 * ecology + 22 * state - 20 * market - 24 * external + jitter(rng, 3))
    inclusion = clamp(16 + 42 * state + 30 * labor + 19 * interop - 19 * commod - 9 * platform + jitter(rng, 3))
    control_power = clamp(10 + 45 * platform + 32 * data + 24 * commod + 15 * debt - 25 * state + jitter(rng, 3))
    boom = clamp(0.36 * liquidity + 0.35 * productivity + 20 * market + 8 * data - 0.25 * crisis_risk - 0.10 * dignity_risk + jitter(rng, 3))
    freedom = clamp(88 - dignity_risk - 0.28 * control_power + 0.30 * inclusion + 8 * state + jitter(rng, 2))
    return {
        "transparency": transparency,
        "liquidity": liquidity,
        "productivity": productivity,
        "dignity_risk": dignity_risk,
        "crisis_risk": crisis_risk,
        "ecology_balance": ecology_balance,
        "inclusion": inclusion,
        "control_power": control_power,
        "boom": boom,
        "freedom": freedom,
    }


def scenario_results(seed: int, part: int, tweak=None) -> List[Dict[str, float]]:
    out = []
    for idx, base in enumerate(BASE_SCENARIOS):
        s = dict(base)
        if tweak:
            tweak(s, idx)
        rng = rng_for(seed, part, idx)
        m = core_metrics(s, rng)
        m["scenario"] = scenario_name(s)
        m["key"] = s["key"]
        for _k in ("market", "state", "data", "commod", "trust", "debt", "ecology", "shock", "labor", "platform", "interoperability", "external"):
            m[_k] = s[_k]
        # A few count-like values used by diagrams and tables.
        m["relations"] = int(round(20 + 80 * s["market"] + 45 * s["data"] + rng.uniform(-5, 6)))
        m["claims"] = int(round(10 + 50 * s["debt"] + 35 * s["market"] + rng.uniform(-4, 5)))
        m["jobs"] = int(round(12 + 55 * s["labor"] + 20 * s["market"] + rng.uniform(-3, 4)))
        m["hours"] = int(round(80 + 140 * s["market"] + 50 * s["labor"] + rng.uniform(-10, 11)))
        m["kwh"] = int(round(600 + 450 * s["market"] + 300 * (1 - s["ecology"]) + rng.uniform(-40, 41)))
        m["kgco2"] = int(round(220 + 460 * s["external"] + 280 * (1 - s["ecology"]) + rng.uniform(-30, 31)))
        out.append(m)
    return out


def pick_max(rows: List[Dict[str, float]], key: str) -> Dict[str, float]:
    return max(rows, key=lambda r: r[key])


def pick_min(rows: List[Dict[str, float]], key: str) -> Dict[str, float]:
    return min(rows, key=lambda r: r[key])


def pick_balance(rows: List[Dict[str, float]]) -> Dict[str, float]:
    # Balance rewards boom, inclusion, ecology and freedom, and penalizes risk.
    def score(r):
        return (0.25 * r["boom"] + 0.22 * r["inclusion"] + 0.20 * r["freedom"] +
                0.18 * r["ecology_balance"] + 0.15 * r["transparency"] -
                0.22 * r["dignity_risk"] - 0.18 * r["crisis_risk"])
    return max(rows, key=score)


def scenario_table(rows: List[Dict[str, float]], units: Sequence[Tuple[str, str]], mode: str = "general") -> str:
    if mode == "risk":
        headers = [L("scenario"), "Boom", "Human risk" if LANG == "en" else "Menschenrisiko", "Control" if LANG == "en" else "Kontrolle", "Freedom" if LANG == "en" else "Freiheit"]
        data = []
        for r in rows:
            data.append([r["scenario"], bar(r["boom"], good=True), bar(r["dignity_risk"], good=False), bar(r["control_power"], good=False), bar(r["freedom"], good=True)])
        return table(headers, data, ["left", "left", "left", "left", "left"], L("scenarios"))
    if mode == "eco":
        headers = [L("scenario"), "ECO" if LANG == "en" else "UMK", "Energy" if LANG == "en" else "Energie", "Burden" if LANG == "en" else "Last", "Boom"]
        data = []
        for r in rows:
            data.append([r["scenario"], bar(r["ecology_balance"], good=True), num(r["kwh"], "kWh", units), num(r["kgco2"], "kgCO2", units), bar(r["boom"], good=True)])
        return table(headers, data, ["left", "left", "right", "right", "left"], L("scenarios"))
    if mode == "counts":
        unit_set = set(u for u, _ in units)
        rel_unit = "rels" if "rels" in unit_set else ("Rel" if "Rel" in unit_set else None)
        claim_unit = "claims" if "claims" in unit_set else ("Anspr" if "Anspr" in unit_set else None)
        job_unit = "jobs" if "jobs" in unit_set else ("Arb" if "Arb" in unit_set else None)
        tx_unit = "tx" if "tx" in unit_set else None
        day_unit = "d" if "d" in unit_set else ("Tg" if "Tg" in unit_set else None)
        pts_unit = "pts" if "pts" in unit_set else ("Pkt" if "Pkt" in unit_set else None)

        columns = []
        if rel_unit:
            columns.append(("Relations" if LANG == "en" else "Relationen", lambda r: num(r["relations"], rel_unit, units)))
        if claim_unit:
            columns.append(("Claims" if LANG == "en" else "Ansprüche", lambda r: num(r["claims"], claim_unit, units)))
        elif tx_unit:
            columns.append(("Transactions" if LANG == "en" else "Transaktionen", lambda r: num(max(1, int(r["liquidity"] / 3)), tx_unit, units)))
        elif pts_unit:
            columns.append(("Activation" if LANG == "en" else "Aktivierung", lambda r: num(r["boom"], pts_unit, units)))
        if job_unit:
            columns.append(("Jobs" if LANG == "en" else "Arbeit", lambda r: num(r["jobs"], job_unit, units)))
        elif day_unit:
            columns.append(("Validity" if LANG == "en" else "Gültigkeit", lambda r: num(20 + r["transparency"] / 2, day_unit, units)))
        elif tx_unit:
            columns.append(("Cleared" if LANG == "en" else "Verrechnet", lambda r: num(max(1, int(r["boom"] / 4)), tx_unit, units)))
        elif pts_unit:
            columns.append(("Strength" if LANG == "en" else "Stärke", lambda r: num(r["productivity"], pts_unit, units)))
        headers = [L("scenario")] + [c[0] for c in columns] + ["Liquidity" if LANG == "en" else "Liquidität"]
        data = []
        for r in rows:
            data.append([r["scenario"]] + [c[1](r) for c in columns] + [bar(r["liquidity"], good=True)])
        return table(headers, data, ["left"] + ["right"] * len(columns) + ["left"], L("scenarios"))
    headers = [L("scenario"), "Liquidity" if LANG == "en" else "Liquidität", "Boom", "Crisis" if LANG == "en" else "Krise", "Freedom" if LANG == "en" else "Freiheit"]
    data = []
    for r in rows:
        data.append([r["scenario"], bar(r["liquidity"], good=True), bar(r["boom"], good=True), bar(r["crisis_risk"], good=False), bar(r["freedom"], good=True)])
    return table(headers, data, ["left", "left", "left", "left", "left"], L("scenarios"))


def outcome_summary(rows: List[Dict[str, float]], abbrs: Dict[str, str], units: Sequence[Tuple[str, str]], focus: str = "general") -> str:
    high_boom = pick_max(rows, "boom")
    high_risk = pick_max(rows, "dignity_risk")
    low_crisis = pick_min(rows, "crisis_risk")
    balance = pick_balance(rows)
    if LANG == "en":
        base = (
            f"{L('highest_boom')}: {high_boom['scenario']} with {high_boom['boom']:.0f} pts. "
            f"{L('highest_risk')}: {high_risk['scenario']} with {high_risk['dignity_risk']:.0f} pts. "
            f"{L('lowest_crisis')}: {low_crisis['scenario']} with {low_crisis['crisis_risk']:.0f} pts. "
            f"{L('best_balance')}: {balance['scenario']}. "
            "The pattern is deliberate: once relations become easier to trade, productivity and liquidity rise; once legal gates weaken, control power and human-risk also rise."
        )
    else:
        base = (
            f"{L('highest_boom')}: {high_boom['scenario']} mit {high_boom['boom']:.0f} Pkt. "
            f"{L('highest_risk')}: {high_risk['scenario']} mit {high_risk['dignity_risk']:.0f} Pkt. "
            f"{L('lowest_crisis')}: {low_crisis['scenario']} mit {low_crisis['crisis_risk']:.0f} Pkt. "
            f"{L('best_balance')}: {balance['scenario']}. "
            "Das Muster ist gewollt: Wenn Relationen leichter handelbar werden, steigen Produktivität und Liquidität; wenn rechtliche Tore schwächer werden, steigen Kontrollmacht und Menschenrisiko ebenfalls."
        )
    return paint(base, abbrs, units)

# ---------------------------------------------------------------------------
# Part metadata and language-localized abbreviations
# ---------------------------------------------------------------------------


def A(part: int) -> Dict[str, str]:
    C = cur_abbr()
    B = bundle_abbr()
    M = market_abbr()
    if LANG == "en":
        data = {
            1: {
                C: "Relational Currency Economy: the whole system in which currency is a structured relation bundle instead of one number.",
                B: "Relational Value Bundle: a tradable table of claims, duties, risks, time windows and proofs.",
                "RID": "Relation identifier: the traceable label of one row inside the bundle.",
                "VAL": "Validity layer: the part that says whether a relation is lawful, current and enforceable.",
            },
            2: {
                "MME": "Market Matching Engine: the simulated market device that connects offers and demands by relation compatibility.",
                "ASK": "Ask table: what a seller is willing to accept as a bundle.",
                "BID": "Bid table: what a buyer can transfer as a bundle.",
                "FIT": "Fit score: the compatibility between one ask table and one bid table.",
            },
            3: {
                "PCN": "Production Chain Network: the web of inputs, labour, machines, delivery duties and output claims.",
                "CAP": "Capacity relation: usable productive ability such as machine time or skilled labour.",
                "WIP": "Work in progress: goods or services that are not finished but already carry relations.",
                "THR": "Throughput: how much useful output flows through the chain per step.",
            },
            4: {
                "LCS": "Labor Contract Shield: the rule layer that protects a worker from being turned into a tradable person.",
                "WKR": "Worker relation: a voluntary, limited work promise, not ownership of a human being.",
                "EMP": "Employer relation: a duty to pay, protect and respect the agreed limits.",
                "NTR": "Non-transfer rule: the worker cannot be sold by transferring the whole human relation bundle.",
            },
            5: {
                "CRT": "Credit Relation Transformer: the bank-like module that turns future claims into more liquid bundles.",
                "COL": "Collateral layer: relations pledged as security for a future obligation.",
                "DRF": "Default risk factor: the probability pressure that promised relations may fail.",
                "SEN": "Seniority rank: the order in which claims are served during failure.",
            },
            6: {
                "LBM": "Liquidity Boom Meter: the simulated gauge for how much hidden relation value becomes tradable.",
                "HVA": "Hidden value activation: the conversion of unused time, trust, rights and micro-claims into marketable bundles.",
                "VEL": "Velocity of relations: how quickly bundles circulate through transactions.",
                "ABS": "Absorption strain: the overload created when too many relations are traded too quickly.",
            },
            7: {
                "DME": "Dark Market Exposure: the simulated exposure to markets that trade domination rather than useful service.",
                "TCR": "Total commodification risk: the danger that every human dependency becomes a market object.",
                "HCP": "Human control portfolio: a toxic bundle of work, debt, housing, data and reputation control.",
                "OVB": "Overbinding: too many life relations are tied to one counterparty.",
            },
            8: {
                "LBG": "Legal Boundary Gate: the state rule gate that decides which relations may become currency.",
                "IAL": "Inalienable layer: rights and freedoms that cannot be sold, pledged or bundled.",
                "SPL": "Split rule: a legal command to separate work, housing, debt, data and residence control.",
                "BAN": "Ban list: relations that are rejected even if a market would profit from them.",
            },
            9: {
                "ECO": "Ecological carry-on: the environmental relation attached to every product and duty.",
                "EMS": "Emission strand: the burden relation carried by energy use, production or transport.",
                "REG": "Regeneration claim: a relation that restores soil, water, air or biodiversity.",
                "LIM": "Limit line: a non-tradable ecological boundary that cannot be bought away.",
            },
            10: {
                "CBC": "Central Bank Circuit: the public circuit that tests relation quality, guarantees safe bundles and quarantines toxic ones.",
                "QFR": "Quality floor rating: the minimum level a relation bundle needs before broad circulation.",
                "CRK": "Crisis kink: the point where trust collapses and many bundles stop clearing.",
                "GRT": "Guarantee rail: the public path that keeps basic payments and duties moving during crisis.",
            },
            11: {
                "BRS": "Basic Relation Shield: public minimum relations for housing, health, education, legal access and participation.",
                "HLT": "Health relation: guaranteed access that prevents sickness from becoming total market exclusion.",
                "EDU": "Education relation: the public path to rebuild skills and future options.",
                "HOU": "Housing relation: a basic shelter claim that protects people from immediate relational collapse.",
            },
            12: {
                "CMP": "Competition Power Map: the diagram of who controls access to relation markets.",
                "MPI": "Monopoly pressure index: the pressure created when one platform controls many relation gates.",
                "INT": "Interoperability rule: the ability to move relations between systems without private captivity.",
                "OPF": "Open protocol floor: the minimum public standard that keeps matching systems contestable.",
            },
            13: {
                "CTL": "Cross-border Translation Layer: the bridge translating one country's relation standards into another's.",
                "STD": "Standard tag: a label for labour, data, ecological and legal quality.",
                "TAR": "Tariff relation: a border duty or permission attached to a traded bundle.",
                "REC": "Recognition score: how much one jurisdiction accepts another jurisdiction's relations.",
            },
            14: {
                C: "Relational Currency Economy: the richer system that trades structured relation bundles.",
                M: "Market Economy: the conventional comparison point that mainly communicates through prices.",
                "INF": "Information depth: how much structure a system reveals beyond a plain price.",
                "DGN": "Dignity guard: the strength of rules that keep persons from becoming market objects.",
                "PRD": "Productive coordination: the system's ability to match resources, duties and needs.",
            },
        }
    else:
        data = {
            1: {
                C: "Relationale Währungsökonomie: das Gesamtsystem, in dem Währung ein strukturiertes Relationenbündel statt einer einzelnen Zahl ist.",
                B: "Relationales Wertbündel: eine handelbare Tabelle aus Ansprüchen, Pflichten, Risiken, Zeitfenstern und Nachweisen.",
                "RID": "Relationskennung: die nachvollziehbare Bezeichnung einer einzelnen Zeile im Bündel.",
                "VAL": "Gültigkeitsschicht: der Teil, der sagt, ob eine Relation rechtmäßig, aktuell und durchsetzbar ist.",
            },
            2: {
                "MME": "Markt-Matching-Engine: die simulierte Markteinheit, die Angebote und Nachfragen nach Relationspassung verbindet.",
                "ASK": "Annahmetabelle: das, was ein Verkäufer als Bündel akzeptieren würde.",
                "BID": "Gebotstabelle: das, was ein Käufer als Bündel übertragen kann.",
                "FIT": "Passungswert: die Übereinstimmung zwischen Annahmetabelle und Gebotstabelle.",
            },
            3: {
                "PCN": "Produktionskettennetz: das Netz aus Eingängen, Arbeit, Maschinen, Lieferpflichten und Ausgangsansprüchen.",
                "CAP": "Kapazitätsrelation: nutzbare Produktionsfähigkeit wie Maschinenzeit oder qualifizierte Arbeit.",
                "WIP": "Zwischenarbeit: unfertige Güter oder Leistungen, die bereits Relationen tragen.",
                "THR": "Durchsatz: wie viel nutzbarer Ausgang pro Schritt durch die Kette fließt.",
            },
            4: {
                "LCS": "Arbeitsschutzschild: die Regelschicht, die verhindert, dass ein Arbeitnehmer zur handelbaren Person wird.",
                "WKR": "Arbeitskraftrelation: ein freiwilliges und begrenztes Arbeitsversprechen, kein Eigentum an einem Menschen.",
                "EMP": "Arbeitgeberrelation: die Pflicht zu Bezahlung, Schutz und Respekt vor den vereinbarten Grenzen.",
                "NTR": "Nichtübertragbarkeitsregel: der Arbeitnehmer darf nicht durch Übertragung des ganzen Menschenbündels verkauft werden.",
            },
            5: {
                "CRT": "Kreditrelationstransformator: das bankartige Modul, das Zukunftsansprüche in liquidere Bündel verwandelt.",
                "COL": "Sicherheitenschicht: Relationen, die zur Absicherung einer Zukunftspflicht verpfändet werden.",
                "DRF": "Ausfallrisikofaktor: der Wahrscheinlichkeitsdruck, dass versprochene Relationen scheitern.",
                "SEN": "Vorrangrang: die Reihenfolge, in der Ansprüche im Scheitern bedient werden.",
            },
            6: {
                "LBM": "Liquiditäts-Boom-Messer: die simulierte Anzeige dafür, wie viel verborgener Relationswert handelbar wird.",
                "HVA": "Aktivierung verborgener Werte: Umwandlung ungenutzter Zeit, Vertrauenswerte, Rechte und Mikroansprüche in marktfähige Bündel.",
                "VEL": "Relationsgeschwindigkeit: wie schnell Bündel durch Transaktionen zirkulieren.",
                "ABS": "Aufnahmespannung: Überlastung, wenn zu viele Relationen zu schnell gehandelt werden.",
            },
            7: {
                "DME": "Dunkelmarkt-Exposition: die simulierte Aussetzung gegenüber Märkten, die Herrschaft statt nützlicher Leistung handeln.",
                "TCR": "Risiko totaler Kommodifizierung: die Gefahr, dass jede menschliche Abhängigkeit zum Marktobjekt wird.",
                "HCP": "Menschenkontrollportfolio: ein toxisches Bündel aus Arbeit, Schuld, Wohnen, Daten und Reputationskontrolle.",
                "OVB": "Überbindung: zu viele Lebensrelationen werden an dieselbe Gegenpartei gekettet.",
            },
            8: {
                "LBG": "Rechtsgrenzentor: das staatliche Regel-Tor, das entscheidet, welche Relationen Währung werden dürfen.",
                "IAL": "Unveräußerliche Schicht: Rechte und Freiheiten, die weder verkauft noch verpfändet noch gebündelt werden dürfen.",
                "SPL": "Spaltungsregel: ein Rechtsbefehl zur Trennung von Arbeit, Wohnen, Schuld, Daten und Aufenthaltskontrolle.",
                "BAN": "Verbotsliste: Relationen, die abgewiesen werden, selbst wenn ein Markt daran verdienen würde.",
            },
            9: {
                "ECO": "Ökologische Mitlast: die Umweltrelation, die jedem Produkt und jeder Pflicht angehängt wird.",
                "EMS": "Emissionsstrang: die Belastungsrelation aus Energieverbrauch, Produktion oder Transport.",
                "REG": "Regenerationsanspruch: eine Relation, die Boden, Wasser, Luft oder Artenvielfalt wiederherstellt.",
                "LIM": "Grenzlinie: eine nicht handelbare ökologische Grenze, die nicht weggekauft werden darf.",
            },
            10: {
                "CBC": "Zentralbankkreislauf: der öffentliche Kreislauf, der Relationsqualität prüft, sichere Bündel garantiert und toxische isoliert.",
                "QFR": "Qualitätsboden: die Mindeststufe, die ein Relationsbündel für breite Zirkulation braucht.",
                "CRK": "Krisenknick: der Punkt, an dem Vertrauen kippt und viele Bündel nicht mehr verrechnet werden.",
                "GRT": "Garantieschiene: der öffentliche Pfad, der Basiszahlungen und Pflichten in der Krise beweglich hält.",
            },
            11: {
                "BRS": "Grundrelationsschild: öffentliche Mindestbeziehungen für Wohnen, Gesundheit, Bildung, Rechtszugang und Teilhabe.",
                "HLT": "Gesundheitsrelation: garantierter Zugang, damit Krankheit nicht zum totalen Marktausschluss wird.",
                "EDU": "Bildungsrelation: der öffentliche Weg, Fähigkeiten und Zukunftsoptionen neu aufzubauen.",
                "HOU": "Wohnrelation: ein grundlegender Schutzanspruch, der Menschen vor sofortigem relationalem Zusammenbruch schützt.",
            },
            12: {
                "CMP": "Wettbewerbsmachtkarte: die Darstellung, wer den Zugang zu Relationsmärkten kontrolliert.",
                "MPI": "Monopoldruckindex: der Druck, der entsteht, wenn eine Plattform viele Relationstore kontrolliert.",
                "INT": "Interoperabilitätsregel: die Fähigkeit, Relationen zwischen Systemen zu bewegen, ohne privat gefangen zu werden.",
                "OPF": "Offener Protokollboden: der öffentliche Mindeststandard, der Matching-Systeme angreifbar und bestreitbar hält.",
            },
            13: {
                "CTL": "Grenzübersetzungs-Schicht: die Brücke, die Relationsstandards eines Landes in die Standards eines anderen übersetzt.",
                "STD": "Standardmarke: ein Kennzeichen für Arbeits-, Daten-, Umwelt- und Rechtsqualität.",
                "TAR": "Zollrelation: eine Grenzpflicht oder Genehmigung, die an einem gehandelten Bündel hängt.",
                "REC": "Anerkennungswert: wie stark eine Rechtsordnung die Relationen einer anderen akzeptiert.",
            },
            14: {
                C: "Relationale Währungsökonomie: das reichere System, das strukturierte Relationenbündel handelt.",
                M: "Marktwirtschaft: der konventionelle Vergleichspunkt, der vor allem über Preise kommuniziert.",
                "INF": "Informationstiefe: wie viel Struktur ein System über einen bloßen Preis hinaus sichtbar macht.",
                "DGN": "Würdewächter: die Stärke von Regeln, die verhindern, dass Personen zu Marktobjekten werden.",
                "PRD": "Produktive Koordination: die Fähigkeit, Ressourcen, Pflichten und Bedürfnisse passend zu verbinden.",
            },
        }
    return data[part]


def U(part: int) -> List[Tuple[str, str]]:
    if LANG == "en":
        data = {
            1: [("rels", "count of relation rows"), ("claims", "count of claim rows"), ("d", "days of validity")],
            2: [("tx", "transactions"), ("rels", "relation rows"), ("pts", "score points")],
            3: [("h", "productive hours"), ("units", "output units"), ("kWh", "energy use")],
            4: [("jobs", "work promises"), ("h", "work hours"), ("pts", "protection points")],
            5: [("claims", "future claims"), ("rels", "collateral relations"), ("pts", "risk points")],
            6: [("rels", "activated relations"), ("tx", "transactions"), ("pts", "strain points")],
            7: [("rels", "controlled relations"), ("h", "bound hours"), ("pts", "human-risk points")],
            8: [("rights", "protected rights"), ("rels", "filtered relations"), ("pts", "boundary points")],
            9: [("kWh", "energy use"), ("kgCO2", "emission burden"), ("rels", "ecological relations")],
            10: [("rels", "bundles tested"), ("claims", "claims supported"), ("pts", "stability points")],
            11: [("rights", "basic rights"), ("jobs", "re-entry work chances"), ("pts", "inclusion points")],
            12: [("rels", "access relations"), ("tx", "platform transactions"), ("pts", "power points")],
            13: [("rels", "translated relations"), ("tx", "cross-border transactions"), ("pts", "recognition points")],
            14: [("pts", "comparison points"), ("rels", "relation rows"), ("%", "relative share")],
        }
    else:
        data = {
            1: [("Rel", "Anzahl der Relationszeilen"), ("Anspr", "Anzahl der Anspruchszeilen"), ("Tg", "Tage Gültigkeit")],
            2: [("tx", "Transaktionen"), ("Rel", "Relationszeilen"), ("Pkt", "Punktwerte")],
            3: [("Std", "produktive Stunden"), ("Einheiten", "Ausgangseinheiten"), ("kWh", "Energieverbrauch")],
            4: [("Arb", "Arbeitsversprechen"), ("Std", "Arbeitsstunden"), ("Pkt", "Schutzpunkte")],
            5: [("Anspr", "Zukunftsansprüche"), ("Rel", "Sicherheitenrelationen"), ("Pkt", "Risikopunkte")],
            6: [("Rel", "aktivierte Relationen"), ("tx", "Transaktionen"), ("Pkt", "Spannungspunkte")],
            7: [("Rel", "kontrollierte Relationen"), ("Std", "gebundene Stunden"), ("Pkt", "Menschenrisiko-Punkte")],
            8: [("Rechte", "geschützte Rechte"), ("Rel", "gefilterte Relationen"), ("Pkt", "Grenzpunkte")],
            9: [("kWh", "Energieverbrauch"), ("kgCO2", "Emissionslast"), ("Rel", "Umweltrelationen")],
            10: [("Rel", "geprüfte Bündel"), ("Anspr", "gestützte Ansprüche"), ("Pkt", "Stabilitätspunkte")],
            11: [("Rechte", "Grundrechte"), ("Arb", "Rückkehr-Arbeitschancen"), ("Pkt", "Teilhabe-Punkte")],
            12: [("Rel", "Zugangsrelationen"), ("tx", "Plattformtransaktionen"), ("Pkt", "Machtpunkte")],
            13: [("Rel", "übersetzte Relationen"), ("tx", "grenzüberschreitende Transaktionen"), ("Pkt", "Anerkennungspunkte")],
            14: [("Pkt", "Vergleichspunkte"), ("Rel", "Relationszeilen"), ("%", "relativer Anteil")],
        }
    return data[part]


def part_title(part: int) -> str:
    en = {
        1: "Anatomy of the relation currency",
        2: "Market matching without a single price",
        3: "Production chain as relation flow",
        4: "Labour market with a worker shield",
        5: "Credit as transformation of future relations",
        6: "The boom: hidden value becomes liquid",
        7: "The amoral dark side: trading domination",
        8: "Government gates and non-tradable rights",
        9: "Ecology attached to every traded bundle",
        10: "Central bank circuit and crisis handling",
        11: "Social state as basic relation shield",
        12: "Competition, platforms and monopoly pressure",
        13: "Foreign trade and translation of standards",
        14: "Full comparison with a plain market economy",
    }
    de = {
        1: "Anatomie der relationalen Währung",
        2: "Markt-Matching ohne einzelnen Preis",
        3: "Produktionskette als Relationsfluss",
        4: "Arbeitsmarkt mit Arbeitsschutzschild",
        5: "Kredit als Transformation von Zukunftsrelationen",
        6: "Der Boom: verborgener Wert wird liquide",
        7: "Die amoralische Schattenseite: Handel mit Herrschaft",
        8: "Regierungstore und nicht handelbare Rechte",
        9: "Ökologie an jedem gehandelten Bündel",
        10: "Zentralbankkreislauf und Krisenbehandlung",
        11: "Sozialstaat als Grundrelationsschild",
        12: "Wettbewerb, Plattformen und Monopoldruck",
        13: "Außenhandel und Übersetzung von Standards",
        14: "Gesamtvergleich mit einer bloßen Marktwirtschaft",
    }
    return en[part] if LANG == "en" else de[part]


def what_why(part: int) -> Tuple[str, str]:
    C = cur_abbr()
    B = bundle_abbr()
    M = market_abbr()
    if LANG == "en":
        what = {
            1: f"The part builds a small {B} with relation rows, claim rows and a validity layer. The aim is to show that the currency object is a table-like bundle, not a number.",
            2: "The part simulates how an ask table and a bid table are matched by compatibility instead of by a single price tag.",
            3: "The part follows inputs, capacity, unfinished output and throughput through a production chain where every step carries rights and duties.",
            4: "The part tests how labour can be represented as limited work promises while a legal shield prevents the worker from becoming a tradable object.",
            5: "The part turns future claims and collateral relations into liquid credit bundles and observes how risk and priority change.",
            6: "The part activates hidden value such as unused time, trust and small claims, then measures circulation and overload.",
            7: "The part deliberately simulates the dangerous version in which work, debt, housing, data and reputation are bundled into control.",
            8: "The part filters a stream of relations through a legal gate and separates allowed market relations from banned or inalienable ones.",
            9: "The part attaches energy, emissions and regeneration relations to products so ecological costs no longer vanish behind price.",
            10: "The part lets a central public circuit rate bundles, support safe claims and quarantine fragile ones during trust stress.",
            11: "The part gives each person public minimum relations for health, education, housing, legal access and re-entry into work.",
            12: "The part maps platform power and tests whether open protocols reduce monopoly pressure in a relation market.",
            13: "The part translates relation standards across borders and tests recognition, tariffs and quality tags.",
            14: f"The part compares {C} with {M}: price simplicity on one side, relation depth and state-bounded complexity on the other.",
        }
        why = {
            1: "This is simulated first because all later markets need a concrete currency object. Counting rows alone would be too weak; the bundle needs legal, time and risk structure.",
            2: "A relation currency becomes useful only if markets can clear it. Matching shows why a richer currency can coordinate more details than a normal price.",
            3: "Production is where the system becomes economically stronger: it can see bottlenecks, obligations and unused capacities before a simple price signal would reveal them.",
            4: "Labour is the moral test. The simulation shows the productive side of matching work, and also why hard boundaries are needed so people are not traded through their dependencies.",
            5: "Credit creates boom power because the future becomes usable today. The same mechanism can also create crisis if weak promises are made to look solid.",
            6: "The boom is special because dormant relations become market fuel. This is powerful, but the speed of activation can overload law, privacy and trust.",
            7: "The dark side cannot be wished away. If every relation is tradable, markets will discover domination as a profitable asset unless government forbids it.",
            8: "The system needs the state not as decoration, but as the gatekeeper that says which relations are never allowed to become currency.",
            9: "Ecology is included because a relational system can carry external costs inside the traded object instead of hiding them outside the transaction.",
            10: "A non-numeric currency still needs macro-stability. The central circuit watches quality, trust and contagion instead of only money quantity.",
            11: "Without basic public relations, weak people are excluded by their risk profile. The social state keeps human life from becoming pure market collateral.",
            12: "The richest matching system will attract platform monopolies. Competition policy must therefore protect access, portability and open protocols.",
            13: "A complete economy trades across borders. Relation bundles need translation, otherwise each country sees the other country's bundles as unclear risk.",
            14: "The conclusion explains why the system is stronger than a plain market economy and why that strength has a dangerous price.",
        }
    else:
        what = {
            1: f"Dieser Teil baut ein kleines {B} mit Relationszeilen, Anspruchszeilen und Gültigkeitsschicht. Ziel ist zu zeigen, dass das Währungsobjekt ein tabellenartiges Bündel ist und keine Zahl.",
            2: "Dieser Teil simuliert, wie Annahmetabelle und Gebotstabelle nach Passung verbunden werden, nicht nach einem einzigen Preisschild.",
            3: "Dieser Teil verfolgt Eingänge, Kapazität, Zwischenarbeit und Durchsatz durch eine Produktionskette, in der jeder Schritt Rechte und Pflichten trägt.",
            4: "Dieser Teil prüft, wie Arbeit als begrenztes Arbeitsversprechen dargestellt werden kann, während ein Rechtsschild verhindert, dass der Arbeitnehmer zum Handelsobjekt wird.",
            5: "Dieser Teil verwandelt Zukunftsansprüche und Sicherheitenrelationen in liquidere Kreditbündel und beobachtet, wie sich Risiko und Vorrang verändern.",
            6: "Dieser Teil aktiviert verborgene Werte wie ungenutzte Zeit, Vertrauen und kleine Ansprüche und misst danach Zirkulation und Überlastung.",
            7: "Dieser Teil simuliert bewusst die gefährliche Version, in der Arbeit, Schuld, Wohnen, Daten und Reputation zu Kontrolle gebündelt werden.",
            8: "Dieser Teil filtert einen Strom von Relationen durch ein Rechtstor und trennt erlaubte Marktrelationen von verbotenen oder unveräußerlichen.",
            9: "Dieser Teil hängt Energie, Emissionen und Regeneration an Produkte, damit ökologische Kosten nicht hinter dem Preis verschwinden.",
            10: "Dieser Teil lässt einen öffentlichen Zentralbankkreislauf Bündel bewerten, sichere Ansprüche stützen und fragile in Vertrauensstress isolieren.",
            11: "Dieser Teil gibt jeder Person öffentliche Mindestrelationen für Gesundheit, Bildung, Wohnen, Rechtszugang und Rückkehr in Arbeit.",
            12: "Dieser Teil kartiert Plattformmacht und prüft, ob offene Protokolle Monopoldruck in einem Relationsmarkt senken.",
            13: "Dieser Teil übersetzt Relationsstandards über Grenzen hinweg und prüft Anerkennung, Zollrelationen und Qualitätsmarken.",
            14: f"Dieser Teil vergleicht {C} mit {M}: Preisschlichtheit auf der einen Seite, Relationstiefe und staatlich begrenzte Komplexität auf der anderen.",
        }
        why = {
            1: "Das wird zuerst simuliert, weil alle späteren Märkte ein konkretes Währungsobjekt brauchen. Zeilenzählen allein wäre zu schwach; das Bündel braucht Rechts-, Zeit- und Risikostruktur.",
            2: "Eine relationale Währung wird nur nützlich, wenn Märkte sie verrechnen können. Matching zeigt, warum eine reichere Währung mehr Details koordinieren kann als ein normaler Preis.",
            3: "In der Produktion wird das System wirtschaftlich stärker: Es sieht Engpässe, Pflichten und ungenutzte Kapazitäten früher als ein bloßes Preissignal.",
            4: "Arbeit ist die moralische Prüfung. Die Simulation zeigt die produktive Seite passender Arbeit und zugleich, warum harte Grenzen nötig sind, damit Menschen nicht über Abhängigkeiten gehandelt werden.",
            5: "Kredit erzeugt Boomkraft, weil Zukunft heute nutzbar wird. Derselbe Mechanismus kann Krisen erzeugen, wenn schwache Versprechen solide aussehen.",
            6: "Der Boom ist besonders, weil ruhende Relationen zu Markttreibstoff werden. Das ist mächtig, aber die Aktivierungsgeschwindigkeit kann Recht, Privatheit und Vertrauen überlasten.",
            7: "Die Schattenseite lässt sich nicht wegwünschen. Wenn jede Relation handelbar ist, entdeckt der Markt Herrschaft als Gewinnquelle, sofern Regierung sie nicht verbietet.",
            8: "Das System braucht den Staat nicht als Schmuck, sondern als Grenzwächter, der sagt, welche Relationen niemals Währung werden dürfen.",
            9: "Ökologie gehört hinein, weil ein relationales System externe Kosten im gehandelten Objekt mittragen kann, statt sie außerhalb der Transaktion zu verstecken.",
            10: "Auch eine nicht numerische Währung braucht Makrostabilität. Der Zentralbankkreislauf beobachtet Qualität, Vertrauen und Ansteckung statt nur Geldmenge.",
            11: "Ohne öffentliche Grundrelationen werden schwache Menschen durch ihr Risikoprofil ausgeschlossen. Der Sozialstaat verhindert, dass Leben zu bloßer Marktsicherheit wird.",
            12: "Das reichste Matching-System zieht Plattformmonopole an. Wettbewerbspolitik muss daher Zugang, Portabilität und offene Protokolle schützen.",
            13: "Eine vollständige Wirtschaft handelt über Grenzen. Relationsbündel brauchen Übersetzung, sonst erscheinen ausländische Bündel als unklares Risiko.",
            14: "Der Schluss erklärt, warum das System stärker ist als eine bloße Marktwirtschaft und warum diese Stärke einen gefährlichen Preis hat.",
        }
    return what[part], why[part]

# ---------------------------------------------------------------------------
# Diagram makers
# ---------------------------------------------------------------------------


def diagram_part_1(abbrs, units):
    B = bundle_abbr()
    C = cur_abbr()
    rows = [
        "╔════════════════════════════════════════════════════════════════════╗",
        f"║ {B} = table-shaped currency object inside {C}                       ║",
        "╠══════════╦════════════╦═════════════╦════════════╦═══════════════╣",
        "║ RID      ║ claim      ║ duty        ║ risk       ║ VAL           ║",
        "╠══════════╬════════════╬═════════════╬════════════╬═══════════════╣",
        "║ R-01     ║ delivery   ║ pay/protect ║ medium     ║ lawful + live ║",
        "║ R-02     ║ machine use║ maintain    ║ low        ║ transferable  ║",
        "║ R-03     ║ work time  ║ respect cap ║ moral test ║ restricted    ║",
        "╚══════════╩════════════╩═════════════╩════════════╩═══════════════╝",
        "          │                         │                         │",
        "          ▼                         ▼                         ▼",
        "   rights and claims          duties and limits          proof and validity",
    ]
    if LANG == "de":
        rows = [
            "╔════════════════════════════════════════════════════════════════════╗",
            f"║ {B} = tabellenförmiges Währungsobjekt innerhalb der {C}            ║",
            "╠══════════╦════════════╦═════════════╦════════════╦═══════════════╣",
            "║ RID      ║ Anspruch   ║ Pflicht     ║ Risiko     ║ VAL           ║",
            "╠══════════╬════════════╬═════════════╬════════════╬═══════════════╣",
            "║ R-01     ║ Lieferung  ║ Zahlung/Sch ║ mittel     ║ gültig + live ║",
            "║ R-02     ║ Maschinzeit║ Wartung     ║ niedrig    ║ übertragbar   ║",
            "║ R-03     ║ Arbeitszeit║ Grenze acht ║ Moraltest  ║ beschränkt    ║",
            "╚══════════╩════════════╩═════════════╩════════════╩═══════════════╝",
            "          │                         │                         │",
            "          ▼                         ▼                         ▼",
            "   Rechte und Ansprüche       Pflichten und Grenzen      Nachweis und Gültigkeit",
        ]
    return line_art(rows, abbrs, units)


def diagram_part_2(abbrs, units, rows):
    vals = [r["liquidity"] for r in rows]
    art = [
        "ASK side                              MME core                              BID side",
        "seller table ──╮                 ╭────────────╮                 ╭── buyer table",
        "repair claim ──┼──── FIT lines ─▶│  match by  │◀─ FIT lines ───┼── time claim",
        "tax credit  ───┤                 │ relation   │                 ├── delivery right",
        "risk cover  ───╯                 │ structure  │                 ╰── insurance row",
        "                                  ╰────────────╯",
    ]
    if LANG == "de":
        art = [
            "ASK-Seite                             MME-Kern                              BID-Seite",
            "Annahmetabelle ─╮                ╭────────────╮                 ╭── Gebotstabelle",
            "Reparaturanspr ─┼──── FIT-Linien▶│  Matching  │◀─ FIT-Linien ───┼── Zeitanspruch",
            "Steuergutsch ───┤                │ nach       │                 ├── Lieferrecht",
            "Risikodeckung ──╯                │ Relation   │                 ╰── Versicherungszeile",
            "                                  ╰────────────╯",
        ]
    trail = "  ".join(mini_bar(v, 100, 8, 82) for v in vals)
    art.append(("Liquidity trail: " if LANG == "en" else "Liquiditätspfad: ") + trail)
    return line_art(art, abbrs, units)


def diagram_part_3(abbrs, units, rows):
    throughput = [r["productivity"] for r in rows]
    art = [
        "        CAP                 WIP                    THR",
        "   ╭─────────╮         ╭──────────╮          ╭────────────╮",
        "   │ machine │──rights▶│ unfinished│──duties▶│ useful out │",
        "   │ labour  │──time──▶│ product   │──proof─▶│ claim rows │",
        "   ╰─────────╯         ╰──────────╯          ╰────────────╯",
        "        ▲                    │                       │",
        "        └──── PCN checks bottlenecks, claims and duties ────┘",
        "THR spark: " + spark(throughput, 20),
    ]
    if LANG == "de":
        art = [
            "        CAP                 WIP                    THR",
            "   ╭─────────╮         ╭──────────╮          ╭────────────╮",
            "   │ Maschine│──Rechte▶│ unfertige│─Pflicht▶│ nutzbarer  │",
            "   │ Arbeit  │──Zeit──▶│ Leistung │─Beweis─▶│ Ausgang    │",
            "   ╰─────────╯         ╰──────────╯          ╰────────────╯",
            "        ▲                    │                       │",
            "        └──── PCN prüft Engpässe, Ansprüche und Pflichten ────┘",
            "THR-Spur: " + spark(throughput, 20),
        ]
    return line_art(art, abbrs, units)


def diagram_part_4(abbrs, units):
    art = [
        "                    LCS protects the person",
        "        ╭────────────────────────────────────────╮",
        " WKR ──▶│ work promise: limited, paid, revocable │──▶ EMP",
        "        │ NTR blocks sale of the human bundle    │",
        "        ╰────────────────────────────────────────╯",
        "              ▲            ▲             ▲",
        "              │            │             │",
        "        max hours      exit right    safety duty",
    ]
    if LANG == "de":
        art = [
            "                    LCS schützt die Person",
            "        ╭────────────────────────────────────────╮",
            " WKR ──▶│ Arbeitsverspr: begrenzt, bezahlt, kündb│──▶ EMP",
            "        │ NTR sperrt Verkauf des Menschenbündels │",
            "        ╰────────────────────────────────────────╯",
            "              ▲            ▲             ▲",
            "              │            │             │",
            "       Höchstzeit     Austritt       Schutzpflicht",
        ]
    return line_art(art, abbrs, units)


def diagram_part_5(abbrs, units, rows):
    risk = [r["crisis_risk"] for r in rows]
    art = [
        "future claims      COL layer         CRT package          SEN order",
        " ╭────────╮      ╭──────────╮      ╭───────────╮      ╭──────────╮",
        " │ small  │─────▶│ pledged  │─────▶│ liquid    │─────▶│ first /  │",
        " │ claims │      │ security │      │ credit    │      │ second   │",
        " ╰────────╯      ╰──────────╯      ╰───────────╯      ╰──────────╯",
        "DRF spark: " + spark(risk, 24),
    ]
    if LANG == "de":
        art = [
            "Zukunftsanspr      COL-Schicht       CRT-Paket           SEN-Rang",
            " ╭────────╮      ╭──────────╮      ╭───────────╮      ╭──────────╮",
            " │ kleine │─────▶│ verpfänd │─────▶│ liquider  │─────▶│ zuerst / │",
            " │ Anspr  │      │ Sicherh  │      │ Kredit    │      │ danach   │",
            " ╰────────╯      ╰──────────╯      ╰───────────╯      ╰──────────╯",
            "DRF-Spur: " + spark(risk, 24),
        ]
    return line_art(art, abbrs, units)


def diagram_part_6(abbrs, units, rows):
    velocity = [r["liquidity"] for r in rows]
    art = [
        "           hidden relation vault                    market river",
        "       ╭──────────────────────╮       HVA       ╭═══════════════════╮",
        "       │ idle time  trust     │ ───────────────▶║  VEL VEL VEL      ║",
        "       │ tiny claims rights   │                 ║  tx tx tx tx      ║",
        "       ╰──────────────────────╯                 ╚═══════════════════╝",
        "                         ABS appears when the river floods",
        "VEL spark: " + spark(velocity, 28),
    ]
    if LANG == "de":
        art = [
            "           Speicher verborgener Relationen          Marktfluss",
            "       ╭──────────────────────╮       HVA       ╭═══════════════════╮",
            "       │ Leerlauf  Vertrauen  │ ───────────────▶║  VEL VEL VEL      ║",
            "       │ Mikroanspr Rechte    │                 ║  tx tx tx tx      ║",
            "       ╰──────────────────────╯                 ╚═══════════════════╝",
            "                         ABS entsteht, wenn der Fluss überläuft",
            "VEL-Spur: " + spark(velocity, 28),
        ]
    return line_art(art, abbrs, units)


def diagram_part_7(abbrs, units):
    art = [
        "       work       debt       housing       data       reputation",
        "        │          │           │            │             │",
        "        └──────────┴───────────┴────────────┴─────────────┘",
        "                              ▼",
        "                     ╭────────────────╮",
        "                     │      HCP       │  DME rises",
        "                     │ human control  │  TCR rises",
        "                     ╰────────────────╯",
        "                              ▲",
        "                         OVB locks exits",
    ]
    if LANG == "de":
        art = [
            "       Arbeit     Schuld      Wohnen       Daten      Reputation",
            "        │          │           │            │             │",
            "        └──────────┴───────────┴────────────┴─────────────┘",
            "                              ▼",
            "                     ╭────────────────╮",
            "                     │      HCP       │  DME steigt",
            "                     │ Menschenkontro │  TCR steigt",
            "                     ╰────────────────╯",
            "                              ▲",
            "                         OVB sperrt Auswege",
        ]
    return line_art(art, abbrs, units)


def diagram_part_8(abbrs, units):
    art = [
        "incoming relation stream",
        "rights ─ work ─ debt ─ data ─ vote ─ body ─ ecology ─ housing",
        "                 │",
        "                 ▼",
        "          ╭────────────╮",
        "          │    LBG     │── allowed market rows ──▶ tradable bundle",
        "          │ IAL + SPL  │── BAN rows ─────────────▶ never currency",
        "          ╰────────────╯",
    ]
    if LANG == "de":
        art = [
            "eingehender Relationsstrom",
            "Rechte ─ Arbeit ─ Schuld ─ Daten ─ Stimme ─ Körper ─ Umwelt ─ Wohnen",
            "                 │",
            "                 ▼",
            "          ╭────────────╮",
            "          │    LBG     │── erlaubte Marktreihen ─▶ handelbares Bündel",
            "          │ IAL + SPL  │── BAN-Reihen ───────────▶ niemals Währung",
            "          ╰────────────╯",
        ]
    return line_art(art, abbrs, units)


def diagram_part_9(abbrs, units, rows):
    co2 = [r["kgco2"] for r in rows]
    art = [
        " product bundle carries ECO rows",
        " ╭─────────╮   EMS strand     ╭─────────────╮",
        " │ product │───────────────▶  │ kgCO2 burden│",
        " ╰─────────╯                  ╰─────────────╯",
        "      │ REG claim                         │ LIM boundary",
        "      ▼                                   ▼",
        " soil / water / air repair          cannot be bought away",
        "EMS spark: " + spark(co2, 24),
    ]
    if LANG == "de":
        art = [
            " Produktbündel trägt ECO-Reihen",
            " ╭─────────╮   EMS-Strang     ╭─────────────╮",
            " │ Produkt │───────────────▶  │ kgCO2-Last  │",
            " ╰─────────╯                  ╰─────────────╯",
            "      │ REG-Anspruch                    │ LIM-Grenze",
            "      ▼                                 ▼",
            " Boden / Wasser / Luft heilen      nicht wegkaufbar",
            "EMS-Spur: " + spark(co2, 24),
        ]
    return line_art(art, abbrs, units)


def diagram_part_10(abbrs, units, rows):
    crisis = [r["crisis_risk"] for r in rows]
    art = [
        " relation pool ──▶ CBC ── QFR test ──▶ circulate",
        "       │             │",
        "       │             ├── GRT public guarantee rail",
        "       │             │",
        "       └──── CRK quarantine when trust breaks",
        "CRK spark: " + spark(crisis, 26),
        "        ╭────────╮       ╭────────╮       ╭────────╮",
        "        │ safe   │──────▶│ watch  │──────▶│ toxic  │",
        "        ╰────────╯       ╰────────╯       ╰────────╯",
    ]
    if LANG == "de":
        art = [
            " Relationspool ─▶ CBC ── QFR-Test ─▶ zirkulieren",
            "       │             │",
            "       │             ├── GRT öffentliche Garantieschiene",
            "       │             │",
            "       └──── CRK-Quarantäne, wenn Vertrauen bricht",
            "CRK-Spur: " + spark(crisis, 26),
            "        ╭────────╮       ╭────────╮       ╭────────╮",
            "        │ sicher │──────▶│ prüfen │──────▶│ toxisch│",
            "        ╰────────╯       ╰────────╯       ╰────────╯",
        ]
    return line_art(art, abbrs, units)


def diagram_part_11(abbrs, units):
    art = [
        "                 ╭──────────── BRS ────────────╮",
        "                 │  HLT       EDU       HOU    │",
        "                 │ health   learning   shelter │",
        "                 │ legal access + re-entry     │",
        "                 ╰─────────────┬───────────────╯",
        "                               ▼",
        "                    person stays market-capable",
    ]
    if LANG == "de":
        art = [
            "                 ╭──────────── BRS ────────────╮",
            "                 │  HLT       EDU       HOU    │",
            "                 │ Gesundh  Bildung   Wohnen   │",
            "                 │ Rechtszugang + Rückkehr     │",
            "                 ╰─────────────┬───────────────╯",
            "                               ▼",
            "                    Person bleibt marktfähig",
        ]
    return line_art(art, abbrs, units)


def diagram_part_12(abbrs, units, rows):
    monopoly = [r["control_power"] for r in rows]
    art = [
        "                           CMP",
        "        small apps ──╮       │       ╭── workers",
        "        banks    ────┼──▶ platform ─┼── sellers",
        "        state link ──╯       │       ╰── buyers",
        "                             ▼",
        "        MPI rises when one hub controls many gates",
        "        INT + OPF cut paths through the hub",
        "MPI spark: " + spark(monopoly, 24),
    ]
    if LANG == "de":
        art = [
            "                           CMP",
            "        kleine Apps ─╮       │       ╭── Arbeiter",
            "        Banken ──────┼──▶ Plattform ┼── Verkäufer",
            "        Staatslink ─╯       │       ╰── Käufer",
            "                             ▼",
            "        MPI steigt, wenn ein Knoten viele Tore kontrolliert",
            "        INT + OPF schneiden Wege durch den Knoten frei",
            "MPI-Spur: " + spark(monopoly, 24),
        ]
    return line_art(art, abbrs, units)


def diagram_part_13(abbrs, units, rows):
    rec = [r["transparency"] for r in rows]
    art = [
        "Country A bundle           CTL bridge             Country B register",
        "╭──────────────╮       ╭──────────────╮        ╭───────────────╮",
        "│ STD labour   │──────▶│ translate    │───────▶│ accepted rows │",
        "│ STD data     │       │ TAR checked  │        │ REC score     │",
        "│ STD ecology  │       ╰──────────────╯        ╰───────────────╯",
        "REC spark: " + spark(rec, 24),
    ]
    if LANG == "de":
        art = [
            "Land-A-Bündel              CTL-Brücke            Land-B-Register",
            "╭──────────────╮       ╭──────────────╮        ╭───────────────╮",
            "│ STD Arbeit   │──────▶│ übersetzen   │───────▶│ akzeptierte   │",
            "│ STD Daten    │       │ TAR geprüft  │        │ REC-Reihen    │",
            "│ STD Umwelt   │       ╰──────────────╯        ╰───────────────╯",
            "REC-Spur: " + spark(rec, 24),
        ]
    return line_art(art, abbrs, units)


def diagram_part_14(abbrs, units, rows):
    C = cur_abbr()
    M = market_abbr()
    art = [
        f"{M}:  thing ──▶ price number ──▶ trade",
        "        simple, fast, liquid, but structurally blind",
        "",
        f"{C}:  relation table ──▶ legal gate ──▶ matching ──▶ trade",
        "        deeper, stronger, more governable, but socially invasive",
        "",
        "INF shows depth; PRD shows coordination; DGN shows whether humans stay protected.",
    ]
    if LANG == "de":
        art = [
            f"{M}:  Sache ──▶ Preiszahl ──▶ Handel",
            "        einfach, schnell, liquide, aber strukturell blind",
            "",
            f"{C}:  Relationstabelle ──▶ Rechtstor ──▶ Matching ──▶ Handel",
            "        tiefer, stärker, besser steuerbar, aber sozial eindringlicher",
            "",
            "INF zeigt Tiefe; PRD zeigt Koordination; DGN zeigt, ob Menschen geschützt bleiben.",
        ]
    return line_art(art, abbrs, units)

# ---------------------------------------------------------------------------
# Simulation parts
# ---------------------------------------------------------------------------


def print_part_header(part: int, abbrs, units):
    global ACTIVE_ABBRS, ACTIVE_UNITS
    ACTIVE_ABBRS = dict(abbrs)
    ACTIVE_UNITS = list(units)
    print("\n" + rainbow_rule())
    label = f"{L('part')} {part:02d}: {part_title(part)}"
    print(ansi(fit_visible(label, WIDTH), fg=15, bg=25, bold=True))
    print(rainbow_rule())
    what, why = what_why(part)
    print(section_box(L("what"), what, abbrs, units, fg=15, bg=24))
    print(section_box(L("why"), why, abbrs, units, fg=15, bg=53))
    print(section_box(L("reading"), L("legend_hint") + " " + L("unit_hint"), abbrs, units, fg=15, bg=55))
    print(legend_abbr(abbrs, units))
    print(legend_units(units))
    print(ansi(L("diagram"), fg=213, bold=True, underline=True))


def run_part_1(seed: int):
    part = 1; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    print(diagram_part_1(abbrs, units))
    rows = scenario_results(seed, part)
    print(scenario_table(rows, units, "counts"))
    values = [[r["transparency"], r["liquidity"], r["crisis_risk"], r["freedom"]] for r in rows]
    print(matrix(["Structure", "Liquidity", "Risk", "Freedom"] if LANG == "en" else ["Struktur", "Liquidität", "Risiko", "Freiheit"], [r["scenario"] for r in rows], values, "Bundle heatmap" if LANG == "en" else "Bündel-Heatmap"))
    if LANG == "en":
        msg = f"The {bundle_abbr()} becomes strongest when relation rows are numerous enough to represent reality, but not so unconstrained that the validity layer is drowned in risk. Row count alone does not define value; validity, risk and transferability change the result."
    else:
        msg = f"Das {bundle_abbr()} wird am stärksten, wenn genug Relationszeilen die Wirklichkeit abbilden, aber nicht so ungegrenzt, dass die Gültigkeitsschicht im Risiko versinkt. Zeilenzahl allein bestimmt keinen Wert; Gültigkeit, Risiko und Übertragbarkeit verändern das Ergebnis."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_2(seed: int):
    part = 2; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    rows = scenario_results(seed, part, lambda s, i: s.update({"interoperability": s["interoperability"] + 0.08}))
    print(diagram_part_2(abbrs, units, rows))
    print(scenario_table(rows, units, "general"))
    fit_rows = []
    for r in rows:
        fit = clamp(0.45 * r["liquidity"] + 0.35 * r["transparency"] + 0.20 * r["inclusion"] - 0.15 * r["crisis_risk"])
        fit_rows.append([r["scenario"], bar(fit, good=True), num(r["relations"], "rels" if LANG == "en" else "Rel", units), num(max(1, int(fit / 10)), "tx", units)])
    print(table([L("scenario"), "FIT", "Rows" if LANG == "en" else "Reihen", "Cleared" if LANG == "en" else "Verrechnet"], fit_rows, ["left", "left", "right", "right"], "FIT detail" if LANG == "en" else "FIT-Detail"))
    msg = "Compatibility replaces the single price as the clearing signal. This is stronger because the market can match needs, risks and duties at the same time." if LANG == "en" else "Passung ersetzt den Einzelpreis als Verrechnungssignal. Das ist stärker, weil der Markt Bedürfnisse, Risiken und Pflichten gleichzeitig abgleichen kann."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_3(seed: int):
    part = 3; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    rows = scenario_results(seed, part, lambda s, i: s.update({"market": min(1, s["market"] + 0.04), "data": min(1, s["data"] + 0.05)}))
    print(diagram_part_3(abbrs, units, rows))
    print(scenario_table(rows, units, "eco"))
    prod_rows = []
    for r in rows:
        out_units = clamp(r["productivity"] * 1.4 - r["crisis_risk"] * 0.3 + 20)
        prod_rows.append([r["scenario"], bar(r["productivity"], good=True), num(r["hours"], "h" if LANG == "en" else "Std", units), num(out_units, "units" if LANG == "en" else "Einheiten", units), num(r["kwh"], "kWh", units)])
    print(table([L("scenario"), "Productivity" if LANG == "en" else "Produktivität", "Input", "Output", "Energy" if LANG == "en" else "Energie"], prod_rows, ["left", "left", "right", "right", "right"], "Production detail" if LANG == "en" else "Produktionsdetail"))
    msg = "The chain gains strength from seeing duties and capacity before the final product exists. The weakness is complexity: bad data can misroute the whole chain." if LANG == "en" else "Die Kette gewinnt Stärke, weil Pflichten und Kapazität sichtbar sind, bevor das Endprodukt existiert. Die Schwäche ist Komplexität: Schlechte Daten können die ganze Kette falsch lenken."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_4(seed: int):
    part = 4; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    def tweak(s, i):
        if s["key"] == "guarded":
            s["labor"] = 0.93; s["state"] = 0.90
        if s["key"] == "dark":
            s["commod"] = 0.96; s["labor"] = 0.05
    rows = scenario_results(seed, part, tweak)
    print(diagram_part_4(abbrs, units))
    print(scenario_table(rows, units, "risk"))
    data = []
    for r in rows:
        protection = clamp(100 - r["dignity_risk"] + 0.25 * r["inclusion"])
        data.append([r["scenario"], bar(protection, good=True), num(r["jobs"], "jobs" if LANG == "en" else "Arb", units), num(r["hours"], "h" if LANG == "en" else "Std", units), bar(r["freedom"], good=True)])
    print(table([L("scenario"), "LCS", "Work" if LANG == "en" else "Arbeit", "Hours" if LANG == "en" else "Stunden", "Freedom" if LANG == "en" else "Freiheit"], data, ["left", "left", "right", "right", "left"], "Labour shield detail" if LANG == "en" else "Arbeitsschutz-Detail"))
    if LANG == "en":
        msg = "The guarded scenario proves the humane design: labour can be matched without selling the worker. The dark scenario proves the opposite danger: if work, debt and housing are bundled, formal contract language can hide practical domination."
    else:
        msg = "Das geschützte Szenario beweist die humane Konstruktion: Arbeit kann passend vermittelt werden, ohne den Arbeitnehmer zu verkaufen. Das dunkle Szenario zeigt die Gegengefahr: Werden Arbeit, Schuld und Wohnen gebündelt, kann formale Vertragssprache praktische Herrschaft verstecken."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_5(seed: int):
    part = 5; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    def tweak(s, i):
        s["debt"] = min(1, s["debt"] + 0.12)
        if s["key"] == "guarded": s["state"] = 0.92
    rows = scenario_results(seed, part, tweak)
    print(diagram_part_5(abbrs, units, rows))
    print(scenario_table(rows, units, "general"))
    cred_rows = []
    for r in rows:
        quality = clamp(100 - r["crisis_risk"] + 0.25 * r["transparency"])
        cred_rows.append([r["scenario"], num(r["claims"], "claims" if LANG == "en" else "Anspr", units), num(r["relations"], "rels" if LANG == "en" else "Rel", units), bar(r["crisis_risk"], good=False), bar(quality, good=True)])
    print(table([L("scenario"), "Claims" if LANG == "en" else "Ansprüche", "COL", "DRF", "SEN quality" if LANG == "en" else "SEN-Qualität"], cred_rows, ["left", "right", "right", "left", "left"], "Credit detail" if LANG == "en" else "Kreditdetail"))
    msg = "Credit is a boom machine because it turns future relations into present capacity. The cost is fragility: if weak claims are over-ranked, the crisis kink arrives suddenly." if LANG == "en" else "Kredit ist eine Boommaschine, weil er Zukunftsrelationen in gegenwärtige Kapazität verwandelt. Der Preis ist Fragilität: Werden schwache Ansprüche zu hoch gerankt, kommt der Krisenknick plötzlich."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_6(seed: int):
    part = 6; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    def tweak(s, i):
        s["market"] = min(1, s["market"] + 0.10)
        s["data"] = min(1, s["data"] + 0.08)
    rows = scenario_results(seed, part, tweak)
    print(diagram_part_6(abbrs, units, rows))
    print(scenario_table(rows, units, "counts"))
    boom_rows = []
    for r in rows:
        strain = clamp(r["liquidity"] * 0.55 + r["crisis_risk"] * 0.45 - r["inclusion"] * 0.25)
        boom_rows.append([r["scenario"], bar(r["boom"], good=True), num(r["relations"], "rels" if LANG == "en" else "Rel", units), num(max(1, int(r["liquidity"] / 4)), "tx", units), bar(strain, good=False)])
    print(table([L("scenario"), "LBM", "HVA", "VEL", "ABS"], boom_rows, ["left", "left", "right", "right", "left"], "Boom detail" if LANG == "en" else "Boom-Detail"))
    msg = "This is where the relational economy outperforms a plain market economy most visibly: dormant capacities become tradable. The price is absorption strain: law, privacy and trust must process far more marketable reality." if LANG == "en" else "Hier übertrifft die relationale Ökonomie eine bloße Marktwirtschaft am sichtbarsten: Ruhende Kapazitäten werden handelbar. Der Preis ist Aufnahmespannung: Recht, Privatheit und Vertrauen müssen viel mehr marktfähige Wirklichkeit verarbeiten."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_7(seed: int):
    part = 7; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    def tweak(s, i):
        if s["key"] in ("spec", "dark"):
            s["commod"] = min(1, s["commod"] + 0.18)
            s["platform"] = min(1, s["platform"] + 0.10)
            s["labor"] = max(0, s["labor"] - 0.12)
    rows = scenario_results(seed, part, tweak)
    print(diagram_part_7(abbrs, units))
    print(scenario_table(rows, units, "risk"))
    risk_rows = []
    for r in rows:
        tcr = clamp(r["dignity_risk"] * 0.72 + r["control_power"] * 0.28)
        ovb = clamp(r["control_power"] * 0.55 + r["crisis_risk"] * 0.20)
        risk_rows.append([r["scenario"], bar(tcr, good=False), bar(ovb, good=False), num(r["relations"], "rels" if LANG == "en" else "Rel", units), num(r["hours"], "h" if LANG == "en" else "Std", units)])
    print(table([L("scenario"), "TCR", "OVB", "HCP rows" if LANG == "en" else "HCP-Reihen", "Bound" if LANG == "en" else "Gebunden"], risk_rows, ["left", "left", "left", "right", "right"], "Dark-side detail" if LANG == "en" else "Schattenseiten-Detail"))
    warning = L("not_moral_advice") + " "
    if LANG == "en":
        msg = warning + "The dark scenario can still boom because domination is economically useful to the controller. That is precisely why law must refuse to treat human dependency as normal currency."
    else:
        msg = warning + "Das dunkle Szenario kann trotzdem boomen, weil Herrschaft für den Kontrolleur ökonomisch nützlich ist. Genau deshalb muss Recht verweigern, menschliche Abhängigkeit als normale Währung zu behandeln."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=88))


def run_part_8(seed: int):
    part = 8; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    def tweak(s, i):
        if s["key"] == "guarded": s["state"] = 0.96
        if s["key"] == "dark": s["state"] = 0.08
    rows = scenario_results(seed, part, tweak)
    print(diagram_part_8(abbrs, units))
    print(scenario_table(rows, units, "risk"))
    gate_rows = []
    for r in rows:
        boundary = clamp(0.55 * r["freedom"] + 0.35 * r["inclusion"] + 0.35 * r["transparency"] - 0.25 * r["dignity_risk"])
        banned = clamp(r["dignity_risk"] * 0.6 + r["control_power"] * 0.4)
        gate_rows.append([r["scenario"], bar(boundary, good=True), num(int(10 + boundary / 5), "rights" if LANG == "en" else "Rechte", units), num(int(20 + banned / 2), "rels" if LANG == "en" else "Rel", units), bar(banned, good=False)])
    print(table([L("scenario"), "LBG", "IAL", "BAN rows" if LANG == "en" else "BAN-Reihen", "Rejected" if LANG == "en" else "Abgewiesen"], gate_rows, ["left", "left", "right", "right", "left"], "Legal gate detail" if LANG == "en" else "Rechtstor-Detail"))
    msg = "This part shows the constitutional heart of the system: the market may be rich, but the gate decides what must remain outside the market." if LANG == "en" else "Dieser Teil zeigt das verfassungsartige Herz des Systems: Der Markt darf reich sein, aber das Tor entscheidet, was außerhalb des Marktes bleiben muss."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_9(seed: int):
    part = 9; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    def tweak(s, i):
        if s["key"] == "guarded": s["ecology"] = 0.92
        if s["key"] == "open": s["ecology"] = 0.60
        if s["key"] == "spec": s["ecology"] = 0.42
        if s["key"] == "dark": s["ecology"] = 0.18
    rows = scenario_results(seed, part, tweak)
    print(diagram_part_9(abbrs, units, rows))
    print(scenario_table(rows, units, "eco"))
    eco_rows = []
    for r in rows:
        lim = clamp(100 - r["ecology_balance"] + r["boom"] * 0.18)
        reg = clamp(r["ecology_balance"] * 0.75 + r["inclusion"] * 0.15)
        eco_rows.append([r["scenario"], bar(r["ecology_balance"], good=True), num(r["kgco2"], "kgCO2", units), bar(reg, good=True), bar(lim, good=False)])
    print(table([L("scenario"), "ECO" if LANG == "en" else "ECO", "EMS", "REG", "LIM pressure" if LANG == "en" else "LIM-Druck"], eco_rows, ["left", "left", "right", "left", "left"], "Ecology detail" if LANG == "en" else "Ökologie-Detail"))
    msg = "The relational system is stronger than price-only trade because environmental burdens travel with the bundle. The danger is that rich actors may try to package harm as tradable permission, so the limit line must be non-tradable." if LANG == "en" else "Das relationale System ist stärker als reiner Preishandel, weil Umweltlasten mit dem Bündel reisen. Die Gefahr ist, dass reiche Akteure Schaden als handelbare Erlaubnis verpacken; deshalb muss die Grenzlinie nicht handelbar sein."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_10(seed: int):
    part = 10; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    def tweak(s, i):
        s["shock"] = min(1, s["shock"] + 0.12)
        if s["key"] == "guarded": s["state"] = 0.94
    rows = scenario_results(seed, part, tweak)
    print(diagram_part_10(abbrs, units, rows))
    print(scenario_table(rows, units, "general"))
    cb_rows = []
    for r in rows:
        qfr = clamp(100 - r["crisis_risk"] + 0.2 * r["transparency"])
        grt = clamp(r["inclusion"] * 0.45 + r["state"] if "state" in r else 50)
        cb_rows.append([r["scenario"], num(r["relations"], "rels" if LANG == "en" else "Rel", units), bar(qfr, good=True), bar(r["crisis_risk"], good=False), num(r["claims"], "claims" if LANG == "en" else "Anspr", units)])
    print(table([L("scenario"), "Tested" if LANG == "en" else "Geprüft", "QFR", "CRK", "GRT support" if LANG == "en" else "GRT-Stütze"], cb_rows, ["left", "right", "left", "left", "right"], "Central circuit detail" if LANG == "en" else "Zentralbankdetail"))
    msg = "The central circuit does not merely print money. It classifies relation quality. That is stronger than ordinary monetary control, but it gives public institutions enormous classification power." if LANG == "en" else "Der Zentralbankkreislauf druckt nicht bloß Geld. Er klassifiziert Relationsqualität. Das ist stärker als gewöhnliche Geldmengensteuerung, gibt öffentlichen Institutionen aber enorme Klassifikationsmacht."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_11(seed: int):
    part = 11; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    def tweak(s, i):
        s["state"] = min(1, s["state"] + 0.14)
        s["labor"] = min(1, s["labor"] + 0.10)
        if s["key"] == "dark": s["state"] = 0.38
    rows = scenario_results(seed, part, tweak)
    print(diagram_part_11(abbrs, units))
    print(scenario_table(rows, units, "risk"))
    social_rows = []
    for r in rows:
        brs = clamp(r["inclusion"] * 0.55 + r["freedom"] * 0.35 + 10)
        social_rows.append([r["scenario"], bar(brs, good=True), num(5 + brs / 12, "rights" if LANG == "en" else "Rechte", units), num(r["jobs"], "jobs" if LANG == "en" else "Arb", units), bar(r["inclusion"], good=True)])
    print(table([L("scenario"), "BRS", "HLT EDU HOU" if LANG == "en" else "HLT EDU HOU", "Re-entry" if LANG == "en" else "Rückkehr", "Inclusion" if LANG == "en" else "Teilhabe"], social_rows, ["left", "left", "right", "right", "left"], "Social shield detail" if LANG == "en" else "Sozialschutz-Detail"))
    msg = "Basic relations are not charity in this model; they are infrastructure. They keep people from being priced as broken bundles and keep the whole market from losing participants." if LANG == "en" else "Grundrelationen sind in diesem Modell keine Wohltätigkeit; sie sind Infrastruktur. Sie verhindern, dass Menschen als kaputte Bündel bewertet werden, und sie halten Teilnehmende im Markt."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_12(seed: int):
    part = 12; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    def tweak(s, i):
        if s["key"] == "guarded": s["interoperability"] = 0.90
        if s["key"] == "dark": s["platform"] = 0.98; s["interoperability"] = 0.10
    rows = scenario_results(seed, part, tweak)
    print(diagram_part_12(abbrs, units, rows))
    print(scenario_table(rows, units, "risk"))
    comp_rows = []
    for r in rows:
        mpi = clamp(r["control_power"] * 0.75 + r["crisis_risk"] * 0.20)
        opf = clamp(100 - mpi + 0.20 * r["inclusion"])
        comp_rows.append([r["scenario"], bar(mpi, good=False), bar(opf, good=True), num(r["relations"], "rels" if LANG == "en" else "Rel", units), num(max(1, int(r["liquidity"] / 3)), "tx", units)])
    print(table([L("scenario"), "MPI", "OPF", "Access" if LANG == "en" else "Zugang", "Flow" if LANG == "en" else "Fluss"], comp_rows, ["left", "left", "left", "right", "right"], "Competition detail" if LANG == "en" else "Wettbewerbsdetail"))
    msg = "The stronger the matching system, the more tempting it is to monopolize the gates. Open protocols are therefore not a technical luxury; they are economic self-defense." if LANG == "en" else "Je stärker das Matching-System, desto verlockender ist die Monopolisierung der Tore. Offene Protokolle sind deshalb kein technischer Luxus, sondern wirtschaftliche Selbstverteidigung."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_13(seed: int):
    part = 13; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    def tweak(s, i):
        s["interoperability"] = min(1, s["interoperability"] + 0.12)
        s["external"] = max(0, s["external"] - 0.06)
    rows = scenario_results(seed, part, tweak)
    print(diagram_part_13(abbrs, units, rows))
    print(scenario_table(rows, units, "counts"))
    trade_rows = []
    for r in rows:
        rec = clamp(r["transparency"] * 0.55 + r["inclusion"] * 0.25 + r["ecology_balance"] * 0.20 - r["crisis_risk"] * 0.15)
        tar = clamp(100 - rec + r["crisis_risk"] * 0.20)
        trade_rows.append([r["scenario"], bar(rec, good=True), num(r["relations"], "rels" if LANG == "en" else "Rel", units), num(max(1, int(rec / 5)), "tx", units), bar(tar, good=False)])
    print(table([L("scenario"), "REC", "STD rows" if LANG == "en" else "STD-Reihen", "Cross tx" if LANG == "en" else "Grenz-tx", "TAR load" if LANG == "en" else "TAR-Last"], trade_rows, ["left", "left", "right", "right", "left"], "Foreign trade detail" if LANG == "en" else "Außenhandelsdetail"))
    msg = "Foreign trade becomes richer because labour, data and ecology standards travel with the bundle. The cost is translation bureaucracy and conflict about whose standards count." if LANG == "en" else "Außenhandel wird reicher, weil Arbeits-, Daten- und Umweltstandards mit dem Bündel reisen. Der Preis ist Übersetzungsbürokratie und Streit darüber, wessen Standards gelten."
    print(section_box(L("evaluation"), outcome_summary(rows, abbrs, units) + "\n" + msg, abbrs, units, fg=15, bg=22))


def run_part_14(seed: int):
    part = 14; abbrs = A(part); units = U(part)
    print_part_header(part, abbrs, units)
    rows = scenario_results(seed, part)
    print(diagram_part_14(abbrs, units, rows))
    # Compare conventional market economy with relational economy under several governance cases.
    comp = []
    for r in rows:
        inf_rce = clamp(r["transparency"] + 12)
        prd_rce = clamp(r["productivity"] + 8)
        dgn_rce = clamp(r["freedom"] + 0.2 * r["inclusion"] - 0.3 * r["dignity_risk"])
        inf_me = clamp(38 + (10 if r["key"] == "open" else 0) - (8 if r["key"] == "dark" else 0))
        prd_me = clamp(55 + 18 * (1 if r["key"] in ("open", "spec") else 0) - 8 * (1 if r["key"] == "shock" else 0))
        dgn_me = clamp(64 - 24 * (1 if r["key"] in ("spec", "dark") else 0))
        comp.append([r["scenario"], inf_rce, prd_rce, dgn_rce, inf_me, prd_me, dgn_me])
    rows_table = []
    for name, inf_rce, prd_rce, dgn_rce, inf_me, prd_me, dgn_me in comp:
        rows_table.append([
            name,
            bar(inf_rce, good=True), bar(prd_rce, good=True), bar(dgn_rce, good=True),
            bar(inf_me, good=True), bar(prd_me, good=True), bar(dgn_me, good=True),
        ])
    C = cur_abbr(); M = market_abbr()
    print(table([L("scenario"), f"{C} INF", f"{C} PRD", f"{C} DGN", f"{M} INF", f"{M} PRD", f"{M} DGN"], rows_table, ["left"] * 7, "System comparison" if LANG == "en" else "Systemvergleich"))
    heat = [[inf_rce, prd_rce, dgn_rce, inf_me, prd_me, dgn_me] for _, inf_rce, prd_rce, dgn_rce, inf_me, prd_me, dgn_me in comp]
    print(matrix([f"{C}-INF", f"{C}-PRD", f"{C}-DGN", f"{M}-INF", f"{M}-PRD", f"{M}-DGN"], [x[0] for x in comp], heat, "Comparison heatmap" if LANG == "en" else "Vergleichs-Heatmap"))
    if LANG == "en":
        msg = f"The {C} side is stronger wherever information depth and productive coordination matter. The {M} side remains stronger in simplicity, privacy by ignorance and fast anonymous liquidity. The dangerous price of {C} strength is social penetration: the same structure that coordinates reality can also classify, rank and control people unless dignity guards remain hard law."
    else:
        msg = f"Die {C}-Seite ist stärker, wo Informationstiefe und produktive Koordination zählen. Die {M}-Seite bleibt stärker bei Einfachheit, Privatheit durch Nichtwissen und schneller anonymer Liquidität. Der gefährliche Preis der {C}-Stärke ist soziale Durchdringung: Dieselbe Struktur, die Wirklichkeit koordiniert, kann Menschen klassifizieren, einstufen und kontrollieren, wenn Würdewächter nicht hartes Recht bleiben."
    print(section_box(L("evaluation"), msg, abbrs, units, fg=15, bg=22))


# ---------------------------------------------------------------------------
# Extended scalar bridge: relation table -> classic market number
# ---------------------------------------------------------------------------

# The following section adds the requested conversion model:
#       cell contribution = cell value * row factor * column factor
#       market-equivalent value = sum of all cell contributions
# It also replaces a few layout helpers with width-aware versions so the
# terminal width is respected after subtracting the requested safety margin.


def clip_ansi(text: str, max_width: int) -> str:
    """Return text clipped to max visible characters while keeping ANSI codes intact."""
    s = str(text)
    out = []
    i = 0
    visible = 0
    while i < len(s) and visible < max_width:
        if s[i] == "\x1b":
            j = i + 1
            while j < len(s) and s[j] != "m":
                j += 1
            if j < len(s):
                out.append(s[i:j + 1])
                i = j + 1
                continue
        out.append(s[i])
        visible += 1
        i += 1
    if USE_COLOR and ANSI_RE.search(s):
        out.append("\033[0m")
    return "".join(out)


def fit_visible(text: str, max_width: int) -> str:
    if vlen(text) <= max_width:
        return str(text)
    return clip_ansi(text, max(0, max_width - 1)) + "…"


# Override wrap_lines after the original definition. This version is safer for
# already-painted text because it wraps the visible text and re-applies the
# currently active abbreviation/unit colors to each line.
def wrap_lines(text: str, width: int) -> List[str]:  # type: ignore[override]
    lines = []
    for para in str(text).split("\n"):
        raw = strip_ansi(para)
        if not raw.strip():
            lines.append("")
            continue
        pieces = textwrap.wrap(raw, width=max(8, width), replace_whitespace=False)
        if not pieces:
            lines.append("")
        else:
            for piece in pieces:
                lines.append(paint(piece, ACTIVE_ABBRS, ACTIVE_UNITS) if (ACTIVE_ABBRS or ACTIVE_UNITS) else piece)
    return lines


# Override line_art so all fixed diagrams are cropped to the detected width.
def line_art(lines: Sequence[str], abbrs: Dict[str, str], units: Sequence[Tuple[str, str]]) -> str:  # type: ignore[override]
    width = max(20, WIDTH)
    return "\n".join(fit_visible(paint(x, abbrs, units), width) for x in lines)


# Override bar with dynamic default width. This keeps scenario tables inside
# narrower terminals while preserving color.
def bar(value: float, maximum: float = 100.0, width: int = None, good: bool = True) -> str:  # type: ignore[override]
    if width is None:
        if WIDTH < 86:
            width = 8
        elif WIDTH < 108:
            width = 12
        elif WIDTH < 130:
            width = 18
        else:
            width = 28
    value = max(0.0, min(float(maximum), float(value)))
    filled = int(round(width * value / maximum)) if maximum else 0
    empty = width - filled
    if not USE_COLOR:
        return "[" + "#" * filled + "." * empty + "] %3d" % round(value)
    if good:
        col = 46 if value >= 70 else (226 if value >= 40 else 196)
    else:
        col = 196 if value >= 70 else (208 if value >= 40 else 46)
    return "[" + ansi("█" * filled, fg=col, bold=True) + ansi("░" * empty, fg=238) + "] %3d" % round(value)


# Override table with width-aware wrapping. Long explanation cells remain
# readable, while bars and numbers stay compact.
def table(headers: Sequence[str], rows: Sequence[Sequence[str]], align: Sequence[str] = None, title: str = "") -> str:  # type: ignore[override]
    if align is None:
        align = ["left"] * len(headers)
    if ACTIVE_ABBRS or ACTIVE_UNITS:
        title = paint(title, ACTIVE_ABBRS, ACTIVE_UNITS) if title else title
        headers = [paint(str(h), ACTIVE_ABBRS, ACTIVE_UNITS) for h in headers]
        rows = [[paint(str(c), ACTIVE_ABBRS, ACTIVE_UNITS) for c in row] for row in rows]
    n = len(headers)
    all_rows = [list(headers)] + [list(r) for r in rows]
    raw_widths = [0] * n
    for row in all_rows:
        for i, cell in enumerate(row):
            raw_widths[i] = max(raw_widths[i], vlen(cell))
    # Target visible width of a table: WIDTH. Border overhead is 3*n + 1.
    overhead = 3 * n + 1
    max_content = max(n * 4, WIDTH - overhead)
    widths = list(raw_widths)
    if sum(widths) > max_content:
        # Keep small code/number columns tight and let description columns carry wrapping.
        min_widths = [4] * n
        for i in range(n):
            h = strip_ansi(str(headers[i])).lower()
            if any(k in h for k in ("code", "kürzel", "unit", "einheit")):
                min_widths[i] = min(5, max(4, raw_widths[i]))
            if any(k in h for k in ("scenario", "szenario")):
                min_widths[i] = min(10, max(6, raw_widths[i]))
        widths = [max(min_widths[i], min(raw_widths[i], max(4, max_content // n))) for i in range(n)]
        while sum(widths) > max_content:
            idx = max(range(n), key=lambda k: widths[k] - min_widths[k])
            if widths[idx] <= min_widths[idx]:
                break
            widths[idx] -= 1
        # Distribute spare room to the widest original columns.
        while sum(widths) < max_content:
            candidates = [i for i in range(n) if widths[i] < raw_widths[i]]
            if not candidates:
                break
            idx = max(candidates, key=lambda k: raw_widths[k] - widths[k])
            widths[idx] += 1
    def wrap_cell(cell, width):
        if vlen(cell) <= width:
            return [cell]
        raw = strip_ansi(str(cell))
        wrapped = textwrap.wrap(raw, width=max(4, width), replace_whitespace=False)
        if not wrapped:
            wrapped = [raw[:width]]
        return [paint(x, ACTIVE_ABBRS, ACTIVE_UNITS) if (ACTIVE_ABBRS or ACTIVE_UNITS) else x for x in wrapped]
    def draw_row(row, is_header=False):
        wrapped_cols = [wrap_cell(row[i] if i < len(row) else "", widths[i]) for i in range(n)]
        height = max(len(c) for c in wrapped_cols)
        out = []
        for line_idx in range(height):
            cells = []
            for i in range(n):
                cell = wrapped_cols[i][line_idx] if line_idx < len(wrapped_cols[i]) else ""
                if is_header:
                    cell = ansi(pad(fit_visible(cell, widths[i]), widths[i], "center"), fg=15, bg=60, bold=True)
                else:
                    cell = pad(fit_visible(cell, widths[i]), widths[i], align[i] if i < len(align) else "left")
                cells.append(" " + cell + " ")
            out.append(ansi("│", fg=39) + ansi("│", fg=39).join(cells) + ansi("│", fg=39))
        return out
    sep_top = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
    sep_mid = "├" + "┼".join("─" * (w + 2) for w in widths) + "┤"
    sep_bot = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"
    out = []
    if title:
        out.append(ansi(fit_visible(title, WIDTH), fg=213, bold=True, underline=True))
    out.append(ansi(sep_top, fg=39))
    out.extend(draw_row(headers, is_header=True))
    out.append(ansi(sep_mid, fg=39))
    for row in rows:
        out.extend(draw_row(list(row), is_header=False))
    out.append(ansi(sep_bot, fg=39))
    return "\n".join(out)


# Override matrix to be responsive to terminal width.
def matrix(labels_x: Sequence[str], labels_y: Sequence[str], values: Sequence[Sequence[float]], title: str = "", invert: bool = False) -> str:  # type: ignore[override]
    if not labels_x or not labels_y:
        return ""
    yw = min(12, max(6, max(vlen(y) for y in labels_y)))
    available = max(18, WIDTH - yw - 2)
    xw = max(3, min(10, (available // max(1, len(labels_x))) - 1))
    cellw = min(3, xw)
    def fit_label(x, w):
        raw = strip_ansi(str(x))
        if len(raw) <= w:
            return str(x)
        return raw[:max(1, w - 1)] + "…"
    rows = []
    if title:
        rows.append(ansi(fit_visible(title, WIDTH), fg=213, bold=True, underline=True))
    head = " " * (yw + 1) + " ".join(pad(fit_label(x, xw), xw, "center") for x in labels_x)
    rows.append(fit_visible(head, WIDTH))
    for y, row in zip(labels_y, values):
        cells = " ".join(pad(heat_cell(v, width=cellw, invert=invert), xw, "center") for v in row)
        rows.append(fit_visible(pad(fit_label(y, yw), yw, "right") + " " + cells, WIDTH))
    return "\n".join(rows)


NEW_PART_META = {
    "en": {
        15: ("Scalar bridge: relation table becomes one market number", "The relation table is converted into a single market-equivalent number by multiplying every cell with a row factor and a column factor, then summing all contributions.", "This matters because it shows exactly how the stronger relational system can be translated back into a classical market economy without pretending that the original table was already just a number."),
        16: ("Row and column factors as political-economic weights", "The part varies the row factors and column factors that turn relation cells into market-equivalent value.", "This is simulated because whoever sets the factors controls how the relational economy becomes a price economy."),
        17: ("Information loss during scalar conversion", "The part collapses rich relation bundles into a single market value and measures what disappears.", "This shows the main trade-off: convertibility creates liquidity, but the single number hides structure."),
        18: ("Arbitrage between relation market and number market", "The part simulates spread, arbitrage and stabilizing circuit breakers between relation bundles and numeric market equivalents.", "This is needed because once conversion exists, traders will exploit differences between relational value and numeric price."),
        19: ("Boom from scalarization and credit expansion", "The part shows how many more bundles become acceptable when a numeric value can be computed for them.", "The boom is simulated because the conversion rule creates liquidity, collateral and credit from formerly hard-to-trade relations."),
        20: ("Amoral conversion of human dependency", "The part deliberately models the dangerous case where work, debt, housing and reputation rows receive market factors.", "This is simulated to expose the moral danger: the formula can hide domination behind a neat numeric result."),
        21: ("Government, tax acceptance and central-bank scalar gates", "The part routes converted values through public acceptance, tax recognition and quality floors.", "A non-numeric currency that can be converted into a number still needs state gates, otherwise bad bundles receive good prices."),
        22: ("Ecological and social cost cells in the conversion matrix", "The part inserts negative cells for emissions, social strain and irreparable limits into the conversion matrix.", "This is simulated because a stronger system should not merely create more trade; it must carry costs that classical prices often hide."),
        23: ("Factor calibration and capture", "The part compares public, market and captured factor-setting regimes.", "The formula is powerful but not neutral. Factor control becomes economic power."),
        24: ("Final conversion dashboard", "The part summarizes how a relational economy can be converted into a classical market economy and what that conversion costs.", "This is the final synthesis: the stronger system becomes interoperable with price markets, but the conversion creates both boom and moral risk."),
    },
    "de": {
        15: ("Skalarbrücke: Relationstabelle wird zu einer Marktzahl", "Die Relationstabelle wird in eine einzelne marktäquivalente Zahl umgerechnet, indem jede Zelle mit einem Zeilenfaktor und einem Spaltenfaktor multipliziert und danach alles summiert wird.", "Das ist wichtig, weil genau sichtbar wird, wie das stärkere relationale System zurück in eine klassische Marktwirtschaft übersetzt werden kann, ohne so zu tun, als sei die ursprüngliche Tabelle schon nur eine Zahl gewesen."),
        16: ("Zeilen- und Spaltenfaktoren als politökonomische Gewichte", "Dieser Teil variiert Zeilenfaktoren und Spaltenfaktoren, die Relationszellen in marktäquivalenten Wert verwandeln.", "Das wird simuliert, weil derjenige, der die Faktoren setzt, kontrolliert, wie die relationale Wirtschaft zur Preiswirtschaft wird."),
        17: ("Informationsverlust bei der Skalarumrechnung", "Dieser Teil verdichtet reiche Relationsbündel zu einem einzelnen Marktwert und misst, was dabei verschwindet.", "Das zeigt den Hauptkonflikt: Umrechenbarkeit erzeugt Liquidität, aber die einzelne Zahl versteckt Struktur."),
        18: ("Arbitrage zwischen Relationsmarkt und Zahlenmarkt", "Dieser Teil simuliert Spanne, Arbitrage und stabilisierende Unterbrecher zwischen Relationsbündeln und numerischen Marktäquivalenten.", "Das ist nötig, weil Händler Unterschiede zwischen relationalem Wert und numerischem Preis ausnutzen werden, sobald Umrechnung möglich ist."),
        19: ("Boom durch Skalarisierung und Kreditausweitung", "Dieser Teil zeigt, wie viel mehr Bündel akzeptiert werden, sobald für sie ein Zahlenwert berechnet werden kann.", "Der Boom wird simuliert, weil die Umrechnungsregel Liquidität, Sicherheiten und Kredit aus vorher schwer handelbaren Relationen erzeugt."),
        20: ("Amoralische Umrechnung menschlicher Abhängigkeit", "Dieser Teil modelliert bewusst den gefährlichen Fall, in dem Arbeit, Schuld, Wohnen und Reputation Marktfaktoren erhalten.", "Das wird simuliert, um die moralische Gefahr sichtbar zu machen: Die Formel kann Herrschaft hinter einem sauberen Zahlenwert verstecken."),
        21: ("Regierung, Steuerakzeptanz und Zentralbank-Skalartore", "Dieser Teil schleust umgerechnete Werte durch öffentliche Anerkennung, Steuerakzeptanz und Qualitätsböden.", "Eine nicht numerische Währung, die in eine Zahl umgerechnet werden kann, braucht trotzdem staatliche Tore; sonst bekommen schlechte Bündel gute Preise."),
        22: ("Ökologische und soziale Kostenzellen in der Umrechnungsmatrix", "Dieser Teil fügt negative Zellen für Emissionen, soziale Belastung und nicht reparierbare Grenzen in die Umrechnungsmatrix ein.", "Das wird simuliert, weil ein stärkeres System nicht nur mehr Handel schaffen soll, sondern Kosten mittragen muss, die klassische Preise oft verstecken."),
        23: ("Faktorkalibrierung und Vereinnahmung", "Dieser Teil vergleicht öffentliche, marktliche und gekaperte Regime der Faktorsetzung.", "Die Formel ist mächtig, aber nicht neutral. Faktorkontrolle wird Wirtschaftsmacht."),
        24: ("Abschließendes Umrechnungs-Dashboard", "Dieser Teil fasst zusammen, wie eine relationale Wirtschaft in eine klassische Marktwirtschaft umgerechnet werden kann und was diese Umrechnung kostet.", "Das ist die Synthese: Das stärkere System wird mit Preismärkten kompatibel, aber die Umrechnung erzeugt Boom und moralisches Risiko zugleich."),
    },
}


def new_part_title(part: int) -> str:
    return NEW_PART_META[LANG][part][0]


def new_part_what_why(part: int) -> Tuple[str, str]:
    meta = NEW_PART_META[LANG][part]
    return meta[1], meta[2]


def print_new_part_header(part: int):
    global ACTIVE_ABBRS, ACTIVE_UNITS
    ACTIVE_ABBRS = {}
    ACTIVE_UNITS = []
    print("\n" + rainbow_rule())
    print(ansi(fit_visible(f"{L('part')} {part:02d}: {new_part_title(part)}", WIDTH), fg=15, bg=25, bold=True))
    print(rainbow_rule())
    what, why = new_part_what_why(part)
    print(section_box(L("what"), what, {}, [], fg=15, bg=24))
    print(section_box(L("why"), why, {}, [], fg=15, bg=53))


def print_utf8_panel(part: int, tag: str, title: str, what: str, why: str,
                     abbrs: Dict[str, str], units: Sequence[Tuple[str, str]],
                     art: str, evaluation: str):
    global ACTIVE_ABBRS, ACTIVE_UNITS
    ACTIVE_ABBRS = dict(abbrs)
    ACTIVE_UNITS = list(units)
    print("\n" + thin_rule())
    print(ansi(f"{L('diagram')} {part}.{tag}: {paint(title, abbrs, units)}", fg=213, bold=True, underline=True))
    print(section_box(L("what"), what, abbrs, units, fg=15, bg=24))
    print(section_box(L("why"), why, abbrs, units, fg=15, bg=53))
    print(section_box(L("reading"), L("legend_hint") + " " + L("unit_hint"), abbrs, units, fg=15, bg=55))
    print(legend_abbr(abbrs, units))
    print(legend_units(units))
    print(ansi(L("diagram"), fg=213, bold=True, underline=True))
    print(art)
    print(section_box(L("evaluation"), evaluation, abbrs, units, fg=15, bg=22))


ROW_KEYS = ["LAB", "CAP", "DAT", "ECO", "LGL", "HUM"]
COL_KEYS = ["QNT", "QLT", "SCY", "RSK", "TR", "DG"]


def row_names():
    if LANG == "en":
        return {
            "LAB": "labour/service row", "CAP": "capacity/assets row", "DAT": "data/proof row",
            "ECO": "ecological row", "LGL": "legal-validity row", "HUM": "human-dependency row",
        }
    return {
        "LAB": "Arbeits- und Dienstleistungszeile", "CAP": "Kapazitäts- und Anlagenzeile", "DAT": "Daten- und Nachweiszeile",
        "ECO": "Umweltzeile", "LGL": "Rechtsgültigkeitszeile", "HUM": "menschliche Abhängigkeitszeile",
    }


def col_names():
    if LANG == "en":
        return {
            "QNT": "quantity column", "QLT": "quality column", "SCY": "scarcity column",
            "RSK": "risk-cost column", "TR": "transferability column", "DG": "dignity-guard column",
        }
    return {
        "QNT": "Mengenspalte", "QLT": "Qualitätsspalte", "SCY": "Knappheitsspalte",
        "RSK": "Risikokostenspalte", "TR": "Übertragbarkeitsspalte", "DG": "Würdeschutzspalte",
    }


def scalar_units(extra: Sequence[str] = ()) -> List[Tuple[str, str]]:
    if LANG == "en":
        base = {
            "pts": "model points", "fac": "dimensionless factor", "MEU": "market-equivalent units",
            "%": "relative share", "rel": "relation rows", "tx": "transactions",
            "cells": "matrix cells", "h": "hours", "kgCO2": "emission burden", "kWh": "energy use",
        }
    else:
        base = {
            "Pkt": "Modellpunkte", "fac": "dimensionsloser Faktor", "MEU": "Marktäquivalent-Einheiten",
            "%": "relativer Anteil", "Rel": "Relationszeilen", "tx": "Transaktionen",
            "Zell": "Matrixzellen", "Std": "Stunden", "kgCO2": "Emissionslast", "kWh": "Energieverbrauch",
        }
    wanted = list(extra)
    out = []
    for k in wanted:
        key = k
        if LANG == "de":
            key = {"pts": "Pkt", "rel": "Rel", "cells": "Zell", "h": "Std"}.get(k, k)
        if key in base:
            out.append((key, base[key]))
    return out


def ukey(unit: str) -> str:
    if LANG == "de":
        return {"pts": "Pkt", "rel": "Rel", "cells": "Zell", "h": "Std"}.get(unit, unit)
    return unit


def valnum(value, unit: str, units: Sequence[Tuple[str, str]], digits=0) -> str:
    return num(value, ukey(unit), units, digits=digits)


def conversion_matrix(seed: int, part: int, scenario_idx: int, tweak=None) -> Dict[str, object]:
    base = dict(BASE_SCENARIOS[scenario_idx])
    if tweak:
        tweak(base, scenario_idx)
    rng = rng_for(seed, part + 100, scenario_idx)
    s = base
    # Row factors: which relation rows carry more market weight.
    rf = {
        "LAB": 0.55 + 1.15 * s["labor"] + 0.15 * s["market"],
        "CAP": 0.70 + 1.05 * s["market"] + 0.20 * s["trust"],
        "DAT": 0.55 + 1.20 * s["data"] + 0.22 * s["platform"],
        "ECO": 0.45 + 1.20 * s["ecology"] + 0.30 * s["state"],
        "LGL": 0.50 + 1.35 * s["state"] + 0.30 * s["trust"],
        "HUM": 0.35 + 1.10 * s["commod"] + 0.45 * s["debt"] - 0.40 * s["state"],
    }
    for k in rf:
        rf[k] = max(0.05, rf[k] + rng.uniform(-0.06, 0.06))
    # Column factors: how much the numeric market rewards or penalizes properties.
    cf = {
        "QNT": 0.55 + 1.05 * s["market"],
        "QLT": 0.65 + 0.95 * s["trust"] + 0.20 * s["state"],
        "SCY": 0.70 + 0.85 * (1 - s["interoperability"]) + 0.35 * s["market"],
        "RSK": -0.35 - 0.90 * s["shock"] - 0.50 * s["debt"],
        "TR": 0.40 + 1.10 * s["interoperability"] + 0.55 * s["market"],
        "DG": 0.45 + 1.10 * s["state"] + 0.65 * s["labor"] - 0.80 * s["commod"],
    }
    for k in cf:
        cf[k] = cf[k] + rng.uniform(-0.05, 0.05)
    # Cell values: relational intensities before row/column factors.
    x = {}
    for r in ROW_KEYS:
        x[r] = {}
        for c in COL_KEYS:
            base_val = 8.0 + rng.uniform(0, 10)
            if r == "LAB": base_val += 18 * s["labor"] + 5 * s["market"]
            if r == "CAP": base_val += 20 * s["market"] + 6 * s["trust"]
            if r == "DAT": base_val += 22 * s["data"] + 10 * s["platform"]
            if r == "ECO": base_val += 18 * (1 - s["external"]) + 12 * s["ecology"]
            if r == "LGL": base_val += 20 * s["state"] + 9 * s["trust"]
            if r == "HUM": base_val += 25 * s["commod"] + 16 * s["debt"] + 6 * s["platform"]
            if c == "QNT": base_val += 7 * s["market"]
            if c == "QLT": base_val += 8 * s["trust"]
            if c == "SCY": base_val += 8 * (1 - s["interoperability"])
            if c == "RSK": base_val += 12 * s["shock"] + 9 * s["debt"]
            if c == "TR": base_val += 11 * s["interoperability"]
            if c == "DG": base_val += 10 * s["state"] + 8 * s["labor"]
            # Risk column and ecological/human burdens can be negative cells.
            if c == "RSK":
                base_val = -base_val
            if r == "ECO" and c in ("RSK", "DG") and s["external"] > 0.5:
                base_val -= 10 * s["external"]
            if r == "HUM" and c in ("RSK", "DG") and s["commod"] > 0.55:
                base_val -= 18 * s["commod"]
            x[r][c] = base_val
    contrib = {r: {c: x[r][c] * rf[r] * cf[c] for c in COL_KEYS} for r in ROW_KEYS}
    mev = sum(contrib[r][c] for r in ROW_KEYS for c in COL_KEYS)
    gross = sum(abs(contrib[r][c]) for r in ROW_KEYS for c in COL_KEYS)
    neg = sum(-contrib[r][c] for r in ROW_KEYS for c in COL_KEYS if contrib[r][c] < 0)
    pos = sum(contrib[r][c] for r in ROW_KEYS for c in COL_KEYS if contrib[r][c] > 0)
    info_loss = clamp(10 + 28 * s["market"] + 32 * s["data"] + 28 * s["commod"] + 16 * s["platform"] - 28 * s["state"] - 10 * s["trust"] + jitter(rng, 2))
    dgr = clamp(8 + 58 * s["commod"] + 30 * s["debt"] + 20 * s["platform"] + 8 * s["data"] - 42 * s["state"] - 22 * s["labor"] + jitter(rng, 2))
    convertibility = clamp(40 + 0.020 * mev + 45 * s["interoperability"] + 30 * s["trust"] - 0.35 * info_loss)
    numeric_boom = clamp(18 + 0.025 * mev + 32 * s["market"] + 18 * s["data"] - 0.20 * dgr - 0.12 * info_loss)
    return {
        "scenario": scenario_name(s), "key": s["key"], "s": s, "rf": rf, "cf": cf, "x": x,
        "contrib": contrib, "mev": mev, "gross": gross, "negative": neg, "positive": pos,
        "info_loss": info_loss, "dgr": dgr, "convertibility": convertibility, "numeric_boom": numeric_boom,
        "relations": int(24 + 90 * s["market"] + 48 * s["data"] + rng.uniform(-3, 4)),
        "tx": int(6 + 70 * s["market"] + 28 * s["interoperability"] - 20 * s["shock"] + rng.uniform(-2, 3)),
        "hours": int(60 + 170 * s["market"] + 45 * s["labor"] + rng.uniform(-8, 9)),
        "kwh": int(400 + 520 * s["market"] + 250 * (1 - s["ecology"]) + rng.uniform(-30, 31)),
        "kgco2": int(160 + 480 * s["external"] + 220 * (1 - s["ecology"]) + rng.uniform(-25, 26)),
    }


def conversion_rows(seed: int, part: int, tweak=None) -> List[Dict[str, object]]:
    return [conversion_matrix(seed, part, i, tweak=tweak) for i in range(len(BASE_SCENARIOS))]


def best_conv_balance(rows):
    return max(rows, key=lambda r: 0.20 * r["numeric_boom"] + 0.20 * r["convertibility"] + 0.18 * (100 - r["info_loss"]) + 0.22 * (100 - r["dgr"]) + 0.20 * max(0, r["mev"] / 20))


def conv_outcome_summary(rows, abbrs, units):
    high_mev = max(rows, key=lambda r: r["mev"])
    high_boom = max(rows, key=lambda r: r["numeric_boom"])
    high_loss = max(rows, key=lambda r: r["info_loss"])
    high_dgr = max(rows, key=lambda r: r["dgr"])
    balance = best_conv_balance(rows)
    if LANG == "en":
        txt = (f"Highest MEV: {high_mev['scenario']} with {high_mev['mev']:.0f} MEU. "
               f"Highest numeric boom: {high_boom['scenario']} with {high_boom['numeric_boom']:.0f} pts. "
               f"Highest ILS: {high_loss['scenario']} with {high_loss['info_loss']:.0f} pts. "
               f"Highest DGR: {high_dgr['scenario']} with {high_dgr['dgr']:.0f} pts. "
               f"Best balance: {balance['scenario']}. The conversion works, but it does not come free: the easier the table becomes a price, the easier hidden structure becomes invisible.")
    else:
        txt = (f"Höchster MEV: {high_mev['scenario']} mit {high_mev['mev']:.0f} MEU. "
               f"Stärkster Zahlenboom: {high_boom['scenario']} mit {high_boom['numeric_boom']:.0f} Pkt. "
               f"Höchster ILS: {high_loss['scenario']} mit {high_loss['info_loss']:.0f} Pkt. "
               f"Höchster DGR: {high_dgr['scenario']} mit {high_dgr['dgr']:.0f} Pkt. "
               f"Bestes Gleichgewicht: {balance['scenario']}. Die Umrechnung funktioniert, aber sie ist nicht kostenlos: Je leichter die Tabelle zum Preis wird, desto leichter wird versteckte Struktur unsichtbar.")
    return paint(txt, abbrs, units)


def conv_table(rows, units, title=None):
    headers = [L("scenario"), "MEV", "ILS", "DGR", "CNV", "NBM"]
    data = []
    for r in rows:
        data.append([
            r["scenario"],
            valnum(r["mev"], "MEU", units),
            bar(r["info_loss"], good=False),
            bar(r["dgr"], good=False),
            bar(r["convertibility"], good=True),
            bar(r["numeric_boom"], good=True),
        ])
    return table(headers, data, ["left", "right", "left", "left", "left", "left"], title or ("Conversion scenarios" if LANG == "en" else "Umrechnungs-Szenarien"))


def heat_values_for_contrib(one):
    # Heat needs positive range. Negative contributions are shown by absolute heat;
    # the evaluation text explains that RSK/DG burdens can pull the total down.
    return [[min(100, abs(one["contrib"][r][c]) / 8.0) for c in COL_KEYS] for r in ROW_KEYS]


def top_contributions(one, n=5):
    items = []
    for r in ROW_KEYS:
        for c in COL_KEYS:
            items.append((one["contrib"][r][c], r, c))
    return sorted(items, key=lambda x: abs(x[0]), reverse=True)[:n]


def art_formula_cell(one, abbrs, units):
    # Pick a stable demonstrator cell and build a width-consistent box.
    x = one["x"]["LAB"]["QLT"]
    rf = one["rf"]["LAB"]
    cf = one["cf"]["QLT"]
    con = x * rf * cf
    pt = ukey("pts")
    fac = ukey("fac")
    meu = ukey("MEU")
    body = []
    body.append("MEV = SUM( XIJ × RFA × CFA )")
    if LANG == "en":
        body.append(f"example: XIJ {x:6.1f} {pt} × RFA {rf:4.2f} {fac} × CFA {cf:4.2f} {fac}")
        body.append(f"result : {con:8.1f} {meu} for one cell")
        tail = "relation table ──► weighted cells ──► one market number"
    else:
        body.append(f"Beispiel: XIJ {x:6.1f} {pt} × RFA {rf:4.2f} {fac} × CFA {cf:4.2f} {fac}")
        body.append(f"Ergebnis: {con:8.1f} {meu} für eine Zelle")
        tail = "Relationstabelle ─► gewichtete Zellen ─► eine Marktzahl"
    inner = min(max(max(vlen(b) for b in body) + 4, 58), max(58, WIDTH - 2))
    lines = ["╔" + "═" * inner + "╗"]
    lines.append("║" + pad(body[0], inner, "center") + "║")
    lines.append("╠" + "═" * inner + "╣")
    for b in body[1:]:
        lines.append("║ " + pad(b, inner - 2) + "║")
    lines.append("╚" + "═" * inner + "╝")
    lines.append(tail)
    return line_art(lines, abbrs, units)

def art_factor_grid(one, abbrs, units, title=""):
    rn = row_names(); cn = col_names()
    rows = []
    for r in ROW_KEYS:
        rows.append([r, rn[r], valnum(one["rf"][r], "fac", units, digits=2), mini_bar(one["rf"][r], 2.2, 14, abbr_color(r, abbrs))])
    cfrows = []
    for c in COL_KEYS:
        cfrows.append([c, cn[c], valnum(one["cf"][c], "fac", units, digits=2), mini_bar(abs(one["cf"][c]), 1.8, 14, abbr_color(c, abbrs))])
    return table(["RFA", "Row" if LANG == "en" else "Zeile", "fac", ""], rows, ["left", "left", "right", "left"], title or ("Row factors" if LANG == "en" else "Zeilenfaktoren")) + "\n" + table(["CFA", "Column" if LANG == "en" else "Spalte", "fac", ""], cfrows, ["left", "left", "right", "left"], "Column factors" if LANG == "en" else "Spaltenfaktoren")


def art_contribution_heat(one, abbrs, units):
    return matrix(COL_KEYS, ROW_KEYS, heat_values_for_contrib(one), "CON heat: |XIJ × RFA × CFA|" if LANG == "en" else "CON-Hitze: |XIJ × RFA × CFA|")


def art_scenario_bars(rows, abbrs, units):
    lines = []
    pt = ukey("pts")
    meu = ukey("MEU")
    if LANG == "en":
        lines.append("MEV bars convert relation tables into numeric market equivalents")
    else:
        lines.append("MEV-Balken übersetzen Relationstabellen in numerische Marktäquivalente")
    max_mev = max(abs(r["mev"]) for r in rows) or 1
    for r in rows:
        width = max(8, min(34, WIDTH - 34))
        b = mini_bar(max(0, r["mev"]), max_mev, width, 46 if r["mev"] >= 0 else 196)
        lines.append(f"{r['scenario']:<13} MEV {b} {r['mev']:8.0f} {meu}   ILS {r['info_loss']:5.1f} {pt}   DGR {r['dgr']:5.1f} {pt}")
    return line_art(lines, abbrs, units)

def art_loss_funnel(rows, abbrs, units):
    avg_mev = sum(r["mev"] for r in rows) / len(rows)
    avg_ils = sum(r["info_loss"] for r in rows) / len(rows)
    avg_dgr = sum(r["dgr"] for r in rows) / len(rows)
    pt = ukey("pts")
    meu = ukey("MEU")
    if LANG == "en":
        lines = [
            "rich relation table",
            "   ╲  rights │ duties │ risk │ time │ proof │ dignity  ╱",
            "    ╲_______________________________________________╱",
            "                      ▼",
            f"                 MEV {avg_mev:7.0f} {meu}",
            "                      ▼",
            f"      hidden after collapse: ILS {avg_ils:5.1f} {pt} | DGR {avg_dgr:5.1f} {pt}",
        ]
    else:
        lines = [
            "reiche Relationstabelle",
            "   ╲ Rechte │ Pflichten │ Risiko │ Zeit │ Nachweis │ Würde ╱",
            "    ╲_____________________________________________________╱",
            "                         ▼",
            f"                    MEV {avg_mev:7.0f} {meu}",
            "                         ▼",
            f"       nach Verdichtung versteckt: ILS {avg_ils:5.1f} {pt} | DGR {avg_dgr:5.1f} {pt}",
        ]
    return line_art(lines, abbrs, units)

def art_waterfall(one, abbrs, units):
    totals = []
    for r in ROW_KEYS:
        totals.append((r, sum(one["contrib"][r][c] for c in COL_KEYS)))
    max_abs = max(abs(v) for _, v in totals) or 1
    lines = ["CON waterfall" if LANG == "en" else "CON-Wasserfall"]
    for r, v in totals:
        col = 46 if v >= 0 else 196
        prefix = "+" if v >= 0 else "-"
        lines.append(f"{r:<4} {prefix} {mini_bar(abs(v), max_abs, max(8, min(32, WIDTH - 20)), col)} {v:8.0f} MEU")
    lines.append(f"SUM  = {one['mev']:8.0f} MEU")
    return line_art(lines, abbrs, units)


def art_arbitrage_loop(rows, abbrs, units):
    spreads = []
    for r in rows:
        market_price = r["mev"] * (0.82 + 0.004 * r["convertibility"] - 0.002 * r["info_loss"])
        spread = r["mev"] - market_price
        spreads.append((r, spread))
    lines = [
        "╭────────────╮      SPY       ╭────────────╮" if LANG == "en" else "╭────────────╮      SPY       ╭────────────╮",
        "│ relation   │ ────────────► │ price      │" if LANG == "en" else "│ Relation   │ ────────────► │ Preis      │",
        "│ bundle     │ ◄──────────── │ market     │" if LANG == "en" else "│ Bündel     │ ◄──────────── │ Markt      │",
        "╰────────────╯      ARB       ╰────────────╯",
    ]
    max_spread = max(abs(s) for _, s in spreads) or 1
    for r, spread in spreads:
        col = 46 if spread >= 0 else 196
        lines.append(f"{r['scenario']:<13} SPR {mini_bar(abs(spread), max_spread, max(8, min(28, WIDTH - 28)), col)} {spread:7.0f} MEU")
    return line_art(lines, abbrs, units)


def art_credit_multiplier(rows, abbrs, units):
    lines = ["SCM turns MEV into collateral and credit velocity" if LANG == "en" else "SCM macht aus MEV Sicherheiten und Kreditgeschwindigkeit"]
    for r in rows:
        collateral = max(0, r["mev"] * (0.35 + 0.006 * r["convertibility"]))
        multiplier = max(0.3, 0.8 + r["numeric_boom"] / 45 - r["dgr"] / 120)
        credit = collateral * multiplier
        lines.append(f"{r['scenario']:<13} COL {collateral:7.0f} MEU × MUL {multiplier:4.2f} fac = CRD {credit:8.0f} MEU")
    return line_art(lines, abbrs, units)


def art_control_stack(rows, abbrs, units):
    target = max(rows, key=lambda r: r["dgr"])
    pt = ukey("pts")
    lines = [
        "HCP stack: many rows create practical control" if LANG == "en" else "HCP-Stapel: viele Zeilen erzeugen praktische Kontrolle",
        "┌──────────────┐",
        f"│ DAT {target['s']['data']*100:5.1f}%    │",
        "├──────────────┤",
        f"│ DEB {target['s']['debt']*100:5.1f}%    │",
        "├──────────────┤",
        f"│ WRK {target['s']['labor']*100:5.1f}%    │",
        "├──────────────┤",
        f"│ HOU {target['s']['commod']*100:5.1f}%    │",
        "├──────────────┤",
        f"│ DGR {target['dgr']:5.1f} {pt} │",
        "└──────────────┘",
    ]
    return line_art(lines, abbrs, units)

def art_gate(rows, abbrs, units):
    lines = [
        "incoming MEV ──► QFG ──► TAX / CLR" if LANG == "en" else "eingehender MEV ──► QFG ──► TAX / CLR",
        "                 │",
        "                 ├──► QRT for toxic rows" if LANG == "en" else "                 ├──► QRT für toxische Zeilen",
        "                 │",
        "                 └──► NTR if human boundary is touched" if LANG == "en" else "                 └──► NTR, wenn Menschengrenze berührt wird",
    ]
    for r in rows:
        accept = clamp(r["convertibility"] - 0.45 * r["dgr"] - 0.25 * r["info_loss"] + 35)
        lines.append(f"{r['scenario']:<13} QFG {bar(accept, width=max(8, min(18, WIDTH//6)), good=True)}")
    return line_art(lines, abbrs, units)


def art_ecology_cost(rows, abbrs, units):
    lines = ["NEG cells reduce MEV before the price is accepted" if LANG == "en" else "NEG-Zellen senken MEV, bevor der Preis akzeptiert wird"]
    for r in rows:
        eco_cost = max(0, r["kgco2"] * (0.6 + r["s"]["external"]))
        gross = r["positive"]
        net = r["mev"]
        lines.append(f"{r['scenario']:<13} GRS {gross:7.0f} MEU - NEG {eco_cost:6.0f} MEU = NET {net:7.0f} MEU  EMS {r['kgco2']:4d} kgCO2")
    return line_art(lines, abbrs, units)


def art_tornado(rows, abbrs, units):
    base = rows[0]
    sens = []
    for key in ROW_KEYS:
        sens.append(("RFA-" + key, abs(base["rf"][key]) * sum(abs(base["x"][key][c] * base["cf"][c]) for c in COL_KEYS)))
    for key in COL_KEYS:
        sens.append(("CFA-" + key, abs(base["cf"][key]) * sum(abs(base["x"][r][key] * base["rf"][r]) for r in ROW_KEYS)))
    sens.sort(key=lambda x: x[1], reverse=True)
    max_s = sens[0][1] or 1
    lines = ["SEN tornado: which factor moves MEV most" if LANG == "en" else "SEN-Tornado: welcher Faktor MEV am stärksten bewegt"]
    for name, val in sens[:10]:
        lines.append(f"{name:<8} {mini_bar(val, max_s, max(8, min(34, WIDTH - 20)), 214)} {val:7.0f} MEU")
    return line_art(lines, abbrs, units)


def art_capture_triangle(rows, abbrs, units):
    lines = [
        "                 PUB" if LANG == "en" else "                 PUB",
        "                /   \\",
        "               /     \\",
        "          CAL /       \\ CAL",
        "             /         \\",
        "          MKT ─── CAP ─── PLT",
    ]
    for r in rows:
        capture = clamp(35 * r["s"]["platform"] + 35 * r["s"]["commod"] + 25 * r["s"]["debt"] - 35 * r["s"]["state"])
        lines.append(f"{r['scenario']:<13} CAP {bar(capture, width=max(8, min(18, WIDTH//6)), good=False)}")
    return line_art(lines, abbrs, units)


def art_final_dashboard(rows, abbrs, units):
    labels = [r["scenario"][:10] for r in rows]
    vals = [[r["numeric_boom"], 100 - r["info_loss"], 100 - r["dgr"], r["convertibility"]] for r in rows]
    return matrix(["NBM", "VIS", "DGS", "CNV"], labels, vals, "Final scalar dashboard" if LANG == "en" else "Abschluss-Skalardashboard")


def local_formula_abbrs():
    if LANG == "en":
        return {
            "XIJ": "Cell value: the raw numeric content of one relation-table cell before factors are applied.",
            "RFA": "Row factor: the multiplier attached to the row type, such as labour, data, ecology or legal validity.",
            "CFA": "Column factor: the multiplier attached to the column type, such as quantity, risk or transferability.",
            "SUM": "Summation rule: all weighted cell contributions are added into one market-equivalent number.",
            "MEV": "Market-equivalent value: the single number obtained after the relational table is converted.",
        }
    return {
        "XIJ": "Zellenwert: der rohe numerische Inhalt einer Relationszelle, bevor Faktoren angewendet werden.",
        "RFA": "Zeilenfaktor: der Multiplikator der Zeilenart, etwa Arbeit, Daten, Ökologie oder Rechtsgültigkeit.",
        "CFA": "Spaltenfaktor: der Multiplikator der Spaltenart, etwa Menge, Risiko oder Übertragbarkeit.",
        "SUM": "Summenregel: Alle gewichteten Zellbeiträge werden zu einer marktäquivalenten Zahl addiert.",
        "MEV": "Marktäquivalenter Wert: die einzelne Zahl nach der Umrechnung der relationalen Tabelle.",
    }


def local_matrix_abbrs(extra=None):
    rn = row_names(); cn = col_names()
    if LANG == "en":
        base = {"CON": "Contribution: the weighted cell result XIJ × RFA × CFA."}
    else:
        base = {"CON": "Beitrag: das gewichtete Zellergebnis XIJ × RFA × CFA."}
    for k in ROW_KEYS: base[k] = rn[k]
    for k in COL_KEYS: base[k] = cn[k]
    if extra: base.update(extra)
    return base


def run_part_15(seed: int):
    part = 15; print_new_part_header(part)
    rows = conversion_rows(seed, part)
    one = rows[0]
    ab = local_formula_abbrs(); un = scalar_units(["pts", "fac", "MEU"])
    print_utf8_panel(part, "A", "Cell × row factor × column factor" if LANG == "en" else "Zelle × Zeilenfaktor × Spaltenfaktor",
        "A single relation-table cell is multiplied as XIJ × RFA × CFA; the SUM over all cells becomes MEV." if LANG == "en" else "Eine einzelne Relationszelle wird als XIJ × RFA × CFA multipliziert; die SUM über alle Zellen wird zu MEV.",
        "This is the exact bridge back into a classical market number: the table stays rich, but the market receives one calculable value." if LANG == "en" else "Das ist die genaue Brücke zurück zur klassischen Marktzahl: Die Tabelle bleibt reich, aber der Markt bekommt einen berechenbaren Wert.",
        ab, un, art_formula_cell(one, ab, un),
        conv_outcome_summary(rows, ab, un))
    ab = local_matrix_abbrs({"XIJ": "Cell value before factors." if LANG == "en" else "Zellenwert vor den Faktoren.", "RFA": "Row factor." if LANG == "en" else "Zeilenfaktor.", "CFA": "Column factor." if LANG == "en" else "Spaltenfaktor."}); un = scalar_units(["MEU", "fac"])
    print_utf8_panel(part, "B", "Contribution heatmap" if LANG == "en" else "Beitrags-Heatmap",
        "The heatmap shows which row-column intersections create the largest absolute weighted contributions." if LANG == "en" else "Die Heatmap zeigt, welche Zeilen-Spalten-Schnittpunkte die größten absoluten gewichteten Beiträge erzeugen.",
        "It is simulated because the final number hides where its power came from." if LANG == "en" else "Das wird simuliert, weil die Endzahl versteckt, woher ihre Kraft kam.",
        ab, un, art_contribution_heat(one, ab, un),
        "The biggest cells show that MEV is not produced by row counting; it is produced by weighted structure." if LANG == "en" else "Die größten Zellen zeigen: MEV entsteht nicht durch Zeilenzählen, sondern durch gewichtete Struktur.")
    ab = {"MEV": "Market-equivalent value after conversion." if LANG == "en" else "Marktäquivalenter Wert nach der Umrechnung.", "ILS": "Information loss score after collapsing the table." if LANG == "en" else "Informationsverlust nach der Verdichtung der Tabelle.", "DGR": "Dignity risk created when human-dependency rows receive market weight." if LANG == "en" else "Würderisiko, wenn menschliche Abhängigkeitszeilen Marktgewicht erhalten."}; un = scalar_units(["MEU", "pts"])
    print_utf8_panel(part, "C", "Scenario scalar bars" if LANG == "en" else "Szenario-Skalarbalken",
        "Four scenarios are converted into MEV while ILS and DGR remain visible beside the number." if LANG == "en" else "Vier Szenarien werden in MEV umgerechnet, während ILS und DGR neben der Zahl sichtbar bleiben.",
        "This prevents the conversion from pretending that the number alone is the whole truth." if LANG == "en" else "Das verhindert, dass die Umrechnung so tut, als sei die Zahl allein die ganze Wahrheit.",
        ab, un, art_scenario_bars(rows, ab, un), conv_outcome_summary(rows, ab, un))


def run_part_16(seed: int):
    part = 16; print_new_part_header(part)
    rows = conversion_rows(seed, part, lambda s, i: s.update({"state": min(1, s["state"] + (0.10 if s["key"] == "guarded" else 0)), "interoperability": min(1, s["interoperability"] + 0.05)}))
    one = rows[1]
    ab = local_matrix_abbrs({"RFA": "Row factor used as the row-side multiplier." if LANG == "en" else "Zeilenfaktor als zeilenseitiger Multiplikator.", "CFA": "Column factor used as the column-side multiplier." if LANG == "en" else "Spaltenfaktor als spaltenseitiger Multiplikator."}); un = scalar_units(["fac"])
    print_utf8_panel(part, "A", "Factor ladders" if LANG == "en" else "Faktorenleitern",
        "Each row type receives RFA and each column type receives CFA." if LANG == "en" else "Jede Zeilenart erhält RFA und jede Spaltenart erhält CFA.",
        "This is simulated because factor-setting decides what the classical market will reward." if LANG == "en" else "Das wird simuliert, weil Faktorsetzung entscheidet, was der klassische Markt belohnt.",
        ab, un, art_factor_grid(one, ab, un),
        "Higher factors do not create reality; they select which relations are amplified in the numeric market." if LANG == "en" else "Höhere Faktoren erschaffen keine Wirklichkeit; sie wählen aus, welche Relationen im Zahlenmarkt verstärkt werden.")
    ab = {"CON": "Weighted contribution of a row to MEV." if LANG == "en" else "Gewichteter Beitrag einer Zeile zu MEV.", "SUM": "Total sum of all row contributions." if LANG == "en" else "Gesamtsumme aller Zeilenbeiträge."}; un = scalar_units(["MEU"])
    print_utf8_panel(part, "B", "Contribution waterfall" if LANG == "en" else "Beitrags-Wasserfall",
        "The waterfall adds positive and negative row contributions into one MEV." if LANG == "en" else "Der Wasserfall addiert positive und negative Zeilenbeiträge zu einem MEV.",
        "This makes clear that burdens and risks can reduce the converted market value." if LANG == "en" else "Das macht sichtbar, dass Lasten und Risiken den umgerechneten Marktwert senken können.",
        ab, un, art_waterfall(one, ab, un),
        f"{one['scenario']} converts to {one['mev']:.0f} MEU; negative rows are not errors but costs carried into the number." if LANG == "en" else f"{one['scenario']} wird zu {one['mev']:.0f} MEU; negative Zeilen sind keine Fehler, sondern in die Zahl mitgenommene Kosten.")
    ab = {"SEN": "Sensitivity: how strongly changing a factor would move MEV." if LANG == "en" else "Sensitivität: wie stark eine Faktoränderung MEV bewegen würde.", "RFA": "Row factor." if LANG == "en" else "Zeilenfaktor.", "CFA": "Column factor." if LANG == "en" else "Spaltenfaktor.", "MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert."}; un = scalar_units(["MEU"])
    print_utf8_panel(part, "C", "Sensitivity tornado" if LANG == "en" else "Sensitivitäts-Tornado",
        "The tornado ranks which factors move MEV most." if LANG == "en" else "Der Tornado ordnet, welche Faktoren MEV am stärksten bewegen.",
        "This is simulated because the formula becomes political at exactly the points where sensitivity is high." if LANG == "en" else "Das wird simuliert, weil die Formel genau dort politisch wird, wo Sensitivität hoch ist.",
        ab, un, art_tornado(rows, ab, un), conv_outcome_summary(rows, ab, un))


def run_part_17(seed: int):
    part = 17; print_new_part_header(part)
    rows = conversion_rows(seed, part, lambda s, i: s.update({"data": min(1, s["data"] + 0.10), "market": min(1, s["market"] + 0.08)}))
    ab = {"MEV": "Single market-equivalent value produced by collapse." if LANG == "en" else "Einzelner marktäquivalenter Wert durch Verdichtung.", "ILS": "Information loss score." if LANG == "en" else "Informationsverlustwert.", "DGR": "Dignity risk score." if LANG == "en" else "Würderisikowert."}; un = scalar_units(["MEU", "pts"])
    print_utf8_panel(part, "A", "Collapse funnel" if LANG == "en" else "Verdichtungstrichter",
        "A wide relation table is squeezed through the conversion formula into MEV." if LANG == "en" else "Eine breite Relationstabelle wird durch die Umrechnungsformel zu MEV verdichtet.",
        "This is simulated because a classical market number is useful exactly because it forgets detail." if LANG == "en" else "Das wird simuliert, weil eine klassische Marktzahl gerade deshalb nützlich ist, weil sie Details vergisst.",
        ab, un, art_loss_funnel(rows, ab, un), conv_outcome_summary(rows, ab, un))
    ab = {"MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert.", "ILS": "Lost structural information." if LANG == "en" else "Verlorene Strukturinformation.", "DGR": "Risk of treating people as priced dependency bundles." if LANG == "en" else "Risiko, Menschen als bepreiste Abhängigkeitsbündel zu behandeln."}; un = scalar_units(["MEU", "pts"])
    print_utf8_panel(part, "B", "Conversion table" if LANG == "en" else "Umrechnungstabelle",
        "The table keeps MEV, ILS and DGR next to each other." if LANG == "en" else "Die Tabelle hält MEV, ILS und DGR nebeneinander sichtbar.",
        "This is simulated to prevent the scalar number from becoming a false moral simplification." if LANG == "en" else "Das wird simuliert, damit die Skalarzahl keine falsche moralische Vereinfachung wird.",
        ab, un, conv_table(rows, un), conv_outcome_summary(rows, ab, un))
    ab = {"VIS": "Visible structure after conversion." if LANG == "en" else "Sichtbare Struktur nach der Umrechnung.", "ILS": "Information loss score." if LANG == "en" else "Informationsverlustwert.", "MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert."}; un = scalar_units(["pts", "MEU"])
    labels = [r["scenario"][:10] for r in rows]
    vals = [[100 - r["info_loss"], r["info_loss"], min(100, abs(r["mev"])/25)] for r in rows]
    print_utf8_panel(part, "C", "Visibility heatmap" if LANG == "en" else "Sichtbarkeits-Heatmap",
        "The heatmap contrasts remaining visibility with loss and converted value." if LANG == "en" else "Die Heatmap stellt verbleibende Sichtbarkeit, Verlust und umgerechneten Wert gegenüber.",
        "This shows why the relational system is stronger: it can keep the hidden columns visible even when a number is produced." if LANG == "en" else "Das zeigt, warum das relationale System stärker ist: Es kann die versteckten Spalten sichtbar halten, obwohl eine Zahl erzeugt wird.",
        ab, un, matrix(["VIS", "ILS", "MEV"], labels, vals, "VIS/ILS/MEV"), conv_outcome_summary(rows, ab, un))


def run_part_18(seed: int):
    part = 18; print_new_part_header(part)
    rows = conversion_rows(seed, part, lambda s, i: s.update({"market": min(1, s["market"] + 0.12), "shock": min(1, s["shock"] + (0.06 if s["key"] in ("spec", "dark") else 0))}))
    ab = {"SPY": "Spread yield: gain from difference between relation value and price value." if LANG == "en" else "Spannenertrag: Gewinn aus Differenz zwischen Relationswert und Preiswert.", "ARB": "Arbitrage loop: repeated conversion to exploit price gaps." if LANG == "en" else "Arbitrage-Schleife: wiederholte Umrechnung zur Ausnutzung von Preislücken.", "SPR": "Spread between MEV and market price." if LANG == "en" else "Spanne zwischen MEV und Marktpreis.", "MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert."}; un = scalar_units(["MEU"])
    print_utf8_panel(part, "A", "Arbitrage loop" if LANG == "en" else "Arbitrage-Schleife",
        "A trader can move between relation bundles and numeric price markets when spreads appear." if LANG == "en" else "Ein Händler kann zwischen Relationsbündeln und Zahlenpreismärkten wechseln, wenn Spannen auftreten.",
        "This is simulated because convertibility always creates a bridge, and every bridge creates arbitrage." if LANG == "en" else "Das wird simuliert, weil Umrechenbarkeit immer eine Brücke erzeugt, und jede Brücke erzeugt Arbitrage.",
        ab, un, art_arbitrage_loop(rows, ab, un), conv_outcome_summary(rows, ab, un))
    ab = {"MEV": "Converted relation value." if LANG == "en" else "Umgerechneter Relationswert.", "ILS": "Information loss score." if LANG == "en" else "Informationsverlustwert.", "DGR": "Dignity risk score." if LANG == "en" else "Würderisikowert."}; un = scalar_units(["MEU", "pts"])
    print_utf8_panel(part, "B", "Spread risk table" if LANG == "en" else "Spannenrisiko-Tabelle",
        "The same converted value can be profitable while carrying hidden loss and dignity risk." if LANG == "en" else "Derselbe umgerechnete Wert kann profitabel sein und zugleich versteckten Verlust und Würderisiko tragen.",
        "This shows the price of strength: a stronger bridge also makes exploitation faster." if LANG == "en" else "Das zeigt den Preis der Stärke: Eine stärkere Brücke macht auch Ausbeutung schneller.",
        ab, un, conv_table(rows, un, "ARB risk" if LANG == "en" else "ARB-Risiko"), conv_outcome_summary(rows, ab, un))
    ab = {"CBR": "Circuit breaker: public interruption of unsafe conversion loops." if LANG == "en" else "Schutzunterbrecher: öffentliche Unterbrechung unsicherer Umrechnungsschleifen.", "SPR": "Market spread." if LANG == "en" else "Marktspanne.", "QFG": "Quality floor gate." if LANG == "en" else "Qualitätsboden-Tor."}; un = scalar_units(["pts"])
    lines = ["SPR high ──► CBR ──► QFG review ──► reopen or quarantine" if LANG == "en" else "SPR hoch ──► CBR ──► QFG-Prüfung ──► Öffnung oder Quarantäne"]
    for r in rows:
        cbr = clamp(r["info_loss"] * 0.45 + r["dgr"] * 0.55)
        lines.append(f"{r['scenario']:<13} CBR {bar(cbr, good=False)}")
    print_utf8_panel(part, "C", "Circuit breaker" if LANG == "en" else "Schutzunterbrecher",
        "The circuit breaker interrupts conversion when spread trading becomes unsafe." if LANG == "en" else "Der Schutzunterbrecher stoppt Umrechnung, wenn Spannenhandel unsicher wird.",
        "This is simulated because no serious scalar bridge can survive without public interruption rules." if LANG == "en" else "Das wird simuliert, weil keine ernsthafte Skalarbrücke ohne öffentliche Unterbrechungsregeln überlebt.",
        ab, un, line_art(lines, ab, un), "High CBR means the market number is moving faster than legal and moral verification." if LANG == "en" else "Hoher CBR bedeutet, dass die Marktzahl schneller läuft als rechtliche und moralische Prüfung.")


def run_part_19(seed: int):
    part = 19; print_new_part_header(part)
    rows = conversion_rows(seed, part, lambda s, i: s.update({"market": min(1, s["market"] + 0.18), "debt": min(1, s["debt"] + 0.12), "data": min(1, s["data"] + 0.06)}))
    ab = {"SCM": "Scalar conversion mechanism: the rule that turns the relation table into one number." if LANG == "en" else "Skalarumrechnungsmechanismus: die Regel, die die Relationstabelle in eine Zahl verwandelt.", "COL": "Collateral generated from converted value." if LANG == "en" else "Sicherheit, die aus umgerechnetem Wert entsteht.", "MUL": "Credit multiplier." if LANG == "en" else "Kreditmultiplikator.", "CRD": "Credit capacity." if LANG == "en" else "Kreditkapazität.", "MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert."}; un = scalar_units(["MEU", "fac"])
    print_utf8_panel(part, "A", "Credit multiplier from conversion" if LANG == "en" else "Kreditmultiplikator aus Umrechnung",
        "Converted MEV becomes collateral, and collateral becomes credit capacity." if LANG == "en" else "Umgerechneter MEV wird zur Sicherheit, und Sicherheit wird zur Kreditkapazität.",
        "This is the boom engine: formerly complex bundles become acceptable to lenders." if LANG == "en" else "Das ist die Boommaschine: Früher komplexe Bündel werden für Kreditgeber akzeptabel.",
        ab, un, art_credit_multiplier(rows, ab, un), conv_outcome_summary(rows, ab, un))
    ab = {"NBM": "Numeric boom meter after scalar conversion." if LANG == "en" else "Zahlenboom-Messer nach Skalarumrechnung.", "CNV": "Convertibility score." if LANG == "en" else "Umrechenbarkeitswert.", "TXF": "Transaction flow created by the bridge." if LANG == "en" else "Transaktionsfluss durch die Brücke."}; un = scalar_units(["tx", "pts"])
    lines = ["CNV opens more TXF; NBM rises until risk overloads verification" if LANG == "en" else "CNV öffnet mehr TXF; NBM steigt, bis Risiko die Prüfung überlastet"]
    for r in rows:
        lines.append(f"{r['scenario']:<13} CNV {bar(r['convertibility'], good=True)} TXF {valnum(r['tx'], 'tx', un)} NBM {r['numeric_boom']:5.1f} {ukey('pts')}")
    print_utf8_panel(part, "B", "Boom flow" if LANG == "en" else "Boomfluss",
        "The flow diagram connects convertibility, transactions and numeric boom." if LANG == "en" else "Das Flussbild verbindet Umrechenbarkeit, Transaktionen und Zahlenboom.",
        "It shows why the scalar bridge can outperform a plain market: more relation assets become liquid." if LANG == "en" else "Es zeigt, warum die Skalarbrücke eine bloße Marktwirtschaft übertreffen kann: Mehr Relationswerte werden liquide.",
        ab, un, line_art(lines, ab, un), conv_outcome_summary(rows, ab, un))
    ab = {"FRG": "Fragility score from credit, loss and dignity risk." if LANG == "en" else "Fragilitätswert aus Kredit, Verlust und Würderisiko.", "CRD": "Credit capacity." if LANG == "en" else "Kreditkapazität.", "ILS": "Information loss score." if LANG == "en" else "Informationsverlustwert.", "DGR": "Dignity risk score." if LANG == "en" else "Würderisikowert."}; un = scalar_units(["pts"])
    lines = ["CRD + ILS + DGR ──► FRG" if LANG == "en" else "CRD + ILS + DGR ──► FRG"]
    for r in rows:
        frg = clamp(0.25 * r["numeric_boom"] + 0.35 * r["info_loss"] + 0.40 * r["dgr"])
        lines.append(f"{r['scenario']:<13} FRG {bar(frg, good=False)}")
    print_utf8_panel(part, "C", "Boom fragility" if LANG == "en" else "Boom-Fragilität",
        "The same bridge that expands credit also concentrates fragility." if LANG == "en" else "Dieselbe Brücke, die Kredit ausweitet, bündelt auch Fragilität.",
        "This is the negative price of the economic boom." if LANG == "en" else "Das ist der negative Preis des Wirtschaftsbooms.",
        ab, un, line_art(lines, ab, un), "The strongest boom is not automatically the best scenario; it may also be the most breakable." if LANG == "en" else "Der stärkste Boom ist nicht automatisch das beste Szenario; er kann auch am leichtesten brechen.")


def run_part_20(seed: int):
    part = 20; print_new_part_header(part)
    rows = conversion_rows(seed, part, lambda s, i: s.update({"commod": min(1, s["commod"] + 0.18), "platform": min(1, s["platform"] + 0.10), "state": max(0, s["state"] - 0.06)}))
    ab = {"HCP": "Human control portfolio: toxic stacking of work, debt, housing, data and reputation." if LANG == "en" else "Menschenkontrollportfolio: toxische Stapelung von Arbeit, Schuld, Wohnen, Daten und Reputation.", "DAT": "Data control row." if LANG == "en" else "Datenkontrollzeile.", "DEB": "Debt control row." if LANG == "en" else "Schuldkontrollzeile.", "WRK": "Work dependency row." if LANG == "en" else "Arbeitsabhängigkeitszeile.", "HOU": "Housing dependency row." if LANG == "en" else "Wohnabhängigkeitszeile.", "DGR": "Dignity risk score." if LANG == "en" else "Würderisikowert."}; un = scalar_units(["pts", "%"])
    print_utf8_panel(part, "A", "Human-control stack" if LANG == "en" else "Menschenkontroll-Stapel",
        "The stack shows how several legal-looking rows can add up to practical control over a person." if LANG == "en" else "Der Stapel zeigt, wie mehrere legal wirkende Zeilen zusammen praktische Kontrolle über eine Person ergeben können.",
        "This is simulated because the formula can make domination look like ordinary value." if LANG == "en" else "Das wird simuliert, weil die Formel Herrschaft wie gewöhnlichen Wert aussehen lassen kann.",
        ab, un, art_control_stack(rows, ab, un), conv_outcome_summary(rows, ab, un))
    ab = {"NTR": "Non-transfer rule: human dependency cannot be sold as a whole control bundle." if LANG == "en" else "Nichtübertragbarkeitsregel: menschliche Abhängigkeit darf nicht als ganzes Kontrollbündel verkauft werden.", "SPL": "Split rule: work, debt, housing and data must be legally separated." if LANG == "en" else "Spaltungsregel: Arbeit, Schuld, Wohnen und Daten müssen rechtlich getrennt werden.", "BAN": "Ban gate for forbidden relation rows." if LANG == "en" else "Verbotstor für verbotene Relationszeilen.", "DGR": "Dignity risk score." if LANG == "en" else "Würderisikowert."}; un = scalar_units(["pts"])
    lines = ["HCP ──► NTR/SPL/BAN ──► allowed work relation only" if LANG == "en" else "HCP ──► NTR/SPL/BAN ──► nur erlaubte Arbeitsrelation"]
    for r in rows:
        guard = clamp(100 - r["dgr"] + 0.30 * (r["s"]["state"] * 100))
        lines.append(f"{r['scenario']:<13} DGR {bar(r['dgr'], good=False)}  guard {bar(guard, good=True)}")
    print_utf8_panel(part, "B", "Legal firewall" if LANG == "en" else "Rechtliche Firewall",
        "The firewall blocks conversion when a human-control bundle is detected." if LANG == "en" else "Die Firewall blockiert Umrechnung, wenn ein Menschenkontrollbündel erkannt wird.",
        "This is why government law is not optional in the system." if LANG == "en" else "Deshalb ist staatliches Recht in diesem System nicht optional.",
        ab, un, line_art(lines, ab, un), "The dark scenario proves the danger: without NTR, SPL and BAN the market can trade the person indirectly." if LANG == "en" else "Das dunkle Szenario beweist die Gefahr: Ohne NTR, SPL und BAN kann der Markt die Person indirekt handeln.")
    ab = {"MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert.", "DGR": "Dignity risk score." if LANG == "en" else "Würderisikowert.", "ILS": "Information loss score." if LANG == "en" else "Informationsverlustwert."}; un = scalar_units(["MEU", "pts"])
    print_utf8_panel(part, "C", "Moral cost beside price" if LANG == "en" else "Moralische Kosten neben dem Preis",
        "The table refuses to show MEV without DGR and ILS." if LANG == "en" else "Die Tabelle weigert sich, MEV ohne DGR und ILS zu zeigen.",
        "This makes the amoral side visible instead of letting the scalar number launder it." if LANG == "en" else "Dadurch wird die amoralische Seite sichtbar, statt dass die Skalarzahl sie reinwäscht.",
        ab, un, conv_table(rows, un), conv_outcome_summary(rows, ab, un))


def run_part_21(seed: int):
    part = 21; print_new_part_header(part)
    rows = conversion_rows(seed, part, lambda s, i: s.update({"state": min(1, s["state"] + 0.14), "trust": min(1, s["trust"] + 0.08)}))
    ab = {"QFG": "Quality floor gate: minimum score before a converted bundle is accepted." if LANG == "en" else "Qualitätsboden-Tor: Mindestwert, bevor ein umgerechnetes Bündel akzeptiert wird.", "TAX": "Tax acceptance path." if LANG == "en" else "Steuerakzeptanz-Pfad.", "CLR": "Clearing path for safe converted values." if LANG == "en" else "Clearing-Pfad für sichere umgerechnete Werte.", "QRT": "Quarantine path for toxic rows." if LANG == "en" else "Quarantänepfad für toxische Zeilen.", "NTR": "Non-transfer rule for human boundaries." if LANG == "en" else "Nichtübertragbarkeitsregel für Menschengrenzen.", "MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert."}; un = scalar_units(["pts"])
    print_utf8_panel(part, "A", "State scalar gate" if LANG == "en" else "Staatliches Skalartor",
        "Converted values pass through a public quality gate before tax or clearing acceptance." if LANG == "en" else "Umgerechnete Werte gehen durch ein öffentliches Qualitätstor, bevor Steuer- oder Clearingakzeptanz möglich ist.",
        "This is simulated because a market-equivalent number is not automatically a legitimate payment object." if LANG == "en" else "Das wird simuliert, weil eine marktäquivalente Zahl nicht automatisch ein legitimes Zahlungsobjekt ist.",
        ab, un, art_gate(rows, ab, un), conv_outcome_summary(rows, ab, un))
    ab = {"MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert.", "CNV": "Convertibility score." if LANG == "en" else "Umrechenbarkeitswert.", "DGR": "Dignity risk score." if LANG == "en" else "Würderisikowert.", "ILS": "Information loss score." if LANG == "en" else "Informationsverlustwert."}; un = scalar_units(["MEU", "pts"])
    print_utf8_panel(part, "B", "Tax acceptance scenarios" if LANG == "en" else "Steuerakzeptanz-Szenarien",
        "The scenario table shows which converted bundles are numerically useful and publicly acceptable." if LANG == "en" else "Die Szenariotabelle zeigt, welche umgerechneten Bündel numerisch nützlich und öffentlich akzeptabel sind.",
        "A state can accept MEV for taxes only if quality, legality and dignity boundaries survive the conversion." if LANG == "en" else "Ein Staat kann MEV für Steuern nur akzeptieren, wenn Qualität, Rechtmäßigkeit und Würdegrenzen die Umrechnung überstehen.",
        ab, un, conv_table(rows, un, "TAX acceptance" if LANG == "en" else "TAX-Akzeptanz"), conv_outcome_summary(rows, ab, un))
    ab = {"QRT": "Quarantine intensity for unsafe conversion." if LANG == "en" else "Quarantäneintensität für unsichere Umrechnung.", "QFG": "Quality floor gate." if LANG == "en" else "Qualitätsboden-Tor.", "CLR": "Clearing acceptance." if LANG == "en" else "Clearing-Akzeptanz."}; un = scalar_units(["pts"])
    labels = [r["scenario"][:10] for r in rows]
    vals = [[clamp(r["convertibility"] - r["dgr"] * 0.3), clamp(r["info_loss"] * 0.5 + r["dgr"] * 0.7), r["convertibility"]] for r in rows]
    print_utf8_panel(part, "C", "Quarantine heatmap" if LANG == "en" else "Quarantäne-Heatmap",
        "The heatmap shows clearance, quarantine pressure and convertibility side by side." if LANG == "en" else "Die Heatmap zeigt Freigabe, Quarantänedruck und Umrechenbarkeit nebeneinander.",
        "This is simulated because public institutions must distinguish useful conversion from dangerous laundering." if LANG == "en" else "Das wird simuliert, weil öffentliche Institutionen nützliche Umrechnung von gefährlicher Reinwaschung unterscheiden müssen.",
        ab, un, matrix(["QFG", "QRT", "CLR"], labels, vals, "QFG/QRT/CLR"), "Strong QRT is not anti-market; it prevents bad relations from receiving good prices." if LANG == "en" else "Starker QRT ist nicht marktfeindlich; er verhindert, dass schlechte Relationen gute Preise erhalten.")


def run_part_22(seed: int):
    part = 22; print_new_part_header(part)
    rows = conversion_rows(seed, part, lambda s, i: s.update({"external": min(1, s["external"] + 0.16), "ecology": max(0, s["ecology"] - (0.08 if s["key"] in ("spec", "dark") else 0))}))
    ab = {"NEG": "Negative cell: a cost cell that subtracts from converted value." if LANG == "en" else "Negative Zelle: eine Kostenzelle, die vom umgerechneten Wert abzieht.", "GRS": "Gross positive contribution before costs." if LANG == "en" else "Positiver Bruttobeitrag vor Kosten.", "NET": "Net market-equivalent value after costs." if LANG == "en" else "Netto-Marktäquivalent nach Kosten.", "EMS": "Emission burden." if LANG == "en" else "Emissionslast.", "MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert."}; un = scalar_units(["MEU", "kgCO2"])
    print_utf8_panel(part, "A", "Negative ecological cells" if LANG == "en" else "Negative Umweltzellen",
        "Ecological and social burdens enter the same multiplication rule as negative cells." if LANG == "en" else "Ökologische und soziale Lasten gehen als negative Zellen in dieselbe Multiplikationsregel ein.",
        "This is simulated because a stronger system must not let the scalar bridge erase external costs." if LANG == "en" else "Das wird simuliert, weil ein stärkeres System nicht zulassen darf, dass die Skalarbrücke externe Kosten löscht.",
        ab, un, art_ecology_cost(rows, ab, un), conv_outcome_summary(rows, ab, un))
    one = rows[2]
    ab = local_matrix_abbrs({"NEG": "Negative burden contribution." if LANG == "en" else "Negativer Lastenbeitrag.", "CON": "Weighted contribution." if LANG == "en" else "Gewichteter Beitrag."}); un = scalar_units(["MEU"])
    print_utf8_panel(part, "B", "Burden heatmap" if LANG == "en" else "Lasten-Heatmap",
        "The contribution heatmap highlights where environmental and risk costs weigh most." if LANG == "en" else "Die Beitrags-Heatmap hebt hervor, wo Umwelt- und Risikokosten am stärksten wiegen.",
        "This is simulated because the final number should inherit burdens instead of ignoring them." if LANG == "en" else "Das wird simuliert, weil die Endzahl Lasten erben soll, statt sie zu ignorieren.",
        ab, un, art_contribution_heat(one, ab, un), f"{one['scenario']} carries {one['kgco2']} kgCO2 and converts to {one['mev']:.0f} MEU." if LANG == "en" else f"{one['scenario']} trägt {one['kgco2']} kgCO2 und wird zu {one['mev']:.0f} MEU.")
    ab = {"LIM": "Non-tradable limit that cannot be bought away." if LANG == "en" else "Nicht handelbare Grenze, die nicht weggekauft werden kann.", "EMS": "Emission burden." if LANG == "en" else "Emissionslast.", "MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert."}; un = scalar_units(["kgCO2", "MEU"])
    lines = ["EMS below LIM: price allowed | EMS above LIM: price rejected" if LANG == "en" else "EMS unter LIM: Preis erlaubt | EMS über LIM: Preis verworfen"]
    for r in rows:
        status = "OK" if r["kgco2"] < 620 else "STOP"
        lines.append(f"{r['scenario']:<13} EMS {r['kgco2']:4d} kgCO2  LIM 620 kgCO2  {status:>4}  MEV {r['mev']:7.0f} MEU")
    print_utf8_panel(part, "C", "Hard ecological limit" if LANG == "en" else "Harte Umweltgrenze",
        "A hard limit can reject a profitable MEV when the burden is too high." if LANG == "en" else "Eine harte Grenze kann einen profitablen MEV verwerfen, wenn die Last zu hoch ist.",
        "This is simulated because some costs must be prohibited, not merely priced." if LANG == "en" else "Das wird simuliert, weil manche Kosten verboten und nicht nur bepreist werden müssen.",
        ab, un, line_art(lines, ab, un), "The relational system is stronger than a plain market only if it can say no to profitable damage." if LANG == "en" else "Das relationale System ist nur dann stärker als eine bloße Marktwirtschaft, wenn es zu profitablem Schaden Nein sagen kann.")


def run_part_23(seed: int):
    part = 23; print_new_part_header(part)
    rows = conversion_rows(seed, part, lambda s, i: s.update({"platform": min(1, s["platform"] + 0.15), "state": max(0, s["state"] - (0.04 if s["key"] in ("spec", "dark") else 0))}))
    ab = {"PUB": "Public factor-setter." if LANG == "en" else "Öffentlicher Faktorsetzer.", "MKT": "Market factor-setter." if LANG == "en" else "Marktlicher Faktorsetzer.", "PLT": "Platform factor-setter." if LANG == "en" else "Plattform-Faktorsetzer.", "CAL": "Calibration link between factor-setters." if LANG == "en" else "Kalibrierungsverbindung zwischen Faktorsetzern.", "CAP": "Capture pressure: private takeover of factor-setting." if LANG == "en" else "Vereinnahmungsdruck: private Übernahme der Faktorsetzung."}; un = scalar_units(["pts"])
    print_utf8_panel(part, "A", "Factor-governance triangle" if LANG == "en" else "Faktor-Governance-Dreieck",
        "The triangle shows public, market and platform pressure over factor calibration." if LANG == "en" else "Das Dreieck zeigt öffentlichen, marktlichen und Plattformdruck auf die Faktorkalibrierung.",
        "This is simulated because the formula itself becomes an institution of power." if LANG == "en" else "Das wird simuliert, weil die Formel selbst zu einer Machtinstitution wird.",
        ab, un, art_capture_triangle(rows, ab, un), conv_outcome_summary(rows, ab, un))
    ab = {"SEN": "Sensitivity of MEV to a factor." if LANG == "en" else "Sensitivität von MEV gegenüber einem Faktor.", "RFA": "Row factor." if LANG == "en" else "Zeilenfaktor.", "CFA": "Column factor." if LANG == "en" else "Spaltenfaktor.", "MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert."}; un = scalar_units(["MEU"])
    print_utf8_panel(part, "B", "Capture-sensitive factors" if LANG == "en" else "Vereinnahmungsanfällige Faktoren",
        "The sensitivity chart identifies which factor changes would move the market number most." if LANG == "en" else "Das Sensitivitätsbild zeigt, welche Faktoränderungen die Marktzahl am stärksten bewegen würden.",
        "Those factors need the strongest public audit." if LANG == "en" else "Diese Faktoren brauchen die stärkste öffentliche Prüfung.",
        ab, un, art_tornado(rows, ab, un), "High SEN means a small political or private change can redirect huge market value." if LANG == "en" else "Hoher SEN bedeutet, dass eine kleine politische oder private Änderung großen Marktwert umlenken kann.")
    ab = {"CAP": "Capture pressure." if LANG == "en" else "Vereinnahmungsdruck.", "DGR": "Dignity risk score." if LANG == "en" else "Würderisikowert.", "ILS": "Information loss score." if LANG == "en" else "Informationsverlustwert.", "MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert."}; un = scalar_units(["MEU", "pts"])
    print_utf8_panel(part, "C", "Captured conversion table" if LANG == "en" else "Gekaperte Umrechnungstabelle",
        "The table shows that high MEV can coexist with high information loss and dignity risk." if LANG == "en" else "Die Tabelle zeigt, dass hoher MEV mit hohem Informationsverlust und Würderisiko zusammenfallen kann.",
        "This is the political price of the conversion bridge." if LANG == "en" else "Das ist der politische Preis der Umrechnungsbrücke.",
        ab, un, conv_table(rows, un, "CAP table" if LANG == "en" else "CAP-Tabelle"), conv_outcome_summary(rows, ab, un))


def run_part_24(seed: int):
    part = 24; print_new_part_header(part)
    rows = conversion_rows(seed, part)
    ab = {"NBM": "Numeric boom after conversion." if LANG == "en" else "Zahlenboom nach Umrechnung.", "VIS": "Visible structure remaining after conversion." if LANG == "en" else "Nach Umrechnung verbleibende sichtbare Struktur.", "DGS": "Dignity safety: inverse of dignity risk." if LANG == "en" else "Würdesicherheit: Umkehrung des Würderisikos.", "CNV": "Convertibility score." if LANG == "en" else "Umrechenbarkeitswert."}; un = scalar_units(["pts"])
    print_utf8_panel(part, "A", "Final dashboard" if LANG == "en" else "Abschlussdashboard",
        "The dashboard places boom, visibility, dignity safety and convertibility on one grid." if LANG == "en" else "Das Dashboard legt Boom, Sichtbarkeit, Würdesicherheit und Umrechenbarkeit auf ein gemeinsames Raster.",
        "This summarizes the full scalar bridge from relation table to classical market number." if LANG == "en" else "Das fasst die ganze Skalarbrücke von der Relationstabelle zur klassischen Marktzahl zusammen.",
        ab, un, art_final_dashboard(rows, ab, un), conv_outcome_summary(rows, ab, un))
    ab = {"MEV": "Market-equivalent value." if LANG == "en" else "Marktäquivalenter Wert.", "ILS": "Information loss score." if LANG == "en" else "Informationsverlustwert.", "DGR": "Dignity risk score." if LANG == "en" else "Würderisikowert."}; un = scalar_units(["MEU", "pts"])
    print_utf8_panel(part, "B", "Final scenario bars" if LANG == "en" else "Abschließende Szenariobalken",
        "The bars show the market number with its two unavoidable shadow indicators." if LANG == "en" else "Die Balken zeigen die Marktzahl mit ihren zwei unvermeidbaren Schattenindikatoren.",
        "This is simulated because a sane conversion must never output only the number." if LANG == "en" else "Das wird simuliert, weil eine vernünftige Umrechnung niemals nur die Zahl ausgeben darf.",
        ab, un, art_scenario_bars(rows, ab, un), conv_outcome_summary(rows, ab, un))
    ab = {"RCE": "Relational Currency Economy: structured relation currency." if LANG == "en" else "Relationale Währungsökonomie: strukturierte Relationswährung.", "RWÖ": "Relationale Währungsökonomie: strukturierte Relationswährung." if LANG == "de" else "Relational Currency Economy.", "ME": "Market Economy: classical price market." if LANG == "en" else "Marktwirtschaft: klassischer Preismarkt.", "MW": "Marktwirtschaft: klassischer Preismarkt." if LANG == "de" else "Market Economy.", "MEV": "Market-equivalent value produced by conversion." if LANG == "en" else "Marktäquivalenter Wert durch Umrechnung.", "LAW": "Legal boundary that keeps persons from becoming market objects." if LANG == "en" else "Rechtsgrenze, die verhindert, dass Personen Marktobjekte werden."}; un = scalar_units(["MEU"])
    C = cur_abbr(); M = market_abbr()
    lines = [
        f"{C} relation table ──► MEV ──► {M} price market",
        "        │                         ▲",
        "        ├── LAW keeps forbidden rows out",
        "        └── if LAW weakens: boom rises, domination risk rises",
    ] if LANG == "en" else [
        f"{C} Relationstabelle ──► MEV ──► {M} Preismarkt",
        "        │                         ▲",
        "        ├── LAW hält verbotene Zeilen draußen",
        "        └── wenn LAW schwach wird: Boom steigt, Herrschaftsrisiko steigt",
    ]
    print_utf8_panel(part, "C", "System verdict" if LANG == "en" else "Systemurteil",
        "The final diagram shows the conversion bridge and the legal boundary beside it." if LANG == "en" else "Das Abschlussbild zeigt die Umrechnungsbrücke und daneben die Rechtsgrenze.",
        "This is the central conclusion: the relational system is stronger because it sees more, but it is dangerous if everything seen becomes tradeable." if LANG == "en" else "Das ist die zentrale Schlussfolgerung: Das relationale System ist stärker, weil es mehr sieht, aber gefährlich, wenn alles Gesehene handelbar wird.",
        ab, un, line_art(lines, ab, un),
        "The conversion makes the system compatible with classical markets. The price is that lawmakers must decide which rows cannot enter the formula at all." if LANG == "en" else "Die Umrechnung macht das System mit klassischen Märkten kompatibel. Der Preis ist, dass Gesetzgeber entscheiden müssen, welche Zeilen gar nicht erst in die Formel dürfen.")


RUNNERS = {
    1: run_part_1,
    2: run_part_2,
    3: run_part_3,
    4: run_part_4,
    5: run_part_5,
    6: run_part_6,
    7: run_part_7,
    8: run_part_8,
    9: run_part_9,
    10: run_part_10,
    11: run_part_11,
    12: run_part_12,
    13: run_part_13,
    14: run_part_14,
    15: run_part_15,
    16: run_part_16,
    17: run_part_17,
    18: run_part_18,
    19: run_part_19,
    20: run_part_20,
    21: run_part_21,
    22: run_part_22,
    23: run_part_23,
    24: run_part_24,
}


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_parts(text: str) -> List[int]:
    if not text:
        return list(range(1, 25))
    parts = []
    for piece in text.split(','):
        piece = piece.strip()
        if not piece:
            continue
        if '-' in piece:
            a, b = piece.split('-', 1)
            start, end = int(a), int(b)
            for x in range(start, end + 1):
                parts.append(x)
        else:
            parts.append(int(piece))
    clean = []
    for p in parts:
        if p < 1 or p > 24:
            raise argparse.ArgumentTypeError("part numbers must be between 1 and 24")
        if p not in clean:
            clean.append(p)
    return clean


def main(argv=None):
    global USE_COLOR, LANG, WIDTH
    parser = argparse.ArgumentParser(
        description="Ultra-color relation-currency economy simulation. Default language is English.")
    parser.add_argument("--lang", choices=["en", "de"], default="en", help="output language; default: en")
    parser.add_argument("--parts", "--teile", default="1-24", help="simulation parts, e.g. 1,4,7-9 or 15-24; default: all")
    parser.add_argument("--seed", type=int, default=42, help="random seed for repeatable scenario values")
    parser.add_argument("--no-color", action="store_true", help="turn off ANSI colors")
    parser.add_argument("--width", type=int, default=None, help="layout width override; by default terminal width minus 5 is detected")
    args = parser.parse_args(argv)
    LANG = args.lang
    USE_COLOR = not args.no_color
    detected_width = max(40, shutil.get_terminal_size((104, 24)).columns - 5)
    WIDTH = max(60, min(170, (args.width - 5) if args.width else detected_width))
    parts = parse_parts(args.parts)

    print(title_box(L("program_title"), L("program_subtitle")))
    if LANG == "en":
        intro = (
            "This program runs several scenarios for each simulation part: guarded, open, speculative and dark. "
            "The scores are illustrative model values, not empirical facts. Their purpose is to make the structure visible: relation depth creates economic strength, scalar conversion creates classical market compatibility, and weak boundaries create domination risk."
        )
    else:
        intro = (
            "Dieses Programm führt je Simulationsteil mehrere Szenarien aus: geschützt, offen, spekulativ und dunkel. "
            "Die Punktwerte sind veranschaulichende Modellwerte, keine empirischen Tatsachen. Ihr Zweck ist, die Struktur sichtbar zu machen: Relationstiefe erzeugt wirtschaftliche Stärke, Skalarumrechnung erzeugt klassische Marktkompatibilität, und schwache Grenzen erzeugen Herrschaftsrisiko."
        )
    print(section_box("Overview" if LANG == "en" else "Überblick", intro, {}, [], fg=15, bg=24))
    for p in parts:
        RUNNERS[p](args.seed)
    print("\n" + rainbow_rule())
    print(section_box("Final note" if LANG == "en" else "Schlussbemerkung", L("footer"), {}, [], fg=15, bg=54))
    print(rainbow_rule())


if __name__ == "__main__":
    try:
        main()
    except BrokenPipeError:
        try:
            sys.stdout.close()
        except Exception:
            pass
        sys.exit(0)
