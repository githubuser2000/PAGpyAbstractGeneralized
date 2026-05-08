#!/usr/bin/env pypy3
# -*- coding: utf-8 -*-
"""
MÜNZÖKONOMIE – ein ausführbares Wirtschaftssystem in PyPy3.

Dieses Programm modelliert das im Chat entwickelte System:
Eine Münze ist eine Optimierungseinheit M = (Hauptfunktion, Nebenbedingung, Kategorie).
Die 19 Kategorien werden als Wirtschaftssektoren abgebildet. Daraus entsteht eine
agentenbasierte Wirtschaftssimulation mit Haushalten, Unternehmen, Banken, Staat,
Zentralbank, Märkten, Außenhandel, Umwelt, Verträgen, Steuern, Geld, Kredit,
Subventionen, Innovation, Bildung, Gesundheit, Kultur, Solidarität und Zielnutzen.

Nur Standardbibliothek. Läuft unter CPython 3 und PyPy3.

Beispiel:
    pypy3 muenzoekonomie.py --years 20 --households 120 --firms-per-category 2 --seed 42 --out ergebnis

Ausgaben im Zielordner:
    metrics.csv       Kennzahlen je Periode
    ledger.csv        Zahlungs- und Ereignisjournal
    agents.json       Endzustand der Akteure
    coins.json        erzeugte Münzen/Optimierungsobjekte
    contracts.json    Arbeits-, Kredit- und Lieferverträge
    summary.md        lesbare Auswertung
"""

from __future__ import print_function
from dataclasses import dataclass, field, asdict
from enum import Enum
from typing import Dict, List, Tuple, Optional, Any
import argparse
import csv
import json
import math
import os
import random
import statistics
import sys
import time

VERSION = "1.0.0"

# ---------------------------------------------------------------------------
# Hilfsfunktionen
# ---------------------------------------------------------------------------


def clamp(x: float, lo: float, hi: float) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if abs(b) < 1e-12:
        return default
    return a / b


def make_id(prefix: str, counter: int) -> str:
    return "%s%06d" % (prefix, counter)


def gini(values: List[float]) -> float:
    """Gini-Koeffizient, 0 = gleich, 1 = maximal ungleich."""
    xs = [max(0.0, float(v)) for v in values]
    if not xs:
        return 0.0
    xs.sort()
    total = sum(xs)
    if total <= 0:
        return 0.0
    n = len(xs)
    cum = 0.0
    for i, x in enumerate(xs, 1):
        cum += i * x
    return clamp((2.0 * cum) / (n * total) - (n + 1.0) / n, 0.0, 1.0)


def weighted_choice(rng: random.Random, items: List[Any], weights: List[float]) -> Any:
    total = sum(max(0.0, w) for w in weights)
    if total <= 0:
        return rng.choice(items)
    r = rng.random() * total
    acc = 0.0
    for item, weight in zip(items, weights):
        acc += max(0.0, weight)
        if r <= acc:
            return item
    return items[-1]


def rnd_normal(rng: random.Random, mean: float, sd: float, lo: Optional[float] = None, hi: Optional[float] = None) -> float:
    value = rng.gauss(mean, sd)
    if lo is not None:
        value = max(lo, value)
    if hi is not None:
        value = min(hi, value)
    return value


# ---------------------------------------------------------------------------
# Kategorien: die 19 Kategorien des Ausdrucks-Kontinuums als Wirtschaftssektoren
# ---------------------------------------------------------------------------


class CoinStatus(Enum):
    IDEA = "Idee"
    PLANNED = "geplant"
    FINANCED = "finanziert"
    IN_PRODUCTION = "in Produktion"
    DONE = "fertig"
    SOLD = "verkauft"
    USED = "genutzt"
    TRANSFORMED = "transformiert"
    FAILED = "gescheitert"


CATEGORY_INFO: Dict[int, Dict[str, Any]] = {
    1: {
        "short": "Expression extrahieren",
        "long": "Ausdruck / Expression extrahieren",
        "sector": "Forschung, Rohideen, Diagnose, Datengewinnung",
        "main": "Erkenntnisgehalt maximieren",
        "constraint": "Budget, Zeit, Datenschutz, Genauigkeit",
        "base_price": 90.0,
        "utility_factor": 0.45,
        "public_weight": 0.90,
        "labor_intensity": 0.85,
        "material_intensity": 0.08,
        "energy_intensity": 0.10,
        "knowledge_intensity": 1.00,
        "carbon_intensity": 0.03,
        "risk": 0.18,
        "innovation_affinity": 0.85,
        "subsidy_weight": 0.70,
        "monopoly_risk": 0.20,
    },
    2: {
        "short": "Drücken / Ausdrücken",
        "long": "Drücken, Arbeitsdruck, Energieeinsatz",
        "sector": "Arbeit, Aufwand, Leistung, Produktionsdruck",
        "main": "wirksamen Output pro Aufwand maximieren",
        "constraint": "Gesundheit, Arbeitszeit, Stress, Maschinenlast",
        "base_price": 55.0,
        "utility_factor": 0.25,
        "public_weight": 0.35,
        "labor_intensity": 1.15,
        "material_intensity": 0.18,
        "energy_intensity": 0.20,
        "knowledge_intensity": 0.35,
        "carbon_intensity": 0.09,
        "risk": 0.15,
        "innovation_affinity": 0.25,
        "subsidy_weight": 0.20,
        "monopoly_risk": 0.12,
    },
    3: {
        "short": "Extrahiertes Ausgedrücktes",
        "long": "Prototyp, Entwurf, Skizze, Halbfabrikat",
        "sector": "Vorprodukte, Entwürfe, Demos, frühe Versionen",
        "main": "Lernwert des Prototyps maximieren",
        "constraint": "noch unfertig, aber prüfbar",
        "base_price": 70.0,
        "utility_factor": 0.35,
        "public_weight": 0.55,
        "labor_intensity": 0.90,
        "material_intensity": 0.25,
        "energy_intensity": 0.16,
        "knowledge_intensity": 0.65,
        "carbon_intensity": 0.07,
        "risk": 0.25,
        "innovation_affinity": 0.70,
        "subsidy_weight": 0.45,
        "monopoly_risk": 0.15,
    },
    4: {
        "short": "Materielle Produktion",
        "long": "Tube drücken, Farbe herauspressen, Fertigung",
        "sector": "Industrie, Handwerk, Bau, Landwirtschaft, Herstellung",
        "main": "Produktionsqualität maximieren",
        "constraint": "Material, Energie, Kosten, Umwelt, Sicherheit",
        "base_price": 85.0,
        "utility_factor": 0.65,
        "public_weight": 0.55,
        "labor_intensity": 1.10,
        "material_intensity": 0.85,
        "energy_intensity": 0.75,
        "knowledge_intensity": 0.40,
        "carbon_intensity": 0.32,
        "risk": 0.20,
        "innovation_affinity": 0.35,
        "subsidy_weight": 0.15,
        "monopoly_risk": 0.25,
    },
    5: {
        "short": "Rahmen / Werkzeug",
        "long": "Express-Erdrücker, Extrahierer, Rahmen um das Bild",
        "sector": "Maschinen, Werkzeuge, Plattformen, Institutionen",
        "main": "Hebelwirkung maximieren",
        "constraint": "Missbrauch, Monopolmacht, Wartung, Zugang",
        "base_price": 130.0,
        "utility_factor": 0.55,
        "public_weight": 0.75,
        "labor_intensity": 0.95,
        "material_intensity": 0.75,
        "energy_intensity": 0.45,
        "knowledge_intensity": 0.75,
        "carbon_intensity": 0.21,
        "risk": 0.23,
        "innovation_affinity": 0.65,
        "subsidy_weight": 0.35,
        "monopoly_risk": 0.80,
    },
    6: {
        "short": "Expressivität / Intensität",
        "long": "Expressivität, Lautstärke, Spektralfarbe, Intensität",
        "sector": "Marken, Signalstärke, Qualität, Aufmerksamkeit",
        "main": "wahrgenommene Intensität und Qualität maximieren",
        "constraint": "Manipulation, Reizüberflutung, Wahrheit",
        "base_price": 95.0,
        "utility_factor": 0.70,
        "public_weight": 0.40,
        "labor_intensity": 0.75,
        "material_intensity": 0.20,
        "energy_intensity": 0.22,
        "knowledge_intensity": 0.60,
        "carbon_intensity": 0.08,
        "risk": 0.17,
        "innovation_affinity": 0.45,
        "subsidy_weight": 0.10,
        "monopoly_risk": 0.35,
    },
    7: {
        "short": "Kreative Formung",
        "long": "Impression, Zeichnen, Malen, Skulptur, Farbkreis",
        "sector": "Kunst, Design, Architektur, Mode, Mediengestaltung",
        "main": "ästhetische und expressive Kohärenz maximieren",
        "constraint": "Medium, Stil, Budget, Publikum, Ethik",
        "base_price": 105.0,
        "utility_factor": 0.85,
        "public_weight": 0.70,
        "labor_intensity": 0.85,
        "material_intensity": 0.25,
        "energy_intensity": 0.18,
        "knowledge_intensity": 0.70,
        "carbon_intensity": 0.06,
        "risk": 0.28,
        "innovation_affinity": 0.70,
        "subsidy_weight": 0.55,
        "monopoly_risk": 0.18,
    },
    8: {
        "short": "Bild / fertiges Objekt",
        "long": "Bild, Image, Picture, Skulptur, Collage, Ware",
        "sector": "Endprodukt, Medienobjekt, fertige Ware",
        "main": "Nutzbarkeit und Wahrnehmbarkeit maximieren",
        "constraint": "Qualität, Haltbarkeit, Verständlichkeit",
        "base_price": 110.0,
        "utility_factor": 0.80,
        "public_weight": 0.50,
        "labor_intensity": 0.80,
        "material_intensity": 0.55,
        "energy_intensity": 0.35,
        "knowledge_intensity": 0.45,
        "carbon_intensity": 0.16,
        "risk": 0.18,
        "innovation_affinity": 0.45,
        "subsidy_weight": 0.15,
        "monopoly_risk": 0.22,
    },
    9: {
        "short": "Typen des Ausdrucks",
        "long": "Typen, Arten, Standards, Genres, Klassifikation",
        "sector": "Normen, Labels, Produktarten, Branchenlogik",
        "main": "Orientierung maximieren",
        "constraint": "Übervereinfachung, Diskriminierung, Starrheit",
        "base_price": 75.0,
        "utility_factor": 0.40,
        "public_weight": 0.85,
        "labor_intensity": 0.65,
        "material_intensity": 0.08,
        "energy_intensity": 0.10,
        "knowledge_intensity": 0.95,
        "carbon_intensity": 0.03,
        "risk": 0.12,
        "innovation_affinity": 0.50,
        "subsidy_weight": 0.55,
        "monopoly_risk": 0.38,
    },
    10: {
        "short": "Galerie / Markt",
        "long": "Galerie, Plattform, Markt, Laden, Archiv",
        "sector": "Märkte, Plattformen, Börsen, Museen, Kataloge",
        "main": "passende Zuordnung von Angebot und Nachfrage maximieren",
        "constraint": "Transparenz, Fairness, Zugang, Machtkonzentration",
        "base_price": 100.0,
        "utility_factor": 0.50,
        "public_weight": 0.75,
        "labor_intensity": 0.70,
        "material_intensity": 0.18,
        "energy_intensity": 0.24,
        "knowledge_intensity": 0.75,
        "carbon_intensity": 0.07,
        "risk": 0.18,
        "innovation_affinity": 0.55,
        "subsidy_weight": 0.20,
        "monopoly_risk": 0.90,
    },
    11: {
        "short": "Stilbruch / Disruption",
        "long": "Stilbruch, chaotischer expressiver Stil, Experiment",
        "sector": "Innovation, Disruption, radikale Experimente",
        "main": "neue Möglichkeiten maximieren",
        "constraint": "Systemrisiko, Täuschung, soziale Schäden",
        "base_price": 125.0,
        "utility_factor": 0.55,
        "public_weight": 0.60,
        "labor_intensity": 0.75,
        "material_intensity": 0.25,
        "energy_intensity": 0.25,
        "knowledge_intensity": 0.90,
        "carbon_intensity": 0.10,
        "risk": 0.45,
        "innovation_affinity": 1.00,
        "subsidy_weight": 0.35,
        "monopoly_risk": 0.30,
    },
    12: {
        "short": "Bewertung / Kritik",
        "long": "Einordnung der Expressivität, Rating, Prüfung, Kritik",
        "sector": "Zertifizierung, Rezension, Qualitätskontrolle, Risikoanalyse",
        "main": "treffsichere Bewertung maximieren",
        "constraint": "Korruption, Bias, Intransparenz",
        "base_price": 82.0,
        "utility_factor": 0.45,
        "public_weight": 0.90,
        "labor_intensity": 0.70,
        "material_intensity": 0.05,
        "energy_intensity": 0.08,
        "knowledge_intensity": 1.05,
        "carbon_intensity": 0.02,
        "risk": 0.15,
        "innovation_affinity": 0.45,
        "subsidy_weight": 0.50,
        "monopoly_risk": 0.70,
    },
    13: {
        "short": "Spektrum / Infrastruktur",
        "long": "Spektrum, Farbverlauf, Akustik, EM, Energie, Netze",
        "sector": "Energie, Datenströme, Verkehrsflüsse, Kommunikationsnetze",
        "main": "stabile Übertragung maximieren",
        "constraint": "Kapazität, Sicherheit, Rauschen, Überlastung",
        "base_price": 120.0,
        "utility_factor": 0.75,
        "public_weight": 0.95,
        "labor_intensity": 0.80,
        "material_intensity": 0.80,
        "energy_intensity": 0.85,
        "knowledge_intensity": 0.80,
        "carbon_intensity": 0.25,
        "risk": 0.20,
        "innovation_affinity": 0.65,
        "subsidy_weight": 0.65,
        "monopoly_risk": 0.85,
    },
    14: {
        "short": "Fusion von Ideen",
        "long": "Kooperation, Fusion, neue Stilrichtung, neue Epoche",
        "sector": "Kooperation, Forschungskonsortien, neue Industrien",
        "main": "Synergie maximieren",
        "constraint": "Machtkonzentration, Koordinationskosten, Konflikte",
        "base_price": 115.0,
        "utility_factor": 0.60,
        "public_weight": 0.80,
        "labor_intensity": 0.75,
        "material_intensity": 0.18,
        "energy_intensity": 0.18,
        "knowledge_intensity": 1.05,
        "carbon_intensity": 0.06,
        "risk": 0.30,
        "innovation_affinity": 0.95,
        "subsidy_weight": 0.65,
        "monopoly_risk": 0.55,
    },
    15: {
        "short": "Rhythmus / Serie",
        "long": "Bilderreihe, Musikstück, Takt, Wiederholung, Rhythmus",
        "sector": "Serienproduktion, Routinen, Prozesse, Abonnements",
        "main": "verlässliche Wiederholung maximieren",
        "constraint": "Monotonie, Verschleiß, Qualitätsverlust",
        "base_price": 88.0,
        "utility_factor": 0.58,
        "public_weight": 0.50,
        "labor_intensity": 0.75,
        "material_intensity": 0.45,
        "energy_intensity": 0.38,
        "knowledge_intensity": 0.45,
        "carbon_intensity": 0.13,
        "risk": 0.12,
        "innovation_affinity": 0.35,
        "subsidy_weight": 0.12,
        "monopoly_risk": 0.25,
    },
    16: {
        "short": "Transformation",
        "long": "Bild-zu-Bild-Umwandlung, Formatierung, Recycling",
        "sector": "Reparatur, Recycling, Übersetzung, Datenkonvertierung, Logistik",
        "main": "verlustarme Umwandlung maximieren",
        "constraint": "Informationsverlust, Kosten, Kompatibilität",
        "base_price": 92.0,
        "utility_factor": 0.66,
        "public_weight": 0.85,
        "labor_intensity": 0.85,
        "material_intensity": 0.25,
        "energy_intensity": 0.30,
        "knowledge_intensity": 0.75,
        "carbon_intensity": -0.08,
        "risk": 0.14,
        "innovation_affinity": 0.60,
        "subsidy_weight": 0.75,
        "monopoly_risk": 0.28,
    },
    17: {
        "short": "Meta-Intelligenz",
        "long": "Intelligenz über Intelligenzen anderer",
        "sector": "Bildung, KI, Beratung, Psychologie, Strategie",
        "main": "Verstehen von Entscheidungsfähigkeit maximieren",
        "constraint": "Privatsphäre, Manipulation, Machtmissbrauch",
        "base_price": 140.0,
        "utility_factor": 0.78,
        "public_weight": 1.00,
        "labor_intensity": 0.90,
        "material_intensity": 0.08,
        "energy_intensity": 0.16,
        "knowledge_intensity": 1.25,
        "carbon_intensity": 0.04,
        "risk": 0.22,
        "innovation_affinity": 0.95,
        "subsidy_weight": 0.80,
        "monopoly_risk": 0.88,
    },
    18: {
        "short": "Wertschätzung / Solidarität",
        "long": "Ausdruck des sich angezogen Fühlens, Wertschätzung, Hilfe",
        "sector": "Pflege, Geschenke, Hilfe, soziale Arbeit, Solidarität",
        "main": "soziale Wärme und Unterstützung maximieren",
        "constraint": "Echtheit, Ausbeutung, Abhängigkeit, Ressourcen",
        "base_price": 65.0,
        "utility_factor": 0.95,
        "public_weight": 1.00,
        "labor_intensity": 1.10,
        "material_intensity": 0.18,
        "energy_intensity": 0.12,
        "knowledge_intensity": 0.55,
        "carbon_intensity": 0.04,
        "risk": 0.10,
        "innovation_affinity": 0.35,
        "subsidy_weight": 0.90,
        "monopoly_risk": 0.15,
    },
    19: {
        "short": "Ziel-Ergebnis / Hot Dog",
        "long": "Ziel-Ergebnis der Expression und Extraktion, Endnutzen",
        "sector": "Konsum, Grundversorgung, Bedürfnisbefriedigung",
        "main": "erreichte Bedürfnisbefriedigung maximieren",
        "constraint": "Kosten, Gesundheit, Nachhaltigkeit, Fairness",
        "base_price": 60.0,
        "utility_factor": 1.00,
        "public_weight": 0.95,
        "labor_intensity": 0.95,
        "material_intensity": 0.50,
        "energy_intensity": 0.35,
        "knowledge_intensity": 0.35,
        "carbon_intensity": 0.16,
        "risk": 0.10,
        "innovation_affinity": 0.25,
        "subsidy_weight": 0.65,
        "monopoly_risk": 0.22,
    },
}

NEED_WEIGHTS: Dict[int, float] = {
    19: 1.00, 18: 0.55, 17: 0.45, 13: 0.55, 8: 0.35, 7: 0.30,
    6: 0.18, 10: 0.18, 16: 0.25, 12: 0.15, 1: 0.12, 9: 0.10,
}

PUBLIC_CATEGORIES = [1, 7, 9, 12, 13, 14, 16, 17, 18, 19]
IMPORTABLE_CATEGORIES = set([4, 5, 8, 13, 15, 16, 19])


# ---------------------------------------------------------------------------
# Datenklassen: Münze, Vertrag, Ledger
# ---------------------------------------------------------------------------


@dataclass
class Coin:
    """Eine wirtschaftliche Münze als Optimierungsproblem."""
    id: str
    tick: int
    owner_id: str
    category: int
    main_function: str
    constraint: str
    inputs: Dict[str, float]
    outputs: Dict[str, float]
    quality: float
    price: float
    public_value: float
    externality: Dict[str, float]
    risk: float
    status: str = CoinStatus.IDEA.value
    score: float = 0.0
    description: str = ""

    def evaluate(self, environment_nature: float, trust: float) -> float:
        rule = CATEGORY_INFO[self.category]
        output_value = sum(self.outputs.values()) * self.quality * self.price
        input_burden = sum(max(0.0, v) for v in self.inputs.values())
        ecological_penalty = max(0.0, self.externality.get("carbon", 0.0)) * (1.1 - environment_nature)
        social_bonus = self.public_value * rule["public_weight"] * (0.5 + trust)
        risk_penalty = self.risk * (0.5 + abs(0.5 - trust)) * 35.0
        self.score = output_value + social_bonus - input_burden - ecological_penalty - risk_penalty
        return self.score


@dataclass
class Contract:
    id: str
    tick: int
    kind: str
    parties: List[str]
    category: Optional[int]
    amount: float
    terms: Dict[str, Any]
    status: str = "aktiv"


@dataclass
class LedgerEntry:
    tick: int
    event: str
    source: str
    target: str
    amount: float
    category: Optional[int]
    description: str


@dataclass
class Ledger:
    entries: List[LedgerEntry] = field(default_factory=list)

    def add(self, tick: int, event: str, source: str, target: str, amount: float, category: Optional[int], description: str) -> None:
        self.entries.append(LedgerEntry(tick, event, source, target, float(amount), category, description))

    def total_event(self, event: str, tick: Optional[int] = None) -> float:
        if tick is None:
            return sum(e.amount for e in self.entries if e.event == event)
        return sum(e.amount for e in self.entries if e.event == event and e.tick == tick)


# ---------------------------------------------------------------------------
# Akteure
# ---------------------------------------------------------------------------


@dataclass
class Household:
    id: str
    name: str
    money: float
    skill: float
    health: float
    education: float
    culture_pref: float
    care_need: float
    trust: float
    attention: float
    utility: float = 0.0
    employed_by: Optional[str] = None
    wage_income: float = 0.0
    unemployment_ticks: int = 0
    last_consumption: Dict[int, float] = field(default_factory=dict)

    def labor_capacity(self) -> float:
        # Gesundheit, Bildung und Aufmerksamkeit bestimmen Arbeitsfähigkeit.
        return clamp(0.25 + 0.35 * self.skill + 0.25 * self.health + 0.20 * self.education + 0.10 * self.attention, 0.0, 1.6)

    def reset_period(self) -> None:
        self.employed_by = None
        self.wage_income = 0.0
        self.last_consumption = {}
        self.attention = clamp(self.attention + 0.03 - 0.02 * self.care_need, 0.15, 1.0)


@dataclass
class Firm:
    id: str
    name: str
    category: int
    money: float
    capital: float
    technology: float
    reputation: float
    productivity: float
    wage_offer: float
    employees: List[str] = field(default_factory=list)
    inventory: float = 0.0
    inventory_quality: float = 0.50
    debt: float = 0.0
    profit: float = 0.0
    last_output: float = 0.0
    market_power: float = 0.0
    failed: bool = False

    def desired_workers(self, market_price: float, policy_rate: float, demand_pressure: float) -> int:
        rule = CATEGORY_INFO[self.category]
        capital_factor = math.sqrt(max(0.0, self.capital) / 900.0)
        tech_factor = 0.6 + self.technology
        price_factor = clamp(market_price / rule["base_price"], 0.5, 1.8)
        interest_drag = clamp(1.0 - 1.5 * policy_rate, 0.45, 1.05)
        desired = rule["labor_intensity"] * capital_factor * tech_factor * price_factor * interest_drag * (0.8 + demand_pressure)
        return int(clamp(round(desired * 3.2), 0, 18))

    def reset_period(self) -> None:
        self.employees = []
        self.profit = 0.0
        self.last_output = 0.0


@dataclass
class Loan:
    id: str
    lender_id: str
    borrower_id: str
    principal: float
    outstanding: float
    interest_rate: float
    start_tick: int
    due_tick: int
    status: str = "aktiv"


@dataclass
class Bank:
    id: str
    name: str
    money: float
    capital_ratio: float
    risk_appetite: float
    loans: Dict[str, Loan] = field(default_factory=dict)
    defaults: int = 0


@dataclass
class State:
    id: str = "STAAT"
    name: str = "Münzstaat"
    money: float = 25000.0
    debt: float = 0.0
    income_tax_rate: float = 0.18
    corporate_tax_rate: float = 0.20
    vat_rate: float = 0.11
    carbon_tax_rate: float = 8.0
    tariff_rate: float = 0.04
    ubi: float = 25.0
    minimum_wage: float = 34.0
    education_index: float = 0.60
    health_index: float = 0.65
    infrastructure_index: float = 0.62
    commons_index: float = 0.55
    culture_index: float = 0.55
    social_index: float = 0.60
    regulation_index: float = 0.60
    environment_program: float = 0.55
    last_tax_revenue: float = 0.0
    last_spending: float = 0.0
    last_deficit: float = 0.0


@dataclass
class CentralBank:
    id: str = "MUENZBANK"
    name: str = "Münzbank"
    policy_rate: float = 0.025
    target_inflation: float = 0.02
    money_supply: float = 0.0
    credibility: float = 0.75

    def update_policy(self, inflation: float, unemployment: float, nature_stress: float) -> None:
        # Einfache Taylor-artige Regel mit Rücksicht auf Arbeitslosigkeit und ökologische Angebotsschocks.
        inflation_gap = inflation - self.target_inflation
        unemployment_gap = unemployment - 0.06
        rate = self.policy_rate + 0.35 * inflation_gap - 0.08 * unemployment_gap + 0.03 * nature_stress
        self.policy_rate = clamp(rate, 0.002, 0.16)
        self.credibility = clamp(self.credibility - 0.04 * abs(inflation_gap) + 0.01, 0.25, 0.95)


@dataclass
class ForeignSector:
    id: str = "AUSLAND"
    name: str = "Außenwirtschaft"
    money: float = 100000.0
    world_prices: Dict[int, float] = field(default_factory=dict)
    import_volume: float = 0.0
    export_volume: float = 0.0


@dataclass
class Environment:
    nature_capital: float = 0.82
    biodiversity: float = 0.78
    carbon_stock: float = 0.0
    current_emissions: float = 0.0
    water_stress: float = 0.22
    resource_pressure: float = 0.25

    def reset_period(self) -> None:
        self.current_emissions = 0.0

    def apply_externality(self, carbon: float, resource_use: float, regeneration: float) -> None:
        carbon = float(carbon)
        resource_use = float(resource_use)
        regeneration = float(regeneration)
        self.current_emissions += max(0.0, carbon)
        self.carbon_stock += max(0.0, carbon) * 0.012
        # Negative carbon_intensity/Transformation und Umweltprogramme regenerieren Naturkapital.
        damage = 0.00035 * max(0.0, carbon) + 0.00025 * max(0.0, resource_use)
        repair = 0.00045 * max(0.0, regeneration)
        self.nature_capital = clamp(self.nature_capital - damage + repair, 0.05, 1.15)
        self.biodiversity = clamp(self.biodiversity - 0.55 * damage + 0.35 * repair, 0.05, 1.05)
        self.resource_pressure = clamp(self.resource_pressure + 0.0002 * resource_use - 0.002 * repair, 0.0, 1.0)
        self.water_stress = clamp(self.water_stress + 0.0001 * resource_use - 0.001 * repair, 0.0, 1.0)

    def regenerate(self, environment_program: float, public_spending: float) -> None:
        natural_regen = 0.004 + 0.004 * environment_program + min(0.015, public_spending / 200000.0)
        climate_drag = min(0.012, self.carbon_stock * 0.00008)
        self.nature_capital = clamp(self.nature_capital + natural_regen - climate_drag, 0.05, 1.15)
        self.biodiversity = clamp(self.biodiversity + 0.6 * natural_regen - 0.5 * climate_drag, 0.05, 1.05)
        self.resource_pressure = clamp(self.resource_pressure * 0.992, 0.0, 1.0)
        self.water_stress = clamp(self.water_stress * 0.994, 0.0, 1.0)


@dataclass
class Market:
    prices: Dict[int, float]
    previous_prices: Dict[int, float]
    demand: Dict[int, float] = field(default_factory=dict)
    supply: Dict[int, float] = field(default_factory=dict)
    sold: Dict[int, float] = field(default_factory=dict)
    turnover: Dict[int, float] = field(default_factory=dict)

    def reset_period(self) -> None:
        self.demand = {k: 0.0 for k in CATEGORY_INFO}
        self.supply = {k: 0.0 for k in CATEGORY_INFO}
        self.sold = {k: 0.0 for k in CATEGORY_INFO}
        self.turnover = {k: 0.0 for k in CATEGORY_INFO}
        self.previous_prices = dict(self.prices)

    def price_index(self) -> float:
        weights = [NEED_WEIGHTS.get(k, 0.15) + CATEGORY_INFO[k]["public_weight"] * 0.05 for k in CATEGORY_INFO]
        values = [self.prices[k] / CATEGORY_INFO[k]["base_price"] for k in CATEGORY_INFO]
        return safe_div(sum(w * v for w, v in zip(weights, values)), sum(weights), 1.0)

    def previous_price_index(self) -> float:
        weights = [NEED_WEIGHTS.get(k, 0.15) + CATEGORY_INFO[k]["public_weight"] * 0.05 for k in CATEGORY_INFO]
        values = [self.previous_prices.get(k, self.prices[k]) / CATEGORY_INFO[k]["base_price"] for k in CATEGORY_INFO]
        return safe_div(sum(w * v for w, v in zip(weights, values)), sum(weights), 1.0)

    def update_prices(self, central_rate: float, regulation: float) -> None:
        for k in CATEGORY_INFO:
            d = self.demand.get(k, 0.0)
            s = self.supply.get(k, 0.0)
            sold = self.sold.get(k, 0.0)
            # Nachfrageüberhang und nicht verkaufte Lagerbestände bewegen Preise.
            shortage = safe_div(d - sold, max(1.0, d + s), 0.0)
            glut = safe_div(max(0.0, s - sold), max(1.0, d + s), 0.0)
            monopoly_markup = CATEGORY_INFO[k]["monopoly_risk"] * (1.0 - regulation) * 0.025
            interest_cost = central_rate * 0.10
            change = 0.22 * shortage - 0.12 * glut + monopoly_markup + interest_cost
            self.prices[k] = clamp(self.prices[k] * math.exp(change), CATEGORY_INFO[k]["base_price"] * 0.35, CATEGORY_INFO[k]["base_price"] * 4.50)


# ---------------------------------------------------------------------------
# Die Wirtschaft selbst
# ---------------------------------------------------------------------------


class Economy:
    def __init__(
        self,
        seed: int = 42,
        households: int = 100,
        firms_per_category: int = 2,
        banks: int = 2,
        foreign_trade: bool = True,
        shock_frequency: float = 0.06,
    ) -> None:
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
        self.tick = 0
        self.household_count = int(households)
        self.firms_per_category = int(firms_per_category)
        self.bank_count = int(banks)
        self.foreign_trade_enabled = bool(foreign_trade)
        self.shock_frequency = float(shock_frequency)

        self.households: Dict[str, Household] = {}
        self.firms: Dict[str, Firm] = {}
        self.banks: Dict[str, Bank] = {}
        self.state = State()
        self.central_bank = CentralBank()
        self.foreign = ForeignSector()
        self.environment = Environment()
        self.ledger = Ledger()
        self.coins: List[Coin] = []
        self.contracts: List[Contract] = []
        self.metrics: List[Dict[str, Any]] = []
        self.event_log: List[str] = []
        self.next_coin_id = 1
        self.next_contract_id = 1
        self.next_loan_id = 1

        initial_prices = {k: CATEGORY_INFO[k]["base_price"] * self.rng.uniform(0.93, 1.07) for k in CATEGORY_INFO}
        self.market = Market(prices=initial_prices, previous_prices=dict(initial_prices))
        self.foreign.world_prices = {k: CATEGORY_INFO[k]["base_price"] * self.rng.uniform(0.80, 1.25) for k in CATEGORY_INFO}
        self.last_inflation = 0.0
        self.last_unemployment = 0.0
        self.last_gdp = 0.0
        self.last_mw = 0.0
        self.last_output_value = 0.0
        self.crisis_flags: Dict[str, int] = {}
        self._setup_agents()
        self.central_bank.money_supply = self.total_money()

    # ------------------------------------------------------------------
    # Aufbau
    # ------------------------------------------------------------------

    def _setup_agents(self) -> None:
        for i in range(self.household_count):
            hid = make_id("H", i + 1)
            education = clamp(self.rng.betavariate(2.5, 2.3), 0.05, 0.98)
            skill = clamp(0.35 * education + self.rng.betavariate(2.0, 2.5) * 0.75, 0.05, 1.0)
            h = Household(
                id=hid,
                name="Haushalt %d" % (i + 1),
                money=rnd_normal(self.rng, 850.0, 270.0, 120.0, 2500.0),
                skill=skill,
                health=rnd_normal(self.rng, 0.72, 0.15, 0.20, 1.0),
                education=education,
                culture_pref=clamp(self.rng.betavariate(2.0, 2.5), 0.02, 1.0),
                care_need=clamp(self.rng.betavariate(1.4, 4.0), 0.0, 1.0),
                trust=rnd_normal(self.rng, 0.62, 0.13, 0.15, 0.95),
                attention=rnd_normal(self.rng, 0.70, 0.12, 0.20, 1.0),
            )
            self.households[hid] = h

        firm_counter = 1
        for category in sorted(CATEGORY_INFO):
            rule = CATEGORY_INFO[category]
            for _ in range(self.firms_per_category):
                fid = make_id("F", firm_counter)
                tech = rnd_normal(self.rng, 0.72 + rule["innovation_affinity"] * 0.08, 0.12, 0.25, 1.25)
                f = Firm(
                    id=fid,
                    name="Firma %d K%02d" % (firm_counter, category),
                    category=category,
                    money=rnd_normal(self.rng, 3200.0, 1150.0, 550.0, 8500.0),
                    capital=rnd_normal(self.rng, 1850.0, 650.0, 400.0, 5000.0),
                    technology=tech,
                    reputation=rnd_normal(self.rng, 0.58, 0.13, 0.15, 0.95),
                    productivity=rnd_normal(self.rng, 0.90, 0.16, 0.35, 1.35),
                    wage_offer=rnd_normal(self.rng, 46.0 + CATEGORY_INFO[category]["knowledge_intensity"] * 6.0, 8.0, 28.0, 95.0),
                    inventory=rnd_normal(self.rng, 6.0, 2.5, 0.5, 16.0),
                    inventory_quality=rnd_normal(self.rng, 0.58, 0.10, 0.25, 0.95),
                    market_power=CATEGORY_INFO[category]["monopoly_risk"] * self.rng.uniform(0.05, 0.35),
                )
                self.firms[fid] = f
                firm_counter += 1

        for i in range(self.bank_count):
            bid = make_id("B", i + 1)
            bank = Bank(
                id=bid,
                name="Geschäftsbank %d" % (i + 1),
                money=rnd_normal(self.rng, 42000.0, 8000.0, 15000.0, 80000.0),
                capital_ratio=rnd_normal(self.rng, 0.12, 0.025, 0.07, 0.22),
                risk_appetite=rnd_normal(self.rng, 0.55, 0.15, 0.20, 0.95),
            )
            self.banks[bid] = bank

    # ------------------------------------------------------------------
    # IDs und Registrierung
    # ------------------------------------------------------------------

    def new_coin(self, **kwargs: Any) -> Coin:
        cid = make_id("M", self.next_coin_id)
        self.next_coin_id += 1
        coin = Coin(id=cid, **kwargs)
        self.coins.append(coin)
        return coin

    def new_contract(self, kind: str, parties: List[str], category: Optional[int], amount: float, terms: Dict[str, Any]) -> Contract:
        cid = make_id("V", self.next_contract_id)
        self.next_contract_id += 1
        contract = Contract(id=cid, tick=self.tick, kind=kind, parties=parties, category=category, amount=float(amount), terms=terms)
        self.contracts.append(contract)
        return contract

    def new_loan_id_value(self) -> str:
        lid = make_id("L", self.next_loan_id)
        self.next_loan_id += 1
        return lid

    # ------------------------------------------------------------------
    # Kernablauf
    # ------------------------------------------------------------------

    def run(self, periods: int, quiet: bool = False, print_every: int = 4) -> List[Dict[str, Any]]:
        periods = int(periods)
        for _ in range(periods):
            self.step()
            if not quiet and (self.tick % max(1, print_every) == 0 or self.tick == 1):
                m = self.metrics[-1]
                print(
                    "t=%03d BMP=%9.1f MW=%8.1f Inflation=%6.2f%% Arbeitslos=%5.1f%% Natur=%4.2f Geld=%9.1f" % (
                        m["tick"], m["bmp"], m["mw"], 100 * m["inflation"], 100 * m["unemployment"],
                        m["nature_capital"], m["money_supply"]
                    )
                )
        return self.metrics

    def step(self) -> None:
        self.tick += 1
        self.market.reset_period()
        self.environment.reset_period()
        self.foreign.import_volume = 0.0
        self.foreign.export_volume = 0.0
        self.state.last_tax_revenue = 0.0
        self.state.last_spending = 0.0
        self.state.last_deficit = 0.0
        self.last_output_value = 0.0
        self._decrement_crises()

        for h in self.households.values():
            h.reset_period()
        for f in self.firms.values():
            f.reset_period()

        self._maybe_apply_shock()
        self._public_baseline_update()
        self._pay_basic_income()
        self._labor_market()
        self._production_phase()
        self._state_public_spending()
        self._household_consumption()
        self._foreign_trade_exports()
        self._loan_service()
        self._corporate_tax_and_failures()
        self._innovation_phase()
        self._social_and_health_dynamics()
        self._environmental_regeneration()
        self._update_market_prices_and_policy()
        self._collect_metrics()

    # ------------------------------------------------------------------
    # Öffentliche Hand und soziale Grundstruktur
    # ------------------------------------------------------------------

    def _ensure_state_funds(self, amount: float, reason: str) -> None:
        if amount <= 0:
            return
        if self.state.money >= amount:
            return
        needed = amount - self.state.money
        # Staatsdefizit wird über Anleihen finanziert; die Münzbank stabilisiert einen Teil.
        self.state.debt += needed
        self.state.money += needed
        self.central_bank.money_supply += needed * 0.65
        self.state.last_deficit += needed
        self.ledger.add(self.tick, "staatsfinanzierung", self.central_bank.id, self.state.id, needed, None, reason)

    def _pay_basic_income(self) -> None:
        unemployment_boost = 1.0 + clamp(self.last_unemployment - 0.08, 0.0, 0.30)
        amount = self.state.ubi * unemployment_boost
        total = amount * len(self.households)
        self._ensure_state_funds(total, "Grundmünzrecht / Grundeinkommen")
        for h in self.households.values():
            self.state.money -= amount
            h.money += amount
            self.ledger.add(self.tick, "transfer", self.state.id, h.id, amount, 18, "Grundmünzrecht: Zugang zu Basismitteln")
        self.state.last_spending += total

    def _state_public_spending(self) -> None:
        # Automatischer Stabilisator und Investitionen in Kategorien 1, 7, 13, 16, 17, 18, 19.
        base_budget = 0.035 * max(1.0, self.total_money())
        recession_boost = clamp(0.09 - self.last_gdp / max(1.0, self.total_money()), 0.0, 0.08) * 12000.0
        budget = base_budget + recession_boost
        self._ensure_state_funds(budget, "öffentliche Investitionen")
        spend = min(self.state.money, budget)
        self.state.money -= spend
        self.state.last_spending += spend

        # Allokation: Bildung, Gesundheit, Infrastruktur, Commons, Kultur, Soziales, Umwelt.
        education = spend * 0.20
        health = spend * 0.18
        infra = spend * 0.20
        commons = spend * 0.14
        culture = spend * 0.10
        social = spend * 0.10
        environment = spend * 0.08

        self.state.education_index = clamp(self.state.education_index + education / 450000.0, 0.10, 1.25)
        self.state.health_index = clamp(self.state.health_index + health / 430000.0, 0.10, 1.25)
        self.state.infrastructure_index = clamp(self.state.infrastructure_index + infra / 500000.0, 0.10, 1.25)
        self.state.commons_index = clamp(self.state.commons_index + commons / 330000.0, 0.10, 1.25)
        self.state.culture_index = clamp(self.state.culture_index + culture / 250000.0, 0.10, 1.25)
        self.state.social_index = clamp(self.state.social_index + social / 280000.0, 0.10, 1.25)
        self.state.environment_program = clamp(self.state.environment_program + environment / 300000.0, 0.10, 1.25)

        for cat, part, label in [(17, education, "Bildung"), (18, health + social, "Gesundheit/Soziales"),
                                 (13, infra, "Infrastruktur"), (1, commons, "Commons/Forschung"),
                                 (7, culture, "Kultur"), (16, environment, "Regeneration")]:
            self.ledger.add(self.tick, "staat_ausgabe", self.state.id, "OEFFENTLICH", part, cat, label)

    def _public_baseline_update(self) -> None:
        # Institutionen verlieren ohne laufende Pflege leicht an Kraft.
        decay = 0.998
        self.state.education_index = clamp(self.state.education_index * decay, 0.10, 1.25)
        self.state.health_index = clamp(self.state.health_index * decay, 0.10, 1.25)
        self.state.infrastructure_index = clamp(self.state.infrastructure_index * decay, 0.10, 1.25)
        self.state.commons_index = clamp(self.state.commons_index * decay, 0.10, 1.25)
        self.state.culture_index = clamp(self.state.culture_index * decay, 0.10, 1.25)
        self.state.social_index = clamp(self.state.social_index * decay, 0.10, 1.25)
        self.state.environment_program = clamp(self.state.environment_program * decay, 0.10, 1.25)
        self.state.regulation_index = clamp(self.state.regulation_index * 0.999 + 0.001 * self.central_bank.credibility, 0.10, 1.25)

    # ------------------------------------------------------------------
    # Arbeit, Produktion, Optimierung
    # ------------------------------------------------------------------

    def _labor_market(self) -> None:
        firms = [f for f in self.firms.values() if not f.failed]
        households = list(self.households.values())
        self.rng.shuffle(households)
        demand_pressure_by_cat = self._demand_pressure_by_category()

        vacancies: List[Tuple[Firm, int]] = []
        for f in firms:
            desired = f.desired_workers(self.market.prices[f.category], self.central_bank.policy_rate, demand_pressure_by_cat.get(f.category, 1.0))
            vacancies.append((f, desired))
        # Höhere Löhne und gute Reputation ziehen zuerst Arbeitskräfte.
        vacancies.sort(key=lambda t: (t[0].wage_offer, t[0].reputation), reverse=True)

        available = [h for h in households if h.health > 0.20]
        for f, desired in vacancies:
            if desired <= 0:
                continue
            for _ in range(desired):
                if not available:
                    break
                # Kategorie 17/Bildung und Wissen profitieren von guter Bildung; Produktion von Skill.
                weights = []
                for h in available:
                    fit = 0.55 * h.skill + 0.35 * h.education + 0.10 * h.trust
                    if CATEGORY_INFO[f.category]["knowledge_intensity"] > 0.8:
                        fit += 0.25 * h.education
                    if f.category == 18:
                        fit += 0.20 * h.trust + 0.10 * h.health
                    weights.append(max(0.05, fit))
                chosen = weighted_choice(self.rng, available, weights)
                available.remove(chosen)
                chosen.employed_by = f.id
                f.employees.append(chosen.id)
                self.new_contract(
                    "arbeitsvertrag",
                    [chosen.id, f.id],
                    f.category,
                    max(self.state.minimum_wage, f.wage_offer),
                    {"lohn": max(self.state.minimum_wage, f.wage_offer), "periode": self.tick},
                )

        for h in self.households.values():
            if h.employed_by is None:
                h.unemployment_ticks += 1
                h.trust = clamp(h.trust - 0.006, 0.05, 1.0)
            else:
                h.unemployment_ticks = 0
                h.trust = clamp(h.trust + 0.003, 0.05, 1.0)

    def _production_phase(self) -> None:
        firms = [f for f in self.firms.values() if not f.failed]
        for f in firms:
            employees = [self.households[eid] for eid in f.employees if eid in self.households]
            # Falls Firma zu wenig Liquidität für Lohn und Vorleistungen hat: Kredit versuchen.
            expected_wages = sum(max(self.state.minimum_wage, f.wage_offer) * h.labor_capacity() for h in employees)
            expected_inputs = self._expected_input_cost(f, len(employees))
            if f.money < expected_wages + expected_inputs:
                self._request_credit(f, expected_wages + expected_inputs - f.money + 200.0, "Betriebsmittel")

            # Löhne zahlen.
            wage_total = 0.0
            for h in employees:
                gross_wage = max(self.state.minimum_wage, f.wage_offer) * h.labor_capacity()
                if f.money < gross_wage:
                    gross_wage = max(0.0, f.money)
                if gross_wage <= 0:
                    continue
                income_tax = gross_wage * self.state.income_tax_rate
                net_wage = gross_wage - income_tax
                f.money -= gross_wage
                h.money += net_wage
                h.wage_income += gross_wage
                self.state.money += income_tax
                self.state.last_tax_revenue += income_tax
                wage_total += gross_wage
                self.ledger.add(self.tick, "lohn", f.id, h.id, net_wage, f.category, "Nettoarbeitslohn")
                self.ledger.add(self.tick, "steuer", h.id, self.state.id, income_tax, None, "Einkommensteuer")

            labor_units = sum(h.labor_capacity() for h in employees)
            if labor_units <= 0.01:
                # Solo-Unternehmer: minimale Erhaltungstätigkeit, falls Geld da ist.
                labor_units = 0.12 * clamp(f.technology, 0.3, 1.3)

            output, quality, input_cost, externality = self._produce_output(f, employees, labor_units)
            if input_cost > 0:
                if f.money < input_cost:
                    scale = clamp(f.money / input_cost, 0.0, 1.0)
                    output *= scale
                    input_cost *= scale
                    externality["carbon"] *= scale
                    externality["resource_use"] *= scale
                    externality["regeneration"] *= scale
                f.money -= input_cost
                f.profit -= input_cost

            # Subventionen für öffentliche/soziale/ökologische Münzen.
            subsidy = self._category_subsidy(f.category, output, quality)
            if subsidy > 0:
                self._ensure_state_funds(subsidy, "Kategorie-Subvention")
                self.state.money -= subsidy
                self.state.last_spending += subsidy
                f.money += subsidy
                f.profit += subsidy
                self.ledger.add(self.tick, "subvention", self.state.id, f.id, subsidy, f.category, "Subvention nach Münzkategorie")

            # Carbonsteuer für positive Emissionen.
            carbon_tax = max(0.0, externality.get("carbon", 0.0)) * self.state.carbon_tax_rate
            if carbon_tax > 0 and f.money > 0:
                paid = min(f.money, carbon_tax)
                f.money -= paid
                f.profit -= paid
                self.state.money += paid
                self.state.last_tax_revenue += paid
                self.ledger.add(self.tick, "steuer", f.id, self.state.id, paid, f.category, "CO2-/Schadenssteuer")

            # Inventar und Qualität aktualisieren.
            if output > 0:
                old_inv = f.inventory
                new_inv = old_inv + output
                if new_inv > 0:
                    f.inventory_quality = clamp((old_inv * f.inventory_quality + output * quality) / new_inv, 0.05, 1.0)
                f.inventory = new_inv
                f.last_output = output
                self.last_output_value += output * self.market.prices[f.category] * quality
                self.market.supply[f.category] += output
                self.environment.apply_externality(externality["carbon"], externality["resource_use"], externality["regeneration"])

                coin = self.new_coin(
                    tick=self.tick,
                    owner_id=f.id,
                    category=f.category,
                    main_function=CATEGORY_INFO[f.category]["main"],
                    constraint=CATEGORY_INFO[f.category]["constraint"],
                    inputs={"arbeit": labor_units, "lohn": wage_total, "vorleistungen": input_cost},
                    outputs={"menge": output, "qualitaet": quality},
                    quality=quality,
                    price=self.market.prices[f.category],
                    public_value=output * quality * CATEGORY_INFO[f.category]["public_weight"],
                    externality=externality,
                    risk=CATEGORY_INFO[f.category]["risk"],
                    status=CoinStatus.DONE.value,
                    description="Produktion in Kategorie %02d: %s" % (f.category, CATEGORY_INFO[f.category]["short"]),
                )
                coin.evaluate(self.environment.nature_capital, self.average_trust())
                self.ledger.add(self.tick, "muenze", f.id, coin.id, coin.score, f.category, "Münze erzeugt und bewertet")

            # Kapitalverschleiß und Wartung.
            depreciation = f.capital * (0.0025 + 0.002 * CATEGORY_INFO[f.category]["energy_intensity"])
            f.capital = max(100.0, f.capital - depreciation + 0.10 * input_cost)

    def _produce_output(self, f: Firm, employees: List[Household], labor_units: float) -> Tuple[float, float, float, Dict[str, float]]:
        rule = CATEGORY_INFO[f.category]
        avg_skill = safe_div(sum(h.skill for h in employees), len(employees), 0.45)
        avg_education = safe_div(sum(h.education for h in employees), len(employees), 0.50)
        avg_health = safe_div(sum(h.health for h in employees), len(employees), 0.65)
        nature_drag = clamp(0.75 + 0.35 * self.environment.nature_capital, 0.35, 1.20)
        infra_boost = 0.80 + 0.35 * self.state.infrastructure_index
        commons_boost = 0.85 + 0.25 * self.state.commons_index if f.category in [1, 9, 12, 14, 17] else 1.0
        culture_boost = 0.90 + 0.25 * self.state.culture_index if f.category in [6, 7, 8, 15] else 1.0
        social_boost = 0.90 + 0.25 * self.state.social_index if f.category == 18 else 1.0
        health_boost = 0.90 + 0.20 * self.state.health_index if f.category in [18, 19] else 1.0
        crisis_drag = self._crisis_drag_for_category(f.category)

        production_base = labor_units * f.productivity * f.technology * rule["labor_intensity"]
        capital_factor = math.sqrt(max(1.0, f.capital) / 1000.0)
        knowledge_factor = 0.75 + 0.40 * avg_education * rule["knowledge_intensity"]
        skill_factor = 0.80 + 0.30 * avg_skill + 0.15 * avg_health
        stochastic = self.rng.uniform(0.86, 1.14)
        output = production_base * capital_factor * knowledge_factor * skill_factor * nature_drag * infra_boost
        output *= commons_boost * culture_boost * social_boost * health_boost * crisis_drag * stochastic
        output = max(0.0, output)

        quality = clamp(
            0.22 + 0.26 * f.technology + 0.16 * f.reputation + 0.18 * avg_skill + 0.14 * avg_education
            + 0.04 * self.state.regulation_index + self.rng.uniform(-0.04, 0.04),
            0.05,
            1.0,
        )
        # Kosten in Geld: Material, Energie, Daten/Wissen, Verwaltung.
        material_cost = output * rule["material_intensity"] * (18.0 + 0.05 * self.market.prices.get(4, 80.0))
        energy_cost = output * rule["energy_intensity"] * (10.0 + 0.05 * self.market.prices.get(13, 100.0))
        knowledge_cost = output * rule["knowledge_intensity"] * 5.0 * (1.20 - self.state.commons_index * 0.25)
        admin_cost = output * (2.0 + 2.0 * rule["risk"])
        input_cost = max(0.0, material_cost + energy_cost + knowledge_cost + admin_cost)

        carbon = output * rule["carbon_intensity"] * (1.15 - 0.35 * f.technology) * (1.10 - 0.15 * self.state.regulation_index)
        resource_use = output * (rule["material_intensity"] + 0.55 * rule["energy_intensity"])
        regeneration = 0.0
        if rule["carbon_intensity"] < 0:
            regeneration = output * abs(rule["carbon_intensity"]) * (1.0 + self.state.environment_program)
            carbon = min(0.0, carbon)
        externality = {"carbon": carbon, "resource_use": resource_use, "regeneration": regeneration}
        return output, quality, input_cost, externality

    def _expected_input_cost(self, f: Firm, employee_count: int) -> float:
        rule = CATEGORY_INFO[f.category]
        return max(40.0, employee_count * (16.0 * rule["material_intensity"] + 10.0 * rule["energy_intensity"] + 7.0 * rule["knowledge_intensity"]))

    def _category_subsidy(self, category: int, output: float, quality: float) -> float:
        if output <= 0:
            return 0.0
        rule = CATEGORY_INFO[category]
        # Staat fördert besonders öffentliche, soziale, regenerative und wissensintensive Kategorien.
        base = output * quality * rule["subsidy_weight"] * 2.8
        # In Deflation/Arbeitslosigkeit stärker, bei hoher Inflation zurückhaltender.
        macro = clamp(1.0 + self.last_unemployment * 1.5 - max(0.0, self.last_inflation - 0.03) * 3.0, 0.25, 1.75)
        return base * macro

    # ------------------------------------------------------------------
    # Markt, Konsum, Außenhandel
    # ------------------------------------------------------------------

    def _household_consumption(self) -> None:
        for h in self.households.values():
            # Haushalte halten eine Sicherheitsreserve; bei hoher Unsicherheit konsumieren sie weniger.
            reserve = 120.0 + 120.0 * (1.0 - h.trust) + 60.0 * h.care_need
            propensity = clamp(0.58 + 0.16 * h.trust - 0.05 * (h.unemployment_ticks > 1), 0.35, 0.86)
            budget = max(0.0, (h.money - reserve) * propensity)
            if budget <= 1.0:
                continue
            weights = self._household_need_weights(h)
            cats = list(weights.keys())
            # Reihenfolge: Grundbedarf zuerst, dann Bildung/Kultur/Reparatur.
            cats.sort(key=lambda k: weights[k], reverse=True)
            for category in cats:
                if budget <= 0.5:
                    break
                price = self.market.prices[category]
                allocation = budget * weights[category]
                desired_qty = allocation / max(1.0, price)
                if desired_qty <= 0.001:
                    continue
                spent, qty, avg_quality = self._purchase_from_market(h.id, category, desired_qty, budget, "haushaltskonsum")
                if spent > 0:
                    h.money -= spent
                    budget -= spent
                    h.last_consumption[category] = h.last_consumption.get(category, 0.0) + qty
                    self._apply_consumption_benefit(h, category, qty, avg_quality, spent)

    def _household_need_weights(self, h: Household) -> Dict[int, float]:
        weights: Dict[int, float] = {}
        # Grundbedarf: Kategorie 19. Niedrige Gesundheit erhöht Bedarf.
        weights[19] = 0.36 + 0.10 * (1.0 - h.health)
        # Solidarität/Pflege: Kategorie 18. Care-Need erhöht Bedarf.
        weights[18] = 0.14 + 0.18 * h.care_need + 0.05 * (1.0 - h.trust)
        # Infrastruktur/Energie und Marktleistungen.
        weights[13] = 0.10 + 0.06 * (1.0 - self.state.infrastructure_index)
        weights[10] = 0.04
        # Bildung und Meta-Intelligenz.
        weights[17] = 0.10 + 0.13 * (1.0 - h.education)
        # Kultur, Bild, kreative Formung, Ausdrucksintensität.
        weights[7] = 0.05 + 0.07 * h.culture_pref
        weights[8] = 0.06 + 0.05 * h.culture_pref
        weights[6] = 0.03 + 0.03 * h.culture_pref
        # Transformation/Reparatur spart Ressourcen.
        weights[16] = 0.05 + 0.04 * (1.0 - self.environment.nature_capital)
        # Bewertung/Orientierung/Forschung klein, aber vorhanden.
        weights[12] = 0.025
        weights[9] = 0.020
        weights[1] = 0.020 + 0.03 * h.education
        total = sum(weights.values())
        return {k: v / total for k, v in weights.items()}

    def _purchase_from_market(self, buyer_id: str, category: int, desired_qty: float, max_budget: float, purpose: str) -> Tuple[float, float, float]:
        self.market.demand[category] += desired_qty
        remaining = desired_qty
        spent_total = 0.0
        qty_total = 0.0
        quality_total = 0.0
        sellers = [f for f in self.firms.values() if (not f.failed) and f.category == category and f.inventory > 0.0001]
        # Bessere Reputation/Qualität zuerst, aber Marktpreis bleibt zentral.
        sellers.sort(key=lambda f: (f.inventory_quality, f.reputation, -f.market_power), reverse=True)
        for f in sellers:
            if remaining <= 0.0001 or max_budget - spent_total <= 0.5:
                break
            unit_price = self.market.prices[category] * (0.88 + 0.20 * f.inventory_quality + 0.04 * f.market_power)
            available_qty = f.inventory
            affordable_qty = max(0.0, (max_budget - spent_total) / max(1.0, unit_price * (1.0 + self.state.vat_rate)))
            qty = min(remaining, available_qty, affordable_qty)
            if qty <= 0:
                continue
            gross = qty * unit_price
            vat = gross * self.state.vat_rate
            amount = gross + vat
            f.inventory -= qty
            f.money += gross
            f.profit += gross
            self.state.money += vat
            self.state.last_tax_revenue += vat
            spent_total += amount
            qty_total += qty
            quality_total += qty * f.inventory_quality
            self.market.sold[category] += qty
            self.market.turnover[category] += amount
            self.ledger.add(self.tick, "kauf", buyer_id, f.id, gross, category, purpose)
            self.ledger.add(self.tick, "steuer", buyer_id, self.state.id, vat, category, "Umsatzsteuer")
            remaining -= qty

        # Import, falls nicht genug Angebot vorhanden ist.
        if self.foreign_trade_enabled and remaining > 0.0001 and category in IMPORTABLE_CATEGORIES and max_budget - spent_total > 1.0:
            world = self.foreign.world_prices.get(category, self.market.prices[category])
            unit_price = world * (1.02 + self.state.tariff_rate)
            affordable_qty = max(0.0, (max_budget - spent_total) / max(1.0, unit_price))
            qty = min(remaining, affordable_qty)
            if qty > 0:
                tariff = qty * world * self.state.tariff_rate
                amount = qty * unit_price
                self.foreign.money += amount - tariff
                self.state.money += tariff
                self.state.last_tax_revenue += tariff
                spent_total += amount
                qty_total += qty
                quality = 0.58 + 0.08 * self.rng.random()
                quality_total += qty * quality
                self.foreign.import_volume += qty * world
                self.market.sold[category] += qty
                self.market.turnover[category] += amount
                self.ledger.add(self.tick, "import", buyer_id, self.foreign.id, amount - tariff, category, purpose)
                self.ledger.add(self.tick, "zoll", buyer_id, self.state.id, tariff, category, "Importzoll")

        avg_quality = safe_div(quality_total, qty_total, 0.50)
        return spent_total, qty_total, avg_quality

    def _apply_consumption_benefit(self, h: Household, category: int, qty: float, quality: float, spent: float) -> None:
        rule = CATEGORY_INFO[category]
        base_utility = qty * quality * rule["utility_factor"] * 12.0
        # Abnehmender Grenznutzen bei sehr viel Konsum.
        base_utility = 18.0 * math.log1p(max(0.0, base_utility) / 18.0)
        h.utility += base_utility
        if category == 19:
            h.health = clamp(h.health + 0.006 * quality * qty, 0.02, 1.0)
            h.trust = clamp(h.trust + 0.002 * quality, 0.02, 1.0)
        elif category == 18:
            h.health = clamp(h.health + 0.005 * quality * qty, 0.02, 1.0)
            h.trust = clamp(h.trust + 0.012 * quality * qty, 0.02, 1.0)
            h.care_need = clamp(h.care_need - 0.010 * quality * qty, 0.0, 1.0)
        elif category == 17:
            h.education = clamp(h.education + 0.010 * quality * qty, 0.02, 1.0)
            h.skill = clamp(h.skill + 0.006 * quality * qty, 0.02, 1.0)
        elif category in [7, 8, 6]:
            h.attention = clamp(h.attention + 0.004 * quality * qty, 0.02, 1.0)
            h.trust = clamp(h.trust + 0.003 * quality * h.culture_pref, 0.02, 1.0)
        elif category == 13:
            h.health = clamp(h.health + 0.003 * quality * qty, 0.02, 1.0)
        elif category == 16:
            # Reparatur/Transformation macht Haushalte widerstandsfähiger.
            h.trust = clamp(h.trust + 0.004 * quality * qty, 0.02, 1.0)
        elif category in [1, 9, 12]:
            h.education = clamp(h.education + 0.003 * quality * qty, 0.02, 1.0)

    def _foreign_trade_exports(self) -> None:
        if not self.foreign_trade_enabled:
            return
        for f in self.firms.values():
            if f.failed or f.inventory <= 0.1:
                continue
            category = f.category
            world_price = self.foreign.world_prices.get(category, self.market.prices[category])
            domestic = self.market.prices[category]
            # Export, wenn Weltpreis attraktiv oder Lager übervoll.
            if world_price > domestic * 1.03 or f.inventory > 30.0:
                qty = min(f.inventory * self.rng.uniform(0.05, 0.25), f.inventory)
                amount = qty * world_price * (0.92 + 0.14 * f.inventory_quality)
                f.inventory -= qty
                f.money += amount
                f.profit += amount
                self.foreign.money -= min(self.foreign.money, amount)
                self.foreign.export_volume += amount
                self.market.sold[category] += qty
                self.market.turnover[category] += amount
                self.ledger.add(self.tick, "export", self.foreign.id, f.id, amount, category, "Außenhandel Export")

        # Weltpreise driften leicht.
        for k in self.foreign.world_prices:
            drift = self.rng.gauss(0.0, 0.012)
            self.foreign.world_prices[k] = clamp(self.foreign.world_prices[k] * math.exp(drift), CATEGORY_INFO[k]["base_price"] * 0.45, CATEGORY_INFO[k]["base_price"] * 3.5)

    # ------------------------------------------------------------------
    # Banken, Geld, Kredit
    # ------------------------------------------------------------------

    def _request_credit(self, firm: Firm, amount: float, reason: str) -> bool:
        amount = float(max(0.0, amount))
        if amount <= 1.0:
            return False
        banks = list(self.banks.values())
        if not banks:
            return False
        # Risiko: Verschuldung, Reputation, Kategorie-Risiko, Zentralbankzins.
        risk = CATEGORY_INFO[firm.category]["risk"] + 0.18 * safe_div(firm.debt, firm.capital + 1.0, 0.0) + 0.12 * (1.0 - firm.reputation) + 0.5 * self.central_bank.policy_rate
        feasible = [b for b in banks if b.risk_appetite >= risk * 0.65 and b.money > amount * b.capital_ratio]
        if not feasible:
            return False
        bank = max(feasible, key=lambda b: b.money * b.risk_appetite)
        rate = clamp(self.central_bank.policy_rate + 0.025 + risk * 0.08, 0.01, 0.22)
        lid = self.new_loan_id_value()
        loan = Loan(lid, bank.id, firm.id, amount, amount, rate, self.tick, self.tick + self.rng.randint(8, 24))
        bank.loans[lid] = loan
        bank.money -= amount * bank.capital_ratio
        firm.money += amount
        firm.debt += amount
        self.central_bank.money_supply += amount * (1.0 - bank.capital_ratio)
        self.new_contract("kredit", [bank.id, firm.id], firm.category, amount, {"zins": rate, "grund": reason, "faellig": loan.due_tick})
        self.ledger.add(self.tick, "kredit", bank.id, firm.id, amount, firm.category, reason)
        return True

    def _loan_service(self) -> None:
        for bank in self.banks.values():
            for loan in list(bank.loans.values()):
                if loan.status != "aktiv":
                    continue
                firm = self.firms.get(loan.borrower_id)
                if firm is None or firm.failed:
                    loan.status = "ausfall"
                    bank.defaults += 1
                    continue
                interest = loan.outstanding * loan.interest_rate / 4.0
                principal_due = 0.0
                if self.tick >= loan.due_tick:
                    principal_due = loan.outstanding * 0.35
                else:
                    principal_due = loan.outstanding * 0.04
                due = interest + principal_due
                if firm.money >= due:
                    firm.money -= due
                    bank.money += due
                    firm.debt = max(0.0, firm.debt - principal_due)
                    loan.outstanding = max(0.0, loan.outstanding - principal_due)
                    firm.profit -= interest
                    self.ledger.add(self.tick, "kreditdienst", firm.id, bank.id, due, firm.category, "Zins und Tilgung")
                    if loan.outstanding <= 1.0:
                        loan.status = "getilgt"
                else:
                    # Teilzahlung oder Ausfall.
                    paid = max(0.0, firm.money * 0.60)
                    if paid > 0:
                        firm.money -= paid
                        bank.money += paid
                        interest_paid = min(interest, paid)
                        principal_paid = max(0.0, paid - interest_paid)
                        loan.outstanding = max(0.0, loan.outstanding - principal_paid)
                        firm.debt = max(0.0, firm.debt - principal_paid)
                        self.ledger.add(self.tick, "kreditdienst", firm.id, bank.id, paid, firm.category, "Teilzahlung")
                    if self.tick > loan.due_tick + 4 and firm.money < due * 0.25:
                        loan.status = "ausfall"
                        bank.defaults += 1
                        loss = loan.outstanding * 0.55
                        bank.money -= min(bank.money, loss * 0.25)
                        firm.debt = max(0.0, firm.debt - loan.outstanding)
                        firm.reputation = clamp(firm.reputation - 0.15, 0.02, 1.0)
                        self.ledger.add(self.tick, "ausfall", firm.id, bank.id, loan.outstanding, firm.category, "Kreditausfall")

    # ------------------------------------------------------------------
    # Steuern, Insolvenzen, Innovation
    # ------------------------------------------------------------------

    def _corporate_tax_and_failures(self) -> None:
        for f in self.firms.values():
            if f.failed:
                continue
            if f.profit > 0:
                tax = f.profit * self.state.corporate_tax_rate
                if f.money >= tax:
                    f.money -= tax
                    self.state.money += tax
                    self.state.last_tax_revenue += tax
                    self.ledger.add(self.tick, "steuer", f.id, self.state.id, tax, f.category, "Gewinnsteuer")
            # Insolvenz/Restrukturierung.
            if f.money < -100.0 or (f.money < 25.0 and f.debt > f.capital * 1.45):
                if self.rng.random() < 0.55:
                    f.failed = True
                    f.employees = []
                    f.inventory *= 0.35
                    f.reputation = clamp(f.reputation - 0.30, 0.01, 1.0)
                    self.ledger.add(self.tick, "insolvenz", f.id, self.state.id, 0.0, f.category, "Firma scheidet aus")
                else:
                    # Restrukturierung: Staat/Banken erlauben Fortbestand, aber Reputation sinkt.
                    haircut = min(f.debt * 0.25, max(0.0, f.debt - f.capital * 0.6))
                    if haircut > 0:
                        f.debt -= haircut
                        f.reputation = clamp(f.reputation - 0.12, 0.01, 1.0)
                        self.ledger.add(self.tick, "restrukturierung", f.id, "BANKEN", haircut, f.category, "Schuldenschnitt")
            # Marktmacht-Regulierung: vor allem K5, K10, K12, K13, K17.
            if CATEGORY_INFO[f.category]["monopoly_risk"] > 0.65:
                f.market_power = clamp(f.market_power - 0.01 * self.state.regulation_index + 0.002 * f.reputation, 0.0, 1.0)

    def _innovation_phase(self) -> None:
        total_research = self.market.turnover.get(1, 0.0) + self.market.turnover.get(14, 0.0) + self.market.turnover.get(17, 0.0)
        public_research = self.state.commons_index + self.state.education_index
        spawned = False
        for f in list(self.firms.values()):
            if f.failed:
                continue
            rule = CATEGORY_INFO[f.category]
            # Firmen investieren einen kleinen Anteil ihres Geldes in Verbesserung.
            invest_rate = 0.006 + 0.012 * rule["innovation_affinity"]
            if f.money > 500.0:
                investment = f.money * invest_rate
                f.money -= investment
                f.profit -= investment
            else:
                investment = 0.0
            chance = 0.010 + 0.020 * rule["innovation_affinity"] + 0.000004 * total_research + 0.010 * public_research
            chance += 0.000015 * investment
            if self.rng.random() < clamp(chance, 0.0, 0.18):
                tech_gain = self.rng.uniform(0.005, 0.045) * (0.7 + rule["innovation_affinity"])
                f.technology = clamp(f.technology + tech_gain, 0.20, 1.80)
                f.productivity = clamp(f.productivity + tech_gain * 0.45, 0.20, 1.80)
                f.reputation = clamp(f.reputation + tech_gain * 0.25, 0.02, 1.0)
                coin = self.new_coin(
                    tick=self.tick,
                    owner_id=f.id,
                    category=14 if f.category in [1, 11, 14, 17] else f.category,
                    main_function="Synergie, Produktivität und zukünftige Münzfähigkeit maximieren",
                    constraint="Budget, Risiko, Gemeinwohl, Monopolgrenzen",
                    inputs={"forschungsausgaben": investment, "commons": self.state.commons_index},
                    outputs={"technologiegewinn": tech_gain},
                    quality=clamp(f.technology / 1.8, 0.05, 1.0),
                    price=self.market.prices.get(f.category, 100.0),
                    public_value=tech_gain * 100.0 * rule["public_weight"],
                    externality={"carbon": 0.0, "resource_use": 0.0, "regeneration": 0.0},
                    risk=rule["risk"],
                    status=CoinStatus.TRANSFORMED.value,
                    description="Innovation / Fusion von Ideen",
                )
                coin.evaluate(self.environment.nature_capital, self.average_trust())
                self.ledger.add(self.tick, "innovation", f.id, coin.id, coin.score, coin.category, "Technologiegewinn")
                # In seltenen Fällen entsteht eine neue Firma aus K11/K14/K17.
                if not spawned and f.category in [11, 14, 17] and self.rng.random() < 0.025:
                    self._spawn_firm_from_innovation(f)
                    spawned = True

    def _spawn_firm_from_innovation(self, parent: Firm) -> None:
        new_category = weighted_choice(
            self.rng,
            list(CATEGORY_INFO.keys()),
            [CATEGORY_INFO[k]["innovation_affinity"] + 0.2 for k in CATEGORY_INFO],
        )
        fid = make_id("F", len(self.firms) + 1)
        f = Firm(
            id=fid,
            name="Spin-off %s K%02d" % (fid, new_category),
            category=new_category,
            money=900.0 + 400.0 * self.rng.random(),
            capital=700.0 + 600.0 * self.rng.random(),
            technology=clamp(parent.technology * self.rng.uniform(0.85, 1.10), 0.20, 1.80),
            reputation=clamp(parent.reputation * self.rng.uniform(0.70, 0.95), 0.05, 0.90),
            productivity=clamp(parent.productivity * self.rng.uniform(0.75, 1.05), 0.20, 1.60),
            wage_offer=max(self.state.minimum_wage, parent.wage_offer * self.rng.uniform(0.80, 1.05)),
            inventory=1.0,
            inventory_quality=0.50,
            market_power=0.02,
        )
        self.firms[fid] = f
        self.ledger.add(self.tick, "gruendung", parent.id, fid, f.money, new_category, "Spin-off durch Innovation")

    # ------------------------------------------------------------------
    # Gesellschaft, Gesundheit, Umwelt
    # ------------------------------------------------------------------

    def _social_and_health_dynamics(self) -> None:
        nature = self.environment.nature_capital
        social = self.state.social_index
        health_public = self.state.health_index
        education_public = self.state.education_index
        for h in self.households.values():
            # Gesundheit und Bildung verändern sich langsam.
            h.health = clamp(h.health + 0.003 * (health_public - 0.55) + 0.002 * (nature - 0.75) - 0.002 * h.care_need, 0.02, 1.0)
            h.education = clamp(h.education + 0.0025 * (education_public - h.education) + 0.0008 * h.last_consumption.get(17, 0.0), 0.02, 1.0)
            h.skill = clamp(h.skill + 0.0015 * (h.education - h.skill) + 0.001 * (1 if h.employed_by else -0.4), 0.02, 1.0)
            h.care_need = clamp(h.care_need + 0.002 * (1.0 - h.health) - 0.004 * h.last_consumption.get(18, 0.0), 0.0, 1.0)
            if h.unemployment_ticks > 3:
                h.health = clamp(h.health - 0.003, 0.02, 1.0)
                h.utility -= 0.5
            h.trust = clamp(h.trust + 0.002 * (social - 0.55) + 0.001 * (self.central_bank.credibility - 0.65), 0.02, 1.0)

    def _environmental_regeneration(self) -> None:
        env_spending = self.state.last_spending * 0.08
        self.environment.regenerate(self.state.environment_program, env_spending)

    # ------------------------------------------------------------------
    # Preise, Zentralbank, Kennzahlen
    # ------------------------------------------------------------------

    def _update_market_prices_and_policy(self) -> None:
        old_index = self.market.previous_price_index()
        self.market.update_prices(self.central_bank.policy_rate, self.state.regulation_index)
        new_index = self.market.price_index()
        inflation = safe_div(new_index - old_index, old_index, 0.0)
        unemployment = self._unemployment_rate()
        nature_stress = clamp(1.0 - self.environment.nature_capital, 0.0, 1.0)
        self.central_bank.update_policy(inflation, unemployment, nature_stress)
        self.last_inflation = inflation
        self.last_unemployment = unemployment
        self.central_bank.money_supply = self.total_money() + self._total_outstanding_credit_money()

    def _collect_metrics(self) -> None:
        transaction_value = sum(self.market.turnover.values())
        output_value = self.last_output_value
        bmp = transaction_value + 0.65 * output_value + self.foreign.export_volume - self.foreign.import_volume * 0.4
        incomes = [h.money for h in self.households.values()]
        inequality = gini(incomes)
        unemployment = self._unemployment_rate()
        avg_utility = safe_div(sum(h.utility for h in self.households.values()), len(self.households), 0.0)
        avg_health = safe_div(sum(h.health for h in self.households.values()), len(self.households), 0.0)
        avg_education = safe_div(sum(h.education for h in self.households.values()), len(self.households), 0.0)
        avg_trust = self.average_trust()
        nature = self.environment.nature_capital
        culture = self.state.culture_index
        social = self.state.social_index
        risk = self._systemic_risk()
        # Münzwohlstand: echte Zielerfüllung, nicht bloß Umsatz.
        mw = (
            0.45 * bmp
            + 1200.0 * avg_utility
            + 9000.0 * avg_health
            + 8000.0 * avg_education
            + 6500.0 * avg_trust
            + 5000.0 * culture
            + 7000.0 * social
            + 10000.0 * nature
            - 9000.0 * inequality
            - 12000.0 * unemployment
            - 6000.0 * abs(self.last_inflation)
            - 10000.0 * risk
        )
        self.last_gdp = bmp
        self.last_mw = mw
        by_cat_output = {str(k): self.market.supply.get(k, 0.0) for k in CATEGORY_INFO}
        by_cat_turnover = {str(k): self.market.turnover.get(k, 0.0) for k in CATEGORY_INFO}
        metric = {
            "tick": self.tick,
            "bmp": bmp,
            "mw": mw,
            "transaction_value": transaction_value,
            "output_value": output_value,
            "inflation": self.last_inflation,
            "policy_rate": self.central_bank.policy_rate,
            "unemployment": unemployment,
            "inequality_gini": inequality,
            "avg_utility": avg_utility,
            "avg_health": avg_health,
            "avg_education": avg_education,
            "avg_trust": avg_trust,
            "nature_capital": nature,
            "biodiversity": self.environment.biodiversity,
            "emissions": self.environment.current_emissions,
            "carbon_stock": self.environment.carbon_stock,
            "state_debt": self.state.debt,
            "state_money": self.state.money,
            "tax_revenue": self.state.last_tax_revenue,
            "state_spending": self.state.last_spending,
            "state_deficit": self.state.last_deficit,
            "money_supply": self.central_bank.money_supply,
            "credit_outstanding": self._total_outstanding_credit_money(),
            "imports": self.foreign.import_volume,
            "exports": self.foreign.export_volume,
            "active_firms": len([f for f in self.firms.values() if not f.failed]),
            "failed_firms": len([f for f in self.firms.values() if f.failed]),
            "coins_created": len(self.coins),
            "systemic_risk": risk,
            "price_index": self.market.price_index(),
            "category_output": by_cat_output,
            "category_turnover": by_cat_turnover,
        }
        self.metrics.append(metric)

    # ------------------------------------------------------------------
    # Schocks und Krisen
    # ------------------------------------------------------------------

    def _maybe_apply_shock(self) -> None:
        if self.shock_frequency <= 0:
            return
        if self.rng.random() >= self.shock_frequency:
            return
        shock_type = weighted_choice(
            self.rng,
            ["energie", "vertrauen", "innovation", "gesundheit", "umwelt", "nachfrage", "finanz"],
            [0.16, 0.14, 0.18, 0.12, 0.18, 0.16, 0.10],
        )
        if shock_type == "energie":
            self.crisis_flags["energie"] = self.rng.randint(3, 8)
            for k in [4, 13, 15, 19]:
                self.market.prices[k] *= self.rng.uniform(1.03, 1.12)
            msg = "Energieschock: Produktion und Infrastruktur werden teurer."
        elif shock_type == "vertrauen":
            self.crisis_flags["vertrauen"] = self.rng.randint(2, 6)
            for h in self.households.values():
                h.trust = clamp(h.trust - self.rng.uniform(0.01, 0.05), 0.02, 1.0)
            msg = "Vertrauensschock: Haushalte und Märkte werden vorsichtiger."
        elif shock_type == "innovation":
            self.crisis_flags["innovation"] = self.rng.randint(3, 10)
            # Innovationsboom: Commons und K11/K14 profitieren.
            self.state.commons_index = clamp(self.state.commons_index + 0.02, 0.10, 1.25)
            msg = "Innovationsimpuls: Stilbruch und Fusion erzeugen neue Möglichkeiten."
        elif shock_type == "gesundheit":
            self.crisis_flags["gesundheit"] = self.rng.randint(3, 8)
            for h in self.households.values():
                h.health = clamp(h.health - self.rng.uniform(0.005, 0.025), 0.02, 1.0)
            msg = "Gesundheitsschock: Pflege und Solidarität werden wichtiger."
        elif shock_type == "umwelt":
            self.crisis_flags["umwelt"] = self.rng.randint(4, 10)
            self.environment.nature_capital = clamp(self.environment.nature_capital - self.rng.uniform(0.01, 0.04), 0.05, 1.15)
            msg = "Umweltschock: Naturkapital sinkt, Kategorie 16 gewinnt Bedeutung."
        elif shock_type == "nachfrage":
            self.crisis_flags["nachfrage"] = self.rng.randint(3, 7)
            msg = "Nachfrageschock: Haushalte verschieben Konsum in Grundbedarf."
        else:
            self.crisis_flags["finanz"] = self.rng.randint(3, 7)
            self.central_bank.policy_rate = clamp(self.central_bank.policy_rate + self.rng.uniform(0.005, 0.025), 0.002, 0.16)
            msg = "Finanzschock: Kredit wird knapper."
        self.event_log.append("t=%d: %s" % (self.tick, msg))
        self.ledger.add(self.tick, "schock", "SYSTEM", "ALLE", 0.0, None, msg)

    def _decrement_crises(self) -> None:
        for key in list(self.crisis_flags.keys()):
            self.crisis_flags[key] -= 1
            if self.crisis_flags[key] <= 0:
                del self.crisis_flags[key]

    def _crisis_drag_for_category(self, category: int) -> float:
        drag = 1.0
        if "energie" in self.crisis_flags and category in [4, 5, 13, 15, 19]:
            drag *= 0.88
        if "vertrauen" in self.crisis_flags and category in [6, 8, 10, 11, 14]:
            drag *= 0.90
        if "gesundheit" in self.crisis_flags and category not in [18, 19, 17]:
            drag *= 0.94
        if "umwelt" in self.crisis_flags and category in [4, 13, 15, 19]:
            drag *= 0.92
        if "innovation" in self.crisis_flags and category in [1, 11, 14, 17]:
            drag *= 1.12
        if "nachfrage" in self.crisis_flags and category not in [18, 19, 13]:
            drag *= 0.93
        if "finanz" in self.crisis_flags and category in [5, 11, 14, 17]:
            drag *= 0.90
        return drag

    # ------------------------------------------------------------------
    # Analysehilfen
    # ------------------------------------------------------------------

    def _demand_pressure_by_category(self) -> Dict[int, float]:
        pressures = {}
        for k in CATEGORY_INFO:
            # Aus letztem Turnover und Lagerbestand grob ableiten.
            active_firms = [f for f in self.firms.values() if (not f.failed) and f.category == k]
            inventory = sum(f.inventory for f in active_firms)
            base_need = NEED_WEIGHTS.get(k, 0.12) * len(self.households) * 0.25
            pressure = safe_div(base_need + self.market.turnover.get(k, 0.0) / max(1.0, self.market.prices[k]), 1.0 + inventory, 1.0)
            pressures[k] = clamp(pressure, 0.35, 2.20)
        return pressures

    def _unemployment_rate(self) -> float:
        if not self.households:
            return 0.0
        unemployed = len([h for h in self.households.values() if h.employed_by is None and h.health > 0.20])
        labor_force = len([h for h in self.households.values() if h.health > 0.20])
        return safe_div(unemployed, labor_force, 0.0)

    def average_trust(self) -> float:
        return safe_div(sum(h.trust for h in self.households.values()), len(self.households), 0.55)

    def total_money(self) -> float:
        total = self.state.money + self.foreign.money
        total += sum(h.money for h in self.households.values())
        total += sum(f.money for f in self.firms.values() if not f.failed)
        total += sum(b.money for b in self.banks.values())
        return total

    def _total_outstanding_credit_money(self) -> float:
        total = 0.0
        for bank in self.banks.values():
            for loan in bank.loans.values():
                if loan.status == "aktiv":
                    total += loan.outstanding
        return total

    def _systemic_risk(self) -> float:
        credit = self._total_outstanding_credit_money()
        money = max(1.0, self.total_money())
        bank_defaults = sum(b.defaults for b in self.banks.values())
        active_loans = sum(1 for b in self.banks.values() for l in b.loans.values() if l.status == "aktiv")
        default_pressure = safe_div(bank_defaults, max(1, bank_defaults + active_loans), 0.0)
        monopoly_pressure = self._monopoly_pressure()
        ecological_pressure = clamp(1.0 - self.environment.nature_capital, 0.0, 1.0)
        inflation_pressure = clamp(abs(self.last_inflation) * 4.0, 0.0, 1.0)
        return clamp(0.25 * safe_div(credit, money, 0.0) + 0.20 * default_pressure + 0.22 * monopoly_pressure + 0.23 * ecological_pressure + 0.10 * inflation_pressure, 0.0, 1.0)

    def _monopoly_pressure(self) -> float:
        vals = []
        for k in CATEGORY_INFO:
            firms = [f for f in self.firms.values() if (not f.failed) and f.category == k]
            if not firms:
                vals.append(1.0)
                continue
            inventories = [max(0.0, f.inventory) + 1.0 for f in firms]
            total = sum(inventories)
            hhi = sum((x / total) ** 2 for x in inventories)
            vals.append(hhi * CATEGORY_INFO[k]["monopoly_risk"])
        return clamp(safe_div(sum(vals), len(vals), 0.0), 0.0, 1.0)

    # ------------------------------------------------------------------
    # Export
    # ------------------------------------------------------------------

    def export(self, outdir: str) -> None:
        if not outdir:
            return
        if not os.path.isdir(outdir):
            os.makedirs(outdir)
        self._export_metrics(os.path.join(outdir, "metrics.csv"))
        self._export_ledger(os.path.join(outdir, "ledger.csv"))
        self._export_agents(os.path.join(outdir, "agents.json"))
        self._export_coins(os.path.join(outdir, "coins.json"))
        self._export_contracts(os.path.join(outdir, "contracts.json"))
        self._export_summary(os.path.join(outdir, "summary.md"))

    def _export_metrics(self, path: str) -> None:
        fields = [
            "tick", "bmp", "mw", "transaction_value", "output_value", "inflation", "policy_rate", "unemployment",
            "inequality_gini", "avg_utility", "avg_health", "avg_education", "avg_trust", "nature_capital",
            "biodiversity", "emissions", "carbon_stock", "state_debt", "state_money", "tax_revenue",
            "state_spending", "state_deficit", "money_supply", "credit_outstanding", "imports", "exports",
            "active_firms", "failed_firms", "coins_created", "systemic_risk", "price_index",
        ]
        with open(path, "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for m in self.metrics:
                w.writerow({k: m.get(k, "") for k in fields})

    def _export_ledger(self, path: str) -> None:
        with open(path, "w", newline="", encoding="utf-8") as f:
            fields = ["tick", "event", "source", "target", "amount", "category", "description"]
            w = csv.DictWriter(f, fieldnames=fields)
            w.writeheader()
            for e in self.ledger.entries:
                w.writerow(asdict(e))

    def _export_agents(self, path: str) -> None:
        data = {
            "households": [asdict(h) for h in self.households.values()],
            "firms": [asdict(f) for f in self.firms.values()],
            "banks": [self._bank_as_dict(b) for b in self.banks.values()],
            "state": asdict(self.state),
            "central_bank": asdict(self.central_bank),
            "environment": asdict(self.environment),
            "foreign": asdict(self.foreign),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    def _bank_as_dict(self, b: Bank) -> Dict[str, Any]:
        d = asdict(b)
        d["loans"] = [asdict(l) for l in b.loans.values()]
        return d

    def _export_coins(self, path: str) -> None:
        # Bei langen Läufen kann die Liste groß werden; trotzdem vollständig exportieren.
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(c) for c in self.coins], f, ensure_ascii=False, indent=2)

    def _export_contracts(self, path: str) -> None:
        with open(path, "w", encoding="utf-8") as f:
            json.dump([asdict(c) for c in self.contracts], f, ensure_ascii=False, indent=2)

    def _export_summary(self, path: str) -> None:
        last = self.metrics[-1] if self.metrics else {}
        top_turnover = []
        if last:
            ct = last.get("category_turnover", {})
            top_turnover = sorted([(int(k), v) for k, v in ct.items()], key=lambda x: x[1], reverse=True)[:8]
        with open(path, "w", encoding="utf-8") as f:
            f.write("# Zusammenfassung der Münzökonomie-Simulation\n\n")
            f.write("Version: `%s`  \n" % VERSION)
            f.write("Seed: `%s`  \n" % self.seed)
            f.write("Perioden: `%s`  \n\n" % self.tick)
            if last:
                f.write("## Endkennzahlen\n\n")
                f.write("| Kennzahl | Wert |\n|---|---:|\n")
                labels = [
                    ("Brutto-Münzprodukt BMP", "bmp"),
                    ("Münzwohlstand MW", "mw"),
                    ("Inflation letzte Periode", "inflation"),
                    ("Arbeitslosigkeit", "unemployment"),
                    ("Ungleichheit Gini", "inequality_gini"),
                    ("Naturkapital", "nature_capital"),
                    ("Durchschnittliche Gesundheit", "avg_health"),
                    ("Durchschnittliche Bildung", "avg_education"),
                    ("Durchschnittliches Vertrauen", "avg_trust"),
                    ("Geldmenge", "money_supply"),
                    ("Kreditvolumen", "credit_outstanding"),
                    ("Staatsschuld", "state_debt"),
                    ("Systemisches Risiko", "systemic_risk"),
                ]
                for label, key in labels:
                    val = last.get(key, 0.0)
                    if key in ["inflation", "unemployment", "inequality_gini", "nature_capital", "avg_health", "avg_education", "avg_trust", "systemic_risk"]:
                        f.write("| %s | %.4f |\n" % (label, val))
                    else:
                        f.write("| %s | %.2f |\n" % (label, val))
                f.write("\n## Umsatzstärkste Kategorien am Ende\n\n")
                f.write("| Kategorie | Sektor | Umsatz |\n|---:|---|---:|\n")
                for cat, value in top_turnover:
                    f.write("| %d | %s | %.2f |\n" % (cat, CATEGORY_INFO[cat]["short"], value))
            f.write("\n## Ereignisse\n\n")
            if self.event_log:
                for msg in self.event_log[-30:]:
                    f.write("- %s\n" % msg)
            else:
                f.write("Keine Schocks protokolliert.\n")
            f.write("\n## Kategorien\n\n")
            f.write(category_markdown_table())


# ---------------------------------------------------------------------------
# Ausgabe/CLI
# ---------------------------------------------------------------------------


def category_markdown_table() -> str:
    lines = ["| Nr. | Kurzname | Wirtschaftssektor | Hauptfunktion | Nebenbedingung |", "|---:|---|---|---|---|"]
    for k in sorted(CATEGORY_INFO):
        info = CATEGORY_INFO[k]
        lines.append("| %d | %s | %s | %s | %s |" % (k, info["short"], info["sector"], info["main"], info["constraint"]))
    return "\n".join(lines) + "\n"


def print_categories() -> None:
    print(category_markdown_table())


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description="Münzökonomie: Wirtschaftssystem aus Münzen/Optimierungsproblemen in PyPy3")
    p.add_argument("--years", type=int, default=12, help="Anzahl Jahre. Ein Jahr besteht aus --periods-per-year Perioden.")
    p.add_argument("--periods-per-year", type=int, default=4, help="Perioden pro Jahr, standardmäßig Quartale.")
    p.add_argument("--households", type=int, default=100, help="Anzahl Haushalte")
    p.add_argument("--firms-per-category", type=int, default=2, help="Unternehmen pro Kategorie")
    p.add_argument("--banks", type=int, default=2, help="Anzahl Geschäftsbanken")
    p.add_argument("--seed", type=int, default=42, help="Zufallsseed")
    p.add_argument("--out", type=str, default="muenzoekonomie_ergebnis", help="Ausgabeordner")
    p.add_argument("--quiet", action="store_true", help="Keine Fortschrittsausgabe")
    p.add_argument("--print-every", type=int, default=4, help="Alle n Perioden eine Zeile ausgeben")
    p.add_argument("--no-foreign", action="store_true", help="Außenhandel deaktivieren")
    p.add_argument("--shock-frequency", type=float, default=0.06, help="Wahrscheinlichkeit eines Schocks pro Periode")
    p.add_argument("--list-categories", action="store_true", help="Kategorientabelle anzeigen und beenden")
    return p


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)
    if args.list_categories:
        print_categories()
        return 0
    periods = max(1, int(args.years) * max(1, int(args.periods_per_year)))
    eco = Economy(
        seed=args.seed,
        households=args.households,
        firms_per_category=args.firms_per_category,
        banks=args.banks,
        foreign_trade=not args.no_foreign,
        shock_frequency=args.shock_frequency,
    )
    start = time.time()
    if not args.quiet:
        print("Münzökonomie %s – Start: %d Haushalte, %d Firmen, %d Perioden, Seed %d" % (
            VERSION, len(eco.households), len(eco.firms), periods, args.seed
        ))
    eco.run(periods, quiet=args.quiet, print_every=args.print_every)
    eco.export(args.out)
    if not args.quiet:
        last = eco.metrics[-1]
        print("\nFertig nach %.2fs. Ergebnisse in: %s" % (time.time() - start, args.out))
        print("Ende: BMP=%.1f MW=%.1f Inflation=%.2f%% Arbeitslosigkeit=%.1f%% Natur=%.2f" % (
            last["bmp"], last["mw"], 100 * last["inflation"], 100 * last["unemployment"], last["nature_capital"]
        ))
    return 0


if __name__ == "__main__":
    sys.exit(main())
