#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
Gestapelte Arbeitsblock-Wirtschaft
Eine bunte PyPy3-kompatible Simulation des Arbeitswährungs-Systems.

Ausführen:
    pypy3 gaw_pypy3_simulation.py
    pypy3 gaw_pypy3_simulation.py --szenario krise --perioden 8 --seed 7
    pypy3 gaw_pypy3_simulation.py --no-color

Nur Standardbibliothek, keine externen Pakete.
"""

from __future__ import annotations

import argparse
import math
import os
import random
import re
import shutil
import sys
import textwrap
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


# ---------------------------------------------------------------------------
# Farbe, Darstellung, Tabellen
# ---------------------------------------------------------------------------

class UI:
    """Terminal-Ausgabe mit ANSI-256-Farben. PyPy3-kompatibel."""

    UNIT_BG = {
        "ID": 244,
        "E": 45,
        "3D": 213,
        "O": 82,
        "O+": 118,
        "O-": 196,
        "M": 201,
        "Mwir": 207,
        "K": 33,
        "Q": 129,
        "AW": 220,
        "P": 208,
        "S": 197,
        "ST": 141,
        "α": 39,
        "β": 77,
        "γ": 162,
        "GF": 51,
        "GM": 226,
        "T": 117,
        "R": 166,
        "KR": 214,
        "B": 34,
        "REG": 40,
        "ENT": 202,
        "SCH": 160,
    }

    UNIT_FG = {
        "ID": 250,
        "E": 45,
        "3D": 213,
        "O": 82,
        "O+": 118,
        "O-": 196,
        "M": 201,
        "Mwir": 207,
        "K": 33,
        "Q": 129,
        "AW": 220,
        "P": 208,
        "S": 197,
        "ST": 141,
        "α": 39,
        "β": 77,
        "γ": 162,
        "GF": 51,
        "GM": 226,
        "T": 117,
        "R": 166,
        "KR": 214,
        "B": 34,
        "REG": 40,
        "ENT": 202,
        "SCH": 160,
    }

    RAINBOW = [196, 202, 226, 46, 51, 39, 129, 201]

    def __init__(self, color: bool = True, width: Optional[int] = None) -> None:
        self.color = bool(color)
        if width is None:
            width = shutil.get_terminal_size((110, 30)).columns
        self.width = max(76, min(140, int(width)))

    def c(self, text: object, fg: Optional[int] = None, bg: Optional[int] = None,
          bold: bool = False, dim: bool = False) -> str:
        text = str(text)
        if not self.color:
            return text
        codes: List[str] = []
        if bold:
            codes.append("1")
        if dim:
            codes.append("2")
        if fg is not None:
            codes.append("38;5;%d" % fg)
        if bg is not None:
            codes.append("48;5;%d" % bg)
        if not codes:
            return text
        return "\033[%sm%s\033[0m" % (";".join(codes), text)

    def strip(self, text: object) -> str:
        return ANSI_RE.sub("", str(text))

    def unit(self, name: str) -> str:
        bg = self.UNIT_BG.get(name, 238)
        fg = 16 if bg not in (16, 17, 18, 19, 20, 21) else 231
        return self.c(" %s " % name, fg=fg, bg=bg, bold=True)

    def amount(self, value: float, unit: str, digits: int = 2, signed: bool = False) -> str:
        sign = "+" if signed else ""
        spec = sign + ",." + str(digits) + "f"
        number = format(float(value), spec).replace(",", "_")
        return self.c(number, fg=self.UNIT_FG.get(unit, 231), bold=True) + " " + self.unit(unit)

    def plain_amount(self, value: float, digits: int = 2, signed: bool = False) -> str:
        sign = "+" if signed else ""
        spec = sign + ",." + str(digits) + "f"
        return format(float(value), spec).replace(",", "_")

    def rainbow(self, text: str) -> str:
        if not self.color:
            return text
        out = []
        colors = self.RAINBOW
        for i, ch in enumerate(text):
            if ch.isspace():
                out.append(ch)
            else:
                out.append(self.c(ch, fg=colors[i % len(colors)], bold=True))
        return "".join(out)

    def rule(self, char: str = "═") -> None:
        print(self.rainbow(char * self.width))

    def title(self, text: str) -> None:
        print()
        self.rule("═")
        inner = "  " + text.strip() + "  "
        pad = max(0, self.width - len(inner))
        left = pad // 2
        right = pad - left
        print(self.c(" " * left + inner + " " * right, fg=16, bg=220, bold=True))
        self.rule("═")

    def subsection(self, text: str, fg: int = 231, bg: int = 54) -> None:
        print(self.c("  " + text + "  ", fg=fg, bg=bg, bold=True))

    def wrap(self, text: str, indent: int = 0) -> None:
        width = max(50, self.width - indent)
        prefix = " " * indent
        for para in text.strip().split("\n"):
            if not para.strip():
                print()
                continue
            print(textwrap.fill(para.strip(), width=width, initial_indent=prefix,
                                subsequent_indent=prefix))

    def kv(self, key: str, value: str) -> None:
        print("  " + self.c(key, fg=229, bold=True) + self.c(" → ", fg=244) + value)

    def table(self, headers: Sequence[str], rows: Sequence[Sequence[object]],
              right: Optional[Iterable[int]] = None) -> None:
        right_set = set(right or [])
        data = [[str(cell) for cell in row] for row in rows]
        heads = [self.c(h, fg=16, bg=250, bold=True) for h in headers]
        all_rows = [heads] + data
        widths = []
        for col in range(len(headers)):
            width = max(len(self.strip(row[col])) for row in all_rows)
            widths.append(min(max(width, 3), 40))

        def fit(cell: str, width: int) -> str:
            raw = self.strip(cell)
            if len(raw) <= width:
                return cell
            # Farbige Zellen werden bei Kürzung unpraktisch; deshalb grob plain kürzen.
            return raw[:max(1, width - 1)] + "…"

        def line(row: Sequence[str], is_header: bool = False) -> str:
            parts = []
            for i, cell in enumerate(row):
                cell = fit(cell, widths[i])
                raw_len = len(self.strip(cell))
                pad = widths[i] - raw_len
                if i in right_set and not is_header:
                    parts.append(" " * pad + cell)
                else:
                    parts.append(cell + " " * pad)
            return "  " + self.c("│", fg=245) + (" " + self.c("│", fg=245) + " ").join(parts) + self.c("│", fg=245)

        top = "  " + self.c("┌" + "┬".join("─" * (w + 2) for w in widths) + "┐", fg=245)
        mid = "  " + self.c("├" + "┼".join("─" * (w + 2) for w in widths) + "┤", fg=245)
        bot = "  " + self.c("└" + "┴".join("─" * (w + 2) for w in widths) + "┘", fg=245)
        print(top)
        print(line(heads, True))
        print(mid)
        for row in data:
            print(line(row))
        print(bot)

    def badge(self, text: str, color: int) -> str:
        return self.c(" %s " % text, fg=16, bg=color, bold=True)

    def heat(self, value: float, low: float = 0.8, high: float = 2.5) -> str:
        """Farbige Ampel für Knappheit oder Risiko."""
        if value < low:
            return self.badge("niedrig", 82)
        if value < 1.2:
            return self.badge("normal", 46)
        if value < high:
            return self.badge("hoch", 208)
        return self.badge("kritisch", 196)


ABBR = {
    "ID": "Kennnummer eines Arbeitsblocks, Prüffalls oder Segments. Sie macht sichtbar, welche Zeile später geprüft, bezahlt, abgelehnt oder gestapelt wird.",
    "E": "Eingangseinheiten. Das sind alle Ressourcen, Zeiten, Materialien, Informationen oder Vorleistungen, die in eine Arbeit hineingehen und deshalb im Vorgang gebucht werden.",
    "3D": "Dreidimensional. Dieses Kürzel bezeichnet Arbeit an räumlichen Körpern und Volumen, zum Beispiel Häuserbau, Maschinenbau, Rohrleitungen, Brücken oder Lagerkörper.",
    "O": "Ausgangseinheiten. Das sind erzeugte Güter, Dienste, Informationen, Reparaturen oder Verbesserungen, die nach der Arbeit als nutzbarer Output vorhanden sind.",
    "O+": "Positiver Ausgang. Damit werden nützliche Wirkungen gezählt: ein gelöster Zustand, ein funktionierendes Produkt, eine bessere Information oder eine reale Verbesserung.",
    "O-": "Negativer Ausgang. Damit werden Schäden, Fehler, Belastungen, Fehlinformationen oder verschlechterte Zustände gezählt, die den Arbeitswert mindern oder Haftung erzeugen.",
    "M": "Arbeitsmenge. In der einfachen Grundrechnung ist sie die Summe aus Eingangseinheiten und Ausgangseinheiten; sie beschreibt die rohe Größe des Vorgangs.",
    "Mwir": "Wirksame Arbeitsmenge. Sie bleibt übrig, nachdem negativer Ausgang mit einem Schadensgewicht abgezogen wurde; sie kann auch unter null fallen.",
    "K": "Arbeitsfaktor. Er ist der Multiplikator der Arbeitsart; höhere Hebelarbeit wie Kommunikation, Blockzerlegung oder Mathematik bekommt einen höheren Faktor als Basisarbeit.",
    "Q": "Qualitätsfaktor. Er beschreibt die geprüfte Güte der Arbeit; 1,00 bedeutet Standardqualität, darunter wird abgewertet, darüber wird aufgewertet.",
    "AW": "Arbeitswährung. Sie ist der gutgeschriebene Wert aus geprüfter, nützlicher Arbeit und kann bezahlt, gestapelt, besteuert oder als Schuld verrechnet werden.",
    "P": "Preis. Er ist die Zahlungsforderung für ein Gut oder eine Dienstleistung; er kann vom Arbeitswert abweichen, weil Knappheit und Marktbedingungen mitwirken.",
    "S": "Knappheitsfaktor. Er steigt bei Mangel und sinkt bei Überangebot; dadurch wird ein knappes Gut teurer, ohne dass seine reine Arbeitsmenge neu gezählt wird.",
    "ST": "Stapelwert. Er ist die aufsummierte Arbeitswährung, die in einem Projekt oder Produkt steckt; neue Arbeit wird oben auf alte Arbeit gelegt.",
    "α": "Eingangsgewicht. Diese Zahl bestimmt, wie stark Eingangseinheiten in der Preisformel zählen; in der Simulation ist sie niedriger als das Ausgangsgewicht.",
    "β": "Ausgangsgewicht. Diese Zahl bestimmt, wie stark Ausgangseinheiten in der Preisformel zählen; Output wird hier stärker bewertet als Input.",
    "γ": "Schadensgewicht. Diese Zahl bestimmt, wie stark negativer Ausgang abgezogen wird; gefährlicher Schaden kann dadurch mehr zählen als normale Menge.",
    "GF": "Gemeinfonds. Das ist das öffentliche Konto für Infrastruktur, Bildung, Verifikation, Sicherheit, Ressourcenpflege und gemeinsame Arbeit.",
    "GM": "Geldmenge. Sie beschreibt die umlaufende Arbeitswährung innerhalb der Simulation; sie verändert sich durch öffentliche Ausgabe, Kredit, Rückzahlung und Verbrennung.",
    "T": "Transaktionsabgabe. Sie ist ein kleiner Anteil von Marktzahlungen, der in den Gemeinfonds fließt und gemeinschaftliche Arbeit finanzieren kann.",
    "R": "Ressourcenrente. Sie ist eine Zahlung für knappe oder belastete Naturressourcen; sie soll verhindern, dass natürliche Bestände kostenlos übernutzt werden.",
    "KR": "Kredit. Das ist vorläufig bereitgestellte Arbeitswährung für Produktion oder Forschung; sie muss später durch Verkauf, Output oder Rückzahlung gedeckt werden.",
    "B": "Bestand. Er bezeichnet die vorhandene Menge einer natürlichen Ressource, bevor oder nachdem Regeneration, Entnahme und Schaden verrechnet wurden.",
    "REG": "Regeneration. Sie ist die natürliche oder technische Erholung eines Ressourcenbestands in einer Periode, zum Beispiel Nachwachsen, Nachfüllen oder Pflege.",
    "ENT": "Entnahme. Sie ist die Menge, die aus einem Ressourcenbestand herausgenommen, genutzt oder verbraucht wird.",
    "SCH": "Schaden. Er bezeichnet zusätzliche Belastung, Verschmutzung oder Zerstörung eines Ressourcenbestands, die nicht als normale Entnahme gelten soll.",
}


def explain(ui: UI, title: str, what: str, abbreviations: Sequence[str]) -> None:
    ui.title(title)
    ui.subsection("Was wird simuliert?", fg=231, bg=54)
    ui.wrap(what, indent=2)
    print()
    ui.subsection("Kürzel genau für diesen Simulationsteil", fg=16, bg=190)
    if not abbreviations:
        ui.wrap("In diesem Teil werden keine zusätzlichen Rechenkürzel benutzt.", indent=2)
    for key in abbreviations:
        prefix = "  " + ui.unit(key) + " " + ui.c("=", fg=244) + " "
        plain_prefix_len = len(ui.strip(prefix))
        width = max(48, ui.width - plain_prefix_len - 2)
        wrapped = textwrap.wrap(ABBR[key], width=width) or [""]
        print(prefix + wrapped[0])
        continuation = " " * plain_prefix_len
        for line in wrapped[1:]:
            print(continuation + line)
    print()


# ---------------------------------------------------------------------------
# Modellkern
# ---------------------------------------------------------------------------

@dataclass(frozen=True)
class WorkType:
    name: str
    factor: int
    short: str


WORK_TYPES: List[WorkType] = [
    WorkType("Ackerlandwirtschaft / Basisarbeit", 1, "Acker"),
    WorkType("Flächenarbeit", 2, "Fläche"),
    WorkType("3D-Arbeit / Häuserbau", 3, "3D"),
    WorkType("Zeitkritische Arbeit", 4, "Zeit"),
    WorkType("Kausal wichtige Arbeit", 5, "Kausal"),
    WorkType("Geistige Arbeit", 6, "Geist"),
    WorkType("Kommunikationsarbeit", 7, "Komm"),
    WorkType("Universum in Blöcke zerlegen", 8, "Block"),
    WorkType("Mathematik", 10, "Mathe"),
]


def stacked_factor(factors: Sequence[int]) -> float:
    """Additive Stapelregel: 1 + Summe aller Zusatzwirkungen."""
    if not factors:
        return 1.0
    return 1.0 + sum(float(k) - 1.0 for k in factors)


@dataclass
class WorkBlock:
    ident: int
    actor: str
    label: str
    e: float
    o: float
    factors: List[int]
    q: float
    verified: bool = True
    negative: float = 0.0
    gamma: float = 1.5

    @property
    def m(self) -> float:
        return self.e + self.o

    @property
    def k(self) -> float:
        return stacked_factor(self.factors)

    @property
    def mwir(self) -> float:
        return self.e + self.o - self.gamma * self.negative

    @property
    def aw(self) -> float:
        if not self.verified:
            return 0.0
        return max(0.0, self.mwir) * self.k * self.q


@dataclass
class SimState:
    seed: int
    scenario: str
    blocks: List[WorkBlock] = field(default_factory=list)
    market_total: float = 0.0
    project_stack: float = 0.0
    public_fund: float = 3000.0
    money_supply: float = 20000.0
    public_created: float = 0.0
    taxes: float = 0.0
    resource_rent: float = 0.0
    credit_issued: float = 0.0
    credit_repaid: float = 0.0
    credit_debt: float = 0.0
    damage_debt: float = 0.0
    economy_total_aw: float = 0.0
    verification_rejected: int = 0


@dataclass
class Scenario:
    name: str
    food_s: float
    housing_s: float
    knowledge_s: float
    communication_s: float
    energy_s: float
    public_pressure: float
    credit_success: float
    extraction_pressure: float


def scenario_config(name: str) -> Scenario:
    if name == "krise":
        return Scenario(name, food_s=2.20, housing_s=1.45, knowledge_s=1.25,
                        communication_s=1.85, energy_s=2.10, public_pressure=1.80,
                        credit_success=0.55, extraction_pressure=1.45)
    if name == "forschung":
        return Scenario(name, food_s=0.95, housing_s=1.05, knowledge_s=1.95,
                        communication_s=1.35, energy_s=1.05, public_pressure=1.15,
                        credit_success=0.78, extraction_pressure=0.90)
    if name == "hausbau":
        return Scenario(name, food_s=1.05, housing_s=2.05, knowledge_s=1.25,
                        communication_s=1.20, energy_s=1.25, public_pressure=1.25,
                        credit_success=0.70, extraction_pressure=1.20)
    return Scenario(name, food_s=1.10, housing_s=1.15, knowledge_s=1.20,
                    communication_s=1.10, energy_s=1.05, public_pressure=1.00,
                    credit_success=0.68, extraction_pressure=1.00)


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def jitter(rng: random.Random, base: float, spread: float) -> float:
    return base * (1.0 + rng.uniform(-spread, spread))


# ---------------------------------------------------------------------------
# Simulationsteile
# ---------------------------------------------------------------------------

def part_banner(ui: UI, state: SimState, cfg: Scenario, periods: int) -> None:
    ui.rule("█")
    print(ui.rainbow("  GESTAPELTE ARBEITSBLOCK-WIRTSCHAFT  "))
    ui.rule("█")
    ui.wrap(
        "Diese Datei simuliert eine Arbeitswährung, in der Arbeit als Transformation von Einheiten gezählt wird. "
        "Jeder Abschnitt erklärt direkt über der Rechnung, was gerade simuliert wird. Die farbigen Kürzel werden "
        "immer nur dort erklärt, wo sie tatsächlich im Abschnitt vorkommen.", indent=2)
    print()
    ui.kv("Szenario", ui.c(cfg.name, fg=220, bold=True))
    ui.kv("Perioden im Mehrperiodenteil", ui.c(periods, fg=82, bold=True))
    ui.kv("Zufalls-Seed", ui.c(state.seed, fg=201, bold=True))
    print()


def part_factor_scale(ui: UI) -> None:
    explain(
        ui,
        "1) Wertskala der Arbeitsarten",
        "Die Simulation beginnt mit der festen Ordnung der Arbeitsarten. Hier wird nur die Faktorhöhe gezeigt. "
        "Diese Ordnung ist später die Grundlage für Preisbildung, Projektstapel, Kredite und öffentliche Arbeit.",
        ["K", "3D"],
    )
    rows = []
    for wt in WORK_TYPES:
        rows.append([wt.name, ui.amount(wt.factor, "K", 0)])
    ui.table(["Arbeitsart", "K"], rows, right=[1])
    print()
    ui.wrap("Stapelregel bei mehreren Eigenschaften: 1 plus alle Zusatzwirkungen. Beispiel: Mathematik und Kausalität ergibt 1 + 9 + 4 = 14.", indent=2)


def part_work_blocks(ui: UI, rng: random.Random, state: SimState) -> None:
    explain(
        ui,
        "2) Einzelne Arbeitsblöcke",
        "Hier werden einzelne Arbeiten erzeugt und bewertet. Jede Arbeit hat Eingänge, Ausgänge, Menge, Faktor, Qualität und am Ende eine farbige Gutschrift in Arbeitswährung.",
        ["ID", "E", "O", "M", "K", "Q", "AW"],
    )

    actors = ["Ada", "Bela", "Cem", "Daria", "Elif", "Farid", "Gita"]
    templates = [
        ("Ernte", [1], 22, 85, 0.12),
        ("Flächenplan", [2], 16, 64, 0.10),
        ("Rohbau", [3], 50, 130, 0.16),
        ("Rettungsreparatur", [3, 4, 5], 38, 96, 0.22),
        ("Diagnose", [6, 5], 18, 72, 0.18),
        ("Teamkoordination", [7], 12, 58, 0.15),
        ("Blockmodell", [8], 20, 70, 0.17),
        ("Algorithmus", [10], 15, 78, 0.20),
    ]
    rows = []
    for i in range(1, 13):
        label, factors, base_e, base_o, spread = rng.choice(templates)
        e = jitter(rng, base_e, spread)
        o = jitter(rng, base_o, spread)
        q = clamp(rng.gauss(1.02, 0.18), 0.45, 1.55)
        verified = rng.random() > 0.06
        block = WorkBlock(i, rng.choice(actors), label, e, o, list(factors), q, verified)
        state.blocks.append(block)
        aw_cell = ui.amount(block.aw, "AW") if verified else ui.badge("abgelehnt", 196)
        rows.append([
            ui.amount(block.ident, "ID", 0),
            block.actor,
            label,
            ui.amount(block.e, "E"),
            ui.amount(block.o, "O"),
            ui.amount(block.m, "M"),
            ui.amount(block.k, "K", 1),
            ui.amount(block.q, "Q", 2),
            aw_cell,
        ])
    ui.table(["ID", "Akteur", "Arbeit", "E", "O", "M", "K", "Q", "AW"], rows, right=[3, 4, 5, 6, 7, 8])
    total = sum(b.aw for b in state.blocks)
    print()
    ui.kv("Formel", "%s = (%s + %s) · %s · %s" % (ui.unit("AW"), ui.unit("E"), ui.unit("O"), ui.unit("K"), ui.unit("Q")))
    ui.kv("Summe dieses Teils", ui.amount(total, "AW"))


def part_project_stack(ui: UI, state: SimState) -> None:
    explain(
        ui,
        "3) Projektstapel am Beispiel eines Hauses",
        "Ein Haus entsteht nicht durch eine einzige Arbeit, sondern durch viele Schichten. Dieser Teil stapelt die geprüften Segmentwerte nacheinander zu einem Projektstapel.",
        ["ID", "M", "K", "Q", "AW", "ST"],
    )

    segments = [
        ("S1", "Grundstück rastern", 160, [2, 8], 1.00),
        ("S2", "Fundament gießen", 280, [3], 1.08),
        ("S3", "Rohbau in 3D", 900, [3], 0.96),
        ("S4", "Statik berechnen", 85, [10], 1.22),
        ("S5", "Baukommunikation", 120, [7, 5], 1.10),
        ("S6", "Dach zeitkritisch abdichten", 210, [3, 4], 1.02),
        ("S7", "Endprüfung", 70, [6, 5], 1.00),
    ]
    stack = 0.0
    rows = []
    for sid, name, m, factors, q in segments:
        k = stacked_factor(factors)
        aw = m * k * q
        stack += aw
        rows.append([
            ui.c(sid, fg=250, bold=True),
            name,
            ui.amount(m, "M"),
            ui.amount(k, "K", 1),
            ui.amount(q, "Q", 2),
            ui.amount(aw, "AW"),
            ui.amount(stack, "ST"),
        ])
    state.project_stack = stack
    ui.table(["ID", "Segment", "M", "K", "Q", "AW", "ST"], rows, right=[2, 3, 4, 5, 6])
    print()
    ui.kv("Stapelregel", "%s neu = %s alt + %s" % (ui.unit("ST"), ui.unit("ST"), ui.unit("AW")))
    ui.kv("Projektstapel", ui.amount(stack, "ST"))


@dataclass
class MarketRow:
    name: str
    e: float
    o: float
    k: float
    q: float
    s: float
    p: float


def part_market(ui: UI, cfg: Scenario, state: SimState) -> List[MarketRow]:
    explain(
        ui,
        "4) Marktpreise mit Knappheit",
        "Dieser Teil zeigt, wie aus Eingang, Ausgang, Faktor, Qualität und Knappheit ein Marktpreis entsteht. Der Marktpreis ist nicht identisch mit bloßer Arbeitsmenge, sondern reagiert auf Mangel und Nachfrage.",
        ["α", "β", "E", "O", "K", "Q", "S", "P"],
    )

    alpha = 0.50
    beta = 1.00
    goods_seed = [
        ("Kartoffelkorb", 40, 120, 1, 1.00, cfg.food_s),
        ("Hausmodul", 130, 350, 3, 1.10, cfg.housing_s),
        ("Stromknoten-Reparatur", 25, 80, stacked_factor([3, 4, 5]), 1.04, cfg.energy_s),
        ("Mathe-Algorithmus", 20, 90, 10, 1.22, cfg.knowledge_s),
        ("Teamabstimmung", 15, 60, 7, 1.12, cfg.communication_s),
    ]
    rows: List[List[object]] = []
    market_rows: List[MarketRow] = []
    total = 0.0
    for name, e, o, k, q, s in goods_seed:
        p = (alpha * e + beta * o) * k * q * s
        total += p
        market_rows.append(MarketRow(name, e, o, k, q, s, p))
        rows.append([
            name,
            ui.amount(e, "E"),
            ui.amount(o, "O"),
            ui.amount(k, "K", 1),
            ui.amount(q, "Q", 2),
            ui.amount(s, "S", 2) + " " + ui.heat(s),
            ui.amount(p, "P"),
        ])
    state.market_total = total
    ui.kv("Formel", "%s = (%s·%s + %s·%s) · %s · %s · %s" % (
        ui.unit("P"), ui.unit("α"), ui.unit("E"), ui.unit("β"), ui.unit("O"), ui.unit("K"), ui.unit("Q"), ui.unit("S")))
    ui.kv("Parameter", "%s = %s, %s = %s" % (ui.unit("α"), ui.c(alpha, fg=39, bold=True), ui.unit("β"), ui.c(beta, fg=77, bold=True)))
    print()
    ui.table(["Gut", "E", "O", "K", "Q", "S", "P"], rows, right=[1, 2, 3, 4, 5, 6])
    print()
    ui.kv("Marktumsatz dieses Teils", ui.amount(total, "P"))
    return market_rows


def part_public_fund(ui: UI, cfg: Scenario, state: SimState) -> None:
    explain(
        ui,
        "5) Gemeinfonds und öffentliche Geldsteuerung",
        "Jetzt wird simuliert, wie ein öffentlicher Fonds Einnahmen aus Marktaktivität und Ressourcennutzung erhält. Danach bezahlt er gemeinsame Arbeit. Wenn die Auszahlung größer ist als die Einnahmen, entsteht neue Arbeitswährung; wenn Überschuss zurückfließt, kann Arbeitswährung verbrannt werden.",
        ["T", "R", "GF", "AW", "GM"],
    )

    start_gf = state.public_fund
    start_gm = state.money_supply
    t = 0.05 * state.market_total
    r = 180.0 * cfg.extraction_pressure + 35.0 * cfg.energy_s
    public_work = 780.0 * cfg.public_pressure
    created = max(0.0, public_work - t - r)
    burned = max(0.0, (t + r - public_work) * 0.35)
    state.taxes += t
    state.resource_rent += r
    state.public_created += created
    state.public_fund = start_gf + t + r - public_work
    state.money_supply = start_gm + created - burned

    rows = [
        ["Start", "öffentlicher Kontostand", "", ui.amount(start_gf, "GF"), ui.amount(start_gm, "GM")],
        ["Einnahme", "Marktabgabe", ui.amount(t, "T"), ui.amount(start_gf + t, "GF"), ui.amount(start_gm, "GM")],
        ["Einnahme", "Ressourcennutzung", ui.amount(r, "R"), ui.amount(start_gf + t + r, "GF"), ui.amount(start_gm, "GM")],
        ["Ausgabe", "gemeinsame Arbeit", ui.amount(-public_work, "AW", signed=True), ui.amount(state.public_fund, "GF"), ui.amount(start_gm, "GM")],
        ["Steuerung", "neu erzeugt", ui.amount(created, "AW"), ui.amount(state.public_fund, "GF"), ui.amount(start_gm + created, "GM")],
        ["Steuerung", "verbrannt", ui.amount(-burned, "AW", signed=True), ui.amount(state.public_fund, "GF"), ui.amount(state.money_supply, "GM")],
    ]
    ui.table(["Art", "Vorgang", "Betrag", "GF", "GM"], rows, right=[2, 3, 4])
    print()
    ui.kv("Ergebnis", "%s ist jetzt %s; %s ist jetzt %s" % (ui.unit("GF"), ui.amount(state.public_fund, "GF"), ui.unit("GM"), ui.amount(state.money_supply, "GM")))


def part_credit(ui: UI, rng: random.Random, cfg: Scenario, state: SimState) -> None:
    explain(
        ui,
        "6) Produktionskredit und Lagerware",
        "Dieser Teil simuliert Ware, die produziert wird, bevor ein Käufer feststeht. Dafür wird Kredit ausgegeben. Bei erfolgreichem Verkauf wird der Kredit zurückgezahlt und der Hauptbetrag aus dem Umlauf genommen; bei Misserfolg bleibt Schuld stehen.",
        ["KR", "Q", "P", "AW"],
    )

    products = [
        ("Werkzeuglager", 620.0, 1.04),
        ("Lernsoftware", 480.0, 1.18),
        ("Bauziegel-Serie", 760.0, 0.96),
        ("Sensorpaket", 540.0, 1.09),
    ]
    rows = []
    for name, kr_base, q_base in products:
        kr = jitter(rng, kr_base, 0.12)
        q = clamp(jitter(rng, q_base, 0.10), 0.60, 1.45)
        success = rng.random() < cfg.credit_success
        state.credit_issued += kr
        state.money_supply += kr
        if success:
            p = kr * (1.10 + 0.20 * q + rng.uniform(0.00, 0.18))
            repayment = min(kr, p * 0.80)
            gain = p - repayment
            state.credit_repaid += repayment
            state.money_supply -= repayment
            outcome = ui.badge("verkauft", 82)
            result_aw = ui.amount(gain, "AW")
        else:
            p = 0.0
            debt = kr * rng.uniform(0.65, 0.95)
            state.credit_debt += debt
            outcome = ui.badge("Lagerverlust", 196)
            result_aw = ui.amount(-debt, "AW", signed=True)
        rows.append([
            name,
            ui.amount(kr, "KR"),
            ui.amount(q, "Q"),
            ui.amount(p, "P"),
            outcome,
            result_aw,
        ])
    ui.table(["Produkt", "KR", "Q", "P", "Ergebnis", "AW"], rows, right=[1, 2, 3, 5])
    print()
    ui.kv("Kredit ausgegeben", ui.amount(state.credit_issued, "KR"))
    ui.kv("Kredit zurückgezahlt", ui.amount(state.credit_repaid, "KR"))
    ui.kv("Offene Schuld", ui.amount(state.credit_debt, "AW"))


def part_resources(ui: UI, rng: random.Random, cfg: Scenario, state: SimState, periods: int) -> None:
    explain(
        ui,
        "7) Ressourcenbestand und ökologische Rückkopplung",
        "Dieser Teil simuliert eine natürliche Ressource. Der Bestand sinkt durch Entnahme und Schaden, erholt sich durch Regeneration und erzeugt bei Übernutzung eine Ressourcenrente.",
        ["B", "REG", "ENT", "SCH", "R"],
    )

    b = 1000.0
    rows = []
    local_r = 0.0
    for t in range(1, periods + 1):
        reg = jitter(rng, 34.0, 0.18)
        ent = jitter(rng, 48.0 * cfg.extraction_pressure, 0.22)
        sch = max(0.0, jitter(rng, 9.0 * cfg.extraction_pressure, 0.35))
        overuse = max(0.0, ent + sch - reg)
        r = overuse * (2.8 + 0.03 * max(0.0, 1000.0 - b))
        b_new = max(0.0, b + reg - ent - sch)
        local_r += r
        rows.append([
            str(t),
            ui.amount(b, "B"),
            ui.amount(reg, "REG"),
            ui.amount(ent, "ENT"),
            ui.amount(sch, "SCH"),
            ui.amount(r, "R"),
            ui.amount(b_new, "B"),
            ui.heat((ent + sch) / max(1.0, reg), low=0.9, high=2.0),
        ])
        b = b_new
    state.resource_rent += local_r
    ui.kv("Bestandsformel", "%s neu = %s alt + %s - %s - %s" % (ui.unit("B"), ui.unit("B"), ui.unit("REG"), ui.unit("ENT"), ui.unit("SCH")))
    print()
    ui.table(["Periode", "B alt", "REG", "ENT", "SCH", "R", "B neu", "Lage"], rows, right=[1, 2, 3, 4, 5, 6])
    print()
    ui.kv("Ressourcenrente dieses Teils", ui.amount(local_r, "R"))


def part_negative_work(ui: UI, state: SimState) -> None:
    explain(
        ui,
        "8) Negative Arbeit und Schadensabzug",
        "Dieser Teil zeigt, dass viel Aufwand nicht automatisch guten Wert erzeugt. Positive Ausgänge werden gezählt, negative Ausgänge werden mit einem Schadensgewicht abgezogen. Wird die wirksame Menge negativ, entsteht Schuld statt Belohnung.",
        ["E", "O+", "O-", "γ", "Mwir", "K", "Q", "AW"],
    )

    cases = [
        ("Fehlerhafte Statik", 40.0, 15.0, 90.0, 1.70, 10.0, 0.20),
        ("Meeting ohne Entscheidung", 10.0, 5.0, 12.0, 1.00, 7.0, 0.50),
        ("Umweltreparatur", 30.0, 80.0, 5.0, 1.50, 5.0, 1.10),
        ("Korrigierte Landkarte", 22.0, 70.0, 8.0, 1.30, 8.0, 1.15),
    ]
    rows = []
    for name, e, op, om, gamma, k, q in cases:
        mwir = e + op - gamma * om
        aw = max(0.0, mwir) * k * q
        debt = max(0.0, -mwir) * k
        state.damage_debt += debt
        rows.append([
            name,
            ui.amount(e, "E"),
            ui.amount(op, "O+"),
            ui.amount(om, "O-"),
            ui.amount(gamma, "γ"),
            ui.amount(mwir, "Mwir", signed=True),
            ui.amount(k, "K", 1),
            ui.amount(q, "Q"),
            ui.amount(aw, "AW"),
            ui.amount(-debt, "AW", signed=True) if debt else ui.c("0", fg=82, bold=True),
        ])
    ui.kv("Formel", "%s = %s + %s - %s·%s" % (ui.unit("Mwir"), ui.unit("E"), ui.unit("O+"), ui.unit("γ"), ui.unit("O-")))
    print()
    ui.table(["Fall", "E", "O+", "O-", "γ", "Mwir", "K", "Q", "AW", "Schuld"], rows, right=[1, 2, 3, 4, 5, 6, 7, 8, 9])
    print()
    ui.kv("Schuld aus Schäden", ui.amount(state.damage_debt, "AW"))


def part_period_economy(ui: UI, rng: random.Random, cfg: Scenario, state: SimState, periods: int) -> None:
    explain(
        ui,
        "9) Mehrperioden-Wirtschaft mit Sektoren",
        "Hier laufen mehrere Wirtschaftsperioden. Jeder Sektor produziert Arbeit, bekommt einen Preis, zahlt eine Transaktionsabgabe und verändert damit Gemeinfonds und Geldmenge. Knappheit beeinflusst die Preise und lockt in der nächsten Runde mehr Produktion an.",
        ["K", "Q", "S", "AW", "P", "T", "GF", "GM"],
    )

    sectors = {
        "Nahrung": {"k": 1.0, "m": 160.0, "scarcity": cfg.food_s, "demand": 500.0, "supply": 470.0},
        "Wohnen": {"k": 3.0, "m": 260.0, "scarcity": cfg.housing_s, "demand": 300.0, "supply": 260.0},
        "Wissen": {"k": 10.0, "m": 95.0, "scarcity": cfg.knowledge_s, "demand": 220.0, "supply": 180.0},
        "Kommunikation": {"k": 7.0, "m": 110.0, "scarcity": cfg.communication_s, "demand": 260.0, "supply": 240.0},
    }

    for period in range(1, periods + 1):
        print()
        ui.subsection("Periode %d" % period, fg=16, bg=45)
        rows = []
        period_aw = 0.0
        period_p = 0.0
        period_t = 0.0
        for name, x in sectors.items():
            # Nachfrage und Angebot ändern sich leicht.
            x["demand"] = max(30.0, x["demand"] * (1.0 + rng.uniform(-0.05, 0.09)))
            raw_s = (x["demand"] / max(1.0, x["supply"])) * x["scarcity"]
            s = clamp(raw_s, 0.65, 3.20)
            q = clamp(rng.gauss(1.03, 0.13), 0.70, 1.45)
            k = float(x["k"])
            m = x["m"] * (1.0 + 0.12 * (s - 1.0))
            aw = m * k * q
            p = aw * (0.72 + 0.28 * s)
            t = 0.05 * p
            state.public_fund += t
            state.taxes += t
            period_aw += aw
            period_p += p
            period_t += t
            # Produktion reagiert: Bei Knappheit steigt Angebot, bei Überangebot langsamer.
            production_push = 0.10 + 0.12 * max(0.0, s - 1.0)
            x["supply"] = max(10.0, x["supply"] * 0.88 + m * production_push + rng.uniform(-8, 12))
            rows.append([
                name,
                ui.amount(k, "K", 1),
                ui.amount(q, "Q"),
                ui.amount(s, "S"),
                ui.heat(s),
                ui.amount(aw, "AW"),
                ui.amount(p, "P"),
                ui.amount(t, "T"),
            ])
        # Öffentliche Stabilisierung: in Krisenperioden werden gemeinsame Arbeiten bezahlt.
        emergency = max(0.0, (cfg.public_pressure - 1.0) * 120.0 + (period_p / 8000.0) * 35.0)
        if emergency > state.public_fund:
            created = emergency - state.public_fund
            state.money_supply += created
            state.public_created += created
            state.public_fund = 0.0
        else:
            state.public_fund -= emergency
        state.economy_total_aw += period_aw
        print("  " + ui.c("Sektorrechnung", fg=229, bold=True) + "  " +
              ui.c("GF", fg=51, bold=True) + "=" + ui.amount(state.public_fund, "GF") + "  " +
              ui.c("GM", fg=226, bold=True) + "=" + ui.amount(state.money_supply, "GM"))
        ui.table(["Sektor", "K", "Q", "S", "Lage", "AW", "P", "T"], rows, right=[1, 2, 3, 5, 6, 7])
        if emergency > 0:
            ui.kv("öffentliche Stabilisierung", ui.amount(emergency, "AW"))
    print()
    ui.kv("Summe der Sektorarbeit", ui.amount(state.economy_total_aw, "AW"))


def part_verification(ui: UI, state: SimState) -> None:
    explain(
        ui,
        "10) Prüfung gegen Faktorbetrug",
        "Dieser Teil simuliert Prüffälle. Akteure behaupten einen hohen Faktor, aber die Prüfung kann den Faktor oder die Qualität senken. Abgelehnte oder entwertete Arbeit erzeugt weniger Arbeitswährung.",
        ["ID", "M", "K", "Q", "AW"],
    )

    claims = [
        ("V1", "korrekter Algorithmus", 60.0, 10.0, 10.0, 1.20),
        ("V2", "Meeting ohne Empfängerwirkung", 35.0, 7.0, 1.0, 0.00),
        ("V3", "künstlich erzeugter Notfall", 42.0, 4.0, 1.0, 0.70),
        ("V4", "Lieferkette sauber kartiert", 55.0, 8.0, 8.0, 1.12),
        ("V5", "falscher Beweis", 50.0, 10.0, 1.0, 0.00),
        ("V6", "echte Engpassdiagnose", 45.0, 5.0, 5.0, 1.18),
    ]
    rows = []
    for ident, name, m, claim_k, checked_k, q in claims:
        aw = m * checked_k * q
        if checked_k < claim_k or q <= 0.0:
            state.verification_rejected += 1
            status = ui.badge("gekürzt", 208) if q > 0 else ui.badge("abgelehnt", 196)
        else:
            status = ui.badge("bestätigt", 82)
        rows.append([
            ui.c(ident, fg=250, bold=True),
            name,
            ui.amount(m, "M"),
            ui.amount(claim_k, "K", 1),
            ui.amount(checked_k, "K", 1),
            ui.amount(q, "Q"),
            ui.amount(aw, "AW"),
            status,
        ])
    ui.table(["ID", "Prüffall", "M", "behauptet K", "geprüft K", "Q", "AW", "Status"], rows, right=[2, 3, 4, 5, 6])
    print()
    ui.kv("gekürzte oder abgelehnte Fälle", ui.c(state.verification_rejected, fg=208, bold=True))


def part_final_summary(ui: UI, state: SimState) -> None:
    explain(
        ui,
        "11) Schlussübersicht der Simulation",
        "Am Ende werden die wichtigsten Konten und Stapelwerte zusammengeführt. Die Übersicht zeigt, wie stark Arbeit, Projekte, öffentliche Steuerung, Ressourcen und Kredite das System bewegt haben.",
        ["AW", "ST", "GF", "GM", "T", "R", "KR"],
    )

    block_aw = sum(b.aw for b in state.blocks)
    total_aw_like = block_aw + state.project_stack + state.economy_total_aw
    rows = [
        ["Arbeitsblöcke", ui.amount(block_aw, "AW"), "aus Einzelarbeiten"],
        ["Projektstapel", ui.amount(state.project_stack, "ST"), "Haus als gestapelter Wert"],
        ["Sektorarbeit", ui.amount(state.economy_total_aw, "AW"), "Mehrperioden-Wirtschaft"],
        ["Arbeitswert gesamt", ui.amount(total_aw_like, "AW"), "ohne doppelte Altzählung"],
        ["Gemeinfonds", ui.amount(state.public_fund, "GF"), "öffentliches Restkonto"],
        ["Geldmenge", ui.amount(state.money_supply, "GM"), "umlaufende Arbeitswährung"],
        ["Transaktionsabgaben", ui.amount(state.taxes, "T"), "öffentlich eingesammelt"],
        ["Ressourcenrenten", ui.amount(state.resource_rent, "R"), "aus Naturbelastung"],
        ["Kredit ausgegeben", ui.amount(state.credit_issued, "KR"), "vorläufige Finanzierung"],
        ["Kredit offen", ui.amount(state.credit_debt, "AW"), "Schuld aus Lagerverlust"],
        ["Schadensschuld", ui.amount(state.damage_debt, "AW"), "negative Arbeit"],
    ]
    ui.table(["Größe", "Wert", "Bedeutung"], rows, right=[1])
    print()
    ui.subsection("Lesart", fg=16, bg=220)
    ui.wrap(
        "Die Simulation zeigt keine perfekte echte Volkswirtschaft. Sie ist ein spielbares Rechenmodell: Arbeit wird segmentiert, "
        "bewertet, geprüft, bezahlt, gestapelt und durch Knappheit, Kredit, Gemeinfonds, Ressourcen und Schaden rückgekoppelt. "
        "Wer das Modell erweitert, sollte vor allem die Verifikation und die Vermeidung doppelter Zählung hart lassen; sonst wird die Währung aufgeblasen.",
        indent=2,
    )


# ---------------------------------------------------------------------------
# Steuerung
# ---------------------------------------------------------------------------

PARTS = {
    "faktoren": part_factor_scale,
    "arbeit": part_work_blocks,
    "projekt": part_project_stack,
    "markt": part_market,
    "fonds": part_public_fund,
    "kredit": part_credit,
    "ressourcen": part_resources,
    "schaden": part_negative_work,
    "perioden": part_period_economy,
    "pruefung": part_verification,
    "schluss": part_final_summary,
}

DEFAULT_ORDER = [
    "faktoren", "arbeit", "projekt", "markt", "fonds", "kredit",
    "ressourcen", "schaden", "perioden", "pruefung", "schluss",
]

SHORT_ORDER = ["faktoren", "arbeit", "markt", "schluss"]


def parse_parts(value: str) -> List[str]:
    value = (value or "alle").strip().lower()
    if value in ("alle", "voll", "full"):
        return list(DEFAULT_ORDER)
    if value in ("kurz", "short"):
        return list(SHORT_ORDER)
    result = []
    for raw in value.split(","):
        key = raw.strip().lower()
        if not key:
            continue
        if key not in PARTS:
            raise SystemExit("Unbekannter Teil '%s'. Erlaubt: %s" % (key, ", ".join(DEFAULT_ORDER)))
        result.append(key)
    # Schluss nur dann automatisch ergänzen, wenn mehr als ein Teil läuft und Schluss nicht schon vorhanden ist.
    if len(result) > 1 and "schluss" not in result:
        result.append("schluss")
    return result


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Bunte PyPy3-Simulation der Gestapelten Arbeitsblock-Wirtschaft.",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--szenario", choices=["normal", "krise", "forschung", "hausbau"], default="normal",
                        help="wirtschaftliche Ausgangslage")
    parser.add_argument("--perioden", type=int, default=6,
                        help="Anzahl der Perioden im Mehrperioden- und Ressourcenteil")
    parser.add_argument("--seed", type=int, default=42,
                        help="Zufalls-Seed für reproduzierbare Ergebnisse")
    parser.add_argument("--teile", default="alle",
                        help="alle, kurz oder Kommaliste: faktoren,arbeit,projekt,markt,fonds,kredit,ressourcen,schaden,perioden,pruefung,schluss")
    parser.add_argument("--breite", type=int, default=None,
                        help="Terminalbreite für Tabellen und Umbruch")
    parser.add_argument("--no-color", action="store_true",
                        help="ANSI-Farben deaktivieren")
    return parser


def run(args: argparse.Namespace) -> None:
    color_enabled = (not args.no_color) and (os.environ.get("NO_COLOR") is None)
    ui = UI(color=color_enabled, width=args.breite)
    rng = random.Random(args.seed)
    cfg = scenario_config(args.szenario)
    periods = max(1, min(50, int(args.perioden)))
    state = SimState(seed=args.seed, scenario=args.szenario)

    parts = parse_parts(args.teile)
    part_banner(ui, state, cfg, periods)

    market_rows: Optional[List[MarketRow]] = None
    for part in parts:
        if part == "faktoren":
            part_factor_scale(ui)
        elif part == "arbeit":
            part_work_blocks(ui, rng, state)
        elif part == "projekt":
            part_project_stack(ui, state)
        elif part == "markt":
            market_rows = part_market(ui, cfg, state)
        elif part == "fonds":
            if state.market_total <= 0.0:
                # Der Fonds braucht einen Umsatz. Wenn der Marktteillauf ausgelassen wurde,
                # wird ein kleiner Standardumsatz angesetzt, ohne zusätzliche Kürzel auszugeben.
                state.market_total = 2500.0
            part_public_fund(ui, cfg, state)
        elif part == "kredit":
            part_credit(ui, rng, cfg, state)
        elif part == "ressourcen":
            part_resources(ui, rng, cfg, state, periods)
        elif part == "schaden":
            part_negative_work(ui, state)
        elif part == "perioden":
            part_period_economy(ui, rng, cfg, state, periods)
        elif part == "pruefung":
            part_verification(ui, state)
        elif part == "schluss":
            part_final_summary(ui, state)

    print()
    ui.rule("█")
    print(ui.rainbow("  ENDE DER SIMULATION  "))
    ui.rule("█")


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    try:
        run(args)
    except KeyboardInterrupt:
        print("\nAbgebrochen.", file=sys.stderr)
        return 130
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
