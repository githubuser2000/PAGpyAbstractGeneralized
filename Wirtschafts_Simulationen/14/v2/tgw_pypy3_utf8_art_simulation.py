#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
TGW UTF-8 Art Simulation Frontend
=================================

PyPy3-compatible, stdlib-only rich reporting layer for the TGW simulation.
It keeps the original simulation engine unchanged and adds extensive UTF-8
art, diagrams, legends and outcome analysis.

Run:
    pypy3 tgw_pypy3_utf8_art_simulation.py --ticks 180 --seed 42 --report-out report.txt

Scenario suite:
    pypy3 tgw_pypy3_utf8_art_simulation.py --scenario-suite --ticks 120 --suite-out suite.md --quiet

This file expects tgw_pypy3_simulation.py to be in the same directory.
"""
from __future__ import print_function

import argparse
import copy
import os
import sys
import textwrap
from collections import Counter, defaultdict
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

try:
    import tgw_pypy3_simulation as core
except ImportError as exc:  # pragma: no cover - user-facing fallback
    sys.stderr.write("Fehler: tgw_pypy3_simulation.py muss im selben Ordner liegen.\n")
    raise exc


SPARKS = "▁▂▃▄▅▆▇█"
HEAT = "·░▒▓█"
BAR_FULL = "█"
BAR_EMPTY = "░"
THIN = "─"

TAG_ABBR = {
    "energy": "ENE",
    "water": "WAT",
    "food": "FOD",
    "health": "HLT",
    "housing": "HOU",
    "infrastructure": "INF",
    "environment": "ENV",
    "security": "SEC",
    "governance": "GOV",
    "finance": "FIN",
    "labor": "LAB",
    "education": "EDU",
    "logistics": "LOG",
    "communication": "COM",
    "research": "RES",
    "industry": "IND",
    "law": "LAW",
    "diplomacy": "DIP",
    "culture": "CUL",
    "transport": "TRN",
}

KIND_ICON = {
    "household": "🏠",
    "firm": "🏭",
    "bank": "🏦",
    "state": "🏛",
    "repair_fund": "🛠",
    "auditor": "🧪",
    "clearinghouse": "⚖",
    "escrow": "🧊",
}

SCENARIO_NAMES = {
    "baseline": "Baseline / Normalwirtschaft",
    "conflict": "Konfliktökonomie",
    "fraud": "Betrugsdruck",
    "intergalactic": "Intergalaktische Verzögerung",
    "scarcity": "Knappheit und viele Startprobleme",
}


def fmt_lz(x: float) -> str:
    if abs(x) < 1e-9:
        x = 0.0
    return core.fmt_lz(x)


def fmt_num(x: float) -> str:
    ax = abs(x)
    if ax >= 1_000_000_000:
        return "%.2fB" % (x / 1_000_000_000.0)
    if ax >= 1_000_000:
        return "%.2fM" % (x / 1_000_000.0)
    if ax >= 1_000:
        return "%.2fk" % (x / 1_000.0)
    if abs(x - int(x)) < 1e-9:
        return str(int(x))
    return "%.2f" % x


def pct(x: float) -> str:
    return "%.1f%%" % (100.0 * x)


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if abs(b) < 1e-9:
        return default
    return a / b


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def clean_name(name: str, n: int = 28) -> str:
    name = str(name).replace("\n", " ")
    if len(name) <= n:
        return name
    return name[: max(1, n - 1)] + "…"


def section(title: str, glyph: str = "✦") -> str:
    bar = "═" * min(86, max(20, len(title) + 8))
    return "\n╔%s╗\n║ %s %s ║\n╚%s╝" % (bar, glyph, title, bar)


def mini_heading(title: str) -> str:
    return "\n%s %s\n%s" % ("◆", title, "─" * min(88, max(10, len(title) + 4)))


def wrap_block(text: str, width: int = 100, prefix: str = "") -> str:
    text = textwrap.dedent(text).strip()
    if not text:
        return ""
    paras = text.split("\n")
    out: List[str] = []
    for para in paras:
        para = para.strip()
        if not para:
            out.append("")
        else:
            out.extend(textwrap.wrap(para, width=width, initial_indent=prefix, subsequent_indent=prefix))
    return "\n".join(out)


def abbreviations(items: Sequence[Tuple[str, str]]) -> str:
    lines = ["🔤 Abkürzungen dieser UTF‑8‑Art:"]
    for key, value in items:
        lines.append("  %-7s = %s" % (key, value))
    return "\n".join(lines)


def bar(value: float, max_value: float, width: int = 28, fill: str = BAR_FULL, empty: str = BAR_EMPTY) -> str:
    if max_value <= 1e-9:
        return empty * width
    frac = clamp(abs(value) / max_value, 0.0, 1.0)
    n = int(round(frac * width))
    return fill * n + empty * (width - n)


def meter(value: float, max_value: float, width: int = 32) -> str:
    return bar(value, max_value, width=width, fill="▓", empty="░")


def heat_symbol(value: float, max_value: float) -> str:
    if max_value <= 1e-9 or value <= 1e-9:
        return HEAT[0]
    idx = int(round(clamp(value / max_value, 0.0, 1.0) * (len(HEAT) - 1)))
    return HEAT[idx]


def sparkline(values: Sequence[float], width: int = 70) -> str:
    vals = list(values)
    if not vals:
        return "∅"
    if len(vals) > width:
        # Deterministic down-sampling by index; enough for console diagnostics.
        step = (len(vals) - 1) / float(width - 1)
        vals = [vals[int(round(i * step))] for i in range(width)]
    lo = min(vals)
    hi = max(vals)
    if abs(hi - lo) < 1e-9:
        return SPARKS[0] * len(vals)
    out = []
    for v in vals:
        idx = int(round((v - lo) / (hi - lo) * (len(SPARKS) - 1)))
        out.append(SPARKS[idx])
    return "".join(out)


def severity_by_cell(sim: core.Simulation) -> Dict[Tuple[int, int, int], float]:
    d: Dict[Tuple[int, int, int], float] = defaultdict(float)
    for pid in sim.open_problem_ids:
        p = sim.problems[pid]
        if p.status != "resolved":
            d[p.location.cell()] += p.severity
    return d


def severity_by_tag(sim: core.Simulation) -> Dict[str, float]:
    d: Dict[str, float] = defaultdict(float)
    for pid in sim.open_problem_ids:
        p = sim.problems[pid]
        if p.status != "resolved":
            for tag in p.domain.tags:
                d[tag] += p.severity / max(1, len(p.domain.tags))
    return d


def count_by_tag(sim: core.Simulation) -> Dict[str, int]:
    d: Dict[str, int] = defaultdict(int)
    for pid in sim.open_problem_ids:
        p = sim.problems[pid]
        if p.status != "resolved":
            for tag in p.domain.tags:
                d[tag] += 1
    return d


def latest(sim: core.Simulation) -> Dict[str, Any]:
    return sim.metrics[-1]


def metric_series(sim: core.Simulation, key: str) -> List[float]:
    return [float(m.get(key, 0.0)) for m in sim.metrics]


def actor_kind_summary(sim: core.Simulation) -> List[Tuple[str, int, float, int]]:
    counts: Dict[str, int] = defaultdict(int)
    balances: Dict[str, float] = defaultdict(float)
    negatives: Dict[str, int] = defaultdict(int)
    for a in sim.actors.values():
        counts[a.kind] += 1
        balances[a.kind] += a.balance
        if a.balance < 0:
            negatives[a.kind] += 1
    rows = []
    for kind in sorted(counts.keys()):
        rows.append((kind, counts[kind], balances[kind], negatives[kind]))
    return rows


def outcome_label(sim: core.Simulation) -> Tuple[str, str]:
    m = latest(sim)
    solved = float(m["cumulative_solved_value"])
    damage = float(m["cumulative_damage_value"])
    open_sev = float(m["open_problem_severity"])
    repair_ratio = safe_div(solved, damage, 0.0)
    backlog_ratio = safe_div(open_sev, damage, 0.0)
    fraud_ratio = safe_div(float(m["cumulative_fraud_penalty"]), max(1.0, solved), 0.0)
    tension = float(m["max_tension"])
    war = int(m["war_events"])
    unemployment_ratio = safe_div(float(m["unemployment"]), max(1.0, len(sim.households)), 0.0)
    if war > 0 or tension > 2.45:
        return ("🔴 Konfliktlastiger Ausgang", "Konflikt- und Sicherheitsprobleme dominieren; LZ wird stark in Reparatur und Schadensausgleich gebunden.")
    if fraud_ratio > 0.12:
        return ("🟠 Audit-/Betrugsstress", "Viele behauptete Lösungen werden korrigiert; die inverse Gruppenbuchung arbeitet, aber Vertrauen und Effizienz leiden.")
    if backlog_ratio > 0.55 and repair_ratio < 0.65:
        return ("🟡 Reparaturrückstand", "Die Wirtschaft löst Probleme, aber neue oder wachsende Probleme laufen schneller auf als die Solver-Kapazität.")
    if tension > 1.65:
        return ("🟡 Kaltkonflikt-Druck", "Es gibt keine dominierende heiße Eskalation, aber hohe Spannungen erzeugen Sicherheits-, Vertrauens- und Governance-Kosten.")
    if unemployment_ratio > 0.18:
        return ("🟡 Arbeitsmarkt-Reibung", "Es existieren offene Probleme, aber Arbeitskraft und Problemlösungsmärkte finden nicht ausreichend gut zusammen.")
    if repair_ratio >= 0.75 and backlog_ratio < 0.45:
        return ("🟢 Stabiler Lösungsaufbau", "Die Solver-Kapazität hält mit Schäden und öffentlichen Problemen mit; das System wird tendenziell stabiler.")
    return ("🟦 Gemischter Übergangszustand", "Kein einzelner Stressor dominiert; das Ergebnis hängt von Kredit, Audit, Topologie-Fit und Konfliktdynamik zugleich ab.")


def build_intro(sim: core.Simulation) -> str:
    m = latest(sim)
    label, label_text = outcome_label(sim)
    return "\n".join([
        section("TGW UTF‑8 Wirtschaftsbericht", "🌌"),
        wrap_block("""
        Dieser Bericht wertet eine Simulation der Topologischen Gruppenwirtschaft aus. Es gibt genau eine Währung: LZ, die Lösungszahl.
        LZ ist eine additive Gruppen-Zahl: Konten können positiv und negativ sein, Zahlungen sind Subtraktion bei einem Akteur und Addition
        bei einem anderen Akteur. Die Topologie bestimmt, ob Problemräume, Märkte, Assets, Staaten und Lösungen zueinander passen.

        Simuliert werden Haushalte/Arbeitnehmer, Unternehmen/Arbeitgeber, Banken, Staaten/Länder, Reparaturfonds, Auditoren, Märkte,
        Kredite, Steuern, öffentliche Probleme, externe Schäden, Betrug, Audits, kalte und heiße Konflikte sowie intergalaktische Escrows
        mit Verzögerung. Es gibt keine zweite Währung. Auch Kredit, Escrow, Steuern, Löhne, Strafen und Problemlösungen werden ausschließlich
        in LZ gebucht.
        """),
        "",
        "📌 Kurzdiagnose: %s" % label,
        "   %s" % label_text,
        "",
        "Szenario: %s | Seed: %s | Ticks: %d | Akteure: %d | Galaxien: %d" % (
            SCENARIO_NAMES.get(sim.config.scenario, sim.config.scenario), sim.config.seed, sim.tick, len(sim.actors), sim.config.galaxies
        ),
        "Gesamtbilanz Σ aller Konten: %.9f LZ | offene Problemschwere: %s | gelöster Wert: %s" % (
            float(m["total_balance"]), fmt_lz(-float(m["open_problem_severity"])), fmt_lz(float(m["cumulative_solved_value"]))
        ),
    ])


def art_math_core(sim: core.Simulation) -> str:
    art = r"""
        ┌──────────────────────┐                         ┌──────────────────────┐
        │  Topologie τ auf X   │                         │  Gruppe G=(ℝ,+,0,-) │
        │  offene Menge U∈τ   │                         │  Gruppenwert g∈G    │
        └──────────┬───────────┘                         └──────────┬───────────┘
                   │                                                │
                   └─────────────── Stack-Schicht (U,g) ────────────┘
                                           │
                              ┌────────────▼────────────┐
                              │ Stack S=((U₁,g₁),...)   │
                              │ Z(S)=Σgᵢ                │
                              │ D(S)=U₁∩U₂∩...          │
                              └────────────┬────────────┘
                                           │
                 Fusion: S⊕T  ⇒  Z(S⊕T)=Z(S)+Z(T),  D(S⊕T)=D(S)∩D(T)
    """.strip("\n")
    explanation = wrap_block("""
    Diese Grafik zeigt den mathematischen Kern: Eine Währungseinheit ist nicht nur ein nackter Kontowert, sondern ein Stack aus
    topologischem Kontext und additivem Gruppenwert. Die Gruppe macht positive und negative LZ möglich. Die Topologie entscheidet,
    ob zwei Lösungen, Assets oder Problemräume sinnvoll zusammenpassen.
    """)
    analysis = wrap_block("""
    Auswertung: In dieser Simulation blieb die Summe aller Konten nahe Null, weil jede LZ-Bewegung als Gruppenoperation gebucht wird.
    Neue positive Zahlungsfähigkeit entsteht immer mit einer Gegenposition: Schuld, Problemfonds, Kredit, Reparaturpflicht oder
    formalisierter Schaden. Dadurch wird die Ökonomie rechnerisch konservativ, aber nicht wertneutral: Wer Probleme erzeugt, wird negativ.
    """)
    return "\n".join([
        section("UTF‑8 Art 1: Mathematischer Stack-Kern", "🧮"),
        abbreviations([
            ("τ", "Topologie: Struktur der offenen Problem- und Lösungsbereiche"),
            ("X", "Problemraum, auf dem die Topologie liegt"),
            ("U∈τ", "offene Menge; Kontext, in dem eine Lösung oder ein Problem gilt"),
            ("G", "additive Gruppe der LZ-Werte; hier ℝ mit +, 0 und Inversen"),
            ("g", "ein konkreter Gruppenwert in LZ"),
            ("S,T", "Stacks aus mehreren Schichten (U,g)"),
            ("Z(S)", "Zahlenwert des Stacks: Summe aller gᵢ"),
            ("D(S)", "Anwendungsbereich des Stacks: Schnitt der offenen Mengen"),
            ("⊕", "Fusion/Kombination von Stacks"),
        ]),
        "",
        explanation,
        "\n" + art,
        "",
        analysis,
    ])


def art_actor_market_flow(sim: core.Simulation) -> str:
    c = sim.ledger.kind_counter
    def n(k: str) -> int:
        return int(c.get(k, 0))
    art = """
      🏦 Banken ── Kredit[%5d] ──▶ 🏭 Unternehmen ── Lohn[%5d] ──▶ 🏠 Haushalte
          ▲                            │  ▲                              │
          │                            │  │ Konsum[%5d]                  │
          │ Kreditrückzahlung[%5d]     │  └───────────────◀──────────────┘
          │                            │
      🧪 Auditoren ◀─ Auditgebühr[%5d] │
          │                            ▼
          └─ Korrektur/Strafe[%5d] ◀ 🛠 Reparaturfonds ◀─ Problem[%5d] ── 🏭/🏛/Akteure
                                      │
                                      └─ Projektzahlung[%5d] ──▶ 🏭 Solver

      🏛 Staaten ◀─ Steuern[%5d] ── 🏠/🏭/🏦        🧊 Escrow: Lock[%5d] → Release[%5d]
    """ % (
        n("loan_disbursement"), n("wage"), n("consumption"), n("loan_repayment"), n("audit_fee"),
        n("fraud_or_underperformance_penalty"), n("problem_formalized") + n("problem_growth"),
        n("project_payment") + n("escrow_release"), n("tax"), n("escrow_lock"), n("escrow_release")
    )
    explanation = wrap_block("""
    Diese Grafik zeigt die wichtigsten Marktflüsse der Simulation. Haushalte arbeiten für Unternehmen, Unternehmen zahlen Löhne,
    Haushalte konsumieren, Staaten erheben Steuern, Banken vergeben Kredite, Reparaturfonds finanzieren Problemlösungen und Auditoren
    korrigieren falsche oder unterperformende Lösungen. Alle Pfeile sind LZ-Bewegungen; es gibt keine zweite Währung.
    """)
    analysis_bits = []
    if n("problem_formalized") + n("problem_growth") > n("project_payment") + n("escrow_release"):
        analysis_bits.append("Es wurden mehr Problem-/Wachstumsbuchungen als Projektzahlungen gezählt; das spricht für hohen Reparaturdruck.")
    else:
        analysis_bits.append("Projektzahlungen halten in der Transaktionsanzahl mit Problemformalisierungen mit; die Reparaturökonomie ist aktiv.")
    if n("fraud_or_underperformance_penalty") > 0:
        analysis_bits.append("Audit-Korrekturen traten auf; inverse Buchungen sind also nicht nur Theorie, sondern Teil des Laufs.")
    if n("loan_disbursement") > n("loan_repayment") * 2 + 5:
        analysis_bits.append("Kreditvergabe überwiegt deutlich gegenüber Rückzahlung; das kann Wachstumsfinanzierung oder Kreditstress bedeuten.")
    analysis = wrap_block("Auswertung: " + " ".join(analysis_bits))
    return "\n".join([
        section("UTF‑8 Art 2: Markt- und Zahlungsfluss", "🔁"),
        abbreviations([
            ("🏠", "Haushalte/Arbeitnehmer"),
            ("🏭", "Unternehmen/Arbeitgeber/Solver"),
            ("🏦", "Banken, Kreditgeber und Kontoführer"),
            ("🏛", "Staaten/Länder/öffentliche Haushalte"),
            ("🛠", "Reparaturfonds; finanziert die Reduktion negativer Problemstacks"),
            ("🧪", "Auditoren/Prüfer"),
            ("🧊", "Escrow; gesperrte LZ für verzögerte/remote Projekte"),
            ("[n]", "Anzahl der Transaktionen dieser Art im bisherigen Lauf"),
        ]),
        "",
        explanation,
        art.rstrip(),
        "",
        analysis,
    ])


def art_galaxy_map(sim: core.Simulation) -> str:
    sev = severity_by_cell(sim)
    max_sev = max(sev.values()) if sev else 0.0
    lines: List[str] = []
    for g in range(sim.config.galaxies):
        lines.append("🌌 G%-2d " % g + "═" * 72)
        for p in range(sim.config.planets_per_galaxy):
            parts = []
            for s in range(sim.config.states_per_planet):
                cell = (g, p, s)
                symbol = heat_symbol(sev.get(cell, 0.0), max_sev)
                parts.append("S%d%s %s" % (s, symbol, fmt_num(-sev.get(cell, 0.0))))
            lines.append("   🪐 P%-2d │ %s" % (p, "  │  ".join(parts)))
    explanation = wrap_block("""
    Diese Karte zeigt keine echte Astronomie, sondern die topologisch-wirtschaftlichen Kausalzellen der Simulation: Galaxie, Planet,
    Staat/Land. Je dunkler das UTF‑8-Feld, desto größer ist die noch offene negative Problemschwere in dieser Zelle.
    """)
    open_total = sum(sev.values())
    heavy_cells = sorted(sev.items(), key=lambda kv: kv[1], reverse=True)[:3]
    if heavy_cells:
        heavy_text = "; ".join(["G%d:P%d:S%d=%s" % (c[0], c[1], c[2], fmt_lz(-v)) for c, v in heavy_cells])
    else:
        heavy_text = "keine offenen Problemschwerpunkte"
    analysis = wrap_block("""
    Auswertung: Die gesamte offene Problemschwere über alle Kausalzellen beträgt %s. Die größten Schwerpunkte liegen bei: %s.
    Das ist wichtig, weil Solver, Banken und Staaten lokal final handeln können, während intergalaktische Synchronisierung verzögert ist.
    """ % (fmt_lz(-open_total), heavy_text))
    return "\n".join([
        section("UTF‑8 Art 3: Intergalaktische Kausalzellen-Karte", "🗺"),
        abbreviations([
            ("G", "Galaxie"),
            ("P", "Planet innerhalb einer Galaxie"),
            ("S", "Staat/Land/öffentliche Kausalzelle auf einem Planet"),
            ("·░▒▓█", "Heat-Skala für offene Problemschwere; · niedrig, █ sehr hoch"),
            ("LZ", "Lösungszahl; negative Anzeige bedeutet offener Problemwert"),
        ]),
        "",
        explanation,
        "\n".join(lines),
        "",
        analysis,
    ])


def art_balance_skyline(sim: core.Simulation) -> str:
    actors = list(sim.actors.values())
    positives = sorted(actors, key=lambda a: a.balance, reverse=True)[:8]
    negatives = sorted(actors, key=lambda a: a.balance)[:8]
    max_abs = max([abs(a.balance) for a in positives + negatives] + [1.0])
    lines = ["🟢 Positive Konten / Lösungsansprüche"]
    for a in positives:
        icon = KIND_ICON.get(a.kind, "•")
        lines.append("  %s %-29s %12s │%s│ rep=%7.2f" % (icon, clean_name(a.name, 29), fmt_lz(a.balance), bar(a.balance, max_abs, 30, "█", "░"), a.reputation))
    lines.append("")
    lines.append("🔴 Negative Konten / Verpflichtungen, Schäden oder Schulden")
    for a in negatives:
        icon = KIND_ICON.get(a.kind, "•")
        lines.append("  %s %-29s %12s │%s│ rep=%7.2f" % (icon, clean_name(a.name, 29), fmt_lz(a.balance), bar(a.balance, max_abs, 30, "█", "░"), a.reputation))
    explanation = wrap_block("""
    Diese Grafik zeigt die stärksten positiven und negativen Akteure. Positive LZ sind Ansprüche oder erwirtschafteter Lösungswert.
    Negative LZ sind offene Verpflichtungen, Kreditlasten, verursachte Probleme, öffentliche Ausgaben oder Korrekturen. Ein negativer
    Stand ist kein Menschenwert-Urteil, sondern eine ökonomische Bilanzposition.
    """)
    neg_count = latest(sim)["negative_actors"]
    analysis = wrap_block("""
    Auswertung: %d von %d Akteuren sind negativ. Entscheidend ist nicht, dass Negativität existiert — Kredite und Reparaturpflichten
    sind normal — sondern ob negative Positionen durch echte Problemlösung, Steuern, Rückzahlung oder Sanierung wieder abgebaut werden.
    """ % (int(neg_count), len(sim.actors)))
    return "\n".join([
        section("UTF‑8 Art 4: Bilanz-Skyline der Akteure", "🏙"),
        abbreviations([
            ("🟢", "positive LZ-Bilanz"),
            ("🔴", "negative LZ-Bilanz"),
            ("rep", "Reputation; steigt durch Lösungen, sinkt durch Schäden, Betrug, Ausfälle"),
            ("│█░│", "Balken relativ zum größten Betrag in dieser Grafik"),
            ("🏠/🏭/🏦/🏛", "Haushalt, Unternehmen, Bank, Staat"),
        ]),
        "",
        explanation,
        "\n".join(lines),
        "",
        analysis,
    ])


def art_timeseries(sim: core.Simulation) -> str:
    sev = metric_series(sim, "open_problem_severity")
    solved = metric_series(sim, "cumulative_solved_value")
    damage = metric_series(sim, "cumulative_damage_value")
    neg = metric_series(sim, "negative_actors")
    tmax = metric_series(sim, "max_tension")
    fraud = metric_series(sim, "fraud_cases_detected")
    rows = [
        ("OP", "offene Problemschwere", -sev[-1] if sev else 0.0, sparkline(sev)),
        ("SOL", "kumulierte Problemlösung", solved[-1] if solved else 0.0, sparkline(solved)),
        ("DMG", "kumulierter Schaden", -damage[-1] if damage else 0.0, sparkline(damage)),
        ("NEG", "negative Akteure", neg[-1] if neg else 0.0, sparkline(neg)),
        ("TMAX", "maximale Spannung", tmax[-1] if tmax else 0.0, sparkline(tmax)),
        ("FRD", "entdeckter Betrug", fraud[-1] if fraud else 0.0, sparkline(fraud)),
    ]
    lines = []
    for code, name, val, sp in rows:
        valstr = fmt_lz(val) if code in ("OP", "SOL", "DMG") else fmt_num(float(val))
        lines.append("  %-4s %-28s %12s  %s" % (code, name, valstr, sp))
    explanation = wrap_block("""
    Diese Sparkline-Grafik verdichtet den gesamten Zeitverlauf. Jeder kleine Block steht für einen Abschnitt der Simulation.
    Steigende Linien bei SOL sind gut, steigende Linien bei DMG/OP/TMAX/FRD sind Warnsignale, je nach Kontext.
    """)
    repair_ratio = safe_div(solved[-1] if solved else 0.0, damage[-1] if damage else 0.0, 0.0)
    backlog_ratio = safe_div(sev[-1] if sev else 0.0, damage[-1] if damage else 0.0, 0.0)
    analysis = wrap_block("""
    Auswertung: Die Reparaturquote SOL/DMG liegt bei %s. Der offene Rückstand OP/DMG liegt bei %s. Eine starke TGW-Ökonomie zeigt
    wachsende SOL-Linien, während OP langfristig flacher wird. Wenn DMG schneller wächst als SOL, erzeugt das System mehr negative
    Stacks, als es abbaut.
    """ % (pct(repair_ratio), pct(backlog_ratio)))
    return "\n".join([
        section("UTF‑8 Art 5: Zeitreihen-Sparklines", "📈"),
        abbreviations([
            ("OP", "Open Problems: aktuelle offene Problemschwere"),
            ("SOL", "Solved Value: kumulierte Problemlösung"),
            ("DMG", "Damage: kumulierter formalisierter Schaden/Problemwert"),
            ("NEG", "Anzahl negativer Akteure"),
            ("TMAX", "höchste Spannung zwischen Staaten/Ländern"),
            ("FRD", "entdeckte Betrugsfälle"),
            ("▁…█", "Sparkline: niedrig bis hoch innerhalb dieser Zeitreihe"),
        ]),
        "",
        explanation,
        "\n".join(lines),
        "",
        analysis,
    ])


def art_domain_heatmap(sim: core.Simulation) -> str:
    sev = severity_by_tag(sim)
    cnt = count_by_tag(sim)
    top = sorted(sev.items(), key=lambda kv: kv[1], reverse=True)[:14]
    max_sev = max([v for _, v in top] + [1.0])
    lines: List[str] = []
    used_abbr: List[Tuple[str, str]] = []
    for tag, value in top:
        ab = TAG_ABBR.get(tag, tag[:3].upper())
        used_abbr.append((ab, tag))
        lines.append("  %-3s %s n=%3d sev=%12s │%s│" % (ab, heat_symbol(value, max_sev), cnt.get(tag, 0), fmt_lz(-value), bar(value, max_sev, 34, "▓", "░")))
    if not lines:
        lines.append("  ∅ Keine offenen Problem-Domänen.")
    explanation = wrap_block("""
    Diese Heatmap verteilt offene Problemstacks auf topologische Domänen. Ein Problem kann mehrere Tags tragen; seine Schwere wird
    dann anteilig gezählt. Das zeigt, wo die Wirtschaft Solver-Kapazität, Kredite, Arbeitskräfte und staatliche Aufmerksamkeit braucht.
    """)
    dominant = top[0][0] if top else "keine"
    analysis = wrap_block("""
    Auswertung: Die stärkste Domäne ist %s. In TGW heißt das nicht automatisch, dass diese Branche schlecht ist, sondern dass dort
    der größte noch offene Lösungsbedarf liegt. Gute Firmen in angrenzenden offenen Mengen können hier durch topologischen Fit oder
    Adapterarbeit positiven LZ-Wert erzeugen.
    """ % dominant)
    abbr_items = [(ab, "Problem-Domäne: %s" % tag) for ab, tag in used_abbr]
    abbr_items.extend([
        ("n", "Anzahl offener Probleme, in denen diese Domäne vorkommt"),
        ("sev", "anteilige offene Problemschwere in LZ"),
        ("·░▒▓█", "Heat-Skala: wenig bis viel offene Schwere"),
    ])
    return "\n".join([
        section("UTF‑8 Art 6: Topologische Problem-Heatmap", "🧭"),
        abbreviations(abbr_items),
        "",
        explanation,
        "\n".join(lines),
        "",
        analysis,
    ])


def art_topology_fit(sim: core.Simulation) -> str:
    buckets = [(0.0, 0.2), (0.2, 0.4), (0.4, 0.6), (0.6, 0.8), (0.8, 1.01)]
    counts = [0 for _ in buckets]
    remote = 0
    fraudulent = 0
    adapter_value = latest(sim).get("cumulative_bridge_value", 0.0)
    for p in sim.projects.values():
        if p.remote:
            remote += 1
        if p.fraudulent:
            fraudulent += 1
        for i, (lo, hi) in enumerate(buckets):
            if lo <= p.topological_fit < hi:
                counts[i] += 1
                break
    max_count = max(counts + [1])
    lines = []
    for (lo, hi), n in zip(buckets, counts):
        lines.append("  FIT %.1f–%.1f  n=%4d │%s│" % (lo, hi, n, bar(n, max_count, 36, "█", "░")))
    lines.append("")
    lines.append("  REM-Projekte: %d   FRD-risk-Projekte: %d   ADA-Wert: %s" % (remote, fraudulent, fmt_lz(float(adapter_value))))
    explanation = wrap_block("""
    Diese Grafik zeigt, wie gut Unternehmen und Problemräume topologisch zusammenpassen. Ein hoher FIT bedeutet direkte Überlappung
    der offenen Mengen. Niedriger FIT kann trotzdem lösbar sein, braucht aber Adapter, Forschung oder Spezialisten.
    """)
    avg_fit = sum(p.topological_fit for p in sim.projects.values()) / max(1, len(sim.projects))
    analysis = wrap_block("""
    Auswertung: Der durchschnittliche FIT liegt bei %.3f. Ein niedriger Durchschnitt bedeutet nicht automatisch Scheitern, aber höhere
    Integrationskosten und mehr Risiko für Unterleistung. Der bisher erzeugte Adapter-/Brückenwert beträgt %s.
    """ % (avg_fit, fmt_lz(float(adapter_value))))
    return "\n".join([
        section("UTF‑8 Art 7: Topologie-Fit und Adapterarbeit", "🧩"),
        abbreviations([
            ("FIT", "topologische Kompatibilität zwischen Solver-Sektor und Problem-Domäne, 0 bis 1"),
            ("n", "Anzahl Projekte in diesem Fit-Intervall"),
            ("REM", "Remote/intergalaktisch oder nicht lokal gelöste Projekte"),
            ("FRD", "Fraud-risk: Projekt wurde intern als betrugsgefährdet simuliert"),
            ("ADA", "Adapter-/Brückenwert durch Verbindung eigentlich ferner offener Mengen"),
            ("│█░│", "Balken relativ zum größten Intervall"),
        ]),
        "",
        explanation,
        "\n".join(lines),
        "",
        analysis,
    ])


def art_escrow(sim: core.Simulation) -> str:
    c = sim.ledger.kind_counter
    locks = int(c.get("escrow_lock", 0))
    releases = int(c.get("escrow_release", 0))
    active_remote = sum(1 for p in sim.projects.values() if p.remote and p.status == "active")
    completed_remote = sum(1 for p in sim.projects.values() if p.remote and p.status in ("completed", "audited"))
    art = """
      🌌 Gᵢ / lokaler Fonds
             │
             │ 1) Lock: LZ wird gesperrt   [%5d]
             ▼
          🧊 Intergalactic Escrow  ── Δt: keine magische Sofort-Finalität ──▶  🌌 Gⱼ / Solver
             ▲                                                                │
             │ 3) Streit/Audit/Korrektur möglich                              │ 2) Release nach Abschluss [%5d]
             └────────────────────────────────────────────────────────────────┘

      Aktive Remote-Projekte: %-5d     abgeschlossene Remote-Projekte: %-5d
    """ % (locks, releases, active_remote, completed_remote)
    explanation = wrap_block("""
    Diese Grafik zeigt, wie intergalaktische Projekte ohne magische Echtzeit-Kommunikation funktionieren. LZ wird zuerst in Escrow
    gesperrt. Wegen Lichtgeschwindigkeitsgrenzen und Distanz wird später freigegeben, geprüft oder korrigiert.
    """)
    if locks == 0:
        verdict = "In diesem Lauf spielte intergalaktischer Escrow praktisch keine Rolle; der Markt blieb überwiegend lokal oder galaktisch."
    elif releases < locks:
        verdict = "Es gibt mehr Locks als Releases; ein Teil der Remote-Projekte befindet sich noch in Verzögerung oder aktiver Ausführung."
    else:
        verdict = "Locks und Releases sind weitgehend ausgeglichen; Remote-Abwicklung kam bis zur Freigabe durch."
    analysis = wrap_block("Auswertung: " + verdict)
    return "\n".join([
        section("UTF‑8 Art 8: Intergalaktischer Escrow-Kanal", "🧊"),
        abbreviations([
            ("Gᵢ/Gⱼ", "sendende und empfangende Galaxie"),
            ("Lock", "LZ wird im Escrow gesperrt"),
            ("Release", "LZ wird nach Abschluss an Solver freigegeben"),
            ("Δt", "Zeitverzögerung durch Entfernung; keine Sofort-Finalität"),
            ("Remote", "Projekt außerhalb der lokalen/galaktischen Standardnähe"),
        ]),
        "",
        explanation,
        art.rstrip(),
        "",
        analysis,
    ])


def art_conflict_ladder(sim: core.Simulation) -> str:
    m = latest(sim)
    avg_t = float(m["avg_tension"])
    max_t = float(m["max_tension"])
    w = int(m["war_events"])
    war_damage = float(m["war_damage"])
    pos = int(round(clamp(max_t / 3.0, 0.0, 1.0) * 48))
    line = "─" * pos + "▲" + "─" * max(0, 48 - pos)
    art = """
      0.0 Frieden        🟢 ├────────────────────────────────────────────────┤
      1.0 Kalter Druck   🟡 ├────────────────────────────────────────────────┤
      2.0 Heiße Gefahr   🟠 ├────────────────────────────────────────────────┤
      3.0 Kriegsspirale  🔴 ├────────────────────────────────────────────────┤
                              %s
                              maxT=%.3f   avgT=%.3f   WAR=%d   WDMG=%s
    """ % (line, max_t, avg_t, w, fmt_lz(-war_damage))
    explanation = wrap_block("""
    Diese Leiter zeigt die höchste und durchschnittliche Spannung zwischen Staaten/Ländern. Kalte Konflikte erzeugen Kosten; heiße
    Konflikte erzeugen massive negative Stacks. Diplomatie-, Sicherheits- und Governance-Lösungen können Spannung reduzieren.
    """)
    if w > 0:
        verdict = "Heiße Konflikte traten auf. Das System verbucht sie als negative LZ-Schäden; militärische Eskalation wird also nicht einfach als Gewinn verschleiert."
    elif max_t > 1.2:
        verdict = "Es gab erhöhten kalten Druck, aber keine heißen Konflikte. Die Wirtschaft trägt Sicherheits- und Vertrauenskosten."
    else:
        verdict = "Die Spannungen blieben niedrig; Konflikte waren kein Haupttreiber des Ergebnisses."
    analysis = wrap_block("Auswertung: " + verdict)
    return "\n".join([
        section("UTF‑8 Art 9: Konfliktleiter", "🛡"),
        abbreviations([
            ("maxT", "höchster Spannungswert zwischen zwei Staaten/Ländern"),
            ("avgT", "durchschnittlicher Spannungswert"),
            ("WAR", "Anzahl heißer Konfliktereignisse"),
            ("WDMG", "Kriegsschaden als negative LZ"),
            ("▲", "aktuelle Position des höchsten Spannungswerts"),
        ]),
        "",
        explanation,
        art.rstrip(),
        "",
        analysis,
    ])


def art_fraud_audit(sim: core.Simulation) -> str:
    projects = list(sim.projects.values())
    promised = sum(p.promised_reduction for p in projects)
    actual = sum(p.actual_reduction for p in projects)
    fraudulent = sum(1 for p in projects if p.fraudulent)
    audited = sum(1 for p in projects if p.status == "audited")
    m = latest(sim)
    penalty = float(m["cumulative_fraud_penalty"])
    ratio = safe_div(actual, promised, 1.0)
    art = """
      Behauptung / Promise      %12s  │%s│
                    │
                    ▼
      Reale Reduktion / Actual  %12s  │%s│
                    │
                    ▼
      🧪 Audit ── entdeckt/Korrektur ──▶ inverser Stack: −LZ

      Audited=%d   FRD-risk=%d   Detected=%d   Penalty=%s   ACT/PROM=%s
    """ % (
        fmt_lz(promised), bar(promised, max(1.0, promised), 34, "█", "░"),
        fmt_lz(actual), bar(actual, max(1.0, promised), 34, "▓", "░"),
        audited, fraudulent, int(m["fraud_cases_detected"]), fmt_lz(-penalty), pct(ratio)
    )
    explanation = wrap_block("""
    Diese Grafik zeigt die Differenz zwischen versprochener und realer Problemlösung. Betrug oder starke Unterleistung wird nicht
    gelöscht, sondern durch inverse LZ-Buchungen korrigiert. Auditoren sind selbst Akteure und können Reputation verlieren, wenn sie
    falsch prüfen.
    """)
    if fraudulent == 0:
        verdict = "Es wurden keine betrugsgefährdeten Projekte simuliert; Audit spielte vor allem als Vertrauensmechanismus eine Rolle."
    elif penalty <= 0:
        verdict = "Betrugsgefährdete Projekte existierten, wurden aber nicht oder kaum sanktioniert; das wäre langfristig ein Schwachpunkt."
    else:
        verdict = "Es gab Korrekturzahlungen; das Protokoll machte falsche Lösungsbehauptungen sichtbar und teilweise rückabwickelbar."
    analysis = wrap_block("Auswertung: " + verdict)
    return "\n".join([
        section("UTF‑8 Art 10: Betrug, Audit und inverse Buchung", "🧪"),
        abbreviations([
            ("Promise", "versprochene Problemlösung"),
            ("Actual", "tatsächlich simulierte Problemreduktion"),
            ("Audited", "bereits geprüfte Projekte"),
            ("FRD", "betrugsgefährdete Projekte"),
            ("Penalty", "negative Korrektur-/Strafzahlung in LZ"),
            ("ACT/PROM", "Verhältnis realer Reduktion zu versprochener Reduktion"),
            ("−LZ", "inverse Gruppenbuchung: falscher positiver Wert wird negativ korrigiert"),
        ]),
        "",
        explanation,
        art.rstrip(),
        "",
        analysis,
    ])


def art_institution_table(sim: core.Simulation) -> str:
    rows = actor_kind_summary(sim)
    max_abs = max([abs(balance) for _, _, balance, _ in rows] + [1.0])
    lines = []
    for kind, count, balance, negs in rows:
        icon = KIND_ICON.get(kind, "•")
        lines.append("  %s %-14s count=%4d neg=%4d Σ=%12s │%s│" % (icon, kind, count, negs, fmt_lz(balance), bar(balance, max_abs, 32, "█", "░")))
    explanation = wrap_block("""
    Diese Tabelle aggregiert die Akteursarten. Sie zeigt, ob LZ vor allem bei Haushalten, Unternehmen, Banken, Staaten, Fonds oder
    Spezialinstitutionen liegt. Die Summen sind keine neue Währung, sondern zusammengefasste LZ-Kontostände.
    """)
    state_balance = sum(sim.actors[sid].balance for sid in sim.states)
    firm_balance = sum(sim.actors[fid].balance for fid in sim.firms)
    bank_balance = sum(sim.actors[bid].balance for bid in sim.banks)
    analysis = wrap_block("""
    Auswertung: Staaten stehen aggregiert bei %s, Unternehmen bei %s, Banken bei %s. Negative öffentliche Positionen können Investitionen
    oder Krieg/Schäden bedeuten; negative Unternehmenspositionen können Kreditstress, Betrugskorrekturen oder echte Reparaturpflichten sein.
    """ % (fmt_lz(state_balance), fmt_lz(firm_balance), fmt_lz(bank_balance)))
    return "\n".join([
        section("UTF‑8 Art 11: Institutionen-Bilanz", "🏛"),
        abbreviations([
            ("count", "Anzahl Akteure dieser Art"),
            ("neg", "Anzahl Akteure dieser Art mit negativem Konto"),
            ("Σ", "Summe der LZ-Konten innerhalb dieser Akteursart"),
            ("│█░│", "Balken relativ zur größten Aggregatsumme"),
            ("Icons", "🏠 Haushalt, 🏭 Firma, 🏦 Bank, 🏛 Staat, 🛠 Fonds, 🧪 Prüfer"),
        ]),
        "",
        explanation,
        "\n".join(lines),
        "",
        analysis,
    ])


def art_outcome_scorecard(sim: core.Simulation) -> str:
    m = latest(sim)
    solved = float(m["cumulative_solved_value"])
    damage = float(m["cumulative_damage_value"])
    open_sev = float(m["open_problem_severity"])
    repair_ratio = safe_div(solved, damage, 0.0)
    backlog_ratio = safe_div(open_sev, damage, 0.0)
    fraud_ratio = safe_div(float(m["cumulative_fraud_penalty"]), max(1.0, solved), 0.0)
    conflict_score = clamp(float(m["max_tension"]) / 3.0 + 0.10 * int(m["war_events"]), 0.0, 1.0)
    unemployment_ratio = safe_div(float(m["unemployment"]), max(1.0, len(sim.households)), 0.0)
    balance_error = abs(float(m["total_balance"]))
    rows = [
        ("REP", "Reparaturquote SOL/DMG", repair_ratio, "hoch ist gut"),
        ("BKL", "Backlog OP/DMG", backlog_ratio, "niedrig ist gut"),
        ("FRS", "Betrugsstress Penalty/SOL", fraud_ratio, "niedrig ist gut"),
        ("CFS", "Konfliktstress", conflict_score, "niedrig ist gut"),
        ("UNM", "Arbeitslosigkeit", unemployment_ratio, "niedrig ist gut"),
    ]
    lines = []
    for code, name, val, meaning in rows:
        lines.append("  %-3s %-30s %7s │%s│ %s" % (code, name, pct(val), meter(val, 1.0, 34), meaning))
    lines.append("  BAL Gruppenbilanzfehler        %s  %s" % ("%.9f LZ" % balance_error, "✓ nahe 0" if balance_error < 1e-5 else "! prüfen"))
    label, label_text = outcome_label(sim)
    explanation = wrap_block("""
    Diese Scorecard ist keine zweite Währung und kein moralischer Absolutwert. Sie fasst nur die wichtigsten Ergebnisverhältnisse
    des Simulationslaufs zusammen: Reparatur, Rückstand, Betrug, Konflikt, Arbeitsmarkt und Gruppenbilanz.
    """)
    analysis = wrap_block("""
    Auswertung: %s — %s Die Gruppenbilanz ist %.9f LZ; das bestätigt, dass der Lauf rechnerisch über additive Transfers und inverse
    Buchungen funktioniert hat. Entscheidend für die Qualität des Ausgangs ist daher nicht Geldschöpfung, sondern ob negative Stacks
    schneller entstehen als echte Lösungen.
    """ % (label, label_text, float(m["total_balance"])))
    return "\n".join([
        section("UTF‑8 Art 12: Ergebnis-Scorecard", "✅"),
        abbreviations([
            ("REP", "Reparaturquote: kumulierte Lösung geteilt durch kumulierten Schaden"),
            ("BKL", "Backlog: noch offene Problemschwere geteilt durch kumulierten Schaden"),
            ("FRS", "Betrugsstress: Korrekturzahlungen geteilt durch gelösten Wert"),
            ("CFS", "Konfliktstress aus max. Spannung und Kriegsevents"),
            ("UNM", "Arbeitslosenquote der Haushalte"),
            ("BAL", "Fehler der Gesamtbilanz Σ aller Konten; sollte nahe 0 sein"),
        ]),
        "",
        explanation,
        "\n".join(lines),
        "",
        analysis,
    ])


def art_recent_events(sim: core.Simulation) -> str:
    lines = []
    for ev in list(sim.events)[-20:]:
        tick, kind, a, value, b = ev
        glyph = {
            "project_start": "🚀", "project_done": "✅", "fraud_detected": "🧪", "underperformance": "⚠",
            "problem": "🧨", "hot_conflict": "🔥", "bankruptcy": "💥", "loan_default": "🏦",
        }.get(kind, "•")
        lines.append("  %s t=%4d %-18s %-34s %12s %s" % (glyph, tick, kind, clean_name(a, 34), fmt_lz(float(value)), clean_name(b, 28)))
    if not lines:
        lines.append("  ∅ Keine Ereignisse aufgezeichnet.")
    explanation = wrap_block("""
    Diese Ereignisleiste zeigt die letzten wichtigen diskreten Vorgänge: neue Probleme, Projektstarts, Abschlüsse, Konflikte,
    Insolvenzen, Kreditausfälle oder Auditkorrekturen. Sie hilft, den Endzustand nicht nur als Zahl, sondern als Verlauf zu lesen.
    """)
    analysis = wrap_block("""
    Auswertung: Die letzten Ereignisse zeigen, welche Mechanik unmittelbar vor dem Ende dominierte. Viele Problemereignisse bedeuten
    neuen Druck; viele Projektabschlüsse bedeuten aktive Reparatur; Audit- oder Konfliktereignisse zeigen Vertrauens- bzw. Sicherheitsstress.
    """)
    return "\n".join([
        section("UTF‑8 Art 13: Ereignisleiste", "🧾"),
        abbreviations([
            ("t", "Tick/Simulationszeitpunkt"),
            ("kind", "Ereignistyp"),
            ("LZ-Wert", "positiv bei Lösung/Zufluss, negativ bei Schaden/Korrektur"),
            ("🚀✅🧪🔥", "Projektstart, Projektabschluss, Audit/Korrektur, heißer Konflikt"),
        ]),
        "",
        explanation,
        "\n".join(lines),
        "",
        analysis,
    ])


def build_utf8_report(sim: core.Simulation) -> str:
    parts = [
        build_intro(sim),
        art_math_core(sim),
        art_actor_market_flow(sim),
        art_galaxy_map(sim),
        art_balance_skyline(sim),
        art_timeseries(sim),
        art_domain_heatmap(sim),
        art_topology_fit(sim),
        art_escrow(sim),
        art_conflict_ladder(sim),
        art_fraud_audit(sim),
        art_institution_table(sim),
        art_outcome_scorecard(sim),
        art_recent_events(sim),
    ]
    return "\n\n".join(parts) + "\n"


def run_simulation(cfg: core.Config, progress: bool = True) -> core.Simulation:
    sim = core.Simulation(cfg)
    if not cfg.quiet and progress:
        print("🌌 TGW UTF‑8 Art Simulation")
        print("Szenario=%s Seed=%s Ticks=%d Galaxien=%d" % (cfg.scenario, cfg.seed, cfg.ticks, cfg.galaxies))
        print(sim.summary_line(0))
    for _ in range(cfg.ticks):
        sim.step()
        if not cfg.quiet and progress and cfg.report_every > 0 and sim.tick % cfg.report_every == 0:
            print(sim.summary_line(sim.tick))
    if cfg.csv_out:
        sim.write_csv(cfg.csv_out)
    if cfg.json_out:
        sim.write_json(cfg.json_out)
    return sim


def scenario_metric_row(name: str, sim: core.Simulation) -> Dict[str, Any]:
    m = latest(sim)
    solved = float(m["cumulative_solved_value"])
    damage = float(m["cumulative_damage_value"])
    open_sev = float(m["open_problem_severity"])
    label, _ = outcome_label(sim)
    return {
        "scenario": name,
        "label": label,
        "solved": solved,
        "damage": damage,
        "open": open_sev,
        "repair_ratio": safe_div(solved, damage, 0.0),
        "backlog_ratio": safe_div(open_sev, damage, 0.0),
        "fraud": int(m["fraud_cases_detected"]),
        "fraud_penalty": float(m["cumulative_fraud_penalty"]),
        "war": int(m["war_events"]),
        "war_damage": float(m["war_damage"]),
        "neg": int(m["negative_actors"]),
        "unemp": int(m["unemployment"]),
        "max_t": float(m["max_tension"]),
        "bankruptcies": int(m["bankruptcies"]),
        "balance": float(m["total_balance"]),
        "actors": len(sim.actors),
    }


def markdown_table(headers: Sequence[str], rows: Sequence[Sequence[str]]) -> str:
    out = []
    out.append("| " + " | ".join(headers) + " |")
    out.append("| " + " | ".join(["---" for _ in headers]) + " |")
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def suite_bar(name: str, value: float, max_value: float, width: int = 34) -> str:
    return "%s │%s│ %s" % (name, bar(value, max_value, width, "█", "░"), fmt_num(value))


def build_suite_report(results: List[Tuple[str, core.Simulation]]) -> str:
    rows = [scenario_metric_row(name, sim) for name, sim in results]
    max_open = max([r["open"] for r in rows] + [1.0])
    max_solved = max([r["solved"] for r in rows] + [1.0])
    max_damage = max([r["damage"] for r in rows] + [1.0])
    max_fraud = max([r["fraud_penalty"] for r in rows] + [1.0])
    max_war = max([r["war_damage"] for r in rows] + [1.0])

    intro = "\n".join([
        "# 🌌 TGW UTF‑8 Szenario-Suite: verschiedene Ausgänge",
        "",
        wrap_block("""
        Diese Auswertung vergleicht mehrere Läufe derselben Wirtschaftslogik. Jeder Lauf verwendet dieselbe einzige Währung LZ,
        dieselbe additive Gruppenbuchhaltung und dieselbe topologische Problem-/Lösungsstruktur. Die Szenarien verändern nur die
        Rahmenbedingungen: Konfliktwahrscheinlichkeit, Betrugsdruck, intergalaktische Remote-Projekte oder Anfangsknappheit.
        """),
        "",
        abbreviations([
            ("SOL", "kumulierte Problemlösung"),
            ("DMG", "kumulierte formalisierte Schäden/Probleme"),
            ("OP", "offene Problemschwere am Ende"),
            ("REP", "Reparaturquote SOL/DMG"),
            ("BKL", "Backlogquote OP/DMG"),
            ("FRD", "entdeckte Betrugsfälle"),
            ("WAR", "heiße Konflikte"),
            ("maxT", "höchste politische Spannung"),
            ("Σbal", "Gesamtsumme aller Konten; soll nahe 0 bleiben"),
        ]),
    ])

    table_rows = []
    for r in rows:
        table_rows.append([
            r["scenario"], r["label"], fmt_lz(r["solved"]), fmt_lz(-r["damage"]), fmt_lz(-r["open"]),
            pct(r["repair_ratio"]), pct(r["backlog_ratio"]), str(r["fraud"]), str(r["war"]), "%.3f" % r["max_t"], "%.6f" % r["balance"],
        ])
    table = markdown_table(["Szenario", "Ausgang", "SOL", "DMG", "OP", "REP", "BKL", "FRD", "WAR", "maxT", "Σbal"], table_rows)

    bars: List[str] = []
    bars.append("## 📊 Vergleichsdiagramme")
    bars.append("")
    bars.append(abbreviations([
        ("SOL", "positive Problemlösung; höher ist besser"),
        ("DMG", "formalisierter Schaden; höher bedeutet mehr negative Stack-Erzeugung"),
        ("OP", "offene Problemschwere am Ende; niedriger ist besser"),
        ("FRP", "Fraud Penalty; Korrekturzahlungen wegen Betrug/Unterleistung"),
        ("WDMG", "Kriegsschaden"),
        ("│█░│", "Balken relativ zum größten Wert in diesem Vergleich"),
    ]))
    bars.append("")
    for r in rows:
        bars.append("### %s" % r["scenario"])
        bars.append("  SOL  " + suite_bar("", r["solved"], max_solved))
        bars.append("  DMG  " + suite_bar("", r["damage"], max_damage))
        bars.append("  OP   " + suite_bar("", r["open"], max_open))
        bars.append("  FRP  " + suite_bar("", r["fraud_penalty"], max_fraud))
        bars.append("  WDMG " + suite_bar("", r["war_damage"], max_war))
        bars.append("")

    interpretations: List[str] = ["## 🧠 Auswertung der verschiedenen Ausgänge", ""]
    for name, sim in results:
        r = scenario_metric_row(name, sim)
        label, label_text = outcome_label(sim)
        interpretations.append("### %s — %s" % (name, label))
        interpretations.append(wrap_block("""
        %s Reparaturquote: %s. Backlogquote: %s. Betrugsfälle: %d. Kriegsevents: %d. Maximalspannung: %.3f.
        Daraus folgt: %s
        """ % (
            SCENARIO_NAMES.get(name, name), pct(r["repair_ratio"]), pct(r["backlog_ratio"]), r["fraud"], r["war"], r["max_t"], label_text
        )))
        interpretations.append("")

    closing = wrap_block("""
    Gesamtlesart: Die TGW-Simulation belohnt nicht einfach Aktivität, sondern prüfbare Problemreduktion. In ruhigen Szenarien kann
    Solver-Kapazität offene Probleme abbauen. In Konflikt- oder Betrugsdruck-Szenarien wird die gleiche Währung durch negative Stacks,
    Audits und Reparaturfonds belastet. Dass Σbal nahe Null bleibt, ist wichtig: Die Simulation erzeugt keine zweite verdeckte Währung,
    sondern verschiebt und korrigiert LZ innerhalb der additiven Gruppe.
    """)

    return "\n\n".join([intro, "## 🧾 Vergleichstabelle", table, "\n".join(bars), "\n".join(interpretations), closing]) + "\n"


def build_config_from_args(args: argparse.Namespace, scenario: Optional[str] = None, seed: Optional[int] = None) -> core.Config:
    return core.Config(
        ticks=max(0, args.ticks),
        seed=args.seed if seed is None else seed,
        scenario=args.scenario if scenario is None else scenario,
        galaxies=max(1, args.galaxies),
        planets_per_galaxy=max(1, args.planets_per_galaxy),
        states_per_planet=max(1, args.states_per_planet),
        households=max(1, args.households),
        firms=max(1, args.firms),
        report_every=max(0, args.report_every),
        initial_problems_per_state=max(0, args.initial_problems_per_state),
        max_projects_started_per_tick=max(1, args.max_projects_started_per_tick),
        max_active_projects=max(1, args.max_active_projects),
        intergalactic_delay=max(1, args.intergalactic_delay),
        remote_project_probability=clamp(args.remote_project_probability, 0.0, 1.0),
        war_probability=max(0.0, args.war_probability),
        fraud_pressure=max(0.1, args.fraud_pressure),
        externality_rate=max(0.0, args.externality_rate),
        credit_leverage=max(0.1, args.credit_leverage),
        csv_out=args.csv_out if scenario is None else "",
        json_out=args.json_out if scenario is None else "",
        quiet=bool(args.quiet),
    )


def parse_args(argv: Optional[List[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="TGW-Simulation mit umfangreichem UTF‑8-Art-Bericht.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--ticks", type=int, default=250, help="Anzahl Simulationsschritte")
    parser.add_argument("--seed", type=int, default=42, help="Zufallsseed")
    parser.add_argument("--scenario", choices=["baseline", "conflict", "fraud", "intergalactic", "scarcity"], default="baseline", help="Einzelszenario")
    parser.add_argument("--scenario-suite", action="store_true", help="Alle fünf Hauptszenarien laufen lassen und vergleichen")
    parser.add_argument("--galaxies", type=int, default=3, help="Anzahl Galaxien")
    parser.add_argument("--planets-per-galaxy", type=int, default=3, help="Planeten pro Galaxie")
    parser.add_argument("--states-per-planet", type=int, default=2, help="Länder/Staaten pro Planet")
    parser.add_argument("--households", type=int, default=300, help="Haushalte/Arbeitnehmer")
    parser.add_argument("--firms", type=int, default=70, help="Unternehmen")
    parser.add_argument("--report-every", type=int, default=25, help="Konsolenbericht alle N Ticks; 0 deaktiviert")
    parser.add_argument("--initial-problems-per-state", type=int, default=5, help="Startprobleme je Staat")
    parser.add_argument("--max-projects-started-per-tick", type=int, default=18, help="Max. neue Problemlösungsprojekte pro Tick")
    parser.add_argument("--max-active-projects", type=int, default=80, help="Max. parallele Projekte")
    parser.add_argument("--intergalactic-delay", type=int, default=18, help="Basisverzögerung zwischen Galaxien")
    parser.add_argument("--remote-project-probability", type=float, default=0.08, help="Wahrscheinlichkeit, remote Solver zu suchen")
    parser.add_argument("--war-probability", type=float, default=0.004, help="Basiswahrscheinlichkeit für heißen Konflikt")
    parser.add_argument("--fraud-pressure", type=float, default=1.0, help="Betrugsdruck-Multiplikator")
    parser.add_argument("--externality-rate", type=float, default=1.0, help="Externe-Schäden-Multiplikator")
    parser.add_argument("--credit-leverage", type=float, default=4.0, help="Wie tief Banken negativ gehen dürfen")
    parser.add_argument("--csv-out", default="", help="CSV-Datei für Zeitreihe, nur Einzelszenario")
    parser.add_argument("--json-out", default="", help="JSON-Datei für Endzustand, nur Einzelszenario")
    parser.add_argument("--report-out", default="", help="UTF‑8-Art-Bericht als Textdatei speichern, nur Einzelszenario")
    parser.add_argument("--suite-out", default="", help="Markdown-Bericht für Szenario-Suite speichern")
    parser.add_argument("--quiet", action="store_true", help="Keine Fortschrittsausgabe")
    return parser.parse_args(argv)


def write_text(path: str, text: str) -> None:
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)


def main(argv: Optional[List[str]] = None) -> int:
    args = parse_args(argv)
    if args.scenario_suite:
        results: List[Tuple[str, core.Simulation]] = []
        scenarios = ["baseline", "conflict", "fraud", "intergalactic", "scarcity"]
        for scenario in scenarios:
            cfg = build_config_from_args(args, scenario=scenario, seed=args.seed)
            # Suite mode should stay readable; progress only if not quiet.
            if not cfg.quiet:
                print("\n🌌 Suite-Lauf: %s" % scenario)
            sim = run_simulation(cfg, progress=not cfg.quiet)
            results.append((scenario, sim))
        report = build_suite_report(results)
        if args.suite_out:
            write_text(args.suite_out, report)
            if not args.quiet:
                print("\nSuite-Bericht geschrieben: %s" % args.suite_out)
        else:
            print(report)
        return 0

    cfg = build_config_from_args(args)
    sim = run_simulation(cfg, progress=not cfg.quiet)
    report = build_utf8_report(sim)
    if args.report_out:
        write_text(args.report_out, report)
        if not args.quiet:
            print("\nUTF‑8-Art-Bericht geschrieben: %s" % args.report_out)
    elif not cfg.quiet:
        print("\n" + report)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
