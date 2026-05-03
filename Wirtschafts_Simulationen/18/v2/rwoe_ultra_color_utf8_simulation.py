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
    out.append(ansi("║" + pad("  " + title + "  ", width - 2, "center") + "║", fg=15, bg=54, bold=True))
    if subtitle:
        out.append(ansi("║" + pad("  " + subtitle + "  ", width - 2, "center") + "║", fg=225, bg=54))
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
    print(ansi(label, fg=15, bg=25, bold=True))
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
}

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_parts(text: str) -> List[int]:
    if not text:
        return list(range(1, 15))
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
        if p < 1 or p > 14:
            raise argparse.ArgumentTypeError("part numbers must be between 1 and 14")
        if p not in clean:
            clean.append(p)
    return clean


def main(argv=None):
    global USE_COLOR, LANG, WIDTH
    parser = argparse.ArgumentParser(
        description="Ultra-color relation-currency economy simulation. Default language is English.")
    parser.add_argument("--lang", choices=["en", "de"], default="en", help="output language; default: en")
    parser.add_argument("--parts", "--teile", default="1-14", help="simulation parts, e.g. 1,4,7-9; default: all")
    parser.add_argument("--seed", type=int, default=42, help="random seed for repeatable scenario values")
    parser.add_argument("--no-color", action="store_true", help="turn off ANSI colors")
    parser.add_argument("--width", type=int, default=104, help="layout width, default: 104")
    args = parser.parse_args(argv)
    LANG = args.lang
    USE_COLOR = not args.no_color
    WIDTH = max(88, min(140, args.width))
    parts = parse_parts(args.parts)

    print(title_box(L("program_title"), L("program_subtitle")))
    if LANG == "en":
        intro = (
            "This program runs several scenarios for each simulation part: guarded, open, speculative and dark. "
            "The scores are illustrative model values, not empirical facts. Their purpose is to make the structure visible: relation depth creates economic strength, while weak boundaries create domination risk."
        )
    else:
        intro = (
            "Dieses Programm führt je Simulationsteil mehrere Szenarien aus: geschützt, offen, spekulativ und dunkel. "
            "Die Punktwerte sind veranschaulichende Modellwerte, keine empirischen Tatsachen. Ihr Zweck ist, die Struktur sichtbar zu machen: Relationstiefe erzeugt wirtschaftliche Stärke, schwache Grenzen erzeugen Herrschaftsrisiko."
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
