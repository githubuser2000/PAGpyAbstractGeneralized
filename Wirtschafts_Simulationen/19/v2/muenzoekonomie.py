#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
MÜNZÖKONOMIE – ausschließlich bunte UTF-8-Art-Simulation in PyPy3.

Der vollständige ökonomische Kern liegt in `muenzoekonomie_core.py`.
Dieses Hauptprogramm führt die Simulation aus, zeigt aber im normalen Lauf nur
bunte UTF-8-Art-Diagramme. Zu jeder Darstellung stehen direkt darüber:

1. warum simuliert wird,
2. was simuliert wird,
3. nur die Abkürzungen, die in genau dieser UTF-8-Art vorkommen.

Direkt unter jeder UTF-8-Art steht die Auswertung des jeweiligen Ergebnisses.
Keine Fortschrittszeilen, keine CSV-/JSON-Tabellen im Standardlauf, keine normale
Konsolenstatistik. Nur Standardbibliothek, PyPy3-kompatibel.

Beispiel:
    pypy3 muenzoekonomie.py --years 20 --households 120 --firms-per-category 2 --seed 42

Optional kann dieselbe UTF-8-Art als Text gespeichert werden:
    pypy3 muenzoekonomie.py --out ergebnis
"""

from __future__ import print_function

import argparse
import os
import sys
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

# Reexport für bestehende Tests und für Nutzer, die den Kern importieren möchten.
from muenzoekonomie_core import *  # noqa: F401,F403
from muenzoekonomie_core import CATEGORY_INFO, Economy, clamp, safe_div

VERSION = "2.0.0-utf8-art"

RAINBOW = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]
HEAT = ["🟦", "🟪", "🟩", "🟨", "🟧", "🟥"]
GOOD = ["🟥", "🟧", "🟨", "🟩", "🟩", "🟦"]
BAD = ["🟦", "🟩", "🟨", "🟧", "🟥", "🟥"]
SPARKS = "▁▂▃▄▅▆▇█"


# ---------------------------------------------------------------------------
# UTF-8-Art-Helfer
# ---------------------------------------------------------------------------


def _to_float(x: Any, default: float = 0.0) -> float:
    try:
        return float(x)
    except Exception:
        return default


def _fmt_money(x: float) -> str:
    sign = "−" if x < 0 else ""
    x = abs(float(x))
    if x >= 1_000_000:
        return "%s%.2fM" % (sign, x / 1_000_000.0)
    if x >= 10_000:
        return "%s%.1fk" % (sign, x / 1_000.0)
    if x >= 1_000:
        return "%s%.2fk" % (sign, x / 1_000.0)
    return "%s%.1f" % (sign, x)


def _fmt_pct(x: float) -> str:
    return "%+.2f%%" % (100.0 * float(x))


def _fmt_unit(x: float) -> str:
    return "%.3f" % float(x)


def _short(s: str, n: int) -> str:
    if len(s) <= n:
        return s
    if n <= 1:
        return s[:n]
    return s[: n - 1] + "…"


def _wrap(text: str, width: int = 96) -> List[str]:
    words = str(text).replace("\n", " ").split()
    if not words:
        return [""]
    lines: List[str] = []
    cur: List[str] = []
    cur_len = 0
    for word in words:
        add = len(word) + (1 if cur else 0)
        if cur and cur_len + add > width:
            lines.append(" ".join(cur))
            cur = [word]
            cur_len = len(word)
        else:
            cur.append(word)
            cur_len += add
    if cur:
        lines.append(" ".join(cur))
    return lines


def _bar(value: float, maximum: float = 1.0, width: int = 22, palette: Sequence[str] = RAINBOW) -> str:
    maximum = max(1e-9, float(maximum))
    ratio = clamp(float(value) / maximum, 0.0, 1.0)
    filled = int(round(ratio * width))
    blocks: List[str] = []
    for i in range(filled):
        blocks.append(palette[i % len(palette)])
    blocks.extend(["⬛"] * max(0, width - filled))
    return "".join(blocks)


def _sparkline(values: Sequence[float], width: int = 54) -> str:
    values = list(values)
    if not values:
        return ""
    if len(values) > width:
        step = float(len(values)) / float(width)
        sampled: List[float] = []
        for i in range(width):
            a = int(i * step)
            b = max(a + 1, int((i + 1) * step))
            sampled.append(sum(values[a:b]) / float(max(1, b - a)))
        values = sampled
    lo, hi = min(values), max(values)
    rng = hi - lo
    out = []
    for v in values:
        if rng <= 1e-12:
            idx = 3
        else:
            idx = int(round((v - lo) / rng * (len(SPARKS) - 1)))
        idx = max(0, min(len(SPARKS) - 1, idx))
        out.append(SPARKS[idx])
    return "".join(out)


def _header_block(title: str, why: str, what: str, abbreviations: Sequence[Tuple[str, str]]) -> List[str]:
    line = "═" * 104
    out = ["🌈╔%s╗🌈" % line]
    out.append("🪙║ %s" % title)
    for prefix, text in [("🟣╟─ Warum: ", why), ("🔵╟─ Was: ", what)]:
        wrapped = _wrap(text, 96)
        for i, part in enumerate(wrapped):
            out.append((prefix if i == 0 else "  ║        ") + part)
    if abbreviations:
        parts = ["%s=%s" % (a, b) for a, b in abbreviations]
        wrapped = _wrap("; ".join(parts), 96)
        for i, part in enumerate(wrapped):
            out.append(("🟢╟─ Abkürzungen: " if i == 0 else "🟢║                 ") + part)
    else:
        out.append("🟢╟─ Abkürzungen: keine")
    out.append("🌈╚%s╝🌈" % line)
    return out


def _evaluation_block(text: str) -> List[str]:
    line = "═" * 104
    out = ["🧾╔%s╗🧾" % line]
    wrapped = _wrap(text, 98)
    for i, part in enumerate(wrapped):
        out.append(("🧾║ Auswertung: " if i == 0 else "🧾║             ") + part)
    out.append("🧾╚%s╝🧾" % line)
    return out


def _section(title: str, why: str, what: str, abbreviations: Sequence[Tuple[str, str]], art: Sequence[str], evaluation: str) -> str:
    lines: List[str] = []
    lines.extend(_header_block(title, why, what, abbreviations))
    lines.append("")
    lines.extend(list(art))
    lines.append("")
    lines.extend(_evaluation_block(evaluation))
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Renderer
# ---------------------------------------------------------------------------


class Utf8ArtRenderer(object):
    def __init__(self, economy: Economy, periods: int) -> None:
        self.eco = economy
        self.periods = periods

    def last(self) -> Dict[str, Any]:
        return self.eco.metrics[-1] if self.eco.metrics else {}

    def first(self) -> Dict[str, Any]:
        return self.eco.metrics[0] if self.eco.metrics else {}

    def metric_series(self, key: str) -> List[float]:
        return [_to_float(m.get(key, 0.0)) for m in self.eco.metrics]

    def category_metric(self, key: str) -> Dict[int, float]:
        last = self.last()
        raw = last.get(key, {}) if last else {}
        return {k: _to_float(raw.get(str(k), 0.0)) for k in CATEGORY_INFO}

    def top_categories(self, key: str, n: int = 6) -> List[Tuple[int, float]]:
        data = self.category_metric(key)
        pairs = sorted(data.items(), key=lambda kv: kv[1], reverse=True)
        return pairs[:n]

    def trend_word(self, key: str) -> Tuple[str, float]:
        first = _to_float(self.first().get(key, 0.0))
        last = _to_float(self.last().get(key, 0.0))
        diff = last - first
        if abs(diff) < 1e-9:
            return "gleich geblieben", diff
        return ("gestiegen" if diff > 0 else "gesunken"), diff

    # ------------------------------------------------------------------
    # 01 Gesamtsiegel
    # ------------------------------------------------------------------

    def art_overview(self) -> str:
        last = self.last()
        bmp = _to_float(last.get("bmp", 0.0))
        mw = _to_float(last.get("mw", 0.0))
        inf = _to_float(last.get("inflation", 0.0))
        alq = _to_float(last.get("unemployment", 0.0))
        nat = _to_float(last.get("nature_capital", 0.0))
        ris = _to_float(last.get("systemic_risk", 0.0))
        mw_trend, mw_diff = self.trend_word("mw")
        max_money = max(1.0, abs(bmp), abs(mw))
        art = [
            "                         🟥🟧🟨🟩🟦🟪  M Ü N Z Ö K O N O M I E  🟪🟦🟩🟨🟧🟥",
            "                  ╭────────────────────────────── 🪙 ──────────────────────────────╮",
            "                  │                         ╭──────────────╮                       │",
            "                  │             🧠 K17 ───▶ │   MÜNZKERN   │ ◀─── K18 💞           │",
            "                  │                         ╰──────┬───────╯                       │",
            "                  │                                │                               │",
            "                  │        K01 🔎 ─▶ K04 🏭 ─▶ K08 🖼️ ─▶ K10 🛒 ─▶ K19 🌭        │",
            "                  ╰────────────────────────────────┼───────────────────────────────╯",
            "                                                   │",
            "      BMP " + _bar(abs(bmp), max_money, 22, RAINBOW) + " " + _fmt_money(bmp),
            "       MW " + _bar(abs(mw), max_money, 22, RAINBOW) + " " + _fmt_money(mw),
            "      INF " + _bar(abs(inf), 0.15, 22, BAD) + " " + _fmt_pct(inf),
            "      ALQ " + _bar(alq, 1.0, 22, BAD) + " " + _fmt_pct(alq),
            "      NAT " + _bar(nat, 1.15, 22, GOOD) + " " + _fmt_unit(nat),
            "      RIS " + _bar(ris, 1.0, 22, BAD) + " " + _fmt_unit(ris),
        ]
        evaluation = (
            "Das Gesamtsiegel zeigt die letzte Periode nach %d Simulationsperioden. Der Münzwohlstand ist gegenüber dem Start %s (%s), "
            "während das Brutto-Münzprodukt bei %s liegt. Entscheidend ist die Kombination: hoher MW bei niedriger RIS und tragfähiger NAT bedeutet, dass nicht nur Umsatz, sondern Zielnutzen entsteht."
            % (self.periods, mw_trend, _fmt_money(mw_diff), _fmt_money(bmp))
        )
        return _section(
            "🪙 UTF-8-Art 01 · Gesamtsiegel der Münzökonomie",
            "Ein Wirtschaftssystem braucht zuerst einen Gesamtblick, sonst sieht man nur Einzelteile.",
            "Gezeigt werden Produktion, Münzwohlstand, Inflation, Arbeitslosigkeit, Natur und Risiko im Endzustand.",
            [
                ("BMP", "Brutto-Münzprodukt"),
                ("MW", "Münzwohlstand"),
                ("INF", "Inflation"),
                ("ALQ", "Arbeitslosenquote"),
                ("NAT", "Naturkapital"),
                ("RIS", "systemisches Risiko"),
                ("K01", "Expression extrahieren"),
                ("K04", "materielle Produktion"),
                ("K08", "fertiges Objekt"),
                ("K10", "Markt/Galerie"),
                ("K17", "Meta-Intelligenz"),
                ("K18", "Solidarität/Wertschätzung"),
                ("K19", "Ziel-Ergebnis"),
            ],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 02 Sektoren-Heatmap
    # ------------------------------------------------------------------

    def art_sector_heatmap(self) -> str:
        output = self.category_metric("category_output")
        max_out = max([1.0] + list(output.values()))
        top = self.top_categories("category_output", 5)
        art: List[str] = []
        art.append("       19-KATEGORIEN-OUTPUT-HEATMAP")
        art.append("       ╭────────────────────────────────────────────────────────────────────────╮")
        for start in [1, 6, 11, 16]:
            row = []
            for k in range(start, min(start + 5, 20)):
                v = output.get(k, 0.0)
                row.append("K%02d %s %6.1f" % (k, _bar(v, max_out, 7, HEAT), v))
            art.append("       │ " + "  ".join(row))
        art.append("       ╰────────────────────────────────────────────────────────────────────────╯")
        art.append("")
        art.append("       TOP: " + "   ".join(["K%02d=%s" % (k, _fmt_money(v)) for k, v in top]))
        evaluation = (
            "Der stärkste Output-Sektor ist K%02d (%s) mit %.1f Einheiten. Die Heatmap zeigt nicht Moral, sondern Produktionsdruck und reale Aktivität: dunkle Felder sind aktuell knapp, nachfrageschwach oder ressourcenbegrenzt."
            % (top[0][0], CATEGORY_INFO[top[0][0]]["short"], top[0][1])
        )
        return _section(
            "🌡️ UTF-8-Art 02 · 19-Sektoren-Heatmap",
            "Die 19 Kategorien sollen nicht nur Begriffe sein, sondern als Wirtschaftssektoren messbar werden.",
            "Gezeigt wird der erzeugte Output jeder Kategorie in der letzten Periode.",
            [("Kxx", "Kategorie xx"), ("OUT", "Outputmenge; als Zahl hinter jedem Balken")],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 03 Marktgalerie
    # ------------------------------------------------------------------

    def art_market_gallery(self) -> str:
        top = self.top_categories("category_turnover", 8)
        art = ["       ╭─────────────── MARKTGALERIE: Angebot trifft Bedürfnis ───────────────╮"]
        shortage_values: List[float] = []
        for k, turnover in top:
            d = self.eco.market.demand.get(k, 0.0)
            s = self.eco.market.supply.get(k, 0.0)
            v = self.eco.market.sold.get(k, 0.0)
            p = self.eco.market.prices.get(k, CATEGORY_INFO[k]["base_price"])
            m = max(1.0, d, s, v)
            shortage_values.append(safe_div(max(0.0, d - v), max(1.0, d), 0.0))
            art.append(
                "       │ K%02d %-20s D %s S %s V %s P %6.1f U %s"
                % (k, _short(CATEGORY_INFO[k]["short"], 20), _bar(d, m, 8, RAINBOW), _bar(s, m, 8, GOOD), _bar(v, m, 8, HEAT), p, _fmt_money(turnover))
            )
        art.append("       ╰────────────────────────────────────────────────────────────────────────╯")
        shortage = safe_div(sum(shortage_values), len(shortage_values), 0.0)
        evaluation = (
            "In den umsatzstärksten Märkten bleiben durchschnittlich %.1f%% der Nachfrage ungedeckt. Viel D bei wenig V bedeutet Engpass; viel S bei wenig V bedeutet Überangebot oder falsche Zuordnung."
            % (100.0 * shortage)
        )
        return _section(
            "🛒 UTF-8-Art 03 · Marktgalerie",
            "Märkte sind in diesem System Galerien: Sie machen Münzen sichtbar und ordnen sie Bedürfnissen zu.",
            "Gezeigt werden die umsatzstärksten Kategorien mit Nachfrage, Angebot, Verkäufen, Preis und Umsatz.",
            [("D", "Nachfrage"), ("S", "Angebot"), ("V", "verkauft"), ("P", "Preis"), ("U", "Umsatz"), ("Kxx", "Kategoriezeile")],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 04 Haushalte
    # ------------------------------------------------------------------

    def art_households(self) -> str:
        last = self.last()
        u = _to_float(last.get("avg_utility", 0.0))
        h = _to_float(last.get("avg_health", 0.0))
        b = _to_float(last.get("avg_education", 0.0))
        t = _to_float(last.get("avg_trust", 0.0))
        alq = _to_float(last.get("unemployment", 0.0))
        gin = _to_float(last.get("inequality_gini", 0.0))
        avg_money = safe_div(sum(x.money for x in self.eco.households.values()), len(self.eco.households), 0.0)
        art = [
            "       👥 HAUSHALTS-COCKPIT",
            "       U   " + _bar(u, 1.0, 30, GOOD) + " " + _fmt_unit(u),
            "       G   " + _bar(h, 1.0, 30, GOOD) + " " + _fmt_unit(h),
            "       B   " + _bar(b, 1.0, 30, GOOD) + " " + _fmt_unit(b),
            "       T   " + _bar(t, 1.0, 30, GOOD) + " " + _fmt_unit(t),
            "       ALQ " + _bar(alq, 1.0, 30, BAD) + " " + _fmt_pct(alq),
            "       GIN " + _bar(gin, 1.0, 30, BAD) + " " + _fmt_unit(gin),
            "",
            "               ╭──────────────╮       ╭──────────────╮       ╭──────────────╮",
            "       🧠 ───▶ │ Fähigkeit    │ ───▶  │ Einkommen    │ ───▶  │ Zielnutzen   │",
            "               ╰──────────────╯       ╰──────────────╯       ╰──────────────╯",
        ]
        evaluation = (
            "Der durchschnittliche Haushalt hält %.1f Geldeinheiten. Gute Werte bei U, G, B und T zeigen breite Münzfähigkeit; hohe ALQ oder GIN zeigen, dass Fähigkeiten sozial blockiert oder ungleich verteilt werden."
            % avg_money
        )
        return _section(
            "👥 UTF-8-Art 04 · Haushaltswohl und Münzfähigkeit",
            "Eine Wirtschaft ist schwach, wenn sie zwar produziert, aber Menschen nicht arbeits-, lern-, gesundheits- und vertrauensfähig hält.",
            "Gezeigt werden Nutzen, Gesundheit, Bildung, Vertrauen, Arbeitslosigkeit und Ungleichheit der Haushalte.",
            [("U", "Nutzen"), ("G", "Gesundheit"), ("B", "Bildung"), ("T", "Vertrauen"), ("ALQ", "Arbeitslosenquote"), ("GIN", "Gini-Ungleichheit")],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 05 Geld und Staat
    # ------------------------------------------------------------------

    def art_money_state(self) -> str:
        last = self.last()
        gm = _to_float(last.get("money_supply", 0.0))
        kr = _to_float(last.get("credit_outstanding", 0.0))
        st = _to_float(last.get("tax_revenue", 0.0))
        aus = _to_float(last.get("state_spending", 0.0))
        deficit = _to_float(last.get("state_deficit", 0.0))
        debt = _to_float(last.get("state_debt", 0.0))
        zs = _to_float(last.get("policy_rate", 0.0))
        inf = _to_float(last.get("inflation", 0.0))
        mx = max(1.0, gm, kr, st, aus, abs(deficit), debt)
        art = [
            "              ╭──────────────╮        ╭──────────────╮        ╭──────────────╮",
            "       ZB 🏦 │ ZS %6s │ ═══▶  │ Banken / KR │ ═══▶  │ Firmen / OUT │ 🏭" % _fmt_pct(zs),
            "              ╰──────┬───────╯        ╰──────┬───────╯        ╰──────┬───────╯",
            "                     │                       │                       │",
            "              ╭──────▼───────╮        ╭──────▼───────╮        ╭──────▼───────╮",
            "       GM 💶 │ Geldmenge    │ ◀═══▶  │ Staat / ST   │ ◀═══▶  │ Haushalte    │ 👥",
            "              ╰──────────────╯        ╰──────────────╯        ╰──────────────╯",
            "",
            "       GM  " + _bar(gm, mx, 28, RAINBOW) + " " + _fmt_money(gm),
            "       KR  " + _bar(kr, mx, 28, BAD) + " " + _fmt_money(kr),
            "       ST  " + _bar(st, mx, 28, GOOD) + " " + _fmt_money(st),
            "       AUS " + _bar(aus, mx, 28, HEAT) + " " + _fmt_money(aus),
            "       DEF " + _bar(abs(deficit), mx, 28, BAD) + " " + _fmt_money(deficit),
            "       SCH " + _bar(debt, mx, 28, BAD) + " " + _fmt_money(debt),
        ]
        evaluation = (
            "Die Inflation liegt bei %s, der Zentralbankzins bei %s. Die Staatsschuld steht bei %s. Problematisch wird es, wenn KR, DEF und INF steigen, ohne dass Bildung, Gesundheit, Infrastruktur oder reale Münzleistung mitwachsen."
            % (_fmt_pct(inf), _fmt_pct(zs), _fmt_money(debt))
        )
        return _section(
            "🏦 UTF-8-Art 05 · Geld, Kredit und Staat",
            "Geld ist im System nur vertrauenswürdig, wenn es zur realen Münzleistung und zu stabilen Institutionen passt.",
            "Gezeigt werden Zentralbank, Kredit, Geldmenge, Steuern, Staatsausgaben, Defizit und Schulden.",
            [("ZB", "Zentralbank"), ("ZS", "Zentralbankzins"), ("GM", "Geldmenge"), ("KR", "Kreditbestand"), ("ST", "Steuern"), ("AUS", "Staatsausgaben"), ("DEF", "Defizit"), ("SCH", "Staatsschuld")],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 06 Umwelt
    # ------------------------------------------------------------------

    def art_environment(self) -> str:
        last = self.last()
        nk = _to_float(last.get("nature_capital", 0.0))
        bio = _to_float(last.get("biodiversity", 0.0))
        em = _to_float(last.get("emissions", 0.0))
        co2 = _to_float(last.get("carbon_stock", 0.0))
        rp = self.eco.environment.resource_pressure
        ws = self.eco.environment.water_stress
        bad_max = max(1.0, em, co2, rp, ws)
        art = [
            "                         🟩",
            "                        🟩🟩🟩                    ☁️  ☁️  ☁️",
            "                       🟩🟩🟩🟩🟩               CO2-Speicher",
            "                      🟩🟩🟩🟩🟩🟩🟩        ≈≈≈≈≈≈≈≈≈≈ Wasser",
            "                            🟫",
            "                  🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫🟫",
            "",
            "       NK  " + _bar(nk, 1.15, 30, GOOD) + " " + _fmt_unit(nk),
            "       BIO " + _bar(bio, 1.05, 30, GOOD) + " " + _fmt_unit(bio),
            "       EM  " + _bar(em, bad_max, 30, BAD) + " " + _fmt_unit(em),
            "       CO2 " + _bar(co2, bad_max, 30, BAD) + " " + _fmt_unit(co2),
            "       RP  " + _bar(rp, 1.0, 30, BAD) + " " + _fmt_unit(rp),
            "       WS  " + _bar(ws, 1.0, 30, BAD) + " " + _fmt_unit(ws),
        ]
        evaluation = (
            "Das Naturkapital steht bei %.1f%% des Modellmaximums, die Biodiversität bei %.1f%%. Steigende EM, CO2, RP oder WS zeigen, dass K16-Transformation, Reparatur und Ressourcenschonung stärker gebraucht werden."
            % (100.0 * nk / 1.15, 100.0 * bio / 1.05)
        )
        return _section(
            "🌳 UTF-8-Art 06 · Natur als oberste Nebenbedingung",
            "Jede Optimierung ist falsch, wenn sie die Naturgrenze dauerhaft verletzt.",
            "Gezeigt werden Naturkapital, Biodiversität, Emissionen, Kohlenstoffspeicher, Ressourcendruck und Wasserstress.",
            [("NK", "Naturkapital"), ("BIO", "Biodiversität"), ("EM", "Emissionen"), ("CO2", "Kohlenstoffspeicher"), ("RP", "Ressourcendruck"), ("WS", "Wasserstress")],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 07 Innovation
    # ------------------------------------------------------------------

    def art_innovation(self) -> str:
        output = self.category_metric("category_output")
        vals = {k: output.get(k, 0.0) for k in [1, 11, 14, 16, 17]}
        mx = max([1.0] + list(vals.values()))
        strength = safe_div(vals[1] + vals[11] + vals[14] + vals[17], 4.0 * mx, 0.0)
        art = [
            "                                  ╭────────╮",
            "                                  │ K17 MI │ 🧠",
            "                                  ╰───┬────╯",
            "                 ╭────────╮          │          ╭────────╮",
            "          🎭 K11 │   SB   │ ════════ ╬ ═══════▶ │   FU   │ K14 🤝",
            "                 ╰───┬────╯          │          ╰───┬────╯",
            "                     │               │              │",
            "              ╭──────▼─╮       ╭─────▼────╮   ╭─────▼────╮",
            "       🔎 K01 │   EX   │  ───▶ │  NEU     │ ─▶│   TR     │ K16 🔁",
            "              ╰────────╯       ╰──────────╯   ╰──────────╯",
            "",
            "       EX " + _bar(vals[1], mx, 28, HEAT) + " " + _fmt_unit(vals[1]),
            "       SB " + _bar(vals[11], mx, 28, HEAT) + " " + _fmt_unit(vals[11]),
            "       FU " + _bar(vals[14], mx, 28, HEAT) + " " + _fmt_unit(vals[14]),
            "       TR " + _bar(vals[16], mx, 28, HEAT) + " " + _fmt_unit(vals[16]),
            "       MI " + _bar(vals[17], mx, 28, HEAT) + " " + _fmt_unit(vals[17]),
        ]
        evaluation = (
            "Die Innovationsstärke liegt bei %.1f%%. EX, SB, FU und MI zeigen, ob das System neue Möglichkeiten erzeugt; TR zeigt, ob alte Münzen sinnvoll umgewandelt statt verschwendet werden."
            % (100.0 * strength)
        )
        return _section(
            "🧠 UTF-8-Art 07 · Innovation, Fusion und Meta-Intelligenz",
            "Ohne Stilbruch, Fusion und Meta-Intelligenz wird die Wirtschaft bloß Routine und verliert Zukunftsfähigkeit.",
            "Gezeigt werden die innovativen Kategorien und ihre Outputstärke.",
            [("EX", "Extraktion in K01"), ("SB", "Stilbruch in K11"), ("FU", "Fusion in K14"), ("TR", "Transformation in K16"), ("MI", "Meta-Intelligenz in K17")],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 08 Solidarität und Zielnutzen
    # ------------------------------------------------------------------

    def art_social_goal(self) -> str:
        output = self.category_metric("category_output")
        k18 = output.get(18, 0.0)
        k19 = output.get(19, 0.0)
        mx = max(1.0, k18, k19)
        social = self.eco.state.social_index
        health = self.eco.state.health_index
        culture = self.eco.state.culture_index
        commons = self.eco.state.commons_index
        art = [
            "              💞 K18 Solidarität                         🌭 K19 Ziel-Ergebnis",
            "              ╭──────────────╮                          ╭──────────────╮",
            "       Pflege │ Hilfe        │ ──────── Wertfluss ─────▶ │ Nutzen       │ Konsum",
            "              ╰──────┬───────╯                          ╰──────┬───────╯",
            "                     │                                             │",
            "              ╭──────▼───────╮                          ╭──────▼───────╮",
            "              │ Vertrauen    │ ◀──── soziale Rückkopplung ─────── │ Bedürfnis    │",
            "              ╰──────────────╯                          ╰──────────────╯",
            "",
            "       K18 " + _bar(k18, mx, 28, GOOD) + " " + _fmt_unit(k18),
            "       K19 " + _bar(k19, mx, 28, GOOD) + " " + _fmt_unit(k19),
            "       SOZ " + _bar(social, 1.0, 28, GOOD) + " " + _fmt_unit(social),
            "       GES " + _bar(health, 1.0, 28, GOOD) + " " + _fmt_unit(health),
            "       KUL " + _bar(culture, 1.0, 28, GOOD) + " " + _fmt_unit(culture),
            "       COM " + _bar(commons, 1.0, 28, GOOD) + " " + _fmt_unit(commons),
        ]
        evaluation = (
            "K18 erzeugt %.1f und K19 %.1f Output. Wenn SOZ, GES, KUL und COM hoch bleiben, entstehen Zielnutzen und Solidarität nicht nur als private Käufe, sondern als tragende Systemschichten."
            % (k18, k19)
        )
        return _section(
            "💞 UTF-8-Art 08 · Solidarität und Ziel-Ergebnis",
            "Eine Wirtschaft kann viel produzieren und trotzdem am Ziel vorbeigehen; daher werden K18 und K19 getrennt sichtbar gemacht.",
            "Gezeigt werden Solidaritätsoutput, Zielnutzenoutput und öffentliche Sozial-, Gesundheits-, Kultur- und Commons-Indizes.",
            [("K18", "Solidarität/Wertschätzung"), ("K19", "Ziel-Ergebnis"), ("SOZ", "Sozialindex"), ("GES", "Gesundheitsindex"), ("KUL", "Kulturindex"), ("COM", "Commons-Index")],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 09 Außenhandel
    # ------------------------------------------------------------------

    def art_foreign_trade(self) -> str:
        last = self.last()
        imp = _to_float(last.get("imports", 0.0))
        exp = _to_float(last.get("exports", 0.0))
        sal = exp - imp
        mx = max(1.0, imp, exp, abs(sal))
        art = [
            "                 ╭─────────────╮       EXP       ╭─────────────╮",
            "          Inland │ Produktion  │ ══════════════▶ │ Ausland     │",
            "                 ╰──────┬──────╯                 ╰──────┬──────╯",
            "                        │                               │",
            "                 ╭──────▼──────╮       IMP       ╭──────▼──────╮",
            "          Inland │ Versorgung  │ ◀══════════════ │ Weltmarkt   │",
            "                 ╰─────────────╯                 ╰─────────────╯",
            "",
            "       EXP " + _bar(exp, mx, 30, GOOD) + " " + _fmt_money(exp),
            "       IMP " + _bar(imp, mx, 30, BAD) + " " + _fmt_money(imp),
            "       SAL " + _bar(abs(sal), mx, 30, RAINBOW) + " " + _fmt_money(sal),
        ]
        evaluation = (
            "Der Außenhandelssaldo beträgt %s. Positives SAL zeigt Exportstärke; negatives SAL zeigt, dass Engpässe, Preisvorteile oder fehlende heimische Münzen durch Import ausgeglichen werden."
            % _fmt_money(sal)
        )
        return _section(
            "🌍 UTF-8-Art 09 · Außenhandel und Versorgung",
            "Kein Wirtschaftssystem ist isoliert; Außenhandel zeigt, ob eigene Münzketten stark genug sind oder Lücken von außen gefüllt werden.",
            "Gezeigt werden Import, Export und Saldo des Außenhandels.",
            [("EXP", "Exporte"), ("IMP", "Importe"), ("SAL", "Export minus Import")],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 10 Risiko
    # ------------------------------------------------------------------

    def art_risk(self) -> str:
        last = self.last()
        rsk = _to_float(last.get("systemic_risk", 0.0))
        ver = _to_float(last.get("avg_trust", 0.0))
        reg = self.eco.state.regulation_index
        inf = abs(_to_float(last.get("inflation", 0.0)))
        nst = clamp(1.0 - _to_float(last.get("nature_capital", 0.0)), 0.0, 1.0)
        akt = int(_to_float(last.get("active_firms", 0)))
        aus = int(_to_float(last.get("failed_firms", 0)))
        verdict = "stabil" if rsk < 0.35 else "angespannt" if rsk < 0.65 else "kritisch"
        art = [
            "                           ╭──────────────────────────╮",
            "                           │       RISIKO-RAD         │",
            "                           ╰────────────┬─────────────╯",
            "                                        │",
            "                 ╭──────────────────────▼──────────────────────╮",
            "                 │ Vertrauen · Preise · Natur · Firmen · Regeln │",
            "                 ╰──────┬──────────┬──────────┬──────────┬─────╯",
            "                        │          │          │          │",
            "                    👥 VER     🏛️ REG     📈 INF     🌳 NST",
            "",
            "       RSK " + _bar(rsk, 1.0, 30, BAD) + " " + _fmt_unit(rsk),
            "       VER " + _bar(ver, 1.0, 30, GOOD) + " " + _fmt_unit(ver),
            "       REG " + _bar(reg, 1.0, 30, GOOD) + " " + _fmt_unit(reg),
            "       INF " + _bar(inf, 0.20, 30, BAD) + " " + _fmt_pct(inf),
            "       NST " + _bar(nst, 1.0, 30, BAD) + " " + _fmt_unit(nst),
            "       AKT %d      AUS %d" % (akt, aus),
        ]
        evaluation = (
            "Das System wirkt am Ende %s: RSK %.1f%%, VER %.1f%%, AKT %d und AUS %d. Sinkendes Vertrauen, steigende Ausfälle oder hoher Naturstress wären die klaren Warnzeichen."
            % (verdict, 100.0 * rsk, 100.0 * ver, akt, aus)
        )
        return _section(
            "⚠️ UTF-8-Art 10 · Stabilität und Systemrisiko",
            "Ein vollständiges Wirtschaftssystem muss zeigen, wann es nicht nur teuer, sondern instabil wird.",
            "Gezeigt werden Systemrisiko, Vertrauen, Regulierung, Inflationsdruck, Naturstress sowie aktive und ausgefallene Firmen.",
            [("RSK", "Systemrisiko"), ("VER", "Vertrauen"), ("REG", "Regulierung"), ("INF", "Inflationsdruck"), ("NST", "Naturstress"), ("AKT", "aktive Firmen"), ("AUS", "ausgefallene Firmen")],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 11 Münz-Lebenszyklus
    # ------------------------------------------------------------------

    def art_coin_lifecycle(self) -> str:
        statuses = ["Idee", "geplant", "finanziert", "in Produktion", "fertig", "verkauft", "genutzt", "transformiert", "gescheitert"]
        codes = ["ID", "PL", "FI", "PR", "FE", "VK", "GN", "TR", "GS"]
        counts = {s: 0 for s in statuses}
        by_cat: Dict[int, int] = {k: 0 for k in CATEGORY_INFO}
        for c in self.eco.coins:
            counts[c.status] = counts.get(c.status, 0) + 1
            by_cat[c.category] = by_cat.get(c.category, 0) + 1
        max_count = max([1] + list(counts.values()))
        art = [
            "       ID ──▶ PL ──▶ FI ──▶ PR ──▶ FE ──▶ VK ──▶ GN ──▶ TR",
            "        ╲                                               ╱",
            "         ╲────────────────────── GS ◀──────────────────╯",
            "",
        ]
        for code, status in zip(codes, statuses):
            art.append("       %-2s  %-14s %s %d" % (code, status, _bar(counts.get(status, 0), max_count, 24, RAINBOW), counts.get(status, 0)))
        top = sorted(by_cat.items(), key=lambda kv: kv[1], reverse=True)[:5]
        art.append("")
        art.append("       TOP-K: " + "   ".join(["K%02d=%d" % (k, v) for k, v in top]))
        total = sum(counts.values())
        done = counts.get("verkauft", 0) + counts.get("genutzt", 0) + counts.get("transformiert", 0)
        failed = counts.get("gescheitert", 0)
        evaluation = (
            "Es wurden %d Münzen erzeugt. Davon sind %.1f%% verkauft, genutzt oder transformiert; %.1f%% sind gescheitert. Das ist die Prozessqualität der Optimierungsprobleme, nicht bloß ihr Umsatz."
            % (total, 100.0 * safe_div(done, max(1, total), 0.0), 100.0 * safe_div(failed, max(1, total), 0.0))
        )
        return _section(
            "🪙 UTF-8-Art 11 · Lebenszyklus der Münzen",
            "Eine Münze ist erst dann wirtschaftlich interessant, wenn man sieht, ob sie von Idee zu realem Zielnutzen gelangt.",
            "Gezeigt wird der Status aller erzeugten Münzen und welche Kategorien die meisten Münzen erzeugt haben.",
            [("ID", "Idee"), ("PL", "geplant"), ("FI", "finanziert"), ("PR", "in Produktion"), ("FE", "fertig"), ("VK", "verkauft"), ("GN", "genutzt"), ("TR", "transformiert"), ("GS", "gescheitert"), ("Kxx", "Kategorie xx")],
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 12 Schockhimmel
    # ------------------------------------------------------------------

    def art_shock_sky(self) -> str:
        events = list(getattr(self.eco, "event_log", []))
        last_events = events[-8:]
        if not last_events:
            art = [
                "                         🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦",
                "                      🟦        ☀️  STABILE LUFT        🟦",
                "                         🟦🟦🟦🟦🟦🟦🟦🟦🟦🟦",
                "                              🌱      🏘️      🏭      🏛️",
            ]
            abbreviations = [("EV", "Ereignis; hier nicht eingetreten")]
            evaluation = "Es wurden keine Schocks protokolliert; die beobachteten Veränderungen stammen aus normalen Markt-, Kredit-, Sozial- und Umweltmechaniken."
        else:
            clouds = ["⛈️", "🌩️", "🌪️", "🔥", "💧", "🧊", "⚡", "🌫️"]
            art = ["                         ⛈️  SCHOCKHIMMEL DER SIMULATION", ""]
            for i, msg in enumerate(last_events, 1):
                art.append("       EV%02d %s %s" % (i, clouds[(i - 1) % len(clouds)], msg))
            art.append("")
            art.append("       " + "".join(["⚡" if i % 2 else "🌩️" for i in range(min(26, len(events) + 6))]))
            abbreviations = [("EV%02d" % i, "Ereignis %d im angezeigten Schockhimmel" % i) for i in range(1, len(last_events) + 1)]
            evaluation = (
                "Es wurden insgesamt %d Schockereignisse protokolliert, davon werden die letzten %d angezeigt. Schocks testen, ob Reserven, Vertrauen, Staat, Kredit und Naturpuffer genügen."
                % (len(events), len(last_events))
            )
        return _section(
            "⛈️ UTF-8-Art 12 · Schockhimmel der Wirtschaft",
            "Ein System ist erst glaubwürdig, wenn sichtbar wird, wie es auf Störungen reagiert.",
            "Gezeigt werden externe Schocks oder ein stabiler Himmel, falls keine Schocks eingetreten sind.",
            abbreviations,
            art,
            evaluation,
        )

    # ------------------------------------------------------------------
    # 13 Zeitverlauf
    # ------------------------------------------------------------------

    def art_timeline(self) -> str:
        mw = self.metric_series("mw")
        bmp = self.metric_series("bmp")
        nat = self.metric_series("nature_capital")
        rsk = self.metric_series("systemic_risk")
        mw_trend, mw_diff = self.trend_word("mw")
        nat_trend, nat_diff = self.trend_word("nature_capital")
        rsk_trend, rsk_diff = self.trend_word("systemic_risk")
        art = [
            "       MW  " + _sparkline(mw, 64) + "  " + mw_trend + " " + _fmt_money(mw_diff),
            "       BMP " + _sparkline(bmp, 64),
            "       NAT " + _sparkline(nat, 64) + "  " + nat_trend + " " + _fmt_unit(nat_diff),
            "       RSK " + _sparkline(rsk, 64) + "  " + rsk_trend + " " + _fmt_unit(rsk_diff),
            "",
            "       t=1 ═════════════════════════════════════════════════════════════════▶ t=%d" % len(self.eco.metrics),
            "       Schocks: %d      Münzen: %d      Verträge: %d" % (len(self.eco.event_log), len(self.eco.coins), len(self.eco.contracts)),
        ]
        evaluation = (
            "Der Münzwohlstand ist im Zeitverlauf %s (%s). Naturkapital ist %s (%s), Systemrisiko ist %s (%s). Daran sieht man, ob Wachstum, Stabilität und Naturgrenzen zusammenpassen."
            % (mw_trend, _fmt_money(mw_diff), nat_trend, _fmt_unit(nat_diff), rsk_trend, _fmt_unit(rsk_diff))
        )
        return _section(
            "📈 UTF-8-Art 13 · Zeitverlauf der Gesamtwirtschaft",
            "Ein einzelner Endwert kann täuschen; die Entwicklung über Zeit zeigt, ob das System kippt, wächst oder regeneriert.",
            "Gezeigt werden Zeitreihen von Münzwohlstand, Brutto-Münzprodukt, Naturkapital und Systemrisiko.",
            [("MW", "Münzwohlstand"), ("BMP", "Brutto-Münzprodukt"), ("NAT", "Naturkapital"), ("RSK", "Systemrisiko"), ("t", "Simulationsperiode")],
            art,
            evaluation,
        )

    def render(self) -> str:
        parts = [
            self.art_overview(),
            self.art_sector_heatmap(),
            self.art_market_gallery(),
            self.art_households(),
            self.art_money_state(),
            self.art_environment(),
            self.art_innovation(),
            self.art_social_goal(),
            self.art_foreign_trade(),
            self.art_risk(),
            self.art_coin_lifecycle(),
            self.art_shock_sky(),
            self.art_timeline(),
        ]
        return "\n\n".join(parts) + "\n"


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Münzökonomie als ausschließlich bunte UTF-8-Art-Simulationsausgabe")
    p.add_argument("--years", type=int, default=12, help="Anzahl Jahre")
    p.add_argument("--periods-per-year", type=int, default=4, help="Perioden pro Jahr")
    p.add_argument("--households", type=int, default=100, help="Anzahl Haushalte")
    p.add_argument("--firms-per-category", type=int, default=2, help="Unternehmen pro Kategorie")
    p.add_argument("--banks", type=int, default=2, help="Anzahl Geschäftsbanken")
    p.add_argument("--seed", type=int, default=42, help="Zufallsseed")
    p.add_argument("--no-foreign", action="store_true", help="Außenhandel deaktivieren")
    p.add_argument("--shock-frequency", type=float, default=0.06, help="Schockwahrscheinlichkeit pro Periode")
    p.add_argument("--out", type=str, default="", help="Optional: Ordner für utf8_art_report.txt")
    p.add_argument("--no-print", action="store_true", help="Nichts im Terminal drucken, nur --out schreiben")
    return p


def run_art_simulation(args: argparse.Namespace) -> str:
    periods = max(1, int(args.years) * max(1, int(args.periods_per_year)))
    eco = Economy(
        seed=args.seed,
        households=args.households,
        firms_per_category=args.firms_per_category,
        banks=args.banks,
        foreign_trade=not args.no_foreign,
        shock_frequency=args.shock_frequency,
    )
    eco.run(periods, quiet=True)
    renderer = Utf8ArtRenderer(eco, periods)
    return renderer.render()


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    report = run_art_simulation(args)
    if args.out:
        if not os.path.isdir(args.out):
            os.makedirs(args.out)
        with open(os.path.join(args.out, "utf8_art_report.txt"), "w", encoding="utf-8") as f:
            f.write(report)
    if not args.no_print:
        try:
            sys.stdout.write(report)
        except UnicodeEncodeError:
            sys.stdout.buffer.write(report.encode("utf-8", "replace"))
    return 0


if __name__ == "__main__":
    sys.exit(main())
