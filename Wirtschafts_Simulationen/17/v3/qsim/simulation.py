# -*- coding: utf-8 -*-
"""Kernsimulation der Q-Ökonomie."""

from __future__ import print_function

import json
import math
import os
import random
from collections import defaultdict

from .agents import Household, Firm, Bank, Government, EconomicAgent
from .finance import CreditSystem
from .markets import LaborMarket, GoodsMarket, CoinMarket
from .money import Wallet, Mint, Q_VALUES, Q_META, vector_from_value
from .sectors import SECTOR_RECIPES, GOODS, LABOR_TYPES, PUBLIC_GOODS
from .utils import IdGenerator, EventLog, clamp, safe_div, gini, mean, percentile, EPS
from .utf8art import format_progress_line


SCENARIOS = {
    "balanced": "Ausgewogene Startwirtschaft ohne großen Schock.",
    "code_bubble": "Software/KI boomt, aber Constraints, Betrieb und Architektur geraten unter Druck.",
    "energy_crisis": "Energieproduktion ist gedrückt, Energiepreise und Folgekosten steigen.",
    "food_crisis": "Landwirtschaftlicher Schock mit Nahrungsmittelknappheit.",
    "architecture_crisis": "Q18-Architektur ist knapp; technische Schulden werden schneller sichtbar.",
    "automation_wave": "Automatisierung steigt stark; Produktivität wächst, aber Arbeitsmarktverdrängung entsteht.",
    "public_investment": "Staat erhöht Bildung, Infrastruktur, Gesundheit und Gemeingüterfonds.",
    "austerity": "Staatliche Ausgaben und Transfers sinken; private Märkte müssen mehr tragen.",
    "climate_shock": "Landwirtschaft, Bau, Energie und Umwelt werden durch Klimafolgen belastet.",
}


class ExternalSector(EconomicAgent):
    """Rest der Welt: Exportnachfrage und Importpuffer."""

    def __init__(self):
        EconomicAgent.__init__(self, "ROW", "Rest der Welt", "external")
        for q, qty in {1: 200, 5: 80, 10: 90, 13: 80, 16: 60, 18: 40, 20: 30}.items():
            self.wallet.add_coin(q, float(qty))
        self.exports_value = 0.0
        self.imports_value = 0.0

    def replenish(self):
        # Rest der Welt kann als offener Devisen-/Q-Raum zusätzliche Forderungen tragen.
        for q, qty in {1: 10, 5: 4, 10: 4, 13: 4, 16: 3, 18: 2, 20: 1}.items():
            self.wallet.add_coin(q, qty)


class EconomySimulation(object):
    def __init__(self, seed=42, households=300, firms=80, banks=4, scenario="balanced"):
        self.seed = int(seed)
        self.rng = random.Random(self.seed)
        self.ids = IdGenerator()
        self.period = 0
        self.scenario = scenario if scenario in SCENARIOS else "balanced"
        self.event_log = EventLog(max_items=3000)
        self.mint = Mint()
        self.credit = CreditSystem(self.ids)
        self.labor_market = LaborMarket()
        self.goods_market = GoodsMarket()
        self.coin_market = CoinMarket()
        self.government = Government()
        self.external = ExternalSector()
        self.households = []
        self.firms = []
        self.banks = []
        self.metrics_history = []
        self._init_population(households, firms, banks)
        self._apply_initial_scenario()
        self.last_metrics = self.compute_metrics(initial=True)

    def _init_population(self, n_households, n_firms, n_banks):
        archetypes = [
            ("manual", 0.24),
            ("industrial", 0.18),
            ("care", 0.16),
            ("knowledge", 0.18),
            ("service", 0.18),
            ("mixed", 0.06),
        ]
        for _ in range(int(n_households)):
            r = self.rng.random()
            acc = 0.0
            arch = "mixed"
            for a, w in archetypes:
                acc += w
                if r <= acc:
                    arch = a
                    break
            self.households.append(Household(self.ids.new("H"), self.rng, archetype=arch))
        sector_keys = list(SECTOR_RECIPES.keys())
        # Basisverteilung: reale Grundversorgung + Dienste + Wissenssektoren.
        sector_weights = {
            "agriculture": 0.075,
            "mining": 0.035,
            "energy": 0.050,
            "manufacturing": 0.105,
            "construction": 0.075,
            "healthcare": 0.075,
            "education": 0.065,
            "logistics": 0.070,
            "retail": 0.075,
            "finance": 0.045,
            "public": 0.055,
            "creative": 0.045,
            "hospitality": 0.050,
            "maintenance": 0.060,
            "software_ai": 0.075,
            "research": 0.040,
            "environment": 0.035,
            "security": 0.035,
        }
        # Mindestens eine Firma je Sektor, wenn möglich.
        for s in sector_keys[:min(len(sector_keys), n_firms)]:
            self.firms.append(Firm(self.ids.new("F"), self.rng, s))
        remaining = max(0, int(n_firms) - len(self.firms))
        weighted = list(sector_weights.items())
        for _ in range(remaining):
            r = self.rng.random() * sum(w for _, w in weighted)
            acc = 0.0
            chosen = weighted[-1][0]
            for s, w in weighted:
                acc += w
                if r <= acc:
                    chosen = s
                    break
            self.firms.append(Firm(self.ids.new("F"), self.rng, chosen))
        for _ in range(int(n_banks)):
            self.banks.append(Bank(self.ids.new("B"), self.rng))
        self.event_log.add(0, "init", "Simulation initialisiert", {
            "households": len(self.households),
            "firms": len(self.firms),
            "banks": len(self.banks),
            "scenario": self.scenario,
        })

    def _apply_initial_scenario(self):
        gov = self.government
        if self.scenario == "public_investment":
            gov.public_investment_rate = 0.24
            gov.basic_income = 0.32
            gov.tax_rate_profit = 0.16
        elif self.scenario == "austerity":
            gov.public_investment_rate = 0.05
            gov.basic_income = 0.08
            gov.tax_rate_income = 0.08
            gov.tax_rate_profit = 0.10
        elif self.scenario == "architecture_crisis":
            self.mint.validation_strictness = 1.12
            for f in self.firms:
                if self.rng.random() < 0.35:
                    f.wallet.add_coin(18, -self.rng.uniform(0.5, 3.0))
        elif self.scenario == "code_bubble":
            for f in self.firms:
                if f.sector_key == "software_ai":
                    f.target_output *= 1.45
                    f.wallet.add_coin(5, self.rng.uniform(5.0, 15.0))
                if self.rng.random() < 0.25:
                    f.wallet.add_coin(10, -self.rng.uniform(0.3, 1.5))
                    f.wallet.add_coin(18, -self.rng.uniform(0.2, 1.2))
        elif self.scenario == "automation_wave":
            for f in self.firms:
                if f.sector_key in ("software_ai", "manufacturing", "logistics", "finance", "retail"):
                    f.automation_level += self.rng.uniform(0.20, 0.45)
                    f.worker_slots = max(1, int(f.worker_slots * self.rng.uniform(0.70, 0.92)))
        elif self.scenario == "energy_crisis":
            for f in self.firms:
                if f.sector_key == "energy":
                    f.capital_stock *= 0.70
                    f.price *= 1.25
        elif self.scenario == "food_crisis":
            for f in self.firms:
                if f.sector_key == "agriculture":
                    f.capital_stock *= 0.80
                    f.price *= 1.20
        elif self.scenario == "climate_shock":
            for f in self.firms:
                if f.sector_key in ("agriculture", "construction", "energy"):
                    f.capital_stock *= self.rng.uniform(0.70, 0.90)
                    f.wallet.add_coin(17, -self.rng.uniform(0.2, 1.8))
                if f.sector_key == "environment":
                    f.target_output *= 1.50

    def all_agents(self):
        return list(self.households) + list(self.firms) + list(self.banks) + [self.government, self.external]

    def agents_by_id(self):
        return dict((a.id, a) for a in self.all_agents())

    def scenario_sector_factor(self, firm):
        s = self.scenario
        k = firm.sector_key
        factor = 1.0
        if s == "energy_crisis":
            if k == "energy":
                factor *= 0.62 + 0.10 * math.sin(self.period / 5.0)
            elif "energy" in firm.recipe.input_goods:
                factor *= 0.90
        elif s == "food_crisis":
            if k == "agriculture":
                factor *= 0.66 + 0.08 * math.sin(self.period / 4.0)
            elif k == "hospitality":
                factor *= 0.92
        elif s == "code_bubble":
            if k == "software_ai":
                factor *= 1.25
            if k in ("maintenance", "public", "construction"):
                factor *= 0.96
        elif s == "architecture_crisis":
            if k in ("construction", "manufacturing", "software_ai", "energy"):
                factor *= 0.88
        elif s == "automation_wave":
            if k in ("software_ai", "manufacturing", "logistics", "finance", "retail"):
                factor *= 1.18
        elif s == "public_investment":
            if k in ("education", "healthcare", "public", "environment", "maintenance", "construction"):
                factor *= 1.10
        elif s == "austerity":
            if firm.recipe.public_share > 0.4:
                factor *= 0.88
        elif s == "climate_shock":
            if k in ("agriculture", "energy", "construction", "logistics"):
                factor *= 0.82
            if k == "environment":
                factor *= 1.20
        # Kleine idiosynkratische Schwankung.
        factor *= self.rng.uniform(0.96, 1.04)
        return clamp(factor, 0.35, 1.65)

    def apply_transfers_and_taxes_pre_market(self):
        gov = self.government
        # Transfers am Anfang, damit Konsum nicht künstlich kollabiert.
        for h in self.households:
            gov.pay_transfer(h, gov.basic_income)
            if h.current_employer is None and h.unemployed_periods > 0:
                gov.pay_transfer(h, gov.unemployment_support * clamp(0.7 + 0.05 * h.unemployed_periods, 0.7, 1.4))
        # Einkommensteuer auf aktuelle Arbeitseinkommen, nicht auf Transfer.
        for h in self.households:
            if h.current_wage > 0:
                gov.collect_tax_value(h, h.current_wage * gov.tax_rate_income, debt_q=10)


    def public_job_program(self):
        """Automatischer öffentlicher Arbeitsanker bei hoher Arbeitslosigkeit.

        Das ist kein bloßer Transfer: Haushalte werden für öffentliche,
        ökologische, Bildungs-, Wartungs- und Sicherheitsleistungen bezahlt.
        Die Arbeit erzeugt kleine Mengen öffentlicher Güter und validierte Q-Deckung.
        """
        unemployed = [h for h in self.households if h.current_employer is None and h.health > 0.03]
        if not unemployed:
            return 0
        natural = int(0.08 * len(self.households))
        excess = max(0, len(unemployed) - natural)
        if excess <= 0:
            return 0
        # Je höher öffentliche Investition, desto stärker das Jobprogramm.
        slots = int(min(len(unemployed), excess * clamp(0.45 + self.government.public_investment_rate, 0.40, 0.78)))
        if slots <= 0:
            return 0
        self.rng.shuffle(unemployed)
        hired = 0
        job_goods = {
            "public_service": "public_service",
            "environmental": "environment_service",
            "maintenance": "maintenance_service",
            "teaching": "education_service",
            "care": "health_service",
            "security": "security_service",
            "manual_basic": "public_service",
            "logistics": "transport_service",
        }
        for h in unemployed[:slots]:
            candidates = list(job_goods.keys())
            lt = max(candidates, key=lambda x: h.employability(x) + self.rng.random() * 0.03)
            skill = h.employability(lt)
            if skill < 0.05:
                continue
            wage = LABOR_TYPES[lt].base_wage * (0.72 + 0.25 * skill)
            # Staat bezahlt wertflexibel, semantisch bevorzugt nach Arbeitstyp.
            vec = LABOR_TYPES[lt].wage_vector(wage)
            preferred = list(vec.keys()) + list(range(20, 0, -1))
            debt_q = 16 if lt in ("public_service", "security", "maintenance") else 11
            self.government.wallet.pay_value_to(h.wallet, wage, preferred_order=preferred, debt_q=debt_q, allow_debt=True)
            self.government.spend_value(wage)
            self.government.public_spending += wage
            h.current_employer = self.government.id
            h.receive_wage(wage, lt)
            # Öffentliche Arbeit schafft öffentliche Güter.
            good = job_goods[lt]
            self.government.inventory[good] += skill * 0.55
            # Und sie erzeugt eine geprüfte, aber moderate Q-Deckung.
            if lt in ("public_service", "security"):
                dist = {10: 0.25, 11: 0.15, 14: 0.25, 16: 0.35}
            elif lt == "environmental":
                dist = {10: 0.25, 12: 0.10, 17: 0.25, 18: 0.40}
            elif lt == "maintenance":
                dist = {10: 0.20, 16: 0.45, 17: 0.20, 20: 0.15}
            elif lt == "teaching":
                dist = {3: 0.20, 6: 0.15, 12: 0.45, 14: 0.20}
            elif lt == "care":
                dist = {11: 0.40, 13: 0.25, 14: 0.10, 16: 0.25}
            else:
                dist = {1: 0.35, 2: 0.25, 7: 0.15, 16: 0.25}
            self.mint.mint_vector(self.government.wallet, vector_from_value(wage * 0.70, dist), quality=0.82 + 0.15 * skill)
            hired += 1
        if hired:
            self.event_log.add(self.period, "public_jobs", "Öffentliches Jobprogramm beschäftigt %d Personen" % hired, {"hired": hired})
        return hired

    def firms_get_bridge_credit_if_needed(self):
        if not self.banks:
            return
        for f in self.firms:
            if f.bankrupt:
                continue
            # Liquidität für Löhne und Inputkosten.
            planned_wage = 0.0
            for lt, n in f.vacancies.items():
                planned_wage += n * f.wage_offer(lt, unemployment_rate=self.labor_market.unemployment_rate)
            input_need = f.buy_input_need()
            input_cost = sum(qty * self.goods_market.avg_prices.get(g, GOODS[g].base_price) for g, qty in input_need.items())
            need = max(0.0, (planned_wage + input_cost * 0.6) - f.wallet.positive_value())
            if need > 1.5:
                bank = max(self.banks, key=lambda b: b.risk_score(f) + self.rng.random() * 0.03)
                purpose = "wage_bridge" if planned_wage > input_cost else "input_purchase"
                self.credit.grant_loan(bank, f, need, purpose=purpose, term=6)

    def collect_profit_taxes(self):
        for f in self.firms:
            if f.last_profit > 0 and not f.bankrupt:
                self.government.collect_tax_value(f, f.last_profit * self.government.tax_rate_profit, debt_q=10)

    def external_trade(self):
        self.external.replenish()
        self.external.exports_value = 0.0
        self.external.imports_value = 0.0
        # Exportnachfrage kauft reale Güter aus exportfähigen Sektoren.
        for f in self.firms:
            if f.bankrupt or f.recipe.export_share <= 0:
                continue
            demand_qty = max(0.0, f.expected_demand * f.recipe.export_share * self.rng.uniform(0.3, 1.1))
            before = self.goods_market.sales_value
            self.goods_market.buy_good(self.external, f.output_good, demand_qty, self.firms, government=None, allow_debt=True)
            self.external.exports_value += max(0.0, self.goods_market.sales_value - before)
        # Importpuffer bei starken Engpässen: importierte Güter werden bei produzierenden Firmen eingelagert,
        # aber der Staat/Rest der Welt verbucht Kosten. Dadurch verschwinden Engpässe nicht kostenlos.
        for g, unmet in list(self.goods_market.unmet_qty_by_good.items()):
            if unmet <= 5.0:
                continue
            producers = [f for f in self.firms if f.output_good == g and not f.bankrupt]
            if not producers:
                continue
            import_price = self.goods_market.avg_prices.get(g, GOODS[g].base_price) * 1.20
            desired_import_qty = unmet * 0.25
            desired_import_value = desired_import_qty * import_price
            # Importe sind ein Puffer, aber kein kostenloser unendlicher Staatskredit.
            # Der Staat importiert nur aus vorhandener Liquidität; sonst bleiben Engpässe sichtbar.
            liquidity_cap = self.government.wallet.positive_value() * (0.10 if GOODS[g].essential >= 0.65 else 0.04)
            import_value = min(desired_import_value, liquidity_cap)
            if import_value > 1.0:
                import_qty = import_value / import_price
                paid = self.government.wallet.pay_value_to(self.external.wallet, import_value, debt_q=16, allow_debt=False)
                if paid > 0:
                    self.government.spend_value(paid)
                    self.external.receive_value(paid)
                    self.external.imports_value += paid
                    per = import_qty / float(len(producers))
                    for p in producers:
                        p.inventory[g] += per

    def bankruptcy_and_replacement(self):
        alive = []
        removed = 0
        for f in self.firms:
            if f.bankrupt:
                removed += 1
                self.event_log.add(self.period, "bankruptcy", "%s ist insolvent" % f.name, {
                    "sector": f.sector_key,
                    "debt_value": f.wallet.debt_value(),
                    "net_worth": f.net_worth(),
                })
                # Restwerte werden teilweise zu Q1/Q2-Problemen der Wirtschaft.
                self.government.wallet.add_coin(1, f.wallet.debt_value() / Q_VALUES[1] * 0.05)
                continue
            alive.append(f)
        self.firms = alive
        # Ersetze einen Teil insolventer Firmen durch neue kleine Firmen im gleichen allgemeinen Markt.
        for _ in range(removed):
            if self.rng.random() < 0.75:
                # Gründungen bevorzugen knappe Güter.
                shortages = self.goods_market.unmet_qty_by_good
                if shortages:
                    good = max(shortages, key=lambda g: shortages[g])
                    sector = None
                    for s, r in SECTOR_RECIPES.items():
                        if r.output_good == good:
                            sector = s
                            break
                    if sector is None:
                        sector = self.rng.choice(list(SECTOR_RECIPES.keys()))
                else:
                    sector = self.rng.choice(list(SECTOR_RECIPES.keys()))
                nf = Firm(self.ids.new("F"), self.rng, sector)
                nf.capital_stock *= 0.55
                nf.worker_slots = max(1, int(nf.worker_slots * 0.65))
                self.firms.append(nf)
                self.event_log.add(self.period, "startup", "Neue Firma gegründet", {"sector": sector, "firm": nf.id})

    def step(self):
        self.period += 1
        # Periode zurücksetzen.
        for a in self.all_agents():
            a.reset_period_accounts()
        self.goods_market.reset_period()
        self.credit.reset_period()

        # Vorperiodenmetriken steuern Politik.
        self.government.set_policy_by_metrics(self.last_metrics)

        # Q-Marktknappheit vor Arbeitsmarkt bestimmen.
        self.coin_market.update(self.all_agents())

        # Arbeitsmarkt: Firmen suchen alle Arten von Arbeit, nicht nur Intelligenzarbeit.
        self.labor_market.match(
            self.rng,
            self.households,
            self.firms,
            unemployment_rate=self.last_metrics.get("unemployment_rate", 0.08),
            q_shortages=self.coin_market.shortage,
        )

        # Öffentlicher Arbeitsanker bei Nachfragemangel/Arbeitslosigkeit.
        self.public_job_program()

        # Kreditbrücken, dann Löhne.
        self.firms_get_bridge_credit_if_needed()
        for f in self.firms:
            if not f.bankrupt:
                f.pay_wages()

        # Transfers und Steuern nach Jobmatching.
        self.apply_transfers_and_taxes_pre_market()

        # Firmen kaufen Inputs aus dem Gütermarkt.
        self.goods_market.firms_buy_inputs(self.rng, self.firms, banks=self.banks, credit_system=self.credit, government=self.government)

        # Produktion und Münzprägung.
        for f in self.firms:
            if f.bankrupt:
                continue
            f.produce(self.rng, self.mint, external_factor=self.scenario_sector_factor(f))

        # Verkäufe: Haushalte, Staat, Rest der Welt.
        self.goods_market.consume_households(self.rng, self.households, self.firms, government=self.government)
        # Öffentliche Nachfrage braucht aktuelle Metriken der Vorperiode.
        self.goods_market.government_purchases(self.rng, self.government, self.firms, metrics=self.last_metrics)
        self.external_trade()

        # Preise, Firmenabschluss, Gewinnsteuern.
        self.goods_market.update_price_index(self.firms)
        # Sektorale Engpasswerte für Preisregeln.
        shortages_by_good = self.goods_market.unmet_qty_by_good
        for f in self.firms:
            good = f.output_good
            unmet = shortages_by_good.get(good, 0.0)
            sold = self.goods_market.sales_qty_by_good.get(good, 0.0)
            shortage_signal = safe_div(unmet, sold + unmet + 1.0, 0.0)
            f.end_period_update(self.rng, sector_shortage=shortage_signal)
        self.collect_profit_taxes()

        # Kredite bedienen.
        self.credit.service_loans(self.agents_by_id(), event_log=self.event_log, period=self.period)

        # Semantische Schuldreparatur am Coin-Markt.
        self.coin_market.update(self.all_agents())
        self.coin_market.repair_all(self.all_agents(), max_fraction=0.05)
        self.coin_market.update(self.all_agents())

        # Insolvenzen und Gründungen.
        self.bankruptcy_and_replacement()

        # Bildungseffekt öffentlicher/privater Bildungsleistung: zufällige Haushalte lernen.
        self.apply_education_spillover()

        # Szenario-spezifische laufende Effekte.
        self.apply_running_scenario_effects()

        metrics = self.compute_metrics()
        self.metrics_history.append(metrics)
        self.last_metrics = metrics
        self.log_notable_events(metrics)
        return metrics

    def apply_education_spillover(self):
        edu_sales = self.goods_market.sales_qty_by_good.get("education_service", 0.0)
        if edu_sales <= EPS or not self.households:
            return
        n = int(clamp(edu_sales * 0.35, 0, len(self.households)))
        if n <= 0:
            return
        for h in self.rng.sample(self.households, n):
            # Verbessert eine zufällige vorhandene Fähigkeit mit Schwerpunkt auf Zukunftsfähigkeiten.
            candidates = ["teaching", "software", "engineering", "health", "maintenance", "agriculture", "construction", "research", "public_service"]
            lt = self.rng.choice(candidates)
            h.skills[lt] = clamp(h.skills.get(lt, 0.0) + 0.015 * (1.0 - h.skills.get(lt, 0.0)), 0.0, 1.0)
            h.education = clamp(h.education + 0.004, 0.0, 1.0)

    def apply_running_scenario_effects(self):
        if self.scenario == "automation_wave":
            for f in self.firms:
                if f.sector_key in ("software_ai", "manufacturing", "logistics", "finance", "retail") and self.rng.random() < 0.18:
                    f.automation_level = clamp(f.automation_level + self.rng.uniform(0.005, 0.020), 0.0, 1.40)
                    if self.rng.random() < 0.08:
                        f.worker_slots = max(1, f.worker_slots - 1)
        elif self.scenario == "code_bubble":
            # Langsam wachsen Q10/Q18-Schulden, wenn Softwareproduktion schneller wächst als Struktur.
            for f in self.firms:
                if f.sector_key == "software_ai" and f.last_output > 0 and f.last_quality < 0.78:
                    f.wallet.add_coin(10, -0.03 * f.last_output / Q_VALUES[10])
                    f.wallet.add_coin(18, -0.02 * f.last_output / Q_VALUES[18])
        elif self.scenario == "climate_shock":
            if self.period % 10 == 0:
                for f in self.firms:
                    if f.sector_key in ("agriculture", "energy", "construction", "logistics") and self.rng.random() < 0.20:
                        f.capital_stock *= self.rng.uniform(0.94, 0.99)
                        f.wallet.add_coin(17, -self.rng.uniform(0.05, 0.30))

    def log_notable_events(self, m):
        if self.period % 12 == 0:
            self.event_log.add(self.period, "annual", "Jahres-/Zyklusbericht", {
                "bqp": round(m.get("bqp", 0.0), 3),
                "unemployment": round(m.get("unemployment_rate", 0.0), 3),
                "inflation": round(m.get("inflation", 0.0), 3),
                "debt": round(m.get("total_debt_value", 0.0), 3),
            })
        if m.get("unemployment_rate", 0.0) > 0.25:
            self.event_log.add(self.period, "warning", "Hohe Arbeitslosigkeit", {"unemployment_rate": m.get("unemployment_rate")})
        if m.get("inflation", 0.0) > 0.12:
            self.event_log.add(self.period, "warning", "Starke Inflation", {"inflation": m.get("inflation")})
        if m.get("q18_debt_value", 0.0) > 180:
            self.event_log.add(self.period, "warning", "Architekturschuld kritisch", {"q18_debt_value": m.get("q18_debt_value")})
        if m.get("q16_debt_value", 0.0) > 180:
            self.event_log.add(self.period, "warning", "Betriebsschuld kritisch", {"q16_debt_value": m.get("q16_debt_value")})

    def compute_metrics(self, initial=False):
        agents = self.all_agents()
        households = self.households
        firms = self.firms
        # Geldmenge und Schulden.
        q_positive_value = dict((q, 0.0) for q in range(1, 21))
        q_debt_value = dict((q, 0.0) for q in range(1, 21))
        for a in agents:
            for q, qty in a.wallet.balances.items():
                if qty > EPS:
                    q_positive_value[q] += qty * Q_VALUES[q]
                elif qty < -EPS:
                    q_debt_value[q] += -qty * Q_VALUES[q]
        sector_output = defaultdict(float)
        sector_sales = defaultdict(float)
        sector_profit = defaultdict(float)
        sector_price = defaultdict(list)
        sector_firms = defaultdict(int)
        for f in firms:
            sector_output[f.sector_key] += f.last_output
            sector_sales[f.sector_key] += f.last_sales_value
            sector_profit[f.sector_key] += f.last_profit
            sector_price[f.sector_key].append(f.price)
            sector_firms[f.sector_key] += 1
        household_worth = [h.net_worth() for h in households]
        firm_worth = [f.net_worth() for f in firms]
        price_index = self.goods_market.price_index
        last_pi = self.goods_market.last_price_index
        inflation = 0.0 if initial else safe_div(price_index - last_pi, last_pi, 0.0)
        employed = sum(1 for h in households if h.current_employer is not None)
        unemployment = safe_div(len(households) - employed, len(households), 0.0)
        # BQP: Verkäufe finaler Güter an Haushalte, Staat, Export; Inputkäufe sind enthalten, aber die Kennzahl
        # heißt bewusst Simulations-BQP, nicht strenges VGR-BIP.
        bqp = self.goods_market.sales_value
        metrics = {
            "period": self.period,
            "scenario": self.scenario,
            "households": len(households),
            "firms": len(firms),
            "banks": len(self.banks),
            "bqp": bqp,
            "sales_value": self.goods_market.sales_value,
            "transactions": self.goods_market.transactions,
            "price_index": price_index,
            "inflation": inflation,
            "unemployment_rate": unemployment,
            "employed": employed,
            "avg_wage": self.labor_market.avg_wage,
            "avg_health": mean(h.health for h in households),
            "avg_education": mean(h.education for h in households),
            "avg_happiness": mean(h.happiness for h in households),
            "household_gini": gini(household_worth),
            "household_net_worth_avg": mean(household_worth),
            "household_net_worth_p10": percentile(household_worth, 10),
            "household_net_worth_p90": percentile(household_worth, 90),
            "firm_net_worth_avg": mean(firm_worth),
            "bankrupt_firms": sum(1 for f in firms if f.bankrupt),
            "total_positive_money_value": sum(q_positive_value.values()),
            "total_debt_value": sum(q_debt_value.values()),
            "q10_debt_value": q_debt_value[10],
            "q16_debt_value": q_debt_value[16],
            "q18_debt_value": q_debt_value[18],
            "q19_debt_value": q_debt_value[19],
            "q20_debt_value": q_debt_value[20],
            "loan_outstanding": self.credit.outstanding_value(),
            "new_credit_zw": self.credit.new_credit_zw,
            "repaid_zw": self.credit.repaid_zw,
            "default_losses_zw": self.credit.default_losses_zw,
            "government_net_worth": self.government.net_worth(),
            "tax_revenue": self.government.tax_revenue,
            "transfer_spending": self.government.transfer_spending,
            "public_spending": self.government.public_spending,
            "exports_value": self.external.exports_value,
            "imports_value": self.external.imports_value,
            "coin_repaired_value": self.coin_market.repaired_value,
            "mint_rejected_value": self.mint.rejected_value,
        }
        # Gute Engpass-Kennzahlen.
        for g in GOODS:
            metrics["shortage_%s" % g] = self.goods_market.unmet_qty_by_good.get(g, 0.0)
            metrics["sales_qty_%s" % g] = self.goods_market.sales_qty_by_good.get(g, 0.0)
            metrics["price_%s" % g] = self.goods_market.avg_prices.get(g, GOODS[g].base_price)
        for q in range(1, 21):
            metrics["q%d_positive_value" % q] = q_positive_value[q]
            metrics["q%d_debt_value" % q] = q_debt_value[q]
            metrics["q%d_coin_price" % q] = self.coin_market.coin_prices.get(q, Q_VALUES[q])
            metrics["q%d_shortage" % q] = self.coin_market.shortage.get(q, 0.0)
        for s in SECTOR_RECIPES:
            metrics["sector_%s_output" % s] = sector_output[s]
            metrics["sector_%s_sales" % s] = sector_sales[s]
            metrics["sector_%s_profit" % s] = sector_profit[s]
            metrics["sector_%s_firms" % s] = sector_firms[s]
            metrics["sector_%s_avg_price" % s] = mean(sector_price[s], SECTOR_RECIPES[s].base_productivity if False else GOODS[SECTOR_RECIPES[s].output_good].base_price)
        return metrics

    def run(self, periods=120, progress=False, color=True, language="en", width=None):
        periods = int(periods)
        for _ in range(periods):
            m = self.step()
            if progress and (self.period % max(1, periods // 10) == 0 or self.period == 1):
                print(format_progress_line(self.period, periods, m, ansi=color, language=language, width=width))
        return self.metrics_history

    def final_summary(self):
        if self.metrics_history:
            m = self.metrics_history[-1]
        else:
            m = self.last_metrics
        top_shortages = []
        for g in GOODS:
            top_shortages.append((g, m.get("shortage_%s" % g, 0.0)))
        top_shortages.sort(key=lambda x: x[1], reverse=True)
        q_debts = []
        for q in range(1, 21):
            q_debts.append((q, m.get("q%d_debt_value" % q, 0.0)))
        q_debts.sort(key=lambda x: x[1], reverse=True)
        sector_sales = []
        for s in SECTOR_RECIPES:
            sector_sales.append((s, m.get("sector_%s_sales" % s, 0.0)))
        sector_sales.sort(key=lambda x: x[1], reverse=True)
        return {
            "scenario": self.scenario,
            "periods": self.period,
            "core": {
                "bqp": m.get("bqp", 0.0),
                "price_index": m.get("price_index", 1.0),
                "inflation": m.get("inflation", 0.0),
                "unemployment_rate": m.get("unemployment_rate", 0.0),
                "total_positive_money_value": m.get("total_positive_money_value", 0.0),
                "total_debt_value": m.get("total_debt_value", 0.0),
                "loan_outstanding": m.get("loan_outstanding", 0.0),
                "government_net_worth": m.get("government_net_worth", 0.0),
                "household_gini": m.get("household_gini", 0.0),
            },
            "top_shortages": top_shortages[:8],
            "top_q_debts": q_debts[:8],
            "top_sector_sales": sector_sales[:8],
            "recent_events": self.event_log.recent(25),
        }

    def save(self, out_dir, language="en", width=None):
        from .reporting import write_reports
        return write_reports(self, out_dir, language=language, width=width)
