#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Planetare Wirtschaftssimulation mit gestapelter Wahrheitswert-Währung.

Version: OOP/UTF-8 Edition

Diese Variante ist absichtlich stark objektorientiert gebaut:
- tiefe Vererbungshierarchien für Akteure, Firmen, Institutionen, Produkte,
  Claims, Transaktionen, Märkte, Ereignisse und Renderer
- globale Wahrheitswert-Währung WK als Vektor aus vielen Wahrheitsdimensionen
- nationale Fiat-Währungen je Land plus Zentralbanken und Geschäftsbanken
- UN-ähnliche Institution, Verteidigungsorganisationen, Sanktionen, Audits,
  Kriege, Krisen, technologische Durchbrüche, Wahrheitsblasen und Schulden
- am Ende werden viele UTF-8/Unicode-Diagramme als Textreport erzeugt

Start:
    python planet_truth_economy_oop_utf8_sim.py --preset tiny --months 24 --verbose
    python planet_truth_economy_oop_utf8_sim.py --preset standard --months 120 --seed 7 --out sim_output
    python planet_truth_economy_oop_utf8_sim.py --preset epic --months 720 --seed 42 --out epic_world

Nur Standardbibliothek. Keine externen Pakete nötig.
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import random
import statistics
import textwrap
import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple, Type


# =============================================================================
# 1. Kleine numerische und textuelle Hilfsfunktionen
# =============================================================================


def uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    return a / b if abs(b) > 1e-12 else default


def mean_or(values: Iterable[float], default: float = 0.0) -> float:
    values = list(values)
    return statistics.mean(values) if values else default


def weighted_choice(rng: random.Random, items: Sequence[Any], weights: Sequence[float]) -> Any:
    if not items:
        return None
    total = sum(max(0.0, w) for w in weights)
    if total <= 0.0:
        return rng.choice(list(items))
    r = rng.random() * total
    acc = 0.0
    for item, weight in zip(items, weights):
        acc += max(0.0, weight)
        if acc >= r:
            return item
    return items[-1]


def fmt_money(x: float) -> str:
    if abs(x) >= 1_000_000_000_000:
        return f"{x/1_000_000_000_000:,.2f}T"
    if abs(x) >= 1_000_000_000:
        return f"{x/1_000_000_000:,.2f}B"
    if abs(x) >= 1_000_000:
        return f"{x/1_000_000:,.2f}M"
    if abs(x) >= 1_000:
        return f"{x/1_000:,.2f}K"
    return f"{x:,.2f}"


def pct(x: float) -> str:
    return f"{100.0*x:.2f}%"


def slug(text: str) -> str:
    keep = []
    for ch in text.lower():
        if ch.isalnum():
            keep.append(ch)
        elif ch in " -_/":
            keep.append("_")
    s = "".join(keep).strip("_")
    while "__" in s:
        s = s.replace("__", "_")
    return s or "x"


# =============================================================================
# 2. Wahrheitsdimensionen und vektorwertige WK-Währung
# =============================================================================


class TruthLayer(str, Enum):
    EXISTENCE = "existence"
    EPISTEMIC = "epistemic"
    SOCIAL = "social"
    LEGAL = "legal"
    CAUSAL = "causal"
    TEMPORAL = "temporal"
    RISK_REDUCTION = "risk_reduction"
    POTENTIAL = "potential"
    PERCEPTION = "perception"
    COMPARATIVE = "comparative"
    SECURITY = "security"
    LIQUIDITY = "liquidity"
    ETHICAL = "ethical"
    ECOLOGICAL = "ecological"
    INFRASTRUCTURE = "infrastructure"
    HEALTH = "health"
    ATTENTION = "attention"
    MEMORY = "memory"
    LOGISTICS = "logistics"
    ENERGY = "energy"
    FOOD = "food"
    SHELTER = "shelter"
    EDUCATION = "education"
    SOVEREIGNTY = "sovereignty"


ALL_TRUTH_LAYERS: Tuple[str, ...] = tuple(layer.value for layer in TruthLayer)

TRUTH_WEIGHTS: Dict[str, float] = {
    TruthLayer.EXISTENCE.value: 1.05,
    TruthLayer.EPISTEMIC.value: 1.35,
    TruthLayer.SOCIAL.value: 0.90,
    TruthLayer.LEGAL.value: 1.20,
    TruthLayer.CAUSAL.value: 1.40,
    TruthLayer.TEMPORAL.value: 0.85,
    TruthLayer.RISK_REDUCTION.value: 1.15,
    TruthLayer.POTENTIAL.value: 1.25,
    TruthLayer.PERCEPTION.value: 0.75,
    TruthLayer.COMPARATIVE.value: 0.80,
    TruthLayer.SECURITY.value: 1.40,
    TruthLayer.LIQUIDITY.value: 1.00,
    TruthLayer.ETHICAL.value: 1.00,
    TruthLayer.ECOLOGICAL.value: 1.10,
    TruthLayer.INFRASTRUCTURE.value: 1.35,
    TruthLayer.HEALTH.value: 1.40,
    TruthLayer.ATTENTION.value: 0.70,
    TruthLayer.MEMORY.value: 0.65,
    TruthLayer.LOGISTICS.value: 1.10,
    TruthLayer.ENERGY.value: 1.20,
    TruthLayer.FOOD.value: 1.20,
    TruthLayer.SHELTER.value: 1.15,
    TruthLayer.EDUCATION.value: 1.10,
    TruthLayer.SOVEREIGNTY.value: 1.45,
}

POSITIVE_DECAY: Dict[str, float] = {
    TruthLayer.EXISTENCE.value: 0.001,
    TruthLayer.EPISTEMIC.value: 0.004,
    TruthLayer.SOCIAL.value: 0.008,
    TruthLayer.LEGAL.value: 0.002,
    TruthLayer.CAUSAL.value: 0.006,
    TruthLayer.TEMPORAL.value: 0.030,
    TruthLayer.RISK_REDUCTION.value: 0.010,
    TruthLayer.POTENTIAL.value: 0.014,
    TruthLayer.PERCEPTION.value: 0.045,
    TruthLayer.COMPARATIVE.value: 0.025,
    TruthLayer.SECURITY.value: 0.015,
    TruthLayer.LIQUIDITY.value: 0.006,
    TruthLayer.ETHICAL.value: 0.006,
    TruthLayer.ECOLOGICAL.value: 0.003,
    TruthLayer.INFRASTRUCTURE.value: 0.004,
    TruthLayer.HEALTH.value: 0.004,
    TruthLayer.ATTENTION.value: 0.065,
    TruthLayer.MEMORY.value: 0.010,
    TruthLayer.LOGISTICS.value: 0.008,
    TruthLayer.ENERGY.value: 0.006,
    TruthLayer.FOOD.value: 0.020,
    TruthLayer.SHELTER.value: 0.003,
    TruthLayer.EDUCATION.value: 0.006,
    TruthLayer.SOVEREIGNTY.value: 0.004,
}

NEGATIVE_GROWTH: Dict[str, float] = {
    TruthLayer.EXISTENCE.value: 0.004,
    TruthLayer.EPISTEMIC.value: 0.020,
    TruthLayer.SOCIAL.value: 0.012,
    TruthLayer.LEGAL.value: 0.014,
    TruthLayer.CAUSAL.value: 0.008,
    TruthLayer.TEMPORAL.value: 0.024,
    TruthLayer.RISK_REDUCTION.value: 0.012,
    TruthLayer.POTENTIAL.value: 0.009,
    TruthLayer.PERCEPTION.value: 0.010,
    TruthLayer.COMPARATIVE.value: 0.006,
    TruthLayer.SECURITY.value: 0.014,
    TruthLayer.LIQUIDITY.value: 0.016,
    TruthLayer.ETHICAL.value: 0.014,
    TruthLayer.ECOLOGICAL.value: 0.008,
    TruthLayer.INFRASTRUCTURE.value: 0.007,
    TruthLayer.HEALTH.value: 0.008,
    TruthLayer.ATTENTION.value: 0.006,
    TruthLayer.MEMORY.value: 0.005,
    TruthLayer.LOGISTICS.value: 0.007,
    TruthLayer.ENERGY.value: 0.010,
    TruthLayer.FOOD.value: 0.014,
    TruthLayer.SHELTER.value: 0.010,
    TruthLayer.EDUCATION.value: 0.007,
    TruthLayer.SOVEREIGNTY.value: 0.018,
}


class LayeredValue(ABC):
    """Abstrakte Grundlage für vektorwertige Werte.

    WK ist nicht einfach Geld, sondern ein mehrdimensionaler Anspruch auf
    Realität. Diese Basisklasse hält die Dimensionen; Unterklassen bestimmen,
    wie Alterung, Score und negative Werte interpretiert werden.
    """

    KIND = "layered"

    def __init__(self, values: Optional[Dict[str, float]] = None) -> None:
        self.values: Dict[str, float] = {layer: 0.0 for layer in ALL_TRUTH_LAYERS}
        if values:
            for k, v in values.items():
                if k in self.values:
                    self.values[k] = float(v)

    def copy(self) -> "LayeredValue":
        return self.__class__(self.values.copy())

    def add(self, other: "LayeredValue") -> "LayeredValue":
        for k in self.values:
            self.values[k] += other.values.get(k, 0.0)
        return self

    def subtract(self, other: "LayeredValue") -> "LayeredValue":
        for k in self.values:
            self.values[k] -= other.values.get(k, 0.0)
        return self

    def scaled(self, factor: float) -> "LayeredValue":
        return self.__class__({k: v * factor for k, v in self.values.items()})

    def clamp_components(self, lo: float, hi: float) -> "LayeredValue":
        for k in self.values:
            self.values[k] = clamp(self.values[k], lo, hi)
        return self

    def abs_sum(self) -> float:
        return sum(abs(v) for v in self.values.values())

    def positive_sum(self) -> float:
        return sum(max(0.0, v) for v in self.values.values())

    def negative_sum(self) -> float:
        return sum(min(0.0, v) for v in self.values.values())

    def score(self, weights: Optional[Dict[str, float]] = None) -> float:
        weights = weights or TRUTH_WEIGHTS
        return sum(self.values[k] * weights.get(k, 1.0) for k in self.values)

    def positive_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        weights = weights or TRUTH_WEIGHTS
        return sum(max(0.0, self.values[k]) * weights.get(k, 1.0) for k in self.values)

    def negative_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        weights = weights or TRUTH_WEIGHTS
        return sum(min(0.0, self.values[k]) * weights.get(k, 1.0) for k in self.values)

    def dominant(self, n: int = 5, positive: bool = True) -> List[Tuple[str, float]]:
        items = list(self.values.items())
        if positive:
            items = [(k, v) for k, v in items if v > 0]
            items.sort(key=lambda kv: kv[1], reverse=True)
        else:
            items = [(k, v) for k, v in items if v < 0]
            items.sort(key=lambda kv: kv[1])
        return items[:n]

    def as_dict(self) -> Dict[str, float]:
        return dict(self.values)

    @classmethod
    def zero(cls) -> "LayeredValue":
        return cls()

    @classmethod
    def from_profile(cls, profile: Dict[str, float], scale: float = 1.0) -> "LayeredValue":
        return cls({k: profile.get(k, 0.0) * scale for k in ALL_TRUTH_LAYERS})


class DecayingLayeredValue(LayeredValue):
    KIND = "decaying_layered"

    def age_one_month(self) -> "DecayingLayeredValue":
        for k, v in list(self.values.items()):
            if v >= 0:
                self.values[k] = v * (1.0 - POSITIVE_DECAY.get(k, 0.01))
            else:
                self.values[k] = v * (1.0 + NEGATIVE_GROWTH.get(k, 0.01))
        return self


class TruthStack(DecayingLayeredValue):
    """WK: globale gestapelte Wahrheitswert-Währung.

    Positive Komponenten: gedeckte Existenz, Recht, Funktion, Anerkennung usw.
    Negative Komponenten: Schulden, falsche Claims, Zukunftspflichten,
    Lügenlasten, uneingelöste Versprechen.
    """

    KIND = "truth_stack"

    @classmethod
    def mint(cls, profile: Dict[str, float], scale: float = 1.0) -> "TruthStack":
        return cls.from_profile(profile, scale)  # type: ignore[return-value]

    @classmethod
    def debt(cls, profile: Dict[str, float], scale: float = 1.0) -> "TruthStack":
        return cls({k: -abs(profile.get(k, 0.0) * scale) for k in ALL_TRUTH_LAYERS})

    @classmethod
    def random_positive(cls, rng: random.Random, scale: float) -> "TruthStack":
        return cls({k: rng.random() * scale for k in ALL_TRUTH_LAYERS})

    def truth_gap(self) -> float:
        pos = self.positive_score()
        neg = abs(self.negative_score())
        return safe_div(neg, pos + neg + 1e-9)


class FiatDebtStack(TruthStack):
    """Negative WK-Komponente, die entsteht, wenn Fiat-Kredite Zukunft binden."""

    KIND = "fiat_debt_truth"


class EpistemicDebtStack(TruthStack):
    """Negative WK-Komponente bei falschen Versprechen, Betrug oder Illusion."""

    KIND = "epistemic_debt_truth"


class SecurityDebtStack(TruthStack):
    """Negative WK-Komponente bei ungeklärten Konflikten und Sicherheitsrisiken."""

    KIND = "security_debt_truth"


# =============================================================================
# 3. Geld- und Wallet-Hierarchie
# =============================================================================


class Currency(ABC):
    def __init__(self, code: str, name: str) -> None:
        self.code = code
        self.name = name

    def __repr__(self) -> str:
        return f"{self.code}({self.name})"


class ScalarCurrency(Currency):
    pass


class FiatCurrency(ScalarCurrency):
    def __init__(self, code: str, name: str, issuing_country: str) -> None:
        super().__init__(code, name)
        self.issuing_country = issuing_country


class PlanetaryCurrency(Currency):
    pass


class TruthCurrency(PlanetaryCurrency):
    def __init__(self) -> None:
        super().__init__("WK", "Wahrheitskapital / Truth Capital")


class Wallet(ABC):
    @abstractmethod
    def total_reference_value(self, planet: "Planet") -> float:
        raise NotImplementedError


class FiatWallet(Wallet):
    def __init__(self) -> None:
        self.balances: Dict[str, float] = {}

    def get(self, code: str) -> float:
        return self.balances.get(code, 0.0)

    def deposit(self, code: str, amount: float) -> None:
        self.balances[code] = self.get(code) + amount

    def withdraw(self, code: str, amount: float) -> bool:
        if self.get(code) >= amount:
            self.balances[code] = self.get(code) - amount
            return True
        # negative Fiat is allowed as overdraft, but costly in truth terms
        self.balances[code] = self.get(code) - amount
        return False

    def total_reference_value(self, planet: "Planet") -> float:
        return sum(amount * planet.fx_to_reference(code) for code, amount in self.balances.items())

    def as_dict(self) -> Dict[str, float]:
        return dict(self.balances)


class TruthWallet(Wallet):
    def __init__(self) -> None:
        self.balance = TruthStack()
        self.escrow = TruthStack()

    def deposit(self, stack: TruthStack) -> None:
        self.balance.add(stack)

    def withdraw(self, stack: TruthStack) -> None:
        self.balance.subtract(stack)

    def incur_debt(self, stack: TruthStack) -> None:
        self.balance.add(stack)

    def age(self) -> None:
        self.balance.age_one_month()
        self.escrow.age_one_month()

    def total_reference_value(self, planet: "Planet") -> float:
        return self.balance.score() * planet.truth_price_reference

    def as_dict(self) -> Dict[str, float]:
        return self.balance.as_dict()


class MultiCurrencyWallet(Wallet):
    def __init__(self) -> None:
        self.fiat = FiatWallet()
        self.truth = TruthWallet()

    def total_reference_value(self, planet: "Planet") -> float:
        return self.fiat.total_reference_value(planet) + self.truth.total_reference_value(planet)

    def age_truth(self) -> None:
        self.truth.age()


# =============================================================================
# 4. Entitäten-Hierarchie: alles lebt als SimNode im Planeten
# =============================================================================


class IdentifiedEntity:
    TYPE = "identified"

    def __init__(self, name: str, prefix: str = "entity") -> None:
        self.id = uid(prefix)
        self.name = name


class TimestampedEntity(IdentifiedEntity):
    TYPE = "timestamped"

    def __init__(self, name: str, prefix: str = "entity") -> None:
        super().__init__(name, prefix)
        self.created_month = 0
        self.last_active_month = 0


class SimNode(TimestampedEntity):
    TYPE = "simnode"

    def __init__(self, name: str, prefix: str = "node") -> None:
        super().__init__(name, prefix)
        self.wallet = MultiCurrencyWallet()
        self.alive = True
        self.trust = 1.0
        self.reputation = 1.0
        self.risk = 0.1
        self.local_log: List[str] = []

    def age_truth(self) -> None:
        self.wallet.age_truth()

    def receive_fiat(self, currency: str, amount: float) -> None:
        self.wallet.fiat.deposit(currency, amount)

    def pay_fiat(self, currency: str, amount: float) -> bool:
        return self.wallet.fiat.withdraw(currency, amount)

    def receive_truth(self, stack: TruthStack) -> None:
        self.wallet.truth.deposit(stack)

    def pay_truth(self, stack: TruthStack) -> None:
        self.wallet.truth.withdraw(stack)

    def incur_truth_debt(self, stack: TruthStack) -> None:
        self.wallet.truth.incur_debt(stack)

    def wk_score(self) -> float:
        return self.wallet.truth.balance.score()

    def step(self, planet: "Planet") -> None:
        self.last_active_month = planet.month


class Agent(SimNode):
    TYPE = "agent"

    def decide(self, planet: "Planet") -> None:
        pass

    def step(self, planet: "Planet") -> None:
        super().step(planet)
        self.decide(planet)


class LegalEntity(Agent):
    TYPE = "legal_entity"

    def __init__(self, name: str, prefix: str = "legal") -> None:
        super().__init__(name, prefix)
        self.legal_integrity = 1.0
        self.audit_pressure = 0.0


class InstitutionalEntity(LegalEntity):
    TYPE = "institution"

    def __init__(self, name: str, prefix: str = "inst") -> None:
        super().__init__(name, prefix)
        self.mandate_strength = 1.0
        self.members: List["Country"] = []

    def add_member(self, country: "Country") -> None:
        if country not in self.members:
            self.members.append(country)


class SovereignEntity(InstitutionalEntity):
    TYPE = "sovereign"

    def __init__(self, name: str, prefix: str = "sovereign") -> None:
        super().__init__(name, prefix)
        self.sovereignty = 1.0


class EconomicEntity(LegalEntity):
    TYPE = "economic_entity"

    def __init__(self, name: str, country: Optional["Country"], prefix: str = "econ") -> None:
        super().__init__(name, prefix)
        self.country = country
        self.employees = 0
        self.revenue_last_month = 0.0
        self.profit_last_month = 0.0


class Household(EconomicEntity):
    TYPE = "household"

    def __init__(self, name: str, country: "Country", population: int) -> None:
        super().__init__(name, country, "house")
        self.population = population
        self.needs_pressure = 1.0


# =============================================================================
# 5. Staaten, Zentralbanken, Banken und Institutionen
# =============================================================================


class Country(SovereignEntity):
    TYPE = "country"

    def __init__(
        self,
        name: str,
        currency: FiatCurrency,
        population: int,
        gdp: float,
        archetype: str,
        rng: random.Random,
    ) -> None:
        super().__init__(name, "country")
        self.currency = currency
        self.population = population
        self.gdp = gdp
        self.archetype = archetype
        self.inflation = rng.uniform(0.01, 0.09)
        self.unemployment = rng.uniform(0.03, 0.17)
        self.tax_rate = rng.uniform(0.14, 0.34)
        self.stability = rng.uniform(0.45, 0.92)
        self.corruption = rng.uniform(0.02, 0.30)
        self.openness = rng.uniform(0.25, 0.95)
        self.research_level = rng.uniform(0.20, 0.90)
        self.defense_need = rng.uniform(0.05, 0.55)
        self.ecological_pressure = rng.uniform(0.05, 0.60)
        self.public_debt = gdp * rng.uniform(0.20, 1.60)
        self.central_bank: Optional[CentralBank] = None
        self.banks: List[CommercialBank] = []
        self.companies: List[Company] = []
        self.households: List[Household] = []
        self.alliances: List[DefenseOrganization] = []
        self.needs: Dict[str, float] = {
            "food": rng.uniform(0.6, 1.4),
            "shelter": rng.uniform(0.6, 1.4),
            "energy": rng.uniform(0.6, 1.4),
            "health": rng.uniform(0.6, 1.4),
            "education": rng.uniform(0.6, 1.4),
            "mobility": rng.uniform(0.6, 1.4),
            "security": rng.uniform(0.5, 1.5),
            "attention": rng.uniform(0.5, 1.5),
            "luxury": rng.uniform(0.3, 1.5),
            "infrastructure": rng.uniform(0.7, 1.6),
        }
        self.receive_fiat(currency.code, gdp * 0.08)
        self.receive_truth(TruthStack.mint({
            TruthLayer.LEGAL.value: 10.0,
            TruthLayer.SOCIAL.value: 8.0,
            TruthLayer.SOVEREIGNTY.value: 12.0,
            TruthLayer.INFRASTRUCTURE.value: 5.0,
            TruthLayer.SECURITY.value: 4.0,
        }, scale=max(1.0, math.log10(gdp))))

    def decide(self, planet: "Planet") -> None:
        # Steuere makroökonomische Variablen.
        self.inflation = clamp(
            self.inflation
            + planet.rng.uniform(-0.008, 0.009)
            + safe_div(self.public_debt, self.gdp, 0.0) * 0.0008
            - self.stability * 0.0015,
            -0.03,
            0.35,
        )
        self.unemployment = clamp(
            self.unemployment
            + planet.rng.uniform(-0.01, 0.012)
            - 0.000001 * len(self.companies) * mean_or([c.productivity for c in self.companies], 1.0),
            0.01,
            0.65,
        )
        # Negative Wahrheit, wenn öffentliche Schulden exzessiv werden.
        debt_ratio = safe_div(self.public_debt, max(1.0, self.gdp))
        if debt_ratio > 1.25:
            self.incur_truth_debt(FiatDebtStack.debt({
                TruthLayer.LIQUIDITY.value: debt_ratio * 0.05,
                TruthLayer.TEMPORAL.value: debt_ratio * 0.03,
                TruthLayer.LEGAL.value: debt_ratio * 0.02,
            }))
        # Fiskalischer Multiplikator: Ausgaben können WK erzeugen, aber Fiat-Schulden erhöhen.
        public_spend = self.gdp * clamp(0.012 + self.tax_rate * 0.015, 0.005, 0.025)
        self.public_debt += public_spend * (0.4 + self.corruption)
        self.gdp *= 1.0 + clamp(0.002 + self.openness * 0.002 - self.inflation * 0.010 - self.unemployment * 0.004, -0.03, 0.05)
        if planet.month % 6 == 0:
            self.receive_truth(TruthStack.mint({
                TruthLayer.INFRASTRUCTURE.value: public_spend / 2e9,
                TruthLayer.HEALTH.value: public_spend / 3e9,
                TruthLayer.EDUCATION.value: public_spend / 4e9,
                TruthLayer.SOCIAL.value: self.stability * 0.2,
            }))

    def collect_taxes(self, planet: "Planet") -> float:
        collected = 0.0
        for firm in self.companies:
            tax = max(0.0, firm.profit_last_month) * self.tax_rate
            if tax:
                firm.pay_fiat(self.currency.code, tax)
                self.receive_fiat(self.currency.code, tax)
                collected += tax
        self.public_debt = max(0.0, self.public_debt - collected * 0.25)
        return collected

    def average_company_truth_gap(self) -> float:
        return mean_or([c.wallet.truth.balance.truth_gap() for c in self.companies], 0.0)


class FinancialInstitution(InstitutionalEntity):
    TYPE = "financial_institution"

    def __init__(self, name: str, country: Optional[Country], prefix: str = "fin") -> None:
        super().__init__(name, prefix)
        self.country = country
        self.assets = 0.0
        self.liabilities = 0.0
        self.capital_ratio = 0.10

    def solvency(self) -> float:
        return safe_div(self.assets - self.liabilities, max(1.0, self.assets), 0.0)


class CentralBank(FinancialInstitution):
    TYPE = "central_bank"

    def __init__(self, name: str, country: Country) -> None:
        super().__init__(name, country, "cb")
        self.policy_rate = 0.035
        self.reserve_requirement = 0.08
        self.fx_reserves = country.gdp * 0.10
        self.mandate_strength = 1.2
        self.receive_fiat(country.currency.code, self.fx_reserves)
        self.receive_truth(TruthStack.mint({
            TruthLayer.LIQUIDITY.value: 8,
            TruthLayer.LEGAL.value: 6,
            TruthLayer.EPISTEMIC.value: 4,
        }, scale=max(1.0, math.log10(country.gdp))))

    def decide(self, planet: "Planet") -> None:
        if not self.country:
            return
        c = self.country
        target = 0.025
        self.policy_rate = clamp(
            self.policy_rate + (c.inflation - target) * 0.12 + (1.0 - c.stability) * 0.005,
            -0.01,
            0.28,
        )
        # Glaubwürdigkeit der Zentralbank als Wahrheitswert.
        if abs(c.inflation - target) < 0.02:
            self.receive_truth(TruthStack.mint({TruthLayer.EPISTEMIC.value: 0.10, TruthLayer.SOCIAL.value: 0.06}))
        else:
            self.incur_truth_debt(EpistemicDebtStack.debt({TruthLayer.EPISTEMIC.value: abs(c.inflation - target) * 0.20}))


class CommercialBank(FinancialInstitution):
    TYPE = "commercial_bank"

    def __init__(self, name: str, country: Country, rng: random.Random) -> None:
        super().__init__(name, country, "bank")
        self.deposit_base = country.gdp * rng.uniform(0.02, 0.12)
        self.loan_book = country.gdp * rng.uniform(0.01, 0.09)
        self.nonperforming_ratio = rng.uniform(0.01, 0.12)
        self.assets = self.deposit_base + self.loan_book
        self.liabilities = self.deposit_base * rng.uniform(0.80, 1.10)
        self.capital_ratio = rng.uniform(0.06, 0.18)
        self.receive_fiat(country.currency.code, self.deposit_base * 0.05)

    def decide(self, planet: "Planet") -> None:
        if not self.country or not self.country.companies:
            return
        c = self.country
        cb_rate = c.central_bank.policy_rate if c.central_bank else 0.04
        # Kredite an Firmen: positive Potenziale, aber negative Zukunftsbindung.
        if planet.rng.random() < 0.32 and self.solvency() > -0.06:
            borrower = weighted_choice(planet.rng, c.companies, [max(1.0, f.productivity * f.reputation) for f in c.companies])
            if borrower:
                amount = c.gdp * planet.rng.uniform(0.00005, 0.0015)
                rate = cb_rate + planet.rng.uniform(0.015, 0.08) + borrower.risk * 0.04
                tx = LoanOriginationTransaction(self, borrower, c.currency.code, amount, rate, maturity_months=planet.rng.randint(12, 96))
                planet.ledger.execute(tx, planet)
        # Bankenstress.
        self.nonperforming_ratio = clamp(
            self.nonperforming_ratio + c.unemployment * 0.002 + planet.rng.uniform(-0.006, 0.007),
            0.0,
            0.70,
        )
        if self.nonperforming_ratio > 0.18:
            self.incur_truth_debt(FiatDebtStack.debt({
                TruthLayer.LIQUIDITY.value: self.nonperforming_ratio * 0.4,
                TruthLayer.EPISTEMIC.value: self.nonperforming_ratio * 0.2,
                TruthLayer.SOCIAL.value: self.nonperforming_ratio * 0.2,
            }))


class DevelopmentBank(CommercialBank):
    TYPE = "development_bank"

    def decide(self, planet: "Planet") -> None:
        super().decide(planet)
        if self.country and planet.rng.random() < 0.22:
            self.country.receive_truth(TruthStack.mint({
                TruthLayer.INFRASTRUCTURE.value: 0.4,
                TruthLayer.EDUCATION.value: 0.2,
                TruthLayer.POTENTIAL.value: 0.25,
            }))


class InvestmentBank(CommercialBank):
    TYPE = "investment_bank"

    def decide(self, planet: "Planet") -> None:
        super().decide(planet)
        if self.country and self.country.companies and planet.rng.random() < 0.25:
            firm = weighted_choice(planet.rng, self.country.companies, [max(0.01, f.growth_expectation) for f in self.country.companies])
            if firm:
                # Bewertungsphantasie: kann echtes Potenzial oder Blase sein.
                firm.receive_truth(TruthStack.mint({TruthLayer.POTENTIAL.value: 0.4, TruthLayer.COMPARATIVE.value: 0.2}))
                if planet.rng.random() < firm.fraud_risk + 0.04:
                    firm.incur_truth_debt(EpistemicDebtStack.debt({TruthLayer.EPISTEMIC.value: 0.35, TruthLayer.ETHICAL.value: 0.15}))


class UnitedNations(InstitutionalEntity):
    TYPE = "united_nations"

    def __init__(self, name: str = "United Planetary Nations") -> None:
        super().__init__(name, "un")
        self.peacekeeping_budget = 0.0
        self.sanction_pressure = 0.0
        self.receive_truth(TruthStack.mint({
            TruthLayer.LEGAL.value: 20,
            TruthLayer.SOCIAL.value: 18,
            TruthLayer.ETHICAL.value: 12,
            TruthLayer.SOVEREIGNTY.value: 10,
        }))

    def decide(self, planet: "Planet") -> None:
        # Beiträge einsammeln und Krisen abmildern.
        for c in self.members:
            contribution = c.gdp * 0.00005 * clamp(c.openness, 0.1, 1.2)
            c.pay_fiat(c.currency.code, contribution)
            self.receive_fiat(c.currency.code, contribution)
            self.peacekeeping_budget += contribution * planet.fx_to_reference(c.currency.code)
        unstable = [c for c in self.members if c.stability < 0.35 or c.average_company_truth_gap() > 0.45]
        if unstable and self.peacekeeping_budget > 1e8:
            target = planet.rng.choice(unstable)
            target.stability = clamp(target.stability + 0.025, 0.0, 1.0)
            target.receive_truth(TruthStack.mint({
                TruthLayer.SECURITY.value: 0.8,
                TruthLayer.LEGAL.value: 0.3,
                TruthLayer.SOCIAL.value: 0.2,
            }))
            self.peacekeeping_budget *= 0.96
            planet.record_event("UN_MEDIATION", f"{self.name} stabilisiert {target.name}", 0.35)


class DefenseOrganization(InstitutionalEntity):
    TYPE = "defense_organization"

    def __init__(self, name: str, doctrine: str, prefix: str = "deforg") -> None:
        super().__init__(name, prefix)
        self.doctrine = doctrine
        self.deterrence = 0.4
        self.interoperability = 0.4
        self.defense_budget_reference = 0.0
        self.receive_truth(TruthStack.mint({TruthLayer.SECURITY.value: 7, TruthLayer.SOCIAL.value: 2, TruthLayer.LEGAL.value: 2}))

    def add_member(self, country: Country) -> None:
        super().add_member(country)
        if self not in country.alliances:
            country.alliances.append(self)

    def decide(self, planet: "Planet") -> None:
        if not self.members:
            return
        spending = 0.0
        for c in self.members:
            contribution = c.gdp * c.defense_need * 0.00008
            c.pay_fiat(c.currency.code, contribution)
            spending += contribution * planet.fx_to_reference(c.currency.code)
            c.receive_truth(TruthStack.mint({TruthLayer.SECURITY.value: contribution / 8e9, TruthLayer.SOVEREIGNTY.value: contribution / 16e9}))
        self.defense_budget_reference += spending
        self.deterrence = clamp(self.deterrence + math.log10(max(1.0, spending)) * 0.0003 - 0.002, 0.05, 1.5)
        self.interoperability = clamp(self.interoperability + 0.004 * len(self.members) - 0.002, 0.05, 1.3)


class MutualDefensePact(DefenseOrganization):
    TYPE = "mutual_defense_pact"

    def __init__(self, name: str) -> None:
        super().__init__(name, "collective defense", "pact")


class MaritimeSecurityLeague(DefenseOrganization):
    TYPE = "maritime_security_league"

    def __init__(self, name: str) -> None:
        super().__init__(name, "trade lane security", "navy")


class CyberDefenseCompact(DefenseOrganization):
    TYPE = "cyber_defense_compact"

    def __init__(self, name: str) -> None:
        super().__init__(name, "cyber resilience", "cyberorg")

    def decide(self, planet: "Planet") -> None:
        super().decide(planet)
        for c in self.members:
            c.receive_truth(TruthStack.mint({TruthLayer.EPISTEMIC.value: 0.05, TruthLayer.INFRASTRUCTURE.value: 0.03}))


# =============================================================================
# 6. Produkt-, Claim- und Asset-Hierarchie
# =============================================================================


class EconomicObject(ABC):
    TYPE = "economic_object"

    def __init__(self, name: str, truth: Optional[TruthStack] = None) -> None:
        self.id = uid("obj")
        self.name = name
        self.truth = truth or TruthStack()

    def truth_score(self) -> float:
        return self.truth.score()


class Asset(EconomicObject):
    TYPE = "asset"

    def __init__(self, name: str, owner: Optional[SimNode], truth: Optional[TruthStack] = None) -> None:
        super().__init__(name, truth)
        self.owner = owner
        self.market_value_reference = max(0.0, self.truth_score()) * 1000.0


class RealAsset(Asset):
    TYPE = "real_asset"


class IntangibleAsset(Asset):
    TYPE = "intangible_asset"


class InfrastructureAsset(RealAsset):
    TYPE = "infrastructure_asset"


class HousingAsset(RealAsset):
    TYPE = "housing_asset"


class EnergyAsset(RealAsset):
    TYPE = "energy_asset"


class KnowledgeAsset(IntangibleAsset):
    TYPE = "knowledge_asset"


class BrandAsset(IntangibleAsset):
    TYPE = "brand_asset"


class Claim(EconomicObject):
    TYPE = "claim"

    def __init__(self, name: str, issuer: SimNode, holder: SimNode, truth: Optional[TruthStack] = None) -> None:
        super().__init__(name, truth)
        self.issuer = issuer
        self.holder = holder
        self.enforceability = 1.0


class TruthClaim(Claim):
    TYPE = "truth_claim"


class PropertyClaim(TruthClaim):
    TYPE = "property_claim"


class TicketClaim(TruthClaim):
    TYPE = "ticket_claim"


class LaborClaim(TruthClaim):
    TYPE = "labor_claim"


class InsuranceClaim(TruthClaim):
    TYPE = "insurance_claim"


class DebtClaim(TruthClaim):
    TYPE = "debt_claim"

    def __init__(self, name: str, issuer: SimNode, holder: SimNode, principal: float, rate: float, currency: str) -> None:
        super().__init__(name, issuer, holder, TruthStack.debt({TruthLayer.TEMPORAL.value: principal / 1e9, TruthLayer.LIQUIDITY.value: principal / 2e9}))
        self.principal = principal
        self.rate = rate
        self.currency = currency


class Product(EconomicObject):
    TYPE = "product"

    def __init__(self, name: str, sector: str, truth: TruthStack, base_price_reference: float) -> None:
        super().__init__(name, truth)
        self.sector = sector
        self.base_price_reference = base_price_reference


class Service(Product):
    TYPE = "service"


class Good(Product):
    TYPE = "good"


class FoodProduct(Good):
    TYPE = "food_product"


class HousingProduct(Good):
    TYPE = "housing_product"


class MobilityTicket(Service):
    TYPE = "mobility_ticket"


class HealthService(Service):
    TYPE = "health_service"


class EducationService(Service):
    TYPE = "education_service"


class DefenseService(Service):
    TYPE = "defense_service"


class AttentionProduct(Service):
    TYPE = "attention_product"


class LuxuryExperience(Service):
    TYPE = "luxury_experience"


# =============================================================================
# 7. Unternehmenshierarchie mit vielen Vererbungsstufen
# =============================================================================


class Company(EconomicEntity, ABC):
    TYPE = "company"
    SECTOR = "generic"
    PRODUCT_NAME = "generic product"
    PRODUCT_CLASS: Type[Product] = Product
    TRUTH_PROFILE: Dict[str, float] = {TruthLayer.EXISTENCE.value: 0.2, TruthLayer.CAUSAL.value: 0.2}
    BASE_PRODUCTIVITY = 1.0
    MARGIN = 0.10
    FRAUD_RISK = 0.03
    CAPITAL_INTENSITY = 1.0

    def __init__(self, name: str, country: Country, rng: random.Random) -> None:
        super().__init__(name, country, "firm")
        self.employees = rng.randint(40, 8000)
        self.productivity = self.BASE_PRODUCTIVITY * rng.uniform(0.55, 1.65)
        self.margin = clamp(self.MARGIN + rng.uniform(-0.05, 0.08), -0.18, 0.45)
        self.fraud_risk = clamp(self.FRAUD_RISK + rng.uniform(-0.015, 0.08), 0.0, 0.45)
        self.growth_expectation = rng.uniform(0.2, 1.8)
        self.inventory = 0.0
        self.capex_need = self.CAPITAL_INTENSITY * rng.uniform(0.4, 2.0)
        self.receive_fiat(country.currency.code, country.gdp * rng.uniform(0.00001, 0.0003))
        self.receive_truth(TruthStack.mint(self.TRUTH_PROFILE, scale=rng.uniform(1.0, 5.0)))

    def make_product(self, scale: float) -> Product:
        truth = TruthStack.mint(self.TRUTH_PROFILE, scale=scale)
        if self.PRODUCT_CLASS is Product:
            return Product(self.PRODUCT_NAME, self.SECTOR, truth, base_price_reference=truth.positive_score() * 1000.0)
        return self.PRODUCT_CLASS(self.PRODUCT_NAME, self.SECTOR, truth, base_price_reference=truth.positive_score() * 1000.0)  # type: ignore[call-arg]

    def market_demand(self, planet: "Planet") -> float:
        if not self.country:
            return 1.0
        return self.country.needs.get(self.SECTOR, 1.0)

    def produce(self, planet: "Planet") -> None:
        if not self.country:
            return
        demand = self.market_demand(planet)
        macro = clamp(self.country.stability + self.country.openness * 0.25 - self.country.inflation * 0.8, 0.20, 1.55)
        random_factor = planet.rng.lognormvariate(0.0, 0.18)
        gross = self.employees * self.productivity * demand * macro * random_factor * 1_000.0
        gross *= planet.sector_price_multiplier(self.SECTOR)
        costs = gross * (1.0 - self.margin)
        profit = gross - costs
        self.revenue_last_month = gross
        self.profit_last_month = profit
        self.receive_fiat(self.country.currency.code, gross * 0.35)
        self.pay_fiat(self.country.currency.code, costs * 0.15)
        self.inventory = clamp(self.inventory + gross / 1e6 - demand * 0.2, 0.0, 1e9)
        self.country.gdp += gross * 0.06
        # Produkt als Wahrheitsherstellung.
        produced_truth = TruthStack.mint(self.TRUTH_PROFILE, scale=max(0.01, gross / 50_000_000.0))
        self.receive_truth(produced_truth)
        self.country.receive_truth(produced_truth.scaled(0.10))
        # Wenn die Firma Illusion statt Realität verkauft.
        if planet.rng.random() < self.fraud_risk:
            fake_boost = TruthStack.mint({
                TruthLayer.PERCEPTION.value: 0.50,
                TruthLayer.SOCIAL.value: 0.25,
                TruthLayer.POTENTIAL.value: 0.35,
                TruthLayer.COMPARATIVE.value: 0.20,
            }, scale=max(0.1, gross / 80_000_000.0))
            hidden_debt = EpistemicDebtStack.debt({
                TruthLayer.EPISTEMIC.value: 0.45,
                TruthLayer.LEGAL.value: 0.18,
                TruthLayer.ETHICAL.value: 0.25,
                TruthLayer.CAUSAL.value: 0.15,
            }, scale=max(0.1, gross / 100_000_000.0))
            self.receive_truth(fake_boost)
            self.incur_truth_debt(hidden_debt)
            planet.record_event("TRUTH_DISTORTION", f"{self.name} verkauft Wahrnehmung über gedeckte Realität", min(1.0, self.fraud_risk))

    def decide(self, planet: "Planet") -> None:
        self.produce(planet)
        # Reputationsdynamik aus Wahrheitslücke.
        gap = self.wallet.truth.balance.truth_gap()
        self.reputation = clamp(self.reputation + 0.01 - gap * 0.04 + planet.rng.uniform(-0.01, 0.012), 0.05, 2.0)
        self.risk = clamp(self.risk + gap * 0.02 - self.reputation * 0.002, 0.01, 1.0)


class ProductiveCompany(Company):
    TYPE = "productive_company"


class CivilianCompany(ProductiveCompany):
    TYPE = "civilian_company"


class EssentialCompany(CivilianCompany):
    TYPE = "essential_company"


class ExperienceCompany(CivilianCompany):
    TYPE = "experience_company"


class KnowledgeCompany(CivilianCompany):
    TYPE = "knowledge_company"


class IndustrialCompany(ProductiveCompany):
    TYPE = "industrial_company"


class StrategicCompany(ProductiveCompany):
    TYPE = "strategic_company"


class FoodCompany(EssentialCompany):
    TYPE = "food_company"
    SECTOR = "food"
    PRODUCT_NAME = "Nahrung / food security bundle"
    PRODUCT_CLASS = FoodProduct
    TRUTH_PROFILE = {
        TruthLayer.EXISTENCE.value: 0.40,
        TruthLayer.CAUSAL.value: 0.35,
        TruthLayer.FOOD.value: 1.20,
        TruthLayer.HEALTH.value: 0.35,
        TruthLayer.TEMPORAL.value: 0.20,
        TruthLayer.ECOLOGICAL.value: 0.12,
    }
    BASE_PRODUCTIVITY = 1.05
    MARGIN = 0.08
    FRAUD_RISK = 0.025
    CAPITAL_INTENSITY = 0.8


class WaterCompany(EssentialCompany):
    TYPE = "water_company"
    SECTOR = "water"
    PRODUCT_NAME = "Wasserzugang / water access"
    TRUTH_PROFILE = {
        TruthLayer.EXISTENCE.value: 0.30,
        TruthLayer.HEALTH.value: 0.80,
        TruthLayer.INFRASTRUCTURE.value: 0.65,
        TruthLayer.RISK_REDUCTION.value: 0.40,
        TruthLayer.ECOLOGICAL.value: 0.25,
    }
    BASE_PRODUCTIVITY = 0.90
    MARGIN = 0.07
    FRAUD_RISK = 0.015


class HousingCompany(EssentialCompany):
    TYPE = "housing_company"
    SECTOR = "shelter"
    PRODUCT_NAME = "Wohnraum / legally recognized shelter"
    PRODUCT_CLASS = HousingProduct
    TRUTH_PROFILE = {
        TruthLayer.SHELTER.value: 1.15,
        TruthLayer.LEGAL.value: 0.60,
        TruthLayer.EXISTENCE.value: 0.55,
        TruthLayer.TEMPORAL.value: 0.40,
        TruthLayer.SOCIAL.value: 0.20,
        TruthLayer.INFRASTRUCTURE.value: 0.35,
    }
    BASE_PRODUCTIVITY = 0.85
    MARGIN = 0.16
    FRAUD_RISK = 0.04
    CAPITAL_INTENSITY = 1.8


class EnergyCompany(EssentialCompany):
    TYPE = "energy_company"
    SECTOR = "energy"
    PRODUCT_NAME = "Energie / usable power"
    TRUTH_PROFILE = {
        TruthLayer.ENERGY.value: 1.20,
        TruthLayer.CAUSAL.value: 0.50,
        TruthLayer.INFRASTRUCTURE.value: 0.45,
        TruthLayer.RISK_REDUCTION.value: 0.20,
        TruthLayer.ECOLOGICAL.value: -0.05,
    }
    BASE_PRODUCTIVITY = 1.15
    MARGIN = 0.14
    FRAUD_RISK = 0.035
    CAPITAL_INTENSITY = 2.2


class HealthCompany(EssentialCompany):
    TYPE = "health_company"
    SECTOR = "health"
    PRODUCT_NAME = "Gesundheitsleistung / treatment probability"
    PRODUCT_CLASS = HealthService
    TRUTH_PROFILE = {
        TruthLayer.HEALTH.value: 1.25,
        TruthLayer.EPISTEMIC.value: 0.60,
        TruthLayer.CAUSAL.value: 0.45,
        TruthLayer.RISK_REDUCTION.value: 0.45,
        TruthLayer.ETHICAL.value: 0.15,
    }
    BASE_PRODUCTIVITY = 0.95
    MARGIN = 0.12
    FRAUD_RISK = 0.035


class EducationCompany(KnowledgeCompany):
    TYPE = "education_company"
    SECTOR = "education"
    PRODUCT_NAME = "Bildung / future ability"
    PRODUCT_CLASS = EducationService
    TRUTH_PROFILE = {
        TruthLayer.EDUCATION.value: 1.10,
        TruthLayer.POTENTIAL.value: 0.80,
        TruthLayer.EPISTEMIC.value: 0.50,
        TruthLayer.ATTENTION.value: 0.30,
        TruthLayer.MEMORY.value: 0.25,
    }
    BASE_PRODUCTIVITY = 0.80
    MARGIN = 0.10
    FRAUD_RISK = 0.045


class SoftwareCompany(KnowledgeCompany):
    TYPE = "software_company"
    SECTOR = "software"
    PRODUCT_NAME = "Software / automated causality"
    TRUTH_PROFILE = {
        TruthLayer.CAUSAL.value: 0.85,
        TruthLayer.POTENTIAL.value: 0.90,
        TruthLayer.EPISTEMIC.value: 0.45,
        TruthLayer.INFRASTRUCTURE.value: 0.35,
        TruthLayer.ATTENTION.value: 0.20,
    }
    BASE_PRODUCTIVITY = 1.55
    MARGIN = 0.24
    FRAUD_RISK = 0.065


class ResearchCompany(KnowledgeCompany):
    TYPE = "research_company"
    SECTOR = "research"
    PRODUCT_NAME = "Forschung / epistemic frontier"
    TRUTH_PROFILE = {
        TruthLayer.EPISTEMIC.value: 1.20,
        TruthLayer.POTENTIAL.value: 1.10,
        TruthLayer.CAUSAL.value: 0.45,
        TruthLayer.EDUCATION.value: 0.40,
        TruthLayer.MEMORY.value: 0.30,
    }
    BASE_PRODUCTIVITY = 0.65
    MARGIN = 0.05
    FRAUD_RISK = 0.07


class MediaCompany(ExperienceCompany):
    TYPE = "media_company"
    SECTOR = "attention"
    PRODUCT_NAME = "Aufmerksamkeit / perception stream"
    PRODUCT_CLASS = AttentionProduct
    TRUTH_PROFILE = {
        TruthLayer.ATTENTION.value: 1.10,
        TruthLayer.PERCEPTION.value: 0.80,
        TruthLayer.SOCIAL.value: 0.45,
        TruthLayer.MEMORY.value: 0.35,
        TruthLayer.EPISTEMIC.value: 0.10,
    }
    BASE_PRODUCTIVITY = 1.25
    MARGIN = 0.20
    FRAUD_RISK = 0.12


class TourismCompany(ExperienceCompany):
    TYPE = "tourism_company"
    SECTOR = "tourism"
    PRODUCT_NAME = "Actionurlaub / intense memory package"
    PRODUCT_CLASS = LuxuryExperience
    TRUTH_PROFILE = {
        TruthLayer.MEMORY.value: 0.80,
        TruthLayer.PERCEPTION.value: 0.50,
        TruthLayer.TEMPORAL.value: 0.55,
        TruthLayer.ATTENTION.value: 0.50,
        TruthLayer.COMPARATIVE.value: 0.25,
    }
    BASE_PRODUCTIVITY = 0.95
    MARGIN = 0.18
    FRAUD_RISK = 0.06


class LuxuryCompany(ExperienceCompany):
    TYPE = "luxury_company"
    SECTOR = "luxury"
    PRODUCT_NAME = "Luxus / comparative status truth"
    PRODUCT_CLASS = LuxuryExperience
    TRUTH_PROFILE = {
        TruthLayer.PERCEPTION.value: 1.00,
        TruthLayer.COMPARATIVE.value: 1.10,
        TruthLayer.SOCIAL.value: 0.45,
        TruthLayer.MEMORY.value: 0.30,
        TruthLayer.EXISTENCE.value: 0.20,
    }
    BASE_PRODUCTIVITY = 0.75
    MARGIN = 0.32
    FRAUD_RISK = 0.09


class ManufacturingCompany(IndustrialCompany):
    TYPE = "manufacturing_company"
    SECTOR = "manufacturing"
    PRODUCT_NAME = "Produkt / embodied function"
    TRUTH_PROFILE = {
        TruthLayer.EXISTENCE.value: 0.70,
        TruthLayer.CAUSAL.value: 0.70,
        TruthLayer.LOGISTICS.value: 0.35,
        TruthLayer.INFRASTRUCTURE.value: 0.20,
        TruthLayer.COMPARATIVE.value: 0.12,
    }
    BASE_PRODUCTIVITY = 1.20
    MARGIN = 0.13
    FRAUD_RISK = 0.04
    CAPITAL_INTENSITY = 1.5


class ConstructionCompany(IndustrialCompany):
    TYPE = "construction_company"
    SECTOR = "infrastructure"
    PRODUCT_NAME = "Bauleistung / constructed reality"
    TRUTH_PROFILE = {
        TruthLayer.INFRASTRUCTURE.value: 1.10,
        TruthLayer.SHELTER.value: 0.50,
        TruthLayer.EXISTENCE.value: 0.60,
        TruthLayer.CAUSAL.value: 0.35,
        TruthLayer.LEGAL.value: 0.25,
    }
    BASE_PRODUCTIVITY = 0.95
    MARGIN = 0.12
    FRAUD_RISK = 0.055
    CAPITAL_INTENSITY = 1.7


class LogisticsCompany(IndustrialCompany):
    TYPE = "logistics_company"
    SECTOR = "mobility"
    PRODUCT_NAME = "Ankommen / logistics arrival probability"
    PRODUCT_CLASS = MobilityTicket
    TRUTH_PROFILE = {
        TruthLayer.LOGISTICS.value: 1.05,
        TruthLayer.TEMPORAL.value: 0.65,
        TruthLayer.CAUSAL.value: 0.45,
        TruthLayer.RISK_REDUCTION.value: 0.25,
        TruthLayer.ENERGY.value: 0.20,
    }
    BASE_PRODUCTIVITY = 1.10
    MARGIN = 0.11
    FRAUD_RISK = 0.035
    CAPITAL_INTENSITY = 1.2


class MiningCompany(IndustrialCompany):
    TYPE = "mining_company"
    SECTOR = "materials"
    PRODUCT_NAME = "Rohstoff / extracted existence"
    TRUTH_PROFILE = {
        TruthLayer.EXISTENCE.value: 0.90,
        TruthLayer.CAUSAL.value: 0.35,
        TruthLayer.ENERGY.value: 0.20,
        TruthLayer.ECOLOGICAL.value: -0.30,
        TruthLayer.LOGISTICS.value: 0.20,
    }
    BASE_PRODUCTIVITY = 1.05
    MARGIN = 0.17
    FRAUD_RISK = 0.05
    CAPITAL_INTENSITY = 2.0


class SpaceCompany(IndustrialCompany):
    TYPE = "space_company"
    SECTOR = "space"
    PRODUCT_NAME = "Orbitale Option / frontier potential"
    TRUTH_PROFILE = {
        TruthLayer.POTENTIAL.value: 1.20,
        TruthLayer.EPISTEMIC.value: 0.65,
        TruthLayer.COMPARATIVE.value: 0.45,
        TruthLayer.INFRASTRUCTURE.value: 0.30,
        TruthLayer.SOVEREIGNTY.value: 0.20,
    }
    BASE_PRODUCTIVITY = 0.60
    MARGIN = 0.18
    FRAUD_RISK = 0.10
    CAPITAL_INTENSITY = 3.0


class DefenseCompany(StrategicCompany):
    TYPE = "defense_company"
    SECTOR = "security"
    PRODUCT_NAME = "Verteidigung / deterrence capability"
    PRODUCT_CLASS = DefenseService
    TRUTH_PROFILE = {
        TruthLayer.SECURITY.value: 1.30,
        TruthLayer.SOVEREIGNTY.value: 0.70,
        TruthLayer.RISK_REDUCTION.value: 0.45,
        TruthLayer.CAUSAL.value: 0.45,
        TruthLayer.LEGAL.value: 0.10,
    }
    BASE_PRODUCTIVITY = 1.00
    MARGIN = 0.18
    FRAUD_RISK = 0.06
    CAPITAL_INTENSITY = 2.3


class CyberSecurityCompany(StrategicCompany):
    TYPE = "cyber_security_company"
    SECTOR = "cybersecurity"
    PRODUCT_NAME = "Cyberabwehr / epistemic infrastructure protection"
    TRUTH_PROFILE = {
        TruthLayer.SECURITY.value: 0.75,
        TruthLayer.EPISTEMIC.value: 0.65,
        TruthLayer.INFRASTRUCTURE.value: 0.55,
        TruthLayer.RISK_REDUCTION.value: 0.45,
        TruthLayer.CAUSAL.value: 0.30,
    }
    BASE_PRODUCTIVITY = 1.35
    MARGIN = 0.22
    FRAUD_RISK = 0.055


class InsuranceCompany(StrategicCompany):
    TYPE = "insurance_company"
    SECTOR = "insurance"
    PRODUCT_NAME = "Versicherung / risk reduction claim"
    PRODUCT_CLASS = HealthService
    TRUTH_PROFILE = {
        TruthLayer.RISK_REDUCTION.value: 1.10,
        TruthLayer.LEGAL.value: 0.45,
        TruthLayer.LIQUIDITY.value: 0.35,
        TruthLayer.TEMPORAL.value: 0.30,
        TruthLayer.SOCIAL.value: 0.25,
    }
    BASE_PRODUCTIVITY = 0.90
    MARGIN = 0.16
    FRAUD_RISK = 0.04


class LegalCompany(StrategicCompany):
    TYPE = "legal_company"
    SECTOR = "legal"
    PRODUCT_NAME = "Rechtliche Position / enforceable truth"
    TRUTH_PROFILE = {
        TruthLayer.LEGAL.value: 1.15,
        TruthLayer.EPISTEMIC.value: 0.45,
        TruthLayer.SOCIAL.value: 0.25,
        TruthLayer.RISK_REDUCTION.value: 0.25,
        TruthLayer.SOVEREIGNTY.value: 0.10,
    }
    BASE_PRODUCTIVITY = 0.75
    MARGIN = 0.22
    FRAUD_RISK = 0.035


COMPANY_CLASSES: List[Type[Company]] = [
    FoodCompany, WaterCompany, HousingCompany, EnergyCompany, HealthCompany,
    EducationCompany, SoftwareCompany, ResearchCompany, MediaCompany,
    TourismCompany, LuxuryCompany, ManufacturingCompany, ConstructionCompany,
    LogisticsCompany, MiningCompany, SpaceCompany, DefenseCompany,
    CyberSecurityCompany, InsuranceCompany, LegalCompany,
]


# =============================================================================
# 8. Transaktionshierarchie
# =============================================================================


class Transaction(ABC):
    TYPE = "transaction"

    def __init__(self, sender: SimNode, receiver: SimNode, description: str = "") -> None:
        self.id = uid("tx")
        self.sender = sender
        self.receiver = receiver
        self.description = description
        self.executed = False
        self.failed = False

    @abstractmethod
    def execute(self, planet: "Planet") -> None:
        raise NotImplementedError

    def record(self, planet: "Planet", status: str) -> None:
        planet.transactions.append({
            "month": planet.month,
            "id": self.id,
            "type": self.TYPE,
            "sender": self.sender.name,
            "receiver": self.receiver.name,
            "description": self.description,
            "status": status,
        })


class FiatTransferTransaction(Transaction):
    TYPE = "fiat_transfer"

    def __init__(self, sender: SimNode, receiver: SimNode, currency: str, amount: float, description: str = "") -> None:
        super().__init__(sender, receiver, description)
        self.currency = currency
        self.amount = amount

    def execute(self, planet: "Planet") -> None:
        self.sender.pay_fiat(self.currency, self.amount)
        self.receiver.receive_fiat(self.currency, self.amount)
        self.executed = True
        self.record(planet, "executed")


class TruthTransferTransaction(Transaction):
    TYPE = "truth_transfer"

    def __init__(self, sender: SimNode, receiver: SimNode, stack: TruthStack, description: str = "") -> None:
        super().__init__(sender, receiver, description)
        self.stack = stack

    def execute(self, planet: "Planet") -> None:
        self.sender.pay_truth(self.stack)
        self.receiver.receive_truth(self.stack.copy())
        self.executed = True
        self.record(planet, "executed")


class PurchaseTransaction(FiatTransferTransaction):
    TYPE = "purchase"

    def __init__(self, buyer: SimNode, seller: Company, currency: str, amount: float, product: Product) -> None:
        super().__init__(buyer, seller, currency, amount, f"purchase {product.name}")
        self.product = product

    def execute(self, planet: "Planet") -> None:
        super().execute(planet)
        self.sender.receive_truth(self.product.truth.scaled(0.85))
        self.receiver.receive_truth(self.product.truth.scaled(0.10))
        self.record(planet, "reality_changed")


class LoanOriginationTransaction(FiatTransferTransaction):
    TYPE = "loan_origination"

    def __init__(self, bank: CommercialBank, borrower: Company, currency: str, amount: float, rate: float, maturity_months: int) -> None:
        super().__init__(bank, borrower, currency, amount, f"loan {amount:.0f} {currency} at {rate:.3f}")
        self.rate = rate
        self.maturity_months = maturity_months

    def execute(self, planet: "Planet") -> None:
        super().execute(planet)
        self.sender.assets += self.amount
        self.receiver.receive_truth(TruthStack.mint({
            TruthLayer.POTENTIAL.value: self.amount / 500_000_000.0,
            TruthLayer.LIQUIDITY.value: self.amount / 800_000_000.0,
        }))
        self.receiver.incur_truth_debt(FiatDebtStack.debt({
            TruthLayer.TEMPORAL.value: self.amount / 900_000_000.0,
            TruthLayer.LIQUIDITY.value: self.amount / 1_100_000_000.0,
            TruthLayer.LEGAL.value: self.amount / 1_300_000_000.0,
        }))


class TaxCollectionTransaction(FiatTransferTransaction):
    TYPE = "tax_collection"


class SubsidyTransaction(FiatTransferTransaction):
    TYPE = "subsidy"

    def execute(self, planet: "Planet") -> None:
        super().execute(planet)
        self.receiver.receive_truth(TruthStack.mint({TruthLayer.POTENTIAL.value: self.amount / 1e9}))


class SanctionTransaction(Transaction):
    TYPE = "sanction"

    def __init__(self, sender: SimNode, receiver: SimNode, intensity: float) -> None:
        super().__init__(sender, receiver, f"sanction intensity {intensity:.2f}")
        self.intensity = intensity

    def execute(self, planet: "Planet") -> None:
        self.receiver.reputation = clamp(self.receiver.reputation - self.intensity * 0.15, 0.01, 2.0)
        self.receiver.incur_truth_debt(EpistemicDebtStack.debt({
            TruthLayer.LEGAL.value: self.intensity,
            TruthLayer.SOCIAL.value: self.intensity * 0.6,
            TruthLayer.LIQUIDITY.value: self.intensity * 0.4,
        }))
        self.executed = True
        self.record(planet, "executed")


class AuditTransaction(Transaction):
    TYPE = "audit"

    def __init__(self, auditor: SimNode, target: SimNode, intensity: float) -> None:
        super().__init__(auditor, target, f"truth audit {intensity:.2f}")
        self.intensity = intensity

    def execute(self, planet: "Planet") -> None:
        gap = self.receiver.wallet.truth.balance.truth_gap()
        if gap > 0.22 and planet.rng.random() < self.intensity + gap:
            penalty = gap * self.intensity
            self.receiver.reputation = clamp(self.receiver.reputation - penalty * 0.4, 0.01, 2.0)
            self.receiver.incur_truth_debt(EpistemicDebtStack.debt({
                TruthLayer.EPISTEMIC.value: penalty,
                TruthLayer.LEGAL.value: penalty * 0.5,
                TruthLayer.SOCIAL.value: penalty * 0.5,
            }))
            planet.record_event("AUDIT_REVEAL", f"Audit deckt Wahrheitslücke bei {self.receiver.name} auf", penalty)
        else:
            self.receiver.receive_truth(TruthStack.mint({TruthLayer.EPISTEMIC.value: self.intensity * 0.05}))
        self.executed = True
        self.record(planet, "executed")


class TruthLedger:
    def __init__(self) -> None:
        self.executed_count = 0
        self.failed_count = 0

    def execute(self, tx: Transaction, planet: "Planet") -> None:
        try:
            tx.execute(planet)
            self.executed_count += 1
        except Exception as exc:  # robust simulation instead of crash
            self.failed_count += 1
            planet.record_event("TX_FAIL", f"{tx.TYPE} fehlgeschlagen: {exc}", 0.1)


# =============================================================================
# 9. Markt-Hierarchie
# =============================================================================


class Market(ABC):
    TYPE = "market"

    def __init__(self, name: str) -> None:
        self.name = name
        self.volume_reference = 0.0
        self.price_index = 1.0

    @abstractmethod
    def clear(self, planet: "Planet") -> None:
        raise NotImplementedError


class GoodsMarket(Market):
    TYPE = "goods_market"

    def clear(self, planet: "Planet") -> None:
        if not planet.companies or not planet.countries:
            return
        trades = max(1, len(planet.countries) // 2)
        for _ in range(trades):
            buyer = weighted_choice(planet.rng, planet.countries, [max(0.1, c.gdp) for c in planet.countries])
            seller = weighted_choice(planet.rng, planet.companies, [max(0.1, f.revenue_last_month + 1.0) for f in planet.companies])
            if not buyer or not seller or not seller.country:
                continue
            product = seller.make_product(scale=planet.rng.uniform(0.02, 0.35))
            amount_ref = max(10_000.0, product.base_price_reference * planet.rng.uniform(10.0, 500.0))
            amount_local = amount_ref / planet.fx_to_reference(buyer.currency.code)
            tx = PurchaseTransaction(buyer, seller, buyer.currency.code, amount_local, product)
            planet.ledger.execute(tx, planet)
            self.volume_reference += amount_ref


class CreditMarket(Market):
    TYPE = "credit_market"

    def clear(self, planet: "Planet") -> None:
        self.price_index = mean_or([c.central_bank.policy_rate for c in planet.countries if c.central_bank], 0.04)


class LaborMarket(Market):
    TYPE = "labor_market"

    def clear(self, planet: "Planet") -> None:
        for c in planet.countries:
            pressure = mean_or([f.productivity for f in c.companies], 1.0)
            c.unemployment = clamp(c.unemployment - pressure * 0.0006 + planet.rng.uniform(-0.002, 0.003), 0.01, 0.65)


class TruthMarket(Market):
    TYPE = "truth_market"

    def clear(self, planet: "Planet") -> None:
        # WK-Preis steigt bei hoher Nachfrage nach Risikoreduktion und Legalität,
        # fällt bei vielen entdeckten Wahrheitslücken.
        total_pos = sum(a.wallet.truth.balance.positive_score() for a in planet.all_nodes())
        total_neg = abs(sum(a.wallet.truth.balance.negative_score() for a in planet.all_nodes()))
        gap = safe_div(total_neg, total_pos + total_neg + 1e-9)
        planet.truth_price_reference *= clamp(1.0 + 0.004 - gap * 0.018 + planet.rng.uniform(-0.006, 0.008), 0.96, 1.05)
        self.price_index = planet.truth_price_reference


class DefenseMarket(Market):
    TYPE = "defense_market"

    def clear(self, planet: "Planet") -> None:
        if planet.rng.random() < 0.18:
            needy = [c for c in planet.countries if c.defense_need > 0.4]
            firms = [f for f in planet.companies if isinstance(f, (DefenseCompany, CyberSecurityCompany))]
            if needy and firms:
                buyer = planet.rng.choice(needy)
                seller = planet.rng.choice(firms)
                product = seller.make_product(scale=planet.rng.uniform(0.1, 0.8))
                amount = buyer.gdp * planet.rng.uniform(0.00005, 0.0006)
                tx = PurchaseTransaction(buyer, seller, buyer.currency.code, amount, product)
                planet.ledger.execute(tx, planet)


# =============================================================================
# 10. Ereignishierarchie
# =============================================================================


class WorldEvent(ABC):
    TYPE = "world_event"
    BASE_PROBABILITY = 0.01

    def __init__(self, severity: float) -> None:
        self.id = uid("event")
        self.severity = clamp(severity, 0.0, 1.0)

    @abstractmethod
    def apply(self, planet: "Planet") -> None:
        raise NotImplementedError

    def log(self, planet: "Planet", text: str) -> None:
        planet.record_event(self.TYPE, text, self.severity)


class NaturalEvent(WorldEvent):
    TYPE = "natural_event"


class ClimateShock(NaturalEvent):
    TYPE = "climate_shock"
    BASE_PROBABILITY = 0.018

    def apply(self, planet: "Planet") -> None:
        c = planet.rng.choice(planet.countries)
        c.ecological_pressure = clamp(c.ecological_pressure + self.severity * 0.15, 0, 1.5)
        c.gdp *= 1.0 - self.severity * 0.025
        c.incur_truth_debt(EpistemicDebtStack.debt({
            TruthLayer.ECOLOGICAL.value: self.severity,
            TruthLayer.FOOD.value: self.severity * 0.5,
            TruthLayer.HEALTH.value: self.severity * 0.3,
        }))
        self.log(planet, f"Klimaschock trifft {c.name}")


class PandemicEvent(NaturalEvent):
    TYPE = "pandemic"
    BASE_PROBABILITY = 0.007

    def apply(self, planet: "Planet") -> None:
        affected = planet.rng.sample(planet.countries, k=max(1, len(planet.countries)//5))
        for c in affected:
            c.stability = clamp(c.stability - self.severity * 0.05, 0, 1)
            c.gdp *= 1.0 - self.severity * 0.018
            c.incur_truth_debt(EpistemicDebtStack.debt({TruthLayer.HEALTH.value: self.severity, TruthLayer.RISK_REDUCTION.value: self.severity * 0.4}))
        self.log(planet, f"Pandemische Welle betrifft {len(affected)} Länder")


class EarthquakeEvent(NaturalEvent):
    TYPE = "earthquake"
    BASE_PROBABILITY = 0.010

    def apply(self, planet: "Planet") -> None:
        c = planet.rng.choice(planet.countries)
        c.gdp *= 1.0 - self.severity * 0.015
        c.incur_truth_debt(SecurityDebtStack.debt({TruthLayer.INFRASTRUCTURE.value: self.severity, TruthLayer.SHELTER.value: self.severity * 0.7}))
        self.log(planet, f"Erdbeben beschädigt Infrastruktur in {c.name}")


class PoliticalEvent(WorldEvent):
    TYPE = "political_event"


class WarEvent(PoliticalEvent):
    TYPE = "war"
    BASE_PROBABILITY = 0.006

    def apply(self, planet: "Planet") -> None:
        a, b = planet.rng.sample(planet.countries, 2)
        a.stability = clamp(a.stability - self.severity * 0.08, 0, 1)
        b.stability = clamp(b.stability - self.severity * 0.08, 0, 1)
        a.defense_need = clamp(a.defense_need + self.severity * 0.18, 0, 1.5)
        b.defense_need = clamp(b.defense_need + self.severity * 0.18, 0, 1.5)
        debt = SecurityDebtStack.debt({TruthLayer.SECURITY.value: self.severity, TruthLayer.SOVEREIGNTY.value: self.severity * 0.6, TruthLayer.ETHICAL.value: self.severity * 0.4})
        a.incur_truth_debt(debt)
        b.incur_truth_debt(debt.copy())
        self.log(planet, f"Bewaffneter Konflikt zwischen {a.name} und {b.name}")


class SanctionEvent(PoliticalEvent):
    TYPE = "sanction_event"
    BASE_PROBABILITY = 0.008

    def apply(self, planet: "Planet") -> None:
        target = max(planet.countries, key=lambda c: c.corruption + c.average_company_truth_gap())
        sender = planet.un if planet.un else planet.rng.choice(planet.countries)
        tx = SanctionTransaction(sender, target, self.severity)
        planet.ledger.execute(tx, planet)
        self.log(planet, f"Sanktionen gegen {target.name}")


class FinancialEvent(WorldEvent):
    TYPE = "financial_event"


class TruthBubbleBurstEvent(FinancialEvent):
    TYPE = "truth_bubble_burst"
    BASE_PROBABILITY = 0.012

    def apply(self, planet: "Planet") -> None:
        candidates = sorted(planet.companies, key=lambda f: f.wallet.truth.balance.truth_gap(), reverse=True)[:max(3, len(planet.companies)//20)]
        if not candidates:
            return
        firm = planet.rng.choice(candidates)
        gap = firm.wallet.truth.balance.truth_gap()
        loss = self.severity * (0.5 + gap)
        firm.reputation = clamp(firm.reputation - loss, 0.01, 2.0)
        firm.incur_truth_debt(EpistemicDebtStack.debt({
            TruthLayer.EPISTEMIC.value: loss,
            TruthLayer.LEGAL.value: loss * 0.5,
            TruthLayer.SOCIAL.value: loss * 0.7,
            TruthLayer.PERCEPTION.value: loss * 0.4,
        }))
        if firm.country:
            firm.country.gdp *= 1.0 - min(0.03, loss * 0.005)
        self.log(planet, f"Wahrheitsblase platzt bei {firm.name}")


class BankRunEvent(FinancialEvent):
    TYPE = "bank_run"
    BASE_PROBABILITY = 0.006

    def apply(self, planet: "Planet") -> None:
        bank = weighted_choice(planet.rng, planet.banks, [max(0.01, b.nonperforming_ratio) for b in planet.banks])
        if not bank:
            return
        bank.nonperforming_ratio = clamp(bank.nonperforming_ratio + self.severity * 0.18, 0, 1)
        bank.incur_truth_debt(FiatDebtStack.debt({TruthLayer.LIQUIDITY.value: self.severity, TruthLayer.SOCIAL.value: self.severity * 0.7}))
        if bank.country:
            bank.country.stability = clamp(bank.country.stability - self.severity * 0.03, 0, 1)
        self.log(planet, f"Bank Run bei {bank.name}")


class TechnologicalEvent(WorldEvent):
    TYPE = "technological_event"


class TechBreakthroughEvent(TechnologicalEvent):
    TYPE = "tech_breakthrough"
    BASE_PROBABILITY = 0.018

    def apply(self, planet: "Planet") -> None:
        firms = [f for f in planet.companies if isinstance(f, (ResearchCompany, SoftwareCompany, SpaceCompany, CyberSecurityCompany))]
        if not firms:
            return
        firm = planet.rng.choice(firms)
        boost = self.severity * planet.rng.uniform(0.8, 1.6)
        firm.productivity *= 1.0 + boost * 0.08
        firm.receive_truth(TruthStack.mint({TruthLayer.EPISTEMIC.value: boost, TruthLayer.POTENTIAL.value: boost, TruthLayer.CAUSAL.value: boost * 0.6}))
        if firm.country:
            firm.country.research_level = clamp(firm.country.research_level + boost * 0.03, 0, 2)
        self.log(planet, f"Technologischer Durchbruch bei {firm.name}")


class SecurityEvent(WorldEvent):
    TYPE = "security_event"


class CyberAttackEvent(SecurityEvent):
    TYPE = "cyber_attack"
    BASE_PROBABILITY = 0.014

    def apply(self, planet: "Planet") -> None:
        target = planet.rng.choice(planet.countries)
        cyber_defense = sum(1 for f in target.companies if isinstance(f, CyberSecurityCompany))
        mitigated = clamp(cyber_defense / 8.0, 0.0, 0.8)
        impact = self.severity * (1.0 - mitigated)
        target.gdp *= 1.0 - impact * 0.012
        target.incur_truth_debt(SecurityDebtStack.debt({TruthLayer.INFRASTRUCTURE.value: impact, TruthLayer.EPISTEMIC.value: impact * 0.6, TruthLayer.SECURITY.value: impact}))
        self.log(planet, f"Cyberangriff gegen {target.name}, abgefedert: {mitigated:.2f}")


EVENT_CLASSES: List[Type[WorldEvent]] = [
    ClimateShock, PandemicEvent, EarthquakeEvent, WarEvent, SanctionEvent,
    TruthBubbleBurstEvent, BankRunEvent, TechBreakthroughEvent, CyberAttackEvent,
]


# =============================================================================
# 11. UTF-8 Visualisierungshierarchie
# =============================================================================


class Renderer(ABC):
    @abstractmethod
    def render(self, planet: "Planet") -> str:
        raise NotImplementedError


class UTF8Renderer(Renderer):
    WIDTH = 108
    BLOCKS = " ▁▂▃▄▅▆▇█"

    def line(self, char: str = "─") -> str:
        return char * self.WIDTH

    def box(self, title: str, body: str) -> str:
        lines = body.splitlines() or [""]
        top = "┌" + "─" * (self.WIDTH - 2) + "┐"
        mid = "├" + "─" * (self.WIDTH - 2) + "┤"
        bottom = "└" + "─" * (self.WIDTH - 2) + "┘"
        t = f" {title} "
        title_line = "│" + t[: self.WIDTH - 2].center(self.WIDTH - 2) + "│"
        out = [top, title_line, mid]
        for line in lines:
            while len(line) > self.WIDTH - 4:
                out.append("│ " + line[: self.WIDTH - 4].ljust(self.WIDTH - 4) + " │")
                line = line[self.WIDTH - 4:]
            out.append("│ " + line.ljust(self.WIDTH - 4) + " │")
        out.append(bottom)
        return "\n".join(out)

    def bar(self, value: float, max_value: float, width: int = 36, label: str = "") -> str:
        ratio = clamp(safe_div(value, max_value, 0.0), 0.0, 1.0)
        full = int(round(ratio * width))
        return f"{label:<22} │{'█' * full}{'░' * (width - full)}│ {value:,.2f}"

    def signed_bar(self, value: float, max_abs: float, width: int = 44, label: str = "") -> str:
        half = width // 2
        ratio = clamp(safe_div(abs(value), max_abs, 0.0), 0.0, 1.0)
        n = int(round(ratio * half))
        if value >= 0:
            bar = " " * half + "│" + "█" * n + "░" * (half - n)
        else:
            bar = "░" * (half - n) + "█" * n + "│" + " " * half
        return f"{label:<22} {bar} {value:,.2f}"

    def sparkline(self, values: Sequence[float], width: int = 64) -> str:
        if not values:
            return ""
        if len(values) > width:
            step = len(values) / width
            compressed = []
            for i in range(width):
                a = int(i * step)
                b = max(a + 1, int((i + 1) * step))
                compressed.append(mean_or(values[a:b], values[a]))
            values = compressed
        lo, hi = min(values), max(values)
        if abs(hi - lo) < 1e-12:
            return self.BLOCKS[4] * len(values)
        chars = []
        for v in values:
            idx = int(clamp((v - lo) / (hi - lo), 0, 0.999) * (len(self.BLOCKS) - 1)) + 1
            idx = min(idx, len(self.BLOCKS) - 1)
            chars.append(self.BLOCKS[idx])
        return "".join(chars)

    def heat_char(self, value: float, lo: float, hi: float) -> str:
        blocks = " ·░▒▓█"
        idx = int(clamp(safe_div(value - lo, hi - lo, 0.0), 0, 0.999) * len(blocks))
        return blocks[min(idx, len(blocks)-1)]

    def render(self, planet: "Planet") -> str:
        sections = [
            self.render_title(planet),
            self.render_oop_hierarchy(),
            self.render_class_counter(),
            self.render_macro_dashboard(planet),
            self.render_truth_stack(planet),
            self.render_negative_truth(planet),
            self.render_country_truth_matrix(planet),
            self.render_country_league(planet),
            self.render_debt_pyramid(planet),
            self.render_company_league(planet),
            self.render_sector_bars(planet),
            self.render_transaction_mix(planet),
            self.render_bank_stress(planet),
            self.render_fx_matrix(planet),
            self.render_currency_map(planet),
            self.render_event_timeline(planet),
            self.render_event_histogram(planet),
            self.render_flow_diagram(),
            self.render_truth_lifecycle_diagram(),
            self.render_institutional_network(planet),
            self.render_security_diagram(planet),
            self.render_potential_debt_scatter(planet),
            self.render_market_sparklines(planet),
        ]
        return "\n\n".join(sections)

    def render_title(self, planet: "Planet") -> str:
        body = f"""
Planet: {planet.name}
Simulationsmonat: {planet.month}
Länder: {len(planet.countries)} | Firmen: {len(planet.companies)} | Banken: {len(planet.banks)} | Verteidigungsorganisationen: {len(planet.defense_orgs)}
Globale Wahrheitspreis-Referenz: {planet.truth_price_reference:,.4f} REF/WK
Transaktionen: {len(planet.transactions)} | Ereignisse: {len(planet.events)}
""".strip()
        return self.box("PLANETARE WK-SIMULATION — UTF-8 ART APPENDIX", body)

    def render_oop_hierarchy(self) -> str:
        diagram = r"""
SimNode
├─ Agent
│  ├─ LegalEntity
│  │  ├─ InstitutionalEntity
│  │  │  ├─ SovereignEntity
│  │  │  │  └─ Country
│  │  │  ├─ FinancialInstitution
│  │  │  │  ├─ CentralBank
│  │  │  │  └─ CommercialBank ─┬─ DevelopmentBank
│  │  │  │                    └─ InvestmentBank
│  │  │  ├─ UnitedNations
│  │  │  └─ DefenseOrganization ─┬─ MutualDefensePact
│  │  │                          ├─ MaritimeSecurityLeague
│  │  │                          └─ CyberDefenseCompact
│  │  └─ EconomicEntity
│  │     ├─ Household
│  │     └─ Company
│  │        └─ ProductiveCompany
│  │           ├─ CivilianCompany
│  │           │  ├─ EssentialCompany ─┬─ FoodCompany ─ WaterCompany ─ HousingCompany
│  │           │  │                    └─ EnergyCompany ─ HealthCompany
│  │           │  ├─ KnowledgeCompany ─┬─ EducationCompany ─ SoftwareCompany
│  │           │  │                    └─ ResearchCompany
│  │           │  └─ ExperienceCompany ─┬─ MediaCompany ─ TourismCompany
│  │           │                        └─ LuxuryCompany
│  │           ├─ IndustrialCompany ─┬─ ManufacturingCompany ─ ConstructionCompany
│  │           │                     ├─ LogisticsCompany ─ MiningCompany
│  │           │                     └─ SpaceCompany
│  │           └─ StrategicCompany ─┬─ DefenseCompany ─ CyberSecurityCompany
│  │                                └─ InsuranceCompany ─ LegalCompany
│
EconomicObject
├─ Asset ─┬─ RealAsset ─ InfrastructureAsset / HousingAsset / EnergyAsset
│         └─ IntangibleAsset ─ KnowledgeAsset / BrandAsset
├─ Claim ─ TruthClaim ─ PropertyClaim / TicketClaim / LaborClaim / InsuranceClaim / DebtClaim
└─ Product ─┬─ Good ─ FoodProduct / HousingProduct
            └─ Service ─ MobilityTicket / HealthService / EducationService / DefenseService / AttentionProduct / LuxuryExperience
""".strip()
        return self.box("KLASSENVERERBUNG / CLASS INHERITANCE MAP", diagram)

    def render_class_counter(self) -> str:
        company_leaves = [cls.__name__ for cls in COMPANY_CLASSES]
        event_leaves = [cls.__name__ for cls in EVENT_CLASSES]
        market_leaves = ["GoodsMarket", "CreditMarket", "LaborMarket", "TruthMarket", "DefenseMarket"]
        transaction_leaves = [
            "FiatTransferTransaction", "TruthTransferTransaction", "PurchaseTransaction",
            "LoanOriginationTransaction", "TaxCollectionTransaction", "SubsidyTransaction",
            "SanctionTransaction", "AuditTransaction",
        ]
        lines = [
            self.bar(len(company_leaves), max(len(company_leaves), 1), width=38, label="Firmenklassen"),
            self.bar(len(event_leaves), max(len(company_leaves), 1), width=38, label="Ereignisklassen"),
            self.bar(len(market_leaves), max(len(company_leaves), 1), width=38, label="Marktklassen"),
            self.bar(len(transaction_leaves), max(len(company_leaves), 1), width=38, label="Transaktionsklassen"),
            "",
            "Firmenblätter:",
            ", ".join(company_leaves),
            "",
            "Ereignisblätter:",
            ", ".join(event_leaves),
        ]
        return self.box("KLASSENZÄHLER / OOP-SURFACE", "\n".join(lines))

    def render_macro_dashboard(self, planet: "Planet") -> str:
        total_gdp = sum(c.gdp for c in planet.countries)
        avg_inflation = mean_or([c.inflation for c in planet.countries])
        avg_stability = mean_or([c.stability for c in planet.countries])
        avg_unemp = mean_or([c.unemployment for c in planet.countries])
        max_gdp = max([c.gdp for c in planet.countries] + [1.0])
        lines = [
            self.bar(total_gdp, max(total_gdp, 1), label="Welt-BIP REF"),
            self.bar(avg_stability, 1.0, label="Ø Stabilität"),
            self.bar(avg_inflation, 0.35, label="Ø Inflation"),
            self.bar(avg_unemp, 0.65, label="Ø Arbeitslosigkeit"),
            "",
            "Top-BIP-Länder:",
        ]
        for c in sorted(planet.countries, key=lambda x: x.gdp, reverse=True)[:8]:
            lines.append(self.bar(c.gdp, max_gdp, width=30, label=c.name[:20]))
        return self.box("MAKRO-DASHBOARD", "\n".join(lines))

    def render_truth_stack(self, planet: "Planet") -> str:
        aggregate = TruthStack()
        for node in planet.all_nodes():
            aggregate.add(node.wallet.truth.balance)
        max_pos = max([abs(v) for v in aggregate.values.values()] + [1.0])
        lines = ["Aggregierter planetarer WK-Vektor: positive Wahrheit rechts, negative Wahrheit links", ""]
        for k, v in sorted(aggregate.values.items(), key=lambda kv: abs(kv[1]), reverse=True):
            lines.append(self.signed_bar(v, max_pos, label=k[:21]))
        return self.box("GESTAPELTE WAHRHEITSWERT-WÄHRUNG WK", "\n".join(lines))

    def render_negative_truth(self, planet: "Planet") -> str:
        debt_layers = {k: 0.0 for k in ALL_TRUTH_LAYERS}
        for node in planet.all_nodes():
            for k, v in node.wallet.truth.balance.values.items():
                if v < 0:
                    debt_layers[k] += abs(v)
        max_debt = max(debt_layers.values() or [1.0])
        lines = ["Negative WK = Schulden, Lügenlasten, Zukunftsverpflichtungen, uneingelöste Kausalität", ""]
        for k, v in sorted(debt_layers.items(), key=lambda kv: kv[1], reverse=True)[:16]:
            lines.append(self.bar(v, max_debt, width=46, label=k[:21]))
        return self.box("ABGRUND DER NEGATIVEN WAHRHEIT", "\n".join(lines))

    def render_country_league(self, planet: "Planet") -> str:
        header = f"{'Land':<24} {'BIP':>12} {'Infl.':>8} {'Stab.':>8} {'WK':>12} {'Schulden/BIP':>12}"
        lines = [header, "─" * len(header)]
        for c in sorted(planet.countries, key=lambda x: x.gdp, reverse=True)[:18]:
            lines.append(f"{c.name[:24]:<24} {fmt_money(c.gdp):>12} {pct(c.inflation):>8} {c.stability:>8.3f} {c.wk_score():>12.2f} {safe_div(c.public_debt,c.gdp):>12.2f}")
        return self.box("LÄNDERLIGA", "\n".join(lines))

    def render_company_league(self, planet: "Planet") -> str:
        header = f"{'Firma':<30} {'Sektor':<16} {'Land':<18} {'Umsatz':>12} {'WK-Lücke':>9}"
        lines = [header, "─" * len(header)]
        for f in sorted(planet.companies, key=lambda x: x.revenue_last_month, reverse=True)[:20]:
            land = f.country.name if f.country else "-"
            lines.append(f"{f.name[:30]:<30} {f.SECTOR[:16]:<16} {land[:18]:<18} {fmt_money(f.revenue_last_month):>12} {f.wallet.truth.balance.truth_gap():>9.3f}")
        return self.box("UNTERNEHMENSLIGA", "\n".join(lines))

    def render_sector_bars(self, planet: "Planet") -> str:
        sector_rev: Dict[str, float] = {}
        sector_wk: Dict[str, float] = {}
        for f in planet.companies:
            sector_rev[f.SECTOR] = sector_rev.get(f.SECTOR, 0.0) + f.revenue_last_month
            sector_wk[f.SECTOR] = sector_wk.get(f.SECTOR, 0.0) + f.wk_score()
        max_rev = max(sector_rev.values() or [1.0])
        lines = ["Umsatz nach Sektoren:", ""]
        for s, v in sorted(sector_rev.items(), key=lambda kv: kv[1], reverse=True):
            lines.append(self.bar(v, max_rev, width=40, label=s[:20]))
        lines.append("")
        lines.append("WK-Score nach Sektoren:")
        max_wk = max([abs(v) for v in sector_wk.values()] + [1.0])
        for s, v in sorted(sector_wk.items(), key=lambda kv: abs(kv[1]), reverse=True):
            lines.append(self.signed_bar(v, max_wk, width=40, label=s[:20]))
        return self.box("SEKTOR-GRAFIKEN", "\n".join(lines))

    def render_fx_matrix(self, planet: "Planet") -> str:
        countries = sorted(planet.countries, key=lambda c: c.gdp, reverse=True)[:10]
        codes = [c.currency.code for c in countries]
        vals = [planet.fx_to_reference(code) for code in codes]
        lo, hi = min(vals or [0]), max(vals or [1])
        header = "      " + " ".join(f"{code:>4}" for code in codes)
        lines = [header]
        for code_i in codes:
            row = [f"{code_i:>4} "]
            for code_j in codes:
                value = safe_div(planet.fx_to_reference(code_i), planet.fx_to_reference(code_j), 1.0)
                row.append(f"  {self.heat_char(planet.fx_to_reference(code_i), lo, hi)} ")
            lines.append("".join(row))
        lines.append("")
        lines.append("Legende: · schwach/klein  ░ mittel  ▒ stark  ▓ sehr stark  █ höchste Referenz")
        return self.box("FIAT-WÄHRUNGS-HEATMAP", "\n".join(lines))

    def render_country_truth_matrix(self, planet: "Planet") -> str:
        countries = sorted(planet.countries, key=lambda c: c.gdp, reverse=True)[:14]
        layers = [
            TruthLayer.LEGAL.value, TruthLayer.CAUSAL.value, TruthLayer.EPISTEMIC.value,
            TruthLayer.SECURITY.value, TruthLayer.INFRASTRUCTURE.value, TruthLayer.HEALTH.value,
            TruthLayer.EDUCATION.value, TruthLayer.SOVEREIGNTY.value,
        ]
        vals = []
        for c in countries:
            for layer in layers:
                vals.append(c.wallet.truth.balance.values.get(layer, 0.0))
        lo, hi = min(vals or [0.0]), max(vals or [1.0])
        header = "Land                 " + " ".join(layer[:3].upper() for layer in layers)
        lines = [header, "─" * len(header)]
        for c in countries:
            row = f"{c.name[:20]:<20} "
            row += " ".join(f" {self.heat_char(c.wallet.truth.balance.values.get(layer,0.0), lo, hi)} " for layer in layers)
            lines.append(row)
        lines.append("")
        lines.append("Spalten: LEG=Legalität, CAU=Kausalität, EPI=Epistemik, SEC=Sicherheit, INF=Infrastruktur, HEA=Gesundheit, EDU=Bildung, SOV=Souveränität")
        return self.box("LÄNDER × WAHRHEITSDIMENSIONEN — HEATMAP", "\n".join(lines))

    def render_debt_pyramid(self, planet: "Planet") -> str:
        countries = sorted(planet.countries, key=lambda c: safe_div(c.public_debt, c.gdp, 0.0), reverse=True)[:18]
        max_ratio = max([safe_div(c.public_debt, c.gdp, 0.0) for c in countries] + [1.0])
        lines = ["Öffentliche Fiat-Schulden als negative Zukunftsbindung:", ""]
        for i, c in enumerate(countries, 1):
            ratio = safe_div(c.public_debt, c.gdp, 0.0)
            indent = " " * min(20, i)
            lines.append(indent + self.bar(ratio, max_ratio, width=42, label=c.name[:20]))
        return self.box("SCHULDENPYRAMIDE", "\n".join(lines))

    def render_transaction_mix(self, planet: "Planet") -> str:
        counts: Dict[str, int] = {}
        for tx in planet.transactions:
            counts[tx.get("type", "unknown")] = counts.get(tx.get("type", "unknown"), 0) + 1
        if not counts:
            return self.box("TRANSAKTIONSMIX", "Keine Transaktionen.")
        max_count = max(counts.values())
        lines = []
        for typ, count in sorted(counts.items(), key=lambda kv: kv[1], reverse=True):
            lines.append(self.bar(count, max_count, width=46, label=typ[:21]))
        lines.append("")
        lines.append("Jede Transaktion ist hier nicht nur Buchung, sondern ein Versuch, Realität anders wahr zu machen.")
        return self.box("TRANSAKTIONSMIX", "\n".join(lines))

    def render_bank_stress(self, planet: "Planet") -> str:
        banks = sorted(planet.banks, key=lambda b: b.nonperforming_ratio, reverse=True)[:20]
        if not banks:
            return self.box("BANKSTRESS", "Keine Banken.")
        lines = ["NPL = non-performing loans; hoher Wert erzeugt Liquiditäts- und Glaubwürdigkeits-Schulden", ""]
        for b in banks:
            lines.append(self.bar(b.nonperforming_ratio, 0.70, width=44, label=b.name[:21]))
        return self.box("BANKSTRESS / KREDIT-WAHRHEIT", "\n".join(lines))

    def render_currency_map(self, planet: "Planet") -> str:
        countries = sorted(planet.countries, key=lambda c: planet.fx_to_reference(c.currency.code), reverse=True)[:24]
        max_fx = max([planet.fx_to_reference(c.currency.code) for c in countries] + [1.0])
        lines = ["Nationale Zahlenwährungen relativ zur Referenz; WK bleibt planetar und vektorwertig.", ""]
        for c in countries:
            code = c.currency.code
            lines.append(self.bar(planet.fx_to_reference(code), max_fx, width=46, label=f"{code} {c.name[:16]}"))
        lines.append("")
        lines.append(f"Planetare WK-Referenz: 1 WK-Score ≈ {planet.truth_price_reference:,.2f} REF")
        return self.box("WÄHRUNGSLANDKARTE", "\n".join(lines))

    def render_event_histogram(self, planet: "Planet") -> str:
        if not planet.events:
            return self.box("EREIGNIS-HISTOGRAMM", "Keine Ereignisse.")
        counts: Dict[str, int] = {}
        severity: Dict[str, float] = {}
        for ev in planet.events:
            typ = ev.get("type", "unknown")
            counts[typ] = counts.get(typ, 0) + 1
            severity[typ] = severity.get(typ, 0.0) + float(ev.get("severity", 0.0))
        max_count = max(counts.values())
        max_sev = max(severity.values()) if severity else 1.0
        lines = ["Links Häufigkeit, rechts kumulierte Schwere:", ""]
        for typ in sorted(counts, key=lambda k: counts[k], reverse=True):
            lines.append(self.bar(counts[typ], max_count, width=24, label=typ[:18]) + "   " + self.bar(severity[typ], max_sev, width=22, label="severity"))
        return self.box("EREIGNIS-HISTOGRAMM", "\n".join(lines))

    def render_event_timeline(self, planet: "Planet") -> str:
        recent = planet.events[-28:]
        if not recent:
            return self.box("EREIGNIS-TIMELINE", "Noch keine Ereignisse.")
        lines = []
        for ev in recent:
            sev = float(ev.get("severity", 0.0))
            dots = "●" * int(clamp(sev, 0, 1) * 10 + 1)
            lines.append(f"M{ev['month']:>4} {ev['type']:<22} {dots:<11} {ev['message'][:68]}")
        return self.box("EREIGNIS-TIMELINE", "\n".join(lines))

    def render_flow_diagram(self) -> str:
        diagram = r"""
                          ┌─────────────────────────────┐
                          │  WK = Wahrheitskapital      │
                          │  Vektor: Recht, Kausalität, │
                          │  Existenz, Zeit, Risiko ... │
                          └──────────────┬──────────────┘
                                         │
      Fiat-Zahlung                       │ Wahrheits-Transfer / Realitätsänderung
┌──────────────┐     Kauf / Kredit       ▼
│ Haushalte /  │ ─────────────────▶ ┌──────────────┐ ───────────────▶ Produkt / Dienst / Claim
│ Staaten      │                    │ Unternehmen  │                  wird wahrer / nutzbarer
└──────┬───────┘ ◀───────────────── └──────┬───────┘
       │         Steuern, Löhne, Dividenden │
       │                                    │ Kredite / Schulden
       ▼                                    ▼
┌──────────────┐                    ┌──────────────┐
│ Zentralbank  │ ◀──── Reserven ─── │ Banken       │
│ Fiat-Stabil. │ ───── Liquidität ▶ │ Kreditmarkt  │
└──────┬───────┘                    └──────┬───────┘
       │                                    │
       ▼                                    ▼
┌──────────────┐                    ┌──────────────┐
│ UN / Recht   │ ── Audits/Sank. ▶  │ Wahrheits-   │
│ Anerkennung  │ ◀─ Legitimität ──  │ schulden     │
└──────────────┘                    └──────────────┘
""".strip()
        return self.box("ÖKONOMISCHER FLUSS: ZAHL → WAHRHEITSÜBERGANG", diagram)

    def render_truth_lifecycle_diagram(self) -> str:
        diagram = r"""
      Idee / Potenzial
             │
             ▼
    ┌─────────────────┐
    │  Versprechen    │  social/perception/potential steigen schnell
    └───────┬─────────┘
            │ Prüfung, Arbeit, Kapital, Zeit
            ▼
    ┌─────────────────┐
    │  gedeckte       │  existence/legal/causal/epistemic werden real
    │  Kausalität     │
    └───────┬─────────┘
            │ Nutzung / Kauf / Vertrag
            ▼
    ┌─────────────────┐
    │  Wahrheit als   │  WK zirkuliert: Anspruch auf spätere Wahrmachung
    │  Währung        │
    └───────┬─────────┘
            │ Alterung, Verschleiß, Erinnerung, Risiko
            ▼
    ┌─────────────────┐
    │  Prüfung oder   │  Wahrheit bleibt gedeckt ODER kippt in Schuld
    │  Entlarvung     │
    └───────┬─────────┘
            │
       ┌────┴────┐
       ▼         ▼
  Reinvestition  negative WK: Lüge, Kredit, nicht eingelöster Anspruch
""".strip()
        return self.box("LEBENSZYKLUS EINES WAHRHEITSWERTS", diagram)

    def render_institutional_network(self, planet: "Planet") -> str:
        lines = []
        if planet.un:
            lines.append(f"{planet.un.name}")
            for c in sorted(planet.countries, key=lambda x: x.gdp, reverse=True)[:16]:
                lines.append(f"  ├─ {c.name:<24} Beitrag/Legitimität: stab={c.stability:.2f} off={c.openness:.2f}")
            lines.append("  └─ ...")
        lines.append("")
        lines.append("Allianzen als soziale/legal-sicherheitliche Wahrheitsbrücken:")
        for org in planet.defense_orgs:
            member_line = " ⇄ ".join(m.name[:12] for m in org.members[:8])
            lines.append(f"  {org.name:<28} {member_line}")
        return self.box("INSTITUTIONELLES NETZWERK", "\n".join(lines))

    def render_security_diagram(self, planet: "Planet") -> str:
        lines = []
        for org in planet.defense_orgs:
            lines.append(f"{org.name} [{org.doctrine}] det={org.deterrence:.2f} interop={org.interoperability:.2f}")
            member_names = [m.name[:16] for m in org.members[:10]]
            lines.append("  ├─ " + "  ─  ".join(member_names))
            lines.append("  └─ " + self.bar(org.deterrence, 1.5, width=32, label="Abschreckung"))
        return self.box("VERTEIDIGUNGSORGANISATIONEN", "\n".join(lines) if lines else "Keine.")

    def render_potential_debt_scatter(self, planet: "Planet") -> str:
        width, height = 62, 18
        grid = [[" " for _ in range(width)] for _ in range(height)]
        countries = planet.countries
        if not countries:
            return self.box("POTENZIAL-SCHULDEN-SCATTER", "Keine Länder.")
        potentials = [c.wallet.truth.balance.values.get(TruthLayer.POTENTIAL.value, 0.0) + c.research_level * 10 for c in countries]
        debts = [safe_div(c.public_debt, c.gdp, 0.0) for c in countries]
        min_p, max_p = min(potentials), max(potentials)
        min_d, max_d = min(debts), max(debts)
        for c, p, d in zip(countries, potentials, debts):
            x = int(clamp(safe_div(p - min_p, max_p - min_p, 0.5), 0, 0.999) * width)
            y = height - 1 - int(clamp(safe_div(d - min_d, max_d - min_d, 0.5), 0, 0.999) * height)
            grid[y][x] = "●"
        lines = ["Schulden/BIP ↑", "┌" + "─" * width + "┐"]
        for row in grid:
            lines.append("│" + "".join(row) + "│")
        lines.append("└" + "─" * width + "┘")
        lines.append(" " * (width//2 - 8) + "Potenzial / Forschung →")
        lines.append("Interpretation: rechts oben = viel Potenzial, aber stark vorweggenommene Zukunft; rechts unten = robustes Zukunftskapital.")
        return self.box("POTENZIAL-SCHULDEN-SCATTER", "\n".join(lines))

    def render_market_sparklines(self, planet: "Planet") -> str:
        if not planet.history:
            return self.box("SPARKLINES", "Noch keine Historie.")
        keys = ["world_gdp", "truth_price", "avg_inflation", "avg_stability", "global_wk_score", "global_truth_gap"]
        labels = {
            "world_gdp": "Welt-BIP",
            "truth_price": "WK-Preis",
            "avg_inflation": "Ø Inflation",
            "avg_stability": "Ø Stabilität",
            "global_wk_score": "Globaler WK",
            "global_truth_gap": "WK-Lücke",
        }
        lines = []
        for key in keys:
            values = [float(h[key]) for h in planet.history if key in h]
            lines.append(f"{labels[key]:<16} {self.sparkline(values, width=72)}  min={min(values):.3g} max={max(values):.3g}")
        return self.box("ZEITREIHEN-SPARKLINES", "\n".join(lines))


# =============================================================================
# 12. Planet, Simulation und Factory
# =============================================================================


@dataclass
class WorldConfig:
    preset: str
    countries: int
    companies_per_country: int
    banks_per_country: int
    defense_orgs: int
    households_per_country: int = 2


PRESETS: Dict[str, WorldConfig] = {
    "tiny": WorldConfig("tiny", countries=6, companies_per_country=12, banks_per_country=2, defense_orgs=2),
    "standard": WorldConfig("standard", countries=18, companies_per_country=32, banks_per_country=4, defense_orgs=4),
    "large": WorldConfig("large", countries=36, companies_per_country=58, banks_per_country=6, defense_orgs=6),
    "epic": WorldConfig("epic", countries=64, companies_per_country=90, banks_per_country=8, defense_orgs=9),
}


class Planet:
    def __init__(self, name: str, rng: random.Random) -> None:
        self.name = name
        self.rng = rng
        self.month = 0
        self.truth_currency = TruthCurrency()
        self.truth_price_reference = 1_000_000.0
        self.countries: List[Country] = []
        self.central_banks: List[CentralBank] = []
        self.banks: List[CommercialBank] = []
        self.companies: List[Company] = []
        self.households: List[Household] = []
        self.un: Optional[UnitedNations] = None
        self.defense_orgs: List[DefenseOrganization] = []
        self.markets: List[Market] = []
        self.fx_rates: Dict[str, float] = {}  # local -> REF
        self.ledger = TruthLedger()
        self.transactions: List[Dict[str, Any]] = []
        self.events: List[Dict[str, Any]] = []
        self.history: List[Dict[str, Any]] = []
        self.sector_multipliers: Dict[str, float] = {}

    def add_country(self, country: Country) -> None:
        self.countries.append(country)
        self.fx_rates[country.currency.code] = max(0.05, self.rng.lognormvariate(0.0, 0.65))

    def add_company(self, company: Company) -> None:
        self.companies.append(company)
        if company.country:
            company.country.companies.append(company)

    def add_bank(self, bank: CommercialBank) -> None:
        self.banks.append(bank)
        if bank.country:
            bank.country.banks.append(bank)

    def add_central_bank(self, bank: CentralBank) -> None:
        self.central_banks.append(bank)
        if bank.country:
            bank.country.central_bank = bank

    def all_nodes(self) -> List[SimNode]:
        nodes: List[SimNode] = []
        nodes.extend(self.countries)
        nodes.extend(self.central_banks)
        nodes.extend(self.banks)
        nodes.extend(self.companies)
        nodes.extend(self.households)
        if self.un:
            nodes.append(self.un)
        nodes.extend(self.defense_orgs)
        return nodes

    def fx_to_reference(self, code: str) -> float:
        return self.fx_rates.get(code, 1.0)

    def sector_price_multiplier(self, sector: str) -> float:
        return self.sector_multipliers.get(sector, 1.0)

    def record_event(self, typ: str, message: str, severity: float) -> None:
        self.events.append({
            "month": self.month,
            "type": typ,
            "message": message,
            "severity": clamp(float(severity), 0.0, 1.0),
        })

    def age_all_truth(self) -> None:
        for node in self.all_nodes():
            node.age_truth()

    def update_fx(self) -> None:
        for c in self.countries:
            code = c.currency.code
            drift = 0.002 * (c.stability - 0.5) - c.inflation * 0.006 + self.rng.uniform(-0.018, 0.018)
            self.fx_rates[code] = clamp(self.fx_rates.get(code, 1.0) * (1.0 + drift), 0.01, 25.0)

    def update_sector_multipliers(self) -> None:
        sectors = {cls.SECTOR for cls in COMPANY_CLASSES}
        for s in sectors:
            base = self.sector_multipliers.get(s, 1.0)
            pressure = mean_or([c.needs.get(s, 1.0) for c in self.countries], 1.0)
            self.sector_multipliers[s] = clamp(base * (1.0 + (pressure - 1.0) * 0.01 + self.rng.uniform(-0.015, 0.015)), 0.25, 6.0)

    def maybe_random_events(self) -> None:
        for event_cls in EVENT_CLASSES:
            p = event_cls.BASE_PROBABILITY * (1.0 + 0.35 * math.sin(self.month / 19.0))
            if self.rng.random() < p:
                severity = clamp(self.rng.betavariate(2.0, 5.0) * 1.4, 0.05, 1.0)
                event = event_cls(severity)
                event.apply(self)

    def audit_truth(self) -> None:
        if not self.un or not self.companies:
            return
        audits = max(1, len(self.companies) // 80)
        candidates = sorted(self.companies, key=lambda f: f.wallet.truth.balance.truth_gap() + f.fraud_risk, reverse=True)
        for firm in candidates[:audits]:
            tx = AuditTransaction(self.un, firm, intensity=0.30 + firm.fraud_risk)
            self.ledger.execute(tx, self)

    def collect_taxes(self) -> None:
        for c in self.countries:
            c.collect_taxes(self)

    def clear_markets(self) -> None:
        for market in self.markets:
            market.clear(self)

    def snapshot(self) -> Dict[str, Any]:
        world_gdp = sum(c.gdp for c in self.countries)
        aggregate = TruthStack()
        for node in self.all_nodes():
            aggregate.add(node.wallet.truth.balance)
        global_wk_score = aggregate.score()
        total_pos = aggregate.positive_score()
        total_neg = abs(aggregate.negative_score())
        return {
            "month": self.month,
            "world_gdp": world_gdp,
            "truth_price": self.truth_price_reference,
            "avg_inflation": mean_or([c.inflation for c in self.countries]),
            "avg_unemployment": mean_or([c.unemployment for c in self.countries]),
            "avg_stability": mean_or([c.stability for c in self.countries]),
            "global_wk_score": global_wk_score,
            "global_positive_wk": total_pos,
            "global_negative_wk": total_neg,
            "global_truth_gap": safe_div(total_neg, total_pos + total_neg + 1e-9),
            "transactions": len(self.transactions),
            "events": len(self.events),
        }

    def step(self) -> None:
        self.month += 1
        self.age_all_truth()
        self.update_sector_multipliers()
        self.update_fx()
        # Zuerst Institutionen und Makroakteure.
        for cb in self.central_banks:
            cb.step(self)
        for bank in self.banks:
            bank.step(self)
        for org in self.defense_orgs:
            org.step(self)
        if self.un:
            self.un.step(self)
        # Staaten und Firmen.
        for c in self.countries:
            c.step(self)
        for firm in self.companies:
            firm.step(self)
        self.collect_taxes()
        self.clear_markets()
        self.audit_truth()
        self.maybe_random_events()
        self.history.append(self.snapshot())

    def run(self, months: int, verbose: bool = False, report_every: int = 12) -> None:
        for _ in range(months):
            self.step()
            if verbose and (self.month == 1 or self.month % report_every == 0 or self.month == months):
                snap = self.history[-1]
                print(
                    f"M{self.month:04d} | Welt-BIP {fmt_money(snap['world_gdp'])} | "
                    f"WK {snap['global_wk_score']:.2f} | Lücke {snap['global_truth_gap']:.3f} | "
                    f"Ereignisse {snap['events']}"
                )


class PlanetFactory:
    COUNTRY_PREFIXES = [
        "Aurelia", "Borealis", "Cyrenia", "Demeria", "Elyria", "Falken", "Gaia", "Helion",
        "Istria", "Juno", "Kalmora", "Lys", "Meridia", "Norian", "Orbis", "Praxa",
        "Quirin", "Ravena", "Solara", "Tir", "Umbra", "Valen", "Westmark", "Xandria",
        "Yara", "Zenit", "Arden", "Brava", "Corvin", "Deltora", "Estara", "Freiland",
    ]
    COUNTRY_SUFFIXES = ["Republic", "Union", "Kingdom", "Federation", "Compact", "State", "Commonwealth", "League"]
    ARCHETYPES = ["industrial", "service", "resource", "research", "island", "agrarian", "financial", "security"]
    FIRM_NAMES = [
        "Atlas", "Nova", "Veritas", "Causal", "Mira", "Solis", "Nexus", "Praxis", "Argent",
        "Helix", "Orion", "Agora", "Vector", "Lucent", "Kappa", "Terra", "Axiom", "Civitas",
        "Pulse", "Anchor", "Summit", "Clear", "Forge", "Signal", "Harbor", "Vivid", "Pioneer",
    ]

    @classmethod
    def create(cls, config: WorldConfig, seed: int) -> Planet:
        rng = random.Random(seed)
        planet = Planet("Gaia-WK", rng)
        # Länder.
        used_codes = set()
        for i in range(config.countries):
            base = cls.COUNTRY_PREFIXES[i % len(cls.COUNTRY_PREFIXES)]
            suffix = rng.choice(cls.COUNTRY_SUFFIXES)
            name = f"{base} {suffix}"
            code = (base[:2].upper() + suffix[:1].upper())[:3]
            while code in used_codes:
                code = (code[:2] + chr(ord('A') + rng.randint(0, 25)))[:3]
            used_codes.add(code)
            currency = FiatCurrency(code, f"{base} {suffix} Credit", name)
            population = int(rng.lognormvariate(16.3, 1.0))
            gdp = rng.lognormvariate(28.2, 1.0)
            archetype = rng.choice(cls.ARCHETYPES)
            country = Country(name, currency, population, gdp, archetype, rng)
            planet.add_country(country)
        # UN.
        planet.un = UnitedNations()
        for c in planet.countries:
            planet.un.add_member(c)
        # Zentralbanken und Banken.
        for c in planet.countries:
            cb = CentralBank(f"Central Bank of {c.name}", c)
            planet.add_central_bank(cb)
            for j in range(config.banks_per_country):
                if j == 0 and rng.random() < 0.45:
                    bank = DevelopmentBank(f"{c.name.split()[0]} Development Bank", c, rng)
                elif j == 1 and rng.random() < 0.45:
                    bank = InvestmentBank(f"{c.name.split()[0]} Investment Bank", c, rng)
                else:
                    bank = CommercialBank(f"{rng.choice(cls.FIRM_NAMES)} Bank {c.currency.code}-{j+1}", c, rng)
                planet.add_bank(bank)
        # Haushalte und Firmen.
        for c in planet.countries:
            for h in range(config.households_per_country):
                hh = Household(f"Household Cluster {c.name}-{h+1}", c, max(1000, c.population // config.households_per_country))
                planet.households.append(hh)
                c.households.append(hh)
            for j in range(config.companies_per_country):
                cls_choice = cls.choose_company_class(rng, c.archetype)
                name = f"{rng.choice(cls.FIRM_NAMES)} {cls_choice.SECTOR.title()} {c.currency.code}-{j+1}"
                firm = cls_choice(name, c, rng)
                planet.add_company(firm)
        # Verteidigungsorganisationen.
        org_classes: List[Type[DefenseOrganization]] = [MutualDefensePact, MaritimeSecurityLeague, CyberDefenseCompact]
        for k in range(config.defense_orgs):
            org_cls = org_classes[k % len(org_classes)]
            org = org_cls(f"{['North','South','Oceanic','Continental','Orbital','Civic','Shield','Vector','Meridian'][k % 9]} Security Accord")
            member_count = rng.randint(max(2, config.countries // 6), max(3, config.countries // 3))
            for c in rng.sample(planet.countries, k=min(member_count, len(planet.countries))):
                org.add_member(c)
            planet.defense_orgs.append(org)
        # Märkte.
        planet.markets = [GoodsMarket("Global Goods Market"), CreditMarket("Credit Market"), LaborMarket("Labor Market"), TruthMarket("Truth Capital Market"), DefenseMarket("Defense Market")]
        # Startpreise pro Sektor.
        for company_cls in COMPANY_CLASSES:
            planet.sector_multipliers[company_cls.SECTOR] = rng.lognormvariate(0.0, 0.25)
        return planet

    @classmethod
    def choose_company_class(cls, rng: random.Random, archetype: str) -> Type[Company]:
        weights: List[float] = []
        for company_cls in COMPANY_CLASSES:
            w = 1.0
            if archetype == "industrial" and issubclass(company_cls, IndustrialCompany):
                w *= 3.0
            if archetype == "service" and issubclass(company_cls, (ExperienceCompany, KnowledgeCompany)):
                w *= 2.4
            if archetype == "resource" and company_cls in (MiningCompany, EnergyCompany, LogisticsCompany):
                w *= 3.0
            if archetype == "research" and company_cls in (ResearchCompany, SoftwareCompany, EducationCompany, SpaceCompany):
                w *= 3.2
            if archetype == "island" and company_cls in (TourismCompany, LogisticsCompany, FoodCompany):
                w *= 1.8
            if archetype == "agrarian" and company_cls in (FoodCompany, WaterCompany, EnergyCompany):
                w *= 2.8
            if archetype == "financial" and company_cls in (InsuranceCompany, LegalCompany, SoftwareCompany, LuxuryCompany):
                w *= 2.2
            if archetype == "security" and company_cls in (DefenseCompany, CyberSecurityCompany, LegalCompany):
                w *= 3.0
            weights.append(w)
        return weighted_choice(rng, COMPANY_CLASSES, weights)


# =============================================================================
# 13. Report Writer
# =============================================================================


class ReportWriter:
    def __init__(self, out_dir: Path) -> None:
        self.out_dir = out_dir
        self.out_dir.mkdir(parents=True, exist_ok=True)

    def write_all(self, planet: Planet) -> None:
        self.write_history(planet)
        self.write_countries(planet)
        self.write_companies(planet)
        self.write_banks(planet)
        self.write_events(planet)
        self.write_summary(planet)
        self.write_art(planet)

    def write_history(self, planet: Planet) -> None:
        path = self.out_dir / "history.csv"
        if not planet.history:
            path.write_text("", encoding="utf-8")
            return
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(planet.history[0].keys()))
            writer.writeheader()
            writer.writerows(planet.history)

    def write_countries(self, planet: Planet) -> None:
        path = self.out_dir / "countries.csv"
        fields = ["id", "name", "currency", "population", "gdp", "inflation", "unemployment", "stability", "public_debt", "wk_score", "truth_gap", "archetype"]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for c in planet.countries:
                writer.writerow({
                    "id": c.id,
                    "name": c.name,
                    "currency": c.currency.code,
                    "population": c.population,
                    "gdp": c.gdp,
                    "inflation": c.inflation,
                    "unemployment": c.unemployment,
                    "stability": c.stability,
                    "public_debt": c.public_debt,
                    "wk_score": c.wk_score(),
                    "truth_gap": c.wallet.truth.balance.truth_gap(),
                    "archetype": c.archetype,
                })

    def write_companies(self, planet: Planet) -> None:
        path = self.out_dir / "companies.csv"
        fields = ["id", "name", "class", "sector", "country", "employees", "productivity", "revenue_last_month", "profit_last_month", "fraud_risk", "reputation", "wk_score", "truth_gap"]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for firm in planet.companies:
                writer.writerow({
                    "id": firm.id,
                    "name": firm.name,
                    "class": firm.__class__.__name__,
                    "sector": firm.SECTOR,
                    "country": firm.country.name if firm.country else "",
                    "employees": firm.employees,
                    "productivity": firm.productivity,
                    "revenue_last_month": firm.revenue_last_month,
                    "profit_last_month": firm.profit_last_month,
                    "fraud_risk": firm.fraud_risk,
                    "reputation": firm.reputation,
                    "wk_score": firm.wk_score(),
                    "truth_gap": firm.wallet.truth.balance.truth_gap(),
                })

    def write_banks(self, planet: Planet) -> None:
        path = self.out_dir / "banks.csv"
        fields = ["id", "name", "class", "country", "assets", "liabilities", "capital_ratio", "nonperforming_ratio", "wk_score", "truth_gap"]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for bank in planet.banks:
                writer.writerow({
                    "id": bank.id,
                    "name": bank.name,
                    "class": bank.__class__.__name__,
                    "country": bank.country.name if bank.country else "",
                    "assets": bank.assets,
                    "liabilities": bank.liabilities,
                    "capital_ratio": bank.capital_ratio,
                    "nonperforming_ratio": bank.nonperforming_ratio,
                    "wk_score": bank.wk_score(),
                    "truth_gap": bank.wallet.truth.balance.truth_gap(),
                })

    def write_events(self, planet: Planet) -> None:
        (self.out_dir / "events.json").write_text(json.dumps(planet.events, ensure_ascii=False, indent=2), encoding="utf-8")
        (self.out_dir / "transactions.json").write_text(json.dumps(planet.transactions[-5000:], ensure_ascii=False, indent=2), encoding="utf-8")

    def write_summary(self, planet: Planet) -> None:
        renderer = UTF8Renderer()
        snap = planet.history[-1] if planet.history else planet.snapshot()
        summary = f"""
Planetare Wirtschaftssimulation — OOP/UTF-8 Edition
===================================================

Monate: {planet.month}
Länder: {len(planet.countries)}
Unternehmen: {len(planet.companies)}
Banken: {len(planet.banks)}
Zentralbanken: {len(planet.central_banks)}
Verteidigungsorganisationen: {len(planet.defense_orgs)}
Transaktionen: {len(planet.transactions)}
Ereignisse: {len(planet.events)}

Welt-BIP: {fmt_money(snap['world_gdp'])}
Globaler WK-Score: {snap['global_wk_score']:.2f}
Globale WK-Lücke: {snap['global_truth_gap']:.4f}
WK-Referenzpreis: {planet.truth_price_reference:.4f}
Ø Inflation: {pct(snap['avg_inflation'])}
Ø Stabilität: {snap['avg_stability']:.4f}

Der folgende Anhang ist absichtlich UTF-8/Unicode-Art: Diagramme, Balken,
Heatmaps, Klassenbaum, Zeitreihen und Wahrheitswert-Visualisierungen.

{renderer.render(planet)}
""".strip()
        (self.out_dir / "summary.txt").write_text(summary, encoding="utf-8")
        (self.out_dir / "summary.json").write_text(json.dumps(snap, ensure_ascii=False, indent=2), encoding="utf-8")

    def write_art(self, planet: Planet) -> None:
        art = UTF8Renderer().render(planet)
        (self.out_dir / "utf8_art_report.txt").write_text(art, encoding="utf-8")


# =============================================================================
# 14. CLI
# =============================================================================


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Planetare OOP-Wirtschaftssimulation mit WK-Wahrheitswährung und UTF-8-Art-Reports.")
    parser.add_argument("--preset", choices=sorted(PRESETS), default="standard")
    parser.add_argument("--months", type=int, default=120)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--out", type=str, default="truth_oop_output")
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--print-art", action="store_true", help="Druckt den UTF-8-Art-Report nach dem Lauf zusätzlich in die Konsole.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    config = PRESETS[args.preset]
    planet = PlanetFactory.create(config, seed=args.seed)
    planet.run(args.months, verbose=args.verbose)
    writer = ReportWriter(Path(args.out))
    writer.write_all(planet)
    print(f"Fertig: {args.out}")
    print(f"- history.csv")
    print(f"- countries.csv")
    print(f"- companies.csv")
    print(f"- banks.csv")
    print(f"- events.json")
    print(f"- transactions.json")
    print(f"- summary.txt")
    print(f"- utf8_art_report.txt")
    if args.print_art:
        print("\n" + UTF8Renderer().render(planet))


if __name__ == "__main__":
    main()
