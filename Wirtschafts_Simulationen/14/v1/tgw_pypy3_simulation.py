#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Topologische Gruppenwirtschaft / Topological Group Economy Simulation
=====================================================================

PyPy3-compatible, stdlib-only simulation of an economy with exactly one
currency: LZ (Loesungszahl / solution number).

Core model:
    - Algebraic group: additive real-valued group, represented by Python floats.
      Balances can become positive or negative.
    - Topology: economic/problem domains are open sets of tags. Compatibility,
      fusion and transferability are derived from overlaps between open sets.
    - Stack: a list of layers (open set + group value). The numeric value of a
      stack is the sum of group values. The domain of a stack is the intersection
      of its layer domains.

No second currency exists. Internally the code distinguishes transaction history,
problem funds, escrows and balances, but all are denominated in the same LZ unit.

Run examples:
    pypy3 tgw_pypy3_simulation.py --ticks 200 --seed 7 --report-every 20
    pypy3 tgw_pypy3_simulation.py --scenario conflict --ticks 300 --json-out final.json
    pypy3 tgw_pypy3_simulation.py --scenario intergalactic --galaxies 5 --ticks 400 --csv-out series.csv

Author: generated from the user's TGW design discussion.
"""

from __future__ import print_function

import argparse
import csv
import heapq
import json
import math
import os
import random
import statistics
import sys
import textwrap
from collections import Counter, defaultdict, deque
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional, Set, FrozenSet, Any

LZ = float
EPS = 1e-9


def clamp(x: float, lo: float, hi: float) -> float:
    if x < lo:
        return lo
    if x > hi:
        return hi
    return x


def safe_div(a: float, b: float, default: float = 0.0) -> float:
    if abs(b) < EPS:
        return default
    return a / b


def fmt_lz(x: float) -> str:
    sign = "" if x < 0 else "+"
    ax = abs(x)
    if ax >= 1_000_000_000:
        return "%s%.2fB LZ" % (sign, x / 1_000_000_000.0)
    if ax >= 1_000_000:
        return "%s%.2fM LZ" % (sign, x / 1_000_000.0)
    if ax >= 1_000:
        return "%s%.2fk LZ" % (sign, x / 1_000.0)
    return "%s%.2f LZ" % (sign, x)


def weighted_choice(rng: random.Random, items: List[Any], weights: List[float]) -> Any:
    if not items:
        return None
    total = sum(max(0.0, w) for w in weights)
    if total <= EPS:
        return rng.choice(items)
    r = rng.random() * total
    acc = 0.0
    for item, w in zip(items, weights):
        acc += max(0.0, w)
        if acc >= r:
            return item
    return items[-1]


@dataclass(frozen=True)
class Location:
    galaxy: int
    planet: int
    state: int

    def cell(self) -> Tuple[int, int, int]:
        return (self.galaxy, self.planet, self.state)

    def short(self) -> str:
        if self.galaxy < 0:
            return "GLOBAL"
        return "G%d:P%d:S%d" % (self.galaxy, self.planet, self.state)


@dataclass(frozen=True)
class OpenSet:
    """A finite representation of a topological open set.

    The real model would use a mathematical topology tau over a problem space X.
    In this simulation, an open set is represented by a non-empty set of domain
    tags. Intersections and unions are the operations we need for compatibility.
    """

    name: str
    tags: FrozenSet[str]

    def is_empty(self) -> bool:
        return len(self.tags) == 0

    def intersects(self, other: "OpenSet") -> bool:
        return bool(self.tags.intersection(other.tags))

    def intersection(self, other: "OpenSet") -> "OpenSet":
        tags = frozenset(self.tags.intersection(other.tags))
        name = "(%s ∩ %s)" % (self.name, other.name)
        return OpenSet(name, tags)

    def union(self, other: "OpenSet") -> "OpenSet":
        tags = frozenset(self.tags.union(other.tags))
        name = "(%s ∪ %s)" % (self.name, other.name)
        return OpenSet(name, tags)

    def compact(self) -> str:
        if not self.tags:
            return "∅"
        return "{" + ",".join(sorted(self.tags)) + "}"


class Topology:
    """Problem topology.

    Compatibility is not magic. It is computed from overlaps and adjacency of
    domain tags. Direct overlap means a solution can probably transfer. Adjacency
    means an adapter/bridge is needed.
    """

    BASE_TAGS = [
        "energy",
        "water",
        "food",
        "health",
        "housing",
        "infrastructure",
        "environment",
        "security",
        "governance",
        "finance",
        "labor",
        "education",
        "logistics",
        "communication",
        "research",
        "industry",
        "law",
        "diplomacy",
        "culture",
        "transport",
    ]

    ADJACENCY = {
        "energy": ["infrastructure", "industry", "environment", "transport"],
        "water": ["health", "environment", "food", "infrastructure"],
        "food": ["water", "health", "logistics", "environment", "labor"],
        "health": ["water", "food", "housing", "education", "law"],
        "housing": ["health", "infrastructure", "labor", "law"],
        "infrastructure": ["energy", "water", "housing", "transport", "communication", "logistics"],
        "environment": ["energy", "water", "food", "law", "research"],
        "security": ["governance", "law", "diplomacy", "communication"],
        "governance": ["security", "law", "finance", "diplomacy", "education"],
        "finance": ["governance", "industry", "labor", "research"],
        "labor": ["industry", "education", "housing", "food", "finance"],
        "education": ["labor", "research", "health", "culture", "governance"],
        "logistics": ["transport", "food", "industry", "infrastructure"],
        "communication": ["infrastructure", "security", "research", "culture"],
        "research": ["education", "communication", "environment", "finance", "industry"],
        "industry": ["energy", "labor", "finance", "logistics", "research"],
        "law": ["governance", "security", "environment", "housing", "health"],
        "diplomacy": ["governance", "security", "culture", "communication"],
        "culture": ["education", "diplomacy", "communication"],
        "transport": ["logistics", "infrastructure", "energy"],
    }

    SECTORS = {
        "energy": ["energy", "infrastructure", "industry"],
        "water": ["water", "health", "environment", "infrastructure"],
        "food": ["food", "water", "logistics", "labor"],
        "health": ["health", "education", "law"],
        "housing": ["housing", "infrastructure", "labor"],
        "infrastructure": ["infrastructure", "transport", "communication"],
        "environment": ["environment", "water", "energy", "law"],
        "security": ["security", "law", "governance"],
        "governance": ["governance", "law", "finance"],
        "finance": ["finance", "governance", "industry"],
        "labor": ["labor", "education", "industry"],
        "education": ["education", "research", "labor"],
        "logistics": ["logistics", "transport", "food", "industry"],
        "communication": ["communication", "infrastructure", "research"],
        "research": ["research", "education", "industry", "communication"],
        "industry": ["industry", "energy", "labor", "finance"],
        "law": ["law", "governance", "security"],
        "diplomacy": ["diplomacy", "governance", "security", "culture"],
        "culture": ["culture", "education", "communication"],
        "transport": ["transport", "logistics", "infrastructure", "energy"],
    }

    def __init__(self) -> None:
        # Symmetrize adjacency.
        adj = defaultdict(set)
        for a, bs in self.ADJACENCY.items():
            for b in bs:
                adj[a].add(b)
                adj[b].add(a)
        self.adj = {k: frozenset(v) for k, v in adj.items()}

    def open_set(self, name: str, tags: List[str], radius: int = 0) -> OpenSet:
        current = set(t for t in tags if t in self.BASE_TAGS)
        frontier = set(current)
        for _ in range(radius):
            new_frontier = set()
            for tag in frontier:
                new_frontier.update(self.adj.get(tag, ()))
            new_frontier.difference_update(current)
            current.update(new_frontier)
            frontier = new_frontier
        return OpenSet(name, frozenset(current))

    def random_sector(self, rng: random.Random) -> OpenSet:
        sector = rng.choice(list(self.SECTORS.keys()))
        return self.open_set(sector, self.SECTORS[sector], radius=0)

    def random_problem_domain(self, rng: random.Random, crisis_bias: float = 0.0) -> OpenSet:
        crisis = ["security", "infrastructure", "energy", "water", "health", "food", "environment", "governance"]
        tags = crisis if rng.random() < crisis_bias else list(self.SECTORS.keys())
        sector = rng.choice(tags)
        base = list(self.SECTORS[sector])
        if rng.random() < 0.35:
            # Add a related tag to make richer open sets.
            tag = rng.choice(base)
            related = list(self.adj.get(tag, ()))
            if related:
                base.append(rng.choice(related))
        return self.open_set("problem:%s" % sector, base, radius=0)

    def compatibility(self, a: OpenSet, b: OpenSet) -> float:
        """0..1: direct topological fit between two open sets."""
        if a.is_empty() or b.is_empty():
            return 0.0
        inter = a.tags.intersection(b.tags)
        if inter:
            # Cosine-like overlap. With 1 common tag in 3x4 sets: ~0.29.
            return clamp(len(inter) / math.sqrt(float(len(a.tags) * len(b.tags))), 0.0, 1.0)
        # No direct overlap: count adjacency edges. This is a weak bridge signal.
        edges = 0
        for x in a.tags:
            ax = self.adj.get(x, frozenset())
            edges += len(ax.intersection(b.tags))
        denom = float(max(1, len(a.tags) * len(b.tags)))
        return clamp(0.30 * edges / denom, 0.0, 0.30)

    def needs_adapter(self, a: OpenSet, b: OpenSet) -> bool:
        return not a.intersects(b) and self.compatibility(a, b) > 0.0

    def adapter_domain(self, a: OpenSet, b: OpenSet) -> OpenSet:
        # The adapter lives in a small union of the two boundaries.
        tags = set()
        for x in a.tags:
            for y in b.tags:
                if y in self.adj.get(x, frozenset()):
                    tags.add(x)
                    tags.add(y)
        if not tags:
            tags = set(a.tags).union(b.tags)
        return OpenSet("adapter", frozenset(tags))


@dataclass
class StackLayer:
    domain: OpenSet
    value: LZ
    note: str = ""


@dataclass
class Stack:
    layers: List[StackLayer] = field(default_factory=list)

    def value(self) -> LZ:
        return sum(layer.value for layer in self.layers)

    def domain(self) -> OpenSet:
        if not self.layers:
            return OpenSet("empty-stack-domain", frozenset())
        d = self.layers[0].domain
        for layer in self.layers[1:]:
            d = d.intersection(layer.domain)
        return d

    def fuse(self, other: "Stack") -> "Stack":
        return Stack(list(self.layers) + list(other.layers))

    def inverse(self, note_suffix: str = "inverse") -> "Stack":
        return Stack([StackLayer(layer.domain, -layer.value, "%s | %s" % (layer.note, note_suffix)) for layer in self.layers])

    def compact(self) -> str:
        return "Stack(value=%s, domain=%s, layers=%d)" % (fmt_lz(self.value()), self.domain().compact(), len(self.layers))


@dataclass
class Transaction:
    tick: int
    from_id: int
    to_id: int
    amount: LZ
    kind: str
    note: str


class Actor:
    """Economic actor: person, firm, bank, state, fund, auditor, clearinghouse."""

    __slots__ = (
        "id",
        "name",
        "kind",
        "location",
        "sector",
        "balance",
        "reputation",
        "integrity",
        "productivity",
        "risk_appetite",
        "skills",
        "employees",
        "employer_id",
        "bank_id",
        "tax_rate",
        "active",
        "last_income",
        "last_expense",
        "stack_events",
        "loan_ids",
        "tags",
        "bankruptcy_count",
    )

    def __init__(self, actor_id: int, name: str, kind: str, location: Location, sector: OpenSet) -> None:
        self.id = actor_id
        self.name = name
        self.kind = kind
        self.location = location
        self.sector = sector
        self.balance = 0.0
        self.reputation = 0.0
        self.integrity = 0.90
        self.productivity = 1.0
        self.risk_appetite = 0.5
        self.skills = defaultdict(float)  # tag -> skill 0..2
        self.employees: List[int] = []
        self.employer_id: Optional[int] = None
        self.bank_id: Optional[int] = None
        self.tax_rate = 0.10
        self.active = True
        self.last_income = 0.0
        self.last_expense = 0.0
        self.stack_events: List[Tuple[int, Stack]] = []
        self.loan_ids: List[int] = []
        self.tags: Set[str] = set()
        self.bankruptcy_count = 0

    def add_stack_event(self, tick: int, stack: Stack) -> None:
        self.stack_events.append((tick, stack))
        # Stack history affects reputation, but we keep it bounded enough for simulation.
        self.reputation += clamp(stack.value() / 2500.0, -20.0, 20.0)
        self.reputation = clamp(self.reputation, -1000.0, 1000.0)
        if len(self.stack_events) > 200:
            self.stack_events.pop(0)

    def skill_for(self, domain: OpenSet) -> float:
        if not domain.tags:
            return 0.0
        return sum(self.skills.get(tag, 0.0) for tag in domain.tags) / float(len(domain.tags))

    def short(self) -> str:
        return "%s[%d]" % (self.name, self.id)

    def summary(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "kind": self.kind,
            "location": self.location.short(),
            "balance_lz": round(self.balance, 3),
            "reputation": round(self.reputation, 3),
            "integrity": round(self.integrity, 3),
            "productivity": round(self.productivity, 3),
            "sector": self.sector.name,
            "active": self.active,
            "employees": len(self.employees),
        }


@dataclass
class Problem:
    id: int
    title: str
    domain: OpenSet
    severity: LZ  # positive magnitude of remaining problem
    owner_id: int
    fund_id: int
    created_by_id: Optional[int]
    location: Location
    cause: str
    created_tick: int
    status: str = "open"  # open, in_progress, resolved
    priority: float = 1.0
    age: int = 0
    assigned_project_id: Optional[int] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    history: List[Tuple[int, str, float]] = field(default_factory=list)

    def negative_stack(self) -> Stack:
        return Stack([StackLayer(self.domain, -self.severity, "problem:%s" % self.title)])

    def compact(self) -> str:
        return "P%d %s sev=%s %s %s" % (self.id, self.title, fmt_lz(-self.severity), self.domain.compact(), self.status)


@dataclass
class Project:
    id: int
    problem_id: int
    solver_id: int
    payer_id: int
    price: LZ
    promised_reduction: LZ
    actual_reduction: LZ
    topological_fit: float
    start_tick: int
    end_tick: int
    status: str = "active"  # active, completed, audited
    fraudulent: bool = False
    remote: bool = False
    escrowed: bool = False
    audit_due_tick: int = 0
    note: str = ""


@dataclass
class Loan:
    id: int
    bank_id: int
    borrower_id: int
    principal: LZ
    outstanding: LZ
    rate: float
    start_tick: int
    due_tick: int
    status: str = "active"


class Ledger:
    def __init__(self, sim: "Simulation") -> None:
        self.sim = sim
        self.transactions: List[Transaction] = []
        self.kind_counter = Counter()

    def transfer(self, from_id: int, to_id: int, amount: LZ, kind: str, note: str = "") -> bool:
        """Group operation: subtract from one account, add to another."""
        if amount < 0:
            return self.transfer(to_id, from_id, -amount, kind, note + " (reversed negative amount)")
        if amount <= EPS:
            return False
        actors = self.sim.actors
        actors[from_id].balance -= amount
        actors[to_id].balance += amount
        actors[from_id].last_expense += amount
        actors[to_id].last_income += amount
        tx = Transaction(self.sim.tick, from_id, to_id, amount, kind, note[:200])
        self.transactions.append(tx)
        self.kind_counter[kind] += 1
        if len(self.transactions) > self.sim.config.max_transactions_kept:
            self.transactions.pop(0)
        return True

    def stack_event(self, actor_id: int, stack: Stack) -> None:
        self.sim.actors[actor_id].add_stack_event(self.sim.tick, stack)


@dataclass
class Config:
    ticks: int = 250
    seed: int = 42
    scenario: str = "baseline"
    galaxies: int = 3
    planets_per_galaxy: int = 3
    states_per_planet: int = 2
    households: int = 300
    firms: int = 70
    report_every: int = 25
    initial_problems_per_state: int = 5
    max_projects_started_per_tick: int = 18
    max_active_projects: int = 80
    intergalactic_delay: int = 18
    remote_project_probability: float = 0.08
    war_probability: float = 0.004
    fraud_pressure: float = 1.0
    externality_rate: float = 1.0
    credit_leverage: float = 4.0
    max_transactions_kept: int = 20000
    csv_out: str = ""
    json_out: str = ""
    quiet: bool = False


class Simulation:
    def __init__(self, config: Config) -> None:
        self.config = config
        self.rng = random.Random(config.seed)
        self.topology = Topology()
        self.tick = 0
        self.next_actor_id = 1
        self.next_problem_id = 1
        self.next_project_id = 1
        self.next_loan_id = 1
        self.actors: Dict[int, Actor] = {}
        self.by_kind: Dict[str, List[int]] = defaultdict(list)
        self.states: List[int] = []
        self.banks: List[int] = []
        self.firms: List[int] = []
        self.households: List[int] = []
        self.auditors: List[int] = []
        self.repair_funds_by_cell: Dict[Tuple[int, int, int], int] = {}
        self.banks_by_cell: Dict[Tuple[int, int, int], List[int]] = defaultdict(list)
        self.firms_by_cell: Dict[Tuple[int, int, int], List[int]] = defaultdict(list)
        self.households_by_cell: Dict[Tuple[int, int, int], List[int]] = defaultdict(list)
        self.problems: Dict[int, Problem] = {}
        self.open_problem_ids: Set[int] = set()
        self.projects: Dict[int, Project] = {}
        self.active_project_ids: Set[int] = set()
        self.audit_queue: List[Tuple[int, int]] = []
        self.loans: Dict[int, Loan] = {}
        self.tension: Dict[Tuple[int, int], float] = {}
        self.metrics: List[Dict[str, Any]] = []
        self.events: deque = deque(maxlen=300)
        self.ledger = Ledger(self)
        self.cumulative_solved_value = 0.0
        self.cumulative_damage_value = 0.0
        self.cumulative_fraud_penalty = 0.0
        self.cumulative_war_damage = 0.0
        self.cumulative_bridge_value = 0.0
        self.war_events = 0
        self.fraud_cases_detected = 0
        self.bankruptcy_events = 0
        self.clearinghouse_id = -1
        self.escrow_id = -1
        self.universal_repair_id = -1
        self._setup_world()

    # ------------------------------------------------------------------
    # Setup
    # ------------------------------------------------------------------
    def _new_actor(self, name: str, kind: str, location: Location, sector: Optional[OpenSet] = None) -> int:
        actor_id = self.next_actor_id
        self.next_actor_id += 1
        if sector is None:
            sector = self.topology.open_set(kind, [], radius=0)
        actor = Actor(actor_id, name, kind, location, sector)
        self.actors[actor_id] = actor
        self.by_kind[kind].append(actor_id)
        return actor_id

    def _issue_initial(self, actor_id: int, amount: float, note: str) -> None:
        self.ledger.transfer(self.clearinghouse_id, actor_id, amount, "genesis_endowment", note)

    def _setup_world(self) -> None:
        # Special global actors. The clearinghouse can be negative: initial positive balances
        # are offset by a negative public genesis stack. Still one currency, still group addition.
        global_loc = Location(-1, -1, -1)
        self.clearinghouse_id = self._new_actor("Universal Clearinghouse", "clearinghouse", global_loc, self.topology.open_set("clearing", ["finance", "governance"], 0))
        self.escrow_id = self._new_actor("Intergalactic Escrow", "escrow", global_loc, self.topology.open_set("escrow", ["finance", "law", "communication"], 0))
        self.universal_repair_id = self._new_actor("Universal Repair Reserve", "repair_fund", global_loc, self.topology.open_set("repair", ["environment", "infrastructure", "health"], 0))
        self.actors[self.clearinghouse_id].balance = 0.0
        self.actors[self.escrow_id].balance = 0.0
        self.actors[self.universal_repair_id].balance = 0.0

        # Apply scenario-specific knobs.
        if self.config.scenario == "conflict":
            self.config.war_probability *= 5.0
            self.config.remote_project_probability *= 0.65
        elif self.config.scenario == "fraud":
            self.config.fraud_pressure *= 2.3
            self.config.externality_rate *= 1.3
        elif self.config.scenario == "intergalactic":
            self.config.remote_project_probability *= 2.3
            self.config.intergalactic_delay = max(8, self.config.intergalactic_delay)
        elif self.config.scenario == "scarcity":
            self.config.initial_problems_per_state += 3
            self.config.externality_rate *= 1.5

        # States, local repair funds, banks, auditors.
        for g in range(self.config.galaxies):
            auditor = self._new_actor(
                "Auditor-G%d" % g,
                "auditor",
                Location(g, -1, -1),
                self.topology.open_set("audit", ["law", "finance", "research", "governance"], 0),
            )
            self.auditors.append(auditor)
            self.actors[auditor].integrity = self.rng.uniform(0.75, 0.98)
            self.actors[auditor].productivity = self.rng.uniform(0.8, 1.4)
            self._issue_initial(auditor, self.rng.uniform(2_000, 8_000), "auditor capitalization")

            for p in range(self.config.planets_per_galaxy):
                for s in range(self.config.states_per_planet):
                    loc = Location(g, p, s)
                    state_sector = self.topology.open_set("state-domain", ["governance", "law", "security", "infrastructure", "finance"], 0)
                    state_id = self._new_actor("State-G%dP%dS%d" % (g, p, s), "state", loc, state_sector)
                    state = self.actors[state_id]
                    state.tax_rate = self.rng.uniform(0.08, 0.18)
                    state.integrity = self.rng.uniform(0.55, 0.96)
                    state.productivity = self.rng.uniform(0.7, 1.2)
                    state.risk_appetite = self.rng.uniform(0.2, 0.75)
                    self.states.append(state_id)
                    self._issue_initial(state_id, self.rng.uniform(20_000, 90_000), "state initial fiscal capacity")

                    fund_id = self._new_actor("RepairFund-G%dP%dS%d" % (g, p, s), "repair_fund", loc, self.topology.open_set("local-repair", ["environment", "infrastructure", "health", "law"], 0))
                    fund = self.actors[fund_id]
                    fund.integrity = self.rng.uniform(0.7, 0.98)
                    self.repair_funds_by_cell[loc.cell()] = fund_id
                    self._issue_initial(fund_id, self.rng.uniform(2_000, 10_000), "local repair reserve")

                    bank_id = self._new_actor("Bank-G%dP%dS%d" % (g, p, s), "bank", loc, self.topology.open_set("bank", ["finance", "law", "governance"], 0))
                    bank = self.actors[bank_id]
                    bank.integrity = self.rng.uniform(0.60, 0.97)
                    bank.productivity = self.rng.uniform(0.8, 1.3)
                    bank.risk_appetite = self.rng.uniform(0.3, 0.9)
                    self.banks.append(bank_id)
                    self.banks_by_cell[loc.cell()].append(bank_id)
                    self._issue_initial(bank_id, self.rng.uniform(30_000, 120_000), "bank reserve")

        # Firms.
        all_cells = list(self.repair_funds_by_cell.keys())
        for i in range(self.config.firms):
            cell = self.rng.choice(all_cells)
            loc = Location(*cell)
            sector = self.topology.random_sector(self.rng)
            firm_id = self._new_actor("Firm-%03d-%s" % (i + 1, sector.name), "firm", loc, sector)
            firm = self.actors[firm_id]
            firm.productivity = self.rng.lognormvariate(0.0, 0.23)
            firm.integrity = clamp(self.rng.betavariate(8, 2) / self.config.fraud_pressure, 0.25, 0.99)
            firm.risk_appetite = self.rng.uniform(0.2, 0.9)
            for tag in sector.tags:
                firm.skills[tag] = self.rng.uniform(0.7, 1.8) * firm.productivity
            # Some firms are bridge/research specialists.
            if self.rng.random() < 0.12:
                firm.tags.add("bridge_builder")
                for tag in self.rng.sample(Topology.BASE_TAGS, 4):
                    firm.skills[tag] = max(firm.skills[tag], self.rng.uniform(0.5, 1.2))
            bank_options = self.banks_by_cell[cell]
            firm.bank_id = self.rng.choice(bank_options) if bank_options else self.rng.choice(self.banks)
            self.firms.append(firm_id)
            self.firms_by_cell[cell].append(firm_id)
            self._issue_initial(firm_id, self.rng.uniform(1_500, 15_000), "firm working capital")

        # Households / workers.
        for i in range(self.config.households):
            cell = self.rng.choice(all_cells)
            loc = Location(*cell)
            skill_tag = self.rng.choice(Topology.BASE_TAGS)
            sector = self.topology.open_set("worker:%s" % skill_tag, [skill_tag], 0)
            hh_id = self._new_actor("Household-%03d" % (i + 1), "household", loc, sector)
            hh = self.actors[hh_id]
            hh.integrity = self.rng.uniform(0.75, 0.99)
            hh.productivity = self.rng.lognormvariate(0.0, 0.18)
            # Workers have a few skills, not one universal ability.
            hh.skills[skill_tag] = self.rng.uniform(0.6, 1.7)
            for tag in self.rng.sample(Topology.BASE_TAGS, self.rng.randint(1, 3)):
                hh.skills[tag] = max(hh.skills[tag], self.rng.uniform(0.1, 0.9))
            hh.bank_id = self.rng.choice(self.banks_by_cell[cell]) if self.banks_by_cell[cell] else self.rng.choice(self.banks)
            self.households.append(hh_id)
            self.households_by_cell[cell].append(hh_id)
            self._issue_initial(hh_id, self.rng.uniform(100, 1_800), "household starting balance")

        # Initial labor matching and initial problem formalization.
        self.match_labor_market(initial=True)
        for state_id in list(self.states):
            state = self.actors[state_id]
            for j in range(self.config.initial_problems_per_state):
                domain = self.topology.random_problem_domain(self.rng, crisis_bias=0.65)
                severity = self.rng.uniform(400, 4_000)
                title = "initial-%s-%d" % (domain.name.replace("problem:", ""), j + 1)
                self.create_problem(
                    owner_id=state_id,
                    created_by_id=state_id,
                    location=state.location,
                    domain=domain,
                    severity=severity,
                    cause="initial_structural_problem",
                    title=title,
                    formalize_transfer=True,
                )

        # Pairwise tensions between states. Nearby states have more interaction.
        for i, a in enumerate(self.states):
            for b in self.states[i + 1:]:
                la = self.actors[a].location
                lb = self.actors[b].location
                base = 0.04
                if la.galaxy == lb.galaxy:
                    base += 0.05
                if la.planet == lb.planet and la.galaxy == lb.galaxy:
                    base += 0.12
                if self.config.scenario == "conflict":
                    base += self.rng.uniform(0.05, 0.35)
                self.tension[self._pair(a, b)] = clamp(base + self.rng.random() * 0.12, 0.0, 2.0)

        self.capture_metrics("setup")

    # ------------------------------------------------------------------
    # Core operations
    # ------------------------------------------------------------------
    def _pair(self, a: int, b: int) -> Tuple[int, int]:
        return (a, b) if a < b else (b, a)

    def local_fund(self, loc: Location) -> int:
        return self.repair_funds_by_cell.get(loc.cell(), self.universal_repair_id)

    def galaxy_auditor(self, galaxy: int) -> int:
        candidates = [aid for aid in self.auditors if self.actors[aid].location.galaxy == galaxy]
        return candidates[0] if candidates else self.rng.choice(self.auditors)

    def galaxy_delay(self, a: int, b: int) -> int:
        if a == b:
            return self.rng.randint(1, 3)
        distance = abs(a - b) + 1
        jitter = self.rng.randint(0, max(1, self.config.intergalactic_delay // 3))
        return distance * self.config.intergalactic_delay + jitter

    def create_problem(
        self,
        owner_id: int,
        created_by_id: Optional[int],
        location: Location,
        domain: OpenSet,
        severity: LZ,
        cause: str,
        title: str,
        formalize_transfer: bool = True,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> int:
        severity = max(0.01, severity)
        pid = self.next_problem_id
        self.next_problem_id += 1
        fund_id = self.local_fund(location)
        p = Problem(
            id=pid,
            title=title,
            domain=domain,
            severity=severity,
            owner_id=owner_id,
            fund_id=fund_id,
            created_by_id=created_by_id,
            location=location,
            cause=cause,
            created_tick=self.tick,
            metadata=metadata or {},
        )
        self.problems[pid] = p
        self.open_problem_ids.add(pid)
        offender = created_by_id if created_by_id is not None else owner_id
        if formalize_transfer:
            self.ledger.transfer(offender, fund_id, severity, "problem_formalized", "%s: %s" % (cause, title))
        problem_stack = Stack([StackLayer(domain, -severity, "%s:%s" % (cause, title))])
        self.ledger.stack_event(offender, problem_stack)
        self.cumulative_damage_value += severity
        self.events.append((self.tick, "problem", title, -severity, self.actors[offender].short()))
        return pid

    def reduce_problem(self, problem_id: int, amount: LZ, solver_id: int, note: str) -> LZ:
        p = self.problems[problem_id]
        if p.status == "resolved":
            return 0.0
        reduction = clamp(amount, 0.0, p.severity)
        if reduction <= EPS:
            return 0.0
        p.severity -= reduction
        p.history.append((self.tick, note, reduction))
        solution_stack = Stack([StackLayer(p.domain, reduction, "solution:%s" % note)])
        self.ledger.stack_event(solver_id, solution_stack)
        self.cumulative_solved_value += reduction
        if p.severity <= 5.0:
            p.severity = 0.0
            p.status = "resolved"
            p.assigned_project_id = None
            self.open_problem_ids.discard(problem_id)
        return reduction

    # ------------------------------------------------------------------
    # Markets
    # ------------------------------------------------------------------
    def match_labor_market(self, initial: bool = False) -> None:
        unemployed = [hid for hid in self.households if self.actors[hid].active and self.actors[hid].employer_id is None]
        self.rng.shuffle(unemployed)
        if not unemployed:
            return
        by_cell_unemployed = defaultdict(list)
        for hid in unemployed:
            by_cell_unemployed[self.actors[hid].location.cell()].append(hid)

        for fid in self.firms:
            firm = self.actors[fid]
            if not firm.active:
                continue
            base_cap = 2 + int(max(0.0, firm.balance) / 5000.0) + int(firm.productivity * 4.0)
            if "bridge_builder" in firm.tags:
                base_cap += 1
            target = clamp(base_cap, 1, 20)
            if not initial and len(firm.employees) >= target:
                continue
            cell = firm.location.cell()
            pool = by_cell_unemployed.get(cell, [])
            if not pool:
                # Some labor migration inside same planet.
                same_planet = [hid for hid in unemployed if self.actors[hid].location.galaxy == firm.location.galaxy and self.actors[hid].location.planet == firm.location.planet]
                pool = same_planet[:]
            while pool and len(firm.employees) < target:
                # Select a worker with topological skill fit.
                weights = []
                for hid in pool:
                    worker = self.actors[hid]
                    fit = self.topology.compatibility(worker.sector, firm.sector)
                    weights.append(0.1 + fit + 0.25 * worker.skill_for(firm.sector))
                chosen = weighted_choice(self.rng, pool, weights)
                if chosen is None:
                    break
                worker = self.actors[chosen]
                worker.employer_id = fid
                firm.employees.append(chosen)
                if chosen in unemployed:
                    unemployed.remove(chosen)
                if chosen in by_cell_unemployed.get(cell, []):
                    by_cell_unemployed[cell].remove(chosen)
                if chosen in pool:
                    pool.remove(chosen)
                if not initial:
                    self.events.append((self.tick, "hire", worker.short(), 0.0, firm.short()))

    def pay_wages(self) -> None:
        for fid in list(self.firms):
            firm = self.actors[fid]
            if not firm.active or not firm.employees:
                continue
            # Wage is paid in LZ, the only currency.
            avg_skill = statistics.mean([self.actors[eid].skill_for(firm.sector) for eid in firm.employees]) if firm.employees else 0.0
            base_wage = 8.0 + 5.5 * avg_skill + 2.0 * firm.productivity
            if firm.balance < base_wage * len(firm.employees) * 0.5:
                self.request_loan(fid, base_wage * len(firm.employees) * self.rng.uniform(1.0, 2.0), "working capital for wages")
            for eid in list(firm.employees):
                worker = self.actors[eid]
                if not worker.active:
                    continue
                wage = base_wage * self.rng.uniform(0.85, 1.18) * worker.productivity
                # Firms may go negative; this is an explicit group balance, not hidden money.
                self.ledger.transfer(fid, eid, wage, "wage", "labor in %s" % firm.sector.name)

    def household_consumption(self) -> None:
        # Households buy from local firms. Negative households receive minimal state support.
        for hid in self.households:
            hh = self.actors[hid]
            if not hh.active:
                continue
            if hh.balance < -800 and self.rng.random() < 0.20:
                state_id = self.state_for_location(hh.location)
                support = self.rng.uniform(15, 60)
                self.ledger.transfer(state_id, hid, support, "welfare", "basic support despite negative balance")
            if hh.balance <= 0 and self.rng.random() > 0.18:
                continue
            spend = clamp(hh.balance * self.rng.uniform(0.004, 0.018), 1.0, self.rng.uniform(15, 90))
            local_firms = [fid for fid in self.firms_by_cell.get(hh.location.cell(), []) if self.actors[fid].active]
            if not local_firms:
                local_firms = [fid for fid in self.firms if self.actors[fid].active]
            if not local_firms:
                continue
            seller = self.rng.choice(local_firms)
            self.ledger.transfer(hid, seller, spend, "consumption", "household goods/services")

    def collect_taxes(self) -> None:
        for aid, actor in list(self.actors.items()):
            if actor.kind not in ("household", "firm", "bank") or not actor.active:
                continue
            if actor.last_income <= 0:
                continue
            state_id = self.state_for_location(actor.location)
            state = self.actors[state_id]
            tax_base = max(0.0, actor.last_income - actor.last_expense * 0.12)
            tax = tax_base * state.tax_rate
            if tax > EPS:
                self.ledger.transfer(aid, state_id, tax, "tax", "income/activity tax")

    def state_for_location(self, loc: Location) -> int:
        # Direct state id matching. In a global location fallback to first state.
        for sid in self.states:
            s = self.actors[sid]
            if s.location.cell() == loc.cell():
                return sid
        return self.states[0]

    def firm_externalities(self) -> None:
        # Production can create external negative stacks. High integrity and good sector fit reduce risk.
        for fid in list(self.firms):
            firm = self.actors[fid]
            if not firm.active:
                continue
            activity = max(0.0, firm.last_income)
            if activity <= 20:
                continue
            risk = self.config.externality_rate * (0.004 + 0.025 * (1.0 - firm.integrity)) * (1.0 + max(0.0, activity) / 30_000.0)
            if self.rng.random() < risk:
                # The problem is in local public space, but caused by the firm.
                state_id = self.state_for_location(firm.location)
                domain = self.topology.random_problem_domain(self.rng, crisis_bias=0.75)
                # Industrial sectors often harm environment/infrastructure if badly run.
                if self.rng.random() < 0.45:
                    domain = self.topology.open_set("externality", ["environment", "health", "water", "infrastructure"], 0)
                severity = self.rng.uniform(60, 650) * (1.0 + (1.0 - firm.integrity))
                self.create_problem(
                    owner_id=state_id,
                    created_by_id=fid,
                    location=firm.location,
                    domain=domain,
                    severity=severity,
                    cause="production_externality",
                    title="externality-by-%s" % firm.name,
                    formalize_transfer=True,
                )

    # ------------------------------------------------------------------
    # Problem market and projects
    # ------------------------------------------------------------------
    def available_problem_ids(self) -> List[int]:
        ids = []
        for pid in list(self.open_problem_ids):
            p = self.problems[pid]
            if p.status == "open" and p.assigned_project_id is None and p.severity > 5:
                ids.append(pid)
        ids.sort(key=lambda pid: self.problems[pid].severity * self.problems[pid].priority, reverse=True)
        return ids

    def problem_market(self) -> None:
        if len(self.active_project_ids) >= self.config.max_active_projects:
            return
        started = 0
        for pid in self.available_problem_ids()[: self.config.max_projects_started_per_tick * 3]:
            if started >= self.config.max_projects_started_per_tick:
                break
            if len(self.active_project_ids) >= self.config.max_active_projects:
                break
            p = self.problems[pid]
            solver_id, fit, remote = self.find_solver_for_problem(p)
            if solver_id is None:
                continue
            self.start_project(pid, solver_id, fit, remote)
            started += 1

    def find_solver_for_problem(self, p: Problem) -> Tuple[Optional[int], float, bool]:
        # Prefer local, then planet, then galaxy, then remote intergalactic.
        local = [fid for fid in self.firms_by_cell.get(p.location.cell(), []) if self.actors[fid].active]
        same_planet = [fid for fid in self.firms if self.actors[fid].active and self.actors[fid].location.galaxy == p.location.galaxy and self.actors[fid].location.planet == p.location.planet]
        same_galaxy = [fid for fid in self.firms if self.actors[fid].active and self.actors[fid].location.galaxy == p.location.galaxy]
        tiers = [(local, False), (same_planet, False), (same_galaxy, False)]
        # High severity unresolved problems may search other galaxies.
        if self.rng.random() < self.config.remote_project_probability or p.severity > 8_000:
            remote = [fid for fid in self.firms if self.actors[fid].active and self.actors[fid].location.galaxy != p.location.galaxy]
            tiers.append((remote, True))

        best = None
        best_score = 0.0
        best_fit = 0.0
        best_remote = False
        for candidates, remote_flag in tiers:
            if not candidates:
                continue
            sample = candidates if len(candidates) <= 60 else self.rng.sample(candidates, 60)
            for fid in sample:
                firm = self.actors[fid]
                fit = self.topology.compatibility(firm.sector, p.domain)
                skill = firm.skill_for(p.domain)
                bridge_bonus = 0.25 if "bridge_builder" in firm.tags and self.topology.needs_adapter(firm.sector, p.domain) else 0.0
                distance_penalty = 0.25 if remote_flag else 0.0
                reputation_bonus = clamp(firm.reputation / 100.0, -0.5, 0.5)
                score = fit + 0.35 * skill + bridge_bonus + 0.08 * firm.productivity + 0.05 * firm.integrity + reputation_bonus - distance_penalty
                if score > best_score and fit + skill + bridge_bonus > 0.18:
                    best = fid
                    best_score = score
                    best_fit = clamp(fit + 0.20 * bridge_bonus, 0.0, 1.0)
                    best_remote = remote_flag
            if best is not None and not best_remote:
                # A usable local/galactic solver exists; no need to scan farther.
                break
        return best, best_fit, best_remote

    def start_project(self, pid: int, solver_id: int, fit: float, remote: bool) -> None:
        p = self.problems[pid]
        firm = self.actors[solver_id]
        skill = firm.skill_for(p.domain)
        bridge = 1.0
        note_parts = []
        if self.topology.needs_adapter(firm.sector, p.domain) or (fit < 0.22 and "bridge_builder" in firm.tags):
            bridge = self.rng.uniform(0.70, 0.95) if "bridge_builder" in firm.tags else self.rng.uniform(0.45, 0.75)
            bridge_domain = self.topology.adapter_domain(firm.sector, p.domain)
            bridge_value = p.severity * (1.0 - fit) * 0.05 * bridge
            if bridge_value > 3.0:
                self.cumulative_bridge_value += bridge_value
                self.ledger.stack_event(solver_id, Stack([StackLayer(bridge_domain, bridge_value, "topological adapter created")]))
                note_parts.append("adapter")
        workforce = max(1, len(firm.employees))
        capacity = (35.0 + 28.0 * workforce + 70.0 * skill) * firm.productivity * (0.55 + fit) * bridge
        promised = clamp(capacity * self.rng.uniform(0.55, 1.35), 20.0, p.severity)
        price_factor = self.rng.uniform(0.62, 0.92) * (1.0 + max(0.0, 0.35 - fit))
        if remote:
            price_factor *= 1.15 + 0.05 * abs(firm.location.galaxy - p.location.galaxy)
        price = promised * price_factor
        # Low integrity + high pressure => more fake claims.
        fraud_probability = clamp((1.0 - firm.integrity) * 0.33 * self.config.fraud_pressure + max(0.0, price - 4_000) / 60_000.0, 0.0, 0.55)
        fraudulent = self.rng.random() < fraud_probability
        if fraudulent:
            actual = promised * self.rng.uniform(0.02, 0.38) * max(0.25, fit)
            note_parts.append("fraud-risk")
        else:
            noise = self.rng.uniform(0.65, 1.12)
            actual = promised * noise * clamp(0.45 + 0.70 * fit + 0.20 * skill, 0.20, 1.25)
        actual = clamp(actual, 0.0, p.severity)
        base_duration = 1 + int(math.sqrt(max(1.0, promised)) / 18.0)
        duration = max(1, base_duration + self.rng.randint(0, 3))
        if remote:
            duration += self.galaxy_delay(firm.location.galaxy, p.location.galaxy)
        project_id = self.next_project_id
        self.next_project_id += 1
        project = Project(
            id=project_id,
            problem_id=pid,
            solver_id=solver_id,
            payer_id=p.fund_id,
            price=price,
            promised_reduction=promised,
            actual_reduction=actual,
            topological_fit=fit,
            start_tick=self.tick,
            end_tick=self.tick + duration,
            fraudulent=fraudulent,
            remote=remote,
            escrowed=False,
            audit_due_tick=self.tick + duration + self.rng.randint(2, 10),
            note=",".join(note_parts),
        )
        self.projects[project_id] = project
        self.active_project_ids.add(project_id)
        p.status = "in_progress"
        p.assigned_project_id = project_id
        # Working capital: firms may borrow before starting.
        setup_cost = price * self.rng.uniform(0.04, 0.18)
        if firm.balance < setup_cost:
            self.request_loan(solver_id, setup_cost * 1.2, "project setup: %s" % p.title)
        # Remote projects use escrow at start. Local projects pay at completion.
        if remote:
            self.ledger.transfer(p.fund_id, self.escrow_id, price, "escrow_lock", "remote project P%d by %s" % (pid, firm.name))
            project.escrowed = True
        self.events.append((self.tick, "project_start", "P%d->%s" % (pid, firm.name), price, "remote" if remote else "local"))

    def advance_projects(self) -> None:
        for project_id in list(self.active_project_ids):
            project = self.projects[project_id]
            if project.end_tick > self.tick:
                continue
            p = self.problems[project.problem_id]
            solver = self.actors[project.solver_id]
            # Payment/release. Even if project underperforms, initial settlement can happen;
            # audits correct later with inverse stacks.
            if project.escrowed:
                self.ledger.transfer(self.escrow_id, project.solver_id, project.price, "escrow_release", "project P%d completed" % p.id)
            else:
                self.ledger.transfer(project.payer_id, project.solver_id, project.price, "project_payment", "project P%d completed" % p.id)
            reduction = self.reduce_problem(p.id, project.actual_reduction, project.solver_id, "project-%d" % project.id)
            # If actual work created side damage, record it.
            if project.fraudulent and self.rng.random() < 0.25:
                state_id = self.state_for_location(p.location)
                side_domain = self.topology.open_set("side-effect", ["law", "governance", "infrastructure"], 0)
                side_severity = project.price * self.rng.uniform(0.05, 0.22)
                self.create_problem(
                    owner_id=state_id,
                    created_by_id=project.solver_id,
                    location=p.location,
                    domain=side_domain,
                    severity=side_severity,
                    cause="solution_side_effect",
                    title="side-effect-P%d" % p.id,
                    formalize_transfer=True,
                )
            if p.status != "resolved":
                p.status = "open"
                p.assigned_project_id = None
            project.status = "completed"
            self.active_project_ids.discard(project_id)
            heapq.heappush(self.audit_queue, (project.audit_due_tick, project_id))
            solver.reputation += clamp(reduction / 1500.0, 0.0, 4.0)
            self.events.append((self.tick, "project_done", "P%d by %s" % (p.id, solver.name), reduction, "fraud?" if project.fraudulent else "ok"))

    def audit_projects(self) -> None:
        while self.audit_queue and self.audit_queue[0][0] <= self.tick:
            _, project_id = heapq.heappop(self.audit_queue)
            project = self.projects.get(project_id)
            if project is None or project.status == "audited":
                continue
            p = self.problems[project.problem_id]
            auditor_id = self.galaxy_auditor(p.location.galaxy)
            auditor = self.actors[auditor_id]
            fee = clamp(project.price * 0.015, 3.0, 180.0)
            payer = p.fund_id
            self.ledger.transfer(payer, auditor_id, fee, "audit_fee", "audit project %d" % project.id)
            detection_power = clamp(0.35 + 0.50 * auditor.integrity + 0.15 * auditor.productivity, 0.0, 0.98)
            # Honest underperformance can still be corrected, but not punished as fraud.
            underperformance_ratio = safe_div(project.actual_reduction, project.promised_reduction, 1.0)
            detected = False
            if project.fraudulent:
                detected = self.rng.random() < detection_power
            elif underperformance_ratio < 0.45:
                detected = self.rng.random() < detection_power * 0.35
            if detected:
                firm_id = project.solver_id
                missing = max(0.0, project.promised_reduction - project.actual_reduction)
                penalty = project.price * (0.65 if not project.fraudulent else 1.25) + missing * (0.18 if not project.fraudulent else 0.42)
                # Inverse stack: a false positive solution is corrected by negative LZ.
                self.ledger.transfer(firm_id, p.fund_id, penalty, "fraud_or_underperformance_penalty", "audit correction P%d" % p.id)
                correction_domain = p.domain
                self.ledger.stack_event(firm_id, Stack([StackLayer(correction_domain, -penalty, "audit inverse/correction P%d" % p.id)]))
                self.cumulative_fraud_penalty += penalty
                if project.fraudulent:
                    self.fraud_cases_detected += 1
                    self.events.append((self.tick, "fraud_detected", self.actors[firm_id].name, -penalty, "P%d" % p.id))
                else:
                    self.events.append((self.tick, "underperformance", self.actors[firm_id].name, -penalty, "P%d" % p.id))
            else:
                # Good audit outcome improves reputation mildly.
                self.actors[project.solver_id].reputation += 0.10
            project.status = "audited"

    # ------------------------------------------------------------------
    # Banks and credit
    # ------------------------------------------------------------------
    def request_loan(self, borrower_id: int, amount: LZ, reason: str) -> Optional[int]:
        if amount <= 1.0:
            return None
        borrower = self.actors[borrower_id]
        if borrower.kind == "bank":
            return None
        bank_id = borrower.bank_id
        if bank_id is None:
            cell_banks = self.banks_by_cell.get(borrower.location.cell(), [])
            bank_id = self.rng.choice(cell_banks) if cell_banks else self.rng.choice(self.banks)
            borrower.bank_id = bank_id
        bank = self.actors[bank_id]
        # Bank can go negative, but only within a leverage/risk threshold.
        credit_floor = -self.config.credit_leverage * (50_000 + max(0.0, bank.reputation) * 100.0 + max(0.0, bank.balance) * 0.5)
        risk = max(0.05, 0.45 - borrower.reputation / 300.0 + max(0.0, -borrower.balance) / 80_000.0)
        approval_score = bank.integrity * 0.55 + bank.risk_appetite * 0.35 + self.rng.random() * 0.25 - risk
        if bank.balance - amount < credit_floor or approval_score < 0.05:
            return None
        amount = clamp(amount, 10.0, 20_000.0)
        rate = clamp(0.012 + risk * 0.035 + self.rng.random() * 0.015, 0.005, 0.12)
        due = self.tick + self.rng.randint(25, 90)
        loan_id = self.next_loan_id
        self.next_loan_id += 1
        loan = Loan(loan_id, bank_id, borrower_id, amount, amount, rate, self.tick, due)
        self.loans[loan_id] = loan
        borrower.loan_ids.append(loan_id)
        bank.loan_ids.append(loan_id)
        self.ledger.transfer(bank_id, borrower_id, amount, "loan_disbursement", reason)
        stack = Stack([StackLayer(self.topology.open_set("credit", ["finance", "law"], 0), -amount, "loan liability %d" % loan_id)])
        self.ledger.stack_event(borrower_id, stack)
        return loan_id

    def service_loans(self) -> None:
        for loan_id, loan in list(self.loans.items()):
            if loan.status != "active":
                continue
            borrower = self.actors[loan.borrower_id]
            bank = self.actors[loan.bank_id]
            if not borrower.active and borrower.balance < 0:
                continue
            # Small periodic repayment if borrower can or must.
            if self.tick % 5 == 0 or self.tick >= loan.due_tick:
                interest = loan.outstanding * loan.rate / 12.0
                principal_part = loan.outstanding * (0.025 if self.tick < loan.due_tick else 0.20)
                due = interest + principal_part
                # If borrower is negative, partial payment deepens negative only if due date passed.
                if borrower.balance > due * 0.25 or self.tick >= loan.due_tick:
                    pay = min(due, max(0.0, borrower.balance * 0.45) if self.tick < loan.due_tick else due)
                    if pay > EPS:
                        self.ledger.transfer(loan.borrower_id, loan.bank_id, pay, "loan_repayment", "loan %d" % loan.id)
                        loan.outstanding = max(0.0, loan.outstanding - max(0.0, pay - interest))
                if loan.outstanding <= 5.0:
                    loan.status = "repaid"
                    borrower.reputation += 0.8
                    bank.reputation += 0.2
                elif self.tick > loan.due_tick + 90 and borrower.balance < -loan.outstanding * 0.35:
                    # Default is not deletion. It is a negative record and a bank loss signal.
                    loan.status = "defaulted"
                    borrower.reputation -= 5.0
                    bank.reputation -= 2.0
                    loss_signal = loan.outstanding * 0.15
                    self.ledger.stack_event(bank.id, Stack([StackLayer(self.topology.open_set("bad-credit", ["finance", "law"], 0), -loss_signal, "bad credit assessment loan %d" % loan.id)]))
                    self.events.append((self.tick, "loan_default", borrower.name, -loan.outstanding, bank.name))

    def handle_bankruptcies(self) -> None:
        for fid in list(self.firms):
            firm = self.actors[fid]
            if not firm.active:
                continue
            threshold = -35_000.0 * (1.0 + max(0.0, firm.reputation) / 100.0)
            if firm.balance < threshold and firm.reputation < -5.0:
                firm.active = False
                firm.bankruptcy_count += 1
                self.bankruptcy_events += 1
                for eid in list(firm.employees):
                    self.actors[eid].employer_id = None
                firm.employees = []
                # Negative history remains; no clean escape.
                stack = Stack([StackLayer(self.topology.open_set("insolvency", ["finance", "law", "labor"], 0), -abs(firm.balance) * 0.10, "bankruptcy residual")])
                self.ledger.stack_event(fid, stack)
                self.events.append((self.tick, "bankruptcy", firm.name, firm.balance, "negative balance persists"))
        # Re-match after layoffs.
        if self.tick % 8 == 0:
            self.match_labor_market(initial=False)

    # ------------------------------------------------------------------
    # Conflict system
    # ------------------------------------------------------------------
    def conflict_dynamics(self) -> None:
        if not self.tension:
            return
        # Random drift and local shocks.
        for pair in list(self.tension.keys()):
            a, b = pair
            state_a = self.actors[a]
            state_b = self.actors[b]
            same_planet = state_a.location.galaxy == state_b.location.galaxy and state_a.location.planet == state_b.location.planet
            drift = self.rng.uniform(-0.015, 0.018) + (0.010 if same_planet else 0.0)
            # High diplomacy/governance reputation lowers tension.
            rep_effect = -0.0004 * (state_a.reputation + state_b.reputation)
            self.tension[pair] = clamp(self.tension[pair] + drift + rep_effect, 0.0, 3.0)

            t = self.tension[pair]
            if t > 0.95 and self.rng.random() < 0.012:
                # Cold conflict: expensive non-hot instability.
                for sid in pair:
                    st = self.actors[sid]
                    domain = self.topology.open_set("cold-conflict", ["security", "governance", "finance", "diplomacy"], 0)
                    severity = self.rng.uniform(80, 500) * t
                    self.create_problem(
                        owner_id=sid,
                        created_by_id=sid,
                        location=st.location,
                        domain=domain,
                        severity=severity,
                        cause="cold_conflict_cost",
                        title="cold-conflict-%d-%d" % pair,
                        formalize_transfer=True,
                        metadata={"conflict_pair": list(pair)},
                    )
            war_prob = self.config.war_probability * max(0.0, t - 1.10) ** 2
            if self.rng.random() < war_prob:
                attacker, defender = (a, b) if self.rng.random() < 0.5 else (b, a)
                self.start_war_event(attacker, defender, t)

    def start_war_event(self, attacker_id: int, defender_id: int, tension: float) -> None:
        attacker = self.actors[attacker_id]
        defender = self.actors[defender_id]
        severity = self.rng.uniform(1_000, 7_000) * (1.0 + tension)
        domain = self.topology.open_set("hot-conflict-damage", ["security", "health", "infrastructure", "governance"], 0)
        self.create_problem(
            owner_id=defender_id,
            created_by_id=attacker_id,
            location=defender.location,
            domain=domain,
            severity=severity,
            cause="hot_conflict_damage",
            title="war-damage-%s-to-%s" % (attacker.name, defender.name),
            formalize_transfer=True,
            metadata={"conflict_pair": list(self._pair(attacker_id, defender_id)), "attacker": attacker_id, "defender": defender_id},
        )
        own_cost = severity * self.rng.uniform(0.15, 0.45)
        self.create_problem(
            owner_id=attacker_id,
            created_by_id=attacker_id,
            location=attacker.location,
            domain=domain,
            severity=own_cost,
            cause="war_self_cost",
            title="war-self-cost-%s" % attacker.name,
            formalize_transfer=True,
            metadata={"conflict_pair": list(self._pair(attacker_id, defender_id))},
        )
        pair = self._pair(attacker_id, defender_id)
        self.tension[pair] = clamp(self.tension.get(pair, 0.0) + 0.25, 0.0, 3.0)
        self.war_events += 1
        self.cumulative_war_damage += severity + own_cost
        self.events.append((self.tick, "hot_conflict", attacker.name, -(severity + own_cost), defender.name))

    def apply_conflict_solution_effect(self, project: Project, reduction: float) -> None:
        p = self.problems[project.problem_id]
        pair_list = p.metadata.get("conflict_pair")
        if not pair_list:
            return
        pair = self._pair(pair_list[0], pair_list[1])
        if pair not in self.tension:
            return
        if "diplomacy" in p.domain.tags or "security" in p.domain.tags or "governance" in p.domain.tags:
            delta = clamp(reduction / max(1.0, reduction + p.severity) * 0.18, 0.0, 0.22)
            self.tension[pair] = max(0.0, self.tension[pair] - delta)

    # ------------------------------------------------------------------
    # Problem aging and shocks
    # ------------------------------------------------------------------
    def age_and_generate_problems(self) -> None:
        for pid in list(self.open_problem_ids):
            p = self.problems[pid]
            if p.status == "resolved":
                continue
            p.age += 1
            # Unresolved problems usually grow. The owner/fund formalizes extra negative LZ.
            growth_rate = 0.0015 + 0.0025 * self.rng.random()
            if p.cause in ("hot_conflict_damage", "production_externality"):
                growth_rate *= 1.5
            growth = p.severity * growth_rate
            if growth > 1.0 and self.rng.random() < 0.60:
                p.severity += growth
                offender = p.created_by_id if p.created_by_id is not None else p.owner_id
                self.ledger.transfer(offender, p.fund_id, growth, "problem_growth", "unresolved growth P%d" % p.id)
                self.ledger.stack_event(offender, Stack([StackLayer(p.domain, -growth, "problem growth P%d" % p.id)]))
                self.cumulative_damage_value += growth

        # New public shocks/decay.
        new_problem_chance = 0.04 + 0.012 * self.config.initial_problems_per_state
        for sid in self.states:
            if self.rng.random() < new_problem_chance:
                state = self.actors[sid]
                domain = self.topology.random_problem_domain(self.rng, crisis_bias=0.55)
                severity = self.rng.lognormvariate(math.log(230.0), 0.75)
                severity = clamp(severity, 30.0, 3_000.0)
                self.create_problem(
                    owner_id=sid,
                    created_by_id=sid,
                    location=state.location,
                    domain=domain,
                    severity=severity,
                    cause="public_decay_or_shock",
                    title="public-shock-%s" % domain.name.replace("problem:", ""),
                    formalize_transfer=True,
                )

    # ------------------------------------------------------------------
    # Tick loop and metrics
    # ------------------------------------------------------------------
    def reset_tick_accounting(self) -> None:
        for actor in self.actors.values():
            actor.last_income = 0.0
            actor.last_expense = 0.0

    def step(self) -> None:
        self.tick += 1
        self.reset_tick_accounting()
        self.age_and_generate_problems()
        if self.tick % 4 == 0:
            self.match_labor_market(initial=False)
        self.pay_wages()
        self.household_consumption()
        self.collect_taxes()
        self.firm_externalities()
        self.conflict_dynamics()
        self.problem_market()
        self.advance_projects()
        # Apply conflict solution effect after projects completed.
        # It is safe to scan recently completed projects only by end_tick.
        for project in list(self.projects.values()):
            if project.end_tick == self.tick and project.status in ("completed", "audited"):
                self.apply_conflict_solution_effect(project, project.actual_reduction)
        self.audit_projects()
        self.service_loans()
        self.handle_bankruptcies()
        self.capture_metrics("tick")

    def run(self) -> None:
        if not self.config.quiet:
            print(self.header())
            print(self.summary_line(0))
        for _ in range(self.config.ticks):
            self.step()
            if not self.config.quiet and self.config.report_every > 0 and self.tick % self.config.report_every == 0:
                print(self.summary_line(self.tick))
        if not self.config.quiet:
            print("\n" + self.final_report())
        if self.config.csv_out:
            self.write_csv(self.config.csv_out)
        if self.config.json_out:
            self.write_json(self.config.json_out)

    def capture_metrics(self, phase: str) -> None:
        balances = [a.balance for a in self.actors.values()]
        open_sev = sum(self.problems[pid].severity for pid in self.open_problem_ids if self.problems[pid].status != "resolved")
        unemployment = sum(1 for hid in self.households if self.actors[hid].employer_id is None and self.actors[hid].active)
        active_firms = sum(1 for fid in self.firms if self.actors[fid].active)
        active_loans = sum(1 for loan in self.loans.values() if loan.status == "active")
        hot_tension = max(self.tension.values()) if self.tension else 0.0
        avg_tension = statistics.mean(self.tension.values()) if self.tension else 0.0
        metric = {
            "tick": self.tick,
            "phase": phase,
            "total_balance": sum(balances),
            "min_balance": min(balances) if balances else 0.0,
            "max_balance": max(balances) if balances else 0.0,
            "negative_actors": sum(1 for b in balances if b < 0),
            "open_problems": sum(1 for pid in self.open_problem_ids if self.problems[pid].status != "resolved"),
            "open_problem_severity": open_sev,
            "active_projects": len(self.active_project_ids),
            "completed_projects": sum(1 for p in self.projects.values() if p.status in ("completed", "audited")),
            "audited_projects": sum(1 for p in self.projects.values() if p.status == "audited"),
            "cumulative_solved_value": self.cumulative_solved_value,
            "cumulative_damage_value": self.cumulative_damage_value,
            "cumulative_fraud_penalty": self.cumulative_fraud_penalty,
            "cumulative_bridge_value": self.cumulative_bridge_value,
            "war_events": self.war_events,
            "war_damage": self.cumulative_war_damage,
            "fraud_cases_detected": self.fraud_cases_detected,
            "bankruptcies": self.bankruptcy_events,
            "unemployment": unemployment,
            "active_firms": active_firms,
            "active_loans": active_loans,
            "avg_tension": avg_tension,
            "max_tension": hot_tension,
        }
        self.metrics.append(metric)

    def header(self) -> str:
        return textwrap.dedent(
            """
            Topologische Gruppenwirtschaft / TGW Simulation
            ------------------------------------------------
            Währung: LZ = additive Gruppen-Zahl, positiv oder negativ.
            Topologie: Problem- und Lösungsbereiche als offene Mengen von Domänen-Tags.
            Szenario: {scenario}, Seed: {seed}, Galaxien: {galaxies}, Ticks: {ticks}
            """.format(
                scenario=self.config.scenario,
                seed=self.config.seed,
                galaxies=self.config.galaxies,
                ticks=self.config.ticks,
            )
        ).strip()

    def latest_metric(self) -> Dict[str, Any]:
        return self.metrics[-1]

    def summary_line(self, tick: int) -> str:
        m = self.latest_metric()
        return (
            "t={tick:4d} | actors={actors:4d} neg={neg:3d} | openP={op:4d} sev={sev:>11} "
            "| projects={proj:3d} solved={solved:>11} damage={damage:>11} | fraud={fraud:3d} war={war:2d} "
            "| unemp={unemp:3d} | Σbal={sum_bal:+.6f}"
        ).format(
            tick=tick,
            actors=len(self.actors),
            neg=m["negative_actors"],
            op=m["open_problems"],
            sev=fmt_lz(-m["open_problem_severity"]),
            proj=m["active_projects"],
            solved=fmt_lz(m["cumulative_solved_value"]),
            damage=fmt_lz(-m["cumulative_damage_value"]),
            fraud=m["fraud_cases_detected"],
            war=m["war_events"],
            unemp=m["unemployment"],
            sum_bal=m["total_balance"],
        )

    def final_report(self) -> str:
        m = self.latest_metric()
        lines = []
        lines.append("Finaler Bericht")
        lines.append("===============")
        lines.append("Ticks: %d" % self.tick)
        lines.append("Gesamtbilanz Σ aller Konten: %.9f LZ (sollte nahe 0 bleiben; reine Gruppen-Transfers)" % m["total_balance"])
        lines.append("Offene Problemschwere: %s" % fmt_lz(-m["open_problem_severity"]))
        lines.append("Kumulierte Problemlösung: %s" % fmt_lz(m["cumulative_solved_value"]))
        lines.append("Kumulierter Schaden/Formalisierung: %s" % fmt_lz(-m["cumulative_damage_value"]))
        lines.append("Topologische Brücken/Adapter-Wert: %s" % fmt_lz(m["cumulative_bridge_value"]))
        lines.append("Entdeckte Betrugsfälle: %d, Betrugs-/Korrekturzahlungen: %s" % (m["fraud_cases_detected"], fmt_lz(-m["cumulative_fraud_penalty"])))
        lines.append("Hot-conflict events: %d, Kriegsschaden: %s" % (m["war_events"], fmt_lz(-m["war_damage"])))
        lines.append("Insolvenzen: %d" % m["bankruptcies"])
        lines.append("Arbeitslose Haushalte: %d von %d" % (m["unemployment"], len(self.households)))
        lines.append("")
        lines.append("Top positive Akteure")
        for actor in sorted(self.actors.values(), key=lambda a: a.balance, reverse=True)[:10]:
            lines.append("  %-32s %-12s %-10s bal=%12s rep=%7.2f" % (actor.name[:32], actor.kind, actor.location.short(), fmt_lz(actor.balance), actor.reputation))
        lines.append("")
        lines.append("Top negative Akteure")
        for actor in sorted(self.actors.values(), key=lambda a: a.balance)[:10]:
            lines.append("  %-32s %-12s %-10s bal=%12s rep=%7.2f" % (actor.name[:32], actor.kind, actor.location.short(), fmt_lz(actor.balance), actor.reputation))
        lines.append("")
        lines.append("Größte offene Probleme")
        open_problems = [self.problems[pid] for pid in self.open_problem_ids if self.problems[pid].status != "resolved"]
        for p in sorted(open_problems, key=lambda p: p.severity, reverse=True)[:12]:
            owner = self.actors[p.owner_id]
            lines.append("  P%-4d %-34s sev=%12s owner=%-20s dom=%s cause=%s" % (p.id, p.title[:34], fmt_lz(-p.severity), owner.name[:20], p.domain.compact(), p.cause))
        lines.append("")
        lines.append("Transaktionsarten")
        for kind, count in self.ledger.kind_counter.most_common(12):
            lines.append("  %-35s %7d" % (kind, count))
        lines.append("")
        lines.append("Letzte wichtige Ereignisse")
        for ev in list(self.events)[-15:]:
            tick, kind, a, value, b = ev
            lines.append("  t=%4d %-18s %-35s %12s %s" % (tick, kind, str(a)[:35], fmt_lz(value), str(b)[:28]))
        return "\n".join(lines)

    def write_csv(self, path: str) -> None:
        if not self.metrics:
            return
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=list(self.metrics[0].keys()))
            writer.writeheader()
            for row in self.metrics:
                writer.writerow(row)

    def write_json(self, path: str) -> None:
        top_positive = [a.summary() for a in sorted(self.actors.values(), key=lambda a: a.balance, reverse=True)[:25]]
        top_negative = [a.summary() for a in sorted(self.actors.values(), key=lambda a: a.balance)[:25]]
        open_problems = [p for p in self.problems.values() if p.status != "resolved"]
        open_problems.sort(key=lambda p: p.severity, reverse=True)
        data = {
            "config": self.config.__dict__,
            "final_metric": self.latest_metric(),
            "top_positive_actors": top_positive,
            "top_negative_actors": top_negative,
            "largest_open_problems": [
                {
                    "id": p.id,
                    "title": p.title,
                    "severity_lz": round(p.severity, 3),
                    "negative_value_lz": round(-p.severity, 3),
                    "owner": self.actors[p.owner_id].name,
                    "fund": self.actors[p.fund_id].name,
                    "cause": p.cause,
                    "domain": sorted(p.domain.tags),
                    "location": p.location.short(),
                    "status": p.status,
                }
                for p in open_problems[:50]
            ],
            "transaction_kinds": dict(self.ledger.kind_counter),
            "recent_events": list(self.events),
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)


def parse_args(argv: Optional[List[str]] = None) -> Config:
    parser = argparse.ArgumentParser(
        description="PyPy3-Simulation der Topologischen Gruppenwirtschaft (TGW).",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--ticks", type=int, default=250, help="Anzahl Simulationsschritte")
    parser.add_argument("--seed", type=int, default=42, help="Zufallsseed")
    parser.add_argument("--scenario", choices=["baseline", "conflict", "fraud", "intergalactic", "scarcity"], default="baseline", help="Szenario")
    parser.add_argument("--galaxies", type=int, default=3, help="Anzahl Galaxien")
    parser.add_argument("--planets-per-galaxy", type=int, default=3, help="Planeten pro Galaxie")
    parser.add_argument("--states-per-planet", type=int, default=2, help="Länder/Staaten pro Planet")
    parser.add_argument("--households", type=int, default=300, help="Haushalte/Arbeitnehmer")
    parser.add_argument("--firms", type=int, default=70, help="Unternehmen")
    parser.add_argument("--report-every", type=int, default=25, help="Konsolenbericht alle N Ticks; 0 deaktiviert")
    parser.add_argument("--initial-problems-per-state", type=int, default=5, help="Startprobleme je Staat")
    parser.add_argument("--max-projects-started-per-tick", type=int, default=18, help="Max. neue Problemlösungsprojekte pro Tick")
    parser.add_argument("--max-active-projects", type=int, default=80, help="Max. parallele Projekte")
    parser.add_argument("--intergalactic-delay", type=int, default=18, help="Basisverzögerung zwischen Galaxien")
    parser.add_argument("--remote-project-probability", type=float, default=0.08, help="Wahrscheinlichkeit, remote Solver zu suchen")
    parser.add_argument("--war-probability", type=float, default=0.004, help="Basiswahrscheinlichkeit für heißen Konflikt")
    parser.add_argument("--fraud-pressure", type=float, default=1.0, help="Betrugsdruck-Multiplikator")
    parser.add_argument("--externality-rate", type=float, default=1.0, help="Externe-Schäden-Multiplikator")
    parser.add_argument("--credit-leverage", type=float, default=4.0, help="Wie tief Banken negativ gehen dürfen")
    parser.add_argument("--csv-out", default="", help="CSV-Datei für Zeitreihe")
    parser.add_argument("--json-out", default="", help="JSON-Datei für Abschlussbericht")
    parser.add_argument("--quiet", action="store_true", help="Keine Konsolenausgabe")
    args = parser.parse_args(argv)
    return Config(
        ticks=max(0, args.ticks),
        seed=args.seed,
        scenario=args.scenario,
        galaxies=max(1, args.galaxies),
        planets_per_galaxy=max(1, args.planets_per_galaxy),
        states_per_planet=max(1, args.states_per_planet),
        households=max(1, args.households),
        firms=max(1, args.firms),
        report_every=max(0, args.report_every),
        initial_problems_per_state=max(0, args.initial_problems_per_state),
        max_projects_started_per_tick=max(1, args.max_projects_started_per_tick),
        max_active_projects=max(1, args.max_active_projects),
        intergalactic_delay=max(1, args.intergalactic_delay),
        remote_project_probability=clamp(args.remote_project_probability, 0.0, 1.0),
        war_probability=max(0.0, args.war_probability),
        fraud_pressure=max(0.1, args.fraud_pressure),
        externality_rate=max(0.0, args.externality_rate),
        credit_leverage=max(0.1, args.credit_leverage),
        csv_out=args.csv_out,
        json_out=args.json_out,
        quiet=bool(args.quiet),
    )


def main(argv: Optional[List[str]] = None) -> int:
    cfg = parse_args(argv)
    sim = Simulation(cfg)
    sim.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
