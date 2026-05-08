# -*- coding: utf-8 -*-
"""Agenten der Q-Ökonomie: Haushalte, Firmen, Banken, Staat."""

from __future__ import print_function

import math
from collections import defaultdict
from dataclasses import dataclass, field

from .money import Wallet, Q_VALUES, vector_from_value, vector_value
from .sectors import LABOR_TYPES, GOODS, SECTOR_RECIPES, HOUSEHOLD_CONSUMPTION_WEIGHTS
from .utils import clamp, safe_div, weighted_choice, normalize_weights, EPS


class EconomicAgent(object):
    def __init__(self, agent_id, name, kind, wallet=None):
        self.id = agent_id
        self.name = name
        self.kind = kind
        self.wallet = wallet if wallet is not None else Wallet()
        self.inventory = defaultdict(float)
        self.reputation = defaultdict(lambda: 0.55)
        self.income_zw = 0.0
        self.expense_zw = 0.0
        self.last_income_zw = 0.0
        self.last_expense_zw = 0.0
        self.failed_payments = 0
        self.bankrupt = False

    def reset_period_accounts(self):
        self.last_income_zw = self.income_zw
        self.last_expense_zw = self.expense_zw
        self.income_zw = 0.0
        self.expense_zw = 0.0

    def net_worth(self):
        inv = 0.0
        for g, qty in self.inventory.items():
            if g in GOODS:
                inv += qty * GOODS[g].base_price
        return self.wallet.total_value() + inv

    def positive_liquidity(self):
        return self.wallet.positive_value()

    def debt_value(self):
        return self.wallet.debt_value()

    def receive_value(self, amount):
        self.income_zw += max(0.0, amount)

    def spend_value(self, amount):
        self.expense_zw += max(0.0, amount)

    def add_good(self, good, qty):
        if qty <= EPS:
            return
        self.inventory[good] += qty

    def remove_good(self, good, qty):
        have = self.inventory.get(good, 0.0)
        take = min(have, max(0.0, qty))
        self.inventory[good] = have - take
        if self.inventory[good] < EPS:
            self.inventory[good] = 0.0
        return take


class Household(EconomicAgent):
    def __init__(self, agent_id, rng, archetype="mixed"):
        EconomicAgent.__init__(self, agent_id, "Haushalt %s" % agent_id, "household")
        self.age = rng.randint(18, 68)
        self.health = clamp(rng.gauss(0.78, 0.12), 0.20, 1.00)
        self.education = clamp(rng.gauss(0.52, 0.20), 0.05, 1.00)
        self.happiness = clamp(rng.gauss(0.62, 0.16), 0.05, 1.00)
        self.risk_preference = clamp(rng.random(), 0.05, 0.95)
        self.consumption_propensity = clamp(rng.gauss(0.46, 0.11), 0.25, 0.78)
        self.primary_labor = None
        self.secondary_labor = None
        self.skills = {}
        self.last_employer = None
        self.current_employer = None
        self.current_labor_type = None
        self.current_wage = 0.0
        self.unemployed_periods = 0
        self.hours_supplied = 1.0
        self.need_satisfaction = defaultdict(lambda: 0.5)
        self.total_consumption_value = 0.0
        self.total_wage_income = 0.0
        self.public_benefit_received = 0.0
        self._init_skills(rng, archetype)
        self._init_wallet(rng)

    def _init_wallet(self, rng):
        # Haushalte starten mit Grundmünzen und etwas Operationsgeld.
        self.wallet.add_coin(1, rng.uniform(2.0, 8.0))
        self.wallet.add_coin(2, rng.uniform(1.0, 5.0))
        self.wallet.add_coin(3, rng.uniform(0.5, 3.0))
        self.wallet.add_coin(5, rng.uniform(0.2, 2.5))
        if rng.random() < self.education:
            self.wallet.add_coin(12, rng.uniform(0.1, 1.0))

    def _init_skills(self, rng, archetype):
        labor_keys = list(LABOR_TYPES.keys())
        # Archetypen sorgen dafür, dass nicht alle in Software landen.
        pools = {
            "manual": ["manual_basic", "agriculture", "mining", "construction", "craft", "hospitality", "retail"],
            "industrial": ["industrial", "energy", "maintenance", "logistics", "construction", "craft"],
            "care": ["care", "health", "teaching", "public_service", "hospitality"],
            "knowledge": ["software", "research", "engineering", "teaching", "finance", "legal"],
            "service": ["retail", "hospitality", "logistics", "finance", "public_service", "security"],
            "mixed": labor_keys,
        }
        pool = pools.get(archetype, labor_keys)
        self.primary_labor = rng.choice(pool)
        second_pool = [x for x in labor_keys if x != self.primary_labor]
        self.secondary_labor = rng.choice(second_pool)
        for key in labor_keys:
            base = rng.uniform(0.03, 0.20)
            if key == self.primary_labor:
                base = rng.uniform(0.45, 0.92)
            elif key == self.secondary_labor:
                base = rng.uniform(0.20, 0.62)
            # Bildung hebt Wissensarbeit, Gesundheit hebt körperliche Arbeit.
            if key in ("software", "research", "engineering", "teaching", "finance", "legal", "management"):
                base += 0.20 * self.education
            if key in ("manual_basic", "agriculture", "mining", "construction", "industrial", "logistics"):
                base += 0.12 * self.health
            self.skills[key] = clamp(base, 0.01, 1.0)

    def employability(self, labor_type):
        skill = self.skills.get(labor_type, 0.0)
        age_factor = 1.0
        if self.age > 60:
            age_factor -= min(0.35, (self.age - 60) * 0.035)
        return clamp(skill * (0.55 + 0.45 * self.health) * age_factor, 0.0, 1.2)

    def choose_labor_offer_score(self, labor_type, wage_zw):
        skill = self.employability(labor_type)
        if skill <= EPS:
            return 0.0
        preference = 1.0
        if labor_type == self.primary_labor:
            preference += 0.25
        if labor_type == self.secondary_labor:
            preference += 0.10
        return skill * wage_zw * preference

    def start_period(self):
        self.current_employer = None
        self.current_labor_type = None
        self.current_wage = 0.0
        self.hours_supplied = 1.0

    def receive_wage(self, wage_zw, labor_type):
        self.total_wage_income += wage_zw
        self.receive_value(wage_zw)
        self.current_wage = wage_zw
        self.current_labor_type = labor_type
        self.unemployed_periods = 0
        # Lernen durch Arbeit.
        if labor_type in self.skills:
            gain = 0.006 + 0.006 * self.education
            self.skills[labor_type] = clamp(self.skills[labor_type] + gain * (1.0 - self.skills[labor_type]), 0.0, 1.0)
        self.happiness = clamp(self.happiness + 0.012, 0.0, 1.0)

    def mark_unemployed(self):
        self.unemployed_periods += 1
        self.happiness = clamp(self.happiness - 0.018 - 0.002 * self.unemployed_periods, 0.0, 1.0)
        # Langzeitarbeitslosigkeit lässt Skills leicht rosten.
        if self.unemployed_periods > 4:
            for k in self.skills:
                self.skills[k] *= 0.997

    def consume_effects(self, bought, prices):
        """Aktualisiert Gesundheit, Bildung und Zufriedenheit nach Konsum."""
        self.total_consumption_value += sum(bought.get(g, 0.0) * prices.get(g, GOODS[g].base_price) for g in bought)
        # Essentielles.
        food = bought.get("food", 0.0)
        energy = bought.get("energy", 0.0)
        housing = bought.get("housing", 0.0)
        health_s = bought.get("health_service", 0.0)
        edu = bought.get("education_service", 0.0)
        culture = bought.get("culture_service", 0.0) + bought.get("hospitality_service", 0.0)
        self.need_satisfaction["food"] = clamp(0.75 * self.need_satisfaction["food"] + 0.25 * min(1.2, food / 0.24), 0.0, 1.2)
        self.need_satisfaction["energy"] = clamp(0.75 * self.need_satisfaction["energy"] + 0.25 * min(1.2, energy / 0.14), 0.0, 1.2)
        self.need_satisfaction["housing"] = clamp(0.82 * self.need_satisfaction["housing"] + 0.18 * min(1.2, housing / 0.055), 0.0, 1.2)
        # Gesundheit reagiert stark auf Nahrung, Wohnraum und medizinische Leistung.
        essential_score = (self.need_satisfaction["food"] + self.need_satisfaction["energy"] + self.need_satisfaction["housing"]) / 3.0
        self.health = clamp(self.health + 0.025 * (essential_score - 0.72) + 0.020 * min(1.0, health_s / 0.06), 0.05, 1.0)
        self.education = clamp(self.education + 0.010 * min(1.0, edu / 0.045), 0.01, 1.0)
        self.happiness = clamp(self.happiness + 0.018 * (essential_score - 0.70) + 0.010 * min(1.0, culture / 0.06), 0.0, 1.0)

    def consumption_budget(self):
        liquid = self.wallet.positive_value()
        # Schulden und Arbeitslosigkeit erhöhen Vorsicht.
        debt_pressure = clamp(self.wallet.debt_value() / max(1.0, liquid + 1.0), 0.0, 1.0)
        prop = self.consumption_propensity * (1.0 - 0.35 * debt_pressure)
        if self.unemployed_periods > 0:
            prop *= 0.85
        return max(0.0, liquid * clamp(prop, 0.20, 0.88))


class Firm(EconomicAgent):
    def __init__(self, agent_id, rng, sector_key):
        recipe = SECTOR_RECIPES[sector_key]
        EconomicAgent.__init__(self, agent_id, "%s-Firma %s" % (recipe.label, agent_id), "firm")
        self.sector_key = sector_key
        self.recipe = recipe
        self.output_good = recipe.output_good
        self.price = GOODS[self.output_good].base_price * rng.uniform(0.85, 1.25)
        self.target_output = rng.uniform(14.0, 42.0)
        self.expected_demand = self.target_output
        self.capital_stock = rng.uniform(15.0, 70.0) * (1.0 + recipe.capital_intensity)
        self.automation_level = rng.uniform(0.00, 0.25 if sector_key in ("software_ai", "manufacturing", "finance") else 0.12)
        self.management_quality = rng.uniform(0.35, 0.85)
        self.worker_slots = int(clamp(rng.gauss(9.0, 4.0), 3, 24))
        self.workers = []  # Liste von (household, labor_type, wage, skill)
        self.vacancies = defaultdict(int)
        self.last_output = 0.0
        self.last_quality = 0.7
        self.last_sales_qty = 0.0
        self.last_sales_value = 0.0
        self.last_wage_bill = 0.0
        self.last_input_cost = 0.0
        self.last_profit = 0.0
        self.bankruptcy_counter = 0
        self.productivity_trend = rng.uniform(0.95, 1.05)
        self.market_power = rng.uniform(0.85, 1.15)
        self.total_output = 0.0
        self.total_sales = 0.0
        self._init_wallet_and_inventory(rng)

    def _init_wallet_and_inventory(self, rng):
        # Firmen starten mit einer semantischen Kapitalstruktur passend zum Sektor.
        self.wallet.add_coin(1, rng.uniform(2, 8))
        self.wallet.add_coin(5, rng.uniform(2, 8))
        self.wallet.add_coin(10, rng.uniform(1, 4))
        self.wallet.add_coin(11, rng.uniform(0.5, 3))
        self.wallet.add_coin(13, rng.uniform(0.5, 3))
        if self.recipe.capital_intensity > 0.5:
            self.wallet.add_coin(18, rng.uniform(0.2, 2.0))
            self.wallet.add_coin(20, rng.uniform(0.1, 1.5))
        if self.sector_key in ("software_ai", "research", "education"):
            self.wallet.add_coin(12, rng.uniform(0.5, 4.0))
            self.wallet.add_coin(19, rng.uniform(0.1, 2.0))
        self.inventory[self.output_good] = rng.uniform(1.0, 10.0)
        for g in self.recipe.input_goods:
            self.inventory[g] += rng.uniform(0.0, 5.0)

    def reset_period(self):
        self.workers = []
        self.vacancies = defaultdict(int)
        self.last_output = 0.0
        self.last_quality = 0.7
        self.last_sales_qty = 0.0
        self.last_sales_value = 0.0
        self.last_wage_bill = 0.0
        self.last_input_cost = 0.0
        self.last_profit = 0.0

    def plan_vacancies(self, rng, labor_market_pressure=1.0):
        # Zielproduktion passt sich an Verkaufssignal und Lager an.
        inventory = self.inventory.get(self.output_good, 0.0)
        inv_pressure = clamp(inventory / max(1.0, self.expected_demand), 0.0, 3.0)
        desired = self.expected_demand * (1.15 - 0.25 * inv_pressure)
        desired = clamp(desired, 2.0, self.capital_stock * 0.7 + 10.0)
        self.target_output = 0.65 * self.target_output + 0.35 * desired
        workers_needed = int(math.ceil(self.target_output / max(1.5, self.recipe.base_productivity * 0.8)))
        workers_needed = int(clamp(workers_needed, 1, self.worker_slots))
        mix = self.recipe.normalized_labor_mix()
        for labor_type, share in mix.items():
            n = int(round(workers_needed * share))
            if n <= 0 and rng.random() < share * workers_needed:
                n = 1
            if n > 0:
                self.vacancies[labor_type] += n
        # Management braucht fast immer mindestens eine Person, wenn groß genug.
        if workers_needed >= 6 and "management" in LABOR_TYPES:
            self.vacancies["management"] = max(self.vacancies.get("management", 0), 1)
        return dict(self.vacancies)

    def wage_offer(self, labor_type, unemployment_rate=0.05, q_shortage=0.0):
        lt = LABOR_TYPES[labor_type]
        sector_premium = 1.0 + 0.08 * self.recipe.capital_intensity + 0.04 * self.market_power
        scarcity_premium = 1.0 + 0.25 * q_shortage - 0.15 * unemployment_rate
        firm_health = clamp(0.75 + self.wallet.positive_value() / max(10.0, self.wallet.debt_value() + 20.0), 0.65, 1.45)
        return max(0.2, lt.base_wage * sector_premium * scarcity_premium * firm_health)

    def hire(self, household, labor_type, wage_zw):
        skill = household.employability(labor_type)
        self.workers.append((household, labor_type, wage_zw, skill))
        household.current_employer = self.id
        household.last_employer = self.id
        return True

    def pay_wages(self):
        total = 0.0
        for household, labor_type, wage_zw, skill in self.workers:
            # Lohn ist Q-semantisch passend zum Arbeitstyp. Bei Liquiditätsmangel entsteht Typenschuld.
            vec = LABOR_TYPES[labor_type].wage_vector(wage_zw)
            amount = vector_value(vec)
            preferred = list(vec.keys()) + list(range(20, 0, -1))
            debt_q = max(vec.keys(), key=lambda q: Q_VALUES[q]) if vec else 1
            self.wallet.pay_value_to(household.wallet, amount, preferred_order=preferred, debt_q=debt_q, allow_debt=True)
            household.receive_wage(wage_zw, labor_type)
            self.spend_value(wage_zw)
            total += wage_zw
        self.last_wage_bill = total
        return total

    def buy_input_need(self, horizon_output=None):
        """Benötigte Inputmengen für Zielproduktion."""
        if horizon_output is None:
            horizon_output = self.target_output
        need = {}
        for g, coeff in self.recipe.input_goods.items():
            required = coeff * horizon_output
            missing = max(0.0, required - self.inventory.get(g, 0.0))
            if missing > EPS:
                need[g] = missing
        return need

    def input_limit(self):
        if not self.recipe.input_goods:
            return 1e12
        limits = []
        for g, coeff in self.recipe.input_goods.items():
            if coeff <= EPS:
                continue
            limits.append(self.inventory.get(g, 0.0) / coeff)
        if not limits:
            return 1e12
        return max(0.0, min(limits))

    def _labor_balance_factor(self):
        if not self.workers:
            return 0.0, 0.0
        mix = self.recipe.normalized_labor_mix()
        effective = defaultdict(float)
        total_eff = 0.0
        for _, labor_type, _, skill in self.workers:
            effective[labor_type] += max(0.0, skill)
            total_eff += max(0.0, skill)
        if total_eff <= EPS:
            return 0.0, 0.0
        ratios = []
        for lt, share in mix.items():
            have_share = effective.get(lt, 0.0) / total_eff
            ratios.append(safe_div(have_share, share, 0.0))
        # Fehlende Schlüsselfähigkeiten sollen bremsen, aber nicht alles auf null setzen.
        balance = clamp(0.45 + 0.55 * min(1.5, min(ratios) if ratios else 1.0), 0.15, 1.25)
        avg_skill = total_eff / float(len(self.workers))
        return balance, avg_skill

    def _q_structure_factor(self):
        if not self.recipe.critical_q:
            return 1.0
        pos = 0.0
        debt = 0.0
        for q in self.recipe.critical_q:
            pos += self.wallet.positive_qty(q) * Q_VALUES[q]
            debt += self.wallet.debt_qty(q) * Q_VALUES[q]
        strength = 1.0 + 0.015 * min(80.0, pos)
        penalty = 1.0 / (1.0 + 0.035 * debt)
        return clamp(strength * penalty, 0.35, 1.50)

    def produce(self, rng, mint, external_factor=1.0):
        balance, avg_skill = self._labor_balance_factor()
        if not self.workers or balance <= EPS:
            self.last_output = 0.0
            self.last_quality = 0.25
            return 0.0
        work_units = sum(max(0.0, skill) for _, _, _, skill in self.workers)
        capital_factor = clamp(math.sqrt(max(1.0, self.capital_stock) / (8.0 + 8.0 * self.recipe.capital_intensity)), 0.45, 2.10)
        automation_factor = 1.0 + self.automation_level * (0.45 if self.sector_key not in ("software_ai", "manufacturing", "finance", "logistics") else 0.75)
        q_factor = self._q_structure_factor()
        raw_output = self.recipe.base_productivity * work_units * balance * capital_factor * automation_factor * q_factor * self.productivity_trend * external_factor
        raw_output = min(raw_output, self.target_output * 1.50)
        # Inputs begrenzen die Produktion, aber kleine Inputlücken sollen keine ganze
        # Volkswirtschaft auf null setzen. Darum wird nicht hart auf das Minimum
        # gekappt, sondern ein gewichteter Inputfaktor berechnet.
        input_factor = 1.0
        if self.recipe.input_goods:
            total_coeff = sum(max(0.0, c) for c in self.recipe.input_goods.values())
            weighted_sat = 0.0
            for g, coeff in self.recipe.input_goods.items():
                if coeff <= EPS:
                    continue
                need = coeff * max(EPS, raw_output)
                sat = clamp(self.inventory.get(g, 0.0) / need, 0.0, 1.0)
                # Energie/Rohstoffe sind systemkritischer als kleine Dienstleistungsinputs.
                critical = 1.35 if g in ("energy", "raw_materials", "manufactured_goods") else 1.0
                weighted_sat += sat * coeff * critical
            denom = sum(c * (1.35 if g in ("energy", "raw_materials", "manufactured_goods") else 1.0) for g, c in self.recipe.input_goods.items())
            input_satisfaction = safe_div(weighted_sat, denom, 1.0)
            input_factor = clamp(0.32 + 0.68 * input_satisfaction, 0.25, 1.0)
        output = raw_output * input_factor
        # Qualität.
        debt_pressure = clamp(self.wallet.debt_value() / max(10.0, self.wallet.positive_value() + 10.0), 0.0, 3.0)
        quality = 0.40 + 0.22 * balance + 0.22 * avg_skill + 0.12 * clamp(q_factor, 0.0, 1.3) + 0.08 * input_factor + rng.gauss(0.0, 0.045)
        quality -= 0.08 * debt_pressure
        quality = clamp(quality, 0.05, 1.20)
        output = max(0.0, output * clamp(0.70 + 0.30 * quality, 0.50, 1.10))
        # Inputs verbrauchen, soweit vorhanden. Fehlmengen senken Qualität und erzeugen ggf. Schuld,
        # aber sie verhindern nicht jede Restproduktion.
        for g, coeff in self.recipe.input_goods.items():
            self.remove_good(g, coeff * output)
        self.add_good(self.output_good, output)
        self.last_output = output
        self.last_quality = quality
        self.total_output += output
        # Q-Münzen prägen: Produktion erzeugt semantisch gedeckte Münzen.
        output_value = output * self.price
        minted_vec = self.recipe.q_mint_for_output_value(output_value, quality)
        mint.mint_vector(self.wallet, minted_vec, quality=quality)
        # Niedrige Qualität erzeugt technische/operative Schuld in kritischen Qs.
        if quality < 0.62 and self.recipe.critical_q:
            deficit_value = output_value * (0.62 - quality) * 0.12
            if deficit_value > EPS:
                share = 1.0 / float(len(self.recipe.critical_q))
                for q in self.recipe.critical_q:
                    self.wallet.add_coin(q, -(deficit_value * share) / Q_VALUES[q])
        # Kapitalabschreibung.
        depreciation = 0.010 + 0.010 * self.recipe.capital_intensity
        self.capital_stock *= (1.0 - depreciation)
        return output

    def receive_sale(self, qty, value):
        self.last_sales_qty += qty
        self.last_sales_value += value
        self.total_sales += value
        self.receive_value(value)

    def end_period_update(self, rng, sector_shortage=0.0):
        revenue = self.last_sales_value
        costs = self.last_wage_bill + self.last_input_cost
        self.last_profit = revenue - costs
        # Erwartete Nachfrage aus Verkäufen + unerfüllter Nachfrage ableiten.
        if self.last_sales_qty > self.inventory.get(self.output_good, 0.0) * 0.65:
            self.expected_demand = 0.75 * self.expected_demand + 0.25 * max(1.0, self.last_sales_qty * 1.10)
        else:
            self.expected_demand = 0.85 * self.expected_demand + 0.15 * max(1.0, self.last_sales_qty)
        # Preisregel.
        inv = self.inventory.get(self.output_good, 0.0)
        sold = self.last_sales_qty
        if sold > 0:
            sellthrough = sold / max(EPS, sold + inv)
        else:
            sellthrough = 0.0
        price_change = 0.0
        price_change += 0.035 * (sellthrough - 0.48)
        price_change += 0.030 * sector_shortage
        price_change += 0.015 * (0.70 - self.last_quality)
        self.price *= clamp(1.0 + price_change, 0.88, 1.15)
        self.price = max(0.05, self.price)
        # Erfolg verbessert Reputation und Kapital; Verlust führt zu Schuldenstress.
        if self.last_profit > 0:
            self.reputation[self.sector_key] = clamp(self.reputation[self.sector_key] + 0.01 * self.last_quality, 0.0, 1.0)
            invest_value = min(self.last_profit * 0.18, self.wallet.positive_value() * 0.12)
            if invest_value > 0.25:
                # Investition verbraucht Liquidität und erhöht Kapital/Automatisierung leicht.
                self.wallet.extract_value(invest_value, debt_q=18, allow_debt=False)
                self.capital_stock += invest_value * (0.65 + 0.30 * self.recipe.capital_intensity)
                if self.sector_key in ("software_ai", "manufacturing", "logistics", "finance", "energy"):
                    self.automation_level = clamp(self.automation_level + 0.002 * invest_value, 0.0, 1.20)
        else:
            self.reputation[self.sector_key] = clamp(self.reputation[self.sector_key] - 0.006, 0.0, 1.0)
        # Insolvenzsignal.
        if self.net_worth() < -20.0 or self.wallet.debt_value() > max(25.0, self.wallet.positive_value() * 3.5):
            self.bankruptcy_counter += 1
        else:
            self.bankruptcy_counter = max(0, self.bankruptcy_counter - 1)
        if self.bankruptcy_counter >= 5:
            self.bankrupt = True


class Bank(EconomicAgent):
    def __init__(self, agent_id, rng):
        EconomicAgent.__init__(self, agent_id, "Q-Bank %s" % agent_id, "bank")
        self.risk_appetite = rng.uniform(0.35, 0.75)
        self.loan_book = []
        self.default_losses = 0.0
        self.interest_income = 0.0
        self.capital_buffer_target = rng.uniform(0.10, 0.22)
        # Banken starten mit breiten Reserven; Q10/Q18 wegen Risikoprüfung.
        for q, qty in {1: 60, 5: 35, 8: 18, 10: 30, 11: 18, 13: 25, 16: 18, 18: 12, 20: 6}.items():
            self.wallet.add_coin(q, qty * rng.uniform(0.7, 1.3))

    def risk_score(self, borrower):
        net = borrower.net_worth()
        debt = borrower.wallet.debt_value()
        pos = borrower.wallet.positive_value()
        liquidity = safe_div(pos, debt + 1.0, 1.0)
        rep = 0.55
        if hasattr(borrower, "sector_key"):
            rep = borrower.reputation[borrower.sector_key]
        base = 0.45
        base += 0.25 * clamp(liquidity / 2.0, 0.0, 1.0)
        base += 0.20 * rep
        base += 0.10 * (1.0 if net > 0 else 0.0)
        if getattr(borrower, "bankrupt", False):
            base *= 0.2
        return clamp(base, 0.0, 1.0)


class Government(EconomicAgent):
    def __init__(self, agent_id="GOV"):
        EconomicAgent.__init__(self, agent_id, "Staat / Gemeingüterfonds", "government")
        self.tax_rate_income = 0.10
        self.tax_rate_profit = 0.13
        self.vat_rate = 0.04
        self.basic_income = 0.18
        self.unemployment_support = 0.38
        self.public_investment_rate = 0.10
        self.debt_limit_soft = 600.0
        self.policy_mode = "balanced"
        self.public_orders = defaultdict(float)
        self.tax_revenue = 0.0
        self.transfer_spending = 0.0
        self.public_spending = 0.0
        # Öffentlicher Startbestand: Grundversorgung, Infrastruktur, Toolboxen, Gemeingüter.
        self.wallet.add_coin(1, 250.0)
        self.wallet.add_coin(2, 160.0)
        self.wallet.add_coin(3, 120.0)
        self.wallet.add_coin(8, 70.0)
        self.wallet.add_coin(9, 40.0)
        self.wallet.add_coin(11, 80.0)
        self.wallet.add_coin(12, 80.0)
        self.wallet.add_coin(16, 90.0)
        self.wallet.add_coin(18, 35.0)

    def reset_period_accounts(self):
        EconomicAgent.reset_period_accounts(self)
        self.tax_revenue = 0.0
        self.transfer_spending = 0.0
        self.public_spending = 0.0
        self.public_orders = defaultdict(float)

    def collect_tax_value(self, payer, amount_zw, debt_q=10):
        amount_zw = max(0.0, amount_zw)
        if amount_zw <= EPS:
            return 0.0
        paid = payer.wallet.pay_value_to(self.wallet, amount_zw, debt_q=debt_q, allow_debt=True)
        payer.spend_value(paid)
        self.receive_value(paid)
        self.tax_revenue += paid
        return paid

    def pay_transfer(self, household, amount_zw):
        if amount_zw <= EPS:
            return 0.0
        # Fiskalregel: passive Transfers dürfen Defizite abfedern, aber nicht unbegrenzt
        # schneller wachsen als reale öffentliche Q-Deckung.
        debt_pressure = self.wallet.debt_value() / max(1.0, self.debt_limit_soft)
        if debt_pressure > 1.0:
            amount_zw *= clamp(1.0 / (1.0 + 0.55 * (debt_pressure - 1.0)), 0.25, 1.0)
        # Sozialtransfer als Grundmünzen / Teilhabemünzen.
        dist = {1: 0.45, 2: 0.20, 3: 0.15, 11: 0.10, 16: 0.10}
        vec = vector_from_value(amount_zw, dist)
        preferred = list(vec.keys()) + list(range(20, 0, -1))
        self.wallet.pay_value_to(household.wallet, amount_zw, preferred_order=preferred, debt_q=1, allow_debt=True)
        household.public_benefit_received += amount_zw
        household.receive_value(amount_zw)
        self.spend_value(amount_zw)
        self.transfer_spending += amount_zw
        return amount_zw

    def set_policy_by_metrics(self, metrics):
        # Einfache automatische Stabilisierung.
        unemployment = metrics.get("unemployment_rate", 0.0)
        inflation = metrics.get("inflation", 0.0)
        q18_debt = metrics.get("q18_debt_value", 0.0)
        q16_debt = metrics.get("q16_debt_value", 0.0)
        if unemployment > 0.18:
            self.basic_income = clamp(self.basic_income + 0.03, 0.40, 1.20)
            self.public_investment_rate = clamp(self.public_investment_rate + 0.03, 0.12, 0.45)
        elif inflation > 0.08:
            self.basic_income = clamp(self.basic_income - 0.02, 0.35, 1.00)
            self.public_investment_rate = clamp(self.public_investment_rate - 0.015, 0.08, 0.35)
        if q18_debt + q16_debt > 200:
            self.public_investment_rate = clamp(self.public_investment_rate + 0.04, 0.15, 0.50)
