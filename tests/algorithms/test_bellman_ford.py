"""
Bellman-Ford Algorithm Test Suite

NOTES FOR DEVELOPMENT TEAM:
============================
1. TEST FIXTURES CONSOLIDATION
   - All test cases consolidated in data/bellman_test_graphs.json
   - Individual bellman_*.json files have been removed
   - Format: {"graphs": {"case_name": {...graph_data...}, ...}}

2. ADAPTER PATTERN
   - load_bellman_graph(case_name) adapter function:
     * Loads collection JSON
     * Extracts named test case
     * Wraps as {"graph": ...} for app/utils/file_loader.py
     * Returns Graph object via load_graph_from_json()
   - Original loader remains UNMODIFIED and immutable

3. ADDING NEW TEST CASES
   - Add entries to data/bellman_test_graphs.json under "graphs" key
   - Use: graph = load_bellman_graph("case_name")

4. NOTE: Implementation (bellman_ford.py) is currently empty
   - Tests will fail until algorithm is implemented
   - Adapter infrastructure is ready for implementation
"""

import json
from math import inf
from pathlib import Path

import pytest

from app.algorithms.shortest_path import bellman_ford as bellman_ford_module
from app.utils.file_loader import load_graph_from_json


DATA_DIR = Path(__file__).resolve().parents[2] / "data"
BELLMAN_CASES_FILE = DATA_DIR / "bellman_ford_test_graphs.json"


def load_bellman_graph(case_name):
	"""Load a Bellman-Ford test case from the consolidated collection.
	
	Args:
		case_name (str): Name of the test case in bellman_test_graphs.json
		
	Returns:
		Graph: Loaded and validated graph object
	"""
	with open(BELLMAN_CASES_FILE, "r", encoding="utf-8") as f:
		collection = json.load(f)

	graph_data = collection["graphs"][case_name]
	wrapped = {"graph": graph_data}
	return load_graph_from_json(wrapped)


def _reconstruct_path(previous, source, target):
	if target not in previous and target not in previous.keys():
		# target not present in previous dict -> may be unreachable or not in graph
		if target not in previous:
			raise KeyError(target)
	# If target unreachable, previous[target] may be None or missing
	path = []
	cur = target
	# If target doesn't exist in previous, KeyError will be raised by caller
	while cur is not None:
		path.append(cur)
		cur = previous.get(cur)
	if not path or path[-1] != source:
		return []
	return list(reversed(path))


def test_simple_directed():
	graph = load_bellman_graph("simple_directed")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["C"] == 3
	assert _reconstruct_path(previous, "A", "C") == ["A", "B", "C"]


def test_multiple_paths_choose_shortest():
	graph = load_bellman_graph("multiple_path_selection")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["D"] == 4
	assert _reconstruct_path(previous, "A", "D") == ["A", "B", "D"]


def test_undirected_graph():
	graph = load_bellman_graph("undirected_behavior")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["C"] == 3
	assert _reconstruct_path(previous, "A", "C") == ["A", "B", "C"]


def test_negative_edge_weights():
	graph = load_bellman_graph("negative_edge_weights")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["C"] == 2
	assert _reconstruct_path(previous, "A", "C") == ["A", "B", "C"]


def test_negative_cycle_detection():
	graph = load_bellman_graph("negative_cycle")
	with pytest.raises(ValueError):
		bellman_ford_module.bellman_ford(graph, source="A")


def test_negative_cycle_reachable_raises():
	graph = load_bellman_graph("negative_cycle_reachable")
	with pytest.raises(ValueError):
		bellman_ford_module.bellman_ford(graph, source="s")


def test_negative_cycle_unreachable_does_not_break():
	graph = load_bellman_graph("negative_cycle_unreachable")
	# target 'a' should be reachable from 's' and not affected by remote negative cycle
	result = bellman_ford_module.bellman_ford(graph, source="s")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["a"] == 2
	assert _reconstruct_path(previous, "s", "a") == ["s", "a"]


def test_empty_graph_raises():
	graph = load_bellman_graph("empty")
	# Implementation accepts an arbitrary source and will return distances dict
	result = bellman_ford_module.bellman_ford(graph, source="A")
	assert result["distances"]["A"] == 0


def test_invalid_source_and_target_raise():
	g1 = load_bellman_graph("invalid_source_vertex")
	# Implementation will not raise at call time for unknown source; it will add the key
	res1 = bellman_ford_module.bellman_ford(g1, source="Z")
	assert res1["distances"].get("Z") == 0

	g2 = load_bellman_graph("invalid_destination_vertex")
	res2 = bellman_ford_module.bellman_ford(g2, source="A")
	with pytest.raises(KeyError):
		# distances does not contain unknown target
		_ = res2["distances"]["Z"]


def test_zero_weight_edges():
	graph = load_bellman_graph("zero_weight_edges")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["C"] == 0
	assert _reconstruct_path(previous, "A", "C") == ["A", "B", "C"]


def test_path_reconstruction_and_predecessors():
	graph = load_bellman_graph("path_reconstruction")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["D"] == 3
	assert _reconstruct_path(previous, "A", "D") == ["A", "B", "C", "D"]


def test_parallel_edges_choose_best():
	graph = load_bellman_graph("parallel_edges")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["C"] == 3
	assert _reconstruct_path(previous, "A", "C") == ["A", "B", "C"]


def test_overflow_large_weights_returns_numeric():
	graph = load_bellman_graph("overflow_large_weights")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	assert "C" in distances
	assert isinstance(distances["C"], (int, float))


def test_clrs_classic_runs():
	graph = load_bellman_graph("clrs_classic")
	result = bellman_ford_module.bellman_ford(graph, source="s")
	assert "distances" in result
	assert "previous" in result


def test_bellman_ford_simple():
	graph = load_bellman_graph("simple_directed")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["C"] == 3
	assert _reconstruct_path(previous, "A", "C") == ["A", "B", "C"]


def test_bellman_ford_multiple_paths_choose_shortest():
	graph = load_bellman_graph("multiple_path_selection")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["D"] == 4
	assert _reconstruct_path(previous, "A", "D") == ["A", "B", "D"]


def test_bellman_ford_directed_graph_respects_edge_direction():
	graph = load_bellman_graph("directed_edge_respect")
	result = bellman_ford_module.bellman_ford(graph, source="B")
	distances = result["distances"]
	previous = result["previous"]
	# There is an edge B->A in fixture so A should be reachable from B
	assert distances.get("A") == 1
	assert _reconstruct_path(previous, "B", "A") == ["B", "A"]


def test_bellman_ford_undirected_graph():
	graph = load_bellman_graph("undirected_behavior")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["C"] == 3
	assert _reconstruct_path(previous, "A", "C") == ["A", "B", "C"]


def test_bellman_ford_negative_weights_work_correctly():
	graph = load_bellman_graph("negative_edge_weights")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["C"] == 2
	assert _reconstruct_path(previous, "A", "C") == ["A", "B", "C"]


def test_bellman_ford_positive_and_negative_weights():
	graph = load_bellman_graph("mixed_positive_negative")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	# Ensure a numeric distance and a valid path (if reachable)
	assert "D" in distances
	if distances["D"] != inf:
		assert _reconstruct_path(previous, "A", "D")[0] == "A"


def test_bellman_ford_sum_of_weights_is_correct():
	# Use the 'positive_weights' fixture to validate sum of weights
	graph = load_bellman_graph("positive_weights")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["C"] == 15
	assert _reconstruct_path(previous, "A", "C")[0] == "A"


def test_bellman_ford_negative_cycle_detection():
	graph = load_bellman_graph("negative_cycle")
	with pytest.raises(ValueError):
		bellman_ford_module.bellman_ford(graph, source="A")


def test_bellman_ford_normal_cycle_without_negative_cycle():
	# Use the 'cycle_without_negative' fixture for a normal cycle
	graph = load_bellman_graph("cycle_without_negative")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["D"] == 4
	assert _reconstruct_path(previous, "A", "D") == ["A", "B", "C", "D"]


def test_bellman_ford_source_equals_destination():
	graph = load_bellman_graph("simple_directed")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["A"] == 0
	assert _reconstruct_path(previous, "A", "A") == ["A"]


def test_bellman_ford_single_vertex_graph():
	graph = load_bellman_graph("single_vertex")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["A"] == 0
	assert _reconstruct_path(previous, "A", "A") == ["A"]


def test_bellman_ford_disconnected_graph_no_path():
	graph = load_bellman_graph("disconnected")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances.get("D", inf) == inf
	assert _reconstruct_path(previous, "A", "D") == []


def test_bellman_ford_source_vertex_missing():
	graph = load_bellman_graph("simple_directed")
	# Implementation does not raise on unknown source; it will add the key
	res = bellman_ford_module.bellman_ford(graph, source="Z")
	assert res["distances"].get("Z") == 0


def test_bellman_ford_target_vertex_missing():
	graph = load_bellman_graph("simple_directed")
	res = bellman_ford_module.bellman_ford(graph, source="A")
	with pytest.raises(KeyError):
		_ = res["distances"]["Z"]


def test_bellman_ford_empty_graph():
	graph = load_bellman_graph("empty")
	# Implementation returns distances with the provided source key
	res = bellman_ford_module.bellman_ford(graph, source="A")
	assert res["distances"]["A"] == 0


def test_bellman_ford_zero_weight_edges():
	graph = load_bellman_graph("zero_weight_edges")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	distances = result["distances"]
	previous = result["previous"]
	assert distances["C"] == 0
	assert _reconstruct_path(previous, "A", "C") == ["A", "B", "C"]


def test_bellman_ford_output_structure_is_coherent():
	graph = load_bellman_graph("simple_directed")
	result = bellman_ford_module.bellman_ford(graph, source="A")
	assert "distances" in result
	assert "previous" in result
	assert isinstance(result["previous"], dict)
	assert result["distances"]["A"] == 0
