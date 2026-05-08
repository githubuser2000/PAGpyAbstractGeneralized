# -*- coding: utf-8 -*-
"""Farbige UTF-8-Art-Berichte für die Q-Wirtschaftssimulation.

Dieses Modul erzeugt absichtlich keine externen Grafiken und nutzt keine
Drittbibliotheken. Alle Darstellungen bestehen aus Unicode-Zeichen, Emoji-
Farbblöcken und optionalen ANSI-Farben für die Konsole. Dadurch laufen die
Berichte auch unter PyPy3 mit Standardbibliothek.
"""

from __future__ import print_function

import math
import os
from collections import defaultdict

from .money import Q_META, Q_VALUES
from .sectors import GOODS, SECTOR_RECIPES, LABOR_TYPES
from .utils import clamp, mean, gini

ANSI = {
    "reset": "\033[0m",
    "bold": "\033[1m",
    "dim": "\033[2m",
    "red": "\033[31m",
    "green": "\033[32m",
    "yellow": "\033[33m",
    "blue": "\033[34m",
    "magenta": "\033[35m",
    "cyan": "\033[36m",
    "white": "\033[37m",
    "bright_red": "\033[91m",
    "bright_green": "\033[92m",
    "bright_yellow": "\033[93m",
    "bright_blue": "\033[94m",
    "bright_magenta": "\033[95m",
    "bright_cyan": "\033[96m",
}

RAINBOW_ANSI = ["bright_red", "yellow", "bright_yellow", "bright_green", "bright_cyan", "bright_blue", "bright_magenta"]
RAINBOW_EMOJI = ["🟥", "🟧", "🟨", "🟩", "🟦", "🟪"]
RISK_EMOJI = ["🟩", "🟨", "🟧", "🟥"]
BLOCKS = "▁▂▃▄▅▆▇█"
SHADE = "░▒▓█"


def _ansi(text, color=None, bold=False, enable=True):
    if not enable:
        return text
    prefix = ""
    if bold:
        prefix += ANSI["bold"]
    if color:
        prefix += ANSI.get(color, "")
    if not prefix:
        return text
    return prefix + text + ANSI["reset"]


def visible_len(s):
    """Grobe sichtbare Länge ohne ANSI. Emoji-Breite wird nicht exakt gezählt."""
    out = []
    skip = False
    i = 0
    while i < len(s):
        ch = s[i]
        if ch == "\033":
            skip = True
        elif skip and ch == "m":
            skip = False
        elif not skip:
            out.append(ch)
        i += 1
    return len("".join(out))


def fmt_num(x, suffix="", digits=2):
    try:
        x = float(x)
    except Exception:
        return str(x) + suffix
    neg = x < 0
    x_abs = abs(x)
    if x_abs >= 1000000:
        s = ("%.*f" % (digits, x / 1000000.0)) + " Mio."
    elif x_abs >= 1000:
        s = ("%.*f" % (digits, x / 1000.0)) + " Tsd."
    else:
        s = "%.*f" % (digits, x)
    if digits > 0 and "." in s:
        # deutsche Lesbarkeit in Textdateien: Punkt bleibt maschinenfreundlich.
        pass
    return s + suffix


def fmt_pct(x, digits=1):
    return fmt_num(float(x) * 100.0, " %", digits)


def sample_values(values, width):
    values = list(values or [])
    if width <= 0:
        return []
    if not values:
        return [0.0] * width
    if len(values) <= width:
        return values
    out = []
    for i in range(width):
        start = int(math.floor(i * len(values) / float(width)))
        end = int(math.floor((i + 1) * len(values) / float(width)))
        if end <= start:
            end = start + 1
        bucket = values[start:end]
        out.append(mean(bucket))
    return out


def sparkline(values, width=64, ansi=False, color="bright_cyan"):
    vals = [float(v or 0.0) for v in sample_values(values, width)]
    if not vals:
        return ""
    lo = min(vals)
    hi = max(vals)
    if abs(hi - lo) < 1e-12:
        chars = "▄" * len(vals)
    else:
        chars = ""
        for v in vals:
            idx = int(round((v - lo) / (hi - lo) * (len(BLOCKS) - 1)))
            idx = int(clamp(idx, 0, len(BLOCKS) - 1))
            chars += BLOCKS[idx]
    return _ansi(chars, color, enable=ansi)


def rainbow_bar(value, maximum, width=30, ansi=False, empty="░"):
    maximum = max(float(maximum or 0.0), 1e-12)
    ratio = clamp(float(value or 0.0) / maximum, 0.0, 1.0)
    filled = int(round(width * ratio))
    if ansi:
        parts = []
        for i in range(filled):
            parts.append(_ansi("█", RAINBOW_ANSI[i % len(RAINBOW_ANSI)], enable=True))
        parts.append(_ansi(empty * max(0, width - filled), "dim", enable=True))
        return "".join(parts)
    parts = []
    for i in range(filled):
        parts.append(RAINBOW_EMOJI[i % len(RAINBOW_EMOJI)])
    parts.append("⬛" * max(0, width - filled))
    return "".join(parts)


def risk_bar(value, width=24, ansi=False, reverse=False):
    """value: 0=gering, 1=hoch. reverse=True: hoch ist gut."""
    v = clamp(float(value or 0.0), 0.0, 1.0)
    if reverse:
        v = 1.0 - v
    filled = int(round(width * v))
    if ansi:
        if v < 0.35:
            color = "bright_green"
        elif v < 0.60:
            color = "bright_yellow"
        elif v < 0.80:
            color = "yellow"
        else:
            color = "bright_red"
        return _ansi("█" * filled, color, enable=True) + _ansi("░" * (width - filled), "dim", enable=True)
    # Emojis: mit Gradient gefüllt, leer schwarz.
    parts = []
    for i in range(filled):
        idx = min(3, int(v * 4.0))
        parts.append(RISK_EMOJI[idx])
    parts.append("⬛" * max(0, width - filled))
    return "".join(parts)


def label_bar(label, value, maximum, width=26, suffix="", ansi=False, value_digits=2):
    lab = (label[:26]).ljust(26)
    bar = rainbow_bar(value, maximum, width=width, ansi=ansi)
    return "%s │%s│ %s" % (lab, bar, fmt_num(value, suffix, value_digits))


def signed_bar(label, value, maximum, width=24, ansi=False, suffix=" ZW"):
    lab = (label[:24]).ljust(24)
    v = float(value or 0.0)
    maximum = max(abs(float(maximum or 0.0)), 1e-12)
    filled = int(round(width * min(abs(v) / maximum, 1.0)))
    sign = "+" if v >= 0 else "-"
    if ansi:
        color = "bright_green" if v >= 0 else "bright_red"
        bar = _ansi("█" * filled, color, enable=True) + _ansi("░" * (width - filled), "dim", enable=True)
        sign = _ansi(sign, color, bold=True, enable=True)
    else:
        token = "🟩" if v >= 0 else "🟥"
        bar = token * filled + "⬛" * (width - filled)
    return "%s │%s│ %s%s" % (lab, bar, sign, fmt_num(abs(v), suffix, 2))


def box(title, lines, width=98, ansi=False, color="bright_cyan"):
    width = max(width, 50)
    top = "╔" + "═" * (width - 2) + "╗"
    mid_title = "║ " + title[:width - 4].ljust(width - 4) + " ║"
    sep = "╠" + "═" * (width - 2) + "╣"
    bottom = "╚" + "═" * (width - 2) + "╝"
    out = [_ansi(top, color, enable=ansi), _ansi(mid_title, color, bold=True, enable=ansi), _ansi(sep, color, enable=ansi)]
    for line in lines:
        raw = line
        # Das Padding ignoriert ANSI teilweise, reicht für Konsole gut genug.
        pad = max(0, width - 4 - visible_len(raw))
        out.append(_ansi("║ ", color, enable=ansi) + raw + " " * pad + _ansi(" ║", color, enable=ansi))
    out.append(_ansi(bottom, color, enable=ansi))
    return "\n".join(out)


def section(title, description, art, evaluation, markdown=True):
    if markdown:
        return "\n".join([
            "## " + title,
            "",
            "### Was wird simuliert und warum?",
            description.strip(),
            "",
            "```text",
            art.rstrip(),
            "```",
            "",
            "### Auswertung",
            evaluation.strip(),
            "",
        ])
    return "\n".join([
        "\n" + title,
        "─" * min(90, max(10, len(title))),
        description.strip(),
        "",
        art.rstrip(),
        "",
        "Auswertung:",
        evaluation.strip(),
        "",
    ])


def metrics_series(sim, key):
    return [float(m.get(key, 0.0) or 0.0) for m in sim.metrics_history]


def last_metric(sim, key, default=0.0):
    if sim.metrics_history:
        return sim.metrics_history[-1].get(key, default)
    return default


def trend_sentence(values, label, unit="", percent=False, good_high=None):
    vals = [float(v or 0.0) for v in values]
    if not vals:
        return "%s wurde nicht gemessen." % label
    start = vals[0]
    end = vals[-1]
    lo = min(vals)
    hi = max(vals)
    diff = end - start
    if abs(diff) < max(1e-9, abs(start) * 0.01):
        direction = "blieb weitgehend stabil"
    elif diff > 0:
        direction = "stieg"
    else:
        direction = "fiel"
    if percent:
        start_s = fmt_pct(start)
        end_s = fmt_pct(end)
        lo_s = fmt_pct(lo)
        hi_s = fmt_pct(hi)
    else:
        start_s = fmt_num(start, unit)
        end_s = fmt_num(end, unit)
        lo_s = fmt_num(lo, unit)
        hi_s = fmt_num(hi, unit)
    sentence = "%s %s von %s auf %s; der beobachtete Korridor lag zwischen %s und %s." % (label, direction, start_s, end_s, lo_s, hi_s)
    if good_high is not None and abs(diff) >= max(1e-9, abs(start) * 0.01):
        if (diff > 0 and good_high) or (diff < 0 and not good_high):
            sentence += " Die Richtung ist für diese Kennzahl grundsätzlich günstig."
        else:
            sentence += " Die Richtung ist für diese Kennzahl grundsätzlich belastend."
    return sentence


def _q_balances(sim):
    agents = sim.all_agents()
    rows = []
    for q in range(1, 21):
        pos_qty = 0.0
        debt_qty = 0.0
        for a in agents:
            qty = a.wallet.balances.get(q, 0.0)
            if qty > 0:
                pos_qty += qty
            elif qty < 0:
                debt_qty += -qty
        rows.append({
            "q": q,
            "label": "Q%d" % q,
            "name": Q_META[q]["name"],
            "asset_value": pos_qty * Q_VALUES[q],
            "debt_value": debt_qty * Q_VALUES[q],
            "price": sim.coin_market.coin_prices.get(q, Q_VALUES[q]),
            "shortage": sim.coin_market.shortage.get(q, 0.0),
        })
    return rows


def _sector_rows(sim):
    rows = []
    for s, recipe in SECTOR_RECIPES.items():
        firms = [f for f in sim.firms if f.sector_key == s]
        rows.append({
            "sector": s,
            "label": recipe.label,
            "sales": sum(f.last_sales_value for f in firms),
            "profit": sum(f.last_profit for f in firms),
            "output": sum(f.last_output for f in firms),
            "capital": sum(f.capital_stock for f in firms),
            "automation": mean(f.automation_level for f in firms) if firms else 0.0,
            "debt": sum(f.wallet.debt_value() for f in firms),
            "firms": len(firms),
        })
    return rows


def _labor_rows(sim):
    rows = []
    counts = sim.labor_market.count_by_labor
    wages = sim.labor_market.wage_by_labor
    for lt, meta in LABOR_TYPES.items():
        employed = counts.get(lt, 0)
        rows.append({
            "labor_type": lt,
            "label": meta.label,
            "employed": employed,
            "wage": wages.get(lt, 0.0) / employed if employed else 0.0,
            "base_wage": meta.base_wage,
            "description": meta.description,
        })
    return rows


def _shortage_rows(sim):
    m = sim.metrics_history[-1] if sim.metrics_history else {}
    rows = []
    for g, meta in GOODS.items():
        rows.append({
            "good": g,
            "label": meta.label,
            "shortage": float(m.get("shortage_%s" % g, 0.0) or 0.0),
            "sales_qty": float(m.get("sales_qty_%s" % g, 0.0) or 0.0),
            "price": float(m.get("price_%s" % g, meta.base_price) or 0.0),
            "base_price": meta.base_price,
        })
    return rows


def _wealth_buckets(sim):
    vals = [h.net_worth() for h in sim.households]
    if not vals:
        return []
    lo = min(vals)
    hi = max(vals)
    if abs(hi - lo) < 1e-9:
        return [("alle Haushalte", len(vals), lo, hi)]
    buckets = 8
    counts = [0] * buckets
    for v in vals:
        idx = int((v - lo) / (hi - lo) * buckets)
        if idx >= buckets:
            idx = buckets - 1
        counts[idx] += 1
    out = []
    for i, c in enumerate(counts):
        a = lo + (hi - lo) * i / buckets
        b = lo + (hi - lo) * (i + 1) / buckets
        out.append(("%s bis %s" % (fmt_num(a, "", 1), fmt_num(b, "", 1)), c, a, b))
    return out


def _risk_items(sim):
    m = sim.metrics_history[-1] if sim.metrics_history else {}
    money = float(m.get("total_positive_money_value", 0.0) or 0.0)
    debt = float(m.get("total_debt_value", 0.0) or 0.0)
    debt_ratio = debt / max(1.0, money)
    total_shortage = sum(float(m.get("shortage_%s" % g, 0.0) or 0.0) for g in GOODS)
    sales_total = max(1.0, sum(float(m.get("sales_qty_%s" % g, 0.0) or 0.0) for g in GOODS))
    shortage_ratio = total_shortage / sales_total
    q18_ratio = float(m.get("q18_debt_value", 0.0) or 0.0) / max(1.0, debt)
    q16_ratio = float(m.get("q16_debt_value", 0.0) or 0.0) / max(1.0, debt)
    default_ratio = float(m.get("default_losses_zw", 0.0) or 0.0) / max(1.0, money)
    return [
        ("Arbeitslosigkeit", clamp(float(m.get("unemployment_rate", 0.0) or 0.0) / 0.30, 0.0, 1.0), fmt_pct(m.get("unemployment_rate", 0.0))),
        ("Schuldenlast", clamp(debt_ratio / 0.85, 0.0, 1.0), fmt_num(debt_ratio, "", 2) + " Schulden/Geld"),
        ("Inflationsdruck", clamp(abs(float(m.get("inflation", 0.0) or 0.0)) / 0.15, 0.0, 1.0), fmt_pct(m.get("inflation", 0.0))),
        ("Q18-Architektur", clamp(q18_ratio / 0.25, 0.0, 1.0), fmt_pct(q18_ratio)),
        ("Q16-Betrieb", clamp(q16_ratio / 0.25, 0.0, 1.0), fmt_pct(q16_ratio)),
        ("Güterengpässe", clamp(shortage_ratio / 0.30, 0.0, 1.0), fmt_num(total_shortage, " ungedeckt", 1)),
        ("Ungleichheit", clamp(float(m.get("household_gini", 0.0) or 0.0) / 0.65, 0.0, 1.0), fmt_num(m.get("household_gini", 0.0), " Gini", 3)),
        ("Kreditausfälle", clamp(default_ratio / 0.08, 0.0, 1.0), fmt_num(m.get("default_losses_zw", 0.0), " ZW", 2)),
    ]


def render_macro_cockpit(sim, ansi=False):
    m = sim.metrics_history[-1] if sim.metrics_history else {}
    money = float(m.get("total_positive_money_value", 0.0) or 0.0)
    debt = float(m.get("total_debt_value", 0.0) or 0.0)
    debt_ratio = debt / max(1.0, money)
    lines = []
    lines.append("Szenario: %-20s Perioden: %-5s Haushalte: %-5s Firmen: %-5s Banken: %-3s" % (
        sim.scenario, sim.period, len(sim.households), len(sim.firms), len(sim.banks)))
    lines.append("BQP / Marktumsatz     " + rainbow_bar(m.get("bqp", 0.0), max(1.0, m.get("bqp", 1.0), money * 0.05), 26, ansi) + "  " + fmt_num(m.get("bqp", 0.0), " ZW"))
    lines.append("Preisindex            " + rainbow_bar(m.get("price_index", 0.0), max(2.0, m.get("price_index", 0.0)), 26, ansi) + "  " + fmt_num(m.get("price_index", 0.0), ""))
    lines.append("Arbeitslosigkeit      " + risk_bar(m.get("unemployment_rate", 0.0) / 0.30, 26, ansi) + "  " + fmt_pct(m.get("unemployment_rate", 0.0)))
    lines.append("Inflation letzte Per. " + risk_bar(abs(m.get("inflation", 0.0)) / 0.15, 26, ansi) + "  " + fmt_pct(m.get("inflation", 0.0)))
    lines.append("Q-Geldmenge positiv   " + rainbow_bar(money, max(1.0, money, debt), 26, ansi) + "  " + fmt_num(money, " ZW"))
    lines.append("Q-Schulden            " + risk_bar(debt_ratio / 0.85, 26, ansi) + "  " + fmt_num(debt, " ZW") + "  Verhältnis " + fmt_num(debt_ratio, ""))
    lines.append("Kreditbestand         " + risk_bar(float(m.get("loan_outstanding", 0.0) or 0.0) / max(1.0, money), 26, ansi) + "  " + fmt_num(m.get("loan_outstanding", 0.0), " ZW"))
    lines.append("Haushalts-Gini        " + risk_bar(float(m.get("household_gini", 0.0) or 0.0) / 0.65, 26, ansi) + "  " + fmt_num(m.get("household_gini", 0.0), ""))
    return box("🌈 Q-Ökonomie Makro-Cockpit", lines, width=112, ansi=ansi, color="bright_cyan")


def macro_evaluation(sim):
    m = sim.metrics_history[-1] if sim.metrics_history else {}
    money = float(m.get("total_positive_money_value", 0.0) or 0.0)
    debt = float(m.get("total_debt_value", 0.0) or 0.0)
    debt_ratio = debt / max(1.0, money)
    parts = []
    parts.append("Das Cockpit zeigt den Endzustand der Simulation. Entscheidend ist die Gleichzeitigkeit von realem Umsatz, Q-Geldmenge, Q-Schulden, Beschäftigung und Preisniveau. Diese Größen dürfen nicht isoliert gelesen werden: Eine Wirtschaft kann hohe Umsätze haben und trotzdem semantisch krank sein, wenn die Schulden in Q16, Q18 oder Q20 liegen.")
    if debt_ratio > 0.65:
        parts.append("Die Schuldenlast ist hoch. In diesem System ist das gefährlicher als in einer reinen Zahlenwährung, weil jede Schuld eine bestimmte Münzart meint. Die Wirtschaft braucht also nicht nur mehr Wert, sondern passende Reparaturfähigkeit.")
    elif debt_ratio > 0.35:
        parts.append("Die Schuldenlast ist sichtbar, aber noch steuerbar. Der nächste Prüfpunkt ist, ob sie sich auf operative Münzen oder auf System- und Kapitalmünzen konzentriert.")
    else:
        parts.append("Die Verschuldung wirkt relativ niedrig. Das lässt Raum für produktive Investitionen, solange die Geldmenge nicht nur in niedrigen Münzen konzentriert ist.")
    if float(m.get("unemployment_rate", 0.0) or 0.0) > 0.18:
        parts.append("Die Arbeitslosigkeit ist ein deutlicher Stresspunkt. Das Modell deutet dann auf Qualifikationsbruch, Nachfrageschwäche, Automatisierungsdruck oder sektorale Fehlallokation hin.")
    if abs(float(m.get("inflation", 0.0) or 0.0)) > 0.08:
        parts.append("Die letzte Inflation ist stark. Das ist ein Signal für Engpässe, zu schnelle Kreditexpansion oder eine Güterstruktur, die mit der Q-Geldstruktur nicht Schritt hält.")
    return " ".join(parts)


def render_series_panel(title, series_specs, ansi=False, width=72):
    lines = []
    for label, values, unit, percent, color in series_specs:
        vals = [float(v or 0.0) for v in values]
        if percent:
            start = fmt_pct(vals[0] if vals else 0.0)
            end = fmt_pct(vals[-1] if vals else 0.0)
            lo = fmt_pct(min(vals) if vals else 0.0)
            hi = fmt_pct(max(vals) if vals else 0.0)
        else:
            start = fmt_num(vals[0] if vals else 0.0, unit)
            end = fmt_num(vals[-1] if vals else 0.0, unit)
            lo = fmt_num(min(vals) if vals else 0.0, unit)
            hi = fmt_num(max(vals) if vals else 0.0, unit)
        lines.append((label[:22]).ljust(22) + " " + sparkline(vals, width=width, ansi=ansi, color=color))
        lines.append(" " * 23 + "Start %s │ Ende %s │ Min %s │ Max %s" % (start, end, lo, hi))
    return box(title, lines, width=118, ansi=ansi, color="bright_magenta")


def render_q_balance_matrix(sim, ansi=False):
    rows = _q_balances(sim)
    max_asset = max([r["asset_value"] for r in rows] + [1.0])
    max_debt = max([r["debt_value"] for r in rows] + [1.0])
    lines = []
    lines.append("Münze  Bedeutung                 Vermögen                              Schulden                              Kurs")
    lines.append("─────  ────────────────────────  ───────────────────────────────────  ───────────────────────────────────  ─────")
    for r in rows:
        qtxt = ("Q%02d" % r["q"]).ljust(5)
        name = r["name"][:24].ljust(24)
        asset = rainbow_bar(r["asset_value"], max_asset, 16, ansi) + " " + fmt_num(r["asset_value"], "")
        debt = risk_bar(r["debt_value"] / max_debt, 16, ansi) + " " + fmt_num(r["debt_value"], "")
        price = fmt_num(r["price"], "")
        lines.append("%s  %s  %-37s  %-37s  %s" % (qtxt, name, asset, debt, price))
    return box("🪙 Q-Münzenmatrix: Vermögen, Schulden und Marktpreis", lines, width=132, ansi=ansi, color="bright_yellow")


def render_q_debt_heatmap(sim, ansi=False):
    rows = _q_balances(sim)
    max_debt = max([r["debt_value"] for r in rows] + [1.0])
    lines = []
    lines.append("Legende: grün = kaum Schuld, gelb/orange = angespannt, rot = starke semantische Schuld")
    line = []
    for r in rows:
        ratio = r["debt_value"] / max_debt if max_debt > 0 else 0.0
        if ansi:
            if ratio < 0.05:
                cell = _ansi("●", "bright_green", enable=True)
            elif ratio < 0.35:
                cell = _ansi("●", "bright_yellow", enable=True)
            elif ratio < 0.70:
                cell = _ansi("●", "yellow", enable=True)
            else:
                cell = _ansi("●", "bright_red", enable=True)
        else:
            if ratio < 0.05:
                cell = "🟩"
            elif ratio < 0.35:
                cell = "🟨"
            elif ratio < 0.70:
                cell = "🟧"
            else:
                cell = "🟥"
        line.append("Q%02d%s %s" % (r["q"], cell, fmt_num(r["debt_value"], "", 1)))
        if len(line) == 4:
            lines.append("   ".join(line))
            line = []
    if line:
        lines.append("   ".join(line))
    top = sorted(rows, key=lambda r: r["debt_value"], reverse=True)[:5]
    lines.append("")
    lines.append("Top-Schuldmünzen: " + " │ ".join("Q%d %s %s" % (r["q"], r["name"], fmt_num(r["debt_value"], " ZW", 1)) for r in top))
    return box("🔥 Q-Schuld-Hitzekarte", lines, width=122, ansi=ansi, color="bright_red")


def render_shortage_map(sim, ansi=False):
    rows = sorted(_shortage_rows(sim), key=lambda r: r["shortage"], reverse=True)
    max_shortage = max([r["shortage"] for r in rows] + [1.0])
    lines = []
    for r in rows[:20]:
        price_ratio = r["price"] / max(0.0001, r["base_price"])
        lines.append(label_bar(r["label"], r["shortage"], max_shortage, width=22, suffix="", ansi=ansi, value_digits=1) + "  Preis×" + fmt_num(price_ratio, "", 2))
    return box("🧺 Güterengpässe und Preisdruck", lines, width=118, ansi=ansi, color="bright_green")


def render_sector_sales(sim, ansi=False):
    rows = sorted(_sector_rows(sim), key=lambda r: r["sales"], reverse=True)
    max_sales = max([r["sales"] for r in rows] + [1.0])
    max_profit = max([abs(r["profit"]) for r in rows] + [1.0])
    lines = []
    lines.append("Sektor                    Umsatzbild                         Profitbild                    Firmen  Auto")
    lines.append("────────────────────────  ────────────────────────────────  ──────────────────────────  ──────  ────")
    for r in rows[:24]:
        sales = rainbow_bar(r["sales"], max_sales, 16, ansi)
        profit = signed_bar("", r["profit"], max_profit, width=10, ansi=ansi, suffix="")
        # signed_bar mit leerem Label erzeugt Labelraum; kürzen wir ab:
        profit = profit.split("│", 1)[1] if "│" in profit else profit
        lines.append("%-24s  %-32s  %-26s  %6d  %.2f" % (
            r["label"][:24], sales + " " + fmt_num(r["sales"], "", 1), profit, r["firms"], r["automation"]))
    return box("🏭 Sektorenlandkarte: Umsatz, Profit und Automatisierung", lines, width=128, ansi=ansi, color="bright_blue")


def render_labor_landscape(sim, ansi=False):
    rows = sorted(_labor_rows(sim), key=lambda r: r["employed"], reverse=True)
    max_emp = max([r["employed"] for r in rows] + [1])
    max_wage = max([r["wage"] for r in rows] + [1.0])
    lines = []
    lines.append("Arbeitstyp                    Beschäftigung                         Lohnbild")
    lines.append("────────────────────────────  ───────────────────────────────────  ─────────────────────────")
    for r in rows:
        emp_bar = rainbow_bar(r["employed"], max_emp, 16, ansi) + " " + str(r["employed"]).rjust(4)
        wage_bar = rainbow_bar(r["wage"], max_wage, 10, ansi) + " " + fmt_num(r["wage"], " ZW", 2)
        lines.append("%-28s  %-38s  %s" % (r["label"][:28], emp_bar, wage_bar))
    return box("👷 Arbeitslandschaft: alle Arbeitsarten, nicht nur Intelligenzarbeit", lines, width=130, ansi=ansi, color="bright_green")


def render_public_credit_panel(sim, ansi=False):
    m = sim.metrics_history[-1] if sim.metrics_history else {}
    money = max(1.0, float(m.get("total_positive_money_value", 0.0) or 0.0))
    lines = []
    vals = [
        ("Steuereinnahmen", m.get("tax_revenue", 0.0), money),
        ("Transfers", m.get("transfer_spending", 0.0), money),
        ("öffentliche Käufe", m.get("public_spending", 0.0), money),
        ("Staatsnettovermögen", abs(m.get("government_net_worth", 0.0)), money),
        ("Kreditbestand", m.get("loan_outstanding", 0.0), money),
        ("neuer Kredit", m.get("new_credit_zw", 0.0), money),
        ("Rückzahlungen", m.get("repaid_zw", 0.0), money),
        ("Ausfallverluste", m.get("default_losses_zw", 0.0), money),
        ("Exporte", m.get("exports_value", 0.0), money),
        ("Importe", m.get("imports_value", 0.0), money),
    ]
    for label, v, maximum in vals:
        if label in ("Ausfallverluste", "Kreditbestand"):
            bar = risk_bar(float(v or 0.0) / maximum, 24, ansi)
        else:
            bar = rainbow_bar(v, maximum, 24, ansi)
        lines.append("%-22s │%s│ %s" % (label, bar, fmt_num(v, " ZW")))
    return box("🏦 Staat, Banken und Außenhandel", lines, width=112, ansi=ansi, color="bright_magenta")


def render_household_distribution(sim, ansi=False):
    buckets = _wealth_buckets(sim)
    max_c = max([b[1] for b in buckets] + [1])
    vals = [h.net_worth() for h in sim.households]
    lines = []
    lines.append("Haushaltsvermögen als Verteilung. Negative Bereiche zeigen Schuld- oder Armutspositionen.")
    for label, count, a, b in buckets:
        lines.append("%-28s │%s│ %4d" % (label[:28], rainbow_bar(count, max_c, 24, ansi), count))
    if vals:
        lines.append("")
        lines.append("Durchschnitt %s ZW │ Minimum %s ZW │ Maximum %s ZW │ Gini %s" % (
            fmt_num(mean(vals), ""), fmt_num(min(vals), ""), fmt_num(max(vals), ""), fmt_num(gini(vals), "", 3)))
    return box("👥 Haushalte, Vermögen und Ungleichheit", lines, width=116, ansi=ansi, color="bright_cyan")


def render_capital_automation(sim, ansi=False):
    rows = sorted(_sector_rows(sim), key=lambda r: (r["automation"], r["capital"]), reverse=True)
    max_capital = max([r["capital"] for r in rows] + [1.0])
    lines = []
    lines.append("Sektor                    Automatisierung                 Kapitalstock")
    lines.append("────────────────────────  ─────────────────────────────  ─────────────────────────────")
    for r in rows[:20]:
        auto = rainbow_bar(r["automation"], 1.0, 14, ansi) + " " + fmt_num(r["automation"], "", 2)
        cap = rainbow_bar(r["capital"], max_capital, 14, ansi) + " " + fmt_num(r["capital"], " ZW", 1)
        lines.append("%-24s  %-30s  %s" % (r["label"][:24], auto, cap))
    return box("🤖 Kapital- und Automatisierungslandschaft", lines, width=120, ansi=ansi, color="bright_yellow")


def render_q_flow(sim, ansi=False):
    rows = _q_balances(sim)
    debt_by_q = dict((r["q"], r["debt_value"]) for r in rows)
    asset_by_q = dict((r["q"], r["asset_value"]) for r in rows)
    max_debt = max(debt_by_q.values() or [1.0])
    def mark(q):
        d = debt_by_q.get(q, 0.0) / max(1.0, max_debt)
        a = asset_by_q.get(q, 0.0)
        if d > 0.65:
            return _ansi("⚠", "bright_red", enable=ansi) if ansi else "🔴"
        if d > 0.25:
            return _ansi("◆", "yellow", enable=ansi) if ansi else "🟧"
        if a > 0:
            return _ansi("●", "bright_green", enable=ansi) if ansi else "🟩"
        return "○"
    lines = []
    lines.append("Grundmünzen      Q1%s ── Q2%s ── Q3%s ── Q4%s" % (mark(1), mark(2), mark(3), mark(4)))
    lines.append("                    │       │       │       │")
    lines.append("Operationen       Q5%s ── Q6%s ── Q7%s ── Q8%s ── Q9%s" % (mark(5), mark(6), mark(7), mark(8), mark(9)))
    lines.append("                    │       │       │       │       │")
    lines.append("Systeme          Q10%s ─ Q11%s ─ Q12%s ─ Q13%s ─ Q14%s ─ Q15%s ─ Q16%s" % (mark(10), mark(11), mark(12), mark(13), mark(14), mark(15), mark(16)))
    lines.append("                    │       │       │       │       │       │       │")
    lines.append("Kapital          Q17%s ───────── Q18%s ───────── Q19%s ───────── Q20%s" % (mark(17), mark(18), mark(19), mark(20)))
    lines.append("")
    lines.append("Lesart: Aufgabe → Teilung → Modell → Form → Code/Regel/Delegation → Struktur/Dienst/Betrieb → Kompression/Architektur/Generierung/Maschine")
    return box("🧭 Q1→Q20-Produktionskette mit aktuellen Stressmarken", lines, width=132, ansi=ansi, color="bright_blue")


def render_risk_radar(sim, ansi=False):
    lines = []
    for label, ratio, value_text in _risk_items(sim):
        lines.append("%-20s │%s│ %s" % (label, risk_bar(ratio, 28, ansi), value_text))
    return box("🚨 Risiko-Radar der Q-Wirtschaft", lines, width=112, ansi=ansi, color="bright_red")


def render_event_timeline(sim, ansi=False, limit=12):
    events = sim.event_log.recent(limit)
    lines = []
    if not events:
        lines.append("Keine besonderen Ereignisse im Protokoll.")
    for ev in events:
        kind = ev.get("kind", "event")
        period = ev.get("period", "?")
        msg = ev.get("message", "")
        if ansi:
            if kind == "warning":
                kind_s = _ansi(kind, "bright_yellow", bold=True, enable=True)
            elif kind in ("default", "bankruptcy"):
                kind_s = _ansi(kind, "bright_red", bold=True, enable=True)
            else:
                kind_s = _ansi(kind, "bright_cyan", bold=True, enable=True)
        else:
            prefix = "🟨" if kind == "warning" else ("🟥" if kind in ("default", "bankruptcy") else "🟦")
            kind_s = prefix + kind
        lines.append("P%04s │ %-18s │ %s" % (period, kind_s, msg[:82]))
    return box("🕰 Ereignis-Timeline", lines, width=124, ansi=ansi, color="bright_cyan")


def render_policy_board(sim, ansi=False):
    m = sim.metrics_history[-1] if sim.metrics_history else {}
    debt = float(m.get("total_debt_value", 0.0) or 0.0)
    money = float(m.get("total_positive_money_value", 0.0) or 0.0)
    debt_ratio = debt / max(1.0, money)
    unemp = float(m.get("unemployment_rate", 0.0) or 0.0)
    inflation = float(m.get("inflation", 0.0) or 0.0)
    q18 = float(m.get("q18_debt_value", 0.0) or 0.0)
    q16 = float(m.get("q16_debt_value", 0.0) or 0.0)
    total_shortage = sum(float(m.get("shortage_%s" % g, 0.0) or 0.0) for g in GOODS)
    levers = []
    if q18 > debt * 0.12:
        levers.append(("Q18-Architekturprogramm", 0.90, "Architekturschuld begrenzen"))
    if q16 > debt * 0.12:
        levers.append(("Q16-Betriebsinfrastruktur", 0.85, "Ausführung und Versorgung sichern"))
    if unemp > 0.12:
        levers.append(("öffentliches Jobprogramm", 0.80, "Nachfrage + Qualifikation stabilisieren"))
    if inflation > 0.07:
        levers.append(("Engpassinvestitionen", 0.75, "Angebot statt blindes Geld erhöhen"))
    if total_shortage > 0:
        levers.append(("Import-/Inputpuffer", 0.60, "kurzfristige Güterknappheit glätten"))
    if debt_ratio > 0.50:
        levers.append(("Schuldenrestrukturierung", 0.70, "semantisch falsche Schulden drehen"))
    if not levers:
        levers.append(("produktive Investition", 0.55, "Wachstum ohne akuten Krisenmodus"))
        levers.append(("Q8/Q9/Q12-Commons", 0.50, "Wiederverwendung und Werkzeuge stärken"))
    lines = []
    for label, strength, reason in levers[:8]:
        lines.append("%-28s │%s│ %s" % (label, rainbow_bar(strength, 1.0, 18, ansi), reason))
    return box("🛠 Maßnahmenkarte: welche Hebel die Simulation nahelegt", lines, width=122, ansi=ansi, color="bright_green")


def build_visual_report(sim, markdown=True, ansi=False):
    """Erzeugt den vollständigen UTF-8-Art-Bericht."""
    title = "# Q-Wirtschaftssimulation – farbiger UTF-8-Art-Bericht" if markdown else "Q-Wirtschaftssimulation – farbiger UTF-8-Art-Bericht"
    intro = []
    intro.append(title)
    intro.append("")
    intro.append("Dieser Bericht ersetzt die trockene Endausgabe durch viele farbige UTF-8-Art-Darstellungen. Jede Abbildung beschreibt zuerst, was simuliert wird und warum diese Sicht wichtig ist. Danach folgt eine Auswertung, damit die Grafik nicht nur dekorativ ist, sondern ökonomisch lesbar wird.")
    intro.append("")
    intro.append("Die Farben sind bewusst kräftig: Regenbogenbalken stehen für positive Mengen, Produktion, Beschäftigung oder Verteilung; Risiko- und Schuldanzeigen gehen von Grün über Gelb/Orange nach Rot. In der Terminalfassung werden zusätzlich ANSI-Farben verwendet.")
    intro.append("")
    sections = []

    sections.append(section(
        "UTF-8 Art 01 – Makro-Cockpit",
        "Simuliert wird der Endzustand der gesamten Volkswirtschaft: BQP, Preisniveau, Inflation, Arbeitslosigkeit, Q-Geldmenge, Q-Schulden, Kreditbestand und Ungleichheit. Diese Darstellung ist wichtig, weil sie sichtbar macht, ob die Wirtschaft nur groß wirkt oder auch tragfähig ist. In einer Q-Ökonomie reicht ein hoher Umsatz nicht aus; entscheidend ist, ob Geld, Schuld, Arbeit und semantische Münzstruktur zusammenpassen.",
        render_macro_cockpit(sim, ansi=ansi),
        macro_evaluation(sim),
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 02 – BQP-Zeitpfad",
        "Simuliert wird die Entwicklung des Brutto-Q-Produkts beziehungsweise des Marktumsatzes über alle Perioden. Das BQP ist hier kein strenges reales Bruttoinlandsprodukt, sondern die beobachtete Wertbewegung im Simulationsmarkt. Die Kurve ist wichtig, weil sie zeigt, ob Produktion und Nachfrage wachsen, stagnieren oder in Krisenphasen einbrechen.",
        render_series_panel("📈 BQP und Marktumsatz im Zeitverlauf", [
            ("BQP", metrics_series(sim, "bqp"), " ZW", False, "bright_green"),
            ("Transaktionen", metrics_series(sim, "transactions"), "", False, "bright_cyan"),
            ("Exporte", metrics_series(sim, "exports_value"), " ZW", False, "bright_blue"),
        ], ansi=ansi),
        " ".join([
            trend_sentence(metrics_series(sim, "bqp"), "Das BQP", " ZW", False, True),
            trend_sentence(metrics_series(sim, "transactions"), "Die Zahl der Transaktionen", "", False, True),
            "Wenn BQP und Transaktionen auseinanderlaufen, entsteht ein Hinweis auf Preisveränderungen, Konzentration oder Exportabhängigkeit. Ein steigendes BQP mit fallenden Transaktionen kann zum Beispiel bedeuten, dass wenige teure Güter dominieren."
        ]),
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 03 – Geld, Kredit und Schulden",
        "Simuliert wird die monetäre Tragfähigkeit: positive Q-Geldmenge, Q-Schulden, Kreditbestand, neue Kredite, Rückzahlungen und Ausfallverluste. Die Darstellung ist notwendig, weil diese Wirtschaft semantische Schulden kennt. Eine hohe Schuld ist besonders kritisch, wenn sie in Betrieb, Architektur oder Maschinenfähigkeit liegt.",
        render_series_panel("💳 Q-Geld, Q-Schulden und Kreditdynamik", [
            ("positive Q-Geldmenge", metrics_series(sim, "total_positive_money_value"), " ZW", False, "bright_green"),
            ("Q-Schulden", metrics_series(sim, "total_debt_value"), " ZW", False, "bright_red"),
            ("Kreditbestand", metrics_series(sim, "loan_outstanding"), " ZW", False, "bright_yellow"),
            ("Ausfallverluste", metrics_series(sim, "default_losses_zw"), " ZW", False, "bright_magenta"),
        ], ansi=ansi),
        " ".join([
            trend_sentence(metrics_series(sim, "total_positive_money_value"), "Die positive Q-Geldmenge", " ZW", False, True),
            trend_sentence(metrics_series(sim, "total_debt_value"), "Die Q-Schulden", " ZW", False, False),
            trend_sentence(metrics_series(sim, "loan_outstanding"), "Der Kreditbestand", " ZW", False, None),
            "Gesund ist ein Kreditpfad nur dann, wenn die daraus finanzierte Produktion die passenden Q-Münzen erzeugt. Kredit, der nur Liquidität schafft, aber Q10-, Q16- oder Q18-Lücken vergrößert, wird später zur Strukturkrise."
        ]),
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 04 – Arbeitsmarkt und Löhne",
        "Simuliert wird der Arbeitsmarkt über Beschäftigung, Arbeitslosigkeit, Durchschnittslohn und die Verteilung auf alle Arbeitstypen. Das ist wichtig, weil das Modell ausdrücklich eine ganze Wirtschaft abbildet: Landwirtschaft, Bau, Pflege, Handel, Industrie, Energie, Forschung, Software/KI und viele andere Arbeitsformen. Arbeit ist hier nicht nur Intelligenzarbeit, sondern gesellschaftliche Produktionsfähigkeit.",
        "\n".join([
            render_series_panel("👥 Beschäftigung, Arbeitslosigkeit und Lohn", [
                ("Arbeitslosigkeit", metrics_series(sim, "unemployment_rate"), "", True, "bright_red"),
                ("Beschäftigte", metrics_series(sim, "employed"), "", False, "bright_green"),
                ("Durchschnittslohn", metrics_series(sim, "avg_wage"), " ZW", False, "bright_yellow"),
            ], ansi=ansi),
            render_labor_landscape(sim, ansi=ansi),
        ]),
        " ".join([
            trend_sentence(metrics_series(sim, "unemployment_rate"), "Die Arbeitslosigkeit", "", True, False),
            trend_sentence(metrics_series(sim, "avg_wage"), "Der Durchschnittslohn", " ZW", False, True),
            "Die Beschäftigungsbalken zeigen, ob die Volkswirtschaft breit arbeitet oder nur einzelne Bereiche übernutzt. Ein gesundes System braucht nicht nur Software/KI, sondern Nahrung, Energie, Bau, Pflege, Logistik, Bildung, Wartung und öffentliche Dienste."
        ]),
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 05 – Preisniveau und Inflation",
        "Simuliert wird, wie sich Preisindex und Inflation über die Perioden bewegen. Diese Sicht ist wichtig, weil Preisdruck in der Q-Ökonomie nicht nur Geldmengenproblem ist. Preissteigerungen können aus realen Güterengpässen, falscher Q-Struktur, Kreditüberdehnung oder mangelnder Betriebsfähigkeit entstehen.",
        render_series_panel("🌡 Preisindex und Inflation", [
            ("Preisindex", metrics_series(sim, "price_index"), "", False, "bright_yellow"),
            ("Inflation", metrics_series(sim, "inflation"), "", True, "bright_red"),
            ("Importe", metrics_series(sim, "imports_value"), " ZW", False, "bright_blue"),
        ], ansi=ansi),
        " ".join([
            trend_sentence(metrics_series(sim, "price_index"), "Der Preisindex", "", False, False),
            trend_sentence(metrics_series(sim, "inflation"), "Die Inflation", "", True, False),
            "Importe wirken als Puffer, aber nicht als unbegrenzte Rettung. Wenn Importwerte steigen, während Engpässe bestehen bleiben, liegt wahrscheinlich ein strukturelles Angebotsproblem vor."
        ]),
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 06 – Q-Münzenmatrix",
        "Simuliert wird die vollständige semantische Bilanz aller Münzen Q1 bis Q20: positive Bestände, Schulden und Marktpreise. Diese Darstellung ist das Herz der Q-Wirtschaft. Sie zeigt nicht nur, wie viel Wert vorhanden ist, sondern welche Art von Wert fehlt oder dominiert. Vier Q1 sind nominal so viel wert wie eine Q20, aber sie ersetzen keine fertige Maschine.",
        render_q_balance_matrix(sim, ansi=ansi),
        "Die Matrix macht sichtbar, ob die Wirtschaft in niedrigen Grundmünzen, mittleren Operationsmünzen oder hohen System- und Kapitalmünzen konzentriert ist. Rote Schuldsegmente in Q16, Q18, Q19 oder Q20 sind besonders ernst, weil sie Betrieb, Architektur, Generierung und fertige Module betreffen. Hohe Bestände bei Q5 ohne passende Q10/Q18-Deckung deuten auf Code- oder Produktionsblasen hin.",
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 07 – Q-Schuld-Hitzekarte",
        "Simuliert wird die Konzentration der Q-Schulden nach Münzart. Die Hitzekarte ist wichtig, weil sie sofort zeigt, an welcher semantischen Stelle die Wirtschaft unter Druck steht. Eine Grundschuld Q1 ist eine ungelöste Aufgabe; eine Q18-Schuld ist fehlende Architektur; eine Q20-Schuld ist fehlende Maschinen- oder Modulreife.",
        render_q_debt_heatmap(sim, ansi=ansi),
        "Die gefährlichsten Felder sind die dunkelsten oder rötesten Felder. Sie zeigen nicht nur finanzielle Last, sondern fehlende Fähigkeit. Wenn die Top-Schulden in System- oder Kapitalmünzen liegen, sollte die Politik nicht einfach Nachfrage erhöhen, sondern gezielt Struktur, Betrieb, Architektur oder Modulbau fördern.",
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 08 – Güterengpässe",
        "Simuliert wird, welche realen Güter und Dienste nicht ausreichend verfügbar waren. Diese Sicht verbindet das Q-System mit der gewöhnlichen Wirtschaft: Nahrung, Energie, Wohnen, Gesundheit, Bildung, Transport, Industrie, Kultur, Sicherheit und weitere Güter. Die Begründung ist einfach: Eine Währung bleibt abstrakt, wenn sie nicht in reale Versorgung übersetzt wird.",
        render_shortage_map(sim, ansi=ansi),
        "Hohe Engpässe zeigen, dass die Nachfrage nicht durch Produktion, Importe oder öffentliche Stabilisierung gedeckt wurde. Entscheidend ist der Zusammenhang zwischen Engpass und Preisverhältnis. Ein hoher Engpass mit starkem Preisaufschlag ist ein harter Angebotsmangel; ein hoher Engpass ohne Preisreaktion kann auf Marktträgheit oder staatliche Puffer hindeuten.",
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 09 – Sektorenlandkarte",
        "Simuliert wird die Wirtschaftsstruktur nach Sektoren: Umsatz, Profit, Anzahl der Firmen und Automatisierungsgrad. Diese Abbildung ist wichtig, weil eine vollständige Volkswirtschaft nicht an einem einzigen Sektor hängt. Landwirtschaft, Rohstoffe, Energie, Industrie, Bau, Gesundheit, Bildung, Logistik, Handel, Finanzwesen, öffentlicher Dienst, Kultur, Wartung, Forschung, Umwelt und Sicherheit müssen zusammenwirken.",
        render_sector_sales(sim, ansi=ansi),
        "Die größten Umsatzbalken zeigen, wo die Nachfrage konzentriert ist. Die Profitbalken zeigen, ob Sektoren Kapital aufbauen oder ausbluten. Negative Profitzonen können auf Preisdeckel, Inputmangel, zu geringe Nachfrage oder hohe Schuldlast hinweisen. Ein hoher Automatisierungswert ist produktiv, wird aber riskant, wenn Beschäftigung, Qualifikation oder Q10/Q16/Q18-Struktur nicht mitwachsen.",
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 10 – Staat, Banken und Außenhandel",
        "Simuliert werden öffentliche Finanzen, Kreditkanäle und der Außenhandel. Diese Darstellung ist nötig, weil Krisen nicht nur innerhalb von Firmen entstehen. Staatliche Transfers, öffentliche Käufe, Kredite, Rückzahlungen, Ausfälle, Exporte und Importe stabilisieren oder destabilisieren das ganze System.",
        render_public_credit_panel(sim, ansi=ansi),
        "Ein tragfähiger Staat stabilisiert, ohne nur Schulden zu verschieben. Hohe öffentliche Käufe sind produktiv, wenn sie Q16-Infrastruktur, Q12-Werkzeuge, Bildung, Gesundheit oder Gemeingüter erzeugen. Banken sind nützlich, wenn Kredit echte Transformation finanziert; sie werden gefährlich, wenn Ausfälle steigen und die Kredite semantische Lücken nur verdecken.",
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 11 – Haushalte und Ungleichheit",
        "Simuliert wird die Verteilung des Haushaltsvermögens. Diese Abbildung ist wichtig, weil eine Wirtschaft auch dann instabil werden kann, wenn die Gesamtsumme gut aussieht, aber Haushalte keinen Zugang zu Arbeit, Bildung, Gesundheit oder Konsum haben. Ungleichheit schwächt Nachfrage, soziale Stabilität und die Fähigkeit, neue Q1-Aufgaben produktiv zu bearbeiten.",
        render_household_distribution(sim, ansi=ansi),
        "Die Verteilung zeigt, ob das Vermögen breit liegt oder in wenigen oberen Bereichen konzentriert ist. Ein hoher Gini-Wert bedeutet nicht automatisch Zusammenbruch, aber er zeigt, dass Teilhabe und Nachfrage enger werden. In einer Q-Wirtschaft ist das besonders relevant, weil Bildung und Fähigkeiten bestimmen, welche Münzen Haushalte überhaupt erzeugen können.",
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 12 – Kapital und Automatisierung",
        "Simuliert wird, welche Sektoren Kapitalstock und Automatisierungsgrad aufbauen. Diese Sicht ist wichtig, weil Automatisierung nicht nur Software/KI bedeutet. Auch Industrie, Logistik, Energie, Bau, Gesundheit, Verwaltung, Landwirtschaft und Wartung können automatisiert oder kapitalintensiver werden. Produktiv ist das nur, wenn die menschliche und institutionelle Struktur nachzieht.",
        render_capital_automation(sim, ansi=ansi),
        "Sektoren mit hohem Kapital und hoher Automatisierung können Produktivität stark erhöhen. Sie können aber auch Beschäftigung verdrängen oder Q16-/Q18-Schulden erzeugen, wenn Betrieb und Architektur nicht ausreichend mitwachsen. Eine gesunde Automatisierungswelle braucht Ausbildung, Wartung, Schnittstellen und robuste Betriebsinfrastruktur.",
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 13 – Q1 bis Q20 als Produktionskette",
        "Simuliert wird die Grundbewegung der Q-Ökonomie: Aufgabe wird zu Teilung, Modell, Form, Operation, System, Architektur, Generierung und schließlich Modul oder Maschine. Diese Darstellung ist begründet, weil sie den Sinn der Münzen sichtbar macht. Die Wirtschaft produziert nicht nur Ware, sondern die Verwandlung von Schwierigkeit in funktionsfähige Struktur.",
        render_q_flow(sim, ansi=ansi),
        "Die Markierungen zeigen, welche Stationen solide und welche belastet sind. Besonders kritisch ist ein Bruch zwischen Q5/Q13 und Q18/Q20: dann gibt es viel Implementierung oder Dienste, aber zu wenig Architektur und Modulreife. Ein Bruch zwischen Q1 und Q3 bedeutet dagegen, dass Aufgaben nicht gut verstanden oder modelliert werden.",
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 14 – Risiko-Radar",
        "Simuliert wird die Krisenanfälligkeit der Wirtschaft anhand mehrerer Stressachsen: Arbeitslosigkeit, Schuldenlast, Inflation, Architektur- und Betriebsschuld, Güterengpässe, Ungleichheit und Kreditausfälle. Diese Darstellung ist wichtig, weil Krisen selten aus nur einer Kennzahl entstehen. Sie entstehen durch Koppelungen.",
        render_risk_radar(sim, ansi=ansi),
        "Rote oder stark gefüllte Balken sind die vorrangigen Krisenkanäle. Wenn mehrere Achsen gleichzeitig hoch stehen, sollte die Reaktion nicht eindimensional sein. Zum Beispiel löst Geldpolitik allein keine Architekturschuld, und ein Jobprogramm allein löst keinen Energieengpass. Die Q-Ökonomie verlangt gezielte Reparatur nach Münzart und Sektor.",
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 15 – Ereignis-Timeline",
        "Simuliert wird die zeitliche Folge wichtiger Ereignisse: Warnungen, Defaults, Insolvenzen, öffentliche Programme oder andere Stresssignale. Diese Abbildung ist wichtig, weil Kennzahlen nur Zustände zeigen, während Ereignisse den Verlauf erklären. Eine Krise entsteht nicht plötzlich; sie sammelt Vorzeichen.",
        render_event_timeline(sim, ansi=ansi),
        "Die Timeline hilft, Ursachen zu sortieren. Häufen sich Warnungen früh, dann war die Endlage vorbereitet. Häufen sich Defaults spät, kann eine Kredit- oder Liquiditätskrise entstanden sein. Treten viele öffentliche Maßnahmen auf, war der Staat bereits als Stabilisator aktiv und sollte auf Wirksamkeit geprüft werden.",
        markdown=markdown))

    sections.append(section(
        "UTF-8 Art 16 – Maßnahmenkarte",
        "Simuliert wird keine automatische Wahrheit, sondern eine Priorisierung möglicher wirtschaftspolitischer Hebel aus dem Endzustand. Die Karte begründet, wo Interventionen ansetzen könnten: Schuldenrestrukturierung, Q18-Architekturprogramm, Q16-Betriebsinfrastruktur, öffentliches Jobprogramm, Engpassinvestitionen, Commons-Fonds oder Importpuffer.",
        render_policy_board(sim, ansi=ansi),
        "Die Maßnahmenkarte ist kein Befehl, sondern eine Diagnoseübersetzung. Sie zeigt, welche Hebel nach den gemessenen Stresspunkten plausibel sind. Der wichtigste Grundsatz bleibt: keine abstrakte Geldflutung, wenn eine semantische Münzlücke vorliegt. Die passende Münze muss repariert oder produktiv erzeugt werden.",
        markdown=markdown))

    return "\n".join(intro + sections)


def build_terminal_dashboard(sim, ansi=True):
    """Konsolenfassung. Etwas kompakter, aber mit denselben Art-Prinzipien."""
    return build_visual_report(sim, markdown=False, ansi=ansi)


def write_visual_report(path, sim, markdown=True, ansi=False):
    text = build_visual_report(sim, markdown=markdown, ansi=ansi)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def format_progress_line(period, total_periods, metrics, ansi=True):
    ratio = float(period) / max(1.0, float(total_periods))
    progress = rainbow_bar(ratio, 1.0, width=18, ansi=ansi)
    unemp = float(metrics.get("unemployment_rate", 0.0) or 0.0)
    debt = float(metrics.get("total_debt_value", 0.0) or 0.0)
    bqp = float(metrics.get("bqp", 0.0) or 0.0)
    infl = float(metrics.get("inflation", 0.0) or 0.0)
    return "%s P%04d/%04d │ BQP %s │ AL %s │ Infl %s │ Schuld %s" % (
        progress, period, total_periods, fmt_num(bqp, " ZW", 1), fmt_pct(unemp), fmt_pct(infl), fmt_num(debt, " ZW", 1)
    )


def build_scenario_comparison_art(rows, markdown=True, ansi=False):
    """UTF-8-Art-Bericht für tools/compare_scenarios.py."""
    title = "# Szenariovergleich – farbige UTF-8-Art" if markdown else "Szenariovergleich – farbige UTF-8-Art"
    lines = [title, ""]
    lines.append("Verglichen werden mehrere politische und wirtschaftliche Szenarien. Die Abbildungen zeigen nicht nur Endwerte, sondern machen sichtbar, welche Szenarien Wachstum, Beschäftigung, Schulden, Preisstabilität und Verteilung unterschiedlich gewichten.")
    lines.append("")
    if not rows:
        lines.append("Keine Szenarien vorhanden.")
        return "\n".join(lines)
    max_bqp = max(float(r.get("bqp", 0.0) or 0.0) for r in rows) or 1.0
    max_debt = max(float(r.get("total_debt_value", 0.0) or 0.0) for r in rows) or 1.0
    def art_block(title_text, metric_key, maximum, percent=False, risk=False):
        art_lines = []
        for r in rows:
            val = float(r.get(metric_key, 0.0) or 0.0)
            if risk:
                bar = risk_bar(val / maximum if maximum else 0.0, 24, ansi)
            else:
                bar = rainbow_bar(val, maximum, 24, ansi)
            shown = fmt_pct(val) if percent else fmt_num(val, " ZW" if "debt" in metric_key or metric_key == "bqp" else "")
            art_lines.append("%-22s │%s│ %s" % (str(r.get("scenario", "?"))[:22], bar, shown))
        return box(title_text, art_lines, width=112, ansi=ansi, color="bright_cyan")
    sections = [
        ("UTF-8 Art A – BQP nach Szenario", "Simuliert wird, welches Szenario den höchsten Endumsatz beziehungsweise das höchste Brutto-Q-Produkt erreicht. Das ist wichtig, weil Wachstum ohne Stabilität nicht reicht, aber fehlendes Wachstum ebenfalls soziale und fiskalische Spannungen erzeugt.", art_block("📈 BQP-Vergleich", "bqp", max_bqp, False, False), "Hohe Balken zeigen starke Endproduktion. Sie sollten zusammen mit Schulden, Arbeitslosigkeit und Inflation gelesen werden. Das beste Szenario ist nicht automatisch das größte, sondern das mit tragfähigem Wachstum."),
        ("UTF-8 Art B – Arbeitslosigkeit nach Szenario", "Simuliert wird, wie stark die Szenarien Beschäftigung sichern oder verdrängen. Das ist besonders wichtig bei Automatisierung, Sparpolitik und Krisenszenarien, weil der Arbeitsmarkt gesellschaftliche Stabilität und Nachfrage trägt.", art_block("👷 Arbeitslosigkeit-Vergleich", "unemployment_rate", 0.30, True, True), "Rote oder lange Risikobalken zeigen Szenarien, in denen Arbeit nicht ausreichend absorbiert wird. Dann braucht die Wirtschaft entweder neue Sektoren, Bildung, öffentliche Beschäftigung oder eine andere Verteilung der Automatisierungsgewinne."),
        ("UTF-8 Art C – Schulden nach Szenario", "Simuliert wird die Endlast der Q-Schulden. Diese Sicht ist entscheidend, weil hohe Schulden in einer semantischen Währung nicht nur Betrag, sondern fehlende Münzfähigkeit bedeuten.", art_block("💳 Q-Schulden-Vergleich", "total_debt_value", max_debt, False, True), "Szenarien mit hoher Schuld müssen nach Schuldart geprüft werden. Eine hohe Q18- oder Q16-Schuld ist strukturell gefährlicher als viele kleine Grundaufgaben."),
        ("UTF-8 Art D – Ungleichheit nach Szenario", "Simuliert wird die Verteilungslage der Haushalte über den Gini-Wert. Diese Sicht ist wichtig, weil eine Volkswirtschaft nicht nur Gesamtleistung, sondern auch Teilhabe und Nachfragebreite braucht.", art_block("👥 Gini-Vergleich", "household_gini", 0.65, False, True), "Hohe Gini-Balken zeigen, dass die Vorteile der Simulation ungleich ankommen. Das kann Konsumnachfrage schwächen und langfristig Bildungs- und Fähigkeitsbildung blockieren."),
    ]
    for title_text, desc, art, eval_text in sections:
        lines.append(section(title_text, desc, art, eval_text, markdown=markdown))
    return "\n".join(lines)
