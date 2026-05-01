# Dijkstra Summary Report

## Purpose
This report summarizes the Dijkstra test investigation, the observed failures, the test scope, and the changes needed from the dev team.

## Tests Covered
The suite in [tests/algorithms/test_dijkstra.py](algorithms/test_dijkstra.py) covers:

- shortest path on a simple directed graph
- multiple path selection
- directed edge respect
- undirected graph behavior
- sum of weights
- source equals destination
- single vertex graph
- disconnected graph behavior
- graphs with no path between nodes
- cycle handling
- negative weight rejection
- missing source vertex handling
- empty graph handling
- zero-weight edge handling
- output structure validation

## Root Issue Found
The failure was caused by a mismatch between the test helper call and the utility function contract.

The tests were calling `load_graph_from_json()` with a file path string such as `data/simple_graph.json`, but the helper in [app/utils/file_loader.py](../app/utils/file_loader.py) expects a parsed JSON object with a top-level `graph` key.

That produced the error:

`TypeError: string indices must be integers, not 'str'`

## Needed Dev-Team Changes
The dev team should standardize graph loading in one of these ways:

1. Keep `load_graph_from_json()` for parsed dictionaries only, and use a separate file-based loader in tests and application code.
2. Or make the loader API explicit and consistent so file paths and JSON objects are not mixed.

Recommended follow-up for the codebase:

- expose a dedicated file loader that reads JSON from disk
- keep the JSON-to-graph conversion helper focused on parsed objects only
- ensure tests import and call the correct helper

## Result
After the loader mismatch was addressed, the Dijkstra test file ran successfully and all 15 tests passed.

## Current Status
The test suite is now green for the Dijkstra cases. The remaining work for the dev team is to keep loader responsibilities clear so this mismatch does not recur.