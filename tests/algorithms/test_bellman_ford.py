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
BELLMAN_CASES_FILE = DATA_DIR / "bellman_test_graphs.json"


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


def test_bellman_ford_simple():
	graph = load_bellman_graph("simple")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert result["distance"] == 3
	assert result["path"] == ["A", "B", "C"]


def test_bellman_ford_multiple_paths_choose_shortest():
	graph = load_bellman_graph("multiple_paths")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="D")

	assert result["distance"] == 2
	assert result["path"] == ["A", "C", "B", "D"]


def test_bellman_ford_directed_graph_respects_edge_direction():
	graph = load_bellman_graph("directed")
	result = bellman_ford_module.bellman_ford(graph, source="B", target="A")

	assert result["distance"] == inf
	assert result["path"] == []


def test_bellman_ford_undirected_graph():
	graph = load_bellman_graph("undirected")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert result["distance"] == 3
	assert result["path"] == ["A", "B", "C"]


def test_bellman_ford_negative_weights_work_correctly():
	graph = load_bellman_graph("negative_weights")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert result["distance"] == 1
	assert result["path"] == ["A", "B", "C"]


def test_bellman_ford_positive_and_negative_weights():
	graph = load_bellman_graph("mixed_weights")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="D")

	assert result["distance"] == 5
	assert result["path"] == ["A", "B", "C", "D"]


def test_bellman_ford_sum_of_weights_is_correct():
	graph = load_bellman_graph("sum_weights")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert result["distance"] == 7
	assert result["path"] == ["A", "B", "C"]


def test_bellman_ford_negative_cycle_detection():
	graph = load_bellman_graph("negative_cycle")

	with pytest.raises(ValueError):
		bellman_ford_module.bellman_ford(graph, source="A", target="D")


def test_bellman_ford_normal_cycle_without_negative_cycle():
	graph = load_bellman_graph("normal_cycle")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="D")

	assert result["distance"] == 4
	assert result["path"] == ["A", "B", "C", "D"]


def test_bellman_ford_source_equals_destination():
	graph = load_bellman_graph("simple")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="A")

	assert result["distance"] == 0
	assert result["path"] == ["A"]


def test_bellman_ford_single_vertex_graph():
	graph = load_bellman_graph("single_vertex")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="A")

	assert result["distance"] == 0
	assert result["path"] == ["A"]


def test_bellman_ford_disconnected_graph_no_path():
	graph = load_bellman_graph("disconnected")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="D")

	assert result["distance"] == inf
	assert result["path"] == []


def test_bellman_ford_source_vertex_missing():
	graph = load_bellman_graph("simple")

	with pytest.raises(KeyError):
		bellman_ford_module.bellman_ford(graph, source="Z", target="C")


def test_bellman_ford_target_vertex_missing():
	graph = load_bellman_graph("simple")

	with pytest.raises(KeyError):
		bellman_ford_module.bellman_ford(graph, source="A", target="Z")


def test_bellman_ford_empty_graph():
	graph = load_bellman_graph("empty")

	with pytest.raises(ValueError):
		bellman_ford_module.bellman_ford(graph, source="A", target="A")


def test_bellman_ford_zero_weight_edges():
	graph = load_bellman_graph("zero_weights")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert result["distance"] == 0
	assert result["path"] == ["A", "B", "C"]


def test_bellman_ford_output_structure_is_coherent():
	graph = load_bellman_graph("simple")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert "distance" in result
	assert "path" in result
	assert isinstance(result["path"], list)
	assert result["path"][0] == "A"
	assert result["path"][-1] == "C"
	assert result["distance"] == 3
