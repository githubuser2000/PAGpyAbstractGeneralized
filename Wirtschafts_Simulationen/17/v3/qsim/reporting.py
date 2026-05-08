# -*- coding: utf-8 -*-
"""Berichte und Exportdateien für die Q-Wirtschaftssimulation."""

from __future__ import print_function

import csv
import json
import os
from collections import defaultdict

from .money import Q_META, Q_VALUES
from .sectors import GOODS, SECTOR_RECIPES, LABOR_TYPES
from .utils import mean, gini
from .utf8art import write_visual_report


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def write_csv(path, rows):
    rows = list(rows)
    if not rows:
        with open(path, "w") as f:
            f.write("")
        return path
    # stabile Header: period/scenario zuerst, dann alphabetisch.
    keys = set()
    for r in rows:
        keys.update(r.keys())
    keys = list(keys)
    ordered = []
    for k in ("period", "scenario"):
        if k in keys:
            ordered.append(k)
            keys.remove(k)
    ordered.extend(sorted(keys))
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=ordered)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)
    return path


def write_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2, sort_keys=True)
    return path


def q_balance_rows(sim):
    rows = []
    agents = sim.all_agents()
    for q in range(1, 21):
        pos_qty = 0.0
        debt_qty = 0.0
        holders = 0
        debtors = 0
        for a in agents:
            qty = a.wallet.balances.get(q, 0.0)
            if qty > 1e-9:
                pos_qty += qty
                holders += 1
            elif qty < -1e-9:
                debt_qty += -qty
                debtors += 1
        rows.append({
            "q": q,
            "label": "Q%d" % q,
            "name": Q_META[q]["name"],
            "layer": Q_META[q]["layer"],
            "coin_value_zw": Q_VALUES[q],
            "positive_qty": pos_qty,
            "positive_value_zw": pos_qty * Q_VALUES[q],
            "debt_qty": debt_qty,
            "debt_value_zw": debt_qty * Q_VALUES[q],
            "holders": holders,
            "debtors": debtors,
            "market_price": sim.coin_market.coin_prices.get(q, Q_VALUES[q]),
            "shortage_index": sim.coin_market.shortage.get(q, 0.0),
            "meaning": Q_META[q]["meaning"],
        })
    return rows


def sector_rows(sim):
    rows = []
    for s, recipe in SECTOR_RECIPES.items():
        firms = [f for f in sim.firms if f.sector_key == s]
        rows.append({
            "sector": s,
            "label": recipe.label,
            "firms": len(firms),
            "output_good": recipe.output_good,
            "avg_price": mean(f.price for f in firms) if firms else GOODS[recipe.output_good].base_price,
            "inventory": sum(f.inventory.get(recipe.output_good, 0.0) for f in firms),
            "last_output": sum(f.last_output for f in firms),
            "last_sales_value": sum(f.last_sales_value for f in firms),
            "last_profit": sum(f.last_profit for f in firms),
            "capital_stock": sum(f.capital_stock for f in firms),
            "automation_level_avg": mean(f.automation_level for f in firms) if firms else 0.0,
            "debt_value": sum(f.wallet.debt_value() for f in firms),
            "positive_wallet_value": sum(f.wallet.positive_value() for f in firms),
            "description": recipe.description,
        })
    return rows


def labor_rows(sim):
    rows = []
    counts = sim.labor_market.count_by_labor
    wages = sim.labor_market.wage_by_labor
    for lt, meta in LABOR_TYPES.items():
        employed = counts.get(lt, 0)
        rows.append({
            "labor_type": lt,
            "label": meta.label,
            "employed_last_period": employed,
            "avg_wage_last_period": wages.get(lt, 0.0) / employed if employed else 0.0,
            "base_wage": meta.base_wage,
            "description": meta.description,
        })
    return rows


def agent_snapshot_rows(sim, max_rows=10000):
    rows = []
    for a in sim.all_agents()[:max_rows]:
        row = {
            "id": a.id,
            "name": a.name,
            "kind": a.kind,
            "net_worth": a.net_worth(),
            "positive_liquidity": a.wallet.positive_value(),
            "debt_value": a.wallet.debt_value(),
            "income_zw": a.income_zw,
            "expense_zw": a.expense_zw,
        }
        if hasattr(a, "sector_key"):
            row["sector"] = a.sector_key
            row["output_good"] = a.output_good
            row["price"] = a.price
            row["capital_stock"] = a.capital_stock
            row["automation_level"] = a.automation_level
            row["last_output"] = a.last_output
            row["last_profit"] = a.last_profit
        if hasattr(a, "health"):
            row["health"] = a.health
            row["education"] = a.education
            row["happiness"] = a.happiness
            row["primary_labor"] = a.primary_labor
            row["current_labor_type"] = a.current_labor_type or ""
            row["unemployed_periods"] = a.unemployed_periods
        rows.append(row)
    return rows


def write_summary_md(sim, path, language="en", width=None):
    """Schreibt den Hauptbericht als ausführlichen UTF-8-Art-Markdownbericht.

    Die frühere Kurzfassung mit Tabellen wurde bewusst ersetzt: Jede zentrale
    Ausgabe ist nun eine beschriebene und ausgewertete UTF-8-Art-Darstellung.
    """
    return write_visual_report(path, sim, markdown=True, ansi=False, language=language, width=width)


def write_visual_ansi_txt(sim, path, language="en", width=None):
    return write_visual_report(path, sim, markdown=False, ansi=True, language=language, width=width)


def write_visual_plain_txt(sim, path, language="en", width=None):
    return write_visual_report(path, sim, markdown=False, ansi=False, language=language, width=width)

def write_reports(sim, out_dir, language="en", width=None):
    ensure_dir(out_dir)
    paths = {}
    paths["time_series"] = write_csv(os.path.join(out_dir, "time_series.csv"), sim.metrics_history)
    paths["q_balances"] = write_csv(os.path.join(out_dir, "q_balances.csv"), q_balance_rows(sim))
    paths["sectors"] = write_csv(os.path.join(out_dir, "sector_report.csv"), sector_rows(sim))
    paths["labor"] = write_csv(os.path.join(out_dir, "labor_report.csv"), labor_rows(sim))
    paths["agents"] = write_csv(os.path.join(out_dir, "agents_snapshot.csv"), agent_snapshot_rows(sim))
    paths["events"] = write_json(os.path.join(out_dir, "events.json"), sim.event_log.items)
    paths["final_state"] = write_json(os.path.join(out_dir, "final_state.json"), sim.final_summary())
    paths["summary"] = write_summary_md(sim, os.path.join(out_dir, "summary.md"), language=language, width=width)
    paths["visual_report"] = write_visual_report(os.path.join(out_dir, "visual_report.md"), sim, markdown=True, ansi=False, language=language, width=width)
    paths["visual_report_ansi"] = write_visual_ansi_txt(sim, os.path.join(out_dir, "visual_report_ansi.txt"), language=language, width=width)
    paths["dashboard_utf8"] = write_visual_plain_txt(sim, os.path.join(out_dir, "dashboard_utf8.txt"), language=language, width=width)
    config = {
        "seed": sim.seed,
        "scenario": sim.scenario,
        "periods": sim.period,
        "households": len(sim.households),
        "firms": len(sim.firms),
        "banks": len(sim.banks),
        "language": language,
        "width": width,
    }
    paths["config"] = write_json(os.path.join(out_dir, "run_config.json"), config)
    return paths
