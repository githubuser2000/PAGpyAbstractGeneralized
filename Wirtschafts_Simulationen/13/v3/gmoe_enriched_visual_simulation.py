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
    if color is None:
        color = Palette.BRIGHT_CYAN
    top = "╔" + "═" * (width - 2) + "╗"
    mid_title = "║" + center(colorizer.c(" " + title + " ", color), width - 2) + "║"
    sep = "╠" + "═" * (width - 2) + "╣"
    bottom = "╚" + "═" * (width - 2) + "╝"
    out = [colorizer.c(top, color), mid_title, colorizer.c(sep, color)]
    for line in lines:
        raw = str(line)
        while visible_len(raw) > width - 4:
            # harte Umbrechung ohne intelligente Worttrennung.
            chunk = ""
            for ch in raw:
                if visible_len(chunk + ch) > width - 4:
                    break
                chunk += ch
            out.append(colorizer.c("║ ", color) + pad(chunk, width - 4) + colorizer.c(" ║", color))
            raw = raw[len(Palette.strip(chunk)):]
        out.append(colorizer.c("║ ", color) + pad(raw, width - 4) + colorizer.c(" ║", color))
    out.append(colorizer.c(bottom, color))
    return "\n".join(out)


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
    def __init__(self, mode, n_agents, n_regions, seed, shock_rate=0.012):
        assert mode in ("gmoe", "baseline")
        self.mode = mode
        self.seed = seed
        self.rng = random.Random(seed)
        self.shock_rate = shock_rate
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
                metrics[m] = clamp(base)
            rid = "R%02d" % i
            regions[rid] = Region(id=rid, name="Region_%02d" % i, metrics=metrics, latency=self.rng.randint(1, 6))
        for a in regions.values():
            for b in regions.values():
                a.trust[b.id] = 1.0 if a.id == b.id else self.rng.uniform(0.45, 0.90)
        return WorldState(regions=regions)

    def create_agents(self, n_agents):
        region_ids = list(self.world.regions.keys())
        roles = ["producer", "auditor", "healer", "engineer", "trader", "governor", "teacher", "insurer", "researcher"]
        for i in range(n_agents):
            if i < int(n_agents * 0.32):
                intent = "noble"
            elif i < int(n_agents * 0.76):
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
        self.width = width

    def banner(self):
        lines = [
            self.cz.c("   ██████╗ ███╗   ███╗ ██████╗ ███████╗    ", Palette.BRIGHT_CYAN) + self.cz.c("  METRIC OPERATOR ECONOMY", Palette.BRIGHT_GREEN),
            self.cz.c("  ██╔════╝ ████╗ ████║██╔═══██╗██╔════╝    ", Palette.BRIGHT_CYAN) + self.cz.c("  Geld = Operation + Metrik + Δ∈K+", Palette.BRIGHT_YELLOW),
            self.cz.c("  ██║  ███╗██╔████╔██║██║   ██║█████╗      ", Palette.BRIGHT_CYAN) + self.cz.c("  Galaktische Transformationsökonomie", Palette.BRIGHT_MAGENTA),
            self.cz.c("  ██║   ██║██║╚██╔╝██║██║   ██║██╔══╝      ", Palette.BRIGHT_CYAN) + self.cz.c("  UTF-8 Visual Report", Palette.BRIGHT_BLUE),
            self.cz.c("  ╚██████╔╝██║ ╚═╝ ██║╚██████╔╝███████╗    ", Palette.BRIGHT_CYAN) + self.cz.c("  f: Ω → Ω", Palette.BRIGHT_GREEN),
            self.cz.c("   ╚═════╝ ╚═╝     ╚═╝ ╚═════╝ ╚══════╝    ", Palette.BRIGHT_CYAN),
        ]
        return "\n".join(lines)

    def color_legend(self):
        lines = []
        for key in ["OMK", "FIAT", "TRUTH", "CAUSE", "NORM", "BEHAV", "HIER", "REPAIR", "GOV", "INS", "STOCK", "BRIDGE", "DEBT", "RISK", "REP", "K+"]:
            lines.append("%s  %s" % (pad(self.cz.unit(key, key), 12), UNIT_EXPLANATION[key]))
        expl = "Diese Legende fixiert die Farben. Jede Einheit behält in allen Diagrammen dieselbe Farbe, damit die Ausgabe lesbar bleibt."
        return box("Feste Farben für Währungen, Fonds und Instrumente", [expl, ""] + lines, self.cz, self.width, Palette.BRIGHT_CYAN)

    def abbreviation_legend(self):
        lines = [
            "Ω: gesamter Weltzustand. Eine unäre Operation ist f: Ω → Ω.",
            "Δ: gemessene Metrikänderung durch eine Operation. Positiv heißt: Abstand zum Ziel wurde kleiner.",
            "K+: positiver Kegel; Menge aller zulässigen Verbesserungsrichtungen im Metrikraum.",
            "NI: Nobility Index; gewichteter Durchschnitt aller Metriken auf Skala 0..100.",
            "DIST: gewichtete Distanz zum Zielzustand 100. Niedriger ist besser.",
            "Pq: Proof Quality; Qualität des Nachweises einer Wirkung, 0..1.",
            "Cs: Causal Share; kausal attribuierter Anteil einer Verbesserung, 0..1.",
            "Gini: Ungleichheitsmaß der Geldverteilung, 0 = gleich, 1 = extrem ungleich.",
            "Einheit der Metriken: abstrakte Simulationspunkte von 0 bis 100.",
            "Einheit des Geldes: skalarisierte OMK-Punkte = gewichtete, zertifizierte positive Metrikbewegung.",
        ]
        lines.append("")
        for m in METRICS:
            lines.append("%s %-6s  %s" % (self.cz.metric(m, METRIC_SHORT[m]), "(" + m + ")", METRIC_EXPLANATION[m]))
        return box("Kürzel, Einheiten und Metriken", lines, self.cz, self.width, Palette.BRIGHT_BLUE)

    def operator_diagram(self, econ):
        lines = []
        lines.append("Das folgende Bild zeigt die Buchungslogik der GMOE-Währung. Der Markt räumt nicht bloß private Zahlung, sondern prüft eine Zustandsoperation.")
        lines.append("")
        lines.append("        " + self.cz.c("ω_t", Palette.BRIGHT_WHITE) + "  " + self.cz.c("─" * 8, Palette.GRAY) + "  " + self.cz.unit("OMK", "f: Ω→Ω") + "  " + self.cz.c("─" * 8, Palette.GRAY) + "  " + self.cz.c("ω_{t+1}", Palette.BRIGHT_WHITE))
        lines.append("                    │")
        lines.append("                    ▼")
        lines.append("            " + self.cz.metric("truth", "Metrikvektor d⃗") + " misst:  Δ = d(ω_t,ω*) - d(f(ω_t),ω*)")
        lines.append("                    │")
        lines.append("                    ▼")
        lines.append("        " + self.cz.unit("K+", "Δ ∈ K+") + " ?  ── ja ──►  " + self.cz.unit("OMK", "OMK prägen") + "  ──►  Handel / Dividende / Kredit")
        lines.append("            │")
        lines.append("            nein")
        lines.append("            ▼")
        lines.append("        " + self.cz.unit("DEBT", "keine Wurzelzahlung: Ablehnung, Slashing, Haftung oder Reparaturpflicht"))
        lines.append("")
        lines.append("Warum das wichtig ist: Im GMOE-Modus kann akzeptiertes Wurzelgeld nur aus positiver Metrikbewegung entstehen. Dadurch wird Handel zur Komposition positiver unärer Operationen.")
        return box("Operator-Metrik-Zahlungsfluss", lines, self.cz, self.width, Palette.BRIGHT_MAGENTA)

    def summary_table(self, econ, title="Zusammenfassung"):
        d = econ.diagnostics()
        initial = econ.history[0]["score_start"] if econ.history else econ.world.score()
        final = econ.world.score()
        lines = []
        rows = [
            ("Modus", econ.mode),
            ("Seed", econ.seed),
            ("Schritte", econ.world.step),
            ("Agenten", len(econ.agents)),
            ("Regionen", len(econ.world.regions)),
            ("NI Start", "%.3f" % initial),
            ("NI Ende", "%.3f" % final),
            ("NI Änderung", "%+.3f" % (final - initial)),
            ("DIST Ende", "%.3f" % econ.world.distance()),
            ("akzeptierte Transaktionen", d["accepted_transactions"]),
            ("abgelehnte Transaktionen", d["rejected_transactions"]),
            ("akzeptierte schädliche Ops", d["harmful_accepted"]),
            ("K+-Verletzungen akzeptiert", d["positive_cone_violations_among_accepted"]),
            ("kumulativer Δ-Score", "%+.3f" % d["cumulative_accepted_weighted_score"]),
            ("Money-Gini", "%.3f" % d["money_gini"]),
            ("corr(Geld, Reputation)", "%.3f" % d["corr_money_reputation"]),
            ("corr(Geld, gültiger Beitrag)", "%.3f" % d["corr_money_valid_contribution"]),
        ]
        for k, v in rows:
            key = self.cz.c(k, Palette.BRIGHT_WHITE)
            val = str(v)
            if k == "K+-Verletzungen akzeptiert":
                val = self.cz.green(val) if int(v) == 0 else self.cz.red(val)
            if k == "akzeptierte schädliche Ops":
                val = self.cz.green(val) if int(v) == 0 else self.cz.red(val)
            lines.append("%s : %s" % (pad(key, 34), val))
        lines.append("")
        lines.append("Auswertung: NI ist die verdichtete Zielgröße. Entscheidend ist aber nicht nur NI, sondern ob akzeptierter Handel den K+-Test verletzt. Im GMOE-Modus soll dieser Wert 0 sein.")
        return box(title, lines, self.cz, self.width, Palette.BRIGHT_GREEN if econ.mode == "gmoe" else Palette.GRAY)

    def score_sparkline(self, econ):
        vals = [h["score_end"] for h in econ.history]
        dist = [h["distance_end"] for h in econ.history]
        lines = []
        lines.append("NI-Verlauf   : " + sparkline(vals, 76, self.cz) + "  min=%.2f max=%.2f" % (min(vals) if vals else 0, max(vals) if vals else 0))
        lines.append("DIST-Verlauf : " + self.cz.c(sparkline(dist, 76), Palette.BRIGHT_YELLOW) + "  min=%.2f max=%.2f" % (min(dist) if dist else 0, max(dist) if dist else 0))
        lines.append("")
        lines.append("Was dargestellt wird: Jede kleine Säule ist ein Simulationszeitpunkt. Höhere NI-Säulen bedeuten mehr Agency, Wahrheit, Fairness, Reparaturfähigkeit usw. Niedrigere DIST bedeutet geringerer Abstand zum Zielzustand.")
        lines.append("Warum es nützlich ist: Tabellen zeigen Endwerte; die Sparkline zeigt, ob die Verbesserung stetig, sprunghaft oder durch Schocks unterbrochen war.")
        return box("Zeitverlauf: Nobility Index und Distanz", lines, self.cz, self.width, Palette.BRIGHT_CYAN)

    def metric_dashboard(self, econ):
        gm = econ.world.global_metrics()
        lines = []
        lines.append("Jeder Balken hat Skala 0..100. Je voller der Balken, desto näher ist die Metrik am Zielzustand.")
        lines.append("")
        for m in METRICS:
            color = Palette.METRIC.get(m, Palette.WHITE) if self.cz.enabled else ""
            lines.append("%s %6.2f  %s  Gewicht %.2f" % (pad(self.cz.metric(m, METRIC_SHORT[m]), 8), gm[m], block_bar(gm[m], 100.0, 34, color), WEIGHTS[m]))
        lines.append("")
        lines.append("Auswertung: Hohe Werte bei AGY, SAFE, TRU, FAIR und CONS sind besonders wichtig, weil sie geschützte Metriken sind. OUT und LIQ sind bewusst niedriger gewichtet, damit bloße Produktion oder Liquidität Schaden nicht überdecken kann.")
        return box("Globales Metrik-Dashboard", lines, self.cz, self.width, Palette.BRIGHT_BLUE)

    def regional_heatmap(self, econ):
        lines = []
        header = "Region  NI     " + " ".join([pad(self.cz.metric(m, METRIC_SHORT[m]), 5) for m in METRICS])
        lines.append(header)
        lines.append("-" * min(self.width - 4, visible_len(Palette.strip(header))))
        for r in sorted(econ.world.regions.values(), key=lambda x: x.id):
            row = [pad(r.id, 6), "%5.1f" % r.score()]
            for m in METRICS:
                row.append(heat_cell(r.metrics[m], self.cz) + " ")
            lines.append(" ".join(row))
        lines.append("")
        lines.append("Legende: " + self.cz.green("██ sehr gut") + "  " + self.cz.c("▓▓ gut", Palette.GREEN) + "  " + self.cz.yellow("▒▒ mittel") + "  " + self.cz.red("░░ schwach") + "  " + self.cz.red("!! kritisch"))
        lines.append("Was dargestellt wird: Regionen sind lokale galaktische Wirtschaftszonen mit eigener Latenz, Ledgergröße und Metriklage. Die Heatmap zeigt, wo Reparaturfonds oder Interventionsrechte besonders wertvoll sind.")
        return box("Regionale Heatmap", lines, self.cz, self.width, Palette.BRIGHT_MAGENTA)

    def operation_matrix(self, econ):
        rows = econ.operation_summary_rows()
        rows.sort(key=lambda r: r["accepted"] + r["rejected"], reverse=True)
        lines = []
        lines.append("Operation                          Einheit   akzept.  abgel.   minted     ΔScore     pGain      Schutzverlust")
        lines.append("-" * 108)
        for r in rows[:22]:
            unit = self.cz.unit(r["unit"], r["unit"])
            op = r["operation"]
            if r["harmful_family"]:
                op = self.cz.red(op)
            else:
                op = self.cz.green(op)
            lines.append("%s %s %7d %7d %9.2f %10.2f %10.2f %13.2f" % (pad(op, 34), pad(unit, 8), r["accepted"], r["rejected"], r["minted"], r["weighted_score"], r["private_gain"], r["protected_loss"]))
        lines.append("")
        lines.append("Was dargestellt wird: Jede Zeile ist eine Operationsfamilie f: Ω→Ω. 'minted' ist geprägtes OMK-Geld. ΔScore ist gewichtete Metrikbewegung. pGain ist privater Profitanreiz. Schutzverlust misst negative Bewegung in geschützten Metriken.")
        lines.append("Warum es wichtig ist: Der Kernvergleich ist, ob private hohe pGain-Werte trotz Schutzverlusten akzeptiert werden. GMOE blockiert rote Linien; Baseline kann sie räumen.")
        return box("Operationsmatrix: Algebra der unären Operationen", lines, self.cz, self.width, Palette.BRIGHT_GREEN)

    def money_stack_diagram(self, econ):
        lines = []
        balances = econ.unit_balances()
        if not balances:
            lines.append("Keine Geldbestände.")
            return box("Geldstapel", lines, self.cz, self.width, Palette.BRIGHT_CYAN)
        total = sum(balances.values()) or 1.0
        lines.append("Jede Farbe ist eine andere Währungs-/Instrumentklasse. Die Länge zeigt den Anteil am Gesamtbestand.")
        lines.append("")
        for unit in ["OMK", "TRUTH", "CAUSE", "NORM", "BEHAV", "HIER", "REPAIR", "GOV", "INS", "STOCK", "BRIDGE", "FIAT", "DEBT"]:
            if unit not in balances or balances[unit] <= 0: continue
            amount = balances[unit]
            bar = block_bar(amount, total, 42, Palette.UNIT.get(unit, Palette.WHITE) if self.cz.enabled else "")
            lines.append("%s %10.2f  %s  %.1f%%" % (pad(self.cz.unit(unit, unit), 10), amount, bar, 100.0 * amount / total))
        lines.append("")
        if econ.mode == "gmoe":
            richest = econ.top_agents_by_money(1)[0]
            lines.append("Größter Wallet-Stapel: %s" % self.cz.c(richest.name, Palette.BRIGHT_WHITE))
            by_unit = richest.wallet.by_unit()
            for unit, amt in sorted(by_unit.items(), key=lambda kv: kv[1], reverse=True):
                coin = self.cz.unit(unit, "◉")
                count = min(30, max(1, int(amt / max(0.1, richest.wallet.balance()) * 30)))
                lines.append("  %s %s %.2f" % (pad(self.cz.unit(unit, unit), 8), coin * count, amt))
            lines.append("")
            lines.append("Interpretation: Das Wallet ist kein bloßer Kontostand. Es ist ein Stapel historischer positiver Transformationen mit Operation, Metrik, Beweisqualität und Kausalanteil.")
        else:
            lines.append("Interpretation: In der Baseline ist Geld ein skalares Fiatguthaben. Es trägt keine interne Information darüber, ob es durch Hilfe, Wahrheit oder Schaden entstand.")
        return box("Zählbarer Geldstapel nach Einheiten", lines, self.cz, self.width, Palette.BRIGHT_CYAN)

    def market_panorama(self, econ):
        rows = econ.market_summary_rows()
        rows.sort(key=lambda r: r["events"], reverse=True)
        lines = []
        lines.append("Markt                         Einheit  Events  Erfolg  Fehler   Betrag     Aktivität")
        lines.append("-" * 100)
        max_events = max([r["events"] for r in rows] + [1])
        for r in rows[:24]:
            unit = self.cz.unit(r["unit"], r["unit"])
            bar = block_bar(r["events"], max_events, 24, Palette.UNIT.get(r["unit"], Palette.WHITE) if self.cz.enabled else "")
            lines.append("%s %s %6d %7d %7d %9.2f  %s" % (pad(r["market"], 30), pad(unit, 8), r["events"], r["success_events"], r["failed_events"], r["amount"], bar))
        lines.append("")
        lines.append("Was dargestellt wird: Die Marktpanorama-Grafik macht sichtbar, welche Teilmärkte die meiste Transaktionsaktivität erzeugen: Güter, Wertpapiere, Wahrheit, Kausalität, Verhalten, Normen, Versicherungen, Bridge-Handel.")
        lines.append("Warum es wichtig ist: Ein Wirtschaftssystem ist nicht nur eine Metrikregel. Es braucht Liquidität, Kredit, Risiko, Wertpapiere, Versicherung und regionale Synchronisation.")
        return box("Marktpanorama", lines, self.cz, self.width, Palette.BRIGHT_YELLOW)

    def intent_analysis(self, econ):
        rows = econ.intent_summary_rows()
        lines = []
        lines.append("Intent     Anzahl   ØGeld     ØRep      ØStake   Øgültiger Δ   Øschädl. Δ   RedLines")
        lines.append("-" * 100)
        for r in rows:
            intent = r["intent"]
            ci = Palette.BRIGHT_GREEN if intent == "noble" else (Palette.BRIGHT_YELLOW if intent == "neutral" else Palette.BRIGHT_RED)
            lines.append("%s %7d %9.2f %9.2f %9.2f %12.2f %12.2f %9d" % (pad(self.cz.c(intent, ci), 10), r["count"], r["avg_money"], r["avg_reputation"], r["avg_stake"], r["avg_valid_contribution"], r["avg_harmful_contribution"], r["redline_violations"]))
        lines.append("")
        lines.append("Auswertung: Diese Tabelle fragt, ob sich Geld und Reputation in Richtung gültiger Beiträge verschieben. Im GMOE-Modus sollten noble und neutrale Akteure durch echte Verbesserung Zahlungsfähigkeit erzeugen können; schädliche Akteure werden durch rote Linien gebremst.")
        return box("Akteursgruppen nach Absicht", lines, self.cz, self.width, Palette.BRIGHT_WHITE)

    def contract_overview(self, econ):
        lines = []
        stats = [
            ("TRUTH", "Wahrheitszertifikate", len(econ.truth_claims), sum(1 for c in econ.truth_claims.values() if c.resolved), sum(c.payout for c in econ.truth_claims.values())),
            ("CAUSE", "Kausalitätszertifikate", len(econ.causal_claims), sum(1 for c in econ.causal_claims.values() if c.resolved), sum(c.payout for c in econ.causal_claims.values())),
            ("BEHAV", "Verhaltensverträge", len(econ.behavior_contracts), sum(1 for c in econ.behavior_contracts.values() if c.resolved), sum(c.payout for c in econ.behavior_contracts.values())),
            ("NORM", "Normdistanzverträge", len(econ.norm_contracts), sum(1 for c in econ.norm_contracts.values() if c.resolved), sum(c.payout for c in econ.norm_contracts.values())),
            ("DEBT", "Kreditverträge", len(econ.credit_contracts), sum(1 for c in econ.credit_contracts if c.fulfilled), 0.0),
            ("INS", "Versicherungen", len(econ.insurance_contracts), sum(1 for c in econ.insurance_contracts if not c.active), sum(c.paid_out for c in econ.insurance_contracts)),
            ("BRIDGE", "Interregionale Pakete", len(econ.pending_packets), sum(1 for p in econ.pending_packets if p.accepted is not None), sum(sum(c.amount for c in p.credits) for p in econ.pending_packets)),
        ]
        lines.append("Instrument                    Einheit   erstellt  erledigt   Auszahlung/Betrag")
        lines.append("-" * 90)
        for unit, name, created, done, payout in stats:
            lines.append("%s %s %8d %8d %16.2f" % (pad(name, 30), pad(self.cz.unit(unit, unit), 8), created, done, payout))
        lines.append("")
        lines.append("Was dargestellt wird: Diese Übersicht zeigt die nichttrivialen Marktinstrumente jenseits einfachen Kaufs: Wahrheit, Kausalität, Normdistanz, Verhalten, Kredit, Versicherung und Galaxie-Bridges.")
        lines.append("Warum es wichtig ist: Die Theorie behauptet, dass diese Instrumente alle Spezialfälle derselben Grundstruktur sind: zustandsabhängige Operationen mit Metrik und Beweis.")
        return box("Zertifikate, Verträge und Bridges", lines, self.cz, self.width, Palette.BRIGHT_MAGENTA)

    def final_evaluation(self, econ, other=None):
        d = econ.diagnostics()
        lines = []
        if econ.mode == "gmoe":
            if d["positive_cone_violations_among_accepted"] == 0 and d["harmful_accepted"] == 0:
                lines.append(self.cz.green("Maschinenprüfung bestanden: Alle akzeptierten GMOE-Wurzeltransaktionen lagen im positiven Kegel K+."))
            else:
                lines.append(self.cz.red("Warnung: Es gab K+-Verletzungen oder akzeptierte schädliche Operationen. Parameter oder Validierungslogik prüfen."))
            lines.append("Damit zeigt die Simulation den postulierten Automatismus im Modell: Wenn Geld nur aus gültiger positiver Zustandsbewegung entsteht, dann ist akzeptierter Handel selbst eine Kette positiver Operatoren.")
        else:
            lines.append("Baseline-Auswertung: Hier räumt privater Profit. Ein akzeptierter Handel kann also auch negative Metrikbewegung besitzen, solange er privat rentabel ist.")
        if other is not None:
            diff = econ.world.score() - other.world.score()
            lines.append("")
            lines.append("Vergleich zu %s: NI-Differenz = %+.3f" % (other.mode, diff))
            lines.append("Akzeptierte schädliche Operationen: %s=%d, %s=%d" % (econ.mode, econ.harmful_accepted_count(), other.mode, other.harmful_accepted_count()))
        lines.append("")
        lines.append("Grenze der Aussage: Das Skript beweist nicht, dass reale Märkte automatisch edel sind. Es demonstriert, dass der postulierte Mechanismus diese Richtung erzwingt, sobald 'Zahlung' definitionsgemäß eine auditierte positive Operator-Metrik-Kontraktion ist.")
        return box("Ausführliche Schlussauswertung", lines, self.cz, self.width, Palette.BRIGHT_GREEN if econ.mode == "gmoe" else Palette.GRAY)

    def render(self, econ, other=None):
        sections = [
            self.banner(),
            self.color_legend(),
            self.abbreviation_legend(),
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
    gmoe = Economy("gmoe", args.agents, args.regions, args.seed, args.shock_rate)
    base = Economy("baseline", args.agents, args.regions, args.seed, args.shock_rate)
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
        local = LocalArgs(); local.agents = args.agents; local.regions = args.regions; local.seed = args.seed + i; local.shock_rate = args.shock_rate; local.steps = args.steps
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
    cz = Colorizer(not args.no_color)
    lines = []
    lines.append(box("Monte-Carlo-Auswertung", [
        "Runs: %d" % args.monte_carlo,
        "Mittelwert NI-Differenz GMOE - Baseline: %+.4f" % safe_mean(diffs),
        "Standardabweichung der Differenz: %.4f" % safe_stdev(diffs),
        "Mittelwert GMOE-K+-Verletzungen: %.4f" % safe_mean([r["gmoe_positive_cone_violations"] for r in rows]),
        "Mittelwert Baseline akzeptierte schädliche Ops: %.4f" % safe_mean([r["baseline_harmful_accepted"] for r in rows]),
        "CSV: %s" % os.path.join(args.out, "monte_carlo_summary.csv"),
    ], cz, 110, Palette.BRIGHT_MAGENTA))
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
    p.add_argument("--width", type=int, default=118)
    p.add_argument("--monte-carlo", type=int, default=0)
    return p.parse_args()


def main():
    args = parse_args()
    if args.monte_carlo and args.monte_carlo > 0:
        print(run_monte_carlo(args))
        return
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
        econ = Economy(args.mode, args.agents, args.regions, args.seed, args.shock_rate)
        econ.run(args.steps)
        print(viz.render(econ))
        if not args.no_export:
            export_economy(econ, args.out, viz)
            print("\n" + cz.green("Exportiert nach: %s" % args.out))


if __name__ == "__main__":
    main()
