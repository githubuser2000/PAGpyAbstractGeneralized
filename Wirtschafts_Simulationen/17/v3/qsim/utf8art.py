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
import re
import shutil
import textwrap
import unicodedata
from collections import defaultdict

from .money import Q_META, Q_VALUES
from .sectors import GOODS, SECTOR_RECIPES, LABOR_TYPES
from .utils import clamp, mean, gini
from .i18n import normalize_language, t, section_title, section_name, section_description, section_evaluation, q_name_lang, SECTION_KEYS

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


ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def char_width(ch):
    """Approximate terminal cell width for Unicode without external wcwidth."""
    if not ch:
        return 0
    o = ord(ch)
    if ch == "\n" or ch == "\r":
        return 0
    if ch == "\t":
        return 4
    if unicodedata.combining(ch):
        return 0
    if o in (0x200D, 0xFE0E, 0xFE0F):  # zero-width joiner / variation selectors
        return 0
    if unicodedata.category(ch) in ("Cc", "Cf"):
        return 0
    # Most emoji and CJK full-width characters occupy two terminal cells.
    if unicodedata.east_asian_width(ch) in ("F", "W"):
        return 2
    if 0x1F000 <= o <= 0x1FAFF:
        return 2
    return 1


def strip_ansi(s):
    return ANSI_RE.sub("", str(s))


def visible_len(s):
    """Visible terminal width without ANSI control sequences."""
    text = strip_ansi(s)
    return sum(char_width(ch) for ch in text)


def detect_screen_width(margin=5, fallback=100, minimum=40, maximum=240):
    """Return detected terminal columns minus a safety margin.

    The user requested automatic screen width detection and exactly five
    characters of safety space.  The fallback keeps report files readable when
    stdout is not an interactive terminal.
    """
    try:
        cols = shutil.get_terminal_size((int(fallback), 25)).columns
    except Exception:
        cols = int(fallback)
    try:
        margin = int(margin)
    except Exception:
        margin = 5
    return max(int(minimum), min(int(maximum), int(cols) - margin))


def normalize_width(width=None, margin=5):
    if width is None or str(width).strip().lower() in ("", "auto", "screen", "terminal"):
        return detect_screen_width(margin=margin)
    try:
        w = int(width)
    except Exception:
        return detect_screen_width(margin=margin)
    return max(40, min(240, w))


def fit_width(requested=None, margin=5):
    detected = detect_screen_width(margin=margin)
    if requested is None or str(requested).strip().lower() in ("", "auto", "screen", "terminal"):
        return detected
    try:
        req = int(requested)
    except Exception:
        return detected
    return max(40, min(req, detected, 240))


def trim_display(s, max_width, ellipsis="…"):
    """Trim a string to max terminal cells, preserving ANSI where possible."""
    text = str(s)
    max_width = max(0, int(max_width))
    if visible_len(text) <= max_width:
        return text
    if max_width <= 0:
        return ""
    ell_w = visible_len(ellipsis)
    target = max(0, max_width - ell_w)
    out = []
    width = 0
    i = 0
    active_ansi = False
    while i < len(text):
        if text[i] == "\033":
            m = ANSI_RE.match(text, i)
            if m:
                code = m.group(0)
                out.append(code)
                active_ansi = True
                if code == ANSI.get("reset"):
                    active_ansi = False
                i = m.end()
                continue
        ch = text[i]
        cw = char_width(ch)
        if width + cw > target:
            break
        out.append(ch)
        width += cw
        i += 1
    out.append(ellipsis)
    if active_ansi:
        out.append(ANSI["reset"])
    return "".join(out)


def _split_display_long_line(line, width):
    width = max(10, int(width or 80))
    out = []
    cur = []
    cur_w = 0
    for ch in str(line):
        cw = char_width(ch)
        if cur and cur_w + cw > width:
            out.append("".join(cur))
            cur = []
            cur_w = 0
        cur.append(ch)
        cur_w += cw
    if cur:
        out.append("".join(cur))
    return out or [""]


def wrap_plain_text(text, width):
    """Wrap prose by terminal display width, including CJK and emoji."""
    width = max(20, int(width or 80))
    lines = []
    for para in str(text).splitlines() or [""]:
        if not para.strip():
            lines.append("")
            continue
        # Prefer word wrapping where it works, then split any visually overlong
        # fragments by actual display width.
        candidates = textwrap.wrap(para, width=width, break_long_words=True, replace_whitespace=False) or [para]
        for candidate in candidates:
            if visible_len(candidate) <= width:
                lines.append(candidate)
            else:
                lines.extend(_split_display_long_line(candidate, width))
    return "\n".join(lines)


def pad_display(text, width):
    trimmed = trim_display(text, width)
    return trimmed + " " * max(0, int(width) - visible_len(trimmed))


def compact_label(label, max_width):
    return pad_display(str(label), max_width)

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


def label_bar(label, value, maximum, width=26, suffix="", ansi=False, value_digits=2, label_width=26):
    lab = pad_display(label, label_width)
    bar = rainbow_bar(value, maximum, width=width, ansi=ansi)
    return "%s │%s│ %s" % (lab, bar, fmt_num(value, suffix, value_digits))


def signed_bar(label, value, maximum, width=24, ansi=False, suffix=" ZW", label_width=24):
    lab = pad_display(label, label_width)
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


def box(title, lines, width=98, ansi=False, color="bright_cyan", screen_width=None):
    """Draw a bordered UTF-8 window that never exceeds screen width minus margin."""
    width = fit_width(screen_width if screen_width is not None else width)
    width = max(width, 40)
    content_width = max(8, width - 4)
    top = "╔" + "═" * (width - 2) + "╗"
    mid_title_raw = pad_display(trim_display(title, content_width), content_width)
    mid_title = "║ " + mid_title_raw + " ║"
    sep = "╠" + "═" * (width - 2) + "╣"
    bottom = "╚" + "═" * (width - 2) + "╝"
    out = [_ansi(top, color, enable=ansi), _ansi(mid_title, color, bold=True, enable=ansi), _ansi(sep, color, enable=ansi)]
    for line in lines:
        raw = trim_display(str(line), content_width)
        pad = max(0, content_width - visible_len(raw))
        out.append(_ansi("║ ", color, enable=ansi) + raw + " " * pad + _ansi(" ║", color, enable=ansi))
    out.append(_ansi(bottom, color, enable=ansi))
    return "\n".join(out)

def section(title, description, art, evaluation, markdown=True, language="en", width=None):
    lang = normalize_language(language)
    w = fit_width(width)
    if markdown:
        return "\n".join([
            "## " + title,
            "",
            "### " + t(lang, "desc_header"),
            wrap_plain_text(description.strip(), w),
            "",
            "```text",
            art.rstrip(),
            "```",
            "",
            "### " + t(lang, "eval_header"),
            wrap_plain_text(evaluation.strip(), w),
            "",
        ])
    rule = "─" * min(w, max(10, visible_len(title)))
    return "\n".join([
        "\n" + title,
        rule,
        wrap_plain_text(description.strip(), w),
        "",
        art.rstrip(),
        "",
        t(lang, "eval_header") + ":",
        wrap_plain_text(evaluation.strip(), w),
        "",
    ])

def metrics_series(sim, key):
    return [float(m.get(key, 0.0) or 0.0) for m in sim.metrics_history]


def last_metric(sim, key, default=0.0):
    if sim.metrics_history:
        return sim.metrics_history[-1].get(key, default)
    return default


def trend_sentence(values, label, unit="", percent=False, good_high=None, language="en"):
    lang = normalize_language(language)
    vals = [float(v or 0.0) for v in values]
    if not vals:
        if lang == "de":
            return "%s wurde nicht gemessen." % label
        return "%s was not measured." % label
    start = vals[0]
    end = vals[-1]
    lo = min(vals)
    hi = max(vals)
    diff = end - start
    stable = abs(diff) < max(1e-9, abs(start) * 0.01)
    if percent:
        start_s = fmt_pct(start); end_s = fmt_pct(end); lo_s = fmt_pct(lo); hi_s = fmt_pct(hi)
    else:
        start_s = fmt_num(start, unit); end_s = fmt_num(end, unit); lo_s = fmt_num(lo, unit); hi_s = fmt_num(hi, unit)
    if lang == "de":
        direction = "blieb weitgehend stabil" if stable else ("stieg" if diff > 0 else "fiel")
        sentence = "%s %s von %s auf %s; der beobachtete Korridor lag zwischen %s und %s." % (label, direction, start_s, end_s, lo_s, hi_s)
        if good_high is not None and not stable:
            sentence += " Die Richtung ist für diese Kennzahl grundsätzlich %s." % ("günstig" if ((diff > 0 and good_high) or (diff < 0 and not good_high)) else "belastend")
        return sentence
    # For all non-German report languages keep the dynamic trend sentence in English;
    # the surrounding report text is localized and the numbers stay comparable.
    direction = "remained largely stable" if stable else ("rose" if diff > 0 else "fell")
    sentence = "%s %s from %s to %s; the observed range was between %s and %s." % (label, direction, start_s, end_s, lo_s, hi_s)
    if good_high is not None and not stable:
        sentence += " The direction is generally %s for this indicator." % ("favorable" if ((diff > 0 and good_high) or (diff < 0 and not good_high)) else "burdensome")
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


def _risk_items(sim, language="en"):
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
    if normalize_language(language) == "de":
        labels = ["Arbeitslosigkeit", "Schuldenlast", "Inflationsdruck", "Q18-Architektur", "Q16-Betrieb", "Güterengpässe", "Ungleichheit", "Kreditausfälle"]
        debt_text = " Schulden/Geld"; shortage_suffix = " ungedeckt"
    else:
        labels = [t(language, "unemployment"), "Debt load", "Inflation pressure", "Q18 Architecture", "Q16 Operation", "Goods shortages", "Inequality", "Credit defaults"]
        debt_text = " debt/money"; shortage_suffix = " unmet"
    return [
        (labels[0], clamp(float(m.get("unemployment_rate", 0.0) or 0.0) / 0.30, 0.0, 1.0), fmt_pct(m.get("unemployment_rate", 0.0))),
        (labels[1], clamp(debt_ratio / 0.85, 0.0, 1.0), fmt_num(debt_ratio, "", 2) + debt_text),
        (labels[2], clamp(abs(float(m.get("inflation", 0.0) or 0.0)) / 0.15, 0.0, 1.0), fmt_pct(m.get("inflation", 0.0))),
        (labels[3], clamp(q18_ratio / 0.25, 0.0, 1.0), fmt_pct(q18_ratio)),
        (labels[4], clamp(q16_ratio / 0.25, 0.0, 1.0), fmt_pct(q16_ratio)),
        (labels[5], clamp(shortage_ratio / 0.30, 0.0, 1.0), fmt_num(total_shortage, shortage_suffix, 1)),
        (labels[6], clamp(float(m.get("household_gini", 0.0) or 0.0) / 0.65, 0.0, 1.0), fmt_num(m.get("household_gini", 0.0), " Gini", 3)),
        (labels[7], clamp(default_ratio / 0.08, 0.0, 1.0), fmt_num(m.get("default_losses_zw", 0.0), " ZW", 2)),
    ]


def render_macro_cockpit(sim, ansi=False, language="en", width=None):
    m = sim.metrics_history[-1] if sim.metrics_history else {}
    money = float(m.get("total_positive_money_value", 0.0) or 0.0)
    debt = float(m.get("total_debt_value", 0.0) or 0.0)
    debt_ratio = debt / max(1.0, money)
    lines = []
    lines.append("%s: %-20s %s: %-5s %s: %-5s %s: %-5s %s: %-3s" % (
        t(language, "scenario"), sim.scenario, t(language, "periods"), sim.period, t(language, "households"), len(sim.households), t(language, "firms"), len(sim.firms), t(language, "banks"), len(sim.banks)))
    lines.append(pad_display(t(language, "bqp_market"), 22) + " " + rainbow_bar(m.get("bqp", 0.0), max(1.0, m.get("bqp", 1.0), money * 0.05), 26, ansi) + "  " + fmt_num(m.get("bqp", 0.0), " ZW"))
    lines.append(pad_display(t(language, "price_index"), 22) + " " + rainbow_bar(m.get("price_index", 0.0), max(2.0, m.get("price_index", 0.0)), 26, ansi) + "  " + fmt_num(m.get("price_index", 0.0), ""))
    lines.append(pad_display(t(language, "unemployment"), 22) + " " + risk_bar(m.get("unemployment_rate", 0.0) / 0.30, 26, ansi) + "  " + fmt_pct(m.get("unemployment_rate", 0.0)))
    lines.append(pad_display(t(language, "inflation_last"), 22) + " " + risk_bar(abs(m.get("inflation", 0.0)) / 0.15, 26, ansi) + "  " + fmt_pct(m.get("inflation", 0.0)))
    lines.append(pad_display(t(language, "q_money_positive"), 22) + " " + rainbow_bar(money, max(1.0, money, debt), 26, ansi) + "  " + fmt_num(money, " ZW"))
    lines.append(pad_display(t(language, "q_debt"), 22) + " " + risk_bar(debt_ratio / 0.85, 26, ansi) + "  " + fmt_num(debt, " ZW") + "  " + t(language, "ratio") + " " + fmt_num(debt_ratio, ""))
    lines.append(pad_display(t(language, "credit_stock"), 22) + " " + risk_bar(float(m.get("loan_outstanding", 0.0) or 0.0) / max(1.0, money), 26, ansi) + "  " + fmt_num(m.get("loan_outstanding", 0.0), " ZW"))
    lines.append(pad_display(t(language, "household_gini"), 22) + " " + risk_bar(float(m.get("household_gini", 0.0) or 0.0) / 0.65, 26, ansi) + "  " + fmt_num(m.get("household_gini", 0.0), ""))
    return box("🌈 " + t(language, "report_title").replace(" – ", " — ").split(" — ")[0], lines, width=112, ansi=ansi, color="bright_cyan", screen_width=width)


def macro_evaluation(sim, language="en"):
    lang = normalize_language(language)
    m = sim.metrics_history[-1] if sim.metrics_history else {}
    money = float(m.get("total_positive_money_value", 0.0) or 0.0)
    debt = float(m.get("total_debt_value", 0.0) or 0.0)
    debt_ratio = debt / max(1.0, money)
    if lang == "de":
        parts = ["Das Cockpit zeigt den Endzustand der Simulation. Entscheidend ist die Gleichzeitigkeit von realem Umsatz, Q-Geldmenge, Q-Schulden, Beschäftigung und Preisniveau. Diese Größen dürfen nicht isoliert gelesen werden: Eine Wirtschaft kann hohe Umsätze haben und trotzdem semantisch krank sein, wenn die Schulden in Q16, Q18 oder Q20 liegen."]
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
    parts = ["The cockpit shows the final state of the simulation. The decisive point is the simultaneous reading of real turnover, Q money, Q debt, employment and the price level. These indicators must not be read in isolation: an economy can have high turnover and still be semantically unhealthy if its debt sits in Q16, Q18 or Q20."]
    if debt_ratio > 0.65:
        parts.append("The debt load is high. In this system that is more dangerous than in a pure number currency because every debt means a specific coin type. The economy needs not only more value but the right repair capacity.")
    elif debt_ratio > 0.35:
        parts.append("The debt load is visible but still manageable. The next check is whether it is concentrated in operational coins or in system and capital coins.")
    else:
        parts.append("Debt appears relatively low. That leaves room for productive investment as long as money is not concentrated only in low coins.")
    if float(m.get("unemployment_rate", 0.0) or 0.0) > 0.18:
        parts.append("Unemployment is a clear stress point. The model then points to skill mismatch, weak demand, automation pressure or sectoral misallocation.")
    if abs(float(m.get("inflation", 0.0) or 0.0)) > 0.08:
        parts.append("The latest inflation is strong. That signals bottlenecks, overly fast credit expansion or a goods structure that cannot keep up with the Q money structure.")
    return " ".join(parts)

def render_series_panel(title, series_specs, ansi=False, width=72, language="en", screen_width=None):
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
        lines.append(pad_display(label, 22) + " " + sparkline(vals, width=width, ansi=ansi, color=color))
        lines.append(" " * 23 + "%s %s │ %s %s │ %s %s │ %s %s" % (t(language, "start"), start, t(language, "end"), end, t(language, "min"), lo, t(language, "max"), hi))
    return box(title, lines, width=118, ansi=ansi, color="bright_magenta", screen_width=screen_width)


def render_q_balance_matrix(sim, ansi=False, language="en", width=None):
    rows = _q_balances(sim)
    max_asset = max([r["asset_value"] for r in rows] + [1.0])
    max_debt = max([r["debt_value"] for r in rows] + [1.0])
    lines = []
    lines.append("%s  %s                 %s                              %s                              %s" % (pad_display(t(language, "coin"), 5), pad_display(t(language, "meaning"), 24), pad_display(t(language, "assets"), 20), pad_display(t(language, "debts"), 20), t(language, "price")))
    lines.append("─────  ────────────────────────  ───────────────────────────────────  ───────────────────────────────────  ─────")
    for r in rows:
        qtxt = ("Q%02d" % r["q"]).ljust(5)
        name = pad_display(q_name_lang(r["q"], language), 24)
        asset = rainbow_bar(r["asset_value"], max_asset, 16, ansi) + " " + fmt_num(r["asset_value"], "")
        debt = risk_bar(r["debt_value"] / max_debt, 16, ansi) + " " + fmt_num(r["debt_value"], "")
        price = fmt_num(r["price"], "")
        lines.append("%s  %s  %-37s  %-37s  %s" % (qtxt, name, asset, debt, price))
    return box("🪙 " + section_title(language, 6, "qmatrix").split(" – ", 1)[1], lines, width=132, ansi=ansi, color="bright_yellow", screen_width=width)


def render_q_debt_heatmap(sim, ansi=False, language="en", width=None):
    rows = _q_balances(sim)
    max_debt = max([r["debt_value"] for r in rows] + [1.0])
    lines = []
    lines.append(t(language, "legend_debt_heat"))
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
    lines.append(t(language, "top_debt_coins") + ": " + " │ ".join("Q%d %s %s" % (r["q"], q_name_lang(r["q"], language), fmt_num(r["debt_value"], " ZW", 1)) for r in top))
    return box("🔥 " + section_title(language, 7, "qdebt").split(" – ", 1)[1], lines, width=122, ansi=ansi, color="bright_red", screen_width=width)


def render_shortage_map(sim, ansi=False, language="en", width=None):
    rows = sorted(_shortage_rows(sim), key=lambda r: r["shortage"], reverse=True)
    max_shortage = max([r["shortage"] for r in rows] + [1.0])
    lines = []
    for r in rows[:20]:
        price_ratio = r["price"] / max(0.0001, r["base_price"])
        lines.append(label_bar(r["label"], r["shortage"], max_shortage, width=22, suffix="", ansi=ansi, value_digits=1) + "  " + t(language, "price_times") + fmt_num(price_ratio, "", 2))
    return box("🧺 " + section_title(language, 8, "shortages").split(" – ", 1)[1], lines, width=118, ansi=ansi, color="bright_green", screen_width=width)


def render_sector_sales(sim, ansi=False, language="en", width=None):
    rows = sorted(_sector_rows(sim), key=lambda r: r["sales"], reverse=True)
    max_sales = max([r["sales"] for r in rows] + [1.0])
    max_profit = max([abs(r["profit"]) for r in rows] + [1.0])
    lines = []
    lines.append("%s  %s                         %s                    %s  %s" % (pad_display(t(language, "sector"), 24), pad_display(t(language, "sales"), 12), pad_display(t(language, "profit"), 12), t(language, "firms"), t(language, "automation")))
    lines.append("────────────────────────  ────────────────────────────────  ──────────────────────────  ──────  ────")
    for r in rows[:24]:
        sales = rainbow_bar(r["sales"], max_sales, 16, ansi)
        profit = signed_bar("", r["profit"], max_profit, width=10, ansi=ansi, suffix="")
        # signed_bar mit leerem Label erzeugt Labelraum; kürzen wir ab:
        profit = profit.split("│", 1)[1] if "│" in profit else profit
        lines.append("%-24s  %-32s  %-26s  %6d  %.2f" % (
            trim_display(r["label"], 24), sales + " " + fmt_num(r["sales"], "", 1), profit, r["firms"], r["automation"]))
    return box("🏭 " + section_title(language, 9, "sectors").split(" – ", 1)[1], lines, width=128, ansi=ansi, color="bright_blue", screen_width=width)


def render_labor_landscape(sim, ansi=False, language="en", width=None):
    rows = sorted(_labor_rows(sim), key=lambda r: r["employed"], reverse=True)
    max_emp = max([r["employed"] for r in rows] + [1])
    max_wage = max([r["wage"] for r in rows] + [1.0])
    lines = []
    lines.append("%s  %s                         %s" % (pad_display(t(language, "labor_type"), 28), pad_display(t(language, "employment"), 16), t(language, "wage")))
    lines.append("────────────────────────────  ───────────────────────────────────  ─────────────────────────")
    for r in rows:
        emp_bar = rainbow_bar(r["employed"], max_emp, 16, ansi) + " " + str(r["employed"]).rjust(4)
        wage_bar = rainbow_bar(r["wage"], max_wage, 10, ansi) + " " + fmt_num(r["wage"], " ZW", 2)
        lines.append("%-28s  %-38s  %s" % (trim_display(r["label"], 28), emp_bar, wage_bar))
    return box("👷 " + section_title(language, 4, "labor").split(" – ", 1)[1], lines, width=130, ansi=ansi, color="bright_green", screen_width=width)


def render_public_credit_panel(sim, ansi=False, language="en", width=None):
    m = sim.metrics_history[-1] if sim.metrics_history else {}
    money = max(1.0, float(m.get("total_positive_money_value", 0.0) or 0.0))
    lines = []
    if normalize_language(language) == "de":
        vals = [("Steuereinnahmen", m.get("tax_revenue", 0.0), money), ("Transfers", m.get("transfer_spending", 0.0), money), ("öffentliche Käufe", m.get("public_spending", 0.0), money), ("Staatsnettovermögen", abs(m.get("government_net_worth", 0.0)), money), ("Kreditbestand", m.get("loan_outstanding", 0.0), money), ("neuer Kredit", m.get("new_credit_zw", 0.0), money), ("Rückzahlungen", m.get("repaid_zw", 0.0), money), ("Ausfallverluste", m.get("default_losses_zw", 0.0), money), ("Exporte", m.get("exports_value", 0.0), money), ("Importe", m.get("imports_value", 0.0), money)]
        risk_labels = ("Ausfallverluste", "Kreditbestand")
    else:
        vals = [("Tax revenue", m.get("tax_revenue", 0.0), money), ("Transfers", m.get("transfer_spending", 0.0), money), ("Public purchases", m.get("public_spending", 0.0), money), ("Gov. net worth", abs(m.get("government_net_worth", 0.0)), money), (t(language, "credit_stock"), m.get("loan_outstanding", 0.0), money), ("New credit", m.get("new_credit_zw", 0.0), money), ("Repayments", m.get("repaid_zw", 0.0), money), ("Default losses", m.get("default_losses_zw", 0.0), money), ("Exports", m.get("exports_value", 0.0), money), ("Imports", m.get("imports_value", 0.0), money)]
        risk_labels = ("Default losses", t(language, "credit_stock"))
    for label, v, maximum in vals:
        if label in risk_labels:
            bar = risk_bar(float(v or 0.0) / maximum, 24, ansi)
        else:
            bar = rainbow_bar(v, maximum, 24, ansi)
        lines.append("%s │%s│ %s" % (pad_display(label, 22), bar, fmt_num(v, " ZW")))
    return box("🏦 " + section_title(language, 10, "public").split(" – ", 1)[1], lines, width=112, ansi=ansi, color="bright_magenta", screen_width=width)


def render_household_distribution(sim, ansi=False, language="en", width=None):
    buckets = _wealth_buckets(sim)
    max_c = max([b[1] for b in buckets] + [1])
    vals = [h.net_worth() for h in sim.households]
    lines = []
    lines.append(t(language, "household_distribution_note"))
    for label, count, a, b in buckets:
        shown_label = label if normalize_language(language) == "de" else ("%s to %s" % (fmt_num(a, "", 1), fmt_num(b, "", 1)))
        lines.append("%s │%s│ %4d" % (pad_display(shown_label, 28), rainbow_bar(count, max_c, 24, ansi), count))
    if vals:
        lines.append("")
        lines.append("%s %s ZW │ %s %s ZW │ %s %s ZW │ Gini %s" % (
            t(language, "average"), fmt_num(mean(vals), ""), t(language, "minimum"), fmt_num(min(vals), ""), t(language, "maximum"), fmt_num(max(vals), ""), fmt_num(gini(vals), "", 3)))
    return box("👥 " + section_title(language, 11, "households").split(" – ", 1)[1], lines, width=116, ansi=ansi, color="bright_cyan", screen_width=width)


def render_capital_automation(sim, ansi=False, language="en", width=None):
    rows = sorted(_sector_rows(sim), key=lambda r: (r["automation"], r["capital"]), reverse=True)
    max_capital = max([r["capital"] for r in rows] + [1.0])
    lines = []
    lines.append("%s  %s                 %s" % (pad_display(t(language, "sector"), 24), pad_display(t(language, "automation"), 16), t(language, "capital_stock")))
    lines.append("────────────────────────  ─────────────────────────────  ─────────────────────────────")
    for r in rows[:20]:
        auto = rainbow_bar(r["automation"], 1.0, 14, ansi) + " " + fmt_num(r["automation"], "", 2)
        cap = rainbow_bar(r["capital"], max_capital, 14, ansi) + " " + fmt_num(r["capital"], " ZW", 1)
        lines.append("%-24s  %-30s  %s" % (trim_display(r["label"], 24), auto, cap))
    return box("🤖 " + section_title(language, 12, "automation").split(" – ", 1)[1], lines, width=120, ansi=ansi, color="bright_yellow", screen_width=width)


def render_q_flow(sim, ansi=False, language="en", width=None):
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
    lines.append(("Base coins" if normalize_language(language)!="de" else "Grundmünzen") + "      Q1%s ── Q2%s ── Q3%s ── Q4%s" % (mark(1), mark(2), mark(3), mark(4)))
    lines.append("                    │       │       │       │")
    lines.append(("Operations" if normalize_language(language)!="de" else "Operationen") + "       Q5%s ── Q6%s ── Q7%s ── Q8%s ── Q9%s" % (mark(5), mark(6), mark(7), mark(8), mark(9)))
    lines.append("                    │       │       │       │       │")
    lines.append(("Systems" if normalize_language(language)!="de" else "Systeme") + "          Q10%s ─ Q11%s ─ Q12%s ─ Q13%s ─ Q14%s ─ Q15%s ─ Q16%s" % (mark(10), mark(11), mark(12), mark(13), mark(14), mark(15), mark(16)))
    lines.append("                    │       │       │       │       │       │       │")
    lines.append(("Capital" if normalize_language(language)!="de" else "Kapital") + "          Q17%s ───────── Q18%s ───────── Q19%s ───────── Q20%s" % (mark(17), mark(18), mark(19), mark(20)))
    lines.append("")
    lines.append(t(language, "read_as") + ": " + t(language, "q_flow_reading"))
    return box("🧭 " + section_title(language, 13, "qflow").split(" – ", 1)[1], lines, width=132, ansi=ansi, color="bright_blue", screen_width=width)


def render_risk_radar(sim, ansi=False, language="en", width=None):
    lines = []
    for label, ratio, value_text in _risk_items(sim, language=language):
        lines.append("%-20s │%s│ %s" % (label, risk_bar(ratio, 28, ansi), value_text))
    return box("🚨 " + section_title(language, 14, "risk").split(" – ", 1)[1], lines, width=112, ansi=ansi, color="bright_red", screen_width=width)


def render_event_timeline(sim, ansi=False, limit=12, language="en", width=None):
    events = sim.event_log.recent(limit)
    lines = []
    if not events:
        lines.append(t(language, "no_events"))
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
    return box("🕰 " + section_title(language, 15, "events").split(" – ", 1)[1], lines, width=124, ansi=ansi, color="bright_cyan", screen_width=width)


def render_policy_board(sim, ansi=False, language="en", width=None):
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
    de = normalize_language(language) == "de"
    if q18 > debt * 0.12:
        levers.append(("Q18-Architekturprogramm" if de else "Q18 architecture program", 0.90, "Architekturschuld begrenzen" if de else "limit architecture debt"))
    if q16 > debt * 0.12:
        levers.append(("Q16-Betriebsinfrastruktur" if de else "Q16 operating infrastructure", 0.85, "Ausführung und Versorgung sichern" if de else "secure execution and supply"))
    if unemp > 0.12:
        levers.append(("öffentliches Jobprogramm" if de else "public job program", 0.80, "Nachfrage + Qualifikation stabilisieren" if de else "stabilize demand and skills"))
    if inflation > 0.07:
        levers.append(("Engpassinvestitionen" if de else "bottleneck investment", 0.75, "Angebot statt blindes Geld erhöhen" if de else "increase supply, not blind money"))
    if total_shortage > 0:
        levers.append(("Import-/Inputpuffer" if de else "import/input buffer", 0.60, "kurzfristige Güterknappheit glätten" if de else "smooth short-term shortages"))
    if debt_ratio > 0.50:
        levers.append(("Schuldenrestrukturierung" if de else "debt restructuring", 0.70, "semantisch falsche Schulden drehen" if de else "rotate semantically wrong debt"))
    if not levers:
        levers.append((t(language, "no_crisis_mode"), 0.55, t(language, "no_crisis_reason")))
        levers.append((t(language, "commons"), 0.50, t(language, "commons_reason")))
    lines = []
    for label, strength, reason in levers[:8]:
        lines.append("%s │%s│ %s" % (pad_display(label, 28), rainbow_bar(strength, 1.0, 18, ansi), reason))
    return box("🛠 " + section_title(language, 16, "policy").split(" – ", 1)[1], lines, width=122, ansi=ansi, color="bright_green", screen_width=width)


def build_visual_report(sim, markdown=True, ansi=False, language="en", width=None):
    """Build the full localized UTF-8-art report."""
    lang = normalize_language(language)
    w = fit_width(width)
    title_text = t(lang, "report_title")
    title = ("# " + title_text) if markdown else title_text
    intro = [title, ""]
    intro.append(wrap_plain_text(t(lang, "report_intro1"), w))
    intro.append("")
    intro.append(wrap_plain_text(t(lang, "report_intro2"), w))
    intro.append("")
    sections = []

    def add(idx, key, art, evaluation=None, description=None):
        sections.append(section(
            section_title(lang, idx, key),
            description or section_description(lang, key),
            art,
            evaluation or section_evaluation(lang, key),
            markdown=markdown,
            language=lang,
            width=w,
        ))

    add(1, "macro", render_macro_cockpit(sim, ansi=ansi, language=lang, width=w), macro_evaluation(sim, language=lang))

    bqp_eval = " ".join([
        trend_sentence(metrics_series(sim, "bqp"), "Das BQP" if lang == "de" else "BQP", " ZW", False, True, language=lang),
        trend_sentence(metrics_series(sim, "transactions"), "Die Zahl der Transaktionen" if lang == "de" else "Transactions", "", False, True, language=lang),
        section_evaluation(lang, "bqp"),
    ])
    add(2, "bqp", render_series_panel("📈 " + section_name(lang, "bqp"), [
        ("BQP", metrics_series(sim, "bqp"), " ZW", False, "bright_green"),
        ("Transaktionen" if lang == "de" else "Transactions", metrics_series(sim, "transactions"), "", False, "bright_cyan"),
        ("Exporte" if lang == "de" else "Exports", metrics_series(sim, "exports_value"), " ZW", False, "bright_blue"),
    ], ansi=ansi, language=lang, screen_width=w), bqp_eval)

    credit_eval = " ".join([
        trend_sentence(metrics_series(sim, "total_positive_money_value"), "Die positive Q-Geldmenge" if lang == "de" else "Positive Q money", " ZW", False, True, language=lang),
        trend_sentence(metrics_series(sim, "total_debt_value"), "Die Q-Schulden" if lang == "de" else "Q debt", " ZW", False, False, language=lang),
        trend_sentence(metrics_series(sim, "loan_outstanding"), "Der Kreditbestand" if lang == "de" else "Credit stock", " ZW", False, None, language=lang),
        section_evaluation(lang, "credit"),
    ])
    add(3, "credit", render_series_panel("💳 " + section_name(lang, "credit"), [
        (t(lang, "q_money_positive"), metrics_series(sim, "total_positive_money_value"), " ZW", False, "bright_green"),
        (t(lang, "q_debt"), metrics_series(sim, "total_debt_value"), " ZW", False, "bright_red"),
        (t(lang, "credit_stock"), metrics_series(sim, "loan_outstanding"), " ZW", False, "bright_yellow"),
        ("Ausfallverluste" if lang == "de" else "Default losses", metrics_series(sim, "default_losses_zw"), " ZW", False, "bright_magenta"),
    ], ansi=ansi, language=lang, screen_width=w), credit_eval)

    labor_eval = " ".join([
        trend_sentence(metrics_series(sim, "unemployment_rate"), t(lang, "unemployment"), "", True, False, language=lang),
        trend_sentence(metrics_series(sim, "avg_wage"), "Der Durchschnittslohn" if lang == "de" else "Average wage", " ZW", False, True, language=lang),
        section_evaluation(lang, "labor"),
    ])
    add(4, "labor", "\n".join([
        render_series_panel("👥 " + section_name(lang, "labor"), [
            (t(lang, "unemployment"), metrics_series(sim, "unemployment_rate"), "", True, "bright_red"),
            ("Beschäftigte" if lang == "de" else "Employed", metrics_series(sim, "employed"), "", False, "bright_green"),
            (t(lang, "wage"), metrics_series(sim, "avg_wage"), " ZW", False, "bright_yellow"),
        ], ansi=ansi, language=lang, screen_width=w),
        render_labor_landscape(sim, ansi=ansi, language=lang, width=w),
    ]), labor_eval)

    price_eval = " ".join([
        trend_sentence(metrics_series(sim, "price_index"), t(lang, "price_index"), "", False, False, language=lang),
        trend_sentence(metrics_series(sim, "inflation"), t(lang, "inflation_last"), "", True, False, language=lang),
        section_evaluation(lang, "prices"),
    ])
    add(5, "prices", render_series_panel("🌡 " + section_name(lang, "prices"), [
        (t(lang, "price_index"), metrics_series(sim, "price_index"), "", False, "bright_yellow"),
        (t(lang, "inflation_last"), metrics_series(sim, "inflation"), "", True, "bright_red"),
        ("Importe" if lang == "de" else "Imports", metrics_series(sim, "imports_value"), " ZW", False, "bright_blue"),
    ], ansi=ansi, language=lang, screen_width=w), price_eval)

    add(6, "qmatrix", render_q_balance_matrix(sim, ansi=ansi, language=lang, width=w))
    add(7, "qdebt", render_q_debt_heatmap(sim, ansi=ansi, language=lang, width=w))
    add(8, "shortages", render_shortage_map(sim, ansi=ansi, language=lang, width=w))
    add(9, "sectors", render_sector_sales(sim, ansi=ansi, language=lang, width=w))
    add(10, "public", render_public_credit_panel(sim, ansi=ansi, language=lang, width=w))
    add(11, "households", render_household_distribution(sim, ansi=ansi, language=lang, width=w))
    add(12, "automation", render_capital_automation(sim, ansi=ansi, language=lang, width=w))
    add(13, "qflow", render_q_flow(sim, ansi=ansi, language=lang, width=w))
    add(14, "risk", render_risk_radar(sim, ansi=ansi, language=lang, width=w))
    add(15, "events", render_event_timeline(sim, ansi=ansi, language=lang, width=w))
    add(16, "policy", render_policy_board(sim, ansi=ansi, language=lang, width=w))

    return "\n".join(intro + sections)

def build_terminal_dashboard(sim, ansi=True, language="en", width=None):
    """Terminal version with the same art principles."""
    return build_visual_report(sim, markdown=False, ansi=ansi, language=language, width=width)


def write_visual_report(path, sim, markdown=True, ansi=False, language="en", width=None):
    text = build_visual_report(sim, markdown=markdown, ansi=ansi, language=language, width=width)
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)
    return path


def format_progress_line(period, total_periods, metrics, ansi=True, language="en", width=None):
    ratio = float(period) / max(1.0, float(total_periods))
    progress = rainbow_bar(ratio, 1.0, width=18, ansi=ansi)
    unemp = float(metrics.get("unemployment_rate", 0.0) or 0.0)
    debt = float(metrics.get("total_debt_value", 0.0) or 0.0)
    bqp = float(metrics.get("bqp", 0.0) or 0.0)
    infl = float(metrics.get("inflation", 0.0) or 0.0)
    p = t(language, "period_short")
    line = "%s %s%04d/%04d │ BQP %s │ %s %s │ %s %s │ %s %s" % (
        progress, p, period, total_periods,
        fmt_num(bqp, " ZW", 1),
        t(language, "progress_unemployment_short"), fmt_pct(unemp),
        t(language, "progress_inflation_short"), fmt_pct(infl),
        t(language, "progress_debt"), fmt_num(debt, " ZW", 1),
    )
    return trim_display(line, fit_width(width))

def build_scenario_comparison_art(rows, markdown=True, ansi=False, language="en", width=None):
    """Localized UTF-8-art report for tools/compare_scenarios.py."""
    lang = normalize_language(language)
    w = fit_width(width)
    title = ("# " + t(lang, "scenario_comparison_title")) if markdown else t(lang, "scenario_comparison_title")
    lines = [title, "", wrap_plain_text(t(lang, "scenario_comparison_intro"), w), ""]
    if not rows:
        lines.append("Keine Szenarien vorhanden." if lang == "de" else "No scenarios available.")
        return "\n".join(lines)
    max_bqp = max(float(r.get("bqp", 0.0) or 0.0) for r in rows) or 1.0
    max_debt = max(float(r.get("total_debt_value", 0.0) or 0.0) for r in rows) or 1.0
    def art_block(title_text, metric_key, maximum, percent=False, risk=False):
        art_lines = []
        for r in rows:
            val = float(r.get(metric_key, 0.0) or 0.0)
            bar = risk_bar(val / maximum if maximum else 0.0, 24, ansi) if risk else rainbow_bar(val, maximum, 24, ansi)
            shown = fmt_pct(val) if percent else fmt_num(val, " ZW" if "debt" in metric_key or metric_key == "bqp" else "")
            art_lines.append("%s │%s│ %s" % (pad_display(str(r.get("scenario", "?")), 22), bar, shown))
        return box(title_text, art_lines, width=112, ansi=ansi, color="bright_cyan", screen_width=w)
    sections = [
        ("A", "BQP", "bqp", max_bqp, False, False, "bqp"),
        ("B", t(lang, "unemployment"), "unemployment_rate", 0.30, True, True, "labor"),
        ("C", t(lang, "q_debt"), "total_debt_value", max_debt, False, True, "credit"),
        ("D", t(lang, "household_gini"), "household_gini", 0.65, False, True, "households"),
    ]
    for letter, label, metric, maximum, percent, risk, key in sections:
        title_text = "UTF-8 Art %s – %s" % (letter, label)
        desc = section_description(lang, key)
        eval_text = section_evaluation(lang, key)
        art = art_block(label, metric, maximum, percent, risk)
        lines.append(section(title_text, desc, art, eval_text, markdown=markdown, language=lang, width=w))
    return "\n".join(lines)
