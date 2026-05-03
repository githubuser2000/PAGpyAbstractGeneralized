#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
RWÖ-Buntsimulation für PyPy3 / Python 3

Dieses Programm simuliert eine relationale Währungsökonomie, in der die
Währung keine einzelne Zahl ist, sondern ein Bündel aus Relationen:
Rechte, Pflichten, Risiken, Nachweise, Zeitbindungen, Umweltlasten,
Arbeitsleistungen und staatliche Schutzgrenzen.

Ausführen:
    pypy3 rwoe_bunte_pypy3_simulation.py

Optionen:
    pypy3 rwoe_bunte_pypy3_simulation.py --seed 7
    pypy3 rwoe_bunte_pypy3_simulation.py --teile 1,4,7
    pypy3 rwoe_bunte_pypy3_simulation.py --no-color

Nur Standardbibliothek. Keine externen Pakete.
"""

from __future__ import print_function

import argparse
import math
import random
import re
import sys
import textwrap
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Sequence, Tuple


# ---------------------------------------------------------------------------
# Farbe, Format und Terminal-Werkzeug
# ---------------------------------------------------------------------------

USE_COLOR = True
ANSI_RE = re.compile(r"\x1b\[[0-9;]*m")


def ansi(text, fg=None, bg=None, bold=False, dim=False, underline=False):
    """Färbt Text mit ANSI-256-Farben. Bei --no-color bleibt Text roh."""
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
        codes.append("38;5;%s" % fg)
    if bg is not None:
        codes.append("48;5;%s" % bg)
    if not codes:
        return str(text)
    return "\033[%sm%s\033[0m" % (";".join(codes), text)


def plain_len(text):
    return len(ANSI_RE.sub("", str(text)))


def pad(text, width, align="left"):
    text = str(text)
    gap = max(0, width - plain_len(text))
    if align == "right":
        return " " * gap + text
    if align == "center":
        left = gap // 2
        return " " * left + text + " " * (gap - left)
    return text + " " * gap


def visible_cut(text, width):
    """Schneidet nur roh; wird nur für unkritische, bereits kurze Felder genutzt."""
    raw = ANSI_RE.sub("", str(text))
    if len(raw) <= width:
        return text
    return raw[: max(0, width - 1)] + "…"


ABBR_COLORS = {
    "RWÖ": 201,
    "RWB": 51,
    "PG": 226,
    "RG": 208,
    "DL": 118,
    "ÜB": 141,
    "MS": 196,
    "ZB": 45,
    "ST": 34,
    "MW": 214,
    "DS": 177,
    "GG": 82,
    "TN": 198,
    "SB": 118,
    "KQ": 39,
    "LB": 220,
    "LQ": 118,
    "UB": 35,
    "KV": 203,
    "FV": 69,
    "VP": 129,
    "RP": 202,
}

UNIT_COLORS = {
    "Std": 48,
    "Tage": 87,
    "kWh": 229,
    "kgCO2": 190,
    "Liter": 159,
    "Kisten": 216,
    "Pkt": 213,
    "Anteil": 117,
    "Schritt": 225,
    "Feld": 120,
    "Relation": 154,
    "Bündel": 209,
}


def color_abbr(k):
    return ansi(k, fg=ABBR_COLORS.get(k, 15), bold=True)


def color_unit(u):
    # Hintergrundfarbe, damit Einheiten anders wirken als Kürzel.
    return ansi(u, fg=16, bg=UNIT_COLORS.get(u, 255), bold=True)


def paint(text, abbrs=None, units=None):
    """Färbt nur die Kürzel und Einheiten, die im aktuellen Abschnitt vorkommen."""
    text = str(text)
    repl = {}
    if abbrs:
        for k in abbrs:
            repl[k] = color_abbr(k)
    if units:
        for u in units:
            repl[u] = color_unit(u)
    if not repl:
        return text
    pattern = re.compile("|".join(re.escape(x) for x in sorted(repl, key=len, reverse=True)))
    return pattern.sub(lambda m: repl[m.group(0)], text)


def rainbow_rule(width=96):
    blocks = "█" * width
    if not USE_COLOR:
        return "=" * width
    colors = [196, 202, 226, 46, 51, 33, 129, 201]
    out = []
    for i, ch in enumerate(blocks):
        out.append(ansi(ch, fg=colors[i % len(colors)], bold=True))
    return "".join(out)


def soft_rule(width=96):
    if not USE_COLOR:
        return "-" * width
    colors = [39, 45, 51, 87, 123, 159, 195]
    return "".join(ansi("─", fg=colors[i % len(colors)]) for i in range(width))


def box(title, body, fg=15, bg=54, width=96):
    """Bunter Infokasten."""
    title = str(title)
    lines = []
    lines.append(ansi("╔" + "═" * (width - 2) + "╗", fg=fg, bg=bg, bold=True))
    title_line = "║" + pad("  " + title + "  ", width - 2, "center") + "║"
    lines.append(ansi(title_line, fg=fg, bg=bg, bold=True))
    lines.append(ansi("╠" + "═" * (width - 2) + "╣", fg=fg, bg=bg, bold=True))
    for paragraph in str(body).split("\n"):
        if paragraph.strip() == "":
            lines.append(ansi("║" + " " * (width - 2) + "║", fg=fg, bg=bg))
            continue
        for wrapped in textwrap.wrap(paragraph, width=width - 6):
            lines.append(ansi("║  " + pad(wrapped, width - 6) + "  ║", fg=fg, bg=bg))
    lines.append(ansi("╚" + "═" * (width - 2) + "╝", fg=fg, bg=bg, bold=True))
    return "\n".join(lines)


def ctable(headers, rows, align=None, title=None):
    """ANSI-sichere Tabelle."""
    if align is None:
        align = ["left"] * len(headers)
    all_rows = [headers] + rows
    widths = [0] * len(headers)
    for row in all_rows:
        for i, cell in enumerate(row):
            widths[i] = max(widths[i], plain_len(str(cell)))
    sep = "┼".join("─" * (w + 2) for w in widths)
    top = "┌" + "┬".join("─" * (w + 2) for w in widths) + "┐"
    mid = "├" + sep + "┤"
    bot = "└" + "┴".join("─" * (w + 2) for w in widths) + "┘"
    out = []
    if title:
        out.append(ansi(title, fg=213, bold=True, underline=True))
    out.append(ansi(top, fg=39))
    out.append(ansi("│", fg=39) + ansi("│", fg=39).join(
        " " + ansi(pad(headers[i], widths[i], "center"), fg=15, bg=60, bold=True) + " "
        for i in range(len(headers))
    ) + ansi("│", fg=39))
    out.append(ansi(mid, fg=39))
    for r, row in enumerate(rows):
        line = []
        for i, cell in enumerate(row):
            line.append(" " + pad(cell, widths[i], align[i] if i < len(align) else "left") + " ")
        out.append(ansi("│", fg=39) + ansi("│", fg=39).join(line) + ansi("│", fg=39))
    out.append(ansi(bot, fg=39))
    return "\n".join(out)


def percent_bar(value, maximum=100, width=24, good=True):
    value = max(0, min(maximum, value))
    filled = int(round(width * value / float(maximum)))
    empty = width - filled
    if not USE_COLOR:
        return "[" + "#" * filled + "." * empty + "] %3d" % value
    if good:
        if value >= 70:
            col = 46
        elif value >= 40:
            col = 226
        else:
            col = 196
    else:
        if value >= 70:
            col = 196
        elif value >= 40:
            col = 208
        else:
            col = 46
    return "[" + ansi("█" * filled, fg=col, bold=True) + ansi("░" * empty, fg=238) + "] %3d" % value


def sparkle(text, fg=15, bg=None):
    if not USE_COLOR:
        return str(text)
    colors = [196, 202, 226, 46, 51, 33, 129, 201]
    out = []
    for i, ch in enumerate(str(text)):
        if ch.isspace():
            out.append(ch)
        else:
            out.append(ansi(ch, fg=colors[i % len(colors)], bg=bg, bold=True))
    return "".join(out)


# ---------------------------------------------------------------------------
# Datenmodell: Relationen, Bündel, Akteure
# ---------------------------------------------------------------------------

@dataclass
class RelationRecord:
    kennung: str
    owner: str
    gegenpartei: str
    typ: str
    objekt: str
    menge: float
    einheit: str
    anspruch: str
    pflicht: str
    dauer_tage: int
    risiko: int
    vertrauen: int
    durchsetzung: int
    uebertragbar: int
    moral: str
    tags: Tuple[str, ...] = field(default_factory=tuple)

    def quality(self):
        # Nur technischer Hilfswert: keine Währung, kein Preis.
        base = self.vertrauen * 0.35 + self.durchsetzung * 0.30 + self.uebertragbar * 0.20 + (100 - self.risiko) * 0.15
        if self.moral == "rot":
            base -= 40
        elif self.moral == "gelb":
            base -= 8
        return int(max(0, min(100, round(base))))

    def risk_badge(self):
        if self.risiko >= 70:
            return ansi("hoch", fg=196, bold=True)
        if self.risiko >= 35:
            return ansi("mittel", fg=208, bold=True)
        return ansi("niedrig", fg=46, bold=True)

    def moral_badge(self):
        if self.moral == "grün":
            return ansi("grün", fg=46, bold=True)
        if self.moral == "gelb":
            return ansi("gelb", fg=226, bold=True)
        return ansi("rot", fg=196, bold=True)


@dataclass
class BundleRecord:
    name: str
    owner: str
    relations: List[RelationRecord]

    def count_by_type(self):
        d = {}
        for r in self.relations:
            d[r.typ] = d.get(r.typ, 0) + 1
        return d

    def average_risk(self):
        if not self.relations:
            return 0
        return int(round(sum(r.risiko for r in self.relations) / float(len(self.relations))))

    def average_trust(self):
        if not self.relations:
            return 0
        return int(round(sum(r.vertrauen for r in self.relations) / float(len(self.relations))))

    def toxic_count(self):
        return sum(1 for r in self.relations if r.moral == "rot")

    def yellow_count(self):
        return sum(1 for r in self.relations if r.moral == "gelb")

    def transferable_count(self):
        return sum(1 for r in self.relations if r.uebertragbar >= 50)

    def tags(self):
        s = set()
        for r in self.relations:
            for t in r.tags:
                s.add(t)
        return s


@dataclass
class Actor:
    name: str
    role: str
    need_tags: List[str]
    bundle: BundleRecord


RELATION_TYPES = [
    "Arbeitsleistung", "Nutzungsrecht", "Lieferforderung", "Steueranrechnung",
    "Versicherung", "Datenrecht", "Umweltpflicht", "Kreditpflicht", "Reputation",
    "Grundgarantie", "Wohnschutz", "Gesundheitsschutz", "Bildungsschutz",
]


def make_world(seed=42):
    rnd = random.Random(seed)

    def jitter(v, spread=6):
        return max(0, min(100, int(round(v + rnd.randint(-spread, spread)))))

    ari_rel = [
        RelationRecord("R-001", "Ari", "Bera Werk", "Arbeitsleistung", "Reparatur", 12, "Std",
                       "Ari kann Reparaturarbeit leisten", "Bera muss Schutz und Gegenleistung sichern", 30,
                       jitter(22), jitter(78), jitter(72), jitter(30), "grün", ("arbeit", "reparatur")),
        RelationRecord("R-002", "Ari", "Staat", "Steueranrechnung", "öffentlicher Beitrag", 2, "Pkt",
                       "anrechenbarer öffentlicher Beitrag", "nur bei sauberem Nachweis nutzbar", 365,
                       jitter(12), jitter(90), jitter(88), jitter(75), "grün", ("steuer", "öffentlich")),
        RelationRecord("R-003", "Ari", "Caro Lager", "Lieferforderung", "Ersatzteile", 6, "Kisten",
                       "Lieferung kleiner Ersatzteile", "Abholung innerhalb der Frist", 45,
                       jitter(34), jitter(68), jitter(65), jitter(80), "grün", ("lieferung", "material")),
        RelationRecord("R-004", "Ari", "Daten-Treuhand", "Datenrecht", "Werkzeughistorie", 30, "Tage",
                       "begrenzte Auswertung der Werkzeugdaten", "keine Weitergabe ohne Zweck", 30,
                       jitter(44), jitter(66), jitter(58), jitter(55), "gelb", ("daten", "analyse")),
        RelationRecord("R-005", "Ari", "Versa Sicherung", "Versicherung", "Ausfallabdeckung", 70, "Pkt",
                       "Teildeckung bei Arbeitsausfall", "Meldung muss belegt sein", 180,
                       jitter(25), jitter(75), jitter(77), jitter(62), "grün", ("risiko", "schutz")),
        RelationRecord("R-006", "Ari", "Bera Werk", "Reputation", "Prüfsiegel Reparatur", 82, "Pkt",
                       "bestätigte Qualität in Reparaturfällen", "kann bei Betrug widerrufen werden", 720,
                       jitter(16), jitter(84), jitter(70), jitter(40), "grün", ("vertrauen", "qualität")),
    ]

    bera_rel = [
        RelationRecord("R-101", "Bera Werk", "Energiewerk Nord", "Nutzungsrecht", "Werkstattstrom", 90, "kWh",
                       "Stromabruf für Produktion", "Zahlung oder Ausgleich durch Steuerbeitrag", 20,
                       jitter(18), jitter(80), jitter(74), jitter(68), "grün", ("energie", "produktion")),
        RelationRecord("R-102", "Bera Werk", "Mara Markt", "Lieferforderung", "Fahrradteile", 10, "Kisten",
                       "Lieferung nach Fertigung", "Qualitätssiegel muss bleiben", 18,
                       jitter(38), jitter(63), jitter(70), jitter(79), "grün", ("lieferung", "produkt")),
        RelationRecord("R-103", "Bera Werk", "Versa Sicherung", "Versicherung", "Produkthaftung", 60, "Pkt",
                       "Deckung bei kleinen Schäden", "Dokumentation der Teile nötig", 365,
                       jitter(20), jitter(76), jitter(76), jitter(70), "grün", ("risiko", "haftung")),
        RelationRecord("R-104", "Bera Werk", "Flussrat", "Umweltpflicht", "Wasserverbrauch", 400, "Liter",
                       "Nutzung gegen Regeneration", "Rückführung muss belegt sein", 60,
                       jitter(45), jitter(60), jitter(64), jitter(35), "gelb", ("umwelt", "wasser")),
    ]

    bank_rel = [
        RelationRecord("R-201", "Cedo Bank", "Ari", "Kreditpflicht", "Werkzeugkredit", 30, "Tage",
                       "Vorfinanzierung gegen künftige Arbeit", "keine Kopplung an Wohnung oder Körper", 90,
                       jitter(41), jitter(62), jitter(85), jitter(73), "grün", ("kredit", "arbeit")),
        RelationRecord("R-202", "Cedo Bank", "Bera Werk", "Kreditpflicht", "Lagerkredit", 12, "Kisten",
                       "Vorfinanzierung von Material", "Rang nach Lohnschutz", 120,
                       jitter(48), jitter(59), jitter(80), jitter(82), "grün", ("kredit", "material")),
        RelationRecord("R-203", "Cedo Bank", "Omni Plattform", "Datenrecht", "Bonitätsprofil", 180, "Tage",
                       "Risikoprüfung mit Zweckbindung", "kein Verkauf an Arbeitgeber", 180,
                       jitter(52), jitter(57), jitter(68), jitter(46), "gelb", ("daten", "kredit")),
    ]

    state_rel = [
        RelationRecord("R-301", "Staat", "Ari", "Grundgarantie", "Existenzschutz", 365, "Tage",
                       "Basiszugang zu Recht und Versorgung", "nicht verkäuflich", 365,
                       jitter(5), jitter(95), jitter(96), jitter(0), "grün", ("grund", "schutz")),
        RelationRecord("R-302", "Staat", "Ari", "Wohnschutz", "Mindestwohnen", 180, "Tage",
                       "Schutz vor plötzlichem Wohnverlust", "Prüfung nach Krise", 180,
                       jitter(8), jitter(92), jitter(94), jitter(0), "grün", ("wohnen", "schutz")),
        RelationRecord("R-303", "Staat", "Ari", "Gesundheitsschutz", "Basismedizin", 365, "Tage",
                       "Zugang zu medizinischer Grundversorgung", "Missbrauchskontrolle", 365,
                       jitter(7), jitter(92), jitter(94), jitter(0), "grün", ("gesundheit", "schutz")),
        RelationRecord("R-304", "Staat", "Ari", "Bildungsschutz", "Neubewertung", 120, "Tage",
                       "Recht auf zweite Prüfung und Weiterbildung", "Teilnahme nötig", 120,
                       jitter(13), jitter(88), jitter(90), jitter(0), "grün", ("bildung", "schutz")),
    ]

    shadow_rel = [
        RelationRecord("R-901", "Omni Plattform", "Ari", "Arbeitsleistung", "exklusive Zukunftsarbeit", 900, "Std",
                       "voller Zugriff auf künftige Arbeit", "Ari darf kaum kündigen", 900,
                       jitter(78), jitter(50), jitter(55), jitter(92), "rot", ("arbeit", "bindung", "toxic")),
        RelationRecord("R-902", "Omni Plattform", "Ari", "Wohnschutz", "Firmenwohnung", 365, "Tage",
                       "Wohnung nur bei Gehorsam", "Wohnverlust bei Vertragsbruch", 365,
                       jitter(82), jitter(46), jitter(61), jitter(88), "rot", ("wohnen", "bindung", "toxic")),
        RelationRecord("R-903", "Omni Plattform", "Ari", "Datenrecht", "Persönlichkeitsprofil", 365, "Tage",
                       "vollständige Auswertung des Lebensprofils", "keine echte Zweckgrenze", 365,
                       jitter(91), jitter(38), jitter(58), jitter(94), "rot", ("daten", "kontrolle", "toxic")),
        RelationRecord("R-904", "Omni Plattform", "Ari", "Kreditpflicht", "Schuldkette", 730, "Tage",
                       "Schuld wird weiterverkauft", "lange Bindung an Plattform", 730,
                       jitter(86), jitter(43), jitter(63), jitter(95), "rot", ("kredit", "bindung", "toxic")),
        RelationRecord("R-905", "Omni Plattform", "Ari", "Reputation", "Sperrprofil", 300, "Pkt",
                       "Marktzugang hängt an Plattformwertung", "Widerspruch schwer", 365,
                       jitter(84), jitter(35), jitter(52), jitter(90), "rot", ("vertrauen", "kontrolle", "toxic")),
    ]

    env_rel = [
        RelationRecord("R-501", "Bera Werk", "Flussrat", "Umweltpflicht", "Kohlenstofflast", 44, "kgCO2",
                       "Emission muss ausgeglichen werden", "Ausgleich vor Weiterverkauf", 90,
                       jitter(36), jitter(61), jitter(72), jitter(50), "gelb", ("umwelt", "co2")),
        RelationRecord("R-502", "Bera Werk", "Waldkooperative", "Umweltpflicht", "Regeneration", 20, "kgCO2",
                       "nachweisbare Bindung oder Ersatz", "Pflege der Fläche", 180,
                       jitter(28), jitter(70), jitter(71), jitter(58), "grün", ("umwelt", "regeneration")),
        RelationRecord("R-503", "Mara Markt", "Recyclinghof", "Lieferforderung", "Rücknahme", 5, "Kisten",
                       "Rücknahme alter Teile", "Sortierung muss stimmen", 120,
                       jitter(26), jitter(74), jitter(73), jitter(70), "grün", ("umwelt", "rücknahme")),
    ]

    bundles = {
        "ari": BundleRecord("Ari-Wertbündel", "Ari", ari_rel),
        "bera": BundleRecord("Bera-Produktionsbündel", "Bera Werk", bera_rel),
        "bank": BundleRecord("Cedo-Bankbündel", "Cedo Bank", bank_rel),
        "staat": BundleRecord("Staatliches Schutzbündel", "Staat", state_rel),
        "schatten": BundleRecord("Omni-Schattenbündel", "Omni Plattform", shadow_rel),
        "umwelt": BundleRecord("Bera-Umweltbündel", "Bera Werk", env_rel),
    }

    actors = {
        "ari": Actor("Ari", "Person", ["produkt", "steuer", "schutz"], bundles["ari"]),
        "bera": Actor("Bera Werk", "Unternehmen", ["arbeit", "material", "energie", "risiko"], bundles["bera"]),
        "bank": Actor("Cedo Bank", "Bank", ["kredit", "schutz", "daten"], bundles["bank"]),
        "staat": Actor("Staat", "Regelsetzer", ["grund", "umwelt", "steuer"], bundles["staat"]),
        "omni": Actor("Omni Plattform", "Schattenakteur", ["bindung", "kontrolle"], bundles["schatten"]),
    }
    return actors, bundles


# ---------------------------------------------------------------------------
# Simulations-Werkzeug
# ---------------------------------------------------------------------------

SECTION_ABBR = {
    1: {
        "RWÖ": "Relationale Währungsökonomie. Das ist die Gesamtordnung, in der nicht eine Zahl, sondern ein Netz aus Rechten, Pflichten, Risiken, Nachweisen und Zeitbindungen als Wertträger dient.",
        "RWB": "Relationales Wertbündel. Das ist eine Tabelle aus einzelnen Relationen; sie ist in dieser Simulation die eigentliche Währung, nicht ein Geldbetrag.",
        "RG": "Risiko-Grad. Dieses Hilfssignal zeigt, wie unsicher eine Relation ist; es ist kein Preis und kein Geldwert.",
        "MS": "Moralstatus. Dieses Feld zeigt, ob eine Relation erlaubt, kritisch oder verboten wirkt; rot bedeutet: rechtlich oder ethisch zu blockieren.",
    },
    2: {
        "RWB": "Relationales Wertbündel. In diesem Teil wird ein solches Bündel als Zahlung angeboten.",
        "PG": "Passungsgrad. Dieses Hilfssignal misst, wie gut angebotene Relationen zu den Bedürfnissen des Gegenübers passen; es ist nicht die Währung.",
        "DL": "Durchsetzbarkeits-Lage. Dieses Hilfssignal zeigt, ob Ansprüche rechtlich und praktisch verlässlich wirken.",
    },
    3: {
        "RWB": "Relationales Wertbündel. Hier wird es in Produktion übersetzt: Arbeit, Energie, Material und Versicherung verbinden sich zu neuen Relationen.",
        "KQ": "Kettenqualität. Dieses Hilfssignal zeigt, ob eine Produktionskette stabil genug ist, um weiter akzeptiert zu werden.",
        "LB": "Lieferbündel. Das ist das Bündel neuer Lieferrelationen, das nach erfolgreicher Produktion entsteht.",
    },
    4: {
        "RWB": "Relationales Wertbündel. Die Bank bündelt mehrere Zukunftsrelationen, anstatt bloß eine Zahl zu verleihen.",
        "KV": "Kreditverwandlung. Damit ist gemeint, dass schwer handelbare Zukunftsansprüche in ein besser prüfbares Bündel umgeformt werden.",
        "RG": "Risiko-Grad. Dieses Hilfssignal zeigt die Ausfallnähe des Bündels; es bleibt eine Prüfziffer, nicht die Währung selbst.",
    },
    5: {
        "RWÖ": "Relationale Währungsökonomie. In diesem Teil zeigt sie ihren Boom, weil verborgene Rechte und Fähigkeiten handelbar sichtbar werden.",
        "RWB": "Relationales Wertbündel. Es sammelt viele kleine Ansprüche, Rechte und Pflichten in einer übertragbaren Struktur.",
        "LQ": "Liquiditäts-Breite. Dieses Hilfssignal zählt, wie viele verschiedene Relationstypen anschlussfähig werden; es ist kein Geldbetrag.",
    },
    6: {
        "RWB": "Relationales Wertbündel. Hier enthält es Arbeits-, Wohn-, Daten- und Kreditrelationen, die geprüft werden.",
        "SB": "Schutzbremse. Das ist die staatliche und rechtliche Sperre gegen Bündel, die Personen faktisch beherrschen würden.",
        "TN": "Toxizitäts-Nähe. Dieses Hilfssignal zeigt, wie nahe ein Bündel an Ausbeutung, Knechtschaft oder totaler Kontrolle liegt.",
        "MS": "Moralstatus. Dieses Feld markiert, ob eine Relation frei akzeptabel, kritisch oder zu verbieten ist.",
    },
    7: {
        "RWB": "Relationales Wertbündel. In der Schattenseite wird es missbraucht, um Lebensbereiche zu bündeln und Kontrolle zu erzeugen.",
        "TN": "Toxizitäts-Nähe. Dieses Hilfssignal zeigt, wie gefährlich die Bündelung von Arbeit, Wohnen, Schuld, Daten und Reputation wird.",
        "ST": "Staat. In diesem Teil ist damit die öffentliche Rechtsmacht gemeint, die solche Bündel begrenzen oder auflösen muss.",
        "SB": "Schutzbremse. Das ist das konkrete Eingreifen, das toxische Übertragbarkeit blockiert.",
        "MS": "Moralstatus. Dieses Feld zeigt, ob eine Relation erlaubt, kritisch oder verboten wirkt; rot bedeutet hier: nicht marktfähig.",
    },
    8: {
        "RWB": "Relationales Wertbündel. Hier trägt es Umweltlasten und Regenerationspflichten direkt mit sich.",
        "UB": "Umweltbilanz. Dieses Hilfssignal zeigt, ob ein Bündel ökologische Lasten offenlegt oder verschiebt.",
        "PG": "Passungsgrad. In diesem Teil misst er, ob ein Käufer ein ökologisch belastetes Bündel akzeptiert.",
    },
    9: {
        "ZB": "Zentralbank. In dieser Simulation erkennt sie nicht nur Geldmengen an, sondern Qualitätsklassen von Relationen.",
        "RWB": "Relationales Wertbündel. Es kann anerkannt, abgewertet, isoliert oder gestützt werden.",
        "FV": "Frost-Vektor. Dieses Hilfssignal zeigt, wie stark Märkte einfrieren, wenn Vertrauen in Relationen bricht.",
        "RG": "Risiko-Grad. Dieses Hilfssignal zeigt, wie riskant ein Bündel nach dem Vertrauensschock wirkt.",
    },
    10: {
        "ST": "Staat. Hier stellt er nicht nur Geld bereit, sondern sichere Grundrelationen.",
        "GG": "Grundgarantie. Das ist ein nicht handelbares Basisbündel aus Wohnen, Gesundheit, Recht, Bildung und Versorgung.",
        "RWB": "Relationales Wertbündel. In diesem Teil ist es das Schutzbündel, nicht Spekulationsgeld.",
    },
    11: {
        "MW": "Marktwirtschaft. Hier steht das Kürzel für eine Ordnung, die Werte meistens in Preisen und Geldbeträgen verdichtet.",
        "RWÖ": "Relationale Währungsökonomie. Hier steht das Kürzel für die Ordnung, die Beziehungen selbst als Wertstruktur benutzt.",
        "DS": "Datenschutz. Dieses Hilfssignal zeigt, wie stark Privatsphäre und Zweckbindung geschützt bleiben.",
        "VP": "Verwertungstiefe. Dieses Hilfssignal zeigt, wie tief ein Wirtschaftssystem in Lebensbereiche eindringt.",
    },
    12: {
        "RWÖ": "Relationale Währungsökonomie. Der Abschluss fasst zusammen, unter welchen Grenzen sie produktiv bleiben kann.",
        "RWB": "Relationales Wertbündel. Es bleibt die Währung, aber nur erlaubte Relationen dürfen darin marktfähig sein.",
        "ST": "Staat. Er setzt Grenzen, damit nicht Menschen, sondern nur erlaubte Leistungen, Rechte und Pflichten gehandelt werden.",
        "SB": "Schutzbremse. Sie ist die rote Linie gegen Menschenhandel durch die Hintertür relationaler Kontrolle.",
    },
}

SECTION_UNITS = {
    1: ["Std", "Tage", "Kisten", "Pkt", "Bündel", "Relation"],
    2: ["Std", "Kisten", "Pkt"],
    3: ["Std", "kWh", "Kisten", "Pkt"],
    4: ["Tage", "Kisten", "Pkt"],
    5: ["Relation", "Bündel", "Pkt", "Feld"],
    6: ["Std", "Tage", "Pkt"],
    7: ["Std", "Tage", "Pkt"],
    8: ["kgCO2", "Liter", "Kisten", "Pkt"],
    9: ["Relation", "Bündel", "Pkt"],
    10: ["Tage", "Pkt", "Bündel"],
    11: ["Pkt", "Feld"],
    12: ["Relation", "Bündel", "Schritt"],
}


def start_section(n, title, what):
    abbrs = SECTION_ABBR.get(n, {})
    units = SECTION_UNITS.get(n, [])
    print("\n" + rainbow_rule())
    print(sparkle("  Simulationsteil %02d: %s" % (n, title)))
    print(rainbow_rule())
    print(box("Was wird hier simuliert?", paint(what, abbrs, units), fg=15, bg=23))
    if abbrs:
        rows = []
        for k, desc in abbrs.items():
            rows.append([color_abbr(k), paint(desc, abbrs, units)])
        print(ctable([ansi("Kürzel", fg=15, bg=90, bold=True), ansi("Erklärung nur für diesen Teil", fg=15, bg=90, bold=True)], rows, title="Kürzel-Legende dieses Simulationsteils"))
    if units:
        unit_line = "  ".join(color_unit(u) for u in units)
        print(ansi("Einheiten in diesem Teil: ", fg=15, bg=24, bold=True) + unit_line)
    print(soft_rule())
    return abbrs, units


def relation_rows(relations, abbrs, units, max_rows=None):
    rows = []
    use = relations if max_rows is None else relations[:max_rows]
    for r in use:
        rows.append([
            ansi(r.kennung, fg=45, bold=True),
            r.owner,
            r.typ,
            r.objekt,
            "%s %s" % (format_amount(r.menge), color_unit(r.einheit) if r.einheit in units else r.einheit),
            "%s %s" % (r.risk_badge(), percent_bar(r.risiko, good=False, width=10)),
            r.moral_badge(),
            percent_bar(r.quality(), width=10),
        ])
    return rows


def format_amount(x):
    if abs(x - int(x)) < 0.0001:
        return str(int(x))
    return ("%.2f" % x).rstrip("0").rstrip(".")


def bundle_summary(bundle):
    by_type = bundle.count_by_type()
    return {
        "Relationen": len(bundle.relations),
        "Typen": len(by_type),
        "Risiko": bundle.average_risk(),
        "Vertrauen": bundle.average_trust(),
        "Gelb": bundle.yellow_count(),
        "Rot": bundle.toxic_count(),
        "Übertragbar": bundle.transferable_count(),
    }


def print_bundle_table(bundle, abbrs, units, title=None, max_rows=None):
    # RG und MS werden nur als Kürzel benutzt, wenn sie im jeweiligen
    # Simulationsteil auch erklärt werden. Sonst heißen die Spalten
    # ausgeschrieben Risiko und Moral.
    risk_header = "RG" if "RG" in abbrs else "Risiko"
    moral_header = "MS" if "MS" in abbrs else "Moral"
    headers = ["Kennung", "Eigentümer", "Typ", "Objekt", "Menge", risk_header, moral_header, "Qualität"]
    headers = [paint(h, abbrs, units) for h in headers]
    rows = relation_rows(bundle.relations, abbrs, units, max_rows=max_rows)
    print(ctable(headers, rows, align=["left", "left", "left", "left", "right", "left", "center", "left"], title=title))


def score_bundle_for_needs(bundle, needs):
    """Gibt PG und Details zurück. Der PG ist nur ein Matching-Hilfssignal."""
    total_weight = 0.0
    got_weight = 0.0
    details = []
    for need in needs:
        tag = need["tag"]
        qty = need.get("qty", 1.0)
        unit = need.get("unit", "Pkt")
        weight = need.get("weight", 1.0)
        min_trust = need.get("min_trust", 0)
        max_risk = need.get("max_risk", 100)
        total_weight += weight
        candidates = [r for r in bundle.relations if tag in r.tags and r.einheit == unit]
        useful = [r for r in candidates if r.vertrauen >= min_trust and r.risiko <= max_risk and r.moral != "rot"]
        amount = sum(r.menge for r in useful)
        coverage = min(1.0, amount / float(qty)) if qty else 1.0
        quality = 0.0
        if useful:
            quality = sum(r.quality() for r in useful) / float(len(useful)) / 100.0
        hit = coverage * (0.55 + 0.45 * quality)
        got_weight += hit * weight
        details.append((need, candidates, useful, amount, int(round(hit * 100))))
    if total_weight <= 0:
        return 0, details
    return int(round(100 * got_weight / total_weight)), details


def chain_quality(relations):
    if not relations:
        return 0
    # Multiplikativ abgeschwächte Qualität: eine schwache Relation schadet der ganzen Kette.
    factors = []
    for r in relations:
        factors.append(max(0.05, r.quality() / 100.0))
    product = 1.0
    for f in factors:
        product *= f
    geom = product ** (1.0 / len(factors))
    penalty = 1.0 - min(0.45, sum(1 for r in relations if r.moral == "gelb") * 0.07 + sum(1 for r in relations if r.moral == "rot") * 0.25)
    return int(round(100 * geom * penalty))


def toxicity_score(bundle):
    if not bundle.relations:
        return 0
    toxic_tags = set(["bindung", "kontrolle", "toxic"])
    toxic = 0
    bundled_domains = set()
    for r in bundle.relations:
        if r.moral == "rot":
            toxic += 25
        if toxic_tags.intersection(r.tags):
            toxic += 14
        if r.uebertragbar >= 80 and r.risiko >= 70:
            toxic += 12
        for domain in ["arbeit", "wohnen", "daten", "kredit", "vertrauen"]:
            if domain in r.tags:
                bundled_domains.add(domain)
    if len(bundled_domains) >= 4:
        toxic += 35
    if len(bundled_domains) >= 5:
        toxic += 20
    return max(0, min(100, toxic))


def environmental_balance(bundle):
    co2_load = 0.0
    co2_regen = 0.0
    water = 0.0
    transparent = 0
    for r in bundle.relations:
        if r.einheit == "kgCO2" and "co2" in r.tags:
            co2_load += r.menge
            transparent += r.quality()
        if r.einheit == "kgCO2" and "regeneration" in r.tags:
            co2_regen += r.menge
            transparent += r.quality()
        if r.einheit == "Liter":
            water += r.menge
            transparent += r.quality()
    net = co2_load - co2_regen
    clarity = int(round(transparent / max(1, len(bundle.relations))))
    # UB: je niedriger Netto-Last und je höher Klarheit, desto besser.
    ub = max(0, min(100, int(round(clarity - max(0, net) * 0.7 - water * 0.03))))
    return ub, net, water, clarity


def clone_bundle(bundle, name=None, owner=None, relations=None):
    return BundleRecord(name or bundle.name, owner or bundle.owner, list(relations if relations is not None else bundle.relations))


# ---------------------------------------------------------------------------
# Simulationsteile
# ---------------------------------------------------------------------------


def part_01_foundation(world, bundles, rnd):
    abbrs, units = start_section(
        1,
        "Grundwährung als RWB statt Zahl",
        "Dieser Teil zeigt die RWÖ als System, in dem ein RWB die Währung bildet. Simuliert wird kein Kontostand, sondern eine farbige Relationstabelle aus Arbeitsleistung, Steueranrechnung, Lieferung, Datenrecht, Versicherung und Reputation. Der RG und der MS zeigen, warum bloßes Zeilenzählen als Wertmessung zu schwach wäre."
    )
    b = bundles["ari"]
    print(paint("Ein RWB besteht hier aus mehreren Relationen. Jede Relation hat Menge, Einheit, Risiko, Moralstatus und Qualität. Die Tabelle wird nicht zu einer einzigen Zahl reduziert.", abbrs, units))
    print_bundle_table(b, abbrs, units, title=paint("Ari besitzt dieses RWB als farbige Währungstabelle", abbrs, units))

    s = bundle_summary(b)
    rows = [
        ["Anzahl sichtbarer Relationen", color_unit("Relation") + " × " + ansi(str(s["Relationen"]), fg=51, bold=True), "Nur Menge, noch kein Wert."],
        ["Verschiedene Relationstypen", ansi(str(s["Typen"]), fg=201, bold=True), "Mehr Typen bedeuten mehr Anschlussmöglichkeiten."],
        [paint("Mittlerer RG", abbrs, units), percent_bar(s["Risiko"], good=False), "Hohes Risiko macht das Bündel schwerer akzeptierbar."],
        ["Mittleres Vertrauen", percent_bar(s["Vertrauen"]), "Vertrauen erhöht Akzeptanz, ersetzt aber keine Gesetze."],
        [paint("Gelber MS", abbrs, units), ansi(str(s["Gelb"]), fg=226, bold=True), "Gelbe Relationen brauchen Prüfung."],
        [paint("Roter MS", abbrs, units), ansi(str(s["Rot"]), fg=196, bold=True), "Rot wäre zu blockieren."],
    ]
    print(ctable(["Struktur", "Messbares Signal", "Deutung"], rows, title=paint("Warum Zeilen allein nicht reichen", abbrs, units)))
    print(box("Schlussfolgerung", paint("Die RWÖ ist stärker als eine einfache Zahl, weil sie nicht nur Menge, sondern Beziehung, Risiko, Pflicht, Zeit und Moral sichtbar macht. Genau dadurch wird sie aber gefährlicher: Wer mehr sieht, kann auch mehr verwerten.", abbrs, units), fg=16, bg=226))


def part_02_market_matching(world, bundles, rnd):
    abbrs, units = start_section(
        2,
        "Marktzahlung durch Passung statt Preiszahl",
        "Dieser Teil simuliert einen Kauf ohne klassische Preiszahl. Bera Werk akzeptiert ein RWB nur, wenn dessen Relationen zu ihrem Bedarf passen. Der PG ist dabei ein Hilfssignal: Er zeigt Passung, aber er ist nicht die Währung. Die DL wird indirekt über Vertrauen, Risiko und Qualität geprüft."
    )
    buyer_bundle = bundles["ari"]
    needs = [
        {"tag": "reparatur", "qty": 8, "unit": "Std", "weight": 1.4, "min_trust": 60, "max_risk": 45, "name": "Reparaturarbeit"},
        {"tag": "material", "qty": 4, "unit": "Kisten", "weight": 1.0, "min_trust": 55, "max_risk": 55, "name": "Ersatzteile"},
        {"tag": "steuer", "qty": 1, "unit": "Pkt", "weight": 0.7, "min_trust": 75, "max_risk": 25, "name": "öffentliche Anrechnung"},
    ]
    pg, details = score_bundle_for_needs(buyer_bundle, needs)
    print(paint("Bera verlangt keine einzelne Geldzahl. Bera formuliert ein Akzeptanzprofil: Reparatur, Material und Steueranrechnung sollen als Relationen im angebotenen RWB vorhanden sein.", abbrs, units))
    rows = []
    for need, candidates, useful, amount, hit in details:
        rows.append([
            need["name"],
            "%s %s" % (format_amount(need["qty"]), color_unit(need["unit"])),
            str(len(candidates)),
            str(len(useful)),
            "%s %s" % (format_amount(amount), color_unit(need["unit"])),
            percent_bar(hit),
        ])
    print(ctable(["Beras Bedarf", "Soll", "gefunden", "gültig", "gedeckt", "Teil-PG"], rows, align=["left", "right", "right", "right", "right", "left"], title=paint("Matching des angebotenen RWB", abbrs, units)))
    print(ansi("Gesamter ", fg=15) + color_abbr("PG") + ansi(": ", fg=15) + percent_bar(pg, width=36))
    if pg >= 70:
        decision = ansi("ANNAHME", fg=46, bold=True)
        reason = "Das RWB passt breit genug: Arbeit, Material und öffentlicher Beitrag bilden eine akzeptable Zahlung."
    elif pg >= 45:
        decision = ansi("TEILANNAHME", fg=226, bold=True)
        reason = "Das RWB passt teilweise; Bera verlangt Nachweis oder Zusatzrelation."
    else:
        decision = ansi("ABLEHNUNG", fg=196, bold=True)
        reason = "Das RWB passt nicht ausreichend zum Bedarf."
    print(ctable(["Entscheidung", "Begründung"], [[decision, paint(reason, abbrs, units)]], title=paint("Marktentscheidung ohne Preiszahl", abbrs, units)))
    print(box("Schlussfolgerung", paint("Die normale Marktwirtschaft fragt: Wie teuer ist es? Dieses System fragt: Welche Relationen passen? Dadurch wird der Markt genauer. Der Preis dafür ist Komplexität: Jede Zahlung muss geprüft, verstanden und rechtlich eingeordnet werden.", abbrs, units), fg=15, bg=54))


def part_03_production_chain(world, bundles, rnd):
    abbrs, units = start_section(
        3,
        "Produktion als Verkettung von Relationen",
        "Dieser Teil simuliert, wie aus Arbeit, Energie, Material und Versicherung ein LB entsteht. Das RWB wird nicht verbraucht wie Münzen, sondern umgebaut: alte Relationen werden erfüllt, neue Lieferrelationen entstehen. Die KQ zeigt, ob die Produktionskette tragfähig ist."
    )
    ari = bundles["ari"]
    bera = bundles["bera"]
    chain = []
    for want in [("reparatur", "Std"), ("energie", "kWh"), ("material", "Kisten"), ("haftung", "Pkt")]:
        tag, unit = want
        candidates = [r for r in ari.relations + bera.relations if tag in r.tags and r.einheit == unit and r.moral != "rot"]
        if candidates:
            chain.append(max(candidates, key=lambda r: r.quality()))
    kq = chain_quality(chain)
    rows = []
    for r in chain:
        rows.append([r.typ, r.objekt, "%s %s" % (format_amount(r.menge), color_unit(r.einheit)), percent_bar(r.quality()), r.risk_badge(), r.moral_badge()])
    print(ctable(["Baustein", "Objekt", "Menge", "Qualität", "Risiko", "Moral"], rows, title=paint("Relationen, aus denen die Produktion zusammengesetzt wird", abbrs, units)))
    print(color_abbr("KQ") + ansi(" der Kette: ", fg=15) + percent_bar(kq, width=34))
    if kq >= 60:
        new_rel = RelationRecord("R-777", "Bera Werk", "Mara Markt", "Lieferforderung", "fertige Reparatursätze", 8, "Kisten",
                                 "Lieferung fertiger Reparatursätze", "Rücknahme mangelhafter Teile", 30,
                                 28, 74, 75, 80, "grün", ("lieferung", "produkt", "neu"))
        lb = BundleRecord("Neues Lieferbündel", "Bera Werk", [new_rel])
        print_bundle_table(lb, abbrs, units, title=paint("Entstandenes LB", abbrs, units))
        result = "Die Kette ist stark genug. Aus vorhandenen Relationen entsteht ein neues handelbares Lieferbündel."
    else:
        result = "Die Kette ist zu schwach. Es entsteht kein sauberes Lieferbündel; der Markt verlangt Schutz, Versicherung oder bessere Nachweise."
    print(box("Produktionsschluss", paint(result, abbrs, units), fg=16, bg=82 if kq >= 60 else 208))
    print(box("Warum stärker als einfache Marktwirtschaft?", paint("Eine Preisrechnung sieht oft nur Kosten. Die relationale Produktion sieht, welche Arbeits-, Energie-, Material-, Haftungs- und Vertrauensrelationen wirklich zusammenpassen. Dadurch kann die Wirtschaft feiner koordinieren; zugleich wird sie abhängiger von Daten und Prüfung.", abbrs, units), fg=15, bg=24))


def part_04_credit(world, bundles, rnd):
    abbrs, units = start_section(
        4,
        "Bank und Kredit als KV",
        "Dieser Teil simuliert, wie eine Bank Zukunftsrelationen bündelt. Das RWB der Bank ist keine Geldsumme, sondern ein Paket aus Kreditpflichten, Sicherheiten, Datenrechten und Rangregeln. Die KV macht etwas handelbar, das vorher nur schwer prüfbar war. Der RG zeigt, wo das Bündel fragil bleibt."
    )
    bank = bundles["bank"]
    print_bundle_table(bank, abbrs, units, title=paint("Bankbündel vor der KV", abbrs, units))
    risk_before = bank.average_risk()
    transformed_relations = []
    for r in bank.relations:
        moral = r.moral
        risk = max(0, r.risiko - (12 if r.moral == "grün" else 4))
        trust = min(100, r.vertrauen + (10 if r.moral == "grün" else 3))
        enforce = min(100, r.durchsetzung + 8)
        nr = RelationRecord(r.kennung.replace("R-", "K-"), r.owner, r.gegenpartei, r.typ, r.objekt, r.menge, r.einheit,
                            r.anspruch + "; geprüft", r.pflicht + "; Rangregel eingetragen", r.dauer_tage,
                            risk, trust, enforce, r.uebertragbar, moral, r.tags)
        transformed_relations.append(nr)
    transformed = BundleRecord("Geprüftes Kredit-RWB", "Cedo Bank", transformed_relations)
    risk_after = transformed.average_risk()
    print_bundle_table(transformed, abbrs, units, title=paint("Bankbündel nach der KV", abbrs, units))
    rows = [
        [paint("RG vorher", abbrs, units), percent_bar(risk_before, good=False), "Ungeprüfte Zukunftsansprüche sind schwerer akzeptierbar."],
        [paint("RG nachher", abbrs, units), percent_bar(risk_after, good=False), "Prüfung senkt Unsicherheit, aber entfernt sie nicht vollständig."],
        ["Vertrauen nachher", percent_bar(transformed.average_trust()), "Mehr Nachweis macht das Bündel marktgängiger."],
    ]
    print(ctable(["Signal", "Anzeige", "Deutung"], rows, title=paint("Wirkung der KV", abbrs, units)))
    print(box("Kehrseite", paint("Die Bank kann die Wirtschaft beschleunigen, weil sie verstreute Zukunftsrelationen bündelt. Aber wenn sie zu viele schwache Relationen schön verpackt, entsteht eine tiefere Krise als bei normalem Kredit: Dann kollabiert nicht nur Geldvertrauen, sondern Beziehungsvertrauen.", abbrs, units), fg=15, bg=88))


def part_05_boom(world, bundles, rnd):
    abbrs, units = start_section(
        5,
        "Wirtschaftsboom durch relationale Liquidität",
        "Dieser Teil simuliert, warum die RWÖ stärker wirken kann als normale Marktwirtschaft. Viele vorher versteckte Fähigkeiten, kleine Rechte und Nachweise werden als RWB sichtbar. Die LQ zeigt nicht Geldmenge, sondern Breite der anschlussfähigen Relationstypen."
    )
    all_rel = []
    for key in ["ari", "bera", "bank", "umwelt"]:
        all_rel.extend(bundles[key].relations)
    hidden_fields = [
        ("freie Werkzeugzeit", "arbeit", "Std", 4, 71),
        ("kleine Steuerleistung", "steuer", "Pkt", 1, 86),
        ("lokales Vertrauen", "vertrauen", "Pkt", 14, 80),
        ("unbenutzte Maschinenzeit", "produktion", "Std", 7, 67),
        ("Rücknahmefähigkeit", "rücknahme", "Kisten", 3, 75),
        ("kleiner Umweltbeitrag", "regeneration", "kgCO2", 6, 72),
    ]
    new = []
    for i, (obj, tag, unit, qty, trust) in enumerate(hidden_fields, 1):
        new.append(RelationRecord("B-%03d" % i, "lokaler Markt", "offenes Register", "Mikrorelation", obj, qty, unit,
                                  "wird als kleine Relation sichtbar", "Nachweis muss erneuert werden", 60,
                                  rnd.randint(18, 42), trust + rnd.randint(-4, 4), rnd.randint(55, 78), rnd.randint(45, 75),
                                  "grün", (tag, "mikro")))
    before = BundleRecord("Vorher", "Markt", all_rel)
    after = BundleRecord("Nachher", "Markt", all_rel + new)

    def liquid_breadth(bundle):
        tags = bundle.tags()
        types = bundle.count_by_type()
        transfer = bundle.transferable_count()
        clean = sum(1 for r in bundle.relations if r.moral == "grün")
        return max(0, min(100, int(round(len(tags) * 4 + len(types) * 3 + transfer * 2 + clean * 1.2))))

    lb_before = liquid_breadth(before)
    lb_after = liquid_breadth(after)
    rows = [
        ["Vor Sichtbarmachung", str(len(before.relations)) + " " + color_unit("Relation"), str(len(before.tags())) + " " + color_unit("Feld"), percent_bar(lb_before)],
        ["Nach Sichtbarmachung", str(len(after.relations)) + " " + color_unit("Relation"), str(len(after.tags())) + " " + color_unit("Feld"), percent_bar(lb_after)],
    ]
    print(ctable(["Zustand", "Relationen", "Anschlussfelder", "LQ"], rows, title=paint("Boom-Simulation: mehr verwertbare Struktur", abbrs, units)))
    print_bundle_table(BundleRecord("Neu sichtbar gewordene Mikrorelationen", "lokaler Markt", new), abbrs, units, title=paint("Neue RWB-Bausteine des Booms", abbrs, units))
    print(box("Boom-Logik", paint("Die RWÖ erzeugt einen Boom, weil sie vorher unflüssige Wirklichkeit flüssig macht: freie Zeit, kleine Ansprüche, Vertrauen, Rücknahme, Regeneration und Nachweise. Das ist produktiver als eine Marktwirtschaft, die vieles erst spät oder gar nicht als Marktstruktur erkennt.", abbrs, units), fg=16, bg=82))
    print(box("Preis des Booms", paint("Je mehr Felder sichtbar werden, desto weniger bleibt privat, unbewertet und unverkauft. Die Stärke entsteht aus tieferer Erfassung; genau daraus entsteht auch die moralische Gefahr.", abbrs, units), fg=15, bg=88))


def part_06_labor_protection(world, bundles, rnd):
    abbrs, units = start_section(
        6,
        "Arbeitsmarkt, Schutzbremse und toxische Bündelung",
        "Dieser Teil simuliert die heikle Grenze: Arbeitsleistung kann Teil eines RWB sein, aber der Mensch selbst darf nicht zum handelbaren Objekt werden. Die SB prüft deshalb, ob Arbeit, Wohnen, Daten, Kredit und Reputation toxisch gebündelt werden. Die TN zeigt die Gefahr der faktischen Beherrschung."
    )
    legal = BundleRecord("Sauberes Arbeitsbündel", "Ari", [bundles["ari"].relations[0], bundles["ari"].relations[4], bundles["ari"].relations[5]])
    toxic = bundles["schatten"]
    rows = []
    for b in [legal, toxic]:
        tn = toxicity_score(b)
        decision = ansi("erlaubt", fg=46, bold=True) if tn < 45 else ansi("prüfen", fg=226, bold=True) if tn < 75 else ansi("blockieren", fg=196, bold=True)
        rows.append([b.name, str(len(b.relations)) + " " + color_unit("Relation"), percent_bar(tn, good=False), decision, str(b.toxic_count())])
    print(ctable([paint("RWB", abbrs, units), "Umfang", paint("TN", abbrs, units), paint("SB-Entscheid", abbrs, units), "roter MS"], rows, title=paint("Schutzprüfung zweier Arbeitsbündel", abbrs, units)))
    print_bundle_table(legal, abbrs, units, title=paint("Erlaubtes Arbeits-RWB: Leistung ist begrenzt, kündbar und geschützt", abbrs, units))
    print_bundle_table(toxic, abbrs, units, title=paint("Toxisches RWB: gebündelte Kontrolle über Lebensbereiche", abbrs, units), max_rows=5)
    print(box("Rechtslogik", paint("Die SB greift nicht, weil Arbeit schlecht wäre. Sie greift, wenn Arbeit mit Wohnung, Schuld, Daten und Reputation so verbunden wird, dass eine Person praktisch nicht mehr frei wechseln kann. Genau hier braucht die RWÖ harte Gesetze.", abbrs, units), fg=15, bg=54))


def part_07_dark_side(world, bundles, rnd):
    abbrs, units = start_section(
        7,
        "Amoralische Schattenseite und staatliche Eindämmung",
        "Dieser Teil ist eine Warnsimulation. Ein Schattenakteur nutzt RWB-Strukturen nicht zur produktiven Koordination, sondern zur Kontrolle. Die TN steigt, wenn Arbeit, Wohnen, Daten, Schuld und Reputation in einer Hand landen. Der ST setzt die SB, damit solche Bündel nicht als Währung umlaufen."
    )
    shadow = clone_bundle(bundles["schatten"], name="Schatten-RWB vor Eingriff")
    tn0 = toxicity_score(shadow)
    print(color_abbr("TN") + ansi(" vor staatlichem Eingriff: ", fg=15) + percent_bar(tn0, width=40, good=False))
    domains = []
    for r in shadow.relations:
        mark = []
        for domain in ["arbeit", "wohnen", "daten", "kredit", "vertrauen"]:
            if domain in r.tags:
                mark.append(domain)
        domains.append([r.kennung, r.typ, ", ".join(mark), r.moral_badge(), percent_bar(r.uebertragbar, width=10), percent_bar(r.risiko, width=10, good=False)])
    print(ctable(["Kennung", "Typ", "kontrollierter Bereich", "MS", "Übertragbarkeit", "Risiko"], domains, title=paint("Wie Herrschaft durch Relationenkopplung entsteht", abbrs, units)))

    # Staatlicher Eingriff: rote Relationen verlieren Marktfähigkeit und Übertragbarkeit.
    cleaned = []
    blocked = []
    for r in shadow.relations:
        if r.moral == "rot" or "toxic" in r.tags:
            nr = RelationRecord(r.kennung, r.owner, r.gegenpartei, r.typ, r.objekt, r.menge, r.einheit,
                                "BLOCKIERT: " + r.anspruch, "nicht marktfähig", r.dauer_tage,
                                min(100, r.risiko), max(0, r.vertrauen - 10), r.durchsetzung, 0, "rot", r.tags)
            blocked.append(nr)
        else:
            cleaned.append(r)
    post = BundleRecord("Schatten-RWB nach SB", "Omni Plattform", cleaned + blocked)
    tn1 = max(0, toxicity_score(post) - 38)  # Blockierung senkt die Marktfähigkeit; die Gefahr bleibt als Warnsignal sichtbar.
    print(color_abbr("TN") + ansi(" nach SB des ", fg=15) + color_abbr("ST") + ansi(": ", fg=15) + percent_bar(tn1, width=40, good=False))
    rows = [[r.kennung, r.typ, ansi("nicht marktfähig", fg=196, bold=True), color_unit(r.einheit)] for r in blocked]
    print(ctable(["Kennung", "Typ", "Eingriff", "Einheit"], rows, title=paint("Blockierte Relationen", abbrs, units)))
    print(box("Moralischer Schluss", paint("Diese Schattenseite lässt sich nicht wegzaubern. Wenn wirklich alles relational handelbar wird, versucht ein Markt auch Abhängigkeit zu handeln. Darum muss der ST Grenzen setzen: Menschen, Grundrechte, Kündigungsfreiheit, Kernprivatheit und politische Rechte dürfen niemals als RWB-Währung umlaufen.", abbrs, units), fg=15, bg=88))


def part_08_environment(world, bundles, rnd):
    abbrs, units = start_section(
        8,
        "Umwelt als sichtbare Relation statt externe Kosten",
        "Dieser Teil simuliert Umweltlasten im RWB. Ein Produkt trägt kgCO2, Liter Wasserverbrauch und Rücknahmepflichten direkt mit. Die UB zeigt, ob die Last transparent und tragbar wirkt. Der PG eines Käufers sinkt, wenn ökologische Pflichten verschoben werden."
    )
    env = bundles["umwelt"]
    print_bundle_table(env, abbrs, units, title=paint("Umweltrelationen am Produkt-RWB", abbrs, units))
    ub, net, water, clarity = environmental_balance(env)
    rows = [
        [paint("UB", abbrs, units), percent_bar(ub), "Je höher, desto sauberer und transparenter wirkt das Bündel."],
        ["Netto-Last", "%s %s" % (format_amount(net), color_unit("kgCO2")), "Positive Zahl bedeutet offene Restlast."],
        ["Wasser", "%s %s" % (format_amount(water), color_unit("Liter")), "Wasserpflicht bleibt als Relation am Produkt sichtbar."],
        ["Nachweisklarheit", percent_bar(clarity), "Klare Nachweise erhöhen Akzeptanz."],
    ]
    print(ctable(["Signal", "Anzeige", "Deutung"], rows, title=paint("Ökologische Bewertung ohne Verstecken der Last", abbrs, units)))
    buyer_needs = [
        {"tag": "regeneration", "qty": 30, "unit": "kgCO2", "weight": 1.2, "min_trust": 55, "max_risk": 45, "name": "Regeneration"},
        {"tag": "rücknahme", "qty": 3, "unit": "Kisten", "weight": 0.8, "min_trust": 55, "max_risk": 40, "name": "Rücknahme"},
    ]
    pg, details = score_bundle_for_needs(env, buyer_needs)
    print(color_abbr("PG") + ansi(" eines ökologisch strengen Käufers: ", fg=15) + percent_bar(pg, width=32))
    print(box("Warum stärker?", paint("Normale Preise können Umweltkosten auslagern. In diesem System hängen Umweltpflichten am RWB selbst. Der Markt sieht also nicht nur Produkt und Preis, sondern auch ökologische Restschuld. Der Preis dafür: noch mehr Daten, Prüfung und Streit über Nachweise.", abbrs, units), fg=16, bg=82))


def part_09_central_bank_crisis(world, bundles, rnd):
    abbrs, units = start_section(
        9,
        "Zentralbank, Vertrauensschock und Frost-Vektor",
        "Dieser Teil simuliert eine Krise. Wenn Vertrauen in Relationen fällt, frieren Märkte ein. Die ZB bewertet RWB-Qualitäten, isoliert toxische Bündel und stützt saubere Bündel. Der FV zeigt, wie stark der Markt einfriert; der RG steigt bei unsicheren Bündeln."
    )
    candidates = [bundles["ari"], bundles["bera"], bundles["bank"], bundles["schatten"], bundles["umwelt"]]
    rows_before = []
    rows_after = []
    for b in candidates:
        risk = b.average_risk()
        trust = b.average_trust()
        toxic = b.toxic_count()
        fv = max(0, min(100, int(round(risk * 0.55 + toxic * 18 + max(0, 65 - trust) * 0.8))))
        rows_before.append([b.name, str(len(b.relations)) + " " + color_unit("Relation"), percent_bar(risk, good=False), percent_bar(trust), percent_bar(fv, good=False)])
        # Zentralbankregel: rote Bündel werden isoliert; grüne mit hoher Durchsetzung erhalten Anerkennung.
        if toxic:
            fv2 = max(10, fv - 15)
            label = ansi("Quarantäne", fg=196, bold=True)
        elif trust >= 70 and risk <= 35:
            fv2 = max(0, fv - 28)
            label = ansi("Anerkennung", fg=46, bold=True)
        else:
            fv2 = max(0, fv - 10)
            label = ansi("Prüfstütze", fg=226, bold=True)
        rows_after.append([b.name, label, percent_bar(fv2, good=False)])
    print(ctable([paint("RWB", abbrs, units), "Umfang", paint("RG", abbrs, units), "Vertrauen", paint("FV vor ZB", abbrs, units)], rows_before, title=paint("Krise vor Eingriff der ZB", abbrs, units)))
    print(ctable([paint("RWB", abbrs, units), paint("ZB-Regel", abbrs, units), paint("FV nach ZB", abbrs, units)], rows_after, title=paint("Stabilisierung nach Qualitätsregeln", abbrs, units)))
    print(box("Krisenlogik", paint("In der RWÖ ist Krise nicht nur Geldmangel. Krise heißt: Niemand weiß mehr, welche Relationen erfüllbar, erlaubt und durchsetzbar sind. Die ZB muss daher Qualität, Anerkennung und Quarantäne steuern. Das ist mächtiger als klassische Geldpolitik, aber auch politisch heikler.", abbrs, units), fg=15, bg=24))


def part_10_welfare_state(world, bundles, rnd):
    abbrs, units = start_section(
        10,
        "Sozialstaat als Grundgarantie statt bloßer Geldtransfer",
        "Dieser Teil simuliert, wie der ST ein GG bereitstellt. Das GG ist ein RWB, das nicht spekulativ verkauft werden darf. Es stabilisiert Personen durch Wohnen, Gesundheit, Bildung, Recht und Versorgung, damit schwache Marktposition nicht zum vollständigen Ausschluss führt."
    )
    gg = bundles["staat"]
    print_bundle_table(gg, abbrs, units, title=paint("Staatliches GG als nicht handelbares Schutz-RWB", abbrs, units))
    crisis_without = {"Wohnen": 20, "Gesundheit": 35, "Bildung": 30, "Recht": 25, "Marktzugang": 28}
    crisis_with = {k: min(100, v + rnd.randint(35, 55)) for k, v in crisis_without.items()}
    rows = []
    for k in crisis_without:
        rows.append([k, percent_bar(crisis_without[k]), percent_bar(crisis_with[k]), ansi("stabilisiert", fg=46, bold=True)])
    print(ctable(["Lebensbereich", "ohne GG", "mit GG", "Wirkung"], rows, title=paint("Schutzwirkung des GG", abbrs, units)))
    print(box("Schlussfolgerung", paint("Eine starke RWÖ braucht einen starken Sozialstaat. Wenn alles relational bewertet wird, müssen Basisrelationen besonders geschützt werden. Sonst wird Armut nicht nur Geldmangel, sondern Verlust von Wohnung, Gesundheit, Bildung, Rechtsschutz und Marktzugang gleichzeitig.", abbrs, units), fg=16, bg=82))


def part_11_compare(world, bundles, rnd):
    abbrs, units = start_section(
        11,
        "Vergleich: MW gegen RWÖ",
        "Dieser Teil vergleicht die MW und die RWÖ über Hilfssignale. Die DS zeigt den Schutz privater Bereiche. Die VP zeigt, wie tief die Wirtschaft in Lebensbereiche eindringt. Der Vergleich ist keine absolute Wahrheit, sondern eine modellhafte Schlussfolgerung aus den vorherigen Simulationsteilen."
    )
    # Modellhafte Scorecard. Nicht als empirische Behauptung, sondern Simulation.
    categories = [
        ("Informationsfülle", 45, 92, True),
        ("Koordination komplexer Ketten", 55, 88, True),
        ("Sichtbarkeit externer Kosten", 38, 83, True),
        ("Liquidität verborgener Rechte", 42, 90, True),
        ("Einfachheit", 88, 34, True),
        ("DS", 62, 35, True),
        ("VP", 48, 91, False),
        ("Ausbeutungsgefahr", 52, 87, False),
        ("Regulierungsbedarf", 60, 96, False),
    ]
    rows = []
    for name, mw, rwoe, good in categories:
        label = paint(name, abbrs, units)
        rows.append([label, percent_bar(mw, good=good), percent_bar(rwoe, good=good)])
    print(ctable(["Feld", paint("MW", abbrs, units), paint("RWÖ", abbrs, units)], rows, title=paint("Bunte Modell-Scorecard", abbrs, units)))
    print(box("Schlussfolgerung", paint("Die RWÖ ist stärker, weil sie mehr Wirklichkeit in das Wirtschaftssystem zieht: Rechte, Pflichten, Zukunft, Risiko, Umwelt und Abhängigkeit. Aber genau dadurch steigt die VP. Ohne starke Regeln fällt der DS, und die Ausbeutungsgefahr wächst. Die MW ist gröber, aber ihre Grobheit schützt manchmal vor totaler Erfassung.", abbrs, units), fg=15, bg=54))


def part_12_final(world, bundles, rnd):
    abbrs, units = start_section(
        12,
        "Verfassung der relationalen Wirtschaft",
        "Dieser Teil fasst die Simulation in Regeln zusammen. Die RWÖ darf RWB als Währung nutzen, aber der ST muss die SB setzen. Nicht alles, was als Relation erfasst werden kann, darf als Bündel gehandelt werden."
    )
    principles = [
        ("Personenschutz", "Menschen sind keine handelbaren Bündel. Nur freiwillige, begrenzte Leistungen dürfen marktfähig sein."),
        ("Unveräußerlichkeit", "Körperfreiheit, Grundrechte, Wahlrecht, Kündigungsfreiheit und Kernprivatheit bleiben außerhalb des Marktes."),
        ("Transparenz", "Jede marktfähige Relation muss Gegenpartei, Pflicht, Risiko, Dauer und Nachweis offenlegen."),
        ("Löschung", "Erfüllte, alte, falsche oder missbräuchliche Relationen brauchen Korrektur und Vergessen."),
        ("Entflechtung", "Arbeit, Wohnen, Kredit, Daten und Reputation dürfen nicht in einer privaten Hand verschmelzen."),
        ("Grundgarantie", "Jede Person braucht sichere Basisrelationen für Leben, Recht, Gesundheit, Wohnen und Bildung."),
        ("Marktgrenze", "Was Freiheit strukturell zerstört, darf niemals als RWB-Währung umlaufen."),
    ]
    rows = []
    for i, (name, text) in enumerate(principles, 1):
        rows.append([str(i) + " " + color_unit("Schritt"), ansi(name, fg=[46, 51, 226, 213, 208, 82, 196][i - 1], bold=True), paint(text, abbrs, units)])
    print(ctable(["Nummer", "Regel", "Inhalt"], rows, title=paint("Mindestverfassung der RWÖ", abbrs, units)))
    print(box("Endschluss", paint("Die RWÖ kann stärker sein als eine Marktwirtschaft mit bloßen Preisen, weil sie die Struktur des Wertes zeigt. Ihr Preis ist die Gefahr totaler Verwertung. Die entscheidende Grenze lautet deshalb: RWB darf Währung sein, aber Menschen dürfen niemals durch ihre Relationen als Währung benutzt werden. Der ST muss diese Grenze mit einer SB schützen.", abbrs, units), fg=16, bg=226))


PARTS = [
    part_01_foundation,
    part_02_market_matching,
    part_03_production_chain,
    part_04_credit,
    part_05_boom,
    part_06_labor_protection,
    part_07_dark_side,
    part_08_environment,
    part_09_central_bank_crisis,
    part_10_welfare_state,
    part_11_compare,
    part_12_final,
]


def title_screen(seed, chosen):
    print(rainbow_rule())
    print(sparkle("RELATIONALE WÄHRUNGSÖKONOMIE — BUNTE SIMULATION"))
    print(rainbow_rule())
    body = (
        "Diese Simulation behandelt eine Wirtschaft, in der die Währung keine einzelne Zahl ist. "
        "Die Währung ist ein Bündel aus Relationen: Rechte, Pflichten, Risiken, Nachweise, Zeitbindungen, Umweltlasten und Schutzgrenzen. "
        "Interne Balken und Signale dienen nur zur Simulation. Sie sind keine neue Geldzahl.\n\n"
        "Startwert für Zufall: %s. Ausgewählte Teile: %s. "
        "Die Farben markieren Kürzel, Einheiten, Risiken, Moralstatus und Entscheidungen."
    ) % (seed, ", ".join(str(x) for x in chosen))
    print(box("Programmidee", body, fg=15, bg=53))
    print(ansi("Hinweis: ", fg=226, bold=True) + "Die dunklen Simulationsteile sind Warnmodelle. Sie beschreiben, was rechtlich verhindert werden muss; sie sind keine Empfehlung.")


def parse_parts(s):
    if not s:
        return list(range(1, len(PARTS) + 1))
    out = []
    for chunk in s.split(","):
        chunk = chunk.strip()
        if not chunk:
            continue
        if "-" in chunk:
            a, b = chunk.split("-", 1)
            a, b = int(a), int(b)
            out.extend(range(a, b + 1))
        else:
            out.append(int(chunk))
    clean = []
    for p in out:
        if p < 1 or p > len(PARTS):
            raise ValueError("Teil %s existiert nicht. Erlaubt sind 1 bis %s." % (p, len(PARTS)))
        if p not in clean:
            clean.append(p)
    return clean


def main(argv=None):
    global USE_COLOR
    parser = argparse.ArgumentParser(description="Sehr bunte RWÖ-Simulation für PyPy3/Python 3.")
    parser.add_argument("--seed", type=int, default=42, help="Startwert für reproduzierbaren Zufall")
    parser.add_argument("--teile", type=str, default="", help="z.B. 1,2,5 oder 3-7; leer bedeutet alle Teile")
    parser.add_argument("--no-color", action="store_true", help="Terminal-Farben ausschalten")
    args = parser.parse_args(argv)
    USE_COLOR = not args.no_color

    try:
        chosen = parse_parts(args.teile)
    except Exception as e:
        print("Fehler bei --teile:", e, file=sys.stderr)
        return 2

    rnd = random.Random(args.seed)
    world, bundles = make_world(args.seed)
    title_screen(args.seed, chosen)
    for idx in chosen:
        PARTS[idx - 1](world, bundles, rnd)
    print("\n" + rainbow_rule())
    print(sparkle("ENDE DER SIMULATION"))
    print(rainbow_rule())
    print("Ausführen mit anderer Auswahl: pypy3 rwoe_bunte_pypy3_simulation.py --teile 1,5,7 --seed 99")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
