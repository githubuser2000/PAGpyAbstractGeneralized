# -*- coding: utf-8 -*-
"""Arbeits-, Güter- und Q-Märkte."""

from __future__ import print_function

import math
from collections import defaultdict

from .sectors import LABOR_TYPES, GOODS, HOUSEHOLD_CONSUMPTION_WEIGHTS, ESSENTIAL_GOODS
from .money import Q_VALUES, vector_value
from .utils import clamp, safe_div, EPS


class LaborMarket(object):
    def __init__(self):
        self.matches = 0
        self.unfilled_jobs = 0
        self.unemployment_rate = 0.0
        self.avg_wage = 0.0
        self.wage_by_labor = defaultdict(float)
        self.count_by_labor = defaultdict(int)

    def match(self, rng, households, firms, unemployment_rate=0.08, q_shortages=None):
        self.matches = 0
        self.unfilled_jobs = 0
        self.avg_wage = 0.0
        self.wage_by_labor = defaultdict(float)
        self.count_by_labor = defaultdict(int)
        q_shortages = q_shortages or {}
        for h in households:
            h.start_period()
        for f in firms:
            f.reset_period()
            f.plan_vacancies(rng)
        jobs = []
        for firm in firms:
            if firm.bankrupt:
                continue
            for labor_type, n in firm.vacancies.items():
                # Knappheit passender Qs erhöht Löhne in strukturellen Jobs.
                q_short = 0.0
                for q in LABOR_TYPES[labor_type].q_wage_distribution:
                    q_short = max(q_short, q_shortages.get(q, 0.0))
                wage = firm.wage_offer(labor_type, unemployment_rate=unemployment_rate, q_shortage=q_short)
                for _ in range(int(n)):
                    jobs.append((firm, labor_type, wage))
        rng.shuffle(jobs)
        # Höhere Löhne zuerst, damit qualifizierte Arbeit nicht völlig zufällig verteilt wird.
        jobs.sort(key=lambda j: j[2], reverse=True)
        available = set(h.id for h in households if h.health > 0.10)
        households_by_id = dict((h.id, h) for h in households)
        total_wage = 0.0
        for firm, labor_type, wage in jobs:
            if not available:
                self.unfilled_jobs += 1
                continue
            # Kandidatenstichprobe hält Laufzeit niedrig bei großen Populationen.
            sample_size = min(24, len(available))
            ids = list(available)
            if len(ids) > sample_size:
                ids = rng.sample(ids, sample_size)
            best_h = None
            best_score = -1.0
            for hid in ids:
                h = households_by_id[hid]
                score = h.choose_labor_offer_score(labor_type, wage) * rng.uniform(0.90, 1.10)
                if score > best_score:
                    best_score = score
                    best_h = h
            # Unterqualifizierte Matching-Versuche dürfen scheitern.
            if best_h is None or best_score < 0.05:
                self.unfilled_jobs += 1
                continue
            firm.hire(best_h, labor_type, wage)
            available.discard(best_h.id)
            self.matches += 1
            total_wage += wage
            self.wage_by_labor[labor_type] += wage
            self.count_by_labor[labor_type] += 1
        for h in households:
            if h.current_employer is None:
                h.mark_unemployed()
        self.unemployment_rate = safe_div(sum(1 for h in households if h.current_employer is None), len(households), 0.0)
        self.avg_wage = safe_div(total_wage, self.matches, 0.0)
        return self


class GoodsMarket(object):
    def __init__(self):
        self.sales_value = 0.0
        self.sales_qty_by_good = defaultdict(float)
        self.unmet_qty_by_good = defaultdict(float)
        self.value_by_good = defaultdict(float)
        self.transactions = 0
        self.price_index = 1.0
        self.last_price_index = 1.0
        self.avg_prices = dict((g, GOODS[g].base_price) for g in GOODS)

    def reset_period(self):
        self.sales_value = 0.0
        self.sales_qty_by_good = defaultdict(float)
        self.unmet_qty_by_good = defaultdict(float)
        self.value_by_good = defaultdict(float)
        self.transactions = 0

    def sellers_for_good(self, firms, good):
        sellers = [f for f in firms if (not f.bankrupt) and f.output_good == good and f.inventory.get(good, 0.0) > EPS]
        sellers.sort(key=lambda f: f.price)
        return sellers

    def buy_good(self, buyer, good, qty, firms, government=None, allow_debt=False, max_budget=None):
        qty = max(0.0, float(qty))
        if qty <= EPS:
            return 0.0, 0.0
        if max_budget is None:
            max_budget = buyer.wallet.positive_value() if not allow_debt else max(0.0, buyer.wallet.positive_value()) + 1e9
        remaining_qty = qty
        remaining_budget = max(0.0, max_budget)
        bought_qty = 0.0
        spent = 0.0
        sellers = self.sellers_for_good(firms, good)
        for seller in sellers:
            if remaining_qty <= EPS or remaining_budget <= EPS:
                break
            price = max(0.01, seller.price)
            available = seller.inventory.get(good, 0.0)
            affordable_qty = remaining_budget / price
            take = min(available, remaining_qty, affordable_qty)
            if take <= EPS:
                continue
            value = take * price
            # Zahlung. Güterkauf erzeugt bei allow_debt=False keine neuen Schulden.
            paid = buyer.wallet.pay_value_to(seller.wallet, value, debt_q=1, allow_debt=allow_debt)
            if paid + EPS < value and not allow_debt:
                # Falls durch Rundungen nicht genug bezahlt wurde, Take rückskalieren.
                take = paid / price
                value = paid
            if value <= EPS or take <= EPS:
                continue
            seller.remove_good(good, take)
            buyer.add_good(good, take)
            buyer.spend_value(value)
            seller.receive_sale(take, value)
            self.sales_value += value
            self.sales_qty_by_good[good] += take
            self.value_by_good[good] += value
            self.transactions += 1
            spent += value
            bought_qty += take
            remaining_qty -= take
            remaining_budget -= value
            # Umsatzsteuer wird beim Verkäufer abgeschöpft.
            if government is not None and government.vat_rate > 0:
                government.collect_tax_value(seller, value * government.vat_rate, debt_q=10)
        if remaining_qty > EPS:
            self.unmet_qty_by_good[good] += remaining_qty
        return bought_qty, spent

    def household_consumption_plan(self, household, prices):
        budget = household.consumption_budget()
        plan = {}
        if budget <= EPS:
            return plan, 0.0
        # Feste Bedarfsanker in physischen Einheiten.
        # Alter/Gesundheit verändern Gesundheitsbedarf, Bildung die Bildungsnachfrage.
        anchors = {
            "food": 0.24,
            "energy": 0.14,
            "housing": 0.055,
            "transport_service": 0.08,
            "health_service": 0.035 + (1.0 - household.health) * 0.09 + (0.025 if household.age > 58 else 0.0),
            "education_service": max(0.012, (1.0 - household.education) * 0.055),
            "public_service": 0.035,
            "security_service": 0.025,
        }
        essential_value = 0.0
        for g, qty in anchors.items():
            essential_value += qty * prices.get(g, GOODS[g].base_price)
        # Wenn Budget nicht reicht, proportional kürzen, aber Nahrung stärker schützen.
        scale = min(1.0, budget * 0.72 / max(EPS, essential_value))
        for g, qty in anchors.items():
            weight = 1.0
            if g == "food":
                weight = 1.25
            elif g in ("culture_service", "hospitality_service"):
                weight = 0.7
            plan[g] = qty * scale * weight
        remaining_budget = max(0.0, budget - sum(plan[g] * prices.get(g, GOODS[g].base_price) for g in plan))
        # Diskretionäre Nachfrage nach Gewicht.
        weights = {}
        for g, w in HOUSEHOLD_CONSUMPTION_WEIGHTS.items():
            if g in plan:
                continue
            # Schulden/Arbeitslosigkeit drücken Luxus.
            lux_penalty = 1.0
            if GOODS[g].essential < 0.40 and household.unemployed_periods > 0:
                lux_penalty = 0.55
            weights[g] = w * lux_penalty
        weights = dict((g, w) for g, w in weights.items() if w > 0)
        total_w = sum(weights.values())
        if total_w > EPS and remaining_budget > EPS:
            for g, w in weights.items():
                value = remaining_budget * w / total_w
                plan[g] = plan.get(g, 0.0) + value / max(0.01, prices.get(g, GOODS[g].base_price))
        return plan, budget

    def consume_households(self, rng, households, firms, government=None):
        prices = self.current_prices(firms)
        for h in households:
            plan, budget = self.household_consumption_plan(h, prices)
            # Essentielles zuerst.
            ordered = sorted(plan.items(), key=lambda item: (-GOODS[item[0]].essential, item[0]))
            spent_total = 0.0
            bought = {}
            for g, qty in ordered:
                remaining_budget = max(0.0, budget - spent_total)
                if remaining_budget <= EPS:
                    break
                allow_debt = False
                bought_qty, spent = self.buy_good(h, g, qty, firms, government=government, allow_debt=allow_debt, max_budget=remaining_budget)
                if bought_qty > EPS:
                    bought[g] = bought.get(g, 0.0) + bought_qty
                spent_total += spent
            h.consume_effects(bought, prices)

    def firms_buy_inputs(self, rng, firms, banks=None, credit_system=None, government=None):
        banks = banks or []
        for firm in firms:
            if firm.bankrupt:
                continue
            need = firm.buy_input_need()
            if not need:
                continue
            est_cost = sum(qty * self.avg_prices.get(g, GOODS[g].base_price) for g, qty in need.items())
            if firm.wallet.positive_value() < est_cost * 0.65 and banks and credit_system is not None:
                bank = max(banks, key=lambda b: b.risk_score(firm) + rng.random() * 0.05)
                credit_system.grant_loan(bank, firm, est_cost * 0.75, purpose="input_purchase", term=8)
            budget = min(firm.wallet.positive_value() * 0.55, est_cost * 1.10 + 1.0)
            spent_total = 0.0
            for g, qty in need.items():
                if budget - spent_total <= EPS:
                    break
                bought, spent = self.buy_good(firm, g, qty, firms, government=government, allow_debt=False, max_budget=budget - spent_total)
                firm.last_input_cost += spent
                spent_total += spent

    def government_purchases(self, rng, government, firms, metrics=None):
        metrics = metrics or {}
        # Staat kauft strategisch öffentliche Güter und Krisenmünz-nahe Leistungen.
        base_budget = min(90.0, max(8.0, government.wallet.positive_value() * government.public_investment_rate))
        q18_debt = metrics.get("q18_debt_value", 0.0)
        q16_debt = metrics.get("q16_debt_value", 0.0)
        unemployment = metrics.get("unemployment_rate", 0.0)
        orders = {
            "public_service": 0.25,
            "education_service": 0.14,
            "health_service": 0.14,
            "environment_service": 0.10,
            "security_service": 0.08,
            "housing": 0.08,
            "maintenance_service": 0.08,
            "automation_service": 0.06,
            "knowledge": 0.07,
        }
        if q18_debt > 60:
            orders["housing"] += 0.05
            orders["maintenance_service"] += 0.05
            orders["knowledge"] += 0.03
        if q16_debt > 60:
            orders["maintenance_service"] += 0.06
            orders["public_service"] += 0.04
        if unemployment > 0.18:
            base_budget *= 1.25
            orders["education_service"] += 0.06
            orders["public_service"] += 0.04
        total_w = sum(orders.values())
        prices = self.current_prices(firms)
        spent_total = 0.0
        for g, w in sorted(orders.items(), key=lambda x: -x[1]):
            budget = base_budget * w / total_w
            qty = budget / max(0.01, prices.get(g, GOODS[g].base_price))
            bought, spent = self.buy_good(government, g, qty, firms, government=None, allow_debt=True, max_budget=budget)
            government.public_spending += spent
            spent_total += spent
        return spent_total

    def current_prices(self, firms):
        prices = dict((g, GOODS[g].base_price) for g in GOODS)
        by_good = defaultdict(list)
        for f in firms:
            if f.bankrupt:
                continue
            by_good[f.output_good].append(f.price)
        for g, arr in by_good.items():
            if arr:
                prices[g] = sum(arr) / float(len(arr))
        return prices

    def update_price_index(self, firms):
        self.last_price_index = self.price_index
        prices = self.current_prices(firms)
        self.avg_prices = prices
        weighted = 0.0
        base = 0.0
        for g, good in GOODS.items():
            weight = good.household_weight + 0.25 * good.essential
            weighted += prices[g] * weight
            base += good.base_price * weight
        self.price_index = safe_div(weighted, base, 1.0)
        return self.price_index


class CoinMarket(object):
    """Einfacher Q-Markt: beobachtet Knappheit und erlaubt semantische Schuldreparatur."""

    def __init__(self):
        self.coin_prices = dict((q, Q_VALUES[q]) for q in range(1, 21))
        self.shortage = dict((q, 0.0) for q in range(1, 21))
        self.repaired_value = 0.0

    def update(self, agents):
        self.repaired_value = 0.0
        for q in range(1, 21):
            pos = 0.0
            debt = 0.0
            for a in agents:
                qty = a.wallet.balances.get(q, 0.0)
                if qty > EPS:
                    pos += qty * Q_VALUES[q]
                elif qty < -EPS:
                    debt += -qty * Q_VALUES[q]
            ratio = safe_div(debt, pos + 1.0, 0.0)
            self.shortage[q] = clamp(ratio, 0.0, 4.0)
            # Marktpreis: Nominalwert plus Knappheitspremie.
            self.coin_prices[q] = Q_VALUES[q] * clamp(1.0 + 0.38 * ratio, 0.75, 3.0)
        return self.shortage

    def repair_agent_debts(self, agent, max_fraction=0.10):
        budget = agent.wallet.positive_value() * max_fraction
        if budget <= EPS:
            return 0.0
        # Kritische hohe Schulden zuerst.
        debts = []
        for q, qty in agent.wallet.debt_vector().items():
            debts.append((q, qty * Q_VALUES[q]))
        debts.sort(key=lambda x: (-Q_VALUES[x[0]], -x[1]))
        repaired = 0.0
        for q, dv in debts:
            if budget <= EPS:
                break
            used = agent.wallet.repay_own_debt(q, max_value=min(budget, dv))
            repaired += used
            budget -= used
        self.repaired_value += repaired
        return repaired

    def repair_all(self, agents, max_fraction=0.06):
        total = 0.0
        for a in agents:
            total += self.repair_agent_debts(a, max_fraction=max_fraction)
        return total
