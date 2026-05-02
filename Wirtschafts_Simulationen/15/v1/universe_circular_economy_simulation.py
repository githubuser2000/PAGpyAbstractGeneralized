#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Universum-Kreislaufwirtschaft / Universe Circular Economy Simulation
====================================================================

PyPy3-compatible, dependency-free simulation of a cosmic circular economy.

Core ideas implemented:
- Currency as stacked for-loop distance through a planetary cycle.
- Earth-type planets use 20 stations; Vulcan-type planets use 22 stations.
- Goods are tracked as identities with cycle passports.
- Money is created by verified transformations, not by mere extraction.
- Waste becomes cycle debt until it is reintegrated.
- Markets, state policy, banks, taxes, repair subsidies, interplanetary trade,
  agents, events, inflation, soil fertility, microbes, water, heat and justice
  are simulated at an aggregate + identity-batch level.

Run example:
    pypy3 universe_circular_economy_simulation.py --seed 73 --ticks 60 --systems 2 \
        --planets-per-system 3 --agents-per-planet 45 --report-dir uce_report

The code intentionally uses only Python's standard library so that it runs on PyPy3.
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
# Utility functions
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


def weighted_choice(rng: random.Random, items: Sequence[Tuple[str, float]]) -> str:
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


def fmt(x: float, digits: int = 2) -> str:
    if abs(x) >= 1000000:
        return f"{x/1000000:.{digits}f}M"
    if abs(x) >= 1000:
        return f"{x/1000:.{digits}f}k"
    return f"{x:.{digits}f}"


# ---------------------------------------------------------------------------
# Station alphabet
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
    1: Station(1, "A", "Punkt", "point", "Befruchtung", "Fecundation", "origin",
               "Pollination, Befruchtung, Start einer neuen Identität.",
               "Pollination, fertilization, start of a new identity."),
    2: Station(2, "B", "Linie", "line", "Samen", "Seed", "plant",
               "Samen, Keimfähigkeit, gespeichertes Potenzial.",
               "Seed, germinability, stored potential."),
    3: Station(3, "C", "Dreieck", "triangle", "Keimling", "Seedling", "plant",
               "Keimling, Sprossen, erste Verwurzelung.",
               "Seedling, sprouts, first rooting."),
    4: Station(4, "D", "Quadrat", "square", "Wachstum", "Growth", "plant",
               "Grüne Pflanze, Biomasse, photosynthetischer Wert.",
               "Green plant, biomass, photosynthetic value."),
    5: Station(5, "E", "Pentagramm", "pentagram", "Dünger-Wachstum", "Fertilizer growth", "soil",
               "Dung, Dünger, Mist, Mulch, Holz, stärkeres Wachstum.",
               "Dung, fertilizer, manure, mulch, wood, stronger growth."),
    6: Station(6, "F", "Hexagramm", "hexagram", "Blüte", "Blossom", "plant",
               "Blume, Blüte, Reife- und Fortpflanzungszeichen.",
               "Flower, blossom, maturity and reproduction signal."),
    7: Station(7, "G", "Heptagramm", "heptagram", "Ernte", "Harvest", "food",
               "Herausreißen, Schneiden, Ernten, Erntegut.",
               "Pulling out, cutting, harvesting, crop."),
    8: Station(8, "H", "Oktagramm", "octagram", "Essen", "Eating", "food",
               "Essen, Füttern, Ernähren, Aufnahme durch Lebewesen.",
               "Eating, feeding, nurturing, intake by living beings."),
    9: Station(9, "I", "Nonagramm", "nonagram", "Fleisch/Wesen", "Flesh/creature", "body",
               "Fleisch, Tier, Mensch, Volk, Wesen, Körperaufbau.",
               "Flesh, animal, human, people, creature, body formation."),
    10: Station(10, "J", "Dekagramm", "decagram", "Einpassung", "Fitting-in", "ecology",
                "Einpassung in anderes Leben, ökologische Rolle.",
                "Fitting into other life, ecological role."),
    11: Station(11, "K", "Hendekagramm", "hendecagram", "Produktionskette", "Production chain", "production",
                "Nahrungskette und Produktionskette: Korn, Müller, Mehl, Bäcker, Brot, Markt, Konsum.",
                "Food chain and production chain: grain, miller, flour, baker, bread, market, consumption."),
    12: Station(12, "L", "Dodekagramm", "dodecagram", "Verdauung", "Digestion", "digestion",
                "Magen, Verdauung, Umwandlung von Nahrung in Körper und Reststoff.",
                "Stomach, digestion, conversion of food into body and residue."),
    13: Station(13, "M", "Triskaidekagramm", "triskaidecagram", "Gülle/Kot", "Slurry/excrement", "waste",
                "Gülle, Kot, organische Rückgabe, Mikrobenfutter.",
                "Slurry, feces, organic return, microbial food."),
    14: Station(14, "N", "Tetrakaidekagramm", "tetrakaidecagram", "Kreislaufwirtschaft", "Circular economy", "governance",
                "Tiere, Pflanzen, Mikroben, Erde, Wiederholung, Gesetze, Gerechtigkeit, Signale.",
                "Animals, plants, microbes, earth, repetition, laws, justice, signals."),
    15: Station(15, "O", "Pentadekagramm", "pentadecagram", "Zersetzung", "Decomposition", "microbes",
                "Degradation, Zersetzen, Auflösen, Rückführung.",
                "Degradation, decomposing, dissolving, return."),
    16: Station(16, "P", "Hexadekagramm", "hexadecagram", "Chemische Reaktion", "Chemical reaction", "chemistry",
                "Reaktion, Umwandlung, Elementwechsel, chemische Neuordnung.",
                "Reaction, transformation, elemental shift, chemical reordering."),
    17: Station(17, "Q", "Heptadekagramm", "heptadecagram", "Rückintegration", "Reintegration", "return",
                "Assimilation, Einbettung, in den Kreislauf zurückführen.",
                "Assimilation, embedding, return into the cycle."),
    18: Station(18, "R", "Oktadekagramm", "octadecagram", "Tod/Mikroben", "Death/microbes", "death",
                "Totes Leben, Mikrobenfutter, organische Restidentität.",
                "Dead life, microbial food, organic residual identity."),
    19: Station(19, "S", "Nonadekagramm", "nonadecagram", "Erde/Boden/Planet", "Earth/soil/planet", "planet",
                "Erde, Boden, Planet Erde, Standort der Kreisläufe.",
                "Earth, soil, planet Earth, location of cycles."),
    20: Station(20, "T", "Ikosigramm", "icosagram", "Hitze/Lava", "Heat/lava", "geology",
                "Heiße Lava, Hitze, Wärmestrom, planetare Grundkraft.",
                "Hot lava, heat, heat stream, planetary base force."),
    21: Station(21, "U", "Henaikosigramm", "henaicosagram", "Vulkanasche", "Volcanic ash", "volcanic",
                "Vulkan, Asche, eruptive Mineralfreisetzung.",
                "Volcano, ash, eruptive mineral release."),
    22: Station(22, "V", "Dyoikosigramm", "dyoicosagram", "Mineralische Neuordnung", "Mineral reordering", "volcanic",
                "Abkühlung, Gesteinsbildung, Asche-zu-Boden-Substrat.",
                "Cooling, rock formation, ash-to-soil substrate."),
}


@dataclass(frozen=True)
class PlanetKind:
    code: str
    label_de: str
    label_en: str
    cycle_length: int


EARTH_TYPE = PlanetKind("EarthType", "Erde-Typ", "Earth-type", 20)
VULCAN_TYPE = PlanetKind("VulcanType", "Vulkan-Typ", "Vulcan-type", 22)
PLANET_KINDS = {EARTH_TYPE.code: EARTH_TYPE, VULCAN_TYPE.code: VULCAN_TYPE}


ROLE_DESCRIPTIONS_DE: Dict[str, str] = {
    "farmer": "Bauer: Samen, Wachstum, Blüte und Ernte.",
    "miller": "Müller: Korn zu Mehl, Produktionskette.",
    "baker": "Bäcker: Mehl/Kette zu Brot und essbarer Nahrung.",
    "merchant": "Händler: Verteilung, Markt, Stationsausgleich.",
    "cook": "Koch: Essen wird aufnahmefähig, Ernährung beginnt.",
    "care_worker": "Pfleger: Körpererhaltung, Verdauung, Gesundheit.",
    "sanitation_worker": "Sanitärarbeiter: sichere Rückführung von Ausscheidungen.",
    "compost_master": "Kompostmeister: Mikrobenarbeit, Zersetzung, Bodenaufbau.",
    "chemist": "Chemiker: Reaktion, Schadstoffkontrolle, Elementwechsel.",
    "geologist": "Geologe/Vulkanarbeiter: Hitze, Lava, Asche, Mineralität.",
    "validator": "Validator/Richter: Station 14, Gesetz, Signale, Gerechtigkeit.",
    "banker": "Kreislaufbank: Kredit auf erwartete Rückführung.",
}


# ---------------------------------------------------------------------------
# Economic data classes
# ---------------------------------------------------------------------------


@dataclass
class CycleValue:
    raw_sg: float
    effective_sg: float
    uke: float
    start_station: int
    end_station: int
    start_repetition: int
    end_repetition: int
    verified: bool


@dataclass
class CycleRecord:
    tick: int
    universe: str
    system: str
    planet: str
    planet_type: str
    agent_id: str
    role: str
    identity_id: str
    action: str
    from_station: int
    to_station: int
    start_repetition: int
    end_repetition: int
    raw_sg: float
    effective_sg: float
    uke: float
    mass: float
    quality: float
    use: float
    justice: float
    verified: bool
    tax: float
    debt_created: float


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
    generation: int = 0
    tags: List[str] = field(default_factory=list)
    history: List[str] = field(default_factory=list)

    def passport(self) -> Dict[str, object]:
        return {
            "identity_id": self.identity_id,
            "label": self.label,
            "planet_type": self.planet_type,
            "cycle_length": PLANET_KINDS[self.planet_type].cycle_length,
            "current_station": self.station,
            "repetition": self.repetition,
            "mass": self.mass,
            "energy": self.energy,
            "nutrients": self.nutrients,
            "quality_factor": self.quality,
            "use_factor": self.use,
            "justice_factor": self.justice,
            "owner_id": self.owner_id,
            "generation": self.generation,
            "tags": list(self.tags),
            "recent_history": list(self.history[-8:]),
        }


@dataclass
class Agent:
    agent_id: str
    name: str
    role: str
    planet_name: str
    money: float
    debt: float
    skill: float
    fairness: float
    efficiency: float
    risk: float
    reputation: float
    actions_done: int = 0
    sg_earned: float = 0.0
    sg_unverified: float = 0.0
    taxes_paid: float = 0.0

    def credit_score(self) -> float:
        return clamp((self.reputation * 0.45 + self.fairness * 0.25 + self.skill * 0.20 + (1.0 - self.risk) * 0.10)
                     - self.debt / max(1000.0, self.money + 1000.0), 0.0, 1.5)


@dataclass
class Loan:
    loan_id: str
    borrower_id: str
    principal: float
    outstanding: float
    interest_rate: float
    due_tick: int
    purpose: str
    expected_sg: float
    status: str = "active"


@dataclass
class Policy:
    exit_tax: float = 0.05
    pollutant_tax: float = 0.08
    soil_rent: float = 0.03
    entropy_levy: float = 0.02
    repair_subsidy: float = 0.08
    compost_bonus: float = 0.06
    water_purity_bonus: float = 0.03
    social_bonus: float = 0.03
    basic_provision_rate: float = 0.05
    verification_strictness: float = 0.55


@dataclass
class PlanetSnapshot:
    tick: int
    universe: str
    system: str
    planet: str
    planet_type: str
    population: float
    health: float
    money_supply: float
    public_budget: float
    inflation_index: float
    soil_fertility: float
    water: float
    microbes: float
    heat: float
    pollution: float
    justice_index: float
    infrastructure: float
    technology: float
    food_stock: float
    seed_stock: float
    waste_stock: float
    return_stock: float
    total_cycle_debt: float
    verified_sg_tick: float
    unverified_sg_tick: float
    trade_volume_tick: float
    closed_loop_rate: float


# ---------------------------------------------------------------------------
# Core formula
# ---------------------------------------------------------------------------


def loop_value(planet_type: str, start: int, end: int, repetition: int) -> int:
    """
    User's base formula:
        SG = (repetition - 1) * N + (end - start)

    Example:
        EarthType, start=4, end=17, repetition=4 => 73
        VulcanType, start=4, end=17, repetition=4 => 79
    """
    N = PLANET_KINDS[planet_type].cycle_length
    value = (repetition - 1) * N + end - start
    if value < 0:
        raise ValueError("End station lies before start station without sufficient repetition.")
    return value


def transition_distance(planet_type: str, start_station: int, start_repetition: int, end_station: int) -> Tuple[int, int]:
    """
    Incremental movement of an identity through the circular alphabet.

    If end station is after start station, the identity stays in the same repetition.
    If it is before or equal to start station, it wraps to the next repetition.
    Equal station means one full cycle.
    """
    N = PLANET_KINDS[planet_type].cycle_length
    if end_station > N:
        raise ValueError(f"Station {end_station} exceeds cycle length {N} for {planet_type}.")
    if end_station > start_station:
        end_repetition = start_repetition
    else:
        end_repetition = start_repetition + 1
    raw = (end_repetition - start_repetition) * N + end_station - start_station
    return raw, end_repetition


# ---------------------------------------------------------------------------
# Planet economy
# ---------------------------------------------------------------------------


class PlanetEconomy:
    def __init__(self, universe_name: str, system_name: str, name: str, kind: PlanetKind,
                 rng: random.Random, agents_per_planet: int = 40) -> None:
        self.universe_name = universe_name
        self.system_name = system_name
        self.name = name
        self.kind = kind
        self.rng = rng
        self.policy = Policy()
        self.population = rng.uniform(700.0, 1800.0)
        self.health = rng.uniform(0.68, 0.92)
        self.soil_fertility = rng.uniform(0.45, 0.85)
        self.water = rng.uniform(0.48, 0.92)
        self.microbes = rng.uniform(0.45, 0.90)
        self.heat = rng.uniform(0.35, 0.75) + (0.20 if kind.code == "VulcanType" else 0.0)
        self.pollution = rng.uniform(0.02, 0.18)
        self.justice_index = rng.uniform(0.58, 0.92)
        self.infrastructure = rng.uniform(0.40, 0.80)
        self.technology = rng.uniform(0.35, 0.72)
        self.public_budget = rng.uniform(700.0, 1500.0)
        self.money_supply = self.public_budget
        self.total_cycle_debt = 0.0
        self.inflation_index = 1.0
        self.trade_volume_tick = 0.0
        self.verified_sg_tick = 0.0
        self.unverified_sg_tick = 0.0
        self.identities: List[Identity] = []
        self.agents: List[Agent] = []
        self.loans: List[Loan] = []
        self.ledger: List[CycleRecord] = []
        self.snapshots: List[PlanetSnapshot] = []
        self.event_log: List[str] = []
        self._id_counter = 0
        self._loan_counter = 0
        self._create_agents(agents_per_planet)
        self._seed_initial_identities()
        self._update_money_supply_from_agents()

    # ----------------------------- identity helpers -----------------------------

    def next_id(self, prefix: str) -> str:
        self._id_counter += 1
        return f"{self.name[:4].upper()}-{prefix}-{self._id_counter:06d}"

    def next_loan_id(self) -> str:
        self._loan_counter += 1
        return f"LOAN-{self.name[:4].upper()}-{self._loan_counter:05d}"

    def _create_identity(self, label: str, station: int, mass: float, owner_id: str,
                         quality: Optional[float] = None, use: Optional[float] = None,
                         justice: Optional[float] = None, energy: Optional[float] = None,
                         nutrients: Optional[float] = None, tags: Optional[List[str]] = None) -> Identity:
        quality = self.rng.uniform(0.70, 1.05) if quality is None else quality
        use = self.rng.uniform(0.70, 1.05) if use is None else use
        justice = self.justice_index if justice is None else justice
        energy = mass * self.rng.uniform(0.3, 1.4) if energy is None else energy
        nutrients = mass * self.rng.uniform(0.3, 1.4) if nutrients is None else nutrients
        ident = Identity(
            identity_id=self.next_id("ID"),
            label=label,
            planet_type=self.kind.code,
            station=station,
            repetition=1,
            mass=max(0.0001, mass),
            energy=max(0.0, energy),
            nutrients=max(0.0, nutrients),
            quality=clamp(quality, 0.02, 1.5),
            use=clamp(use, 0.02, 1.5),
            justice=clamp(justice, 0.02, 1.5),
            owner_id=owner_id,
            tags=list(tags or []),
            history=[f"created@{station}:{STATIONS[station].name_en}"],
        )
        self.identities.append(ident)
        return ident

    def _split_identity(self, ident: Identity, amount: float) -> Identity:
        """Split amount from identity. If amount >= mass, return identity unchanged."""
        if amount >= ident.mass * 0.98:
            return ident
        amount = max(0.0001, amount)
        ratio = amount / ident.mass
        ident.mass -= amount
        ident.energy *= (1.0 - ratio)
        ident.nutrients *= (1.0 - ratio)
        clone = Identity(
            identity_id=self.next_id("SPL"),
            label=ident.label,
            planet_type=ident.planet_type,
            station=ident.station,
            repetition=ident.repetition,
            mass=amount,
            energy=ident.energy * ratio / max(1e-9, (1.0 - ratio)),
            nutrients=ident.nutrients * ratio / max(1e-9, (1.0 - ratio)),
            quality=ident.quality,
            use=ident.use,
            justice=ident.justice,
            owner_id=ident.owner_id,
            generation=ident.generation,
            tags=list(ident.tags),
            history=list(ident.history[-6:]) + [f"split:{amount:.3f}"],
        )
        self.identities.append(clone)
        return clone

    def find_identity(self, stations: Sequence[int], min_mass: float = 0.05,
                      tags_any: Optional[Sequence[str]] = None, prefer_quality: bool = True) -> Optional[Identity]:
        candidates: List[Identity] = []
        station_set = set(stations)
        tag_set = set(tags_any or [])
        for ident in self.identities:
            if ident.station in station_set and ident.mass >= min_mass:
                if tag_set and not (set(ident.tags) & tag_set):
                    continue
                candidates.append(ident)
        if not candidates:
            return None
        if prefer_quality:
            candidates.sort(key=lambda x: (x.quality * x.use * x.mass, x.repetition), reverse=True)
            top = candidates[:max(1, min(5, len(candidates)))]
            return self.rng.choice(top)
        return self.rng.choice(candidates)

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
        values: List[float] = []
        weights: List[float] = []
        for ident in self.identities:
            if station is not None and ident.station != station:
                continue
            values.append(ident.quality)
            weights.append(ident.mass)
        if not values:
            return 0.0
        total_w = sum(weights)
        return sum(v * w for v, w in zip(values, weights)) / max(total_w, 1e-9)

    # ----------------------------- setup -----------------------------

    def _create_agents(self, n: int) -> None:
        role_weights = [
            ("farmer", 9.0),
            ("miller", 3.0),
            ("baker", 4.0),
            ("merchant", 5.0),
            ("cook", 4.0),
            ("care_worker", 3.0),
            ("sanitation_worker", 4.0),
            ("compost_master", 4.0),
            ("chemist", 3.0),
            ("geologist", 2.5 if self.kind.code == "VulcanType" else 1.0),
            ("validator", 2.0),
            ("banker", 1.5),
        ]
        syllables = ["Ka", "Lo", "Mi", "Ra", "Sen", "Tor", "Via", "No", "Ari", "Zen", "Mol", "Gre", "Uri", "Sol"]
        for i in range(n):
            role = weighted_choice(self.rng, role_weights)
            name = self.rng.choice(syllables) + self.rng.choice(syllables).lower() + f"-{i:02d}"
            money = self.rng.uniform(60.0, 190.0)
            agent = Agent(
                agent_id=f"{self.name[:3].upper()}-AG-{i:03d}",
                name=name,
                role=role,
                planet_name=self.name,
                money=money,
                debt=self.rng.uniform(0.0, 40.0),
                skill=clamp(self.rng.gauss(0.75, 0.16), 0.20, 1.25),
                fairness=clamp(self.rng.gauss(self.justice_index, 0.13), 0.15, 1.20),
                efficiency=clamp(self.rng.gauss(0.75, 0.14), 0.25, 1.30),
                risk=clamp(self.rng.betavariate(2.2, 5.0), 0.02, 0.95),
                reputation=clamp(self.rng.gauss(0.72, 0.14), 0.15, 1.20),
            )
            self.agents.append(agent)

    def _agent_by_role(self, role: str) -> Optional[Agent]:
        candidates = [a for a in self.agents if a.role == role]
        if not candidates:
            return None
        return self.rng.choice(candidates)

    def _any_agent(self) -> Agent:
        return self.rng.choice(self.agents)

    def _seed_initial_identities(self) -> None:
        state_owner = f"STATE-{self.name}"
        for _ in range(8):
            self._create_identity("seed_batch", 2, self.rng.uniform(2.0, 6.0), state_owner,
                                  quality=self.rng.uniform(0.70, 1.05), use=0.90, tags=["seed", "plant"])
        for _ in range(10):
            self._create_identity("green_biomass", 4, self.rng.uniform(3.0, 10.0), state_owner,
                                  quality=self.soil_fertility * self.rng.uniform(0.8, 1.2), use=0.85, tags=["plant", "biomass"])
        for _ in range(7):
            self._create_identity("crop_grain", 7, self.rng.uniform(2.0, 8.0), state_owner,
                                  quality=self.rng.uniform(0.72, 1.05), use=0.95, tags=["food", "grain"])
        for _ in range(5):
            self._create_identity("market_food", 8, self.rng.uniform(1.0, 5.0), state_owner,
                                  quality=self.rng.uniform(0.65, 1.00), use=1.0, tags=["food", "edible"])
        for _ in range(6):
            self._create_identity("organic_waste", 13, self.rng.uniform(1.0, 5.5), state_owner,
                                  quality=self.rng.uniform(0.45, 0.85), use=0.70, tags=["waste", "microbes"])
        for _ in range(6):
            self._create_identity("soil_volume", 19, self.rng.uniform(4.0, 12.0), state_owner,
                                  quality=self.soil_fertility, use=0.95, tags=["soil", "planet"])
        for _ in range(3):
            self._create_identity("heat_stream", 20, self.rng.uniform(1.0, 4.0), state_owner,
                                  quality=self.heat, use=0.60, energy=self.rng.uniform(4.0, 12.0), tags=["heat", "geology"])
        if self.kind.code == "VulcanType":
            for _ in range(4):
                self._create_identity("volcanic_ash", 21, self.rng.uniform(2.0, 8.0), state_owner,
                                      quality=self.rng.uniform(0.60, 1.15), use=0.75, tags=["ash", "mineral"])
            for _ in range(2):
                self._create_identity("mineral_substrate", 22, self.rng.uniform(2.0, 6.0), state_owner,
                                      quality=self.rng.uniform(0.70, 1.15), use=0.80, tags=["mineral", "soil"])

    def _update_money_supply_from_agents(self) -> None:
        self.money_supply = self.public_budget + sum(a.money for a in self.agents)

    # ----------------------------- transformation and money -----------------------------

    def verification_probability(self, actor: Optional[Agent]) -> float:
        validator_count = sum(1 for a in self.agents if a.role == "validator")
        actor_rep = actor.reputation if actor else 0.7
        p = (self.policy.verification_strictness * 0.45 +
             self.infrastructure * 0.22 +
             self.technology * 0.13 +
             self.justice_index * 0.10 +
             min(0.10, validator_count * 0.008) +
             actor_rep * 0.10)
        return clamp(p, 0.10, 0.98)

    def transform(self, tick: int, actor: Agent, ident: Identity, target_station: int, action: str,
                  amount: Optional[float] = None, quality_delta: float = 0.0, use_delta: float = 0.0,
                  justice_delta: float = 0.0, material_loss: float = 0.0, material_gain: float = 0.0,
                  pollution_delta: float = 0.0, debt_factor: float = 0.0,
                  tags_add: Optional[List[str]] = None, force_verify: bool = False) -> Optional[CycleValue]:
        if target_station > self.kind.cycle_length:
            return None
        if amount is not None and amount < ident.mass * 0.98:
            ident = self._split_identity(ident, amount)
        start_station = ident.station
        start_rep = ident.repetition
        raw, end_rep = transition_distance(self.kind.code, start_station, start_rep, target_station)
        # Environmental modifiers.
        env_quality = 1.0 - self.pollution * 0.22 + self.technology * 0.04 + self.infrastructure * 0.03
        skill_factor = 0.92 + actor.skill * 0.16 + actor.efficiency * 0.08
        fairness_factor = (ident.justice * 0.40 + actor.fairness * 0.40 + self.justice_index * 0.20)
        new_mass = max(0.0001, ident.mass * (1.0 - material_loss) + material_gain)
        ident.energy = max(0.0, ident.energy * (1.0 - material_loss * 0.7) + material_gain * self.heat * 0.5)
        ident.nutrients = max(0.0, ident.nutrients * (1.0 - material_loss * 0.5) + material_gain * self.soil_fertility * 0.5)
        ident.mass = new_mass
        ident.quality = clamp((ident.quality + quality_delta) * env_quality * (0.96 + actor.skill * 0.08), 0.03, 1.50)
        ident.use = clamp(ident.use + use_delta + actor.efficiency * 0.04, 0.03, 1.50)
        ident.justice = clamp(fairness_factor + justice_delta, 0.02, 1.50)
        ident.station = target_station
        ident.repetition = end_rep
        ident.owner_id = actor.agent_id
        ident.generation += 1
        if tags_add:
            for t in tags_add:
                if t not in ident.tags:
                    ident.tags.append(t)
        ident.history.append(f"t{tick}:{action}:{start_station}->{target_station}/r{start_rep}->{end_rep}")
        if len(ident.history) > 32:
            ident.history = ident.history[-32:]

        verified = force_verify or (self.rng.random() < self.verification_probability(actor))
        material_factor = ident.mass
        # Effective money is a stacked value: distance * material * quality * use * justice.
        effective = raw * material_factor * ident.quality * ident.use * ident.justice
        if not verified:
            actor.sg_unverified += effective
            self.unverified_sg_tick += effective
            effective_minted = 0.0
            actor.reputation = clamp(actor.reputation - 0.008, 0.02, 1.5)
        else:
            effective_minted = effective
            actor.reputation = clamp(actor.reputation + 0.004, 0.02, 1.5)

        uke = raw / float(self.kind.cycle_length)
        tax_rate = self._tax_rate_for_transition(start_station, target_station, action, ident)
        tax = effective_minted * tax_rate
        bonus = self._bonus_for_transition(target_station, action, ident, effective_minted)
        # bonus can only be paid if budget exists. It is not new money; it redistributes public money.
        bonus_paid = min(self.public_budget, bonus)
        self.public_budget -= bonus_paid
        actor.money += max(0.0, effective_minted - tax) + bonus_paid
        actor.sg_earned += effective_minted + bonus_paid
        actor.taxes_paid += tax
        self.public_budget += tax
        self.money_supply += effective_minted

        # Environmental effects and debt.
        self.pollution = clamp(self.pollution + pollution_delta, 0.0, 2.0)
        debt_created = 0.0
        if debt_factor > 0.0:
            debt_created = raw * ident.mass * debt_factor * (1.0 + self.pollution)
            actor.debt += debt_created * 0.60
            self.total_cycle_debt += debt_created
        self.verified_sg_tick += effective_minted
        actor.actions_done += 1

        record = CycleRecord(
            tick=tick,
            universe=self.universe_name,
            system=self.system_name,
            planet=self.name,
            planet_type=self.kind.code,
            agent_id=actor.agent_id,
            role=actor.role,
            identity_id=ident.identity_id,
            action=action,
            from_station=start_station,
            to_station=target_station,
            start_repetition=start_rep,
            end_repetition=end_rep,
            raw_sg=raw,
            effective_sg=effective_minted,
            uke=uke,
            mass=ident.mass,
            quality=ident.quality,
            use=ident.use,
            justice=ident.justice,
            verified=verified,
            tax=tax,
            debt_created=debt_created,
        )
        self.ledger.append(record)
        return CycleValue(raw, effective_minted, uke, start_station, target_station, start_rep, end_rep, verified)

    def _tax_rate_for_transition(self, start_station: int, target_station: int, action: str, ident: Identity) -> float:
        rate = 0.0
        if target_station in (13, 18) or "waste" in ident.tags:
            rate += self.policy.exit_tax * 0.4
        if ident.quality < 0.45:
            rate += self.policy.pollutant_tax * (0.50 - ident.quality)
        if target_station in (19, 20, 21, 22):
            rate += self.policy.soil_rent * 0.5
        if action in ("burn_loss", "failed_disposal", "extractive_heat"):
            rate += self.policy.entropy_levy
        return clamp(rate, 0.0, 0.30)

    def _bonus_for_transition(self, target_station: int, action: str, ident: Identity, effective: float) -> float:
        if effective <= 0:
            return 0.0
        bonus_rate = 0.0
        if target_station in (15, 16, 17):
            bonus_rate += self.policy.repair_subsidy
        if action in ("compost_return", "microbial_decomposition", "sanitary_return"):
            bonus_rate += self.policy.compost_bonus
        if ident.justice > 0.90:
            bonus_rate += self.policy.social_bonus * 0.5
        if self.pollution < 0.12 and target_station == 17:
            bonus_rate += self.policy.water_purity_bonus
        return effective * clamp(bonus_rate, 0.0, 0.25)

    # ----------------------------- per-role actions -----------------------------

    def step(self, tick: int) -> None:
        self.verified_sg_tick = 0.0
        self.unverified_sg_tick = 0.0
        self.trade_volume_tick = 0.0
        self._natural_environment_tick(tick)
        self._cosmic_or_local_event(tick)
        # Active agents perform one or two actions. Bankers and validators also matter.
        agents = list(self.agents)
        self.rng.shuffle(agents)
        for agent in agents:
            # low-health planets lose productivity; skilled agents may act twice.
            if self.rng.random() > clamp(0.45 + self.health * 0.35 + agent.skill * 0.15, 0.15, 0.97):
                continue
            self._perform_agent_action(tick, agent)
            if self.rng.random() < (agent.efficiency - 0.55) * 0.35:
                self._perform_agent_action(tick, agent)
        self._population_consumption_and_health(tick)
        self._apply_cycle_debt_and_open_loops(tick)
        self._policy_adjustment(tick)
        self._settle_loans(tick)
        self._prune_and_merge_identities()
        self._update_inflation()
        self._take_snapshot(tick)

    def _perform_agent_action(self, tick: int, agent: Agent) -> None:
        role = agent.role
        if role == "farmer":
            self._farmer_action(tick, agent)
        elif role == "miller":
            self._miller_action(tick, agent)
        elif role == "baker":
            self._baker_action(tick, agent)
        elif role == "merchant":
            self._merchant_action(tick, agent)
        elif role == "cook":
            self._cook_action(tick, agent)
        elif role == "care_worker":
            self._care_worker_action(tick, agent)
        elif role == "sanitation_worker":
            self._sanitation_action(tick, agent)
        elif role == "compost_master":
            self._compost_action(tick, agent)
        elif role == "chemist":
            self._chemist_action(tick, agent)
        elif role == "geologist":
            self._geologist_action(tick, agent)
        elif role == "validator":
            self._validator_action(tick, agent)
        elif role == "banker":
            self._banker_action(tick, agent)
        else:
            self._merchant_action(tick, agent)

    def _farmer_action(self, tick: int, agent: Agent) -> None:
        # First use fertilizer if available; otherwise progress plant identities.
        if self.rng.random() < 0.25:
            fert = self.find_identity([5, 17, 22] if self.kind.code == "VulcanType" else [5, 17], min_mass=0.05)
            if fert:
                amount = min(fert.mass, self.rng.uniform(0.2, 1.0) * agent.efficiency)
                self.transform(tick, agent, fert, 4, "fertility_to_growth", amount=amount,
                               quality_delta=0.03 * self.microbes, use_delta=0.02,
                               material_loss=0.15, pollution_delta=-0.002,
                               tags_add=["plant", "biomass"])
                self.soil_fertility = clamp(self.soil_fertility + 0.006 * amount * fert.quality, 0.02, 1.5)
                return
        # Pipeline: 1->2, 2->3, 3->4, 4->6, 6->7.
        candidates = [
            ([6], 7, "harvest_crop"),
            ([4], 6, "flowering"),
            ([3], 4, "green_growth"),
            ([2], 3, "germination"),
            ([1], 2, "pollination_to_seed"),
        ]
        for stations, target, action in candidates:
            ident = self.find_identity(stations, min_mass=0.05)
            if ident:
                amount = min(ident.mass, self.rng.uniform(0.4, 1.8) * agent.efficiency)
                water_stress = max(0.0, 0.55 - self.water)
                soil_bonus = (self.soil_fertility - 0.50) * 0.06
                material_gain = 0.0
                if target in (4, 6, 7):
                    material_gain = amount * max(0.0, (self.soil_fertility + self.water + self.microbes) / 3.0 - 0.35) * 0.35
                    self.water = clamp(self.water - 0.0015 * amount, 0.02, 1.5)
                    self.soil_fertility = clamp(self.soil_fertility - 0.0009 * amount, 0.02, 1.5)
                self.transform(tick, agent, ident, target, action, amount=amount,
                               quality_delta=soil_bonus - water_stress * 0.08,
                               use_delta=0.03 if target == 7 else 0.01,
                               material_gain=material_gain,
                               pollution_delta=0.0005 * water_stress,
                               debt_factor=0.02 if water_stress > 0.18 else 0.0,
                               tags_add=["food", "grain"] if target == 7 else ["plant"])
                return
        # Create new fecundation identity if fields are empty.
        self._create_identity("pollination_identity", 1, self.rng.uniform(0.8, 2.0) * agent.efficiency,
                              agent.agent_id, quality=self.soil_fertility, use=0.75,
                              justice=agent.fairness, tags=["origin", "seed"])

    def _miller_action(self, tick: int, agent: Agent) -> None:
        ident = self.find_identity([7], min_mass=0.10, tags_any=["grain", "food"])
        if not ident:
            self._merchant_action(tick, agent)
            return
        amount = min(ident.mass, self.rng.uniform(0.3, 1.5) * agent.efficiency)
        self.transform(tick, agent, ident, 11, "milling_grain_to_chain", amount=amount,
                       quality_delta=0.02 * agent.skill, use_delta=0.08,
                       material_loss=0.04 * (1.1 - agent.efficiency),
                       pollution_delta=0.0008,
                       tags_add=["flour", "production", "food"])

    def _baker_action(self, tick: int, agent: Agent) -> None:
        ident = self.find_identity([11], min_mass=0.08, tags_any=["flour", "production", "food"])
        if not ident:
            ident = self.find_identity([7], min_mass=0.08, tags_any=["food", "grain"])
            target = 11
            action = "direct_baking_chain"
        else:
            target = 8
            action = "baking_to_edible_food"
        if not ident:
            return
        amount = min(ident.mass, self.rng.uniform(0.2, 1.2) * agent.efficiency)
        self.transform(tick, agent, ident, target, action, amount=amount,
                       quality_delta=0.03 * agent.skill + self.technology * 0.01,
                       use_delta=0.14,
                       material_loss=0.025,
                       pollution_delta=0.0008,
                       tags_add=["bread", "edible", "food"])

    def _merchant_action(self, tick: int, agent: Agent) -> None:
        # Merchants move usable goods into production-chain visibility or distribution.
        ident = self.find_identity([7, 8, 11, 5, 21, 22], min_mass=0.07)
        if not ident:
            return
        if ident.station in (7,):
            target = 11
            action = "market_chain_registration"
        elif ident.station == 11:
            target = 8
            action = "market_to_eating_access"
        elif ident.station == 8:
            target = 10
            action = "fit_food_into_life"
        elif ident.station in (21, 22):
            target = 5
            action = "mineral_to_fertilizer_market"
        else:
            target = 4
            action = "fertilizer_distribution"
        amount = min(ident.mass, self.rng.uniform(0.1, 1.0) * agent.efficiency)
        self.transform(tick, agent, ident, target, action, amount=amount,
                       quality_delta=0.005, use_delta=0.06,
                       justice_delta=0.01 if agent.fairness > 0.80 else -0.005,
                       material_loss=0.015,
                       pollution_delta=0.0003,
                       tags_add=["distributed"])

    def _cook_action(self, tick: int, agent: Agent) -> None:
        ident = self.find_identity([8, 10, 11], min_mass=0.05, tags_any=["food", "bread", "edible"])
        if not ident:
            return
        target = 12 if ident.station != 12 else 13
        amount = min(ident.mass, self.rng.uniform(0.08, 0.7) * agent.efficiency)
        cv = self.transform(tick, agent, ident, target, "eating_to_digestion", amount=amount,
                            quality_delta=0.02 * agent.skill, use_delta=0.10,
                            material_loss=0.12,
                            pollution_delta=0.0002,
                            tags_add=["digested"])
        if cv and cv.verified:
            # A portion becomes body/creature value at station 9.
            body_mass = amount * 0.18 * self.health
            if body_mass > 0.01:
                self._create_identity("body_growth", 9, body_mass, agent.agent_id,
                                      quality=ident.quality * self.health, use=0.90,
                                      justice=ident.justice, tags=["body", "creature"])
            self.health = clamp(self.health + 0.00025 * amount * ident.quality, 0.05, 1.4)

    def _care_worker_action(self, tick: int, agent: Agent) -> None:
        ident = self.find_identity([12, 9], min_mass=0.04)
        if not ident:
            return
        if ident.station == 12:
            target = 13
            action = "digestion_to_excretion"
            loss = 0.18
            tags = ["waste", "microbes"]
        else:
            target = 10
            action = "body_to_ecological_fit"
            loss = 0.02
            tags = ["life", "creature"]
        amount = min(ident.mass, self.rng.uniform(0.05, 0.5) * agent.efficiency)
        self.transform(tick, agent, ident, target, action, amount=amount,
                       quality_delta=0.01 * agent.skill, use_delta=0.04,
                       justice_delta=0.02 * agent.fairness,
                       material_loss=loss,
                       tags_add=tags)
        self.health = clamp(self.health + 0.0005 * agent.fairness, 0.05, 1.4)

    def _sanitation_action(self, tick: int, agent: Agent) -> None:
        ident = self.find_identity([12, 13, 18], min_mass=0.05)
        if not ident:
            return
        if ident.station == 12:
            target = 13
            action = "sanitary_excretion_collection"
        elif ident.station == 13:
            target = 15
            action = "sanitary_return"
        else:
            target = 15
            action = "death_to_decomposition_collection"
        amount = min(ident.mass, self.rng.uniform(0.1, 1.2) * agent.efficiency)
        dirty = max(0.0, 0.55 - self.infrastructure)
        self.transform(tick, agent, ident, target, action, amount=amount,
                       quality_delta=0.02 * agent.skill - dirty * 0.06,
                       use_delta=0.05,
                       material_loss=0.04,
                       pollution_delta=-0.002 * amount * agent.skill + dirty * 0.001,
                       debt_factor=0.03 if dirty > 0.20 else 0.0,
                       tags_add=["waste", "microbes", "safe_return"])

    def _compost_action(self, tick: int, agent: Agent) -> None:
        ident = self.find_identity([13, 15, 16, 18], min_mass=0.06)
        if not ident:
            return
        if ident.station in (13, 18):
            target = 15
            action = "microbial_decomposition"
        elif ident.station == 15:
            target = 16
            action = "compost_chemical_reaction"
        else:
            target = 17
            action = "compost_return"
        amount = min(ident.mass, self.rng.uniform(0.12, 1.4) * agent.efficiency)
        microbe_bonus = (self.microbes - 0.50) * 0.08
        cv = self.transform(tick, agent, ident, target, action, amount=amount,
                            quality_delta=0.04 * agent.skill + microbe_bonus,
                            use_delta=0.08 if target == 17 else 0.04,
                            material_loss=0.08 if target != 17 else 0.04,
                            pollution_delta=-0.003 * amount * agent.skill,
                            tags_add=["compost", "return", "soil"])
        self.microbes = clamp(self.microbes + 0.0015 * amount * agent.skill, 0.02, 1.5)
        if target == 17 and cv and cv.verified:
            self.soil_fertility = clamp(self.soil_fertility + 0.006 * amount * ident.quality, 0.02, 1.5)
            # Return creates fertilizer-growth material at station 5.
            if self.rng.random() < 0.55:
                self._create_identity("fertility_credit", 5, amount * 0.35, agent.agent_id,
                                      quality=ident.quality, use=1.0, justice=ident.justice,
                                      tags=["fertilizer", "soil", "return"])

    def _chemist_action(self, tick: int, agent: Agent) -> None:
        ident = self.find_identity([15, 16, 13, 20, 21, 22], min_mass=0.04)
        if not ident:
            return
        if ident.station == 15:
            target = 16
            action = "chemical_reaction"
        elif ident.station == 16:
            target = 17
            action = "element_shift_to_return"
        elif ident.station in (21, 22):
            target = 5
            action = "mineral_chemistry_to_fertility"
        elif ident.station == 20:
            target = 16
            action = "heat_assisted_reaction"
        else:
            target = 16
            action = "waste_stabilization"
        amount = min(ident.mass, self.rng.uniform(0.08, 0.9) * agent.efficiency)
        self.transform(tick, agent, ident, target, action, amount=amount,
                       quality_delta=0.05 * agent.skill + self.technology * 0.02,
                       use_delta=0.07,
                       material_loss=0.05,
                       pollution_delta=-0.006 * amount * agent.skill,
                       tags_add=["chemistry", "safe"])
        self.technology = clamp(self.technology + 0.0007 * agent.skill, 0.02, 1.5)

    def _geologist_action(self, tick: int, agent: Agent) -> None:
        if self.kind.code == "VulcanType":
            ident = self.find_identity([20, 21, 22, 19], min_mass=0.05)
            if not ident:
                # Create deep heat/lava if no geologic stock exists.
                self._create_identity("deep_heat_stream", 20, self.rng.uniform(0.5, 2.0), agent.agent_id,
                                      quality=self.heat, use=0.60, energy=self.heat * 5.0,
                                      tags=["heat", "lava", "geology"])
                return
            if ident.station == 20:
                target = 21
                action = "lava_to_volcanic_ash"
                tags = ["ash", "mineral", "volcanic"]
            elif ident.station == 21:
                target = 22
                action = "ash_to_mineral_reordering"
                tags = ["mineral", "substrate"]
            elif ident.station == 22:
                target = 5
                action = "mineral_substrate_to_fertility"
                tags = ["fertilizer", "soil"]
            else:
                target = 20
                action = "soil_to_geologic_heat_memory"
                tags = ["heat", "geology"]
            amount = min(ident.mass, self.rng.uniform(0.05, 0.8) * agent.efficiency)
            self.transform(tick, agent, ident, target, action, amount=amount,
                           quality_delta=0.03 * agent.skill + self.heat * 0.01,
                           use_delta=0.05,
                           material_loss=0.03,
                           material_gain=0.10 * amount if target in (21, 22) else 0.0,
                           pollution_delta=0.003 * amount if target == 21 else -0.001,
                           debt_factor=0.02 if target == 21 and agent.skill < 0.50 else 0.0,
                           tags_add=tags)
            if target == 5:
                self.soil_fertility = clamp(self.soil_fertility + 0.004 * amount, 0.02, 1.5)
        else:
            ident = self.find_identity([19, 20, 17], min_mass=0.05)
            if not ident:
                return
            target = 20 if ident.station != 20 else 19
            action = "earth_geologic_heat_cycle" if target == 20 else "heat_memory_to_soil"
            amount = min(ident.mass, self.rng.uniform(0.05, 0.7) * agent.efficiency)
            self.transform(tick, agent, ident, target, action, amount=amount,
                           quality_delta=0.01 * agent.skill,
                           use_delta=0.03,
                           material_loss=0.02,
                           pollution_delta=0.001 if target == 20 else -0.0005,
                           tags_add=["geology", "soil"])

    def _validator_action(self, tick: int, agent: Agent) -> None:
        # Station 14 governance loop: law, signal, communication, justice.
        ident = self.find_identity([14], min_mass=0.02)
        if not ident:
            ident = self._create_identity("law_signal", 14, self.rng.uniform(0.08, 0.25), agent.agent_id,
                                          quality=self.justice_index, use=1.0, justice=agent.fairness,
                                          tags=["law", "signal", "justice"])
        self.transform(tick, agent, ident, 14, "governance_signal_repeat", amount=min(ident.mass, 0.2),
                       quality_delta=0.02 * agent.skill,
                       use_delta=0.05,
                       justice_delta=0.03 * agent.fairness,
                       material_loss=0.0,
                       pollution_delta=-0.0005,
                       tags_add=["validated"], force_verify=(self.rng.random() < 0.35))
        self.justice_index = clamp(self.justice_index + 0.0012 * agent.fairness + 0.0003 * agent.skill, 0.02, 1.5)
        self.infrastructure = clamp(self.infrastructure + 0.0006 * agent.skill, 0.02, 1.5)

    def _banker_action(self, tick: int, agent: Agent) -> None:
        # Cycle bank: finance agents who can close loops, especially return infrastructure.
        active_loans = [l for l in self.loans if l.status == "active"]
        if len(active_loans) > max(5, len(self.agents) // 4):
            return
        role_priority = ["compost_master", "sanitation_worker", "farmer", "chemist", "baker", "merchant"]
        candidates = [a for a in self.agents if a.role in role_priority and a.credit_score() > 0.45]
        if not candidates:
            return
        borrower = self.rng.choice(candidates)
        principal = self.rng.uniform(20.0, 120.0) * (0.6 + borrower.credit_score())
        if agent.money < principal * 0.2:
            return
        interest = 0.01 + 0.06 * borrower.risk + 0.02 * max(0.0, self.inflation_index - 1.0)
        loan = Loan(
            loan_id=self.next_loan_id(),
            borrower_id=borrower.agent_id,
            principal=principal,
            outstanding=principal * (1.0 + interest),
            interest_rate=interest,
            due_tick=tick + self.rng.randint(6, 16),
            purpose=f"cycle-credit:{borrower.role}",
            expected_sg=principal * (1.2 + borrower.skill),
        )
        self.loans.append(loan)
        borrower.money += principal
        agent.money -= principal * 0.08  # bank operational reserve at risk
        self.money_supply += principal * 0.92  # credit expansion, partially backed by expected SG
        self.event_log.append(f"t{tick} {self.name}: Kreislaufbank loan {loan.loan_id} to {borrower.role} {fmt(principal)}")

    # ----------------------------- planet-level processes -----------------------------

    def _natural_environment_tick(self, tick: int) -> None:
        # Slow drift: soil/water/microbes recover or decline based on pollution and return stock.
        return_stock = self.stock_mass(17)
        waste_stock = self.stock_mass(13) + self.stock_mass(18)
        self.soil_fertility = clamp(self.soil_fertility + 0.0008 * return_stock - 0.0005 * waste_stock - 0.002 * self.pollution, 0.02, 1.5)
        self.microbes = clamp(self.microbes + 0.0005 * (waste_stock + return_stock) - 0.0015 * self.pollution, 0.02, 1.5)
        self.water = clamp(self.water + self.rng.gauss(0.002, 0.010) - 0.002 * self.pollution, 0.02, 1.5)
        self.heat = clamp(self.heat + self.rng.gauss(0.0005, 0.005) + (0.001 if self.kind.code == "VulcanType" else 0.0), 0.02, 1.5)
        self.pollution = clamp(self.pollution * 0.992 - 0.001 * self.infrastructure + 0.0008 * waste_stock, 0.0, 2.0)

    def _cosmic_or_local_event(self, tick: int) -> None:
        # Event probabilities are kept modest to make long runs interesting but not chaotic.
        roll = self.rng.random()
        if roll < 0.018:
            # Drought or water shock.
            loss = self.rng.uniform(0.06, 0.18)
            self.water = clamp(self.water - loss, 0.02, 1.5)
            self.event_log.append(f"t{tick} {self.name}: Dürre/Wasserschock -{loss:.2f}")
        elif roll < 0.034:
            # Microbial bloom.
            gain = self.rng.uniform(0.04, 0.14)
            self.microbes = clamp(self.microbes + gain, 0.02, 1.5)
            self.event_log.append(f"t{tick} {self.name}: Mikrobenblüte +{gain:.2f}")
        elif roll < 0.049:
            # Contamination.
            gain = self.rng.uniform(0.04, 0.16)
            self.pollution = clamp(self.pollution + gain, 0.0, 2.0)
            self.total_cycle_debt += gain * 90.0
            self.event_log.append(f"t{tick} {self.name}: Schadstoffereignis +{gain:.2f}")
        elif roll < 0.063:
            # Technology discovery.
            gain = self.rng.uniform(0.02, 0.08)
            self.technology = clamp(self.technology + gain, 0.02, 1.5)
            self.event_log.append(f"t{tick} {self.name}: Kreislauftechnologie +{gain:.2f}")
        elif self.kind.code == "VulcanType" and roll < 0.088:
            # Volcanic eruption creates ash but also pollution/heat.
            mass = self.rng.uniform(2.0, 9.0)
            quality = self.rng.uniform(0.55, 1.20)
            self._create_identity("eruption_ash", 21, mass, f"STATE-{self.name}",
                                  quality=quality, use=0.75, energy=mass * 1.8,
                                  tags=["ash", "volcanic", "mineral"])
            self.heat = clamp(self.heat + 0.03, 0.02, 1.5)
            self.pollution = clamp(self.pollution + 0.015, 0.0, 2.0)
            self.event_log.append(f"t{tick} {self.name}: Vulkaneruption erzeugt {fmt(mass)} Asche")

    def _population_consumption_and_health(self, tick: int) -> None:
        food_need = self.population * 0.0022
        food_stock = self.stock_mass(8) + 0.35 * self.stock_mass(11) + 0.25 * self.stock_mass(7)
        if food_stock >= food_need:
            self.health = clamp(self.health + 0.002 * min(1.0, food_stock / max(food_need, 0.01)), 0.05, 1.4)
            # population grows slowly when health and food are good.
            self.population *= (1.0 + 0.0005 * clamp(self.health - 0.75, 0.0, 0.5))
        else:
            shortage = 1.0 - safe_div(food_stock, food_need, 0.0)
            self.health = clamp(self.health - 0.008 * shortage, 0.05, 1.4)
            self.population *= (1.0 - 0.001 * shortage)
            # Hunger creates social cycle debt.
            hunger_debt = shortage * self.population * 0.08
            self.total_cycle_debt += hunger_debt
            self.public_budget -= min(self.public_budget, hunger_debt * self.policy.basic_provision_rate)
            if tick % 4 == 0:
                self.event_log.append(f"t{tick} {self.name}: Nahrungsmangel, Kreislaufschuld +{fmt(hunger_debt)}")
        # Natural death creates station 18 identity.
        death_rate = clamp(0.0002 + max(0.0, 0.75 - self.health) * 0.0015 + self.pollution * 0.0004, 0.00005, 0.01)
        death_mass = self.population * death_rate * 0.04
        if death_mass > 0.02:
            self._create_identity("death_residue", 18, death_mass, f"STATE-{self.name}",
                                  quality=clamp(0.65 - self.pollution * 0.2, 0.05, 1.1), use=0.65,
                                  justice=self.justice_index, tags=["death", "microbes", "waste"])

    def _apply_cycle_debt_and_open_loops(self, tick: int) -> None:
        waste = self.stock_mass(13) + self.stock_mass(18)
        pollutant_debt = self.pollution * 18.0
        open_loop_debt = max(0.0, waste - (self.infrastructure + self.microbes) * 15.0) * 0.08
        debt = pollutant_debt + open_loop_debt
        self.total_cycle_debt += debt
        # Small debt tax distributed to economy.
        if debt > 0:
            tax = min(self.public_budget * 0.02, debt * 0.03)
            self.public_budget = max(0.0, self.public_budget - tax)
        # justice erodes if debt is high.
        self.justice_index = clamp(self.justice_index - 0.00004 * debt, 0.02, 1.5)

    def _policy_adjustment(self, tick: int) -> None:
        if tick % 6 != 0:
            return
        waste = self.stock_mass(13) + self.stock_mass(18)
        food = self.stock_mass(8) + self.stock_mass(11) * 0.35
        # Biological chamber: pollution/waste.
        if self.pollution > 0.25 or waste > 25.0:
            self.policy.pollutant_tax = clamp(self.policy.pollutant_tax + 0.01, 0.02, 0.25)
            self.policy.repair_subsidy = clamp(self.policy.repair_subsidy + 0.01, 0.02, 0.25)
        else:
            self.policy.pollutant_tax = clamp(self.policy.pollutant_tax - 0.003, 0.02, 0.25)
        # Economic chamber: inflation and food.
        if self.inflation_index > 1.25:
            self.policy.verification_strictness = clamp(self.policy.verification_strictness + 0.025, 0.20, 0.95)
        elif self.inflation_index < 0.85:
            self.policy.verification_strictness = clamp(self.policy.verification_strictness - 0.015, 0.20, 0.95)
        if food < self.population * 0.004:
            self.policy.basic_provision_rate = clamp(self.policy.basic_provision_rate + 0.01, 0.01, 0.20)
        # Justice chamber.
        if self.justice_index < 0.60:
            self.policy.social_bonus = clamp(self.policy.social_bonus + 0.01, 0.01, 0.18)
        elif self.justice_index > 0.90:
            self.policy.social_bonus = clamp(self.policy.social_bonus - 0.003, 0.01, 0.18)

    def _settle_loans(self, tick: int) -> None:
        for loan in self.loans:
            if loan.status != "active" or tick < loan.due_tick:
                continue
            borrower = next((a for a in self.agents if a.agent_id == loan.borrower_id), None)
            if not borrower:
                loan.status = "lost"
                continue
            recent_sg = sum(r.effective_sg for r in self.ledger[-250:] if r.agent_id == borrower.agent_id)
            payment_capacity = max(0.0, borrower.money * 0.35 + recent_sg * 0.10)
            payment = min(payment_capacity, loan.outstanding)
            borrower.money -= payment
            loan.outstanding -= payment
            self.public_budget += payment * 0.03  # transaction duty
            if loan.outstanding <= 1.0:
                loan.status = "repaid"
                borrower.reputation = clamp(borrower.reputation + 0.04, 0.02, 1.5)
            else:
                # Failure converts expected loop into cycle debt.
                loan.status = "default"
                default_debt = loan.outstanding * (1.0 + borrower.risk)
                borrower.debt += default_debt
                self.total_cycle_debt += default_debt
                borrower.reputation = clamp(borrower.reputation - 0.08, 0.02, 1.5)
                self.event_log.append(f"t{tick} {self.name}: Kreditausfall {loan.loan_id}, Schuld +{fmt(default_debt)}")

    def _prune_and_merge_identities(self) -> None:
        # Remove negligible dust; merge if identity count is too high.
        self.identities = [i for i in self.identities if i.mass > 0.002]
        if len(self.identities) <= 900:
            return
        # Merge by station and coarse tags to keep PyPy fast in long simulations.
        buckets: Dict[Tuple[int, str], List[Identity]] = {}
        for ident in self.identities:
            key = (ident.station, ident.tags[0] if ident.tags else ident.label)
            buckets.setdefault(key, []).append(ident)
        merged: List[Identity] = []
        for (station, tag), items in buckets.items():
            if len(items) <= 4:
                merged.extend(items)
                continue
            total_mass = sum(i.mass for i in items)
            if total_mass <= 0:
                continue
            owner = max(items, key=lambda i: i.mass).owner_id
            quality = sum(i.quality * i.mass for i in items) / total_mass
            use = sum(i.use * i.mass for i in items) / total_mass
            justice = sum(i.justice * i.mass for i in items) / total_mass
            energy = sum(i.energy for i in items)
            nutrients = sum(i.nutrients for i in items)
            rep = max(i.repetition for i in items)
            ident = Identity(
                identity_id=self.next_id("MRG"),
                label=f"merged_{tag}",
                planet_type=self.kind.code,
                station=station,
                repetition=rep,
                mass=total_mass,
                energy=energy,
                nutrients=nutrients,
                quality=quality,
                use=use,
                justice=justice,
                owner_id=owner,
                generation=max(i.generation for i in items),
                tags=list(sorted({t for i in items for t in i.tags}))[:8],
                history=[f"merged {len(items)} identities at station {station}"],
            )
            merged.append(ident)
        self.identities = merged

    def _update_inflation(self) -> None:
        real_cycle_capacity = (self.stock_mass(7) * 1.2 + self.stock_mass(8) * 1.5 + self.stock_mass(17) * 1.0 +
                               self.soil_fertility * 100.0 + self.water * 60.0 + self.infrastructure * 80.0 +
                               self.technology * 70.0 + 1.0)
        debt_drag = 1.0 + self.total_cycle_debt / max(5000.0, self.money_supply + 1.0)
        raw = self.money_supply / max(real_cycle_capacity * 18.0, 1.0) * debt_drag
        # Blend to avoid violent oscillations.
        self.inflation_index = clamp(self.inflation_index * 0.88 + raw * 0.12, 0.25, 8.0)

    def _take_snapshot(self, tick: int) -> None:
        closed_loop_rate = safe_div(self.stock_mass(17) + self.stock_mass(5), self.stock_mass(13) + self.stock_mass(18) + 1.0, 0.0)
        snap = PlanetSnapshot(
            tick=tick,
            universe=self.universe_name,
            system=self.system_name,
            planet=self.name,
            planet_type=self.kind.code,
            population=self.population,
            health=self.health,
            money_supply=self.money_supply,
            public_budget=self.public_budget,
            inflation_index=self.inflation_index,
            soil_fertility=self.soil_fertility,
            water=self.water,
            microbes=self.microbes,
            heat=self.heat,
            pollution=self.pollution,
            justice_index=self.justice_index,
            infrastructure=self.infrastructure,
            technology=self.technology,
            food_stock=self.stock_mass(8) + self.stock_mass(11) * 0.35 + self.stock_mass(7) * 0.25,
            seed_stock=self.stock_mass(2),
            waste_stock=self.stock_mass(13) + self.stock_mass(18),
            return_stock=self.stock_mass(17) + self.stock_mass(5),
            total_cycle_debt=self.total_cycle_debt,
            verified_sg_tick=self.verified_sg_tick,
            unverified_sg_tick=self.unverified_sg_tick,
            trade_volume_tick=self.trade_volume_tick,
            closed_loop_rate=closed_loop_rate,
        )
        self.snapshots.append(snap)

    # ----------------------------- trade and external operations -----------------------------

    def export_identity(self, station_options: Sequence[int], max_mass: float) -> Optional[Identity]:
        ident = self.find_identity(station_options, min_mass=0.10)
        if not ident:
            return None
        amount = min(max_mass, ident.mass)
        return self._split_identity(ident, amount)

    def import_identity(self, ident: Identity, buyer_agent: Optional[Agent] = None) -> None:
        # Clone to this planet's type if station exists; if station exceeds target kind, map Vulcan ash to fertilizer.
        station = ident.station
        tags = list(ident.tags)
        label = "imported_" + ident.label
        if station > self.kind.cycle_length:
            # Earth cannot hold station 21/22 as native station; imports become station 5 mineral fertilizer.
            station = 5
            label = "imported_mineral_fertilizer"
            if "fertilizer" not in tags:
                tags.append("fertilizer")
        owner_id = buyer_agent.agent_id if buyer_agent else f"STATE-{self.name}"
        new_ident = self._create_identity(label, station, ident.mass, owner_id,
                                          quality=ident.quality * 0.98, use=ident.use,
                                          justice=ident.justice, energy=ident.energy,
                                          nutrients=ident.nutrients, tags=tags + ["import"])
        new_ident.repetition = 1
        new_ident.history.append(f"imported_from:{ident.identity_id}")

    def price_for_station(self, station: int) -> float:
        base = 1.0 + station / float(self.kind.cycle_length)
        scarcity = 1.0 + 1.0 / math.sqrt(max(0.05, self.stock_mass(station)))
        quality = max(0.25, self.avg_quality(station))
        debt = 1.0 + min(1.0, self.total_cycle_debt / max(5000.0, self.money_supply + 1.0))
        inflation = self.inflation_index
        return base * scarcity * quality * debt * inflation

    # ----------------------------- reports -----------------------------

    def top_agents(self, n: int = 5) -> List[Agent]:
        return sorted(self.agents, key=lambda a: (a.sg_earned - a.debt, a.reputation), reverse=True)[:n]

    def final_summary_dict(self) -> Dict[str, object]:
        last = self.snapshots[-1] if self.snapshots else None
        station_masses = {str(k): self.stock_mass(k) for k in range(1, self.kind.cycle_length + 1)}
        return {
            "universe": self.universe_name,
            "system": self.system_name,
            "planet": self.name,
            "planet_type": self.kind.code,
            "cycle_length": self.kind.cycle_length,
            "population": self.population,
            "health": self.health,
            "money_supply": self.money_supply,
            "public_budget": self.public_budget,
            "inflation_index": self.inflation_index,
            "soil_fertility": self.soil_fertility,
            "water": self.water,
            "microbes": self.microbes,
            "heat": self.heat,
            "pollution": self.pollution,
            "justice_index": self.justice_index,
            "infrastructure": self.infrastructure,
            "technology": self.technology,
            "total_cycle_debt": self.total_cycle_debt,
            "identities": len(self.identities),
            "agents": len(self.agents),
            "ledger_records": len(self.ledger),
            "active_loans": len([l for l in self.loans if l.status == "active"]),
            "defaulted_loans": len([l for l in self.loans if l.status == "default"]),
            "repaid_loans": len([l for l in self.loans if l.status == "repaid"]),
            "station_masses": station_masses,
            "last_snapshot": asdict(last) if last else None,
        }


# ---------------------------------------------------------------------------
# Star systems, universes, cosmos
# ---------------------------------------------------------------------------


class StarSystem:
    def __init__(self, universe_name: str, name: str, rng: random.Random,
                 planets_per_system: int, agents_per_planet: int) -> None:
        self.universe_name = universe_name
        self.name = name
        self.rng = rng
        self.planets: List[PlanetEconomy] = []
        self._create_planets(planets_per_system, agents_per_planet)

    def _create_planets(self, n: int, agents_per_planet: int) -> None:
        roots = ["Gaia", "Tellus", "Vesta", "Nysa", "Orion", "Centauri", "Solum", "Aster", "Pyra", "Luma", "Kora"]
        for i in range(n):
            kind = VULCAN_TYPE if self.rng.random() < 0.35 else EARTH_TYPE
            if i == 0 and self.rng.random() < 0.60:
                kind = EARTH_TYPE
            if i == n - 1 and self.rng.random() < 0.45:
                kind = VULCAN_TYPE
            name = f"{self.rng.choice(roots)}-{self.name[-1]}-{i}"
            planet = PlanetEconomy(self.universe_name, self.name, name, kind, self.rng, agents_per_planet)
            self.planets.append(planet)

    def step(self, tick: int) -> None:
        for planet in self.planets:
            planet.step(tick)
        self._interplanetary_trade(tick)

    def _interplanetary_trade(self, tick: int) -> None:
        if len(self.planets) < 2:
            return
        # Food/fertilizer/mineral trade based on station deficits. Values are normalized by UKE.
        pairs = list(self.planets)
        self.rng.shuffle(pairs)
        for buyer in pairs:
            # Determine needs.
            food_need = buyer.population * 0.003
            buyer_food = buyer.stock_mass(8) + 0.35 * buyer.stock_mass(11) + 0.25 * buyer.stock_mass(7)
            buyer_waste = buyer.stock_mass(13) + buyer.stock_mass(18)
            need_type = None
            station_options: Sequence[int] = []
            if buyer_food < food_need:
                need_type = "food"
                station_options = [8, 11, 7]
            elif buyer.soil_fertility < 0.48 or buyer_waste > 20.0:
                need_type = "fertility"
                station_options = [5, 17, 22, 21]
            elif buyer.kind.code == "EarthType" and buyer.rng.random() < 0.03:
                need_type = "mineral"
                station_options = [21, 22, 5]
            if not need_type:
                continue
            sellers = [p for p in self.planets if p is not buyer]
            self.rng.shuffle(sellers)
            for seller in sellers:
                if need_type == "food":
                    surplus = seller.stock_mass(8) + seller.stock_mass(11) * 0.35 + seller.stock_mass(7) * 0.25
                    if surplus < seller.population * 0.004:
                        continue
                    export_options = [8, 11, 7]
                elif need_type == "fertility":
                    if seller.stock_mass(5) + seller.stock_mass(17) + seller.stock_mass(22) < 3.0:
                        continue
                    export_options = [5, 17, 22, 21]
                else:
                    if seller.kind.code != "VulcanType" or seller.stock_mass(21) + seller.stock_mass(22) < 2.0:
                        continue
                    export_options = [21, 22]
                exported = seller.export_identity(export_options, max_mass=self.rng.uniform(0.2, 1.8))
                if not exported:
                    continue
                price = (seller.price_for_station(exported.station) + buyer.price_for_station(min(exported.station, buyer.kind.cycle_length))) / 2.0
                # Normalize by Universal Cycle Units so 20/22 economies can trade without artificial inflation.
                uke_factor = 1.0 / max(0.5, PLANET_KINDS[exported.planet_type].cycle_length / float(buyer.kind.cycle_length))
                trade_value = exported.mass * price * uke_factor * exported.quality * exported.use
                buyer.public_budget -= min(buyer.public_budget * 0.05, trade_value * 0.03)
                seller.public_budget += trade_value * 0.03
                buyer.import_identity(exported)
                seller.trade_volume_tick += trade_value
                buyer.trade_volume_tick += trade_value
                seller.money_supply += trade_value * 0.02
                buyer.money_supply += trade_value * 0.01
                seller.event_log.append(f"t{tick} {seller.name}: Export {need_type} to {buyer.name}, value {fmt(trade_value)}")
                buyer.event_log.append(f"t{tick} {buyer.name}: Import {need_type} from {seller.name}, value {fmt(trade_value)}")
                break

    def all_planets(self) -> List[PlanetEconomy]:
        return list(self.planets)


class Universe:
    def __init__(self, name: str, rng: random.Random, systems: int,
                 planets_per_system: int, agents_per_planet: int) -> None:
        self.name = name
        self.rng = rng
        self.systems: List[StarSystem] = []
        for i in range(systems):
            system = StarSystem(name, f"System-{i}", rng, planets_per_system, agents_per_planet)
            self.systems.append(system)
        self.age = 0
        self.cosmic_events: List[str] = []

    def step(self, tick: int) -> None:
        self.age = tick
        self._cosmic_law_or_shock(tick)
        for system in self.systems:
            system.step(tick)

    def _cosmic_law_or_shock(self, tick: int) -> None:
        roll = self.rng.random()
        planets = self.all_planets()
        if not planets:
            return
        if roll < 0.010:
            # Cosmic signal improves interoperability of UKE accounting.
            for p in planets:
                p.justice_index = clamp(p.justice_index + 0.008, 0.02, 1.5)
                p.technology = clamp(p.technology + 0.004, 0.02, 1.5)
            self.cosmic_events.append(f"t{tick} {self.name}: kosmisches Signal stärkt UKE-Recht und Kommunikation")
        elif roll < 0.018:
            # Radiation damages exposed planets.
            p = self.rng.choice(planets)
            p.pollution = clamp(p.pollution + 0.08, 0.0, 2.0)
            p.health = clamp(p.health - 0.025, 0.05, 1.4)
            p.total_cycle_debt += 80.0
            self.cosmic_events.append(f"t{tick} {self.name}: Strahlungsereignis trifft {p.name}")
        elif roll < 0.026:
            # Interplanetary assembly harmonizes exchange.
            for p in planets:
                p.policy.verification_strictness = clamp(p.policy.verification_strictness + 0.006, 0.20, 0.95)
                p.infrastructure = clamp(p.infrastructure + 0.003, 0.02, 1.5)
            self.cosmic_events.append(f"t{tick} {self.name}: interplanetare Kammern harmonisieren Prüfung und Handel")

    def run(self, ticks: int, progress: bool = False) -> None:
        for tick in range(1, ticks + 1):
            self.step(tick)
            if progress and (tick == 1 or tick % max(1, ticks // 10) == 0):
                print(f"[progress] {self.name}: tick {tick}/{ticks}")

    def all_planets(self) -> List[PlanetEconomy]:
        planets: List[PlanetEconomy] = []
        for system in self.systems:
            planets.extend(system.all_planets())
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
            "cycle_debt": sum(p.total_cycle_debt for p in planets),
            "verified_sg_total": sum(r.effective_sg for p in planets for r in p.ledger),
            "unverified_claim_total": sum(a.sg_unverified for p in planets for a in p.agents),
            "cosmic_events": list(self.cosmic_events[-20:]),
        }


class Cosmos:
    def __init__(self, seed: int, universes: int, systems: int,
                 planets_per_system: int, agents_per_planet: int) -> None:
        self.seed = seed
        self.rng = random.Random(seed)
        self.universes: List[Universe] = []
        for i in range(universes):
            # Each universe receives its own RNG stream for reproducibility.
            rng = random.Random(self.rng.randint(1, 10**12))
            self.universes.append(Universe(f"Universe-{i}", rng, systems, planets_per_system, agents_per_planet))

    def run(self, ticks: int, progress: bool = False) -> None:
        for universe in self.universes:
            universe.run(ticks, progress=progress)
        self._inter_universe_resonance(ticks)

    def _inter_universe_resonance(self, ticks: int) -> None:
        # A small post-run resonance: high-debt universes learn from low-debt universes.
        if len(self.universes) < 2:
            return
        ranked = sorted(self.universes, key=lambda u: u.summary()["cycle_debt"])
        best = ranked[0]
        worst = ranked[-1]
        best_tech = statistics.mean([p.technology for p in best.all_planets()])
        for p in worst.all_planets():
            p.technology = clamp(p.technology + best_tech * 0.002, 0.02, 1.5)
            p.justice_index = clamp(p.justice_index + 0.001, 0.02, 1.5)
        worst.cosmic_events.append(f"t{ticks} kosmische Resonanz: Lernsignal aus {best.name}")

    def all_planets(self) -> List[PlanetEconomy]:
        planets: List[PlanetEconomy] = []
        for u in self.universes:
            planets.extend(u.all_planets())
        return planets

    def summary(self) -> Dict[str, object]:
        universes = [u.summary() for u in self.universes]
        return {
            "seed": self.seed,
            "universes": len(self.universes),
            "total_planets": sum(u["planets"] for u in universes),
            "total_population": sum(u["population"] for u in universes),
            "total_money_supply": sum(u["money_supply"] for u in universes),
            "total_cycle_debt": sum(u["cycle_debt"] for u in universes),
            "total_verified_sg": sum(u["verified_sg_total"] for u in universes),
            "universes_detail": universes,
        }


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


def write_reports(cosmos: Cosmos, report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    # Snapshots CSV.
    snapshot_rows: List[Dict[str, object]] = []
    ledger_rows: List[Dict[str, object]] = []
    agents_rows: List[Dict[str, object]] = []
    identity_samples: List[Dict[str, object]] = []
    for planet in cosmos.all_planets():
        for snap in planet.snapshots:
            snapshot_rows.append(asdict(snap))
        for rec in planet.ledger:
            ledger_rows.append(asdict(rec))
        for agent in planet.agents:
            d = asdict(agent)
            d["universe"] = planet.universe_name
            d["system"] = planet.system_name
            d["planet_type"] = planet.kind.code
            agents_rows.append(d)
        # Keep identity sample limited.
        for ident in sorted(planet.identities, key=lambda x: x.mass, reverse=True)[:30]:
            identity_samples.append(ident.passport() | {"universe": planet.universe_name, "system": planet.system_name, "planet": planet.name})

    if snapshot_rows:
        write_csv(report_dir / "snapshots.csv", snapshot_rows, list(snapshot_rows[0].keys()))
    if ledger_rows:
        write_csv(report_dir / "ledger.csv", ledger_rows, list(ledger_rows[0].keys()))
    if agents_rows:
        write_csv(report_dir / "agents.csv", agents_rows, list(agents_rows[0].keys()))
    if identity_samples:
        write_csv(report_dir / "identity_samples.csv", identity_samples, list(identity_samples[0].keys()))

    with (report_dir / "final_state.json").open("w", encoding="utf-8") as f:
        json.dump({
            "cosmos": cosmos.summary(),
            "planets": [p.final_summary_dict() for p in cosmos.all_planets()],
        }, f, ensure_ascii=False, indent=2)
    with (report_dir / "final_report.md").open("w", encoding="utf-8") as f:
        f.write(render_markdown_report(cosmos))


def render_markdown_report(cosmos: Cosmos) -> str:
    summary = cosmos.summary()
    lines: List[str] = []
    lines.append("# Universum-Kreislaufwirtschaft — Simulationsbericht\n")
    lines.append("## Kosmos-Zusammenfassung\n")
    lines.append(f"- Seed: `{summary['seed']}`")
    lines.append(f"- Universen: `{summary['universes']}`")
    lines.append(f"- Planeten: `{summary['total_planets']}`")
    lines.append(f"- Bevölkerung gesamt: `{fmt(summary['total_population'])}`")
    lines.append(f"- Geldmenge gesamt: `{fmt(summary['total_money_supply'])} SG`")
    lines.append(f"- Kreislaufschuld gesamt: `{fmt(summary['total_cycle_debt'])}`")
    lines.append(f"- Verifizierte Schleifenwährung: `{fmt(summary['total_verified_sg'])} SG`\n")
    lines.append("## Planetentabelle\n")
    lines.append("| Universum | System | Planet | Typ | N | Pop. | Gesundheit | Inflation | Boden | Wasser | Mikroben | Pollution | Schuld | SG verifiziert |")
    lines.append("|---|---|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|")
    for p in cosmos.all_planets():
        verified = sum(r.effective_sg for r in p.ledger)
        lines.append(
            f"| {p.universe_name} | {p.system_name} | {p.name} | {p.kind.label_de} | {p.kind.cycle_length} | "
            f"{fmt(p.population)} | {p.health:.2f} | {p.inflation_index:.2f} | {p.soil_fertility:.2f} | "
            f"{p.water:.2f} | {p.microbes:.2f} | {p.pollution:.2f} | {fmt(p.total_cycle_debt)} | {fmt(verified)} |"
        )
    lines.append("\n## Top-Agenten je Planet\n")
    for p in cosmos.all_planets():
        lines.append(f"### {p.name} ({p.kind.label_de}, N={p.kind.cycle_length})\n")
        lines.append("| Rang | Agent | Rolle | SG verdient | Geld | Schuld | Fairness | Reputation |")
        lines.append("|---:|---|---|---:|---:|---:|---:|---:|")
        for idx, agent in enumerate(p.top_agents(5), 1):
            lines.append(f"| {idx} | {agent.name} | {agent.role} | {fmt(agent.sg_earned)} | {fmt(agent.money)} | {fmt(agent.debt)} | {agent.fairness:.2f} | {agent.reputation:.2f} |")
        lines.append("")
    lines.append("## Jüngste Ereignisse\n")
    for u in cosmos.universes:
        for ev in u.cosmic_events[-10:]:
            lines.append(f"- {ev}")
    for p in cosmos.all_planets():
        for ev in p.event_log[-5:]:
            lines.append(f"- {ev}")
    lines.append("\n## Stationsalphabet\n")
    lines.append("| Nr. | Buchstabe | Deutsch | English | Domäne |")
    lines.append("|---:|---|---|---|---|")
    for i in range(1, 23):
        s = STATIONS[i]
        lines.append(f"| {s.no} | {s.letter} | {s.name_de} | {s.name_en} | {s.domain} |")
    lines.append("\n## Währungsformel\n")
    lines.append("```text")
    lines.append("SG_roh = (r - 1) * N + e - s")
    lines.append("N(EarthType) = 20")
    lines.append("N(VulcanType) = 22")
    lines.append("SG_stack = Σ SG_roh_i * M_i * Q_i * U_i * G_i")
    lines.append("UKE = SG_roh / N")
    lines.append("```\n")
    return "\n".join(lines)


def print_console_summary(cosmos: Cosmos) -> None:
    summary = cosmos.summary()
    print("\n=== Universum-Kreislaufwirtschaft Simulation ===")
    print(f"Seed: {summary['seed']}")
    print(f"Universen: {summary['universes']} | Planeten: {summary['total_planets']}")
    print(f"Bevölkerung: {fmt(summary['total_population'])}")
    print(f"Geldmenge: {fmt(summary['total_money_supply'])} SG")
    print(f"Kreislaufschuld: {fmt(summary['total_cycle_debt'])}")
    print(f"Verifizierte SG: {fmt(summary['total_verified_sg'])}")
    print("\nPlaneten:")
    for p in cosmos.all_planets():
        verified = sum(r.effective_sg for r in p.ledger)
        print(
            f"- {p.name:14s} {p.kind.code:10s} N={p.kind.cycle_length:2d} "
            f"Pop={fmt(p.population):>8s} Health={p.health:.2f} Infl={p.inflation_index:.2f} "
            f"Soil={p.soil_fertility:.2f} Water={p.water:.2f} Microbes={p.microbes:.2f} "
            f"Poll={p.pollution:.2f} Debt={fmt(p.total_cycle_debt):>8s} SG={fmt(verified):>8s}"
        )
    print("\nBeispiele der Kernformel:")
    print(f"- EarthType:  start=4, end=17, repetition=4 => {loop_value('EarthType', 4, 17, 4)} SG")
    print(f"- VulcanType: start=4, end=17, repetition=4 => {loop_value('VulcanType', 4, 17, 4)} SG")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args(argv: Optional[Sequence[str]] = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="PyPy3 simulation of the Universe Circular Economy: stacked for-loop currency, Earth/Vulcan planet cycles, markets, debt and trade."
    )
    parser.add_argument("--seed", type=int, default=73, help="Random seed for reproducibility.")
    parser.add_argument("--ticks", type=int, default=60, help="Number of simulation ticks.")
    parser.add_argument("--universes", type=int, default=1, help="Number of universes inside the cosmos.")
    parser.add_argument("--systems", type=int, default=2, help="Star systems per universe.")
    parser.add_argument("--planets-per-system", type=int, default=3, help="Planets per star system.")
    parser.add_argument("--agents-per-planet", type=int, default=45, help="Agents per planet.")
    parser.add_argument("--report-dir", type=str, default="uce_report", help="Directory for CSV/JSON/Markdown reports. Use empty string to disable.")
    parser.add_argument("--progress", action="store_true", help="Print progress while running.")
    parser.add_argument("--no-files", action="store_true", help="Do not write report files.")
    return parser.parse_args(argv)


def main(argv: Optional[Sequence[str]] = None) -> int:
    args = parse_args(argv)
    if args.ticks < 1:
        print("ticks must be >= 1", file=sys.stderr)
        return 2
    if args.universes < 1 or args.systems < 1 or args.planets_per_system < 1 or args.agents_per_planet < 1:
        print("universes/systems/planets/agents must be >= 1", file=sys.stderr)
        return 2
    cosmos = Cosmos(
        seed=args.seed,
        universes=args.universes,
        systems=args.systems,
        planets_per_system=args.planets_per_system,
        agents_per_planet=args.agents_per_planet,
    )
    cosmos.run(args.ticks, progress=args.progress)
    print_console_summary(cosmos)
    if not args.no_files and args.report_dir:
        report_dir = Path(args.report_dir)
        write_reports(cosmos, report_dir)
        print(f"\nBerichte geschrieben nach: {report_dir.resolve()}")
        print("- final_report.md")
        print("- final_state.json")
        print("- snapshots.csv")
        print("- ledger.csv")
        print("- agents.csv")
        print("- identity_samples.csv")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
