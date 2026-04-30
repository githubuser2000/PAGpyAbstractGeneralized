# Solar Hierarchy Market — PyPy-safe Network/Category/Sheaf Simulation

This version fixes the PyPy3 segmentation fault that can occur on the `large` profile when the script materializes a very large live graph of network nodes, queues, identities, morphisms, functor maps, packets, and sheaf data.

## What changed

The simulation now has a **PyPy-safe sparse graph mode**.

The economic population remains large: workers, products, companies, countries, markets, privileges, burdens and trades are still simulated. The difference is that, in safe mode, not every worker and product receives a full live network/category object. Many smaller entities remain economically real but are represented as virtual graph entities.

This avoids the dangerous PyPy pattern:

- huge live object graph
- thousands of queues and morphism objects
- many category identity morphisms
- many routed packets
- large post-build mutation phase

## Automatic behavior

When the script is run under PyPy and the profile is `large` or `huge`, safe mode is enabled automatically.

This should now work directly:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large --ticks 1
```

The script also accepts the positional shorthand:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large 1
```

## Manual switches

Force safe mode, useful for testing on CPython:

```bash
python3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large 1 --safe-mode
```

Disable safe mode and materialize the full graph. This is intentionally dangerous on PyPy large/huge:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large 1 --unsafe-full-graph
```

Disable UTF-8 diagrams:

```bash
pypy3 solar_hierarchy_market_network_category_sim_pypy3.py --profile large 1 --quiet --no-visuals
```


## Compatibility with older `--processes` commands

The script still accepts `--processes`, `--no-parallel`, `--live-process-cap`, and `--debug-stages` so older commands do not fail. In PyPy-safe mode, however, it avoids spawning worker processes after the large graph is built. The reason is practical: forking or process-spawning from a huge PyPy heap was part of the segfault/OOM risk. The safe replacement is sparse graph materialization plus virtual graph counts.

## Output explanations

The script output now includes:

- a full explanation at the beginning of the run
- a glossary of abbreviations and concepts
- explanation blocks before numeric sections
- interpretation blocks after numeric sections
- explanation and interpretation around each UTF-8 visualization
- a balanced final summary describing multiple possible random outcomes

## Important interpretation

In safe mode, `entities` is the economic size of the simulation. `graph_nodes` is the number of live network/category nodes. `virtual_graph_entities` is the number of economic entities represented virtually in the graph layer.

That means market volume, hierarchy levels, ownership changes and trades still describe the large economy. Fine-grained per-worker network routing should be read as sampled graph behavior rather than a complete worker-to-worker network.

## Files

- `solar_hierarchy_market_network_category_sim_pypy3.py` — main script
- `solar_hierarchy_network_category_pypy_safe_demo_output.txt` — demo run with explanations and UTF-8 visuals
- `solar_hierarchy_network_category_pypy_safe_demo_plain_output.txt` — demo run without visuals
- `solar_hierarchy_network_category_pypy_safe_large_plain_output.txt` — large safe-mode run without visuals
- `solar_hierarchy_network_category_pypy_safe_large_time.txt` — CPython timing/RSS measurement for the large safe-mode test
