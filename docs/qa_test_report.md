# QA Test Report

Date: 2026-05-02
Scope: tests/algorithms and tests/core
Command: pytest -q tests/algorithms tests/core
Result: 44 failed, 262 passed

## Context
This report documents the updated validation-oriented tests requested in docs/test_a_faire.md.
No algorithm code was modified in this phase; only tests were adjusted or added.

## What was validated
Common validations expected across algorithms:
- Input schema integrity (nodes list, edges list, edge fields)
- Non-empty graphs
- Valid node references in edges
- Numeric weights and capacities
- Deterministic output
- No mutation of graph structure
- Self-loop policy enforcement
- Directed/undirected constraints per algorithm

## Test execution summary
- Total failures: 44
- Primary cause: missing or inconsistent validation and error handling in code
- Secondary cause: loader accepts malformed inputs without explicit ValueError

## Failures by area

### Loader and schema validation
Expected: loader rejects malformed nodes/edges and invalid field types with ValueError.
Actual: TypeError/KeyError or silent acceptance.
Tests:
- tests/algorithms/test_edge_cases.py
- tests/algorithms/test_ford_fulkerson.py
Code:
- app/utils/file_loader.py

### Bellman and Bellman-Ford
Expected: raise ValueError for invalid source/target, empty graph, self-loop, negative cycle, invalid DAG order.
Actual: no validation or no error raised.
Tests:
- tests/algorithms/test_bellman.py
- tests/algorithms/test_bellman_ford.py
Code:
- app/algorithms/shortest_path/bellman.py
- app/algorithms/shortest_path/bellman_ford.py

### Dijkstra
Expected: reject self-loop, invalid adjacency reference, non-numeric weight with ValueError.
Actual: no validation, KeyError/TypeError or no error.
Tests:
- tests/algorithms/test_dijkstra.py
Code:
- app/algorithms/shortest_path/dijkstra.py

### Ford-Fulkerson
Expected: reject missing source/sink, non-directed graphs, missing or negative capacities.
Actual: no errors raised.
Tests:
- tests/algorithms/test_ford_fulkerson.py
Code:
- app/algorithms/flow/ford_fulkerson.py

### Eulerian path
Expected: ValueError for empty graph, non-eulerian or disconnected cases, invalid directed connectivity.
Actual: returns None or raises IndexError.
Tests:
- tests/algorithms/test_eulerian_path.py
Code:
- app/algorithms/eulerian/eulerian_path.py

### Kruskal / Prim
Expected: reject self-loops; Kruskal rejects disconnected graph; Prim rejects directed graphs.
Actual: self-loops accepted and processed.
Tests:
- tests/algorithms/test_kruskal.py
- tests/algorithms/test_prim.py
Code:
- app/algorithms/spanning_tree/kruskal.py
- app/algorithms/spanning_tree/prim.py

### Welsh-Powell
Expected: reject directed graphs and self-loops.
Actual: no validation; algorithm runs and prints debug output.
Tests:
- tests/algorithms/test_welsh_powell.py
Code:
- app/algorithms/coloring/welsh_powell.py

### Connectivity (connected / strongly connected)
Expected: malformed adjacency raises ValueError.
Actual: KeyError or no error.
Tests:
- tests/algorithms/test_connected_components.py
- tests/algorithms/test_strongly_connected.py
Code:
- app/algorithms/connectivity/connected_components.py
- app/algorithms/connectivity/strongly_connected.py

### Graph core
Expected: undirected edges deduplicated in get_edges().
Actual: duplicates returned when both directions added.
Tests:
- tests/core/test_graph.py
Code:
- app/core/graph.py

## Required corrections (developer action)
1) Implement strict validation in loader
- Enforce nodes as list, edges as list
- Enforce edge fields: from, to
- Enforce numeric weight/capacity
- Enforce edge endpoints exist in nodes
- Raise ValueError with clear messages

2) Add per-algorithm input validation
- bellman/bellman_ford: non-empty, source/target exists, negative cycle detection, self-loop policy
- dijkstra: source exists, no negative weights, reject invalid adjacency and non-numeric weights
- ford_fulkerson: directed graph, source/sink exist, capacities present and non-negative
- eulerian_path: reject empty graph, enforce connectivity rules, raise ValueError instead of None/IndexError
- kruskal/prim: reject self-loops
- welsh_powell: reject directed graph and self-loop
- connectivity algorithms: validate adjacency references

3) Define and document policy choices
- Self-loop policy (reject vs allow)
- Cycle policy for Bellman (reject only negative cycles vs all cycles)
- Empty graph policy (return empty vs raise error)

4) Normalize error behavior
- Replace KeyError/TypeError with explicit ValueError where tests expect it

## Risks if not fixed
- Uncontrolled runtime errors (KeyError, IndexError) on invalid input
- Silent acceptance of malformed graphs and bad parameters
- Non-deterministic or undefined behavior

## Next steps
- Developer implements validations and error handling
- Re-run: pytest -q tests/algorithms tests/core
- Expect failures to drop to 0 once validations align with tests
