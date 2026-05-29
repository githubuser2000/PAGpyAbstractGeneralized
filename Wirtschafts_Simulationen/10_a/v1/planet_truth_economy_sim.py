#!/usr/bin/env python3
"""
Planetare Wirtschaftssimulation mit gestapelter Wahrheitswert-Währung.

Dieses Skript modelliert einen Planeten mit:
- Ländern und je eigener Fiat-/Zahlenwährung
- Zentralbanken und Geschäftsbanken
- Unternehmen in vielen Sektoren
- einer UN-ähnlichen Institution
- mehreren Verteidigungsorganisationen
- klassischen Geldzahlungen plus einer globalen, vektorwertigen Wahrheitswährung

Die globale Wahrheitswährung heißt hier WK = Wahrheitskapital.
WK ist keine einzelne Zahl, sondern ein Stapel/Vektor aus Wahrheitsdimensionen:
Existenz, epistemische Korrektheit, soziale Anerkennung, Legalität,
Kausalität, Zeitbindung, Risikoreduktion, Potenzial, Wahrnehmung,
Vergleich/Status, Sicherheit, Liquidität, Ethik, Ökologie, Infrastruktur,
Gesundheit, Aufmerksamkeit und Erinnerung.

Kaufen bedeutet in diesem Modell:
    Fiat-Zahlung + Wahrheitswert-Zahlung gegen eine Realitätsänderung.

Schulden entstehen als negative Wahrheitswerte, zum Beispiel:
    - rechtliche Verpflichtung
    - zeitliche Vorwegnahme
    - soziale Glaubwürdigkeitslast
    - epistemische Schuld bei Betrug oder falschen Versprechen

Das Modell ist bewusst groß und modular, aber ohne externe Bibliotheken.
Es ist kein ökonomisches Prognoseinstrument, sondern ein Simulationsbaukasten.

Beispiele:
    python planet_truth_economy_sim.py --preset tiny --months 24
    python planet_truth_economy_sim.py --preset standard --months 120 --seed 7 --out sim_output
    python planet_truth_economy_sim.py --preset epic --months 600 --seed 42 --out epic_world
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
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, Iterable, List, Optional, Sequence, Tuple


# ---------------------------------------------------------------------------
# Kleine Hilfsfunktionen
# ---------------------------------------------------------------------------


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    return a / b if abs(b) > 1e-12 else default


def uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def mean_or(values: Iterable[float], default: float = 0.0) -> float:
    values = list(values)
    return statistics.mean(values) if values else default


def weighted_choice(
    rng: random.Random,
    items: Sequence[Any],
    weight_fn: Callable[[Any], float],
) -> Optional[Any]:
    if not items:
        return None
    weights = [max(0.0, float(weight_fn(item))) for item in items]
    total = sum(weights)
    if total <= 0.0:
        return rng.choice(list(items))
    r = rng.random() * total
    acc = 0.0
    for item, w in zip(items, weights):
        acc += w
        if acc >= r:
            return item
    return items[-1]


# ---------------------------------------------------------------------------
# Wahrheitswert-Schichten
# ---------------------------------------------------------------------------


class Layer(str, Enum):
    EXISTENCE = "existence"                # Das Ding / der Zustand existiert.
    EPISTEMIC = "epistemic"                # Geprüft, belegt, korrekt, bekannt.
    SOCIAL = "social"                      # Von anderen anerkannt.
    LEGAL = "legal"                        # Institutionell gültig.
    CAUSAL = "causal"                      # Kann Wirkungen erzeugen.
    TEMPORAL = "temporal"                  # Zeitbindung, Reservierung, Dauer.
    RISK_REDUCTION = "risk_reduction"      # Risiko wird reduziert / abgesichert.
    POTENTIAL = "potential"                # Möglichkeit, Option, Zukunftsfähigkeit.
    PERCEPTION = "perception"              # Wahrnehmung, Schönheit, Image.
    COMPARATIVE = "comparative"            # Besser/knapper/schneller als andere.
    SECURITY = "security"                  # Schutz, Verteidigung, Abschreckung.
    LIQUIDITY = "liquidity"                # Tauschbarkeit, Zahlungsfähigkeit.
    ETHICAL = "ethical"                    # Legitimität, Verantwortung, Fairness.
    ECOLOGICAL = "ecological"              # Umweltzustand, Nachhaltigkeit.
    INFRASTRUCTURE = "infrastructure"      # Straßen, Netze, Gebäude, Systeme.
    HEALTH = "health"                      # Körperliche und soziale Gesundheit.
    ATTENTION = "attention"                # Aufmerksamkeit, Fokus, Arbeitszeit.
    MEMORY = "memory"                      # Erzählbarkeit, Erinnerung, Kulturspur.


ALL_LAYERS: Tuple[str, ...] = tuple(layer.value for layer in Layer)

# Ein Score ist nur die grobe Zahlform des Stapels. Der Vektor selbst bleibt erhalten.
DEFAULT_LAYER_WEIGHTS: Dict[str, float] = {
    Layer.EXISTENCE.value: 1.05,
    Layer.EPISTEMIC.value: 1.30,
    Layer.SOCIAL.value: 0.90,
    Layer.LEGAL.value: 1.20,
    Layer.CAUSAL.value: 1.35,
    Layer.TEMPORAL.value: 0.85,
    Layer.RISK_REDUCTION.value: 1.10,
    Layer.POTENTIAL.value: 1.25,
    Layer.PERCEPTION.value: 0.75,
    Layer.COMPARATIVE.value: 0.80,
    Layer.SECURITY.value: 1.40,
    Layer.LIQUIDITY.value: 1.00,
    Layer.ETHICAL.value: 0.95,
    Layer.ECOLOGICAL.value: 1.05,
    Layer.INFRASTRUCTURE.value: 1.30,
    Layer.HEALTH.value: 1.35,
    Layer.ATTENTION.value: 0.70,
    Layer.MEMORY.value: 0.65,
}

# Manche Wahrheiten altern schneller als andere. Perzeption und Aufmerksamkeit
# verdampfen schneller als Legalität oder Infrastruktur.
POSITIVE_DECAY: Dict[str, float] = {
    Layer.EXISTENCE.value: 0.001,
    Layer.EPISTEMIC.value: 0.004,
    Layer.SOCIAL.value: 0.008,
    Layer.LEGAL.value: 0.002,
    Layer.CAUSAL.value: 0.006,
    Layer.TEMPORAL.value: 0.030,
    Layer.RISK_REDUCTION.value: 0.010,
    Layer.POTENTIAL.value: 0.014,
    Layer.PERCEPTION.value: 0.045,
    Layer.COMPARATIVE.value: 0.025,
    Layer.SECURITY.value: 0.015,
    Layer.LIQUIDITY.value: 0.006,
    Layer.ETHICAL.value: 0.006,
    Layer.ECOLOGICAL.value: 0.003,
    Layer.INFRASTRUCTURE.value: 0.004,
    Layer.HEALTH.value: 0.004,
    Layer.ATTENTION.value: 0.065,
    Layer.MEMORY.value: 0.010,
}

# Negative Wahrheitswerte wachsen wie Zinsen, weil offene Verpflichtungen Druck erzeugen.
NEGATIVE_GROWTH: Dict[str, float] = {
    Layer.EXISTENCE.value: 0.004,
    Layer.EPISTEMIC.value: 0.018,
    Layer.SOCIAL.value: 0.010,
    Layer.LEGAL.value: 0.012,
    Layer.CAUSAL.value: 0.006,
    Layer.TEMPORAL.value: 0.020,
    Layer.RISK_REDUCTION.value: 0.010,
    Layer.POTENTIAL.value: 0.008,
    Layer.PERCEPTION.value: 0.009,
    Layer.COMPARATIVE.value: 0.006,
    Layer.SECURITY.value: 0.012,
    Layer.LIQUIDITY.value: 0.015,
    Layer.ETHICAL.value: 0.012,
    Layer.ECOLOGICAL.value: 0.006,
    Layer.INFRASTRUCTURE.value: 0.006,
    Layer.HEALTH.value: 0.006,
    Layer.ATTENTION.value: 0.005,
    Layer.MEMORY.value: 0.004,
}


def layer_name(layer: str | Layer) -> str:
    return layer.value if isinstance(layer, Layer) else str(layer)


@dataclass
class TruthStack:
    """Vektorwertige Wahrheitswährung WK.

    Positive Komponenten sind gedeckte Wahrheitswerte / Ansprüche / Fähigkeiten.
    Negative Komponenten sind Schulden, Lügenlasten, Zukunftsverpflichtungen oder
    nicht eingelöste Kausalversprechen.
    """

    values: Dict[str, float] = field(default_factory=dict)
    source: str = ""
    confidence: float = 1.0

    def __post_init__(self) -> None:
        cleaned: Dict[str, float] = {}
        for k, v in self.values.items():
            key = layer_name(k)
            if key not in ALL_LAYERS:
                raise ValueError(f"Unbekannte Wahrheits-Schicht: {key}")
            fv = float(v)
            if abs(fv) > 1e-12:
                cleaned[key] = fv
        self.values = cleaned
        self.confidence = clamp(float(self.confidence), 0.0, 1.0)

    @classmethod
    def zero(cls) -> "TruthStack":
        return cls({})

    @classmethod
    def from_layers(cls, **kwargs: float) -> "TruthStack":
        values: Dict[str, float] = {}
        for key, value in kwargs.items():
            layer_key = key.lower()
            if layer_key not in ALL_LAYERS:
                # Erlaubt auch Enum-Namen wie RISK_REDUCTION.
                layer_key = getattr(Layer, key.upper()).value if hasattr(Layer, key.upper()) else layer_key
            values[layer_key] = float(value)
        return cls(values)

    def copy(self) -> "TruthStack":
        return TruthStack(dict(self.values), source=self.source, confidence=self.confidence)

    def get(self, layer: str | Layer) -> float:
        return self.values.get(layer_name(layer), 0.0)

    def add_layer(self, layer: str | Layer, amount: float) -> None:
        key = layer_name(layer)
        self.values[key] = self.values.get(key, 0.0) + float(amount)
        if abs(self.values[key]) < 1e-12:
            del self.values[key]

    def scaled(self, factor: float) -> "TruthStack":
        return TruthStack(
            {k: v * float(factor) for k, v in self.values.items()},
            source=self.source,
            confidence=self.confidence,
        )

    def __add__(self, other: "TruthStack") -> "TruthStack":
        out = self.copy()
        for k, v in other.values.items():
            out.add_layer(k, v)
        out.confidence = min(self.confidence, other.confidence)
        return out

    def __sub__(self, other: "TruthStack") -> "TruthStack":
        out = self.copy()
        for k, v in other.values.items():
            out.add_layer(k, -v)
        out.confidence = min(self.confidence, other.confidence)
        return out

    def __mul__(self, factor: float) -> "TruthStack":
        return self.scaled(factor)

    __rmul__ = __mul__

    def score(self, weights: Optional[Dict[str, float]] = None, confidence_adjusted: bool = True) -> float:
        weights = weights or DEFAULT_LAYER_WEIGHTS
        raw = sum(v * weights.get(k, 1.0) for k, v in self.values.items())
        return raw * (self.confidence if confidence_adjusted else 1.0)

    def positive_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        weights = weights or DEFAULT_LAYER_WEIGHTS
        return sum(max(0.0, v) * weights.get(k, 1.0) for k, v in self.values.items()) * self.confidence

    def negative_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        weights = weights or DEFAULT_LAYER_WEIGHTS
        return sum(min(0.0, v) * weights.get(k, 1.0) for k, v in self.values.items()) * self.confidence

    def debt_score(self, weights: Optional[Dict[str, float]] = None) -> float:
        return -self.negative_score(weights)

    def decayed(self, months: int = 1) -> "TruthStack":
        current = self.copy()
        for _ in range(months):
            new_values: Dict[str, float] = {}
            for k, v in current.values.items():
                if v >= 0:
                    nv = v * (1.0 - POSITIVE_DECAY.get(k, 0.005))
                else:
                    nv = v * (1.0 + NEGATIVE_GROWTH.get(k, 0.008))
                if abs(nv) > 1e-10:
                    new_values[k] = nv
            current = TruthStack(new_values, source=current.source, confidence=current.confidence)
        return current

    def top_layers(self, n: int = 5) -> List[Tuple[str, float]]:
        return sorted(self.values.items(), key=lambda kv: abs(kv[1]), reverse=True)[:n]

    def as_dict(self) -> Dict[str, float]:
        return {k: round(v, 6) for k, v in sorted(self.values.items())}

    def compact(self, n: int = 4) -> str:
        if not self.values:
            return "{}"
        parts = [f"{k}={v:+.2f}" for k, v in self.top_layers(n)]
        if len(self.values) > n:
            parts.append("...")
        return "{" + ", ".join(parts) + "}"


# ---------------------------------------------------------------------------
# Kaufprofile: Welche Realitätsaussage wird gekauft?
# ---------------------------------------------------------------------------


@dataclass
class PurchaseTemplate:
    key: str
    label: str
    sector: str
    demand_weight: float
    base_price: float
    truth_profile: TruthStack
    description: str


SECTORS: Tuple[str, ...] = (
    "food",
    "housing",
    "mobility",
    "energy",
    "health",
    "education",
    "defense",
    "finance",
    "software",
    "tourism",
    "media",
    "luxury",
    "logistics",
    "construction",
    "research",
    "agriculture",
    "mining",
    "insurance",
    "security",
    "legal",
    "entertainment",
)


PURCHASE_TEMPLATES: Dict[str, PurchaseTemplate] = {
    "food_security": PurchaseTemplate(
        key="food_security",
        label="Nahrung / Versorgung",
        sector="food",
        demand_weight=0.125,
        base_price=35.0,
        truth_profile=TruthStack({
            Layer.EXISTENCE.value: 0.35,
            Layer.HEALTH.value: 0.90,
            Layer.TEMPORAL.value: 0.25,
            Layer.RISK_REDUCTION.value: 0.45,
        }),
        description="Die Aussage 'Menschen können essen und bleiben handlungsfähig' wird wahrer.",
    ),
    "housing_right": PurchaseTemplate(
        key="housing_right",
        label="Wohnraum / Aufenthaltsrecht",
        sector="housing",
        demand_weight=0.135,
        base_price=180.0,
        truth_profile=TruthStack({
            Layer.EXISTENCE.value: 0.40,
            Layer.LEGAL.value: 0.95,
            Layer.SOCIAL.value: 0.65,
            Layer.SECURITY.value: 0.70,
            Layer.TEMPORAL.value: 0.85,
            Layer.INFRASTRUCTURE.value: 0.45,
        }),
        description="Die Aussage 'Ich darf hier wohnen und werde nicht vertrieben' wird wahrer.",
    ),
    "ticket_arrival": PurchaseTemplate(
        key="ticket_arrival",
        label="Ticket / Ankommen",
        sector="mobility",
        demand_weight=0.045,
        base_price=52.0,
        truth_profile=TruthStack({
            Layer.CAUSAL.value: 0.95,
            Layer.TEMPORAL.value: 0.70,
            Layer.LEGAL.value: 0.25,
            Layer.RISK_REDUCTION.value: 0.25,
            Layer.INFRASTRUCTURE.value: 0.35,
        }),
        description="Die Aussage 'Ich werde von A nach B ankommen' wird wahrscheinlicher.",
    ),
    "car_mobility": PurchaseTemplate(
        key="car_mobility",
        label="Auto / eigenständige Bewegung",
        sector="mobility",
        demand_weight=0.020,
        base_price=420.0,
        truth_profile=TruthStack({
            Layer.EXISTENCE.value: 0.50,
            Layer.LEGAL.value: 0.40,
            Layer.CAUSAL.value: 1.40,
            Layer.TEMPORAL.value: 0.45,
            Layer.COMPARATIVE.value: 0.20,
            Layer.RISK_REDUCTION.value: 0.15,
        }),
        description="Die Aussage 'Ich kann unabhängig fahren' wird wahrer.",
    ),
    "energy_supply": PurchaseTemplate(
        key="energy_supply",
        label="Energie / Betrieb",
        sector="energy",
        demand_weight=0.075,
        base_price=75.0,
        truth_profile=TruthStack({
            Layer.CAUSAL.value: 0.85,
            Layer.INFRASTRUCTURE.value: 0.75,
            Layer.RISK_REDUCTION.value: 0.25,
            Layer.ECOLOGICAL.value: -0.20,
        }),
        description="Die Aussage 'Maschinen, Haushalte und Systeme können laufen' wird wahrer.",
    ),
    "healthcare": PurchaseTemplate(
        key="healthcare",
        label="Gesundheit / Behandlung",
        sector="health",
        demand_weight=0.085,
        base_price=120.0,
        truth_profile=TruthStack({
            Layer.HEALTH.value: 1.40,
            Layer.EPISTEMIC.value: 0.40,
            Layer.RISK_REDUCTION.value: 0.80,
            Layer.POTENTIAL.value: 0.30,
        }),
        description="Die Aussage 'Körperzustand und Lebensfähigkeit verbessern sich' wird wahrscheinlicher.",
    ),
    "education_potential": PurchaseTemplate(
        key="education_potential",
        label="Bildung / zukünftiges Können",
        sector="education",
        demand_weight=0.060,
        base_price=90.0,
        truth_profile=TruthStack({
            Layer.POTENTIAL.value: 1.25,
            Layer.EPISTEMIC.value: 0.95,
            Layer.CAUSAL.value: 0.45,
            Layer.TEMPORAL.value: 0.35,
            Layer.SOCIAL.value: 0.25,
        }),
        description="Die Aussage 'Menschen können später mehr bewirken' wird wahrer.",
    ),
    "software_automation": PurchaseTemplate(
        key="software_automation",
        label="Software / Automatisierung",
        sector="software",
        demand_weight=0.040,
        base_price=110.0,
        truth_profile=TruthStack({
            Layer.CAUSAL.value: 1.20,
            Layer.POTENTIAL.value: 0.90,
            Layer.ATTENTION.value: 0.50,
            Layer.TEMPORAL.value: 0.35,
            Layer.EPISTEMIC.value: 0.35,
        }),
        description="Die Aussage 'Arbeit kann automatisiert und skaliert werden' wird wahrer.",
    ),
    "insurance": PurchaseTemplate(
        key="insurance",
        label="Versicherung / Risikoabsicherung",
        sector="insurance",
        demand_weight=0.035,
        base_price=80.0,
        truth_profile=TruthStack({
            Layer.RISK_REDUCTION.value: 1.45,
            Layer.LEGAL.value: 0.65,
            Layer.TEMPORAL.value: 0.50,
            Layer.LIQUIDITY.value: 0.35,
        }),
        description="Die Aussage 'Ein Schaden zerstört mich nicht vollständig' wird wahrer.",
    ),
    "security_service": PurchaseTemplate(
        key="security_service",
        label="Sicherheit / Schutz",
        sector="security",
        demand_weight=0.030,
        base_price=105.0,
        truth_profile=TruthStack({
            Layer.SECURITY.value: 1.40,
            Layer.RISK_REDUCTION.value: 0.80,
            Layer.CAUSAL.value: 0.35,
            Layer.SOCIAL.value: 0.25,
        }),
        description="Die Aussage 'Angriffe werden unwahrscheinlicher oder abgewehrt' wird wahrer.",
    ),
    "defense_deterrence": PurchaseTemplate(
        key="defense_deterrence",
        label="Verteidigung / Abschreckung",
        sector="defense",
        demand_weight=0.035,
        base_price=260.0,
        truth_profile=TruthStack({
            Layer.SECURITY.value: 1.80,
            Layer.RISK_REDUCTION.value: 0.70,
            Layer.CAUSAL.value: 0.80,
            Layer.LEGAL.value: 0.20,
            Layer.ECOLOGICAL.value: -0.25,
        }),
        description="Die Aussage 'Wir können uns verteidigen' wird wahrer, aber Nebenrisiken steigen.",
    ),
    "legal_certainty": PurchaseTemplate(
        key="legal_certainty",
        label="Recht / Gültigkeit",
        sector="legal",
        demand_weight=0.025,
        base_price=140.0,
        truth_profile=TruthStack({
            Layer.LEGAL.value: 1.40,
            Layer.EPISTEMIC.value: 0.45,
            Layer.SOCIAL.value: 0.35,
            Layer.RISK_REDUCTION.value: 0.30,
        }),
        description="Die Aussage 'Ein Anspruch gilt und kann durchgesetzt werden' wird wahrer.",
    ),
    "finance_liquidity": PurchaseTemplate(
        key="finance_liquidity",
        label="Finanzierung / Liquidität",
        sector="finance",
        demand_weight=0.035,
        base_price=95.0,
        truth_profile=TruthStack({
            Layer.LIQUIDITY.value: 1.30,
            Layer.LEGAL.value: 0.45,
            Layer.TEMPORAL.value: 0.55,
            Layer.SOCIAL.value: 0.30,
        }),
        description="Die Aussage 'Ich kann heute handeln und morgen ausgleichen' wird wahrer.",
    ),
    "research_option": PurchaseTemplate(
        key="research_option",
        label="Forschung / Option auf Zukunft",
        sector="research",
        demand_weight=0.030,
        base_price=160.0,
        truth_profile=TruthStack({
            Layer.POTENTIAL.value: 1.65,
            Layer.EPISTEMIC.value: 0.80,
            Layer.CAUSAL.value: 0.45,
            Layer.COMPARATIVE.value: 0.35,
        }),
        description="Die Aussage 'Eine neue Möglichkeit kann entstehen' wird wahrer.",
    ),
    "construction_infrastructure": PurchaseTemplate(
        key="construction_infrastructure",
        label="Bau / Infrastruktur",
        sector="construction",
        demand_weight=0.070,
        base_price=210.0,
        truth_profile=TruthStack({
            Layer.EXISTENCE.value: 0.75,
            Layer.INFRASTRUCTURE.value: 1.40,
            Layer.CAUSAL.value: 0.60,
            Layer.TEMPORAL.value: 0.45,
            Layer.LEGAL.value: 0.20,
        }),
        description="Die Aussage 'Ein realer Ort oder ein System funktioniert' wird wahrer.",
    ),
    "action_vacation": PurchaseTemplate(
        key="action_vacation",
        label="Actionurlaub / Intensität",
        sector="tourism",
        demand_weight=0.025,
        base_price=150.0,
        truth_profile=TruthStack({
            Layer.PERCEPTION.value: 0.85,
            Layer.MEMORY.value: 1.20,
            Layer.TEMPORAL.value: 0.45,
            Layer.COMPARATIVE.value: 0.35,
            Layer.HEALTH.value: 0.15,
            Layer.RISK_REDUCTION.value: -0.10,
        }),
        description="Die Aussage 'In kurzer Zeit passieren intensive erinnerbare Zustände' wird wahrer.",
    ),
    "beauty_status": PurchaseTemplate(
        key="beauty_status",
        label="Schönheit / Status",
        sector="luxury",
        demand_weight=0.025,
        base_price=240.0,
        truth_profile=TruthStack({
            Layer.PERCEPTION.value: 1.35,
            Layer.COMPARATIVE.value: 0.95,
            Layer.SOCIAL.value: 0.55,
            Layer.MEMORY.value: 0.20,
        }),
        description="Die Aussage 'Ich werde schöner oder höherstatus wahrgenommen' wird wahrscheinlicher.",
    ),
    "media_attention": PurchaseTemplate(
        key="media_attention",
        label="Medien / Aufmerksamkeit",
        sector="media",
        demand_weight=0.030,
        base_price=70.0,
        truth_profile=TruthStack({
            Layer.ATTENTION.value: 1.35,
            Layer.PERCEPTION.value: 0.75,
            Layer.EPISTEMIC.value: 0.20,
            Layer.SOCIAL.value: 0.35,
        }),
        description="Die Aussage 'Andere nehmen diese Botschaft wahr' wird wahrer.",
    ),
    "entertainment_memory": PurchaseTemplate(
        key="entertainment_memory",
        label="Unterhaltung / Erinnerung",
        sector="entertainment",
        demand_weight=0.025,
        base_price=55.0,
        truth_profile=TruthStack({
            Layer.PERCEPTION.value: 0.65,
            Layer.MEMORY.value: 0.75,
            Layer.ATTENTION.value: 0.45,
            Layer.SOCIAL.value: 0.20,
        }),
        description="Die Aussage 'Zeit wird erlebt, erzählt und erinnert' wird wahrer.",
    ),
    "ecological_repair": PurchaseTemplate(
        key="ecological_repair",
        label="Ökologische Reparatur",
        sector="research",
        demand_weight=0.018,
        base_price=185.0,
        truth_profile=TruthStack({
            Layer.ECOLOGICAL.value: 1.45,
            Layer.HEALTH.value: 0.35,
            Layer.RISK_REDUCTION.value: 0.55,
            Layer.POTENTIAL.value: 0.35,
        }),
        description="Die Aussage 'Die Umwelt trägt künftiges Leben besser' wird wahrer.",
    ),
}

EMPLOYEE_TIME_TEMPLATE = PurchaseTemplate(
    key="employee_time",
    label="Arbeitnehmerzeit / gerichtete Handlungsmacht",
    sector="labor",
    demand_weight=0.0,
    base_price=1.0,
    truth_profile=TruthStack({
        Layer.ATTENTION.value: 1.00,
        Layer.CAUSAL.value: 0.75,
        Layer.TEMPORAL.value: 0.80,
        Layer.LEGAL.value: 0.25,
        Layer.SOCIAL.value: 0.20,
    }),
    description="Die Aussage 'Eine Person richtet begrenzte Zeit auf dieses Ziel' wird wahrer.",
)


# ---------------------------------------------------------------------------
# Agenten
# ---------------------------------------------------------------------------


@dataclass
class Agent:
    name: str
    kind: str
    country_id: Optional[str] = None
    agent_id: str = field(default_factory=lambda: uid("agent"))
    fiat: Dict[str, float] = field(default_factory=dict)
    truth: TruthStack = field(default_factory=TruthStack)
    reputation: float = 0.55
    risk: float = 0.45

    def cash(self, currency: str) -> float:
        return self.fiat.get(currency, 0.0)

    def add_fiat(self, currency: str, amount: float) -> None:
        self.fiat[currency] = self.fiat.get(currency, 0.0) + float(amount)

    def pay_fiat(self, currency: str, amount: float) -> None:
        self.add_fiat(currency, -float(amount))

    def add_truth(self, stack: TruthStack) -> None:
        self.truth = self.truth + stack

    def pay_truth(self, stack: TruthStack) -> None:
        self.truth = self.truth - stack

    def truth_score(self) -> float:
        return self.truth.score()

    def truth_debt(self) -> float:
        return self.truth.debt_score()

    def decay_truth(self) -> None:
        self.truth = self.truth.decayed(1)


@dataclass
class Country(Agent):
    currency: str = "XXX"
    population: float = 1_000_000.0
    gdp: float = 100_000.0
    inflation: float = 0.03
    unemployment: float = 0.07
    stability: float = 0.65
    infrastructure: float = 0.55
    health_index: float = 0.65
    education_index: float = 0.55
    tech_level: float = 0.50
    environment: float = 0.60
    resource_index: float = 0.50
    trade_openness: float = 0.55
    tax_rate: float = 0.22
    policy_rate: float = 0.035
    public_debt: float = 0.0
    sanction_level: float = 0.0
    conflict_fatigue: float = 0.0
    central_bank_id: str = ""
    bank_ids: List[str] = field(default_factory=list)
    company_ids: List[str] = field(default_factory=list)
    military_capacity: float = 0.50
    resilience: float = 0.50

    def development_score(self) -> float:
        return clamp(
            0.18 * self.stability
            + 0.15 * self.infrastructure
            + 0.15 * self.health_index
            + 0.14 * self.education_index
            + 0.12 * self.tech_level
            + 0.10 * self.environment
            + 0.10 * self.trade_openness
            + 0.06 * (1.0 - self.unemployment),
            0.0,
            1.0,
        )


@dataclass
class CentralBank(Agent):
    currency: str = "XXX"
    inflation_target: float = 0.025
    policy_rate: float = 0.035
    credibility: float = 0.65
    reserves_truth: TruthStack = field(default_factory=TruthStack)
    reserves_fx: Dict[str, float] = field(default_factory=dict)
    money_supply: float = 1_000_000.0


@dataclass
class Bank(Agent):
    currency: str = "XXX"
    deposits: float = 0.0
    loans: float = 0.0
    reserves: float = 0.0
    equity: float = 0.0
    risk_appetite: float = 0.55
    nonperforming_loans: float = 0.0

    def capital_ratio(self) -> float:
        return safe_div(self.equity, max(self.loans, 1.0), default=0.0)


@dataclass
class Company(Agent):
    currency: str = "XXX"
    sector: str = "food"
    employees: float = 100.0
    wage: float = 3.0
    productivity: float = 1.0
    capital: float = 1_000.0
    inventory: float = 0.0
    price: float = 50.0
    product_quality: float = 0.65
    export_orientation: float = 0.45
    fraud_tendency: float = 0.03
    monthly_revenue: float = 0.0
    monthly_cost: float = 0.0
    cumulative_profit: float = 0.0
    fiat_debt: float = 0.0
    last_output: float = 0.0

    def reset_month(self) -> None:
        self.monthly_revenue = 0.0
        self.monthly_cost = 0.0
        self.last_output = 0.0


@dataclass
class UNInstitution(Agent):
    legitimacy: float = 0.62
    audit_strength: float = 0.55
    peacekeeping_capacity: float = 0.50
    humanitarian_pool: TruthStack = field(default_factory=TruthStack)
    resolutions_passed: int = 0
    sanctions_issued: int = 0


@dataclass
class DefenseOrganization:
    name: str
    member_ids: List[str]
    doctrine: str
    organization_id: str = field(default_factory=lambda: uid("deforg"))
    readiness: float = 0.55
    cohesion: float = 0.55
    deterrence: float = 0.55
    truth: TruthStack = field(default_factory=TruthStack)
    budgets: Dict[str, float] = field(default_factory=dict)


# ---------------------------------------------------------------------------
# Ansprüche, Transaktionen, Ledger
# ---------------------------------------------------------------------------


@dataclass
class ClaimInstrument:
    issuer_id: str
    holder_id: Optional[str]
    stack: TruthStack
    issued_month: int
    maturity_month: int
    backing_ratio: float
    description: str
    claim_id: str = field(default_factory=lambda: uid("claim"))
    fraudulent: bool = False
    detected: bool = False

    def age(self, month: int) -> int:
        return max(0, month - self.issued_month)

    def exposed_score(self) -> float:
        return self.stack.positive_score() * max(0.0, 1.0 - self.backing_ratio)


@dataclass
class Transaction:
    month: int
    kind: str
    buyer_id: str
    seller_id: str
    currency: str
    fiat_amount: float
    truth_score: float
    truth_layers: Dict[str, float]
    description: str


@dataclass
class TruthLedger:
    weights: Dict[str, float] = field(default_factory=lambda: dict(DEFAULT_LAYER_WEIGHTS))
    claims: List[ClaimInstrument] = field(default_factory=list)
    certified_events: int = 0
    transfers: int = 0
    frauds_detected: int = 0

    def transfer(self, payer: Agent, receiver: Agent, stack: TruthStack) -> None:
        """Überträgt WK. Negative Kontostände sind möglich und sind Wahrheitsschulden."""
        payer.pay_truth(stack)
        receiver.add_truth(stack)
        self.transfers += 1

    def certify(self, agent: Agent, stack: TruthStack, month: int, description: str) -> ClaimInstrument:
        """Mintet/validiert WK durch reale, auditierbare Verbesserung."""
        agent.add_truth(stack)
        claim = ClaimInstrument(
            issuer_id=agent.agent_id,
            holder_id=agent.agent_id,
            stack=stack,
            issued_month=month,
            maturity_month=month + 36,
            backing_ratio=1.0,
            description=description,
            fraudulent=False,
        )
        self.claims.append(claim)
        self.certified_events += 1
        return claim

    def issue_unbacked_claim(
        self,
        issuer: Agent,
        stack: TruthStack,
        month: int,
        backing_ratio: float,
        description: str,
    ) -> ClaimInstrument:
        """Erzeugt einen fragilen oder betrügerischen Wahrheitsanspruch."""
        issuer.add_truth(stack.scaled(backing_ratio))
        claim = ClaimInstrument(
            issuer_id=issuer.agent_id,
            holder_id=issuer.agent_id,
            stack=stack,
            issued_month=month,
            maturity_month=month + 12,
            backing_ratio=clamp(backing_ratio, 0.0, 1.0),
            description=description,
            fraudulent=True,
        )
        self.claims.append(claim)
        return claim

    def audit_claims(
        self,
        agents: Dict[str, Agent],
        rng: random.Random,
        month: int,
        audit_strength: float,
        max_audits: int,
    ) -> List[str]:
        findings: List[str] = []
        open_claims = [c for c in self.claims if not c.detected]
        rng.shuffle(open_claims)
        for claim in open_claims[:max_audits]:
            issuer = agents.get(claim.issuer_id)
            if issuer is None:
                continue
            age_factor = clamp(claim.age(month) / 24.0, 0.05, 1.50)
            reputation_factor = 1.25 - clamp(issuer.reputation, 0.05, 0.95)
            detect_prob = clamp(audit_strength * age_factor * reputation_factor, 0.01, 0.92)
            if claim.fraudulent and rng.random() < detect_prob:
                claim.detected = True
                exposed = claim.stack.scaled(1.0 - claim.backing_ratio)
                penalty = TruthStack({
                    Layer.EPISTEMIC.value: exposed.positive_score(self.weights) * 0.25,
                    Layer.LEGAL.value: exposed.positive_score(self.weights) * 0.18,
                    Layer.SOCIAL.value: exposed.positive_score(self.weights) * 0.15,
                })
                # Entferne Scheindeckung und buche zusätzlich Wahrheits-Schuld.
                issuer.pay_truth(exposed)
                issuer.pay_truth(penalty)
                issuer.reputation = clamp(issuer.reputation - 0.06 - 0.08 * (1.0 - claim.backing_ratio), 0.01, 0.99)
                issuer.risk = clamp(issuer.risk + 0.05 + 0.10 * (1.0 - claim.backing_ratio), 0.0, 1.0)
                self.frauds_detected += 1
                findings.append(
                    f"Betrug entdeckt bei {issuer.name}: {claim.description}, "
                    f"offene WK-Schuld {exposed.debt_score(self.weights) + exposed.positive_score(self.weights):.2f}"
                )
            elif not claim.fraudulent and rng.random() < audit_strength * 0.08:
                # Gute Audits erhöhen epistemische Sicherheit.
                issuer.add_truth(TruthStack({Layer.EPISTEMIC.value: claim.stack.positive_score(self.weights) * 0.02}))
                issuer.reputation = clamp(issuer.reputation + 0.005, 0.01, 0.99)
        return findings


# ---------------------------------------------------------------------------
# Planet und Simulationslogik
# ---------------------------------------------------------------------------


@dataclass
class Planet:
    seed: int
    rng: random.Random
    countries: Dict[str, Country]
    central_banks: Dict[str, CentralBank]
    banks: Dict[str, Bank]
    companies: Dict[str, Company]
    un: UNInstitution
    defense_orgs: List[DefenseOrganization]
    ledger: TruthLedger
    fiat_per_wk: Dict[str, float]
    month: int = 0
    transactions: List[Transaction] = field(default_factory=list)
    events: List[Dict[str, Any]] = field(default_factory=list)
    history: List[Dict[str, Any]] = field(default_factory=list)
    monthly_stats: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self._rebuild_indexes()
        self.reset_monthly_stats()

    def _rebuild_indexes(self) -> None:
        self.companies_by_sector: Dict[str, List[Company]] = {sector: [] for sector in SECTORS}
        for company in self.companies.values():
            self.companies_by_sector.setdefault(company.sector, []).append(company)

    def reset_monthly_stats(self) -> None:
        self.monthly_stats = {
            "fiat_trade_wk": 0.0,
            "truth_trade_score": 0.0,
            "conflicts": 0.0,
            "frauds_detected": 0.0,
            "shocks": 0.0,
            "loans_wk": 0.0,
            "un_interventions": 0.0,
        }

    # ------------------------- Zugriff und Umrechnung ----------------------

    def all_agents(self) -> Dict[str, Agent]:
        agents: Dict[str, Agent] = {}
        agents.update(self.countries)
        agents.update(self.central_banks)
        agents.update(self.banks)
        agents.update(self.companies)
        agents[self.un.agent_id] = self.un
        return agents

    def country(self, country_id: str) -> Country:
        return self.countries[country_id]

    def local_currency(self, agent: Agent) -> str:
        if isinstance(agent, Country):
            return agent.currency
        if getattr(agent, "currency", None):
            return getattr(agent, "currency")
        if agent.country_id and agent.country_id in self.countries:
            return self.countries[agent.country_id].currency
        return next(iter(self.fiat_per_wk))

    def convert_fiat(self, amount: float, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return amount
        wk_value = amount / max(self.fiat_per_wk.get(from_currency, 100.0), 1e-9)
        return wk_value * max(self.fiat_per_wk.get(to_currency, 100.0), 1e-9)

    def fiat_to_wk(self, amount: float, currency: str) -> float:
        return amount / max(self.fiat_per_wk.get(currency, 100.0), 1e-9)

    # ------------------------- Kern: Kauf als Wahrheitsübergang ------------

    def execute_purchase(
        self,
        buyer: Agent,
        seller: Agent,
        template: PurchaseTemplate,
        quantity: float,
        seller_currency: str,
        description_suffix: str = "",
    ) -> Optional[Transaction]:
        if quantity <= 0:
            return None
        buyer_currency = self.local_currency(buyer)
        unit_price = getattr(seller, "price", template.base_price)
        fiat_amount_seller = unit_price * quantity
        fiat_amount_buyer = self.convert_fiat(fiat_amount_seller, seller_currency, buyer_currency)

        buyer.pay_fiat(buyer_currency, fiat_amount_buyer)
        seller.add_fiat(seller_currency, fiat_amount_seller)
        if isinstance(seller, Company):
            seller.inventory = max(0.0, seller.inventory - quantity)
            seller.monthly_revenue += fiat_amount_seller

        quality = clamp(getattr(seller, "product_quality", seller.reputation), 0.05, 1.50)
        trust_multiplier = 0.7 + 0.6 * clamp(seller.reputation, 0.01, 0.99)
        product_stack = template.truth_profile.scaled(quantity * 0.020 * quality * trust_multiplier)

        # Planetare Wahrheitswährung: Eine Transaktion enthält eine WK-Komponente.
        # Der Käufer zahlt WK; der Verkäufer bekommt WK; der Käufer erhält zusätzlich
        # die Realitätswirkung des Produkts / der Leistung.
        truth_payment = product_stack.scaled(0.10)
        self.ledger.transfer(buyer, seller, truth_payment)
        buyer.add_truth(product_stack.scaled(0.62))

        # Wenn der Verkäufer real liefert, wird etwas WK zertifiziert.
        # Bei Betrug entsteht ein fragiler Wahrheitsstapel, der später platzen kann.
        fraud_prob = clamp(getattr(seller, "fraud_tendency", 0.02) * (1.15 - seller.reputation), 0.0, 0.55)
        if self.rng.random() < fraud_prob:
            backing = self.rng.uniform(0.10, 0.65)
            self.ledger.issue_unbacked_claim(
                issuer=seller,
                stack=product_stack.scaled(self.rng.uniform(0.25, 0.90)),
                month=self.month,
                backing_ratio=backing,
                description=f"Übertriebene Liefer-/Qualitätswahrheit: {template.label}",
            )
        else:
            self.ledger.certify(
                agent=seller,
                stack=product_stack.scaled(0.18),
                month=self.month,
                description=f"Zertifizierte Realitätsänderung: {template.label}",
            )
            seller.reputation = clamp(seller.reputation + 0.0015 * quality, 0.01, 0.99)

        if isinstance(buyer, Country):
            self.apply_truth_to_country(buyer, product_stack)

        truth_score = product_stack.score()
        self.monthly_stats["fiat_trade_wk"] += self.fiat_to_wk(fiat_amount_buyer, buyer_currency)
        self.monthly_stats["truth_trade_score"] += truth_score

        tx = Transaction(
            month=self.month,
            kind=template.key,
            buyer_id=buyer.agent_id,
            seller_id=seller.agent_id,
            currency=seller_currency,
            fiat_amount=fiat_amount_seller,
            truth_score=truth_score,
            truth_layers=product_stack.as_dict(),
            description=f"{buyer.name} kauft {template.label} von {seller.name}. {description_suffix}".strip(),
        )
        self.transactions.append(tx)
        return tx

    def apply_truth_to_country(self, country: Country, stack: TruthStack) -> None:
        scale = 0.00010
        country.infrastructure = clamp(country.infrastructure + stack.get(Layer.INFRASTRUCTURE) * scale, 0.0, 1.4)
        country.health_index = clamp(country.health_index + stack.get(Layer.HEALTH) * scale, 0.0, 1.4)
        country.education_index = clamp(country.education_index + stack.get(Layer.EPISTEMIC) * scale * 0.8 + stack.get(Layer.POTENTIAL) * scale * 0.5, 0.0, 1.4)
        country.tech_level = clamp(country.tech_level + stack.get(Layer.POTENTIAL) * scale * 0.8 + stack.get(Layer.CAUSAL) * scale * 0.3, 0.0, 1.4)
        country.environment = clamp(country.environment + stack.get(Layer.ECOLOGICAL) * scale * 1.2, 0.0, 1.4)
        country.resilience = clamp(country.resilience + stack.get(Layer.RISK_REDUCTION) * scale + stack.get(Layer.SECURITY) * scale * 0.7, 0.0, 1.4)
        country.stability = clamp(
            country.stability
            + (stack.get(Layer.LEGAL) + stack.get(Layer.SOCIAL) + stack.get(Layer.SECURITY)) * scale * 0.35
            - max(0.0, -stack.get(Layer.RISK_REDUCTION)) * scale * 0.5,
            0.0,
            1.4,
        )
        country.military_capacity = clamp(country.military_capacity + stack.get(Layer.SECURITY) * scale * 0.5, 0.0, 1.5)

    # ------------------------- Monatsphasen --------------------------------

    def run(self, months: int, verbose: bool = False) -> None:
        for _ in range(months):
            self.run_month()
            if verbose and (self.month == 1 or self.month % 12 == 0):
                print(self.short_status())

    def run_month(self) -> None:
        self.month += 1
        self.reset_monthly_stats()
        for company in self.companies.values():
            company.reset_month()

        self.decay_all_truth()
        self.central_bank_phase()
        self.institution_phase()
        self.credit_phase()
        self.labor_and_production_phase()
        self.trade_phase()
        self.public_finance_phase()
        self.audit_phase()
        self.geopolitics_phase()
        self.random_shock_phase()
        self.macro_update_phase()
        self.record_history()

    def decay_all_truth(self) -> None:
        for agent in self.all_agents().values():
            agent.decay_truth()
        for org in self.defense_orgs:
            org.truth = org.truth.decayed(1)

    def central_bank_phase(self) -> None:
        for country in self.countries.values():
            cb = self.central_banks[country.central_bank_id]
            inflation_gap = country.inflation - cb.inflation_target
            unemployment_gap = country.unemployment - 0.055
            cb.policy_rate = clamp(cb.policy_rate + 0.20 * inflation_gap - 0.05 * unemployment_gap, 0.0, 0.30)
            cb.credibility = clamp(cb.credibility - abs(inflation_gap) * 0.015 + 0.002 * country.stability, 0.05, 0.98)
            country.policy_rate = cb.policy_rate

            # Liquidity backstop: Zentralbank rettet Banken, aber nimmt dafür Wahrheitspfand.
            local_banks = [self.banks[bid] for bid in country.bank_ids if bid in self.banks]
            for bank in local_banks:
                if bank.reserves < 0.02 * max(bank.deposits, 1.0):
                    liquidity = 0.04 * max(bank.deposits, country.gdp / 12.0)
                    bank.add_fiat(country.currency, liquidity)
                    bank.reserves += liquidity
                    cb.money_supply += liquidity
                    pledge_score = self.fiat_to_wk(liquidity, country.currency)
                    pledge = TruthStack({
                        Layer.LEGAL.value: pledge_score * 0.45,
                        Layer.LIQUIDITY.value: pledge_score * 0.60,
                        Layer.TEMPORAL.value: pledge_score * 0.35,
                    })
                    bank.pay_truth(pledge)
                    cb.add_truth(pledge.scaled(0.75))

    def institution_phase(self) -> None:
        # UN-Beiträge und globale Standards.
        for country in self.countries.values():
            due = country.gdp / 12.0 * 0.00055 * (0.6 + country.development_score())
            country.pay_fiat(country.currency, due)
            self.un.add_fiat(country.currency, due)
            wk_due = self.fiat_to_wk(due, country.currency)
            dues_stack = TruthStack({
                Layer.LEGAL.value: wk_due * 0.25,
                Layer.SOCIAL.value: wk_due * 0.20,
                Layer.ETHICAL.value: wk_due * 0.35,
                Layer.EPISTEMIC.value: wk_due * 0.15,
            })
            self.ledger.transfer(country, self.un, dues_stack)
            self.un.humanitarian_pool = self.un.humanitarian_pool + dues_stack.scaled(0.40)

        self.un.legitimacy = clamp(
            self.un.legitimacy
            + 0.0005 * mean_or((c.stability for c in self.countries.values()), 0.6)
            - 0.0003 * mean_or((c.sanction_level for c in self.countries.values()), 0.0),
            0.05,
            0.98,
        )
        self.un.audit_strength = clamp(self.un.audit_strength + 0.0008 * self.un.truth.positive_score() / 10_000.0, 0.05, 0.95)

        # Verteidigungsorganisationen erzeugen Sicherheitswahrheit, kosten aber Ressourcen.
        for org in self.defense_orgs:
            paid_members = 0
            for cid in org.member_ids:
                country = self.countries.get(cid)
                if country is None:
                    continue
                due = country.gdp / 12.0 * 0.0012 * (0.7 + country.military_capacity)
                country.pay_fiat(country.currency, due)
                org.budgets[country.currency] = org.budgets.get(country.currency, 0.0) + due
                wk_due = self.fiat_to_wk(due, country.currency)
                security_stack = TruthStack({
                    Layer.SECURITY.value: wk_due * 0.45 * org.cohesion,
                    Layer.RISK_REDUCTION.value: wk_due * 0.30 * org.deterrence,
                    Layer.LEGAL.value: wk_due * 0.10,
                    Layer.SOCIAL.value: wk_due * 0.08,
                })
                country.add_truth(security_stack.scaled(0.45))
                org.truth = org.truth + security_stack.scaled(0.30)
                country.resilience = clamp(country.resilience + security_stack.score() * 0.00002, 0.0, 1.4)
                paid_members += 1
            if paid_members:
                avg_budget_wk = sum(self.fiat_to_wk(v, cur) for cur, v in org.budgets.items()) / max(1, paid_members)
                org.readiness = clamp(org.readiness + 0.00002 * avg_budget_wk - 0.002, 0.05, 0.98)
                org.deterrence = clamp(0.55 * org.deterrence + 0.45 * (0.5 * org.readiness + 0.5 * org.cohesion), 0.05, 0.98)

    def credit_phase(self) -> None:
        companies = list(self.companies.values())
        for bank in self.banks.values():
            country = self.countries[bank.country_id]
            if not companies:
                continue
            local = [c for c in companies if c.country_id == bank.country_id]
            if not local:
                continue
            loan_attempts = 1 + int(self.rng.random() < bank.risk_appetite)
            for _ in range(loan_attempts):
                borrower = weighted_choice(
                    self.rng,
                    local,
                    lambda c: max(0.01, c.product_quality * c.reputation * (1.2 - c.risk))
                    * (1.0 + 0.3 * c.export_orientation),
                )
                if borrower is None:
                    continue
                demand = max(0.0, borrower.monthly_cost - borrower.cash(borrower.currency))
                base = country.gdp / 12.0 * self.rng.uniform(0.00008, 0.00070)
                amount = max(base, demand * self.rng.uniform(0.15, 0.50))
                if self.rng.random() > bank.risk_appetite * (1.05 - borrower.risk):
                    continue
                self.make_loan(bank, borrower, amount, borrower.currency, "Unternehmensfinanzierung")

    def make_loan(self, bank: Bank, borrower: Agent, amount: float, currency: str, purpose: str) -> None:
        borrower.add_fiat(currency, amount)
        bank.loans += amount
        bank.deposits += amount * 0.82
        bank.reserves -= amount * 0.04
        bank.equity += amount * 0.006
        if hasattr(borrower, "fiat_debt"):
            borrower.fiat_debt += amount
        wk = self.fiat_to_wk(amount, currency)
        claim = TruthStack({
            Layer.LEGAL.value: wk * 0.75,
            Layer.TEMPORAL.value: wk * 0.70,
            Layer.SOCIAL.value: wk * 0.25,
            Layer.LIQUIDITY.value: wk * 0.18,
        })
        borrower.pay_truth(claim)
        bank.add_truth(claim.scaled(0.80))
        self.monthly_stats["loans_wk"] += wk
        self.transactions.append(Transaction(
            month=self.month,
            kind="bank_credit",
            buyer_id=borrower.agent_id,
            seller_id=bank.agent_id,
            currency=currency,
            fiat_amount=amount,
            truth_score=-claim.score(),
            truth_layers=claim.scaled(-1.0).as_dict(),
            description=f"{borrower.name} nimmt Kredit bei {bank.name}: {purpose}",
        ))

    def labor_and_production_phase(self) -> None:
        for company in self.companies.values():
            country = self.countries[company.country_id]
            currency = company.currency

            # Arbeitnehmerzeit kaufen: Unternehmen zahlt Lohn und bekommt gerichtete Handlungsmacht.
            wage_bill = company.employees * company.wage * (1.0 + country.inflation / 12.0)
            company.pay_fiat(currency, wage_bill)
            country.add_fiat(currency, wage_bill * 0.88)
            company.monthly_cost += wage_bill

            work_stack = EMPLOYEE_TIME_TEMPLATE.truth_profile.scaled(company.employees * 0.006)
            company.add_truth(work_stack.scaled(0.55))
            self.ledger.transfer(company, country, work_stack.scaled(0.035))
            self.apply_truth_to_country(country, TruthStack({Layer.SOCIAL.value: company.employees * 0.0012}))

            # Produktion ist gerichtete Kausalität plus Kapital plus Landesbedingungen.
            infra_factor = 0.55 + country.infrastructure * 0.75
            stability_factor = 0.60 + country.stability * 0.55
            tech_factor = 0.75 + country.tech_level * 0.55
            sector_noise = self.rng.lognormvariate(0.0, 0.08)
            output = (
                company.employees
                * company.productivity
                * math.pow(max(company.capital, 1.0), 0.18)
                * infra_factor
                * stability_factor
                * tech_factor
                * sector_noise
                * 0.065
            )
            if country.sanction_level > 0 and company.export_orientation > 0.5:
                output *= max(0.20, 1.0 - 0.45 * country.sanction_level)
            company.inventory += output
            company.last_output = output
            company.capital *= 0.997
            company.capital += max(0.0, company.monthly_revenue - company.monthly_cost) * 0.04

            # Sektoreffekte und ökologische Kosten.
            if company.sector in {"energy", "mining", "defense", "construction"}:
                country.environment = clamp(country.environment - output * 0.0000025, 0.0, 1.4)
            if company.sector in {"research", "software", "education"}:
                country.tech_level = clamp(country.tech_level + output * 0.0000015, 0.0, 1.4)

    def choose_supplier(self, buyer_country: Country, sector: str) -> Optional[Company]:
        candidates = [c for c in self.companies_by_sector.get(sector, []) if c.inventory > 0.01]
        if not candidates:
            return None
        # Für große Welten nur eine Stichprobe prüfen.
        if len(candidates) > 60:
            candidates = self.rng.sample(candidates, 60)

        def supplier_weight(c: Company) -> float:
            seller_country = self.countries[c.country_id]
            home_bonus = 1.45 if c.country_id == buyer_country.agent_id else buyer_country.trade_openness * c.export_orientation
            sanction_penalty = max(0.05, 1.0 - 0.75 * max(buyer_country.sanction_level, seller_country.sanction_level))
            fx_penalty = 1.0 / (1.0 + abs(math.log(max(self.fiat_per_wk[buyer_country.currency], 1e-9) / max(self.fiat_per_wk[c.currency], 1e-9))))
            quality = 0.2 + c.product_quality + 0.5 * c.reputation
            return max(0.001, home_bonus * sanction_penalty * fx_penalty * quality / max(c.price, 1.0))

        return weighted_choice(self.rng, candidates, supplier_weight)

    def trade_phase(self) -> None:
        templates = list(PURCHASE_TEMPLATES.values())
        for country in self.countries.values():
            development = country.development_score()
            demand_multiplier = (0.65 + 0.70 * development) * (1.0 - 0.30 * country.sanction_level)
            # Reichere Länder kaufen mehr Wahrnehmung/Status/Optionen, ärmere relativ mehr Basisgüter.
            for template in templates:
                sector = template.sector
                supplier = self.choose_supplier(country, sector)
                if supplier is None:
                    continue
                luxury_factor = 1.0
                if sector in {"luxury", "tourism", "entertainment", "media"}:
                    luxury_factor = 0.45 + 1.25 * development
                if sector in {"food", "housing", "energy", "health"}:
                    luxury_factor = 1.15 - 0.30 * development
                monthly_budget_local = (
                    country.gdp
                    / 12.0
                    * template.demand_weight
                    * demand_multiplier
                    * luxury_factor
                    * self.rng.uniform(0.55, 1.25)
                )
                supplier_currency = supplier.currency
                budget_supplier_currency = self.convert_fiat(monthly_budget_local, country.currency, supplier_currency)
                quantity = min(supplier.inventory, budget_supplier_currency / max(supplier.price, 1.0))
                if quantity <= 0.01:
                    continue
                self.execute_purchase(
                    buyer=country,
                    seller=supplier,
                    template=template,
                    quantity=quantity,
                    seller_currency=supplier_currency,
                )

    def public_finance_phase(self) -> None:
        for country in self.countries.values():
            currency = country.currency
            firms = [self.companies[cid] for cid in country.company_ids if cid in self.companies]
            taxable_profit = 0.0
            for company in firms:
                interest = company.fiat_debt * (country.policy_rate + 0.035) / 12.0
                if interest > 0:
                    company.pay_fiat(currency, interest)
                    company.monthly_cost += interest
                    # Zinszahlungen gehen an lokale Banken.
                    if country.bank_ids:
                        bank = self.banks[self.rng.choice(country.bank_ids)]
                        bank.add_fiat(currency, interest)
                        bank.equity += interest * 0.10
                profit = company.monthly_revenue - company.monthly_cost
                company.cumulative_profit += profit
                if profit > 0:
                    tax = profit * country.tax_rate
                    company.pay_fiat(currency, tax)
                    country.add_fiat(currency, tax)
                    taxable_profit += profit

            public_spending = country.gdp / 12.0 * (0.012 + 0.025 * (1.0 - country.infrastructure) + 0.010 * (1.0 - country.health_index))
            country.pay_fiat(currency, public_spending)
            public_stack = TruthStack({
                Layer.INFRASTRUCTURE.value: self.fiat_to_wk(public_spending, currency) * 0.25,
                Layer.HEALTH.value: self.fiat_to_wk(public_spending, currency) * 0.12,
                Layer.LEGAL.value: self.fiat_to_wk(public_spending, currency) * 0.06,
                Layer.SOCIAL.value: self.fiat_to_wk(public_spending, currency) * 0.08,
            })
            country.add_truth(public_stack.scaled(0.50))
            self.apply_truth_to_country(country, public_stack)

            # Defizitfinanzierung: heutige Wirklichkeit gegen Zukunftsschuld.
            if country.cash(currency) < -0.06 * country.gdp:
                cb = self.central_banks[country.central_bank_id]
                bailout = abs(country.cash(currency)) * 0.30
                country.add_fiat(currency, bailout)
                cb.money_supply += bailout
                country.public_debt += bailout
                wk = self.fiat_to_wk(bailout, currency)
                debt_stack = TruthStack({
                    Layer.LEGAL.value: wk * 0.70,
                    Layer.TEMPORAL.value: wk * 0.90,
                    Layer.SOCIAL.value: wk * 0.25,
                    Layer.LIQUIDITY.value: wk * 0.15,
                })
                country.pay_truth(debt_stack)
                cb.add_truth(debt_stack.scaled(0.60))

    def audit_phase(self) -> None:
        agents = self.all_agents()
        max_audits = max(5, int(len(agents) * (0.012 + self.un.audit_strength * 0.018)))
        findings = self.ledger.audit_claims(
            agents=agents,
            rng=self.rng,
            month=self.month,
            audit_strength=self.un.audit_strength,
            max_audits=max_audits,
        )
        if findings:
            self.monthly_stats["frauds_detected"] += len(findings)
            for text in findings[:8]:
                self.events.append({"month": self.month, "type": "audit", "description": text})

    def geopolitics_phase(self) -> None:
        country_list = list(self.countries.values())
        if len(country_list) < 2:
            return
        pair_checks = min(8, max(1, len(country_list) // 2))
        for _ in range(pair_checks):
            a, b = self.rng.sample(country_list, 2)
            shared_defense = any(a.agent_id in org.member_ids and b.agent_id in org.member_ids for org in self.defense_orgs)
            resource_tension = abs(a.resource_index - b.resource_index) * 0.004
            instability = (2.0 - a.stability - b.stability) * 0.006
            sanction_tension = max(a.sanction_level, b.sanction_level) * 0.004
            base_risk = 0.0012 + resource_tension + instability + sanction_tension
            if shared_defense:
                base_risk *= 0.28
            deterrence_against = mean_or(
                (org.deterrence for org in self.defense_orgs if a.agent_id in org.member_ids or b.agent_id in org.member_ids),
                0.45,
            )
            base_risk *= 1.15 - 0.65 * deterrence_against
            if self.rng.random() < clamp(base_risk, 0.0001, 0.12):
                self.trigger_conflict(a, b)

    def trigger_conflict(self, a: Country, b: Country) -> None:
        severity = self.rng.uniform(0.06, 0.35) * (1.15 - 0.45 * self.un.legitimacy)
        involved_orgs = [org for org in self.defense_orgs if a.agent_id in org.member_ids or b.agent_id in org.member_ids]
        if involved_orgs:
            deterrence = mean_or((org.deterrence * org.cohesion for org in involved_orgs), 0.5)
            severity *= max(0.25, 1.0 - 0.55 * deterrence)
            for org in involved_orgs:
                org.readiness = clamp(org.readiness - severity * 0.15, 0.05, 0.98)
                org.cohesion = clamp(org.cohesion - severity * self.rng.uniform(0.01, 0.05), 0.05, 0.98)

        # UN kann vermitteln.
        if self.rng.random() < self.un.legitimacy * self.un.peacekeeping_capacity:
            severity *= 0.55
            self.monthly_stats["un_interventions"] += 1
            self.un.resolutions_passed += 1
            mediation_stack = TruthStack({
                Layer.LEGAL.value: 20.0 * severity,
                Layer.SOCIAL.value: 18.0 * severity,
                Layer.SECURITY.value: 12.0 * severity,
                Layer.ETHICAL.value: 15.0 * severity,
            })
            a.add_truth(mediation_stack.scaled(0.35))
            b.add_truth(mediation_stack.scaled(0.35))
            self.un.add_truth(mediation_stack.scaled(0.30))

        damage_stack = TruthStack({
            Layer.SECURITY.value: 80.0 * severity,
            Layer.INFRASTRUCTURE.value: 45.0 * severity,
            Layer.SOCIAL.value: 40.0 * severity,
            Layer.HEALTH.value: 35.0 * severity,
            Layer.LEGAL.value: 20.0 * severity,
            Layer.ECOLOGICAL.value: 18.0 * severity,
        })
        a.pay_truth(damage_stack)
        b.pay_truth(damage_stack.scaled(self.rng.uniform(0.7, 1.2)))
        for c in (a, b):
            c.stability = clamp(c.stability - severity * 0.18, 0.02, 1.4)
            c.infrastructure = clamp(c.infrastructure - severity * 0.10, 0.02, 1.4)
            c.health_index = clamp(c.health_index - severity * 0.06, 0.02, 1.4)
            c.conflict_fatigue = clamp(c.conflict_fatigue + severity, 0.0, 1.5)
            c.sanction_level = clamp(c.sanction_level + severity * self.rng.uniform(0.05, 0.18), 0.0, 1.0)
        self.monthly_stats["conflicts"] += 1
        self.events.append({
            "month": self.month,
            "type": "conflict",
            "description": f"Konflikt zwischen {a.name} und {b.name}, Schwere {severity:.3f}",
        })

    def random_shock_phase(self) -> None:
        # Nicht jeden Monat ein Schock, aber oft genug, um Vielfalt zu erzeugen.
        shock_probability = 0.18 + 0.002 * len(self.countries)
        if self.rng.random() > min(0.55, shock_probability):
            return
        self.monthly_stats["shocks"] += 1
        event_type = self.rng.choices(
            population=[
                "natural_disaster",
                "tech_breakthrough",
                "truth_bubble",
                "commodity_shock",
                "cyber_attack",
                "pandemic_wave",
                "social_movement",
                "climate_event",
                "un_standard_upgrade",
            ],
            weights=[1.3, 1.1, 0.8, 1.0, 0.8, 0.7, 0.9, 1.0, 0.5],
            k=1,
        )[0]
        handler = getattr(self, f"shock_{event_type}")
        handler()

    def shock_natural_disaster(self) -> None:
        country = self.rng.choice(list(self.countries.values()))
        severity = self.rng.uniform(0.04, 0.22) * (1.2 - 0.55 * country.resilience)
        damage = TruthStack({
            Layer.INFRASTRUCTURE.value: 90.0 * severity,
            Layer.HEALTH.value: 35.0 * severity,
            Layer.SECURITY.value: 20.0 * severity,
            Layer.ECOLOGICAL.value: 55.0 * severity,
            Layer.RISK_REDUCTION.value: 30.0 * severity,
        })
        country.pay_truth(damage)
        country.infrastructure = clamp(country.infrastructure - severity * 0.18, 0.0, 1.4)
        country.health_index = clamp(country.health_index - severity * 0.08, 0.0, 1.4)
        country.environment = clamp(country.environment - severity * 0.12, 0.0, 1.4)
        self.un.humanitarian_pool = self.un.humanitarian_pool - damage.scaled(0.08)
        self.events.append({"month": self.month, "type": "shock", "description": f"Naturkatastrophe in {country.name}, Schwere {severity:.3f}"})

    def shock_tech_breakthrough(self) -> None:
        company = self.rng.choice(list(self.companies.values()))
        country = self.countries[company.country_id]
        magnitude = self.rng.uniform(0.04, 0.20)
        company.productivity *= 1.0 + magnitude
        company.product_quality = clamp(company.product_quality + magnitude * 0.6, 0.05, 1.50)
        country.tech_level = clamp(country.tech_level + magnitude * 0.12, 0.0, 1.4)
        stack = TruthStack({
            Layer.POTENTIAL.value: 80.0 * magnitude,
            Layer.EPISTEMIC.value: 45.0 * magnitude,
            Layer.CAUSAL.value: 55.0 * magnitude,
            Layer.COMPARATIVE.value: 30.0 * magnitude,
        })
        self.ledger.certify(company, stack, self.month, "technologischer Durchbruch")
        self.events.append({"month": self.month, "type": "shock", "description": f"Technologischer Durchbruch bei {company.name} ({company.sector})"})

    def shock_truth_bubble(self) -> None:
        sector = self.rng.choice(list(SECTORS))
        firms = self.companies_by_sector.get(sector, [])
        if not firms:
            return
        hit = self.rng.sample(firms, min(len(firms), max(1, len(firms) // 5)))
        total_loss = 0.0
        for firm in hit:
            fragility = clamp(firm.fraud_tendency + firm.risk - firm.reputation * 0.3, 0.05, 0.85)
            loss = firm.truth.positive_score() * fragility * self.rng.uniform(0.02, 0.18)
            if loss <= 0:
                continue
            firm.pay_truth(TruthStack({
                Layer.EPISTEMIC.value: loss * 0.35,
                Layer.SOCIAL.value: loss * 0.25,
                Layer.LIQUIDITY.value: loss * 0.20,
                Layer.LEGAL.value: loss * 0.15,
            }))
            firm.reputation = clamp(firm.reputation - fragility * 0.035, 0.01, 0.99)
            total_loss += loss
        self.events.append({"month": self.month, "type": "shock", "description": f"Wahrheitsblase im Sektor {sector} platzt, WK-Verlust {total_loss:.1f}"})

    def shock_commodity_shock(self) -> None:
        affected = self.rng.sample(list(self.countries.values()), max(1, len(self.countries) // 4))
        shock = self.rng.uniform(0.02, 0.12)
        for country in affected:
            country.inflation = clamp(country.inflation + shock * (1.1 - country.resource_index), -0.08, 0.60)
            country.stability = clamp(country.stability - shock * 0.08, 0.0, 1.4)
        self.events.append({"month": self.month, "type": "shock", "description": f"Rohstoffschock erhöht Inflation um bis zu {shock:.2%}"})

    def shock_cyber_attack(self) -> None:
        bank = self.rng.choice(list(self.banks.values()))
        country = self.countries[bank.country_id]
        severity = self.rng.uniform(0.03, 0.20) * (1.2 - country.tech_level * 0.3)
        loss = max(bank.deposits, 1.0) * severity * 0.015
        bank.pay_fiat(bank.currency, loss)
        bank.reserves -= loss * 0.6
        bank.pay_truth(TruthStack({
            Layer.EPISTEMIC.value: 60.0 * severity,
            Layer.SECURITY.value: 50.0 * severity,
            Layer.LIQUIDITY.value: 45.0 * severity,
            Layer.SOCIAL.value: 30.0 * severity,
        }))
        bank.reputation = clamp(bank.reputation - severity * 0.10, 0.01, 0.99)
        country.stability = clamp(country.stability - severity * 0.03, 0.0, 1.4)
        self.events.append({"month": self.month, "type": "shock", "description": f"Cyberangriff auf {bank.name}, Schwere {severity:.3f}"})

    def shock_pandemic_wave(self) -> None:
        affected = self.rng.sample(list(self.countries.values()), max(1, len(self.countries) // 3))
        severity = self.rng.uniform(0.02, 0.16)
        for country in affected:
            mitigated = severity * (1.2 - country.health_index * 0.55 - country.resilience * 0.25)
            country.health_index = clamp(country.health_index - mitigated * 0.15, 0.0, 1.4)
            country.unemployment = clamp(country.unemployment + mitigated * 0.05, 0.0, 0.60)
            country.pay_truth(TruthStack({
                Layer.HEALTH.value: 75.0 * mitigated,
                Layer.RISK_REDUCTION.value: 40.0 * mitigated,
                Layer.TEMPORAL.value: 30.0 * mitigated,
            }))
        self.events.append({"month": self.month, "type": "shock", "description": f"Pandemiewelle, globale Schwere {severity:.3f}"})

    def shock_social_movement(self) -> None:
        country = self.rng.choice(list(self.countries.values()))
        direction = self.rng.choice([-1, 1])
        magnitude = self.rng.uniform(0.03, 0.14)
        if direction > 0:
            country.stability = clamp(country.stability + magnitude * 0.10, 0.0, 1.4)
            stack = TruthStack({Layer.SOCIAL.value: 55.0 * magnitude, Layer.ETHICAL.value: 45.0 * magnitude, Layer.LEGAL.value: 15.0 * magnitude})
            country.add_truth(stack)
            desc = f"Reformbewegung stärkt soziale Wahrheit in {country.name}"
        else:
            country.stability = clamp(country.stability - magnitude * 0.12, 0.0, 1.4)
            country.pay_truth(TruthStack({Layer.SOCIAL.value: 60.0 * magnitude, Layer.LEGAL.value: 35.0 * magnitude, Layer.ETHICAL.value: 25.0 * magnitude}))
            desc = f"Legitimationskrise schwächt soziale Wahrheit in {country.name}"
        self.events.append({"month": self.month, "type": "shock", "description": desc})

    def shock_climate_event(self) -> None:
        country = min(self.countries.values(), key=lambda c: c.environment + self.rng.random() * 0.2)
        severity = self.rng.uniform(0.04, 0.18) * (1.25 - country.environment * 0.35)
        country.environment = clamp(country.environment - severity * 0.18, 0.0, 1.4)
        country.infrastructure = clamp(country.infrastructure - severity * 0.08, 0.0, 1.4)
        country.pay_truth(TruthStack({Layer.ECOLOGICAL.value: 90.0 * severity, Layer.INFRASTRUCTURE.value: 35.0 * severity, Layer.HEALTH.value: 20.0 * severity}))
        self.events.append({"month": self.month, "type": "shock", "description": f"Klimaschock in {country.name}, Schwere {severity:.3f}"})

    def shock_un_standard_upgrade(self) -> None:
        magnitude = self.rng.uniform(0.02, 0.08)
        self.un.audit_strength = clamp(self.un.audit_strength + magnitude, 0.05, 0.97)
        self.un.legitimacy = clamp(self.un.legitimacy + magnitude * 0.40, 0.05, 0.98)
        stack = TruthStack({Layer.EPISTEMIC.value: 80.0 * magnitude, Layer.LEGAL.value: 50.0 * magnitude, Layer.ETHICAL.value: 35.0 * magnitude})
        self.un.add_truth(stack)
        self.events.append({"month": self.month, "type": "shock", "description": f"UN erhöht globale Prüfstandards um {magnitude:.3f}"})

    def macro_update_phase(self) -> None:
        for country in self.countries.values():
            firms = [self.companies[cid] for cid in country.company_ids if cid in self.companies]
            domestic_revenue = sum(c.monthly_revenue for c in firms)
            annualized_output = domestic_revenue * 12.0
            country.gdp = max(1_000.0, 0.965 * country.gdp + 0.035 * annualized_output)
            employed = sum(c.employees for c in firms)
            labor_force = country.population * 0.48 / 1000.0  # interne Skalierung
            employment_rate = clamp(safe_div(employed, max(labor_force, 1.0), 0.5), 0.0, 1.2)
            country.unemployment = clamp(0.90 * country.unemployment + 0.10 * max(0.0, 1.0 - employment_rate), 0.01, 0.60)

            cb = self.central_banks[country.central_bank_id]
            debt_pressure = safe_div(country.public_debt, max(country.gdp, 1.0), 0.0)
            sanction_pressure = country.sanction_level * 0.05
            money_pressure = safe_div(cb.money_supply, max(country.gdp, 1.0), 1.0) * 0.001
            output_gap = clamp(0.50 - country.unemployment, -0.40, 0.50)
            inflation_drift = (
                0.45 * country.inflation
                + 0.30 * cb.inflation_target
                + 0.10 * output_gap
                + 0.07 * debt_pressure
                + sanction_pressure
                + money_pressure
                - 0.06 * cb.credibility
            )
            country.inflation = clamp(inflation_drift + self.rng.gauss(0.0, 0.004), -0.08, 0.75)

            truth_net = country.truth.score()
            country.stability = clamp(
                0.985 * country.stability
                + 0.015 * country.development_score()
                - 0.018 * max(0.0, country.inflation - 0.08)
                - 0.012 * country.unemployment
                - 0.006 * country.sanction_level
                + 0.000004 * truth_net,
                0.01,
                1.4,
            )
            country.sanction_level = clamp(country.sanction_level * 0.985, 0.0, 1.0)
            country.conflict_fatigue = clamp(country.conflict_fatigue * 0.97, 0.0, 1.5)

            # Wechselkurs: Fiat pro WK. Höher = Fiat wird schwächer.
            fx = self.fiat_per_wk[country.currency]
            credibility = cb.credibility
            real_quality = country.development_score()
            drift = country.inflation / 12.0 + 0.004 * debt_pressure + 0.006 * country.sanction_level - 0.006 * real_quality - 0.003 * credibility
            self.fiat_per_wk[country.currency] = clamp(fx * math.exp(drift + self.rng.gauss(0.0, 0.006)), 0.1, 1_000_000.0)

            # Firmen passen Preise und Beschäftigung an.
            for company in firms:
                company.price = max(0.1, company.price * (1.0 + country.inflation / 12.0 + self.rng.gauss(0.0, 0.004)))
                profit = company.monthly_revenue - company.monthly_cost
                if profit > 0:
                    company.employees *= 1.0 + min(0.015, profit / max(company.monthly_cost + 1.0, 1.0) * 0.01)
                    company.reputation = clamp(company.reputation + 0.0008, 0.01, 0.99)
                else:
                    company.employees *= 1.0 - min(0.020, abs(profit) / max(company.monthly_cost + 1.0, 1.0) * 0.015)
                    company.risk = clamp(company.risk + 0.002, 0.0, 1.0)
                company.employees = clamp(company.employees, 3.0, 80_000.0)
                # Zu hohe WK-Schulden verschlechtern Reputation und Risiko.
                if company.truth_debt() > max(10.0, company.truth.positive_score() * 0.75):
                    company.reputation = clamp(company.reputation - 0.002, 0.01, 0.99)
                    company.risk = clamp(company.risk + 0.003, 0.0, 1.0)

    def record_history(self) -> None:
        countries = list(self.countries.values())
        companies = list(self.companies.values())
        agents = list(self.all_agents().values())
        total_truth = sum(a.truth.score() for a in agents)
        positive_truth = sum(a.truth.positive_score() for a in agents)
        debt_truth = sum(a.truth.debt_score() for a in agents)
        total_gdp = sum(c.gdp / max(self.fiat_per_wk[c.currency], 1.0) for c in countries)
        avg_inflation = mean_or(c.inflation for c in countries)
        avg_stability = mean_or(c.stability for c in countries)
        avg_unemployment = mean_or(c.unemployment for c in countries)
        avg_environment = mean_or(c.environment for c in countries)
        avg_reputation = mean_or(c.reputation for c in companies)
        self.history.append({
            "month": self.month,
            "global_gdp_wk": total_gdp,
            "total_truth_score": total_truth,
            "positive_truth_score": positive_truth,
            "truth_debt_score": debt_truth,
            "avg_inflation": avg_inflation,
            "avg_stability": avg_stability,
            "avg_unemployment": avg_unemployment,
            "avg_environment": avg_environment,
            "avg_company_reputation": avg_reputation,
            "fiat_trade_wk": self.monthly_stats["fiat_trade_wk"],
            "truth_trade_score": self.monthly_stats["truth_trade_score"],
            "loans_wk": self.monthly_stats["loans_wk"],
            "conflicts": self.monthly_stats["conflicts"],
            "frauds_detected": self.monthly_stats["frauds_detected"],
            "shocks": self.monthly_stats["shocks"],
            "un_legitimacy": self.un.legitimacy,
            "un_audit_strength": self.un.audit_strength,
        })

    # ------------------------- Ausgabe -------------------------------------

    def short_status(self) -> str:
        if not self.history:
            return "Noch keine Historie."
        row = self.history[-1]
        return (
            f"Monat {self.month:4d} | GDP(WK) {row['global_gdp_wk']:10.1f} | "
            f"Truth {row['total_truth_score']:10.1f} | Debt {row['truth_debt_score']:9.1f} | "
            f"Infl {row['avg_inflation']:.2%} | Stabilität {row['avg_stability']:.3f} | "
            f"Konflikte {int(row['conflicts'])} | Betrug {int(row['frauds_detected'])}"
        )

    def top_countries(self, n: int = 8) -> List[Country]:
        return sorted(self.countries.values(), key=lambda c: c.gdp / max(self.fiat_per_wk[c.currency], 1.0), reverse=True)[:n]

    def top_companies(self, n: int = 10) -> List[Company]:
        return sorted(self.companies.values(), key=lambda c: c.monthly_revenue + c.truth.positive_score(), reverse=True)[:n]

    def summary_text(self) -> str:
        last = self.history[-1] if self.history else {}
        top_c = self.top_countries(6)
        top_f = self.top_companies(8)
        lines = [
            "Planetare Wahrheitsoekonomie - Simulationsergebnis",
            "=" * 56,
            f"Seed: {self.seed}",
            f"Monate simuliert: {self.month}",
            f"Laender: {len(self.countries)}, Unternehmen: {len(self.companies)}, Banken: {len(self.banks)}, Verteidigungsorganisationen: {len(self.defense_orgs)}",
            f"UN-Legitimität: {self.un.legitimacy:.3f}, UN-Auditstaerke: {self.un.audit_strength:.3f}",
        ]
        if last:
            lines.extend([
                f"Globales BIP in WK-Numeraire: {last['global_gdp_wk']:.2f}",
                f"Netto-Wahrheitsscore: {last['total_truth_score']:.2f}",
                f"Positive WK: {last['positive_truth_score']:.2f}",
                f"WK-Schuld: {last['truth_debt_score']:.2f}",
                f"Durchschnittsinflation: {last['avg_inflation']:.2%}",
                f"Durchschnittsstabilität: {last['avg_stability']:.3f}",
                f"Durchschnittsumwelt: {last['avg_environment']:.3f}",
                "",
                "Top-Laender nach BIP(WK):",
            ])
            for c in top_c:
                lines.append(
                    f"  - {c.name:24s} {c.currency:4s} GDP(WK)={c.gdp / max(self.fiat_per_wk[c.currency], 1.0):9.1f} "
                    f"Stab={c.stability:.3f} Infl={c.inflation:.2%} WK={c.truth.score():.1f} Debt={c.truth_debt():.1f}"
                )
            lines.extend(["", "Top-Unternehmen:"])
            for f in top_f:
                lines.append(
                    f"  - {f.name:28s} {f.sector:14s} Umsatz={f.monthly_revenue:9.1f} "
                    f"Rep={f.reputation:.3f} WK={f.truth.score():.1f} Debt={f.truth_debt():.1f}"
                )
        recent_events = self.events[-10:]
        if recent_events:
            lines.extend(["", "Letzte Ereignisse:"])
            for e in recent_events:
                lines.append(f"  M{e['month']:04d} [{e['type']}] {e['description']}")
        return "\n".join(lines)

    def write_reports(self, out_dir: Path) -> None:
        out_dir.mkdir(parents=True, exist_ok=True)
        self.write_history(out_dir / "history.csv")
        self.write_countries(out_dir / "countries.csv")
        self.write_companies(out_dir / "companies.csv")
        self.write_banks(out_dir / "banks.csv")
        self.write_events(out_dir / "events.json")
        self.write_summary(out_dir / "summary.json")
        (out_dir / "summary.txt").write_text(self.summary_text(), encoding="utf-8")

    def write_history(self, path: Path) -> None:
        if not self.history:
            return
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(self.history[0].keys()))
            writer.writeheader()
            writer.writerows(self.history)

    def write_countries(self, path: Path) -> None:
        fields = [
            "id", "name", "currency", "population", "gdp", "gdp_wk", "fiat_per_wk", "inflation", "unemployment",
            "stability", "infrastructure", "health_index", "education_index", "tech_level", "environment", "trade_openness",
            "public_debt", "sanction_level", "truth_score", "truth_positive", "truth_debt", "top_truth_layers",
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for c in self.countries.values():
                writer.writerow({
                    "id": c.agent_id,
                    "name": c.name,
                    "currency": c.currency,
                    "population": round(c.population, 2),
                    "gdp": round(c.gdp, 4),
                    "gdp_wk": round(c.gdp / max(self.fiat_per_wk[c.currency], 1.0), 4),
                    "fiat_per_wk": round(self.fiat_per_wk[c.currency], 6),
                    "inflation": round(c.inflation, 6),
                    "unemployment": round(c.unemployment, 6),
                    "stability": round(c.stability, 6),
                    "infrastructure": round(c.infrastructure, 6),
                    "health_index": round(c.health_index, 6),
                    "education_index": round(c.education_index, 6),
                    "tech_level": round(c.tech_level, 6),
                    "environment": round(c.environment, 6),
                    "trade_openness": round(c.trade_openness, 6),
                    "public_debt": round(c.public_debt, 4),
                    "sanction_level": round(c.sanction_level, 6),
                    "truth_score": round(c.truth.score(), 4),
                    "truth_positive": round(c.truth.positive_score(), 4),
                    "truth_debt": round(c.truth_debt(), 4),
                    "top_truth_layers": c.truth.compact(8),
                })

    def write_companies(self, path: Path) -> None:
        fields = [
            "id", "name", "country", "currency", "sector", "employees", "price", "inventory", "monthly_revenue", "monthly_cost",
            "cumulative_profit", "fiat_debt", "productivity", "product_quality", "reputation", "risk", "fraud_tendency",
            "truth_score", "truth_positive", "truth_debt", "top_truth_layers",
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for c in self.companies.values():
                country = self.countries[c.country_id]
                writer.writerow({
                    "id": c.agent_id,
                    "name": c.name,
                    "country": country.name,
                    "currency": c.currency,
                    "sector": c.sector,
                    "employees": round(c.employees, 2),
                    "price": round(c.price, 4),
                    "inventory": round(c.inventory, 4),
                    "monthly_revenue": round(c.monthly_revenue, 4),
                    "monthly_cost": round(c.monthly_cost, 4),
                    "cumulative_profit": round(c.cumulative_profit, 4),
                    "fiat_debt": round(c.fiat_debt, 4),
                    "productivity": round(c.productivity, 6),
                    "product_quality": round(c.product_quality, 6),
                    "reputation": round(c.reputation, 6),
                    "risk": round(c.risk, 6),
                    "fraud_tendency": round(c.fraud_tendency, 6),
                    "truth_score": round(c.truth.score(), 4),
                    "truth_positive": round(c.truth.positive_score(), 4),
                    "truth_debt": round(c.truth_debt(), 4),
                    "top_truth_layers": c.truth.compact(8),
                })

    def write_banks(self, path: Path) -> None:
        fields = [
            "id", "name", "country", "currency", "deposits", "loans", "reserves", "equity", "capital_ratio", "risk_appetite",
            "reputation", "truth_score", "truth_positive", "truth_debt", "top_truth_layers",
        ]
        with path.open("w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fields)
            writer.writeheader()
            for b in self.banks.values():
                country = self.countries[b.country_id]
                writer.writerow({
                    "id": b.agent_id,
                    "name": b.name,
                    "country": country.name,
                    "currency": b.currency,
                    "deposits": round(b.deposits, 4),
                    "loans": round(b.loans, 4),
                    "reserves": round(b.reserves, 4),
                    "equity": round(b.equity, 4),
                    "capital_ratio": round(b.capital_ratio(), 6),
                    "risk_appetite": round(b.risk_appetite, 6),
                    "reputation": round(b.reputation, 6),
                    "truth_score": round(b.truth.score(), 4),
                    "truth_positive": round(b.truth.positive_score(), 4),
                    "truth_debt": round(b.truth_debt(), 4),
                    "top_truth_layers": b.truth.compact(8),
                })

    def write_events(self, path: Path) -> None:
        path.write_text(json.dumps(self.events, ensure_ascii=False, indent=2), encoding="utf-8")

    def write_summary(self, path: Path) -> None:
        summary = {
            "seed": self.seed,
            "months": self.month,
            "countries": len(self.countries),
            "companies": len(self.companies),
            "banks": len(self.banks),
            "defense_organizations": len(self.defense_orgs),
            "un": {
                "legitimacy": self.un.legitimacy,
                "audit_strength": self.un.audit_strength,
                "truth_score": self.un.truth.score(),
                "truth_debt": self.un.truth_debt(),
            },
            "last_history": self.history[-1] if self.history else None,
            "top_countries": [
                {
                    "name": c.name,
                    "currency": c.currency,
                    "gdp_wk": c.gdp / max(self.fiat_per_wk[c.currency], 1.0),
                    "stability": c.stability,
                    "truth_score": c.truth.score(),
                    "truth_debt": c.truth_debt(),
                }
                for c in self.top_countries(10)
            ],
            "top_companies": [
                {
                    "name": c.name,
                    "sector": c.sector,
                    "country": self.countries[c.country_id].name,
                    "monthly_revenue": c.monthly_revenue,
                    "reputation": c.reputation,
                    "truth_score": c.truth.score(),
                    "truth_debt": c.truth_debt(),
                }
                for c in self.top_companies(15)
            ],
        }
        path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")


# ---------------------------------------------------------------------------
# Weltgenerator
# ---------------------------------------------------------------------------


COUNTRY_ROOTS = [
    "Aurel", "Boreal", "Cyren", "Damar", "Eldor", "Faron", "Galen", "Helio", "Istr", "Jorvik",
    "Kael", "Lumer", "Merid", "Novar", "Orion", "Prax", "Quorin", "Rhen", "Selen", "Tavor",
    "Ulmar", "Valen", "Westr", "Xand", "Ymir", "Zerin", "Arc", "Bel", "Casp", "Drav",
    "Ephy", "Fjell", "Gond", "Hesper", "Illyr", "Karth", "Lyk", "Myr", "Ner", "Ost",
]
COUNTRY_SUFFIXES = ["ia", "land", "stan", "mark", "reich", "ora", "esia", "grad", "polis", "mere", "terra", "heim"]
COMPANY_PREFIXES = [
    "Astra", "Nova", "Terra", "Omni", "Helix", "Vector", "Atlas", "Nexus", "Quantum", "Civitas", "Sol", "Argent",
    "Blue", "Iron", "Green", "Vertex", "Prism", "Union", "Pioneer", "Cobalt", "Meridian", "Saffron", "Signal", "Kinetic",
]
COMPANY_SUFFIXES = {
    "food": ["Foods", "Harvest", "Nutrition"],
    "housing": ["Homes", "Habitat", "Residences"],
    "mobility": ["Motors", "Transit", "Mobility"],
    "energy": ["Energy", "Grid", "Power"],
    "health": ["Health", "Care", "Biomed"],
    "education": ["Academy", "Learning", "Scholars"],
    "defense": ["Defense", "Aegis", "Arms"],
    "finance": ["Capital", "Ledger", "Markets"],
    "software": ["Systems", "Softworks", "AI"],
    "tourism": ["Adventures", "Travel", "Expeditions"],
    "media": ["Media", "Broadcast", "Attention"],
    "luxury": ["Luxury", "Atelier", "Status"],
    "logistics": ["Logistics", "Freight", "Routes"],
    "construction": ["Build", "Works", "Infrastructure"],
    "research": ["Labs", "Research", "Frontier"],
    "agriculture": ["Agro", "Fields", "Seed"],
    "mining": ["Mining", "Ore", "Minerals"],
    "insurance": ["Insurance", "Mutual", "Assure"],
    "security": ["Security", "Shield", "Guard"],
    "legal": ["Legal", "Law", "Rights"],
    "entertainment": ["Entertainment", "Stories", "Culture"],
}
DEFENSE_NAMES = [
    "Northern Shield", "Maritime Accord", "Continental Compact", "Skyline Defense Union", "Aurora Pact",
    "Equatorial Security Forum", "Free Routes Coalition", "Civic Protection League", "Oceanic Deterrence Treaty",
    "Mountain Ring Alliance", "Eastern Stability Organization", "Southern Sentinel",
]
DOCTRINES = ["collective_defense", "maritime_security", "deterrence", "peace_enforcement", "infrastructure_protection", "cyber_defense"]


PRESETS: Dict[str, Dict[str, int]] = {
    "tiny": {"countries": 5, "companies": 55, "banks": 12, "defense_orgs": 3, "months": 36},
    "standard": {"countries": 12, "companies": 240, "banks": 42, "defense_orgs": 5, "months": 120},
    "large": {"countries": 32, "companies": 1_200, "banks": 160, "defense_orgs": 9, "months": 360},
    "epic": {"countries": 72, "companies": 6_000, "banks": 780, "defense_orgs": 16, "months": 720},
}


def make_currency_code(name: str, existing: set[str]) -> str:
    letters = "".join(ch for ch in name.upper() if ch.isalpha())
    base = (letters[:3] or "CUR").ljust(3, "X")
    code = base
    i = 1
    while code in existing:
        suffix = str(i)
        code = (base[: max(0, 3 - len(suffix))] + suffix).ljust(3, "X")
        i += 1
    existing.add(code)
    return code


def sector_base_quality(sector: str) -> Tuple[float, float, float]:
    # productivity, capital intensity, fraud tendency base
    table = {
        "food": (0.95, 0.9, 0.025),
        "housing": (0.75, 1.3, 0.035),
        "mobility": (0.85, 1.4, 0.030),
        "energy": (0.90, 1.8, 0.028),
        "health": (0.85, 1.2, 0.020),
        "education": (0.80, 0.8, 0.018),
        "defense": (0.78, 1.7, 0.045),
        "finance": (1.00, 0.7, 0.055),
        "software": (1.18, 0.6, 0.032),
        "tourism": (0.82, 0.9, 0.030),
        "media": (0.95, 0.5, 0.060),
        "luxury": (0.70, 1.0, 0.050),
        "logistics": (0.88, 1.3, 0.025),
        "construction": (0.80, 1.5, 0.035),
        "research": (0.75, 1.1, 0.040),
        "agriculture": (0.78, 1.0, 0.022),
        "mining": (0.72, 1.7, 0.035),
        "insurance": (0.92, 0.6, 0.045),
        "security": (0.80, 1.0, 0.035),
        "legal": (0.82, 0.45, 0.025),
        "entertainment": (0.88, 0.6, 0.045),
    }
    return table.get(sector, (0.85, 1.0, 0.03))


class PlanetFactory:
    @staticmethod
    def create(
        seed: int = 42,
        countries_n: int = 12,
        companies_n: int = 240,
        banks_n: int = 42,
        defense_orgs_n: int = 5,
    ) -> Planet:
        rng = random.Random(seed)
        countries: Dict[str, Country] = {}
        central_banks: Dict[str, CentralBank] = {}
        banks: Dict[str, Bank] = {}
        companies: Dict[str, Company] = {}
        fiat_per_wk: Dict[str, float] = {}
        used_country_names: set[str] = set()
        used_currencies: set[str] = set()

        for i in range(countries_n):
            root = COUNTRY_ROOTS[i % len(COUNTRY_ROOTS)]
            suffix = rng.choice(COUNTRY_SUFFIXES)
            name = f"{root}{suffix}"
            while name in used_country_names:
                name = f"{root}{rng.choice(COUNTRY_SUFFIXES)}{rng.randint(2, 99)}"
            used_country_names.add(name)
            currency = make_currency_code(name, used_currencies)
            population = rng.lognormvariate(math.log(18_000_000), 0.85)
            gdp_per_capita = rng.lognormvariate(math.log(22.0), 0.55)
            gdp = max(15_000.0, population / 1000.0 * gdp_per_capita)
            stability = rng.uniform(0.38, 0.86)
            infrastructure = rng.uniform(0.32, 0.88)
            health = rng.uniform(0.35, 0.90)
            education = rng.uniform(0.30, 0.88)
            tech = rng.uniform(0.25, 0.90)
            environment = rng.uniform(0.35, 0.88)
            resource = rng.uniform(0.20, 0.95)
            trade = rng.uniform(0.25, 0.90)
            inflation = rng.uniform(0.005, 0.085)
            unemployment = rng.uniform(0.025, 0.18)
            country = Country(
                name=name,
                kind="country",
                currency=currency,
                population=population,
                gdp=gdp,
                inflation=inflation,
                unemployment=unemployment,
                stability=stability,
                infrastructure=infrastructure,
                health_index=health,
                education_index=education,
                tech_level=tech,
                environment=environment,
                resource_index=resource,
                trade_openness=trade,
                tax_rate=rng.uniform(0.14, 0.36),
                policy_rate=rng.uniform(0.01, 0.08),
                public_debt=gdp * rng.uniform(0.05, 0.95),
                military_capacity=rng.uniform(0.20, 0.95),
                resilience=rng.uniform(0.25, 0.85),
                reputation=stability,
                risk=1.0 - stability,
            )
            country.country_id = country.agent_id
            country.add_fiat(currency, gdp * rng.uniform(0.02, 0.12))
            initial_truth = TruthStack({
                Layer.LEGAL.value: stability * 60.0,
                Layer.SOCIAL.value: stability * 55.0,
                Layer.INFRASTRUCTURE.value: infrastructure * 80.0,
                Layer.HEALTH.value: health * 70.0,
                Layer.EPISTEMIC.value: education * 50.0,
                Layer.POTENTIAL.value: tech * 65.0,
                Layer.ECOLOGICAL.value: environment * 55.0,
                Layer.SECURITY.value: country.military_capacity * 45.0,
            })
            country.add_truth(initial_truth)
            countries[country.agent_id] = country

            fiat_per_wk[currency] = rng.lognormvariate(math.log(110.0), 0.65)
            cb = CentralBank(
                name=f"Central Bank of {name}",
                kind="central_bank",
                country_id=country.agent_id,
                currency=currency,
                inflation_target=rng.uniform(0.015, 0.035),
                policy_rate=country.policy_rate,
                credibility=clamp(0.45 + stability * 0.45 + rng.gauss(0, 0.05), 0.05, 0.98),
                money_supply=gdp * rng.uniform(0.65, 2.50),
                reputation=stability,
                risk=1.0 - stability,
            )
            cb.add_fiat(currency, gdp * rng.uniform(0.02, 0.10))
            cb.reserves_truth = TruthStack({Layer.LIQUIDITY.value: gdp / max(fiat_per_wk[currency], 1.0) * 0.08, Layer.LEGAL.value: stability * 50.0})
            cb.add_truth(cb.reserves_truth)
            central_banks[cb.agent_id] = cb
            country.central_bank_id = cb.agent_id

        country_list = list(countries.values())
        # Banken verteilen.
        for i in range(banks_n):
            country = country_list[i % len(country_list)] if i < len(country_list) else rng.choice(country_list)
            name = f"{rng.choice(COMPANY_PREFIXES)} {country.currency} Bank {i+1}"
            deposits = country.gdp * rng.uniform(0.01, 0.12)
            loans = deposits * rng.uniform(0.45, 1.25)
            bank = Bank(
                name=name,
                kind="bank",
                country_id=country.agent_id,
                currency=country.currency,
                deposits=deposits,
                loans=loans,
                reserves=deposits * rng.uniform(0.03, 0.18),
                equity=max(1.0, loans * rng.uniform(0.04, 0.16)),
                risk_appetite=rng.uniform(0.22, 0.84),
                reputation=clamp(0.35 + country.stability * 0.45 + rng.gauss(0, 0.08), 0.03, 0.96),
                risk=rng.uniform(0.15, 0.75),
            )
            bank.add_fiat(country.currency, bank.reserves)
            wk = loans / max(fiat_per_wk[country.currency], 1.0)
            bank.add_truth(TruthStack({Layer.LEGAL.value: wk * 0.22, Layer.LIQUIDITY.value: wk * 0.18, Layer.TEMPORAL.value: wk * 0.12}))
            banks[bank.agent_id] = bank
            country.bank_ids.append(bank.agent_id)

        # Unternehmen: Sektorverteilung breit, aber Basisgüter stärker.
        sector_weights = {
            "food": 1.2, "housing": 1.0, "mobility": 0.9, "energy": 0.8, "health": 0.9,
            "education": 0.7, "defense": 0.45, "finance": 0.65, "software": 0.75, "tourism": 0.65,
            "media": 0.55, "luxury": 0.48, "logistics": 0.75, "construction": 0.90, "research": 0.52,
            "agriculture": 0.85, "mining": 0.45, "insurance": 0.50, "security": 0.55, "legal": 0.50,
            "entertainment": 0.55,
        }
        sector_population = list(sector_weights.keys())
        sector_probs = [sector_weights[s] for s in sector_population]
        for i in range(companies_n):
            country = weighted_choice(rng, country_list, lambda c: max(0.01, c.gdp) * (0.4 + c.stability))
            sector = rng.choices(sector_population, weights=sector_probs, k=1)[0]
            prefix = rng.choice(COMPANY_PREFIXES)
            suffix = rng.choice(COMPANY_SUFFIXES.get(sector, ["Corp"]))
            name = f"{prefix} {suffix} {i+1}"
            prod_base, cap_intensity, fraud_base = sector_base_quality(sector)
            employees = rng.lognormvariate(math.log(280.0), 0.95)
            employees = clamp(employees, 8.0, 25_000.0)
            productivity = prod_base * rng.lognormvariate(0.0, 0.22) * (0.75 + country.tech_level * 0.55)
            capital = employees * rng.uniform(20.0, 140.0) * cap_intensity
            base_price = mean_or((t.base_price for t in PURCHASE_TEMPLATES.values() if t.sector == sector), 80.0)
            price = base_price * rng.lognormvariate(0.0, 0.28) * (0.65 + fiat_per_wk[country.currency] / 120.0 * 0.35)
            quality = clamp(rng.uniform(0.35, 0.92) * (0.75 + country.tech_level * 0.45), 0.05, 1.50)
            reputation = clamp(0.30 + country.stability * 0.45 + quality * 0.25 + rng.gauss(0, 0.06), 0.03, 0.98)
            fraud = clamp(fraud_base * rng.lognormvariate(0.0, 0.55) * (1.15 - country.stability * 0.45), 0.001, 0.35)
            company = Company(
                name=name,
                kind="company",
                country_id=country.agent_id,
                currency=country.currency,
                sector=sector,
                employees=employees,
                wage=rng.uniform(1.2, 8.5) * (0.45 + fiat_per_wk[country.currency] / 100.0 * 0.22),
                productivity=productivity,
                capital=capital,
                inventory=rng.uniform(10.0, 250.0),
                price=price,
                product_quality=quality,
                export_orientation=rng.uniform(0.05, 0.95) * country.trade_openness,
                fraud_tendency=fraud,
                reputation=reputation,
                risk=clamp(rng.uniform(0.15, 0.70) * (1.05 - reputation * 0.45), 0.02, 0.98),
            )
            company.add_fiat(country.currency, capital * rng.uniform(0.02, 0.18))
            initial_wk = TruthStack({
                Layer.CAUSAL.value: productivity * 12.0,
                Layer.POTENTIAL.value: quality * 15.0,
                Layer.SOCIAL.value: reputation * 8.0,
                Layer.LEGAL.value: reputation * 6.0,
                Layer.EXISTENCE.value: math.log1p(capital) * 2.0,
            })
            company.add_truth(initial_wk)
            companies[company.agent_id] = company
            country.company_ids.append(company.agent_id)

        un = UNInstitution(
            name="United Nations of the Planet",
            kind="un",
            country_id=None,
            legitimacy=clamp(mean_or((c.stability for c in country_list), 0.6) + rng.gauss(0, 0.05), 0.08, 0.95),
            audit_strength=clamp(0.35 + mean_or((c.education_index for c in country_list), 0.55) * 0.35 + rng.gauss(0, 0.04), 0.05, 0.90),
            peacekeeping_capacity=clamp(0.30 + mean_or((c.military_capacity for c in country_list), 0.5) * 0.30 + rng.gauss(0, 0.05), 0.05, 0.90),
            reputation=0.70,
            risk=0.30,
        )
        un.add_truth(TruthStack({Layer.LEGAL.value: 200.0, Layer.SOCIAL.value: 180.0, Layer.EPISTEMIC.value: 160.0, Layer.ETHICAL.value: 220.0, Layer.SECURITY.value: 90.0}))

        defense_orgs: List[DefenseOrganization] = []
        for i in range(defense_orgs_n):
            size = rng.randint(max(2, countries_n // 8), max(2, min(countries_n, countries_n // 3 + 2)))
            members = rng.sample(country_list, min(size, len(country_list)))
            name = DEFENSE_NAMES[i % len(DEFENSE_NAMES)]
            if i >= len(DEFENSE_NAMES):
                name += f" {i+1}"
            readiness = rng.uniform(0.25, 0.85)
            cohesion = clamp(mean_or((c.stability for c in members), 0.6) + rng.gauss(0, 0.09), 0.05, 0.98)
            deterrence = clamp(mean_or((c.military_capacity for c in members), 0.5) * 0.6 + readiness * 0.4, 0.05, 0.98)
            org = DefenseOrganization(
                name=name,
                member_ids=[m.agent_id for m in members],
                doctrine=rng.choice(DOCTRINES),
                readiness=readiness,
                cohesion=cohesion,
                deterrence=deterrence,
            )
            org.truth = TruthStack({
                Layer.SECURITY.value: deterrence * 160.0,
                Layer.LEGAL.value: cohesion * 55.0,
                Layer.SOCIAL.value: cohesion * 40.0,
                Layer.RISK_REDUCTION.value: readiness * 75.0,
            })
            defense_orgs.append(org)

        planet = Planet(
            seed=seed,
            rng=rng,
            countries=countries,
            central_banks=central_banks,
            banks=banks,
            companies=companies,
            un=un,
            defense_orgs=defense_orgs,
            ledger=TruthLedger(),
            fiat_per_wk=fiat_per_wk,
        )
        return planet


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Planetare Wirtschaftssimulation mit gestapelter Wahrheitswert-Währung WK.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent(
            """
            Presets:
              tiny      kleine Testwelt
              standard  normale große Welt
              large     sehr große Welt
              epic      maximal große Welt, kann je nach Rechner länger laufen

            Beispiele:
              python planet_truth_economy_sim.py --preset tiny --months 24 --verbose
              python planet_truth_economy_sim.py --preset standard --seed 7 --out sim_output
              python planet_truth_economy_sim.py --preset large --months 240 --out large_run
            """
        ),
    )
    parser.add_argument("--preset", choices=sorted(PRESETS), default="standard")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--months", type=int, default=None, help="Ueberschreibt die Monatszahl des Presets.")
    parser.add_argument("--countries", type=int, default=None, help="Ueberschreibt Laenderzahl.")
    parser.add_argument("--companies", type=int, default=None, help="Ueberschreibt Unternehmenszahl.")
    parser.add_argument("--banks", type=int, default=None, help="Ueberschreibt Bankenzahl.")
    parser.add_argument("--defense-orgs", type=int, default=None, help="Ueberschreibt Zahl der Verteidigungsorganisationen.")
    parser.add_argument("--out", type=Path, default=Path("truth_economy_output"), help="Ausgabeordner fuer CSV/JSON/TXT.")
    parser.add_argument("--verbose", action="store_true", help="Jaehrlichen Status ausgeben.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    preset = PRESETS[args.preset]
    countries_n = args.countries if args.countries is not None else preset["countries"]
    companies_n = args.companies if args.companies is not None else preset["companies"]
    banks_n = args.banks if args.banks is not None else preset["banks"]
    defense_orgs_n = args.defense_orgs if args.defense_orgs is not None else preset["defense_orgs"]
    months = args.months if args.months is not None else preset["months"]

    planet = PlanetFactory.create(
        seed=args.seed,
        countries_n=countries_n,
        companies_n=companies_n,
        banks_n=banks_n,
        defense_orgs_n=defense_orgs_n,
    )
    print(
        f"Starte Simulation: preset={args.preset}, seed={args.seed}, "
        f"Laender={countries_n}, Unternehmen={companies_n}, Banken={banks_n}, "
        f"Verteidigungsorganisationen={defense_orgs_n}, Monate={months}"
    )
    planet.run(months=months, verbose=args.verbose)
    planet.write_reports(args.out)
    print()
    print(planet.summary_text())
    print()
    print(f"Berichte geschrieben nach: {args.out.resolve()}")


if __name__ == "__main__":
    main()
