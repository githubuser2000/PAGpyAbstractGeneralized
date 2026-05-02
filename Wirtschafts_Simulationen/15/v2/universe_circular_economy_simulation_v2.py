#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universe Circular Economy Simulation v2
=======================================

PyPy3-compatible, dependency-free simulation of a universe/cosmos economy based
on stacked cycle currency. This version emphasizes partial-cycle companies:
most firms only operate a segment such as 5->7 or 15->19, while rare integrator
firms close larger loops.

Default output language is English. Use --lang de for German reports.

Core formula:
    SG_raw = (end_repetition - start_repetition) * N + end_station - start_station

This is the incremental form of the user's original example:
    EarthType, start=4, end=17, end repetition/pass=4 => (4-1)*20 + 17 - 4 = 73
    VulcanType, start=4, end=17, end repetition/pass=4 => (4-1)*22 + 17 - 4 = 79

The code uses only Python standard library modules so that it can run on PyPy3.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
import os
import random
import statistics
import sys
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Small utilities
# ---------------------------------------------------------------------------


def clamp(value: float, low: float, high: float) -> float:
    if value < low:
        return low
    if value > high:
        return high
    return value


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if abs(b) < 1e-12:
        return default
    return a / b


def fmt(x: float, digits: int = 2) -> str:
    if abs(x) >= 1_000_000_000:
        return f"{x/1_000_000_000:.{digits}f}B"
    if abs(x) >= 1_000_000:
        return f"{x/1_000_000:.{digits}f}M"
    if abs(x) >= 1_000:
        return f"{x/1_000:.{digits}f}k"
    return f"{x:.{digits}f}"


def weighted_choice(rng: random.Random, items: Sequence[Tuple[object, float]]) -> object:
    total = sum(max(0.0, w) for _, w in items)
    if total <= 0:
        return items[-1][0]
    x = rng.random() * total
    acc = 0.0
    for item, weight in items:
        acc += max(0.0, weight)
        if x <= acc:
            return item
    return items[-1][0]


def mean(values: Sequence[float], default: float = 0.0) -> float:
    if not values:
        return default
    return sum(values) / float(len(values))


def text(lang: str, en: str, de: str) -> str:
    return de if lang == "de" else en


# ---------------------------------------------------------------------------
# Color and abbreviation system
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Abbreviation:
    code: str
    color: str
    name_en: str
    name_de: str
    explanation_en: str
    explanation_de: str


ABBREVIATIONS: Dict[str, Abbreviation] = {
    "SG": Abbreviation("SG", "#E6194B", "Stacked-loop currency", "Schleifen-Geld",
                       "Raw counted currency distance through the planetary cycle.",
                       "Rohe gezählte Währungsdistanz durch den planetaren Kreislauf."),
    "UKE": Abbreviation("UKE", "#3CB44B", "Universal Cycle Unit", "Universelle Kreislauf-Einheit",
                        "Normalizes cycle value by cycle length so 20-station and 22-station planets can trade.",
                        "Normalisiert Kreislaufwert durch Kreislauflänge, damit 20er- und 22er-Planeten handeln können."),
    "NCL": Abbreviation("NCL", "#4363D8", "Native cycle length", "Native Kreislauflänge",
                        "The number of stations on the planet type: Earth=20, Vulcan=22.",
                        "Anzahl der Stationen des Planetentyps: Erde=20, Vulkan=22."),
    "STA": Abbreviation("STA", "#F58231", "Start station", "Startstation",
                        "The station where a company begins transforming an identity.",
                        "Station, an der ein Unternehmen die Transformation einer Identität beginnt."),
    "END": Abbreviation("END", "#911EB4", "End station", "Endstation",
                        "The station where a company leaves the identity for the next company or loop stage.",
                        "Station, an der das Unternehmen die Identität an die nächste Firma oder Schleifenstufe übergibt."),
    "REP": Abbreviation("REP", "#46F0F0", "Repetition/pass", "Wiederholung/Umlauf",
                        "The counted pass of the cycle in which a station is reached.",
                        "Gezählter Umlauf des Kreislaufs, in dem eine Station erreicht wird."),
    "MAT": Abbreviation("MAT", "#F032E6", "Material factor", "Materialfaktor",
                        "Standardized material quantity moved by the calculation.",
                        "Standardisierte Materialmenge, die in der Rechnung bewegt wird."),
    "QAL": Abbreviation("QAL", "#BCF60C", "Quality factor", "Qualitätsfaktor",
                        "Purity, fertility, health and low contamination of the identity.",
                        "Reinheit, Fruchtbarkeit, Gesundheit und geringe Belastung der Identität."),
    "USE": Abbreviation("USE", "#FABEBE", "Use factor", "Nutzenfaktor",
                        "Actual usefulness for food, soil, body, production, return or planetary infrastructure.",
                        "Tatsächlicher Nutzen für Nahrung, Boden, Körper, Produktion, Rückführung oder planetare Infrastruktur."),
    "JUS": Abbreviation("JUS", "#008080", "Justice factor", "Gerechtigkeitsfaktor",
                        "Fairness of labor, ownership, access and damage allocation.",
                        "Fairness von Arbeit, Eigentum, Zugang und Schadensverteilung."),
    "ESV": Abbreviation("ESV", "#E6BEFF", "Effective stack value", "Effektiver Stapelwert",
                        "Quality-weighted money value: SG × MAT × QAL × USE × JUS.",
                        "Qualitätsgewichteter Geldwert: SG × MAT × QAL × USE × JUS."),
    "VSG": Abbreviation("VSG", "#9A6324", "Verified SG", "Verifiziertes SG",
                        "Effective value accepted by validators and minted as spendable currency.",
                        "Effektiver Wert, der von Validatoren anerkannt und als ausgebbare Währung geprägt wird."),
    "USG": Abbreviation("USG", "#FFFAC8", "Unverified SG claim", "Unverifizierter SG-Anspruch",
                        "Value claimed by a company but not publicly minted because verification failed.",
                        "Von einer Firma beanspruchter Wert, der wegen fehlender Prüfung nicht öffentlich geprägt wird."),
    "CLD": Abbreviation("CLD", "#800000", "Cycle debt", "Kreislaufschuld",
                        "Damage or open-loop cost caused by pollution, shortage or missing reintegration.",
                        "Schaden oder offene Schleifenkosten durch Verschmutzung, Mangel oder fehlende Rückintegration."),
    "CLR": Abbreviation("CLR", "#AAFFC3", "Closed-loop rate", "Geschlossene-Schleifen-Rate",
                        "Share of recent material transformations that reached return, soil or loop closure stations.",
                        "Anteil jüngerer Materialtransformationen, die Rückführung, Boden oder Schleifenschluss erreichen."),
    "MSI": Abbreviation("MSI", "#808000", "Material Stock Index", "Materialbestandsindex",
                        "Balance score of food, waste, return and soil stocks.",
                        "Bilanzwert von Nahrung, Abfall, Rückführung und Bodenbeständen."),
    "SOF": Abbreviation("SOF", "#FFD8B1", "Soil fertility", "Bodenfruchtbarkeit",
                        "Capacity of soil to support plant growth and reintegration.",
                        "Fähigkeit des Bodens, Pflanzenwachstum und Rückintegration zu tragen."),
    "WAT": Abbreviation("WAT", "#000075", "Water", "Wasser",
                        "Available water for growth, health and microbial stability.",
                        "Verfügbares Wasser für Wachstum, Gesundheit und mikrobielle Stabilität."),
    "MIC": Abbreviation("MIC", "#808080", "Microbes", "Mikroben",
                        "Microbial activity for decomposition and return.",
                        "Mikrobielle Aktivität für Zersetzung und Rückführung."),
    "HEA": Abbreviation("HEA", "#FFD700", "Heat", "Hitze",
                        "Geological or volcanic heat available for transformation.",
                        "Geologische oder vulkanische Hitze für Transformationen."),
    "POL": Abbreviation("POL", "#A9A9A9", "Pollution", "Verschmutzung",
                        "Toxic load that lowers quality and creates cycle debt.",
                        "Giftlast, die Qualität senkt und Kreislaufschuld erzeugt."),
    "HLT": Abbreviation("HLT", "#DCBEFF", "Health", "Gesundheit",
                        "Population and organism health produced by food, water and care loops.",
                        "Bevölkerungs- und Organismusgesundheit aus Nahrung, Wasser und Pflegekreisläufen."),
    "INF": Abbreviation("INF", "#A6CEE3", "Infrastructure", "Infrastruktur",
                        "Capacity for markets, sanitation, verification and safe return.",
                        "Kapazität für Märkte, Sanitärsysteme, Prüfung und sichere Rückführung."),
    "TEC": Abbreviation("TEC", "#1F78B4", "Technology", "Technologie",
                        "Tools that improve measurement, transformation and return safety.",
                        "Werkzeuge, die Messung, Transformation und Rückführungssicherheit verbessern."),
    "JIX": Abbreviation("JIX", "#B2DF8A", "Justice index", "Gerechtigkeitsindex",
                        "Planet-level social fairness and legal reliability.",
                        "Planetarer Wert für soziale Fairness und rechtliche Verlässlichkeit."),
    "CPI": Abbreviation("CPI", "#33A02C", "Circular price index", "Kreislaufpreisindex",
                        "Inflation indicator based on money supply, output, debt and scarcity.",
                        "Inflationsindikator aus Geldmenge, Output, Schuld und Knappheit."),
    "TAX": Abbreviation("TAX", "#FB9A99", "Tax", "Steuer",
                        "Public deduction on damaging or extractive transitions.",
                        "Öffentlicher Abzug auf schädliche oder extraktive Übergänge."),
    "SUB": Abbreviation("SUB", "#E31A1C", "Subsidy/bonus", "Subvention/Bonus",
                        "Public reward for compost, soil building, clean water or fair return work.",
                        "Öffentliche Belohnung für Kompost, Bodenaufbau, sauberes Wasser oder faire Rückführungsarbeit."),
    "SEG": Abbreviation("SEG", "#FF7F00", "Company segment", "Unternehmenssegment",
                        "The licensed part of the cycle a company is allowed and optimized to operate.",
                        "Lizenzierter Kreislaufausschnitt, den ein Unternehmen bearbeiten darf."),
}

ANSI_CODES = [31, 32, 34, 35, 36, 33, 91, 92, 94, 95, 96, 93]


def ansi(code: str, s: str, enabled: bool = True) -> str:
    if not enabled:
        return s
    idx = list(ABBREVIATIONS.keys()).index(code) % len(ANSI_CODES) if code in ABBREVIATIONS else 0
    return f"\033[{ANSI_CODES[idx]}m{s}\033[0m"


def badge(code: str) -> str:
    ab = ABBREVIATIONS.get(code)
    if not ab:
        return f"`{code}`"
    # Black text for very light colors, white for darker backgrounds.
    light = ab.color.upper() in {"#FFFAC8", "#BCF60C", "#FABEBE", "#AAFFC3", "#FFD8B1", "#DCBEFF", "#A6CEE3", "#B2DF8A"}
    fg = "#111111" if light else "#FFFFFF"
    return f'<span style="background:{ab.color};color:{fg};padding:2px 7px;border-radius:999px;font-weight:700;white-space:nowrap">{code}</span>'


def abbreviations_markdown(lang: str, codes: Optional[Sequence[str]] = None) -> str:
    codes = list(codes or ABBREVIATIONS.keys())
    lines = ["| " + text(lang, "Code", "Kürzel") + " | " + text(lang, "Meaning", "Bedeutung") + " | " + text(lang, "Explanation", "Erklärung") + " |",
             "|---|---|---|"]
    for code in codes:
        ab = ABBREVIATIONS[code]
        lines.append(f"| {badge(code)} | {text(lang, ab.name_en, ab.name_de)} | {text(lang, ab.explanation_en, ab.explanation_de)} |")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Stations and planet kinds
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Station:
    no: int
    letter: str
    form_de: str
    form_en: str
    name_de: str
    name_en: str
    domain: str
    description_de: str
    description_en: str


STATIONS: Dict[int, Station] = {
    1: Station(1, "A", "Punkt", "point", "Befruchtung", "Fecundation", "origin", "Pollination, Befruchtung, Start einer neuen Identität.", "Pollination, fertilization, start of a new identity."),
    2: Station(2, "B", "Linie", "line", "Samen", "Seed", "plant", "Samen, Keimfähigkeit, gespeichertes Potenzial.", "Seed, germinability, stored potential."),
    3: Station(3, "C", "Dreieck", "triangle", "Keimling", "Seedling", "plant", "Keimling, Sprossen, erste Verwurzelung.", "Seedling, sprouts, first rooting."),
    4: Station(4, "D", "Quadrat", "square", "Wachstum", "Growth", "plant", "Grüne Pflanze, Biomasse, photosynthetischer Wert.", "Green plant, biomass, photosynthetic value."),
    5: Station(5, "E", "Pentagramm", "pentagram", "Dünger-Wachstum", "Fertilizer growth", "soil", "Dung, Dünger, Mist, Mulch, Holz, stärkeres Wachstum.", "Dung, fertilizer, manure, mulch, wood, stronger growth."),
    6: Station(6, "F", "Hexagramm", "hexagram", "Blüte", "Blossom", "plant", "Blume, Blüte, Reife- und Fortpflanzungszeichen.", "Flower, blossom, maturity and reproduction signal."),
    7: Station(7, "G", "Heptagramm", "heptagram", "Ernte", "Harvest", "food", "Herausreißen, Schneiden, Ernten, Erntegut.", "Pulling out, cutting, harvesting, crop."),
    8: Station(8, "H", "Oktagramm", "octagram", "Essen", "Eating", "food", "Essen, Füttern, Ernähren, Aufnahme durch Lebewesen.", "Eating, feeding, nurturing, intake by living beings."),
    9: Station(9, "I", "Nonagramm", "nonagram", "Fleisch/Wesen", "Flesh/creature", "body", "Fleisch, Tier, Mensch, Volk, Wesen, Körperaufbau.", "Flesh, animal, human, people, creature, body formation."),
    10: Station(10, "J", "Dekagramm", "decagram", "Einpassung", "Fitting-in", "ecology", "Einpassung in anderes Leben, ökologische Rolle.", "Fitting into other life, ecological role."),
    11: Station(11, "K", "Hendekagramm", "hendecagram", "Produktionskette", "Production chain", "production", "Nahrungskette und Produktionskette: Korn, Müller, Mehl, Bäcker, Brot, Markt, Konsum.", "Food chain and production chain: grain, miller, flour, baker, bread, market, consumption."),
    12: Station(12, "L", "Dodekagramm", "dodecagram", "Verdauung", "Digestion", "digestion", "Magen, Verdauung, Umwandlung von Nahrung in Körper und Reststoff.", "Stomach, digestion, conversion of food into body and residue."),
    13: Station(13, "M", "Triskaidekagramm", "triskaidecagram", "Gülle/Kot", "Slurry/excrement", "waste", "Gülle, Kot, organische Rückgabe, Mikrobenfutter.", "Slurry, feces, organic return, microbial food."),
    14: Station(14, "N", "Tetrakaidekagramm", "tetrakaidecagram", "Kreislaufwirtschaft", "Circular economy", "governance", "Tiere, Pflanzen, Mikroben, Erde, Wiederholung, Gesetze, Gerechtigkeit, Signale.", "Animals, plants, microbes, earth, repetition, laws, justice, signals."),
    15: Station(15, "O", "Pentadekagramm", "pentadecagram", "Zersetzung", "Decomposition", "microbes", "Degradation, Zersetzen, Auflösen, Rückführung.", "Degradation, decomposing, dissolving, return."),
    16: Station(16, "P", "Hexadekagramm", "hexadecagram", "Chemische Reaktion", "Chemical reaction", "chemistry", "Reaktion, Umwandlung, Elementwechsel, chemische Neuordnung.", "Reaction, transformation, elemental shift, chemical reordering."),
    17: Station(17, "Q", "Heptadekagramm", "heptadecagram", "Rückintegration", "Reintegration", "return", "Assimilation, Einbettung, in den Kreislauf zurückführen.", "Assimilation, embedding, return into the cycle."),
    18: Station(18, "R", "Oktadekagramm", "octadecagram", "Tod/Mikroben", "Death/microbes", "death", "Totes Leben, Mikrobenfutter, organische Restidentität.", "Dead life, microbial food, organic residual identity."),
    19: Station(19, "S", "Nonadekagramm", "nonadecagram", "Erde/Boden/Planet", "Earth/soil/planet", "planet", "Erde, Boden, Planet Erde, Standort der Kreisläufe.", "Earth, soil, planet Earth, location of cycles."),
    20: Station(20, "T", "Ikosigramm", "icosagram", "Hitze/Lava", "Heat/lava", "geology", "Heiße Lava, Hitze, Wärmestrom, planetare Grundkraft.", "Hot lava, heat, heat stream, planetary base force."),
    21: Station(21, "U", "Henaikosigramm", "henaicosagram", "Vulkanasche", "Volcanic ash", "volcanic", "Vulkan, Asche, eruptive Mineralfreisetzung.", "Volcano, ash, eruptive mineral release."),
    22: Station(22, "V", "Dyoikosigramm", "dyoicosagram", "Mineralische Neuordnung", "Mineral reordering", "volcanic", "Abkühlung, Gesteinsbildung, Asche-zu-Boden-Substrat.", "Cooling, rock formation, ash-to-soil substrate."),
}


@dataclass(frozen=True)
class PlanetKind:
    code: str
    label_de: str
    label_en: str
    cycle_length: int


EARTH_TYPE = PlanetKind("EarthType", "Erde-Typ", "Earth-type", 20)
VULCAN_TYPE = PlanetKind("VulcanType", "Vulkan-Typ", "Vulcan-type", 22)
PLANET_KINDS = {"EarthType": EARTH_TYPE, "VulcanType": VULCAN_TYPE}


# ---------------------------------------------------------------------------
# Segment licenses: companies mostly handle parts of the cycle
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class SegmentDefinition:
    code: str
    start: int
    end: int
    label_en: str
    label_de: str
    explanation_en: str
    explanation_de: str
    weight: float
    planet_scope: str = "any"  # any, EarthType, VulcanType
    partial: bool = True

    def compatible(self, planet_type: str) -> bool:
        return self.planet_scope == "any" or self.planet_scope == planet_type


SEGMENTS: List[SegmentDefinition] = [
    SegmentDefinition("ORG", 1, 3, "Origin-to-seed", "Ursprung-bis-Samen",
                      "Firms that handle fecundation, seed creation and early potential.",
                      "Firmen für Befruchtung, Samenbildung und frühes Potenzial.", 7.0),
    SegmentDefinition("GRO", 3, 5, "Seedling-to-growth", "Keimling-bis-Wachstum",
                      "Growth firms turn seedlings into biomass and fertilizer-responsive plants.",
                      "Wachstumsfirmen führen Keimlinge zu Biomasse und düngerfähigen Pflanzen.", 8.0),
    SegmentDefinition("FHV", 5, 7, "Fertilizer-to-harvest", "Dünger-bis-Ernte",
                      "This is the requested example of a company operating only stations 5 to 7.",
                      "Dies ist das gewünschte Beispiel einer Firma, die nur Station 5 bis 7 übernimmt.", 10.0),
    SegmentDefinition("FOD", 7, 8, "Harvest-to-food", "Ernte-bis-Essen",
                      "Distribution firms move harvest into edible access without closing digestion.",
                      "Verteilfirmen führen Ernte zu essbarem Zugang, ohne Verdauung zu schließen.", 6.0),
    SegmentDefinition("PRC", 7, 11, "Production-chain", "Produktionskette",
                      "Millers, bakers and traders operate the grain-flour-bread-market chain.",
                      "Müller, Bäcker und Händler bearbeiten Korn-Mehl-Brot-Markt-Ketten.", 7.0),
    SegmentDefinition("DIG", 8, 13, "Eating-to-slurry", "Essen-bis-Gülle",
                      "Care and digestion firms convert food into body value and recover excretion.",
                      "Pflege- und Verdauungsfirmen wandeln Essen in Körperwert und Ausscheidung.", 7.0),
    SegmentDefinition("GOV", 14, 15, "Governance-to-return-gate", "Gesetz-bis-Rückführungstor",
                      "Validators convert law, justice and signals into a usable return permission.",
                      "Validatoren wandeln Gesetz, Gerechtigkeit und Signale in Rückführungserlaubnis.", 4.0),
    SegmentDefinition("CMP", 13, 17, "Compost-to-reintegration", "Kompost-bis-Rückintegration",
                      "Compost firms decompose waste, perform chemistry and reach reintegration.",
                      "Kompostfirmen zersetzen Abfall, leisten Chemie und erreichen Rückintegration.", 9.0),
    SegmentDefinition("RSO", 15, 19, "Decomposition-to-soil", "Zersetzung-bis-Boden",
                      "This is the requested example of a company operating stations 15 to 19.",
                      "Dies ist das gewünschte Beispiel einer Firma, die Station 15 bis 19 übernimmt.", 10.0),
    SegmentDefinition("GEO", 19, 20, "Soil-to-heat memory", "Boden-bis-Hitzespeicher",
                      "Geological firms move soil/planet memory into heat/lava bookkeeping.",
                      "Geologiefirmen führen Boden-/Planetengedächtnis in Hitze-/Lava-Buchhaltung.", 3.5, "EarthType"),
    SegmentDefinition("VUL", 20, 22, "Lava-to-mineral", "Lava-bis-Mineral",
                      "Vulcan firms turn heat/lava into ash and mineral reordering.",
                      "Vulkanfirmen wandeln Hitze/Lava in Asche und mineralische Neuordnung.", 5.5, "VulcanType"),
    SegmentDefinition("MIN", 21, 5, "Ash-to-fertility", "Asche-bis-Fruchtbarkeit",
                      "Vulcan mineral firms wrap ash/minerals into fertilizer growth.",
                      "Vulkanische Mineralfirmen führen Asche/Minerale zurück in Düngerwachstum.", 4.5, "VulcanType"),
    SegmentDefinition("LCI", 17, 1, "Loop-closure integrator", "Schleifenschluss-Integrator",
                      "Rare integrators bridge reintegration back to fecundation so the circle can restart.",
                      "Seltene Integratoren schlagen die Brücke von Rückintegration zur Befruchtung.", 2.2, "any", partial=False),
    SegmentDefinition("FUL", 1, 20, "Full Earth loop", "Voller Erde-Kreislauf",
                      "Very rare company allowed to span almost the full Earth cycle.",
                      "Sehr seltene Firma mit Lizenz für fast den ganzen Erde-Kreislauf.", 0.7, "EarthType", partial=False),
    SegmentDefinition("FUV", 1, 22, "Full Vulcan loop", "Voller Vulkan-Kreislauf",
                      "Very rare company allowed to span almost the full Vulcan cycle.",
                      "Sehr seltene Firma mit Lizenz für fast den ganzen Vulkan-Kreislauf.", 0.7, "VulcanType", partial=False),
]




SEGMENT_COLORS: Dict[str, str] = {
    "ORG": "#E6194B",
    "GRO": "#3CB44B",
    "FHV": "#FFE119",
    "FOD": "#4363D8",
    "PRC": "#F58231",
    "DIG": "#911EB4",
    "GOV": "#46F0F0",
    "CMP": "#F032E6",
    "RSO": "#BCF60C",
    "GEO": "#008080",
    "VUL": "#9A6324",
    "MIN": "#800000",
    "LCI": "#AAFFC3",
    "FUL": "#808000",
    "FUV": "#1F78B4",
}


def seg_badge(code: str) -> str:
    color = SEGMENT_COLORS.get(code, "#FF7F00")
    light = color.upper() in {"#FFE119", "#46F0F0", "#BCF60C", "#AAFFC3"}
    fg = "#111111" if light else "#FFFFFF"
    return f'<span style="background:{color};color:{fg};padding:2px 7px;border-radius:999px;font-weight:700;white-space:nowrap">{code}</span>'


ROLE_BY_SEGMENT: Dict[str, Tuple[str, str]] = {
    "ORG": ("seed_company", "Saatfirma"),
    "GRO": ("growth_company", "Wachstumsfirma"),
    "FHV": ("fertility_harvest_company", "Dünger-Ernte-Firma"),
    "FOD": ("food_access_company", "Nahrungszugangsfirma"),
    "PRC": ("production_chain_company", "Produktionskettenfirma"),
    "DIG": ("digestion_care_company", "Verdauungs-/Pflegefirma"),
    "GOV": ("validator_company", "Validatorfirma"),
    "CMP": ("compost_company", "Kompostfirma"),
    "RSO": ("return_soil_company", "Rückführungs-Boden-Firma"),
    "GEO": ("geology_company", "Geologiefirma"),
    "VUL": ("vulcan_company", "Vulkanfirma"),
    "MIN": ("mineral_fertility_company", "Mineral-Fruchtbarkeitsfirma"),
    "LCI": ("loop_integrator", "Schleifenintegrator"),
    "FUL": ("full_cycle_company", "Vollkreislauffirma"),
    "FUV": ("full_vulcan_company", "Vollvulkanfirma"),
}


def station_path(start: int, end: int, n: int) -> List[int]:
    if start <= end:
        return list(range(start, end + 1))
    return list(range(start, n + 1)) + list(range(1, end + 1))


def station_name(station: int, lang: str) -> str:
    s = STATIONS[station]
    return f"{s.no}-{s.letter} {text(lang, s.name_en, s.name_de)}"


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------


@dataclass
class Identity:
    identity_id: str
    label: str
    planet_type: str
    station: int
    repetition: int
    mass: float
    energy: float
    nutrients: float
    quality: float
    use: float
    justice: float
    owner_id: str
    tags: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)

    def passport(self) -> Dict[str, object]:
        return {
            "identity_id": self.identity_id,
            "label": self.label,
            "planet_type": self.planet_type,
            "cycle_length": PLANET_KINDS[self.planet_type].cycle_length,
            "station": self.station,
            "station_letter": STATIONS[self.station].letter,
            "repetition": self.repetition,
            "mass": self.mass,
            "energy": self.energy,
            "nutrients": self.nutrients,
            "quality": self.quality,
            "use": self.use,
            "justice": self.justice,
            "owner_id": self.owner_id,
            "tags": ";".join(self.tags),
            "recent_history": " | ".join(self.history[-6:]),
        }


@dataclass
class Company:
    company_id: str
    name: str
    segment_code: str
    segment_start: int
    segment_end: int
    partial: bool
    role_en: str
    role_de: str
    planet_name: str
    money: float
    debt: float
    skill: float
    fairness: float
    efficiency: float
    risk: float
    reputation: float
    sg_earned: float = 0.0
    sg_unverified: float = 0.0
    taxes_paid: float = 0.0
    subsidies_received: float = 0.0
    actions_done: int = 0
    idle_ticks: int = 0
    trades_done: int = 0

    def segment_label(self) -> str:
        return f"{self.segment_start}->{self.segment_end}"

    def credit_score(self) -> float:
        score = self.reputation * 0.35 + self.fairness * 0.25 + self.skill * 0.20 + self.efficiency * 0.12 + (1.0 - self.risk) * 0.08
        score -= self.debt / max(900.0, self.money + 900.0)
        return clamp(score, 0.0, 1.5)


@dataclass
class Loan:
    loan_id: str
    lender_id: str
    borrower_id: str
    principal: float
    outstanding: float
    due_tick: int
    expected_sg: float
    status: str = "active"


@dataclass
class Policy:
    exit_tax: float = 0.055
    pollutant_tax: float = 0.09
    soil_rent: float = 0.025
    entropy_levy: float = 0.018
    repair_subsidy: float = 0.075
    compost_bonus: float = 0.060
    water_purity_bonus: float = 0.028
    social_bonus: float = 0.030
    verification_strictness: float = 0.58
    company_specialization_bias: float = 0.86


@dataclass
class LedgerEntry:
    tick: int
    universe: str
    system: str
    planet: str
    planet_type: str
    company_id: str
    company_name: str
    segment_code: str
    segment_span: str
    partial_company: bool
    action: str
    identity_id: str
    identity_label: str
    from_station: int
    to_station: int
    start_repetition: int
    end_repetition: int
    ncl: int
    raw_sg: float
    uke: float
    mat: float
    qal: float
    use: float
    jus: float
    esv: float
    verified: bool
    minted_sg: float
    usg: float
    tax: float
    subsidy: float
    debt_created: float
    outcome: str
    explanation_en: str
    explanation_de: str
    formula_en: str
    formula_de: str
    analysis_en: str
    analysis_de: str
    alternatives_en: str
    alternatives_de: str


@dataclass
class TradeRecord:
    tick: int
    universe: str
    system: str
    planet: str
    seller_id: str
    buyer_id: str
    identity_id: str
    station: int
    mass: float
    price: float
    value: float
    reason: str


@dataclass
class PlanetSnapshot:
    tick: int
    universe: str
    system: str
    planet: str
    planet_type: str
    population: float
    hlt: float
    sof: float
    wat: float
    mic: float
    hea: float
    pol: float
    jix: float
    inf: float
    tec: float
    cpi: float
    money_supply: float
    public_budget: float
    cld: float
    vsg_tick: float
    usg_tick: float
    local_trade_tick: float
    interplanetary_trade_tick: float
    clr: float
    msi: float
    food_stock: float
    waste_stock: float
    return_stock: float
    soil_stock: float
    partial_company_share: float


# ---------------------------------------------------------------------------
# Core formula
# ---------------------------------------------------------------------------


def original_loop_value(planet_type: str, start: int, end: int, end_repetition: int) -> int:
    n = PLANET_KINDS[planet_type].cycle_length
    value = (end_repetition - 1) * n + end - start
    if value < 0:
        raise ValueError("Invalid loop value: end lies before start without enough repetitions.")
    return value


def transition_distance(planet_type: str, start_station: int, start_repetition: int, end_station: int) -> Tuple[int, int]:
    n = PLANET_KINDS[planet_type].cycle_length
    if start_station < 1 or start_station > n or end_station < 1 or end_station > n:
        raise ValueError("Station outside native cycle length.")
    if end_station > start_station:
        end_repetition = start_repetition
    else:
        end_repetition = start_repetition + 1
    raw = (end_repetition - start_repetition) * n + end_station - start_station
    return raw, end_repetition


# ---------------------------------------------------------------------------
# Planet economy
# ---------------------------------------------------------------------------


class PlanetEconomy:
    def __init__(self, universe_name: str, system_name: str, name: str, kind: PlanetKind,
                 rng: random.Random, companies_per_planet: int = 45) -> None:
        self.universe_name = universe_name
        self.system_name = system_name
        self.name = name
        self.kind = kind
        self.rng = rng
        self.policy = Policy(company_specialization_bias=rng.uniform(0.78, 0.93))
        self.population = rng.uniform(700.0, 1900.0)
        self.hlt = rng.uniform(0.66, 0.93)
        self.sof = rng.uniform(0.46, 0.86)
        self.wat = rng.uniform(0.45, 0.95)
        self.mic = rng.uniform(0.44, 0.90)
        self.hea = rng.uniform(0.35, 0.76) + (0.20 if kind.code == "VulcanType" else 0.0)
        self.pol = rng.uniform(0.02, 0.18)
        self.jix = rng.uniform(0.56, 0.92)
        self.inf = rng.uniform(0.38, 0.82)
        self.tec = rng.uniform(0.34, 0.78)
        self.cpi = 1.0
        self.public_budget = rng.uniform(700.0, 1600.0)
        self.money_supply = self.public_budget
        self.cld = 0.0
        self.vsg_tick = 0.0
        self.usg_tick = 0.0
        self.local_trade_tick = 0.0
        self.interplanetary_trade_tick = 0.0
        self.identities: List[Identity] = []
        self.companies: List[Company] = []
        self.loans: List[Loan] = []
        self.ledger: List[LedgerEntry] = []
        self.trades: List[TradeRecord] = []
        self.snapshots: List[PlanetSnapshot] = []
        self.event_log: List[str] = []
        self._id_counter = 0
        self._company_counter = 0
        self._loan_counter = 0
        self._create_companies(companies_per_planet)
        self._seed_initial_identities()
        self._update_money_supply()

    # ----------------------------- identifiers -----------------------------

    def next_id(self, prefix: str) -> str:
        self._id_counter += 1
        return f"{self.name[:4].upper()}-{prefix}-{self._id_counter:06d}"

    def next_company_id(self) -> str:
        self._company_counter += 1
        return f"{self.name[:3].upper()}-CO-{self._company_counter:04d}"

    def next_loan_id(self) -> str:
        self._loan_counter += 1
        return f"{self.name[:3].upper()}-LN-{self._loan_counter:04d}"

    # ----------------------------- setup -----------------------------

    def _compatible_segments(self) -> List[SegmentDefinition]:
        return [s for s in SEGMENTS if s.compatible(self.kind.code) and s.end <= self.kind.cycle_length if s.start <= self.kind.cycle_length]

    def _choose_segment(self) -> SegmentDefinition:
        compatible = self._compatible_segments()
        # The key requested behavior: most companies are partial-cycle firms.
        partials = [s for s in compatible if s.partial]
        broad = [s for s in compatible if not s.partial]
        if partials and (not broad or self.rng.random() < self.policy.company_specialization_bias):
            return weighted_choice(self.rng, [(s, s.weight) for s in partials])  # type: ignore[return-value]
        return weighted_choice(self.rng, [(s, s.weight) for s in broad or partials])  # type: ignore[return-value]

    def _create_companies(self, n: int) -> None:
        syllables = ["Ari", "Sol", "Kora", "Nexa", "Mira", "Vesta", "Rho", "Zen", "Gaia", "Pyra", "Luma", "Tor", "Sena", "Orin"]
        for _ in range(n):
            seg = self._choose_segment()
            role_en, role_de = ROLE_BY_SEGMENT.get(seg.code, ("cycle_company", "Kreislauffirma"))
            name = self.rng.choice(syllables) + self.rng.choice(syllables).lower() + " " + seg.code
            company = Company(
                company_id=self.next_company_id(),
                name=name,
                segment_code=seg.code,
                segment_start=seg.start,
                segment_end=seg.end,
                partial=seg.partial,
                role_en=role_en,
                role_de=role_de,
                planet_name=self.name,
                money=self.rng.uniform(70.0, 240.0),
                debt=self.rng.uniform(0.0, 50.0),
                skill=clamp(self.rng.gauss(0.76, 0.16), 0.18, 1.30),
                fairness=clamp(self.rng.gauss(self.jix, 0.14), 0.12, 1.25),
                efficiency=clamp(self.rng.gauss(0.76, 0.15), 0.20, 1.32),
                risk=clamp(self.rng.betavariate(2.1, 5.1), 0.02, 0.96),
                reputation=clamp(self.rng.gauss(0.72, 0.15), 0.12, 1.25),
            )
            self.companies.append(company)

    def _create_identity(self, label: str, station: int, mass: float, owner_id: str,
                         quality: Optional[float] = None, use: Optional[float] = None,
                         justice: Optional[float] = None, energy: Optional[float] = None,
                         nutrients: Optional[float] = None, tags: Optional[List[str]] = None) -> Identity:
        quality = self.rng.uniform(0.70, 1.05) if quality is None else quality
        use = self.rng.uniform(0.70, 1.05) if use is None else use
        justice = self.jix if justice is None else justice
        energy = mass * self.rng.uniform(0.25, 1.6) if energy is None else energy
        nutrients = mass * self.rng.uniform(0.25, 1.6) if nutrients is None else nutrients
        ident = Identity(
            identity_id=self.next_id("ID"),
            label=label,
            planet_type=self.kind.code,
            station=station,
            repetition=1,
            mass=max(0.0001, mass),
            energy=max(0.0, energy),
            nutrients=max(0.0, nutrients),
            quality=clamp(quality, 0.02, 1.50),
            use=clamp(use, 0.02, 1.50),
            justice=clamp(justice, 0.02, 1.50),
            owner_id=owner_id,
            tags=list(tags or []),
            history=[f"created@{station}:{STATIONS[station].letter}"],
        )
        self.identities.append(ident)
        return ident

    def _seed_initial_identities(self) -> None:
        state_owner = f"STATE-{self.name}"
        seed_specs = [
            ("fecundation_identity", 1, 4, 0.9, 0.75, ["origin", "seed"]),
            ("seed_batch", 2, 8, 0.92, 0.90, ["seed", "plant"]),
            ("seedling_sprouts", 3, 6, 0.86, 0.86, ["plant", "sprout"]),
            ("green_biomass", 4, 10, self.sof, 0.84, ["plant", "biomass"]),
            ("fertility_mulch", 5, 6, self.sof, 0.85, ["fertilizer", "soil"]),
            ("flowering_crop", 6, 5, 0.84, 0.88, ["flower", "plant"]),
            ("crop_grain", 7, 8, 0.86, 0.96, ["food", "grain"]),
            ("market_food", 8, 6, 0.82, 1.00, ["food", "edible"]),
            ("body_life", 9, 3, self.hlt, 0.90, ["body", "creature"]),
            ("production_chain_stock", 11, 5, 0.82, 0.92, ["production", "food"]),
            ("digestive_residue", 12, 5, 0.70, 0.72, ["digestion"]),
            ("organic_waste", 13, 8, 0.62, 0.70, ["waste", "microbes"]),
            ("law_signal", 14, 3, self.jix, 0.95, ["law", "signal"]),
            ("decomposition_stock", 15, 5, 0.66, 0.74, ["compost", "microbes"]),
            ("reaction_stock", 16, 4, 0.68, 0.76, ["chemistry"]),
            ("return_stock", 17, 4, 0.78, 0.88, ["return", "soil"]),
            ("dead_organic_matter", 18, 4, 0.58, 0.70, ["death", "microbes"]),
            ("soil_volume", 19, 8, self.sof, 0.96, ["soil", "planet"]),
            ("heat_stream", 20, 4, self.hea, 0.62, ["heat", "geology"]),
        ]
        for label, station, count, quality, use, tags in seed_specs:
            if station <= self.kind.cycle_length:
                for _ in range(count):
                    self._create_identity(label, station, self.rng.uniform(0.8, 6.5), state_owner,
                                          quality=quality * self.rng.uniform(0.85, 1.16), use=use,
                                          justice=self.jix, tags=list(tags))
        if self.kind.code == "VulcanType":
            for _ in range(6):
                self._create_identity("volcanic_ash", 21, self.rng.uniform(1.0, 7.0), state_owner,
                                      quality=self.rng.uniform(0.55, 1.16), use=0.78, tags=["ash", "mineral", "volcanic"])
            for _ in range(4):
                self._create_identity("mineral_substrate", 22, self.rng.uniform(1.0, 6.0), state_owner,
                                      quality=self.rng.uniform(0.64, 1.18), use=0.82, tags=["mineral", "soil"])

    # ----------------------------- identity selection -----------------------------

    def _split_identity(self, ident: Identity, amount: float) -> Identity:
        amount = max(0.0001, min(amount, ident.mass))
        if amount >= ident.mass * 0.97:
            return ident
        original_mass = ident.mass
        ratio = amount / original_mass
        clone = Identity(
            identity_id=self.next_id("SPL"),
            label=ident.label,
            planet_type=ident.planet_type,
            station=ident.station,
            repetition=ident.repetition,
            mass=amount,
            energy=ident.energy * ratio,
            nutrients=ident.nutrients * ratio,
            quality=ident.quality,
            use=ident.use,
            justice=ident.justice,
            owner_id=ident.owner_id,
            tags=list(ident.tags),
            history=list(ident.history[-5:]) + [f"split:{amount:.3f}"],
        )
        ident.mass -= amount
        ident.energy *= (1.0 - ratio)
        ident.nutrients *= (1.0 - ratio)
        self.identities.append(clone)
        return clone

    def stock_mass(self, station: Optional[int] = None, domain: Optional[str] = None) -> float:
        total = 0.0
        for ident in self.identities:
            if station is not None and ident.station != station:
                continue
            if domain is not None and STATIONS[ident.station].domain != domain:
                continue
            total += ident.mass
        return total

    def avg_quality(self, station: Optional[int] = None) -> float:
        total = 0.0
        weights = 0.0
        for ident in self.identities:
            if station is not None and ident.station != station:
                continue
            total += ident.quality * ident.mass
            weights += ident.mass
        return safe_div(total, weights, 0.0)

    def _identity_candidates_for_company(self, company: Company) -> List[Identity]:
        n = self.kind.cycle_length
        path = station_path(company.segment_start, company.segment_end, n)
        # A partial company usually wants inputs before its endpoint. End station is an output stock.
        input_stations = set(path[:-1]) if len(path) > 1 else set(path)
        candidates = [i for i in self.identities if i.station in input_stations and i.mass >= 0.05]
        # Prefer identities owned by the company or available state stocks, but do not block market circulation.
        scored: List[Tuple[float, Identity]] = []
        for ident in candidates:
            ownership = 0.18 if ident.owner_id == company.company_id else 0.0
            start_bonus = 0.15 if ident.station == company.segment_start else 0.0
            score = ident.mass * ident.quality * ident.use + ownership + start_bonus + self.rng.random() * 0.05
            scored.append((score, ident))
        scored.sort(key=lambda x: x[0], reverse=True)
        return [i for _, i in scored]

    # ----------------------------- calculation and transformation -----------------------------

    def _verification_probability(self, company: Company) -> float:
        validator_share = safe_div(sum(1 for c in self.companies if c.segment_code == "GOV"), len(self.companies), 0.0)
        p = (0.20 +
             self.policy.verification_strictness * 0.24 +
             self.inf * 0.17 +
             self.tec * 0.12 +
             self.jix * 0.12 +
             company.reputation * 0.12 +
             validator_share * 0.10 -
             self.pol * 0.08)
        return clamp(p, 0.08, 0.985)

    def _tax_rate(self, company: Company, target_station: int, action: str) -> float:
        rate = 0.0
        if target_station in (20, 21):
            rate += self.policy.entropy_levy
        if self.pol > 0.25:
            rate += self.policy.pollutant_tax * min(1.0, self.pol)
        if target_station in (19, 20):
            rate += self.policy.soil_rent * 0.5
        if company.fairness < 0.45:
            rate += 0.035
        if company.segment_code in ("FUL", "FUV"):
            rate += self.policy.exit_tax * 0.35
        return clamp(rate, 0.0, 0.35)

    def _subsidy(self, target_station: int, company: Company, esv: float) -> float:
        rate = 0.0
        if target_station in (15, 16, 17):
            rate += self.policy.compost_bonus
        if target_station in (17, 19, 5):
            rate += self.policy.repair_subsidy
        if company.fairness > 0.80:
            rate += self.policy.social_bonus
        if self.wat > 0.75 and target_station in (5, 17, 19):
            rate += self.policy.water_purity_bonus
        return esv * clamp(rate, 0.0, 0.22)

    def _environment_modifiers(self, company: Company, start: int, target: int) -> Tuple[float, float, float, float, float, List[str]]:
        """Return quality_delta, use_delta, material_loss, material_gain, pollution_delta, tags."""
        qd = 0.0
        ud = 0.0
        loss = 0.015
        gain = 0.0
        pd = 0.0
        tags: List[str] = []
        # Use target and segment to make each partial industry materially different.
        if target in (3, 4, 5, 6, 7):
            water_stress = max(0.0, 0.55 - self.wat)
            qd += (self.sof - 0.50) * 0.08 - water_stress * 0.10 + company.skill * 0.018
            ud += 0.035
            gain += max(0.0, (self.sof + self.wat + self.mic) / 3.0 - 0.38) * 0.30
            self.wat = clamp(self.wat - 0.0012 * company.efficiency, 0.02, 1.5)
            self.sof = clamp(self.sof - 0.0007 * company.efficiency, 0.02, 1.5)
            tags.extend(["plant"])
            if target == 7:
                tags.extend(["food", "grain", "harvest"])
        if target in (8, 9, 10, 11, 12, 13):
            qd += company.skill * 0.020 + self.inf * 0.006
            ud += 0.050
            loss += 0.045 if target in (12, 13) else 0.025
            pd += 0.0006 * max(0.0, 1.0 - company.efficiency)
            tags.extend(["food"] if target in (8, 11) else ["digestion"])
            if target == 13:
                tags.extend(["waste", "microbes"])
        if target in (15, 16, 17, 18, 19):
            qd += company.skill * 0.025 + (self.mic - 0.5) * 0.070
            ud += 0.055
            loss += 0.035 if target != 19 else 0.020
            pd -= 0.0028 * company.skill
            tags.extend(["return", "soil", "microbes"])
            if target in (17, 19):
                self.sof = clamp(self.sof + 0.0020 * company.skill, 0.02, 1.5)
                self.mic = clamp(self.mic + 0.0018 * company.skill, 0.02, 1.5)
        if target in (20, 21, 22):
            qd += company.skill * 0.012 + self.hea * 0.010
            ud += 0.035
            loss += 0.020
            gain += 0.080 if target in (21, 22) else 0.0
            pd += 0.0035 if target == 21 else -0.0008
            tags.extend(["geology", "heat"])
            if target in (21, 22):
                tags.extend(["volcanic", "mineral"])
        if target in (1, 2):
            qd += self.sof * 0.015 + company.skill * 0.015
            ud += 0.025
            tags.extend(["origin", "seed"])
        if company.segment_code == "GOV":
            qd += self.jix * 0.020 + company.fairness * 0.030
            ud += 0.060
            loss = 0.0
            pd -= 0.001
            tags.extend(["law", "signal", "justice"])
            self.jix = clamp(self.jix + 0.0009 * company.fairness, 0.02, 1.5)
            self.inf = clamp(self.inf + 0.0004 * company.skill, 0.02, 1.5)
        return qd, ud, loss, gain, pd, tags

    def _next_target_for_company(self, company: Company, ident: Identity) -> int:
        n = self.kind.cycle_length
        path = station_path(company.segment_start, company.segment_end, n)
        if ident.station not in path:
            return company.segment_end
        idx = path.index(ident.station)
        # Most segment firms sell an endpoint service; sometimes they only advance by one station.
        if self.rng.random() < 0.64 or idx == len(path) - 2:
            return company.segment_end
        return path[min(len(path) - 1, idx + 1)]

    def _make_explanations(self, company: Company, ident: Identity, start: int, target: int, start_rep: int,
                           end_rep: int, raw: float, uke: float, mat: float, qal: float, use: float, jus: float,
                           esv: float, verified: bool, tax: float, subsidy: float, debt: float, outcome: str) -> Tuple[str, str, str, str, str, str, str, str]:
        n = self.kind.cycle_length
        seg = next((s for s in SEGMENTS if s.code == company.segment_code), None)
        seg_en = seg.explanation_en if seg else "The company operates its licensed segment."
        seg_de = seg.explanation_de if seg else "Das Unternehmen bearbeitet sein lizenziertes Segment."
        exp_en = (
            f"This calculation simulates a partial-cycle company, {company.name}, operating {badge('SEG')} {seg_badge(company.segment_code)} {company.segment_start}->{company.segment_end}. "
            f"The identity starts at station {start} ({STATIONS[start].name_en}) and is handed to station {target} ({STATIONS[target].name_en}). "
            f"The reason is division of labor: most companies do not own the whole cosmic loop; they specialize in a productive segment and pass the identity onward. {seg_en}"
        )
        exp_de = (
            f"Diese Rechnung simuliert ein Teilzyklus-Unternehmen, {company.name}, mit {badge('SEG')} {seg_badge(company.segment_code)} {company.segment_start}->{company.segment_end}. "
            f"Die Identität startet bei Station {start} ({STATIONS[start].name_de}) und wird an Station {target} ({STATIONS[target].name_de}) übergeben. "
            f"Der Grund ist Arbeitsteilung: Die meisten Unternehmen besitzen nicht die ganze kosmische Schleife, sondern spezialisieren sich auf einen produktiven Ausschnitt und reichen die Identität weiter. {seg_de}"
        )
        formula_en = (
            f"{badge('SG')} = ({badge('REP')}_end - {badge('REP')}_start) × {badge('NCL')} + {badge('END')} - {badge('STA')} "
            f"= ({end_rep} - {start_rep}) × {n} + {target} - {start} = {raw:.3f}.\n"
            f"{badge('UKE')} = {badge('SG')} / {badge('NCL')} = {raw:.3f} / {n} = {uke:.4f}.\n"
            f"{badge('ESV')} = {badge('SG')} × {badge('MAT')} × {badge('QAL')} × {badge('USE')} × {badge('JUS')} "
            f"= {raw:.3f} × {mat:.3f} × {qal:.3f} × {use:.3f} × {jus:.3f} = {esv:.3f}."
        )
        formula_de = (
            f"{badge('SG')} = ({badge('REP')}_Ende - {badge('REP')}_Start) × {badge('NCL')} + {badge('END')} - {badge('STA')} "
            f"= ({end_rep} - {start_rep}) × {n} + {target} - {start} = {raw:.3f}.\n"
            f"{badge('UKE')} = {badge('SG')} / {badge('NCL')} = {raw:.3f} / {n} = {uke:.4f}.\n"
            f"{badge('ESV')} = {badge('SG')} × {badge('MAT')} × {badge('QAL')} × {badge('USE')} × {badge('JUS')} "
            f"= {raw:.3f} × {mat:.3f} × {qal:.3f} × {use:.3f} × {jus:.3f} = {esv:.3f}."
        )
        if verified:
            analysis_en = (
                f"Outcome: {outcome}. Verification succeeded, so {badge('VSG')} is minted. "
                f"The company receives effective value after {badge('TAX')} plus any {badge('SUB')}. "
                f"The result is strong when material, quality, usefulness and justice are all high; here the multipliers produced {esv:.2f} effective units. "
                f"Debt created by this calculation is {debt:.2f}, so the net effect is {'regenerative' if debt < esv * 0.05 else 'mixed'}."
            )
            analysis_de = (
                f"Ergebnis: {outcome}. Die Prüfung war erfolgreich, daher wird {badge('VSG')} geprägt. "
                f"Das Unternehmen erhält den effektiven Wert nach {badge('TAX')} plus mögliche {badge('SUB')}. "
                f"Das Ergebnis ist stark, wenn Material, Qualität, Nutzen und Gerechtigkeit gemeinsam hoch sind; hier erzeugten die Multiplikatoren {esv:.2f} effektive Einheiten. "
                f"Die in dieser Rechnung erzeugte Schuld beträgt {debt:.2f}, also ist der Nettoeffekt {'regenerativ' if debt < esv * 0.05 else 'gemischt'}."
            )
        else:
            analysis_en = (
                f"Outcome: {outcome}. Verification failed, therefore the value remains {badge('USG')} rather than spendable money. "
                f"The physical transformation still happened, but the public ledger refuses to mint full currency until validation improves. "
                f"This protects the economy from fake loops and keeps inflation tied to real evidence. Debt created is {debt:.2f}."
            )
            analysis_de = (
                f"Ergebnis: {outcome}. Die Prüfung scheiterte, daher bleibt der Wert {badge('USG')} statt ausgebbarer Währung. "
                f"Die physische Transformation fand statt, aber das öffentliche Hauptbuch prägt kein volles Geld ohne bessere Prüfung. "
                f"Das schützt die Wirtschaft vor Scheinschleifen und bindet Inflation an Belege. Erzeugte Schuld: {debt:.2f}."
            )
        alternatives_en = (
            "Possible alternative outcomes: (1) higher verification infrastructure would turn the same movement into full VSG; "
            "(2) lower quality or justice would shrink ESV even with the same SG distance; "
            "(3) stronger pollution or material loss would create more CLD and could make the transaction net-negative."
        )
        alternatives_de = (
            "Mögliche alternative Ausgänge: (1) bessere Prüfinfrastruktur würde dieselbe Bewegung in volles VSG verwandeln; "
            "(2) niedrigere Qualität oder Gerechtigkeit würde den ESV trotz gleicher SG-Distanz senken; "
            "(3) stärkere Verschmutzung oder Materialverluste würden mehr CLD erzeugen und die Transaktion netto negativ machen."
        )
        return exp_en, exp_de, formula_en, formula_de, analysis_en, analysis_de, alternatives_en, alternatives_de

    def transform(self, tick: int, company: Company, ident: Identity, target_station: int, action: str,
                  amount: float, force_verify: bool = False) -> Optional[LedgerEntry]:
        if target_station > self.kind.cycle_length:
            return None
        amount = min(max(0.0001, amount), ident.mass)
        ident = self._split_identity(ident, amount)
        start = ident.station
        start_rep = ident.repetition
        raw, end_rep = transition_distance(self.kind.code, start, start_rep, target_station)
        qd, ud, loss, gain_unit, pd, tags = self._environment_modifiers(company, start, target_station)

        env_quality = 1.0 - self.pol * 0.22 + self.tec * 0.04 + self.inf * 0.035
        skill_factor = 0.92 + company.skill * 0.13 + company.efficiency * 0.07
        fairness_factor = ident.justice * 0.35 + company.fairness * 0.45 + self.jix * 0.20
        material_gain = amount * gain_unit * max(0.0, skill_factor)
        new_mass = max(0.0001, ident.mass * (1.0 - loss) + material_gain)
        ident.energy = max(0.0, ident.energy * (1.0 - loss * 0.65) + material_gain * self.hea * 0.6)
        ident.nutrients = max(0.0, ident.nutrients * (1.0 - loss * 0.45) + material_gain * self.sof * 0.7)
        ident.mass = new_mass
        ident.quality = clamp((ident.quality + qd) * env_quality * (0.96 + company.skill * 0.075), 0.03, 1.50)
        ident.use = clamp(ident.use + ud + company.efficiency * 0.035, 0.03, 1.50)
        ident.justice = clamp(fairness_factor, 0.02, 1.50)
        ident.station = target_station
        ident.repetition = end_rep
        ident.owner_id = company.company_id
        for tag in tags:
            if tag not in ident.tags:
                ident.tags.append(tag)
        ident.history.append(f"t{tick}:{action}:{start}->{target_station}/r{start_rep}->{end_rep}")
        if len(ident.history) > 36:
            ident.history = ident.history[-36:]

        mat = ident.mass
        qal = ident.quality
        use = ident.use
        jus = ident.justice
        esv = raw * mat * qal * use * jus
        verify_p = self._verification_probability(company)
        verified = force_verify or (self.rng.random() < verify_p)
        minted = esv if verified else 0.0
        usg = 0.0 if verified else esv
        tax = minted * self._tax_rate(company, target_station, action)
        requested_subsidy = self._subsidy(target_station, company, esv if verified else 0.0)
        subsidy = min(self.public_budget, requested_subsidy)
        self.public_budget -= subsidy
        self.public_budget += tax
        company.money += max(0.0, minted - tax) + subsidy
        company.sg_earned += minted + subsidy
        company.sg_unverified += usg
        company.taxes_paid += tax
        company.subsidies_received += subsidy
        company.actions_done += 1
        if verified:
            self.vsg_tick += minted
            self.money_supply += minted
            company.reputation = clamp(company.reputation + 0.004, 0.02, 1.5)
        else:
            self.usg_tick += usg
            company.reputation = clamp(company.reputation - 0.007, 0.02, 1.5)

        self.pol = clamp(self.pol + pd, 0.0, 2.0)
        debt_created = 0.0
        if pd > 0:
            debt_created += pd * 110.0 * (1.0 + self.pol)
        if qal < 0.40:
            debt_created += (0.40 - qal) * raw * mat * 0.35
        if jus < 0.45:
            debt_created += (0.45 - jus) * raw * mat * 0.25
        if company.segment_code in ("FUL", "FUV") and not verified:
            debt_created += usg * 0.10
        self.cld += debt_created
        company.debt += debt_created * 0.25

        # Direct environment effects after successful returns.
        if target_station in (17, 19, 5) and verified:
            self.sof = clamp(self.sof + min(0.012, 0.0008 * mat * qal), 0.02, 1.5)
            self.mic = clamp(self.mic + min(0.010, 0.0007 * mat), 0.02, 1.5)
        if target_station in (8, 9, 12) and verified:
            self.hlt = clamp(self.hlt + min(0.008, 0.0008 * mat * qal), 0.05, 1.5)
        if target_station == 21 and self.kind.code == "VulcanType":
            self.hea = clamp(self.hea + 0.002, 0.02, 1.5)
        if target_station == 22 and verified:
            self.sof = clamp(self.sof + 0.0015, 0.02, 1.5)

        outcome = "verified_regenerative" if verified and debt_created < esv * 0.03 else "verified_mixed" if verified else "unverified_claim"
        if debt_created > esv * 0.12:
            outcome = "debt_heavy"
        uke = raw / float(self.kind.cycle_length)
        exp_en, exp_de, formula_en, formula_de, analysis_en, analysis_de, alt_en, alt_de = self._make_explanations(
            company, ident, start, target_station, start_rep, end_rep, raw, uke, mat, qal, use, jus, esv,
            verified, tax, subsidy, debt_created, outcome
        )
        entry = LedgerEntry(
            tick=tick,
            universe=self.universe_name,
            system=self.system_name,
            planet=self.name,
            planet_type=self.kind.code,
            company_id=company.company_id,
            company_name=company.name,
            segment_code=company.segment_code,
            segment_span=company.segment_label(),
            partial_company=company.partial,
            action=action,
            identity_id=ident.identity_id,
            identity_label=ident.label,
            from_station=start,
            to_station=target_station,
            start_repetition=start_rep,
            end_repetition=end_rep,
            ncl=self.kind.cycle_length,
            raw_sg=raw,
            uke=uke,
            mat=mat,
            qal=qal,
            use=use,
            jus=jus,
            esv=esv,
            verified=verified,
            minted_sg=minted,
            usg=usg,
            tax=tax,
            subsidy=subsidy,
            debt_created=debt_created,
            outcome=outcome,
            explanation_en=exp_en,
            explanation_de=exp_de,
            formula_en=formula_en,
            formula_de=formula_de,
            analysis_en=analysis_en,
            analysis_de=analysis_de,
            alternatives_en=alt_en,
            alternatives_de=alt_de,
        )
        self.ledger.append(entry)
        return entry

    # ----------------------------- company action and markets -----------------------------

    def _create_missing_input(self, company: Company) -> Optional[Identity]:
        # Specialized companies can create or attract a small input only for natural source stations.
        owner = company.company_id
        if company.segment_start == 1:
            return self._create_identity("new_fecundation_identity", 1, self.rng.uniform(0.4, 1.6), owner,
                                         quality=self.sof, use=0.74, justice=company.fairness, tags=["origin", "seed"])
        if company.segment_start == 5 and self.stock_mass(5) < 3.0:
            return self._create_identity("purchased_fertilizer_mix", 5, self.rng.uniform(0.3, 1.3), owner,
                                         quality=self.sof * self.rng.uniform(0.85, 1.08), use=0.82,
                                         justice=company.fairness, tags=["fertilizer", "soil"])
        if company.segment_start == 13 and self.stock_mass(13) < 2.0 and self.stock_mass(12) > 0.5:
            ident = self._find_identity_at([12], 0.05)
            if ident:
                return ident
        if company.segment_start == 19 and self.stock_mass(19) < 2.0:
            return self._create_identity("new_soil_memory", 19, self.rng.uniform(0.3, 1.0), owner,
                                         quality=self.sof, use=0.90, justice=company.fairness, tags=["soil", "planet"])
        if company.segment_start == 20 and self.stock_mass(20) < 2.0:
            return self._create_identity("deep_heat_stream", 20, self.rng.uniform(0.3, 1.2), owner,
                                         quality=self.hea, use=0.62, energy=self.hea * 8.0, tags=["heat", "lava"])
        return None

    def _find_identity_at(self, stations: Sequence[int], min_mass: float) -> Optional[Identity]:
        candidates = [i for i in self.identities if i.station in stations and i.mass >= min_mass]
        if not candidates:
            return None
        candidates.sort(key=lambda i: i.mass * i.quality * i.use, reverse=True)
        top = candidates[:max(1, min(6, len(candidates)))]
        return self.rng.choice(top)

    def company_action(self, tick: int, company: Company) -> None:
        candidates = self._identity_candidates_for_company(company)
        if candidates:
            ident = candidates[0]
        else:
            ident = self._create_missing_input(company)
        if not ident:
            company.idle_ticks += 1
            return
        target = self._next_target_for_company(company, ident)
        if target == ident.station and company.segment_code not in ("FUL", "FUV"):
            company.idle_ticks += 1
            return
        amount = min(ident.mass, self.rng.uniform(0.10, 1.60) * company.efficiency)
        action = f"{company.segment_code}_service_{ident.station}_to_{target}"
        # Validators sometimes force verification of law/signal work; risky full-cycle firms never do.
        force = company.segment_code == "GOV" and self.rng.random() < 0.25
        self.transform(tick, company, ident, target, action, amount=amount, force_verify=force)

    def _local_market_turn(self, tick: int) -> None:
        # Move endpoint stock from seller companies to buyer companies whose segment starts there.
        buyers_by_start: Dict[int, List[Company]] = {}
        for c in self.companies:
            buyers_by_start.setdefault(c.segment_start, []).append(c)
        for ident in list(self.identities):
            if ident.mass < 0.08:
                continue
            buyers = buyers_by_start.get(ident.station, [])
            if not buyers:
                continue
            seller = next((c for c in self.companies if c.company_id == ident.owner_id), None)
            if seller and seller.segment_start == ident.station:
                continue
            if self.rng.random() > 0.20:
                continue
            buyer = self.rng.choice(buyers)
            price = self.price_for_station(ident.station) * ident.mass * ident.quality * ident.use
            trade_value = min(price, max(0.0, buyer.money * 0.22))
            if trade_value <= 0.01:
                continue
            buyer.money -= trade_value
            if seller:
                seller.money += trade_value
                seller.trades_done += 1
            else:
                self.public_budget += trade_value * 0.15
            ident.owner_id = buyer.company_id
            buyer.trades_done += 1
            self.local_trade_tick += trade_value
            self.trades.append(TradeRecord(tick, self.universe_name, self.system_name, self.name,
                                           seller.company_id if seller else "STATE", buyer.company_id,
                                           ident.identity_id, ident.station, ident.mass,
                                           safe_div(trade_value, ident.mass, 0.0), trade_value, "segment_handoff"))

    def _bank_credit_turn(self, tick: int) -> None:
        # A light credit layer: well-reputed partial companies can finance missing handoffs.
        if self.rng.random() > 0.16:
            return
        lenders = [c for c in self.companies if c.money > 180.0 and c.credit_score() > 0.70]
        borrowers = [c for c in self.companies if c.partial and c.money < 110.0 and c.credit_score() > 0.48]
        if not lenders or not borrowers:
            return
        lender = self.rng.choice(lenders)
        borrower = self.rng.choice(borrowers)
        principal = min(lender.money * 0.10, self.rng.uniform(18.0, 85.0) * borrower.credit_score())
        if principal <= 5.0:
            return
        lender.money -= principal * 0.10
        borrower.money += principal
        loan = Loan(self.next_loan_id(), lender.company_id, borrower.company_id,
                    principal, principal * (1.02 + borrower.risk * 0.05),
                    tick + self.rng.randint(8, 22), principal * (1.2 + borrower.skill))
        self.loans.append(loan)
        self.money_supply += principal * 0.90
        self.event_log.append(f"t{tick} {self.name}: credit {loan.loan_id} to {borrower.segment_code} {fmt(principal)}")

    def _settle_loans(self, tick: int) -> None:
        companies = {c.company_id: c for c in self.companies}
        for loan in self.loans:
            if loan.status != "active" or loan.due_tick > tick:
                continue
            borrower = companies.get(loan.borrower_id)
            lender = companies.get(loan.lender_id)
            if not borrower:
                loan.status = "default"
                continue
            recent_sg = borrower.sg_earned
            can_pay = borrower.money >= loan.outstanding * 0.65 or recent_sg >= loan.expected_sg * 0.55
            if can_pay:
                payment = min(borrower.money, loan.outstanding)
                borrower.money -= payment
                if lender:
                    lender.money += payment
                loan.status = "repaid"
                borrower.reputation = clamp(borrower.reputation + 0.015, 0.02, 1.5)
            else:
                default_debt = loan.outstanding * (0.35 + borrower.risk)
                borrower.debt += default_debt
                self.cld += default_debt * 0.25
                loan.status = "default"
                borrower.reputation = clamp(borrower.reputation - 0.06, 0.02, 1.5)

    # ----------------------------- environment and society -----------------------------

    def _environment_tick(self, tick: int) -> None:
        return_stock = self.stock_mass(17) + self.stock_mass(5)
        waste_stock = self.stock_mass(13) + self.stock_mass(18)
        soil_stock = self.stock_mass(19)
        self.sof = clamp(self.sof + 0.00055 * return_stock + 0.00018 * soil_stock - 0.00045 * waste_stock - 0.0019 * self.pol, 0.02, 1.5)
        self.mic = clamp(self.mic + 0.00038 * (waste_stock + return_stock) - 0.0012 * self.pol, 0.02, 1.5)
        self.wat = clamp(self.wat + self.rng.gauss(0.002, 0.009) - 0.0018 * self.pol, 0.02, 1.5)
        self.hea = clamp(self.hea + self.rng.gauss(0.0005, 0.0045) + (0.0008 if self.kind.code == "VulcanType" else 0.0), 0.02, 1.5)
        self.pol = clamp(self.pol * 0.993 - 0.0008 * self.inf + 0.00055 * waste_stock, 0.0, 2.0)

    def _population_tick(self, tick: int) -> None:
        need = self.population * 0.00235
        food_stock = self.stock_mass(8) + 0.45 * self.stock_mass(11) + 0.30 * self.stock_mass(7)
        if food_stock >= need:
            self.hlt = clamp(self.hlt + 0.0018 * min(1.0, food_stock / max(need, 0.01)), 0.05, 1.5)
            self.population *= 1.0 + 0.00042 * clamp(self.hlt - 0.73, 0.0, 0.6)
        else:
            shortage = 1.0 - safe_div(food_stock, need, 0.0)
            self.hlt = clamp(self.hlt - 0.009 * shortage, 0.05, 1.5)
            self.population *= 1.0 - 0.0009 * shortage
            hunger_debt = shortage * self.population * 0.085
            self.cld += hunger_debt
            self.public_budget -= min(self.public_budget, hunger_debt * 0.045)
            self.event_log.append(f"t{tick} {self.name}: food shortage created CLD {fmt(hunger_debt)}")

    def _event_tick(self, tick: int) -> None:
        roll = self.rng.random()
        if roll < 0.016:
            loss = self.rng.uniform(0.05, 0.18)
            self.wat = clamp(self.wat - loss, 0.02, 1.5)
            self.event_log.append(f"t{tick} {self.name}: water shock -{loss:.2f}")
        elif roll < 0.030:
            gain = self.rng.uniform(0.035, 0.13)
            self.mic = clamp(self.mic + gain, 0.02, 1.5)
            self.event_log.append(f"t{tick} {self.name}: microbe bloom +{gain:.2f}")
        elif roll < 0.045:
            gain = self.rng.uniform(0.04, 0.15)
            self.pol = clamp(self.pol + gain, 0.0, 2.0)
            self.cld += gain * 95.0
            self.event_log.append(f"t{tick} {self.name}: contamination +{gain:.2f}")
        elif roll < 0.060:
            gain = self.rng.uniform(0.018, 0.075)
            self.tec = clamp(self.tec + gain, 0.02, 1.5)
            self.event_log.append(f"t{tick} {self.name}: cycle technology +{gain:.2f}")
        elif self.kind.code == "VulcanType" and roll < 0.085:
            mass = self.rng.uniform(1.8, 8.5)
            self._create_identity("eruption_ash", 21, mass, f"STATE-{self.name}",
                                  quality=self.rng.uniform(0.55, 1.22), use=0.78,
                                  energy=mass * 1.8, tags=["ash", "volcanic", "mineral"])
            self.hea = clamp(self.hea + 0.028, 0.02, 1.5)
            self.pol = clamp(self.pol + 0.013, 0.0, 2.0)
            self.event_log.append(f"t{tick} {self.name}: volcanic eruption created {fmt(mass)} ash")

    def _price_and_policy_tick(self) -> None:
        output = max(1.0, self.vsg_tick + self.local_trade_tick * 0.20 + self.stock_mass(8) * 2.0 + self.stock_mass(17))
        debt_pressure = 1.0 + min(2.0, self.cld / max(1000.0, self.money_supply))
        money_pressure = self.money_supply / max(1000.0, output * 18.0)
        scarcity = 1.0 + 1.0 / max(1.0, self.stock_mass(8) + self.stock_mass(7) * 0.4)
        target_cpi = clamp(0.72 + 0.08 * money_pressure + 0.08 * debt_pressure + 0.05 * scarcity, 0.55, 2.8)
        self.cpi = clamp(self.cpi * 0.94 + target_cpi * 0.06, 0.45, 3.5)
        # Public basic provision: if budget exists, reduce the worst failure modes.
        if self.public_budget > 10.0 and (self.hlt < 0.62 or self.sof < 0.42 or self.inf < 0.42):
            spend = min(self.public_budget * 0.015, 12.0)
            self.public_budget -= spend
            self.hlt = clamp(self.hlt + spend * 0.0008, 0.05, 1.5)
            self.inf = clamp(self.inf + spend * 0.0005, 0.02, 1.5)
            self.sof = clamp(self.sof + spend * 0.00035, 0.02, 1.5)

    def _closed_loop_rate(self) -> float:
        recent = self.ledger[-120:]
        if not recent:
            return 0.0
        closed = 0
        for r in recent:
            if r.to_station in (5, 17, 19, 1, 2):
                closed += 1
        return closed / float(len(recent))

    def _material_stock_index(self) -> float:
        food = self.stock_mass(8) + self.stock_mass(7) * 0.3 + self.stock_mass(11) * 0.45
        waste = self.stock_mass(13) + self.stock_mass(18)
        returns = self.stock_mass(17) + self.stock_mass(5)
        soil = self.stock_mass(19)
        return clamp((food * 0.30 + returns * 0.35 + soil * 0.25 - waste * 0.18) / max(1.0, self.population * 0.01), -2.0, 5.0)

    def _take_snapshot(self, tick: int) -> None:
        partial_share = safe_div(sum(1 for c in self.companies if c.partial), len(self.companies), 0.0)
        snap = PlanetSnapshot(
            tick=tick,
            universe=self.universe_name,
            system=self.system_name,
            planet=self.name,
            planet_type=self.kind.code,
            population=self.population,
            hlt=self.hlt,
            sof=self.sof,
            wat=self.wat,
            mic=self.mic,
            hea=self.hea,
            pol=self.pol,
            jix=self.jix,
            inf=self.inf,
            tec=self.tec,
            cpi=self.cpi,
            money_supply=self.money_supply,
            public_budget=self.public_budget,
            cld=self.cld,
            vsg_tick=self.vsg_tick,
            usg_tick=self.usg_tick,
            local_trade_tick=self.local_trade_tick,
            interplanetary_trade_tick=self.interplanetary_trade_tick,
            clr=self._closed_loop_rate(),
            msi=self._material_stock_index(),
            food_stock=self.stock_mass(8) + self.stock_mass(7) * 0.3 + self.stock_mass(11) * 0.45,
            waste_stock=self.stock_mass(13) + self.stock_mass(18),
            return_stock=self.stock_mass(17) + self.stock_mass(5),
            soil_stock=self.stock_mass(19),
            partial_company_share=partial_share,
        )
        self.snapshots.append(snap)

    def _update_money_supply(self) -> None:
        self.money_supply = self.public_budget + sum(c.money for c in self.companies) + sum(l.outstanding for l in self.loans if l.status == "active") * 0.25

    def step(self, tick: int) -> None:
        self.vsg_tick = 0.0
        self.usg_tick = 0.0
        self.local_trade_tick = 0.0
        self.interplanetary_trade_tick = 0.0
        self._event_tick(tick)
        self._environment_tick(tick)
        # More actions than companies? No: a company usually acts at most once per tick, preserving specialization.
        order = list(self.companies)
        self.rng.shuffle(order)
        active_count = max(1, int(len(order) * self.rng.uniform(0.62, 0.92)))
        for company in order[:active_count]:
            self.company_action(tick, company)
        self._local_market_turn(tick)
        self._bank_credit_turn(tick)
        self._settle_loans(tick)
        self._population_tick(tick)
        self._price_and_policy_tick()
        self._update_money_supply()
        self._take_snapshot(tick)

    # ----------------------------- trade with other planets -----------------------------

    def export_identity(self, station_options: Sequence[int], max_mass: float) -> Optional[Identity]:
        ident = self._find_identity_at(station_options, 0.10)
        if not ident:
            return None
        return self._split_identity(ident, min(max_mass, ident.mass))

    def import_identity(self, ident: Identity) -> None:
        station = ident.station
        label = "imported_" + ident.label
        tags = list(ident.tags) + ["import"]
        if station > self.kind.cycle_length:
            station = 5
            label = "imported_mineral_fertilizer"
            if "fertilizer" not in tags:
                tags.append("fertilizer")
        new_ident = self._create_identity(label, station, ident.mass, f"STATE-{self.name}",
                                          quality=ident.quality * 0.98, use=ident.use, justice=ident.justice,
                                          energy=ident.energy, nutrients=ident.nutrients, tags=tags)
        new_ident.history.append(f"imported_from:{ident.identity_id}")

    def price_for_station(self, station: int) -> float:
        base = 1.0 + station / float(self.kind.cycle_length)
        scarcity = 1.0 + 1.0 / math.sqrt(max(0.06, self.stock_mass(station)))
        quality = max(0.22, self.avg_quality(station))
        debt = 1.0 + min(1.3, self.cld / max(4000.0, self.money_supply + 1.0))
        return base * scarcity * quality * debt * self.cpi

    # ----------------------------- summaries -----------------------------

    def top_companies(self, n: int = 6) -> List[Company]:
        return sorted(self.companies, key=lambda c: (c.sg_earned - c.debt, c.reputation, c.trades_done), reverse=True)[:n]

    def company_segment_counts(self) -> Dict[str, int]:
        d: Dict[str, int] = {}
        for c in self.companies:
            d[c.segment_code] = d.get(c.segment_code, 0) + 1
        return d

    def latest_snapshot(self) -> Optional[PlanetSnapshot]:
        return self.snapshots[-1] if self.snapshots else None

    def final_summary_dict(self) -> Dict[str, object]:
        return {
            "universe": self.universe_name,
            "system": self.system_name,
            "planet": self.name,
            "planet_type": self.kind.code,
            "cycle_length": self.kind.cycle_length,
            "population": self.population,
            "hlt": self.hlt,
            "sof": self.sof,
            "wat": self.wat,
            "mic": self.mic,
            "hea": self.hea,
            "pol": self.pol,
            "jix": self.jix,
            "inf": self.inf,
            "tec": self.tec,
            "cpi": self.cpi,
            "money_supply": self.money_supply,
            "public_budget": self.public_budget,
            "cld": self.cld,
            "clr": self._closed_loop_rate(),
            "msi": self._material_stock_index(),
            "companies": len(self.companies),
            "partial_company_share": safe_div(sum(1 for c in self.companies if c.partial), len(self.companies), 0.0),
            "identities": len(self.identities),
            "ledger_records": len(self.ledger),
            "trades": len(self.trades),
            "segment_counts": self.company_segment_counts(),
            "active_loans": len([l for l in self.loans if l.status == "active"]),
            "repaid_loans": len([l for l in self.loans if l.status == "repaid"]),
            "defaulted_loans": len([l for l in self.loans if l.status == "default"]),
            "station_masses": {str(k): self.stock_mass(k) for k in range(1, self.kind.cycle_length + 1)},
            "events": list(self.event_log[-12:]),
        }


# ---------------------------------------------------------------------------
# Star systems, universes and cosmos
# ---------------------------------------------------------------------------


class StarSystem:
    def __init__(self, universe_name: str, name: str, rng: random.Random,
                 planets_per_system: int, companies_per_planet: int) -> None:
        self.universe_name = universe_name
        self.name = name
        self.rng = rng
        self.planets: List[PlanetEconomy] = []
        self._create_planets(planets_per_system, companies_per_planet)

    def _create_planets(self, n: int, companies_per_planet: int) -> None:
        roots = ["Gaia", "Tellus", "Vesta", "Nysa", "Orion", "Centauri", "Solum", "Aster", "Pyra", "Luma", "Kora", "Rhea"]
        for i in range(n):
            kind = VULCAN_TYPE if self.rng.random() < 0.35 else EARTH_TYPE
            if i == 0 and self.rng.random() < 0.62:
                kind = EARTH_TYPE
            if i == n - 1 and self.rng.random() < 0.45:
                kind = VULCAN_TYPE
            planet_name = f"{self.rng.choice(roots)}-{self.name.split('-')[-1]}-{i}"
            self.planets.append(PlanetEconomy(self.universe_name, self.name, planet_name, kind, self.rng, companies_per_planet))

    def step(self, tick: int) -> None:
        for p in self.planets:
            p.step(tick)
        self._interplanetary_trade(tick)

    def _interplanetary_trade(self, tick: int) -> None:
        if len(self.planets) < 2:
            return
        buyers = list(self.planets)
        self.rng.shuffle(buyers)
        for buyer in buyers:
            food_need = buyer.population * 0.0030
            food_stock = buyer.stock_mass(8) + buyer.stock_mass(11) * 0.45 + buyer.stock_mass(7) * 0.30
            need = None
            export_options: Sequence[int] = []
            if food_stock < food_need:
                need = "food"
                export_options = [8, 11, 7]
            elif buyer.sof < 0.45 or buyer.stock_mass(13) + buyer.stock_mass(18) > 35.0:
                need = "fertility"
                export_options = [5, 17, 19, 22, 21]
            elif buyer.kind.code == "EarthType" and buyer.rng.random() < 0.025:
                need = "mineral"
                export_options = [21, 22, 5]
            if not need:
                continue
            sellers = [p for p in self.planets if p is not buyer]
            self.rng.shuffle(sellers)
            for seller in sellers:
                if need == "food" and seller.stock_mass(8) + seller.stock_mass(11) * 0.45 + seller.stock_mass(7) * 0.30 < seller.population * 0.0035:
                    continue
                if need == "fertility" and seller.stock_mass(5) + seller.stock_mass(17) + seller.stock_mass(22) < 2.5:
                    continue
                if need == "mineral" and seller.kind.code != "VulcanType":
                    continue
                exported = seller.export_identity(export_options, max_mass=self.rng.uniform(0.2, 1.7))
                if not exported:
                    continue
                target_station = min(exported.station, buyer.kind.cycle_length)
                price = (seller.price_for_station(exported.station) + buyer.price_for_station(target_station)) / 2.0
                uke_factor = seller.kind.cycle_length / float(buyer.kind.cycle_length)
                trade_value = exported.mass * price * exported.quality * exported.use / max(0.65, uke_factor)
                buyer.import_identity(exported)
                buyer.interplanetary_trade_tick += trade_value
                seller.interplanetary_trade_tick += trade_value
                buyer.public_budget -= min(buyer.public_budget * 0.04, trade_value * 0.025)
                seller.public_budget += trade_value * 0.025
                buyer.event_log.append(f"t{tick} {buyer.name}: interplanetary import {need} from {seller.name}, value {fmt(trade_value)}")
                seller.event_log.append(f"t{tick} {seller.name}: interplanetary export {need} to {buyer.name}, value {fmt(trade_value)}")
                break

    def all_planets(self) -> List[PlanetEconomy]:
        return list(self.planets)


class Universe:
    def __init__(self, name: str, rng: random.Random, systems: int,
                 planets_per_system: int, companies_per_planet: int) -> None:
        self.name = name
        self.rng = rng
        self.systems = [StarSystem(name, f"System-{i}", rng, planets_per_system, companies_per_planet) for i in range(systems)]
        self.age = 0
        self.cosmic_events: List[str] = []

    def step(self, tick: int) -> None:
        self.age = tick
        self._cosmic_event(tick)
        for system in self.systems:
            system.step(tick)

    def _cosmic_event(self, tick: int) -> None:
        planets = self.all_planets()
        if not planets:
            return
        roll = self.rng.random()
        if roll < 0.010:
            for p in planets:
                p.jix = clamp(p.jix + 0.007, 0.02, 1.5)
                p.tec = clamp(p.tec + 0.004, 0.02, 1.5)
            self.cosmic_events.append(f"t{tick} {self.name}: cosmic signal strengthened UKE law and communication")
        elif roll < 0.018:
            p = self.rng.choice(planets)
            p.pol = clamp(p.pol + 0.08, 0.0, 2.0)
            p.hlt = clamp(p.hlt - 0.025, 0.05, 1.5)
            p.cld += 80.0
            self.cosmic_events.append(f"t{tick} {self.name}: radiation event hit {p.name}")
        elif roll < 0.026:
            for p in planets:
                p.policy.verification_strictness = clamp(p.policy.verification_strictness + 0.006, 0.20, 0.95)
                p.inf = clamp(p.inf + 0.003, 0.02, 1.5)
            self.cosmic_events.append(f"t{tick} {self.name}: interplanetary chamber harmonized verification")

    def run(self, ticks: int, progress: bool = False) -> None:
        for tick in range(1, ticks + 1):
            self.step(tick)
            if progress and (tick == 1 or tick % max(1, ticks // 10) == 0):
                print(f"[progress] {self.name}: tick {tick}/{ticks}")

    def all_planets(self) -> List[PlanetEconomy]:
        planets: List[PlanetEconomy] = []
        for s in self.systems:
            planets.extend(s.all_planets())
        return planets

    def summary(self) -> Dict[str, object]:
        planets = self.all_planets()
        return {
            "universe": self.name,
            "age": self.age,
            "systems": len(self.systems),
            "planets": len(planets),
            "earth_type_planets": sum(1 for p in planets if p.kind.code == "EarthType"),
            "vulcan_type_planets": sum(1 for p in planets if p.kind.code == "VulcanType"),
            "population": sum(p.population for p in planets),
            "money_supply": sum(p.money_supply for p in planets),
            "public_budget": sum(p.public_budget for p in planets),
            "cld": sum(p.cld for p in planets),
            "vsg_total": sum(r.minted_sg for p in planets for r in p.ledger),
            "usg_total": sum(r.usg for p in planets for r in p.ledger),
            "partial_company_share": safe_div(sum(1 for p in planets for c in p.companies if c.partial), sum(len(p.companies) for p in planets), 0.0),
            "cosmic_events": list(self.cosmic_events[-16:]),
        }


class Cosmos:
    def __init__(self, seed: int, universes: int, systems: int,
                 planets_per_system: int, companies_per_planet: int) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.universes: List[Universe] = []
        for i in range(universes):
            rng = random.Random(self.rng.randint(1, 10**12))
            self.universes.append(Universe(f"Universe-{i}", rng, systems, planets_per_system, companies_per_planet))

    def run(self, ticks: int, progress: bool = False) -> None:
        for u in self.universes:
            u.run(ticks, progress=progress)
        self._inter_universe_resonance(ticks)

    def _inter_universe_resonance(self, ticks: int) -> None:
        if len(self.universes) < 2:
            return
        ranked = sorted(self.universes, key=lambda u: u.summary()["cld"])
        best = ranked[0]
        worst = ranked[-1]
        best_tech = mean([p.tec for p in best.all_planets()], 0.0)
        for p in worst.all_planets():
            p.tec = clamp(p.tec + best_tech * 0.002, 0.02, 1.5)
            p.jix = clamp(p.jix + 0.001, 0.02, 1.5)
        worst.cosmic_events.append(f"t{ticks} cosmic resonance: learning signal from {best.name}")

    def all_planets(self) -> List[PlanetEconomy]:
        planets: List[PlanetEconomy] = []
        for u in self.universes:
            planets.extend(u.all_planets())
        return planets

    def summary(self) -> Dict[str, object]:
        us = [u.summary() for u in self.universes]
        return {
            "seed": self.seed,
            "universes": len(self.universes),
            "total_planets": sum(u["planets"] for u in us),
            "total_population": sum(u["population"] for u in us),
            "total_money_supply": sum(u["money_supply"] for u in us),
            "total_public_budget": sum(u["public_budget"] for u in us),
            "total_cld": sum(u["cld"] for u in us),
            "total_vsg": sum(u["vsg_total"] for u in us),
            "total_usg": sum(u["usg_total"] for u in us),
            "partial_company_share": safe_div(sum(u["partial_company_share"] * u["planets"] for u in us), max(1, sum(u["planets"] for u in us)), 0.0),
            "universes_detail": us,
        }


# ---------------------------------------------------------------------------
# Report rendering
# ---------------------------------------------------------------------------


def evaluation_paragraph(lang: str, subject: str) -> str:
    if lang == "de":
        return (
            f"**Was hier simuliert wird und warum:** Diese Auswertung betrachtet {subject}. "
            "Sie ist bewusst nicht nur eine Zahlentabelle: Die Universum-Kreislaufwirtschaft erzeugt Geld aus nachweisbaren Transformationen, "
            "deshalb muss jede Auswertung zeigen, welche Kreislaufstrecke, welche Materialqualität, welcher Nutzen, welche Gerechtigkeit und welche Schuld entstanden sind. "
            "Besonders wichtig ist, ob Teilzyklus-Unternehmen sauber aneinander übergeben oder ob offene Schleifen als Kreislaufschuld hängen bleiben."
        )
    return (
        f"**What is simulated here and why:** This evaluation examines {subject}. "
        "It is deliberately more than a number table: the Universe Circular Economy creates money from verified transformations, "
        "so every evaluation must show which cycle distance, material quality, usefulness, justice and debt were produced. "
        "The key question is whether partial-cycle companies hand identities off cleanly or leave open loops as cycle debt."
    )


def outcome_text(lang: str, good: bool, medium: bool) -> str:
    if lang == "de":
        if good:
            return "regenerativ: Die Simulation erzeugte mehr verifizierte Rückführung als offene Schuld."
        if medium:
            return "gemischt: Die Simulation erzeugte produktive SG-Werte, aber auch sichtbare Kreislaufschuld."
        return "angespannt: Die Simulation zeigt, dass Schulden, Mangel oder Verschmutzung die Kreisläufe dominieren."
    if good:
        return "regenerative: the run produced more verified return than open debt."
    if medium:
        return "mixed: the run produced useful SG values but also visible cycle debt."
    return "strained: debt, shortage or pollution dominated the cycle."


def render_markdown_report(cosmos: Cosmos, lang: str = "en", explain_limit: int = 20) -> str:
    summary = cosmos.summary()
    lines: List[str] = []
    title = text(lang, "# Universe Circular Economy — Simulation Report v2", "# Universum-Kreislaufwirtschaft — Simulationsbericht v2")
    lines.append(title)
    lines.append("")
    lines.append(text(
        lang,
        "This report is colorful on purpose: each multi-letter abbreviation receives its own color, because the simulation has many interacting variables and the color badges make repeated formulas readable.",
        "Dieser Bericht ist absichtlich bunt: Jedes mehrbuchstabige Kürzel erhält eine eigene Farbe, weil die Simulation viele gekoppelte Variablen besitzt und die Farbbadges die wiederholten Formeln lesbar machen."
    ))
    lines.append("")
    lines.append("## " + text(lang, "Color-coded abbreviation legend", "Farbige Kürzel-Legende"))
    lines.append(evaluation_paragraph(lang, text(lang, "the vocabulary of the simulation", "das Vokabular der Simulation")))
    lines.append("")
    lines.append(abbreviations_markdown(lang))
    lines.append("")

    lines.append("## " + text(lang, "Core formulas", "Kernformeln"))
    lines.append(evaluation_paragraph(lang, text(lang, "the money calculation itself", "die Geldrechnung selbst")))
    lines.append("")
    lines.append("```text")
    lines.append("SG_raw = (REP_end - REP_start) * NCL + END - STA")
    lines.append("UKE = SG_raw / NCL")
    lines.append("ESV = SG_raw * MAT * QAL * USE * JUS")
    lines.append("VSG = ESV if verified else 0")
    lines.append("USG = ESV if not verified else 0")
    lines.append("CLD = damage/open-loop cost")
    lines.append("NCL(EarthType)=20, NCL(VulcanType)=22")
    lines.append("```")
    lines.append("")
    lines.append(text(
        lang,
        f"Example check: EarthType start 4 to end 17 in pass 4 gives `{original_loop_value('EarthType', 4, 17, 4)}` SG. VulcanType gives `{original_loop_value('VulcanType', 4, 17, 4)}` SG.",
        f"Beispielprüfung: Erde-Typ Start 4 bis Ende 17 im Umlauf 4 ergibt `{original_loop_value('EarthType', 4, 17, 4)}` SG. Vulkan-Typ ergibt `{original_loop_value('VulcanType', 4, 17, 4)}` SG."
    ))
    lines.append("")

    lines.append("## " + text(lang, "Company segment economy", "Unternehmens-Segmentwirtschaft"))
    lines.append(evaluation_paragraph(lang, text(lang, "the new rule that most companies only operate part of the cycle", "die neue Regel, dass die meisten Unternehmen nur einen Teil des Kreislaufs übernehmen")))
    lines.append("")
    lines.append(text(
        lang,
        "Most companies are deliberately partial-cycle firms. They do not own the whole universe loop; they own a license such as 5→7 or 15→19, transform identities inside that segment, and sell or hand off the resulting endpoint stock to the next company. Rare integrators close longer loops.",
        "Die meisten Unternehmen sind absichtlich Teilzyklus-Firmen. Sie besitzen nicht die ganze Universums-Schleife, sondern eine Lizenz wie 5→7 oder 15→19, transformieren Identitäten in diesem Abschnitt und verkaufen oder übergeben den Endpunktbestand an die nächste Firma. Seltene Integratoren schließen längere Schleifen."
    ))
    lines.append("")
    lines.append("| " + text(lang, "Code", "Code") + " | " + text(lang, "Span", "Spanne") + " | " + text(lang, "Meaning", "Bedeutung") + " | " + text(lang, "Partial?", "Teilzyklus?") + " |")
    lines.append("|---|---:|---|---|")
    for seg in SEGMENTS:
        if seg.code in ("FUV", "VUL", "MIN"):
            scope = "Vulcan"
        elif seg.code in ("FUL", "GEO"):
            scope = "Earth" if seg.planet_scope == "EarthType" else "Any"
        else:
            scope = "Any"
        lines.append(f"| {seg_badge(seg.code)} | `{seg.start}→{seg.end}` | {text(lang, seg.label_en, seg.label_de)} ({scope}) | {text(lang, 'yes', 'ja') if seg.partial else text(lang, 'rare integrator', 'seltener Integrator')} |")
    lines.append("")

    lines.append("## " + text(lang, "Cosmos evaluation", "Kosmos-Auswertung"))
    lines.append(evaluation_paragraph(lang, text(lang, "the whole universe/cosmos run", "den gesamten Universum-/Kosmos-Lauf")))
    lines.append("")
    lines.append("| Metric | Value |")
    lines.append("|---|---:|")
    metrics = [
        ("Seed", summary["seed"]),
        (text(lang, "Universes", "Universen"), summary["universes"]),
        (text(lang, "Planets", "Planeten"), summary["total_planets"]),
        (text(lang, "Population", "Bevölkerung"), fmt(summary["total_population"])),
        (badge("VSG") + " total", fmt(summary["total_vsg"])),
        (badge("USG") + " total", fmt(summary["total_usg"])),
        (badge("CLD") + " total", fmt(summary["total_cld"])),
        (text(lang, "Partial company share", "Anteil Teilzyklus-Unternehmen"), f"{summary['partial_company_share']:.2%}"),
        (text(lang, "Money supply", "Geldmenge"), fmt(summary["total_money_supply"])),
    ]
    for k, v in metrics:
        lines.append(f"| {k} | `{v}` |")
    lines.append("")
    good = summary["total_vsg"] > summary["total_cld"] * 2.0
    medium = summary["total_vsg"] > summary["total_cld"] * 0.65
    lines.append("**" + text(lang, "Detailed result evaluation", "Ausführliche Ergebnis-Auswertung") + ":** " + outcome_text(lang, good, medium))
    lines.append(" " + text(
        lang,
        "Several outcomes were possible: strong VSG with low CLD means stable regeneration; high USG means the economy physically moved material but lacked verification; high CLD means open loops, pollution or food shortages dominated.",
        "Mehrere Ausgänge waren möglich: starkes VSG bei niedriger CLD bedeutet stabile Regeneration; hohes USG bedeutet physische Materialbewegung ohne ausreichende Prüfung; hohe CLD bedeutet, dass offene Schleifen, Verschmutzung oder Nahrungsknappheit dominierten."
    ))
    lines.append("")

    lines.append("## " + text(lang, "Universe evaluations", "Universums-Auswertungen"))
    for u in cosmos.universes:
        us = u.summary()
        lines.append(f"### {u.name}")
        lines.append(evaluation_paragraph(lang, text(lang, f"universe {u.name} and its star systems", f"Universum {u.name} und seine Sternsysteme")))
        lines.append("")
        lines.append("| Metric | Value |")
        lines.append("|---|---:|")
        for k, v in [
            (text(lang, "Systems", "Systeme"), us["systems"]),
            (text(lang, "Planets", "Planeten"), us["planets"]),
            ("EarthType", us["earth_type_planets"]),
            ("VulcanType", us["vulcan_type_planets"]),
            (badge("VSG"), fmt(us["vsg_total"])),
            (badge("USG"), fmt(us["usg_total"])),
            (badge("CLD"), fmt(us["cld"])),
            (text(lang, "Partial company share", "Anteil Teilzyklus-Unternehmen"), f"{us['partial_company_share']:.2%}"),
        ]:
            lines.append(f"| {k} | `{v}` |")
        lines.append("")
        lines.append(text(
            lang,
            "The universe score shows whether specialized companies can still behave like one larger organism. If segment handoffs fail, USG and CLD rise even when many companies are active.",
            "Der Universumswert zeigt, ob spezialisierte Firmen trotzdem wie ein größerer Organismus handeln können. Wenn Segmentübergaben scheitern, steigen USG und CLD auch bei vielen aktiven Firmen."
        ))
        lines.append("")

    lines.append("## " + text(lang, "Planet evaluations", "Planeten-Auswertungen"))
    for p in cosmos.all_planets():
        snap = p.latest_snapshot()
        if not snap:
            continue
        lines.append(f"### {p.name} — {text(lang, p.kind.label_en, p.kind.label_de)} `{p.kind.cycle_length}`")
        lines.append(evaluation_paragraph(lang, text(lang, f"planet {p.name}, its environment, company segments and money/debt balance", f"Planet {p.name}, seine Umwelt, Unternehmenssegmente und Geld-/Schuldbilanz")))
        lines.append("")
        lines.append(abbreviations_markdown(lang, ["NCL", "HLT", "SOF", "WAT", "MIC", "HEA", "POL", "JIX", "INF", "TEC", "CPI", "CLR", "MSI", "VSG", "USG", "CLD", "SEG"]))
        lines.append("")
        lines.append("| Metric | Value | Metric | Value |")
        lines.append("|---|---:|---|---:|")
        rows = [
            (badge("NCL"), p.kind.cycle_length, badge("HLT"), f"{snap.hlt:.3f}"),
            (badge("SOF"), f"{snap.sof:.3f}", badge("WAT"), f"{snap.wat:.3f}"),
            (badge("MIC"), f"{snap.mic:.3f}", badge("HEA"), f"{snap.hea:.3f}"),
            (badge("POL"), f"{snap.pol:.3f}", badge("JIX"), f"{snap.jix:.3f}"),
            (badge("INF"), f"{snap.inf:.3f}", badge("TEC"), f"{snap.tec:.3f}"),
            (badge("CPI"), f"{snap.cpi:.3f}", badge("CLR"), f"{snap.clr:.3f}"),
            (badge("MSI"), f"{snap.msi:.3f}", badge("CLD"), fmt(snap.cld)),
            (badge("VSG"), fmt(sum(r.minted_sg for r in p.ledger)), badge("USG"), fmt(sum(r.usg for r in p.ledger))),
            (text(lang, "Partial companies", "Teilzyklus-Unternehmen"), f"{snap.partial_company_share:.2%}", text(lang, "Identities", "Identitäten"), len(p.identities)),
        ]
        for a, b, c, d in rows:
            lines.append(f"| {a} | `{b}` | {c} | `{d}` |")
        lines.append("")
        # Segment counts table.
        lines.append("| " + text(lang, "Segment", "Segment") + " | " + text(lang, "Companies", "Unternehmen") + " | " + text(lang, "Meaning", "Bedeutung") + " |")
        lines.append("|---|---:|---|")
        seg_map = {s.code: s for s in SEGMENTS}
        for code, count in sorted(p.company_segment_counts().items()):
            seg = seg_map.get(code)
            label = text(lang, seg.label_en, seg.label_de) if seg else code
            span = f"{seg.start}→{seg.end}" if seg else "?"
            lines.append(f"| {seg_badge(code)} `{span}` | `{count}` | {label} |")
        lines.append("")
        planet_good = (sum(r.minted_sg for r in p.ledger) > p.cld * 1.5 and p.pol < 0.35 and p._closed_loop_rate() > 0.22)
        planet_medium = (sum(r.minted_sg for r in p.ledger) > p.cld * 0.45 and p.hlt > 0.45)
        lines.append("**" + text(lang, "Detailed result evaluation", "Ausführliche Ergebnis-Auswertung") + ":** " + outcome_text(lang, planet_good, planet_medium))
        lines.append(" " + text(
            lang,
            "The planet can end in several regimes: a regenerative regime if return firms and soil firms dominate; a throughput regime if harvest and food companies produce SG but return lags; or a debt regime if pollution, hunger and unverifiable claims rise. The table above shows which regime emerged from this run.",
            "Der Planet kann in mehreren Regimen enden: regenerativ, wenn Rückführungs- und Bodenfirmen dominieren; Durchsatzregime, wenn Ernte- und Nahrungsfirmen SG erzeugen, aber Rückführung nachhinkt; Schuldregime, wenn Verschmutzung, Hunger und unverifizierte Ansprüche steigen. Die Tabelle zeigt, welches Regime in diesem Lauf entstand."
        ))
        lines.append("")

    lines.append("## " + text(lang, "Top company evaluations", "Top-Unternehmens-Auswertungen"))
    for p in cosmos.all_planets():
        lines.append(f"### {p.name}")
        lines.append(evaluation_paragraph(lang, text(lang, f"the strongest companies on {p.name}", f"die stärksten Unternehmen auf {p.name}")))
        lines.append("")
        lines.append("| Rank | Company | Segment | Partial | Role | SG earned | Money | Debt | Fairness | Reputation | Trades |")
        lines.append("|---:|---|---|---|---|---:|---:|---:|---:|---:|---:|")
        for idx, c in enumerate(p.top_companies(7), 1):
            lines.append(f"| {idx} | {c.name} | {seg_badge(c.segment_code)} `{c.segment_label()}` | {c.partial} | {text(lang, c.role_en, c.role_de)} | {fmt(c.sg_earned)} | {fmt(c.money)} | {fmt(c.debt)} | {c.fairness:.2f} | {c.reputation:.2f} | {c.trades_done} |")
        lines.append("")
        lines.append(text(
            lang,
            "A high-ranking company is not necessarily a full-cycle company. In this model, a narrow segment company can win when it produces verified handoffs, avoids CLD and keeps justice high.",
            "Ein hochrangiges Unternehmen ist nicht zwingend eine Vollkreislauffirma. In diesem Modell kann eine enge Segmentfirma gewinnen, wenn sie verifizierte Übergaben erzeugt, CLD vermeidet und Gerechtigkeit hoch hält."
        ))
        lines.append("")

    lines.append("## " + text(lang, "Detailed calculation evaluations", "Detaillierte Rechnungs-Auswertungen"))
    all_entries: List[LedgerEntry] = []
    for p in cosmos.all_planets():
        all_entries.extend(p.ledger[-max(3, explain_limit // max(1, len(cosmos.all_planets()))):])
    # Also include a few high-value entries to show alternative outcomes.
    high_value = sorted([r for p in cosmos.all_planets() for r in p.ledger], key=lambda r: r.esv, reverse=True)[:max(4, explain_limit // 3)]
    combined: List[LedgerEntry] = []
    seen = set()
    for r in high_value + all_entries:
        key = (r.tick, r.identity_id, r.company_id, r.from_station, r.to_station)
        if key not in seen:
            seen.add(key)
            combined.append(r)
        if len(combined) >= explain_limit:
            break
    lines.append(evaluation_paragraph(lang, text(lang, "individual SG calculations from the ledger", "einzelne SG-Rechnungen aus dem Hauptbuch")))
    lines.append("")
    lines.append(abbreviations_markdown(lang, ["SG", "UKE", "NCL", "STA", "END", "REP", "MAT", "QAL", "USE", "JUS", "ESV", "VSG", "USG", "TAX", "SUB", "CLD", "SEG"]))
    lines.append("")
    for idx, r in enumerate(combined, 1):
        lines.append(f"### {text(lang, 'Calculation', 'Rechnung')} {idx}: `{r.company_name}` — {seg_badge(r.segment_code)} `{r.segment_span}`")
        lines.append(text(lang, r.explanation_en, r.explanation_de))
        lines.append("")
        lines.append("**" + text(lang, "Formula", "Formel") + "**")
        lines.append("")
        lines.append(text(lang, r.formula_en, r.formula_de))
        lines.append("")
        lines.append("| Field | Value | Field | Value |")
        lines.append("|---|---:|---|---:|")
        fields = [
            (badge("STA"), r.from_station, badge("END"), r.to_station),
            (badge("REP") + " start", r.start_repetition, badge("REP") + " end", r.end_repetition),
            (badge("NCL"), r.ncl, badge("SG"), f"{r.raw_sg:.3f}"),
            (badge("UKE"), f"{r.uke:.4f}", badge("MAT"), f"{r.mat:.3f}"),
            (badge("QAL"), f"{r.qal:.3f}", badge("USE"), f"{r.use:.3f}"),
            (badge("JUS"), f"{r.jus:.3f}", badge("ESV"), f"{r.esv:.3f}"),
            (badge("VSG"), f"{r.minted_sg:.3f}", badge("USG"), f"{r.usg:.3f}"),
            (badge("TAX"), f"{r.tax:.3f}", badge("SUB"), f"{r.subsidy:.3f}"),
            (badge("CLD"), f"{r.debt_created:.3f}", text(lang, "Outcome", "Ausgang"), r.outcome),
        ]
        for a, b, c, d in fields:
            lines.append(f"| {a} | `{b}` | {c} | `{d}` |")
        lines.append("")
        lines.append("**" + text(lang, "Detailed result evaluation", "Ausführliche Ergebnis-Auswertung") + ":** " + text(lang, r.analysis_en, r.analysis_de))
        lines.append("")
        lines.append("**" + text(lang, "Multiple possible outcomes", "Mehrere mögliche Ausgänge") + ":** " + text(lang, r.alternatives_en, r.alternatives_de))
        lines.append("")

    lines.append("## " + text(lang, "Station alphabet", "Stationsalphabet"))
    lines.append(evaluation_paragraph(lang, text(lang, "the symbolic alphabet used by the simulation", "das symbolische Alphabet der Simulation")))
    lines.append("")
    lines.append("| No. | Letter | Form | Name | Domain | Description |")
    lines.append("|---:|---|---|---|---|---|")
    for i in range(1, 23):
        s = STATIONS[i]
        lines.append(f"| {s.no} | {s.letter} | {text(lang, s.form_en, s.form_de)} | {text(lang, s.name_en, s.name_de)} | {s.domain} | {text(lang, s.description_en, s.description_de)} |")
    lines.append("")

    lines.append("## " + text(lang, "Recent events", "Jüngste Ereignisse"))
    lines.append(evaluation_paragraph(lang, text(lang, "random shocks, credits, imports and cosmic signals", "zufällige Schocks, Kredite, Importe und kosmische Signale")))
    lines.append("")
    for u in cosmos.universes:
        for ev in u.cosmic_events[-10:]:
            lines.append(f"- {ev}")
    for p in cosmos.all_planets():
        for ev in p.event_log[-6:]:
            lines.append(f"- {ev}")
    lines.append("")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Output writers
# ---------------------------------------------------------------------------


def write_csv(path: Path, rows: Iterable[Dict[str, object]], fieldnames: Sequence[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def write_reports(cosmos: Cosmos, report_dir: Path, lang: str, explain_limit: int) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    snapshots: List[Dict[str, object]] = []
    ledger: List[Dict[str, object]] = []
    companies: List[Dict[str, object]] = []
    trades: List[Dict[str, object]] = []
    identities: List[Dict[str, object]] = []
    for p in cosmos.all_planets():
        for s in p.snapshots:
            snapshots.append(asdict(s))
        for r in p.ledger:
            ledger.append(asdict(r))
        for c in p.companies:
            d = asdict(c)
            d.update({"universe": p.universe_name, "system": p.system_name, "planet_type": p.kind.code})
            companies.append(d)
        for t in p.trades:
            trades.append(asdict(t))
        for ident in sorted(p.identities, key=lambda x: x.mass, reverse=True)[:40]:
            d = ident.passport()
            d.update({"universe": p.universe_name, "system": p.system_name, "planet": p.name})
            identities.append(d)
    if snapshots:
        write_csv(report_dir / "snapshots.csv", snapshots, list(snapshots[0].keys()))
    if ledger:
        write_csv(report_dir / "ledger.csv", ledger, list(ledger[0].keys()))
    if companies:
        write_csv(report_dir / "companies.csv", companies, list(companies[0].keys()))
    if trades:
        write_csv(report_dir / "trades.csv", trades, list(trades[0].keys()))
    if identities:
        write_csv(report_dir / "identity_samples.csv", identities, list(identities[0].keys()))
    with (report_dir / "final_state.json").open("w", encoding="utf-8") as f:
        json.dump({
            "cosmos": cosmos.summary(),
            "planets": [p.final_summary_dict() for p in cosmos.all_planets()],
        }, f, ensure_ascii=False, indent=2)
    with (report_dir / "final_report.md").open("w", encoding="utf-8") as f:
        f.write(render_markdown_report(cosmos, lang=lang, explain_limit=explain_limit))


# ---------------------------------------------------------------------------
# Console output
# ---------------------------------------------------------------------------


def print_console_summary(cosmos: Cosmos, lang: str, color: bool = True) -> None:
    s = cosmos.summary()
    print("\n" + ("=" * 72))
    print(text(lang, "Universe Circular Economy Simulation v2", "Universum-Kreislaufwirtschaft Simulation v2"))
    print("=" * 72)
    print(f"Seed: {s['seed']} | {text(lang, 'Universes', 'Universen')}: {s['universes']} | {text(lang, 'Planets', 'Planeten')}: {s['total_planets']}")
    print(f"{ansi('VSG', 'VSG', color)}: {fmt(s['total_vsg'])} | {ansi('USG', 'USG', color)}: {fmt(s['total_usg'])} | {ansi('CLD', 'CLD', color)}: {fmt(s['total_cld'])}")
    print(f"{text(lang, 'Partial company share', 'Anteil Teilzyklus-Unternehmen')}: {s['partial_company_share']:.2%}")
    print(text(lang, "\nPlanets:", "\nPlaneten:"))
    for p in cosmos.all_planets():
        vsg = sum(r.minted_sg for r in p.ledger)
        usg = sum(r.usg for r in p.ledger)
        print(
            f"- {p.name:14s} {p.kind.code:10s} {ansi('NCL','NCL',color)}={p.kind.cycle_length:2d} "
            f"{ansi('HLT','HLT',color)}={p.hlt:.2f} {ansi('SOF','SOF',color)}={p.sof:.2f} {ansi('WAT','WAT',color)}={p.wat:.2f} "
            f"{ansi('POL','POL',color)}={p.pol:.2f} {ansi('CPI','CPI',color)}={p.cpi:.2f} "
            f"{ansi('VSG','VSG',color)}={fmt(vsg):>8s} {ansi('USG','USG',color)}={fmt(usg):>8s} {ansi('CLD','CLD',color)}={fmt(p.cld):>8s} "
            f"{ansi('SEG','SEG',color)}={safe_div(sum(1 for c in p.companies if c.partial), len(p.companies), 0.0):.1%}"
        )
    print("\n" + text(lang, "Formula checks:", "Formelprüfungen:"))
    print(f"EarthType 4→17 pass 4 = {original_loop_value('EarthType', 4, 17, 4)} SG")
    print(f"VulcanType 4→17 pass 4 = {original_loop_value('VulcanType', 4, 17, 4)} SG")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PyPy3 simulation of the Universe Circular Economy with partial-cycle companies, colorful explanations and EN/DE reports."
    )
    parser.add_argument("--seed", type=int, default=73, help="Random seed for reproducibility.")
    parser.add_argument("--ticks", type=int, default=80, help="Number of simulation ticks.")
    parser.add_argument("--universes", type=int, default=1, help="Number of universes in the cosmos.")
    parser.add_argument("--systems", type=int, default=2, help="Star systems per universe.")
    parser.add_argument("--planets-per-system", type=int, default=3, help="Planets per star system.")
    parser.add_argument("--companies-per-planet", type=int, default=55, help="Companies per planet; most will be partial-cycle companies.")
    parser.add_argument("--lang", choices=["en", "de"], default="en", help="Report/console language. Default is English.")
    parser.add_argument("--report-dir", type=str, default="uce_report_v2", help="Directory for CSV/JSON/Markdown reports. Empty string disables files.")
    parser.add_argument("--explain-limit", type=int, default=24, help="How many individual ledger calculations receive detailed explanations in final_report.md.")
    parser.add_argument("--progress", action="store_true", help="Print progress while running.")
    parser.add_argument("--no-files", action="store_true", help="Do not write report files.")
    parser.add_argument("--no-color", action="store_true", help="Disable ANSI colors in console output.")
    return parser.parse_args(argv)


def validate_args(args: argparse.Namespace) -> Optional[str]:
    if args.ticks < 1:
        return "ticks must be >= 1"
    if args.universes < 1 or args.systems < 1 or args.planets_per_system < 1 or args.companies_per_planet < 1:
        return "universes/systems/planets/companies must be >= 1"
    if args.explain_limit < 1:
        return "explain-limit must be >= 1"
    return None


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    err = validate_args(args)
    if err:
        print(err, file=sys.stderr)
        return 2
    cosmos = Cosmos(
        seed=args.seed,
        universes=args.universes,
        systems=args.systems,
        planets_per_system=args.planets_per_system,
        companies_per_planet=args.companies_per_planet,
    )
    cosmos.run(args.ticks, progress=args.progress)
    print_console_summary(cosmos, lang=args.lang, color=not args.no_color)
    if not args.no_files and args.report_dir:
        report_dir = Path(args.report_dir)
        write_reports(cosmos, report_dir, lang=args.lang, explain_limit=args.explain_limit)
        print("\n" + text(args.lang, "Reports written to:", "Berichte geschrieben nach:") + f" {report_dir.resolve()}")
        print("- final_report.md")
        print("- final_state.json")
        print("- snapshots.csv")
        print("- ledger.csv")
        print("- companies.csv")
        print("- trades.csv")
        print("- identity_samples.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
