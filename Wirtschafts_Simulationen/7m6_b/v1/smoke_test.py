#!/usr/bin/env python3
from vector_currency_sim import VectorEconomySim

sim = VectorEconomySim(seed=123, n_countries=2, n_households=80, n_firms=32, n_banks=4, verbose=False)
for _ in range(3):
    row = sim.step()
assert row["gdp"] >= 0
assert 0 <= row["unemployment"] <= 1
assert 0 <= row["world_money_concentration"] <= 1
assert row["active_firms"] > 0
print("smoke test ok", row["t"], row["gdp"], row["world_money_theta_deg"])
