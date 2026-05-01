#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GMOE Enriched Visual Simulation
===============================

Galaktische Metrische Operatorökonomie mit farbigen UTF-8-Diagrammen.

Kernpostulat:
    Geld ist kein bloßer Skalar.
    Geld ist ein zählbarer Stapel aus:
        gültiger unärer Operation f: Ω -> Ω
        + gültiger Metrik d
        + zertifizierter positiver Zustandsänderung Δ ∈ K+

Das Skript simuliert zwei Modi:
    1. gmoe      : nur positive Operator-Metrik-Kontraktionen werden als OMK-Geld geprägt.
    2. baseline  : normales Fiatgeld; privater Profit kann auch schädliche Operationen räumen.

Es erzeugt:
    - sehr farbige ANSI-/UTF-8-Terminalgrafiken,
    - ausführliche Legenden und Erklärungen aller Kürzel und Einheiten,
    - Tabellen, Heatmaps, Sparklines, Balkendiagramme, Stack-Diagramme,
    - CSV-Exporte und farbige / unfarbige Reports.

Beispiel:
    pypy3 gmoe_enriched_visual_simulation.py --compare --steps 180 --agents 60 --regions 5 --seed 7 --out gmoe_visual_out
    pypy3 gmoe_enriched_visual_simulation.py --mode gmoe --steps 220 --agents 80 --regions 7 --seed 42 --out gmoe_visual_out

Keine externen Pakete nötig.
"""

from __future__ import print_function

import argparse
import copy
import csv
import math
import os
import random
import re
import statistics
import sys
import shutil
import textwrap
from collections import defaultdict
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple, Any


# ============================================================
# 0. ANSI Farben und UTF-8-Grafik
# ============================================================

class Palette:
    RESET = "\033[0m"
    BOLD = "\033[1m"
    DIM = "\033[2m"
    UNDER = "\033[4m"

    BLACK = "\033[30m"
    RED = "\033[31m"
    GREEN = "\033[32m"
    YELLOW = "\033[33m"
    BLUE = "\033[34m"
    MAGENTA = "\033[35m"
    CYAN = "\033[36m"
    WHITE = "\033[37m"
    GRAY = "\033[90m"
    BRIGHT_RED = "\033[91m"
    BRIGHT_GREEN = "\033[92m"
    BRIGHT_YELLOW = "\033[93m"
    BRIGHT_BLUE = "\033[94m"
    BRIGHT_MAGENTA = "\033[95m"
    BRIGHT_CYAN = "\033[96m"
    BRIGHT_WHITE = "\033[97m"

    BG_RED = "\033[41m"
    BG_GREEN = "\033[42m"
    BG_YELLOW = "\033[43m"
    BG_BLUE = "\033[44m"
    BG_MAGENTA = "\033[45m"
    BG_CYAN = "\033[46m"
    BG_GRAY = "\033[100m"

    # Stabile Farben für Währungseinheiten und Instrumente.
    UNIT = {
        "OMK": CYAN,
        "FIAT": GRAY,
        "TRUTH": BRIGHT_GREEN,
        "CAUSE": BRIGHT_MAGENTA,
        "NORM": BRIGHT_BLUE,
        "BEHAV": BRIGHT_YELLOW,
        "HIER": BRIGHT_RED,
        "REPAIR": GREEN,
        "GOV": BRIGHT_CYAN,
        "INS": BRIGHT_RED,
        "STOCK": YELLOW,
        "BRIDGE": BLUE,
        "DEBT": RED,
        "RISK": MAGENTA,
        "REP": WHITE,
        "K+": BRIGHT_GREEN,
        "BAD": BRIGHT_RED,
        "OK": BRIGHT_GREEN,
    }

    METRIC = {
        "agency": BRIGHT_CYAN,
        "freedom_from_harm": BRIGHT_GREEN,
        "truth": BRIGHT_GREEN,
        "causal_integrity": BRIGHT_MAGENTA,
        "norm_alignment": BRIGHT_BLUE,
        "hierarchy_legitimacy": BRIGHT_RED,
        "behavior_cooperation": BRIGHT_YELLOW,
        "repair_capacity": GREEN,
        "help_potential": CYAN,
        "resource_resilience": BLUE,
        "material_output": YELLOW,
        "liquidity": CYAN,
        "fairness": WHITE,
        "consent_quality": BRIGHT_YELLOW,
        "reversibility": MAGENTA,
    }

    @staticmethod
    def strip(s):
        return re.sub(r"\x1b\[[0-9;]*m", "", s)


class Colorizer:
    def __init__(self, enabled=True):
        self.enabled = enabled

    def c(self, text, color):
        if not self.enabled:
            return str(text)
        return str(color) + str(text) + Palette.RESET

    def unit(self, key, text=None):
        if text is None:
            text = key
        return self.c(text, Palette.UNIT.get(key, Palette.WHITE))

    def metric(self, key, text=None):
        if text is None:
            text = key
        return self.c(text, Palette.METRIC.get(key, Palette.WHITE))

    def bold(self, text):
        return self.c(text, Palette.BOLD)

    def dim(self, text):
        return self.c(text, Palette.DIM)

    def red(self, text):
        return self.c(text, Palette.BRIGHT_RED)

    def green(self, text):
        return self.c(text, Palette.BRIGHT_GREEN)

    def yellow(self, text):
        return self.c(text, Palette.BRIGHT_YELLOW)

    def cyan(self, text):
        return self.c(text, Palette.BRIGHT_CYAN)

    def magenta(self, text):
        return self.c(text, Palette.BRIGHT_MAGENTA)

    def blue(self, text):
        return self.c(text, Palette.BRIGHT_BLUE)


def visible_len(s):
    return len(Palette.strip(str(s)))


def pad(s, width):
    s = str(s)
    return s + " " * max(0, width - visible_len(s))


def center(s, width):
    s = str(s)
    extra = max(0, width - visible_len(s))
    left = extra // 2
    right = extra - left
    return " " * left + s + " " * right


def block_bar(value, max_value=100.0, width=24, color=""):
    value = max(0.0, min(max_value, value))
    filled = int(round(width * value / max_value))
    chars = "█" * filled + "░" * (width - filled)
    if color:
        return color + chars + Palette.RESET
    return chars


def signed_bar(value, max_abs=10.0, width=26, pos_color="", neg_color=""):
    # Mittelachse für positive/negative Δ.
    half = width // 2
    value = max(-max_abs, min(max_abs, value))
    n = int(round(half * abs(value) / max_abs))
    if value >= 0:
        left = " " * half
        right = "█" * n + "░" * (half - n)
        if pos_color:
            right = pos_color + right + Palette.RESET
    else:
        left = "░" * (half - n) + "█" * n
        right = " " * half
        if neg_color:
            left = neg_color + left + Palette.RESET
    return left + "│" + right


def sparkline(values, width=60, colorizer=None):
    if not values:
        return ""
    chars = "▁▂▃▄▅▆▇█"
    if len(values) > width:
        step = float(len(values)) / width
        sampled = []
        for i in range(width):
            start = int(i * step)
            end = int((i + 1) * step)
            end = max(end, start + 1)
            sampled.append(sum(values[start:end]) / float(end - start))
        values = sampled
    lo, hi = min(values), max(values)
    if hi - lo < 1e-9:
        out = chars[-1] * len(values)
    else:
        out = "".join(chars[int((v - lo) / (hi - lo) * (len(chars) - 1))] for v in values)
    if colorizer:
        return colorizer.c(out, Palette.BRIGHT_CYAN)
    return out


def heat_cell(value, colorizer):
    # 0..100 -> farbige Zelle.
    if value >= 85:
        return colorizer.green("██")
    if value >= 70:
        return colorizer.c("▓▓", Palette.GREEN)
    if value >= 55:
        return colorizer.yellow("▒▒")
    if value >= 40:
        return colorizer.c("░░", Palette.YELLOW)
    if value >= 25:
        return colorizer.red("░░")
    return colorizer.c("!!", Palette.BRIGHT_RED)


def box(title, lines, colorizer, width=100, color=None):
    """Draw a bounded UTF-8 box. Long colored lines are safely wrapped as plain text.

    The width passed to this function is always the intended terminal-safe width.
    It should normally be terminal_width - 5.
    """
    if color is None:
        color = Palette.BRIGHT_CYAN
    width = max(54, int(width))
    inner = max(10, width - 4)
    top = "╔" + "═" * (width - 2) + "╗"
    mid_title = "║" + center(colorizer.c(" " + str(title) + " ", color), width - 2) + "║"
    sep = "╠" + "═" * (width - 2) + "╣"
    bottom = "╚" + "═" * (width - 2) + "╝"
    out = [colorizer.c(top, color), mid_title, colorizer.c(sep, color)]
    for line in lines:
        raw = str(line)
        if visible_len(raw) <= inner:
            wrapped = [raw]
        else:
            # Preserve safety over color fidelity. If a line is too wide, strip ANSI
            # before wrapping so borders never spill past the configured width.
            plain = Palette.strip(raw)
            wrapped = textwrap.wrap(plain, width=inner, replace_whitespace=False, drop_whitespace=False) or [""]
        for part in wrapped:
            out.append(colorizer.c("║ ", color) + pad(part, inner) + colorizer.c(" ║", color))
    out.append(colorizer.c(bottom, color))
    return "\n".join(out)


def terminal_safe_width(requested=None):
    """Return output width five columns smaller than the current screen width.

    If requested is given and positive, it is treated as an upper bound, but the
    actual width still never exceeds terminal_width - 5. This matches the user
    requirement that the report should be five characters narrower than the screen.
    """
    try:
        cols = shutil.get_terminal_size((120, 30)).columns
    except Exception:
        cols = 120
    safe = max(54, cols - 5)
    if requested and requested > 0:
        return max(54, min(int(requested), safe))
    return safe


# ============================================================
# 1. Metriken und Einheiten
# ============================================================

METRICS = [
    "agency",
    "freedom_from_harm",
    "truth",
    "causal_integrity",
    "norm_alignment",
    "hierarchy_legitimacy",
    "behavior_cooperation",
    "repair_capacity",
    "help_potential",
    "resource_resilience",
    "material_output",
    "liquidity",
    "fairness",
    "consent_quality",
    "reversibility",
]

METRIC_SHORT = {
    "agency": "AGY",
    "freedom_from_harm": "SAFE",
    "truth": "TRU",
    "causal_integrity": "CAUS",
    "norm_alignment": "NORM",
    "hierarchy_legitimacy": "HIER",
    "behavior_cooperation": "BEHV",
    "repair_capacity": "REPR",
    "help_potential": "HELP",
    "resource_resilience": "RES",
    "material_output": "OUT",
    "liquidity": "LIQ",
    "fairness": "FAIR",
    "consent_quality": "CONS",
    "reversibility": "REV",
}

METRIC_EXPLANATION = {
    "agency": "Handlungsfähigkeit: Fähigkeit zu handeln, zu widersprechen, auszusteigen und zu reparieren.",
    "freedom_from_harm": "Schadensfreiheit: Abwesenheit von Schaden, Zwang, Degradation und Hilflosmachung.",
    "truth": "Wahrheitsnähe: Verlässlichkeit von Behauptungen, Beweisen und Prognosen.",
    "causal_integrity": "Kausale Integrität: Wie gut Ursachen, Wirkungen und Verantwortlichkeiten nachvollziehbar sind.",
    "norm_alignment": "Normabstand: Nähe zu gültigen Normen statt privaten Tyrannenmetriken.",
    "hierarchy_legitimacy": "Legitime Hierarchie: Macht ist überprüfbar, anfechtbar, delegierbar und nicht bloß Dominanz.",
    "behavior_cooperation": "Kooperatives Verhalten: freiwillige, transparente Verhaltensanpassung ohne Zwang.",
    "repair_capacity": "Reparaturfähigkeit: Fähigkeit, Schaden rückgängig zu machen, zu kompensieren oder zu entschärfen.",
    "help_potential": "Hilfspotenzial: Fähigkeit künftiger hilfreicher Zustandsverbesserungen.",
    "resource_resilience": "Ressourcenresilienz: Stabilität von Energie, Gütern, Infrastruktur und Reserven.",
    "material_output": "Materieller Output: reale Produktion, aber mit niedrigem Moralgewicht.",
    "liquidity": "Liquidität: Handelbarkeit und Umlaufgeschwindigkeit von gültigen Ansprüchen.",
    "fairness": "Fairness: gerechte Verteilung von Rechten, Lasten, Chancen und Vorteilen.",
    "consent_quality": "Zustimmungsqualität: freiwillig, informiert, widerrufbar, ohne versteckten Zwang.",
    "reversibility": "Reversibilität: Eingriffe sind rücknehmbar oder wenigstens reparierbar.",
}

WEIGHTS = {
    "agency": 2.20,
    "freedom_from_harm": 2.25,
    "truth": 1.75,
    "causal_integrity": 1.45,
    "norm_alignment": 1.15,
    "hierarchy_legitimacy": 1.05,
    "behavior_cooperation": 0.90,
    "repair_capacity": 1.45,
    "help_potential": 1.30,
    "resource_resilience": 0.95,
    "material_output": 0.50,
    "liquidity": 0.35,
    "fairness": 1.60,
    "consent_quality": 1.70,
    "reversibility": 1.00,
}

PROTECTED = [
    "agency",
    "freedom_from_harm",
    "truth",
    "causal_integrity",
    "fairness",
    "consent_quality",
]

MEANINGFUL = [
    "agency",
    "freedom_from_harm",
    "truth",
    "causal_integrity",
    "norm_alignment",
    "hierarchy_legitimacy",
    "behavior_cooperation",
    "repair_capacity",
    "help_potential",
    "fairness",
    "consent_quality",
    "reversibility",
]

TARGET = {m: 100.0 for m in METRICS}

POSITIVE_SCORE_THRESHOLD = 0.035
PROTECTED_LOSS_TOLERANCE = -0.055

UNIT_EXPLANATION = {
    "OMK": "Operation-Metrik-Kredit. Zählbares Wurzelgeld aus Operation + Metrik + zertifiziertem Δ ∈ K+.",
    "FIAT": "Normales Skalar-Geld. In der Baseline kann es privaten Profit auch bei schädlichen Operationen räumen.",
    "TRUTH": "Wahrheitszertifikat. Auszahlung für verifizierte Wahrheit, nicht Kauf der Wahrheit selbst.",
    "CAUSE": "Kausalitätszertifikat. Zahlung für belastbar attribuierte Ursache-Wirkungs-Verbesserung.",
    "NORM": "Normdistanzgeld. Zahlung für Verringerung des Abstands zu gültigen Normen.",
    "BEHAV": "Verhaltensgeld. Zahlung für freiwillige, transparente, widerrufbare Verhaltensänderung.",
    "HIER": "Hierarchiegeld. Rechte für legitime Inversion, Reparatur, Rotation oder Delegation von Hierarchie.",
    "REPAIR": "Reparaturfonds. Gemeinsamer Fonds für Schadenreduktion und Agency-Wiederherstellung.",
    "GOV": "Governance-Fonds. Mittel für Audit, Gerichte, Metrikregister und Red-Line-Durchsetzung.",
    "INS": "Versicherung. Schutz gegen negative Metrikbewegung; Eigenverursachung ist ungültig.",
    "STOCK": "Aktie/Wertpapier. Anspruch auf künftige metrische Produktivität eines Operatorbündels.",
    "BRIDGE": "Interregionale Bridge-Credits. Latenz- und Vertrauensabhängiger Austausch zwischen Regionen.",
    "DEBT": "Schuld/Haftung. Entsteht durch nicht gelieferte Verbesserung oder schädliche Δ-Bewegung.",
    "RISK": "Risikoaufschlag. Preisanteil für Unsicherheit, Irreversibilität und Latenz.",
    "REP": "Reputation. Nicht direkt Geld, aber vertrauensbildendes Kapital für künftige Operatorrechte.",
    "K+": "Positiver Kegel. Menge der erlaubten Verbesserungsrichtungen im Metrikraum.",
}


# ============================================================
# 1b. Szenarien
# ============================================================

SCENARIOS = {
    "balanced": {
        "title": "Ausbalancierte Galaxie",
        "desc": "Gemischte Lage: moderate Schocks, mittlere Vertrauensnetze, normale Verteilung von noblen, neutralen und schädlichen Akteuren.",
        "intent": (0.32, 0.44, 0.24),
        "shock_multiplier": 1.00,
        "shock_add": 0.000,
        "trust_multiplier": 1.00,
        "trust_shift": 0.00,
        "latency_multiplier": 1.00,
        "metric_bias": {},
        "op_bias": {},
    },
    "flourishing": {
        "title": "Blühende Hilfsökonomie",
        "desc": "Mehr noble Akteure, höhere Start-Agency, bessere Wahrheit und weniger externe Schocks. GMOE sollte hier sehr stabil wachsen; Baseline kann ebenfalls ordentlich laufen.",
        "intent": (0.46, 0.42, 0.12),
        "shock_multiplier": 0.45,
        "shock_add": 0.000,
        "trust_multiplier": 1.08,
        "trust_shift": 0.05,
        "latency_multiplier": 0.80,
        "metric_bias": {"agency": 6, "truth": 5, "fairness": 4, "consent_quality": 4, "repair_capacity": 3},
        "op_bias": {"restore_agency": 1.20, "repair_harm": 1.15, "education": 1.20, "exploit_labor": 0.70, "fake_truth_certificate": 0.65},
    },
    "sabotage_wave": {
        "title": "Sabotagewelle",
        "desc": "Mehr schädliche Akteure und mehr Sabotageversuche. GMOE kann vieles ablehnen, aber externe Reibung und Angriffe können den Endwert trotzdem drücken.",
        "intent": (0.24, 0.40, 0.36),
        "shock_multiplier": 1.30,
        "shock_add": 0.004,
        "trust_multiplier": 0.90,
        "trust_shift": -0.04,
        "latency_multiplier": 1.15,
        "metric_bias": {"freedom_from_harm": -6, "truth": -4, "fairness": -4, "consent_quality": -3},
        "op_bias": {"sabotage_competitor": 1.55, "metric_hack": 1.35, "fake_truth_certificate": 1.35, "repair_harm": 1.15},
    },
    "truth_crisis": {
        "title": "Wahrheitskrise",
        "desc": "Wahrheit und Kausalität starten schwach. Es gibt mehr Fake-Truth- und Audit-Aktivität. Der Test zeigt, ob Wahrheitsgeld Lügen isolieren kann.",
        "intent": (0.30, 0.42, 0.28),
        "shock_multiplier": 0.95,
        "shock_add": 0.002,
        "trust_multiplier": 0.92,
        "trust_shift": -0.02,
        "latency_multiplier": 1.00,
        "metric_bias": {"truth": -10, "causal_integrity": -8, "norm_alignment": -3},
        "op_bias": {"truth_audit": 1.45, "fake_truth_certificate": 1.55, "causal_intervention": 1.20},
    },
    "frontier_shock": {
        "title": "Frontier-Schockzone",
        "desc": "Viele äußere Schäden, schwache Ressourcenresilienz, hohe Reparaturnachfrage. Ausgang kann stark schwanken, weil Schocks die positive Operatorenkette stören.",
        "intent": (0.34, 0.44, 0.22),
        "shock_multiplier": 2.20,
        "shock_add": 0.008,
        "trust_multiplier": 0.95,
        "trust_shift": -0.01,
        "latency_multiplier": 1.25,
        "metric_bias": {"resource_resilience": -10, "repair_capacity": -8, "freedom_from_harm": -5, "reversibility": -5},
        "op_bias": {"repair_harm": 1.65, "infrastructure_maintenance": 1.45, "insurance_underwrite": 1.35, "self_created_need": 1.10},
    },
    "latency_fragmented": {
        "title": "Fragmentierte Latenz-Galaxie",
        "desc": "Niedriges interregionales Vertrauen und hohe Latenz. Bridge-Credits sind riskanter, regionale Unterschiede können größer bleiben.",
        "intent": (0.32, 0.46, 0.22),
        "shock_multiplier": 1.05,
        "shock_add": 0.002,
        "trust_multiplier": 0.72,
        "trust_shift": -0.08,
        "latency_multiplier": 1.85,
        "metric_bias": {"liquidity": -6, "causal_integrity": -3},
        "op_bias": {"interregional_bridge": 1.35, "fair_exchange": 0.85},
    },
    "tyranny_pressure": {
        "title": "Hierarchischer Druck",
        "desc": "Legitimität, Fairness und Zustimmung starten niedrig; es gibt mehr Tyrannenmetriken und Hierarchieoperationen. Das Szenario testet lokale Hierarchie-Inversion als Reparatur.",
        "intent": (0.28, 0.42, 0.30),
        "shock_multiplier": 1.10,
        "shock_add": 0.003,
        "trust_multiplier": 0.86,
        "trust_shift": -0.03,
        "latency_multiplier": 1.05,
        "metric_bias": {"hierarchy_legitimacy": -10, "agency": -5, "fairness": -8, "consent_quality": -7},
        "op_bias": {"hierarchy_inversion_repair": 1.60, "tyrant_hierarchy_inversion": 1.55, "restore_agency": 1.25},
    },
    "scarcity": {
        "title": "Knappheitsökonomie",
        "desc": "Güter, Energie und Ressourcen sind knapp. Produktion kann helfen, darf aber im GMOE-Modus geschützte Metriken nicht opfern.",
        "intent": (0.30, 0.48, 0.22),
        "shock_multiplier": 1.40,
        "shock_add": 0.004,
        "trust_multiplier": 0.95,
        "trust_shift": 0.00,
        "latency_multiplier": 1.10,
        "metric_bias": {"resource_resilience": -10, "material_output": -8, "liquidity": -5, "repair_capacity": -4},
        "op_bias": {"produce_goods": 1.50, "infrastructure_maintenance": 1.35, "exploit_labor": 1.35, "insurance_underwrite": 1.15},
    },
}

SCENARIO_ORDER = [k for k in SCENARIOS.keys() if k != "balanced"]


# ============================================================
# 2. Mathematische Hilfsfunktionen
# ============================================================

def clamp(x, lo=0.0, hi=100.0):
    return max(lo, min(hi, x))


def empty_delta():
    return {m: 0.0 for m in METRICS}


def weighted_score(delta):
    return sum(delta.get(m, 0.0) * WEIGHTS[m] for m in METRICS)


def positive_amount(delta):
    return sum(max(0.0, delta.get(m, 0.0)) * WEIGHTS[m] for m in METRICS)


def negative_amount(delta):
    return sum(max(0.0, -delta.get(m, 0.0)) * WEIGHTS[m] for m in METRICS)


def protected_loss(delta):
    return sum(max(0.0, -delta.get(m, 0.0)) * WEIGHTS[m] for m in PROTECTED)


def nobility_index(metrics):
    total = sum(WEIGHTS.values())
    return sum(metrics[m] * WEIGHTS[m] for m in METRICS) / total


def metric_distance(metrics):
    total = sum(WEIGHTS.values())
    return sum((TARGET[m] - metrics[m]) * WEIGHTS[m] for m in METRICS) / total


def safe_mean(xs, default=0.0):
    return sum(xs) / float(len(xs)) if xs else default


def safe_stdev(xs, default=0.0):
    return statistics.stdev(xs) if len(xs) >= 2 else default


def gini(xs):
    xs = sorted([max(0.0, x) for x in xs])
    n = len(xs)
    if n == 0:
        return 0.0
    total = sum(xs)
    if total <= 0:
        return 0.0
    acc = 0.0
    for i, x in enumerate(xs, 1):
        acc += i * x
    return (2.0 * acc) / (n * total) - (n + 1.0) / n


def pearson(xs, ys):
    if len(xs) < 2 or len(xs) != len(ys):
        return 0.0
    mx = safe_mean(xs)
    my = safe_mean(ys)
    vx = sum((x - mx) ** 2 for x in xs)
    vy = sum((y - my) ** 2 for y in ys)
    if vx <= 1e-12 or vy <= 1e-12:
        return 0.0
    cov = sum((x - mx) * (y - my) for x, y in zip(xs, ys))
    return cov / math.sqrt(vx * vy)


def format_delta(delta, limit=5):
    items = [(m, delta[m]) for m in METRICS if abs(delta.get(m, 0.0)) > 1e-9]
    items.sort(key=lambda x: abs(x[1]), reverse=True)
    out = []
    for m, v in items[:limit]:
        sign = "+" if v >= 0 else ""
        out.append("%s%s%.2f" % (METRIC_SHORT[m], sign, v))
    if len(items) > limit:
        out.append("...")
    return ", ".join(out) if out else "no metric change"


def fmt(x):
    if isinstance(x, float):
        return "%.6f" % x
    return str(x)


# ============================================================
# 3. Operationen: typisierte unäre Algebra f: Ω -> Ω
# ============================================================

OPERATION_SPECS = {
    "restore_agency": {
        "from": "damage", "to": "agency", "kind": "repair", "unit": "OMK",
        "base": {"agency": 3.0, "repair_capacity": 1.0, "help_potential": 1.2, "freedom_from_harm": 0.8, "truth": 0.2, "fairness": 0.7, "consent_quality": 0.4, "reversibility": 0.3},
        "private_gain": 1.1, "red_flags": [], "reversible": False,
    },
    "repair_harm": {
        "from": "damage", "to": "effect", "kind": "repair", "unit": "REPAIR",
        "base": {"freedom_from_harm": 2.9, "repair_capacity": 1.6, "agency": 0.7, "truth": 0.2, "help_potential": 0.6, "fairness": 0.6, "reversibility": 0.5},
        "private_gain": 1.3, "red_flags": [], "reversible": False,
    },
    "truth_audit": {
        "from": "truth", "to": "money", "kind": "truth", "unit": "TRUTH",
        "base": {"truth": 2.7, "causal_integrity": 0.9, "norm_alignment": 0.5, "hierarchy_legitimacy": 0.3, "fairness": 0.3},
        "private_gain": 1.0, "red_flags": [], "reversible": True,
    },
    "causal_intervention": {
        "from": "causality", "to": "effect", "kind": "causal", "unit": "CAUSE",
        "base": {"causal_integrity": 1.9, "resource_resilience": 1.4, "help_potential": 1.0, "material_output": 0.8, "truth": 0.4, "reversibility": 0.2},
        "private_gain": 1.8, "red_flags": [], "reversible": False,
    },
    "norm_reform": {
        "from": "norm", "to": "behavior", "kind": "norm", "unit": "NORM",
        "base": {"norm_alignment": 2.2, "agency": 0.8, "hierarchy_legitimacy": 0.8, "behavior_cooperation": 0.6, "fairness": 0.7, "consent_quality": 0.3},
        "private_gain": 0.9, "red_flags": [], "reversible": True,
    },
    "voluntary_behavior_contract": {
        "from": "behavior", "to": "money", "kind": "behavior", "unit": "BEHAV",
        "base": {"behavior_cooperation": 2.3, "norm_alignment": 0.7, "agency": 0.4, "resource_resilience": 0.5, "consent_quality": 1.2, "fairness": 0.3},
        "private_gain": 1.05, "red_flags": [], "reversible": True,
    },
    "hierarchy_inversion_repair": {
        "from": "hierarchy", "to": "hierarchy", "kind": "hierarchy", "unit": "HIER",
        "base": {"hierarchy_legitimacy": 2.6, "agency": 1.1, "truth": 0.5, "norm_alignment": 0.5, "fairness": 0.8, "consent_quality": 0.4, "reversibility": 0.4},
        "private_gain": 1.2, "red_flags": [], "reversible": True,
    },
    "produce_goods": {
        "from": "effect", "to": "money", "kind": "production", "unit": "STOCK",
        "base": {"material_output": 2.8, "resource_resilience": 0.9, "help_potential": 0.4, "agency": 0.15, "liquidity": 0.35},
        "private_gain": 3.2, "red_flags": [], "reversible": True,
    },
    "education": {
        "from": "truth", "to": "agency", "kind": "education", "unit": "TRUTH",
        "base": {"agency": 2.0, "truth": 1.3, "help_potential": 0.9, "behavior_cooperation": 0.5, "fairness": 0.4, "consent_quality": 0.4},
        "private_gain": 1.2, "red_flags": [], "reversible": False,
    },
    "infrastructure_maintenance": {
        "from": "effect", "to": "resource", "kind": "infrastructure", "unit": "REPAIR",
        "base": {"resource_resilience": 2.1, "freedom_from_harm": 0.8, "repair_capacity": 0.8, "material_output": 0.6, "reversibility": 0.3},
        "private_gain": 1.5, "red_flags": [], "reversible": False,
    },
    "fair_exchange": {
        "from": "money", "to": "money", "kind": "market", "unit": "OMK",
        "base": {"liquidity": 1.4, "fairness": 0.7, "behavior_cooperation": 0.3, "truth": 0.1, "consent_quality": 0.4},
        "private_gain": 1.1, "red_flags": [], "reversible": True,
    },
    "interregional_bridge": {
        "from": "ledger", "to": "ledger", "kind": "galactic_bridge", "unit": "BRIDGE",
        "base": {"liquidity": 1.2, "truth": 0.4, "causal_integrity": 0.4, "resource_resilience": 0.3, "reversibility": 0.2},
        "private_gain": 1.0, "red_flags": [], "reversible": False,
    },
    "insurance_underwrite": {
        "from": "damage", "to": "money", "kind": "insurance", "unit": "INS",
        "base": {"freedom_from_harm": 0.8, "repair_capacity": 0.7, "resource_resilience": 0.5, "fairness": 0.4, "reversibility": 0.6},
        "private_gain": 1.0, "red_flags": [], "reversible": True,
    },
    "exploit_labor": {
        "from": "agency", "to": "money", "kind": "harmful_market", "unit": "DEBT",
        "base": {"material_output": 2.9, "liquidity": 0.6, "agency": -2.1, "freedom_from_harm": -1.9, "norm_alignment": -1.2, "behavior_cooperation": -0.4, "fairness": -1.8, "consent_quality": -1.4, "reversibility": -0.5},
        "private_gain": 5.8, "red_flags": ["coercion", "agency_loss"], "reversible": False,
    },
    "fake_truth_certificate": {
        "from": "truth", "to": "money", "kind": "truth_fraud", "unit": "DEBT",
        "base": {"material_output": 1.2, "liquidity": 0.4, "truth": -3.1, "causal_integrity": -1.2, "norm_alignment": -0.8, "fairness": -0.4},
        "private_gain": 4.5, "red_flags": ["fake_truth", "epistemic_fraud"], "reversible": True,
    },
    "coercive_behavior_purchase": {
        "from": "behavior", "to": "money", "kind": "coercion", "unit": "DEBT",
        "base": {"behavior_cooperation": 1.5, "liquidity": 0.3, "agency": -2.6, "freedom_from_harm": -1.5, "norm_alignment": -1.5, "truth": -0.4, "fairness": -1.5, "consent_quality": -2.4},
        "private_gain": 4.0, "red_flags": ["coercion", "unconsented_behavior"], "reversible": False,
    },
    "sabotage_competitor": {
        "from": "effect", "to": "damage", "kind": "sabotage", "unit": "DEBT",
        "base": {"material_output": -2.0, "freedom_from_harm": -2.7, "truth": -0.8, "causal_integrity": -0.5, "norm_alignment": -1.0, "fairness": -0.8, "reversibility": -0.6},
        "private_gain": 3.8, "red_flags": ["harm", "third_party_damage"], "reversible": False,
    },
    "tyrant_hierarchy_inversion": {
        "from": "hierarchy", "to": "hierarchy", "kind": "tyranny", "unit": "DEBT",
        "base": {"hierarchy_legitimacy": -2.9, "agency": -2.3, "truth": -0.6, "norm_alignment": -1.5, "material_output": 0.4, "fairness": -2.0, "consent_quality": -1.4, "reversibility": -0.4},
        "private_gain": 4.4, "red_flags": ["tyrant_metric", "agency_loss"], "reversible": False,
    },
    "metric_hack": {
        "from": "ledger", "to": "money", "kind": "metric_fraud", "unit": "DEBT",
        "base": {"material_output": 0.8, "liquidity": 0.7, "behavior_cooperation": 0.6, "truth": -2.3, "causal_integrity": -1.9, "norm_alignment": -0.7, "fairness": -0.8},
        "private_gain": 3.6, "red_flags": ["metric_fraud"], "reversible": True,
    },
    "self_created_need": {
        "from": "damage", "to": "money", "kind": "self_created_need", "unit": "DEBT",
        "base": {"freedom_from_harm": -3.1, "repair_capacity": -0.6, "truth": -0.5, "norm_alignment": -1.0, "material_output": 0.2, "fairness": -0.8, "reversibility": -0.6},
        "private_gain": 2.6, "red_flags": ["self_caused_harm"], "reversible": False,
    },
}

GOOD_OPERATIONS = [k for k, v in OPERATION_SPECS.items() if not v["red_flags"]]
HARMFUL_OPERATIONS = [k for k, v in OPERATION_SPECS.items() if v["red_flags"]]
ALL_OPERATIONS = list(OPERATION_SPECS.keys())


# ============================================================
# 4. Datenstrukturen
# ============================================================

@dataclass
class OMK:
    id: int
    issuer: str
    owner: str
    operation_family: str
    unit: str
    type_from: str
    type_to: str
    delta: Dict[str, float]
    amount: float
    proof_quality: float
    causal_share: float
    region: str
    step: int
    source: str = "realized"
    reversible: bool = False

    def short(self, colorizer=None):
        label = self.unit
        if colorizer:
            label = colorizer.unit(self.unit, self.unit)
        return (
            "%s OMK#%s amount=%.3f op=%s %s→%s proof=%.2f causal=%.2f region=%s Δ=[%s]"
            % (label, self.id, self.amount, self.operation_family, self.type_from, self.type_to, self.proof_quality, self.causal_share, self.region, format_delta(self.delta, 4))
        )


@dataclass
class MoneyStack:
    credits: List[OMK] = field(default_factory=list)

    def balance(self):
        return sum(c.amount for c in self.credits)

    def deposit(self, credit):
        self.credits.append(credit)

    def deposit_many(self, credits):
        self.credits.extend(credits)

    def spend(self, amount, new_owner, next_id_func):
        if amount <= 0:
            return []
        if self.balance() + 1e-9 < amount:
            return []
        self.credits.sort(key=lambda c: (c.step, c.amount))
        spent = []
        kept = []
        remaining = amount
        for c in self.credits:
            if remaining <= 1e-9:
                kept.append(c)
                continue
            if c.amount <= remaining + 1e-9:
                moved = copy.copy(c)
                moved.owner = new_owner
                spent.append(moved)
                remaining -= c.amount
            else:
                moved = copy.copy(c)
                moved.id = next_id_func()
                moved.owner = new_owner
                moved.amount = remaining
                residual = copy.copy(c)
                residual.id = next_id_func()
                residual.amount = c.amount - remaining
                spent.append(moved)
                kept.append(residual)
                remaining = 0.0
        self.credits = kept
        return spent

    def by_unit(self):
        out = defaultdict(float)
        for c in self.credits:
            out[c.unit] += c.amount
        return dict(out)


@dataclass
class Region:
    id: str
    name: str
    metrics: Dict[str, float]
    latency: int
    trust: Dict[str, float] = field(default_factory=dict)
    local_ledger_size: int = 0
    imported_omk: float = 0.0
    exported_omk: float = 0.0
    invalidated_imports: int = 0

    def score(self):
        return nobility_index(self.metrics)

    def distance(self):
        return metric_distance(self.metrics)

    def apply_delta(self, delta):
        for m in METRICS:
            self.metrics[m] = clamp(self.metrics[m] + delta.get(m, 0.0))


@dataclass
class WorldState:
    regions: Dict[str, Region]
    step: int = 0
    hierarchy: Dict[str, int] = field(default_factory=dict)
    property_rights: Dict[str, List[str]] = field(default_factory=dict)

    def global_metrics(self):
        out = {m: 0.0 for m in METRICS}
        for r in self.regions.values():
            for m in METRICS:
                out[m] += r.metrics[m]
        for m in METRICS:
            out[m] /= float(len(self.regions))
        return out

    def score(self):
        return nobility_index(self.global_metrics())

    def distance(self):
        return metric_distance(self.global_metrics())

    def apply_delta(self, region_id, delta):
        self.regions[region_id].apply_delta(delta)


@dataclass
class Agent:
    id: str
    name: str
    intent: str
    region: str
    role: str
    skills: Dict[str, float]
    wallet: MoneyStack = field(default_factory=MoneyStack)
    fiat_balance: float = 100.0
    reputation: float = 50.0
    stake: float = 50.0
    rank: int = 50
    capital: float = 50.0
    goods: float = 10.0
    energy: float = 10.0
    shares: Dict[str, float] = field(default_factory=dict)
    insurance: float = 0.0
    self_created_need_flag: bool = False
    redline_violations: int = 0
    valid_contribution: float = 0.0
    harmful_contribution: float = 0.0

    def skill(self, family):
        return self.skills.get(family, 0.35)

    def money(self, mode):
        return self.wallet.balance() if mode == "gmoe" else self.fiat_balance


@dataclass
class Security:
    id: str
    issuer: str
    kind: str
    price: float
    shares_outstanding: float
    metric_focus: str
    region: str


@dataclass
class TruthClaim:
    id: str
    issuer: str
    region: str
    created_step: int
    due_step: int
    stake: float
    predicted_true: bool
    fraud: bool
    actual_true: Optional[bool] = None
    resolved: bool = False
    payout: float = 0.0


@dataclass
class CausalClaim:
    id: str
    issuer: str
    region: str
    created_step: int
    due_step: int
    expected_score: float
    realized_score: Optional[float] = None
    causal_share: Optional[float] = None
    resolved: bool = False
    payout: float = 0.0


@dataclass
class BehaviorContract:
    id: str
    participant: str
    sponsor: str
    region: str
    due_step: int
    voluntary: bool
    stake: float
    resolved: bool = False
    payout: float = 0.0


@dataclass
class NormContract:
    id: str
    sponsor: str
    region: str
    start_distance: float
    due_step: int
    resolved: bool = False
    payout: float = 0.0


@dataclass
class CreditContract:
    id: str
    borrower: str
    lender: str
    promised_family: str
    promised_amount: float
    stake: float
    due_step: int
    fulfilled: bool = False


@dataclass
class InsuranceContract:
    id: str
    holder: str
    insurer: str
    premium: float
    coverage: float
    metric: str
    region: str
    active_until: int
    active: bool = True
    paid_out: float = 0.0


@dataclass
class PendingPacket:
    id: str
    source_region: str
    target_region: str
    owner: str
    credits: List[OMK]
    created_step: int
    arrival_step: int
    accepted: Optional[bool] = None
    reason: str = "pending"


@dataclass
class Operation:
    family: str
    actor_id: str
    target_id: Optional[str]
    region: str
    intensity: float
    declared_metric: str
    private_gain: float
    flags: List[str]
    type_from: str
    type_to: str
    unit: str
    reversible: bool

    def realized_delta(self, agent, region, rng):
        spec = OPERATION_SPECS[self.family]
        base = spec["base"]
        skill = agent.skill(self.family)
        factor = self.intensity * (0.50 + 0.95 * skill)
        delta = empty_delta()
        for m, v in base.items():
            noise = rng.uniform(-0.12, 0.12) * abs(v)
            delta[m] = (v + noise) * factor
        for m in METRICS:
            if delta[m] > 0:
                room = max(0.0, TARGET[m] - region.metrics[m])
                delta[m] = min(delta[m], room * 0.36)
            elif delta[m] < 0:
                room_bad = max(0.0, region.metrics[m])
                delta[m] = max(delta[m], -room_bad * 0.36)
        return delta


@dataclass
class ValidationResult:
    accepted: bool
    reason: str
    score: float
    protected_losses: Dict[str, float]
    red_flags: List[str]
    proof_quality: float
    causal_share: float


@dataclass
class LedgerEntry:
    step: int
    mode: str
    region: str
    actor_id: str
    actor_intent: str
    operation: str
    unit: str
    type_from: str
    type_to: str
    accepted: bool
    reason: str
    delta: Dict[str, float]
    score_before: float
    score_after: float
    region_score_before: float
    region_score_after: float
    minted: float
    private_gain: float
    proof_quality: float
    causal_share: float
    flags: List[str]


@dataclass
class MarketEvent:
    step: int
    mode: str
    market: str
    unit: str
    region: str
    actor_a: str
    actor_b: str
    amount: float
    object_id: str
    result: str


# ============================================================
# 5. Governance und Validierung
# ============================================================

class MetricRegistry:
    def __init__(self):
        self.valid_metrics = set(METRICS)
        self.suspended_metrics = set()
        self.revision_count = 0

    def valid(self, metric):
        return metric in self.valid_metrics and metric not in self.suspended_metrics


class Governance:
    def __init__(self, mode, registry):
        self.mode = mode
        self.registry = registry

    def validate(self, op, delta, region, actor, rng):
        score = weighted_score(delta)
        protected_losses = {m: delta[m] for m in PROTECTED if delta.get(m, 0.0) < PROTECTED_LOSS_TOLERANCE}
        red_flags = list(op.flags)
        proof_quality = clamp(0.55 + 0.38 * actor.skill(op.family) + rng.random() * 0.03)
        causal_share = clamp(0.45 + 0.45 * actor.skill(op.family) + rng.random() * 0.04)

        if self.mode == "baseline":
            private = op.private_gain
            private += 0.35 * max(0.0, delta.get("material_output", 0.0))
            private += 0.10 * max(0.0, delta.get("liquidity", 0.0))
            accepted = private > 0.20
            return ValidationResult(accepted, "private-profit-clears" if accepted else "insufficient private profit", score, protected_losses, red_flags, proof_quality, causal_share)

        if not self.registry.valid(op.declared_metric):
            return ValidationResult(False, "invalid or suspended metric", score, protected_losses, red_flags, proof_quality, causal_share)
        if red_flags:
            return ValidationResult(False, "red-line violation: " + ",".join(red_flags), score, protected_losses, red_flags, proof_quality, causal_share)
        if score <= POSITIVE_SCORE_THRESHOLD:
            return ValidationResult(False, "not a positive metric contraction", score, protected_losses, red_flags, proof_quality, causal_share)
        if protected_losses:
            return ValidationResult(False, "protected metric loss", score, protected_losses, red_flags, proof_quality, causal_share)
        meaningful_gain = sum(max(0.0, delta.get(m, 0.0)) * WEIGHTS[m] for m in MEANINGFUL)
        if meaningful_gain <= 0.05:
            return ValidationResult(False, "material/liquidity-only payment", score, protected_losses, red_flags, proof_quality, causal_share)
        if actor.self_created_need_flag and op.family in ("repair_harm", "restore_agency", "insurance_underwrite"):
            return ValidationResult(False, "self-created need cannot be monetized", score, protected_losses, red_flags, proof_quality, causal_share)

        return ValidationResult(True, "valid operator-metric payment", score, protected_losses, red_flags, proof_quality, causal_share)


# ============================================================
# 6. Wirtschaftssimulation
# ============================================================

class Economy:
    def __init__(self, mode, n_agents, n_regions, seed, shock_rate=0.012, scenario="balanced"):
        assert mode in ("gmoe", "baseline")
        self.mode = mode
        self.seed = seed
        self.rng = random.Random(seed)
        if scenario == "auto":
            scenario = self.rng.choice(SCENARIO_ORDER)
        if scenario not in SCENARIOS:
            scenario = "balanced"
        self.scenario_name = scenario
        self.scenario = SCENARIOS[scenario]
        self.shock_rate = max(0.0, shock_rate * self.scenario.get("shock_multiplier", 1.0) + self.scenario.get("shock_add", 0.0))
        self.metric_registry = MetricRegistry()
        self.governance = Governance(mode, self.metric_registry)
        self.next_credit_id = 1
        self.agents: Dict[str, Agent] = {}
        self.securities: Dict[str, Security] = {}
        self.truth_claims: Dict[str, TruthClaim] = {}
        self.causal_claims: Dict[str, CausalClaim] = {}
        self.behavior_contracts: Dict[str, BehaviorContract] = {}
        self.norm_contracts: Dict[str, NormContract] = {}
        self.credit_contracts: List[CreditContract] = []
        self.insurance_contracts: List[InsuranceContract] = []
        self.pending_packets: List[PendingPacket] = []
        self.ledger: List[LedgerEntry] = []
        self.market_events: List[MarketEvent] = []
        self.history: List[Dict[str, Any]] = []
        self.metric_history: List[Dict[str, Any]] = []
        self.repair_fund = MoneyStack()
        self.governance_fund = MoneyStack()
        self.world = self.create_initial_world(max(1, n_regions))
        self.create_agents(n_agents)
        self.create_initial_securities()
        self.genesis_seed_money()

    def next_id(self):
        x = self.next_credit_id
        self.next_credit_id += 1
        return x

    def create_initial_world(self, n_regions):
        regions = {}
        for i in range(n_regions):
            metrics = {}
            for m in METRICS:
                base = self.rng.uniform(41.0, 60.0)
                if i == 0 and m in ("truth", "causal_integrity"):
                    base += 8.0
                if i == 1 and m in ("material_output", "liquidity"):
                    base += 9.0
                if i == 2 and m in ("agency", "fairness", "consent_quality"):
                    base -= 8.0
                if i == 3 and m in ("resource_resilience", "repair_capacity"):
                    base -= 7.0
                base += self.scenario.get("metric_bias", {}).get(m, 0.0)
                metrics[m] = clamp(base)
            rid = "R%02d" % i
            latency = max(1, int(round(self.rng.randint(1, 6) * self.scenario.get("latency_multiplier", 1.0))))
            regions[rid] = Region(id=rid, name="Region_%02d" % i, metrics=metrics, latency=latency)
        for a in regions.values():
            for b in regions.values():
                if a.id == b.id:
                    a.trust[b.id] = 1.0
                else:
                    raw_trust = self.rng.uniform(0.45, 0.90)
                    a.trust[b.id] = clamp(raw_trust * self.scenario.get("trust_multiplier", 1.0) + self.scenario.get("trust_shift", 0.0), 0.05, 1.0)
        return WorldState(regions=regions)

    def create_agents(self, n_agents):
        region_ids = list(self.world.regions.keys())
        roles = ["producer", "auditor", "healer", "engineer", "trader", "governor", "teacher", "insurer", "researcher"]
        for i in range(n_agents):
            noble_share, neutral_share, harmful_share = self.scenario.get("intent", (0.32, 0.44, 0.24))
            if i < int(n_agents * noble_share):
                intent = "noble"
            elif i < int(n_agents * (noble_share + neutral_share)):
                intent = "neutral"
            else:
                intent = "harmful"
            aid = "A%03d" % i
            role = self.rng.choice(roles)
            region = self.rng.choice(region_ids)
            name = "%s_%s_%03d" % (intent.capitalize(), role, i)
            skills = {}
            for fam in ALL_OPERATIONS:
                spec = OPERATION_SPECS[fam]
                kind = spec["kind"]
                if intent == "noble":
                    skills[fam] = self.rng.uniform(0.46, 0.96) if fam in GOOD_OPERATIONS else self.rng.uniform(0.04, 0.30)
                elif intent == "neutral":
                    skills[fam] = self.rng.uniform(0.25, 0.78) if fam in GOOD_OPERATIONS else self.rng.uniform(0.12, 0.48)
                else:
                    skills[fam] = self.rng.uniform(0.12, 0.48) if fam in GOOD_OPERATIONS else self.rng.uniform(0.55, 0.98)
                if role == "auditor" and kind in ("truth", "metric_fraud"):
                    skills[fam] = clamp(skills[fam] + 0.15, 0.0, 1.0)
                if role == "healer" and kind == "repair":
                    skills[fam] = clamp(skills[fam] + 0.18, 0.0, 1.0)
                if role == "engineer" and kind in ("causal", "infrastructure", "production"):
                    skills[fam] = clamp(skills[fam] + 0.14, 0.0, 1.0)
                if role == "teacher" and fam == "education":
                    skills[fam] = clamp(skills[fam] + 0.18, 0.0, 1.0)
                if role == "insurer" and kind == "insurance":
                    skills[fam] = clamp(skills[fam] + 0.18, 0.0, 1.0)
            rank = self.rng.randint(1, 100)
            a = Agent(
                id=aid, name=name, intent=intent, region=region, role=role, skills=skills,
                fiat_balance=self.rng.uniform(80.0, 145.0),
                reputation=self.rng.uniform(45.0, 75.0) if intent != "harmful" else self.rng.uniform(20.0, 55.0),
                stake=self.rng.uniform(30.0, 85.0), rank=rank,
                capital=self.rng.uniform(35.0, 95.0), goods=self.rng.uniform(5.0, 26.0), energy=self.rng.uniform(6.0, 25.0),
            )
            self.agents[aid] = a
            self.world.hierarchy[aid] = rank
            self.world.property_rights[aid] = ["basic_agency", "trade", "appeal", "metric_challenge"]

    def create_initial_securities(self):
        firms = sorted(self.agents.values(), key=lambda a: a.capital + 20.0 * a.skill("produce_goods"), reverse=True)
        firms = firms[:max(3, min(8, max(1, len(self.agents) // 8)))]
        for idx, a in enumerate(firms):
            sid = "STOCK_%s" % a.id
            focus = self.rng.choice(["material_output", "repair_capacity", "truth", "agency", "resource_resilience"])
            self.securities[sid] = Security(id=sid, issuer=a.id, kind="stock", price=18.0 + idx * 2.6, shares_outstanding=100.0, metric_focus=focus, region=a.region)
            a.shares[sid] = 30.0

    def genesis_seed_money(self):
        if self.mode == "baseline":
            return
        for a in self.agents.values():
            delta = empty_delta()
            if a.intent == "noble":
                delta["agency"] = 0.7
                delta["truth"] = 0.4
                delta["fairness"] = 0.3
            elif a.intent == "neutral":
                delta["material_output"] = 0.7
                delta["resource_resilience"] = 0.3
                delta["liquidity"] = 0.2
            else:
                delta["material_output"] = 0.15
            credit = OMK(
                id=self.next_id(), issuer="genesis", owner=a.id,
                operation_family="genesis_certified_past_improvement", unit="OMK",
                type_from="history", type_to="money", delta=delta, amount=positive_amount(delta),
                proof_quality=1.0, causal_share=1.0, region=a.region, step=0, source="genesis", reversible=True,
            )
            a.wallet.deposit(credit)

    def weighted_choice(self, choices, weights):
        total = sum(weights)
        r = self.rng.random() * total
        acc = 0.0
        for c, w in zip(choices, weights):
            acc += w
            if r <= acc:
                return c
        return choices[-1]

    def apply_scenario_operation_bias(self, choices, weights):
        bias = self.scenario.get("op_bias", {})
        if not bias:
            return choices, weights
        return choices, [w * bias.get(c, 1.0) for c, w in zip(choices, weights)]

    def choose_operation_family(self, agent):
        if agent.intent == "noble":
            choices = ["restore_agency", "repair_harm", "truth_audit", "education", "norm_reform", "hierarchy_inversion_repair", "infrastructure_maintenance", "causal_intervention", "voluntary_behavior_contract", "produce_goods", "fair_exchange", "insurance_underwrite"]
            weights = [1.3, 1.25, 1.05, 1.1, 0.85, 0.65, 0.85, 0.75, 0.60, 0.45, 0.50, 0.35]
        elif agent.intent == "neutral":
            choices = ["produce_goods", "infrastructure_maintenance", "truth_audit", "causal_intervention", "voluntary_behavior_contract", "education", "norm_reform", "repair_harm", "fair_exchange", "insurance_underwrite", "exploit_labor", "metric_hack", "fake_truth_certificate"]
            weights = [1.35, 0.90, 0.55, 0.65, 0.55, 0.45, 0.40, 0.30, 0.55, 0.35, 0.14, 0.08, 0.05]
        else:
            choices = ["exploit_labor", "fake_truth_certificate", "coercive_behavior_purchase", "sabotage_competitor", "tyrant_hierarchy_inversion", "metric_hack", "self_created_need", "produce_goods", "truth_audit", "fair_exchange"]
            weights = [1.20, 0.95, 0.90, 0.75, 0.80, 0.80, 0.58, 0.25, 0.10, 0.20]
        choices, weights = self.apply_scenario_operation_bias(choices, weights)
        return self.weighted_choice(choices, weights)

    def choose_operation(self, agent):
        family = self.choose_operation_family(agent)
        spec = OPERATION_SPECS[family]
        intensity = self.rng.uniform(0.42, 1.38)
        target = self.rng.choice(list(self.agents.keys()))
        if target == agent.id:
            target = None
        declared_metric = self.rng.choice(METRICS)
        if agent.intent == "harmful" and self.rng.random() < 0.45:
            declared_metric = self.rng.choice(["material_output", "liquidity", "behavior_cooperation"])
        private_gain = spec["private_gain"] * intensity * (0.50 + agent.skill(family))
        return Operation(
            family=family, actor_id=agent.id, target_id=target, region=agent.region,
            intensity=intensity, declared_metric=declared_metric, private_gain=private_gain,
            flags=list(spec["red_flags"]), type_from=spec["from"], type_to=spec["to"],
            unit=spec.get("unit", "OMK"), reversible=bool(spec["reversible"]),
        )

    def execute_operation(self, op):
        actor = self.agents[op.actor_id]
        region = self.world.regions[op.region]
        global_before = self.world.score()
        region_before = region.score()
        delta = op.realized_delta(actor, region, self.rng)
        validation = self.governance.validate(op, delta, region, actor, self.rng)
        minted = 0.0
        if validation.accepted:
            self.world.apply_delta(op.region, delta)
            region.local_ledger_size += 1
            global_after = self.world.score()
            region_after = region.score()
            if self.mode == "gmoe":
                minted = self.mint_omk(actor, op, delta, validation)
                actor.valid_contribution += weighted_score(delta)
                actor.reputation = clamp(actor.reputation + 0.20 * max(0.0, validation.score))
                actor.stake += 0.035 * minted
                if op.family == "produce_goods":
                    actor.goods += max(0.0, delta.get("material_output", 0.0)) * 1.35
                if op.family == "infrastructure_maintenance":
                    actor.energy += max(0.0, delta.get("resource_resilience", 0.0)) * 0.45
            else:
                actor.fiat_balance += max(0.0, op.private_gain)
                actor.capital += max(0.0, op.private_gain) * 0.20
                actor.reputation = clamp(actor.reputation + 0.035 * validation.score)
                if op.family in ("produce_goods", "exploit_labor"):
                    actor.goods += max(0.0, delta.get("material_output", 0.0)) * 1.2
                if weighted_score(delta) < 0:
                    actor.harmful_contribution += -weighted_score(delta)
        else:
            global_after = global_before
            region_after = region_before
            if self.mode == "gmoe":
                penalty = min(actor.stake, 0.7 + 0.25 * len(op.flags) + max(0.0, -validation.score) * 0.07)
                actor.stake -= penalty
                actor.reputation = clamp(actor.reputation - 0.75 * penalty)
                actor.redline_violations += 1 if op.flags else 0
                if "self_caused_harm" in op.flags:
                    actor.self_created_need_flag = True
            else:
                actor.fiat_balance -= 0.05
        self.ledger.append(LedgerEntry(
            step=self.world.step, mode=self.mode, region=op.region, actor_id=actor.id, actor_intent=actor.intent,
            operation=op.family, unit=op.unit, type_from=op.type_from, type_to=op.type_to,
            accepted=validation.accepted, reason=validation.reason, delta=delta,
            score_before=global_before, score_after=global_after, region_score_before=region_before, region_score_after=region_after,
            minted=minted, private_gain=op.private_gain, proof_quality=validation.proof_quality, causal_share=validation.causal_share,
            flags=op.flags,
        ))
        if validation.accepted or self.mode == "baseline":
            self.maybe_spawn_truth_claim(actor, op)
            self.maybe_spawn_causal_claim(actor, op, delta)
            self.maybe_spawn_behavior_or_norm_contract(actor, op)

    def mint_omk(self, actor, op, delta, validation):
        base_amount = positive_amount(delta)
        if base_amount <= 1e-9:
            return 0.0
        amount = base_amount * validation.proof_quality * validation.causal_share
        distributions = [(actor.id, 0.72), ("__repair_fund__", 0.11), ("__governance_fund__", 0.07)]
        if op.target_id in self.agents:
            distributions.append((op.target_id, 0.10))
        else:
            distributions.append((actor.id, 0.10))
        for owner, share in distributions:
            credit = OMK(
                id=self.next_id(), issuer="GMOE-MINT", owner=owner,
                operation_family=op.family, unit=op.unit if op.unit != "DEBT" else "OMK",
                type_from=op.type_from, type_to=op.type_to, delta=copy.deepcopy(delta), amount=amount * share,
                proof_quality=validation.proof_quality, causal_share=validation.causal_share,
                region=op.region, step=self.world.step, source="realized", reversible=op.reversible,
            )
            if owner == "__repair_fund__":
                credit.unit = "REPAIR"
                self.repair_fund.deposit(credit)
            elif owner == "__governance_fund__":
                credit.unit = "GOV"
                self.governance_fund.deposit(credit)
            else:
                self.agents[owner].wallet.deposit(credit)
        return amount

    # ---------------- Instrumente ----------------

    def maybe_spawn_truth_claim(self, actor, op):
        if op.family not in ("truth_audit", "fake_truth_certificate") or self.rng.random() > 0.35:
            return
        cid = "TC_%d_%s_%d" % (self.world.step, actor.id, len(self.truth_claims) + 1)
        fraud = op.family == "fake_truth_certificate"
        self.truth_claims[cid] = TruthClaim(id=cid, issuer=actor.id, region=op.region, created_step=self.world.step, due_step=self.world.step + self.rng.randint(3, 8), stake=min(actor.stake, self.rng.uniform(1.0, 4.5)), predicted_true=True if not fraud else self.rng.random() < 0.80, fraud=fraud)
        self.market_events.append(MarketEvent(self.world.step, self.mode, "truth_market", "TRUTH", op.region, actor.id, "market", 0.0, cid, "created"))

    def maybe_spawn_causal_claim(self, actor, op, delta):
        if op.family != "causal_intervention" or self.rng.random() > 0.40:
            return
        cid = "CC_%d_%s_%d" % (self.world.step, actor.id, len(self.causal_claims) + 1)
        self.causal_claims[cid] = CausalClaim(id=cid, issuer=actor.id, region=op.region, created_step=self.world.step, due_step=self.world.step + self.rng.randint(4, 9), expected_score=max(0.0, weighted_score(delta)))
        self.market_events.append(MarketEvent(self.world.step, self.mode, "causality_market", "CAUSE", op.region, actor.id, "market", 0.0, cid, "created"))

    def maybe_spawn_behavior_or_norm_contract(self, actor, op):
        if op.family == "voluntary_behavior_contract" and self.rng.random() < 0.30:
            sponsor = actor.id
            participant = op.target_id if op.target_id in self.agents else actor.id
            cid = "BC_%d_%s_%d" % (self.world.step, participant, len(self.behavior_contracts) + 1)
            self.behavior_contracts[cid] = BehaviorContract(id=cid, participant=participant, sponsor=sponsor, region=op.region, due_step=self.world.step + self.rng.randint(3, 7), voluntary=True, stake=1.0 + self.rng.random() * 2.0)
            self.market_events.append(MarketEvent(self.world.step, self.mode, "behavior_market", "BEHAV", op.region, sponsor, participant, 0.0, cid, "created"))
        elif op.family == "norm_reform" and self.rng.random() < 0.28:
            cid = "NC_%d_%s_%d" % (self.world.step, actor.id, len(self.norm_contracts) + 1)
            region = self.world.regions[op.region]
            start_distance = TARGET["norm_alignment"] - region.metrics["norm_alignment"]
            self.norm_contracts[cid] = NormContract(id=cid, sponsor=actor.id, region=op.region, start_distance=start_distance, due_step=self.world.step + self.rng.randint(4, 8))
            self.market_events.append(MarketEvent(self.world.step, self.mode, "norm_market", "NORM", op.region, actor.id, "region", 0.0, cid, "created"))

    def settle_truth_claims(self):
        for claim in list(self.truth_claims.values()):
            if claim.resolved or claim.due_step > self.world.step:
                continue
            issuer = self.agents[claim.issuer]
            actual_true = self.rng.random() < (0.18 if claim.fraud else (0.55 + 0.40 * issuer.skill("truth_audit")))
            claim.actual_true = actual_true
            claim.resolved = True
            if self.mode == "gmoe":
                if actual_true and not claim.fraud:
                    delta = empty_delta(); delta["truth"] = 1.2; delta["causal_integrity"] = 0.3; delta["fairness"] = 0.2
                    amount = positive_amount(delta) * (0.7 + 0.3 * issuer.skill("truth_audit"))
                    credit = OMK(self.next_id(), "TRUTH-SETTLEMENT", issuer.id, "truth_audit", "TRUTH", "truth", "money", delta, amount, 0.95, 0.80, claim.region, self.world.step, "truth_certificate", True)
                    issuer.wallet.deposit(credit); issuer.reputation = clamp(issuer.reputation + 1.5); claim.payout = amount
                else:
                    penalty = min(issuer.stake, claim.stake * (2.0 if claim.fraud else 1.0))
                    issuer.stake -= penalty; issuer.reputation = clamp(issuer.reputation - 2.5 - penalty * 0.3); claim.payout = -penalty
            else:
                if claim.predicted_true == actual_true:
                    payout = claim.stake * 1.7; issuer.fiat_balance += payout; claim.payout = payout
                else:
                    issuer.fiat_balance -= min(issuer.fiat_balance, claim.stake); claim.payout = -claim.stake
            self.market_events.append(MarketEvent(self.world.step, self.mode, "truth_market", "TRUTH", claim.region, claim.issuer, "settlement", claim.payout, claim.id, "resolved_true=%s" % actual_true))

    def settle_causal_claims(self):
        for claim in list(self.causal_claims.values()):
            if claim.resolved or claim.due_step > self.world.step:
                continue
            issuer = self.agents[claim.issuer]
            causal_share = clamp(0.40 + 0.50 * issuer.skill("causal_intervention") + self.rng.uniform(-0.10, 0.10))
            realized = claim.expected_score * causal_share * self.rng.uniform(0.75, 1.25)
            claim.causal_share = causal_share; claim.realized_score = realized; claim.resolved = True
            if self.mode == "gmoe" and realized > 0.05:
                delta = empty_delta(); delta["causal_integrity"] = min(1.5, realized / 3.5); delta["truth"] = min(0.7, realized / 7.0); delta["help_potential"] = min(0.9, realized / 5.5)
                amount = positive_amount(delta) * causal_share
                credit = OMK(self.next_id(), "CAUSAL-SETTLEMENT", issuer.id, "causal_intervention", "CAUSE", "causality", "effect", delta, amount, 0.88, causal_share, claim.region, self.world.step, "causal_certificate", False)
                issuer.wallet.deposit(credit); issuer.reputation = clamp(issuer.reputation + 1.0); claim.payout = amount
            elif self.mode == "baseline":
                payout = max(0.0, realized) * 0.45; issuer.fiat_balance += payout; claim.payout = payout
            self.market_events.append(MarketEvent(self.world.step, self.mode, "causality_market", "CAUSE", claim.region, claim.issuer, "settlement", claim.payout, claim.id, "resolved"))

    def settle_behavior_and_norm_contracts(self):
        for c in list(self.behavior_contracts.values()):
            if c.resolved or c.due_step > self.world.step:
                continue
            participant = self.agents[c.participant]; sponsor = self.agents[c.sponsor]
            success = c.voluntary and self.rng.random() < (0.45 + 0.45 * participant.skill("voluntary_behavior_contract"))
            c.resolved = True
            if self.mode == "gmoe" and success:
                delta = empty_delta(); delta["behavior_cooperation"] = 1.1; delta["consent_quality"] = 0.8; delta["agency"] = 0.25
                amount = positive_amount(delta) * 0.80
                credit = OMK(self.next_id(), "BEHAVIOR-SETTLEMENT", participant.id, "voluntary_behavior_contract", "BEHAV", "behavior", "money", delta, amount, 0.85, 0.75, c.region, self.world.step, "behavior_contract", True)
                participant.wallet.deposit(credit); participant.reputation = clamp(participant.reputation + 0.8); c.payout = amount
            elif self.mode == "baseline" and success:
                payout = min(sponsor.fiat_balance, 2.0); sponsor.fiat_balance -= payout; participant.fiat_balance += payout; c.payout = payout
            self.market_events.append(MarketEvent(self.world.step, self.mode, "behavior_market", "BEHAV", c.region, c.sponsor, c.participant, c.payout, c.id, "resolved_success=%s" % success))
        for c in list(self.norm_contracts.values()):
            if c.resolved or c.due_step > self.world.step:
                continue
            sponsor = self.agents[c.sponsor]; region = self.world.regions[c.region]
            new_distance = TARGET["norm_alignment"] - region.metrics["norm_alignment"]
            improvement = max(0.0, c.start_distance - new_distance)
            c.resolved = True
            if self.mode == "gmoe" and improvement > 0.05:
                delta = empty_delta(); delta["norm_alignment"] = min(1.6, improvement); delta["fairness"] = min(0.8, improvement / 2.0)
                amount = positive_amount(delta) * 0.85
                credit = OMK(self.next_id(), "NORM-SETTLEMENT", sponsor.id, "norm_reform", "NORM", "norm", "behavior", delta, amount, 0.82, 0.72, c.region, self.world.step, "norm_contract", True)
                sponsor.wallet.deposit(credit); c.payout = amount
            elif self.mode == "baseline":
                payout = improvement * 0.6; sponsor.fiat_balance += payout; c.payout = payout
            self.market_events.append(MarketEvent(self.world.step, self.mode, "norm_market", "NORM", c.region, c.sponsor, "region", c.payout, c.id, "resolved"))

    # ---------------- Märkte ----------------

    def pay(self, payer, payee, amount, market, unit, object_id, region):
        if amount <= 0:
            return True
        if self.mode == "gmoe":
            spent = payer.wallet.spend(amount, payee.id, self.next_id)
            if spent:
                payee.wallet.deposit_many(spent)
                self.market_events.append(MarketEvent(self.world.step, self.mode, market, unit, region, payer.id, payee.id, amount, object_id, "paid_omk"))
                return True
            self.market_events.append(MarketEvent(self.world.step, self.mode, market, unit, region, payer.id, payee.id, amount, object_id, "insufficient_omk"))
            return False
        if payer.fiat_balance >= amount:
            payer.fiat_balance -= amount; payee.fiat_balance += amount
            self.market_events.append(MarketEvent(self.world.step, self.mode, market, "FIAT", region, payer.id, payee.id, amount, object_id, "paid_fiat"))
            return True
        self.market_events.append(MarketEvent(self.world.step, self.mode, market, "FIAT", region, payer.id, payee.id, amount, object_id, "insufficient_fiat"))
        return False

    def run_goods_market(self):
        by_region = defaultdict(list)
        for a in self.agents.values(): by_region[a.region].append(a)
        for rid, agents in by_region.items():
            buyers = [a for a in agents if a.goods < 8.0]
            sellers = [a for a in agents if a.goods > 17.0]
            self.rng.shuffle(buyers)
            for buyer in buyers[: max(1, len(buyers) // 2)]:
                if not sellers: break
                seller = self.rng.choice(sellers)
                if seller.goods <= 12.0: continue
                units = min(3.0, seller.goods - 12.0)
                price = units * (1.1 + 0.02 * (100.0 - self.world.regions[rid].metrics["resource_resilience"]))
                if self.pay(buyer, seller, price, "goods_market", "OMK", "goods", rid):
                    seller.goods -= units; buyer.goods += units
                    if self.mode == "gmoe" and self.rng.random() < 0.25:
                        spec = OPERATION_SPECS["fair_exchange"]
                        self.execute_operation(Operation("fair_exchange", buyer.id, seller.id, rid, 0.45, "liquidity", 0.5, [], spec["from"], spec["to"], spec["unit"], True))

    def run_energy_market(self):
        buyers = [a for a in self.agents.values() if a.energy < 7.0]
        sellers = [a for a in self.agents.values() if a.energy > 18.0]
        self.rng.shuffle(buyers)
        for b in buyers[: max(1, len(buyers) // 3)]:
            candidates = [s for s in sellers if s.region == b.region and s.energy > 13.0]
            if not candidates: continue
            s = self.rng.choice(candidates); units = min(2.5, s.energy - 13.0); price = units * 0.9
            if self.pay(b, s, price, "energy_market", "OMK", "energy", b.region):
                b.energy += units; s.energy -= units

    def run_securities_market(self):
        if not self.securities: return
        firms = sorted(self.securities.values(), key=lambda sec: self.agents[sec.issuer].reputation + 0.25 * self.agents[sec.issuer].capital, reverse=True)
        investors = list(self.agents.values()); self.rng.shuffle(investors)
        for investor in investors[: max(2, len(investors) // 5)]:
            sec = self.rng.choice(firms[: min(5, len(firms))]); issuer = self.agents[sec.issuer]
            if investor.id == issuer.id: continue
            shares = self.rng.uniform(0.15, 1.6)
            price = shares * sec.price * (0.75 + issuer.reputation / 125.0)
            if self.pay(investor, issuer, price, "securities_market", "STOCK", sec.id, investor.region):
                investor.shares[sec.id] = investor.shares.get(sec.id, 0.0) + shares

    def distribute_dividends(self):
        for sec in self.securities.values():
            issuer = self.agents[sec.issuer]
            holders = [(a, a.shares.get(sec.id, 0.0)) for a in self.agents.values() if a.shares.get(sec.id, 0.0) > 0]
            total = sum(sh for _, sh in holders)
            if total <= 0: continue
            if self.mode == "gmoe":
                pool = min(issuer.wallet.balance() * 0.012, 3.0)
                if pool <= 0.01: continue
                for holder, sh in holders:
                    amount = pool * sh / total
                    spent = issuer.wallet.spend(amount, holder.id, self.next_id)
                    if spent:
                        holder.wallet.deposit_many(spent)
                        self.market_events.append(MarketEvent(self.world.step, self.mode, "dividend", "STOCK", issuer.region, issuer.id, holder.id, amount, sec.id, "omk_dividend"))
            else:
                pool = min(issuer.fiat_balance * 0.012, 3.0)
                if pool <= 0.01: continue
                issuer.fiat_balance -= pool
                for holder, sh in holders:
                    amount = pool * sh / total; holder.fiat_balance += amount
                    self.market_events.append(MarketEvent(self.world.step, self.mode, "dividend", "STOCK", issuer.region, issuer.id, holder.id, amount, sec.id, "fiat_dividend"))

    def run_credit_market(self):
        if self.mode == "gmoe":
            borrowers = [a for a in self.agents.values() if a.wallet.balance() < 4.5 and a.intent != "harmful"]
            lenders = sorted([a for a in self.agents.values() if a.wallet.balance() > 16.0], key=lambda a: a.wallet.balance(), reverse=True)
            for b in borrowers[:4]:
                if not lenders: break
                lender = lenders[0]
                if lender.id == b.id: continue
                amount = min(3.5, lender.wallet.balance() * 0.07)
                if amount <= 0.25: continue
                spent = lender.wallet.spend(amount, b.id, self.next_id)
                if spent:
                    b.wallet.deposit_many(spent)
                    family = max(GOOD_OPERATIONS, key=lambda f: b.skill(f))
                    c = CreditContract("CR_%d_%s" % (self.world.step, b.id), b.id, lender.id, family, amount * 1.10, min(b.stake, amount), self.world.step + 5)
                    self.credit_contracts.append(c)
                    self.market_events.append(MarketEvent(self.world.step, self.mode, "credit_market", "DEBT", b.region, lender.id, b.id, amount, c.id, "omk_credit"))
        else:
            borrowers = [a for a in self.agents.values() if a.fiat_balance < 35.0]
            lenders = sorted([a for a in self.agents.values() if a.fiat_balance > 155.0], key=lambda a: a.fiat_balance, reverse=True)
            for b in borrowers[:4]:
                if not lenders: break
                lender = lenders[0]; amount = min(12.0, lender.fiat_balance * 0.05)
                lender.fiat_balance -= amount; b.fiat_balance += amount
                c = CreditContract("FIAT_CR_%d_%s" % (self.world.step, b.id), b.id, lender.id, "fiat", amount * 1.16, min(b.stake, amount * 0.5), self.world.step + 5)
                self.credit_contracts.append(c)
                self.market_events.append(MarketEvent(self.world.step, self.mode, "credit_market", "DEBT", b.region, lender.id, b.id, amount, c.id, "fiat_credit"))

    def settle_credit_contracts(self):
        for c in self.credit_contracts:
            if c.fulfilled or c.due_step > self.world.step: continue
            borrower = self.agents[c.borrower]; lender = self.agents[c.lender]
            if self.mode == "gmoe":
                spent = borrower.wallet.spend(c.promised_amount, lender.id, self.next_id)
                if spent:
                    lender.wallet.deposit_many(spent); borrower.reputation = clamp(borrower.reputation + 0.9); result = "fulfilled_omk"
                else:
                    loss = min(borrower.stake, c.stake); borrower.stake -= loss; borrower.reputation = clamp(borrower.reputation - 2.5 - loss * 0.2); result = "default_slash"
                c.fulfilled = True
                self.market_events.append(MarketEvent(self.world.step, self.mode, "credit_settlement", "DEBT", borrower.region, borrower.id, lender.id, c.promised_amount, c.id, result))
            else:
                if borrower.fiat_balance >= c.promised_amount:
                    borrower.fiat_balance -= c.promised_amount; lender.fiat_balance += c.promised_amount; result = "fulfilled_fiat"
                else:
                    loss = min(borrower.stake, c.stake); borrower.stake -= loss; borrower.reputation = clamp(borrower.reputation - 2.0); result = "default"
                c.fulfilled = True
                self.market_events.append(MarketEvent(self.world.step, self.mode, "credit_settlement", "DEBT", borrower.region, borrower.id, lender.id, c.promised_amount, c.id, result))

    def run_insurance_market(self):
        richest = sorted(self.agents.values(), key=lambda a: a.money(self.mode), reverse=True)
        if not richest: return
        insurer = richest[0]
        candidates = [a for a in self.agents.values() if a.id != insurer.id and a.insurance <= 0.0 and a.intent != "harmful"]
        self.rng.shuffle(candidates)
        for holder in candidates[:2]:
            premium = 1.0 + self.rng.random() * 0.8; coverage = 4.0 + self.rng.random() * 3.0
            if self.pay(holder, insurer, premium, "insurance_market", "INS", "insurance", holder.region):
                holder.insurance += coverage
                c = InsuranceContract("IN_%d_%s" % (self.world.step, holder.id), holder.id, insurer.id, premium, coverage, "freedom_from_harm", holder.region, self.world.step + 12)
                self.insurance_contracts.append(c)

    def settle_insurance_after_shock(self, region_id, shock_size):
        for c in self.insurance_contracts:
            if not c.active or c.region != region_id or c.active_until < self.world.step: continue
            holder = self.agents[c.holder]; insurer = self.agents[c.insurer]
            payout = min(c.coverage, max(0.0, shock_size * 1.2))
            if payout <= 0: continue
            if self.pay(insurer, holder, payout, "insurance_payout", "INS", c.id, region_id):
                c.paid_out += payout; c.active = False; holder.insurance = max(0.0, holder.insurance - payout)

    def run_interregional_bridge(self):
        if self.mode != "gmoe" or len(self.world.regions) < 2: return
        candidates = [a for a in self.agents.values() if a.wallet.balance() > 8.0]
        if not candidates: return
        for a in self.rng.sample(candidates, min(3, len(candidates))):
            target_region = self.rng.choice([r for r in self.world.regions.keys() if r != a.region])
            amount = min(2.0, a.wallet.balance() * 0.08)
            if amount <= 0.2: continue
            credits = a.wallet.spend(amount, a.id, self.next_id)
            if not credits: continue
            source = self.world.regions[a.region]; target = self.world.regions[target_region]
            source.exported_omk += amount
            arrival = self.world.step + max(1, source.latency + target.latency + self.rng.randint(-1, 2))
            pid = "PKT_%d_%s_%s_%d" % (self.world.step, a.region, target_region, len(self.pending_packets) + 1)
            self.pending_packets.append(PendingPacket(pid, a.region, target_region, a.id, credits, self.world.step, arrival))
            self.market_events.append(MarketEvent(self.world.step, self.mode, "interregional_bridge", "BRIDGE", a.region, a.id, target_region, amount, pid, "sent"))

    def settle_interregional_packets(self):
        if self.mode != "gmoe": return
        for p in self.pending_packets:
            if p.accepted is not None or p.arrival_step > self.world.step: continue
            source = self.world.regions[p.source_region]; target = self.world.regions[p.target_region]
            trust = target.trust.get(source.id, 0.5)
            proof_quality = safe_mean([c.proof_quality for c in p.credits])
            threshold = 0.50 + 0.15 * (1.0 - trust)
            accepted = trust * proof_quality >= threshold
            p.accepted = accepted
            amount = sum(c.amount for c in p.credits)
            if accepted:
                self.agents[p.owner].wallet.deposit_many(p.credits); target.imported_omk += amount
                actor = self.agents[p.owner]; spec = OPERATION_SPECS["interregional_bridge"]
                self.execute_operation(Operation("interregional_bridge", actor.id, None, p.target_region, 0.35, "liquidity", 0.5, [], spec["from"], spec["to"], spec["unit"], False))
                p.reason = "accepted"
            else:
                target.invalidated_imports += 1; self.agents[p.owner].wallet.deposit_many(p.credits); self.agents[p.owner].reputation = clamp(self.agents[p.owner].reputation - 0.5); p.reason = "rejected_low_trust_or_proof"
            self.market_events.append(MarketEvent(self.world.step, self.mode, "interregional_settlement", "BRIDGE", p.target_region, p.owner, p.target_region, amount, p.id, p.reason))

    def maybe_external_shock(self):
        if self.rng.random() > self.shock_rate: return
        rid = self.rng.choice(list(self.world.regions.keys()))
        region = self.world.regions[rid]
        delta = empty_delta()
        shock_size = self.rng.uniform(1.0, 3.4)
        delta["freedom_from_harm"] = -shock_size
        delta["resource_resilience"] = -self.rng.uniform(0.4, 1.8)
        delta["repair_capacity"] = -self.rng.uniform(0.2, 1.1)
        delta["reversibility"] = -self.rng.uniform(0.1, 0.8)
        before = self.world.score(); rb = region.score()
        self.world.apply_delta(rid, delta)
        after = self.world.score(); ra = region.score()
        self.ledger.append(LedgerEntry(self.world.step, self.mode, rid, "EXTERNAL", "none", "external_shock", "RISK", "environment", "damage", True, "exogenous shock", delta, before, after, rb, ra, 0.0, 0.0, 1.0, 1.0, ["external"]))
        self.market_events.append(MarketEvent(self.world.step, self.mode, "shock", "RISK", rid, "EXTERNAL", "region", shock_size, "shock", "occurred"))
        self.settle_insurance_after_shock(rid, shock_size)

    def repair_fund_action(self):
        if self.mode != "gmoe" or self.repair_fund.balance() < 1.5: return
        regions = sorted(self.world.regions.values(), key=lambda r: r.metrics["freedom_from_harm"] + r.metrics["agency"] + r.metrics["fairness"])
        region = regions[0]
        candidates = [a for a in self.agents.values() if a.region == region.id]
        if not candidates: return
        actor = max(candidates, key=lambda a: a.skill("repair_harm") + a.skill("restore_agency"))
        grant = min(2.5, self.repair_fund.balance() * 0.10)
        spent = self.repair_fund.spend(grant, actor.id, self.next_id)
        if spent:
            actor.wallet.deposit_many(spent)
            opfam = "repair_harm" if region.metrics["freedom_from_harm"] < region.metrics["agency"] else "restore_agency"
            spec = OPERATION_SPECS[opfam]
            self.execute_operation(Operation(opfam, actor.id, None, region.id, 0.75, "freedom_from_harm", 1.0, [], spec["from"], spec["to"], spec["unit"], spec["reversible"]))
            self.market_events.append(MarketEvent(self.world.step, self.mode, "repair_fund", "REPAIR", region.id, "repair_fund", actor.id, grant, opfam, "funded"))

    def step_once(self):
        self.world.step += 1
        score_start = self.world.score(); dist_start = self.world.distance()
        self.maybe_external_shock()
        agents = list(self.agents.values()); self.rng.shuffle(agents)
        active_count = max(1, int(len(agents) * 0.58))
        for a in agents[:active_count]:
            self.execute_operation(self.choose_operation(a))
        self.settle_truth_claims(); self.settle_causal_claims(); self.settle_behavior_and_norm_contracts()
        self.run_goods_market(); self.run_energy_market(); self.run_securities_market(); self.distribute_dividends()
        self.run_credit_market(); self.settle_credit_contracts(); self.run_insurance_market()
        self.run_interregional_bridge(); self.settle_interregional_packets(); self.repair_fund_action()
        score_end = self.world.score(); dist_end = self.world.distance()
        self.history.append({
            "step": self.world.step, "mode": self.mode, "score_start": score_start, "score_end": score_end,
            "score_change": score_end - score_start, "distance_start": dist_start, "distance_end": dist_end,
            "distance_change": dist_end - dist_start, "total_omk": self.total_omk_balance(),
            "total_fiat": sum(a.fiat_balance for a in self.agents.values()),
            "accepted": sum(1 for e in self.ledger if e.step == self.world.step and e.accepted and e.actor_id != "EXTERNAL"),
            "rejected": sum(1 for e in self.ledger if e.step == self.world.step and not e.accepted),
            "harmful_accepted": sum(1 for e in self.ledger if e.step == self.world.step and e.accepted and e.operation in HARMFUL_OPERATIONS),
        })
        metrics_row = {"step": self.world.step, "mode": self.mode}
        gm = self.world.global_metrics()
        for m in METRICS: metrics_row[m] = gm[m]
        self.metric_history.append(metrics_row)

    def run(self, steps):
        for _ in range(steps):
            self.step_once()

    # ---------------- Analyse ----------------

    def total_omk_balance(self):
        return sum(a.wallet.balance() for a in self.agents.values()) + self.repair_fund.balance() + self.governance_fund.balance()

    def accepted_entries(self):
        return [e for e in self.ledger if e.accepted and e.actor_id != "EXTERNAL"]

    def rejected_entries(self):
        return [e for e in self.ledger if not e.accepted]

    def harmful_accepted_count(self):
        return sum(1 for e in self.accepted_entries() if e.operation in HARMFUL_OPERATIONS)

    def positive_cone_violations_among_accepted(self):
        count = 0
        for e in self.accepted_entries():
            if e.operation in HARMFUL_OPERATIONS:
                count += 1; continue
            if weighted_score(e.delta) <= POSITIVE_SCORE_THRESHOLD:
                count += 1; continue
            for m in PROTECTED:
                if e.delta.get(m, 0.0) < PROTECTED_LOSS_TOLERANCE:
                    count += 1; break
        return count

    def cumulative_accepted_score(self):
        return sum(weighted_score(e.delta) for e in self.accepted_entries())

    def monotonic_score_steps(self):
        if len(self.history) < 2: return 0, 0
        ok = 0; total = 0; prev = self.history[0]["score_end"]
        for h in self.history[1:]:
            total += 1
            if h["score_end"] + 1e-9 >= prev: ok += 1
            prev = h["score_end"]
        return ok, total

    def top_agents_by_money(self, n=8):
        return sorted(self.agents.values(), key=lambda a: a.money(self.mode), reverse=True)[:n]

    def operation_summary_rows(self):
        stats = {}
        for e in self.ledger:
            key = e.operation
            if key not in stats:
                stats[key] = {"operation": key, "unit": e.unit, "accepted": 0, "rejected": 0, "minted": 0.0, "weighted_score": 0.0, "private_gain": 0.0, "protected_loss": 0.0, "harmful_family": int(key in HARMFUL_OPERATIONS)}
            row = stats[key]
            row["accepted" if e.accepted else "rejected"] += 1
            row["minted"] += e.minted; row["weighted_score"] += weighted_score(e.delta); row["private_gain"] += e.private_gain; row["protected_loss"] += protected_loss(e.delta)
        return list(stats.values())

    def market_summary_rows(self):
        stats = {}
        for e in self.market_events:
            key = e.market
            if key not in stats:
                stats[key] = {"market": key, "unit": e.unit, "events": 0, "amount": 0.0, "success_events": 0, "failed_events": 0}
            stats[key]["events"] += 1; stats[key]["amount"] += e.amount
            if any(word in e.result for word in ("paid", "fulfilled", "created", "resolved", "sent", "accepted", "funded", "dividend")):
                stats[key]["success_events"] += 1
            if any(word in e.result for word in ("insufficient", "default", "rejected")):
                stats[key]["failed_events"] += 1
        return list(stats.values())

    def intent_summary_rows(self):
        rows = []
        for intent in sorted(set(a.intent for a in self.agents.values())):
            group = [a for a in self.agents.values() if a.intent == intent]
            rows.append({
                "intent": intent, "count": len(group), "avg_money": safe_mean([a.money(self.mode) for a in group]),
                "avg_reputation": safe_mean([a.reputation for a in group]), "avg_stake": safe_mean([a.stake for a in group]),
                "avg_valid_contribution": safe_mean([a.valid_contribution for a in group]), "avg_harmful_contribution": safe_mean([a.harmful_contribution for a in group]),
                "redline_violations": sum(a.redline_violations for a in group),
            })
        return rows

    def unit_balances(self):
        out = defaultdict(float)
        if self.mode == "gmoe":
            for a in self.agents.values():
                for k, v in a.wallet.by_unit().items(): out[k] += v
            for k, v in self.repair_fund.by_unit().items(): out[k] += v
            for k, v in self.governance_fund.by_unit().items(): out[k] += v
        else:
            out["FIAT"] = sum(a.fiat_balance for a in self.agents.values())
        return dict(out)

    def diagnostics(self):
        accepted = self.accepted_entries(); rejected = self.rejected_entries(); ok, total = self.monotonic_score_steps()
        money_by_agent = [a.money(self.mode) for a in self.agents.values()]
        rep_by_agent = [a.reputation for a in self.agents.values()]
        valid_by_agent = [a.valid_contribution for a in self.agents.values()]
        return {
            "scenario": self.scenario_name,
            "scenario_title": self.scenario.get("title", self.scenario_name),
            "accepted_transactions": len(accepted),
            "rejected_transactions": len(rejected),
            "harmful_accepted": self.harmful_accepted_count(),
            "positive_cone_violations_among_accepted": self.positive_cone_violations_among_accepted(),
            "cumulative_accepted_weighted_score": self.cumulative_accepted_score(),
            "score_nondecreasing_transitions": ok,
            "score_transition_total": total,
            "final_nobility_index": self.world.score(),
            "final_distance_to_target": self.world.distance(),
            "total_omk": self.total_omk_balance(),
            "total_fiat": sum(a.fiat_balance for a in self.agents.values()),
            "money_gini": gini(money_by_agent),
            "corr_money_reputation": pearson(money_by_agent, rep_by_agent),
            "corr_money_valid_contribution": pearson(money_by_agent, valid_by_agent),
            "pending_packets": sum(1 for p in self.pending_packets if p.accepted is None),
            "accepted_packets": sum(1 for p in self.pending_packets if p.accepted is True),
            "rejected_packets": sum(1 for p in self.pending_packets if p.accepted is False),
        }

    # ---------------- CSV Export ----------------

    def agents_rows(self):
        rows = []
        for a in self.agents.values():
            rows.append({
                "id": a.id, "name": a.name, "intent": a.intent, "role": a.role, "region": a.region,
                "money": a.money(self.mode), "omk_balance": a.wallet.balance(), "fiat_balance": a.fiat_balance,
                "reputation": a.reputation, "stake": a.stake, "rank": a.rank, "capital": a.capital,
                "goods": a.goods, "energy": a.energy, "insurance": a.insurance,
                "self_created_need_flag": int(a.self_created_need_flag), "redline_violations": a.redline_violations,
                "valid_contribution": a.valid_contribution, "harmful_contribution": a.harmful_contribution,
                "wallet_units": len(a.wallet.credits),
            })
        return rows

    def region_rows(self):
        rows = []
        for r in self.world.regions.values():
            row = {"id": r.id, "name": r.name, "score": r.score(), "distance": r.distance(), "latency": r.latency, "local_ledger_size": r.local_ledger_size, "imported_omk": r.imported_omk, "exported_omk": r.exported_omk, "invalidated_imports": r.invalidated_imports}
            for m in METRICS: row[m] = r.metrics[m]
            rows.append(row)
        return rows

    def ledger_rows(self):
        rows = []
        for e in self.ledger:
            row = {"step": e.step, "mode": e.mode, "region": e.region, "actor_id": e.actor_id, "actor_intent": e.actor_intent, "operation": e.operation, "unit": e.unit, "type_from": e.type_from, "type_to": e.type_to, "accepted": int(e.accepted), "reason": e.reason, "score_before": e.score_before, "score_after": e.score_after, "region_score_before": e.region_score_before, "region_score_after": e.region_score_after, "weighted_delta_score": weighted_score(e.delta), "protected_loss": protected_loss(e.delta), "minted": e.minted, "private_gain": e.private_gain, "proof_quality": e.proof_quality, "causal_share": e.causal_share, "flags": ";".join(e.flags)}
            for m in METRICS: row["delta_" + m] = e.delta.get(m, 0.0)
            rows.append(row)
        return rows

    def market_event_rows(self): return [e.__dict__.copy() for e in self.market_events]
    def security_rows(self): return [s.__dict__.copy() for s in self.securities.values()]
    def truth_claim_rows(self): return [c.__dict__.copy() for c in self.truth_claims.values()]
    def causal_claim_rows(self): return [c.__dict__.copy() for c in self.causal_claims.values()]
    def behavior_contract_rows(self): return [c.__dict__.copy() for c in self.behavior_contracts.values()]
    def norm_contract_rows(self): return [c.__dict__.copy() for c in self.norm_contracts.values()]
    def credit_contract_rows(self): return [c.__dict__.copy() for c in self.credit_contracts]
    def insurance_contract_rows(self): return [c.__dict__.copy() for c in self.insurance_contracts]

    def packet_rows(self):
        rows = []
        for p in self.pending_packets:
            rows.append({"id": p.id, "source_region": p.source_region, "target_region": p.target_region, "owner": p.owner, "created_step": p.created_step, "arrival_step": p.arrival_step, "accepted": p.accepted, "reason": p.reason, "amount": sum(c.amount for c in p.credits), "avg_proof_quality": safe_mean([c.proof_quality for c in p.credits])})
        return rows

    def omk_wallet_rows(self, limit_per_agent=20):
        rows = []
        if self.mode != "gmoe": return rows
        for a in self.agents.values():
            top = sorted(a.wallet.credits, key=lambda c: c.amount, reverse=True)[:limit_per_agent]
            for c in top:
                row = {"agent_id": a.id, "agent_name": a.name, "agent_intent": a.intent, "agent_region": a.region, "omk_id": c.id, "amount": c.amount, "issuer": c.issuer, "unit": c.unit, "operation_family": c.operation_family, "type_from": c.type_from, "type_to": c.type_to, "proof_quality": c.proof_quality, "causal_share": c.causal_share, "source": c.source, "region": c.region, "step": c.step, "reversible": int(c.reversible)}
                for m in METRICS: row["delta_" + m] = c.delta.get(m, 0.0)
                rows.append(row)
        return rows

    def hierarchy_rows(self):
        return [{"agent_id": a.id, "name": a.name, "intent": a.intent, "region": a.region, "rank": self.world.hierarchy.get(a.id, a.rank), "reputation": a.reputation, "money": a.money(self.mode)} for a in self.agents.values()]

    def export_csv(self, outdir):
        ensure_dir(outdir)
        write_csv(os.path.join(outdir, "%s_history.csv" % self.mode), self.history)
        write_csv(os.path.join(outdir, "%s_metric_history.csv" % self.mode), self.metric_history)
        write_csv(os.path.join(outdir, "%s_agents_final.csv" % self.mode), self.agents_rows())
        write_csv(os.path.join(outdir, "%s_regions_final.csv" % self.mode), self.region_rows())
        write_csv(os.path.join(outdir, "%s_ledger.csv" % self.mode), self.ledger_rows())
        write_csv(os.path.join(outdir, "%s_market_events.csv" % self.mode), self.market_event_rows())
        write_csv(os.path.join(outdir, "%s_operation_summary.csv" % self.mode), self.operation_summary_rows())
        write_csv(os.path.join(outdir, "%s_market_summary.csv" % self.mode), self.market_summary_rows())
        write_csv(os.path.join(outdir, "%s_intent_summary.csv" % self.mode), self.intent_summary_rows())
        write_csv(os.path.join(outdir, "%s_diagnostics.csv" % self.mode), [self.diagnostics()])
        write_csv(os.path.join(outdir, "%s_securities.csv" % self.mode), self.security_rows())
        write_csv(os.path.join(outdir, "%s_truth_claims.csv" % self.mode), self.truth_claim_rows())
        write_csv(os.path.join(outdir, "%s_causal_claims.csv" % self.mode), self.causal_claim_rows())
        write_csv(os.path.join(outdir, "%s_behavior_contracts.csv" % self.mode), self.behavior_contract_rows())
        write_csv(os.path.join(outdir, "%s_norm_contracts.csv" % self.mode), self.norm_contract_rows())
        write_csv(os.path.join(outdir, "%s_credit_contracts.csv" % self.mode), self.credit_contract_rows())
        write_csv(os.path.join(outdir, "%s_insurance_contracts.csv" % self.mode), self.insurance_contract_rows())
        write_csv(os.path.join(outdir, "%s_interregional_packets.csv" % self.mode), self.packet_rows())
        write_csv(os.path.join(outdir, "%s_omk_wallets.csv" % self.mode), self.omk_wallet_rows(limit_per_agent=20))
        write_csv(os.path.join(outdir, "%s_hierarchy.csv" % self.mode), self.hierarchy_rows())


# ============================================================
# 7. Visualisierung und ausführliche Auswertung
# ============================================================


class VisualReport:
    def __init__(self, colorizer, width=118):
        self.cz = colorizer
        self.width = terminal_safe_width(width)

    # ---------- small visual helpers ----------

    def _abbr_lines(self, pairs):
        lines = [self.cz.c("Kürzel in genau dieser UTF-8-Art:", Palette.BRIGHT_WHITE)]
        for key, explanation in pairs:
            lines.append("  %s = %s" % (self.cz.c(str(key), Palette.BRIGHT_YELLOW), explanation))
        return lines

    def _eval_lines(self, lines):
        out = [self.cz.c("Auswertung dieser Abbildung:", Palette.BRIGHT_WHITE)]
        out.extend(lines)
        return out

    def _section(self, title, abbrs, art_lines, eval_lines, color):
        return box(title, self._abbr_lines(abbrs) + [""] + art_lines + [""] + self._eval_lines(eval_lines), self.cz, self.width, color)

    def _bar_width(self, reserve=52, max_width=44, min_width=14):
        return max(min_width, min(max_width, self.width - reserve))

    def _spark_width(self):
        return max(20, min(90, self.width - 38))

    def _rainbow(self, text):
        colors = [Palette.BRIGHT_RED, Palette.BRIGHT_YELLOW, Palette.BRIGHT_GREEN, Palette.BRIGHT_CYAN, Palette.BRIGHT_BLUE, Palette.BRIGHT_MAGENTA]
        if not self.cz.enabled:
            return text
        out = []
        for i, ch in enumerate(str(text)):
            if ch == " ":
                out.append(ch)
            else:
                out.append(colors[i % len(colors)] + ch + Palette.RESET)
        return "".join(out)

    # ---------- sections ----------

    def banner(self):
        art = [
            self.cz.c("   ██████╗ ███╗   ███╗ ██████╗ ███████╗", Palette.BRIGHT_CYAN) + "  " + self.cz.c("METRIC OPERATOR ECONOMY", Palette.BRIGHT_GREEN),
            self.cz.c("  ██╔════╝ ████╗ ████║██╔═══██╗██╔════╝", Palette.BRIGHT_CYAN) + "  " + self.cz.c("Geld = Operation + Metrik + Δ∈K+", Palette.BRIGHT_YELLOW),
            self.cz.c("  ██║  ███╗██╔████╔██║██║   ██║█████╗  ", Palette.BRIGHT_CYAN) + "  " + self.cz.c("Galaktische Transformationsökonomie", Palette.BRIGHT_MAGENTA),
            self.cz.c("  ██║   ██║██║╚██╔╝██║██║   ██║██╔══╝  ", Palette.BRIGHT_CYAN) + "  " + self.cz.c("UTF-8 Visual Report", Palette.BRIGHT_BLUE),
            self.cz.c("  ╚██████╔╝██║ ╚═╝ ██║╚██████╔╝███████╗", Palette.BRIGHT_CYAN) + "  " + self.cz.c("f: Ω → Ω", Palette.BRIGHT_GREEN),
            self.cz.c("   ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚══════╝", Palette.BRIGHT_CYAN),
            "",
            self._rainbow("Breitenregel: Jede Box ist höchstens Bildschirmbreite minus 5 Zeichen breit."),
        ]
        return self._section(
            "Titelbild und Breitenregel",
            [("GMOE", "Galactic Metric Operator Economy, also die galaktische metrische Operatorökonomie."), ("f:Ω→Ω", "unäre Operation: ein Weltzustand Ω wird in einen neuen Weltzustand Ω überführt."), ("Δ∈K+", "die gemessene Zustandsänderung Δ liegt im positiven Kegel K+, also in einer erlaubten Verbesserungsrichtung.")],
            art,
            ["Das Titelbild markiert den Grundsatz der Simulation: Nicht der nackte Geldbetrag ist das Fundament, sondern eine geprüfte Zustandsoperation. Die dynamische Breite verhindert, dass breite UTF-8-Grafiken den Terminalrand berühren."],
            Palette.BRIGHT_CYAN,
        )

    def color_legend(self):
        units = ["OMK", "FIAT", "TRUTH", "CAUSE", "NORM", "BEHAV", "HIER", "REPAIR", "GOV", "INS", "STOCK", "BRIDGE", "DEBT", "RISK", "REP", "K+"]
        art = []
        for key in units:
            art.append("%s  %s" % (pad(self.cz.unit(key, key), 12), UNIT_EXPLANATION[key]))
        art.append("")
        art.append(self.cz.c("Farbregel:", Palette.BRIGHT_WHITE) + " Jede Einheit behält im gesamten Skript dieselbe Farbe.")
        return self._section(
            "Feste Farben für Einheiten, Währungen, Fonds und Instrumente",
            [(k, UNIT_EXPLANATION[k]) for k in units],
            art,
            ["Die Farbcodierung macht Tabellen und Diagramme schneller lesbar. Wenn zum Beispiel OMK immer cyan und TRUTH immer grün ist, erkennt man sofort, ob Geld aus allgemeiner Operator-Metrik-Leistung, Wahrheitsprüfung oder Kausalitätsarbeit stammt."],
            Palette.BRIGHT_CYAN,
        )

    def abbreviation_legend(self):
        metric_pairs = [(METRIC_SHORT[m], METRIC_EXPLANATION[m]) for m in METRICS]
        art = [
            "Ω      gesamter Weltzustand der Simulation.",
            "ω_t    Weltzustand zum Zeitpunkt t.",
            "ω*     Ziel-, Norm- oder Referenzzustand.",
            "f      unäre Operation; sie transformiert einen Zustand in einen Folgezustand.",
            "Δ      gemessene Änderung nach Anwendung von f.",
            "K+     positiver Kegel; gültige Verbesserungsrichtungen im Metrikraum.",
            "NI     Nobility Index, gewichteter Gesamtwert aller Metriken auf Skala 0..100.",
            "DIST   gewichtete Distanz zum Zielzustand 100; niedriger ist besser.",
            "Pq     Proof Quality, Nachweisqualität von 0..1.",
            "Cs     Causal Share, kausal zugerechneter Anteil von 0..1.",
            "Gini   Ungleichheit der Geldverteilung; 0 = gleich, 1 = extrem ungleich.",
            "",
            self.cz.c("Metrikkürzel:", Palette.BRIGHT_WHITE),
        ]
        for m in METRICS:
            art.append("%s %-8s %s" % (self.cz.metric(m, METRIC_SHORT[m]), "(" + m + ")", METRIC_EXPLANATION[m]))
        return self._section(
            "Globale Kürzel und Einheiten",
            [("Ω", "Weltzustand"), ("ω_t", "aktueller Zustand"), ("ω*", "Zielzustand"), ("f", "unäre Operation"), ("Δ", "Metrikänderung"), ("K+", "positiver Kegel"), ("NI", "Nobility Index"), ("DIST", "Distanz zum Ziel"), ("Pq", "Proof Quality"), ("Cs", "Causal Share"), ("Gini", "Ungleichheitsmaß")] + metric_pairs,
            art,
            ["Diese Legende ist die Übersetzungsschicht. Die späteren Diagramme verwenden nur noch die jeweils benötigten Kürzel, damit jedes Bild lokal verständlich bleibt."],
            Palette.BRIGHT_BLUE,
        )

    def scenario_panel(self, econ):
        title = econ.scenario.get("title", econ.scenario_name)
        desc = econ.scenario.get("desc", "")
        nob, neu, harm = econ.scenario.get("intent", (0.0, 0.0, 0.0))
        art = [
            self.cz.c("┌─ Szenario-Profil ─────────────────────────────────────────────┐", Palette.BRIGHT_MAGENTA),
            "  SCN  : %s (%s)" % (self.cz.c(title, Palette.BRIGHT_WHITE), econ.scenario_name),
            "  DESC : %s" % desc,
            "  INT  : noble %.0f%% | neutral %.0f%% | harmful %.0f%%" % (nob * 100, neu * 100, harm * 100),
            "  SR   : effektive Schockrate %.4f pro Schritt" % econ.shock_rate,
            "  TR   : Vertrauensfaktor %.2f %+0.2f" % (econ.scenario.get("trust_multiplier", 1.0), econ.scenario.get("trust_shift", 0.0)),
            "  LAT  : Latenzfaktor %.2f" % econ.scenario.get("latency_multiplier", 1.0),
            self.cz.c("└────────────────────────────────────────────────────────────────┘", Palette.BRIGHT_MAGENTA),
            "",
            "Mögliche Ausgänge: Wachstum, Stagnation, Rückschlag durch Schocks, Baseline-Überraschung, GMOE-Schutzwirkung, regionale Fragmentierung.",
            "Der Ausgang hängt von Seed, Schocks, Akteursmix, regionalem Vertrauen, Latenz und zufälligen Operationen ab.",
        ]
        return self._section(
            "Szenario und mögliche Ausgänge",
            [("SCN", "Scenario Name, also das gewählte Szenario."), ("DESC", "Beschreibung der Startlage."), ("INT", "Intent-Verteilung: Anteil nobler, neutraler und schädlicher Akteure."), ("SR", "Shock Rate: Wahrscheinlichkeit externer negativer Schocks pro Schritt."), ("TR", "Trust-Regel: Multiplikator und Verschiebung für Vertrauen zwischen Regionen."), ("LAT", "Latency: Faktor für interregionale Verzögerungen."), ("Seed", "Zufallsstartwert; andere Seeds können andere Ausgänge erzeugen.")],
            art,
            ["Diese Abbildung erklärt, warum die Simulation jetzt verschieden ausgehen kann. Das GMOE-Prinzip erzwingt weiterhin positive Wurzelzahlungen, aber externe Schocks, Latenz und Akteursmix können den Gesamtpfad unterschiedlich machen."],
            Palette.BRIGHT_MAGENTA,
        )

    def operator_diagram(self, econ):
        art = [
            "        " + self.cz.c("ω_t", Palette.BRIGHT_WHITE) + "  " + self.cz.c("─" * 6, Palette.GRAY) + "  " + self.cz.unit("OMK", "f:Ω→Ω") + "  " + self.cz.c("─" * 6, Palette.GRAY) + "  " + self.cz.c("ω_{t+1}", Palette.BRIGHT_WHITE),
            "                    │",
            "                    ▼",
            "            " + self.cz.metric("truth", "d⃗ misst") + ":  Δ = d(ω_t,ω*) - d(f(ω_t),ω*)",
            "                    │",
            "                    ▼",
            "        " + self.cz.unit("K+", "Δ∈K+") + " ?  ── ja ──►  " + self.cz.unit("OMK", "OMK prägen") + "  ──►  Markt / Kredit / Dividende",
            "            │",
            "            nein",
            "            ▼",
            "        " + self.cz.unit("DEBT", "Ablehnung / Slashing / Haftung / Reparaturpflicht"),
        ]
        return self._section(
            "Operator-Metrik-Zahlungsfluss",
            [("ω_t", "aktueller Weltzustand vor der Operation."), ("ω_{t+1}", "Folgezustand nach Anwendung der Operation."), ("f:Ω→Ω", "unäre Operation auf dem gesamten Zustandsraum."), ("d⃗", "Metrikvektor; misst mehrere Dimensionen gleichzeitig."), ("Δ", "Distanzverringerung oder -vergrößerung."), ("K+", "positiver Kegel gültiger Verbesserung."), ("OMK", "Operation-Metrik-Kredit; zählbares Wurzelgeld."), ("DEBT", "Schuld/Haftung statt Geldprägung.")],
            art,
            ["Dieses Diagramm ist die zentrale Buchungslogik. GMOE prägt Geld erst nach einer bestandenen Metrikprüfung. Deshalb wird akzeptierter Wurzelhandel im Modell zu einer Kette geprüfter positiver Operatoren."],
            Palette.BRIGHT_MAGENTA,
        )

    def summary_table(self, econ, title="Kernzahlen der Simulation"):
        d = econ.diagnostics()
        initial = econ.history[0]["score_start"] if econ.history else econ.world.score()
        final = econ.world.score()
        rows = [
            ("SCN", econ.scenario_name),
            ("Modus", econ.mode),
            ("Seed", econ.seed),
            ("Steps", econ.world.step),
            ("Agents", len(econ.agents)),
            ("Regions", len(econ.world.regions)),
            ("NI Start", "%.3f" % initial),
            ("NI Ende", "%.3f" % final),
            ("NI Δ", "%+.3f" % (final - initial)),
            ("DIST Ende", "%.3f" % econ.world.distance()),
            ("accepted", d["accepted_transactions"]),
            ("rejected", d["rejected_transactions"]),
            ("harmful accepted", d["harmful_accepted"]),
            ("K+ violations", d["positive_cone_violations_among_accepted"]),
            ("ΣΔScore", "%+.3f" % d["cumulative_accepted_weighted_score"]),
            ("Gini", "%.3f" % d["money_gini"]),
            ("corr(M,Rep)", "%.3f" % d["corr_money_reputation"]),
            ("corr(M,Δvalid)", "%.3f" % d["corr_money_valid_contribution"]),
        ]
        art = []
        for k, v in rows:
            key = self.cz.c(k, Palette.BRIGHT_WHITE)
            val = str(v)
            if k in ("K+ violations", "harmful accepted"):
                try:
                    val = self.cz.green(val) if int(v) == 0 else self.cz.red(val)
                except Exception:
                    pass
            if k == "NI Δ":
                val = self.cz.green(val) if float(str(v)) >= 0 else self.cz.red(val)
            art.append("%s : %s" % (pad(key, 24), val))
        return self._section(
            title,
            [("SCN", "Szenario."), ("NI", "Nobility Index, gewichteter Gesamtwert 0..100."), ("DIST", "Distanz zum Zielzustand; niedriger ist besser."), ("accepted", "akzeptierte Transaktionen."), ("rejected", "abgelehnte Transaktionen."), ("K+", "positiver Kegel."), ("ΣΔScore", "Summe gewichteter Metrikänderungen."), ("Gini", "Ungleichheit der Geldverteilung."), ("corr", "Korrelation zwischen zwei Größen."), ("M", "Geldbestand."), ("Rep", "Reputation."), ("Δvalid", "gültiger Beitrag im Metrikraum.")],
            art,
            ["Die Kernzahlen prüfen, ob das Szenario zu Verbesserung oder Rückgang führte. Der wichtigste GMOE-Invariant ist K+ violations = 0: Dann lag jede akzeptierte Wurzelzahlung im erlaubten positiven Metrikkegel."],
            Palette.BRIGHT_GREEN if econ.mode == "gmoe" else Palette.GRAY,
        )

    def score_sparkline(self, econ):
        vals = [h["score_end"] for h in econ.history]
        dist = [h["distance_end"] for h in econ.history]
        width = self._spark_width()
        art = [
            "NI   : " + sparkline(vals, width, self.cz) + "  min=%.2f max=%.2f" % (min(vals) if vals else 0, max(vals) if vals else 0),
            "DIST : " + self.cz.c(sparkline(dist, width), Palette.BRIGHT_YELLOW) + "  min=%.2f max=%.2f" % (min(dist) if dist else 0, max(dist) if dist else 0),
            "       " + self.cz.c("▁▂▃▄▅▆▇█", Palette.BRIGHT_CYAN) + " = Verlauf von niedrig nach hoch; jeder Block ist ein Zeitfenster.",
        ]
        trend = (vals[-1] - vals[0]) if len(vals) >= 2 else 0.0
        ev = "Der NI-Verlauf steigt insgesamt." if trend >= 0 else "Der NI-Verlauf fällt insgesamt; das kann durch Schocks, Knappheit oder Fragmentierung passieren."
        return self._section(
            "Zeitverlauf: Nobility Index und Distanz",
            [("NI", "Nobility Index; höher ist besser."), ("DIST", "Distanz zum Zielzustand; niedriger ist besser."), ("min", "kleinster beobachteter Wert."), ("max", "größter beobachteter Wert."), ("▁▂▃▄▅▆▇█", "Sparkline-Zeichen von niedrig bis hoch.")],
            art,
            [ev, "Diese Grafik zeigt nicht nur den Endwert, sondern den Pfad. Dadurch sieht man, ob die Verbesserung stetig war oder ob äußere Schocks die Richtung zeitweise umgedreht haben."],
            Palette.BRIGHT_CYAN,
        )

    def metric_dashboard(self, econ):
        gm = econ.world.global_metrics()
        bw = self._bar_width(reserve=42, max_width=46)
        art = ["Skala je Balken: 0..100 Simulationspunkte. 100 bedeutet Zielzustand erreicht.", ""]
        for m in METRICS:
            color = Palette.METRIC.get(m, Palette.WHITE) if self.cz.enabled else ""
            art.append("%s %6.2f %s  w=%.2f" % (pad(self.cz.metric(m, METRIC_SHORT[m]), 6), gm[m], block_bar(gm[m], 100.0, bw, color), WEIGHTS[m]))
        protected_avg = safe_mean([gm[m] for m in PROTECTED])
        prod_avg = safe_mean([gm[m] for m in ("material_output", "liquidity", "resource_resilience")])
        ev = "Geschützte Metriken liegen im Mittel bei %.2f; Produktions-/Liquiditätsmetriken bei %.2f." % (protected_avg, prod_avg)
        return self._section(
            "Globales Metrik-Dashboard",
            [(METRIC_SHORT[m], METRIC_EXPLANATION[m]) for m in METRICS] + [("w", "Gewicht der Metrik in der Gesamtbewertung."), ("0..100", "abstrakte Simulationspunkte; höher ist besser.")],
            art,
            [ev, "Hohe Werte bei AGY, SAFE, TRU, FAIR und CONS sind besonders relevant. OUT und LIQ sind absichtlich niedriger gewichtet, damit bloße Produktion oder Liquidität Schaden nicht moralisch überdecken kann."],
            Palette.BRIGHT_BLUE,
        )

    def regional_heatmap(self, econ):
        # Keep all metrics if possible; if terminal is narrow, show protected + economic core.
        if self.width >= 110:
            metrics = METRICS
        else:
            metrics = PROTECTED + ["repair_capacity", "resource_resilience", "material_output", "liquidity"]
        header = "Region  NI    " + " ".join([pad(self.cz.metric(m, METRIC_SHORT[m]), 5) for m in metrics])
        art = [header, "─" * min(self.width - 8, visible_len(Palette.strip(header)))]
        for r in sorted(econ.world.regions.values(), key=lambda x: x.id):
            row = [pad(r.id, 6), "%5.1f" % r.score()]
            for m in metrics:
                row.append(heat_cell(r.metrics[m], self.cz) + " ")
            art.append(" ".join(row))
        art.append("")
        art.append("Legende: " + self.cz.green("██ sehr gut") + "  " + self.cz.c("▓▓ gut", Palette.GREEN) + "  " + self.cz.yellow("▒▒ mittel") + "  " + self.cz.c("░░ schwach", Palette.YELLOW) + "  " + self.cz.red("!! kritisch"))
        weakest = min(econ.world.regions.values(), key=lambda r: r.score())
        strongest = max(econ.world.regions.values(), key=lambda r: r.score())
        return self._section(
            "Regionale Heatmap",
            [("Rxx", "Region mit zweistelliger Nummer."), ("NI", "regionaler Nobility Index."), ("██/▓▓/▒▒/░░/!!", "Heatmap-Zellen von sehr gut bis kritisch.")] + [(METRIC_SHORT[m], METRIC_EXPLANATION[m]) for m in metrics],
            art,
            ["Stärkste Region: %s mit NI %.2f. Schwächste Region: %s mit NI %.2f." % (strongest.id, strongest.score(), weakest.id, weakest.score()), "Die Heatmap zeigt, wohin Reparaturfonds, Interventionsrechte oder Bridge-Credits besonders sinnvoll fließen könnten."],
            Palette.BRIGHT_MAGENTA,
        )

    def operation_matrix(self, econ):
        rows = econ.operation_summary_rows()
        rows.sort(key=lambda r: r["accepted"] + r["rejected"], reverse=True)
        art = []
        art.append("Operation                    Unit   acc   rej     minted     ΔScore      pGain    protLoss")
        art.append("─" * min(self.width - 8, 94))
        for r in rows[:max(10, min(26, self.width // 4))]:
            unit = self.cz.unit(r["unit"], r["unit"])
            op = self.cz.red(r["operation"]) if r["harmful_family"] else self.cz.green(r["operation"])
            art.append("%s %s %5d %5d %10.2f %10.2f %10.2f %10.2f" % (pad(op, 28), pad(unit, 6), r["accepted"], r["rejected"], r["minted"], r["weighted_score"], r["private_gain"], r["protected_loss"]))
        harmful_acc = econ.harmful_accepted_count()
        ev = "Akzeptierte schädliche Operationen: %d." % harmful_acc
        if econ.mode == "gmoe" and harmful_acc == 0:
            ev += " Im GMOE-Modus blockieren Red-Lines diese Wurzelzahlungen."
        return self._section(
            "Operationsmatrix: Algebra der unären Operationen",
            [("Unit", "farbcodierte Währungs- oder Instrumentklasse."), ("acc", "accepted: akzeptierte Operationen."), ("rej", "rejected: abgelehnte Operationen."), ("minted", "geprägtes Geld aus akzeptierter positiver Metrikbewegung."), ("ΔScore", "gewichtete Summe der Metrikänderungen."), ("pGain", "privater Profitanreiz."), ("protLoss", "Verlust in geschützten Metriken."), ("Op", "Operationsfamilie f:Ω→Ω.")],
            art,
            [ev, "Diese Matrix trennt privaten Anreiz von gültiger Zustandsverbesserung. Genau hier sieht man den Unterschied zwischen Baseline-Geld und Operator-Metrik-Geld."],
            Palette.BRIGHT_RED if econ.mode == "baseline" else Palette.BRIGHT_GREEN,
        )

    def money_stack_diagram(self, econ):
        balances = econ.unit_balances()
        total = sum(balances.values()) or 1.0
        bw = self._bar_width(reserve=36, max_width=48)
        art = ["Jede Zeile zeigt Anteil einer Geld-/Instrumentklasse am Gesamtbestand.", ""]
        order = ["OMK", "TRUTH", "CAUSE", "NORM", "BEHAV", "HIER", "REPAIR", "GOV", "INS", "STOCK", "BRIDGE", "FIAT", "DEBT"]
        present = [u for u in order if balances.get(u, 0.0) > 0]
        for unit in present:
            amount = balances[unit]
            bar = block_bar(amount, total, bw, Palette.UNIT.get(unit, Palette.WHITE) if self.cz.enabled else "")
            art.append("%s %10.2f  %s  %5.1f%%" % (pad(self.cz.unit(unit, unit), 8), amount, bar, 100.0 * amount / total))
        if econ.mode == "gmoe" and econ.agents:
            richest = econ.top_agents_by_money(1)[0]
            art.append("")
            art.append("Größter Wallet-Stapel: %s" % self.cz.c(richest.name, Palette.BRIGHT_WHITE))
            by_unit = richest.wallet.by_unit()
            for unit, amt in sorted(by_unit.items(), key=lambda kv: kv[1], reverse=True):
                coin = self.cz.unit(unit, "◉")
                count = min(28, max(1, int(amt / max(0.1, richest.wallet.balance()) * 28)))
                art.append("  %s %s %.2f" % (pad(self.cz.unit(unit, unit), 8), coin * count, amt))
        present_abbrs = [(u, UNIT_EXPLANATION.get(u, u)) for u in present]
        if econ.mode == "gmoe":
            ev = "Der Geldbestand ist ein zählbarer Stapel von Herkunftsklassen. Ein OMK trägt intern Operation, Metrik, Beweisqualität und Kausalanteil."
        else:
            ev = "Die Baseline zeigt Fiatgeld als skalaren Bestand ohne interne moralische Herkunftsinformation."
        return self._section("Zählbarer Geldstapel nach Einheiten", present_abbrs + [("◉", "einzelne sichtbare Münz-/Stapelmarke im Wallet-Beispiel.")], art, [ev], Palette.BRIGHT_CYAN)

    def market_panorama(self, econ):
        rows = econ.market_summary_rows()
        rows.sort(key=lambda r: r["events"], reverse=True)
        max_events = max([r["events"] for r in rows] + [1])
        bw = self._bar_width(reserve=66, max_width=30, min_width=10)
        art = ["Markt                     Unit  Events Erfolg Fehler    Betrag   Aktivität", "─" * min(self.width - 8, 88)]
        for r in rows[:24]:
            unit = self.cz.unit(r["unit"], r["unit"])
            bar = block_bar(r["events"], max_events, bw, Palette.UNIT.get(r["unit"], Palette.WHITE) if self.cz.enabled else "")
            art.append("%s %s %6d %6d %6d %9.2f  %s" % (pad(r["market"], 24), pad(unit, 5), r["events"], r["success_events"], r["failed_events"], r["amount"], bar))
        busiest = rows[0]["market"] if rows else "none"
        present_units = sorted(set(r["unit"] for r in rows))
        return self._section(
            "Marktpanorama",
            [("Unit", "Instrumentklasse des Marktes."), ("Events", "Anzahl der Marktereignisse."), ("Erfolg", "erfolgreiche Ereignisse."), ("Fehler", "gescheiterte oder abgelehnte Ereignisse."), ("Betrag", "übertragene Geld-/OMK-Menge."), ("Aktivität", "Balken proportional zur Ereigniszahl.")] + [(u, UNIT_EXPLANATION.get(u, u)) for u in present_units],
            art,
            ["Aktivster Markt: %s." % busiest, "Das Panorama zeigt, ob die Ökonomie vor allem durch Güterhandel, Kredit, Zertifikate, Versicherungen oder regionale Bridge-Vorgänge bewegt wird."],
            Palette.BRIGHT_YELLOW,
        )

    def intent_analysis(self, econ):
        rows = econ.intent_summary_rows()
        art = ["Intent     Anzahl    ØGeld     ØRep    ØStake   ØgültigerΔ  Øschädl.Δ  RedLines", "─" * min(self.width - 8, 92)]
        for r in rows:
            intent = r["intent"]
            ci = Palette.BRIGHT_GREEN if intent == "noble" else (Palette.BRIGHT_YELLOW if intent == "neutral" else Palette.BRIGHT_RED)
            art.append("%s %7d %9.2f %8.2f %8.2f %11.2f %10.2f %8d" % (pad(self.cz.c(intent, ci), 10), r["count"], r["avg_money"], r["avg_reputation"], r["avg_stake"], r["avg_valid_contribution"], r["avg_harmful_contribution"], r["redline_violations"]))
        return self._section(
            "Akteursgruppen nach Absicht",
            [("Intent", "Absichtsgruppe: noble, neutral oder harmful."), ("Ø", "Durchschnitt."), ("Geld", "OMK-Stack oder Fiatbestand je nach Modus."), ("Rep", "Reputation."), ("Stake", "hinterlegte Haftungs-/Einsatzmittel."), ("gültigerΔ", "durchschnittlicher gültiger positiver Beitrag."), ("schädl.Δ", "durchschnittlich verursachter schädlicher Beitrag."), ("RedLines", "rote Linien / schwere Regelverletzungen.")],
            art,
            ["Diese Tabelle prüft, ob Geld und Reputation zu den Akteuren wandern, die gültige Beiträge liefern. In GMOE sollte Zahlungsfähigkeit stärker mit gültiger Transformationsfähigkeit korrelieren als mit bloßem Besitz."],
            Palette.BRIGHT_WHITE,
        )

    def contract_overview(self, econ):
        stats = [
            ("TRUTH", "Wahrheitszertifikate", len(econ.truth_claims), sum(1 for c in econ.truth_claims.values() if c.resolved), sum(c.payout for c in econ.truth_claims.values())),
            ("CAUSE", "Kausalitätszertifikate", len(econ.causal_claims), sum(1 for c in econ.causal_claims.values() if c.resolved), sum(c.payout for c in econ.causal_claims.values())),
            ("BEHAV", "Verhaltensverträge", len(econ.behavior_contracts), sum(1 for c in econ.behavior_contracts.values() if c.resolved), sum(c.payout for c in econ.behavior_contracts.values())),
            ("NORM", "Normdistanzverträge", len(econ.norm_contracts), sum(1 for c in econ.norm_contracts.values() if c.resolved), sum(c.payout for c in econ.norm_contracts.values())),
            ("DEBT", "Kreditverträge", len(econ.credit_contracts), sum(1 for c in econ.credit_contracts if c.fulfilled), 0.0),
            ("INS", "Versicherungen", len(econ.insurance_contracts), sum(1 for c in econ.insurance_contracts if not c.active), sum(c.paid_out for c in econ.insurance_contracts)),
            ("BRIDGE", "Interregionale Pakete", len(econ.pending_packets), sum(1 for p in econ.pending_packets if p.accepted is not None), sum(sum(c.amount for c in p.credits) for p in econ.pending_packets)),
        ]
        art = ["Instrument                  Unit  erstellt erledigt  Auszahlung/Betrag", "─" * min(self.width - 8, 84)]
        for unit, name, created, done, payout in stats:
            art.append("%s %s %8d %8d %16.2f" % (pad(name, 26), pad(self.cz.unit(unit, unit), 6), created, done, payout))
        present = [u for u, _, created, _, _ in stats if created > 0]
        return self._section(
            "Zertifikate, Verträge und Bridges",
            [("Unit", "Instrumentklasse."), ("erstellt", "Anzahl erzeugter Verträge/Zertifikate/Pakete."), ("erledigt", "Anzahl entschiedener oder abgewickelter Instrumente."), ("Auszahlung/Betrag", "Summe der Auszahlungen oder transportierten Beträge.")] + [(u, UNIT_EXPLANATION.get(u, u)) for u in present],
            art,
            ["Hier sieht man, welche komplexen Märkte aktiv waren: Wahrheit, Kausalität, Normdistanz, Verhalten, Kredit, Versicherung und galaktische Bridge-Pakete. Diese Märkte sind Spezialfälle der gleichen Operator-Metrik-Logik."],
            Palette.BRIGHT_MAGENTA,
        )

    def final_evaluation(self, econ, other=None):
        d = econ.diagnostics()
        art = []
        if econ.mode == "gmoe":
            if d["positive_cone_violations_among_accepted"] == 0 and d["harmful_accepted"] == 0:
                art.append(self.cz.green("✓ Maschinenprüfung: Alle akzeptierten GMOE-Wurzeltransaktionen lagen in K+."))
            else:
                art.append(self.cz.red("✗ Warnung: Es gab K+-Verletzungen oder akzeptierte schädliche Operationen."))
            art.append("GMOE-Aussage: akzeptierter Handel = geprüfte positive Operator-Metrik-Bewegung.")
        else:
            art.append(self.cz.yellow("Baseline-Aussage: Handel räumt durch privaten Profit; moralische Metrik ist nicht die Wurzelbedingung."))
        if other is not None:
            diff = econ.world.score() - other.world.score()
            art.append("Vergleich zu %s: NI-Differenz = %+.3f" % (other.mode, diff))
            art.append("Schädliche akzeptierte Ops: %s=%d, %s=%d" % (econ.mode, econ.harmful_accepted_count(), other.mode, other.harmful_accepted_count()))
        outcome = "positiv" if (econ.history and econ.history[-1]["score_end"] >= econ.history[0]["score_start"]) else "negativ oder schockbelastet"
        art.append("Szenarioausgang in diesem Lauf: %s." % outcome)
        art.append("Grenze: Das ist ein Simulationsmodell. Es demonstriert den postulierten Mechanismus, nicht die reale Welt ohne diese Regeln.")
        return self._section(
            "Ausführliche Schlussauswertung",
            [("K+", "positiver Kegel gültiger Verbesserungsrichtungen."), ("NI", "Nobility Index."), ("Ops", "Operationen."), ("GMOE", "galaktische metrische Operatorökonomie.")],
            art,
            ["Das Ergebnis ist jetzt szenarioabhängig: Schocks, Knappheit, Vertrauensbrüche und schädliche Akteure können die Gesamtentwicklung verändern. Der formale GMOE-Invariant bleibt aber: gültiges Wurzelgeld entsteht nur aus akzeptierter positiver Metrikbewegung."],
            Palette.BRIGHT_GREEN if econ.mode == "gmoe" else Palette.GRAY,
        )

    def render(self, econ, other=None):
        sections = [
            self.banner(),
            self.color_legend(),
            self.abbreviation_legend(),
            self.scenario_panel(econ),
            self.operator_diagram(econ),
            self.summary_table(econ, "Kernzahlen der Simulation"),
            self.score_sparkline(econ),
            self.metric_dashboard(econ),
            self.regional_heatmap(econ),
            self.operation_matrix(econ),
            self.money_stack_diagram(econ),
            self.market_panorama(econ),
            self.intent_analysis(econ),
            self.contract_overview(econ),
            self.final_evaluation(econ, other),
        ]
        return "\n\n".join(sections)


# ============================================================
# 8. Export-Hilfen
# ============================================================

def ensure_dir(path):
    if path and not os.path.exists(path):
        os.makedirs(path)


def write_csv(path, rows):
    ensure_dir(os.path.dirname(path))
    if not rows:
        with open(path, "w", newline="", encoding="utf-8") as f: f.write("")
        return
    keys = []
    seen = set()
    for r in rows:
        for k in r.keys():
            if k not in seen:
                keys.append(k); seen.add(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in rows: writer.writerow(r)


def write_text(path, text):
    ensure_dir(os.path.dirname(path))
    with open(path, "w", encoding="utf-8") as f: f.write(text)


# ============================================================
# 9. Vergleich und Monte Carlo
# ============================================================

def run_pair(args):
    gmoe = Economy("gmoe", args.agents, args.regions, args.seed, args.shock_rate, args.scenario)
    base = Economy("baseline", args.agents, args.regions, args.seed, args.shock_rate, args.scenario)
    gmoe.run(args.steps); base.run(args.steps)
    return gmoe, base


def comparison_summary_rows(gmoe, base):
    return [
        {"quantity": "final_nobility_gmoe", "value": gmoe.world.score()},
        {"quantity": "final_nobility_baseline", "value": base.world.score()},
        {"quantity": "difference_gmoe_minus_baseline", "value": gmoe.world.score() - base.world.score()},
        {"quantity": "harmful_accepted_gmoe", "value": gmoe.harmful_accepted_count()},
        {"quantity": "harmful_accepted_baseline", "value": base.harmful_accepted_count()},
        {"quantity": "positive_cone_violations_gmoe", "value": gmoe.positive_cone_violations_among_accepted()},
        {"quantity": "positive_cone_violations_baseline", "value": base.positive_cone_violations_among_accepted()},
        {"quantity": "cumulative_accepted_score_gmoe", "value": gmoe.cumulative_accepted_score()},
        {"quantity": "cumulative_accepted_score_baseline", "value": base.cumulative_accepted_score()},
    ]


def export_economy(econ, outdir, visualizer):
    econ.export_csv(outdir)
    ansi = visualizer.render(econ)
    plain = Palette.strip(ansi)
    write_text(os.path.join(outdir, "%s_visual_report_ansi.txt" % econ.mode), ansi)
    write_text(os.path.join(outdir, "%s_visual_report_plain.txt" % econ.mode), plain)


def export_comparison(gmoe, base, outdir, color=True, width=118):
    ensure_dir(outdir)
    cz = Colorizer(color)
    viz = VisualReport(cz, width)
    export_economy(gmoe, outdir, viz)
    export_economy(base, outdir, viz)
    write_csv(os.path.join(outdir, "comparison_summary.csv"), comparison_summary_rows(gmoe, base))
    combined_ansi = viz.render(gmoe, base) + "\n\n" + viz.render(base, gmoe)
    write_text(os.path.join(outdir, "comparison_visual_report_ansi.txt"), combined_ansi)
    write_text(os.path.join(outdir, "comparison_visual_report_plain.txt"), Palette.strip(combined_ansi))


def run_monte_carlo(args):
    ensure_dir(args.out)
    rows = []
    for i in range(args.monte_carlo):
        class LocalArgs: pass
        local = LocalArgs(); local.agents = args.agents; local.regions = args.regions; local.seed = args.seed + i; local.shock_rate = args.shock_rate; local.steps = args.steps; local.scenario = args.scenario
        gmoe, base = run_pair(local)
        rows.append({
            "run": i, "seed": args.seed + i,
            "gmoe_final_nobility": gmoe.world.score(), "baseline_final_nobility": base.world.score(),
            "difference": gmoe.world.score() - base.world.score(),
            "gmoe_harmful_accepted": gmoe.harmful_accepted_count(), "baseline_harmful_accepted": base.harmful_accepted_count(),
            "gmoe_positive_cone_violations": gmoe.positive_cone_violations_among_accepted(), "baseline_positive_cone_violations": base.positive_cone_violations_among_accepted(),
            "gmoe_cumulative_score": gmoe.cumulative_accepted_score(), "baseline_cumulative_score": base.cumulative_accepted_score(),
        })
    write_csv(os.path.join(args.out, "monte_carlo_summary.csv"), rows)
    diffs = [r["difference"] for r in rows]
    args.width = terminal_safe_width(getattr(args, "width", 0))
    cz = Colorizer(not args.no_color)
    lines = []
    lines.append(box("Monte-Carlo-Auswertung", [
        "Runs: %d" % args.monte_carlo,
        "Mittelwert NI-Differenz GMOE - Baseline: %+.4f" % safe_mean(diffs),
        "Standardabweichung der Differenz: %.4f" % safe_stdev(diffs),
        "Mittelwert GMOE-K+-Verletzungen: %.4f" % safe_mean([r["gmoe_positive_cone_violations"] for r in rows]),
        "Mittelwert Baseline akzeptierte schädliche Ops: %.4f" % safe_mean([r["baseline_harmful_accepted"] for r in rows]),
        "CSV: %s" % os.path.join(args.out, "monte_carlo_summary.csv"),
    ], cz, args.width, Palette.BRIGHT_MAGENTA))
    return "\n".join(lines)


# ============================================================
# 10. CLI
# ============================================================

def parse_args():
    p = argparse.ArgumentParser(description="GMOE enriched visual UTF-8 simulation")
    p.add_argument("--mode", choices=["gmoe", "baseline"], default="gmoe")
    p.add_argument("--steps", type=int, default=180)
    p.add_argument("--agents", type=int, default=60)
    p.add_argument("--regions", type=int, default=5)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--shock-rate", type=float, default=0.012)
    p.add_argument("--compare", action="store_true")
    p.add_argument("--out", default="gmoe_visual_output")
    p.add_argument("--no-export", action="store_true")
    p.add_argument("--no-color", action="store_true")
    p.add_argument("--width", type=int, default=0, help="Maximale Breite; standardmäßig Bildschirmbreite minus 5")
    p.add_argument("--scenario", choices=["auto"] + sorted(SCENARIOS.keys()), default="auto", help="Szenarioausgang: auto wählt per Seed zufällig ein Profil")
    p.add_argument("--monte-carlo", type=int, default=0)
    return p.parse_args()


def main():
    args = parse_args()
    if args.monte_carlo and args.monte_carlo > 0:
        print(run_monte_carlo(args))
        return
    args.width = terminal_safe_width(args.width)
    cz = Colorizer(not args.no_color)
    viz = VisualReport(cz, args.width)
    if args.compare:
        gmoe, base = run_pair(args)
        print(viz.render(gmoe, base))
        print("\n" + "═" * args.width + "\n")
        print(viz.render(base, gmoe))
        if not args.no_export:
            export_comparison(gmoe, base, args.out, not args.no_color, args.width)
            print("\n" + cz.green("Exportiert nach: %s" % args.out))
    else:
        econ = Economy(args.mode, args.agents, args.regions, args.seed, args.shock_rate, args.scenario)
        econ.run(args.steps)
        print(viz.render(econ))
        if not args.no_export:
            export_economy(econ, args.out, viz)
            print("\n" + cz.green("Exportiert nach: %s" % args.out))


if __name__ == "__main__":
    main()
