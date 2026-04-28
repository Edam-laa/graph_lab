import json
from math import inf
from pathlib import Path

import pytest

from app.algorithms.shortest_path import bellman_ford as bellman_ford_module


DATA_DIR = Path(__file__).resolve().parents[2] / "data"


def load_graph(path):
	with (DATA_DIR / Path(path).name).open(encoding="utf-8") as handle:
		return json.load(handle)


def test_bellman_ford_simple():
	graph = load_graph("data/bellman_simple_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert result["distance"] == 3
	assert result["path"] == ["A", "B", "C"]


def test_bellman_ford_multiple_paths_choose_shortest():
	graph = load_graph("data/bellman_multiple_paths_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="D")

	assert result["distance"] == 2
	assert result["path"] == ["A", "C", "B", "D"]


def test_bellman_ford_directed_graph_respects_edge_direction():
	graph = load_graph("data/bellman_directed_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="B", target="A")

	assert result["distance"] == inf
	assert result["path"] == []


def test_bellman_ford_undirected_graph():
	graph = load_graph("data/bellman_undirected_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert result["distance"] == 3
	assert result["path"] == ["A", "B", "C"]


def test_bellman_ford_negative_weights_work_correctly():
	graph = load_graph("data/negative_weights.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert result["distance"] == 1
	assert result["path"] == ["A", "B", "C"]


def test_bellman_ford_positive_and_negative_weights():
	graph = load_graph("data/bellman_mixed_weights_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="D")

	assert result["distance"] == 5
	assert result["path"] == ["A", "B", "C", "D"]


def test_bellman_ford_sum_of_weights_is_correct():
	graph = load_graph("data/bellman_sum_weights_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert result["distance"] == 7
	assert result["path"] == ["A", "B", "C"]


def test_bellman_ford_negative_cycle_detection():
	graph = load_graph("data/bellman_negative_cycle_graph.json")

	with pytest.raises(ValueError):
		bellman_ford_module.bellman_ford(graph, source="A", target="D")


def test_bellman_ford_normal_cycle_without_negative_cycle():
	graph = load_graph("data/bellman_normal_cycle_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="D")

	assert result["distance"] == 4
	assert result["path"] == ["A", "B", "C", "D"]


def test_bellman_ford_source_equals_destination():
	graph = load_graph("data/bellman_simple_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="A")

	assert result["distance"] == 0
	assert result["path"] == ["A"]


def test_bellman_ford_single_vertex_graph():
	graph = load_graph("data/bellman_single_vertex_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="A")

	assert result["distance"] == 0
	assert result["path"] == ["A"]


def test_bellman_ford_disconnected_graph_no_path():
	graph = load_graph("data/disconnected_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="D")

	assert result["distance"] == inf
	assert result["path"] == []


def test_bellman_ford_source_vertex_missing():
	graph = load_graph("data/bellman_simple_graph.json")

	with pytest.raises(KeyError):
		bellman_ford_module.bellman_ford(graph, source="Z", target="C")


def test_bellman_ford_target_vertex_missing():
	graph = load_graph("data/bellman_simple_graph.json")

	with pytest.raises(KeyError):
		bellman_ford_module.bellman_ford(graph, source="A", target="Z")


def test_bellman_ford_empty_graph():
	graph = load_graph("data/empty_graph.json")

	with pytest.raises(ValueError):
		bellman_ford_module.bellman_ford(graph, source="A", target="A")


def test_bellman_ford_zero_weight_edges():
	graph = load_graph("data/bellman_zero_weights_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert result["distance"] == 0
	assert result["path"] == ["A", "B", "C"]


def test_bellman_ford_output_structure_is_coherent():
	graph = load_graph("data/bellman_simple_graph.json")
	result = bellman_ford_module.bellman_ford(graph, source="A", target="C")

	assert "distance" in result
	assert "path" in result
	assert isinstance(result["path"], list)
	assert result["path"][0] == "A"
	assert result["path"][-1] == "C"
	assert result["distance"] == 3
