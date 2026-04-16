#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Abstrakte Markt- und Wirtschaftssimulation in EINER einzigen Python-Datei.

Ziel
----
Diese Datei soll die Kernidee einer Marktsimulation möglichst klar zeigen:

    Zustand S_t
    -> Agenten treffen Entscheidungen A_t
    -> Marktmechanismus erzeugt Trades T_t
    -> Buchhaltung / Settlement aktualisiert Bestände
    -> neuer Zustand S_{t+1}

Mathematische Kurzform:
    S_{t+1} = F(S_t, A_t, \varepsilon_t)

Was hier modelliert wird
------------------------
- ein einziges Gut
- viele Haushalte (Käufer / Konsumenten)
- einige Firmen (Produzenten / Verkäufer)
- ein zentraler Markt mit Limit-Orders
- Preisbildung durch Order-Matching + Preisanpassung aus Ungleichgewicht
- Konsum, Produktion, Dividenden, Zufallsschocks, Buchhaltung

Wichtige Vereinfachungen
------------------------
- Es gibt KEINEN expliziten Arbeitsmarkt.
- Produktion ist hier abstrakt: Firmen erzeugen Güter nach einer Produktivitätsregel.
- Kosten wirken vor allem über die Preisgrenzen der Firmen, nicht über einen vollständigen
  Input-Output-Mechanismus.
- Das Modell ist bewusst einfach gehalten, damit die Struktur sichtbar bleibt.

Starten
-------
Einfach im Terminal:
    python market_economy_simulation.py

Mit Parametern:
    python market_economy_simulation.py --ticks 300 --households 80 --firms 8 --seed 7

CSV-Ausgabe:
    python market_economy_simulation.py --csv history.csv

Presets:
    python market_economy_simulation.py --preset stable
    python market_economy_simulation.py --preset volatile

Hinweis
-------
Die Datei verwendet nur die Python-Standardbibliothek.
"""

from __future__ import annotations

import argparse
import csv
import math
import random
import statistics
from dataclasses import dataclass
from typing import Dict, Iterable, List, Optional


# ============================================================================
# Hilfsfunktionen
# ============================================================================


def clamp(value: float, lower: float, upper: float) -> float:
    """Begrenzt einen Wert auf [lower, upper]."""
    return max(lower, min(upper, value))


def positive_gauss(rng: random.Random, mean: float, std: float, floor: float = 0.0) -> float:
    """Zieht eine Normalverteilung und schneidet alles unterhalb von floor ab."""
    return max(floor, rng.gauss(mean, std))


def safe_mean(values: Iterable[float], default: float = 0.0) -> float:
    values = list(values)
    return statistics.fmean(values) if values else default


def gini(values: Iterable[float]) -> float:
    """Einfache Gini-Koeffizient-Berechnung für nichtnegative Werte."""
    data = [max(0.0, float(v)) for v in values]
    n = len(data)
    if n == 0:
        return 0.0
    total = sum(data)
    if total <= 0.0:
        return 0.0
    data.sort()
    weighted_sum = 0.0
    for idx, value in enumerate(data, start=1):
        weighted_sum += idx * value
    return (2.0 * weighted_sum) / (n * total) - (n + 1.0) / n


def sparkline(values: List[float], width: int = 64) -> str:
    """Kleine Textgrafik für Konsole."""
    if not values:
        return ""
    blocks = "▁▂▃▄▅▆▇█"
    if len(values) > width:
        step = len(values) / width
        sample = [values[int(i * step)] for i in range(width)]
    else:
        sample = values[:]
    lo = min(sample)
    hi = max(sample)
    if math.isclose(lo, hi):
        return blocks[0] * len(sample)
    chars: List[str] = []
    for v in sample:
        pos = (v - lo) / (hi - lo)
        idx = min(len(blocks) - 1, int(pos * (len(blocks) - 1)))
        chars.append(blocks[idx])
    return "".join(chars)


def fmt(value: float, digits: int = 2) -> str:
    return f"{value:,.{digits}f}"


# ============================================================================
# Konfiguration
# ============================================================================


@dataclass
class SimulationConfig:
    # Allgemein
    seed: int = 42
    ticks: int = 240
    household_count: int = 60
    firm_count: int = 6

    # Preisprozess
    initial_price: float = 10.0
    min_price: float = 0.10
    max_price: float = 1_000_000.0
    price_adjustment_speed: float = 0.35
    trade_price_weight: float = 0.60
    price_shock_std: float = 0.010

    # Makro-Schocks (langsam fortwirkende Zufallseinflüsse)
    macro_demand_shock_std: float = 0.25
    macro_supply_shock_std: float = 0.15
    shock_persistence: float = 0.85

    # Haushalte
    household_initial_cash_mean: float = 180.0
    household_initial_cash_std: float = 40.0
    household_initial_goods_mean: float = 2.5
    household_initial_goods_std: float = 1.0
    household_target_inventory_mean: float = 5.5
    household_target_inventory_std: float = 1.2
    household_consumption_mean: float = 1.6
    household_consumption_std: float = 0.4
    household_valuation_mean: float = 13.0
    household_valuation_std: float = 2.0
    household_valuation_noise_std: float = 0.9
    household_expectation_weight: float = 0.15
    household_max_buy_per_tick: int = 6

    # Firmen
    firm_initial_cash_mean: float = 650.0
    firm_initial_cash_std: float = 120.0
    firm_initial_inventory_mean: float = 24.0
    firm_initial_inventory_std: float = 6.0
    firm_productivity_mean: float = 9.0
    firm_productivity_std: float = 1.8
    firm_production_noise_std: float = 1.2
    firm_unit_cost_mean: float = 7.0
    firm_unit_cost_std: float = 0.8
    firm_markup_mean: float = 0.22
    firm_markup_std: float = 0.07
    firm_inventory_target_mean: float = 25.0
    firm_inventory_target_std: float = 5.0
    firm_sell_fraction: float = 0.60

    # Geldkreislauf
    dividend_payout_ratio: float = 0.30
    firm_cash_reserve: float = 250.0

    # Sicherheit / Debugging
    accounting_assertions: bool = True


def apply_preset(cfg: SimulationConfig, preset: str) -> SimulationConfig:
    """Verändert die Parameter in Richtung eines groben Szenarios."""
    preset = preset.lower().strip()

    if preset == "base":
        return cfg

    if preset == "stable":
        cfg.price_adjustment_speed = 0.18
        cfg.trade_price_weight = 0.45
        cfg.price_shock_std = 0.004
        cfg.macro_demand_shock_std = 0.08
        cfg.macro_supply_shock_std = 0.05
        cfg.dividend_payout_ratio = 0.25
        return cfg

    if preset == "volatile":
        cfg.price_adjustment_speed = 0.70
        cfg.trade_price_weight = 0.75
        cfg.price_shock_std = 0.035
        cfg.macro_demand_shock_std = 0.65
        cfg.macro_supply_shock_std = 0.30
        cfg.dividend_payout_ratio = 0.35
        cfg.household_valuation_noise_std = 1.6
        return cfg

    if preset == "scarcity":
        cfg.firm_productivity_mean = 6.5
        cfg.firm_initial_inventory_mean = 16.0
        cfg.macro_supply_shock_std = 0.25
        cfg.price_adjustment_speed = 0.55
        return cfg

    raise ValueError(f"Unbekanntes Preset: {preset}")


# ============================================================================
# Domänenobjekte: Orders, Trades, Agenten
# ============================================================================


@dataclass
class ShockState:
    demand_shift: float = 0.0
    supply_shift: float = 0.0


@dataclass
class Order:
    agent_id: int
    side: str  # "buy" oder "sell"
    qty: int
    limit_price: float
    budget: Optional[float] = None  # nur bei Buy-Orders relevant


@dataclass
class WorkingOrder:
    agent_id: int
    qty_remaining: int
    limit_price: float
    remaining_budget: Optional[float] = None


@dataclass
class Trade:
    buyer_id: int
    seller_id: int
    qty: int
    price: float


@dataclass
class MarketResult:
    trades: List[Trade]
    total_bid_qty: int
    total_ask_qty: int
    matched_qty: int
    unmatched_demand: int
    unmatched_supply: int
    vwap: Optional[float]


@dataclass
class Household:
    id: int
    cash: float
    goods: int
    target_inventory: float
    consumption_need: float
    base_valuation: float
    valuation_noise_std: float
    expected_price: float

    last_consumed: int = 0
    total_consumed: int = 0
    last_order_qty: int = 0
    last_limit_price: float = 0.0

    def consume(self, rng: random.Random) -> int:
        """
        Verbrauch zerstört Güter im Haushalt.
        Das ist der einfachste Weg, 'Nutzung' zu modellieren.
        """
        consumption_noise_std = max(0.15, self.consumption_need * 0.25)
        raw = max(0.0, rng.gauss(self.consumption_need, consumption_noise_std))
        qty = min(self.goods, max(0, int(round(raw))))
        self.goods -= qty
        self.last_consumed = qty
        self.total_consumed += qty
        return qty

    def update_expectation(self, market_price: float, weight: float) -> None:
        """Einfache adaptive Erwartung."""
        self.expected_price = (1.0 - weight) * self.expected_price + weight * market_price

    def valuation(self, current_price: float, demand_shift: float, rng: random.Random) -> float:
        """
        Subjektive Zahlungsbereitschaft.

        Bausteine:
        - Basisbewertung
        - Knappheit im Haushalt -> Nachfrage steigt
        - wenn der aktuelle Preis unter Erwartung liegt -> Kauf attraktiver
        - makroökonomischer Nachfrageschock
        - Zufallsrauschen
        """
        scarcity = max(0.0, self.target_inventory - self.goods)
        scarcity_bonus = 0.55 * scarcity
        cheapness_bonus = max(0.0, self.expected_price - current_price) * 0.18
        noise = rng.gauss(0.0, self.valuation_noise_std)
        val = self.base_valuation + scarcity_bonus + cheapness_bonus + demand_shift + noise
        return max(0.05, val)

    def decide_buy_order(
        self,
        current_price: float,
        demand_shift: float,
        rng: random.Random,
        max_buy_per_tick: int,
    ) -> Optional[Order]:
        """
        Einfache Kaufregel:
        - wenn Lager im Haushalt unter Zielbestand liegt, steigt Kaufdruck
        - wenn der Marktpreis 'günstig' gegenüber der Erwartung ist, wird mehr gekauft
        - wenn die subjektive Bewertung unter dem Preis liegt, wird selten oder gar nicht gekauft
        """
        self.last_order_qty = 0
        self.last_limit_price = 0.0

        valuation = self.valuation(current_price, demand_shift, rng)
        shortage = max(0.0, self.target_inventory - self.goods)
        affordable_qty = int(self.cash // max(current_price, 0.01))

        if affordable_qty <= 0:
            return None

        # Grundnachfrage aus Bestandslücke.
        desired_qty = shortage

        # Wenn Preis unter Erwartung liegt, lohnt sich Vorratsaufbau.
        if current_price < self.expected_price:
            desired_qty += 1.0

        # Wenn subjektive Bewertung höher als Preis ist, wächst die Kaufbereitschaft.
        if valuation > current_price:
            relative_surplus = (valuation - current_price) / max(current_price, 0.01)
            desired_qty += min(2.5, 2.0 * relative_surplus)

        # Ein bisschen Zufall für Heterogenität im Verhalten.
        desired_qty += rng.random() * 0.8

        qty = int(math.ceil(desired_qty))
        qty = min(qty, max_buy_per_tick, affordable_qty)

        if qty <= 0:
            return None

        # Falls Bewertung unter Marktpreis liegt, nur im Knappheitsfall minimal kaufen.
        if valuation < current_price:
            if shortage < 2.0:
                return None
            qty = min(qty, 1)

        if qty <= 0:
            return None

        self.last_order_qty = qty
        self.last_limit_price = valuation
        return Order(
            agent_id=self.id,
            side="buy",
            qty=qty,
            limit_price=valuation,
            budget=self.cash,
        )


@dataclass
class Firm:
    id: int
    cash: float
    inventory: int
    productivity: float
    production_noise_std: float
    unit_cost: float
    markup: float
    inventory_target: float

    last_produced: int = 0
    total_produced: int = 0
    last_offered: int = 0
    last_sold: int = 0
    last_limit_price: float = 0.0

    def produce(self, supply_shift: float, rng: random.Random) -> int:
        """
        Produktion ist absichtlich abstrahiert.
        Firmen erzeugen Output nach Produktivität + Schock + Lagerdruck.
        """
        # Wenn Lager schon sehr voll sind, wird gebremst.
        inventory_pressure = self.inventory / max(1.0, self.inventory_target)
        pressure_factor = 1.0
        if inventory_pressure > 2.0:
            pressure_factor = 0.55
        elif inventory_pressure > 1.5:
            pressure_factor = 0.75
        elif inventory_pressure < 0.6:
            pressure_factor = 1.20

        raw = max(0.0, rng.gauss(self.productivity, self.production_noise_std))

        # Positiver supply_shift erhöht Produktion leicht, negativer senkt sie.
        shock_factor = math.exp(0.08 * supply_shift)
        qty = max(0, int(round(raw * pressure_factor * shock_factor)))

        self.inventory += qty
        self.last_produced = qty
        self.total_produced += qty
        return qty

    def reservation_price(self, supply_shift: float) -> float:
        """
        Minimale akzeptierte Preisgrenze.
        Inventardruck drückt den Reservationspreis,
        Knappheit erhöht ihn.
        """
        inv_gap = (self.inventory - self.inventory_target) / max(1.0, self.inventory_target)
        dynamic_markup = self.markup

        if inv_gap > 0:
            dynamic_markup *= max(0.50, 1.0 - 0.25 * inv_gap)
        else:
            dynamic_markup *= 1.0 + 0.15 * min(1.5, abs(inv_gap))

        cost_factor = math.exp(-0.05 * supply_shift)
        price_floor = self.unit_cost * (1.0 + dynamic_markup) * cost_factor
        return max(0.05, price_floor)

    def decide_sell_order(self, current_price: float, supply_shift: float, rng: random.Random) -> Optional[Order]:
        """
        Firmen bieten einen Teil ihres Lagers an.
        Je stärker das Lager über Zielbestand liegt, desto aggressiver wird verkauft.
        """
        self.last_offered = 0
        self.last_sold = 0
        self.last_limit_price = 0.0

        if self.inventory <= 0:
            return None

        limit_price = self.reservation_price(supply_shift)

        base_offer = self.inventory * 0.60
        if self.inventory > self.inventory_target:
            base_offer += (self.inventory - self.inventory_target)
        elif self.inventory < 0.5 * self.inventory_target:
            base_offer *= 0.75

        # Kleine Zufallskomponente, damit nicht jede Firma gleich handelt.
        base_offer += rng.random() * 1.5

        qty = int(max(1, round(base_offer)))
        qty = min(qty, self.inventory)

        if qty <= 0:
            return None

        self.last_offered = qty
        self.last_limit_price = limit_price

        return Order(
            agent_id=self.id,
            side="sell",
            qty=qty,
            limit_price=limit_price,
            budget=None,
        )

    def adapt_after_market(self) -> None:
        """
        Primitive Lernregel:
        - viel verkauft und eher knapp -> Aufschlag erhöhen
        - wenig verkauft oder Überlager -> Aufschlag senken
        """
        offered = max(1, self.last_offered)
        sold_ratio = self.last_sold / offered
        inv_pressure = (self.inventory - self.inventory_target) / max(1.0, self.inventory_target)

        if sold_ratio > 0.90 and inv_pressure < 0.1:
            self.markup = clamp(self.markup + 0.015, 0.01, 1.50)
        elif inv_pressure > 0.80 or sold_ratio < 0.25:
            self.markup = clamp(self.markup - 0.020, 0.01, 1.50)
        elif sold_ratio > 0.60:
            self.markup = clamp(self.markup + 0.005, 0.01, 1.50)
        else:
            self.markup = clamp(self.markup - 0.005, 0.01, 1.50)


# ============================================================================
# Marktmechanismus
# ============================================================================


class Market:
    """
    Einfacher zentraler Markt mit Limit-Orders.

    Idee:
    - Buy-Orders werden nach höchstem Limitpreis sortiert.
    - Sell-Orders werden nach niedrigstem Limitpreis sortiert.
    - Solange höchste Bid >= niedrigste Ask gilt, gibt es einen Trade.
    - Ausführungspreis = Mittel aus Bid- und Ask-Limit.

    Das ist nicht der einzig mögliche Marktmechanismus, aber ein sehr klarer.
    """

    def clear(
        self,
        buy_orders: List[Order],
        sell_orders: List[Order],
        rng: random.Random,
    ) -> MarketResult:
        if not buy_orders or not sell_orders:
            total_bid_qty = sum(o.qty for o in buy_orders)
            total_ask_qty = sum(o.qty for o in sell_orders)
            return MarketResult(
                trades=[],
                total_bid_qty=total_bid_qty,
                total_ask_qty=total_ask_qty,
                matched_qty=0,
                unmatched_demand=total_bid_qty,
                unmatched_supply=total_ask_qty,
                vwap=None,
            )

        # Zufällige Tie-Breaker, damit gleichpreisige Orders nicht immer gleich behandelt werden.
        buy_orders_sorted = sorted(
            buy_orders,
            key=lambda o: (-o.limit_price, rng.random()),
        )
        sell_orders_sorted = sorted(
            sell_orders,
            key=lambda o: (o.limit_price, rng.random()),
        )

        bid_book = [
            WorkingOrder(
                agent_id=o.agent_id,
                qty_remaining=o.qty,
                limit_price=o.limit_price,
                remaining_budget=o.budget,
            )
            for o in buy_orders_sorted
        ]
        ask_book = [
            WorkingOrder(
                agent_id=o.agent_id,
                qty_remaining=o.qty,
                limit_price=o.limit_price,
                remaining_budget=None,
            )
            for o in sell_orders_sorted
        ]

        trades: List[Trade] = []
        i = 0
        j = 0

        while i < len(bid_book) and j < len(ask_book):
            bid = bid_book[i]
            ask = ask_book[j]

            # Kein weiterer Match möglich.
            if bid.limit_price + 1e-12 < ask.limit_price:
                break

            execution_price = 0.5 * (bid.limit_price + ask.limit_price)

            max_affordable = bid.qty_remaining
            if bid.remaining_budget is not None:
                max_affordable = min(max_affordable, int(bid.remaining_budget // max(execution_price, 1e-12)))

            qty = min(max_affordable, ask.qty_remaining)

            if qty <= 0:
                # Käufer kann zu diesem Preis nichts bezahlen -> nächste Buy-Order.
                i += 1
                continue

            trades.append(
                Trade(
                    buyer_id=bid.agent_id,
                    seller_id=ask.agent_id,
                    qty=qty,
                    price=execution_price,
                )
            )

            bid.qty_remaining -= qty
            ask.qty_remaining -= qty

            if bid.remaining_budget is not None:
                bid.remaining_budget -= qty * execution_price

            if bid.qty_remaining <= 0:
                i += 1
            if ask.qty_remaining <= 0:
                j += 1

        matched_qty = sum(t.qty for t in trades)
        total_bid_qty = sum(o.qty for o in buy_orders)
        total_ask_qty = sum(o.qty for o in sell_orders)
        unmatched_demand = max(0, total_bid_qty - matched_qty)
        unmatched_supply = max(0, total_ask_qty - matched_qty)

        vwap: Optional[float]
        if matched_qty > 0:
            traded_value = sum(t.qty * t.price for t in trades)
            vwap = traded_value / matched_qty
        else:
            vwap = None

        return MarketResult(
            trades=trades,
            total_bid_qty=total_bid_qty,
            total_ask_qty=total_ask_qty,
            matched_qty=matched_qty,
            unmatched_demand=unmatched_demand,
            unmatched_supply=unmatched_supply,
            vwap=vwap,
        )


# ============================================================================
# Simulation
# ============================================================================


class EconomySimulation:
    def __init__(self, config: SimulationConfig):
        self.cfg = config
        self.rng = random.Random(config.seed)
        self.market = Market()

        self.price = config.initial_price
        self.shocks = ShockState()

        self.households: Dict[int, Household] = {}
        self.firms: Dict[int, Firm] = {}
        self.history: List[Dict[str, float]] = []

        self._create_agents()
        self.initial_total_money = self.total_money()
        self.record_state(
            tick=0,
            traded_volume=0,
            trade_count=0,
            vwap=None,
            total_bid_qty=0,
            total_ask_qty=0,
            unmatched_demand=0,
            unmatched_supply=0,
            produced=0,
            consumed=0,
            dividends=0.0,
        )

    # ------------------------------------------------------------------
    # Aufbau des Systems
    # ------------------------------------------------------------------

    def _create_agents(self) -> None:
        for hid in range(self.cfg.household_count):
            household = Household(
                id=hid,
                cash=positive_gauss(
                    self.rng,
                    self.cfg.household_initial_cash_mean,
                    self.cfg.household_initial_cash_std,
                    floor=20.0,
                ),
                goods=max(
                    0,
                    int(
                        round(
                            positive_gauss(
                                self.rng,
                                self.cfg.household_initial_goods_mean,
                                self.cfg.household_initial_goods_std,
                                floor=0.0,
                            )
                        )
                    ),
                ),
                target_inventory=positive_gauss(
                    self.rng,
                    self.cfg.household_target_inventory_mean,
                    self.cfg.household_target_inventory_std,
                    floor=1.0,
                ),
                consumption_need=positive_gauss(
                    self.rng,
                    self.cfg.household_consumption_mean,
                    self.cfg.household_consumption_std,
                    floor=0.2,
                ),
                base_valuation=positive_gauss(
                    self.rng,
                    self.cfg.household_valuation_mean,
                    self.cfg.household_valuation_std,
                    floor=0.5,
                ),
                valuation_noise_std=max(0.01, self.cfg.household_valuation_noise_std),
                expected_price=self.cfg.initial_price,
            )
            self.households[hid] = household

        for fid in range(self.cfg.firm_count):
            firm = Firm(
                id=fid,
                cash=positive_gauss(
                    self.rng,
                    self.cfg.firm_initial_cash_mean,
                    self.cfg.firm_initial_cash_std,
                    floor=100.0,
                ),
                inventory=max(
                    0,
                    int(
                        round(
                            positive_gauss(
                                self.rng,
                                self.cfg.firm_initial_inventory_mean,
                                self.cfg.firm_initial_inventory_std,
                                floor=0.0,
                            )
                        )
                    ),
                ),
                productivity=positive_gauss(
                    self.rng,
                    self.cfg.firm_productivity_mean,
                    self.cfg.firm_productivity_std,
                    floor=0.5,
                ),
                production_noise_std=max(0.05, self.cfg.firm_production_noise_std),
                unit_cost=positive_gauss(
                    self.rng,
                    self.cfg.firm_unit_cost_mean,
                    self.cfg.firm_unit_cost_std,
                    floor=0.1,
                ),
                markup=positive_gauss(
                    self.rng,
                    self.cfg.firm_markup_mean,
                    self.cfg.firm_markup_std,
                    floor=0.01,
                ),
                inventory_target=positive_gauss(
                    self.rng,
                    self.cfg.firm_inventory_target_mean,
                    self.cfg.firm_inventory_target_std,
                    floor=1.0,
                ),
            )
            self.firms[fid] = firm

    # ------------------------------------------------------------------
    # Aggregation / Buchhaltung
    # ------------------------------------------------------------------

    def total_money(self) -> float:
        return sum(h.cash for h in self.households.values()) + sum(f.cash for f in self.firms.values())

    def total_goods(self) -> int:
        return sum(h.goods for h in self.households.values()) + sum(f.inventory for f in self.firms.values())

    def household_cash(self) -> float:
        return sum(h.cash for h in self.households.values())

    def firm_cash(self) -> float:
        return sum(f.cash for f in self.firms.values())

    def household_goods(self) -> int:
        return sum(h.goods for h in self.households.values())

    def firm_inventory(self) -> int:
        return sum(f.inventory for f in self.firms.values())

    def pay_dividends(self) -> float:
        """
        Damit Geld wieder zu Haushalten zurückfließt,
        zahlen Firmen einen Anteil ihres Kassenüberschusses aus.
        """
        if not self.households:
            return 0.0

        total_paid = 0.0
        household_count = len(self.households)

        for firm in self.firms.values():
            distributable = max(0.0, firm.cash - self.cfg.firm_cash_reserve)
            payout = distributable * self.cfg.dividend_payout_ratio
            if payout <= 0.0:
                continue
            firm.cash -= payout
            per_household = payout / household_count
            for household in self.households.values():
                household.cash += per_household
            total_paid += payout

        return total_paid

    def update_shocks(self) -> None:
        p = self.cfg.shock_persistence
        self.shocks.demand_shift = p * self.shocks.demand_shift + self.rng.gauss(0.0, self.cfg.macro_demand_shock_std)
        self.shocks.supply_shift = p * self.shocks.supply_shift + self.rng.gauss(0.0, self.cfg.macro_supply_shock_std)

    def settle(self, trades: List[Trade]) -> List[Trade]:
        """
        Führt Trades wirklich aus.

        Marktmechanismus und Settlement werden getrennt gehalten.
        Genau hier werden Cash und Güter umgebucht.
        """
        executed: List[Trade] = []

        for trade in trades:
            buyer = self.households[trade.buyer_id]
            seller = self.firms[trade.seller_id]

            affordable_qty = int(buyer.cash // max(trade.price, 1e-12))
            feasible_qty = min(trade.qty, affordable_qty, seller.inventory)

            if feasible_qty <= 0:
                continue

            value = feasible_qty * trade.price

            buyer.cash -= value
            buyer.goods += feasible_qty

            seller.cash += value
            seller.inventory -= feasible_qty
            seller.last_sold += feasible_qty

            executed.append(
                Trade(
                    buyer_id=trade.buyer_id,
                    seller_id=trade.seller_id,
                    qty=feasible_qty,
                    price=trade.price,
                )
            )

        return executed

    # ------------------------------------------------------------------
    # Preisupdate
    # ------------------------------------------------------------------

    def update_reference_price(self, vwap: Optional[float], total_bid_qty: int, total_ask_qty: int) -> None:
        """
        Neuer Referenzpreis für den nächsten Tick.

        Komponenten:
        - Orientierung am tatsächlich gehandelten Preis (VWAP)
        - Überschussnachfrage / Überschussangebot
        - kleiner externer Preisschock
        """
        price = self.price

        if vwap is not None:
            price = (1.0 - self.cfg.trade_price_weight) * price + self.cfg.trade_price_weight * vwap

        imbalance_denominator = max(1, total_bid_qty + total_ask_qty)
        imbalance = (total_bid_qty - total_ask_qty) / imbalance_denominator

        price *= math.exp(self.cfg.price_adjustment_speed * imbalance + self.rng.gauss(0.0, self.cfg.price_shock_std))
        self.price = clamp(price, self.cfg.min_price, self.cfg.max_price)

    # ------------------------------------------------------------------
    # Ein einzelner Tick
    # ------------------------------------------------------------------

    def step(self, tick: int) -> None:
        self.update_shocks()

        # 1) Konsum im Haushalt
        consumed = sum(h.consume(self.rng) for h in self.households.values())

        # 2) Produktion in Firmen
        produced = sum(f.produce(self.shocks.supply_shift, self.rng) for f in self.firms.values())

        # 3) Geldkreislauf: Dividenden
        dividends = self.pay_dividends()

        # 4) Erwartungen aktualisieren
        for household in self.households.values():
            household.update_expectation(self.price, self.cfg.household_expectation_weight)

        # 5) Orders erzeugen
        buy_orders: List[Order] = []
        sell_orders: List[Order] = []

        for household in self.households.values():
            order = household.decide_buy_order(
                current_price=self.price,
                demand_shift=self.shocks.demand_shift,
                rng=self.rng,
                max_buy_per_tick=self.cfg.household_max_buy_per_tick,
            )
            if order is not None:
                buy_orders.append(order)

        for firm in self.firms.values():
            order = firm.decide_sell_order(
                current_price=self.price,
                supply_shift=self.shocks.supply_shift,
                rng=self.rng,
            )
            if order is not None:
                sell_orders.append(order)

        # 6) Markt-Clearing
        market_result = self.market.clear(buy_orders=buy_orders, sell_orders=sell_orders, rng=self.rng)

        # 7) Settlement / Buchung
        executed_trades = self.settle(market_result.trades)
        traded_volume = sum(t.qty for t in executed_trades)
        traded_value = sum(t.qty * t.price for t in executed_trades)
        actual_vwap = (traded_value / traded_volume) if traded_volume > 0 else None

        # 8) Firmen passen Verhalten leicht an
        for firm in self.firms.values():
            firm.adapt_after_market()

        # 9) Neuer Referenzpreis für nächsten Tick
        self.update_reference_price(
            vwap=actual_vwap if actual_vwap is not None else market_result.vwap,
            total_bid_qty=market_result.total_bid_qty,
            total_ask_qty=market_result.total_ask_qty,
        )

        # 10) Zustand speichern
        self.record_state(
            tick=tick,
            traded_volume=traded_volume,
            trade_count=len(executed_trades),
            vwap=actual_vwap,
            total_bid_qty=market_result.total_bid_qty,
            total_ask_qty=market_result.total_ask_qty,
            unmatched_demand=max(0, market_result.total_bid_qty - traded_volume),
            unmatched_supply=max(0, market_result.total_ask_qty - traded_volume),
            produced=produced,
            consumed=consumed,
            dividends=dividends,
        )

        # 11) Invarianten prüfen
        if self.cfg.accounting_assertions:
            self.assert_invariants()

    def assert_invariants(self) -> None:
        total_money = self.total_money()
        if not math.isclose(total_money, self.initial_total_money, rel_tol=1e-9, abs_tol=1e-6):
            raise AssertionError(
                f"Geldbestand nicht invariant: initial={self.initial_total_money}, jetzt={total_money}"
            )

        for household in self.households.values():
            if household.cash < -1e-9:
                raise AssertionError(f"Negativer Kassenbestand im Haushalt {household.id}: {household.cash}")
            if household.goods < 0:
                raise AssertionError(f"Negativer Güterbestand im Haushalt {household.id}: {household.goods}")

        for firm in self.firms.values():
            if firm.cash < -1e-9:
                raise AssertionError(f"Negativer Kassenbestand in Firma {firm.id}: {firm.cash}")
            if firm.inventory < 0:
                raise AssertionError(f"Negativer Lagerbestand in Firma {firm.id}: {firm.inventory}")

        if self.price <= 0.0:
            raise AssertionError(f"Preis muss positiv bleiben, ist aber {self.price}")

    # ------------------------------------------------------------------
    # Logging / History
    # ------------------------------------------------------------------

    def record_state(
        self,
        tick: int,
        traded_volume: int,
        trade_count: int,
        vwap: Optional[float],
        total_bid_qty: int,
        total_ask_qty: int,
        unmatched_demand: int,
        unmatched_supply: int,
        produced: int,
        consumed: int,
        dividends: float,
    ) -> None:
        row = {
            "tick": float(tick),
            "price": self.price,
            "vwap": float("nan") if vwap is None else vwap,
            "trade_volume": float(traded_volume),
            "trade_count": float(trade_count),
            "bid_qty": float(total_bid_qty),
            "ask_qty": float(total_ask_qty),
            "unmatched_demand": float(unmatched_demand),
            "unmatched_supply": float(unmatched_supply),
            "produced": float(produced),
            "consumed": float(consumed),
            "dividends": dividends,
            "demand_shift": self.shocks.demand_shift,
            "supply_shift": self.shocks.supply_shift,
            "household_cash": self.household_cash(),
            "firm_cash": self.firm_cash(),
            "household_goods": float(self.household_goods()),
            "firm_inventory": float(self.firm_inventory()),
            "total_money": self.total_money(),
            "total_goods": float(self.total_goods()),
            "mean_household_cash": safe_mean(h.cash for h in self.households.values()),
            "mean_household_goods": safe_mean(h.goods for h in self.households.values()),
            "mean_firm_inventory": safe_mean(f.inventory for f in self.firms.values()),
            "mean_firm_markup": safe_mean(f.markup for f in self.firms.values()),
            "cash_gini_households": gini(h.cash for h in self.households.values()),
        }
        self.history.append(row)

    def write_csv(self, path: str) -> None:
        if not self.history:
            return
        fieldnames = list(self.history[0].keys())
        with open(path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            for row in self.history:
                writer.writerow(row)

    # ------------------------------------------------------------------
    # Lauf
    # ------------------------------------------------------------------

    def run(self) -> List[Dict[str, float]]:
        for tick in range(1, self.cfg.ticks + 1):
            self.step(tick)
        return self.history

    # ------------------------------------------------------------------
    # Bericht / Ausgabe
    # ------------------------------------------------------------------

    def summary(self, last_n: int = 12) -> str:
        if not self.history:
            return "Keine History vorhanden."

        rows = self.history
        dynamic_rows = rows[1:] if len(rows) > 1 else rows

        prices = [row["price"] for row in rows]
        volumes = [row["trade_volume"] for row in dynamic_rows]
        produced = [row["produced"] for row in dynamic_rows]
        consumed = [row["consumed"] for row in dynamic_rows]
        trade_counts = [row["trade_count"] for row in dynamic_rows]

        start_price = prices[0]
        end_price = prices[-1]
        min_price = min(prices)
        max_price = max(prices)
        avg_price = safe_mean(prices)
        total_volume = sum(volumes)
        total_trades = sum(trade_counts)
        avg_volume = safe_mean(volumes)
        avg_production = safe_mean(produced)
        avg_consumption = safe_mean(consumed)
        final = rows[-1]

        lines: List[str] = []
        lines.append("=" * 90)
        lines.append("ABSTRAKTE MARKT- / WIRTSCHAFTSSIMULATION")
        lines.append("=" * 90)
        lines.append(
            f"Ticks={self.cfg.ticks} | Seed={self.cfg.seed} | Haushalte={self.cfg.household_count} | Firmen={self.cfg.firm_count}"
        )
        lines.append(
            f"Preis: Start={fmt(start_price)} | Ende={fmt(end_price)} | Min={fmt(min_price)} | Max={fmt(max_price)} | Mittel={fmt(avg_price)}"
        )
        lines.append(
            f"Volumen gesamt={fmt(total_volume, 0)} | Trades gesamt={fmt(total_trades, 0)} | Volumen/Tick={fmt(avg_volume)}"
        )
        lines.append(
            f"Produktion/Tick={fmt(avg_production)} | Konsum/Tick={fmt(avg_consumption)} | Geld invariant={fmt(final['total_money'])}"
        )
        lines.append(
            f"Haushalts-Cash={fmt(final['household_cash'])} | Firmen-Cash={fmt(final['firm_cash'])} | Haushalts-Güter={fmt(final['household_goods'], 0)} | Firmenlager={fmt(final['firm_inventory'], 0)}"
        )
        lines.append(
            f"Durchschnitts-Markup Firmen={fmt(final['mean_firm_markup'], 3)} | Cash-Gini Haushalte={fmt(final['cash_gini_households'], 3)}"
        )
        lines.append(f"Preisverlauf: {sparkline(prices)}")
        lines.append("-" * 90)
        lines.append(
            f"{'tick':>6} {'price':>12} {'vwap':>12} {'vol':>8} {'bid':>8} {'ask':>8} {'prod':>8} {'cons':>8} {'hh_cash':>12} {'firm_inv':>10}"
        )
        lines.append("-" * 90)

        for row in rows[-last_n:]:
            vwap_str = "-" if math.isnan(row["vwap"]) else fmt(row["vwap"])
            lines.append(
                f"{int(row['tick']):>6} "
                f"{fmt(row['price']):>12} "
                f"{vwap_str:>12} "
                f"{int(row['trade_volume']):>8} "
                f"{int(row['bid_qty']):>8} "
                f"{int(row['ask_qty']):>8} "
                f"{int(row['produced']):>8} "
                f"{int(row['consumed']):>8} "
                f"{fmt(row['household_cash']):>12} "
                f"{int(row['firm_inventory']):>10}"
            )

        lines.append("-" * 90)
        lines.append("Interpretation in einem Satz:")
        lines.append(
            "Jeder Tick macht genau dies: Konsum + Produktion + Orders + Matching + Buchhaltung + Preisupdate."
        )
        lines.append("=" * 90)
        return "\n".join(lines)


# ============================================================================
# CLI
# ============================================================================


def build_arg_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Abstrakte Markt- und Wirtschaftssimulation in einer einzigen Python-Datei."
    )
    parser.add_argument("--ticks", type=int, default=240, help="Anzahl der Zeitschritte")
    parser.add_argument("--households", type=int, default=60, help="Anzahl der Haushalte")
    parser.add_argument("--firms", type=int, default=6, help="Anzahl der Firmen")
    parser.add_argument("--seed", type=int, default=42, help="Zufalls-Seed für reproduzierbare Läufe")
    parser.add_argument("--price", type=float, default=10.0, help="Startpreis")
    parser.add_argument(
        "--preset",
        type=str,
        default="base",
        choices=["base", "stable", "volatile", "scarcity"],
        help="Grobe Parametervarianten",
    )
    parser.add_argument("--csv", type=str, default="", help="Optionaler Pfad für CSV-History")
    parser.add_argument("--last", type=int, default=12, help="Wie viele letzte Zeilen im Bericht erscheinen")
    parser.add_argument(
        "--no-assertions",
        action="store_true",
        help="Deaktiviert Buchhaltungs- und Konsistenzprüfungen",
    )
    return parser


def config_from_args(args: argparse.Namespace) -> SimulationConfig:
    cfg = SimulationConfig(
        seed=args.seed,
        ticks=args.ticks,
        household_count=args.households,
        firm_count=args.firms,
        initial_price=args.price,
        accounting_assertions=not args.no_assertions,
    )
    cfg = apply_preset(cfg, args.preset)
    return cfg


def main() -> None:
    parser = build_arg_parser()
    args = parser.parse_args()

    cfg = config_from_args(args)
    sim = EconomySimulation(cfg)
    sim.run()

    if args.csv:
        sim.write_csv(args.csv)

    print(sim.summary(last_n=args.last))


if __name__ == "__main__":
    main()
