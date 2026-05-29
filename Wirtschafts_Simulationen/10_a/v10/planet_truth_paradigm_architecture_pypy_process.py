#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Planetare Wirtschaftssimulation: Paradigma-Architektur-Edition.

Diese Version modelliert die vorherige Wirtschaft mit gestapelten Wahrheitswerten
als mehrschichtige Architektur:

1. Transport- und Ausführungsschicht
   - Netzwerke, Topologien, FIFO/LIFO/Priority-Queues
   - Half-Duplex- und Full-Duplex-Kanäle
   - Semaphoren als knappe Durchleitungs-, Liquiditäts- und Vertrauenskapazitäten

2. Semantik- und Bedeutungs-Schicht
   - Kategorien, Objekte, Morphismen
   - Funktoren zwischen Fiat-, Rechts-, Sicherheits- und Wahrheitskategorien
   - natürliche Transformationen als Kohärenzlücken zwischen Bewertungsparadigmen
   - universelle Eigenschaften: Terminalobjekt, Produkt, Pullback, Pushout, Equalizer

3. Lokal-global-Schicht
   - Topologische Räume aus Ländern, Allianzen, Handelszonen und Institutionen
   - Prägarben lokaler Wahrheitszustände
   - Garbenkleben: lokale Wahrheiten werden zu globalem Wahrheitskapital geglättet

4. Ökonomische Domäne
   - Länder, Zentralbanken, Banken, UN, Verteidigungsorganisationen, Unternehmen
   - Fiat-Währungen je Land plus planetare WK-Währung als TruthVector
   - Schulden, Defizite, falsche Wahrheitsstapel, Audits, Sanktionen, Konflikte

Nur Standardbibliothek. Keine externen Pakete nötig.

Start:
    python planet_truth_paradigm_architecture_pypy_process.py --preset tiny --months 24 --print-art
    pypy3 planet_truth_paradigm_architecture_pypy_process.py --preset standard --months 120 --workers auto --out run_standard
    pypy3 planet_truth_paradigm_architecture_pypy_process.py --preset epic --months 720 --workers auto --seed 42 --out epic_world
"""
from __future__ import annotations

import argparse
import csv
import heapq
import json
import math
import multiprocessing as mp
import os
import random
import re
import shutil
import statistics
import textwrap
import uuid
from abc import ABC, abstractmethod
from collections import Counter, defaultdict, deque
from concurrent.futures import ProcessPoolExecutor
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Deque, Dict, FrozenSet, Iterable, Iterator, List, Optional, Sequence, Tuple, Type


# =============================================================================
# 0. Hilfsfunktionen
# =============================================================================


def uid(prefix: str) -> str:
    return f"{prefix}_{uuid.uuid4().hex[:10]}"


def clamp(x: float, lo: float, hi: float) -> float:
    return max(lo, min(hi, x))


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    return a / b if abs(b) > 1e-12 else default


def mean_or(values: Iterable[float], default: float = 0.0) -> float:
    vals = list(values)
    return statistics.mean(vals) if vals else default


def fmt(x: float) -> str:
    sign = "-" if x < 0 else ""
    x = abs(x)
    if x >= 1_000_000_000_000:
        return f"{sign}{x/1_000_000_000_000:.2f}T"
    if x >= 1_000_000_000:
        return f"{sign}{x/1_000_000_000:.2f}B"
    if x >= 1_000_000:
        return f"{sign}{x/1_000_000:.2f}M"
    if x >= 1_000:
        return f"{sign}{x/1_000:.2f}K"
    return f"{sign}{x:.2f}"


def pct(x: float) -> str:
    return f"{100*x:.2f}%"


def bar(value: float, max_value: float, width: int = 28, charset: str = "█") -> str:
    if max_value <= 0:
        filled = 0
    else:
        filled = int(clamp(abs(value) / max_value, 0, 1) * width)
    return charset * filled + "░" * (width - filled)


def spark(values: Sequence[float], width: int = 60) -> str:
    chars = "▁▂▃▄▅▆▇█"
    if not values:
        return ""
    if len(values) > width:
        step = len(values) / width
        reduced = [values[int(i * step)] for i in range(width)]
    else:
        reduced = list(values)
    lo, hi = min(reduced), max(reduced)
    span = hi - lo
    out = []
    for v in reduced:
        idx = 0 if span <= 1e-12 else int(clamp((v - lo) / span, 0, 0.999) * len(chars))
        out.append(chars[idx])
    return "".join(out)


def slug(text: str) -> str:
    out = []
    for ch in text.lower():
        if ch.isalnum():
            out.append(ch)
        elif ch in " -_/":
            out.append("_")
    s = "".join(out).strip("_")
    while "__" in s:
        s = s.replace("__", "_")
    return s or "x"


def weighted_choice(rng: random.Random, items: Sequence[Any], weights: Sequence[float]) -> Optional[Any]:
    if not items:
        return None
    total = sum(max(0.0, w) for w in weights)
    if total <= 0:
        return rng.choice(list(items))
    r = rng.random() * total
    acc = 0.0
    for item, weight in zip(items, weights):
        acc += max(0.0, weight)
        if acc >= r:
            return item
    return items[-1]


# UTF-8-Art ist absichtlich fünf Zeichen schmaler als angefragt.
# Viele Terminals brechen bei exakt voller Breite wegen Scrollbar/Prompt/
# Ambiguous-Width-Zeichen rechts um. Diese zentrale Reserve behebt das.
UTF8_PRINT_WIDTH_SAFETY_MARGIN = 5
MIN_PRINT_WIDTH = 48
FALLBACK_PRINT_WIDTH = 120


def terminal_print_width(default: int = FALLBACK_PRINT_WIDTH, margin: int = UTF8_PRINT_WIDTH_SAFETY_MARGIN) -> int:
    columns = shutil.get_terminal_size(fallback=(default, 40)).columns
    return max(MIN_PRINT_WIDTH, int(columns) - int(margin))


def clamp_print_width(requested: Optional[int] = None) -> int:
    detected = terminal_print_width()
    if requested is None:
        return detected
    # Angefragte Boxbreite ebenfalls um fünf Zeichen reduzieren, danach an Terminal kappen.
    requested_safe = max(MIN_PRINT_WIDTH, int(requested) - UTF8_PRINT_WIDTH_SAFETY_MARGIN)
    return max(MIN_PRINT_WIDTH, min(requested_safe, detected))


ANSI_RESET = "\033[0m"
ANSI_COLORS = {
    "border": "\033[38;5;39m",
    "country": "\033[1;38;5;51m",
    "company": "\033[1;38;5;82m",
    "household": "\033[1;38;5;220m",
    "bank": "\033[1;38;5;201m",
    "central_bank": "\033[1;38;5;165m",
    "un": "\033[1;38;5;45m",
    "defense": "\033[1;38;5;196m",
    "currency": "\033[1;38;5;214m",
    "wk": "\033[1;38;5;226m",
    "number_pos": "\033[38;5;118m",
    "number_neg": "\033[38;5;203m",
    "keyword": "\033[1;38;5;141m",
    "bar": "\033[38;5;84m",
    "bar_bg": "\033[38;5;240m",
    "spark_low": "\033[38;5;117m",
    "spark_mid": "\033[38;5;190m",
    "spark_high": "\033[38;5;208m",
}


def ansi(text: str, color: str, enabled: bool = True) -> str:
    if not enabled or not text:
        return text
    return f"{ANSI_COLORS.get(color, color)}{text}{ANSI_RESET}"


def translate_output(text: str, lang: str = "en") -> str:
    if lang.lower().startswith("de"):
        return text
    replacements = [
        ("Planetare Wirtschaftssimulation — Paradigma-Architektur-Edition", "Planetary Economic Simulation — Paradigm Architecture Edition"),
        ("Preset", "Preset"),
        ("Monate", "Months"),
        ("Agenten", "Agents"),
        ("Länder", "Countries"),
        ("Events", "Events"),
        ("Wahrheitsschuld", "Truth debt"),
        ("Morphismen", "Morphisms"),
        ("Letzte Garben-Konsistenzlücke", "Latest sheaf consistency gap"),
        ("Prozesse", "Processes"),
        ("Volatilität", "Volatility"),
        ("Gesamt", "Overall"),
        ("Sprache", "Language"),
        ("Klassenvererbung und Paradigma-Architektur", "Class inheritance and paradigm architecture"),
        ("Netzwerk-Topologie, Queues, Half-/Full-Duplex", "Network topology, queues, half/full duplex"),
        ("Semaphore als Knappheits- und Durchleitungslogik", "Semaphores as scarcity and throughput logic"),
        ("Kategorie, Morphismus, Funktor, natürliche Transformation", "Category, morphism, functor, natural transformation"),
        ("Prägarben, Garben, Topologie und Klebeeigenschaft", "Presheaves, sheaves, topology, and gluing property"),
        ("Gestapelte Wahrheit als planetare Vektorwährung WK", "Stacked truth as planetary vector currency WK"),
        ("Länder × Wahrheitsdimensionen Heatmap", "Countries × truth dimensions heatmap"),
        ("FIFO/LIFO/Priority Queues pro Agent", "FIFO/LIFO/priority queues per agent"),
        ("Makro-Zeitreihen als UTF-8 Sparklines", "Macro time series as UTF-8 sparklines"),
        ("Welt-Ereignisse, Krisen, Durchbrüche", "World events, crises, breakthroughs"),
        ("Morphismenfluss: Netzwerk → Kategorie → WK", "Morphism flow: network → category → WK"),
        ("UN, Zentralbanken und Verteidigungsorganisationen", "UN, central banks, and defense organizations"),
        ("Output", "Output"),
    ]
    out = text
    for src, dst in replacements:
        out = out.replace(src, dst)
    return out


def chunked(items: Sequence[Any], chunk_count: int) -> List[List[Any]]:
    if not items:
        return []
    chunk_count = max(1, min(int(chunk_count), len(items)))
    size = int(math.ceil(len(items) / chunk_count))
    return [list(items[i:i + size]) for i in range(0, len(items), size)]


def resolve_mp_start_method(requested: str = "auto") -> str:
    methods = mp.get_all_start_methods()
    if requested != "auto":
        if requested not in methods:
            raise ValueError(f"Multiprocessing start method {requested!r} nicht verfügbar; verfügbar: {methods}")
        return requested
    if "fork" in methods:
        return "fork"
    if "forkserver" in methods:
        return "forkserver"
    return methods[0] if methods else "spawn"


def auto_worker_count(preset: str, requested: Any = "auto") -> int:
    if isinstance(requested, str):
        value = requested.strip().lower()
        if value not in ("", "0", "auto"):
            return max(1, int(value))
    else:
        if int(requested) > 0:
            return max(1, int(requested))
    cpu = os.cpu_count() or 1
    caps = {"tiny": 4, "standard": 8, "large": 16, "epic": 32}
    return max(1, min(cpu, caps.get(preset, 4)))


class ProcessParallelRuntime:
    """PyPy3-freundliche Prozessparallelität. Keine Threads.

    Jobs sind absichtlich grob gebündelt: PyPy3 profitiert von Prozessen, aber
    nicht von tausenden winzigen Pickle-Tasks. Bei exotischen Pickle-/Pool-
    Problemen fällt die Runtime deterministisch auf seriell zurück.
    """

    def __init__(self, preset: str, requested_workers: Any = "auto", start_method: str = "auto", min_items: int = 16) -> None:
        self.requested_workers = requested_workers
        self.workers = auto_worker_count(preset, requested_workers)
        self.start_method = resolve_mp_start_method(start_method)
        self.min_items = max(1, int(min_items))
        self.executor: Optional[ProcessPoolExecutor] = None
        self.disabled_reason = ""
        self.parallel_batches = 0
        self.parallel_tasks = 0
        self.fallback_batches = 0

    @property
    def enabled(self) -> bool:
        return self.workers > 1 and not self.disabled_reason

    def should_parallel(self, item_count: int, min_items: Optional[int] = None) -> bool:
        threshold = self.min_items if min_items is None else int(min_items)
        return self.enabled and item_count >= threshold

    def _ensure_executor(self) -> Optional[ProcessPoolExecutor]:
        if not self.enabled:
            return None
        if self.executor is not None:
            return self.executor
        try:
            ctx = mp.get_context(self.start_method)
            self.executor = ProcessPoolExecutor(max_workers=self.workers, mp_context=ctx)
            return self.executor
        except Exception as exc:  # defensive fallback for PyPy/embedded runtimes
            self.disabled_reason = f"process pool unavailable: {type(exc).__name__}: {exc}"
            return None

    def map(self, func: Callable[[Any], Any], tasks: Sequence[Any], min_items: Optional[int] = None, chunksize: Optional[int] = None) -> List[Any]:
        task_list = list(tasks)
        if not self.should_parallel(len(task_list), min_items):
            self.fallback_batches += 1
            return [func(t) for t in task_list]
        executor = self._ensure_executor()
        if executor is None:
            self.fallback_batches += 1
            return [func(t) for t in task_list]
        try:
            cs = chunksize or max(1, len(task_list) // max(1, self.workers * 4))
            out = list(executor.map(func, task_list, chunksize=cs))
            self.parallel_batches += 1
            self.parallel_tasks += len(task_list)
            return out
        except Exception as exc:
            self.disabled_reason = f"process fallback after {type(exc).__name__}: {exc}"
            self.shutdown()
            self.fallback_batches += 1
            return [func(t) for t in task_list]

    def shutdown(self) -> None:
        if self.executor is not None:
            self.executor.shutdown(wait=True, cancel_futures=False)
            self.executor = None

    def summary(self) -> Dict[str, Any]:
        return {
            "mode": "multiprocessing.ProcessPoolExecutor",
            "requested_workers": self.requested_workers,
            "workers": self.workers,
            "start_method": self.start_method,
            "enabled": self.enabled,
            "parallel_batches": self.parallel_batches,
            "parallel_tasks": self.parallel_tasks,
            "fallback_batches": self.fallback_batches,
            "disabled_reason": self.disabled_reason,
        }


# =============================================================================
# 1. Wahrheitswährung: gestapelte Wahrheitswerte als Vektor-Währung
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
    CATEGORY_COHERENCE = "category_coherence"
    SHEAF_CONSISTENCY = "sheaf_consistency"
    NETWORK_REACHABILITY = "network_reachability"


ALL_TRUTH_LAYERS: Tuple[str, ...] = tuple(layer.value for layer in TruthLayer)

TRUTH_WEIGHTS: Dict[str, float] = {
    TruthLayer.EXISTENCE.value: 1.05,
    TruthLayer.EPISTEMIC.value: 1.35,
    TruthLayer.SOCIAL.value: 0.90,
    TruthLayer.LEGAL.value: 1.20,
    TruthLayer.CAUSAL.value: 1.45,
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
    TruthLayer.CATEGORY_COHERENCE.value: 1.25,
    TruthLayer.SHEAF_CONSISTENCY.value: 1.30,
    TruthLayer.NETWORK_REACHABILITY.value: 1.05,
}

POSITIVE_DECAY: Dict[str, float] = {layer: 0.006 for layer in ALL_TRUTH_LAYERS}
POSITIVE_DECAY.update({
    TruthLayer.TEMPORAL.value: 0.030,
    TruthLayer.PERCEPTION.value: 0.045,
    TruthLayer.ATTENTION.value: 0.065,
    TruthLayer.FOOD.value: 0.020,
    TruthLayer.CAUSAL.value: 0.008,
    TruthLayer.SHEAF_CONSISTENCY.value: 0.004,
    TruthLayer.CATEGORY_COHERENCE.value: 0.004,
})
NEGATIVE_GROWTH: Dict[str, float] = {layer: 0.009 for layer in ALL_TRUTH_LAYERS}
NEGATIVE_GROWTH.update({
    TruthLayer.EPISTEMIC.value: 0.020,
    TruthLayer.LEGAL.value: 0.014,
    TruthLayer.SOVEREIGNTY.value: 0.018,
    TruthLayer.LIQUIDITY.value: 0.016,
    TruthLayer.SHEAF_CONSISTENCY.value: 0.012,
    TruthLayer.CATEGORY_COHERENCE.value: 0.013,
})


@dataclass
class TruthVector:
    """Planetare WK-Währung als gestapelter Wahrheitsvektor.

    Positive Komponenten sind realitätsstabilisierende Aussagen.
    Negative Komponenten sind Schulden, Lügenlasten, Defizite, uneingelöste Claims.
    """

    values: Dict[str, float] = field(default_factory=dict)

    def __post_init__(self) -> None:
        for layer in ALL_TRUTH_LAYERS:
            self.values.setdefault(layer, 0.0)

    @classmethod
    def zero(cls) -> "TruthVector":
        return cls({layer: 0.0 for layer in ALL_TRUTH_LAYERS})

    @classmethod
    def from_scalar(cls, amount: float, layers: Optional[Sequence[str]] = None) -> "TruthVector":
        layers = list(layers or ALL_TRUTH_LAYERS)
        if not layers:
            return cls.zero()
        share = amount / len(layers)
        return cls({layer: share if layer in layers else 0.0 for layer in ALL_TRUTH_LAYERS})

    @classmethod
    def random(cls, rng: random.Random, scale: float = 100.0, positive_bias: float = 0.8) -> "TruthVector":
        data: Dict[str, float] = {}
        for layer in ALL_TRUTH_LAYERS:
            sign = 1.0 if rng.random() < positive_bias else -1.0
            data[layer] = sign * rng.random() * scale * rng.uniform(0.2, 1.0)
        return cls(data)

    def copy(self) -> "TruthVector":
        return TruthVector(dict(self.values))

    def __getitem__(self, layer: str) -> float:
        return self.values.get(layer, 0.0)

    def __setitem__(self, layer: str, value: float) -> None:
        self.values[layer] = float(value)

    def add(self, other: "TruthVector", factor: float = 1.0) -> "TruthVector":
        for layer in ALL_TRUTH_LAYERS:
            self.values[layer] = self.values.get(layer, 0.0) + other.values.get(layer, 0.0) * factor
        return self

    def added(self, other: "TruthVector", factor: float = 1.0) -> "TruthVector":
        return self.copy().add(other, factor)

    def scale(self, factor: float) -> "TruthVector":
        for layer in ALL_TRUTH_LAYERS:
            self.values[layer] *= factor
        return self

    def scaled(self, factor: float) -> "TruthVector":
        return self.copy().scale(factor)

    def weighted_score(self) -> float:
        return sum(self.values[layer] * TRUTH_WEIGHTS.get(layer, 1.0) for layer in ALL_TRUTH_LAYERS)

    def positive_score(self) -> float:
        return sum(max(0.0, self.values[layer]) * TRUTH_WEIGHTS.get(layer, 1.0) for layer in ALL_TRUTH_LAYERS)

    def negative_score(self) -> float:
        return sum(min(0.0, self.values[layer]) * TRUTH_WEIGHTS.get(layer, 1.0) for layer in ALL_TRUTH_LAYERS)

    def debt_score(self) -> float:
        return -self.negative_score()

    def norm(self) -> float:
        return math.sqrt(sum(v * v for v in self.values.values()))

    def decay_one_month(self) -> "TruthVector":
        for layer, val in list(self.values.items()):
            if val >= 0:
                self.values[layer] = val * (1.0 - POSITIVE_DECAY.get(layer, 0.006))
            else:
                self.values[layer] = val * (1.0 + NEGATIVE_GROWTH.get(layer, 0.009))
        return self

    def top(self, n: int = 5, positive: bool = True) -> List[Tuple[str, float]]:
        items = list(self.values.items())
        if positive:
            items = [(k, v) for k, v in items if v > 0]
            return sorted(items, key=lambda kv: kv[1], reverse=True)[:n]
        items = [(k, v) for k, v in items if v < 0]
        return sorted(items, key=lambda kv: kv[1])[:n]

    def clamp_layers(self, lo: float, hi: float) -> "TruthVector":
        for layer in ALL_TRUTH_LAYERS:
            self.values[layer] = clamp(self.values[layer], lo, hi)
        return self

    def as_dict(self) -> Dict[str, float]:
        return dict(self.values)




def _aggregate_agent_chunk(rows: List[Tuple[bool, float, Dict[str, float]]]) -> Tuple[float, Dict[str, float]]:
    gdp = 0.0
    values = {layer: 0.0 for layer in ALL_TRUTH_LAYERS}
    for is_country, country_gdp, truth_values in rows:
        if is_country:
            gdp += country_gdp
        for layer in ALL_TRUTH_LAYERS:
            values[layer] += truth_values.get(layer, 0.0)
    return gdp, values


# =============================================================================
# 2. Queues, Semaphore, Duplex-Kanäle
# =============================================================================


class QueueDiscipline(str, Enum):
    FIFO = "FIFO"
    LIFO = "LIFO"
    PRIORITY = "PRIORITY"


class DuplexMode(str, Enum):
    HALF = "HALF_DUPLEX"
    FULL = "FULL_DUPLEX"


class MessageKind(str, Enum):
    TRADE = "trade"
    CREDIT = "credit"
    AUDIT = "audit"
    SANCTION = "sanction"
    DEFENSE = "defense"
    KNOWLEDGE = "knowledge"
    LIQUIDITY = "liquidity"
    SHEAF_PATCH = "sheaf_patch"
    CATEGORY_MORPHISM = "category_morphism"


@dataclass(order=True)
class PrioritizedMessage:
    priority: float
    serial: int
    message: "NetworkMessage" = field(compare=False)


@dataclass
class NetworkMessage:
    source_id: str
    target_id: str
    kind: MessageKind
    fiat_amount: float = 0.0
    currency: str = "WK"
    truth: TruthVector = field(default_factory=TruthVector.zero)
    payload: Dict[str, Any] = field(default_factory=dict)
    ttl: int = 8
    priority: float = 1.0
    id: str = field(default_factory=lambda: uid("msg"))

    def tick(self) -> bool:
        self.ttl -= 1
        return self.ttl > 0


class MessageQueue(ABC):
    def __init__(self, name: str, capacity: int = 10_000) -> None:
        self.name = name
        self.capacity = capacity
        self.dropped = 0

    @abstractmethod
    def push(self, message: NetworkMessage) -> bool:
        raise NotImplementedError

    @abstractmethod
    def pop(self) -> Optional[NetworkMessage]:
        raise NotImplementedError

    @abstractmethod
    def __len__(self) -> int:
        raise NotImplementedError

    def drain(self, limit: int) -> List[NetworkMessage]:
        out: List[NetworkMessage] = []
        for _ in range(limit):
            item = self.pop()
            if item is None:
                break
            out.append(item)
        return out


class FIFOQueue(MessageQueue):
    def __init__(self, name: str, capacity: int = 10_000) -> None:
        super().__init__(name, capacity)
        self.data: Deque[NetworkMessage] = deque()

    def push(self, message: NetworkMessage) -> bool:
        if len(self.data) >= self.capacity:
            self.dropped += 1
            return False
        self.data.append(message)
        return True

    def pop(self) -> Optional[NetworkMessage]:
        return self.data.popleft() if self.data else None

    def __len__(self) -> int:
        return len(self.data)


class LIFOQueue(MessageQueue):
    def __init__(self, name: str, capacity: int = 10_000) -> None:
        super().__init__(name, capacity)
        self.data: List[NetworkMessage] = []

    def push(self, message: NetworkMessage) -> bool:
        if len(self.data) >= self.capacity:
            self.dropped += 1
            return False
        self.data.append(message)
        return True

    def pop(self) -> Optional[NetworkMessage]:
        return self.data.pop() if self.data else None

    def __len__(self) -> int:
        return len(self.data)


class PriorityMessageQueue(MessageQueue):
    def __init__(self, name: str, capacity: int = 10_000) -> None:
        super().__init__(name, capacity)
        self.heap: List[PrioritizedMessage] = []
        self.serial = 0

    def push(self, message: NetworkMessage) -> bool:
        if len(self.heap) >= self.capacity:
            self.dropped += 1
            return False
        self.serial += 1
        heapq.heappush(self.heap, PrioritizedMessage(-message.priority, self.serial, message))
        return True

    def pop(self) -> Optional[NetworkMessage]:
        return heapq.heappop(self.heap).message if self.heap else None

    def __len__(self) -> int:
        return len(self.heap)


class SimpleSemaphore:
    """Diskrete Semaphor-Primitive für Simulationsressourcen.

    Der Semaphore ist bewusst nicht threading-orientiert, sondern ökonomisch:
    Tokens stehen für Leitungskapazität, Liquidität, Rechtssicherheit oder Vertrauen.
    """

    def __init__(self, name: str, capacity: int) -> None:
        self.name = name
        self.capacity = max(0, int(capacity))
        self.available = max(0, int(capacity))
        self.waits = 0
        self.acquisitions = 0
        self.releases = 0

    def acquire(self, tokens: int = 1) -> bool:
        tokens = max(0, int(tokens))
        if tokens <= self.available:
            self.available -= tokens
            self.acquisitions += tokens
            return True
        self.waits += 1
        return False

    def release(self, tokens: int = 1) -> None:
        tokens = max(0, int(tokens))
        self.available = min(self.capacity, self.available + tokens)
        self.releases += tokens

    @property
    def utilization(self) -> float:
        return 1.0 - safe_div(self.available, self.capacity, 0.0)

    def snapshot(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "capacity": self.capacity,
            "available": self.available,
            "utilization": self.utilization,
            "waits": self.waits,
        }


class Channel(ABC):
    def __init__(
        self,
        a_id: str,
        b_id: str,
        capacity: int = 20,
        queue_discipline: QueueDiscipline = QueueDiscipline.FIFO,
        latency: int = 1,
        name: Optional[str] = None,
    ) -> None:
        self.id = uid("ch")
        self.name = name or f"{a_id[:4]}↔{b_id[:4]}"
        self.a_id = a_id
        self.b_id = b_id
        self.capacity = max(1, capacity)
        self.latency = max(1, latency)
        self.q_ab = self._make_queue(f"{self.name}:A→B", queue_discipline)
        self.q_ba = self._make_queue(f"{self.name}:B→A", queue_discipline)
        self.in_flight: List[Tuple[int, str, NetworkMessage]] = []
        self.transmitted = 0
        self.blocked = 0

    def _make_queue(self, name: str, discipline: QueueDiscipline) -> MessageQueue:
        if discipline == QueueDiscipline.LIFO:
            return LIFOQueue(name, capacity=10_000)
        if discipline == QueueDiscipline.PRIORITY:
            return PriorityMessageQueue(name, capacity=10_000)
        return FIFOQueue(name, capacity=10_000)

    def other(self, node_id: str) -> str:
        if node_id == self.a_id:
            return self.b_id
        if node_id == self.b_id:
            return self.a_id
        raise ValueError(f"Node {node_id} not on channel {self.id}")

    def queue_for(self, source_id: str) -> MessageQueue:
        return self.q_ab if source_id == self.a_id else self.q_ba

    @property
    @abstractmethod
    def mode(self) -> DuplexMode:
        raise NotImplementedError

    @abstractmethod
    def can_inject(self, source_id: str) -> bool:
        raise NotImplementedError

    @abstractmethod
    def after_tick_release(self) -> None:
        raise NotImplementedError

    def enqueue(self, message: NetworkMessage) -> bool:
        q = self.queue_for(message.source_id)
        return q.push(message)

    def tick(self) -> List[NetworkMessage]:
        delivered: List[NetworkMessage] = []
        remaining: List[Tuple[int, str, NetworkMessage]] = []
        for steps_left, direction, message in self.in_flight:
            steps_left -= 1
            if steps_left <= 0:
                delivered.append(message)
            else:
                remaining.append((steps_left, direction, message))
        self.in_flight = remaining
        for source in (self.a_id, self.b_id):
            if not self.can_inject(source):
                continue
            quota = self.capacity
            q = self.queue_for(source)
            for message in q.drain(quota):
                if not message.tick():
                    continue
                direction = "AB" if source == self.a_id else "BA"
                self.in_flight.append((self.latency, direction, message))
                self.transmitted += 1
        self.after_tick_release()
        return delivered

    def load(self) -> int:
        return len(self.q_ab) + len(self.q_ba) + len(self.in_flight)

    def endpoints(self) -> Tuple[str, str]:
        return self.a_id, self.b_id


class HalfDuplexChannel(Channel):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.mutex = SimpleSemaphore(f"halfduplex:{self.name}", 1)
        self.active_direction: Optional[str] = None

    @property
    def mode(self) -> DuplexMode:
        return DuplexMode.HALF

    def can_inject(self, source_id: str) -> bool:
        direction = "AB" if source_id == self.a_id else "BA"
        if self.active_direction is None:
            if self.mutex.acquire(1):
                self.active_direction = direction
                return True
            self.blocked += 1
            return False
        return self.active_direction == direction

    def after_tick_release(self) -> None:
        if not self.in_flight:
            self.active_direction = None
            self.mutex.release(1)


class FullDuplexChannel(Channel):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.sem_ab = SimpleSemaphore(f"fullduplex:{self.name}:AB", self.capacity)
        self.sem_ba = SimpleSemaphore(f"fullduplex:{self.name}:BA", self.capacity)

    @property
    def mode(self) -> DuplexMode:
        return DuplexMode.FULL

    def can_inject(self, source_id: str) -> bool:
        sem = self.sem_ab if source_id == self.a_id else self.sem_ba
        ok = sem.acquire(1)
        if not ok:
            self.blocked += 1
        return ok

    def after_tick_release(self) -> None:
        self.sem_ab.release(self.capacity)
        self.sem_ba.release(self.capacity)


class SecureFullDuplexChannel(FullDuplexChannel):
    """Spezialisierter Full-Duplex-Kanal für Governance/Kredit/Verteidigung."""

    def __init__(self, *args: Any, encryption_truth: float = 3.0, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        self.encryption_truth = encryption_truth

    def enqueue(self, message: NetworkMessage) -> bool:
        message.truth[TruthLayer.SECURITY.value] += self.encryption_truth
        message.truth[TruthLayer.EPISTEMIC.value] += 0.25 * self.encryption_truth
        return super().enqueue(message)


# =============================================================================
# 3. Netzwerke und Topologien
# =============================================================================


class NetworkTopology(ABC):
    name = "abstract"

    @abstractmethod
    def build(self, network: "Network", node_ids: Sequence[str], rng: random.Random) -> None:
        raise NotImplementedError


class MeshTopology(NetworkTopology):
    name = "mesh"

    def __init__(self, density: float = 0.15, max_edges: int = 1_500) -> None:
        self.density = density
        self.max_edges = max_edges

    def build(self, network: "Network", node_ids: Sequence[str], rng: random.Random) -> None:
        ids = list(node_ids)
        edges = 0
        for i, a in enumerate(ids):
            for b in ids[i + 1:]:
                if edges >= self.max_edges:
                    return
                if rng.random() < self.density:
                    network.connect(a, b, rng=rng)
                    edges += 1


class RingTopology(NetworkTopology):
    name = "ring"

    def build(self, network: "Network", node_ids: Sequence[str], rng: random.Random) -> None:
        ids = list(node_ids)
        rng.shuffle(ids)
        if len(ids) < 2:
            return
        for i, a in enumerate(ids):
            network.connect(a, ids[(i + 1) % len(ids)], rng=rng)


class StarTopology(NetworkTopology):
    name = "star"

    def __init__(self, hubs: int = 1) -> None:
        self.hubs = max(1, hubs)

    def build(self, network: "Network", node_ids: Sequence[str], rng: random.Random) -> None:
        ids = list(node_ids)
        if len(ids) < 2:
            return
        hubs = ids[: self.hubs]
        for node in ids[self.hubs:]:
            network.connect(rng.choice(hubs), node, rng=rng)


class CorePeripheryTopology(NetworkTopology):
    name = "core-periphery"

    def __init__(self, core_fraction: float = 0.18, periphery_degree: int = 2) -> None:
        self.core_fraction = core_fraction
        self.periphery_degree = periphery_degree

    def build(self, network: "Network", node_ids: Sequence[str], rng: random.Random) -> None:
        ids = list(node_ids)
        rng.shuffle(ids)
        if len(ids) < 2:
            return
        core_n = max(2, int(len(ids) * self.core_fraction))
        core = ids[:core_n]
        periphery = ids[core_n:]
        for i, a in enumerate(core):
            for b in core[i + 1:]:
                network.connect(a, b, rng=rng)
        for node in periphery:
            for hub in rng.sample(core, min(len(core), self.periphery_degree)):
                network.connect(node, hub, rng=rng)


class Network(ABC):
    def __init__(
        self,
        name: str,
        topology: NetworkTopology,
        channel_cls: Type[Channel],
        queue_discipline: QueueDiscipline = QueueDiscipline.FIFO,
        default_capacity: int = 20,
    ) -> None:
        self.name = name
        self.topology = topology
        self.channel_cls = channel_cls
        self.queue_discipline = queue_discipline
        self.default_capacity = default_capacity
        self.nodes: Dict[str, "Agent"] = {}
        self.channels: Dict[Tuple[str, str], Channel] = {}
        self.delivered_total = 0
        self.failed_sends = 0

    def add_node(self, agent: "Agent") -> None:
        self.nodes[agent.id] = agent

    def key(self, a: str, b: str) -> Tuple[str, str]:
        return tuple(sorted((a, b)))  # type: ignore[return-value]

    def connect(self, a_id: str, b_id: str, rng: Optional[random.Random] = None) -> Optional[Channel]:
        if a_id == b_id:
            return None
        key = self.key(a_id, b_id)
        if key in self.channels:
            return self.channels[key]
        rng = rng or random.Random()
        cap = max(1, int(self.default_capacity * rng.uniform(0.6, 1.8)))
        latency = rng.choice([1, 1, 2, 2, 3])
        channel = self.channel_cls(
            a_id,
            b_id,
            capacity=cap,
            queue_discipline=self.queue_discipline,
            latency=latency,
            name=f"{self.name}:{a_id[:4]}↔{b_id[:4]}",
        )
        self.channels[key] = channel
        return channel

    def build_topology(self, rng: random.Random) -> None:
        self.topology.build(self, list(self.nodes.keys()), rng)

    def send(self, message: NetworkMessage) -> bool:
        key = self.key(message.source_id, message.target_id)
        channel = self.channels.get(key)
        if not channel:
            self.failed_sends += 1
            return False
        ok = channel.enqueue(message)
        if not ok:
            self.failed_sends += 1
        return ok

    def tick(self) -> List[NetworkMessage]:
        delivered: List[NetworkMessage] = []
        for channel in self.channels.values():
            delivered.extend(channel.tick())
        self.delivered_total += len(delivered)
        return delivered

    def degree(self, node_id: str) -> int:
        return sum(1 for a, b in self.channels if node_id in (a, b))

    def density(self) -> float:
        n = len(self.nodes)
        max_edges = n * (n - 1) / 2
        return safe_div(len(self.channels), max_edges, 0.0)

    def loads(self) -> List[int]:
        return [ch.load() for ch in self.channels.values()]

    def duplex_counts(self) -> Counter:
        return Counter(ch.mode.value for ch in self.channels.values())

    def queue_depth(self) -> int:
        return sum(ch.load() for ch in self.channels.values())


class TradeNetwork(Network):
    pass


class CreditNetwork(Network):
    pass


class GovernanceNetwork(Network):
    pass


class DefenseNetwork(Network):
    pass


class KnowledgeNetwork(Network):
    pass


class TruthNetwork(Network):
    pass


# =============================================================================
# 4. Kategorien, Morphismen, Funktoren, natürliche Transformationen
# =============================================================================


@dataclass
class CategoryObject:
    name: str
    ref_id: str
    kind: str = "object"
    meta: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Morphism:
    source: str
    target: str
    name: str
    kind: str
    fiat_value: float = 0.0
    truth_value: TruthVector = field(default_factory=TruthVector.zero)
    meta: Dict[str, Any] = field(default_factory=dict)
    id: str = field(default_factory=lambda: uid("mor"))

    def compose(self, other: "Morphism") -> "Morphism":
        if self.target != other.source:
            raise ValueError("Morphismen nicht komponierbar")
        return Morphism(
            source=self.source,
            target=other.target,
            name=f"{other.name}∘{self.name}",
            kind=f"{self.kind}→{other.kind}",
            fiat_value=self.fiat_value + other.fiat_value,
            truth_value=self.truth_value.added(other.truth_value),
            meta={"left": self.id, "right": other.id, "composition": True},
        )


class IdentityMorphism(Morphism):
    def __init__(self, object_id: str) -> None:
        super().__init__(object_id, object_id, f"id({object_id[:6]})", "identity")


class Category(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.objects: Dict[str, CategoryObject] = {}
        self.morphisms: List[Morphism] = []
        self.identities: Dict[str, IdentityMorphism] = {}

    def add_object(self, obj: CategoryObject) -> None:
        self.objects[obj.ref_id] = obj
        self.identities[obj.ref_id] = IdentityMorphism(obj.ref_id)

    def add_morphism(self, morphism: Morphism) -> None:
        if morphism.source not in self.objects:
            self.add_object(CategoryObject(morphism.source, morphism.source, "implicit"))
        if morphism.target not in self.objects:
            self.add_object(CategoryObject(morphism.target, morphism.target, "implicit"))
        self.morphisms.append(morphism)

    def compose_recent(self, limit: int = 20) -> List[Morphism]:
        recent = self.morphisms[-limit:]
        by_source: Dict[str, List[Morphism]] = defaultdict(list)
        for m in recent:
            by_source[m.source].append(m)
        comps: List[Morphism] = []
        for m in recent:
            for nxt in by_source.get(m.target, [])[:2]:
                try:
                    comps.append(m.compose(nxt))
                except ValueError:
                    pass
        return comps

    def identity_law_gap(self, sample: int = 100) -> float:
        if not self.morphisms:
            return 0.0
        subset = self.morphisms[-sample:]
        gaps = []
        for m in subset:
            left = self.identities.get(m.source)
            right = self.identities.get(m.target)
            if left and right and left.source == left.target and right.source == right.target:
                gaps.append(abs(m.truth_value.norm() - m.truth_value.norm()))
        return mean_or(gaps, 0.0)


class EconomicCategory(Category):
    pass


class TruthCategory(Category):
    pass


class LegalCategory(Category):
    pass


class SecurityCategory(Category):
    pass


class UniversalProperty(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.last_gap = 0.0

    @abstractmethod
    def verify(self, category: Category) -> float:
        raise NotImplementedError


class TerminalUniversalProperty(UniversalProperty):
    """UN als terminale Annäherung: jedes Land hat einen Governance-Morphismus zur UN."""

    def __init__(self, terminal_id: str) -> None:
        super().__init__("Terminalobjekt")
        self.terminal_id = terminal_id

    def verify(self, category: Category) -> float:
        objects = [oid for oid in category.objects if oid != self.terminal_id]
        if not objects:
            return 0.0
        hits = 0
        for oid in objects:
            if any(m.source == oid and m.target == self.terminal_id for m in category.morphisms[-2000:]):
                hits += 1
        self.last_gap = 1.0 - safe_div(hits, len(objects), 0.0)
        return self.last_gap


class ProductUniversalProperty(UniversalProperty):
    """Produkt: Fiat- und WK-Bewertung sollen zusammen ein kaufbares Bündel ergeben."""

    def __init__(self) -> None:
        super().__init__("Produktobjekt Fiat×WK")

    def verify(self, category: Category) -> float:
        pairs = [m for m in category.morphisms[-2000:] if abs(m.fiat_value) > 1e-9]
        if not pairs:
            self.last_gap = 0.0
            return 0.0
        gaps = []
        for m in pairs:
            truth_proxy = m.truth_value.positive_score() + 1.0
            fiat_proxy = abs(m.fiat_value) / 1_000_000 + 1.0
            gaps.append(abs(math.log(truth_proxy) - math.log(fiat_proxy)))
        self.last_gap = mean_or(gaps, 0.0)
        return self.last_gap


class PullbackUniversalProperty(UniversalProperty):
    """Pullback: Vertragsrecht und Lieferung sollen denselben realen Kauf referenzieren."""

    def __init__(self) -> None:
        super().__init__("Pullback Vertrag×Lieferung")

    def verify(self, category: Category) -> float:
        recent = category.morphisms[-1500:]
        purchases = [m for m in recent if m.kind == "purchase"]
        audits = [m for m in recent if m.kind == "audit"]
        if not purchases:
            self.last_gap = 0.0
            return 0.0
        audit_targets = {m.target for m in audits}
        covered = sum(1 for p in purchases if p.target in audit_targets or p.source in audit_targets)
        self.last_gap = 1.0 - safe_div(covered, len(purchases), 0.0)
        return self.last_gap


class PushoutUniversalProperty(UniversalProperty):
    """Pushout: Konfliktparteien werden über UN/Sicherheitsmorphismus ko-limitiert."""

    def __init__(self) -> None:
        super().__init__("Pushout Konflikt→Resolution")

    def verify(self, category: Category) -> float:
        recent = category.morphisms[-2000:]
        sanctions = [m for m in recent if m.kind in ("sanction", "defense")]
        resolutions = [m for m in recent if m.kind in ("audit", "governance")]
        if not sanctions:
            self.last_gap = 0.0
            return 0.0
        involved = {m.source for m in sanctions} | {m.target for m in sanctions}
        resolved = {m.source for m in resolutions} | {m.target for m in resolutions}
        self.last_gap = 1.0 - safe_div(len(involved & resolved), len(involved), 0.0)
        return self.last_gap


class EqualizerUniversalProperty(UniversalProperty):
    """Equalizer: soziale und epistemische Wahrheit sollen nicht auseinanderlaufen."""

    def __init__(self) -> None:
        super().__init__("Equalizer sozial=epistemisch")

    def verify(self, category: Category) -> float:
        recent = category.morphisms[-2000:]
        diffs = [abs(m.truth_value[TruthLayer.SOCIAL.value] - m.truth_value[TruthLayer.EPISTEMIC.value]) for m in recent]
        self.last_gap = mean_or(diffs, 0.0)
        return self.last_gap


class Functor(ABC):
    def __init__(self, name: str, source: Category, target: Category) -> None:
        self.name = name
        self.source = source
        self.target = target

    @abstractmethod
    def map_object(self, obj: CategoryObject) -> CategoryObject:
        raise NotImplementedError

    @abstractmethod
    def map_morphism(self, morphism: Morphism) -> Morphism:
        raise NotImplementedError

    def apply_recent(self, limit: int = 200) -> List[Morphism]:
        mapped: List[Morphism] = []
        for obj in self.source.objects.values():
            mapped_obj = self.map_object(obj)
            if mapped_obj.ref_id not in self.target.objects:
                self.target.add_object(mapped_obj)
        for morphism in self.source.morphisms[-limit:]:
            mm = self.map_morphism(morphism)
            self.target.add_morphism(mm)
            mapped.append(mm)
        return mapped


class FiatToTruthFunctor(Functor):
    """Bewertungsfunktor: Fiat-Zahlungen werden als minimale WK-Claims interpretiert."""

    def map_object(self, obj: CategoryObject) -> CategoryObject:
        return CategoryObject(obj.name, obj.ref_id, f"truth({obj.kind})", dict(obj.meta))

    def map_morphism(self, morphism: Morphism) -> Morphism:
        tv = morphism.truth_value.copy()
        fiat_signal = math.log1p(abs(morphism.fiat_value)) * 0.18
        tv[TruthLayer.LIQUIDITY.value] += fiat_signal
        tv[TruthLayer.SOCIAL.value] += fiat_signal * 0.55
        tv[TruthLayer.CAUSAL.value] += fiat_signal * 0.35
        return Morphism(morphism.source, morphism.target, f"F({morphism.name})", morphism.kind, morphism.fiat_value, tv, {"functor": self.name})


class LegalityFunctor(Functor):
    """Rechtsfunktor: Morphismen werden nach Legalität/Souveränität gewichtet."""

    def map_object(self, obj: CategoryObject) -> CategoryObject:
        return CategoryObject(obj.name, obj.ref_id, f"legal({obj.kind})", dict(obj.meta))

    def map_morphism(self, morphism: Morphism) -> Morphism:
        tv = TruthVector.zero()
        tv[TruthLayer.LEGAL.value] = max(0.0, morphism.truth_value[TruthLayer.LEGAL.value]) + 1.0
        tv[TruthLayer.SOVEREIGNTY.value] = morphism.truth_value[TruthLayer.SOVEREIGNTY.value]
        tv[TruthLayer.EPISTEMIC.value] = morphism.truth_value[TruthLayer.EPISTEMIC.value] * 0.5
        return Morphism(morphism.source, morphism.target, f"L({morphism.name})", morphism.kind, morphism.fiat_value, tv, {"functor": self.name})


class SecurityFunctor(Functor):
    """Sicherheitsfunktor: Sicherheits-/Risikoanteile einer Transaktion."""

    def map_object(self, obj: CategoryObject) -> CategoryObject:
        return CategoryObject(obj.name, obj.ref_id, f"security({obj.kind})", dict(obj.meta))

    def map_morphism(self, morphism: Morphism) -> Morphism:
        tv = TruthVector.zero()
        tv[TruthLayer.SECURITY.value] = morphism.truth_value[TruthLayer.SECURITY.value]
        tv[TruthLayer.RISK_REDUCTION.value] = morphism.truth_value[TruthLayer.RISK_REDUCTION.value]
        tv[TruthLayer.NETWORK_REACHABILITY.value] = morphism.truth_value[TruthLayer.NETWORK_REACHABILITY.value]
        return Morphism(morphism.source, morphism.target, f"S({morphism.name})", morphism.kind, morphism.fiat_value, tv, {"functor": self.name})


class NaturalTransformation:
    """Natürliche Transformation η: F ⇒ G.

    In der Simulation ist sie kein Beweisassistent, sondern ein Kohärenz-Instrument:
    Je größer die Differenz der Komponenten η_X, desto größer die Bewertungsblase
    zwischen zwei Paradigmen, etwa Fiat→WK und Legal→WK.
    """

    def __init__(self, name: str, F: Functor, G: Functor) -> None:
        self.name = name
        self.F = F
        self.G = G
        self.components: Dict[str, Morphism] = {}
        self.last_naturality_gap = 0.0

    def build_components(self) -> None:
        shared = set(self.F.source.objects) & set(self.G.source.objects)
        for oid in shared:
            tv = TruthVector.zero()
            tv[TruthLayer.CATEGORY_COHERENCE.value] = 1.0
            self.components[oid] = Morphism(oid, oid, f"η_{oid[:5]}", "natural_component", truth_value=tv)

    def evaluate_gap(self, limit: int = 300) -> float:
        morphisms = self.F.source.morphisms[-limit:]
        if not morphisms:
            self.last_naturality_gap = 0.0
            return 0.0
        gaps = []
        for m in morphisms:
            fm = self.F.map_morphism(m)
            gm = self.G.map_morphism(m)
            gaps.append(abs(fm.truth_value.weighted_score() - gm.truth_value.weighted_score()))
        self.last_naturality_gap = mean_or(gaps, 0.0)
        return self.last_naturality_gap


# =============================================================================
# 5. Topologische Räume, Prägarben und Garben
# =============================================================================


@dataclass(frozen=True)
class OpenSet:
    name: str
    members: FrozenSet[str]

    def intersect(self, other: "OpenSet") -> "OpenSet":
        return OpenSet(f"{self.name}∩{other.name}", frozenset(self.members & other.members))

    def is_subset_of(self, other: "OpenSet") -> bool:
        return self.members.issubset(other.members)


class TopologicalSpace:
    def __init__(self, name: str) -> None:
        self.name = name
        self.opens: Dict[str, OpenSet] = {}

    def add_open(self, open_set: OpenSet) -> None:
        self.opens[open_set.name] = open_set

    def ensure_intersections(self, limit: int = 600) -> None:
        names = list(self.opens)
        added = 0
        for i, a_name in enumerate(names):
            for b_name in names[i + 1:]:
                if added >= limit:
                    return
                inter = self.opens[a_name].intersect(self.opens[b_name])
                if inter.members and inter.name not in self.opens:
                    self.add_open(inter)
                    added += 1

    def cover(self, target: OpenSet, max_parts: int = 12) -> List[OpenSet]:
        candidates = [o for o in self.opens.values() if o.members and o.members.issubset(target.members) and o != target]
        candidates.sort(key=lambda o: len(o.members), reverse=True)
        covered: set[str] = set()
        out: List[OpenSet] = []
        for o in candidates:
            if len(out) >= max_parts:
                break
            if not o.members.issubset(covered):
                out.append(o)
                covered |= set(o.members)
            if covered >= set(target.members):
                break
        return out or [target]


@dataclass
class Section:
    open_set: OpenSet
    truth: TruthVector
    fiat_mass: float
    annotations: Dict[str, Any] = field(default_factory=dict)


class Presheaf(ABC):
    def __init__(self, name: str, space: TopologicalSpace) -> None:
        self.name = name
        self.space = space
        self.sections: Dict[str, Section] = {}

    @abstractmethod
    def assign(self, agents: Dict[str, "Agent"]) -> None:
        raise NotImplementedError

    def restrict(self, from_open: OpenSet, to_open: OpenSet) -> Optional[Section]:
        if not to_open.is_subset_of(from_open):
            return None
        sec = self.sections.get(from_open.name)
        if not sec:
            return None
        ratio = safe_div(len(to_open.members), max(1, len(from_open.members)), 0.0)
        return Section(to_open, sec.truth.scaled(ratio), sec.fiat_mass * ratio, {"restricted_from": from_open.name})


class LocalTruthPresheaf(Presheaf):
    def assign(self, agents: Dict[str, "Agent"]) -> None:
        self.sections.clear()
        for o in self.space.opens.values():
            tv = TruthVector.zero()
            fiat = 0.0
            count = 0
            for aid in o.members:
                agent = agents.get(aid)
                if not agent:
                    continue
                tv.add(agent.truth)
                fiat += agent.total_fiat()
                count += 1
            if count > 0:
                tv.scale(1.0 / count)
                fiat /= count
            self.sections[o.name] = Section(o, tv, fiat, {"count": count})


class Sheaf(LocalTruthPresheaf):
    def compatible(self, a: Section, b: Section, tolerance: float = 250.0) -> bool:
        inter = a.open_set.intersect(b.open_set)
        if not inter.members:
            return True
        ra = self.restrict(a.open_set, inter)
        rb = self.restrict(b.open_set, inter)
        if not ra or not rb:
            return True
        return abs(ra.truth.weighted_score() - rb.truth.weighted_score()) <= tolerance

    def glue(self, target: OpenSet, cover: Sequence[OpenSet]) -> Tuple[Section, float]:
        sections = [self.sections[o.name] for o in cover if o.name in self.sections]
        if not sections:
            return Section(target, TruthVector.zero(), 0.0, {"glued": False}), 0.0
        tv = TruthVector.zero()
        fiat = 0.0
        total_members = 0
        incompatibilities = 0
        checks = 0
        for sec in sections:
            w = max(1, len(sec.open_set.members))
            tv.add(sec.truth, factor=w)
            fiat += sec.fiat_mass * w
            total_members += w
        for i, a in enumerate(sections):
            for b in sections[i + 1:]:
                checks += 1
                if not self.compatible(a, b):
                    incompatibilities += 1
        if total_members:
            tv.scale(1.0 / total_members)
            fiat /= total_members
        gap = safe_div(incompatibilities, checks, 0.0)
        tv[TruthLayer.SHEAF_CONSISTENCY.value] += (1.0 - gap) * 20.0
        glued = Section(target, tv, fiat, {"glued": True, "cover_size": len(sections), "gap": gap})
        self.sections[target.name] = glued
        return glued, gap


class GrothendieckTopology(TopologicalSpace):
    """Benannter Spezialfall: Coverings werden nicht nur durch Mengen, sondern durch Institutionen erzeugt."""

    def __init__(self, name: str = "Planetary Grothendieck Site") -> None:
        super().__init__(name)
        self.covering_families: Dict[str, List[List[str]]] = defaultdict(list)

    def add_covering_family(self, target: str, family: List[str]) -> None:
        self.covering_families[target].append(family)




def _sheaf_assign_chunk(payload: Tuple[List[Tuple[str, Tuple[str, ...]]], Dict[str, Tuple[Dict[str, float], float]]]) -> List[Tuple[str, Dict[str, float], float, int]]:
    open_specs, agent_snapshot = payload
    out: List[Tuple[str, Dict[str, float], float, int]] = []
    for open_name, members in open_specs:
        values = {layer: 0.0 for layer in ALL_TRUTH_LAYERS}
        fiat = 0.0
        count = 0
        for aid in members:
            data = agent_snapshot.get(aid)
            if data is None:
                continue
            truth_values, fiat_value = data
            for layer in ALL_TRUTH_LAYERS:
                values[layer] += truth_values.get(layer, 0.0)
            fiat += fiat_value
            count += 1
        if count > 0:
            inv = 1.0 / count
            for layer in ALL_TRUTH_LAYERS:
                values[layer] *= inv
            fiat *= inv
        out.append((open_name, values, fiat, count))
    return out


# =============================================================================
# 6. Domänenobjekte, Akteure und Klassenvererbung
# =============================================================================


class SimNode:
    def __init__(self, name: str) -> None:
        self.id = uid(self.__class__.__name__.lower())
        self.name = name
        self.tags: set[str] = set()

    def label(self) -> str:
        return f"{self.name}<{self.__class__.__name__}>"


class TruthBearer:
    def __init__(self) -> None:
        self.truth = TruthVector.zero()

    def truth_score(self) -> float:
        return self.truth.weighted_score()

    def truth_debt(self) -> float:
        return self.truth.debt_score()


class FiatBearer:
    def __init__(self) -> None:
        self.fiat: Dict[str, float] = defaultdict(float)
        self.debt: Dict[str, float] = defaultdict(float)

    def total_fiat(self) -> float:
        return sum(self.fiat.values())

    def total_debt(self) -> float:
        return sum(self.debt.values())

    def receive_fiat(self, currency: str, amount: float) -> None:
        self.fiat[currency] += amount

    def pay_fiat(self, currency: str, amount: float) -> float:
        paid = min(max(0.0, amount), self.fiat[currency])
        self.fiat[currency] -= paid
        if paid < amount:
            self.debt[currency] += amount - paid
            self.truth[TruthLayer.LIQUIDITY.value] -= math.log1p(amount - paid)
            self.truth[TruthLayer.TEMPORAL.value] -= 0.4 * math.log1p(amount - paid)
        return paid


class QueueOwner:
    def __init__(self) -> None:
        self.inbox: MessageQueue = FIFOQueue("inbox")
        self.outbox: MessageQueue = LIFOQueue("outbox")
        self.priority_box: MessageQueue = PriorityMessageQueue("priority")

    def enqueue_inbox(self, msg: NetworkMessage) -> None:
        self.inbox.push(msg)


class NetworkParticipant:
    def __init__(self) -> None:
        self.network_ids: set[str] = set()

    def join_network(self, network: Network) -> None:
        network.add_node(self)  # type: ignore[arg-type]
        self.network_ids.add(network.name)


class Agent(SimNode, TruthBearer, FiatBearer, QueueOwner, NetworkParticipant):
    def __init__(self, name: str, home_currency: str) -> None:
        SimNode.__init__(self, name)
        TruthBearer.__init__(self)
        FiatBearer.__init__(self)
        QueueOwner.__init__(self)
        NetworkParticipant.__init__(self)
        self.home_currency = home_currency
        self.reputation = 1.0
        self.population_weight = 1.0
        self.risk_appetite = 0.5
        self.received_messages = 0

    def month_passes(self, rng: random.Random) -> None:
        self.truth.decay_one_month()
        for cur, debt in list(self.debt.items()):
            if debt > 0:
                interest = debt * rng.uniform(0.002, 0.018)
                self.debt[cur] += interest
                self.truth[TruthLayer.TEMPORAL.value] -= math.log1p(interest)

    def decide_messages(self, sim: "PlanetaryParadigmSimulation") -> List[Tuple[str, NetworkMessage]]:
        return []

    def handle_message(self, message: NetworkMessage, sim: "PlanetaryParadigmSimulation") -> None:
        self.received_messages += 1
        if message.kind == MessageKind.KNOWLEDGE:
            self.truth.add(message.truth, 0.25)
        elif message.kind == MessageKind.SHEAF_PATCH:
            self.truth[TruthLayer.SHEAF_CONSISTENCY.value] += 0.8
        else:
            self.truth.add(message.truth, 0.05)


class LegalEntity(Agent):
    def __init__(self, name: str, home_currency: str) -> None:
        super().__init__(name, home_currency)
        self.legal_status = "recognized"
        self.truth[TruthLayer.LEGAL.value] += 10.0


class InstitutionalEntity(LegalEntity):
    def __init__(self, name: str, home_currency: str) -> None:
        super().__init__(name, home_currency)
        self.mandate = "institutional"
        self.truth[TruthLayer.SOCIAL.value] += 8.0
        self.truth[TruthLayer.EPISTEMIC.value] += 4.0


class SovereignEntity(InstitutionalEntity):
    def __init__(self, name: str, home_currency: str) -> None:
        super().__init__(name, home_currency)
        self.truth[TruthLayer.SOVEREIGNTY.value] += 30.0
        self.tax_rate = 0.18


class Country(SovereignEntity):
    def __init__(self, name: str, currency: str, region: str, population: float, gdp: float) -> None:
        super().__init__(name, currency)
        self.currency = currency
        self.region = region
        self.population = population
        self.gdp = gdp
        self.stability = random.random()
        self.inflation = 0.03
        self.unemployment = 0.06
        self.defense_posture = random.random()
        self.alliances: set[str] = set()
        self.receive_fiat(currency, gdp * 0.15)
        self.truth[TruthLayer.EXISTENCE.value] += 50.0
        self.truth[TruthLayer.INFRASTRUCTURE.value] += math.log1p(gdp) * 2.5
        self.truth[TruthLayer.SHELTER.value] += math.log1p(population) * 3.0
        self.truth[TruthLayer.FOOD.value] += math.log1p(population) * 2.0
        self.tags.add("country")

    def collect_tax(self, agents: Iterable[Agent]) -> float:
        tax = 0.0
        for a in agents:
            if a is self or a.home_currency != self.currency:
                continue
            base = max(0.0, a.total_fiat()) * self.tax_rate * 0.002
            paid = a.pay_fiat(self.currency, base)
            tax += paid
        self.receive_fiat(self.currency, tax)
        self.gdp += tax * 0.15
        self.truth[TruthLayer.LEGAL.value] += math.log1p(tax) * 0.03
        return tax

    def spend_public_goods(self, rng: random.Random) -> TruthVector:
        spend = self.pay_fiat(self.currency, self.gdp * rng.uniform(0.0004, 0.0015))
        tv = TruthVector.zero()
        tv[TruthLayer.INFRASTRUCTURE.value] += math.log1p(spend) * rng.uniform(0.5, 1.2)
        tv[TruthLayer.HEALTH.value] += math.log1p(spend) * rng.uniform(0.1, 0.6)
        tv[TruthLayer.EDUCATION.value] += math.log1p(spend) * rng.uniform(0.1, 0.8)
        tv[TruthLayer.SHEAF_CONSISTENCY.value] += rng.uniform(0, 1.5)
        self.truth.add(tv)
        return tv

    def month_passes(self, rng: random.Random) -> None:
        super().month_passes(rng)
        self.inflation = clamp(self.inflation + rng.gauss(0.0, 0.004), -0.03, 0.35)
        self.unemployment = clamp(self.unemployment + rng.gauss(0.0, 0.006), 0.01, 0.45)
        self.stability = clamp(self.stability + rng.gauss(0.0, 0.01) - self.unemployment * 0.002, 0.0, 1.0)
        self.gdp *= 1.0 + rng.gauss(0.002, 0.006) - self.inflation * 0.01
        self.truth[TruthLayer.SOCIAL.value] += (self.stability - 0.5) * 0.5
        if self.inflation > 0.12:
            self.truth[TruthLayer.LIQUIDITY.value] -= (self.inflation - 0.12) * 10


class FinancialInstitution(InstitutionalEntity):
    def __init__(self, name: str, home_currency: str) -> None:
        super().__init__(name, home_currency)
        self.capital_ratio = 0.12
        self.reserve_ratio = 0.10
        self.truth[TruthLayer.LIQUIDITY.value] += 20.0
        self.tags.add("financial")

    def issue_loan(self, borrower: Agent, amount: float, rng: random.Random) -> NetworkMessage:
        currency = borrower.home_currency
        self.receive_fiat(currency, -amount)
        borrower.receive_fiat(currency, amount)
        borrower.debt[currency] += amount * rng.uniform(1.01, 1.08)
        tv = TruthVector.zero()
        tv[TruthLayer.LIQUIDITY.value] += math.log1p(amount) * 0.4
        tv[TruthLayer.TEMPORAL.value] -= math.log1p(amount) * 0.15
        tv[TruthLayer.POTENTIAL.value] += math.log1p(amount) * 0.25
        borrower.truth.add(tv)
        bank_tv = TruthVector.zero()
        bank_tv[TruthLayer.LEGAL.value] += math.log1p(amount) * 0.05
        bank_tv[TruthLayer.RISK_REDUCTION.value] -= math.log1p(amount) * 0.03
        self.truth.add(bank_tv)
        return NetworkMessage(self.id, borrower.id, MessageKind.CREDIT, amount, currency, tv, {"loan": amount}, priority=2.0)


class CentralBank(FinancialInstitution):
    def __init__(self, country: Country) -> None:
        super().__init__(f"Central Bank of {country.name}", country.currency)
        self.country_id = country.id
        self.policy_rate = 0.035
        self.reserve_ratio = 0.12
        self.mandate = "price stability and currency ontology"
        self.truth[TruthLayer.LEGAL.value] += 20.0
        self.tags.add("central_bank")

    def set_policy(self, country: Country, rng: random.Random) -> None:
        target = 0.025
        self.policy_rate = clamp(self.policy_rate + 0.22 * (country.inflation - target) + rng.gauss(0, 0.002), -0.01, 0.25)
        if country.inflation > 0.08:
            self.truth[TruthLayer.EPISTEMIC.value] += 0.3
            country.truth[TruthLayer.LIQUIDITY.value] -= 0.2
        else:
            country.truth[TruthLayer.LIQUIDITY.value] += 0.2


class CommercialBank(FinancialInstitution):
    def __init__(self, name: str, home_currency: str) -> None:
        super().__init__(name, home_currency)
        self.loan_book = 0.0
        self.tags.add("commercial_bank")

    def decide_messages(self, sim: "PlanetaryParadigmSimulation") -> List[Tuple[str, NetworkMessage]]:
        if sim.rng.random() > 0.20:
            return []
        candidates = [a for a in sim.agents.values() if isinstance(a, (Company, Country)) and a.home_currency == self.home_currency and a.id != self.id]
        if not candidates:
            return []
        borrower = sim.rng.choice(candidates)
        amount = max(10_000.0, sim.rng.lognormvariate(11.0, 0.9))
        self.loan_book += amount
        msg = NetworkMessage(self.id, borrower.id, MessageKind.CREDIT, amount, self.home_currency, TruthVector.zero(), {"requested_loan": amount}, priority=2.0)
        return [("credit", msg)]


class DevelopmentBank(CommercialBank):
    def decide_messages(self, sim: "PlanetaryParadigmSimulation") -> List[Tuple[str, NetworkMessage]]:
        out = super().decide_messages(sim)
        for _, msg in out:
            msg.truth[TruthLayer.INFRASTRUCTURE.value] += 8.0
            msg.truth[TruthLayer.POTENTIAL.value] += 6.0
        return out


class InvestmentBank(CommercialBank):
    def decide_messages(self, sim: "PlanetaryParadigmSimulation") -> List[Tuple[str, NetworkMessage]]:
        out = super().decide_messages(sim)
        for _, msg in out:
            msg.truth[TruthLayer.COMPARATIVE.value] += 6.0
            msg.truth[TruthLayer.POTENTIAL.value] += 9.0
            msg.priority += 0.5
        return out


class UnitedNations(InstitutionalEntity):
    def __init__(self) -> None:
        super().__init__("United Nations / Planetary Truth Council", "WK")
        self.mandate = "planetary gluing of local truths"
        self.truth[TruthLayer.SHEAF_CONSISTENCY.value] += 50.0
        self.truth[TruthLayer.CATEGORY_COHERENCE.value] += 40.0
        self.tags.add("un")

    def decide_messages(self, sim: "PlanetaryParadigmSimulation") -> List[Tuple[str, NetworkMessage]]:
        out: List[Tuple[str, NetworkMessage]] = []
        countries = [a for a in sim.agents.values() if isinstance(a, Country)]
        if not countries:
            return out
        worst = sorted(countries, key=lambda c: c.truth_score())[: max(1, len(countries) // 10)]
        for c in worst[:3]:
            tv = TruthVector.zero()
            tv[TruthLayer.EPISTEMIC.value] += 8.0
            tv[TruthLayer.LEGAL.value] += 4.0
            tv[TruthLayer.SHEAF_CONSISTENCY.value] += 6.0
            tv[TruthLayer.SOCIAL.value] += 2.0
            msg = NetworkMessage(self.id, c.id, MessageKind.AUDIT, 0.0, "WK", tv, {"audit": "truth-stack review"}, priority=5.0)
            out.append(("governance", msg))
        return out


class DefenseOrganization(InstitutionalEntity):
    def __init__(self, name: str, home_currency: str = "WK") -> None:
        super().__init__(name, home_currency)
        self.members: set[str] = set()
        self.readiness = random.random()
        self.truth[TruthLayer.SECURITY.value] += 35.0
        self.tags.add("defense_org")

    def add_member(self, country: Country) -> None:
        self.members.add(country.id)
        country.alliances.add(self.id)

    def decide_messages(self, sim: "PlanetaryParadigmSimulation") -> List[Tuple[str, NetworkMessage]]:
        out = []
        if sim.rng.random() > 0.28 or not self.members:
            return out
        country_id = sim.rng.choice(list(self.members))
        tv = TruthVector.zero()
        tv[TruthLayer.SECURITY.value] += 4.0 + 8.0 * self.readiness
        tv[TruthLayer.RISK_REDUCTION.value] += 3.0
        tv[TruthLayer.SOVEREIGNTY.value] += 1.5
        out.append(("defense", NetworkMessage(self.id, country_id, MessageKind.DEFENSE, truth=tv, priority=3.5)))
        return out


class MutualDefensePact(DefenseOrganization):
    pass


class MaritimeSecurityLeague(DefenseOrganization):
    def __init__(self, name: str, home_currency: str = "WK") -> None:
        super().__init__(name, home_currency)
        self.truth[TruthLayer.LOGISTICS.value] += 20.0


class CyberDefenseCompact(DefenseOrganization):
    def __init__(self, name: str, home_currency: str = "WK") -> None:
        super().__init__(name, home_currency)
        self.truth[TruthLayer.EPISTEMIC.value] += 20.0
        self.truth[TruthLayer.NETWORK_REACHABILITY.value] += 25.0


class EconomicEntity(LegalEntity):
    def __init__(self, name: str, home_currency: str) -> None:
        super().__init__(name, home_currency)
        self.productivity = random.uniform(0.5, 1.5)
        self.tags.add("economic")


class Household(EconomicEntity):
    def __init__(self, name: str, home_currency: str, population: float) -> None:
        super().__init__(name, home_currency)
        self.population_weight = population
        self.truth[TruthLayer.SHELTER.value] += 5.0
        self.truth[TruthLayer.HEALTH.value] += 4.0


class Company(EconomicEntity):
    def __init__(self, name: str, home_currency: str, sector: str) -> None:
        super().__init__(name, home_currency)
        self.sector = sector
        self.inventory_truth = TruthVector.zero()
        self.revenue = 0.0
        self.costs = 0.0
        self.employees = random.randint(20, 5000)
        self.truth[TruthLayer.CAUSAL.value] += 8.0
        self.tags.add("company")

    def produce(self, rng: random.Random) -> TruthVector:
        base = rng.lognormvariate(2.4, 0.5) * self.productivity
        tv = sector_truth_vector(self.sector, base)
        self.inventory_truth.add(tv)
        self.truth.add(tv, 0.08)
        self.costs += base * rng.uniform(5000, 60000)
        return tv

    def decide_messages(self, sim: "PlanetaryParadigmSimulation") -> List[Tuple[str, NetworkMessage]]:
        out: List[Tuple[str, NetworkMessage]] = []
        if sim.rng.random() > 0.55:
            return out
        targets = [a for a in sim.agents.values() if isinstance(a, (Company, Country, Household)) and a.id != self.id]
        if not targets:
            return out
        target = sim.rng.choice(targets)
        amount = sim.rng.lognormvariate(10.0, 1.0) * self.productivity
        tv = sector_truth_vector(self.sector, math.log1p(amount) * 0.8)
        tv[TruthLayer.NETWORK_REACHABILITY.value] += 1.0
        msg = NetworkMessage(self.id, target.id, MessageKind.TRADE, amount, self.home_currency, tv, {"sector": self.sector}, priority=1.0)
        out.append(("trade", msg))
        return out


class ProductiveCompany(Company):
    pass


class CivilianCompany(ProductiveCompany):
    pass


class IndustrialCompany(ProductiveCompany):
    def produce(self, rng: random.Random) -> TruthVector:
        tv = super().produce(rng)
        tv[TruthLayer.INFRASTRUCTURE.value] += rng.uniform(1.0, 6.0)
        tv[TruthLayer.ENERGY.value] += rng.uniform(0.5, 5.0)
        self.inventory_truth.add(tv, 0.25)
        return tv


class StrategicCompany(ProductiveCompany):
    def produce(self, rng: random.Random) -> TruthVector:
        tv = super().produce(rng)
        tv[TruthLayer.SECURITY.value] += rng.uniform(2.0, 8.0)
        tv[TruthLayer.SOVEREIGNTY.value] += rng.uniform(1.0, 5.0)
        self.inventory_truth.add(tv, 0.35)
        return tv


class PlatformCompany(CivilianCompany):
    def produce(self, rng: random.Random) -> TruthVector:
        tv = super().produce(rng)
        tv[TruthLayer.ATTENTION.value] += rng.uniform(3.0, 12.0)
        tv[TruthLayer.NETWORK_REACHABILITY.value] += rng.uniform(4.0, 10.0)
        self.inventory_truth.add(tv, 0.2)
        return tv


class MediaCompany(CivilianCompany):
    def produce(self, rng: random.Random) -> TruthVector:
        tv = super().produce(rng)
        tv[TruthLayer.PERCEPTION.value] += rng.uniform(4.0, 14.0)
        tv[TruthLayer.MEMORY.value] += rng.uniform(1.0, 8.0)
        self.inventory_truth.add(tv, 0.2)
        return tv


class ResearchCompany(CivilianCompany):
    def produce(self, rng: random.Random) -> TruthVector:
        tv = super().produce(rng)
        tv[TruthLayer.EPISTEMIC.value] += rng.uniform(6.0, 18.0)
        tv[TruthLayer.POTENTIAL.value] += rng.uniform(5.0, 20.0)
        self.inventory_truth.add(tv, 0.2)
        return tv


class EconomicObject(SimNode, TruthBearer):
    def __init__(self, name: str, owner_id: str) -> None:
        SimNode.__init__(self, name)
        TruthBearer.__init__(self)
        self.owner_id = owner_id


class Asset(EconomicObject):
    pass


class Claim(EconomicObject):
    def __init__(self, name: str, owner_id: str, debtor_id: str, amount: float, currency: str) -> None:
        super().__init__(name, owner_id)
        self.debtor_id = debtor_id
        self.amount = amount
        self.currency = currency
        self.truth[TruthLayer.LEGAL.value] += math.log1p(amount)
        self.truth[TruthLayer.TEMPORAL.value] -= math.log1p(amount) * 0.2


class Product(EconomicObject):
    def __init__(self, name: str, owner_id: str, sector: str, price: float, currency: str) -> None:
        super().__init__(name, owner_id)
        self.sector = sector
        self.price = price
        self.currency = currency
        self.truth.add(sector_truth_vector(sector, math.log1p(price)))


SECTORS = [
    "food", "housing", "mobility", "energy", "health", "education", "defense", "software", "media",
    "luxury", "research", "construction", "insurance", "law", "logistics", "finance", "agriculture",
    "tourism", "semiconductors", "water", "culture", "space", "cybersecurity", "biotech",
]

SECTOR_LAYER_MAP: Dict[str, List[str]] = {
    "food": [TruthLayer.FOOD.value, TruthLayer.HEALTH.value, TruthLayer.EXISTENCE.value],
    "housing": [TruthLayer.SHELTER.value, TruthLayer.LEGAL.value, TruthLayer.SOCIAL.value],
    "mobility": [TruthLayer.LOGISTICS.value, TruthLayer.TEMPORAL.value, TruthLayer.CAUSAL.value],
    "energy": [TruthLayer.ENERGY.value, TruthLayer.INFRASTRUCTURE.value, TruthLayer.CAUSAL.value],
    "health": [TruthLayer.HEALTH.value, TruthLayer.RISK_REDUCTION.value, TruthLayer.EPISTEMIC.value],
    "education": [TruthLayer.EDUCATION.value, TruthLayer.POTENTIAL.value, TruthLayer.EPISTEMIC.value],
    "defense": [TruthLayer.SECURITY.value, TruthLayer.SOVEREIGNTY.value, TruthLayer.RISK_REDUCTION.value],
    "software": [TruthLayer.CAUSAL.value, TruthLayer.NETWORK_REACHABILITY.value, TruthLayer.POTENTIAL.value],
    "media": [TruthLayer.PERCEPTION.value, TruthLayer.ATTENTION.value, TruthLayer.MEMORY.value],
    "luxury": [TruthLayer.COMPARATIVE.value, TruthLayer.PERCEPTION.value, TruthLayer.SOCIAL.value],
    "research": [TruthLayer.EPISTEMIC.value, TruthLayer.POTENTIAL.value, TruthLayer.CATEGORY_COHERENCE.value],
    "construction": [TruthLayer.INFRASTRUCTURE.value, TruthLayer.SHELTER.value, TruthLayer.CAUSAL.value],
    "insurance": [TruthLayer.RISK_REDUCTION.value, TruthLayer.LEGAL.value, TruthLayer.LIQUIDITY.value],
    "law": [TruthLayer.LEGAL.value, TruthLayer.EPISTEMIC.value, TruthLayer.SOVEREIGNTY.value],
    "logistics": [TruthLayer.LOGISTICS.value, TruthLayer.TEMPORAL.value, TruthLayer.NETWORK_REACHABILITY.value],
    "finance": [TruthLayer.LIQUIDITY.value, TruthLayer.TEMPORAL.value, TruthLayer.POTENTIAL.value],
    "agriculture": [TruthLayer.FOOD.value, TruthLayer.ECOLOGICAL.value, TruthLayer.EXISTENCE.value],
    "tourism": [TruthLayer.MEMORY.value, TruthLayer.ATTENTION.value, TruthLayer.PERCEPTION.value],
    "semiconductors": [TruthLayer.INFRASTRUCTURE.value, TruthLayer.POTENTIAL.value, TruthLayer.NETWORK_REACHABILITY.value],
    "water": [TruthLayer.EXISTENCE.value, TruthLayer.HEALTH.value, TruthLayer.ECOLOGICAL.value],
    "culture": [TruthLayer.MEMORY.value, TruthLayer.SOCIAL.value, TruthLayer.PERCEPTION.value],
    "space": [TruthLayer.POTENTIAL.value, TruthLayer.SOVEREIGNTY.value, TruthLayer.EPISTEMIC.value],
    "cybersecurity": [TruthLayer.SECURITY.value, TruthLayer.NETWORK_REACHABILITY.value, TruthLayer.EPISTEMIC.value],
    "biotech": [TruthLayer.HEALTH.value, TruthLayer.EPISTEMIC.value, TruthLayer.POTENTIAL.value],
}


def sector_truth_vector(sector: str, scale: float) -> TruthVector:
    tv = TruthVector.zero()
    layers = SECTOR_LAYER_MAP.get(sector, [TruthLayer.CAUSAL.value, TruthLayer.SOCIAL.value])
    for i, layer in enumerate(layers):
        tv[layer] += scale * (1.0 - 0.18 * i)
    tv[TruthLayer.EXISTENCE.value] += scale * 0.18
    tv[TruthLayer.LEGAL.value] += scale * 0.07
    return tv




# =============================================================================
# 6b. Prozess-Worker: PyPy3-Parallelität ohne Threads
# =============================================================================


def _agent_month_passes_worker(payload: Tuple[Agent, int]) -> Tuple[str, Agent]:
    agent, seed = payload
    rng = random.Random(seed)
    agent.month_passes(rng)
    return agent.id, agent


def _company_production_worker(payload: Tuple[Company, Tuple[str, ...], int]) -> Tuple[str, Company, List[NetworkMessage]]:
    company, target_ids, seed = payload
    rng = random.Random(seed)
    company.produce(rng)
    messages: List[NetworkMessage] = []
    if target_ids and rng.random() <= 0.55:
        target_id = rng.choice(target_ids)
        if target_id == company.id and len(target_ids) > 1:
            target_id = rng.choice([tid for tid in target_ids if tid != company.id])
        if target_id != company.id:
            amount = rng.lognormvariate(10.0, 1.0) * company.productivity
            tv = sector_truth_vector(company.sector, math.log1p(amount) * 0.8)
            tv[TruthLayer.NETWORK_REACHABILITY.value] += 1.0
            messages.append(NetworkMessage(company.id, target_id, MessageKind.TRADE, amount, company.home_currency, tv, {"sector": company.sector}, priority=1.0))
    return company.id, company, messages


def _credit_bank_worker(payload: Tuple[CommercialBank, int, Optional[str]]) -> Tuple[str, CommercialBank, List[NetworkMessage]]:
    bank, seed, borrower_id = payload
    rng = random.Random(seed)
    messages: List[NetworkMessage] = []
    if borrower_id and rng.random() <= 0.20:
        amount = max(10_000.0, rng.lognormvariate(11.0, 0.9))
        bank.loan_book += amount
        tv = TruthVector.zero()
        priority = 2.0
        if isinstance(bank, DevelopmentBank):
            tv[TruthLayer.INFRASTRUCTURE.value] += 8.0
            tv[TruthLayer.POTENTIAL.value] += 6.0
        if isinstance(bank, InvestmentBank):
            tv[TruthLayer.COMPARATIVE.value] += 6.0
            tv[TruthLayer.POTENTIAL.value] += 9.0
            priority += 0.5
        messages.append(NetworkMessage(bank.id, borrower_id, MessageKind.CREDIT, amount, bank.home_currency, tv, {"requested_loan": amount}, priority=priority))
    return bank.id, bank, messages


def _labor_company_worker(payload: Tuple[Company, str, int]) -> Tuple[str, Company, str, float, TruthVector]:
    company, country_id, seed = payload
    rng = random.Random(seed)
    wage = company.employees * rng.uniform(500, 5000)
    paid = company.pay_fiat(company.home_currency, wage)
    tv = TruthVector.zero()
    tv[TruthLayer.CAUSAL.value] += math.log1p(company.employees) * 0.05
    tv[TruthLayer.SOCIAL.value] += math.log1p(paid) * 0.02
    company.truth.add(tv)
    return company.id, company, country_id, paid * 0.05, tv.scaled(0.3)


def _agent_month_passes_batch_worker(payload: List[Tuple[Agent, int]]) -> List[Tuple[str, Agent]]:
    return [_agent_month_passes_worker(item) for item in payload]


def _company_production_batch_worker(payload: List[Tuple[Company, Tuple[str, ...], int]]) -> List[Tuple[str, Company, List[NetworkMessage]]]:
    return [_company_production_worker(item) for item in payload]


def _credit_bank_batch_worker(payload: List[Tuple[CommercialBank, int, Optional[str]]]) -> List[Tuple[str, CommercialBank, List[NetworkMessage]]]:
    return [_credit_bank_worker(item) for item in payload]


def _labor_company_batch_worker(payload: List[Tuple[Company, str, int]]) -> List[Tuple[str, Company, str, float, TruthVector]]:
    return [_labor_company_worker(item) for item in payload]


def _country_tax_assessment_worker(payload: Tuple[str, str, float, List[Tuple[str, float]]]) -> Tuple[str, str, List[Tuple[str, str, float]]]:
    country_id, currency, tax_rate, rows = payload
    assessments: List[Tuple[str, str, float]] = []
    for agent_id, total_fiat in rows:
        if agent_id == country_id:
            continue
        base = max(0.0, total_fiat) * tax_rate * 0.002
        if base > 0.0:
            assessments.append((agent_id, currency, base))
    return country_id, currency, assessments


def _country_public_goods_worker(payload: Tuple[Country, int]) -> Tuple[str, Country]:
    country, seed = payload
    rng = random.Random(seed)
    country.spend_public_goods(rng)
    return country.id, country


def _central_bank_policy_worker(payload: Tuple[CentralBank, Country, int]) -> Tuple[str, CentralBank, str, Country]:
    central_bank, country, seed = payload
    rng = random.Random(seed)
    central_bank.set_policy(country, rng)
    return central_bank.id, central_bank, country.id, country


def _defense_org_decision_worker(payload: Tuple[DefenseOrganization, int]) -> Tuple[str, List[Tuple[str, NetworkMessage]]]:
    org, seed = payload
    rng = random.Random(seed)
    out: List[Tuple[str, NetworkMessage]] = []
    if rng.random() > 0.28 or not org.members:
        return org.id, out
    country_id = rng.choice(list(org.members))
    tv = TruthVector.zero()
    tv[TruthLayer.SECURITY.value] += 4.0 + 8.0 * org.readiness
    tv[TruthLayer.RISK_REDUCTION.value] += 3.0
    tv[TruthLayer.SOVEREIGNTY.value] += 1.5
    out.append(("defense", NetworkMessage(org.id, country_id, MessageKind.DEFENSE, truth=tv, priority=3.5)))
    return org.id, out


def _defense_org_decision_batch_worker(payload: List[Tuple[DefenseOrganization, int]]) -> List[Tuple[str, List[Tuple[str, NetworkMessage]]]]:
    return [_defense_org_decision_worker(item) for item in payload]


def _network_topology_build_worker(payload: Tuple[str, Network, int]) -> Tuple[str, Network]:
    name, network, seed = payload
    rng = random.Random(seed)
    network.build_topology(rng)
    return name, network


def _agent_export_row_worker(agent: Agent) -> Dict[str, Any]:
    return {
        "id": agent.id,
        "name": agent.name,
        "class": agent.__class__.__name__,
        "home_currency": agent.home_currency,
        "fiat": agent.total_fiat(),
        "debt": agent.total_debt(),
        "truth_score": agent.truth_score(),
        "truth_debt": agent.truth_debt(),
        "tags": ";".join(sorted(agent.tags)),
    }


def _morphism_export_row_worker(payload: Tuple[str, Morphism]) -> Dict[str, Any]:
    category_name, m = payload
    return {
        "id": m.id,
        "category": category_name,
        "source": m.source,
        "target": m.target,
        "name": m.name,
        "kind": m.kind,
        "fiat_value": m.fiat_value,
        "truth_score": m.truth_value.weighted_score(),
    }


def _channel_batch_worker(payload: Tuple[str, List[Tuple[Tuple[str, str], Channel]]]) -> Tuple[str, List[Tuple[Tuple[str, str], Channel]], List[NetworkMessage]]:
    net_name, batch = payload
    updates: List[Tuple[Tuple[str, str], Channel]] = []
    delivered_all: List[NetworkMessage] = []
    for key, channel in batch:
        delivered = channel.tick()
        updates.append((key, channel))
        delivered_all.extend(delivered)
    return net_name, updates, delivered_all


def _map_morphism_by_functor(kind: str, functor_name: str, morphism: Morphism) -> Morphism:
    if kind == "FiatToTruthFunctor":
        tv = morphism.truth_value.copy()
        fiat_signal = math.log1p(abs(morphism.fiat_value)) * 0.18
        tv[TruthLayer.LIQUIDITY.value] += fiat_signal
        tv[TruthLayer.SOCIAL.value] += fiat_signal * 0.55
        tv[TruthLayer.CAUSAL.value] += fiat_signal * 0.35
        return Morphism(morphism.source, morphism.target, f"F({morphism.name})", morphism.kind, morphism.fiat_value, tv, {"functor": functor_name})
    if kind == "LegalityFunctor":
        tv = TruthVector.zero()
        tv[TruthLayer.LEGAL.value] = max(0.0, morphism.truth_value[TruthLayer.LEGAL.value]) + 1.0
        tv[TruthLayer.SOVEREIGNTY.value] = morphism.truth_value[TruthLayer.SOVEREIGNTY.value]
        tv[TruthLayer.EPISTEMIC.value] = morphism.truth_value[TruthLayer.EPISTEMIC.value] * 0.5
        return Morphism(morphism.source, morphism.target, f"L({morphism.name})", morphism.kind, morphism.fiat_value, tv, {"functor": functor_name})
    if kind == "SecurityFunctor":
        tv = TruthVector.zero()
        tv[TruthLayer.SECURITY.value] = morphism.truth_value[TruthLayer.SECURITY.value]
        tv[TruthLayer.RISK_REDUCTION.value] = morphism.truth_value[TruthLayer.RISK_REDUCTION.value]
        tv[TruthLayer.NETWORK_REACHABILITY.value] = morphism.truth_value[TruthLayer.NETWORK_REACHABILITY.value]
        return Morphism(morphism.source, morphism.target, f"S({morphism.name})", morphism.kind, morphism.fiat_value, tv, {"functor": functor_name})
    raise ValueError(f"Unbekannter Funktor: {kind}")


def _functor_morphism_worker(payload: Tuple[str, str, Morphism]) -> Morphism:
    kind, functor_name, morphism = payload
    return _map_morphism_by_functor(kind, functor_name, morphism)


def _naturality_gap_worker(payload: Tuple[str, str, str, str, Morphism]) -> float:
    f_kind, f_name, g_kind, g_name, morphism = payload
    fm = _map_morphism_by_functor(f_kind, f_name, morphism)
    gm = _map_morphism_by_functor(g_kind, g_name, morphism)
    return abs(fm.truth_value.weighted_score() - gm.truth_value.weighted_score())


# =============================================================================
# 7. Transaktionen als ökonomische Morphismen
# =============================================================================


class Transaction(Morphism):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> None:
        sim.economic_category.add_morphism(self)


class FiatTransferTransaction(Transaction):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> None:
        src = sim.agents.get(self.source)
        tgt = sim.agents.get(self.target)
        currency = self.meta.get("currency", "WK")
        if src and tgt:
            paid = src.pay_fiat(currency, abs(self.fiat_value))
            tgt.receive_fiat(currency, paid)
        super().apply(sim)


class TruthTransferTransaction(Transaction):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> None:
        tgt = sim.agents.get(self.target)
        if tgt:
            tgt.truth.add(self.truth_value)
        super().apply(sim)


class PurchaseTransaction(Transaction):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> None:
        buyer = sim.agents.get(self.source)
        seller = sim.agents.get(self.target)
        currency = self.meta.get("currency", "WK")
        amount = abs(self.fiat_value)
        if buyer and seller:
            paid = buyer.pay_fiat(currency, amount)
            seller.receive_fiat(currency, paid)
            buyer.truth.add(self.truth_value)
            seller.truth[TruthLayer.LIQUIDITY.value] += math.log1p(paid) * 0.1
            if paid < amount:
                buyer.truth[TruthLayer.LEGAL.value] -= math.log1p(amount - paid) * 0.2
        super().apply(sim)


class LoanOriginationTransaction(Transaction):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> None:
        bank = sim.agents.get(self.source)
        borrower = sim.agents.get(self.target)
        currency = self.meta.get("currency", "WK")
        amount = abs(self.fiat_value)
        if isinstance(bank, FinancialInstitution) and borrower:
            bank.issue_loan(borrower, amount, sim.rng)
        super().apply(sim)


class SanctionTransaction(Transaction):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> None:
        target = sim.agents.get(self.target)
        if target:
            target.truth[TruthLayer.LIQUIDITY.value] -= abs(self.fiat_value) * 0.000001
            target.truth[TruthLayer.LEGAL.value] -= 2.0
            target.truth[TruthLayer.SOCIAL.value] -= 1.5
        sim.legal_category.add_morphism(self)
        sim.security_category.add_morphism(self)


class AuditTransaction(Transaction):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> None:
        target = sim.agents.get(self.target)
        if target:
            if target.truth[TruthLayer.EPISTEMIC.value] < -10:
                target.truth[TruthLayer.LEGAL.value] -= 2.0
                target.truth[TruthLayer.SOCIAL.value] -= 3.0
            target.truth[TruthLayer.EPISTEMIC.value] += 5.0
            target.truth[TruthLayer.CATEGORY_COHERENCE.value] += 3.0
        sim.legal_category.add_morphism(self)
        sim.truth_category.add_morphism(self)


# =============================================================================
# 8. Märkte, Ereignisse und Simulationsdynamik
# =============================================================================


class Market(ABC):
    def __init__(self, name: str) -> None:
        self.name = name
        self.volume = 0.0
        self.truth_volume = 0.0
        self.cleared = 0

    @abstractmethod
    def clear(self, sim: "PlanetaryParadigmSimulation") -> None:
        raise NotImplementedError


class GoodsMarket(Market):
    def clear(self, sim: "PlanetaryParadigmSimulation") -> None:
        companies = [a for a in sim.agents.values() if isinstance(a, Company)]
        selected = sim.rng.sample(companies, min(len(companies), sim.config["monthly_market_actors"]))
        if sim.can_parallel(len(selected), min_items=24):
            target_ids = tuple(a.id for a in sim.agents.values() if isinstance(a, (Company, Country, Household)))
            tasks = [(company, target_ids, sim.next_worker_seed()) for company in selected]
            batches = chunked(tasks, max(1, sim.parallel.workers * 4))
            batch_results = sim.parallel_map(_company_production_batch_worker, batches, min_items=2)
            results = [item for batch in batch_results for item in batch]
            routed: List[NetworkMessage] = []
            for _cid, company_copy, messages in results:
                sim.replace_agent_copy(company_copy)
                routed.extend(messages)
            sim.refresh_network_agent_refs()
            for msg in routed:
                sim.route_message("trade", msg)
            return
        for c in selected:
            c.produce(sim.rng)
            for net_name, msg in c.decide_messages(sim):
                sim.route_message(net_name, msg)


class CreditMarket(Market):
    def clear(self, sim: "PlanetaryParadigmSimulation") -> None:
        banks = [a for a in sim.agents.values() if isinstance(a, CommercialBank)]
        selected = sim.rng.sample(banks, min(len(banks), max(1, sim.config["country_count"] // 2)))
        if sim.can_parallel(len(selected), min_items=12):
            by_currency: Dict[str, List[str]] = defaultdict(list)
            for agent in sim.agents.values():
                if isinstance(agent, (Company, Country)):
                    by_currency[agent.home_currency].append(agent.id)
            tasks = []
            for bank in selected:
                candidates = [aid for aid in by_currency.get(bank.home_currency, []) if aid != bank.id]
                borrower_id = sim.rng.choice(candidates) if candidates else None
                tasks.append((bank, sim.next_worker_seed(), borrower_id))
            batches = chunked(tasks, max(1, sim.parallel.workers * 4))
            batch_results = sim.parallel_map(_credit_bank_batch_worker, batches, min_items=2)
            results = [item for batch in batch_results for item in batch]
            routed: List[NetworkMessage] = []
            for _bid, bank_copy, messages in results:
                sim.replace_agent_copy(bank_copy)
                routed.extend(messages)
            sim.refresh_network_agent_refs()
            for msg in routed:
                sim.route_message("credit", msg)
            return
        for b in selected:
            for net_name, msg in b.decide_messages(sim):
                sim.route_message(net_name, msg)


class LaborMarket(Market):
    def clear(self, sim: "PlanetaryParadigmSimulation") -> None:
        countries = [a for a in sim.agents.values() if isinstance(a, Country)]
        companies = [a for a in sim.agents.values() if isinstance(a, Company)]
        if not countries or not companies:
            return
        selected = sim.rng.sample(companies, min(len(companies), sim.config["monthly_labor_adjustments"]))
        if sim.can_parallel(len(selected), min_items=32):
            tasks = [(company, sim.rng.choice(countries).id, sim.next_worker_seed()) for company in selected]
            batches = chunked(tasks, max(1, sim.parallel.workers * 4))
            batch_results = sim.parallel_map(_labor_company_batch_worker, batches, min_items=2)
            results = [item for batch in batch_results for item in batch]
            for _cid, company_copy, country_id, gdp_delta, country_tv in results:
                sim.replace_agent_copy(company_copy)
                country = sim.agents.get(country_id)
                if isinstance(country, Country):
                    country.gdp += gdp_delta
                    country.truth.add(country_tv)
            sim.refresh_network_agent_refs()
            return
        for c in selected:
            country = sim.rng.choice(countries)
            wage = c.employees * sim.rng.uniform(500, 5000)
            paid = c.pay_fiat(c.home_currency, wage)
            country.gdp += paid * 0.05
            tv = TruthVector.zero()
            tv[TruthLayer.CAUSAL.value] += math.log1p(c.employees) * 0.05
            tv[TruthLayer.SOCIAL.value] += math.log1p(paid) * 0.02
            c.truth.add(tv)
            country.truth.add(tv, 0.3)


class TruthMarket(Market):
    def clear(self, sim: "PlanetaryParadigmSimulation") -> None:
        # Institutionen kaufen/verkaufen Wahrheitskapital: Audit, Reputationsbeweis, Zertifizierung.
        institutions = [a for a in sim.agents.values() if isinstance(a, InstitutionalEntity)]
        companies = [a for a in sim.agents.values() if isinstance(a, Company)]
        if not institutions or not companies:
            return
        for _ in range(min(12, len(companies))):
            inst = sim.rng.choice(institutions)
            target = sim.rng.choice(companies)
            tv = TruthVector.zero()
            tv[TruthLayer.EPISTEMIC.value] += sim.rng.uniform(0.5, 4.0)
            tv[TruthLayer.LEGAL.value] += sim.rng.uniform(0.2, 2.0)
            tv[TruthLayer.CATEGORY_COHERENCE.value] += sim.rng.uniform(0.5, 3.0)
            msg = NetworkMessage(inst.id, target.id, MessageKind.AUDIT, truth=tv, priority=4.0)
            sim.route_message("truth", msg)


class DefenseMarket(Market):
    def clear(self, sim: "PlanetaryParadigmSimulation") -> None:
        orgs = [a for a in sim.agents.values() if isinstance(a, DefenseOrganization)]
        if sim.can_parallel(len(orgs), min_items=4):
            tasks = [(org, sim.next_worker_seed()) for org in orgs]
            batches = chunked(tasks, max(1, sim.parallel.workers * 4))
            batch_results = sim.parallel_map(_defense_org_decision_batch_worker, batches, min_items=2)
            for batch in batch_results:
                for _org_id, messages in batch:
                    for net_name, msg in messages:
                        sim.route_message(net_name, msg)
            return
        for org in orgs:
            for net_name, msg in org.decide_messages(sim):
                sim.route_message(net_name, msg)


class WorldEvent(ABC):
    def __init__(self, name: str, severity: float) -> None:
        self.name = name
        self.severity = severity
        self.id = uid("event")

    @abstractmethod
    def apply(self, sim: "PlanetaryParadigmSimulation") -> Dict[str, Any]:
        raise NotImplementedError


class NaturalEvent(WorldEvent):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> Dict[str, Any]:
        countries = [a for a in sim.agents.values() if isinstance(a, Country)]
        if not countries:
            return {}
        c = sim.rng.choice(countries)
        c.gdp *= 1.0 - self.severity * 0.05
        c.truth[TruthLayer.INFRASTRUCTURE.value] -= 12.0 * self.severity
        c.truth[TruthLayer.HEALTH.value] -= 8.0 * self.severity
        c.truth[TruthLayer.SHEAF_CONSISTENCY.value] -= 3.0 * self.severity
        return {"country": c.name, "severity": self.severity}


class PoliticalEvent(WorldEvent):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> Dict[str, Any]:
        countries = [a for a in sim.agents.values() if isinstance(a, Country)]
        if len(countries) < 2:
            return {}
        a, b = sim.rng.sample(countries, 2)
        a.stability = clamp(a.stability - self.severity * 0.06, 0, 1)
        b.stability = clamp(b.stability - self.severity * 0.04, 0, 1)
        a.truth[TruthLayer.SOVEREIGNTY.value] -= self.severity * 4
        b.truth[TruthLayer.SECURITY.value] -= self.severity * 3
        tv = TruthVector.zero()
        tv[TruthLayer.SECURITY.value] -= self.severity * 6
        m = SanctionTransaction(a.id, b.id, f"sanction/{a.name}->{b.name}", "sanction", self.severity * 1_000_000, tv)
        m.apply(sim)
        return {"source": a.name, "target": b.name, "severity": self.severity}


class FinancialEvent(WorldEvent):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> Dict[str, Any]:
        banks = [a for a in sim.agents.values() if isinstance(a, FinancialInstitution)]
        if not banks:
            return {}
        b = sim.rng.choice(banks)
        loss = sim.rng.lognormvariate(12.0, 1.0) * self.severity
        b.debt[b.home_currency] += loss
        b.truth[TruthLayer.LIQUIDITY.value] -= math.log1p(loss)
        b.truth[TruthLayer.EPISTEMIC.value] -= self.severity * 3
        return {"bank": b.name, "loss": loss}


class TechnologicalEvent(WorldEvent):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> Dict[str, Any]:
        companies = [a for a in sim.agents.values() if isinstance(a, (ResearchCompany, PlatformCompany, StrategicCompany))]
        if not companies:
            return {}
        c = sim.rng.choice(companies)
        gain = self.severity * sim.rng.uniform(15, 80)
        c.truth[TruthLayer.POTENTIAL.value] += gain
        c.truth[TruthLayer.EPISTEMIC.value] += gain * 0.5
        c.truth[TruthLayer.CAUSAL.value] += gain * 0.3
        c.productivity *= 1.0 + self.severity * 0.05
        return {"company": c.name, "gain": gain}


class SecurityEvent(WorldEvent):
    def apply(self, sim: "PlanetaryParadigmSimulation") -> Dict[str, Any]:
        agents = list(sim.agents.values())
        if not agents:
            return {}
        a = sim.rng.choice(agents)
        a.truth[TruthLayer.SECURITY.value] -= 10.0 * self.severity
        a.truth[TruthLayer.NETWORK_REACHABILITY.value] -= 8.0 * self.severity
        a.truth[TruthLayer.EPISTEMIC.value] -= 4.0 * self.severity
        return {"target": a.name, "severity": self.severity}


EVENT_CLASSES: List[Type[WorldEvent]] = [NaturalEvent, PoliticalEvent, FinancialEvent, TechnologicalEvent, SecurityEvent]


# =============================================================================
# 9. Renderer: UTF-8 Art, Diagramme, Visualisierungen
# =============================================================================


class UTF8Renderer(ABC):
    title: str = "Renderer"

    @abstractmethod
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        raise NotImplementedError

    def box(self, title: str, body: str, width: int = 100) -> str:
        # Breitenkorrektur: alle UTF-8-Boxen werden zentral zwei Zeichen schmaler.
        width = clamp_print_width(width)
        inner = max(1, width - 4)
        top = "╔" + "═" * (width - 2) + "╗"
        head = f"║ {title[:inner]:<{inner}} ║"
        sep = "╠" + "═" * (width - 2) + "╣"
        lines = []
        for raw in body.splitlines() or [""]:
            raw = str(raw)
            while len(raw) > inner:
                lines.append(f"║ {raw[:inner]:<{inner}} ║")
                raw = raw[inner:]
            lines.append(f"║ {raw:<{inner}} ║")
        bot = "╚" + "═" * (width - 2) + "╝"
        return "\n".join([top, head, sep] + lines + [bot])


class ClassTreeRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        tree = r"""
SimNode
├─ Agent = TruthBearer + FiatBearer + QueueOwner + NetworkParticipant
│  ├─ LegalEntity
│  │  ├─ InstitutionalEntity
│  │  │  ├─ SovereignEntity
│  │  │  │  └─ Country
│  │  │  ├─ FinancialInstitution
│  │  │  │  ├─ CentralBank
│  │  │  │  └─ CommercialBank
│  │  │  │     ├─ DevelopmentBank
│  │  │  │     └─ InvestmentBank
│  │  │  ├─ UnitedNations
│  │  │  └─ DefenseOrganization
│  │  │     ├─ MutualDefensePact
│  │  │     ├─ MaritimeSecurityLeague
│  │  │     └─ CyberDefenseCompact
│  │  └─ EconomicEntity
│  │     ├─ Household
│  │     └─ Company
│  │        └─ ProductiveCompany
│  │           ├─ CivilianCompany ─┬─ PlatformCompany
│  │           │                   ├─ MediaCompany
│  │           │                   └─ ResearchCompany
│  │           ├─ IndustrialCompany
│  │           └─ StrategicCompany
│  └─ Queues: FIFOQueue, LIFOQueue, PriorityMessageQueue
├─ EconomicObject
│  ├─ Asset
│  ├─ Claim
│  └─ Product
├─ Channel
│  ├─ HalfDuplexChannel
│  └─ FullDuplexChannel
│     └─ SecureFullDuplexChannel
├─ Network
│  ├─ TradeNetwork, CreditNetwork, GovernanceNetwork
│  └─ DefenseNetwork, KnowledgeNetwork, TruthNetwork
├─ Category
│  ├─ EconomicCategory, TruthCategory, LegalCategory, SecurityCategory
│  └─ Morphism / Transaction / UniversalProperty / Functor / NaturalTransformation
└─ Presheaf
   └─ LocalTruthPresheaf
      └─ Sheaf
""".strip("\n")
        return self.box("Klassenvererbung und Paradigma-Architektur", tree, 108)


class NetworkTopologyRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        lines = []
        for name, net in sim.networks.items():
            loads = net.loads()
            counts = net.duplex_counts()
            lines.append(f"{name:<12} topology={net.topology.name:<15} nodes={len(net.nodes):>5} edges={len(net.channels):>5} density={net.density():.4f} queue={net.queue_depth():>5} delivered={net.delivered_total:>7}")
            lines.append(f"             duplex: HALF={counts.get(DuplexMode.HALF.value,0):>4} FULL={counts.get(DuplexMode.FULL.value,0):>4} load-spark={spark(loads, 50)}")
        return self.box("Netzwerk-Topologie, Queues, Half-/Full-Duplex", "\n".join(lines), 120)


class SemaphoreRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        sems: List[SimpleSemaphore] = []
        for net in sim.networks.values():
            for ch in net.channels.values():
                if isinstance(ch, HalfDuplexChannel):
                    sems.append(ch.mutex)
                if isinstance(ch, FullDuplexChannel):
                    sems.append(ch.sem_ab)
                    sems.append(ch.sem_ba)
        sems = sorted(sems, key=lambda s: s.waits + s.utilization, reverse=True)[:24]
        lines = []
        for s in sems:
            lines.append(f"{s.name[:48]:<48} [{bar(s.utilization,1,24)}] util={s.utilization:5.1%} waits={s.waits:>4} tokens={s.available:>3}/{s.capacity:<3}")
        return self.box("Semaphore als Knappheits- und Durchleitungslogik", "\n".join(lines) or "keine Semaphore", 118)


class CategoryRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        lines = []
        cats = [sim.economic_category, sim.truth_category, sim.legal_category, sim.security_category]
        for c in cats:
            lines.append(f"{c.name:<20} Objekte={len(c.objects):>6} Morphismen={len(c.morphisms):>8} id-law-gap={c.identity_law_gap():.4f}")
        lines.append("")
        lines.append("Diagramm:")
        lines.append("   Fiat/Trade-Morphismus ──F──▶ Truth-Morphismus")
        lines.append("           │                         │")
        lines.append("           L                         η: F⇒L / F⇒S")
        lines.append("           ▼                         ▼")
        lines.append("     Legal-Morphismus ──S──▶ Security-Morphismus")
        lines.append("")
        for up in sim.universal_properties:
            lines.append(f"UniversalProperty {up.name:<34} gap={up.last_gap:.4f}")
        for nt in sim.natural_transformations:
            lines.append(f"NaturalTransformation {nt.name:<30} naturality_gap={nt.last_naturality_gap:.4f} components={len(nt.components)}")
        return self.box("Kategorie, Morphismus, Funktor, natürliche Transformation", "\n".join(lines), 116)


class SheafRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        lines = []
        space = sim.space
        lines.append(f"Topologischer Raum: {space.name} | offene Mengen={len(space.opens)}")
        lines.append(f"Globale Garben-Konsistenzlücke: {sim.last_sheaf_gap:.4f}")
        world = sim.world_open
        cover = space.cover(world, max_parts=8)
        lines.append("")
        lines.append("Covering-Family für Planet:")
        for o in cover:
            sec = sim.sheaf.sections.get(o.name)
            score = sec.truth.weighted_score() if sec else 0.0
            lines.append(f"  U={o.name[:24]:<24} |U|={len(o.members):>4} section-score={score:>10.2f}")
        lines.append("")
        lines.append("Garben-Kleben:")
        lines.append("  lokale Sektionen s_i ∈ F(U_i)")
        lines.append("  kompatibel auf U_i∩U_j  ⇒  eindeutige globale Sektion s ∈ F(Planet)")
        lines.append("  ökonomisch: lokale Wahrheiten müssen auf Handels-/Rechts-/Sicherheitsüberschneidungen passen")
        return self.box("Prägarben, Garben, Topologie und Klebeeigenschaft", "\n".join(lines), 118)


class TruthVectorRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        tv = sim.global_truth_vector()
        max_abs = max(1.0, max(abs(v) for v in tv.values.values()))
        lines = [f"Globaler WK-Score={tv.weighted_score():.2f} | Positiv={tv.positive_score():.2f} | Wahrheitsschuld={tv.debt_score():.2f}", ""]
        for layer, value in sorted(tv.values.items(), key=lambda kv: abs(kv[1]), reverse=True)[:28]:
            sign = "+" if value >= 0 else "-"
            lines.append(f"{layer[:24]:<24} {sign} {bar(value, max_abs, 36)} {value:>10.2f}")
        return self.box("Gestapelte Wahrheit als planetare Vektorwährung WK", "\n".join(lines), 118)


class CountryHeatmapRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        countries = sorted([a for a in sim.agents.values() if isinstance(a, Country)], key=lambda c: c.truth_score(), reverse=True)[:24]
        layers = [TruthLayer.EPISTEMIC.value, TruthLayer.LEGAL.value, TruthLayer.CAUSAL.value, TruthLayer.SECURITY.value, TruthLayer.LIQUIDITY.value, TruthLayer.SHEAF_CONSISTENCY.value, TruthLayer.CATEGORY_COHERENCE.value]
        chars = " ·░▒▓█"
        lines = ["Land                       " + " ".join(l[:3].upper() for l in layers) + "  score        debt      fiat"]
        vals = [abs(c.truth[layer]) for c in countries for layer in layers]
        maxv = max(vals) if vals else 1.0
        for c in countries:
            cells = []
            for layer in layers:
                v = c.truth[layer]
                idx = int(clamp(abs(v) / maxv, 0, 0.999) * (len(chars) - 1))
                ch = chars[idx]
                cells.append(ch if v >= 0 else "╳")
            lines.append(f"{c.name[:26]:<26} " + "  ".join(cells) + f"  {c.truth_score():>9.1f} {c.truth_debt():>9.1f} {fmt(c.total_fiat()):>9}")
        return self.box("Länder × Wahrheitsdimensionen Heatmap", "\n".join(lines), 116)


class QueueRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        lines = []
        for a in sorted(sim.agents.values(), key=lambda x: len(x.inbox) + len(x.outbox) + len(x.priority_box), reverse=True)[:25]:
            total = len(a.inbox) + len(a.outbox) + len(a.priority_box)
            if total == 0:
                continue
            lines.append(f"{a.name[:32]:<32} FIFO(in)={len(a.inbox):>4} LIFO(out)={len(a.outbox):>4} PRIO={len(a.priority_box):>4} {bar(total,50,30)}")
        return self.box("FIFO/LIFO/Priority Queues pro Agent", "\n".join(lines) or "Alle Agent-Queues leer; Netzwerkkanäle tragen die Last.", 112)


class MacroRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        hist = sim.history
        gdp = [row["planet_gdp"] for row in hist]
        truth = [row["truth_score"] for row in hist]
        debt = [row["truth_debt"] for row in hist]
        gap = [row["naturality_gap"] for row in hist]
        lines = [
            f"Monate={sim.month}  Agenten={len(sim.agents)}  Länder={sim.config['country_count']}  Events={len(sim.events)}",
            f"GDP       {spark(gdp, 80)}",
            f"WK-Score  {spark(truth, 80)}",
            f"WK-Debt   {spark(debt, 80)}",
            f"η-Gap     {spark(gap, 80)}",
        ]
        return self.box("Makro-Zeitreihen als UTF-8 Sparklines", "\n".join(lines), 118)


class EventRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        counts = Counter(e["type"] for e in sim.events)
        lines = ["Ereignis-Histogramm:"]
        maxc = max(counts.values()) if counts else 1
        for k, v in counts.most_common():
            lines.append(f"{k:<22} {bar(v,maxc,40)} {v}")
        lines.append("")
        lines.append("Letzte Ereignisse:")
        for e in sim.events[-18:]:
            lines.append(f"M{e['month']:>04} {e['type']:<22} {e['name']:<32} {json.dumps(e['details'], ensure_ascii=False)[:80]}")
        return self.box("Welt-Ereignisse, Krisen, Durchbrüche", "\n".join(lines), 118)


class MorphismFlowRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        kinds = Counter(m.kind for m in sim.economic_category.morphisms[-5000:])
        lines = ["Ökonomische Morphismen im aktuellen Fenster:", ""]
        maxc = max(kinds.values()) if kinds else 1
        for k, v in kinds.most_common():
            lines.append(f"{k:<18} {bar(v,maxc,44)} {v}")
        lines += [
            "",
            "Morphismus-Lebenszyklus:",
            "  Claim/Intent ─▶ Queue ─▶ Channel(HALF/FULL) ─▶ Transaction ─▶ Category",
            "        │             │                │                 │",
            "        ▼             ▼                ▼                 ▼",
            "  TruthVector    Semaphore       Topology          Functor F/L/S",
            "                                                        │",
            "                                                        ▼",
            "                                                Natürliche Transformation η",
        ]
        return self.box("Morphismenfluss: Netzwerk → Kategorie → WK", "\n".join(lines), 116)


class InstitutionalRenderer(UTF8Renderer):
    def render(self, sim: "PlanetaryParadigmSimulation") -> str:
        orgs = [a for a in sim.agents.values() if isinstance(a, (UnitedNations, DefenseOrganization, CentralBank))]
        lines = ["Institutionelles Netzwerk:"]
        for o in sorted(orgs, key=lambda x: x.truth_score(), reverse=True)[:32]:
            kind = o.__class__.__name__
            degree = sum(net.degree(o.id) for net in sim.networks.values())
            lines.append(f"{kind:<24} {o.name[:42]:<42} degree={degree:>4} WK={o.truth_score():>10.1f}")
        return self.box("UN, Zentralbanken und Verteidigungsorganisationen", "\n".join(lines), 118)


# =============================================================================
# 10. Hauptsimulation
# =============================================================================


PRESETS: Dict[str, Dict[str, int]] = {
    "tiny": {
        "country_count": 6,
        "companies_per_country": 8,
        "households_per_country": 2,
        "banks_per_country": 2,
        "defense_orgs": 3,
        "monthly_market_actors": 32,
        "monthly_labor_adjustments": 20,
        "network_ticks": 3,
    },
    "standard": {
        "country_count": 18,
        "companies_per_country": 18,
        "households_per_country": 4,
        "banks_per_country": 3,
        "defense_orgs": 5,
        "monthly_market_actors": 180,
        "monthly_labor_adjustments": 90,
        "network_ticks": 4,
    },
    "large": {
        "country_count": 48,
        "companies_per_country": 28,
        "households_per_country": 6,
        "banks_per_country": 4,
        "defense_orgs": 8,
        "monthly_market_actors": 600,
        "monthly_labor_adjustments": 240,
        "network_ticks": 5,
    },
    "epic": {
        "country_count": 96,
        "companies_per_country": 44,
        "households_per_country": 8,
        "banks_per_country": 5,
        "defense_orgs": 12,
        "monthly_market_actors": 1600,
        "monthly_labor_adjustments": 700,
        "network_ticks": 6,
    },
}

REGIONS = ["Nordkreis", "Südband", "Ostbogen", "Westarchipel", "Mittelmeer", "Hochland", "Äquatorzone", "Polarfront"]
COUNTRY_PREFIXES = ["Aster", "Boreal", "Civitas", "Dorian", "Elios", "Ferro", "Gaia", "Helio", "Ionia", "Juno", "Kairo", "Lumen", "Mira", "Nadir", "Orion", "Praxa", "Quanta", "Rhea", "Sol", "Tethys", "Umbra", "Vela", "Wega", "Xenia", "Yara", "Zenit"]
COUNTRY_SUFFIXES = ["land", "reich", "union", "staat", "republik", "föderation", "zone", "bund", "kron", "mark"]


class PlanetaryParadigmSimulation:
    def __init__(
        self,
        preset: str = "tiny",
        months: int = 24,
        seed: int = 7,
        out_dir: str = "paradigm_world",
        verbose: bool = False,
        workers: Any = "auto",
        mp_start_method: str = "auto",
        parallel_min_items: int = 16,
        lang: str = "en",
        color_output: bool = True,
        volatility: float = 1.0,
        truth_volatility: float = 1.0,
        fiat_volatility: float = 1.0,
    ) -> None:
        self.preset = preset
        self.config = dict(PRESETS[preset])
        self.months = months
        self.rng = random.Random(seed)
        self.seed = seed
        self.out_dir = Path(out_dir)
        self.verbose = verbose
        self.parallel = ProcessParallelRuntime(preset, workers, mp_start_method, parallel_min_items)
        self.lang = (lang or "en").lower()
        self.color_output = bool(color_output)
        self.volatility = max(0.0, float(volatility))
        self.truth_volatility = max(0.0, float(truth_volatility))
        self.fiat_volatility = max(0.0, float(fiat_volatility))
        self.month = 0
        self.agents: Dict[str, Agent] = {}
        self.objects: Dict[str, EconomicObject] = {}
        self.events: List[Dict[str, Any]] = []
        self.history: List[Dict[str, Any]] = []
        self.economic_category = EconomicCategory("𝓔 Economy")
        self.truth_category = TruthCategory("𝓣 Truth")
        self.legal_category = LegalCategory("𝓛 Law")
        self.security_category = SecurityCategory("𝓢 Security")
        self.networks: Dict[str, Network] = {}
        self.markets: List[Market] = [GoodsMarket("goods"), CreditMarket("credit"), LaborMarket("labor"), TruthMarket("truth"), DefenseMarket("defense")]
        self.space = GrothendieckTopology()
        self.sheaf = Sheaf("𝓕_truth", self.space)
        self.world_open = OpenSet("Planet", frozenset())
        self.last_sheaf_gap = 0.0
        self.functors: List[Functor] = []
        self.natural_transformations: List[NaturalTransformation] = []
        self.universal_properties: List[UniversalProperty] = []
        self.un: Optional[UnitedNations] = None
        self.renderers: List[UTF8Renderer] = [
            ClassTreeRenderer(), NetworkTopologyRenderer(), SemaphoreRenderer(), CategoryRenderer(), SheafRenderer(),
            TruthVectorRenderer(), CountryHeatmapRenderer(), QueueRenderer(), MacroRenderer(), EventRenderer(),
            MorphismFlowRenderer(), InstitutionalRenderer(),
        ]

    # ----- Setup -------------------------------------------------------------

    def add_agent(self, agent: Agent) -> Agent:
        self.agents[agent.id] = agent
        obj = CategoryObject(agent.name, agent.id, agent.__class__.__name__, {"currency": agent.home_currency})
        self.economic_category.add_object(obj)
        self.truth_category.add_object(obj)
        self.legal_category.add_object(obj)
        self.security_category.add_object(obj)
        return agent

    def build_world(self) -> None:
        countries = self._build_countries()
        self._build_institutions(countries)
        self._build_companies_and_households(countries)
        self._build_networks()
        self._build_topology_space(countries)
        self._build_category_architecture()
        self.assign_sheaf_sections()

    def _build_countries(self) -> List[Country]:
        out = []
        used = set()
        for i in range(self.config["country_count"]):
            while True:
                name = self.rng.choice(COUNTRY_PREFIXES) + self.rng.choice(COUNTRY_SUFFIXES)
                if name not in used:
                    used.add(name)
                    break
            currency = (slug(name)[:3].upper() + str(i % 10))
            region = self.rng.choice(REGIONS)
            population = self.rng.lognormvariate(16.0, 1.1)
            gdp = self.rng.lognormvariate(24.0, 1.0)
            c = Country(name, currency, region, population, gdp)
            c.stability = self.rng.uniform(0.35, 0.95)
            c.defense_posture = self.rng.uniform(0.05, 0.9)
            self.add_agent(c)
            out.append(c)
        return out

    def _build_institutions(self, countries: List[Country]) -> None:
        self.un = self.add_agent(UnitedNations())  # type: ignore[assignment]
        for c in countries:
            cb = CentralBank(c)
            cb.receive_fiat(c.currency, c.gdp * 0.05)
            self.add_agent(cb)
            for b in range(self.config["banks_per_country"]):
                cls: Type[CommercialBank] = self.rng.choice([CommercialBank, DevelopmentBank, InvestmentBank])
                bank = cls(f"{self.rng.choice(['Meridian','Atlas','Civic','Nova','Trust','Vector','Union'])} Bank {c.name}-{b+1}", c.currency)
                bank.receive_fiat(c.currency, c.gdp * self.rng.uniform(0.002, 0.02))
                self.add_agent(bank)
        org_classes: List[Type[DefenseOrganization]] = [MutualDefensePact, MaritimeSecurityLeague, CyberDefenseCompact]
        for i in range(self.config["defense_orgs"]):
            org = org_classes[i % len(org_classes)](f"{['Shield','Harbor','Cipher','Aegis','Sentinel','Maritime','Cyber'][i % 7]} Compact {i+1}")
            for c in self.rng.sample(countries, self.rng.randint(2, min(len(countries), max(2, len(countries)//2)))):
                org.add_member(c)
            self.add_agent(org)

    def _build_companies_and_households(self, countries: List[Country]) -> None:
        company_classes: List[Type[Company]] = [CivilianCompany, IndustrialCompany, StrategicCompany, PlatformCompany, MediaCompany, ResearchCompany]
        for c in countries:
            for h in range(self.config["households_per_country"]):
                hh = Household(f"Household Bloc {c.name}-{h+1}", c.currency, c.population / max(1, self.config["households_per_country"]))
                hh.receive_fiat(c.currency, c.gdp * self.rng.uniform(0.0001, 0.001))
                self.add_agent(hh)
            for i in range(self.config["companies_per_country"]):
                sector = self.rng.choice(SECTORS)
                cls = self.rng.choice(company_classes)
                if sector in ("defense", "cybersecurity", "space"):
                    cls = StrategicCompany
                elif sector in ("energy", "construction", "semiconductors", "logistics", "water"):
                    cls = IndustrialCompany
                elif sector in ("media", "culture", "tourism"):
                    cls = MediaCompany
                elif sector in ("research", "biotech", "education"):
                    cls = ResearchCompany
                company = cls(f"{sector.title()} {self.rng.choice(['Works','Systems','Guild','Foundry','Trust','Labs','Arc'])} {c.name}-{i+1}", c.currency, sector)
                company.receive_fiat(c.currency, c.gdp * self.rng.uniform(0.00005, 0.002))
                self.add_agent(company)

    def _build_networks(self) -> None:
        agents = list(self.agents.values())
        institutions = [a for a in agents if isinstance(a, InstitutionalEntity)]
        finance = [a for a in agents if isinstance(a, FinancialInstitution) or isinstance(a, Country)]
        defense = [a for a in agents if isinstance(a, (DefenseOrganization, Country, StrategicCompany))]
        companies = [a for a in agents if isinstance(a, (Company, Country, Household))]
        truth_agents = [a for a in agents if isinstance(a, (InstitutionalEntity, Company, Country))]
        self.networks = {
            "trade": TradeNetwork("trade", CorePeripheryTopology(0.16, 3), FullDuplexChannel, QueueDiscipline.FIFO, 16),
            "credit": CreditNetwork("credit", StarTopology(hubs=max(1, self.config["country_count"] // 3)), SecureFullDuplexChannel, QueueDiscipline.PRIORITY, 12),
            "governance": GovernanceNetwork("governance", StarTopology(hubs=1), SecureFullDuplexChannel, QueueDiscipline.PRIORITY, 8),
            "defense": DefenseNetwork("defense", MeshTopology(0.10, max_edges=1800), HalfDuplexChannel, QueueDiscipline.LIFO, 10),
            "knowledge": KnowledgeNetwork("knowledge", MeshTopology(0.08, max_edges=1400), FullDuplexChannel, QueueDiscipline.FIFO, 14),
            "truth": TruthNetwork("truth", CorePeripheryTopology(0.20, 2), SecureFullDuplexChannel, QueueDiscipline.PRIORITY, 10),
        }
        mapping = {
            "trade": companies,
            "credit": finance,
            "governance": institutions + [a for a in agents if isinstance(a, Country)],
            "defense": defense,
            "knowledge": truth_agents,
            "truth": truth_agents,
        }
        for name, net in self.networks.items():
            for a in mapping[name]:
                a.join_network(net)
        if self.can_parallel(len(self.networks), min_items=2):
            tasks = [(name, net, self.next_worker_seed()) for name, net in self.networks.items()]
            for name, net_copy in self.parallel_map(_network_topology_build_worker, tasks, min_items=2):
                self.networks[name] = net_copy
            self.refresh_network_agent_refs()
        else:
            for net in self.networks.values():
                net.build_topology(self.rng)
        # Sicherheitsnetz: bei Star/zufälliger Topologie können isolierte Knoten übrig bleiben.
        for net in self.networks.values():
            ids = list(net.nodes)
            if len(ids) > 1:
                for node_id in ids:
                    if net.degree(node_id) == 0:
                        net.connect(node_id, self.rng.choice([x for x in ids if x != node_id]), self.rng)

    def _build_topology_space(self, countries: List[Country]) -> None:
        all_ids = frozenset(self.agents.keys())
        self.world_open = OpenSet("Planet", all_ids)
        self.space.add_open(self.world_open)
        by_region: Dict[str, List[str]] = defaultdict(list)
        by_currency: Dict[str, List[str]] = defaultdict(list)
        by_alliance: Dict[str, List[str]] = defaultdict(list)
        by_sector: Dict[str, List[str]] = defaultdict(list)
        for a in self.agents.values():
            if isinstance(a, Country):
                by_region[a.region].append(a.id)
                by_currency[a.currency].append(a.id)
                for alliance_id in a.alliances:
                    by_alliance[alliance_id].append(a.id)
            elif isinstance(a, Company):
                by_currency[a.home_currency].append(a.id)
                by_sector[a.sector].append(a.id)
            else:
                by_currency[a.home_currency].append(a.id)
        for region, ids in by_region.items():
            self.space.add_open(OpenSet(f"Region:{region}", frozenset(ids)))
        for currency, ids in by_currency.items():
            self.space.add_open(OpenSet(f"Currency:{currency}", frozenset(ids)))
        for sector, ids in by_sector.items():
            self.space.add_open(OpenSet(f"Sector:{sector}", frozenset(ids)))
        for alliance_id, ids in by_alliance.items():
            org = self.agents.get(alliance_id)
            self.space.add_open(OpenSet(f"Alliance:{org.name if org else alliance_id}", frozenset(ids)))
        self.space.ensure_intersections(limit=900)
        for o in list(self.space.opens.values())[:50]:
            if o.name != "Planet":
                self.space.add_covering_family("Planet", [o.name])

    def _build_category_architecture(self) -> None:
        F = FiatToTruthFunctor("F:Fiat→Truth", self.economic_category, self.truth_category)
        L = LegalityFunctor("L:Economy→Law", self.economic_category, self.legal_category)
        S = SecurityFunctor("S:Economy→Security", self.economic_category, self.security_category)
        self.functors = [F, L, S]
        eta_FL = NaturalTransformation("η: F⇒L", F, L)
        eta_FS = NaturalTransformation("η: F⇒S", F, S)
        eta_FL.build_components()
        eta_FS.build_components()
        self.natural_transformations = [eta_FL, eta_FS]
        terminal_id = self.un.id if self.un else "UN"
        self.universal_properties = [
            TerminalUniversalProperty(terminal_id), ProductUniversalProperty(), PullbackUniversalProperty(),
            PushoutUniversalProperty(), EqualizerUniversalProperty(),
        ]

    # ----- Prozess-Parallelität ---------------------------------------------

    def next_worker_seed(self) -> int:
        return self.rng.randrange(1, 2**31 - 1)

    def can_parallel(self, item_count: int, min_items: Optional[int] = None) -> bool:
        return self.parallel.should_parallel(item_count, min_items)

    def parallel_map(self, func: Callable[[Any], Any], tasks: Sequence[Any], min_items: Optional[int] = None) -> List[Any]:
        return self.parallel.map(func, tasks, min_items=min_items)

    def replace_agent_copy(self, agent: Agent) -> None:
        self.agents[agent.id] = agent
        if self.un is not None and self.un.id == agent.id and isinstance(agent, UnitedNations):
            self.un = agent

    def refresh_network_agent_refs(self) -> None:
        for net in self.networks.values():
            for aid in list(net.nodes.keys()):
                replacement = self.agents.get(aid)
                if replacement is not None:
                    net.nodes[aid] = replacement

    def parallel_month_passes(self) -> None:
        agents = list(self.agents.values())
        if self.can_parallel(len(agents), min_items=32):
            tasks = [(agent, self.next_worker_seed()) for agent in agents]
            batches = chunked(tasks, max(1, self.parallel.workers * 4))
            batch_results = self.parallel_map(_agent_month_passes_batch_worker, batches, min_items=2)
            for batch in batch_results:
                for _aid, agent_copy in batch:
                    self.replace_agent_copy(agent_copy)
            self.refresh_network_agent_refs()
            return
        for agent in agents:
            agent.month_passes(self.rng)

    def parallel_collect_taxes(self, countries: List[Country]) -> None:
        rows_by_currency: Dict[str, List[Tuple[str, float]]] = defaultdict(list)
        for agent in self.agents.values():
            rows_by_currency[agent.home_currency].append((agent.id, agent.total_fiat()))
        tasks = [(c.id, c.currency, c.tax_rate, rows_by_currency.get(c.currency, [])) for c in countries]
        if self.can_parallel(len(tasks), min_items=4):
            results = self.parallel_map(_country_tax_assessment_worker, tasks, min_items=4)
        else:
            results = [_country_tax_assessment_worker(t) for t in tasks]
        for country_id, currency, assessments in results:
            country = self.agents.get(country_id)
            if not isinstance(country, Country):
                continue
            tax = 0.0
            for agent_id, cur, base in assessments:
                agent = self.agents.get(agent_id)
                if agent is None or agent is country:
                    continue
                tax += agent.pay_fiat(cur, base)
            country.receive_fiat(currency, tax)
            country.gdp += tax * 0.15
            country.truth[TruthLayer.LEGAL.value] += math.log1p(tax) * 0.03

    def parallel_public_goods(self, countries: List[Country]) -> None:
        if self.can_parallel(len(countries), min_items=4):
            tasks = [(country, self.next_worker_seed()) for country in countries]
            for country_id, country_copy in self.parallel_map(_country_public_goods_worker, tasks, min_items=4):
                self.replace_agent_copy(country_copy)
            self.refresh_network_agent_refs()
            return
        for country in countries:
            country.spend_public_goods(self.rng)

    def parallel_central_bank_policy(self) -> None:
        tasks: List[Tuple[CentralBank, Country, int]] = []
        for cb in [a for a in self.agents.values() if isinstance(a, CentralBank)]:
            country = self.agents.get(cb.country_id)
            if isinstance(country, Country):
                tasks.append((cb, country, self.next_worker_seed()))
        if self.can_parallel(len(tasks), min_items=4):
            results = self.parallel_map(_central_bank_policy_worker, tasks, min_items=4)
            for cb_id, cb_copy, country_id, country_copy in results:
                self.replace_agent_copy(cb_copy)
                self.replace_agent_copy(country_copy)
            self.refresh_network_agent_refs()
            return
        for cb, country, seed in tasks:
            cb.set_policy(country, self.rng)

    def assign_sheaf_sections(self) -> None:
        opens = list(self.space.opens.values())
        if self.can_parallel(len(opens), min_items=40):
            agent_snapshot = {aid: (agent.truth.as_dict(), agent.total_fiat()) for aid, agent in self.agents.items()}
            specs = [(o.name, tuple(o.members)) for o in opens]
            tasks = [(chunk, agent_snapshot) for chunk in chunked(specs, self.parallel.workers)]
            results = self.parallel_map(_sheaf_assign_chunk, tasks, min_items=2)
            self.sheaf.sections.clear()
            for batch in results:
                for open_name, truth_values, fiat, count in batch:
                    open_set = self.space.opens.get(open_name)
                    if open_set is not None:
                        self.sheaf.sections[open_name] = Section(open_set, TruthVector(truth_values), fiat, {"count": count, "parallel": True})
            return
        self.sheaf.assign(self.agents)

    def tick_networks_and_process(self) -> None:
        for _ in range(self.config["network_ticks"]):
            all_channels = sum(len(net.channels) for net in self.networks.values())
            if self.can_parallel(all_channels, min_items=24):
                tasks: List[Tuple[str, List[Tuple[Tuple[str, str], Channel]]]] = []
                for net_name, net in self.networks.items():
                    batches = chunked(list(net.channels.items()), max(1, self.parallel.workers * 2))
                    for batch in batches:
                        tasks.append((net_name, batch))
                results = self.parallel_map(_channel_batch_worker, tasks, min_items=2)
                delivered_messages: List[NetworkMessage] = []
                delivered_counts: Counter = Counter()
                for net_name, updates, delivered in results:
                    net = self.networks[net_name]
                    for key, channel in updates:
                        net.channels[key] = channel
                    delivered_counts[net_name] += len(delivered)
                    delivered_messages.extend(delivered)
                for net_name, count in delivered_counts.items():
                    self.networks[net_name].delivered_total += count
                for msg in delivered_messages:
                    self.process_delivered(msg)
            else:
                for net in self.networks.values():
                    for msg in net.tick():
                        self.process_delivered(msg)

    def apply_functors_recent(self, limit: int = 100) -> None:
        morphisms = list(self.economic_category.morphisms[-limit:])
        for functor in self.functors:
            for obj in functor.source.objects.values():
                mapped_obj = functor.map_object(obj)
                if mapped_obj.ref_id not in functor.target.objects:
                    functor.target.add_object(mapped_obj)
            if self.can_parallel(len(morphisms), min_items=64):
                tasks = [(functor.__class__.__name__, functor.name, m) for m in morphisms]
                mapped = self.parallel_map(_functor_morphism_worker, tasks, min_items=64)
                for mm in mapped:
                    functor.target.add_morphism(mm)
            else:
                for morphism in morphisms:
                    functor.target.add_morphism(functor.map_morphism(morphism))

    def evaluate_naturality_gaps(self, limit: int = 200) -> List[float]:
        morphisms = list(self.economic_category.morphisms[-limit:])
        gaps_out: List[float] = []
        for nt in self.natural_transformations:
            if not morphisms:
                nt.last_naturality_gap = 0.0
            elif self.can_parallel(len(morphisms), min_items=64):
                tasks = [(nt.F.__class__.__name__, nt.F.name, nt.G.__class__.__name__, nt.G.name, m) for m in morphisms]
                gaps = self.parallel_map(_naturality_gap_worker, tasks, min_items=64)
                nt.last_naturality_gap = mean_or(gaps, 0.0)
            else:
                nt.last_naturality_gap = nt.evaluate_gap(limit=limit)
            gaps_out.append(nt.last_naturality_gap)
        return gaps_out

    # ----- Laufzeit ----------------------------------------------------------

    def route_message(self, net_name: str, message: NetworkMessage) -> bool:
        net = self.networks.get(net_name)
        if not net:
            return False
        # Paradigma-Architektur: Routing darf Topologie adaptiv erweitern.
        # Wenn ein ökonomischer Morphismus eine Verbindung verlangt, wird sie
        # als neuer Kanal materialisiert, sofern beide Agenten existieren.
        for aid in (message.source_id, message.target_id):
            agent = self.agents.get(aid)
            if agent is not None and aid not in net.nodes:
                agent.join_network(net)
        if message.source_id in net.nodes and message.target_id in net.nodes and net.key(message.source_id, message.target_id) not in net.channels:
            net.connect(message.source_id, message.target_id, self.rng)
        if message.fiat_amount:
            message.fiat_amount *= self.volatility_factor("fiat")
        if message.truth is not None:
            message.truth.scale(self.volatility_factor("truth"))
        source = self.agents.get(message.source_id)
        if source is not None:
            source.outbox.push(message)
        ok = net.send(message)
        if ok and source is not None:
            # LIFO-Outbox als Audit-Spur: das zuletzt behauptete Ereignis ist oben.
            source.outbox.pop()
        return ok

    def process_delivered(self, message: NetworkMessage) -> None:
        target = self.agents.get(message.target_id)
        if target:
            target.handle_message(message, self)
        if message.kind == MessageKind.TRADE:
            tx = PurchaseTransaction(
                message.source_id, message.target_id, f"purchase/{message.payload.get('sector','goods')}", "purchase",
                message.fiat_amount, message.truth, {"currency": message.currency, **message.payload},
            )
            tx.apply(self)
        elif message.kind == MessageKind.CREDIT:
            tx = LoanOriginationTransaction(
                message.source_id, message.target_id, "loan-origination", "loan",
                message.fiat_amount or message.payload.get("requested_loan", 0.0), message.truth, {"currency": message.currency},
            )
            tx.apply(self)
        elif message.kind == MessageKind.AUDIT:
            tx = AuditTransaction(message.source_id, message.target_id, "audit", "audit", 0.0, message.truth)
            tx.apply(self)
        elif message.kind == MessageKind.SANCTION:
            tx = SanctionTransaction(message.source_id, message.target_id, "sanction", "sanction", message.fiat_amount, message.truth)
            tx.apply(self)
        elif message.kind == MessageKind.DEFENSE:
            tx = Transaction(message.source_id, message.target_id, "defense-support", "defense", 0.0, message.truth)
            tx.apply(self)
            self.security_category.add_morphism(tx)
        elif message.kind in (MessageKind.KNOWLEDGE, MessageKind.SHEAF_PATCH, MessageKind.CATEGORY_MORPHISM):
            tx = TruthTransferTransaction(message.source_id, message.target_id, message.kind.value, message.kind.value, message.fiat_amount, message.truth)
            tx.apply(self)

    def random_event(self) -> None:
        if self.rng.random() > 0.22:
            return
        cls = self.rng.choice(EVENT_CLASSES)
        severity = self.rng.betavariate(2.0, 5.0) * 3.0 * self.volatility_factor("overall")
        name_map = {
            NaturalEvent: "climate/flood/earthquake shock",
            PoliticalEvent: "border dispute / sanctions spiral",
            FinancialEvent: "bank liquidity truth-crack",
            TechnologicalEvent: "technological breakthrough",
            SecurityEvent: "cyber or hybrid security incident",
        }
        event = cls(name_map.get(cls, "event"), severity)
        details = event.apply(self)
        self.events.append({"month": self.month, "type": cls.__name__, "name": event.name, "severity": severity, "details": details})

    def update_category_layer(self) -> float:
        self.apply_functors_recent(limit=100)
        gaps = self.evaluate_naturality_gaps(limit=200)
        for up in self.universal_properties:
            up.verify(self.economic_category)
        category_gap = mean_or(gaps, 0.0)
        # Gap als negative Kategorie-Kohärenz in planetarem System streuen.
        if category_gap > 100:
            for a in self.rng.sample(list(self.agents.values()), min(10, len(self.agents))):
                a.truth[TruthLayer.CATEGORY_COHERENCE.value] -= math.log1p(category_gap) * 0.2
        return category_gap

    def update_sheaf_layer(self) -> float:
        self.assign_sheaf_sections()
        cover = self.space.cover(self.world_open, max_parts=16)
        glued, gap = self.sheaf.glue(self.world_open, cover)
        self.last_sheaf_gap = gap
        # Globale Klebeeigenschaft wirkt als Governance-Patch über TruthNetwork.
        if self.un and gap > 0.05:
            for o in cover[:6]:
                for aid in list(o.members)[:2]:
                    tv = TruthVector.zero()
                    tv[TruthLayer.SHEAF_CONSISTENCY.value] += (1.0 - gap) * 2.0
                    tv[TruthLayer.EPISTEMIC.value] += 0.5
                    self.route_message("truth", NetworkMessage(self.un.id, aid, MessageKind.SHEAF_PATCH, truth=tv, priority=4.0))
        return gap

    def tick_month(self) -> None:
        self.month += 1
        self.parallel_month_passes()
        self.apply_global_volatility_shocks()
        countries = [a for a in self.agents.values() if isinstance(a, Country)]
        self.parallel_collect_taxes(countries)
        countries = [a for a in self.agents.values() if isinstance(a, Country)]
        self.parallel_public_goods(countries)
        self.parallel_central_bank_policy()
        # Institutionelle Messages
        if self.un:
            for net_name, msg in self.un.decide_messages(self):
                self.route_message(net_name, msg)
        for market in self.markets:
            market.clear(self)
        # Netzwerke ticken mehrfach pro Monat; prozessparallel über Channel-Batches.
        self.tick_networks_and_process()
        self.random_event()
        cat_gap = self.update_category_layer()
        sheaf_gap = self.update_sheaf_layer()
        self.record_history(cat_gap, sheaf_gap)
        if self.verbose and (self.month == 1 or self.month % max(1, self.months // 10) == 0):
            print(f"month={self.month:>4} GDP={fmt(self.planet_gdp())} WK={self.global_truth_vector().weighted_score():.1f} η-gap={cat_gap:.2f} sheaf-gap={sheaf_gap:.3f}")

    def run(self) -> None:
        self.build_world()
        for _ in range(self.months):
            self.tick_month()

    # ----- Aggregation -------------------------------------------------------

    def planetary_aggregates(self) -> Tuple[float, TruthVector]:
        agents = list(self.agents.values())
        rows = [(isinstance(a, Country), getattr(a, "gdp", 0.0), a.truth.as_dict()) for a in agents]
        if self.can_parallel(len(rows), min_items=512):
            batches = chunked(rows, self.parallel.workers)
            partials = self.parallel_map(_aggregate_agent_chunk, batches, min_items=2)
            total_gdp = 0.0
            tv = TruthVector.zero()
            for gdp_part, values in partials:
                total_gdp += gdp_part
                tv.add(TruthVector(values))
            return total_gdp, tv
        total_gdp = sum(a.gdp for a in agents if isinstance(a, Country))
        tv = TruthVector.zero()
        for a in agents:
            tv.add(a.truth)
        return total_gdp, tv

    def planet_gdp(self) -> float:
        return self.planetary_aggregates()[0]

    def global_truth_vector(self) -> TruthVector:
        return self.planetary_aggregates()[1]

    def record_history(self, category_gap: float, sheaf_gap: float) -> None:
        planet_gdp, tv = self.planetary_aggregates()
        self.history.append({
            "month": self.month,
            "planet_gdp": planet_gdp,
            "truth_score": tv.weighted_score(),
            "truth_positive": tv.positive_score(),
            "truth_debt": tv.debt_score(),
            "naturality_gap": category_gap,
            "sheaf_gap": sheaf_gap,
            "economic_morphisms": len(self.economic_category.morphisms),
            "truth_morphisms": len(self.truth_category.morphisms),
            "network_queue_depth": sum(net.queue_depth() for net in self.networks.values()),
            "events": len(self.events),
        })

    def localize_output(self, text: str) -> str:
        return translate_output(text, self.lang)

    def entity_color(self, agent: Optional[Agent]) -> str:
        if isinstance(agent, Country):
            return "country"
        if isinstance(agent, CentralBank):
            return "central_bank"
        if isinstance(agent, FinancialInstitution):
            return "bank"
        if isinstance(agent, UnitedNations):
            return "un"
        if isinstance(agent, DefenseOrganization):
            return "defense"
        if isinstance(agent, Company):
            return "company"
        if isinstance(agent, Household):
            return "household"
        return "keyword"

    def apply_color_to_output(self, text: str, enabled: Optional[bool] = None) -> str:
        enabled = self.color_output if enabled is None else enabled
        if not enabled:
            return text
        out = text
        for ch in "╔╗╚╝╠╣║═":
            out = out.replace(ch, ansi(ch, "border", True))
        for sym in "█▓▒░":
            out = out.replace(sym, ansi(sym, "bar" if sym in "█▓" else "bar_bg", True))
        for sym in "▁▂▃▄":
            out = out.replace(sym, ansi(sym, "spark_low", True))
        for sym in "▅▆":
            out = out.replace(sym, ansi(sym, "spark_mid", True))
        for sym in "▇":
            out = out.replace(sym, ansi(sym, "spark_high", True))
        out = re.sub(r"\bWK\b", lambda m: ansi(m.group(0), "wk", True), out)
        for kw in ["GDP", "TV", "FIFO", "LIFO", "PRIO", "HALF", "FULL", "SEM", "Morphismus", "Morphism", "Functor", "Funktor", "Topology", "Topologie"]:
            out = re.sub(rf"\b{re.escape(kw)}\b", lambda m: ansi(m.group(0), "keyword", True), out)
        for cur in sorted(set(a.home_currency for a in self.agents.values()), key=len, reverse=True):
            out = re.sub(rf"\b{re.escape(cur)}\b", lambda m: ansi(m.group(0), "currency", True), out)
        for agent in sorted(self.agents.values(), key=lambda a: len(a.name), reverse=True):
            out = out.replace(agent.name, ansi(agent.name, self.entity_color(agent), True))
        out = re.sub(r"(?<![A-Za-z0-9])(-[0-9]+(?:\.[0-9]+)?(?:[KMBT])?)", lambda m: ansi(m.group(1), "number_neg", True), out)
        out = re.sub(r"(?<![A-Za-z0-9])(\+[0-9]+(?:\.[0-9]+)?(?:[KMBT])?)", lambda m: ansi(m.group(1), "number_pos", True), out)
        return out

    def volatility_sigma(self, domain: str = "overall") -> float:
        if domain == "truth":
            scale = self.volatility * self.truth_volatility
        elif domain == "fiat":
            scale = self.volatility * self.fiat_volatility
        else:
            scale = self.volatility
        return 0.06 * max(0.0, scale)

    def volatility_factor(self, domain: str = "overall") -> float:
        sigma = self.volatility_sigma(domain)
        if sigma <= 1e-12:
            return 1.0
        return clamp(self.rng.lognormvariate(-0.5 * sigma * sigma, sigma), 0.35, 3.5)

    def apply_global_volatility_shocks(self) -> None:
        truth_sigma = self.volatility_sigma("truth")
        fiat_sigma = self.volatility_sigma("fiat")
        if truth_sigma <= 1e-12 and fiat_sigma <= 1e-12:
            return
        for agent in self.agents.values():
            if truth_sigma > 1e-12:
                for layer in ALL_TRUTH_LAYERS:
                    base = max(1.0, abs(agent.truth[layer]))
                    agent.truth[layer] += base * self.rng.gauss(0.0, truth_sigma)
            if fiat_sigma > 1e-12:
                for cur, amount in list(agent.fiat.items()):
                    if amount > 0:
                        agent.fiat[cur] = max(0.0, amount * clamp(1.0 + self.rng.gauss(0.0, fiat_sigma), 0.2, 4.0))
                for cur, amount in list(agent.debt.items()):
                    if amount > 0:
                        agent.debt[cur] = max(0.0, amount * clamp(1.0 + self.rng.gauss(0.0, fiat_sigma), 0.2, 4.0))

    # ----- Export ------------------------------------------------------------

    def summary_dict(self) -> Dict[str, Any]:
        planet_gdp, tv = self.planetary_aggregates()
        return {
            "preset": self.preset,
            "seed": self.seed,
            "months": self.months,
            "agents": len(self.agents),
            "countries": self.config["country_count"],
            "planet_gdp": planet_gdp,
            "truth_score": tv.weighted_score(),
            "truth_positive": tv.positive_score(),
            "truth_debt": tv.debt_score(),
            "events": len(self.events),
            "economic_morphisms": len(self.economic_category.morphisms),
            "truth_morphisms": len(self.truth_category.morphisms),
            "legal_morphisms": len(self.legal_category.morphisms),
            "security_morphisms": len(self.security_category.morphisms),
            "networks": {name: {"nodes": len(net.nodes), "edges": len(net.channels), "density": net.density(), "delivered": net.delivered_total, "queue_depth": net.queue_depth()} for name, net in self.networks.items()},
            "last_sheaf_gap": self.last_sheaf_gap,
            "natural_transformations": {nt.name: nt.last_naturality_gap for nt in self.natural_transformations},
            "universal_properties": {up.name: up.last_gap for up in self.universal_properties},
            "parallel": self.parallel.summary(),
            "language": self.lang,
            "volatility": self.volatility,
            "truth_volatility": self.truth_volatility,
            "fiat_volatility": self.fiat_volatility,
        }

    def write_outputs(self) -> None:
        self.out_dir.mkdir(parents=True, exist_ok=True)
        with (self.out_dir / "history.csv").open("w", newline="", encoding="utf-8") as f:
            if self.history:
                writer = csv.DictWriter(f, fieldnames=list(self.history[0].keys()))
                writer.writeheader()
                writer.writerows(self.history)
        with (self.out_dir / "agents.csv").open("w", newline="", encoding="utf-8") as f:
            fieldnames = ["id", "name", "class", "home_currency", "fiat", "debt", "truth_score", "truth_debt", "tags"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            agents = list(self.agents.values())
            if self.can_parallel(len(agents), min_items=64):
                rows = self.parallel_map(_agent_export_row_worker, agents, min_items=64)
            else:
                rows = [_agent_export_row_worker(a) for a in agents]
            writer.writerows(rows)
        with (self.out_dir / "morphisms.csv").open("w", newline="", encoding="utf-8") as f:
            fieldnames = ["id", "category", "source", "target", "name", "kind", "fiat_value", "truth_score"]
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            morphism_tasks = [(category.name, m) for category in [self.economic_category, self.truth_category, self.legal_category, self.security_category] for m in category.morphisms]
            if self.can_parallel(len(morphism_tasks), min_items=256):
                rows = self.parallel_map(_morphism_export_row_worker, morphism_tasks, min_items=256)
            else:
                rows = [_morphism_export_row_worker(t) for t in morphism_tasks]
            writer.writerows(rows)
        with (self.out_dir / "events.json").open("w", encoding="utf-8") as f:
            json.dump(self.events, f, ensure_ascii=False, indent=2)
        with (self.out_dir / "summary.json").open("w", encoding="utf-8") as f:
            json.dump(self.summary_dict(), f, ensure_ascii=False, indent=2)
        art = self.render_art_report()
        with (self.out_dir / "utf8_paradigm_architecture_report.txt").open("w", encoding="utf-8") as f:
            f.write(art)
        summary = self.render_summary_text() + "\n\n" + art
        with (self.out_dir / "summary.txt").open("w", encoding="utf-8") as f:
            f.write(summary)

    def render_summary_text(self, color: bool = False) -> str:
        data = self.summary_dict()
        lines = [
            "Planetare Wirtschaftssimulation — Paradigma-Architektur-Edition",
            "=" * 72,
            f"Preset: {data['preset']} | Seed: {data['seed']} | Monate: {data['months']} | Sprache={data['language']}",
            f"Agenten: {data['agents']} | Länder: {data['countries']} | Events: {data['events']}",
            f"Planet-GDP: {fmt(data['planet_gdp'])}",
            f"WK-Score: {data['truth_score']:.2f} | WK-positiv: {data['truth_positive']:.2f} | Wahrheitsschuld: {data['truth_debt']:.2f}",
            f"Volatilität: Gesamt={data['volatility']:.2f} | WK={data['truth_volatility']:.2f} | Fiat={data['fiat_volatility']:.2f}",
            f"Morphismen: Economy={data['economic_morphisms']} Truth={data['truth_morphisms']} Law={data['legal_morphisms']} Security={data['security_morphisms']}",
            f"Letzte Garben-Konsistenzlücke: {data['last_sheaf_gap']:.4f}",
            f"Parallel: Prozesse={data['parallel']['workers']} Start={data['parallel']['start_method']} Batches={data['parallel']['parallel_batches']} Tasks={data['parallel']['parallel_tasks']} Fallback={data['parallel']['fallback_batches']}",
        ]
        out = self.localize_output("\n".join(lines))
        return self.apply_color_to_output(out, color)

    def render_art_report(self, color: bool = False) -> str:
        parts = [r.render(self) for r in self.renderers]
        out = self.localize_output("\n\n".join(parts))
        return self.apply_color_to_output(out, color)


# =============================================================================
# 11. CLI
# =============================================================================


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Planetare Wirtschaftssimulation als Paradigma-Architektur")
    p.add_argument("--preset", choices=sorted(PRESETS), default="tiny")
    p.add_argument("--months", type=int, default=24)
    p.add_argument("--seed", type=int, default=7)
    p.add_argument("--out", type=str, default="paradigm_world")
    p.add_argument("--verbose", action="store_true")
    p.add_argument("--lang", choices=["en", "de"], default="en", help="Ausgabesprache / output language; default: en")
    p.add_argument("--volatility", type=float, default=1.0, help="Globale Volatilität der Simulation")
    p.add_argument("--truth-volatility", type=float, default=1.0, help="Volatilität der planetaren Wahrheitswährung WK")
    p.add_argument("--fiat-volatility", type=float, default=1.0, help="Volatilität der Landes-/Fiat-Währungen")
    color_group = p.add_mutually_exclusive_group()
    color_group.add_argument("--color", dest="color_output", action="store_true", default=True, help="Bunte ANSI-Ausgabe aktivieren; Standard: aktiv")
    color_group.add_argument("--no-color", dest="color_output", action="store_false", help="Bunte ANSI-Ausgabe deaktivieren")
    art_group = p.add_mutually_exclusive_group()
    art_group.add_argument("--print-art", dest="print_art", action="store_true", default=True, help="UTF-8-Art nach dem Lauf ausgeben; Standard: aktiv")
    art_group.add_argument("--no-print-art", dest="print_art", action="store_false", help="UTF-8-Art auf stdout unterdrücken; Dateien werden trotzdem geschrieben")
    p.add_argument("--workers", "--processes", dest="workers", default="auto", help="Anzahl PyPy3-/multiprocessing-Prozesse; auto oder 1 für seriell")
    p.add_argument("--mp-start-method", choices=["auto", "fork", "spawn", "forkserver"], default="auto", help="multiprocessing-Startmethode")
    p.add_argument("--parallel-min-items", type=int, default=16, help="Mindestgröße eines Batches für Prozessparallelisierung")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    sim = PlanetaryParadigmSimulation(
        args.preset,
        args.months,
        args.seed,
        args.out,
        args.verbose,
        workers=args.workers,
        mp_start_method=args.mp_start_method,
        parallel_min_items=args.parallel_min_items,
        lang=args.lang,
        color_output=args.color_output,
        volatility=args.volatility,
        truth_volatility=args.truth_volatility,
        fiat_volatility=args.fiat_volatility,
    )
    try:
        sim.run()
        sim.write_outputs()
        if args.print_art:
            print(sim.render_summary_text(color=args.color_output))
            print()
            print(sim.render_art_report(color=args.color_output))
        else:
            print(sim.render_summary_text(color=args.color_output))
            print(f"\nOutput: {Path(args.out).resolve()}")
    finally:
        sim.parallel.shutdown()


if __name__ == "__main__":
    main()
